#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 mjbots Robotic Systems, LLC.  info@mjbots.com
# Copyright 2024 Inria
#
# This file incorporates code from utils/gui/moteus_gui/tview.py
# (https://github.com/mjbots/moteus, 49c698a63f0ded22528ad7539cc2e27e41cd486d)

"""Interactively display values from a MessagePack stream."""

import argparse
import asyncio
import os
import sys

import PySide2  # noqa: E402 F401
from qtpy import QtCore, QtWidgets

from .stream_client import StreamClient

# For these imports to work, we should set QT_API after PySide2 has been
# imported (yes) but before asyncqt and the other imports for the main window
os.environ["QT_API"] = "pyside2"

# The following imports should come after QT_API has been set
import asyncqt  # noqa: E402

from .window import Window  # noqa: E402

# Why this is necessary and not just the default, I don't know, but
# otherwise we get a warning about "Qt WebEngine seems to be
# initialized from a plugin..."
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)


def parse_command_line_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Namespace resulting from parsing command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Serve most recent values from a spine log.",
    )
    parser.add_argument(
        "destination",
        help="host name or IP address to connect to",
        type=str,
    )
    parser.add_argument(
        "--port",
        "-p",
        help="port to listen to",
        type=int,
        default=4747,
    )
    return parser.parse_args()


def main(argv=None) -> None:
    args = parse_command_line_arguments()
    stream_client = StreamClient(args.destination, args.port)
    app = QtWidgets.QApplication(sys.argv)
    loop = asyncqt.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # To work around https://bugreports.qt.io/browse/PYSIDE-88
    app.aboutToQuit.connect(lambda: os._exit(0))

    window = Window(stream_client)
    window.show()
    app.exec_()
