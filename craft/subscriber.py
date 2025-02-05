#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-01-26 14:17
# @Author  :   oscar
# @Desc    :   None
"""
import asyncio
from collections import defaultdict
from typing import Dict, Callable, Coroutine, Set, Optional


class Subscriber:
    def __init__(self):
        self._subscriber: Dict[str, Set[Callable[..., Coroutine]]] = defaultdict(set)

    def subscribe(
            self,
            event_name: str,  # 必填参数
            receiver: Optional[Callable[..., Coroutine]] = None,  # 可选参数
    ) -> None:
        if receiver is not None:
            self._subscriber[event_name].add(receiver)

    def unsubscribe(
            self,
            event_name: str,  # 必填参数
            receiver: Optional[Callable[..., Coroutine]] = None,  # 可选参数
    ) -> None:
        if receiver is not None:
            self._subscriber[event_name].discard(receiver)

    async def notify(self, event_name: str, *args, **kwargs):
        for receiver in self._subscriber[event_name]:
            task = asyncio.create_task(receiver(*args, **kwargs))

            # 添加回调函数处理异常
            def handle_task_result(task):
                try:
                    task.result()  # 获取任务结果（如果有异常会抛出）
                except Exception as e:
                    print(f"Task failed: {e}")

            task.add_done_callback(handle_task_result)