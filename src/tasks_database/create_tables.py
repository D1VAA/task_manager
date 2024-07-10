from models import Base
#from crud_database import engine
from dotenv import load_dotenv
from sqlalchemy import create_engine, asc
import os

load_dotenv(f'{os.getcwd()}/src/tasks_database/.env')
DATABASE_URL = os.getenv('TASKS_DATABASE_URL')
if DATABASE_URL is None:
    raise ValueError('DATABASE_URL cannot be None.')

try:
    engine = create_engine(DATABASE_URL)  # type: ignore

except Exception as e:
    raise ValueError(f'Failed to create engine: {e}')


Base.metadata.create_all(bind=engine)