from datetime import datetime, timedelta
from typing import List, Union
import sys

import numpy as np
import pandas as pd
import yfinance as yf
from loguru import logger


from router import Router
from schema import Product



def get_hist_price(stock_code: List[str], 
                   start_date: str, 
                   end_date: str, 
                   price_type: str='Close') -> pd.DataFrame:
    '''
    獲得歷史收盤價 
    '''
    stock_hist = yf.download(stock_code, start=start_date, end=end_date)[price_type]

    return stock_hist


def get_latest_price(stock_code: List[str], price_type: str='Close') -> dict:
    '''
    獲得最新一天的收盤價
    '''
    curr_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=5)).strftime('%Y-%m-%d')
    stock_latest = get_hist_price(stock_code=stock_code, start_date=start_date, end_date=curr_date, price_type=price_type)
    stock_latest = stock_latest.reset_index()
    ret = stock_latest.to_dict("records")[-1]
    ret['Date'] = ret['Date'].strftime('%Y-%m-%d')
    
    return ret


def replace_after(df, condition_type, critical_val, replace_val):
    '''
    給一個dataframe或series，去判斷所有值是否大於、等於、小於、小於等於、大於等於critical_val，
    是的話就把符合條件的值全部替代成replace_val
    如果給定的dataframe不只一個column的話，只要有一個column符合條件，整個row都會換成replace_val 
    '''
    
    if condition_type not in {'<', '<=', '>', '>=', '=='}:
        return 
    if isinstance(df, pd.Series):
        dd = df.to_frame()
    else:
        dd = df.copy()
    condition_str = 'dd' + condition_type + str(critical_val)
    condition = eval(condition_str)
    init_date = dd[dd[condition].any(axis=1)].index
    if len(init_date) == 0:
        return dd
    else:
        init_date = init_date[0]
    init_idx = dd.index.get_loc(init_date)
    dd.iloc[(init_idx + 1):] = replace_val
    
    return dd


def get_hist_report(product: Product,
                    report_start_date: str,
                    report_end_date: str
                    ) -> pd.DataFrame:
    
    stock_codes = [st['code'] for st in product.stock_list]
    start_date = product.start_date
    end_date = product.end_date
    price_type = product.price_type
    start_trace_date = product.start_trace_date
    ko_limit = product.ko_limit
    ki_limit = product.ki_limit

    stock_hist = get_hist_price(stock_code=stock_codes, 
                                start_date=start_date, 
                                end_date=end_date, 
                                price_type=price_type)
    

    # 得到與ko及ki的差距比例(%)
    ko_diff = stock_hist.sub(stock_hist.iloc[0] * ko_limit).div(stock_hist) * 100
    ki_diff = stock_hist.sub((stock_hist.iloc[0] * ki_limit)).div(stock_hist) * 100

    # 換一下column name，對不同dataframe加上後綴
    ko_diff = ko_diff.rename(columns={col: col+'_koDiff' for col in ko_diff.columns})
    ki_diff = ki_diff.rename(columns={col: col+'_kiDiff' for col in ki_diff.columns})

    # 當每支股票遇到ko差值大於等於0的情況時（目前價>=起始價) 後面都變nan值 （從起始追蹤日開始判斷)
    start_trace_dt = datetime.strptime(start_trace_date, '%Y-%m-%d')
    report_start_dt = datetime.strptime(report_start_date, '%Y-%m-%d')
    report_end_dt = datetime.strptime(report_end_date, '%Y-%m-%d')

    if start_trace_dt > report_end_dt:
        logger.info('還未到達開始追蹤日期')
        merge_df = ko_diff.merge(ki_diff, left_index=True, right_index=True).merge(stock_hist, left_index=True, right_index=True)
        return merge_df
    elif start_trace_date not in stock_hist.index:
        raise ValueError('開始追蹤日期不能給假日(不能給沒開市的日期)')
        
    # 從開始追蹤日期後ko的話就不再記
    ts_list = []
    for c in ko_diff.columns:
        ts = replace_after(ko_diff[c].loc[start_trace_date:], '>=', 0, np.nan)
        ts_list.append(ts)
    ko = pd.concat(ts_list, axis=1)

    # 當每一支股票ko_diff都變nan時直接結束
    ko.dropna(how='all', inplace=True)

    # 把起始追蹤日期之前的資料合併進來
    init_idx = ko_diff.index.get_loc(start_trace_date)
    ko = pd.concat([ko_diff.iloc[:(init_idx)], ko])

    # 當其中一支股票的ki差值小於等於0時，後面的值都變nan（目前價<=（起始價×0.6）) (從產品起始日就開始判斷)
    ki = replace_after(ki_diff, '<=', 0, np.nan)

    # 將產品開始到產品結束（可能會因all ko而提前結束)的資料合併起來
    merge_df = ko.merge(ki, left_index=True, right_index=True).merge(stock_hist, left_index=True, right_index=True)
    merge_df.reset_index(inplace=True)
    filter_df = merge_df[pd.to_datetime(merge_df['Date']) >= report_start_dt]
    base_row = merge_df.head(1)
    result_df = pd.concat([base_row, filter_df])


    return result_df


def get_stock_list_by_product(product_code: str, db_router: Router):

    sql_stmt = f"""
        select stock.code, stock.id
        from stock 
        join product_stock as ps on stock.id = ps.stock_id
        join product as p on ps.product_id = p.id
        where p.code = '{product_code}'
        """

    try:
        stock_df = pd.read_sql(sql_stmt, db_router.postgres_fcn_conn)
        stock_list = stock_df.to_dict('records')
        return stock_list
    
    except Exception as e:
        logger.error(e)
        return 


def report_to_db(report: pd.DataFrame, product: Product, db_router: Router):
    
    product_id = product.id 
    ko_limit = product.ko_limit
    ki_limit = product.ki_limit
    stock_list = product.stock_list

    report.reset_index(inplace=True)
    report_rc = report.to_dict('records')
    base_row = report_rc[0]

    ret = []
    for row in report_rc[1:]:
        date = row['Date']
        for st in stock_list:
            stock_report_row = {}
            stock_report_row['product_id_fk'] = product_id
            stock_report_row['stock_id_fk'] = st['id']
            stock_report_row['date'] = date
            stock_report_row['close'] = row[st['code']]
            stock_report_row['ko_base'] = base_row[st['code']] * ko_limit
            stock_report_row['ki_base'] = base_row[st['code']] * ki_limit
            stock_report_row['ko_diff'] = row[f'{st["code"]}_koDiff']
            stock_report_row['ki_diff'] = row[f'{st["code"]}_kiDiff']
            stock_report_row['is_ko'] = (stock_report_row['ko_diff'] >= 0) or np.isnan(stock_report_row['ko_diff'])
            stock_report_row['is_ki'] = (stock_report_row['ki_diff'] <= 0) or np.isnan(stock_report_row['ki_diff'])
         
            ret.append(stock_report_row)
    
    ret_df = pd.DataFrame(ret)
    try:
        ret_df.to_sql(
            name='daily_report',
            con=db_router.engine, 
            schema='public',
            if_exists='append',
            index=False)
        
        return ret_df
    except Exception as e:
        logger.info(f'import到資料庫失敗：{e}')

    return 

          


def import_product(product: Product, db_router: Router):
    '''
    Initialize historical report by product
    '''
    curr_dt = datetime.today()
    curr_date = curr_dt.strftime('%Y-%m-%d')
    start_dt = datetime.strptime(product.start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(product.end_date, '%Y-%m-%d')
    stock_list = product.stock_list
   
    # 還沒開始
    if curr_dt < start_dt:
        logger.info(f'產品：{product.code}還沒開始')
        return
    
    # 已過結束日期
    if curr_dt > end_dt:
        logger.info(f'產品{product.code}已過期')
        return
    
    # 確認資料庫有沒有產品資料
    
    sql_stmt = f'''
        select product_id_fk, date 
        from daily_report 
        where product_id_fk = {product.id}
        '''
    df = pd.read_sql(sql_stmt, db_router.postgres_fcn_conn)

    if len(df) > 0:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        db_latest_date = df['date'].iloc[-1]
        today = pd.Timestamp.today().normalize()
        # 如果DB目前最新日期不是今日日期，則更新到今日日期
        if today > db_latest_date:
            start_dt = db_latest_date + timedelta(days=1)
            start_date = start_dt.strftime('%Y-%m-%d')

            df = get_hist_report(
                product=product,
                report_start_date=start_date,
                report_end_date=curr_date
            ) 
            
            report_to_db(report=df, product=product, db_router=db_router)
            
            logger.info(f'產品{product.code}已更新至資料庫，從{start_date}開始更新')
        else:
            logger.info(f'產品{product.code}已更新到最新日期')
            return 

    
    else:
        # 資料庫還沒有產品資料（要進行初始化 - 從開始日期計算到當前日期，並將結果存至db中daily_report的table)
        df = get_hist_report(
            product=product,
            report_start_date=product.start_date,
            report_end_date=curr_date) 
        report_to_db(report=df, product=product, db_router=db_router)
    
        logger.info(f'產品{product.code}已初始化至資料庫')
    




def get_product(product_code: str, db_router: Router) -> Union[Product, None]:
    
    sql_stmt = f"select * from product where product.code = '{product_code}'"
    df = pd.read_sql(sql_stmt, db_router.postgres_fcn_conn)
    stock_list = get_stock_list_by_product(product_code, db_router)
    if len(df) > 0:
        product = Product(
            id=df['id'].iloc[0],
            code=df['code'].iloc[0],
            start_date=df['start_date'].iloc[0].strftime('%Y-%m-%d'),
            start_trace_date=df['start_trace_date'].iloc[0].strftime('%Y-%m-%d'),
            end_date=df['end_date'].iloc[0].strftime('%Y-%m-%d'),
            ko_limit=df['ko_limit'].iloc[0],
            ki_limit=df['ki_limit'].iloc[0],
            price_type=df['price_type'].iloc[0],
            stock_list=stock_list
        )

        return product
    else:
        logger.info(f"找不到product: {product_code}")
        return None

def get_all_product(db_router: Router) -> List[Union[Product, None]]:

    sql_stmt = f"select * from product"
    df = pd.read_sql(sql_stmt, db_router.postgres_fcn_conn)
    print(df)
    df['stock_list'] = df.apply(lambda x: get_stock_list_by_product(x['code'], db_router), axis=1)
    if len(df) == 0:
        return []
    ret = []
    for row in df.to_dict('records'):
        product = Product(
            id=row['id'],
            code=row['code'],
            start_date=row['start_date'].strftime('%Y-%m-%d'),
            start_trace_date=row['start_trace_date'].strftime('%Y-%m-%d'),
            end_date=row['end_date'].strftime('%Y-%m-%d'),
            ko_limit=row['ko_limit'],
            ki_limit=row['ki_limit'],
            price_type=row['price_type'],
            stock_list=row['stock_list']
        )
        ret.append(product)
    
    return ret



def main():
    db_router = Router()
    product_list = get_all_product(db_router)
    for product in product_list:
        import_product(product, db_router)


if __name__ == "__main__":
    # product_code = sys.argv[1]
    main()
    
    
  

