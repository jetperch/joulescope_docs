(js320-meet-your-joulescope-js320)=

# Meet Your Joulescope JS320

```{include} _in_the_box.md
```

The front side of the JS320 has the connectors that connect to your system:

![JS320 front panel with the binding posts and Sensor Status indicator](media/js320_image9.jpeg)

Your JS320 measures the voltage across the Voltage + and Voltage – binding
posts. Your JS320 measures the current flowing through the Current + to the
Current – binding posts. If you have a power source and target device, connect
the positive side through the current binding posts. You can then connect the
voltage signals across either your power source or your target device. For
more connection examples, see {numref}`js320-how-to-connect-your-joulescope`.

The Sensor Status indicator is off when your JS320 is powered off or inactive.
Slow flashing red indicates that the instrument is ready, but the current flow
is not yet enabled. Solid green indicates that current measurement is enabled.
Fast flashing red indicates that the soft fuse is engaged.

The backside of Joulescope has the host USB connector, status LED, GPIO
connector, and trigger connector:

![JS320 back panel with the USB, GPIO and trigger connectors](media/js320_image10.jpeg)

Use the provided USB cable to connect the USB host computer connector to your
host computer. If your computer only has USB C ports, use the provided
adapter.

The Controller Status indicator is off when the JS320 is not connected to the
host computer, or the host computer has not yet activated the JS320 over USB.
Microsoft Windows computers activate devices immediately when connected while
macOS and Linux do not activate the device until the Joulescope software
attempts to use the device. Solid blue indicates that the JS320 is activated.
Solid green indicates that the JS320 device is running normally.

The GPIO connector provides four general-purpose inputs and two
general-purpose outputs. See {numref}`js320-gpi-gpo` for details.

The BNC Trigger connector provides either a Trigger Out or a Trigger In. This
Trigger allows the JS320 to synchronize data collection with other equipment.
