from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
#from sqlalchemy import ForeignKey

class Base(DeclarativeBase):...

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    creation_date: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
