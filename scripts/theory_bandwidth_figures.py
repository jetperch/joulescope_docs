# SPDX-FileCopyrightText: 2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

"""Generate the figures for source/theory/bandwidth.md.

Usage: python scripts/theory_bandwidth_figures.py

Needs numpy, scipy and matplotlib, which are not docs build dependencies.
The figures are committed, so run this only when they change.
"""

import os
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


MEDIA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'source', 'theory', 'media')
FS = 1_000_000          # instrument sample rate
OVERSAMPLE = 16         # simulation grid relative to FS
I_BASE = 1e-3           # baseline current, A
I_PULSE = 30e-3         # pulse current, A
T_PULSE = 10e-6         # pulse duration, s
T_START = 150e-6        # pulse start time, s
T_END = 400e-6          # plot duration, s
DECIMATE = 20           # 1 Msps / 20 = 50 ksps
COLORS = ['#1f5fa8', '#d1495b', '#2a9d5c']

plt.rcParams.update({
    'font.size': 10,
    'svg.fonttype': 'none',
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def load_current(t):
    x = np.full(len(t), I_BASE)
    x[(t >= T_START) & (t < T_START + T_PULSE)] = I_PULSE
    return x


def instrument(x):
    """Approximate the analog front end: 2nd order Bessel, then sample at FS."""
    fs = FS * OVERSAMPLE
    b, a = signal.bessel(2, 2 * np.pi * 377e3, analog=True, norm='mag')
    bz, az = signal.bilinear(b, a, fs)
    zi = signal.lfilter_zi(bz, az) * x[0]
    return signal.lfilter(bz, az, x, zi=zi)[0][::OVERSAMPLE]


def sinc_downsample(x, order, phase):
    """sincN downsample by DECIMATE, keeping outputs at the given phase."""
    h = np.ones(DECIMATE)
    k = h
    for _ in range(order - 1):
        k = np.convolve(k, h)
    k = k / k.sum()
    pad = np.full(len(k) - 1, x[0])
    y = np.convolve(np.concatenate([pad, x]), k, mode='valid')
    idx = np.arange(phase, len(x), DECIMATE)
    return idx, y[idx]


def fig_pulse():
    t = np.arange(int(T_END * FS * OVERSAMPLE)) / (FS * OVERSAMPLE)
    y = instrument(load_current(t))
    t1 = np.arange(len(y)) / FS
    phase = 7
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5.2), sharex=True,
                                   gridspec_kw={'height_ratios': [3, 2]})
    ax1.plot(t1 * 1e6, y * 1e3, color=COLORS[0], label='1 Msps (full bandwidth)')
    q_base = I_BASE / FS
    q = [(t1, np.cumsum(y / FS - q_base))]
    for color, order in zip(COLORS[1:], [1, 3]):
        idx, z = sinc_downsample(y, order, phase)
        ax1.step(t1[idx] * 1e6, z * 1e3, where='post', color=color,
                 marker='o', markersize=3, label=f'50 ksps, sinc{order}')
        q.append((t1[idx], np.cumsum((z - I_BASE) * DECIMATE / FS)))
        print(f'sinc{order} peak = {z.max() * 1e3:.1f} mA')
    print(f'1 Msps peak = {y.max() * 1e3:.1f} mA')
    ax1.set_ylabel('Current (mA)')
    ax1.set_ylim(0, 35)
    ax1.legend(frameon=False, loc='upper right')
    ax1.set_title('Same 10 µs, 30 mA pulse at two sample rates')
    labels = ['1 Msps', '50 ksps, sinc1', '50 ksps, sinc3']
    for color, (tq, qi), label in zip(COLORS, q, labels):
        ax2.step(tq * 1e6, qi * 1e9, where='post', color=color, label=label)
        print(f'{label} charge = {qi[-1] * 1e9:.1f} nC')
    ax2.set_ylabel('Pulse charge (nC)')
    ax2.set_xlabel('Time (µs)')
    ax2.set_xlim(100, 300)
    ax2.legend(frameon=False, loc='lower right')
    fig.tight_layout()
    fig.savefig(os.path.join(MEDIA, 'theory_bandwidth_pulse.svg'))
    plt.close(fig)


def fig_frequency():
    f = np.logspace(2, np.log10(500e3), 2000)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    b, a = signal.bessel(2, 2 * np.pi * 377e3, analog=True, norm='mag')
    _, h = signal.freqs(b, a, 2 * np.pi * f)
    ax.semilogx(f, 20 * np.log10(np.abs(h)), color=COLORS[0], label='1 Msps (full bandwidth)')
    for color, order in zip(COLORS[1:], [1, 3]):
        hs = np.abs(np.sinc(f * DECIMATE / FS) / np.sinc(f / FS)) ** order
        with np.errstate(divide='ignore'):
            ax.semilogx(f, 20 * np.log10(hs), color=color, label=f'50 ksps, sinc{order}')
    ax.axhline(-3, color='0.5', linewidth=0.8, linestyle='--')
    ax.set_ylim(-60, 3)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Gain (dB)')
    ax.legend(frameon=False, loc='lower left')
    ax.set_title('Frequency response: the −3 dB line marks each bandwidth')
    fig.tight_layout()
    fig.savefig(os.path.join(MEDIA, 'theory_bandwidth_frequency.svg'))
    plt.close(fig)


def _resistor(ax, x0, x1, y):
    n = 6
    xs = np.linspace(x0, x1, 2 * n + 1)
    ys = [y] + [y + (0.12 if i % 2 else -0.12) for i in range(1, 2 * n)] + [y]
    ax.plot(xs, ys, color='k', linewidth=1.5)


def fig_system():
    fig = plt.figure(figsize=(7, 5.6))
    ax = fig.add_axes([0.02, 0.62, 0.96, 0.36])
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.3, 2.9)
    ax.axis('off')
    k = dict(color='k', linewidth=1.5)
    # supply
    ax.add_patch(plt.Circle((0.8, 1.1), 0.4, fill=False, **k))
    ax.text(0.8, 1.1, '+\n−', ha='center', va='center', fontsize=9, linespacing=0.9)
    ax.text(0.8, 0.45, 'Supply', ha='center', va='top')
    ax.plot([0.8, 0.8, 2.3], [1.5, 2.0, 2.0], **k)
    ax.plot([0.8, 0.8], [0.7, 0.0], **k)
    # Joulescope shunt
    _resistor(ax, 2.3, 3.9, 2.0)
    ax.add_patch(plt.Rectangle((2.0, 1.55), 2.2, 0.95, fill=False, linestyle='--',
                               edgecolor=COLORS[0]))
    ax.text(3.1, 2.6, 'Joulescope shunt R', ha='center', color=COLORS[0])
    ax.text(3.1, 1.65, 'measures $I_{\\mathrm{meas}}$', ha='center', color=COLORS[0])
    ax.plot([3.9, 8.6, 8.6], [2.0, 2.0, 1.5], **k)
    ax.plot([0.8, 8.6, 8.6], [0.0, 0.0, 0.7], **k)
    # target capacitor
    ax.plot([6.0, 6.0], [2.0, 1.15], **k)
    ax.plot([5.6, 6.4], [1.15, 1.15], **k)
    ax.plot([5.6, 6.4], [0.95, 0.95], **k)
    ax.plot([6.0, 6.0], [0.95, 0.0], **k)
    ax.text(6.55, 1.05, 'C', va='center')
    # load current source
    ax.add_patch(plt.Circle((8.6, 1.1), 0.4, fill=False, **k))
    ax.annotate('', xy=(8.6, 0.85), xytext=(8.6, 1.35),
                arrowprops=dict(arrowstyle='->', color='k'))
    ax.text(9.1, 1.1, '$I_{\\mathrm{load}}$', va='center')
    ax.add_patch(plt.Rectangle((5.3, -0.2), 4.5, 2.6, fill=False, linestyle='--',
                               edgecolor=COLORS[2]))
    ax.text(7.55, 2.6, 'Target device', ha='center', color=COLORS[2])

    ax2 = fig.add_axes([0.11, 0.09, 0.85, 0.46])
    fs = FS * OVERSAMPLE
    t = np.arange(int(T_END * fs)) / fs
    x = load_current(t)
    ax2.plot(t * 1e6, x * 1e3, color='0.4', linestyle='--', label='$I_{\\mathrm{load}}$')
    for color, tau in zip(COLORS, [1e-6, 10e-6, 50e-6]):
        a = np.exp(-1 / (fs * tau))
        y = signal.lfilter([1 - a], [1, -a], x, zi=[I_BASE * a])[0]
        f3 = 1 / (2 * np.pi * tau)
        ax2.plot(t * 1e6, y * 1e3, color=color,
                 label=f'$I_{{\\mathrm{{meas}}}}$, RC = {tau * 1e6:g} µs ({f3 / 1e3:.1f} kHz)')
    ax2.set_xlim(100, 350)
    ax2.set_ylim(0, 35)
    ax2.set_xlabel('Time (µs)')
    ax2.set_ylabel('Current (mA)')
    ax2.legend(frameon=False, loc='upper right')
    fig.savefig(os.path.join(MEDIA, 'theory_bandwidth_system.svg'))
    plt.close(fig)


if __name__ == '__main__':
    os.makedirs(MEDIA, exist_ok=True)
    fig_pulse()
    fig_frequency()
    fig_system()
