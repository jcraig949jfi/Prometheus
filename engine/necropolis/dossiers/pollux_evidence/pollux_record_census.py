"""Pollux record census: every prior verdict about Pollux on the tree, in
date order, with the citation verified (file exists, line contains the
quoted text), plus the daemon's commit history and the list of artifacts
that every prior verdict rests on but that are absent from this tree.

The purpose is LAW-N17 portability: a fresh adjudicator must be able to
find each certificate and see which ones contradict each other. Nothing
here is interpreted; the dossier does that.

Static, offline, read-only. git is used read-only (git log on one path).
Writes only pollux_record_census_result.json.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
OUT = HERE / "pollux_record_census_result.json"

# (date, path, needle, what the record asserts, kind)
RECORDS = [
    ("2026-05-25", "pivot/charon_swarm_diminishing_returns_2026-05-25.md",
     "Was 100% deterministic; auto-growth patch (today)",
     "PRIMARY OBSERVATION during the run: per-pair output is deterministic; v0.6 settle/replace patch is the response", "primary_observation"),
    ("2026-05-25", "pivot/charon_swarm_diminishing_returns_2026-05-25.md",
     "POLLUX-* short-circuits with `stygian_pollux_survivor_loader_pending`",
     "PRIMARY OBSERVATION: the Stygian survivor path is a stub (E9, ~120 LOC, never built)", "primary_observation"),
    ("2026-05-27", "pivot/charon_swarm_2026-05-27.md",
     "pair=narrow_band_1.10_1.20_vs_1.30_1.50 kp=pollux_sign_flips_under_normalization",
     "PRIMARY OBSERVATION: 21 ticks, last summary; a verdict string identical to today's rescan", "primary_observation"),
    ("2026-05-28", "pivot/agent_roster_2026-05-28.md",
     "| Pollux | M2 | tool | active | 28m | 43 ev |",
     "PRIMARY OBSERVATION: 28-min cadence, 43 events by 05-28", "primary_observation"),
    ("2026-06-10", "aporia/docs/program_audit_2026-06-10.md",
     "Pollux produced real signal: 39 PROMOTED correlations surviving mean-spacing",
     "CERTIFICATE: 'real signal' (39 PROMOTED / 86 REJECTED) with no null and no check of the raw leg", "interpretation"),
    ("2026-06-10", "aporia/docs/program_audit_2026-06-10.md",
     "39 PROMOTED pairs (real, scale-artifact-controlled)",
     "CERTIFICATE repeated as a program-level result", "interpretation"),
    ("2026-06-07", "roles/Ergon/GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md",
     "pollux gold claims are all-False templated",
     "PRIMARY OBSERVATION by the only training consumer: every Pollux row labelled False; slice 1.0 -> 0.395 without it", "primary_observation"),
    ("2026-06-22", "pivot/REASSESSMENT_2026-06-22_consolidated.md",
     "keep Hecate+Pollux+Moros; Pollux = real signal",
     "CERTIFICATE: LIVE (reduced), 'real signal'", "interpretation"),
    ("2026-06-23", "pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md",
     "| 34 | **Pollux** | M2 | REVIVE |",
     "CERTIFICATE: REVIVE, 'Real signal'", "interpretation"),
    ("2026-06-24", "pivot/COMPONENT_DOSSIERS_2026-06-24.md",
     "ALL 286 ledger rows have corr_raw=1.0",
     "PRIMARY OBSERVATION (from the ledger, then present): the raw leg is constant; typed as tautology; RETIRE-after-HITL", "primary_observation"),
    ("2026-06-24", "pivot/COMPONENT_DOSSIERS_2026-06-24.md",
     "The Ergon Learner has ZERO references to generator_id=pollux",
     "CERTIFICATE, FALSE on its own tree: ergon/learner/greedy/sources.py source='pollux' landed 7e38227ee 2026-06-10", "interpretation"),
    ("2026-06-24", "pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md",
     "correlates two *sorted* arrays",
     "CERTIFICATE: measurement bug; overturns the 06-22 keep", "interpretation"),
    ("2026-08-12", "charon/CHARON_SESSION_2026-08-12.md",
     "computes Pollux's statistic on sorted and on shuffled inputs and print both",
     "PRESCRIPTION for the tautology-verification script; not executed until pollux_instrument_null.py (this dossier)", "prescription"),
    ("2026-08-12", "aporia/docs/frontier_leverage_reassessment_2026-08-12.md",
     "tautology-verification pass** on Hecate / Pollux / Moros /",
     "PRESCRIPTION repeated as the immediate target", "prescription"),
    ("2026-08-20", "engine/queues/PROF_TRIAGE.jsonl",
     '"agent": "Pollux", "kind": "tool", "lifecycle": "active", "binding": "VACUOUS-NO-SOLVER"',
     "CERTIFICATE: not a solver (profiling triage); lifecycle still 'active' 82 days after the fleet halt", "interpretation"),
    ("2026-08-21", "engine/ledger/AGENT_AUTOPSIES.jsonl",
     '"agent_id": "Pollux", "autopsied": "2026-08-21", "by": "Aporia P69"',
     "CERTIFICATE (typed autopsy): LOW-BITS-PER-VERDICT-EMISSION; census 86/39/161; 'mechanically explains the Hecate MI null'; never mentions the corr_raw tautology already on record since 06-24", "interpretation"),
    ("2026-08-21", "engine/shadow/WORKLOG.jsonl",
     "Pollux kill_ledger per-pair distinct-outcome census printed in-pass",
     "PROVENANCE GAP: the P69 census was printed, not saved; the ledger it was computed over is absent from this tree", "provenance"),
    ("2026-08-21", "engine/shadow/WORKLOG.jsonl",
     "charon/agents/hecate/artifacts/gradient_archaeology_20260530T162054Z.md",
     "PROVENANCE GAP: P69's Hecate figure (0.0034 bits) is cited to an artifact path absent from this tree", "provenance"),
    ("2026-08-21", "engine/ledger/AUTOPSY_TAXONOMY.md",
     "each = 9 facts, emitted as 286 ledger rows + 286 artifacts",
     "CERTIFICATE (taxonomy cluster 2 LOW-BITS-EMISSION) built on P69", "interpretation"),
    ("2026-08-22", "engine/queues/BACKLOG.jsonl",
     '"id": "AUTOPSY-POLLUX"',
     "QUEUE: AUTOPSY-POLLUX DONE (P69 result copied into the queue row)", "queue"),
]

ABSENT = [
    "charon/agents/pollux/state/kill_ledger.jsonl",
    "charon/agents/pollux/state/pair_history.json",
    "charon/agents/pollux/state/settled_pairs.json",
    "charon/agents/pollux/state/candidate_pool_idx.json",
    "charon/agents/pollux/artifacts",
    "charon/agents/hecate/artifacts/gradient_archaeology_20260530T162054Z.md",
    "charon/agents/stygian/loaders/pollux_survivor.py",
    "charon/agents/pollux/tests",
]


def check(path, needle):
    p = REPO_ROOT / path
    if not p.exists():
        return {"found": False, "line": None, "error": "file_missing"}
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if needle in line:
            return {"found": True, "line": i}
    return {"found": False, "line": None}


def git_log(path):
    try:
        out = subprocess.run(
            ["git", "log", "--format=%H|%ad|%s", "--date=iso-strict", "--", path],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=110)
        return [dict(zip(("sha", "date", "subject"), l.split("|", 2)))
                for l in out.stdout.splitlines() if l.strip()]
    except Exception as e:
        return [{"error": "%s: %s" % (type(e).__name__, e)}]


def main():
    r = {"script": "pollux_record_census.py"}
    recs = []
    for date, path, needle, assertion, kind in RECORDS:
        c = check(path, needle)
        recs.append({"date": date, "path": path, "line": c.get("line"), "found": c["found"],
                     "needle": needle, "asserts": assertion, "kind": kind})
    r["records"] = sorted(recs, key=lambda x: x["date"])
    r["all_citations_found"] = all(x["found"] for x in recs)
    r["citations_not_found"] = [x for x in recs if not x["found"]]
    r["counts_by_kind"] = {k: sum(1 for x in recs if x["kind"] == k)
                           for k in ("primary_observation", "interpretation", "prescription", "provenance", "queue")}
    r["daemon_commits"] = git_log("charon/agents/pollux/daemon.py")
    r["pollux_dir_listing"] = sorted(p.name for p in (REPO_ROOT / "charon/agents/pollux").iterdir())
    r["absent_from_this_tree"] = {p: (REPO_ROOT / p).exists() for p in ABSENT}
    r["contradictions_on_record"] = [
        "06-10/06-22/06-23 'real signal' + REVIVE  vs  06-24 'measurement bug' + RETIRE: same ledger, no new data between them; the difference is that 06-24 looked at the raw leg.",
        "06-24 'Ergon Learner has ZERO references to generator_id=pollux'  vs  ergon/learner/greedy/sources.py (2026-06-10) and roles/Ergon/GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md: the Learner trained on all 286 rows.",
        "08-21 P69 types the grave as LOW-BITS-EMISSION and says the wiring 'worked - rows landed, Hecate consumed'  vs  Hecate's >=2-generator rule, under which no Pollux row can enter the cross-generator set regardless of how many bits it carries.",
        "08-21 P69 census 86/39/161 (54/56 per pair)  vs  deterministic replay of the v0.6 policy on today's data (15/15/256, 87/88): the on-tree code alone does not produce P69's numbers; ~22.6 h of v0.5 (no settle policy) and any short-circuit rows are unrecorded.",
        "08-20 PROF_TRIAGE lifecycle 'active'  vs  second-channel last row 2026-05-30 11:55 local.",
    ]
    OUT.write_text(json.dumps(r, indent=1) + "\n", encoding="ascii")
    print(json.dumps({k: r[k] for k in ("all_citations_found", "citations_not_found", "counts_by_kind",
                                         "daemon_commits", "pollux_dir_listing", "absent_from_this_tree")}, indent=1))


if __name__ == "__main__":
    main()
