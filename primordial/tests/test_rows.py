"""F4 commit-on-write rows, exercised in a throwaway git repo."""
from __future__ import annotations

import json
import subprocess

import pytest

from primordial.fabric.rows import RowWriter, commit_path


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture(autouse=True)
def tagged(monkeypatch):
    monkeypatch.setenv("PM_TAG", "t-0000")
    monkeypatch.setenv("PM_LANE", "F")


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README").write_text("x", encoding="utf-8")
    (tmp_path / "other.txt").write_text("staged elsewhere", encoding="utf-8")
    git(tmp_path, "add", "README")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def n_commits(repo):
    return int(git(repo, "rev-list", "--count", "HEAD"))


def test_rows_commit_on_write_and_on_close_only_the_rows_file(repo):
    p = repo / "rows" / "X1.jsonl"
    git(repo, "add", "other.txt")                                  # someone else's staged file
    w = RowWriter(p, "X1", commit_every_s=0, repo=repo)
    w.write({"status": "dev", "fitness": 1.0})
    assert n_commits(repo) == 2
    w.every = 3600
    w.write({"status": "aborted", "fitness": None})
    assert n_commits(repo) == 2                                    # not yet due
    w.close()
    assert n_commits(repo) == 3
    committed = git(repo, "show", "HEAD:rows/X1.jsonl").splitlines()
    assert [json.loads(x)["status"] for x in committed] == ["dev", "aborted"]
    assert "other.txt" not in git(repo, "log", "--name-only", "--format=")  # --only kept it out
    assert "A  other.txt" in git(repo, "status", "--short")


def test_status_tag_is_required(repo):
    w = RowWriter(repo / "rows" / "X2.jsonl", "X2", commit_every_s=3600, repo=repo)
    with pytest.raises(ValueError):
        w.write({"fitness": 3})
    w.close()


def test_exception_inside_context_still_commits_rows(repo):
    p = repo / "rows" / "X3.jsonl"
    with pytest.raises(RuntimeError):
        with RowWriter(p, "X3", commit_every_s=3600, repo=repo) as w:
            w.write({"status": "record", "v": 1})
            raise RuntimeError("TTL")
    assert "(aborted)" in git(repo, "log", "-1", "--format=%s")
    assert commit_path(p, "X3", repo=repo) is None                 # nothing left uncommitted
