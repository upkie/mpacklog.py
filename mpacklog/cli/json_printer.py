#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

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
