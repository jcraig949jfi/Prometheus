"""X-H1-TRANSPLANT (EXPLORE, TRANSPLANT; child of C9-H1R). Declared before running.

C9-H1R (confirmatory): on H1's fixed task (ADD1), gating the answer on cue consumption
abolishes competence when reading the cue costs instructions (I = +0.20) and is harmless when
the cue is free. Does that interaction TRANSPLANT to other tasks?

Single coordinate (task_transform), everything else exactly C9-H1R's repaired design (same
cell otherwise, same four arms, tier S, the repaired runner). Transforms: XOR1, XOR15, XOR5A
(atomic), ADD37. 30 fresh seeds each (9_130_000 + 1000*t + s).
Readout per transform: H1's M and I (hypotheses.h1).
Classification: SIGNAL (transplants) if I >= 0.15 with the same sign in >= 3 of 4 transforms;
CLEAN_NULL if |I| < 0.15 in all four; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
C9 = ROOT.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
sys.path.insert(0, str(ROOT / "c9_h1r"))
TRANSFORMS = ("XOR1", "XOR15", "XOR5A", "ADD37")


def job(a):
    import run_h1r
    R = run_h1r.repaired_runner()
    s = R(a["cell"], a["seed"], tier=a["tier"], **a["kwargs"]).run()
    return {"t": a["t"], "seed": a["seed"], "arm": a["arm"], "held_max_final": s["held_max_final"],
            "crossed_ever": s["crossed_ever"], "crossed_at_final": s["crossed_at_final"]}


def main():
    import manifest as M
    import hypotheses as HY
    base = M.h1_bundles(1)[0]
    arms = []
    for ti, t in enumerate(TRANSFORMS):
        for s in range(30):
            for a in base["arms"]:
                arms.append(dict(a, t=t, cell=dict(a["cell"], task_transform=t), seed=9_130_000 + 1000 * ti + s))
    with mp.Pool(6, maxtasksperchild=8) as pool:
        res = pool.map(job, arms)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    per = {}
    for t in TRANSFORMS:
        by = {}
        for r in res:
            if r["t"] == t:
                by.setdefault(r["seed"], {})[r["arm"]] = r
        per[t] = HY.h1([{"results": v} for v in by.values()])
    Is = [per[t]["I"] for t in TRANSFORMS]
    pos = sum(1 for i in Is if i >= 0.15)
    neg = sum(1 for i in Is if i <= -0.15)
    cls = "SIGNAL" if max(pos, neg) >= 3 else ("CLEAN_NULL" if all(abs(i) < 0.15 for i in Is) else "WEAK_SIGNAL")
    out = {"classification": cls, "per_transform": {t: {k: per[t][k] for k in ("verdict", "M", "I", "means_held_final")}
                                                    for t in TRANSFORMS}}
    (HERE / "SUMMARY.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
