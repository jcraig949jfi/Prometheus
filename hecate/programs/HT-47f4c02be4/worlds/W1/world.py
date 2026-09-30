"""PHASE 2: TREATMENT (real stream, cost sweep), CONTROL (depth 0), and the
three pilot arms rerun through the same code path. Rows -> rows.jsonl."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import run_agent, self_check, SILENT, PRIME, COMPOSITE
from eval_common import mertens
from pilot import pc_stream, twin_stream, N, KMAX

HERE = os.path.dirname(os.path.abspath(__file__))
COSTS = [0.001, 0.003, 0.01, 0.03, 0.1]


def real_stream(N):
    lab = np.full(N + 1, PRIME, dtype=np.int8)
    for p in range(2, int(N ** 0.5) + 1):
        if lab[p] == PRIME:
            lab[p * p::p] = COMPOSITE
    return lab


def cost_block(r):
    cost = {str(c): [c * K + r[K] for K in range(KMAX + 1)] for c in COSTS}
    kstar = {str(c): int(np.argmin(cost[str(c)])) for c in COSTS}
    return cost, kstar


def main():
    t0 = time.process_time()
    self_check(real_stream)
    params = dict(N=N, KMAX=KMAX, costs=COSTS)
    out = open(os.path.join(HERE, "rows.jsonl"), "w", encoding="utf-8")

    def emit(row):
        out.write(json.dumps(row) + "\n"); out.flush()

    for seed in range(5):
        lab = real_stream(N)
        r, periods, _ = run_agent(lab, N, KMAX)
        cost, kstar = cost_block(r)
        emit(dict(arm="TREATMENT", seed=seed, params=params, r_by_K=r,
                  periods=periods, depth_final=len(periods),
                  cost_per_step=cost, K_star=kstar))
        emit(dict(arm="CONTROL", seed=seed, params=params, r0=r[0],
                  cost_per_step={str(c): r[0] for c in COSTS}))
    for seed in range(5):
        lab = pc_stream(N)
        r, periods, m = run_agent(lab, N, KMAX)
        lab2 = lab[2:N + 1]
        after = np.arange(2, N + 1) > 7
        fires = m < KMAX
        resid = (lab2 != SILENT) & ((~fires) | (fires & (lab2 != COMPOSITE)))
        emit(dict(arm="POSITIVE_CONTROL", seed=seed, params=params, r_by_K=r,
                  periods=periods, depth_final=len(periods),
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
        cost, kstar = cost_block(r)
        emit(dict(arm="NULL_TWIN", seed=seed, params=params, r_by_K=r,
                  periods=periods, depth_final=len(periods),
                  ratio_20_0=r[20] / r[0], K_star=kstar))
    out.close()
    json.dump({"cpu_seconds": time.process_time() - t0},
              open(os.path.join(HERE, "world_cpu.json"), "w"))


if __name__ == "__main__":
    main()
