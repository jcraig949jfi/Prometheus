"""G3 (Archaeon's Campaign 4 launch gate): PROVE, machine-readably, that the
Campaign-4 consumer identity is live -- not claim it in a message.

Every line below is READ from the engine, the store or the host at run time:

    engine        GET /v2/version as seen by the consumer's own client
    identity      a world the consumer created, read AS the consumer: the
                  engine's client_id on that world == the registered client id;
                  the same read as the marked `vivarium-test` identity is 403
                  ("not owned by this client") -- the token maps to the owner
    liveness      viv.worker_heartbeat row for vivarium@m2 (age on the DB
                  clock) and whether its pid is a live python on this host
    build         the restart receipt's base_sha == the pinned worktree HEAD
    read grant    the newest scope_reconcile receipt (the B1 grant to
                  Archaeon): its grantee, and the engine's answer
    outbox        PENDING / DELIVERED counts (G4 context)

No token value is read by this script: the engine reads run inside the
pinned worktree, whose gitignored config holds the identities, and only the
answers come back. Output: a JSON receipt with a digest over its own body.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("EW_DB_HOST", "192.168.1.202"); os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
HERE = Path(__file__).resolve().parent
VIVARIUM = HERE.parent
REPO = VIVARIUM.parent
PINNED = Path(r"D:\Prometheus-worktrees\vivarium-consumer")
VAR = Path(r"D:\Prometheus-data\vivarium\var")
sys.path.insert(0, str(VIVARIUM))
from viv import db as _db                                        # noqa: E402


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def engine_reads(world_id: str) -> dict:
    code = (
        "import json,os,sys; sys.path.insert(0, r'%s')\n"
        "from viv import db as _db, identity as _i\n"
        "from sfclient import EngineClient\n"
        "cfg=_db.load_config(); ca=os.path.join(r'%s', cfg['sfe_cacert'])\n"
        "out={}\n"
        "for role in ('production','test'):\n"
        "    c=EngineClient(cfg['sfe_base_url'], _i.token_for(role), cafile=ca, timeout=60)\n"
        "    out[role]={'registered_client_id': _i.client_id_for(role)}\n"
        "    if role=='production': out['version']=c.version()\n"
        "    try:\n"
        "        w=c.get_world(sys.argv[1]); out[role]['get_world']={'http': 200, 'client_id': w.get('client_id'), 'state': w.get('state'), 'name': w.get('name')}\n"
        "    except Exception as e:\n"
        "        out[role]['get_world']={'error': str(e)[:160]}\n"
        "print(json.dumps(out))\n"
    ) % (str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient"), str(PINNED))
    env = dict(os.environ, VIV_SFE_BASE_URL="https://192.168.1.191:8811",
               VIV_SFE_CACERT="SerendipityFoundry/SerendipityFoundryClient/config/m2.crt")
    r = subprocess.run([sys.executable, "-c", code, world_id], capture_output=True, text=True,
                       cwd=str(PINNED / "vivarium"), env=env, timeout=120)
    if r.returncode != 0:
        return {"error": (r.stderr or r.stdout).strip().splitlines()[-1][:300]}
    return json.loads(r.stdout.strip().splitlines()[-1])


def pid_alive(pid: int) -> bool:
    out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=20).stdout
    line = (out or "").strip().splitlines()
    return bool(line) and "No tasks" not in line[0] and line[0].lower().startswith('"python')


def main() -> int:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "roles" / "Vivarium" / "receipts" / "window_C4-20260917-W1" / "G3_IDENTITY_PROOF.json"
    rec = {"schema": "vivarium_g3_identity_proof.v1", "at": _utc(), "host": os.environ.get("COMPUTERNAME"),
           "gate_item": "G3 Campaign-4 consumer identity live and its M2 B1 read grant valid", "checks": {}}
    conn = _db.connect()
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT worker_id, pid, host, EXTRACT(EPOCH FROM (now() - last_seen)) AS age_s, current_experiment, "
                    "build->'code'->>'base_sha' AS base_sha FROM viv.worker_heartbeat WHERE worker_id='vivarium@m2'")
        hb = dict(cur.fetchone() or {})
        cur.execute("SELECT s.result->>'world_id' AS wid FROM viv.execution_step s JOIN viv.execution_attempt a USING (attempt_id) "
                    "JOIN viv.research_experiment_queue q USING (experiment_id) WHERE s.step_kind='world' AND s.result ? 'world_id' "
                    "AND q.created_by='vivarium-canary' ORDER BY s.started_at DESC LIMIT 1")
        wid = (cur.fetchone() or {}).get("wid")
        cur.execute("SELECT state, count(*) AS n FROM viv.pew_outbox GROUP BY state")
        outbox = {r["state"]: r["n"] for r in cur.fetchall()}
    conn.rollback(); conn.close()

    restart = json.loads((VAR / "restart-vivarium@m2.json").read_text(encoding="utf-8"))
    pin_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(PINNED)).stdout.strip()
    alive = pid_alive(int(hb.get("pid") or 0)) and str(hb.get("host") or "").upper() == os.environ.get("COMPUTERNAME", "").upper()
    rec["checks"]["consumer_alive"] = {"ok": alive and float(hb.get("age_s") or 1e9) < 900,
                                       "worker_id": hb.get("worker_id"), "pid": hb.get("pid"), "host": hb.get("host"),
                                       "heartbeat_age_s": round(float(hb.get("age_s") or 0), 1), "pid_is_live_python_here": alive,
                                       "current_experiment": hb.get("current_experiment")}
    rec["checks"]["build_pinned"] = {"ok": restart["code"]["base_sha"] == pin_head and not restart["code"]["dirty"] and restart["code"]["detached"],
                                     "restart_receipt_base_sha": restart["code"]["base_sha"], "pinned_worktree_head": pin_head,
                                     "restart_receipt_ok": restart.get("ok"), "refuse": restart.get("refuse")}
    e = engine_reads(wid) if wid else {"error": "no canary world to read"}
    prod = e.get("production", {}); test = e.get("test", {})
    owner_ok = (prod.get("get_world", {}).get("http") == 200
                and prod.get("get_world", {}).get("client_id") == prod.get("registered_client_id")
                and "not owned" in (test.get("get_world", {}).get("error") or "").lower())
    rec["checks"]["identity_is_the_owner_on_the_engine"] = {
        "ok": bool(owner_ok), "world_read": wid,
        "as_vivarium": prod, "as_vivarium_test": test,
        "engine_version": e.get("version"),
        "meaning": "the consumer's token authenticates as the client that owns the worlds it creates; the marked test identity is refused on them"}
    scopes = sorted(VAR.glob("scope_reconcile-*.json"))
    latest = json.loads(scopes[-1].read_text(encoding="utf-8")) if scopes else {}
    sc = (latest.get("scopes") or [{}])[0]
    granted = not sc.get("error") and latest.get("added_total") is not None
    rec["checks"]["b1_read_grant_to_archaeon"] = {
        "ok": bool(granted), "direction": "OWNER = Vivarium grants; GRANTEE = Archaeon's engine client (config.json read_scopes[0].grantee)",
        "grantee_configured": sc.get("grantee_client_id"), "engine_answer": sc.get("error") or "granted",
        "receipt": str(scopes[-1]) if scopes else None, "at": latest.get("at"),
        "what_closes_it": "Archaeon registers its Campaign-4 client on THIS ledger (P1) and tells Vivarium the client_id; "
                          "Vivarium sets read_scopes[0].grantee to it (a committed, non-secret config change + pin advance); "
                          "the next batch boundary grants every viv-* world. Not an engine-side action; not Daedalus's."}
    rec["outbox"] = outbox
    rec["ok_for_gate"] = {"identity_live": rec["checks"]["consumer_alive"]["ok"] and rec["checks"]["build_pinned"]["ok"]
                          and rec["checks"]["identity_is_the_owner_on_the_engine"]["ok"],
                          "read_grant_valid": rec["checks"]["b1_read_grant_to_archaeon"]["ok"]}
    body = json.dumps(rec, sort_keys=True, default=str).encode("utf-8")
    rec["digest"] = "sha256:" + hashlib.sha256(body).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"ok_for_gate": rec["ok_for_gate"], "digest": rec["digest"], "receipt": str(out_path)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
