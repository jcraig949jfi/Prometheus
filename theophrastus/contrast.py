"""CONTRAST(A, B): the primitive scientific object (charter VIII).

Implements PREREG section 4-5 exactly:
  p_cell = mean accuracy over the repeats; n = repeats x n_ic_total
  SE_cell = sqrt(p(1-p)/n);  D = p_A - p_B;  SE_D = sqrt(SE_A^2 + SE_B^2)
  INSTRUMENT_BLOCKED   a side is missing, FAILED, partial (<count repeats)
                       or INCONCLUSIVE
  NO_SIGNAL            |D| <  2 SE_D
  WEAK_SIGNAL          2 SE_D <= |D| < 4 SE_D, or a 4-SE primary whose
                       replication fails the 4-SE bar or flips sign
  REPRODUCIBLE_SIGNAL  |D| >= 4 SE_D in primary AND replication, same sign
SE_D can be 0 (both sides exactly 0 or 1, e.g. maj's structural zero); then
D == 0 is NO_SIGNAL and D != 0 is scored against a floor SE of 1/n.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

K_CANDIDATE = 4.0
K_WEAK = 2.0


def cell_stat(row: Optional[dict], expected_repeats: int) -> dict:
    if row is None:
        return {"ok": False, "why": "no row"}
    if row.get("status") != "COMPLETED":
        return {"ok": False, "why": "status %s" % row.get("status")}
    reps = (row.get("work_result") or {}).get("repeats") or []
    if len(reps) < expected_repeats:
        return {"ok": False, "why": "partial: %d/%d repeats" % (len(reps), expected_repeats)}
    if row.get("outcome") not in ("SURVIVED", "FALSIFIED"):
        return {"ok": False, "why": "outcome %s" % row.get("outcome")}
    accs = [float(r["result"]["accuracy"]) for r in reps]
    ntot = sum(int(r["result"].get("n_ic_total", 0)) for r in reps)
    if ntot <= 0:
        return {"ok": False, "why": "n_ic_total missing"}
    p = sum(a * int(r["result"]["n_ic_total"]) for a, r in zip(accs, reps)) / ntot
    se = math.sqrt(max(p * (1 - p), 0.0) / ntot)
    return {"ok": True, "p": p, "n": ntot, "se": se, "accuracies": accs,
            "row_id": row.get("row_id"), "spec_hash": row.get("spec_hash"),
            "outcome": row.get("outcome")}


def evaluate(a: Optional[dict], b: Optional[dict], *, expected_repeats: int,
             a_rep: Optional[dict] = None, b_rep: Optional[dict] = None) -> dict:
    """Score CONTRAST(A, B) from execution rows. `a_rep`/`b_rep` are the
    replication-pass rows (may be None: then the best disposition is
    WEAK_SIGNAL, never REPRODUCIBLE)."""
    sa, sb = cell_stat(a, expected_repeats), cell_stat(b, expected_repeats)
    out = {"a": sa, "b": sb, "eligible": sa["ok"] and sb["ok"]}
    if not out["eligible"]:
        out["disposition"] = "INSTRUMENT_BLOCKED"
        out["why"] = {"a": sa.get("why"), "b": sb.get("why")}
        return out
    d = sa["p"] - sb["p"]
    se = math.sqrt(sa["se"] ** 2 + sb["se"] ** 2)
    if se == 0.0:
        se_eff = 1.0 / max(sa["n"], sb["n"])
        z = 0.0 if d == 0.0 else d / se_eff
    else:
        z = d / se
    out.update({"delta": d, "se_delta": se, "z": z,
                "attainable_range": [-1.0, 1.0],
                "bar_candidate": K_CANDIDATE * se, "bar_weak": K_WEAK * se})
    if abs(z) < K_WEAK:
        out["disposition"] = "NO_SIGNAL"
        return out
    if abs(z) < K_CANDIDATE:
        out["disposition"] = "WEAK_SIGNAL"
        return out
    # candidate at 4 SE: replication decides
    if a_rep is None or b_rep is None:
        out["disposition"] = "WEAK_SIGNAL"
        out["why"] = "candidate at %.2f SE; replication pass not available" % abs(z)
        return out
    ra, rb = cell_stat(a_rep, expected_repeats), cell_stat(b_rep, expected_repeats)
    out["replication"] = {"a": ra, "b": rb}
    if not (ra["ok"] and rb["ok"]):
        out["disposition"] = "INSTRUMENT_BLOCKED"
        out["why"] = "replication side missing: %s / %s" % (ra.get("why"), rb.get("why"))
        return out
    d2 = ra["p"] - rb["p"]
    se2 = math.sqrt(ra["se"] ** 2 + rb["se"] ** 2)
    z2 = (d2 / se2) if se2 > 0 else (0.0 if d2 == 0 else d2 * max(ra["n"], rb["n"]))
    out["replication"].update({"delta": d2, "se_delta": se2, "z": z2})
    same_sign = (d > 0) == (d2 > 0) and d2 != 0
    if same_sign and abs(z2) >= K_CANDIDATE:
        out["disposition"] = "REPRODUCIBLE_SIGNAL"
    else:
        out["disposition"] = "WEAK_SIGNAL"
        out["why"] = ("replication %.2f SE, same_sign=%s" % (abs(z2), same_sign))
    return out


FAMILIES = ("C-WORLD", "C-PRESS", "C-BRANCH", "C-INTERV", "C-RES", "C-NULL")

#: which signal type a firing family names (PREREG s5); NEVER magnitude
SIGNAL_TYPE = {
    "C-WORLD": "ENVIRONMENTAL_OBSOLESCENCE",
    "C-PRESS": "PRESSURE_SENSITIVITY",
    "C-BRANCH": "BRANCH_CONTRAST",       # BRANCH_REVERSAL needs sign flip across worlds
    "C-INTERV": "REPRESENTATION_FAILURE",
    "C-RES": "PRESSURE_SENSITIVITY(resource)",
    "C-NULL": "INSTRUMENT",
}


def declared_contrasts() -> List[dict]:
    """The pre-declared contrast families (PREREG s5), as label tuples
    (mech, world, pressure, intervention) for A and B."""
    out = []
    M = ("maj", "GKL", "exp", "par")
    for m in M:
        for p in ("P_iid", "P_unif"):
            out.append({"family": "C-WORLD", "a": (m, "W149", p, "NONE"), "b": (m, "W599", p, "NONE")})
    for m in M:
        for w in ("W149", "W599"):
            out.append({"family": "C-PRESS", "a": (m, w, "P_iid", "NONE"), "b": (m, w, "P_unif", "NONE")})
    for w in ("W149", "W599"):
        for p in ("P_iid", "P_unif"):
            for h, g in (("GKL", "exp"), ("GKL", "par"), ("maj", "exp"), ("maj", "par")):
                out.append({"family": "C-BRANCH", "a": (h, w, p, "NONE"), "b": (g, w, p, "NONE")})
    for m in ("GKL", "exp", "par", "maj"):
        out.append({"family": "C-INTERV", "a": (m, "W149", "P_iid", "NONE"), "b": (m, "W149", "P_iid", "REFLECT")})
    for m in ("GKL", "exp"):
        out.append({"family": "C-RES", "a": (m, "W149", "P_iid", "NONE"), "b": (m, "W149h", "P_iid", "NONE")})
        out.append({"family": "C-RES", "a": (m, "W599", "P_iid", "NONE"), "b": (m, "W599h", "P_iid", "NONE")})
    out.append({"family": "C-NULL", "a": ("GKL", "W149", "P_iid", "NONE"), "b": ("GKL", "W149", "P_iid_T", "NONE")})
    assert len(out) == 8 + 8 + 16 + 4 + 4 + 1
    return out
