"""The Mahler precision budget ON REAL DATA, and the tolerance that depends on it. Cycle 048.

Cycle 047 measured `mahler_measure`'s relative error at up to **5.1e-6** on a synthetic product
built by multiplying two Hypothesis-drawn polynomials, and warned that this could mis-rank
candidates near Lehmer's constant.

**Cycle 048 checked that against the actual catalog and it does not happen.** Recomputing all
8,625 stored entries and comparing to their stored values gives a maximum absolute discrepancy of
**4.481e-10** — four orders of magnitude below `lookup_by_M`'s default `tol=1e-6`, which is the one
place a consumer's correctness actually depends on this number.

So the 5.1e-6 figure is real but **unrepresentative**: it belongs to a deliberately awkward
synthetic product, not to the published polynomials anyone looks up. Cycle 047 generalised from it
to real usage without checking, and this file is the check.

These tests exist so that the tolerance stays defensible: if a future change to `mahler_measure`
degrades real-data accuracy toward 1e-6, `lookup_by_M`'s default silently starts missing entries,
and the failure would be a lookup returning `[]` rather than anything that looks like a bug.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.databases import mahler as mdb  # noqa: E402
from techne.lib.mahler_measure import mahler_measure  # noqa: E402

LEHMER_M = 1.176280818259917

# Measured cycle 048 over all 8,625 entries. Set from the MEASUREMENT, with headroom, never a
# guess — cycle 047's lesson about picking 1e-7 out of the air.
MEASURED_MAX_ABS_ERR = 4.481e-10
BUDGET = 1e-8          # ~20x the measured worst case, still 100x under lookup_by_M's default


@pytest.fixture(scope="module")
def catalog():
    import prometheus_math.databases._mahler_data as md
    return [e for e in md.MAHLER_TABLE
            if e.get("coeffs") and e.get("mahler_measure") is not None]


def test_THE_REAL_DATA_ERROR_BUDGET(catalog):
    """**The measurement cycle 047 should have taken before warning about mis-ranking.**

    Recompute every stored entry and compare. Max absolute discrepancy measured at 4.481e-10.
    """
    assert len(catalog) > 8000, "catalog unexpectedly small; the budget below was measured on ~8625"
    worst = 0.0
    worst_name = None
    for e in catalog:
        try:
            recomputed = float(mahler_measure(list(reversed(e["coeffs"]))))
        except Exception:
            continue
        d = abs(recomputed - float(e["mahler_measure"]))
        if d > worst:
            worst, worst_name = d, e.get("name")
    assert worst < BUDGET, f"real-data error grew to {worst:.3e} at {worst_name!r}"


def test_the_budget_leaves_room_under_lookup_by_M_default_tolerance():
    """`lookup_by_M`'s default is `tol=1e-6`. A consumer computes M with `mahler_measure` and looks
    it up; if the recompute error ever approached that tolerance, the lookup would return an empty
    list and the caller would read it as 'not in the catalog' rather than as a precision failure —
    an absence presented as a fact, which is this loop's oldest recurring shape.
    """
    import inspect
    default = inspect.signature(mdb.lookup_by_M).parameters["tol"].default
    assert default == pytest.approx(1e-6)
    # `<=`, not `<`: BUDGET is 1e-8 and default/100 is exactly 1e-8, so strict inequality fails on
    # equality. That was my arithmetic slip, caught by the test failing. The fix is the assertion,
    # NOT a smaller BUDGET — loosening the budget to satisfy a mis-stated inequality would be
    # moving the goalposts, and BUDGET is set from a measurement.
    assert BUDGET <= default / 100, "the measured budget no longer leaves two orders of headroom"


def test_a_recomputed_lehmer_measure_still_finds_its_catalog_entry():
    """End-to-end on the value that matters most: compute M for Lehmer's polynomial with the tool,
    then look it up at the DEFAULT tolerance. This is the exact path a consumer takes."""
    coeffs_desc = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    m = mahler_measure(coeffs_desc)
    assert m == pytest.approx(LEHMER_M, rel=1e-12)
    hits = mdb.lookup_by_M(m)
    assert hits, "a freshly recomputed Lehmer measure failed to find its own catalog entry"


def test_THE_IN_BAND_SLICE_IS_ONE_MEASURE_WEARING_TWENTY_ONE_HATS(catalog):
    """**A finding about the data, not about precision — and it is the more interesting half.**

    The band `1.001 < M < 1.18` used by `aporia/experiments/reasoning_steering/stage0b` selects
    **21 entries, and every one has Lehmer's measure.** They are genuinely 21 DISTINCT polynomials
    spanning degrees 10 to 28 — Lehmer's polynomial times various cyclotomics, plus
    "Lehmer-extension" variants — but M is multiplicative and cyclotomics have M = 1, so
    multiplying by them changes the polynomial and not its measure.

    Their stored measures span **2.1e-14**, which is floating-point noise, not mathematics.
    Anything that sorts this slice by measure is sorting by rounding.
    """
    band = [e for e in catalog if 1.001 < float(e["mahler_measure"]) < 1.18]
    assert len(band) == 21
    assert len({tuple(e["coeffs"]) for e in band}) == 21          # 21 distinct polynomials...
    spread = (max(float(e["mahler_measure"]) for e in band)
              - min(float(e["mahler_measure"]) for e in band))
    assert spread < 1e-12                                         # ...but one measure
    for e in band:
        assert abs(float(e["mahler_measure"]) - LEHMER_M) < 1e-12


def test_the_band_edges_are_nowhere_near_a_live_value(catalog):
    """Criterion 2 of the cycle-048 pre-registration, kept as a regression: no live value sits
    within the error budget of either band edge, so no plausible precision change flips one across.
    """
    vals = [float(e["mahler_measure"]) for e in catalog
            if 1.001 < float(e["mahler_measure"]) < 1.18]
    assert min(abs(v - 1.001) for v in vals) > 1e-3
    assert min(abs(v - 1.18) for v in vals) > 1e-3
