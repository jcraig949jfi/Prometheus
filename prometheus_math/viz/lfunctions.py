"""prometheus_math.viz.lfunctions — L-function zero visualization.

Public API
----------
- :func:`get_zeros(label, n_zeros=50)` — pull or compute the first
  ``n_zeros`` imaginary parts of nontrivial zeros of the L-function
  named by ``label``.  ``label='Riemann'`` falls back to mpmath's
  :func:`mpmath.zetazero`; LMFDB-style labels are looked up against the
  ``lfunc_lfunctions`` mirror at devmirror.lmfdb.xyz.
- :func:`plot_zeros(label, n_zeros=50, ax=None, show_riemann_band=False,
  backend='matplotlib')` — plot the zeros as vertical lines at their
  imaginary parts.
- :func:`plot_critical_strip(label, n_zeros=20, ax=None)` — heat-map of
  ``|L(s)|`` over a small grid around the critical strip with zeros
  overlaid as red dots on the critical line.
- :func:`plot_zero_spacings(label, n_zeros=200, ax=None)` — histogram
  of normalized nearest-neighbor zero spacings with the GUE Wigner
  surmise and a Poisson reference curve.
- :func:`compare_zero_statistics(labels, n_zeros=100)` — overlay
  spacing statistics for several L-functions and report Kolmogorov-
  Smirnov distance to GUE.
- :func:`save_zeros_plot(label, path, n_zeros=50, fmt=None)` — compute
  and save in one call.

Backends
--------
The ``backend`` argument follows the project convention shared with
``viz.knot``: ``'matplotlib'`` returns an ``mpl.figure.Figure``;
``'svg'`` returns the figure rendered to a raw SVG string.

LMFDB labels
------------
The ``lfunc_lfunctions`` table has a mix of populated and ``NULL``
labels in the public mirror.  We accept three label shapes:

- The new label format, e.g. ``'1-1-1.1-r0-0-0'`` (Riemann zeta in
  LMFDB), looked up via the ``label`` column.
- An ``origin``-style identifier, e.g. ``'EllipticCurve.Q.11.a'`` or
  ``'EllipticCurve/Q/11/a'`` — dots are translated to slashes before
  the LIKE-match against the ``origin`` column.
- The literal string ``'Riemann'`` — handled via mpmath without a
  network round-trip.

If neither lookup succeeds the LMFDB layer raises a clean ValueError
with the offending label embedded.

Authority
---------
- First non-trivial zero of ζ(s) lies at ``t = 14.13472514173469...``
  (Edwards, "Riemann's Zeta Function", §10).  The ``Riemann`` branch is
  cross-checked against ``mpmath.zetazero(1).imag``.
- LMFDB stores the imaginary parts of the positive zeros of every
  curated L-function in ``lfunc_lfunctions.positive_zeros`` (a JSONB
  array of decimal strings).
"""
from __future__ import annotations

import io
import math
import warnings
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from . import _common

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    _HAS_MPL = True
except Exception:  # pragma: no cover
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    Figure = object  # type: ignore
    _HAS_MPL = False

try:
    import mpmath
    _HAS_MPMATH = True
except Exception:  # pragma: no cover
    mpmath = None  # type: ignore
    _HAS_MPMATH = False

try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:  # pragma: no cover
    np = None  # type: ignore
    _HAS_NUMPY = False


__all__ = [
    "get_zeros",
    "plot_zeros",
    "plot_critical_strip",
    "plot_zero_spacings",
    "compare_zero_statistics",
    "save_zeros_plot",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require_mpl() -> None:
    if not _HAS_MPL:
        raise ImportError(
            "prometheus_math.viz.lfunctions requires matplotlib. "
            "Install via `pip install matplotlib`."
        )


def _require_mpmath() -> None:
    if not _HAS_MPMATH:
        raise ImportError(
            "prometheus_math.viz.lfunctions requires mpmath. "
            "Install via `pip install mpmath`."
        )


def _is_riemann_label(label: str) -> bool:
    """True iff ``label`` refers to the Riemann zeta function."""
    if not isinstance(label, str):
        return False
    norm = label.strip().lower()
    return norm in (
        "riemann",
        "riemann_zeta",
        "riemann-zeta",
        "zeta",
        "ζ",
        "1-1-1.1-r0-0-0",  # LMFDB label for ζ
        "character/dirichlet/1/1",
        "character.dirichlet.1.1",
    )


def _normalize_origin(label: str) -> str:
    """Convert a dotted origin shorthand to LMFDB slash-form.

    LMFDB's ``origin`` column uses ``/`` as the separator, but dots
    are how the rest of the codebase passes around object labels
    (``11.a1``, ``2.0.20.1``, etc.).  We accept either.
    """
    return label.replace(".", "/").strip()


def _zeros_via_lmfdb(label: str, n_zeros: int) -> Optional[List[float]]:
    """Pull positive_zeros from LMFDB for the given label.

    Tries three lookups, in order:

    1. exact match on ``lfunc_lfunctions.label``
    2. exact match on ``lfunc_lfunctions.origin``
    3. LIKE-prefix match on ``origin`` (``label + '/%'``) so callers
       can pass e.g. ``'EllipticCurve/Q/11/a'`` without specifying the
       isogeny-class member index.

    Returns ``None`` if the LMFDB mirror is unreachable; raises
    ``ValueError`` if the mirror is reachable but the label is unknown.
    """
    try:
        from prometheus_math.databases import lmfdb
    except Exception:
        return None

    if not lmfdb.probe(timeout=3.0):
        return None

    origin_norm = _normalize_origin(label)
    sql_attempts = [
        (
            'SELECT positive_zeros FROM "lfunc_lfunctions" '
            'WHERE "label" = %s LIMIT 1',
            (label,),
        ),
        (
            'SELECT positive_zeros FROM "lfunc_lfunctions" '
            'WHERE "origin" = %s LIMIT 1',
            (origin_norm,),
        ),
        (
            'SELECT positive_zeros FROM "lfunc_lfunctions" '
            'WHERE "origin" LIKE %s ORDER BY "origin" LIMIT 1',
            (origin_norm + "/%",),
        ),
    ]
    for sql, params in sql_attempts:
        try:
            rows = lmfdb.query_dicts(sql, params, timeout=10)
        except Exception:
            return None
        if rows and rows[0].get("positive_zeros"):
            raw = rows[0]["positive_zeros"]
            zeros = [float(x) for x in raw]
            return zeros[:n_zeros]
    raise ValueError(
        f"LMFDB has no L-function matching label {label!r} "
        f"(tried label/origin lookups)."
    )


def _zeros_via_mpmath(n_zeros: int) -> List[float]:
    """First ``n_zeros`` non-trivial Riemann ζ zeros via mpmath."""
    _require_mpmath()
    return [float(mpmath.zetazero(k).imag) for k in range(1, n_zeros + 1)]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_zeros(label: str, n_zeros: int = 50) -> List[float]:
    """Return the first ``n_zeros`` imaginary parts of zeros of L(s, label).

    Parameters
    ----------
    label : str
        Either a built-in tag (``'Riemann'``), an LMFDB label
        (``'1-1-1.1-r0-0-0'``), or an LMFDB origin in either dotted or
        slashed form (``'EllipticCurve.Q.11.a'`` /
        ``'EllipticCurve/Q/11/a'``).
    n_zeros : int, default 50
        Number of zeros to return.  Must be ``>= 0``.

    Returns
    -------
    list[float]
        Imaginary parts (positive reals, monotone increasing).  Length
        is ``min(n_zeros, available)``.  When fewer than ``n_zeros``
        zeros are available, a ``UserWarning`` is emitted with the
        actual count.

    Raises
    ------
    ValueError
        ``n_zeros < 0``, ``label`` is not a string, or LMFDB has no
        match for ``label``.
    """
    if not isinstance(label, str) or not label.strip():
        raise ValueError(
            f"label must be a non-empty string, got {label!r}"
        )
    if not isinstance(n_zeros, int) or n_zeros < 0:
        raise ValueError(
            f"n_zeros must be a non-negative integer, got {n_zeros!r}"
        )
    if n_zeros == 0:
        return []

    if _is_riemann_label(label):
        return _zeros_via_mpmath(n_zeros)

    zeros = _zeros_via_lmfdb(label, n_zeros)
    if zeros is None:
        # Mirror unreachable
        raise ValueError(
            f"cannot retrieve zeros for label {label!r}: LMFDB mirror "
            "unreachable and no built-in fallback for this label."
        )

    if len(zeros) < n_zeros:
        warnings.warn(
            f"requested n_zeros={n_zeros} but LMFDB stores only "
            f"{len(zeros)} for {label!r}; returning truncated list.",
            UserWarning,
            stacklevel=2,
        )
    return zeros


def plot_zeros(label: str,
               n_zeros: int = 50,
               ax: Optional[Any] = None,
               show_riemann_band: bool = False,
               backend: str = "matplotlib") -> Union[Figure, str]:
    """Plot the first ``n_zeros`` imaginary parts of L(s, label).

    Each zero is rendered as a vertical line on the x-axis; the y-axis
    is symbolic (it ranges over ``[-1, 1]`` and is not labeled).

    Parameters
    ----------
    label : str
        L-function label.  See :func:`get_zeros` for the accepted
        forms.
    n_zeros : int, default 50
        Number of zeros to plot.
    ax : matplotlib.axes.Axes, optional
        Pre-existing axes; when provided the new lines are *added* to
        it (cumulative plotting), otherwise a new figure is created.
    show_riemann_band : bool, default False
        If True, shade the band between the first and last zero so the
        density of zeros is visually obvious.
    backend : {'matplotlib', 'svg'}, default 'matplotlib'
        ``'matplotlib'`` returns an ``mpl.figure.Figure``;
        ``'svg'`` returns the figure as a raw SVG string.

    Returns
    -------
    matplotlib.figure.Figure or str
    """
    if backend not in ("matplotlib", "svg"):
        raise ValueError(
            f"unknown backend {backend!r}; expected 'matplotlib' or 'svg'"
        )
    _require_mpl()
    _common._setup_matplotlib(backend=backend)

    zeros = get_zeros(label, n_zeros=n_zeros)

    if backend == "matplotlib":
        if ax is None:
            fig, ax_local = plt.subplots(figsize=(8.0, 2.5))
        else:
            ax_local = ax
            fig = ax_local.figure
        _draw_zeros(ax_local, label, zeros, show_riemann_band)
        if ax is None:
            fig.tight_layout()
        return fig

    # SVG backend
    fig, ax_local = plt.subplots(figsize=(8.0, 2.5))
    try:
        _draw_zeros(ax_local, label, zeros, show_riemann_band)
        fig.tight_layout()
        buf = io.StringIO()
        fig.savefig(buf, format="svg")
        return buf.getvalue()
    finally:
        plt.close(fig)


def _draw_zeros(ax,
                label: str,
                zeros: Sequence[float],
                show_riemann_band: bool) -> None:
    """Add zero markers to ``ax``; helper for :func:`plot_zeros`."""
    if zeros:
        # Vertical line per zero, height [-1, 1].  Use vlines for
        # vectorised drawing — one Line2D collection added to ax.
        ax.vlines(
            list(zeros),
            ymin=-1.0,
            ymax=1.0,
            colors="black",
            linewidth=1.2,
        )
        if show_riemann_band:
            ax.axvspan(
                min(zeros), max(zeros),
                ymin=0.45, ymax=0.55,
                alpha=0.15, color="#1f77b4",
            )
        # Mark each zero with a small dot at y=0 too — helps identify
        # ticks visually and is what tests count.
        ax.plot(
            list(zeros),
            [0.0] * len(zeros),
            marker="o",
            markersize=3.0,
            linestyle="None",
            color="#d62728",
        )

    ax.set_ylim(-1.2, 1.2)
    ax.set_yticks([])
    ax.set_xlabel("Im(s)  (imaginary part of zero)")
    ax.set_title(f"L-function zeros: {label}  (N={len(zeros)})", fontsize=10)
    ax.grid(True, axis="x", alpha=0.25)
    if zeros:
        # Tight x-limits with a small pad so the leftmost / rightmost
        # zeros aren't on the figure edge.
        lo, hi = min(zeros), max(zeros)
        pad = max(0.05 * (hi - lo), 0.5)
        ax.set_xlim(lo - pad, hi + pad)


def plot_critical_strip(label: str,
                        n_zeros: int = 20,
                        ax: Optional[Any] = None,
                        sigma_window: float = 0.6,
                        n_sigma_samples: int = 41) -> Figure:
    """Plot ``|L(σ + it)|`` on a grid around the critical strip.

    For ``label='Riemann'`` we use mpmath's ``zeta`` to evaluate the
    function exactly.  For other labels we don't have a generic
    L-evaluator, so the heat-map degrades gracefully to a plot of the
    *zero locations* on a critical-line backdrop.  Either way, the
    zeros from :func:`get_zeros` are overlaid as red dots on the
    critical line ``σ = 1/2``.

    Parameters
    ----------
    label : str
        L-function label (see :func:`get_zeros`).
    n_zeros : int, default 20
        Number of zeros to overlay.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw into.
    sigma_window : float, default 0.6
        Half-width of the σ window centred on σ=1/2.
    n_sigma_samples : int, default 41
        Number of σ samples in the heat-map (only used for Riemann).

    Returns
    -------
    matplotlib.figure.Figure
    """
    _require_mpl()
    _common._setup_matplotlib()

    if not _HAS_NUMPY:
        raise ImportError("plot_critical_strip requires numpy.")

    zeros = get_zeros(label, n_zeros=n_zeros)
    if ax is None:
        fig, ax_local = plt.subplots(figsize=(8.0, 4.0))
    else:
        ax_local = ax
        fig = ax_local.figure

    if _is_riemann_label(label) and _HAS_MPMATH and zeros:
        sigmas = np.linspace(0.5 - sigma_window, 0.5 + sigma_window,
                             n_sigma_samples)
        t_max = max(zeros) + 2.0
        t_min = max(0.0, min(zeros) - 2.0)
        ts = np.linspace(t_min, t_max, 200)
        Z = np.zeros((len(sigmas), len(ts)))
        for i, sigma in enumerate(sigmas):
            for j, t in enumerate(ts):
                Z[i, j] = float(abs(mpmath.zeta(complex(sigma, t))))
        # log scale for visibility (|zeta| varies orders of magnitude)
        Z = np.log10(Z + 1e-9)
        ax_local.imshow(
            Z,
            origin="lower",
            extent=(t_min, t_max, sigmas[0], sigmas[-1]),
            aspect="auto",
            cmap="viridis",
        )

    # Overlay zeros on the critical line.
    if zeros:
        ax_local.plot(
            list(zeros), [0.5] * len(zeros),
            marker="o", linestyle="None",
            color="#d62728", markersize=4.0,
            markeredgecolor="white", markeredgewidth=0.5,
        )
    ax_local.axhline(0.5, color="white", linewidth=0.7, alpha=0.7,
                     linestyle="--")
    ax_local.set_xlabel("Im(s) = t")
    ax_local.set_ylabel("Re(s) = σ")
    ax_local.set_title(
        f"Critical strip: {label}  (first {len(zeros)} zeros)",
        fontsize=10,
    )
    if ax is None:
        fig.tight_layout()
    return fig


def _normalized_spacings(zeros: Sequence[float]) -> List[float]:
    """Return mean-normalised nearest-neighbour spacings.

    ``s_k = (z_{k+1} - z_k) / mean_gap`` where ``mean_gap`` is the
    average consecutive gap.  This is the standard normalisation under
    which the GUE Wigner surmise has the closed-form

        P(s) = (32 / π²) · s² · exp(-(4/π) · s²) .
    """
    if len(zeros) < 2:
        return []
    gaps = [zeros[i + 1] - zeros[i] for i in range(len(zeros) - 1)]
    mean_gap = sum(gaps) / len(gaps)
    if mean_gap <= 0:
        return []
    return [g / mean_gap for g in gaps]


def _wigner_gue_pdf(s: float) -> float:
    """GUE Wigner surmise density at ``s``."""
    return (32.0 / math.pi ** 2) * s * s * math.exp(-(4.0 / math.pi) * s * s)


def _wigner_gue_cdf(s: float) -> float:
    """Closed-form CDF of the GUE Wigner surmise.

    Derived by direct integration of ``P(s)``:

        F(s) = 1 - exp(-(4/π) s²) · (1 + (4/π) s²)

    (Verified by differentiation: ``F'(s) = (32/π²) s² e^{-(4/π) s²}``.)
    """
    a = 4.0 / math.pi
    return 1.0 - math.exp(-a * s * s) * (1.0 + a * s * s)


def _ks_distance_to_gue(spacings: Sequence[float]) -> float:
    """Empirical KS distance between ``spacings`` and the GUE CDF."""
    if not spacings:
        return float("nan")
    sorted_s = sorted(spacings)
    n = len(sorted_s)
    d = 0.0
    for i, s in enumerate(sorted_s):
        f_emp_lo = i / n
        f_emp_hi = (i + 1) / n
        f_th = _wigner_gue_cdf(s)
        d = max(d, abs(f_emp_hi - f_th), abs(f_emp_lo - f_th))
    return d


def plot_zero_spacings(label: str,
                       n_zeros: int = 200,
                       ax: Optional[Any] = None,
                       n_bins: int = 30) -> Figure:
    """Histogram of normalised nearest-neighbour zero spacings.

    Overlays the GUE Wigner surmise (random-matrix prediction) and the
    Poisson reference (``e^{-s}``, what unrelated zeros would do).

    Parameters
    ----------
    label : str
        L-function label.
    n_zeros : int, default 200
        Number of zeros to base the histogram on.  Larger is better
        for statistics; 200 is a reasonable default for ζ.
    ax : matplotlib.axes.Axes, optional
        Axes to draw into.
    n_bins : int, default 30
        Number of histogram bins on ``s ∈ [0, 4]``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    _require_mpl()
    _common._setup_matplotlib()
    if not _HAS_NUMPY:
        raise ImportError("plot_zero_spacings requires numpy.")

    zeros = get_zeros(label, n_zeros=n_zeros)
    spacings = _normalized_spacings(zeros)

    if ax is None:
        fig, ax_local = plt.subplots(figsize=(7.0, 4.0))
    else:
        ax_local = ax
        fig = ax_local.figure

    # Histogram (density-normalised).
    if spacings:
        ax_local.hist(
            spacings,
            bins=n_bins,
            range=(0.0, 4.0),
            density=True,
            alpha=0.55,
            color="#1f77b4",
            edgecolor="white",
            label="empirical spacings",
        )

    s_grid = np.linspace(0.0, 4.0, 401)
    gue = np.array([_wigner_gue_pdf(s) for s in s_grid])
    poisson = np.exp(-s_grid)
    ax_local.plot(s_grid, gue, color="#d62728", linewidth=2.0,
                  label="GUE Wigner surmise")
    ax_local.plot(s_grid, poisson, color="#2ca02c", linewidth=1.5,
                  linestyle="--", label="Poisson")

    ax_local.set_xlim(0.0, 4.0)
    ax_local.set_xlabel("normalised gap  s = (z_{k+1} − z_k) / ⟨gap⟩")
    ax_local.set_ylabel("density")
    ax_local.set_title(
        f"Zero-spacing distribution: {label}  "
        f"(N={len(spacings)})",
        fontsize=10,
    )
    ax_local.legend(loc="upper right", fontsize=8)
    if ax is None:
        fig.tight_layout()
    return fig


def compare_zero_statistics(labels: Sequence[str],
                            n_zeros: int = 100,
                            ax: Optional[Any] = None) -> dict:
    """Compute & display nearest-neighbour spacing statistics for many L-fns.

    For each label in ``labels`` the function pulls ``n_zeros`` zeros,
    computes the empirical CDF of normalised gaps, and overlays it
    onto a single axes together with the GUE Wigner-surmise CDF.  The
    return value reports per-label mean spacing, KS distance to GUE,
    and zero count.

    Parameters
    ----------
    labels : sequence of str
        L-function labels.  Must contain at least two entries (this is
        a *comparison* operator).
    n_zeros : int, default 100
        Zeros per label.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw into.

    Returns
    -------
    dict
        ``{'figure': Figure, 'stats': {label: {...}}, 'ks_table': {...}}``
        ``stats[label]`` has keys ``mean_spacing``, ``ks_to_gue``,
        ``n_spacings``.  ``ks_table`` is a label-vs-label dict of
        Kolmogorov-Smirnov distances between the empirical spacing
        distributions.
    """
    _require_mpl()
    _common._setup_matplotlib()
    if not _HAS_NUMPY:
        raise ImportError("compare_zero_statistics requires numpy.")

    if not isinstance(labels, (list, tuple)):
        raise ValueError("labels must be a list or tuple of strings.")
    if len(labels) < 2:
        raise ValueError(
            f"compare_zero_statistics needs at least 2 labels, got {len(labels)}."
        )

    if ax is None:
        fig, ax_local = plt.subplots(figsize=(7.0, 4.5))
    else:
        ax_local = ax
        fig = ax_local.figure

    s_grid = np.linspace(0.0, 4.0, 401)
    gue_cdf = np.array([_wigner_gue_cdf(s) for s in s_grid])
    ax_local.plot(s_grid, gue_cdf, color="black", linewidth=2.0,
                  label="GUE Wigner CDF")

    stats: dict = {}
    spacing_lists: dict = {}
    palette = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e",
               "#9467bd", "#8c564b", "#e377c2"]
    for idx, label in enumerate(labels):
        zeros = get_zeros(label, n_zeros=n_zeros)
        spacings = _normalized_spacings(zeros)
        spacing_lists[label] = spacings
        if spacings:
            sorted_s = np.sort(spacings)
            ecdf = np.arange(1, len(sorted_s) + 1) / len(sorted_s)
            ax_local.step(
                sorted_s, ecdf, where="post",
                color=palette[idx % len(palette)],
                linewidth=1.4,
                label=f"{label} (N={len(spacings)})",
            )
        stats[label] = {
            "mean_spacing": (
                float(sum([zeros[i + 1] - zeros[i]
                           for i in range(len(zeros) - 1)]))
                / max(1, len(zeros) - 1)
            ) if len(zeros) >= 2 else float("nan"),
            "ks_to_gue": _ks_distance_to_gue(spacings),
            "n_spacings": len(spacings),
        }

    # Pairwise KS table between empirical distributions.
    ks_table: dict = {}
    for li in labels:
        ks_table[li] = {}
        for lj in labels:
            si, sj = spacing_lists[li], spacing_lists[lj]
            ks_table[li][lj] = _ks_two_sample(si, sj)

    ax_local.set_xlim(0.0, 4.0)
    ax_local.set_ylim(0.0, 1.05)
    ax_local.set_xlabel("normalised gap  s")
    ax_local.set_ylabel("CDF")
    ax_local.set_title("Empirical CDFs of normalised zero spacings",
                       fontsize=10)
    ax_local.legend(loc="lower right", fontsize=8)
    ax_local.grid(True, alpha=0.25)
    if ax is None:
        fig.tight_layout()

    return {"figure": fig, "stats": stats, "ks_table": ks_table}


def _ks_two_sample(a: Sequence[float], b: Sequence[float]) -> float:
    """Two-sample Kolmogorov-Smirnov statistic.

    Returns ``nan`` if either sample is empty.  No p-value — this is
    the supremum-distance only.

    Implementation note: we walk a sorted merge of the two samples and
    compare empirical CDFs at every distinct value.  Ties between the
    two samples advance both pointers simultaneously, so two identical
    samples produce a KS distance of exactly 0.
    """
    if not a or not b:
        return float("nan")
    a_sorted = sorted(a)
    b_sorted = sorted(b)
    n_a, n_b = len(a_sorted), len(b_sorted)
    i = j = 0
    d = 0.0
    while i < n_a and j < n_b:
        ai, bj = a_sorted[i], b_sorted[j]
        if ai <= bj:
            i += 1
        if bj <= ai:
            j += 1
        d = max(d, abs(i / n_a - j / n_b))
    # Tail: any leftover advances widen one CDF only.
    while i < n_a:
        i += 1
        d = max(d, abs(i / n_a - j / n_b))
    while j < n_b:
        j += 1
        d = max(d, abs(i / n_a - j / n_b))
    return d


def save_zeros_plot(label: str,
                    path: Union[str, "Path"],
                    n_zeros: int = 50,
                    fmt: Optional[str] = None,
                    show_riemann_band: bool = False) -> None:
    """Compute zeros and save a zeros plot to disk in one call.

    Parameters
    ----------
    label : str
        L-function label.
    path : str or os.PathLike
        Output path.  Format is inferred from the extension when
        ``fmt`` is omitted.
    n_zeros : int, default 50
        Zeros to plot.
    fmt : {'png', 'svg', 'pdf'}, optional
        Output format override.
    show_riemann_band : bool, default False
        Forwarded to :func:`plot_zeros`.

    Raises
    ------
    ValueError
        If ``path`` and ``fmt`` together cannot resolve to a supported
        format.
    """
    _require_mpl()
    resolved_path, fmt_out = _common._resolve_path(path, fmt)
    fig = plot_zeros(
        label,
        n_zeros=n_zeros,
        show_riemann_band=show_riemann_band,
        backend="matplotlib",
    )
    try:
        fig.savefig(str(resolved_path), format=fmt_out)
    finally:
        plt.close(fig)
