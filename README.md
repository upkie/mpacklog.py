# mpacklog

[![Build](https://img.shields.io/github/workflow/status/stephane-caron/mpacklog/Bazel)](https://github.com/stephane-caron/mpacklog/actions)
[![Coverage](https://coveralls.io/repos/github/stephane-caron/mpacklog/badge.svg?branch=main)](https://coveralls.io/github/stephane-caron/mpacklog?branch=main)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen?logo=read-the-docs&style=flat)](https://scaron.info/doc/mpacklog/)
![C++ version](https://img.shields.io/badge/C++-17/20-blue.svg?style=flat)
[![Release](https://img.shields.io/github/v/release/stephane-caron/mpacklog.svg?sort=semver)](https://github.com/stephane-caron/mpacklog/releases)
![Status](https://img.shields.io/pypi/status/mpacklog)

Log dictionaries to file using the MessagePack serialization format.

## Installation

### Command-line and Python

```console
pip install mpacklog
```

### Bazel

Add a `git_repository` rule to your Bazel ``WORKSPACE``:

```python
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

git_repository(
    name = "mpacklog",
    remote = "https://github.com/stephane-caron/mpacklog.git",
    tag = "v1.0.0",
)
```

You can then use the following dependencies:

- ``@mpacklog//:cpp`` for C++ targets
- ``@mpacklog//:python`` for Python targets

## Usage

### C++

The C++ implementation uses multi-threading. Add messages to the log using the `put` function, they will be written to file in the background.

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
        logger.put(dict):
    }
}
```

### Python

The Python implementation uses asynchronous I/O. Add messages to the log using the `put` function, write them to file in the separate `write` coroutine.

```python
import asyncio
from mpacklog.python import AsyncLogger

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
