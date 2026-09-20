"""
AETH-00A -- deliberately broken transition implementations ("mutants",
reference/mutants.py) and proof that the suite rejects each of them
(AETHER_TEST_PLAN.md test 24: "construct at least one deliberately WRONG
... implementation and assert the test suite FAILS it"). Covers all 9
bug shapes named in the AETH-00A instructions. None of these mutants is
a production implementation.
"""

from reference import mutants as mut
from reference import oracle as ok


def _world(H, W, seed, cells):
    grid = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    for (r, c), cell in cells.items():
        grid[r][c] = cell
    return ok.Aeth00World(H, W, seed, grid=grid)


def test_mutant_min_priority_picks_wrong_winner():
    # Both proposals target (1,1) opcode via South/North -- a genuine collision.
    world = _world(
        3,
        3,
        seed=111,
        cells={(0, 1): (1, 2, 0, 0x10), (2, 1): (1, 0, 0, 0x20)},  # both -> (1,1) opcode
    )
    proposals = ok.decode_proposals(world.grid, world.H, world.W)
    contests = ok.group_contests(proposals)
    correct = ok.arbitrate(world.seed, world.tick, contests)[((1, 1), 0)][0]
    buggy = mut.mutant_min_priority_arbitrate(world.seed, world.tick, contests)[((1, 1), 0)][0]
    assert buggy.source != correct.source


def test_mutant_in_place_update_violates_snapshot_semantics():
    grid = [[(0, 0, 0, 0)] * 4]
    grid[0][0] = (1, 1, 0, 0x00)  # WRITE East -> (0,1) opcode := 0
    grid[0][1] = (1, 1, 3, 0xAB)  # WRITE East -> (0,2) payload := 0xAB
    world = ok.Aeth00World(1, 4, seed=7, grid=grid)
    correct = world.step()
    buggy = mut.mutant_in_place_sequential_step(world)
    # Correct: cell1's WRITE is decoded from the S[t] snapshot regardless
    # of cell0's concurrent write, so cell2's payload becomes 0xAB.
    assert correct.grid[0][2] == (0, 0, 0, 0xAB)
    # Buggy: cell1 is clobbered in-place before it is decoded, so its
    # write never happens.
    assert buggy[0][2] != correct.grid[0][2]
    assert buggy[0][2] == (0, 0, 0, 0)


def test_mutant_duplicate_source_aliasing_is_detected_by_harness():
    world = _world(1, 3, seed=3, cells={(0, 0): (1, 0, 0, 0x11)})  # N==S at H=1
    contests = mut.mutant_duplicate_source_proposals(world)
    try:
        ok.assert_no_duplicate_sources(contests)
        assert False, "harness failed to detect the duplicate-source mutant"
    except ok.DuplicateSourceProposalError as e:
        sources = e.args[1]
        assert len(sources) == 2
        assert sources[0] == sources[1] == (0, 0)


def test_mutant_signed_priority_picks_wrong_winner():
    from reference.golden_vectors import SIGNED_VS_UNSIGNED_VECTOR as v

    tr, tc = v["target"]
    proposals = [ok.Proposal(s, (tr, tc), v["field"], 0xFF) for s in v["sources"]]
    contests = ok.group_contests(proposals)
    correct = ok.arbitrate(v["seed"], v["tick"], contests)[((tr, tc), v["field"])][0]
    buggy = mut.mutant_signed_priority_arbitrate(v["seed"], v["tick"], contests)
    buggy_winner = buggy[((tr, tc), v["field"])][0]
    assert correct.source == v["correct_unsigned_winner"]
    assert buggy_winner.source == v["buggy_signed_winner"]
    assert buggy_winner.source != correct.source


def test_mutant_stale_next_state_reverts_untouched_field():
    grid = [[(0, 0, 0, 0) for _ in range(3)] for _ in range(3)]
    grid[0][0] = (1, 1, 3, 0x99)  # East -> (0,1) payload
    grid[2][2] = (1, 3, 1, 0x55)  # West -> (2,1) arg0
    grid[1][2] = (1, 2, 0, 0x00)  # South -> (2,2) opcode := 0 (self-deactivates)
    world0 = ok.Aeth00World(3, 3, seed=1, grid=grid)
    world1 = world0.step()
    world2 = world1.step()

    stale = mut.MutantStaleNextState()
    stale.step(world0)  # first call: no divergence yet (base == world0.grid)
    m2 = stale.step(world1)  # second call: commits onto STALE world0.grid

    # Correct: (2,1)'s arg0, set at tick0 and untouched at tick1, persists.
    assert world2.grid[2][1] == (0, 0x55, 0, 0)
    # Buggy: reverts to the pre-tick0 value because it committed onto the
    # cached (one-tick-stale) base instead of world1.grid.
    assert m2[2][1] == (0, 0, 0, 0)
    assert m2[2][1] != world2.grid[2][1]


def test_mutant_wrong_direction_encoding_targets_wrong_cell():
    world = _world(3, 3, seed=5, cells={(1, 1): (1, 1, 3, 0x77)})  # East -> (1,2) payload
    correct = world.step()
    buggy = mut.mutant_wrong_direction_step(world)
    assert correct.grid[1][2] == (0, 0, 0, 0x77)
    assert buggy[1][2] == (0, 0, 0, 0)  # East mis-mapped to South in the mutant
    assert buggy[2][1] == (0, 0, 0, 0x77)  # written to the wrong cell instead


def test_mutant_global_arbitration_drops_a_genuinely_independent_field():
    world = _world(
        3,
        3,
        seed=9,
        cells={
            (0, 1): (1, 2, 0, 0x01),  # South -> (1,1) opcode field
            (1, 0): (1, 1, 3, 0x02),  # East -> (1,1) payload field
        },
    )
    correct = world.step()
    buggy = mut.mutant_global_arbitration_step(world)
    # Correct: independent per-field arbitration -- BOTH fields change.
    assert correct.grid[1][1] == (1, 0, 0, 2)
    # Buggy: only the single globally-highest-priority proposal's field
    # is written; the other genuinely-targeted field is silently dropped.
    assert buggy[1][1] != correct.grid[1][1]


def test_mutant_priority_payload_swap_writes_wrong_value():
    world = _world(
        3,
        3,
        seed=1,
        cells={(0, 0): (1, 2, 3, 0xAA), (2, 0): (1, 0, 3, 0xBB)},  # both -> (1,0) payload
    )
    correct = world.step()
    buggy = mut.mutant_priority_payload_swap_step(world)
    assert correct.grid[1][0] == (0, 0, 0, 0xBB)  # true arbitration winner's value
    assert buggy[1][0] == (0, 0, 0, 0xAA)  # BUG: first-enumerated proposal's value
    assert buggy[1][0] != correct.grid[1][0]


def test_mutant_missing_uint64_wrap_diverges_from_frozen_vector():
    from reference.golden_vectors import PRIORITY_VECTORS

    seed, tick, tr, tc, tf, sr, sc, expected = PRIORITY_VECTORS[0]
    buggy = mut.mutant_priority_missing_wrap(seed, tick, tr, tc, tf, sr, sc)
    assert buggy != expected
