#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-02 07:37
# @Author  :   oscar
# @Desc    :   None
"""
from craft import event
from craft.utils.common import get_now, date_delta


class LogStats:
    def __init__(self, stats):
        self._stats = stats

    @classmethod
    def create_instance(cls, crawler):
        o = cls(crawler.stats)
        crawler.subscriber.subscribe(event_name=event.spider_opened, receiver=o.spider_opened)
        crawler.subscriber.subscribe(event_name=event.spider_closed, receiver=o.spider_closed)
        crawler.subscriber.subscribe(event_name=event.item_successful, receiver=o.item_successful)
        crawler.subscriber.subscribe(event_name=event.item_discard, receiver=o.item_discard)
        crawler.subscriber.subscribe(event_name=event.response_received, receiver=o.response_received)
        crawler.subscriber.subscribe(event_name=event.request_scheduled, receiver=o.request_scheduled)

        return o

    async def spider_opened(self):
        self._stats['start_time'] = get_now()

    async def spider_closed(self):
        self._stats['end_time'] = get_now()
        self._stats['cost_time(s)'] = date_delta(self._stats['start_time'], self._stats['end_time'])

    async def item_successful(self, _item, _spider):
        self._stats.inc_value['item_successful_count']

    async def item_discard(self, _item, _spider, _exception):
        self._stats.inc_value['item_discard_count']
        reason = _exception.msg
        if reason:
            self._stats.inc_value[f'item_discard/{reason}']

    async def response_received(self, _request, _spider):
        self._stats.inc_value['response_received_count']

    async def request_scheduled(self, _response, _spider):
        self._stats.inc_value['request_scheduled_count']
