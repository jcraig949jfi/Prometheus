"""The base role tests its own claims (WORKING_CONTRACT.md s10).

Every mandatory artifact path is committable, every inherited file exists
and is pure ASCII, every role carries the banner, every issued manifest's
hashes match the files, and the executable invariants can be satisfied by
the supported harness. A failure here is a defect in the constitution.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest

from archaeon import workspace as W

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "roles" / "base-role"
BANNER = "> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md"
PRIMARY = ("RESPONSIBILITIES.md", "ROLE.md", "BOOTSTRAP.md", "CHARTER.md")
MANDATORY = ("journal/2026-01-01.md", "INBOX_SOMEONE_TOPIC_2026-01-01.md", "prompts/2026-01-01_topic/PROMPT.md",
             "BACKLOG_H0H5.md", "STATUS.md")


def _roles():
    return sorted(p for p in (REPO / "roles").iterdir() if p.is_dir() and p.name != "base-role")


def _ignored(path: str) -> bool:
    r = subprocess.run(["git", "check-ignore", "-q", path], cwd=str(REPO), capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def test_every_mandatory_artifact_path_is_committable_for_every_seat():
    """Vivarium aee89ff8b: `journal/` ignored the journals the base role mandated, for all 27 seats."""
    bad = []
    for role in _roles():
        for rel in MANDATORY:
            p = "roles/{}/{}".format(role.name, rel)
            if _ignored(p):
                bad.append(p)
    assert not bad, "gitignored mandatory artifact paths: {}".format(bad[:8])


def test_base_role_files_exist_and_are_pure_ascii():
    for name in ("RESPONSIBILITIES.md", "WORKING_CONTRACT.md", "NORTH_STAR.md", "README.md", "INHERITANCE.md"):
        f = BASE / name
        assert f.exists(), name
        raw = f.read_bytes()
        non_ascii = [i for i, b in enumerate(raw) if b > 0x7F]
        assert not non_ascii, "{} has non-ASCII bytes at {}".format(name, non_ascii[:5])
    assert "PROMETHEUS NORTH STAR" in (BASE / "NORTH_STAR.md").read_text(encoding="utf-8")


def test_every_role_carries_the_inheritance_banner_on_a_primary_document():
    missing = []
    for role in _roles():
        docs = [role / n for n in PRIMARY if (role / n).exists()] or sorted(role.glob("CHARTER*.md")) + sorted(role.glob("ROLE*.md"))
        if not docs:
            missing.append(role.name + " (no primary document)"); continue
        if not any(BANNER in d.read_text(encoding="utf-8", errors="replace") for d in docs):
            missing.append(role.name)
    assert not missing, missing


def test_issued_manifests_verify_against_their_files():
    """A prompt is what its manifest says it is: sha256 over the committed bytes (LF)."""
    checked = 0
    for manifest in (REPO / "roles" / "Archaeon" / "prompts").glob("*/MANIFEST.md"):
        text = manifest.read_text(encoding="utf-8")
        for m in re.finditer(r"^- (\S+)\s+sha256:([0-9a-f]{64})", text, flags=re.M):
            f = manifest.parent / m.group(1)
            if not f.exists():
                continue
            blob = subprocess.run(["git", "show", "HEAD:{}".format(f.relative_to(REPO).as_posix())], cwd=str(REPO),
                                  capture_output=True, timeout=30).stdout
            if not blob:
                continue                                   # not committed yet in this tree
            assert hashlib.sha256(blob).hexdigest() == m.group(2), "{} does not match its manifest".format(f)
            checked += 1
    assert checked >= 5


def _init_repo(path: Path):
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "t"], check=True)
    (path / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "f.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", "init"], check=True)


def test_a_harness_linked_worktree_under_the_canonical_path_passes_the_guard(tmp_path):
    """Ruling 2: isolation is the invariant, not the path. The harness assigns
    .claude/worktrees/<name> beneath the canonical checkout; that is a linked
    worktree (git-dir != git-common-dir) and must be allowed."""
    canonical = tmp_path / "canonical"; canonical.mkdir()
    _init_repo(canonical)
    harness = canonical / ".claude" / "worktrees" / "seat-task"
    harness.parent.mkdir(parents=True)
    subprocess.run(["git", "-C", str(canonical), "worktree", "add", "-q", str(harness), "-b", "seat/task"], check=True)
    assert W.is_main_worktree(canonical) is True
    assert W.is_main_worktree(harness) is False
    assert W.receipt(harness)["worktree_path"].startswith(str(canonical.resolve()))


def test_this_test_runs_from_a_linked_worktree_and_journals_are_committable_here():
    assert W.is_main_worktree(REPO) is False, W.receipt(REPO)
    assert not _ignored("roles/Archaeon/journal/2026-09-11.md")
