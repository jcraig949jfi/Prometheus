"""Instrument controls for the four RSI toys (base role s2: positive, negative, cheat).

Positive: the instrument detects real success. Negative: it reports none
where none exists. Cheat: injected success is observed by the channel, so
a null would mean "nothing happened", not "could not have been seen".
"""
import random

import e1_feedback as e1
import e2_self_improver as e2
import e3_memory as e3
import e4_guard as e4


# ------------------------------------------------------------------ E1
def test_e1_positive_distance_one_is_solved_by_every_informative_regime():
    rng = random.Random(0)
    for seed in range(20):
        tgt = [rng.randrange(e1.V) for _ in range(8)]
        start = tgt[:]
        start[3] = (tgt[3] + 1) % e1.V
        d = e1.run(8, "DENSE", seed, start=start, target=tgt)
        s = e1.run(8, "SCALAR", seed, start=start, target=tgt)
        assert d.solved and d.evaluations <= e1.V
        assert s.solved


def test_e1_negative_unreachable_target_is_never_reported_solved():
    for regime in e1.REGIMES:
        for seed in range(5):
            o = e1.run(4, regime, seed, unreachable=True)
            assert not o.solved
            assert o.evaluations == o.budget


def test_e1_cheat_injected_solution_is_observed_at_zero_cost():
    tgt = [1, 2, 3, 4]
    for regime in e1.REGIMES:
        o = e1.run(4, regime, 0, start=tgt, target=tgt)
        assert o.solved and o.evaluations == 0


def test_e1_dense_always_solves_within_budget():
    # eligibility: a DENSE failure is a defect, not a result
    for k in (2, 4, 8, 16):
        for seed in range(30):
            assert e1.run(k, "DENSE", seed).solved


# ------------------------------------------------------------------ E2
def test_e2_positive_good_theta_solves_sphere():
    # (the first draft used lambda=4, patience=50: 0.06 at 400 evals, 2.8e-17 at 4000 --
    # a slow setting, not a broken optimiser; journal 2026-09-17)
    good = e2.Theta(-1.0, 1.5, 1, 400)
    t = e2.make_task("sphere", 0)
    ctr = e2.Counter(lambda x: e2.f_value(t, x))
    _, fb, _ = e2.es_minimise(good, None, e2.D, [-5] * e2.D, [5] * e2.D, t.x0, e2.BASE_BUDGET,
                              random.Random(1), "honest", ctr)
    assert fb < 1e-3
    assert ctr.real == e2.BASE_BUDGET


def test_e2_negative_constant_objective_reports_no_improvement():
    t0 = e2.Theta(-1.0, 1.5, 4, 50)
    ctr = e2.Counter(lambda x: 7.0)
    _, fb, _ = e2.es_minimise(t0, None, 3, [0] * 3, [1] * 3, [0.5] * 3, 100, random.Random(2), "honest", ctr)
    assert fb == 7.0


def test_e2_cheat_leaky_accounting_is_caught_by_the_counter():
    lam16 = e2.Theta(-1.0, 1.5, 16, 50)
    t = e2.make_task("sphere", 0)
    ctr = e2.Counter(lambda x: e2.f_value(t, x))
    _, _, declared = e2.es_minimise(lam16, None, e2.D, [-5] * e2.D, [5] * e2.D, t.x0, e2.BASE_BUDGET,
                                    random.Random(3), "leaky", ctr)
    assert declared <= e2.BASE_BUDGET + 1
    assert ctr.real >= 15 * e2.BASE_BUDGET  # the real spend the leaky label hides


def test_e2_theta_roundtrip():
    th = e2.Theta(*e2.THETA0)
    back = e2.Theta.decode(th.encode())
    assert back.lam == th.lam and back.patience == th.patience
    assert abs(back.log_sigma0 - th.log_sigma0) < 1e-9 and abs(back.a - th.a) < 1e-9


# ------------------------------------------------------------------ E3
def test_e3_positive_verified_distillation_generalises_in_color_worlds():
    accs = [e3.run("COLOR", "DISTILLED_VERIFIED", False, s).test_acc for s in range(30)]
    assert sum(accs) / len(accs) > 0.85


def test_e3_negative_raw_memory_cannot_generalise_to_unseen_shapes():
    accs = [e3.run("COLOR", "RAW", False, s).test_acc for s in range(60)]
    assert sum(accs) / len(accs) < 0.4


def test_e3_cheat_injected_false_rules_are_seen_in_unverified_memory():
    # the channel can observe poison: unverified memory must be hurt by it
    clean = [e3.run("COLOR", "DISTILLED_UNVERIFIED", False, s).test_acc for s in range(30)]
    poisoned = [e3.run("COLOR", "DISTILLED_UNVERIFIED", True, s).test_acc for s in range(30)]
    assert sum(poisoned) / 30 < sum(clean) / 30 - 0.2


# ------------------------------------------------------------------ E4
def test_e4_positive_true_rule_scores_near_the_noise_ceiling():
    a, b, c = e4.make_sets(0)
    true_rule = [0, 0, 1, 0, 0, 0]
    assert 0.8 <= e4.acc(true_rule, c) <= 0.9


def test_e4_negative_no_leak_hint_carries_no_signal_on_c():
    _, _, c = e4.make_sets(0, leak=False)
    assert abs(e4.acc([1, 0, 0, 0, 0, 0], c) - 0.5) < 0.06


def test_e4_cheat_planted_leak_is_visible_on_a_and_flagged():
    a, b, _ = e4.make_sets(0)
    hint_only = [1, 0, 0, 0, 0, 0]
    assert e4.acc(hint_only, a) > 0.9
    assert e4.acc(hint_only, a) - e4.acc(hint_only, b) >= 0.3
