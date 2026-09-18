"""Positive, negative and cheat controls for S1-S4, plus model self-checks."""
import random

import models as M
import sims as S


# ------------------------------------------------------------------ S1
def test_s1_positive_no_verification_full_trust_spreads():
    rng = random.Random(1)
    sizes = [S.s1_run(2000, 4, 1.0, 0.0, rng) for _ in range(20)]
    assert sum(s > 100 for s in sizes) >= 15


def test_s1_negative_perfect_verification_never_spreads():
    rng = random.Random(2)
    assert all(S.s1_run(2000, 8, 1.0, 1.0, rng) == 1 for _ in range(50))


def test_s1_cheat_certain_transmission_reaches_almost_everyone():
    rng = random.Random(3)
    assert S.s1_run(2000, 8, 1.0, 0.0, rng) >= 0.99 * 2000


def test_s1_models_sane():
    assert M.s1_outbreak_prob(4, 0.2) < 1e-9          # R0 = 0.8
    assert 0.5 < M.s1_outbreak_prob(2, 1.0) <= 1.0    # R0 = 2, certain edges
    assert abs(M.s1_final_fraction(2.0) - 0.7968) < 1e-3
    assert M.s1_required_verification(4, 0.5) == 0.5


# ------------------------------------------------------------------ S2
def test_s2a_positive_perfect_verifier_gives_perfect_precision():
    rng = random.Random(4)
    res = [S.s2a_trial(0.05, 0.0, 1.0, 5000, rng) for _ in range(300)]
    assert res.count(0) == 0 and res.count(1) > 250


def test_s2a_negative_useless_proposer_all_accepts_wrong():
    rng = random.Random(5)
    res = [S.s2a_trial(0.0, 0.05, 1.0, 5000, rng) for _ in range(300)]
    assert res.count(1) == 0 and res.count(0) > 250


def test_s2a_cheat_rubber_stamp_verifier_precision_equals_solve_rate():
    rng = random.Random(6)
    res = [S.s2a_trial(0.3, 1.0, 1.0, 10, rng) for _ in range(4000)]
    assert abs(res.count(1) / 4000 - 0.3) < 0.03


def test_s2b_model_k1_equals_p():
    assert abs(M.s2b_accuracy(0.1, 0.05, [1])[0] - 0.1) < 1e-6


def test_s2b_cheat_all_wrong_are_hacks_large_k_fails():
    rng = random.Random(7)
    acc = sum(S.s2b_trial(0.1, 1.0, 256, rng) for _ in range(300)) / 300
    assert acc < 0.05


# ------------------------------------------------------------------ S3
def test_s3_positive_unaudited_exploit_takes_over():
    rng = random.Random(8)
    assert S.s3_run(200, 0.5, 0.0, 0.005, 300, rng) > 0.9


def test_s3_negative_heavily_audited_exploit_stays_rare():
    rng = random.Random(9)
    assert S.s3_run(200, 0.1, 0.6, 0.005, 300, rng) < 0.1


def test_s3_model_boundary():
    assert abs(M.s3_audit_boundary(0.5) - 1 / 3) < 1e-12


# ------------------------------------------------------------------ S4
def test_s4_negative_coinflip_agents_stay_at_half():
    rng = random.Random(10)
    acc = sum(S.s4_majority_trial(81, 0.5, 0.0, rng) for _ in range(4000)) / 4000
    assert abs(acc - 0.5) < 0.03


def test_s4_positive_good_independent_agents_approach_one():
    rng = random.Random(11)
    assert sum(S.s4_majority_trial(81, 0.7, 0.0, rng) for _ in range(2000)) / 2000 > 0.99


def test_s4_cheat_full_correlation_equals_single_agent():
    rng = random.Random(12)
    acc = sum(S.s4_majority_trial(81, 0.7, 1.0, rng) for _ in range(4000)) / 4000
    assert abs(acc - 0.7) < 0.03


def test_s4_herding_chain_n1_is_p():
    assert abs(M.s4_herding_last_correct(1, 0.7) - 0.7) < 1e-12
