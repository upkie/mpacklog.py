#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Inria

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
        server.connect((host, port))
        self.server = server
        self.unpacker = unpacker

    def __del__(self):
        """Close connection to the server."""
        if hasattr(self, "server"):
            self.server.close()

    def read(self) -> Optional[dict]:
        """Read a dictionary from the streaming server."""
        self.server.send("get".encode("utf-8"))
        reply_dict = {}
        while not reply_dict:
            data = self.server.recv(4096)
            if not data:
                return None
            self.unpacker.feed(data)
            for unpacked in self.unpacker:
                reply_dict = unpacked
        return reply_dict
