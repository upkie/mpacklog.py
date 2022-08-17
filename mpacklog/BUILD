# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

cc_library(
    name = "circular_buffer",
    hdrs = [
        "CircularBuffer.h",
    ],
    include_prefix = "mpacklog",
    deps = [
        "@spdlog",
    ],
)

cc_library(
    name = "logger",
    hdrs = [
        "Logger.h",
    ],
    include_prefix = "mpacklog",
    srcs = [
        "Logger.cpp",
    ],
    copts = [
        "-pthread",
    ],
    linkopts = [
        "-pthread",
    ],
    deps = [
        "@palimpsest",
        ":circular_buffer",
    ],
)

cc_library(
    name = "cpp",
    deps = [
        ":circular_buffer",
        ":logger",
    ],
)

add_lint_tests(enable_clang_format_lint = True)
