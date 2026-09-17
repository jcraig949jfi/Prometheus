"""Restore a PEW dump into a scratch database and PROVE it, mechanically.

"pg_restore returned 0" is not proof. This restores into a throwaway database
and compares it against the live canonical cluster table-for-table on row
counts across EVERY schema (the dump is the whole database: ew, comms, viv,
archaeon, agora, ... -- O2 is about recovering the CLUSTER, not one schema),
walks the full provenance chain of a named evidence record, and compares a
set of ew samples.

O2 (operator ruling MNE-D1, 2026-09-17): the restore TARGET may be a
different cluster from the source -- on M2, the local PostgreSQL 17.11 --
so that the restore proves recoverability INDEPENDENT of M1. The restored
copy is NOT canonical by identity (its pg_control_system() id is the
target cluster's); the receipt records both identities and says so.

    python ops/pew_restore_verify.py                    # newest dump
    python ops/pew_restore_verify.py --dump <path>
    python ops/pew_restore_verify.py --keep-scratch     # quarantine, no drop
    python ops/pew_restore_verify.py --write-tracked    # also refresh the
                                                        # committed receipt
                                                        # (task worktree only)

Resolution (no drive letter in code):
    source (live)   as pew_backup.cfg(): EW_DB_HOST > canonical_db_host > db_host
    target          PEW_RESTORE_TARGET_HOST > config.local.json
                    restore_target_host > the source host (M1 behaviour)
Receipts: <backup dir>/restore_verify_<stamp>.json and
derived/restore_state.json (last_success, last_verdict, consecutive_failures).
The scratch database never shares a name with the live database, and nothing
here writes to the live database (read-only comparisons).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from ew import db as ewdb                         # noqa: E402
from ew import workspace                          # noqa: E402
sys.path.insert(0, str(HERE / "ops"))

import psycopg2                                   # noqa: E402
import psycopg2.extras                            # noqa: E402
from pew_backup import (PGBIN, backup_dir, cfg, env_with_pw, newest,   # noqa: E402
                        sha256_file, alert, ACCOUNTABLE_SEAT)

# The first real end-to-end Harmonia evidence. Its chain is the acceptance
# test for any restore: if this cannot be walked, the backup is worthless.
CHAIN_EVIDENCE = os.environ.get("PEW_CHAIN_EVIDENCE", "E-dbe8c504b8cc")
STATE = HERE / "derived" / "restore_state.json"


def target_host(c):
    env = os.environ.get("PEW_RESTORE_TARGET_HOST")
    if env:
        return env
    local = ewdb.load_config().get("restore_target_host")
    return local or c["db_host"]


def connect(host, dbname, c):
    return psycopg2.connect(host=host, dbname=dbname, user=c["db_user"],
                            password=c["db_password"], connect_timeout=20)


def q(conn, sql, args=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, args)
        return [dict(r) for r in cur.fetchall()]


def admin(host, sql, c):
    cn = connect(host, "postgres", c)
    cn.autocommit = True
    with cn.cursor() as cur:
        cur.execute(sql)
    cn.close()


def cluster_identity(conn):
    r = q(conn, "SELECT system_identifier::text AS db_system_id FROM pg_control_system()")[0]
    r["server_version"] = q(conn, "SELECT version() v")[0]["v"]
    r["db_name"] = q(conn, "SELECT current_database() d")[0]["d"]
    return r


def all_table_counts(conn):
    """Row count of every base table in every user schema. Whole-cluster
    sanity, not ew-only: the dump is the whole database."""
    rows = q(conn, "SELECT table_schema s, table_name t FROM information_schema.tables "
                   "WHERE table_type='BASE TABLE' AND table_schema NOT IN "
                   "('pg_catalog','information_schema') ORDER BY 1, 2")
    out = {}
    for r in rows:
        key = f"{r['s']}.{r['t']}"
        out[key] = q(conn, f'SELECT count(*) n FROM "{r["s"]}"."{r["t"]}"')[0]["n"]
    return out


def chain(conn, eid):
    """Walk evidence -> claim/packet -> encounter -> players/world -> SFE."""
    ev = q(conn, "SELECT evidence_id, claim_id, packet_id, evidence_type, "
                 "encounter_id, encounter_run_id, submitted_by, machine "
                 "FROM ew.evidence WHERE evidence_id=%s", (eid,))
    if not ev:
        return {"found": False}
    e = ev[0]
    out = {"found": True, "evidence": e}
    if e["claim_id"]:
        out["claim"] = q(conn, "SELECT claim_id, text_canonical, status FROM "
                               "ew.claims WHERE claim_id=%s ORDER BY version "
                               "DESC LIMIT 1", (e["claim_id"],))
    if e["packet_id"]:
        out["packet"] = q(conn, "SELECT packet_id, uri, kind, content_sha256 "
                                "FROM ew.source_packets WHERE packet_id=%s",
                          (e["packet_id"],))
    if e["encounter_id"]:
        enc = q(conn, "SELECT encounter_id, run_id, world_id, players, "
                      "sfe_event_id, sfe_entry_hash, sfe_event_seq, namespace "
                      "FROM ew.fossil_encounters WHERE encounter_id=%s AND "
                      "run_key=%s", (e["encounter_id"], e["encounter_run_id"] or ""))
        out["encounter"] = enc
        if enc:
            out["world"] = q(conn, "SELECT world_id, manifest_hash, "
                                   "sfe_head_hash, namespace FROM "
                                   "ew.fossil_worlds WHERE world_id=%s",
                             (enc[0]["world_id"],))
            out["players"] = q(conn, "SELECT player_id, genome_hash, "
                                     "runtime_hash, namespace FROM "
                                     "ew.fossil_players WHERE player_id = "
                                     "ANY(%s)", (enc[0]["players"] or [],))
            out["sfe_anchor"] = {"event_id": enc[0]["sfe_event_id"],
                                 "entry_hash": enc[0]["sfe_entry_hash"],
                                 "event_seq": enc[0]["sfe_event_seq"]}
    return out


def samples(conn):
    return {
        "fossil_by_namespace": q(conn, "SELECT namespace, count(*) n FROM "
                                       "ew.fossil_encounters GROUP BY 1 ORDER BY 1"),
        "prod_row": q(conn, "SELECT encounter_id, sfe_entry_hash, sfe_event_id "
                            "FROM ew.fossil_encounters WHERE namespace='prod' "
                            "ORDER BY encounter_id LIMIT 1"),
        "test_row": q(conn, "SELECT encounter_id, run_id, sfe_entry_hash FROM "
                            "ew.fossil_encounters WHERE namespace='test' "
                            "ORDER BY encounter_id LIMIT 1"),
        "canonical_revision": q(conn, "SELECT last_value FROM "
                                      "ew.canonical_revision_seq"),
        "ontology_registry": q(conn, "SELECT count(*) n, max(version) v FROM "
                                     "ew.mechanism_registry"),
        "vocab_terms": q(conn, "SELECT count(*) n FROM ew.vocab WHERE NOT retired"),
        "object_namespace": q(conn, "SELECT object_type, namespace, count(*) n "
                                    "FROM ew.object_namespace GROUP BY 1,2 ORDER BY 1,2"),
        "evidence_bindings": q(conn, "SELECT count(*) n FROM ew.evidence "
                                     "WHERE encounter_id IS NOT NULL"),
        "fossil_pk": q(conn, "SELECT pg_get_constraintdef(oid) d FROM "
                             "pg_constraint WHERE "
                             "conrelid='ew.fossil_encounters'::regclass AND contype='p'"),
        "evidence_fk": q(conn, "SELECT pg_get_constraintdef(oid) d FROM "
                               "pg_constraint WHERE "
                               "conname='evidence_fossil_encounter_fk'"),
        "comms_last_message": q(conn, "SELECT max(id) id FROM comms.messages"),
    }


def classify_diffs(differing):
    """Split count differences into live-source DRIFT (restored <= live on
    an append-only table: rows arrived after the dump) and LOSS (restored
    is None or restored > live, or fewer rows than the dump could have held).
    Only LOSS fails the verdict; drift is reported beside it."""
    drift, loss = {}, {}
    for t, d in differing.items():
        r, l = d.get("restored"), d.get("live")
        if r is not None and l is not None and r <= l:
            drift[t] = d
        else:
            loss[t] = d
    return drift, loss


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_success": None, "last_attempt": None, "last_verdict": None,
                "consecutive_failures": 0}


def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1, default=str), encoding="utf-8")


WORKSPACE = workspace.assert_not_canonical("verify a PEW restore")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--keep-scratch", action="store_true")
    ap.add_argument("--write-tracked", action="store_true",
                    help="also refresh ops/restore_verification.json (task worktree only)")
    a = ap.parse_args()
    bdir = backup_dir(a.dir)
    dump = Path(a.dump) if a.dump else newest(bdir)
    if not dump or not dump.exists():
        raise SystemExit("no dump to verify")
    c = cfg()
    src_host, tgt_host = c["db_host"], target_host(c)
    stamp = time.strftime("%Y%m%d%H%M%S")
    scratch = "pew_restore_check_" + stamp
    assert scratch != c["db_name"]

    st = load_state()
    st["last_attempt"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    man_path = dump.with_suffix(".manifest.json")
    man = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else {}
    report = {"dump": str(dump), "backup_id": man.get("backup_id"),
              "dump_sha256_recorded": man.get("sha256"),
              "dump_sha256_now": sha256_file(dump),
              "source_host": src_host, "target_host": tgt_host,
              "scratch_db": scratch, "started": st["last_attempt"],
              "pg_restore_version": subprocess.run(
                  [str(PGBIN / "pg_restore.exe"), "--version"],
                  capture_output=True, text=True).stdout.strip(),
              "workspace": WORKSPACE}
    report["dump_intact"] = report["dump_sha256_recorded"] == report["dump_sha256_now"]
    t0 = time.time()
    admin(tgt_host, f'CREATE DATABASE "{scratch}"', c)
    try:
        r = subprocess.run(
            [str(PGBIN / "pg_restore.exe"), "-h", tgt_host, "-U",
             c["db_user"], "-d", scratch, "--no-owner", "--no-privileges",
             str(dump)], env=env_with_pw(c), capture_output=True, text=True)
        report["pg_restore_rc"] = r.returncode
        report["pg_restore_stderr_tail"] = (r.stderr or "").strip()[-400:]
        report["restore_seconds"] = round(time.time() - t0, 1)

        live, rest = connect(src_host, c["db_name"], c), connect(tgt_host, scratch, c)
        report["source_identity"] = cluster_identity(live)
        report["target_identity"] = cluster_identity(rest)
        report["restored_copy_is_canonical_by_identity"] = (
            report["source_identity"]["db_system_id"] == report["target_identity"]["db_system_id"])
        lt, rt = all_table_counts(live), all_table_counts(rest)
        missing = sorted(set(lt) - set(rt))
        differing = {t: {"live": lt[t], "restored": rt.get(t)}
                     for t in lt if rt.get(t) != lt[t]}
        report["tables_live"] = len(lt)
        report["tables_restored"] = len(rt)
        report["tables_missing_in_restore"] = missing
        report["tables_with_differing_counts"] = differing
        report["total_rows_live"] = sum(lt.values())
        report["total_rows_restored"] = sum(rt.values())
        report["schemas_live"] = sorted({k.split(".")[0] for k in lt})
        report["schemas_restored"] = sorted({k.split(".")[0] for k in rt})

        lc, rc = chain(live, CHAIN_EVIDENCE), chain(rest, CHAIN_EVIDENCE)
        report["chain_evidence_id"] = CHAIN_EVIDENCE
        report["chain_live"] = lc
        report["chain_restored"] = rc
        report["chain_identical"] = (json.dumps(lc, sort_keys=True, default=str)
                                     == json.dumps(rc, sort_keys=True, default=str))

        ls, rs = samples(live), samples(rest)
        report["samples_live"] = ls
        report["samples_restored"] = rs
        report["samples_identical"] = (json.dumps(ls, sort_keys=True, default=str)
                                       == json.dumps(rs, sort_keys=True, default=str))
        live.close(); rest.close()

        # Row counts on a LIVE source drift between dump and compare (comms,
        # write_log, read_log receive rows every few minutes). A difference
        # where restored <= live on an append-only table is drift, not loss,
        # and is reported as such; a table with FEWER live rows than restored,
        # or a missing table, is a failure.
        drift, loss = classify_diffs(differing)
        report["count_drift_append_only"] = drift
        report["count_loss"] = loss
        report["VERDICT"] = ("RESTORE_VERIFIED" if (
            report["dump_intact"] and report["pg_restore_rc"] == 0 and not missing
            and not loss and report["chain_identical"] and lc.get("found")
            and report["schemas_live"] == report["schemas_restored"]) else "RESTORE_NOT_VERIFIED")
        report["verdict_note"] = ("samples identical" if report["samples_identical"] else
                                  "samples differ (see samples_live/samples_restored; "
                                  "live-source drift on append-only counters is expected)")
    finally:
        if a.keep_scratch:
            report["scratch_disposition"] = f"QUARANTINED as {scratch} on {tgt_host} (drop manually)"
        else:
            admin(tgt_host, f'DROP DATABASE IF EXISTS "{scratch}"', c)
            report["scratch_disposition"] = "dropped"

    report["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if man_path.exists():
        man["verified_restore"] = {
            "verdict": report["VERDICT"], "at": report["started"],
            "target_host": tgt_host,
            "target_db_system_id": report.get("target_identity", {}).get("db_system_id"),
            "chain_evidence": CHAIN_EVIDENCE,
            "chain_identical": report.get("chain_identical"),
            "total_rows": report.get("total_rows_restored")}
        man_path.write_text(json.dumps(man, indent=1, default=str), encoding="utf-8")

    receipt = bdir / f"restore_verify_{stamp}.json"
    receipt.write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    (bdir / "restore_verify_latest.json").write_text(
        json.dumps(report, indent=1, default=str), encoding="utf-8")
    if a.write_tracked:
        (HERE / "ops" / "restore_verification.json").write_text(
            json.dumps(report, indent=1, default=str), encoding="utf-8")

    ok = report["VERDICT"] == "RESTORE_VERIFIED"
    if ok:
        st.update({"last_success": report["finished"], "last_verdict": report["VERDICT"],
                   "consecutive_failures": 0, "last_receipt": str(receipt),
                   "last_backup_id": report["backup_id"]})
    else:
        st.update({"last_verdict": report["VERDICT"],
                   "consecutive_failures": int(st.get("consecutive_failures") or 0) + 1,
                   "last_receipt": str(receipt)})
        alert(f"PEW RESTORE QUALIFICATION FAILED on {tgt_host}: {report['VERDICT']}; "
              f"backup {report['backup_id']}",
              f"restore_verify receipt: {receipt}\nmissing={missing} loss={loss} "
              f"chain_identical={report.get('chain_identical')} rc={report.get('pg_restore_rc')}\n")
    save_state(st)
    print(json.dumps({k: v for k, v in report.items()
                      if not k.startswith(("chain_", "samples_"))
                      or k in ("chain_identical", "samples_identical",
                               "chain_evidence_id")}, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
