"""proteus.graph_organism.v1 runtime -- controls.

identity   the graph runtime hash is not the v0 hash; v0's hash is unchanged by this package
replay     same manifest + same inputs + same seed -> byte-identical outputs and meter
dormant    an unconnected node never executes and costs 0 ops; adding one does not change behaviour
routing    ROUTE takes port 0 on nonzero, port 1 on zero; moving a subgraph (re-indexing) keeps it
call       CALL/RETURN reuse one subgraph from two sites; depth limit refuses without crashing
yield      YIELD resumes at its successor next tick; HALT resumes at entry
persist    node persist keeps a value across ticks; persist_state keeps the state array
validate   out-of-table kind, double edge into a port, bad port, unknown key are refused
abi        run_tick has the v0 shape (state, inputs, n_out, rng, meter) and speaks channels
hygiene    proteus.graph imports only stdlib + proteus.foundry.{prng,identity}
"""
from __future__ import annotations

import ast
import copy
import os

import pytest

from proteus.foundry.identity import RUNTIME_HASH as V0_RUNTIME_HASH
from proteus.foundry.prng import SplitMix64
from proteus.graph import generate as G
from proteus.graph import identity as I
from proteus.graph.vm import (ADD, CALL, CONST, HALT, ID, IN, OUT, RETURN, ROUTE, SCHEMA, YIELD, GraphMeter, GraphPlayer,
                              canonicalize, live_nodes, validate_manifest)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _n(kind, *params, persist=False):
    return {"kind": kind, "params": list(params), "persist": persist}


def _m(nodes, data, control, entry=0, **cfg):
    base = {"schema_version": SCHEMA, "nodes": nodes, "data_edges": data, "control_edges": control, "entry": entry,
            "state_words": 16, "tick_budget": 64, "out_cap": 4, "call_depth_max": 4, "persist_state": False}
    base.update(cfg)
    return canonicalize(base)


def _run(m, inputs, ticks=1, seed=0, n_out=1):
    p = GraphPlayer(m)
    st = p.fresh_state()
    rng = SplitMix64(seed)
    mt = GraphMeter(p.n)
    outs = []
    for _ in range(ticks):
        o, status = p.run_tick(st, inputs, n_out, rng, meter=mt)
        outs.append((o, status))
        st["ticks"] += 1
    return outs, mt.as_dict(), st


def test_identity_is_new_and_v0_untouched():
    assert I.RUNTIME_HASH != V0_RUNTIME_HASH
    assert V0_RUNTIME_HASH.startswith("73f110e21b9d")
    assert I.RUNTIME["runtime_version"] == "proteus.runtime.graph.v1"


def test_replay_is_byte_identical_over_random_population():
    fm = dict(G.DEFAULT_FOUNDRY_MANIFEST, seed=3, n=60)
    for o in G.generate(fm):
        a = _run(o["manifest"], [[5, 6], [7]], ticks=4, seed=11)
        b = _run(o["manifest"], [[5, 6], [7]], ticks=4, seed=11)
        assert a[0] == b[0] and a[1] == b[1]


def test_dormant_node_costs_nothing_and_changes_nothing():
    m = _m([_n(CONST, 42), _n(CONST, 0), _n(OUT), _n(HALT)], [[0, 2, 0], [1, 2, 1]], [[0, 0, 1], [1, 0, 2], [2, 0, 3]])
    outs, meter, _ = _run(m, [[]])
    assert outs[0][0] == [[42]] and meter["ops"] == 4
    m2 = copy.deepcopy(m)
    m2["nodes"].append(_n(ADD))                       # unconnected
    m2 = canonicalize(m2)
    assert GraphPlayer(m2).dormant == [4]
    outs2, meter2, _ = _run(m2, [[]])
    assert outs2[0][0] == [[42]] and meter2["ops"] == 4 and meter2["node_exec"][4] == 0


def test_route_selects_port_by_predicate():
    # entry: IN key -> ROUTE(key): port0 -> OUT 1 ; port1 -> OUT 2
    nodes = [_n(CONST, 0), _n(IN), _n(ROUTE), _n(CONST, 1), _n(OUT), _n(HALT), _n(CONST, 2), _n(OUT), _n(HALT)]
    data = [[0, 1, 0], [1, 2, 0], [3, 4, 0], [0, 4, 1], [6, 7, 0], [0, 7, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 4], [4, 0, 5], [2, 1, 6], [6, 0, 7], [7, 0, 8]]
    m = _m(nodes, data, control)
    assert _run(m, [[7]])[0][0][0] == [[1]]
    assert _run(m, [[0]])[0][0][0] == [[2]]
    # re-indexing the whole genome (a permutation) preserves behaviour: structure is connectivity
    perm = [8, 7, 6, 5, 4, 3, 2, 1, 0]
    inv = {old: new for new, old in enumerate(perm)}
    m2 = _m([nodes[i] for i in perm], [[inv[s], inv[d], p] for s, d, p in data],
            [[inv[s], p, inv[d]] for s, p, d in control], entry=inv[0])
    assert _run(m2, [[7]])[0][0][0] == [[1]] and _run(m2, [[0]])[0][0][0] == [[2]]


def test_call_return_reuses_one_subgraph_from_two_sites():
    # body: node 5 = ADD(acc, one) persist -> RETURN.  main: CALL body, CALL body, OUT acc, HALT
    nodes = [_n(CALL), _n(CALL), _n(OUT), _n(HALT), _n(CONST, 1), _n(ADD, persist=True), _n(RETURN), _n(CONST, 0)]
    data = [[5, 5, 0], [4, 5, 1], [5, 2, 0], [7, 2, 1]]
    control = [[0, 0, 4], [4, 0, 5], [5, 0, 6], [0, 1, 1], [1, 0, 4], [1, 1, 2], [2, 0, 3]]
    m = _m(nodes, data, control)
    outs, meter, _ = _run(m, [[]])
    assert outs[0][0] == [[2]]                          # body ran twice from two call sites
    assert meter["node_exec"][5] == 2 and meter["call_depth_max_reached"] == 1
    m0 = _m(nodes, data, control, call_depth_max=0)     # depth 0: CALL falls through to `after`
    outs0, meter0, _ = _run(m0, [[]])
    assert outs0[0][0] == [[0]] and meter0["call_depth_refused"] == 2


def test_yield_resumes_at_successor_and_halt_at_entry():
    nodes = [_n(CONST, 1), _n(CONST, 0), _n(OUT), _n(YIELD), _n(CONST, 2), _n(OUT), _n(HALT)]
    data = [[0, 2, 0], [1, 2, 1], [4, 5, 0], [1, 5, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 4], [4, 0, 5], [5, 0, 6]]
    outs, meter, st = _run(_m(nodes, data, control), [[]], ticks=3)
    assert [o for o, _ in outs] == [[[1]], [[2]], [[1]]]
    assert [s for _, s in outs] == ["yield", "halt", "yield"]


def test_persistence_flags():
    # counter: persist node ADD(self, 1) each tick; OUT it
    nodes = [_n(CONST, 1), _n(ADD, persist=True), _n(CONST, 0), _n(OUT), _n(HALT)]
    data = [[1, 1, 0], [0, 1, 1], [1, 3, 0], [2, 3, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 4]]
    outs, _, _ = _run(_m(nodes, data, control), [[]], ticks=3)
    assert [o for o, _ in outs] == [[[1]], [[2]], [[3]]]
    nodes2 = list(nodes); nodes2[1] = _n(ADD, persist=False)
    outs2, _, _ = _run(_m(nodes2, data, control), [[]], ticks=3)
    assert [o for o, _ in outs2] == [[[1]], [[1]], [[1]]]


def test_validation_refusals():
    good = _m([_n(CONST, 1), _n(HALT)], [], [[0, 0, 1]])
    for mutate in (
        lambda m: m["nodes"].append({"kind": 99, "params": [], "persist": False}),
        lambda m: m["data_edges"].extend([[0, 0, 0]]),                     # CONST has no data-in port
        lambda m: m["control_edges"].extend([[0, 0, 0]]),                  # second edge out of (0,0)
        lambda m: m.update(bogus=1),
        lambda m: m.update(entry=7),
        lambda m: m.update(tick_budget=1),
    ):
        bad = copy.deepcopy(good)
        mutate(bad)
        with pytest.raises(ValueError):
            validate_manifest(bad)


def test_live_nodes_and_abi_shape():
    fm = dict(G.DEFAULT_FOUNDRY_MANIFEST, seed=5, n=20)
    for o in G.generate(fm):
        m = o["manifest"]
        live = live_nodes(m)
        p = GraphPlayer(m)
        assert set(p.dormant) == set(range(p.n)) - live
        st = p.fresh_state()
        outs, status = p.run_tick(st, [[1, 2], [3]], 2, SplitMix64(1), meter=GraphMeter(p.n))
        assert len(outs) == 2 and status in ("halt", "yield", "budget")


def test_import_hygiene():
    allowed = {"proteus.foundry.prng", "proteus.foundry.identity"}
    for fn in ("affordances.py", "vm.py", "generate.py", "grammar.py", "lineage.py", "identity.py"):
        tree = ast.parse(open(os.path.join(ROOT, "proteus", "graph", fn), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("proteus.") \
                    and not node.module.startswith("proteus.graph"):
                assert node.module in allowed, (fn, node.module)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                for nm in names:
                    assert not any(nm.startswith(x) for x in ("ew", "evidence_wiki", "requests", "httpx", "psycopg", "archaeon")), (fn, nm)
