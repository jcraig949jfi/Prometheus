"""PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only. Usage: python pilot.py <attempt>"""
import sys, json, time
import common as K
import arms

attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
params = {"D": K.D, "N": K.N, "H": K.H, "R": K.R, "C": K.C, "LAMS": K.LAMS, "TOLS": K.TOLS,
          "LAZY": K.LAZY, "attempt": attempt}
t0 = time.process_time()
with open("pilot_rows.jsonl", "w") as f:
    for s in K.SEEDS:
        w = K.make_world(s)
        mix = K.mixing_dist(w["P"])
        pc = arms.positive_control(w)
        nt, ch = arms.null_twin_and_cheat(w)
        for arm, conds in (("POSITIVE_CONTROL", pc), ("NULL_TWIN", nt), ("CHEAT", ch)):
            f.write(json.dumps({"arm": arm, "seed": s, "params": params, "mixing_dist_P20": mix,
                                "conds": conds}) + "\n")
            f.flush()
cpu = time.process_time() - t0
with open("pilot_cpu.json", "w") as f:
    json.dump({"attempt": attempt, "cpu_seconds": cpu}, f)
print("cpu_s", round(cpu, 2))
