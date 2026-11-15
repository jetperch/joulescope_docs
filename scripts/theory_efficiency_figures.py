# SPDX-FileCopyrightText: 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Generate the figures for the efficiency theory page.

Usage: python scripts/theory_efficiency_figures.py

Needs matplotlib, which is not a docs build dependency.  The figures are
committed, so run this only when they change.
"""

import os
from diagram_util import canvas, box, wire, save, THEORY_MEDIA, BLUE, GREEN, GRAY


def _sense(ax, xs, ys):
    wire(ax, xs, ys, color=GREEN, linestyle=(0, (4, 2)))


def _dot(ax, x, y, color):
    ax.plot([x], [y], 'o', color=color, markersize=5)


def _terminal(ax, x, y, text, ha, va, color):
    ax.text(x, y, text, ha=ha, va=va, fontsize=8, color=color)


def _joulescope(ax, x0, label):
    """Draw a Joulescope with I+ left, I- right, V+ and V- below."""
    box(ax, x0, 2.6, x0 + 2.2, 4.6, label, color=BLUE, fontsize=9)
    _terminal(ax, x0 + 0.08, 4.1, 'I+', 'left', 'center', BLUE)
    _terminal(ax, x0 + 2.12, 4.1, 'I−', 'right', 'center', BLUE)
    _terminal(ax, x0 + 0.7, 2.68, 'V+', 'center', 'bottom', GREEN)
    _terminal(ax, x0 + 1.5, 2.68, 'V−', 'center', 'bottom', GREEN)


def fig_wiring():
    fig, ax = canvas(8.4, 3.6, (0, 13.1), (-0.95, 4.75))
    box(ax, 0.2, 1.0, 1.6, 3.6, 'Supply')
    _joulescope(ax, 2.4, 'Input\nJoulescope')
    box(ax, 5.6, 0.6, 7.6, 3.6, 'Converter', fontweight='bold')
    _terminal(ax, 5.68, 3.1, 'VIN', 'left', 'center', 'k')
    _terminal(ax, 7.52, 3.1, 'VOUT', 'right', 'center', 'k')
    _terminal(ax, 6.6, 0.68, 'GND', 'center', 'bottom', 'k')
    _joulescope(ax, 8.6, 'Output\nJoulescope')
    box(ax, 11.6, 1.0, 12.9, 3.6, 'Load')
    _terminal(ax, 1.52, 3.2, '+', 'right', 'center', 'k')
    _terminal(ax, 1.52, 1.4, '−', 'right', 'center', 'k')
    _terminal(ax, 11.68, 3.2, '+', 'left', 'center', 'k')
    _terminal(ax, 11.68, 1.4, '−', 'left', 'center', 'k')

    # current path: supply -> input Joulescope -> converter -> output Joulescope -> load
    wire(ax, [1.6, 2.0, 2.0, 2.4], [3.2, 3.2, 4.1, 4.1], color=BLUE)
    wire(ax, [4.6, 5.1, 5.1, 5.6], [4.1, 4.1, 3.1, 3.1], color=BLUE)
    wire(ax, [7.6, 8.1, 8.1, 8.6], [3.1, 3.1, 4.1, 4.1], color=BLUE)
    wire(ax, [10.8, 11.2, 11.2, 11.6], [4.1, 4.1, 3.2, 3.2], color=BLUE)
    # common ground
    wire(ax, [1.6, 1.9, 1.9, 11.3, 11.3, 11.6], [1.4, 1.4, 0.0, 0.0, 1.4, 1.4])
    wire(ax, [6.6, 6.6], [0.6, 0.0])

    # voltage sense at the converter pins
    _sense(ax, [3.1, 3.1, 5.4, 5.4], [2.6, 2.2, 2.2, 3.1])
    _dot(ax, 5.4, 3.1, GREEN)
    _sense(ax, [9.3, 9.3, 7.8, 7.8], [2.6, 2.2, 2.2, 3.1])
    _dot(ax, 7.8, 3.1, GREEN)
    _sense(ax, [3.9, 3.9, 10.1, 10.1], [2.6, 0.3, 0.3, 2.6])
    _sense(ax, [6.6, 6.6], [0.3, 0.6])
    _dot(ax, 6.6, 0.3, GREEN)

    ax.text(6.6, 4.25, 'η = P$_{\\mathrm{OUT}}$ / P$_{\\mathrm{IN}}$', ha='center', fontsize=10)
    # legend
    wire(ax, [3.3, 4.0], [-0.55, -0.55], color=BLUE)
    ax.text(4.15, -0.55, 'current path', va='center', fontsize=8, color=BLUE)
    _sense(ax, [6.2, 6.9], [-0.55, -0.55])
    ax.text(7.05, -0.55, 'voltage sensed at the converter pins', va='center', fontsize=8,
            color=GREEN)
    ax.text(6.6, -0.88, 'Each Joulescope burden voltage stays outside the measured power',
            ha='center', va='center', fontsize=8, color=GRAY)
    save(fig, os.path.join(THEORY_MEDIA, 'theory_efficiency_wiring.svg'))


if __name__ == '__main__':
    fig_wiring()
