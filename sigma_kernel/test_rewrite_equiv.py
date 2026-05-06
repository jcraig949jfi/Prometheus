"""Tests for sigma_kernel REWRITE + EQUIV opcodes.

Substrate v2.3 §6.4 + the 2026-05-06 CoC feasibility pass:
    REWRITE  src_expr -> tgt_expr  via <rewrite_rule_id>  preserves <invariant_set>
    EQUIV    expr_a   ==  expr_b   under <equivalence_class_id>  with <witness>

Both opcodes mint regular Symbols (no schema change; see migration
006_add_rewrite_equiv_opcodes.sql for the no-op rationale). They MUST:
  - hash-lock src/tgt (or a/b) def_hashes into def_blob
  - flow both endpoints into provenance so TRACE walks back
  - consume a PromoteCap atomically with the symbol insert
  - reject malformed rule/class ids
  - leave existing 7 opcodes / caveats / precision_metadata behaviour
    completely unchanged

Test layout follows the math-tdd skill rubric (authority/property/edge/
composition).
"""
from __future__ import annotations

import json

import pytest

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel() -> SigmaKernel:
    return SigmaKernel(":memory:")


def _bootstrap_two_symbols(
    k: SigmaKernel,
    name_a: str = "expr_a",
    name_b: str = "expr_b",
) -> tuple[Symbol, Symbol]:
    """Bootstrap two distinct symbols for use as REWRITE/EQUIV endpoints."""
    sym_a = k.bootstrap_symbol(name_a, 1, {"value": "a", "tag": "alpha"})
    sym_b = k.bootstrap_symbol(name_b, 1, {"value": "b", "tag": "beta"})
    return sym_a, sym_b


def _bootstrap_clear_claim_promoted(
    k: SigmaKernel,
    target: str,
) -> Symbol:
    """Mint a CLEAR claim and PROMOTE it to produce a 'real' (non-bootstrap)
    Symbol with a verdict. Used to verify REWRITE/EQUIV does not interfere
    with existing PROMOTE-style provenance scraping.
    """
    claim = k.CLAIM(
        target_name=target,
        hypothesis="test hypothesis",
        evidence={"dataset_hash": "a" * 64, "null_hash": "b" * 64},
        kill_path="test_kill_path",
        target_tier=Tier.Possible,
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
    cap = k.mint_capability("PromoteCap")
    return k.PROMOTE(claim, cap)


# ---------------------------------------------------------------------------
# AUTHORITY TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_authority_rewrite_mints_symbol_with_endpoints_in_def_blob():
    """REWRITE produces a new Symbol whose def_blob contains src_def_hash,
    tgt_def_hash, and rewrite_rule_id. The op-code marker is also present.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")

    sym = k.REWRITE(
        src_expr=src,
        tgt_expr=tgt,
        rewrite_rule_id="ring_homomorphism_naturality",
        invariants_preserved=["degree", "leading_coefficient"],
        cap=cap,
        rationale="apply naturality square",
    )

    blob = json.loads(sym.def_blob)
    assert blob["opcode"] == "REWRITE"
    assert blob["src_def_hash"] == src.def_hash
    assert blob["tgt_def_hash"] == tgt.def_hash
    assert blob["rewrite_rule_id"] == "ring_homomorphism_naturality"
    assert blob["invariants_preserved"] == ["degree", "leading_coefficient"]
    assert blob["rationale"] == "apply naturality square"
    # The Symbol's tier defaults to WorkingTheory (rewrite is provisional).
    assert sym.tier == Tier.WorkingTheory
    # Auto-name convention.
    assert sym.name == "REWRITE_expr_a_to_expr_b"
    assert sym.version == 1


def test_authority_rewrite_provenance_includes_both_endpoint_hashes():
    """REWRITE provenance MUST include both src_def_hash and tgt_def_hash
    so TRACE walks back to both endpoints.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")

    sym = k.REWRITE(
        src_expr=src,
        tgt_expr=tgt,
        rewrite_rule_id="naturality",
        invariants_preserved=[],
        cap=cap,
    )

    assert src.def_hash in sym.provenance
    assert tgt.def_hash in sym.provenance


def test_authority_rewrite_persists_via_normal_symbol_path():
    """REWRITE writes to the standard `symbols` table; RESOLVE round-trips
    the Symbol back unchanged (and the hash-integrity check passes).
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    sym = k.REWRITE(
        src_expr=src, tgt_expr=tgt,
        rewrite_rule_id="r1",
        invariants_preserved=["norm"],
        cap=cap,
    )

    resolved = k.RESOLVE(sym.name, sym.version)
    assert resolved.def_hash == sym.def_hash
    assert resolved.def_blob == sym.def_blob
    assert resolved.tier == Tier.WorkingTheory


def test_authority_equiv_mints_symbol_with_endpoints_and_witness():
    """EQUIV produces a Symbol whose def_blob contains a_def_hash,
    b_def_hash, equivalence_class_id, and the typed witness.
    """
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")

    witness = {
        "witness_type": "finite_check",
        "value": {"checked_n": 1000, "method": "exhaustive"},
    }
    sym = k.EQUIV(
        expr_a=a, expr_b=b,
        equivalence_class_id="polynomial_modulo_equivalence",
        witness=witness,
        cap=cap,
        rationale="checked exhaustively to N=1000",
    )

    blob = json.loads(sym.def_blob)
    assert blob["opcode"] == "EQUIV"
    assert blob["a_def_hash"] == a.def_hash
    assert blob["b_def_hash"] == b.def_hash
    assert blob["equivalence_class_id"] == "polynomial_modulo_equivalence"
    assert blob["witness"] == witness
    assert sym.tier == Tier.WorkingTheory
    assert sym.name == "EQUIV_expr_a_eq_expr_b"


def test_authority_equiv_provenance_includes_both_endpoint_hashes():
    """EQUIV provenance MUST carry both endpoints' def_hashes."""
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    sym = k.EQUIV(
        expr_a=a, expr_b=b,
        equivalence_class_id="test_relation",
        witness={"witness_type": "finite_check", "value": {"n": 1}},
        cap=cap,
    )
    assert a.def_hash in sym.provenance
    assert b.def_hash in sym.provenance


# ---------------------------------------------------------------------------
# PROPERTY TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_property_rewrite_trace_walks_to_both_endpoints():
    """TRACE on a REWRITE Symbol must yield child nodes whose `ref` fields
    correspond to both src and tgt.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k, "src_thing", "tgt_thing")
    cap = k.mint_capability("PromoteCap")
    sym = k.REWRITE(
        src_expr=src, tgt_expr=tgt,
        rewrite_rule_id="ringhom",
        invariants_preserved=["deg"],
        cap=cap,
    )

    graph = k.TRACE(sym)
    assert graph["ref"] == sym.ref
    child_refs = {c.get("ref") for c in graph["children"] if "ref" in c}
    assert "src_thing@v1" in child_refs
    assert "tgt_thing@v1" in child_refs


def test_property_equiv_trace_walks_to_both_endpoints():
    """TRACE on an EQUIV Symbol walks to a and b."""
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k, "alpha", "beta")
    cap = k.mint_capability("PromoteCap")
    sym = k.EQUIV(
        expr_a=a, expr_b=b,
        equivalence_class_id="rel",
        witness={"witness_type": "finite_check", "value": {"n": 1}},
        cap=cap,
    )
    graph = k.TRACE(sym)
    child_refs = {c.get("ref") for c in graph["children"] if "ref" in c}
    assert "alpha@v1" in child_refs
    assert "beta@v1" in child_refs


def test_property_rewrite_consumes_capability():
    """A consumed PromoteCap cannot be re-used by REWRITE."""
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    k.REWRITE(
        src_expr=src, tgt_expr=tgt,
        rewrite_rule_id="r",
        invariants_preserved=[],
        cap=cap,
    )
    # Re-presenting the same cap is rejected by the persisted spent_caps row.
    src2 = k.bootstrap_symbol("src2", 1, {"v": 1})
    tgt2 = k.bootstrap_symbol("tgt2", 1, {"v": 2})
    with pytest.raises(CapabilityError, match="already consumed"):
        k.REWRITE(
            src_expr=src2, tgt_expr=tgt2,
            rewrite_rule_id="r2",
            invariants_preserved=[],
            cap=cap,
        )


def test_property_equiv_consumes_capability():
    """A consumed PromoteCap cannot be re-used by EQUIV."""
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    k.EQUIV(
        expr_a=a, expr_b=b,
        equivalence_class_id="rel",
        witness={"witness_type": "finite_check", "value": {"n": 1}},
        cap=cap,
    )
    a2 = k.bootstrap_symbol("a2", 1, {"v": 1})
    b2 = k.bootstrap_symbol("b2", 1, {"v": 2})
    with pytest.raises(CapabilityError, match="already consumed"):
        k.EQUIV(
            expr_a=a2, expr_b=b2,
            equivalence_class_id="rel2",
            witness={"witness_type": "finite_check", "value": {"n": 2}},
            cap=cap,
        )


def test_property_equiv_proof_ref_witness_flows_into_provenance():
    """When witness_type == 'proof_ref' and the value is a 64-char hex
    def_hash, that hash MUST appear in the EQUIV Symbol's provenance.
    """
    k = _make_kernel()
    # Promote a 'proof' Symbol to get a real def_hash.
    proof_sym = _bootstrap_clear_claim_promoted(k, target="proof_thing")
    a, b = _bootstrap_two_symbols(k, "lhs", "rhs")
    cap = k.mint_capability("PromoteCap")
    sym = k.EQUIV(
        expr_a=a, expr_b=b,
        equivalence_class_id="proof_backed_relation",
        witness={"witness_type": "proof_ref", "value": proof_sym.def_hash},
        cap=cap,
    )
    # Endpoints are first; the proof hash flows in via the def_blob scrape.
    assert a.def_hash in sym.provenance
    assert b.def_hash in sym.provenance
    assert proof_sym.def_hash in sym.provenance


def test_property_symmetric_equiv_records_two_distinct_symbols():
    """EQUIV(a, b) and EQUIV(b, a) both succeed; the substrate is append-
    only and they produce two different Symbols (different names AND
    different def_hashes).
    """
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k, "x", "y")
    cap1 = k.mint_capability("PromoteCap")
    cap2 = k.mint_capability("PromoteCap")
    sym_ab = k.EQUIV(
        expr_a=a, expr_b=b,
        equivalence_class_id="rel",
        witness={"witness_type": "finite_check", "value": {"n": 1}},
        cap=cap1,
    )
    sym_ba = k.EQUIV(
        expr_a=b, expr_b=a,
        equivalence_class_id="rel",
        witness={"witness_type": "finite_check", "value": {"n": 1}},
        cap=cap2,
    )
    assert sym_ab.name != sym_ba.name
    assert sym_ab.def_hash != sym_ba.def_hash
    # Both still resolve cleanly.
    assert k.RESOLVE(sym_ab.name, sym_ab.version).def_hash == sym_ab.def_hash
    assert k.RESOLVE(sym_ba.name, sym_ba.version).def_hash == sym_ba.def_hash


# ---------------------------------------------------------------------------
# EDGE TESTS  (>=3)
# ---------------------------------------------------------------------------


def test_edge_rewrite_rejects_rule_id_with_path_separator():
    """REWRITE must reject a rewrite_rule_id containing '/'; the id flows
    into def_blob and downstream resolvers expect a Symbol-name shape.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    with pytest.raises(ValueError, match="invalid"):
        k.REWRITE(
            src_expr=src, tgt_expr=tgt,
            rewrite_rule_id="bad/rule/name",
            invariants_preserved=[],
            cap=cap,
        )


def test_edge_rewrite_rejects_rule_id_with_whitespace_or_backslash():
    """Whitespace + backslashes are also rejected. Both would break
    downstream parsers that expect a clean symbol-name token.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    with pytest.raises(ValueError, match="invalid"):
        k.REWRITE(
            src_expr=src, tgt_expr=tgt,
            rewrite_rule_id="rule with spaces",
            invariants_preserved=[],
            cap=cap,
        )

    cap2 = k.mint_capability("PromoteCap")
    with pytest.raises(ValueError, match="invalid"):
        k.REWRITE(
            src_expr=src, tgt_expr=tgt,
            rewrite_rule_id="rule\\with\\backslash",
            invariants_preserved=[],
            cap=cap2,
        )


def test_edge_equiv_without_capability_raises():
    """Calling EQUIV with an unminted (or never-registered) capability
    raises CapabilityError.
    """
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k)
    bogus_cap = Capability(cap_id="cap_neverregistered", cap_type="PromoteCap")
    with pytest.raises(CapabilityError, match="not registered"):
        k.EQUIV(
            expr_a=a, expr_b=b,
            equivalence_class_id="rel",
            witness={"witness_type": "finite_check", "value": {"n": 1}},
            cap=bogus_cap,
        )


def test_edge_equiv_rejects_unknown_witness_type():
    """The substrate refuses witness types it does not understand; this
    keeps the witness payload contract typed.
    """
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    with pytest.raises(ValueError, match="witness_type"):
        k.EQUIV(
            expr_a=a, expr_b=b,
            equivalence_class_id="rel",
            witness={"witness_type": "vibes", "value": "trust me"},
            cap=cap,
        )


def test_edge_equiv_rejects_empty_witness():
    """Empty witness dict is rejected — every EQUIV must declare HOW the
    equivalence is supported.
    """
    k = _make_kernel()
    a, b = _bootstrap_two_symbols(k)
    cap = k.mint_capability("PromoteCap")
    with pytest.raises(ValueError, match="empty"):
        k.EQUIV(
            expr_a=a, expr_b=b,
            equivalence_class_id="rel",
            witness={},
            cap=cap,
        )


# ---------------------------------------------------------------------------
# COMPOSITION TESTS  (>=3) — REWRITE/EQUIV must not break existing kernel state
# ---------------------------------------------------------------------------


def test_composition_existing_symbols_still_readable_after_rewrite():
    """SMOKE CHECK: after a REWRITE, the original src/tgt Symbols still
    RESOLVE cleanly with their original def_hashes.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k, "preserve_src", "preserve_tgt")
    src_hash_before = src.def_hash
    tgt_hash_before = tgt.def_hash
    cap = k.mint_capability("PromoteCap")
    k.REWRITE(
        src_expr=src, tgt_expr=tgt,
        rewrite_rule_id="r",
        invariants_preserved=[],
        cap=cap,
    )
    src_after = k.RESOLVE("preserve_src", 1)
    tgt_after = k.RESOLVE("preserve_tgt", 1)
    assert src_after.def_hash == src_hash_before
    assert tgt_after.def_hash == tgt_hash_before


def test_composition_caveats_propagate_through_rewrite_endpoints():
    """If a REWRITE points at a PROMOTE-d Symbol that carries caveats,
    `collect_caveats` on the REWRITE walks back to those caveats.

    Property: REWRITE/EQUIV don't break the caveat propagation discipline
    documented in `proposal §6` and `test_caveats.py`.
    """
    k = _make_kernel()

    # Mint a CLEAR claim with a caveat and PROMOTE it to get a Symbol with caveats.
    claim = k.CLAIM(
        target_name="caveated_target",
        hypothesis="h",
        evidence={"dataset_hash": "a" * 64, "null_hash": "b" * 64},
        kill_path="kp",
        target_tier=Tier.Possible,
        caveats=["small_n"],
    )
    verdict = VerdictResult(
        status=Verdict.CLEAR, rationale="r",
        input_hash="c" * 64, seed=42, runtime_ms=1,
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
    cap_p = k.mint_capability("PromoteCap")
    sym_with_caveat = k.PROMOTE(claim, cap_p)
    assert "small_n" in json.loads(sym_with_caveat.def_blob)["caveats"]

    # A 'plain' tgt symbol.
    sym_plain = k.bootstrap_symbol("plain", 1, {"v": 1})
    cap_r = k.mint_capability("PromoteCap")
    rewrite_sym = k.REWRITE(
        src_expr=sym_with_caveat,
        tgt_expr=sym_plain,
        rewrite_rule_id="rule",
        invariants_preserved=[],
        cap=cap_r,
    )
    # collect_caveats walks the lineage and returns the union.
    collected = k.collect_caveats(rewrite_sym)
    assert "small_n" in collected


def test_composition_existing_kernel_state_unchanged_after_equiv():
    """SMOKE CHECK: after several EQUIVs, an unrelated Symbol promoted via
    the standard CLAIM->FALSIFY->PROMOTE pipeline is still readable, and
    its caveats are still hash-locked.

    This is the load-bearing backwards-compat assertion.
    """
    k = _make_kernel()

    # Promote an unrelated Symbol BEFORE doing any EQUIV ops.
    sym_unrelated = _bootstrap_clear_claim_promoted(k, target="unrelated")
    unrelated_hash = sym_unrelated.def_hash

    # Now do a few EQUIV ops.
    for i in range(3):
        a = k.bootstrap_symbol(f"a_{i}", 1, {"v": i})
        b = k.bootstrap_symbol(f"b_{i}", 1, {"v": i + 100})
        cap = k.mint_capability("PromoteCap")
        k.EQUIV(
            expr_a=a, expr_b=b,
            equivalence_class_id="rel",
            witness={"witness_type": "finite_check", "value": {"n": i}},
            cap=cap,
        )

    # The unrelated Symbol is still reachable, hash unchanged.
    re_resolved = k.RESOLVE(sym_unrelated.name, sym_unrelated.version)
    assert re_resolved.def_hash == unrelated_hash


def test_composition_rewrite_versions_correctly_on_repeat():
    """Two REWRITE calls between the same (src, tgt) pair produce v1 and v2
    of the auto-named Symbol. Versioning is max+1, identical to PROMOTE.
    """
    k = _make_kernel()
    src, tgt = _bootstrap_two_symbols(k)
    cap1 = k.mint_capability("PromoteCap")
    cap2 = k.mint_capability("PromoteCap")
    sym1 = k.REWRITE(
        src_expr=src, tgt_expr=tgt,
        rewrite_rule_id="rule_one",
        invariants_preserved=[],
        cap=cap1,
    )
    sym2 = k.REWRITE(
        src_expr=src, tgt_expr=tgt,
        rewrite_rule_id="rule_two",
        invariants_preserved=[],
        cap=cap2,
    )
    assert sym1.name == sym2.name
    assert sym1.version == 1
    assert sym2.version == 2
    # Different rule_ids -> different def_blobs -> different hashes.
    assert sym1.def_hash != sym2.def_hash
