from megascan_link_python.import_controller import ImportController
from megascan_link_python.payloads import normalize_payload


class DummyTransport:
    def __init__(self):
        self.calls = []

    def send_payload(self, payload, settings, decision):
        self.calls.append((payload, settings, decision))


def test_import_resources_is_handled_in_python(monkeypatch):
    payload = normalize_payload(
        {
            "assets": [
                {
                    "assetId": "fab_asset_01",
                    "assetName": "Forest Moss",
                    "assetType": "surface",
                    "textures": [{"path": "D:/Fab/ForestMoss/albedo.png", "usage": "baseColor"}],
                }
            ]
        }
    )
    transport = DummyTransport()
    imported = {}

    def fake_import(paths, group_name="", select_after_import=False):
        imported["value"] = (list(paths), group_name, select_after_import)
        return len(imported["value"][0])

    monkeypatch.setattr("megascan_link_python.painter_ops.is_project_open", lambda: True)
    monkeypatch.setattr(
        "megascan_link_python.painter_ops.import_project_textures",
        fake_import,
    )
    monkeypatch.setattr(
        "megascan_link_python.config.ConfigSettings.checkIfOptionIsSet",
        lambda category, prop, fallback="": True if (category, prop) == ("General", "selectafterimport") else False,
    )

    controller = ImportController(transport=transport)
    controller.handle_payload(payload)

    assert transport.calls == []
    assert imported["value"] == (["D:/Fab/ForestMoss/albedo.png"], "Megascan", True)


def test_import_resources_uses_filtered_transport_textures(monkeypatch):
    payload = normalize_payload(
        [
            {
                "id": "fab_asset",
                "name": "Metal",
                "materials": [
                    {
                        "textures": {
                            "albedo": "C:/maps/albedo.jpg",
                            "diffuse": "C:/maps/diffuse.jpg",
                            "roughness": "C:/maps/roughness.jpg",
                            "glossiness": "C:/maps/gloss.jpg",
                            "normal": "C:/maps/normal.jpg",
                            "specular": "C:/maps/specular.jpg",
                        }
                    }
                ],
            }
        ]
    )
    transport = DummyTransport()
    imported = {}

    def fake_import(paths, group_name="", select_after_import=False):
        imported["value"] = list(paths)
        return len(imported["value"])

    monkeypatch.setattr("megascan_link_python.painter_ops.is_project_open", lambda: True)
    monkeypatch.setattr("megascan_link_python.painter_ops.import_project_textures", fake_import)
    monkeypatch.setattr(
        "megascan_link_python.config.ConfigSettings.checkIfOptionIsSet",
        lambda category, prop, fallback="": False,
    )

    controller = ImportController(transport=transport)
    controller.handle_payload(payload)

    assert transport.calls == []
    assert imported["value"] == [
        "C:/maps/albedo.jpg",
        "C:/maps/normal.jpg",
        "C:/maps/roughness.jpg",
    ]


def test_create_project_is_handled_in_python(monkeypatch):
    payload = normalize_payload(
        {
            "assets": [
                {
                    "assetId": "fab_mesh_01",
                    "assetName": "Statue",
                    "assetType": "model",
                    "textures": [{"path": "D:/Fab/Statue/albedo.png", "usage": "baseColor"}],
                    "meshes": [{"path": "D:/Fab/Statue/statue.fbx"}],
                }
            ]
        }
    )
    transport = DummyTransport()
    created = {}

    monkeypatch.setattr("megascan_link_python.painter_ops.is_project_open", lambda: False)
    monkeypatch.setattr(
        "megascan_link_python.painter_ops.create_project",
        lambda mesh_path, texture_paths, resolution=None: created.setdefault(
            "value", (mesh_path, list(texture_paths), resolution)
        )
        or True,
    )

    controller = ImportController(transport=transport)
    controller.handle_payload(payload)

    assert transport.calls == []
    assert created["value"] == ("D:/Fab/Statue/statue.fbx", ["D:/Fab/Statue/albedo.png"], 4096)
