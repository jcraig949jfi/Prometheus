"""AETH-03 ladder 2 intervention: carrier ablation (PHYSICS_DESIGN_02 s2.4).

Run only for a law that earned it. Same twins as the propagation assay
(one bit at an active-emitter origin, identical hash-keyed perturbation),
perturbation OFF. In BOTH twins, before every tick, energy is set to 0 on
a ring two sites thick (Manhattan radius 5-6 around the origin): nothing
on it can emit, whether by opcode or by receipt. SHAM: the identical ring
shape, same treatment, centred n/4 sites away along a row, so it does not
enclose the origin.

Measured per origin: whether the divergence ever reaches Manhattan radius
>= 8 from the origin (outside the ring), and the max radius reached.

Supported (propagation runs through active matter) if the ABLATION share
of origins reaching radius >= 8 is at least 80% lower than the SHAM
share. Not supported otherwise -- then the law moves influence through
starved matter, and the mechanism is investigated before anything else
is claimed.
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

from observatory import aeth03_propagation as P          # noqa: E402
from observatory import aeth03_scouts as S               # noqa: E402

RING = (5, 6)
OUTSIDE = 8


def ring_mask(n, r0, c0):
    d = P.manhattan_from(n, r0, c0)
    return (d >= RING[0]) & (d <= RING[1])


def ablated_pair(w0, origin, field, bit, par, tick0, ticks, ring):
    n = w0.f[0].shape[0]
    dist = P.manhattan_from(n, *origin)
    a, b = w0.copy(), w0.copy()
    b.f[field][origin] ^= np.uint8(1 << bit)
    max_r = 0
    for t in range(1, ticks + 1):
        for wld in (a, b):
            wld.f[4] = np.where(ring, np.uint8(0), wld.f[4]).astype(np.uint8)
        a.step(tick0 + t, par)
        b.step(tick0 + t, par)
        site, _pf = P.diff_masks(a, b)
        if site.any():
            max_r = max(max_r, int(dist[site].max()))
    return {"max_radius": max_r, "reached_outside": max_r >= OUTSIDE}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("variant")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--origins", type=int, default=32)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--perturbation", choices=("off", "on"), default="off",
                    help="PHYSICS_DESIGN_02 s2.4 specifies off; 'on' is run "
                         "only as a labelled extension")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    n = a.n
    seed, rng_seed = S.SEED0 + a.seed_index, S.RNG0 + a.seed_index
    rng = np.random.default_rng(0xAB1A + a.seed_index)
    par_on, par_off = S.params(seed, S.MUT_ON), S.params(seed, 0)
    w = P.World(a.variant, S.initial(a.variant, n, rng_seed))
    for t in range(1, a.warmup + 1):
        w.step(t, par_on)
    em = S.emitters(a.variant, w.f, par_on["write_cost"])
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), min(a.origins, len(cand)), replace=False)]
    rows = []
    for p in pick:
        origin = (int(p[0]), int(p[1]))
        field, bit = int(rng.integers(5)), int(rng.integers(8))
        par = par_off if a.perturbation == "off" else par_on
        abl = ablated_pair(w, origin, field, bit, par, a.warmup, a.ticks,
                           ring_mask(n, *origin))
        sham = ablated_pair(w, origin, field, bit, par, a.warmup, a.ticks,
                            ring_mask(n, origin[0], (origin[1] + n // 4) % n))
        rows.append({"origin": list(origin), "field": field, "bit": bit,
                     "ablation": abl, "sham": sham})
    share_abl = float(np.mean([r["ablation"]["reached_outside"] for r in rows]))
    share_sham = float(np.mean([r["sham"]["reached_outside"] for r in rows]))
    out = {"variant": a.variant, "n": n, "seed_index": a.seed_index,
           "perturbation": a.perturbation,
           "ring": RING, "outside_radius": OUTSIDE, "rows": rows,
           "share_outside_ablation": share_abl, "share_outside_sham": share_sham,
           "reduction": (1 - share_abl / share_sham) if share_sham else None,
           "supported": bool(share_sham and share_abl <= 0.2 * share_sham)}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in ("share_outside_ablation",
                                          "share_outside_sham", "reduction",
                                          "supported")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
