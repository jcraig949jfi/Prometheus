"""E-R8-H1: the sham ladder arms keep exactly the nuisance they claim, and the preregistered outcome rule reads
planted response curves as designed (A, B, C, FLAT, INDETERMINATE)."""
import numpy as np
import pytest

from primordial.cohorts.e import r8_h1_sham_ladder as H
from primordial.fabric import envelope as EV
from primordial.qd import e7_run as E7
from primordial.score import evidence_n as EN


@pytest.fixture(scope="module")
def worlds():
    return E7.G7(H.RECIPIENT, H.FAMILY), E7.G7(H.DONOR, H.FAMILY)


def test_charge_columns_differ_between_donor_and_recipient(worlds):
    g7r, g7d = worlds
    assert (H.charge_col(g7r), H.charge_col(g7d)) == (2, 3)


@pytest.mark.parametrize("seed", range(6))
def test_arms_integrity_and_determinism(worlds, seed):
    g7r, g7d = worlds
    dA = g7r.pack(g7r.init(np.random.default_rng(seed), 16))
    filler = g7r.pack(g7r.init(np.random.default_rng(1000 + seed), 64))
    fam, rs = H.FAMILIES[seed % 4], H.RUN_SEEDS[seed % 8]
    slots, meta = H.make_arms(g7r, g7d, dA, filler, fam, rs)
    integ = H.arm_integrity(g7r, dA, slots, meta)
    assert all(v["ok"] for v in integ.values()), integ
    slots2, meta2 = H.make_arms(g7r, g7d, dA, filler, fam, rs)
    assert all(np.array_equal(slots[a], slots2[a]) for a in H.ARMS) and meta == meta2
    assert meta["L1_partial_featperm"]["moved"] == 3 and meta["L2_full_featperm"]["moved"] == 5
    assert meta["X_charge_align"]["perm"] == [0, 1, 3, 2, 4]
    # L2 is transfer_v2's sham exactly (R7's control)
    from primordial.cohorts.e import transfer_v2 as V
    assert np.array_equal(slots["L2_full_featperm"], V.featperm(g7r, dA, rs, H.RECIPIENT, fam)[0])


def test_integrity_catches_a_broken_arm(worlds):
    g7r, g7d = worlds
    dA = g7r.pack(g7r.init(np.random.default_rng(7), 16))
    slots, meta = H.make_arms(g7r, g7d, dA, g7r.pack(g7r.init(np.random.default_rng(8), 64)), 4200, 24)
    (W, b), C = g7r.unpack(slots["L3_entry_shuffle"])
    slots["L3_entry_shuffle"] = g7r.pack(((W, b + 1), C))
    (W4, b4), C4 = g7r.unpack(slots["L4_matched_gaussian"])
    slots["L4_matched_gaussian"] = g7r.pack(((W4 * 2, b4), C4))
    integ = H.arm_integrity(g7r, dA, slots, meta)
    assert not integ["L3_entry_shuffle"]["ok"] and not integ["L4_matched_gaussian"]["ok"]


def _rows(curve, n_runs=32, noise=0.3, charge=0.0, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i, (f, rs) in enumerate(H.run_order()[:n_runs]):
        base = 100 + rng.normal(0, 2)
        for arm in H.ARMS:
            if arm == "scratch":
                v = base - 1
            elif arm == "X_charge_align":
                v = base + curve[0] + charge
            else:
                v = base + curve[H.ORDINAL[arm]]
            rows.append({"exp_id": H.EXP, "condition": arm, "status": H.STATUS[arm], "run_id": f"{f}|{rs}",
                         "held_auc": float(v + rng.normal(0, noise)), "held64": 1.0, "zero_shot_held64": 1.0,
                         "train_auc": 1.0, "arm_integrity": {"ok": True}, "donor_fused_eq_numpy": True,
                         "arm_meta": {"charge_aligned": bool(i % 4 == 0)}})
    return rows


@pytest.mark.parametrize("curve,want", [((4, 3, 2, 1, 0), "A_DECREASING_WITH_DESTRUCTION"),
                                        ((0, 1, 2, 3, 4), "B_INCREASING_WITH_DESTRUCTION"),
                                        ((0, 3, 3, 3, 0), "C_NONMONOTONIC"),
                                        ((0, 0, 0, 0, 0), "FLAT_NO_SYSTEMATIC_RESPONSE")])
def test_outcome_rule_reads_planted_curves(curve, want):
    got = H.analyze(_rows(curve))
    assert got["n_complete_runs"] == 32 and got["outcome"] == want


def test_partial_sample_is_indeterminate_and_charge_reading():
    assert H.analyze(_rows((4, 3, 2, 1, 0), n_runs=28))["outcome"] == "INDETERMINATE"
    got = H.analyze(_rows((0, 0, 0, 0, 0), charge=3.0))
    assert got["structural_charge_align"]["reading"] == "CHARGE_ALIGNMENT_RAISES"


def test_spearman_ties_and_holm():
    assert H.spearman_levels([1, 1, 1, 1, 1]) == 0.0
    assert H.spearman_levels([0, 1, 2, 3, 4]) == pytest.approx(1.0)
    assert H.holm({"a": 0.01, "b": 0.04}) == {"a": 0.02, "b": 0.04}


def test_envelope_is_an_observation_with_a_conforming_sample():
    env = dict(H.ENVELOPE)
    assert EV.validate(env) == []
    assert EN.admission_reasons(env) == []
    assert env["runs_total"] == 32 and env["rng_family_count"] == 4 and env["runs_per_family"] == 8
    assert env["experiment_class"] not in EN.VERDICT_CLASSES and env["evidence_class"] == "OBSERVATION"
    assert EV.check_rows([{"status": H.STATUS[a]} for a in H.ARMS]) == []
