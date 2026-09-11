"""C3-3: the CA acquisition corpus on a criterion with an attainable range.

Built from Harmonia's ruling 57c259656 (items 3a-3f) and nothing else:

  3a  TWO PRIMARIES. Location = per-rule mean cellwise_majority_match
      (separates maj from random; cannot separate constants from random).
      Dispersion = within-rule spread of cellwise_majority_match, the row's
      `cellwise_sd_across_ics` (constants sit at its 0.5 ceiling; random
      rules near 0.10). Bonferroni across the two; neither is a fallback.
  3b  The constants sit on a BOUNDARY of the dispersion axis -- but it is the
      CEILING, not zero: under Herakles's measure a constant rule matches
      every cell or none per IC, so per-IC values are 0 or 1, the mean is
      exactly 0.5 and sd_across_ics is exactly 0.5 (the maximum for a 0/1
      variable), while random tables sit near 0.10 (measured in the
      preflight). Harmonia's 3b says "structurally ZERO"; the direction is
      inverted but the ruling's substance stands: a boundary comparison,
      labelled, never an effect size with a two-sided interval. Filed to
      Harmonia for the one-line amendment.
  3c  Units: one rule's location/dispersion -> the IC sample (four shared,
      n = 4); rule vs rule -> paired across the four samples; the population
      of rules -> the rule; D3 / variance ratio across regions -> the
      descriptor region.
  3d  ICC: eligible count (groups with all four samples) printed BEFORE the
      ICC; f near 1 expected, so 120 rules give 120 groups.
  3e  D3 IS NOT THE H2 INSTRUMENT: random rules come from one distribution,
      so regions have near-equal within variance and the ratio sits inside
      D3's band by construction. If the preflight's expected ratio lies in
      [0.3333, 3.0], H2's instrument is the X1 variance-ratio test across
      regions (unit = region) and D3 is a LEAD GENERATOR only.
  3f  BEFORE ISSUE, printed before any gate: support size, p_mode (<= 0.50,
      R-C3-1), f, granularity, corpus = ceil(120 / f) random tables for 120
      non-degenerate rules = 10 regions x 12, and the expected count of
      regions with >= 8 independent non-degenerate rules and a
      neighbourhood of >= 16.

Descriptor regions are DECLARED from the rule table alone (popcount deciles
of Binomial(128, 1/2), analytic quantiles), never from outcomes. The four
IC samples reuse C3-2's seed_root so the same organisms are paired across
the two criteria; the first 120 random tables are C3-2's own.

Not issued without the operator's word.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import statistics
from typing import Any, Dict, List, Optional, Sequence

from . import campaign_c3 as C3
from . import specbuild

KIND = C3.KIND
CAMPAIGN_ID = "C3-3"
SEED_ROOT = C3.SEED_ROOT             # the same four IC samples as C3-2: paired across criteria
SUCCESS = "cellwise_majority_match"
LOCATION_FIELD = "accuracy"          # per-cell mean under this criterion (accuracy_is_per_cell_mean)
DISPERSION_FIELD = "cellwise_sd_across_ics"
TARGET_NONDEGENERATE = 120           # 10 regions x 12 (Harmonia 3f)
N_REGIONS = 10
D3_BAND = (0.3333, 3.0)
PREFLIGHT_RANDOM = 60


# --------------------------------------------------------------------------
# Declared descriptor regions: popcount deciles of Binomial(128, 1/2)
# --------------------------------------------------------------------------
def _binom_cdf_edges(n: int = 128, k: int = N_REGIONS) -> List[int]:
    """Popcount cut points at the analytic deciles of Binomial(n, 1/2)."""
    probs = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    cum, edges, q = 0.0, [], 1
    for i, pr in enumerate(probs):
        cum += pr
        while q < k and cum >= q / k:
            edges.append(i); q += 1
    return edges


REGION_EDGES = _binom_cdf_edges()


def popcount(rule_hex: str) -> int:
    return bin(int(rule_hex, 16)).count("1")


def region_of(rule_hex: str) -> str:
    pc = popcount(rule_hex)
    idx = sum(1 for e in REGION_EDGES if pc > e)
    return "pc{:02d}".format(idx)


def centre1_ones(rule_hex: str) -> int:
    n = int(rule_hex, 16)
    return sum(1 for k in range(128) if (k >> 3) & 1 and (n >> (127 - k)) & 1)


# --------------------------------------------------------------------------
# Specs and plan
# --------------------------------------------------------------------------
def _spec(rule_hex: str, transform: str, hypothesis: str) -> Dict[str, Any]:
    return {
        "spec_version": 3,
        "world": {"seed_root": SEED_ROOT},
        "hypothesis": hypothesis,
        "prediction": {"basis": "Harmonia 57c259656 item 3: location and dispersion primaries; "
                                "nothing here predicts a per-rule value",
                       "success_criterion": SUCCESS},
        "work": {"kind": KIND, "payload": {
            "rule_hex": rule_hex, "radius": C3.RADIUS, "n_cells": C3.N_CELLS, "steps": C3.STEPS,
            "n_ic": C3.N_IC, "ic_density_set": C3.IC_DENSITIES,
            "success_criterion": SUCCESS, "transform": transform}},
        # the executor-level rule is deliberately weak: the science is the analysis (3a)
        "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0,
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE", "aggregate": "all"},
        "pew": {"required": True,
                "encounter_id": "ENC-archaeon-c33-" + hashlib.sha256(
                    "{}|{}|{}|{}".format(rule_hex, transform, SEED_ROOT, SUCCESS).encode()).hexdigest()[:16],
                "players": []},
        "repeat": dict(C3.REPEAT),
    }


def plan(n_random: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    i = 0

    def add(arm, label, rule_hex, transform, hyp):
        nonlocal i
        i += 1
        rows.append({"index": i, "family_id": "fam-" + CAMPAIGN_ID, "arm_id": arm, "label": label,
                     "rule_hex": rule_hex, "transform": transform, "region": region_of(rule_hex),
                     "descriptors": {"popcount": popcount(rule_hex), "centre1_ones": centre1_ones(rule_hex)},
                     "request_key": "{}-{:03d}".format(CAMPAIGN_ID, i),
                     "spec": _spec(rule_hex, transform, hyp)})

    hist = C3.historical_rules()
    for name, rh in hist.items():
        add("C3-hist", name, rh, "none", "historical genome {} under cellwise_majority_match".format(name))
    for name, rh in {**C3.CONSTANT_RULES, **C3.CENTRE_RULES}.items():
        add("C3-base", name, rh, "none", "baseline rule {} (constants: per-IC match 0 or 1, mean 0.5, dispersion at the 0.5 ceiling)".format(name))
    for name, rh in hist.items():
        for t in C3.TRANSFORMS:
            add("C3-null", "{}:{}".format(name, t), rh, t,
                "G1: {} under {} has identical cellwise statistics (exact symmetry)".format(name, t))
    for j in range(n_random):
        add("C3-acq", "random_{:03d}".format(j), C3.random_rule(j), "none",
            "random rule table {} on a criterion whose attainable range is not a point".format(j))
    return rows


# --------------------------------------------------------------------------
# The pre-issue distribution preflight (3f), through Vivarium's own executor
# --------------------------------------------------------------------------
def _run(rule_hex: str, transform: str = "none", seed: int = 0) -> Dict[str, Any]:
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    from viv import executors as X
    return X.run(_spec(rule_hex, transform, "preflight"), seed=seed)


def preflight(n_random: int = PREFLIGHT_RANDOM, seed: int = 0) -> Dict[str, Any]:
    """Everything Harmonia requires printed BEFORE any gate. Offline, one IC
    sample (the seed) per rule, through the registered executor."""
    randoms = []
    for j in range(n_random):
        rh = C3.random_rule(j)
        o = _run(rh, seed=seed)
        randoms.append({"label": "random_{:03d}".format(j), "region": region_of(rh),
                        "location": o.get(LOCATION_FIELD), "dispersion": o.get(DISPERSION_FIELD),
                        "per_cell_mean": o.get("accuracy_is_per_cell_mean")})
    named = {}
    for name, rh in {**C3.historical_rules(), **C3.CONSTANT_RULES, **C3.CENTRE_RULES}.items():
        o = _run(rh, seed=seed)
        named[name] = {"location": o.get(LOCATION_FIELD), "dispersion": o.get(DISPERSION_FIELD)}
    # the null under the third criterion, one genome x three transforms
    g0 = next(iter(C3.historical_rules().items()))
    base = _run(g0[1], seed=seed)
    null = {}
    for t in C3.TRANSFORMS:
        o = _run(g0[1], t, seed=seed)
        null[t] = {"identical": all(o.get(f) == base.get(f) for f in (LOCATION_FIELD, DISPERSION_FIELD, "n_incorrect_at_T", "mask_digest_at_T")),
                   "location": o.get(LOCATION_FIELD)}
    locs = [r["location"] for r in randoms]
    disps = [r["dispersion"] for r in randoms]
    # support, mode, f, granularity (3f + R-C3-1..3)
    counts: Dict[float, int] = {}
    for v in locs:
        counts[v] = counts.get(v, 0) + 1
    p_mode = max(counts.values()) / len(locs)
    nondeg = [r for r in randoms if (r["dispersion"] or 0.0) > 0.0]
    f = len(nondeg) / len(randoms)
    granularity = 1.0 / (C3.N_CELLS * C3.N_IC)
    corpus = math.ceil(TARGET_NONDEGENERATE / f) if f > 0 else None
    # regions: within variance per region and the D3-style ratio (3e)
    by_region: Dict[str, List[float]] = {}
    for r in nondeg:
        by_region.setdefault(r["region"], []).append(r["location"])
    within = {reg: (statistics.variance(v) if len(v) >= 2 else None) for reg, v in by_region.items()}
    ratios = {}
    for reg, v in by_region.items():
        others = [x for o, w in by_region.items() if o != reg and len(w) >= 2 for x in w]
        pooled_num = sum((len(w) - 1) * statistics.variance(w) for o, w in by_region.items() if o != reg and len(w) >= 2)
        pooled_df = sum(len(w) - 1 for o, w in by_region.items() if o != reg and len(w) >= 2)
        if len(v) >= 2 and pooled_df > 0 and pooled_num > 0:
            ratios[reg] = statistics.variance(v) / (pooled_num / pooled_df)
    ratio_vals = list(ratios.values())
    # Harmonia 3e is about the TRUE ratio: random tables are drawn from ONE
    # distribution, so every region's within variance has the same
    # expectation and the true ratio is 1.0 by construction. The per-region
    # ratios observed on ~6 tables per region are F-distributed noise around
    # it (F(5, ~50) spans about [0.2, 2.9] at 95%), so "all observed ratios
    # inside the band" is the wrong test; the expected ratio is what decides.
    expected_true_ratio = 1.0
    inside = D3_BAND[0] <= expected_true_ratio <= D3_BAND[1]
    observed_inside = (sum(1 for x in ratio_vals if D3_BAND[0] <= x <= D3_BAND[1]), len(ratio_vals))
    # expected region occupancy at the corpus size (analytic deciles -> ~1/10 each)
    expected_per_region = (corpus * f / N_REGIONS) if corpus else None
    regions_ge8 = N_REGIONS if expected_per_region and expected_per_region >= 8 else 0
    neighbourhood_ge16 = (N_REGIONS - 1) * expected_per_region if expected_per_region else 0
    return {
        "schema": "archaeon.c3_3.preflight.v0",
        "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "criterion": SUCCESS, "location_field": LOCATION_FIELD, "dispersion_field": DISPERSION_FIELD,
        "n_random_preflighted": n_random, "seed": seed,
        "random": {"location_mean": statistics.mean(locs), "location_min": min(locs), "location_max": max(locs),
                   "location_sd": statistics.pstdev(locs), "dispersion_mean": statistics.mean(d for d in disps if d is not None),
                   "support_size": len(counts), "p_mode": p_mode, "f_nondegenerate": f,
                   "granularity": granularity, "granules_in_range": (max(locs) - min(locs)) / granularity},
        "named": named,
        "null_under_third_criterion": {"genome": g0[0], "transforms": null},
        "regions": {"edges_popcount": REGION_EDGES, "n_regions": N_REGIONS,
                    "occupied_in_preflight": {k: len(v) for k, v in by_region.items()},
                    "within_variance": within, "d3_style_ratio_observed": ratios,
                    "observed_ratios_inside_band": observed_inside,
                    "expected_true_ratio": expected_true_ratio, "expected_ratio_inside_band": inside, "band": D3_BAND,
                    "note": "one generating distribution for every random table => true ratio 1.0; the observed spread at ~6 per region is F noise"},
        "gates_printed_before_any_gate": {
            "R-C3-1 p_mode <= 0.50": p_mode <= 0.50,
            "corpus_random_tables": corpus,
            "expected_nondegenerate_per_region": expected_per_region,
            "regions_with_>=8_nondegenerate_expected": regions_ge8,
            "expected_neighbourhood_size": neighbourhood_ge16,
            "neighbourhood_>=16": bool(neighbourhood_ge16 and neighbourhood_ge16 >= 16)},
        "h2_instrument": ("X1 variance-ratio test across descriptor regions (unit = region); D3 is a LEAD GENERATOR only"
                          if inside else "D3 band may discriminate; report both -- Harmonia rules"),
        "primaries": {"location": "per-rule mean of " + LOCATION_FIELD + " over the four IC samples",
                      "dispersion": "per-rule " + DISPERSION_FIELD + " (within-rule spread across ICs)",
                      "multiplicity": "Bonferroni across the two primaries",
                      "constants": "structural BOUNDARY on the dispersion axis: sd_across_ics = 0.5 exactly (the ceiling for a "
                                   "0/1 per-IC value), random ~0.10; a boundary comparison, labelled (Harmonia 3b says zero; direction filed)"},
    }


def check(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    arms: Dict[str, int] = {}
    for r in rows:
        arms[r["arm_id"]] = arms.get(r["arm_id"], 0) + 1
    out: Dict[str, Any] = {"campaign": CAMPAIGN_ID, "rows": len(rows), "arms": arms, "invalid": [], "blockers": []}
    from .contract import ensure_viv_importable
    ensure_viv_importable()
    from viv import kinds as vk, executors as X
    k = vk.get(KIND)
    out["kind_registered"] = bool(k and k.implemented)
    if not out["kind_registered"]:
        out["blockers"].append({"lane": "vivarium", "what": "ca_density_v0 not registered"}); return out
    for r in rows:
        try:
            specbuild.validate(r["spec"])
        except specbuild.SpecInvalid as exc:
            out["invalid"].append({"index": r["index"], "reason": str(exc)[:240]})
    first: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        first.setdefault(r["arm_id"], r)
    ran, refused = {}, {}
    for arm, r in first.items():
        try:
            o = X.run(r["spec"], seed=0)
            ran[arm] = {"label": r["label"], "location": o.get(LOCATION_FIELD), "dispersion": o.get(DISPERSION_FIELD),
                        "per_cell_mean": o.get("accuracy_is_per_cell_mean")}
        except Exception as exc:                                 # noqa: BLE001
            refused[arm] = "{}: {}".format(type(exc).__name__, str(exc)[:200])
    out["executor_preflight"] = {"ran": ran, "refused": refused}
    if out["invalid"]:
        out["blockers"].append({"lane": "archaeon", "what": "specs rejected by Vivarium's validator", "n": len(out["invalid"])})
    if refused:
        out["blockers"].append({"lane": "archaeon", "what": "executor refuses a payload", "detail": refused})
    out["ok_to_issue"] = not out["invalid"] and not refused
    return out


def main(argv=None) -> int:
    from .. import workspace as _ws
    _ws.assert_not_canonical("run a campaign CLI")               # D-23
    ap = argparse.ArgumentParser(prog="archaeon.producer.campaign_c3_3")
    ap.add_argument("--preflight", action="store_true"); ap.add_argument("--n-random", type=int, default=PREFLIGHT_RANDOM)
    ap.add_argument("--out", default="archaeon/docs/h0h5/C3_3_PREFLIGHT.json")
    a = ap.parse_args(argv)
    if a.preflight:
        pf = preflight(a.n_random)
        corpus = pf["gates_printed_before_any_gate"]["corpus_random_tables"]
        rows = plan(corpus) if corpus else []
        pf["plan"] = {"rows": len(rows), "arms": {k: sum(1 for r in rows if r["arm_id"] == k) for k in ("C3-hist", "C3-base", "C3-null", "C3-acq")},
                      "check": {k: v for k, v in check(rows).items() if k != "rows"} if rows else None}
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(pf, f, indent=1, sort_keys=True, default=str)
        print(json.dumps({"random": pf["random"], "gates": pf["gates_printed_before_any_gate"], "inside_band": pf["regions"]["expected_ratio_inside_band"],
                          "null": pf["null_under_third_criterion"], "plan": pf["plan"]["arms"] if rows else None,
                          "ok_to_issue": pf["plan"]["check"]["ok_to_issue"] if rows else None}, default=str))
        return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
