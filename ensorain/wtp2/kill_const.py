"""Post-hoc kill test (declared in PREREG s9 A8): is a positive's unseen-cell competence (CGu)
explained by ONE constant? CGu is scored against the zero predictor, so any organism that
learns a DC offset beats it. For each positive, replace organism 0's memory predictor with
  (a) the true global mean of the field (best constant a learner could know), and
  (b) the organism's own learned constant (mean of what it observed),
and compare CGu. A positive whose CGu <= the constant ceiling carries no structure beyond a scalar."""
import json
import os
import sys

import numpy as np

from ensorain.wtp import organism
from .world2 import build, run_life, streams

OUT = os.path.join(os.path.dirname(__file__), "..", "runs", "wtp02")


def const_life(g, seed, c):
    orig = organism.Memory.predict
    organism.Memory.predict = lambda self, cells: np.full(len(cells), c)
    try:
        return run_life(g, seed, freeze=True, no_marks=True)
    finally:
        organism.Memory.predict = orig


def audit(g, seed):
    x = build(g, streams(seed)[0], None, False)[0]
    real = run_life(g, seed, return_memory=True)
    mem = real.pop("_memory", None)
    learned = float(getattr(mem, "mean", np.nan)) if mem is not None else np.nan
    return dict(seed=seed, n_floats=real.get("n_floats"), CGu_org=real.get("CGu"),
                field_mean=float(x.mean()), learned_const=learned,
                CGu_true_mean=const_life(g, seed, float(x.mean())).get("CGu"),
                CGu_learned_const=const_life(g, seed, learned).get("CGu") if np.isfinite(learned) else None,
                CGu_zero=const_life(g, seed, 0.0).get("CGu"))


def main(n_seeds=5):
    rows = {r["genome_hash"]: r for r in json.load(open(os.path.join(OUT, "waveA.json")))}
    summ = json.load(open(os.path.join(OUT, "waveA_summary.json")))
    hs = [p["h"] for p in summ["positives"]]
    out = []
    for h in hs:
        r = rows[h]
        res = [audit(r["genome"], r["seed"] + 1000 * k) for k in range(n_seeds)]
        org = np.array([x["CGu_org"] if x["CGu_org"] is not None else np.nan for x in res], float)
        tm = np.array([x["CGu_true_mean"] if x["CGu_true_mean"] is not None else np.nan for x in res], float)
        lc = np.array([x["CGu_learned_const"] if x["CGu_learned_const"] is not None else np.nan for x in res], float)
        exceed = org - np.fmax(tm, lc)
        verdict = "SCALAR-EXPLAINED" if np.nanmedian(exceed) < 0.10 else "EXCEEDS-CONSTANT"
        out.append(dict(h=h, substrate=r["genome"]["memory"]["substrate"], n_floats=res[0]["n_floats"],
                        median_CGu_org=float(np.nanmedian(org)), median_CGu_true_mean=float(np.nanmedian(tm)),
                        median_CGu_learned_const=float(np.nanmedian(lc)),
                        median_excess_over_best_constant=float(np.nanmedian(exceed)), verdict=verdict, seeds=res))
        print(h, out[-1]["substrate"], "nf", out[-1]["n_floats"], "org", round(out[-1]["median_CGu_org"], 3),
              "true_mean", round(out[-1]["median_CGu_true_mean"], 3), "learned_c",
              round(out[-1]["median_CGu_learned_const"], 3), "excess", round(out[-1]["median_excess_over_best_constant"], 3),
              verdict, flush=True)
    json.dump(out, open(os.path.join(OUT, "kill_const.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)


def recombinant9(seeds=range(8_710_000, 8_710_005)):
    """A8 on Wave F recombinant #9 (D2 jump): does the jump survive replacing the learner by its own constant?"""
    from .detect2 import jump
    g = json.load(open(os.path.join(OUT, "waveF_i9_genome.json")))
    out = []
    for s in seeds:
        r = run_life(g, s, return_memory=True)
        m = r.pop("_memory")
        c = const_life(g, s, float(m.mean))
        out.append(dict(seed=s, n_floats=r["n_floats"], learned_const=float(m.mean), CGu=r["CGu"],
                        trace=[t["ACu"] - t["ACu0"] for t in r["trace"] if t.get("ACu") is not None],
                        jump_org=jump(r), jump_const=jump(c), CGu_const=c.get("CGu")))
    json.dump(out, open(os.path.join(OUT, "kill_const_f9.json"), "w"), indent=1, default=float)
    print("F9 jump fires org", sum(o["jump_org"][1] for o in out), "/5; const", sum(o["jump_const"][1] for o in out), "/5")
