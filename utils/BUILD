# -*- python -*-
#
# Copyright 2022 Stéphane Caron

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

cc_library(
    name = "circular_buffer",
    hdrs = ["CircularBuffer.h"],
    deps = [
        "@spdlog",
    ],
    include_prefix = "vulp/utils",
)

cc_library(
    name = "utils",
    deps = [
        ":circular_buffer",
    ],
)

add_lint_tests(enable_clang_format_lint = True)
