"""Replicate footnote [13] of Capcarrere, Sipper, Tomassini 1996 (PRL 77:4969).

Protocol, committed before this file existed:
herakles/specimens/spec-capcarrere-r1-density/PROTOCOL.md. This runner
implements that protocol and adds nothing. The predictions P1..P6 are
evaluated by the predicates below, and the verdict is whatever they return.

    python -m herakles.eca.tools.run_capcarrere_screen
"""
from __future__ import annotations

from herakles.workspace import assert_not_canonical

import json
import math
import os
import sys
import time

import numpy as np

from herakles import eca

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "specimens", "spec-capcarrere-r1-density",
                   "derived", "footnote13_screen.json")

N_CELLS = 149
STEPS = (N_CELLS + 1) // 2          # ceil(N/2) = 75
N_ICS = 1000
VARIANTS = ("bernoulli", "uniform_density")
SCREEN_SEEDS = (20260911, 20260912)
NAMED_SEEDS = (20260911, 20260912, 20260913, 20260914, 20260915)
NAMED_RULES = (184, 226, 57, 99, 0, 255, 204)
P2_BAND = (0.50, 0.70)


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(centre - half, 4), round(centre + half, 4))


def screen(variant: str, seed: int):
    ics = eca.make_ics(N_ICS, N_CELLS, seed, variant=variant)
    rows = []
    for r in range(eca.N_RULES):
        res = eca.block_output_score(r, ics, STEPS)
        rows.append({"rule": r, "n_correct": res["n_correct"],
                     "n_eligible": res["n_eligible"],
                     "score": res["score"],
                     "wilson95": wilson(res["n_correct"], res["n_eligible"])})
    return {"variant": variant, "seed": seed, "n_cells": N_CELLS,
            "steps": STEPS, "n_ics": N_ICS, "shared_ics": True,
            "ic_density_mean": float(eca.density(ics).mean()),
            "ic_density_sd": float(eca.density(ics).std()),
            "rows": rows}


def named(variant: str):
    out = {}
    for r in NAMED_RULES:
        per_seed = []
        for seed in NAMED_SEEDS:
            ics = eca.make_ics(N_ICS, N_CELLS, seed, variant=variant)
            res = eca.block_output_score(r, ics, STEPS)
            per_seed.append({"seed": seed, "n_correct": res["n_correct"],
                             "score": res["score"],
                             "wilson95": wilson(res["n_correct"], N_ICS)})
        scores = [p["score"] for p in per_seed]
        out[str(r)] = {"per_seed": per_seed,
                       "mean": float(np.mean(scores)),
                       "sd_across_seeds": float(np.std(scores, ddof=1)),
                       "n_seeds": len(NAMED_SEEDS)}
    return out


def wrong_criterion(variant: str):
    ics = eca.make_ics(N_ICS, N_CELLS, NAMED_SEEDS[0], variant=variant)
    res = eca.uniform_at_T_score(184, ics, STEPS)
    return {"rule": 184, "criterion": "uniform_at_T", "seed": NAMED_SEEDS[0],
            "n_correct": res["n_correct"], "n_eligible": res["n_eligible"],
            "score": res["score"]}


def evaluate(screens, named_by_variant, wrong_by_variant):
    """The preregistered predicates. Returns {P: {holds, evidence}}."""
    P = {}
    # P1: 184 and 226 exactly 1.0 under both variants, every seed.
    ev = {}
    ok = True
    for s in screens:
        for r in (184, 226):
            sc = s["rows"][r]["score"]
            ev["%s/%d/%d" % (s["variant"], s["seed"], r)] = sc
            ok = ok and sc == 1.0
    for v, nm in named_by_variant.items():
        for r in (184, 226):
            for p in nm[str(r)]["per_seed"]:
                ev["%s/%d/%d" % (v, p["seed"], r)] = p["score"]
                ok = ok and p["score"] == 1.0
    P["P1"] = {"holds": ok, "evidence": ev}
    if not ok:
        P["STOP"] = "P1 failed: implementation or convention defect. " \
                    "Nothing below is read."
        return P
    # P2: 57 and 99 in band under at least one variant (5-seed mean).
    in_band = {}
    for v, nm in named_by_variant.items():
        m57, m99 = nm["57"]["mean"], nm["99"]["mean"]
        in_band[v] = (P2_BAND[0] <= m57 <= P2_BAND[1]) and \
                     (P2_BAND[0] <= m99 <= P2_BAND[1])
    P["P2"] = {"holds": any(in_band.values()),
               "band": P2_BAND,
               "evidence": {v: {"57": nm["57"]["mean"], "99": nm["99"]["mean"],
                                "in_band": in_band[v]}
                            for v, nm in named_by_variant.items()}}
    # P3: under the variant(s) where P2 holds, no rule other than 184/226
    # scores above min(57, 99) in the screen (both screen seeds).
    p3 = {}
    for s in screens:
        if not in_band.get(s["variant"]):
            continue
        floor = min(s["rows"][57]["score"], s["rows"][99]["score"])
        intruders = [r["rule"] for r in s["rows"]
                     if r["rule"] not in (184, 226, 57, 99)
                     and r["score"] > floor]
        p3["%s/%d" % (s["variant"], s["seed"])] = {
            "floor_57_99": floor, "intruders": intruders,
            "top6": sorted(((r["score"], r["rule"]) for r in s["rows"]),
                           reverse=True)[:6]}
    P["P3"] = {"holds": bool(p3) and all(not x["intruders"]
                                         for x in p3.values()),
               "applicable": bool(p3), "evidence": p3}
    # P4: 57 and 99 within 2 SE of each other (5-seed means, paired ICs).
    p4 = {}
    for v, nm in named_by_variant.items():
        diff = abs(nm["57"]["mean"] - nm["99"]["mean"])
        se = math.sqrt(2 * 0.6 * 0.4 / (N_ICS * len(NAMED_SEEDS)))
        p4[v] = {"diff": diff, "se_diff": se, "within_2se": diff <= 2 * se}
    P["P4"] = {"holds": all(x["within_2se"] for x in p4.values()),
               "evidence": p4}
    # P5: variant discrimination.
    held = [v for v, b in in_band.items() if b]
    if len(held) == 1:
        P["P5"] = {"reading": "LEAD", "variant": held[0],
                   "note": "the only variant under which footnote [13]'s "
                           "60% reproduces; a lead, not a fact"}
    else:
        P["P5"] = {"reading": "INDETERMINATE", "variants_in_band": held}
    # P6: rule 184 under the fixed-point criterion below 0.02.
    P["P6"] = {"holds": all(w["score"] < 0.02 for w in wrong_by_variant.values()),
               "evidence": wrong_by_variant}
    return P


def main(argv=None):
    ws = assert_not_canonical("run the Capcarrere footnote-13 screen")
    t0 = time.time()
    screens = [screen(v, s) for v in VARIANTS for s in SCREEN_SEEDS]
    named_by_variant = {v: named(v) for v in VARIANTS}
    wrong_by_variant = {v: wrong_criterion(v) for v in VARIANTS}
    P = evaluate(screens, named_by_variant, wrong_by_variant)
    out = {
        "protocol": "herakles/specimens/spec-capcarrere-r1-density/PROTOCOL.md",
        "source": "PRL 77(24):4969-4971 footnote [13]; published: 184 and 226 "
                  "at 100%, 57 and 99 at about 60%, N=149, 1000 random ICs",
        "config": {"n_cells": N_CELLS, "steps": STEPS, "n_ics": N_ICS,
                   "variants": VARIANTS, "screen_seeds": SCREEN_SEEDS,
                   "named_seeds": NAMED_SEEDS, "named_rules": NAMED_RULES,
                   "p2_band": P2_BAND, "chance_floor_analytic": 0.5,
                   "attainable_range": [0.0, 1.0]},
        "workspace": ws,
        "runtime_s": round(time.time() - t0, 1),
        "predictions": P,
        "named": named_by_variant,
        "wrong_criterion": wrong_by_variant,
        "screens": screens,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("wrote", os.path.relpath(OUT), "runtime %.1fs" % out["runtime_s"])
    for k, v in P.items():
        if isinstance(v, dict):
            print(k, v.get("holds", v.get("reading")),
                  json.dumps(v.get("evidence", v), default=str)[:300])
        else:
            print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
