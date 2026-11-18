(ui-troubleshooting)=

# Troubleshooting

## Reporting issues

While we work diligently to ensure that the Joulescope UI is stable, sometimes
the unexpected happens. If the Joulescope UI fails to launch or crashes, it
may prompt you to report the issue. Please report issues and include your
email in the report so that we can work with you to solve the issue.

If the Joulescope UI crashes but does not prompt you to report the issue,
please manually report the issue when you next start the Joulescope UI. Select
**Help** → **Report Issue**. Please include your email so that we can work
with you to solve the issue.

(ui-troubleshooting-windows-usb-driver)=

## Joulescope not detected on Windows

The Joulescope is connected and its rear status LED is on, but the Joulescope
UI does not list it.  The Device Control widget shows no instrument, and the
device controls on the left side of the UI are grayed out.  Device Manager may
still show the device as working properly.

Windows uses its built-in WinUSB driver for every Joulescope.  If Windows
binds a different driver, or keeps a damaged device entry, often after
repeated USB disconnects, the Joulescope software cannot find the instrument.

Try these steps in order, and stop when the Joulescope works:

1. Reset the Joulescope UI configuration and the USB connection:
   1. In the Joulescope UI, select **File** → **Config** → **Clear and
      exit**.  See {ref}`ui-settings-config`.
   2. Unplug the Joulescope.  Connect it directly to a USB port on the
      computer, not through a hub, dock or monitor.  Use a different USB
      cable if you have one.
   3. Start the Joulescope UI.  If the Joulescope still does not appear,
      close the Joulescope UI and continue with the next step.
2. Remove and reinstall the Windows driver, either with Device Manager or
   with the PowerShell script below.  With Device Manager:
   1. With the Joulescope UI closed and the Joulescope plugged in, open
      **Device Manager**.
   2. Select **View** → **Show hidden devices**.
   3. Find every entry for the Joulescope, including grayed-out entries.
      They are usually under **Universal Serial Bus devices**.  Right-click
      each entry and select **Uninstall device**.  If Windows offers
      **Attempt to remove the driver for this device**, select it.
   4. Unplug the Joulescope, wait 10 seconds and plug it back in.
   5. Start the Joulescope UI.
3. Try the Joulescope on another computer.  If it works there, the problem
   is with the first computer.  On company computers, ask your IT department
   whether a USB device control or endpoint security policy blocks the
   Joulescope.

If the Joulescope still does not appear, report the issue with
**Help** → **Report Issue**, and include the output of the PowerShell
script below.

### PowerShell script

The {download}`joulescope_usb.ps1 <joulescope_usb.ps1>` script lists and
reinstalls the Joulescope device entries.  It finds the JS110, JS220 and
JS320 by their USB vendor and product IDs, so it also finds a Joulescope
that Windows bound to the wrong driver under a different name.

1. Close the Joulescope UI.
2. Download the script and open PowerShell in the download folder.
3. To list the Joulescope device entries, type:

   ```
   powershell -ExecutionPolicy Bypass -File .\joulescope_usb.ps1
   ```

   Each connected Joulescope should show **Present** True, **Status** OK and
   **Service** WinUSB.  The script warns about a connected Joulescope that
   uses another driver.
4. To remove all Joulescope device entries and reinstall the driver, type:

   ```
   powershell -ExecutionPolicy Bypass -File .\joulescope_usb.ps1 -Reinstall
   ```

   Windows asks for permission to make changes.  Select **Yes**.  You need
   administrator rights.  The script lists the entries, removes them, scans
   for hardware changes and lists the entries again.

If a connected Joulescope still does not use WinUSB after `-Reinstall`,
another driver package claims it.  The **Inf** column names that package,
for example `oem42.inf`.  To remove it, open PowerShell as administrator,
type the following with that name, and then run the script with
`-Reinstall` again:

```
pnputil /delete-driver oem42.inf /uninstall
```

```{literalinclude} joulescope_usb.ps1
:language: powershell
```

## Lost samples and long captures

If the waveform shows gaps, or a long capture stops, configure your host
computer as described in
{ref}`Host configuration <host-config>`, which covers sleep, power
management, updates and background tasks.

## Windows memory compression

Windows memory compression can reduce performance.  See
{ref}`Memory compression <host-config-windows-memory-compression>` in Host
configuration.

## Virtual Machines

We do not support running the Joulescope UI in virtual machines. The
Joulescope UI requires low-latency USB communication which can be problematic
under virtual machines. If you find that running the Joulescope UI within your
virtual machine works, great! If not, please install the Joulescope UI on the
native operating system.

## Recording to Network Storage

Joulescopes at full sample rate generate a lot of data. When recording, we
strongly recommend recording to a local solid-state drive (SSD) or hard disk
drive (HDD). If your computer lacks sufficient storage, you can purchase an
external HDD, which is very affordable.

Networks and network storage are often not able to keep up with the Joulescope
data rates. If you need to put your recording to network storage, we recommend
copying it over after the recording completes.

## UI opens to white / blank window

ASUS Sonic Studio 3 and ASUS Sonic Radar 3 cause a known issue with all OpenGL
applications in dual-monitor setups. If you close the Joulescope UI with a
Waveform widget on the second monitor and then restart the UI, it will appear
as a blank, white window. The workaround is to either keep the UI on the
primary monitor or uninstall both ASUS Sonic Studio 3 and ASUS Sonic Radar 3.
For more details, see
[issue \#252](https://github.com/jetperch/pyjoulescope_ui/issues/252) on
GitHub.
