"""Block E's preregistered E-P2 probe, and the falsifier for Block D's positives.

PHYSICS_DESIGN_03 s3 said: if more than 25% of fwd's content differences at
generation >= 2 are "altered", classify the altered events by cause. They
were (92%). The same classification is the first falsifier for the two
combinations that passed N1/N2 (rcv_add, rcv_str): their "content"
propagation could be the same thing.

For every new template-field difference (site x, field f) at tick t+1, with
the twins' observers, classify:

  WRITTEN_BOTH   both worlds had a winning write into (x, f) this tick and
                 the committed values differ -> content that differs
                 ARRIVED in both worlds. Split: PRESERVED (XOR == the
                 origin's flip) vs TRANSFORMED (any other XOR).
  WRITTEN_ONE    exactly one world wrote into (x, f): the difference is the
                 PRESENCE of a write -- a timing difference leaving a mark,
                 not content travelling.
  WRITTEN_NONE   neither world wrote (only possible via perturbation or
                 add-style accumulation into an existing difference; counted
                 separately).

And, for every new difference (any field), the youngest AGE among its
differing parents (ticks the parent has differed continuously). DELAYED if
that youngest age is >= 20: the difference was caused only by differences
that had been standing for 20+ ticks -- stored state being re-emitted.
Reported as shares, per law, perturbation OFF.

POST HOC with respect to the Block D verdicts (it was written after they
were computed); the E-P2 trigger itself was preregistered.
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

from observatory import aeth01_graph as G                # noqa: E402
from observatory import aeth03_propagation as P          # noqa: E402
from observatory import aeth03_scouts as S               # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

DELAY = 20


def step_obs(w, tick, par):
    """World.step with the observer exported (winner slot per field)."""
    h, wd = w.f[0].shape
    kw = {}
    if w.variant in V.RCV_FAMILY:
        kw["received"] = w.extra["received"]
    if w.variant == "fwd":
        kw["received_value"] = w.extra["received_value"]
    obs = []
    out = V.step(w.variant, H=h, W=wd, tick=tick, opcode=w.f[0], arg0=w.f[1],
                 arg1=w.f[2], payload=w.f[3], energy=w.f[4], observer=obs, **kw, **par)
    w.f = list(out[:5])
    if w.variant in V.RCV_FAMILY:
        w.extra["received"] = out[5]["received"]
    if w.variant == "fwd":
        w.extra["received_value"] = out[5]["received_value"]
    return [G.unpack(o)[0] != G.NO_WINNER for o in obs]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("law")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--origins", type=int, default=32)
    ap.add_argument("--seed-index", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    seed, rng_seed = S.SEED0 + a.seed_index, S.RNG0 + a.seed_index
    rng = np.random.default_rng(0xB0A7 + a.seed_index)      # the assay's origins
    par_on, par = S.params(seed, S.MUT_ON), S.params(seed, 0)
    w = P.World(a.law, S.initial(a.law, a.n, rng_seed))
    for t in range(1, a.warmup + 1):
        w.step(t, par_on)
    em = S.emitters(a.law, w.f, par_on["write_cost"])
    if a.law in V.RCV_FAMILY:
        em = em | (w.received & (w.f[4].astype(np.int64) >= par_on["write_cost"]))
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), min(a.origins, len(cand)), replace=False)]
    specs = [(tuple(int(x) for x in p), int(rng.integers(5)), int(rng.integers(8)))
             for p in pick]
    nb = P.stencil(a.law)
    tot = {"content_new": 0, "written_both": 0, "both_preserved": 0,
           "both_transformed": 0, "written_one": 0, "written_none": 0,
           "new_any": 0, "delayed": 0, "gen_ge2_content": 0,
           "gen_ge2_written_both": 0, "gen_ge2_both_transformed": 0}
    for origin, field, bit in specs:
        a0, b0 = w.copy(), w.copy()
        b0.f[field][origin] ^= np.uint8(1 << bit)
        sig = np.uint8(1 << bit)
        site, pf = P.diff_masks(a0, b0)
        age = np.where(site, 1, 0).astype(np.int32)
        gen = np.where(site, np.int32(0), P.BIG)
        for t in range(1, a.ticks + 1):
            prev_site, prev_pf, prev_age, prev_gen = site, pf, age, gen
            wa = step_obs(a0, a.warmup + t, par)
            wb = step_obs(b0, a.warmup + t, par)
            site, pf = P.diff_masks(a0, b0)
            newly = site & ~prev_site
            pmin = P.neighbour_min(np.where(prev_site, prev_gen, P.BIG), nb)
            gen = np.where(site & prev_site, prev_gen, P.BIG)
            gen = np.where(newly, pmin + 1, gen)
            # youngest parent age among differing neighbours
            young = np.full(site.shape, P.BIG, dtype=np.int32)
            for dr, dc in nb:
                young = np.minimum(young, np.roll(np.where(prev_site, prev_age, P.BIG),
                                                  (dr, dc), axis=(0, 1)))
            if newly.any():
                tot["new_any"] += int(newly.sum())
                tot["delayed"] += int((newly & (young >= DELAY) & (young < P.BIG)).sum())
            for i in range(4):
                fresh = pf[i] & ~prev_pf[i]
                if not fresh.any():
                    continue
                both = fresh & wa[i] & wb[i]
                one = fresh & (wa[i] ^ wb[i])
                none = fresh & ~wa[i] & ~wb[i]
                xs = a0.f[i] ^ b0.f[i]
                g2 = fresh & (gen >= 2) & (gen < P.BIG)
                tot["content_new"] += int(fresh.sum())
                tot["written_both"] += int(both.sum())
                tot["both_preserved"] += int((both & (xs == sig)).sum())
                tot["both_transformed"] += int((both & (xs != sig)).sum())
                tot["written_one"] += int(one.sum())
                tot["written_none"] += int(none.sum())
                tot["gen_ge2_content"] += int(g2.sum())
                tot["gen_ge2_written_both"] += int((g2 & both).sum())
                tot["gen_ge2_both_transformed"] += int((g2 & both & (xs != sig)).sum())
            age = np.where(site, np.where(prev_site, prev_age + 1, 1), 0).astype(np.int32)
    c = float(max(1, tot["content_new"]))
    g = float(max(1, tot["gen_ge2_content"]))
    shares = {"written_both": tot["written_both"] / c, "written_one": tot["written_one"] / c,
              "written_none": tot["written_none"] / c,
              "both_preserved_of_both": (tot["both_preserved"] / float(tot["written_both"])
                                         if tot["written_both"] else None),
              "gen_ge2_written_both": tot["gen_ge2_written_both"] / g,
              "gen_ge2_both_transformed": tot["gen_ge2_both_transformed"] / g,
              "delayed_of_new_any": tot["delayed"] / float(max(1, tot["new_any"]))}
    out = {"post_hoc_wrt_block_d": True, "law": a.law, "seed_index": a.seed_index,
           "perturbation": "off", "origins": len(specs), "totals": tot, "shares": shares}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out["shares"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
