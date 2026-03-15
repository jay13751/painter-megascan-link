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
