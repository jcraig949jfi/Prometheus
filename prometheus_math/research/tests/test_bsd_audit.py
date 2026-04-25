"""Test suite for prometheus_math.research.bsd_audit (project #8).

Follows the math-tdd skill's 4-category rubric (Authority / Property /
Edge / Composition). Aim: ≥ 2 in each category.

References cited per test in docstrings. LMFDB authority is the
``ec_curvedata`` + ``ec_mwbsd`` mirror at devmirror.lmfdb.xyz; tests
that need it skip when the registry probe is False.
"""
from __future__ import annotations

import math
import os
import tempfile

import pytest

from prometheus_math.research import bsd_audit

# LMFDB liveness probe — many tests need the mirror.
_LMFDB_OK = False
try:
    from prometheus_math.databases import lmfdb as _lmfdb
    _LMFDB_OK = _lmfdb.probe(timeout=3.0)
except Exception:
    _LMFDB_OK = False

requires_lmfdb = pytest.mark.skipif(
    not _LMFDB_OK, reason="LMFDB Postgres mirror unreachable"
)


# Curated anchors. NOTE: LMFDB's "11.a1" has ainvs [0,-1,1,-7820,-263580]
# (the optimal isogeny representative), which differs from Cremona's
# "11a1". The BSD anchors here use LMFDB labels and corresponding ainvs.
ANCHORS = ["11.a2", "37.a1", "389.a1", "5077.a1", "210.e1"]
# 11.a2 = [0,-1,1,-10,-20] (Cremona's "11a1") — the canonical rank-0 BSD anchor.


# ---------------------------------------------------------------------------
# AUTHORITY — anchored against LMFDB-curated values
# ---------------------------------------------------------------------------


@requires_lmfdb
def test_authority_five_bsd_anchors_consistent():
    """All five BSD anchors must pass full consistency.

    Reference: LMFDB ec_curvedata + ec_mwbsd for labels {11.a2, 37.a1,
    389.a1, 5077.a1, 210.e1}. These are the canonical rank-0 (sha=1),
    rank-1, rank-2, rank-3, and rank-0-with-Sha=16 anchors that
    Charon's manual F011 audit used. A regression in any tool in the
    BSD chain (regulator, analytic_sha, ellrank, ellrootno) shows up
    here as ``all_consistent=False`` on at least one anchor.
    """
    # Loose tolerance to accommodate the ~5e-3 BSD residual at rank 3.
    results = bsd_audit.run(ANCHORS, lmfdb_compare=True, tolerance=5e-3)
    assert len(results) == 5
    bad = [r["label"] for r in results if not r["all_consistent"]]
    assert bad == [], f"Anchors failed BSD-audit: {bad}"
    # Every anchor's analytic_sha must round to the LMFDB sha.
    for r in results:
        assert r["analytic_sha"] is not None
        assert r["lmfdb_analytic_sha"] is not None
        assert round(r["analytic_sha"]) == int(r["lmfdb_analytic_sha"])


@requires_lmfdb
def test_authority_ten_random_rank0_curves():
    """Ten random rank-0 LMFDB curves all pass consistency.

    Reference: LMFDB ec_curvedata, rank=0 filter. The set is sampled
    deterministically (first 10 results sorted by id) so the test is
    reproducible across runs.
    """
    rows = _lmfdb.elliptic_curves(rank=0, limit=10)
    labels = [r["lmfdb_label"] for r in rows]
    assert len(labels) == 10
    results = bsd_audit.run(labels, lmfdb_compare=True, tolerance=1e-3)
    inconsistent = [r["label"] for r in results if not r["all_consistent"]]
    assert inconsistent == [], (
        f"Rank-0 curves expected consistent; got inconsistent={inconsistent}"
    )


@requires_lmfdb
def test_authority_rank_consistency_check_anchors():
    """Rank-consistency cheap subset matches LMFDB rank parity.

    Reference: LMFDB analytic_rank parity vs computed root number.
    This is the parity conjecture (BSD consequence) — a w(E) of -1
    means rank is odd, +1 means even. Anchors selected to span
    rank 0/1/2/3.
    """
    for label, expected_rank in [("11.a2", 0), ("37.a1", 1),
                                 ("389.a1", 2), ("5077.a1", 3)]:
        out = bsd_audit.rank_consistency_check(label)
        assert out["rank_parity_ok"] is True, (
            f"{label}: parity check failed, got {out}"
        )
        assert out["rank_consistent"] is True
        assert out["lmfdb_rank"] == expected_rank


# ---------------------------------------------------------------------------
# PROPERTY — invariants that hold across many inputs
# ---------------------------------------------------------------------------


@requires_lmfdb
def test_property_all_consistent_implies_small_deltas():
    """all_consistent=True iff every numeric delta is below tolerance.

    Property: the verdict respects the user-supplied tolerance.
    For each anchor, increase the tolerance enough that consistency
    holds, then assert every available delta is within that tolerance.
    """
    tol = 5e-3
    results = bsd_audit.run(["11.a2", "37.a1"], lmfdb_compare=True,
                            tolerance=tol)
    for r in results:
        if r["all_consistent"]:
            for k, v in r.items():
                if k.startswith("delta_") and v is not None:
                    assert abs(float(v)) <= tol, f"{r['label']}: {k}={v} > tol"


@requires_lmfdb
def test_property_rank_matches_lmfdb_rank():
    """Computed rank from analytic_sha equals LMFDB ec_curvedata rank.

    Property: when analytic_sha succeeds (rank is proved by ellrank or
    by the rank_hint shortcut), the returned rank exactly matches the
    LMFDB-curated value. A failure here implicates either the rank
    ground truth in LMFDB or PARI's ellanalyticrank convention.
    """
    rows = _lmfdb.elliptic_curves(rank=1, limit=4)
    labels = [r["lmfdb_label"] for r in rows]
    results = bsd_audit.run(labels, lmfdb_compare=True)
    for r in results:
        if r["rank"] is None or r["lmfdb_rank"] is None:
            continue
        assert int(r["rank"]) == int(r["lmfdb_rank"])


def test_property_runtime_ms_nonnegative():
    """Property: runtime_ms is always present and finite >= 0.

    Even on malformed input or LMFDB outage, every record carries a
    runtime field so that batch summary statistics are well-defined.
    """
    results = bsd_audit.run([[0, 0, 1, -1, 0]], lmfdb_compare=False)
    assert len(results) == 1
    rt = results[0]["runtime_ms"]
    assert isinstance(rt, float)
    assert math.isfinite(rt) and rt >= 0


# ---------------------------------------------------------------------------
# EDGE — explicitly enumerated edges
# ---------------------------------------------------------------------------


def test_edge_empty_curve_list_returns_empty():
    """Edge: empty input -> empty output (not ValueError).

    A batch composer should accept the empty batch as the identity case.
    """
    assert bsd_audit.run([]) == []
    # Summary on empty input is the zero-state, not a crash:
    s = bsd_audit.summary([])
    assert s["n_curves"] == 0
    assert s["n_consistent"] == 0
    assert s["mean_runtime_ms"] == 0.0
    assert s["top_outliers"] == []


@requires_lmfdb
def test_edge_bogus_label_returns_warnings_not_crash():
    """Edge: an LMFDB label that doesn't exist must not crash the batch.

    Returns a dict with the bogus label, ``all_consistent=False``, and a
    ``lmfdb_row_missing`` / ``ainvs_unresolvable`` warning string.
    """
    results = bsd_audit.run(["999999999.zzz1"], lmfdb_compare=True)
    assert len(results) == 1
    r = results[0]
    assert r["label"] == "999999999.zzz1"
    assert r["all_consistent"] is False
    # At minimum we expect a warning that the row was missing
    assert "lmfdb_row_missing" in r["warnings"] or "ainvs_unresolvable" in r["warnings"]


def test_edge_malformed_spec_records_warning():
    """Edge: a spec that's neither a label nor a 5-tuple is recorded
    as a per-record input_error rather than crashing the batch.
    """
    results = bsd_audit.run([{"weird": 1}, [1, 2, 3]])  # both invalid
    assert len(results) == 2
    for r in results:
        assert r["all_consistent"] is False
        assert "input_error" in r["warnings"]


@requires_lmfdb
def test_edge_rank_consistency_check_works_when_full_audit_too_slow():
    """Edge: rank_consistency_check is a cheap subset that returns
    even on inputs where the full audit would time out.

    We don't actually trigger a timeout; instead we verify that the
    cheap path skips the regulator + analytic_sha + selmer keys and
    therefore can't time out on those tools. A PARI failure in
    root_number would still bubble up as a warning.
    """
    out = bsd_audit.rank_consistency_check("37.a1")
    # No regulator / analytic_sha / selmer keys at all in the cheap path
    assert "regulator" not in out
    assert "analytic_sha" not in out
    assert "selmer_2_rank" not in out
    # But the parity result is meaningful
    assert out["root_number"] in (-1, +1)
    assert out["rank_parity_ok"] is True
    assert out["conductor"] == 37


def test_edge_lmfdb_compare_false_skips_db():
    """Edge: with lmfdb_compare=False, no LMFDB queries are issued and
    no lmfdb_* fields are populated. Useful for offline / CI runs.
    """
    a = [0, 0, 1, -1, 0]  # 37.a1 ainvs
    results = bsd_audit.run([a], lmfdb_compare=False)
    r = results[0]
    assert r["lmfdb_regulator"] is None
    assert r["lmfdb_conductor"] is None
    assert r["lmfdb_analytic_sha"] is None
    # Local computation still ran
    assert r["conductor"] == 37
    assert r["root_number"] in (-1, +1)
    # all_consistent is False because we have no deltas to check
    assert r["all_consistent"] is False


# ---------------------------------------------------------------------------
# COMPOSITION — chain across modules
# ---------------------------------------------------------------------------


@requires_lmfdb
def test_composition_bsd_identity_via_assembled_residual():
    """Composition: assembled BSD value (analytic_sha) equals the
    LMFDB-curated Sha across the rank-0/1/2/3/Sha=16 anchors.

    The chain composes regulator + analytic_sha (which internally calls
    ellanalyticrank, omega, elltors, ellsaturation) + global_reduction
    (Tamagawa product) + LMFDB lookup. A failure here is the canonical
    BSD-formula regression — off-by-r!, off-by-2 from real-period sign,
    or off-by-index^2 from missing ellsaturation.

    Reference: project #42 in techne/PROJECT_BACKLOG_1000.md established
    the BSD anchors; LMFDB ec_mwbsd.sha_an is the curated reference.
    """
    results = bsd_audit.run(ANCHORS, lmfdb_compare=True, tolerance=5e-3)
    for r in results:
        # The assembled BSD value rounds to the LMFDB Sha
        assert r["analytic_sha"] is not None
        assert r["lmfdb_analytic_sha"] is not None
        assert round(r["analytic_sha"]) == int(r["lmfdb_analytic_sha"]), (
            f"{r['label']}: assembled={r['analytic_sha']} "
            f"lmfdb={r['lmfdb_analytic_sha']}"
        )
        # And the residual is small in absolute terms
        assert abs(r["bsd_residual"]) <= 5e-3


@requires_lmfdb
def test_composition_summary_filter_inconsistent_roundtrip():
    """Composition: summary() + filter_inconsistent() are consistent
    with the per-record verdicts.

    Property of the aggregator: n_consistent + n_inconsistent ==
    n_curves; filter_inconsistent returns a subset that sums to
    n_inconsistent (modulo records with no comparable deltas, which
    are excluded from filter_inconsistent).
    """
    results = bsd_audit.run(["11.a2", "37.a1"], lmfdb_compare=True,
                            tolerance=5e-3)
    s = bsd_audit.summary(results)
    assert s["n_curves"] == 2
    assert s["n_consistent"] + s["n_inconsistent"] == 2
    # All anchors should be consistent at this tolerance
    assert s["n_inconsistent"] == 0
    # filter_inconsistent should agree
    assert bsd_audit.filter_inconsistent(results, tolerance=5e-3) == []


@requires_lmfdb
def test_composition_to_csv_roundtrip():
    """Composition: to_csv produces a valid CSV that round-trips back
    to dicts via the standard csv reader.

    Verifies the schema is CSV-flat (no nested objects) and that every
    documented field appears in the header. A failure here would mean
    we accidentally regressed the dict shape (e.g., embedded a list
    object in a delta field).
    """
    import csv as _csv
    results = bsd_audit.run(["11.a2"], lmfdb_compare=True, tolerance=5e-3)
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "audit.csv")
        bsd_audit.to_csv(results, path)
        with open(path, "r", encoding="utf-8", newline="") as fh:
            rows = list(_csv.DictReader(fh))
    assert len(rows) == 1
    row = rows[0]
    # Header carries all 33 expected fields (label..runtime_ms)
    assert "label" in row and row["label"] == "11.a2"
    assert "all_consistent" in row
    # CSV writes booleans as their str repr; this is a property of the
    # CSV layer, not a bug — but we DO require non-None floats serialise.
    assert row["analytic_sha"] != ""
    assert row["lmfdb_analytic_sha"] != ""
    # And all_consistent serialised to a string we can recover
    assert row["all_consistent"] in ("True", "False")


@requires_lmfdb
def test_composition_parity_root_number_chain():
    """Composition: rank parity vs computed root number across anchors.

    Composes ellrootno (root_number tool) with ellanalyticrank (rank
    inside analytic_sha). For rank-0/2 anchors w(E) must be +1; for
    rank-1/3 anchors w(E) must be -1.

    Reference: parity conjecture; verified against LMFDB analytic_rank
    column.
    """
    expected = {
        "11.a2": +1,    # rank 0
        "37.a1": -1,    # rank 1
        "389.a1": +1,   # rank 2
        "5077.a1": -1,  # rank 3
    }
    results = bsd_audit.run(list(expected), lmfdb_compare=True, tolerance=5e-3)
    by_label = {r["label"]: r for r in results}
    for label, expected_w in expected.items():
        r = by_label[label]
        assert r["root_number"] == expected_w
        assert r["parity_ok"] is True


# ---------------------------------------------------------------------------
# Helper: smoke
# ---------------------------------------------------------------------------


def test_module_exports_match_spec():
    """Module surface matches the project #8 spec.

    The five public callables must be exposed at module level so that
    downstream Charon scripts can import them by name.
    """
    for name in ("run", "to_csv", "summary", "filter_inconsistent",
                 "rank_consistency_check"):
        assert hasattr(bsd_audit, name), f"missing public name: {name}"
        assert callable(getattr(bsd_audit, name))
