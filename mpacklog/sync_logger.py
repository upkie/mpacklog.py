#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023 Inria
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

"""Logger with synchronous I/O."""

import os
import queue

import msgpack

from .serialize import serialize


class SyncLogger:
    """Logger with synchronous I/O.

    This logger exposes an API similar to AsyncLogger, but all I/O operations
    are synchronous.
    """

    def __init__(self, path):
        """Initialize logger.

        Args:
            path: Path to the output log file.
        """
        self.__keep_going = True
        self.path = path
        self.queue = queue.Queue()

        # Check if the file already exists so that SyncLogger.write doesn't
        # append to an existing file
        if os.path.exists(self.path):
            raise FileExistsError(f"File {path} already exists!")

    def put(self, message, write=False):
        """Puts a message in the queue.

        Args:
            message (dict): message to log
            write (bool): whether to append the message to the file immediately

        """
        self.queue.put(message)

        if write:
            self.write()

    def write(self):
        """Write all messages in the queue to the file.

        This method appends to the file if it already exists.
        """
        with open(self.path, "ab") as file:
            packer = msgpack.Packer(default=serialize, use_bin_type=True)

            while not self.queue.empty():
                message = self.queue.get()
                file.write(packer.pack(message))
