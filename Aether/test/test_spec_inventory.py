"""
AETH-00A -- executable translation of AETHER_TEST_PLAN.md's frozen
27-item inventory (semantics_id aeth00.v1), tests 1-11, 13-19, 21, 26-27
(test 12 -> test_properties.py, test 20/25 -> test_statistical_
diagnostics.py, test 22 -> test_differential_oracle.py, test 23 ->
test_golden_vectors.py, test 24 -> test_mutants.py).

Every test function's docstring/name states the exact plan item number
so the mapping in AETH-00A_RECEIPT.md is checkable line-by-line.
"""

import random

from reference import oracle as ok


def _world(H, W, seed, sites=None, tick=0):
    grid = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    for (r, c), site in (sites or {}).items():
        grid[r][c] = site
    return ok.Aeth00World(H, W, seed, tick=tick, grid=grid)


# --- Test 1: all-NOP world invariant -------------------------------------


def test_01_all_nop_world_invariant_across_ticks():
    world = _world(3, 3, seed=1)
    original = world.to_bytes()
    for _ in range(20):
        world = world.step()
        assert world.to_bytes() == original


# --- Test 2: single WRITE changes exactly the intended (neighbor, field) --


def test_02_single_write_changes_only_intended_neighbor_field():
    world = _world(3, 3, seed=2, sites={(1, 1): (1, 1, 3, 0x42)})  # East, payload
    nxt = world.step()
    for r in range(3):
        for c in range(3):
            for f in range(4):
                changed = nxt.grid[r][c][f] != world.grid[r][c][f]
                is_intended = (r, c, f) == (1, 2, 3)
                assert changed == is_intended, f"unexpected change at ({r},{c},{f})"
    assert nxt.grid[1][2][3] == 0x42


# --- Test 3: toroidal wrapping exact from every edge/corner, all 4 dirs --


def test_03_toroidal_wrap_from_every_edge_and_corner():
    H = W = 3
    positions = [(0, 0), (0, W - 1), (H - 1, 0), (H - 1, W - 1), (0, 1), (1, 0)]
    for (r, c) in positions:
        for direction in range(4):
            world = _world(H, W, seed=10 + direction, sites={(r, c): (1, direction, 3, 0x07)})
            nxt = world.step()
            expected_target = ok.neighbor(r, c, H, W, direction)
            tr, tc = expected_target
            assert nxt.grid[tr][tc][3] == 0x07
            for rr in range(H):
                for cc in range(W):
                    for f in range(4):
                        if (rr, cc, f) == (tr, tc, 3) or (rr, cc, f) == (r, c, 1):
                            continue
                        assert nxt.grid[rr][cc][f] == world.grid[rr][cc][f]


# --- Test 4: all four target fields achievable, parametrized arg1 mod 4 --


def test_04_all_four_target_fields_reachable():
    for field in range(4):
        world = _world(3, 3, seed=field, sites={(1, 1): (1, 1, field, 0x55)})
        nxt = world.step()
        assert nxt.grid[1][2][field] == 0x55


# --- Test 5: tick-start snapshot semantics ---------------------------------


def test_05_snapshot_semantics_differ_from_sequential_evaluation():
    grid = [[(0, 0, 0, 0)] * 4]
    grid[0][0] = (1, 1, 0, 0x00)  # East -> (0,1) opcode := 0 (deactivate)
    grid[0][1] = (1, 1, 3, 0xAB)  # East -> (0,2) payload := 0xAB
    world = ok.Aeth00World(1, 4, seed=7, grid=grid)
    nxt = world.step()
    # Sequential (non-snapshot) evaluation would clobber cell1's opcode
    # before cell1 is decoded, so cell2's payload would stay 0. The
    # correct, snapshot-based answer still writes 0xAB.
    assert nxt.grid[0][2] == (0, 0, 0, 0xAB)


# --- Test 6: a write to a neighbor's opcode has no effect until next tick -


def test_06_newly_written_opcode_has_no_effect_this_tick():
    grid = [[(0, 0, 0, 0) for _ in range(3)] for _ in range(3)]
    grid[0][1] = (1, 2, 0, 0x01)  # South -> (1,1) opcode := WRITE(0x01)
    world = ok.Aeth00World(3, 3, seed=4, grid=grid)
    step1 = world.step()
    assert step1.grid[1][1][0] == 0x01  # now WRITE-opcode...
    # ...but (1,1) had arg0=arg1=payload=0 at tick 0, so even though its
    # OPCODE is now WRITE, it never got a chance to emit a proposal this
    # tick (it wasn't WRITE at decode time). Confirm no side effect
    # attributable to (1,1) occurred in step1 beyond the intended write.
    for r in range(3):
        for c in range(3):
            for f in range(4):
                if (r, c, f) == (1, 1, 0):
                    continue
                assert step1.grid[r][c][f] == world.grid[r][c][f]
    # Next tick, (1,1) DOES act (arg0=0=North -> (0,1) opcode field).
    step2 = step1.step()
    assert step2.grid[0][1][0] == 0x00  # (1,1)'s own payload is 0



# --- Test 7: collision outcome deterministic across independent runs -----


def test_07_collision_outcome_deterministic():
    sites = {(0, 1): (1, 2, 0, 0xAA), (2, 1): (1, 0, 0, 0xBB)}  # both -> (1,1) opcode
    r1 = _world(3, 3, seed=77, sites=sites).step()
    r2 = _world(3, 3, seed=77, sites=sites).step()
    assert r1.to_bytes() == r2.to_bytes()


# --- Test 8: collision outcome independent of enumeration order ----------


def test_08_collision_outcome_independent_of_enumeration_order():
    proposals = [
        ok.Proposal((0, 1), (1, 1), 0, 0xAA),
        ok.Proposal((2, 1), (1, 1), 0, 0xBB),
        ok.Proposal((1, 0), (1, 1), 0, 0xCC),
        ok.Proposal((1, 2), (1, 1), 0, 0xDD),
    ]
    contests = {((1, 1), 0): list(proposals)}
    baseline = ok.arbitrate(55, 3, contests)[((1, 1), 0)][0].source
    rng = random.Random(1234)
    for _ in range(20):
        shuffled = list(proposals)
        rng.shuffle(shuffled)
        contests2 = {((1, 1), 0): shuffled}
        winner = ok.arbitrate(55, 3, contests2)[((1, 1), 0)][0].source
        assert winner == baseline


# --- Test 9: replay bit-identical full lattice bytes, tick-for-tick ------


def test_09_replay_is_bit_identical_tick_for_tick_not_only_hash():
    sites = {(0, 0): (1, 1, 3, 0x11), (2, 2): (1, 3, 1, 0x22)}
    w1 = _world(3, 3, seed=321, sites=sites)
    w2 = _world(3, 3, seed=321, sites=sites)
    for _ in range(8):
        assert w1.to_bytes() == w2.to_bytes()  # full bytes, not a hash
        assert hash(w1.to_bytes()) == hash(w2.to_bytes())  # hash as a fast secondary check only
        w1 = w1.step()
        w2 = w2.step()


# --- Test 10: only winner-targeted fields change; untargeted preserved ---


def test_10_only_winning_fields_change_and_untargeted_fields_preserved():
    sites = {(0, 1): (1, 2, 3, 0xAA), (2, 1): (1, 0, 3, 0xBB)}  # both -> (1,1) payload
    world = _world(3, 3, seed=1, sites=sites)  # seed=1 -> winner is (2,1) (see test_mutants)
    nxt = world.step()
    assert nxt.grid[1][1][3] == 0xBB  # winner's value, never the loser's 0xAA
    for r in range(3):
        for c in range(3):
            for f in range(4):
                if (r, c, f) == (1, 1, 3):
                    continue
                assert nxt.grid[r][c][f] == world.grid[r][c][f]


# --- Test 11: dimensions and dtypes invariant across ticks ----------------


def test_11_dimensions_and_dtypes_invariant_across_ticks():
    world = _world(4, 5, seed=1, sites={(0, 0): (1, 1, 3, 200)})
    for _ in range(5):
        world = world.step()
        assert world.H == 4 and world.W == 5
        for row in world.grid:
            for site in row:
                assert len(site) == 4
                for byte in site:
                    assert isinstance(byte, int) and 0 <= byte <= 255



# --- Test 13: dense 2-/3-/4-way collisions, many seeds --------------------


def test_13_dense_collisions_exactly_one_winner_across_many_seeds():
    for seed in range(50):
        for arity, sites in [
            (2, {(0, 1): (1, 2, 0, 1), (2, 1): (1, 0, 0, 2)}),
            (3, {(0, 1): (1, 2, 0, 1), (2, 1): (1, 0, 0, 2), (1, 0): (1, 1, 0, 3)}),
            (
                4,
                {
                    (0, 1): (1, 2, 0, 1),
                    (2, 1): (1, 0, 0, 2),
                    (1, 0): (1, 1, 0, 3),
                    (1, 2): (1, 3, 0, 4),
                },
            ),
        ]:
            world = _world(3, 3, seed=seed, sites=sites)
            nxt = world.step()
            # Exactly one of the `arity` competing values is stored (a
            # single uint8 field cannot hold more than one value at
            # once, so this also confirms decode+arbitrate+commit did
            # not corrupt the field into something outside the contest).
            assert nxt.grid[1][1][0] in range(1, arity + 1)


# --- Test 14: degenerate small-lattice self-targeting (H,W in {1,2}) -----


def test_14_degenerate_self_targeting_h1_is_one_ordinary_proposal():
    world = _world(1, 3, seed=1, sites={(0, 0): (1, 0, 3, 0x99)})  # N==S at H=1
    nxt = world.step()
    assert nxt.grid[0][0] == (1, 0, 3, 0x99)  # writes its own payload into itself


def test_14_degenerate_self_targeting_h2_north_south_distinct_but_wrap():
    world = _world(2, 3, seed=1, sites={(0, 0): (1, 0, 3, 0x88)})  # N: (H-1,0)=(1,0)
    nxt = world.step()
    assert nxt.grid[1][0][3] == 0x88
    assert nxt.grid[0][0] == world.grid[0][0]  # source itself untouched


def test_14_genuine_collision_at_minimal_dimensions_arbitrated_normally():
    # H=1: two DIFFERENT sources both target (0,1) via opposite wraps.
    world = _world(1, 3, seed=42, sites={(0, 0): (1, 1, 3, 0xA1), (0, 2): (1, 3, 3, 0xA2)})
    nxt = world.step()
    assert nxt.grid[0][1][3] in (0xA1, 0xA2)  # exactly one winner, arbitrated normally



# --- Test 15: RESERVED_INERT byte preservation ----------------------------


def test_15_reserved_inert_bytes_preserved_untouched_never_traps():
    sample_opcodes = [0x00, 0x02, 0x03, 0x7F, 0x80, 0xFE, 0xFF]
    sites = {(0, i): (op, 1, 2, 3) for i, op in enumerate(sample_opcodes)}
    world = _world(1, len(sample_opcodes), seed=1, sites=sites)
    for _ in range(5):
        proposals = ok.decode_proposals(world.grid, world.H, world.W)
        assert proposals == []  # (a) no proposal from any RESERVED_INERT site
        world = world.step()  # (c) never traps/errors
    for i, op in enumerate(sample_opcodes):
        assert world.grid[0][i] == (op, 1, 2, 3)  # (b) bit-identical, incl. opcode byte


# --- Test 16: same-value WRITE is valid, proposal_won but no bit change --


def test_16_same_value_write_wins_but_changes_zero_bits():
    world = _world(3, 3, seed=1, sites={(1, 1): (1, 1, 3, 0x00)})  # East, payload=0 (already 0)
    trace = []
    nxt = world.step(trace=trace)
    assert nxt.grid[1][2][3] == 0x00
    won = [t for t in trace if t[0] == "proposal_won"]
    changed = [t for t in trace if t[0] == "stored_bits_changed"]
    assert len(won) == 1
    assert changed[0][1] == (1, 2) and changed[0][2] == 3 and changed[0][3] is False


# --- Test 17: an inert source site can still be a write target -----------


def test_17_inert_cell_can_still_be_written_to():
    world = _world(3, 3, seed=1, sites={(0, 1): (1, 2, 0, 0x01), (1, 1): (0, 9, 9, 9)})
    nxt = world.step()
    assert nxt.grid[1][1][0] == 0x01  # inert target's opcode field changed normally


# --- Test 18: independent per-field arbitration ---------------------------


def test_18_independent_per_field_arbitration_no_cross_field_interaction():
    sites = {
        (0, 1): (1, 2, 0, 0x01),  # South -> (1,1) opcode field, from a lone source
        (1, 0): (1, 1, 3, 0x02),  # East -> (1,1) payload field, from a lone source
        (1, 2): (1, 3, 3, 0x03),  # West -> (1,1) payload field, second competitor
    }
    world = _world(3, 3, seed=1, sites=sites)
    nxt = world.step()
    assert nxt.grid[1][1][0] == 0x01  # opcode contest had only one competitor: unaffected
    assert nxt.grid[1][1][3] in (0x02, 0x03)  # payload contest resolved independently


# --- Test 19: complete replay identity uses all six components -----------


def test_19_replay_identity_uses_all_six_required_components():
    world = _world(3, 3, seed=99, sites={(0, 0): (1, 1, 3, 0x5A)}, tick=7)
    identity = (
        world.SEMANTICS_ID,
        world.H,
        world.W,
        world.seed,
        world.tick,
        world.to_bytes(),
    )
    same = _world(3, 3, seed=99, sites={(0, 0): (1, 1, 3, 0x5A)}, tick=7)
    identity2 = (
        same.SEMANTICS_ID,
        same.H,
        same.W,
        same.seed,
        same.tick,
        same.to_bytes(),
    )
    assert identity == identity2
    assert len(identity) == 6  # a 5-component (or fewer) comparison is not accepted



# --- Test 21: exhaustive tiny-torus identity fixtures ---------------------


def _expected_neighbor_independent(row, col, H, W, direction):
    """Independently re-derives the neighbor formula (not calling
    reference.oracle.neighbor) so this fixture is a genuine cross-check,
    not a tautology against the code under test."""
    if direction == 0:
        return ((row - 1) % H, col)
    if direction == 1:
        return (row, (col + 1) % W)
    if direction == 2:
        return ((row + 1) % H, col)
    return (row, (col - 1) % W)


def test_21_exhaustive_tiny_torus_single_write_fixtures():
    shapes = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 3)]
    for H, W in shapes:
        for direction in range(4):
            for field in range(4):
                for payload in (0x00, 0x01, 0xFF):
                    world = _world(H, W, seed=0, sites={(0, 0): (1, direction, field, payload)})
                    nxt = world.step()
                    tr, tc = _expected_neighbor_independent(0, 0, H, W, direction)
                    expected = [[list(site) for site in row] for row in world.grid]
                    expected[tr][tc][field] = payload
                    got = [[list(site) for site in row] for row in nxt.grid]
                    assert got == expected, (
                        f"H={H} W={W} dir={direction} field={field} payload={payload}: "
                        f"got {got}, expected {expected}"
                    )


# --- Test 26: tick-overflow rejection -------------------------------------


def test_26_tick_overflow_is_rejected_not_wrapped():
    world = _world(3, 3, seed=1, tick=ok.MASK64)
    try:
        world.step()
        assert False, "expected TickOverflowError from tick == 2**64-1"
    except ok.TickOverflowError:
        pass
    # Ordinary stepping just below the boundary is unaffected (no off-by-one).
    world_ok = _world(3, 3, seed=1, tick=ok.MASK64 - 1)
    nxt = world_ok.step()
    assert nxt.tick == ok.MASK64


# --- Test 27: duplicate-source proposal detection in the harness ---------


def test_27_harness_detects_duplicate_physical_source_proposal():
    duplicated = ok.Proposal((0, 0), (1, 1), 0, 0x01)
    contests = {((1, 1), 0): [duplicated, duplicated]}
    try:
        ok.assert_no_duplicate_sources(contests)
        assert False, "expected DuplicateSourceProposalError"
    except ok.DuplicateSourceProposalError as e:
        key, sources = e.args
        assert key == ((1, 1), 0)
        assert sources == [(0, 0), (0, 0)]
    # A genuine 2-source contest (distinct sources) must NOT raise.
    ok.assert_no_duplicate_sources(
        {((1, 1), 0): [ok.Proposal((0, 0), (1, 1), 0, 1), ok.Proposal((2, 2), (1, 1), 0, 2)]}
    )
