#!/usr/bin/env python3
import sys
import re
from pathlib import Path
import yaml

REQUIRED_ENTRY_FIELDS = ["id", "name", "kind", "visibility", "category", "description"]
ALLOWED_VISIBILITY = {"public", "protected", "private"}
ALLOWED_KIND = {"addon", "scenario", "profile", "stack"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate_catalog.py <catalog.yaml>")

    path = Path(sys.argv[1])
    if not path.exists():
        fail(f"catalog not found: {path}")

    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        fail("catalog must be a YAML object")

    if data.get("apiVersion") != "catalogs.productive-k3s.io/v1alpha1":
        fail("unsupported or missing apiVersion")

    if data.get("kind") != "ProductiveK3SCatalog":
        fail("unsupported or missing kind")

    entries = data.get("entries")
    if not isinstance(entries, list):
        fail("entries must be a list")

    ids = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"entry #{index} must be an object")

        for field in REQUIRED_ENTRY_FIELDS:
            if not entry.get(field):
                fail(f"entry #{index} missing required field: {field}")

        if entry["id"] in ids:
            fail(f"duplicated entry id: {entry['id']}")
        ids.add(entry["id"])

        if entry["visibility"] not in ALLOWED_VISIBILITY:
            fail(f"entry {entry['id']} has invalid visibility: {entry['visibility']}")

        if entry["kind"] not in ALLOWED_KIND:
            fail(f"entry {entry['id']} has invalid kind: {entry['kind']}")

        artifact = entry.get("artifact", {})
        if entry["visibility"] == "public" and not artifact.get("url"):
            fail(f"public entry {entry['id']} must expose artifact.url")

        if entry["visibility"] != "public" and not artifact.get("url"):
            commercial = entry.get("commercial", {})
            if not commercial.get("url"):
                fail(f"protected/private entry {entry['id']} must expose artifact.url or commercial.url")

        if artifact.get("url"):
            if not SHA256_RE.fullmatch(str(artifact.get("sha256", ""))):
                fail(f"entry {entry['id']} must expose artifact.sha256")
            bom = entry.get("bom", {})
            if not bom.get("url") or bom.get("embeddedPath") != "bom.json":
                fail(f"entry {entry['id']} must expose bom.url and embedded bom.json")
            if not SHA256_RE.fullmatch(str(bom.get("sha256", ""))):
                fail(f"entry {entry['id']} must expose bom.sha256")

    print(f"OK: {len(entries)} entries validated")


if __name__ == "__main__":
    main()
