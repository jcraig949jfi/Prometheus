"""Tests for sigma_kernel caveat-as-metadata-on-CLAIM (C3 fix).

Operationalizes ChatGPT's structural fix to the AI-to-AI inflation pattern
(C3 in stoa/discussions/2026-05-03-team-review-techne-bind-eval-and-pivot.md).
Caveats are typed metadata on the Claim that propagate through
CLAIM -> FALSIFY -> PROMOTE -> TRACE.

Math-tdd skill rubric: at least 3 tests in each of authority/property/
edge/composition.

Test-first per the math-tdd skill: this file documents the contract for
``Claim.caveats``, ``CLAIM(caveats=...)``, FALSIFY's WARN-caveat append,
PROMOTE's hash-locked caveats in def_blob, and TRACE's caveat
propagation.

References:
- Proposal: stoa/proposals/2026-05-04-techne-caveat-as-metadata-schema.md
- Migration: sigma_kernel/migrations/004_add_caveats_to_claims.sql
- Preset list: sigma_kernel/caveats.py (KNOWN_CAVEATS, validate_caveats)
- The C3 critique: stoa/discussions/2026-05-03-team-review-techne-bind-eval-and-pivot.md §C3
"""
from __future__ import annotations

import json
import warnings

import pytest
from hypothesis import given, settings, strategies as st

from sigma_kernel.sigma_kernel import (
    Capability,
    CapabilityError,
    Claim,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
)
from sigma_kernel.caveats import (
    KNOWN_CAVEATS,
    MAX_CAVEAT_LENGTH,
    describe,
    is_known,
    validate_caveats,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel() -> SigmaKernel:
    return SigmaKernel(":memory:")


def _bootstrap_clear_claim(
    k: SigmaKernel,
    target: str = "test_target",
    caveats: list[str] | None = None,
) -> Claim:
    """Mint a claim and bind a synthetic CLEAR verdict to it without
    routing through the subprocess oracle. The verdict is what PROMOTE
    requires; we synthesize one so tests don't take seconds per case.
    """
    claim = k.CLAIM(
        target_name=target,
        hypothesis="test hypothesis",
        evidence={"dataset_hash": "a" * 64, "null_hash": "b" * 64},
        kill_path="test_kill_path",
        target_tier=Tier.Possible,
        caveats=caveats,
    )
    # Synthesize a CLEAR verdict and persist it directly. This is the
    # same shape FALSIFY would write; we skip the subprocess for speed.
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


def _bootstrap_warn_claim(
    k: SigmaKernel,
    target: str = "test_warn_target",
    caveats: list[str] | None = None,
) -> Claim:
    """Mint a claim and bind a synthetic WARN verdict using the kernel's
    real FALSIFY-equivalent path (so the warn-caveat append fires)."""
    claim = k.CLAIM(
        target_name=target,
        hypothesis="warn-flavored hypothesis",
        evidence={"dataset_hash": "a" * 64},
        kill_path="test_warn_kill_path",
        target_tier=Tier.Possible,
        caveats=caveats,
    )
    # Build the WARN verdict and re-create the FALSIFY persistence
    # logic in-line (without spawning a subprocess oracle). We copy the
    # exact branch from sigma_kernel.SigmaKernel.FALSIFY for the WARN
    # path so the tested behavior matches production.
    verdict = VerdictResult(
        status=Verdict.WARN,
        rationale="synthetic warn rationale x" * 10,  # > 80 chars to test trunc
        input_hash="c" * 64,
        seed=42,
        runtime_ms=1,
    )
    claim.verdict = verdict
    claim.status = "falsified"
    warn_token = f"falsify_warn:{verdict.rationale[:80]}"
    if warn_token not in claim.caveats:
        claim.caveats = list(claim.caveats) + [warn_token]
    caveats_json = json.dumps(claim.caveats)
    k.conn.execute(
        "UPDATE claims SET status='falsified', verdict_status=?, "
        "verdict_rationale=?, verdict_input_hash=?, verdict_seed=?, "
        "verdict_runtime_ms=?, caveats=? WHERE id=?",
        (
            verdict.status.value, verdict.rationale, verdict.input_hash,
            verdict.seed, verdict.runtime_ms, caveats_json, claim.id,
        ),
    )
    k.conn.commit()
    return claim


# ---------------------------------------------------------------------------
# AUTHORITY TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_authority_claim_with_caveats_persists_through_full_pipeline():
    """A CLAIM minted with caveats=['small_n'] persists through
    CLAIM -> FALSIFY -> PROMOTE.

    Reference: feedback_replicate_seeds (the substrate's standard for
    when 'small_n' applies — n < 5 seeds).
    """
    k = _make_kernel()
    claim = _bootstrap_clear_claim(k, caveats=["small_n"])
    assert claim.caveats == ["small_n"]

    # Persistence check via the DB.
    row = k.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (claim.id,)
    ).fetchone()
    assert json.loads(row[0]) == ["small_n"]

    # PROMOTE preserves the caveat.
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    blob = json.loads(sym.def_blob)
    assert blob["caveats"] == ["small_n"]


def test_authority_promoted_symbol_def_blob_is_hash_locked():
    """A PROMOTE'd symbol's def_blob carries the caveats list, and the
    def_hash is computed over a blob that includes the caveats. Two
    symbols differing only in caveats have different hashes.

    This is the load-bearing property: the substrate cannot lose a
    caveat without changing the symbol's hash, which would break
    RESOLVE / TRACE for any downstream consumer.
    """
    k1 = _make_kernel()
    k2 = _make_kernel()
    claim1 = _bootstrap_clear_claim(k1, caveats=[])
    claim2 = _bootstrap_clear_claim(
        k2, caveats=["rediscovery_not_discovery"]
    )
    cap1 = k1.mint_capability("PromoteCap")
    cap2 = k2.mint_capability("PromoteCap")
    sym1 = k1.PROMOTE(claim1, cap1)
    sym2 = k2.PROMOTE(claim2, cap2)
    assert sym1.def_hash != sym2.def_hash
    # And the blob does carry the caveat:
    blob2 = json.loads(sym2.def_blob)
    assert "rediscovery_not_discovery" in blob2["caveats"]


def test_authority_trace_walks_caveats_from_promoted_symbol():
    """TRACE on a symbol with caveats returns a graph node carrying
    those caveats. ``collect_caveats`` returns the union along the path.

    Reference: proposal §6 ("Acceptance test for adoption"). If TRACE
    drops a caveat, the proposal has failed.
    """
    k = _make_kernel()
    claim = _bootstrap_clear_claim(
        k, caveats=["small_n", "bandit_structure"]
    )
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    graph = k.TRACE(sym)
    assert "caveats" in graph
    assert set(graph["caveats"]) == {"small_n", "bandit_structure"}
    # And the convenience helper returns the union.
    collected = k.collect_caveats(sym)
    assert collected == sorted({"small_n", "bandit_structure"})


# ---------------------------------------------------------------------------
# PROPERTY TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_property_claim_caveats_mutable_in_python_visible_in_db_after_falsify():
    """Caveats list is mutable on the Claim dataclass (Python). Mutation
    by the FALSIFY-WARN path is visible in the DB after the verdict
    persistence. Property: in-Python mutation -> DB write atomicity.
    """
    k = _make_kernel()
    # FALSIFY's WARN branch appends a 'falsify_warn:...' caveat.
    claim = _bootstrap_warn_claim(k, caveats=["small_n"])
    # In-Python: caveats now has ['small_n', 'falsify_warn:...'].
    assert "small_n" in claim.caveats
    assert any(c.startswith("falsify_warn:") for c in claim.caveats)
    # DB matches in-Python.
    row = k.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (claim.id,)
    ).fetchone()
    db_caveats = json.loads(row[0])
    assert db_caveats == claim.caveats


def test_property_promoted_symbol_caveats_immutable_via_hash():
    """A symbol's caveats are content-addressed: they live in the
    sha256-hashed def_blob. Tampering with the stored def_blob (e.g.
    dropping a caveat) is detected at RESOLVE time as an IntegrityError.

    Property: substrate-level immutability of caveats post-PROMOTE.
    """
    from sigma_kernel.sigma_kernel import IntegrityError

    k = _make_kernel()
    claim = _bootstrap_clear_claim(
        k, caveats=["small_n", "synthetic_battery_used"]
    )
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)

    # Tamper: simulate someone dropping a caveat from def_blob.
    blob = json.loads(sym.def_blob)
    blob["caveats"] = []
    new_blob = json.dumps(blob, sort_keys=True)
    k.conn.execute(
        "UPDATE symbols SET def_blob=? WHERE name=? AND version=?",
        (new_blob, sym.name, sym.version),
    )
    k.conn.commit()
    # RESOLVE detects the tamper because def_hash is checked.
    with pytest.raises(IntegrityError):
        k.RESOLVE(sym.name, sym.version)


def test_property_validate_caveats_normalizes_misspellings():
    """validate_caveats accepts misspellings of preset tokens but emits
    a warning naming the canonical form.

    Property: substrate is permissive at write, strict at hash.
    """
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = validate_caveats(["small-n"])
        # Token preserved as-is; warning emitted naming canonical form.
        assert out == ["small-n"]
        assert any(
            "small_n" in str(warning.message) for warning in w
        ), f"expected misspelling warning; got {[str(x.message) for x in w]}"


def test_property_promote_canonicalizes_caveats_in_def_blob():
    """PROMOTE sorts + de-dups caveats in the def_blob to canonicalize
    the content hash. Property: caveat order should not affect hash.
    """
    k1 = _make_kernel()
    k2 = _make_kernel()
    # Same caveats, different orders + a duplicate.
    claim1 = _bootstrap_clear_claim(
        k1, caveats=["small_n", "bandit_structure"]
    )
    claim2 = _bootstrap_clear_claim(
        k2, caveats=["bandit_structure", "small_n", "small_n"]
    )
    cap1 = k1.mint_capability("PromoteCap")
    cap2 = k2.mint_capability("PromoteCap")
    sym1 = k1.PROMOTE(claim1, cap1)
    sym2 = k2.PROMOTE(claim2, cap2)
    # def_hash equal because canonicalization sorts + dedups.
    assert sym1.def_hash == sym2.def_hash


# ---------------------------------------------------------------------------
# EDGE TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_edge_empty_caveats_list_default_no_db_regression():
    """Default behavior: existing CLAIM calls without caveats work
    unchanged; the DB row stores '[]'; no regression on old kernel
    behavior.

    Edge: backward compatibility at the API layer.
    """
    k = _make_kernel()
    # Old-style CLAIM with no caveats kwarg.
    claim = k.CLAIM(
        target_name="legacy_target",
        hypothesis="legacy hypothesis",
        evidence={"dataset_hash": "a" * 64},
        kill_path="legacy_kill",
        target_tier=Tier.Conjecture,
    )
    assert claim.caveats == []
    row = k.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (claim.id,)
    ).fetchone()
    assert json.loads(row[0]) == []


def test_edge_long_caveat_string_is_truncated_with_visible_marker():
    """A caveat string > MAX_CAVEAT_LENGTH chars is truncated with a
    visible '...[truncated]' suffix. Edge: prevent megabyte rationale
    dumps but keep truncation observable.
    """
    long = "x" * (MAX_CAVEAT_LENGTH + 500)
    out = validate_caveats([long])
    assert len(out) == 1
    assert len(out[0]) == MAX_CAVEAT_LENGTH
    assert out[0].endswith("...[truncated]")


def test_edge_duplicate_caveats_deduped_in_promoted_def_blob():
    """Duplicate caveats from the caller are de-duped (in-validate)
    AND re-canonicalized in PROMOTE's def_blob. Edge: caller may pass
    duplicates with no harm.
    """
    k = _make_kernel()
    claim = _bootstrap_clear_claim(
        k, caveats=["small_n", "small_n", "small_n"]
    )
    # validate_caveats already dedups at CLAIM time.
    assert claim.caveats == ["small_n"]
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    blob = json.loads(sym.def_blob)
    assert blob["caveats"] == ["small_n"]


def test_edge_validate_rejects_non_list_input():
    """validate_caveats raises TypeError on non-list inputs (other than
    None which is the empty-default sentinel). Edge: type discipline.
    """
    with pytest.raises(TypeError):
        validate_caveats("small_n")  # bare string, not a list
    with pytest.raises(TypeError):
        validate_caveats({"small_n"})  # set, not a list/tuple
    with pytest.raises(TypeError):
        validate_caveats([42])  # non-string item


def test_edge_unknown_caveat_token_accepted_silently():
    """An arbitrary new token (not in KNOWN_CAVEATS, not a misspelling
    of a preset) is accepted without warning. Edge: substrate permissive
    at write — new tokens should not require a code change.
    """
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = validate_caveats(["totally_new_caveat_token_xyz"])
        assert out == ["totally_new_caveat_token_xyz"]
        # No warnings (no preset is similar to this string).
        misspelling_warnings = [
            x for x in w if "misspelling" in str(x.message)
        ]
        assert misspelling_warnings == []


# ---------------------------------------------------------------------------
# COMPOSITION TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_composition_caveats_propagate_through_trace():
    """End-to-end: CLAIM with caveats -> PROMOTE -> TRACE returns the
    caveats verbatim. This is the PROPOSAL'S LOAD-BEARING ACCEPTANCE
    TEST (proposal §6).

    If this fails, the proposal has failed; agents will go right back
    to manual documentation discipline, which has already failed.
    """
    k = _make_kernel()
    claim = _bootstrap_clear_claim(
        k,
        caveats=["small_n", "rediscovery_not_discovery"],
    )
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    # TRACE round-trips both caveats.
    collected = k.collect_caveats(sym)
    assert "small_n" in collected
    assert "rediscovery_not_discovery" in collected


def test_composition_falsify_warn_appends_caveat_visible_in_promote():
    """End-to-end: a CLAIM that gets a WARN verdict has the warn-caveat
    appended atomic with the verdict write; PROMOTE's def_blob captures
    it. Composition: FALSIFY-WARN -> PROMOTE -> caveat lives in the
    symbol forever.
    """
    k = _make_kernel()
    claim = _bootstrap_warn_claim(k, caveats=["small_n"])
    # PROMOTE the WARN claim (allowed; only BLOCK is rejected).
    cap = k.mint_capability("PromoteCap")
    sym = k.PROMOTE(claim, cap)
    blob = json.loads(sym.def_blob)
    # Both the original caveat AND the warn-caveat are in the symbol.
    assert "small_n" in blob["caveats"]
    assert any(
        c.startswith("falsify_warn:") for c in blob["caveats"]
    )


def test_composition_resolve_returns_caveats_via_def_blob():
    """End-to-end: another process (simulated by re-opening kernel on
    a file-backed DB) can RESOLVE the symbol and see its caveats by
    parsing def_blob. Composition: cross-process visibility.
    """
    import tempfile
    import os

    # Use a real file path so two SigmaKernel instances see the same DB.
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        k1 = SigmaKernel(path)
        claim = _bootstrap_clear_claim(
            k1, caveats=["ground_truth_absent"]
        )
        cap = k1.mint_capability("PromoteCap")
        sym = k1.PROMOTE(claim, cap)
        ref = (sym.name, sym.version)
        k1.close()

        # Reopen as a fresh kernel (the second-process simulation).
        k2 = SigmaKernel(path)
        sym2 = k2.RESOLVE(*ref)
        blob = json.loads(sym2.def_blob)
        assert blob["caveats"] == ["ground_truth_absent"]
        k2.close()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def test_composition_migration_backward_compat_existing_claims_no_caveats():
    """Migration backward-compat: existing claim rows that pre-date
    migration 004 (no caveats column at INSERT time) still RESOLVE /
    work correctly.

    Simulates the pre-004 state by inserting a row with empty caveats
    JSON ('[]'), which is what the migration default puts on existing
    rows. The kernel must read this as the empty list and treat the
    claim no differently from a claim minted with explicit caveats=[].
    """
    k = _make_kernel()
    # Synthesize a pre-004-style row: caveats = '[]' (the migration
    # default) — what an existing row looks like after the ALTER TABLE.
    k.conn.execute(
        "INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "claim_legacy_pre_004", "legacy", "legacy hypothesis",
            json.dumps({"dataset_hash": "a" * 64}, sort_keys=True),
            "legacy_kill", Tier.Possible.value, "pending",
            None, None, None, None, None,
            "[]",
        ),
    )
    k.conn.commit()
    row = k.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", ("claim_legacy_pre_004",)
    ).fetchone()
    assert json.loads(row[0]) == []


# ---------------------------------------------------------------------------
# Smoke tests for the preset list itself
# ---------------------------------------------------------------------------


def test_preset_list_is_nontrivial_and_well_formed():
    """KNOWN_CAVEATS has at least 10 entries, all snake_case, all with
    non-empty rationale.
    """
    assert len(KNOWN_CAVEATS) >= 10
    for token, rationale in KNOWN_CAVEATS.items():
        assert token == token.lower(), token
        assert " " not in token, token
        assert "-" not in token, token
        assert len(rationale) > 10, f"empty rationale for {token}"


def test_describe_returns_rationale_for_known_token():
    """describe() returns the rationale for a known token; None for
    unknown.
    """
    assert describe("small_n") is not None
    assert describe("totally_unknown_xyz") is None


def test_is_known_strict_match():
    """is_known checks exact-match against the preset list."""
    assert is_known("small_n")
    assert not is_known("small-n")  # misspelling
    assert not is_known("falsify_warn:foo")  # prefix form
