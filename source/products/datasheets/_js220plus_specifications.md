<!--
Include-only fragment: the JS220+ specifications.  Included by
js220plus/specifications.md and datasheets/js220plus.md.  No labels here, since
each label would be defined twice.  Table values: js220plus.yaml.
-->

The JS220+ specifications are the same as the JS220, except for the current
measurement, voltage measurement and parasitic effects specifications.
Resolution is given for 10 kHz measurement bandwidth (20 ksps).  The JS220+
includes a safety banana jack front panel rather than binding posts.

## Absolute maximum ratings

```{datasheet} js220plus
:section: absolute_maximum_ratings
```

## Mechanical

### Instrument only

```{datasheet} js220plus
:section: mechanical_instrument
```

### Complete product kit

```{datasheet} js220plus
:section: mechanical_kit
```

## Recommended operating conditions

```{datasheet} js220plus
:section: recommended_operating_conditions
```

## Specification conditions

```{datasheet} js220plus
:section: specification_conditions
```

## Current measurement specifications

```{datasheet} js220plus
:section: current_ranges
```

Test current measurement bandwidth by varying the effective load impedance.
Due to load capacitance, altering the source voltage is not a valid method of
testing current bandwidth.

The JS220 is sensitive to RF radiation which induces real current in test
setups.  When tested with EN61326-1 and 3 V RMS/m, the JS220 measured up to
10 µA (observed, not guaranteed) of current at several frequencies.  The
exact frequency susceptibility varies with cable length and configuration.

## Voltage measurement specifications

```{datasheet} js220plus
:section: voltage_ranges
```

The JS220 is sensitive to RF radiation which induces real voltages in test
setups.  When tested with EN61326-1 and 3 V RMS/m, the JS220 error increased
by 10 mV (observed, not guaranteed) at several frequencies.  The exact
frequency susceptibility varies with cable length and configuration.

## General specifications

```{datasheet} js220plus
:section: general
```

## Parasitic effects specifications

```{datasheet} js220plus
:section: parasitic
```

## Software-controlled fuse specifications

```{datasheet} js220plus
:section: fuse
```

## General purpose inputs and outputs

```{datasheet} js220plus
:section: gpio
```

The Joulescope uses the TI SN74LVC2T45 for both the GPIs and GPOs.  See the
[SN74LVC2T45 datasheet](http://www.ti.com/lit/gpn/sn74lvc2t45) for more
information.  Both the GPIs and GPOs are protected with the TI TPD4E1U06 for
ESD protection.
