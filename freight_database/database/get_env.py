import os
from dotenv import load_dotenv

print(f"{os.getcwd()}/freight_database/database/.env")
load_dotenv(f"{os.getcwd()}/freight_database/database/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = os.getenv("REDIS_URL")
