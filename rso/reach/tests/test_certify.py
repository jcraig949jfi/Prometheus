"""Certification is independent of training fitness and can fail (RED first)."""
import numpy as np
import pytest

from rso.reach import certify
from rso.reach._proto import org, ru, wm

P = ru.Params()


def test_certification_lives_are_disjoint_from_training_and_from_the_prototype_receipt():
    tr = set(range(certify.TRAIN0, certify.TRAIN0 + certify.N_TRAIN))
    sel = set(range(certify.SELECT0, certify.SELECT0 + certify.N_SELECT))
    sea = set(range(certify.SEALED0, certify.SEALED0 + certify.N_SEALED))
    proto_sealed = set(range(ru.SEALED_BASE + 60_000, ru.SEALED_BASE + 60_000 + 64))
    assert not (tr & sel) and not (tr & sea) and not (sel & sea) and not (sea & proto_sealed)
    assert certify.SEALED0 >= ru.SEALED_BASE and certify.SELECT0 + certify.N_SELECT <= ru.SEALED_BASE


def test_the_target_certifies_and_the_oracle_agrees():
    c = certify.certify(org.builder_min())
    assert c["certified"] is True
    assert c["selection_ok"] and c["sealed_verdict"] == ru.PASS and c["oracle_agrees"]


@pytest.mark.parametrize("impostor", ["holder", "constant", "lookup", "empty"])
def test_impostors_do_not_certify(impostor):
    prog = {"holder": org.holder(P.K), "constant": org.constant(), "lookup": org.lookup(),
            "empty": np.zeros((8, 4), dtype=np.int64)}[impostor]
    c = certify.certify(prog)
    assert c["certified"] is False


def test_a_training_perfect_lookup_with_its_inherited_table_is_rejected():
    """An organism that is perfect on ONE life only (the impostor class training fitness can be fooled by) must fail
    selection. The search genome has an empty store, so this is a fire test of the selection gate itself."""
    st = org.lookup_store(P.seed, certify.TRAIN0, P.K, P.R, P.S)
    c = certify.certify(org.lookup(), store0=st)
    assert c["certified"] is False


def test_oracle_disagreement_voids_the_certificate(monkeypatch):
    """Fire test: if the compiled evaluator and the independent oracle disagree, the hit is VOID, never certified."""
    real = certify._numba_sealed_counts

    def lie(prog, store0):
        c = real(prog, store0).copy()
        c[wm.T_PROBE, 1] -= 1
        return c
    monkeypatch.setattr(certify, "_numba_sealed_counts", lie)
    c = certify.certify(org.builder_min())
    assert c["certified"] is False and c["oracle_agrees"] is False and c["status"] == "VOID"


def test_training_fitness_is_never_read_by_certify():
    """certify() recomputes everything it uses; a wrong claimed training score changes nothing."""
    a = certify.certify(org.builder_min(), claimed_training_fit=0)
    b = certify.certify(org.builder_min(), claimed_training_fit=126)
    assert a["certified"] == b["certified"] is True
    assert a["training_fit_recomputed"] == 126
