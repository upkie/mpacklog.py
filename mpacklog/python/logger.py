#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import asyncio

import aiofiles
import msgpack

from .serialize import serialize


class Logger:

    """!
    Logger with Asynchronous I/O.
    """

    def __init__(self, path):
        self.__keep_going = True
        self.path = path
        self.queue = asyncio.Queue()

    async def put(self, message):
        await self.queue.put(message)

    async def stop(self):
        self.__keep_going = False

    async def write(self):
        file = await aiofiles.open(self.path, "wb")
        packer = msgpack.Packer(default=serialize, use_bin_type=True)
        while self.__keep_going:
            message = await self.queue.get()
            if message == {"exit": True}:
                break
            await file.write(packer.pack(message))
            # Flushing has little effect when the Python process is configured
            # more predictable although a little bit lower on average.
            # on its own core (CPUID). When running on the default core, it
            # tends to make the slack duration of the other coroutines
            await file.flush()
        await file.close()
