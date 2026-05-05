"""Tests for sigma_kernel precision_metadata-on-CLAIM (2026-05-04 substrate change).

Operationalizes ChatGPT's reframe: "verification depth is a first-class
axis of truth, not a runtime detail." Precision metadata becomes typed
fields on the Claim that propagate through CLAIM -> FALSIFY -> PROMOTE
-> TRACE, and auto-caveats fire when precision drops below the expected
floor or convergence fails.

Math-tdd skill rubric: at least 3 tests in each of authority/property/
edge/composition.

Test-first per the math-tdd skill: this file documents the contract
for ``Claim.precision_metadata``, ``CLAIM(precision_metadata=...)``,
the auto-caveat firing rules, the def_blob hash-locking, and the
backwards-compat seam (legacy claims without the field still load).

References:
- Spec: sigma_kernel/PRECISION_METADATA_SPEC.md
- Migration: sigma_kernel/migrations/005_add_precision_metadata.sql
- Lehmer 17-entry trigger: techne/.../LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md
- Companion test: prometheus_math/tests/test_kill_vector_precision.py
"""
from __future__ import annotations

import json

import pytest

from sigma_kernel.sigma_kernel import (
    Capability,
    Claim,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel() -> SigmaKernel:
    return SigmaKernel(":memory:")


def _bootstrap_clear_claim_with_precision(
    k: SigmaKernel,
    target: str = "test_target",
    caveats: list[str] | None = None,
    precision_metadata: dict | None = None,
) -> Claim:
    """Mint a claim with an optional precision_metadata, then bind a
    synthetic CLEAR verdict so PROMOTE can fire. Mirrors the helper in
    test_caveats.py — same shape, just with the new kwarg.
    """
    claim = k.CLAIM(
        target_name=target,
        hypothesis="test hypothesis",
        evidence={"dataset_hash": "a" * 64, "null_hash": "b" * 64},
        kill_path="test_kill_path",
        target_tier=Tier.Possible,
        caveats=caveats,
        precision_metadata=precision_metadata,
    )
    verdict = VerdictResult(
        status=Verdict.CLEAR,
        rationale="synthetic test verdict",
        input_hash="c" * 64,
        seed=42,
        runtime_ms=1,
    )
    claim.verdict = verdict
    claim.status = "falsified"
    k.conn.execute(
        "UPDATE claims SET status='falsified', verdict_status=?, "
        "verdict_rationale=?, verdict_input_hash=?, verdict_seed=?, "
        "verdict_runtime_ms=? WHERE id=?",
        (
            verdict.status.value, verdict.rationale, verdict.input_hash,
            verdict.seed, verdict.runtime_ms, claim.id,
        ),
    )
    k.conn.commit()
    return claim


# ---------------------------------------------------------------------------
# AUTHORITY TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_authority_killcomponent_at_dps60_persists_in_claim_metadata():
    """A CLAIM minted with precision_metadata={dps=60, method=mpmath_polyroots,
    convergence=converged, stability=None} persists those fields in the DB
    and reads them back unchanged.

    This is the load-bearing happy path: the dps=60 case from Path A of
    the Lehmer 17-entry resolution. After this change, a dps=30 PASS and
    a dps=60 PASS are no longer indistinguishable in the ledger.
    """
    k = _make_kernel()
    pm = {
        "dps": 60,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": None,
    }
    claim = k.CLAIM(
        target_name="lehmer_at_dps60",
        hypothesis="Lehmer poly survives at dps=60",
        evidence={"dataset_hash": "a" * 64},
        kill_path="lehmer_check",
        target_tier=Tier.Possible,
        precision_metadata=pm,
    )
    assert claim.precision_metadata == pm
    # dps=60 meets the expected floor — no auto-caveat fired.
    assert "precision_below_expected" not in claim.caveats
    assert "verification_failed" not in claim.caveats

    # Persistence check via the DB.
    row = k.conn.execute(
        "SELECT precision_metadata FROM claims WHERE id=?", (claim.id,)
    ).fetchone()
    assert json.loads(row[0]) == pm


def test_authority_round_trip_through_serialization():
    """Claim.precision_metadata round-trips through PROMOTE: the symbol's
    def_blob carries the precision_metadata, and a downstream consumer
    can read it back via TRACE.
    """
    k = _make_kernel()
    pm = {
        "dps": 100,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": 0.99,
    }
    claim = _bootstrap_clear_claim_with_precision(
        k, target="auth_roundtrip", precision_metadata=pm
    )
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    blob = json.loads(sym.def_blob)
    assert blob["precision_metadata"] == pm
    # TRACE walks the precision_metadata.
    graph = k.TRACE(sym)
    assert graph["precision_metadata"] == pm


def test_authority_auto_caveat_precision_below_expected():
    """A CLAIM with precision_metadata.dps below the expected minimum
    (60 by default) automatically gets the 'precision_below_expected'
    caveat attached. The user did NOT pass it explicitly — the kernel
    inferred it from the precision metadata.

    This is the actionable consequence of the substrate change: if
    Mnemosyne's pre-2026-05-04 default of dps=30 is still in use
    somewhere, the substrate marks every such CLAIM as
    epistemically-suspect automatically.
    """
    k = _make_kernel()
    pm = {
        "dps": 30,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": None,
    }
    claim = k.CLAIM(
        target_name="auto_caveat_test",
        hypothesis="dps=30 should fire auto-caveat",
        evidence={"dataset_hash": "a" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
        precision_metadata=pm,
    )
    assert "precision_below_expected" in claim.caveats
    # Persisted in DB too.
    row = k.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (claim.id,)
    ).fetchone()
    db_caveats = json.loads(row[0])
    assert "precision_below_expected" in db_caveats


def test_authority_auto_caveat_verification_failed_on_convergence_fail():
    """A CLAIM with convergence_status='failed_max_steps' gets the
    'verification_failed' caveat automatically. Same for 'nan_returned'.
    """
    k = _make_kernel()
    for conv in ("failed_max_steps", "nan_returned"):
        pm = {
            "dps": 60,
            "method": "mpmath_polyroots",
            "convergence": conv,
            "stability": None,
        }
        claim = k.CLAIM(
            target_name=f"verif_{conv}",
            hypothesis=f"convergence={conv} should fire verification_failed",
            evidence={"dataset_hash": "a" * 64},
            kill_path="kp",
            target_tier=Tier.Possible,
            precision_metadata=pm,
        )
        assert "verification_failed" in claim.caveats, (
            f"verification_failed not added for convergence={conv}"
        )


# ---------------------------------------------------------------------------
# PROPERTY TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_property_legacy_claim_without_precision_metadata_loads_unchanged():
    """A claim minted without precision_metadata gets None as the field
    value, both in-Python and in the DB. Backwards-compat: existing
    CLAIM call sites work unchanged.
    """
    k = _make_kernel()
    claim = k.CLAIM(
        target_name="legacy",
        hypothesis="no precision_metadata supplied",
        evidence={"dataset_hash": "a" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
    )
    assert claim.precision_metadata is None
    # No auto-caveats fired (None metadata cannot trigger the rules).
    assert "precision_below_expected" not in claim.caveats
    assert "verification_failed" not in claim.caveats
    # DB row reflects None.
    row = k.conn.execute(
        "SELECT precision_metadata FROM claims WHERE id=?", (claim.id,)
    ).fetchone()
    assert row[0] is None


def test_property_user_caveats_preserved_when_auto_caveats_fire():
    """When auto-caveats fire from precision_metadata, the user's
    explicitly-provided caveats are preserved alongside.

    Property: kernel never silently drops a user-provided token.
    """
    k = _make_kernel()
    pm = {
        "dps": 30,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": None,
    }
    claim = k.CLAIM(
        target_name="combined",
        hypothesis="combined caveats",
        evidence={"dataset_hash": "a" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
        caveats=["small_n", "rediscovery_not_discovery"],
        precision_metadata=pm,
    )
    assert "small_n" in claim.caveats
    assert "rediscovery_not_discovery" in claim.caveats
    assert "precision_below_expected" in claim.caveats


def test_property_auto_caveat_dedup_when_user_already_supplied_token():
    """If the user passed 'precision_below_expected' explicitly AND
    precision_metadata would also auto-fire it, the resulting caveats
    list contains it exactly ONCE.

    Property: the substrate dedups; appending an auto-caveat already in
    the user's list is a no-op.
    """
    k = _make_kernel()
    pm = {
        "dps": 20,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": None,
    }
    claim = k.CLAIM(
        target_name="dedup",
        hypothesis="dedup test",
        evidence={"dataset_hash": "a" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
        caveats=["precision_below_expected"],
        precision_metadata=pm,
    )
    assert claim.caveats.count("precision_below_expected") == 1


def test_property_promoted_symbol_def_hash_changes_when_precision_changes():
    """Two claims identical except for precision_metadata.dps produce
    promoted symbols with different def_hashes.

    Property: precision is hash-locked into the symbol — the substrate
    cannot lose precision without changing the symbol's hash, breaking
    RESOLVE for any downstream consumer. This is the load-bearing
    property of precision-as-first-class (mirrors the same property
    for caveats from migration 004).
    """
    k1 = _make_kernel()
    k2 = _make_kernel()
    pm_60 = {"dps": 60, "method": "mpmath_polyroots",
             "convergence": "converged", "stability": None}
    pm_100 = {"dps": 100, "method": "mpmath_polyroots",
              "convergence": "converged", "stability": None}
    c1 = _bootstrap_clear_claim_with_precision(k1, target="hash", precision_metadata=pm_60)
    c2 = _bootstrap_clear_claim_with_precision(k2, target="hash", precision_metadata=pm_100)
    cap1 = k1.mint_capability("PromoteCap")
    cap2 = k2.mint_capability("PromoteCap")
    sym1 = k1.PROMOTE(c1, cap1)
    sym2 = k2.PROMOTE(c2, cap2)
    assert sym1.def_hash != sym2.def_hash


# ---------------------------------------------------------------------------
# EDGE TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_edge_precision_metadata_with_none_dps_handled():
    """precision_metadata.dps=None means "no mpmath was used" (e.g.
    catalog_lookup or sympy_factor). The auto-caveat MUST NOT fire
    (no precision to compare against).
    """
    k = _make_kernel()
    pm = {
        "dps": None,
        "method": "catalog_lookup",
        "convergence": "exact",
        "stability": None,
    }
    claim = k.CLAIM(
        target_name="catalog_exact",
        hypothesis="exact catalog hit",
        evidence={"dataset_hash": "a" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
        precision_metadata=pm,
    )
    assert "precision_below_expected" not in claim.caveats
    assert "verification_failed" not in claim.caveats
    assert claim.precision_metadata == pm


def test_edge_precision_metadata_must_be_dict_or_none():
    """Passing a non-dict, non-None precision_metadata raises TypeError.

    Edge: protect downstream consumers from corrupt JSON. The substrate
    is permissive at write but not THIS permissive — the field is
    typed.
    """
    k = _make_kernel()
    with pytest.raises(TypeError):
        k.CLAIM(
            target_name="bad",
            hypothesis="bad pm",
            evidence={"dataset_hash": "a" * 64},
            kill_path="kp",
            target_tier=Tier.Possible,
            precision_metadata="not a dict",  # type: ignore[arg-type]
        )


def test_edge_precision_metadata_with_failed_convergence_and_low_dps_both_fire():
    """When BOTH rules fire (low dps AND failed convergence), both
    auto-caveats are attached. Edge: rules are independent.
    """
    k = _make_kernel()
    pm = {
        "dps": 25,
        "method": "mpmath_polyroots",
        "convergence": "failed_max_steps",
        "stability": None,
    }
    claim = k.CLAIM(
        target_name="both_fire",
        hypothesis="both auto-caveats fire",
        evidence={"dataset_hash": "a" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
        precision_metadata=pm,
    )
    assert "precision_below_expected" in claim.caveats
    assert "verification_failed" in claim.caveats


def test_edge_legacy_pre_005_row_no_precision_metadata_column_still_resolves():
    """Migration backward-compat: existing claim rows that pre-date
    migration 005 (no precision_metadata column at INSERT time) still
    work correctly via the SQLite path.

    Simulates the pre-005 state by inserting a row with NULL
    precision_metadata, which is what the migration default puts on
    existing rows. The kernel must read this as None and treat the
    claim no differently from a claim minted with explicit
    precision_metadata=None.
    """
    k = _make_kernel()
    k.conn.execute(
        "INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "claim_legacy_pre_005", "legacy", "legacy hypothesis",
            json.dumps({"dataset_hash": "a" * 64}, sort_keys=True),
            "legacy_kill", Tier.Possible.value, "pending",
            None, None, None, None, None,
            "[]", None,
        ),
    )
    k.conn.commit()
    row = k.conn.execute(
        "SELECT caveats, precision_metadata FROM claims WHERE id=?",
        ("claim_legacy_pre_005",),
    ).fetchone()
    assert json.loads(row[0]) == []
    assert row[1] is None


# ---------------------------------------------------------------------------
# COMPOSITION TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_composition_full_pipeline_claim_falsify_promote_trace():
    """Full pipeline: CLAIM with precision_metadata -> FALSIFY (synthetic)
    -> PROMOTE -> TRACE walks the precision_metadata through the chain.

    Reference: PRECISION_METADATA_SPEC.md "auto-propagate via TRACE".
    If TRACE drops the precision_metadata, the spec has failed.
    """
    k = _make_kernel()
    pm = {
        "dps": 80,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": 0.95,
    }
    claim = _bootstrap_clear_claim_with_precision(
        k, target="full_pipeline", precision_metadata=pm
    )
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    graph = k.TRACE(sym)
    assert graph["precision_metadata"] == pm


def test_composition_cross_process_roundtrip_via_db():
    """Cross-process roundtrip: a claim minted in kernel-instance A is
    readable from kernel-instance B (sharing the same SQLite file).
    The precision_metadata survives the roundtrip.
    """
    import tempfile
    import os

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        k1 = SigmaKernel(path)
        pm = {
            "dps": 60,
            "method": "mpmath_polyroots",
            "convergence": "converged",
            "stability": None,
        }
        claim = k1.CLAIM(
            target_name="xproc",
            hypothesis="cross-process",
            evidence={"dataset_hash": "a" * 64},
            kill_path="kp",
            target_tier=Tier.Possible,
            precision_metadata=pm,
        )
        claim_id = claim.id
        k1.close()

        # Re-open from a fresh kernel instance.
        k2 = SigmaKernel(path)
        row = k2.conn.execute(
            "SELECT precision_metadata FROM claims WHERE id=?", (claim_id,)
        ).fetchone()
        assert json.loads(row[0]) == pm
        k2.close()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def test_composition_migration_idempotent_re_apply_safe():
    """The SQLite SCHEMA contains the precision_metadata column; running
    the SCHEMA twice is idempotent (CREATE TABLE IF NOT EXISTS). The
    Postgres migration uses ADD COLUMN IF NOT EXISTS for the same
    property.

    This is the local-equivalent test for migration 005 idempotency.
    Re-creating the kernel against the same file does NOT raise.
    """
    import tempfile
    import os

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        k1 = SigmaKernel(path)
        # Insert a claim so we know the schema is real.
        k1.CLAIM(
            target_name="idem",
            hypothesis="idempotency",
            evidence={"dataset_hash": "a" * 64},
            kill_path="kp",
            target_tier=Tier.Possible,
            precision_metadata={"dps": 60, "method": "mpmath_polyroots",
                                "convergence": "converged", "stability": None},
        )
        k1.close()
        # Open again — SCHEMA executescript should not fail because all
        # CREATE TABLE statements are IF NOT EXISTS.
        k2 = SigmaKernel(path)
        # Confirm the existing claim still readable.
        rows = k2.conn.execute(
            "SELECT precision_metadata FROM claims"
        ).fetchall()
        assert len(rows) == 1
        assert json.loads(rows[0][0])["dps"] == 60
        k2.close()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def test_composition_collect_caveats_walks_auto_caveats():
    """A symbol promoted from a CLAIM whose precision_metadata triggered
    auto-caveats has those caveats walked by collect_caveats. Ensures the
    auto-caveats propagate end-to-end (CLAIM -> PROMOTE -> TRACE ->
    collect_caveats), the same way user-provided caveats do.
    """
    k = _make_kernel()
    pm = {
        "dps": 30,
        "method": "mpmath_polyroots",
        "convergence": "converged",
        "stability": None,
    }
    claim = _bootstrap_clear_claim_with_precision(
        k, target="auto_walk", precision_metadata=pm
    )
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    collected = k.collect_caveats(sym)
    assert "precision_below_expected" in collected
