"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only. No treatment arm."""
import json, sys, time
import numpy as np
import sim

SEEDS = list(range(10))
ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
out = f"pilot_rows.jsonl" if ATTEMPT == 1 else f"pilot_rows_attempt{ATTEMPT}.jsonl"

with open(out, "w") as f:
    for s in SEEDS:
        t0 = time.process_time()
        A, gh, gv, anomA = sim.phase_a(s)
        tA = time.process_time() - t0
        base = {"seed": s, "attempt": ATTEMPT, "params": sim.PARAMS,
                "phaseA_anomalies": anomA, "phaseA_amap_std": float(A.std()),
                "learned_g": sim.gstats(gh, gv), "phaseA_cpu_s": tA}
        # POSITIVE_CONTROL
        t0 = time.process_time()
        ch, cv = sim.carved_graph(A)
        B, anom = sim.phase_b(ch, cv, s)
        r, degen = sim.pearson_z(A, B)
        f.write(json.dumps({**base, "arm": "POSITIVE_CONTROL", "r": r, "degenerate": degen,
                            "phaseB_anomalies": anom, "graph": sim.gstats(ch, cv),
                            "cpu_s": time.process_time() - t0}) + "\n"); f.flush()
        # NULL_TWIN
        t0 = time.process_time()
        ph, pv = sim.permuted_graph(gh, gv, s)
        B, anom = sim.phase_b(ph, pv, s)
        r, degen = sim.pearson_z(A, B)
        f.write(json.dumps({**base, "arm": "NULL_TWIN", "r": r, "degenerate": degen,
                            "phaseB_anomalies": anom, "graph": sim.gstats(ph, pv),
                            "cpu_s": time.process_time() - t0}) + "\n"); f.flush()
        # CHEAT: success injected directly into the observable
        r, degen = sim.pearson_z(A, A.copy())
        f.write(json.dumps({**base, "arm": "CHEAT", "r": r, "degenerate": degen,
                            "cpu_s": 0.0}) + "\n"); f.flush()
        print(s, "done", flush=True)
