(js220-host-software)=

# Host software

The Joulescope host software runs on a host computer and communicates with the
Joulescope JS220 instrument over USB 2.0 high-speed.

## Joulescope User Interface

The Joulescope User Interface (UI) is the quickest and easiest way to get
started with your Joulescope. The UI works with Microsoft® Windows®, Apple®
macOS®, and Linux®.  See the {ref}`supported platforms <supported-platforms>`.

For more information on the Joulescope UI, see the
{doc}`Joulescope UI User's Guide </software/joulescope_ui/index>`.

## Scripts and automation

Want to go beyond the Joulescope UI? Automate a test? Integrate with a larger
test setup? The Joulescope host software is ready to support you. The
Joulescope software contains several layers that you can use to integrate. The
easiest way to get started is with Python. You can use the original
**joulescope** API or the newer, more powerful **joulescope_driver**. Both
have python bindings. However, the **joulescope_driver** is a native C
application, so you can integrate it with any programming language that can
call into a dynamic library.

For more detail, visit the GitHub repositories for each project:

| Repo name | Python package name | Description |
|---|---|---|
| [pyjoulescope_ui](https://github.com/jetperch/pyjoulescope_ui) | joulescope_ui | The Joulescope User Interface written in QT/PySide6 |
| [pyjoulescope](https://github.com/jetperch/pyjoulescope) | joulescope | The Joulescope Python "driver" with pyjoulescope_driver adapter for JS110 applications.  The UI only uses this package to provide JLS v1 read support. |
| [joulescope_driver](https://github.com/jetperch/joulescope_driver) | pyjoulescope_driver | Native JS220 and JS110 user-space driver with Python and Node.js bindings |
| [jls](https://github.com/jetperch/jls) | pyjls | High performance file storage for Joulescope data |

You can find examples of how to use Joulescope in your Python application at:

<https://github.com/jetperch/pyjoulescope_examples>

<https://github.com/jetperch/joulescope_driver/tree/main/pyjoulescope_driver/entry_points>

Also see the documentation for {doc}`pyjoulescope </software/pyjoulescope/index>` and
the {doc}`Joulescope Driver </software/joulescope_driver/index>`.

The Joulescope software depends upon other software and libraries. See
CREDITS.html for
[pyjoulescope_ui](http://htmlpreview.github.io/?https://github.com/jetperch/pyjoulescope_ui/blob/master/CREDITS.html)
and
[pyjoulescope](http://htmlpreview.github.io/?https://github.com/jetperch/pyjoulescope/blob/master/CREDITS.html).
