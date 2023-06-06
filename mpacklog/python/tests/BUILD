# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

py_test(
    name = "async_logger_test",
    srcs = ["async_logger_test.py"],
    deps = [
        "//mpacklog/python",
    ],
)

py_test(
    name = "sync_logger_test",
    srcs = ["sync_logger_test.py"],
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

add_lint_tests()
