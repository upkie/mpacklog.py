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

"""!
Manipulate MessagePack log files from the command line.
"""

import argparse
import time

import msgpack

from .printers import (
    CSVPrinter,
    FieldPrinter,
    JSONPrinter,
    Printer,
    ScriptPrinter,
)


def parse_command_line_arguments():
    main_parser = argparse.ArgumentParser(
        description="Manipulate MessagePack log files."
    )
    subparsers = main_parser.add_subparsers(title="subcommands", dest="subcmd")

    # mpacklog dump -----------------------------------------------------------
    dump_parser = subparsers.add_parser(
        "dump",
        help="Dump log file to the standard output.",
    )
    dump_parser.add_argument(
        "logfile", metavar="logfile", help="log file to open"
    )
    dump_parser.add_argument("fields", nargs="*", help="fields to plot")
    dump_parser.add_argument(
        "--csv",
        action="store_true",
        help="format output in CSV",
    )
    dump_parser.add_argument(
        "-f",
        "--follow",
        action="store_true",
        help="keep file open and follow, as in `tail -f`",
    )
    dump_parser.add_argument(
        "-l",
        "--list-fields",
        dest="list_fields",
        action="store_true",
        help="list available fields (nested keys) from each entry",
    )
    dump_parser.add_argument(
        "--script",
        metavar="script",
        help="dump listed fields to a //sandbox/... Python target",
    )
    return main_parser.parse_args()


def dump_log(logfile: str, follow: bool, printer: Printer):
    """!
    Dump log file.

    @param logfile Path to input log file.
    @param follow Keep file open and wait for updates?
    @param printer Printer class to process unpacked messages.
    """
    filehandle = open(logfile, "rb")
    unpacker = msgpack.Unpacker(raw=False)
    while True:
        data = filehandle.read(4096)
        if not data:  # end of file
            if follow:
                time.sleep(0.001)
                continue
            else:  # not follow
                break
        unpacker.feed(data)
        try:
            for unpacked in unpacker:
                printer.process(unpacked)
        except BrokenPipeError:  # handle e.g. piping to `head`
            break
    printer.finish(logfile)


def main(argv=None):
    args = parse_command_line_arguments()
    if args.list_fields:  # if -l is present, it overrides any other printer
        printer = FieldPrinter()
    elif args.csv:
        printer = CSVPrinter(args.fields)
    elif args.script:
        printer = ScriptPrinter(args.script, args.fields)
    else:  # print as JSON to standard output
        printer = JSONPrinter(args.fields)
    dump_log(args.logfile, args.follow, printer)
