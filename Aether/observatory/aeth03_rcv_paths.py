"""Block B probe: does the substrate ORGANISE rcv's relay, or only execute it?

POST HOC, descriptive, labelled so. Under `rcv` a difference travels along
receipt-triggered emissions; each relay's direction is its own arg0. If the
relay network is the frozen random background, the SAME origin site flipped
at different times should send its divergence along the SAME paths (high
footprint overlap regardless of time gap). If the medium reorganises, the
overlap should fall as the gap grows.

For each of K origin sites (active or receipt-active at the first fork):
  - fork at t0, t0+200, t0+400 of ONE continuing world, flip the same bit of
    the same field at that site, follow `ticks` ticks, record the set of
    sites that EVER differed (the footprint);
  - control A (content): at t0, flip a DIFFERENT bit/field at the same site;
  - control B (baseline): footprints of different origin sites at t0.
Reported: mean Jaccard overlap of footprints for (same site, gap 200), (same
site, gap 400), (same site and time, different bit), (different sites),
over origins whose footprints are non-trivial (>= 3 sites) in both members
of the pair. Perturbation OFF (the arm where rcv's propagation is its own).
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


def footprint(w0, origin, field, bit, par, tick0, ticks):
    a, b = w0.copy(), w0.copy()
    b.f[field][origin] ^= np.uint8(1 << bit)
    ever, _ = P.diff_masks(a, b)
    for t in range(1, ticks + 1):
        a.step(tick0 + t, par)
        b.step(tick0 + t, par)
        site, _ = P.diff_masks(a, b)
        ever |= site
    return ever


def jac(x, y):
    u = (x | y).sum()
    return float((x & y).sum()) / u if u else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--law", default="rcv")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=300)
    ap.add_argument("--origins", type=int, default=32)
    ap.add_argument("--seed-index", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    seed, rng_seed = S.SEED0 + a.seed_index, S.RNG0 + a.seed_index
    rng = np.random.default_rng(0x9A7 + a.seed_index)
    par_on, par_off = S.params(seed, S.MUT_ON), S.params(seed, 0)
    w = P.World(a.law, S.initial(a.law, a.n, rng_seed))
    for t in range(1, a.warmup + 1):
        w.step(t, par_on)
    em = S.emitters(a.law, w.f, par_on["write_cost"]) | (
        w.received & (w.f[4].astype(np.int64) >= par_on["write_cost"]))
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), a.origins, replace=False)]
    specs = [((int(p[0]), int(p[1])), int(rng.integers(5)), int(rng.integers(8)),
              int(rng.integers(5)), int(rng.integers(8))) for p in pick]
    # the continuing world (perturbation OFF from the fork on) at t0, +200, +400
    snaps = {0: w.copy()}
    cur = w.copy()
    for t in range(1, 401):
        cur.step(a.warmup + t, par_off)
        if t in (200, 400):
            snaps[t] = cur.copy()
    fp = {}
    for i, (o, f1, b1, f2, b2) in enumerate(specs):
        for gap, snap in snaps.items():
            fp[(i, gap)] = footprint(snap, o, f1, b1, par_off, a.warmup + gap, a.ticks)
        fp[(i, "alt")] = footprint(snaps[0], o, f2, b2, par_off, a.warmup, a.ticks)
    big = lambda m: m.sum() >= 3                              # noqa: E731
    res = {"same_site_gap200": [], "same_site_gap400": [], "same_time_other_bit": [],
           "different_sites": []}
    for i in range(len(specs)):
        for key, other in (("same_site_gap200", (i, 200)), ("same_site_gap400", (i, 400)),
                           ("same_time_other_bit", (i, "alt"))):
            if big(fp[(i, 0)]) and big(fp[other]):
                res[key].append(jac(fp[(i, 0)], fp[other]))
        j = (i + 1) % len(specs)
        if big(fp[(i, 0)]) and big(fp[(j, 0)]):
            res["different_sites"].append(jac(fp[(i, 0)], fp[(j, 0)]))
    summary = {k: {"pairs": len(v), "mean_jaccard": (float(np.mean(v)) if v else None)}
               for k, v in res.items()}
    out = {"post_hoc": True, "law": a.law, "n": a.n, "ticks": a.ticks,
           "seed_index": a.seed_index, "origins": a.origins,
           "nontrivial_footprints_t0": int(sum(big(fp[(i, 0)]) for i in range(len(specs)))),
           "summary": summary, "pairs": res}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"nontrivial_t0": out["nontrivial_footprints_t0"], "summary": summary},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
