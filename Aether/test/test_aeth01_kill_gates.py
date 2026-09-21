"""
AETH-01 -- scientific contract regressions for K1-K6. A disagreement
requires checking BOTH the oracle and the derivation, not assuming either
is correct. K3 is seeded, fixture-local evidence, not a heredity detector.
"""

from math import inf

import pytest

from reference import oracle_aeth01 as ok1
from reference.provenance_aeth01 import SEEDED_CONTROL, SPONTANEOUS, instrument_class
from reference.scientific_aeth01 import (
    CLAIM_TIERS, activation_world, distributed_world, isolated_pulse_budget,
    recursive_activation_world, relay_world, set_field,
)


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
# K3 -- observed edges, distributed attribution and recursive activation.
# These helpers classify ONLY the named fixtures; no resemblance or
# HEREDITY_VARIATION detector (or spontaneous-origin claim) is implied.
# ---------------------------------------------------------------------

def _record(world, ticks=4):
    states, traces = [world], []
    for _ in range(ticks):
        trace = []
        world = world.step(trace=trace)
        states.append(world)
        traces.append(trace)
    return states, traces


def _actions(record, source, include_value=False):
    # Capacity means whether/where/which field is written, NOT payload content.
    return [(tick, *event[2:5 if include_value else 4])
            for tick, trace in enumerate(record[1]) for event in trace
            if event[0] == "proposal_emitted" and event[1] == source]


def _caused_fields(baseline, changed, source, target):
    r, c = target
    return {event[3] for tick, trace in enumerate(baseline[1]) for event in trace
            if event[0] == "proposal_won" and event[1:3] == (source, target)
            and baseline[0][tick + 1].grid[r][c][event[3]]
            != changed[0][tick + 1].grid[r][c][event[3]]}


def _edge_verdict(baseline, changed, control, source, target):
    """Fixture-local verdict from winners, byte effects AND emitted behavior.

    No evidence is unresolved (None), not automatic STRUCTURAL_RESEMBLANCE.
    This is intentionally not a population/recursion/variation detector.
    """
    r, c = target
    assert [w.grid[r][c] for w in baseline[0]] == [w.grid[r][c] for w in control[0]]
    assert _actions(baseline, target, True) == _actions(control, target, True)
    fields = _caused_fields(baseline, changed, source, target)
    if not fields:
        return None
    if fields & {ok1.OPCODE, ok1.ARG0, ok1.ARG1} and _actions(baseline, target) != _actions(changed, target):
        return "CONSTRUCTED_CAPACITY"
    return "CAUSAL_VALUE_CONSTRUCTION"


def _perturbed(builder, cell, field, value):
    world = builder()
    set_field(world, cell, field, value)
    return _record(world)


def test_k3_fixtures_receive_different_observed_verdicts():
    verdicts = []
    for builder in (relay_world, activation_world):
        baseline = _record(builder())
        content = _perturbed(builder, (0, 0), ok1.PAYLOAD, 0)
        ablated = _record(builder(False))
        control = _perturbed(builder, (0, 3), ok1.PAYLOAD, 29)
        verdicts.append(_edge_verdict(baseline, content, control, (0, 0), (0, 1)))
        assert baseline[0][-1].grid[0][2][ok1.PAYLOAD] in (77, 99)
        assert content[0][-1].grid[0][2][ok1.PAYLOAD] == 0
        assert _actions(content, (0, 1)) == _actions(ablated, (0, 1))
        assert _actions(baseline, (0, 0)) == _actions(content, (0, 0))
    assert verdicts == ["CAUSAL_VALUE_CONSTRUCTION", "CONSTRUCTED_CAPACITY"]


@pytest.mark.parametrize("opcode_active,routing_active,opcode,routing,c_payload,f_payload", [
    (True, True, 1, 1, 77, 0),
    (False, True, 0, 1, 0, 0),
    (True, False, 1, 2, 0, 77),
    (False, False, 0, 2, 0, 0),
])
def test_k3_distributed_construction_per_source_ablations(
        opcode_active, routing_active, opcode, routing, c_payload, f_payload):
    states, traces = _record(distributed_world(opcode_active, routing_active))
    assert not any(e[0] == "proposal_emitted" and e[1] == (1, 1) for e in traces[0])
    for state in states[1:]:
        assert state.grid[1][1][:3] == (opcode, routing, 3)
        assert state.grid[1][1][ok1.PAYLOAD] == 77  # initialized, NEVER built
    assert states[-1].grid[1][2][ok1.PAYLOAD] == c_payload
    assert states[-1].grid[2][1][ok1.PAYLOAD] == f_payload


def test_k3_distributed_attribution_requires_two_distinct_sources():
    baseline = _record(distributed_world())
    control = _perturbed(distributed_world, (0, 0), ok1.PAYLOAD, 29)
    contributors = {}
    for source, field in (((0, 1), ok1.OPCODE), ((1, 0), ok1.ARG0)):
        value = 0 if field == ok1.OPCODE else ok1.SOUTH
        content = _perturbed(distributed_world, source, ok1.PAYLOAD, value)
        contributors[source] = _caused_fields(baseline, content, source, (1, 1))
        assert contributors[source] == {field}
        assert _edge_verdict(baseline, content, control, source, (1, 1)) == "CONSTRUCTED_CAPACITY"
        assert _actions(baseline, source) == _actions(content, source)
    assert set().union(*contributors.values()) == {ok1.OPCODE, ok1.ARG0}
    assert all(fields != {ok1.OPCODE, ok1.ARG0} for fields in contributors.values())
    wins = [e[1:4] for e in baseline[1][0] if e[0] == "proposal_won" and e[2] == (1, 1)]
    assert set(wins) == {((0, 1), (1, 1), ok1.OPCODE), ((1, 0), (1, 1), ok1.ARG0)}


def test_k3_neutral_routing_byte_change_is_not_constructed_behavior():
    baseline = _record(distributed_world())
    # 1 -> 5 changes stored arg0 but both decode EAST. Bytes alone overclaim.
    neutral = _perturbed(distributed_world, (1, 0), ok1.PAYLOAD, 5)
    control = _perturbed(distributed_world, (0, 0), ok1.PAYLOAD, 29)
    assert _caused_fields(baseline, neutral, (1, 0), (1, 1)) == {ok1.ARG0}
    assert _edge_verdict(baseline, neutral, control, (1, 0), (1, 1)) == "CAUSAL_VALUE_CONSTRUCTION"
    assert _edge_verdict(baseline, baseline, control, (1, 0), (1, 1)) is None


@pytest.mark.parametrize("field,value,expected_field,expected_payload", [
    (ok1.ARG1, 2, ok1.ARG1, 0),
    (ok1.PAYLOAD, 55, ok1.PAYLOAD, 55),
    (ok1.ENERGY, 0, None, 0),
])
def test_k3_distributed_construction_depends_on_initialized_scaffold(
        field, value, expected_field, expected_payload):
    record = _perturbed(distributed_world, (1, 1), field, value)
    actions = _actions(record, (1, 1))
    assert record[0][-1].grid[1][1][:2] == (1, 1)
    assert {a[2] for a in actions} == (set() if expected_field is None else {expected_field})
    assert record[0][-1].grid[1][2][ok1.PAYLOAD] == expected_payload


@pytest.mark.parametrize("builder,control,focal", [
    (relay_world, (0, 3), ((0, 1), (0, 2))),
    (activation_world, (0, 3), ((0, 1), (0, 2))),
    (distributed_world, (0, 0), ((1, 1), (1, 2), (2, 1))),
    (recursive_activation_world, (0, 4), ((0, 1), (0, 2), (0, 3))),
])
def test_k3_control_is_perturbed_not_merely_untouched(builder, control, focal):
    baseline = _record(builder())
    inert = _perturbed(builder, control, ok1.PAYLOAD, 29)
    # Also give the control equal WRITE cost/energy and a real winning path
    # outside the focal mechanism. This is opportunity-matched for emission,
    # not evidence that arbitrary environments/locations are interchangeable.
    active = []
    for payload in (17, 29):
        world = builder()
        r, c = control
        world.grid[r][c] = (1, 0, 3, payload, 10)
        active.append(_record(world))
    assert _actions(active[0], control, True) != _actions(active[1], control, True)
    assert all(any(e[0] == "proposal_won" and e[1] == control for e in run[1][0]) for run in active)
    for run in (inert, *active):
        for r, c in focal:
            assert [w.grid[r][c] for w in run[0]] == [w.grid[r][c] for w in baseline[0]]
            assert _actions(run, (r, c), True) == _actions(baseline, (r, c), True)


def test_k3_recursive_activation_checks_each_edge_and_time_order():
    baseline = _record(recursive_activation_world())
    control = _perturbed(recursive_activation_world, (0, 4), ok1.PAYLOAD, 29)
    for source, target in (((0, 0), (0, 1)), ((0, 1), (0, 2))):
        content = _perturbed(recursive_activation_world, source, ok1.PAYLOAD, 0)
        assert _edge_verdict(baseline, content, control, source, target) == "CONSTRUCTED_CAPACITY"
        assert _caused_fields(baseline, content, source, target) == {ok1.OPCODE}
        assert content[0][-1].grid[0][3][ok1.PAYLOAD] == 0
    assert _actions(baseline, (0, 1))[0][0] == 1  # A->B committed at tick 0
    assert _actions(baseline, (0, 2))[0][0] == 2  # B->C committed at tick 1
    assert [w.grid[0][3][ok1.PAYLOAD] for w in baseline[0]] == [0, 0, 0, 99, 99]
    for c in (1, 2):
        assert all(w.grid[0][c][1:4] == baseline[0][0].grid[0][c][1:4] for w in baseline[0])
    # Formal tier 4 is supported by both timed edges, but the observed
    # mechanism is RECURSIVE_ACTIVATION_OF_PRECONFIGURED_MACHINERY only.


def test_k3_recursive_activation_upstream_ablation_and_intermediate_rescues():
    absent = _record(recursive_activation_world(False))
    assert not _actions(absent, (0, 1)) and not _actions(absent, (0, 2))
    assert absent[0][-1].grid[0][3][ok1.PAYLOAD] == 0
    for kwargs, first_output_tick in (({"b_active": True}, 2), ({"c_active": True}, 1)):
        rescued = _record(recursive_activation_world(False, **kwargs))
        assert not _actions(rescued, (0, 0))
        output = [w.grid[0][3][ok1.PAYLOAD] for w in rescued[0]]
        assert output.index(99) == first_output_tick
        assert output[-1] == 99
    # Local B->C block leaves A->B working: a global A knockout alone
    # could not establish this edge-specific causal attribution.
    blocked = _perturbed(recursive_activation_world, (0, 1), ok1.PAYLOAD, 0)
    assert blocked[0][-1].grid[0][1][ok1.OPCODE] == 1
    assert _actions(blocked, (0, 1)) and not _actions(blocked, (0, 2))


def test_k3_recursive_activation_does_not_construct_initialized_field_selection():
    def relay_instead_of_second_activation():
        world = recursive_activation_world()
        set_field(world, (0, 1), ok1.ARG1, ok1.PAYLOAD)
        return world

    baseline = _record(relay_instead_of_second_activation())
    content = _perturbed(relay_instead_of_second_activation, (0, 1), ok1.PAYLOAD, 0)
    control = _perturbed(relay_instead_of_second_activation, (0, 4), ok1.PAYLOAD, 29)
    assert baseline[0][-1].grid[0][1][ok1.OPCODE] == 1  # A->B still works.
    assert baseline[0][-1].grid[0][2][ok1.PAYLOAD] == 1  # B->C transports a value.
    assert _edge_verdict(baseline, content, control, (0, 1), (0, 2)) == "CAUSAL_VALUE_CONSTRUCTION"
    assert not _actions(baseline, (0, 2))  # C was never enabled.
    assert baseline[0][-1].grid[0][3][ok1.PAYLOAD] == 0


def test_k3_five_tier_names_are_not_mechanism_labels():
    assert CLAIM_TIERS == (
        "STRUCTURAL_RESEMBLANCE", "CAUSAL_VALUE_CONSTRUCTION", "CONSTRUCTED_CAPACITY",
        "RECURSIVE_CONSTRUCTION", "HEREDITY_VARIATION",
    )


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

@pytest.mark.parametrize("energy0,write_cost,maintenance_cost,expected_pulses", [
    (0, 3, 2, 0), (2, 3, 2, 0), (3, 3, 2, 1), (4, 3, 2, 1),
    (20, 3, 2, 4), (22, 3, 2, 4), (23, 3, 2, 5), (24, 3, 2, 5),
    (7, 3, 0, 2), (255, 255, 255, 1), (255, 1, 255, 1),
])
def test_k4_isolated_pulse_budget_cell_exhausts_deterministically(
        energy0, write_cost, maintenance_cost, expected_pulses):
    assert isolated_pulse_budget(energy0, write_cost, maintenance_cost) == expected_pulses
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
    assert w.grid[0][0][ok1.ENERGY] < write_cost  # starvation need not mean energy=0.


def test_k4_pulse_budget_all_byte_energies_against_independent_recurrence():
    for write_cost in (1, 2, 3, 5, 16, 255):
        for maintenance_cost in (0, 1, 2, 3, 5, 16, 255):
            for energy0 in range(256):
                energy, pulses = energy0, 0
                while energy >= write_cost:
                    pulses += 1
                    energy = max(0, energy - write_cost - maintenance_cost)
                assert isolated_pulse_budget(energy0, write_cost, maintenance_cost) == pulses


@pytest.mark.parametrize("energy0,maintenance_cost", [(0, 0), (0, 2), (5, 2), (255, 255)])
def test_k4_zero_write_cost_never_starves_even_after_maintenance(energy0, maintenance_cost):
    assert isolated_pulse_budget(energy0, 0, maintenance_cost) == inf
    w = _world(1, 2, seed=41, maintenance_cost=maintenance_cost,
               grid=[[(1, 1, 3, 7, energy0), (0, 0, 0, 0, 0)]])
    for _ in range(8):
        trace = []
        w = w.step(trace=trace)
        assert sum(e[0] == "proposal_emitted" for e in trace) == 1


@pytest.mark.parametrize("values", [(-1, 1, 0), (256, 1, 0), (1, -1, 0), (1, 1, 256)])
def test_k4_pulse_budget_rejects_out_of_domain_values(values):
    with pytest.raises(ValueError):
        isolated_pulse_budget(*values)


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
    # reachable, NOT that their probabilities are equal. Amount-blindness
    # follows from the law's inputs, not from two reachable outcomes.
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
