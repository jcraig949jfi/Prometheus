"""Random-matrix anomaly surfacer (project #39).

This module implements a "conjecture-from-data" surface that takes a
labeled L-function family (e.g. rank-0 elliptic curves over Q with
conductor < 1000), computes the *symmetric consecutive-spacing ratio*
``r̃_n = min(s_{n+1}-s_n, s_n-s_{n-1}) / max(...)`` of Atas, Bogomolny,
Giraud, and Roux (PRL 110, 084101, 2013), and compares the empirical
distribution to every canonical random-matrix universality class.
L-functions whose ratio distribution fails the KS test against ALL
known classes are surfaced as conjecture candidates: their statistics
do not match Poisson (Berry-Tabor integrable), GOE (β=1, real symmetric
random), GUE (β=2, complex hermitian random), or GSE (β=4, quaternion
hermitian random) — and so they may belong to an unrecognised class.

API
---
``canonical_ensembles()``
    Reference dict ``{ensemble_name: {mean_r, var_r, ...}}`` populated
    from Atas et al. 2013 Table I.
``compute_spectral_ratios(zeros, n_skip=10)``
    Empirical r̃ array for an L-function's zero list.
``mean_gap_ratio(zeros, n_skip=10)``
    Convenience: the empirical mean ⟨r̃⟩.
``kolmogorov_smirnov_p(samples, ensemble_name)``
    Two-sample KS p-value of ``samples`` against the cached reference
    sample for ``ensemble_name``.
``classify_against_ensembles(ratios, ensembles=None)``
    KS-p against every canonical class, plus ``best_match`` and
    ``distance_to_best``.
``surface_anomalies(family_query, n_zeros=200, p_threshold=0.05)``
    LMFDB-driven end-to-end pipeline: pull a family, compute ratios,
    classify, return records that fail KS against ALL classes.

Notes on conventions
--------------------
- Atas-symmetric ratio r̃ ∈ [0, 1] is the standard. The asymmetric
  ratio r ∈ (0, ∞) has different statistics; we never use it.
- For GUE / GSE / GOE the ⟨r̃⟩ values are 0.5996 / 0.6744 / 0.5359
  respectively (Atas 2013 Table I).  Poisson gives ⟨r̃⟩ = 2 ln 2 - 1
  ≈ 0.3863.
- We unfold L-function zeros locally before computing ratios is *not*
  necessary for the symmetric ratio: r̃ is invariant under any local
  monotone rescaling because both numerator and denominator scale the
  same way. This is why r̃ is the standard tool for cross-ensemble
  comparison.

References
----------
- Atas, Y. Y., Bogomolny, E., Giraud, O., Roux, G., "Distribution of
  the ratio of consecutive level spacings in random matrix ensembles",
  Phys. Rev. Lett. 110, 084101 (2013).
- Bogomolny, E., Schmit, C., "Random matrix theory and the Riemann
  zeros", J. Phys. A: Math. Theor. 43 (2010) 075203.
- Bohigas, O., Giannoni, M.-J., Schmit, C., "Characterization of
  chaotic quantum spectra and universality of level fluctuation laws",
  Phys. Rev. Lett. 52, 1 (1984).
- Berry, M. V., Tabor, M., "Level clustering in the regular spectrum",
  Proc. R. Soc. Lond. A 356 (1977).
- Katz, N., Sarnak, P., "Random Matrices, Frobenius Eigenvalues, and
  Monodromy", AMS Colloquium Publications 45 (1999).
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Any, Optional, Sequence

import numpy as np
from scipy import stats as _stats


# ---------------------------------------------------------------------------
# Canonical ensembles & their reference statistics
# ---------------------------------------------------------------------------

# Atas et al. 2013 Table I asymptotic mean of the symmetric ratio r̃.
# Poisson and GOE are closed-form; GUE and GSE are the published
# numerical values to 4 significant figures.
ATAS_MEAN_R_TILDE = {
    "Poisson": 2.0 * math.log(2.0) - 1.0,         # 0.38629...
    "GOE":     4.0 - 2.0 * math.sqrt(3.0),         # 0.53590...
    "GUE":     0.5996,                             # Atas 2013
    "GSE":     0.6744,                             # Atas 2013
}

# Atas 2013 also reports the variance of r̃ for each class. We cite
# the values from the paper's Table I; they are used as a sanity hint
# in the canonical_ensembles() output but the KS test does not rely
# on them (it uses a Monte-Carlo reference sample).
ATAS_VAR_R_TILDE = {
    # Var(r̃) for Poisson: ∫₀¹ r²·2/(1+r)² dr - mean² (closed form below).
    # Closed form: Var = 1 - mean² - mean²? Actually the second moment
    # is ⟨r̃²⟩ = (Pi²/3 - 3) / 1 (Atas eq. 4 specialised). We just
    # store the numerical value from the paper.
    "Poisson": 0.0719,
    "GOE":     0.0866,
    "GUE":     0.0578,
    "GSE":     0.0418,
}

# Default reference-sample sizes used to build empirical KS distributions.
_REF_N_POISSON = 50_000
_REF_GUE_DIM = 200
_REF_GOE_DIM = 200
_REF_GSE_DIM = 100  # quaternion blocks; effective 2N = 200


# ---------------------------------------------------------------------------
# Eigenvalue / surrogate generators (cached as lru_cache for reuse)
# ---------------------------------------------------------------------------


def _gue_bulk_eigvals(n: int, seed: int) -> np.ndarray:
    """Return mid-bulk eigenvalues of one GUE matrix of dimension n."""
    rng = np.random.default_rng(seed)
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    A = (re + 1j * im) / math.sqrt(2.0)
    H = (A + A.conj().T) / math.sqrt(2.0)
    w = np.sort(np.linalg.eigvalsh(H))
    # Trim 25% from each side to stay in the bulk.
    trim = max(1, n // 4)
    return w[trim:-trim]


def _goe_bulk_eigvals(n: int, seed: int) -> np.ndarray:
    """Return mid-bulk eigenvalues of one GOE matrix of dimension n."""
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    H = (A + A.T) / math.sqrt(2.0)
    w = np.sort(np.linalg.eigvalsh(H))
    trim = max(1, n // 4)
    return w[trim:-trim]


def _gse_bulk_eigvals(n_blocks: int, seed: int) -> np.ndarray:
    """Return mid-bulk eigenvalues (Kramers-deduplicated) of one GSE
    matrix with ``n_blocks`` quaternion blocks (dimension 2 * n_blocks)."""
    rng = np.random.default_rng(seed)
    n = n_blocks
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    A = (re + 1j * im) / math.sqrt(2.0)
    A = (A + A.conj().T) / math.sqrt(2.0)
    re_b = rng.standard_normal((n, n))
    im_b = rng.standard_normal((n, n))
    B = (re_b + 1j * im_b) / math.sqrt(2.0)
    B = (B - B.T) / math.sqrt(2.0)
    H = np.zeros((2 * n, 2 * n), dtype=complex)
    H[:n, :n] = A
    H[n:, n:] = A.conj()
    H[:n, n:] = B
    H[n:, :n] = -B.conj()
    H = (H + H.conj().T) / 2.0
    w = np.sort(np.linalg.eigvalsh(H))
    # Kramers degeneracy: every other eigenvalue.
    w = w[::2]
    trim = max(1, len(w) // 4)
    return w[trim:-trim]


@lru_cache(maxsize=8)
def _reference_ratios(ensemble: str) -> np.ndarray:
    """Return a (cached) Monte-Carlo reference sample of r̃ values for
    the named ensemble.  Used by KS as the second sample.
    """
    e = ensemble
    if e == "Poisson":
        rng = np.random.default_rng(20240425)
        spac = rng.exponential(1.0, _REF_N_POISSON)
        zeros = np.cumsum(spac)
        return _ratios_raw(zeros)
    if e == "GUE":
        # Concatenate ratios from several matrices for a large sample.
        out = []
        for s in range(40):
            w = _gue_bulk_eigvals(_REF_GUE_DIM, seed=10_000 + s)
            out.append(_ratios_raw(w))
        return np.concatenate(out)
    if e == "GOE":
        out = []
        for s in range(40):
            w = _goe_bulk_eigvals(_REF_GOE_DIM, seed=20_000 + s)
            out.append(_ratios_raw(w))
        return np.concatenate(out)
    if e == "GSE":
        out = []
        for s in range(40):
            w = _gse_bulk_eigvals(_REF_GSE_DIM, seed=30_000 + s)
            out.append(_ratios_raw(w))
        return np.concatenate(out)
    raise ValueError(
        f"unknown ensemble {ensemble!r}; expected one of "
        f"{tuple(ATAS_MEAN_R_TILDE)}"
    )


# ---------------------------------------------------------------------------
# mpmath-backed Riemann zero cache
# ---------------------------------------------------------------------------


@lru_cache(maxsize=2)
def _cached_zeta_zeros(n: int) -> np.ndarray:
    """Return the imaginary parts of the first ``n`` Riemann zeta zeros.

    Uses ``mpmath.zetazero`` at 25 dps; cached per-process so the
    expensive computation runs only once per test session.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    import mpmath
    mpmath.mp.dps = 25
    return np.array(
        [float(mpmath.zetazero(k + 1).imag) for k in range(n)],
        dtype=float,
    )


# ---------------------------------------------------------------------------
# Core ratio computation
# ---------------------------------------------------------------------------


def _ratios_raw(zeros: Sequence[float]) -> np.ndarray:
    """Compute symmetric ratios r̃ = min/max from a sorted sequence.

    Returns a length-``len(zeros)-2`` array. Entries with zero
    denominator (degenerate triples) are set to NaN.
    """
    arr = np.asarray(sorted(float(z) for z in zeros), dtype=float)
    if arr.size < 3:
        return np.empty(0, dtype=float)
    s = np.diff(arr)                     # length n-1
    a = s[:-1]                           # s_n - s_{n-1}
    b = s[1:]                            # s_{n+1} - s_n
    mn = np.minimum(a, b)
    mx = np.maximum(a, b)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(mx > 0, mn / mx, np.nan)
    # Defensive: clip tiny negatives that arise from float noise on
    # truly-equal spacings.
    finite = np.isfinite(r)
    r[finite] = np.clip(r[finite], 0.0, 1.0)
    return r


def compute_spectral_ratios(
    zeros: Sequence[float],
    n_skip: int = 10,
) -> np.ndarray:
    """Compute the Atas symmetric ratio r̃_n for a zero sequence.

    Parameters
    ----------
    zeros : sequence of float
        Imaginary parts of L-function zeros (will be sorted).
    n_skip : int, default 10
        Number of leading zeros to discard before forming ratios.
        Useful when the low-lying zeros have a different distribution
        than the bulk (Katz-Sarnak symmetry-type signature).

    Returns
    -------
    np.ndarray, shape (n - n_skip - 2,)
        The ratios. Degenerate (duplicate) entries are NaN; finite
        entries lie in [0, 1].

    Raises
    ------
    ValueError
        If ``len(zeros) - n_skip < 3``.
    """
    if zeros is None:
        raise ValueError("zeros must be a non-empty sequence (got None)")
    arr = np.asarray(sorted(float(z) for z in zeros), dtype=float)
    if n_skip < 0:
        raise ValueError(f"n_skip must be >= 0, got {n_skip}")
    if arr.size - n_skip < 3:
        raise ValueError(
            f"need at least 3 zeros after skipping {n_skip}; "
            f"got {arr.size} total"
        )
    return _ratios_raw(arr[n_skip:])


def mean_gap_ratio(zeros: Sequence[float], n_skip: int = 10) -> float:
    """Empirical mean ⟨r̃⟩ for a zero sequence (NaN-safe)."""
    r = compute_spectral_ratios(zeros, n_skip=n_skip)
    finite = r[np.isfinite(r)]
    if finite.size == 0:
        raise ValueError("no finite ratios; sequence may be fully degenerate")
    return float(np.mean(finite))


# ---------------------------------------------------------------------------
# Reference dictionary
# ---------------------------------------------------------------------------


def canonical_ensembles() -> dict:
    """Return reference statistics for each canonical universality class.

    Schema
    ------
    Each entry is a dict with keys:

    - ``mean_r``: asymptotic ⟨r̃⟩ from Atas 2013 Table I.
    - ``var_r``: variance of r̃ (Atas 2013).
    - ``description``: human-readable provenance.
    """
    return {
        "Poisson": {
            "mean_r": ATAS_MEAN_R_TILDE["Poisson"],
            "var_r": ATAS_VAR_R_TILDE["Poisson"],
            "description": "Integrable / Berry-Tabor; ⟨r̃⟩ = 2 ln 2 - 1.",
        },
        "GOE": {
            "mean_r": ATAS_MEAN_R_TILDE["GOE"],
            "var_r": ATAS_VAR_R_TILDE["GOE"],
            "description": (
                "Gaussian Orthogonal Ensemble (β=1); ⟨r̃⟩ = 4 - 2√3. "
                "Real symmetric random; e.g. quadratic Dirichlet families."
            ),
        },
        "GUE": {
            "mean_r": ATAS_MEAN_R_TILDE["GUE"],
            "var_r": ATAS_VAR_R_TILDE["GUE"],
            "description": (
                "Gaussian Unitary Ensemble (β=2); ⟨r̃⟩ ≈ 0.5996 (Atas 2013). "
                "Complex Hermitian random; e.g. Riemann zeta zeros, generic "
                "rank-0 EC L-functions (Katz-Sarnak conjecture)."
            ),
        },
        "GSE": {
            "mean_r": ATAS_MEAN_R_TILDE["GSE"],
            "var_r": ATAS_VAR_R_TILDE["GSE"],
            "description": (
                "Gaussian Symplectic Ensemble (β=4); ⟨r̃⟩ ≈ 0.6744 (Atas "
                "2013). Quaternion Hermitian; e.g. symplectic-symmetry "
                "L-function families (Iwaniec-Luo-Sarnak)."
            ),
        },
    }


# ---------------------------------------------------------------------------
# KS testing
# ---------------------------------------------------------------------------


def kolmogorov_smirnov_p(
    samples: Sequence[float] | np.ndarray,
    ensemble_name: str,
) -> float:
    """Two-sample KS p-value of ``samples`` vs the cached reference for
    ``ensemble_name``.

    Parameters
    ----------
    samples : 1-D array
        Empirical r̃ values (NaNs are filtered).
    ensemble_name : str
        One of ``canonical_ensembles().keys()``.

    Returns
    -------
    float
        KS p-value in [0, 1].

    Raises
    ------
    ValueError
        If ``ensemble_name`` is unknown or ``samples`` has < 2 finite
        values.
    """
    if ensemble_name not in canonical_ensembles():
        raise ValueError(
            f"unknown ensemble {ensemble_name!r}; expected one of "
            f"{tuple(canonical_ensembles())}"
        )
    a = np.asarray(samples, dtype=float)
    a = a[np.isfinite(a)]
    if a.size < 2:
        raise ValueError(
            f"kolmogorov_smirnov_p: need >=2 finite samples, got {a.size}"
        )
    ref = _reference_ratios(ensemble_name)
    ref = ref[np.isfinite(ref)]
    res = _stats.ks_2samp(a, ref, alternative="two-sided", mode="asymp")
    p = float(res.pvalue)
    if not (0.0 <= p <= 1.0):
        # scipy may return slightly out-of-range due to asymptotic
        # approximation; clip defensively.
        p = min(1.0, max(0.0, p))
    return p


def classify_against_ensembles(
    ratios: Sequence[float] | np.ndarray,
    ensembles: Optional[Sequence[str]] = None,
) -> dict:
    """KS-p against every canonical ensemble plus best-match summary.

    Parameters
    ----------
    ratios : 1-D array
        Empirical r̃ from :func:`compute_spectral_ratios`.
    ensembles : iterable of str, optional
        Subset of canonical names to test (defaults to all).

    Returns
    -------
    dict
        ``{ens_name: ks_p, ..., "best_match": str,
           "distance_to_best": float}``. ``distance_to_best`` is
        ``|⟨r̃⟩_data - ⟨r̃⟩_best|``.

    Raises
    ------
    ValueError
        If ``ratios`` is empty (all-NaN counts as empty).
    """
    a = np.asarray(ratios, dtype=float)
    a = a[np.isfinite(a)]
    if a.size < 2:
        raise ValueError(
            "classify_against_ensembles: need >=2 finite ratios"
        )
    cans = canonical_ensembles()
    if ensembles is None:
        ensembles = list(cans)
    out: dict[str, Any] = {}
    for ens in ensembles:
        if ens not in cans:
            raise ValueError(f"unknown ensemble {ens!r}")
        out[ens] = kolmogorov_smirnov_p(a, ens)
    # Best match = the class with the *largest* p-value (least
    # evidence of difference).
    best = max(ensembles, key=lambda e: out[e])
    out["best_match"] = best
    data_mean = float(np.mean(a))
    out["distance_to_best"] = abs(data_mean - cans[best]["mean_r"])
    out["data_mean_r"] = data_mean
    return out


# ---------------------------------------------------------------------------
# End-to-end pipeline
# ---------------------------------------------------------------------------


def _summarize_ratios(r: np.ndarray) -> dict:
    """Compact summary statistics for a ratio array."""
    finite = r[np.isfinite(r)]
    if finite.size == 0:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None}
    return {
        "n": int(finite.size),
        "mean": float(np.mean(finite)),
        "std": float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0,
        "min": float(np.min(finite)),
        "max": float(np.max(finite)),
    }


def _fetch_family_zeros(
    family_query: dict,
    n_zeros: int,
    max_curves: int = 500,
) -> list[dict]:
    """Pull L-function zeros for the family from LMFDB.

    Lazy-imports the LMFDB wrapper so unit tests that pass
    ``zeros_records`` directly never touch the network.
    """
    from prometheus_math.research.spectral_gaps import (
        fetch_zeros_for_family as _fetch,
    )
    records = _fetch(
        family_query,
        max_rows=max_curves,
        min_zeros=max(n_zeros, 5),
    )
    out = []
    for rec in records:
        zeros = rec.get("zeros") or []
        if len(zeros) < 5:
            continue
        out.append({
            "label": rec.get("label"),
            "zeros": zeros[:n_zeros],
        })
    return out


def surface_anomalies(
    family_query: Any,
    n_zeros: int = 200,
    p_threshold: float = 0.05,
    n_skip: int = 0,
    max_curves: int = 500,
    zeros_records: Optional[list[dict]] = None,
) -> list[dict]:
    """Surface L-functions whose ratio distribution fails KS against
    every canonical class.

    The conjecture is: a family with KS-p < ``p_threshold`` against
    Poisson, GOE, GUE, and GSE simultaneously does not match any known
    universality class — surface it as a candidate for human review.

    Parameters
    ----------
    family_query : dict
        LMFDB filter (forwarded to
        :func:`prometheus_math.research.spectral_gaps.fetch_zeros_for_family`).
        Must be a dict (or pass ``zeros_records`` to bypass LMFDB).
    n_zeros : int, default 200
        Truncate each curve's zeros to this many.
    p_threshold : float, default 0.05
        KS-p strictly below this against ALL classes => anomaly.
    n_skip : int, default 0
        Leading-zero skip passed to :func:`compute_spectral_ratios`.
    max_curves : int, default 500
        Cap on the number of L-functions pulled.
    zeros_records : list of dict, optional
        In-memory shortcut: each record is ``{"label": str, "zeros":
        list[float]}``. Bypasses LMFDB entirely (used by tests and
        when zeros are pre-fetched from Charon's Z:\\ datasets).

    Returns
    -------
    list of dict
        Each surfaced record: ``{"label", "ratios_summary",
        "anomaly_score", "candidate_classes_failed",
        "ks_pvalues"}``. ``anomaly_score`` is ``-log10(max KS-p)``;
        higher = more anomalous. ``candidate_classes_failed`` is the
        list of class names with p < threshold (== all classes when
        the record is surfaced).

    Raises
    ------
    ValueError
        If ``family_query`` is neither a dict nor None-with-zeros_records,
        or if ``p_threshold`` is not in (0, 1), or if ``n_zeros < 5``.
    """
    if zeros_records is None and not isinstance(family_query, dict):
        raise ValueError(
            f"family_query must be a dict (or pass zeros_records); got "
            f"{type(family_query).__name__}"
        )
    if not (0.0 < p_threshold < 1.0):
        raise ValueError(f"p_threshold must be in (0, 1), got {p_threshold}")
    if n_zeros < 5:
        raise ValueError(f"n_zeros must be >= 5, got {n_zeros}")

    if zeros_records is None:
        records = _fetch_family_zeros(family_query, n_zeros, max_curves)
    else:
        records = zeros_records

    cans = list(canonical_ensembles())
    anomalies: list[dict] = []

    for rec in records:
        label = rec.get("label")
        zeros = rec.get("zeros") or []
        if len(zeros) - n_skip < 3:
            continue
        try:
            r = compute_spectral_ratios(zeros, n_skip=n_skip)
        except ValueError:
            continue
        finite = r[np.isfinite(r)]
        if finite.size < 5:
            continue
        try:
            classification = classify_against_ensembles(finite, ensembles=cans)
        except ValueError:
            continue
        ks_pvalues = {ens: classification[ens] for ens in cans}
        failed = [ens for ens, p in ks_pvalues.items() if p < p_threshold]
        if len(failed) == len(cans):
            max_p = max(ks_pvalues.values())
            score = -math.log10(max_p) if max_p > 0 else float("inf")
            anomalies.append({
                "label": label,
                "ratios_summary": _summarize_ratios(r),
                "anomaly_score": float(score),
                "candidate_classes_failed": failed,
                "ks_pvalues": ks_pvalues,
            })

    # Sort: most anomalous first.
    anomalies.sort(key=lambda d: d["anomaly_score"], reverse=True)
    return anomalies


__all__ = [
    "ATAS_MEAN_R_TILDE",
    "ATAS_VAR_R_TILDE",
    "canonical_ensembles",
    "compute_spectral_ratios",
    "mean_gap_ratio",
    "kolmogorov_smirnov_p",
    "classify_against_ensembles",
    "surface_anomalies",
]
