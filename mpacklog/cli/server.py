#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Inria

import asyncio
import glob
import logging
import os
import socket
from typing import Optional

import aiofiles
import msgpack
from loop_rate_limiters import AsyncRateLimiter

from mpacklog.serialize import serialize

last_log: dict = {}


async def unpack(log_file: str):
    """Unpack latest data from log file.

    Args:
        log_file: Path to the log file to monitor.
    """
    global last_log
    rate = AsyncRateLimiter(frequency=2000.0, name="unpack", warn=True)
    async with aiofiles.open(log_file, "rb") as file:
        await file.seek(0, 2)  # 0 is the offset, 2 means seek from the end
        unpacker = msgpack.Unpacker(raw=False)
        while True:
            data = await file.read(4096)
            if not data:  # end of file
                await rate.sleep()
                continue
            unpacker.feed(data)
            try:
                for unpacked in unpacker:
                    if not isinstance(unpacked, dict):
                        raise ValueError(f"{unpacked=} not a dictionary")
                    if "observation" not in unpacked:
                        raise ValueError(f"{unpacked=} has no observation")
                    last_log = unpacked
            except BrokenPipeError:  # handle e.g. piping to `head`
                break
            await rate.sleep()


async def serve_client(client, address):
    """Server a client connection.

    Args:
        client: Socket of connection to client.
        address: IP address and port of the connection.
    """
    loop = asyncio.get_event_loop()
    request: str = "start"
    packer = msgpack.Packer(default=serialize, use_bin_type=True)
    logging.info("New connection from %s", address)
    rate = AsyncRateLimiter(frequency=2000.0, name="serve", warn=False)
    try:
        while request != "stop":
            data = await loop.sock_recv(client, 4096)
            if not data:
                break
            try:
                request = data.decode("utf-8").strip()
            except UnicodeDecodeError as exn:
                logging.warning(str(exn))
                continue
            if request == "get":
                reply = packer.pack(last_log)
                await loop.sock_sendall(client, reply)
            await rate.sleep()
    except BrokenPipeError:
        logging.info("Connection closed by %s", address)
    logging.info("Closing connection with %s", address)
    client.close()


async def listen(port: int):
    """Listen to clients connecting on a given port.

    Args:
        port: Port to listen to.
    """
    loop = asyncio.get_event_loop()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(8)
    server_socket.setblocking(False)  # required by loop.sock_accept
    while True:
        client_socket, address = await loop.sock_accept(server_socket)
        loop.create_task(serve(client_socket, address))


async def main(log_file: str, port: int) -> None:
    """Start the two server coroutines.

    Args:
        log_file: Path to the log file to monitor.
        port: Port to listen to.
    """
    await asyncio.gather(unpack(log_file), listen(port))


def find_log_file(log_path: Optional[str]) -> str:
    """Find log file to open.

    Args:
        log_file: Path to a directory or a specific log file.
    """
    if os.path.exists(log_path):
        if os.path.isfile(log_path):
            return log_path
    mpack_files = glob.glob(os.path.join(log_path, "*.mpack"))
    log_file = max(mpack_files, key=os.path.getmtime)
    logging.info(
        "Opening the most recent log in %s: %s",
        log_path,
        os.path.basename(log_file),
    )
    return log_file


def serve(log_path: str, port: int):
    logging.getLogger().setLevel(logging.INFO)
    log_file = find_log_file(log_path)
    asyncio.run(main(log_file, port))
