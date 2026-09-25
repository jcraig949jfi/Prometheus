import numpy as np

from ensorain.e1.world import World1
from ensorain.e1 import mem as M
from ensorain.e1p5.core import compress_tt, compress_lowrank, effective_ranks, replay, r2_ho, run_one


def test_compress_exact_tt_is_lossless_at_true_size():
    w = World1(0, 7)
    inj = M.inject_tt(w, 192)  # exact, ranks (3,3,3)
    big = M.TTAls(384, order=inj.order, ranks=(5, 5, 3))
    for k in range(4):  # embed the exact TT in a larger-rank TT (zero padding)
        big.tt.cores[k][...] = 0.0
        a, n, b = inj.tt.cores[k].shape
        big.tt.cores[k][:a, :, :b] = inj.tt.cores[k]
    assert effective_ranks(big.tt) == [3, 3, 3]
    c = compress_tt(big, 192)
    assert M.audit(c, 192) <= 192
    assert r2_ho(w, c) > 0.999


def test_compress_never_reads_truth():
    import inspect
    from ensorain.e1p5 import core
    src = inspect.getsource(core.compress_tt) + inspect.getsource(core.compress_lowrank)
    assert "world" not in src and ".x" not in src


def test_replay_oracle_all_correct():
    w = World1(0, 8)
    r = replay(w, M.Oracle(0, w.x), w.events())
    assert r["ok_L2"] == r["n_L2"] > 0


def test_lowrank_compress_shapes():
    m = M.LowRank(384, R=3)
    c = compress_lowrank(m, 256)
    assert c.R == 2 and M.audit(c, 256) == 256


def test_run_one_emits_curve():
    r = run_one(dict(arm="TT_TUNED", cap=384, inst_seed=9, org_seed=0,
                     cfg=dict(lam=30, sweeps=2, init_scale=0.5, ranks=[5, 5, 3], order=[0, 1, 2, 3])))
    assert r["status"] == "OK" and len(r["compress_curve"]) >= 5
    assert r["workspace_floats"] == 4096
