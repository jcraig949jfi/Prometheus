"""Property-based tests for the REWRITE/EQUIV opcodes (substrate v2.3 §6.4).

Per inbox ticket T-2026-05-07-T011 (P1-high, Aporia 2026-05-07): REWRITE
and EQUIV are the symbolic half of the Sigma-language and relatively
new. Existing tests at sigma_kernel/test_rewrite_equiv.py are
authority/edge style (20 hand-written unit tests). This module adds
algebraic-property fuzzing.

Algebraic semantics in an APPEND-ONLY substrate
------------------------------------------------
The substrate is APPEND-ONLY (see kernel docstring on EQUIV: ``the
substrate is APPEND-ONLY: EQUIV(a, b, ...) and EQUIV(b, a, ...) produce
two distinct Symbols``). Mathematical reflexivity / symmetry /
transitivity are caller-level semantic claims; the kernel does NOT
collapse them. This module tests two kinds of property:

  (A) **Constructibility** properties: REWRITE/EQUIV opcodes accept the
      input shapes that the algebraic property requires (e.g. EQUIV(a, a)
      for reflexivity is mintable).

  (B) **Content-determinism** properties: same input ⇒ same def_hash;
      different rule_id ⇒ different def_hash; provenance contains the
      claimed endpoints; etc. These are the substrate's load-bearing
      identity discipline.

Property categories (acceptance criterion #2):

  1. **EQUIV reflexivity (constructibility)** —
     ``EQUIV(a, a, ...)`` succeeds and the def_blob carries
     ``a_def_hash == b_def_hash``.

  2. **EQUIV symmetry (APPEND-ONLY behavior)** — ``EQUIV(a, b, ...)``
     and ``EQUIV(b, a, ...)`` produce DISTINCT Symbols (different
     def_hashes), but BOTH carry the same equivalence_class_id and
     reference both endpoints. Symmetry is a caller-level semantic
     property, not a kernel-collapsing one.

  3. **EQUIV transitivity (chain witness flow)** — given
     ``EQUIV(a, b)`` and ``EQUIV(b, c)`` with content-addressed Symbol
     refs, an ``EQUIV(a, c, witness=equiv_chain[...])`` referencing both
     can be minted; the chain witness's hashes flow into the new
     Symbol's provenance for TRACE walks.

  4. **REWRITE idempotence (content-determinism)** — minting REWRITE
     twice with identical inputs (and two different caps) yields two
     Symbols at name@v1 and name@v2 with IDENTICAL def_hashes (same
     content). Identity-at-the-content layer.

  5. **REWRITE confluence (substrate non-enforcement)** — two REWRITE
     Symbols with the same src/tgt endpoints but DIFFERENT rule_ids
     yield DIFFERENT def_hashes. The substrate does NOT collapse
     different rules into one canonical rewrite — confluence is the
     caller's responsibility per the kernel docstring.

  6. **REWRITE × canonicalization commutativity** — REWRITE def_hash
     depends on (src.def_hash, src.ref, tgt.def_hash, tgt.ref, rule_id,
     invariants_preserved, rationale). If two endpoints share the same
     def_hash but different refs, the REWRITE def_hash differs (the
     substrate keys identity by ref AND def_hash). This documents the
     substrate's identity discipline: canonicalization at the def_hash
     layer is preserved under REWRITE; canonicalization at the ref
     layer is NOT (refs are name@version, which the substrate treats
     as identity-bearing).

Plus 1 sanity property:

  7. **Provenance-walks-back invariant** — REWRITE and EQUIV both
     include their endpoints in provenance. For TRACE to work, both
     endpoints' def_hashes must be present in the new Symbol's
     provenance list.

Coverage matrix: 7 categories, each with ≥1 Hypothesis-based fuzz test
where the input space is non-trivial (rule_ids, rationales, witness
payloads). NO contract change to SigmaKernel — pure test additions.
"""
from __future__ import annotations

from typing import Tuple

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from sigma_kernel.sigma_kernel import (
    Capability,
    SigmaKernel,
    Symbol,
    Tier,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kernel() -> SigmaKernel:
    return SigmaKernel(":memory:")


def _bootstrap(
    k: SigmaKernel, name: str, version: int = 1, value: str = "v"
) -> Symbol:
    """Bootstrap a Symbol with a minimal def payload."""
    return k.bootstrap_symbol(name, version, {"value": value, "tag": name})


def _two_symbols(k: SigmaKernel) -> Tuple[Symbol, Symbol]:
    return _bootstrap(k, "expr_a", value="a"), _bootstrap(k, "expr_b", value="b")


def _three_symbols(k: SigmaKernel) -> Tuple[Symbol, Symbol, Symbol]:
    return (
        _bootstrap(k, "expr_a", value="a"),
        _bootstrap(k, "expr_b", value="b"),
        _bootstrap(k, "expr_c", value="c"),
    )


def _proof_witness(k: SigmaKernel, ref_value: str = "thm_proof") -> dict:
    """A minimal proof_ref witness pointing at a synthesized Symbol."""
    proof_sym = _bootstrap(k, ref_value, value="proof_payload")
    return {"witness_type": "proof_ref", "value": proof_sym.def_hash}


def _equiv_chain_witness(refs: list[str]) -> dict:
    return {"witness_type": "equiv_chain", "value": list(refs)}


# Hypothesis strategies — bounded to substrate-allowed character classes.
_rule_id_strategy = st.from_regex(r"^[A-Za-z0-9_.\-]{1,40}$", fullmatch=True)
_rationale_strategy = st.text(max_size=80)
_invariants_strategy = st.lists(
    st.from_regex(r"^[A-Za-z0-9_.\-]{1,20}$", fullmatch=True),
    max_size=5,
).map(list)
_payload_value_strategy = st.text(min_size=1, max_size=20)


_FUZZ_SETTINGS = settings(
    max_examples=20,
    derandomize=False,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    deadline=None,
)


# ---------------------------------------------------------------------------
# Property 1 — EQUIV reflexivity (constructibility)
# ---------------------------------------------------------------------------


class TestProperty1EquivReflexivityConstructibility:
    """EQUIV(a, a, ...) is mintable; def_blob carries identical endpoints."""

    @_FUZZ_SETTINGS
    @given(
        rule_id=_rule_id_strategy,
        rationale=_rationale_strategy,
    )
    def test_equiv_self_succeeds_and_blob_records_identical_endpoints(
        self, rule_id: str, rationale: str,
    ) -> None:
        import json as _json
        k = _make_kernel()
        sym_a = _bootstrap(k, "expr_self")
        cap = k.mint_capability("PromoteCap")
        witness = _proof_witness(k)
        eq_sym = k.EQUIV(
            expr_a=sym_a,
            expr_b=sym_a,  # reflexive
            equivalence_class_id=rule_id,
            witness=witness,
            cap=cap,
            rationale=rationale,
        )
        blob = _json.loads(eq_sym.def_blob)
        assert blob["opcode"] == "EQUIV"
        assert blob["a_def_hash"] == blob["b_def_hash"] == sym_a.def_hash
        assert blob["a_ref"] == blob["b_ref"] == sym_a.ref


# ---------------------------------------------------------------------------
# Property 2 — EQUIV symmetry (APPEND-ONLY substrate behaviour)
# ---------------------------------------------------------------------------


class TestProperty2EquivSymmetryAppendOnly:
    """Per kernel docstring: EQUIV(a, b) and EQUIV(b, a) produce two
    distinct Symbols. Symmetry is caller-level semantic, not kernel-
    enforced. We test the documented APPEND-ONLY behaviour."""

    @_FUZZ_SETTINGS
    @given(
        rule_id=_rule_id_strategy,
        val_a=_payload_value_strategy,
        val_b=_payload_value_strategy,
    )
    def test_equiv_a_b_and_b_a_yield_distinct_symbols(
        self, rule_id: str, val_a: str, val_b: str,
    ) -> None:
        import json as _json
        if val_a == val_b:
            # ensure distinct def_hashes for the test's premise
            val_b = val_b + "_distinct"
        k = _make_kernel()
        sym_a = _bootstrap(k, "expr_alpha", value=val_a)
        sym_b = _bootstrap(k, "expr_beta", value=val_b)
        cap_ab = k.mint_capability("PromoteCap")
        cap_ba = k.mint_capability("PromoteCap")
        witness = _proof_witness(k)
        eq_ab = k.EQUIV(
            sym_a, sym_b, rule_id, witness, cap_ab, rationale="forward",
        )
        eq_ba = k.EQUIV(
            sym_b, sym_a, rule_id, witness, cap_ba, rationale="reverse",
        )
        # APPEND-ONLY: the two records are distinct Symbols.
        assert eq_ab.def_hash != eq_ba.def_hash
        # But both reference the same equivalence_class_id and the same
        # endpoint def_hashes (just in opposite positions).
        blob_ab = _json.loads(eq_ab.def_blob)
        blob_ba = _json.loads(eq_ba.def_blob)
        assert blob_ab["equivalence_class_id"] == blob_ba["equivalence_class_id"] == rule_id
        assert {blob_ab["a_def_hash"], blob_ab["b_def_hash"]} == {
            sym_a.def_hash, sym_b.def_hash
        }
        assert {blob_ba["a_def_hash"], blob_ba["b_def_hash"]} == {
            sym_a.def_hash, sym_b.def_hash
        }


# ---------------------------------------------------------------------------
# Property 3 — EQUIV transitivity via chain witness
# ---------------------------------------------------------------------------


class TestProperty3EquivTransitivityViaChainWitness:
    """EQUIV(a, c, witness=equiv_chain([EQ_ab.def_hash, EQ_bc.def_hash]))
    is mintable; the chain refs flow into provenance."""

    @_FUZZ_SETTINGS
    @given(rule_id=_rule_id_strategy)
    def test_equiv_transitivity_chain_provenance_flows(
        self, rule_id: str,
    ) -> None:
        k = _make_kernel()
        sym_a, sym_b, sym_c = _three_symbols(k)
        # Mint EQUIV(a, b) and EQUIV(b, c) first.
        cap1 = k.mint_capability("PromoteCap")
        cap2 = k.mint_capability("PromoteCap")
        cap3 = k.mint_capability("PromoteCap")
        wit = _proof_witness(k, ref_value="step_proof")
        eq_ab = k.EQUIV(sym_a, sym_b, rule_id, wit, cap1, "step1")
        eq_bc = k.EQUIV(sym_b, sym_c, rule_id, wit, cap2, "step2")
        # Now mint EQUIV(a, c) with chain witness.
        chain_witness = _equiv_chain_witness([eq_ab.def_hash, eq_bc.def_hash])
        eq_ac = k.EQUIV(sym_a, sym_c, rule_id, chain_witness, cap3, "transitive")
        # Provenance must contain the two chain links.
        assert eq_ab.def_hash in eq_ac.provenance
        assert eq_bc.def_hash in eq_ac.provenance
        # And both endpoints.
        assert sym_a.def_hash in eq_ac.provenance
        assert sym_c.def_hash in eq_ac.provenance


# ---------------------------------------------------------------------------
# Property 4 — REWRITE idempotence (content-determinism)
# ---------------------------------------------------------------------------


class TestProperty4RewriteIdempotenceContentDeterminism:
    """Same REWRITE inputs ⇒ same def_hash. Versions differ (APPEND-ONLY)
    but content addressing is stable."""

    @_FUZZ_SETTINGS
    @given(
        rule_id=_rule_id_strategy,
        invariants=_invariants_strategy,
        rationale=_rationale_strategy,
    )
    def test_repeated_rewrite_with_identical_inputs_yields_same_def_hash(
        self, rule_id: str, invariants: list, rationale: str,
    ) -> None:
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap1 = k.mint_capability("PromoteCap")
        cap2 = k.mint_capability("PromoteCap")
        rw1 = k.REWRITE(sym_a, sym_b, rule_id, invariants, cap1, rationale)
        rw2 = k.REWRITE(sym_a, sym_b, rule_id, invariants, cap2, rationale)
        # Identity at the content layer.
        assert rw1.def_hash == rw2.def_hash
        # APPEND-ONLY: different versions of the same name.
        assert rw1.name == rw2.name
        assert rw1.version != rw2.version
        assert rw2.version > rw1.version


# ---------------------------------------------------------------------------
# Property 5 — REWRITE non-confluence (different rule_id => different content)
# ---------------------------------------------------------------------------


class TestProperty5RewriteNonConfluenceUnderRuleIdChange:
    """Per kernel docstring: 'Confluence + termination of the rewrite-rule
    registry are likewise the caller's responsibility'. The substrate
    does NOT collapse two different rules into one canonical rewrite —
    different rule_id ⇒ different def_hash even with the same endpoints."""

    @_FUZZ_SETTINGS
    @given(
        rule_a=_rule_id_strategy,
        rule_b=_rule_id_strategy,
    )
    def test_different_rule_ids_yield_different_def_hashes(
        self, rule_a: str, rule_b: str,
    ) -> None:
        if rule_a == rule_b:
            return  # premise requires distinct rule ids
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap1 = k.mint_capability("PromoteCap")
        cap2 = k.mint_capability("PromoteCap")
        rw_a = k.REWRITE(sym_a, sym_b, rule_a, [], cap1, "")
        rw_b = k.REWRITE(sym_a, sym_b, rule_b, [], cap2, "")
        # Different rules ⇒ different content hashes (no confluence
        # collapse).
        assert rw_a.def_hash != rw_b.def_hash


# ---------------------------------------------------------------------------
# Property 6 — REWRITE × canonicalization commutativity
# ---------------------------------------------------------------------------


class TestProperty6RewriteCanonicalizationDiscipline:
    """REWRITE def_hash depends on (src.def_hash, src.ref, tgt.def_hash,
    tgt.ref, rule_id, invariants, rationale). Two endpoints with the
    same def_hash but different refs (= different name@version) yield
    DIFFERENT REWRITE def_hashes. The substrate keys identity by both
    def_hash AND ref, not just content."""

    def test_same_content_different_refs_yield_different_rewrite_def_hash(self) -> None:
        k = _make_kernel()
        # Two symbols with identical def_obj content but different names
        # ⇒ same def_hash (content-addressed) but different refs.
        sym_a1 = k.bootstrap_symbol("expr_one", 1, {"value": "shared"})
        sym_a2 = k.bootstrap_symbol("expr_two", 1, {"value": "shared"})
        assert sym_a1.def_hash == sym_a2.def_hash  # premise: same content
        assert sym_a1.ref != sym_a2.ref            # premise: different refs

        sym_tgt = _bootstrap(k, "expr_target", value="t")
        cap1 = k.mint_capability("PromoteCap")
        cap2 = k.mint_capability("PromoteCap")
        rw1 = k.REWRITE(sym_a1, sym_tgt, "rule1", [], cap1, "")
        rw2 = k.REWRITE(sym_a2, sym_tgt, "rule1", [], cap2, "")
        # Different refs (even with identical def_hashes) ⇒ different
        # REWRITE def_hash. The substrate's identity discipline
        # preserves the ref-level distinction.
        assert rw1.def_hash != rw2.def_hash

    def test_same_content_same_ref_yields_same_rewrite_def_hash(self) -> None:
        """Sister test: when src has the same def_hash AND same ref,
        REWRITE def_hash is identical (the property-4 idempotence
        result, but anchored on canonicalization at the source level)."""
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap1 = k.mint_capability("PromoteCap")
        cap2 = k.mint_capability("PromoteCap")
        rw1 = k.REWRITE(sym_a, sym_b, "rule_id", [], cap1, "")
        rw2 = k.REWRITE(sym_a, sym_b, "rule_id", [], cap2, "")
        assert rw1.def_hash == rw2.def_hash


# ---------------------------------------------------------------------------
# Property 7 — Provenance-walks-back invariant (sanity)
# ---------------------------------------------------------------------------


class TestProperty7ProvenanceWalksBackToBothEndpoints:
    """Both REWRITE and EQUIV must include both endpoints in provenance.
    This is the load-bearing TRACE invariant — a TRACE walk on the
    REWRITE/EQUIV Symbol must surface both src and tgt (or a and b)."""

    @_FUZZ_SETTINGS
    @given(
        rule_id=_rule_id_strategy,
        rationale=_rationale_strategy,
        invariants=_invariants_strategy,
    )
    def test_rewrite_provenance_contains_both_endpoints(
        self, rule_id: str, rationale: str, invariants: list,
    ) -> None:
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap = k.mint_capability("PromoteCap")
        rw = k.REWRITE(sym_a, sym_b, rule_id, invariants, cap, rationale)
        assert sym_a.def_hash in rw.provenance
        assert sym_b.def_hash in rw.provenance

    @_FUZZ_SETTINGS
    @given(rule_id=_rule_id_strategy)
    def test_equiv_provenance_contains_both_endpoints(
        self, rule_id: str,
    ) -> None:
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap = k.mint_capability("PromoteCap")
        wit = _proof_witness(k)
        eq = k.EQUIV(sym_a, sym_b, rule_id, wit, cap, "")
        assert sym_a.def_hash in eq.provenance
        assert sym_b.def_hash in eq.provenance

    @_FUZZ_SETTINGS
    @given(rule_id=_rule_id_strategy)
    def test_equiv_proof_ref_witness_hash_flows_into_provenance(
        self, rule_id: str,
    ) -> None:
        """When witness type is proof_ref carrying a 64-char def_hash,
        that hash must be scraped into the EQUIV Symbol's provenance for
        TRACE to walk back to the proof Symbol."""
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        proof_sym = _bootstrap(k, "thm_proof", value="proof_data")
        cap = k.mint_capability("PromoteCap")
        wit = {"witness_type": "proof_ref", "value": proof_sym.def_hash}
        eq = k.EQUIV(sym_a, sym_b, rule_id, wit, cap, "")
        assert proof_sym.def_hash in eq.provenance


# ---------------------------------------------------------------------------
# Bonus property — REWRITE rejects malformed rule_ids
# ---------------------------------------------------------------------------


class TestRewriteRejectsMalformedRuleIds:
    """Negative-direction property: REWRITE/EQUIV both refuse rule_ids
    with characters outside [A-Za-z0-9_.-]. Loud-fail discipline."""

    _BAD_RULE_IDS = [
        "rule with space",
        "rule/with/slash",
        "rule\twith\ttab",
        "rule;with;semicolon",
        "",
    ]

    @pytest.mark.parametrize("bad_id", _BAD_RULE_IDS)
    def test_rewrite_rejects_bad_rule_id(self, bad_id: str) -> None:
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap = k.mint_capability("PromoteCap")
        with pytest.raises(ValueError):
            k.REWRITE(sym_a, sym_b, bad_id, [], cap, "")

    @pytest.mark.parametrize("bad_id", _BAD_RULE_IDS)
    def test_equiv_rejects_bad_class_id(self, bad_id: str) -> None:
        k = _make_kernel()
        sym_a, sym_b = _two_symbols(k)
        cap = k.mint_capability("PromoteCap")
        wit = _proof_witness(k)
        with pytest.raises(ValueError):
            k.EQUIV(sym_a, sym_b, bad_id, wit, cap, "")
