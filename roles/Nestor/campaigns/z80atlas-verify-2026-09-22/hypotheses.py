"""Hypothesis-level decision rules, as ruled by the operator (2026-09-24).

H2 (strong endpoint, primary):
  per seed, arm X "reaches" iff max_causal_replication_depth >= C["CAUSAL_DEPTH"] (5);
  a specimen SUPPORTS iff arm B reaches in >= C["H2_B_MIN"] (8) of its 16 seeds AND arm C
  reaches in <= C["H2_C_MAX"] (2) of 16;
  PANEL_POSITIVE iff >= C["H2_PANEL_MIN_SPECIMENS"] (2) supporting specimens from DIFFERENT
  frozen strata; exactly one supporting specimen is ISOLATED_CANDIDATE, never a panel-level
  positive; otherwise REPLICATION_EVENTS_WITHOUT_PROPAGATION (the default conclusion).
  Secondary readouts ONLY (never a verdict): the same counts at depth >= 2 and >= 3.

A specimen with any bundle missing an arm is INCOMPLETE and never supports.
"""
from __future__ import annotations

from constants import C

SECONDARY_DEPTHS = (2, 3)


def _reach(result, depth):
    return (result.get("max_causal_replication_depth") or 0) >= depth


def h2_specimen(bundles):
    """bundles: list of {"results": {arm_name: summary}} for ONE specimen (16 seeds)."""
    n = len(bundles)
    complete = all({"A_in_situ", "B_reimplant_actual", "C_reimplant_random"}
                   <= set(b["results"]) for b in bundles)
    b_hits = sum(_reach(b["results"]["B_reimplant_actual"], C["CAUSAL_DEPTH"])
                 for b in bundles) if complete else None
    c_hits = sum(_reach(b["results"]["C_reimplant_random"], C["CAUSAL_DEPTH"])
                 for b in bundles) if complete else None
    secondary = {}
    if complete:
        for d in SECONDARY_DEPTHS:
            secondary["depth_ge_%d" % d] = {
                arm: sum(_reach(b["results"][arm], d) for b in bundles)
                for arm in ("A_in_situ", "B_reimplant_actual", "C_reimplant_random")}
    if not complete or n != C["H2_SEEDS"]:
        verdict = "INCOMPLETE"
    elif b_hits >= C["H2_B_MIN"] and c_hits <= C["H2_C_MAX"]:
        verdict = "SUPPORTS"
    else:
        verdict = "DOES_NOT_SUPPORT"
    return {"verdict": verdict, "n_seeds": n, "B_reaching": b_hits, "C_reaching": c_hits,
            "secondary_readouts_only": secondary}


def h2_panel(specimens):
    """specimens: {run_id: {"stratum": [...], "bundles": [...]}} -> panel verdict."""
    per = {sid: dict(h2_specimen(sp["bundles"]), stratum=tuple(sp["stratum"]))
           for sid, sp in specimens.items()}
    supporting = [sid for sid, v in per.items() if v["verdict"] == "SUPPORTS"]
    strata = {per[s]["stratum"] for s in supporting}
    if len(strata) >= C["H2_PANEL_MIN_SPECIMENS"]:
        verdict = "PANEL_POSITIVE"
    elif len(supporting) == 1:
        verdict = "ISOLATED_CANDIDATE"
    elif len(supporting) > 1:
        # Two or more supporting specimens, all in ONE stratum. Not covered by the 2026-09-24
        # ruling; reported under its own name and never as a panel-level positive.
        verdict = "SAME_STRATUM_CANDIDATES"
    else:
        verdict = "REPLICATION_EVENTS_WITHOUT_PROPAGATION"
    return {"verdict": verdict, "supporting": sorted(supporting),
            "distinct_supporting_strata": len(strata),
            "incomplete": sorted(s for s, v in per.items() if v["verdict"] == "INCOMPLETE"),
            "specimens": per}


# --------------------------------------------------------------------------- H1
H1_ARMS = ("gate_off_cost_vm", "gate_on_cost_vm", "gate_off_cost_free", "gate_on_cost_free")


def h1(bundles):
    """bundles: list of {"results": {arm: summary}}. Complete bundles only are used; the
    readout is final held-out competence (`held_max_final`), with crossed_ever and
    crossed_at_final reported beside it and never substituted for it."""
    comp = [b for b in bundles if set(H1_ARMS) <= set(b["results"])]
    if not comp:
        return {"verdict": "INCOMPLETE", "n_complete": 0}
    mean = {a: sum((b["results"][a].get("held_max_final") or 0.0) for b in comp) / len(comp)
            for a in H1_ARMS}
    M = ((mean["gate_on_cost_vm"] + mean["gate_on_cost_free"])
         - (mean["gate_off_cost_vm"] + mean["gate_off_cost_free"])) / 2
    I = ((mean["gate_on_cost_free"] - mean["gate_off_cost_free"])
         - (mean["gate_on_cost_vm"] - mean["gate_off_cost_vm"]))
    rates = {a: {"crossed_ever": sum(bool(b["results"][a].get("crossed_ever")) for b in comp) / len(comp),
                 "crossed_at_final": sum(bool(b["results"][a].get("crossed_at_final")) for b in comp) / len(comp)}
             for a in H1_ARMS}
    if abs(M) >= C["H1_THRESHOLD"] and abs(I) >= C["H1_THRESHOLD"]:
        v = "GATE_EFFECT_AND_COST_INTERACTION"
    elif abs(M) >= C["H1_THRESHOLD"]:
        v = "GATE_EFFECT"
    elif abs(I) >= C["H1_THRESHOLD"]:
        v = "COST_INTERACTION_ONLY"
    else:
        v = "NO_DETECTED_EFFECT"
    return {"verdict": v, "n_complete": len(comp), "n_bundles": len(bundles),
            "M": round(M, 4), "I": round(I, 4), "means_held_final": {a: round(x, 4) for a, x in mean.items()},
            "readouts_only": rates}


# --------------------------------------------------------------------------- H3
H3_ARMS = ("A_easy_plus_migration", "B_homogeneous_same_migration", "C_easy_no_migration")


def _h3_rates(comp, key):
    return {a: sum(bool(b["results"][a].get(key)) for b in comp) for a in H3_ARMS}


def h3(bundles):
    """Primary: POOLED over both pinned cells (declared before launch). Certificate = ruler
    R3 (`has_reservoir_certificate`, material). RESERVOIR_SUPPORTED iff arm A has >=
    H3_MIN_CERTIFICATES certificates AND A's rate exceeds both B's and C's by >=
    H3_SEPARATION. Fewer than the minimum in A is NOT_DEMONSTRATED. The legacy id
    certificate is reported as a sensitivity reading only."""
    comp = [b for b in bundles if set(H3_ARMS) <= set(b["results"])]
    if not comp:
        return {"verdict": "INCOMPLETE", "n_complete": 0}
    n = len(comp)
    cnt = _h3_rates(comp, "has_reservoir_certificate")
    rate = {a: cnt[a] / n for a in H3_ARMS}
    sep_b = rate[H3_ARMS[0]] - rate[H3_ARMS[1]]
    sep_c = rate[H3_ARMS[0]] - rate[H3_ARMS[2]]
    if cnt[H3_ARMS[0]] < C["H3_MIN_CERTIFICATES"]:
        v = "NOT_DEMONSTRATED"
    elif sep_b >= C["H3_SEPARATION"] and sep_c >= C["H3_SEPARATION"]:
        v = "RESERVOIR_SUPPORTED"
    else:
        v = "NO_SEPARATION"
    legacy = {a: sum(bool(b["results"][a].get("id_certificate_legacy")) for b in comp) for a in H3_ARMS}
    cross = {a: sum(bool(b["results"][a].get("crossed_ever")) for b in comp) for a in H3_ARMS}
    return {"verdict": v, "n_complete": n, "n_bundles": len(bundles), "certificates": cnt,
            "rates": {a: round(x, 4) for a, x in rate.items()},
            "separation_vs_B": round(sep_b, 4), "separation_vs_C": round(sep_c, 4),
            "sensitivity_id_certificate_counts": legacy, "readout_crossed_ever_counts": cross}
