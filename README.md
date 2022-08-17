# mpacklog

[![Build](https://img.shields.io/github/workflow/status/stephane-caron/mpacklog/Bazel)](https://github.com/stephane-caron/mpacklog/actions)
[![Coverage](https://coveralls.io/repos/github/stephane-caron/mpacklog/badge.svg?branch=main)](https://coveralls.io/github/stephane-caron/mpacklog?branch=main)
![C++ version](https://img.shields.io/badge/C++-17/20-blue.svg?style=flat)
[![Release](https://img.shields.io/github/v/release/stephane-caron/mpacklog.svg?sort=semver)](https://github.com/stephane-caron/palimpsest/releases)

Log dictionaries to file using the MessagePack serialization format.

## Installation

### Bazel

Call a [git\_repository](https://bazel.build/rules/lib/repo/git#git_repository) rule from your Bazel ``WORKSPACE``:

```python
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

def mpacklog_repository():
    git_repository(
        name = "mpacklog",
        remote = "git@github.com:stephane-caron/mpacklog.git",
        commit = "...",
        shallow_since = "..."
    )
```

You can then use the ``@mpacklog//mpacklog:cpp`` dependency in your C++ targets.

## Usage

### C++ logger

```cpp
#include <mpacklog/Logger.h>
#include <palimpsest/Dictionary.h>

int main()
{
    mpacklog::Logger logger("output.mpack");

    for (unsigned bar = 0; bar < 1000u; ++bar) {
        palimpsest::Dictionary dict;
        dict("foo") = bar;
        dict("something") = "else";

        logger.write(dict):
    }
}
```
