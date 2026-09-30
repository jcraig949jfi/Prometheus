"""W6 probe round 3 (HT-55162c0ac0): TREATMENT, CONTROL and rerun controls.

Imports the frozen controls.py so every arm uses the same code path.
Does NOT call controls.main (it would overwrite the frozen control_rows.jsonl).
Rows -> probe/rows.jsonl, one per (arm, seed), flushed per row.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import controls as C  # frozen

OUT = os.path.join(HERE, "rows.jsonl")
EPS_G_TREAT = 0.05   # spec.mechanism eps_g
SEEDS = list(C.SEEDS)
assert SEEDS == list(range(10))
assert C.EPS_G_TWIN == EPS_G_TREAT


def params(extra=None):
    p = {"N": C.N, "G": C.G, "KAPPA": C.KAPPA, "DELTA": C.DELTA, "TAU": C.TAU,
         "K": C.K, "SPACING": C.SPACING, "BURN": C.BURN, "L": C.L}
    if extra:
        p.update(extra)
    return p


def main():
    t0 = time.process_time()
    f = open(OUT, "w", encoding="utf-8")

    def emit(r):
        f.write(json.dumps(r) + "\n"); f.flush()

    Pg = C.group_partners()
    # TREATMENT and CONTROL (correlation grouping on the same trajectory)
    for sd in SEEDS:
        r = C.run_arm("TREATMENT", sd, Pg, EPS_G_TREAT)
        r["params"] = params({"eps_g": EPS_G_TREAT, "partners": "group"})
        emit(r)
        c = {"arm": "CONTROL", "seed": sd, "eps_g": EPS_G_TREAT, "kappa": C.KAPPA,
             "readout": "correlation grouping on the TREATMENT trajectory",
             "partition_corr": r["partition_corr"], "ari_corr": r["ari_corr"],
             "corr_within_mean": r["corr_within_mean"], "corr_between_mean": r["corr_between_mean"],
             "params": r["params"]}
        emit(c)
    # controls, re-run exactly as controls.main defines them
    for sd in SEEDS:
        r = C.run_arm("POSITIVE_CONTROL", sd, Pg, C.EPS_G_PC)
        r["params"] = params({"eps_g": C.EPS_G_PC, "partners": "group"}); emit(r)
        ch = dict(r); ch["arm"] = "CHEAT"; ch["partition_ftle"] = C.LABELS.tolist()
        ch["ari_ftle"] = C.ari(C.LABELS, C.LABELS); emit(ch)
    for sd in SEEDS:
        Pr = C.random_partners(np.random.default_rng(500 + sd))
        r = C.run_arm("NULL_TWIN", sd, Pr, C.EPS_G_TWIN)
        r["params"] = params({"eps_g": C.EPS_G_TWIN, "partners": "random rng(500+seed)"}); emit(r)
    for sd in SEEDS:
        Pr = C.random_partners(np.random.default_rng(500 + sd))
        r = C.run_arm("NULL_TWIN_NOLEAK", sd, Pr, C.EPS_G_PC)
        r["params"] = params({"eps_g": C.EPS_G_PC, "partners": "random rng(500+seed)"}); emit(r)
    emit({"arm": "RUNINFO", "cpu_seconds": time.process_time() - t0, "attempt": 1})
    f.close()


if __name__ == "__main__":
    main()
