#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-02 06:33
# @Author  :   oscar
# @Desc    :   None
"""
from pprint import pformat
from typing import List
from asyncio import create_task

from craft.event import item_successful, item_discard
from craft.exceptions import PipelineInitError, ItemDiscard, InvalidOutputError
from craft.utils.log import get_logger
from craft.utils.tools import load_class, common_callback


class PipelineManager:
    def __init__(self, crawler):
        self.crawler = crawler
        self.pipelines: List = []
        self.methods: List = []
        self.logger = get_logger(self.__class__.__name__, crawler.settings.get('LOG_LEVEL'))
        pipelines = crawler.settings.get_list('PIPELINES')
        self._add_pipelines(pipelines)
        self._add_methods()

    @classmethod
    def create_instance(cls, *args, **kwargs):
        o = cls(*args, **kwargs)
        return o

    def _add_pipelines(self, pipelines):
        for pipeline in pipelines:
            pipeline_cls = load_class(pipeline)
            if not hasattr(pipeline_cls, 'create_instance'):
                raise PipelineInitError(
                    f'{pipeline_cls.__name__} must have a create_instance method or must inherit from `BasePipeline`'
                )
            self.pipelines.append(pipeline_cls.create_instance(self.crawler))
        if pipelines:
            self.logger.info(f'enabled pipeline:\n {pformat(pipelines)}')

    def _add_methods(self):
        for pipeline in self.pipelines:
            if hasattr(pipeline, 'process_item'):
                self.methods.append(pipeline.process_item)

    async def process_item(self, item):
        try:
            for method in self.methods:
                item = await common_callback(method, item, self.crawler.spider)
                if not item:
                    raise InvalidOutputError(f'{method.__qualname__} return None is not supported.')
        except ItemDiscard as exp:
            await create_task(self.crawler.subscriber.notify(item_discard, item, self.crawler.spider, exp.msg))
        else:
            await create_task(self.crawler.subscriber.notify(item_successful, item, self.crawler.spider))

