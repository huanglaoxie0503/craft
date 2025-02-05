#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-02 07:22
# @Author  :   oscar
# @Desc    :   None
"""
from pprint import pformat

from craft import Item
from craft.spider import Spider
from craft.utils.log import get_logger


class DebugPipeline(object):
    def __init__(self, logger):
        self.logger = logger

    @classmethod
    def create_instance(cls, crawler):
        logger = get_logger(cls.__name__, crawler.settings.get('LOG_LEVEL'))
        logger.info('DebugPipeline init')
        return cls(logger)

    def process_item(self, item: Item, spider: Spider) -> None:
        self.logger.debug(pformat(item.to_dict()))
