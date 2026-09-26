"""H2-X: is long edge persistence sustained by incoming energy transfers?

POST HOC, and labelled so. `aeth02_closure.py`'s preregistered H2-P2
failed in an informative direction: a null conditioned on the edge
cohort, with source energy as an i.i.d. walk, UNDER-predicts the
>=64-tick cohort about 5x. The i.i.d. walk destroys any correlation
between a source and its own energy supply. The hypothesis this module
tests was formed after seeing that result:

  HX  Long-lived edges have sources that are persistently fed by an
      energy-field edge from a neighbour, and that inflow is what keeps
      them above WRITE_COST.

Two parts, both on the unmodified `aeth01.v1` kernel:

  OBSERVATION  At a stationary snapshot, compare PERSISTENT (run >= 64)
      and SHORT (run <= 8) template-field edges: the source's energy,
      whether the source is the target of an energy-field edge this
      tick, and the fraction of the last 64 ticks in which it was.
  INTERVENTION From the same snapshot, three arms:
      CUT    re-aim (arg0 + 1) every active energy-field emitter that is
             currently feeding the SOURCE of a sampled persistent edge;
      SHAM   re-aim the same number of active energy-field emitters that
             feed sites that are not sources of any sampled edge;
      NONE   change nothing.
      Measure the fraction of sampled persistent edges still present
      with the same winner at +16, +32, +64, +128, +200.

PREDICTION under HX: CUT persistence falls far below NONE and SHAM
within tens of ticks (a source with no inflow drains at net -1/tick and
cannot hold 64+ ticks from a typical stored energy).
FALSIFIED IF: CUT persistence at +64 is within 0.05 of SHAM, i.e.
removing the inflow does not matter.

The re-aim is the H1 lesion (arg0 + 1): the emitter stays active and
keeps its field, only its target moves, so CUT and SHAM disturb the same
number of emitters in the same way.
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

OFFS = np.array(G.SLOT_OFFSETS, dtype=np.int64)
HORIZONS = (16, 32, 64, 128, 200)
WINDOW = 64


def run_tracking_inflow(n, warmup, seed, rng_seed):
    par = F.params(seed)
    fields, _ = F.R.build_initial("sparse_soup", n, n, rng_seed,
                                  write_density=0.50)
    fields = [f.copy() for f in fields]
    runs = G.new_runlengths(np, n, n)
    ring = np.zeros((WINDOW, n, n), dtype=bool)
    obs = None
    for t in range(1, warmup + 1):
        fields, obs = F.step(fields, t, par)
        G.update_runlengths(np, runs, obs)
        ring[t % WINDOW] = G.unpack(obs[4])[0] != G.NO_WINNER
    return fields, runs, obs, ring.mean(axis=0), par, warmup


def sources_of(n, mask, winner):
    targets = np.argwhere(mask)
    return targets, (targets + OFFS[winner[mask].astype(np.int64)]) % n


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
    fields, runs, obs, inflow_frac, par, tick = run_tracking_inflow(
        n, a.warmup, seed, rng_seed)
    wc = par["write_cost"]
    fed_now = G.unpack(obs[4])[0] != G.NO_WINNER          # site receives energy edge

    # ---- observation, template fields only (0-3)
    rows = {"persistent": [], "short": []}
    energy = fields[4].astype(np.int64)
    picks = {}
    for f in range(4):
        w = G.unpack(obs[f])[0]
        run = runs["run"][f]
        present = w != G.NO_WINNER
        for label, m in (("persistent", present & (run >= 64)),
                         ("short", present & (run >= 1) & (run <= 8))):
            tg, src = sources_of(n, m, w)
            rows[label].append((f, tg, src, run[m].astype(np.int64)))
    obs_out = {}
    for label, parts in rows.items():
        src = np.concatenate([p[2] for p in parts])
        ages = np.concatenate([p[3] for p in parts])
        old = ages > 255
        obs_out[label] = {
            # An active emitter with no inflow drifts -1/tick and energy
            # caps at 255, so an edge older than ~255 ticks is impossible
            # without net inflow. This counts how many such edges exist.
            "run_gt_255": int(old.sum()),
            "run_gt_255_source_fed_fraction_last64": (
                float(inflow_frac[src[old, 0], src[old, 1]].mean())
                if old.any() else None),
            "edges": int(len(src)),
            "source_energy_mean": float(energy[src[:, 0], src[:, 1]].mean()),
            "source_fed_now": float(fed_now[src[:, 0], src[:, 1]].mean()),
            "source_fed_fraction_last64": float(
                inflow_frac[src[:, 0], src[:, 1]].mean()),
        }
    obs_out["all_sites"] = {"fed_now": float(fed_now.mean()),
                            "fed_fraction_last64": float(inflow_frac.mean()),
                            "energy_mean": float(energy.mean())}

    # ---- intervention
    rng = np.random.default_rng(0xF33D + a.seed_index)
    per = [(f, tg, src) for f, tg, src, _age in rows["persistent"]]
    all_tg = np.concatenate([p[1] for p in per])
    all_src = np.concatenate([p[2] for p in per])
    all_f = np.concatenate([np.full(len(p[1]), p[0]) for p in per])
    k = min(a.k, len(all_tg))
    pick = rng.choice(len(all_tg), k, replace=False)
    tg, src, fl = all_tg[pick], all_src[pick], all_f[pick]
    slot0 = np.array([G.unpack(obs[f])[0][r, c] for f, (r, c) in zip(fl, tg)])

    w4 = G.unpack(obs[4])[0]
    feeder_of = {}
    for (r, c) in {tuple(x) for x in src.tolist()}:
        s = w4[r, c]
        if s != G.NO_WINNER:
            fr, fc = (r + OFFS[s, 0]) % n, (c + OFFS[s, 1]) % n
            feeder_of[(r, c)] = (int(fr), int(fc))
    cut = sorted(set(feeder_of.values()))
    src_set = {tuple(x) for x in src.tolist()}
    fed_sites = np.argwhere(fed_now)
    others = [tuple(x) for x in fed_sites.tolist() if tuple(x) not in src_set]
    sham_targets = [others[i] for i in rng.choice(len(others), min(len(cut), len(others)),
                                                  replace=False)]
    sham = []
    for (r, c) in sham_targets:
        s = w4[r, c]
        sham.append(((r + OFFS[s, 0]) % n, (c + OFFS[s, 1]) % n))
    arms = {}
    for name, lesion in (("NONE", []), ("CUT", cut), ("SHAM", sham)):
        cur = [x.copy() for x in fields]
        for (r, c) in lesion:
            cur[1][r, c] = cur[1][r, c] + np.uint8(1)
        series = {}
        alive = np.ones(k, dtype=bool)
        for step_no in range(1, max(HORIZONS) + 1):
            cur, o = F.step(cur, tick + step_no, par)
            now = np.array([G.unpack(o[f])[0][r, c] for f, (r, c) in zip(fl, tg)])
            alive &= now == slot0
            if step_no in HORIZONS:
                series[step_no] = float(alive.mean())
        arms[name] = series
    out = {"n": n, "warmup": a.warmup, "seed_index": a.seed_index,
           "semantics": "aeth01.v1", "post_hoc": True,
           "observation": obs_out,
           "sampled_persistent_edges": int(k),
           "sources_with_a_feeder": len(feeder_of),
           "feeders_cut": len(cut), "sham_lesions": len(sham),
           "arms": arms,
           "falsified": abs(arms["CUT"][64] - arms["SHAM"][64]) <= 0.05}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k2: out[k2] for k2 in ("observation", "sources_with_a_feeder",
                                             "feeders_cut", "arms", "falsified")},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
