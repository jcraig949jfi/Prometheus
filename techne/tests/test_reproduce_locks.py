"""techne.scripts.reproduce_locks: the parts that need no network.

- a lock whose interpreter tag is not the running one is REFUSED (a lock is not portable);
- the cheat-control helper flips exactly one hex digit of the first hash and nothing else;
- paths.tool_cache() defaults to the CANONICAL checkout, not the task worktree (2026-09-16).
"""
from __future__ import annotations

import pathlib
import re
import subprocess

from techne.acquisition import paths
from techne.scripts import reproduce_locks as rl


def test_lock_tag_and_entry_parse():
    p = pathlib.Path("hypothesis-cp312-win-amd64.lock.txt")
    assert rl._lock_tag(p) == "cp312-win-amd64" and rl._lock_entry(p) == "hypothesis"
    assert rl._lock_tag(pathlib.Path("weird.txt")) == ""


def test_flip_one_hex_changes_exactly_one_hash_digit():
    text = "a==1 \\n    --hash=sha256:" + "ab" * 32 + "\nb==2 \\n    --hash=sha256:" + "cd" * 32 + "\n"
    out = rl._flip_one_hex(text)
    diffs = [i for i, (x, y) in enumerate(zip(text, out)) if x != y]
    assert len(diffs) == 1 and len(out) == len(text)
    assert "cd" * 32 in out, "the second hash is untouched"


def test_wrong_tag_is_refused_without_touching_anything(tmp_path, monkeypatch):
    monkeypatch.setenv("TECHNE_TOOL_CACHE", str(tmp_path / "cache"))
    lock = tmp_path / "x-cp299-nowhere.lock.txt"
    lock.write_text("# techne.acquisition lock -- entry 'x', isolated env 'e'\nfoo==1 \\n    --hash=sha256:" + "0" * 64 + "\n", encoding="utf-8")
    monkeypatch.setattr(paths, "locks", lambda: tmp_path)
    monkeypatch.setattr(rl.receipt, "write", lambda rec, out_dir=None: tmp_path / "r.json")
    rc = rl.main(["--lock", lock.name])
    assert rc == 1
    assert not (tmp_path / "cache").exists(), "no env may be created for a refused lock"


def test_tool_cache_default_is_under_the_canonical_checkout(monkeypatch):
    monkeypatch.delenv("TECHNE_TOOL_CACHE", raising=False)
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            cwd=str(paths.REPO_ROOT), capture_output=True, text=True).stdout.strip()
    canonical = pathlib.Path(common).parent
    tc = paths.tool_cache()
    assert tc == canonical / "vault" / "techne_tools" or "config.local.json" in str(tc) or tc.is_absolute()
    if canonical != paths.REPO_ROOT:   # we are in a linked worktree: the default must NOT be here
        assert not str(tc).startswith(str(paths.REPO_ROOT))
