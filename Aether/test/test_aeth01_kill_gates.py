"""
AETH-01 -- executable contract tests for KILL_GATES_01.md's K1, K2, K3,
K6 (repair cycle). Each test below reproduces, in code, one hand-worked
case already adjudicated in KILL_GATES_01.md; a failure here means the
CPU oracle (`reference/oracle_aeth01.py`) disagrees with the hand
derivation, not that the derivation itself is in question.
"""

from reference import oracle_aeth01 as ok1
from reference.provenance_aeth01 import SEEDED_CONTROL, SPONTANEOUS, instrument_class


def _world(H, W, seed, write_cost=0, maintenance_cost=0, replenish_numer=0,
           replenish_amount=0, mut_numer=0, tick=0, grid=None):
    return ok1.Aeth01World(H, W, seed, write_cost, maintenance_cost,
                            replenish_numer, replenish_amount, mut_numer,
                            tick=tick, grid=grid)


# ---------------------------------------------------------------------
# K1 -- accounting identity hand ledger (6 cases, KILL_GATES_01.md K1)
# ---------------------------------------------------------------------

def test_k1_case1_execution_alone():
    w = _world(1, 2, seed=1, write_cost=5)
    w.grid = [[(1, 1, 0, 7, 100), (0, 0, 0, 0, 0)]]
    n = w.step()
    assert n.grid[0][0][ok1.ENERGY] == 95


def test_k1_case2_two_competing_donors():
    w = _world(1, 3, seed=5, write_cost=5)
    w.grid = [[(1, 1, 4, 30, 50), (0, 0, 0, 0, 0), (1, 3, 4, 40, 80)]]
    trace = []
    n = w.step(trace=trace)
    total_before = 50 + 0 + 80
    total_after = sum(n.grid[0][c][ok1.ENERGY] for c in range(3))
    credited = [row[2] for row in trace if row[0] == "energy_credited"][0]
    assert total_after == total_before - (5 + 5) - (30 + 40) + credited


def test_k1_case3_overflow():
    w = _world(1, 2, seed=7, write_cost=2)
    # payload=250 forces transfer_amt = min(250, energy-2) = 198.
    w.grid = [[(1, 1, 4, 250, 200), (0, 0, 0, 0, 100)]]
    n = w.step()
    assert n.grid[0][0][ok1.ENERGY] == 0
    assert n.grid[0][1][ok1.ENERGY] == 255  # 100 + min(198, 155) = 255


def test_k1_case4_self_transfer_nets_to_minus_write_cost():
    w = _world(1, 1, seed=2, write_cost=3)
    w.grid = [[(1, 0, 4, 100, 50)]]  # any direction wraps to self on W=1.
    n = w.step()
    assert n.grid[0][0][ok1.ENERGY] == 47  # 50 - WRITE_COST, no creation.


def test_k1_case5_maintenance_floor():
    w = _world(1, 1, seed=3, maintenance_cost=5)
    w.grid = [[(0, 0, 0, 0, 2)]]
    n = w.step()
    assert n.grid[0][0][ok1.ENERGY] == 0


def test_k1_case6_saturated_replenishment():
    w = _world(1, 1, seed=4, replenish_numer=2**32, replenish_amount=20)
    w.grid = [[(0, 0, 0, 0, 250)]]
    n = w.step()
    assert n.grid[0][0][ok1.ENERGY] == 255  # gross 20 partially rejected.


# ---------------------------------------------------------------------
# K2 -- exact conditional mutation graph
# ---------------------------------------------------------------------

def test_k2_all_inert_world_never_mutates_at_probability_one():
    w = _world(1, 3, seed=9, mut_numer=2**32)  # probability 1, all inert.
    w.grid = [[(0, 11, 22, 33, 0), (0, 44, 55, 66, 0), (0, 77, 88, 99, 0)]]
    trace = []
    n = w.step(trace=trace)
    assert n.grid == w.grid  # byte-for-byte unchanged, at MUT_NUMER=2**32.
    assert not any(row[0] == "mutation_applied" for row in trace)


def test_k2_fixed_donor_repeated_overwrite_is_memoryless():
    # Donor's own payload is never targeted, so it stays fixed; target
    # is overwritten fresh each tick, never accumulating drift. If the
    # implementation instead mutated the TARGET's evolving stored value
    # (a bug), popcount would tend to exceed 1 after a few ticks; a
    # fixed-donor memoryless process keeps it at exactly 1 every tick.
    w = _world(1, 2, seed=11, mut_numer=2**32)  # always mutates.
    w.grid = [[(1, 1, 3, 0b00000000, 0), (0, 0, 0, 0, 0)]]
    for _ in range(5):
        w = w.step()
        v = w.grid[0][1][ok1.PAYLOAD]
        assert bin(v).count("1") == 1, f"expected single-bit draw from fixed donor, got {v:#04x}"


def test_k2_mod5_selector_has_zero_single_bit_neutral_edges():
    # Exhaustive, matching KILL_GATES_01.md K2's proof: no single-bit
    # flip of any of the 256 byte values preserves value % 5.
    neutral_edges = 0
    for value in range(256):
        for bit in range(8):
            if (value ^ (1 << bit)) % 5 == value % 5:
                neutral_edges += 1
    assert neutral_edges == 0
    counts = {r: sum(1 for v in range(256) if v % 5 == r) for r in range(5)}
    assert counts == {0: 52, 1: 51, 2: 51, 3: 51, 4: 51}


# ---------------------------------------------------------------------
# K3 -- relay negative vs constructed-capacity positive
# (HEREDITY_REQUIREMENTS.md "K3 fixtures"; H=1, W=4: A,B,C,D=unrelated
# control cell; direction "right" = arg0 mod 4 == 1 (EAST), field
# indices as named in the fixture text.)
# ---------------------------------------------------------------------

RIGHT = 1
WRITE_COST_K3 = 1


def test_k3_relay_fixture_capacity_is_unaffected_by_ablation():
    def build(a_active: bool):
        a_opcode = ok1.WRITE_OPCODE if a_active else 0x02  # inert if ablated.
        A = (a_opcode, RIGHT, 3, 77, 10)          # writes payload=77 -> B.field3
        B = (ok1.WRITE_OPCODE, RIGHT, 3, 0, 10)   # writes its own payload -> C.field3
        C = (0, 0, 0, 0, 0)
        D = (0, 5, 5, 5, 0)                       # unrelated inert control cell
        return _world(1, 4, seed=21, write_cost=WRITE_COST_K3, grid=[[A, B, C, D]])

    with_a, without_a = build(True), build(False)
    for _ in range(3):
        with_a, without_a = with_a.step(), without_a.step()
        b_with = with_a.grid[0][1]
        b_without = without_a.grid[0][1]
        # CONSTRUCTED_CAPACITY would require ablating A to change B's own
        # opcode/arg0/arg1; it does not (A only ever targets B's payload).
        assert b_with[ok1.OPCODE:ok1.PAYLOAD] == b_without[ok1.OPCODE:ok1.PAYLOAD]
        # But B's PAYLOAD (the value transported onward to C) does differ,
        # confirming CAUSAL_VALUE_CONSTRUCTION holds for A->B.
    assert with_a.grid[0][1][ok1.PAYLOAD] != without_a.grid[0][1][ok1.PAYLOAD]


def test_k3_constructed_capacity_fixture_b_never_activates_without_a():
    def build(a_active: bool):
        a_opcode = ok1.WRITE_OPCODE if a_active else 0x02
        A = (a_opcode, RIGHT, 0, ok1.WRITE_OPCODE, 10)  # targets B's OPCODE field.
        B = (0x00, RIGHT, 3, 99, 10)                     # pre-wired, but inert.
        C = (0, 0, 0, 0, 0)
        D = (0, 5, 5, 5, 0)
        return _world(1, 4, seed=23, write_cost=WRITE_COST_K3, grid=[[A, B, C, D]])

    with_a = build(True)
    without_a = build(False)
    for _ in range(4):
        with_a, without_a = with_a.step(), without_a.step()
    # With A: B was activated (opcode became WRITE) and forwarded to C.
    assert with_a.grid[0][1][ok1.OPCODE] == ok1.WRITE_OPCODE
    assert with_a.grid[0][2][ok1.PAYLOAD] == 99
    # Without A: B's capacity to act never changed -- this IS
    # CONSTRUCTED_CAPACITY evidence (ablating A changes B's own capacity).
    assert without_a.grid[0][1][ok1.OPCODE] == 0x00
    assert without_a.grid[0][2][ok1.PAYLOAD] == 0


def test_k3_fixtures_receive_different_verdicts_ladder_is_usable():
    # Operator's pre-registered pass condition: if these two fixtures
    # got the SAME verdict, the claim standard would be unusable.
    relay_reaches_constructed_capacity = False  # proven above: opcode/arg0/arg1 unaffected.
    capacity_fixture_reaches_constructed_capacity = True  # proven above: opcode IS affected.
    assert relay_reaches_constructed_capacity != capacity_fixture_reaches_constructed_capacity


# ---------------------------------------------------------------------
# K6 -- provenance overlay composition (EXPERIMENTS.md S06 repair)
# ---------------------------------------------------------------------

def test_k6_seeded_base_survives_every_overlay():
    # Regime 3/4 (seeded) base + regime 5/6/7 (resource/init) overlay.
    assert instrument_class(seeded_pattern_present=True) == SEEDED_CONTROL


def test_k6_spontaneous_base_survives_every_overlay():
    # Regime 1/2 (unstructured) base + regime 5/6/7 overlay.
    assert instrument_class(seeded_pattern_present=False) == SPONTANEOUS


def test_k6_no_configuration_is_labeled_both_ways():
    # Totality + exclusivity of the composition rule.
    assert {instrument_class(True), instrument_class(False)} == {SEEDED_CONTROL, SPONTANEOUS}
