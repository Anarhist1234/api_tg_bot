from typing import Any

from psycopg.rows import dict_row
import asyncpg
import psycopg
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from typing import Union, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection

from config import DatabaseConfig, ADatabaseConfig, AsteriskDatabaseConfig

engine = create_engine(DatabaseConfig.DB_URL, pool_size=40, max_overflow=0)
Base = declarative_base()

acs_engine = create_engine(DatabaseConfig.DB_URL, isolation_level="READ UNCOMMITTED", query_cache_size=0)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
AcsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=acs_engine, class_=Session)


def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


AsyncEngine = create_async_engine(
    ADatabaseConfig.DB_URL
)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=AsyncEngine, class_=AsyncSession)


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


class BasePgDriver:

    def get_default_row_factory(self): ...

    def __init__(self,
                 db_dsn: str = None,
                 db_name: str = DatabaseConfig.DB_NAME,
                 db_user: str = DatabaseConfig.DB_USER,
                 db_host: str = DatabaseConfig.DB_HOST,
                 db_port: str = DatabaseConfig.DB_PORT,
                 db_password: str = DatabaseConfig.DB_PASSWORD,
                 row_factory: callable = None
                 ):
        """   """
        self._db_name = db_name
        self._db_password = db_password
        self._db_user = db_user
        self._db_host = db_host
        self._db_port = db_port
        self._dsn = db_dsn
        if row_factory:
            self._row_factory = row_factory

        if any([self._db_name, self._db_password, self._db_port, self._db_user, self._db_host]):
            if self._dsn is not None:
                raise ValueError("Если заполняется DSN, остальные поля должны быть пустыми")
            if not all([self._db_name, self._db_password, self._db_port, self._db_user, self._db_host]):
                raise ValueError("В драйвере заполнены не все поля для подключения к БД")
            self._dsn = f"postgresql://{self._db_user}:{self._db_password}@{self._db_host}:{self._db_port}/{self._db_name}"
        else:
            if not self._dsn:
                self._dsn = DatabaseConfig.DB_URL


class APgDriver(BasePgDriver):

    def _get_default_row_factory(self): return dict_row

    async def __aenter__(self):
        self.conn = await psycopg.AsyncConnection.connect(self._dsn, row_factory=self._get_default_row_factory())
        self.curr = self.conn.cursor()
        return self.curr

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.commit()
        await self.conn.close()
        await self.curr.close()


class PgDriver(BasePgDriver):
    """
    Контекстный менеджер для работы с БД прямыми SQL запросами.
    Usage:
        from core.services.database import PgDriver
        with PgDriver() as curr:
            curr.execute("SELECT first_name, last_name FROM usession")
            result = curr.fetchall()
            for row in result:
                print(row["first_name"], row["last_name"])
    Usage with SqlAlchemy models:
        from core.models.operator import Operator
        from core.services.database import PgDriver
        with PgDriver() as curr:
            curr.execute("SELECT * FROM operators")
            items = curr.fetchall()
        if not items:
            return None
        return [Operator(**item) for item in items]
    """

    def _get_default_row_factory(self): return RealDictCursor

    def __enter__(self):
        self.conn = psycopg2.connect(self._dsn, cursor_factory=self._get_default_row_factory())
        self.curr = self.conn.cursor()
        return self.curr

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
        self.curr.close()

