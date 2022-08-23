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

from .fields import list_fields
from .printer import Printer


class FieldPrinter(Printer):

    """
    Parse whole log, then finally list all fields encountered.
    """

    def __init__(self):
        self.fields = set([])
        self.observation = {}

    def process(self, unpacked: dict):
        """
        Process a new unpacked dictionary.

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

    def finish(self, logfile: str):
        """
        Instructions executed once the whole log has been processed.

        Args:
            logfile: Path to input log file.
        """
