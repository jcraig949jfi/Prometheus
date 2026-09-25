"""S1-A part 1: the deepest replication funnel the FROZEN 72-hour record supports.

Population: every RANDOM-start run whose reproduction physics is ENDOGENOUS_COPY,
ENDOGENOUS_PARTIAL, CONSTRUCTIVE or OVERWRITE (PAIR_EXECUTION is excluded by the
directive; EXTERNAL has ALLOC/BIRTH disabled and is reported only as a count).

Read-only. The frozen observatory is opened for reading and nothing is written under
it. Every step the frozen counters cannot establish is labelled NOT_MEASURED; a
LOWER_BOUND is a count the record proves is at least this large, never an estimate.

The frozen record is run-level and marginal: it holds per-run totals, not per-organism
event order, so "reached step k" here means "the run contains evidence of step k", not
"one organism did steps 1..k in order". The sequential per-organism funnel is the
forensic replay's job (replay_funnel.py).

    python frozen_funnel.py [FROZEN_OBSERVATORY]   -> FROZEN_FUNNEL.json / .md
"""
from __future__ import annotations

import gzip
import json
import os
import pathlib
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_OBS = pathlib.Path(os.environ.get(
    "Z80A_FROZEN_OBS",
    r"F:/Prometheus-worktrees/nestor-sidequest-graphworld/roles/Nestor/campaigns/"
    r"z80atlas-2026-09-19/observatory"))
PHYSICS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE", "OVERWRITE")
FREE_POLICY = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "CONSTRUCTIVE")   # z8.FREE

STEPS = ("self_location_executed", "alloc_attempted", "alloc_succeeded", "target_writes",
         "birth_attempted", "birth_accepted", "fidelity_ge_090", "offspring_evidence_child")


def population(obs):
    rows = [json.loads(l) for l in gzip.open(obs / "INDEX.jsonl.gz", "rt")]
    pop = [r for r in rows if r["cell"]["seeding"] == "RANDOM"
           and r["cell"]["reproduction"] in PHYSICS]
    ext = sum(1 for r in rows if r["cell"]["seeding"] == "RANDOM"
              and r["cell"]["reproduction"] == "EXTERNAL")
    return sorted(pop, key=lambda r: r["run_id"]), ext


def run_steps(r, s, cfg):
    """Per-run step evidence. Value is True/False, or a string label when unmeasured."""
    phys = r["cell"]["reproduction"]
    sl = r["cell"]["self_location"]
    alloc_ok = s["alloc_calls"] - s["alloc_fails"]
    births_wrote = s["births_endogenous"] - s["births_no_copy"]
    fid_births = s["replication_events"] + s["births_similar_no_write"]
    out = {}
    out["self_location_executed"] = "NOT_APPLICABLE" if sl == "NONE" else "NOT_MEASURED"
    out["alloc_attempted"] = s["alloc_calls"] > 0
    out["alloc_succeeded"] = alloc_ok > 0
    if phys in FREE_POLICY:
        # FREE policy: an out-of-span write is only permitted inside the world's free
        # window, which is the organism's allocated daughter slot (or, for the rest of the
        # slice in which it was born, the slot just born). So writes_other > 0 is direct
        # evidence of writing into an allocated target.
        out["target_writes"] = s["writes_other"] > 0
    else:
        # OVERWRITE runs under ARENA: writes_other counts writes anywhere outside the
        # organism's span, target or not. Only a birth whose bytes differ from the slot's
        # pre-image proves a target write.
        out["target_writes"] = True if births_wrote > 0 else "NOT_MEASURED"
    # BIRTH/SPLIT calls are counted per slice in z8 but never aggregated into the record.
    out["birth_attempted"] = True if s["births_endogenous"] > 0 else "NOT_MEASURED"
    out["birth_accepted"] = s["births_endogenous"] > 0
    out["fidelity_ge_090"] = fid_births > 0
    # Evidence-backed = fid >= 0.90 AND placed >= half the child's bytes (world._on_birth).
    # If the run has no evidence-backed birth at all, no offspring can have produced one.
    # Otherwise the frozen lineage tuple cannot say which edges were evidence-backed
    # (span stores wrote_bytes OR len(g) when wrote_bytes == 0), so it is unmeasured.
    out["offspring_evidence_child"] = False if s["replication_events"] == 0 else "NOT_MEASURED"
    return out


def main(obs=DEFAULT_OBS):
    obs = pathlib.Path(obs)
    pop, n_external = population(obs)
    per = defaultdict(lambda: {"runs": 0, "steps": Counter(), "unmeasured": Counter(),
                               "not_applicable": Counter(), "events": Counter(),
                               "by_sl_cp": defaultdict(Counter), "by_sl_cp_runs": Counter()})
    runs_out = []
    invaders = Counter()
    for r in pop:
        d = obs / r["paths"]["dir"].replace("\\", "/")
        res = json.loads((d / "RESULT.json").read_text())
        cfg = json.loads((d / "CONFIG.json").read_text())
        invaders[cfg["job"].get("invaders", 0)] += 1
        s = res["summary"]
        phys = r["cell"]["reproduction"]
        st = run_steps(r, s, cfg)
        P = per[phys]
        P["runs"] += 1
        key = "%s/%s" % (r["cell"]["self_location"], r["cell"]["copy_primitive"])
        P["by_sl_cp_runs"][key] += 1
        for k, v in st.items():
            if v is True:
                P["steps"][k] += 1
                P["by_sl_cp"][key][k] += 1
            elif v == "NOT_MEASURED":
                P["unmeasured"][k] += 1
            elif v == "NOT_APPLICABLE":
                P["not_applicable"][k] += 1
        for k in ("alloc_calls", "alloc_fails", "writes_other", "births_endogenous",
                  "births_no_copy", "births_no_copy_live", "births_similar_no_write",
                  "replication_events", "copy_bytes", "births_external"):
            P["events"][k] += s.get(k, 0)
        P["events"]["alloc_succeeded"] += s["alloc_calls"] - s["alloc_fails"]
        P["events"]["births_wrote_any"] += s["births_endogenous"] - s["births_no_copy"]
        P["events"]["births_fid_ge_090"] += s["replication_events"] + s["births_similar_no_write"]
        runs_out.append({"run_id": r["run_id"], "physics": phys, "tier": r["tier"],
                         "self_location": r["cell"]["self_location"],
                         "copy_primitive": r["cell"]["copy_primitive"], "steps": st})

    report = {"population": {"random_start_non_pair_runs": len(pop),
                             "random_start_external_runs_excluded": n_external,
                             "invaders_distribution": dict(invaders)},
              "semantics": "run-level marginal evidence from frozen per-run totals; "
                           "NOT_MEASURED = the frozen record cannot establish the step; "
                           "values are runs whose record PROVES the step",
              "steps": STEPS, "physics": {}}
    for phys in PHYSICS:
        P = per[phys]
        n = P["runs"]
        rows, prev = [], n
        for k in STEPS:
            um = P["unmeasured"][k]
            na = P["not_applicable"][k]
            got = P["steps"][k]
            row = {"step": k, "runs_proven": got, "runs_not_measured": um,
                   "runs_not_applicable": na}
            if um == 0 and na == 0 and prev is not None:
                row["transition_p"] = round(got / prev, 4) if prev else None
                row["absolute_loss"] = prev - got
                prev = got
            elif um == 0 and na == n:
                row["status"] = "NOT_APPLICABLE"
            else:
                row["status"] = "NOT_MEASURED" if got == 0 else "LOWER_BOUND"
                row["transition_p"] = None
                row["absolute_loss"] = None
                # a proven lower bound does not re-anchor the chain: the next measured
                # step's transition is taken from the last fully measured count
            rows.append(row)
        report["physics"][phys] = {
            "runs": n, "funnel": rows, "event_totals": dict(P["events"]),
            "by_self_location_copy_primitive": {k: {"runs": P["by_sl_cp_runs"][k], **dict(v)}
                                                for k, v in sorted(P["by_sl_cp"].items())}}
    (HERE / "FROZEN_FUNNEL.json").write_text(json.dumps(report, indent=1))
    (HERE / "FROZEN_FUNNEL_RUNS.jsonl").write_text(
        "".join(json.dumps(x) + "\n" for x in runs_out))
    return report


if __name__ == "__main__":
    rep = main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OBS)
    for phys, P in rep["physics"].items():
        print("==", phys, "runs", P["runs"])
        for row in P["funnel"]:
            print("  %-26s proven %5d  unmeasured %5d  n/a %5d  p=%s loss=%s %s" % (
                row["step"], row["runs_proven"], row["runs_not_measured"],
                row["runs_not_applicable"], row.get("transition_p"), row.get("absolute_loss"),
                row.get("status", "")))
        print("  events", P["event_totals"])
