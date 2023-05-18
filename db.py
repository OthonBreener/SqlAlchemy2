from dotenv import load_dotenv
from os import getenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase

class Modelo(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_lable)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)",
        }
    )

load_dotenv()

engine = create_engine(getenv('DATABASE_URL'))
Modelo.metadata.create_all(engine)