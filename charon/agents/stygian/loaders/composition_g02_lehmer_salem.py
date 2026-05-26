"""Concrete composition loader: EREBOS-G02-* x BL-C-001 (Lehmer) x
Salem/non-Salem split.

The SPIKE that validates the composition-aware Stygian loader
contract end-to-end. Handles the simplest case: G02 Contrast claims
on BL-C-001 where the binary split is `salem_class` (a categorical
flag native to the Mossinghoff catalog).

Per pivot/erebos_g04..g25 research notes' "composition-aware loader
needed" sections: once this spike lights up, future loaders follow
the same shape with different transformation logic.

Falsification flow:
1. Load Mossinghoff catalog via the existing BL-C-001 loader path.
2. Partition entries by salem_class True / False.
3. For each group: compute the parent-claim survival fraction
   (here: fraction of entries with M >= M_Lehmer, since BL-C-001
   asserts Lehmer's bound holds).
4. Observed divergence = |survival_A - survival_B|.
5. Permutation null: shuffle group labels N=1000 times; recompute
   divergence; compare observed to shuffled distribution.
6. Verdict:
   - PROMOTED if observed > 95th-percentile of shuffled (real
     divergence beyond permutation noise).
   - REJECTED with kill_pattern=permutation_null if observed within
     the 95% central mass.
   - UNVERIFIED on data-loader failure or insufficient sample.

This is the FIRST Erebos generator emission to ever get a real
battery verdict instead of a short-circuit. Substrate-grade.
"""
from __future__ import annotations

import random
from typing import Any, Optional

from charon.agents.stygian.loaders._composition import (
    CompositionLoader,
    register,
)


# Lehmer's polynomial Mahler measure
M_LEHMER = 1.1762808182599176

# Permutation null params
PERMUTATION_N = 1000
PERMUTATION_SEED = 42

# Significance threshold for PROMOTED
PROMOTED_PERCENTILE = 0.95


def _load_mossinghoff_partition() -> Optional[dict]:
    """Load Mossinghoff catalog; partition entries by salem_class.
    Returns dict with keys 'salem' (M values list) and 'non_salem'
    (M values list), or None on failure."""
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
            continue  # exclude cyclotomic floor
        if bool(e.get("salem_class")):
            salem.append(float(m))
        else:
            non_salem.append(float(m))
    if not salem or not non_salem:
        return None
    return {"salem": salem, "non_salem": non_salem}


def _survival_fraction(values: list[float], threshold: float) -> float:
    """Fraction of values >= threshold. The "parent claim survives"
    for an entry if M(P) >= M_Lehmer."""
    if not values:
        return 0.0
    return sum(1 for v in values if v >= threshold) / len(values)


def _permutation_null(
    pooled_values: list[float],
    n_a: int,
    threshold: float,
    n_perm: int,
    seed: int,
) -> list[float]:
    """Shuffle group labels N times; recompute |survival_A -
    survival_B| each shuffle; return list of observed divergences."""
    rng = random.Random(seed)
    null_divergences: list[float] = []
    for _ in range(n_perm):
        shuffled = list(pooled_values)
        rng.shuffle(shuffled)
        group_a = shuffled[:n_a]
        group_b = shuffled[n_a:]
        d = abs(
            _survival_fraction(group_a, threshold)
            - _survival_fraction(group_b, threshold)
        )
        null_divergences.append(d)
    return null_divergences


def run_composition_battery(queue_payload: dict) -> dict:
    """End-to-end execution. Returns a result dict the Stygian
    executor can convert to a kill_ledger row.

    Result schema:
    {
      "verdict": "PROMOTED" | "REJECTED" | "UNVERIFIED",
      "kill_pattern": str | None,
      "observed_divergence": float,
      "null_p95": float,
      "permutation_n": int,
      "n_salem": int,
      "n_non_salem": int,
      "survival_fraction_salem": float,
      "survival_fraction_non_salem": float,
      "notes": str,
    }
    """
    data = _load_mossinghoff_partition()
    if data is None:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no partition",
        }
    salem = data["salem"]
    non_salem = data["non_salem"]
    if len(salem) < 10 or len(non_salem) < 10:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_salem": len(salem),
            "n_non_salem": len(non_salem),
            "notes": "either group has < 10 entries",
        }

    surv_s = _survival_fraction(salem, M_LEHMER)
    surv_ns = _survival_fraction(non_salem, M_LEHMER)
    observed = abs(surv_s - surv_ns)

    pooled = salem + non_salem
    null_divs = _permutation_null(
        pooled, n_a=len(salem),
        threshold=M_LEHMER,
        n_perm=PERMUTATION_N,
        seed=PERMUTATION_SEED,
    )
    null_sorted = sorted(null_divs)
    p95_idx = int(PROMOTED_PERCENTILE * (len(null_sorted) - 1))
    null_p95 = null_sorted[p95_idx]

    if observed > null_p95:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"observed divergence {observed:.4f} > null 95th percentile "
            f"{null_p95:.4f}; survival diverges between Salem ({surv_s:.4f}) "
            f"and non-Salem ({surv_ns:.4f}) by more than permutation chance"
        )
    else:
        verdict = "REJECTED"
        kp = "permutation_null"
        notes = (
            f"observed divergence {observed:.4f} within null 95% mass "
            f"(p95 = {null_p95:.4f}); claim cannot be distinguished from "
            f"shuffled labels"
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "observed_divergence": round(observed, 4),
        "null_p95": round(null_p95, 4),
        "permutation_n": PERMUTATION_N,
        "n_salem": len(salem),
        "n_non_salem": len(non_salem),
        "survival_fraction_salem": round(surv_s, 4),
        "survival_fraction_non_salem": round(surv_ns, 4),
        "notes": notes,
    }


class G02LehmerSalemLoader:
    plugin_id = "g02_contrast"
    composition_id = "g02_lehmer_salem"
    description = (
        "Composition loader for EREBOS-G02-* claims where the parent "
        "is BL-C-001 Lehmer and the binary split is Salem vs "
        "non-Salem (Mossinghoff salem_class flag)."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g02_contrast":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "")
        # Must match EREBOS-G02-BL-C-001-x-salem_vs_non_salem (or
        # the BL-C-003/004 Mahler-family variants that also use the
        # Salem split per PROBLEM_BINARY_SPLITS in g02_contrast.py)
        return (
            "BL-C-001-x-salem_vs_non_salem" in composed_id
            or "BL-C-003-x-salem_vs_non_salem" in composed_id
            or "BL-C-004-x-salem_vs_non_salem" in composed_id
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        """For this composition, we don't use UnifiedBattery directly --
        we have our own permutation-null implementation. Returns a
        dict the executor uses to construct the kill_ledger row.

        Conventionally returns the same shape as the regular
        BatteryLoaderResult but with mode='custom_composition' and
        a pre-computed result block.
        """
        result = run_composition_battery(queue_payload)  # type: ignore[unreachable]
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G02 composition: Lehmer survival rate "
                f"diverges between Salem-class and non-Salem polynomials "
                f"in the Mossinghoff catalog. Permutation null with "
                f"N={PERMUTATION_N} shuffles, 95th-percentile threshold."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "catalog, salem_class flag"
            ),
            "result": result,
            "notes": (
                f"First Erebos generator emission to receive a real "
                f"battery verdict instead of a short-circuit. Per "
                f"pivot/erebos_design_philosophy_dna_2026-05-26.md "
                f"P12 (falsification asymmetry), this lifts G02 "
                f"Contrast from 'unfalsifiable MVP' to 'empirical "
                f"instrument' for the specific (Lehmer, Salem) "
                f"composition."
            ),
        }


# Register an INSTANCE (not the class) so loader.applicable(queue_payload)
# binds queue_payload correctly. Module-import-time side-effect.
register(G02LehmerSalemLoader())
