# Painter Megascan Link (Unofficial Maintenance Fork)

This fork revives the original [Raider-Arts painter-megascan-link](https://github.com/Raider-Arts/painter-megascan-link) for modern `Adobe Substance 3D Painter 10.1+`.

It targets the current Painter plugin runtime (`Qt 6`, `PySide6`, `Python 3.11`) and supports `Fab Launcher` using `Custom (socket port)` export.

## What changed in this fork

- Migrated the Python plugin to a Qt6-friendly import path with a `PySide6` first runtime.
- Added a payload normalizer for Fab Launcher exports.
- Moved import decisions into Python, leaving the JavaScript plugin as a thin Painter action shim.
- Added config migration defaults for new connection/debug options.
- Added Fab payload fixtures and tests.

## Supported environment

- Painter: `10.1+`
- OS validation target: Windows
- Export source: Fab Launcher only

## Installation

Painter now separates Python and JavaScript plugin folders.

Windows:
- `%USERPROFILE%\\Documents\\Adobe\\Adobe Substance 3D Painter\\python\\plugins\\megascan_link_python`
- `%USERPROFILE%\\Documents\\Adobe\\Adobe Substance 3D Painter\\javascript\\plugins\\megascan_link_js`

macOS:
- `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/megascan_link_python`
- `~/Documents/Adobe/Adobe Substance 3D Painter/javascript/plugins/megascan_link_js`

Copy the two folders from this repository into those locations, then restart Painter or reload plugin folders from Painter's plugin settings.

## Fab Launcher setup

1. Open Fab in Launcher.
2. Choose a Megascans asset.
3. Set export target to `Custom (socket port)`.
4. Use socket port `24981` unless you changed it in the plugin settings.
5. Export while Painter is running.

## Current behavior

- If Painter already has a project open and the export includes mesh assets, the plugin can prompt to create a new project.
- If no project is open and a mesh asset exists, the plugin can create a Painter project from the first mesh or ask you to choose one.
- If only textures are exported, the plugin imports them as project resources.
- Bake settings are still forwarded to the JS shim after project creation.

## Tests

The repository includes payload normalization and config migration tests:

```powershell
pytest tests
```

## Known limitations

- Painter-side import and project creation still rely on a small QML shim because the original workflow depends on Painter JavaScript APIs.
- Fab payload formats may continue to evolve. When a new payload shape appears, add a fixture under `tests/fixtures` and extend `megascan_link_python/payloads.py`.
- This fork does not aim to preserve pre-10.1 Painter compatibility.
