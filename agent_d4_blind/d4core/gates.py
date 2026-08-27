"""Frozen gate evaluator and verdict vocabulary.

THRESHOLDS start in CALIBRATING status; they are finalized against the
synthetic controls (instrument calibration) and then FROZEN verbatim into
PREREG-PHASE1.md before any real-substrate measurement. After freeze, this
file must not change (hash recorded in the constitution).

Verdict vocabulary (machine-readable, frozen):
  INSTRUMENT_INVALID          instrument failed synthetic-control validation
  PHENOTYPE_POVERTY           too little viable behavioral diversity
  DISPLACEMENT_COLLAPSE       mutations exist but barely move behavior
  ACCESSIBILITY_FRAGMENTED    navigation fails AND no observed path exists
  PRIVILEGED_CORRIDOR         accessibility depends on a designed mechanism
  NAVIGATION_FAILURE          paths observed, generic navigation cannot use them
  REFINDABILITY_FAILURE       reached once, not reproducibly reachable
  REPRESENTATION_SENSITIVE    conclusions do not survive re-coding
  COUNTERFACTUAL_UNSTABLE     conclusions do not survive menu perturbation
  ACCESSIBILITY_GEOMETRY_ESTABLISHED   all gates passed
  NO_BASIS_PASSED             no substrate passed (overall verdict)

Gate evaluation order = causal upstream-ness; primary flag is the first
failure. All fired flags are reported.
"""
from __future__ import annotations

THRESHOLDS = {
    "status": "CALIBRATING",
    # G1 phenotype mass
    "MIN_VIABLE_FRAC": 0.005,
    "MIN_CLASSES": 250,
    # G2 displacement liveness
    "MAX_IDENTITY": 0.85,          # pooled identity rate over menu transitions
    "MIN_EFFECTIVE": 0.05,         # pooled non-identity & viable-child rate
    "MIN_ALIVE_OPS": 3,            # ops with effective_rate >= 0.02
    # G3 fragmentation attribution
    "ORACLE_FAR_MIN": 0.20,
    # G4 privilege
    "MIN_HIT_FOR_ABLATION": 0.15,  # per-stratum baseline needed to judge drop
    "MAX_ABLATION_REL_DROP": 0.60,
    "IDENT_ACC_HI": 0.30,          # calibrated between C5 and C3
    "ANISO_HI": 0.75,              # calibrated between C5 and C3
    # G5 navigation
    "MIN_POOLED_HIT": 0.25,        # each of the competitive pair
    "MIN_FAR_HIT": 0.10,           # best pair navigator, far stratum
    # G6 re-findability
    "MIN_REFIND": 0.40,
    # G7/G8 robustness bands (real substrates only)
    "REPRESENTATION_BAND": 0.15,   # abs change in pooled hit under re-coding
    "COUNTERFACTUAL_BAND": 0.15,   # abs change under reweight/radius
    "EPS_HIT": 0.10,
    "EPS_DENS": 0.15,
}

FLAG_ORDER = [
    "PHENOTYPE_POVERTY",
    "DISPLACEMENT_COLLAPSE",
    "ACCESSIBILITY_FRAGMENTED",
    "PRIVILEGED_CORRIDOR",
    "NAVIGATION_FAILURE",
    "REFINDABILITY_FAILURE",
    "REPRESENTATION_SENSITIVE",
    "COUNTERFACTUAL_UNSTABLE",
]


def evaluate_gates(res: dict, th: dict = THRESHOLDS) -> dict:
    """res: aggregated results dict for one substrate. Returns flags, primary,
    margins. Never mutates res."""
    flags = []
    margins = {}

    census = res["census"]
    ops = res["op_census"]
    nav = res["nav_summary"]
    oracle = res.get("oracle", {})

    # --- G1 phenotype mass
    vf = census["viable_frac"]
    nc = census["n_classes_viable"]
    margins["viable_frac"] = {"value": vf, "gate": th["MIN_VIABLE_FRAC"],
                              "ci95": census.get("viable_frac_ci95")}
    margins["n_classes"] = {"value": nc, "gate": th["MIN_CLASSES"]}
    if vf < th["MIN_VIABLE_FRAC"] or nc < th["MIN_CLASSES"]:
        flags.append("PHENOTYPE_POVERTY")

    # --- G2 displacement liveness
    ident = ops["pooled_identity_rate"]
    eff = ops["pooled_effective_rate"]
    alive = ops["n_alive_ops"]
    margins["pooled_identity"] = {"value": ident, "gate": th["MAX_IDENTITY"]}
    margins["pooled_effective"] = {"value": eff, "gate": th["MIN_EFFECTIVE"]}
    margins["n_alive_ops"] = {"value": alive, "gate": th["MIN_ALIVE_OPS"]}
    if ident > th["MAX_IDENTITY"] or eff < th["MIN_EFFECTIVE"] or alive < th["MIN_ALIVE_OPS"]:
        flags.append("DISPLACEMENT_COLLAPSE")

    # --- navigation pass/fail (used by G3 attribution and G5)
    pair_hits = nav.get("pair_pooled_hits", [])
    best_nav = nav.get("best_pair_nav")
    best_stats = nav["per_navigator"].get(best_nav) if best_nav else None
    far_hit = None
    if best_stats and "far" in best_stats["strata"]:
        far_hit = best_stats["strata"]["far"]["hit_rate"]
    nav_ok = (len(pair_hits) >= 2
              and all(h >= th["MIN_POOLED_HIT"] for h in pair_hits)
              and far_hit is not None and far_hit >= th["MIN_FAR_HIT"])
    margins["pair_pooled_hits"] = {"value": pair_hits, "gate": th["MIN_POOLED_HIT"]}
    margins["best_far_hit"] = {"value": far_hit, "gate": th["MIN_FAR_HIT"]}

    # --- G3 fragmentation (topology attribution)
    ofar = oracle.get("strata_reach", {}).get("far")
    margins["oracle_far_reach"] = {"value": ofar, "gate": th["ORACLE_FAR_MIN"]}
    if (not nav_ok) and ofar is not None and ofar < th["ORACLE_FAR_MIN"]:
        flags.append("ACCESSIBILITY_FRAGMENTED")

    # --- G4 privilege
    priv = False
    abl = res.get("ablation", {})
    worst = None
    for op_name, strata in abl.get("stratum_drops", {}).items():
        for sname, d in strata.items():
            if d["baseline"] >= th["MIN_HIT_FOR_ABLATION"] and d["baseline"] > 0:
                rel = (d["baseline"] - d["ablated"]) / d["baseline"]
                if worst is None or rel > worst[2]:
                    worst = (op_name, sname, rel)
    margins["worst_ablation_drop"] = {
        "value": None if worst is None else {"op": worst[0], "stratum": worst[1],
                                             "rel_drop": worst[2]},
        "gate": th["MAX_ABLATION_REL_DROP"]}
    if worst is not None and worst[2] > th["MAX_ABLATION_REL_DROP"]:
        priv = True
    ident_res = ops.get("identifiability", {})
    aniso = ops.get("anisotropy_top_share")
    if (ident_res.get("status") == "OK" and aniso is not None
            and ident_res["accuracy"] > th["IDENT_ACC_HI"] and aniso > th["ANISO_HI"]):
        priv = True
    margins["identifiability_acc"] = {
        "value": ident_res.get("accuracy"), "chance": ident_res.get("chance"),
        "ci95": ident_res.get("ci95"), "gate_with_aniso": th["IDENT_ACC_HI"]}
    margins["anisotropy_top_share"] = {"value": aniso, "gate_with_acc": th["ANISO_HI"]}
    if priv:
        flags.append("PRIVILEGED_CORRIDOR")

    # --- G5 navigation
    if not nav_ok and "ACCESSIBILITY_FRAGMENTED" not in flags:
        flags.append("NAVIGATION_FAILURE")

    # --- G6 re-findability (best pair navigator)
    refind = best_stats["refind_ratio"] if best_stats else 0.0
    margins["refind_ratio"] = {"value": refind, "gate": th["MIN_REFIND"]}
    if nav_ok and refind < th["MIN_REFIND"]:
        flags.append("REFINDABILITY_FAILURE")

    # --- G7 representation robustness (real substrates only)
    rep = res.get("representation")
    if rep is not None and rep.get("status") == "OK":
        delta = abs(rep["pooled_hit"] - rep["baseline_pooled_hit"])
        margins["representation_delta"] = {"value": delta, "gate": th["REPRESENTATION_BAND"]}
        if delta > th["REPRESENTATION_BAND"]:
            flags.append("REPRESENTATION_SENSITIVE")

    # --- G8 counterfactual stability (real substrates only)
    cf = res.get("counterfactual_stability")
    if cf is not None and cf.get("status") == "OK":
        worst_cf = max((abs(v["pooled_hit"] - v["baseline_pooled_hit"])
                        for v in cf["variants"].values()), default=0.0)
        margins["counterfactual_worst_delta"] = {"value": worst_cf,
                                                 "gate": th["COUNTERFACTUAL_BAND"]}
        if worst_cf > th["COUNTERFACTUAL_BAND"]:
            flags.append("COUNTERFACTUAL_UNSTABLE")

    ordered = [f for f in FLAG_ORDER if f in flags]
    primary = ordered[0] if ordered else "PASS"
    return {"flags": ordered, "primary": primary, "margins": margins,
            "thresholds_status": th["status"]}
