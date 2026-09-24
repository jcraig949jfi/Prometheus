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
