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
import json
import logging
import os
import pickle
import time
from dataclasses import dataclass
from os import path
from typing import Any, Dict, List, Optional, Union

import msgpack
import numpy as np


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


@dataclass
class Field:

    """!
    A field stores the key path to a value in input dictionaries. The path
    `"foo/bar/blah"` means the value in a dictionary `input` is located at
    `input["foo"]["bar"]["blah"]`.
    """

    label: str
    plot_right: bool = False

    @property
    def keys(self):
        """
        List of keys to search field values from in input data dictionaries.
        """
        return self.label.split("/")


def list_fields(observation: dict, prefix: str = "") -> List[str]:
    """!
    List all fields available in an observation dictionary.

    @param observation Observation dictionary.
    @returns List of fields in the observation dictionary.
    """
    fields = []
    for key in observation:
        child_prefix = key if not prefix else f"{prefix}/{key}"
        if isinstance(observation[key], dict):
            fields.extend(list_fields(observation[key], child_prefix))
        else:  # observation[key] is a value
            fields.append(child_prefix)
    return fields


def print_fields(observation: dict, label: str = "") -> None:
    """!
    Print all fields available in an observation dictionary.

    @param observation Observation dictionary
    @param label Label to identify the dictionary.
    """
    manucure = "\n- "
    fields = list_fields(observation)
    print(f"Fields in {label}:" if label else "Fields:", end="")
    print(manucure.join([""] + sorted(fields)))


def get_from_keys(
    collection: Union[dict, list], keys: list, default: Optional[Any] = None
):
    """!
    Get value `d[key1][key2][...][keyN]` into a dictionary `d` from keys
    `[key1, key2, ..., keyN]`.

    @param collection Dictionary or list to get value from.
    @param keys Sequence of keys to the value.
    @param default If provided, return this value if there is nothing in
        `collection` at that field.
    """
    key = keys[0]
    if isinstance(collection, list):
        key = int(key)
    try:
        child = collection[key]
    except KeyError:
        if default is not None:
            return default
        raise
    if len(keys) == 1:
        return child
    try:
        return get_from_keys(child, keys[1:])
    except KeyError as e:
        if default is not None:
            return default
        raise KeyError(f"{key}/{str(e)[1:-1]}")


def get_from_field(
    collection: Union[dict, list], field: str, default: Optional[Any] = None
):
    """!
    Get value `d[key1][key2][...][keyN]` into a dictionary `d` from its field
    "key1/key2/.../keyN".

    @param collection Dictionary or list to get value from.
    @param field Field string.
    @param default If provided, return this value if there is nothing in
        `collection` at that field.
    """
    keys = field.split("/")
    return get_from_keys(collection, keys, default)


def set_from_keys(dictionary: dict, keys: list, value):
    """!
    Set the value `d[key1][key2][...][keyN]` into a dictionary `d`.

    @param dictionary Dictionary to get value from.
    @param keys Sequence of keys to the value.
    @param value New value.
    """
    key = keys[0]
    if len(keys) > 1:
        if key not in dictionary:
            dictionary[key] = {}
        return set_from_keys(dictionary[key], keys[1:], value)
    dictionary[key] = value


def filter_fields(dictionary: Dict, fields: Optional[List] = None):
    """!
    Filter selected fields in a dictionary.

    @param dictionary Dictionary to filter.
    @param fields If given, only print out these selected fields (nested keys
        in "key1/.../keyN" format).
    @returns Filtered dictionary.
    """
    if not fields:
        return dictionary
    output = {}
    for field in fields:
        keys = field.split("/")
        try:
            value = get_from_keys(dictionary, keys)
            set_from_keys(output, keys, value)
        except KeyError as e:
            print(f"Field {str(e)} not found when looking up '{field}'")
    return output


class Printer:

    """!
    Base class for printers. A printer processes unpacked dictionaries one by
    one, and wraps up this data once the whole log has been parsed.
    """

    def process(self, unpacked):
        """!
        Process a new unpacked dictionary.

        @param unpacked Unpacked dictionary.
        """
        pass

    def finish(self, logfile: str = ""):
        """!
        Instructions executed once the whole log has been processed.

        @param logfile Path to input log file.
        """
        pass


class JSONPrinter(Printer):

    """!
    Default printer: print everything in JSON Lines.
    """

    def __init__(self, fields: Optional[List] = None):
        """
        Configure printer options.

        @param fields If given, only print out these selected fields (nested
            keys in "key1/.../keyN" format).
        """
        self.fields = fields

    def process(self, unpacked):
        """
        Process a new unpacked dictionary.

        @param unpacked Unpacked dictionary.
        """
        output_with_nan = json.dumps(
            filter_fields(unpacked, self.fields), allow_nan=True
        )
        print(output_with_nan.replace(" NaN", " null"))  # kroOOOOoooonn!!!


class FieldPrinter(Printer):

    """!
    Parse whole log, then finally list all fields encountered.
    """

    def __init__(self):
        self.fields = set([])
        self.observation = {}

    def process(self, unpacked):
        """
        Process a new unpacked dictionary.

        @param unpacked Unpacked dictionary.
        """
        unpacked_fields = set(list_fields(unpacked))
        new_fields = unpacked_fields - self.fields
        if len(new_fields) > 0:
            for field in sorted(list(new_fields)):
                print(f"- {field}")
            print("")
        self.fields = set.union(self.fields, new_fields)
        self.observation.update(unpacked)

    def finish(self, logfile):
        """
        Instructions executed once the whole log has been processed.

        @param logfile Path to input log file.
        """


class CSVPrinter(Printer):

    """!
    Print a list of fields in CSV format.
    """

    def __init__(self, fields: List[str]):
        assert len(fields) > 0
        if fields[0] != "time":
            fields.insert(0, "time")
        print(",".join(fields))
        self.fields = fields

    def process(self, unpacked: dict):
        """!
        Process a new unpacked dictionary.

        @param unpacked Unpacked dictionary.
        """

        def str_from_value(v):
            if isinstance(v, bool):
                return "1" if v else "0"
            return str(v)

        values = [
            str_from_value(get_from_field(unpacked, field, default="0"))
            for field in self.fields
        ]
        print(",".join(values))

    def finish(self, logfile: str = ""):
        """!
        Instructions executed once the whole log has been processed.

        @param logfile Path to log file.
        """
        pass


class ScriptAggregator(Printer):

    """!
    Dump listed fields to a //sandbox/... Python target.
    """

    def __init__(self, script_path: str, fields: List):
        """!
        Configure printer options.

        @param script_path Path to output script.
        @param fields If given, only print out these selected fields (nested
            keys in "key1/.../keyN" format).
        """
        script = path.basename(script_path)
        output_dir = path.dirname(script_path)
        if path.exists(output_dir):
            raise FileExistsError(f"Directory {output_dir} already exists")
        os.makedirs(output_dir)
        if "time" not in fields:
            fields.append("time")
        fields = [
            field[2:] if field.startswith("R:") else field for field in fields
        ]
        self.at_least_one_value = {field: False for field in fields}
        self.fields = fields
        self.output_dir = output_dir
        self.script = script
        self.series = {field: [] for field in fields}

    def process(self, unpacked):
        """!
        Process a new unpacked dictionary.

        @param unpacked Unpacked dictionary.
        """
        for field in self.fields:
            keys = field.split("/")
            try:
                value = get_from_keys(unpacked, keys)
                self.series[field].append(value)
                self.at_least_one_value[field] = True
            except KeyError:
                self.series[field].append(None)

    def finish(self, logfile):
        """!
        Instructions executed once the whole log has been processed.

        @param logfile Path to input log file.
        """
        for field in self.fields:
            # first two values are None except for time
            self.series[field] = np.array(self.series[field][2:])
            if not self.at_least_one_value[field]:
                logging.warning(f'No data for field "{field}"')
        output_dir = self.output_dir
        data_file = path.join(output_dir, f"{self.script}.pkl")
        main_file = path.join(output_dir, f"{self.script}.py")
        start_ipython_file = path.join(output_dir, "start_ipython.py")
        build_file = path.join(output_dir, "BUILD")
        with open(data_file, "wb") as pickle_file:
            pickle.dump(self.series, pickle_file)
        with open(start_ipython_file, "w") as output:
            output.write(
                f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import IPython

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    IPython.start_ipython(["--pylab", "-i", "{main_file}"])
                """
            )
        with open(build_file, "w") as output:
            output.write(
                f"""# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "{self.script}",
    srcs = [
        "{path.basename(main_file)}",
        "start_ipython.py",
    ],
    main = "start_ipython.py",
    data = ["{path.basename(data_file)}"],
    deps = [
        # add dependencies here
    ],
)

add_lint_tests(enable_clang_format_lint = True)"""
            )
        with open(main_file, "w") as output:
            output.write(
                f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Data extracted with `dump_log` from:
# {path.realpath(logfile)}

import pickle
import pylab

if __name__ == "__main__":
    series = pickle.load(open("{self.script}.pkl", "rb"))
    time = series["time"]
    dt = round((time[-1] - time[0]) / (len(time) - 1), 3)
"""
            )
            for i, field in enumerate(self.fields):
                if field != "time":
                    output.write(f'    y{i} = series["{field}"]\n')
            output.write(
                """
    t = []
    start_time = 0.0  # [s]
    end_time = dt * len(time)  # [s]
    for i in range(int(start_time / dt), int(end_time / dt)):
        t.append(time[i] - time[0])
        # fun starts here

    pylab.ion()
    pylab.grid(True)
    pylab.plot(t, y0)
"""
            )
        print(f"Log dumped to {output_dir}")
        print(f"Go edit {main_file}, then run it")


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
        printer = ScriptAggregator(args.script, args.fields)
    else:  # print as JSON to standard output
        printer = JSONPrinter(args.fields)
    dump_log(args.logfile, args.follow, printer)
