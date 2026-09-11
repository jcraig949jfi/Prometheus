"""D-23: the seat refuses to do mutating work from the canonical checkout.

The detection is path-free on purpose. A check written against
`F:\\Prometheus` as a string passes on a clone, on another machine, and on the
day somebody moves the canonical checkout -- which is precisely when it has to
hold. `git rev-parse --git-dir` equals `--git-common-dir` only in a
repository's MAIN worktree; in a linked worktree the git-dir lives under
`<common>/worktrees/<name>` and the two differ.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
if str(VIVARIUM) not in sys.path:
    sys.path.insert(0, str(VIVARIUM))

from viv import workspace as _ws                            # noqa: E402


def _git_ok():
    try:
        return subprocess.run(["git", "--version"], capture_output=True,
                              timeout=20).returncode == 0
    except Exception:                                       # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _git_ok(), reason="git unavailable")


def test_this_worktree_is_not_the_canonical_checkout():
    """If this ever fails, the suite is running somewhere it must not."""
    assert _ws.is_main_worktree() is False
    assert _ws.receipt()["main_worktree"] is False


def test_the_canonical_checkout_is_detected_as_canonical():
    """The positive control. A guard that never fires has not been shown to
    detect anything, and this is the one directory it must recognise."""
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=str(_ws.REPO), capture_output=True, text=True).stdout.strip()
    if not common:
        pytest.skip("cannot resolve the common git dir here")
    canonical = Path(common).parent           # <canonical>/.git -> <canonical>
    assert _ws.is_main_worktree(canonical) is True


def test_assert_not_canonical_passes_here_and_returns_the_receipt():
    r = _ws.assert_not_canonical("run the suite", allow_override=False)
    assert r["main_worktree"] is False
    for key in ("base_sha", "branch", "detached", "worktree_path", "dirty"):
        assert key in r, key
    assert len(r["base_sha"]) == 40


def test_the_receipt_reports_detached_separately_from_branch():
    """Rule 6 wants a long-lived process on a DETACHED pinned SHA, and 'HEAD'
    as a branch name is easy to read past."""
    r = _ws.receipt()
    assert r["detached"] == (r["branch"] == "HEAD")


def test_an_unanswerable_question_is_not_a_refusal(monkeypatch):
    """git missing or failing must not stop a consumer from starting. The
    receipt records the uncertainty; the guard does not invent a verdict."""
    monkeypatch.setattr(_ws, "_git", lambda *a, **k: "")
    assert _ws.is_main_worktree() is False
    assert _ws.assert_not_canonical("start", allow_override=False)


def test_the_override_cannot_unlock_a_write(monkeypatch):
    """VIV_ALLOW_CANONICAL is for read-only inspection. The consumer and the
    queue writer pass allow_override=False, so an operator who sets it still
    cannot run them from the canonical checkout -- an override that unlocked
    the write would be a hole with a polite name."""
    monkeypatch.setattr(_ws, "is_main_worktree", lambda *a, **k: True)
    monkeypatch.setenv(_ws.OVERRIDE_ENV, "1")
    with pytest.raises(_ws.CanonicalCheckoutRefused):
        _ws.assert_not_canonical("run the consumer", allow_override=False)
    # ... while inspection is permitted.
    assert _ws.assert_not_canonical("inspect", allow_override=True)


def test_the_refusal_names_the_way_out():
    """A refusal that does not say what to do instead gets worked around."""
    import os
    real = _ws.is_main_worktree
    try:
        _ws.is_main_worktree = lambda *a, **k: True
        os.environ.pop(_ws.OVERRIDE_ENV, None)
        with pytest.raises(_ws.CanonicalCheckoutRefused) as e:
            _ws.assert_not_canonical("run the consumer", allow_override=False)
        msg = str(e.value)
        assert "worktree add" in msg
        assert "D-23" in msg
    finally:
        _ws.is_main_worktree = real


def test_the_write_entry_points_all_carry_the_guard():
    """cli.run, cli.tick and cli.enqueue write; a new one that forgets the
    guard is the failure this test exists to catch."""
    src = (VIVARIUM / "viv" / "cli.py").read_text(encoding="utf-8")
    for fn in ("def cmd_run(", "def cmd_tick(", "def cmd_enqueue("):
        i = src.index(fn)
        body = src[i:i + 900]
        assert "assert_not_canonical" in body, fn
        assert "allow_override=False" in body, fn
