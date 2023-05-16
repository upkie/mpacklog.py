# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")
load("@pip_mpacklog//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "python",
    deps = [
        requirement("aiofiles"),
        requirement("msgpack"),
    ],
    srcs = [
        "__init__.py",
        "logger.py",
        "serialize.py",
    ],
)

add_lint_tests()
