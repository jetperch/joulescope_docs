# SPDX-FileCopyrightText: 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Shared matplotlib helpers for the block diagrams in scripts/.

Needs matplotlib, which is not a docs build dependency.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEORY_MEDIA = os.path.join(ROOT, 'source', 'theory', 'media')
RED = '#d1495b'
BLUE = '#1f5fa8'
GREEN = '#2a9d5c'
GRAY = '0.45'

plt.rcParams.update({
    'font.size': 10,
    'svg.fonttype': 'none',
    'svg.hashsalt': 'joulescope_docs',  # stable element ids, so unchanged figures stay unchanged
})


def canvas(width, height, xlim, ylim):
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax


def box(ax, x0, y0, x1, y1, text, color='k', fill='none', va='center', **kwargs):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle='round,pad=0,rounding_size=0.12',
                                edgecolor=color, facecolor=fill, linewidth=1.5))
    y = (y0 + y1) / 2 if va == 'center' else y1 - 0.12
    ax.text((x0 + x1) / 2, y, text, ha='center', va=va, color=color, **kwargs)


def wire(ax, xs, ys, color='k', **kwargs):
    ax.plot(xs, ys, color=color, linewidth=1.5, solid_capstyle='round', **kwargs)


def arrow(ax, xy_from, xy_to, color, text=None, text_xy=None, **kwargs):
    ax.annotate('', xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle='-|>', color=color, linewidth=2,
                                mutation_scale=14))
    if text:
        ax.text(*text_xy, text, color=color, **kwargs)


def earth(ax, x, y):
    wire(ax, [x, x], [y, y - 0.15])
    for i, w in enumerate([0.25, 0.16, 0.07]):
        wire(ax, [x - w, x + w], [y - 0.15 - i * 0.08] * 2)


def save(fig, path):
    """Save an SVG without a timestamp, so regenerating only changes what changed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, metadata={'Date': None})
    plt.close(fig)
