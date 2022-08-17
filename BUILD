# -*- python -*-

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

exports_files([
    "CPPLINT.cfg",
    ".clang-format",
])

cc_library(
    name = "mpacklog",
    deps = [
        ":dictionary",
    ],
)

add_lint_tests()
