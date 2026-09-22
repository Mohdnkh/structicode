"""Check whitespace errors in the committed revision range used by CI."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def resolve_ref(ref: str) -> str:
    for candidate in (ref, f"origin/{ref}"):
        try:
            git("rev-parse", "--verify", candidate)
            return candidate
        except subprocess.CalledProcessError:
            continue
    raise RuntimeError(f"Unable to resolve revision: {ref}")


def committed_range(base: str | None, head: str | None) -> tuple[str, str, str]:
    if base and head:
        return resolve_ref(base), resolve_ref(head), "..."
    event = os.getenv("GITHUB_EVENT_NAME", "")
    sha = os.getenv("GITHUB_SHA", "HEAD")
    if event == "pull_request":
        return resolve_ref(os.environ["GITHUB_BASE_REF"]), resolve_ref(os.getenv("GITHUB_HEAD_REF", sha)), "..."
    before = os.getenv("GITHUB_BEFORE", "")
    if before and set(before) != {"0"}:
        return resolve_ref(before), resolve_ref(sha), ".."
    return resolve_ref(f"{sha}^"), resolve_ref(sha), ".."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    parser.add_argument("--head")
    args = parser.parse_args()
    base, head, operator = committed_range(args.base, args.head)
    revision_range = f"{base}{operator}{head}"
    print(f"Checking committed whitespace range: {revision_range}")
    result = subprocess.run(["git", "diff", "--check", revision_range])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
