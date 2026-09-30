"""W6 probe world: TREATMENT (Hebbian-written medium), TREATMENT_TWIN(_B), CONTROL (FIXED),
plus POSITIVE_CONTROL, NULL_TWIN, NULL_TWIN_B, CHEAT re-run in the same loop through the
frozen ../controls.py functions. Writes rows.jsonl (one row per arm x seed, flushed) and
run_meta.json. See NOTES.md."""
import importlib.util
import json
import os
import sys
import time

sys.dont_write_bytecode = True
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("w6_controls", os.path.join(WORLD, "controls.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

SPEC = json.load(open(os.path.join(WORLD, "spec.json")))
SEEDS = list(SPEC["seeds"])
T_A = 3000          # Phase A (plastic)
ETA, LAM = 0.1, 0.1
G_MIN, G_MAX = 0.1, 5.0
assert (C.N, C.MU, C.D0, C.DH, C.DT, C.T_SETTLE, C.T_REGROW, C.L, C.LES_NOISE) == \
    (48, 2.0, 0.5, 10.0, 0.02, 1500, 3000, 24, 0.3)


def hebb_run(a, h, gh, gv, n):
    """Simultaneous explicit Euler: g and (a,h) updates both use the state at time t."""
    for _ in range(n):
        m2 = a.mean() ** 2
        ph = a * np.roll(a, -1, 1) / m2
        pv = a * np.roll(a, -1, 0) / m2
        gh_n = np.clip(gh + C.DT * (ETA * (ph - 1.0) - LAM * (gh - 1.0)), G_MIN, G_MAX)
        gv_n = np.clip(gv + C.DT * (ETA * (pv - 1.0) - LAM * (gv - 1.0)), G_MIN, G_MAX)
        a, h = C.step(a, h, gh, gv)
        gh, gv = gh_n, gv_n
    return a, h, gh, gv


def gstats(gh, gv, mask):
    inh = mask & np.roll(mask, -1, 1)
    inv = mask & np.roll(mask, -1, 0)
    allg = np.concatenate([gh.ravel(), gv.ravel()])
    ing = np.concatenate([gh[inh], gv[inv]])
    return {"g_mean": float(allg.mean()), "g_std": float(allg.std()),
            "g_frac_at_min": float((allg <= G_MIN + 1e-12).mean()),
            "g_frac_at_max": float((allg >= G_MAX - 1e-12).mean()),
            "g_in_lesion_mean": float(ing.mean()), "g_in_lesion_std": float(ing.std())}


def main():
    out = os.path.join(HERE, "rows.jsonl")
    ones = np.ones((C.N, C.N))
    params = {"eta": ETA, "lambda": LAM, "clip": [G_MIN, G_MAX], "T_A": T_A,
              "T_settle": C.T_SETTLE, "T_regrow": C.T_REGROW, "L": C.L, "lesion_noise": C.LES_NOISE,
              "mu": C.MU, "D0": C.D0, "Dh": C.DH, "dt": C.DT, "N": C.N, "g_across_pc": C.G_ACROSS}
    t0 = time.process_time()
    with open(out, "w") as f:
        def emit(row):
            row.update({"world": "W6", "params": params})
            f.write(json.dumps(row) + "\n")
            f.flush()
        for s in SEEDS:
            ts = time.process_time()
            # ---- controls: identical sequence to controls.main ----
            r0 = C.rng_for(s, 0)
            a0 = 1 + 0.01 * r0.standard_normal((C.N, C.N))
            h0 = 1 + 0.01 * r0.standard_normal((C.N, C.N))
            a_ref, h_ref = C.run(a0, h0, ones, ones, C.T_REF)
            mask = C.lesion_mask(s)
            aO, hO = C.run(a_ref, h_ref, ones, ones, C.T_SETTLE)
            al, hl = C.lesion(aO, hO, mask, s)
            aR, _ = C.run(al, hl, ones, ones, C.T_REGROW)
            emit({"seed": s, "arm": "FIXED", "role": "CONTROL", **C.score(aO, aR, mask)})
            gh, gv = C.carve(a_ref)
            aO, hO = C.run(a_ref, h_ref, gh, gv, C.T_SETTLE)
            al, hl = C.lesion(aO, hO, mask, s)
            aR, _ = C.run(al, hl, gh, gv, C.T_REGROW)
            emit({"seed": s, "arm": "POSITIVE_CONTROL", "role": "POSITIVE_CONTROL", **C.score(aO, aR, mask),
                  "frac_cut_edges": float(((gh < 1).sum() + (gv < 1).sum()) / (2 * C.N * C.N))})
            gh2, gv2 = C.scramble_inside(gh, gv, mask, s, 3)
            aT, _ = C.run(al, hl, gh2, gv2, C.T_REGROW)
            emit({"seed": s, "arm": "NULL_TWIN", "role": "NULL_TWIN (of positive control)", **C.score(aO, aT, mask)})
            gh3, gv3 = C.scramble_inside(gh, gv, mask, s, 4)
            aT2, _ = C.run(al, hl, gh3, gv3, C.T_REGROW)
            emit({"seed": s, "arm": "NULL_TWIN_B", "role": "twin-in-arm-slot for controls", **C.score(aO, aT2, mask)})
            aC = aT.copy()
            aC[mask] = aO[mask]
            emit({"seed": s, "arm": "CHEAT", "role": "CHEAT", **C.score(aO, aC, mask)})
            # ---- treatment ----
            r0 = C.rng_for(s, 0)
            a0 = 1 + 0.01 * r0.standard_normal((C.N, C.N))
            h0 = 1 + 0.01 * r0.standard_normal((C.N, C.N))
            aA, hA, lgh, lgv = hebb_run(a0, h0, ones.copy(), ones.copy(), T_A)
            aO, hO = C.run(aA, hA, lgh, lgv, C.T_SETTLE)
            al, hl = C.lesion(aO, hO, mask, s)
            aR, _ = C.run(al, hl, lgh, lgv, C.T_REGROW)
            gs = gstats(lgh, lgv, mask)
            emit({"seed": s, "arm": "TREATMENT", "role": "TREATMENT", **C.score(aO, aR, mask), **gs,
                  "O_mean": float(aO.mean()), "O_std": float(aO.std())})
            th, tv = C.scramble_inside(lgh, lgv, mask, s, 3)
            aT, _ = C.run(al, hl, th, tv, C.T_REGROW)
            emit({"seed": s, "arm": "TREATMENT_TWIN", "role": "NULL_TWIN (of treatment)", **C.score(aO, aT, mask)})
            th, tv = C.scramble_inside(lgh, lgv, mask, s, 4)
            aT2, _ = C.run(al, hl, th, tv, C.T_REGROW)
            emit({"seed": s, "arm": "TREATMENT_TWIN_B", "role": "twin-in-arm-slot for treatment twin",
                  **C.score(aO, aT2, mask), "cpu_s_seed": time.process_time() - ts})
            print("seed", s, "done", round(time.process_time() - ts, 2), file=sys.stderr)
    cpu = time.process_time() - t0
    json.dump({"cpu_s": cpu, "core_minutes": cpu / 60.0, "seeds": SEEDS, "attempt": 1,
               "numpy": np.__version__, "python": sys.version},
              open(os.path.join(HERE, "run_meta.json"), "w"), indent=1)
    print("cpu_s", cpu, file=sys.stderr)


if __name__ == "__main__":
    main()
