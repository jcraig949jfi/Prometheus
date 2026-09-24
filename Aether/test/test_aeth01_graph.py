"""Known-answer tests for the functional-graph observatory.

Every statistic is checked against a graph whose answer is known by
construction, and cycle detection is additionally checked against a
brute-force walk written from the definition rather than from the module
under test. A graph measurement that is wrong is worse than absent: it
would produce cycle counts and persistence numbers that look like
evidence of circuitry.
"""

import numpy as np
import pytest

from observatory import aeth01_graph as g
from reference.gpu_aeth01 import gpu_step, mix64_scalar
from reference import oracle_aeth01 as ok1

NO = g.NO_WINNER


def _observer(h, w, entries, differs=None):
    """Build a side-channel record by hand.

    entries: {(field, r, c): slot}. differs: {(field, r, c): n_differ},
    the number of valid proposals that would have changed that target.
    """
    obs = []
    differs = differs or {}
    for field in range(5):
        ws = np.full((h, w), NO, dtype=np.uint8)
        cs = np.zeros((h, w), dtype=np.uint8)
        nd = np.zeros((h, w), dtype=np.uint8)
        for (f, r, c), slot in entries.items():
            if f == field:
                ws[r, c] = slot
                cs[r, c] = 1
        for (f, r, c), n in differs.items():
            if f == field:
                nd[r, c] = n
        obs.append((ws, cs, nd))
    return obs


def _brute_cycle_nodes(nxt):
    """Straight from the definition: v is on a cycle iff walking from v
    returns to v within N steps."""
    nxt = np.asarray(nxt)
    n = nxt.shape[0]
    on = set()
    for v in range(n):
        if nxt[v] < 0:
            continue
        seen = {}
        cur, step = v, 0
        while cur >= 0 and cur not in seen:
            seen[cur] = step
            cur = int(nxt[cur])
            step += 1
        if cur >= 0:
            # everything from the first repeat onward is on the cycle
            start = seen[cur]
            for node, s in seen.items():
                if s >= start:
                    on.add(node)
    return on


# ------------------------------------------------------- realized map

def test_realized_map_points_source_to_target():
    h = w = 4
    # target (1,1) won by slot 0, whose offset is (-1,0): source (0,1).
    obs = _observer(h, w, {(0, 1, 1): 0})
    nxt = g.realized_map(np, obs, h, w)
    src = 0 * w + 1
    tgt = 1 * w + 1
    assert int(nxt[src]) == tgt
    assert int((np.asarray(nxt) >= 0).sum()) == 1


def test_realized_map_wraps_on_the_torus():
    h = w = 4
    # target (0,0) won by slot 0 (offset -1,0): source is (3,0) by wrap.
    obs = _observer(h, w, {(2, 0, 0): 0})
    nxt = g.realized_map(np, obs, h, w)
    assert int(nxt[3 * w + 0]) == 0


@pytest.mark.parametrize("slot,offset", list(enumerate(g.SLOT_OFFSETS)))
def test_every_slot_maps_to_the_right_neighbour(slot, offset):
    h = w = 5
    dr, dc = offset
    obs = _observer(h, w, {(1, 2, 2): slot})
    nxt = g.realized_map(np, obs, h, w)
    expected_src = ((2 + dr) % h) * w + ((2 + dc) % w)
    assert int(nxt[expected_src]) == 2 * w + 2


def test_unwon_sites_are_undefined_not_zero():
    h = w = 3
    nxt = g.realized_map(np, _observer(h, w, {}), h, w)
    assert np.all(np.asarray(nxt) == -1), "an empty tick must map nothing"


# ------------------------------------------------- the partial-function claim

def test_partial_function_holds_on_a_real_tick():
    h = w = 16
    rng = np.random.default_rng(5)
    f = [rng.integers(0, 256, size=(h, w), dtype=np.uint8) for _ in range(5)]
    f[0] = np.where(rng.random((h, w)) < 0.8, np.uint8(1), f[0]).astype(np.uint8)
    obs = []
    gpu_step(h, w, 0xABC, 5, 1, 0, 0, 0, 1 << 30, *f, observer=obs)
    assert g.assert_partial_function(np, obs, h, w) <= 1, (
        "a source won more than one contest; out-degree is not 1 and every "
        "graph statistic in this module is invalid")


def test_a_deliberately_impossible_record_is_detected():
    # Cheat control for the claim itself: fabricate two fields claiming
    # the same source and require the check to notice.
    h = w = 4
    obs = _observer(h, w, {(0, 1, 1): 0, (1, 1, 1): 0})
    assert g.assert_partial_function(np, obs, h, w) == 2


# ------------------------------------------------------- cycle detection

def test_cycle_count_on_a_hand_built_two_cycle():
    h, w = 1, 2
    # (0,0) -> (0,1) via slot 2 (offset 0,+1 means source is target+(0,1));
    # build the 2-cycle explicitly instead: both sites win from each other.
    obs = _observer(h, w, {(0, 0, 0): 2, (0, 0, 1): 3})
    nxt = g.realized_map(np, obs, h, w)
    count, _steps = g.cycle_node_count(np, nxt)
    assert count == len(_brute_cycle_nodes(nxt))
    assert count == 2


def test_a_pure_chain_has_no_cycle_nodes():
    n = 8
    nxt = np.full(n, -1, dtype=np.int64)
    for i in range(n - 1):
        nxt[i] = i + 1           # 0->1->...->7, 7 undefined
    count, _ = g.cycle_node_count(np, nxt)
    assert count == 0
    assert _brute_cycle_nodes(nxt) == set()


def test_trees_feeding_a_cycle_count_only_the_cycle():
    #  3 -> 4 -> 0 -> 1 -> 2 -> 0     cycle is {0,1,2}
    nxt = np.array([1, 2, 0, 4, 0, -1, -1, -1], dtype=np.int64)
    count, _ = g.cycle_node_count(np, nxt)
    assert count == 3
    assert _brute_cycle_nodes(nxt) == {0, 1, 2}


def test_self_loop_counts_as_a_cycle():
    nxt = np.array([0, -1], dtype=np.int64)
    count, _ = g.cycle_node_count(np, nxt)
    assert count == 1


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5, 6, 7, 8])
def test_cycle_count_matches_brute_force_on_random_functional_graphs(seed):
    rng = np.random.default_rng(seed)
    n = 64
    nxt = rng.integers(-1, n, size=n, dtype=np.int64)
    count, _ = g.cycle_node_count(np, nxt)
    assert count == len(_brute_cycle_nodes(nxt)), nxt.tolist()


# ---------------------------------------------------------- aggregates

def test_edges_and_changed_edges_are_counted_separately():
    h = w = 4
    obs = _observer(h, w, {(3, 2, 2): 1, (3, 0, 0): 1})
    before = [np.zeros((h, w), dtype=np.uint8) for _ in range(5)]
    after = [b.copy() for b in before]
    after[3][2, 2] = 7          # one of the two edges actually changed state
    agg = g.edge_aggregates(np, obs, before, after)
    assert agg["edges_total"] == 2
    assert agg["edges_by_field"]["payload"] == 2
    assert agg["changed_by_field"]["payload"] == 1, (
        "a same-value rewrite is a real edge but moved no information; the "
        "two must not be conflated")


def test_fan_in_histogram_is_the_contender_distribution():
    h = w = 4
    obs = _observer(h, w, {})
    obs[0][1][0, 0] = 3          # one target had 3 contenders
    obs[0][1][1, 1] = 2
    before = [np.zeros((h, w), dtype=np.uint8) for _ in range(5)]
    agg = g.edge_aggregates(np, obs, before, before)
    hist = agg["fan_in_hist"]["opcode"]
    assert hist[3] == 1 and hist[2] == 1
    assert hist[0] == h * w - 2


def test_slot_histogram_records_directional_flow():
    h = w = 4
    obs = _observer(h, w, {(4, 1, 1): 2, (4, 2, 2): 2, (4, 3, 3): 0})
    before = [np.zeros((h, w), dtype=np.uint8) for _ in range(5)]
    agg = g.edge_aggregates(np, obs, before, before)
    assert agg["slot_hist"]["energy"] == [1, 0, 2, 0]


# --------------------------------------------------------- persistence

def test_run_lengths_grow_while_the_same_slot_keeps_winning():
    h = w = 3
    state = g.new_runlengths(np, h, w)
    obs = _observer(h, w, {(0, 1, 1): 2})
    for expected in (1, 2, 3):
        stats = g.update_runlengths(np, state, obs)
        assert stats["opcode"]["run_max"] == expected
        assert stats["opcode"]["edges_present"] == 1
        assert stats["opcode"]["repeating_edges"] == (1 if expected > 1 else 0)


def test_run_length_resets_when_the_winner_changes():
    h = w = 3
    state = g.new_runlengths(np, h, w)
    a = _observer(h, w, {(0, 1, 1): 2})
    b = _observer(h, w, {(0, 1, 1): 3})
    g.update_runlengths(np, state, a)
    g.update_runlengths(np, state, a)
    # A different winner restarts the run at 1 -- the edge is present,
    # it is just a new edge.
    assert g.update_runlengths(np, state, b)["opcode"]["run_max"] == 1
    assert g.update_runlengths(np, state, b)["opcode"]["run_max"] == 2


def test_run_length_resets_when_the_edge_disappears():
    h = w = 3
    state = g.new_runlengths(np, h, w)
    live = _observer(h, w, {(0, 1, 1): 2})
    empty = _observer(h, w, {})
    g.update_runlengths(np, state, live)
    stats = g.update_runlengths(np, state, empty)
    assert stats["opcode"]["edges_present"] == 0
    assert stats["opcode"]["run_max"] == 0


def test_run_length_saturates_rather_than_wrapping():
    h = w = 1
    state = g.new_runlengths(np, h, w)
    state["run"][0][0, 0] = np.uint16(65534)
    state["last"][0][0, 0] = np.uint8(1)
    obs = _observer(h, w, {(0, 0, 0): 1})
    assert g.update_runlengths(np, state, obs)["opcode"]["run_max"] == 65535
    assert g.update_runlengths(np, state, obs)["opcode"]["run_max"] == 65535, (
        "a wrapped counter would read as a brand-new edge and understate "
        "persistence")


# -------------------------------------------------------------- windows

def test_window_edges_report_sources_outside_the_window():
    h = w = 8
    # target (0,3) won by slot 0 (offset -1,0): source (7,3), outside a
    # window anchored at row 0. Clipping it would hide an inbound edge.
    obs = _observer(h, w, {(2, 0, 3): 0})
    edges = g.window_edges(obs, h, w, 0, 0, 4)
    assert len(edges) == 1
    assert edges[0]["target"] == [0, 3]
    assert edges[0]["source"] == [7, 3]
    assert edges[0]["field"] == 2


def test_window_edges_exclude_targets_outside_the_window():
    h = w = 8
    obs = _observer(h, w, {(0, 6, 6): 1})
    assert g.window_edges(obs, h, w, 0, 0, 4) == []


def test_window_b_origin_is_seed_determined_and_in_range():
    h = w = 4096
    a = g.window_origin(mix64_scalar, 0x5C011701, h, w, 256)
    b = g.window_origin(mix64_scalar, 0x5C011702, h, w, 256)
    assert a != b, "different worlds must not share the seeded window"
    for origin in (a, b):
        assert 0 <= origin[0] <= h - 256 and 0 <= origin[1] <= w - 256
    assert g.window_origin(mix64_scalar, 0x5C011701, h, w, 256) == a, \
        "the seeded origin must be reproducible from the seed alone"


# ------------------------------------- end to end against the oracle

def test_graph_layer_agrees_with_the_oracle_on_a_real_tick():
    h = w = 6
    rng = np.random.default_rng(21)
    grid = [[(ok1.WRITE_OPCODE if rng.random() < 0.8 else int(rng.integers(2, 256)),
              int(rng.integers(0, 256)), int(rng.integers(0, 256)),
              int(rng.integers(0, 256)), int(rng.integers(0, 256)))
             for _ in range(w)] for _ in range(h)]
    world = ok1.Aeth01World(h, w, 0xFEED, 1, 0, 0, 0, 0, tick=4, grid=grid)
    arr = np.array(world.grid, dtype=np.uint8)
    fields = [arr[:, :, i] for i in range(5)]
    obs = []
    out = gpu_step(h, w, world.seed, world.tick, world.write_cost,
                   world.maintenance_cost, world.replenish_numer,
                   world.replenish_amount, world.mut_numer, *fields,
                   observer=obs)
    trace = []
    world.step(trace=trace)
    won = [e for e in trace if e[0] == "proposal_won"]
    agg = g.edge_aggregates(np, obs, fields, list(out[:5]))
    assert agg["edges_total"] == len(won), (
        "aggregate edge count disagrees with the oracle's winning proposals")
    # And the map really is a partial function on this real tick.
    assert g.assert_partial_function(np, obs, h, w) <= 1


# ------------------------------------------- the four-way edge classes
#
# The class names are mechanical and none of them asserts function.
# "same value" does NOT mean "no function": a contested same-value write
# may gate a different value out, and a persistent same-value structure
# may hold state. Only intervention distinguishes those, so these tests
# check the BOOKKEEPING only.

def _flat(h, w, v=0):
    return [np.full((h, w), v, dtype=np.uint8) for _ in range(5)]


def test_state_changing_is_classified_when_the_target_moves():
    h = w = 3
    obs = _observer(h, w, {(3, 1, 1): 0})
    before = _flat(h, w, 5)
    after = [b.copy() for b in before]
    after[3][1, 1] = 9
    cls = g.edge_classes(np, obs, before, after)["payload"]
    assert cls["edges"] == 1
    assert cls["STATE_CHANGING"] == 1
    assert cls["SAME_VALUE_UNCONTESTED"] == 0


def test_same_value_uncontested_is_a_single_contender_rewrite():
    h = w = 3
    obs = _observer(h, w, {(3, 1, 1): 0})
    before = _flat(h, w, 5)
    cls = g.edge_classes(np, obs, before, before)["payload"]
    assert cls["STATE_CHANGING"] == 0
    assert cls["SAME_VALUE_UNCONTESTED"] == 1
    assert cls["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"] == 0
    assert cls["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"] == 0


def test_contested_same_value_splits_on_whether_a_loser_would_have_changed_it():
    h = w = 3
    before = _flat(h, w, 5)

    # Contested, and at least one valid proposal differed from the stored
    # value: this winner's victory kept that change out. Whether that
    # gating matters is a question for intervention, not for this count.
    gating = _observer(h, w, {(3, 1, 1): 0}, differs={(3, 1, 1): 1})
    gating[3][1][1, 1] = 3
    cls = g.edge_classes(np, gating, before, before)["payload"]
    assert cls["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"] == 1
    assert cls["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"] == 0
    assert cls["SAME_VALUE_UNCONTESTED"] == 0

    # Contested, but nobody proposed anything different: a redundant
    # multi-way refresh, which gates nothing out.
    inert = _observer(h, w, {(3, 1, 1): 0}, differs={(3, 1, 1): 0})
    inert[3][1][1, 1] = 2
    cls = g.edge_classes(np, inert, before, before)["payload"]
    assert cls["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"] == 1
    assert cls["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"] == 0


def test_classes_partition_the_edges_exactly():
    h = w = 8
    rng = np.random.default_rng(4)
    f = [rng.integers(0, 256, size=(h, w), dtype=np.uint8) for _ in range(5)]
    f[0] = np.where(rng.random((h, w)) < 0.8, np.uint8(1), f[0]).astype(np.uint8)
    obs = []
    out = gpu_step(h, w, 0x1234, 9, 1, 0, 0, 0, 1 << 30, *f, observer=obs)
    cls = g.edge_classes(np, obs, f, list(out[:5]))
    for name, row in cls.items():
        total = (row["STATE_CHANGING"] + row["SAME_VALUE_UNCONTESTED"]
                 + row["SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE"]
                 + row["SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE"])
        assert total == row["edges"], (
            "%s: classes sum to %d over %d edges; the four classes must "
            "partition the edge set exactly" % (name, total, row["edges"]))


def test_energy_is_classified_separately_from_the_template_fields():
    h = w = 6
    rng = np.random.default_rng(8)
    f = [rng.integers(0, 256, size=(h, w), dtype=np.uint8) for _ in range(5)]
    f[0] = np.where(rng.random((h, w)) < 0.9, np.uint8(1), f[0]).astype(np.uint8)
    f[2] = np.full((h, w), 4, dtype=np.uint8)      # every writer targets ENERGY
    obs = []
    out = gpu_step(h, w, 0xBEEF, 2, 1, 0, 0, 0, 0, *f, observer=obs)
    cls = g.edge_classes(np, obs, f, list(out[:5]))
    assert cls["energy"]["edges"] > 0
    assert all(cls[k]["edges"] == 0
               for k in ("opcode", "arg0", "arg1", "payload"))


def test_classes_can_be_restricted_to_a_persistent_structure():
    h = w = 4
    obs = _observer(h, w, {(3, 1, 1): 0, (3, 2, 2): 0})
    before = _flat(h, w, 5)
    after = [b.copy() for b in before]
    after[3][1, 1] = 7
    after[3][2, 2] = 7
    keep = np.zeros((h, w), dtype=bool)
    keep[1, 1] = True
    assert g.edge_classes(np, obs, before, after)["payload"]["edges"] == 2
    assert g.edge_classes(np, obs, before, after,
                          restrict=keep)["payload"]["edges"] == 1


def test_cycle_mask_matches_the_cycle_count():
    nxt = np.array([1, 2, 0, 4, 0, -1, -1, -1], dtype=np.int64)
    mask, count, _ = g.cycle_node_mask(np, nxt)
    assert count == 3
    assert sorted(np.nonzero(np.asarray(mask))[0].tolist()) == [0, 1, 2]
    assert count == g.cycle_node_count(np, nxt)[0]
