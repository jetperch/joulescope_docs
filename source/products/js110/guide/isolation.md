(js110-electrical-isolation)=

# Electrical Isolation

The Joulescope is electrically isolated between the USB interface and the
IN/OUT sensor. Joulescope is rated to ±48V between USB ground and any of IN+,
IN-, OUT+, and OUT-. The individual component ratings far exceed this
specification. The components are:

| Part # | Mfgr | Description | Isolation working | Isolation 60s | Isolation 1 s |
|---|---|---|---|---|---|
| 760390014 | Wurth | Transformer | 400 VRMS | 2500 VAC | 3125 VAC |
| Si8661BB-B-IS1 | Silicon Labs | Digital isolator | 445 VRMS | | 4500 VRMS |
| TLP2361(TPL,E | Toshiba | Opto isolator | 500 VRMS | 3750 VRMS | |

The printed circuit board (PCB) clearance between the isolated sensor side and
the USB host side is 1 mm. The use of an aluminum enclosure effectively limits
the isolation voltage and requires that USB chassis ground surrounds the
sensor edges. If you use Joulescope in a custom application without the
standard enclosure, the four chassis ground rails (2 top & 2 bottom) can be
cut around the isolation line to give a 4 mm PCB clearance between the USB
host side and the sensor side.
