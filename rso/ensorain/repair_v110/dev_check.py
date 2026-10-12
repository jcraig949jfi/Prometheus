"""C-016-T041 development check of the v1.1.0 rule (PREREGISTRATION.md v1.1.0 s8): the registered controls (now with
jitter = Q-d and learns_pre = Q-e) plus Pallas's other challenge subjects (rso/ensorain/challenge/subjects_c.py,
imported unchanged; innate_zero is P3's ref_like(0.0, 1.0, 0.5)), on DEVELOPMENT seeds 16_300_001..400 at the
registered N = 400, every arm. No searched subject's endpoint is computed (they get `assay.preflight` only), no
confirmatory seed is used. Writes DEV_CHECK.json (verdicts, qualification, power) and DEV_ROWS.jsonl.gz (the rows).

    python -B -m rso.ensorain.repair_v110.dev_check
"""
import gzip
import json
import os
import time

from rso.ensorain import analysis, assay, subjects as S
from rso.ensorain.challenge import subjects_c as C

HERE = os.path.dirname(os.path.abspath(__file__))
N = S.N_CONFIRM
SEEDS = [S.DEV[0] + i for i in range(N)]


def challenge_subjects():
    return {"innate_zero": C.ref_like(0.0, 1.0, 0.5), "innate_max": C.innate_max(), "clock_hybrid": C.clock_hybrid()}


def power_table(v):
    """Power at the registered N from the reference's development revised-life rates, and a sensitivity grid."""
    ref = v["reference"]
    rate = {a: rv / N for a, rv in zip(ref["arms"], ref["revised_lives"])}
    out = dict(reference_rates={a: "%d/%d" % (rv, N) for a, rv in zip(ref["arms"], ref["revised_lives"])}, rows=[])
    for ctrl in ("frozen", "noise", "shuffle"):
        out["rows"].append(dict(p_full=round(rate["full"], 4), p_ctrl=round(rate[ctrl], 4), control=ctrl,
                                P_n400=round(analysis.power_revised(rate["full"], rate[ctrl], N), 4),
                                S_n400=round(analysis.power_revised(rate["full"], rate[ctrl], N, analysis.ALPHA / 6), 4)))
    for pf, pc in ((0.6, 0.45), (0.6, 0.4), (0.6, 0.3), (0.4, 0.25), (0.3, 0.15)):
        out["rows"].append(dict(p_full=pf, p_ctrl=pc, control="sensitivity",
                                P_n200=round(analysis.power_revised(pf, pc, 200), 4),
                                P_n400=round(analysis.power_revised(pf, pc, N), 4),
                                S_n400=round(analysis.power_revised(pf, pc, N, analysis.ALPHA / 6), 4)))
    return out


def main():
    t0 = time.time()
    subs = dict(assay.controls(), **challenge_subjects())
    rows = assay.run(subs, analysis.ARMS, SEEDS)
    v = analysis.report(rows, N)
    searched = S.load_searched(os.path.join(HERE, "..", "SUBJECTS.json"))
    res = dict(schema="prometheus.rso.ensorain.dev_check.v1.1", task="C-016-T041", spec=assay.SPEC, K=assay.K,
               seeds=[SEEDS[0], SEEDS[-1]], n=N, environment=assay.environment(), rows=len(rows),
               rows_sha256=assay.rows_sha256(rows), family_s=assay.family_s(searched),
               searched_preflight=assay.preflight(searched, SEEDS[:2]), verdicts=v,
               qualification=analysis.qualification(v), power=power_table(v), cpu_wall_s=None)
    res["cpu_wall_s"] = round(time.time() - t0, 1)
    with gzip.open(os.path.join(HERE, "DEV_ROWS.jsonl.gz"), "wt", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(HERE, "DEV_CHECK.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    assay.print_verdicts(v)
    print("qualification", res["qualification"])
    print(json.dumps(res["power"], indent=1))
    print("rows", len(rows), res["rows_sha256"], res["cpu_wall_s"], "s")


if __name__ == "__main__":
    main()
