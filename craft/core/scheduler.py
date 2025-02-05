#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:49
# @Author  :   oscar
# @Desc    :   调度器
"""
import asyncio
from typing import Optional

from craft.event import request_scheduled
from craft.utils.pqueue import SpiderPriorityQueue
from craft.utils.log import get_logger


class Scheduler:
    def __init__(self, crawler):
        self.crawler = crawler
        self.request_queue: Optional[SpiderPriorityQueue] = None
        self.logger = get_logger(self.__class__.__name__, self.crawler.settings.get('LOG_LEVEL'))
        self.item_count = 0
        self.response_count = 0

    def open(self):
        self.request_queue = SpiderPriorityQueue()

    async def next_request(self):
        request = await self.request_queue.get()
        return request

    async def enqueue_request(self, request):
        await self.request_queue.put(request)
        asyncio.create_task(self.crawler.subscriber.notify(request_scheduled, request, self.crawler.spider))
        self.crawler.stats.inc_value(key='request_scheduler_count')

    async def interval_log(self, interval=3):
        while True:
            last_item_count = self.crawler.stats.get_value('item_successful_count', default=0)
            last_response_count = self.crawler.stats.get_value('response_received_count', default=0)
            item_rate = last_item_count - self.item_count
            response_rate = last_response_count - self.response_count
            self.item_count, self.response_count = last_item_count, last_response_count
            self.logger.info(f"Crawled {last_response_count} pages (at {response_rate:.2f} pages/{interval}s),"
                             f"Got {last_item_count} items (at {item_rate:.2f} items/{interval}s)")
            await asyncio.sleep(interval)

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return self.request_queue.qsize()
