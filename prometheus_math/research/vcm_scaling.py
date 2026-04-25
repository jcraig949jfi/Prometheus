"""V-CM-scaling stratifier — codifies Aporia's per-disc gap-compression
regression as a reusable Prometheus arsenal module.

Origin
------
Aporia's F011 paper-track sub-void *V-CM-scaling*: rank-0 CM elliptic
curves (i.e. those with a non-trivial CM discriminant in
``ec_curvedata.cm``) show a per-discriminant gap-compression deficit
that scales linearly with ``log|D|``. The hand-computed fit, run by
Charon over LMFDB rank-0 CM curves, is::

    Heegner-only (h(K)=1, fundamental, maximal):
        gap1_deficit = 19.15 * log|D| + 6.0,    R² = 0.68,    r = +0.82
    Across-all rank-0 CM (12 discs):
        r = +0.79

Reference: ``roles/Aporia/SESSION_JOURNAL_20260422.md`` (lines 23, 89);
``roles/Aporia/loop_state.json`` keys T22, T23, T26, v_cm_scaling_FULL.
The Heegner discriminants used are::

    HEEGNER_FUNDAMENTAL = {-3, -4, -7, -8, -11, -19, -43, -67, -163}

(Cox, "Primes of the Form x²+ny²", Theorem 7.30: the imaginary quadratic
fields of class number 1.)

API
---
``fetch_cm_curves(rank, conductor_max, n_max)``
    Pull CM elliptic curves from the LMFDB mirror. Filters: ``cm != 0``,
    ``rank == rank``, ``conductor <= conductor_max``. Attaches CM-order
    invariants ``(d_K, f, h(O_D), is_maximal)`` via
    ``techne.lib.cm_order_data`` when available.
``per_curve_compression(curve, gap_index)``
    Compute the gap-index compression for one curve. Defers to
    ``prometheus_math.research.spectral_gaps`` if installed; otherwise
    falls back to the cached ``compression`` field on synthetic / pre-
    computed inputs (used by tests and offline analysis).
``per_disc_summary(cm_curves, gap_index)``
    Group curves by CM discriminant ``D`` and report
    ``(D, d_K, f, n, mean_compression, std, ci, is_heegner)`` per group.
``regress_log_abs_d(per_disc_data, weighted)``
    OLS regression of ``mean_compression ~ log|D|``. ``weighted=True``
    weights each disc by its sample-count ``n``.
``heegner_only_regression(per_disc_data)``
    Filter to Heegner discriminants (h(K)=1, fundamental, maximal) and
    re-run the regression. Convenience facade equivalent to filtering by
    ``is_heegner`` and calling ``regress_log_abs_d`` (always unweighted —
    matches Aporia's reference fit).
``per_disc_residuals(per_disc_data, regression_result)``
    Per-disc deviation ``observed - predicted``. Sorted by ascending
    residual (most-under-predicted first).
``figure(scan_result, out_path)``
    Two-panel matplotlib figure: log|D| vs compression (with regression
    line + per-disc points) and residuals subplot.

Forged: 2026-04-25 | Project #10 (techne/PROJECT_BACKLOG_1000.md)
"""
from __future__ import annotations

import math
from typing import Any, Callable, Iterable, Optional

import numpy as np
import scipy.stats as _stats


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Heegner fundamental discriminants — the imaginary quadratic fields with
#: class number 1 (Cox, Theorem 7.30). These are the discriminants where
#: ``D = d_K`` and the CM order is the maximal order ``O_K`` itself.
HEEGNER_FUNDAMENTAL: frozenset[int] = frozenset({
    -3, -4, -7, -8, -11, -19, -43, -67, -163,
})


# ---------------------------------------------------------------------------
# 1. fetch_cm_curves
# ---------------------------------------------------------------------------

def fetch_cm_curves(
    rank: int = 0,
    conductor_max: int = 10**6,
    n_max: int = 10_000,
    *,
    lmfdb_module: Optional[Any] = None,
    cm_order_data_fn: Optional[Callable[[int], dict]] = None,
) -> list[dict]:
    """Fetch CM elliptic curves from the LMFDB Postgres mirror.

    Parameters
    ----------
    rank : int
        Mordell-Weil rank filter (default 0 — Aporia's published thread).
    conductor_max : int
        Upper bound on conductor.
    n_max : int
        Max rows to return.
    lmfdb_module : module, optional
        Override for ``prometheus_math.databases.lmfdb`` (testing /
        offline use).
    cm_order_data_fn : callable, optional
        Override for ``techne.lib.cm_order_data.cm_order_data`` (testing).

    Returns
    -------
    list of dicts, each containing the LMFDB row plus ``fundamental_disc``,
    ``cm_conductor``, ``is_maximal``, ``class_number``, ``is_heegner``
    when the cm-order resolver is available.
    """
    if conductor_max <= 0:
        raise ValueError(f"conductor_max must be positive, got {conductor_max}")
    if n_max <= 0:
        raise ValueError(f"n_max must be positive, got {n_max}")

    if lmfdb_module is None:
        from prometheus_math.databases import lmfdb as lmfdb_module

    sql = (
        'SELECT "lmfdb_label", "ainvs", "conductor", "rank", '
        '"analytic_rank", "torsion", "cm", "regulator", "sha", '
        '"faltings_height" '
        'FROM "ec_curvedata" '
        'WHERE "cm" != 0 AND "rank" = %s AND "conductor" <= %s '
        'LIMIT %s'
    )
    rows = lmfdb_module.query_dicts(sql, (rank, conductor_max, n_max))

    # attach CM-order invariants
    if cm_order_data_fn is None:
        try:
            from techne.lib.cm_order_data import cm_order_data as cm_order_data_fn
        except Exception:
            cm_order_data_fn = None

    cache: dict[int, dict] = {}
    for r in rows:
        D = int(r['cm'])
        if cm_order_data_fn is not None:
            if D not in cache:
                try:
                    cache[D] = cm_order_data_fn(D)
                except Exception:
                    cache[D] = {}
            data = cache[D]
            r['fundamental_disc'] = data.get('fundamental_disc', D)
            r['cm_conductor'] = data.get('cm_conductor', 1)
            r['is_maximal'] = data.get('is_maximal', True)
            r['class_number'] = data.get('class_number', None)
        else:
            r['fundamental_disc'] = D
            r['cm_conductor'] = 1
            r['is_maximal'] = True
            r['class_number'] = None
        r['is_heegner'] = (
            r['fundamental_disc'] in HEEGNER_FUNDAMENTAL
            and r.get('cm_conductor', 1) == 1
            and (r.get('class_number') in (None, 1))
        )
    return rows


# ---------------------------------------------------------------------------
# 2. per_curve_compression
# ---------------------------------------------------------------------------

def per_curve_compression(curve: dict, gap_index: int = 1) -> float:
    """Return the gap-index compression for one curve.

    Behavior
    --------
    1. If the curve dict has a precomputed ``compression`` field, return
       it (this is the path used by tests and by the Aporia per-disc
       residual table that's already cached).
    2. Otherwise defer to ``prometheus_math.research.spectral_gaps`` if
       installed.
    3. If neither path yields a value, raise ``RuntimeError`` — the
       caller must either cache compression on the curve or install the
       sibling spectral_gaps module.
    """
    if 'compression' in curve:
        return float(curve['compression'])

    try:
        from prometheus_math.research import spectral_gaps  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "per_curve_compression: no cached `compression` on the input "
            "curve and `prometheus_math.research.spectral_gaps` is not "
            f"importable ({e!r}). Either precompute compression upstream "
            "or install the spectral_gaps module."
        )

    # spectral_gaps API contract (project #9): given a curve dict and gap
    # index, return the compression deficit relative to GUE null.
    if hasattr(spectral_gaps, 'compression_for_curve'):
        return float(spectral_gaps.compression_for_curve(curve, gap_index=gap_index))
    if hasattr(spectral_gaps, 'gap_compression'):
        return float(spectral_gaps.gap_compression(curve, gap_index=gap_index))
    raise RuntimeError(
        "per_curve_compression: spectral_gaps module is installed but does "
        "not expose `compression_for_curve` or `gap_compression`. "
        "Coordinate with the spectral_gaps author."
    )


# ---------------------------------------------------------------------------
# 3. per_disc_summary
# ---------------------------------------------------------------------------

def per_disc_summary(
    cm_curves: Iterable[dict],
    gap_index: int = 1,
    *,
    ci_z: float = 1.96,
) -> list[dict]:
    """Group CM curves by discriminant and summarize per-disc compression.

    Parameters
    ----------
    cm_curves : iterable of dict
        Each dict must carry ``cm`` (the CM discriminant) and
        ``compression`` (or be resolvable via ``per_curve_compression``).
    gap_index : int
        Forwarded to ``per_curve_compression``.
    ci_z : float
        z-score for the symmetric confidence interval on the mean
        (default 1.96 = 95% normal CI).

    Returns
    -------
    list of dicts, sorted by ``|D|`` ascending. Keys::

        D                — CM discriminant (negative int)
        d_K              — fundamental discriminant
        f                — CM conductor (1 if maximal order)
        n                — sample size for this D
        mean_compression — sample mean
        std              — sample std (ddof=1) or 0.0 if n<2
        ci               — (lower, upper) tuple for the mean (CI_z * sem)
        is_heegner       — d_K in HEEGNER_FUNDAMENTAL and f == 1

    Raises
    ------
    ValueError
        If ``cm_curves`` is empty.
    """
    curves = list(cm_curves)
    if not curves:
        raise ValueError("per_disc_summary: cm_curves is empty")

    by_D: dict[int, list[dict]] = {}
    for c in curves:
        D = int(c['cm'])
        by_D.setdefault(D, []).append(c)

    out: list[dict] = []
    for D in sorted(by_D, key=lambda d: abs(d)):
        group = by_D[D]
        compressions = np.array(
            [per_curve_compression(c, gap_index=gap_index) for c in group],
            dtype=float,
        )
        n = len(compressions)
        mean = float(compressions.mean())
        if n >= 2:
            std = float(compressions.std(ddof=1))
            sem = std / math.sqrt(n)
        else:
            std = 0.0
            sem = 0.0
        ci = (mean - ci_z * sem, mean + ci_z * sem)

        # representative metadata from the first curve in the group
        rep = group[0]
        d_K = int(rep.get('fundamental_disc', D))
        f = int(rep.get('cm_conductor', 1))
        is_maximal = bool(rep.get('is_maximal', f == 1))
        is_heegner = (d_K in HEEGNER_FUNDAMENTAL) and is_maximal

        out.append({
            'D': D,
            'd_K': d_K,
            'f': f,
            'n': n,
            'mean_compression': mean,
            'std': std,
            'ci': ci,
            'is_heegner': is_heegner,
        })
    return out


# ---------------------------------------------------------------------------
# 4. regress_log_abs_d
# ---------------------------------------------------------------------------

def _ols_unweighted(xs: np.ndarray, ys: np.ndarray) -> dict:
    """OLS via scipy.stats.linregress for clean p-value access."""
    res = _stats.linregress(xs, ys)
    return {
        'slope': float(res.slope),
        'intercept': float(res.intercept),
        'r': float(res.rvalue),
        'r_squared': float(res.rvalue ** 2),
        'p_value': float(res.pvalue),
    }


def _ols_weighted(xs: np.ndarray, ys: np.ndarray, ws: np.ndarray) -> dict:
    """Weighted OLS via numpy lstsq with a sqrt(w) row-scaling.

    Returns the same dict shape as ``_ols_unweighted``. r/r_squared are
    the *weighted* correlation; p_value is computed via the t-statistic
    on the slope using the effective weighted DoF (n - 2).
    """
    n = len(xs)
    A = np.column_stack([xs, np.ones_like(xs)])
    sw = np.sqrt(ws)
    Aw = A * sw[:, None]
    yw = ys * sw
    sol, *_ = np.linalg.lstsq(Aw, yw, rcond=None)
    slope, intercept = float(sol[0]), float(sol[1])

    pred = slope * xs + intercept
    # weighted means
    w_sum = ws.sum()
    x_mean = float((ws * xs).sum() / w_sum)
    y_mean = float((ws * ys).sum() / w_sum)
    cov_xy = float((ws * (xs - x_mean) * (ys - y_mean)).sum())
    var_x = float((ws * (xs - x_mean) ** 2).sum())
    var_y = float((ws * (ys - y_mean) ** 2).sum())
    if var_x <= 0 or var_y <= 0:
        r = 0.0
    else:
        r = cov_xy / math.sqrt(var_x * var_y)
    r_squared = r * r

    # t-statistic for slope; SE(slope) ≈ sqrt(SSE / ((n-2) * SSx))
    sse = float((ws * (ys - pred) ** 2).sum())
    if n > 2 and var_x > 0:
        s2 = sse / (n - 2)
        se_slope = math.sqrt(s2 / var_x) if s2 > 0 else 0.0
        if se_slope > 0:
            t = slope / se_slope
            p_value = 2.0 * (1.0 - _stats.t.cdf(abs(t), df=n - 2))
        else:
            p_value = float('nan')
    else:
        p_value = float('nan')

    return {
        'slope': slope,
        'intercept': intercept,
        'r': r,
        'r_squared': r_squared,
        'p_value': float(p_value),
    }


def regress_log_abs_d(
    per_disc_data: list[dict],
    weighted: bool = True,
) -> dict:
    """OLS regression of ``mean_compression ~ log|D|`` over per-disc rows.

    Parameters
    ----------
    per_disc_data : list of dict
        Output of :func:`per_disc_summary`.
    weighted : bool
        If True, weight each disc by its sample-count ``n`` (default).

    Returns
    -------
    dict with keys::

        slope, intercept, r, r_squared, p_value, fit_predictions

    ``fit_predictions`` is a list of dicts ``{D, log_abs_D, predicted}``
    for plotting.

    Edge behavior
    -------------
    * Empty ``per_disc_data`` -> ``ValueError``.
    * Single-row data (degenerate fit) -> ``slope = NaN``,
      ``r_squared = NaN``, ``p_value = NaN``, ``intercept`` = the lone
      ``mean_compression``.
    """
    if not per_disc_data:
        raise ValueError("regress_log_abs_d: per_disc_data is empty")

    xs = np.array([math.log(abs(r['D'])) for r in per_disc_data], dtype=float)
    ys = np.array([r['mean_compression'] for r in per_disc_data], dtype=float)
    ws = np.array([r['n'] for r in per_disc_data], dtype=float)

    if len(per_disc_data) < 2:
        # degenerate — line through one point is undetermined
        return {
            'slope': float('nan'),
            'intercept': float(ys[0]),
            'r': float('nan'),
            'r_squared': float('nan'),
            'p_value': float('nan'),
            'fit_predictions': [{
                'D': per_disc_data[0]['D'],
                'log_abs_D': float(xs[0]),
                'predicted': float(ys[0]),
            }],
        }

    fit = _ols_weighted(xs, ys, ws) if weighted else _ols_unweighted(xs, ys)

    fit_preds = []
    for r, x in zip(per_disc_data, xs):
        fit_preds.append({
            'D': r['D'],
            'log_abs_D': float(x),
            'predicted': fit['slope'] * float(x) + fit['intercept'],
        })
    fit['fit_predictions'] = fit_preds
    return fit


# ---------------------------------------------------------------------------
# 5. heegner_only_regression
# ---------------------------------------------------------------------------

def heegner_only_regression(per_disc_data: list[dict]) -> dict:
    """Filter to Heegner discriminants and re-run the regression.

    Heegner discs are the ``-3, -4, -7, -8, -11, -19, -43, -67, -163``
    set (h(K)=1, fundamental, maximal). The reference fit is::

        gap1_deficit ≈ 19.15 * log|D| + 6.0       R² = 0.68

    The convenience function calls :func:`regress_log_abs_d` *unweighted*
    on the filtered subset — this matches Aporia's published fit, which
    treats each Heegner disc as one data point regardless of curve count.

    Returns the same dict shape as :func:`regress_log_abs_d`.
    """
    heegner_subset = [r for r in per_disc_data if r.get('is_heegner', False)]
    if not heegner_subset:
        raise ValueError(
            "heegner_only_regression: no Heegner discriminants in per_disc_data. "
            f"Heegner set is {sorted(HEEGNER_FUNDAMENTAL)}; "
            f"observed D values: {[r.get('D') for r in per_disc_data]}"
        )
    return regress_log_abs_d(heegner_subset, weighted=False)


# ---------------------------------------------------------------------------
# 6. per_disc_residuals
# ---------------------------------------------------------------------------

def per_disc_residuals(
    per_disc_data: list[dict],
    regression_result: dict,
) -> list[dict]:
    """Per-disc deviation from the regression fit, rank-ordered.

    Parameters
    ----------
    per_disc_data : list of dict
        Output of :func:`per_disc_summary`.
    regression_result : dict
        Output of :func:`regress_log_abs_d` (or
        :func:`heegner_only_regression`).

    Returns
    -------
    list of dicts, sorted by ascending residual::

        {D, log_abs_D, observed, predicted, residual,
         is_heegner, n, rank}

    where ``residual = observed - predicted``. The ``rank`` field is the
    1-indexed position in ascending order (i.e., rank 1 = most negative
    residual = most under-predicted disc).
    """
    slope = regression_result['slope']
    intercept = regression_result['intercept']

    rows: list[dict] = []
    for r in per_disc_data:
        D = r['D']
        x = math.log(abs(D))
        predicted = slope * x + intercept
        observed = r['mean_compression']
        rows.append({
            'D': D,
            'log_abs_D': x,
            'observed': observed,
            'predicted': predicted,
            'residual': observed - predicted,
            'is_heegner': r.get('is_heegner', False),
            'n': r.get('n', 0),
        })
    rows.sort(key=lambda x: x['residual'])
    for i, row in enumerate(rows, start=1):
        row['rank'] = i
    return rows


# ---------------------------------------------------------------------------
# 7. figure
# ---------------------------------------------------------------------------

def figure(
    scan_result: dict,
    out_path: Optional[str] = None,
) -> str:
    """Two-panel matplotlib figure of the V-CM-scaling fit.

    Parameters
    ----------
    scan_result : dict
        Must contain keys::

            per_disc        — output of per_disc_summary
            regression      — output of regress_log_abs_d
            residuals       — output of per_disc_residuals

    out_path : str, optional
        If given, save the figure to this path. Returns the path.
        Otherwise saves to a temp file and returns that path.

    Returns
    -------
    str — path to the saved PNG.
    """
    import os
    import tempfile
    import matplotlib
    matplotlib.use("Agg")  # headless safe
    import matplotlib.pyplot as plt

    per_disc = scan_result['per_disc']
    fit = scan_result['regression']
    residuals = scan_result['residuals']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 9), sharex=False)

    # Panel 1: log|D| vs mean_compression with regression line
    xs = np.array([math.log(abs(r['D'])) for r in per_disc])
    ys = np.array([r['mean_compression'] for r in per_disc])
    ns = np.array([r['n'] for r in per_disc])
    is_h = np.array([r.get('is_heegner', False) for r in per_disc])

    ax1.scatter(xs[is_h], ys[is_h], s=np.sqrt(ns[is_h]) * 8,
                c='tab:red', label='Heegner', alpha=0.85, edgecolor='k')
    ax1.scatter(xs[~is_h], ys[~is_h], s=np.sqrt(ns[~is_h]) * 8,
                c='tab:blue', label='non-Heegner', alpha=0.6,
                edgecolor='k')

    if not math.isnan(fit['slope']):
        x_line = np.linspace(xs.min() - 0.1, xs.max() + 0.1, 100)
        y_line = fit['slope'] * x_line + fit['intercept']
        ax1.plot(x_line, y_line, 'k--',
                 label=f'fit: y = {fit["slope"]:.2f}·log|D| + '
                       f'{fit["intercept"]:.2f}, R²={fit["r_squared"]:.3f}')

    ax1.set_xlabel("log|D|")
    ax1.set_ylabel("mean compression")
    ax1.set_title("V-CM-scaling: per-disc gap compression")
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Panel 2: residuals (rank-ordered)
    res_xs = np.arange(len(residuals))
    res_vals = np.array([r['residual'] for r in residuals])
    res_h = np.array([r['is_heegner'] for r in residuals])
    colors = ['tab:red' if h else 'tab:blue' for h in res_h]
    ax2.bar(res_xs, res_vals, color=colors, edgecolor='k')
    ax2.axhline(0, color='k', linewidth=0.5)
    ax2.set_xticks(res_xs)
    ax2.set_xticklabels([f"D={r['D']}" for r in residuals],
                        rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel("residual (observed - predicted)")
    ax2.set_title("Per-disc residuals (rank-ordered)")
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if out_path is None:
        fd, out_path = tempfile.mkstemp(prefix='vcm_scaling_', suffix='.png')
        os.close(fd)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------

__all__ = [
    'HEEGNER_FUNDAMENTAL',
    'fetch_cm_curves',
    'per_curve_compression',
    'per_disc_summary',
    'regress_log_abs_d',
    'heegner_only_regression',
    'per_disc_residuals',
    'figure',
]
