"""KA-B bookkeeping tests for W-T (synthetic; no simulation except a plant genome decode)."""
import os
import pathlib
import sys

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import pytest

import wt
import summ

S, A, R = 10, 20, 30          # source, readout, relay site ids
TAU = 100


def cp(te, arr, v=S):
    return (te, arr, v, 0, 3)


def test_all_held_is_S():
    assert wt.p8_features({cp(96, 100), cp(96, 100)}, A, S, TAU)["P8_srcfirst"] == "S"


def test_all_flight_is_C():
    assert wt.p8_features({cp(96, 101), cp(96, 102)}, A, S, TAU)["P8_srcfirst"] == "C"


def test_split_is_M_and_P8any_C():
    r = wt.p8_features({cp(96, 100), cp(96, 101)}, A, S, TAU)
    assert r["P8_srcfirst"] == "M" and r["n1_held"] == 1 and r["n1_flight"] == 1
    assert list(wt.p8any_of(np.array(["M", "U", "S", "C"]))) == ["C", "S", "S", "C"]


def test_later_source_copies_and_relays_ignored():
    d = {cp(96, 100), cp(98, 103), cp(100, 104), cp(95, 101, v=R)}
    r = wt.p8_features(d, A, S, TAU)
    assert r["P8_srcfirst"] == "S" and r["te1_rel"] == -4


def test_no_source_copy_is_U():
    assert wt.p8_features({cp(95, 101, v=R)}, A, S, TAU)["P8_srcfirst"] == "U"
    assert wt.p8_features(set(), A, S, TAU)["P8_srcfirst"] == "U"


def test_te1_after_tau_literal_C():
    # literal W-S rule: te1 > tau is not special-cased -> all arrivals after tau -> C
    assert wt.p8_features({cp(102, 106)}, A, S, TAU)["P8_srcfirst"] == "C"


def test_p8all_uses_each_sources_first():
    d = {cp(96, 100, v=1), cp(98, 101, v=1), cp(97, 101, v=2)}
    assert wt.p8all_features(d, A, [1, 2], TAU) == "M"
    assert wt.p8all_features(d, A, [1], TAU) == "S"


def test_decide_thresholds():
    good = {"acc": 1.0, "ci99": (0.95, 1.0)}
    assert summ.decide(good, 0.30, {"acc": .9, "ci99": (.85, .95)})[0] == "REACHES"
    v, f = summ.decide({"acc": .95, "ci99": (.90, 1.0)}, 0.30, {"acc": .9, "ci99": (.85, .95)})
    assert v == "DOES NOT REACH" and f == ["P8 decisive lo99 <= .90"]      # lo99 must be strictly > .90
    assert summ.decide(good, 0.24, {"acc": .9, "ci99": (.85, .95)})[1] == ["coverage < .25"]
    assert summ.decide(good, 0.30, {"acc": .9, "ci99": (.80, .95)})[1] == ["P8any strict lo99 <= .80"]


def test_unit_accuracy_and_shuffle_mustfail():
    rng = np.random.default_rng(1)
    n = 400
    pat = rng.choice(["S", "C"], n)
    arr = {"ok_frozen": np.ones(n, int), "o": np.full(n, 4), "q": np.zeros(n, int), "pat_frozen": pat,
           "pair": np.arange(n) // 4, "P8": pat.copy(), "P8all": pat.copy()}
    for k in ("n_cue_a", "n_src_a", "n_src_first", "n_src_later", "n_relay_a", "n_relay_flight", "n_emit_src",
              "te1_rel"):
        arr[k] = np.zeros(n, int)
    r = summ.unit(arr, 4, 0, "frozen")
    assert r["P8_decisive"]["acc"] == 1.0 and r["verdict"] == "REACHES"
    assert abs(r["P8_decisive_shuffled"]["acc"] - 0.5) < 0.1          # must-fail input -> chance
    arr["P8"][:200] = "M"                                              # half abstain: coverage .5, P8any hurt
    r = summ.unit(arr, 4, 0, "frozen")
    assert abs(r["P8_coverage"] - 0.5) < 1e-9 and r["P8_decisive"]["acc"] == 1.0


def test_plant_genomes_decode():
    for kind in ("P1", "PF", "PL"):
        ph, env, g, meta = wt.plant_spec(f"PLANT_{kind}_J1")
        assert g.shape == (1, 1, ph.prog_len, 5) or g.shape[-2:] == (ph.prog_len, 5)
        assert ph.update_mode == "sync" and ph.update_period == 2 and ph.lat_jitter == 1
        assert env.family == "RELAY" and env.d == 3 and env.delta == 8
    ph0, *_ = wt.plant_spec("PLANT_P1_J0")
    assert ph0.lat_jitter == 0
    with pytest.raises(KeyError):
        wt.plant_lines("XX")
