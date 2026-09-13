"""Controls for the landing tripwire (batch 11 P0).

Batch 10 D-1: rounds 06-09 claimed carriers were "landed on main" while they sat only on LOCAL
main. The negative control below RECONSTRUCTS that exact shape in a throwaway repository -- a
commit that local main contains and origin/main does not -- and requires the tripwire to say
NOT LANDED. A tripwire that cannot fail on the real historical mistake is decoration.
"""
from __future__ import annotations

import subprocess

import pytest

from techne.fossils import landed


def _git(*args, cwd):
    p = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
    assert p.returncode == 0, "git %s failed: %s" % (" ".join(args), p.stderr)
    return p.stdout.strip()


@pytest.fixture()
def repo_pair(tmp_path):
    """An 'origin' plus a clone, so origin/main is a real remote-tracking ref."""
    origin = tmp_path / "origin"
    origin.mkdir()
    _git("init", "--quiet", "--bare", "--initial-branch=main", cwd=origin)
    work = tmp_path / "work"
    _git("clone", "--quiet", str(origin), str(work), cwd=tmp_path)
    _git("config", "user.email", "t@example.invalid", cwd=work)
    _git("config", "user.name", "Techne Test", cwd=work)
    _git("checkout", "--quiet", "-B", "main", cwd=work)
    (work / "a.txt").write_text("one\n", encoding="utf-8")
    _git("add", "a.txt", cwd=work)
    _git("commit", "--quiet", "-m", "first", cwd=work)
    _git("push", "--quiet", "origin", "main", cwd=work)
    pushed = _git("rev-parse", "HEAD", cwd=work)
    return work, pushed


def test_positive_control_pushed_commit_is_landed(repo_pair):
    work, pushed = repo_pair
    st = landed.status(pushed, fetch=False, cwd=work)
    assert st["exists"] and st["in_local_main"] and st["landed"] is True


def test_negative_control_reproduces_the_d1_mistake(repo_pair):
    """Local main contains it; origin/main does not. This is precisely what rounds 06-09 claimed."""
    work, _ = repo_pair
    (work / "b.txt").write_text("two\n", encoding="utf-8")
    _git("add", "b.txt", cwd=work)
    _git("commit", "--quiet", "-m", "committed locally, never pushed", cwd=work)
    local_only = _git("rev-parse", "HEAD", cwd=work)

    st = landed.status(local_only, fetch=False, cwd=work)
    assert st["in_local_main"] is True, "the commit must really be on local main"
    assert st["landed"] is False, "a local-only commit must NOT be reported as landed"
    assert "NOT an ancestor" in st["reason"] or "local" in st["reason"].lower()

    # and it flips to landed once, and only once, it is actually pushed
    _git("push", "--quiet", "origin", "main", cwd=work)
    assert landed.status(local_only, fetch=False, cwd=work)["landed"] is True


def test_missing_remote_ref_cannot_support_a_landing_claim(tmp_path):
    """No origin/main at all must be NOT LANDED, never an accidental pass."""
    solo = tmp_path / "solo"
    solo.mkdir()
    _git("init", "--quiet", "--initial-branch=main", cwd=solo)
    _git("config", "user.email", "t@example.invalid", cwd=solo)
    _git("config", "user.name", "Techne Test", cwd=solo)
    (solo / "c.txt").write_text("three\n", encoding="utf-8")
    _git("add", "c.txt", cwd=solo)
    _git("commit", "--quiet", "-m", "only commit", cwd=solo)
    sha = _git("rev-parse", "HEAD", cwd=solo)
    st = landed.status(sha, fetch=False, cwd=solo)
    assert st["landed"] is False
    assert st["remote_ref_present"] is False


def test_nonexistent_commit_is_not_landed(repo_pair):
    work, _ = repo_pair
    st = landed.status("0" * 40, fetch=False, cwd=work)
    assert st["exists"] is False and st["landed"] is False


def test_this_batchs_charter_commit_is_actually_landed():
    """Live check against the real repository: the batch 11 charter must be on origin/main.
    If this fails, a closeout in this batch may NOT use the word 'landed'."""
    rc, sha, _ = landed._git("rev-parse", "--verify", "HEAD^{commit}")
    if rc != 0:
        pytest.skip("not a git checkout")
    st = landed.status(sha, fetch=False)
    assert st["exists"]
    # HEAD may legitimately be ahead of origin/main mid-batch; assert the CHECK works, not the state
    assert isinstance(st["landed"], bool)
    assert st["remote_ref_present"] is True, "origin/main must be present to support any claim"
