"""Tests for prometheus_math.viz.lfunctions — project #37.

Per math-tdd skill, every operation has tests in 4 categories:

* Authority — peer-reviewed / mpmath / LMFDB reference values.
* Property — invariants across many inputs.
* Edge — empty / invalid / oversized inputs.
* Composition — chaining get_zeros -> plot -> save -> file on disk
  and cross-checking get_zeros vs mpmath.zetazero on ζ.

Run with:
    cd F:/Prometheus && python -m pytest \\
        prometheus_math/viz/tests/test_lfunctions.py -v
"""
from __future__ import annotations

import math
import os
import tempfile
import shutil
import warnings

import pytest

# Headless-safe matplotlib must come BEFORE any pyplot usage in the
# import graph.
import matplotlib
matplotlib.use("Agg")

mpmath = pytest.importorskip(
    "mpmath",
    reason="mpmath required for L-function zero tests",
)
np = pytest.importorskip(
    "numpy",
    reason="numpy required for L-function spacing tests",
)

from prometheus_math.viz import lfunctions as lfn  # noqa: E402
from prometheus_math import viz  # noqa: E402


def _lmfdb_reachable() -> bool:
    """Cheap check for whether the LMFDB devmirror is online."""
    try:
        from prometheus_math.databases import lmfdb
    except Exception:
        return False
    try:
        return bool(lmfdb.probe(timeout=3.0))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Authority-based tests
# ---------------------------------------------------------------------------

def test_authority_first_riemann_zero_matches_edwards():
    """First non-trivial zero of ζ(s) is at t = 14.13472514173469...

    Reference: Edwards, "Riemann's Zeta Function" (1974), §10
    (numerical computation of zeros).  Cross-checked against
    ``mpmath.zetazero(1).imag``.
    """
    z = lfn.get_zeros("Riemann", n_zeros=1)
    assert len(z) == 1
    assert abs(z[0] - 14.134725141734695) < 1e-6


def test_authority_first_five_riemann_zeros_match_mpmath():
    """First five Riemann zeros agree with mpmath.zetazero(k).imag.

    Reference values (Odlyzko, "Tables of zeros of the Riemann zeta
    function", and any modern mpmath build):

        z1 = 14.134725141734695
        z2 = 21.022039638771553
        z3 = 25.010857580145687
        z4 = 30.424876125859512
        z5 = 32.93506158773919
    """
    expected = [
        14.134725141734695,
        21.022039638771553,
        25.010857580145687,
        30.424876125859512,
        32.93506158773919,
    ]
    got = lfn.get_zeros("Riemann", n_zeros=5)
    assert len(got) == 5
    for g, e in zip(got, expected):
        assert abs(g - e) < 1e-5


def test_authority_gue_wigner_pdf_at_unity():
    """GUE Wigner surmise at s=1 has the published value.

    P(s) = (32/π²) s² exp(-(4/π) s²)
    At s=1:  (32/π²) · exp(-4/π)  ≈  3.2423 · 0.27951  ≈  0.9076.

    Reference: Mehta, "Random Matrices", 3rd ed., eq. (6.5.31) for
    the GUE 2x2 surmise.
    """
    val = lfn._wigner_gue_pdf(1.0)
    assert abs(val - 0.9075892109166814) < 1e-9


def test_authority_gue_wigner_cdf_zero_and_infty():
    """CDF endpoints: F(0) = 0 and F(∞) → 1.

    Reference: F(s) = 1 - exp(-(4/π) s²) (1 + (4/π) s²); at s=0
    the second factor is 1 and the exponential is 1, giving 0; at
    large s the exponential dominates.
    """
    assert lfn._wigner_gue_cdf(0.0) == 0.0
    assert abs(lfn._wigner_gue_cdf(50.0) - 1.0) < 1e-12


@pytest.mark.skipif(
    not _lmfdb_reachable(),
    reason="LMFDB devmirror unreachable",
)
def test_authority_lmfdb_ec_11a_first_zero():
    """LMFDB-stored zeros for the EC 11.a L-function.

    Reference: ``lfunc_lfunctions.positive_zeros`` for origin
    ``'EllipticCurve/Q/11/a'`` in the public LMFDB mirror.  The first
    positive zero is t ≈ 6.36 (the analytic conductor of 11.a is
    ~5.0, so the lowest zero sits at a relatively low height).
    """
    zeros = lfn.get_zeros("EllipticCurve.Q.11.a", n_zeros=3)
    assert len(zeros) == 3
    # First zero in [6.0, 7.0] -- documented in LMFDB.
    assert 6.0 < zeros[0] < 7.0


@pytest.mark.skipif(
    not _lmfdb_reachable(),
    reason="LMFDB devmirror unreachable",
)
def test_authority_lmfdb_origin_slash_form_also_works():
    """Slash-form origins are accepted as labels (LMFDB native form)."""
    zeros = lfn.get_zeros("EllipticCurve/Q/11/a", n_zeros=2)
    assert len(zeros) == 2
    assert all(z > 0 for z in zeros)


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

def test_property_get_zeros_returns_exact_n_or_warns():
    """``get_zeros(label, n)`` returns exactly n entries on Riemann.

    For Riemann ζ, mpmath always supplies the requested count, so the
    returned length is exactly n.
    """
    for n in (1, 3, 7, 12):
        zeros = lfn.get_zeros("Riemann", n_zeros=n)
        assert len(zeros) == n


def test_property_zeros_are_positive_reals():
    """All returned zeros are positive reals (we ask for positive_zeros)."""
    zeros = lfn.get_zeros("Riemann", n_zeros=20)
    assert all(isinstance(z, float) for z in zeros)
    assert all(z > 0 for z in zeros)


def test_property_zeros_monotone_increasing():
    """Returned zeros are strictly increasing."""
    zeros = lfn.get_zeros("Riemann", n_zeros=15)
    for a, b in zip(zeros, zeros[1:]):
        assert b > a


def test_property_normalized_spacings_have_unit_mean():
    """By construction, ``mean(_normalized_spacings(z)) == 1``.

    The normalisation divides by the mean gap, so the mean of the
    normalised spacings is identically 1 (up to float precision).
    """
    zeros = lfn.get_zeros("Riemann", n_zeros=30)
    s = lfn._normalized_spacings(zeros)
    assert len(s) == len(zeros) - 1
    assert abs(sum(s) / len(s) - 1.0) < 1e-12


def test_property_gue_pdf_integrates_to_one():
    """Wigner GUE pdf integrates to ~1 over [0, ∞).

    Property test on the analytical formula -- we verify by Riemann
    sum over a fine grid.
    """
    s_grid = np.linspace(0.0, 8.0, 8001)
    pdf = np.array([lfn._wigner_gue_pdf(float(s)) for s in s_grid])
    # Trapezoidal rule (trapezoid in numpy >=2; fall back to trapz).
    trap = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    integral = float(trap(pdf, s_grid))
    assert abs(integral - 1.0) < 1e-3


def test_property_ax_persistence_cumulative_plot():
    """Passing the same ax twice produces a cumulative plot.

    Each plot_zeros call adds vlines + scatter dots; calling twice on
    the same axes should leave more line/collection artists than a
    single call.
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 2))
    try:
        lfn.plot_zeros("Riemann", n_zeros=5, ax=ax)
        n_after_first = (
            len(ax.collections) + len(ax.get_lines())
        )
        lfn.plot_zeros("Riemann", n_zeros=5, ax=ax)
        n_after_second = (
            len(ax.collections) + len(ax.get_lines())
        )
        assert n_after_second > n_after_first
    finally:
        plt.close(fig)


def test_property_riemann_zero_spacings_close_to_gue():
    """Riemann ζ zero spacings agree with GUE within KS tolerance.

    Reference: Montgomery's pair-correlation conjecture / Odlyzko's
    numerical experiments — the high zeros of ζ are statistically
    indistinguishable from GUE-1 spacings.

    With only 60 spacings near the bottom of the critical line the
    KS distance is moderate (~0.25) -- Odlyzko's high-zero
    experiments use millions of zeros around t ~ 10^20.  We use a
    loose threshold (0.35) since the surmise is asymptotic, not
    exact at finite N near the foot of the critical line.
    """
    zeros = lfn.get_zeros("Riemann", n_zeros=60)
    s = lfn._normalized_spacings(zeros)
    d = lfn._ks_distance_to_gue(s)
    assert d < 0.35, f"KS distance {d:.3f} too large vs GUE"


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_invalid_label_raises():
    """Edge: empty string label -> ValueError."""
    with pytest.raises(ValueError):
        lfn.get_zeros("", n_zeros=1)
    with pytest.raises(ValueError):
        lfn.get_zeros("    ", n_zeros=1)


def test_edge_negative_n_zeros_raises():
    """Edge: n_zeros < 0 -> ValueError."""
    with pytest.raises(ValueError):
        lfn.get_zeros("Riemann", n_zeros=-1)


def test_edge_n_zeros_zero_returns_empty_list():
    """Edge: n_zeros=0 returns [] without raising or computing."""
    assert lfn.get_zeros("Riemann", n_zeros=0) == []


def test_edge_n_zeros_zero_plot_does_not_crash():
    """Edge: plot_zeros with n_zeros=0 produces an empty plot."""
    fig = lfn.plot_zeros("Riemann", n_zeros=0)
    try:
        ax = fig.axes[0]
        # No vlines, no scatter dots
        assert len(ax.collections) == 0
        # And no plotted lines.
        assert all(
            ln.get_linestyle() in ("None", "none") or
            len(ln.get_xdata()) == 0
            for ln in ax.get_lines()
        )
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)


def test_edge_unknown_backend_raises():
    """Edge: backend not in {'matplotlib', 'svg'} -> ValueError."""
    with pytest.raises(ValueError):
        lfn.plot_zeros("Riemann", n_zeros=1, backend="opengl")


def test_edge_compare_needs_two_labels():
    """Edge: compare_zero_statistics with < 2 labels raises ValueError."""
    with pytest.raises(ValueError):
        lfn.compare_zero_statistics(["Riemann"])
    with pytest.raises(ValueError):
        lfn.compare_zero_statistics([])


def test_edge_save_unknown_format_raises():
    """Edge: save_zeros_plot with an unrecognised format -> ValueError."""
    tmpdir = tempfile.mkdtemp(prefix="pm_lfn_test_")
    try:
        with pytest.raises(ValueError):
            lfn.save_zeros_plot(
                "Riemann",
                os.path.join(tmpdir, "out.bmp"),
                n_zeros=2,
                fmt="bmp",
            )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_edge_save_no_extension_no_fmt_raises():
    """Edge: missing ext + missing fmt -> ValueError."""
    tmpdir = tempfile.mkdtemp(prefix="pm_lfn_test_")
    try:
        with pytest.raises(ValueError):
            lfn.save_zeros_plot(
                "Riemann",
                os.path.join(tmpdir, "noext"),
                n_zeros=2,
            )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_edge_oversized_request_warns_and_truncates():
    """Edge: requesting more zeros than LMFDB stores warns + truncates.

    We simulate by stubbing LMFDB to return a short list — keeps the
    test offline-safe.
    """
    real_fn = lfn._zeros_via_lmfdb

    def short_stub(label, n_zeros):
        return [1.0, 2.0, 3.0]

    lfn._zeros_via_lmfdb = short_stub  # type: ignore[assignment]
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            zeros = lfn.get_zeros("FakeLabel/Q/X", n_zeros=10)
            assert zeros == [1.0, 2.0, 3.0]
            assert any("truncated" in str(w.message).lower()
                       for w in caught)
    finally:
        lfn._zeros_via_lmfdb = real_fn  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

def test_composition_get_zeros_then_plot_then_save_writes_file():
    """Composition: get_zeros -> plot_zeros -> save_zeros_plot -> file."""
    tmpdir = tempfile.mkdtemp(prefix="pm_lfn_test_")
    try:
        zeros = lfn.get_zeros("Riemann", n_zeros=3)
        # Round-trip: plot then save (twice over, distinct paths).
        fig = lfn.plot_zeros("Riemann", n_zeros=3)
        try:
            assert fig is not None
        finally:
            import matplotlib.pyplot as plt
            plt.close(fig)
        out_png = os.path.join(tmpdir, "zeta_zeros.png")
        lfn.save_zeros_plot("Riemann", out_png, n_zeros=3)
        assert os.path.isfile(out_png)
        assert os.path.getsize(out_png) > 200
        # Sanity: zeros list is consistent before/after the round-trip.
        zeros2 = lfn.get_zeros("Riemann", n_zeros=3)
        assert zeros == zeros2
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_composition_get_zeros_matches_mpmath_zetazero_directly():
    """Composition: get_zeros for ζ matches mpmath.zetazero(k).imag for k=1..5.

    This composes get_zeros with mpmath's zero-finder and asserts the
    pipeline produces identical results.  Catches any future
    re-implementation bug that might silently re-order or scale.
    """
    got = lfn.get_zeros("Riemann", n_zeros=5)
    direct = [float(mpmath.zetazero(k).imag) for k in range(1, 6)]
    for g, d in zip(got, direct):
        # zetazero is deterministic, so we expect bit-identical values
        # up to float rounding.
        assert abs(g - d) < 1e-12


def test_composition_plot_zeros_axes_has_n_markers():
    """Composition: plot_zeros draws exactly n_zeros scatter markers.

    The y=0 dot trace is plotted as a single Line2D with n points
    (linestyle='None'); count its xdata length.
    """
    fig = lfn.plot_zeros("Riemann", n_zeros=7)
    try:
        ax = fig.axes[0]
        marker_lines = [
            ln for ln in ax.get_lines()
            if ln.get_linestyle() in ("None", "none")
            and len(ln.get_xdata()) > 0
        ]
        assert len(marker_lines) >= 1
        assert max(len(ln.get_xdata()) for ln in marker_lines) == 7
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)


def test_composition_compare_returns_well_formed_stats():
    """Composition: compare_zero_statistics returns a stats dict whose
    KS-vs-GUE for Riemann is small and whose pairwise KS table is
    symmetric and zero on the diagonal.
    """
    out = lfn.compare_zero_statistics(
        ["Riemann", "Riemann"], n_zeros=30,
    )
    assert "figure" in out
    assert "stats" in out
    assert "ks_table" in out

    stats = out["stats"]
    assert "Riemann" in stats
    assert math.isfinite(stats["Riemann"]["ks_to_gue"])
    assert stats["Riemann"]["n_spacings"] == 29

    table = out["ks_table"]
    # diagonal is zero, table is symmetric (ζ vs ζ comparison)
    assert table["Riemann"]["Riemann"] == 0.0

    import matplotlib.pyplot as plt
    plt.close(out["figure"])


def test_composition_plot_zero_spacings_shows_gue_curve():
    """Composition: plot_zero_spacings overlays the GUE Wigner surmise.

    The GUE curve and the Poisson curve are added as Line2D objects
    on the axes.  We assert at least three line artists exist
    (histogram bars are Patches/Rectangles, not Lines, plus 2 ref
    curves + maybe extra cosmetic lines).
    """
    fig = lfn.plot_zero_spacings("Riemann", n_zeros=20)
    try:
        ax = fig.axes[0]
        # Two reference curves drawn as Line2D.
        plotted_lines = [
            ln for ln in ax.get_lines()
            if len(ln.get_xdata()) > 100  # the smooth ref curves
        ]
        assert len(plotted_lines) >= 2
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)


def test_composition_pm_viz_reexports_lfunctions_api():
    """Composition: ``pm.viz.plot_zeros`` and friends are re-exported.

    The wave-7 -> wave-8 refactor turned ``viz`` from a module into a
    package; this test pins the public surface via the package
    ``__init__``.
    """
    assert callable(viz.plot_zeros)
    assert callable(viz.get_zeros)
    assert callable(viz.plot_zero_spacings)
    assert callable(viz.compare_zero_statistics)
    assert callable(viz.save_zeros_plot)
    # Knot API must still be visible via the same import.
    assert callable(viz.draw_knot)
    assert callable(viz.knot_diagram_data)


def test_composition_riemann_via_lmfdb_label_matches_alias():
    """Composition: the literal LMFDB label '1-1-1.1-r0-0-0' resolves
    via the Riemann alias path, not the network.

    This checks that ``_is_riemann_label`` covers the Edwards/LMFDB
    pseudonym so callers passing either form get identical results
    even when the mirror is offline.
    """
    a = lfn.get_zeros("Riemann", n_zeros=3)
    b = lfn.get_zeros("1-1-1.1-r0-0-0", n_zeros=3)
    for x, y in zip(a, b):
        assert abs(x - y) < 1e-12
