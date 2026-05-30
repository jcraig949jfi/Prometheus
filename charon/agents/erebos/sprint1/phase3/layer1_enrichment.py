"""Phase 3.B — Layer-1 verdict enrichment (ITER-57b).

Run the Phase 1A retrofitted detectors against real Mossinghoff
catalog at MULTIPLE parameter settings. Each call is a REAL Layer-1
verdict on REAL data. Emit ~50 enrichment rows to a separate file
(not the production ledger) so Phase 3.0 smoke can be re-run with
the enriched data.

## What "enrichment" means here

The current real ledger (570 rows) is dominated by
`*_pending` and `*_not_yet_implemented` kps -- not the kind of
rich Layer-1 verdicts Layer 2 was designed to navigate. The four
Phase 1A retrofits (G02 WY, G10 BOCPD, G23 bootstrap, G11 MC G-test)
DO produce rich verdicts, but they've been run only once or twice
in production.

This script calls the underlying primitives with parameter
variation to generate ~50 distinct Layer-1 verdicts:

  - G23 bootstrap CI with 20 different seeds
  - G11 MC G-test with 20 different seeds
  - G10 BOCPD with 5 different hazard rates (deterministic per
    hazard but each is a distinct sweep)
  - G02 WY with 5 different multi-binary seed configurations

Total target: ~50 enriched rows.

Output: enriched ledger rows appended to
`charon/agents/erebos/state/kill_ledger_enriched.jsonl`. This is
SEPARATE from production state — Phase 3.0 smoke can load both
files combined.
"""
from __future__ import annotations

import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from charon.agents.stygian.loaders._bocpd import detect_changepoints
from charon.agents.stygian.loaders._bootstrap_ci import bootstrap_ci
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
    survival_fraction,
)


ENRICHMENT_PATH = Path(
    "charon/agents/erebos/state/kill_ledger_enriched.jsonl"
)
SWEEP_THRESHOLDS = [M_LEHMER, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50]


def _make_row(
    plugin_id: str,
    kill_pattern: str,
    domain: str,
    verdict: str,
    extra: dict,
) -> dict:
    """Construct an enrichment row in the same shape as production
    ledger rows (subset of fields used by Layer 2 primitives)."""
    return {
        "record_id": uuid.uuid4().hex,
        "batch_id": f"phase3_b_enrichment_{plugin_id}",
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "generator_id": "erebos",
        "claim_kind": f"erebos_{plugin_id}_claim",
        "kill_pattern": kill_pattern,
        "verdict": verdict,
        "claim_payload": {
            "problem_id": "BL-C-001",  # Mahler / Lehmer context
            "enrichment_extra": extra,
        },
        "kill_vector": extra,  # rich raw layer-1 output
        "method": "phase3_b_enrichment",
        "convergence_status": "evaluated",
        "parent_record_id": None,
        "sigma_claim_id": None,
        "sigma_symbol_ref": None,
        "step_trace": None,
        "training_weight": None,
        "extras": {},
        "info_density": None,
        "novelty_estimate": None,
        "diversity_score": None,
        "precision_dps": None,
        "canonical_claim_text": (
            f"enrichment[{plugin_id}]: {kill_pattern}"
        ),
    }


def _enrich_g10_bocpd(values: list[float]) -> list[dict]:
    """G10 BOCPD with 5 different hazard rates (deterministic per
    hazard but each is a distinct sweep result)."""
    rows: list[dict] = []
    survivals = [survival_fraction(values, t) for t in SWEEP_THRESHOLDS]
    hazards = [0.05, 0.10, 0.125, 0.20, 0.30]
    for h in hazards:
        result = detect_changepoints(
            observations=survivals,
            hazard_rate=h,
            prior_kappa=0.1,
            prior_alpha=0.5,
            prior_beta=0.001,
        )
        # Heuristic verdict: changepoint detected if any interior
        # cell has run-length-based signal above 0.30 (matches
        # original loader's POSTERIOR_THRESHOLD)
        interior = result.changepoint_probabilities[2:]
        spike = max(interior) if interior else 0.0
        if spike > 0.30:
            verdict = "REJECTED"
            kp = "sharp_boundary_detected_bocpd"
        else:
            verdict = "PROMOTED"
            kp = "smooth_decay_bocpd"
        rows.append(_make_row(
            plugin_id="g10_boundary",
            kill_pattern=kp,
            domain="mahler",
            verdict=verdict,
            extra={
                "hazard_rate": h,
                "max_interior_signal": spike,
                "survivals_head": survivals[:4],
            },
        ))
    return rows


def _enrich_g23_bootstrap(degrees_errs: list[tuple[int, float]]) -> list[dict]:
    """G23 bootstrap CI with 20 different seeds."""
    import math
    rows: list[dict] = []
    def slope_stat(pts):
        if len(pts) < 2:
            return None
        xs = [math.log(d) for d, _ in pts if d > 0]
        ys = [math.log(e) for _, e in pts if e > 0]
        if len(xs) != len(ys) or len(xs) < 2:
            return None
        n = len(xs)
        mx = sum(xs) / n; my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        return num / den if den else None

    for seed in range(20):
        ci = bootstrap_ci(
            data=degrees_errs,
            statistic_fn=slope_stat,
            n_resamples=500,
            confidence_level=0.95,
            seed=seed,
        )
        # Classify per the original loader's bands
        if ci.ci_lower is None or ci.ci_upper is None:
            continue
        lo, hi = ci.ci_lower, ci.ci_upper
        if lo >= -1.5 and hi <= -0.5:
            verdict = "PROMOTED"
            kp = "decay_consistent_with_1_over_N"
        elif lo > -0.5:
            verdict = "REJECTED"
            kp = "error_term_does_not_decay_bootstrap"
        elif hi < -1.5:
            verdict = "REJECTED"
            kp = "decay_faster_than_1_over_N_bootstrap"
        else:
            verdict = "UNCERTAIN"
            kp = "decay_slope_ci_straddles_boundary"
        rows.append(_make_row(
            plugin_id="g23_asymptotic_limit",
            kill_pattern=kp,
            domain="mahler",
            verdict=verdict,
            extra={
                "seed": seed,
                "slope_observed": ci.statistic_observed,
                "ci_lower": ci.ci_lower,
                "ci_upper": ci.ci_upper,
            },
        ))
    return rows


def _enrich_g11_mc_gtest(entries: list[dict]) -> list[dict]:
    """G11 MC G-test with 20 different seeds.

    Re-implement the core G-statistic + permutation null with a
    seed knob, calling the same shape as the production loader.
    """
    from collections import Counter
    rows: list[dict] = []

    def _cube_key(e):
        return (
            bool(e.get("salem_class")),
            bool(e.get("is_smyth_extremal")),
            int(e.get("degree", 0)) % 2 == 0,
        )

    cube_total: Counter = Counter()
    cube_survivors: Counter = Counter()
    flag_pool: list[bool] = []
    keys_per_record: list[tuple] = []
    for e in entries:
        k = _cube_key(e); cube_total[k] += 1
        is_dm = bool(e.get("degree_minimum"))
        if is_dm:
            cube_survivors[k] += 1
        flag_pool.append(is_dm)
        keys_per_record.append(k)

    total_n = sum(cube_total.values())
    total_s = sum(cube_survivors.values())
    if total_s == 0 or total_n == 0:
        return rows
    rate = total_s / total_n

    import math
    def _g_stat(survivors: Counter) -> float:
        g = 0.0
        for k, n in cube_total.items():
            o = survivors.get(k, 0); e = rate * n
            if e < 1e-9 or o <= 0:
                continue
            g += 2.0 * o * math.log(o / e)
        return g

    g_obs = _g_stat(cube_survivors)
    for seed in range(20):
        rng = random.Random(seed)
        pool_copy = list(flag_pool)
        n_at_or_above = 0
        for _ in range(500):  # 500 permutations per seed
            rng.shuffle(pool_copy)
            null_surv: Counter = Counter()
            for k, f in zip(keys_per_record, pool_copy):
                if f:
                    null_surv[k] += 1
            if _g_stat(null_surv) >= g_obs:
                n_at_or_above += 1
        p_value_mc = n_at_or_above / 500
        if p_value_mc < 0.05:
            verdict = "PROMOTED"
            kp = "degree_minima_concentration_mc_significant"
        else:
            verdict = "REJECTED"
            kp = "flag_distribution_uniform_under_mc_null"
        rows.append(_make_row(
            plugin_id="g11_exception_miner",
            kill_pattern=kp,
            domain="mahler",
            verdict=verdict,
            extra={
                "seed": seed,
                "g_observed": g_obs,
                "p_value_mc": p_value_mc,
                "n_permutations": 500,
            },
        ))
    return rows


def _enrich_g02_wy(entries: list[dict]) -> list[dict]:
    """G02 Westfall-Young multi-binary with 5 different seed sets.

    Test 3 binaries (salem_class, is_smyth_extremal, degree_parity)
    against permutation null; emit 3 rows per seed = 15 rows.
    """
    rows: list[dict] = []

    def _binary_label(e, which: str) -> bool:
        if which == "salem":
            return bool(e.get("salem_class"))
        if which == "smyth":
            return bool(e.get("is_smyth_extremal"))
        return int(e.get("degree", 0)) % 2 == 0

    M_THRESHOLD = 1.30
    binaries = ["salem", "smyth", "degree_parity"]
    for seed in range(5):
        # Filter to below-threshold subset
        below = [e for e in entries
                 if float(e.get("mahler_measure", 0)) < M_THRESHOLD]
        above = [e for e in entries
                 if float(e.get("mahler_measure", 0)) >= M_THRESHOLD]
        if not below or not above:
            continue
        rng = random.Random(seed)
        for which in binaries:
            obs_below = sum(_binary_label(e, which) for e in below)
            obs_above = sum(_binary_label(e, which) for e in above)
            obs_div = (
                abs(obs_below / len(below) - obs_above / len(above))
                if below and above else 0
            )
            # Permutation null
            all_e = below + above
            labels = [_binary_label(e, which) for e in all_e]
            n_below = len(below)
            n_extreme = 0
            for _ in range(200):
                rng.shuffle(labels)
                p_below_rate = sum(labels[:n_below]) / n_below
                p_above_rate = sum(labels[n_below:]) / len(above)
                if abs(p_below_rate - p_above_rate) >= obs_div:
                    n_extreme += 1
            p_val = n_extreme / 200
            if p_val < 0.05:
                verdict = "PROMOTED"
                kp = f"contrast_separation_{which}_promoted"
            else:
                verdict = "REJECTED"
                kp = f"contrast_separation_{which}_rejected"
            rows.append(_make_row(
                plugin_id="g02_contrast",
                kill_pattern=kp,
                domain="mahler",
                verdict=verdict,
                extra={
                    "seed": seed,
                    "binary": which,
                    "obs_divergence": obs_div,
                    "permutation_p": p_val,
                },
            ))
    return rows


def run_enrichment() -> dict:
    """Run all four enrichment passes; append rows to enriched
    ledger; return summary."""
    entries = load_non_cyclotomic_mahler_entries()
    values = [float(e["mahler_measure"]) for e in entries]

    # Per-degree min for G23 bootstrap inputs
    EPSILON = 1e-9
    by_degree: dict[int, float] = {}
    for e in entries:
        d = e.get("degree"); m = float(e.get("mahler_measure", 0))
        if d is None or m <= 1.0 + EPSILON:
            continue
        if d not in by_degree or m < by_degree[d]:
            by_degree[d] = m
    degrees_errs = [
        (d, m - M_LEHMER) for d, m in by_degree.items()
        if m - M_LEHMER > EPSILON
    ]
    degrees_errs.sort()

    print(f"Catalog: {len(entries)} entries; {len(degrees_errs)} per-degree positive-error points")

    all_rows: list[dict] = []
    t0 = time.time()
    print("Running G10 BOCPD x5 hazards...")
    g10_rows = _enrich_g10_bocpd(values)
    print(f"  +{len(g10_rows)} rows ({time.time()-t0:.1f}s)")
    all_rows.extend(g10_rows)

    t0 = time.time()
    print("Running G23 bootstrap CI x20 seeds...")
    g23_rows = _enrich_g23_bootstrap(degrees_errs)
    print(f"  +{len(g23_rows)} rows ({time.time()-t0:.1f}s)")
    all_rows.extend(g23_rows)

    t0 = time.time()
    print("Running G11 MC G-test x20 seeds...")
    g11_rows = _enrich_g11_mc_gtest(entries)
    print(f"  +{len(g11_rows)} rows ({time.time()-t0:.1f}s)")
    all_rows.extend(g11_rows)

    t0 = time.time()
    print("Running G02 WY x5 seeds x 3 binaries...")
    g02_rows = _enrich_g02_wy(entries)
    print(f"  +{len(g02_rows)} rows ({time.time()-t0:.1f}s)")
    all_rows.extend(g02_rows)

    ENRICHMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ENRICHMENT_PATH, "w") as f:
        for r in all_rows:
            f.write(json.dumps(r) + "\n")

    return {
        "n_total_enriched_rows": len(all_rows),
        "n_g10": len(g10_rows),
        "n_g23": len(g23_rows),
        "n_g11": len(g11_rows),
        "n_g02": len(g02_rows),
        "output_path": str(ENRICHMENT_PATH),
    }


if __name__ == "__main__":
    summary = run_enrichment()
    print()
    print("=" * 70)
    print("Phase 3.B -- Enrichment summary")
    print("=" * 70)
    for k, v in summary.items():
        print(f"  {k:30s} = {v}")
