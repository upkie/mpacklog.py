# mpacklog

[![Build](https://img.shields.io/github/workflow/status/stephane-caron/mpacklog/Bazel)](https://github.com/stephane-caron/mpacklog/actions)
[![Coverage](https://coveralls.io/repos/github/stephane-caron/mpacklog/badge.svg?branch=main)](https://coveralls.io/github/stephane-caron/mpacklog?branch=main)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen?logo=read-the-docs&style=flat)](https://scaron.info/doc/mpacklog/)
![C++ version](https://img.shields.io/badge/C++-17/20-blue.svg?style=flat)
[![Release](https://img.shields.io/github/v/release/stephane-caron/mpacklog.svg?sort=semver)](https://github.com/stephane-caron/mpacklog/releases)
<!-- ![Status](https://img.shields.io/pypi/status/mpacklog) -->

Log dictionaries to MessagePack files in C++ and Python.

## Installation

### Python

```console
pip install mpacklog
```

### Bazel

Add a git repository rule to your Bazel ``WORKSPACE``:

```python
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

git_repository(
    name = "mpacklog",
    remote = "https://github.com/stephane-caron/mpacklog.git",
    tag = "v1.0.0",
)
```

You can then use the ``@mpacklog`` dependency for C++ targets, or the
``@mpacklog//:python`` dependency for Python targets.

## Usage

### C++

The C++ implementation uses multi-threading. Add messages to the log using the [`put`](https://scaron.info/doc/mpacklog/classmpacklog_1_1Logger.html#af0c278a990b1275b306e89013bb1fac6) function, they will be written to file in the background.

```cpp
#include <mpacklog/Logger.h>
#include <palimpsest/Dictionary.h>

int main() {
    mpacklog::Logger logger("output.mpack");

    for (unsigned bar = 0; bar < 1000u; ++bar) {
        palimpsest::Dictionary dict;
        dict("foo") = bar;
        dict("something") = "else";
        logger.put(dict):
    }
}
```

### Python

The Python implementation uses asynchronous I/O. Add messages to the log using the [`put`](https://scaron.info/doc/mpacklog/classmpacklog_1_1mpacklog_1_1python_1_1logger_1_1Logger.html#aa0f928ac07280acd132627d8545a7e18) function, have them written to file in the separate [`write`](https://scaron.info/doc/mpacklog/classmpacklog_1_1mpacklog_1_1python_1_1logger_1_1Logger.html#acbea9c05c465423efc3f38a25ed699d2) coroutine.

```python
import asyncio
import mpacklog

async def main():
    logger = mpacklog.Logger("output.mpack")

    await asyncio.gather(
        main_loop(logger),
        logger.write(),
    )

async def main_loop(logger):
    for bar in range(1000):
        await asyncio.sleep(1e-3)
        await logger.put({"foo": bar, "something": "else"})
    await logger.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Command-line

If you ``pip``-installed mpacklog, you can use the ``mpacklog`` command to dump logs to JSON:

```console
mpacklog dump my_log.mpack
```

Alternatively and more generally, two great tools to manipulate logs from the command line are:

* [`rq`](https://github.com/dflemstr/rq): transform from/to MessagePack, JSON, YAML, TOML, ...
* [`jq`](https://github.com/stedolan/jq): manipulate JSON series to add, remove or extend fields

For instance, ``mpacklog dump`` is equivalent to:

```console
rq -mJ < my_log.mpack
```
