"""W6 Pass 4 ALT world, CONTROL-FIRST: positive control, cheat, null twin.

No treatment arm (group partners with eps_g 0.05) is run or defined here.
Rows -> alt_control_rows.jsonl (flushed per row); ALT_ATTAINABILITY.json.
"""
import json, os, time
import numpy as np
import alt_world as A

C = A.C
HERE = A.HERE
LEVELS = [0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 1.0]
SIGMA_ALT = 0.05
EPS = 0.05
SEEDS = list(range(100, 110))
A1_THR, A2_THR = 0.2, 0.6


def clauses(rows, classes):
    """A1, A2 on a set of rows spanning all levels."""
    means = {r: float(np.mean([x["ari_ftle"] for x in rows if x["r"] == r])) for r in LEVELS}
    ch = [means[r] for r in LEVELS if classes[str(r)] == "chaotic"]
    nc = [means[r] for r in LEVELS if classes[str(r)] == "non-chaotic"]
    a1 = (min(ch) - max(nc)) if ch and nc else float("nan")
    a2 = A.spearman([x["lle"] for x in rows], [x["ari_ftle"] for x in rows])
    lvl_lle = [float(np.mean([x["lle"] for x in rows if x["r"] == r])) for r in LEVELS]
    a2_levels = A.spearman(lvl_lle, [means[r] for r in LEVELS])
    return {"A1": {"value": a1, "threshold": A1_THR, "met": bool(a1 >= A1_THR)},
            "A2": {"value": a2, "threshold": A2_THR, "met": bool(a2 >= A2_THR)},
            "level_means": means, "level_lle": dict(zip(map(str, LEVELS), lvl_lle)),
            "spearman_level_means_secondary": a2_levels}


def main():
    t0 = time.process_time()
    f = open(os.path.join(HERE, "alt_control_rows.jsonl"), "w", encoding="utf-8")

    def emit(r):
        f.write(json.dumps(r) + "\n"); f.flush()

    # exactness: r=1, sigma=0 reproduces the frozen controls.run_arm (frozen PC arm, seed 0)
    Pg = C.group_partners()
    a = A.run("EXACTNESS_CHECK", 0, Pg, 0.0, 1.0, 0.0)
    b = C.run_arm("EXACTNESS_CHECK", 0, Pg, 0.0)
    exact = all(a[k] == b[k] for k in b)
    emit({"arm": "EXACTNESS_CHECK", "exact": exact, "ari_ftle": a["ari_ftle"], "ari_corr": a["ari_corr"]})

    # 1. null twin at every level (random partners, eps 0.05, sigma 0.05)
    twin = []
    for r in LEVELS:
        for sd in SEEDS:
            Pr = C.random_partners(np.random.default_rng(500 + sd))
            x = A.run("ALT_NULL_TWIN", sd, Pr, EPS, r, SIGMA_ALT, {"attack": "ALT"}); twin.append(x); emit(x)
    classes = {}
    for r in LEVELS:
        m = float(np.mean([x["lle"] for x in twin if x["r"] == r]))
        classes[str(r)] = "chaotic" if m > 0 else ("non-chaotic" if m < 0 else "edge")
    # 2. positive control: grouping gated on chaos by construction
    pc = []
    for r in LEVELS:
        for sd in SEEDS:
            if classes[str(r)] == "chaotic":
                x = A.run("ALT_POSITIVE_CONTROL", sd, Pg, 0.0, r, SIGMA_ALT,
                          {"attack": "ALT", "pc_construction": "group partners, eps_g 0 (chaotic level)"})
            else:
                Pr = C.random_partners(np.random.default_rng(500 + sd))
                x = A.run("ALT_POSITIVE_CONTROL", sd, Pr, EPS, r, SIGMA_ALT,
                          {"attack": "ALT", "pc_construction": "random partners, eps_g 0.05 (non-chaotic level)"})
            pc.append(x); emit(x)
    # 3. cheat: null twin rows with nominal partition injected at chaotic levels
    cheat = []
    for x in twin:
        c = dict(x); c["arm"] = "ALT_CHEAT"
        if classes[str(x["r"])] == "chaotic":
            c["partition_ftle"] = C.LABELS.tolist(); c["ari_ftle"] = C.ari(C.LABELS, C.LABELS)
        cheat.append(c); emit(c)

    cl = {"POSITIVE_CONTROL": clauses(pc, classes), "CHEAT": clauses(cheat, classes),
          "NULL_TWIN": clauses(twin, classes)}
    n_ch = sum(v == "chaotic" for v in classes.values()); n_nc = sum(v == "non-chaotic" for v in classes.values())
    e0 = len(LEVELS) >= 5 and n_ch >= 1 and n_nc >= 1
    per = []
    for cid in ["A1", "A2"]:
        per.append({"id": cid, "positive_value": cl["POSITIVE_CONTROL"][cid]["value"],
                    "cheat_value": cl["CHEAT"][cid]["value"], "twin_value": cl["NULL_TWIN"][cid]["value"],
                    "threshold": cl["POSITIVE_CONTROL"][cid]["threshold"], "comparison": ">=",
                    "attainable": cl["POSITIVE_CONTROL"][cid]["met"],
                    "cheat_detected": cl["CHEAT"][cid]["met"],
                    "discriminating": not cl["NULL_TWIN"][cid]["met"]})
    eligible = bool(exact and e0 and all(p["attainable"] and p["cheat_detected"] and p["discriminating"] for p in per))
    cpu = time.process_time() - t0
    emit({"arm": "RUNINFO", "cpu_seconds": cpu, "attempt": 1})
    f.close()
    out = {"triplicateId": "HT-55162c0ac0", "world": "W6", "attack": "ALT",
           "frozen_before_treatment_code": True,
           "levels_r": LEVELS, "sigma": SIGMA_ALT, "eps_g": EPS, "kappa": C.KAPPA, "seeds": SEEDS,
           "level_class_frozen": classes, "level_class_source": "NULL_TWIN carrier mean LLE sign",
           "n_chaotic": n_ch, "n_nonchaotic": n_nc,
           "E0_levels_ok": e0, "exactness_r1_sigma0_equals_controls": exact,
           "clauses": per, "detail": cl, "eligible": eligible,
           "status_if_not_eligible": None if eligible else "NOT_ELIGIBLE",
           "cpu_seconds": cpu}
    json.dump(out, open(os.path.join(HERE, "ALT_ATTAINABILITY.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: out[k] for k in ["level_class_frozen", "E0_levels_ok",
                                          "exactness_r1_sigma0_equals_controls", "clauses", "eligible",
                                          "cpu_seconds"]}, indent=1))
    print("level LLE (twin)", cl["NULL_TWIN"]["level_lle"])


if __name__ == "__main__":
    main()
