"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN on the linear OU substrate.
No treatment code. Usage: python pilot.py <attempt>"""
import sys, os, time
from common import *  # noqa

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
OUT = os.path.join(HERE, "pilot_rows.jsonl" if ATTEMPT == 1 else f"pilot_rows_attempt{ATTEMPT}.jsonl")


def run_pilot_arms(seeds=SEEDS, out_path=OUT, attempt=ATTEMPT, tag="pilot"):
    acc = {arm: {s: {"spearman": {}, "imag": {}} for s in seeds}
           for arm in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT", "CHEAT_NULL")}
    for di, d in enumerate(DISTANCES):
        systems = [ou_J(s, d) for s in seeds]
        rngs = [np.random.default_rng([s, di, 202]) for s in seeds]
        X = simulate_ou([J for J, _ in systems], rngs)
        for si, s in enumerate(seeds):
            J, xs = systems[si]
            true = true_press_responses(J, xs)
            Jh, im = estimate_J(X[:, si, :])
            acc["POSITIVE_CONTROL"][s]["spearman"][str(d)] = press_spearmans(predict_responses(Jh, xs), true)
            acc["POSITIVE_CONTROL"][s]["imag"][str(d)] = im
            Xn = circular_shift(X[:, si, :], np.random.default_rng([s, di, 303]))
            Jn, imn = estimate_J(Xn)
            acc["NULL_TWIN"][s]["spearman"][str(d)] = press_spearmans(predict_responses(Jn, xs), true)
            acc["NULL_TWIN"][s]["imag"][str(d)] = imn
            if d == -0.01:
                perm = np.random.default_rng([s, 404]).permutation(N_SP)
                cheat_pred = true[perm, :]
            else:
                cheat_pred = true.copy()
            acc["CHEAT"][s]["spearman"][str(d)] = press_spearmans(cheat_pred, true)
            acc["CHEAT"][s]["imag"][str(d)] = 0.0
            if attempt >= 2:  # repair: injected at-chance null for the cheat
                pr = np.random.default_rng([s, di, 405])
                cn = np.stack([true[pr.permutation(N_SP), k] for k in range(N_SP)], axis=1)
                acc["CHEAT_NULL"][s]["spearman"][str(d)] = press_spearmans(cn, true)
                acc["CHEAT_NULL"][s]["imag"][str(d)] = 0.0
        del X
    params = {"N_SP": N_SP, "DT": DT, "N_OBS": N_OBS, "TAU": TAU, "DISTANCES": DISTANCES,
              "PRESS": PRESS, "OU_SIGMA": OU_SIGMA, "substrate": "linear OU, J=diag(x*)A shifted"}
    for arm, d in acc.items():
        if arm == "CHEAT_NULL" and attempt < 2:
            continue
        for s in seeds:
            append_row(out_path, {"tag": tag, "attempt": attempt, "arm": arm, "seed": s,
                                  "spearman": d[s]["spearman"], "logm_max_imag": d[s]["imag"],
                                  "params": params})


if __name__ == "__main__":
    t0c, t0w = time.process_time(), time.time()
    if os.path.exists(OUT):
        raise SystemExit(f"{OUT} exists; refusing to overwrite")
    run_pilot_arms()
    print(log_cpu("pilot.py", t0c, t0w, {"attempt": ATTEMPT}))
