"""D-23: the canonical checkout refusal must actually refuse.

The end-to-end version of this test is a trap and I fell into it once: running
an entry point "from the canonical checkout" executes the copy of the code
that LIVES there, which is whatever main last had. That tests the wrong file
and, worse, writes into the canonical tree. The property is therefore tested
by pointing the module's REPO at the canonical path, which is exactly the
state the guard exists to detect.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from herakles import workspace as w

REPO = Path(__file__).resolve().parents[2]


def _canonical_path():
    """The repository's MAIN worktree, asked of git rather than assumed."""
    out = subprocess.run(["git", "worktree", "list", "--porcelain"],
                         cwd=str(REPO), capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if line.startswith("worktree "):
            return Path(line.split(" ", 1)[1])
    return None


def test_the_tests_themselves_run_in_a_linked_worktree():
    """If this fails, the suite is running where no work should happen."""
    assert not w.is_main_worktree(REPO), (
        "tests are running in the canonical checkout; D-23 forbids work there")


def test_main_and_linked_worktrees_are_distinguished():
    canonical = _canonical_path()
    assert canonical is not None
    assert w.is_main_worktree(canonical) is True
    assert w.is_main_worktree(REPO) is False


def test_assert_not_canonical_refuses_for_the_canonical_repo(monkeypatch):
    monkeypatch.setattr(w, "REPO", _canonical_path())
    monkeypatch.delenv("HERAKLES_ALLOW_CANONICAL", raising=False)
    with pytest.raises(w.CanonicalCheckoutRefused) as e:
        w.assert_not_canonical("write a result file")
    msg = str(e.value)
    assert "canonical checkout" in msg
    assert "worktree add" in msg, "the refusal must say what to do instead"


def test_the_override_is_read_only_and_is_recorded(monkeypatch):
    monkeypatch.setattr(w, "REPO", _canonical_path())
    monkeypatch.setenv("HERAKLES_ALLOW_CANONICAL", "1")
    r = w.assert_not_canonical("read-only inspection")
    assert r["allow_canonical_override"] is True
    assert r["main_worktree"] is True


def test_receipt_carries_what_a_receipt_must_carry():
    r = w.receipt(REPO)
    for field in ("base_sha", "branch", "worktree_path", "dirty",
                  "main_worktree"):
        assert field in r, field
    assert len(r["base_sha"]) == 40


@pytest.mark.parametrize("module", [
    "herakles/evca/tools/make_golden.py",
    "herakles/evca/c1e/run_c1e.py",
    "herakles/evca/c1e/compare_c3_2.py",
    "herakles/ca_stream/run_alpha.py",
])
def test_every_writing_entry_point_is_guarded(module):
    src = (REPO / module).read_text(encoding="utf-8")
    assert "assert_not_canonical" in src, module


def test_the_pure_reader_is_deliberately_not_guarded():
    """c3_null_check writes nothing and another seat runs it.

    Guarding a pure reader would block Archaeon from a diagnostic for a reason
    that has nothing to do with them. Asserted so the omission is a decision
    on the record rather than an oversight someone later "fixes".
    """
    src = (REPO / "herakles/evca/c3_null_check.py").read_text(encoding="utf-8")
    assert "assert_not_canonical" not in src
    assert '"w"' not in src and "'w'" not in src, "it must remain a pure reader"
