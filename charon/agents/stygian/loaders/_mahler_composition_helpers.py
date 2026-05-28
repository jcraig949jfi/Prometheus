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


# ---------------------------------------------------------------------
# v3 Phase 1A ITER-31: Westfall-Young max-T family-wise correction
# ---------------------------------------------------------------------

def run_multi_binary_westfall_young_null(
    *,
    predicates: list[tuple[str, Callable[[dict], bool]]],
    threshold: float,
    in_band: Optional[tuple[float, float]] = None,
    n_perm: int = 1000,
    seed: int = 42,
    promoted_percentile: float = 0.95,
    min_group_size: int = 10,
) -> dict:
    """Multi-binary Westfall-Young max-T family-wise-error-corrected null.

    Per Erebos v3 doctrine Phase 1A ITER-31 + DR batch 1 convergence.
    Replaces independent single-shuffle nulls (one per binary) — which
    inflate family-wise false-positive rates when N binaries fire —
    with a single permutation procedure that tracks the MAXIMUM
    observed-statistic across binaries per permutation.

    The max-T null is the distribution of max(|surv_a - surv_b|) over
    binaries per shuffle. Each binary's observed divergence is then
    compared to this MAX-distribution. p_fwer = fraction of shuffles
    whose max-divergence >= observed.

    This is strictly more conservative than independent nulls (one
    binary's observed must beat the SHUFFLE-MAX of all binaries) but
    has the right family-wise error rate without independence
    assumptions — appropriate for correlated catalog binaries
    like (salem_class, is_smyth_extremal, degree_parity).

    Parameters
    ----------
    predicates : list of (label, predicate_callable) tuples
        Each predicate splits entries into group_a (True) and group_b
        (False). Labels appear in the per-binary result rows.
    threshold : float
        Survival threshold for surv_a / surv_b computation.
    in_band : optional (lo, hi)
        Restrict catalog to entries with M in [lo, hi].
    n_perm : int
        Number of permutations.
    seed : int
        RNG seed.
    promoted_percentile : float
        Percentile of the max-T null above which observed promotes.
    min_group_size : int
        Per-binary minimum; binaries below get UNVERIFIED per-row but
        still contribute to the shuffle procedure (their per-shuffle
        divergence is computed and counted into the max).

    Returns
    -------
    dict with:
        verdict: "MIXED" | "ALL_PROMOTED" | "ALL_REJECTED" | "UNVERIFIED"
        per_binary: list of dicts (one per predicate) with:
            label, observed_divergence, fwer_p_value,
            null_max_p95, individual_p95,
            verdict ("PROMOTED" | "REJECTED" | "UNVERIFIED"),
            kill_pattern ("permutation_null_fwer" or None),
            n_group_a, n_group_b
        max_t_null_distribution: list of per-shuffle max divergences
            (for downstream consumers and visualization)
        notes: human-readable summary
    """
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }
    if in_band is not None:
        m_lo, m_hi = in_band
        entries = [
            e for e in entries
            if m_lo <= float(e["mahler_measure"]) <= m_hi
        ]
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "notes": f"in_band={in_band} produced empty restriction",
        }

    # Per-predicate partitions
    per_binary: list[dict] = []
    pooled_values = [float(e["mahler_measure"]) for e in entries]
    n_pool = len(pooled_values)
    observed_divs: list[float] = []
    group_a_sizes: list[int] = []
    for label, pred in predicates:
        parts = partition_by_predicate(entries, pred)
        ga = parts["group_a"]
        gb = parts["group_b"]
        surv_a = survival_fraction(ga, threshold)
        surv_b = survival_fraction(gb, threshold)
        obs = abs(surv_a - surv_b)
        observed_divs.append(obs)
        group_a_sizes.append(len(ga))
        per_binary.append({
            "label": label,
            "n_group_a": len(ga),
            "n_group_b": len(gb),
            "surv_a": round(surv_a, 4),
            "surv_b": round(surv_b, 4),
            "observed_divergence": round(obs, 4),
        })

    # Westfall-Young max-T permutation: per shuffle, compute divergence
    # for EVERY binary AT ITS OWN GROUP SIZE, track the MAX.
    import random
    rng = random.Random(seed)
    max_t_nulls: list[float] = []
    individual_nulls: list[list[float]] = [[] for _ in predicates]
    for _ in range(n_perm):
        shuffled = list(pooled_values)
        rng.shuffle(shuffled)
        shuffle_divs: list[float] = []
        for n_a in group_a_sizes:
            ga = shuffled[:n_a]
            gb = shuffled[n_a:]
            d = abs(
                survival_fraction(ga, threshold)
                - survival_fraction(gb, threshold)
            )
            shuffle_divs.append(d)
        for i, d in enumerate(shuffle_divs):
            individual_nulls[i].append(d)
        max_t_nulls.append(max(shuffle_divs))
    max_t_sorted = sorted(max_t_nulls)
    max_t_p95 = max_t_sorted[
        int(promoted_percentile * (len(max_t_sorted) - 1))
    ]

    # Compute per-binary FWER p-values vs the max-T distribution
    n_promoted = 0
    n_rejected = 0
    n_unverified = 0
    for i, (binary_row, obs) in enumerate(zip(per_binary, observed_divs)):
        # FWER p-value = fraction of shuffles where max-divergence >= observed
        fwer_p = sum(1 for v in max_t_nulls if v >= obs) / n_perm
        ind_sorted = sorted(individual_nulls[i])
        ind_p95 = ind_sorted[
            int(promoted_percentile * (len(ind_sorted) - 1))
        ]
        binary_row["fwer_p_value"] = round(fwer_p, 6)
        binary_row["null_max_p95"] = round(max_t_p95, 4)
        binary_row["individual_p95"] = round(ind_p95, 4)

        n_a, n_b = binary_row["n_group_a"], binary_row["n_group_b"]
        if n_a < min_group_size or n_b < min_group_size:
            binary_row["verdict"] = "UNVERIFIED"
            binary_row["kill_pattern"] = "stygian_composition_insufficient_sample"
            n_unverified += 1
        elif obs > max_t_p95:
            binary_row["verdict"] = "PROMOTED"
            binary_row["kill_pattern"] = None
            n_promoted += 1
        else:
            binary_row["verdict"] = "REJECTED"
            binary_row["kill_pattern"] = "permutation_null_fwer"
            n_rejected += 1

    # Aggregate verdict
    if n_promoted == len(per_binary):
        agg = "ALL_PROMOTED"
    elif n_rejected == len(per_binary):
        agg = "ALL_REJECTED"
    elif n_unverified == len(per_binary):
        agg = "UNVERIFIED"
    else:
        agg = "MIXED"

    notes = (
        f"Westfall-Young max-T over {len(predicates)} binaries "
        f"({n_perm} permutations, seed={seed}). "
        f"max-T null p95 = {max_t_p95:.4f}. "
        f"Per-binary verdicts: {n_promoted} PROMOTED, "
        f"{n_rejected} REJECTED, {n_unverified} UNVERIFIED. "
        f"Family-wise correction applied — observed must exceed "
        f"SHUFFLE-MAX of all binaries, strictly more conservative "
        f"than independent per-binary nulls."
    )

    return {
        "verdict": agg,
        "kill_pattern": "permutation_null_fwer" if agg == "ALL_REJECTED" else None,
        "per_binary": per_binary,
        "max_t_null_p95": round(max_t_p95, 4),
        "max_t_null_distribution_head": [round(v, 4) for v in max_t_sorted[:20]],
        "max_t_null_distribution_tail": [round(v, 4) for v in max_t_sorted[-20:]],
        "permutation_n": n_perm,
        "permutation_seed": seed,
        "threshold": threshold,
        "in_band": in_band,
        "n_pool": n_pool,
        "notes": notes,
    }
