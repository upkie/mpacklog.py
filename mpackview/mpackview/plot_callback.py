#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 mjbots Robotic Systems, LLC.  info@mjbots.com
# Copyright 2024 Inria
#
# This file incorporates code from utils/gui/moteus_gui/tview.py
# (https://github.com/mjbots/moteus, 49c698a63f0ded22528ad7539cc2e27e41cd486d)

"""Callback mechanism to append new values to time series plots."""


class PlotCallback:
    """Connect a tree item and a callback function updating its plot."""

    class Connection:  # pylint: disable=too-few-public-methods
        """Remember callback index in parent list."""

        def __init__(self, parent: "PlotCallback", index: int):
            """Initialize connection.

            Args:
                parent: Plot callback holding the connection.
                index: Index of connection in the callback list.
            """
            self.parent = parent
            self.index = index

        def remove(self):
            """Remove callback from list."""
            del self.parent._callbacks[  # pylint: disable=protected-access
                self.index
            ]

    def __init__(self):
        """Initialize callback."""
        self._index = 0
        self._callbacks = {}

    def connect(self, handler) -> Connection:
        """Connect a new callback function.

        Args:
            handler: Callback function.
        """
        result = self._index
        self._index += 1
        self._callbacks[result] = handler
        return PlotCallback.Connection(self, result)

    def update(self, value) -> bool:
        """Append a new value to plot data.

        Args:
            value: New value.

        Returns:
            True if the update was successful, False if the callback is
            disconnected.
        """
        for handler in self._callbacks.values():
            handler(value)
        return len(self._callbacks) != 0
