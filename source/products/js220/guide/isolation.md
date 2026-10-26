(js220-electrical-isolation)=

# Electrical Isolation

The Joulescope is electrically isolated between the USB interface and the
sensor terminals. Joulescope is rated to ±48V between USB ground and any of
sensor terminals: **Current +**, **Current -**, **Voltage +**, and **Voltage
-**. The ±48V is limited by the aluminum enclosure and the fit within
low-voltage safety requirements.

The individual component ratings far exceed this specification. The components
are:

| Part # | Mfgr | Description | Isolation working | Isolation 60s | Isolation 1s |
|---|---|---|---|---|---|
| 750316018 | Wurth | Transformer | 400 VRMS | 2500 VAC | 3125 VAC |
| ISO7762 | TI | Digital isolator | 445 VRMS | | 4500 VRMS |
| TLP2361(TPL,E | Toshiba | Opto isolator | 500 VRMS | 3750 VRMS | |

The printed circuit board (PCB) clearance between the isolated sensor side and
the USB host side is 1 mm. The use of an aluminum enclosure effectively limits
the isolation voltage and requires that USB chassis ground surrounds the
sensor edges.

While all the sensor terminals are isolated from USB ground, they are not
isolated from each other. The sensor is referenced to **Current +**, and the
other sensor terminals must remain within ±15V from **Current +**.
