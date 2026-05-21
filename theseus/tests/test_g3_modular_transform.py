"""Unit tests for G3ModularTransformGenerator."""
from __future__ import annotations

from theseus.emit.record_schema import ClaimKind, Verdict
from theseus.generators.base import GeneratorStatus
from theseus.generators.g3_modular_transform import (
    G3ModularTransformGenerator,
    _sieve_primes,
    _hasse_bound_squared,
    _get_ap_list,
)


def test_sieve_primes_first_ten():
    assert _sieve_primes(10) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_sieve_primes_zero():
    assert _sieve_primes(0) == []


def test_sieve_primes_large():
    p = _sieve_primes(100)
    assert len(p) == 100
    assert p[-1] == 541


def test_hasse_bound_squared_formula():
    assert _hasse_bound_squared(2) == 8
    assert _hasse_bound_squared(7) == 28
    assert _hasse_bound_squared(101) == 404


def test_get_ap_list_valid():
    assert _get_ap_list({"base": {"a_p": [1, -1, 2]}}) == [1, -1, 2]


def test_get_ap_list_missing():
    assert _get_ap_list({"base": {}}) is None
    assert _get_ap_list({"base": {"a_p": None}}) is None
    assert _get_ap_list({"base": {"a_p": "not a list"}}) is None


def test_generator_status_is_active():
    assert G3ModularTransformGenerator.status == GeneratorStatus.ACTIVE


def test_generator_emits_records_with_correct_verdict():
    g = G3ModularTransformGenerator(batch_id="test", seed=0)
    if not g._eligible:
        return
    records = []
    for _ in range(20):
        r = g.next()
        if r is None:
            break
        records.append(r)
    assert len(records) >= 1
    for r in records:
        assert r.generator_id == "g3"
        assert r.claim_kind == ClaimKind.SYMMETRY_TRANSFORM.value
        # Hasse bound is a theorem (proved by Hasse 1933) — every record
        # should be SHADOW_CATALOG. Any REJECTED is a substrate-detected
        # anomaly (=Weil-conjecture-collapse-candidate, fascinating).
        assert r.verdict in {
            Verdict.SHADOW_CATALOG.value,
            Verdict.REJECTED.value,
        }
        # Internal consistency: |a_p|² and 4p must agree with verdict.
        ap_sq = r.claim_payload["a_p_squared"]
        bound = r.claim_payload["hasse_bound_squared"]
        if r.verdict == Verdict.SHADOW_CATALOG.value:
            assert ap_sq <= bound
        else:
            assert ap_sq > bound


def test_hasse_bound_should_hold_universally_on_catalog():
    """All catalog ECs are over Q with proven modularity → Hasse bound
    is a theorem. 100% hold rate expected."""
    g = G3ModularTransformGenerator(batch_id="test", seed=777)
    if not g._eligible:
        return
    holds_count = 0
    total = 0
    for _ in range(min(500, len(g._eligible) * 10)):
        r = g.next()
        if r is None:
            break
        total += 1
        if r.claim_payload.get("holds"):
            holds_count += 1
    if total > 0:
        # Theorem says 100%. If catalog has a Hasse-bound failure, that's
        # a catalog-corruption or substrate-discovery moment. Either way
        # we want to know — assert strict 100%.
        assert holds_count == total, (
            f"Hasse bound fails {total - holds_count}/{total} — "
            f"catalog corruption or unexpected substrate finding"
        )


def test_generator_seed_determinism():
    g1 = G3ModularTransformGenerator(batch_id="b1", seed=314)
    g2 = G3ModularTransformGenerator(batch_id="b2", seed=314)
    ids1 = []
    ids2 = []
    for _ in range(20):
        r1 = g1.next()
        r2 = g2.next()
        if r1 is not None and r2 is not None:
            ids1.append(r1.record_id)
            ids2.append(r2.record_id)
    assert ids1 == ids2


def test_registry_can_resolve_g3():
    from theseus.registry import get_generator_class

    cls = get_generator_class("g3")
    assert cls is G3ModularTransformGenerator
