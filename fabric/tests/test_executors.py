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
