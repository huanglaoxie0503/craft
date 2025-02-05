#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:25
# @Author  :   oscar
# @Desc    :   None
"""
from craft import Request


class Spider(object):
    def __init__(self):
        if not hasattr(self, 'start_urls'):
            self.start_urls = []
        self.crawler = None

    @classmethod
    def create_instance(cls, crawler):
        o = cls()
        o.crawler = crawler
        return o

    def start_requests(self):
        if self.start_urls:
            for url in self.start_urls:
                yield Request(url=url)
        else:
            if hasattr(self, 'start_url') and isinstance(getattr(self, 'start_url'), str):
                yield getattr(self, 'start_url')

    def parse(self, response):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    async def spider_opened(self):
        pass

    async def spider_closed(self, reason):
        pass
