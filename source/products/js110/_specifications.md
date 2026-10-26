<!--
Include-only fragment: the JS110 specifications.  Included by
guide/specifications.md and datasheet.md.  No labels here, since
each label would be defined twice.  Table values: js110.yaml.
-->

## Absolute maximum ratings

```{datasheet} js110
:section: absolute_maximum_ratings
```

## Mechanical

```{datasheet} js110
:section: mechanical
```

## Recommended operating conditions

```{datasheet} js110
:section: recommended_operating_conditions
```

## Specification conditions

```{datasheet} js110
:section: specification_conditions
```

## Current measurement specifications

```{datasheet} js110
:section: current_ranges
```

Test current measurement bandwidth by varying the effective load impedance.
Due to load capacitance, altering the source voltage is not a valid method of
testing current bandwidth.

## Voltage measurement specifications

```{datasheet} js110
:section: voltage_ranges
```

## General specifications

```{datasheet} js110
:section: general
```

## Parasitic effects specifications

```{datasheet} js110
:section: parasitic
```

## Software-controlled fuse specifications

```{datasheet} js110
:section: fuse
```

## General purpose inputs and outputs

```{datasheet} js110
:section: gpio
```

The Joulescope uses the TI SN74LVC2T45 for both the GPIs and GPOs.  See the
[SN74LVC2T45 datasheet](http://www.ti.com/lit/gpn/sn74lvc2t45) for more
information.  Both the GPIs and GPOs are protected with the
[Vishay VEMI45AA-HNH](https://www.vishay.com/docs/81385/vemi45aa.pdf), which
is an EMI filter with ESD protection.  The VEMI45AA is a pi filter with
100 Ohm resistance and capacitance between 29 pF and 60 pF.

### GPIO supply

```{datasheet} js110
:section: gpio_supply
```
