"""Regression tests for 409 conflict diagnostics (charter 2026-09-04, Task 2).

The improvement: a conflict now names the field AND both values, so a producer
diagnoses it without querying the substrate. What must NOT change: the status
code, the message prefix, fail-closed behaviour, and the no-overwrite rule.
These tests pin all four.

Run:  python tests/test_conflict_diagnostics.py     (exit 0 = all pass)
"""
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db as ewdb          # noqa: E402
from ew.client import CFG          # noqa: E402

B = f"http://127.0.0.1:{CFG['port']}/api/v1"
H = {"Authorization": f"Bearer {CFG['machine_tokens']['M1']}",
     "X-Prometheus-Machine": "M1", "X-Prometheus-Agent": "regress-conflict"}
FAILS = []

ENC = "TESTFIX-CONFLICT-DIAG-0001"
RUN = "TESTFIX-CONFLICTRUN-0001"
H1 = "sha256:" + "a1" * 32
E1 = "evt_" + "a1" * 12


def check(name, cond, detail):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")
    if not cond:
        FAILS.append(name)


def post(path, body):
    return requests.post(f"{B}/{path}", headers=H, json=body, timeout=60)


def base(**kw):
    return dict({"encounter_id": ENC, "run_id": RUN, "sfe_entry_hash": H1,
                 "sfe_event_id": E1, "world_id": "TESTFIX-WORLD-0002",
                 "outcome": "committed", "namespace": "test"}, **kw)


def stored_outcome():
    conn = ewdb.connect()
    try:
        with ewdb.dict_cur(conn) as cur:
            cur.execute("SELECT outcome FROM ew.fossil_encounters WHERE "
                        "encounter_id=%s AND run_key=%s", (ENC, RUN))
            r = cur.fetchone()
            return r["outcome"] if r else None
    finally:
        conn.close()


def main():
    first = post("fossil/encounters", base())
    check("baseline_write_accepted", first.status_code == 200,
          f"HTTP {first.status_code} {first.json().get('status')}")

    # identical replay stays a 200 duplicate: enrichment must not turn
    # idempotent retries into conflicts
    again = post("fossil/encounters", base())
    check("identical_replay_still_200_duplicate",
          again.status_code == 200 and
          again.json().get("status") == "duplicate_identical",
          f"HTTP {again.status_code} {again.json().get('status')}")

    # the conflict itself
    conf = post("fossil/encounters", base(outcome="DIFFERENT-OUTCOME"))
    detail = conf.json().get("detail", "") if conf.status_code == 409 else conf.text
    check("conflict_status_unchanged", conf.status_code == 409,
          f"HTTP {conf.status_code}")
    check("conflict_prefix_unchanged",
          detail.startswith("conflict_existing_row_differs:"),
          f"detail starts: {detail[:45]!r}")
    check("conflict_names_field", "outcome(" in detail, f"detail={detail[:120]}")
    check("conflict_reports_stored_value", "stored=committed" in detail,
          f"detail={detail[:120]}")
    check("conflict_reports_submitted_value",
          "submitted=DIFFERENT-OUTCOME" in detail, f"detail={detail[:120]}")

    # fail-closed: the stored row is untouched by the rejected write
    check("no_overwrite_on_conflict", stored_outcome() == "committed",
          f"stored outcome after conflict = {stored_outcome()!r}")

    # long values are truncated so a huge payload cannot bloat the error
    longv = "X" * 500
    lc = post("fossil/encounters", base(outcome=longv))
    ld = lc.json().get("detail", "")
    check("long_values_truncated",
          lc.status_code == 409 and "..." in ld and len(ld) < 400,
          f"detail length {len(ld)}, truncated={'...' in ld}")

    # anchors report values too
    wc = post("fossil/worlds", {"world_id": "TESTFIX-WORLD-0002",
                                "seed_root": "999999", "namespace": "test"})
    wd = wc.json().get("detail", "") if wc.status_code == 409 else wc.text
    check("world_anchor_conflict_reports_values",
          wc.status_code == 409 and "seed_root(" in wd and "submitted=999999" in wd,
          f"HTTP {wc.status_code} {wd[:110]}")

    # batch conflicts keep their own prefix and carry values
    bc = post("fossil/encounters/batch",
              {"encounters": [base(outcome="BATCH-DIFFERENT")]})
    bd = bc.json().get("detail", "") if bc.status_code == 409 else bc.text
    check("batch_conflict_reports_values",
          bc.status_code == 409 and
          bd.startswith("conflict_existing_rows_differ:") and
          "stored=committed" in bd,
          f"HTTP {bc.status_code} {bd[:130]}")

    # every refusal is still durably recorded
    conn = ewdb.connect()
    try:
        with ewdb.dict_cur(conn) as cur:
            cur.execute("SELECT count(*) n FROM ew.write_log WHERE accepted=false "
                        "AND agent='regress-conflict' AND reject_reason LIKE "
                        "'conflict_existing_row%%'")
            n = cur.fetchone()["n"]
    finally:
        conn.close()
    check("refusals_recorded_in_write_log", n >= 2,
          f"{n} conflict refusals logged for this agent")

    print(json.dumps({"failures": FAILS, "all_pass": not FAILS}))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
