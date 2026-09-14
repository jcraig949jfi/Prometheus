#!/usr/bin/env python3
"""Committed experiments that no observation ever followed — the scar a stall
leaves in the ledger.

    python deploy/orphaned_commits.py [--db <path>] [--since-hours N] [--json]

WHY THIS EXISTS. Backlog A6: when `BEGIN IMMEDIATE` exceeds its lock wait the
engine cannot record its own failure, because recording needs the very lock that
just failed. The hash chain is silent precisely when the engine is what broke.

But the engine CAN see the SCAR. A run that committed an experiment and then
died before writing its observation leaves a committed experiment with no
observation — and reading that is a read done LATER, not a write done at failure
time, so the lock that defeated A6 does not defeat this. The failure is
unrecordable; its consequence is queryable.

IT REPORTS; IT DOES NOT CLASSIFY. My first cut split these into "orphaned" and
"legitimately pending" on whether the world still had outstanding work -- and
got a KNOWN answer wrong: Vivarium's five confirmed-abandoned runs all came back
"pending", because each world still holds a QUEUED work item with no claimant.
Having work is not evidence of progress, and whether such an item will ever be
claimed is a fact about the PRODUCER's register, not about this ledger.

So the engine states what it can see -- committed, unobserved, with the work
state and age beside it -- and leaves the verdict to whoever holds the register.
That is the same boundary A6 draws: the engine can show the scar, it cannot
diagnose the wound. A detector that guesses the producer's intent would be
confidently wrong in exactly the cases that matter.

WHAT IT IS FOR, CONCRETELY. Vivarium's 2026-09-11 stall left five
committed-but-unobserved experiments its register could not name. When those
rules are re-issued the engine will hold TWO experiments for each — one
abandoned, one real — so anything counting experiments per rule rather than
reading the fossil record double-counts exactly those. This LISTS the candidates
with their exp_ids so a register holder can decide which to exclude; it does not
decide for them.

READ ONLY. Opens the ledger `mode=ro` and writes nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time

DEFAULT_DB = r"D:\Prometheus-data\sfe\engine.db"   # moved off the HDD 2026-09-12 (C9)

#: Work states that mean a run may still legitimately produce its observation.
OUTSTANDING = ("QUEUED", "CLAIMED", "RUNNING", "RETRYABLE")


def scan(db: str, since_hours: float | None):
    cx = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True,
                         timeout=60)
    cx.row_factory = sqlite3.Row
    try:
        now = time.time()
        cutoff = 0 if since_hours is None else now - since_hours * 3600
        rows = cx.execute(
            "SELECT e.exp_id, e.world_id, e.created_ts, e.spec_hash "
            "FROM experiments e "
            "WHERE e.committed_seq IS NOT NULL AND e.created_ts >= ? "
            "  AND NOT EXISTS (SELECT 1 FROM observations o "
            "                  WHERE o.exp_id = e.exp_id) "
            "ORDER BY e.created_ts DESC", (cutoff,)).fetchall()
        q = ",".join("?" * len(OUTSTANDING))
        found = []
        for r in rows:
            wi = cx.execute(
                "SELECT status, claimed_by, updated_ts FROM work_items "
                "WHERE world_id=? AND status IN (%s)" % q,
                (r["world_id"],) + OUTSTANDING).fetchall()
            found.append({
                "exp_id": r["exp_id"], "world_id": r["world_id"],
                "created": time.strftime("%Y-%m-%dT%H:%M:%S",
                                         time.localtime(r["created_ts"])),
                "age_hours": round((now - r["created_ts"]) / 3600.0, 1),
                "spec_hash": r["spec_hash"],
                "outstanding_work": [
                    {"status": w["status"],
                     "claimed_by": w["claimed_by"],
                     "idle_hours": round((now - w["updated_ts"]) / 3600.0, 1)}
                    for w in wi],
                "unclaimed_work": sum(1 for w in wi
                                      if w["claimed_by"] is None)})
        committed = cx.execute(
            "SELECT COUNT(*) FROM experiments WHERE committed_seq IS NOT NULL "
            "AND created_ts >= ?", (cutoff,)).fetchone()[0]
        return {"db": os.path.abspath(db), "committed_experiments": committed,
                "committed_without_observation": len(rows),
                "_verdict": "NOT CLASSIFIED -- deciding abandoned vs pending "
                            "needs the producer's register, which is the "
                            "authority on whether a queued item will ever be "
                            "claimed",
                "found": found}
    finally:
        cx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--since-hours", type=float, default=None,
                    help="only experiments created in the last N hours")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=15)
    a = ap.parse_args()

    if not os.path.exists(a.db):
        print("no such ledger: %s" % a.db, file=sys.stderr)
        return 2
    r = scan(a.db, a.since_hours)

    print("COMMITTED BUT UNOBSERVED -- the scar a stall leaves (read only)")
    print("=" * 74)
    print("  ledger                        %s" % r["db"])
    print("  committed experiments         %d" % r["committed_experiments"])
    print("  ... with NO observation       %d"
          % r["committed_without_observation"])
    print()
    print("  NOT CLASSIFIED. Whether one of these is abandoned or still")
    print("  progressing is a fact about the PRODUCER's register, not about")
    print("  this ledger -- an unclaimed QUEUED item looks identical either")
    print("  way from here. Join on exp_id to decide.")
    print()
    if not r["found"]:
        print("  none in range.")
    else:
        print("  %-28s %-19s %6s  outstanding work"
              % ("exp_id", "created", "age_h"))
        for o in r["found"][:a.limit]:
            w = o["outstanding_work"]
            desc = "none" if not w else "%d (%d unclaimed, idle %.1fh)" % (
                len(w), o["unclaimed_work"],
                max(x["idle_hours"] for x in w))
            print("    %-26s %-19s %5.1f  %s"
                  % (o["exp_id"][:26], o["created"], o["age_hours"], desc))
        if len(r["found"]) > a.limit:
            print("    ... and %d more" % (len(r["found"]) - a.limit))
    print()
    print("  On RE-ISSUE the engine holds TWO experiments for that spec -- one")
    print("  abandoned, one real -- so counting experiments per rule rather")
    print("  than reading the fossil record double-counts exactly these.")
    if a.json:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "ORPHANED_COMMITS.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(r, indent=2) + "\n")
        print(json.dumps(r, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
