from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, column
from typing import Optional


class Base(DeclarativeBase):
    ...


class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    creation_date: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    updates = relationship("Updates", backref='task')
    # Coluna para referência da outra tarefa.
    dependency_id: Mapped[Optional[int]] = mapped_column(Integer,
                                                         ForeignKey("tasks.id"),
                                                         nullable=True)
    #
    dependency: Mapped[Optional["Task"]] = relationship("Task",
                                                        remote_side=[id],
                                                        backref="dependent_tasks")


class Updates(Base):
    __tablename__ = 'updates'
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    description: Mapped[str] = mapped_column(nullable=True)
    creation_date: Mapped[str] = mapped_column(nullable=False)
