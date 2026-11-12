(host-config-macos)=

# macOS

macOS rarely interrupts a capture while the computer is awake, but by
default it sleeps when idle.  A Mac laptop also sleeps when you close the
lid, unless an external display is connected.

These steps apply to macOS 26 and newer.  See {ref}`host-config` for the
general guidelines.


(host-config-macos-power)=

## Power settings

On a Mac laptop:

1. Plug the Mac into its power adapter.
2. Open **System Settings** → **Battery**.
   1. Set **Low Power Mode** to **Never**.
   2. Select **Options…** and turn on **Prevent automatic sleeping on power
      adapter when the display is off**.
3. Leave the lid open, or connect an external display, keyboard and mouse.

On a Mac desktop, open **System Settings** → **Energy** and turn on
**Prevent automatic sleeping when the display is off**.  Turn off
**Low Power Mode** if it is listed.

Instead of changing these settings, you can keep the Mac awake only for the
duration of a capture.  Open Terminal and type:

```
caffeinate -i -s
```

The Mac stays awake until you press Control-C or close the Terminal window.
`-i` prevents idle sleep, and `-s` prevents system sleep while on the power
adapter.  `caffeinate` does not prevent sleep when you close a laptop lid.


(host-config-macos-app-nap)=

## App Nap

macOS reduces the priority of applications whose windows are hidden, a
feature called App Nap.  Keep the Joulescope UI window visible during a
capture.  To turn off App Nap for the Joulescope UI, open Terminal and type:

```
defaults write com.jetperch.joulescope NSAppSleepDisabled -bool YES
```

Then restart the Joulescope UI.


(host-config-macos-updates)=

## Updates and background tasks

1. Before the capture, install pending updates and restart.
2. Open **System Settings** → **General** → **Software Update**.  Select
   the information button next to **Automatic updates**, and turn off the
   options that install updates.
3. Quit applications you do not need, and pause cloud sync.
4. Turn off automatic Time Machine backups, or exclude the recording folder.
5. For critical captures, disconnect the network.


(host-config-macos-time)=

## Time

macOS synchronizes its clock automatically.  Open **System Settings** →
**General** → **Date & Time** and check that **Set time and date
automatically** is on.
