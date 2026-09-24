"""Fail-closed gate on the ruler qualification (P-G01): rereads and ruler-dependent probes refuse to run
unless RESULT.json of P-G01 says INSTRUMENT_QUALIFIED. Writes a BLOCKED result if not."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common as CM            # noqa: E402
L = CM.L


def require_qualified(exp_dir, pid, tid, ph):
    p = HERE / "P-G01" / "RESULT.json"
    r = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    if r and r.get("disposition") == "INSTRUMENT_QUALIFIED":
        return r
    out = {"perturbation_id": pid, "parent": tid, "disposition": "BLOCKED_BY_INSTRUMENT", "reason": "P-G01 did not qualify the scattered ruler (%s)" % (r.get("disposition") if r else "no result"),
           "material": False, "elapsed_s": 0.0, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    L.result(exp_dir, out, ph)
    L.append_evidence(tid, pid, "BLOCKED_BY_INSTRUMENT: the scattered ruler was not qualified (P-G01 %s)" % (r.get("disposition") if r else "missing"), False)
    print("BLOCKED_BY_INSTRUMENT")
    sys.exit(0)
