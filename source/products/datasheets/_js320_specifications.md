<!--
Include-only fragment: the JS320 specifications.  Included by
js320/specifications.md and datasheets/js320.md.  No labels here, since
each label would be defined twice.  Table values: js320.yaml.
-->

## Absolute maximum ratings

```{datasheet} js320
:section: absolute_maximum_ratings
```

## Mechanical

### Instrument only

```{datasheet} js320
:section: mechanical_instrument
```

### Complete product kit

```{datasheet} js320
:section: mechanical_kit
```

## Recommended operating conditions

```{datasheet} js320
:section: recommended_operating_conditions
```

## Specification conditions

```{datasheet} js320
:section: specification_conditions
```

## Current measurement specifications

```{datasheet} js320
:section: current_ranges
```

The resolution depends on the noise.  Noise depends on both the current range
and signal bandwidth, which is limited by the sample frequency.  The
following table shows the typical (not guaranteed) resolution given only the
JS320 self-noise with no additional external noise pickup.

```{datasheet} js320
:section: current_resolution
```

Test current measurement bandwidth by varying the effective load impedance.
Due to load capacitance, altering the source voltage is often not a valid
method of testing current bandwidth.

The JS320 is sensitive to RF radiation, which induces real current in test
setups.  When tested with EN61326-1 and 3 V RMS/m, the JS320 measured up to
10 µA (observed, not guaranteed) of current at several frequencies.  The
exact frequency susceptibility varies with cable length and configuration.

## Voltage measurement specifications

```{datasheet} js320
:section: voltage_ranges
```

The resolution depends on the noise.  Noise depends on both the current range
and signal bandwidth, which is limited by the sample frequency.  The
following table shows the typical (not guaranteed) resolution given only the
JS320 self-noise with no additional external noise pickup.

```{datasheet} js320
:section: voltage_resolution
```

The JS320 is sensitive to RF radiation, which induces real voltages in test
setups.  When tested with EN61326-1 and 3 V RMS/m, the JS320 error increased
by 10 mV (observed, not guaranteed) at several frequencies.  The exact
frequency susceptibility varies with cable length and configuration.

## General specifications

```{datasheet} js320
:section: general
```

## Parasitic effects specifications

```{datasheet} js320
:section: parasitic
```

## Software-controlled fuse specifications

```{datasheet} js320
:section: fuse
```

## General purpose inputs and outputs

```{datasheet} js320
:section: gpio
```

The Joulescope uses the TI [TLV9034](https://www.ti.com/product/TLV9034) for
GPIs and the TI [SN74LVC2T45](https://www.ti.com/product/SN74LVC2T45) to
drive the GPOs.  Both the GPIs and GPOs are protected with the TI
[TPD4E1U06](https://www.ti.com/product/TPD4E1U06) for ESD protection.

Both gates of the TI SN74LVC2G125 drive the trigger in parallel, each through
a 100 Ω resistor for 50 Ω drive.
