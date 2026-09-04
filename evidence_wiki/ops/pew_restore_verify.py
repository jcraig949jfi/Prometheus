"""Restore a PEW dump into a scratch database and PROVE it, mechanically.

"pg_restore returned 0" is not proof. This restores into a throwaway database
and compares it against the live one row-for-row on the things that matter,
including the full provenance chain of a named evidence record.

    python ops/pew_restore_verify.py                    # newest dump
    python ops/pew_restore_verify.py --dump <path>
    python ops/pew_restore_verify.py --keep-scratch     # quarantine, no drop

The scratch database is dropped afterwards unless --keep-scratch. It never
shares a name with the live database, and nothing here writes to the live
database (read-only comparisons).
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
sys.path.insert(0, str(HERE / "ops"))

import psycopg2                                   # noqa: E402
import psycopg2.extras                            # noqa: E402
from pew_backup import PGBIN, DEFAULT_DIR, cfg, env_with_pw, newest  # noqa: E402

# The first real end-to-end Harmonia evidence. Its chain is the acceptance
# test for any restore: if this cannot be walked, the backup is worthless.
CHAIN_EVIDENCE = os.environ.get("PEW_CHAIN_EVIDENCE", "E-dbe8c504b8cc")


def conn_to(dbname):
    c = cfg()
    return psycopg2.connect(host=c["db_host"], dbname=dbname, user=c["db_user"],
                            password=c["db_password"])


def q(conn, sql, args=()):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, args)
        return [dict(r) for r in cur.fetchall()]


def admin(sql):
    c = cfg()
    cn = psycopg2.connect(host=c["db_host"], dbname="postgres",
                          user=c["db_user"], password=c["db_password"])
    cn.autocommit = True
    with cn.cursor() as cur:
        cur.execute(sql)
    cn.close()


def table_counts(conn):
    rows = q(conn, "SELECT table_name FROM information_schema.tables "
                   "WHERE table_schema='ew' AND table_type='BASE TABLE' "
                   "ORDER BY table_name")
    out = {}
    for r in rows:
        t = r["table_name"]
        out[t] = q(conn, f"SELECT count(*) n FROM ew.{t}")[0]["n"]
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
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=None)
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--keep-scratch", action="store_true")
    a = ap.parse_args()
    dump = Path(a.dump) if a.dump else newest(Path(a.dir))
    if not dump or not dump.exists():
        raise SystemExit("no dump to verify")
    c = cfg()
    scratch = "pew_restore_check_" + time.strftime("%Y%m%d%H%M%S")
    assert scratch != c["db_name"]

    report = {"dump": str(dump), "scratch_db": scratch,
              "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    t0 = time.time()
    admin(f'CREATE DATABASE "{scratch}"')
    try:
        r = subprocess.run(
            [str(PGBIN / "pg_restore.exe"), "-h", c["db_host"], "-U",
             c["db_user"], "-d", scratch, "--no-owner", "--no-privileges",
             str(dump)], env=env_with_pw(c), capture_output=True, text=True)
        report["pg_restore_rc"] = r.returncode
        report["pg_restore_stderr_tail"] = (r.stderr or "").strip()[-400:]
        report["restore_seconds"] = round(time.time() - t0, 1)

        live, rest = conn_to(c["db_name"]), conn_to(scratch)
        lt, rt = table_counts(live), table_counts(rest)
        missing = sorted(set(lt) - set(rt))
        differing = {t: {"live": lt[t], "restored": rt.get(t)}
                     for t in lt if rt.get(t) != lt[t]}
        report["tables_live"] = len(lt)
        report["tables_restored"] = len(rt)
        report["tables_missing_in_restore"] = missing
        report["tables_with_differing_counts"] = differing
        report["total_rows_live"] = sum(lt.values())
        report["total_rows_restored"] = sum(rt.values())

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

        report["VERDICT"] = ("RESTORE_VERIFIED" if (
            report["pg_restore_rc"] == 0 and not missing and not differing
            and report["chain_identical"] and report["samples_identical"]
            and lc.get("found")) else "RESTORE_NOT_VERIFIED")
    finally:
        if a.keep_scratch:
            report["scratch_disposition"] = f"QUARANTINED as {scratch} (drop manually)"
        else:
            admin(f'DROP DATABASE IF EXISTS "{scratch}"')
            report["scratch_disposition"] = "dropped"

    man_path = dump.with_suffix(".manifest.json")
    if man_path.exists():
        man = json.loads(man_path.read_text(encoding="utf-8"))
        man["verified_restore"] = {
            "verdict": report["VERDICT"], "at": report["started"],
            "chain_evidence": CHAIN_EVIDENCE,
            "chain_identical": report["chain_identical"],
            "total_rows": report["total_rows_restored"]}
        man_path.write_text(json.dumps(man, indent=1), encoding="utf-8")

    out = HERE / "ops" / "restore_verification.json"
    out.write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if not k.startswith(("chain_", "samples_"))
                      or k in ("chain_identical", "samples_identical",
                               "chain_evidence_id")}, indent=1, default=str))
    return 0 if report["VERDICT"] == "RESTORE_VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
