#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    source = root / "catalogs" / "index.yaml"
    target = root / "docs" / "catalogs" / "index.yaml"

    if not source.exists():
      fail(f"catalog source not found: {source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"Synced catalog into docs: {target}")


if __name__ == "__main__":
    main()
