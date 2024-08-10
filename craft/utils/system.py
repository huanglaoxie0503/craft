#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2024-08-10 17:53
# @Author  :   oscar
# @Desc    :   None
"""
import platform

system = platform.system().lower()
if system == 'windows':
    import asyncio
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
