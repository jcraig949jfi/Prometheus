"""HT-e106e1603b / W2: syndrome sandpile on a (3,6)-regular Tanner graph.

Arms: TREATMENT, CONTROL, NULL_TWIN, POSITIVE_CONTROL, CHEAT.
See IMPLEMENTATION_NOTES.md. Writes rows.jsonl (flushed per row).
"""
import json
import os
import random
import time

import numpy as np
from sklearn.linear_model import LogisticRegression

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")
ATTEMPTS = os.path.join(HERE, "attempts.json")

NS = (1000, 2000)
DV, DC = 3, 6
T_RULE = 2
MAX_SWEEPS = 50
N_INJ = 30000
CONTROL_BITS = 10
SEEDS = (0, 1, 2, 3, 4)
PC_NP = 20
PC_BLOCKS = 200
PC_PGRID = np.geomspace(0.01, 0.2, PC_NP)
CHEAT_REL_NOISE = 0.02
CPU_BUDGET_S = 540.0
ARM_CODE = {"TREATMENT": 1, "CONTROL": 2, "NULL_TWIN": 3, "POSITIVE_CONTROL": 4,
            "CHEAT": 5, "GRAPH": 0}

PARAMS = dict(dv=DV, dc=DC, t_rule=T_RULE, max_sweeps=MAX_SWEEPS, n_inj=N_INJ,
              control_bits=CONTROL_BITS, pc_blocks=PC_BLOCKS,
              pc_pgrid=[float(p) for p in PC_PGRID], cheat_rel_noise=CHEAT_REL_NOISE,
              cpu_budget_s=CPU_BUDGET_S, four_cycle_free=True)


def rng_for(seed, n, arm):
    return np.random.default_rng(np.random.SeedSequence([seed, n, ARM_CODE[arm]]))


def pyrand_for(seed, n, arm):
    return random.Random(int(rng_for(seed, n, arm).integers(0, 2**62)))


def four_cycle_vars(vc, m):
    """Variables with a repeated check or sharing >= 2 checks with another variable."""
    n = vc.shape[0]
    cvs = [[] for _ in range(m)]
    for v in range(n):
        for c in vc[v]:
            cvs[c].append(v)
    bad = set()
    for v in range(n):
        if len(set(vc[v])) < DV:
            bad.add(v)
            continue
        seen = set()
        for c in vc[v]:
            for w in cvs[c]:
                if w == v:
                    continue
                if w in seen:
                    bad.add(v)
                seen.add(w)
    return sorted(bad)


def build_tanner(n, rng):
    """(3,6)-regular configuration model; multi-edges repaired by socket swaps."""
    m = n * DV // DC
    sock_check = np.repeat(np.arange(m), DC)
    rng.shuffle(sock_check)
    vc = sock_check.reshape(n, DV).copy()
    for _ in range(100000):
        bad = [v for v in range(n) if len(set(vc[v])) < DV]
        if not bad:
            break
        for v in bad:
            j = int(rng.integers(DV))
            w = int(rng.integers(n))
            k = int(rng.integers(DV))
            vc[v, j], vc[w, k] = vc[w, k], vc[v, j]
    else:
        raise RuntimeError("multi-edge repair failed")
    # REPAIR (attempt 2): remove 4-cycles (two variables sharing >= 2 checks) by socket swaps
    for _ in range(100000):
        bad = four_cycle_vars(vc, m)
        if not bad:
            break
        for v in bad:
            j = int(rng.integers(DV))
            w = int(rng.integers(n))
            k = int(rng.integers(DV))
            vc[v, j], vc[w, k] = vc[w, k], vc[v, j]
    else:
        raise RuntimeError("4-cycle repair failed")
    cv_lists = [[] for _ in range(m)]
    for v in range(n):
        for c in vc[v]:
            cv_lists[c].append(v)
    assert all(len(x) == DC for x in cv_lists)
    assert all(len(set(vc[v])) == DV for v in range(n))
    assert not four_cycle_vars(vc, m)
    cv = np.array(cv_lists, dtype=np.int64)
    return vc.astype(np.int64), cv


class SandpileState:
    """Incremental e, syndrome s, unsatisfied counts u; cand = {v: u_v >= 2}."""

    def __init__(self, vc, cv):
        self.n = vc.shape[0]
        self.m = cv.shape[0]
        self.vc = [tuple(int(c) for c in row) for row in vc]
        self.cv = [tuple(int(v) for v in row) for row in cv]
        self.e = bytearray(self.n)
        self.s = bytearray(self.m)
        self.u = [0] * self.n
        self.cand = set()
        self.nerr = 0

    def flip(self, F):
        e, s, u, vc, cv, cand = self.e, self.s, self.u, self.vc, self.cv, self.cand
        tog = {}
        d = 0
        for v in F:
            e[v] ^= 1
            d += 1 if e[v] else -1
            for c in vc[v]:
                tog[c] = tog.get(c, 0) ^ 1
        self.nerr += d
        for c, t in tog.items():
            if t:
                s[c] ^= 1
                dd = 1 if s[c] else -1
                for w in cv[c]:
                    uw = u[w] + dd
                    u[w] = uw
                    if uw >= T_RULE:
                        cand.add(w)
                    else:
                        cand.discard(w)

    def relax(self):
        """Parallel sweeps; returns list of flip counts per sweep."""
        ks = []
        while self.cand and len(ks) < MAX_SWEEPS:
            F = list(self.cand)
            ks.append(len(F))
            self.flip(F)
        return ks


def decode_batch(E, vc, cv):
    """Vectorised parallel 2-of-3 bit flip, full recompute each sweep. E: (B, n) uint8."""
    E = E.copy()
    for _ in range(MAX_SWEEPS):
        S = E[:, cv].sum(axis=2, dtype=np.int16) & 1
        U = S[:, vc].sum(axis=2, dtype=np.int16)
        F = U >= T_RULE
        if not F.any():
            break
        E ^= F.astype(np.uint8)
    return E


def self_test(vc, cv, rng):
    n = vc.shape[0]
    for p in (0.02, 0.04, 0.08):
        E = (rng.random((10, n)) < p).astype(np.uint8)
        Eb = decode_batch(E, vc, cv)
        for b in range(E.shape[0]):
            st = SandpileState(vc, cv)
            st.flip([int(v) for v in np.nonzero(E[b])[0]])
            st.relax()
            assert bytes(st.e) == Eb[b].tobytes(), "decoder mismatch"
    return True


def logistic_crossing(fails):
    """fails: {n: (P_array, y_array)}; returns (p_star or None, fit info)."""
    fits = {}
    for n, (P, y) in fails.items():
        if y.min() == y.max():
            fits[n] = None
            continue
        lr = LogisticRegression(C=1e6, max_iter=1000)
        lr.fit(np.log(P).reshape(-1, 1), y)
        fits[n] = (float(lr.intercept_[0]), float(lr.coef_[0, 0]))
    info = {str(n): (None if f is None else {"a": f[0], "b": f[1]}) for n, f in fits.items()}
    f1, f2 = fits[NS[0]], fits[NS[1]]
    if f1 is None or f2 is None or f1[1] <= 0 or f2[1] <= 0 or f1[1] == f2[1]:
        return None, info
    x = (f2[0] - f1[0]) / (f1[1] - f2[1])
    return float(np.exp(x)), info


class Budget:
    def __init__(self, prior):
        self.t0 = time.process_time()
        self.prior = prior

    def used(self):
        return time.process_time() - self.t0

    def exhausted(self):
        return self.used() > CPU_BUDGET_S


def summarize_avalanche(sizes):
    a = np.asarray(sizes, dtype=np.int64)
    return {"mean": float(a.mean()), "s95": float(np.percentile(a, 95)), "max": int(a.max())}


def run_treatment_and_twin(seed, n, vc, cv, budget, write):
    st = SandpileState(vc, cv)
    rng = rng_for(seed, n, "TREATMENT")
    inj = rng.integers(0, n, size=N_INJ)
    counts, aval, capped, schedule = [], [], 0, []
    truncated = False
    for i in range(N_INJ):
        if i % 50 == 0 and budget.exhausted():
            truncated = True
            break
        st.flip([int(inj[i])])
        ks = st.relax()
        if len(ks) == MAX_SWEEPS and st.cand:
            capped += 1
        schedule.append(ks)
        aval.append(sum(ks))
        counts.append(st.nerr)
    write({"arm": "TREATMENT", "seed": seed, "n": n, "params": PARAMS,
           "truncated": truncated, "n_done": len(counts), "counts": counts,
           "avalanche": summarize_avalanche(aval) if aval else None,
           "capped_relaxations": capped})
    # paired null twin: same graph, same injected bits, matched flip counts, random choice
    prand = pyrand_for(seed, n, "NULL_TWIN")
    e = bytearray(n)
    nerr = 0
    tcounts = []
    for i, ks in enumerate(schedule):
        v = int(inj[i])
        e[v] ^= 1
        nerr += 1 if e[v] else -1
        for k in ks:
            for w in prand.sample(range(n), k):
                e[w] ^= 1
                nerr += 1 if e[w] else -1
        tcounts.append(nerr)
    write({"arm": "NULL_TWIN", "seed": seed, "n": n, "params": PARAMS,
           "truncated": truncated, "n_done": len(tcounts), "counts": tcounts,
           "matched_flip_volume": int(sum(aval))})


def run_control(seed, n, vc, cv, budget, write):
    st = SandpileState(vc, cv)
    prand = pyrand_for(seed, n, "CONTROL")
    counts, aval, capped = [], [], 0
    truncated = False
    for i in range(N_INJ):
        if i % 50 == 0 and budget.exhausted():
            truncated = True
            break
        st.flip(prand.sample(range(n), CONTROL_BITS))
        ks = st.relax()
        if len(ks) == MAX_SWEEPS and st.cand:
            capped += 1
        aval.append(sum(ks))
        counts.append(st.nerr)
    write({"arm": "CONTROL", "seed": seed, "n": n, "params": PARAMS,
           "truncated": truncated, "n_done": len(counts), "counts": counts,
           "avalanche": summarize_avalanche(aval) if aval else None,
           "capped_relaxations": capped})


def main():
    attempts = {"attempts": 0, "cpu_s_total": 0.0}
    if os.path.exists(ATTEMPTS):
        with open(ATTEMPTS) as f:
            attempts = json.load(f)
    attempt = attempts["attempts"] + 1
    if os.path.exists(ROWS):
        os.replace(ROWS, os.path.join(HERE, f"rows_attempt{attempt - 1}.jsonl"))
    budget = Budget(attempts["cpu_s_total"])
    fout = open(ROWS, "w")

    def write(obj):
        obj["attempt"] = attempt
        fout.write(json.dumps(obj) + "\n")
        fout.flush()

    graphs = {}
    for seed in SEEDS:
        for n in NS:
            graphs[(seed, n)] = build_tanner(n, rng_for(seed, n, "GRAPH"))
    self_test(*graphs[(0, 1000)], np.random.default_rng(12345))
    print("self-test ok", flush=True)

    # POSITIVE_CONTROL (L2 threshold), per seed
    pstars = []
    for seed in SEEDS:
        fails, frac = {}, {}
        for n in NS:
            vc, cv = graphs[(seed, n)]
            rng = rng_for(seed, n, "POSITIVE_CONTROL")
            P, Y, fr = [], [], []
            for p in PC_PGRID:
                E = (rng.random((PC_BLOCKS, n)) < p).astype(np.uint8)
                y = (decode_batch(E, vc, cv).sum(axis=1) > 0).astype(int)
                P.extend([p] * PC_BLOCKS)
                Y.extend(y.tolist())
                fr.append(float(y.mean()))
            fails[n] = (np.array(P), np.array(Y))
            frac[str(n)] = fr
        ps, info = logistic_crossing(fails)
        pstars.append(ps)
        write({"arm": "POSITIVE_CONTROL", "seed": seed, "params": PARAMS,
               "p_grid": PARAMS["pc_pgrid"], "fail_frac": frac, "fits": info,
               "p_star_seed": ps})
        print("PC seed", seed, "p*", ps, "cpu", round(budget.used(), 1), flush=True)

    # TREATMENT + paired NULL_TWIN
    for seed in SEEDS:
        for n in NS:
            run_treatment_and_twin(seed, n, *graphs[(seed, n)], budget, write)
            print("T/twin", seed, n, "cpu", round(budget.used(), 1), flush=True)
    # CONTROL
    for seed in SEEDS:
        for n in NS:
            run_control(seed, n, *graphs[(seed, n)], budget, write)
            print("C", seed, n, "cpu", round(budget.used(), 1), flush=True)
    # CHEAT: success written directly into the observable
    valid = [p for p in pstars if p is not None]
    p_ref = float(np.mean(valid)) if valid else 0.05
    for seed in SEEDS:
        for n in NS:
            z = rng_for(seed, n, "CHEAT").standard_normal(N_INJ)
            counts = np.rint(n * p_ref * (1 + CHEAT_REL_NOISE * z)).astype(int).tolist()
            write({"arm": "CHEAT", "seed": seed, "n": n, "params": PARAMS,
                   "truncated": False, "n_done": N_INJ, "counts": counts,
                   "cheat_p_ref": p_ref})
    cpu = budget.used()
    attempts = {"attempts": attempt, "cpu_s_total": attempts["cpu_s_total"] + cpu}
    write({"arm": "META", "cpu_s_this_attempt": cpu,
           "cpu_s_total": attempts["cpu_s_total"], "attempts": attempt})
    fout.close()
    with open(ATTEMPTS, "w") as f:
        json.dump(attempts, f)
    print("done cpu", round(cpu, 1), flush=True)


if __name__ == "__main__":
    main()
