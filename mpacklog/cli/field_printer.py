#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Parse whole log and list all fields encountered."""

from .fields import list_fields
from .printer import Printer


class FieldPrinter(Printer):
    """Parse whole log, then finally list all fields encountered."""

    def __init__(self):
        """Initialize field printer."""
        self.fields = set([])
        self.observation = {}

    def process(self, unpacked: dict):
        """Process a new unpacked dictionary.

        Args:
            unpacked: Unpacked dictionary.
        """
        unpacked_fields = set(list_fields(unpacked))
        new_fields = unpacked_fields - self.fields
        if len(new_fields) > 0:
            for field in sorted(list(new_fields)):
                print(f"- {field}")
            print("")
        self.fields = set.union(self.fields, new_fields)
        self.observation.update(unpacked)
