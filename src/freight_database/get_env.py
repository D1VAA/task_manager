import os
from dotenv import load_dotenv

load_dotenv(f'{os.getcwd()}/src/freight_database/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = os.getenv('REDIS_URL')