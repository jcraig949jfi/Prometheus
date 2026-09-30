"""PHASE 2: TREATMENT + CONTROL arms, plus the three pilot arms rerun in the same code path."""
import json, time
import common as K
import arms

params = {"D": K.D, "N": K.N, "H": K.H, "R": K.R, "C": K.C, "LAMS": K.LAMS, "TOLS": K.TOLS,
          "LAZY": K.LAZY, "tanh": "centred (attempt-2 repair)"}
t0 = time.process_time()
with open("rows.jsonl", "w") as f:
    for s in K.SEEDS:
        w = K.make_world(s)
        mix = K.mixing_dist(w["P"])
        tr, ct = [], []
        for c in K.C:
            for r in K.R:
                q = K.make_q(w, r, c)
                for lam in K.LAMS:
                    m, _ = K.measure(q, w["P"], lam)
                    base = {"r": r, "c": c, "lam": lam}
                    tr.append({**base, "z": m["z"], "V": m["V"], "tanh": m["tanh"], "zdiag": m["zdiag"]})
                    ct.append({**base, "tanh": m["tanh"], "quant": m["quant"], "V": m["V"]})
        pc = arms.positive_control(w)
        nt, ch = arms.null_twin_and_cheat(w)
        for arm, conds in (("TREATMENT", tr), ("CONTROL", ct), ("POSITIVE_CONTROL", pc),
                           ("NULL_TWIN", nt), ("CHEAT", ch)):
            f.write(json.dumps({"arm": arm, "seed": s, "params": params, "mixing_dist_P20": mix,
                                "conds": conds}) + "\n")
            f.flush()
json.dump({"cpu_seconds": time.process_time() - t0}, open("world_cpu.json", "w"))
print("cpu_s", round(time.process_time() - t0, 2))
