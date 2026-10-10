"""The preregistered analysis on SYNTHETIC ledgers (no reach-world outcome is used)."""
import random

from rso.reach import analyze


def _ledger(rounds, rates, seed=0, void_at=None):
    rng = random.Random(seed)
    rows = []
    for j in range(rounds):
        for d in analyze.DISTANCES:
            for a in analyze.ARMS:
                disc = rng.random() < rates.get(a, 0.04)
                cert = {"status": "VOID" if (void_at == (j, a, d)) else ("CERTIFIED" if disc else "NOT_CERTIFIED"),
                        "certified": disc} if disc or void_at == (j, a, d) else None
                rows.append(dict(round=j, arm=a, d=d, discovery=disc, hit=cert is not None, evals=1000 if disc else -1,
                                 certificate=cert, cells=10, distinct_genomes=100, stones_retained_end=0,
                                 stones_evaluated=0, max_stone_restored=0))
    return rows


def test_a_planted_large_effect_separates_and_names_the_direction():
    res = analyze.analyze(_ledger(24, {"X1": 0.6}))
    assert res["status"] == "ANALYZED"
    assert res["contrasts"]["C2_retention"]["verdict"] == "SEPARATES: X1 > chain_neutral"
    assert res["contrasts"]["C3_rarely_visited_selection"]["verdict"].startswith("SEPARATES: X2 < X1")


def test_no_effect_separates_nothing():
    res = analyze.analyze(_ledger(24, {}))
    assert all(c["verdict"].startswith("NOT SEPARATED") for c in res["contrasts"].values())


def test_incomplete_rounds_are_dropped_and_too_few_rounds_is_underpowered():
    rows = _ledger(11, {"X1": 0.9})
    rows += [r for r in _ledger(12, {})[-18:] if r["arm"] != "X3G"]       # a partial 12th round
    res = analyze.analyze(rows)
    assert res["rounds_completed"] == 11 and res["status"] == "UNDERPOWERED" and "contrasts" not in res


def test_a_void_certificate_voids_the_analysis():
    res = analyze.analyze(_ledger(24, {}, void_at=(3, "X2", 8)))
    assert res["status"] == "VOID"


def test_zero_counts_carry_an_upper_bound_not_impossibility():
    res = analyze.analyze(_ledger(24, {a: 0.0 for a in analyze.ARMS}))
    c = res["cells"]["X3 d=8"]
    assert c["discoveries"] == 0 and abs(c["upper_95"] - (1 - 0.05 ** (1 / 24))) < 1e-6
