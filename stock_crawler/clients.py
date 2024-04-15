from sqlalchemy import create_engine, engine

def get_postgres_fcn_conn() -> engine.base.Connection:
    '''
    user: admin
    password: 0220
    host: localhost
    port: 5435
    database: fcn2
    '''
    db_url = 'postgresql://admin:0220@localhost:5435/fcn2'
    engine = create_engine(db_url)
    connect = engine.connect()

    return connect



