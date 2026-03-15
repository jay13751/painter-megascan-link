"""Python-side control flow for Megascans imports."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from . import config, log, painter_ops
from .payloads import NormalizedPayload
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
        self._transport.send_payload(payload, config.ConfigSettings.getAsDict(), decision.to_dict())

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


