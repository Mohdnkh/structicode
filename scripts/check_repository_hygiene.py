"""Fail when generated, secret, or local-only artifacts are tracked."""
from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath


def forbidden(path: str) -> bool:
    parts = PurePosixPath(path).parts
    basename = PurePosixPath(path).name
    if any(part in {"node_modules", "dist", "__pycache__", ".pytest_cache"} for part in parts):
        return True
    if path.endswith((".pyc", ".pyo", ".pyd")):
        return True
    if PurePosixPath(path).name == "report.pdf" or path.endswith((".db", ".sqlite", ".sqlite3", ".pkl")):
        return True
    if basename.startswith(".env") and path != ".env.example":
        return True
    return False


def main() -> int:
    result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True)
    tracked = [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    violations = [path for path in tracked if forbidden(path)]
    if violations:
        print("Tracked generated or local-only artifacts detected:")
        print("\n".join(sorted(violations)))
        return 1
    print(f"Repository hygiene check passed ({len(tracked)} tracked files inspected).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
