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


class Printer:

    """
    Base class for printers. A printer processes unpacked dictionaries one by
    one, and wraps up this data once the whole log has been parsed.
    """

    def process(self, unpacked: dict):
        """
        Process a new unpacked dictionary.

        Args:
            unpacked: Unpacked dictionary.
        """
        pass

    def finish(self, logfile: str = ""):
        """
        Instructions executed once the whole log has been processed.

        @param logfile Path to input log file.
        """
        pass
