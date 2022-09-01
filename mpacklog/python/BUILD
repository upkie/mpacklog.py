# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "python",
    srcs = [
        "__init__.py",
        "logger.py",
        "serialize.py",
    ],
)

add_lint_tests(enable_clang_format_lint = True)
