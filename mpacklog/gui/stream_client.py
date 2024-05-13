#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Inria

import asyncio
import socket
from typing import Optional

import msgpack


class StreamClient:

    def __init__(self, host: str, port: int) -> None:
        """Connect to a server.

        Args:
            host: Host name or IP address of the server.
            port: Port number to connect to.
        """
        unpacker = msgpack.Unpacker(raw=False)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.settimeout(5.0)
        server.connect((host, port))
        self.server = server
        self.unpacker = unpacker

    def __del__(self):
        """Close connection to the server."""
        if hasattr(self, "server"):
            self.server.close()

    async def read(self) -> Optional[dict]:
        """Read a dictionary from the streaming server."""
        loop = asyncio.get_event_loop()
        request = "get".encode("utf-8")
        await loop.sock_sendall(self.server, request)
        reply_dict = None
        while reply_dict is None:
            data = await loop.sock_recv(self.server, 4096)
            if not data:
                return None
            self.unpacker.feed(data)
            for unpacked in self.unpacker:
                reply_dict = unpacked
        return reply_dict
