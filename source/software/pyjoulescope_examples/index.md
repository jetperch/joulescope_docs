---
description: >-
  Runnable Python scripts for Joulescope instruments in the
  pyjoulescope_examples GitHub repository, listed by task.  Start with the
  pyjoulescope_driver examples.
---

(examples)=

# Python examples

The [pyjoulescope_examples](https://github.com/jetperch/pyjoulescope_examples)
repository on GitHub holds runnable Python scripts for Joulescope
instruments.  Its tests run each script with and without connected
instruments.  This page lists the scripts by task and links each one on
GitHub, where the code lives.  It describes pyjoulescope_examples 1.0.2.

The scripts are grouped by the Python package they use, in
`examples/<package>/`.  Use the
{ref}`pyjoulescope_driver examples <examples-pyjoulescope-driver>` unless you
maintain code written for the `joulescope` package.  See
{ref}`python-package`.


## Run the examples

```bash
git clone https://github.com/jetperch/pyjoulescope_examples.git
cd pyjoulescope_examples
python -m pip install -U -r requirements.txt
python examples/pyjoulescope_driver/statistics.py
```

The examples need Python 3.12 or newer.  Scripts that take arguments describe
them with `--help`.  With several Joulescopes connected, the
pyjoulescope_driver examples select one with `--device`, such as
`--device js320`, `--device 000415` or `--device js220-000415`.

Some tasks need no script.  The `pyjoulescope_driver` package includes
command-line tools, such as `python -m pyjoulescope_driver statistics` and
`python -m pyjoulescope_driver record`.  See the Joulescope Driver
{doc}`Python API </software/joulescope_driver/py_api>`.


(examples-pyjoulescope-driver)=

## pyjoulescope_driver examples

These scripts use `pyjoulescope_driver`, the recommended package.  They work
with the JS320, JS220 and JS110 unless the Models column says otherwise.
The instrument settings they publish are listed in the
{doc}`JS320 topics </software/joulescope_driver/js320_topics>` and
{doc}`JS220 topics </software/joulescope_driver/js220_topics>`.

| Task | Script | Models |
|---|---|---|
| List instruments as they connect and disconnect | [hotplug.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/hotplug.py) | All |
| Display statistics: average, minimum and maximum current, voltage and power, plus charge and energy | [statistics.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/statistics.py) | All |
| Measure average current, power and energy over one interval, such as sleep current | [measure.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/measure.py) | All |
| Read full-rate samples into NumPy arrays, for captures that fit in memory | [read.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/read.py) | All |
| Record full-rate samples to a JLS file | [record.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/record.py) | All |
| Log downsampled data to CSV for long captures, such as battery life | [downsample_logging.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/downsample_logging.py) | All |
| Measure charge and energy for each event marked by a general-purpose input | [gpi_region.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/gpi_region.py) | JS320, JS220 |
| Detect current events while streaming | [detector.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/detector.py) | JS320, JS220 |
| Drive the BNC trigger output from host-side detection | [trigger_out.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/trigger_out.py) | JS320, JS220 |
| Turn power to the target device on or off | [dut_power.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/dut_power.py) | All |
| Configure the fuse | [fuse.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/fuse.py) | JS320, JS220 |
| Measure time synchronization between several instruments | [timesync.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjoulescope_driver/timesync.py) | All |


## pyjls examples

These scripts read JLS files, such as the recordings made by the Joulescope
UI or `record.py`.  See the {doc}`JLS File Format </software/jls/index>`.

| Task | Script |
|---|---|
| Plot a JLS file to an image | [jls_plot.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjls/jls_plot.py) |
| Plot the energy in a JLS file | [jls_energy_plot.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjls/jls_energy_plot.py) |
| Export downsampled points from a JLS file to CSV | [jls_export_points.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/pyjls/jls_export_points.py) |


## joulescope examples

These scripts use the original `joulescope` package, documented in
{doc}`pyjoulescope </software/pyjoulescope/index>`.  Use them to maintain
existing code.  For new code, use the
{ref}`pyjoulescope_driver examples <examples-pyjoulescope-driver>`.

| Task | Script |
|---|---|
| List instruments, or show one instrument's information | [scan.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/scan.py) |
| Print the present sample | [capture_simple.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/capture_simple.py) |
| Display statistics | [statistics.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/statistics.py), [statistics_logger.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/statistics_logger.py) |
| Read samples with a blocking call | [read_by_method.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/read_by_method.py) |
| Read samples with a callback | [read_by_callback.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/read_by_callback.py) |
| Record to a JLS file | [capture_jls.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/capture_jls.py), [capture_all.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/capture_all.py) for every instrument |
| Print charge and energy | [energy_printer.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/energy_printer.py), [accumulators.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/accumulators.py) |
| Discharge a battery to measure its charge and energy | [battery_discharge.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/battery_discharge.py) |
| Disconnect the target when the voltage drops below a threshold | [low_voltage_shutoff.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/low_voltage_shutoff.py) |
| Record full-rate samples to JLS when statistics meet a trigger condition | [statistics_with_trigger_to_jls.py](https://github.com/jetperch/pyjoulescope_examples/blob/main/examples/joulescope/statistics_with_trigger_to_jls.py) |

`examples/legacy/` keeps older scripts, including JS110-only and JLS v1
examples, for reference.  The `bin/` directory still runs each script by its
original name, so older links keep working.
