"""Python-side control flow for Megascans imports."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from . import config, log, painter_ops
from .payloads import NormalizedAsset, NormalizedPayload
from .websocket_link import WebsocketLink


@dataclass
class ImportDecision:
    action: str
    reason: str
    project_is_open: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "project_is_open": self.project_is_open,
        }


class ImportController:
    """Coordinates payload handling before handing off to the Painter shim."""

    def __init__(self, transport: Optional[WebsocketLink] = None):
        self._transport = transport or WebsocketLink()

    def handle_payload(self, payload: NormalizedPayload):
        decision = self.decide(payload)
        log.LoggerLink.Log(
            "Dispatching {} assets from {} with action {}".format(
                len(payload.assets), payload.source, decision.action
            ),
            logging.INFO,
        )
        if self._handle_in_python(payload, decision):
            return
        self._transport.send_payload(payload, config.ConfigSettings.getAsDict(), decision.to_dict())

    def _handle_in_python(self, payload: NormalizedPayload, decision: ImportDecision) -> bool:
        if decision.action == "import_resources":
            return self._import_resources(payload)
        if decision.action == "create_project":
            return self._create_project_from_payload(payload, None)
        if decision.action == "create_project_select_mesh":
            mesh_assets = [asset for asset in payload.assets if asset.meshes]
            choice = painter_ops.choose_mesh_asset([self._asset_label(asset) for asset in mesh_assets])
            if choice is None:
                log.LoggerLink.Log("Mesh selection cancelled by user", logging.INFO)
                return True
            return self._create_project_from_payload(payload, mesh_assets[choice])
        if decision.action == "prompt_project_creation":
            mesh_assets = [asset for asset in payload.assets if asset.meshes]
            user_action = painter_ops.ask_create_project(len(mesh_assets), has_open_project=True)
            if user_action == "import_resources":
                return self._import_resources(payload)
            if user_action == "create_project":
                selected_asset = None
                if len(mesh_assets) > 1:
                    choice = painter_ops.choose_mesh_asset([self._asset_label(asset) for asset in mesh_assets])
                    if choice is None:
                        log.LoggerLink.Log("Mesh selection cancelled by user", logging.INFO)
                        return True
                    selected_asset = mesh_assets[choice]
                return self._create_project_from_payload(payload, selected_asset)
            log.LoggerLink.Log("Project creation prompt cancelled by user", logging.INFO)
            return True
        return False

    def _asset_label(self, asset: NormalizedAsset) -> str:
        return "{} ({})".format(asset.name, asset.id)

    def _filtered_texture_paths(self, payload: NormalizedPayload, action: str) -> List[str]:
        transport_payload = payload.to_transport_dict(action)
        texture_paths: List[str] = []
        for asset in transport_payload.get("assets", []):
            for texture in asset.get("textures", []):
                path = texture.get("path")
                if path:
                    texture_paths.append(path)
        return texture_paths

    def _import_resources(self, payload: NormalizedPayload) -> bool:
        texture_paths = self._filtered_texture_paths(payload, "import_resources")
        if not texture_paths:
            log.LoggerLink.Log("No texture paths available for Python-side import", logging.WARNING)
            return True

        select_after_import = config.ConfigSettings.checkIfOptionIsSet("General", "selectafterimport")
        imported_count = painter_ops.import_project_textures(
            texture_paths,
            group_name="Megascan",
            select_after_import=select_after_import,
        )

        log.LoggerLink.Log(
            "Python-side resource import completed: {} of {} textures".format(
                imported_count, len(texture_paths)
            ),
            logging.INFO,
        )
        return True

    def _create_project_from_payload(self, payload: NormalizedPayload, selected_asset: Optional[NormalizedAsset]) -> bool:
        mesh_assets = [asset for asset in payload.assets if asset.meshes]
        asset = selected_asset or (mesh_assets[0] if mesh_assets else None)
        if asset is None:
            log.LoggerLink.Log("No mesh asset available for project creation", logging.WARNING)
            return True

        if painter_ops.is_project_open():
            if not painter_ops.save_and_close_project():
                log.LoggerLink.Log("Aborted project creation because the current project could not be closed", logging.ERROR)
                return True

        texture_paths = self._filtered_texture_paths(payload, "create_project")
        resolution = 4096
        created = painter_ops.create_project(
            mesh_path=asset.meshes[0].path,
            texture_paths=texture_paths,
            resolution=resolution,
        )
        if created:
            log.LoggerLink.Log(
                "Python-side project creation completed using mesh {}".format(asset.meshes[0].path),
                logging.INFO,
            )
        return True

    def decide(self, payload: NormalizedPayload) -> ImportDecision:
        project_is_open = painter_ops.is_project_open()
        mesh_assets = [asset for asset in payload.assets if asset.meshes]
        ask_create = config.ConfigSettings.checkIfOptionIsSet("General", "askcreateproject")

        if not payload.assets:
            return ImportDecision("no_assets", "No assets available after normalization", project_is_open)

        if project_is_open is False and not mesh_assets:
            return ImportDecision("warn_no_project", "No open project and no mesh assets available", project_is_open)

        if project_is_open is False and len(mesh_assets) > 1:
            return ImportDecision("create_project_select_mesh", "Multiple mesh assets available", project_is_open)

        if project_is_open is False and mesh_assets:
            return ImportDecision("create_project", "Creating a project from the first mesh asset", project_is_open)

        if project_is_open is True and mesh_assets and ask_create:
            return ImportDecision("prompt_project_creation", "Project is open and mesh assets were exported", project_is_open)

        if project_is_open is True:
            return ImportDecision("import_resources", "Importing resources into the active project", project_is_open)

        if mesh_assets:
            return ImportDecision("process_payload", "Project state unavailable, defer mesh decision to JS shim", project_is_open)

        return ImportDecision("process_payload", "Project state unavailable, defer import decision to JS shim", project_is_open)


