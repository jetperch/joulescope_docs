(js220plus-introduction)=

# Introduction

The Joulescope JS220+ is a limited-edition, performance-enhanced version of
the Joulescope JS220. The JS220+ achieves ±1 nanoamp accuracy with exceptional
temperature stability, all while providing the same best-in-class high-dynamic
current range measurement as the standard JS220.

This limited document only describes the JS220+ improvements over the JS220.
The JS220+ is operationally identical to the JS220. For instructions on how to
operate your JS220+, see the
{doc}`Joulescope JS220 User's Guide </products/js220/index>` and the
{doc}`Joulescope UI User's Guide </software/joulescope_ui/index>`.

Some modern semiconductors now have sleep currents measured in nanoamps (1e-9
A) or tens of nanoamps (1e-8 A) with active currents in the tens of milliamps
(1e-2 A) and greater. These components typically require bypass capacitances
of at least 100 nF (1e-7 F). Total bypass capacitances of a power supply rail
are typically 10 µF to 400 µF (1e-5 F to 4e-4 F).

Many low-measurement instruments based on transimpedance amplifiers (feedback
ammeters) can measure down to fA (1e-15 A). However, these instruments are
typically specified for a maximum capacitance, often around 10 nF (1e-8 F),
four orders of magnitude below what is needed.

The Joulescope JS220 is a shunt ammeter designed for extremely fast
auto-ranging, perfect for the dynamic range requirements and large capacitive
loads. Shunt ammeter accuracy is bounded by input bias currents, leakage
currents, noise bandwidth, and offset temperature stability. By combining
Jetperch’s extensive experience in developing the JS110 and JS220 with newly
available components, we can now deliver the JS220+ with nanoamp accuracy
while retaining the fantastic performance of the existing Joulescope JS220.
