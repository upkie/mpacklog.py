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

import asyncio
import os
import sys

import moteus.reader as reader
import numpy
from PySide2 import QtUiTools
from qtpy import QtCore, QtWidgets
from sized_tree_widget import SizedTreeWidget
from stream_client import StreamClient

os.environ["QT_API"] = "pyside2"

import asyncqt  # noqa: E402
from plot_widget import PlotWidget  # noqa: E402

DEFAULT_RATE = 100
FORMAT_ROLE = QtCore.Qt.UserRole + 1
MAX_HISTORY_SIZE = 100


def _get_data(value, name):
    fields = name.split(".")
    for field in fields:
        if isinstance(value, list):
            value = value[int(field)]
        else:
            value = getattr(value, field)
    return value


def _add_schema_item(parent, element, terminal_flags=None):
    # Cache our schema, so that we can use it for things like
    # generating better input options.
    parent.setData(1, QtCore.Qt.UserRole, element)

    if isinstance(element, reader.ObjectType):
        for field in element.fields:
            name = field.name

            item = QtWidgets.QTreeWidgetItem(parent)
            item.setText(0, name)

            _add_schema_item(
                item, field.type_class, terminal_flags=terminal_flags
            )
    else:
        if terminal_flags:
            parent.setFlags(terminal_flags)


def _set_tree_widget_data(item, struct, element, terminal_flags=None):
    if (
        isinstance(element, reader.ObjectType)
        or isinstance(element, reader.ArrayType)
        or isinstance(element, reader.FixedArrayType)
    ):
        if not isinstance(element, reader.ObjectType):
            for i in range(item.childCount(), len(struct)):
                subitem = QtWidgets.QTreeWidgetItem(item)
                subitem.setText(0, str(i))
                _add_schema_item(
                    subitem, element.type_class, terminal_flags=terminal_flags
                )
        for i in range(item.childCount()):
            child = item.child(i)
            if isinstance(struct, list):
                field = struct[i]
                child_element = element.type_class
            else:
                name = child.text(0)
                field = getattr(struct, name)
                child_element = element.fields[i].type_class
            _set_tree_widget_data(
                child, field, child_element, terminal_flags=terminal_flags
            )
    else:
        text = repr(struct)
        item.setText(1, text)


class RecordSignal(object):
    def __init__(self):
        self._index = 0
        self._callbacks = {}

    def connect(self, handler):
        result = self._index
        self._index += 1
        self._callbacks[result] = handler

        class Connection(object):
            def __init__(self, parent, index):
                self.parent = parent
                self.index = index

            def remove(self):
                del self.parent._callbacks[self.index]

        return Connection(self, result)

    def update(self, value):
        for handler in self._callbacks.values():
            handler(value)
        return len(self._callbacks) != 0


class Record:
    def __init__(self, archive):
        self.archive = archive
        self.signals = {}
        self.history = []

    def get_signal(self, name):
        if name not in self.signals:
            self.signals[name] = RecordSignal()
        return self.signals[name]

    def update(self, struct):
        count = 0
        self.history.append(struct)
        if len(self.history) > MAX_HISTORY_SIZE:
            self.history = self.history[1:]

        for key, signal in self.signals.items():
            if key.startswith("__STDDEV_"):
                remaining = key.split("__STDDEV_")[1]
                values = [_get_data(x, remaining) for x in self.history]
                value = numpy.std(values)
            elif key.startswith("__MEAN_"):
                remaining = key.split("__MEAN_")[1]
                values = [_get_data(x, remaining) for x in self.history]
                value = numpy.mean(values)
            else:
                value = _get_data(struct, key)
            if signal.update(value):
                count += 1
        return count != 0


def _get_item_root(item):
    while item.parent().parent():
        item = item.parent()
    return item.text(0)


class MpacklogMainWindow:
    """Main application window.

    Attributes:
        stream_client: Client to read streaming data from.
    """

    stream_client: StreamClient

    def __init__(self, host: str, port: int, parent=None):
        stream_client = StreamClient(host, port)
        self.default_rate = 100
        self.user_task = None

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
            self._handle_tree_expanded
        )
        self.ui.telemetryTreeWidget.itemCollapsed.connect(
            self._handle_tree_collapsed
        )
        self.ui.telemetryTreeWidget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        self.ui.telemetryTreeWidget.customContextMenuRequested.connect(
            self._handle_telemetry_context_menu
        )

        self.ui.plotItemRemoveButton.clicked.connect(
            self._handle_plot_item_remove
        )

        layout = QtWidgets.QVBoxLayout(self.ui.plotHolderWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.ui.plotHolderWidget.setLayout(layout)
        self.ui.plotWidget = PlotWidget(self.ui.plotHolderWidget)
        layout.addWidget(self.ui.plotWidget)

        def update_plot_widget(value):
            self.ui.plotWidget.history_s = value

        self.ui.historySpin.valueChanged.connect(update_plot_widget)

        QtCore.QTimer.singleShot(0, self._handle_startup)
        self.stream_client = stream_client
        self.tree = {}

    def show(self):
        self.ui.show()

    def _handle_startup(self):
        self.ui.telemetryTreeWidget.clear()
        data = self.stream_client.read()
        self.tree = {}
        self.update_telemetry(self.ui.telemetryTreeWidget, data, self.tree)
        asyncio.create_task(self._run())

    def update_telemetry(self, item, data, tree: dict):
        tree["__item__"] = item
        if isinstance(data, dict):
            for key, value in data.items():
                child = QtWidgets.QTreeWidgetItem(item)
                child.setText(0, key)
                tree[key] = {}
                self.update_telemetry(child, value, tree[key])

    async def _run(self):
        while True:
            data = self.stream_client.read()
            self.update_data(data, self.tree)
            await asyncio.sleep(0.01)

    def update_data(self, data, tree):
        item = tree["__item__"]
        if isinstance(data, dict):
            for key, value in data.items():
                self.update_data(value, tree[key])
        else:  # data is not a dictionary
            item.setText(1, str(data))
            if "__record__" in tree:
                tree["__record__"].update(data)

    def _handle_tree_expanded(self, item):
        self.ui.telemetryTreeWidget.resizeColumnToContents(0)
        user_data = item.data(0, QtCore.Qt.UserRole)
        if user_data:
            user_data.expand()

    def _handle_tree_collapsed(self, item):
        user_data = item.data(0, QtCore.Qt.UserRole)
        if user_data:
            user_data.collapse()

    def _handle_telemetry_context_menu(self, pos):
        item = self.ui.telemetryTreeWidget.itemAt(pos)
        if item.childCount() > 0:
            return

        menu = QtWidgets.QMenu(self.ui)
        left_action = menu.addAction("Plot Left")
        right_action = menu.addAction("Plot Right")

        plot_actions = [
            left_action,
            right_action,
        ]

        right_actions = [right_action]

        menu.addSeparator()
        copy_name = menu.addAction("Copy Name")
        copy_value = menu.addAction("Copy Value")

        requested = menu.exec_(self.ui.telemetryTreeWidget.mapToGlobal(pos))

        if requested in plot_actions:
            top = item
            keys = []
            while top:
                keys.append(top.text(0))
                top = top.parent()
            keys.reverse()
            name = ".".join(keys)
            print(f"{name=}")
            node = self.tree
            for key in keys:
                node = node[key]
            record_signal = RecordSignal()
            node["__record__"] = record_signal
            axis = 1 if requested in right_actions else 0
            plot_item = self.ui.plotWidget.add_plot(name, record_signal, axis)
            self.ui.plotItemCombo.addItem(name, plot_item)
        elif requested == copy_name:
            QtWidgets.QApplication.clipboard().setText(item.text(0))
        elif requested == copy_value:
            QtWidgets.QApplication.clipboard().setText(item.text(1))
        else:  # the user cancelled
            pass

    def _handle_plot_item_remove(self):
        index = self.ui.plotItemCombo.currentIndex()
        if index < 0:
            return
        item = self.ui.plotItemCombo.itemData(index)
        self.ui.plotWidget.remove_plot(item)
        self.ui.plotItemCombo.removeItem(index)


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = asyncqt.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # To work around https://bugreports.qt.io/browse/PYSIDE-88
    app.aboutToQuit.connect(lambda: os._exit(0))

    window = MpacklogMainWindow("localhost", 4747)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
