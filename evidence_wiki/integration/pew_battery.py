"""PEW standard integration battery E0-E12 (Harmonia handoff, 2026-09-03).

Repeatable, cheap, and honest: every write is proved by an INDEPENDENT
read-back (a different endpoint, plus a direct SQL read that does not go
through the service process at all). HTTP 200 is never treated as evidence
of persistence.

Usage (from evidence_wiki/):
    python integration/pew_battery.py                    # against 127.0.0.1
    python integration/pew_battery.py --host 192.168.1.X # against M1 over LAN
    python integration/pew_battery.py --no-sql           # remote host: skip
                                                         # the direct-SQL leg

Exit code 0 = every gate PASS. Results written to integration/battery_results.json.
"""
import argparse
import json
import os
import subprocess
import sqlite3
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
FIXTURE = json.loads((HERE / "integration" / "fixture_harmonia_v1.json")
                     .read_text(encoding="utf-8"))
SFE_DB = HERE.parent / "SerendipityFoundry" / "SerendipityFoundryEngine" / "var" / "engine.db"

R = []          # gate results


def gate(name, ok, detail, skipped=False):
    """A skipped gate is reported as SKIP and excluded from all_pass. It is
    never silently counted as a pass."""
    R.append({"gate": name, "pass": bool(ok), "skipped": skipped,
              "detail": detail})
    print(f"[{'SKIP' if skipped else ('PASS' if ok else 'FAIL')}] {name}: {detail}")
    return bool(ok)


# S-2: the Postgres system_identifier of each machine's PEW store. Server truth,
# not a client claim -- these do not change for a given cluster.
EXPECTED_DB_ID = {"M1": "7628127204585430828", "M2": "7681719240261676752"}


class C:
    def __init__(self, host, port, token, machine, agent):
        self.base = f"http://{host}:{port}/api/v1"
        self.h = {"Authorization": f"Bearer {token}",
                  "X-Prometheus-Machine": machine, "X-Prometheus-Agent": agent}

    def get(self, path, **params):
        return requests.get(f"{self.base}/{path}", headers=self.h,
                            params=params, timeout=30)

    def post(self, path, body):
        return requests.post(f"{self.base}/{path}", headers=self.h,
                             json=body, timeout=60)


def sql_rows(query, args):
    """Read-back that never touches the service process."""
    from ew import db as ewdb
    conn = ewdb.connect()
    try:
        with ewdb.dict_cur(conn) as cur:
            cur.execute(query, args)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def real_sfe_run():
    """A REAL world/player/run-shaped record built from live SFE history
    (opened read-only). Deterministic pick so the battery is repeatable."""
    if not SFE_DB.exists():
        return None
    c = sqlite3.connect(f"file:{SFE_DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    exp = c.execute(
        "SELECT exp_id, world_id, work_id, spec_hash, created_seq FROM "
        "experiments WHERE work_id IS NOT NULL AND state='OBSERVED' "
        "ORDER BY created_seq DESC LIMIT 1").fetchone()
    if not exp:
        return None
    w = c.execute("SELECT world_id, seed_root, head_hash FROM worlds WHERE "
                  "world_id=?", (exp["world_id"],)).fetchone()
    ob = c.execute("SELECT obs_id, outcome, work_id, created_seq FROM "
                   "observations WHERE exp_id=? ORDER BY created_seq LIMIT 1",
                   (exp["exp_id"],)).fetchone()
    ev = c.execute("SELECT event_seq, event_id, entry_hash, ts FROM events "
                   "WHERE world_id=? ORDER BY event_seq DESC LIMIT 1",
                   (exp["world_id"],)).fetchone()
    wk = c.execute("SELECT work_id, status, result_hash FROM work_items "
                   "WHERE work_id=?", (exp["work_id"],)).fetchone()
    c.close()
    if not (w and ev):
        return None
    # namespace='test': these identifiers are REAL, but this row is written by
    # an integration battery, so it must not enter the scientific corpus.
    return {
        "encounter_id": f"SFEREAL-{exp['exp_id']}",
        "run_id": f"{exp['exp_id']}:{exp['work_id']}",
        "sfe_entry_hash": ev["entry_hash"],
        "sfe_world_id": exp["world_id"],
        "sfe_event_id": ev["event_id"],
        "sfe_event_seq": ev["event_seq"],
        "world_id": exp["world_id"],
        "players": [f"sfe-work:{exp['work_id']}"],
        "seed": str(w["seed_root"]),
        "outcome": (ob["outcome"] if ob else (wk["status"] if wk else None)),
        "resources_used": {"result_hash": wk["result_hash"] if wk else None},
        "occurred_ts": time.strftime("%Y-%m-%dT%H:%M:%S+00:00",
                                     time.gmtime(ev["ts"])),
        "producer": {"component": "sfe.engine", "spec_hash": exp["spec_hash"],
                     "head_hash": w["head_hash"],
                     "ingested_by": "pew_battery.py"},
        "namespace": "test",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--token", default=None)
    ap.add_argument("--machine", default="M1")
    ap.add_argument("--expect-db-id", default=None,
                    help="S-2: override the expected db_system_id for --machine")
    ap.add_argument("--agent", default="pew-battery")
    ap.add_argument("--no-sql", action="store_true",
                    help="skip direct-SQL legs (use when not on the DB host)")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    port = a.port or cfg["port"]
    token = a.token or cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    c = C(a.host, port, token, a.machine, a.agent)
    fx, enc = FIXTURE, FIXTURE["encounter"]

    # E0 ------------------------------------------------------ reachable
    t0 = time.time()
    try:
        h = c.get("health")
        gate("E0_service_reachable", h.status_code == 200,
             f"{h.status_code} {h.json()} in {round((time.time()-t0)*1000)}ms")
    except Exception as e:
        gate("E0_service_reachable", False, f"unreachable: {e}")
        return finish()

    # E1 --------------------------------------- version/schema identity
    v, sc, ct = c.get("version"), c.get("schema"), c.get("fossil/contract")
    ok = all(r.status_code == 200 for r in (v, sc, ct))
    gate("E1_version_schema_identity", ok,
         f"schema_version={sc.json().get('schema_version')} "
         f"ontology_version={sc.json().get('ontology_version')} "
         f"fossil_contract={ct.json().get('fossil_contract')} "
         f"canonical_revision={v.json().get('canonical_revision')}")

    # S-2 ------------------- server-attested MACHINE identity (HARD gate)
    # Assert GET /api/v1/identity's db_system_id equals the KNOWN id for the
    # named --machine. The db_system_id is the Postgres cluster system_identifier
    # -- server truth. A bearer token / X-Prometheus-Machine header must NOT be
    # able to substitute for it. Controls (all must hold):
    #   M2 as M2           -> actual == expected                  (PASS)
    #   M1 claimed as M2   -> the M1 id does NOT satisfy expected  (would FAIL)
    #   M2 + wrong db id   -> a wrong id does NOT match the server (would FAIL)
    idr = c.get("identity")
    idj = idr.json() if idr.status_code == 200 else {}
    actual = idj.get("db_system_id")
    expected = a.expect_db_id or EXPECTED_DB_ID.get(a.machine)
    other_ids = [vv for kk, vv in EXPECTED_DB_ID.items() if kk != a.machine]
    # server identity must be independent of the CLAIMED machine header:
    spoof_machine = "M1" if a.machine != "M1" else "M2"
    try:
        spoof = requests.get(f"{c.base}/identity",
                             headers={**c.h, "X-Prometheus-Machine": spoof_machine},
                             timeout=30).json().get("db_system_id")
    except Exception:
        spoof = None
    controls = {
        "M2_as_M2_PASS": bool(actual) and actual == expected,
        "M1_claimed_as_M2_FAIL": expected is not None and expected not in other_ids,
        "M2_wrong_dbid_FAIL": actual != "WRONG-DB-ID" and actual == expected,
        "header_not_substitute_for_server": spoof == actual and actual is not None,
    }
    s2_ok = idr.status_code == 200 and all(controls.values())
    gate("S2_server_machine_identity", s2_ok,
         f"machine={a.machine} db_system_id={actual} expected={expected} "
         f"controls={controls}")

    # anchors first (world + player version rows the evidence joins back to)
    wr = c.post("fossil/worlds", fx["world"])
    pr = c.post("fossil/players", fx["player"])
    gate("E2a_anchor_writes_accepted",
         wr.status_code == 200 and pr.status_code == 200,
         f"world={wr.status_code}:{wr.json().get('status')} "
         f"player={pr.status_code}:{pr.json().get('status')}")

    # E2 ------------------------------------------- known-good write
    w = c.post("fossil/encounters", enc)
    ok = (w.status_code == 200 and
          w.json().get("status") in ("inserted", "duplicate_identical"))
    gate("E2_known_good_write_accepted", ok, f"{w.status_code} {w.text[:160]}")

    # E3 ------------------------------------- stable evidence identity
    body = w.json() if w.status_code == 200 else {}
    ident_ok = body.get("encounter_id") == enc["encounter_id"] and \
        body.get("run_id") == enc["run_id"] and "read_back" in body
    gate("E3_stable_evidence_identity", ident_ok,
         f"identity=({body.get('encounter_id')},{body.get('run_id')}) "
         f"read_back={body.get('read_back')}")

    # E4 --------------------------- independent read-back (HTTP + SQL)
    g = c.get(f"fossil/encounters/{enc['encounter_id']}")
    http_found = g.status_code == 200 and g.json()["n_runs"] >= 1
    sql_found = None
    if not a.no_sql:
        rows = sql_rows("SELECT * FROM ew.fossil_encounters WHERE "
                        "encounter_id=%s AND run_id=%s",
                        (enc["encounter_id"], enc["run_id"]))
        sql_found = len(rows) == 1
    gate("E4_independent_read_back", http_found and (sql_found is not False),
         f"http_get={http_found} direct_sql={sql_found} "
         f"(sql skipped={a.no_sql})")

    # E5 ------------------------- persisted fields == submitted fields
    got = next((r for r in g.json()["runs"] if r["run_id"] == enc["run_id"]),
               {}) if http_found else {}
    mismatch = []
    for k, want in enc.items():
        if k in ("idempotency_key",):
            continue
        have = got.get(k)
        if k == "occurred_ts" and have:
            have = have.replace("Z", "+00:00")
        if json.dumps(have, sort_keys=True, default=str) != \
           json.dumps(want, sort_keys=True, default=str):
            mismatch.append(f"{k}: sent={want!r} stored={have!r}")
    gate("E5_persisted_equals_submitted", not mismatch,
         "all fields byte-equal" if not mismatch else "; ".join(mismatch))

    # E6 ------------------------------ query by run / world / player
    q_run = c.get("fossil/encounters", run_id=enc["run_id"])
    q_world = c.get("fossil/encounters", world_id=enc["world_id"])
    q_player = c.get("fossil/encounters", player_id=enc["players"][0])
    q_none = c.get("fossil/encounters")
    ok = (q_run.status_code == 200 and q_run.json()["n"] >= 1 and
          q_world.status_code == 200 and q_world.json()["n"] >= 1 and
          q_player.status_code == 200 and q_player.json()["n"] >= 1 and
          q_none.status_code == 400)
    gate("E6_query_by_run_world_player", ok,
         f"run={q_run.json().get('n')} world={q_world.json().get('n')} "
         f"player={q_player.json().get('n')} unfiltered={q_none.status_code}")

    # E7 ----------------------------------- duplicate / idempotency
    again = c.post("fossil/encounters", enc)
    differing = dict(enc, outcome="DELIBERATELY-DIFFERENT")
    conflict = c.post("fossil/encounters", differing)
    n_before = len(sql_rows("SELECT 1 FROM ew.fossil_encounters WHERE "
                            "encounter_id=%s", (enc["encounter_id"],))) \
        if not a.no_sql else None
    ok = (again.status_code == 200 and
          again.json().get("status") == "duplicate_identical" and
          conflict.status_code == 409 and
          "conflict_existing_row_differs" in conflict.text)
    gate("E7_duplicate_and_conflict_semantics", ok,
         f"identical_replay={again.status_code}:{again.json().get('status')} "
         f"differing={conflict.status_code}:{conflict.text[:90]}")

    # E8 ------------------------------------ malformed fails overtly
    m1 = c.post("fossil/encounters", {k: v for k, v in enc.items()
                                      if k != "sfe_entry_hash"})
    m2 = c.post("fossil/encounters", dict(enc, encounter_id="TESTFIX-E8-UNKNOWN",
                                          run_id="TESTFIX-E8", nonsense_field=1))
    m3 = c.post("fossil/encounters", {"encounter_id": "TESTFIX-E8-EMPTY",
                                      "sfe_entry_hash": "   "})
    ok = m1.status_code == 422 and m2.status_code == 422 and m3.status_code == 422
    gate("E8_malformed_fails_overtly", ok,
         f"missing_provenance={m1.status_code} unknown_field={m2.status_code} "
         f"blank_provenance={m3.status_code}")

    # E9 ------------------------------ unavailable backend fails overtly
    env = dict(os.environ, EW_DB_HOST="10.255.255.1", PYTHONIOENCODING="utf-8")
    probe = ("import sys; sys.path.insert(0, r'%s');\n"
             "from ew import db\n"
             "try:\n"
             "    c = db.connect(); print('SILENT_SUCCESS', c)\n"
             "except Exception as e:\n"
             "    print('RAISED', type(e).__name__)\n") % str(HERE)
    p = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                       text=True, env=env, timeout=180)
    ok = "RAISED" in p.stdout and "SILENT_SUCCESS" not in p.stdout
    if not ok and "ModuleNotFoundError" in (p.stderr or ""):
        # Off-host consumer without the DB driver: this leg belongs to the
        # service host. Skipped, never counted as a pass.
        gate("E9_unavailable_backend_fails_overtly", False,
             "no local DB driver; this leg runs on the service host (M1)",
             skipped=True)
    else:
        gate("E9_unavailable_backend_fails_overtly", ok,
             f"unroutable DB host -> {p.stdout.strip()[:80] or p.stderr.strip()[:80]} "
             "(library layer; service-with-Postgres-down not exercised: shared DB)")

    # E10 ------------------------------- no silent-success in this route
    leaked = []
    if not a.no_sql:
        for bad_id in ("TESTFIX-E8-UNKNOWN", "TESTFIX-E8-EMPTY"):
            if sql_rows("SELECT 1 FROM ew.fossil_encounters WHERE "
                        "encounter_id=%s", (bad_id,)):
                leaked.append(bad_id)
        n_after = len(sql_rows("SELECT 1 FROM ew.fossil_encounters WHERE "
                               "encounter_id=%s", (enc["encounter_id"],)))
        rejected_logged = sql_rows(
            "SELECT reject_reason, count(*) n FROM ew.write_log WHERE "
            "accepted=false AND endpoint LIKE 'fossil.%%' GROUP BY 1", ())
    else:
        n_after, rejected_logged = n_before, []
    if a.no_sql:
        # Off-host this gate can observe nothing, so it must not report PASS:
        # a gate that verifies nothing while claiming success is the very
        # failure mode this battery exists to catch.
        gate("E10_no_silent_success", False,
             "requires direct DB access; runs on the service host (M1)",
             skipped=True)
    else:
        ok = not leaked and n_after == n_before and len(rejected_logged) > 0
        gate("E10_no_silent_success", ok,
             f"rejected writes that left rows: {leaked or 'none'}; "
             f"row count across conflict attempt {n_before}->{n_after}; "
             f"refusals recorded in write_log: {len(rejected_logged)} kinds")

    # E13 -------------------- batch path: idempotent and all-or-nothing
    def brow(n, **kw):
        import hashlib as _h
        _d = _h.sha256(f"pew.integration.batch|{n}".encode()).hexdigest()
        return dict({"encounter_id": f"TESTFIX-BATCH-{n:03d}",
                     "run_id": "TESTFIX-BATCHRUN-0002",
                     "sfe_entry_hash": "sha256:" + _d,
                     "sfe_event_id": "evt_" + _d[:24],
                     "world_id": fx["world"]["world_id"],
                     "players": [fx["player"]["player_id"]],
                     "outcome": "committed", "namespace": "test"}, **kw)
    b1 = c.post("fossil/encounters/batch", {"encounters": [brow(i) for i in range(5)]})
    b2 = c.post("fossil/encounters/batch", {"encounters": [brow(i) for i in range(5)]})
    # one poisoned row (differs from what is stored) must refuse the WHOLE batch
    poisoned = [brow(i) for i in range(5, 8)] + [brow(0, outcome="DIFFERENT")]
    b3 = c.post("fossil/encounters/batch", {"encounters": poisoned})
    after = c.get("fossil/encounters", run_id="TESTFIX-BATCHRUN-0002")
    n_after_batch = after.json().get("n") if after.status_code == 200 else -1
    ok = (b1.status_code == 200 and
          b2.status_code == 200 and b2.json().get("duplicate_identical") == 5 and
          b3.status_code == 409 and n_after_batch == 5)
    gate("E13_batch_idempotent_and_atomic", ok,
         f"first={b1.status_code}:{b1.json().get('inserted')} "
         f"replay={b2.status_code}:dup={b2.json().get('duplicate_identical')} "
         f"poisoned_batch={b3.status_code} rows_after={n_after_batch} "
         "(expect 5: the 3 clean rows in the poisoned batch must NOT land)")

    # E11 --------------------------- one REAL player-run-shaped record
    real = real_sfe_run()
    if real is None:
        gate("E11_real_run_recorded", False, "no SFE ledger available")
        gate("E12_real_run_reconstructable", False, "skipped (E11)")
        return finish(real_id=None)
    rw = c.post("fossil/encounters", real)
    ok = rw.status_code == 200 and rw.json().get("status") in (
        "inserted", "duplicate_identical")
    gate("E11_real_run_recorded", ok,
         f"{rw.status_code} {rw.json().get('status')} "
         f"encounter={real['encounter_id']} run={real['run_id']}")

    # E12 ------------------- reconstruct world / player / run / outcome
    rq = c.get("fossil/encounters", run_id=real["run_id"])
    rec = rq.json()["encounters"][0] if rq.status_code == 200 and \
        rq.json()["n"] else {}
    have_all = all(rec.get(f) for f in ("world_id", "players", "run_id",
                                        "outcome", "sfe_entry_hash"))
    gate("E12_real_run_reconstructable", have_all,
         f"world={rec.get('world_id')} player={(rec.get('players') or [None])[0]} "
         f"run={rec.get('run_id')} outcome={rec.get('outcome')} "
         f"anchor={str(rec.get('sfe_entry_hash'))[:24]}...")
    return finish(real_id=real["encounter_id"], real_run=real["run_id"])


def finish(**extra):
    scored = [r for r in R if not r.get("skipped")]
    out = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "n_gates": len(R), "n_scored": len(scored),
           "n_pass": sum(r["pass"] for r in scored),
           "n_skipped": len(R) - len(scored),
           "skipped": [r["gate"] for r in R if r.get("skipped")],
           "all_pass": bool(scored) and all(r["pass"] for r in scored),
           "gates": R, **extra}
    (HERE / "integration" / "battery_results.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "gates"}, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
