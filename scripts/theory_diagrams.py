# SPDX-FileCopyrightText: 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Generate the block diagrams for the leakage and ground loop theory pages.

Usage: python scripts/theory_diagrams.py

Needs matplotlib, which is not a docs build dependency.  The figures are
committed, so run this only when they change.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


MEDIA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'source', 'theory', 'media')
RED = '#d1495b'
BLUE = '#1f5fa8'
GREEN = '#2a9d5c'
GRAY = '0.45'

plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none'})


def _canvas(width, height, xlim, ylim):
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def _box(ax, x0, y0, x1, y1, text, color='k', fill='none', va='center', **kwargs):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle='round,pad=0,rounding_size=0.12',
                                edgecolor=color, facecolor=fill, linewidth=1.5))
    y = (y0 + y1) / 2 if va == 'center' else y1 - 0.12
    ax.text((x0 + x1) / 2, y, text, ha='center', va=va, color=color, **kwargs)


def _wire(ax, xs, ys, color='k', **kwargs):
    ax.plot(xs, ys, color=color, linewidth=1.5, solid_capstyle='round', **kwargs)


def _arrow(ax, xy_from, xy_to, color, text=None, text_xy=None, **kwargs):
    ax.annotate('', xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle='-|>', color=color, linewidth=2,
                                mutation_scale=14))
    if text:
        ax.text(*text_xy, text, color=color, **kwargs)


def _earth(ax, x, y):
    _wire(ax, [x, x], [y, y - 0.15])
    for i, w in enumerate([0.25, 0.16, 0.07]):
        _wire(ax, [x - w, x + w], [y - 0.15 - i * 0.08] * 2)


def fig_leakage():
    fig, ax = _canvas(7.5, 3.3, (0, 10.9), (-0.1, 4.6))
    _box(ax, 0.2, 0.6, 1.6, 2.8, 'Supply')
    _box(ax, 2.3, 3.0, 4.1, 4.0, 'Joulescope\nI+ → I−', color=BLUE)
    _box(ax, 4.9, 0.6, 7.1, 4.4, 'Target', va='top', fontweight='bold')
    _box(ax, 5.2, 1.4, 6.8, 3.2, 'MCU')
    ax.text(5.6, 3.0, 'VDD', ha='center', va='top', fontsize=8)
    ax.text(6.7, 2.3, 'IO', ha='right', va='center', fontsize=8)
    _box(ax, 8.8, 0.6, 10.7, 3.2, 'Debugger or\nlogic analyzer', va='top')
    # supply through the Joulescope to the target VDD
    _wire(ax, [1.6, 1.9, 1.9, 2.3], [2.4, 2.4, 3.5, 3.5])
    _wire(ax, [4.1, 5.6, 5.6], [3.5, 3.5, 3.2])
    # ground
    _wire(ax, [1.6, 8.8], [1.0, 1.0])
    _wire(ax, [6.0, 6.0], [1.4, 1.0])
    ax.text(8.4, 0.75, 'GND', ha='center', fontsize=8)
    # IO line
    _wire(ax, [6.8, 8.8], [2.3, 2.3])
    ax.text(9.75, 1.55, 'input resistance,\npull-ups, drivers', ha='center',
            fontsize=8, color=GRAY)
    _arrow(ax, (7.35, 2.55), (8.55, 2.55), RED)
    ax.text(7.95, 2.95, 'out of target:\nmeasured, adds', color=RED, ha='center',
            fontsize=8)
    _arrow(ax, (8.55, 2.05), (7.35, 2.05), GREEN)
    ax.text(7.95, 1.3, 'into target:\nnot measured,\nsubtracts', color=GREEN,
            ha='center', fontsize=8)
    fig.savefig(os.path.join(MEDIA, 'theory_leakage_paths.svg'))
    plt.close(fig)


def fig_ground_loop():
    fig, ax = _canvas(7.0, 4.2, (0, 10), (-0.2, 5.8))
    _box(ax, 3.5, 4.4, 6.5, 5.4, 'Computer')
    _box(ax, 0.3, 2.0, 2.7, 3.2, 'Joulescope\n(GPIO side)', color=BLUE)
    _box(ax, 7.3, 2.0, 9.7, 3.2, 'Debugger')
    _box(ax, 3.5, 0.0, 6.5, 1.2, 'Target')
    _wire(ax, [3.5, 1.5, 1.5], [4.9, 4.9, 3.2])
    _wire(ax, [6.5, 8.5, 8.5], [4.9, 4.9, 3.2])
    _wire(ax, [1.5, 1.5, 3.5], [2.0, 0.6, 0.6])
    _wire(ax, [8.5, 8.5, 6.5], [2.0, 0.6, 0.6])
    ax.text(2.4, 5.05, 'USB', ha='center', fontsize=8)
    ax.text(7.6, 5.05, 'USB', ha='center', fontsize=8)
    ax.text(2.5, 0.75, 'GPIO + GND', ha='center', fontsize=8)
    ax.text(7.5, 0.75, 'SWD + GND', ha='center', fontsize=8)
    # the loop
    xs = [2.0, 2.0, 8.0, 8.0, 2.0]
    ys = [1.6, 4.4, 4.4, 1.6, 1.6]
    ax.plot([2.0, 2.0, 3.3], [3.4, 4.4, 4.4], color=RED, linewidth=2, linestyle='--')
    ax.plot([6.7, 8.0, 8.0], [4.4, 4.4, 3.4], color=RED, linewidth=2, linestyle='--')
    ax.plot([8.0, 8.0, 6.7], [1.8, 1.2, 1.2], color=RED, linewidth=2, linestyle='--')
    ax.plot([3.3, 2.0, 2.0], [1.2, 1.2, 1.8], color=RED, linewidth=2, linestyle='--')
    ax.text(5.0, 2.95, 'Ground loop', color=RED, ha='center', fontsize=11,
            fontweight='bold')
    ax.text(5.0, 2.25, 'Its area is an antenna for\nmagnetic fields', color=RED,
            ha='center', fontsize=8)
    fig.savefig(os.path.join(MEDIA, 'theory_ground_loop.svg'))
    plt.close(fig)


def fig_return_path():
    fig, ax = _canvas(7.5, 4.0, (0, 10.4), (-1.3, 4.2))
    _box(ax, 0.2, 1.0, 1.6, 3.2, 'Bench\nsupply')
    _box(ax, 4.4, 1.0, 6.4, 3.2, 'Target')
    _box(ax, 2.2, -0.5, 3.8, 0.5, 'Joulescope', color=BLUE)
    _box(ax, 8.2, 1.0, 10.2, 2.2, 'Debugger')
    _box(ax, 8.2, 2.9, 10.2, 3.9, 'Computer')
    # supply + to target
    _wire(ax, [1.6, 4.4], [2.8, 2.8])
    # low-side return through the Joulescope
    _wire(ax, [4.4, 4.2, 4.2, 3.8], [1.4, 1.4, 0.0, 0.0])
    _wire(ax, [2.2, 1.9, 1.9, 1.6], [0.0, 0.0, 1.4, 1.4])
    # debugger ground and USB
    _wire(ax, [6.4, 8.2], [1.4, 1.4])
    ax.text(7.3, 1.55, 'SWD + GND', ha='center', fontsize=8)
    _wire(ax, [9.2, 9.2], [2.2, 2.9])
    ax.text(9.35, 2.5, 'USB', fontsize=8)
    # protective earth
    _wire(ax, [0.9, 0.9], [1.0, -0.9], color=GRAY, linestyle=':')
    _wire(ax, [10.2, 10.35, 10.35], [3.4, 3.4, -0.9], color=GRAY, linestyle=':')
    _wire(ax, [0.9, 10.35], [-0.9, -0.9], color=GRAY, linestyle=':')
    ax.text(5.6, -1.2, 'protective earth through the mains wiring', color=GRAY,
            ha='center', fontsize=8)
    _earth(ax, 0.9, -0.9)
    # currents
    _arrow(ax, (4.0, 1.25), (4.0, 0.35), BLUE)
    ax.text(3.45, 0.75, '$I_{\\mathrm{meas}}$', color=BLUE, ha='center')
    _arrow(ax, (6.6, 1.2), (8.0, 1.2), RED)
    ax.text(7.3, 0.75, '$I_{\\mathrm{bypass}}$', color=RED, ha='center')
    fig.savefig(os.path.join(MEDIA, 'theory_ground_return_path.svg'))
    plt.close(fig)


if __name__ == '__main__':
    os.makedirs(MEDIA, exist_ok=True)
    fig_leakage()
    fig_ground_loop()
    fig_return_path()
