# mpacklog

[![Build](https://img.shields.io/github/workflow/status/stephane-caron/mpacklog/Bazel)](https://github.com/stephane-caron/mpacklog/actions)
[![Coverage](https://coveralls.io/repos/github/stephane-caron/mpacklog/badge.svg?branch=main)](https://coveralls.io/github/stephane-caron/mpacklog?branch=main)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen?logo=read-the-docs&style=flat)](https://scaron.info/doc/mpacklog/)
![C++ version](https://img.shields.io/badge/C++-17/20-blue.svg?style=flat)
[![Release](https://img.shields.io/github/v/release/stephane-caron/mpacklog.svg?sort=semver)](https://github.com/stephane-caron/mpacklog/releases)
<!-- ![Status](https://img.shields.io/pypi/status/mpacklog) -->

Log dictionaries to file using the MessagePack serialization format.

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

using palimpsest::Dictionary;

int main() {
    mpacklog::Logger logger("output.mpack");
    for (unsigned bar = 0; bar < 1000u; ++bar) {
        Dictionary dict;
        dict("foo") = bar;
        dict("something") = "else";
        logger.put(dict):
    }
}
```

### Python

The Python implementation uses asynchronous I/O. Add messages to the log using the [`put`](https://scaron.info/doc/mpacklog/classmpacklog_1_1mpacklog_1_1python_1_1async__logger_1_1AsyncLogger.html#a0ce63a4b1ef7664126a4816e94ebf21b) function, write them to file in the separate [`write`](https://scaron.info/doc/mpacklog/classmpacklog_1_1mpacklog_1_1python_1_1async__logger_1_1AsyncLogger.html#a3f7d7b7f2579f036af203f856fbe9b7b) coroutine.

```python
import asyncio
from mpacklog import AsyncLogger

async def main(logger):
    for bar in range(1000):
        await asyncio.sleep(1e-3)
        await logger.put({"foo": bar, "something": "else"})

async def main_with_logging():
    logger = AsyncLogger("output.mpack")
    await asyncio.gather(
        main(logger),
        logger.write(),  # write to file when main is idle
    )

if __name__ == "__main__":
    asyncio.run(main_with_logging())
```
