"""REACH01 R1 / TEST-4: does recoil + exchange carry distinguishable information beyond exchange transport?

Laws (exact previously qualified aeth03 MOB semantics; aeth01.v1 kernel underneath; B_balanced; P0; D50):
  V1  aeth01.v1
  X   aeth03.mob_r0x1e0   exchange only
  R   aeth03.mob_r1x0e0   recoil only
  RX  aeth03.mob_r1x1e0   recoil + exchange (TEST-3 MECHANISM_SUPPORTED law)
law_step reproduces aeth03_variants.step bit-for-bit (r1_conformance.py).

DECODABILITY UNIT (law, seed k):
  1. Build the D50 soup (rng 0xE2010000+k), run WARM ticks (physics 0xE2011000+k): the shared snapshot.
  2. Origins: 256 grid points (16 + 32 i, 16 + 32 j); each is moved to the nearest site (scan order, radius <= 3)
     that is WRITE with energy >= 1 in the snapshot, else kept. Separation 32 >> radius 6 + reach.
  3. Nine branches from the snapshot, identical except: BASE (no plant) and PLANT_j, j = 0..7, which sets the payload
     at EVERY origin to V[j]. V = 8 fixed, well-spread bytes. Each branch runs OBS ticks.
  4. Features at ticks TS: for each origin, radius r = 1..6 (Chebyshev ring) and template field f (opcode, arg0,
     arg1, payload): a 256-bin histogram of the ring's bytes. Also divergence vs BASE: the share of ring sites
     with any template field different from BASE.
  The decoder (r1_reduce.py) sees features and labels j ONLY for training origins; held-out evaluation is
  leave-one-seed-out. It never receives V[j] or any proxy: features are mean-centred per origin across the 8 branches
  (a label-free operation) and classified by nearest training centroid.
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, AETHER, os.path.join(AETHER, "test"), os.path.join(AETHER, "runpod", "aeth01_canary")):
    sys.path.insert(0, p)
from observatory import aeth01_run as R  # noqa: E402

RUNNER_VERSION = "r1_test4.v1"
LAWS = {"V1": "aeth01.v1", "X": "aeth03.mob_r0x1e0", "R": "aeth03.mob_r1x0e0", "RX": "aeth03.mob_r1x1e0"}
ENERGY = dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125 * (1 << 32))), replenish_amount=8)
DENSITY = 0.50
RNG_SEED_BASE = 0xE2010000
PHYS_SEED_BASE = 0xE2011000
V = [0x03, 0x2A, 0x51, 0x7C, 0x96, 0xB5, 0xD8, 0xF7]
RADII = (1, 2, 3, 4, 5, 6)
TS = (25, 50, 100, 200)


def table_hash():
    blob = json.dumps({"laws": LAWS, "energy": ENERGY, "dens": DENSITY, "rng": RNG_SEED_BASE, "phys": PHYS_SEED_BASE,
                       "V": V, "radii": RADII, "ts": TS}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def load_backend(name):
    if name == "gpu":
        import aeth01_gpu_kernel as K
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def host(x):
    return np.asarray(getattr(x, "get", lambda: x)())


def digest(fields):
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(host(f)).tobytes())
    return h.hexdigest()[:32]


def law_step(xp, K, law, n, seed, tick, s, observer=None):
    obs = [] if observer is None else observer
    out = K.gpu_step(n, n, seed, tick, ENERGY["write_cost"], ENERGY["maintenance_cost"],
                     ENERGY["replenish_numer"], ENERGY["replenish_amount"], 0, *s, observer=obs)
    nxt = list(out[:5])
    if law == "V1":
        return nxt, obs
    won_tmpl = xp.zeros((n, n), dtype=bool)
    disp = xp.zeros((n, n), dtype=xp.uint8)
    for f in range(4):
        slot = obs[f][0]
        for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
            m = xp.roll(slot == sl, (dr, dc), axis=(0, 1))
            won_tmpl |= m
            disp = xp.where(m, xp.roll(s[f], (dr, dc), axis=(0, 1)), disp)
    a0w = obs[1][0] != 255
    pw = obs[3][0] != 255
    if law in ("R", "RX"):    # recoil: arg0 := (pre-tick arg0 + displaced) & 0xFF on a template win, unless arg0 written
        nxt[1] = xp.where(won_tmpl & ~a0w, ((s[1].astype(xp.int16) + disp.astype(xp.int16)) & 0xFF).astype(xp.uint8),
                          nxt[1])
    if law in ("X", "RX"):    # exchange: payload := displaced byte on a template win, unless payload written
        nxt[3] = xp.where(won_tmpl & ~pw, disp, nxt[3])
    return nxt, obs


def choose_origins(s, K, n, spacing=32):
    op = host(s[0])
    en = host(s[4]).astype(np.int64)
    act = (op == K.WRITE_OPCODE) & (en >= ENERGY["write_cost"])
    out = []
    for gi in range(spacing // 2, n, spacing):
        for gj in range(spacing // 2, n, spacing):
            pick = (gi, gj)
            done = False
            for rad in range(0, 4):
                for di in range(-rad, rad + 1):
                    for dj in range(-rad, rad + 1):
                        if max(abs(di), abs(dj)) != rad:
                            continue
                        y, x = (gi + di) % n, (gj + dj) % n
                        if act[y, x]:
                            pick, done = (y, x), True
                            break
                    if done:
                        break
                if done:
                    break
            out.append(pick)
    return out


def ring_offsets(r):
    return [(dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if max(abs(dy), abs(dx)) == r]


def features(xp, s, base, ys, xs, n):
    """Returns (hist uint8 [O, 6, 4, 256], div float32 [O, 6]) for the current state s vs BASE state base."""
    O = len(ys)
    H = np.zeros((O, len(RADII), 4, 256), dtype=np.uint8)
    D = np.zeros((O, len(RADII)), dtype=np.float32)
    oy = xp.asarray(np.array(ys)).reshape(O, 1)
    ox = xp.asarray(np.array(xs)).reshape(O, 1)
    for ri, r in enumerate(RADII):
        offs = np.array(ring_offsets(r))
        yy = (oy + xp.asarray(offs[:, 0]).reshape(1, -1)) % n
        xx = (ox + xp.asarray(offs[:, 1]).reshape(1, -1)) % n
        diff = xp.zeros(yy.shape, dtype=bool)
        for f in range(4):
            vals = s[f][yy, xx].astype(xp.int32)                      # (O, ring)
            key = (xp.arange(O, dtype=xp.int32).reshape(O, 1) * 256 + vals).ravel()
            h = xp.bincount(key, minlength=O * 256).reshape(O, 256)
            H[:, ri, f, :] = host(h).astype(np.uint8)
            if base is not None:
                diff |= vals != base[f][yy, xx].astype(xp.int32)
        D[:, ri] = host(diff.mean(axis=1))
    return H, D


def run_unit(backend, law, k, n, warm, obs_ticks, out_npz, init=None, origins=None, plant_field=3):
    xp, K = load_backend(backend)
    if init is None:
        f0, _ = R.build_initial(R.SPARSE_SOUP, n, n, RNG_SEED_BASE + k, write_density=DENSITY,
                                energy_mode=R.ENERGY_UNIFORM)
    else:
        f0 = [x.copy() for x in init]
    s = [xp.asarray(f) for f in f0]
    phys = PHYS_SEED_BASE + k
    t0 = time.time()
    for t in range(warm):
        s, _ = law_step(xp, K, law, n, phys, t + 1, s)
    snap = [f.copy() for f in s]
    org = choose_origins(snap, K, n) if origins is None else origins
    ys = [o[0] for o in org]
    xs = [o[1] for o in org]
    ts = [t for t in TS if t <= obs_ticks]
    # BASE branch, keep its states at the feature ticks
    base_states = {}
    b = [f.copy() for f in snap]
    for t in range(obs_ticks):
        b, _ = law_step(xp, K, law, n, phys, warm + t + 1, b)
        if t + 1 in ts:
            base_states[t + 1] = [f.copy() for f in b]
    HS = np.zeros((8, len(org), len(ts), len(RADII), 4, 256), dtype=np.uint8)
    DS = np.zeros((8, len(org), len(ts), len(RADII)), dtype=np.float32)
    digests = []
    oy = xp.asarray(np.array(ys))
    ox = xp.asarray(np.array(xs))
    for j in range(8):
        w = [f.copy() for f in snap]
        w[plant_field][oy, ox] = np.uint8(V[j])
        for t in range(obs_ticks):
            w, _ = law_step(xp, K, law, n, phys, warm + t + 1, w)
            if t + 1 in ts:
                h, d = features(xp, w, base_states[t + 1], ys, xs, n)
                HS[j, :, ts.index(t + 1)] = h
                DS[j, :, ts.index(t + 1)] = d
        digests.append(digest(w))
    np.savez_compressed(out_npz, H=HS, D=DS)
    meta = {"schema": "aether.reach01.r1.unit.v1", "runner": RUNNER_VERSION, "table_hash": table_hash(),
            "backend": backend, "law": law, "semantics_id": LAWS[law], "seed_index": k, "n": n, "warm": warm,
            "obs": obs_ticks, "ts": ts, "origins": org, "V": V, "plant_field": plant_field,
            "snapshot_digest": digest(snap), "branch_final_digests": digests,
            "base_final_digest": digest(b), "features_npz": os.path.basename(out_npz),
            "wall_seconds": time.time() - t0}
    if backend == "gpu":
        import cupy
        meta["gpu"] = {"mempool_total_bytes": int(cupy.get_default_memory_pool().total_bytes())}
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--law", choices=sorted(LAWS), required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--warm", type=int, default=1000)
    ap.add_argument("--obs", type=int, default=200)
    ap.add_argument("--out", required=True, help="unit JSON path; features go to <out>.npz")
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        return 0
    meta = run_unit(a.backend, a.law, a.seed_index, a.n, a.warm, a.obs, a.out[:-5] + ".npz")
    tmp = a.out + ".partial"
    json.dump(meta, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done %s s%d %.1fs" % (a.law, a.seed_index, meta["wall_seconds"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
