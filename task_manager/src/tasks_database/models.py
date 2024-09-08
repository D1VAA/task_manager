from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from sqlalchemy import ForeignKey, Table, Column
from typing import List, Optional


class Base(DeclarativeBase):
    ...

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    creation_date: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    updates: Mapped[List["Updates"]] = relationship("Updates", backref='task')
    dependencies: Mapped[List["Task"]] = relationship(
        secondary='task_dependencies',
        primaryjoin=id == 'task_dependencies.task_id',
        secondaryjoin=id == 'task_dependencies.dependency_id',
        backref=backref('dependent_tasks', lazy='dinamic')
    )

task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column('task_id', ForeignKey('tasks.id'), primary_key=True),
    Column('dependency_id', ForeignKey('tasks.id'), primary_key=True),
)

class Updates(Base):
    __tablename__ = 'updates'
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    description: Mapped[str] = mapped_column(nullable=True)
    creation_date: Mapped[str] = mapped_column(nullable=False)
