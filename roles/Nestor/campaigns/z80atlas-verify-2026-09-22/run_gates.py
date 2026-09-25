"""Run every pre-freeze gate and write GATES_PREFREEZE.json. Never writes a freeze artifact.

Each gate's exit code is captured from the tool itself, never from a pipe, and a gate
that could not run is recorded as NOT_VERIFIED, never as a pass.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
PRED = HERE.parent / "z80atlas-2026-09-19"
GATES = [
    ("VM selftest", [sys.executable, "selftest_z8.py"], HERE),
    ("T-P1,2,3,8,9,10 repairs", [sys.executable, "tests/test_repairs.py"], HERE),
    ("T-P4 reservoir", [sys.executable, "tests/test_p4_reservoir.py"], HERE),
    ("T-P5 index-only", [sys.executable, "tests/test_p5_index.py"], HERE),
    ("T-P7 bundles", [sys.executable, "tests/test_p7_bundles.py"], HERE),
    ("T-P11 pair-copy causality", [sys.executable, "tests/test_p11.py"], HERE),
    ("T-S3 engineering repairs", [sys.executable, "tests/test_s3_repairs.py"], HERE),
    ("P-6 report audit (predecessor)", [sys.executable, "test_report_audit.py"], PRED),
    ("calibration controls (PREFREEZE)", [sys.executable, "controls.py"], HERE),
]


FROZEN_OBS = pathlib.Path(os.environ.get(
    "Z80A_FROZEN_OBS",
    r"F:/Prometheus-worktrees/nestor-sidequest-graphworld/roles/Nestor/campaigns/"
    r"z80atlas-2026-09-19/observatory"))


def p6_sandbox():
    """C9-D06. P-6 reads the predecessor's gitignored INDEX.jsonl and per-run files, which
    exist only in the checkout that ran the campaign, and in any other checkout its test
    crashes (IndexError on an empty FAIL list) instead of reporting NOT_VERIFIED. Rather
    than edit the predecessor directory, run it from a temporary copy of the campaign's
    top-level files, with `observatory` a directory junction to the frozen record. report_audit
    writes its receipt next to itself (the copy) and nothing under observatory/."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="p6gate_"))
    for f in PRED.iterdir():                  # the audit also reads campaign source
        if f.is_file():
            shutil.copy2(f, tmp / f.name)
    if not (FROZEN_OBS / "INDEX.jsonl").exists():
        return None
    subprocess.run(["cmd", "/c", "mklink", "/J", str(tmp / "observatory"), str(FROZEN_OBS)],
                   capture_output=True, check=True)
    return tmp


def main():
    out = []
    ok = True
    gates = list(GATES)
    sb = p6_sandbox()
    gates = [(n, c, (sb if n.startswith("P-6") else w)) for n, c, w in gates]
    for name, cmd, cwd in gates:
        if cwd is None:
            out.append({"gate": name, "rc": None, "outcome": "NOT_VERIFIED",
                        "tail": ["frozen INDEX.jsonl not found at %s" % FROZEN_OBS]})
            ok = False
            print("NOT_VERIFIED %s" % name)
            continue
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=3600)
            rc, tail = p.returncode, (p.stdout + p.stderr).strip().splitlines()[-3:]
            outcome = "PASS" if rc == 0 else "FAIL"
        except Exception as e:                                   # noqa: BLE001
            rc, tail, outcome = None, ["%s: %s" % (type(e).__name__, e)], "NOT_VERIFIED"
        ok &= outcome == "PASS"
        out.append({"gate": name, "rc": rc, "outcome": outcome,
                    "seconds": round(time.time() - t0, 1), "tail": tail})
        print("%-12s %-36s rc=%s %.1fs  %s" % (outcome, name, rc, time.time() - t0,
                                              tail[-1] if tail else ""), flush=True)
    if sb is not None:
        # Remove ONLY the junction (rmdir on a junction unlinks it; it never recurses into
        # the frozen record). Never rm -rf a directory that contains a junction.
        subprocess.run(["cmd", "/c", "rmdir", str(sb / "observatory")], capture_output=True)
    if (HERE / "CALIBRATION.json").exists():
        ok = False
        out.append({"gate": "stop line", "outcome": "FAIL",
                    "tail": ["CALIBRATION.json exists: the freeze artifact must not be written"]})
    (HERE / "GATES_PREFREEZE.json").write_text(json.dumps(
        {"ok": ok, "written": time.strftime("%Y-%m-%d %H:%M:%S"), "gates": out}, indent=1))
    print("ALL GATES:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
