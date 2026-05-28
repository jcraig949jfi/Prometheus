"""Stage 10 TDD tests — promote k1/l1/m1/n1/o1 from stub to REAL gen.

v0 tests (test_new_gen_families_v0.py) verified each gen emits records
in the new claim shape. v1 tests verify each gen actually DOES WORK:
- emits more than the stub's hand-coded count
- derives records from catalogs / corpus / enumeration (not hardcode)
- produces diverse records (no two identical payloads)
- has structurally complete payloads (all expected fields present)
- performs the work its name implies (enumeration, bounded search,
  replay, perturbation)

Failing now → green as each gen is implemented to real-quality.
"""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import TheseusRecord
from theseus.generators.base import GeneratorRole


def _exhaust(gen, max_calls=500):
    """Drive next() until None or max_calls; return all records emitted."""
    out = []
    for _ in range(max_calls):
        r = gen.next()
        if r is None:
            break
        out.append(r)
    return out


# =============================================================================
# k1 — real typed bridge
# =============================================================================

def test_k1_real_emits_more_than_stub():
    """Stub emitted 4; real should emit ≥ 20 (cross-product of arrows × objects)."""
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="real-test-k1")
    recs = _exhaust(g)
    assert len(recs) >= 20, f"k1 real emitted only {len(recs)} records"


def test_k1_real_records_derive_from_catalog():
    """Records should reference real catalog object IDs, not the literal
    pattern strings 'knot:5_2' / 'ec:11.a1' from the stub."""
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="real-test-k1")
    recs = _exhaust(g, max_calls=50)
    objs = {r.claim_payload.get("source_object") for r in recs}
    # Stub had 4 fixed objects: knot:5_2, ec:11.a1, knot:7_3, ec:37.a1.
    # Real should have a wider set drawn from catalog.
    assert len(objs) >= 8, f"k1 real used only {len(objs)} distinct objects"


def test_k1_real_diverse_records():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="real-test-k1")
    recs = _exhaust(g, max_calls=50)
    rids = {r.record_id for r in recs}
    assert len(rids) == len(recs), "k1 duplicate record_ids"


def test_k1_real_payload_complete():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="real-test-k1")
    recs = _exhaust(g, max_calls=20)
    for r in recs:
        p = r.claim_payload
        assert "arrow_chain" in p
        assert isinstance(p["arrow_chain"], list)
        assert len(p["arrow_chain"]) >= 1
        for arrow in p["arrow_chain"]:
            assert "arrow" in arrow
            assert "source_type" in arrow
            assert "target_type" in arrow


def test_k1_real_computes_target_value():
    """Real k1 should attach a computed target_value when the arrow chain
    is evaluable, distinguishing real work from stub references."""
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="real-test-k1")
    recs = _exhaust(g, max_calls=50)
    with_value = [r for r in recs if r.claim_payload.get("target_value") is not None]
    assert len(with_value) >= 5, (
        f"k1 only computed target_value for {len(with_value)} records"
    )


# =============================================================================
# l1 — real obstruction
# =============================================================================

def test_l1_real_emits_more_than_stub():
    """Stub emitted 4; real should emit ≥ 10 from real catalog enumeration."""
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="real-test-l1")
    recs = _exhaust(g)
    assert len(recs) >= 10, f"l1 real emitted only {len(recs)} records"


def test_l1_real_executes_bounded_search():
    """Real l1 should attach search statistics (count enumerated, witness
    if found) to every record."""
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="real-test-l1")
    recs = _exhaust(g, max_calls=30)
    for r in recs:
        p = r.claim_payload
        assert "enumerated_count" in p, "l1 missing enumerated_count"
        assert isinstance(p["enumerated_count"], int)
        assert p["enumerated_count"] > 0


def test_l1_real_emits_verdict_per_search_outcome():
    """Some searches find a counterexample (REJECTED+witness), some don't
    (SHADOW_CATALOG = obstruction holds)."""
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="real-test-l1")
    recs = _exhaust(g, max_calls=30)
    verdicts = {r.verdict for r in recs}
    # At least one obstruction-search must produce a real verdict
    # (not all UNVERIFIED).
    assert verdicts - {"UNVERIFIED"}, (
        f"l1 emits only UNVERIFIED, no actual search results: {verdicts}"
    )


def test_l1_real_diverse_records():
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="real-test-l1")
    recs = _exhaust(g, max_calls=30)
    rids = {r.record_id for r in recs}
    assert len(rids) == len(recs), "l1 duplicate record_ids"


def test_l1_real_payload_includes_witness_when_found():
    """If a search finds a counterexample, the payload should include the
    witness so the falsification is reproducible."""
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="real-test-l1")
    recs = _exhaust(g, max_calls=30)
    rejected = [r for r in recs if r.verdict == "REJECTED"]
    for r in rejected:
        assert r.claim_payload.get("witness") is not None, (
            f"l1 REJECTED record missing witness: {r.canonical_claim_text}"
        )


# =============================================================================
# m1 — real minimal counterexample
# =============================================================================

def test_m1_real_emits_more_than_stub():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="real-test-m1")
    recs = _exhaust(g)
    assert len(recs) >= 8, f"m1 real emitted only {len(recs)} records"


def test_m1_real_certificate_is_actual_enumeration():
    """Real m1 minimality_certificate.enumerated_count must reflect
    the actual count of smaller objects checked."""
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="real-test-m1")
    recs = _exhaust(g, max_calls=30)
    for r in recs:
        cert = r.claim_payload.get("minimality_certificate") or {}
        assert "enumerated_count" in cert
        assert isinstance(cert["enumerated_count"], int)
        assert cert["enumerated_count"] >= 0


def test_m1_real_emits_no_violator_when_conjecture_holds():
    """Some conjectures hold on the entire enumeration range — m1 must
    handle the 'no minimal counterexample found' case with verdict
    SHADOW_CATALOG."""
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="real-test-m1")
    recs = _exhaust(g, max_calls=30)
    verdicts = {r.verdict for r in recs}
    assert verdicts - {"UNVERIFIED"}, (
        f"m1 emits only UNVERIFIED, no actual search results"
    )


def test_m1_real_diverse_records():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="real-test-m1")
    recs = _exhaust(g, max_calls=30)
    rids = {r.record_id for r in recs}
    assert len(rids) == len(recs), "m1 duplicate record_ids"


def test_m1_real_minimal_violator_is_smallest_in_certificate():
    """For records where a violator was found, the violator's size must
    be strictly larger than every enumerated-passing object's size."""
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="real-test-m1")
    recs = _exhaust(g, max_calls=30)
    with_violator = [
        r for r in recs
        if r.claim_payload.get("minimal_violator") is not None
        and r.claim_payload.get("minimal_violator_size") is not None
    ]
    for r in with_violator:
        cert = r.claim_payload["minimality_certificate"]
        size = r.claim_payload["minimal_violator_size"]
        smaller_sizes = cert.get("smaller_passing_sizes", [])
        for s in smaller_sizes:
            assert s < size, (
                f"m1 cert claims size {s} passes but {size} is minimal — inconsistent"
            )


# =============================================================================
# n1 — real active disagreement
# =============================================================================

def test_n1_real_emits_more_than_stub():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="real-test-n1")
    recs = _exhaust(g)
    # If the corpus has no disagreements, n1 may legit emit zero —
    # but in stub-replacement we require ≥ 5 from a small synthetic
    # workload at init time.
    assert len(recs) >= 5, f"n1 real emitted only {len(recs)} records"


def test_n1_real_records_reference_real_input():
    """n1's subject_record_summary must point to a real record_id from
    the corpus or a synthetic-input identifier (not a free-form string)."""
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="real-test-n1")
    recs = _exhaust(g, max_calls=30)
    for r in recs:
        p = r.claim_payload
        assert "subject_record_id" in p or "subject_record_hash" in p, (
            "n1 must identify subject record by id or hash, not just summary"
        )


def test_n1_real_disagreements_are_actual():
    """The two verdicts in each n1 record must actually differ."""
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="real-test-n1")
    recs = _exhaust(g, max_calls=30)
    for r in recs:
        p = r.claim_payload
        assert p["verdict_a"] != p["verdict_b"], (
            f"n1 emitted record with V_a == V_b: {p}"
        )


def test_n1_real_diverse_records():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="real-test-n1")
    recs = _exhaust(g, max_calls=30)
    rids = {r.record_id for r in recs}
    assert len(rids) == len(recs), "n1 duplicate record_ids"


def test_n1_real_verifier_pair_named():
    """Both verifiers must have non-placeholder names referring to
    actual logic. We forbid the stub names like 'fast_heuristic_check'."""
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="real-test-n1")
    recs = _exhaust(g, max_calls=30)
    forbidden = {"fast_heuristic_check", "kill_pattern_classifier_v1",
                 "kill_pattern_classifier_v2", "polyfit_dps_15",
                 "polyfit_dps_30"}
    for r in recs:
        p = r.claim_payload
        # Allow real verifier names to overlap with stub-like names only
        # if at least the verifier_a and verifier_b refer to real logic;
        # we check that the explicit stub names don't appear in BOTH
        # fields of any record (a record using both stub names is
        # certainly stub data).
        if p["verifier_a"] in forbidden and p["verifier_b"] in forbidden:
            pytest.fail(
                f"n1 record uses two stub verifier names: "
                f"{p['verifier_a']} vs {p['verifier_b']}"
            )


# =============================================================================
# o1 — real conjecture neighborhood
# =============================================================================

def test_o1_real_emits_more_than_stub():
    """Stub emitted 4; real with theorem × perturbation cross-product
    should emit ≥ 15."""
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="real-test-o1")
    recs = _exhaust(g)
    assert len(recs) >= 15, f"o1 real emitted only {len(recs)} records"


def test_o1_real_uses_multiple_perturbation_operators():
    """Real o1 should emit multiple perturbation operators across the
    pool of theorems, not just one perturbation per theorem."""
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="real-test-o1")
    recs = _exhaust(g, max_calls=50)
    ops = {r.claim_payload.get("perturbation_operator") for r in recs}
    assert len(ops) >= 3, f"o1 used only {len(ops)} perturbation operators"


def test_o1_real_diverse_theorems():
    """Real o1 catalog should cover ≥ 5 theorems."""
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="real-test-o1")
    recs = _exhaust(g, max_calls=50)
    theorems = {r.claim_payload.get("source_theorem") for r in recs}
    assert len(theorems) >= 5, f"o1 covered only {len(theorems)} theorems"


def test_o1_real_diverse_records():
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="real-test-o1")
    recs = _exhaust(g, max_calls=50)
    rids = {r.record_id for r in recs}
    assert len(rids) == len(recs), "o1 duplicate record_ids"


def test_o1_real_payload_includes_original_and_perturbed_hypotheses():
    """Each record must clearly identify the original hypothesis list
    AND the perturbation applied."""
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="real-test-o1")
    recs = _exhaust(g, max_calls=30)
    for r in recs:
        p = r.claim_payload
        assert "original_hypotheses" in p
        assert isinstance(p["original_hypotheses"], list)
        assert len(p["original_hypotheses"]) >= 1
        assert "perturbation_operator" in p
        assert "perturbed_hypothesis" in p
        assert p["perturbed_hypothesis"] != p["original_hypotheses"][
            p.get("perturbed_hypothesis_index", 0)
        ]
