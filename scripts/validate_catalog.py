#!/usr/bin/env python3
import sys
import re
from pathlib import Path
import yaml

REQUIRED_ENTRY_FIELDS = ["id", "name", "kind", "visibility", "category", "description"]
ALLOWED_VISIBILITY = {"public", "protected", "private"}
ALLOWED_KIND = {"addon", "scenario", "profile", "stack"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SOURCE_REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


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
    compatibility_entries = 0
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
            compatibility = entry.get("compatibility")
            if compatibility is not None:
                compatibility_entries += 1
                require(bool(SOURCE_REVISION_RE.fullmatch(str(entry.get("sourceRevision", "")))), f"entry {entry['id']} must expose an immutable sourceRevision")
                validate_compatibility(entry["id"], entry["kind"], compatibility)

    require(compatibility_entries in {0, len(entries)}, "catalog cannot mix legacy and compatibility-aware entries")
    if compatibility_entries:
        metadata = data.get("metadata")
        require(isinstance(metadata, dict), "compatibility-aware catalog metadata is required")
        require_semver(metadata.get("version"), "metadata.version")

    return len(entries)


def require_semver(value: object, field: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v?([0-9]+)\.([0-9]+)\.([0-9]+)", str(value or ""))
    require(bool(match), f"{field} must be a stable semantic version")
    return tuple(int(part) for part in match.groups())


def validate_window(owner: dict, minimum_key: str, maximum_key: str, prefix: str) -> None:
    require(isinstance(owner, dict), f"{prefix} must be an object")
    minimum = require_semver(owner.get(minimum_key), f"{prefix}.{minimum_key}")
    maximum = require_semver(owner.get(maximum_key), f"{prefix}.{maximum_key}")
    require(minimum < maximum, f"{prefix} must define a non-empty version window")


def validate_compatibility(entry_id: str, kind: str, compatibility: object) -> None:
    require(isinstance(compatibility, dict), f"entry {entry_id} compatibility must be an object")
    requires = compatibility.get("requires")
    require(isinstance(requires, dict), f"entry {entry_id} compatibility.requires is required")
    if kind == "profile":
        infra = requires.get("infra")
        require(isinstance(infra, dict) and infra.get("contract") == "profile/v1", f"entry {entry_id} requires supported Infra contract profile/v1")
        validate_window(infra, "minEngineVersion", "maxEngineVersionExclusive", f"entry {entry_id} Infra requirement")
        validate_window(requires.get("core"), "minVersion", "maxVersionExclusive", f"entry {entry_id} Core requirement")
        return
    core = requires.get("core")
    require(isinstance(core, dict) and core.get("contract") == "artifact/v1", f"entry {entry_id} requires supported Core contract artifact/v1")
    validate_window(core, "minVersion", "maxVersionExclusive", f"entry {entry_id} Core requirement")
    kubernetes = requires.get("kubernetes")
    distros = kubernetes.get("distros") if isinstance(kubernetes, dict) else None
    require(isinstance(distros, list) and bool(distros), f"entry {entry_id} requires Kubernetes distros")
    require(set(distros).issubset({"k3s", "rke2"}), f"entry {entry_id} declares an unsupported Kubernetes distro")


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
