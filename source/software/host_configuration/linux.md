(host-config-linux)=

# Linux

Linux rarely interrupts a capture while the computer is awake, but desktop
distributions suspend the computer when idle.  A laptop also suspends when
you close the lid.

These steps apply to Ubuntu 26.04 LTS with the GNOME desktop.  Other
distributions have similar settings.  See {ref}`host-config` for the general
guidelines.


(host-config-linux-power)=

## Power settings

1. Plug a laptop into its power adapter.
2. Open **Settings** → **Power**.
   1. Set **Power Mode** to **Performance**, if it is available.
   2. Under **Power Saving Options**, turn off **Automatic Suspend**, or
      turn it off for **When Plugged In**.  The screen may still blank.

You can also turn off automatic suspend when plugged in from a terminal:

```
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
```

Instead of changing these settings, you can keep the computer awake only for
the duration of a capture.  Open a terminal and type:

```
systemd-inhibit --what=idle:sleep --why="Joulescope capture" sleep infinity
```

The computer stays awake until you press Ctrl+C or close the terminal.

If you use other power management tools, such as TLP, configure them to
leave USB devices powered.


(host-config-linux-lid)=

## Laptop lid

To keep a laptop running with the lid closed, create the file
`/etc/systemd/logind.conf.d/joulescope.conf` containing:

```
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
```

Then restart the computer.


(host-config-linux-dedicated)=

## Dedicated test computers

On a computer used only for testing, you can prevent sleep entirely:

```
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

To allow sleep again, run the same command with `unmask` instead of `mask`.


(host-config-linux-updates)=

## Updates and background tasks

Ubuntu installs security updates automatically in the background.  These
updates use processor and disk time, and can restart services.

1. Before the capture, install pending updates and restart.
2. Open **Software & Updates** → **Updates**.  Set **When there are
   security updates** to **Display immediately**, so that updates wait for
   you to install them.
3. Quit applications you do not need, and pause cloud sync and backups.
4. For critical captures, disconnect the network.


(host-config-linux-time)=

## Time

Ubuntu synchronizes its clock automatically.  To check, open a terminal and
type:

```
timedatectl
```

**System clock synchronized** should be **yes**.
