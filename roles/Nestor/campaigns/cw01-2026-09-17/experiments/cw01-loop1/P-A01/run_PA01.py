"""P-A01: e08 re-posed with held-out representative selection and a rate-derived minimum count.

Parent T-E08. Delta: (1) representatives = top-8 of the final population by INTACT score on a
DISJOINT selection seed set 30100..30115 (not train8); (2) a disjoint pilot (4 CONTROL
lineages, seed component pilotB) measures the competent-lineage rate p under that rule;
the minimum eligible count per TAX level is frozen as floor(16 * p_lo), p_lo = p - sqrt(p(1-p)/4),
and production runs only if that count is >= 6 (else this perturbation closes UNREACHABLE
under this rule, cheaply). Unchanged: w13, organism, arms, lambda 390, g_amp 5, 200
generations, held64 assay 30000..30063, statistic (stratified randomisation), overlap rule.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W8 = L.import_world("cw01-e08", "world_e08")
PID, TID, AID = "P-A01", "T-E08", "cw01-loop1-PA01"
SEL = np.arange(30100, 30116)


def reps_by_heldout_selection(cfg, spec, pop, top_k=8):
    s = W8.rollout(spec, pop, SEL)["fit"] / len(SEL)
    idx = np.argsort(-s, kind="stable")[:top_k]
    return W8.take(pop, idx), s[idx]


def assay_lineage(cfg, spec, pop, floor):
    reps, _ = reps_by_heldout_selection(cfg, spec, pop)
    hs = W8.held_seeds(cfg)
    held = W8.rollout(spec, reps, hs)["fit"] / len(hs)
    B = W8.burden(reps, cfg, spec)
    sb = W8.scalar_burden(B, cfg, spec)
    comp = held > floor
    return {"n_competent": int(comp.sum()), "competent": bool(comp.sum() >= 4),
            "C": float(held[comp].mean()) if comp.any() else float(held.mean()),
            "scalar": float(sb[comp].mean()) if comp.any() else float(sb.mean()),
            "held64_all": float(held.mean()), "scalar_all": float(sb.mean()),
            "b": {c: float(B[c][comp].mean() if comp.any() else B[c].mean()) for c in W8.COORDS}}


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e08", AID)
    spec = W8.world_spec(cfg)
    ev, tx, st, floor = cfg["evolution"], cfg["tax"], cfg["stats"], cfg["assay"]["competence_floor_held64"]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "break-inconclusive-confirmatory",
                         "delta": "representatives by intact score on disjoint selection seeds 30100..30115; minimum eligible count per TAX level from a disjoint pilot rate with a one-SE margin; production only if >= 6",
                         "unchanged": "w13, organism, 4 arms x 8 lineages, lambda %.1f, g_amp %d, G %d, held64 assay, stratified randomisation, overlap rule, non-competent excess rule"
                                      % (tx["lambda"], ev["g_amp"], ev["generations"]),
                         "attacks": "D066: eligibility frozen against a marginal pilot; train8-selected representatives do not generalise",
                         "pilot": "4 CONTROL lineages, seed component pilotB", "rule": "min_count = floor(16 * (p - sqrt(p(1-p)/4))); run iff >= 6",
                         "decision": {"COMPLETE": "c_tax < p05 with overlap, counts, excess", "NULL": "counts and overlap ok, c_tax not < p05",
                                      "INCONCLUSIVE": "counts or overlap fail", "UNREACHABLE_UNDER_RULE": "pilot lower bound < 6: no production run"}})
    # ---- disjoint pilot under the NEW selection rule
    pilot = []
    for j in range(4):
        r = W8.evolve(cfg, spec, AID, "CONTROL", j, ev["generations"], lam=0.0, g_amp=None, seed_component="pilotB", history_every=0)
        a = assay_lineage(cfg, spec, r["pop"], floor)
        pilot.append(a)
        print("   pilot %d: competent reps %d/8  held64 all %.1f" % (j, a["n_competent"], a["held64_all"]), flush=True)
    p = float(np.mean([a["competent"] for a in pilot]))
    p_lo = max(0.0, p - np.sqrt(max(p * (1 - p), 1e-9) / 4))
    min_count = int(np.floor(16 * p_lo))
    print("   pilot competent-lineage rate p=%.2f, p_lo=%.2f -> min_count %d" % (p, p_lo, min_count), flush=True)
    if min_count < 6:
        res = {"perturbation_id": PID, "parent": TID, "disposition": "UNREACHABLE_UNDER_RULE",
               "pilot": pilot, "p": p, "p_lo": p_lo, "min_count": min_count, "elapsed_s": round(time.time() - t0, 1),
               "reading": "held-out representative selection does not raise the competent-lineage rate enough to power the contrast; no production run"}
        L.result(HERE, res, ph)
        L.append_evidence(TID, PID, "held-out selection pilot: competent-lineage rate %.2f (lower bound %.2f, min_count %d < 6): unreachable under this rule, no production spent" % (p, p_lo, min_count),
                          True, detail=res, state="ACTIVE", state_reason="eligibility surface confirmed to be about generalisation, not selection rule; next: P-A04's breadth result")
        print("DISPOSITION UNREACHABLE_UNDER_RULE (%.0f s)" % (time.time() - t0))
        return
    # ---- production
    lineages = []
    for arm in cfg["arms"]:
        for li in range(cfg["lineages_per_arm"]):
            r = W8.evolve(cfg, spec, AID, arm, li, ev["generations"], lam=tx["lambda"], g_amp=ev["g_amp"], seed_component="evo", history_every=0)
            a = assay_lineage(cfg, spec, r["pop"], floor)
            a.update({"arm": arm, "lineage": li, "tax": W8.is_tax(arm), "amp": W8.is_amp(arm)})
            lineages.append(a)
            print("   %-8s L%d competent %d/8 C %.1f scalar %.3f" % (arm, li, a["n_competent"], a["C"], a["scalar"]), flush=True)
    comp = [x for x in lineages if x["competent"]]
    n_tax, n_no = sum(x["tax"] for x in comp), sum(not x["tax"] for x in comp)
    excess = {}
    for amp in (False, True):
        t_arm = [x for x in lineages if x["tax"] and x["amp"] == amp]
        c_arm = [x for x in lineages if not x["tax"] and x["amp"] == amp]
        excess["amp" if amp else "sham"] = sum(not x["competent"] for x in t_arm) - sum(not x["competent"] for x in c_arm)
    counts_ok = n_tax >= min_count and n_no >= min_count
    ov = W8.overlap(np.array([x["C"] for x in comp if not x["tax"]]), np.array([x["C"] for x in comp if x["tax"]]), st["overlap_min"]) if (n_tax and n_no) else {"ok": False}
    excess_ok = all(v <= st["noncompetent_excess_max"] for v in excess.values())
    contrast = None
    if counts_ok and ov["ok"]:
        contrast = W8.stratified_contrast([x["scalar"] for x in comp], [x["C"] for x in comp], [x["tax"] for x in comp], [x["amp"] for x in comp],
                                          st["n_perm"], S.rng(AID, "perm"))
    if not excess_ok:
        disp = "INCONCLUSIVE (tax removed competence)"
    elif not (counts_ok and ov["ok"]):
        disp = "INCONCLUSIVE (counts %d/%d vs min %d, overlap %s)" % (n_tax, n_no, min_count, ov["ok"])
    elif contrast["c_tax_below_p05"]:
        disp = "COMPLETE (lower capability-adjusted burden under TAX)"
    else:
        disp = "NULL"
    res = {"perturbation_id": PID, "parent": TID, "disposition": disp, "pilot": pilot, "p": p, "p_lo": p_lo, "min_count": min_count,
           "counts": {"tax": n_tax, "notax": n_no}, "overlap": ov, "excess": excess, "contrast": contrast, "lineages": lineages,
           "per_arm": {a: {"competent_lineages": sum(x["competent"] for x in lineages if x["arm"] == a),
                           "scalar_all": float(np.mean([x["scalar_all"] for x in lineages if x["arm"] == a])),
                           "held64_all": float(np.mean([x["held64_all"] for x in lineages if x["arm"] == a]))} for a in cfg["arms"]},
           "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "e08 re-posed with held-out selection: %s; per arm %s" % (disp, res["per_arm"]), True, detail={"contrast": contrast, "counts": res["counts"]})
    print("DISPOSITION %s (%.0f s)" % (disp, time.time() - t0))


if __name__ == "__main__":
    main()
