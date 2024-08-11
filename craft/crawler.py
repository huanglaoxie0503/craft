#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-10 23:36
# @Author  :   oscar
# @Desc    :   None
"""
import signal
import asyncio
from typing import Type, Final, Set, Optional

from craft.exceptions import SpiderTypeError
from craft.spider import Spider
from craft.core.engine import Engine
from craft.settings.settings_manager import SettingsManager
from craft.utils.tools import merge_settings
from craft.utils.log import get_logger

logger = get_logger(__name__)


class Crawler(object):

    def __init__(self, spider_cls, settings):
        self.spider_cls = spider_cls
        self.settings: SettingsManager = settings.copy()
        self.spider: Optional[Spider] = None
        self.engine: Optional[Engine] = None

    async def crawl(self):
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        await self.engine.start_spider(self.spider)

    def _create_spider(self) -> Spider:
        spider = self.spider_cls.create_instance(self)
        self._set_spider(spider)
        return spider

    def _create_engine(self) -> Engine:
        engine = Engine(self)
        return engine

    def _set_spider(self, spider):
        merge_settings(spider, self.settings)


class CrawlerProcess(object):

    def __init__(self, settings=None):
        self.crawlers: Final[Set] = set()
        self._active_spiders: Final[Set] = set()
        self.settings = settings

        signal.signal(signal.SIGINT, self._shutdown)

    async def crawl(self, spider: Type[Spider]):
        crawler: Crawler = self._create_crawler(spider)
        self.crawlers.add(crawler)
        task = await self._crawl(crawler)
        self._active_spiders.add(task)

    @staticmethod
    async def _crawl(crawler):
        return asyncio.create_task(crawler.crawl())

    async def start(self):
        await asyncio.gather(*self._active_spiders)

    def _create_crawler(self, spider_cls) -> Crawler:
        if isinstance(spider_cls, str):
            raise SpiderTypeError(f'{type(self)}.crawl args: String not supported.')
        crawler = Crawler(spider_cls, self.settings)
        return crawler

    def _shutdown(self, signum, frame):
        for crawler in self.crawlers:
            crawler.engine.running = False
        logger.warning(f'Crawler received "ctrl c" signal {signum}, shutting down.')
