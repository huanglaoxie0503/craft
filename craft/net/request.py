#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-09 00:13
# @Author  :   oscar
# @Desc    :   Request 请求体封装
"""
from typing import Dict, Optional, Callable


class Request(object):

    def __init__(
            self,
            url: str,
            *,
            callback: Optional[Callable] = None,
            headers: Optional[Dict[str, str]] = None,
            body: Optional[bytes] = None,
            method: Optional[str] = 'GET',
            cookies: Optional[Dict[str, str]] = None,
            priority: int = 0

    ):
        self.url = url
        self.callback = callback
        self.headers = headers
        self.body = body
        self.method = method
        self.cookies = cookies
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority
