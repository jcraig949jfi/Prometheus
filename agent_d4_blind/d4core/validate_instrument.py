"""Instrument validation: run the full pipeline on synthetic controls C1..C7
and check the frozen gate evaluator recovers each control's known pathology.

Usage: python -m d4core.validate_instrument [control_name ...]
"""
from __future__ import annotations

import json
import os
import sys
import time

from .pipeline import run_pipeline, _san
from .synthetic import ALL_CONTROLS, EXPECTED

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "synthetic_geometry_controls")


def main(names=None):
    names = names or list(ALL_CONTROLS.keys())
    summary = {}
    for name in names:
        t0 = time.time()
        sub = ALL_CONTROLS[name]()
        res = run_pipeline(sub, {}, OUT, is_real=False)
        got = res["gates"]["primary"]
        want = EXPECTED[name]
        ok = got in want
        summary[name] = {"primary": got, "flags": res["gates"]["flags"],
                         "expected": sorted(want), "ok": ok,
                         "wall_s": round(time.time() - t0, 1)}
        print(f"== {name}: got={got} expected={sorted(want)} "
              f"{'OK' if ok else 'MISMATCH'} ({summary[name]['wall_s']}s)")
    all_ok = all(v["ok"] for v in summary.values())
    summary["_instrument_valid"] = all_ok
    with open(os.path.join(OUT, "synthetic_control_results.json"), "w") as fh:
        json.dump(_san(summary), fh, indent=1)
    print(f"INSTRUMENT {'VALID' if all_ok else 'INVALID'}")
    return summary


if __name__ == "__main__":
    main(sys.argv[1:] or None)
