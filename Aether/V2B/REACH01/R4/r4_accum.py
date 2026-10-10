"""REACH01 R4 / ACCUM01: can a certified mechanism become a building block for a NEW capability?

PHYSICS / ENERGY / TILE: as R3 (aeth01.op_xor, execution-only, 20x20 tile, 16x16 patch), plus a third input.
TASK 2 (the new capability): inputs A (6,1), B (13,1), C (9,1), each a one-shot WRITE into the patch's column 0;
output = payload of (9,18) after T_EVAL ticks; input values IN2 = (0x33, 0xCC) per input -> 8 passes.
Capability COMBINE3 = strict dependence of the output on all three inputs (every slice of the other two).
Task 1's capability (COMBINE on a, b) is what the reused component was certified for.

COMPONENT (from a certificate): the cell set Na U Nb (+ any cell listed in `extra`) of a certified COMBINE mechanism,
with its exact cell states. Library entries are (cells, states).
ARMS (equal evaluations; certificate-guided parent selection from R3 for every arm, so search infrastructure is held
fixed and only the component's availability differs):
  N  none                    no component; random initial patches
  S  shuffled component      insert-operator available, but the component's cell states are permuted among its cells
  U  unpromoted component    the correct mechanism patch seeds the archive as a restore point; cell mutation only
  P  promoted component      insert-operator: with prob P_INSERT a candidate is its parent with the component written
                             at a random offset (dy, dx) in [-OFF, OFF]^2 (duplicate / relocate); otherwise mutation
DESCRIPTOR for parent selection: R3's causal-interventional descriptor, generalized to 3 inputs (reach of a-, b-,
c-dependent state; joint cells depending on >= 2 inputs; output rung 0..3 = number of strictly-depended inputs).
"""

import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "R3"))
sys.path.insert(0, os.path.join(HERE, "..", "R2"))
import r3_frontier as F  # noqa: E402
import express01 as X  # noqa: E402

INC = (9, 1)
IN2 = (0x33, 0xCC)
PASSES = list(itertools.product(range(2), repeat=3))      # (ia, ib, ic)
P_INSERT = 0.3
OFF = 3
RUNNER_VERSION = "r4_accum.v1"


class Eval3(F.Evaluator):
    def run_batch(self, patches, extra=None):
        xp, n, side = self.xp, self.n, self.side
        m = patches.shape[0]
        base = np.zeros((5, n, n), np.uint8)
        base[0] = X.INERT
        for i in range(m):
            ty, tx = divmod(i, side)
            t = F.tile_world(patches[i])
            t[:, INC[0], INC[1]] = (1, X.E, 3, 0, 1)
            base[:, ty * F.TILE:(ty + 1) * F.TILE, tx * F.TILE:(tx + 1) * F.TILE] = t
        outs = np.zeros((m, 8), np.uint8)
        ph, pw = F.PATCH[1] - F.PATCH[0], F.PATCH[3] - F.PATCH[2]
        fin = np.zeros((m, 8, ph, pw), np.uint32)
        idx = np.arange(m)
        oy = (idx // side) * F.TILE + F.OUT[0]
        ox = (idx % side) * F.TILE + F.OUT[1]
        for c, (ia, ib, ic) in enumerate(PASSES):
            w = base.copy()
            for i in range(m):
                ty, tx = divmod(i, side)
                w[3, ty * F.TILE + F.INA[0], tx * F.TILE + F.INA[1]] = IN2[ia]
                w[3, ty * F.TILE + F.INB[0], tx * F.TILE + F.INB[1]] = IN2[ib]
                w[3, ty * F.TILE + INC[0], tx * F.TILE + INC[1]] = IN2[ic]
            s = [xp.asarray(w[f]) for f in range(5)]
            for t in range(F.T_EVAL):
                s, _ = X.step(xp, self.K, self.op, n, self.seed, t + 1, s, F.ENERGY)
            pay = np.asarray(getattr(s[3], "get", lambda: s[3])())
            outs[:, c] = pay[oy, ox]
            packed = (np.asarray(getattr(s[0], "get", lambda: s[0])()).astype(np.uint32) << 16) | \
                     (np.asarray(getattr(s[2], "get", lambda: s[2])()).astype(np.uint32) << 8) | pay.astype(np.uint32)
            for i in range(m):
                ty, tx = divmod(i, side)
                fin[i, c] = packed[ty * F.TILE + F.PATCH[0]:ty * F.TILE + F.PATCH[1],
                                   tx * F.TILE + F.PATCH[2]:tx * F.TILE + F.PATCH[3]]
        self.last_fin = fin
        return outs


def strict3(out8):
    t = out8.reshape(2, 2, 2)
    dep = []
    for ax in range(3):
        a0 = np.take(t, 0, axis=ax)
        a1 = np.take(t, 1, axis=ax)
        dep.append(bool((a0 != a1).all()))
    return dep


def descriptor3(out8, fin8):
    f = fin8.reshape(2, 2, 2, *fin8.shape[1:])
    deps = [(np.take(f, 0, axis=ax) != np.take(f, 1, axis=ax)).any(axis=0).any(axis=0) for ax in range(3)]

    def reach(m):
        cols = np.nonzero(m.any(axis=0))[0]
        return 0 if cols.size == 0 else int(cols.max()) + 1
    r = [reach(d) for d in deps]
    multi = (deps[0].astype(int) + deps[1].astype(int) + deps[2].astype(int)) >= 2
    rj, nj = reach(multi), int(multi.sum())
    rung = sum(strict3(out8))
    return tuple(x // 4 + (x > 0) for x in r) + (rj // 4 + (rj > 0), min(3, (nj + 3) // 4), rung)


def progress3(k):
    return 1 + k[0] + k[1] + k[2] + 2 * k[3] + 2 * k[4] + 4 * k[5]


def insert(rng, patch, comp):
    cells, states = comp
    q = patch.copy()
    dy, dx = rng.integers(-OFF, OFF + 1), rng.integers(-OFF, OFF + 1)
    for (y, x), st in zip(cells, states):
        yy, xx = y + dy, x + dx
        if 0 <= yy < q.shape[1] and 0 <= xx < q.shape[2]:
            q[:, yy, xx] = st
    return q


def search(arm, seed, batches, batch, comp, comp_patch, op="XOR", backend="gpu"):
    rng = np.random.default_rng(0x4ACC + 1000 * seed + "NSUP".index(arm))
    ev = Eval3(op, side=int(np.ceil(np.sqrt(batch))), backend=backend)
    if arm == "S":
        perm = rng.permutation(len(comp[0]))
        comp = (comp[0], [comp[1][i] for i in perm])
    elites = {}
    if arm == "U":
        elites[("seed",)] = (comp_patch.copy(), "component-seed")
    first, found, n = None, {}, 0
    log = []
    t0 = time.time()
    for bi in range(batches):
        cands = []
        for _ in range(batch):
            if elites and rng.random() < F.P_RESTORE:
                keys = list(elites)
                wts = np.array([progress3(k) ** 2 if k != ("seed",) else 1.0 for k in keys])
                par = elites[keys[rng.choice(len(keys), p=wts / wts.sum())]][0]
                if arm in ("S", "P") and rng.random() < P_INSERT:
                    cands.append(insert(rng, par, comp))
                else:
                    cands.append(F.mutate(rng, par))
            else:
                base = F.random_patches(rng, 1)[0]
                cands.append(insert(rng, base, comp) if arm in ("S", "P") and rng.random() < P_INSERT else base)
        P = np.stack(cands)
        outs = ev.run_batch(P)
        for i in range(batch):
            n += 1
            d = descriptor3(outs[i], ev.last_fin[i])
            if d not in elites:
                elites[d] = (P[i], F.phash(P[i]))
            if d[5] == 3:
                h = F.phash(P[i])
                if h not in found:
                    found[h] = (n, P[i], outs[i])
                    if first is None:
                        first = n
        log.append({"batch": bi, "evals": n, "bins": len(elites), "found": len(found),
                    "max_progress": max(progress3(k) for k in elites if k != ("seed",)) if len(elites) > (arm == "U") else 0,
                    "seconds": round(time.time() - t0, 1)})
    keys = [k for k in elites if k != ("seed",)]
    return {"arm": arm, "seed": seed, "evals": n, "first_combine3_eval": first, "combine3_distinct": len(found),
            "bins": len(keys), "max_rung": max(k[5] for k in keys) if keys else 0,
            "max_progress": max(progress3(k) for k in keys) if keys else 0, "log": log,
            "wall_seconds": time.time() - t0}, found


def load_component(path):
    c = json.load(open(path))
    return ([tuple(x) for x in c["cells"]], [tuple(s) for s in c["states"]]), np.array(c["patch"], np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=list("NSUP"), required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--component", required=True)
    ap.add_argument("--batches", type=int, default=20)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        return 0
    comp, cpatch = load_component(a.component)
    res, found = search(a.arm, a.seed, a.batches, a.batch, comp, cpatch)
    res.update(schema="aether.reach01.r4.search.v1", runner=RUNNER_VERSION, component=os.path.basename(a.component))
    if found:
        hs = sorted(found, key=lambda h: found[h][0])
        np.savez_compressed(a.out[:-5] + "_found.npz", patches=np.stack([found[h][1] for h in hs]),
                            outs=np.stack([found[h][2] for h in hs]), evals=np.array([found[h][0] for h in hs]))
        res["found_npz"] = os.path.basename(a.out[:-5] + "_found.npz")
    json.dump(res, open(a.out + ".partial", "w"), separators=(",", ":"))
    os.replace(a.out + ".partial", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
