"""Close the seeded-world moat_advantage ledger (FORENSIC-MOAT-01; plan fixed in MOAT_LEDGER.json before the replay).

Reads the preserved campaign records + replays/REPLAY_seeded_moat_advantage.json; writes MOAT_LEDGER_CLOSURE_<date>.json.
Flags are only ever REMOVED (VOID runs; in the LOWER bound also unadjudicated seeded moat_crossed); no flag is created, so the
known asymmetry (controls not replayed; an advantage the original scorer missed cannot be added) is reported as a count.

    python -m archaeon.z80atlas.postcampaign.close_moat_ledger --date 2026-09-24
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path

from archaeon.z80atlas.postcampaign import adjudicate as A
from archaeon.z80atlas import scheduler as S

HERE = Path(__file__).resolve().parent
MOAT = ("moat_crossed", "moat_advantage")


def classify(rep: dict) -> dict:
    per = {}; q = False
    for t, v in rep["provenance"]["first_crossing"].items():
        if t in rep["provenance"]["first_clean_crossing"]:
            k = "QUALIFIED"; q = True
        elif v["inserted_ancestry"]:
            k = "WITNESS_ONLY_UNMODIFIED" if v["is_unmodified_founder_tape"] else "WITNESS_ONLY_DESCENDANT"
        else:
            k = "ANOMALY"
        per[t] = {"class": k, "first_crossing_epoch": v["epoch"], "clean_crossing_epoch": rep["provenance"]["first_clean_crossing"].get(t, {}).get("epoch")}
    return {"run_status": "QUALIFIED" if q else "VOID_INSERTED_ONLY", "tasks": per}


def rescore(runs: dict, fams: dict, strip) -> dict:
    """Family best scores after removing moat flags from runs for which strip(run) is true (flags as the campaign scorer set them)."""
    best = {}
    for fam, f in fams.items():
        b = 0; br = None
        for rid in f["runs"]:
            fl = dict(runs[rid].get("flags") or {})
            if strip(runs[rid]):
                for k in MOAT: fl.pop(k, None)
            sc = S.score_flags(fl)
            if sc > b: b = sc; br = rid
        best[fam] = (b, br)
    return best


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); a = ap.parse_args(argv)
    rep = json.loads((HERE / "replays" / "REPLAY_seeded_moat_advantage.json").read_text(encoding="utf-8"))
    runs, _, _ = A.load_runs(Path(A.DEFAULT_HIST))
    for r in runs.values():                                                  # the directive's spontaneous correction first
        if r["status"] == "DONE" and ":transplant:" in r["scheduler_reason"] and r["signals"].get("spontaneous_replication"):
            r["signals"] = dict(r["signals"], spontaneous_replication=False)
    fams = A.family_table(runs)
    cls = {x["run_id"]: classify(x) for x in rep["results"] if x["admitted"]}
    unadmitted = [x["run_id"] for x in rep["results"] if not x["admitted"]]
    void = {k for k, v in cls.items() if v["run_status"] == "VOID_INSERTED_ONLY"}
    seeded = lambda r: r["status"] == "DONE" and r["factor_vector"]["init"] == "seeded_replicator"
    unadj = lambda r: seeded(r) and r["run_id"] not in cls and any(k in (r.get("flags") or {}) for k in MOAT)
    corrected = rescore(runs, fams, lambda r: False)
    upper = rescore(runs, fams, lambda r: r["run_id"] in void)
    lower = rescore(runs, fams, lambda r: r["run_id"] in void or unadj(r))

    def tier(sc):
        top = max(v[0] for v in sc.values()); return top, {f for f, v in sc.items() if v[0] == top}
    t_c, top_c = tier(corrected); t_u, top_u = tier(upper); t_l, top_l = tier(lower)
    order = lambda sc: [{"family": f, "score": v[0], "best_run": v[1], "best_run_init": runs[v[1]]["factor_vector"]["init"] if v[1] else None}
                        for f, v in sorted(sc.items(), key=lambda x: (-x[1][0], x[0]))[:40]]
    missed = 0
    for fam, f in fams.items():                                              # seeded treatments whose control also crossed: advantages that
        ctrls = [r2 for r2 in f["specs"].values() if r2["scheduler_reason"].startswith("matched_control:reproduction")]   # a witness-only control
        for rid in f["runs"]:                                                # crossing may have hidden (not searched)
            r = runs[rid]
            if seeded(r) and r["signals"].get("moat_crossed") and not r["scheduler_reason"].startswith("matched_control") and "moat_advantage" not in (r.get("flags") or {}):
                if any(c["factor_vector"]["task"] == r["factor_vector"]["task"] and c["signals"].get("moat_crossed") for c in ctrls): missed += 1
    task_counts = Counter(t["class"] for v in cls.values() for t in v["tasks"].values())
    clean_epoch0 = sum(1 for v in cls.values() for t in v["tasks"].values() if t["class"] == "QUALIFIED" and t["clean_crossing_epoch"] == 0)
    out = {"schema": "archaeon.z80atlas.moat_ledger_closure.v1", "date": a.date, "plan": "MOAT_LEDGER.json (fixed before launch)",
           "replayed": rep["n"], "admitted": len(cls), "unadmitted": unadmitted,
           "runs": dict(Counter(v["run_status"] for v in cls.values())), "task_crossings": dict(task_counts),
           "qualified_task_crossings_at_epoch0": clean_epoch0,
           "void_runs": sorted(void), "void_families": sorted({runs[r]["family"] for r in void}),
           "unadjudicated_seeded_runs_with_moat_flags_outside_set": sum(1 for r in runs.values() if unadj(r)),
           "not_searched_upper_bound_missed_advantages": missed,
           "ranking": {"corrected_spontaneous_only": {"top_score": t_c, "top_tier_size": len(top_c)},
                       "UPPER_void_removed": {"top_score": t_u, "top_tier_size": len(top_u), "top40": order(upper)},
                       "LOWER_void_and_unadjudicated_removed": {"top_score": t_l, "top_tier_size": len(top_l), "top40": order(lower)}},
           "families_whose_score_changes": {f: {"corrected": corrected[f][0], "upper": upper[f][0], "lower": lower[f][0]} for f in fams
                                            if len({corrected[f][0], upper[f][0], lower[f][0]}) > 1 and corrected[f][0] >= 10},
           "per_run": cls,
           "status": {"seeded_world_moat_advantage": "CLOSED (every flag adjudicated: QUALIFIED or VOID_INSERTED_ONLY)",
                      "seeded_world_moat_crossed_outside_the_932": "UNADJUDICATED by design (about 1040 CPU-hours; not bounded)",
                      "random_world_moat_flags": "USABLE",
                      "allocation": "only the LOWER-bound ranking may steer allocation; families whose standing depends on unadjudicated flags are listed"}}
    p = HERE / ("MOAT_LEDGER_CLOSURE_%s.json" % a.date)
    p.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("admitted", "runs", "task_crossings", "qualified_task_crossings_at_epoch0", "unadjudicated_seeded_runs_with_moat_flags_outside_set",
                                          "not_searched_upper_bound_missed_advantages")}))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "top40"} for k, v in out["ranking"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
