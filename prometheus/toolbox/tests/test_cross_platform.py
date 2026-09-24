"""Cross-platform replay evidence (overnight C46/C47): the same fixtures recomputed by a DIFFERENT CPython on a
DIFFERENT OS (WSL Linux python3 when present) must give identical trace hashes -- the BIT claim across hosts,
including the float-state c6 world. Skipped with the reason when no second interpreter is reachable."""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run(cmd, cwd, timeout=600):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=timeout)
    return r.returncode, r.stdout.decode("utf-8", "replace").replace("\x00", "")


def test_trace_hashes_agree_across_interpreters_and_platforms():
    rc, out = _run([sys.executable, "-m", "prometheus.toolbox.tests.replay_probe"], ROOT)
    assert rc == 0, out[-500:]
    here = json.loads(out.strip().splitlines()[-1])
    other = None
    if shutil.which("wsl"):
        wsl_path = "/mnt/" + str(ROOT).replace("\\", "/").replace(":", "").lower()[0] + str(ROOT).replace("\\", "/")[2:]
        rc2, out2 = _run(["wsl", "-e", "bash", "-c", "cd %s && python3 -m prometheus.toolbox.tests.replay_probe 2>/dev/null" % wsl_path], ROOT)
        lines = [l for l in out2.strip().splitlines() if l.startswith("{")]
        if rc2 == 0 and lines:
            other = json.loads(lines[-1])
    if other is None:
        pytest.skip("no second interpreter/platform reachable (wsl python3)")
    assert (other["platform"], other["python"]) != (here["platform"], here["python"])
    for name, fx in here["fixtures"].items():
        assert "error" not in fx, (name, fx)
        if name.endswith("q1e-13"):
            # C63 evidence, not an assertion: at a quantum below libm's cross-platform agreement the SEMANTIC world's
            # traces MAY differ (observed 2/3 seeds differing, Windows py3.14 vs Linux py3.12). Recorded, never widened.
            continue
        assert other["fixtures"].get(name) == fx, "trace hashes differ across platforms for %s" % name
    fine = here["fixtures"].get("pendulum_q1e-13", {}); fine_o = other["fixtures"].get("pendulum_q1e-13", {})
    n_differ = sum(1 for k in fine if fine[k] != fine_o.get(k))
    print("SEMANTIC evidence: pendulum quantum 1e-13 differs across platforms on %d/%d seeds; quantum 1e-6 agrees on all" % (n_differ, len(fine)))
