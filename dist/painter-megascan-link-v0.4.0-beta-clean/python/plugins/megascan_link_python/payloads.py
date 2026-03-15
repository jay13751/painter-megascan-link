"""Normalize Fab Launcher export payloads into a stable internal schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


TEXTURE_KEYS = ("textures", "maps", "components", "files", "packedTextures")
MESH_KEYS = ("meshes", "models", "meshList")
LOD_KEYS = ("highPolyMeshes", "lodList", "lods", "highpoly")
ASSET_LIST_KEYS = ("assets", "payload", "items")
CORE_TEXTURE_USAGES = {
    "albedo",
    "basecolor",
    "base_color",
    "diffuse",
    "normal",
    "normal_dx",
    "normalgl",
    "roughness",
    "metal",
    "metalness",
    "occlusion",
    "ao",
    "displacement",
    "height",
}


@dataclass
class TextureEntry:
    path: str
    name: str = ""
    usage: str = ""
    texture_type: str = ""
    color_space: str = ""


@dataclass
class MeshEntry:
    path: str
    name: str = ""
    lod: str = ""
    mesh_type: str = ""


@dataclass
class NormalizedAsset:
    id: str
    name: str
    kind: str
    export_path: str = ""
    preview_image: str = ""
    textures: List[TextureEntry] = field(default_factory=list)
    meshes: List[MeshEntry] = field(default_factory=list)
    high_poly_meshes: List[MeshEntry] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "export_path": self.export_path,
            "preview_image": self.preview_image,
            "textures": [texture.__dict__ for texture in self.textures],
            "meshes": [mesh.__dict__ for mesh in self.meshes],
            "high_poly_meshes": [mesh.__dict__ for mesh in self.high_poly_meshes],
        }

    def to_transport_dict(self, action: str) -> Dict[str, Any]:
        legacy_kind = _legacy_kind(self.kind, bool(self.meshes))
        data: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "type": legacy_kind,
        }

        if action in {"import_resources", "warn_no_project", "no_assets"}:
            transport_textures = _textures_for_transport(self.textures)
            data["textures"] = transport_textures
            data["components"] = transport_textures
            return data

        transport_textures = _textures_for_transport(self.textures)
        data["textures"] = transport_textures
        data["components"] = transport_textures
        if self.meshes:
            transport_meshes = [{"path": mesh.path} for mesh in self.meshes if mesh.path]
            data["meshes"] = transport_meshes
            data["meshList"] = transport_meshes
        if self.high_poly_meshes:
            transport_lods = [{"path": mesh.path, "lod": "high"} for mesh in self.high_poly_meshes if mesh.path]
            data["high_poly_meshes"] = [{"path": mesh.path} for mesh in self.high_poly_meshes if mesh.path]
            data["lodList"] = transport_lods
        if self.preview_image:
            data["preview_image"] = self.preview_image
        return data


@dataclass
class NormalizedPayload:
    source: str
    assets: List[NormalizedAsset]
    raw: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "assets": [asset.to_dict() for asset in self.assets],
        }

    def to_transport_dict(self, action: str) -> Dict[str, Any]:
        return {
            "source": self.source,
            "assets": [asset.to_transport_dict(action) for asset in self.assets],
        }


def normalize_payload(raw_payload: Any) -> NormalizedPayload:
    assets_data = list(_extract_assets(raw_payload))
    normalized_assets = [_normalize_asset(asset_data) for asset_data in assets_data]
    return NormalizedPayload(source="fab", assets=normalized_assets, raw=raw_payload)


def _extract_assets(raw_payload: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(raw_payload, list):
        return [asset for asset in raw_payload if isinstance(asset, dict)]
    if not isinstance(raw_payload, dict):
        return []
    for key in ASSET_LIST_KEYS:
        candidate = raw_payload.get(key)
        if isinstance(candidate, list):
            return [asset for asset in candidate if isinstance(asset, dict)]
    return [raw_payload]


def _normalize_asset(asset: Dict[str, Any]) -> NormalizedAsset:
    asset_id = _string(asset.get("assetId") or asset.get("id") or asset.get("uuid"))
    metadata = asset.get("metadata") or {}
    megascans = metadata.get("megascans") or {}
    name = _string(asset.get("assetName") or asset.get("name") or megascans.get("name") or asset_id or "Unnamed Asset")
    kind = _normalize_kind(asset)
    textures = _normalize_textures(asset)
    meshes = _normalize_mesh_entries(_collect_entries(asset, MESH_KEYS))
    high_poly_meshes = _normalize_mesh_entries(_collect_entries(asset, LOD_KEYS), high_poly_only=True)
    export_path = _discover_export_path(asset, textures, meshes, high_poly_meshes)
    preview_image = _string(
        asset.get("preview")
        or asset.get("previewImage")
        or asset.get("thumbnail")
        or asset.get("image")
        or _preview_from_metadata(megascans)
    )
    return NormalizedAsset(
        id=asset_id or name,
        name=name,
        kind=kind,
        export_path=export_path,
        preview_image=preview_image,
        textures=textures,
        meshes=meshes,
        high_poly_meshes=high_poly_meshes,
        raw=asset,
    )


def _normalize_kind(asset: Dict[str, Any]) -> str:
    metadata = asset.get("metadata") or {}
    megascans = metadata.get("megascans") or {}
    semantic = megascans.get("semanticTags") or {}
    kind = _string(
        asset.get("assetType")
        or asset.get("type")
        or asset.get("category")
        or semantic.get("asset_type")
        or megascans.get("texture_type")
        or ""
    ).lower()
    if kind in {"3d", "3dplant", "model", "surface", "atlas", "decal", "material", "texture-set"}:
        return "surface" if kind in {"material", "texture-set"} else kind
    if _collect_entries(asset, MESH_KEYS):
        return "3d"
    if _normalize_textures(asset):
        return "surface"
    return kind or "asset"


def _normalize_textures(asset: Dict[str, Any]) -> List[TextureEntry]:
    textures = []
    for entry in _collect_entries(asset, TEXTURE_KEYS):
        path = _extract_path(entry)
        if not path:
            continue
        textures.append(
            TextureEntry(
                path=path,
                name=_string(entry.get("name") or entry.get("label") or Path(path).stem),
                usage=_string(entry.get("usage") or entry.get("channel") or entry.get("type") or entry.get("mapType")),
                texture_type=_string(entry.get("type") or entry.get("mimeType") or ""),
                color_space=_string(entry.get("colorSpace") or entry.get("colorspace") or ""),
            )
        )

    materials = asset.get("materials") or []
    for material in materials:
        if not isinstance(material, dict):
            continue
        tex_dict = material.get("textures") or {}
        for usage, path in tex_dict.items():
            if not path:
                continue
            textures.append(
                TextureEntry(
                    path=_string(path),
                    name=_string(material.get("name") or Path(_string(path)).stem),
                    usage=_string(usage),
                    color_space="",
                )
            )

    for path in asset.get("additional_textures") or []:
        if path:
            textures.append(TextureEntry(path=_string(path), name=Path(_string(path)).stem, usage="additional"))

    return _dedupe_paths(textures)


def _normalize_mesh_entries(entries: List[Dict[str, Any]], high_poly_only: bool = False) -> List[MeshEntry]:
    meshes = []
    for entry in entries:
        path = _extract_path(entry)
        if not path:
            continue
        lod = _string(entry.get("lod") or entry.get("level") or entry.get("meshQuality") or "")
        mesh_type = _string(entry.get("meshType") or entry.get("type") or "")
        if high_poly_only and not _is_high_poly(lod, mesh_type, path):
            continue
        meshes.append(MeshEntry(path=path, name=_string(entry.get("name") or Path(path).stem), lod=lod, mesh_type=mesh_type))
    return _dedupe_paths(meshes)


def _collect_entries(asset: Dict[str, Any], keys: Iterable[str]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for key in keys:
        value = asset.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    entries.append(item)
                elif isinstance(item, str):
                    entries.append({"path": item})
        elif isinstance(value, dict):
            for sub_key, item in value.items():
                if isinstance(item, dict):
                    if "usage" not in item and "type" not in item:
                        item = {**item, "usage": sub_key}
                    entries.append(item)
                elif isinstance(item, str):
                    entries.append({"path": item, "usage": sub_key})
    return entries


def _discover_export_path(asset: Dict[str, Any], textures: List[TextureEntry], meshes: List[MeshEntry], high_poly_meshes: List[MeshEntry]) -> str:
    direct = _string(asset.get("exportPath") or asset.get("folder") or asset.get("path") or asset.get("assetPath"))
    if direct and Path(direct).suffix == "":
        return direct
    for candidate in list(textures) + list(meshes) + list(high_poly_meshes):
        if candidate.path:
            return str(Path(candidate.path).parent)
    if direct:
        return str(Path(direct).parent)
    return ""


def _preview_from_metadata(megascans: Dict[str, Any]) -> str:
    previews = (megascans.get("previews") or {}).get("images") or []
    if previews:
        return _string(previews[0].get("uri") or "")
    return ""


def _extract_path(entry: Dict[str, Any]) -> str:
    return _string(entry.get("path") or entry.get("uri") or entry.get("file") or entry.get("url"))


def _is_high_poly(lod: str, mesh_type: str, path: str) -> bool:
    haystack = " ".join((lod, mesh_type, path)).lower()
    return any(token in haystack for token in ("high", "highpoly", "high_poly", "_hp"))


def _dedupe_paths(entries: List[Any]) -> List[Any]:
    seen = set()
    result = []
    for entry in entries:
        if entry.path in seen:
            continue
        seen.add(entry.path)
        result.append(entry)
    return result


def _textures_for_transport(textures: List[TextureEntry]) -> List[Dict[str, str]]:
    preferred_by_usage: Dict[str, str] = {}
    fallback_paths: List[str] = []

    for texture in textures:
        if not texture.path:
            continue
        usage = _canonical_usage(texture.usage)
        if usage and usage in CORE_TEXTURE_USAGES and usage not in preferred_by_usage:
            preferred_by_usage[usage] = texture.path
        elif not usage:
            fallback_paths.append(texture.path)

    ordered_usages = ("albedo", "normal", "roughness", "metal", "occlusion", "displacement")
    ordered_paths = [preferred_by_usage[usage] for usage in ordered_usages if usage in preferred_by_usage]

    if not ordered_paths:
        ordered_paths = fallback_paths[:]

    return [{"path": path} for path in ordered_paths]


def _canonical_usage(usage: str) -> str:
    normalized = usage.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "basecolor": "albedo",
        "base_color": "albedo",
        "diffuse": "albedo",
        "metalness": "metal",
        "ao": "occlusion",
        "normal_dx": "normal",
        "normal_gl": "normal",
        "normalgl": "normal",
        "height": "displacement",
    }
    return aliases.get(normalized, normalized)


def _legacy_kind(kind: str, has_meshes: bool) -> str:
    if kind in {"3d", "3dplant", "model"} or has_meshes:
        return "3d"
    return "surface"


def _string(value: Optional[Any]) -> str:
    if value is None:
        return ""
    return str(value)

