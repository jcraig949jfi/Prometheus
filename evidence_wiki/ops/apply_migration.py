"""Apply one numbered PEW migration to the CANONICAL store, guarded and
receipted (order 2026-09-17 s4: idempotent/guarded execution, schema version
recorded, source and target revision recorded, backup receipt referenced,
restore path known before migration).

    python ops/apply_migration.py 014 --backup-id <pewbk-...> \
        --restore-receipt <path to restore_verify_*.json> [--dry-run]

Refuses when: the store is not the named environment (identity guard in
ew.db); the migration row already exists (prints it and exits 0: applying
twice is a no-op by construction, the SQL is IF NOT EXISTS throughout);
the named backup manifest does not exist or does not carry a
RESTORE_VERIFIED verdict (a migration without a proven restore path is an
act of faith). Writes ops/migration_receipts/<id>_<stamp>.json.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from ew import db as ewdb          # noqa: E402
from ew import workspace           # noqa: E402

WORKSPACE = workspace.assert_not_canonical("apply a PEW migration")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("migration", help="e.g. 014")
    ap.add_argument("--backup-id", required=True)
    ap.add_argument("--restore-receipt", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rehearsal", action="store_true",
                    help="target is a RESTORED COPY (PROMETHEUS_ENV=m2-rehearsal): skip the source==target identity check, mark the receipt")
    a = ap.parse_args()
    files = sorted((HERE / "migrations").glob(f"{a.migration}_*.sql"))
    if len(files) != 1:
        raise SystemExit(f"expected exactly one migrations/{a.migration}_*.sql, found {files}")
    sql_path = files[0]
    sql = sql_path.read_text(encoding="utf-8")
    sql_sha = hashlib.sha256(sql.replace("\r\n", "\n").encode()).hexdigest()

    rr = json.loads(Path(a.restore_receipt).read_text(encoding="utf-8"))
    if rr.get("VERDICT") != "RESTORE_VERIFIED":
        raise SystemExit(f"restore receipt verdict is {rr.get('VERDICT')!r}; refusing")
    if rr.get("backup_id") != a.backup_id:
        raise SystemExit(f"restore receipt is for {rr.get('backup_id')}, not {a.backup_id}; refusing")
    bdir = Path(os.environ.get("PEW_BACKUP_DIR") or ewdb.load_config().get("backup_dir") or "")
    manifests = list(bdir.glob("*.manifest.json")) if bdir else []
    man = None
    for m in manifests:
        try:
            j = json.loads(m.read_text(encoding="utf-8"))
        except Exception:
            continue
        if j.get("backup_id") == a.backup_id:
            man = j
    if man is None:
        raise SystemExit(f"no manifest for backup {a.backup_id} under {bdir}; refusing")

    conn = ewdb.connect()                          # identity guard runs here
    cur = conn.cursor()
    cur.execute("SELECT system_identifier::text FROM pg_control_system()")
    sysid = cur.fetchone()[0]
    if man["source_identity"]["db_system_id"] != sysid and not a.rehearsal:
        raise SystemExit("backup is of a different cluster than the target; refusing (use --rehearsal on a restored copy)")
    cur.execute("SELECT to_regclass('ew.schema_migrations')")
    have_table = cur.fetchone()[0] is not None
    if have_table:
        cur.execute("SELECT applied_at, applied_by, backup_id FROM ew.schema_migrations WHERE migration_id=%s", (a.migration,))
        row = cur.fetchone()
        if row:
            print(json.dumps({"migration": a.migration, "already_applied": True,
                              "applied_at": str(row[0]), "applied_by": row[1], "backup_id": row[2]}, indent=1))
            conn.close()
            return 0
    cur.execute("SELECT last_value FROM ew.canonical_revision_seq")
    rev_before = cur.fetchone()[0]
    receipt = {"migration": a.migration, "sql_file": str(sql_path.relative_to(HERE)), "sql_sha256": sql_sha,
               "target_db_system_id": sysid, "revision_before": rev_before,
               "backup_id": a.backup_id, "backup_sha256": man["sha256"], "backup_created_at": man["created_at"],
               "restore_receipt": str(a.restore_receipt), "restore_verdict": rr["VERDICT"],
               "restore_target_db_system_id": rr.get("target_identity", {}).get("db_system_id"),
               "applied_by": f"Mnemosyne @ {os.environ.get('COMPUTERNAME')}",
               "applied_from": f"{WORKSPACE['worktree_path']} @ {WORKSPACE['base_sha']} dirty={WORKSPACE['dirty']}",
               "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "dry_run": a.dry_run, "rehearsal": a.rehearsal,
               "environment": os.environ.get("PROMETHEUS_ENV", "prometheus-canonical")}
    if a.dry_run:
        print(json.dumps(receipt, indent=1)); conn.close(); return 0
    cur.execute(sql)
    cur.execute("UPDATE ew.schema_migrations SET applied_by=%s, applied_from=%s, revision_before=%s, "
                "backup_id=%s, restore_receipt=%s WHERE migration_id=%s",
                (receipt["applied_by"], receipt["applied_from"], rev_before, a.backup_id,
                 str(a.restore_receipt), a.migration))
    conn.commit()
    cur.execute("SELECT last_value FROM ew.canonical_revision_seq")
    receipt["revision_after"] = cur.fetchone()[0]
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='ew' ORDER BY 1")
    receipt["ew_tables_after"] = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='ew' AND table_name='typed_refs' ORDER BY ordinal_position")
    receipt["typed_refs_columns_after"] = [r[0] for r in cur.fetchall()]
    receipt["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    conn.close()
    out = HERE / "ops" / "migration_receipts"
    out.mkdir(exist_ok=True)
    p = out / f"{a.migration}_{time.strftime('%Y%m%dT%H%M%S')}.json"
    p.write_text(json.dumps(receipt, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k not in ("ew_tables_after", "typed_refs_columns_after")}, indent=1, default=str))
    print("receipt:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
