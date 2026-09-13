"""S4 producer contract: interchangeable, not epistemically identical."""
import inspect
import random

import pytest

from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P


def _score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _fossils(t, xs):
    return [FI.Fossil(x, _score(x, t)) for x in xs]


def test_contract_fields_and_versions():
    L = 8; t = "10110010"; fs = _fossils(t, ["00000000", "11110000"]); si = {"lane": "s4", "world": 1, "step": 1}
    for p in (P.produce_U(L, si), P.produce_G(fs, si), P.produce_W(fs, si)):
        for f in ("producer_id", "producer_version", "evidence_policy", "evidence_snapshot_id", "probe", "seed_inputs", "objective", "tie_class", "ancestry", "compute_seconds"):
            assert hasattr(p, f)
        assert len(p.probe) == L and p.producer_version == P.PRODUCER_VERSION and p.probe in p.tie_class


def test_U_is_pew_blind_by_signature_and_by_behaviour():
    assert "fossils" not in inspect.signature(P.produce_U).parameters and "evidence" not in inspect.signature(P.produce_U).parameters
    si = {"lane": "s4", "world": 3, "step": 2}
    a = P.produce_U(12, si); b = P.produce_U(12, dict(si))
    assert a.probe == b.probe and a.evidence_policy == "PEW_BLIND" and a.evidence_snapshot_id is None and a.ancestry["fossils_consumed"] == []


def test_cheat_no_producer_can_receive_the_hidden_target():
    for fn in (P.produce_U, P.produce_G, P.produce_W, P.produce_M):
        params = inspect.signature(fn).parameters
        assert not any(k in ("target", "hidden_target", "t") for k in params), fn.__name__
    # a deliberately cheating producer would need the target as an input; the harness contract has no such slot
    def cheating(fossils, seed_inputs, hidden_target): return hidden_target
    assert "hidden_target" in inspect.signature(cheating).parameters   # and therefore cannot be called through the contract


def test_pew_consuming_producers_change_with_evidence_and_snapshot_ids_differ():
    L = 10; t = "1011001010"; si = {"lane": "s4", "world": 5, "step": 1}
    fs1 = _fossils(t, ["0000000000"]); fs2 = _fossils(t, ["0000000000", "1111100000"])
    g1, g2 = P.produce_G(fs1, si), P.produce_G(fs2, si)
    assert g1.evidence_snapshot_id != g2.evidence_snapshot_id and g1.evidence_policy == "PEW_CONSUMING"
    assert g1.ancestry["fossils_consumed"] != g2.ancestry["fossils_consumed"]
    # same probe from different histories must still be distinguishable events: force it and check the snapshot ids
    w1, w2 = P.produce_W(fs1, si), P.produce_W(fs2, si)
    assert w1.evidence_snapshot_id != w2.evidence_snapshot_id


def test_W_is_exact_global_optimum_at_small_L_and_never_worse_than_G():
    rnd = random.Random(4)
    for _ in range(8):
        L = 10; t = "".join(rnd.choice("01") for _ in range(L)); fs = _fossils(t, list({"".join(rnd.choice("01") for _ in range(L)) for _ in range(2)}))
        si = {"lane": "s4", "world": _, "step": 1}
        g, w = P.produce_G(fs, si), P.produce_W(fs, si)
        best_num, cls = AQ.optimum_by_enumeration(fs)
        st = AQ.feasible(fs)
        assert AQ.value(st, w.probe).er_numerator == best_num and w.probe in cls and w.ancestry["exhaustive"]
        assert w.objective_value <= g.objective_value + 1e-9


def test_W_pool_is_not_fossil_centred_at_large_L():
    rnd = random.Random(8); L = 24; t = "".join(rnd.choice("01") for _ in range(L)); fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L))])
    st = AQ.feasible(fs); pool = P.widened_pool(st, fs, random.Random(1))
    far = sum(1 for q in pool if min(AQ.hamming(q, f.bits) for f in fs) >= L // 3)
    assert len(pool) > 300 and far >= 200


def test_M_is_tractable_at_small_L_and_declares_intractability():
    rnd = random.Random(2); L = 8; t = "".join(rnd.choice("01") for _ in range(L)); fs = _fossils(t, ["".join(rnd.choice("01") for _ in range(L))])
    m = P.produce_M(fs, {"lane": "s4", "world": 0, "step": 1})
    assert m.producer_id == "M" and m.objective_value is not None and m.compute_seconds < 60 and not m.extra.get("intractable")
    m2 = P.produce_M(fs, {"lane": "s4", "world": 0, "step": 1}, time_bound_s=0.0)
    assert m2.extra.get("intractable") is True and len(m2.probe) == L


def test_external_channel_slot_is_recorded_not_built():
    e = P.external_channel()
    assert e["evidence_policy"] == "EXTERNAL" and e["satisfies_contract"] and e["requires_change_to_harmonia"] is False
