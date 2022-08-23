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

"""
Manipulate MessagePack log files from the command line.
"""

import argparse
import time

import msgpack

from .csv_printer import CSVPrinter
from .field_printer import FieldPrinter
from .json_printer import JSONPrinter
from .printer import Printer
from .script_printer import ScriptPrinter


def get_argument_parser() -> argparse.ArgumentParser:
    """
    Parser for command-line arguments.

    Returns:
        Command-line argument parser.
    """
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
        "--format",
        choices=["csv", "json", "python"],
        default="json",
        help="output format (CSV, JSON Lines or Python script)",
    )
    dump_parser.add_argument(
        "-f",
        "--follow",
        action="store_true",
        help="keep file open and follow, as in `tail -f`",
    )
    dump_parser.add_argument(
        "--output-dir",
        metavar="output_dir",
        help="Output directory to write data and Python script to.",
    )

    # mpacklog list -----------------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="List fields in a log",
    )
    list_parser.add_argument(
        "logfile", metavar="logfile", help="log file to open"
    )

    return main_parser


def dump_log(logfile: str, printer: Printer, follow: bool = False) -> None:
    """
    Dump log file.

    Args:
        logfile: Path to input log file.
        printer: Printer class to process unpacked messages.
        follow (optional): Keep file open and wait for updates?
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


def main(argv=None) -> None:
    """
    Main function for the `mpacklog` command line.

    Args:
        argv: Command-line arguments.
    """
    parser = get_argument_parser()
    args = parser.parse_args(argv)
    if args.subcmd == "list":
        printer = FieldPrinter()
        dump_log(args.logfile, printer)
    elif args.subcmd == "dump":
        if args.format == "csv":
            printer = CSVPrinter(args.fields)
        elif args.format == "json":
            printer = JSONPrinter(args.fields)
        elif args.format == "python":
            printer = ScriptPrinter(args.output_dir, args.fields)
        dump_log(args.logfile, printer, follow=args.follow)
    else:  # no subcommand
        parser.print_help()
