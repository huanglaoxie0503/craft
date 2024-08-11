#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-11 13:39
# @Author  :   oscar
# @Desc    :   None
"""


class BaseMiddleware(object):

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def process_exception(self, request, exception):
        pass

    @classmethod
    def create_instance(cls, crawler):
        return cls()
