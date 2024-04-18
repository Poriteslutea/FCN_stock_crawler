from sqlalchemy import create_engine, engine

from config import DB_URL

def get_engine() -> engine:
    
    engine = create_engine(DB_URL)
    return engine

def get_postgres_fcn_conn() -> engine.base.Connection:
 
    engine = get_engine()
    connect = engine.connect()

    return connect





