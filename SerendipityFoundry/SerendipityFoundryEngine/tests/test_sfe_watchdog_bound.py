"""Base rule 10 on the engine watchdog: the loop must be able to park itself,
and the bound must key on the engine ANSWERING, never on the script emitting.

Runs the real PowerShell script in a temp deploy dir with its test hooks
(-SimulateProbe, -NoLaunch, -NoDisable). Windows-only by nature; skipped
elsewhere so the suite stays green on a Linux reviewer's machine.

Controls, in the order a reviewer should read them:
  positive  a healthy engine writes last_success_at and resets the count
  negative  BOUND-1 failed relaunches do NOT park (no false park)
  bound     the BOUND-th failed relaunch parks: typed record, parked=true,
            exit 2, and the next fire refuses (exit 3) instead of resuming
  cheat     a failure followed by a successful relaunch is PRODUCTIVE and
            resets the count -- an emission-keyed bound would count it
  freshness the state file is rewritten on a healthy tick (Pronoia #120:
            the old script wrote nothing on success)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(_ENGINE_ROOT, "deploy", "sfengine_m2_watchdog.ps1")
PWSH = shutil.which("powershell") or shutil.which("pwsh")

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or PWSH is None,
    reason="the watchdog is a Windows Task Scheduler script")

BOUND = 3


def _tick(deploy: str, probe: str, *, relaunch: str = "fail") -> int:
    args = [PWSH, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SCRIPT,
            "-Deploy", deploy, "-Bound", str(BOUND), "-NoDisable",
            "-SimulateProbe", probe, "-SimulateRelaunch", relaunch]
    p = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return p.returncode


def _state(deploy: str) -> dict:
    with open(os.path.join(deploy, "sfengine_m2_watchdog.state.json"), encoding="ascii") as fh:
        return json.load(fh)


def test_positive_healthy_tick_writes_freshness(tmp_path):
    d = str(tmp_path)
    assert _tick(d, "ok") == 0
    s = _state(d)
    assert s["last_probe_ok"] is True
    assert s["last_success_at"] == s["last_probe_at"]
    assert s["consecutive_failures"] == 0 and s["parked"] is False
    # freshness: the OLD script left no observable on success at all
    assert not os.path.exists(os.path.join(d, "sfengine_m2_watchdog.park.json"))


def test_negative_below_the_bound_does_not_park(tmp_path):
    d = str(tmp_path)
    for i in range(1, BOUND):
        assert _tick(d, "fail") == 1
        s = _state(d)
        assert s["consecutive_failures"] == i and s["parked"] is False
    assert not os.path.exists(os.path.join(d, "sfengine_m2_watchdog.park.json"))


def test_bound_parks_with_a_typed_record_and_refuses_to_resume(tmp_path):
    d = str(tmp_path)
    for _ in range(BOUND - 1):
        assert _tick(d, "fail") == 1
    assert _tick(d, "fail") == 2                       # the BOUND-th tick parks
    s = _state(d)
    assert s["parked"] is True and s["consecutive_failures"] == BOUND
    park = json.load(open(os.path.join(d, "sfengine_m2_watchdog.park.json"), encoding="ascii"))
    assert park["schema"] == "loop_park.v1"
    assert park["accountable_seat"] == "Daedalus"
    assert park["consecutive_non_productive_ticks"] == BOUND
    # a parked loop never resumes on its own, even if the task fires again
    assert _tick(d, "ok") == 3
    assert _state(d)["parked"] is True


def test_cheat_control_a_successful_relaunch_is_productive_and_resets(tmp_path):
    """The engine is down (probe fails) but the relaunch brings it back. Under
    an emission-keyed bound this tick counts like any other; under the rule-8
    signal it is PRODUCTIVE because the engine ANSWERED, so BOUND-1 prior
    failures are wiped, not carried -- and the tick after it starts from 0."""
    d = str(tmp_path)
    for _ in range(BOUND - 1):
        assert _tick(d, "fail") == 1
    assert _state(d)["consecutive_failures"] == BOUND - 1
    assert _tick(d, "fail", relaunch="ok") == 0
    s = _state(d)
    assert s["consecutive_failures"] == 0 and s["parked"] is False
    assert s["last_probe_ok"] is True and s["last_success_at"] == s["last_probe_at"]
    # and a further failure counts from 1, not from BOUND
    assert _tick(d, "fail") == 1
    assert _state(d)["consecutive_failures"] == 1


def test_the_bound_is_declared_where_the_registry_says(tmp_path):
    """The registry row for SFEngineM2Watchdog declares BOUND 3 ticks; the
    script's default must match, or the row is a label."""
    src = open(SCRIPT, encoding="ascii").read()
    assert "[int]$Bound = 3" in src
    reg = os.path.join(_ENGINE_ROOT, "..", "..", "roles", "base-role", "MONITORS.md")
    reg = os.path.normpath(reg)
    row = [l for l in open(reg, encoding="ascii").read().splitlines() if l.startswith("SFEngineM2Watchdog |")]
    assert len(row) == 1
    cols = [c.strip() for c in row[0].split("|")]
    assert cols[10].startswith("3 ticks"), cols[10][:80]
    assert cols[11] == "Daedalus"
