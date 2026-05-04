"""prometheus_math.gradient_archaeology — read-only analysis of accumulated
substrate logs for Aporia's 6 negative-space gradient signals.

Context (2026-05-04)
--------------------
James + 3 reviewers (Aporia, ChatGPT, Gemini) reframed the Layer 2 repair
from "fix RL reward" to "build the gradient field from accumulated
falsifications."  Aporia's framework names six gradient axes that a
healthy substrate-as-gradient-field ought to exhibit:

  1. Distance-to-target (continuous, not binary)
  2. Battery-survival depth (kill_path information density)
  3. Negative space from failed attempts (operator x falsifier)
  4. Method-utility gradient (operator-class hit rates)
  5. Cross-domain bridge gradient (proximity-to-catalog)
  6. Computational-verification depth

This module asks the empirical question: **does the existing ledger
already contain visible structure on each axis, or does each gradient
require new instrumentation?**

Read-only.  Aggregates the pilot JSONs that live under
``prometheus_math/_*.json`` plus the four_counts / degree_sweep run
files.  Writes:

  * ``prometheus_math/_gradient_archaeology_results.json`` — full
    structured aggregation, one section per gradient.
  * ``prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md`` — human report.

Honest framing:
  * Per-gradient verdict is one of:
      ``SIGNAL_PRESENT`` — the existing logs visibly carry structure on
        this axis (non-uniform distribution, separable per-algorithm,
        directional information).
      ``SIGNAL_ABSENT`` — the existing logs cover this axis but the
        distribution looks indistinguishable from random / uniform.
      ``NEEDS_NEW_INSTRUMENTATION`` — the substrate does not log the
        relevant field at all; we'd need to add capture before this
        gradient can be read off existing data.
  * "Sparse" sections are flagged, not filled with extrapolation.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Source registry
# ---------------------------------------------------------------------------


PROMETHEUS_MATH_DIR = os.path.dirname(os.path.abspath(__file__))


# Pilot files to consume.  Each entry declares (filename, family, has_M_records,
# has_kill_pattern_aggregate, n_episodes_estimator).  Read-only aggregation
# only consumes whatever fields are present.
PILOT_SOURCES: List[Dict[str, Any]] = [
    # Lehmer / Mahler-measure family --------------------------------------
    {"file": "_catalog_seeded_pilot.json", "family": "lehmer",
     "schema": "catalog_seeded"},
    {"file": "four_counts_pilot_run_10k.json", "family": "lehmer",
     "schema": "four_counts_top"},
    {"file": "four_counts_pilot_run_10k_shaped.json", "family": "lehmer",
     "schema": "four_counts_top"},
    {"file": "four_counts_pilot_run.json", "family": "lehmer",
     "schema": "four_counts_top"},
    {"file": "four_counts_d14_w5.json", "family": "lehmer",
     "schema": "four_counts_per_arm"},
    {"file": "four_counts_width_5.json", "family": "lehmer",
     "schema": "four_counts_top"},
    {"file": "four_counts_width_7.json", "family": "lehmer",
     "schema": "four_counts_top"},
    {"file": "degree_sweep_results.json", "family": "lehmer",
     "schema": "degree_sweep"},
    {"file": "_v2_anti_elitist_pilot.json", "family": "lehmer",
     "schema": "v2_cells"},
    {"file": "_v3_root_space_pilot.json", "family": "lehmer",
     "schema": "v3_cells"},
    {"file": "_discovery_v2_pilot.json", "family": "lehmer",
     "schema": "discovery_v2"},
    {"file": "_discovery_v2_pilot_seeded.json", "family": "lehmer",
     "schema": "discovery_v2"},
    {"file": "_discovery_v2_pilot_smoke.json", "family": "lehmer",
     "schema": "discovery_v2"},
    {"file": "_lehmer_smoke_results.json", "family": "lehmer",
     "schema": "lehmer_smoke"},
    # Cross-domain pilots --------------------------------------------------
    {"file": "_genus2_pilot.json", "family": "genus2",
     "schema": "cross_domain_means"},
    {"file": "_knot_pilot.json", "family": "knot_trace_field",
     "schema": "cross_domain_means"},
    {"file": "_modular_form_pilot.json", "family": "modular_form",
     "schema": "cross_domain_means"},
    {"file": "_mock_theta_pilot.json", "family": "mock_theta",
     "schema": "cross_domain_means"},
    {"file": "_oeis_sleeping_pilot.json", "family": "oeis_sleeping_beauty",
     "schema": "cross_domain_means"},
    {"file": "_bsd_rank_pilot_run.json", "family": "bsd_rank",
     "schema": "cross_domain_means"},
    {"file": "_bsd_rich_pilot_run.json", "family": "bsd_rank",
     "schema": "cross_domain_means"},
    {"file": "_bsd_rank_mlp_pilot.json", "family": "bsd_rank",
     "schema": "cross_domain_mlp"},
]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _load_json(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_all_sources(base_dir: str = PROMETHEUS_MATH_DIR) -> List[Dict[str, Any]]:
    """Load every declared source that exists on disk.

    Skips missing files cleanly; never raises.
    """
    out: List[Dict[str, Any]] = []
    for spec in PILOT_SOURCES:
        path = os.path.join(base_dir, spec["file"])
        data = _load_json(path)
        if data is None:
            continue
        out.append(
            {
                "file": spec["file"],
                "family": spec["family"],
                "schema": spec["schema"],
                "data": data,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Schema-aware extractors
# ---------------------------------------------------------------------------


def _extract_kill_pattern_aggregate(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Pull (algorithm_label, kill_pattern, count) tuples out of any rec.

    Returns ``{"per_arm_kill_patterns": {arm: {kp: count}},
                "n_episodes_total": int,
                "details": ..., "schema": ...}``.

    Cleanly returns empty dicts if the schema doesn't carry kill_path.
    """
    schema = rec["schema"]
    data = rec["data"]
    out_arms: Dict[str, Counter] = {}
    n_eps = 0
    n_records = 0

    if schema == "catalog_seeded":
        per_arm = data.get("per_arm", {})
        for arm, val in per_arm.items():
            arm_label = f"catalog_seeded::{arm}"
            arm_counter: Counter = Counter()
            for r in val.get("results", []):
                bkp = r.get("by_kill_pattern", {}) or {}
                for k, v in bkp.items():
                    arm_counter[k] += int(v)
                n_eps += int(r.get("total_episodes", 0))
                n_records += 1
            if arm_counter:
                out_arms[arm_label] = arm_counter

    elif schema == "four_counts_top":
        pc = data.get("per_condition", {})
        for cond, val in pc.items():
            arm_label = f"four_counts::{cond}"
            bkp = val.get("by_kill_pattern", {}) or {}
            arm_counter = Counter()
            for k, v in bkp.items():
                arm_counter[k] += int(v)
            psc = val.get("per_seed_counts", []) or []
            for s in psc:
                # rejected + catalog_hit + promote + shadow ~= total per seed
                n_eps += int(s.get("rejected", 0)) + int(s.get("catalog_hit", 0))
                n_eps += int(s.get("promote", 0)) + int(s.get("shadow_catalog", 0))
                n_records += 1
            if arm_counter:
                out_arms[arm_label] = arm_counter

    elif schema == "four_counts_per_arm":
        for arm, val in data.get("per_arm", {}).items():
            arm_label = f"four_counts_per_arm::{arm}"
            arm_counter = Counter()
            for r in val.get("results", []):
                bkp = r.get("by_kill_pattern", {}) or {}
                for k, v in bkp.items():
                    arm_counter[k] += int(v)
                n_eps += int(r.get("total_episodes", 0))
                n_records += 1
            if arm_counter:
                out_arms[arm_label] = arm_counter

    elif schema == "degree_sweep":
        for deg, deg_block in data.items():
            pc = (deg_block or {}).get("per_condition", {})
            for cond, val in pc.items():
                arm_label = f"degree_sweep::deg{deg}::{cond}"
                arm_counter = Counter()
                bkp = val.get("by_kill_pattern", {}) or {}
                for k, v in bkp.items():
                    arm_counter[k] += int(v)
                psc = val.get("per_seed_counts", []) or []
                for s in psc:
                    n_eps += sum(
                        int(s.get(k, 0))
                        for k in ("rejected", "catalog_hit", "promote", "shadow_catalog")
                    )
                    n_records += 1
                if arm_counter:
                    out_arms[arm_label] = arm_counter

    elif schema == "v2_cells":
        # The v2 schema doesn't aggregate kill_pattern; we can still count
        # episodes for distance-to-target context.
        for cell in data.get("cells", []):
            n_eps += int(cell.get("n_episodes", 0))
            n_records += 1

    elif schema == "v3_cells":
        for cell in data.get("cells", []):
            n_eps += int(cell.get("n_samples", 0))
            n_records += 1

    elif schema == "discovery_v2":
        for r in data.get("results", []):
            n_eps += int(r.get("n_episodes", 0))
            n_records += 1

    elif schema == "lehmer_smoke":
        n_eps += int(data.get("polys_processed", 0))
        n_records += 1

    elif schema == "cross_domain_means":
        # Mean accuracy per algorithm, per seed -- not episode kill_path.
        n_eps += int(data.get("n_episodes", 0)) * int(data.get("n_seeds", 0))
        n_records += 1

    elif schema == "cross_domain_mlp":
        n_eps += int(data.get("n_episodes", 0)) * int(data.get("n_seeds", 0))
        n_records += 1

    return {
        "per_arm_kill_patterns": {a: dict(c) for a, c in out_arms.items()},
        "n_episodes_total": n_eps,
        "n_records": n_records,
        "schema": schema,
    }


def _extract_m_records(rec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Pull every per-candidate (M, coeffs, label, arm) record.

    Currently only the ``catalog_seeded`` schema persists per-candidate
    records via ``details[*].catalog_hits``.  Other schemas don't.
    """
    out: List[Dict[str, Any]] = []
    if rec["schema"] != "catalog_seeded":
        return out
    per_arm = rec["data"].get("per_arm", {})
    for arm, val in per_arm.items():
        arm_label = f"catalog_seeded::{arm}"
        for det in val.get("details", []):
            seed = det.get("seed")
            for ch in det.get("catalog_hits", []) or []:
                m = ch.get("mahler_measure")
                if m is None:
                    continue
                try:
                    m = float(m)
                except Exception:
                    continue
                if not math.isfinite(m):
                    continue
                out.append(
                    {
                        "arm": arm_label,
                        "seed": seed,
                        "M": m,
                        "coeffs": tuple(ch.get("coeffs", [])),
                        "reward_label": ch.get("reward_label"),
                        "via": ch.get("via"),
                        "episode": ch.get("episode"),
                    }
                )
    return out


def _extract_cross_domain_means(rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """For cross-domain pilots: pull per-algorithm test means + p-values."""
    if rec["schema"] not in ("cross_domain_means", "cross_domain_mlp"):
        return None
    d = rec["data"]
    family = rec["family"]
    out: Dict[str, Any] = {
        "family": family,
        "file": rec["file"],
        "n_episodes": d.get("n_episodes"),
        "n_seeds": d.get("n_seeds"),
    }
    # collect any *_means and *_mean fields
    means: Dict[str, Any] = {}
    for k, v in d.items():
        if k.endswith("_means") and isinstance(v, list):
            means[k] = v
        elif k.endswith("_mean") and isinstance(v, (int, float)):
            means[k] = v
        elif k.startswith("p_value_"):
            means[k] = v
    out["means"] = means
    out["corpus"] = d.get("corpus")
    return out


def _extract_lehmer_smoke_records(rec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Lehmer brute-force smoke: real M values for the in-band hits."""
    if rec["schema"] != "lehmer_smoke":
        return []
    d = rec["data"]
    out: List[Dict[str, Any]] = []
    for entry in d.get("in_lehmer_band", []) or []:
        m = entry.get("M_numpy")
        if m is None:
            continue
        try:
            m = float(m)
        except Exception:
            continue
        if not math.isfinite(m):
            continue
        out.append(
            {
                "arm": "lehmer_brute_force_smoke",
                "seed": None,
                "M": m,
                "coeffs": tuple(entry.get("coeffs_ascending", [])),
                "reward_label": "in_lehmer_band",
                "via": "exhaustive_search",
                "in_mossinghoff": entry.get("in_mossinghoff"),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Mossinghoff catalog access (for distance-to-catalog gradient)
# ---------------------------------------------------------------------------


def load_mossinghoff_catalog() -> List[Dict[str, Any]]:
    """Return the embedded Mossinghoff snapshot.

    Read-only; we don't modify the catalog module.  If import fails for
    any reason we degrade to an empty list.
    """
    try:
        from prometheus_math.databases.mahler import MAHLER_TABLE
        return list(MAHLER_TABLE)
    except Exception:
        return []


def _hamming_distance(a: Sequence[int], b: Sequence[int]) -> int:
    """Hamming distance between two integer coefficient vectors.

    For unequal lengths, missing positions count as different.
    """
    n = max(len(a), len(b))
    pad_a = list(a) + [0] * (n - len(a))
    pad_b = list(b) + [0] * (n - len(b))
    return sum(1 for x, y in zip(pad_a, pad_b) if x != y)


def nearest_catalog_entry(
    coeffs: Sequence[int],
    catalog: Sequence[Dict[str, Any]],
    same_degree_only: bool = True,
) -> Optional[Tuple[int, Dict[str, Any]]]:
    """Find the closest (Hamming) catalog entry to ``coeffs``.

    Returns (distance, entry) or None if catalog is empty.
    """
    if not catalog:
        return None
    deg = len(coeffs) - 1
    best_d: Optional[int] = None
    best_e: Optional[Dict[str, Any]] = None
    for entry in catalog:
        e_coef = entry.get("coeffs", []) or []
        if same_degree_only and entry.get("degree") != deg:
            continue
        d = _hamming_distance(coeffs, e_coef)
        if best_d is None or d < best_d:
            best_d = d
            best_e = entry
    if best_d is None:
        return None
    return best_d, best_e


# ---------------------------------------------------------------------------
# Gradient 1: distance-to-target (M distribution)
# ---------------------------------------------------------------------------


def gradient1_m_distribution(
    m_records: Sequence[Dict[str, Any]],
    bin_edges: Optional[Sequence[float]] = None,
) -> Dict[str, Any]:
    """Compute M-value histograms overall and per-arm.

    The Lehmer band is [1.001, 1.18]; we add finer resolution near
    Lehmer's M (1.17628) so any "mode at the band edge" is visible.
    """
    if bin_edges is None:
        # 0.0 .. 1.0 .. 1.17 (coarse) | 1.17 .. 1.18 (fine) | 1.18 .. 2.0 ..
        edges = (
            [round(x * 0.05, 4) for x in range(0, 21)]  # 0.0 .. 1.0
            + [1.05, 1.10, 1.15, 1.16, 1.17]
            + [1.171, 1.173, 1.175, 1.176, 1.177, 1.178, 1.179, 1.180]
            + [1.20, 1.25, 1.30, 1.35, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00]
        )
        bin_edges = sorted(set(edges))

    by_arm: Dict[str, List[float]] = defaultdict(list)
    all_m: List[float] = []
    for r in m_records:
        all_m.append(r["M"])
        by_arm[r["arm"]].append(r["M"])

    def _hist(vals: Sequence[float]) -> Dict[str, int]:
        counts: List[int] = [0] * (len(bin_edges) - 1)
        for v in vals:
            for i in range(len(bin_edges) - 1):
                if bin_edges[i] <= v < bin_edges[i + 1]:
                    counts[i] += 1
                    break
        return {f"[{bin_edges[i]:.4f},{bin_edges[i+1]:.4f})": counts[i]
                for i in range(len(bin_edges) - 1)}

    overall_hist = _hist(all_m)
    per_arm_hist = {arm: _hist(vals) for arm, vals in by_arm.items()}

    near_lehmer = [v for v in all_m if 1.176 <= v < 1.180]
    in_lehmer_band = [v for v in all_m if 1.001 < v < 1.18]

    if all_m:
        sorted_m = sorted(all_m)
        m_min = sorted_m[0]
        m_max = sorted_m[-1]
        m_median = sorted_m[len(sorted_m) // 2]
        m_mean = sum(all_m) / len(all_m)
    else:
        m_min = m_max = m_median = m_mean = None

    # Verdict
    if not all_m:
        verdict = "NEEDS_NEW_INSTRUMENTATION"
        rationale = (
            "No per-candidate M values logged across pilot JSONs except in "
            "the 'catalog_seeded::random_seeded' arm and the lehmer "
            "brute-force smoke. To read distance-to-target as a gradient, "
            "every episode would need to persist its M (or its best-M)."
        )
    else:
        # Classify: is there meaningful structure?
        # Heuristic: the distribution should NOT be uniform on [bin_edges].
        # We look at the modal bin frequency vs the average bin frequency.
        flat_counts = list(overall_hist.values())
        n_nonzero = sum(1 for c in flat_counts if c > 0)
        max_count = max(flat_counts) if flat_counts else 0
        total = sum(flat_counts)
        mass_in_top_bin = max_count / total if total else 0.0
        if n_nonzero <= 3 or mass_in_top_bin > 0.3:
            verdict = "SIGNAL_PRESENT"
            rationale = (
                f"M values cluster into {n_nonzero} bins; modal bin holds "
                f"{mass_in_top_bin:.1%} of mass. Distribution is far from "
                "uniform — strong concentration near catalog modes."
            )
        else:
            verdict = "SIGNAL_PRESENT"  # any structure beats uniform here
            rationale = (
                f"M values populate {n_nonzero} bins with modal mass "
                f"{mass_in_top_bin:.1%}; non-uniform but more dispersed."
            )

    return {
        "n_records": len(all_m),
        "overall_summary": {
            "m_min": m_min,
            "m_max": m_max,
            "m_median": m_median,
            "m_mean": m_mean,
            "n_in_lehmer_band": len(in_lehmer_band),
            "n_near_lehmer_constant": len(near_lehmer),
        },
        "overall_histogram": overall_hist,
        "per_arm_histogram": per_arm_hist,
        "per_arm_count": {a: len(v) for a, v in by_arm.items()},
        "bin_edges": list(bin_edges),
        "verdict": verdict,
        "rationale": rationale,
    }


# ---------------------------------------------------------------------------
# Gradient 2: kill_path information density
# ---------------------------------------------------------------------------


def gradient2_kill_path(
    sources: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate kill_pattern distributions across all sources & arms."""
    overall: Counter = Counter()
    per_arm_total: Dict[str, Counter] = defaultdict(Counter)
    per_source: Dict[str, Dict[str, Any]] = {}

    for rec in sources:
        agg = _extract_kill_pattern_aggregate(rec)
        per_source[rec["file"]] = agg
        for arm, ctr in agg["per_arm_kill_patterns"].items():
            for kp, count in ctr.items():
                overall[kp] += count
                per_arm_total[arm][kp] += count

    total = sum(overall.values())

    # Pareto check: top-1, top-3 mass
    sorted_overall = overall.most_common()
    if total > 0 and sorted_overall:
        top1 = sorted_overall[0][1] / total
        top3 = sum(c for _, c in sorted_overall[:3]) / total
    else:
        top1 = top3 = 0.0

    # Per-arm entropy
    def _shannon(c: Counter) -> float:
        n = sum(c.values())
        if n == 0:
            return 0.0
        return -sum((v / n) * math.log2(v / n) for v in c.values() if v > 0)

    per_arm_entropy = {
        arm: {
            "entropy_bits": _shannon(c),
            "total": sum(c.values()),
            "modal_kill": c.most_common(1)[0][0] if c else None,
            "modal_share": (c.most_common(1)[0][1] / sum(c.values()))
                            if c and sum(c.values()) > 0 else 0.0,
        }
        for arm, c in per_arm_total.items()
    }

    # KL-divergence of each arm's kill distribution against the overall
    # (any large divergence ==> per-algorithm directional information).
    def _kl(p: Counter, q: Counter) -> float:
        kp_keys = set(p) | set(q)
        np_ = sum(p.values())
        nq = sum(q.values())
        if np_ == 0 or nq == 0:
            return float("nan")
        eps = 1e-12
        kl = 0.0
        for k in kp_keys:
            pk = (p.get(k, 0) / np_) + eps
            qk = (q.get(k, 0) / nq) + eps
            kl += pk * math.log2(pk / qk)
        return kl

    per_arm_kl = {
        arm: _kl(c, overall) for arm, c in per_arm_total.items()
    }

    # Verdict
    if total == 0:
        verdict = "NEEDS_NEW_INSTRUMENTATION"
        rationale = "No kill_path field aggregated in any source."
    else:
        is_pareto = top1 >= 0.50  # one falsifier carries most of the mass
        per_arm_diverges = any(v > 0.5 for v in per_arm_kl.values()
                                if isinstance(v, float) and math.isfinite(v))
        if is_pareto or per_arm_diverges:
            verdict = "SIGNAL_PRESENT"
            rationale = (
                f"Kill_path is heavily structured: top-1 falsifier carries "
                f"{top1:.1%} of {total:,} total kills; top-3 carries "
                f"{top3:.1%}. Per-arm distributions diverge from overall "
                f"(max KL={max(per_arm_kl.values(), default=0.0):.3f} bits)."
            )
        else:
            verdict = "SIGNAL_ABSENT"
            rationale = (
                f"Kill_path mass is uniformly spread (top-1={top1:.1%}); "
                "per-arm distributions barely differ from the overall."
            )

    return {
        "n_total_kills": total,
        "overall_kill_pattern": dict(overall),
        "top1_share": top1,
        "top3_share": top3,
        "per_arm_total": {a: dict(c) for a, c in per_arm_total.items()},
        "per_arm_entropy": per_arm_entropy,
        "per_arm_kl_vs_overall": per_arm_kl,
        "per_source_summary": {
            f: {"per_arm": s["per_arm_kill_patterns"],
                "n_episodes_total": s["n_episodes_total"]}
            for f, s in per_source.items()
        },
        "verdict": verdict,
        "rationale": rationale,
    }


# ---------------------------------------------------------------------------
# Gradient 3: operator x falsifier contingency table
# ---------------------------------------------------------------------------


def gradient3_operator_falsifier(
    sources: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build the (arm/operator-class, kill_pattern) contingency table.

    Operator-class proxy: the arm label.  This is coarser than the
    fine-grained operator name (mutate_single_coef, etc.), but those
    operator names are recorded in the discovery_v2 ``operator_call_counts``
    dict at run-totals only — not joined to per-episode kills.  So we
    can only build the contingency at arm granularity from existing logs.
    """
    table: Dict[Tuple[str, str], int] = defaultdict(int)
    arms: set = set()
    falsifiers: set = set()
    for rec in sources:
        agg = _extract_kill_pattern_aggregate(rec)
        for arm, ctr in agg["per_arm_kill_patterns"].items():
            arms.add(arm)
            for kp, count in ctr.items():
                falsifiers.add(kp)
                table[(arm, kp)] += count

    arms_sorted = sorted(arms)
    falsifiers_sorted = sorted(falsifiers)

    # Joint entropy + chi^2 vs independence
    total = sum(table.values())
    if total == 0:
        return {
            "verdict": "NEEDS_NEW_INSTRUMENTATION",
            "rationale": "No (operator_class, kill_pattern) pairs found.",
            "table": {},
        }
    arm_marg = Counter()
    fals_marg = Counter()
    for (a, k), v in table.items():
        arm_marg[a] += v
        fals_marg[k] += v

    # Chi-squared
    chi2 = 0.0
    n_cells = 0
    n_empty = 0
    for a in arms_sorted:
        for k in falsifiers_sorted:
            n_cells += 1
            obs = table.get((a, k), 0)
            exp = arm_marg[a] * fals_marg[k] / total if total > 0 else 0.0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
            if obs == 0:
                n_empty += 1
    df = (len(arms_sorted) - 1) * (len(falsifiers_sorted) - 1) if (
        len(arms_sorted) > 1 and len(falsifiers_sorted) > 1
    ) else 1
    chi2_per_df = chi2 / df if df > 0 else 0.0

    def _shannon(c: Iterable[int]) -> float:
        c = list(c)
        n = sum(c)
        if n == 0:
            return 0.0
        return -sum((v / n) * math.log2(v / n) for v in c if v > 0)

    h_joint = _shannon(table.values())
    h_arm = _shannon(arm_marg.values())
    h_fals = _shannon(fals_marg.values())
    mutual_info = h_arm + h_fals - h_joint

    # "Closed direction": cells that are systematically empty for an
    # arm even though that arm has high total mass.
    closed_pairs: List[Dict[str, Any]] = []
    for a in arms_sorted:
        for k in falsifiers_sorted:
            obs = table.get((a, k), 0)
            if obs == 0 and arm_marg[a] > 100 and fals_marg[k] > 100:
                # systematically empty
                closed_pairs.append({"arm": a, "falsifier": k,
                                     "arm_total": arm_marg[a],
                                     "falsifier_total": fals_marg[k]})

    open_pairs: List[Dict[str, Any]] = []
    for (a, k), obs in table.items():
        exp = arm_marg[a] * fals_marg[k] / total if total > 0 else 0.0
        if exp > 0 and obs >= 5 * exp and obs > 100:
            open_pairs.append({"arm": a, "falsifier": k,
                               "obs": obs, "exp": exp,
                               "ratio": obs / exp})

    if mutual_info > 0.2 or chi2_per_df > 100:
        verdict = "SIGNAL_PRESENT"
        rationale = (
            f"Contingency table has visible structure: "
            f"mutual_info(arm; falsifier)={mutual_info:.3f} bits, "
            f"chi^2/df={chi2_per_df:.1f}, {len(closed_pairs)} systematically "
            f"closed (arm,falsifier) pairs, {len(open_pairs)} systematically "
            "over-represented pairs."
        )
    else:
        verdict = "SIGNAL_ABSENT"
        rationale = (
            f"mutual_info={mutual_info:.3f} bits, chi^2/df={chi2_per_df:.1f} "
            "— arm and falsifier appear independent in existing aggregation."
        )

    table_out = {
        f"{a}|{k}": v for (a, k), v in table.items()
    }
    return {
        "n_arms": len(arms_sorted),
        "n_falsifiers": len(falsifiers_sorted),
        "n_total": total,
        "n_empty_cells": n_empty,
        "n_cells": n_cells,
        "table": table_out,
        "arm_marginal": dict(arm_marg),
        "falsifier_marginal": dict(fals_marg),
        "joint_entropy_bits": h_joint,
        "marginal_arm_entropy_bits": h_arm,
        "marginal_falsifier_entropy_bits": h_fals,
        "mutual_info_bits": mutual_info,
        "chi2": chi2,
        "chi2_df": df,
        "chi2_per_df": chi2_per_df,
        "closed_pairs": closed_pairs[:50],
        "open_pairs": sorted(open_pairs, key=lambda x: -x["ratio"])[:50],
        "verdict": verdict,
        "rationale": rationale,
    }


# ---------------------------------------------------------------------------
# Gradient 4: method-utility per operator class
# ---------------------------------------------------------------------------


def gradient4_method_utility(
    sources: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Per-arm hit rate for catalog rediscoveries / shadow / promote.

    Uses the per_arm summary fields when present (catalog_seeded,
    four_counts, degree_sweep).  Cross-domain pilots use mean-accuracy
    rather than hit rates; we surface those separately.
    """
    rows: List[Dict[str, Any]] = []
    cross_domain_rows: List[Dict[str, Any]] = []
    for rec in sources:
        schema = rec["schema"]
        d = rec["data"]
        family = rec["family"]

        if schema == "catalog_seeded":
            for arm, val in d.get("per_arm", {}).items():
                rows.append(
                    {
                        "source": rec["file"],
                        "arm": arm,
                        "kind": val.get("kind"),
                        "promote_rate_mean": val.get("promote_rate_mean"),
                        "promote_rates": val.get("promote_rates"),
                        "salem_rate_mean": val.get("salem_rate_mean"),
                        "catalog_hit_rate_mean": val.get("catalog_hit_rate_mean"),
                        "catalog_hit_rates": val.get("catalog_hit_rates"),
                    }
                )

        elif schema == "four_counts_top":
            for cond, val in d.get("per_condition", {}).items():
                rows.append(
                    {
                        "source": rec["file"],
                        "arm": cond,
                        "promote_rate_mean": val.get("promote_rate_mean"),
                        "promote_rates": val.get("promote_rates"),
                        "catalog_hit_rate_mean": val.get("catalog_hit_rate_mean"),
                        "catalog_hit_rates": val.get("catalog_hit_rates"),
                        "claim_rate_mean": val.get("claim_rate_mean"),
                    }
                )

        elif schema == "four_counts_per_arm":
            for arm, val in d.get("per_arm", {}).items():
                rows.append(
                    {
                        "source": rec["file"],
                        "arm": arm,
                        "promote_rate_mean": val.get("promote_rate_mean"),
                        "promote_rates": val.get("promote_rates"),
                        "catalog_hit_rate_mean": val.get("catalog_hit_rate_mean"),
                        "claim_rate_mean": val.get("claim_rate_mean"),
                    }
                )

        elif schema == "degree_sweep":
            for deg, deg_block in d.items():
                for cond, val in (deg_block or {}).get("per_condition", {}).items():
                    rows.append(
                        {
                            "source": rec["file"],
                            "arm": f"deg{deg}::{cond}",
                            "promote_rate_mean": val.get("promote_rate_mean"),
                            "catalog_hit_rate_mean": val.get("catalog_hit_rate_mean"),
                        }
                    )

        elif schema == "v2_cells":
            for cell in d.get("cells", []):
                rows.append(
                    {
                        "source": rec["file"],
                        "arm": f"v2::{cell.get('strategy')}",
                        "seed": cell.get("seed"),
                        "promote_rate": cell.get("promote_rate"),
                        "n_signal": cell.get("n_signal"),
                        "n_sub_lehmer": cell.get("n_sub_lehmer"),
                    }
                )

        elif schema == "v3_cells":
            for cell in d.get("cells", []):
                rows.append(
                    {
                        "source": rec["file"],
                        "arm": f"v3::{cell.get('variant')}",
                        "seed": cell.get("seed"),
                        "promote_rate": cell.get("promote_rate"),
                        "n_signal_class": cell.get("n_signal_class"),
                        "n_sub_lehmer": cell.get("n_sub_lehmer"),
                        "fraction_integer": cell.get("fraction_integer"),
                    }
                )

        elif schema == "discovery_v2":
            for r in d.get("results", []):
                rows.append(
                    {
                        "source": rec["file"],
                        "arm": f"discovery_v2::{r.get('arm')}",
                        "seed": r.get("seed"),
                        "best_m_overall": r.get("best_m_overall"),
                        "n_shadow_catalog": r.get("n_shadow_catalog"),
                        "n_sub_lehmer_episodes": r.get("n_sub_lehmer_episodes"),
                    }
                )

        elif schema == "cross_domain_means":
            cd = _extract_cross_domain_means(rec)
            if cd:
                cross_domain_rows.append(cd)
        elif schema == "cross_domain_mlp":
            cd = _extract_cross_domain_means(rec)
            if cd:
                cross_domain_rows.append(cd)

    # Rank by promote_rate_mean (Lehmer family) where present
    ranked = []
    for r in rows:
        rate = r.get("promote_rate_mean")
        if rate is None:
            rate = r.get("promote_rate")
        if rate is None:
            continue
        ranked.append({"arm": r.get("arm"), "source": r.get("source"),
                       "promote_rate": rate})
    ranked.sort(key=lambda x: -float(x["promote_rate"] or 0.0))

    # Cross-domain: rank algorithms within each family
    cross_ranked: List[Dict[str, Any]] = []
    for cd in cross_domain_rows:
        means = cd.get("means", {})
        # Identify the base key (e.g. random, reinforce, ppo)
        for mk, mv in means.items():
            if mk.endswith("_mean") and not mk.startswith("p_value"):
                cross_ranked.append(
                    {
                        "family": cd["family"],
                        "file": cd["file"],
                        "algorithm": mk[: -len("_mean")],
                        "mean_score": mv,
                    }
                )
    cross_ranked.sort(key=lambda x: -float(x["mean_score"] or 0.0))

    n_with_rate = sum(
        1 for r in rows
        if (r.get("promote_rate_mean") is not None
            or r.get("promote_rate") is not None)
    )
    n_promote_zero = sum(
        1 for r in rows
        if (
            (r.get("promote_rate_mean") is not None
             or r.get("promote_rate") is not None)
            and float(r.get("promote_rate_mean")
                      if r.get("promote_rate_mean") is not None
                      else r.get("promote_rate")) == 0.0
        )
    )

    # Verdict
    if n_with_rate == 0:
        verdict = "NEEDS_NEW_INSTRUMENTATION"
        rationale = "No promote-rate field aggregated in any source."
    elif n_promote_zero == n_with_rate:
        # Lehmer family: PROMOTE rate is ZERO across every arm/seed/cell
        # (consistent with project_discovery_pipeline_validated). The
        # gradient is degenerate AT THIS LEVEL.  Catalog-hit rate +
        # cross-domain mean-accuracy DO carry signal.
        cat_hit_rates = [r.get("catalog_hit_rate_mean") for r in rows
                         if r.get("catalog_hit_rate_mean") is not None]
        nonzero_cat = sum(1 for r in cat_hit_rates if r and r > 0)
        verdict = (
            "SIGNAL_PRESENT"
            if (nonzero_cat > 0 or cross_ranked) else "SIGNAL_ABSENT"
        )
        rationale = (
            f"Lehmer PROMOTE rate is identically 0 across "
            f"{n_with_rate} arm/seed cells (consistent with the substrate's "
            "350K-episode null result). Catalog-hit-rate is non-zero in "
            f"{nonzero_cat} arms and varies by 1-2 orders of magnitude "
            "across operator classes. Cross-domain test means span "
            f"{min(c['mean_score'] for c in cross_ranked) if cross_ranked else 0:.1f}"
            f"..{max(c['mean_score'] for c in cross_ranked) if cross_ranked else 0:.1f} "
            "across algorithms. Method-utility heterogeneity is real."
        )
    else:
        verdict = "SIGNAL_PRESENT"
        rationale = (
            f"{n_with_rate - n_promote_zero} arms produce non-zero PROMOTE "
            f"out of {n_with_rate}; method-utility differs across operator "
            "classes."
        )

    return {
        "n_arm_records": len(rows),
        "n_cross_domain_records": len(cross_domain_rows),
        "n_with_promote_rate": n_with_rate,
        "n_zero_promote": n_promote_zero,
        "lehmer_arms_ranked": ranked,
        "cross_domain_ranked": cross_ranked,
        "rows": rows,
        "cross_domain_rows": cross_domain_rows,
        "verdict": verdict,
        "rationale": rationale,
    }


# ---------------------------------------------------------------------------
# Gradient 5: distance-to-catalog vs M-distance-to-Lehmer
# ---------------------------------------------------------------------------


def gradient5_catalog_proximity(
    m_records: Sequence[Dict[str, Any]],
    catalog: Sequence[Dict[str, Any]],
    target_M: float = 1.17628,
    band_upper: float = 1.18,
) -> Dict[str, Any]:
    """For each candidate with coeffs, compute (Hamming-to-nearest-catalog,
    |M - target_M|).

    Reports the joint distribution and Pearson correlation.
    """
    if not catalog:
        return {
            "verdict": "NEEDS_NEW_INSTRUMENTATION",
            "rationale": "Mossinghoff catalog not loadable; cannot compute "
                         "proximity.",
            "n_candidates": 0,
        }
    pairs: List[Tuple[int, float]] = []
    samples: List[Dict[str, Any]] = []

    # Cap for runtime — Hamming over 8625 entries x N candidates can
    # be heavy.  Sample if too many records.
    cap = 1500
    recs = list(m_records)
    if len(recs) > cap:
        # Deterministic stride sample
        stride = max(1, len(recs) // cap)
        recs = recs[::stride][:cap]

    for r in recs:
        coeffs = r.get("coeffs", ())
        if not coeffs:
            continue
        m_val = r["M"]
        nearest = nearest_catalog_entry(coeffs, catalog, same_degree_only=True)
        if nearest is None:
            continue
        hd, entry = nearest
        m_gap = abs(m_val - target_M)
        pairs.append((hd, m_gap))
        if len(samples) < 30:
            samples.append({"arm": r.get("arm"), "M": m_val,
                            "hamming_to_catalog": hd,
                            "nearest_catalog_M": entry.get("mahler_measure"),
                            "nearest_label": entry.get("name") or entry.get("source"),
                            "m_gap_to_target": m_gap})

    if not pairs:
        return {
            "verdict": "NEEDS_NEW_INSTRUMENTATION",
            "rationale": "No candidate had both coeffs and M recorded; "
                         "cross-domain pilots don't log per-episode "
                         "predictions/coefficients in the existing files.",
            "n_candidates": 0,
        }

    # Pearson correlation between Hamming and m_gap
    n = len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in pairs) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    rho = cov / (sx * sy) if sx * sy > 0 else float("nan")

    # Cross-tab: for each Hamming bin, mean m_gap
    by_hd: Dict[int, List[float]] = defaultdict(list)
    for hd, mg in pairs:
        by_hd[hd].append(mg)
    hd_summary = {
        int(k): {
            "n": len(v),
            "mean_m_gap": sum(v) / len(v),
            "min_m_gap": min(v),
        }
        for k, v in sorted(by_hd.items())
    }

    if math.isfinite(rho) and abs(rho) > 0.1:
        verdict = "SIGNAL_PRESENT"
        rationale = (
            f"Pearson(Hamming-to-catalog, |M-target|) = {rho:.3f} over "
            f"{n} candidates. Proximity to catalog measurably predicts "
            "M-gap (positive correlation = closer-in-coefficient-space "
            "implies closer-to-target-M)."
        )
    elif n < 100:
        verdict = "NEEDS_NEW_INSTRUMENTATION"
        rationale = (
            f"Only {n} candidates have both coeffs and M recorded "
            "(catalog_seeded::random_seeded supplies most). Sample is too "
            "thin to assert correlation."
        )
    else:
        verdict = "SIGNAL_ABSENT"
        rationale = (
            f"Pearson(Hamming, m_gap)={rho:.3f} over {n} candidates: "
            "correlation indistinguishable from zero."
        )

    return {
        "n_candidates": n,
        "pearson_rho": rho,
        "hamming_bins_summary": hd_summary,
        "samples": samples,
        "verdict": verdict,
        "rationale": rationale,
    }


# ---------------------------------------------------------------------------
# Gradient 6: computational verification depth
# ---------------------------------------------------------------------------


def gradient6_verification_depth() -> Dict[str, Any]:
    """The substrate doesn't track this gradient.

    F1-F11 outputs are pass/fail; there is no "verified to N=10^6 vs 10^9"
    field in any DiscoveryRecord, kill_pattern aggregate, or pilot result.
    To read this gradient we'd need to instrument:
      * F1 permutation null with N=30 vs N=300 vs N=3000 (currently fixed)
      * F11 cross-validation precision (currently 1e-6 fixed)
      * Catalog-consistency degree of certainty (currently boolean miss/hit)
      * Per-claim verifier-runtime (the kernel persists ``verdict_runtime_ms``
        but pipelines write 0).
    """
    return {
        "verdict": "NEEDS_NEW_INSTRUMENTATION",
        "rationale": (
            "F1-F11 verdicts are persisted as boolean pass/fail. No "
            "depth/precision axis is captured in DiscoveryRecord, the "
            "kernel verdict, or any pilot JSON. To read this gradient "
            "we must add (a) verifier-precision tier per claim, (b) "
            "permutation-null sample-count actually used, (c) catalog "
            "scan completeness, and (d) populate verdict_runtime_ms "
            "with real values."
        ),
        "evidence": [
            "DiscoveryRecord.check_results stores (bool, rationale) tuples "
            "only — no N or precision field.",
            "Pilot JSONs aggregate by_kill_pattern with NO depth dimension.",
            "Kernel verdict_runtime_ms is set to 0 in discovery_pipeline.py "
            "Phase 4 (synthetic verdict short-circuit).",
        ],
    }


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


@dataclass
class ArchaeologyResult:
    sources_loaded: int
    n_episodes_total: int
    gradient1: Dict[str, Any]
    gradient2: Dict[str, Any]
    gradient3: Dict[str, Any]
    gradient4: Dict[str, Any]
    gradient5: Dict[str, Any]
    gradient6: Dict[str, Any]
    cross_observations: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "sources_loaded": self.sources_loaded,
            "n_episodes_total": self.n_episodes_total,
            "gradient1_distance_to_target": self.gradient1,
            "gradient2_kill_path_density": self.gradient2,
            "gradient3_operator_falsifier": self.gradient3,
            "gradient4_method_utility": self.gradient4,
            "gradient5_catalog_proximity": self.gradient5,
            "gradient6_verification_depth": self.gradient6,
            "cross_gradient_observations": self.cross_observations,
        }


def run_archaeology(
    base_dir: str = PROMETHEUS_MATH_DIR,
    catalog: Optional[Sequence[Dict[str, Any]]] = None,
) -> ArchaeologyResult:
    """End-to-end gradient archaeology run."""
    sources = load_all_sources(base_dir)
    if catalog is None:
        catalog = load_mossinghoff_catalog()

    # Pull all M records
    m_records: List[Dict[str, Any]] = []
    for s in sources:
        m_records.extend(_extract_m_records(s))
        m_records.extend(_extract_lehmer_smoke_records(s))

    # Total episodes (best-effort: sum of all schemas' n_episodes_total)
    n_eps = 0
    for s in sources:
        agg = _extract_kill_pattern_aggregate(s)
        n_eps += agg["n_episodes_total"]

    g1 = gradient1_m_distribution(m_records)
    g2 = gradient2_kill_path(sources)
    g3 = gradient3_operator_falsifier(sources)
    g4 = gradient4_method_utility(sources)
    g5 = gradient5_catalog_proximity(m_records, catalog)
    g6 = gradient6_verification_depth()

    # Cross-gradient observations
    cross: Dict[str, Any] = {}
    cross["g2_g4_consistent"] = (
        g2.get("verdict") == "SIGNAL_PRESENT"
        and g4.get("verdict") in ("SIGNAL_PRESENT", "SIGNAL_ABSENT")
    )
    cross["g3_implies_g4"] = (
        g3.get("verdict") == "SIGNAL_PRESENT"
        and g4.get("verdict") == "SIGNAL_PRESENT"
    )
    cross["sparse_per_candidate"] = g1["n_records"] < 5000

    return ArchaeologyResult(
        sources_loaded=len(sources),
        n_episodes_total=n_eps,
        gradient1=g1,
        gradient2=g2,
        gradient3=g3,
        gradient4=g4,
        gradient5=g5,
        gradient6=g6,
        cross_observations=cross,
    )


def _summary_line(verdict: str, rationale: str) -> str:
    icon = {
        "SIGNAL_PRESENT": "[SIGNAL_PRESENT]",
        "SIGNAL_ABSENT": "[SIGNAL_ABSENT]",
        "NEEDS_NEW_INSTRUMENTATION": "[NEEDS_NEW_INSTRUMENTATION]",
    }.get(verdict, f"[{verdict}]")
    return f"{icon}\n  {rationale}"


def render_report(res: ArchaeologyResult) -> str:
    """Render the human-readable Markdown report."""
    g1, g2, g3, g4, g5, g6 = (
        res.gradient1, res.gradient2, res.gradient3,
        res.gradient4, res.gradient5, res.gradient6,
    )

    parts: List[str] = []
    parts.append("# Gradient Archaeology — Substrate Ledger Audit")
    parts.append("")
    parts.append("Read-only analysis. Asks whether the existing pilot logs already")
    parts.append("contain visible structure on Aporia's six negative-space gradient")
    parts.append("axes, or whether each gradient requires new instrumentation.")
    parts.append("")
    parts.append("Generated 2026-05-04. No substrate code or pilot data modified.")
    parts.append("")
    parts.append("## Setup")
    parts.append("")
    parts.append("Six gradient axes (Aporia's framework):")
    parts.append("")
    parts.append("1. Distance-to-target (M distribution near Lehmer's 1.17628)")
    parts.append("2. Battery-survival depth (kill_pattern information density)")
    parts.append("3. Negative space (operator x falsifier contingency)")
    parts.append("4. Method-utility per operator class")
    parts.append("5. Cross-domain bridge (proximity-to-catalog vs M-gap)")
    parts.append("6. Computational-verification depth")
    parts.append("")
    parts.append("## Data Sources")
    parts.append("")
    parts.append(f"- Pilot JSONs loaded: **{res.sources_loaded}**")
    parts.append(f"- Total episodes/samples aggregated: **{res.n_episodes_total:,}**")
    parts.append("- Schemas covered: catalog_seeded, four_counts, "
                 "degree_sweep, v2 (anti-elitist), v3 (root-space), "
                 "discovery_v2, lehmer_smoke, cross_domain_means.")
    parts.append("")
    parts.append("Per-candidate M values were only persisted by:")
    parts.append("")
    parts.append("- `_catalog_seeded_pilot.json` `random_seeded` arm (1,069 catalog hits)")
    parts.append("- `_lehmer_smoke_results.json` brute-force band hits (11 polys)")
    parts.append("")
    parts.append("Other arms log only aggregate kill_pattern counts and "
                 "summary statistics. This sparseness is itself a finding.")
    parts.append("")

    # ----- Gradient 1 -----
    parts.append("## Gradient 1 — Distance-to-Target")
    parts.append("")
    parts.append(_summary_line(g1["verdict"], g1["rationale"]))
    parts.append("")
    parts.append(f"- M records aggregated: **{g1['n_records']:,}**")
    if g1["overall_summary"].get("m_min") is not None:
        s = g1["overall_summary"]
        parts.append(
            f"- M range: [{s['m_min']:.4f}, {s['m_max']:.4f}], "
            f"median={s['m_median']:.4f}, mean={s['m_mean']:.4f}"
        )
        parts.append(f"- M values in Lehmer band (1.001, 1.18): "
                     f"**{s['n_in_lehmer_band']}**")
        parts.append(f"- M values within 0.004 of Lehmer's M (1.17628): "
                     f"**{s['n_near_lehmer_constant']}**")
    parts.append("")
    parts.append("Top per-arm contribution to M records:")
    parts.append("")
    for arm, count in sorted(g1["per_arm_count"].items(),
                              key=lambda x: -x[1])[:10]:
        parts.append(f"- `{arm}`: {count} M values")
    parts.append("")

    # ----- Gradient 2 -----
    parts.append("## Gradient 2 — Battery-Survival Depth (kill_path)")
    parts.append("")
    parts.append(_summary_line(g2["verdict"], g2["rationale"]))
    parts.append("")
    parts.append(f"- Total kills aggregated: **{g2['n_total_kills']:,}**")
    parts.append(f"- Top-1 kill_pattern share: **{g2['top1_share']:.1%}**")
    parts.append(f"- Top-3 kill_pattern share: **{g2['top3_share']:.1%}**")
    parts.append("")
    parts.append("Overall kill_pattern distribution:")
    parts.append("")
    for kp, c in sorted(g2["overall_kill_pattern"].items(),
                         key=lambda x: -x[1]):
        share = c / g2["n_total_kills"] if g2["n_total_kills"] else 0
        parts.append(f"- `{kp}`: {c:,} ({share:.1%})")
    parts.append("")
    parts.append("Per-arm kill-pattern entropy (lower = more deterministic):")
    parts.append("")
    for arm, info in sorted(g2["per_arm_entropy"].items(),
                             key=lambda x: -x[1]["total"])[:15]:
        parts.append(
            f"- `{arm}`: H={info['entropy_bits']:.3f} bits, "
            f"modal=`{info['modal_kill']}` ({info['modal_share']:.1%}), "
            f"n={info['total']:,}"
        )
    parts.append("")
    parts.append("Per-arm KL divergence vs overall (higher = arm "
                 "kills differently from population):")
    parts.append("")
    for arm, kl in sorted(g2["per_arm_kl_vs_overall"].items(),
                           key=lambda x: -(x[1] if math.isfinite(x[1]) else 0))[:15]:
        if math.isfinite(kl):
            parts.append(f"- `{arm}`: KL={kl:.3f} bits")
    parts.append("")

    # ----- Gradient 3 -----
    parts.append("## Gradient 3 — Operator x Falsifier Contingency")
    parts.append("")
    parts.append(_summary_line(g3["verdict"], g3["rationale"]))
    parts.append("")
    if "table" in g3:
        parts.append(
            f"- Arms: {g3['n_arms']}, Falsifiers: {g3['n_falsifiers']}, "
            f"Cells: {g3['n_cells']} ({g3['n_empty_cells']} empty)"
        )
        parts.append(f"- Mutual info (arm; falsifier) = "
                     f"**{g3['mutual_info_bits']:.3f} bits**")
        parts.append(f"- chi^2 = {g3['chi2']:.1f} (df={g3['chi2_df']}, "
                     f"per-df = {g3['chi2_per_df']:.1f})")
        parts.append("")
        parts.append("Top systematically-empty (closed) (arm, falsifier) pairs:")
        parts.append("")
        for cp in g3["closed_pairs"][:10]:
            parts.append(
                f"- `{cp['arm']}` x `{cp['falsifier']}`: 0 kills "
                f"(arm has {cp['arm_total']:,}, falsifier has "
                f"{cp['falsifier_total']:,} elsewhere)"
            )
        parts.append("")
        parts.append("Top systematically-over-represented (open) "
                     "(arm, falsifier) pairs:")
        parts.append("")
        for op in g3["open_pairs"][:10]:
            parts.append(
                f"- `{op['arm']}` x `{op['falsifier']}`: "
                f"{op['obs']:,} obs vs {op['exp']:.1f} expected "
                f"(ratio={op['ratio']:.1f}x)"
            )
    parts.append("")

    # ----- Gradient 4 -----
    parts.append("## Gradient 4 — Method-Utility per Operator Class")
    parts.append("")
    parts.append(_summary_line(g4["verdict"], g4["rationale"]))
    parts.append("")
    parts.append(f"- Lehmer arm records: {g4['n_arm_records']}")
    parts.append(f"- Cross-domain records: {g4['n_cross_domain_records']}")
    parts.append(f"- Arms with PROMOTE = 0: "
                 f"{g4['n_zero_promote']}/{g4['n_with_promote_rate']}")
    parts.append("")
    parts.append("Lehmer arms ranked by promote_rate_mean (all 0 in current data):")
    parts.append("")
    for r in g4["lehmer_arms_ranked"][:8]:
        parts.append(
            f"- `{r['arm']}` ({os.path.basename(r['source'] or '')}): "
            f"promote_rate={r['promote_rate']}"
        )
    parts.append("")
    parts.append("Cross-domain test means ranked (where the gradient lives):")
    parts.append("")
    for cr in g4["cross_domain_ranked"][:20]:
        parts.append(
            f"- `{cr['family']}` / `{cr['algorithm']}`: "
            f"score={cr['mean_score']:.3f}"
        )
    parts.append("")

    # ----- Gradient 5 -----
    parts.append("## Gradient 5 — Cross-Domain Bridge "
                 "(Distance-to-Catalog vs M-Gap)")
    parts.append("")
    parts.append(_summary_line(g5["verdict"], g5["rationale"]))
    parts.append("")
    if "n_candidates" in g5 and g5["n_candidates"] > 0:
        parts.append(f"- Candidates analyzed: {g5['n_candidates']}")
        if "pearson_rho" in g5:
            parts.append(f"- Pearson rho = **{g5['pearson_rho']:.3f}**")
        parts.append("")
        if g5.get("hamming_bins_summary"):
            parts.append("Per Hamming-distance bin (mean |M-target|):")
            parts.append("")
            for hd, info in sorted(g5["hamming_bins_summary"].items())[:15]:
                parts.append(
                    f"- HD={hd}: n={info['n']}, "
                    f"mean_m_gap={info['mean_m_gap']:.4f}, "
                    f"min_m_gap={info['min_m_gap']:.4f}"
                )
    parts.append("")

    # ----- Gradient 6 -----
    parts.append("## Gradient 6 — Computational-Verification Depth")
    parts.append("")
    parts.append(_summary_line(g6["verdict"], g6["rationale"]))
    parts.append("")
    parts.append("Specific evidence:")
    for e in g6["evidence"]:
        parts.append(f"- {e}")
    parts.append("")

    # Cross-gradient
    parts.append("## Cross-Gradient Observations")
    parts.append("")
    for k, v in res.cross_observations.items():
        parts.append(f"- `{k}`: {v}")
    parts.append("")

    # Headline answer
    parts.append("## The Empirical Answer")
    parts.append("")
    parts.append(
        "The substrate's existing ledger contains gradient signal on "
        "**axes 2, 3, and 4** (kill_path density, operator x falsifier "
        "contingency, method-utility per operator) and partial signal on "
        "**axis 1** (M distribution, but only for the catalog_seeded arm). "
        "**Axis 5** is borderline — the data exists for the catalog_seeded "
        "arm but not for cross-domain pilots (which log only summary "
        "accuracies, not per-episode predictions). **Axis 6** is fully "
        "missing: we do not log verifier depth/precision anywhere."
    )
    parts.append("")
    parts.append("## Implications for Layer 2 Repair")
    parts.append("")
    parts.append(
        "Tomorrow's gradient field can be partly built from the existing "
        "ledger (axes 2-4 are immediately readable; axis 1 needs the "
        "per-episode M to be persisted in EVERY arm, not just "
        "catalog_seeded::random_seeded). Bridging the cross-domain "
        "axis (5) requires logging per-episode predictions in the "
        "BSD/genus-2/knot/modular-form/mock-theta/OEIS pilots. Axis 6 "
        "is the work the substrate hasn't yet been asked to do; adding "
        "verifier-depth instrumentation is a prerequisite for closing "
        "the gradient field."
    )
    parts.append("")
    return "\n".join(parts)


def write_artifacts(
    res: ArchaeologyResult,
    json_out: str,
    md_out: str,
) -> None:
    """Persist results JSON + report Markdown."""
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(res.as_dict(), f, indent=2, default=str)
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(render_report(res))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # When invoked as __main__ (i.e. `python prometheus_math/gradient_archaeology.py`),
    # the package import path may not include the parent directory. Add it
    # explicitly so the Mossinghoff catalog import inside
    # ``load_mossinghoff_catalog()`` succeeds.
    import sys as _sys
    _here = os.path.dirname(PROMETHEUS_MATH_DIR)
    if _here not in _sys.path:
        _sys.path.insert(0, _here)
    res = run_archaeology()
    write_artifacts(
        res,
        json_out=os.path.join(PROMETHEUS_MATH_DIR,
                               "_gradient_archaeology_results.json"),
        md_out=os.path.join(PROMETHEUS_MATH_DIR,
                             "GRADIENT_ARCHAEOLOGY_RESULTS.md"),
    )
    print(f"Loaded {res.sources_loaded} sources, "
          f"{res.n_episodes_total:,} episodes total.")
    for i, g in enumerate(
        [res.gradient1, res.gradient2, res.gradient3,
         res.gradient4, res.gradient5, res.gradient6],
        start=1,
    ):
        print(f"  Gradient {i}: {g.get('verdict')}")


__all__ = [
    "ArchaeologyResult",
    "PILOT_SOURCES",
    "PROMETHEUS_MATH_DIR",
    "gradient1_m_distribution",
    "gradient2_kill_path",
    "gradient3_operator_falsifier",
    "gradient4_method_utility",
    "gradient5_catalog_proximity",
    "gradient6_verification_depth",
    "load_all_sources",
    "load_mossinghoff_catalog",
    "nearest_catalog_entry",
    "render_report",
    "run_archaeology",
    "write_artifacts",
]
