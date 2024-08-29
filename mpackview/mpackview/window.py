#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 mjbots Robotic Systems, LLC.  info@mjbots.com
# Copyright 2024 Inria
#
# This file incorporates code from utils/gui/moteus_gui/tview.py
# (https://github.com/mjbots/moteus, 49c698a63f0ded22528ad7539cc2e27e41cd486d)

"""Main application window."""

import asyncio
import logging
import os
from typing import Any, Tuple, Union

from PySide2 import QtUiTools
from qtpy import QtCore, QtWidgets

from .plot_callback import PlotCallback
from .plot_widget import PlotWidget
from .sized_tree_widget import SizedTreeWidget
from .stream_client import StreamClient
from .utils import format_value


class Window:
    """Main application window.

    Attributes:
        stream_client: Client to read streaming data from.
        tree: Internal tree connecting the GUI tree from the left panel and
            data streamed from mpacklog.
    """

    stream_client: StreamClient
    tree: dict

    def __init__(self, stream_client: StreamClient, parent=None):
        """Initialize window.

        Attributes:
            stream_client: Client to read streaming data from.
            parent: Optional parent Qt widget.
        """
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        uifilename = os.path.join(current_script_dir, "mpackview.ui")

        loader = QtUiTools.QUiLoader()  # pylint: disable=c-extension-no-member
        ui_file = QtCore.QFile(uifilename)  # noqa: E1101
        ui_file.open(QtCore.QFile.ReadOnly)  # noqa: E1101
        self.ui = loader.load(ui_file, parent)
        ui_file.close()

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
        """Show user interface."""
        self.ui.show()

    def handle_startup(self):
        """Method called at startup."""
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

    def update_tree(
        self,
        item: QtWidgets.QTreeWidgetItem,
        data: Union[dict, list, Any],
        node: dict,
    ) -> None:
        """Update the tree structure of the GUI left pane.

        Args:
            item: Tree widget item from the left GUI panel.
            data: Deserialized object to read the tree structure from. A
                dictionary or a list yields an internal node in the tree, while
                a value yields a leaf.
            node: Node in the internal tree.
        """
        node["__item__"] = item
        if isinstance(data, dict):
            keys = sorted(data.keys())
            is_dict = True
        elif isinstance(data, list):
            keys = [str(i) for i, _ in enumerate(data)]
            is_dict = False
        else:  # not isinstance(data, (dict, list)):
            return
        for index, key in enumerate(keys):
            if key not in node:
                child = QtWidgets.QTreeWidgetItem(item)
                child.setText(0, key)
                node[key] = {}
            else:  # item is already in the tree
                child = node[key]["__item__"]
            value = data[key if is_dict else index]
            self.update_tree(child, value, node[key])

    def update_data(self, data: Union[dict, list, Any], node: dict) -> None:
        """Update data in the tree of the GUI left pane.

        Args:
            data: Data to update the tree with.
            node: Node corresponding to the data in the tree.
        """
        item = node["__item__"]
        if isinstance(data, dict):
            for key, value in data.items():
                self.update_data(value, node[key])
        elif isinstance(data, list):
            for index, value in enumerate(data):
                self.update_data(value, node[str(index)])
        else:  # data is not a dictionary
            item.setText(1, format_value(data))
            if "__plot__" in node:
                active = node["__plot__"].update(data)
                if not active:
                    del node["__plot__"]

    def handle_tree_expanded(
        self,
        item: QtWidgets.QTreeWidgetItem,
    ) -> None:
        """Handle event where a tree item is expanded.

        Args:
            item: Tree item that was expanded.
        """
        self.ui.telemetryTreeWidget.resizeColumnToContents(0)
        user_data = item.data(0, QtCore.Qt.UserRole)
        if user_data:
            user_data.expand()

    def handle_tree_collapsed(
        self,
        item: QtWidgets.QTreeWidgetItem,
    ) -> None:
        """Handle event where a tree item is collapsed.

        Args:
            item: Tree item that was collapsed.
        """
        user_data = item.data(0, QtCore.Qt.UserRole)
        if user_data:
            user_data.collapse()

    def get_node_name_from_item(
        self,
        item: QtWidgets.QTreeWidgetItem,
    ) -> Tuple[Union[dict, Any], str]:
        """Get internal tree node and name string from a GUI tree item.

        Args:
            item: Tree item from the GUI.

        Returns:
            Pair consisting of the corresponding internal-tree node (either a
            dictionary for an internal node, or a value) and its full
            dot-separated name.
        """
        top = item
        keys = []
        while top:
            keys.append(top.text(0))
            top = top.parent()
        keys.reverse()
        node = self.tree
        for key in keys:
            node = node[key]
        name = ".".join(keys)
        return node, name

    def handle_telemetry_context_menu(self, pos: QtCore.QPoint) -> None:
        """Display a right-click context menu in the telemetry tree.

        Args:
            pos: Coordinates where the user right-clicked.
        """
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
            node, name = self.get_node_name_from_item(item)
            callback = PlotCallback()
            node["__plot__"] = callback
            plot_item = self.ui.plotWidget.add_plot(
                name,
                callback,
                axis_number=1 if requested == plot_right_action else 0,
            )
            self.ui.plotItemCombo.addItem(name, plot_item)
        elif requested == copy_name_action:
            QtWidgets.QApplication.clipboard().setText(item.text(0))
        elif requested == copy_value_action:
            QtWidgets.QApplication.clipboard().setText(item.text(1))
        else:  # the user cancelled
            pass

    def handle_plot_item_remove(self):
        """Handle removal of a plot item."""
        index = self.ui.plotItemCombo.currentIndex()
        if index < 0:
            return
        item = self.ui.plotItemCombo.itemData(index)
        self.ui.plotWidget.remove_plot(item)
        self.ui.plotItemCombo.removeItem(index)
