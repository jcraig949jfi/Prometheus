"""AETH-V2B-ROUTE01: content-dependent retargeting, measured with the PROP01 paired-world causal assay (unchanged).

Laws (B_balanced, P0, D50):
  V1  aeth01.v1
  L1  aeth01.reaim1       winner (any field): arg0 += 1, unless its arg0 was written
  RT  aeth01.route1       winner (any field): arg0 := (byte it displaced at its target, pre-tick) & 3, unless its arg0
                          was written. One law difference vs reaim1; payload, arg1 untouched.
  RN  aeth01.randaim1     NULL: winner (any field): arg0 := keyed-hash(seed, tick, site) & 3, unless its arg0 was
                          written. Same trigger and value range as RT, no dependence on content.

PROP01 assay text follows.
AETH-V2B-PROP01: multi-generation causal reach (paired-world impulse assay with conservative causal attribution).

Worlds CONTROL and IMPULSE share initial state, RNG/physics stream and parameters. After a shared warm-up of WARM
ticks, IMPULSE gets exactly one change: bit 0 of the payload byte at site O, where O is drawn (rng seeded by the seed
index) uniformly from sites that are WRITE with energy >= write_cost at warm-up end. Both worlds then run H ticks
in lockstep with the frozen kernel's observer channel.

CONSERVATIVE ATTRIBUTION (per tick, for every site that is NOT divergent before the tick and IS after it):
  candidate parents, in priority of nothing -- all are collected and the minimum-generation one is kept:
   (a) a winning source (either world) into any newly divergent field of the site, if that source was divergent
       before the tick;
   (b) for rule-driven fields (uptake / re-aim / recoil act on the WINNER's own payload or arg0): a target the site
       itself won into (either world), if that target was divergent before the tick.
  none -> UNKNOWN (generation -1). Never inferred from state differencing alone.
  generation(site) = generation(parent) + 1; the impulse origin is generation 0.
TYPE of a new divergence (per site, from its newly divergent fields):
  STRUCT  the winning source differs between the worlds (the divergence changed WHO writes) -- secondary causal
          effect via control structure
  CARRY   same winner in both worlds, different delivered value (a divergent byte moved/copied one step)
  RULE    no winning write into that field in either world (rule-driven or energy settlement)
Per-unit records: divergent sites/fields over time, max Chebyshev radius from O, generation histogram, type counts by
generation, extinction tick, re-entry events, and the parent array (for the counterfactual cut).

COUNTERFACTUAL CUT (--cut): a third world CUT runs alongside; from the tick B first diverged onward, B's five fields
are CLAMPED to CONTROL's values every tick (B is neutralized; a one-shot restore would be overwritten at once by a
persistent upstream copier). B = the earliest generation-1 site that has >= 1 STRUCT-or-CARRY child in the
IMPULSE tree (taken from a previous uncut run of the same seed). Reported: of B's IMPULSE-tree descendants, the
fraction that ever diverge (vs CONTROL) in CUT, compared with the same quantity for a matched non-descendant set.
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, AETHER, os.path.join(AETHER, "test"), os.path.join(AETHER, "runpod", "aeth01_canary")):
    sys.path.insert(0, p)
from observatory import aeth01_run as R  # noqa: E402

RUNNER_VERSION = "route01_run.v1"
LAWS = {"V1": "aeth01.v1", "L1": "aeth01.reaim1", "RT": "aeth01.route1", "RN": "aeth01.randaim1"}
RANDAIM_DOMAIN = 0x5EED_A1A1
ENERGY = dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8)
DENSITY = 0.50
RNG_SEED_BASE = 0xE2010000
PHYS_SEED_BASE = 0xE2011000
IMPULSE_DOMAIN = 0x1A9F   # same origin rule as PROP01


def table_hash():
    blob = json.dumps({"laws": LAWS, "energy": ENERGY, "dens": DENSITY, "rng": RNG_SEED_BASE,
                       "phys": PHYS_SEED_BASE, "imp": IMPULSE_DOMAIN}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def load_backend(name):
    if name == "gpu":
        import aeth01_gpu_kernel as K
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def digest(fields):
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(np.asarray(getattr(f, "get", lambda: f)())).tobytes())
    return h.hexdigest()[:32]


def law_step(xp, K, law, n, seed, tick, s):
    obs = []
    out = K.gpu_step(n, n, seed, tick, ENERGY["write_cost"], ENERGY["maintenance_cost"],
                     ENERGY["replenish_numer"], ENERGY["replenish_amount"], 0, *s, observer=obs)
    nxt = list(out[:5])
    if law == "V1":
        return nxt, obs
    won_any = xp.zeros((n, n), dtype=bool)
    disp_any = xp.zeros((n, n), dtype=xp.uint8)          # pre-tick byte at the winner's target, any field
    for f in range(5):
        slot = obs[f][0]
        for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
            m = xp.roll(slot == sl, (dr, dc), axis=(0, 1))
            won_any |= m
            disp_any = xp.where(m, xp.roll(s[f], (dr, dc), axis=(0, 1)), disp_any)
    a0w = obs[1][0] != 255
    upd = won_any & ~a0w
    if law == "L1":
        nxt[1] = xp.where(upd, (nxt[1].astype(xp.uint16) + 1).astype(xp.uint8), nxt[1])
    elif law == "RT":
        nxt[1] = xp.where(upd, disp_any & 3, nxt[1]).astype(xp.uint8)
    elif law == "RN":
        packed = K.pack_coords_vec(xp.arange(n).reshape(n, 1), xp.arange(n).reshape(1, n))
        h0 = K.mix64_scalar(xp.uint64(seed) ^ xp.uint64(RANDAIM_DOMAIN))
        h1 = K.mix64_scalar(h0 ^ xp.uint64(tick))
        r = (K.mix64_vec(h1 ^ packed) >> xp.uint64(62)).astype(xp.uint8)
        nxt[1] = xp.where(upd, r, nxt[1]).astype(xp.uint8)
    return nxt, obs


def pick_origin(xp, K, s, k):
    act = (host(s[0]) == K.WRITE_OPCODE) & (host(s[4]).astype(np.int64) >= ENERGY["write_cost"])
    idx = np.flatnonzero(act.ravel())
    rng = np.random.default_rng(IMPULSE_DOMAIN + k)
    return int(idx[rng.integers(0, idx.size)])


def host(x):
    return np.asarray(getattr(x, "get", lambda: x)())


def run_unit(backend, law, k, n, warm, H, cut_site=None, cut_tick=None, digest_every=0, init=None, origin=None):
    xp, K = load_backend(backend)
    if init is None:
        fields, recipe = R.build_initial(R.SPARSE_SOUP, n, n, RNG_SEED_BASE + k, write_density=DENSITY,
                                         energy_mode=R.ENERGY_UNIFORM)
    else:
        fields = [f.copy() for f in init]
    s = [xp.asarray(f) for f in fields]
    phys = PHYS_SEED_BASE + k
    for t in range(warm):
        s, _ = law_step(xp, K, law, n, phys, t + 1, s)
    warm_digest = digest(s)
    o = pick_origin(xp, K, s, k) if origin is None else origin
    oy, ox = divmod(o, n)
    sc = [f.copy() for f in s]
    si = [f.copy() for f in s]
    si[3][oy, ox] ^= np.uint8(1)
    scut = [f.copy() for f in si] if cut_site is not None else None
    N = n * n
    idx = xp.arange(N, dtype=xp.int32).reshape(n, n)
    gen = xp.full((n, n), -9, dtype=xp.int32)          # -9 never divergent; -1 UNKNOWN
    parent = xp.full((n, n), -9, dtype=xp.int32)
    ftick = xp.full((n, n), -1, dtype=xp.int32)
    typ = xp.zeros((n, n), dtype=xp.int8)               # 1 STRUCT, 2 CARRY, 3 RULE
    gen[oy, ox] = 0
    parent[oy, ox] = -1
    ftick[oy, ox] = 0
    ever = xp.zeros((n, n), dtype=bool)
    ever[oy, ox] = True
    cut_ever = xp.zeros((n, n), dtype=bool) if scut is not None else None
    yy = xp.arange(n).reshape(n, 1)
    xx = xp.arange(n).reshape(1, n)
    dy = xp.minimum((yy - oy) % n, (oy - yy) % n)
    dx = xp.minimum((xx - ox) % n, (ox - xx) % n)
    cheb = xp.maximum(dy, dx)
    series = []
    reentry = 0
    gtyp = {}                                           # (gen, type) -> count of new divergent sites
    extinct = None
    t0 = time.time()
    tick0 = warm
    for t in range(H):
        tick = tick0 + t + 1
        div_pre = (sc[0] != si[0]) | (sc[1] != si[1]) | (sc[2] != si[2]) | (sc[3] != si[3]) | (sc[4] != si[4])
        nc, oc = law_step(xp, K, law, n, phys, tick, sc)
        ni, oi = law_step(xp, K, law, n, phys, tick, si)
        dfield = [nc[f] != ni[f] for f in range(5)]
        div_post = dfield[0] | dfield[1] | dfield[2] | dfield[3] | dfield[4]
        new = div_post & ~div_pre
        if bool(new.any()):
            BIG = 1 << 30
            best_g = xp.full((n, n), BIG, dtype=xp.int32)
            best_p = xp.full((n, n), -1, dtype=xp.int32)
            struct = xp.zeros((n, n), dtype=bool)
            carry = xp.zeros((n, n), dtype=bool)
            gpos = xp.where(gen >= 0, gen, BIG)
            for f in range(5):
                nf = new & dfield[f]
                slc, sli = oc[f][0], oi[f][0]
                wrote = (slc != 255) | (sli != 255)
                struct |= nf & wrote & (slc != sli)
                carry |= nf & wrote & (slc == sli)
                for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
                    sdiv = xp.roll(div_pre, (-dr, -dc), axis=(0, 1))
                    sg = xp.roll(gpos, (-dr, -dc), axis=(0, 1))
                    sp = xp.roll(idx, (-dr, -dc), axis=(0, 1))
                    for slot in (slc, sli):
                        m = nf & (slot == sl) & sdiv & (sg < best_g)
                        best_g = xp.where(m, sg, best_g)
                        best_p = xp.where(m, sp, best_p)
                    # (b) rule-driven: this site (as source) won into target t' = site - (dr, dc), which was divergent
                    if f in (1, 3):
                        tdiv = xp.roll(div_pre, (dr, dc), axis=(0, 1))
                        tg = xp.roll(gpos, (dr, dc), axis=(0, 1))
                        tp = xp.roll(idx, (dr, dc), axis=(0, 1))
                        for ob in (oc, oi):
                            for ff in range(4):
                                wonhere = xp.roll(ob[ff][0] == sl, (dr, dc), axis=(0, 1))
                                m = nf & wonhere & tdiv & (tg < best_g)
                                best_g = xp.where(m, tg, best_g)
                                best_p = xp.where(m, tp, best_p)
            known = new & (best_g < BIG)
            unk = new & ~known
            firsttime = new & ~ever
            re = new & ever
            reentry += int(re.sum())
            gnew = xp.where(known, best_g + 1, -1)
            t_new = xp.where(struct, 1, xp.where(carry, 2, 3)).astype(xp.int8)
            upd = firsttime
            gen = xp.where(upd, gnew, gen)
            parent = xp.where(upd, xp.where(known, best_p, -2), parent)
            ftick = xp.where(upd, t + 1, ftick)
            typ = xp.where(upd, t_new, typ)
            ever |= new
            # histogram of first-time divergences by (generation, type)
            gh = host(gnew[firsttime])
            th = host(t_new[firsttime])
            for g_, ty_ in zip(gh.tolist(), th.tolist()):
                gtyp[(g_, ty_)] = gtyp.get((g_, ty_), 0) + 1
        if scut is not None:
            nx, _ = law_step(xp, K, law, n, phys, tick, scut)
            if t + 1 >= cut_tick:          # CLAMP (neutralize) B to CONTROL from its first divergence onward
                cy, cx = divmod(cut_site, n)
                for f in range(5):
                    nx[f][cy, cx] = nc[f][cy, cx]
            cd = (nx[0] != nc[0]) | (nx[1] != nc[1]) | (nx[2] != nc[2]) | (nx[3] != nc[3]) | (nx[4] != nc[4])
            cut_ever |= cd
            scut = nx
        sc, si = nc, ni
        if (t + 1) % 50 == 0 or t == H - 1 or not bool(div_post.any()):
            nd = int(div_post.sum())
            series.append({"t": t + 1, "div_sites": nd,
                           "div_fields": int(sum(int(d.sum()) for d in dfield)),
                           "radius_now": int(cheb[div_post].max()) if nd else 0,
                           "ever_sites": int(ever.sum()), "ever_radius": int(cheb[ever].max()),
                           "max_gen": int(gen.max())})
        if not bool(div_post.any()):
            extinct = t + 1
            if scut is None:
                break
    gh = host(gen)
    tp = host(typ)
    res = {"schema": "aether.route01.unit.v1", "runner": RUNNER_VERSION, "table_hash": table_hash(), "backend": backend,
           "law": law, "semantics_id": LAWS[law], "seed_index": k, "n": n, "warm": warm, "H": H,
           "origin": o, "warm_digest": warm_digest, "final_digest_control": digest(sc), "final_digest_impulse": digest(si),
           "extinct_tick": extinct, "reentry_events": reentry, "series": series,
           "gen_type_counts": {"%d_%d" % kk: v for kk, v in sorted(gtyp.items())},
           "ever_sites": int(host(ever).sum()), "ever_radius": int(host(cheb)[host(ever)].max()),
           "max_gen": int(gh.max()), "unknown_sites": int((gh == -1).sum()),
           "wall_seconds": time.time() - t0}
    # tree (sparse) for the cut and for path analysis
    sel = np.flatnonzero(gh.ravel() != -9)
    res["tree"] = {"site": sel.tolist(), "gen": gh.ravel()[sel].tolist(), "parent": host(parent).ravel()[sel].tolist(),
                   "ftick": host(ftick).ravel()[sel].tolist(), "type": tp.ravel()[sel].tolist()}
    if scut is not None:
        res["cut"] = {"site": cut_site, "tick": cut_tick, "cut_ever_sites": host(cut_ever).ravel().nonzero()[0].tolist()}
    if backend == "gpu":
        import cupy
        res["gpu"] = {"mempool_total_bytes": int(cupy.get_default_memory_pool().total_bytes())}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--law", choices=sorted(LAWS), required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--warm", type=int, required=True)
    ap.add_argument("--H", type=int, required=True)
    ap.add_argument("--cut-from", default=None, help="uncut unit JSON of the same seed/law: choose B from its tree")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        return 0
    cs = ct = None
    if a.cut_from:
        import prop01_tree as T  # noqa: E402 (shared tree utilities)
        cs, ct = T.choose_cut(json.load(open(a.cut_from)))
        if cs is None:
            json.dump({"schema": "aether.route01.unit.v1", "law": a.law, "seed_index": a.seed_index,
                       "cut": None, "note": "no qualifying generation-1 site with children"}, open(a.out, "w"))
            return 0
    res = run_unit(a.backend, a.law, a.seed_index, a.n, a.warm, a.H, cs, ct)
    tmp = a.out + ".partial"
    json.dump(res, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done %s s%d ever %d gen %d ext %s %.1fs" % (a.law, a.seed_index, res["ever_sites"], res["max_gen"],
                                                      res["extinct_tick"], res["wall_seconds"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
