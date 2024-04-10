#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:10
# @Author  :   oscar
# @Desc    :   爬虫引擎
"""
import asyncio
from inspect import iscoroutine, isgenerator, isasyncgen
from typing import Optional, Generator, Callable

from craft import Request
from craft.core.scheduler import Scheduler
from craft.core.downloader import Downloader
from craft.exceptions import TransformTypeError, OutputError
from craft.spider import Spider
from craft.task_manager import TaskManager


class Engine(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.downloader: Optional[Downloader] = None
        self.start_requests: Optional[Generator] = None
        self.scheduler: Optional[Scheduler] = None
        self.spider: Optional[Spider] = None
        print(f'当前的并发数{self.settings.get_int("CONCURRENCY_NUMS")}')
        self.task_manager: Optional[TaskManager] = None
        self.running = False

    async def start_spider(self, spider):
        self.running = True
        self.spider = spider
        self.scheduler = Scheduler()
        self.task_manager = TaskManager(self.settings.get_int('CONCURRENCY_NUMS'))
        if hasattr(self.scheduler, 'open'):
            self.scheduler.open()

        self.downloader = Downloader()

        self.start_requests = iter(spider.start_requests())

        await self._open_spider()

    async def _open_spider(self):
        crawling = asyncio.create_task(self.crawl())
        await crawling
        print('*********************')

    async def crawl(self):
        """
        爬虫主逻辑
        :return:
        """
        while self.running:
            if (request := await self._get_next_request()) is not None:
                await self._crawl(request)
            else:
                try:
                    start_request = next(self.start_requests)  # noqa
                except StopIteration:
                    self.start_requests = None
                except Exception as exp:
                    # 1、发起请求的task要运行完毕
                    # 2、调度器是否空闲
                    # 3、下载器是否空闲
                    # 3 个条件同时满足才能 break
                    if not await self._exit():
                        continue
                    self.running = False
                else:
                    # 入队
                    await self.enqueue_request(start_request)

    async def _crawl(self, request):
        # TODO 1、实现并发
        async def crawl_task():
            outputs = await self._fetch(request=request)
            # TODO 2、处理 outputs
            if outputs:
                await self._handle_spider_output(outputs)

        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

    async def transform(self, funcs):
        if isgenerator(funcs):
            for func in funcs:
                yield func
        elif isasyncgen(funcs):
            async for func in funcs:
                yield func
        else:
            raise TransformTypeError('callback must be a `generator` or `async generator`!')

    async def _fetch(self, request):
        async def _successful(_response):
            callback: Callable = request.callback or self.spider.parse
            if _outputs := callback(_response):
                # 判断是否是coroutine
                if iscoroutine(_outputs):
                    await _outputs
                else:
                    return self.transform(_outputs)

        _response = await self.downloader.fetch(request)
        outputs = await _successful(_response)
        return outputs

    async def enqueue_request(self, request):
        await self.filter_request(request)

    async def filter_request(self, request):
        # TODO 去重
        await self.scheduler.enqueue_request(request=request)

    async def _get_next_request(self):
        # 出队
        return await self.scheduler.next_request()

    async def _handle_spider_output(self, outputs):
        async for spider_output in outputs:
            if isinstance(spider_output, Request):
                # 请求入队
                await self.enqueue_request(spider_output)
            # TODO 判断是不是数据
            else:
                raise OutputError(f'{type(self.spider)} must return a `Request` or a `Item`!')

    async def _exit(self):
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done():
            return True
        else:
            return False
