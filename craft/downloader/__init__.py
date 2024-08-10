#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-10 17:15
# @Author  :   oscar
# @Desc    :   None
"""
from abc import abstractmethod
from typing import Final, Set, Optional
from contextlib import asynccontextmanager

from craft import Response, Request
from craft.utils.log import get_logger


class DownloaderBase(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self._active = ActiveRequestManager()
        self.logger = get_logger(self.__class__.__name__, self.crawler.settings.get('LOG_LEVEL'))

    @classmethod
    def create_instance(cls, *args, **kwargs) -> 'DownloaderBase':
        return cls(*args, **kwargs)

    def open(self):
        self.logger.info(
            f'{self.crawler.spider} <downloader class：{type(self).__name__}>'
            f' <concurrency：{self.crawler.settings.get_int("CONCURRENCY_NUMS")}>'
        )

    async def fetch(self, request) -> Optional[Response]:
        async with self._active(request):
            response = await self.download(request=request)
            return response

    @abstractmethod
    async def download(self, request: Request) -> Response:
        raise NotImplementedError

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._active)

    async def close(self):
        pass


class ActiveRequestManager(object):
    def __init__(self):
        self._active: Final[Set] = set()

    def add(self, request):
        self._active.add(request)

    def remove(self, request):
        self._active.remove(request)

    def __len__(self):
        return len(self._active)

    @asynccontextmanager
    async def __call__(self, request):
        try:
            yield self.add(request=request)
        finally:
            self.remove(request=request)
