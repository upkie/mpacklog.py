# -*- python -*-
#
# Copyright 2022 Stéphane Caron

workspace(name = "mpacklog")

load("//tools/workspace:default.bzl", "add_default_repositories")
add_default_repositories()

# @palimpsest is a default repository
load("@palimpsest//tools/workspace:default.bzl", add_palimpsest_repositories = "add_default_repositories")
add_palimpsest_repositories()

# We can load this now that @rules_python has been added as a @palimpsest repository
load("//tools/workspace/pip_mpacklog:parse_deps.bzl", "parse_deps")
parse_deps()
load("@pip_mpacklog//:requirements.bzl", "install_deps")
install_deps()
