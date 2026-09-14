"""N4 tests. The numpy tests run everywhere (gw-venv suite); the GPU tests run only where cuquantum + a CUDA
device import (WSL ~/lab/nv-venv-t) and skip elsewhere."""
import numpy as np
import pytest

from primordial.brain import genomes as gm
from primordial.nv.tensornet import tt_cutn as tn


def _genome(D=5, A=8, n=300, seed=0):
    fam = gm.TTDigits(D=D, A=A)
    rng = np.random.default_rng(seed)
    g1 = fam.one(fam.init(rng, 1), 0)
    obs = rng.integers(0, 65536, size=(n, D), dtype=np.int64)
    return fam, g1, obs


def test_network_operands_match_oracle_via_numpy_einsum():
    fam, g1, obs = _genome(D=3, n=200)
    got = np.einsum(*tn.network_operands(g1, obs), optimize="greedy")
    r = tn.compare_to_oracle(fam, g1, obs, got)
    assert r["n_clear"] > 150 and r["argmax_mismatch_clear"] == 0
    assert r["max_abs_err_rownorm_all"] < 1e-9


def test_numpy_einsum_stride_cheat_is_caught():
    fam, g1, obs = _genome(D=3, n=200, seed=1)
    bad = np.einsum(*tn.network_operands(g1, obs, stride=2), optimize="greedy")
    assert tn.compare_to_oracle(fam, g1, obs, bad)["argmax_mismatch_clear"] > 30


def _gpu():
    pytest.importorskip("cupy")
    try:
        tn._cq()
    except ImportError:
        pytest.skip("cuquantum not importable")
    import cupy as cp
    try:
        cp.cuda.runtime.getDeviceCount()
    except Exception:
        pytest.skip("no CUDA device")


@pytest.mark.parametrize("D", [5, 8])
def test_cutensornet_contract_matches_oracle_and_cheat_is_caught(D):
    _gpu()
    fam, g1, obs = _genome(D=D, n=400, seed=D)
    r = tn.compare_to_oracle(fam, g1, obs, tn.contract_logits(g1, obs))
    assert r["n_clear"] > 350 and r["argmax_mismatch_clear"] == 0
    assert r["max_abs_err_rownorm_all"] < 1e-9
    bad = tn.compare_to_oracle(fam, g1, obs, tn.contract_logits(g1, obs, stride=2))
    assert bad["argmax_mismatch_clear"] > 50


def test_n4_oracle_quick_receipt(tmp_path):
    _gpu()
    from primordial.nv.tensornet import n4_oracle
    out = tmp_path / "rows.jsonl"
    assert n4_oracle.main(["--quick", "--out", str(out), "--status", "dev"]) == 0
    import json
    rows = [json.loads(x) for x in out.read_text().splitlines()]
    summ = rows[-1]
    assert summ["kind"] == "summary" and summ["honest_argmax_mismatch_clear"] == 0
    assert summ["cheat_cells_caught"] == summ["cheat_cells"] == 4
    assert all(r["status"] in ("dev", "cheat") for r in rows[1:-1])


def test_planned_network_reused_across_genomes():
    _gpu()
    fam, g1, obs = _genome(D=5, n=256, seed=11)
    plan = tn.PlannedTT(g1, obs)
    try:
        assert plan.plan_s > 0
        for s in range(3):
            _, g2, obs2 = _genome(D=5, n=256, seed=100 + s)
            r = tn.compare_to_oracle(fam, g2, obs2, plan.run(g2, obs2))
            assert r["argmax_mismatch_clear"] == 0 and r["max_abs_err_rownorm_all"] < 1e-9
    finally:
        plan.close()
