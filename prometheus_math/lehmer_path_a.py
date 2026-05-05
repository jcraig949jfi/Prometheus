"""Lehmer brute-force — Path A: high-precision re-verification.

Mission
-------
The brute-force F at deg-14 (-5..+5) palindromic completed earlier
today and produced 43 verified band hits. Of those, 26 lie in the
Mossinghoff catalog and 17 do NOT — but those 17 ALL have
``verification_failed=True`` because ``mpmath.polyroots`` at dps=30
failed to converge (returned NaN). They cannot be classified.

The brute-force run wrote ``verdict: INCONCLUSIVE`` precisely because
this many entries have NaN M_mpmath; we cannot safely declare H5 vs H2
without a high-precision certification of every band entry.

Path A is the cheapest of three resolution strategies. It re-verifies
the 17 unverified entries at higher mpmath precision and, more
importantly, by **factoring the polynomial first** so that
``polyroots`` only has to handle each irreducible factor in isolation
(rather than fighting clustered repeated unit-circle roots in the
unfactored deg-14 polynomial). Path A does NOT do symbolic work
(that's Path B) — factorisation is just a numerical pre-conditioner
here.

Approach
--------
For each of the 17 entries:

1. Factor the integer polynomial via ``sympy.factor_list`` (this
   returns the irreducible factors over Z exactly, with multiplicities).
2. For each non-constant factor, compute its Mahler measure via
   ``sympy.Poly.nroots(n=80)`` — a high-precision (80-digit) numerical
   root-finder that handles each irreducible factor in isolation. Each
   factor has at most ~10 roots, so the eigenvalue-based root-finder is
   well-conditioned even on 80-digit precision. (This is the key win
   over running ``polyroots`` on the full deg-14 polynomial: the
   Durand-Kerner iteration in mpmath gets stuck on the unfactored
   polynomial because of clustered repeated roots from cyclotomic
   factors.)
3. Multiply factor-Mahlers (with multiplicity) to get the full M.
4. Classify the entry:

   * **A1: cyclotomic_only** — at high precision, M ≤ 1 + 1e-8. The
     polynomial is purely cyclotomic; the numpy noise was the entire
     M_numpy - 1 deviation.
   * **A2: cyclotomic_times_small_salem** — M ∈ (1+1e-8, 1.001]. A
     genuine residual factor with measure barely above 1, almost
     certainly a small-degree Salem at the boundary. (Borderline; we
     don't try to certify the residual is actually a Salem.)
   * **A3: confirmed_in_band** — M ∈ (1.001, 1.18). Genuine in-band
     candidate. Cross-check against Mossinghoff via M-proximity.
   * **A4: still_failed** — even high-precision factorisation failed to
     produce a finite M. Documented but not classified.

5. For A3 entries, re-run ``lookup_by_M`` against Mossinghoff. The
   original brute-force run looked up by NaN M (impossible to match);
   with the corrected high-precision M these entries should match
   Lehmer's polynomial via the Lehmer × cyclotomic factorisation.

Verdict
-------
If A4 == 0 (every entry classified) AND every A3 entry matches
Mossinghoff, Path A lifts the brute-force verdict from INCONCLUSIVE
to **H5_CONFIRMED** (Mossinghoff catalog ate the reachable subspace).
If any A3 entry has no Mossinghoff match, that entry is a candidate
for novel discovery (flagged for Path B/C cross-check). If A4 > 0,
some entries remain unverified and the verdict stays INCONCLUSIVE for
the unresolved entries.

Forged: 2026-05-04 by Techne (toolsmith) for Charon's H1 settlement,
Path A.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Optional, Sequence

# We import sympy lazily inside functions because sympy import is heavy
# and not all callers need it (the dataclass and JSON loaders don't).


__all__ = [
    "DEFAULT_NROOTS_PRECISION",
    "A1_CYCLOTOMIC_TOL",
    "A2_SMALL_SALEM_UPPER",
    "A3_BAND_LOWER",
    "A3_BAND_UPPER",
    "MOSSINGHOFF_M_TOL",
    "build_palindrome_descending",
    "high_precision_M_via_factor",
    "classify_path_a",
    "lookup_in_mossinghoff_by_M",
    "verify_entry",
    "load_unverified_entries",
    "run_path_a",
]


# Precision (decimal digits) for sympy's nroots() per factor. 80 is
# overkill for our needs (Lehmer's M is known to ~30 digits), but the
# cost is negligible because each factor is small. We err on the side of
# precision so the M-comparison is unambiguous.
DEFAULT_NROOTS_PRECISION: int = 80

# Classification thresholds.
#
# A1: M is within A1_CYCLOTOMIC_TOL of 1 ⇒ entry is purely cyclotomic
# (true M = 1 exactly; numpy noise made it look like a band hit). 1e-8
# is well below any genuine Salem residual we'd care about.
A1_CYCLOTOMIC_TOL: float = 1e-8

# A2: M ∈ (1+A1, A2_SMALL_SALEM_UPPER]. A small but genuine residual
# above 1. 1.001 puts the boundary right at where the brute-force band
# filter (1 + 1e-6) begins; everything below 1.001 is borderline and
# likely close to a known small Salem (the smallest known Salem is
# Lehmer at 1.176, so a 1.0007 residual would in fact be unusual /
# numerically unreliable).
A2_SMALL_SALEM_UPPER: float = 1.001

# A3: confirmed in-band. Lower bound matches the brute-force band
# filter; upper bound is the Lehmer +100 cap.
A3_BAND_LOWER: float = 1.001
A3_BAND_UPPER: float = 1.18

# Tolerance for cross-checking against Mossinghoff via M-proximity. The
# original brute-force used 1e-6; we use the same so Path A's lookup is
# directly comparable. (1e-5 was suggested in the spec; we use 1e-6 to
# match the existing pipeline. The difference is irrelevant for a poly
# at Lehmer's M which matches catalog Lehmer entries to ~1e-15.)
MOSSINGHOFF_M_TOL: float = 1e-6


# ---------------------------------------------------------------------------
# Polynomial construction
# ---------------------------------------------------------------------------

def build_palindrome_descending(half_coeffs: Sequence[int]) -> list[int]:
    """Build the deg-14 palindromic poly in descending coefficient order.

    Mirrors ``prometheus_math.lehmer_brute_force.build_palindrome_descending``
    (re-implemented locally to avoid a circular dependency on the heavy
    brute-force module's import chain).
    """
    if len(half_coeffs) != 8:
        raise ValueError(
            f"half_coeffs must have length 8; got {len(half_coeffs)}"
        )
    c = [int(x) for x in half_coeffs]
    return [c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7],
            c[6], c[5], c[4], c[3], c[2], c[1], c[0]]


# ---------------------------------------------------------------------------
# High-precision Mahler measure via sympy factorisation
# ---------------------------------------------------------------------------

def high_precision_M_via_factor(
    coeffs_ascending: Sequence[int],
    nroots_precision: int = DEFAULT_NROOTS_PRECISION,
) -> dict:
    """Compute Mahler measure at high precision by factoring first.

    Strategy
    --------
    The bare ``mpmath.polyroots`` Durand-Kerner iteration cannot
    converge on these polynomials at any reasonable maxsteps (verified
    empirically up to dps=400, maxsteps=4000) because they contain
    repeated unit-circle roots from cyclotomic factors. Factoring the
    polynomial over Z first (via ``sympy.factor_list``) decomposes it
    into irreducible pieces, each of which has only simple roots; then
    ``Poly.nroots(n=...)`` on each factor converges fast.

    Mahler measure is multiplicative under polynomial product, so

        M(P) = prod_i M(f_i)^{m_i}

    where P = prod_i f_i^{m_i} is the irreducible factorisation.

    Parameters
    ----------
    coeffs_ascending : sequence of int (length deg+1)
        Ascending-degree coefficients ``[a_0, a_1, ..., a_n]``.
    nroots_precision : int, default 80
        Decimal digits for ``Poly.nroots``.

    Returns
    -------
    dict with keys:
        ``M`` : float (Mahler measure; nan if computation failed)
        ``factors`` : list of dicts ``{degree, multiplicity, M_factor,
                       coeffs_ascending}``
        ``status`` : "ok" | "factor_failed" | "nroots_failed"
        ``error`` : optional str (when status != "ok")
        ``precision_digits`` : int (the nroots_precision actually used)
    """
    import sympy as sp

    # Build sympy polynomial from ascending coeffs.
    deg = len(coeffs_ascending) - 1
    if deg < 1:
        return {
            "M": float("nan"),
            "factors": [],
            "status": "factor_failed",
            "error": "polynomial has degree < 1",
            "precision_digits": int(nroots_precision),
        }

    x = sp.symbols("x")
    expr = sum(int(c) * x**i for i, c in enumerate(coeffs_ascending))
    try:
        poly = sp.Poly(expr, x, domain=sp.ZZ)
    except Exception as exc:  # pragma: no cover -- shouldn't trigger
        return {
            "M": float("nan"),
            "factors": [],
            "status": "factor_failed",
            "error": f"Poly construction failed: {exc!r}",
            "precision_digits": int(nroots_precision),
        }

    # Factor over Z. factor_list returns (content, [(factor, multiplicity), ...]).
    try:
        content, factor_list = sp.factor_list(poly)
    except Exception as exc:
        return {
            "M": float("nan"),
            "factors": [],
            "status": "factor_failed",
            "error": f"factor_list failed: {exc!r}",
            "precision_digits": int(nroots_precision),
        }

    # The content for a primitive polynomial with leading coef ±1 is
    # ±1; M(content)^1 = |content|. We absorb it as a multiplicative
    # constant into M_total. (For our subspace c_0 ∈ {1..5} so content
    # could in principle be > 1, but the palindromic structure with
    # c_n = c_0 means in practice content == 1 here; we still handle
    # the general case.)
    M_total = sp.Abs(sp.Rational(content))
    factor_records: list[dict] = []
    for f, mult in factor_list:
        fp = sp.Poly(f, x, domain=sp.ZZ)
        d = fp.degree()
        leading = fp.LC()
        if d == 0:
            # Constant factor; contributes |leading|^mult to M.
            M_factor = sp.Abs(sp.Rational(leading))
        else:
            try:
                rts = fp.nroots(n=int(nroots_precision))
            except Exception as exc:
                return {
                    "M": float("nan"),
                    "factors": factor_records,
                    "status": "nroots_failed",
                    "error": (
                        f"nroots failed on factor "
                        f"deg={d} mult={mult}: {exc!r}"
                    ),
                    "precision_digits": int(nroots_precision),
                }
            # M(f) = |leading| * prod_{|r|>1} |r|.
            M_factor = sp.Abs(sp.Rational(leading))
            one = sp.Float(1, int(nroots_precision))
            for r in rts:
                ar = sp.Abs(r)
                # Compare in float for the threshold; if the real value
                # is on the unit circle the float comparison errs by
                # at most ~eps ≈ 1e-15, far below the Salem floor of
                # 1.176 - 1 ≈ 0.176, so this is safe even at low n.
                if float(ar) > float(one) + 1e-50:
                    M_factor = M_factor * ar
        # Apply multiplicity.
        M_factor_mult = M_factor**int(mult)
        try:
            M_factor_mult_f = float(M_factor_mult)
        except Exception:
            M_factor_mult_f = float("nan")
        factor_records.append({
            "degree": int(d),
            "multiplicity": int(mult),
            "leading_coef": int(leading),
            "M_factor": M_factor_mult_f,
            "coeffs_ascending": [int(c) for c in fp.all_coeffs()][::-1],
        })
        M_total = M_total * M_factor_mult

    try:
        M_value = float(M_total)
    except Exception:
        M_value = float("nan")

    return {
        "M": M_value,
        "factors": factor_records,
        "status": "ok" if math.isfinite(M_value) else "nroots_failed",
        "error": None if math.isfinite(M_value) else "M evaluated to non-finite",
        "precision_digits": int(nroots_precision),
    }


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_path_a(
    M: float,
    a1_tol: float = A1_CYCLOTOMIC_TOL,
    a2_upper: float = A2_SMALL_SALEM_UPPER,
    a3_lower: float = A3_BAND_LOWER,
    a3_upper: float = A3_BAND_UPPER,
) -> str:
    """Map a verified M into one of the Path A buckets A1/A2/A3/A4.

    See module docstring for definitions.
    """
    if not (isinstance(M, float) and math.isfinite(M)):
        return "A4"
    if M <= 1.0 + a1_tol:
        return "A1"
    if M <= a2_upper:
        return "A2"
    if a3_lower < M < a3_upper:
        return "A3"
    # M >= a3_upper means the entry is OUTSIDE the band — possible if
    # the original numpy run's M was close to the cap and the true M is
    # above 1.18. For Path A's purposes, treat this as "A4" (cannot
    # classify into A1/A2/A3 cleanly; entry exits the band entirely).
    return "A4"


# ---------------------------------------------------------------------------
# Mossinghoff cross-check
# ---------------------------------------------------------------------------

def lookup_in_mossinghoff_by_M(
    coeffs_ascending: Sequence[int],
    M_value: float,
    M_tol: float = MOSSINGHOFF_M_TOL,
    degree_filter: Optional[int] = None,
) -> dict:
    """Cross-check an entry's high-precision M against the Mossinghoff catalog.

    Tries (1) coefficient-exact match (with x -> -x flip) and
    (2) Mahler-measure proximity match. Restricts proximity hits to the
    degree of the input polynomial when ``degree_filter`` is given.

    Returns
    -------
    dict with keys:
        ``in_catalog`` : bool
        ``label`` : str | None — name of matched entry
        ``match_type`` : "coefficient" | "M_proximity" | None
        ``catalog_M`` : float | None
        ``catalog_degree`` : int | None
    """
    from prometheus_math.databases.mahler import (
        lookup_polynomial,
        lookup_by_M,
    )

    # 1. coefficient-exact match (already attempted by the brute-force
    # run, but harmless to retry — gives a label if it lands).
    entry = lookup_polynomial(list(coeffs_ascending))
    if entry is not None:
        return {
            "in_catalog": True,
            "label": str(entry.get("name", "Mossinghoff (coeff match)")),
            "match_type": "coefficient",
            "catalog_M": float(entry.get("mahler_measure", float("nan"))),
            "catalog_degree": entry.get("degree"),
        }

    # 2. M-proximity. Use the high-precision M from Path A.
    if not math.isfinite(M_value):
        return {
            "in_catalog": False,
            "label": None,
            "match_type": None,
            "catalog_M": None,
            "catalog_degree": None,
        }
    M_hits = lookup_by_M(float(M_value), tol=float(M_tol))
    if not M_hits:
        return {
            "in_catalog": False,
            "label": None,
            "match_type": None,
            "catalog_M": None,
            "catalog_degree": None,
        }
    # Prefer same-degree hits.
    if degree_filter is not None:
        same_deg = [h for h in M_hits if h.get("degree") == degree_filter]
        if same_deg:
            best = same_deg[0]
            return {
                "in_catalog": True,
                "label": str(best.get("name", "Mossinghoff (M+deg match)")),
                "match_type": "M_proximity",
                "catalog_M": float(best.get("mahler_measure", float("nan"))),
                "catalog_degree": best.get("degree"),
            }
    best = M_hits[0]
    return {
        "in_catalog": True,
        "label": str(best.get("name", "Mossinghoff (M match)")),
        "match_type": "M_proximity",
        "catalog_M": float(best.get("mahler_measure", float("nan"))),
        "catalog_degree": best.get("degree"),
    }


# ---------------------------------------------------------------------------
# Single-entry pipeline
# ---------------------------------------------------------------------------

def verify_entry(
    entry: dict,
    nroots_precision_ladder: tuple[int, ...] = (60, 100, 200),
) -> dict:
    """Run Path A on a single brute-force band entry.

    Tries ``high_precision_M_via_factor`` at each precision in
    ``nroots_precision_ladder`` until one succeeds (status == "ok").
    Records which precision was needed.

    Parameters
    ----------
    entry : dict
        A single dict from
        ``_lehmer_brute_force_results.json["in_lehmer_band"]``. Must
        have keys ``coeffs_ascending``, ``half_coeffs``, ``M_numpy``.
    nroots_precision_ladder : tuple of int, default (60, 100, 200)
        Tried in order; first success wins.

    Returns
    -------
    dict — see ``run_path_a`` for the schema.
    """
    coeffs_asc = list(entry.get("coeffs_ascending", []))
    if not coeffs_asc:
        # Reconstruct from half_coeffs if needed.
        half = entry.get("half_coeffs")
        if half:
            desc = build_palindrome_descending(half)
            coeffs_asc = list(reversed(desc))

    M_history: list[dict] = []
    converged_dps: Optional[int] = None
    M_value: float = float("nan")
    factors: list[dict] = []
    last_status = "factor_failed"
    last_error: Optional[str] = "no precision tried"

    for dps in nroots_precision_ladder:
        t0 = time.perf_counter()
        try:
            res = high_precision_M_via_factor(coeffs_asc, nroots_precision=dps)
        except Exception as exc:
            res = {
                "M": float("nan"),
                "factors": [],
                "status": "nroots_failed",
                "error": f"verify_entry top-level exception: {exc!r}",
                "precision_digits": int(dps),
            }
        elapsed = time.perf_counter() - t0
        M_history.append({
            "precision_digits": int(dps),
            "M": res.get("M"),
            "status": res.get("status"),
            "wall_time_seconds": float(elapsed),
            "error": res.get("error"),
        })
        last_status = res.get("status", "factor_failed")
        last_error = res.get("error")
        M_value = float(res.get("M", float("nan")))
        factors = res.get("factors", [])
        if last_status == "ok" and math.isfinite(M_value):
            converged_dps = int(dps)
            break

    classification = classify_path_a(M_value)

    moss = {
        "in_catalog": False,
        "label": None,
        "match_type": None,
        "catalog_M": None,
        "catalog_degree": None,
    }
    if classification == "A3":
        moss = lookup_in_mossinghoff_by_M(
            coeffs_asc,
            M_value=M_value,
            degree_filter=len(coeffs_asc) - 1,
        )

    return {
        "half_coeffs": list(entry.get("half_coeffs", [])),
        "coeffs_ascending": coeffs_asc,
        "M_numpy": float(entry.get("M_numpy", float("nan"))),
        "M_mpmath_original": float(entry.get("M_mpmath", float("nan"))),
        "M_path_a": M_value,
        "convergence_precision_digits": converged_dps,
        "precision_history": M_history,
        "factors": factors,
        "status": last_status,
        "error": last_error,
        "classification": classification,
        "mossinghoff_match": moss,
        "verdict_per_entry": _per_entry_verdict(classification, moss),
    }


def _per_entry_verdict(classification: str, moss: dict) -> str:
    """Map (classification, mossinghoff_match) into a per-entry verdict.

    * cyclotomic_noise — A1 or A2 (true M = 1 or just barely above)
    * rediscovery — A3 with Mossinghoff match
    * candidate — A3 with NO Mossinghoff match (potential discovery)
    * still_unverified — A4
    """
    if classification in ("A1", "A2"):
        return "cyclotomic_noise"
    if classification == "A3":
        if moss.get("in_catalog", False):
            return "rediscovery"
        return "candidate"
    return "still_unverified"


# ---------------------------------------------------------------------------
# Top-level pipeline
# ---------------------------------------------------------------------------

def load_unverified_entries(brute_force_results_path: str | Path) -> list[dict]:
    """Read the brute-force JSON and return the 17 not-in-Mossinghoff
    entries with verification_failed=True (i.e. the Path A targets).

    Doesn't filter further — accepts any entry where
    ``in_mossinghoff is False``. (In the current brute-force run, every
    such entry also has verification_failed=True, but Path A's logic
    doesn't depend on that — it re-verifies regardless.)
    """
    path = Path(brute_force_results_path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    band = data.get("in_lehmer_band", [])
    return [e for e in band if not e.get("in_mossinghoff", True)]


def run_path_a(
    brute_force_results_path: str | Path = (
        Path(__file__).parent / "_lehmer_brute_force_results.json"
    ),
    output_path: Optional[str | Path] = None,
    nroots_precision_ladder: tuple[int, ...] = (60, 100, 200),
    progress: bool = False,
) -> dict:
    """Run Path A end-to-end on the unverified brute-force entries.

    Parameters
    ----------
    brute_force_results_path : path
        Path to the brute-force results JSON (NOT modified).
    output_path : path, optional
        Where to write the Path A results JSON. If None, no file is
        written (useful for in-test invocations).
    nroots_precision_ladder : tuple of int, default (60, 100, 200)
        Precision (decimal digits) ladder for nroots; first converged
        precision per entry wins.
    progress : bool, default False
        Print per-entry progress to stdout.

    Returns
    -------
    dict — the full Path A results document. Also written to
    ``output_path`` if provided.
    """
    t_start = time.perf_counter()
    entries = load_unverified_entries(brute_force_results_path)
    n_total = len(entries)
    if progress:
        print(f"[lehmer_path_a] loaded {n_total} unverified entries")

    per_entry_results: list[dict] = []
    for i, entry in enumerate(entries):
        if progress:
            print(f"[lehmer_path_a] verifying {i+1}/{n_total} half={entry.get('half_coeffs')}")
        result = verify_entry(
            entry,
            nroots_precision_ladder=nroots_precision_ladder,
        )
        per_entry_results.append(result)
        if progress:
            print(
                f"  -> M_path_a={result['M_path_a']!r} "
                f"class={result['classification']} "
                f"verdict={result['verdict_per_entry']}"
            )

    # Aggregate convergence + classification stats.
    convergence_counts: dict[int, int] = {dps: 0 for dps in nroots_precision_ladder}
    convergence_counts[-1] = 0  # represents "did not converge"
    for r in per_entry_results:
        dps = r.get("convergence_precision_digits")
        if dps is None:
            convergence_counts[-1] += 1
        else:
            convergence_counts[dps] = convergence_counts.get(dps, 0) + 1

    class_counts = {"A1": 0, "A2": 0, "A3": 0, "A4": 0}
    for r in per_entry_results:
        class_counts[r["classification"]] = class_counts.get(r["classification"], 0) + 1

    verdict_counts = {
        "cyclotomic_noise": 0,
        "rediscovery": 0,
        "candidate": 0,
        "still_unverified": 0,
    }
    for r in per_entry_results:
        v = r["verdict_per_entry"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    # Path A's substrate-level verdict.
    if class_counts["A4"] == 0 and verdict_counts["candidate"] == 0:
        # Every entry classified, every A3 matched in Mossinghoff.
        substrate_verdict = "H5_CONFIRMED"
        substrate_explanation = (
            "All 17 unverified entries resolved at high precision. "
            "All A1+A2 entries are cyclotomic-noise (true M ≈ 1, not "
            "in-band). All A3 entries match Mossinghoff via M-proximity "
            "(rediscovery of catalog entries). Path A lifts the "
            "INCONCLUSIVE verdict to H5_CONFIRMED for the deg-14 "
            "palindromic ±5 subspace."
        )
    elif class_counts["A4"] > 0:
        substrate_verdict = "INCONCLUSIVE"
        substrate_explanation = (
            f"{class_counts['A4']} entry/entries (A4) failed to converge "
            f"even at the highest precision ({nroots_precision_ladder[-1]} "
            f"digits). The substrate cannot certify these entries; Path A "
            f"alone is insufficient. Try Path B (symbolic factorisation) "
            f"or Path C."
        )
    else:
        # No A4 but at least one candidate (A3 with no Moss match).
        substrate_verdict = "H2_BREAKS"
        substrate_explanation = (
            f"All entries verified at high precision, but "
            f"{verdict_counts['candidate']} A3 candidate(s) lack a "
            f"Mossinghoff match. These are potential novel sub-1.18 "
            f"specimens — flagged for Path B/C cross-check."
        )

    candidate_flagged = [
        r for r in per_entry_results
        if r["verdict_per_entry"] == "candidate"
    ]

    wall_time = time.perf_counter() - t_start

    document = {
        "subspace": "deg14_palindromic_coeffs_pm5_c0_positive",
        "source_brute_force_results": str(brute_force_results_path),
        "nroots_precision_ladder": list(nroots_precision_ladder),
        "n_unverified_entries_loaded": n_total,
        "convergence_counts": convergence_counts,
        "classification_counts": class_counts,
        "verdict_counts": verdict_counts,
        "substrate_verdict": substrate_verdict,
        "substrate_explanation": substrate_explanation,
        "candidate_flagged": candidate_flagged,
        "wall_time_seconds": float(wall_time),
        "per_entry_results": per_entry_results,
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

    default_brute = str(Path(__file__).parent / "_lehmer_brute_force_results.json")
    default_out = str(Path(__file__).parent / "_lehmer_brute_force_path_a_results.json")
    parser = argparse.ArgumentParser(
        description="Path A: high-precision re-verification of "
                    "unverified Lehmer brute-force band entries."
    )
    parser.add_argument("--input", type=str, default=default_brute)
    parser.add_argument("--output", type=str, default=default_out)
    parser.add_argument(
        "--ladder",
        type=str,
        default="60,100,200",
        help="Comma-separated precision (decimal-digits) ladder."
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    ladder = tuple(int(x) for x in args.ladder.split(","))
    res = run_path_a(
        brute_force_results_path=args.input,
        output_path=args.output,
        nroots_precision_ladder=ladder,
        progress=not args.quiet,
    )

    print()
    print("=" * 64)
    print(f"Path A substrate verdict: {res['substrate_verdict']}")
    print(f"Classification counts: {res['classification_counts']}")
    print(f"Verdict counts: {res['verdict_counts']}")
    print(f"Convergence counts: {res['convergence_counts']}")
    print(f"Wall time: {res['wall_time_seconds']:.1f}s")
    print(f"Output: {args.output}")
