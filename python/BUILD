# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "serialize",
    srcs = [
        "serialize.py",
    ],
)

py_library(
    name = "async_logger",
    srcs = [
        "async_logger.py",
    ],
    deps = [
        ":serialize",
    ],
)

py_library(
    name = "python",
    deps = [
        ":async_logger",
    ],
)

add_lint_tests(enable_clang_format_lint = True)
