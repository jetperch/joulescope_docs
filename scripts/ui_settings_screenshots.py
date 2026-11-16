#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Capture the Settings chapter screenshots of the Joulescope UI guide.

Launches the UI from a pyjoulescope_ui checkout with --tcp-server, drives it
with the ci/uitest harness, and saves PNGs to
source/software/joulescope_ui/media/.  The UI runs offscreen with HOME set to
a temporary directory, so it starts from a cleared configuration and never
touches your own UI configuration.  Connected Joulescopes appear in the
screenshots, which is why it is not run by the docs build.

Usage, in a Python environment where joulescope_ui is importable:

    python scripts/ui_settings_screenshots.py ../pyjoulescope_ui
"""

import argparse
import os
import sys
import tempfile
import time

MEDIA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'source', 'software', 'joulescope_ui', 'media')
WINDOW_SIZE = (1100, 700)
SETTLE = 1.0  # seconds for the UI to process a publish and repaint


def get_parser():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('ui_repo', help='The pyjoulescope_ui checkout to run.')
    return p


def _path_to(tree, predicate):
    """Find the widget path to the first node matching predicate.

    Each segment is ClassName:index among same-class siblings, which the UI
    server resolves without relying on objectName.
    """
    def walk(node, path):
        if predicate(node):
            return path
        counts = {}
        for child in node.get('children', []) or []:
            cls = child.get('class')
            idx = counts.get(cls, 0)
            counts[cls] = idx + 1
            found = walk(child, path + [f'{cls}:{idx}'])
            if found is not None:
                return found
        return None
    found = walk(tree, [])
    if found is None:
        raise RuntimeError('widget not found')
    return '/'.join(found)


def _iter(node):
    yield node
    for child in node.get('children', []) or []:
        yield from _iter(child)


def _visible(cls):
    return lambda n: n.get('class') == cls and n.get('visible')


class Shots:

    def __init__(self, session):
        self.s = session

    def tree(self):
        return self.s.qt_inspect(max_depth=60)

    def path(self, predicate):
        return _path_to(self.tree(), predicate)

    def save(self, name, path=''):
        time.sleep(SETTLE)
        png = self.s.qt_screenshot(path)
        fname = os.path.join(MEDIA, name)
        with open(fname, 'wb') as f:
            f.write(png)
        print(f'wrote {fname}')

    def call(self, path, method, *args):
        rv = self.s.qt_action('call', path=path, method=method, args=list(args))
        if not rv.get('ok', False):
            raise RuntimeError(f'{method} failed: {rv}')
        return rv.get('result')

    def tree_select(self, selector, text):
        """Select the tree item whose text starts with text."""
        self.call(selector, 'expandAll')
        self.call(selector, 'setFocus')
        self.call(selector, 'keyboardSearch', text)
        time.sleep(SETTLE)

    def tree_down(self, selector):
        """Select the next tree item, the first instance below a class."""
        self.s.qt_action('key', path=selector, key='Down')
        time.sleep(SETTLE)

    def run(self):
        s = self.s
        s.publish('registry/view/settings/active', 'view:oscilloscope')
        time.sleep(SETTLE)
        # after the view change, which restores the view's saved geometry
        if not s.resize_window_settled(*WINDOW_SIZE):
            raise RuntimeError('could not resize the main window')

        # Side Bar settings: the class defaults of the Waveform widget.
        s.qt_action('click', path='central_widget/side_bar_icons/settings')
        time.sleep(SETTLE)
        selector = self.path(_visible('SelectorWidget'))
        tabs = self.path(_visible('QTabWidget'))
        self.tree_select(selector, 'Waveform')
        self.call(tabs, 'setCurrentIndex', 0)  # Settings
        self.save('ui_settings_widget_defaults.png')

        # One row down: the Waveform widget instance in the active view.
        self.tree_down(selector)
        self.call(tabs, 'setCurrentIndex', 1)  # Colors
        self.save('ui_settings_widget_colors.png')
        self.call(tabs, 'setCurrentIndex', 0)

        # Devices: the class defaults, then a connected instrument.
        devices = s.query('registry/jsdrv/settings/device_ids') or []
        if devices:
            model = devices[0].split('-')[0]
            self.tree_select(selector, model)
            self.save('ui_settings_device_defaults.png')
            self.tree_down(selector)
            self.save('ui_settings_device_instance.png')
        else:
            print('No Joulescope connected: skipped the device screenshots')
        s.qt_action('click', path='central_widget/side_bar_icons/settings')  # close
        time.sleep(SETTLE)


def run():
    args = get_parser().parse_args()
    ui_repo = os.path.abspath(args.ui_repo)
    with tempfile.TemporaryDirectory() as home:
        os.environ['HOME'] = home  # isolate the UI configuration
        sys.path.insert(0, os.path.join(ui_repo, 'ci'))
        from uitest.harness import UiSession
        session = UiSession(offscreen=True, cwd=ui_repo, config_clear_on_exit=False)
        session.start()
        try:
            Shots(session).run()
        finally:
            session.stop()
    return 0


if __name__ == '__main__':
    sys.exit(run())
