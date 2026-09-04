"""PEW backup: dump, hash, manifest, rotate (charter 2026-09-04, Task 1).

The interpretation layer is the only copy of what Prometheus BELIEVES about
its history -- SFE holds only what happened. Append-only protects against
overwrite, not against a dead disk. This is the durability path.

    python ops/pew_backup.py                 # dump + hash + manifest + rotate
    python ops/pew_backup.py --verify-only   # re-hash the newest dump
    python ops/pew_backup.py --dir <path>    # override destination

Custom format (-Fc): compressed, selective-restore capable, and the format
pg_restore expects. Owner/privilege noise is excluded so a restore works into
a scratch database owned by anyone.
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

PGBIN = Path(os.environ.get("PGBIN", r"C:\Program Files\PostgreSQL\17\bin"))
DEFAULT_DIR = Path(os.environ.get("PEW_BACKUP_DIR", r"F:\PrometheusBackups\pew"))
KEEP = int(os.environ.get("PEW_BACKUP_KEEP", "14"))   # rotation depth


def cfg():
    return json.loads((HERE / "config.json").read_text(encoding="utf-8"))


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


def dump(dest_dir: Path):
    c = cfg()
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
        "dump_file": str(out),
        "source_db": f"{c['db_user']}@{c['db_host']}/{c['db_name']}",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "format": "custom (-Fc) --no-owner --no-privileges",
        "pg_dump_version": subprocess.run(
            [str(PGBIN / "pg_dump.exe"), "--version"], capture_output=True,
            text=True).stdout.strip(),
        "bytes": out.stat().st_size,
        "sha256": digest,
        "dump_seconds": secs,
        "restore_command":
            f'"{PGBIN / "pg_restore.exe"}" -h {c["db_host"]} -U {c["db_user"]} '
            f'-d <TARGET_DB> --no-owner --no-privileges "{out}"',
        "verified_restore": None,   # set by pew_restore_verify.py
    }
    (out.with_suffix(".manifest.json")).write_text(
        json.dumps(man, indent=1), encoding="utf-8")
    return man


def rotate(dest_dir: Path, keep=KEEP):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir)

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

    man = dump(d)
    man["rotated_out"] = rotate(d)
    print(json.dumps(man, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
