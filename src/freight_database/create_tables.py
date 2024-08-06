from models import Base
from crud_database import engine

Base.metadata.create_all(bind=engine)