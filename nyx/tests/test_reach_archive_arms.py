"""The reach archive-arm ladder on TOY landscapes only (no reach world, no science). Each test is a control that shows
the ladder's contrast CAN fire: a landscape built so that exactly one ingredient decides success."""
import random

from nyx.atlas.experiments.reach_archive.archive_arms import ARMS, run_chain, run_lineage


def _rng(seed):
    r = random.Random(seed)
    cache = {}

    def u(i):
        if i not in cache:
            cache[i] = r.random()
        return cache[i]
    return u


def _bits_world(n, fitness, cell):
    def evaluate(p):
        return fitness(p), cell(p)

    def propose_factory(seed):
        r = random.Random(seed)

        def propose(p, i):
            k = r.randrange(n)
            return p[:k] + (1 - p[k],) + p[k + 1:]
        return propose
    return evaluate, propose_factory


def test_on_a_flat_plateau_ge_acceptance_already_admits_new_cells():
    """FOUND WHEN THIS TEST FIRST RAN (2026-10-03): on a zero-reward plateau, '>= parent' admits every neutral move,
    and a neutral move into an empty cell founds that cell, so X2 already climbs the cell ladder: the X3 vs X2 contrast
    CANNOT fire on a flat plateau. Recorded as a test so the design keeps saying so."""
    n = 10
    evaluate, pf = _bits_world(n, lambda p: 10 if sum(p) == n else 0, lambda p: sum(p))
    for s in range(5):
        assert run_lineage("X2_archive_count_ge", (0,) * n, evaluate, pf(s), 3000, 10, _rng(s))[0] >= 0


def test_new_cell_acceptance_is_what_crosses_a_deceptive_valley():
    """Fitness DECREASES with the number of ones except at the all-ones target; cells = number of ones. Every step
    toward the target is strictly worse, so only X3 (which admits a WORSE child into an EMPTY cell) can walk there.
    Control: the contrast X3 vs X2 must fire here."""
    n = 10
    evaluate, pf = _bits_world(n, lambda p: 3 * n if sum(p) == n else n - sum(p), lambda p: sum(p))
    wins = {a: 0 for a in ARMS}
    for s in range(20):
        for a in ARMS:
            e, _ = run_lineage(a, (0,) * n, evaluate, pf(s), 3000, 3 * n, _rng(s))
            wins[a] += e >= 0
    assert wins["X3_archive_count_newcell"] > wins["X2_archive_count_ge"], wins


def test_retention_matters_when_the_chain_can_drift_away():
    """A deceptive landscape where a neutral chain drifts along a plateau away from the only gateway, while an
    archive keeps the gateway-adjacent program. Control: X1 (archive, greedy) must not do worse than the chain."""
    n = 8
    gate = (1, 1, 0, 0, 0, 0, 0, 0)

    def f(p):
        if p == (1,) * n:
            return 3
        return 1 if sum(a == b for a, b in zip(p, gate)) >= n - 1 or sum(p) >= 2 else 0
    evaluate, pf = _bits_world(n, f, lambda p: p)
    x1 = sum(run_lineage("X1_archive_greedy_ge", (0,) * n, evaluate, pf(s), 4000, 3, _rng(s))[0] >= 0 for s in range(15))
    ch = sum(run_chain((0,) * n, evaluate, pf(s), 4000, 3) >= 0 for s in range(15))
    assert x1 >= ch, (x1, ch)


def test_arms_are_deterministic_and_the_ladder_is_complete():
    assert ARMS == ("X1_archive_greedy_ge", "X2_archive_count_ge", "X3_archive_count_newcell")
    n = 6
    evaluate, pf = _bits_world(n, lambda p: sum(p), lambda p: sum(p))
    for a in ARMS:
        r1 = run_lineage(a, (0,) * n, evaluate, pf(3), 500, n, _rng(3))
        r2 = run_lineage(a, (0,) * n, evaluate, pf(3), 500, n, _rng(3))
        assert r1 == r2
        assert r1[0] >= 0   # a smooth landscape: every arm reaches the top
