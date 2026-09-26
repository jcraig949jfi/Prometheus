"""AETH-03 ladder 2: paired-world propagation assay.

Operator directive 2026-09-26 "NEXT ROUND"
(roles/Aether/prompts/2026-09-26_next_round). Question: can a local state
difference causally propagate into a larger region under primitive local
physics?

METHOD. From a warmed world, fork two copies A and B that are identical
except for ONE BIT at one origin site. Step both under the same law, the
same seed and the same parameters; perturbation (Mu) is a hash of
(seed, tick, site, field), so both worlds receive the identical injected
stream and any difference between them is caused by the flipped bit.
Run the pair with perturbation ON and, separately, OFF.

WHY GENERATIONS ARE EXACT HERE. Every law in `aeth03_variants` except
`mov` is strictly radius-1 (`mov` is radius 2; see RADIUS below): a site's next state is a function of its own state and its four
neighbours' states at the previous tick (plus the shared hash stream). A
site that does not differ at t and has no differing neighbour at t cannot
differ at t+1. So every newly differing site has at least one differing
PARENT among its four neighbours, and its causal generation is

    gen(x, t+1) = 1 + min{ gen(y, t) : y a differing neighbour of x at t }

(the length of the shortest causal chain from the origin). The assay
CHECKS this every tick and counts violations; a nonzero count means the
instrument, not the physics, is wrong, and the result is void.

    generation 0      the origin itself
    generation 1      DIRECT MECHANICAL SPREAD: made to differ by the origin
    generation >= 2   SECONDARY CAUSAL SPREAD: made to differ by sites that
                      were themselves made to differ
    SUSTAINED         an origin whose divergence reaches generation >= 5,
                      a Manhattan radius >= 5, and is still adding new
                      generations after tick 50

Raw Hamming distance is reported but never used as the verdict: a flipped
byte that simply sits in an inert site differs forever with generation 0
and propagates nothing.

A site that stops differing and later differs again is a RE-ENTRY. A new
difference with two or more differing parents is a BRANCH point.

Instrument controls, built in:
  - locality violations must be 0 (checked every tick, every origin);
  - `--selftest-null`: flip the bit twice (B == A); every tick must show
    zero differences.

`rcv` carries one bit of per-site state ("received a winning template
write last tick"); it is part of the compared state.
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

from observatory import aeth03_scouts as S               # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402

HORIZONS = (1, 2, 5, 10, 25, 50, 100, 200, 300, 400)
BIG = np.int32(1 << 30)
_NB = ((-1, 0), (1, 0), (0, 1), (0, -1))
_NB2 = tuple((dr, dc) for dr in range(-2, 3) for dc in range(-2, 3)
             if 0 < abs(dr) + abs(dc) <= 2)
# Causal radius of one tick, per law. Every law is radius 1 EXCEPT `mov`:
# whether a source's payload is cleared depends on whether its proposal
# WON at its target, which depends on the target's other neighbours, two
# sites from the source. For `mov` the parent search therefore covers the
# Manhattan-2 neighbourhood, and one generation may span two sites.
RADIUS = {"mov": 2}


def stencil(variant):
    return _NB2 if RADIUS.get(variant, 1) == 2 else _NB


class World:
    """Five byte fields plus rcv's received flag, stepped under one law."""

    def __init__(self, variant, fields, received=None):
        self.variant = variant
        self.f = [x.copy() for x in fields]
        n = fields[0].shape[0]
        self.received = (received.copy() if received is not None
                         else np.zeros((n, n), dtype=bool))

    def copy(self):
        return World(self.variant, self.f, self.received)

    def step(self, tick, par):
        h, w = self.f[0].shape
        out = V.step(self.variant, H=h, W=w, tick=tick, opcode=self.f[0],
                     arg0=self.f[1], arg1=self.f[2], payload=self.f[3],
                     energy=self.f[4],
                     received=self.received if self.variant == "rcv" else None,
                     **par)
        self.f = list(out[:5])
        if self.variant == "rcv":
            self.received = out[5]["received"]


def diff_masks(a, b):
    per_field = [a.f[i] != b.f[i] for i in range(5)]
    site = per_field[0] | per_field[1] | per_field[2] | per_field[3] | per_field[4]
    site = site | (a.received != b.received)
    return site, per_field


def neighbour_min(gen, nb=_NB):
    """min over the stencil neighbours of gen (BIG where not differing)."""
    out = np.full(gen.shape, BIG, dtype=np.int32)
    for dr, dc in nb:
        out = np.minimum(out, np.roll(gen, (dr, dc), axis=(0, 1)))
    return out


def neighbour_count(mask, nb=_NB):
    out = np.zeros(mask.shape, dtype=np.int8)
    for dr, dc in nb:
        out += np.roll(mask, (dr, dc), axis=(0, 1)).astype(np.int8)
    return out


def manhattan_from(n, r0, c0):
    rows, cols = np.indices((n, n))
    dr = np.abs(rows - r0)
    dc = np.abs(cols - c0)
    return np.minimum(dr, n - dr) + np.minimum(dc, n - dc)


def components(mask):
    """4-connected components on the torus (union-find over rows/cols)."""
    n = mask.shape[0]
    idx = np.flatnonzero(mask.ravel())
    if not len(idx):
        return 0, 0
    parent = {int(i): int(i) for i in idx}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    flat = mask.ravel()
    for i in idx:
        r, c = divmod(int(i), n)
        for j in (r * n + (c + 1) % n, ((r + 1) % n) * n + c):
            if flat[j]:
                a, b = find(int(i)), find(int(j))
                if a != b:
                    parent[a] = b
    roots = {}
    for i in idx:
        k = find(int(i))
        roots[k] = roots.get(k, 0) + 1
    return len(roots), max(roots.values())


def pair_run(a0, origin, field, bit, par, tick0, ticks, dist, null=False):
    """Follow one twin pair. Returns per-horizon rows and a summary."""
    n = a0.f[0].shape[0]
    nb = stencil(a0.variant)
    a, b = a0.copy(), a0.copy()
    r0, c0 = origin
    b.f[field][r0, c0] ^= np.uint8(1 << bit)
    if null:
        b.f[field][r0, c0] ^= np.uint8(1 << bit)
    site, _pf = diff_masks(a, b)
    gen = np.where(site, np.int32(0), BIG)
    ever = site.copy()
    violations = reentries = branches = new_total = 0
    gen_hist = np.zeros(64, dtype=np.int64)      # new differences by generation
    max_gen = 0 if site.any() else -1
    max_radius = 0
    last_alive = 0 if site.any() else -1
    last_new_gen_tick = 0
    rows = {}
    for t in range(1, ticks + 1):
        prev_site, prev_gen = site, gen
        a.step(tick0 + t, par)
        b.step(tick0 + t, par)
        site, per_field = diff_masks(a, b)
        newly = site & ~prev_site
        pmin = neighbour_min(np.where(prev_site, prev_gen, BIG), nb)
        orphan = newly & (pmin >= BIG)
        violations += int(orphan.sum())
        gen = np.where(site & prev_site, prev_gen, BIG)
        gen = np.where(newly & ~orphan, pmin + 1, gen)
        nk = int(newly.sum())
        if nk:
            new_total += nk
            g_new = gen[newly & ~orphan]
            gen_hist += np.bincount(np.minimum(g_new, 63), minlength=64)
            branches += int((newly & (neighbour_count(prev_site, nb) >= 2)).sum())
            reentries += int((newly & ever).sum())
            gmax = int(g_new.max()) if len(g_new) else 0
            if gmax > max_gen:
                max_gen = gmax
                last_new_gen_tick = t
        ever |= site
        if site.any():
            last_alive = t
            max_radius = max(max_radius, int(dist[site].max()))
        if t in HORIZONS:
            live = gen[site]
            ncomp, largest = components(site)
            rows[t] = {
                "differing_sites": int(site.sum()),
                "differing_pairs": int(sum(int(m.sum()) for m in per_field)),
                "differing_pairs_by_field": [int(m.sum()) for m in per_field],
                "radius_now": int(dist[site].max()) if site.any() else 0,
                "max_generation_now": int(live.max()) if len(live) else -1,
                "sites_gen_ge4_now": int((live >= 4).sum()),
                "components": ncomp, "largest_component": largest,
            }
    summary = {
        "origin": [int(r0), int(c0)], "field": int(field), "bit": int(bit),
        "died": bool(not site.any()),
        "duration": int(last_alive),
        "max_radius": int(max_radius),
        "max_generation": int(max_gen),
        "last_new_generation_tick": int(last_new_gen_tick),
        "new_differences": int(new_total),
        "new_by_generation": [int(x) for x in gen_hist[:16]],
        "new_gen1": int(gen_hist[1]),
        "new_gen_ge2": int(gen_hist[2:].sum()),
        "new_gen_ge5": int(gen_hist[5:].sum()),
        "branch_points": int(branches),
        "reentries": int(reentries),
        "locality_violations": int(violations),
        "final_differing_fraction": float(site.mean()),
    }
    summary["class"] = classify(summary)
    return rows, summary


def classify(s):
    if s["max_generation"] <= 0:
        return "INERT"            # only the flipped byte ever differed
    if s["max_radius"] <= 1 and s["max_generation"] <= 1:
        return "DIRECT_ONLY"
    if (s["max_generation"] >= 5 and s["max_radius"] >= 5
            and s["last_new_generation_tick"] > 50):
        return "SUSTAINED"
    if s["max_generation"] >= 2:
        return "SECONDARY"
    return "DIRECT_ONLY"


def assay(variant, n, warmup, ticks, origins, seed_index, null=False):
    seed, rng_seed = S.SEED0 + seed_index, S.RNG0 + seed_index
    rng = np.random.default_rng(0xB0A7 + seed_index)
    t0 = time.time()
    fields = S.initial(variant, n, rng_seed)
    par_on = S.params(seed, S.MUT_ON)
    w = World(variant, fields)
    for t in range(1, warmup + 1):
        w.step(t, par_on)
    em = S.emitters(variant, w.f, par_on["write_cost"])
    if variant == "rcv":
        em = em | (w.received & (w.f[4].astype(np.int64) >= par_on["write_cost"]))
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), min(origins, len(cand)), replace=False)]
    specs = [(tuple(int(x) for x in p), int(rng.integers(5)), int(rng.integers(8)))
             for p in pick]
    out = {"variant": variant, "semantics_id": V.SEMANTICS_ID[variant],
           "n": n, "warmup": warmup, "ticks": ticks, "seed_index": seed_index,
           "seed": seed, "rng_seed": rng_seed, "null_selftest": null,
           "arms": {}}
    for arm, mut in (("perturbation_off", 0), ("perturbation_on", S.MUT_ON)):
        par = S.params(seed, mut)
        runs = []
        for origin, field, bit in specs:
            dist = manhattan_from(n, *origin)
            rows, summ = pair_run(w, origin, field, bit, par, warmup, ticks,
                                  dist, null=null)
            runs.append({"summary": summ, "horizons": rows})
        out["arms"][arm] = runs
    out["wall_seconds"] = time.time() - t0
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("variant", choices=V.VARIANTS)
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--origins", type=int, default=24)
    ap.add_argument("--seeds", type=str, default="0,1,2")
    ap.add_argument("--selftest-null", action="store_true")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    for s in [int(x) for x in a.seeds.split(",")]:
        res = assay(a.variant, a.n, a.warmup, a.ticks, a.origins, s,
                    null=a.selftest_null)
        tag = "null_" if a.selftest_null else ""
        path = os.path.join(a.out_dir, "prop_%s%s_n%d_s%d.json"
                            % (tag, a.variant, a.n, s))
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
            fh.write("\n")
        viol = sum(r["summary"]["locality_violations"]
                   for arm in res["arms"].values() for r in arm)
        print("wrote %s (%.0fs) locality_violations=%d"
              % (path, res["wall_seconds"], viol), file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
