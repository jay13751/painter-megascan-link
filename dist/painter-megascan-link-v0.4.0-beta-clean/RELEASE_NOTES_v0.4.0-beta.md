# v0.4.0-beta

## Highlights

- Restored Fab Launcher support for Substance 3D Painter 10.1+.
- Reworked the plugin around a Python-first import flow.
- Texture-only Fab exports now import directly through the Painter Python API.
- Mesh-based Fab exports can now create a new Painter project from Python.
- Reduced dependence on the old Python-to-JS websocket bridge.

## What changed

- Added Fab payload normalization for current Launcher exports.
- Added filtering for core texture maps used during texture-only imports.
- Added Python-side project creation for mesh-based Fab assets.
- Added Python-side mesh selection and project creation prompts.
- Updated socket handling for current Painter and Fab runtime behavior.
- Updated README to match the current Fab-only workflow.

## Supported workflow

- Painter `10.1+`
- Fab Launcher `Custom (socket port)` export
- Surface / texture-set imports into an open Painter project
- Mesh-based exports creating a new Painter project

## Tests

- `pytest tests`
- Current result at release time: `8 passed`

## Known limitations

- Bake follow-up behavior has not been fully reworked around the new Python-first flow yet.
- The JavaScript plugin is still bundled for compatibility and remaining Painter-side behavior.
- Legacy Quixel Bridge support is intentionally removed.
