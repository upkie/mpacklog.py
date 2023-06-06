# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "python",
    srcs = [
        "__init__.py",
        "async_logger.py",
        "sync_logger.py",
        "serialize.py",
    ],
)

add_lint_tests()
