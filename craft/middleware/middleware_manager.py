#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-11 13:40
# @Author  :   oscar
# @Desc    :   中间件
"""
from typing import List, Dict
from types import MethodType
from pprint import pformat
from collections import defaultdict

from craft.exceptions import MiddlewareInitError
from craft.middleware import BaseMiddleware
from craft.utils.log import get_logger
from craft.utils.tools import load_class


class MiddlewareManager:
    def __init__(self, crawler):
        self.crawler = crawler
        self.middlewares: List = []
        self.methods: Dict[str, List[MethodType]] = defaultdict(list)
        self.logger = get_logger(self.__class__.__name__, self.crawler.settings.get('LOG_LEVEL'))
        middlewares = self.crawler.settings.get_list('MIDDLEWARES')
        self._add_middleware(middlewares)
        self._add_method()

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
    def _validate_method(method_name, middleware):
        method = getattr(type(middleware), method_name)
        base_method = getattr(BaseMiddleware, method_name)
        if method == base_method:
            return False
        else:
            return True

    @classmethod
    def create_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)
