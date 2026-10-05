"""P1 ruler qualification (V2-B DEV-2): synthetic known-answer sequences for aeth_mobility.MobilityMeter + classify.

Each sequence is built to be exactly one class. The travelling pattern is a CALIBRATION positive: it shows the ruler can
say "mobile". It is not physics, and a law that merely replayed such a driving rule would not count as a discovery.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_HERE, "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth_mobility as M               # noqa: E402

N, T = 64, 400


def run(seq):
    it = iter(seq)
    m = M.MobilityMeter(next(it))
    for f in it:
        m.update(f)
    return m.metrics()


def base(rng):
    return [rng.integers(0, 256, size=(N, N), dtype=np.uint8) for _ in range(5)]


def test_frozen():
    rng = np.random.default_rng(1)
    f = base(rng)
    assert M.classify(run([f] * (T + 1))) == "FROZEN"


def test_flip_flop_is_cycling():
    rng = np.random.default_rng(2)
    a, b = base(rng), base(rng)
    mask = rng.random((N, N)) < 0.5
    mix = [np.where(mask, b[i], a[i]).astype(np.uint8) for i in range(5)]
    m = run([a if t % 2 == 0 else mix for t in range(T + 1)])
    assert m["revisit_share"] > 0.9 and M.classify(m) == "CYCLING"


def test_unconditional_counter():
    rng = np.random.default_rng(3)
    f = base(rng)
    mask = rng.random((N, N)) < 0.3
    seq = []
    for t in range(T + 1):
        g = [x.copy() for x in f]
        g[3] = ((f[3].astype(np.int32) + np.where(mask, t, 0)) & 0xFF).astype(np.uint8)
        seq.append(g)
    m = run(seq)
    assert m["counter_share"] > 0.9 and M.classify(m) == "COUNTER"


def test_decaying():
    rng = np.random.default_rng(4)
    f = base(rng)
    seq = [f]
    for t in range(T):
        g = [x.copy() for x in seq[-1]]
        rate = 0.10 if t < 100 else 0.02           # payload only: turnover 0.025 early, 0.005 late (above the floor)
        m = rng.random((N, N)) < rate
        g[3] = np.where(m, rng.integers(0, 256, size=(N, N), dtype=np.uint8), g[3]).astype(np.uint8)
        seq.append(g)
    assert M.classify(run(seq)) == "DECAYING"


def test_localised_hot_row():
    rng = np.random.default_rng(5)
    f = base(rng)
    seq = [f]
    for t in range(T):
        g = [x.copy() for x in seq[-1]]
        g[3][0, :] = rng.integers(0, 256, size=N, dtype=np.uint8)
        seq.append(g)
    m = run(seq)
    assert m["active_site_share"] < 0.05 and M.classify(m) == "LOCALISED"


def test_travelling_pattern_is_mobile_calibration_positive():
    rng = np.random.default_rng(6)
    f = base(rng)
    seq = [[np.roll(x, t, axis=1) for x in f] for t in range(T + 1)]   # period 64 > the revisit window
    m = run(seq)
    assert M.classify(m) == "ENDOGENOUSLY_MOBILE", m
