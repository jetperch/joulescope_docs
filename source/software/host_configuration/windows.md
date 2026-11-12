(host-config-windows)=

# Windows

Windows is the most likely of the supported operating systems to interrupt a
long capture.  It aggressively saves power, updates itself and runs
background tasks.  Computer manufacturers also add their own power
management and support software, and some hide settings.  The goal is a
computer that stays awake, at full power, with nothing running in the
background.

These steps apply to Windows 11.  See {ref}`host-config` for the general
guidelines.


(host-config-windows-time)=

## Configure high accuracy time

By default, Windows synchronizes its clock infrequently, so the clock can be
off by many milliseconds.  The Joulescope UI can configure Windows for high
accuracy time, which synchronizes the clock every 64 seconds.

1. In the Joulescope UI, select **Tools** → **Configure high accuracy time**.
2. Windows asks for permission to make changes.  Select **Yes**.  You need
   administrator rights.

You only need to do this once.  The setting remains after restart.  For
details, see Microsoft's
[Configuring systems for high accuracy](https://learn.microsoft.com/en-us/windows-server/networking/windows-time-service/configuring-systems-for-high-accuracy).

To check the time synchronization status, open a terminal and type:

```
w32tm /query /status
```

**Last Successful Sync Time** should be within the last few minutes.  The
clock is only as accurate as its time server and network.  For the best
accuracy, use a local NTP time server.


(host-config-windows-power)=

## Power settings

These settings matter even when you log at a low sample rate.  The JS110
always streams its full 2 million samples per second to the computer, which
does the downsampling, so a low sample rate in the Joulescope UI does not
reduce the computer's processing load.  The JS220 and JS320 downsample on
the instrument.

1. Plug a laptop into its power adapter.
2. Open **Settings** → **System** → **Power & battery**.
   1. Set **Power mode** to **Best performance**.
   2. Under **Screen, sleep, & hibernate timeouts**, set the **screen**,
      **sleep** and **hibernate** timeouts for when plugged in to **Never**.
3. Open **Settings** → **Accounts** → **Sign-in options**.  Set **If
   you've been away, when should Windows require you to sign in again?** to
   **Never**, and turn off **Dynamic lock**.
4. Press Windows+R, type `powercfg.cpl` and select **OK** to open the
   Control Panel Power Options.  Select **High performance** if it is
   listed.  Then select **Change plan settings** → **Change advanced power
   settings** and set:
   * **USB settings** → **USB selective suspend setting** = Disabled
   * **PCI Express** → **Link State Power Management** = Off
   * **Processor power management** → **Minimum processor state** = 100%
5. In Power Options, select **Choose what the power buttons do** →
   **Change settings that are currently unavailable**, then clear
   **Turn on fast startup**.
6. Open **Device Manager**.  Under **Universal Serial Bus controllers**,
   open each **USB Root Hub** and **Generic USB Hub**.  On the
   **Power Management** tab, clear **Allow the computer to turn off this
   device to save power**.  Not all devices have this tab.

Keeping the screen on and unlocked is a precaution for unattended captures
with the Joulescope UI open.  We have reports of the Joulescope UI stopping
responding during multi-day captures after the computer was idle for a long
time with the screen off, but have not confirmed the cause.

Some computers hide settings in Power Options.  Instead of steps 2, 4 and 5, you
can open a terminal as administrator and type:

```
powercfg /change monitor-timeout-ac 0
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /setacvalueindex scheme_current 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a576df5 0
powercfg /setacvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 100
powercfg /setactive scheme_current
powercfg /hibernate off
```

The `/change` lines set the screen, sleep and hibernate timeouts to never
when plugged in.  The `setacvalueindex` lines turn off USB selective suspend and PCI Express
link state power management, and set the minimum processor state to 100 %,
when plugged in.  The last line turns off hibernate and fast startup.

For the most demanding captures, you can also disable processor C-states in
the computer's BIOS or UEFI setup.


(host-config-windows-updates)=

## Updates

Windows Update can take over the computer and restart it in the middle of a
capture.

1. Before the capture, install pending updates and restart.
2. Open **Settings** → **Windows Update** and select **Pause updates** for
   longer than the capture.
3. Turn off automatic updates in other software, such as the computer
   manufacturer's update or support software.  Some manufacturer support
   applications pause the computer for several seconds each day.  Quit them
   or disable their services.
4. For critical captures, disconnect the network: unplug the Ethernet cable
   and turn off Wi-Fi.  This is the most reliable way to prevent updates and
   restarts.

Before you start, also update the graphics, USB and network drivers and the
BIOS from the computer manufacturer.


(host-config-windows-background)=

## Background tasks

* Save recordings to a local folder that is not synced by OneDrive,
  Dropbox or similar, for example `C:\joulescope`.  Windows often puts
  your Documents folder in OneDrive by default.
* Quit applications you do not need, such as Teams and Outlook.  Pause
  OneDrive and other cloud sync.
* Turn off or reschedule backups.
* Antivirus software with real-time scanning can slow the Joulescope UI and
  get worse over time.  If you cannot turn it off for the capture, add
  exclusions for the Joulescope UI and the recording folder.  For Microsoft
  Defender, open **Windows Security** → **Virus & threat protection** →
  **Manage settings** → **Add or remove exclusions**.
* Check that Task Manager does not show the Joulescope UI in
  **Efficiency mode**, which reduces its priority.
* On computers with two graphics processors, open **Settings** →
  **System** → **Display** → **Graphics** and set the Joulescope UI to
  **High performance**.


(host-config-windows-memory-compression)=

## Memory compression

Windows compresses memory by default.  Memory compression can reduce
performance, especially if you increase the Joulescope UI memory buffer size
on a computer with a lot of RAM.

To check whether memory compression is on, open PowerShell as administrator
and type:

```
Get-MMAgent
```

If **MemoryCompression** is True, memory compression is on.  To turn it off,
type:

```
Disable-MMAgent -mc
```

Then restart the computer.


(host-config-windows-storage)=

## Storage

Check that the recording drive is healthy and has enough free space.  In
File Explorer, right-click the drive and select **Properties** → **Tools** →
**Check**.  You can also check the system files by opening a terminal as
administrator and typing `sfc /scannow`.
