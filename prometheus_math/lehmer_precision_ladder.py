"""Lehmer precision ladder — empirical convergence-vs-dps curve.

Mission
-------
Path A demonstrated that the 17 ``verification_failed=True`` brute-force
band entries all converge at dps=60 once we *factor before
root-finding*. The natural follow-up question is empirical, not
philosophical:

    At what mpmath precision does each entry first converge?

This driver builds the full precision-→-classification curve for
``dps ∈ {30, 40, 50, 60, 80, 100}`` × ``strategy ∈ {direct, factor_first}``
on those same 17 entries. The output is the artifact: a
strategy-stratified convergence rate as a function of precision, plus a
per-entry ``min_dps_converged`` distribution. The headline is the
precision at which the curve flattens to 17/17.

Honest framing
--------------
* The curve is ONE specific ladder (six points). Broader ladders
  (dps ∈ {200, 500, 1000} or ``maxsteps`` sweeps) might reveal further
  structure but are out of scope here.
* "Direct" uses ``mpmath.polyroots`` on the unfactored deg-14
  polynomial with ``maxsteps=200`` — fixed, NOT escalated. Path A's
  background experiments showed the unfactored polynomial does not
  converge at any reasonable maxsteps; this driver records that as a
  data point rather than working around it.
* "Factor-first" mirrors Path A's strategy: ``sympy.factor_list`` then
  ``Poly.nroots(n=dps)`` per irreducible factor. Mahler's
  multiplicativity composes factor measures into the full M.
* Classification reuses Path A's buckets so the curve is directly
  comparable to the Path A summary.

Precision regimes (per-entry verdict)
-------------------------------------
* ``PRECISION_REGIME_LOW``      — converges directly at dps=30.
* ``PRECISION_REGIME_MID``      — converges direct at dps ∈ {40, 50}.
* ``PRECISION_REGIME_HIGH``     — converges direct only at dps ≥ 60.
* ``PRECISION_REGIME_FACTOR_FIRST_ONLY`` — factor-first converges at
  some dps in the ladder, but direct never does (across the ladder).
* ``PRECISION_REGIME_DIVERGENT`` — both strategies fail at every dps.

Outputs
-------
``prometheus_math/_lehmer_precision_ladder_results.json``
    Full per-(entry, dps, strategy) results + per-entry regime.
``prometheus_math/LEHMER_PRECISION_LADDER_RESULTS.md``
    Companion narrative.

Forged: 2026-05-04 by Techne (toolsmith), follow-up to lehmer_path_a.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Optional, Sequence

# Import sympy / mpmath lazily inside functions; both are heavy and not
# every entry point needs them (the loaders / dataclasses don't).


__all__ = [
    "DEFAULT_DPS_LADDER",
    "DEFAULT_DIRECT_MAXSTEPS",
    "PRECISION_REGIME_LOW",
    "PRECISION_REGIME_MID",
    "PRECISION_REGIME_HIGH",
    "PRECISION_REGIME_FACTOR_FIRST_ONLY",
    "PRECISION_REGIME_DIVERGENT",
    "compute_M_direct",
    "compute_M_factor_first",
    "classify_precision_regime",
    "evaluate_entry_on_ladder",
    "aggregate_convergence_curve",
    "run_precision_ladder",
]


# Default ladder requested by the spec. Six points cover the
# interesting band: dps=30 (where the brute-force originally failed),
# 40/50 (the boundary layer), 60 (where Path A succeeded), 80/100
# (well past Path A's empirical boundary; a sanity tail).
DEFAULT_DPS_LADDER: tuple[int, ...] = (30, 40, 50, 60, 80, 100)

# maxsteps for the direct ``mpmath.polyroots`` strategy. Held constant
# across the ladder so the curve isolates the precision axis. Path A's
# background experiments (dps up to 400, maxsteps up to 4000) showed
# the unfactored polynomial does not converge regardless; this is the
# precision-only sweep.
DEFAULT_DIRECT_MAXSTEPS: int = 200


PRECISION_REGIME_LOW = "PRECISION_REGIME_LOW"
PRECISION_REGIME_MID = "PRECISION_REGIME_MID"
PRECISION_REGIME_HIGH = "PRECISION_REGIME_HIGH"
PRECISION_REGIME_FACTOR_FIRST_ONLY = "PRECISION_REGIME_FACTOR_FIRST_ONLY"
PRECISION_REGIME_DIVERGENT = "PRECISION_REGIME_DIVERGENT"


# ---------------------------------------------------------------------------
# Single-strategy compute kernels
# ---------------------------------------------------------------------------

def compute_M_direct(
    coeffs_ascending: Sequence[int],
    dps: int,
    maxsteps: int = DEFAULT_DIRECT_MAXSTEPS,
) -> dict:
    """Direct mpmath.polyroots strategy at a fixed dps.

    Parameters
    ----------
    coeffs_ascending : sequence of int
    dps : int
        mpmath decimal precision.
    maxsteps : int, default 200
        Durand-Kerner iteration cap (held constant; we are sweeping
        precision only).

    Returns
    -------
    dict with keys ``M``, ``status``, ``wall_time_ms``, ``error``,
    ``strategy``, ``dps``, ``converged`` (bool).
    """
    import mpmath as mp

    desc = list(reversed(list(coeffs_ascending)))
    while len(desc) > 1 and desc[0] == 0:
        desc = desc[1:]

    t0 = time.perf_counter()

    if len(desc) <= 1:
        return {
            "strategy": "direct",
            "dps": int(dps),
            "M": float("nan"),
            "status": "degenerate",
            "wall_time_ms": (time.perf_counter() - t0) * 1000.0,
            "error": "polynomial degree < 1",
            "converged": False,
        }

    leading = abs(mp.mpf(desc[0]))
    try:
        # Save and restore mp.dps so the global state isn't poisoned for
        # adjacent calls.
        old_dps = mp.mp.dps
        mp.mp.dps = int(dps)
        try:
            roots = mp.polyroots(
                [mp.mpf(c) for c in desc],
                maxsteps=int(maxsteps),
            )
        finally:
            mp.mp.dps = old_dps
        M = leading
        for r in roots:
            a = abs(r)
            if a > 1:
                M = M * a
        try:
            M_value = float(M)
        except Exception:
            M_value = float("nan")
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if math.isfinite(M_value):
            return {
                "strategy": "direct",
                "dps": int(dps),
                "M": M_value,
                "status": "ok",
                "wall_time_ms": elapsed_ms,
                "error": None,
                "converged": True,
            }
        return {
            "strategy": "direct",
            "dps": int(dps),
            "M": float("nan"),
            "status": "non_finite",
            "wall_time_ms": elapsed_ms,
            "error": "polyroots returned non-finite roots",
            "converged": False,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "strategy": "direct",
            "dps": int(dps),
            "M": float("nan"),
            "status": "no_convergence",
            "wall_time_ms": elapsed_ms,
            "error": f"{type(exc).__name__}: {exc!s}"[:200],
            "converged": False,
        }


def compute_M_factor_first(
    coeffs_ascending: Sequence[int],
    dps: int,
) -> dict:
    """Factor-first strategy: factor over Z, root-find each piece.

    Mirrors ``prometheus_math.lehmer_path_a.high_precision_M_via_factor``
    but exposes a uniform schema with the ``compute_M_direct`` sibling.

    Returns
    -------
    dict with keys ``M``, ``status``, ``wall_time_ms``, ``error``,
    ``strategy``, ``dps``, ``converged`` (bool).
    """
    from prometheus_math.lehmer_path_a import high_precision_M_via_factor

    t0 = time.perf_counter()
    try:
        res = high_precision_M_via_factor(
            coeffs_ascending, nroots_precision=int(dps)
        )
    except Exception as exc:
        return {
            "strategy": "factor_first",
            "dps": int(dps),
            "M": float("nan"),
            "status": "factor_first_exception",
            "wall_time_ms": (time.perf_counter() - t0) * 1000.0,
            "error": f"{type(exc).__name__}: {exc!s}"[:200],
            "converged": False,
        }
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    M_value = float(res.get("M", float("nan")))
    converged = res.get("status") == "ok" and math.isfinite(M_value)
    return {
        "strategy": "factor_first",
        "dps": int(dps),
        "M": M_value if math.isfinite(M_value) else float("nan"),
        "status": str(res.get("status", "unknown")),
        "wall_time_ms": elapsed_ms,
        "error": res.get("error"),
        "converged": bool(converged),
    }


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def _path_a_classify(M: float) -> str:
    """Wrap Path A's classifier to keep the precision-ladder JSON
    self-contained and stable to internal Path A constant edits."""
    from prometheus_math.lehmer_path_a import classify_path_a

    return classify_path_a(M)


def _classification_label(path_a_bucket: str) -> str:
    """Map Path A buckets onto the spec's named labels."""
    return {
        "A1": "cyclotomic_only",
        "A2": "cyclotomic_times_small_salem",
        "A3": "confirmed_in_band",
        "A4": "still_failed",
    }.get(path_a_bucket, "still_failed")


def classify_precision_regime(
    direct_min_dps: Optional[int],
    factor_first_min_dps: Optional[int],
    ladder: Sequence[int] = DEFAULT_DPS_LADDER,
) -> str:
    """Map (direct_min_dps, factor_first_min_dps) into a regime label.

    See module docstring for the regime definitions.
    """
    if (direct_min_dps is None) and (factor_first_min_dps is None):
        return PRECISION_REGIME_DIVERGENT
    if direct_min_dps is None and factor_first_min_dps is not None:
        return PRECISION_REGIME_FACTOR_FIRST_ONLY
    # direct converges somewhere on the ladder.
    assert direct_min_dps is not None
    if direct_min_dps <= 30:
        return PRECISION_REGIME_LOW
    if direct_min_dps in (40, 50):
        return PRECISION_REGIME_MID
    return PRECISION_REGIME_HIGH


# ---------------------------------------------------------------------------
# Per-entry pipeline
# ---------------------------------------------------------------------------

def evaluate_entry_on_ladder(
    entry: dict,
    dps_ladder: Sequence[int] = DEFAULT_DPS_LADDER,
    direct_maxsteps: int = DEFAULT_DIRECT_MAXSTEPS,
) -> dict:
    """Evaluate a single brute-force entry at every (dps, strategy).

    Returns a dict with the full per-(dps, strategy) measurement table
    plus aggregate per-entry summaries (min_dps_converged_per_strategy,
    classification_at_convergence, regime).
    """
    coeffs_asc = list(entry.get("coeffs_ascending", []))
    if not coeffs_asc:
        # Allow loading from half_coeffs as a defensive fallback.
        from prometheus_math.lehmer_path_a import build_palindrome_descending

        half = entry.get("half_coeffs")
        if half:
            coeffs_asc = list(reversed(build_palindrome_descending(half)))

    measurements: list[dict] = []
    direct_min_dps: Optional[int] = None
    factor_first_min_dps: Optional[int] = None
    M_at_factor_first_convergence: Optional[float] = None
    M_at_direct_convergence: Optional[float] = None

    for dps in dps_ladder:
        # Direct
        d = compute_M_direct(coeffs_asc, dps=dps, maxsteps=direct_maxsteps)
        if d["converged"]:
            if direct_min_dps is None:
                direct_min_dps = int(dps)
                M_at_direct_convergence = float(d["M"])
        d_record = {
            "dps": int(dps),
            "strategy": "direct",
            "M_value": (float(d["M"]) if math.isfinite(d["M"]) else None),
            "status": d["status"],
            "wall_time_ms": float(d["wall_time_ms"]),
            "converged": bool(d["converged"]),
            "error": d["error"],
        }
        measurements.append(d_record)

        # Factor-first
        f = compute_M_factor_first(coeffs_asc, dps=dps)
        if f["converged"]:
            if factor_first_min_dps is None:
                factor_first_min_dps = int(dps)
                M_at_factor_first_convergence = float(f["M"])
        f_record = {
            "dps": int(dps),
            "strategy": "factor_first",
            "M_value": (float(f["M"]) if math.isfinite(f["M"]) else None),
            "status": f["status"],
            "wall_time_ms": float(f["wall_time_ms"]),
            "converged": bool(f["converged"]),
            "error": f["error"],
        }
        measurements.append(f_record)

    # Classification reuses Path A's buckets, anchored to the
    # factor-first M at first convergence (the most reliable reading).
    classification_anchor = (
        M_at_factor_first_convergence
        if M_at_factor_first_convergence is not None
        else (M_at_direct_convergence if M_at_direct_convergence is not None
              else float("nan"))
    )
    path_a_bucket = _path_a_classify(classification_anchor)
    classification = _classification_label(path_a_bucket)

    regime = classify_precision_regime(
        direct_min_dps=direct_min_dps,
        factor_first_min_dps=factor_first_min_dps,
        ladder=dps_ladder,
    )

    return {
        "half_coeffs": list(entry.get("half_coeffs", [])),
        "coeffs_ascending": coeffs_asc,
        "M_numpy": float(entry.get("M_numpy", float("nan"))),
        "M_mpmath_original": float(entry.get("M_mpmath", float("nan"))),
        "measurements": measurements,
        "direct_min_dps_converged": direct_min_dps,
        "factor_first_min_dps_converged": factor_first_min_dps,
        "M_at_factor_first_convergence": M_at_factor_first_convergence,
        "M_at_direct_convergence": M_at_direct_convergence,
        "classification": classification,
        "path_a_bucket": path_a_bucket,
        "regime": regime,
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_convergence_curve(
    per_entry: Sequence[dict],
    dps_ladder: Sequence[int] = DEFAULT_DPS_LADDER,
) -> dict:
    """Compute the (dps, strategy)-stratified convergence rate.

    Returns
    -------
    dict::

        {
          "n_entries": <int>,
          "ladder": [...],
          "by_strategy": {
            "direct": {
                "convergence_count_by_dps": {30: <int>, 40: ...},
                "convergence_rate_by_dps": {30: <float>, ...},
            },
            "factor_first": {... same shape ...},
          },
          "min_dps_distribution": {
            "direct": {"30": <int>, ..., "never": <int>},
            "factor_first": {"30": <int>, ..., "never": <int>},
          },
          "regime_counts": {<regime>: <int>, ...},
          "classification_counts": {<label>: <int>, ...},
          "headline_dps_full_factor_first": <int|None>,
          "headline_dps_full_direct": <int|None>,
        }

    ``headline_dps_full_*`` is the smallest dps at which the strategy
    achieves N/N convergence, or ``None`` if the curve never flattens
    to full coverage on this ladder.
    """
    n = len(per_entry)
    ladder_sorted = sorted(set(int(d) for d in dps_ladder))
    by_strategy: dict[str, dict] = {}
    for strategy in ("direct", "factor_first"):
        count_by = {int(d): 0 for d in ladder_sorted}
        for r in per_entry:
            for m in r.get("measurements", []):
                if (
                    m.get("strategy") == strategy
                    and bool(m.get("converged"))
                    and int(m["dps"]) in count_by
                ):
                    count_by[int(m["dps"])] += 1
        rate_by = {
            int(d): (count_by[int(d)] / n if n > 0 else 0.0)
            for d in ladder_sorted
        }
        by_strategy[strategy] = {
            "convergence_count_by_dps": count_by,
            "convergence_rate_by_dps": rate_by,
        }

    # min_dps distribution per strategy.
    min_dps_dist: dict[str, dict] = {}
    for strategy, key in (("direct", "direct_min_dps_converged"),
                          ("factor_first", "factor_first_min_dps_converged")):
        bucket: dict[str, int] = {str(int(d)): 0 for d in ladder_sorted}
        bucket["never"] = 0
        for r in per_entry:
            v = r.get(key)
            if v is None:
                bucket["never"] += 1
            else:
                bucket[str(int(v))] = bucket.get(str(int(v)), 0) + 1
        min_dps_dist[strategy] = bucket

    regime_counts: dict[str, int] = {
        PRECISION_REGIME_LOW: 0,
        PRECISION_REGIME_MID: 0,
        PRECISION_REGIME_HIGH: 0,
        PRECISION_REGIME_FACTOR_FIRST_ONLY: 0,
        PRECISION_REGIME_DIVERGENT: 0,
    }
    for r in per_entry:
        regime = r.get("regime", PRECISION_REGIME_DIVERGENT)
        regime_counts[regime] = regime_counts.get(regime, 0) + 1

    class_counts: dict[str, int] = {}
    for r in per_entry:
        label = r.get("classification", "still_failed")
        class_counts[label] = class_counts.get(label, 0) + 1

    # Headlines: smallest dps at which strategy converges on ALL entries.
    def _headline_full(strategy: str) -> Optional[int]:
        counts = by_strategy[strategy]["convergence_count_by_dps"]
        for d in ladder_sorted:
            if counts.get(int(d), 0) >= n and n > 0:
                return int(d)
        return None

    return {
        "n_entries": n,
        "ladder": ladder_sorted,
        "by_strategy": by_strategy,
        "min_dps_distribution": min_dps_dist,
        "regime_counts": regime_counts,
        "classification_counts": class_counts,
        "headline_dps_full_direct": _headline_full("direct"),
        "headline_dps_full_factor_first": _headline_full("factor_first"),
    }


# ---------------------------------------------------------------------------
# Top-level pipeline
# ---------------------------------------------------------------------------

def run_precision_ladder(
    brute_force_results_path: str | Path = (
        Path(__file__).parent / "_lehmer_brute_force_results.json"
    ),
    output_path: Optional[str | Path] = None,
    dps_ladder: Sequence[int] = DEFAULT_DPS_LADDER,
    direct_maxsteps: int = DEFAULT_DIRECT_MAXSTEPS,
    progress: bool = False,
) -> dict:
    """Top-level driver: load entries, evaluate ladder, aggregate, write JSON.

    Parameters
    ----------
    brute_force_results_path : path
        Path to the brute-force results JSON (READ-ONLY).
    output_path : path, optional
        Where to write the precision-ladder results JSON. None = no file.
    dps_ladder : sequence of int, default DEFAULT_DPS_LADDER
        Precision points to sweep.
    direct_maxsteps : int, default 200
        maxsteps for the direct strategy (held constant).
    progress : bool, default False
        Print per-entry progress to stdout.

    Returns
    -------
    dict — full results document (also written to ``output_path``).
    """
    from prometheus_math.lehmer_path_a import load_unverified_entries

    t_start = time.perf_counter()
    entries = load_unverified_entries(brute_force_results_path)
    n_total = len(entries)
    if progress:
        print(f"[precision_ladder] loaded {n_total} unverified entries")

    per_entry_results: list[dict] = []
    for i, entry in enumerate(entries):
        if progress:
            print(
                f"[precision_ladder] {i+1}/{n_total} half="
                f"{entry.get('half_coeffs')}"
            )
        result = evaluate_entry_on_ladder(
            entry,
            dps_ladder=dps_ladder,
            direct_maxsteps=direct_maxsteps,
        )
        if progress:
            print(
                f"  -> regime={result['regime']} "
                f"class={result['classification']} "
                f"direct_min={result['direct_min_dps_converged']} "
                f"factor_first_min={result['factor_first_min_dps_converged']}"
            )
        per_entry_results.append(result)

    aggregate = aggregate_convergence_curve(
        per_entry_results, dps_ladder=dps_ladder
    )

    wall_time_seconds = time.perf_counter() - t_start

    document = {
        "subspace": "deg14_palindromic_coeffs_pm5_c0_positive",
        "source_brute_force_results": str(brute_force_results_path),
        "dps_ladder": list(dps_ladder),
        "direct_maxsteps": int(direct_maxsteps),
        "n_entries": n_total,
        "aggregate": aggregate,
        "per_entry_results": per_entry_results,
        "wall_time_seconds": float(wall_time_seconds),
    }

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(document, fh, indent=2, default=_json_safe)

    return document


def _json_safe(o):
    """Coerce sympy / mpmath types to plain Python for JSON dump."""
    try:
        return float(o)
    except Exception:
        return str(o)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    default_brute = str(
        Path(__file__).parent / "_lehmer_brute_force_results.json"
    )
    default_out = str(
        Path(__file__).parent / "_lehmer_precision_ladder_results.json"
    )
    parser = argparse.ArgumentParser(
        description=(
            "Lehmer precision ladder: empirical convergence-vs-dps curve "
            "for the 17 verification_failed brute-force band entries."
        ),
    )
    parser.add_argument("--input", type=str, default=default_brute)
    parser.add_argument("--output", type=str, default=default_out)
    parser.add_argument(
        "--ladder",
        type=str,
        default=",".join(str(d) for d in DEFAULT_DPS_LADDER),
        help="Comma-separated dps ladder.",
    )
    parser.add_argument(
        "--direct-maxsteps",
        type=int,
        default=DEFAULT_DIRECT_MAXSTEPS,
        help="maxsteps for the direct mpmath.polyroots strategy.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    ladder = tuple(int(x) for x in args.ladder.split(","))
    res = run_precision_ladder(
        brute_force_results_path=args.input,
        output_path=args.output,
        dps_ladder=ladder,
        direct_maxsteps=args.direct_maxsteps,
        progress=not args.quiet,
    )

    print()
    print("=" * 64)
    print(f"Entries: {res['n_entries']}")
    print(f"Ladder:  {res['dps_ladder']}")
    print(f"Regime counts: {res['aggregate']['regime_counts']}")
    print(f"Classification counts: {res['aggregate']['classification_counts']}")
    print(
        "Direct convergence rate by dps: "
        f"{res['aggregate']['by_strategy']['direct']['convergence_count_by_dps']}"
    )
    print(
        "Factor-first convergence rate by dps: "
        f"{res['aggregate']['by_strategy']['factor_first']['convergence_count_by_dps']}"
    )
    print(
        f"Headline dps where direct hits N/N: "
        f"{res['aggregate']['headline_dps_full_direct']}"
    )
    print(
        f"Headline dps where factor_first hits N/N: "
        f"{res['aggregate']['headline_dps_full_factor_first']}"
    )
    print(f"Wall time: {res['wall_time_seconds']:.1f}s")
    print(f"Output: {args.output}")
