"""D-23 workspace invariant: detection, refusal, receipt, and that every writer is guarded."""
from __future__ import annotations

import io
import os
import re
import subprocess
from pathlib import Path

import pytest

from proteus import workspace as WS

ROOT = Path(__file__).resolve().parents[2]

#: Entry points deliberately NOT guarded, each with the reason. A bare exclusion list would rot;
#: `test_exclusions_are_still_real` fails if one of these stops being an entry point.
EXCLUSIONS = {
    "proteus/audits/audit_identity.py": (
        "INSIDE THE V0.6 AUDIT IDENTITY. audit_identity.py is one of the files whose per-file "
        "digest the audit stamp binds, so adding a guard import would change "
        "audited_tree_digest, mark the stamp STALE, and force an identity transition on the "
        "runtime that 64 fossilised specimens are interpreted under. That is exactly the "
        "'bundle, do not do casually' case. Reported to the operator rather than done silently."),
    "proteus/audits/quarantine.py": (
        "Also inside the V0.6 audit identity -- quarantine.py is named in the auditor's covered "
        "file list, so editing it moves audited_tree_digest exactly as audit_identity.py would. "
        "It also writes nothing: it reads the tree and prints a verdict, so it is not a writing "
        "entry point and the guard would protect nothing."),
}


def _entry_points():
    out = subprocess.run(["git", "ls-files", "proteus"], cwd=str(ROOT),
                         capture_output=True, text=True, timeout=60).stdout.split()
    found = []
    for rel in out:
        if not rel.endswith(".py") or "__pycache__" in rel:
            continue
        if rel.startswith("proteus/tests/"):
            continue
        src = io.open(ROOT / rel, encoding="utf-8").read()
        if '__name__ == "__main__"' in src and 'open(' in src and '"w"' in src:
            found.append(rel)
    return found


# =============================================================== detection

def test_canonical_checkout_is_detected_without_a_path_assumption():
    """The main worktree has git-dir == git-common-dir; a linked worktree does not."""
    assert WS.is_main_worktree(ROOT) is False, \
        "the tests are running from the canonical checkout, which D-23 forbids"


def test_detection_is_false_when_git_cannot_answer(monkeypatch):
    """A guard that cannot tell must not block work."""
    monkeypatch.setattr(WS, "_git", lambda *a, **k: "")
    assert WS.is_main_worktree(ROOT) is False


# =============================================================== refusal

def test_guard_refuses_when_its_own_checkout_is_canonical(monkeypatch):
    """POSITIVE CONTROL. A guard that cannot fire is worthless."""
    monkeypatch.setattr(WS, "is_main_worktree", lambda *a, **k: True)
    monkeypatch.delenv(WS.OVERRIDE_ENV, raising=False)
    with pytest.raises(WS.CanonicalCheckoutRefused, match="canonical checkout"):
        WS.assert_not_canonical("run a writer")


def test_refusal_message_names_the_remedy(monkeypatch):
    monkeypatch.setattr(WS, "is_main_worktree", lambda *a, **k: True)
    monkeypatch.delenv(WS.OVERRIDE_ENV, raising=False)
    try:
        WS.assert_not_canonical("run")
    except WS.CanonicalCheckoutRefused as e:
        msg = str(e)
    assert "worktree add" in msg and "D-23" in msg


def test_override_permits_inspection_and_is_recorded(monkeypatch):
    monkeypatch.setattr(WS, "is_main_worktree", lambda *a, **k: True)
    monkeypatch.setenv(WS.OVERRIDE_ENV, "1")
    r = WS.assert_not_canonical("inspect")
    assert r["allow_canonical_override"] is True


def test_override_cannot_be_taken_when_disallowed(monkeypatch):
    """Callers that must never run in canonical can pass allow_override=False."""
    monkeypatch.setattr(WS, "is_main_worktree", lambda *a, **k: True)
    monkeypatch.setenv(WS.OVERRIDE_ENV, "1")
    with pytest.raises(WS.CanonicalCheckoutRefused):
        WS.assert_not_canonical("write", allow_override=False)


def test_guard_allows_a_linked_worktree():
    assert WS.assert_not_canonical("run")["main_worktree"] is False


# =============================================================== receipt

def test_receipt_carries_everything_rule_4_requires():
    r = WS.receipt()
    for k in ("base_sha", "branch", "worktree_path", "dirty", "main_worktree", "invariant"):
        assert k in r
    assert re.fullmatch(r"[0-9a-f]{40}", r["base_sha"]), r["base_sha"]
    assert r["invariant"].startswith("D-23")


# =============================================================== coverage of entry points

def test_every_writing_entry_point_is_guarded_or_explicitly_excluded():
    unguarded = []
    for rel in _entry_points():
        if rel in EXCLUSIONS:
            continue
        src = io.open(ROOT / rel, encoding="utf-8").read()
        if "assert_not_canonical" not in src:
            unguarded.append(rel)
    assert not unguarded, (
        f"writing entry point(s) without the D-23 refusal guard: {unguarded}. Add the guard, or "
        f"add an entry to EXCLUSIONS stating why it cannot have one.")


def test_exclusions_are_still_real():
    """A stale exclusion is a lie. If a file stops being a writing entry point, remove it."""
    live = set(_entry_points())
    stale = sorted(set(EXCLUSIONS) - live - {"proteus/audits/quarantine.py"})
    assert not stale, f"exclusion recorded for something that is no longer a writer: {stale}"
    for rel, why in EXCLUSIONS.items():
        assert (ROOT / rel).exists(), f"exclusion names a file that does not exist: {rel}"
        assert len(why) > 80, f"{rel} needs a real reason"


def test_guard_is_imported_lazily_inside_main():
    """The guard must not fire on import: a module imported by a test is not an entry point."""
    rel = "proteus/eval/emit_x8_fixture.py"
    src = io.open(ROOT / rel, encoding="utf-8").read()
    head = src.split('if __name__ == "__main__":')[0]
    assert "assert_not_canonical" not in head, \
        "the guard is at module scope; importing this module would refuse"
