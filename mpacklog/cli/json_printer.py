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

"""JSON Lines printer."""

import json
from typing import List, Optional

from .fields import filter_fields
from .printer import Printer


class JSONPrinter(Printer):
    """Default printer: print everything in JSON Lines."""

    def __init__(self, fields: Optional[List] = None):
        """Configure printer options.

        Args:
            fields: If given, only print out these selected fields (nested keys
                in "key1/.../keyN" format).
        """
        self.fields = fields

    def process(self, unpacked: dict) -> None:
        """Process a new unpacked dictionary.

        Args:
            unpacked: Unpacked dictionary.
        """
        output_with_nan = json.dumps(
            filter_fields(unpacked, self.fields), allow_nan=True
        )
        print(output_with_nan.replace(" NaN", " null"))  # kroOOOOoooonn!!!
