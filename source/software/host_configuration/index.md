(host-config)=

# Host configuration

A Joulescope streams samples to the host computer over USB.  The host must
receive and process each block of samples within a short time.  When the
host goes to sleep, throttles USB or the processor to save power, installs
updates or runs a long background task, it falls behind and samples are
lost.  The Joulescope UI shows lost samples as gaps in the waveform, and
Python scripts receive them as NaN values.

Occasional lost samples have little effect on averages, but a host that
sleeps or reboots ends the capture.  For short captures at your desk, the
default settings usually work.  Before a capture that runs unattended,
overnight or for days, configure the host computer as described here.

The Joulescope software does not keep the computer awake for you.  Configure
the power settings before you start the capture.


(host-config-guidelines)=

## General guidelines

These apply to every operating system:

* **Stay awake.**  Turn off sleep, hibernate and automatic suspend while the
  computer is plugged in.  The display may turn off.
* **Use full power.**  Plug a laptop into its power adapter and select the
  highest performance power mode.  Turn off power saving for USB.
* **Defer updates.**  Operating system and application updates can take over
  the computer or restart it.  Pause or defer them for the duration of the
  capture.  For critical captures, also disconnect the network, which stops
  updates, cloud sync and network backups.
* **Minimize background work.**  Quit applications you do not need, pause
  cloud sync and backups, and schedule antivirus scans outside the capture.
  If you cannot turn off antivirus scanning, exclude the Joulescope UI and
  the recording folder.
* **Record locally.**  Record to a local solid-state drive (SSD) or hard disk
  drive (HDD) with enough free space, not to network storage.  Copy the
  recording to network storage after the capture ends.
* **Use the native operating system.**  Virtual machines often cannot
  service USB quickly enough.
* **Connect directly.**  If you see lost samples, connect the Joulescope
  directly to a USB port on the computer instead of through a hub, dock or
  adapter.
* **Keep the clock accurate.**  The Joulescope software timestamps samples
  using the host computer's clock.  Keep the clock synchronized to a time
  server.  This matters most when you compare recordings from multiple
  Joulescopes or align them with other equipment.

For very long captures, consider recording statistics instead of, or in
addition to, the full-rate samples.  The instrument computes statistics,
including the charge and energy accumulators, so they stay correct even if
the host misses an update.

Then follow the steps for your operating system:

{doc}`windows`
: Power plan, USB and PCI Express power management, Windows Update and high
  accuracy time.

{doc}`macos`
: Sleep settings, `caffeinate`, App Nap and software updates.

{doc}`linux`
: Automatic suspend, `systemd-inhibit`, lid switch and unattended upgrades.

```{toctree}
:hidden:

windows
macos
linux
```
