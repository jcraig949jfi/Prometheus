"""Round-2 driver: Steps B-E of ROUND2_DISSECTION_PLAN with predictions
frozen BEFORE execution (adaptive record), then execution, then scoring.

    python -m theophrastus.round2 predict   # writes round2/ADAPTIVE_RECORD_01.json
    python -m theophrastus.round2 execute   # runs the planned cells (budget_round2)
    python -m theophrastus.round2 score     # per-IC re-derivation + tests

Predictions use the SIGNED-margin curve of (rule, N) estimated from the
founding per-IC table, applied to the EXACT initial conditions the planned
cell will draw (its repeat seeds are a pure function of the sealed spec).
CHEAT-B predicts one cell from the WRONG rule's curve and must miss.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO, REPO / "vivarium"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
from viv import spec as _vspec                     # noqa: E402
from herakles.evca import core                     # noqa: E402
from theophrastus import crucible as CR            # noqa: E402
from theophrastus import curves as CV              # noqa: E402
from theophrastus import dissect as DS             # noqa: E402
from theophrastus import ecology as E              # noqa: E402
from theophrastus.ledger import Ledger             # noqa: E402

R2 = CV.R2
MIN_N = 20
WIDTH = 0.01


# ----------------------------------------------------------- planned cells
def planned() -> List[dict]:
    P = []
    def add(step, m, w, p, why):
        P.append({"step": step, "cell": E.cell(m, w, p, "NONE", E.SEED_PRIMARY, "round2:" + step, why),
                  "why": why})
    # Step B: constructive / invert / boundary
    add("B", "exp", "W599", "P_d40", "INVERT: majority-0 side at m~0.10; one-class collapse predicts near-failure")
    add("B", "exp", "W599", "P_d60", "INVERT: majority-1 side at m~0.10; predicts ~1.0")
    add("B", "exp", "W149", "P_d40", "same inversion at the smaller world: asymmetry milder")
    add("B", "exp", "W149", "P_d60", "same inversion at the smaller world")
    add("B", "par", "W599", "P_d48", "par asymmetry, opposite sign: d<1/2 side high")
    add("B", "par", "W599", "P_d52", "par asymmetry: d>1/2 side lower")
    add("B", "GKL", "W599", "P_d48", "symmetry control: GKL predicted equal on both sides")
    add("B", "GKL", "W599", "P_d52", "symmetry control")
    add("B", "maj", "W149", "P_d20", "boundary: maj at m~0.30, N=149 predicted mid")
    add("B", "maj", "W599", "P_d20", "boundary shift: maj at m~0.30, N=599 predicted low")
    # Step C: horizon
    add("C", "exp", "W599s", "P_unif", "H4: halved horizon; exact identity with W599/P_unif predicted (digest)")
    add("C", "par", "W599s", "P_unif", "H4: halved horizon; exact identity predicted")
    # Step D: transport to an unused GA genome
    add("D", "particle1", "W149", "P_iid", "transport: H1 invariance + H6 asymmetry predicted (direction unknown)")
    add("D", "particle1", "W149", "P_unif", "transport")
    add("D", "particle1", "W599", "P_iid", "transport")
    add("D", "particle1", "W599", "P_unif", "transport")
    # Step E: third world for the scaling verdict
    add("E", "exp", "W999", "P_iid", "scaling: one-class collapse predicts accuracy -> 0.50 and total asymmetry")
    add("E", "exp", "W999", "P_unif", "scaling")
    add("E", "GKL", "W999", "P_iid", "scaling: sharpening predicts fixed-m success >= N599's")
    add("E", "GKL", "W999", "P_unif", "scaling")
    return P


# -------------------------------------------------------------- prediction
def signed_curve(recs, rule, N) -> Dict[float, tuple]:
    t = defaultdict(lambda: [0, 0])
    for r in recs:
        if r["rule"] == rule and r["N"] == N:
            b = round(math.floor(r["signed_m"] / WIDTH) * WIDTH, 4)
            t[b][0] += int(r["success"]); t[b][1] += 1
    return {b: (v[0], v[1]) for b, v in t.items() if v[1] >= MIN_N}


def cell_margins(cell) -> List[float]:
    spec = cell.to_spec()
    seeds = _vspec.repeat_plan(spec)["seeds"]
    payload = spec["work"]["payload"]
    out = []
    for s in seeds:
        ics = DS.regenerate(payload, int(s))
        k = ics.sum(axis=1)
        out.extend((k / payload["n_cells"] - 0.5).tolist())
    return out


def predict_from(curve_t, ms) -> dict:
    if not curve_t:
        return {"pred": None, "se": None, "note": "no curve at this (rule, N)"}
    keys = sorted(curve_t)
    tot, var, fb = 0.0, 0.0, 0
    for m in ms:
        b = round(math.floor(m / WIDTH) * WIDTH, 4)
        if b not in curve_t:
            b = min(keys, key=lambda x: abs(x - b)); fb += 1
        s, n = curve_t[b]
        p = s / n
        tot += p; var += p * (1 - p) / n
    return {"pred": round(tot / len(ms), 4), "se": round(math.sqrt(var) / len(ms), 4),
            "fallback_ics": fb, "n_ics": len(ms)}


def phase_predict() -> dict:
    recs = CV.load()
    rec = {"record": "ADAPTIVE_RECORD_01", "frozen": True,
           "current_evidence": "round2/stepA_tests.json (H1 pass 8/8; collapse on m not |2k-N|; "
                               "exp/par complement-asymmetric, GKL/maj symmetric; N-trend at fixed m "
                               "rule-specific)",
           "competing_explanations_live": ["H2 nominal-parameterisation artifact (arithmetic; contributes)",
                                           "H3 rule-intrinsic finite-size response (contributes; sign per rule)",
                                           "H4 convergence horizon (untested under P_unif)",
                                           "H6 branch-specific asymmetry (observed on 2 GA rules; transport untested)",
                                           "H7 nothing transportable"],
           "question": "Is the signed-margin curve CONSTRUCTIVE (predicts new single-density cells), "
                       "horizon-independent, transportable to an unused GA genome, and does the N-trend "
                       "continue at W999?",
           "selection_rule": "each cell must have at least one frozen quantitative prediction whose failure "
                             "falsifies a named explanation; cells chosen where the curves at 149 vs 599 or "
                             "d<1/2 vs d>1/2 diverge most (|z|>=4 in step A)",
           "cells": []}
    P = planned()
    for item in P:
        c = item["cell"]; l = c.labels
        rule, N = l["mechanism"], c.world.n_cells
        entry = {"step": item["step"], "labels": l, "cell_id": c.cell_id, "spec_hash": c.spec_hash,
                 "why": item["why"]}
        if item["step"] in ("B", "C") or (item["step"] == "E"):
            ms = cell_margins(c)
            entry["realised_margin_summary"] = {"n": len(ms), "mean_signed_m": round(float(np.mean(ms)), 4),
                                                "min": round(min(ms), 4), "max": round(max(ms), 4)}
            src_N = N if N in (149, 599) else 599
            entry["prediction"] = {**predict_from(signed_curve(recs, rule, src_N), ms),
                                   "from_curve": "%s/N%d signed-margin" % (rule, src_N),
                                   "pass_rule": "|observed - pred| <= 2*sqrt(se^2 + p(1-p)/800)"}
            if item["step"] == "C":
                entry["prediction"]["exact_identity_with"] = E.cell(rule, "W599", "P_unif").spec_hash
                entry["prediction"]["pass_rule"] = "result_digest equal to the W599/P_unif row's => H4 killed"
            if item["step"] == "E":
                entry["prediction"]["note"] = ("curve is N=599's; the frozen QUALITATIVE prediction is the "
                                               "N-trend: exp -> accuracy 0.50 +- 0.04 under P_iid with "
                                               "asymmetry |z|>=10; GKL fixed-m success at m in [0.01,0.03] "
                                               ">= N599's value - 2SE")
        else:  # D
            entry["prediction"] = {"H1": "P_iid vs P_unif at fixed m: no bin |z|>=3 (pass)",
                                   "H6": "signed asymmetry: at least one bin |z|>=3 (GA-branch prediction); "
                                         "direction UNKNOWN and recorded either way",
                                   "N_trend": "UNKNOWN; recorded"}
        rec["cells"].append(entry)
    # CHEAT-B: wrong-rule prediction for exp/W599/P_d40 from GKL's curve
    c = E.cell("exp", "W599", "P_d40")
    ms = cell_margins(c)
    rec["cheat_b"] = {"cell": c.labels, "prediction_from_wrong_curve": predict_from(signed_curve(recs, "GKL", 599), ms),
                      "prediction_from_right_curve": predict_from(signed_curve(recs, "exp", 599), ms),
                      "expected": "the wrong-curve prediction MISSES the observation; the right one passes"}
    rec["outcome_meanings"] = {
        "B pass (>=8 of 10 within 2 SE)": "curve is constructive: SUFFICIENCY established",
        "B fail on exp inversion": "one-class collapse reading killed; asymmetry is not class-side",
        "B fail on maj W599": "boundary shift not real or curve too coarse",
        "C identical digests": "H4 killed",
        "C different digests": "horizon is an ingredient; reopen H4 with a sweep",
        "D H1 pass + H6 asym": "branch-level transport of asymmetry to an unused genome",
        "D H6 symmetric": "asymmetry is rule-specific, not branch-specific",
        "E exp accuracy ~0.50 + asymmetry": "one-class collapse continues; obsolescence = collapse",
        "E GKL sharpening": "sharpening continues; scaling verdict: relative margin + sharpening"}
    (R2 / "ADAPTIVE_RECORD_01.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return rec


# ---------------------------------------------------------------- execute
def phase_execute() -> dict:
    CR.ENGINE_FILE = "budget_round2.json"
    led = Ledger()
    cells = [it["cell"] for it in planned()]
    return CR._run_batch(led, cells, phase="round2", mode="expansion")


# ------------------------------------------------------------------ score
def phase_score() -> dict:
    rec = json.loads((R2 / "ADAPTIVE_RECORD_01.json").read_text(encoding="utf-8"))
    led = Ledger()
    rows = {r["spec_hash"]: r for r in led.read("rows") if r.get("phase") == "round2"}
    # per-IC re-derivation for the new rows (instrument check on each)
    new_recs, vals = [], []
    for r in rows.values():
        recs, val = DS.per_ic_rows(r)
        vals.append({"row": r["row_id"], "labels": r["labels"], "all_match": val["all_match"]})
        new_recs.extend(recs)
    with (R2 / "per_ic_round2.jsonl").open("w", encoding="utf-8") as f:
        for x in new_recs:
            f.write(json.dumps(x) + "\n")
    out = {"rows": len(rows), "rederivation_all_match": all(v["all_match"] for v in vals),
           "validation": vals, "cells": []}
    w599_unif = {}
    for r in led.read("rows"):
        if r["labels"]["world"] == "W599" and r["labels"]["pressure"] == "P_unif" and r["labels"]["seed_root"] == E.SEED_PRIMARY:
            w599_unif[r["labels"]["mechanism"]] = r["result_digest"]
    for entry in rec["cells"]:
        r = rows.get(entry["spec_hash"])
        res = {"step": entry["step"], "labels": entry["labels"], "status": r["status"] if r else "NOT_RUN"}
        if r and r["status"] == "COMPLETED":
            st = CR.X.cell_stat(r, E.REPEAT.count)
            res["observed"] = round(st["p"], 4); res["se_obs"] = round(st["se"], 4)
            pred = entry["prediction"]
            if entry["step"] == "C":
                res["identical_to_W599_P_unif"] = (r["result_digest"] == w599_unif.get(entry["labels"]["mechanism"]))
            elif pred.get("pred") is not None:
                tol = 2 * math.sqrt(pred["se"] ** 2 + st["se"] ** 2)
                res["predicted"] = pred["pred"]; res["tolerance"] = round(tol, 4)
                res["pass"] = abs(st["p"] - pred["pred"]) <= tol
        out["cells"].append(res)
    # CHEAT-B scoring
    cb = rec["cheat_b"]; r = rows.get(E.cell("exp", "W599", "P_d40").spec_hash)
    if r and r["status"] == "COMPLETED":
        st = CR.X.cell_stat(r, E.REPEAT.count)
        w = cb["prediction_from_wrong_curve"]; g = cb["prediction_from_right_curve"]
        out["cheat_b"] = {"observed": round(st["p"], 4), "wrong_curve_pred": w["pred"],
                          "wrong_misses": abs(st["p"] - w["pred"]) > 2 * math.sqrt(w["se"] ** 2 + st["se"] ** 2),
                          "right_curve_pred": g["pred"],
                          "right_passes": abs(st["p"] - g["pred"]) <= 2 * math.sqrt(g["se"] ** 2 + st["se"] ** 2)}
    # Step D tests on particle1; Step E trends
    p1 = [x for x in new_recs if x["rule"] == "particle1"]
    if p1:
        out["step_D_particle1"] = {"H1": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                                          for k, v in CV.h1_ensemble_invariance(p1).items()},
                                   "H6": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                                          for k, v in CV.h6_signed_asymmetry(p1).items()},
                                   "H6_rows": {k: [x for x in v["rows"] if abs(x["z"]) >= 2][:8]
                                               for k, v in CV.h6_signed_asymmetry(p1).items()}}
    old = CV.load()
    e999 = [x for x in new_recs if x["N"] == 999]
    if e999:
        trend = {}
        for rule in ("exp", "GKL"):
            A = [x for x in old if x["rule"] == rule and x["N"] == 599]
            B = [x for x in e999 if x["rule"] == rule]
            cmp_m = CV.compare(CV.table(A, lambda r: CV.bin_m(r["m"])), CV.table(B, lambda r: CV.bin_m(r["m"])))
            trend[rule] = {"N599_vs_N999_by_m": {k: v for k, v in cmp_m.items() if k != "rows"},
                           "low_m_rows": [x for x in cmp_m["rows"] if x["bin"] <= 0.03],
                           "H6_at_999": {k: {kk: vv for kk, vv in v.items() if kk != "rows"}
                                         for k, v in CV.h6_signed_asymmetry(B).items()}}
        out["step_E_scaling"] = trend
    (R2 / "ROUND2_SCORE.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    CR._ws.assert_not_canonical("theophrastus round2")
    if not argv:
        print(__doc__); return 2
    fn = {"predict": phase_predict, "execute": phase_execute, "score": phase_score}[argv[0]]
    print(json.dumps(fn(), indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
