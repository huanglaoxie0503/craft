#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:23
# @Author  :   oscar
# @Desc    :   None
"""
import asyncio

from craft.core.engine import Engine
from tests.news_spider.news import NewsSpider


async def main():
    news_spider = NewsSpider()
    engine = Engine()
    await engine.start_spider(news_spider)


if __name__ == '__main__':
    asyncio.run(main())
