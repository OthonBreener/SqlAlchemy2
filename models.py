from db import Modelo
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Produto(Modelo):
    __tablename__ = 'produtos'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(64))
    fabricado: Mapped[str] = mapped_column(String(64))
    year: Mapped[int]
    pais: Mapped[str] = mapped_column(String(32))
    cpu: Mapped[str] = mapped_column(String(32))

    def __repr__(self):
        return f'Produto({self.id}, "{self.nome}")'