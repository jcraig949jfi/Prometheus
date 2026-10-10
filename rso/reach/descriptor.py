"""Does the behaviour descriptor see stepping stones? A pre-freeze qualification of C-BEH (C-013-T010, Argus).

    python -m rso.reach.descriptor [--pool 60000] [--out rso/reach/DESCRIPTOR_QUALIFICATION.json]

Ruling s3 bullet 6 and Nyx's attack A4 / M2: a behaviour descriptor is a ruler only if it can fail, and it must
separate MEANINGFUL intermediates from arbitrary genomes of equal score without merely hashing genotypes.

Objects
  path intermediates   the 254 genomes I(S) = builder_min with the positions in S replaced by NOP, 1 <= |S| <= 7.
                       Under the arms' operator (one whole instruction row replaced) the shortest edit path from ANY
                       knock-out start to the target passes only through such genomes (each step restores one row),
                       so these are exactly the shortest-edit-path intermediates of every knock-out start.
  equal-score others   genomes NOT on any path (no row-subset of the target with NOPs) with EXACTLY the same training
                       score: drawn from uniform random programs under the operator's row distribution and from off-path
                       one- and two-row mutants of the target and of the intermediates.
  synonyms             behaviour-preserving edits of an intermediate: the unused fields of a row re-drawn, or a NOP row
                       replaced by an instruction that writes only a register builder_min never reads (r2, r4, r5, r7).

Rulers (thresholds fixed in this file before the first measurement)
  R1 separation   share of (intermediate, equal-score other) pairs given DIFFERENT cells      PASS >= 0.90
  R1c             R1 restricted to pairs whose TRACEs differ (behaviourally distinguishable pairs)   PASS >= 0.90
  R2 invariance   share of (intermediate, synonym) pairs given the SAME cell                   PASS >= 0.90
  Planted must-fail controls: C-FIT (score bins) must FAIL R1 -- equal score is the same cell by construction;
  GENO (genotype hash) must FAIL R2 -- synonyms are different genomes. If either control passes, the test is broken.
  TRACE (the full action sequence on the training block, the finest training-behaviour descriptor that exists)
  is reported beside C-BEH: an intermediate TRACE cannot separate from an equal-score other is behaviourally
  INVISIBLE on the training block, and no training-behaviour descriptor can keep it.
"""
import argparse
import json
from itertools import combinations

import numpy as np
from numba import njit

from rso.reach import arms
from rso.reach._proto import wm

R1_PASS = 0.90
R2_PASS = 0.90
INERT_REGS = (2, 4, 5, 7)            # builder_min reads r0, r1, r3, r6 only
USED_FIELDS = {wm.PH: 2, wm.SKZ: 2, wm.JMP: (0, 3), wm.IN: 2, wm.STR: 3, wm.OUT: 2, wm.STW: 3}


@njit(cache=True)
def _trace_hash(prog, n, store0, seed, life0, nlives, K, R, E, T, F, cap):
    h = np.uint64(1469598103934665603)
    reg = np.zeros(wm.NREG, dtype=np.int64)
    fmem = np.zeros(F, dtype=np.int64)
    out = np.zeros((T, 4), dtype=np.int64)
    for j in range(nlives):
        store = store0.copy()
        seen_prev = np.zeros(K, dtype=np.int64)
        probed = np.zeros(K, dtype=np.int64)
        repeated = np.zeros(K, dtype=np.int64)
        for ep in range(E):
            reg[:] = 0
            fmem[:] = 0
            wm.run_episode(prog, n, reg, fmem, store, seen_prev, probed, repeated, seed, life0 + j, ep, K, R, T,
                           cap, True, False, out)
            for t in range(T):
                h = wm.khash(h, j * 64 + ep, t, out[t, 2])
    return h


def trace_hash(prog):
    P = arms.P
    prog = np.ascontiguousarray(prog, dtype=np.int64)
    return int(_trace_hash(prog, prog.shape[0], arms.STORE0, P.seed, arms.TRAIN0, arms.N_TRAIN, P.K, P.R, P.E, P.T,
                           P.F, P.cap))


DESCRIPTORS = {
    "C-BEH": lambda p, f, k: k,
    "C-FIT": lambda p, f, k: f,
    "GENO": lambda p, f, k: arms.genome_hash(p),
    "TRACE": lambda p, f, k: trace_hash(p),
}


def intermediates():
    out = []
    for size in range(1, 8):
        for S in combinations(range(8), size):
            g = arms.TARGET.copy()
            g[list(S)] = 0
            out.append((S, g))
    return out


def is_path_genome(g):
    """True iff every row of g equals the target's row or is a NOP row (0,0,0,0)."""
    return all((g[i] == arms.TARGET[i]).all() or not g[i].any() for i in range(8))


def _random_row(rng):
    return np.array([rng.integers(wm.NOPS), rng.integers(8), rng.integers(64), rng.integers(16)], dtype=np.int64)


def synonyms(S, g, rng, k=6):
    """Behaviour-preserving variants of intermediate g (S = its NOP positions)."""
    out = []
    for _ in range(k * 4):
        v = g.copy()
        i = int(rng.integers(8))
        if i in S:      # NOP row -> NOP with junk fields, or a write to a never-read register
            if rng.random() < 0.5:
                v[i] = [0, rng.integers(8), rng.integers(64), rng.integers(16)]
            else:
                v[i] = [wm.SET, INERT_REGS[int(rng.integers(4))], rng.integers(64), rng.integers(16)]
        else:           # re-draw the fields the instruction does not read (op mod 19 and used fields kept)
            op = int(g[i, 0])
            if op == wm.JMP:
                v[i, 1], v[i, 2] = rng.integers(8), rng.integers(64)
            elif op in (wm.STR, wm.STW):
                v[i, 3] = rng.integers(16)
            else:
                v[i, 2], v[i, 3] = rng.integers(64), rng.integers(16)
        if not (v == g).all():
            out.append(v)
        if len(out) >= k:
            break
    return out


def pool(rng, n_random, inters):
    progs = [np.stack([_random_row(rng) for _ in range(8)]) for _ in range(n_random)]
    bases = [arms.TARGET] + [g for _, g in inters]
    for _ in range(n_random // 2):
        g = bases[int(rng.integers(len(bases)))].copy()
        for _ in range(int(rng.integers(1, 3))):
            g[int(rng.integers(8))] = _random_row(rng)
        progs.append(g)
    return [p for p in progs if not is_path_genome(p)]


def run(n_random=40000, per=20, seed=7):
    rng = np.random.default_rng(seed)
    inters = intermediates()
    rows = []
    for S, g in inters:
        f, _, k = arms.train_eval(g)
        rows.append(dict(S=S, g=g, f=f, k=k))
    others = []
    for p in pool(rng, n_random, inters):
        f, _, k = arms.train_eval(p)
        others.append(dict(g=p, f=f, k=k))
    by_f = {}
    for o in others:
        by_f.setdefault(o["f"], []).append(o)
    res = {name: dict(sep_pairs=0, sep_diff=0, inv_pairs=0, inv_same=0, c_pairs=0, c_diff=0) for name in DESCRIPTORS}
    tcache = {}

    def tr(g):
        b = g.tobytes()
        if b not in tcache:
            tcache[b] = trace_hash(g)
        return tcache[b]
    per_class = {}
    for r in rows:
        cands = by_f.get(r["f"], [])
        pick = [cands[int(i)] for i in rng.choice(len(cands), size=min(per, len(cands)), replace=False)] if cands else []
        syn = synonyms(r["S"], r["g"], rng)
        missing = tuple(int(x) for x in r["S"])
        cls = per_class.setdefault(len(missing), {name: [0, 0] for name in DESCRIPTORS})
        for name, fn in DESCRIPTORS.items():
            mine = fn(r["g"], r["f"], r["k"])
            for o in pick:
                diff = fn(o["g"], o["f"], o["k"]) != mine
                res[name]["sep_pairs"] += 1
                res[name]["sep_diff"] += int(diff)
                if tr(o["g"]) != tr(r["g"]):
                    res[name]["c_pairs"] += 1
                    res[name]["c_diff"] += int(diff)
                cls[name][0] += 1
                cls[name][1] += int(diff)
            for v in syn:
                fv, _, kv = arms.train_eval(v)
                assert fv == r["f"], "a synonym changed the training score: the synonym generator is wrong"
                res[name]["inv_pairs"] += 1
                res[name]["inv_same"] += int(fn(v, fv, kv) == mine)
        r["n_equal_score_others"] = len(cands)
    summary = {}
    for name, x in res.items():
        sep = x["sep_diff"] / x["sep_pairs"] if x["sep_pairs"] else None
        inv = x["inv_same"] / x["inv_pairs"] if x["inv_pairs"] else None
        sepc = x["c_diff"] / x["c_pairs"] if x["c_pairs"] else None
        summary[name] = dict(R1_separation=sep, R1=("PASS" if sep is not None and sep >= R1_PASS else "FAIL"),
                             R1c_separation_given_trace_differs=sepc,
                             R1c=("PASS" if sepc is not None and sepc >= R1_PASS else "FAIL"), pairs_R1c=x["c_pairs"],
                             R2_invariance=inv, R2=("PASS" if inv is not None and inv >= R2_PASS else "FAIL"),
                             pairs_R1=x["sep_pairs"], pairs_R2=x["inv_pairs"])
    by_k = {k: {name: (v[1] / v[0] if v[0] else None) for name, v in d.items()} for k, d in sorted(per_class.items())}
    scores = sorted({r["f"] for r in rows})
    no_match = sum(1 for r in rows if r["n_equal_score_others"] == 0)
    return dict(summary=summary, R1_separation_by_rows_missing=by_k, intermediate_scores=scores,
                intermediates=len(rows), intermediates_with_no_equal_score_other=no_match,
                pool_size=len(others), thresholds=dict(R1_PASS=R1_PASS, R2_PASS=R2_PASS),
                controls_ok=(summary["C-FIT"]["R1"] == "FAIL" and summary["GENO"]["R2"] == "FAIL"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=int, default=40000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = run(n_random=a.pool)
    print(json.dumps(out["summary"], indent=1))
    print("R1 separation by rows missing:", json.dumps(out["R1_separation_by_rows_missing"]))
    print("controls_ok:", out["controls_ok"], " intermediates without an equal-score other:",
          out["intermediates_with_no_equal_score_other"], "of", out["intermediates"])
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, sort_keys=True, default=str)
            fh.write("\n")


if __name__ == "__main__":
    main()
