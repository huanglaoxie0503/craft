#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 17:26
# @Author  :   oscar
# @Desc    :   封装优先级队列
"""
import asyncio
from asyncio import PriorityQueue, TimeoutError


class SpiderPriorityQueue(PriorityQueue):
    def __init__(self, maxsize=0):
        super(SpiderPriorityQueue, self).__init__(maxsize=maxsize)

    async def get(self):
        coro = super().get()
        try:
            return await asyncio.wait_for(coro, timeout=0.1)
        except TimeoutError:
            return None
