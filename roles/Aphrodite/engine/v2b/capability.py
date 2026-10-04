"""D-stratified capability endpoint (T53).

Historical CAPABILITY (a18_c1/a20_c3) was this test: SELECTED qualifies within the 250k escrow, and START and
PRISTINE fail to qualify at the 10M ladder. W2 showed the result is decided by whether a library holds an early
extensional equivalent of the witness:
- PRISTINE coverage is 151,920 programs;
- beyond it, each fallback init block is 83.9M charges;
- so "capability" ratios are generic walk-cliff ratios.
Any library holding an early equivalent gains 10^3-10^4x.

This endpoint replaces "pass/fail at a budget" with a budget-free quantity, measured exactly by the
deterministic walk:

  D(lib, cell) = log10(charge of the FIRST TRIBUNAL-QUALIFIED program), cap C.
                 Spurious dev-consistent hits are walked past. Censored at C means D >= log10(C).

Families are stratified by D_PRISTINE:
  COVERED    D_P <= log10(N_COV)            PRISTINE solves inside its coverage; a library can only speed it up
  WINDOW     log10(N_COV) < D_P < log10(C)  PRISTINE solves in the fallback before the cap
  CENSORED   D_P >= log10(C)                PRISTINE does not solve within the cap

The endpoint never reports a single "capability" bit. Per arm and stratum it reports:
  - n, and the median and mean of delta = D_PRISTINE - D_arm (censored values enter at the cap, a lower bound
    on delta when the arm solves);
  - SOLVES_WHERE_P_CENSORED: families where the arm qualifies below the cap and PRISTINE is censored. This is
    the only budget-free "new capability" count, and even it is relative to C;
  - SPURIOUS: spurious hits walked past before the first qualified program.
A capability claim must exceed the same quantity for the equal-expressivity shams. That comparison is the
generic-cliff control: a sham holding an early equivalent gains just as much.
"""
import math
import statistics

import paths  # noqa: F401
import a17
from a18 import FR, G

import walk

N_COV = len(G.H1_SPACE) * len(G.H2_SPACE) * len(G.FINAL_SPACE)
DEFAULT_CAP = 40 * a17.ESCROW                    # 10M, the historical LADDER_CAP


def stratum(d_p, cap=DEFAULT_CAP):
    if d_p["censored"]:
        return "CENSORED"
    return "COVERED" if d_p["charge"] <= N_COV else "WINDOW"


def measure(libs, prov, name, size, cells_idx, qualify, cap=DEFAULT_CAP, label="V2B-CAP"):
    """libs: {arm: KLib}. It must include 'PRISTINE'. Returns one row per cell, with {arm: first_qualified}."""
    rows = []
    for i in cells_idx:
        c = FR.Cell(prov, name, i, size, label=label)
        row = {"family": name, "cell": i, "arms": {}}
        for arm, lib in libs.items():
            row["arms"][arm] = walk.first_qualified(lib, c, cap, qualify)
        rows.append(row)
    return rows


def _D(x):
    return math.log10(max(1, x["charge"]))


def summarise(rows, cap=DEFAULT_CAP, ref="PRISTINE"):
    out = {}
    arms = sorted({a for r in rows for a in r["arms"]})
    for arm in arms:
        per = {}
        for r in rows:
            p, a = r["arms"][ref], r["arms"][arm]
            s = stratum(p, cap)
            e = per.setdefault(s, {"n": 0, "delta": [], "solves_where_ref_censored": 0, "arm_censored": 0,
                                   "spurious": 0})
            e["n"] += 1
            e["delta"].append(_D(p) - _D(a))
            e["spurious"] += a["spurious_before"]
            e["arm_censored"] += int(a["censored"])
            if s == "CENSORED" and not a["censored"]:
                e["solves_where_ref_censored"] += 1
        for s, e in per.items():
            d = e.pop("delta")
            e["median_delta"] = round(statistics.median(d), 4) if d else None
            e["mean_delta"] = round(statistics.fmean(d), 4) if d else None
        out[arm] = per
    return {"cap": cap, "N_COV": N_COV, "ref": ref, "by_arm": out}


def generic_cliff_excess(summary, treatment, shams, stratum_name="CENSORED"):
    """Treatment SOLVES_WHERE_REF_CENSORED minus the max over shams. A capability claim needs a positive excess
    (the sham comparison is the generic-cliff control)."""
    t = summary["by_arm"].get(treatment, {}).get(stratum_name, {}).get("solves_where_ref_censored", 0)
    s = max((summary["by_arm"].get(x, {}).get(stratum_name, {}).get("solves_where_ref_censored", 0)
             for x in shams), default=0)
    return t - s
