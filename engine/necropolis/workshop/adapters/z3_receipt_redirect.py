"""Run a Techne acquisition check without appending to its ledgers (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: techne/acquisition/checks/*.py (e.g. z3_h1_oracle.py,
z3_first_check.py) executed UNCHANGED via runpy.  Techne's receipts/ and
locks/ are append-only ledgers; a coroner re-run must not append to them, so
techne.acquisition.paths.ACQ_ROOT is pointed at a temporary directory for the
duration of the subprocess only.

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::z3_oracle.PARITY.*
and ::adapters_z3_redirect.*

Reads: the check script.  Writes: only inside the temporary ACQ_ROOT (deleted
afterwards unless keep=True).  Reports any receipt file whose mtime changed
during the run so a leak is visible rather than assumed absent.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _snapshot(d: Path) -> dict:
    return {p.name: p.stat().st_mtime for p in d.glob("*")} if d.exists() else {}


def run_check(script_rel: str, repo: Path, *, extra_argv=(), timeout: int = 600, keep: bool = False) -> dict:
    repo = Path(repo)
    receipts = repo / "techne/acquisition/receipts"
    locks = repo / "techne/acquisition/locks"
    before = {"receipts": _snapshot(receipts), "locks": _snapshot(locks)}
    td = tempfile.mkdtemp(prefix="necro_acq_")
    fixture = str(pathlib.Path(td) / "fixture.json")
    argv = [Path(script_rel).name, "--fixture-out", fixture, *extra_argv]
    code = ("import pathlib,sys; sys.path.insert(0, %r); import techne.acquisition.paths as P; "
            "P.ACQ_ROOT = pathlib.Path(%r); import runpy; sys.argv=%r; runpy.run_path(%r, run_name='__main__')"
            % (str(repo), td, argv, str(repo / script_rel)))
    t0 = time.time()
    r = subprocess.run([sys.executable, "-c", code], cwd=str(repo), capture_output=True, text=True,
                       timeout=timeout, encoding="utf-8", errors="replace")
    fx = None
    try:
        fx = json.loads(Path(fixture).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        pass
    after = {"receipts": _snapshot(receipts), "locks": _snapshot(locks)}
    touched = {k: sorted(n for n, m in after[k].items() if n not in before[k] or m != before[k][n]) for k in after}
    if not keep:
        shutil.rmtree(td, ignore_errors=True)
    return {"script": script_rel, "rc": r.returncode, "seconds": round(time.time() - t0, 2), "fixture": fx,
            "ledger_touched": touched, "acq_root_tmp": td if keep else None, "tail": (r.stdout + r.stderr)[-400:]}
