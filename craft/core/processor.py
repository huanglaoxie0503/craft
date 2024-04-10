#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-11 02:17
# @Author  :   oscar
# @Desc    :   None
"""
from asyncio import Queue
from craft import Request, Item


class Processor(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.queue: Queue = Queue()

    async def process(self):
        # 出队
        while not self.idle():
            # 队列不空闲，则取数据
            result = await self.queue.get()
            if isinstance(result, Request):
                await self.crawler.engine.enqueue_request(result)
            else:
                assert isinstance(result, Item)
                await self._process_item(result)

    async def _process_item(self, item):
        print(item)

    async def enqueue(self, output):
        await self.queue.put(output)
        await self.process()

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return self.queue.qsize()
