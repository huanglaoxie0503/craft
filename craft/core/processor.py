#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-11 02:17
# @Author  :   oscar
# @Desc    :   None
"""
from asyncio import Queue, Task, create_task
from craft import Request, Item


class Processor:
    def __init__(self, crawler):
        self.crawler = crawler
        self.queue: Queue = Queue()
        self._processing_task: Task | None = None  # 处理队列的任务

    async def _process_queue(self):
        """持续从队列中取出数据并处理"""
        while True:
            try:
                result = await self.queue.get()
                try:
                    if isinstance(result, Request):
                        await self.crawler.engine.enqueue_request(result)
                    elif isinstance(result, Item):
                        await self._process_item(result)
                    else:
                        print(f"Unknown item type: {type(result)}")
                finally:
                    self.queue.task_done()  # 标记任务已完成
            except Exception as e:
                print(f"Error processing queue item: {e}")
                self.queue.task_done()

    async def start_processing(self):
        """启动队列处理协程"""
        if not self._processing_task or self._processing_task.done():
            self._processing_task = create_task(self._process_queue())

    async def stop_processing(self):
        """等待所有队列任务完成并停止处理协程"""
        await self.queue.join()  # 等待所有队列中的任务被处理完毕
        if self._processing_task:
            self._processing_task.cancel()

    async def enqueue(self, output):
        """向队列中添加新条目"""
        await self.queue.put(output)
        await self.start_processing()  # 确保处理协程正在运行

    async def _process_item(self, item: Item) -> None:
        """处理单个项目"""
        self.crawler.stats.inc_value("item_successful_count")
        # 可选：打印或进一步处理项目
        # print(item)

    def idle(self) -> bool:
        """检查队列是否为空闲状态"""
        return self.queue.empty()

    def __len__(self):
        """返回当前队列中的项数"""
        return self.queue.qsize()
# from asyncio import Queue
# from craft import Request, Item
#
#
# class Processor(object):
#
#     def __init__(self, crawler):
#         self.crawler = crawler
#         self.queue: Queue = Queue()
#
#     async def process(self):
#         # 出队
#         while not self.idle():
#             # 队列不空闲，则取数据
#             result = await self.queue.get()
#             # 处理 Request
#             if isinstance(result, Request):
#                 await self.crawler.engine.enqueue_request(result)
#             else:
#                 # 处理 Item
#                 assert isinstance(result, Item)
#                 await self._process_item(result)
#
#     async def _process_item(self, item: Item) -> None:
#         self.crawler.stats.inc_value("item_successful_count")
#         # print(item)
#
#     async def enqueue(self, output):
#         await self.queue.put(output)
#         await self.process()
#
#     def idle(self) -> bool:
#         return len(self) == 0
#
#     def __len__(self):
#         return self.queue.qsize()
