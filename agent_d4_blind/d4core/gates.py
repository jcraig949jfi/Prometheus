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
    "ABLATION_MIN_Z": 1.96,        # drop must exceed two-proportion noise
    # NOTE (v4): identifiability accuracy and displacement anisotropy are
    # DIAGNOSTICS ONLY — reported with chance level, CI, and confusion
    # matrix; never gated. The red-team review confirmed a gate on them
    # would relabel menu distinctness as privilege (zero positive
    # calibration; absolute accuracy vs data-dependent chance; anisotropy
    # calibrated on a feature family real substrates never produce).
    # Privilege gating rests on PRIV-3 (ablation) and PRIV-4 (re-coding).
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
    "NAVIGATION_FAILURE",
    "PRIVILEGED_CORRIDOR",
    "REFINDABILITY_FAILURE",
    "REPRESENTATION_SENSITIVE",
    "COUNTERFACTUAL_UNSTABLE",
]
# v2 repair: NAVIGATION_FAILURE is upstream of PRIVILEGED_CORRIDOR. Privilege
# is a claim about HOW navigation succeeds; ablation drops measured around a
# failing baseline are noise (C1 v1 false positive). Privilege gates are
# evaluated only when navigation passes; privilege DIAGNOSTICS are always
# reported.


def _two_prop_z(p1: float, n1: int, p2: float, n2: int) -> float:
    if n1 == 0 or n2 == 0:
        return 0.0
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    se2 = p * (1 - p) * (1 / n1 + 1 / n2)
    if se2 <= 0:
        return 0.0 if p1 == p2 else 99.0
    return abs(p1 - p2) / se2 ** 0.5


def evaluate_gates(res: dict, th: dict = THRESHOLDS) -> dict:
    """res: aggregated results dict for one substrate. Returns flags, primary,
    margins. Never mutates res."""
    flags = []
    margins = {}

    census = res["census"]
    ops = res["op_census"]
    diversity = res.get("diversity", {})
    nav = res["nav_summary"]
    oracle = res.get("oracle", {})

    # --- G1 phenotype mass
    vf = census["viable_frac"]
    # v4: diversity floor counted on census UNION target-generation pool
    # (both generic processes); the census alone caps classes at
    # viable_frac * census_n, making the floor unattainable in
    # [MIN_VIABLE_FRAC, MIN_CLASSES/census_n).
    nc = diversity.get("combined_classes", census["n_classes_viable"])
    margins["viable_frac"] = {"value": vf, "gate": th["MIN_VIABLE_FRAC"],
                              "ci95": census.get("viable_frac_ci95")}
    margins["n_classes"] = {"value": nc, "gate": th["MIN_CLASSES"],
                            "census_only": census["n_classes_viable"]}
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

    # --- G4 navigation (upstream of privilege)
    if not nav_ok and "ACCESSIBILITY_FRAGMENTED" not in flags:
        flags.append("NAVIGATION_FAILURE")

    # --- G5 privilege (evaluated only around a PASSING navigation baseline;
    #     diagnostics always reported)
    priv = False
    abl = res.get("ablation", {})
    worst = None          # max drop among ELIGIBLE cells (diagnostic)
    qualifying = []       # ALL cells that clear drop AND z (v4: no masking —
    #                       a qualifying cell fires regardless of whether a
    #                       larger-drop-but-insignificant cell exists)
    for op_name, strata in abl.get("stratum_drops", {}).items():
        for sname, d in strata.items():
            base, ab = d["baseline"], d["ablated"]
            nb, na = d.get("n_base", 0), d.get("n_abl", 0)
            if base >= th["MIN_HIT_FOR_ABLATION"] and base > 0:
                rel = (base - ab) / base
                z = _two_prop_z(base, nb, ab, na)
                if worst is None or rel > worst[2]:
                    worst = (op_name, sname, rel, z)
                if rel > th["MAX_ABLATION_REL_DROP"] and z >= th["ABLATION_MIN_Z"]:
                    qualifying.append({"op": op_name, "stratum": sname,
                                       "rel_drop": rel, "z": z})
    margins["worst_ablation_drop"] = {
        "value": None if worst is None else {"op": worst[0], "stratum": worst[1],
                                             "rel_drop": worst[2], "z": worst[3]},
        "qualifying_cells": qualifying,
        "gate": th["MAX_ABLATION_REL_DROP"], "z_gate": th["ABLATION_MIN_Z"]}
    if nav_ok and qualifying:
        priv = True
    # PRIV-1 / PRIV-2 diagnostics (never gated; red-team can use them to
    # weaken a verdict narrative, never to strengthen one)
    ident_res = ops.get("identifiability", {})
    aniso = ops.get("anisotropy_top_share")
    margins["identifiability_acc_DIAGNOSTIC"] = {
        "value": ident_res.get("accuracy"), "chance": ident_res.get("chance"),
        "ci95": ident_res.get("ci95")}
    margins["anisotropy_top_share_DIAGNOSTIC"] = {"value": aniso}
    if priv:
        flags.append("PRIVILEGED_CORRIDOR")

    # --- G6 re-findability (best pair navigator)
    refind = best_stats["refind_ratio"] if best_stats else 0.0
    margins["refind_ratio"] = {"value": refind, "gate": th["MIN_REFIND"]}
    if nav_ok and refind < th["MIN_REFIND"]:
        flags.append("REFINDABILITY_FAILURE")

    # --- G7 representation robustness (real substrates only)
    rep = res.get("representation")
    if rep is not None:
        if rep.get("status") == "OK":
            delta = abs(rep["pooled_hit"] - rep["baseline_pooled_hit"])
            zr = _two_prop_z(rep["pooled_hit"], rep.get("n_runs", 0),
                             rep["baseline_pooled_hit"], rep.get("baseline_n", 0))
            margins["representation_delta"] = {"value": delta, "z": zr,
                                               "gate": th["REPRESENTATION_BAND"],
                                               "z_gate": th["ABLATION_MIN_Z"]}
            if delta > th["REPRESENTATION_BAND"] and zr >= th["ABLATION_MIN_Z"]:
                flags.append("REPRESENTATION_SENSITIVE")
        else:
            # v4: the composite requires "not an artifact of encoding" —
            # unmeasured is NOT established. No silent skip.
            margins["representation_delta"] = {"value": "NOT_MEASURED",
                                               "status": rep.get("status")}
            flags.append("REPRESENTATION_SENSITIVE")

    # --- G8 counterfactual stability (real substrates only)
    cf = res.get("counterfactual_stability")
    if cf is not None and cf.get("status") != "OK":
        margins["counterfactual_worst_delta"] = {"value": "NOT_MEASURED"}
        flags.append("COUNTERFACTUAL_UNSTABLE")
    if cf is not None and cf.get("status") == "OK":
        worst_cf, worst_z = 0.0, 0.0
        for v in cf["variants"].values():
            d = abs(v["pooled_hit"] - v["baseline_pooled_hit"])
            if d > worst_cf:
                worst_cf = d
                worst_z = _two_prop_z(v["pooled_hit"], v.get("n_runs", 0),
                                      v["baseline_pooled_hit"], v.get("baseline_n", 0))
        margins["counterfactual_worst_delta"] = {"value": worst_cf, "z": worst_z,
                                                 "gate": th["COUNTERFACTUAL_BAND"],
                                                 "z_gate": th["ABLATION_MIN_Z"]}
        if worst_cf > th["COUNTERFACTUAL_BAND"] and worst_z >= th["ABLATION_MIN_Z"]:
            flags.append("COUNTERFACTUAL_UNSTABLE")

    ordered = [f for f in FLAG_ORDER if f in flags]
    primary = ordered[0] if ordered else "PASS"
    return {"flags": ordered, "primary": primary, "margins": margins,
            "thresholds_status": th["status"]}
