"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only. Rows -> pilot_rows.jsonl.
Usage: python pilot.py <attempt>"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import core as K

HERE = os.path.dirname(os.path.abspath(__file__))


def rng(seed, arm, stream):
    return np.random.default_rng([seed, K.ARM_CODE[arm], stream])


def shared_series(seed):
    return K.training_series(np.random.default_rng([seed, 0, 0]))


def summarize_first(first):
    f = [v for v in first if v >= 0]
    return dict(n_success=len(f), median_first=float(np.median(f)) if f else None)


def run_positive(seed):
    xs, us = shared_series(seed)
    grid, extra = {K.POS_C: {}}, {}
    for p in K.POS_PS:
        orb, _ = K.find_upo(p)
        W, nrows = K.fit_controller(xs, us, orb, K.POS_C)
        s = K.simulate(orb, [W], [K.POS_C], rng(seed, "POSITIVE_CONTROL", p))
        grid[K.POS_C][p] = s["frac"][0]
        extra[p] = dict(nrows=nrows, mean_kick=s["mean_kick"][0], **summarize_first(s["first"][0]))
    return grid, extra


def run_shuffled_grid(seed, arm):
    xs, us = shared_series(seed)
    perm = rng(seed, arm, 999).permutation(len(xs))
    xs, us = xs[perm], us[perm]  # one time-shuffled copy per seed x arm
    grid, extra = {C: {} for C in K.CS}, {}
    for p in K.PS:
        orb, _ = K.find_upo(p)
        fits = [K.fit_controller(xs, us, orb, C) for C in K.CS]
        s = K.simulate(orb, [f[0] for f in fits], K.CS, rng(seed, arm, p))
        for i, C in enumerate(K.CS):
            grid[C][p] = s["frac"][i]
        extra[p] = dict(nrows_C8=fits[-1][1], mean_kick=s["mean_kick"],
                        n_success=[summarize_first(fr)["n_success"] for fr in s["first"]])
    return grid, extra


def run_cheat(seed):
    grid, twin, extra = {C: {} for C in K.CS}, {C: {} for C in K.CS}, {}
    for p in K.PS:
        orb, _ = K.find_upo(p)
        Ws = [np.zeros((p, C)) for C in K.CS] * 2
        inject = [p <= C for C in K.CS] + [False] * len(K.CS)
        s = K.simulate(orb, Ws, K.CS + K.CS, rng(seed, "CHEAT", p), inject=inject)
        for i, C in enumerate(K.CS):
            grid[C][p] = s["frac"][i]
            twin[C][p] = s["frac"][len(K.CS) + i]
        extra[p] = dict(uncontrolled_n_success=sum(summarize_first(fr)["n_success"]
                                                  for fr in s["first"][len(K.CS):]))
    return grid, twin, extra


def main():
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    path = os.path.join(HERE, "pilot_rows.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for seed in K.SEEDS:
            for arm in ("POSITIVE_CONTROL", "CHEAT", "NULL_TWIN"):
                t0 = time.process_time()
                row = dict(arm=arm, seed=seed, attempt=attempt, params=K.PARAMS)
                if arm == "POSITIVE_CONTROL":
                    row["grid"], row["extra"] = run_positive(seed)
                elif arm == "CHEAT":
                    row["grid"], row["twin_grid"], row["extra"] = run_cheat(seed)
                else:
                    row["grid"], row["extra"] = run_shuffled_grid(seed, arm)
                row["cpu_seconds"] = time.process_time() - t0
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                print(arm, seed, round(row["cpu_seconds"], 1), flush=True)


if __name__ == "__main__":
    main()
