"""Thin wrappers around Painter Python APIs.

The plugin can still delegate some work to the JavaScript shim when Painter's
Python surface is too limited, but common project and resource operations live
here so we can avoid the JS bridge for the common Fab workflows.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from . import log
from .qt_compat import QtWidgets


def is_project_open() -> Optional[bool]:
    try:
        import substance_painter.project as project
    except Exception:
        return None

    try:
        return bool(project.is_open())
    except Exception:
        return None


def save_and_close_project() -> bool:
    try:
        import substance_painter.project as project
    except Exception as exc:
        log.LoggerLink.Log("Painter project API unavailable: {}".format(exc))
        return False

    try:
        project.save()
        project.close()
        return True
    except Exception as exc:
        log.LoggerLink.Log("Failed to save and close project: {}".format(exc))
        return False


def create_project(mesh_path: str, texture_paths: Sequence[str], resolution: Optional[int] = None) -> bool:
    try:
        import substance_painter.project as project
    except Exception as exc:
        log.LoggerLink.Log("Painter project API unavailable: {}".format(exc))
        return False

    try:
        settings = project.Settings()
        if resolution:
            settings.default_texture_resolution = resolution
        project.create(mesh_file_path=mesh_path, mesh_map_file_paths=list(texture_paths), settings=settings)
        log.LoggerLink.Log("Python created Painter project from mesh {}".format(mesh_path))
        return True
    except Exception as exc:
        log.LoggerLink.Log("Failed to create Painter project from mesh {}: {}".format(mesh_path, exc))
        return False


def import_project_textures(paths: Iterable[str], group_name: str = "", select_after_import: bool = False) -> int:
    try:
        import substance_painter.resource as resource
    except Exception:
        return 0

    imported: List[object] = []
    for path in paths:
        if not path:
            continue
        try:
            imported.append(
                resource.import_project_resource(
                    file_path=path,
                    resource_usage=resource.Usage.TEXTURE,
                    group=group_name or None,
                )
            )
            log.LoggerLink.Log("Python imported project resource {}".format(path))
        except Exception as exc:
            log.LoggerLink.Log("Python failed to import resource {}: {}".format(path, exc))
            continue

    if imported and select_after_import:
        try:
            resource.show_resources_in_ui(imported)
        except Exception:
            pass
    return len(imported)


def ask_create_project(asset_count: int, has_open_project: bool) -> str:
    title = "Megascan Link"
    if has_open_project:
        text = "The Fab export contains {} mesh asset(s). Create a new Painter project with a mesh, or only import textures into the current project?".format(asset_count)
    else:
        text = "The Fab export contains {} mesh asset(s). Create a new Painter project now?".format(asset_count)

    message_box = QtWidgets.QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(text)
    create_button = message_box.addButton("New Project", QtWidgets.QMessageBox.AcceptRole)
    import_button = None
    if has_open_project:
        import_button = message_box.addButton("Import Only", QtWidgets.QMessageBox.ActionRole)
    cancel_button = message_box.addButton(QtWidgets.QMessageBox.Cancel)
    message_box.setDefaultButton(create_button)
    message_box.exec_()

    clicked = message_box.clickedButton()
    if clicked == create_button:
        return "create_project"
    if import_button is not None and clicked == import_button:
        return "import_resources"
    if clicked == cancel_button:
        return "cancel"
    return "cancel"


def choose_mesh_asset(asset_names: Sequence[str]) -> Optional[int]:
    if not asset_names:
        return None
    selected, accepted = QtWidgets.QInputDialog.getItem(
        None,
        "Megascan Link",
        "Select the mesh asset to use for the new project:",
        list(asset_names),
        0,
        False,
    )
    if not accepted:
        return None
    try:
        return list(asset_names).index(selected)
    except ValueError:
        return None
