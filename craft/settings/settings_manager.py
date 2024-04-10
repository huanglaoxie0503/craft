#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-10 16:28
# @Author  :   oscar
# @Desc    :   None
"""
from copy import deepcopy
from importlib import import_module
from collections.abc import MutableMapping

from craft.settings import default_settings


class SettingsManager(MutableMapping):

    def __init__(self, values=None):
        self.attributes = {}
        # 加载默认配置
        self.set_settings(default_settings)
        self.update(values)

    def set(self, key, value):
        self.attributes[key] = value

    def get(self, key, default=None):
        return self[key] if self[key] is not None else default

    def get_int(self, key, default=0):
        return int(self.get(key, default))

    def get_float(self, key, default=0.0):
        return float(self.get(key, default))

    def get_list(self, key, default=None):
        values = self.get(key, default or [])
        if isinstance(values, str):
            values = values.split(',')
        return list(values)

    def get_bool(self, key, default=False):
        r = self.get(key, default)
        try:
            return bool(int(r))
        except ValueError:
            if r in ('True', 'true', 'TRUE'):
                return True
            if r in ('False', 'false', 'FALSE'):
                return False
            raise ValueError("Invalid value for '{}': {}".format(key, r))

    def delete(self, key):
        del self.attributes[key]

    def __contains__(self, item):
        return item in self.attributes

    def __getitem__(self, item):
        if item not in self:
            return None
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __str__(self):
        return f'Settings value: {self.attributes}'

    __repr__ = __str__

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def update(self, values):
        if values is not None:
            for key, value in values.items():
                self.set(key, value)

    def copy(self):
        return deepcopy(self)

    def set_settings(self, module):
        if isinstance(module, str):
            # 动态导入包
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))


if __name__ == '__main__':
    setting = SettingsManager()
    setting['CONCURRENCY_NUMS'] = 16
    print(setting.items())
    print(setting.values())
