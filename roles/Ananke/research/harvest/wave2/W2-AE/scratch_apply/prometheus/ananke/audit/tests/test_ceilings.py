"""audit.ceilings: the unified ceiling API keeps every known-answer equality its source authors proved.

  H-PLANT lc_census          lightcone(opt) and joint(terms=()) reproduce lc_census.json exactly (W2-T 60/60,
                             W2-U KA1 165/165, W2-P KA 18/18 on the same seeds)
  W2-P / W2-U recorded       joint reproduces the recorded RELAY / MAJ (W2-P) and XOR / FLIP (W2-U) ceilings
  W2-T exact wake            lightcone(exact) on the held set reproduces W2-T and is never exceeded by a recorded
                             SIGNAL (the full 166-cell check is W2-AE dev/probe_sig_all.py: 0 mismatches, 0
                             violations; here the 8 tightest cells where exact wake is strictly tighter)
  W2-J lc2                   mc reproduces lc2.json bit for bit (same seeds, same RNG path); the deterministic limit
                             equals the light cone trial by trial; latency beyond the readout gives f = 0
  W2-S epidemic              epidemic reproduces epidemic_bound.json (20 / 20)
  W2-P KA2                   closed forms .788 / .837 / .875 / .98
"""
from __future__ import annotations

import numpy as np
import pytest

from prometheus.ananke import assays, envs, topology
from prometheus.ananke.audit import ceilings as CL
from prometheus.ananke.audit.tests import _data as D
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
from prometheus.ananke.search import HELD_NS

H = "roles/Ananke/research/harvest/"
LC = H + "H-PLANT/out/lc_census.json"
SCORE_NS = 0x48504C54                       # H-PLANT hp_common.SCORE_NS


def cell(cid):
    r = D.by_id()[cid]
    return r, Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])


def test_closed_forms_W2P_KA2():
    pc = 1 - 0.25
    assert round(sum(CL.poisson_binom([pc] * 5)[i] * CL.maj_bayes(i, 0.3) for i in range(6)), 3) == 0.788
    assert round(CL.maj_bayes(5, 0.3), 3) == 0.837
    assert CL.maj_bayes(0, 0.3) == 0.5 and CL.maj_bayes(2, 0.3) == pytest.approx(0.7 ** 2 + 0.7 * 0.3)
    assert CL.value_table(envs.EnvSpec(family="XOR", d=3, delta=8, trials=12)) == [0.5, 0.5, 1.0]
    # RELAY single sensor, async p, cue_len 2, no transport delay: 1 - .5 (1-p)^2
    for p, want in ((0.5, 0.875), (0.8, 0.98)):
        assert 0.5 + 0.5 * (1 - (1 - p) ** 2) == pytest.approx(want)


@D.need(D.REPO / LC, D.ROWS)
def test_lightcone_and_joint_terms_off_reproduce_lc_census():
    lc = D.load_json(LC)["rows"]
    g = np.random.default_rng(3)
    pick = [lc[i] for i in g.choice(len(lc), 8, replace=False)] + [x for x in lc if x["bound"] < 0.9][:8]
    assert {x["family"] for x in pick} >= {"XOR", "RELAY"} and {x["update_mode"] for x in pick} == {"sync", "async"}
    seeds = assays.world_seeds(SCORE_NS, 64)
    for x in pick:
        _, ph, env = cell(x["cell"])
        a = CL.lightcone(ph, env, seeds)
        j = CL.joint(ph, env, seeds, terms=())
        assert a["bound"] == pytest.approx(x["bound"], abs=1e-12), x
        assert j["lc"] == pytest.approx(x["bound"], abs=1e-12) and j["joint"] == pytest.approx(x["bound"], abs=1e-12)
    # MUST-FAIL: a cell with bound < 1 under a latency that cannot reach is pushed to exactly .5
    x = next(x for x in pick if x["family"] == "RELAY" and x["bound"] > 0.5)
    _, ph, env = cell(x["cell"])
    assert CL.lightcone(ph.replace(lat_base=env.delta + 40), env, seeds)["bound"] == 0.5


@D.need(D.REPO / H / "wave2/W2-P/out/task2_timing.json", D.ROWS)
def test_joint_reproduces_W2P_relay_and_maj():
    rows = [o for o in D.load_json(H + "wave2/W2-P/out/task2_timing.json")["rows"] if o["update_mode"] == "async"]
    pick = [o for o in rows if o["family"] == "MAJ" and o["ceil_joint"] < 0.8][:2] + \
        [o for o in rows if o["family"] == "RELAY" and o["ceil_joint"] < 0.99][:2]
    assert len(pick) == 4
    for o in pick:
        _, ph, env = cell(o["cell"])
        j = CL.joint(ph, env, assays.world_seeds(H_int(0x57325050, int(o["cell"][:8], 16)), 128))
        for k in ("lc", "cue", "joint"):
            assert j[k] == pytest.approx(o["ceil_" + k], abs=1e-9), (o["cell"], k)
        assert j["joint"] <= j["lc"] + 1e-12            # adding loss terms can only lower a ceiling


@D.need(D.REPO / H / "wave2/W2-U/out/task1_xor_flip.json", D.ROWS)
def test_joint_reproduces_W2U_xor_and_flip():
    rows = [o for o in D.load_json(H + "wave2/W2-U/out/task1_xor_flip.json")["rows"]
            if o["update_mode"] == "async" and o["ceil"]["joint"] < 0.999]
    pick = [o for o in rows if o["family"] == "FLIP"][:2] + [o for o in rows if o["family"] == "XOR"][:2]
    assert len(pick) == 4
    for o in pick:
        _, ph, env = cell(o["cell"])
        j = CL.joint(ph, env, assays.world_seeds(H_int(0x57325555, int(o["cell"][:8], 16)), 128))
        for k, v in o["ceil"].items():
            if k != "n_trials":
                assert j[k] == pytest.approx(v, abs=1e-9), (o["cell"], k)
        if env.family == "FLIP":
            assert j["copy_block"] <= j["joint_block"] <= j["joint_episode"] <= j["lc"] + 1e-12


@D.need(D.REPO / H / "wave2/W2-T/out/lcwake_sig_b0of1.json", D.ROWS)
def test_exact_wake_reproduces_W2T_and_no_signal_exceeds_it():
    sig = D.load_json(H + "wave2/W2-T/out/lcwake_sig_b0of1.json")["rows"]
    tighter = [o for o in sig if o["held_exact"]["bound"] < o["held_opt"]["bound"] - 1e-9]
    pick = sorted(tighter, key=lambda o: o["held_exact"]["bound"] - o["held_acc"])[:8]
    assert len(pick) == 8
    for o in pick:
        r, ph, env = cell(o["cell"])
        hs = assays.world_seeds(H_int(r["search_seed"], HELD_NS), r["search"]["M_held"])
        e = CL.lightcone(ph, env, hs, wake="exact")
        assert e["bound"] == pytest.approx(o["held_exact"]["bound"], abs=1e-12)
        assert r["labels"]["SIGNAL"] and r["result"]["held"]["acc"] <= e["bound"] + 1e-12      # 0 violations
        assert e["bound"] < CL.lightcone(ph, env, hs, wake="opt")["bound"]                     # strictly tighter


@D.need(D.REPO / H / "wave2/W2-J/out/lc2.json", D.ROWS)
def test_mc_reproduces_lc2_and_deterministic_limit_equals_lightcone():
    lc2 = {o["cell"]: o for o in D.load_json(H + "wave2/W2-J/out/lc2.json")["rows"]}
    seeds = assays.world_seeds(0x57324A53 + 7, 32)             # W2-J WJ_NS + 7, M = 32, R = 4, seed 0
    for cid in ("89a6a9cdf834c4e3", "0e99a4bb"):
        cid = next(c for c in lc2 if c.startswith(cid))
        _, ph, env = cell(cid)
        m = CL.mc(ph, env, seeds, reps=4, rng_seed=0)
        assert m["f_opt"] == lc2[cid]["f_opt"] and m["bound"] == pytest.approx(lc2[cid]["acc_ub"], abs=1e-12)
    xs = [r for r in D.rows() if r["env"]["family"] == "XOR" and r["kind"] == "evolve"
          and r["physics"]["topology"] != "global"]
    g = np.random.default_rng(1)
    n = bad = 0
    s8 = assays.world_seeds(0x57324A53 + 7, 8)
    for r in xs[::max(1, len(xs) // 4)][:4]:
        ph = Physics.from_dict(r["physics"]).replace(loss=0.0, dup=0.0, dest_mode="all", update_mode="sync",
                                                     lat_jitter=0)
        env = envs.EnvSpec(**r["env"])
        lcp = CL.lightcone(ph, env, s8, per_trial=True)
        ep = envs.build(ph, env, s8)
        sidx, ridx = ep.schedule.sense_idx.numpy(), ep.schedule.read_idx.numpy()[:, 0]
        nbr, dist = topology.build(ph)
        for wi, b in enumerate(range(0, 8, 2)):
            for k in range(env.trials):
                i = CL.mc_trial(ph, env, [int(x) for x in sidx[b][:2]], int(ridx[b]), k * env.period(), g, nbr,
                                dist, "all")
                n += 1
                bad += bool(i.all()) != bool(lcp["per_trial_ok"][wi, k].all())
    assert n >= 150 and bad == 0
    # MUST-FAIL: latency 40 (beyond every readout) -> nothing arrives
    r = xs[0]
    ph = Physics.from_dict(r["physics"]).replace(lat_base=40, lat_jitter=0)
    assert CL.mc(ph, envs.EnvSpec(**r["env"]), assays.world_seeds(1, 4), reps=1)["f_opt"] == 0.0


@D.need(D.REPO / H / "wave2/W2-S/out/epidemic_bound.json", D.ROWS)
def test_epidemic_reproduces_W2S():
    rows = D.load_json(H + "wave2/W2-S/out/epidemic_bound.json")
    assert len(rows) == 20
    for o in rows:
        _, ph, env = cell(o["cell"])
        b = CL.epidemic(ph, env)
        assert round(b["bound"], 4) == o["acc_bound"] and round(b["q_max"], 4) == o["q_max"]
    with pytest.raises(ValueError):
        CL.epidemic(Physics.from_dict({**D.by_id()[rows[0]["cell"]]["physics"], "topology": "ring"}), env)


@D.need(D.ROWS)
def test_dispatcher_and_tightest():
    r = next(r for r in D.rows() if r["kind"] == "evolve" and r["env"]["family"] == "FLIP"
             and r["physics"]["update_mode"] == "async" and r["physics"]["topology"] == "global")
    ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(SCORE_NS, 16)
    allc = CL.ceilings(ph, env, seeds)
    assert set(allc) >= {"lightcone", "lightcone_exact", "joint", "epidemic", "tightest"}
    det, exp_ = allc["tightest"]["deterministic"], allc["tightest"]["expectation"]
    assert det[0] in ("lightcone", "lightcone_exact") and exp_[1] <= det[1]
    assert CL.ceiling(ph, env, seeds, model="lightcone")["bound"] == allc["lightcone"]["bound"]
    with pytest.raises(ValueError):
        CL.ceiling(ph, env, None, model="joint")
    with pytest.raises(ValueError):
        CL.ceiling(ph, env, seeds, model="lc3")
