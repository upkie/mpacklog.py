# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("@rules_python//python:pip.bzl", "pip_parse")

def parse_deps():
    """
    Parse Python dependencies to a @pip_mpacklog external repository.

    This function intended to be loaded and called from your WORKSPACE.
    """
    pip_parse(
        name = "pip_mpacklog",
        requirements_lock = Label("//tools/workspace/pip_mpacklog:requirements_lock.txt"),
    )
