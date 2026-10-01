"""W6 Pass 4 attacks: R, ORIG, ALT. Written AFTER ALT_ATTAINABILITY.json (eligible).

Rows -> rows.jsonl, one row per attack x variant x arm x seed, flushed per row.
Prints no treatment statistic.
"""
import json, os, time
import numpy as np
import alt_world as A
import alt_controls as AC

C = A.C
HERE = A.HERE
SEEDS = list(range(100, 110))
EPS = 0.05
ORIG_R = 0.2
ORIG_SIGMAS = [0.0, 0.01, 0.05]


def main():
    att = json.load(open(os.path.join(HERE, "ALT_ATTAINABILITY.json"), encoding="utf-8"))
    t0 = time.process_time()
    f = open(os.path.join(HERE, "rows.jsonl"), "w", encoding="utf-8")

    def emit(r):
        f.write(json.dumps(r) + "\n"); f.flush()

    Pg = C.group_partners()

    def four_arms(attack, variant, r, sigma):
        for sd in SEEDS:
            Pr = C.random_partners(np.random.default_rng(500 + sd))
            tag = {"attack": attack, "variant": variant}
            emit(A.run("TREATMENT", sd, Pg, EPS, r, sigma, tag))
            pc = A.run("POSITIVE_CONTROL", sd, Pg, 0.0, r, sigma, tag); emit(pc)
            ch = dict(pc); ch["arm"] = "CHEAT"; ch["partition_ftle"] = C.LABELS.tolist()
            ch["ari_ftle"] = C.ari(C.LABELS, C.LABELS); emit(ch)
            emit(A.run("NULL_TWIN", sd, Pr, EPS, r, sigma, tag))

    # R: original world (r = 1, sigma = 0 is bit-identical to controls.run_arm), fresh seeds
    four_arms("R", "original", 1.0, 0.0)
    # ORIG: contracting carrier r = 0.2, noise grid
    for s in ORIG_SIGMAS:
        four_arms("ORIG", f"r0.2_sigma{s}", ORIG_R, s)
    # ALT: controls copied from the control-first phase (same code, same seeds)
    for l in open(os.path.join(HERE, "alt_control_rows.jsonl"), encoding="utf-8"):
        x = json.loads(l)
        if x["arm"].startswith("ALT_"):
            x["source"] = "alt_control_rows.jsonl"; x["variant"] = "sweep"; emit(x)
    # ALT treatment (only if eligible)
    if att["eligible"]:
        for r in AC.LEVELS:
            for sd in SEEDS:
                emit(A.run("ALT_TREATMENT", sd, Pg, EPS, r, AC.SIGMA_ALT, {"attack": "ALT", "variant": "sweep"}))
    emit({"arm": "RUNINFO", "cpu_seconds": time.process_time() - t0, "attempt": 1})
    f.close()
    print("rows written; cpu_seconds", time.process_time() - t0)


if __name__ == "__main__":
    main()
