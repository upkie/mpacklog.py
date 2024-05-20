#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 mjbots Robotic Systems, LLC.  info@mjbots.com
# Copyright 2024 Inria
#
# This file incorporates code from utils/gui/moteus_gui/tview.py
# (https://github.com/mjbots/moteus, 49c698a63f0ded22528ad7539cc2e27e41cd486d)

"""Sized tree widget for Qt application window."""

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QHeaderView  # pylint: disable=no-name-in-module


class SizedTreeWidget(QtWidgets.QTreeWidget):
    """Sized tree widget.

    Attributes:
        COLUMN_PADDING: Column padding in pixels.
        MIN_VALUE_WIDTH: Minimum width in pixels for the Value column.
    """

    COLUMN_PADDING: int = 10
    MIN_VALUE_WIDTH: int = 100

    def __init__(self, parent=None) -> None:
        """Initialized tree widget.

        Args:
            parent: Parent Qt widget.
        """
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.setColumnCount(2)
        self.headerItem().setText(0, "Name")
        self.headerItem().setText(1, "Value")

        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.header().setDefaultAlignment(QtCore.Qt.AlignLeft)

    def resizeEvent(self, event):  # pylint: disable=invalid-name
        """Resize first column (Name) to keep the Value column width fixed."""
        width = self.width() - self.MIN_VALUE_WIDTH - self.COLUMN_PADDING
        self.setColumnWidth(0, width)
        super().resizeEvent(event)

    def sizeHint(self):  # pylint: disable=invalid-name
        """Initial guess for widget dimensions."""
        return QtCore.QSize(250, 500)
