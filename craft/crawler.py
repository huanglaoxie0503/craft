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

from craft.spider import Spider
from craft.event import spider_opened, spider_closed
from craft.core.engine import Engine
from craft.subscriber import Subscriber
from craft.exceptions import SpiderTypeError
from craft.utils.tools import merge_settings
from craft.utils.log import get_logger
from craft.utils.common import get_now
from craft.utils.stats_collector import StatsCollector
from craft.settings.settings_manager import SettingsManager

logger = get_logger(__name__)


class Crawler(object):

    def __init__(self, spider_cls, settings):
        self.spider_cls = spider_cls
        self.settings: SettingsManager = settings.copy()
        self.spider: Optional[Spider] = None
        self.engine: Optional[Engine] = None
        self.stats: Optional[StatsCollector] = None
        self.subscriber: Optional[Subscriber] = None

    async def crawl(self):
        self.subscriber = self._create_subscriber()
        self.spider = self._create_spider()
        self.engine = self._create_engine()
        self.stats = self._create_stats()
        await self.engine.start_spider(self.spider)

    def _create_spider(self) -> Spider:
        spider = self.spider_cls.create_instance(self)
        self._set_spider(spider)
        return spider

    def _create_engine(self) -> Engine:
        engine = Engine(self)
        return engine

    def _create_stats(self) -> StatsCollector:
        stats = StatsCollector(self)
        stats['start_time'] = get_now()
        return stats

    @staticmethod
    def _create_subscriber():
        subscriber = Subscriber()
        return subscriber

    def _set_spider(self, spider):
        self.subscriber.subscribe(event_name=spider_opened, receiver=spider.spider_opened)
        self.subscriber.subscribe(event_name=spider_closed, receiver=spider.spider_closed)
        merge_settings(spider, self.settings)

    async def close(self, reason='finished') -> None:
        notify_task = asyncio.create_task(self.subscriber.notify(event_name=spider_closed, reason=reason))
        self.stats.close_spider(self.spider, reason=reason)
        await notify_task  # 等待通知完成


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
            crawler.engine.normal = False
            crawler.stats.close_spider(crawler.spider, 'ctrl c')
        logger.warning(f'Crawler received "Ctrl C" signal {signum}, shutting down.')
