"""AMENDMENT 21 -- C3R: the recurrence-controlled assay of AMENDMENT 20 with ONE
change: OBSERVE families carry no PRISTINE learnability floor.

Why (declared before any donor ran): C3's frozen OBSERVE floor
(0 < p_PRISTINE <= 0.75) is almost never met in the T4/W5 world, which is
bimodal for PRISTINE (T31; W2), so C3 replicates were unfillable. Observation
is not on the composition path (candidates come from the held schema;
selection uses VALIDATE), and W4 showed observation is thin anyway.

Everything else is AMENDMENT 20 verbatim: panel, motifs, VALIDATE / T_SAME /
T_OTHER roles, window p_PRISTINE <= 0.75 on VALIDATE/TRANSFER, arms, n = 8,
ladder, verdicts (a20_c3.stage_report). The C3 SUPPLY is REUSED unchanged: the
qualified foundry rows engine/A20_C3/A20_FOUNDRY_ROWS_2026-09-28.jsonl and plan
A20_PLAN (sha256 recorded in AMENDMENT 21). Artifacts go under engine/A21_C3R/.
OBSERVE = the replicate's T4-qualified NAT spares (first 4 by name); if fewer
than 4, the remaining qualified OTHER-motif spares not used by any role
(first by name).
Usage: python a21_c3r.py <donors|transfer|report> [workers]
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a20_c3 as B               # noqa: E402  (sets C.HERE to A20_C3; overridden below)
from a20_c3 import C, ON, NREP, log   # noqa: E402

SRC = HERE / "A20_C3"
C.HERE = HERE / "A21_C3R"
C.HERE.mkdir(exist_ok=True)
for f in ("A20_PLAN_%s.json" % C.DATE, "A20_FOUNDRY_ROWS_%s.jsonl" % C.DATE, "A20_PANEL_%s.json" % C.DATE):
    if not (C.HERE / f).exists():
        shutil.copyfile(SRC / f, C.HERE / f)


def assign(rows, r):
    q = [x for x in rows if x.get("T4_qualified") and x["source"].startswith("%d|" % r)]
    q.sort(key=lambda x: x["name"])
    head = [x for x in q if x.get("p_PRISTINE", 0) <= 0.75]
    fams, used, ok = [], set(), True

    def take(pool, k, role, tag):
        nonlocal ok
        c = [x for x in pool if x["name"] not in used][:k]
        if len(c) < k:
            ok = False
        for x in c:
            used.add(x["name"])
            fams.append(dict(x, role=role, tclass=tag, qualified_dev_size=x["Q2_size"]))

    for a in ON:
        take([x for x in head if x["source"] == "%d|%s|MOTIF" % (r, a)], 1, "VALIDATE", a + ":MOTIF")
        take([x for x in head if x["source"] == "%d|%s|MOTIF" % (r, a)], 2, "TRANSFER", a + ":SAME")
        take([x for x in head if x["source"] == "%d|%s|OTHER" % (r, a)], 2, "TRANSFER", a + ":OTHER")
    nat = [x for x in q if x["source"] == "%d|NAT|NAT" % r and x["name"] not in used]
    spare = [x for x in q if x["source"].endswith("|OTHER") and x["name"] not in used]
    obs = (nat + spare)[:4]
    if len(obs) < 4:
        ok = False
    for x in obs:
        used.add(x["name"])
        fams.append(dict(x, role="OBSERVE", tclass="OBS", qualified_dev_size=x["Q2_size"]))
    return fams, ok


B.assign = assign
N_MIN = 7          # declared before any C3R donor ran: replicate 4 is unfillable (14/16 TRANSFER)


def stage_report(_w=0):
    """A20's frozen report logic, then the A21 verdict with the declared n: YES iff
    REUSED_SAME >= 5 and CAPABILITY_SAME >= 5 among >= N_MIN run replicates, and the
    frozen sign tests (p < 0.05) -- the same absolute thresholds as A20."""
    import json as _j
    B.stage_report()
    res = C.rd("A20_C3_RESULT_%s.json" % C.DATE)
    cnt = res["counts"]

    def yes(arm, v):
        return (cnt[arm]["n"] >= N_MIN and cnt[arm]["REUSED_SAME"] >= 5 and cnt[arm]["CAPABILITY_SAME"] >= 5
                and all(p < 0.05 for p in v["sign_p_REUSED_SAME"].values()))
    res["A21_H1_G1_YES"] = yes("G1", res["H1_G1"])
    res["A21_G1_RECURRENT_STEPPING_STONE"] = ("UNTESTABLE" if cnt["G1"]["n"] < N_MIN
                                              else ("YES" if res["A21_H1_G1_YES"] else "NO"))
    res["A21_GENERIC_RECURRENT_STEPPING_STONE"] = sum(yes(s, v) for s, v in res["H2_SHAMS"].items())
    res["A21_note"] = "A20 verdict fields (n >= 8) are superseded by the A21_* fields (n >= 7)."
    C.wr("A21_C3R_RESULT_%s.json" % C.DATE, res)
    log("A21 G1_RECURRENT_STEPPING_STONE=%s GENERIC=%d/3" % (res["A21_G1_RECURRENT_STEPPING_STONE"],
                                                          res["A21_GENERIC_RECURRENT_STEPPING_STONE"]))

if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    log("A21 stage %s workers %d" % (st, w))
    {"donors": B.stage_donors, "transfer": B.stage_transfer, "report": stage_report}[st](w)
    log("A21 stage %s done" % st)
