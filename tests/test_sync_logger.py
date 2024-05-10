#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 Inria

"""Test the synchronous logger."""

import os
import tempfile
import unittest

import msgpack

from mpacklog import SyncLogger


class TestSyncLogger(unittest.TestCase):
    def test_put(self):
        tmp_file = tempfile.mktemp(suffix=".mpack")
        logger = SyncLogger(tmp_file)
        self.assertTrue(logger.queue.empty())
        logger.put({"foo": 42, "something": "else"})
        self.assertFalse(logger.queue.empty())

    def test_write(self):
        tmp_file = tempfile.mktemp(suffix=".mpack")
        self.assertFalse(os.path.exists(tmp_file))

        logger = SyncLogger(tmp_file)
        logger.write()
        self.assertTrue(os.path.exists(tmp_file))

    def test_write_and_read(self):
        tmp_path = tempfile.mktemp(suffix=".mpack")

        logger = SyncLogger(tmp_path)
        logger.put({"foo": 42, "something": "else"})
        logger.write()

        with open(tmp_path, "rb") as tmp_file:
            message = msgpack.load(tmp_file)
            self.assertEqual(message, {"foo": 42, "something": "else"})
