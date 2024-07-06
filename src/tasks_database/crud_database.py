from sqlalchemy import create_engine, asc
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from .tasks_storage import TaskObj
from .models import Task
from typing import Dict, Any, Optional

load_dotenv(f'{os.getcwd()}/src/tasks_database/.env')
DATABASE_URL = os.getenv('TASKS_DATABASE_URL')
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

def create_task(name: str, 
                description: Optional[str], 
                creation_date: str, 
                status: str):
    with get_db() as db:
        if quick_query(Task, {'name':name}) is not None:
            raise ValueError('Task already exists.')
        new_freight = Task(name=name, 
                           description=description, creation_date=creation_date, 
                           status=status)
        db.add(new_freight)
        db.commit()
        return {'message': f'Task created succesfully.'}

def delete_task(task_id):
    with get_db() as db:
        if quick_query(Task, {"id":task_id}) is not None:
            task = db.get(Task, task_id)
            if task is not None:
                try:
                    db.delete(task)
                    db.commit()
                    return {'message': f'Task delted succesfully.'}
                except:
                    db.rollback()

def update_task(name, description, status, task_id=None):
    with get_db() as db:
        if task_id is not None:
            task = db.get(Task, task_id)
        else:
            task = db.query(Task).filter_by(name=name).first()

        if task is not None:
            try:
                task.name = name
                task.description = description
                task.status = status
                db.commit()
            except Exception as e:
                print(e)
                db.rollback()
        else:
            print(f"[!] Task with {task_id} not found.")

def get_tasks_excluding_status(status):
    with get_db() as db:
        tasks = db.query(Task).filter(Task.status != status).order_by(Task.id.asc()).all()
        task_dict = {}
        for cont, task in enumerate(tasks):
            task_dict[cont+1] = TaskObj(task.name, 
                                 task.description, 
                                 task.creation_date,
                                 task.status)
        return task_dict


def get_task_id(name):
    try:
        return quick_query(Task, {'name':name}).id
    except:
        pass
