"""
AETH-00B -- production-conformance tests (red/green).

These call ONLY the production public API (`production.aeth00`) --
never `reference.oracle` internals -- against expected results already
frozen by AETHER_SPEC.md / AETH-00A's golden vectors. Written BEFORE
`Aether/production/aeth00.py` exists, so the first run of this file
must fail on import (red); it turns green only once the smallest
production implementation satisfying aeth00.v1 exists.

Two of the WINNER_VECTORS fixtures (2-way, 3-way) use sources that are
NOT physical von-Neumann neighbors of their target -- they exist only
to test the raw arbitration math in isolation (as reference/golden_
vectors.py's docstring states), so they are checked here against
`production.aeth00.arbitration_priority` plus an inline max-priority
reduction (this reduction is a one-line application of the frozen
"greatest unsigned priority wins" rule, not a reimplementation of
production's transition logic). The 4-way fixture IS four genuine
physical neighbors of its target, so it is additionally checked at the
full grid/step() level below.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from reference.golden_vectors import PRIORITY_VECTORS, SIGNED_VS_UNSIGNED_VECTOR, WINNER_VECTORS

from production import aeth00 as prod


def _blank_grid(H, W):
    return bytearray(H * W * 4)


def _set_cell(data, W, row, col, opcode, arg0, arg1, payload):
    i = (row * W + col) * 4
    data[i : i + 4] = bytes((opcode, arg0, arg1, payload))


# --- State validation -----------------------------------------------------


def test_state_accepts_minimal_valid_construction():
    s = prod.State(1, 1, bytes(4))
    assert s.H == 1 and s.W == 1 and s.data == bytes(4)


@pytest.mark.parametrize("H,W", [(0, 3), (3, 0), (-1, 3), (3, -1)])
def test_state_rejects_nonpositive_dimensions(H, W):
    with pytest.raises(prod.InvalidStateError):
        prod.State(H, W, bytes(max(H, 0) * max(W, 0) * 4))


def test_state_rejects_wrong_length_buffer():
    with pytest.raises(prod.InvalidStateError):
        prod.State(2, 2, bytes(15))  # needs 16


def test_state_rejects_out_of_range_byte_values():
    with pytest.raises(prod.InvalidStateError):
        prod.State(1, 1, [256, 0, 0, 0])


def test_state_rejects_bare_int_data_instead_of_treating_it_as_a_length():
    # bytes(4) would silently build 4 zero bytes; an int is not a byte
    # sequence and must be rejected, not silently reinterpreted.
    with pytest.raises(prod.InvalidStateError):
        prod.State(1, 1, 4)


def test_state_rejects_non_int_dimensions():
    with pytest.raises(prod.InvalidStateError):
        prod.State(1.0, 1, bytes(4))
    with pytest.raises(prod.InvalidStateError):
        prod.State(True, 1, bytes(4))


# --- seed/tick validation at step() ----------------------------------------


def test_step_rejects_seed_out_of_uint64_range():
    s = prod.State(1, 1, bytes(4))
    with pytest.raises(prod.InvalidStateError):
        prod.step(s, -1, 0)
    with pytest.raises(prod.InvalidStateError):
        prod.step(s, 1 << 64, 0)


def test_step_rejects_tick_out_of_uint64_range():
    s = prod.State(1, 1, bytes(4))
    with pytest.raises(prod.InvalidStateError):
        prod.step(s, 0, -1)
    with pytest.raises(prod.InvalidStateError):
        prod.step(s, 0, 1 << 64)


def test_step_rejects_from_tick_mask64_without_wrapping():
    s = prod.State(1, 1, bytes(4))
    with pytest.raises(prod.TickOverflowError):
        prod.step(s, 0, (1 << 64) - 1)


# --- golden priority vectors (AETHER_TEST_PLAN.md test 23) -----------------


def test_all_priority_vectors_match_production():
    for seed, tick, tr, tc, tf, sr, sc, expected in PRIORITY_VECTORS:
        got = prod.arbitration_priority(seed, tick, tr, tc, tf, sr, sc)
        assert got == expected, f"mismatch: got {got:#018x} expected {expected:#018x}"


def test_signed_vs_unsigned_vector_matches_production_and_picks_unsigned_max():
    v = SIGNED_VS_UNSIGNED_VECTOR
    tr, tc = v["target"]
    prios = {}
    for source in v["sources"]:
        got = prod.arbitration_priority(v["seed"], v["tick"], tr, tc, v["field"], *source)
        assert got == v["priorities"][source]
        prios[source] = got
    assert max(prios, key=lambda s: prios[s]) == v["correct_unsigned_winner"]


def test_winner_vectors_2way_3way_match_production_priority_reduction():
    for seed, tick, target, field, sources_values, exp_source, exp_value in WINNER_VECTORS[0:2]:
        tr, tc = target
        best_source, best_value, best_prio = None, None, -1
        for source, value in sources_values:
            sr, sc = source
            prio = prod.arbitration_priority(seed, tick, tr, tc, field, sr, sc)
            if prio > best_prio:
                best_prio, best_source, best_value = prio, source, value
        assert best_source == exp_source
        assert best_value == exp_value


def test_winner_vector_4way_matches_production_step():
    # WINNER_VECTORS[2]: target (5,5) field 3, all four von Neumann
    # neighbors of (5,5) contest it. H=W=11 keeps (5,5) far from any
    # toroidal wrap so each source is an unambiguous physical neighbor.
    seed, tick, target, field, sources_values, exp_source, exp_value = WINNER_VECTORS[2]
    tr, tc = target
    H = W = 11
    data = _blank_grid(H, W)
    # direction each source must encode to hit (5,5): north-of-target
    # source moves SOUTH, south-of-target moves NORTH, east moves WEST,
    # west moves EAST (AETHER_SPEC.md "Direction encoding").
    dir_for_source = {
        (tr - 1, tc): prod.SOUTH,
        (tr + 1, tc): prod.NORTH,
        (tr, tc + 1): prod.WEST,
        (tr, tc - 1): prod.EAST,
    }
    for source, value in sources_values:
        direction = dir_for_source[source]
        _set_cell(data, W, source[0], source[1], prod.WRITE_OPCODE, direction, field, value)
    state = prod.State(H, W, bytes(data))
    nxt = prod.step(state, seed, tick)
    assert nxt.cell(tr, tc)[field] == exp_value


# --- trace semantics (AETHER_SPEC.md "Instrumentation") --------------------


def _contested_state():
    # (5,5) field 3 contested by two of its four physical neighbors; a
    # third neighbor is RESERVED_INERT (emits no proposal); the same
    # cell that wins also gets a same-value write on another field
    # elsewhere to exercise stored_bits_changed=False.
    H = W = 11
    data = _blank_grid(H, W)
    _set_cell(data, W, 4, 5, prod.WRITE_OPCODE, prod.SOUTH, 3, 0xAA)  # -> (5,5) f3
    _set_cell(data, W, 6, 5, prod.WRITE_OPCODE, prod.NORTH, 3, 0xBB)  # -> (5,5) f3
    _set_cell(data, W, 5, 6, 0x02, 0, 0, 0)  # RESERVED_INERT, no proposal
    _set_cell(data, W, 0, 0, prod.WRITE_OPCODE, prod.EAST, prod.PAYLOAD, 0x00)  # same-value win
    return prod.State(H, W, bytes(data))


def test_trace_contains_all_three_required_event_types():
    state = _contested_state()
    trace = []
    prod.step(state, seed=1, tick=1, trace=trace)
    kinds = {ev[0] for ev in trace}
    assert {"proposal_emitted", "proposal_won", "stored_bits_changed"} <= kinds


def test_trace_reports_same_value_write_as_won_but_unchanged():
    state = _contested_state()
    trace = []
    prod.step(state, seed=1, tick=1, trace=trace)
    changed_flags = [ev[3] for ev in trace if ev[0] == "stored_bits_changed" and ev[1] == (0, 1)]
    assert changed_flags and changed_flags[0] is False


def test_trace_enabled_and_disabled_produce_identical_next_state():
    state = _contested_state()
    trace = []
    with_trace = prod.step(state, seed=1, tick=1, trace=trace)
    without_trace = prod.step(state, seed=1, tick=1, trace=None)
    assert with_trace.data == without_trace.data
    assert trace  # trace was actually populated in the traced run


_cell_strategy = st.one_of(
    st.tuples(st.just(prod.WRITE_OPCODE), st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
    st.tuples(
        st.integers(0, 255).filter(lambda o: o != prod.WRITE_OPCODE),
        st.integers(0, 3),
        st.integers(0, 3),
        st.integers(0, 3),
    ),
)


@st.composite
def _small_worlds(draw):
    H = draw(st.integers(min_value=1, max_value=5))
    W = draw(st.integers(min_value=1, max_value=5))
    seed = draw(st.integers(min_value=0, max_value=(1 << 64) - 1))
    tick = draw(st.integers(min_value=0, max_value=(1 << 64) - 2))
    grid = draw(st.lists(st.lists(_cell_strategy, min_size=W, max_size=W), min_size=H, max_size=H))
    data = bytearray(H * W * 4)
    idx = 0
    for row in grid:
        for cell in row:
            data[idx : idx + 4] = bytes(cell)
            idx += 4
    return H, W, seed, tick, bytes(data)


@settings(max_examples=3000, deadline=None)
@given(world=_small_worlds())
def test_property_trace_never_changes_next_state(world):
    H, W, seed, tick, data = world
    state = prod.State(H, W, data)
    trace = []
    with_trace = prod.step(state, seed, tick, trace=trace)
    without_trace = prod.step(state, seed, tick, trace=None)
    assert with_trace.data == without_trace.data
