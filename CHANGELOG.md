# Changelog

## Unreleased

### Added

- Bazel: Find clang-format on various operating systems

### Changed

- **Breaking:** Clean up unused script printer from CLI
- **Breaking:** Move C++ version to ``mpacklog.cpp``
- Bazel: Compile build targets in optimized mode by default
- Bazel: Compile coverage and test targets in debug mode by default
- Compile in optimized rather than fast-build mode by default

## [3.0.0] - 2023/06/06

### Added

- Synchronous ``SyncLogger`` class

### Changed

- CI: Update Bazelisk script
- Rename ``Logger`` to ``AsyncLogger``
- Remove unused ``mypy_integration``

## [2.1.0] - 2023/04/26

### Changed

- Make code compatible with macOS (thanks to @boragokbakan)

## [2.0.0] - 2022/09/01

### Added

- Dump log to CSV from the command line
- Dump log to JSON from the command line
- Dump log to Python script from the command line
- List log fields from the command line
- Python `Logger` implementation
- `mpacklog` command-line tool
- Unit tests for Python API

## [1.0.0] - 2022/08/17

First release of the project.
