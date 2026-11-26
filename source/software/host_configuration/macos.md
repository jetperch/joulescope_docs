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


(host-config-macos-background)=

## Spotlight and Apple Intelligence

macOS runs background work in bursts.  Spotlight indexes files, and Apple
Intelligence and Photos analyze content and load machine learning models.
When a burst starts many tasks at once, the Mac can briefly stop servicing
USB.  During long full-rate captures on a test Mac, these bursts delayed
the Joulescope software by up to tens of milliseconds and occasionally lost
samples.

1. Exclude the recording folder from Spotlight.  Open **System Settings** →
   **Spotlight** and select **Search Privacy…**.  Select **+** and add the
   folder or drive you record to.  Spotlight then does not index large
   recordings while they are written.
2. For critical captures, turn off Apple Intelligence.  Open **System
   Settings** → **Apple Intelligence & Siri** and turn off **Apple
   Intelligence**.  Turn it back on after the capture if you use it.
3. After you install macOS or a major update, Spotlight and Photos may
   index and analyze for some time.  Leave the Mac on and idle until this
   background work finishes before you start a long capture.

On a computer dedicated to measurements, you can turn off Spotlight
indexing for all drives.  Open Terminal and type:

```
sudo mdutil -a -i off
```

To turn indexing back on, type `sudo mdutil -a -i on`.


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
