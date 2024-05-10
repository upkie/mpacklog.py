#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Output printers."""


class Printer:
    """Base class for printers.

    A printer processes unpacked dictionaries one by one, and wraps up this
    data once the whole log has been parsed.
    """

    def process(self, unpacked: dict):
        """Process a new unpacked dictionary.

        Args:
            unpacked: Unpacked dictionary.
        """
