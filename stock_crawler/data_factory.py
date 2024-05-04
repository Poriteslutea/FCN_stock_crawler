# 以布朗運動進行蒙地卡羅模擬，生成時間序列的資料樣本

import numpy as np 
import pandas as pd



def generate_sample_data(rows:int, cols:int, freq:str='D', r:float=0.05, sigma:float=0.5):
    '''
    Parameter:
    rows: int
        要生成的資料列數
    cols: int
        要生成的行數
    freq: str
        DatetimeIndex 頻率字串
    r: float
        固定的短期利率
    sigma: float
        波動率因子
    
    Return:
    df: DataFrame
    '''

    rows = int(rows)
    cols = int(cols)
    # 生成一組DatetimeIndex
    index = pd.date_range('2024-01-01', periods=rows, freq=freq)
    # 得到時間差
    dt = (index[1] - index[0]) / pd.Timedelta(value='365D')
    # 生成縱列名稱
    columns = [f'No{i}' for i in range(cols)]
    # 生成幾何布朗運動的樣本路徑
    raw = np.exp(np.cumsum((r - 0.5 * sigma ** 2) * dt +
                           sigma * np.sqrt(dt) *
                           np.random.standard_normal((rows, cols)), axis=0))
    # normalize data (from 100)
    raw = raw / raw[0] * 100
    # 生成Dataframe
    df = pd.DataFrame(raw, index=index, columns=columns)

    return df


# Function to generate next random value based on existing value
def generate_next_random(existing_values, freq, r=0.05, sigma=0.5):
    '''
    只由前一個數來產生下一個隨機值 
    '''

    index = pd.date_range('2024-01-01', periods=2, freq=freq)
    dt = (index[1] - index[0]) / pd.Timedelta(value='365D')

    next_random = existing_values * np.exp((r - 0.5 * sigma ** 2) * dt +
                                          sigma * np.sqrt(dt) *
                                          np.random.standard_normal(len(existing_values)))
    return next_random




if __name__ == '__main__':
    rows = 100
    cols = 3
    freq = 'D'
    df = generate_sample_data(rows, cols, freq)
    latest_val = df.iloc[-1, :].values
    next_val = generate_next_random(latest_val, freq)
   


    