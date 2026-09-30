"""HT-8a87057933 / W1 world: core-guided forgetting under plant switches.

See IMPLEMENTATION_NOTES.md for the spec -> code mapping. Writes rows.jsonl
(one row per (arm, seed)), flushed per row.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

P = dict(
    noise=0.05, miss=0.1, n_a=16, n_b=16, a_lo=-1.2, a_hi=1.2, b_lo=0.5, b_hi=2.0,
    window=40, sw_window=10, regime_len=200, n_switches=10, ref_amp=1.0,
    ref_half_period=25, tol=0.1, consec=10, censor=200, n_seeds=30, x0=0.0,
    mus_order="oldest_first", observable="run_start_step_min1",
)
A_GRID = np.linspace(P["a_lo"], P["a_hi"], P["n_a"])
B_GRID = np.linspace(P["b_lo"], P["b_hi"], P["n_b"])
MA = np.repeat(A_GRID, P["n_b"])  # model index = 16*i + j
MB = np.tile(B_GRID, P["n_a"])
NM = MA.size
ALL = (1 << NM) - 1
T_TOTAL = P["regime_len"] * (P["n_switches"] + 1)
SWITCHES = [P["regime_len"] * (k + 1) for k in range(P["n_switches"])]


def ref(t):
    return P["ref_amp"] if (t // P["ref_half_period"]) % 2 == 0 else -P["ref_amp"]


def to_mask(ok):
    return int.from_bytes(np.packbits(ok, bitorder="little").tobytes(), "little")


def inter(clauses):
    m = ALL
    for c in clauses:
        m &= c[1]
        if not m:
            return 0
    return m


def mus_by_deletion(clauses):
    """Deletion-based MUS over an UNSAT list of (t, mask); oldest-first order."""
    core = list(clauses)
    i = 0
    while i < len(core):
        trial = core[:i] + core[i + 1:]
        if inter(trial) == 0:
            core = trial
        else:
            i += 1
    return core


def core_guided_drop(window):
    """Repeat: extract MUS, drop its oldest clause, until SAT. Returns (new_window, dropped, cores)."""
    w = list(window)
    dropped, cores = [], []
    while inter(w) == 0:
        core = mus_by_deletion(w)
        cores.append(core)
        oldest = min(core, key=lambda c: c[0])
        w.remove(oldest)
        dropped.append(oldest)
    return w, dropped, cores


def generate_env(seed):
    rng = np.random.default_rng([seed, 1])
    models = [int(rng.integers(NM))]
    for _ in range(P["n_switches"]):
        m = int(rng.integers(NM - 1))
        if m >= models[-1]:
            m += 1
        models.append(m)
    noise = rng.uniform(-P["noise"], P["noise"], size=T_TOTAL)
    return models, noise


def jaccard_turnover(c1, c2):
    s1, s2 = {c[0] for c in c1}, {c[0] for c in c2}
    u = s1 | s2
    return 1.0 - len(s1 & s2) / len(u) if u else 0.0


def run(arm, seed):
    models, noise = generate_env(seed)
    drop_rng = np.random.default_rng([seed, 2])
    cap = P["sw_window"] if arm == "CONTROL_SW10" else P["window"]
    window = []
    x = P["x0"]
    xs = [x]
    poles = []
    n_unsat = 0
    k_total = 0
    extra_total = 0
    core_sizes, turnovers, preswitch_frac = [], [], []
    prev_core = None
    for t in range(T_TOTAL):
        regime = t // P["regime_len"]
        t_regime_start = regime * P["regime_len"]
        if arm == "POSITIVE_CONTROL" and t in SWITCHES:
            window = []
        m = inter(window) if window else ALL
        idx = (m & -m).bit_length() - 1
        ah, bh = MA[idx], MB[idx]
        a, b = MA[models[regime]], MB[models[regime]]
        u = (ref(t + 1) - ah * x) / bh
        xn = a * x + b * u + noise[t]
        poles.append(a - b * ah / bh)
        ok = np.abs(MA * x + MB * u - xn) <= P["miss"]
        window.append((t, to_mask(ok)))
        if len(window) > cap:
            window.pop(0)
        if inter(window) == 0:
            n_unsat += 1
            if arm in ("TREATMENT", "CHEAT"):
                window, dropped, cores = core_guided_drop(window)
                k = len(dropped)
                extra = 0
            else:
                _, dropped_cg, cores = core_guided_drop(window)
                k = len(dropped_cg)
                dropped = []
                extra = 0
                if arm in ("CONTROL", "POSITIVE_CONTROL", "CONTROL_SW10"):
                    if arm == "CONTROL":
                        dropped, window = window[:k], window[k:]
                    while inter(window) == 0:
                        dropped.append(window.pop(0))
                        extra += 1
                    if arm == "CONTROL":
                        extra = len(dropped) - k
                    else:
                        k = 0
                elif arm == "NULL_TWIN":
                    kk = k
                    while True:
                        kk = min(kk, len(window))
                        pick = set(drop_rng.choice(len(window), size=kk, replace=False).tolist())
                        dropped += [c for i, c in enumerate(window) if i in pick]
                        window = [c for i, c in enumerate(window) if i not in pick]
                        if inter(window) != 0:
                            break
                        _, d2, _ = core_guided_drop(window)
                        kk = len(d2)
                        extra += kk
            k_total += k
            extra_total += extra
            core = cores[0]
            core_sizes.append(len(core))
            if prev_core is not None:
                turnovers.append(jaccard_turnover(prev_core, core))
            prev_core = core
            if dropped:
                preswitch_frac.append(sum(1 for c in dropped if c[0] < t_regime_start) / len(dropped))
        x = xn
        xs.append(x)
    # observable
    rec, pole_frac = [], []
    for ts in SWITCHES:
        good_run = 0
        r_time = P["censor"]
        for s in range(1, P["regime_len"] + 1):
            tt = ts + s
            if tt >= len(xs):
                break
            if abs(xs[tt] - ref(tt)) < P["tol"]:
                good_run += 1
                if good_run >= P["consec"]:
                    r_time = s - P["consec"] + 1  # repair (attempt 2): step the run BEGINS
                    break
            else:
                good_run = 0
        rec.append(r_time)
        seg = poles[ts:ts + r_time + P["consec"] - 1]
        pole_frac.append(float(np.mean(np.abs(seg) < 1.0)) if seg else None)
    true_rec = list(rec)
    if arm == "CHEAT":
        rec = [1] * len(rec)  # success injected directly into the observable
    return dict(
        arm=arm, seed=seed, params=P, plant_models=models, switch_times=SWITCHES,
        recovery_times=rec, recovery_times_mechanism=true_rec,
        cheat_injected=(arm == "CHEAT"),
        n_unsat_events=n_unsat, k_core_guided_total=k_total, extra_drops_total=extra_total,
        mean_core_size=float(np.mean(core_sizes)) if core_sizes else None,
        mean_core_turnover=float(np.mean(turnovers)) if turnovers else None,
        mean_preswitch_fraction_dropped=float(np.mean(preswitch_frac)) if preswitch_frac else None,
        recovery_pole_stable_fraction=pole_frac,
        max_abs_x=float(np.max(np.abs(xs))),
    )


def main():
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    arms = ["TREATMENT", "CONTROL", "CONTROL_SW10", "NULL_TWIN", "POSITIVE_CONTROL", "CHEAT"]
    c0 = time.process_time()
    with open(ROWS, "w", encoding="utf-8") as f:
        for arm in arms:
            for seed in range(P["n_seeds"]):
                r0 = time.process_time()
                row = run(arm, seed)
                row["attempt"] = attempt
                row["cpu_seconds"] = time.process_time() - r0
                f.write(json.dumps(row) + "\n")
                f.flush()
            print(arm, "done", round(time.process_time() - c0, 1), "cpu s", flush=True)
    with open(os.path.join(HERE, "world_cpu.json"), "w", encoding="utf-8") as f:
        json.dump({"attempt": attempt, "cpu_seconds": time.process_time() - c0}, f)


if __name__ == "__main__":
    main()
