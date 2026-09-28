"""Freeze reduced-model predictions for every condition (before any engine run)."""
import dataclasses
import json
import time

import conditions as C
import echo_model as em

if __name__ == "__main__":
    t0 = time.time()
    out = {}
    for cond, name, ph, env, g, prog in C.conditions():
        key = f"{cond}:{name}"
        rec = {"kernel": {int(k): round(float(v), 4) for k, v in em.kernel(ph, prog).items()},
               "sat": {}, "nosat": {}}
        for gap in C.GAPS:
            e = dataclasses.replace(env, gap=gap)
            rec["sat"][gap] = em.predict(ph, e, prog, nw=4000, seed=gap, sat=True)
            rec["nosat"][gap] = em.predict(ph, e, prog, nw=4000, seed=gap, sat=False)
        out[key] = rec
        print(key, " ".join(f"{gp}:{rec['sat'][gp]:.2f}" for gp in C.GAPS), flush=True)
    out["_wall_s"] = time.time() - t0
    (C.HERE / "out").mkdir(exist_ok=True)
    (C.HERE / "out" / "predictions.json").write_text(json.dumps(out, indent=1))
