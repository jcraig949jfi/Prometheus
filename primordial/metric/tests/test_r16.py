"""Operator 16 (SWARM_R4 s9): family-seeded runs, pooled 32x4 values with refusals, and the R16 jobs."""
from __future__ import annotations

import json
import pathlib
import pickle

import numpy as np
import pytest

from primordial.metric import baseline as B
from primordial.metric import floors as F
from primordial.metric import invariant as I
from primordial.metric import r16 as R
from primordial.metric import readout as RO
from primordial.metric.ci import median_ci
from primordial.qd import e4_run as E4
from primordial.qd.archive import load_elites
from primordial.tests._live import live_url


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for pat in ("pm:qd:g-r16-*", "pm:qd:g-r4-base-*", "pm:qd:g-r4-inv-*"):
        for k in c.scan_iter(pat, count=5000):
            c.delete(k)


def test_family_seeds_follow_d_r4_2_and_4200_is_the_v1_m2_stream():
    assert B.seeds_of(13, 128, 5, None) == B.seeds_of(13, 128, 5, 4200) == ([4200, 5, 13, 128], [4201, 5, 13, 128])
    assert B.seeds_of(13, 128, 5, 3303) == ([3303, 5, 13, 128], [3304, 5, 13, 128])
    assert I.seeds_of(13, 8, 2, None) == ([4100, 2, 13, 8], [4101, 2, 13, 8])            # P0 learner stream kept
    assert I.seeds_of(13, 8, 2, 2101) == ([2101, 2, 13, 8], [2102, 2, 13, 8])
    assert B.run_key(13, "p", 1) == "g-r4-base-w13-p-r1" and B.run_key(13, "p", 1, 5501) == "g-r16-base-w13-p-f5501-r1"
    assert B.FAMILIES == I.FAMILIES == R.FAMILIES == (4200, 2101, 3303, 5501)


def test_baseline_family_4200_reproduces_the_v1_run_and_carries_both_readouts(r, tmp_path):
    old = B.baseline_run(r, 4, "train8_held64", 3, gens=3, batch=8, elites_dir=tmp_path / "v1")
    new = B.baseline_run(r, 4, "train8_held64", 3, gens=3, batch=8, elites_dir=tmp_path / "r16", rng_family=4200)
    assert new["held64_per_seed"] == old["held64_per_seed"] and new["top_sha256"] == old["top_sha256"]
    assert new["rng_family"] == 4200 and "rng_family" not in old and new["readout"] == RO.NAME
    assert pathlib.Path(new["elites"]).name != pathlib.Path(old["elites"]).name                  # never overwrites v1
    from primordial.qd import e7_run as E7
    g7 = E7.G7(4, "linear")
    top16 = B.top_raw(RO.elites_of(load_elites(new["elites"])), g7.glen)
    assert new["held64_legacy_top16"] == B.fused_per_seed(g7, top16, F.HELD64)
    other = B.baseline_run(r, 4, "train8_held64", 3, gens=3, batch=8, elites_dir=tmp_path / "o", rng_family=2101)
    assert other["top_sha256"] != new["top_sha256"]
    assert B.reread(4, new["elites"])["held64_per_seed"] == new["held64_per_seed"]              # one reader


def _runs(values_by_family: dict, readout=RO.NAME):
    return [{"rng_family": f, "run_seed": i, "held64_per_seed": float(v), "readout": readout, "world": "w1",
             "gen_seed": 1, "pressure": "p", "genome_bytes": 200, "budget_ok": True, "genomes": 1, "elites": f"e{f}{i}"}
            for f, vs in values_by_family.items() for i, v in enumerate(vs)]


def test_pooled_stats_order_median_ci_and_every_refusal():
    vals = {5501: range(30, 38), 4200: range(0, 8), 3303: range(20, 28), 2101: range(10, 18)}
    s = B.pooled_stats(_runs(vals))
    ordered = [float(v) for f in (4200, 2101, 3303, 5501) for v in vals[f]]
    assert list(s["held64_by_run"].values()) == ordered and list(s["held64_by_run"])[:2] == ["4200|0", "4200|1"]
    assert s["median"] == float(np.median(ordered)) and s["ci95"] == list(median_ci(ordered))
    assert s["n_runs"] == 32 and s["families"] == [2101, 3303, 4200, 5501] and s["n_per_family"]["3303"] == 8
    with pytest.raises(ValueError, match="BASELINE_N"):
        B.pooled_stats(_runs({4200: range(8), 2101: range(8), 3303: range(8), 5501: range(7)}))          # 31
    with pytest.raises(ValueError, match="BASELINE_N"):
        B.pooled_stats(_runs({4200: range(11), 2101: range(11), 3303: range(10)}))                        # 3 families
    with pytest.raises(ValueError, match="BASELINE_N"):
        B.pooled_stats(_runs({4200: range(29), 2101: range(1), 3303: range(1), 5501: range(1)}))          # 29+1+1+1
    dup = _runs(vals)
    dup[1]["run_seed"] = 0
    with pytest.raises(ValueError, match="duplicate"):
        B.pooled_stats(dup)
    mixed = _runs(vals)
    mixed[0]["readout"] = RO.LEGACY
    with pytest.raises(ValueError, match="mix readouts"):
        B.pooled_stats(mixed)
    assert B.pooled_summary(_runs(vals))["elites"]["5501|7"] == "e55017"


def test_random_policy_family_streams():
    spec = E4.Spec(13)                      # w13: uniform random scores well above 0 (stage 1 median 58.44), so streams differ
    seeds = F.HELD64[:4]
    assert np.array_equal(F.random_scores(spec, seeds, [0, 1]), F.random_scores(spec, seeds, [0, 1], rng_family=None))
    a = F.random_scores(spec, seeds, range(4), rng_family=3303)
    assert np.array_equal(a, F.random_scores(spec, seeds, range(4), rng_family=3303))
    assert not np.array_equal(a, F.random_scores(spec, seeds, range(4), rng_family=5501))
    pooled = R.random_pooled(4, families=(4200, 2101), policy_seeds=range(2))
    assert pooled["n_runs"] == 4 and pooled["families"] == [2101, 4200] and pooled["readout"] == "policy"


def test_learner_family_run_reads_top1_train_and_keeps_top16(r, tmp_path):
    row = I.learner_run(r, 4, "train8_held64", 1, gens=3, batch=8, elites_dir=tmp_path, rng_family=5501)
    spec = E4.Spec(4)
    doc = load_elites(row["elites"])
    want, sha = I.top1_per_seed(spec, RO.elites_of(doc), F.HELD64)
    assert row["readout"] == RO.NAME and row["top"] == 1 and row["held64_per_seed"] == want and row["top_sha256"] == sha
    legacy = I.learner_run(r, 4, "train8_held64", 1, gens=3, batch=8, elites_dir=tmp_path / "leg")
    assert "readout" not in legacy and legacy["top_sha256"] != sha
    assert row["held64_legacy_top16"] >= 0 and row["rng_family"] == 5501


class Ctx:
    def __init__(self, pause_after=None):
        self.rows, self.ck, self.pause_after, self.polls = [], None, pause_after, 0

    def emit(self, row):
        self.rows.append(json.loads(json.dumps(row)))

    def load_checkpoint(self):
        return self.ck

    def checkpoint(self, st):
        self.ck = pickle.loads(pickle.dumps(st))

    def should_pause(self):
        self.polls += 1
        return self.pause_after is not None and self.polls >= self.pause_after

    def pause(self, st):
        self.checkpoint(st)
        raise RuntimeError("paused")


VOL = ("qd_wall_s", "elites", "wall_s", "oracle_held8", "gate", "wforge_episodes_per_s")


def strip(x):
    return {k: v for k, v in x.items() if k not in VOL}


def test_floors_job_rows_det_check_and_resume(r, tmp_path, monkeypatch):
    monkeypatch.setattr(I, "PAUSE_EVERY", 2)
    kw = dict(gen_seeds=[3], families=(4200, 2101), run_seeds=(0, 1), learner_gens=3, learner_batch=8,
              archive_url=live_url(), elites_dir=str(tmp_path))
    ref = Ctx()
    R.floors_job(ref, **kw)
    kinds = [x["kind"] for x in ref.rows]
    assert kinds == ["r16_det"] * 2 + ["r16_random"] + ["run"] * 4 + ["floor_invariant_r16"] + ["floor_suite_r16"] * 2
    assert all(x["matches_stage1"] for x in ref.rows if x["kind"] == "r16_det")               # committed stage 1 w3
    s8, s128 = ref.rows[-2], ref.rows[-1]
    assert s8["learner"]["status"] == "run" and s8["learner"]["readout"] == RO.NAME and not s8["floor_is_bound"]
    assert s8["floor_stats"]["input_invariant_learner"]["n_runs"] == 4 and s128["floor_is_bound"]
    assert s8["floor_stats"]["uniform_random_median"]["families"] == [2101, 4200]
    ctx = Ctx(pause_after=3)
    with pytest.raises(RuntimeError):
        R.floors_job(ctx, **kw)
    ctx.pause_after = None
    R.floors_job(ctx, **kw)
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]


def test_baseline_job_pools_every_family_and_resumes(r, tmp_path, monkeypatch):
    monkeypatch.setattr(B, "PAUSE_EVERY", 2)
    kw = dict(cells=[[4, "train8_held64"]], families=(4200, 2101), run_seeds=(0, 1), gens=3, batch=8,
              archive_url=live_url(), elites_dir=str(tmp_path))
    ref = Ctx()
    R.baseline_job(ref, **kw)
    assert [x["kind"] for x in ref.rows] == ["run"] * 4 + ["baseline_r16"]
    assert [x["rng_family"] for x in ref.rows[:4]] == [4200, 4200, 2101, 2101]
    assert "oracle_held8" in ref.rows[0] and ref.rows[0]["oracle_held8"]["world"]["elites_failing"] == 0
    b = ref.rows[-1]
    assert b["n_runs"] == 4 and b["n_per_family"] == {"2101": 2, "4200": 2} and b["readout"] == RO.NAME
    ctx = Ctx(pause_after=3)
    with pytest.raises(RuntimeError):
        R.baseline_job(ctx, **kw)
    ctx.pause_after = None
    R.baseline_job(ctx, **kw)
    assert [strip(x) for x in ctx.rows] == [strip(x) for x in ref.rows]


def test_order_puts_w13_train128_first_then_gate_headroom():
    o = R.order_r16()
    assert o[0] == [13, "train128_held64"] and len(o) == 74 and len({tuple(c) for c in o}) == 74
    assert o[1] == [7, "train8_held64"]                               # the largest gate headroom in stage 1
