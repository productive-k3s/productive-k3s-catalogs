#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys


def sync_catalog(root: Path) -> Path:
    source_dir = root / "catalogs"
    source_index = source_dir / "index.yaml"
    target_dir = root / "docs" / "src" / "catalogs"
    if not source_index.exists():
        raise FileNotFoundError(f"catalog source not found: {source_index}")
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    return target_dir / "index.yaml"


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
