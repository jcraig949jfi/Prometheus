"""AIM01 known-answer fixtures for the measurement layer (order s11).

Synthetic trajectories, no Aether physics: each fixture drives
Aether/V2B/AIM01/aim01_run.Meter directly with hand-built (state, next,
reaim, targeted) tuples whose correct readings are known by construction.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "V2B", "AIM01"))
import aim01_run as A  # noqa: E402

N = 16
T = 200
LATE = 100


def world():
    rng = np.random.default_rng(7)
    s = [rng.integers(0, 256, (N, N), dtype=np.uint8) for _ in range(5)]
    s[0][:] = 9            # no WRITE sites
    s[4][:] = 50
    return s


def none_sf():
    return [np.zeros((N, N), dtype=bool) for _ in range(5)]


def run(stepper, init_sf=None, bin_ticks=50):
    m = A.Meter(np, N, T, bin_ticks, LATE, init_sf or none_sf())
    s = world()
    for t in range(T):
        nxt, reaim, tgt = stepper(t, s)
        m.update(s, nxt, reaim, tgt)
        s = nxt
    return m, m.finalize()


def test_static():
    def step(t, s):
        return [x.copy() for x in s], None, none_sf()
    m, r = run(step)
    assert r["ever_changed_eff"] == 0 and r["ever_changed_raw"] == 0
    assert r["late_turnover_eff"] == 0 and r["frozen_strict_eff"] == 1.0
    assert r["tail64_novel_change_frac"] is None and r["tail64_changed_sites"] == 0
    assert all(row["target_support_growth_sf"] == 0 for row in m.series)
    assert r["subset_violations"] == 0


def test_fixed_flicker():
    sites = [(1, 1), (5, 7), (9, 3)]

    def step(t, s):
        nxt = [x.copy() for x in s]
        tgt = none_sf()
        for (i, j) in sites:
            nxt[3][i, j] = 10 if t % 2 == 0 else 20     # payload alternates 10/20
            tgt[3][i, j] = True
        return nxt, None, tgt
    m, r = run(step)
    assert abs(r["ever_changed_eff"] - 3 / N ** 2) < 1e-12           # tiny fixed support
    assert abs(r["late_turnover_eff"] - 3 / N ** 2) < 1e-12           # every flicker site every tick
    assert r["tail64_novel_change_frac"] == 0.0                       # revisits recent states only
    assert r["tail64_periodic_le16_frac"] == 1.0                      # period 2
    assert r["tail64_unique_nonaim_mean"] == 2.0
    assert m.series[-1]["target_support_growth_sf"] == m.series[0]["target_support_growth_sf"]
    assert r["subset_violations"] == 0


def test_expanding_support():
    order = [(i, j) for i in range(N) for j in range(N)]

    def step(t, s):
        nxt = [x.copy() for x in s]
        tgt = none_sf()
        i, j = order[t % len(order)]
        nxt[3][i, j] = (int(s[3][i, j]) + 1 + t) % 256 or 1
        if nxt[3][i, j] == s[3][i, j]:
            nxt[3][i, j] = (nxt[3][i, j] + 1) % 256
        tgt[3][i, j] = True
        return nxt, None, tgt
    m, r = run(step)
    ever = [row["ever_changed_eff"] for row in m.series]
    assert ever == sorted(ever) and ever[-1] > ever[0]               # monotone growth
    assert abs(r["ever_changed_eff"] - T / N ** 2) < 1e-12 or r["ever_changed_eff"] == 1.0
    growth = [row["target_support_growth_sf"] for row in m.series]
    assert growth[-1] > growth[0] > 0                                 # beyond the (empty) init support
    assert r["tail64_novel_change_frac"] == 1.0
    assert r["change_given_new_target"] == 1.0
    assert r["subset_violations"] == 0


def test_aim_bookkeeping_only():
    sites = np.zeros((N, N), dtype=bool)
    sites[::3, ::2] = True

    def step(t, s):
        nxt = [x.copy() for x in s]
        nxt[1] = np.where(sites, (s[1].astype(np.uint16) + 1).astype(np.uint8), s[1])
        return nxt, sites.copy(), none_sf()
    m, r = run(step)
    assert r["ever_changed_raw"] == sites.mean() and r["late_turnover_raw"] > 0     # RAW moves
    assert r["ever_changed_eff"] == 0 and r["late_turnover_eff"] == 0               # EFFECT does not
    assert r["frozen_strict_eff"] == 1.0 and r["frozen_net64_eff"] == 1.0
    assert all(row["eff_turnover"] == 0 for row in m.series)
    assert all(row["reaim_rate"] > 0 for row in m.series)
    assert r["subset_violations"] == 0


def test_bookkeeping_plus_real_write_counts_only_the_write():
    """A re-aimed site whose arg0 is ALSO written must not happen under the law
    (written arg0 suppresses re-aim); a real arg0 write elsewhere must count."""
    def step(t, s):
        nxt = [x.copy() for x in s]
        reaim = np.zeros((N, N), dtype=bool)
        reaim[0, 0] = True
        nxt[1][0, 0] = (int(s[1][0, 0]) + 1) % 256
        tgt = none_sf()
        if t == 50:
            nxt[1][4, 4] = (int(s[1][4, 4]) + 7) % 256
            tgt[1][4, 4] = True
        return nxt, reaim, tgt
    m, r = run(step)
    assert abs(r["ever_changed_eff"] - 1 / N ** 2) < 1e-12           # only (4,4)
    assert abs(r["ever_changed_raw"] - 2 / N ** 2) < 1e-12
    assert r["subset_violations"] == 0
