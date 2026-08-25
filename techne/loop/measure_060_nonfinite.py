"""Cycle 060 measurement: the height family's response to non-finite coefficients.

FULL ENUMERATION of the declared population -- 5 scalar entry points x the non-finite input
grid. Not a sample, not an ordered slice. The instrument passes a known-answer positive control
before any result is read (`techne.lib.measurement_guard`), because cycle 059's sweep reported
"128/128 RAISES" from an instrument that was handing every function a string.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from techne.lib.measurement_guard import measure                      # noqa: E402
from techne.lib.mahler_measure import (mahler_measure, log_mahler_measure,  # noqa: E402
                                       is_cyclotomic)
from prometheus_math.polynomial_length import polynomial_length       # noqa: E402
from prometheus_math.house import house                               # noqa: E402

NAN, INF, NINF = float("nan"), float("inf"), float("-inf")

ENTRY_POINTS = [
    ("techne/lib/mahler_measure.py::mahler_measure", mahler_measure),
    ("techne/lib/mahler_measure.py::log_mahler_measure", log_mahler_measure),
    ("techne/lib/mahler_measure.py::is_cyclotomic", is_cyclotomic),
    ("prometheus_math/polynomial_length.py::polynomial_length", polynomial_length),
    ("prometheus_math/house.py::house", house),
]

# degree-0, degree>=1 with the non-finite value LEADING, and with it TRAILING.
def grid(v):
    return [(f"deg0[{v}]", [v]),
            (f"lead[{v},1,-1]", [v, 1.0, -1.0]),
            (f"trail[1,-1,{v}]", [1.0, -1.0, v])]

INPUTS = [c for v in (NAN, INF, NINF) for c in grid(v)]


def classify(fn, coeffs):
    try:
        r = fn(list(coeffs))
    except ValueError as e:
        return "RAISES", f"ValueError: {str(e)[:60]}"
    except Exception as e:                                    # noqa: BLE001
        return "RAISES_OTHER", f"{type(e).__name__}: {str(e)[:60]}"
    if isinstance(r, bool):
        return "RETURNS_BOOL", repr(r)
    try:
        finite = math.isfinite(float(r))
    except (TypeError, ValueError):
        return "RETURNS_OTHER", repr(r)
    return ("RETURNS_FINITE" if finite else "RETURNS_NONFINITE"), repr(r)


def sweep():
    rows = []
    for name, fn in ENTRY_POINTS:
        for label, coeffs in INPUTS:
            outcome, detail = classify(fn, coeffs)
            rows.append({"function": name, "input": label,
                         "outcome": outcome, "detail": detail})
    return rows


def lehmer_screen_probe():
    """P3: does a NaN measure pass the Lehmer screen silently?"""
    try:
        m = mahler_measure([NAN, 1.0, -1.0])
    except ValueError:
        return {"raised": True}
    return {"raised": False, "value": repr(m),
            "below_lehmer_bound": bool(m < 1.17628081),
            "above_lehmer_bound": bool(m > 1.17628081),
            "equals_one": bool(m == 1.0)}


def main():
    # POSITIVE CONTROL: the instrument must report the KNOWN classification on cases whose
    # answer is known independently of it. `mahler_measure([])` raises (zero polynomial, stated
    # in the docstring and tested); `mahler_measure([1,-2])` = 2 (root at 2, exactly).
    m = measure(
        "nonfinite_sweep",
        sweep,
        population=("FULL enumeration: 5 height-family scalar entry points x 9 non-finite "
                    "inputs = 45 calls. No sampling."),
        controls=[
            ("empty-input-classified-RAISES",
             lambda: classify(mahler_measure, [])[0], "RAISES"),
            ("known-M(x-2)=2-classified-RETURNS_FINITE",
             lambda: classify(mahler_measure, [1.0, -2.0])[0], "RETURNS_FINITE"),
            ("known-M(x-2)-value",
             lambda: mahler_measure([1.0, -2.0]), 2.0),
        ],
        command="python techne/loop/measure_060_nonfinite.py",
    )
    rows = m.value
    tally = {}
    for r in rows:
        tally[r["outcome"]] = tally.get(r["outcome"], 0) + 1
    propagating = sorted({r["function"] for r in rows if r["outcome"] == "RETURNS_NONFINITE"})
    out = {
        "population": m.population,
        "command": m.command,
        "controls_passed": m.controls_passed,
        "n_calls": len(rows),
        "tally": tally,
        "functions_returning_nonfinite": propagating,
        "n_functions_returning_nonfinite": len(propagating),
        "lehmer_screen_probe": lehmer_screen_probe(),
        "rows": rows,
    }
    dest = REPO / "techne" / "loop" / "rung_notes" / "cycle_060_nonfinite_sweep.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    for r in rows:
        print(f"  {r['outcome']:20s} {r['function'].split('::')[-1]:20s} {r['input']:22s} {r['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
