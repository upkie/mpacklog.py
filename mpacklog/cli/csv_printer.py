#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

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
