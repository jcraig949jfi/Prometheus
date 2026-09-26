"""AETH-03 cheap scouts: one battery, run identically on v1 and every variant.

Operator directive 2026-09-26. The question is not "does something
interesting happen" but whether a single physical change gives
endogenous state change, persistent causal structure, and consequential
history that v1 lacks. Every number below is measured the same way on
the unmodified `aeth01.v1` baseline, so a variant is only ever read
against v1 at the same size, seeds, parameters and tick counts.

BATTERY (all CPU, small lattice, $0.00):

  S0  viability at the end of warmup: activity density, mean energy,
      the frozen fraction (sites whose four template fields do not change
      over 64 ticks, the AETH-02 H1b measure).
  S1  endogenous change: from the warmed state, fork a control that
      keeps perturbation and an arm with perturbation OFF; template
      change rate at +1, +10, +100, +500. v1 falls ~95% (AETH-02 H4).
  S2  consequential history (twin divergence): from the warmed state,
      flip one template bit at each of 16 widely spaced ACTIVE EMITTERS
      in a twin, perturbation OFF in both, and follow 500 ticks. Report
      the number of differing (site, field) pairs OUTSIDE the flipped
      sites themselves (the footprint -- a flipped byte that merely sits
      there is not history mattering), the reach (largest torus distance
      of a differing site from its origin), and the fraction of origins
      whose neighbourhood still differs. Repeated with perturbation ON,
      whose hash-keyed stream is identical in both twins.
  S3  functional-graph turnover with perturbation OFF: Jaccard overlap of
      the realized edge sets (source, target, field) at lags 1, 10, 100,
      averaged over the last 100 ticks of the arm.
  S4  contested persistence with perturbation OFF: P(the same contender
      wins a contested (site, field) slot on consecutive ticks), against
      the 1/k expected from v1's per-tick hash.

Semantics ids come from `aeth03_variants.SEMANTICS_ID`; nothing here is
reported under `aeth01.v1` except the v1 arm.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth01_graph as G                # noqa: E402
from observatory import aeth01_run as R                  # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

B_BALANCED = dict(write_cost=1, maintenance_cost=1,
                  replenish_numer=int(round(0.125 * (1 << 32))),
                  replenish_amount=8)
MUT_ON = int(round(0.1 * (1 << 32)))
SEED0 = 0x5C011701
RNG0 = 0xA37E01
HORIZONS = (1, 10, 50, 100, 250, 500)


def params(seed, mut):
    out = dict(B_BALANCED)
    out.update(seed=seed, mut_numer=mut)
    return out


def step(variant, fields, tick, par, watch=False):
    obs = [] if watch else None
    h, w = fields[0].shape
    out = V.step(variant, H=h, W=w, tick=tick, opcode=fields[0],
                 arg0=fields[1], arg1=fields[2], payload=fields[3],
                 energy=fields[4], observer=obs, **par)
    return list(out[:5]), obs


def initial(variant, n, rng_seed):
    fields, _ = R.build_initial("sparse_soup", n, n, rng_seed,
                                write_density=0.50)
    fields = [f.copy() for f in fields]
    if variant == "cnd":
        # Give the second opcode a presence to start from: half the
        # emitters become 0x02. Stated in the report as an initial-state
        # difference, not hidden.
        rng = np.random.default_rng(rng_seed ^ 0xC0D)
        flip = (fields[0] == 1) & (rng.random((n, n)) < 0.5)
        fields[0] = np.where(flip, np.uint8(V.COND_OPCODE), fields[0]).astype(np.uint8)
    return fields


def emitters(variant, fields, write_cost):
    op = fields[0]
    is_em = op == 1
    if variant == "cnd":
        is_em = is_em | (op == V.COND_OPCODE)
    return is_em & (fields[4].astype(np.int64) >= write_cost)


def template_change(before, after):
    return float(np.mean([np.mean(before[i] != after[i]) for i in range(4)]))


def edge_keys(obs, n):
    """Set of realized edges as int64 keys: (target*5 + field)*4 + slot."""
    keys = []
    tgt = np.arange(n * n, dtype=np.int64).reshape(n, n)
    for f, entry in enumerate(obs):
        w = G.unpack(entry)[0]
        m = w != G.NO_WINNER
        keys.append((tgt[m] * 5 + f) * 4 + w[m].astype(np.int64))
    return np.concatenate(keys) if keys else np.zeros(0, np.int64)


def jaccard(a, b):
    if not len(a) and not len(b):
        return None
    inter = len(np.intersect1d(a, b, assume_unique=True))
    return inter / float(len(a) + len(b) - inter)


def torus_dist(n, r0, c0, r, c):
    dr = np.abs(r - r0)
    dc = np.abs(c - c0)
    return np.maximum(np.minimum(dr, n - dr), np.minimum(dc, n - dc))


def twin(variant, fields, tick0, par, rng, n, spacing):
    """S2: flip one template bit at spaced active emitters, follow both."""
    em = emitters(variant, fields, par["write_cost"])
    origins = []
    half = spacing // 2
    for r0 in range(half, n, spacing):
        for c0 in range(half, n, spacing):
            # a random active emitter inside this square of the origin grid
            rr, cc = np.nonzero(em[r0 - half:r0 + half, c0 - half:c0 + half])
            if not len(rr):
                continue
            k = rng.integers(len(rr))
            origins.append((r0 - half + int(rr[k]), c0 - half + int(cc[k])))
    a = [f.copy() for f in fields]
    b = [f.copy() for f in fields]
    for (r, c) in origins:
        fld = int(rng.integers(4))
        b[fld][r, c] ^= np.uint8(1 << int(rng.integers(8)))
    orr = np.array([o[0] for o in origins])
    occ = np.array([o[1] for o in origins])
    rows, cols = np.indices((n, n))
    # nearest origin for every site, and distance to it
    dist = np.full((n, n), 10 ** 9)
    for r0, c0 in origins:
        dist = np.minimum(dist, torus_dist(n, r0, c0, rows, cols))
    is_origin = np.zeros((n, n), dtype=bool)
    is_origin[orr, occ] = True
    out = {}
    for t in range(1, max(HORIZONS) + 1):
        a, _ = step(variant, a, tick0 + t, par)
        b, _ = step(variant, b, tick0 + t, par)
        if t in HORIZONS:
            diff_site = np.zeros((n, n), dtype=bool)
            pairs = 0
            for i in range(5):
                d = a[i] != b[i]
                pairs += int(d.sum())
                diff_site |= d
            foot = diff_site & ~is_origin
            local = [bool(diff_site[max(0, r - half):r + half,
                                    max(0, c - half):c + half].any())
                     for r, c in origins]
            out[t] = {
                "differing_pairs": pairs,
                "footprint_sites": int(foot.sum()),
                "footprint_per_origin": foot.sum() / float(max(1, len(origins))),
                "reach": int(dist[diff_site].max()) if diff_site.any() else 0,
                "origins_still_differing": float(np.mean(local)) if local else 0.0,
                "origins_self_differing": float(diff_site[orr, occ].mean())
                if len(origins) else 0.0,
            }
    return {"origins": len(origins), "by_horizon": out}


def battery(variant, n, warmup, follow, seed_index, spacing):
    seed, rng_seed = SEED0 + seed_index, RNG0 + seed_index
    rng = np.random.default_rng(0xA3 + seed_index)
    par_on, par_off = params(seed, MUT_ON), params(seed, 0)
    t0 = time.time()
    fields = initial(variant, n, rng_seed)
    tick = 0
    for _ in range(warmup):
        tick += 1
        fields, _ = step(variant, fields, tick, par_on)
    warm = [f.copy() for f in fields]
    wc = par_on["write_cost"]

    # S0
    probe = [f.copy() for f in warm]
    for k in range(64):
        probe, _ = step(variant, probe, tick + 1 + k, par_on)
    frozen = np.ones((n, n), dtype=bool)
    for i in range(4):
        frozen &= probe[i] == warm[i]
    s0 = {"activity_density": float(emitters(variant, warm, wc).mean()),
          "energy_mean": float(warm[4].mean()),
          "frozen_fraction_64": float(frozen.mean())}

    # S1, S3, S4
    arms = {}
    s3 = {"jaccard_lag1": [], "jaccard_lag10": [], "jaccard_lag100": []}
    s4 = {"same_winner": 0, "contested": 0, "expected_if_rerolled": 0.0}
    for name, par in (("perturbation_on", par_on), ("perturbation_off", par_off)):
        cur = [f.copy() for f in warm]
        series, keys_hist, last_obs = {}, {}, None
        for k in range(1, follow + 1):
            before = cur
            watch = name == "perturbation_off"
            cur, obs = step(variant, cur, tick + k, par, watch=watch)
            if k in HORIZONS:
                series[k] = template_change(before, cur)
            if watch:
                if k > follow - 100 - 100:
                    keys_hist[k] = edge_keys(obs, n)
                if last_obs is not None and k > follow - 100:
                    for f in range(5):
                        w0, c0, _ = G.unpack(last_obs[f])
                        w1, c1, _ = G.unpack(obs[f])
                        m = (c0 >= 2) & (c1 >= 2) & (w0 != G.NO_WINNER)
                        s4["contested"] += int(m.sum())
                        s4["same_winner"] += int((m & (w0 == w1)).sum())
                        s4["expected_if_rerolled"] += float(
                            (1.0 / c1[m].astype(np.float64)).sum())
                last_obs = obs
        arms[name] = series
        if keys_hist:
            for k in range(follow - 99, follow + 1):
                for lag, key in ((1, "jaccard_lag1"), (10, "jaccard_lag10"),
                                 (100, "jaccard_lag100")):
                    if k - lag in keys_hist:
                        j = jaccard(keys_hist[k - lag], keys_hist[k])
                        if j is not None:
                            s3[key].append(j)
    s1 = {h: {"on": arms["perturbation_on"][h],
              "off": arms["perturbation_off"][h],
              "retained": (arms["perturbation_off"][h] / arms["perturbation_on"][h]
                           if arms["perturbation_on"][h] else None)}
          for h in HORIZONS}
    s3 = {k: (float(np.mean(v)) if v else None) for k, v in s3.items()}
    s4["p_same_winner"] = (s4["same_winner"] / s4["contested"]
                           if s4["contested"] else None)
    s4["p_expected_if_rerolled"] = (s4["expected_if_rerolled"] / s4["contested"]
                                    if s4["contested"] else None)

    # S2
    s2 = {"perturbation_off": twin(variant, warm, tick, par_off, rng, n, spacing),
          "perturbation_on": twin(variant, warm, tick, par_on, rng, n, spacing)}
    return {"variant": variant, "semantics_id": V.SEMANTICS_ID[variant],
            "n": n, "warmup": warmup, "follow": follow,
            "seed_index": seed_index, "seed": seed, "rng_seed": rng_seed,
            "S0": s0, "S1": s1, "S2": s2, "S3": s3, "S4": s4,
            "wall_seconds": time.time() - t0}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("variant", choices=V.VARIANTS)
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--follow", type=int, default=500)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--spacing", type=int, default=32)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    for s in range(a.seeds):
        res = battery(a.variant, a.n, a.warmup, a.follow, s, a.spacing)
        path = os.path.join(a.out_dir, "scout_%s_n%d_s%d.json" % (a.variant, a.n, s))
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True, default=float)
            fh.write("\n")
        print("wrote %s (%.0fs)" % (path, res["wall_seconds"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
