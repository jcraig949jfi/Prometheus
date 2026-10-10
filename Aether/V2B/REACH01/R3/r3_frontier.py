"""REACH01 R3 / FRONTIER01: can search assemble a composition, and does certificate-guided frontier restoration help?

PHYSICS: aeth01.op_xor (R2 PLANTED_COMPOSITION_SUPPORTED); alien arm aeth01.op_rotx. Execution-only energy regime
(w 1, m 0, no rain), as in the R2 gadgets. P0.

TASK TILE (20 x 20, one candidate per tile, the same tile for all 16 input passes, because arbitration is keyed to
coordinates):
  moat:    rows 0-1 and 18-19, cols 0 and 19 -- inert (opcode 9), energy 0
  inputs:  A at (6, 1) and B at (13, 1): one-shot WRITE sites (energy 1) aimed EAST into payload, carrying a, b
  output:  O = payload of (9, 18) after T_EVAL ticks; O is inert, energy 0 (it only receives)
  patch:   rows 2-17 x cols 2-17 = 16 x 16 cells, the search material. Per cell: opcode WRITE with prob 0.35 else
           random non-WRITE (WRITE prob 0.5); arg0, arg1, payload uniform bytes; energy uniform 0..31 (each unit = one firing; >= 24 lets a cell fire through the whole evaluation, so the planted relay solution lies inside the search space)
  The input values range over IN = {0x0F, 0x33, 0x55, 0xAA}: 16 passes per evaluation.
CAPABILITY RUNGS (from the 4 x 4 output table; certification is in r3_certify.py):
  TRANSMIT  the output depends on at least one input (some slice)
  COMBINE   strict dependence on BOTH inputs (every slice)
  COMPOSE   COMBINE + ablation certificate: the cells whose individual inertion destroys a-dependence (Na) and
            b-dependence (Nb) contain cells exclusive to each path (Na\\Nb and Nb\\Na both non-empty): two
            causally necessary substructures that meet in a combination neither performs alone
SEARCH ARMS (equal evaluations per seed; batches of BATCH candidates):
  A ordinary   every candidate is a fresh random patch
  B random-checkpoint  with prob P_RESTORE a candidate is a K-cell mutation of a uniformly random archived
               candidate (reservoir of past evaluations, size-matched to C's archive), else fresh
  C certificate-guided  same P_RESTORE; the parent comes from a MAP-Elites archive keyed by the CAUSAL
               INTERVENTIONAL descriptor frontier_descriptor() = (reach of a-dependent state, reach of b-dependent state,
               reach of jointly a&b-dependent cells, joint-cell count, output rung), all measured by controlled input
               variation across the 16 passes. A bin is chosen with weight progress^2, progress = 1 + ra + rb + 2 rj +
               2 nj + 4 rung. No entropy, turnover, novelty or spatial-complexity descriptor.
  All arms record the same descriptor for measurement; only C selects on it.
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "R2"))
import express01 as X  # noqa: E402

TILE = 20
PATCH = (2, 18, 2, 18)          # rows [2, 18), cols [2, 18)
INA, INB, OUT = (6, 1), (13, 1), (9, 18)
IN = (0x0F, 0x33, 0x55, 0xAA)
T_EVAL = 24
P_WRITE = 0.5
K_MUT = 3
P_RESTORE = 0.9
ENERGY = X.EXEC_ONLY
RUNNER_VERSION = "r3_frontier.v2"  # v2 (R3 attempt 2): per-column frontier descriptor (repair of v1 bucket defect)


def random_patches(rng, m):
    h, w = PATCH[1] - PATCH[0], PATCH[3] - PATCH[2]
    p = np.zeros((m, 5, h, w), np.uint8)
    nonw = rng.integers(2, 256, size=(m, h, w)).astype(np.uint8)
    p[:, 0] = np.where(rng.random((m, h, w)) < P_WRITE, 1, nonw)
    p[:, 1] = rng.integers(0, 256, size=(m, h, w))
    p[:, 2] = rng.integers(0, 256, size=(m, h, w))
    p[:, 3] = rng.integers(0, 256, size=(m, h, w))
    p[:, 4] = rng.integers(0, 32, size=(m, h, w))
    return p


def mutate(rng, patch, k=K_MUT):
    q = patch.copy()
    h, w = q.shape[1:]
    fresh = random_patches(rng, 1)[0]
    for _ in range(k):
        y, x = rng.integers(0, h), rng.integers(0, w)
        q[:, y, x] = fresh[:, y, x]
    return q


def tile_world(patch):
    t = np.zeros((5, TILE, TILE), np.uint8)
    t[0] = X.INERT
    t[:, PATCH[0]:PATCH[1], PATCH[2]:PATCH[3]] = patch
    for (y, x) in (INA, INB):
        t[:, y, x] = (1, X.E, 3, 0, 1)
    t[:, OUT[0], OUT[1]] = (X.INERT, 0, 0, 0, 0)
    return t


class Evaluator:
    def __init__(self, op="XOR", side=32, backend="gpu", seed=0xF00D):
        self.op, self.side, self.seed = op, side, seed
        self.xp, self.K = X.load(backend)
        self.n = side * TILE

    def run_batch(self, patches, extra=None):
        """patches (m <= side^2, 5, 16, 16) -> outputs (m, 16) uint8 for the 16 (a, b) passes."""
        xp, n, side = self.xp, self.n, self.side
        m = patches.shape[0]
        base = np.zeros((5, n, n), np.uint8)
        base[0] = X.INERT
        for i in range(m):
            ty, tx = divmod(i, side)
            base[:, ty * TILE:(ty + 1) * TILE, tx * TILE:(tx + 1) * TILE] = tile_world(patches[i])
        if extra is not None:
            extra(base)
        outs = np.zeros((m, 16), np.uint8)
        ph, pw = PATCH[1] - PATCH[0], PATCH[3] - PATCH[2]
        fin = np.zeros((m, 16, ph, pw), np.uint32)           # packed (opcode, arg1, payload) of every patch cell
        idx = np.arange(m)
        oy = (idx // side) * TILE + OUT[0]
        ox = (idx % side) * TILE + OUT[1]
        for c in range(16):
            a, b = IN[c // 4], IN[c % 4]
            w = base.copy()
            for i in range(m):
                ty, tx = divmod(i, side)
                w[3, ty * TILE + INA[0], tx * TILE + INA[1]] = a
                w[3, ty * TILE + INB[0], tx * TILE + INB[1]] = b
            s = [xp.asarray(w[f]) for f in range(5)]
            for t in range(T_EVAL):
                s, _ = X.step(xp, self.K, self.op, n, self.seed, t + 1, s, ENERGY)
            pay = np.asarray(getattr(s[3], "get", lambda: s[3])())
            outs[:, c] = pay[oy, ox]
            packed = (np.asarray(getattr(s[0], "get", lambda: s[0])()).astype(np.uint32) << 16) |                      (np.asarray(getattr(s[2], "get", lambda: s[2])()).astype(np.uint32) << 8) | pay.astype(np.uint32)
            for i in range(m):
                ty, tx = divmod(i, side)
                fin[i, c] = packed[ty * TILE + PATCH[0]:ty * TILE + PATCH[1], tx * TILE + PATCH[2]:tx * TILE + PATCH[3]]
        self.last_fin = fin
        return outs


def depmap(fin16):
    """fin16 (16, ph, pw): per-cell final packed non-AIM state per input pass. Returns bool maps (dep_a, dep_b):
    cell depends on a (some b slice where varying a changes it), resp. on b."""
    f = fin16.reshape(4, 4, *fin16.shape[1:])            # [a idx, b idx, y, x]
    dep_a = (f != f[0:1, :, :, :]).any(axis=0).any(axis=0)
    dep_b = (f != f[:, 0:1, :, :]).any(axis=1).any(axis=0)
    return dep_a, dep_b


def frontier_descriptor(out16, fin16):
    """CAUSAL descriptor for arm C: (reach_a, reach_b, joint-cell reach, joint-cell count bucket, output rung).
    reach = 1 + rightmost patch column holding input-dependent state (0 = none), per column (v2). Joint cells depend
    on BOTH inputs (partial combination sites)."""
    da, db = depmap(fin16)
    joint = da & db
    def reach(m):
        cols = np.nonzero(m.any(axis=0))[0]
        return 0 if cols.size == 0 else int(cols.max()) + 1
    ra, rb, rj = reach(da), reach(db), reach(joint)
    nj = int(joint.sum())
    _d, rung = descriptor(out16)
    # v2: PER-COLUMN reach (0..16). v1 bucketed reach into 4-column bins, so every elite had progress <= 4 and arm C's
    # parent weights were uniform: C reduced to B by construction (R3 attempt-1 instrument defect).
    return (ra, rb, rj, min(3, (nj + 3) // 4), rung)


def progress(k):
    ra, rb, rj, nj, rung = k
    return 1 + ra + rb + 2 * rj + 2 * nj + 4 * rung


def descriptor(out16):
    t = out16.reshape(4, 4)                    # [a index, b index]
    a_slices = [len(set(t[:, j])) > 1 for j in range(4)]   # varying a with b fixed
    b_slices = [len(set(t[i, :])) > 1 for i in range(4)]
    any_a, any_b = any(a_slices), any(b_slices)
    strict_a, strict_b = all(a_slices), all(b_slices)
    joint = sum(a_slices) + sum(b_slices)
    rung = 2 if (strict_a and strict_b) else (1 if (any_a or any_b) else 0)
    return (int(any_a), int(any_b), int(strict_a), int(strict_b), int(joint)), rung


def phash(p):
    return hashlib.sha256(p.tobytes()).hexdigest()[:16]


def search(arm, op, seed, batches, batch, backend="gpu"):
    rng = np.random.default_rng(0xA5C0 + 1000 * seed + {"A": 1, "B": 2, "C": 3}[arm])
    ev = Evaluator(op, side=int(np.ceil(np.sqrt(batch))), backend=backend)
    elites = {}            # descriptor -> (patch, hash)
    reservoir = []         # (patch, hash) for arm B
    seen_combine = {}      # hash -> (eval index, patch, descriptor)
    n_eval = 0
    first_combine = None
    log = []
    t0 = time.time()
    lineage_parent = {}
    for bi in range(batches):
        cands, parents = [], []
        for _ in range(batch):
            restore = arm != "A" and rng.random() < P_RESTORE and (elites if arm == "C" else reservoir)
            if restore and arm == "C":
                keys = list(elites)
                wts = np.array([progress(k) ** 2 for k in keys], dtype=np.float64)
                k = keys[rng.choice(len(keys), p=wts / wts.sum())]
                par = elites[k]
                cands.append(mutate(rng, par[0]))
                parents.append(par[1])
            elif restore and arm == "B":
                par = reservoir[rng.integers(0, len(reservoir))]
                cands.append(mutate(rng, par[0]))
                parents.append(par[1])
            else:
                cands.append(random_patches(rng, 1)[0])
                parents.append(None)
        P = np.stack(cands)
        outs = ev.run_batch(P)
        for i in range(batch):
            _d0, rung = descriptor(outs[i])
            d = frontier_descriptor(outs[i], ev.last_fin[i])
            h = phash(P[i])
            lineage_parent[h] = parents[i]
            n_eval += 1
            if d not in elites:
                elites[d] = (P[i], h)
            if arm == "B":
                if len(reservoir) < max(1, len(elites)):
                    reservoir.append((P[i], h))
                else:
                    j = rng.integers(0, n_eval)
                    if j < len(reservoir):
                        reservoir[j] = (P[i], h)
            if rung == 2 and h not in seen_combine:
                seen_combine[h] = (n_eval, P[i], d, outs[i])
                if first_combine is None:
                    first_combine = n_eval
        log.append({"batch": bi, "evals": n_eval, "bins": len(elites), "combine_distinct": len(seen_combine),
                    "max_progress": max(progress(k) for k in elites),
                    "seconds": round(time.time() - t0, 1)})
    best = max(elites, key=progress)
    return {"arm": arm, "op": op, "seed": seed, "evals": n_eval, "bins_reached": len(elites),
            "max_progress": progress(best), "best_bin": list(best),
            "max_reach_a": max(k[0] for k in elites), "max_reach_b": max(k[1] for k in elites),
            "max_joint_reach": max(k[2] for k in elites), "max_rung": max(k[4] for k in elites),
            "bins": [list(k) for k in elites], "first_combine_eval": first_combine,
            "combine_distinct": len(seen_combine), "log": log, "wall_seconds": time.time() - t0,
            "lineage_parent": lineage_parent}, seen_combine


GEOMS = {"R3": ((6, 1), (13, 1), (9, 18)),            # the frozen R3 task (default)
         "G1": ((8, 1), (10, 1), (9, 6)),             # LADDER01: inputs 2 rows apart, output 5 columns in
         "G2": ((8, 1), (10, 1), (9, 10)),            # output 9 columns in
         "G3": ((8, 1), (10, 1), (9, 18))}            # output at the tile edge (R3 distance)


def set_geom(name):
    global INA, INB, OUT
    INA, INB, OUT = GEOMS[name]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", choices=sorted(GEOMS), default="R3")
    ap.add_argument("--arm", choices=["A", "B", "C"], required=True)
    ap.add_argument("--op", default="XOR")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--batches", type=int, default=20)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--backend", default="gpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        return 0
    set_geom(a.geom)
    res, combos = search(a.arm, a.op, a.seed, a.batches, a.batch, a.backend)
    res["geom"] = a.geom
    res["schema"] = "aether.reach01.r3.search.v1"
    res["runner"] = RUNNER_VERSION
    npz = a.out[:-5] + "_combine.npz"
    if combos:
        hs = sorted(combos, key=lambda h: combos[h][0])
        np.savez_compressed(npz, patches=np.stack([combos[h][1] for h in hs]), outs=np.stack([combos[h][3] for h in hs]),
                            evals=np.array([combos[h][0] for h in hs]), hashes=np.array(hs))
        res["combine_npz"] = os.path.basename(npz)
    lp = res.pop("lineage_parent")
    res["lineage_parents_of_combine"] = {h: lp.get(h) for h in combos}
    tmp = a.out + ".partial"
    json.dump(res, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done", a.arm, a.op, a.seed, res["combine_distinct"], res["first_combine_eval"], round(res["wall_seconds"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
