"""Shared helpers for Mahler-catalog composition loaders.

Per ITER-5 roadmap (pivot/erebos_iteration_roadmap_iter4_loop_2026-
05-26.md). Extracted from composition_g02_lehmer_salem +
composition_g02_g04_lehmer_tightened to avoid duplicating
partition / survival / permutation-null logic across the growing
set of (Mahler categorical x band) loaders.

Per DNA P1 (living code): this is shared infrastructure for the
composition-loader family; not user-facing.
"""
from __future__ import annotations

import random
from typing import Callable, Optional

# Lehmer's polynomial Mahler measure (canonical constant across
# Mahler-spectrum work).
M_LEHMER = 1.1762808182599176


def load_non_cyclotomic_mahler_entries(upper_M: float = 2.0) -> list[dict]:
    """Return all Mossinghoff catalog entries with M strictly above
    cyclotomic floor (1.0) and below `upper_M`."""
    try:
        from prometheus_math.databases.mahler import all_below
    except Exception:
        return []
    entries = all_below(upper_M)
    return [
        e for e in entries
        if e.get("mahler_measure") is not None
        and e["mahler_measure"] > 1.0 + 1e-9
    ]


def partition_by_predicate(
    entries: list[dict],
    predicate: Callable[[dict], bool],
    *,
    in_band: Optional[tuple[float, float]] = None,
) -> dict:
    """Partition entries into group_a (predicate True) and group_b
    (predicate False), optionally restricted to a Mahler-measure
    band [m_lo, m_hi].

    Returns {"group_a": [M values...], "group_b": [...]}.
    Empty lists if no entries match.
    """
    if in_band is not None:
        m_lo, m_hi = in_band
        entries = [
            e for e in entries
            if m_lo <= float(e["mahler_measure"]) <= m_hi
        ]
    group_a: list[float] = []
    group_b: list[float] = []
    for e in entries:
        m = float(e["mahler_measure"])
        if predicate(e):
            group_a.append(m)
        else:
            group_b.append(m)
    return {"group_a": group_a, "group_b": group_b}


def survival_fraction(values: list[float], threshold: float) -> float:
    if not values:
        return 0.0
    return sum(1 for v in values if v >= threshold) / len(values)


def permutation_null_divergence(
    pooled: list[float],
    n_a: int,
    threshold: float,
    n_perm: int = 1000,
    seed: int = 42,
) -> list[float]:
    """Shuffle group labels N times; return list of |surv_a - surv_b|
    divergences under the null."""
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(n_perm):
        shuffled = list(pooled)
        rng.shuffle(shuffled)
        d = abs(
            survival_fraction(shuffled[:n_a], threshold)
            - survival_fraction(shuffled[n_a:], threshold)
        )
        out.append(d)
    return out


def run_binary_split_permutation_null(
    *,
    predicate: Callable[[dict], bool],
    group_a_label: str,
    group_b_label: str,
    threshold: float,
    in_band: Optional[tuple[float, float]] = None,
    n_perm: int = 1000,
    seed: int = 42,
    promoted_percentile: float = 0.95,
    min_group_size: int = 10,
) -> dict:
    """End-to-end binary-split permutation null test. Used by every
    g02_* (Contrast) composition loader.

    Returns a result dict with verdict / kill_pattern / divergence /
    null p95 / per-group survival fractions / sample sizes. The
    Stygian executor consumes this directly.
    """
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }
    parts = partition_by_predicate(entries, predicate, in_band=in_band)
    group_a, group_b = parts["group_a"], parts["group_b"]

    if len(group_a) < min_group_size or len(group_b) < min_group_size:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_group_a": len(group_a),
            "n_group_b": len(group_b),
            "group_a_label": group_a_label,
            "group_b_label": group_b_label,
            "band": in_band,
            "threshold": threshold,
            "notes": (
                f"group(s) below min={min_group_size}; in_band="
                f"{in_band}, threshold={threshold}"
            ),
        }

    surv_a = survival_fraction(group_a, threshold)
    surv_b = survival_fraction(group_b, threshold)
    observed = abs(surv_a - surv_b)

    pooled = group_a + group_b
    nulls = permutation_null_divergence(
        pooled, n_a=len(group_a), threshold=threshold,
        n_perm=n_perm, seed=seed,
    )
    nulls_sorted = sorted(nulls)
    p95 = nulls_sorted[int(promoted_percentile * (len(nulls_sorted) - 1))]

    if observed > p95:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"At threshold M >= {threshold:.4f} "
            f"(band={in_band}), observed divergence "
            f"|surv({group_a_label})={surv_a:.4f} - "
            f"surv({group_b_label})={surv_b:.4f}| = {observed:.4f} > "
            f"null p95 {p95:.4f}. {group_a_label} moderates the "
            f"M-distribution at this threshold."
        )
    else:
        verdict = "REJECTED"
        kp = "permutation_null"
        notes = (
            f"At threshold M >= {threshold:.4f} "
            f"(band={in_band}), observed divergence "
            f"{observed:.4f} within null p95 {p95:.4f}. "
            f"{group_a_label} moderation cannot be distinguished "
            f"from shuffled labels."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "threshold": threshold,
        "band": in_band,
        "group_a_label": group_a_label,
        "group_b_label": group_b_label,
        "n_group_a": len(group_a),
        "n_group_b": len(group_b),
        "survival_fraction_a": round(surv_a, 4),
        "survival_fraction_b": round(surv_b, 4),
        "observed_divergence": round(observed, 4),
        "null_p95": round(p95, 4),
        "permutation_n": n_perm,
        "notes": notes,
    }
