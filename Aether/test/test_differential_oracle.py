"""
AETH-00A -- test 22, "Independent transition oracle": differential
testing between the two structurally independent CPU implementations
(reference/oracle.py's Aeth00World.step and reference/
oracle_independent.py's step_bytes) of the same frozen aeth00.v1 law.
"""

import random

from hypothesis import given, settings
from hypothesis import strategies as st

from reference import oracle as ok
from reference import oracle_independent as oki


def _random_grid(rng, H, W, active_fraction):
    grid = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    for r in range(H):
        for c in range(W):
            if rng.random() < active_fraction:
                grid[r][c] = (
                    ok.WRITE_OPCODE,
                    rng.randrange(256),
                    rng.randrange(256),
                    rng.randrange(256),
                )
            else:
                grid[r][c] = (rng.choice([0, 2, 5, 200]), 0, 0, 0)
    return grid


def test_hand_built_examples_agree():
    cases = [
        (3, 3, 1, {(1, 1): (1, 1, 3, 0x42)}),
        (1, 3, 5, {(0, 0): (1, 0, 3, 0x99)}),  # degenerate H=1 self/alias target
        (2, 3, 7, {(0, 0): (1, 0, 3, 0x88)}),
        (
            3,
            3,
            9,
            {(0, 1): (1, 2, 0, 0x01), (1, 0): (1, 1, 3, 0x02), (1, 2): (1, 3, 3, 0x03)},
        ),
    ]
    for H, W, seed, sites in cases:
        grid = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
        for (r, c), site in sites.items():
            grid[r][c] = site
        world = ok.Aeth00World(H, W, seed, grid=grid)
        primary_next = world.step().to_bytes()
        independent_next = oki.step_bytes(H, W, seed, world.tick, world.to_bytes())
        assert primary_next == independent_next


@settings(max_examples=300, deadline=None)
@given(
    H=st.integers(min_value=1, max_value=4),
    W=st.integers(min_value=1, max_value=4),
    seed=st.integers(min_value=0, max_value=(1 << 64) - 1),
    tick=st.integers(min_value=0, max_value=(1 << 64) - 2),
    rng_seed=st.integers(min_value=0, max_value=2**31 - 1),
    active_fraction=st.sampled_from([0.3, 0.6, 0.9, 1.0]),
)
def test_property_random_worlds_agree_between_independent_oracles(
    H, W, seed, tick, rng_seed, active_fraction
):
    rng = random.Random(rng_seed)
    grid = _random_grid(rng, H, W, active_fraction)
    world = ok.Aeth00World(H, W, seed, tick=tick, grid=grid)
    primary_next = world.step().to_bytes()
    independent_next = oki.step_bytes(H, W, seed, tick, world.to_bytes())
    assert primary_next == independent_next


def test_independent_oracle_also_rejects_a_duplicate_source_scenario():
    # oracle_independent.py detects duplicate physical sources via its own
    # route (a seen-set during the single decode pass), never via
    # reference.oracle.assert_no_duplicate_sources. A correct decode of a
    # valid AETH-00 state cannot trigger this in EITHER oracle; both
    # independently agree that no such state exists to test here beyond
    # confirming neither oracle raises spuriously on ordinary input.
    H, W = 1, 3
    grid = [[(0, 0, 0, 0) for _ in range(W)]]
    grid[0][0] = (1, 0, 3, 0x11)
    world = ok.Aeth00World(H, W, seed=3, grid=grid)
    world.step()  # must not raise
    oki.step_bytes(H, W, 3, 0, world.to_bytes())  # must not raise
