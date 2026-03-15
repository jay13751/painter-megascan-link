# Painter Megascan Link (Unofficial Maintenance Fork)

This fork revives the original [Raider-Arts painter-megascan-link](https://github.com/Raider-Arts/painter-megascan-link) for modern `Adobe Substance 3D Painter 10.1+`.

It targets the current Painter plugin runtime (`Qt 6`, `PySide6`, `Python 3.11`) and supports `Fab Launcher` using `Custom (socket port)` export.

## What changed in this fork

- Migrated the Python plugin to a Qt6-friendly import path with a `PySide6` first runtime.
- Added a payload normalizer for Fab Launcher exports.
- Moved the main Fab import flow into Python instead of relying on the old Python-to-JS bridge for every action.
- Added config migration defaults for new connection/debug options.
- Added Fab payload fixtures and tests.

## Supported environment

- Painter: `10.1+`
- OS validation target: Windows
- Export source: Fab Launcher only
- Asset types validated so far:
  - surface / texture-set imports into an open Painter project
  - mesh-based Fab assets creating a new Painter project

## Installation

Painter now separates Python and JavaScript plugin folders. Keep both plugin folders installed in Painter even though the common Fab import path now runs mostly through Python.

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
5. Start Painter before exporting.
6. Export while Painter is running.

## How it works now

- Surface or texture-set exports:
  - Export into an already open Painter project.
  - The Python plugin imports the filtered core texture maps directly as project resources.
- Mesh-based exports:
  - If no project is open, the Python plugin can create a new Painter project from the exported mesh.
  - If multiple mesh assets are present, the plugin asks which mesh to use.
  - If a project is already open and `askcreateproject` is enabled, the plugin asks whether to create a new project or only import textures.

## Core texture filtering

For texture-only imports, the plugin currently keeps the main Painter-relevant maps and ignores duplicate or less-useful Fab maps.

- Included:
  - `BaseColor / Albedo`
  - `Normal`
  - `Roughness`
  - `Metalness`
  - `AO`
  - `Displacement`
- Ignored by default:
  - `Diffuse`
  - `Gloss`
  - `Specular`
  - `Bump`
  - `Cavity`

## Current behavior

- The socket listener runs in the Python plugin on port `24981`.
- Fab payloads are normalized into a stable internal schema before import decisions are made.
- Texture-only imports are handled directly through the Painter Python API.
- Mesh project creation is also handled from Python using the Painter Python API.
- The JavaScript plugin is still bundled for compatibility with the original plugin structure and for remaining Painter-side behavior that may still require it.

## Tests

The repository includes payload normalization, config migration, and import-controller tests:

```powershell
pytest tests
```

## Known limitations

- Fab payload formats may continue to evolve. When a new payload shape appears, add a fixture under `tests/fixtures` and extend `megascan_link_python/payloads.py`.
- Bake follow-up behavior has not been fully reworked around the new Python-first import path yet.
- This fork is focused on Fab Launcher workflows and does not aim to preserve pre-10.1 Painter compatibility.
- Legacy Quixel Bridge support has been removed.
