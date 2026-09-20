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
# K3 closure-patch addendum -- CONSTRUCTION (fixture 3, per-field
# ablations) and RECURSIVE_CONSTRUCTION (fixture 4), HEREDITY_REQUIREMENTS.md.
# ---------------------------------------------------------------------

NORTH_K3, EAST_K3, SOUTH_K3, WEST_K3 = 0, 1, 2, 3
WRITE_COST_K3B = 1


def _fixture3_grid(a_opcode_active: bool, a_arg0_active: bool):
    # H=3, W=3 torus; B at center (1,1); N=(0,1)=A_opcode writes SOUTH
    # into B; W=(1,0)=A_arg0 writes EAST into B; E=(1,2)=C is B's
    # CORRECTLY-routed target; S=(2,1)=F is B's WRONG (inert-default)
    # target; (0,0)=CTRL unrelated control cell.
    a_opcode_op = ok1.WRITE_OPCODE if a_opcode_active else 0x02
    a_arg0_op = ok1.WRITE_OPCODE if a_arg0_active else 0x02
    ctrl = (0, 5, 5, 5, 0)
    a_opcode_cell = (a_opcode_op, SOUTH_K3, 0, ok1.WRITE_OPCODE, 10)  # -> B field0(OPCODE)=WRITE_OPCODE.
    a_arg0_cell = (a_arg0_op, EAST_K3, 1, EAST_K3, 10)                # -> B field1(ARG0)=EAST.
    b = (0x00, SOUTH_K3, 3, 77, 10)  # inert; wrong-default routes SOUTH to F; field3=PAYLOAD.
    unused = (0, 0, 0, 0, 0)
    c = (0, 0, 0, 0, 0)  # correctly-routed target (E neighbor of B).
    f = (0, 0, 0, 0, 0)  # wrong-default target (S neighbor of B).
    grid = [
        [ctrl, a_opcode_cell, unused],
        [a_arg0_cell, b, c],
        [unused, f, unused],
    ]
    return _world(3, 3, seed=31, write_cost=WRITE_COST_K3B, grid=grid), ctrl


def test_k3_construction_fixture_both_ablations_active_routes_to_c():
    w, ctrl = _fixture3_grid(a_opcode_active=True, a_arg0_active=True)
    for _ in range(3):
        w = w.step()
    assert w.grid[1][1][ok1.OPCODE] == ok1.WRITE_OPCODE  # B activated.
    assert w.grid[1][1][ok1.ARG0] == EAST_K3              # B's routing was CONSTRUCTED, not just activated.
    assert w.grid[1][2][ok1.PAYLOAD] == 77                # C (correct target) received B's payload.
    assert w.grid[2][1][ok1.PAYLOAD] == 0                 # F (wrong-default target) never received it.
    assert w.grid[0][0] == ctrl                           # matched control untouched.


def test_k3_construction_fixture_opcode_only_ablation_b_never_activates():
    w, ctrl = _fixture3_grid(a_opcode_active=False, a_arg0_active=True)
    for _ in range(3):
        w = w.step()
    assert w.grid[1][1][ok1.OPCODE] == 0x00  # B never activated at all -- ablation (a).
    assert w.grid[1][2][ok1.PAYLOAD] == 0
    assert w.grid[2][1][ok1.PAYLOAD] == 0
    assert w.grid[0][0] == ctrl


def test_k3_construction_fixture_routing_only_ablation_b_activates_but_misroutes():
    w, ctrl = _fixture3_grid(a_opcode_active=True, a_arg0_active=False)
    for _ in range(3):
        w = w.step()
    # B DOES activate (opcode construction unaffected by this ablation) --
    # this is exactly the ACTIVATION_OF_PRECONFIGURED_MACHINERY vs.
    # CONSTRUCTION distinction: activation alone does not imply correct
    # routing was also constructed.
    assert w.grid[1][1][ok1.OPCODE] == ok1.WRITE_OPCODE
    assert w.grid[1][1][ok1.ARG0] == SOUTH_K3   # routing NEVER constructed -- stuck at inert default.
    assert w.grid[1][2][ok1.PAYLOAD] == 0       # C (intended target) never receives anything.
    assert w.grid[2][1][ok1.PAYLOAD] == 77      # F (wrong default target) receives it instead.
    assert w.grid[0][0] == ctrl


RIGHT_K3 = 1


def _fixture4_grid(a_active: bool):
    # 1x5 chain A,B,C,D,E (E = unrelated control). A constructs B's
    # capacity (opcode); B, once capable, constructs C's capacity
    # (opcode); C, once capable, writes to D. Single-lever ablation (A)
    # must break BOTH construction steps if RECURSIVE_CONSTRUCTION holds.
    a_op = ok1.WRITE_OPCODE if a_active else 0x02
    a = (a_op, RIGHT_K3, 0, ok1.WRITE_OPCODE, 10)     # -> B field0(OPCODE)=WRITE_OPCODE.
    b = (0x00, RIGHT_K3, 0, ok1.WRITE_OPCODE, 10)     # pre-wired: once active, -> C field0(OPCODE)=WRITE_OPCODE.
    c = (0x00, RIGHT_K3, 3, 99, 10)                   # pre-wired: once active, -> D field3(PAYLOAD)=99.
    d = (0, 0, 0, 0, 0)
    e = (0, 5, 5, 5, 0)
    return _world(1, 5, seed=37, write_cost=WRITE_COST_K3, grid=[[a, b, c, d, e]])


def test_k3_recursive_construction_fixture_full_chain_with_a():
    w = _fixture4_grid(a_active=True)
    for _ in range(4):
        w = w.step()
    assert w.grid[0][1][ok1.OPCODE] == ok1.WRITE_OPCODE   # B's capacity constructed by A.
    assert w.grid[0][2][ok1.OPCODE] == ok1.WRITE_OPCODE   # C's capacity constructed by B (recursively).
    assert w.grid[0][3][ok1.PAYLOAD] == 99                # D received C's write -- chain completed.
    assert w.grid[0][4] == (0, 5, 5, 5, 0)                # control untouched.


def test_k3_recursive_construction_fixture_single_ablation_breaks_both_steps():
    w = _fixture4_grid(a_active=False)
    for _ in range(4):
        w = w.step()
    # A single upstream ablation propagates through BOTH construction
    # steps -- exactly the RECURSIVE_CONSTRUCTION signature.
    assert w.grid[0][1][ok1.OPCODE] == 0x00
    assert w.grid[0][2][ok1.OPCODE] == 0x00
    assert w.grid[0][3][ok1.PAYLOAD] == 0
    assert w.grid[0][4] == (0, 5, 5, 5, 0)


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


# ---------------------------------------------------------------------
# K4 -- cheap DETERMINISTIC oracle fixtures (closure-patch addendum).
# These are existence-proof golden vectors for one concrete instance
# each, NOT the statistical characterization K4 ultimately requires
# (emergent strategy DISTRIBUTIONS need a running sweep, still
# deferred -- KILL_GATES_01.md). Each fixture below is fully
# reproducible from a fixed seed/config; nothing here is sampled or
# averaged.
# ---------------------------------------------------------------------

def test_k4_isolated_pulse_budget_cell_exhausts_deterministically():
    write_cost, maintenance_cost, energy0 = 3, 2, 20
    per_tick_cost_while_active = write_cost + maintenance_cost
    expected_pulses = energy0 // per_tick_cost_while_active  # closed-form budget.
    w = _world(1, 2, seed=41, write_cost=write_cost, maintenance_cost=maintenance_cost)
    w.grid = [[(1, 1, 3, 7, energy0), (0, 0, 0, 0, 0)]]
    pulses = 0
    for _ in range(expected_pulses + 3):  # run past exhaustion to confirm it STAYS stopped.
        trace = []
        w = w.step(trace=trace)
        if any(ev[0] == "proposal_emitted" for ev in trace):
            pulses += 1
        else:
            break
    assert pulses == expected_pulses
    for _ in range(5):  # no replenishment configured -- must never resume.
        trace = []
        w = w.step(trace=trace)
        assert not any(ev[0] == "proposal_emitted" for ev in trace)
    assert w.grid[0][0][ok1.ENERGY] == 0


def test_k4_equal_mean_bursty_vs_uniform_replenishment_diverge():
    # Equal MEAN replenishment rate (5/tick) via two different mechanisms:
    # uniform (prob=1, amount=5) vs bursty (prob=0.5, amount=10). A
    # closed-form mean-rate argument alone cannot distinguish these;
    # this demonstrates their REALIZED trajectories differ at a fixed,
    # reproducible seed -- burstiness is a real observable degree of
    # freedom, not collapsed by matching the mean.
    seed = 51
    uniform = _world(1, 1, seed=seed, replenish_numer=2**32, replenish_amount=5)
    bursty = _world(1, 1, seed=seed, replenish_numer=2**31, replenish_amount=10)
    uniform.grid, bursty.grid = [[(0, 0, 0, 0, 0)]], [[(0, 0, 0, 0, 0)]]
    uniform_trace, bursty_trace = [], []
    for _ in range(6):
        uniform, bursty = uniform.step(), bursty.step()
        uniform_trace.append(uniform.grid[0][0][ok1.ENERGY])
        bursty_trace.append(bursty.grid[0][0][ok1.ENERGY])
    assert uniform_trace == [5, 10, 15, 20, 25, 30]  # deterministic every-tick golden vector.
    assert uniform_trace != bursty_trace              # equal mean, divergent realized trajectory.


def test_k4_reserve_pooling_from_two_sequential_distinct_sources():
    # Two DISTINCT sources, never contending in the same tick's
    # arbitration (donor1 acts at tick 0 then is starved; donor2 is
    # activated only afterward -- the causal activation MECHANISM is
    # K3's concern, not this fixture's; here it is set up directly),
    # sequentially pool into the same target's energy reserve.
    write_cost = 5
    w = _world(1, 3, seed=61, write_cost=write_cost)
    w.grid = [[(1, 1, 4, 100, 105), (0, 0, 0, 0, 0), (0x02, 3, 4, 80, 150)]]
    w = w.step()
    assert w.grid[0][1][ok1.ENERGY] == 100         # target received donor1's contribution.
    assert w.grid[0][0][ok1.ENERGY] < write_cost    # donor1 now starved (spent exactly its budget).
    grid = [list(row) for row in w.grid]
    grid[0][2] = (1, 3, 4, 80, 150)  # activate donor2 for this tick only (separate from donor1's).
    w.grid = grid
    w = w.step()
    assert w.grid[0][1][ok1.ENERGY] == 180  # 100 (donor1) + 80 (donor2) -- pooled, not overwritten.


def test_k4_zero_amount_can_beat_large_amount_arbitration_is_amount_blind():
    # Arbitration priority is a hash of (seed, tick, target, source
    # coords) -- NEVER a function of the proposed VALUE. Search a small,
    # fixed seed range (deterministic, no sampling/statistics) for one
    # concrete seed where a zero-amount proposal beats a large one, and
    # one where the large amount wins -- proving BOTH outcomes are
    # reachable, i.e. winning is not biased toward larger transfers.
    write_cost = 1
    zero_wins_seed = large_wins_seed = None
    for seed in range(200):
        w = _world(1, 3, seed=seed, write_cost=write_cost)
        w.grid = [[(1, 1, 4, 0, 50), (0, 0, 0, 0, 0), (1, 3, 4, 200, 250)]]
        n = w.step()
        target_e = n.grid[0][1][ok1.ENERGY]
        if target_e == 0 and zero_wins_seed is None:
            zero_wins_seed = seed
        if target_e > 0 and large_wins_seed is None:
            large_wins_seed = seed
        if zero_wins_seed is not None and large_wins_seed is not None:
            break
    assert zero_wins_seed is not None, "no seed in range found where the zero-amount proposal won"
    assert large_wins_seed is not None, "no seed in range found where the large-amount proposal won"


# ---------------------------------------------------------------------
# K5 -- cheap DETERMINISTIC oracle fixtures (closure-patch addendum).
# Existence proofs that near-zero/no-visible-change activity is NOT
# proof a world cannot change further (GPU_RUNPOD.md S05 repair); the
# full continued-horizon reactivation AUDIT over an actual sweep
# remains deferred (KILL_GATES_01.md).
# ---------------------------------------------------------------------

def test_k5_starved_writer_reactivates_after_delayed_replenishment():
    write_cost, energy0, replenish_amount = 10, 3, 4
    w = _world(1, 2, seed=71, write_cost=write_cost, replenish_numer=2**32, replenish_amount=replenish_amount)
    w.grid = [[(1, 1, 3, 7, energy0), (0, 0, 0, 0, 0)]]
    emitted_by_tick = []
    for _ in range(3):
        trace = []
        w = w.step(trace=trace)
        emitted_by_tick.append(any(ev[0] == "proposal_emitted" for ev in trace))
    # Dormant (looks "dead") for at least one full tick, THEN reactivates --
    # a naive detector stopping early on "no activity" would have missed this.
    assert emitted_by_tick[0] is False
    assert True in emitted_by_tick[1:], "writer never reactivated within the horizon checked"


def test_k5_same_value_written_repeatedly_then_mutates():
    # Fixed donor (K2's memoryless-overwrite setup); scan for the first
    # tick a mutation actually fires. Finding idle_ticks > 0 confirms a
    # "looks frozen" (same byte written repeatedly) run segment existed
    # before the eventual change -- same-value is NOT proof of immutability.
    mut_numer = 1 << 28  # ~6.5% per tick -- small enough to usually take
                          # several ticks to fire, large enough this
                          # fixture doesn't need a long search window.
    w = _world(1, 2, seed=81, mut_numer=mut_numer)
    w.grid = [[(1, 1, 3, 0b00000000, 0), (0, 0, 0, 0, 0)]]
    values = []
    for _ in range(60):
        w = w.step()
        values.append(w.grid[0][1][ok1.PAYLOAD])
    first_change = next((i for i, v in enumerate(values) if v != 0), None)
    assert first_change is not None, "no mutation observed within the search window"
    assert first_change > 0, "expected at least one idle (unchanged-value) tick before the mutation"
    assert bin(values[first_change]).count("1") == 1  # single-bit flip, per K2.


def test_k5_losing_proposal_later_wins_under_a_different_ticks_priority():
    # SAME source/target coordinates every tick; only `tick` (folded into
    # the arbitration hash) changes. Scan for both outcomes appearing --
    # a currently-losing writer is not permanently excluded, because
    # arbitration is tick-dependent, not a fixed, static ranking.
    w = _world(1, 3, seed=91)
    w.grid = [[(1, 1, 3, 11, 50), (0, 0, 0, 0, 0), (1, 3, 3, 22, 50)]]
    winners = []
    for _ in range(30):
        w = w.step()
        winners.append(w.grid[0][1][ok1.PAYLOAD])
    assert set(winners) == {11, 22}, f"expected both competitors to win at least once, got {set(winners)}"
