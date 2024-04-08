#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:07
# @Contact :   heshuaihuang@gmail.com
# @Author  :   oscar
# @Desc    :   新闻爬虫测试
"""
import requests
from craft.core.engine import Engine
from craft import Request
from craft.spider import Spider


class NewsSpider(Spider):
    start_urls = ["https://www.stcn.com/article/list/kx.html", "https://www.baidu.com"]

    def parse(self, response):
        print('parse->', response)
        for i in range(10):
            url = 'https://www.baodu.com'
            request = Request(url=url, callback=self.parse_page)
            yield request

    def parse_page(self, response):
        print('parse_page->', response)
        for i in range(10):
            url = 'https://www.baodu.com'
            request = Request(url=url, callback=self.parse_detail)
            yield request

    def parse_detail(self, response):
        print('parse_detail->', response)



