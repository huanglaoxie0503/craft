#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-09 02:10
# @Author  :   oscar
# @Desc    :   None
"""
from asyncio import create_task, Task, Future, Semaphore
from typing import Final, Set


class TaskManager:

    def __init__(self, concurrency_nums=8):
        # 初始化当前任务集合和信号量
        self.current_task: Final[Set[Task]] = set()  # 当前正在运行的任务集合
        self.semaphore: Semaphore = Semaphore(concurrency_nums)  # 控制并发数量的信号量

    async def create_task(self, coroutine) -> Task:
        # 在创建新任务之前获取信号量以限制并发数
        await self.semaphore.acquire()

        # 创建一个新的异步任务并将其添加到当前任务集合中
        task = create_task(coroutine)
        self.current_task.add(task)

        # 定义任务完成后的回调函数
        def done_callback(finished_task: Task) -> None:
            # 确保只移除存在的任务，防止 KeyError 错误
            if finished_task in self.current_task:
                self.current_task.remove(finished_task)
            # 释放信号量，允许新的任务开始
            self.semaphore.release()

        # 将回调函数添加到任务中
        task.add_done_callback(done_callback)

        return task

    def all_done(self) -> bool:
        # 检查所有任务是否已经完成
        return len(self.current_task) == 0
