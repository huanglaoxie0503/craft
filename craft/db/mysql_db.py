#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-10 23:46
# @Author  :   oscar
# @Desc    :   使用单例模式实现MySQL连接
"""
import asyncio
import aiomysql
from typing import Dict, Any


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AsyncDB(metaclass=Singleton):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.pool = None

    async def init_pool(self, host: str, port: int, user: str, password: str, db: str, minsize: int = 5,
                        maxsize: int = 10):
        self.pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            minsize=minsize,
            maxsize=maxsize,
            loop=self.loop
        )

    async def execute(self, query: str, params: Dict[str, Any] = None) -> Any:
        assert self.pool, "Database pool is not initialized, call init_pool first"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if params:
                    await cur.execute(query, params)
                else:
                    await cur.execute(query)
                return await cur.fetchall()

    async def insert(self, table: str, data: Dict[str, Any]) -> int:
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        await self.execute(query, tuple(data.values()))
        return cur.lastrowid  # 注意：此处cur需要在execute方法内部获取

    async def update(self, table: str, conditions: Dict[str, Any], updates: Dict[str, Any]) -> int:
        set_clause = ', '.join([f"{k}=%s" for k in updates])
        where_clause = ' AND '.join([f"{k}=%s" for k in conditions])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        await self.execute(query, (*updates.values(), *conditions.values()))
        return cur.rowcount  # 同样，此处cur需要在execute方法内部获取

    async def delete(self, table: str, conditions: Dict[str, Any]) -> int:
        where_clause = ' AND '.join([f"{k}=%s" for k in conditions])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        await self.execute(query, tuple(conditions.values()))
        return cur.rowcount  # 同理，此处cur也需要在execute方法内部获取


# 使用方式：
async def main():
    db = AsyncDB()
    await db.init_pool('localhost', 3306, 'root', 'password', 'test_db')
    # 进行CRUD操作...


asyncio.run(main())