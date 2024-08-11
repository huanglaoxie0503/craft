#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-11 11:22
# @Author  :   oscar
# @Desc    :   数据统计收集器
"""
from pprint import pformat
from craft.utils.log import get_logger
from craft.utils.common import date_delta, now


class StatsCollector(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self._stats = {}
        self.logger = get_logger(name=self.__class__.__name__, level='INFO')

    def inc_value(self, key, count=1, start=0):
        self._stats[key] = self._stats.setdefault(key, start) + count

    def get_value(self, key, default=None):
        return self._stats.get(key, default)

    def get_stats(self):
        return self._stats

    def set_stats(self, stats):
        self._stats = stats

    def clear_stats(self):
        self._stats.clear()

    def close_spider(self, spider_name, reason):
        self._stats['end_time'] = now()
        self._stats['reason'] = reason
        self._stats['cost_time(s)'] = date_delta(self._stats['start_time'], self._stats['end_time'])
        self.logger.info(f"{spider_name} stats: \n" + pformat(self._stats))

    def __getitem__(self, item):
        return self._stats[item]

    def __setitem__(self, key, value):
        self._stats[key] = value

    def __delitem__(self, key):
        del self._stats[key]