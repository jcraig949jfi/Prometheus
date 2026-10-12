"""C-013-T010 harness tests. Written before the implementation (RED first; receipt red_observed).

Run:  <venv-with-numba>/python -m pytest rso/reach/tests -q
"""
import hashlib
import random
import subprocess

import numpy as np
import pytest

from rso.reach import arms
from rso.reach._proto import PROTO_DIR, org, ru

NYX_SHA = "3318a2098"
NYX_PATH = "nyx/atlas/experiments/reach_archive/archive_arms.py"


# ---------------------------------------------------------------- the generic ladder vs Nyx's reference (toy worlds)

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


def test_nyx_reference_file_is_the_cited_commit():
    """The differential below is against Nyx's file exactly as committed at 3318a2098 (read only)."""
    at_sha = subprocess.run(["git", "show", "%s:%s" % (NYX_SHA, NYX_PATH)], capture_output=True, check=True,
                            cwd=str(arms.ROOT)).stdout
    on_disk = (arms.ROOT / NYX_PATH).read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(at_sha).hexdigest() == hashlib.sha256(on_disk).hexdigest()


@pytest.mark.parametrize("landscape", ["plateau", "valley", "smooth", "drift"])
def test_generic_ladder_matches_nyx_reference_on_toy_worlds(landscape):
    from nyx.atlas.experiments.reach_archive import archive_arms as nyx
    n = 8
    worlds = {
        "plateau": (lambda p: 10 if sum(p) == n else 0, lambda p: sum(p), 10),
        "valley": (lambda p: 3 * n if sum(p) == n else n - sum(p), lambda p: sum(p), 3 * n),
        "smooth": (lambda p: sum(p), lambda p: sum(p), n),
        "drift": (lambda p: 3 if p == (1,) * n else (1 if sum(p) >= 2 else 0), lambda p: p, 3),
    }
    f, c, top = worlds[landscape]
    evaluate, pf = _bits_world(n, f, c)
    for s in range(6):
        for a_nyx, a_me in zip(nyx.ARMS, ("X1", "X2", "X3")):
            ref = nyx.run_lineage(a_nyx, (0,) * n, evaluate, pf(s), 1500, top, _rng(s))
            me = arms.run_ladder(a_me, (0,) * n, evaluate, pf(s), 1500, top, _rng(s))
            assert me["evals"] == ref[0], (landscape, s, a_me)
            assert me["cells"] == ref[1]["cells"]
        ref = nyx.run_chain((0,) * n, evaluate, pf(s), 1500, top)
        me = arms.run_ladder("chain_neutral", (0,) * n, evaluate, pf(s), 1500, top, _rng(s))
        assert me["evals"] == ref


def test_x3_admits_a_worse_child_into_an_empty_cell_and_x2_does_not():
    n = 6
    evaluate, pf = _bits_world(n, lambda p: 3 * n if sum(p) == n else n - sum(p), lambda p: sum(p))
    wins = {a: 0 for a in ("X2", "X3")}
    for s in range(10):
        for a in wins:
            wins[a] += arms.run_ladder(a, (0,) * n, evaluate, pf(s), 2000, 3 * n, _rng(s))["evals"] >= 0
    assert wins["X3"] > wins["X2"]


def test_chain_strict_rejects_neutral_moves():
    n = 6
    evaluate, pf = _bits_world(n, lambda p: 10 if sum(p) == n else 0, lambda p: 0)
    r = arms.run_ladder("chain_strict", (0,) * n, evaluate, pf(1), 500, 10, _rng(1))
    assert r["evals"] == -1 and r["accepted"] == 0


# ---------------------------------------------------------------- reach-world adapters

P = ru.Params()
TARGET = org.builder_min()
TOY = -1000        # development lineages: knock-out index LINEAGE0 - 1000 + k; the frozen set is lineage >= 0


def test_fresh_stream_refuses_frozen_lineages_outside_a_confirmatory_run():
    with pytest.raises(ValueError):
        arms.run_reach_lineage("X1", 3, 0, budget=10)
    assert arms.run_reach_lineage("X1", 3, 0, budget=0, confirmatory=True)["evals"] == -1


@pytest.mark.parametrize("regime", ["chain_neutral", "chain_strict"])
@pytest.mark.parametrize("d", [1, 2, 3, 8])
def test_chain_reproduces_prototype_search_lineage(regime, d):
    """Differential against reach.search_lineage (the prototype's own chain), on reach.py's own hash stream."""
    import reach
    st = org.empty_store(P.S)
    reg_id = {"chain_neutral": 1, "chain_strict": 2}[regime]
    for lineage in range(3):
        out = np.zeros((8, 4), dtype=np.int64)
        done, fp = reach.search_lineage(TARGET, 8, d, st, P.seed, lineage, 3000, reg_id,
                                        P.K, P.R, P.E, P.T, P.F, P.cap, 0, 16, out)
        me = arms.run_reach_lineage(regime, d, lineage, budget=3000, impl="py", stream="reach")
        assert me["evals"] == done
        assert me["final_fit"] == fp
        assert np.array_equal(me["final_prog"], out)


def test_descriptor_is_the_per_type_correct_count_vector():
    fit, nfix, key = arms.train_eval(TARGET)
    assert (fit, nfix) == (126, 126)
    counts = arms.train_counts(TARGET)
    assert arms.unpack_beh(key) == tuple(int(x) for x in counts[:, 1])
    assert arms.unpack_beh(key)[2] == fit


def test_mutation_operator_is_the_prototypes():
    """One proposal changes at most one instruction row, all four fields drawn as in reach.search_lineage."""
    parent = TARGET.copy()
    for i in range(200):
        child = arms.mutate(parent, arms.SEED, 7, 3, i)
        diff = np.nonzero((child != parent).any(axis=1))[0]
        assert len(diff) <= 1


def test_geno_hash_cells_respect_the_bucket_count():
    r = arms.run_reach_lineage("X3G", 8, TOY, budget=2000, impl="py", geno_buckets=5)
    assert r["cells"] <= 5


def test_seeded_start_is_reported_as_a_control_not_a_discovery():
    r = arms.run_reach_lineage("X2", 0, TOY, budget=100, impl="py")
    assert r["evals"] == 0 and r["seeded_hit"] is True


@pytest.mark.parametrize("arm", arms.ARMS)
def test_reach_lineage_is_deterministic(arm):
    kw = dict(budget=1500, impl="py", geno_buckets=7)
    a = arms.run_reach_lineage(arm, 3, TOY + 2, **kw)
    b = arms.run_reach_lineage(arm, 3, TOY + 2, **kw)
    assert a["evals"] == b["evals"] and a["cells"] == b["cells"]
    assert np.array_equal(a["final_prog"], b["final_prog"])


# ---------------------------------------------------------------- numba port (exists only if the timing justified it)

@pytest.mark.skipif(not arms.HAVE_NB_PORT, reason="numba port not built")
@pytest.mark.parametrize("arm", arms.ARMS)
@pytest.mark.parametrize("d", [1, 3, 8])
def test_numba_port_matches_reference(arm, d):
    for lineage in range(TOY, TOY + 3):
        kw = dict(budget=2500, geno_buckets=9)
        ref = arms.run_reach_lineage(arm, d, lineage, impl="py", **kw)
        nb = arms.run_reach_lineage(arm, d, lineage, impl="nb", **kw)
        for k in ("evals", "cells", "final_fit", "new_cells_admitted", "accepted", "distinct_genomes",
                  "stones_evaluated", "max_stone_restored", "stones_retained_end", "seeded_hit"):
            assert ref[k] == nb[k], (arm, d, lineage, k, ref[k], nb[k])
        assert np.array_equal(ref["final_prog"], nb["final_prog"])
        assert np.array_equal(ref["hit_prog"], nb["hit_prog"])


@pytest.mark.skipif(not arms.HAVE_NB_PORT, reason="numba port not built")
@pytest.mark.parametrize("arm,buckets", [("X3", None), ("X3G", 3000)])
def test_numba_port_matches_reference_past_the_initial_archive_capacity(arm, buckets):
    """The port's archive starts at 1024 cells and doubles; this case must cross that boundary."""
    kw = dict(budget=26000, geno_buckets=buckets)
    ref = arms.run_reach_lineage(arm, 8, TOY + 5, impl="py", **kw)
    nb = arms.run_reach_lineage(arm, 8, TOY + 5, impl="nb", **kw)
    assert nb["cells"] > 1024
    for k in ("evals", "cells", "final_fit", "new_cells_admitted", "accepted", "distinct_genomes",
              "stones_evaluated", "max_stone_restored", "stones_retained_end"):
        assert ref[k] == nb[k], (k, ref[k], nb[k])
    assert np.array_equal(ref["final_prog"], nb["final_prog"])


def test_path_restored_identifies_shortest_path_genomes():
    start = arms.TARGET.copy()
    start[[1, 4, 6]] = 0
    assert arms._path_restored(start, start, arms.TARGET) == 0
    g = start.copy()
    g[4] = arms.TARGET[4]
    assert arms._path_restored(g, start, arms.TARGET) == 1
    g[0] = [3, 2, 9, 0]                       # an unknocked row changed: off path
    assert arms._path_restored(g, start, arms.TARGET) == -1
    h = start.copy()
    h[1] = [5, 1, 1, 1]                       # a knocked row set to something else: off path
    assert arms._path_restored(h, start, arms.TARGET) == -1
    assert arms._path_restored(arms.TARGET, start, arms.TARGET) == 3


def test_stepping_stone_counts_are_reported_and_consistent():
    r = arms.run_reach_lineage("X3", 3, TOY + 7, budget=3000, impl="py")
    assert r["stones_evaluated"] >= r["stones_retained_end"] >= 0
    assert 0 <= r["max_stone_restored"] <= 2


@pytest.mark.skipif(not arms.HAVE_NB_PORT, reason="numba port not built")
def test_blind_mode_never_reports_a_hit_and_matches_reference():
    """Even the seeded start (d=0, the target itself) is not a hit in blind mode: no outcome is observable."""
    for impl in ("py", "nb"):
        r = arms.run_reach_lineage("X3", 0, TOY, budget=300, impl=impl, blind=True)
        assert r["evals"] == -1 and r["seeded_hit"] is False
    ref = arms.run_reach_lineage("X3", 3, TOY + 3, budget=2000, impl="py", blind=True)
    nb = arms.run_reach_lineage("X3", 3, TOY + 3, budget=2000, impl="nb", blind=True)
    assert ref["cells"] == nb["cells"] and ref["evals"] == nb["evals"] == -1
