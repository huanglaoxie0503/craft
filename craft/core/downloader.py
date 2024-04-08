#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:18
# @Author  :   oscar
# @Desc    :   下载器
"""
import asyncio
import time
import random
import requests


class Downloader(object):
    def __init__(self):
        pass

    async def fetch(self, request):
        return await self.download(request=request)

    async def download(self, request):
        stop_num = random.uniform(0, 1)
        await asyncio.sleep(stop_num)
        result = f'response {stop_num}'
        return result
        # print(f'response {stop_num}')
        # response = requests.get(request.url)
        # if response.status_code == 200:
        #     print(response)
