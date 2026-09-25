"""S1-C: aggregate the P-11 reassay of the predecessor's 1,031 admissible spontaneous
replicators.

P-11 does NOT rewrite the frozen result. The frozen record says 1,031 ADMISSIBLE under
the predecessor criterion and that stays true. This file reports, beside it, how many
survive the stricter causal reassay (P11_SPEC.md, commit f28e5fd72, specified and tested
before any of the 1,031 was inspected).

A run SURVIVES iff its replay reproduced the frozen run exactly (REPLAY_MATCH) and it
contains at least one P-11-causal pair event. Criterion failure counts are per EVENT
(majority over the 3 draws). A replay that did not match is reported, never counted.

    python p11_reassay.py   -> P11_REASSAY.jsonl (one row per run), P11_REASSAY.json
"""
from __future__ import annotations

import gzip
import json
import pathlib
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "replays" / "p11"


def first_p11(run_id):
    p = OUT / (run_id + ".events.jsonl.gz")
    if not p.exists():
        return None, 0, Counter()
    first, n, crit = None, 0, Counter()
    with gzip.open(p, "rt") as fh:
        for line in fh:
            e = json.loads(line)
            n += 1
            for c in ("C2", "C4", "C5"):
                if not e[c]:
                    crit["fail_" + c] += 1
            if not e["C2"] and e["C4"] and e["C5"]:
                crit["only_C2"] += 1
            if e["C2"] and not e["C4"] and e["C5"]:
                crit["only_C4"] += 1
            if e["C2"] and e["C4"] and not e["C5"]:
                crit["only_C5"] += 1
            if e["p11"] and first is None:
                first = {k: e.get(k) for k in ("epoch", "pair", "fid_other", "fid_self",
                                               "donor_wrote", "draws_passed", "donor_genome",
                                               "donor_authored_share_ordinary",
                                               "fid_init_ordinary")}
    return first, n, crit


def main():
    ids = [l.strip() for l in open(HERE / "p11_ids.txt") if l.strip()]
    rows, status = [], Counter()
    for rid in ids:
        p = OUT / (rid + ".json")
        if not p.exists():
            status["NOT_YET_RUN"] += 1
            continue
        r = json.loads(p.read_text())
        status[r["status"]] += 1
        row = {"run_id": rid, "status": r["status"], "cell": r.get("cell"),
               "tier": r.get("tier"), "wall_s": r.get("wall_s")}
        if r["status"] == "REPLAY_MATCH":
            q = r["p11"]
            fe, n_ev, crit = first_p11(rid)
            row.update({k: q[k] for k in ("n_pred_events", "n_p11_events", "n_p11_literal_events",
                                          "fail_C2", "fail_C4", "fail_C5", "max_pred_depth",
                                          "max_p11_depth", "max_p11_literal_depth")})
            row["first_p11_event"] = fe
            row["event_criteria"] = dict(crit)
            row["events_file_count"] = n_ev
        rows.append(row)
    (HERE / "P11_REASSAY.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n"
                                                   for x in rows), encoding="ascii")
    M = [x for x in rows if x["status"] == "REPLAY_MATCH"]
    surv = [x for x in M if x["n_p11_events"] > 0]
    surv_lit = [x for x in M if x["n_p11_literal_events"] > 0]

    def dist(key, xs):
        return dict(sorted(Counter(x[key] for x in xs).items()))

    def cdist(f, xs):
        return dict(Counter(x["cell"][f] for x in xs).most_common())

    ev = Counter()
    for x in M:
        ev["pred_events"] += x["n_pred_events"]
        ev["p11_events"] += x["n_p11_events"]
        ev["p11_literal_events"] += x["n_p11_literal_events"]
        for k, v in x["event_criteria"].items():
            ev[k] += v
    runs_fail = {c: sum(1 for x in M if x["n_p11_events"] == 0 and x["fail_" + c] > 0)
                 for c in ("C2", "C4", "C5")}
    rep = {
        "predecessor_criterion_admissible": 1031,
        "replay_status": dict(status),
        "n_reassayed": len(M),
        "p11_surviving_runs": len(surv),
        "p11_surviving_runs_literal_authorship": len(surv_lit),
        "event_totals": dict(ev),
        "non_surviving_runs_with_an_event_failing": runs_fail,
        "depth_predecessor_criterion": dist("max_pred_depth", M),
        "depth_p11": dist("max_p11_depth", M),
        "depth_p11_among_survivors": dist("max_p11_depth", surv),
        "depth_1_share_predecessor": (round(sum(1 for x in M if x["max_pred_depth"] == 1) / len(M), 4)
                                      if M else None),
        "depth_1_share_p11_survivors": (round(sum(1 for x in surv if x["max_p11_depth"] == 1) / len(surv), 4)
                                        if surv else None),
        "survivors_by_structure": cdist("structure", surv),
        "survivors_by_representation": cdist("representation", surv),
        "survivors_by_pressure": cdist("pressure", surv),
        "survivors_by_atlas_axis": cdist("atlas_axis", surv),
        "reassayed_by_atlas_axis": cdist("atlas_axis", M),
    }
    (HERE / "P11_REASSAY.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__":
    main()
