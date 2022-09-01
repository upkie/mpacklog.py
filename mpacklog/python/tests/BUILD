# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_test(
    name = "logger_test",
    srcs = ["logger_test.py"],
    deps = [
        "//mpacklog/python",
    ],
)

py_test(
    name = "serialize_test",
    srcs = ["serialize_test.py"],
    deps = [
        "//mpacklog/python",
    ],
)

add_lint_tests(enable_clang_format_lint = True)
