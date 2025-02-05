#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-10 17:16
# @Author  :   oscar
# @Desc    :   None
"""
from typing import Optional
from aiohttp import ClientSession, TCPConnector, BaseConnector, ClientTimeout, ClientResponse, TraceConfig

from craft import Response
from craft.downloader import DownloaderBase


class AioHttpDownloader(DownloaderBase):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.session: Optional[ClientSession] = None
        self._user_session: Optional[bool] = None
        self.connector: Optional[BaseConnector] = None
        self._verify_ssl: Optional[bool] = None
        self._timeout: Optional[ClientTimeout] = None
        self.trace_configs: Optional[TraceConfig] = None
        self.request_method = {
            'get': self._get,
            'post': self._post
        }

    def open(self):
        super().open()
        timeout = self.crawler.settings.get_int('TIMEOUT')
        self._timeout = ClientTimeout(total=timeout)
        self._verify_ssl = self.crawler.settings.get_bool('VERIFY_SSL')
        self.trace_configs = TraceConfig()
        self.trace_configs.on_request_start.append(self.request_start)
        self._user_session = self.crawler.settings.get_bool('USER_SESSION')
        if self._user_session:
            self.connector = TCPConnector(verify_ssl=self._verify_ssl)
            self.session = ClientSession(
                connector=self.connector, timeout=self._timeout, trace_configs=[self.trace_configs]
            )

    async def request_start(self, _session, _trace_config_ctx, params):
        self.logger.debug(f'Request start: {params.url}, method: {params.method}')

    async def fetch(self, request) -> Optional[Response]:
        async with self._active(request):
            response = await self.download(request=request)
            return response

    async def download(self, request) -> Optional[Response]:
        try:
            if self._user_session:
                response = await self.send_request(self.session, request)
                body = await response.read()
            else:
                connector = TCPConnector(verify_ssl=self._verify_ssl)
                async with ClientSession(
                        connector=connector, timeout=self._timeout, trace_configs=[self.trace_configs]
                ) as session:
                    response = await self.send_request(session, request)
                    body = await response.read()
        except Exception as exp:
            self.logger.error(f'Error downloading {request}: {exp}')
            raise exp
        return self.structure_response(request, response, body)

    @staticmethod
    def structure_response(request, response, body):
        return Response(
            url=response.url,
            headers=dict(response.headers),
            status_code=response.status,
            body=body,
            request=request
        )

    async def send_request(self, session, request) -> ClientResponse:
        try:
            return await self.request_method[request.method.lower()](session, request)
        except KeyError as exp:
            self.logger.error(f'Error downloading {request}: {exp}')
            raise exp

    @staticmethod
    async def _get(session, request) -> ClientResponse:
        response = await session.get(
            request.url,
            headers=request.headers,
            cookies=request.cookies,
            # proxy=request.proxy
        )
        return response

    @staticmethod
    async def _post(session, request) -> ClientResponse:
        response = await session.post(
            request.url,
            data=request.body,
            headers=request.headers,
            cookies=request.cookies,
            # proxy=request.proxy
        )
        return response

    async def close(self):
        if self.connector:
            await self.connector.close()
        if self.session:
            await self.session.close()
