"""The PEW workspace guard fails CLOSED (2026-09-16).

Observed that morning on M2: the service answered /health from the
canonical checkout with base_sha "" and main_worktree false, because the
scheduled task's context had no git on PATH and every _git() call returned
"". A guard that answers "not canonical" when it cannot run git is a label,
not a property. Controls:

    positive   a linked worktree (this test's own) is known and allowed
    negative   git absent -> workspace_known False -> refused, with the
               reason in the message
    cheat      the read-only override still opens it, and says so in the
               receipt, so an override can never be invisible
    canonical  the main worktree is still refused (the original rule)
"""
import os
from pathlib import Path

import pytest

from ew import workspace


def test_positive_this_worktree_is_known_and_allowed():
    r = workspace.receipt()
    assert r["workspace_known"] is True
    assert r["base_sha"] and len(r["base_sha"]) == 40
    if not r["main_worktree"]:
        assert workspace.assert_not_canonical("test")["base_sha"] == r["base_sha"]


def test_negative_git_absent_is_refused_not_admitted(monkeypatch):
    monkeypatch.setattr(workspace, "_git", lambda *a, **k: "")
    r = workspace.receipt()
    assert r["workspace_known"] is False
    assert r["main_worktree"] is False, "the old answer, which is why it must not be trusted alone"
    monkeypatch.delenv("EW_ALLOW_CANONICAL", raising=False)
    with pytest.raises(workspace.CanonicalCheckoutRefused) as ei:
        workspace.assert_not_canonical("serve PEW")
    assert "git did not answer" in str(ei.value)


def test_cheat_override_admits_and_is_recorded(monkeypatch):
    monkeypatch.setattr(workspace, "_git", lambda *a, **k: "")
    monkeypatch.setenv("EW_ALLOW_CANONICAL", "1")
    r = workspace.assert_not_canonical("inspect")
    assert r["allow_canonical_override"] is True
    assert r["workspace_known"] is False


def test_canonical_main_worktree_is_still_refused(monkeypatch):
    def fake_git(*args, cwd=None):
        if args[:2] == ("rev-parse", "--git-dir"):
            return ".git"
        if args[:2] == ("rev-parse", "--git-common-dir"):
            return ".git"
        if args == ("rev-parse", "HEAD"):
            return "a" * 40
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return "main"
        return ""
    monkeypatch.setattr(workspace, "_git", fake_git)
    monkeypatch.delenv("EW_ALLOW_CANONICAL", raising=False)
    r = workspace.receipt()
    assert r["workspace_known"] is True and r["main_worktree"] is True
    with pytest.raises(workspace.CanonicalCheckoutRefused) as ei:
        workspace.assert_not_canonical("serve PEW")
    assert "CANONICAL checkout" in str(ei.value)
