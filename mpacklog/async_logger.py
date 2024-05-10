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

    async def write(self):
        """Continuously write messages from the logging queue to file."""
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
