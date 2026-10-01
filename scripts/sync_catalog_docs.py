#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys


def sync_catalog(root: Path) -> Path:
    source = root / "catalogs" / "index.yaml"
    target = root / "docs" / "src" / "catalogs" / "index.yaml"
    if not source.exists():
        raise FileNotFoundError(f"catalog source not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    try:
        target = sync_catalog(root)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"Synced catalog into docs: {target}")


if __name__ == "__main__":
    main()
