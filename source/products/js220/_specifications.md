<!--
Include-only fragment: the JS220 specifications.  Included by
guide/specifications.md and datasheet.md.  No labels here, since
each label would be defined twice.  Table values: js220.yaml.
The "label:" comments mark where js220/specifications.md adds labels.
-->

## Absolute maximum ratings

```{datasheet} js220
:section: absolute_maximum_ratings
```

## Mechanical

### Instrument only

```{datasheet} js220
:section: mechanical_instrument
```

### Complete product kit

```{datasheet} js220
:section: mechanical_kit
```

## Recommended operating conditions

```{datasheet} js220
:section: recommended_operating_conditions
```

## Specification conditions

```{datasheet} js220
:section: specification_conditions
```

<!-- label: current -->

## Current measurement specifications

```{datasheet} js220
:section: current_ranges
```

Test current measurement bandwidth by varying the effective load impedance.
Due to load capacitance, altering the source voltage is not a valid method of
testing current bandwidth.

The JS220 is sensitive to RF radiation which induces real current in test
setups.  When tested with EN61326-1 and 3 V RMS/m, the JS220 measured up to
10 µA (observed, not guaranteed) of current at several frequencies.  The
exact frequency susceptibility varies with cable length and configuration.

<!-- label: voltage -->

## Voltage measurement specifications

```{datasheet} js220
:section: voltage_ranges
```

The JS220 is sensitive to RF radiation which induces real voltages in test
setups.  When tested with EN61326-1 and 3 V RMS/m, the JS220 error increased
by 10 mV (observed, not guaranteed) at several frequencies.  The exact
frequency susceptibility varies with cable length and configuration.

## General specifications

```{datasheet} js220
:section: general
```

<!-- label: parasitic -->

## Parasitic effects specifications

```{datasheet} js220
:section: parasitic
```

## Software-controlled fuse specifications

```{datasheet} js220
:section: fuse
```

## General purpose inputs and outputs

```{datasheet} js220
:section: gpio
```

The Joulescope uses the TI SN74LVC2T45 for both the GPIs and GPOs.  See the
[SN74LVC2T45 datasheet](http://www.ti.com/lit/gpn/sn74lvc2t45) for more
information.  Both the GPIs and GPOs are protected with the TI TPD4E1U06 for
ESD protection.
