from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .models import Freight
from typing import Dict, Any

load_dotenv(f'{os.getcwd()}/src/database/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise ValueError('DATABASE_URL cannot be None.')

try:
    engine = create_engine(DATABASE_URL)  # type: ignore

except Exception as e:
    raise ValueError(f'Failed to create engine: {e}')

try:
    LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise ValueError(f'Failed to create sessionmaker: {e}')

@contextmanager
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def quick_query(obj: Any, filter_dict: Dict[str, Any]):
    with get_db() as _db:
        query = _db.query(obj).filter_by(**filter_dict).first()
        return query

def create_freight(origem: str, destino: str, client: str, link: str):
    with get_db() as db:
        if quick_query(Freight, {'origem': origem, 'destino': destino, 'client':client}) is not None:
            return {'message': 'Freight already exists.'}
        new_freight = Freight(origem=origem,
                              destino=destino,
                              client=client,
                              link=link)
        db.add(new_freight)
        db.commit()
        return {'message': f'Freight created succesfully.'}

def query_freight(origem: str, destino: str, client: str):
    with get_db() as db:
        query = db.query(Freight)

   # Filtros por igualdade (mantidos)
        if origem:
            query = query.filter(Freight.origem.contains(origem))
        if destino:
            query = query.filter(Freight.destino.contains(destino))
        if client:
            query = query.filter(Freight.client.contains(client))

        freights = query.all()
        links = []
        for x in freights:
            links.append({f'{x.origem} x {x.destino}':x.link})

        return links 

def delete_freight(freight_id):
    with get_db() as db:
        freight = db.get(Freight, freight_id)
        if freight is not None:
            try:
                db.delete(freight)
                db.commit()

            except:
                print("[!] An error occurred!")
                db.rollback()

def get_unique_values(column_name):
    with get_db() as db:
        column = getattr(Freight, column_name)
        distinct_values = db.query(column).distinct().all()
        return [value[0] for value in distinct_values]
