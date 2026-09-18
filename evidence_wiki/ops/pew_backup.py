"""PEW backup: dump, hash, manifest, rotate (charter 2026-09-04, Task 1;
O2 of MNE-D1, operator ruling 2026-09-17: an M2-OWNED nightly dump of the
CANONICAL cluster over the LAN, with the source cluster's identity attested
before a byte is written).

The interpretation layer is the only copy of what Prometheus BELIEVES about
its history -- SFE holds only what happened. Append-only protects against
overwrite, not against a dead disk. This is the durability path.

    python ops/pew_backup.py                 # dump + hash + manifest + rotate
    python ops/pew_backup.py --verify-only   # re-hash the newest dump
    python ops/pew_backup.py --dir <path>    # override destination

Resolution (no drive letter in code):
    source host     EW_DB_HOST > config.local.json canonical_db_host >
                    config.json db_host        (ew.db.load_config precedence)
    destination     PEW_BACKUP_DIR > config.local.json backup_dir >
                    the 2026-09-04 host default (kept so M1 keeps working)
    retention       PEW_BACKUP_KEEP > config.local.json backup_keep > 14

The source MUST be the environment named by PROMETHEUS_ENV (default
prometheus-canonical) by pg_control_system() identity; a dump of the wrong
cluster is refused, not labelled. Custom format (-Fc): compressed,
selective-restore capable, and the format pg_restore expects. Owner and
privilege noise is excluded so a restore works into a scratch database on
ANOTHER cluster owned by anyone (that is the O2 restore target).

State and alerts: derived/backup_state.json carries last_success,
last_attempt, consecutive_failures; a failure posts one comms report to the
accountable seat (the state file is the alarm if comms is down). The M2
watchdog reads the state file's age and reports a MISSED backup.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))     # comms.identity (the environment registry)
from ew import db as ewdb          # noqa: E402
from ew import workspace           # noqa: E402

PGBIN = Path(os.environ.get("PGBIN", r"C:\Program Files\PostgreSQL\17\bin"))
STATE = HERE / "derived" / "backup_state.json"
ACCOUNTABLE_SEAT = "Mnemosyne"


def cfg():
    """env > config.local.json > config.json, exactly as the service resolves
    its own connection. `canonical_db_host` (untracked) names the store on a
    host that is not the database host, e.g. M2 backing up M1."""
    c = ewdb.load_config()
    if not os.environ.get("EW_DB_HOST") and c.get("canonical_db_host"):
        c["db_host"] = c["canonical_db_host"]
    return c


def backup_dir(explicit=None):
    if explicit:
        return Path(explicit)
    env = os.environ.get("PEW_BACKUP_DIR")
    if env:
        return Path(env)
    c = ewdb.load_config()
    if c.get("backup_dir"):
        return Path(c["backup_dir"])
    return Path(r"F:\PrometheusBackups\pew")      # 2026-09-04 M1 host default


def keep_n():
    env = os.environ.get("PEW_BACKUP_KEEP")
    if env:
        return int(env)
    return int(ewdb.load_config().get("backup_keep") or 14)


DEFAULT_DIR = backup_dir()
KEEP = keep_n()


def sha256_file(p: Path, chunk=1 << 20):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def env_with_pw(c):
    e = dict(os.environ)
    e["PGPASSWORD"] = c["db_password"]
    return e


def source_identity(c, environment=None):
    """Attest the SOURCE cluster before dumping: pg_control_system()
    identity against comms/environments.json for PROMETHEUS_ENV. Refuses
    (raises) on a mismatch -- a backup of the fork labelled canonical would
    be worse than no backup. Returns the identity and a cheap inventory
    (schemas, base-table count, ew row totals) the restore compares."""
    import psycopg2
    from comms import identity as _ident
    environment = environment or os.environ.get("PROMETHEUS_ENV", "prometheus-canonical")
    cn = psycopg2.connect(host=c["db_host"], dbname=c["db_name"],
                          user=c["db_user"], password=c["db_password"],
                          connect_timeout=20)
    try:
        v = _ident.require(cn, environment)
        with cn.cursor() as cur:
            cur.execute("SELECT version()")
            server_version = cur.fetchone()[0]
            cur.execute("SELECT pg_database_size(current_database())")
            db_bytes = cur.fetchone()[0]
            cur.execute("SELECT table_schema, count(*) FROM information_schema.tables "
                        "WHERE table_type='BASE TABLE' AND table_schema NOT IN "
                        "('pg_catalog','information_schema') GROUP BY 1 ORDER BY 1")
            tables_by_schema = {s: n for s, n in cur.fetchall()}
            cur.execute("SELECT last_value FROM ew.canonical_revision_seq")
            canonical_revision = cur.fetchone()[0]
            cur.execute("SELECT (SELECT count(*) FROM ew.write_log), "
                        "(SELECT count(*) FROM ew.fossil_encounters), "
                        "(SELECT count(*) FROM comms.messages)")
            wl, fe, cm = cur.fetchone()
    finally:
        cn.close()
    return {"environment": environment,
            "db_system_id": str(v["observed"]["db_system_id"]),
            "db_name": v["observed"]["db_name"],
            "server_version": server_version, "db_bytes": db_bytes,
            "base_tables_by_schema": tables_by_schema,
            "base_tables_total": sum(tables_by_schema.values()),
            "ew_canonical_revision": canonical_revision,
            "ew_write_log_rows": wl, "ew_fossil_encounters_rows": fe,
            "comms_messages_rows": cm}


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_success": None, "last_attempt": None, "consecutive_failures": 0,
                "last_dump": None, "last_error": None}


def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1, default=str), encoding="utf-8")


def alert(subject, body):
    """Visible alarm: one comms report to the accountable seat. Best effort;
    the state file on disk is the alarm of record if comms is unreachable."""
    try:
        p = HERE / "derived" / "backup_alert_body.md"
        p.write_text(body, encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "comms", "post", "--from", ACCOUNTABLE_SEAT,
                            "--to", ACCOUNTABLE_SEAT, "--kind", "report",
                            "--subject", subject, "--body-file", str(p)],
                           cwd=str(HERE.parent), capture_output=True, text=True, timeout=120)
        return r.returncode == 0
    except Exception:
        return False


def dump(dest_dir: Path):
    c = cfg()
    ident = source_identity(c)                    # refuses the wrong cluster
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = dest_dir / f"prometheus_fire_{stamp}.dump"
    cmd = [str(PGBIN / "pg_dump.exe"), "-h", c["db_host"], "-U", c["db_user"],
           "-d", c["db_name"], "-Fc", "--no-owner", "--no-privileges",
           "-f", str(out)]
    t0 = time.time()
    r = subprocess.run(cmd, env=env_with_pw(c), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"pg_dump FAILED rc={r.returncode}: {r.stderr[:500]}")
    secs = round(time.time() - t0, 1)
    digest = sha256_file(out)
    man = {
        "backup_id": f"pewbk-{stamp}-{digest[:12]}",
        "dump_file": str(out),
        "source_db": f"{c['db_user']}@{c['db_host']}/{c['db_name']}",
        "source_identity": ident,
        "backup_host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME"),
        "backup_machine": os.environ.get("PROMETHEUS_MACHINE"),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "format": "custom (-Fc) --no-owner --no-privileges",
        "pg_dump_version": subprocess.run(
            [str(PGBIN / "pg_dump.exe"), "--version"], capture_output=True,
            text=True).stdout.strip(),
        "bytes": out.stat().st_size,
        "sha256": digest,
        "dump_seconds": secs,
        "retention_keep": KEEP,
        "workspace": WORKSPACE,
        "restore_command":
            f'"{PGBIN / "pg_restore.exe"}" -h <TARGET_HOST> -U {c["db_user"]} '
            f'-d <TARGET_DB> --no-owner --no-privileges "{out}"',
        "verified_restore": None,   # set by pew_restore_verify.py
    }
    (out.with_suffix(".manifest.json")).write_text(
        json.dumps(man, indent=1, default=str), encoding="utf-8")
    return man


def rotate(dest_dir: Path, keep=None):
    keep = keep or KEEP
    dumps = sorted(dest_dir.glob("prometheus_fire_*.dump"))
    removed = []
    for old in dumps[:-keep] if len(dumps) > keep else []:
        removed.append(old.name)
        old.unlink()
        m = old.with_suffix(".manifest.json")
        if m.exists():
            m.unlink()
    return removed


def newest(dest_dir: Path):
    d = sorted(dest_dir.glob("prometheus_fire_*.dump"))
    return d[-1] if d else None


WORKSPACE = workspace.assert_not_canonical("back up PEW")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()
    d = backup_dir(a.dir)

    if a.verify_only:
        p = newest(d)
        if not p:
            raise SystemExit("no dump found")
        man = json.loads(p.with_suffix(".manifest.json").read_text(encoding="utf-8"))
        now = sha256_file(p)
        ok = now == man["sha256"]
        print(json.dumps({"dump": str(p), "sha256_recorded": man["sha256"],
                          "sha256_now": now, "intact": ok}, indent=1))
        return 0 if ok else 1

    st = load_state()
    st["last_attempt"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        man = dump(d)
        man["rotated_out"] = rotate(d)
    except BaseException as e:            # SystemExit from pg_dump included
        st["consecutive_failures"] = int(st.get("consecutive_failures") or 0) + 1
        st["last_error"] = str(e)[:400]
        save_state(st)
        alert(f"PEW BACKUP FAILED on {os.environ.get('PROMETHEUS_MACHINE') or 'this host'}: "
              f"{st['consecutive_failures']} consecutive; last_success {st.get('last_success')}",
              f"pew_backup.py failed at {st['last_attempt']}\n\n{st['last_error']}\n\n"
              f"state: {STATE}\n")
        print(json.dumps({"BACKUP": "FAILED", "error": st["last_error"]}, indent=1))
        return 1
    st.update({"last_success": man["created_at"], "consecutive_failures": 0,
               "last_dump": man["dump_file"], "last_backup_id": man["backup_id"],
               "last_sha256": man["sha256"], "last_bytes": man["bytes"],
               "source_db_system_id": man["source_identity"]["db_system_id"],
               "last_error": None})
    save_state(st)
    print(json.dumps(man, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
