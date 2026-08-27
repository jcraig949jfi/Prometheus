"""Tests for the Operator Genesis substrate. Fast, deterministic."""
from __future__ import annotations

import ast
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from domains import make_domains, DEPTHS                          # noqa: E402
from dsl import BASELINE, classify, enumerate_stage, enumeration_sha, \
    serial                                                        # noqa: E402
from runtime import Adapter, MacroAdapter, Meter, run_program     # noqa: E402
import learner as L                                               # noqa: E402

A3LIKE = ("STAGE", (("A", "S"), ("Z", "P")), ("IF", "FSIZE", "LE", "FSIZE"), "MEET")


# ── dsl ─────────────────────────────────────────────────────────────────────────────

def test_enumeration_frozen():
    progs = enumerate_stage()
    assert len(progs) == 634
    assert enumeration_sha(progs) == "c44f6a4f09094537"


def test_classifier_rules():
    assert classify({"kind": "macro", "word": ["r01", "r02"]}) == "MACRO"
    assert classify(BASELINE) == "NOT_NEW"
    assert classify(A3LIKE) == "ARCHITECTURAL"
    seq = ("SEQ", A3LIKE, A3LIKE)
    assert classify(seq) == "ARCHITECTURAL"


def test_classifier_needs_behavioral_agreement():
    # structural claim unexercised at runtime does not count
    fake_trace = {"spawned": 1, "gens": ["S"], "halt": "goal_fwd"}
    assert classify(A3LIKE, fake_trace) == "PARAMETRIC"


# ── domains ─────────────────────────────────────────────────────────────────────────

def test_clean_domain_predecessors_are_true_inverses():
    for wid in ("dA", "dB", "dC"):
        dom = make_domains()[wid]
        rng = random.Random(1)
        s = dom._rand_state(rng)
        for pid, prev in dom.pred(s):
            assert dom.apply(pid, prev) == s


def test_lossy_domain_predecessors_are_poisoned():
    dD = make_domains()["dD"]
    rng = random.Random(2)
    bad = 0
    for _ in range(20):
        s = dD._rand_state(rng)
        for pid, prev in dD.pred(s):
            if dD.apply(pid, prev) != s:
                bad += 1
    assert bad > 0


def test_task_schema_and_minimality():
    doms = make_domains()
    rng = random.Random(3)
    for wid in ("dA", "dC"):
        task, omni = doms[wid].gen_task(rng, DEPTHS[wid][0])
        assert set(task) == {"start", "target"}
        assert doms[wid].diag_min_dist(omni["s"], omni["t"]) == len(omni["witness"])
    task, omni = doms["dE"].gen_task(rng, 10)
    assert set(task) == {"start", "via", "target"}


# ── runtime ─────────────────────────────────────────────────────────────────────────

def test_strict_budget_no_goal_credit():
    dA = make_domains()["dA"]
    rng = random.Random(4)
    task, _ = dA.gen_task(rng, 10)
    r = run_program(dA, task, BASELINE, 5_000)
    assert not r["solved"] and r["budget_exhausted"]


def test_meet_program_solves_and_verifies():
    dA = make_domains()["dA"]
    rng = random.Random(5)
    task, omni = dA.gen_task(rng, 10)
    r = run_program(dA, task, A3LIKE, 400_000)
    assert r["solved"] and r["trace"]["halt"] == "meet"
    s = omni["s"]
    for pid in r["word"]:
        s = dA.apply(pid, s)
    assert s == omni["t"]


def test_wrong_orientation_never_produces_candidates():
    dA = make_domains()["dA"]
    rng = random.Random(6)
    task, _ = dA.gen_task(rng, 6)
    prog = ("STAGE", (("A", "P"), ("Z", "S")), ("ALT",), "MEET")
    r = run_program(dA, task, prog, 30_000)
    assert not r["solved"] and r["trace"]["verify_calls"] == 0


def test_macro_adapter_flattens_and_charges():
    dA = make_domains()["dA"]
    rng = random.Random(7)
    task, omni = dA.gen_task(rng, 6)
    macro = [dA.pids[1], dA.pids[2], dA.pids[1]]
    meter = Meter(400_000)
    ad = MacroAdapter(dA, task, meter, macro)
    r = run_program(dA, task, BASELINE, 400_000, meter=meter, adapter=ad)
    assert r["solved"]
    assert all(isinstance(p, str) for p in r["word"])      # tuples flattened
    s = omni["s"]
    for pid in r["word"]:
        s = dA.apply(pid, s)
    assert s == omni["t"]


def test_backward_audit_flags_only_lossy():
    doms = make_domains()
    rng = random.Random(8)
    tD, _ = doms["dD"].gen_task(rng, 6)
    rD = run_program(doms["dD"], tD, A3LIKE, 400_000, audit=True)
    tA, _ = doms["dA"].gen_task(rng, 6)
    rA = run_program(doms["dA"], tA, A3LIKE, 400_000, audit=True)
    assert rD["trace"]["bwd_inconsistent"] > 0
    assert rA["trace"]["bwd_inconsistent"] == 0


# ── learner ─────────────────────────────────────────────────────────────────────────

def test_trigger_thresholds():
    ok = [{"budget_exhausted": False}] * 10
    bad = [{"budget_exhausted": True}] * 4 + [{"budget_exhausted": False}] * 6
    assert not L.trigger_fired(ok)[0]
    assert L.trigger_fired(bad)[0]
    assert not L.trigger_fired(bad[:6])[0]        # too few tasks


def test_router_learning_and_routing():
    doms = make_domains()
    rng = random.Random(9)
    bad = [(doms["dD"], doms["dD"].gen_task(rng, 6)[0]) for _ in range(3)]
    good = [(doms["dA"], doms["dA"].gen_task(rng, 6)[0]) for _ in range(3)]
    router = L.learn_router(bad, good)
    assert router is not None and router["feature"] == "AUDIT_T"
    op = ("ROUTE", router["feature"], router["threshold"], BASELINE, A3LIKE)
    rD = L.run_operator(*bad[0], op, 400_000)
    rA = L.run_operator(*good[0], op, 400_000)
    assert rD["routed_to"] == "fallback" and rA["routed_to"] == "operator"


def test_mutants_deterministic_and_novel():
    m1 = L.mutants(A3LIKE)
    m2 = L.mutants(A3LIKE)
    assert [serial(p) for p in m1] == [serial(p) for p in m2]
    assert serial(A3LIKE) not in {serial(p) for p in m1}


def test_learner_import_boundary():
    """learner.py must not import domains nor reference the ceiling constant."""
    tree = ast.parse(open(os.path.join(ROOT, "learner.py")).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {n.name.split(".")[0] for n in node.names} & {"domains"}
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] != "domains"
        elif isinstance(node, ast.Name):
            assert node.id != "A3"
