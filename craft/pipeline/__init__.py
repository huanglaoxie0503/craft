#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-02 06:33
# @Author  :   oscar
# @Desc    :   None
"""
from craft.items.items import Item


class BasePipeline(object):
    def process_item(self, item, spider) -> None:
        raise NotImplementedError

    @classmethod
    def create_instance(cls, crawler):
        return cls()
