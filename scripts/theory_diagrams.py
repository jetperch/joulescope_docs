# SPDX-FileCopyrightText: 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Generate the block diagrams for the leakage and ground loop theory pages.

Usage: python scripts/theory_diagrams.py

Needs matplotlib, which is not a docs build dependency.  The figures are
committed, so run this only when they change.
"""

import os
from diagram_util import canvas, box, wire, arrow, earth, save, THEORY_MEDIA as MEDIA, \
    RED, BLUE, GREEN, GRAY


def fig_leakage():
    fig, ax = canvas(7.5, 3.3, (0, 10.9), (-0.1, 4.6))
    box(ax, 0.2, 0.6, 1.6, 2.8, 'Supply')
    box(ax, 2.3, 3.0, 4.1, 4.0, 'Joulescope\nI+ → I−', color=BLUE)
    box(ax, 4.9, 0.6, 7.1, 4.4, 'Target', va='top', fontweight='bold')
    box(ax, 5.2, 1.4, 6.8, 3.2, 'MCU')
    ax.text(5.6, 3.0, 'VDD', ha='center', va='top', fontsize=8)
    ax.text(6.7, 2.3, 'IO', ha='right', va='center', fontsize=8)
    box(ax, 8.8, 0.6, 10.7, 3.2, 'Debugger or\nlogic analyzer', va='top')
    # supply through the Joulescope to the target VDD
    wire(ax, [1.6, 1.9, 1.9, 2.3], [2.4, 2.4, 3.5, 3.5])
    wire(ax, [4.1, 5.6, 5.6], [3.5, 3.5, 3.2])
    # ground
    wire(ax, [1.6, 8.8], [1.0, 1.0])
    wire(ax, [6.0, 6.0], [1.4, 1.0])
    ax.text(8.4, 0.75, 'GND', ha='center', fontsize=8)
    # IO line
    wire(ax, [6.8, 8.8], [2.3, 2.3])
    ax.text(9.75, 1.55, 'input resistance,\npull-ups, drivers', ha='center',
            fontsize=8, color=GRAY)
    arrow(ax, (7.35, 2.55), (8.55, 2.55), RED)
    ax.text(7.95, 2.95, 'out of target:\nmeasured, adds', color=RED, ha='center',
            fontsize=8)
    arrow(ax, (8.55, 2.05), (7.35, 2.05), GREEN)
    ax.text(7.95, 1.3, 'into target:\nnot measured,\nsubtracts', color=GREEN,
            ha='center', fontsize=8)
    save(fig, os.path.join(MEDIA, 'theory_leakage_paths.svg'))


def fig_ground_loop():
    fig, ax = canvas(7.0, 4.2, (0, 10), (-0.2, 5.8))
    box(ax, 3.5, 4.4, 6.5, 5.4, 'Computer')
    box(ax, 0.3, 2.0, 2.7, 3.2, 'Joulescope\n(GPIO side)', color=BLUE)
    box(ax, 7.3, 2.0, 9.7, 3.2, 'Debugger')
    box(ax, 3.5, 0.0, 6.5, 1.2, 'Target')
    wire(ax, [3.5, 1.5, 1.5], [4.9, 4.9, 3.2])
    wire(ax, [6.5, 8.5, 8.5], [4.9, 4.9, 3.2])
    wire(ax, [1.5, 1.5, 3.5], [2.0, 0.6, 0.6])
    wire(ax, [8.5, 8.5, 6.5], [2.0, 0.6, 0.6])
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
    save(fig, os.path.join(MEDIA, 'theory_ground_loop.svg'))


def fig_return_path():
    fig, ax = canvas(7.5, 4.0, (0, 10.4), (-1.3, 4.2))
    box(ax, 0.2, 1.0, 1.6, 3.2, 'Bench\nsupply')
    box(ax, 4.4, 1.0, 6.4, 3.2, 'Target')
    box(ax, 2.2, -0.5, 3.8, 0.5, 'Joulescope', color=BLUE)
    box(ax, 8.2, 1.0, 10.2, 2.2, 'Debugger')
    box(ax, 8.2, 2.9, 10.2, 3.9, 'Computer')
    # supply + to target
    wire(ax, [1.6, 4.4], [2.8, 2.8])
    # low-side return through the Joulescope
    wire(ax, [4.4, 4.2, 4.2, 3.8], [1.4, 1.4, 0.0, 0.0])
    wire(ax, [2.2, 1.9, 1.9, 1.6], [0.0, 0.0, 1.4, 1.4])
    # debugger ground and USB
    wire(ax, [6.4, 8.2], [1.4, 1.4])
    ax.text(7.3, 1.55, 'SWD + GND', ha='center', fontsize=8)
    wire(ax, [9.2, 9.2], [2.2, 2.9])
    ax.text(9.35, 2.5, 'USB', fontsize=8)
    # protective earth
    wire(ax, [0.9, 0.9], [1.0, -0.9], color=GRAY, linestyle=':')
    wire(ax, [10.2, 10.35, 10.35], [3.4, 3.4, -0.9], color=GRAY, linestyle=':')
    wire(ax, [0.9, 10.35], [-0.9, -0.9], color=GRAY, linestyle=':')
    ax.text(5.6, -1.2, 'protective earth through the mains wiring', color=GRAY,
            ha='center', fontsize=8)
    earth(ax, 0.9, -0.9)
    # currents
    arrow(ax, (4.0, 1.25), (4.0, 0.35), BLUE)
    ax.text(3.45, 0.75, '$I_{\\mathrm{meas}}$', color=BLUE, ha='center')
    arrow(ax, (6.6, 1.2), (8.0, 1.2), RED)
    ax.text(7.3, 0.75, '$I_{\\mathrm{bypass}}$', color=RED, ha='center')
    save(fig, os.path.join(MEDIA, 'theory_ground_return_path.svg'))


if __name__ == '__main__':
    os.makedirs(MEDIA, exist_ok=True)
    fig_leakage()
    fig_ground_loop()
    fig_return_path()
