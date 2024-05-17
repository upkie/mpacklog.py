#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Logger with Asynchronous I/O."""

import asyncio

import aiofiles
import msgpack

from .serialize import serialize


class AsyncLogger:
    """Logger with Asynchronous I/O."""

    def __init__(self, path):
        """Initialize logger.

        Args:
            path: Path to the output log file.
        """
        self.__writing = False
        self.__keep_going = True
        self.path = path
        self.queue = asyncio.Queue()

    async def put(self, message):
        """Put a new message in the logging queue.

        Args:
            message: New message.
        """
        await self.queue.put(message)

    async def stop(self):
        """Break the loop of the `write` coroutine."""
        self.__keep_going = False
        while self.__writing:
            await self.put({"exit": True})
            await asyncio.sleep(0.01)

    async def write(self, flush: bool = False):
        """Continuously write messages from the logging queue to file."""
        assert not self.__writing
        self.__writing = True
        async with aiofiles.open(self.path, "wb") as file:
            packer = msgpack.Packer(default=serialize, use_bin_type=True)
            keep_going = not self.queue.empty() if flush else self.__keep_going
            while keep_going:
                message = await self.queue.get()
                if message == {"exit": True}:
                    break
                await file.write(packer.pack(message))
                await file.flush()
                keep_going = (
                    not self.queue.empty() if flush else self.__keep_going
                )
        self.__writing = False

    async def flush(self):
        """Flush messages from the logging queue to file."""
        await self.write(flush=True)
