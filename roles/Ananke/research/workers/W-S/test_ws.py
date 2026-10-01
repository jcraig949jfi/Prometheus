"""KA-B bookkeeping tests for W-S (synthetic, no engine runs)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import analyze as A

# entries: (te, arr, v, jit, dist); readout a = 9, source s = 0, t0 = 10, tau = 15, ro = 18
A_, S_, T0, TAU, RO = 9, 0, 10, 15, 18


def test_held_direct_is_S():
    pidx = {A_: {(11, 15, S_, 1, 3)}}
    f = A.features(pidx, A_, S_, T0, TAU, RO)
    assert f["P3_cone"] == "S" and f["P1_first"] == "S" and f["P2_dflight"] == "S"
    assert f["first_jit_cross"] == 0


def test_inflight_direct_is_C_and_jitter_cross():
    pidx = {A_: {(11, 16, S_, 1, 3)}}          # without jitter it would arrive at 15 = tau
    f = A.features(pidx, A_, S_, T0, TAU, RO)
    assert f["P3_cone"] == "C" and f["P1_first"] == "C" and f["P2_dflight"] == "C"
    assert f["first_jit_cross"] == 1 and f["first_from_source"] == 1


def test_straddle_is_M_and_share():
    pidx = {A_: {(11, 15, S_, 0, 3), (11, 16, S_, 1, 3), (11, 17, 1, 1, 2)}}
    f = A.features(pidx, A_, S_, T0, TAU, RO)
    assert f["P3_cone"] == "M" and f["P5_dleaf"] == "M" and f["P6_share"] == "C"
    assert f["first_sib_split"] == 1


def test_relay_after_tau_recurses():
    # relay 5 emits at 16 (> tau) to a; it got the cue in flight (arr 16 > tau) -> C
    pidx = {A_: {(16, 18, 5, 0, 1)}, 5: {(12, 16, S_, 1, 2)}}
    assert A.features(pidx, A_, S_, T0, TAU, RO)["P3_cone"] == "C"
    # same relay, cue already held at tau -> S
    pidx = {A_: {(16, 18, 5, 0, 1)}, 5: {(12, 14, S_, 0, 2)}}
    assert A.features(pidx, A_, S_, T0, TAU, RO)["P3_cone"] == "S"
    # relay with no cue-bearing input: its difference was site-held -> S
    pidx = {A_: {(16, 18, 5, 0, 1)}}
    assert A.features(pidx, A_, S_, T0, TAU, RO)["P3_cone"] == "S"


def test_pre_trial_and_late_copies_ignored():
    pidx = {A_: {(8, 16, S_, 0, 3), (17, 19, S_, 0, 3)}}      # emitted before t0 / arrives after ro
    f = A.features(pidx, A_, S_, T0, TAU, RO)
    assert f["P3_cone"] == "U" and f["P1_first"] == "U"


def test_accuracy_strict_and_shuffle():
    pat = np.array(["S", "C"] * 50 + ["N"] * 10)
    pred = np.array(["S", "C"] * 50 + ["S"] * 10)
    pair = np.arange(110) // 2
    r = A.accuracy(pred, pat, pair)
    assert r["n"] == 100 and r["acc"] == 1.0
    pred2 = pred.copy(); pred2[:10] = "M"
    assert A.accuracy(pred2, pat, pair)["acc"] == 0.9          # M counts as an error
    sh = A.shuffled(pred, pat, seed=0)
    assert abs(A.accuracy(sh, pat, pair)["acc"] - 0.5) < 0.15  # must-fail input drops to chance


def test_loo_pair_majority():
    pat = np.array(["S", "S", "S", "C", "C", "C", "C"])
    pair = np.array([0, 0, 0, 1, 1, 1, 1])
    assert list(A.loo_pair_majority(pat, pair)) == ["S", "S", "S", "C", "C", "C", "C"]
    pat = np.array(["S", "C"])
    assert list(A.loo_pair_majority(pat, np.array([0, 0]))) == ["C", "S"]
