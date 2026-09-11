"""The watchdog measures the property, not presence (2026-09-11).

Runs the REAL scripts/ew_watchdog.ps1 against tests/_fake_pew.py on a port
that is not the live service's, with a process match that is a unique
marker, so nothing here can touch the live PEW. Windows only (PowerShell,
Get-NetTCPConnection); skipped elsewhere.

Controls, in the base-role sense:
    cheat control     a healthy service must NOT be restarted (the morning's
                      defect: three services started by a slow probe)
    positive control  a service that accepts TCP and never answers MUST be
                      stopped and started after FailThreshold ticks (the
                      afternoon's defect: a hung service kept for 3 h)
    warm-up           a loading model inside the grace window counts nothing
    token             the search probe carries the bearer; a wrong one is a
                      failure, so a 'healthy' log line proves an
                      authenticated search answered, not merely liveness
"""
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE / "scripts" / "ew_watchdog.ps1"
FAKE = HERE / "tests" / "_fake_pew.py"
PORT = 8378
TOKEN = "watchdog-test-token-not-a-secret"

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="PowerShell watchdog")


def _root(tmp_path):
    root = tmp_path / "evidence_wiki"
    (root / "derived").mkdir(parents=True)
    (root / "config.json").write_text(json.dumps(
        {"auth_token": TOKEN, "machine_tokens": {"M1": TOKEN}}), encoding="utf-8")
    return root


def _start_fake(mode, marker):
    p = subprocess.Popen([sys.executable, str(FAKE), "--port", str(PORT),
                          "--mode", mode, "--token", TOKEN, "--marker", marker],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    line = p.stdout.readline()
    assert "fake pew" in line, line
    return p


def _tick(root, marker, mode_for_restart="healthy", **kw):
    """One scheduled-task tick, with the test's parameters."""
    args = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
            "-Port", str(PORT), "-Machine", "M1", "-ProcMatch", marker,
            "-Root", str(root), "-StartFile", str(FAKE),
            "-StartArgs", f"--port {PORT} --mode {mode_for_restart} --token {TOKEN} --marker {marker}",
            "-HealthTimeoutSec", "3", "-SearchTimeoutSec", "3",
            "-StartGraceSec", str(kw.get("grace", 60)),
            "-FailThreshold", str(kw.get("threshold", 3))]
    env = dict(os.environ, EW_PYTHON=sys.executable)
    env.pop("EW_AUTH_TOKEN", None)
    # No pipes: a service the watchdog starts inherits PowerShell's handles,
    # and a captured pipe would then never reach EOF (measured: the test hung
    # exactly on the ticks that start a process).
    r = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=120, env=env)
    log = (root / "derived" / "watchdog.log").read_text(encoding="utf-8").splitlines()
    st = json.loads((root / "derived" / "watchdog_state.json").read_text(encoding="utf-8"))
    return r.returncode, log, st


def _alive(p):
    return p.poll() is None


def _kill_marked(marker):
    """End anything carrying the marker, and anything still listening on the
    test port (a leftover from an interrupted run answered for every later
    test once; the fake now refuses to double-bind, and this clears it)."""
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    f"Where-Object {{ $_.CommandLine -match '{marker}' }} | "
                    "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; "
                    f"Get-NetTCPConnection -State Listen -LocalPort {PORT} -ErrorAction SilentlyContinue | "
                    "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
                   capture_output=True, timeout=60)


@pytest.fixture
def marker():
    _kill_marked("fakepew-")
    time.sleep(0.5)
    m = "fakepew-" + uuid.uuid4().hex[:12]
    yield m
    _kill_marked(m)


def test_cheat_control_healthy_service_is_not_restarted(tmp_path, marker):
    root = _root(tmp_path)
    p = _start_fake("healthy", marker)
    try:
        rc, log, st = _tick(root, marker)
        assert rc == 0
        assert log[-1].split("  ", 1)[1].startswith("ok  health "), log
        assert "hybrid search" in log[-1] and "last_success" in log[-1]
        assert st["consecutive_failures"] == 0 and st["last_success"]
        assert st["last_start_pid"] is None, "a healthy service must not be (re)started"
        assert _alive(p)
        assert TOKEN not in "\n".join(log), "the token must never reach the log"
    finally:
        p.kill()


def test_positive_control_hung_service_is_stopped_and_started(tmp_path, marker):
    root = _root(tmp_path)
    p = _start_fake("hung", marker)
    try:
        rc1, log1, st1 = _tick(root, marker)
        assert st1["consecutive_failures"] == 1 and "probe failed (1/3)" in log1[-1]
        assert _alive(p), "one failed tick must not restart a present service"
        rc2, log2, st2 = _tick(root, marker)
        assert st2["consecutive_failures"] == 2 and "probe failed (2/3)" in log2[-1]
        assert _alive(p)
        rc3, log3, st3 = _tick(root, marker)
        assert "stopping pids" in log3[-2], log3
        assert log3[-1].split("  ", 1)[1].startswith("started pid "), log3
        time.sleep(1.0)
        assert not _alive(p), "the hung process must be gone"
        assert st3["last_start_pid"] and st3["consecutive_failures"] == 0
        # The replacement (started healthy) answers on the next tick.
        time.sleep(1.0)
        rc4, log4, st4 = _tick(root, marker)
        assert log4[-1].split("  ", 1)[1].startswith("ok  health "), log4
        assert st4["last_success"]
    finally:
        if _alive(p):
            p.kill()


def test_warm_up_inside_grace_counts_nothing(tmp_path, marker):
    root = _root(tmp_path)
    p = _start_fake("loading", marker)
    try:
        rc, log, st = _tick(root, marker, grace=600)
        assert "warming up" in log[-1], log
        assert st["consecutive_failures"] == 0 and st["last_success"] is None
        assert _alive(p)
    finally:
        p.kill()


def test_unready_beyond_grace_is_a_failure(tmp_path, marker):
    root = _root(tmp_path)
    p = _start_fake("unready", marker)
    try:
        rc, log, st = _tick(root, marker)
        assert st["consecutive_failures"] == 1
        assert "search model not ready" in log[-1], log
        assert _alive(p)
    finally:
        p.kill()


def test_wrong_token_is_a_failure_not_a_success(tmp_path, marker):
    """A 'healthy' line means an AUTHENTICATED search answered."""
    root = _root(tmp_path)
    (root / "config.json").write_text(json.dumps(
        {"auth_token": "wrong", "machine_tokens": {"M1": "wrong"}}), encoding="utf-8")
    p = _start_fake("healthy", marker)
    try:
        rc, log, st = _tick(root, marker)
        assert st["consecutive_failures"] == 1
        assert "search http 401" in log[-1], log
        assert _alive(p)
    finally:
        p.kill()


def test_fresh_start_gets_grace_before_judgement(tmp_path, marker):
    """After the watchdog starts a service, a not-yet-answering tick inside
    the grace window is logged as waiting, not counted (cold start: ~4 min)."""
    root = _root(tmp_path)
    # Nothing is running: the first tick starts a HUNG replacement on purpose.
    rc1, log1, st1 = _tick(root, marker, mode_for_restart="hung", grace=600)
    assert log1[-1].split("  ", 1)[1].startswith("started pid "), log1
    time.sleep(1.0)
    rc2, log2, st2 = _tick(root, marker, mode_for_restart="hung", grace=600)
    assert "not yet answering" in log2[-1] and "waiting" in log2[-1], log2
    assert st2["last_start_pid"] == st1["last_start_pid"], "no second start inside grace"
