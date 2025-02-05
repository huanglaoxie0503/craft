#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-01-26 14:30
# @Author  :   oscar
# @Desc    :   Spider 中可以触发的事件
"""
# arguments: exception, spider
spider_error = 'spider_error'
# arguments: spider open
spider_opened = 'spider_opened'
# arguments: spider close
spider_closed = 'spider_closed'
# arguments: request, spider,exception
ignore_request = 'ignore_request'
# arguments: request, spider
request_scheduled = 'request_scheduled'
# arguments: request, spider
response_received = 'response_received'
# arguments: item, spider
item_successful = 'item_successful'
# arguments: item, spider, exception
item_discard = 'item_discard'

