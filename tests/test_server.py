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

from mpacklog import SyncLogger
from mpacklog.cli.server import Server


class TestServer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        log_file = tempfile.mktemp(suffix=".mpack")
        logger = SyncLogger(log_file)
        logger.put({"foo": 42, "something": "else"})
        logger.write()
        server = Server(log_file, 4949)
        self.server = server

    async def asyncSetUp(self):
        await super().asyncSetUp()
        asyncio.create_task(self.server.run_async())

    async def test_get(self):
        unpacker = msgpack.Unpacker(raw=False)
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.settimeout(5.0)
        sock.connect(("localhost", 4949))

        request = "get".encode("utf-8")
        await loop.sock_sendall(sock, request)
        reply_dict = None
        data = await loop.sock_recv(sock, 4096)
        if not data:
            return None
        unpacker.feed(data)
        for unpacked in self.unpacker:
            reply_dict = unpacked

        sock.close()
        self.assertEqual(reply_dict["foo"], 42)
