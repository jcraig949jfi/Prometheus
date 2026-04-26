"""Spectral-gap-k scan over L-function families vs random-matrix nulls.

This module generalizes Ergon's gap-k scan (``ergon/gap_k_scan.py``,
``ergon/cm_gap_k_scan.py``, ``ergon/g2c_gap_k_scan.py``) to a single
reusable surface.  The thesis under test (F011) is that L-function
zero-spacing variances are *compressed* relative to the appropriate
matched random-matrix ensemble (Katz-Sarnak symmetry type), and that
the compression depth varies with the gap index ``k``.

Pipeline
--------
1. ``fetch_zeros_for_family(family_query)`` queries
   ``lfunc_lfunctions`` via :mod:`prometheus_math.databases.lmfdb`
   and returns one record per L-function with the first ``~24`` zeros
   plus identifying metadata.
2. ``normalize_zeros(zeros, mode='local-4-gap')`` converts a single
   sequence of zeros to a sequence of *normalized spacings* whose
   mean over the chosen window equals 1.
3. ``gap_k_variance(spacings, k)`` returns the empirical variance of
   the k-th gap distribution.
4. ``matched_null(N, n_samples, ensemble='GUE')`` returns a sample of
   gap distributions drawn from the matching random-matrix ensemble.
5. ``scan(family_query, k_max, ...)`` chains the above; returns a
   per-k dict of (data_var, null_var, deficit_pct, z_score).
6. ``bootstrap_ci(values, null_values, ...)`` returns a CI on the
   deficit using a resampling bootstrap.
7. ``figure(scan_result)`` renders a 4-panel matplotlib figure
   suitable for the paper-track Axis 3b.

Random-matrix recipes
---------------------
- **GUE / β=2**: H = (A + A†)/2 with A complex iid N(0,1) — matches the
  Mehta book §1.5 convention.
- **GOE / β=1**: H = (A + A^T)/2 with A real iid N(0,1).
- **GSE / β=4**: quaternion-real Hermitian via 2×2 quaternion blocks.
  Used for ``USp(2N)`` in the Katz-Sarnak family of finite N (we use
  N=2, i.e. matrices of degree 4).
- **CUE**: Haar-uniform unitary via QR of a complex Ginibre matrix
  (Mezzadri, Notices AMS 2007). Eigenvalues lie on the unit circle;
  we unfold to the bulk for gap statistics.
- **O+ / O-**: Haar-uniform real orthogonal, split by det = ±1.
  In the bulk both reduce to GOE statistics.

Wigner surmise reference values (mean-spacing-1):

.. math::

    \\mathrm{Var}_{GOE}(s) = 4/\\pi - 1 \\approx 0.2732

    \\mathrm{Var}_{GUE}(s) = 3\\pi/8 - 1 \\approx 0.1781

    \\mathrm{Var}_{GSE}(s) = 45\\pi/128 - 1 \\approx 0.1042

These are used by the authority test in
``test_spectral_gaps.py`` to validate the matched-null generator at
sample size 10K.

References
----------
- Mehta, M. L., *Random Matrices*, 3rd ed., 2004.  Ch. 1, 6.
- Katz & Sarnak, *Random Matrices, Frobenius Eigenvalues, and
  Monodromy*, 1999.  AMS Colloquium Publications 45.
- Mezzadri, F., "How to Generate Random Matrices from the Classical
  Compact Groups", *Notices AMS*, vol. 54 no. 5, 2007.
- Iwaniec, Luo, Sarnak, "Low lying zeros of families of L-functions",
  IHES Pub. Math. 91, 2000.
"""
from __future__ import annotations

import json
import math
from typing import Any, Iterable, Optional, Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Constants & supported ensembles
# ---------------------------------------------------------------------------

K_DEFAULT_MAX = 24
N_DEFAULT_NULL_MATRICES = 1000
N_DEFAULT_MATRIX_SIZE = 40

SUPPORTED_ENSEMBLES = ("GUE", "GOE", "GSE", "CUE", "USp(4)", "O+", "O-")

# Wigner surmise variances (mean-spacing-1 normalization). These are the
# classical small-N approximations; the bulk N→∞ values are
# numerically very close (typically <0.5% off).
WIGNER_SURMISE_VARIANCE = {
    "GOE": 4.0 / math.pi - 1.0,                 # ≈ 0.27324
    "GUE": 3.0 * math.pi / 8.0 - 1.0,           # ≈ 0.17810
    "GSE": 45.0 * math.pi / 128.0 - 1.0,        # ≈ 0.10416
}


# ---------------------------------------------------------------------------
# Zero fetching from LMFDB
# ---------------------------------------------------------------------------


def _parse_zeros(raw: Any) -> Optional[list[float]]:
    """Parse a Postgres-encoded zero list to a Python list of floats.

    LMFDB stores zeros as either JSON arrays (text/jsonb) or Postgres
    arrays. The wrapper in
    :func:`prometheus_math.databases.lmfdb.lfunctions` already converts
    most cases to ``list``; this helper handles the residual stringy
    cases for safety.
    """
    if raw is None:
        return None
    if isinstance(raw, list):
        try:
            return [float(z) for z in raw]
        except (TypeError, ValueError):
            return None
    s = str(raw).strip()
    if s in ("", "[]", "{}", "None"):
        return None
    s = s.replace("{", "[").replace("}", "]")
    try:
        return [float(z) for z in json.loads(s)]
    except Exception:
        return None


def fetch_zeros_for_family(
    family_query: dict,
    max_rows: int = 1000,
    min_zeros: int = K_DEFAULT_MAX + 1,
    conn: Optional[Any] = None,
) -> list[dict]:
    """Fetch L-function zeros from ``lfunc_lfunctions`` for a family.

    Parameters
    ----------
    family_query : dict
        Keyword filters forwarded to
        :func:`prometheus_math.databases.lmfdb.lfunctions`.  Any
        combination of ``origin`` (LIKE-pattern), ``degree``,
        ``conductor``, ``order_of_vanishing``.
    max_rows : int, default 1000
        Hard cap on rows returned.
    min_zeros : int
        Drop rows with fewer than this many zeros (default 25,
        i.e. enough for ``k_max=24``).
    conn : optional psycopg2 connection
        Reuse a connection across calls.

    Returns
    -------
    list[dict]
        Each row has at least ``label``, ``origin``, ``conductor``,
        ``order_of_vanishing``, ``zeros`` (list[float], length ≥
        ``min_zeros``).
    """
    # Lazy import: keep matplotlib / lmfdb / psycopg2 optional for tests
    # that don't touch the network.
    from prometheus_math.databases import lmfdb as _lmfdb  # noqa: WPS433

    rows = _lmfdb.lfunctions(
        with_zeros=True,
        limit=int(max_rows),
        conn=conn,
        **{k: v for k, v in family_query.items() if v is not None},
    )

    out: list[dict] = []
    for row in rows:
        zeros = _parse_zeros(row.get("positive_zeros"))
        if zeros is None or len(zeros) < min_zeros:
            continue
        rec = {
            "label": row.get("label"),
            "origin": row.get("origin"),
            "conductor": row.get("conductor"),
            "order_of_vanishing": row.get("order_of_vanishing"),
            "zeros": zeros[:max(min_zeros, K_DEFAULT_MAX + 1)],
        }
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_zeros(
    zeros: Sequence[float],
    mode: str = "local-4-gap",
) -> list[float]:
    """Compute normalized spacings of a zero sequence.

    Modes
    -----
    ``'global'``
        Spacings ``g_i = z_{i+1} - z_i`` divided by the mean of *all*
        spacings.
    ``'local-Nk'``
        Take the first ``Nk`` spacings (default ``Nk=24`` via
        ``mode='local-24-gap'``), divide each by the *local* mean.
        This was Aporia's protocol after the April 22 reframing.
    ``'local-4-gap'``
        Convenience alias for ``'local-4-gap'`` — first 4 spacings,
        normalized by their local mean.

    Returns
    -------
    list[float]
        Normalized spacings. ``mean(result) == 1`` over the relevant
        window by construction.

    Raises
    ------
    ValueError
        If ``zeros`` has fewer than 2 elements (no spacings exist),
        if ``mode`` is not recognized, or if the local-window mean is
        non-positive (e.g. duplicated zeros).
    """
    if zeros is None:
        raise ValueError("zeros must be a non-empty sequence (got None)")
    z = sorted(float(x) for x in zeros)
    if len(z) < 2:
        raise ValueError(
            f"normalize_zeros requires >=2 zeros to define a spacing, got {len(z)}"
        )
    spacings = np.diff(np.asarray(z, dtype=float))

    m = mode.lower()
    if m == "global":
        mean = spacings.mean()
        if mean <= 0:
            raise ValueError("global mean spacing is non-positive")
        return (spacings / mean).tolist()

    if m.startswith("local-") and m.endswith("-gap"):
        try:
            nk = int(m[len("local-"):-len("-gap")])
        except ValueError as e:
            raise ValueError(f"could not parse Nk from mode={mode!r}") from e
        if nk < 2:
            raise ValueError(f"local window must be >= 2, got {nk}")
        if len(spacings) < nk:
            raise ValueError(
                f"need at least {nk} spacings for mode={mode!r}, got {len(spacings)}"
            )
        window = spacings[:nk]
        mean = window.mean()
        if mean <= 0:
            raise ValueError(f"local-{nk} mean spacing is non-positive")
        return (window / mean).tolist()

    raise ValueError(
        f"unknown normalization mode {mode!r}; "
        f"expected 'global' or 'local-Nk-gap'"
    )


# ---------------------------------------------------------------------------
# Gap statistics
# ---------------------------------------------------------------------------


def gap_k_variance(normalized_spacings: Sequence[float], k: int = 1) -> float:
    """Return the empirical variance of the k-th normalized spacing.

    For a 1-D sequence, the "k-th gap" is the spacing at index ``k-1``
    (zero-based), i.e. the gap between the k-th and (k+1)-th zeros.
    To compute *the variance over a sample of curves*, call this on a
    1-D array of "k-th gaps across curves".

    Convention: when given a flat list of spacings (length N), this
    returns ``var(spacings)`` over the whole list (interpretable as
    "all-gaps variance"). For per-k variances over a curve sample,
    pass an array of shape ``(n_curves,)`` containing the k-th gap
    of each curve.

    Parameters
    ----------
    normalized_spacings : array_like
        1-D array of normalized spacings.
    k : int
        For 2-D input (n_curves × n_gaps), select the k-th gap before
        taking the variance. For 1-D input, ``k`` is ignored except
        that ``k`` must satisfy ``1 <= k <= len`` (else ValueError).

    Returns
    -------
    float
        Empirical (unbiased) variance.

    Raises
    ------
    ValueError
        If the input is empty or 1-element, or k is out of range.
    """
    arr = np.asarray(normalized_spacings, dtype=float)
    if arr.size == 0:
        raise ValueError("gap_k_variance: input is empty")
    if arr.ndim == 2:
        if not (1 <= k <= arr.shape[1]):
            raise ValueError(
                f"k={k} out of range for shape {arr.shape}"
            )
        col = arr[:, k - 1]
        if col.size < 2:
            raise ValueError(
                "gap_k_variance: need >=2 samples to estimate variance"
            )
        return float(np.var(col, ddof=1))
    if arr.ndim != 1:
        raise ValueError(f"gap_k_variance: bad input ndim={arr.ndim}")
    if arr.size < 2:
        raise ValueError(
            "gap_k_variance: need >=2 spacings to estimate variance"
        )
    if not (1 <= k <= arr.size):
        raise ValueError(f"k={k} out of range for length {arr.size}")
    return float(np.var(arr, ddof=1))


# ---------------------------------------------------------------------------
# Random-matrix-ensemble null generators
# ---------------------------------------------------------------------------


def _gue_eigvals(n: int, rng: np.random.Generator) -> np.ndarray:
    """Sorted eigenvalues of a single GUE matrix of size n."""
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    A = (re + 1j * im) / math.sqrt(2.0)
    H = (A + A.conj().T) / math.sqrt(2.0)
    return np.sort(np.linalg.eigvalsh(H))


def _goe_eigvals(n: int, rng: np.random.Generator) -> np.ndarray:
    """Sorted eigenvalues of a single GOE matrix of size n."""
    A = rng.standard_normal((n, n))
    H = (A + A.T) / math.sqrt(2.0)
    return np.sort(np.linalg.eigvalsh(H))


def _gse_eigvals(n_quaternion_blocks: int, rng: np.random.Generator) -> np.ndarray:
    """Sorted eigenvalues of a single GSE matrix.

    The matrix is 2n × 2n complex Hermitian with the quaternion-real
    structure ``H = [[A, B], [-B*, A*]]`` where A is Hermitian and B
    is anti-symmetric. Each eigenvalue appears with multiplicity 2
    (Kramers degeneracy); we de-duplicate before returning.
    """
    n = n_quaternion_blocks
    # A: complex Hermitian
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    A = (re + 1j * im) / math.sqrt(2.0)
    A = (A + A.conj().T) / math.sqrt(2.0)
    # B: complex skew-symmetric (B^T = -B)
    re_b = rng.standard_normal((n, n))
    im_b = rng.standard_normal((n, n))
    B = (re_b + 1j * im_b) / math.sqrt(2.0)
    B = (B - B.T) / math.sqrt(2.0)
    H = np.zeros((2 * n, 2 * n), dtype=complex)
    H[:n, :n] = A
    H[n:, n:] = A.conj()
    H[:n, n:] = B
    H[n:, :n] = -B.conj()
    H = (H + H.conj().T) / 2.0  # numerical symmetrization
    w = np.linalg.eigvalsh(H)
    # Kramers: pair-wise degenerate to numerical precision.
    # Take every other eigenvalue.
    w = np.sort(w)
    return w[::2]


def _haar_unitary(n: int, rng: np.random.Generator) -> np.ndarray:
    """Haar-distributed unitary matrix of size n (Mezzadri 2007)."""
    re = rng.standard_normal((n, n))
    im = rng.standard_normal((n, n))
    Z = (re + 1j * im) / math.sqrt(2.0)
    Q, R = np.linalg.qr(Z)
    d = np.diag(R)
    ph = d / np.abs(d)
    return Q * ph  # broadcasts on columns


def _haar_orthogonal(n: int, rng: np.random.Generator) -> np.ndarray:
    """Haar-distributed orthogonal matrix of size n (Mezzadri 2007)."""
    Z = rng.standard_normal((n, n))
    Q, R = np.linalg.qr(Z)
    d = np.diag(R)
    ph = np.sign(d)
    ph[ph == 0] = 1.0
    return Q * ph


def _cue_eigangles(n: int, rng: np.random.Generator) -> np.ndarray:
    """Sorted eigenphases (in [0, 2π)) of a Haar unitary."""
    U = _haar_unitary(n, rng)
    w = np.linalg.eigvals(U)
    angles = np.mod(np.angle(w), 2 * math.pi)
    return np.sort(angles)


def _orthogonal_eigvals_with_sign(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, int]:
    """Return (sorted real eigenvalues of Haar-orthogonal, det sign).

    For O(n) the eigenvalues come in conjugate pairs e^{±iθ} (and ±1
    for fixed points). We return the *eigenangles* in [0, π] of the
    upper-half pairs, which is the standard 'unfolded angles' for
    bulk gap statistics.
    """
    Q = _haar_orthogonal(n, rng)
    w = np.linalg.eigvals(Q)
    sign = int(round(np.real(np.linalg.det(Q))))
    angles = np.angle(w)
    angles = angles[(angles > 1e-9) & (angles < math.pi - 1e-9)]
    return np.sort(angles), sign


def _ensemble_one_sample_gaps(
    ensemble: str,
    N: int,
    kmax: int,
    rng: np.random.Generator,
) -> Optional[np.ndarray]:
    """Return one length-`kmax` array of locally-normalized mid-bulk gaps.

    Returns None if the sample is degenerate (e.g. wrong-determinant
    Haar orthogonal sample for O+/O-).
    """
    e = ensemble.upper().replace(" ", "")
    if e == "GUE":
        w = _gue_eigvals(N, rng)
    elif e == "GOE":
        w = _goe_eigvals(N, rng)
    elif e == "GSE":
        # n_quaternion_blocks=N produces 2N complex eigenvalues, of which
        # N are distinct after Kramers de-duplication. Use at least
        # kmax+5 blocks so we always have enough mid-bulk gaps.
        nq = max(kmax + 5, N)
        w = _gse_eigvals(nq, rng)
    elif e == "USP(4)":
        # Katz-Sarnak USp(4): 4×4 symplectic matrices.
        # Bulk statistics → GSE in the Mehta classification (β=4).
        # The literal degree-4 case has only 2 mid-bulk eigenvalue
        # pairs which is far too few for the kmax window; we sample
        # GSE at the block dimension dictated by kmax / N (the
        # Katz-Sarnak claim is about the universal bulk statistics,
        # not about literal 4×4 matrices).
        nq = max(kmax + 5, N)
        w = _gse_eigvals(nq, rng)
    elif e == "CUE":
        w = _cue_eigangles(N, rng)
    elif e == "O+":
        w, sgn = _orthogonal_eigvals_with_sign(N, rng)
        if sgn != 1:
            return None
    elif e == "O-":
        w, sgn = _orthogonal_eigvals_with_sign(N, rng)
        if sgn != -1:
            return None
    else:
        raise ValueError(
            f"unsupported ensemble {ensemble!r}; "
            f"expected one of {SUPPORTED_ENSEMBLES}"
        )
    if len(w) < kmax + 1:
        return None
    mid = max(0, len(w) // 2 - kmax // 2)
    gaps = np.diff(w)[mid:mid + kmax]
    if len(gaps) < kmax:
        return None
    m = gaps.mean()
    if m <= 0:
        return None
    return gaps / m


def matched_null(
    N: int = N_DEFAULT_MATRIX_SIZE,
    n_samples: int = N_DEFAULT_NULL_MATRICES,
    ensemble: str = "GUE",
    kmax: int = K_DEFAULT_MAX,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Generate a matched random-matrix-ensemble null sample.

    Parameters
    ----------
    N : int
        Matrix size for the chosen ensemble. For O± / CUE this is the
        size of the orthogonal / unitary matrix; for GUE/GOE/GSE it is
        the matrix dimension; for USp(4) the convention follows
        Katz-Sarnak (4×4 symplectic, but we use the equivalent GSE
        recipe at degree ``N//2``).
    n_samples : int
        Number of sampled gap-blocks (each of length ``kmax``).
    ensemble : str
        One of :data:`SUPPORTED_ENSEMBLES`.
    kmax : int
        Number of consecutive mid-bulk gaps to return per sample.
    rng : numpy.random.Generator, optional
        Seeded RNG.

    Returns
    -------
    np.ndarray, shape (n_samples_collected, kmax)
        Each row is a length-``kmax`` array of locally-normalized
        spacings (so each row's mean equals 1). ``n_samples_collected``
        may be < ``n_samples`` if the ensemble has rejection (O+/O-).

    Raises
    ------
    ValueError
        If ``ensemble`` is not supported, or N / kmax / n_samples are
        non-positive.
    """
    if ensemble.upper().replace(" ", "") not in {
        e.upper().replace(" ", "") for e in SUPPORTED_ENSEMBLES
    }:
        raise ValueError(
            f"unsupported ensemble {ensemble!r}; "
            f"expected one of {SUPPORTED_ENSEMBLES}"
        )
    if N < 4:
        raise ValueError(f"matrix size N must be >=4, got {N}")
    if n_samples <= 0:
        raise ValueError(f"n_samples must be positive, got {n_samples}")
    if kmax <= 0:
        raise ValueError(f"kmax must be positive, got {kmax}")
    if rng is None:
        rng = np.random.default_rng()

    out = []
    # For O+/O- we expect ~50% rejection; allow up to 4× tries.
    is_split = ensemble.upper().replace(" ", "") in {"O+", "O-"}
    max_tries = n_samples * (4 if is_split else 1)
    tries = 0
    while len(out) < n_samples and tries < max_tries:
        g = _ensemble_one_sample_gaps(ensemble, N, kmax, rng)
        tries += 1
        if g is not None:
            out.append(g)
    if not out:
        raise ValueError(
            f"could not generate any matched-null samples for ensemble={ensemble!r} "
            f"with N={N}, kmax={kmax} (matrix too small?)"
        )
    return np.asarray(out)


# ---------------------------------------------------------------------------
# Scan + bootstrap
# ---------------------------------------------------------------------------


def _se_var(v: float, n: int) -> float:
    """Standard error of the variance estimator under normality."""
    if n <= 1:
        return float("inf")
    return math.sqrt(2.0 * v * v / max(1, n - 1))


def scan(
    family_query: dict | Sequence[dict],
    k_max: int = K_DEFAULT_MAX,
    n_curves: Optional[int] = None,
    ensemble: str = "GUE",
    null_N: int = N_DEFAULT_MATRIX_SIZE,
    null_n_samples: int = 10_000,
    rng_seed: Optional[int] = 2024,
    zeros_records: Optional[list[dict]] = None,
) -> dict:
    """End-to-end scan: family → per-k deficit + z-score against null.

    Parameters
    ----------
    family_query : dict or list of dict
        A LMFDB filter (forwarded to :func:`fetch_zeros_for_family`) or
        an already-fetched list of records (each with a ``zeros`` key).
        For testing, pass ``zeros_records`` directly.
    k_max : int, default 24
    n_curves : int, optional
        Cap on the number of curves used.  Default: all available.
    ensemble : str
        Matching null ensemble; one of :data:`SUPPORTED_ENSEMBLES`.
    null_N : int
        Matrix size for the null.
    null_n_samples : int
        Null sample size.
    rng_seed : int, optional
        Seed for the null generator.
    zeros_records : list of dict, optional
        If supplied, skip the LMFDB fetch entirely.

    Returns
    -------
    dict
        Keys: ``k_max``, ``ensemble``, ``n_curves``, ``n_null``,
        ``data_var`` (list[float], length k_max),
        ``null_var`` (list[float]),
        ``deficit_pct`` (list[float], = 100*(1 - data/null)),
        ``z_score`` (list[float]),
        ``data_matrix`` (list[list[float]], shape (n_curves, k_max)),
        ``null_matrix`` (list[list[float]], shape (n_null, k_max)).
    """
    if zeros_records is not None:
        records = zeros_records
    elif isinstance(family_query, list):
        records = family_query
    else:
        records = fetch_zeros_for_family(
            family_query,
            max_rows=n_curves if n_curves else 5000,
            min_zeros=k_max + 1,
        )
    if n_curves is not None:
        records = records[:n_curves]
    if not records:
        raise ValueError("scan: no curves available after fetch")

    data_matrix = []
    for rec in records:
        zeros = rec.get("zeros")
        if zeros is None or len(zeros) < k_max + 1:
            continue
        try:
            spac = normalize_zeros(zeros, mode=f"local-{k_max}-gap")
        except ValueError:
            continue
        data_matrix.append(spac)
    data = np.asarray(data_matrix)
    if data.ndim != 2 or data.shape[0] < 2:
        raise ValueError(
            f"scan: not enough usable curves (got {data.shape[0]} rows)"
        )

    rng = np.random.default_rng(rng_seed)
    null = matched_null(
        N=null_N,
        n_samples=null_n_samples,
        ensemble=ensemble,
        kmax=k_max,
        rng=rng,
    )

    data_var = data.var(axis=0, ddof=1)
    null_var = null.var(axis=0, ddof=1)
    deficit_pct = (1.0 - data_var / null_var) * 100.0

    z = np.zeros(k_max)
    for i in range(k_max):
        se_d = _se_var(data_var[i], data.shape[0])
        se_n = _se_var(null_var[i], null.shape[0])
        se = math.sqrt(se_d * se_d + se_n * se_n)
        z[i] = (data_var[i] - null_var[i]) / se if se > 0 else 0.0

    return {
        "k_max": int(k_max),
        "ensemble": ensemble,
        "n_curves": int(data.shape[0]),
        "n_null": int(null.shape[0]),
        "data_var": data_var.tolist(),
        "null_var": null_var.tolist(),
        "deficit_pct": deficit_pct.tolist(),
        "z_score": z.tolist(),
        "data_matrix": data.tolist(),
        "null_matrix": null.tolist(),
    }


def bootstrap_ci(
    values: Sequence[float] | np.ndarray,
    null_values: Sequence[float] | np.ndarray,
    n_bootstrap: int = 10_000,
    alpha: float = 0.05,
    rng_seed: Optional[int] = 2024,
) -> dict:
    """Bootstrap CI + p-value for the deficit.

    The deficit is defined as ``1 - var(values) / var(null_values)``.
    Two-sided p-value is computed as the fraction of bootstrap
    replicates of (var_data, var_null) that produce a deficit of the
    opposite sign of (or smaller magnitude than) the observed point
    estimate.

    Parameters
    ----------
    values : 1-D array
        Sample of "k-th gap" values from data (length n).
    null_values : 1-D array
        Sample of "k-th gap" values from the matched null (length m).
    n_bootstrap : int
        Number of bootstrap replicates.
    alpha : float
        CI level: returns the central (1-alpha) interval.

    Returns
    -------
    dict
        ``mean`` (point-estimate of the deficit),
        ``ci_low``, ``ci_high`` (bootstrap CI),
        ``p_value`` (two-sided fraction-of-replicates with
        opposite-sign deficit).
    """
    values = np.asarray(values, dtype=float)
    null_values = np.asarray(null_values, dtype=float)
    if values.size < 2 or null_values.size < 2:
        raise ValueError(
            "bootstrap_ci: both samples need >=2 elements"
        )
    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be in (0,1), got {alpha}")
    if n_bootstrap < 100:
        raise ValueError(f"n_bootstrap must be >=100, got {n_bootstrap}")

    rng = np.random.default_rng(rng_seed)
    point = 1.0 - np.var(values, ddof=1) / np.var(null_values, ddof=1)
    n, m = values.size, null_values.size

    deficits = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        v_b = values[rng.integers(0, n, size=n)]
        u_b = null_values[rng.integers(0, m, size=m)]
        var_v = np.var(v_b, ddof=1)
        var_u = np.var(u_b, ddof=1)
        if var_u <= 0:
            deficits[b] = 0.0
        else:
            deficits[b] = 1.0 - var_v / var_u

    lo = float(np.quantile(deficits, alpha / 2.0))
    hi = float(np.quantile(deficits, 1.0 - alpha / 2.0))
    # Two-sided p-value: fraction of replicates whose deficit is
    # opposite-sign of (or as extreme on the other side as) the
    # point estimate. For a one-sided "is data var < null var?" the
    # p-value is the fraction with deficit <= 0.
    if point >= 0:
        p = float(np.mean(deficits <= 0)) * 2.0
    else:
        p = float(np.mean(deficits >= 0)) * 2.0
    p = min(1.0, max(0.0, p))

    return {
        "mean": float(point),
        "ci_low": lo,
        "ci_high": hi,
        "p_value": p,
    }


# ---------------------------------------------------------------------------
# Figure rendering
# ---------------------------------------------------------------------------


def figure(
    scan_result: dict,
    out_path: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Render a 4-panel summary figure of a scan result.

    Panels:
      1. data_var(k) and null_var(k) overlay
      2. histogram of gap_1 distribution (data vs null)
      3. deficit % vs k
      4. z-score vs k

    Returns
    -------
    str
        Path of the saved figure (PNG). If ``out_path`` is None, a
        temporary path under the system temp dir is used.
    """
    import matplotlib
    matplotlib.use("Agg")  # headless safety
    import matplotlib.pyplot as plt

    k_max = scan_result["k_max"]
    ks = np.arange(1, k_max + 1)
    data_var = np.asarray(scan_result["data_var"])
    null_var = np.asarray(scan_result["null_var"])
    deficit = np.asarray(scan_result["deficit_pct"])
    z = np.asarray(scan_result["z_score"])
    data_mat = np.asarray(scan_result.get("data_matrix", []))
    null_mat = np.asarray(scan_result.get("null_matrix", []))

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    ax = axs[0, 0]
    ax.plot(ks, data_var, "o-", label="data")
    ax.plot(ks, null_var, "s--", label=f"null ({scan_result['ensemble']})")
    ax.set_xlabel("gap index k")
    ax.set_ylabel("Var[gap_k] (mean-spacing-1)")
    ax.set_title("Per-k variance")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axs[0, 1]
    if data_mat.size and null_mat.size:
        ax.hist(data_mat[:, 0], bins=40, density=True, alpha=0.5, label="data g1")
        ax.hist(null_mat[:, 0], bins=40, density=True, alpha=0.5, label="null g1")
        ax.set_xlabel("gap_1 / mean")
        ax.set_ylabel("density")
        ax.set_title("Gap_1 distribution overlay")
        ax.legend()
        ax.grid(alpha=0.3)
    else:
        ax.text(0.5, 0.5, "no matrices saved", ha="center")

    ax = axs[1, 0]
    ax.bar(ks, deficit, color=["C3" if v > 0 else "C0" for v in deficit])
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel("gap index k")
    ax.set_ylabel("deficit % (= 100*(1 - data_var/null_var))")
    ax.set_title("Compression deficit per k")
    ax.grid(alpha=0.3)

    ax = axs[1, 1]
    ax.bar(ks, z, color=["C3" if v < 0 else "C0" for v in z])
    ax.axhline(0, color="k", lw=0.5)
    ax.axhline(-2, color="gray", ls="--", lw=0.5)
    ax.axhline(2, color="gray", ls="--", lw=0.5)
    ax.set_xlabel("gap index k")
    ax.set_ylabel("z-score")
    ax.set_title("Per-k z-score")
    ax.grid(alpha=0.3)

    if title:
        fig.suptitle(title)
    fig.tight_layout()

    if out_path is None:
        import tempfile
        out_path = tempfile.mktemp(suffix=".png", prefix="spectral_gaps_")
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return str(out_path)


__all__ = [
    "K_DEFAULT_MAX",
    "SUPPORTED_ENSEMBLES",
    "WIGNER_SURMISE_VARIANCE",
    "fetch_zeros_for_family",
    "normalize_zeros",
    "gap_k_variance",
    "matched_null",
    "scan",
    "bootstrap_ci",
    "figure",
]
