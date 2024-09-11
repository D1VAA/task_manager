from models import Base
#from crud_database import engine
from dotenv import load_dotenv
from sqlalchemy import create_engine, asc
import os

<<<<<<< HEAD
load_dotenv(f'{os.getcwd()}/src/tasks_database/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
=======
load_dotenv(f'{os.getcwd()}/.docker_env')
print(os.getcwd())
DATABASE_URL = os.getenv('DATABASE_CREATE_URL')
print(DATABASE_URL)
>>>>>>> cf82c78b3fae19affbf3916dbc34c87cb9b05cf1
if DATABASE_URL is None:
    raise ValueError('DATABASE_URL cannot be None.')

try:
    engine = create_engine(DATABASE_URL, echo=True)  # type: ignore

except Exception as e:
    raise ValueError(f'Failed to create engine: {e}')


Base.metadata.create_all(bind=engine)