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

"""Print fields from the input in CSV format."""

from typing import List

from .fields import get_from_field
from .printer import Printer


class CSVPrinter(Printer):
    """Print fields from the input in CSV format."""

    def __init__(self, fields: List[str]):
        """Initialize printer.

        Args:
            fields: List of fields to print.
        """
        if len(fields) < 1:
            raise ValueError("A list of fields is required for the CSV format")
        if fields[0] != "time":
            fields.insert(0, "time")
        print(",".join(fields))
        self.fields = fields

    def process(self, unpacked: dict):
        """Process a new unpacked dictionary.

        Args:
            unpacked: Unpacked dictionary.
        """

        def str_from_value(value):
            if isinstance(value, bool):
                return "1" if value else "0"
            return str(value)

        values = [
            str_from_value(get_from_field(unpacked, field, default="0"))
            for field in self.fields
        ]
        print(",".join(values))
