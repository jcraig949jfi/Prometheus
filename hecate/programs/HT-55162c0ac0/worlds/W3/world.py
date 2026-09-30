"""HT-55162c0ac0 / W3: order effect under a rising modulator in globally
coupled logistic maps. See IMPLEMENTATION_NOTES.md (written first).

Writes rows.jsonl (one JSON object per (arm, seed), flushed per row) plus
one META row. Parameters are fixed; do not tune after a treatment result.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json
import time
import numpy as np
from scipy.sparse.csgraph import connected_components
from sklearn.metrics import adjusted_rand_score

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

N = 100
EPS = 0.1
AMP = 0.02
FORCED = 500
UNFORCED = 1000
UNFORCED_LONG = 5000
SEEDS = list(range(30))
TOL = 1e-5
LAST = 20
RHO = 0.5
CAL_STEPS, CAL_BURN = 1200, 200
SWEEP_A = np.linspace(3.7, 3.9, 21)
SWEEP_STEPS = 200
EASY_HARD = [(2, 3.7), (4, 3.8), (8, 3.9)]
HARD_EASY = [(8, 3.9), (4, 3.8), (2, 3.7)]
PARAMS = dict(N=N, eps=EPS, amp=AMP, forced=FORCED, unforced=UNFORCED,
              tol=TOL, last=LAST, rho=RHO, cal_steps=CAL_STEPS,
              cal_burn=CAL_BURN, sweep_n=len(SWEEP_A), sweep_steps=SWEEP_STEPS)


def f_log(x, a):
    return a * x * (1.0 - x)


class Affine:
    """Contracting affine null map g_a(x) = mu + rho (x - mu) + s xi."""

    def __init__(self, cal, rng):
        self.cal = cal  # a -> (mu, s)
        self.rng = rng

    def __call__(self, x, a):
        mu, s = self.cal[round(a, 4)]
        return mu + RHO * (x - mu) + s * self.rng.standard_normal(x.shape)


def step(x, a, b, fmap):
    fx = fmap(x, a)
    return (1.0 - EPS) * fx + EPS * fx.mean() + b


def partition(hist):
    """hist: (LAST, N). Link i,j if max_t |x_i - x_j| < TOL; components."""
    d = np.max(np.abs(hist[:, :, None] - hist[:, None, :]), axis=0)
    _, lab = connected_components(d < TOL, directed=False)
    return lab


def make_patterns(rng):
    pats = {}
    for k in (2, 4, 8):
        lab = rng.permutation(np.arange(N) % k)
        pats[k] = lab
    return pats


def levels(lab, k):
    return AMP * lab / (k - 1)


def run_protocol(x0, pats, schedule, fmap, unforced, a_fixed=None):
    x = x0.copy()
    for k, a in schedule:
        a_use = a_fixed if a_fixed is not None else a
        b = levels(pats[k], k)
        for _ in range(FORCED):
            x = step(x, a_use, b, fmap)
    a_end = a_fixed if a_fixed is not None else schedule[-1][1]
    zero = np.zeros(N)
    hist = np.empty((unforced, N))
    for t in range(unforced):
        x = step(x, a_end, zero, fmap)
        hist[t] = x
    lab = partition(hist[-LAST:])
    return lab, hist, a_end


def score(lab, pats, ks):
    aris = {str(k): float(adjusted_rand_score(pats[k], lab)) for k in ks}
    return aris, float(np.mean(list(aris.values())))


def calibrate(seed):
    rng = np.random.default_rng(20_000 + seed)
    cal, raw = {}, {}
    zero = np.zeros(N)
    for a in (3.7, 3.8, 3.9):
        x = rng.uniform(0, 1, N)
        h = np.empty((CAL_STEPS, N))
        for t in range(CAL_STEPS):
            x = step(x, a, zero, f_log)
            h[t] = x
        h = h[CAL_BURN:]
        mu = float(h.mean())
        var = float(h.var(axis=0).mean())
        s = np.sqrt(var * (1 - (1 - EPS) ** 2 * RHO ** 2)) / (1 - EPS)
        cal[round(a, 4)] = (mu, float(s))
        raw[str(a)] = {"mu": mu, "target_var": var, "s": float(s)}
    return cal, raw


def loop_area(x0):
    x = x0.copy()
    zero = np.zeros(N)
    q = {}
    for direction, arr in (("up", SWEEP_A), ("down", SWEEP_A[::-1])):
        qs = []
        for a in arr:
            h = np.empty((SWEEP_STEPS, N))
            for t in range(SWEEP_STEPS):
                x = step(x, a, zero, f_log)
                h[t] = x
            qs.append(len(np.unique(partition(h[-LAST:]))) / N)
        q[direction] = qs if direction == "up" else qs[::-1]
    up, down = np.array(q["up"]), np.array(q["down"])
    area = float(np.trapezoid(up - down, SWEEP_A))
    return area, q


def main():
    prior_cpu, attempt = 0.0, 1
    if os.path.exists(ROWS):
        with open(ROWS, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("arm") == "META":
                    prior_cpu = r["cumulative_cpu_seconds"]
                    attempt = r["attempt"] + 1
        os.replace(ROWS, os.path.join(HERE, f"rows_attempt{attempt - 1}.jsonl"))
    t0 = time.process_time()
    out = open(ROWS, "w", encoding="utf-8")

    def emit(row):
        row.update(params=PARAMS, attempt=attempt)
        out.write(json.dumps(row) + "\n")
        out.flush()

    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        x0 = rng.uniform(0, 1, N)
        pats = make_patterns(rng)
        ks = (2, 4, 8)

        def order_pair(fmap, unforced, a_fixed=None):
            res = {}
            for name, sch in (("easy_hard", EASY_HARD), ("hard_easy", HARD_EASY)):
                lab, hist, a_end = run_protocol(x0, pats, sch, fmap, unforced, a_fixed)
                aris, ret = score(lab, pats, ks)
                res[name] = {"retention": ret, "ari": aris,
                             "n_clusters": int(len(np.unique(lab))),
                             "a_unforced": a_end,
                             "site_var_last500": float(hist[-500:].var(axis=0).mean())}
            res["diff"] = res["easy_hard"]["retention"] - res["hard_easy"]["retention"]
            return res

        c = time.process_time()
        emit({"arm": "TREATMENT", "seed": seed, **order_pair(f_log, UNFORCED)})
        emit({"arm": "CONTROL", "seed": seed, "a_fixed": 3.8,
              **order_pair(f_log, UNFORCED, a_fixed=3.8)})
        cal, raw = calibrate(seed)
        null_map = Affine(cal, np.random.default_rng(10_000 + seed))
        emit({"arm": "NULL_TWIN", "seed": seed, "calibration": raw,
              **order_pair(null_map, UNFORCED)})
        # positive control: single k=2 pattern at a=3.7
        lab, _, _ = run_protocol(x0, pats, [(2, 3.7)], f_log, UNFORCED)
        emit({"arm": "POSITIVE_CONTROL", "seed": seed,
              "ari": float(adjusted_rand_score(pats[2], lab)),
              "n_clusters": int(len(np.unique(lab)))})
        # cheat: real hard->easy, injected easy->hard
        lab_he, _, _ = run_protocol(x0, pats, HARD_EASY, f_log, UNFORCED)
        _, ret_he = score(lab_he, pats, ks)
        aris_cheat = {str(k): float(adjusted_rand_score(pats[k], pats[k])) for k in ks}
        ret_eh = float(np.mean(list(aris_cheat.values())))
        emit({"arm": "CHEAT", "seed": seed,
              "easy_hard": {"retention": ret_eh, "ari": aris_cheat, "injected": True},
              "hard_easy": {"retention": ret_he},
              "diff": ret_eh - ret_he})
        emit({"arm": "TRANSIENT_CHECK", "seed": seed, "unforced_steps": UNFORCED_LONG,
              **order_pair(f_log, UNFORCED_LONG)})
        area, q = loop_area(x0)
        emit({"arm": "LOOP", "seed": seed, "loop_area": area,
              "q_up": q["up"], "q_down": q["down"],
              "cpu_seconds_seed": time.process_time() - c})

    cpu = time.process_time() - t0
    emit({"arm": "META", "cpu_seconds": cpu,
          "cumulative_cpu_seconds": prior_cpu + cpu})
    out.close()
    print(f"done attempt {attempt}, cpu {cpu:.1f}s, cumulative {prior_cpu + cpu:.1f}s")


if __name__ == "__main__":
    main()
