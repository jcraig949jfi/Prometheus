"""Adversarial tests for rogit (read-only git for workers; defect D12)."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROGIT = str(Path(__file__).resolve().parents[1] / "tools" / "rogit.py")


def _git(repo, *a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "wt"; r.mkdir()
    _git(r, "init", "-q", "-b", "main"); _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    (r / "a.txt").write_text("alpha\nbeta\n"); (r / "sub").mkdir(); (r / "sub" / "b.py").write_text("print(1)\n")
    _git(r, "add", "-A"); _git(r, "commit", "-qm", "one")
    _git(r, "branch", "side"); (r / "a.txt").write_text("alpha\ngamma\n"); _git(r, "commit", "-qam", "two")
    # hostile repo-local configuration: every read path that could run a program would touch a marker
    m = tmp_path / "MARKER"
    (r / ".gitattributes").write_text("*.txt diff=evil\n")
    _git(r, "config", "diff.evil.textconv", "sh -c 'touch %s; cat'" % m)
    _git(r, "config", "diff.external", "sh -c 'touch %s'" % m)
    _git(r, "config", "core.fsmonitor", "sh -c 'touch %s'" % m)
    _git(r, "config", "core.pager", "sh -c 'touch %s; cat'" % m)
    _git(r, "config", "alias.evil", "!touch %s" % m)
    (r / ".git" / "hooks" / "post-checkout").write_text("#!/bin/sh\ntouch %s\n" % m)
    os.chmod(r / ".git" / "hooks" / "post-checkout", 0o755)
    (r / "a.txt").write_text("alpha\ngamma\ndelta\n")                  # a worktree change so diff has work to do
    return r, m


def run(repo, *args, env_extra=None):
    env = {"PATH": os.environ["PATH"], "HOME": str(repo.parent), "FABRIC_WORKTREE": str(repo)}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, ROGIT, *args], env=env, capture_output=True, text=True, cwd=str(repo))


ALLOWED = [
    ["log", "--all", "--oneline"], ["log", "-p", "--all"], ["show", "HEAD:a.txt"], ["show", "HEAD"], ["-C", "sub", "log", "--oneline"],
    ["branch", "--contains", "HEAD~1"], ["branch", "-a"], ["branch"], ["tag", "-l"], ["for-each-ref"],
    ["grep", "-n", "alpha"], ["grep", "-F", "alpha", "--", "a.txt"], ["cat-file", "-p", "HEAD"], ["rev-parse", "HEAD"],
    ["status"], ["diff"], ["diff", "HEAD~1", "HEAD"], ["ls-tree", "-r", "HEAD"], ["blame", "a.txt"], ["merge-base", "main", "side"],
    ["log", "--full-history", "--diff-filter=A", "--", "a.txt"], ["rev-list", "--all", "--count"],
]
REFUSED = [
    ["commit", "-m", "x"], ["push"], ["fetch"], ["checkout", "side"], ["reset", "--hard"], ["config", "--list"],
    ["evil"], ["submodule", "update"], ["archive", "HEAD"], ["clone", "."],
    ["-C", "/etc", "log"], ["-C", "..", "log"], ["--git-dir=/tmp", "log"], ["-c", "core.pager=cat", "log"],
    ["log", "--git-dir=/tmp"], ["log", "-c", "x"] if False else ["log", "--exec-path=/tmp"],
    ["diff", "--no-index", "/etc/hostname", "a.txt"], ["grep", "--no-index", "x"], ["grep", "-f", "/etc/hostname"],
    ["grep", "--file=/etc/hostname"], ["grep", "-O", "x"], ["log", "--output=/tmp/rogit_out"],
    ["show", "--ext-diff", "HEAD"], ["cat-file", "--textconv", "HEAD:a.txt"], ["cat-file", "--filters", "HEAD:a.txt"],
    ["branch", "newbranch"], ["branch", "-D", "side"], ["branch", "-f", "side", "HEAD"], ["branch", "-m", "x"],
    ["tag", "v1"], ["tag", "-d", "v1"], ["blame", "--contents", "/etc/hostname", "a.txt"], ["blame", "-S", "/etc/hostname", "a.txt"],
    ["blame", "--ignore-revs-file=/etc/hostname", "a.txt"], ["ls-files", "--exclude-from=/etc/hostname"], ["ls-files", "-X", "/etc/hostname"],
    ["diff", "-O/etc/hostname"], ["rev-parse", "--resolve-git-dir", "/etc"], ["log", "--paginate"], [],
]


@pytest.mark.parametrize("args", ALLOWED, ids=lambda a: " ".join(a))
def test_allowed_reads_work_and_run_no_program(repo, args):
    r, m = repo
    p = run(r, *args)
    assert p.returncode in (0, 1), p.stderr                     # 1 = e.g. grep no match
    assert "refused" not in p.stderr
    assert not m.exists(), "a repo-configured program ran for: %s" % args


@pytest.mark.parametrize("args", REFUSED, ids=lambda a: " ".join(a) or "<empty>")
def test_refused(repo, args):
    r, m = repo
    p = run(r, *args)
    assert p.returncode == 64 and "refused" in p.stderr, (args, p.returncode, p.stderr)
    assert not m.exists()
    assert not Path("/tmp/rogit_out").exists()


def test_branch_list_does_not_create_ref(repo):
    r, _ = repo
    before = subprocess.run(["git", "-C", str(r), "for-each-ref"], capture_output=True, text=True).stdout
    run(r, "branch", "--list", "zzz"); run(r, "branch", "--contains", "HEAD")
    assert subprocess.run(["git", "-C", str(r), "for-each-ref"], capture_output=True, text=True).stdout == before


def test_hostile_caller_env_is_scrubbed(repo, tmp_path):
    r, m = repo
    other = tmp_path / "other"; other.mkdir(); _git(other, "init", "-q")
    p = run(r, "rev-parse", "--show-toplevel", env_extra={"GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(other),
                                                            "GIT_EXTERNAL_DIFF": "sh -c 'touch %s'" % m, "GIT_PAGER": "touch %s" % m})
    assert p.stdout.strip() == str(r.resolve()) and not m.exists()
    assert run(r, "diff", env_extra={"GIT_EXTERNAL_DIFF": "sh -c 'touch %s'" % m}).returncode == 0 and not m.exists()


def test_no_worktree_env_refuses(repo):
    r, _ = repo
    p = subprocess.run([sys.executable, ROGIT, "log"], env={"PATH": os.environ["PATH"]}, capture_output=True, text=True)
    assert p.returncode == 64


def test_symlinked_dir_outside_is_refused(repo, tmp_path):
    r, _ = repo
    (r / "escape").symlink_to("/etc")
    assert run(r, "-C", "escape", "log").returncode == 64


def test_repo_state_unchanged(repo):
    r, _ = repo
    head = subprocess.run(["git", "-C", str(r), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    idx = (r / ".git" / "index").read_bytes()
    for a in ALLOWED:
        run(r, *a)
    assert subprocess.run(["git", "-C", str(r), "rev-parse", "HEAD"], capture_output=True, text=True).stdout == head
    assert (r / ".git" / "index").read_bytes() == idx


@pytest.mark.parametrize("args", [["diff"], ["log", "-p", "-1"], ["status"], ["evil"]], ids=lambda a: " ".join(a))
def test_positive_control_plain_git_does_run_the_hostile_config(repo, args):
    """Without rogit, the same reads DO execute repo-configured programs: the refusals above are not vacuous."""
    r, m = repo
    subprocess.run(["git", "-C", str(r), "-c", "core.pager=cat", *args], capture_output=True,
                   env={"PATH": os.environ["PATH"], "HOME": str(r.parent)})
    assert m.exists(), "control failed: plain git did not trigger the hostile config for %s" % args
