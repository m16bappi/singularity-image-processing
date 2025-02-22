from threading import Lock
from sqlalchemy import Engine
from typing import Self, Optional
from sqlmodel import SQLModel, create_engine, Session

from .image import ImageMetadata

__all__ = [
    "ImageMetadata",
    "db",
]


class Database:
    engine: Engine
    _instance: Optional[Self] = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is not None:
                return cls._instance

            cls._instance = super().__new__(cls)
            cls._instance.engine = create_engine("sqlite:///./database.db", echo=True)
            cls._instance._initialize_database()
        return cls._instance

    def _initialize_database(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        with Session(self.engine) as session:
            yield session


db = Database()
