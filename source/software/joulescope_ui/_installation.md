The Joulescope software is available to download at

[www.joulescope.com/download/](http://www.joulescope.com/download/)

Click on the download link for your operating system and platform
architecture. We recommend installing the Joulescope software on the native
operating system, not under a virtual machine, due to Joulescope’s demanding
USB communication requirements.

Check that your computer runs one of the
{ref}`supported platforms <supported-platforms>`, then see the section below
for your operating system.

## Microsoft® Windows

Click on the installer executable. Read and accept the license agreement, and
click **Next**. Accept the default installation location or change it as
needed, then click **Next**. Select **Next** and **Install**. Finally, click
**Finish** to complete the setup and launch the Joulescope UI.

## Apple® macOS

On macOS, download the dmg file which supports both x86_64 (Intel) and arm64
(Apple Silicon) platforms. Open the dmg file and then drag **joulescope.app**
to the **Applications** folder. Once the installation completes, you can eject
the dmg file.

The macOS distribution is currently signed and notarized, but it is not
distributed through the Apple Store. macOS should display that the application
has been checked by Apple, but that it was downloaded from the web. It should
install and run if you accept this warning.

If you receive a security warning, control-click the Joulescope application in
Finder, then select **open** to bypass these security warnings. You will need
to repeat the control-click, **open** process several times (usually twice)
until macOS finally allows the Joulescope software to launch. After going
through this process to grant permission once, subsequent runs will start
normally.

## Ubuntu Linux

Unpack the tar.gz file to the location of your choice. Then run the
joulescope_launcher binary in the extracted directory. You may need to install
additional dependencies.

```
sudo apt install libudev-dev libxcb-cursor0
```

Many Linux systems, including Ubuntu, use “udev” to manage devices and grant
permissions. You will need to install a udev rule that grants Joulescope
hardware access to your account. Download and follow the instructions in this
file:

<https://raw.githubusercontent.com/jetperch/joulescope_driver/main/99-joulescope.rules>

If you receive the error
`Could not load the Qt platform plugin "xcb" in "" even though it was found`,
then you need to install additional Qt6 dependencies. You can identify the
missing dependencies by running `export QT_DEBUG_PLUGINS=1` before starting
the Joulescope UI. Then install the missing dependencies with your package
manager.

## Python (all platforms)

Install a {ref}`supported version of Python <supported-platforms>` for your
platform.  Then create a virtual environment, which keeps the Joulescope UI
and its dependencies separate from your other Python software:

```
python -m venv ~/venv/joulescope
```

Activate the virtual environment.  On Windows:

```
~\joulescope\Scripts\activate
```

On macOS and Linux:

```
source ~/venv/joulescope/bin/activate
```

Then install the Joulescope UI:

```
python -m pip install -U --upgrade-strategy=eager joulescope_ui
```

Whenever you want to run the Joulescope UI, activate the virtual environment,
then type:

```
python -m joulescope_ui
```

To update the Joulescope UI, activate the virtual environment and repeat the
install command.
