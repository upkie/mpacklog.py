#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
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

"""
Test the serialization function.
"""

import unittest

import numpy as np

from mpacklog.serialize import serialize


class FooSerializer:
    def serialize(self):
        return {"foo": "bar"}


class MockPinocchioSE3:
    def __init__(self, array: np.ndarray):
        self.np = array


class TestSerialize(unittest.TestCase):
    def test_serialize(self):
        foo = FooSerializer()
        x = np.array([1, 2, 3])
        self.assertEqual(serialize(x), list(x))
        self.assertEqual(serialize(MockPinocchioSE3(x)), list(x))
        self.assertEqual(serialize(foo), {"foo": "bar"})
