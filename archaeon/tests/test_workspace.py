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


def test_repo_id_is_the_root_commit_and_separates_same_named_repositories(tmp_path):
    """Hermes HERMES-32 (#118): two repositories with the same branch name,
    the same worktree role and the same file names but different histories
    are EXACTLY distinguishable by their root commit; two worktrees of ONE
    repository share it (positive control); a clone shares it too, so the
    field names the history, not the machine (cheat control: a copy that
    kept the name but not the history does not pass as the same repo)."""
    a = tmp_path / "a"; a.mkdir(); _init_repo(a)
    b = tmp_path / "b"; b.mkdir(); _init_repo(b)          # same name pattern...
    # ...but a different history. NOTE (measured 2026-09-11): two repos initialised
    # with identical content, author, message and second have IDENTICAL root SHAs,
    # so repo_id names the HISTORY, not the directory; an identical history is the
    # same repository for every purpose this field serves.
    (b / "g.txt").write_text("different history", encoding="utf-8")
    subprocess.run(["git", "-C", str(b), "add", "g.txt"], check=True)
    subprocess.run(["git", "-C", str(b), "commit", "-q", "--amend", "-m", "init b"], check=True)
    ra, rb = W.receipt(a), W.receipt(b)
    assert len(ra["repo_id"]) == 40 and ra["repo_id"] != rb["repo_id"]
    linked = tmp_path / "a-wt"
    subprocess.run(["git", "-C", str(a), "worktree", "add", "-q", str(linked), "-b", "seat/task"], check=True)
    assert W.receipt(linked)["repo_id"] == ra["repo_id"]
    clone = tmp_path / "a-clone"
    subprocess.run(["git", "clone", "-q", str(a), str(clone)], check=True)
    assert W.receipt(clone)["repo_id"] == ra["repo_id"]
    assert W.receipt(clone)["repo_id"] != rb["repo_id"]


def test_the_configured_sfe_ledger_exists_on_this_host():
    """2026-09-11: the pinned tick worktree fell through to the in-repo
    default ledger path, which does not exist in a linked worktree, and read
    0 fossils for 51 ticks while reporting CONFORMANT. The eye must be
    checked as a property: whatever path resolution lands on must be a file.
    In a linked worktree with no ARCHAEON_SFE_DB and no config.local.json
    sfe_db this test FAILS by design -- that is the deployment defect."""
    import os
    from pathlib import Path
    from archaeon import fossils
    path = Path(fossils._default_sfe_db())
    configured = bool(os.environ.get("ARCHAEON_SFE_DB")) or (Path(fossils.__file__).resolve().parent / "config.local.json").exists()
    assert path.exists(), (
        "the resolved SFE ledger {} does not exist ({}); write archaeon/config.local.json with sfe_db = the engine's --db "
        "(OPERATIONS.md, Start (deployed))".format(path, "configured" if configured else "no ARCHAEON_SFE_DB and no config.local.json: in-repo default in a linked worktree"))
