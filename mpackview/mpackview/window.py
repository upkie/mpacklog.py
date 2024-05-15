#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 mjbots Robotic Systems, LLC.  info@mjbots.com
# Copyright 2024 Inria
#
# This file incorporates code from utils/gui/moteus_gui/tview.py
# (https://github.com/mjbots/moteus, 49c698a63f0ded22528ad7539cc2e27e41cd486d)

import asyncio
import logging
import os

from PySide2 import QtUiTools
from qtpy import QtCore, QtWidgets

from .plot_callback import PlotCallback
from .plot_widget import PlotWidget
from .sized_tree_widget import SizedTreeWidget
from .stream_client import StreamClient


def format_value(value) -> str:
    """Format incoming values for the Values column.

    Args:
        value: Value to format as a string.

    Returns:
        Value formatted as a string.
    """
    return f"{value:.2g}" if isinstance(value, float) else str(value)


class Window:
    """Main application window.

    Attributes:
        stream_client: Client to read streaming data from.
    """

    stream_client: StreamClient
    tree: dict

    def __init__(self, stream_client: StreamClient, parent=None):
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        uifilename = os.path.join(current_script_dir, "mpacklog.ui")

        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile(uifilename)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uifile, parent)
        uifile.close()

        self.ui.telemetryTreeWidget = SizedTreeWidget()
        self.ui.telemetryDock.setWidget(self.ui.telemetryTreeWidget)
        self.ui.telemetryTreeWidget.itemExpanded.connect(
            self.handle_tree_expanded
        )
        self.ui.telemetryTreeWidget.itemCollapsed.connect(
            self.handle_tree_collapsed
        )
        self.ui.telemetryTreeWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        self.ui.telemetryTreeWidget.customContextMenuRequested.connect(
            self.handle_telemetry_context_menu
        )

        self.ui.plotItemRemoveButton.clicked.connect(
            self.handle_plot_item_remove
        )

        layout = QtWidgets.QVBoxLayout(self.ui.plotHolderWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.ui.plotHolderWidget.setLayout(layout)
        self.ui.plotWidget = PlotWidget(self.ui.plotHolderWidget)
        layout.addWidget(self.ui.plotWidget)

        def update_plot_widget(value):
            self.ui.plotWidget.history_duration = value

        self.ui.historySpin.valueChanged.connect(update_plot_widget)

        QtCore.QTimer.singleShot(0, self.handle_startup)
        self.stream_client = stream_client
        self.tree = {}

    def show(self):
        self.ui.show()

    def handle_startup(self):
        asyncio.create_task(self.run())

    async def run(self):
        """Main loop of the application."""
        data = await self.stream_client.read()
        self.ui.telemetryTreeWidget.clear()
        self.tree.clear()
        self.update_tree(self.ui.telemetryTreeWidget, data, self.tree)
        while True:
            try:
                data = await self.stream_client.read()
            except ConnectionResetError:
                data = None
            if data is None:
                logging.warning("Connection reset by peer, plot is now frozen")
                break
            try:
                self.update_data(data, self.tree)
            except KeyError:  # tree structure has changed
                self.update_tree(self.ui.telemetryTreeWidget, data, self.tree)
                self.update_data(data, self.tree)
            await asyncio.sleep(0.01)

    def update_tree(self, item, data, tree: dict):
        tree["__item__"] = item
        is_dict = isinstance(data, dict)
        is_list = isinstance(data, list)
        if not is_dict and not is_list:
            return
        keys = sorted(data.keys()) if is_dict else map(str, range(len(data)))
        for index, key in enumerate(keys):
            if key not in tree:
                child = QtWidgets.QTreeWidgetItem(item)
                child.setText(0, key)
                tree[key] = {}
            else:  # item is already in the tree
                child = tree[key]["__item__"]
            value = data[key] if is_dict else data[index]
            self.update_tree(child, value, tree[key])

    def update_data(self, data, tree):
        item = tree["__item__"]
        if isinstance(data, dict):
            for key, value in data.items():
                self.update_data(value, tree[key])
        elif isinstance(data, list):
            for index, value in enumerate(data):
                self.update_data(value, tree[str(index)])
        else:  # data is not a dictionary
            item.setText(1, format_value(data))
            if "__plot__" in tree:
                active = tree["__plot__"].update(data)
                if not active:
                    del tree["__plot__"]

    def handle_tree_expanded(self, item):
        self.ui.telemetryTreeWidget.resizeColumnToContents(0)
        user_data = item.data(0, QtCore.Qt.UserRole)
        if user_data:
            user_data.expand()

    def handle_tree_collapsed(self, item):
        user_data = item.data(0, QtCore.Qt.UserRole)
        if user_data:
            user_data.collapse()

    def handle_telemetry_context_menu(self, pos):
        item = self.ui.telemetryTreeWidget.itemAt(pos)
        if item.childCount() > 0:
            return

        menu = QtWidgets.QMenu(self.ui)
        plot_left_action = menu.addAction("Plot Left")
        plot_right_action = menu.addAction("Plot Right")
        plot_actions = [plot_left_action, plot_right_action]

        menu.addSeparator()
        copy_name_action = menu.addAction("Copy Name")
        copy_value_action = menu.addAction("Copy Value")

        requested = menu.exec_(self.ui.telemetryTreeWidget.mapToGlobal(pos))
        if requested in plot_actions:
            top = item
            keys = []
            while top:
                keys.append(top.text(0))
                top = top.parent()
            keys.reverse()
            name = ".".join(keys)
            node = self.tree
            for key in keys:
                node = node[key]
            callback = PlotCallback()
            node["__plot__"] = callback
            axis = 1 if requested == plot_right_action else 0
            plot_item = self.ui.plotWidget.add_plot(name, callback, axis)
            self.ui.plotItemCombo.addItem(name, plot_item)
        elif requested == copy_name_action:
            QtWidgets.QApplication.clipboard().setText(item.text(0))
        elif requested == copy_value_action:
            QtWidgets.QApplication.clipboard().setText(item.text(1))
        else:  # the user cancelled
            pass

    def handle_plot_item_remove(self):
        index = self.ui.plotItemCombo.currentIndex()
        if index < 0:
            return
        item = self.ui.plotItemCombo.itemData(index)
        self.ui.plotWidget.remove_plot(item)
        self.ui.plotItemCombo.removeItem(index)
