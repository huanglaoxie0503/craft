#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-11 13:40
# @Author  :   oscar
# @Desc    :   中间件
"""
from typing import List, Dict, Callable, Optional
from types import MethodType
from pprint import pformat
from collections import defaultdict

from craft import Request, Response
from craft.exceptions import MiddlewareInitError, InvalidOutputError, RequestMethodError
from craft.middleware import BaseMiddleware
from craft.utils.log import get_logger
from craft.utils.tools import load_class, common_callback


class MiddlewareManager:
    def __init__(self, crawler):
        self.crawler = crawler
        self.middlewares: List = []
        self.methods: Dict[str, List[MethodType]] = defaultdict(list)
        self.logger = get_logger(self.__class__.__name__, self.crawler.settings.get('LOG_LEVEL'))
        middlewares = self.crawler.settings.get_list('MIDDLEWARES')
        self._add_middleware(middlewares)
        self._add_method()

        self.download_method: Callable = crawler.engine.downloader.download
        self._stats = crawler.stats

    async def _process_request(self, request: Request):
        for method in self.methods['process_request']:
            result = await common_callback(method, request, self.crawler.spider)
            if result is None:
                continue
            if isinstance(result, (Request, Response)):
                return result
            raise InvalidOutputError(
                f"{method.__qualname__} must return None, Request or Response, got {type(result).__name__}"
            )
        return await self.download_method(request)

    async def _process_response(self, request: Request, response: Response):
        for method in reversed(self.methods['process_response']):
            response = await common_callback(method, request, response, self.crawler.spider)
            if isinstance(response, Request):
                return response
            if isinstance(response, Response):
                continue
            raise InvalidOutputError(
                f"{method.__qualname__} must return Request or Response, got {type(response).__name__}"
            )
        return response

    async def _process_exception(self, request: Request, exp: Exception):
        for method in reversed(self.methods['process_exception']):
            response = await common_callback(method, request, exp, self.crawler.spider)
            if response is None:
                continue
            if isinstance(response, (Request, Response)):
                return response
            raise InvalidOutputError(
                f"{method.__qualname__} must return None, Request or Response, got {type(response).__name__}"
            )
        else:
            raise exp

    async def download(self, request: Request) -> Optional[Response]:
        """ called in downloader """
        try:
            response = await self._process_request(request)
        except KeyError:
            raise RequestMethodError(f"Request method {request.method.lower()} is not supported.")
        except Exception as exp:
            self._stats.inc_value(f'download_error/{exp.__class__.__name__}')
            response = await self._process_exception(request, exp)
        else:
            self.crawler.stats.inc_value('response_received_count')

        if isinstance(response, Response):
            response = await self._process_response(request, response)
        if isinstance(response, Request):
            # 入队
            await self.crawler.engine.enqueue_request(request)
            return None
        return response

    def _add_middleware(self, middlewares):
        enabled_middlewares = [m for m in middlewares if self._validate_middleware(m)]
        if enabled_middlewares:
            self.logger.info(f'enable middleware:\n{pformat(enabled_middlewares)}')

    def _validate_middleware(self, middleware):
        middleware_cls = load_class(middleware)
        if not hasattr(middleware_cls, 'create_instance'):
            raise MiddlewareInitError(f"Middleware init failed, you must inherit from 'BaseMiddleware' or "
                                      f"have method create_instance.")
        instance = middleware_cls.create_instance(self.crawler)
        self.middlewares.append(instance)
        return True

    def _add_method(self):
        for middleware in self.middlewares:
            if hasattr(middleware, 'process_request'):
                if self._validate_method('process_request', middleware):
                    self.methods['process_request'].append(middleware.process_request)
            if hasattr(middleware, 'process_response'):
                if self._validate_method('process_response', middleware):
                    self.methods['process_response'].append(middleware.process_response)
            if hasattr(middleware, 'process_exception'):
                if self._validate_method('process_exception', middleware):
                    self.methods['process_exception'].append(middleware.process_exception)

    @staticmethod
    def _validate_method(method_name, middleware) -> bool:
        method = getattr(type(middleware), method_name)
        base_method = getattr(BaseMiddleware, method_name)
        return False if method == base_method else True

    @classmethod
    def create_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)
