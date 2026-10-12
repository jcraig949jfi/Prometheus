"""C-018-T020 demand gate: planted spatial fixtures, built on Aether's own (read-only) kernel and rulers.

Nothing here edits Aether. The kernel step is Aether's `r1_test4.law_step` over `Aether/test/reference/gpu_aeth01.py`
(CPU). Fixtures are hand-built (instrument qualification, not discovery). Decision rules: PREREG.md (committed first).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AETHER = os.path.join(REPO, "Aether")
R1 = os.path.join(AETHER, "V2B", "REACH01", "R1")
for p in (R1, AETHER, os.path.join(AETHER, "test"), os.path.join(AETHER, "V2B", "REACH01", "R2"),
          os.path.join(AETHER, "V2B", "PROP01")):
    if p not in sys.path:
        sys.path.insert(0, p)
import r1_test4 as T  # noqa: E402  (Aether, unmodified)
import r1_reduce as RD  # noqa: E402

PHYS = 0xC18B0000      # disjoint from Aether 0xE2011000
NOISE = 0xC18C0000
SURR = 0xC18D0000
RNG = 0xC18A0000
INERT, WRITE = 9, 1
NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
V = T.V                                    # Aether's 8 planted payload bytes
LB = [0, 35, 70, 105, 140, 175, 210, 245]  # arg1 labels, all = 0 mod 5 (field selector stays 0)
KINDS = ("A", "B", "E", "G", "N")
_xp, _K = T.load_backend("cpu")


def blank(n):
    return [np.full((n, n), INERT, np.uint8), np.zeros((n, n), np.uint8), np.zeros((n, n), np.uint8),
            np.zeros((n, n), np.uint8), np.zeros((n, n), np.uint8)]


def plant(s, kind, y, x, n, j, seedk=0, branch=0):
    """Write fixture `kind` at origin (y, x) into state s. j = label index, or None for the BASE branch."""
    def link(c, opcode, d, field, payload, energy=255):
        for f, v in enumerate((opcode, d, field, payload, energy)):
            s[f][y, (x + c) % n] = v
    if kind in ("A", "G"):
        for c in range(6 if kind == "A" else 3):
            link(c, WRITE, EAST, 3, 0)
        s[3][y, x] = 0x10 if j is None else V[j]
    elif kind == "B":
        link(0, WRITE if j is not None else INERT, EAST, 0, 1)
        s[2][y, x] = 0 if j is None else LB[j]
        for c in range(1, 6):
            link(c, INERT, EAST, 0, 1)
    elif kind == "E":
        for c in range(7):
            s[3][y, (x + c) % n] = 0 if j is None else V[j]
    elif kind == "N":
        rng = np.random.default_rng([NOISE + seedk, y, x, 0 if j is None else 1 + branch])
        for c in range(7):
            s[3][y, (x + c) % n] = 0 if j is None else int(rng.integers(0, 256))
    else:
        raise ValueError(kind)


def step(s, tick, seed, law="V1"):
    n = s[0].shape[0]
    nxt, _ = T.law_step(np, _K, "V1" if law in ("V1", "TELEPORT") else law, n, seed, tick, s)
    if law == "TELEPORT":                 # counterfeit non-local law: payloads leak (7, 7) away each tick
        nxt[3] = nxt[3] ^ np.roll(nxt[3], (7, 7), axis=(0, 1))
    return nxt


def diff_mask(a, b):
    m = np.zeros(a[0].shape, bool)
    for f in range(5):
        m |= a[f] != b[f]
    return m


def cheb_to_set(n, sites):
    yy = np.arange(n).reshape(n, 1)
    xx = np.arange(n).reshape(1, n)
    best = np.full((n, n), 10 ** 6)
    for (y, x) in sites:
        dy = np.minimum((yy - y) % n, (y - yy) % n)
        dx = np.minimum((xx - x) % n, (x - xx) % n)
        best = np.minimum(best, np.maximum(dy, dx))
    return best


def ancestry_run(kind, seedk, label=3, n=48, horizon=100, law="V1"):
    """Paired worlds BASE / PLANT / CUT / NONANC for one origin. Returns the recorded observables."""
    y0, x0 = 24, 10
    phys = PHYS + seedk
    base0, pl0 = blank(n), blank(n)
    plant(base0, kind, y0, x0, n, None, seedk)
    plant(pl0, kind, y0, x0, n, label, seedk, branch=label)
    # all four worlds share the rain/energy stream (same phys seed); only the plant (and the clamps) differ
    cut_site = (y0, x0 + 2)
    non_site = (y0 - 2, x0)
    worlds = {"base": base0, "plant": pl0, "cut": [f.copy() for f in pl0], "nonanc": [f.copy() for f in pl0]}
    t0_mask = diff_mask(base0, pl0)
    t0_sites = [tuple(int(v) for v in p) for p in np.argwhere(t0_mask)]
    down = [(y0, x0 + k) for k in range(3, 7)]
    ever = {w: {d: None for d in down} for w in ("plant", "cut", "nonanc")}
    for d in down:
        if t0_mask[d]:
            ever["plant"][d] = 0
    cone_ok, max_ratio = True, 0.0
    dist = cheb_to_set(n, t0_sites) if t0_sites else None
    for t in range(1, horizon + 1):
        nb = step(worlds["base"], t, phys, law)
        for w in ("plant", "cut", "nonanc"):
            nw = step(worlds[w], t, phys, law)
            site = cut_site if w == "cut" else non_site if w == "nonanc" else None
            if site is not None:
                for f in range(5):
                    nw[f][site] = nb[f][site]        # clamp to BASE (PROP01 semantics: every tick from tick 1)
            worlds[w] = nw
            dm = diff_mask(nw, nb)
            for d in down:
                if dm[d] and ever[w][d] is None:
                    ever[w][d] = t
            if w == "plant" and dist is not None and dm.any():
                r = int(dist[dm].max())
                max_ratio = max(max_ratio, r / t)
                if r > t:
                    cone_ok = False
        worlds["base"] = nb
    div = [d for d in down if ever["plant"][d] is not None]
    out = {"kind": kind, "seed": seedk, "law": law, "t0_sites": len(t0_sites), "downstream": len(down),
           "div": len(div),
           "first_tick": {"%d,%d" % d: ever["plant"][d] for d in down},
           "cut_div": sum(1 for d in div if ever["cut"][d] is not None),
           "nonanc_div": sum(1 for d in div if ever["nonanc"][d] is not None),
           "light_cone_ok": cone_ok, "max_radius_over_tick": round(max_ratio, 3)}
    out["removed_cut"] = None if not div else round(1 - out["cut_div"] / len(div), 3)
    out["removed_nonanc"] = None if not div else round(1 - out["nonanc_div"] / len(div), 3)
    return out


def decode_unit(kind, seedk, n=96, obs=100, ts=(25, 50, 100)):
    """Decodability unit: 36 origins, BASE + 8 labelled PLANT branches, Aether's feature extractor unchanged."""
    phys = PHYS + seedk
    org = [(8 + 16 * i, 2 + 16 * jx) for i in range(6) for jx in range(6)]
    ys, xs = [o[0] for o in org], [o[1] for o in org]

    def world(j):
        s = blank(n)
        for (y, x) in org:
            plant(s, kind, y, x, n, j, seedk, branch=0 if j is None else j)
        return s
    b = world(None)
    base_states = {}
    for t in range(1, obs + 1):
        b = step(b, t, phys)
        if t in ts:
            base_states[t] = [f.copy() for f in b]
    HS = np.zeros((8, len(org), len(ts), 6, 4, 256), np.uint8)
    DS = np.zeros((8, len(org), len(ts), 6), np.float32)
    for j in range(8):
        w = world(j)
        for t in range(1, obs + 1):
            w = step(w, t, phys)
            if t in ts:
                h, d = T.features(np, w, base_states[t], ys, xs, n)
                HS[j, :, ts.index(t)] = h
                DS[j, :, ts.index(t)] = d
    return (seedk, {}, HS, DS)


def decode_kind(kind, seeds=(0, 1, 2, 3)):
    units = [decode_unit(kind, k) for k in seeds]
    st = RD.stats(RD.decode(units))
    acc = {s: np.array(v["acc"]) for s, v in st.items()}
    by_r = np.mean([a.mean(axis=0) for a in acc.values()], axis=0)          # mean over seeds and ticks, per radius
    return {"kind": kind, "seeds": list(seeds),
            "Dstat": {str(s): round(v["Dstat"], 4) for s, v in st.items()},
            "D1": {str(s): round(v["D1"], 4) for s, v in st.items()},
            "acc_by_radius": [round(float(x), 3) for x in by_r],
            "min_seed_acc_by_radius": [round(float(min(a.mean(axis=0)[r] for a in acc.values())), 3) for r in range(6)],
            "divergence_share_by_radius": [round(float(np.mean([u[3].mean(axis=(0, 1, 2))[r] for u in units])), 3)
                                           for r in range(6)]}
