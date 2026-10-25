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

## Windows memory compression

Microsoft Windows includes memory compression by default. While this is
normally not an issue, it can slow down performance on Windows, especially if
you increase the Joulescope memory buffer size on computers with large RAM.

To check if memory compression is enabled, launch PowerShell as Administrator
and type:

```
Get-MMAgent
```

If MemoryCompression is True, then memory compression is enabled on your
computer.

To disable memory compression, launch PowerShell as Administrator and type:

```
Disable-MMAgent -mc
```

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
