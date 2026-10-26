(js110-typical-behavior)=

# Typical Behavior

This section contains information regarding typical Joulescope behavior.

## Step Response

Joulescope is a shunt ammeter with incredibly fast autoranging. This section
contains typical autoranging measurements.

The test setup includes a Joulescope, a custom load board, a power supply, a
computer, and some cables. A custom load board is the Joulescope target. The
load board was specifically designed for the sole purpose of creating very
fast, repeatable edges. It has a 1 MΩ resistor in parallel with a 1Ω resistor.
The board contains a momentary pushbutton and debouncer, which is the input to
the MCP1416 MOSFET driver. The MCP1416 drives the FDMC7678 MOSFET, which
enables or disables the 1Ω resistor. The entire circuit is powered by a 9V
battery and connected to the Joulescope OUT.

The power supply is a Siglent SPD3303X-E bench supply configured for 1.00V and
2.9A. The supply is connected to Joulescope IN. Any bench supply with
reasonable transient performance should do.

```{figure} media/js110_image26.jpeg
:alt: Step response test setup

The step response test setup
```

The normal Joulescope user interface software captures data while pressing the
target board’s switch to toggle the MOSFET & 1Ω resistor. A custom Python
script reads the data, processes the data, and creates plots. The python
script finds each edge and aligns them so that they can be plotted together.
The plots show rising edges in the left column and falling edges in the right
column.

The first capture “step_2A.png” is the baseline with Joulescope auto-ranging
disabled and set to a fixed 2A range. The rise time you see is due to the
Joulescope bandwidth. The actual edge is much, much faster.

```{figure} media/js110_image27.png
:alt: Step response plots with fixed 2A range

Step response with fixed 2A range
```

The second capture “step_autorange.png” is with auto-ranging. The two samples
after over-range tend to contain “garbage” data that messes up the y-axis
range, so they are omitted. These samples are captured at 2 MSPS (500 ns).
Joulescope’s stated bandwidth is 250 kHz (4 µs = 8 samples).

```{figure} media/js110_image28.png
:alt: Step response plots with autoranging

Step response with autoranging
```

The Joulescope specification states that range switching occurs within 1.2 µs
max. This specification determines how much (or in the case of Joulescope, how
little) voltage drop happens when the target changes current demands. The
Joulescope specification gives over-range settling time is 2 µs typical with 5
µs max. This specification determines how well Joulescope can measure data
through the transition. Any auto-ranging ammeter needs to be VERY fast to
limit voltage variations at the target device, and Joulescope was designed to
meet these demanding requirements.
