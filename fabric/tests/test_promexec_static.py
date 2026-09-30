"""promexec round 2: static checks that need no root and no installed broker (EXPERIMENTAL; not enabled).

The isolation claims themselves are verified only by the acceptance matrix against the installed broker
(fabric/promexec/ACCEPTANCE_MATRIX.md, ACCEPTANCE_RUNS/). These tests pin the source-level repairs.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


broker = _load("promexec_broker", ROOT / "fabric/promexec/broker.py")
wrapper = _load("promexec_wrapper", ROOT / "fabric/tools/promexec.py")

GOOD = ["--run-id", "att-1-1", "--in", "/x/in", "--out", "/x/out"]


def test_parse_ok_and_clamped():
    rid, src, dst, lim = broker.parse_args(GOOD + ["--mem-mb", "999999", "--tasks", "1"])
    assert (rid, src, dst) == ("att-1-1", "/x/in", "/x/out")
    assert lim["mem_mb"] == 4096 and lim["tasks"] == 4 and lim["wall_s"] == 600


@pytest.mark.parametrize("argv", [
    GOOD + ["--", "secret-arg"],                     # B1: nothing after --
    GOOD + ["--script", "x.py"],                     # removed option
    GOOD + ["--bogus", "1"],                         # unknown option (M19)
    GOOD + ["--wall-s"],                             # unpaired
    GOOD + ["--run-id", "again"],                    # repeated
    ["--run-id", "a/b", "--in", "/i", "--out", "/o"],
    ["--run-id", "a", "--in", "rel", "--out", "/o"],
    GOOD + ["--wall-s", "-5"],
    GOOD + ["--wall-s", "1e9"],
])
def test_parse_refuses(argv):
    with pytest.raises(ValueError):
        broker.parse_args(argv)


def test_unit_properties_carry_the_repairs():
    props = broker.unit_properties("/var/lib/promexec/runs/r-00", {"mem_mb": 512, "cpu_pct": 100, "tasks": 16, "wall_s": 60})
    joined = "\n".join(props)
    for need in ("DynamicUser=yes", "NoNewPrivileges=yes", "RestrictSUIDSGID=yes", "ProtectSystem=strict",
                 "ProtectHome=yes", "PrivateDevices=yes", "PrivateTmp=yes", "ProtectProc=invisible", "ProcSubset=pid",
                 "PrivateNetwork=yes", "IPAddressDeny=any", "TemporaryFileSystem=/var/lib/promexec:ro",
                 "MemoryMax=512M", "TasksMax=16", "RuntimeMaxSec=60", "TMPDIR=/var/lib/promexec/work/tmp"):
        assert need in joined, need
    assert not any(p.startswith(("User=", "Group=")) for p in props)      # a static user would defeat DynamicUser
    assert "BindReadOnlyPaths=/var/lib/promexec/runs/r-00/in:/var/lib/promexec/in" in props


def test_broker_command_line_has_no_user_material():
    src = (ROOT / "fabric/promexec/broker.py").read_text()
    assert 'cmd += ["--", PY, "-I", "-B", VIEW + "/in/" + ENTRY]' in src
    assert "script_args" not in src
    # finding 5: ownership is set only on freshly created paths, never after an unprivileged process could reach them
    chowns = [l.strip() for l in src.splitlines() if "chown(" in l and not l.strip().startswith(("#", '"'))]
    assert chowns == ["os.chown(rundir, 0, xfer_gid)                  # set before any unprivileged process can know the name",
                      'os.lchown(os.path.join(rundir, "in"), xpw.pw_uid, xpw.pw_gid)']


def _attempt(tmp_path, monkeypatch):
    att = tmp_path / "att-abc"; out = att / "out"; wt = tmp_path / "wt"
    out.mkdir(parents=True); (wt / ".git").mkdir(parents=True)
    (wt / ".git" / "config").write_text("[remote]\n")
    (wt / "data.csv").write_text("1,2\n")
    (out / "job.py").write_text("print(1)\n")
    monkeypatch.setenv("FABRIC_OUT_DIR", str(out)); monkeypatch.setenv("FABRIC_WORKTREE", str(wt))
    return att, out, wt


def test_wrapper_refuses_git_inputs(tmp_path, monkeypatch, capsys):
    _attempt(tmp_path, monkeypatch)
    assert wrapper.main(["job.py", "--input", ".git/config"]) == 64
    assert ".git" in capsys.readouterr().err


def test_wrapper_refuses_mismatched_broker(tmp_path, monkeypatch, capsys):
    _attempt(tmp_path, monkeypatch)
    fake = tmp_path / "installed"; fake.write_text("not the committed broker\n")
    real = wrapper.broker_matches
    monkeypatch.setattr(wrapper, "broker_matches", lambda: real(fake, wrapper.COMMITTED_BROKER))
    assert wrapper.main(["job.py"]) == 64
    assert "M20" in capsys.readouterr().err


def test_broker_matches_detects_difference(tmp_path):
    a = tmp_path / "a"; a.write_text("x"); b = tmp_path / "b"; b.write_text("y")
    assert wrapper.broker_matches(a, a)[0] is True
    assert wrapper.broker_matches(a, b)[0] is False
    assert wrapper.broker_matches(tmp_path / "missing", a)[0] is False


def test_wrapper_stages_args_in_a_file_not_argv(tmp_path, monkeypatch):
    att, out, wt = _attempt(tmp_path, monkeypatch)
    monkeypatch.setattr(wrapper, "broker_matches", lambda: (True, "test"))
    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        stage = Path(cmd[cmd.index("--in") + 1])
        seen["files"] = sorted(str(p.relative_to(stage)) for p in stage.rglob("*") if p.is_file())
        seen["args"] = json.loads((stage / ".promexec_args.json").read_text())

        class R:
            stdout = json.dumps({"ok": True, "result": "success", "exit_code": 0})
            stderr = ""
        return R()
    monkeypatch.setattr(wrapper.subprocess, "run", fake_run)
    assert wrapper.main(["job.py", "--input", "data.csv", "--", "CANARY-ARG-7f3e", "x y"]) == 0
    assert seen["args"] == ["CANARY-ARG-7f3e", "x y"]
    assert not any("CANARY" in c or "job.py" in c for c in seen["cmd"])
    assert "--" not in seen["cmd"] and "--script" not in seen["cmd"]
    assert seen["files"] == [".promexec_args.json", "data.csv", "main.py"]


def test_transfer_keeps_mtime(tmp_path):
    """DEF-ODY-001: returned files kept mtime 0 (1970). Exercise the tar producer/extractor as the current user."""
    import os
    src = tmp_path / "src"; dst = tmp_path / "dst"; src.mkdir()
    f = src / "r.txt"; f.write_text("x"); os.utime(f, (1790000000, 1790000000))
    uid, gid = os.getuid(), os.getgid()
    if uid == 0:
        pytest.skip("run as an ordinary user")
    orig = broker.drop_to
    broker.drop_to = lambda u, g: None                       # no privilege change needed for this check
    try:
        c1, c2 = broker.transfer(uid, gid, str(src), uid, gid, str(dst), 2**20, 10)
    finally:
        broker.drop_to = orig
    assert (c1, c2) == (0, 0)
    assert int((dst / "r.txt").stat().st_mtime) == 1790000000
