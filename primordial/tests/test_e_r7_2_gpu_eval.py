"""E-R7-2: lockstep evaluation reproduces G's sequential baseline runs exactly (elites and run rows); the backend decision
is code (A 1789505093129-0: fastest eligible backend iff >= 1.25x cpu_sequential on every measured cell)."""
from __future__ import annotations

import numpy as np
import pytest

from primordial.nv import r7_gpu_eval as G


def _redis():
    try:
        import redis
        r = redis.Redis.from_url(G.ARCHIVE_URL)
        r.ping()
        return r
    except Exception:
        return None


@pytest.mark.skipif(_redis() is None, reason="archive redis 6394 not reachable")
def test_numba_lockstep_elites_equal_sequential_baseline_runs(tmp_path):
    from primordial.metric import floors as F
    from primordial.qd import e7_run as E7
    r = _redis()
    fams, seeds, gens, batch = (4200, 2101), (0, 1), 4, 8
    g7 = E7.G7(13, "linear")
    ev = G.numba_evaluator(g7, len(fams) * len(seeds) * batch, F.PRESSURES["train8_held64"])
    lock = G.lockstep(r, 13, "train8_held64", ev, fams, seeds, gens, batch, tag="test", elites_dir=tmp_path / "l")
    seq = G.sequential(r, 13, "train8_held64", fams, seeds, gens, batch, elites_dir=str(tmp_path / "s"))
    assert set(lock["digests"]) == {"4200|0", "4200|1", "2101|0", "2101|1"}
    assert lock["digests"] == seq["digests"]


@pytest.mark.skipif(_redis() is None, reason="archive redis 6394 not reachable")
def test_lockstep_detects_a_planted_evaluator_defect(tmp_path):
    from primordial.metric import floors as F
    from primordial.qd import e7_run as E7
    r = _redis()
    g7 = E7.G7(13, "linear")
    ev = G.numba_evaluator(g7, 2 * 8, F.PRESSURES["train8_held64"])

    def off_by_one(g):
        fit, cells = ev(g)
        fit = np.asarray(fit).copy()
        fit[3] += 1
        return fit, cells
    seq = G.sequential(r, 13, "train8_held64", (4200,), (0, 1), 4, 8, elites_dir=str(tmp_path / "s"))
    bad = G.lockstep(r, 13, "train8_held64", off_by_one, (4200,), (0, 1), 4, 8, tag="test-bad", elites_dir=tmp_path / "b")
    assert bad["digests"] != seq["digests"]


@pytest.mark.skipif(_redis() is None, reason="archive redis 6394 not reachable")
def test_g_hook_rows_equal_baseline_run_rows_including_pause_resume(tmp_path):
    from primordial.metric import baseline as B
    r = _redis()
    fams, seeds, gens, batch = (4200, 3303), (0, 1), 5, 8
    want = {}
    for f in fams:
        for rs in seeds:
            row = B.baseline_run(r, 13, "train8_held64", rs, gens, batch, str(tmp_path / "seq"), None, None, f)
            want[B.run_key(13, "train8_held64", rs, f)] = row
    done = {B.run_key(13, "train8_held64", 0, 4200): want[B.run_key(13, "train8_held64", 0, 4200)]}
    calls = {"n": 0}

    def pause_once():
        calls["n"] += 1
        return calls["n"] == 1
    old = B.PAUSE_EVERY
    B.PAUSE_EVERY = 2
    try:
        out = G.baseline_runs_lockstep(r, 13, "train8_held64", fams, seeds, gens, batch, str(tmp_path / "lock"), done,
                                       should_pause=pause_once)
        assert out["rows"] == [] and out["paused"]["gen"] == 2
        out = G.baseline_runs_lockstep(r, 13, "train8_held64", fams, seeds, gens, batch, str(tmp_path / "lock"), done,
                                       should_pause=pause_once, state=out["paused"])
    finally:
        B.PAUSE_EVERY = old
    assert out["paused"] is None and len(out["rows"]) == 3                               # the done run is skipped
    skip = {"qd_wall_s", "elites", "search_cpu_s", "search_wall_s", "backend", "search_split"}
    for row in out["rows"]:
        ref = want[B.run_key(13, "train8_held64", row["run_seed"], row["rng_family"])]
        assert {k: v for k, v in row.items() if k not in skip} == {k: v for k, v in ref.items() if k not in skip}
        assert set(ref) - set(row) == set() and row["backend"] == "cpu_lockstep"


def _cell(world="w13", pressure="train8_held64", eligible=("cpu_sequential", "cpu_lockstep", "gpu_lockstep"), **ratio):
    base = {"cpu_sequential": 1.0, "cpu_lockstep": 1.0, "gpu_lockstep": 1.0}
    base.update(ratio)
    return {"kind": "cell_ratio", "world": world, "pressure": pressure, "eligible": list(eligible),
            "ratio_vs_cpu_sequential": {k: base[k] for k in eligible}}


def _oracles(cpu="PASS", gpu="PASS"):
    return [{"kind": "oracle", "backend": "cpu_lockstep", "exactness": cpu},
            {"kind": "oracle", "backend": "gpu_lockstep", "exactness": gpu}]


def test_decision_rule_best_exact_backend():
    d = G.decide(_oracles() + [_cell(cpu_lockstep=1.6, gpu_lockstep=1.3)])
    assert d["backend"] == "cpu_lockstep" and d["decision"] == G.REJECT                  # fastest eligible wins
    d = G.decide(_oracles() + [_cell(cpu_lockstep=1.3, gpu_lockstep=2.0)])
    assert d["backend"] == "gpu_lockstep" and d["decision"] == G.ADOPT
    assert G.decide(_oracles() + [_cell(cpu_lockstep=1.25)])["backend"] == "cpu_lockstep"  # >= inclusive
    assert G.decide(_oracles() + [_cell(cpu_lockstep=1.2499, gpu_lockstep=0.1)])["backend"] == "cpu_sequential"
    two = [_cell(cpu_lockstep=1.5, gpu_lockstep=3.0), _cell(pressure="train128_held64", cpu_lockstep=1.4, gpu_lockstep=1.1)]
    assert G.decide(_oracles() + two)["backend"] == "cpu_lockstep"                        # every measured cell
    assert G.decide(_oracles(gpu="FAIL") + [_cell(cpu_lockstep=1.0, gpu_lockstep=9.0)])["backend"] == "cpu_sequential"
    assert G.decide(_oracles(cpu="FAIL", gpu="FAIL") + [_cell(cpu_lockstep=9.0, gpu_lockstep=9.0)])["backend"] == "cpu_sequential"
    assert G.decide(_oracles())["backend"] == "cpu_sequential"                              # nothing measured
    d = G.decide(_oracles() + [_cell(eligible=("cpu_sequential", "cpu_lockstep"), cpu_lockstep=1.5),
                               {"kind": "device_oom", "world": "w13", "pressure": "train128_held64"}])
    assert d["backend"] == "cpu_lockstep" and d["device_oom_cells"] == ["w13 train128_held64"]
