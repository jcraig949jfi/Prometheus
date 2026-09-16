#!/usr/bin/env python3
"""Adopt M1's production ledger on the M2 engine (the SFE ecosystem moves to M2).

    python deploy/adopt_m1_ledger.py --check  [--src DIR]   # verify the landed bytes; change nothing
    python deploy/adopt_m1_ledger.py --apply  [--src DIR]   # stop twin, swap data, start, verify

WHAT THIS IS. The operator's ccb26df01 (2026-09-15): "M1 is handed to Nestor and
SFE moves to M2 carrying M1's engine.db." M1's data dir (D:\\Prometheus-data\\sfe
on SKULLPORT: engine.db, blobs/, backup/) has to be landed on M2 by a path the
operator chooses (no share is reachable in either direction, Techne #231);
this tool takes it from there. The M2 engine already runs the layout, build,
launcher and supervisor the migrated ledger will run on (relocate_m2.py,
2026-09-16), so the swap is data only.

THE INVARIANT. `engine_instance_id` is ledger state. The landed ledger must
identify itself as eng_8a37a5d305969034d488c43e (the production identity every
consumer, grant and contract is keyed to), at schema 8, with at least as many
events as the last M1 receipt recorded (LEDGER_MOVE_2026-09-12/apply.json:
129,401) -- a ledger cannot shrink. After the start, /v2/version on
https://192.168.1.191:8811 must report that id and the M2 build hash. If any
of these fail, nothing is switched (check) or the twin is restored (apply).

WHAT IS KEPT. The twin's own ledger (eng_906356f7) is MOVED to
D:\\Prometheus-data\\sfe-twin-rollback\\, never deleted. m2.crt / m2.key stay:
the engine binds 192.168.1.191 and serves M2's cert; consumers switch cacert
to SerendipityFoundryClient/config/m2.crt. M1's m1.key is NOT wanted here and
is refused if present in the landed dir (charter rule 5: it never leaves M1).

NOT DONE HERE. Harmonia's promote_candidate_contract.py (contract base_url ->
192.168.1.191, engine hash -> 726275da) is the step after this one, run and
receipted separately; consumers re-point after THAT is posted.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from move_service_out_of_canonical import instance_of, sha256_file  # noqa: E402
from relocate_m2 import DATA, HOST, PORT, version, ps  # noqa: E402

PROD_INSTANCE = "eng_8a37a5d305969034d488c43e"
M2_BUILD = "sha256:726275da9c8daa30ea2fff5e66e9a1df53aa5263256d342602fad25cb415d75c"
LAST_M1_RECEIPT = os.path.join(HERE, "LEDGER_MOVE_2026-09-12", "apply.json")
ROLLBACK = r"D:\Prometheus-data\sfe-twin-rollback"
WATCHDOG = os.path.join(DATA, "sfengine_m2_watchdog.ps1")


def ledger_facts(db):
    cx = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=20)
    try:
        meta = dict(cx.execute("SELECT key, value FROM meta").fetchall())
        ev = cx.execute("SELECT COUNT(*), COALESCE(MAX(event_seq),0) FROM events").fetchone()
        wi = dict(cx.execute("SELECT status, COUNT(*) FROM work_items GROUP BY status").fetchall())
        return {"engine_instance_id": meta.get("engine_instance_id"),
                "schema_version": int(meta.get("schema_version", 0)),
                "events": ev[0], "max_event_seq": ev[1], "work_items": wi}
    finally:
        cx.close()


def count_files(d):
    return sum(len(fs) for _dp, _d, fs in os.walk(d)) if os.path.isdir(d) else 0


def stop_engine(rec):
    rc, out = ps(
        "$c = Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue; "
        "if ($c) { $id = $c.OwningProcess; $p = Get-CimInstance Win32_Process -Filter \"ProcessId=$id\"; "
        "Stop-Process -Id $id -Force; Stop-Process -Id $p.ParentProcessId -Force -ErrorAction SilentlyContinue; "
        "\"stopped $id parent $($p.ParentProcessId)\" } else { 'not listening' }" % PORT)
    rec["steps"].append({"stop": out, "rc": rc})
    for _ in range(20):
        rc2, out2 = ps("if (Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue) {'held'} else {'free'}" % PORT)
        if out2.strip() == "free":
            return True
        time.sleep(0.5)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--src", default=r"D:\Prometheus-data\sfe-from-m1",
                    help="where the operator landed M1's data dir (engine.db, blobs/, backup/)")
    ap.add_argument("--receipt", default=None)
    a = ap.parse_args()
    stamp = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    receipt = a.receipt or os.path.join(HERE, "ADOPT_M1_LEDGER_2026-09-16",
                                        ("apply" if a.apply else "check") + "_" + stamp + ".json")
    rec = {"tool": "adopt_m1_ledger.py", "mode": "apply" if a.apply else "check",
           "src": a.src, "started_at": stamp, "checks": [], "steps": []}
    ok = True

    def row(name, passed, **detail):
        nonlocal ok
        ok = ok and bool(passed)
        rec["checks"].append({"check": name, "pass": bool(passed), **detail})
        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        for k, v in detail.items():
            print("         %s: %s" % (k, v))

    print("ADOPT M1 LEDGER ON M2 -- %s" % ("APPLY" if a.apply else "CHECK (changes nothing)"))
    print("=" * 74)

    # -- the landed bytes ---------------------------------------------------
    src_db = os.path.join(a.src, "engine.db")
    row("landed dir exists", os.path.isdir(a.src), src=a.src)
    row("landed engine.db exists", os.path.exists(src_db),
        size_mb=round(os.path.getsize(src_db) / 1048576, 1) if os.path.exists(src_db) else None)
    if not os.path.exists(src_db):
        return _write(rec, receipt, 1)
    wal = os.path.join(a.src, "engine.db-wal")
    row("no pending WAL beside the landed ledger (a copy taken while the engine "
        "ran is inconsistent without it)", not (os.path.exists(wal) and os.path.getsize(wal) > 0),
        wal_bytes=os.path.getsize(wal) if os.path.exists(wal) else 0)
    facts = ledger_facts(src_db)
    rec["landed_ledger"] = facts
    last = json.load(open(LAST_M1_RECEIPT, encoding="utf-8"))["ledger_at_stop"]
    row("landed ledger IS the production ledger", facts["engine_instance_id"] == PROD_INSTANCE,
        landed=facts["engine_instance_id"], expected=PROD_INSTANCE)
    row("landed ledger is schema 8", facts["schema_version"] == 8, schema=facts["schema_version"])
    row("landed ledger has not shrunk since the last M1 receipt (2026-09-12)",
        facts["events"] >= last["events"] and facts["max_event_seq"] >= last["max_event_seq"],
        events=facts["events"], receipt_events=last["events"],
        max_seq=facts["max_event_seq"], receipt_max_seq=last["max_event_seq"])
    nblobs = count_files(os.path.join(a.src, "blobs"))
    row("landed blobs present and not fewer than the last M1 receipt (2,141)", nblobs >= 2141, blobs=nblobs)
    row("m1.key is NOT in the landed dir (it never leaves M1)",
        not os.path.exists(os.path.join(a.src, "m1.key")))
    rec["landed_sha256_engine_db"] = sha256_file(src_db)
    print("  work_items: %s" % json.dumps(facts["work_items"]))

    # -- the twin as it is now ------------------------------------------------
    twin_db = os.path.join(DATA, "engine.db")
    twin_inst = instance_of(twin_db) if os.path.exists(twin_db) else None
    row("twin data dir holds the twin ledger (not already production)", twin_inst != PROD_INSTANCE,
        twin_instance=twin_inst)
    v = version(os.path.join(DATA, "m2.crt"))
    rec["live_before"] = v
    row("M2 engine reachable before the swap (or absent; both fine)", True,
        engine_instance_id=v.get("engine_instance_id"), engine_source_hash=v.get("engine_source_hash"))
    row("M2 serves the intended build", v.get("engine_source_hash") in (None, M2_BUILD),
        live=v.get("engine_source_hash"), expected=M2_BUILD)
    row("rollback dir does not already hold a ledger", not os.path.exists(os.path.join(ROLLBACK, "engine.db")),
        rollback=ROLLBACK)

    if not a.apply:
        print("\n  CHECK ONLY. Nothing was changed.%s" % ("" if ok else "  A precondition FAILED; --apply would refuse."))
        return _write(rec, receipt, 0 if ok else 1)
    if not ok:
        print("\n  REFUSING to apply: a precondition failed above.")
        return _write(rec, receipt, 1)

    # -- 1. stop the twin --------------------------------------------------------
    t0 = time.time()
    row("twin stopped and port free", stop_engine(rec))
    if not ok:
        return _write(rec, receipt, 1)

    # -- 2. move the twin's ledger aside, copy production in ------------------------
    os.makedirs(ROLLBACK, exist_ok=True)
    for name in ("engine.db", "engine.db-wal", "engine.db-shm", "blobs", "backup", "incidents"):
        s = os.path.join(DATA, name)
        if os.path.exists(s):
            shutil.move(s, os.path.join(ROLLBACK, name))
            rec["steps"].append({"moved_aside": name, "to": os.path.join(ROLLBACK, name)})
    for name in ("engine.db", "blobs", "backup"):
        s, d = os.path.join(a.src, name), os.path.join(DATA, name)
        if not os.path.exists(s):
            rec["steps"].append({"absent_in_src": name})
            continue
        t1 = time.time()
        if os.path.isdir(s):
            shutil.copytree(s, d)
            rec["steps"].append({"copied": name, "files": count_files(d), "s": round(time.time() - t1, 1)})
        else:
            shutil.copy2(s, d)
            rec["steps"].append({"copied": name, "sha256": sha256_file(d),
                                 "identical": sha256_file(d) == rec["landed_sha256_engine_db"],
                                 "s": round(time.time() - t1, 1)})
    got = ledger_facts(os.path.join(DATA, "engine.db"))
    row("copied ledger IS the production ledger, same size", got == facts, copy=got)
    if not ok:
        _restore(rec)
        return _write(rec, receipt, 1)

    # -- 3. start through the supervisor, verify -------------------------------------
    rc, out = ps("powershell -NoProfile -ExecutionPolicy Bypass -File \"%s\"" % WATCHDOG)
    rec["steps"].append({"watchdog_tick": out[-400:], "rc": rc})
    v = {}
    for _ in range(30):
        v = version(os.path.join(DATA, "m2.crt"))
        if "_error" not in v:
            break
        time.sleep(1)
    rec["live_after"] = v
    rec["outage_s"] = round(time.time() - t0, 1)
    row("engine answers /v2/version", "_error" not in v, error=v.get("_error"))
    row("engine reports the PRODUCTION ledger", v.get("engine_instance_id") == PROD_INSTANCE,
        live=v.get("engine_instance_id"))
    row("engine reports the M2 build", v.get("engine_source_hash") == M2_BUILD, live=v.get("engine_source_hash"))
    row("engine is schema 8", v.get("schema_version") == 8)
    if not ok:
        print("  a post-start check FAILED: restoring the twin's data")
        stop_engine(rec)
        _restore(rec)
        ps("powershell -NoProfile -ExecutionPolicy Bypass -File \"%s\"" % WATCHDOG)
        return _write(rec, receipt, 1)
    print("\n  outage %.1f s. Twin ledger kept at %s (not deleted)." % (rec["outage_s"], ROLLBACK))
    print("  NEXT: roles/Harmonia/contracts/promote_candidate_contract.py --base https://%s:%d ... (separate receipt)" % (HOST, PORT))
    return _write(rec, receipt, 0)


def _restore(rec):
    for name in ("engine.db", "blobs", "backup"):
        d = os.path.join(DATA, name)
        if os.path.exists(d):
            (shutil.rmtree if os.path.isdir(d) else os.remove)(d)
    for name in os.listdir(ROLLBACK) if os.path.isdir(ROLLBACK) else []:
        shutil.move(os.path.join(ROLLBACK, name), os.path.join(DATA, name))
    rec["steps"].append({"restored_twin": True})


def _write(rec, path, rc):
    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["rc"] = rc
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    print("  receipt: %s" % path)
    return rc


if __name__ == "__main__":
    sys.exit(main())
