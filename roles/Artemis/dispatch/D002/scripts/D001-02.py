"""D001-02 -- which non-standard WTP physics stays learnable?  (NOT RUN by the author; outputs unknown.)

Inputs (read-only, repo commit 0424c372a6bba88f50d31f3abbd8b1204871bba6):
  ensorain/runs/wtp03/waveA.json@0424c372a       (admitted genomes, Wave A of WTP-03)
  ensorain/wtp/registry.py@0424c372a             (REG, FIELD_OPS, VECTOR_OPS, sample_params)
  ensorain/wtp/world.py@0424c372a                (base_field, _std)
  ensorain/wtp/genome.py@0424c372a               (_dims, GENERATORS)

Run from a checkout of that commit:   python analysis.py [--repo PATH] [--draws 60] [--seed 7]
Dependencies: stdlib + numpy (+ the repo's own numpy-only modules named above).

Parts
  A  Descriptive tally of the 181 admitted WTP-03 worlds (exact counts that the report makes by grep):
     per-law weirdness features, per founder root, and the obs-kind x obs-chain cross-tab.
  B  FIELD-LAW ablation (offline, economy-free): for each field op, apply it to base fields from every
     generator and measure the G5-style completion excess (masked ALS on the best unfolding minus the
     best of constant/additive nulls) on interp cells. Compared with the no-op baseline.
  C  CHANNEL-LAW ablation: fixed learnable fields; vary observation kind, vector-op chain and credit
     corruption (noise, sign_flip, radius, delay). Measure label fidelity against the scored target and
     the completion excess when training on the corrupted stream and scoring on the true field.
  D  DYNAMICS-LAW ablation: basis_change_period, catastrophe_rate, drift. Stream sampled from the evolving
     field, scored on x_final (as collider.experience does, ensorain/wtp3/collider.py:85-91).

What decides the question (declared before any output exists):
  H1 (separating property) holds if ALL of:
    B: every op in PRESERVE has median excess >= 0.8 x the no-op median AND frac(excess >= .10) within
       .15 of the no-op fraction; and at least 4 of the ops in DESTROY fall below .5 x the no-op median.
    C: cell/fiber/masked with an empty chain, v_tanh, or v_quantize(levels>=4) keep >= .8 x baseline
       excess; marginal obs and fiber/masked + (v_cumsum | v_sort | v_fft_abs) fall below .5 x baseline;
       delay>0 changes excess by < .05 (information-neutral); sign_flip degrades monotonically.
    D: any basis_change_period < lifetime or catastrophe_rate >= .005 drops excess below .5 x baseline;
       drift <= .1 keeps >= .8 x baseline.
  If B shows DESTROY ops that stay learnable, or PRESERVE ops that do not, H1's field clause is wrong.
  If C shows marginal/cumsum channels staying learnable, the "channel corruption" clause is wrong and
  the WTP-03 scarcity is economic (G1-G4), not informational.
"""
import argparse
import collections
import json
import os
import sys

import numpy as np

PRESERVE = ("f_permute", "f_split_mode", "f_merge_modes", "f_gemv_mode", "f_qr_mode", "f_contract_mode",
            "f_svd_power", "f_tt_round", "f_lowpass", "f_outer_marginals")
ALGEBRAIC = ("f_hadamard_self", "f_reduce_norm")          # structure-raising but deterministic/smooth
DESTROY = ("f_binary_field", "f_mask", "f_noise", "f_rare_spikes", "f_unary", "f_topk_sparsify",
           "f_phase_scramble", "f_fft_abs", "f_reduce_max", "f_correlated_noise")


# ------------------------------------------------------------------ shared estimators

def AC(pred, y, V0):
    mse = float(np.mean((np.nan_to_num(pred) - y) ** 2))
    return float(np.clip(-np.log10(max(mse / max(V0, 1e-12), 1e-12)), -3, 6))


def interp_cells(dims, seen_flat):
    """Unseen cells with a seen cell differing in exactly one coordinate (PREREG_WTP03 s2 'interp')."""
    seen = seen_flat.reshape(dims)
    near = np.zeros(dims, bool)
    for m in range(len(dims)):
        near |= np.broadcast_to(seen.any(axis=m, keepdims=True), dims)
    return np.flatnonzero((near & ~seen).reshape(-1))


def additive_fit(dims, c, y, sweeps=5):
    addr = np.array(np.unravel_index(c, dims)).T
    mu = float(y.mean())
    eff = [np.zeros(n) for n in dims]
    for _ in range(sweeps):
        for m, n in enumerate(dims):
            r = y - mu - sum(eff[k][addr[:, k]] for k in range(len(dims)) if k != m)
            s = np.bincount(addr[:, m], weights=r, minlength=n)
            k_ = np.bincount(addr[:, m], minlength=n)
            eff[m] = np.where(k_ > 0, s / np.maximum(k_, 1), 0.0)

    def pred(cells):
        a = np.array(np.unravel_index(cells, dims)).T
        return mu + sum(eff[k][a[:, k]] for k in range(len(dims)))
    return pred


def masked_als(rows, cols, y, a, b, r, lam, iters, rng):
    U = 0.1 * rng.normal(size=(a, r))
    V = 0.1 * rng.normal(size=(b, r))
    by_r = collections.defaultdict(list)
    by_c = collections.defaultdict(list)
    for i, (p, q) in enumerate(zip(rows, cols)):
        by_r[p].append(i)
        by_c[q].append(i)
    I = lam * np.eye(r)
    for _ in range(iters):
        for p, ix in by_r.items():
            Vi = V[cols[ix]]
            U[p] = np.linalg.solve(Vi.T @ Vi + I, Vi.T @ y[ix])
        for q, ix in by_c.items():
            Ui = U[rows[ix]]
            V[q] = np.linalg.solve(Ui.T @ Ui + I, Ui.T @ y[ix])
    return U, V


def completion_fit(dims, c, y, rng, ranks=(1, 2, 3, 4), lams=(.01, .1, 1.), iters=15):
    """Best (unfolding cut, rank, ridge) chosen on a 10% validation split of the TRAINING stream only."""
    n = len(c)
    perm = rng.permutation(n)
    nv = max(8, n // 10)
    va, tr = perm[:nv], perm[nv:]
    best = None
    D = len(dims)
    for k in range(1, D):
        b = int(np.prod(dims[k:]))
        a = int(np.prod(dims[:k]))
        rows, cols = c // b, c % b
        for r in ranks:
            if r > min(a, b):
                continue
            for lam in lams:
                U, V = masked_als(rows[tr], cols[tr], y[tr], a, b, r, lam, iters, rng)
                err = float(np.mean(((U[rows[va]] * V[cols[va]]).sum(1) - y[va]) ** 2))
                if best is None or err < best[0]:
                    best = (err, k, r, lam)
    if best is None:
        return None
    _, k, r, lam = best
    b = int(np.prod(dims[k:]))
    a = int(np.prod(dims[:k]))
    U, V = masked_als(c // b, c % b, y, a, b, r, lam, iters, rng)
    return lambda cells: (U[cells // b] * V[cells % b]).sum(1)


def excess_on(dims, x_true, c, y, rng):
    """Completion AC minus best of (constant, additive) on interp cells, scored on x_true."""
    x = x_true.reshape(-1)
    V0 = float(x.var())
    seen = np.zeros(x.size, bool)
    seen[c] = True
    T = interp_cells(dims, seen)
    if len(T) > 512:
        T = rng.choice(T, 512, replace=False)
    if len(T) < 32:
        return None
    f = completion_fit(dims, c, y, rng)
    if f is None:
        return None
    ac_c = AC(f(T), x[T], V0)
    ac_const = AC(np.full(len(T), y.mean()), x[T], V0)
    ac_add = AC(additive_fit(dims, c, y)(T), x[T], V0)
    return ac_c - max(ac_const, ac_add, 0.0)


# ------------------------------------------------------------------ Part A

def part_a(repo):
    W = json.load(open(os.path.join(repo, "ensorain", "runs", "wtp03", "waveA.json")))
    adm = W["admitted"]
    cls = {**{o: "PRESERVE" for o in PRESERVE}, **{o: "ALGEBRAIC" for o in ALGEBRAIC}, **{o: "DESTROY" for o in DESTROY}}
    C = collections.Counter()
    per_root = collections.defaultdict(collections.Counter)
    xtab = collections.Counter()
    for a in adm:
        g = a["g"]
        s, ob, cr, tr, geo = g["substrate"], g["observation"], g["credit"], g["transition"], g["geometry"]
        f = dict(
            stratum=a["stratum"], gen=s["gen"], geo=geo["kind"], obs=ob["kind"],
            field_chain=bool(s["chain"]), obs_chain=bool(ob["chain"]), reward_chain=bool(s.get("reward_chain")),
            field_destroy=any(cls.get(o["op"]) == "DESTROY" for o in s["chain"]),
            field_only_preserve=bool(s["chain"]) and all(cls.get(o["op"]) == "PRESERVE" for o in s["chain"]),
            sign_flip_material=cr["sign_flip"] >= 0.01, credit_noise_gt05=cr["noise"] > 0.05,
            radius=cr["radius"] > 0, delay=cr["delay"] > 0,
            drift=tr["drift"] > 0, basis=tr["basis_change_period"] > 0, catastrophe=tr["catastrophe_rate"] > 0,
            door_close=g["irreversibility"]["door_close"] > 0, rewire=tr["rewire_period"] > 0,
        )
        for k, v in f.items():
            C[(k, v)] += 1
            per_root[a["root"]][(k, v)] += 1
        xtab[(ob["kind"], tuple(o["op"] for o in ob["chain"]))] += 1
        for o in s["chain"]:
            C[("field_op", o["op"])] += 1
        for o in s.get("reward_chain", []):
            C[("reward_op", o["op"])] += 1
        for o in ob["chain"]:
            C[("obs_op", o["op"])] += 1
    print("PART A  admitted =", len(adm), " roots =", len(per_root))
    for k in sorted(C, key=str):
        print("  ", k, C[k])
    print("  obs kind x obs chain:")
    for k, v in sorted(xtab.items(), key=lambda kv: -kv[1]):
        print("    ", k, v)
    print("  per root (n, tensor_index, field_destroy, obs_chain):")
    for r, c in per_root.items():
        n = sum(v for (k, _), v in c.items() if k == "stratum")
        print("    ", r, n, c[("geo", "tensor_index")], c[("field_destroy", True)], c[("obs_chain", True)])
    founders = [a for a in adm if a["stratum"] != "mutant"]
    print("  non-mutant founders:", [(a["stratum"], a["g"]["geometry"]["kind"], a["g"]["observation"]["kind"],
                                      [o["op"] for o in a["g"]["substrate"]["chain"]]) for a in founders])


# ------------------------------------------------------------------ Part B

def part_b(draws, seed):
    from ensorain.wtp.registry import REG, FIELD_OPS, sample_params
    from ensorain.wtp.world import base_field, _std
    from ensorain.wtp.genome import _dims
    gens = ("lowrank", "cp", "tt", "pairwise", "spectral", "sum", "sparse", "random")
    res = collections.defaultdict(list)
    rng = np.random.default_rng(seed)
    for d in range(draws):
        for gen in gens:
            dims = _dims(rng)
            x0 = base_field(gen, dims, int(rng.integers(1, 6)), rng)
            for op in (None,) + tuple(FIELD_OPS):
                r2 = np.random.default_rng(rng.integers(2 ** 62))
                try:
                    x = x0 if op is None else np.asarray(REG[op].fn(x0, sample_params(REG[op], r2), r2), float)
                except Exception:
                    continue
                if (not np.all(np.isfinite(x))) or x.ndim < 2 or x.size < 64 or x.size > 4096 or x.std() < 1e-6:
                    continue
                x = _std(x)
                n = max(16, int(0.2 * x.size))
                c = r2.integers(x.size, size=n)
                y = x.reshape(-1)[c] + 0.1 * r2.normal(size=n)
                e = excess_on(list(x.shape), x, c, y, r2)
                if e is not None:
                    res[(op or "NONE", gen)].append(e)
    print("PART B  field-op ablation: op, class, median excess, frac>=.10, n  (pooled over structured gens)")
    structured = ("lowrank", "cp", "tt", "pairwise", "spectral", "sum")
    for op in ("NONE",) + tuple(FIELD_OPS):
        v = [e for g in structured for e in res[(op, g)]]
        if v:
            k = "PRESERVE" if op in PRESERVE else "ALGEBRAIC" if op in ALGEBRAIC else "DESTROY" if op in DESTROY else "-"
            print(f"   {op:22s} {k:9s} {np.median(v):7.3f} {np.mean(np.array(v) >= .10):5.2f} {len(v)}")
    for gen in ("sparse", "random"):
        v = res[("NONE", gen)]
        if v:
            print(f"   NONE on {gen:8s} median {np.median(v):.3f} frac>=.10 {np.mean(np.array(v) >= .10):.2f}")
    return res


# ------------------------------------------------------------------ Part C

def observe(x, dims, cell, kind, mode, k, chain, noise_sd, rng, REG, t):
    a = np.array(np.unravel_index(cell, dims))
    if kind == "cell":
        cc = np.array([cell])
    else:
        m = mode % len(dims)
        fib = np.repeat(a[None], dims[m], 0)
        fib[:, m] = np.arange(dims[m])
        cc = np.ravel_multi_index(fib.T, dims)
        if kind == "masked":
            cc = cc[rng.permutation(len(cc))[:min(k, len(cc))]]
    vals = x.reshape(-1)[cc].copy()
    if kind == "marginal":
        vals = np.full(1, vals.mean())
        cc = np.array([cell])
    for op in chain:                          # same semantics as ensorain/wtp3/world3.py:215-218
        vals = np.asarray(REG[op["op"]].fn(vals, op["p"], np.random.default_rng(t)), float)
        if vals.shape[0] != len(cc):
            vals = np.resize(vals, len(cc))
    return cc, vals + noise_sd * rng.normal(size=len(vals))


def part_c(draws, seed):
    from ensorain.wtp.registry import REG
    from ensorain.wtp.world import base_field, _std
    rng = np.random.default_rng(seed + 1)
    chains = {"none": [], "v_tanh": [{"op": "v_tanh", "p": {}}], "v_sign": [{"op": "v_sign", "p": {}}],
              "v_quantize4": [{"op": "v_quantize", "p": {"levels": 4}}], "v_quantize2": [{"op": "v_quantize", "p": {"levels": 2}}],
              "v_cumsum": [{"op": "v_cumsum", "p": {}}], "v_sort": [{"op": "v_sort", "p": {}}],
              "v_fft_abs": [{"op": "v_fft_abs", "p": {}}], "v_sign+v_cumsum": [{"op": "v_sign", "p": {}}, {"op": "v_cumsum", "p": {}}]}
    credits = {"clean": dict(noise=0, sign_flip=0, radius=0, delay=0), "delay32": dict(noise=0, sign_flip=0, radius=0, delay=32),
               "noise.5": dict(noise=.5, sign_flip=0, radius=0, delay=0), "flip.03": dict(noise=0, sign_flip=.03, radius=0, delay=0),
               "flip.15": dict(noise=0, sign_flip=.15, radius=0, delay=0), "flip.3": dict(noise=0, sign_flip=.3, radius=0, delay=0),
               "radius2": dict(noise=0, sign_flip=0, radius=2, delay=0)}
    res = collections.defaultdict(list)
    for d in range(draws):
        gen = str(rng.choice(["lowrank", "cp", "tt", "pairwise"]))
        dims = [int(v) for v in rng.choice([[8, 8, 8], [12, 12, 6], [16, 16], [5, 5, 5, 5]])]
        x = _std(base_field(gen, dims, int(rng.integers(1, 5)), rng))
        T = int(0.15 * x.size)
        for kind in ("cell", "fiber", "masked", "marginal"):
            for cname, chain in chains.items():
                for crn, cr in credits.items():
                    if cname != "none" and crn != "clean":
                        continue                 # one-factor-at-a-time
                    r2 = np.random.default_rng(rng.integers(2 ** 62))
                    cs, ys = [], []
                    for t in range(T):
                        cell = int(r2.integers(x.size))
                        cc, v = observe(x, dims, cell, kind, int(r2.integers(16)), 4, chain, 0.1, r2, REG, t)
                        cc, v = cc[:64], v[:64]
                        if cr["noise"] > 0 and len(v) <= 32:
                            v = v + cr["noise"] * r2.normal(size=len(v))
                        if cr["sign_flip"] > 0 and r2.random() < cr["sign_flip"]:
                            v = -v
                        if cr["radius"] > 0:        # tensor_index neighbour: change one coordinate
                            ex_c, ex_v = [], []
                            for c1, v1 in zip(cc, v):
                                for _ in range(cr["radius"]):
                                    a = np.array(np.unravel_index(int(c1), dims))
                                    m = int(r2.integers(len(dims)))
                                    a[m] = int(r2.integers(dims[m]))
                                    ex_c.append(int(np.ravel_multi_index(a, dims)))
                                    ex_v.append(v1)
                            cc, v = np.concatenate([cc, ex_c]).astype(int), np.concatenate([v, ex_v])
                        if t + cr["delay"] < T:     # delay only truncates the tail of the stream
                            cs.append(cc)
                            ys.append(v)
                    c, y = np.concatenate(cs).astype(int), np.concatenate(ys)
                    fid = 1 - float(np.mean((y - x.reshape(-1)[c]) ** 2)) / float(x.var())
                    e = excess_on(dims, x, c, y, r2)
                    res[(kind, cname, crn)].append((fid, e))
    print("PART C  channel ablation: kind, obs chain, credit, median label R2, median excess, frac>=.10, n")
    for key, v in sorted(res.items()):
        f = [a for a, _ in v]
        e = [b for _, b in v if b is not None]
        if e:
            print(f"   {key!s:45s} {np.median(f):7.3f} {np.median(e):7.3f} {np.mean(np.array(e) >= .1):5.2f} {len(e)}")
    return res


# ------------------------------------------------------------------ Part D

def part_d(draws, seed):
    from ensorain.wtp.world import base_field, _std
    rng = np.random.default_rng(seed + 2)
    settings = {"static": {}, "drift.05/100": dict(drift=.05, period=100), "drift.3/100": dict(drift=.3, period=100),
                "basis/400": dict(basis=400), "basis/100": dict(basis=100),
                "cat.002": dict(cat=.002), "cat.01": dict(cat=.01)}
    res = collections.defaultdict(list)
    for d in range(draws):
        gen = str(rng.choice(["lowrank", "cp", "tt", "pairwise"]))
        dims = [12, 12, 6]
        rank = int(rng.integers(1, 5))
        x0 = _std(base_field(gen, dims, rank, rng))
        T = 1500
        for name, s in settings.items():
            r2 = np.random.default_rng(rng.integers(2 ** 62))
            x = x0.copy()
            cs, ys = [], []
            for t in range(T):
                if s.get("drift") and t > 0 and t % s["period"] == 0:
                    x = np.sqrt(1 - s["drift"]) * x + np.sqrt(s["drift"]) * _std(base_field(gen, dims, rank, r2))
                if s.get("basis") and t > 0 and t % s["basis"] == 0:
                    m = int(r2.integers(len(dims)))
                    x = np.take(x, r2.permutation(dims[m]), axis=m)
                if s.get("cat") and r2.random() < s["cat"]:
                    m = int(r2.integers(len(dims)))
                    sl = [slice(None)] * len(dims)
                    sl[m] = int(r2.integers(dims[m]))
                    x = x.copy()
                    x[tuple(sl)] = 0.0
                c = int(r2.integers(x.size))
                cs.append(c)
                ys.append(float(x.reshape(-1)[c] + 0.1 * r2.normal()))
            c, y = np.array(cs), np.array(ys)
            res[name].append(excess_on(dims, x, c, y, r2))       # scored on x_final
    print("PART D  dynamics ablation (scored on x_final): setting, median excess, frac>=.10, n")
    for k, v in res.items():
        v = [e for e in v if e is not None]
        if v:
            print(f"   {k:14s} {np.median(v):7.3f} {np.mean(np.array(v) >= .1):5.2f} {len(v)}")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--draws", type=int, default=60)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--parts", default="ABCD")
    A = ap.parse_args()
    sys.path.insert(0, os.path.abspath(A.repo))
    if "A" in A.parts:
        part_a(A.repo)
    if "B" in A.parts:
        part_b(A.draws, A.seed)
    if "C" in A.parts:
        part_c(max(10, A.draws // 3), A.seed)
    if "D" in A.parts:
        part_d(max(10, A.draws // 3), A.seed)
