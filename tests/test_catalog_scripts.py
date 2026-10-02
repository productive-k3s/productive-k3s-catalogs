import sys
from pathlib import Path

import pytest
import yaml

from scripts import sync_catalog_docs, validate_catalog as catalog_validator
from scripts.sync_catalog_docs import sync_catalog
from scripts.validate_catalog import CatalogValidationError, validate_catalog


SHA = "a" * 64
REVISION = "b" * 40


def addon_compatibility():
    return {
        "requires": {
            "core": {"contract": "artifact/v1", "minVersion": "0.9.6", "maxVersionExclusive": "0.10.0"},
            "kubernetes": {"distros": ["k3s", "rke2"]},
        }
    }


def entry(**overrides):
    value = {
        "id": "demo",
        "name": "Demo",
        "kind": "addon",
        "visibility": "public",
        "category": "testing",
        "description": "Fixture",
        "artifact": {"url": "https://example.test/demo.tgz", "sha256": SHA},
        "bom": {"url": "https://example.test/demo.bom.json", "sha256": SHA, "embeddedPath": "bom.json"},
    }
    value.update(overrides)
    return value


def write_catalog(tmp_path: Path, entries=None, **overrides) -> Path:
    data = {
        "apiVersion": "catalogs.productive-k3s.io/v1alpha1",
        "kind": "ProductiveK3SCatalog",
        "metadata": {"name": "test", "version": "0.9.65"},
        "entries": entries if entries is not None else [entry()],
    }
    data.update(overrides)
    path = tmp_path / "catalog.yaml"
    path.write_text(yaml.safe_dump(data))
    return path


def test_accepts_public_artifact_and_commercial_entry(tmp_path):
    commercial = entry(id="pro", visibility="private", artifact={}, commercial={"url": "https://example.test/buy"})
    assert validate_catalog(write_catalog(tmp_path, [entry(), commercial])) == 2


def test_accepts_compatibility_aware_catalog(tmp_path):
    compatible = entry(sourceRevision=REVISION, compatibility=addon_compatibility())
    assert validate_catalog(write_catalog(tmp_path, [compatible])) == 1


def test_rejects_mixed_legacy_and_compatibility_entries(tmp_path):
    compatible = entry(id="compatible", sourceRevision=REVISION, compatibility=addon_compatibility())
    with pytest.raises(CatalogValidationError, match="cannot mix"):
        validate_catalog(write_catalog(tmp_path, [compatible, entry(id="legacy")]))


def test_rejects_unknown_contract_and_invalid_window(tmp_path):
    compatibility = addon_compatibility()
    compatibility["requires"]["core"]["contract"] = "artifact/v2"
    value = entry(sourceRevision=REVISION, compatibility=compatibility)
    with pytest.raises(CatalogValidationError, match="artifact/v1"):
        validate_catalog(write_catalog(tmp_path, [value]))

    compatibility = addon_compatibility()
    compatibility["requires"]["core"]["maxVersionExclusive"] = "0.9.6"
    value = entry(sourceRevision=REVISION, compatibility=compatibility)
    with pytest.raises(CatalogValidationError, match="non-empty"):
        validate_catalog(write_catalog(tmp_path, [value]))


def test_rejects_compatibility_catalog_without_semantic_snapshot_version(tmp_path):
    compatible = entry(sourceRevision=REVISION, compatibility=addon_compatibility())
    with pytest.raises(CatalogValidationError, match="metadata.version"):
        validate_catalog(write_catalog(tmp_path, [compatible], metadata={"name": "test"}))


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data.update(apiVersion="old"), "apiVersion"),
        (lambda data: data.update(kind="Other"), "kind"),
        (lambda data: data.update(entries={}), "entries must be a list"),
        (lambda data: data.update(entries=["bad"]), "must be an object"),
        (lambda data: data["entries"][0].pop("name"), "missing required field"),
        (lambda data: data.update(entries=[entry(), entry()]), "duplicated"),
        (lambda data: data["entries"][0].update(visibility="unknown"), "invalid visibility"),
        (lambda data: data["entries"][0].update(kind="unknown"), "invalid kind"),
        (lambda data: data["entries"][0].update(artifact={}), "must expose artifact.url"),
        (lambda data: data["entries"][0]["artifact"].update(sha256="bad"), "artifact.sha256"),
        (lambda data: data["entries"][0].update(bom={}), "bom.url"),
        (lambda data: data["entries"][0]["bom"].update(sha256="bad"), "bom.sha256"),
    ],
)
def test_rejects_invalid_catalog_contract(tmp_path, mutation, message):
    data = {
        "apiVersion": "catalogs.productive-k3s.io/v1alpha1",
        "kind": "ProductiveK3SCatalog",
        "entries": [entry()],
    }
    mutation(data)
    path = tmp_path / "catalog.yaml"
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(CatalogValidationError, match=message):
        validate_catalog(path)


def test_rejects_missing_and_non_object_catalog(tmp_path):
    with pytest.raises(CatalogValidationError, match="not found"):
        validate_catalog(tmp_path / "missing.yaml")
    path = tmp_path / "catalog.yaml"
    path.write_text("- list\n")
    with pytest.raises(CatalogValidationError, match="YAML object"):
        validate_catalog(path)


def test_sync_catalog_copies_source_and_creates_parent(tmp_path):
    source = tmp_path / "catalogs" / "index.yaml"
    source.parent.mkdir()
    source.write_text("entries: []\n")
    target = sync_catalog(tmp_path)
    assert target.read_text() == source.read_text()


def test_sync_catalog_rejects_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError, match="catalog source not found"):
        sync_catalog(tmp_path)


def test_validator_main_success_and_failures(tmp_path, monkeypatch, capsys):
    path = write_catalog(tmp_path)
    monkeypatch.setattr(sys, "argv", ["validate_catalog.py", str(path)])
    catalog_validator.main()
    assert "1 entries validated" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["validate_catalog.py"])
    with pytest.raises(SystemExit, match="1"):
        catalog_validator.main()
    assert "usage:" in capsys.readouterr().err

    monkeypatch.setattr(sys, "argv", ["validate_catalog.py", str(tmp_path / "missing.yaml")])
    with pytest.raises(SystemExit, match="1"):
        catalog_validator.main()
    assert "catalog not found" in capsys.readouterr().err


def test_sync_main_success_and_failure(tmp_path, monkeypatch, capsys):
    script = tmp_path / "scripts" / "sync_catalog_docs.py"
    script.parent.mkdir()
    source = tmp_path / "catalogs" / "index.yaml"
    source.parent.mkdir()
    source.write_text("entries: []\n")
    monkeypatch.setattr(sync_catalog_docs, "__file__", str(script))
    sync_catalog_docs.main()
    assert "Synced catalog" in capsys.readouterr().out

    source.unlink()
    with pytest.raises(SystemExit, match="1"):
        sync_catalog_docs.main()
    assert "catalog source not found" in capsys.readouterr().err
