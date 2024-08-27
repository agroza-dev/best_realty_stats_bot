import asyncio
import sqlite3
from sqlite3 import Connection
from contextlib import asynccontextmanager
from collections.abc import Iterable
from typing import Any, AnyStr

import aiosqlite

from common.config import config


class DatabaseException(Exception):
    """Исключение, возникающее при ошибке выполнения SQL-запроса."""
    def __init__(self, message: str, sql: AnyStr, params: Iterable[Any] | None):
        super().__init__(message)
        self.sql = sql
        self.params = params

    def __str__(self):
        return f"{super().__str__()} | SQL: {self.sql} | Params: {self.params}"


@asynccontextmanager
async def in_savepoint():
    try:
        await execute('begin')  # Начало транзакции
        yield  # Здесь выполняется блок кода внутри транзакции
        await execute('commit')  # Коммит транзакции
    except Exception as e:
        await execute('rollback')  # Откат транзакции в случае ошибки
        # Если это DatabaseExecutionError, райзим его дальше
        if isinstance(e, DatabaseException):
            raise e
        else:
            raise DatabaseException("Ошибка в транзакции", "BEGIN/COMMIT", None) from e


async def get_db() -> aiosqlite.Connection:
    if not getattr(get_db, "db", None):
        db = await aiosqlite.connect(config.Db.DB_FILE)
        get_db.db = db

    return get_db.db


def get_simple_conn() -> Connection:
    return sqlite3.connect(config.Db.DB_FILE)


async def fetch_all(
    sql: AnyStr, params: Iterable[Any] | None = None
) -> list[dict]:
    cursor = await _get_cursor(sql, params)
    rows = await cursor.fetchall()
    results = []
    for row_ in rows:
        results.append(_get_result_with_column_names(cursor, row_))
    await cursor.close()
    return results


async def fetch_one(
    sql: AnyStr, params: Iterable[Any] | None = None
) -> dict | None:
    cursor = await _get_cursor(sql, params)
    row_ = await cursor.fetchone()
    if not row_:
        await cursor.close()
        return None
    row = _get_result_with_column_names(cursor, row_)
    await cursor.close()
    return row


async def execute(
    sql: AnyStr, params: Iterable[Any] | None = None, *, autocommit: bool = True
) -> None:
    db = await get_db()
    args: tuple[AnyStr, Iterable[Any] | None] = (sql, params)
    try:
        await db.execute(*args)
    except Exception as e:
        raise DatabaseException('Ошибка выполнения SQL-запроса!', sql, params) from e
    if autocommit:
        await db.commit()


def db_close() -> None:
    asyncio.run(_async_close_db())


def db_close_async() -> None:
    """
    Это нужно для миграций, так как мы запускаем миграции через asyncio,
    нужно в этом же потоке и закрывать подключение
    """
    if asyncio.get_running_loop():
        # Если уже есть активный цикл, просто вызываем асинхронную функцию
        asyncio.create_task(_async_close_db())
    else:
        # Иначе запускаем новый цикл
        asyncio.run(_async_close_db())


async def _async_close_db() -> None:
    await (await get_db()).close()


async def _get_cursor(
    sql: AnyStr, params: Iterable[Any] | None
) -> aiosqlite.Cursor:
    db = await get_db()
    args: tuple[AnyStr, Iterable[Any] | None] = (sql, params)
    cursor = await db.execute(*args)
    db.row_factory = aiosqlite.Row
    return cursor


def _get_result_with_column_names(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> dict:
    column_names = [d[0] for d in cursor.description]
    resulting_row = {}
    for index, column_name in enumerate(column_names):
        resulting_row[column_name] = row[index]
    return resulting_row

