"""H2-X2: SUSTAINED removal of energy inflow to persistent-edge sources.

POST HOC, second test, labelled so. H2-X (`aeth02_h2x_inflow.py`) cut the
energy feeders of sampled persistent-edge sources ONCE, at the snapshot,
and was falsified at its preregistered bar (CUT within 0.05 of SHAM at
+64 on both seeds: 0.045, 0.030). Its own observation block says why a
one-shot cut is weak: only ~15% of those sources are fed at any instant
(feeding is intermittent) and they hold a large reserve (mean energy
~94). The same run also found 65% of the >=64-tick cohort older than
255 ticks, which the law forbids without net inflow.

This test removes the inflow for the whole follow, not once:

  CUT_SUSTAINED   before every tick, any active energy-field emitter
                  whose current target is the SOURCE of a sampled
                  persistent edge is re-aimed (arg0 + 1);
  SHAM_SUSTAINED  before every tick, exactly as many active energy-field
                  emitters as CUT_SUSTAINED re-aimed on that same tick,
                  drawn from those aiming at sites that are not sampled
                  sources, are re-aimed the same way (CUT runs first and
                  its per-tick counts are replayed, so both arms make
                  identical numbers of lesions on identical ticks);
  NONE            nothing.

The re-aim is H1's lesion; CUT and SHAM disturb the same number of
emitters per tick in the same way.

PREDICTION, from the accounting alone (active drift -1/tick, energy cap
255): with inflow removed, a sampled source runs out within roughly its
stored energy in ticks, so CUT_SUSTAINED persistence at +128 is at most
half of SHAM_SUSTAINED's.
FALSIFIED IF: CUT_SUSTAINED(+128) > 0.5 x SHAM_SUSTAINED(+128).
"""

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth01_graph as G                # noqa: E402
from observatory import aeth02_falsifiers as F           # noqa: E402
from observatory import aeth02_h2x_inflow as X           # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

HORIZONS = (16, 32, 64, 128, 200)


def energy_emitters_aiming_at(fields, write_cost, n):
    """(row, col) of active energy-field emitters and the flat index they aim at."""
    active = (fields[0] == K.WRITE_OPCODE) & (
        fields[4].astype(np.int64) >= write_cost)
    em = active & ((fields[2] % 5) == K.ENERGY)
    r, c = np.nonzero(em)
    d = (fields[1][r, c] % 4).astype(np.int64)
    dr = np.array([V._DIR_OFFSET[k][0] for k in range(4)])[d]
    dc = np.array([V._DIR_OFFSET[k][1] for k in range(4)])[d]
    tgt = ((r + dr) % n) * n + ((c + dc) % n)
    return r, c, tgt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--warmup", type=int, default=2500)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--k", type=int, default=400)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    n = a.n
    seed, rng_seed = F.B_SEED0 + a.seed_index, F.B_RNG0 + a.seed_index
    fields, runs, obs, _inflow, par, tick = X.run_tracking_inflow(
        n, a.warmup, seed, rng_seed)
    wc = par["write_cost"]
    rng = np.random.default_rng(0x5057 + a.seed_index)
    tg_all, src_all, f_all = [], [], []
    for f in range(4):
        w = G.unpack(obs[f])[0]
        m = (w != G.NO_WINNER) & (runs["run"][f] >= 64)
        tg, src = X.sources_of(n, m, w)
        tg_all.append(tg)
        src_all.append(src)
        f_all.append(np.full(len(tg), f))
    tg_all, src_all, f_all = (np.concatenate(tg_all), np.concatenate(src_all),
                              np.concatenate(f_all))
    k = min(a.k, len(tg_all))
    pick = rng.choice(len(tg_all), k, replace=False)
    tg, src, fl = tg_all[pick], src_all[pick], f_all[pick]
    slot0 = np.array([G.unpack(obs[f])[0][r, c] for f, (r, c) in zip(fl, tg)])
    protected = np.zeros(n * n, dtype=bool)
    protected[src[:, 0] * n + src[:, 1]] = True

    arms, lesions, cut_schedule = {}, {}, []
    for name in ("NONE", "CUT_SUSTAINED", "SHAM_SUSTAINED"):
        cur = [x.copy() for x in fields]
        arm_rng = np.random.default_rng(0x5A11 + a.seed_index)
        alive = np.ones(k, dtype=bool)
        series, count = {}, 0
        for step_no in range(1, max(HORIZONS) + 1):
            if name != "NONE":
                r, c, t = energy_emitters_aiming_at(cur, wc, n)
                hit = protected[t]
                if name == "CUT_SUSTAINED":
                    sel = np.flatnonzero(hit)
                    cut_schedule.append(len(sel))
                else:
                    want = cut_schedule[step_no - 1]
                    pool = np.flatnonzero(~hit)
                    sel = arm_rng.choice(pool, min(want, len(pool)), replace=False) \
                        if want else np.zeros(0, dtype=np.int64)
                cur[1][r[sel], c[sel]] = cur[1][r[sel], c[sel]] + np.uint8(1)
                count += len(sel)
            cur, o = F.step(cur, tick + step_no, par)
            now = np.array([G.unpack(o[f])[0][rr, cc] for f, (rr, cc) in zip(fl, tg)])
            alive &= now == slot0
            if step_no in HORIZONS:
                series[step_no] = float(alive.mean())
        arms[name] = series
        lesions[name] = count
    cut, sham = arms["CUT_SUSTAINED"][128], arms["SHAM_SUSTAINED"][128]
    out = {"n": n, "warmup": a.warmup, "seed_index": a.seed_index,
           "semantics": "aeth01.v1", "post_hoc": True, "k": int(k),
           "arms": arms, "re_aims_total": lesions,
           "cut_over_sham_128": cut / sham if sham else None,
           "falsified": cut > 0.5 * sham}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
