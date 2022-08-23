# -*- python -*-

load("//tools/lint:lint.bzl", "add_lint_tests")

package(default_visibility = ["//visibility:public"])

exports_files([
    "CPPLINT.cfg",
    ".clang-format",
])

cc_library(
    name = "cpp",
    deps = [
        "//mpacklog/cpp",
    ],
)

cc_library(
    name = "mpacklog",
    deps = [
        "//mpacklog/cpp",
    ],
)

py_library(
    name = "python",
    srcs = [
        "__init__.py",
    ],
    deps = [
        "//mpacklog/python",
    ],
)

add_lint_tests()
