"""D-23: the canonical-checkout refusal and the workspace receipt."""
import subprocess

import pytest

from archaeon import workspace as W


def _init_repo(path):
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "t"], check=True)
    (path / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "f.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", "init"], check=True)


def test_main_worktree_is_detected_and_a_linked_worktree_is_not(tmp_path):
    main = tmp_path / "canonical"; main.mkdir()
    _init_repo(main)
    linked = tmp_path / "wt-seat"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", str(linked), "-b", "seat/task"], check=True)
    assert W.is_main_worktree(main) is True
    assert W.is_main_worktree(linked) is False
    r = W.receipt(linked)
    assert r["branch"] == "seat/task" and len(r["base_sha"]) == 40 and r["dirty"] is False and r["main_worktree"] is False
    (linked / "f.txt").write_text("y", encoding="utf-8")
    assert W.receipt(linked)["dirty"] is True


def test_refusal_from_the_canonical_checkout_and_the_read_only_override(tmp_path, monkeypatch):
    main = tmp_path / "canonical"; main.mkdir()
    _init_repo(main)
    monkeypatch.setattr(W, "REPO", main)
    monkeypatch.delenv("ARCHAEON_ALLOW_CANONICAL", raising=False)
    with pytest.raises(W.CanonicalCheckoutRefused):
        W.assert_not_canonical("tick")
    monkeypatch.setenv("ARCHAEON_ALLOW_CANONICAL", "1")
    assert W.assert_not_canonical("inspect")["allow_canonical_override"] is True
    with pytest.raises(W.CanonicalCheckoutRefused):
        W.assert_not_canonical("write the queue", allow_override=False)     # queue writes never unlock


def test_this_checkout_is_a_linked_worktree_not_the_canonical_one():
    """Archaeon itself must never be running from the canonical checkout."""
    assert W.is_main_worktree() is False, W.receipt()
