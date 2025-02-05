#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-02 08:01
# @Author  :   oscar
# @Desc    :   None
"""
from craft.event import ignore_request
from craft.exceptions import IgnoreRequestError
from craft.utils.log import get_logger


class RequestIgnoreMiddleware(object):
    def __init__(self, stats, log_level):
        self.logger = get_logger(self.__class__.__name__, log_level)
        self.stats = stats

    @classmethod
    def create_instance(cls, crawler):
        o = cls(
            crawler.stats,
            crawler.settings.get('LOG_LEVEL')
        )
        crawler.subscriber.subscribe(event_name=ignore_request, receiver=o.ignore_request)
        return o

    async def ignore_request(self, request, _spider, exception):
        self.logger.info(f'Request ignored: {request}')
        self.stats.inc_value('request_ignored_count')
        reason = exception.msg
        if reason:
            self.stats.inc_value(f'request_ignored_count/{reason}')

    @staticmethod
    def process_exception(_request, exception, _spider):
        if isinstance(exception, IgnoreRequestError):
            return True
