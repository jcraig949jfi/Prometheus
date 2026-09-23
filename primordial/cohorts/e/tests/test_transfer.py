import json

import numpy as np

from primordial.cohorts.e import transfer as T
from primordial.qd import e7_run as E7
from primordial.qd.archive import serial_reference


def test_nparchive_matches_serial_reference_any_order():
    rng = np.random.default_rng(0)
    glen = 8
    cells = rng.integers(0, 20, 600).astype(np.uint32)
    fits = rng.integers(0, 5, 600).astype(np.int32)          # many ties -> genome order decides
    gs = rng.integers(0, 3, (600, glen)).astype(np.uint8)
    ref = serial_reference(cells, fits, gs)
    for order in (np.arange(600), rng.permutation(600)):
        a = T.NpArchive(glen, 20)
        for i in range(0, 600, 37):
            j = order[i:i + 37]
            a.insert(cells[j], fits[j], gs[j])
        assert a.as_dict() == ref


def test_nparchive_sampling_is_seeded():
    a = T.NpArchive(4, 10)
    a.insert(np.arange(10), np.arange(10), np.arange(40, dtype=np.uint8).reshape(10, 4))
    s1 = a.sample(np.random.default_rng(3), 32)
    s2 = a.sample(np.random.default_rng(3), 32)
    assert np.array_equal(s1, s2)


def test_compatibility_is_exact_layout():
    assert T.compatible(E7.G7(2, "linear"), E7.G7(4, "linear"))[0]        # D=8, W=3
    ok, why = T.compatible(E7.G7(1, "linear"), E7.G7(4, "linear"))       # D=9 vs 8
    assert not ok and "layout differs" in why
    assert not T.compatible(E7.G7(2, "linear"), E7.G7(4, "tt_feat"))[0]
    assert T.default_donor(4, "linear") == 2


def test_shuffle_keeps_value_multisets_and_abstain_row():
    g7 = E7.G7(4, "linear")
    rng = np.random.default_rng(1)
    raw = g7.pack(g7.init(rng, 4))
    sh = T.shuffle_genomes(g7, raw, rng)
    assert sh.shape == raw.shape and not np.array_equal(sh, raw)
    (W, b), C = g7.unpack(raw)
    (W2, b2), C2 = g7.unpack(sh)
    for i in range(4):
        assert np.array_equal(np.sort(W[i].ravel()), np.sort(W2[i].ravel()))
        assert np.array_equal(np.sort(b[i]), np.sort(b2[i]))
        assert np.array_equal(np.sort(C[i, 1:].ravel()), np.sort(C2[i, 1:].ravel()))
    assert (C2[:, 0] == 0).all()


def test_checkpoints_geometric_and_end_at_gens():
    ck = T.checkpoints(200)
    assert ck[0] == 1 and ck[-1] == 200 and np.all(np.diff(ck) > 0)
    assert T.checkpoints(3).tolist() == [1, 2, 3]


def test_signflip_and_gens_to():
    assert T.signflip_p([1, 1, 1, 1, 1, 1, 1, 1]) == 1 / 256
    assert T.signflip_p([-1] * 8) == 1.0
    assert T.gens_to(np.array([1, 3, 5]), 3) == 2
    assert T.gens_to(np.array([1, 3, 5]), 9) == 4


class _W:
    def __init__(self):
        self.rows = []

    def write(self, r):
        json.dumps(r)
        self.rows.append(r)


def test_run_pair_smoke_integrity_and_abort():
    w = _W()
    s = T.run_pair(2, 4, "linear", [0, 1], gens=3, batch=24, n_train=2, tag="test", writer=w, oracles=False,
                   log=lambda *_: None)
    conds = [r["condition"] for r in w.rows]
    assert conds == list(T.CONDITIONS) * 2 + ["summary"]
    for g in (r for r in w.rows if r["condition"] == "graft"):
        assert g["graft_bytes_unmodified"] and g["graft_fused_eq_numpy"]
    by = {(r["condition"], r["run_seed"]): r for r in w.rows if r["condition"] != "summary"}
    # common filler: scratch and rand_graft differ only in their K slots, graft differs from shuffle
    assert by[("scratch", 0)]["slot_sha256"] != by[("rand_graft", 0)]["slot_sha256"]
    assert by[("graft", 0)]["slot_sha256"] != by[("shuffle_graft", 0)]["slot_sha256"]
    assert len(by[("graft", 0)]["held_curve"]) == len(T.checkpoints(3))
    assert {r["status"] for r in w.rows} == {"record", "cheat", "control"}
    assert "held_auc_p" in s["graft"] and "gens_to" in s["scratch"]
    for c in ("graft", "self_graft"):
        assert s[c]["vs_cheats_held_auc_p_max"] == max(s[c]["vs_rand_graft_held_auc_p"], s[c]["vs_shuffle_graft_held_auc_p"])
    by_c = lambda c: np.array([by[(c, rs)]["held_auc"] for rs in (0, 1)])
    assert np.isclose(s["graft"]["vs_rand_graft_held_auc_diff_mean"], (by_c("graft") - by_c("rand_graft")).mean())
    w2 = _W()
    assert "aborted" in T.run_pair(1, 4, "linear", [0], 3, 24, 2, "test", w2, oracles=False)
    assert w2.rows[0]["status"] == "aborted"


def test_rerun_is_bit_identical():
    rows = []
    for _ in range(2):
        w = _W()
        T.run_pair(2, 4, "linear", [0], gens=4, batch=24, n_train=2, tag="test", writer=w, oracles=False,
                   log=lambda *_: None)
        rows.append([{k: v for k, v in r.items() if k != "ts"} for r in w.rows])
    assert rows[0] == rows[1]
