"""Bounded productive-liveness survey over the heartbeat estate.

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

Reads agora.agent_heartbeats and classifies every row with the same
derive_health() the Pronoia loop now uses, so the survey and the
instrument cannot drift apart.

It is a READER. It writes nothing to any database, and it makes no claim
about levels it cannot observe: L1 (eligibility), L4 (artifact) and L5
(consumption) are NOT inferable from a heartbeat table, and this script
prints them as UNOBSERVED rather than guessing. The per-specimen L1-L5
findings in the accompanying report were established by hand, each with
its own command, and are recorded there rather than manufactured here.

    python roles/Pronoia/science/liveness_survey.py [--json OUT]

Requires EW_DB_HOST to point at the host holding the canonical Postgres
when run off M1.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from productive_liveness import Health, WorkEvidence, derive_health  # noqa: E402

#: Cadence assumed when a row does not declare one. One hour is the most
#: common intended cadence in MONITORS.md. Rows whose real cadence is slower
#: are therefore judged slightly harshly; that is stated rather than tuned
#: away, and it never affects the two verdicts that matter here
#: (NO_WORK_OBSERVED and INCOHERENT are cadence-independent).
ASSUMED_CADENCE_SEC = 3600.0

FRESH_SEC = 3600.0  # a heartbeat older than this is not evidence of liveness


def survey(conn) -> dict:
    cur = conn.cursor()
    cur.execute(
        "select agent_name, machine, status, last_heartbeat, connected_at,"
        " last_work_attempt_at, last_work_success_at, health, pid"
        " from agora.agent_heartbeats order by last_heartbeat desc nulls last"
    )
    now = datetime.now(timezone.utc)
    rows = []
    for (name, machine, status, hb, conn_at, attempt, success, health, pid) in cur.fetchall():
        age_h = (now - hb).total_seconds() / 3600.0 if hb else None
        ev = WorkEvidence(started_at=conn_at, last_heartbeat_at=hb,
                          last_attempt_at=attempt, last_success_at=success)
        try:
            derived = derive_health(now, ev, cadence_sec=ASSUMED_CADENCE_SEC)
        except Exception as e:
            derived = "UNCOMPUTABLE(%s)" % type(e).__name__

        # L0: does the heartbeat itself evidence a live process RIGHT NOW?
        l0 = "FRESH" if (hb and (now - hb).total_seconds() <= FRESH_SEC) else "STALE"
        # L2/L3: is there any work evidence at all?
        l2 = "PRESENT" if attempt else "ABSENT"
        l3 = "PRESENT" if success else "ABSENT"

        rows.append({
            "agent": name, "machine": machine,
            "status_claimed": status,
            "heartbeat_age_h": round(age_h, 1) if age_h is not None else None,
            "L0_process": l0,
            "L2_attempt_evidence": l2,
            "L3_success_evidence": l3,
            "health_stored": health,
            "health_derived": derived,
            # Not inferable from this table. Never guessed.
            "L1_eligibility": "UNOBSERVED",
            "L4_artifact": "UNOBSERVED",
            "L5_consumption": "UNOBSERVED",
            "pid": pid,
        })

    total = len(rows)
    claims_online = [r for r in rows if (r["status_claimed"] or "").lower() == "online"]
    online_but_stale = [r for r in claims_online if r["L0_process"] == "STALE"]
    no_work_evidence = [r for r in rows if r["L2_attempt_evidence"] == "ABSENT"
                        and r["L3_success_evidence"] == "ABSENT"]
    incoherent = [r for r in rows if r["health_derived"] == Health.INCOHERENT]
    productive = [r for r in rows if r["health_derived"] == Health.PRODUCTIVE]

    return {
        "generated_utc": now.isoformat(),
        "assumed_cadence_sec": ASSUMED_CADENCE_SEC,
        "totals": {
            "rows": total,
            "claim_status_online": len(claims_online),
            "claim_online_but_heartbeat_stale": len(online_but_stale),
            "no_work_evidence_at_all": len(no_work_evidence),
            "derived_incoherent": len(incoherent),
            "derived_productive": len(productive),
        },
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", help="write the full result to this path")
    args = ap.parse_args()

    from comms.api import connect
    result = survey(connect())

    t = result["totals"]
    print("Productive-liveness survey  %s" % result["generated_utc"])
    print("  rows in agora.agent_heartbeats            %4d" % t["rows"])
    print("  rows whose status says 'online'           %4d" % t["claim_status_online"])
    print("  ... of those, heartbeat older than 1 h    %4d   <-- the label outlives the process"
          % t["claim_online_but_heartbeat_stale"])
    print("  rows with NO work evidence of any kind    %4d" % t["no_work_evidence_at_all"])
    print("  rows whose work evidence is incoherent    %4d" % t["derived_incoherent"])
    print("  rows derived PRODUCTIVE                   %4d" % t["derived_productive"])
    print()
    print("  %-22s %-9s %-8s %-6s %-6s %-18s" %
          ("agent", "claimed", "hb age", "L2", "L3", "derived"))
    for r in result["rows"]:
        print("  %-22s %-9s %6sh  %-6s %-6s %-18s" % (
            r["agent"][:22], (r["status_claimed"] or "?")[:9],
            r["heartbeat_age_h"], r["L2_attempt_evidence"][:6],
            r["L3_success_evidence"][:6], r["health_derived"]))

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=str)
            fh.flush()
        print("\n  wrote %s" % args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
