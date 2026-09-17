"""THE COORDINATED DEPLOY WINDOW for Vivarium (point release; operator Stage 3 /
implementation order s10-s12). Every step is a receipted, separately
runnable act; nothing here runs unless --confirm names the window. Order:

    1. backup      pg_dump of the PRODUCTION queue schema `viv` (schema-only
                   + data) to <data_dir>/backups/viv-<utc>.dump, sha256 recorded
    2. drafts      re-run migrations/drafts/check_drafts.py on a throwaway
                   schema (15 trigger cases) -- refuse the window if any fails
    3. promote     copy migrations/drafts/006..009 into migrations/ (the
                   deploy act; apply_migrations globs them from then on)
    4. migrate     viv.db.apply_migrations on `viv`: 006 (attempts/steps/
                   envelope + the release transition), 007 (backfill, UNKNOWN,
                   no steps), 008 (bundles/receipts/gates), 009 (outbox)
    5. verify      old rows: count and a sample of `viv.cli show` before ==
                   after (byte comparison of the JSON); attempts backfilled
                   == rows terminal at migration time; no steps fabricated
    6. advance     the pinned consumer worktree to --sha (prepare_m2.py
                   --advance; tests must have passed at that SHA)
    7. tasks       register VivariumOutboxDelivererM2 (5 min, DISABLED);
                   VivariumDeadmanM2 stays DISABLED until the restart step
    8. bootstrap   credentials for the role (viv.cli sfe-identity --ensure
                   against the descriptor's engine; refused if a client of
                   that name already exists on THIS ledger); PEW writer
                   registration is Mnemosyne's -- recorded as PENDING if absent
    9. restart     enable VivariumDeadmanM2 -> its first tick starts the
                   consumer from the pinned worktree; the consumer writes the
                   RESTART RECEIPT and REFUSES if the descriptor disagrees;
                   enable VivariumOutboxDelivererM2
   10. receipt     deploy receipt with every step's outcome and inputs

Rollback (s10): DROP the four tables (they hold nothing production-derived
until the consumer runs), restore the pinned worktree to the previous SHA,
re-disable the tasks; the backup from step 1 is the fallback for the queue
schema itself. Old rows are never modified by 006-009, so a rollback loses
nothing they held.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIVARIUM = HERE.parent
REPO = VIVARIUM.parent
DRAFTS = VIVARIUM / "migrations" / "drafts"
MIGRATIONS = VIVARIUM / "migrations"
PG_DUMP = os.environ.get("PG_DUMP", r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe")
DRAFT_FILES = ("006_execution_attempts_and_steps.sql", "007_backfill_attempts_reversible.sql",
               "008_bundles_receipts_gates.sql", "009_pew_outbox.sql")


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def step_backup(data_dir: Path, out: dict) -> bool:
    sys.path.insert(0, str(VIVARIUM))
    from viv import db as _db                                   # noqa: PLC0415
    cfg = _db.load_config()
    bdir = data_dir / "backups"
    bdir.mkdir(parents=True, exist_ok=True)
    target = bdir / ("viv-%s.dump" % _utc().replace(":", ""))
    env = dict(os.environ)
    if cfg.get("db_password"):
        env["PGPASSWORD"] = cfg["db_password"]                  # never printed, never written
    cmd = [PG_DUMP, "-h", cfg["db_host"], "-U", cfg["db_user"], "-d", cfg["db_name"], "-n", "viv",
           "-F", "c", "-f", str(target)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=1800)
    ok = r.returncode == 0 and target.exists() and target.stat().st_size > 0
    out["backup"] = {"ok": ok, "path": str(target), "bytes": target.stat().st_size if target.exists() else 0,
                     "sha256": _sha(target) if ok else None, "stderr": (r.stderr or "")[-300:]}
    return ok


def step_drafts(out: dict) -> bool:
    r = subprocess.run([sys.executable, str(DRAFTS / "check_drafts.py")], capture_output=True, text=True,
                       cwd=str(VIVARIUM), timeout=600)
    text = (r.stdout or "") + (r.stderr or "")
    ok = r.returncode == 0 and "BAD" not in text and "FAIL" not in text and text.count("  ok ") >= 15
    out["drafts"] = {"ok": ok, "ok_lines": text.count("  ok "), "tail": text[-600:]}
    return ok


def step_promote(out: dict) -> bool:
    rec = {}
    for name in DRAFT_FILES:
        src, dst = DRAFTS / name, MIGRATIONS / name
        if not dst.exists():
            shutil.copyfile(src, dst)
        rec[name] = {"sha256": _sha(dst), "same_as_draft": _sha(src) == _sha(dst)}
    out["promote"] = {"ok": all(v["same_as_draft"] for v in rec.values()), "files": rec}
    return out["promote"]["ok"]


def step_migrate(out: dict) -> bool:
    sys.path.insert(0, str(VIVARIUM))
    from viv import db as _db                                   # noqa: PLC0415
    conn = _db.connect()
    try:
        if _db.schema() != "viv":
            out["migrate"] = {"ok": False, "reason": "VIV_SCHEMA is not viv; the window migrates PRODUCTION only"}
            return False
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM viv.research_experiment_queue WHERE status IN ('completed','failed','cancelled')")
            terminal_before = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM viv.research_experiment_queue")
            rows_before = cur.fetchone()[0]
            # every old row, hashed over its PRE-migration columns (rehearse_window.py proved this on a copy)
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='viv' AND "
                        "table_name='research_experiment_queue' ORDER BY ordinal_position")
            old_cols = [c[0] for c in cur.fetchall()]
            proj = "SELECT experiment_id::text, md5(json_build_array(%s)::text) FROM viv.research_experiment_queue q" % (
                ", ".join('q."%s"' % c for c in old_cols))
            cur.execute(proj)
            before = dict(cur.fetchall())
        conn.rollback()
        applied = _db.apply_migrations(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM viv.execution_attempt")
            attempts = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM viv.execution_step")
            steps = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM viv.research_experiment_queue")
            rows_after = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM viv.execution_attempt WHERE termination->>'termination_reason' = 'UNKNOWN'")
            unknown = cur.fetchone()[0]
            cur.execute(proj)
            after = dict(cur.fetchall())
        conn.rollback()
        changed = sorted(e for e in before if before[e] != after.get(e))
        ok = (rows_before == rows_after and attempts == terminal_before and steps == 0 and unknown == attempts
              and not changed and set(before) == set(after))
        out["migrate"] = {"ok": ok, "applied": applied, "rows_before": rows_before, "rows_after": rows_after,
                          "terminal_rows": terminal_before, "attempts_backfilled": attempts,
                          "attempts_unknown_reason": unknown, "steps_fabricated": steps,
                          "old_rows_changed_over_old_columns": changed[:10], "old_columns": len(old_cols)}
        return ok
    finally:
        conn.close()


def step_verify_old_rows(out: dict, sample_ids: list) -> bool:
    """`viv.cli show` output for sampled old rows, compared to a pre-window
    capture (window.py --capture wrote it)."""
    cap = out.get("_capture") or {}
    rec = {}
    for eid in sample_ids:
        r = subprocess.run([sys.executable, "-m", "viv.cli", "show", eid], capture_output=True, text=True,
                           cwd=str(VIVARIUM), timeout=120)
        rec[eid] = {"same": cap.get(eid) == r.stdout, "captured": eid in cap}
    out["verify_old_rows"] = {"ok": all(v["same"] for v in rec.values()) if rec else None, "rows": rec}
    return out["verify_old_rows"]["ok"] is not False


def _unheld_foreign_rows() -> list:
    """Queued rows another producer owns that the consumer would claim now.
    Archaeon #284 holds five; a restart must not decide for them."""
    sys.path.insert(0, str(VIVARIUM))
    from viv import db as _db                                   # noqa: PLC0415
    conn = _db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT experiment_id::text, created_by FROM viv.research_experiment_queue WHERE status='queued' "
                        "AND (not_before IS NULL OR not_before <= now()) AND created_by NOT LIKE 'vivarium%%' ORDER BY created_at")
            return [{"experiment_id": e, "created_by": c} for e, c in cur.fetchall()]
    finally:
        conn.rollback(); conn.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Vivarium point-release deploy window")
    ap.add_argument("--confirm", required=True, help="the operator's window id (a date-stamped string); refused otherwise")
    ap.add_argument("--data-dir", default=r"D:\Prometheus-data\vivarium")
    ap.add_argument("--sha", required=True)
    ap.add_argument("--steps", default="backup,drafts,promote,migrate,verify,advance,tasks,bootstrap,restart",
                    help="comma list; run a subset to resume")
    ap.add_argument("--capture", default=None, help="path of the pre-window `viv.cli show` capture (JSON)")
    ap.add_argument("--sample", default="", help="comma list of old experiment ids to compare")
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--write-capture", default=None,
                    help="BEFORE the window: write `viv.cli show` of --sample rows to this path and exit")
    a = ap.parse_args(argv)
    os.environ.setdefault("EW_DB_HOST", "192.168.1.202"); os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
    if a.write_capture:
        cap = {}
        for eid in [s for s in a.sample.split(",") if s]:
            r = subprocess.run([sys.executable, "-m", "viv.cli", "show", eid], capture_output=True, text=True,
                               cwd=str(VIVARIUM), timeout=120)
            cap[eid] = r.stdout
        Path(a.write_capture).write_text(json.dumps(cap, indent=1), encoding="utf-8")
        print("captured %d rows -> %s" % (len(cap), a.write_capture)); return 0
    if not a.confirm or len(a.confirm) < 8:
        print("refused: --confirm must name the operator's window"); return 2
    os.environ.setdefault("EW_DB_HOST", "192.168.1.202"); os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
    data_dir = Path(a.data_dir)
    out = {"schema": "vivarium_deploy_window.v1", "window": a.confirm, "at": _utc(), "sha": a.sha,
           "host": os.environ.get("COMPUTERNAME"), "steps": {}}
    if a.capture and Path(a.capture).exists():
        out["_capture"] = json.loads(Path(a.capture).read_text(encoding="utf-8"))
    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    ok = True
    for step in steps:
        if not ok:
            out["steps"][step] = "SKIPPED (an earlier step failed)"; continue
        if step == "backup":
            ok = step_backup(data_dir, out)
        elif step == "drafts":
            ok = step_drafts(out)
        elif step == "promote":
            ok = step_promote(out)
        elif step == "migrate":
            ok = step_migrate(out)
        elif step == "verify":
            ok = step_verify_old_rows(out, [s for s in a.sample.split(",") if s])
        elif step == "advance":
            prep = data_dir / ("prepare_m2-window-%s.json" % a.confirm)
            r = subprocess.run([sys.executable, str(HERE / "prepare_m2.py"), "--sha", a.sha, "--advance", "--register",
                                "--receipt", str(prep)],
                               capture_output=True, text=True, cwd=str(VIVARIUM), timeout=1800)
            try:
                rec = json.loads(prep.read_text(encoding="utf-8"))
            except Exception:                                   # noqa: BLE001
                rec = {"stdout_tail": r.stdout[-400:], "stderr": r.stderr[-400:]}
            wt_ok = bool((rec.get("worktree") or {}).get("ok"))
            out["advance"] = {"ok": wt_ok, "worktree": rec.get("worktree"), "preconditions": rec.get("preconditions")}
            ok = wt_ok
        elif step == "tasks":
            cmd = data_dir / "vivarium_deliverer_m2.cmd"
            wt = (out.get("advance") or {}).get("worktree", {}).get("path") or r"D:\Prometheus-worktrees\vivarium-consumer"
            cmd.write_text("@echo off\r\nset \"PATH=C:\\Program Files\\Git\\cmd;%PATH%\"\r\nset \"EW_DB_HOST=192.168.1.202\"\r\n"
                           "set \"VIV_DB_HOST=192.168.1.202\"\r\nset \"VIV_VAR_DIR=%s\\var\"\r\ncd /d \"%s\\vivarium\"\r\n"
                           "\"D:\\Prometheus\\.venv-m2\\Scripts\\python.exe\" -m viv.deliver --producer vivarium@m2 "
                           "--task-name VivariumOutboxDelivererM2 --var-dir \"%s\\var\"\r\n" % (data_dir, wt, data_dir),
                           encoding="utf-8")
            r1 = subprocess.run(["schtasks", "/Create", "/F", "/TN", "VivariumOutboxDelivererM2", "/SC", "MINUTE", "/MO", "5",
                                 "/TR", 'cmd.exe /c "%s"' % cmd], capture_output=True, text=True, timeout=60)
            r2 = subprocess.run(["schtasks", "/Change", "/TN", "VivariumOutboxDelivererM2", "/DISABLE"],
                                capture_output=True, text=True, timeout=60)
            out["tasks"] = {"ok": r1.returncode == 0 and r2.returncode == 0, "create": (r1.stdout or r1.stderr)[-160:],
                            "disable": (r2.stdout or r2.stderr)[-160:], "launcher": str(cmd)}
            ok = out["tasks"]["ok"]
        elif step == "bootstrap":
            wt = Path((out.get("advance") or {}).get("worktree", {}).get("path") or r"D:\Prometheus-worktrees\vivarium-consumer")
            r = subprocess.run([sys.executable, "-m", "viv.cli", "sfe-identity", "--ensure", "--role", "production"],
                               capture_output=True, text=True, cwd=str(wt / "vivarium"), timeout=120,
                               env=dict(os.environ, VIV_SFE_BASE_URL="https://192.168.1.191:8811",
                                        VIV_SFE_CACERT="SerendipityFoundry/SerendipityFoundryClient/config/m2.crt"))
            text = (r.stdout or "") + (r.stderr or "")        # the CLI prints names/ids, never a token
            out["bootstrap"] = {"sfe": {"rc": r.returncode, "tail": text[-400:]},
                                "pew": "PENDING -- writer registration is Mnemosyne's route; recorded, not attempted"}
            ok = r.returncode == 0
        elif step == "restart":
            foreign = _unheld_foreign_rows()
            if foreign:
                out["restart"] = {"ok": False, "reason": "queued rows not created by vivarium and not held would be "
                                  "claimed on the first tick; hold them (viv.cli hold <id> --until ...) or have their "
                                  "producer clear them first", "rows": foreign}
                ok = False; out["steps"][step] = "FAILED"; continue
            r1 = subprocess.run(["schtasks", "/Change", "/TN", "VivariumDeadmanM2", "/ENABLE"], capture_output=True, text=True, timeout=60)
            r2 = subprocess.run(["schtasks", "/Run", "/TN", "VivariumDeadmanM2"], capture_output=True, text=True, timeout=60)
            r3 = subprocess.run(["schtasks", "/Change", "/TN", "VivariumOutboxDelivererM2", "/ENABLE"], capture_output=True, text=True, timeout=60)
            out["restart"] = {"deadman_enabled": r1.returncode == 0, "deadman_run": r2.returncode == 0,
                              "deliverer_enabled": r3.returncode == 0,
                              "note": "the dead-man's first tick launches the consumer; read var/restart-vivarium@m2.json for the restart receipt"}
            ok = all(v is True for k, v in out["restart"].items() if k != "note")
        else:
            out["steps"][step] = "UNKNOWN STEP"; ok = False
        out["steps"][step] = "OK" if ok else "FAILED"
    out.pop("_capture", None)
    out["ok"] = ok
    receipt = Path(a.receipt) if a.receipt else data_dir / ("deploy_window-%s.json" % a.confirm)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("backup",)}, indent=2, default=str))
    print("receipt:", receipt)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
