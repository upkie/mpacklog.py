#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Test the asynchronous logger."""

import os
import tempfile
import unittest

from mpacklog import AsyncLogger


class TestAsyncLogger(unittest.IsolatedAsyncioTestCase):
    async def test_put(self):
        tmp_file = tempfile.mktemp(suffix=".mpack")
        logger = AsyncLogger(tmp_file)
        self.assertTrue(logger.queue.empty())
        await logger.put({"foo": 42, "something": "else"})
        self.assertFalse(logger.queue.empty())

    async def test_stop_and_write(self):
        tmp_file = tempfile.mktemp(suffix=".mpack")
        self.assertFalse(os.path.exists(tmp_file))

        logger = AsyncLogger(tmp_file)
        await logger.stop()
        await logger.write()
        self.assertTrue(os.path.exists(tmp_file))
