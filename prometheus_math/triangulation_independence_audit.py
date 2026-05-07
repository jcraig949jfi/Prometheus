"""Empirical pairwise-MI audit of TriangulationProtocol's independence
assumption — per inbox ticket T-2026-05-07-T009 (P1-high).

The TriangulationProtocol (sigma_kernel/triangulation_protocol.py) upgrades
INCONCLUSIVE -> LOCAL_LEMMA only when independent paths agree. The
substrate's independence ASSERTION today is taken on trust: two falsifiers
declared "independent" via IndependenceClass tags are assumed to provide
genuinely uncorrelated evidence. This audit empirically checks that
assumption against the existing kill-record corpus by computing pairwise
mutual information (MI) between falsifier outcomes — per
``feedback_mi_bias``, MI on sparse histograms is biased upward, so we
correct against a random-pairing null.

CLI
---
::

    python -m prometheus_math.triangulation_independence_audit \\
        [--store PATH] [--threshold 0.3] [--n-null 50] [--out PATH]

Defaults
--------
* Store:     ``prometheus_math/_native_kill_vector_pilot.json``
* Threshold: 0.3 bits  (per the v2.3 lock-in: > 0.3 bits MI between
                        nominally-independent falsifiers indicates a
                        triangulation-violation candidate worth Aporia
                        review)
* n_null:    50  (random-pairing shuffles for bias-correction null)
* Out:       ``prometheus_math/TRIANGULATION_AUDIT_RESULTS.md``

Outputs
-------
* Markdown report at ``--out`` with: header, methodology, bias-corrected
  MI table for active pairs, ranked top-10, threshold-flagged list.
* Returns a dict of audit results (pair → metrics) for programmatic use.

NO contract change to KillVector, TriangulationProtocol, or any
sigma_kernel module. All acceptance criteria (#1-#6) per T009.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from prometheus_math.kill_vector import (
    ALL_COMPONENT_NAMES,
    KillVector,
)


# ---------------------------------------------------------------------------
# Defaults (per acceptance criterion #5 — documented threshold)
# ---------------------------------------------------------------------------


DEFAULT_KILL_STORE: Path = (
    Path(__file__).resolve().parent / "_native_kill_vector_pilot.json"
)
"""Default per-claim kill-record corpus. Use --store to override."""


DEFAULT_FLAG_THRESHOLD_BITS: float = 0.3
"""Per substrate v2.3: bias-corrected MI > 0.3 bits between nominally-
independent falsifier components indicates a triangulation-violation
CANDIDATE. The threshold is conservative — the original ejection-finding
MI on the kernel ledger was 0.725 bits between operators and binary
kill_path. 0.3 bits is roughly half that (the substrate's "look here"
band, not "definitely a violation" band)."""


DEFAULT_N_NULL_SHUFFLES: int = 50
"""Per ``feedback_mi_bias``: MI on sparse histograms is biased upward;
the random-pairing null estimates that bias by destroying any genuine
joint dependence while preserving each component's marginal. 50 shuffles
gives a stable mean while keeping the audit fast (~5s on 24K-episode
corpus)."""


DEFAULT_REPORT_PATH: Path = (
    Path(__file__).resolve().parent / "TRIANGULATION_AUDIT_RESULTS.md"
)
"""Default markdown output path. Use --out to override."""


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PairMI:
    """One row of the audit: (a, b) pair with observed/null/corrected MI."""
    component_a: str
    component_b: str
    observed_mi_bits: float
    null_mi_mean_bits: float
    null_mi_std_bits: float
    bias_corrected_mi_bits: float
    n_a_triggered: int
    n_b_triggered: int
    n_both_triggered: int
    flagged: bool


@dataclass(frozen=True)
class AuditResult:
    """Audit summary returned from :func:`run_audit`."""
    n_records: int
    n_active_components: int
    threshold_bits: float
    n_null_shuffles: int
    pair_results: Tuple[PairMI, ...]
    top_10: Tuple[PairMI, ...]
    flagged: Tuple[PairMI, ...]
    elapsed_s: float


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_kill_vectors_from_pilot_store(path: Path) -> List[KillVector]:
    """Load KillVectors from a pilot-store JSON file.

    Expects the schema produced by the kill-vector pilot: a top-level dict
    with ``pilot.episodes``, each episode having a ``kill_vector`` dict.
    Episodes lacking a ``kill_vector`` are silently skipped (legacy
    pre-vector records).

    Returns
    -------
    list[KillVector]
        Reconstructed via :meth:`KillVector.from_dict`. Order preserved.
    """
    with open(path, encoding="utf-8") as f:
        store = json.load(f)
    if not isinstance(store, dict) or "pilot" not in store:
        raise ValueError(
            f"unexpected store schema at {path}: expected dict with "
            f"'pilot' key, got {type(store).__name__} with keys "
            f"{list(store.keys()) if isinstance(store, dict) else 'n/a'}"
        )
    episodes = store["pilot"].get("episodes")
    if not isinstance(episodes, list):
        raise ValueError(
            f"unexpected pilot.episodes shape at {path}: expected list, "
            f"got {type(episodes).__name__}"
        )
    out: List[KillVector] = []
    for ep in episodes:
        kv_raw = ep.get("kill_vector") if isinstance(ep, dict) else None
        if kv_raw is None:
            continue
        out.append(KillVector.from_dict(kv_raw))
    return out


# ---------------------------------------------------------------------------
# Bias-corrected pairwise MI
# ---------------------------------------------------------------------------


def _trigger_flags_per_component(
    vectors: Sequence[KillVector],
    component_names: Sequence[str],
) -> Dict[str, List[int]]:
    """Build {component_name -> list of 0/1 trigger flags across corpus}."""
    n = len(vectors)
    flags: Dict[str, List[int]] = {name: [0] * n for name in component_names}
    for i, kv in enumerate(vectors):
        triggered_set = {c.falsifier_name for c in kv.components if c.triggered}
        for name in component_names:
            if name in triggered_set:
                flags[name][i] = 1
    return flags


def _pairwise_mi_from_flags(
    flags: Dict[str, List[int]],
    component_names: Sequence[str],
) -> Dict[Tuple[str, str], Tuple[float, int]]:
    """Compute pairwise MI from a precomputed flags dict.

    Returns
    -------
    dict[(name_a, name_b), (mi_bits, n_both_triggered)]
        Keys sorted (a < b). Only includes pairs where both components
        have non-degenerate marginals (0 < p < 1). The n_both_triggered
        count is included for transparency in the report.
    """
    n = len(next(iter(flags.values()))) if flags else 0
    if n == 0:
        return {}

    # Active = non-constant marginal.
    active: List[str] = []
    for name in component_names:
        s = sum(flags[name])
        if 0 < s < n:
            active.append(name)

    out: Dict[Tuple[str, str], Tuple[float, int]] = {}
    for i in range(len(active)):
        a = active[i]
        for j in range(i + 1, len(active)):
            b = active[j]
            n00 = n01 = n10 = n11 = 0
            fa, fb = flags[a], flags[b]
            for k in range(n):
                if fa[k] == 0 and fb[k] == 0:
                    n00 += 1
                elif fa[k] == 0 and fb[k] == 1:
                    n01 += 1
                elif fa[k] == 1 and fb[k] == 0:
                    n10 += 1
                else:
                    n11 += 1
            # Laplace smoothing, matching KillVector.compute_pairwise_mi.
            total = float(n + 4)
            p00 = (n00 + 1) / total
            p01 = (n01 + 1) / total
            p10 = (n10 + 1) / total
            p11 = (n11 + 1) / total
            pa1 = p10 + p11
            pa0 = p00 + p01
            pb1 = p01 + p11
            pb0 = p00 + p10
            mi = 0.0
            for pjoint, pma, pmb in (
                (p00, pa0, pb0),
                (p01, pa0, pb1),
                (p10, pa1, pb0),
                (p11, pa1, pb1),
            ):
                denom = pma * pmb
                if denom > 0 and pjoint > 0:
                    mi += pjoint * math.log2(pjoint / denom)
            if mi < 0.0 and mi > -1e-12:
                mi = 0.0
            key = (a, b) if a < b else (b, a)
            out[key] = (float(mi), n11)
    return out


def _null_pairwise_mi(
    flags: Dict[str, List[int]],
    component_names: Sequence[str],
    n_shuffles: int,
    rng: random.Random,
) -> Dict[Tuple[str, str], Tuple[float, float]]:
    """Compute null pairwise MI by independently shuffling each component's
    flag vector. Preserves each component's marginal P(triggered) but
    destroys joint dependence. Per ``feedback_mi_bias``.

    Returns
    -------
    dict[(name_a, name_b), (mean_mi, std_mi)]
    """
    if not flags:
        return {}
    accumulators: Dict[Tuple[str, str], List[float]] = {}
    n = len(next(iter(flags.values())))
    for _ in range(n_shuffles):
        # Independent per-component shuffle.
        shuffled = {name: list(vec) for name, vec in flags.items()}
        for name in component_names:
            rng.shuffle(shuffled[name])
        mi_dict = _pairwise_mi_from_flags(shuffled, component_names)
        for key, (mi, _n11) in mi_dict.items():
            accumulators.setdefault(key, []).append(mi)
    out: Dict[Tuple[str, str], Tuple[float, float]] = {}
    for key, vals in accumulators.items():
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        out[key] = (float(mean), float(math.sqrt(var)))
    return out


# ---------------------------------------------------------------------------
# Top-level audit
# ---------------------------------------------------------------------------


def run_audit(
    vectors: Sequence[KillVector],
    *,
    component_names: Sequence[str] = ALL_COMPONENT_NAMES,
    threshold_bits: float = DEFAULT_FLAG_THRESHOLD_BITS,
    n_null_shuffles: int = DEFAULT_N_NULL_SHUFFLES,
    seed: int = 42,
) -> AuditResult:
    """Compute the bias-corrected pairwise-MI audit over ``vectors``.

    Parameters
    ----------
    vectors : Sequence[KillVector]
        Per-claim kill records. Empty input returns an AuditResult with
        ``n_records=0`` and empty pair_results.
    component_names : Sequence[str]
        Components to audit. Default: all 20 from ALL_COMPONENT_NAMES.
    threshold_bits : float
        Bias-corrected MI threshold for flagging.
    n_null_shuffles : int
        Number of random-pairing shuffles for null MI estimation.
    seed : int
        RNG seed for the null shuffles (cross-machine determinism).
    """
    t0 = time.time()
    if not vectors:
        return AuditResult(
            n_records=0,
            n_active_components=0,
            threshold_bits=threshold_bits,
            n_null_shuffles=n_null_shuffles,
            pair_results=(),
            top_10=(),
            flagged=(),
            elapsed_s=time.time() - t0,
        )

    flags = _trigger_flags_per_component(vectors, component_names)
    n = len(vectors)

    observed = _pairwise_mi_from_flags(flags, component_names)
    null = _null_pairwise_mi(
        flags, component_names, n_null_shuffles, random.Random(seed)
    )

    triggered_counts: Dict[str, int] = {
        name: sum(flags[name]) for name in component_names
    }

    rows: List[PairMI] = []
    for key, (obs_mi, n11) in observed.items():
        a, b = key
        null_mean, null_std = null.get(key, (0.0, 0.0))
        corrected = obs_mi - null_mean
        flagged = corrected > threshold_bits
        rows.append(
            PairMI(
                component_a=a,
                component_b=b,
                observed_mi_bits=obs_mi,
                null_mi_mean_bits=null_mean,
                null_mi_std_bits=null_std,
                bias_corrected_mi_bits=corrected,
                n_a_triggered=triggered_counts[a],
                n_b_triggered=triggered_counts[b],
                n_both_triggered=n11,
                flagged=flagged,
            )
        )

    # Sort descending by bias-corrected MI.
    rows.sort(key=lambda r: r.bias_corrected_mi_bits, reverse=True)
    top_10 = tuple(rows[:10])
    flagged = tuple(r for r in rows if r.flagged)

    n_active = sum(1 for name in component_names if 0 < triggered_counts[name] < n)

    return AuditResult(
        n_records=n,
        n_active_components=n_active,
        threshold_bits=threshold_bits,
        n_null_shuffles=n_null_shuffles,
        pair_results=tuple(rows),
        top_10=top_10,
        flagged=flagged,
        elapsed_s=time.time() - t0,
    )


# ---------------------------------------------------------------------------
# Markdown report rendering
# ---------------------------------------------------------------------------


def render_report(
    result: AuditResult,
    *,
    store_path: Optional[Path] = None,
) -> str:
    """Render the audit result as a markdown report string."""
    lines: List[str] = []
    lines.append("# TriangulationProtocol Independence Audit Results")
    lines.append("")
    lines.append(
        f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}_"
    )
    lines.append(
        f"_Per inbox ticket T-2026-05-07-T009 "
        f"(prometheus_math/triangulation_independence_audit.py)_"
    )
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append(
        "Per `feedback_mi_bias`: MI on sparse histograms is biased upward. "
        "The audit corrects observed pairwise MI between falsifier-triggered "
        "flags by subtracting the mean MI of a random-pairing null "
        "(per-component flag vectors are independently shuffled to destroy "
        "joint dependence while preserving each component's marginal). "
        "Bias-corrected MI > threshold is flagged as a "
        "triangulation-violation candidate."
    )
    lines.append("")
    lines.append("## Run Parameters")
    lines.append("")
    if store_path is not None:
        lines.append(f"- **Kill-record store:** `{store_path}`")
    lines.append(f"- **Records audited:** {result.n_records}")
    lines.append(f"- **Active components (non-constant marginal):** {result.n_active_components}")
    lines.append(f"- **Bias-correction null shuffles:** {result.n_null_shuffles}")
    lines.append(f"- **Flagging threshold (bits):** {result.threshold_bits:.3f}")
    lines.append(f"- **Elapsed seconds:** {result.elapsed_s:.2f}")
    lines.append("")

    if not result.pair_results:
        lines.append("## Result: No Active Pairs")
        lines.append("")
        if result.n_records == 0:
            lines.append(
                "The store contained zero kill records. Audit cannot "
                "proceed without input data."
            )
        elif result.n_active_components <= 1:
            lines.append(
                f"**Substrate finding (data-shape gap):** {result.n_records} "
                f"kill records loaded, but only {result.n_active_components} "
                "component(s) have a non-constant trigger marginal. "
                "TriangulationProtocol's independence assumption cannot be "
                "empirically tested on this corpus because the records are "
                "**first-fail-only-coded** (each kill_vector captures only "
                "the single falsifier that fired first; all other "
                "components have always-0 marginals)."
            )
            lines.append("")
            lines.append(
                "To unblock empirical independence verification, the "
                "kill-record pipeline must be extended to capture **joint** "
                "falsifier outcomes per claim — i.e. each candidate is "
                "evaluated against ALL falsifiers (not short-circuited at "
                "first kill) so the joint distribution is observable. "
                "Until then, this audit reports only the data-shape gap, "
                "not an independence verdict."
            )
        else:
            lines.append(
                f"{result.n_records} records, {result.n_active_components} "
                "active components, but no component pairs survived the "
                "marginal-non-degenerate filter (each pair must have "
                "0 < p(triggered) < 1 for both components)."
            )
        lines.append("")
        return "\n".join(lines)

    lines.append("## Top-10 Highest Bias-Corrected MI")
    lines.append("")
    lines.append(
        "| # | Component A | Component B | Observed MI (bits) | "
        "Null mean (bits) | Null std (bits) | Corrected (bits) | "
        "n(A) | n(B) | n(A&B) | Flag |"
    )
    lines.append(
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"
    )
    for i, row in enumerate(result.top_10, start=1):
        flag_marker = "FLAG" if row.flagged else ""
        lines.append(
            f"| {i} | `{row.component_a}` | `{row.component_b}` | "
            f"{row.observed_mi_bits:.4f} | {row.null_mi_mean_bits:.4f} | "
            f"{row.null_mi_std_bits:.4f} | "
            f"{row.bias_corrected_mi_bits:.4f} | "
            f"{row.n_a_triggered} | {row.n_b_triggered} | "
            f"{row.n_both_triggered} | {flag_marker} |"
        )
    lines.append("")

    lines.append("## Flagged Pairs (Bias-Corrected MI > Threshold)")
    lines.append("")
    if not result.flagged:
        lines.append(
            f"No component pairs exceeded the {result.threshold_bits:.3f}-bit "
            "threshold after bias correction. The TriangulationProtocol's "
            "independence assumption is consistent with the observed corpus."
        )
    else:
        lines.append(
            f"**{len(result.flagged)} pair(s) exceed the "
            f"{result.threshold_bits:.3f}-bit bias-corrected threshold.** "
            "These are triangulation-violation candidates worth Aporia "
            "review — the substrate's independence ASSERTION between "
            "these falsifier outcomes is not borne out empirically."
        )
        lines.append("")
        for row in result.flagged:
            lines.append(
                f"- `{row.component_a}` <-> `{row.component_b}`: "
                f"corrected MI = {row.bias_corrected_mi_bits:.4f} bits "
                f"(observed {row.observed_mi_bits:.4f}, "
                f"null mean {row.null_mi_mean_bits:.4f}). "
                f"n(A&B) = {row.n_both_triggered}."
            )
    lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "1. **First-fail-only coding.** If the corpus records only the "
        "first-failing falsifier per claim (legacy `kill_pattern`-style "
        "store), components are mutually exclusive by construction; the "
        "MI estimator will detect strong negative coupling that is a "
        "data-shape artifact, not a substrate finding. Inspect "
        "`n(A&B)` — if it's near 0 across all pairs, this caveat applies."
    )
    lines.append(
        "2. **Sparse-marginal sensitivity.** Components with very low "
        "trigger marginals (n(A) < 30) have wide MI confidence intervals; "
        "the null std column documents the uncertainty floor."
    )
    lines.append(
        "3. **Bias-correction assumes IID shuffles.** The null preserves "
        "each component's marginal but destroys joint structure. If the "
        "corpus has temporal or operator-class clustering, the null may "
        "under-represent baseline coincidence; consider running the audit "
        "stratified by operator_class."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m prometheus_math.triangulation_independence_audit",
        description=(
            "Empirical pairwise-MI audit of TriangulationProtocol's "
            "independence assumption (T-2026-05-07-T009)."
        ),
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_KILL_STORE,
        help=f"Path to kill-record store JSON. Default: {DEFAULT_KILL_STORE.name}",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_FLAG_THRESHOLD_BITS,
        help=(
            f"Bias-corrected MI threshold (bits) for flagging. "
            f"Default: {DEFAULT_FLAG_THRESHOLD_BITS}."
        ),
    )
    parser.add_argument(
        "--n-null",
        type=int,
        default=DEFAULT_N_NULL_SHUFFLES,
        help=(
            f"Number of random-pairing null shuffles. "
            f"Default: {DEFAULT_N_NULL_SHUFFLES}."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for null shuffles (default 42).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown report output path. Default: {DEFAULT_REPORT_PATH.name}",
    )
    args = parser.parse_args(argv)

    print(f"[audit] loading {args.store}")
    vectors = load_kill_vectors_from_pilot_store(args.store)
    print(f"[audit] loaded {len(vectors)} kill vectors")

    print(f"[audit] running audit (threshold={args.threshold} bits, "
          f"n_null={args.n_null}, seed={args.seed})")
    result = run_audit(
        vectors,
        threshold_bits=args.threshold,
        n_null_shuffles=args.n_null,
        seed=args.seed,
    )

    print(f"[audit] active pairs: {len(result.pair_results)}, "
          f"flagged: {len(result.flagged)}")
    print(f"[audit] elapsed: {result.elapsed_s:.2f}s")

    report_md = render_report(result, store_path=args.store)
    args.out.write_text(report_md, encoding="utf-8")
    print(f"[audit] report written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "PairMI",
    "AuditResult",
    "DEFAULT_KILL_STORE",
    "DEFAULT_FLAG_THRESHOLD_BITS",
    "DEFAULT_N_NULL_SHUFFLES",
    "DEFAULT_REPORT_PATH",
    "load_kill_vectors_from_pilot_store",
    "run_audit",
    "render_report",
    "main",
]
