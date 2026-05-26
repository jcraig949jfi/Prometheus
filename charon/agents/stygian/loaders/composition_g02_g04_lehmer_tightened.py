"""Composition loader: combined G02+G04 (Contrast + Tightening) on
Lehmer.

Per ITER-4 priority #2 (entry-point doc): the v0.10 G02+Lehmer+Salem
composition was REJECTED with permutation_null because the M_Lehmer
threshold (1.176) is too loose -- ~100% of entries exceed it
regardless of Salem class. The G04 tightening hypothesis says
divergence MIGHT appear at a stricter threshold.

This loader chains two compositions:
- G02 binary-split (Salem vs non-Salem from Mossinghoff)
- G04 threshold-tighten (M >= 1.30 instead of M >= 1.176)

Test: run the G02 permutation null at the tightened threshold.
- If observed divergence > null p95 -> PROMOTED. The Salem class
  moderates Lehmer survival at the tighter threshold; the v0.10
  REJECTED was a too-loose-threshold artifact.
- Else -> REJECTED permutation_null at tighter threshold; the
  hypothesis "tighter threshold reveals signal" is itself wrong.

This is the FIRST chained composition in the swarm. Per DNA P9
(rolling cadence) + composition-aware loader philosophy: each
generator's outputs become inputs for the next.
"""
from __future__ import annotations

import random
from typing import Any, Optional

from charon.agents.stygian.loaders._composition import register


M_LEHMER = 1.1762808182599176
TIGHTENED_THRESHOLD = 1.30  # G04 tightening per ladder
PERMUTATION_N = 1000
PERMUTATION_SEED = 42
PROMOTED_PERCENTILE = 0.95


def _load_mossinghoff_partition() -> Optional[dict]:
    try:
        from prometheus_math.databases.mahler import all_below
    except Exception:
        return None
    entries = all_below(2.0)
    salem: list[float] = []
    non_salem: list[float] = []
    for e in entries:
        m = e.get("mahler_measure")
        if m is None or m <= 1.0 + 1e-9:
            continue
        if bool(e.get("salem_class")):
            salem.append(float(m))
        else:
            non_salem.append(float(m))
    if not salem or not non_salem:
        return None
    return {"salem": salem, "non_salem": non_salem}


def _survival_fraction(values: list[float], threshold: float) -> float:
    if not values:
        return 0.0
    return sum(1 for v in values if v >= threshold) / len(values)


def _permutation_null(
    pooled_values: list[float], n_a: int, threshold: float,
    n_perm: int, seed: int,
) -> list[float]:
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(n_perm):
        shuffled = list(pooled_values)
        rng.shuffle(shuffled)
        d = abs(
            _survival_fraction(shuffled[:n_a], threshold)
            - _survival_fraction(shuffled[n_a:], threshold)
        )
        out.append(d)
    return out


def run_g02_g04_lehmer_tightened() -> dict:
    """G02+G04 chain: Salem vs non-Salem permutation null at the
    tightened threshold M >= 1.30."""
    data = _load_mossinghoff_partition()
    if data is None:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff partition empty",
        }
    salem = data["salem"]
    non_salem = data["non_salem"]
    if len(salem) < 10 or len(non_salem) < 10:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_salem": len(salem),
            "n_non_salem": len(non_salem),
            "notes": "either group < 10 entries at the tightened scope",
        }

    # Survival at TIGHTENED threshold (G04 contribution)
    surv_s = _survival_fraction(salem, TIGHTENED_THRESHOLD)
    surv_ns = _survival_fraction(non_salem, TIGHTENED_THRESHOLD)
    observed = abs(surv_s - surv_ns)

    pooled = salem + non_salem
    null_divs = _permutation_null(
        pooled, n_a=len(salem),
        threshold=TIGHTENED_THRESHOLD,
        n_perm=PERMUTATION_N, seed=PERMUTATION_SEED,
    )
    null_sorted = sorted(null_divs)
    null_p95 = null_sorted[int(PROMOTED_PERCENTILE * (len(null_sorted) - 1))]

    # Comparison to baseline (G02-only at M_Lehmer): the V0.10 spike
    # showed divergence ~0.0001, way under noise. We expect tightening
    # to make divergence detectable IF Salem class genuinely moderates
    # mid-range Mahler-measure distribution.
    baseline_s = _survival_fraction(salem, M_LEHMER)
    baseline_ns = _survival_fraction(non_salem, M_LEHMER)
    baseline_divergence = abs(baseline_s - baseline_ns)

    if observed > null_p95:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"At tightened threshold M>={TIGHTENED_THRESHOLD}, "
            f"observed Salem-vs-non-Salem survival divergence "
            f"{observed:.4f} > null p95 {null_p95:.4f}. The Salem "
            f"class DOES moderate Lehmer survival at the stricter "
            f"threshold. The v0.10 REJECTED at M={M_LEHMER:.4f} was "
            f"a too-loose-threshold artifact; G04's tightening "
            f"hypothesis is CONFIRMED for this composition."
        )
    else:
        verdict = "REJECTED"
        kp = "permutation_null"
        notes = (
            f"At tightened threshold M>={TIGHTENED_THRESHOLD}, "
            f"observed divergence {observed:.4f} still within null "
            f"p95 {null_p95:.4f}. Tightening did NOT reveal hidden "
            f"signal -- Salem-class moderation is genuinely absent "
            f"(or beyond what this catalog can resolve)."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "tightened_threshold": TIGHTENED_THRESHOLD,
        "baseline_threshold": M_LEHMER,
        "observed_divergence_at_tightened": round(observed, 4),
        "null_p95_at_tightened": round(null_p95, 4),
        "survival_fraction_salem_at_tightened": round(surv_s, 4),
        "survival_fraction_non_salem_at_tightened": round(surv_ns, 4),
        "baseline_divergence_at_M_lehmer": round(baseline_divergence, 4),
        "baseline_survival_salem": round(baseline_s, 4),
        "baseline_survival_non_salem": round(baseline_ns, 4),
        "permutation_n": PERMUTATION_N,
        "n_salem": len(salem),
        "n_non_salem": len(non_salem),
        "notes": notes,
    }


class G02G04LehmerTightenedLoader:
    plugin_id = "g04_survivor_tightening"  # G04 is the outer wrapper
    composition_id = "g02_g04_lehmer_tightened"
    description = (
        "Combined G02+G04 composition loader: Salem-vs-non-Salem "
        "permutation null at M_tightened=1.30 instead of M_Lehmer. "
        "Tests whether the v0.10 G02-Salem REJECTED was a too-loose-"
        "threshold artifact."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        plugin_id = queue_payload.get("erebos_plugin_id")
        if plugin_id != "g04_survivor_tightening":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        # G04 emission whose parent is a G02 Salem-Lehmer composition,
        # OR a direct Lehmer-context G04 tightening
        return "BL-C-001" in composed_id or "salem" in composed_id.lower()

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g02_g04_lehmer_tightened()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G02+G04 chained composition: at the "
                f"G04-tightened threshold M>={TIGHTENED_THRESHOLD} "
                f"(instead of the loose M_Lehmer={M_LEHMER:.4f}), "
                f"Salem-vs-non-Salem permutation-null survival "
                f"divergence is/isn't statistically significant. "
                f"Direct test of the ITER-3 follow-on hypothesis that "
                f"the v0.10 REJECTED was a too-loose-threshold "
                f"artifact."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff catalog "
                "with Salem class filter; permutation null N=1000"
            ),
            "result": result,
            "notes": (
                "FIRST chained-composition loader in the swarm. "
                "Demonstrates the per-DNA-P9 rolling-cadence pattern: "
                "each iteration's output becomes the next iteration's "
                "input."
            ),
        }


register(G02G04LehmerTightenedLoader())
