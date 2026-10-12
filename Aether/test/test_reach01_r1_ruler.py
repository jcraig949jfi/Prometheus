"""REACH01 R1 ruler qualification (TEST-4 planted controls), through the production code path.

F_EXCH  exchange law X: at each origin a WRITE site aimed east into its neighbour's payload. The planted value shuttles
        origin <-> neighbour: decodable at radius 1 only (Dstat ~ 0, D1 > 0).
F_RELAY aeth01.v1 copy chain: origin + 5 more WRITE sites in a row, all aimed east into the next payload. The planted
        value is copied outward: decodable at radii 1..6 (Dstat >> 0).
F_NOINFO decoder-level: branches differ at every radius, but the difference is random per origin and unrelated to the
        label. Held-out decoding is at chance (Dstat ~ 0) even though divergence is total.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "V2B", "REACH01", "R1"))
import r1_test4 as T  # noqa: E402
import r1_reduce as RD  # noqa: E402

n = 128
SP = 16
EAST = 1


def grid():
    return [(y, x) for y in range(SP // 2, n, SP) for x in range(2, n, SP)]


def world(kind):
    s = [np.full((n, n), 9, np.uint8), np.zeros((n, n), np.uint8), np.zeros((n, n), np.uint8),
         np.zeros((n, n), np.uint8), np.full((n, n), 255, np.uint8)]
    length = 1 if kind == "exch" else 6
    for (y, x) in grid():
        for c in range(length):
            s[0][y, x + c] = 1
            s[1][y, x + c] = EAST
            s[2][y, x + c] = 3
        s[3][y, x] = 0x10
    return s


def run(kind, law, tmp):
    units = []
    for k in range(3):
        out = os.path.join(tmp, "%s_s%d.npz" % (law, k))
        m = T.run_unit("cpu", law, k, n, 0, 100, out, init=world(kind), origins=grid())
        z = np.load(out)
        units.append((k, m, z["H"], z["D"]))
    return RD.stats(RD.decode(units))


def test_exchange_decodes_at_radius_1_only(tmp_path):
    st = run("exch", "X", str(tmp_path))
    for s in st.values():
        assert s["D1"] > 0.1
        assert abs(s["Dstat"]) < 0.02


def test_relay_chain_decodes_at_every_radius(tmp_path):
    st = run("relay", "V1", str(tmp_path))
    for s in st.values():
        assert s["D1"] > 0.5 and s["Dstat"] > 0.5
        acc = np.array(s["acc"])
        assert (acc[:, 1:] > 0.6).all()          # radii 2..6 at every observed tick


def test_divergence_without_information_is_chance():
    rng = np.random.default_rng(0)
    units = []
    for k in range(3):
        H = rng.integers(0, 3, size=(8, 64, 2, 6, 4, 256)).astype(np.uint8)   # every branch differs, randomly
        units.append((k, {}, H, np.ones((8, 64, 2, 6), np.float32)))
    st = RD.stats(RD.decode(units))
    for s in st.values():
        assert abs(s["Dstat"]) < 0.03 and abs(s["D1"]) < 0.05
