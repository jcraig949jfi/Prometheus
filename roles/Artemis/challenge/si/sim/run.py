"""SI Phase 2 driver: prereg s5 (1b573ac95) as amended in AMENDMENTS_P2.md (written before any grid cell ran).

usage: python3 run.py OUTDIR [--smoke]
"""
import json
import math
import os
import random
import sys
import time
from multiprocessing import Pool

import numpy as np

import sources as src
from learners import run_learner
from search_c1 import search_cell

BUDGET_S = 3600.0
F1_Q = [0.0, 0.01, 0.03, 0.1, 0.3]
F1_W = [0, 1, 2, 4, 8, 16, 64, None]
F2_W = [0, 1, 2, None]
F3_W = [1, 2, 4, 8, 16, None]
F3_K = [1, 2, 3, 4, 6]
F3_X = [2, 4]
LMT_W = [8, 32]
F4_CELLS = [(W, d) for W in (1, 2, 3) for d in (8, 10, 12)]
REVERSIBLE = ("RG", "RU", "RULMT", "RQ", "RMIN", "RH", "RX")


def make_ih(m, seed, T):
    rng = np.random.Generator(np.random.PCG64(seed ^ 0x5EED))
    PH = [rng.permutation(256).tolist() for _ in range(m.nX)]
    PHinv = []
    for P in PH:
        inv = [0] * 256
        for i, v in enumerate(P):
            inv[v] = i
        PHinv.append(inv)
    kbit = rng.integers(0, 8, size=T + 1)
    # calibration on a disjoint sequence (A6)
    Tc = 65536
    xs2, S2 = m.sample(Tc, (seed * 7 + 12345) % (2 ** 32))
    kb2 = rng.integers(0, 8, size=Tc + 1)
    counts = np.full((256, m.nX), 0.5)
    h = 0
    for t in range(1, Tc):
        x = int(xs2[t])
        h = PH[x][h]
        if m.merges(int(S2[t]), x):
            h &= ~(1 << int(kb2[t]))
        counts[h, int(xs2[t + 1])] += 1
    PIH = counts / counts.sum(axis=1, keepdims=True)
    return (PH, PHinv, kbit, PIH)


def oracle_loss(m, xs, S):
    T = len(xs) - 1
    return float(np.mean([-math.log2(m.T[int(S[t]), int(xs[t + 1])]) for t in range(1, T)]))


def run_specs(m, xs, S, Dend, specs, seed, meta):
    rows = []
    ih = None
    for (kind, W, cap, k) in specs:
        if kind == "IH" and ih is None:
            ih = make_ih(m, seed, len(xs) - 1)
        r = run_learner(kind, m, xs, S, Dend, W, cap=cap, k=k, ih=ih)
        r.update(meta)
        rows.append(r)
    return rows


def specs_F1(q):
    sp = []
    for W in F1_W:
        if W == 0:
            sp += [("I", 0, None, None)] + [("IW", 0, None, k) for k in (2, 8, 32)]
            sp += [("IH", 0, None, None), ("RH", 0, None, None), ("RX", 0, None, None), ("RQ", 0, None, None)]
        else:
            sp += [("I", W, None, None)]
            if W is not None:
                sp += [("RG", W, 8, None), ("RG", W, 64, None)]
            sp += [("RG", W, None, None), ("RU", W, None, None), ("RQ", W, None, None)]
            if q == 0.0:
                sp += [("RMIN", W, None, None)]
    return sp


def specs_F2(name):
    sp = []
    for W in F2_W:
        if W == 0:
            sp += [("I", 0, None, None), ("RQ", 0, None, None)]
        else:
            sp += [("I", W, None, None), ("RG", W, None, None), ("RU", W, None, None), ("RQ", W, None, None)]
            if name == "EVEN":
                sp += [("RMIN", W, None, None)]
    return sp


def specs_F3():
    sp = []
    for W in F3_W:
        sp += [("I", W, None, None), ("RG", W, None, None), ("RU", W, None, None), ("RQ", W, None, None)]
        if W == 1:
            sp += [("IH", 1, None, None)]
    return sp


def machine_F3(k, X, j):
    return src.random_machine(k, X, src.seed_for("F3gen", "k%dX%d" % (k, X), j))


def job(spec):
    t0 = time.process_time()
    fam = spec["fam"]
    rows = []
    info = {}
    if fam == "F1":
        m = src.rp(spec["q"])
        seed = src.seed_for("F1", "RP%g" % spec["q"], spec["i"])
        xs, S = m.sample(spec["T"], seed)
        Dend = m.sync_depth_end(xs)
        meta = dict(fam="F1", source=m.name, q=spec["q"], seed_i=spec["i"], T=spec["T"], oracle_loss=oracle_loss(m, xs, S))
        rows = run_specs(m, xs, S, Dend, specs_F1(spec["q"]), seed, meta)
    elif fam == "F2":
        m = src.golden_mean() if spec["name"] == "GM" else src.even()
        seed = src.seed_for("F2", spec["name"], spec["i"])
        xs, S = m.sample(spec["T"], seed)
        Dend = m.sync_depth_end(xs)
        meta = dict(fam="F2", source=m.name, seed_i=spec["i"], T=spec["T"], oracle_loss=oracle_loss(m, xs, S))
        rows = run_specs(m, xs, S, Dend, specs_F2(spec["name"]), seed, meta)
    elif fam in ("F3", "LMT"):
        m = machine_F3(spec["k"], spec["X"], spec["j"])
        seed = src.seed_for(fam, m.name, spec["i"])
        xs, S = m.sample(spec["T"], seed)
        Dend = m.sync_depth_end(xs)
        meta = dict(fam=fam, source=m.name, k=spec["k"], X=spec["X"], j=spec["j"], seed_i=spec["i"], T=spec["T"],
                    oracle_loss=oracle_loss(m, xs, S), rejects=m.rejects, co_unifilar=m.co_unifilar())
        if fam == "F3":
            rows = run_specs(m, xs, S, Dend, specs_F3(), seed, meta)
        else:
            sp = []
            for W in LMT_W:
                sp += [("I", W, None, None), ("RULMT", W, None, None), ("RU", W, None, None)]
            rows = run_specs(m, xs, S, Dend, sp, seed, meta)
    elif fam == "F4":
        info = search_cell(spec["W"], spec["d"], spec["cap_s"])
    cpu = time.process_time() - t0
    return dict(spec=spec, rows=rows, info=info, cpu=cpu)


def build_jobs(T1=8192, T2=8192, T3=4096, f3_seeds=4, smoke=False):
    jobs = []
    for q in F1_Q:
        for i in range(8 if not smoke else 1):
            jobs.append(dict(fam="F1", q=q, i=i, T=T1))
    for name in ("GM", "EVEN"):
        for i in range(8 if not smoke else 1):
            jobs.append(dict(fam="F2", name=name, i=i, T=T2))
    for k in F3_K:
        for X in F3_X:
            for j in range(8 if not smoke else 1):
                for i in range(f3_seeds if not smoke else 1):
                    jobs.append(dict(fam="F3", k=k, X=X, j=j, i=i, T=T3))
    for k in (1, 2, 3, 4):
        for X in F3_X:
            for j in range(8 if not smoke else 1):
                for i in range(2 if not smoke else 1):
                    jobs.append(dict(fam="LMT", k=k, X=X, j=j, i=i, T=512))
    return jobs


def main():
    out = sys.argv[1]
    smoke = "--smoke" in sys.argv
    os.makedirs(out, exist_ok=True)
    log = open(os.path.join(out, "run_log.txt"), "a")

    def L(msg):
        line = "%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
        print(line, flush=True)
        log.write(line + "\n")
        log.flush()

    wall0 = time.time()
    cpu_spent = 0.0
    if smoke:
        # toy sizes only (A0): not grid cells, results discarded
        jobs = build_jobs(T1=300, T2=300, T3=200, f3_seeds=1, smoke=True)
        jobs = [j for j in jobs if j["fam"] != "LMT"][:12] + [j for j in jobs if j["fam"] == "LMT"][:2]
        with Pool(4) as p:
            res = p.map(job, jobs)
        for r in res:
            for row in r["rows"]:
                if row["kind"] in REVERSIBLE and not row["cert"]:
                    L("SMOKE CERT FAIL %s %s" % (row["source"], row["kind"]))
        L("smoke ok, %d jobs, cpu %.1f" % (len(res), sum(r["cpu"] for r in res)))
        print(search_cell(1, 5, 20))
        print(search_cell(2, 5, 20))
        return

    # A4: the preregistered F4 caps alone (9 x 600 s) exceed the 3600 s budget, so the
    # preregistered scale-down order is applied in full before any run.
    T1, f3_seeds, f4_cells = 4096, 2, [(W, d) for (W, d) in F4_CELLS if d != 12]
    L("A4 scale-down applied before any run: F3 seeds 4->2, F1 T 8192->4096, F4 d=12 dropped")
    jobs = build_jobs(T1=T1, T2=8192, T3=4096, f3_seeds=f3_seeds)
    rnd = random.Random(src.FREEZE_SHA)
    rnd.shuffle(jobs)
    n10 = max(1, len(jobs) // 10)
    results = []
    with Pool(4) as p:
        first = p.map(job, jobs[:n10])
        results += first
        cpu_spent += sum(r["cpu"] for r in first)
        per = {}
        for r in first:
            per.setdefault(r["spec"]["fam"], []).append(r["cpu"])
        proj = 0.0
        for fam in ("F1", "F2", "F3", "LMT"):
            cnt = sum(1 for j in jobs if j["fam"] == fam)
            mean = np.mean(per[fam]) if fam in per else np.mean([r["cpu"] for r in first])
            proj += mean * cnt
        L("first 10%% (%d jobs): cpu %.1f s; projection F1-F3+LMT = %.1f s; reserve for F4 = %.1f s" %
          (n10, cpu_spent, proj, BUDGET_S - proj))
        rest = p.map(job, jobs[n10:], chunksize=1)
        results += rest
        cpu_spent += sum(r["cpu"] for r in rest)
    L("F1-F3+LMT done: cpu %.1f s, wall %.1f s" % (cpu_spent, time.time() - wall0))
    remaining = BUDGET_S - cpu_spent - 60.0
    cap = max(30.0, min(600.0, remaining / len(f4_cells)))
    L("F4: %d cells, per-cell cap %.1f s (A4)" % (len(f4_cells), cap))
    with Pool(4) as p:
        f4 = p.map(job, [dict(fam="F4", W=W, d=d, cap_s=cap) for (W, d) in f4_cells], chunksize=1)
    cpu_spent += sum(r["cpu"] for r in f4)
    results += f4
    L("ALL done: total cpu %.1f s, wall %.1f s" % (cpu_spent, time.time() - wall0))
    rows = [row for r in results for row in r["rows"]]
    f4info = [r["info"] for r in f4]
    with open(os.path.join(out, "rows.json"), "w") as f:
        json.dump(rows, f, default=float)
    with open(os.path.join(out, "f4.json"), "w") as f:
        json.dump(f4info, f, default=float)
    with open(os.path.join(out, "budget.json"), "w") as f:
        json.dump(dict(cpu_total_s=cpu_spent, wall_s=time.time() - wall0, T1=T1, f3_seeds=f3_seeds,
                       f4_cells=f4_cells, f4_cap_s=cap, n_jobs=len(jobs)), f)
    L("wrote rows.json (%d rows), f4.json" % len(rows))


if __name__ == "__main__":
    main()
