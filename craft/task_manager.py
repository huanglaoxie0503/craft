#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-09 02:10
# @Author  :   oscar
# @Desc    :   None
"""
import asyncio
from typing import Set, Final
from asyncio import Task, Future, Semaphore


class TaskManager:

    def __init__(self, concurrency_nums=8):
        self.current_task: Final[Set] = set()
        self.semaphore: Semaphore = Semaphore(concurrency_nums)

    def create_task(self, coroutine) -> Task:
        task = asyncio.create_task(coro=coroutine)
        self.current_task.add(task)

        def done_callback(_fut: Future) -> None:
            self.current_task.remove(task)
            self.semaphore.release()

        task.add_done_callback(done_callback)

        return task

    def all_done(self) -> bool:
        return len(self.current_task) == 0
