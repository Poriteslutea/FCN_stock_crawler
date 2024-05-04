import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.environ.get("PG_HOST")
PG_USER = os.environ.get("PG_USER")
PG_PASSWORD = os.environ.get("PG_PASSWORD")
PG_PORT = os.environ.get("PG_PORT")
PG_DATABASE = os.environ.get("PG_DATABASE")
DB_URL = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}'
MQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER")
MQ_PASSWORD = os.environ.get("RABBITMQ_DEFAULT_PASS")
