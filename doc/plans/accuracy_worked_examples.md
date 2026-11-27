# Plan: worked accuracy examples

Status: proposed 2026-11-27, not started.

## Problem

Customers and LLM agents ask "how accurate is a 1 µA measurement on the
JS320?" or "can I measure 5 mAh per day to 1 %?".  The datasheets give the
inputs, but no page shows how to combine them, and agents get the arithmetic
wrong: they use the wrong range, add the offset as a percentage, or let
averaging shrink the offset.

The inputs exist, per range, in `<model>_datasheet.yaml`:

* `current_ranges`: accuracy as `gain_pct` plus a fixed `offset` per range
  (JS320: 0.25 % on every range; offset 500 µA at 10 A down to 10 nA at
  18 µA, ±1 nA with trim calibration).
* The noise table: RMS noise per range at 1 Msps, 10 ksps and 10 sps.
* `voltage_ranges`: 0.1 % + 500 µV (15 V) or 200 µV (2 V).

Autoranging is what makes this hard.  A sleep/active load spends most of
its time in a low range and most of its charge in a high range, so the
error of an average depends on how the time and charge divide across the
ranges, and on the transitions between them.

## Recommendations

### 1. A theory page, "Measurement accuracy" (`theory/accuracy.md`)

Explain the model once for all instruments, with values from the YAML:

* The error of one range is `gain_pct × |reading| + offset`.  The offset is
  systematic: averaging reduces noise, not offset.
* Noise falls with averaging: use the noise table at the bandwidth of the
  measurement, scaled by `1/sqrt(N)` for longer averages, and state that
  the spec is RMS.
* Total uncertainty of a single-range DC measurement is the gain and offset
  error plus a noise term.
* For an autoranged average over a window T, split by range i, with time
  t_i in the range and charge Q_i measured in it:

  error(Q) ≤ gain_pct × |Q| + Σ_i offset_i × t_i

  The gain term covers the whole charge.  The offset term weights each
  range's offset by its time, which is why a load that sleeps in the 18 µA
  range for 99 % of the time has a small offset contribution even though it
  peaks at 100 mA.
* Transitions: state what Enwavify™ and the predicted range do (link
  `js320-theory-of-operation` autoranging sections) and whether transition
  error is inside the published spec.  Needs a decision from Matt, below.

### 2. Worked examples generated from the YAML

Hand-typed numbers would break the authoring rule that specification values
live only in the YAML.  Add a small `datasheet` directive mode, or a script
in `scripts/` that writes an include-only fragment, which computes:

1. A DC current in one range: 1 µA, 100 µA and 100 mA on the JS320, with
   and without trim calibration.
2. A duty-cycled load: 5 µA sleep for 990 ms and 20 mA active for 10 ms,
   averaged over 1 s, 1 h and 1 day: average current, charge, and the
   error bound from the formula above.
3. Energy: the same load at 3.0 V, combining current and voltage errors.

Generate the table per active model (JS320 first), so a datasheet change
updates the examples.

### 3. Measured range occupancy (later)

The instrument already reports the current range with each sample (the
`s/i/range/!data` stream in the driver, the current range signal in the UI
and its JLS recordings).  A
script in pyjoulescope_examples, or a pyjls helper, can compute t_i and Q_i
from a real capture and print its error bound.  This turns the formula into
a number for the customer's own waveform, which is what agents need to
answer "how accurate was my measurement?".

### 4. Validate on hardware

Check the worked examples against a reference: a calibrated source and
DMM, or a known resistor load, on a HIL station with a JS320.  Record the
results in the plan, and correct the page if the bound is not conservative.

## Decisions needed (Matt)

* Are autorange transition errors included in the published accuracy, or a
  separate term?  If separate, what is a defensible bound per transition?
* Are the gain errors of different ranges independent, or correlated by
  calibration?  The formula above assumes the worst case, which adds them.
* Which conditions apply: the specification conditions table (temperature,
  warm-up) and the calibration interval.  Say so on the page.
* JS220 and JS110: worth examples, or JS320 only with a note?

## Stages

1. `theory/accuracy.md` with the model and the single-range example.
   Glossary "Accuracy" links to it.
2. The YAML-driven example tables and the duty-cycled and energy examples.
3. The range-occupancy script, in pyjoulescope_examples.
4. HIL validation.
