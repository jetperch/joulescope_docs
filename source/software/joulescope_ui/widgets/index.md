(ui-widgets)=

# Widgets

The Joulescope UI is built from widgets.  Each view, such as the Multimeter
view and the Oscilloscope view, is a set of widgets in the central widget
area.  {ref}`ui-meet-the-joulescope-ui` introduces the main views.  This
chapter describes each widget in detail.

To add a widget to the active view, select it from the **Widgets** menu.
Drag a widget's title bar to rearrange it, or to undock it into its own
window.  Click the × on the title bar to close it.  The UI saves the widgets
in each view, with their settings, when it exits.

Most widgets share these conventions:

* Right-click (control-click on macOS) on a widget for a context menu.  The
  menu depends on where you click.
* Select **Settings** from the context menu to see and change all of the
  widget's settings.
* Hover over a control to show its tooltip.
* Widgets that display one instrument have a source selection.  **default**
  follows the default device, which you set in the **Device Control**
  widget.  See {ref}`ui-multiple-instrument-support`.
* Widgets that display live data stop updating while the **Signal sample
  streaming** or **Statistics display** button on the **Side Bar** pauses
  that data.

```{toctree}
:maxdepth: 2

multimeter
waveform
trigger
spectrum
efficiency
```
