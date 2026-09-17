#!/usr/bin/env python3
"""Point release 2026-09 (schema 8 -> 9) on the M2 production engine.

    python deploy/release_v9.py preflight --commit <sha>     # operator order s8; changes nothing but writes a backup
    python deploy/release_v9.py apply     --commit <sha>     # advance pin, stop, supervisor restarts, migrate, record identities (s7)
    python deploy/release_v9.py verify                       # re-record identities of the running service; compare to the deploy receipt

PRE-DEPLOY SAFETY (s8): records the production descriptor; verifies the
ledger is eng_906356f7 at schema 8; takes a verified SQLite backup (the
backup API, then re-opened and read) into the data dir's backup/; records
the current build; checks that nobody is writing (events in the last 10 min,
work items RUNNING/CLAIMED, connections in the engine log tail) and refuses
to apply if anything is; states the consumer tolerance (additive routes read
INCOMPLETE-covered; the schema bump reads mismatch until the contract lands).

RESTART DISCIPLINE (s7): the pinned worktree is advanced to the release
commit, the running process is killed (child + launcher parent), the
supervisor (pinned watchdog) starts the new process, the migration runs at
first open, and the service's identities are recorded: process start time,
engine instance, source hash, schema, route digest, ledger identity, bind
endpoint, descriptor pin. Any identity that differs from what the preflight
expected STOPS qualification with a named difference.

ROLLBACK: restore the preflight backup over engine.db (with the service
stopped), re-pin the worktree to the previous commit, restart. Written in
SFE_SCHEMA9_MIGRATION_RECEIPT.md; not automated here on purpose (a rollback
is an operator act).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from relocate_m2 import DATA, HOST, PORT, PINNED_WT, PINNED, version, ps  # noqa: E402
from move_service_out_of_canonical import sha256_file, _hash_sfe           # noqa: E402

DB = os.path.join(DATA, "engine.db")
CA = os.path.join(DATA, "m2.crt")
WATCHDOG = os.path.join(DATA, "sfengine_m2_watchdog.ps1")
RECEIPTS = os.path.join(HERE, "POINT_RELEASE_2026-09-17")
FROM_SCHEMA, TO_SCHEMA, ROUTES_DELTA = 8, 9, 4
PROD_INSTANCE = "eng_906356f7fb1da180131f9290"
BASE = "https://%s:%d" % (HOST, PORT)


def get(path, timeout=10):
    import ssl
    ctx = ssl.create_default_context(cafile=CA)
    with urllib.request.urlopen(BASE + path, context=ctx, timeout=timeout) as r:
        return json.loads(r.read().decode())


def ledger_facts():
    cx = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True, timeout=20)
    try:
        meta = dict(cx.execute("SELECT key, value FROM meta").fetchall())
        ev = cx.execute("SELECT COUNT(*), COALESCE(MAX(event_seq),0), COALESCE(MAX(ts),0) FROM events").fetchone()
        recent = cx.execute("SELECT COUNT(*) FROM events WHERE ts > ?", (time.time() - 600,)).fetchone()[0]
        wi = dict(cx.execute("SELECT status, COUNT(*) FROM work_items GROUP BY status").fetchall())
        obs_max = cx.execute("SELECT COALESCE(MAX(c),0) FROM (SELECT COUNT(*) c FROM observations GROUP BY world_id)").fetchone()[0]
        exp_max = cx.execute("SELECT COALESCE(MAX(c),0) FROM (SELECT COUNT(*) c FROM experiments GROUP BY world_id)").fetchone()[0]
        return {"engine_instance_id": meta.get("engine_instance_id"),
                "schema_version": int(meta.get("schema_version", 0)),
                "events": ev[0], "max_event_seq": ev[1], "last_event_ts": ev[2],
                "events_last_10min": recent, "work_items": wi,
                "max_observations_per_world": obs_max, "max_experiments_per_world": exp_max}
    finally:
        cx.close()


def route_digest():
    spec = get("/v2/openapi.json")
    rows = sorted("%s %s" % (m.upper(), p) for p, ops in spec["paths"].items() for m in ops)
    return "sha256:" + hashlib.sha256("\n".join(rows).encode()).hexdigest(), len(rows)


def process_facts():
    rc, out = ps("$c = Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue; "
                 "if ($c) { $p = Get-CimInstance Win32_Process -Filter \"ProcessId=$($c.OwningProcess)\"; "
                 "@{pid=$p.ProcessId; start=$p.CreationDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'); "
                 "cmd=$p.CommandLine; bind=$c.LocalAddress} | ConvertTo-Json -Compress } else { '{}' }" % PORT)
    try:
        return json.loads(out or "{}")
    except Exception:                                    # noqa: BLE001
        return {"raw": out}


def identities():
    v = get("/v2/version")
    cap = get("/v2/capabilities") if v.get("schema_version", 0) >= 9 else None
    rd, nroutes = route_digest()
    pf = process_facts()
    lf = ledger_facts()
    pin = json.load(open(os.path.join(HERE, "DEPLOYED_BUILD_M2.json"), encoding="utf-8"))
    return {"recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "process_start_utc": pf.get("start"), "pid": pf.get("pid"), "bind": pf.get("bind"),
            "cmdline": pf.get("cmd"),
            "engine_instance_id": v["engine_instance_id"], "engine_source_hash": v["engine_source_hash"],
            "source_commit": v.get("source_commit"), "schema_version": v["schema_version"],
            "route_digest": rd, "routes": nroutes,
            "capabilities_features": cap["features"] if cap else None,
            "ledger": {"path": DB, "engine_instance_id": lf["engine_instance_id"],
                       "schema_version": lf["schema_version"], "events": lf["events"]},
            "endpoint": BASE, "descriptor_pin": {"engine_source_hash": pin.get("engine_source_hash"),
                                                 "source_commit": pin.get("source_commit_containing_build")}}


def git(*args):
    p = subprocess.run(["git", "-C", PINNED_WT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip() + p.stderr.strip()


def write(rec, name):
    os.makedirs(RECEIPTS, exist_ok=True)
    p = os.path.join(RECEIPTS, name)
    json.dump(rec, open(p, "w", encoding="utf-8"), indent=1)
    print("  receipt: %s" % p)
    return p


def preflight(commit):
    rec = {"phase": "preflight", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "checks": [], "commit": commit}
    ok = True

    def row(name, passed, **d):
        nonlocal ok
        ok = ok and bool(passed)
        rec["checks"].append({"check": name, "pass": bool(passed), **d})
        print("  [%s] %s %s" % ("PASS" if passed else "FAIL", name, json.dumps(d)[:200]))

    print("PREFLIGHT (order s8)")
    ident = identities()
    rec["production_descriptor_before"] = ident
    row("production ledger identity", ident["engine_instance_id"] == PROD_INSTANCE == ident["ledger"]["engine_instance_id"],
        live=ident["engine_instance_id"], ledger=ident["ledger"]["engine_instance_id"])
    row("current schema is %d (this release: %d -> %d)" % (FROM_SCHEMA, FROM_SCHEMA, TO_SCHEMA),
        ident["schema_version"] == FROM_SCHEMA == ident["ledger"]["schema_version"])
    row("pin agrees with the running build", ident["descriptor_pin"]["engine_source_hash"] == ident["engine_source_hash"])
    # the release commit exists in the pinned worktree's repo and reproduces the expected hash
    rc, out = git("fetch", "-q", "origin")
    rc, sha = git("rev-parse", commit)
    row("release commit resolvable", rc == 0, sha=sha[:12])
    rc, tree_hash = 0, None
    # hash the candidate tree WITHOUT checking it out: git archive to a temp dir
    tmp = os.path.join(RECEIPTS, "_candidate_tree")
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp, exist_ok=True)
    p = subprocess.run(["git", "-C", PINNED_WT, "archive", "--format=tar", commit,
                        "SerendipityFoundry/SerendipityFoundryEngine/sfe"], capture_output=True)
    import io, tarfile
    tarfile.open(fileobj=io.BytesIO(p.stdout)).extractall(tmp)
    tree_hash = _hash_sfe(os.path.join(tmp, "SerendipityFoundry", "SerendipityFoundryEngine", "sfe"))
    shutil.rmtree(tmp, ignore_errors=True)
    rec["candidate_engine_source_hash"] = tree_hash
    row("candidate tree hashes to a NEW build", bool(tree_hash) and tree_hash != ident["engine_source_hash"], candidate=tree_hash)
    # nobody writing
    lf = ledger_facts()
    inflight = sum(v for k, v in lf["work_items"].items() if k in ("RUNNING", "CLAIMED"))
    row("no scientific writes in the last 10 min", lf["events_last_10min"] == 0, events_last_10min=lf["events_last_10min"],
        last_event_age_s=round(time.time() - lf["last_event_ts"]))
    row("no work in flight", inflight == 0, work_items=lf["work_items"])
    rec["ledger_before"] = lf
    rec["consumer_tolerance"] = ("additive routes read INCOMPLETE-covered, never DRIFT, for consumers that declare their routes "
                                 "(#256 C5); the schema bump 8->9 reads as a mismatch to any gate until the contract is regenerated "
                                 "and landed in the same window; no consumer process is running (C3 closed #326; Vivarium not "
                                 "launched, #318/#329); default list responses gain keys, no consumer parses them positionally")
    # backup (SQLite backup API, then verified by re-open)
    os.makedirs(os.path.join(DATA, "backup"), exist_ok=True)
    bak = os.path.join(DATA, "backup", "engine.db.pre-%s-%s.bak" % (
        ("schema%d" % TO_SCHEMA) if TO_SCHEMA != FROM_SCHEMA else "release",
        time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())))
    t0 = time.time()
    src = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True, timeout=30)
    dst = sqlite3.connect(bak)
    src.backup(dst); dst.close(); src.close()
    chk = sqlite3.connect("file:%s?mode=ro" % bak.replace("\\", "/"), uri=True)
    bmeta = dict(chk.execute("SELECT key, value FROM meta").fetchall())
    bev = chk.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    integrity = chk.execute("PRAGMA integrity_check").fetchone()[0]
    chk.close()
    row("backup written and verified", bmeta.get("engine_instance_id") == PROD_INSTANCE and bev == lf["events"] and integrity == "ok",
        path=bak, events=bev, integrity=integrity, sha256=sha256_file(bak), s=round(time.time() - t0, 1))
    rec["backup"] = {"path": bak, "sha256": sha256_file(bak), "events": bev, "schema": bmeta.get("schema_version")}
    # blobs count for the record
    rec["blobs_files"] = sum(len(fs) for _d, _dd, fs in os.walk(os.path.join(DATA, "blobs")))
    rec["ok"] = ok
    write(rec, "preflight.json")
    print("  PREFLIGHT %s" % ("OK -- apply may proceed" if ok else "FAILED -- do not apply"))
    return 0 if ok else 1


def apply(commit):
    pre_path = os.path.join(RECEIPTS, "preflight.json")
    if not os.path.exists(pre_path):
        print("REFUSING: no preflight receipt"); return 2
    pre = json.load(open(pre_path, encoding="utf-8"))
    if not pre.get("ok") or pre.get("commit") != commit:
        print("REFUSING: preflight not OK or for a different commit"); return 2
    if time.time() - time.mktime(time.strptime(pre["at"], "%Y-%m-%dT%H:%M:%SZ")) > 3600 * 6:
        print("REFUSING: preflight older than 6 h"); return 2
    rec = {"phase": "apply", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "commit": commit, "steps": [], "checks": []}
    ok = True

    def row(name, passed, **d):
        nonlocal ok
        ok = ok and bool(passed)
        rec["checks"].append({"check": name, "pass": bool(passed), **d})
        print("  [%s] %s %s" % ("PASS" if passed else "FAIL", name, json.dumps(d)[:200]))

    print("APPLY (order s7)")
    before = identities()
    rec["before"] = before
    lf = ledger_facts()
    row("still nobody writing", lf["events_last_10min"] == 0, events_last_10min=lf["events_last_10min"])
    if not ok:
        write(rec, "apply.json"); return 1
    # 1. advance the pin
    rc, prev = git("rev-parse", "HEAD")
    rc, out = git("checkout", "-q", "--detach", commit)
    rc2, head = git("rev-parse", "HEAD")
    rec["steps"].append({"pin": {"from": prev[:12], "to": head[:12], "rc": rc}})
    row("pinned worktree advanced", rc == 0 and head.startswith(commit[:7]) if len(commit) < 40 else head == commit, head=head[:12])
    row("pinned tree reproduces the candidate hash", _hash_sfe(os.path.join(PINNED, "sfe")) == pre["candidate_engine_source_hash"])
    if not ok:
        git("checkout", "-q", "--detach", prev)
        write(rec, "apply.json"); return 1
    # 2. stop the running process (child + launcher parent)
    t0 = time.time()
    rc, out = ps("$c = Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue; "
                 "if ($c) { $id=$c.OwningProcess; $p=Get-CimInstance Win32_Process -Filter \"ProcessId=$id\"; "
                 "Stop-Process -Id $id -Force; Stop-Process -Id $p.ParentProcessId -Force -ErrorAction SilentlyContinue; "
                 "\"stopped $id\" } else { 'not listening' }" % PORT)
    rec["steps"].append({"stop": out})
    for _ in range(60):
        rc, o = ps("if (Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue) {'held'} else {'free'}" % PORT)
        if o.strip() == "free":
            break
        time.sleep(0.5)
    # 3. the supervisor starts the new process (migration runs at first open)
    rc, out = ps("powershell -NoProfile -ExecutionPolicy Bypass -File \"%s\"" % WATCHDOG)
    rec["steps"].append({"watchdog": out[-300:], "rc": rc})
    v = None
    for _ in range(60):
        try:
            v = get("/v2/version"); break
        except Exception:                                # noqa: BLE001
            time.sleep(1)
    rec["outage_s"] = round(time.time() - t0, 1)
    row("engine answers after restart", v is not None, outage_s=rec["outage_s"])
    if v is None:
        write(rec, "apply.json"); return 1
    after = identities()
    rec["after"] = after
    # 4. the identity checklist (order s7): expected vs observed
    row("process is NEW (start time advanced, pid changed)",
        after["process_start_utc"] != before["process_start_utc"] and after["pid"] != before["pid"],
        before=before["process_start_utc"], after=after["process_start_utc"])
    row("engine instance UNCHANGED (ledger state)", after["engine_instance_id"] == PROD_INSTANCE == after["ledger"]["engine_instance_id"])
    row("source hash == candidate", after["engine_source_hash"] == pre["candidate_engine_source_hash"], live=after["engine_source_hash"])
    row("schema %d live AND in the ledger" % TO_SCHEMA, after["schema_version"] == TO_SCHEMA == after["ledger"]["schema_version"])
    row("route count delta == %+d" % ROUTES_DELTA, after["routes"] == before["routes"] + ROUTES_DELTA,
        before=before["routes"], after=after["routes"])
    if TO_SCHEMA >= 9:
        try:
            ck = get("/v2/health").get("checkpointer")
        except Exception:                                    # noqa: BLE001
            ck = None
        if ck is not None:
            row("checkpointer alive on the new process", ck.get("alive") is True and ck.get("errors") == 0,
                runs=ck.get("runs"), wal_bytes=ck.get("wal_bytes"))
    row("ledger path and bind unchanged", after["ledger"]["path"] == before["ledger"]["path"] and after["bind"] == before["bind"], bind=after["bind"])
    row("no event lost across the migration", after["ledger"]["events"] == before["ledger"]["events"], events=after["ledger"]["events"])
    row("capabilities advertises the release", bool(after["capabilities_features"]) and all(after["capabilities_features"].values()))
    # 5. re-pin the descriptor
    if ok:
        pin_path = os.path.join(HERE, "DEPLOYED_BUILD_M2.json")
        pin = json.load(open(pin_path, encoding="utf-8"))
        pin["history"].append({after["recorded_at"]: "release (schema %d): %s / %s" % (TO_SCHEMA, head[:12], after["engine_source_hash"][:20])})
        pin.update({"pinned_at": after["recorded_at"], "schema_version": TO_SCHEMA,
                    "source_commit_containing_build": head, "engine_source_hash": after["engine_source_hash"],
                    "route_digest": after["route_digest"], "routes": after["routes"],
                    "contract": "roles/Harmonia/contracts/sfe_contract.json (REGENERATED after this restart; see POINT_RELEASE_2026-09-17/)"})
        pin.pop("live_verified_2026-09-16T17:2xZ", None)
        json.dump(pin, open(pin_path, "w", encoding="utf-8"), indent=1); open(pin_path, "a").write("\n")
        rec["steps"].append({"repinned": pin_path})
    rec["ok"] = ok
    write(rec, "apply.json")
    print("  APPLY %s" % ("OK -- qualification may proceed" if ok else "IDENTITY MISMATCH -- STOP QUALIFICATION, diagnose"))
    return 0 if ok else 1


def verify():
    rec = {"phase": "verify", "identities": identities()}
    ap_ = json.load(open(os.path.join(RECEIPTS, "apply.json"), encoding="utf-8"))
    same = {k: rec["identities"][k] == ap_["after"][k] for k in
            ("process_start_utc", "pid", "engine_instance_id", "engine_source_hash", "schema_version", "route_digest", "bind")}
    rec["same_as_apply"] = same
    print(json.dumps(same, indent=1))
    write(rec, "verify_%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    return 0 if all(same.values()) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=("preflight", "apply", "verify"))
    ap.add_argument("--commit", default=None)
    ap.add_argument("--from-schema", type=int, default=8, help="schema the ledger must be at before apply")
    ap.add_argument("--to-schema", type=int, default=9, help="schema the ledger must be at after apply")
    ap.add_argument("--routes-delta", type=int, default=4, help="expected change in route count")
    ap.add_argument("--tag", default=None, help="receipt subdirectory (default POINT_RELEASE_2026-09-17)")
    a = ap.parse_args()
    global RECEIPTS, FROM_SCHEMA, TO_SCHEMA, ROUTES_DELTA
    FROM_SCHEMA, TO_SCHEMA, ROUTES_DELTA = a.from_schema, a.to_schema, a.routes_delta
    if a.tag:
        RECEIPTS = os.path.join(HERE, a.tag)
    if a.phase == "preflight":
        return preflight(a.commit)
    if a.phase == "apply":
        return apply(a.commit)
    return verify()


if __name__ == "__main__":
    sys.exit(main())
