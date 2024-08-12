#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-11 13:39
# @Author  :   oscar
# @Desc    :   None
"""
from typing import Optional
from craft import Request, Response


class BaseMiddleware(object):

    def process_request(self, request, spider) -> None | Request | Response:
        pass

    def process_response(self, request, response, spider) -> Request | Response:
        pass

    def process_exception(self, request, exception, spider) -> None | Request | Response:
        pass

    @classmethod
    def create_instance(cls, crawler):
        return cls()
