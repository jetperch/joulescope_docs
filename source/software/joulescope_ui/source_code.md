---
description: >-
  The open-source repositories behind the Joulescope UI and how to script
  Joulescope instruments in Python.
---

(ui-source-code)=

# Source Code

The UI is open source and written in Python ({ref}`supported platforms
<supported-platforms>`). The UI consists of several layers:

| **Repo name** | **Python package name** | **Description** |
|----|----|----|
| pyjoulescope_ui | joulescope_ui | The Joulescope User Interface written in Qt6/PySide6 |
| pyjoulescope | joulescope | The Joulescope Python “driver” with pyjoulescope_driver adapter for JS110 applications. The UI only uses this package to provide JLS v1 read support. |
| joulescope_driver | pyjoulescope_driver | Native JS220 and JS110 driver with Python bindings |
| jls | pyjls | High performance file storage for Joulescope data |

The Joulescope package was designed so that you can script custom Joulescope
actions and integrate Joulescope into your applications.

See the GitHub repositories for the latest details.

- <https://github.com/jetperch/pyjoulescope_ui>
- <https://github.com/jetperch/pyjoulescope>
- <https://github.com/jetperch/joulescope_driver>
- <https://github.com/jetperch/jls>

The [pyjoulescope_examples](https://github.com/jetperch/pyjoulescope_examples)
repository on GitHub holds runnable Python examples.
{doc}`Python examples </software/pyjoulescope_examples/index>` lists them by
task.  For new scripts, use `pyjoulescope_driver` and its examples: see
{ref}`python-package`.

See the documentation:

{doc}`pyjoulescope documentation </software/pyjoulescope/index>`

The Joulescope software depends upon other software and libraries. See
CREDITS.html for
[pyjoulescope_ui](http://htmlpreview.github.io/?https://github.com/jetperch/pyjoulescope_ui/blob/master/CREDITS.html)
and
[pyjoulescope](http://htmlpreview.github.io/?https://github.com/jetperch/pyjoulescope/blob/master/CREDITS.html).
