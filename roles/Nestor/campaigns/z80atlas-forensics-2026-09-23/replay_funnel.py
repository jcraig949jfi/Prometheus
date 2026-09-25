"""S1-A part 2: aggregate the 256 forensic replays into the replication funnel.

Only replays whose summary matched the frozen record (REPLAY_MATCH) are used; any other
status is counted and excluded, never silently merged.

Three views, per reproduction physics:
  SEQUENTIAL (primary)  organisms that did step k AFTER doing steps 1..k-1 themselves,
                        in order, at some point in their life. Step 1 is NOT_APPLICABLE
                        under self_location NONE (there is no self-location op to
                        execute), so those organisms enter the chain at step 2.
  MARGINAL              organisms that ever did step k, regardless of order.
  RUN-LEVEL             runs in which at least one organism reached step k sequentially.
Transition probability p_k = count_k / count_{k-1}; absolute loss = count_{k-1} - count_k.

    python replay_funnel.py  -> REPLAY_FUNNEL.json
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "replays" / "funnel"
PHYSICS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE", "OVERWRITE")
STEPS = ("self_location_executed", "alloc_attempted", "alloc_succeeded", "target_writes",
         "birth_attempted", "birth_accepted", "fidelity_ge_090", "offspring_evidence_child")


def chain(counts, entry):
    rows, prev = [], entry
    for k in STEPS:
        c = counts[k]
        rows.append({"step": k, "count": c,
                     "transition_p": (round(c / prev, 6) if prev else None),
                     "absolute_loss": (prev - c) if prev is not None else None})
        prev = c
    return rows


def main():
    ids = [l.strip() for l in open(HERE / "replay_ids.txt") if l.strip()]
    recs, status = [], Counter()
    for rid in ids:
        p = OUT / (rid + ".json")
        if not p.exists():
            status["MISSING"] += 1
            continue
        r = json.loads(p.read_text())
        status[r["status"]] += 1
        if r["status"] == "REPLAY_MATCH":
            recs.append(r)
    rep = {"status": dict(status), "n_used": len(recs), "physics": {}}
    for phys in PHYSICS:
        R = [r for r in recs if r["cell"]["reproduction"] == phys]
        orgs = sum(r["organisms_total"] for r in R)
        seq, mar, runs = Counter(), Counter(), Counter()
        ct = Counter()
        strata = defaultdict(lambda: {"runs": 0, "organisms": 0, "seq": Counter(), "ct": Counter()})
        for r in R:
            none = r["cell"]["self_location"] == "NONE"
            for k in STEPS:
                v = r["funnel_sequential"][k]
                seq[k] += v
                if v:
                    runs[k] += 1
                m = r["funnel_marginal"][k]
                if m is not None:
                    mar[k] += m
            ct.update(r["ct"])
            key = "%s/%s" % (r["cell"]["self_location"], r["cell"]["copy_primitive"])
            S = strata[key]
            S["runs"] += 1
            S["organisms"] += r["organisms_total"]
            S["ct"].update(r["ct"])
            for k in STEPS:
                S["seq"][k] += r["funnel_sequential"][k]
        # Under NONE every organism starts at step 1 by definition; separate that out so
        # step 1's count is only organisms that actually EXECUTED a self-location op.
        none_orgs = sum(r["organisms_total"] for r in R if r["cell"]["self_location"] == "NONE")
        loc_orgs = orgs - none_orgs
        rep["physics"][phys] = {
            "runs": len(R), "organisms": orgs,
            "organisms_self_location_NONE": none_orgs,
            "self_location_executed_by_locating_organisms":
                seq["self_location_executed"] - none_orgs,
            "locating_organisms": loc_orgs,
            "sequential": chain(seq, orgs),
            "marginal": {k: mar[k] for k in STEPS},
            "runs_reaching": {k: runs[k] for k in STEPS},
            "event_counts": dict(ct),
            "by_self_location_copy_primitive": {
                k: {"runs": v["runs"], "organisms": v["organisms"],
                    "sequential": {s: v["seq"][s] for s in STEPS},
                    "events": dict(v["ct"])} for k, v in sorted(strata.items())},
        }
    (HERE / "REPLAY_FUNNEL.json").write_text(json.dumps(rep, indent=1))
    print("status", dict(status))
    for phys, P in rep["physics"].items():
        print("==", phys, "runs", P["runs"], "organisms", P["organisms"],
              "(NONE-located %d)" % P["organisms_self_location_NONE"])
        for row in P["sequential"]:
            print("  %-26s %8d  p=%-10s loss=%s   marginal %d   runs %d" % (
                row["step"], row["count"], row["transition_p"], row["absolute_loss"],
                P["marginal"][row["step"]], P["runs_reaching"][row["step"]]))
        print("  events", P["event_counts"])
    return rep


if __name__ == "__main__":
    main()
