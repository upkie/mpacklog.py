# -*- python -*-
#
# Copyright 2022 Stéphane Caron

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
        "async_logger.py",
        "sync_logger.py",
        "serialize.py",
    ],
)
