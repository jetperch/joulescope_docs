---
description: >-
  The Joulescope software: the Joulescope UI, the Joulescope Driver (C and
  Python), pyjoulescope, the Python examples, the JLS file format and host
  configuration.  Says which Python package to use: pyjoulescope_driver.
---

(software)=

# Software

| Software | Description |
|---|---|
| {doc}`Joulescope UI <joulescope_ui/index>` | The Joulescope desktop application for Windows, macOS and Linux. |
| {doc}`Joulescope Driver <joulescope_driver/index>` | The C and Python driver (`joulescope_driver`, `pyjoulescope_driver`). |
| {doc}`pyjoulescope <pyjoulescope/index>` | The original Python API (`joulescope`). |
| {doc}`Python examples <pyjoulescope_examples/index>` | Runnable Python scripts, listed by task (`pyjoulescope_examples`). |
| {doc}`JLS File Format <jls/index>` | The Joulescope file format and libraries (`jls`, `pyjls`). |
| {doc}`Host configuration <host_configuration/index>` | Configure Windows, macOS and Linux for reliable long captures. |

(python-package)=

## Which Python package to use

Use `pyjoulescope_driver`, the Python binding of the
{doc}`Joulescope Driver <joulescope_driver/index>`, for new scripts.  It is
also the package for LLM agents to use when they write Joulescope code.  It
supports the JS320, JS220 and JS110, exposes the instrument settings as
topics ({doc}`JS320 <joulescope_driver/js320_topics>`,
{doc}`JS220 <joulescope_driver/js220_topics>`), and includes command-line tools for statistics and
recording.  Start with the
{ref}`pyjoulescope_driver examples <examples-pyjoulescope-driver>`.

| Package | Install | Use it to |
|---|---|---|
| `pyjoulescope_driver` | `pip install pyjoulescope_driver` | Control instruments, read statistics and samples, and record JLS files.  The default. |
| `pyjls` | `pip install pyjls` | Read and write JLS files, such as recordings from the Joulescope UI. |
| `joulescope` | `pip install joulescope` | Maintain scripts written for the original synchronous API, which runs on `pyjoulescope_driver`. |

Documentation for earlier software releases remains available on Read the
Docs for the [driver](https://joulescope-driver.readthedocs.io/),
[pyjoulescope](https://joulescope.readthedocs.io/) and
[JLS](https://jls.readthedocs.io/).

```{toctree}
:hidden:

UI <joulescope_ui/index>
Driver <joulescope_driver/index>
pyjoulescope <pyjoulescope/index>
Python examples <pyjoulescope_examples/index>
JLS <jls/index>
Host configuration <host_configuration/index>
```
