"""Run a flat sigma_kernel module under its historical convention (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: sigma_kernel/a148_obstruction.py, a149_obstruction.py
and siblings, executed UNCHANGED in a fresh interpreter with cwd=sigma_kernel/
and nothing else imported.  The in-tree package __init__.py (added later)
shadows the flat sigma_kernel.py these modules were written against, so an
in-process package import fails; that breakage is recorded, not repaired
(run_controls.py::a148_obstruction.*).

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_sigma_runner.*

Reads: the module and whatever it reads.  Writes: whatever the module writes
(the a148 family writes nothing when called as a library); the caller passes
an expression over the module `M` and gets its JSON back.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_expr(module: str, expr: str, repo: Path, *, timeout: int = 300) -> dict:
    code = ("import json, %s as M; v = eval(%r, {'M': M}); "
            "print('__RESULT__' + json.dumps(v, default=repr))" % (module, expr))
    r = subprocess.run([sys.executable, "-c", code], cwd=str(Path(repo) / "sigma_kernel"), capture_output=True,
                       text=True, timeout=timeout, encoding="utf-8", errors="replace")
    val, ok = None, False
    for line in r.stdout.splitlines():
        if line.startswith("__RESULT__"):
            val, ok = json.loads(line[len("__RESULT__"):]), True
    return {"module": module, "expr": expr, "rc": r.returncode, "ok": ok and r.returncode == 0, "value": val,
            "stderr_tail": r.stderr[-400:], "convention": "fresh interpreter, cwd=sigma_kernel/, flat import"}


def names(module: str, repo: Path) -> dict:
    return run_expr(module, "sorted(n for n in dir(M) if not n.startswith('_'))", repo)
