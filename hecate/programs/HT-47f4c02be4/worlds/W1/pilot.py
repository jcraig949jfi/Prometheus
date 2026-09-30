"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only (no treatment)."""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import run_agent, self_check, SILENT, PRIME, COMPOSITE
from eval_common import mertens

HERE = os.path.dirname(os.path.abspath(__file__))
N, KMAX = 100000, 40
ATTEMPT = int(os.environ.get("PILOT_ATTEMPT", "1"))
PC_SOURCES = [2, 3, 5, 7]


def pc_stream(N):
    lab = np.full(N + 1, SILENT, dtype=np.int8)
    for p in PC_SOURCES:
        lab[p::p] = COMPOSITE
    for p in PC_SOURCES:
        lab[p] = PRIME
    return lab


def twin_stream(N, seed):
    rng = np.random.default_rng(seed)
    lab = np.full(N + 1, COMPOSITE, dtype=np.int8)
    n = np.arange(3, N + 1)
    u = rng.random(n.size)
    lab[3:][u < 1 / np.log(n)] = PRIME
    lab[2] = PRIME
    return lab


def main():
    t0 = time.process_time()
    self_check(pc_stream)
    self_check(lambda n: twin_stream(n, 12345))
    params = dict(N=N, KMAX=KMAX, attempt=ATTEMPT)
    out = open(os.path.join(HERE, "pilot_rows.jsonl"), "w", encoding="utf-8")

    def emit(row):
        out.write(json.dumps(row) + "\n"); out.flush()

    for seed in range(5):
        lab = pc_stream(N)
        r, periods, m = run_agent(lab, N, KMAX)
        lab2 = lab[2:N + 1]
        after = np.arange(2, N + 1) > 7
        fires = m < KMAX
        resid = (lab2 != SILENT) & ((~fires) | (fires & (lab2 != COMPOSITE)))
        emit(dict(arm="POSITIVE_CONTROL", seed=seed, params=params,
                  r_by_K=r, periods=periods, depth_final=len(periods),
                  residual_after_4th_promotion=int((resid & after).sum())))
    for seed in range(5):
        rng = np.random.default_rng(1000 + seed)
        eps = rng.uniform(-0.01, 0.01, KMAX + 1)
        r = [1.0] + [mertens(K) * (1 + eps[K]) for K in range(1, KMAX + 1)]
        emit(dict(arm="CHEAT", seed=seed, params=params, r_by_K=r,
                  injected=True, twin_ratio_injected=1.0))
    for seed in range(10):
        lab = twin_stream(N, seed)
        r, periods, _ = run_agent(lab, N, KMAX)
        emit(dict(arm="NULL_TWIN", seed=seed, params=params, r_by_K=r,
                  periods=periods, depth_final=len(periods),
                  twin_prime_count=int((lab[2:] == PRIME).sum()),
                  ratio_20_0=r[20] / r[0]))
    out.close()
    with open(os.path.join(HERE, "pilot_cpu.json"), "w") as f:
        json.dump({"attempt": ATTEMPT, "cpu_seconds": time.process_time() - t0}, f)


if __name__ == "__main__":
    main()
