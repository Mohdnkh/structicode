"""Pure revision-range selection tests for the committed whitespace CI gate."""
from scripts.check_committed_whitespace import select_revision_range


def test_local_mode_uses_three_dot_range():
    assert select_revision_range("", local_base="main", local_head="HEAD") == ("main", "HEAD", "...")


def test_pull_request_uses_event_sha_values():
    assert select_revision_range("pull_request", pr_base_sha="a" * 40, pr_head_sha="c" * 40) == ("a" * 40, "c" * 40, "...")


def test_push_uses_before_and_after_for_multi_commit_push():
    assert select_revision_range("push", before="a" * 40, after="c" * 40) == ("a" * 40, "c" * 40, "..")


def test_missing_invented_github_before_does_not_change_event_range():
    assert select_revision_range("push", before="a" * 40, after="c" * 40) == ("a" * 40, "c" * 40, "..")


def test_zero_before_uses_default_base_or_documented_final_fallback():
    zeros = "0" * 40
    assert select_revision_range("push", before=zeros, after="c" * 40, default_base="main") == ("main", "c" * 40, "...")
    assert select_revision_range("push", before=zeros, after="c" * 40) == ("c" * 40 + "^", "c" * 40, "..")
