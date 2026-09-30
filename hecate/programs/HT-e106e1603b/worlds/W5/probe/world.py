"""W5 probe (HT-e106e1603b): TREATMENT (real min-sum iteration count) and
the frozen control arms re-run through controls.py's own code path.
See NOTES.md. Writes rows.jsonl (one row per (arm, seed), flushed) and
treatment_blocks_seed{k}.npz.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.path.insert(0, WORLD)
import controls as C  # noqa: E402  (frozen; main() is never called)

ROWS = os.path.join(HERE, "rows.jsonl")
ARMS = ("TREATMENT", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT")


def var_edge_index(cv):
    """For each variable, the flat edge indices (into M*DC) touching it."""
    flat = cv.reshape(-1)
    order = np.argsort(flat, kind="stable")
    idx = order.reshape(C.N, C.DV)
    assert np.all(flat[idx] == np.arange(C.N)[:, None])
    return idx


def min_sum_iterations(cv, e):
    """Flooding min-sum on hard received words e (blocks x N), all-zero
    codeword, fixed LLR magnitude 1. Returns t per block and a flag for
    zero-syndrome stops at a nonzero word."""
    B = e.shape[0]
    t = np.full(B, C.TMAX, dtype=np.int64)
    wrong_cw = np.zeros(B, dtype=bool)
    synd0 = e[:, cv].sum(axis=2) % 2
    t[synd0.sum(axis=1) == 0] = 0
    active = np.nonzero(synd0.sum(axis=1) != 0)[0]
    if active.size == 0:
        return t, wrong_cw
    vidx = var_edge_index(cv)
    llr = 1.0 - 2.0 * e[active].astype(np.float64)      # A x N
    recv = e[active].astype(np.uint8)
    Q = llr[:, cv]                                       # A x M x DC
    act = active
    for it in range(1, C.TMAX + 1):
        # check update
        mag = np.abs(Q)
        neg = Q < 0
        sgn_all = np.where(neg.sum(axis=2) % 2 == 1, -1.0, 1.0)  # A x M
        own = np.where(neg, -1.0, 1.0)
        sgn = sgn_all[:, :, None] * own
        amin = np.argmin(mag, axis=2)
        srt = np.partition(mag, 1, axis=2)
        m1, m2 = srt[:, :, 0], srt[:, :, 1]
        mex = np.broadcast_to(m1[:, :, None], mag.shape).copy()
        a_i, c_i = np.nonzero(np.ones(amin.shape, dtype=bool))
        mex[a_i, c_i, amin.reshape(-1)] = m2.reshape(-1)
        R = sgn * mex
        # variable update
        Rf = R.reshape(R.shape[0], -1)
        total = llr + Rf[:, vidx].sum(axis=2)            # A x N
        hard = np.where(total < 0, 1, np.where(total > 0, 0, recv)).astype(np.uint8)
        syn = hard[:, cv].sum(axis=2) % 2
        done = syn.sum(axis=1) == 0
        if done.any():
            t[act[done]] = it
            wrong_cw[act[done]] = hard[done].sum(axis=1) > 0
            keep = ~done
            act, llr, recv, R, total = act[keep], llr[keep], recv[keep], R[keep], total[keep]
            if act.size == 0:
                break
        Q = total[:, cv] - R
    return t, wrong_cw


def channel_with_e(cv, seed):
    """Identical RNG stream to controls.channel, also returning e."""
    rng = np.random.default_rng(20_000 + seed)
    p = rng.uniform(C.P_LO, C.P_HI, size=C.BLOCKS)
    e = (rng.random((C.BLOCKS, C.N)) < p[:, None]).astype(np.uint8)
    return p, e


def main():
    c0, w0 = time.process_time(), time.time()
    open(ROWS, "w").close()
    with open(ROWS, "a", encoding="utf-8") as fh:
        for seed in C.SEEDS:
            cv = C.make_graph(seed)
            p, w, s = C.channel(cv, seed)
            p2, e = channel_with_e(cv, seed)
            assert np.array_equal(p, p2) and np.array_equal(w, e.sum(axis=1).astype(float))
            for arm in ARMS:
                extra = {}
                if arm == "TREATMENT":
                    ts = time.process_time()
                    t, wrong = min_sum_iterations(cv, e)
                    t = t.astype(float)
                    extra = {"n_t0": int((t == 0).sum()), "n_cap": int((t == C.TMAX).sum()),
                             "n_wrong_codeword": int(wrong.sum()),
                             "decoder_cpu_s": time.process_time() - ts}
                    np.savez(os.path.join(HERE, f"treatment_blocks_seed{seed}.npz"),
                             p=p, w=w, s=s, t=t, wrong=wrong)
                else:
                    t = C.arm_t(arm, w, s, seed)
                g, mse_s, mse_st = C.g_statistic(w, s, t, seed)
                row = {"arm": arm, "seed": seed, "blocks": int(len(w)),
                       "G": g, "cvmse_s": mse_s, "cvmse_st": mse_st,
                       "mean_t": float(t.mean()), "sd_t": float(t.std()),
                       "mean_w": float(w.mean()), "mean_s": float(s.mean()),
                       "params": {"N": C.N, "TMAX": C.TMAX, "P": [C.P_LO, C.P_HI],
                                  "decoder": "flooding min-sum, LLR +-1, tie->received bit"
                                  if arm == "TREATMENT" else "controls.arm_t"}}
                row.update(extra)
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                print(arm, seed, round(g, 4), extra.get("decoder_cpu_s", ""), flush=True)
    with open(os.path.join(HERE, "world_cpu.json"), "w") as fh:
        json.dump({"cpu_seconds": time.process_time() - c0, "wall_seconds": time.time() - w0}, fh)


if __name__ == "__main__":
    sys.exit(main())
