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

AMENDED 2026-09-16 (Harmonia ruling be82cdd8b / comms #255, NO-GO on the
preflight as printed; the constants sentences above are SUPERSEDED, kept
for the record):
  - The region gate was ASSERTED (regions_ge8 = N_REGIONS if mean >= 8),
    which assumed popcount deciles hold 1/10 each. Popcount is discrete;
    the exact Binomial(128, 1/2) masses under region_of() range from
    0.069 (pc05, popcount 65 alone) to 0.136 (pc03), and at corpus 120
    P(every region >= 8) = 0.123. Now COMPUTED: region_masses(),
    p_all_regions_ge() (exact DP), expected_neighbourhoods(),
    band_chance_floor() (seeded Monte Carlo, reps printed).
  - Option B adopted (Harmonia's recommendation): the ten regions stand as
    declared and only the corpus grows, CORPUS_OPTION_B = 180 random
    tables, a DECLARED design constant; the gate probability at it is
    computed, never assumed.
  - 3b corrected past both versions: a constant rule's LOCATION is the IC
    sample's majority share p_s (a property of the sample, not the rule;
    all_zero + all_one == 1 exactly); its DISPERSION is sqrt(p_s (1 - p_s))
    exactly, at the ceiling to within 1e-3 and never exactly 0.5 unless
    p_s is. Constants are EXCLUDED from the location primary and are a
    labelled BOUNDARY comparison on the dispersion primary.
  - The six-row baseline arm is THREE distinct-behaviour classes
    (all_zero = centre_00, all_one = centre_11, centre_01 = centre_10);
    the classes are derived from executed outputs, never pooled as
    replicates (HARM-28 applies to functionally identical rules).
  - GO is the mechanical predicate G1-G6 of the ruling, printed as
    go_predicate; Archaeon applies it without returning to Harmonia.
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
CORPUS_OPTION = "B"                  # Harmonia #255 section 3: ten regions as declared, corpus raised
CORPUS_OPTION_B = 180                # DECLARED design constant (random tables); the gate at it is computed
MIN_REGION_N = 8                     # non-degenerate rules a region needs to be tested (3f)
MIN_NEIGHBOURHOOD = 16               # expected non-degenerate rules in the other regions (3f)
G2_THRESHOLD = 0.80                  # P(every region >= MIN_REGION_N) at the issued corpus (G2)
BAND_FLOOR_REPS = 4000               # Monte Carlo corpora for the D3 band chance floor (G4)
BAND_FLOOR_SEED = 20260916


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
# Region occupancy, COMPUTED from the declared edges and assignment
# (Harmonia #255 section 3: the gate was asserted; these functions replace it)
# --------------------------------------------------------------------------
def region_masses(n: int = 128) -> Dict[str, float]:
    """Exact Binomial(n, 1/2) mass of every region under region_of()'s
    assignment (idx = number of edges strictly below the popcount)."""
    out: Dict[str, float] = {"pc{:02d}".format(i): 0.0 for i in range(N_REGIONS)}
    for pc in range(n + 1):
        idx = sum(1 for e in REGION_EDGES if pc > e)
        out["pc{:02d}".format(idx)] += math.comb(n, pc) / 2 ** n
    return out


def _binom_pmf(n: int, x: int, p: float) -> float:
    """Binomial pmf in log space (math.comb overflows float past n ~ 1000)."""
    if p <= 0.0:
        return 1.0 if x == 0 else 0.0
    if p >= 1.0:
        return 1.0 if x == n else 0.0
    return math.exp(math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
                    + x * math.log(p) + (n - x) * math.log1p(-p))


def p_all_regions_ge(corpus: int, masses: Dict[str, float], f: float = 1.0, k: int = MIN_REGION_N) -> float:
    """EXACT P(every region receives >= k non-degenerate tables) when `corpus`
    tables are drawn i.i.d., each landing in region r with probability
    masses[r] * f and being degenerate with probability 1 - f. Dynamic
    programme over regions with the conditional-binomial factorisation of
    the multinomial; the degenerate bin is unconstrained slack."""
    if corpus < k * len(masses):
        return 0.0
    rem = 1.0
    dp: Dict[int, float] = {0: 1.0}
    for m in (masses[r] * f for r in sorted(masses)):
        p = 1.0 if rem <= 1e-12 else min(1.0, m / rem)
        nxt: Dict[int, float] = {}
        for used, pr in dp.items():
            M = corpus - used
            for x in range(k, M + 1):
                w = _binom_pmf(M, x, p)
                if w:
                    nxt[used + x] = nxt.get(used + x, 0.0) + pr * w
        dp = nxt
        rem -= m
        if not dp:
            return 0.0
    return min(1.0, sum(dp.values()))


def min_corpus_for(target: float, masses: Dict[str, float], f: float = 1.0, k: int = MIN_REGION_N, cap: int = 2000) -> Optional[int]:
    """Smallest corpus at which p_all_regions_ge >= target (diagnostic; the
    issued corpus is the DECLARED constant, and G2 is checked at it)."""
    for n in range(k * len(masses), cap + 1):
        if p_all_regions_ge(n, masses, f, k) >= target:
            return n
    return None


def expected_neighbourhoods(corpus: int, masses: Dict[str, float], f: float = 1.0) -> Dict[str, float]:
    """Expected non-degenerate tables in the OTHER regions, per region, from
    the masses (G3) -- not (N_REGIONS - 1) x mean."""
    tot = corpus * f
    return {r: tot * (1.0 - masses[r]) for r in sorted(masses)}


def band_chance_floor(corpus: int, masses: Dict[str, float], f: float = 1.0, *, reps: int = BAND_FLOOR_REPS,
                      seed: int = BAND_FLOOR_SEED, band=D3_BAND, min_n: int = MIN_REGION_N) -> Dict[str, Any]:
    """Monte Carlo D3-style false-fire rate at TRUE ratio 1.0 for the issued
    geometry (G4): occupancies multinomial over (masses x f, 1 - f), values
    i.i.d. normal, each region with n >= min_n tested as var(region) over the
    pooled within-variance of every other region with n >= 2. Reports the
    fraction of corpora with ANY region outside the band and with >= 2."""
    import numpy as np
    rng = np.random.default_rng(seed)
    names = sorted(masses)
    probs = [masses[r] * f for r in names] + [max(0.0, 1.0 - f)]
    any_out = two_out = 0
    tested_total = 0
    for _ in range(reps):
        occ = rng.multinomial(corpus, probs)[:len(names)]
        vals = [rng.standard_normal(int(n)) for n in occ]
        v = [(float(x.var(ddof=1)) if len(x) >= 2 else None) for x in vals]
        out = 0
        for i, n in enumerate(occ):
            if n < min_n:
                continue
            num = sum((len(vals[j]) - 1) * v[j] for j in range(len(names)) if j != i and v[j] is not None)
            df = sum(len(vals[j]) - 1 for j in range(len(names)) if j != i and v[j] is not None)
            if df <= 0 or num <= 0:
                continue
            tested_total += 1
            ratio = v[i] / (num / df)
            if ratio < band[0] or ratio > band[1]:
                out += 1
        any_out += out >= 1
        two_out += out >= 2
    return {"corpus": corpus, "reps": reps, "seed": seed, "band": list(band), "min_region_n": min_n,
            "p_any_region_outside": any_out / reps, "p_two_or_more_outside": two_out / reps,
            "mean_regions_tested_per_corpus": tested_total / reps}


def baseline_classes(named: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Distinct-behaviour classes of the baseline arm, DERIVED from executed
    outputs: rules whose location, dispersion, n_incorrect_at_T and
    mask_digest_at_T are all identical share a class (G5)."""
    keyf = ("location", "dispersion", "n_incorrect_at_T", "mask_digest_at_T")
    classes: Dict[tuple, List[str]] = {}
    for name in {**C3.CONSTANT_RULES, **C3.CENTRE_RULES}:
        o = named[name]
        classes.setdefault(tuple(o.get(k) for k in keyf), []).append(name)
    return {"+".join(sorted(v)): sorted(v) for v in classes.values()}


BASELINE_CLASSES_EXPECTED = {"all_zero+centre_00", "all_one+centre_11", "centre_01+centre_10"}   # Harmonia #255 F3


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


def preflight(n_random: int = PREFLIGHT_RANDOM, seed: int = 0, band_reps: int = BAND_FLOOR_REPS) -> Dict[str, Any]:
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
        named[name] = {"location": o.get(LOCATION_FIELD), "dispersion": o.get(DISPERSION_FIELD),
                       "n_incorrect_at_T": o.get("n_incorrect_at_T"), "mask_digest_at_T": o.get("mask_digest_at_T")}
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
    # region occupancy at the ISSUED corpus, COMPUTED from the masses (G1-G4).
    # `corpus_for_120` is the old ceil(120 / f) figure, kept as a diagnostic;
    # the issued corpus is the declared option-B constant.
    corpus_for_120 = corpus
    corpus = CORPUS_OPTION_B
    masses = region_masses()
    expected_per_region = {r: corpus * f * m for r, m in masses.items()}
    p_ge_k_per_region = {r: sum(_binom_pmf(corpus, x, m * f) for x in range(MIN_REGION_N, corpus + 1)) for r, m in masses.items()}
    p_all = p_all_regions_ge(corpus, masses, f)
    p_all_at_120 = p_all_regions_ge(120, masses, f)
    min_corpus = min_corpus_for(G2_THRESHOLD, masses, f)
    neigh = expected_neighbourhoods(corpus, masses, f)
    floor = {"eligible_regions_only": band_chance_floor(corpus, masses, f, reps=band_reps, seed=BAND_FLOOR_SEED),
             "every_region_n_ge_2_harmonia_convention": band_chance_floor(corpus, masses, f, reps=band_reps, seed=BAND_FLOOR_SEED, min_n=2),
             "note": "Harmonia #255 s3 quoted the floor over every region with n >= 2 (0.136 at 180); the readout tests only regions with n >= MIN_REGION_N, whose floor is the first entry"}
    classes = baseline_classes(named)
    executor_ran_every_arm = all(v.get("location") is not None for v in named.values()) and len(randoms) == n_random
    go = {
        "G1 region masses computed from the declared edges and assignment": {"masses": masses, "pass": abs(sum(masses.values()) - 1.0) < 1e-9},
        "G2 P(every region >= {} non-degenerate) at corpus {} >= {}".format(MIN_REGION_N, corpus, G2_THRESHOLD):
            {"value": p_all, "method": "exact DP over the multinomial", "pass": p_all >= G2_THRESHOLD,
             "at_120_for_the_record": p_all_at_120, "min_corpus_reaching_threshold": min_corpus},
        "G3 expected neighbourhood >= {} for every region, from the masses".format(MIN_NEIGHBOURHOOD):
            {"value": neigh, "pass": all(v >= MIN_NEIGHBOURHOOD for v in neigh.values())},
        "G4 D3 band chance floor at the issued geometry printed in the h2 block": {"value": floor, "pass": True},
        "G5 baseline arm listed as distinct-behaviour classes": {"value": classes, "expected": sorted(BASELINE_CLASSES_EXPECTED),
                                                                   "pass": set(classes) == BASELINE_CLASSES_EXPECTED},
        "G6 unchanged: R-C3-1 PASS, f printed, executor ran every arm, null identical":
            {"R-C3-1": p_mode <= 0.50, "f": f, "executor_ran_every_arm": executor_ran_every_arm,
             "null_identical": all(v["identical"] for v in null.values()),
             "pass": p_mode <= 0.50 and executor_ran_every_arm and all(v["identical"] for v in null.values())},
    }
    go_all = all(v["pass"] for v in go.values())
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
            "corpus_option": CORPUS_OPTION,
            "corpus_random_tables": corpus,
            "corpus_ceil_120_over_f_for_the_record": corpus_for_120,
            "expected_nondegenerate_per_region": expected_per_region,
            "p_region_>=_{}_per_region".format(MIN_REGION_N): p_ge_k_per_region,
            "p_every_region_>=_{}_at_corpus".format(MIN_REGION_N): p_all,
            "p_every_region_>=_{}_at_120_for_the_record".format(MIN_REGION_N): p_all_at_120,
            "expected_neighbourhood_per_region": neigh,
            "neighbourhood_>=16_every_region": all(v >= MIN_NEIGHBOURHOOD for v in neigh.values()),
            "superseded_2026-09-16": "regions_with_>=8_nondegenerate_expected was asserted as N_REGIONS whenever the mean >= 8 (Harmonia #255 s3); now computed above"},
        "go_predicate": {"items": go, "GO": go_all, "ruling": "Harmonia #255 section 6 (be82cdd8b); mechanical, applied by Archaeon"},
        "h2_instrument": ("X1 variance-ratio test across descriptor regions (unit = region); D3 is a LEAD GENERATOR only"
                          if inside else "D3 band may discriminate; report both -- Harmonia rules"),
        "h2_band_chance_floor": floor,
        "primaries": {"location": "per-rule mean of " + LOCATION_FIELD + " over the four IC samples",
                      "dispersion": "per-rule " + DISPERSION_FIELD + " (within-rule spread across ICs)",
                      "multiplicity": "Bonferroni across the two primaries",
                      "constants": "EXCLUDED from the location primary (a constant's location is the IC sample's majority share p_s, "
                                   "a property of the sample; all_zero + all_one == 1 exactly); on the dispersion primary a labelled "
                                   "BOUNDARY comparison at the ceiling sqrt(p_s (1 - p_s)), within 1e-3 of 0.5 and never exactly 0.5 "
                                   "unless p_s is; random ~0.10 (Harmonia #255 s4, superseding 3a/3b and the 2026-09-11 wording)",
                      "baseline_arm": "three distinct-behaviour classes, never pooled as replicates (HARM-28 on functionally identical rules)"},
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
    ap.add_argument("--out", default="archaeon/docs/h0h5/C3_3_PREFLIGHT_B_2026-09-16.json")
    ap.add_argument("--band-reps", type=int, default=BAND_FLOOR_REPS)
    a = ap.parse_args(argv)
    if a.preflight:
        pf = preflight(a.n_random, band_reps=a.band_reps)
        pf["workspace"] = _ws.receipt()
        corpus = pf["gates_printed_before_any_gate"]["corpus_random_tables"]
        rows = plan(corpus) if corpus else []
        pf["plan"] = {"rows": len(rows), "arms": {k: sum(1 for r in rows if r["arm_id"] == k) for k in ("C3-hist", "C3-base", "C3-null", "C3-acq")},
                      "check": {k: v for k, v in check(rows).items() if k != "rows"} if rows else None}
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(pf, f, indent=1, sort_keys=True, default=str)
        print(json.dumps({"random": pf["random"], "gates": pf["gates_printed_before_any_gate"], "inside_band": pf["regions"]["expected_ratio_inside_band"],
                          "GO": pf["go_predicate"]["GO"], "go_items": {k: v["pass"] for k, v in pf["go_predicate"]["items"].items()},
                          "null": pf["null_under_third_criterion"], "plan": pf["plan"]["arms"] if rows else None,
                          "ok_to_issue": pf["plan"]["check"]["ok_to_issue"] if rows else None}, default=str))
        return 0
    ap.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
