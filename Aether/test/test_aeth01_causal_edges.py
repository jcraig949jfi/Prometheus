"""The causal-edge side-channel must report the TRUE winning source.

AETH-02 Track 2 needs `source -> target` edges. The operator's locked
design principle is to instrument at the point the kernel already knows
the winning source rather than inferring causality afterwards from state
differences, because differencing is ambiguous whenever two candidate
sources could have produced the same target value.

This file is what makes that claim checkable, and it has two halves.

HALF ONE -- OBSERVING MUST NOT CHANGE THE WORLD. With the observer on
and off, the five output fields and `counters` must be byte-identical.
If that fails, the observatory is inside the universe and every AETH-02
number would describe a different world than the one being claimed.

HALF TWO -- THE REPORTED EDGE MUST BE THE REAL ONE. The CPU oracle
records `("proposal_won", source, target, field, value)` from a wholly
independent implementation that does not import the kernel. The GPU
side-channel's edge set must equal the oracle's exactly -- same sources,
same targets, same fields. Agreement between the kernel and itself would
prove nothing; this compares two implementations of the same law.

The contender count is checked the same way, against the oracle's
`proposal_emitted` events, because "how many lost" is the arbitration
outcome the directive asks for and is what makes destroyed transfer
amounts observable.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from reference import oracle_aeth01 as ok1
from reference.gpu_aeth01 import gpu_step, _NEIGHBOR_SLOTS

NO_WINNER = 255


def _arrays(grid):
    arr = np.array(grid, dtype=np.uint8)
    return [arr[:, :, f] for f in range(5)]


def _run(world, observe):
    observer = [] if observe else None
    out = gpu_step(world.H, world.W, world.seed, world.tick, world.write_cost,
                   world.maintenance_cost, world.replenish_numer,
                   world.replenish_amount, world.mut_numer,
                   *_arrays(world.grid), observer=observer)
    return out, observer


def _gpu_edges(observer, H, W):
    """(source, target, field) set implied by the side-channel."""
    edges = set()
    for field, (winner_slot, _contenders) in enumerate(observer):
        rows, cols = np.nonzero(winner_slot != NO_WINNER)
        for r, c in zip(rows.tolist(), cols.tolist()):
            dr, dc, _required = _NEIGHBOR_SLOTS[int(winner_slot[r, c])]
            edges.add((((r + dr) % H, (c + dc) % W), (r, c), field))
    return edges


def _gpu_contenders(observer):
    out = {}
    for field, (_winner_slot, contenders) in enumerate(observer):
        rows, cols = np.nonzero(contenders)
        for r, c in zip(rows.tolist(), cols.tolist()):
            out[((r, c), field)] = int(contenders[r, c])
    return out


def _oracle(world):
    trace = []
    world.step(trace=trace)
    won = {(e[1], e[2], e[3]) for e in trace if e[0] == "proposal_won"}
    emitted = {}
    for e in trace:
        if e[0] == "proposal_emitted":
            emitted[(e[2], e[3])] = emitted.get((e[2], e[3]), 0) + 1
    return won, emitted


def _world(H, W, seed, grid, **kw):
    return ok1.Aeth01World(H, W, seed, kw.get("write_cost", 1),
                           kw.get("maintenance_cost", 0),
                           kw.get("replenish_numer", 0),
                           kw.get("replenish_amount", 0),
                           kw.get("mut_numer", 0),
                           tick=kw.get("tick", 0), grid=grid)


def _dense_grid(H, W, rng):
    """Writers at high density, so contests actually happen."""
    grid = []
    for _ in range(H):
        row = []
        for _ in range(W):
            write = rng.random() < 0.7
            row.append((ok1.WRITE_OPCODE if write else int(rng.integers(2, 256)),
                        int(rng.integers(0, 256)), int(rng.integers(0, 256)),
                        int(rng.integers(0, 256)), int(rng.integers(0, 256))))
        grid.append(row)
    return grid


# ------------------------------------------- HALF ONE: no back-reaction

@pytest.mark.parametrize("dims", [(1, 1), (1, 3), (3, 1), (2, 2), (4, 4), (5, 3)])
def test_observing_does_not_change_the_world(dims):
    H, W = dims
    rng = np.random.default_rng(0xE1)
    world = _world(H, W, 0xC0FFEE, _dense_grid(H, W, rng),
                   write_cost=2, maintenance_cost=1, replenish_numer=1 << 30,
                   replenish_amount=7, mut_numer=1 << 30, tick=11)
    quiet, _ = _run(world, observe=False)
    watched, observer = _run(world, observe=True)
    for field in range(5):
        assert np.array_equal(quiet[field], watched[field]), (
            "field %d differs with the observer attached: the observatory is "
            "inside the universe" % field)
    assert quiet[5] == watched[5], "counters differ with the observer attached"
    assert observer is not None and len(observer) == 5


@settings(max_examples=60, deadline=None)
@given(st.integers(1, 4), st.integers(1, 4), st.integers(0, 2 ** 64 - 1),
       st.integers(0, 255), st.integers(0, 255), st.integers(0, 2 ** 32),
       st.integers(0, 2 ** 32), st.integers(0, 10 ** 4))
def test_no_back_reaction_over_the_parameter_domain(H, W, seed, write_cost,
                                                    maintenance_cost,
                                                    replenish_numer,
                                                    mut_numer, tick):
    rng = np.random.default_rng(seed % (2 ** 32))
    world = _world(H, W, seed, _dense_grid(H, W, rng), write_cost=write_cost,
                   maintenance_cost=maintenance_cost,
                   replenish_numer=replenish_numer, replenish_amount=9,
                   mut_numer=mut_numer, tick=tick)
    quiet, _ = _run(world, observe=False)
    watched, _ = _run(world, observe=True)
    for field in range(5):
        assert np.array_equal(quiet[field], watched[field])
    assert quiet[5] == watched[5]


# ------------------------------- HALF TWO: the edge is the oracle's edge

@pytest.mark.parametrize("dims", [(1, 2), (2, 2), (3, 3), (4, 4), (3, 5), (5, 4)])
def test_edge_set_equals_the_independent_cpu_oracle_trace(dims):
    H, W = dims
    rng = np.random.default_rng(0x5EED)
    world = _world(H, W, 0xABCDEF, _dense_grid(H, W, rng),
                   write_cost=1, maintenance_cost=0, mut_numer=1 << 31, tick=3)
    _out, observer = _run(world, observe=True)
    gpu = _gpu_edges(observer, H, W)
    won, _emitted = _oracle(world)
    assert gpu == won, (
        "side-channel edge set disagrees with the oracle trace\n"
        "  only in side-channel: %s\n  only in oracle: %s"
        % (sorted(gpu - won)[:6], sorted(won - gpu)[:6]))


@settings(max_examples=120, deadline=None)
@given(st.integers(1, 4), st.integers(1, 4), st.integers(0, 2 ** 64 - 1),
       st.integers(0, 6), st.integers(0, 3), st.integers(0, 2 ** 32),
       st.integers(0, 10 ** 4))
def test_edge_set_matches_the_oracle_over_randomized_worlds(H, W, seed,
                                                            write_cost,
                                                            maintenance_cost,
                                                            mut_numer, tick):
    rng = np.random.default_rng(seed % (2 ** 32))
    world = _world(H, W, seed, _dense_grid(H, W, rng), write_cost=write_cost,
                   maintenance_cost=maintenance_cost, replenish_numer=1 << 29,
                   replenish_amount=5, mut_numer=mut_numer, tick=tick)
    _out, observer = _run(world, observe=True)
    won, _emitted = _oracle(world)
    assert _gpu_edges(observer, H, W) == won


@pytest.mark.parametrize("dims", [(2, 2), (3, 3), (4, 4), (4, 5)])
def test_contender_counts_match_the_oracle(dims):
    H, W = dims
    rng = np.random.default_rng(0xC0DE)
    world = _world(H, W, 0x1234, _dense_grid(H, W, rng), write_cost=1, tick=7)
    _out, observer = _run(world, observe=True)
    _won, emitted = _oracle(world)
    assert _gpu_contenders(observer) == emitted, (
        "contender counts disagree with the oracle's proposal_emitted events")


def test_a_world_with_no_writers_reports_no_edges_at_all():
    H = W = 4
    grid = [[(9, 1, 1, 5, 200) for _ in range(W)] for _ in range(H)]
    world = _world(H, W, 42, grid, write_cost=1)
    _out, observer = _run(world, observe=True)
    assert _gpu_edges(observer, H, W) == set()
    for winner_slot, contenders in observer:
        assert np.all(winner_slot == NO_WINNER)
        assert not np.any(contenders)


def test_every_reported_source_actually_qualified_as_a_writer():
    # An edge is only legal if its source was a non-starved WRITE site
    # aimed at that direction and that field. Checked against the input
    # lattice directly, independently of both the oracle and the kernel.
    H = W = 5
    rng = np.random.default_rng(7)
    world = _world(H, W, 0xFEED, _dense_grid(H, W, rng), write_cost=3, tick=2)
    opcode, arg0, arg1, _payload, energy = _arrays(world.grid)
    _out, observer = _run(world, observe=True)
    checked = 0
    for field, (winner_slot, _c) in enumerate(observer):
        rows, cols = np.nonzero(winner_slot != NO_WINNER)
        for r, c in zip(rows.tolist(), cols.tolist()):
            dr, dc, required = _NEIGHBOR_SLOTS[int(winner_slot[r, c])]
            sr, sc = (r + dr) % H, (c + dc) % W
            assert opcode[sr, sc] == ok1.WRITE_OPCODE
            assert int(energy[sr, sc]) >= world.write_cost
            assert int(arg0[sr, sc]) % 4 == required
            assert int(arg1[sr, sc]) % 5 == field
            checked += 1
    assert checked > 0, "fixture produced no edges; it is not testing anything"


# ----------------------------------------------------------- cheat control

def test_the_edge_comparison_can_actually_fail():
    # Without this, "edge sets match" is indistinguishable from "the
    # comparison is vacuous". Corrupt one recorded winner and require
    # the oracle comparison to notice.
    H = W = 4
    rng = np.random.default_rng(11)
    world = _world(H, W, 0x99, _dense_grid(H, W, rng), write_cost=1, tick=1)
    _out, observer = _run(world, observe=True)
    won, _emitted = _oracle(world)
    assert _gpu_edges(observer, H, W) == won, "fixture must start clean"

    for field, (winner_slot, _c) in enumerate(observer):
        rows, cols = np.nonzero(winner_slot != NO_WINNER)
        if rows.size:
            r, c = int(rows[0]), int(cols[0])
            original = int(winner_slot[r, c])
            winner_slot[r, c] = (original + 1) % 4
            assert _gpu_edges(observer, H, W) != won, (
                "corrupting a winning slot did not change the edge set, so "
                "the comparison is not measuring what it claims")
            return
    pytest.fail("fixture produced no edges to corrupt")
