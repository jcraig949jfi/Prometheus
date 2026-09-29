"""Script-executor guards (no DB needed): module mode stays inside the pinned worktree; only allow-listed env."""
from pathlib import Path

from fabric import executors as X


def _task(**params):
    return {"task_id": "tsk-x", "executor": "script", "params": params}


def test_module_mode_runs_inside_worktree(tmp_path: Path):
    wt = tmp_path / "wt"; (wt / "pkg").mkdir(parents=True)
    (wt / "pkg" / "__init__.py").write_text("")
    (wt / "pkg" / "hello.py").write_text("import os\nprint('hi', os.environ.get('COSMOS_BROKER'))\n")
    r = X.run_script(_task(module="pkg.hello", env=["COSMOS_BROKER"]), "att-x", str(wt), tmp_path / "a", lambda: None)
    assert r.exit_code == 0 and r.final_text.strip() == "hi 1"


def test_module_outside_worktree_refused(tmp_path: Path):
    wt = tmp_path / "wt"; wt.mkdir()
    for m in ("json", "os.path", "../x", "pkg;rm"):
        r = X.run_script(_task(module=m), "att-x", str(wt), tmp_path / "a", lambda: None)
        assert r.exit_code is None and "not inside" in r.error


def test_env_not_allow_listed_refused(tmp_path: Path):
    wt = tmp_path / "wt"; wt.mkdir(); (wt / "s.py").write_text("print(1)\n")
    r = X.run_script(_task(script="s.py", env=["EW_DB_HOST"]), "att-x", str(wt), tmp_path / "a", lambda: None)
    assert r.exit_code is None and "allow-listed" in r.error


def test_script_path_escape_refused(tmp_path: Path):
    wt = tmp_path / "wt"; wt.mkdir(); (tmp_path / "evil.py").write_text("print(1)\n")
    r = X.run_script(_task(script="../evil.py"), "att-x", str(wt), tmp_path / "a", lambda: None)
    assert r.exit_code is None and "inside the pinned worktree" in r.error


def test_probe_replaces_declared_environment_caps():
    from fabric.worker import effective_capabilities, probe_environment, AGENT_NAME
    probe = probe_environment()
    assert "python.stdlib" in probe["capabilities"] and any(c.startswith("pin.python==") for c in probe["capabilities"])
    eff = effective_capabilities(["repo.read", "python.stdlib", "python.notapackage", "pin.numpy==0.0.1"], probe)
    assert "repo.read" in eff["capabilities"]
    assert set(eff["dropped"]) == {"python.notapackage", "pin.numpy==0.0.1"}
    assert "pin.numpy==0.0.1" not in eff["capabilities"]
    assert AGENT_NAME.match("worker.ubu002") and AGENT_NAME.match("worker.ubu001.sci")
    assert not AGENT_NAME.match("Artemis") and not AGENT_NAME.match("Odysseus")


def test_gc_bases_keeps_only_most_recent(tmp_path):
    """DEF-ODY-015: the per-worker base cache is bounded; removal goes through git and leaves the clone consistent."""
    import os
    import subprocess
    import time
    from fabric.worker import gc_bases
    clone = tmp_path / "clone"; clone.mkdir()
    g = lambda *a: subprocess.run(["git", "-C", str(clone), *a], check=True, capture_output=True, text=True).stdout
    g("init", "-q", "-b", "main"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    (clone / "f").write_text("x"); g("add", "-A"); g("commit", "-qm", "c")
    bases = tmp_path / "worker" / "bases"; bases.mkdir(parents=True)
    for i in range(4):
        g("worktree", "add", "--detach", str(bases / ("b%d" % i)), "HEAD")
        t = time.time() - 100 + i
        os.utime(bases / ("b%d" % i), (t, t))
    other = tmp_path / "not_a_base"; g("worktree", "add", "--detach", str(other), "HEAD")
    removed = gc_bases(bases, clone, keep=2)
    diag = "removed=%r left=%r mtimes=%r worktrees=%r" % (removed, sorted(p.name for p in bases.iterdir()),
                                                           {p.name: p.stat().st_mtime for p in bases.iterdir()},
                                                           g("worktree", "list"))
    assert sorted(removed) == ["b0", "b1", "b2"], diag
    assert sorted(p.name for p in bases.iterdir()) == ["b3"], diag
    listed = g("worktree", "list")
    assert str(other) in listed and "b3" in listed and "b0" not in listed
