from sqlalchemy import create_engine, delete
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from src.model.tasks_structure import TaskObj
from src.model.updates_strcuture import Update
from .models import Task, Updates
from typing import Dict, Any, List, Optional
from sqlalchemy.exc import IntegrityError

load_dotenv(f"{os.getcwd()}/src/tasks_database/.env")
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL cannot be None.")

try:
    engine = create_engine(DATABASE_URL)
    LocalSession = sessionmaker(autocommit=False,
                                autoflush=False,
                                bind=engine)
except Exception as e:
    raise ValueError(f"Failed to create engine: {e}")

try:
    LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise ValueError(f"Failed to create sessionmaker: {e}")


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
        if (
            quick_query(Task, {"name": name}) is not None
            or quick_query(Task, {"description": description}) is not None
        ):
            raise ValueError("Task already exists.")
        try:
            new_task = Task(
                name=name,
                description=description,
                creation_date=creation_date,
                status=status,
            )
            db.add(new_task)
            db.commit()
            return {"message": "Task created succesfully.", 
                    'task_id': new_task.id}
        except Exception as e:
            print(e)


def delete_all_updates_from_task(task_id):
    with get_db() as db:
        delete_stmt = delete(Updates).where(Updates.task_id == task_id)
        db.execute(delete_stmt)
        db.commit()


def delete_task(task_id):
    with get_db() as db:
        if quick_query(Task, {"id": task_id}) is not None:
            task = db.get(Task, task_id)
            if task is not None:
                try:
                    db.delete(task)
                    db.commit()
                except IntegrityError:
                    db.rollback()
                    delete_all_updates_from_task(task_id)
                    delete_task(task_id)

                except Exception as e:
                    db.rollback()
                    print("[!] Error while deleting task from database: ",e)


def update_task(name=None, 
                description=None, 
                status=None, 
                updates=None, 
                dependencies=None, 
                task_id=None):
    with get_db() as db:
        if name is None and task_id is None:
            print("[!] A name or a task ID must be informed.")

        if task_id is not None:
            task = db.get(Task, task_id)

        else:
            task = db.query(Task).filter_by(name=name).first()

        if task is not None:
            try:
                # if (task.name == name and task.description == description and task.status == status, task.updates == updates, task.dependencies == dependencies): return None
                if name is not None:
                    task.name = name
                if description is not None:
                    task.description = description
                if status is not None:
                    task.status = status
                if updates is not None:
                    for desc, cd in updates.items():
                        create_update(task_id=task.id,
                                      description=desc,
                                      creation_date=cd)
                if dependencies is not None:
                    for did in dependencies:
                        create_dependencie(main_t_id=task.id, 
                                           dependent_t_id=did)

                db.commit()
            except sqlalchemy.exc.IntegrityError as e:
                db.rollback()
                raise sqlalchemy.exc.IntegrityError(
                    f"Error updating task: {e}")
            except:
                db.rollback()
        else:
            raise ValueError(f"[!] Task with ID {task_id} not found.")


def get_tasks_excluding_status(status):
    with get_db() as db:
        tasks = (
            db.query(Task).filter(Task.status !=
                                  status).order_by(Task.id.asc()).all()
        )
        task_dict = {}
        for cont, task in enumerate(tasks):
            updates = {c+1: up for c, up in enumerate(task.updates)}
            dependencies = {tasks.index(d)+1: d for d in task.dependencies}
            task_dict[cont + 1] = TaskObj(
                task.name,
                task.description,
                task.creation_date,
                task.id,
                task.status,
                updates,
                dependencies
            )
        task_dict_copy = task_dict.copy()
        return task_dict_copy


def get_task_id(name, description=None):
    try:
        if description is not None:
            query = quick_query(Task, {"name": name, "description": description})
            assert query is not None
            return int(query.id)
        query = quick_query(Task, {"name": name})
        assert query is not None
        return int(query.id)
    except:
        ...


def get_update_id(description: str):
    try:
        query = quick_query(Updates, {"description": description})
        if query is not None:
            return int(query.id)
    except:
        ...


def create_update(task_id: int, description: str, creation_date: str):
    with get_db() as db:
        try:
            if (
                quick_query(Updates, {"task_id": task_id,
                            "description": description})
                is not None
            ):
                raise ValueError("Update already exists.")
            new_update = Updates(
                task_id=task_id, description=description, creation_date=creation_date
            )
            task_to_update = db.query(Task).filter(Task.id == task_id).first()
            assert task_to_update is not None
            task_to_update.updates.append(new_update)
            db.commit()

        except:
            db.rollback()


def delete_update(update_id: int) -> None:
    with get_db() as db:
        try:
            update_to_delete = db.query(Updates).filter_by(id=update_id).first()
            if update_to_delete is None:
                raise ValueError(f"Update with ID: {update_id} not found.")
            db.delete(update_to_delete)
            db.commit()

        except Exception as e:
            print(f"An error occurred while deleting the update: {e}")
            db.rollback()


def get_updates_by_task(task_id: int) -> Dict[int, Dict[int, Update]]:
    with get_db() as db:
        updates = (
            db.query(Updates)
            .filter(Updates.task_id == task_id)
            .order_by(Updates.id.asc())
            .all()
        )
        updates_dict = {}
        if task_id not in updates_dict.keys():
            updates_dict[task_id] = {}
        for update in updates:
            updates_dict[update.id] = Update(
                update.description, update.creation_date, update.id
            )
        return updates_dict


def get_all_updates(task_ids: List[int] | None = None) -> Dict[int, Dict[int, Update]]:
    with get_db() as db:
        # Pega todos os updates na database
        if task_ids is None:
            updates = db.query(Updates).order_by(Updates.id.asc()).all()
        else:
            updates = (
                db.query(Updates)
                .filter(Updates.task_id.in_(task_ids))
                .order_by(Updates.id.asc())
                .all()
            )

        updates_dict = {}
        for update in updates:
            task_id = update.task_id
            if task_id not in updates_dict.keys():
                updates_dict[task_id] = {}

            # Contador para a quantidade de updates de cada task. Se o dicionário de updates para aquela task estiver vazio, ele atribui o valor 1
            cont = len(updates_dict[task_id].keys()) + 1
            updates_dict[task_id][cont] = Update(
                update.description, update.creation_date, update.id
            )
        updates_dict_copy = updates_dict.copy()
        return updates_dict_copy


def edit_update(description=None, task_id=None, update_id=None):
    with get_db() as db:
        if description is None and update_id is None:
            print("[!] A name or a update_id must be informed.")
        if update_id is not None:
            update = db.get(Updates, update_id)
        else:
            update = db.query(Updates).filter_by(
                description=description).first()
        if update is not None:
            try:
                if update.description == description and update.task_id == task_id:
                    return None
                if description is not None:
                    update.description = description
                if task_id is not None:
                    update.task_id = task_id
                db.commit()
            except sqlalchemy.exc.IntegrityError as e:
                print(f"Error updating task: {e}")
                db.rollback()
            except Exception as e:
                print(e)
                db.rollback()
        else:
            print(f"[!] Task with {task_id} not found.")
        
def create_dependencie(main_t_id: int, dependent_t_id: int):
    with get_db() as db:
        try:
            main_task = db.get(Task, main_t_id)
            dependent_task = db.get(Task, dependent_t_id)
            assert main_task is not None and dependent_task is not None
            main_task.dependencies.append(dependent_task)
            db.commit()

        except:
            db.rollback()

def delete_dependencie(main_t_id: int, dependent_t_id: int):
    with get_db() as db:
        try:
            main_task = db.get(Task, main_t_id)
            dependent_task = db.get(Task, dependent_t_id)
            assert main_task is not None and dependent_task is not None
            main_task.dependencies.remove(dependent_task)
            db.commit()

        except:
            db.rollback()
