#!/usr/bin/env python3
import sys
import re
from pathlib import Path
import yaml

REQUIRED_ENTRY_FIELDS = ["id", "name", "kind", "visibility", "category", "description"]
ALLOWED_VISIBILITY = {"public", "protected", "private"}
ALLOWED_KIND = {"addon", "scenario", "profile", "stack"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CatalogValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogValidationError(message)


def validate_catalog(path: Path) -> int:
    require(path.exists(), f"catalog not found: {path}")

    data = yaml.safe_load(path.read_text())
    require(isinstance(data, dict), "catalog must be a YAML object")
    require(data.get("apiVersion") == "catalogs.productive-k3s.io/v1alpha1", "unsupported or missing apiVersion")
    require(data.get("kind") == "ProductiveK3SCatalog", "unsupported or missing kind")

    entries = data.get("entries")
    require(isinstance(entries, list), "entries must be a list")

    ids = set()
    for index, entry in enumerate(entries):
        require(isinstance(entry, dict), f"entry #{index} must be an object")
        for field in REQUIRED_ENTRY_FIELDS:
            require(bool(entry.get(field)), f"entry #{index} missing required field: {field}")

        require(entry["id"] not in ids, f"duplicated entry id: {entry['id']}")
        ids.add(entry["id"])
        require(entry["visibility"] in ALLOWED_VISIBILITY, f"entry {entry['id']} has invalid visibility: {entry['visibility']}")
        require(entry["kind"] in ALLOWED_KIND, f"entry {entry['id']} has invalid kind: {entry['kind']}")

        artifact = entry.get("artifact", {})
        if entry["visibility"] == "public":
            require(bool(artifact.get("url")), f"public entry {entry['id']} must expose artifact.url")
        elif not artifact.get("url"):
            commercial = entry.get("commercial", {})
            require(bool(commercial.get("url")), f"protected/private entry {entry['id']} must expose artifact.url or commercial.url")

        if artifact.get("url"):
            require(bool(SHA256_RE.fullmatch(str(artifact.get("sha256", "")))), f"entry {entry['id']} must expose artifact.sha256")
            bom = entry.get("bom", {})
            require(bool(bom.get("url")) and bom.get("embeddedPath") == "bom.json", f"entry {entry['id']} must expose bom.url and embedded bom.json")
            require(bool(SHA256_RE.fullmatch(str(bom.get("sha256", "")))), f"entry {entry['id']} must expose bom.sha256")

    return len(entries)


def main() -> None:
    if len(sys.argv) != 2:
        print("ERROR: usage: validate_catalog.py <catalog.yaml>", file=sys.stderr)
        raise SystemExit(1)
    try:
        count = validate_catalog(Path(sys.argv[1]))
    except CatalogValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"OK: {count} entries validated")


if __name__ == "__main__":
    main()
