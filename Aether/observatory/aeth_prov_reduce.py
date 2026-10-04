"""Reduce aeth_prov_assay unit results (V2-B TEST-1): pooled, per-law rung shares at a horizon.

Per law (pooled over its seed units), the share of origins whose payload lineage, at the horizon:
- P3_far: has a holder at Chebyshev distance >= FAR (3) from the origin;
- P4_transformed: has a holder whose value differs from the origin's value;
- P5_composed: has a holder that carries two or more tracked lineages;
- P6_deep: has a lineage that survived >= DEEP (5) rewrites (max_hops);
- alive: has any holder.

Positive control (fwd):
    QUALIFIED  iff  P3_far(fwd) >= max(0.05, 2 x P3_far(rcv))  AND  P3_far(fwd) > P3_far(v1)
otherwise CONTROL_FAILED. The thresholds follow the old E-P1 rule (>= 2x rcv and >= 0.05) for direct comparability.
"""
from __future__ import annotations

import glob
import json
import os
import sys

FAR, DEEP, HORIZON = 3, 5, "400"


def load(d):
    by = {}
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            r = json.load(fh)
        if r.get("instrument") != "aeth_prov_assay":
            continue
        by.setdefault(r["variant"], []).append(r)
    return by


def law_shares(results, horizon=HORIZON):
    profs = [p for r in results for p in r["horizons"][horizon]]
    n = len(profs) or 1
    return {"origins": len(profs),
            "P3_far": sum(p["max_distance"] >= FAR for p in profs) / n,
            "P4_transformed": sum(p["transformed"] > 0 for p in profs) / n,
            "P5_composed": sum(p["composed"] > 0 for p in profs) / n,
            "P6_deep": sum(p["max_hops"] >= DEEP for p in profs) / n,
            "alive": sum(p["holders"] > 0 for p in profs) / n,
            "seeds": sorted(r["seed_index"] for r in results)}


def main(argv=None):
    d = (argv or sys.argv[1:])[0]
    by = load(d)
    laws = {k: law_shares(v) for k, v in sorted(by.items())}
    ctrl = None
    if all(k in laws for k in ("fwd", "rcv", "v1")):
        f, r, v = laws["fwd"]["P3_far"], laws["rcv"]["P3_far"], laws["v1"]["P3_far"]
        ok = f >= max(0.05, 2 * r) and f > v
        ctrl = {"fwd_P3_far": f, "rcv_P3_far": r, "v1_P3_far": v,
                "verdict": "QUALIFIED" if ok else "CONTROL_FAILED"}
    print(json.dumps({"reducer": "aeth_prov_reduce", "far": FAR, "deep": DEEP, "horizon": HORIZON,
                      "laws": laws, "positive_control": ctrl}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
