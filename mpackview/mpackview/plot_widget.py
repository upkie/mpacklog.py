#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 mjbots Robotic Systems, LLC.  info@mjbots.com
# Copyright 2024 Inria
#
# This file incorporates code from utils/gui/moteus_gui/tview.py
# (https://github.com/mjbots/moteus, 49c698a63f0ded22528ad7539cc2e27e41cd486d)

"""Interactively display and update values from an embedded device."""

import time

import matplotlib
import matplotlib.figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # noqa: E402
from qtpy import QtCore, QtWidgets

from .plot_callback import PlotCallback
from .plot_item import PlotItem

qt_backend = matplotlib.backends.backend_qt5agg

# This value is also written in the XML layout file, in the "value" property of
# the "historySpin" spinbox. The two values should be kept in sync.
DEFAULT_HISTORY_DURATION: float = 10.0  # seconds


class PlotWidget(
    QtWidgets.QWidget
):  # pylint: disable=too-many-instance-attributes
    """Plot widget.

    Attributes:
        canvas: Canvas to plot figure to.
        figure: Matplotlib figure.
        history_duration: History duration in seconds.
        last_draw_time: Last time the canvas was redrawn.
        left_axis: Left plot axis.
        next_color: Next plot color to pick.
        pause_action: GUI action for the pause button.
        paused: True if and only if plotting is paused.
        right_axis: Right plot axis.
        toolbar: GUI toolbar with a pause button.
    """

    canvas: FigureCanvasQTAgg
    figure: matplotlib.figure.Figure
    history_duration: float
    last_draw_time: float
    left_axis: matplotlib.axes.Axes
    next_color: int
    pause_action: QtWidgets.QAction
    paused: bool
    right_axis: matplotlib.axes.Axes
    toolbar: qt_backend.NavigationToolbar2QT

    def __init__(self, *args, **kwargs):
        """Initialize widget.

        Args:
            args: Positional arguments for parent constructor.
            kwargs: Keyword arguments for parent constructor.
        """
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.history_duration = DEFAULT_HISTORY_DURATION
        self.last_draw_time = 0.0
        self.next_color = 0
        self.paused = False

        self.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumSize(10, 10)
        self.canvas.mpl_connect("key_press_event", self.handle_key_press)
        self.canvas.mpl_connect("key_release_event", self.handle_key_release)

        self.left_axis = self.figure.add_subplot(111)
        self.left_axis.grid()
        self.left_axis.fmt_xdata = lambda x: f"{x:.3f}"
        self.left_axis.legend_loc = 3
        self.right_axis = None

        self.toolbar = qt_backend.NavigationToolbar2QT(self.canvas, self)
        self.pause_action = QtWidgets.QAction("Pause", self)
        self.pause_action.setCheckable(True)
        self.pause_action.toggled.connect(self.handle_pause)
        self.toolbar.addAction(self.pause_action)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.toolbar, 0)
        layout.addWidget(self.canvas, 1)

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)

    def handle_pause(self, state: bool) -> None:
        """Pause plot at a given state.

        Args:
            state: Pause state.
        """
        self.paused = state

    def add_plot(
        self, name: str, callback: PlotCallback, axis_number: int
    ) -> PlotItem:
        """Add a new plot to track.

        Args:
            name: Full name in the data tree.
            callback: Plot callback connecting tree item and plot data.
            axis_number: Left (0) or right (1) axis.

        Returns:
            New plot item.
        """
        axis = self.left_axis
        if axis_number == 1:
            if self.right_axis is None:
                self.right_axis = self.left_axis.twinx()
                self.right_axis.legend_loc = 2
            axis = self.right_axis
        item = PlotItem(axis, self, name, callback)
        return item

    def remove_plot(self, item: PlotItem) -> None:
        """Remove a plot.

        Args:
            item: Plot item corresponding to the plot to remove.
        """
        item.remove()

    def data_update(self) -> None:
        """Redraw plot after data has been updated."""
        now = time.time()
        elapsed = now - self.last_draw_time
        if elapsed > 0.1:
            self.last_draw_time = now
            self.canvas.draw()

    def __get_axes_keys(self):
        result = []
        result.append(("1", self.left_axis))
        if self.right_axis:
            result.append(("2", self.right_axis))
        return result

    def handle_key_press(self, event):
        """Handle a key-press event.

        Args:
            event: Event to handle.
        """
        if event.key not in ["1", "2"]:
            return
        for key, axis in self.__get_axes_keys():
            if key == event.key:
                axis.set_navigate(True)
            else:
                axis.set_navigate(False)

    def handle_key_release(self, event):
        """Handle a key-release event.

        Args:
            event: Event to handle.
        """
        if event.key not in ["1", "2"]:
            return
        for _, axis in self.__get_axes_keys():
            axis.set_navigate(True)
