"""E-R7-2: lockstep evaluation reproduces G's sequential baseline runs exactly; the adoption decision is code."""
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


def _rows(oracle="PASS", ratios=(1.4,), fail=False, oom=False):
    rows = [{"kind": "oracle", "exactness": oracle, "world": "w13", "pressure": "train8_held64"}]
    rows += [{"kind": "cell_ratio", "world": "w13", "pressure": f"p{i}", "ratio_gpu_over_best_cpu": v}
             for i, v in enumerate(ratios)]
    if fail:
        rows.append({"kind": "verdict", "verdict": "INSTRUMENT_FAIL"})
    if oom:
        rows.append({"kind": "device_oom", "world": "w13", "pressure": "train128_held64"})
    return rows


def test_decision_rule():
    assert G.decide(_rows())["decision"] == G.ADOPT
    assert G.decide(_rows(ratios=(1.25,)))["decision"] == G.ADOPT                 # >= is inclusive
    assert G.decide(_rows(ratios=(1.2499,)))["decision"] == G.REJECT
    assert G.decide(_rows(ratios=(1.5, 1.1)))["decision"] == G.REJECT              # every measured cell
    assert G.decide(_rows(oracle="FAIL"))["decision"] == G.REJECT
    assert G.decide(_rows(fail=True))["decision"] == G.REJECT
    assert G.decide(_rows(ratios=()))["decision"] == G.REJECT                      # nothing measured
    d = G.decide(_rows(oom=True))
    assert d["decision"] == G.ADOPT and d["device_oom_cells"] == ["w13 train128_held64"]
