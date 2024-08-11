#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-04-10 17:24
# @Author  :   oscar
# @Desc    :   默认配置
"""

# 爬虫名称
SPIDER_NAME = 'craft_spider'
# 并发数
CONCURRENCY_NUMS = 32
# 日志级别
LOG_LEVEL = 'INFO'

VERIFY_SSL = True
# 请求超时时间
TIMEOUT = 60
# 延迟时间
INTERVAL = 5
# 是否使用同一个连接
USER_SESSION = True
# 默认下载器
DOWNLOADER = 'craft.downloader.aiohttp_downloader.AioHttpDownloader'
# 中间件
MIDDLEWARES = [

]
