#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:23
# @Author  :   oscar
# @Desc    :   None
"""
import time
import asyncio

from tests.news_spider.spiders.news import NewsSpider
from tests.news_spider.spiders.news2 import NewsSpider2
from craft.crawler import CrawlerProcess
from craft.utils.tools import get_settings


async def main():
    settings = get_settings()
    process = CrawlerProcess(settings)
    await process.crawl(NewsSpider)
    # await process.crawl(NewsSpider2)
    await process.start()


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())

    end_time = time.time()

    print('Total time: {} seconds'.format(end_time - start_time))
