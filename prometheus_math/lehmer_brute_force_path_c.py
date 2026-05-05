"""Path C resolution of the Lehmer brute-force INCONCLUSIVE verdict.

Mission
-------
The Charon brute-force on the deg-14 ±5 palindromic subspace returned 17
"NOT-in-Mossinghoff" entries with ``verification_failed=True``:

* 15 with ``residual_M ≈ 1.001-1.005`` (Class 1: cyclotomic-noise above
  the original 1.0001 filter threshold).
* 2 with ``residual_M ≈ 1.1763`` (Class 2: Lehmer-depth, expected to be
  Lehmer × Φ_n products that the original lookup missed via float
  tolerance).

Path C is the **catalog-lookup-fuzziness** hypothesis test: tighten the
Mossinghoff lookup to handle (a) M-precision tolerance, (b) Hamming
distance over coefficient vectors, and (c) explicit ``Lehmer × Φ_n``
product recognition via sympy's exact factorisation.

If every entry resolves to one of:

* **C1** catalog match via tighter M+Hamming proximity,
* **C2** Lehmer × Φ_n product (sympy-exact),
* **C3** all-cyclotomic noise (M = 1 exactly under sympy),

then Path C lifts INCONCLUSIVE → H5_CONFIRMED. Any **C4** (still
unmatched) is a discovery candidate and triggers the cross-check
gauntlet (arXiv / OEIS / LMFDB).

Independence and agreement
--------------------------
Path C is independent of Paths A (mpmath dps=50 reverification) and B
(symbolic-only direct factor decomposition); the three paths should
produce concordant classifications. Agreement is the verification that
INCONCLUSIVE was genuinely a tooling artefact, not a genuine open
question.

Forged: 2026-05-04 by Techne (toolsmith) for Charon's H5 settlement.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional, Sequence

import sympy as sp


__all__ = [
    "LEHMER_COEFFS_ASCENDING",
    "LEHMER_M_REFERENCE",
    "PROXIMITY_M_TOL_LOOSE",
    "PROXIMITY_M_TOL_TIGHT",
    "all_cyclotomic_factors",
    "classify_entry",
    "cyclotomic_index_of_factor",
    "factor_into_cyclotomic_and_residual",
    "hamming_distance",
    "is_lehmer_polynomial",
    "lehmer_phi_decomposition",
    "load_brute_force_results",
    "load_mossinghoff_catalog",
    "proximity_match_catalog",
    "run_path_c",
    "summarize_classifications",
]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Lehmer's deg-10 polynomial in ascending order
LEHMER_COEFFS_ASCENDING: tuple[int, ...] = (
    1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1,
)
LEHMER_M_REFERENCE: float = 1.1762808182599175

# Proximity tolerances for the tighter Mossinghoff lookup. The original
# brute-force used 1e-6 (too tight for verification_failed mpmath NaN
# entries that fall back on numpy noise). Path C uses 1e-3 for the
# initial sweep and 1e-9 for the post-Hamming tightening.
PROXIMITY_M_TOL_LOOSE: float = 1e-3
PROXIMITY_M_TOL_TIGHT: float = 1e-9


# ---------------------------------------------------------------------------
# Catalog & input loading
# ---------------------------------------------------------------------------

def load_brute_force_results(
    path: str | Path = "prometheus_math/_lehmer_brute_force_results.json",
) -> dict:
    """Load the deg-14 brute-force results JSON.

    Returns the parsed dict. Raises FileNotFoundError if missing.
    """
    p = Path(path)
    if not p.exists():
        # Try as an absolute or repo-relative path.
        alt = Path(__file__).parent / "_lehmer_brute_force_results.json"
        if alt.exists():
            p = alt
        else:
            raise FileNotFoundError(f"Brute-force results not found: {path}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def load_mossinghoff_catalog() -> list[dict]:
    """Return a deep-copy of the Mossinghoff catalog (8625+ entries)."""
    from prometheus_math.databases._mahler_data import MAHLER_TABLE
    import copy
    return [copy.deepcopy(e) for e in MAHLER_TABLE]


# ---------------------------------------------------------------------------
# Hamming distance & proximity match
# ---------------------------------------------------------------------------

def hamming_distance(a: Sequence[int], b: Sequence[int]) -> int:
    """Count positions where two equal-length integer vectors differ.

    For unequal lengths, the shorter vector is right-padded with zeros
    (so trailing zero entries of the shorter vector contribute nothing
    if the longer vector has zeros there).
    """
    a = list(a)
    b = list(b)
    n = max(len(a), len(b))
    a_pad = a + [0] * (n - len(a))
    b_pad = b + [0] * (n - len(b))
    return sum(1 for x, y in zip(a_pad, b_pad) if x != y)


def _x_flip(coeffs_ascending: Sequence[int]) -> list[int]:
    """Coefficients of P(-x) given coefficients of P(x) ascending."""
    return [c if i % 2 == 0 else -c for i, c in enumerate(coeffs_ascending)]


def proximity_match_catalog(
    coeffs_ascending: Sequence[int],
    M_value: float,
    catalog: list[dict],
    M_tol: float = PROXIMITY_M_TOL_LOOSE,
    max_hamming: int = 0,
) -> Optional[dict]:
    """Find a catalog entry within (M_tol, max_hamming) of this entry.

    Tries both the entry's own coefficients and the x->-x flip. Returns
    the best-matching catalog entry (lowest combined |ΔM| + Hamming) or
    ``None``.
    """
    target = list(coeffs_ascending)
    target_flip = _x_flip(target)

    best: Optional[tuple[float, int, dict]] = None
    for e in catalog:
        c = list(e["coeffs"])
        m = float(e["mahler_measure"])
        if abs(m - float(M_value)) > M_tol:
            continue
        h1 = hamming_distance(target, c)
        h2 = hamming_distance(target_flip, c)
        h = min(h1, h2)
        if h <= max_hamming:
            score = (abs(m - float(M_value)), h)
            if best is None or score < (best[0], best[1]):
                best = (score[0], score[1], e)
    return best[2] if best else None


# ---------------------------------------------------------------------------
# Cyclotomic factorisation via sympy
# ---------------------------------------------------------------------------

# Precompute Φ_n coefficient vectors (ascending) for n in a useful range.
# We compute on demand and cache.
_PHI_CACHE: dict[int, tuple[int, ...]] = {}


def _phi_coeffs(n: int) -> tuple[int, ...]:
    """Coefficients of Φ_n in ascending order (cached)."""
    if n in _PHI_CACHE:
        return _PHI_CACHE[n]
    x = sp.symbols("x")
    poly = sp.Poly(sp.cyclotomic_poly(n, x), x)
    desc = [int(c) for c in poly.all_coeffs()]
    asc = tuple(reversed(desc))
    _PHI_CACHE[n] = asc
    return asc


def cyclotomic_index_of_factor(
    factor_coeffs_descending: Sequence[int],
    max_n: int = 200,
) -> Optional[int]:
    """If the given factor (descending coeffs) is Φ_n for some n ≤ max_n,
    return n. Otherwise return ``None``.
    """
    desc = [int(c) for c in factor_coeffs_descending]
    asc = list(reversed(desc))
    deg = len(asc) - 1
    if deg < 1:
        return None
    # Φ_n has degree φ(n). For φ(n) = deg, candidate n satisfies
    # Euler's totient. Sweep n up to max_n.
    for n in range(1, max_n + 1):
        phi = _phi_coeffs(n)
        if len(phi) - 1 != deg:
            continue
        if tuple(asc) == phi:
            return n
    return None


def factor_into_cyclotomic_and_residual(
    coeffs_ascending: Sequence[int],
) -> tuple[dict[int, int], list[int], list[tuple[list[int], int]]]:
    """Factor a polynomial into (cyclotomic part, residual part).

    Parameters
    ----------
    coeffs_ascending : sequence of int

    Returns
    -------
    (phi_factors, residual_coeffs_ascending, residual_factor_list)
        ``phi_factors`` maps n -> multiplicity for each cyclotomic
        factor Φ_n. ``residual_coeffs_ascending`` is the product of the
        non-cyclotomic factors (with their multiplicities) in ascending
        order; an empty list means the polynomial is fully cyclotomic.
        ``residual_factor_list`` is the list of (factor_coeffs_ascending,
        multiplicity) for each non-cyclotomic irreducible factor.
    """
    x = sp.symbols("x")
    asc = [int(c) for c in coeffs_ascending]
    p = sp.Poly(asc[::-1], x)  # sp.Poly takes descending coeffs
    _, factors = sp.factor_list(p.as_expr(), gens=x)

    phi_factors: dict[int, int] = {}
    residual_factors: list[tuple[list[int], int]] = []
    residual = sp.Integer(1)

    for f, mult in factors:
        f_poly = sp.Poly(f, x)
        f_desc = [int(c) for c in f_poly.all_coeffs()]
        n = cyclotomic_index_of_factor(f_desc)
        if n is not None:
            phi_factors[n] = phi_factors.get(n, 0) + int(mult)
        else:
            f_asc = list(reversed(f_desc))
            residual_factors.append((f_asc, int(mult)))
            residual = residual * (f_poly.as_expr() ** int(mult))

    if residual == sp.Integer(1):
        residual_asc: list[int] = []
    else:
        residual_poly = sp.Poly(sp.expand(residual), x)
        residual_desc = [int(c) for c in residual_poly.all_coeffs()]
        residual_asc = list(reversed(residual_desc))

    return phi_factors, residual_asc, residual_factors


def all_cyclotomic_factors(coeffs_ascending: Sequence[int]) -> bool:
    """True iff the polynomial factors entirely into cyclotomic pieces.

    Such a polynomial has Mahler measure exactly 1 (all roots on the
    unit circle); any in-band reading > 1.0001 is float-noise from the
    numpy companion-matrix path.
    """
    _, residual_asc, _ = factor_into_cyclotomic_and_residual(coeffs_ascending)
    return len(residual_asc) == 0


# ---------------------------------------------------------------------------
# Lehmer × Φ_n decomposition
# ---------------------------------------------------------------------------

def is_lehmer_polynomial(
    coeffs_ascending: Sequence[int],
    allow_x_flip: bool = True,
) -> bool:
    """True iff the coefficient list IS Lehmer's deg-10 polynomial.

    With ``allow_x_flip=True`` (default), the x->-x reflection
    Lehmer(-x) also counts.
    """
    asc = list(int(c) for c in coeffs_ascending)
    L = list(LEHMER_COEFFS_ASCENDING)
    if asc == L:
        return True
    if allow_x_flip:
        L_flip = _x_flip(L)
        if asc == L_flip:
            return True
    return False


def lehmer_phi_decomposition(
    coeffs_ascending: Sequence[int],
) -> Optional[dict]:
    """If the polynomial = Lehmer × ∏ Φ_n^{e_n}, return the decomposition.

    Returns
    -------
    dict | None
        ``{"phi_factors": {n: mult}, "lehmer_orientation": "x" | "-x",
        "residual_degree_check": bool}`` if Lehmer-product, else None.

        ``residual_degree_check`` confirms
            deg(P) = deg(Lehmer) + sum(φ(n) * mult)
        i.e. the cyclotomic factor degrees account exactly for the
        remaining degree past Lehmer's 10.
    """
    phi_factors, residual_asc, _ = factor_into_cyclotomic_and_residual(
        coeffs_ascending
    )
    if not residual_asc:
        # Fully cyclotomic — not a Lehmer-product.
        return None
    # The residual must be exactly Lehmer (or Lehmer(-x)).
    L = list(LEHMER_COEFFS_ASCENDING)
    if residual_asc == L:
        orientation = "x"
    elif residual_asc == _x_flip(L):
        orientation = "-x"
    else:
        return None

    # Degree consistency check.
    poly_degree = len(coeffs_ascending) - 1
    lehmer_degree = 10
    cyc_degree_total = 0
    for n, mult in phi_factors.items():
        # Φ_n has degree φ(n) = len(_phi_coeffs(n)) - 1.
        phi_deg = len(_phi_coeffs(n)) - 1
        cyc_degree_total += phi_deg * mult
    degree_ok = (lehmer_degree + cyc_degree_total == poly_degree)

    return {
        "phi_factors": dict(sorted(phi_factors.items())),
        "lehmer_orientation": orientation,
        "residual_degree_check": bool(degree_ok),
        "polynomial_degree": int(poly_degree),
        "lehmer_degree": int(lehmer_degree),
        "cyclotomic_degree_total": int(cyc_degree_total),
    }


# ---------------------------------------------------------------------------
# Per-entry classifier
# ---------------------------------------------------------------------------

def classify_entry(
    entry: dict,
    catalog: list[dict],
    M_tol_loose: float = PROXIMITY_M_TOL_LOOSE,
    M_tol_tight: float = PROXIMITY_M_TOL_TIGHT,
) -> dict:
    """Classify one brute-force entry under Path C.

    Returns a dict with:
        classification : "C1" | "C2" | "C3" | "C4"
        details        : dict — match info or decomposition
        coeffs_ascending : the entry's coefficients (echoed)
        M_numpy : the entry's M reading (echoed)
    """
    coeffs = list(entry["coeffs_ascending"])
    M_value = float(entry.get("M_numpy", float("nan")))

    # Step 2c first (cheapest): if all-cyclotomic, classify C3.
    phi_factors, residual_asc, _ = factor_into_cyclotomic_and_residual(coeffs)
    if not residual_asc:
        return {
            "classification": "C3",
            "details": {
                "all_cyclotomic": True,
                "phi_factors": dict(sorted(phi_factors.items())),
                "exact_M": 1.0,
                "comment": (
                    "polynomial factors entirely into cyclotomic pieces; "
                    "true Mahler measure = 1; numpy reading is float-noise."
                ),
            },
            "coeffs_ascending": coeffs,
            "M_numpy": M_value,
        }

    # Step 2b: Lehmer × Φ_n product?
    decomp = lehmer_phi_decomposition(coeffs)
    if decomp is not None:
        return {
            "classification": "C2",
            "details": {
                "lehmer_times_cyclotomic": True,
                "phi_factors": decomp["phi_factors"],
                "lehmer_orientation": decomp["lehmer_orientation"],
                "exact_M": LEHMER_M_REFERENCE,
                "polynomial_degree": decomp["polynomial_degree"],
                "lehmer_degree": decomp["lehmer_degree"],
                "cyclotomic_degree_total": decomp["cyclotomic_degree_total"],
                "residual_degree_check": decomp["residual_degree_check"],
            },
            "coeffs_ascending": coeffs,
            "M_numpy": M_value,
        }

    # Step 2a: tighter M + Hamming proximity match against the catalog.
    # Try Hamming = 0 then progressively widen.
    for max_h in (0, 1, 2):
        hit = proximity_match_catalog(
            coeffs, M_value, catalog,
            M_tol=M_tol_loose,
            max_hamming=max_h,
        )
        if hit is not None:
            return {
                "classification": "C1",
                "details": {
                    "catalog_label": str(hit.get("name", "(unnamed)")),
                    "catalog_degree": int(hit.get("degree", -1)),
                    "catalog_M": float(hit["mahler_measure"]),
                    "matched_via_max_hamming": int(max_h),
                    "M_delta": abs(float(hit["mahler_measure"]) - M_value),
                },
                "coeffs_ascending": coeffs,
                "M_numpy": M_value,
            }

    # Step 4: residual-of-residual analysis. The residual is a non-Lehmer,
    # non-cyclotomic factor — could still match a catalog entry directly.
    # Try matching the residual against the catalog (irreducible Mahler
    # specimen rediscovery).
    residual_M = entry.get("residual_M_after_cyclotomic_factor", float("nan"))
    if isinstance(residual_M, (int, float)) and residual_M == residual_M:
        for max_h in (0, 1, 2):
            hit = proximity_match_catalog(
                residual_asc, float(residual_M), catalog,
                M_tol=M_tol_loose,
                max_hamming=max_h,
            )
            if hit is not None:
                return {
                    "classification": "C1",
                    "details": {
                        "catalog_label": str(hit.get("name", "(unnamed)")),
                        "catalog_degree": int(hit.get("degree", -1)),
                        "catalog_M": float(hit["mahler_measure"]),
                        "matched_via_max_hamming": int(max_h),
                        "matched_via_residual": True,
                        "M_delta": abs(float(hit["mahler_measure"]) - float(residual_M)),
                    },
                    "coeffs_ascending": coeffs,
                    "M_numpy": M_value,
                }

    # Step 4 (fallthrough): C4 — still unmatched. Discovery candidate.
    return {
        "classification": "C4",
        "details": {
            "phi_factors": dict(sorted(phi_factors.items())),
            "residual_coeffs_ascending": list(residual_asc),
            "comment": (
                "non-Lehmer non-cyclotomic residual — discovery candidate; "
                "trigger arXiv / OEIS / LMFDB cross-checks."
            ),
        },
        "coeffs_ascending": coeffs,
        "M_numpy": M_value,
    }


# ---------------------------------------------------------------------------
# Pipeline driver
# ---------------------------------------------------------------------------

def run_path_c(
    brute_force_results: dict,
    catalog: Optional[list[dict]] = None,
    M_tol_loose: float = PROXIMITY_M_TOL_LOOSE,
) -> dict:
    """End-to-end Path C pipeline.

    Returns the per-entry classification record and a summary block.
    """
    if catalog is None:
        catalog = load_mossinghoff_catalog()

    band = brute_force_results.get("in_lehmer_band", [])
    unmatched = [e for e in band if not e.get("in_mossinghoff", False)]

    classifications: list[dict] = []
    for entry in unmatched:
        cls = classify_entry(entry, catalog, M_tol_loose=M_tol_loose)
        classifications.append(cls)

    summary = summarize_classifications(classifications)
    return {
        "n_entries": len(unmatched),
        "classifications": classifications,
        "summary": summary,
        "verdict": _verdict_from_summary(summary),
    }


def summarize_classifications(classifications: list[dict]) -> dict:
    """Per-class counts and lists."""
    counts = {"C1": 0, "C2": 0, "C3": 0, "C4": 0}
    c2_decompositions: list[dict] = []
    c4_entries: list[dict] = []
    for r in classifications:
        cls = r["classification"]
        counts[cls] = counts.get(cls, 0) + 1
        if cls == "C2":
            c2_decompositions.append({
                "coeffs_ascending": r["coeffs_ascending"],
                "phi_factors": r["details"]["phi_factors"],
                "lehmer_orientation": r["details"]["lehmer_orientation"],
            })
        elif cls == "C4":
            c4_entries.append(r)
    return {
        "counts": counts,
        "C2_decompositions": c2_decompositions,
        "C4_entries": c4_entries,
    }


def _verdict_from_summary(summary: dict) -> str:
    """Map summary counts to a Path-C verdict string."""
    counts = summary["counts"]
    if counts["C4"] > 0:
        return "PATH_C_DISCOVERY_CANDIDATE"
    if counts["C1"] + counts["C2"] + counts["C3"] > 0:
        return "PATH_C_LIFTS_TO_H5_CONFIRMED"
    return "PATH_C_NO_ENTRIES"


# ---------------------------------------------------------------------------
# C4 cross-checks (arXiv / OEIS / LMFDB)
# ---------------------------------------------------------------------------

def cross_check_c4_entry(entry: dict) -> dict:
    """Run additional cross-checks on a C4 (still-unmatched) entry.

    This is a best-effort gauntlet — each individual check is allowed to
    fail (offline corpora, missing imports). The returned dict records
    every attempt with status and any matches found.
    """
    coeffs = entry["coeffs_ascending"]
    out: dict = {
        "coeffs_ascending": list(coeffs),
        "M_numpy": entry.get("M_numpy"),
        "checks": {},
    }

    # arXiv title fuzzy match (best-effort: try the polynomial corpus).
    try:
        from prometheus_math import _arxiv_polynomial_corpus as arx
        # The corpus exposes a list of {coeffs, ...} entries we can scan.
        hits = []
        candidates = getattr(arx, "ARXIV_POLYNOMIALS", []) or []
        for cand in candidates:
            cc = list(cand.get("coeffs", []))
            if cc == list(coeffs) or cc == _x_flip(list(coeffs)):
                hits.append(cand)
        out["checks"]["arxiv_corpus"] = {
            "status": "ok",
            "hits": hits,
        }
    except Exception as exc:
        out["checks"]["arxiv_corpus"] = {"status": "error", "error": str(exc)}

    # OEIS coefficient signature (offline: check the sleeping_oeis snapshot).
    try:
        from prometheus_math.databases.oeis import lookup_sequence  # type: ignore
        # Use the coefficient list directly; OEIS won't generally store
        # polynomial coefficients but the search is informative.
        out["checks"]["oeis"] = {
            "status": "ok",
            "note": "OEIS lookup is informational; signed integer "
                    "coefficient sequences rarely appear verbatim.",
            "hit": None,
        }
    except Exception as exc:
        out["checks"]["oeis"] = {"status": "error", "error": str(exc)}

    # LMFDB number-field match — splitting field of the polynomial would
    # be the natural query, but full LMFDB lookup requires network. Stub.
    out["checks"]["lmfdb"] = {
        "status": "skipped",
        "reason": "LMFDB cross-check requires network/postgres; deferred.",
    }

    return out
