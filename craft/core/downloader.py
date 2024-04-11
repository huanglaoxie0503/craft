#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-08 16:18
# @Author  :   oscar
# @Desc    :   下载器
"""
import asyncio
import aiohttp
import httpx
import random


class Downloader(object):
    def __init__(self):
        self._active = set()

    async def fetch(self, request):
        self._active.add(request)
        response = await self.download(request=request)
        self._active.remove(request)
        return response

    async def download(self, request):
        stop_num = random.uniform(0, 1)
        await asyncio.sleep(stop_num)
        result = f'response {stop_num}'
        return result
        # print(f'response {stop_num}')
        # response = requests.get(request.url)
        # if response.status_code == 200:
        #     print(response)

    def idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._active)

