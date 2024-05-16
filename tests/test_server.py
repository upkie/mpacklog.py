#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Test the server."""

import asyncio
import socket
import tempfile
import unittest

import msgpack

from mpacklog import AsyncLogger
from mpacklog.cli.server import Server


class TestServer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        log_file = tempfile.mktemp(suffix=".mpack")
        logger = AsyncLogger(log_file)
        self.assertTrue(logger.queue.empty())
        await logger.put({"foo": 42})
        server = Server(log_file, 4949)
        self.server = server
        self.logger = logger

    async def asyncSetUp(self):
        await super().asyncSetUp()
        asyncio.create_task(self.server.run_async())

    async def test_get(self):
        unpacker = msgpack.Unpacker(raw=False)
        loop = asyncio.get_event_loop()
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setblocking(False)
        server_sock.settimeout(5.0)
        server_sock.connect(("localhost", 4949))

        request = "get".encode("utf-8")
        await loop.sock_sendall(self.server, request)
        reply_dict = None
        data = await loop.sock_recv(self.server, 4096)
        if not data:
            return None
        unpacker.feed(data)
        for unpacked in self.unpacker:
            reply_dict = unpacked

        server_sock.close()
        self.assertEqual(reply_dict["foo"], 42)
