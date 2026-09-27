"""AETH-03 Block C: does locality depend on the observation horizon?

The ladder-2 assay followed each twin pair for 400 ticks at 128^2. Every
law is local (influence moves at most one site per tick; `mov` two), so a
difference COULD in principle travel 10,000 sites in 10,000 ticks: a
larger lattice alone cannot answer "is anything slow being missed?". Time
must vary first, with a guard that proves no footprint came near a
boundary.

DESIGN. One 256^2 twin pair per (law, seed, arm), carrying 16 origins at
once on a 4x4 grid with 64-site spacing: one bit flipped at an active
emitter near each grid point. Differences from different origins evolve
independently unless they meet (locality), so each difference is
attributed to its nearest origin, and a region is BREACHED -- its numbers
no longer attributable -- as soon as any difference assigned to it lies
at Chebyshev distance >= 28 from its origin (4 sites short of the region
edge). Breached regions are reported and excluded from per-origin
statistics from that tick on; a breach is itself a result (reach >= 28).

Per origin, at horizons 500, 1000, 2000, 5000, 10000: alive (any
difference), max radius so far, current radius, differing sites, max
generation so far (the assay's adjacency generation -- a LOWER BOUND on
causal depth, see PROPAGATION_ASSAY_AUDIT.md), and the last tick at which
a new maximum generation appeared.

The question it answers: do conclusions drawn at +400 (local, dying,
bounded) still hold at +2,000 and +10,000, or does anything keep growing?
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

from observatory import aeth03_propagation as P          # noqa: E402
from observatory import aeth03_scouts as S               # noqa: E402

HORIZONS = (100, 400, 500, 1000, 2000, 5000, 10000)
SPACING = 64
BREACH = 28


def chebyshev_from(n, r0, c0):
    rows, cols = np.indices((n, n))
    dr = np.abs(rows - r0)
    dc = np.abs(cols - c0)
    return np.maximum(np.minimum(dr, n - dr), np.minimum(dc, n - dc))


def run(law, n, warmup, ticks, seed_index, mut, progress_every=500):
    seed, rng_seed = S.SEED0 + seed_index, S.RNG0 + seed_index
    rng = np.random.default_rng(0x10C0 + seed_index)
    par_on = S.params(seed, S.MUT_ON)
    par = S.params(seed, mut)
    w = P.World(law, S.initial(law, n, rng_seed))
    for t in range(1, warmup + 1):
        w.step(t, par_on)
    em = S.emitters(law, w.f, par_on["write_cost"])
    if law in P.V.RCV_FAMILY:
        em = em | (w.received & (w.f[4].astype(np.int64) >= par_on["write_cost"]))
    origins = []
    half = SPACING // 2
    for gr in range(half, n, SPACING):
        for gc in range(half, n, SPACING):
            box = em[gr - 6:gr + 6, gc - 6:gc + 6]
            rr, cc = np.nonzero(box)
            if not len(rr):
                continue
            k = int(rng.integers(len(rr)))
            origins.append((gr - 6 + int(rr[k]), gc - 6 + int(cc[k]),
                            int(rng.integers(5)), int(rng.integers(8))))
    a, b = w.copy(), w.copy()
    for (r, c, f, bit) in origins:
        b.f[f][r, c] ^= np.uint8(1 << bit)
    k = len(origins)
    cheb = np.stack([chebyshev_from(n, r, c) for r, c, _f, _b in origins])
    manh = np.stack([P.manhattan_from(n, r, c) for r, c, _f, _b in origins])
    owner = np.argmin(cheb, axis=0)
    nb = P.stencil(law)
    site, _ = P.diff_masks(a, b)
    gen = np.where(site, np.int32(0), P.BIG)
    st = [{"origin": [r, c], "field": f, "bit": bit, "breached_at": None,
           "max_radius": 0, "max_gen": 0, "last_new_gen_tick": 0,
           "last_alive_tick": 0, "horizons": {}} for r, c, f, bit in origins]
    violations = 0
    t0 = time.time()
    for t in range(1, ticks + 1):
        prev_site, prev_gen = site, gen
        a.step(warmup + t, par)
        b.step(warmup + t, par)
        site, _ = P.diff_masks(a, b)
        newly = site & ~prev_site
        pmin = P.neighbour_min(np.where(prev_site, prev_gen, P.BIG), nb)
        orphan = newly & (pmin >= P.BIG)
        violations += int(orphan.sum())
        gen = np.where(site & prev_site, prev_gen, P.BIG)
        gen = np.where(newly & ~orphan, pmin + 1, gen)
        if site.any():
            idx = np.flatnonzero(site.ravel())
            own = owner.ravel()[idx]
            for j in np.unique(own):
                s = st[j]
                if s["breached_at"] is not None:
                    continue
                member_idx = idx[own == j]
                cd = cheb[j].ravel()[member_idx]
                if cd.max() >= BREACH:
                    s["breached_at"] = t
                    continue
                md = int(manh[j].ravel()[member_idx].max())
                g = int(gen.ravel()[member_idx].max())
                s["max_radius"] = max(s["max_radius"], md)
                if g > s["max_gen"]:
                    s["max_gen"] = g
                    s["last_new_gen_tick"] = t
                s["last_alive_tick"] = t
        if t in HORIZONS:
            per = {}
            if site.any():
                idx = np.flatnonzero(site.ravel())
                own = owner.ravel()[idx]
                for j in range(k):
                    per[j] = idx[own == j]
            for j in range(k):
                s = st[j]
                if s["breached_at"] is not None:
                    s["horizons"][str(t)] = {"breached": True}
                    continue
                member_idx = per.get(j, np.zeros(0, dtype=np.int64))
                s["horizons"][str(t)] = {
                    "alive": bool(len(member_idx)),
                    "differing_sites": int(len(member_idx)),
                    "radius_now": int(manh[j].ravel()[member_idx].max()) if len(member_idx) else 0,
                    "max_radius_so_far": s["max_radius"],
                    "max_gen_so_far": s["max_gen"],
                    "last_new_gen_tick": s["last_new_gen_tick"],
                }
        if progress_every and t % progress_every == 0:
            print("  %s seed %d mut %s tick %d/%d %.0fs" % (law, seed_index, bool(mut),
                                                        t, ticks, time.time() - t0),
                  file=sys.stderr, flush=True)
    return {"law": law, "n": n, "warmup": warmup, "ticks": ticks,
            "seed_index": seed_index, "perturbation": "on" if mut else "off",
            "origins": st, "locality_violations": violations,
            "spacing": SPACING, "breach_chebyshev": BREACH,
            "wall_seconds": time.time() - t0}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("law")
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=10000)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--perturbation", choices=("off", "on"), default="off")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = run(a.law, a.n, a.warmup, a.ticks, a.seed_index,
              S.MUT_ON if a.perturbation == "on" else 0)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote %s (%.0fs) violations=%d" % (a.out, res["wall_seconds"],
                                              res["locality_violations"]),
          file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
