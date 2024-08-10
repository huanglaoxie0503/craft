#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-10 16:26
# @Author  :   oscar
# @Desc    :   None
"""
import os
import sys
from importlib import import_module

from craft.settings.settings_manager import SettingsManager


def _get_closest(path='.'):
    path = os.path.abspath(path)
    return path


def _init_env():
    closest_env = _get_closest()
    if closest_env:
        project_dir = os.path.dirname(closest_env)
        sys.path.append(project_dir)


def get_settings(settings='settings'):
    _settings = SettingsManager()
    _init_env()
    _settings.set_settings(module=settings)
    return _settings


def merge_settings(spider, settings):
    if hasattr(spider, 'custom_settings'):
        custom_settings = getattr(spider, 'custom_settings')
        settings.update(custom_settings)


def load_class(path):
    """
    动态加载类
    :param path: 路径
    :return:
    """
    if not isinstance(path, str):
        if callable(path):
            return path
        else:
            raise TypeError('path must be a string or object, got {}'.format(type(path)))
    module_name, class_name = path.rsplit('.', 1)
    module = import_module(module_name)

    try:
        cls = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(f'Module {module_name!r} does not define any object with name {class_name!r}.')
    return cls


if __name__ == '__main__':
    _init_env()
