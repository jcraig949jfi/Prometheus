"""Phase 3.G — BSD-domain ledger enrichment via ITER-61 detectors.

Calls the two BSD detectors against the real 1000-entry catalog at
varying parameter splits to produce ~30 BSD-domain rows. Appends
to kill_ledger_enriched.jsonl so cross-cell smoke can detect
cross-domain motifs.

Variations:
  - rank stratum: 0, 1, 2 (3 rows)
  - bootstrap subsample seeds for rank-1 stratum (10 rows)
  - bootstrap subsample seeds for rank-2 stratum (10 rows)
  - consistency loader on random catalog subsets of N=200 (10 rows)
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path

from charon.agents.stygian.loaders._bootstrap_ci import bootstrap_ci
from charon.agents.stygian.loaders._bsd_helpers import (
    get_conductor,
    get_label,
    get_rank,
    get_regulator,
    load_bsd_entries,
)
from charon.agents.stygian.loaders.composition_bsd_rank_strata import (
    _log_log_slope,
)


ENRICHMENT_PATH = Path(
    "charon/agents/erebos/state/kill_ledger_enriched.jsonl"
)


def _make_bsd_row(
    plugin_id: str,
    kill_pattern: str,
    verdict: str,
    input_signature: str,
    extra: dict,
) -> dict:
    return {
        "record_id": uuid.uuid4().hex,
        "batch_id": f"phase3_g_bsd_enrichment_{plugin_id}",
        "emitted_at": datetime.now(timezone.utc).isoformat(),
        "generator_id": "erebos",
        "claim_kind": f"erebos_{plugin_id}_claim",
        "kill_pattern": kill_pattern,
        "verdict": verdict,
        "claim_payload": {
            "problem_id": "BL-B-001",  # BSD context (B-tier)
            "domain": "BSD",
            "enrichment_extra": extra,
        },
        "kill_vector": extra,
        "method": "phase3_g_bsd_enrichment",
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
        "input_signature": input_signature,
        "canonical_claim_text": (
            f"BSD enrichment[{plugin_id}]: {kill_pattern}"
        ),
    }


def _classify_slope_ci(rank: int, slope: float, lo: float, hi: float) -> tuple[str, str]:
    if lo > 0:
        return "PROMOTED", f"bsd_regulator_grows_with_conductor_rank{rank}"
    if hi < 0:
        return "REJECTED", f"bsd_regulator_shrinks_with_conductor_rank{rank}"
    return "REJECTED", f"bsd_regulator_independent_of_conductor_rank{rank}"


def run_bsd_enrichment() -> dict:
    entries = load_bsd_entries()
    rows: list[dict] = []

    # ----- 1. Per-rank stratum scaling tests (one per stratum) -----
    for rank in [0, 1, 2]:
        stratum = [e for e in entries if get_rank(e) == rank]
        points = [
            (get_conductor(e), get_regulator(e)) for e in stratum
            if get_conductor(e) is not None
            and get_regulator(e) is not None
            and get_regulator(e) > 0
        ]
        if len(points) < 10:
            continue
        ci = bootstrap_ci(
            data=points,
            statistic_fn=_log_log_slope,
            n_resamples=500,
            confidence_level=0.95,
            seed=900 + rank,
        )
        if ci.statistic_observed is None or ci.ci_lower is None:
            continue
        verdict, kp = _classify_slope_ci(
            rank, ci.statistic_observed, ci.ci_lower, ci.ci_upper,
        )
        rows.append(_make_bsd_row(
            plugin_id="g23_asymptotic_limit",
            kill_pattern=kp,
            verdict=verdict,
            input_signature=f"bsd:rank_stratum_{rank}",
            extra={
                "rank": rank,
                "slope": ci.statistic_observed,
                "ci_lower": ci.ci_lower,
                "ci_upper": ci.ci_upper,
                "n_points": len(points),
            },
        ))

    # ----- 2. Bootstrap subsample replication for rank-1 stratum -----
    rank1 = [e for e in entries if get_rank(e) == 1]
    rank1_points = [
        (get_conductor(e), get_regulator(e)) for e in rank1
        if get_conductor(e) and get_regulator(e) and get_regulator(e) > 0
    ]
    for seed in range(10):
        rng = random.Random(seed + 700)
        subsample = rng.sample(rank1_points, min(100, len(rank1_points)))
        ci = bootstrap_ci(
            data=subsample,
            statistic_fn=_log_log_slope,
            n_resamples=200,
            confidence_level=0.95,
            seed=seed,
        )
        if ci.statistic_observed is None or ci.ci_lower is None:
            continue
        verdict, kp = _classify_slope_ci(
            1, ci.statistic_observed, ci.ci_lower, ci.ci_upper,
        )
        rows.append(_make_bsd_row(
            plugin_id="g23_asymptotic_limit",
            kill_pattern=kp,
            verdict=verdict,
            input_signature=f"bsd:rank1_subsample_seed{seed}",
            extra={"seed": seed, "rank": 1, "subsample_n": len(subsample),
                   "slope": ci.statistic_observed},
        ))

    # ----- 3. Bootstrap subsample for rank-2 stratum -----
    rank2 = [e for e in entries if get_rank(e) == 2]
    rank2_points = [
        (get_conductor(e), get_regulator(e)) for e in rank2
        if get_conductor(e) and get_regulator(e) and get_regulator(e) > 0
    ]
    for seed in range(10):
        rng = random.Random(seed + 800)
        subsample = rng.sample(rank2_points, min(60, len(rank2_points)))
        ci = bootstrap_ci(
            data=subsample,
            statistic_fn=_log_log_slope,
            n_resamples=200,
            confidence_level=0.95,
            seed=seed,
        )
        if ci.statistic_observed is None or ci.ci_lower is None:
            continue
        verdict, kp = _classify_slope_ci(
            2, ci.statistic_observed, ci.ci_lower, ci.ci_upper,
        )
        rows.append(_make_bsd_row(
            plugin_id="g23_asymptotic_limit",
            kill_pattern=kp,
            verdict=verdict,
            input_signature=f"bsd:rank2_subsample_seed{seed}",
            extra={"seed": seed, "rank": 2, "subsample_n": len(subsample),
                   "slope": ci.statistic_observed},
        ))

    # ----- 4. Consistency-loader random subsets -----
    valid_for_consistency = [
        e for e in entries
        if get_rank(e) is not None and get_regulator(e) is not None
    ]
    for seed in range(10):
        rng = random.Random(seed + 600)
        subset = rng.sample(valid_for_consistency, min(200, len(valid_for_consistency)))
        n_consistent = 0
        for e in subset:
            rank = get_rank(e); reg = get_regulator(e)
            if rank == 0 and abs(reg - 1.0) < 1e-9:
                n_consistent += 1
            elif rank >= 1 and reg > 0:
                n_consistent += 1
        rate = n_consistent / len(subset)
        if rate >= 0.95:
            verdict = "PROMOTED"
            kp = "bsd_subset_consistency_promoted"
        else:
            verdict = "REJECTED"
            kp = "bsd_regulator_rank_inconsistent"
        rows.append(_make_bsd_row(
            plugin_id="g25_degeneracy",
            kill_pattern=kp,
            verdict=verdict,
            input_signature=f"bsd:consistency_subset_seed{seed}",
            extra={"seed": seed, "n_subset": len(subset),
                   "consistency_rate": rate},
        ))

    # ----- Append to enriched ledger (already has Mahler enrichment) -----
    ENRICHMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ENRICHMENT_PATH, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    return {
        "n_bsd_rows_added": len(rows),
        "output_path": str(ENRICHMENT_PATH),
    }


if __name__ == "__main__":
    summary = run_bsd_enrichment()
    print("=" * 72)
    print("Phase 3.G -- BSD enrichment summary")
    print("=" * 72)
    for k, v in summary.items():
        print(f"  {k:30s} = {v}")
