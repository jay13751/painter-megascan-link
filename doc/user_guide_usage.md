# How to Use

## Basic flow

1. Start Substance 3D Painter.
2. Make sure the Megascan Link toolbar button is visible.
3. Export an asset from Fab Launcher using the configured socket port.
4. Let the plugin either import textures into the current project or create a new project from an exported mesh.

## Import behavior

- Texture-only exports are imported as project resources under `Megascan/<AssetName>(<AssetId>)`.
- Mesh exports can trigger new project creation.
- If multiple mesh assets are present, the plugin can ask you which mesh to use as the project base.

## Settings

### Connection

- `Port Number`: TCP port the plugin listens on. Default `24981`.
- `Timeout`: Socket timeout in seconds. Default `5`.

### Import

- `Don't ask to create new project`: suppresses the prompt when a mesh arrives while a project is open.
- `Print log to console`: mirrors plugin logs to the Painter console.
- `Select resources after import`: highlights imported resources in Painter.
- `Log raw payloads`: writes the incoming raw JSON payload to the plugin log for debugging.
- `Ignore missing optional fields`: continues importing when non-critical payload fields are absent.

### Bake

Bake options still apply after a project is created from a mesh export.

## Troubleshooting

- If exports do nothing, verify the port matches on both sides.
- If Painter logs a payload normalization error, capture the raw payload and add a fixture for it before adjusting the normalizer.
- If the plugin loads but cannot create a project, keep the JS shim installed under `javascript/plugins`.
