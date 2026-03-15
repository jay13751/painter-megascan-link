# Fab Launcher Manual QA

This checklist is for validating the maintained Fab-only fork inside Substance 3D Painter 10.1+.

## Preconditions

- Install both plugin folders into Painter's plugin directories.
- Launch Painter 10.1+.
- Confirm the Megascan Link toolbar button is visible.
- Open Fab in Launcher.
- Set Fab export target to `Custom (socket port)`.
- Match the export port to the plugin setting, default `24981`.

## Smoke test

1. Export a texture-only surface asset from Fab.
2. Confirm Painter logs a socket connection and normalized payload handling.
3. Confirm textures appear under `Megascan/<AssetName>(<AssetId>)` in project resources.
4. If `Select resources after import` is enabled, confirm the imported resources are selected.

## New project flow

1. Close the current Painter project.
2. Export a mesh-based asset from Fab.
3. Confirm a new Painter project is created from the first mesh.
4. Confirm related textures are added during project creation.

## Multi-mesh selection flow

1. Export a payload containing more than one mesh asset.
2. Confirm the mesh selection dialog appears.
3. Pick a mesh and verify project creation uses that mesh.
4. Confirm non-selected assets are still imported as resources.

## Existing project prompt flow

1. Open any Painter project.
2. Export a mesh-based asset from Fab.
3. Confirm the dialog asks whether to import textures only or create a new project.
4. Test both choices.

## Bake flow

1. Enable bake in the plugin settings.
2. Export a mesh asset with a high poly mesh reference.
3. Confirm project creation completes.
4. Confirm bake parameters are applied and baking starts.

## Debugging notes

- Check `megascanlink.log` beside the Python plugin for payload and socket diagnostics.
- Enable `Log raw payloads` when validating a new Fab payload shape.
- If import works but project creation fails, confirm the JS shim is installed under `javascript/plugins`.
