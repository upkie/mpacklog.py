# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/workspace/palimpsest:repository.bzl", "palimpsest_repository")
load("//tools/workspace/pycodestyle:repository.bzl", "pycodestyle_repository")

def add_default_repositories():
    """
    Declare workspace repositories for all dependencies. This function should
    be loaded and called from a WORKSPACE file.
    """
    palimpsest_repository()
    pycodestyle_repository()
