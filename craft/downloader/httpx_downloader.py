#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-10 17:16
# @Author  :   oscar
# @Desc    :   None
"""
from typing import Optional
from httpx import AsyncClient, Timeout

from craft import Response
from craft.downloader import DownloaderBase


class HttpxDownloader(DownloaderBase):
    def __init__(self, crawler):
        super().__init__(crawler)
        self._client: Optional[AsyncClient] = None
        self._timeout: Optional[Timeout] = None

    def open(self):
        super().open()
        timeout = self.crawler.settings.get_int('TIMEOUT')
        self._timeout = Timeout(timeout=timeout)

    async def fetch(self, request) -> Optional[Response]:
        async with self._active(request):
            response = await self.download(request=request)
            return response

    async def download(self, request) -> Optional[Response]:
        try:
            proxies = None # request.proxy
            async with AsyncClient(timeout=self._timeout, proxies=proxies) as client:
                self.logger.debug(f'Request start: {request.url}, method: {request.method}')
                response = await client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    cookies=request.cookies,
                    data=request.body
                )
                body = await response.aread()
        except Exception as exp:
            self.logger.error(f'ERROR during request: {request.url}')
            raise exp

        return self.structure_response(request, response, body)

    @staticmethod
    def structure_response(request, response, body) -> Response:
        return Response(
            url=response.url,
            headers=dict(response.headers),
            status_code=response.status_code,
            body=body,
            request=request
        )

