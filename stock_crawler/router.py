import time 
import typing

from loguru import logger
from sqlalchemy import engine, text

from stock_crawler import clients

def check_alive(
    connect: engine.base.Connection
):
    """check if connect alive before every use"""

    sql_stmt = text("SELECT 1 + 1")
    connect.execute(sql_stmt)


def reconnect(
    connect_func: typing.Callable
) -> engine.base.Connection:
    """reconnect if connect failed"""

    try:
        connect = connect_func()
    except Exception as e:
        logger.info(
            f"{connect_func.__name__} reconnect error {e}"
        )
    return connect

def check_connect_alive(
    connect: engine.base.Connection,
    connect_func: typing.Callable
):
    if connect:
        try:
            check_alive(connect)
            return connect
        except Exception as e:
            logger.info(
                f"{connect_func.__name__} connect, error: {e}"
            )
            time.sleep(1)
            connect = reconnect(connect_func)
            
            return check_connect_alive(connect, connect_func
                                       )
    else:
        connect = reconnect(connect_func)

        return check_connect_alive(connect, connect_func)


class Router:
    def __init__(self):
        self._postgres_fcn_conn = clients.get_postgres_fcn_conn()
    
    def check_postgres_fcn_conn_alive(self):

        self._postgres_fcn_conn = check_connect_alive(
            self._postgres_fcn_conn,
            clients.get_postgres_fcn_conn
        )

        return self._postgres_fcn_conn
    
    @property
    def postgres_fcn_conn(self):
        return self.check_postgres_fcn_conn_alive()