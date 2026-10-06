"""AIM02 known-answer fixtures for the non-AIM richness instrument (order s7, s8).

Synthetic site-field trajectories (no Aether physics). Each fixture builds a (W+1, M) recording whose correct
readings are known by construction, runs Aether/V2B/AIM02/aim02_meter.analyze, and checks them. The AIM_BOOKKEEPING
fixture goes through aim02_run.record_columns to prove arg0 can never enter the primary channel.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "V2B", "AIM02"))
sys.path.insert(0, os.path.join(HERE, "..", "V2B", "AIM02"))
import aim02_meter as Mtr  # noqa: E402

W = 1024
M = 64


def rec(fn):
    seq = np.zeros((W + 1, M), dtype=np.uint8)
    for t in range(W + 1):
        for j in range(M):
            seq[t, j] = fn(t, j) % 256
    return seq


def allbins(out, key):
    return [r[key + "_mean"] for r in out["bins"] if r["columns"]]


def test_static():
    out = Mtr.analyze(np, rec(lambda t, j: j))
    assert out["columns_changing"] == 0 and out["columns_ge1"] == 0


def test_two_state_flicker():
    out = Mtr.analyze(np, rec(lambda t, j: 10 + 10 * ((t + j) % 2)))
    assert out["columns_changing"] == M
    assert allbins(out, "n_ch") == [W]                      # every tick a change, one activity bin
    assert allbins(out, "U") == [2.0]
    assert abs(allbins(out, "upc")[0] - 1 / W) < 1e-12
    assert abs(allbins(out, "tpc")[0] - 2 / W) < 1e-12       # 10->20 and 20->10
    assert allbins(out, "n16")[0] <= 1 / W + 1e-12           # only possibly the very first event
    assert allbins(out, "n64")[0] <= 1 / W + 1e-12
    r = [b for b in out["bins"] if b["columns"]][0]
    assert r["return_q"] == [2.0, 2.0, 2.0]                  # concentrated recurrence


def test_k_state_flicker():
    rng = np.random.default_rng(1)
    cat = rng.integers(0, 256, (M, 5))
    seq_idx = rng.integers(0, 5, (W + 1, M))
    out = Mtr.analyze(np, rec(lambda t, j: cat[j, seq_idx[t, j]]))
    assert max(allbins(out, "U")) <= 5
    assert max(allbins(out, "n64")) < 0.01                    # all 5 states are always held within 64 ticks
    assert max(allbins(out, "dr2")) < 0.01                    # catalogue saturated early -> no late discovery


def test_recent_revisit_separates_n16_from_n64():
    # cycle through 32 distinct values, each held 1 tick: a value recurs every 32 ticks (> 16, < 64)
    out = Mtr.analyze(np, rec(lambda t, j: 3 * ((t // 1) % 32) + j))
    n16, n64 = allbins(out, "n16")[0], allbins(out, "n64")[0]
    assert n16 > 0.95 and n64 < 0.05
    r = [b for b in out["bins"] if b["columns"]][0]
    assert r["return_q"][1] == 32.0


def test_expanding_catalog():
    # a new value every 4 ticks, never repeating within the window (W/4 = 256 values -> use values mod 256 with
    # W chosen so no repeats: 1024/4 = 256 distinct)
    out = Mtr.analyze(np, rec(lambda t, j: (t // 4 + j) % 256))
    assert allbins(out, "n64")[0] > 0.99 and allbins(out, "n16")[0] > 0.99
    assert allbins(out, "upc")[0] > 0.99
    assert allbins(out, "dr2")[0] > 0.99                     # still discovering in the second half


def test_aim_bookkeeping_never_enters_primary():
    import aim02_run as RUN
    rng = np.random.default_rng(3)
    n = 8
    s0 = [rng.integers(0, 256, (n, n), dtype=np.uint8) for _ in range(5)]
    frames = []
    for t in range(W + 1):
        s = [f.copy() for f in s0]
        s[1] = ((s0[1].astype(np.int64) + 7 * t) % 256).astype(np.uint8)   # arg0 changes arbitrarily
        s[4] = ((s0[4].astype(np.int64) + t) % 256).astype(np.uint8)       # energy too
        frames.append(RUN.record_columns(np, s, step=1))
    out = Mtr.analyze(np, np.stack(frames))
    assert out["columns_changing"] == 0 and out["columns_ge1"] == 0


def test_positive_control_rule_separates_expanding_from_flicker():
    """Positive control: the frozen comparison must score an expanding catalogue richer than K-state flicker,
    and K-state flicker equivalent to itself, on every primary richness dimension."""
    rng = np.random.default_rng(5)
    Mw = 400
    cat = rng.integers(0, 256, (Mw, 4))

    def mk(fn):
        seq = np.zeros((W + 1, Mw), dtype=np.uint8)
        for t in range(W + 1):
            seq[t] = fn(t) % 256
        return seq
    # matched activity: both change on (almost) every tick
    flick = mk(lambda t: cat[np.arange(Mw), (t + np.arange(Mw)) % 4])
    flick2 = mk(lambda t: cat[np.arange(Mw), (t * 3 + np.arange(Mw)) % 4])
    expand = mk(lambda t: (t + 37 * np.arange(Mw)) % 256)
    a_f, a_f2, a_e = (Mtr.analyze(np, x)["bins"] for x in (flick, flick2, expand))
    rich = Mtr.compare_conds(a_e, a_f)
    same = Mtr.compare_conds(a_f2, a_f)
    for k in ("upc", "tpc", "n64"):
        assert rich[k]["diff"] > 0.2, (k, rich[k])
        assert abs(same[k]["diff"]) < 0.01, (k, same[k])


def test_positive_control_through_the_frozen_decision_rule():
    """Order s8: the frozen DECISION function (aim02_reduce.decide, with the frozen RULES.json once it exists) must
    return RICHNESS_SUPPORTED for an expanding catalogue against flicker comparators, and FLICKER_EQUIVALENT for
    flicker against flicker."""
    import json as _json
    import aim02_reduce as RED
    rules_path = os.path.join(HERE, "..", "V2B", "AIM02", "RULES.json")
    rules = _json.load(open(rules_path)) if os.path.exists(rules_path) else {
        "margins": {"NOVELTY": 0.05, "REPERTOIRE": 0.05, "DISCOVERY": 0.05, "TRANSITIONS": 0.05, "RECURRENCE": 1.5},
        "seeds_min": 2, "densities_min": 2, "coverage_min": 0.5}
    rng = np.random.default_rng(9)
    Mw = 300

    def mk(fn):
        seq = np.zeros((W + 1, Mw), dtype=np.uint8)
        for t in range(W + 1):
            seq[t] = fn(t) % 256
        return seq

    def flick(seed):
        r = np.random.default_rng(seed)
        cat = r.integers(0, 256, (Mw, 4))
        idx = r.integers(0, 4, (W + 1, Mw))
        return mk(lambda t: cat[np.arange(Mw), idx[t]])

    def expand(seed):
        off = np.random.default_rng(seed).integers(0, 256, Mw)
        return mk(lambda t: (t // 4 + off))   # a new value every 4 ticks; 256 values over the window

    seeds = range(int(rules["seeds_min"]))
    def units(treat):
        u = {}
        for k in seeds:
            for c in ("L1D25", "L1D50", "L1D75"):
                u[(c, k, W, W, False)] = {"primary": Mtr.analyze(np, treat(100 + k))}
            u[("C1FREE", k, W, W, False)] = {"primary": Mtr.analyze(np, flick(200 + k))}
            u[("C2RICH", k, W, W, False)] = {"primary": Mtr.analyze(np, flick(300 + k))}
        return u
    pos = RED.decide(RED.contrasts(units(expand), W, W), rules)
    neg = RED.decide(RED.contrasts(units(flick), W, W), rules)
    assert pos["disposition"] == "RICHNESS_SUPPORTED", pos
    assert neg["disposition"] == "FLICKER_EQUIVALENT", neg
