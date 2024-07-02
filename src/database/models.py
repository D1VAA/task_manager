from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
#from sqlalchemy import ForeignKey

class Base(DeclarativeBase):...

class Freight(Base):
    __tablename__ = 'freight'
    id: Mapped[int] = mapped_column(primary_key=True)
    origem: Mapped[str] = mapped_column(nullable=False)
    destino: Mapped[str] = mapped_column(nullable=False)
    client: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)
