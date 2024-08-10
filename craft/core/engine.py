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
from craft.downloader import DownloaderBase
from craft.core.processor import Processor
from craft.exceptions import TransformTypeError, OutputError
from craft.items.items import Item
from craft.spider import Spider
from craft.task_manager import TaskManager
from craft.utils.log import get_logger
from craft.utils.tools import load_class


class Engine(object):
    def __init__(self, crawler):
        self.log = get_logger(self.__class__.__name__)
        self.crawler = crawler
        self.settings = crawler.settings
        self.downloader: Optional[DownloaderBase] = None
        self.processor: Optional[Processor] = None
        self.start_requests: Optional[Generator] = None
        self.scheduler: Optional[Scheduler] = None
        self.spider: Optional[Spider] = None
        print(f'当前的并发数{self.settings.get_int("CONCURRENCY_NUMS")}')
        self.task_manager: Optional[TaskManager] = None
        self.running = False

    def _get_downloader(self):
        downloader_cls = load_class(self.settings.get('DOWNLOADER'))
        if not issubclass(downloader_cls, DownloaderBase):
            raise TypeError(f"{downloader_cls} The Downloader is not a subclass of {DownloaderBase}")
        return downloader_cls

    async def start_spider(self, spider):
        self.running = True
        self.log.info(f"info Spider started. (spider name: {self.settings.get('SPIDER_NAME')})")
        self.spider = spider
        self.processor = Processor(self.crawler)
        self.task_manager = TaskManager(self.settings.get_int('CONCURRENCY_NUMS'))
        # 调度器
        self.scheduler = Scheduler()
        if hasattr(self.scheduler, 'open'):
            self.scheduler.open()

        # 下载器
        # self.downloader = Downloader(self.crawler)
        # self.downloader = HttpxDownloader(crawler=self.crawler)
        downloader_cls = self._get_downloader()  # load_class(self.settings.get('DOWNLOADER'))
        self.downloader = downloader_cls(self.crawler)
        if hasattr(self.downloader, 'open'):
            self.downloader.open()

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
                    if self.start_requests is not None:
                        self.log.error(f"Error in crawling start_requests: {exp}")
                else:
                    # 入队
                    await self.enqueue_request(start_request)
        if not self.running:
            await self.close_spider()

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
        if _response is None:
            return None
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
            if isinstance(spider_output, (Request, Item)):
                # 入队
                await self.processor.enqueue(spider_output)
            else:
                raise OutputError(f'{type(self.spider)} must return a `Request` or a `Item`!')

    async def _exit(self):
        if self.scheduler.idle() and self.downloader.idle() and self.task_manager.all_done() and self.processor.idle():
            return True
        else:
            return False

    async def close_spider(self):
        await self.downloader.close()
