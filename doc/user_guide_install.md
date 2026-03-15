# How to Install

This maintained fork supports `Substance 3D Painter 10.1+` and expects both the Python plugin and the JavaScript shim to be installed.

## Plugin folders

Windows:
- `%USERPROFILE%\\Documents\\Adobe\\Adobe Substance 3D Painter\\python\\plugins\\megascan_link_python`
- `%USERPROFILE%\\Documents\\Adobe\\Adobe Substance 3D Painter\\javascript\\plugins\\megascan_link_js`

macOS:
- `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/megascan_link_python`
- `~/Documents/Adobe/Adobe Substance 3D Painter/javascript/plugins/megascan_link_js`

## Install steps

1. Copy `megascan_link_python` into Painter's `python/plugins` folder.
2. Copy `megascan_link_js` into Painter's `javascript/plugins` folder.
3. Launch Painter.
4. Enable both plugins if Painter asks.
5. Open the Megascan Link toolbar button and confirm the socket port, default `24981`.

## Fab Launcher setup

- Use `Custom (socket port)` export.
- Match the port to the Painter plugin setting.

## Notes

- This fork is intended for Painter `10.1+` only.
- If you change the port, wait for the socket timeout window to expire or restart Painter.
- The JavaScript plugin remains required for Painter-side project creation and resource import commands.
