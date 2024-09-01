from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

from freight_database.freight_obj import FreightOBJ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .get_env import DATABASE_URL
from .models import Freight

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL cannot be None.")

try:
    engine = create_engine(DATABASE_URL)  # type: ignore

except Exception as e:
    raise ValueError(f"Failed to create engine: {e}")

try:
    LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise ValueError(f"Failed to create sessionmaker: {e}")


@contextmanager
def get_db():
    """
    Contextmanager para gerenciar a sessão com o banco de dados.
    Garantindo que a sessão seja aberta e fechada corretamente.
    """
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
    """Função para criar um novo frete na base de dados.

    Args:
        origem (str): A origem da prestação do serviço.
        O ideal é que a UF seja informada junto. Ex: 'Cidade, UF'

        destino (str): O destino do frete. O ideal é que a UF seja
        informada junto com a cidade. Ex: 'Cidade, UF'

        client (str): Nome do cliente.
        link (str): Link de download do google drive.

    Returns:
        Dict [str, str]: Mensagem de sucesso ou erro.

    """
    with get_db() as db:
        if (
            quick_query(
                Freight, {"origem": origem,
                          "destino": destino, "client": client}
            )
            is not None
        ):
            return {"message": "Freight already exists."}
        try:
            new_freight = Freight(
                origem=origem, destino=destino, client=client, link=link
            )
            db.add(new_freight)
            db.commit()
            return {"message": "Freight created succesfully."}
        except Exception as e:
            db.rollback()
            return {
                "message": "An error occurred while creating the freight.",
                "error": e,
            }


def query_freight(
    origem: Optional[str] = None,
    destino: Optional[str] = None,
    client: Optional[str] = None,
) -> List[FreightOBJ] | str:
    """Função para consultar um frete na base de dados.
    Caso nenhum parâmetro seja informado, a função irá retornar todos.

    Args:
        origem (str): Origem do frete. (Opcional)
        destino (str): Destino do frete. (Opcional)
        client (str): Cliente do frete. (Opcional)

    Returns:
    List[FreightOBJ]: Retorna uma lista de FreightOBJs.
    """

    with get_db() as db:
        query = db.query(Freight)
        if origem:
            query = query.filter(Freight.origem.contains(origem))
        if destino:
            query = query.filter(Freight.destino.contains(destino))
        if client:
            query = query.filter(Freight.client.contains(client))

        freights = query.all()
        result = [
            FreightOBJ(freight.origem, freight.destino,
                       freight.client, freight.link)
            for freight in freights
        ]
        if not result:
            return "No result found."
        else:
            return result


def delete_freight(
    freight_id: int,
) -> Union[Dict[str, str], Dict[str, Union[Exception, str]]]:
    """
    Função para deletar um frete da base de dados.

    Args:
        freight_id (int): Id do frete na base de dados.

    """
    with get_db() as db:
        freight = db.get(Freight, freight_id)
        if freight is not None:
            try:
                db.delete(freight)
                db.commit()
                return {"message": "Freight succesfully deleted."}

            except Exception as e:
                db.rollback()
                return {"message": "[!] An error occurred!", "error": e}
        else:
            return {"error": "Freight id not informed."}


def get_unique_values(column_name):
    """
    Função para retornar os valores únicos de determinada coluna da base de dados.

    Args:
        column_name(str): Nome da coluna que se deseja retornar os valores.
    """
    with get_db() as db:
        column = getattr(Freight, column_name)
        distinct_values = db.query(column).distinct().all()
        return [value[0] for value in distinct_values]
