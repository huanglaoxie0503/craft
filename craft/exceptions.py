#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-09 01:04
# @Author  :   oscar
# @Desc    :   异常处理
"""


class TransformTypeError(TypeError):
    pass


class OutputError(Exception):
    pass


class SpiderTypeError(TypeError):
    pass


class ItemInitError(Exception):
    pass


class ItemAttributeError(Exception):
    pass


class DecodeError(Exception):
    pass


class MiddlewareInitError(Exception):
    pass


class InvalidOutputError(Exception):
    pass


class RequestMethodError(Exception):
    pass
