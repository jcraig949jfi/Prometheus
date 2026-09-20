"""
AETH-00A -- test 12, property-based tests over randomized small worlds
(Hypothesis). Premise stated explicitly per AETHER_TEST_PLAN.md test 12:
"small" here means H, W in [1, 5] -- a practical test-runtime choice;
the arbitration law itself has no coordinate-range restriction narrower
than the frozen dimension domain (1 <= H,W <= 2**32-1), which is
exercised separately by the golden vectors (boundary/near-max
coordinates) and test 21 (exhaustive tiny-torus fixtures), not by this
randomized suite.

Generators are deliberately biased toward ACTIVE and CONTESTED worlds
(mostly WRITE opcode, many proposals aimed at the same targets) rather
than uniform-random bytes, because only opcode 0x01 out of 256 possible
byte values is active; uniform-random generation would produce almost
all-inert worlds and rarely exercise arbitration at all.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from reference import oracle as ok

MAX_DIM = 5  # explicit, stated bound for "small" worlds in this file.

_cell_strategy = st.one_of(
    # Mostly WRITE (opcode=1), all four fields free -- direction/field mod
    # 4 collapses the byte space, and a small W/H forces many contests.
    st.tuples(
        st.just(ok.WRITE_OPCODE),
        st.integers(0, 255),
        st.integers(0, 255),
        st.integers(0, 255),
    ),
    # Occasionally a non-WRITE (RESERVED_INERT) cell, incl. same-value bytes.
    st.tuples(
        st.integers(0, 255).filter(lambda o: o != ok.WRITE_OPCODE),
        st.integers(0, 3),
        st.integers(0, 3),
        st.integers(0, 3),
    ),
)


@st.composite
def worlds(draw, max_dim=MAX_DIM, max_steps_ahead=1):
    """`max_steps_ahead` bounds how many chained .step() calls a test
    using this world intends to make, so `tick` is generated far enough
    below the tick-overflow boundary (test_26) that none of those
    chained steps spuriously hits it; the overflow boundary ITSELF is
    exercised deliberately, not incidentally, by test_spec_inventory.py
    test_26."""
    H = draw(st.integers(min_value=1, max_value=max_dim))
    W = draw(st.integers(min_value=1, max_value=max_dim))
    seed = draw(st.integers(min_value=0, max_value=(1 << 64) - 1))
    tick = draw(st.integers(min_value=0, max_value=(1 << 64) - 1 - max_steps_ahead))
    grid = draw(
        st.lists(
            st.lists(_cell_strategy, min_size=W, max_size=W),
            min_size=H,
            max_size=H,
        )
    )
    return ok.Aeth00World(H, W, seed, tick=tick, grid=grid)


def _distinct_byte_values(world):
    return {b for row in world.grid for cell in row for b in cell}


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_only_winner_targeted_fields_may_differ(world):
    proposals = ok.decode_proposals(world.grid, world.H, world.W)
    contests = ok.group_contests(proposals)
    ok.assert_no_duplicate_sources(contests)  # (test 27, generically re-checked here)
    winners = ok.arbitrate(world.seed, world.tick, contests)
    nxt = world.step()
    winner_targets = set(winners.keys())
    for r in range(world.H):
        for c in range(world.W):
            for f in range(4):
                changed = nxt.grid[r][c][f] != world.grid[r][c][f]
                if changed:
                    assert ((r, c), f) in winner_targets


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_every_stored_byte_existed_in_a_permitted_path(world):
    before = _distinct_byte_values(world)
    nxt = world.step()
    after = _distinct_byte_values(nxt)
    assert after <= before  # AETHER_SPEC.md "Known limitation -- no byte synthesis"


@settings(max_examples=300, deadline=None)
@given(world=worlds(max_steps_ahead=4))
def test_property_byte_alphabet_cannot_grow_over_multiple_ticks(world):
    seen = _distinct_byte_values(world)
    w = world
    for _ in range(4):
        w = w.step()
        now = _distinct_byte_values(w)
        assert now <= seen
        seen = now


@settings(max_examples=300, deadline=None)
@given(world=worlds())
def test_property_proposal_enumeration_order_cannot_alter_result(world):
    import random

    proposals = ok.decode_proposals(world.grid, world.H, world.W)
    contests = ok.group_contests(proposals)
    baseline = {k: v[0].source for k, v in ok.arbitrate(world.seed, world.tick, contests).items()}
    rng = random.Random(0)
    for _ in range(5):
        shuffled = {k: list(v) for k, v in contests.items()}
        for plist in shuffled.values():
            rng.shuffle(plist)
        again = {k: v[0].source for k, v in ok.arbitrate(world.seed, world.tick, shuffled).items()}
        assert again == baseline


@settings(max_examples=200, deadline=None)
@given(world=worlds())
def test_property_replay_complete_identical_input_gives_identical_output(world):
    clone = ok.Aeth00World(world.H, world.W, world.seed, tick=world.tick, grid=world.grid)
    assert world.step().to_bytes() == clone.step().to_bytes()
