"""
AETH-00B -- differential qualification: production vs. BOTH AETH-00A
independent oracles (reference.oracle "scatter" pipeline and
reference.oracle_independent "gather-agnostic" flat-byte oracle).
Production itself is a THIRD, independently-shaped "gather" algorithm
(see production/aeth00.py's independence statement) -- three
differently-structured implementations of the same frozen law.

Hand fixtures cover the required explicit categories (dims 1/2/3/
ordinary, dense contests, RESERVED_INERT-heavy, same-value writes,
multi-field contests, high-bit seed/tick). The property-based test
adds >=100,000 randomized, WRITE/contest-biased cases (an engineering
stress target, not a five-nines scientific claim -- AETH-00B
instructions).
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from reference import oracle as ok
from reference import oracle_independent as oi
from production import aeth00 as prod

MASK64 = (1 << 64) - 1
MAX_DIM = 5


def _grid_to_bytes(grid, H, W):
    out = bytearray(H * W * 4)
    idx = 0
    for r in range(H):
        for c in range(W):
            out[idx : idx + 4] = bytes(grid[r][c])
            idx += 4
    return bytes(out)


def _assert_all_agree(H, W, seed, tick, grid):
    data = _grid_to_bytes(grid, H, W)
    prod_next = prod.step(prod.State(H, W, data), seed, tick).data
    primary_next = ok.Aeth00World(H, W, seed, tick=tick, grid=grid).step().to_bytes()
    indep_next = oi.step_bytes(H, W, seed, tick, data)
    assert prod_next == primary_next == indep_next


# --- explicit hand fixtures -------------------------------------------------


def test_dim_1x1_self_targeting():
    grid = [[(prod.WRITE_OPCODE, 0, 0, 0x42)]]  # North of (0,0) in H=1 is itself
    _assert_all_agree(1, 1, seed=7, tick=0, grid=grid)


def test_dim_2x2_all_four_directions_alias_pairwise():
    grid = [
        [(prod.WRITE_OPCODE, 0, 3, 0x01), (prod.WRITE_OPCODE, 1, 2, 0x02)],
        [(prod.WRITE_OPCODE, 2, 1, 0x03), (prod.WRITE_OPCODE, 3, 0, 0x04)],
    ]
    _assert_all_agree(2, 2, seed=99, tick=1, grid=grid)


def test_dim_3x3_ordinary_no_aliasing():
    grid = [[(prod.WRITE_OPCODE, (r + c) % 4, (r * c) % 4, (r * 3 + c)) for c in range(3)] for r in range(3)]
    _assert_all_agree(3, 3, seed=555, tick=2, grid=grid)


def test_dim_ordinary_7x9_mixed_reserved_and_write():
    H, W = 7, 9
    grid = [
        [
            (prod.WRITE_OPCODE, (r + 2 * c) % 4, (r * c + 1) % 4, (r * W + c) % 256)
            if (r + c) % 3 == 0
            else (((r * W + c) % 255) + 1, r % 4, c % 4, (r + c) % 256)  # RESERVED_INERT
            for c in range(W)
        ]
        for r in range(H)
    ]
    _assert_all_agree(H, W, seed=0xABCDEF, tick=12345, grid=grid)


def test_dense_4way_collisions_every_cell_same_field():
    # Every cell WRITEs its payload into its own field-0 (opcode) of the
    # neighbor found by (row+col) mod 4 -- forces many genuine multi-way
    # contests concentrated on field 0 across a small torus.
    H, W = 4, 4
    grid = [[(prod.WRITE_OPCODE, (r + c) % 4, 0, (r * W + c) % 256) for c in range(W)] for r in range(H)]
    _assert_all_agree(H, W, seed=31337, tick=8, grid=grid)


def test_reserved_inert_heavy_sparse_writes():
    H, W = 6, 6
    grid = [[(2 + ((r * W + c) % 253), r, c, r ^ c) for c in range(W)] for r in range(H)]  # all RESERVED_INERT
    grid[0][0] = (prod.WRITE_OPCODE, 1, 3, 0x99)
    grid[5][5] = (prod.WRITE_OPCODE, 2, 1, 0x11)
    _assert_all_agree(H, W, seed=42, tick=100, grid=grid)


def test_same_value_writes_change_zero_bits_but_still_win():
    grid = [
        [(prod.WRITE_OPCODE, SOUTH := 2, 3, 0x77), (prod.WRITE_OPCODE, 1, 3, 0x00)],
        [(0x00, 0, 0, 0x77), (prod.WRITE_OPCODE, 0, 3, 0x00)],
    ]
    _assert_all_agree(2, 2, seed=8, tick=3, grid=grid)


def test_multi_field_target_contests_independent():
    # (1,1) is contested on all 4 fields simultaneously by its 4 neighbors.
    H, W = 3, 3
    grid = [[(0x00, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    grid[0][1] = (prod.WRITE_OPCODE, 2, 0, 0xA0)  # -> south = (1,1), field 0
    grid[1][2] = (prod.WRITE_OPCODE, 3, 1, 0xA1)  # -> west = (1,1), field 1
    grid[2][1] = (prod.WRITE_OPCODE, 0, 2, 0xA2)  # -> north = (1,1), field 2
    grid[1][0] = (prod.WRITE_OPCODE, 1, 3, 0xA3)  # -> east = (1,1), field 3
    _assert_all_agree(H, W, seed=2024, tick=1, grid=grid)


def test_high_bit_seed_and_max_valid_tick():
    grid = [[(prod.WRITE_OPCODE, r, c, (r + c) % 256) for c in range(3)] for r in range(3)]
    _assert_all_agree(3, 3, seed=MASK64, tick=MASK64 - 1, grid=grid)
    _assert_all_agree(3, 3, seed=1 << 63, tick=1 << 63, grid=grid)


# --- large-volume randomized differential property --------------------------

_cell_strategy = st.one_of(
    st.tuples(st.just(prod.WRITE_OPCODE), st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
    st.tuples(st.integers(0, 255).filter(lambda o: o != prod.WRITE_OPCODE), st.integers(0, 3), st.integers(0, 3), st.integers(0, 3)),
)


@st.composite
def _worlds(draw):
    H = draw(st.integers(min_value=1, max_value=MAX_DIM))
    W = draw(st.integers(min_value=1, max_value=MAX_DIM))
    seed = draw(st.integers(min_value=0, max_value=MASK64))
    tick = draw(st.integers(min_value=0, max_value=MASK64 - 1))
    grid = draw(st.lists(st.lists(_cell_strategy, min_size=W, max_size=W), min_size=H, max_size=H))
    return H, W, seed, tick, grid


@settings(max_examples=100_000, deadline=None)
@given(world=_worlds())
def test_property_production_agrees_with_both_oracles_on_random_worlds(world):
    H, W, seed, tick, grid = world
    _assert_all_agree(H, W, seed, tick, grid)
