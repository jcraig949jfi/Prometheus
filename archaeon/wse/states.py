"""Typed scientific / assay states computed FROM MEASUREMENTS (campaign 2, Phase A group B).

assay_states(decl, meas) evaluates the declared preconditions of an experiment against what
was measured and returns every state that fired, with its evidence. disposition_candidate()
turns states + the declared primary comparison into a candidate disposition. The candidate
is machine output; the record's science section may argue with it but must quote it.

States (directive section 9):
  ENGINE_FAILURE            engine errors on the attempt of record
  INSTRUMENT_FAILURE        harness errors on the attempt of record
  INTERVENTION_NOT_APPLIED  a declared intervention's applied counter is 0 on every row of an arm
  RESIDUE_BELOW_FLOOR       an artifact's source population never beat chance
  IMMATURE_ARTIFACT         an artifact's source never solved its own cell
  STREAM_BELOW_THRESHOLD    a sealed stream's maximum source score is below the sealed threshold
  TARGET_UNREACHABLE        the baseline arm reached the target on 0 rows and the table says
                            OBSERVED_UNREACHABLE_AT_BUDGET or the run's own 0/n has n >= 3
  READOUT_CANNOT_EXPRESS    the perfect-memory control is at chance under the readout
  POSITIVE_CONTROL_FAILED   the declared positive control missed its criterion
  UNDERPOWERED              fewer usable rows than the declared minimum
  INCONCLUSIVE / CAPABLE_NEGATIVE / WEAK_POSITIVE / SUPPORTED_POSITIVE   science candidates
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from .reachability import wilson

ASSAY_STATES = ("INTERVENTION_NOT_APPLIED", "RESIDUE_BELOW_FLOOR", "IMMATURE_ARTIFACT", "STREAM_BELOW_THRESHOLD",
                "TARGET_UNREACHABLE", "READOUT_CANNOT_EXPRESS", "POSITIVE_CONTROL_FAILED")
EXECUTION_STATES = ("ENGINE_FAILURE", "INSTRUMENT_FAILURE")
SCIENCE_STATES = ("UNDERPOWERED", "INCONCLUSIVE", "CAPABLE_NEGATIVE", "WEAK_POSITIVE", "SUPPORTED_POSITIVE")
ALL_STATES = EXECUTION_STATES + ASSAY_STATES + SCIENCE_STATES


def _mean(xs: Sequence[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def _ranks(xs: Sequence[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def spearman(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    """Spearman rank correlation with average ranks for ties; None if fewer than 3 points or a
    constant series."""
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    rx, ry = _ranks(list(xs)), _ranks(list(ys))
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxx = sum((a - mx) ** 2 for a in rx); syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sxx * syy) ** 0.5


def arm_values(rows: List[dict], arm_field: str, arm: str, metric: str) -> List[float]:
    return [r[metric] for r in rows if r.get(arm_field) == arm and r.get(metric) is not None]


def assay_states(decl: dict, meas: dict) -> List[dict]:
    """decl (preregistered):
         positive_control      {"arm": str, "metric": str, "min": float, "min_rows": int}   (min_rows rows >= min)
         interventions         [{"arm": str, "counter": str}]                                 (row field that counts applications)
         artifacts             {name: maturity_block}                                         (telemetry.maturity)
         stream                {"threshold": float}
         readout_control       {"arm": str, "metric": str, "chance": float, "min_above": float}
         target                {"baseline_arm": str, "reach_metric": str, "reach_min": float, "reachability_class": str}
         n_min                 int
       meas (measured):
         rows                  list of row dicts; arm_field names the arm column
         arm_field             str
         engine_errors         list;  harness_errors  list
         stream_max_score      float (when decl.stream)
    """
    rows = meas.get("rows", [])
    af = meas.get("arm_field", "arm")
    out: List[dict] = []

    if meas.get("engine_errors"):
        out.append({"state": "ENGINE_FAILURE", "evidence": {"n_errors": len(meas["engine_errors"]), "first": meas["engine_errors"][0]}})
    if meas.get("harness_errors"):
        out.append({"state": "INSTRUMENT_FAILURE", "evidence": {"n_errors": len(meas["harness_errors"]), "first": meas["harness_errors"][0]}})

    for iv in decl.get("interventions", []) or []:
        rs = [r for r in rows if r.get(af) == iv["arm"]]
        if rs and all((r.get(iv["counter"]) or 0) == 0 for r in rs):
            out.append({"state": "INTERVENTION_NOT_APPLIED", "evidence": {"arm": iv["arm"], "counter": iv["counter"], "rows": len(rs)}})

    # maturity blocks are MEASUREMENTS: they arrive in meas["artifacts"] (the harness passes the
    # blocks of every artifact whose maturity gates the assay); decl["artifacts"] is accepted for
    # preregistered blocks (rare: a frozen artifact reused from an earlier experiment).
    for name, m in ((meas.get("artifacts") or decl.get("artifacts") or {})).items():
        if m.get("share_above_chance") == 0.0 and m.get("source_elite_reward", 0.0) <= m.get("chance", 0.0):
            out.append({"state": "RESIDUE_BELOW_FLOOR", "evidence": {"artifact": name, "source_elite_reward": m.get("source_elite_reward")}})
        elif not m.get("solved", False):
            out.append({"state": "IMMATURE_ARTIFACT", "evidence": {"artifact": name, "source_elite_reward": m.get("source_elite_reward"),
                                                                   "solve_threshold": m.get("solve_threshold")}})

    st = decl.get("stream")
    if st and meas.get("stream_max_score") is not None and meas["stream_max_score"] < st["threshold"]:
        out.append({"state": "STREAM_BELOW_THRESHOLD", "evidence": {"stream_max_score": meas["stream_max_score"], "threshold": st["threshold"]}})

    rc = decl.get("readout_control")
    if rc:
        vals = arm_values(rows, af, rc["arm"], rc["metric"])
        if vals and _mean(vals) < rc["chance"] + rc.get("min_above", 0.05):
            out.append({"state": "READOUT_CANNOT_EXPRESS", "evidence": {"arm": rc["arm"], "mean": round(_mean(vals), 4), "chance": rc["chance"]}})

    pc = decl.get("positive_control")
    if pc:
        vals = arm_values(rows, af, pc["arm"], pc["metric"])
        hits = sum(1 for v in vals if v >= pc["min"])
        if vals and hits < pc.get("min_rows", 1):
            out.append({"state": "POSITIVE_CONTROL_FAILED", "evidence": {"arm": pc["arm"], "metric": pc["metric"], "min": pc["min"],
                                                                         "rows_meeting": hits, "rows": len(vals), "values": [round(v, 4) for v in vals]}})

    tg = decl.get("target")
    if tg:
        # baseline_arm "*": the assay is capable if ANY arm reaches (designs whose premise is
        # that the baseline cannot reach and a treatment might)
        vals = ([r[tg["reach_metric"]] for r in rows if r.get(tg["reach_metric"]) is not None] if tg["baseline_arm"] == "*"
                else arm_values(rows, af, tg["baseline_arm"], tg["reach_metric"]))
        reached = sum(1 for v in vals if v >= tg["reach_min"])
        cls = tg.get("reachability_class")
        if vals and reached == 0 and (len(vals) >= 3 or cls == "OBSERVED_UNREACHABLE_AT_BUDGET"):
            out.append({"state": "TARGET_UNREACHABLE", "evidence": {"baseline_arm": tg["baseline_arm"], "reached": reached, "rows": len(vals),
                                                                    "band95_upper": wilson(0, len(vals))[1], "table_class": cls}})

    n_min = decl.get("n_min")
    if n_min:
        arms = sorted({r.get(af) for r in rows})
        short = {a: sum(1 for r in rows if r.get(af) == a) for a in arms}
        low = {a: n for a, n in short.items() if n < n_min}
        if rows and low:
            out.append({"state": "UNDERPOWERED", "evidence": {"n_min": n_min, "arms_below": low}})
    return out


def disposition_candidate(decl: dict, meas: dict, states: Optional[List[dict]] = None) -> dict:
    """decl.primary: {"treatment": arm, "control": arm, "metric": str, "min_effect": float,
    "direction": "greater"|"less"}; decl.battery: list of {"name", "passed": bool|None} (filled by
    the harness from its own falsification runs). Never promotes on sample size alone."""
    states = assay_states(decl, meas) if states is None else states
    names = [s["state"] for s in states]
    for s in EXECUTION_STATES:
        if s in names:
            return {"disposition": s, "reason": "execution state fired", "states": names, "claim_ceiling": "none"}
    for s in ASSAY_STATES:
        if s in names:
            return {"disposition": s, "reason": "assay precondition failed; the scientific question was not posed",
                    "states": names, "claim_ceiling": "none"}
    if "UNDERPOWERED" in names:
        return {"disposition": "UNDERPOWERED", "reason": "fewer rows than the preregistered minimum", "states": names, "claim_ceiling": "none"}
    pr = decl.get("primary")
    rows = meas.get("rows", [])
    af = meas.get("arm_field", "arm")
    if not pr or not rows:
        return {"disposition": "INCONCLUSIVE", "reason": "no primary comparison declared or no rows", "states": names, "claim_ceiling": "none"}
    if pr.get("type") == "rank_correlation":
        # a preregistered predictor: Spearman rho between x and y over the rows, in the declared direction
        xs = [r.get(pr["x"]) for r in rows]; ys = [r.get(pr["y"]) for r in rows]
        pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
        rho = spearman([p[0] for p in pts], [p[1] for p in pts])
        signed = (rho or 0.0) * pr.get("expected_sign", 1)
        ev = {"rho": None if rho is None else round(rho, 4), "n": len(pts), "expected_sign": pr.get("expected_sign", 1), "min_abs_rho": pr["min_abs_rho"]}
        capable = "POSITIVE_CONTROL_FAILED" not in names and "READOUT_CANNOT_EXPRESS" not in names
        if rho is not None and signed >= pr["min_abs_rho"]:
            return {"disposition": "WEAK_POSITIVE", "reason": "predictor rank-correlates in the declared direction at |rho| >= min", "states": names,
                    "claim_ceiling": "weak; one evaluator family", "evidence": ev}
        if capable:
            return {"disposition": "CAPABLE_NEGATIVE", "reason": "predictor does not rank-correlate at the declared strength/direction", "states": names,
                    "claim_ceiling": "negative for this predictor on this evaluator", "evidence": ev}
        return {"disposition": "INCONCLUSIVE", "reason": "assay capability not shown", "states": names, "claim_ceiling": "none", "evidence": ev}
    t = arm_values(rows, af, pr["treatment"], pr["metric"])
    c = arm_values(rows, af, pr["control"], pr["metric"])
    if not t or not c:
        return {"disposition": "INCONCLUSIVE", "reason": "an arm of the primary comparison has no rows", "states": names, "claim_ceiling": "none"}
    effect = _mean(t) - _mean(c)
    if pr.get("direction", "greater") == "less":
        effect = -effect
    # paired sign count when the arms share seeds (common random numbers): how many seeds favour treatment
    pairs = 0; wins = 0
    # rows that do not carry the metric are not pairable (e.g. an arm the harness marked
    # uninformative and returned early); they are skipped, never read as zero (campaign 3 L3-038)
    by_seed_t = {r.get("seed"): r[pr["metric"]] for r in rows if r.get(af) == pr["treatment"] and r.get(pr["metric"]) is not None}
    by_seed_c = {r.get("seed"): r[pr["metric"]] for r in rows if r.get(af) == pr["control"] and r.get(pr["metric"]) is not None}
    for s in by_seed_t:
        if s in by_seed_c:
            pairs += 1
            d = by_seed_t[s] - by_seed_c[s]
            if pr.get("direction", "greater") == "less":
                d = -d
            wins += 1 if d > 0 else 0
    n = min(len(t), len(c))
    ev = {"effect": round(effect, 4), "treatment_mean": round(_mean(t), 4), "control_mean": round(_mean(c), 4),
          "n_treatment": len(t), "n_control": len(c), "paired": pairs, "paired_wins": wins, "min_effect": pr["min_effect"]}
    capable = "POSITIVE_CONTROL_FAILED" not in names and "TARGET_UNREACHABLE" not in names
    if effect >= pr["min_effect"]:
        # the battery's NAMES and rule are preregistered (decl.battery); its outcomes are
        # measurements the harness computes from rows and passes in meas.battery
        battery = meas.get("battery") or decl.get("battery") or []
        attacked = [b for b in battery if b.get("passed") is not None]
        survived = [b for b in attacked if b.get("passed")]
        if n >= 10 and battery and attacked and len(survived) == len(attacked) and len(attacked) == len(battery):
            return {"disposition": "SUPPORTED_POSITIVE", "reason": "effect >= min_effect, n >= 10, every declared falsification attack survived",
                    "states": names, "claim_ceiling": "supported (still one bench, one substrate)", "evidence": ev,
                    "battery": {"declared": len(battery), "attacked": len(attacked), "survived": len(survived)}}
        return {"disposition": "WEAK_POSITIVE", "reason": "effect >= min_effect but n < 10 or a declared falsification attack failed or was not run",
                "states": names, "claim_ceiling": "weak; not for propagation", "evidence": ev,
                "battery": {"declared": len(battery), "attacked": len(attacked), "survived": len(survived)}}
    if capable:
        return {"disposition": "CAPABLE_NEGATIVE", "reason": "assay capable and effect < min_effect", "states": names,
                "claim_ceiling": "negative at this budget/envelope", "evidence": ev}
    return {"disposition": "INCONCLUSIVE", "reason": "effect < min_effect and assay capability not shown", "states": names,
            "claim_ceiling": "none", "evidence": ev}
