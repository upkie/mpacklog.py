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

import logging
import os
import pickle
from os import path
from typing import List, Optional

import numpy as np

from .fields import get_from_field
from .printer import Printer


class ScriptPrinter(Printer):

    """
    Dump listed fields to a //sandbox/... Python target.
    """

    def __init__(self, output_dir: Optional[str], fields: List):
        """
        Configure printer options.

        Args:
            output_dir: Directory to write data and Python script to.
            fields: If given, only print out these selected fields (nested keys
                in "key1/.../keyN" format).
        """
        if output_dir is None:
            logging.warn("No --output-dir specified, defaulting to /tmp")
            output_dir = "/tmp"
        if not path.exists(output_dir):
            os.makedirs(output_dir)
        if "time" not in fields:
            fields.append("time")
        fields = [
            field[2:] if field.startswith("R:") else field for field in fields
        ]
        self.at_least_one_value = {field: False for field in fields}
        self.fields = fields
        self.output_dir = output_dir
        self.series = {field: [] for field in fields}

    def process(self, unpacked: dict):
        """
        Process a new unpacked dictionary.

        Args:
            unpacked: Unpacked dictionary.
        """
        for field in self.fields:
            try:
                value = get_from_field(unpacked, field)
                self.series[field].append(value)
                self.at_least_one_value[field] = True
            except KeyError:
                self.series[field].append(None)

    def finish(self, logfile):
        """
        Instructions executed once the whole log has been processed.

        Args:
            logfile: Path to input log file.
        """
        for field in self.fields:
            # first two values are None except for time
            self.series[field] = np.array(self.series[field][2:])
            if not self.at_least_one_value[field]:
                logging.warning(f'No data for field "{field}"')
        output_dir = self.output_dir
        data_file = path.join(output_dir, "data.pkl")
        main_file = path.join(output_dir, "main.py")
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
                """# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "main",
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
    series = pickle.load(open("data.pkl", "rb"))
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
