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
from plot_item import PlotItem
from qtpy import QtCore, QtWidgets

qt_backend = matplotlib.backends.backend_qt5agg

LEFT_LEGEND_LOC = 3
RIGHT_LEGEND_LOC = 2


class PlotWidget(QtWidgets.QWidget):
    COLORS = "rbgcmyk"

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.history_s = 20.0
        self.next_color = 0
        self.paused = False

        self.last_draw_time = 0.0

        self.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumSize(10, 10)

        self.canvas.mpl_connect("key_press_event", self.handle_key_press)
        self.canvas.mpl_connect("key_release_event", self.handle_key_release)

        self.left_axis = self.figure.add_subplot(111)
        self.left_axis.grid()
        self.left_axis.fmt_xdata = lambda x: "%.3f" % x

        self.left_axis.legend_loc = LEFT_LEGEND_LOC

        self.right_axis = None

        self.toolbar = qt_backend.NavigationToolbar2QT(self.canvas, self)
        self.pause_action = QtWidgets.QAction("Pause", self)
        self.pause_action.setCheckable(True)
        self.pause_action.toggled.connect(self._handle_pause)
        self.toolbar.addAction(self.pause_action)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.toolbar, 0)
        layout.addWidget(self.canvas, 1)

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)

    def _handle_pause(self, value):
        self.paused = value

    def add_plot(self, name, signal, axis_number):
        axis = self.left_axis
        if axis_number == 1:
            if self.right_axis is None:
                self.right_axis = self.left_axis.twinx()
                self.right_axis.legend_loc = RIGHT_LEGEND_LOC
            axis = self.right_axis
        item = PlotItem(axis, self, name, signal)
        return item

    def remove_plot(self, item):
        item.remove()

    def data_update(self):
        now = time.time()
        elapsed = now - self.last_draw_time
        if elapsed > 0.1:
            self.last_draw_time = now
            self.canvas.draw()

    def _get_axes_keys(self):
        result = []
        result.append(("1", self.left_axis))
        if self.right_axis:
            result.append(("2", self.right_axis))
        return result

    def handle_key_press(self, event):
        if event.key not in ["1", "2"]:
            return
        for key, axis in self._get_axes_keys():
            if key == event.key:
                axis.set_navigate(True)
            else:
                axis.set_navigate(False)

    def handle_key_release(self, event):
        if event.key not in ["1", "2"]:
            return
        for key, axis in self._get_axes_keys():
            axis.set_navigate(True)
