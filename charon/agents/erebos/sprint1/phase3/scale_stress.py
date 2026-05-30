"""Phase 3.K — Scale stress test (ITER-66).

Phase 3.H produced p=0.055 — borderline significance. The natural
resolution test: 5x more enrichment from real detectors. If signal
scales, p drops below 0.05. If it washes out, p rises and the
architectural claim collapses.

## Protocol

1. Generate 5x more Mahler enrichment (300 rows: G23 x 60 seeds,
   G11 x 60 seeds, G02 x 60 seeds, G10 x 15 hazards).
2. Generate 5x more BSD enrichment (150+ rows).
3. Append to a SEPARATE scale-stress ledger file (don't pollute
   original).
4. Re-run cross-cell smoke on the scale-stress combined ledger.
5. Re-run permutation null with N=200 trials.
6. Compare: do actionable deltas scale, hold, or collapse?
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path

from charon.agents.erebos._cross_cell_motif import (
    conditional_kp_recommendations,
    extract_cooccurrence_motifs,
    per_plugin_majority,
)
from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
    _normalize_row,
)
from charon.agents.stygian.loaders._bootstrap_ci import bootstrap_ci
from charon.agents.stygian.loaders._bsd_helpers import (
    get_conductor, get_rank, get_regulator, load_bsd_entries,
)
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER, load_non_cyclotomic_mahler_entries, survival_fraction,
)
from charon.agents.stygian.loaders.composition_bsd_rank_strata import (
    _log_log_slope,
)


SCALE_LEDGER = Path("charon/agents/erebos/state/kill_ledger_scale_stress.jsonl")
N_PERMUTATIONS = 200
MIN_COOCCURRENCE = 3
MIN_LIFT = 1.5
SEED = 2026


def _make_row(plugin_id, kill_pattern, verdict, input_signature, domain, extra):
    return {
        "record_id": uuid.uuid4().hex,
        "batch_id": f"phase3_k_scale_{plugin_id}",
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "generator_id": "erebos",
        "claim_kind": f"erebos_{plugin_id}_claim",
        "kill_pattern": kill_pattern,
        "verdict": verdict,
        "claim_payload": {"problem_id": "BL-C-001" if domain == "mahler" else "BL-B-001",
                          "domain": domain, "extra": extra},
        "kill_vector": extra,
        "method": "phase3_k_scale_enrichment",
        "convergence_status": "evaluated",
        "input_signature": input_signature,
        "parent_record_id": None,
        "canonical_claim_text": f"scale[{plugin_id}]: {kill_pattern}",
    }


def _bsd_enrichment(rng: random.Random) -> list[dict]:
    rows = []
    entries = load_bsd_entries()
    rank1_pts = [(get_conductor(e), get_regulator(e)) for e in entries
                 if get_rank(e) == 1 and get_regulator(e) and get_regulator(e) > 0]
    rank2_pts = [(get_conductor(e), get_regulator(e)) for e in entries
                 if get_rank(e) == 2 and get_regulator(e) and get_regulator(e) > 0]
    for seed in range(50):
        subsample = rng.sample(rank1_pts, min(100, len(rank1_pts)))
        ci = bootstrap_ci(subsample, _log_log_slope, n_resamples=100, seed=seed)
        if ci.statistic_observed is None or ci.ci_lower is None:
            continue
        if ci.ci_lower > 0:
            kp = "bsd_regulator_grows_with_conductor_rank1"; v = "PROMOTED"
        elif ci.ci_upper < 0:
            kp = "bsd_regulator_shrinks_with_conductor_rank1"; v = "REJECTED"
        else:
            kp = "bsd_regulator_independent_of_conductor_rank1"; v = "REJECTED"
        rows.append(_make_row("g23_asymptotic_limit", kp, v,
                              f"bsd_scale:rank1_seed{seed}", "BSD",
                              {"seed": seed, "rank": 1}))
    for seed in range(50):
        subsample = rng.sample(rank2_pts, min(60, len(rank2_pts)))
        ci = bootstrap_ci(subsample, _log_log_slope, n_resamples=100, seed=seed)
        if ci.statistic_observed is None or ci.ci_lower is None:
            continue
        if ci.ci_lower > 0:
            kp = "bsd_regulator_grows_with_conductor_rank2"; v = "PROMOTED"
        elif ci.ci_upper < 0:
            kp = "bsd_regulator_shrinks_with_conductor_rank2"; v = "REJECTED"
        else:
            kp = "bsd_regulator_independent_of_conductor_rank2"; v = "REJECTED"
        rows.append(_make_row("g23_asymptotic_limit", kp, v,
                              f"bsd_scale:rank2_seed{seed}", "BSD",
                              {"seed": seed, "rank": 2}))
    return rows


def _mahler_enrichment(rng: random.Random) -> list[dict]:
    import math
    rows = []
    entries = load_non_cyclotomic_mahler_entries()
    values = [float(e["mahler_measure"]) for e in entries]
    # G23 bootstrap (more seeds)
    by_deg = {}
    for e in entries:
        d = e.get("degree"); m = float(e.get("mahler_measure", 0))
        if d is None or m <= 1.0 + 1e-9: continue
        if d not in by_deg or m < by_deg[d]: by_deg[d] = m
    deg_errs = sorted([(d, m - M_LEHMER) for d, m in by_deg.items()
                       if m - M_LEHMER > 1e-9])
    for seed in range(60):
        ci = bootstrap_ci(deg_errs, _log_log_slope, n_resamples=300,
                          confidence_level=0.95, seed=seed + 5000)
        if ci.statistic_observed is None or ci.ci_lower is None:
            continue
        lo, hi = ci.ci_lower, ci.ci_upper
        if lo >= -1.5 and hi <= -0.5:
            kp = "decay_consistent_with_1_over_N"; v = "PROMOTED"
        elif lo > -0.5:
            kp = "error_term_does_not_decay_bootstrap"; v = "REJECTED"
        elif hi < -1.5:
            kp = "decay_faster_than_1_over_N_bootstrap"; v = "REJECTED"
        else:
            kp = "decay_slope_ci_straddles_boundary"; v = "UNCERTAIN"
        rows.append(_make_row("g23_asymptotic_limit", kp, v,
                              f"mahler_scale:g23_seed{seed}", "mahler",
                              {"seed": seed, "slope": ci.statistic_observed}))
    # G02 WY variations (more seeds + more thresholds)
    for seed in range(60):
        rng_local = random.Random(seed + 7000)
        thresh = rng_local.choice([1.20, 1.25, 1.30, 1.35, 1.40])
        binary = rng_local.choice(["salem", "smyth", "degree_parity"])
        def label(e, w):
            if w == "salem": return bool(e.get("salem_class"))
            if w == "smyth": return bool(e.get("is_smyth_extremal"))
            return int(e.get("degree", 0)) % 2 == 0
        below = [e for e in entries if float(e.get("mahler_measure", 0)) < thresh]
        above = [e for e in entries if float(e.get("mahler_measure", 0)) >= thresh]
        if not below or not above: continue
        obs_div = abs(sum(label(e, binary) for e in below) / len(below)
                       - sum(label(e, binary) for e in above) / len(above))
        # quick permutation
        labels = [label(e, binary) for e in below + above]
        n_below = len(below)
        n_extreme = 0
        for _ in range(150):
            rng_local.shuffle(labels)
            d = abs(sum(labels[:n_below]) / n_below
                    - sum(labels[n_below:]) / len(above))
            if d >= obs_div: n_extreme += 1
        p_val = n_extreme / 150
        if p_val < 0.05:
            kp = f"contrast_separation_{binary}_promoted"; v = "PROMOTED"
        else:
            kp = f"contrast_separation_{binary}_rejected"; v = "REJECTED"
        rows.append(_make_row("g02_contrast", kp, v,
                              f"mahler_scale:g02_seed{seed}_t{thresh}", "mahler",
                              {"seed": seed, "threshold": thresh, "binary": binary}))
    return rows


def generate_scale_enrichment():
    rng = random.Random(SEED)
    bsd_rows = _bsd_enrichment(rng)
    mahler_rows = _mahler_enrichment(rng)
    all_rows = bsd_rows + mahler_rows
    SCALE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(SCALE_LEDGER, "w") as f:
        for r in all_rows:
            f.write(json.dumps(r) + "\n")
    return {"n_bsd": len(bsd_rows), "n_mahler": len(mahler_rows), "n_total": len(all_rows)}


def _load_scale_stress_combined() -> list[dict]:
    from charon.agents.erebos.sprint1.phase3.real_residue_smoke import (
        REAL_LEDGER_PATHS, ENRICHED_LEDGER_PATH,
    )
    paths = list(REAL_LEDGER_PATHS) + [ENRICHED_LEDGER_PATH, SCALE_LEDGER]
    rows = []
    for p in paths:
        if not p.exists(): continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError: continue
                norm = _normalize_row(raw)
                if norm and norm["plugin_id"]:
                    rows.append(norm)
    return rows


def _count_actionable_deltas(rows) -> int:
    counter = per_plugin_majority(rows)
    mr = extract_cooccurrence_motifs(rows, min_cooccurrence=MIN_COOCCURRENCE,
                                      min_lift=MIN_LIFT)
    cr = conditional_kp_recommendations(rows, mr.motifs)
    return sum(1 for (p, _), c in cr.items()
                if counter.get(p) and counter[p] != c)


def run_scale_stress() -> dict:
    enrichment = generate_scale_enrichment()
    rows = _load_scale_stress_combined()
    n_total = len(rows)

    observed = _count_actionable_deltas(rows)

    # Permutation null on scale-stress combined ledger
    rng = random.Random(SEED + 1)
    null = []
    for _ in range(N_PERMUTATIONS):
        sigs = [r.get("input_signature") for r in rows]
        rng.shuffle(sigs)
        shuffled = [{**r, "input_signature": s} for r, s in zip(rows, sigs)]
        null.append(_count_actionable_deltas(shuffled))

    null_mean = sum(null) / len(null)
    null_var = sum((n - null_mean) ** 2 for n in null) / len(null)
    null_std = null_var ** 0.5
    null_p95 = sorted(null)[int(0.95 * (len(null) - 1))]
    null_max = max(null)
    n_ge = sum(1 for n in null if n >= observed)
    p_value = n_ge / len(null)
    z = (observed - null_mean) / null_std if null_std > 0 else float("inf")

    return {
        "enrichment_added": enrichment,
        "n_rows_combined": n_total,
        "observed_actionable_deltas": observed,
        "null_mean": round(null_mean, 2),
        "null_std": round(null_std, 2),
        "null_p95": null_p95,
        "null_max": null_max,
        "n_null_ge_observed": n_ge,
        "p_value": round(p_value, 4),
        "z_score": round(z, 2),
        "verdict": (
            "DEFINITIVE_PASS" if p_value < 0.01
            else "PASS" if p_value < 0.05
            else "INCONCLUSIVE" if p_value < 0.10
            else "FAIL"
        ),
    }


if __name__ == "__main__":
    r = run_scale_stress()
    print("=" * 72)
    print("Phase 3.K -- Scale stress test (5x enrichment + permutation null)")
    print("=" * 72)
    print()
    print(f"Enrichment added: {r['enrichment_added']}")
    print(f"Total rows (incl. scale enrichment): {r['n_rows_combined']}")
    print()
    print(f"  observed_actionable_deltas       : {r['observed_actionable_deltas']}")
    print(f"  null mean (+/- std)              : {r['null_mean']} (+/- {r['null_std']})")
    print(f"  null max / p95                   : {r['null_max']} / {r['null_p95']}")
    print(f"  n_null >= observed               : {r['n_null_ge_observed']} / 200")
    print(f"  empirical p-value                : {r['p_value']}")
    print(f"  z-score (obs vs null)            : {r['z_score']}")
    print()
    print(f"VERDICT: {r['verdict']}")
