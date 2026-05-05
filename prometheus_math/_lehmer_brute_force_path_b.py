"""Path B: symbolic factorization over Z[x] of the 17 verification_failed
entries from the deg-14 ±5 palindromic Lehmer brute-force run.

Mission
-------
Brute force returned INCONCLUSIVE. The 17 ``verification_failed`` band
hits (M < 1.18, mpmath returned NaN, has_cyclotomic_factor=True, NOT in
Mossinghoff) need an authoritative classification:

* B1 — all-cyclotomic (true M = 1; numpy noise put them in band)
* B2 — Lehmer × Phi_n (Mossinghoff label-fuzzy missed)
* B3 — non-cyclotomic factor that's not Lehmer (potential discovery)
* B4 — irreducible degree-N palindromic with M < 1.18 NOT in Mossinghoff
       (the dramatic finding)

Method
------
Exact symbolic factorization over Z[x] via sympy. For each entry:
1. ``sympy.Poly(P, x, domain='ZZ').factor_list()`` — exact factor list.
2. For each factor, test whether it equals ``cyclotomic_poly(n, x)`` for
   some n with phi(n) = factor.degree(). (Cyclotomics have M = 1 exactly.)
3. Classify B1 / B2 / B3 / B4 from the factor pattern.
4. Compute exact M of any non-cyclotomic factor via mpmath at high dps
   (factored polynomial is small degree, so this is robust unlike the
   degree-14 mpmath recheck that returned NaN).
5. Cross-check against Mossinghoff by M-value and by exact coefficient
   match of the non-cyclotomic factor.

Output
------
* ``prometheus_math/_lehmer_brute_force_path_b_results.json``
* ``prometheus_math/LEHMER_BRUTE_FORCE_PATH_B_RESULTS.md``

Exact arithmetic. Honest framing. Wall budget: ~10 min.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Optional

import sympy as sp


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEHMER_COEFFS_ASC = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
"""Lehmer's polynomial L(x) coefficients (ascending). Degree 10."""

LEHMER_M_EXACT_DPS_60 = "1.17628081825991750654407033847403505069341580656469320656763"
"""Lehmer's M to 60 dps (Mossinghoff catalog)."""

LEHMER_BAND_UPPER = 1.18
"""Lehmer band upper limit (matches brute-force run config)."""

# Max n for cyclotomic factor candidate search. phi(n) <= 14 implies
# n <= 60 is plenty (phi(61) = 60 already). We extend to 200 to match
# the brute-force heuristic envelope for safety.
MAX_CYCLOTOMIC_N = 200


# ---------------------------------------------------------------------------
# Cyclotomic detection
# ---------------------------------------------------------------------------

_x = sp.symbols("x")


def _build_cyclotomic_table(max_n: int = MAX_CYCLOTOMIC_N) -> dict[int, sp.Poly]:
    """Precompute Phi_n(x) as sympy.Poly for n = 1..max_n."""
    table = {}
    for n in range(1, max_n + 1):
        phi = sp.Poly(sp.cyclotomic_poly(n, _x), _x, domain="ZZ")
        table[n] = phi
    return table


_CYCLO_TABLE: dict[int, sp.Poly] = _build_cyclotomic_table()
_CYCLO_BY_DEG: dict[int, list[int]] = {}
for _n, _phi in _CYCLO_TABLE.items():
    _CYCLO_BY_DEG.setdefault(_phi.degree(), []).append(_n)


def identify_cyclotomic(factor_poly: sp.Poly) -> Optional[int]:
    """If ``factor_poly`` equals Phi_n(x) for some n <= MAX_CYCLOTOMIC_N,
    return n. Otherwise return None.

    Exact equality test (sympy.Poly equality is structural over the
    given domain, normalised to a canonical form).
    """
    deg = factor_poly.degree()
    candidates = _CYCLO_BY_DEG.get(deg, [])
    for n in candidates:
        if factor_poly == _CYCLO_TABLE[n]:
            return n
    return None


def is_lehmer_factor(factor_poly: sp.Poly) -> bool:
    """Test whether ``factor_poly`` is Lehmer's polynomial (or its
    x -> -x reflection, which has the same M).

    Lehmer ascending: [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1] (degree 10).
    Sign-flip (x -> -x) gives [1, -1, 0, 1, -1, 1, -1, 1, 0, -1, 1].
    """
    if factor_poly.degree() != 10:
        return False
    coeffs_desc = factor_poly.all_coeffs()  # leading first
    coeffs_asc = list(reversed(coeffs_desc))
    if coeffs_asc == LEHMER_COEFFS_ASC:
        return True
    # x -> -x: alternate signs starting with sign +1 at x^0
    flipped = [c if i % 2 == 0 else -c for i, c in enumerate(LEHMER_COEFFS_ASC)]
    if coeffs_asc == flipped:
        return True
    # Also check global sign flip
    if coeffs_asc == [-c for c in LEHMER_COEFFS_ASC]:
        return True
    if coeffs_asc == [-c for c in flipped]:
        return True
    return False


def mahler_measure_high_precision(factor_poly: sp.Poly, dps: int = 80) -> float:
    """Compute M(factor_poly) at high mpmath precision.

    For a polynomial with integer coefficients, M = |a_n| * prod(max(1, |alpha_i|))
    where alpha_i are the roots and a_n is the leading coefficient.

    Returns
    -------
    float (best to convert to mpmath at the call site for full precision,
    but float is enough for in-band cross-checking at our 1e-6 tolerance).
    """
    import mpmath as mp

    saved_dps = mp.mp.dps
    mp.mp.dps = dps
    try:
        coeffs_desc = factor_poly.all_coeffs()
        # mpmath polyroots wants mpc coefficients
        mp_coeffs = [mp.mpf(int(c)) for c in coeffs_desc]
        roots = mp.polyroots(mp_coeffs, maxsteps=200, extraprec=2 * dps)
        leading = abs(mp.mpf(int(coeffs_desc[0])))
        product = leading
        for r in roots:
            ar = abs(r)
            if ar > 1:
                product *= ar
        return float(product)
    finally:
        mp.mp.dps = saved_dps


# ---------------------------------------------------------------------------
# Per-entry classification
# ---------------------------------------------------------------------------

def factor_and_classify(coeffs_ascending: list[int]) -> dict:
    """Symbolic factorization + B1/B2/B3/B4 classification.

    Parameters
    ----------
    coeffs_ascending : list[int]
        Polynomial coefficients in ascending order (c_0 first, c_n last).

    Returns
    -------
    dict with keys:
      coeffs_ascending, factor_list (list of {coeffs, degree, multiplicity,
      is_cyclotomic, cyclotomic_n, is_lehmer, M_exact}),
      classification (B1 / B2 / B3 / B4), classification_reason,
      M_non_cyclotomic_product (float, M of the product of non-cyclo factors),
      mossinghoff_check_for_non_cyclo_factor.
    """
    # Build sympy polynomial. Sympy expects descending or expression form.
    desc = list(reversed(coeffs_ascending))
    P = sp.Poly(desc, _x, domain="ZZ")

    # factor_list -> (content, [(factor_poly, multiplicity), ...])
    content, factors = P.factor_list()

    factor_records = []
    non_cyclo_factors = []
    for fp, mult in factors:
        cyclo_n = identify_cyclotomic(fp)
        is_cyclo = cyclo_n is not None
        is_lehm = is_lehmer_factor(fp) if not is_cyclo else False
        if not is_cyclo:
            non_cyclo_factors.append((fp, mult))
        # Compute M of this factor (only meaningful for non-cyclo; for
        # cyclo we know M = 1 exactly).
        if is_cyclo:
            M_factor = 1.0
        else:
            try:
                M_factor = mahler_measure_high_precision(fp, dps=80)
            except Exception as exc:  # pragma: no cover - documented fallback
                M_factor = None
        factor_records.append({
            "coeffs_descending": [int(c) for c in fp.all_coeffs()],
            "degree": int(fp.degree()),
            "multiplicity": int(mult),
            "is_cyclotomic": bool(is_cyclo),
            "cyclotomic_n": int(cyclo_n) if cyclo_n is not None else None,
            "is_lehmer_polynomial": bool(is_lehm),
            "M_exact": float(M_factor) if M_factor is not None else None,
        })

    # Classification
    n_non_cyclo = len(non_cyclo_factors)
    if n_non_cyclo == 0:
        classification = "B1"
        reason = "All factors are cyclotomic; M(P) = 1 exactly. Numpy noise put it in band."
    else:
        # Check for irreducibility (single non-cyclo factor of full degree, no cyclo factors)
        is_full_irreducible = (
            len(factors) == 1
            and factors[0][1] == 1
            and not factor_records[0]["is_cyclotomic"]
        )
        # Lehmer × cyclotomic test: exactly one non-cyclo factor, AND that factor is Lehmer.
        # (Multiplicity arbitrary, but Lehmer^k has M = Lehmer_M^k. For our band
        #  M < 1.18, only k=1 is in band; document if k > 1.)
        all_non_cyclo_lehmer = all(
            is_lehmer_factor(fp) for fp, _ in non_cyclo_factors
        )
        if all_non_cyclo_lehmer and n_non_cyclo == 1:
            classification = "B2"
            mult = non_cyclo_factors[0][1]
            cyclo_ns = [r["cyclotomic_n"] for r in factor_records if r["is_cyclotomic"]]
            reason = (
                f"Lehmer (mult={mult}) × cyclotomic factor(s) Phi_{cyclo_ns}. "
                f"M(P) = Lehmer_M = 1.17628..."
            )
        elif is_full_irreducible:
            classification = "B4"
            reason = (
                f"Irreducible non-cyclotomic factor of degree "
                f"{factor_records[0]['degree']} (= full poly degree). "
                f"Genuine Salem/Lehmer-band candidate NOT in Mossinghoff!"
            )
        else:
            # Some other non-cyclotomic factor or multi-non-cyclo product
            classification = "B3"
            reason = (
                f"{n_non_cyclo} non-cyclotomic factor(s), not all Lehmer. "
                f"Investigate: novel small-Mahler factor or unrecognised product."
            )

    # Compute M of the product of non-cyclotomic factors (= M(P) since
    # cyclotomic factors contribute M = 1).
    if non_cyclo_factors:
        prod = sp.Poly(1, _x, domain="ZZ")
        for fp, mult in non_cyclo_factors:
            prod = prod * (fp ** mult)
        try:
            M_non_cyclo_product = mahler_measure_high_precision(prod, dps=80)
        except Exception as exc:
            M_non_cyclo_product = None
    else:
        M_non_cyclo_product = 1.0

    # Mossinghoff cross-check on the non-cyclotomic part (only if non-trivial)
    mossinghoff_check = _mossinghoff_check_factor(non_cyclo_factors, M_non_cyclo_product)

    return {
        "coeffs_ascending": list(coeffs_ascending),
        "content": int(content),
        "factor_list": factor_records,
        "n_factors": len(factor_records),
        "n_non_cyclotomic_factors": int(n_non_cyclo),
        "classification": classification,
        "classification_reason": reason,
        "M_non_cyclotomic_product": (
            float(M_non_cyclo_product) if M_non_cyclo_product is not None else None
        ),
        "mossinghoff_cross_check": mossinghoff_check,
    }


def _mossinghoff_check_factor(non_cyclo_factors, M_non_cyclo_product):
    """Cross-check the non-cyclotomic factor product against Mossinghoff.

    1. Coefficient match (with x -> -x flip) of the product.
    2. M-value proximity match (tol 1e-6).

    Returns dict {in_catalog, label, match_method}.
    """
    if not non_cyclo_factors:
        return {"in_catalog": None, "label": None, "match_method": "no_non_cyclotomic_factor"}
    try:
        from prometheus_math.databases.mahler import lookup_polynomial, lookup_by_M
    except Exception as exc:  # pragma: no cover
        return {"in_catalog": None, "label": None, "match_method": f"db_import_error: {exc}"}

    # Build product
    prod = sp.Poly(1, _x, domain="ZZ")
    for fp, mult in non_cyclo_factors:
        prod = prod * (fp ** mult)
    coeffs_desc = [int(c) for c in prod.all_coeffs()]
    coeffs_asc = list(reversed(coeffs_desc))

    # Coefficient match (and x -> -x flipped)
    entry = lookup_polynomial(coeffs_asc)
    if entry is not None:
        return {
            "in_catalog": True,
            "label": str(entry.get("name", "Mossinghoff (unnamed)")),
            "match_method": "coefficient_exact",
        }
    flipped = [c if i % 2 == 0 else -c for i, c in enumerate(coeffs_asc)]
    entry = lookup_polynomial(flipped)
    if entry is not None:
        return {
            "in_catalog": True,
            "label": str(entry.get("name", "Mossinghoff (unnamed)")),
            "match_method": "coefficient_xflip",
        }

    # M-value match
    if M_non_cyclo_product is not None and math.isfinite(M_non_cyclo_product):
        M_hits = lookup_by_M(float(M_non_cyclo_product), tol=1e-6)
        if M_hits:
            # Prefer same-degree match
            deg = sum(fp.degree() * mult for fp, mult in non_cyclo_factors)
            same_deg = [h for h in M_hits if h.get("degree") == deg]
            chosen = same_deg[0] if same_deg else M_hits[0]
            return {
                "in_catalog": True,
                "label": str(chosen.get("name", "Mossinghoff (M-match)")),
                "match_method": (
                    f"M_value_match (tol=1e-6, "
                    f"{'same_degree' if same_deg else 'any_degree'})"
                ),
            }

    return {
        "in_catalog": False,
        "label": None,
        "match_method": "no_match",
    }


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------

def load_verification_failed_entries(json_path: Path) -> list[dict]:
    """Load the 17 verification_failed entries from the brute-force JSON."""
    with open(json_path) as f:
        data = json.load(f)
    band = data["in_lehmer_band"]
    failed = [
        e for e in band
        if e.get("verification_failed") and not e.get("in_mossinghoff")
    ]
    return failed


def run_path_b(
    json_path: Path = Path("prometheus_math/_lehmer_brute_force_results.json"),
    output_json: Path = Path("prometheus_math/_lehmer_brute_force_path_b_results.json"),
) -> dict:
    """Execute Path B end-to-end."""
    t0 = time.time()
    entries = load_verification_failed_entries(json_path)
    print(f"[path_b] Loaded {len(entries)} verification_failed entries.")

    results = []
    classification_counts = {"B1": 0, "B2": 0, "B3": 0, "B4": 0}
    for i, entry in enumerate(entries):
        coeffs_asc = entry["coeffs_ascending"]
        print(f"[path_b] {i+1}/{len(entries)} factoring deg={len(coeffs_asc)-1} ...")
        try:
            classification = factor_and_classify(coeffs_asc)
        except Exception as exc:
            classification = {
                "coeffs_ascending": list(coeffs_asc),
                "classification": "ERROR",
                "classification_reason": f"sympy factorization failed: {exc}",
                "factor_list": [],
                "n_factors": 0,
                "n_non_cyclotomic_factors": 0,
                "M_non_cyclotomic_product": None,
                "mossinghoff_cross_check": {"in_catalog": None, "label": None, "match_method": "error"},
            }
        # Attach original brute-force fields (so the report has full context)
        merged = {
            "source_entry": entry,
            **classification,
        }
        results.append(merged)
        cls = classification["classification"]
        if cls in classification_counts:
            classification_counts[cls] += 1
        else:
            classification_counts[cls] = classification_counts.get(cls, 0) + 1

    wall_time = time.time() - t0

    # Determine Path B verdict
    n_total = len(entries)
    n_B1 = classification_counts.get("B1", 0)
    n_B2 = classification_counts.get("B2", 0)
    n_B3 = classification_counts.get("B3", 0)
    n_B4 = classification_counts.get("B4", 0)

    if n_B4 > 0:
        path_b_verdict = "H2_BREAKS_CANDIDATE"
        verdict_reason = (
            f"{n_B4} irreducible deg-N palindromic poly with M < 1.18 NOT in Mossinghoff. "
            "DISCOVERY CANDIDATE. Independent verification required."
        )
    elif n_B3 > 0:
        path_b_verdict = "INVESTIGATE_B3"
        verdict_reason = (
            f"{n_B3} entry(ies) classified B3 (non-cyclotomic factors not matching Lehmer). "
            "Manual review required for novelty assessment."
        )
    elif n_B1 + n_B2 == n_total:
        path_b_verdict = "H5_CONFIRMED"
        verdict_reason = (
            f"All {n_total} verification_failed entries resolve to either "
            f"all-cyclotomic ({n_B1}) or Lehmer × cyclotomic ({n_B2}). "
            "INCONCLUSIVE lifted: every band hit reproduces a known catalog entry "
            "(modulo Mossinghoff label-match limitations)."
        )
    else:
        path_b_verdict = "INCONCLUSIVE"
        verdict_reason = "Some entries failed classification."

    summary = {
        "input": str(json_path),
        "n_entries": n_total,
        "classification_counts": classification_counts,
        "path_b_verdict": path_b_verdict,
        "verdict_reason": verdict_reason,
        "wall_time_seconds": wall_time,
        "lehmer_M_reference_dps_60": LEHMER_M_EXACT_DPS_60,
        "results": results,
    }

    with open(output_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"[path_b] Wrote {output_json}")
    print(f"[path_b] Counts: {classification_counts}")
    print(f"[path_b] Verdict: {path_b_verdict}")
    print(f"[path_b] Wall time: {wall_time:.1f}s")

    return summary


if __name__ == "__main__":
    run_path_b()
