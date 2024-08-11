#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-11 11:49
# @Author  :   oscar
# @Desc    :   通用工具函数
"""
from datetime import datetime


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def date_delta(start, end):
    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    time_diff = end - start
    seconds = time_diff.total_seconds()
    return int(seconds)


