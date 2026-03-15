import json
from pathlib import Path

from megascan_link_python.payloads import normalize_payload


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_normalize_fab_payload():
    payload = normalize_payload(load_fixture("fab_payload.json"))

    assert payload.source == "fab"
    assert len(payload.assets) == 2
    assert payload.assets[0].export_path.endswith("ForestMoss")
    assert payload.assets[1].kind == "model"
    assert payload.assets[1].meshes[0].path.endswith("statue.fbx")
    assert payload.assets[1].high_poly_meshes[0].path.endswith("statue_high.fbx")


def test_normalize_handles_missing_optional_fields():
    payload = normalize_payload({"assets": [{"assetId": "a", "assetName": "Only Name"}]})

    assert payload.source == "fab"
    assert payload.assets[0].textures == []
    assert payload.assets[0].meshes == []
    assert payload.assets[0].export_path == ""


def test_transport_payload_is_minimal_for_import_resources():
    payload = normalize_payload(load_fixture("fab_payload.json"))

    transport = payload.to_transport_dict("import_resources")

    first_asset = transport["assets"][0]
    assert set(first_asset.keys()) == {"id", "name", "kind", "type", "textures", "components"}
    assert set(first_asset["textures"][0].keys()) == {"path"}
    assert len(first_asset["textures"]) == 2
    assert first_asset["components"] == first_asset["textures"]
    assert first_asset["type"] == "surface"

    mesh_asset = payload.to_transport_dict("create_project")["assets"][1]
    assert "meshes" in mesh_asset
    assert "meshList" in mesh_asset
    assert "high_poly_meshes" in mesh_asset
    assert "lodList" in mesh_asset
    assert set(mesh_asset["meshes"][0].keys()) == {"path"}
    assert mesh_asset["type"] == "3d"


def test_transport_payload_filters_to_core_fab_channels():
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

    transport = payload.to_transport_dict("import_resources")

    assert transport["assets"][0]["textures"] == [
        {"path": "C:/maps/albedo.jpg"},
        {"path": "C:/maps/normal.jpg"},
        {"path": "C:/maps/roughness.jpg"},
    ]
