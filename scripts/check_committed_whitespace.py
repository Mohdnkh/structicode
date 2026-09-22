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


def select_revision_range(
    event: str,
    *,
    local_base: str | None = None,
    local_head: str | None = None,
    before: str = "",
    after: str = "",
    pr_base_sha: str = "",
    pr_head_sha: str = "",
    default_base: str = "",
) -> tuple[str, str, str]:
    """Select the authoritative committed range without reading GitHub itself."""
    if local_base and local_head:
        return local_base, local_head, "..."
    if event == "pull_request":
        if not pr_base_sha or not pr_head_sha:
            raise ValueError("Pull-request base/head SHAs are required")
        return pr_base_sha, pr_head_sha, "..."
    if event == "push":
        if not after:
            raise ValueError("Push after SHA is required")
        if before and set(before) != {"0"}:
            return before, after, ".."
        if default_base:
            return default_base, after, "..."
        return f"{after}^", after, ".."
    head = after or "HEAD"
    return f"{head}^", head, ".."


def committed_range(base: str | None, head: str | None) -> tuple[str, str, str]:
    event = os.getenv("GITHUB_EVENT_NAME", "")
    after = os.getenv("STRUCTICODE_CI_EVENT_AFTER", os.getenv("GITHUB_SHA", "HEAD"))
    before = os.getenv("STRUCTICODE_CI_EVENT_BEFORE", "")
    pr_base_sha = os.getenv("STRUCTICODE_CI_PR_BASE_SHA", "")
    pr_head_sha = os.getenv("STRUCTICODE_CI_PR_HEAD_SHA", "")
    default_base = os.getenv("STRUCTICODE_CI_DEFAULT_BASE_REF", "")
    selected = select_revision_range(
        event, local_base=base, local_head=head, before=before, after=after,
        pr_base_sha=pr_base_sha, pr_head_sha=pr_head_sha, default_base=default_base,
    )
    if event == "push" and selected[2] == "..." and selected[0] == default_base:
        try:
            selected = (git("merge-base", resolve_ref(default_base), selected[1]), selected[1], "...")
        except (RuntimeError, subprocess.CalledProcessError):
            pass
    return selected


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
