# mpackview

[![Conda version](https://img.shields.io/conda/vn/conda-forge/mpackview.svg)](https://anaconda.org/conda-forge/mpackview)
[![PyPI version](https://img.shields.io/pypi/v/mpackview)](https://pypi.org/project/mpackview/)

Watch and plot live updates from dictionaries serialized with MessagePack and streamed with [mpacklog](https://pypi.org/project/mpacklog/).

## Installation

### From conda-forge

```console
conda install -c conda-forge mpacklog
```

### From PyPI

```console
pip install mpackview
```

## Usage

```
mpackview <hostname>
```

## See also

- [mpacklog](https://pypi.org/project/mpacklog/): parent project this viewer is designed for.
- [moteus-gui](https://pypi.org/project/moteus-gui/): includes the fantastic ``tview`` telemetry GUI that ``mpackview`` derives from (the name is
itself a reference).
