# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("@rules_python//python:pip.bzl", "pip_install")

def install_python_deps():
    """
    Install Python packages to a @pip_mpack_logs external repository.

    This function intended to be loaded and called from your WORKSPACE.
    """
    pip_install(
        name = "pip_mpack_logs",
        requirements = Label("//tools/workspace/pip_mpack_logs:requirements.txt"),
    )
