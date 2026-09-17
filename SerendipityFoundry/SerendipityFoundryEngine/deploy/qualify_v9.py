#!/usr/bin/env python3
"""Post-restart qualification of the schema-9 production engine (order s9).

    python deploy/qualify_v9.py [--out DIR]

Runs, in order, against https://192.168.1.191:8811 and records each as a
SHAPE with numbers (a failed shape is a finding, never a red X):

    1. old-schema READ compatibility: pre-v9 worlds/observations read NULL
       facts; head hashes of the 5 oldest worlds unchanged vs the preflight
       backup; verify-anchor on 20 pre-migration OBSERVATION_RECORDED events
    2. the standing batteries: harness 12, isolation 7 (subprocess)
    3. contract gate: conformance_check.py on the regenerated contract (0)
    4. the v9 surface on a throwaway world on PRODUCTION (registered client
       "qualify-v9-<ts>"): capabilities, manifest round-trip, logical_time
       write/read, generic event ordering + idempotent duplicate, typed
       termination, artifact list, pagination traversal + resume, checkpoint
       digest + fork ancestry, advisory cross-session read, strict extra-
       field rejection
    5. the D11 fixture in running-engine mode (kill/relaunch skipped: the
       restart was performed by the supervisor and recorded by release_v9)

Everything it writes to production is under its own client and a world it
terminates; nothing of any other client's is touched.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sqlite3
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "SerendipityFoundryClient", "test_harness"))
from relocate_m2 import DATA, HOST, PORT                          # noqa: E402
from longrun_restart import Api                                    # noqa: E402

BASE = "https://%s:%d" % (HOST, PORT)
CA = os.path.join(DATA, "m2.crt")
DB = os.path.join(DATA, "engine.db")
CLIENT = os.path.normpath(os.path.join(HERE, "..", "..", "SerendipityFoundryClient"))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PY = sys.executable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "POINT_RELEASE_2026-09-17"))
    ap.add_argument("--preflight", default=os.path.join(HERE, "POINT_RELEASE_2026-09-17", "preflight.json"))
    a = ap.parse_args()
    rec = {"phase": "qualify", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "shapes": []}
    ok_all = True

    def shape(name, held, **d):
        nonlocal ok_all
        ok_all = ok_all and bool(held)
        rec["shapes"].append({"shape": name, "held": bool(held), **d})
        print("  [%s] %s %s" % ("HELD" if held else "BROKE", name, json.dumps(d)[:180]))

    api = Api(BASE, cafile=CA)
    v = api.ok("GET", "/v2/version")
    rec["engine"] = v
    shape("engine is schema 9 on the production ledger", v["schema_version"] == 9 and v["engine_instance_id"] == "eng_906356f7fb1da180131f9290")

    # ---- 1. old-schema read compatibility
    pre = json.load(open(a.preflight, encoding="utf-8"))
    bak = pre["backup"]["path"]
    live = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True); live.row_factory = sqlite3.Row
    old = sqlite3.connect("file:%s?mode=ro" % bak.replace("\\", "/"), uri=True); old.row_factory = sqlite3.Row
    cols = {r["name"] for r in live.execute("PRAGMA table_info(worlds)")}
    shape("v9 columns present", {"manifest", "manifest_hash", "labels", "termination"} <= cols
          and "logical_time" in {r["name"] for r in live.execute("PRAGMA table_info(observations)")})
    # The two "pre-migration facts read NULL" shapes are a property of the 8->9
    # MIGRATION (no backfill), so they hold only when the backup is a schema-8
    # ledger. On a code-only release over a schema-9 ledger (9.0.1) worlds
    # created after the migration legitimately carry manifests / labels /
    # logical_time, and the checks misreported BROKE (RELEASE_9_0_1 qualify.json,
    # 16/18). Gate them on the BACKUP's schema, and say so in the receipt.
    bak_schema = int((old.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone() or ["0"])[0])
    rec["backup_schema_version"] = bak_schema
    if bak_schema < 9:
        n_old_worlds = old.execute("SELECT COUNT(*) FROM worlds").fetchone()[0]
        nulls = live.execute("SELECT COUNT(*) FROM worlds WHERE manifest IS NULL AND labels IS NULL AND termination IS NULL "
                             "AND world_id IN (SELECT world_id FROM worlds ORDER BY created_ts LIMIT ?)", (n_old_worlds,)).fetchone()[0]
        shape("every pre-migration world reads NULL facts (no backfill)", nulls == n_old_worlds, worlds=n_old_worlds)
        n_old_obs = old.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        onull = live.execute("SELECT COUNT(*) FROM observations WHERE logical_time IS NULL").fetchone()[0]
        shape("every pre-migration observation reads logical_time NULL", onull >= n_old_obs, old=n_old_obs, null_now=onull)
    else:
        rec["shapes_not_applicable"] = ["every pre-migration world reads NULL facts (no backfill)",
                                        "every pre-migration observation reads logical_time NULL"]
        print("  [N/A ] the two 8->9 no-backfill shapes: backup is already schema %d (code-only release)" % bak_schema)
    heads_old = {r["world_id"]: r["head_hash"] for r in old.execute("SELECT world_id, head_hash FROM worlds ORDER BY created_ts LIMIT 25")}
    heads_new = {r["world_id"]: r["head_hash"] for r in live.execute("SELECT world_id, head_hash FROM worlds WHERE world_id IN (%s)"
                                                                    % ",".join("?" * len(heads_old)), tuple(heads_old))}
    shape("head hashes of the 25 oldest worlds unchanged", heads_old == heads_new, n=len(heads_old))
    ev_old = old.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    ev_new_at_backup = live.execute("SELECT COUNT(*) FROM events WHERE event_seq <= ?",
                                    (old.execute("SELECT MAX(event_seq) FROM events").fetchone()[0],)).fetchone()[0]
    shape("event count up to the backup's last seq identical", ev_old == ev_new_at_backup, events=ev_old)
    # verify-anchor on 20 pre-migration observation events needs a token: use the throwaway client below
    sample = [dict(r) for r in old.execute("SELECT world_id, event_id, entry_hash, refs FROM events WHERE event_type='OBSERVATION_RECORDED' ORDER BY event_seq DESC LIMIT 20")]
    old.close(); live.close()

    # ---- 4. the v9 surface on a throwaway world (also gives us a token for 1's anchors and 3's gate)
    tag = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    api.token = api.ok("POST", "/v2/clients", {"name": "qualify-v9-" + tag})["token"]
    n_ok = 0
    for e in sample:
        st, out = api.req("POST", "/v2/audit/verify-anchor", {"world_id": e["world_id"], "event_id": e["event_id"],
                                                             "entry_hash": e["entry_hash"], "obs_id": json.loads(e["refs"]).get("obs_id")})
        n_ok += int(st == 200 and out.get("valid") is True)
    shape("pre-migration observation anchors verify", n_ok == len(sample), verified=n_ok, total=len(sample))
    cap = api.ok("GET", "/v2/capabilities")
    shape("capabilities route: schema 9, features, read semantics, no forbidden words",
          cap["schema_version"] == 9 and all(cap["features"].values()) and cap["read_semantics"]["advisory"]["no_key"] == "ADMITTED_AUDITED"
          and not any(w in json.dumps(cap).upper() for w in ("SHELF", "SUMMIT", "CORRIDOR", "TAKEOVER", "GENERALIZATION")))
    sess = api.ok("POST", "/v2/sessions", {"name": "qualify"})
    api.session_key = sess["session_key"]
    man = {"kind": "qualify", "logical_time_unit": "generation", "declared_event_kinds": ["phase", "import.realized"]}
    w = api.ok("POST", "/v2/worlds", {"session_id": sess["session_id"], "name": "qualify-v9", "manifest": man,
                                      "manifest_schema": "qualify/1", "labels": {"attempt": "qualify/" + tag}, "seed_root": 1})
    wid = w["world_id"]
    got = api.ok("GET", "/v2/worlds/%s/manifest" % wid)
    shape("manifest hash round-trip", got["manifest"] == man and got["manifest_hash"] == w["manifest_hash"] and w["labels"]["attempt"].startswith("qualify/"))
    api.ok("POST", "/v2/worlds/%s/start" % wid)
    exps = []
    for i in range(12):
        e = api.ok("POST", "/v2/worlds/%s/experiments" % wid, {"spec": {"i": i}}, headers={"Idempotency-Key": "q:%s:e%d" % (tag, i)})["exp_id"]
        api.ok("POST", "/v2/worlds/%s/experiments/%s/commit" % (wid, e), {})
        api.ok("POST", "/v2/worlds/%s/observations" % wid, {"exp_id": e, "content": {"i": i}, "outcome": "SURVIVED", "logical_time": i * 10},
               headers={"Idempotency-Key": "q:%s:o%d" % (tag, i)})
        exps.append(e)
    obs = api.ok("GET", "/v2/worlds/%s/observations" % wid)["observations"]
    shape("logical_time write/read", [o["logical_time"] for o in obs] == [i * 10 for i in range(12)])
    a1 = api.ok("POST", "/v2/worlds/%s/events" % wid, {"kind": "phase", "logical_time": 30, "payload": {"phase": 1}}, headers={"Idempotency-Key": "q:%s:ev1" % tag})
    a2 = api.ok("POST", "/v2/worlds/%s/events" % wid, {"kind": "import.realized", "logical_time": 40, "payload": {"requested_dose": 4, "realized_dose": 3}})
    a1b = api.ok("POST", "/v2/worlds/%s/events" % wid, {"kind": "phase", "logical_time": 30, "payload": {"phase": 1}}, headers={"Idempotency-Key": "q:%s:ev1" % tag})
    st_bad, _ = api.req("POST", "/v2/worlds/%s/events" % wid, {"kind": "not.declared", "payload": {}})
    shape("generic events: ordered, idempotent duplicate, undeclared kind refused", a2["world_index"] == a1["world_index"] + 1 and a1b == a1 and st_bad == 422)
    # pagination traversal + resume
    walk, after, pages = [], 0, 0
    while after is not None:
        p = api.ok("GET", "/v2/worlds/%s/events?after_seq=%d&limit=10" % (wid, after)); walk += p["events"]; after = p["next_after_seq"]; pages += 1
    full = api.ok("GET", "/v2/worlds/%s/events?after_seq=0&limit=1000" % wid)["events"]
    resume = api.ok("GET", "/v2/worlds/%s/events?after_seq=%d&limit=1000" % (wid, walk[9]["event_seq"]))["events"]
    shape("pagination traversal == single page; resume from a cursor exact",
          [e["event_seq"] for e in walk] == [e["event_seq"] for e in full] and [e["event_seq"] for e in resume] == [e["event_seq"] for e in full[10:]],
          pages=pages, events=len(full))
    # artifact list
    aid = api.ok("POST", "/v2/worlds/%s/artifacts" % wid, {"kind": "trace", "data_b64": base64.b64encode(b"qualify").decode()})["artifact_id"]
    al = api.ok("GET", "/v2/worlds/%s/artifacts" % wid)["artifacts"]
    shape("artifact list", [x["artifact_id"] for x in al] == [aid] and al[0]["kind"] == "trace")
    # checkpoint digest + fork ancestry + changed diff
    ck = api.ok("POST", "/v2/worlds/%s/checkpoint" % wid)
    kids = api.ok("POST", "/v2/worlds/%s/fork" % wid, {"checkpoint_id": ck["checkpoint_id"], "children": [
        {"name": "q-same"}, {"name": "q-Q", "manifest": {**man, "pressure": "Q"}, "manifest_schema": "qualify/1", "interventions": {"p": "Q"}}]})["children"]
    fev = [e for e in api.ok("GET", "/v2/worlds/%s/events?after_seq=0&limit=5" % kids[1]["world_id"])["events"] if e["event_type"] == "WORLD_FORKED"][0]
    shape("checkpoint digest + fork ancestry + changed-field diff",
          bool(ck["state_hash"]) and all(k["parent_world_id"] == wid and k["fork_point"] == ck["world_index"] for k in kids)
          and "manifest_hash" in fev["payload"]["changed"] and kids[0]["manifest_hash"] == w["manifest_hash"])
    # advisory cross-session read: no key admitted, wrong key refused, strict extra field refused
    saved = api.session_key
    api.session_key = None
    st_nokey, _ = api.req("GET", "/v2/worlds/%s/observations" % wid)
    s2 = api.ok("POST", "/v2/sessions", {"name": "other"})
    api.session_key = s2["session_key"]
    st_wrong, _ = api.req("GET", "/v2/worlds/%s/observations" % wid)
    api.session_key = saved
    st_extra, _ = api.req("POST", "/v2/worlds/%s/observations" % wid, {"exp_id": exps[0], "content": {}, "outcome": "SURVIVED", "bogus": 1})
    shape("advisory read semantics + strict extra-field rejection", st_nokey == 200 and st_wrong in (403, 421) and st_extra == 422,
          nokey=st_nokey, wrongkey=st_wrong, extra=st_extra)
    # typed termination
    t = api.ok("POST", "/v2/worlds/%s/terminate" % wid, {"reason": "qualify:horizon", "logical_time": 110, "horizon": 120, "reference": "qualify/" + tag})
    st_after, _ = api.req("POST", "/v2/worlds/%s/events" % wid, {"kind": "phase", "payload": {}})
    shape("typed termination write/read; writes refused after", t["termination"]["horizon"] == 120
          and api.ok("GET", "/v2/worlds/%s" % wid)["termination"]["reason"] == "qualify:horizon" and st_after == 409)
    for k in kids:
        api.ok("POST", "/v2/worlds/%s/terminate" % k["world_id"], {"reason": "qualify:cleanup"})

    # ---- 2. the standing batteries (subprocess), 3. the gate, 5. the D11 fixture in running-engine mode
    def run(cmd, cwd, name):
        t0 = time.time()
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
        rec.setdefault("subprocess", {})[name] = {"rc": p.returncode, "s": round(time.time() - t0, 1), "tail": tail}
        return p.returncode, "\n".join(tail)
    rc, tail = run([PY, "test_harness/harness.py", "--base-url", BASE, "--cafile", "config/m2.crt"], CLIENT, "harness")
    shape("harness 12/12", rc == 0 and "12/12" in tail, tail=tail[-80:])
    rc, tail = run([PY, "test_harness/isolation_two_experimenters.py", "--base-url", BASE, "--cafile", "config/m2.crt"], CLIENT, "isolation")
    shape("isolation 7/7", rc == 0 and "7/7" in tail, tail=tail[-80:])
    rc, tail = run([PY, "roles/Harmonia/contracts/conformance_check.py", "--contract", "roles/Harmonia/contracts/sfe_contract.json",
                    "--cacert", CA], ROOT, "gate")
    shape("contract gate CONFORMANT (0)", rc == 0 and "CONFORMANT" in tail, tail=tail[-80:])
    rc, tail = run([PY, "test_harness/longrun_restart.py", "--base", BASE, "--token", api.token, "--cafile", CA, "--n", "150",
                    "--receipt", os.path.join(a.out, "longrun_restart_production.json")], CLIENT, "longrun_restart")
    shape("D11 fixture (running-engine mode) all shapes held", rc == 0, tail=tail[-100:])

    rec["ok"] = ok_all
    rec["held"] = sum(1 for s in rec["shapes"] if s["held"]); rec["broke"] = sum(1 for s in rec["shapes"] if not s["held"])
    os.makedirs(a.out, exist_ok=True)
    json.dump(rec, open(os.path.join(a.out, "qualify.json"), "w", encoding="utf-8"), indent=1)
    print("\n  QUALIFICATION: %d held, %d broke  -> %s" % (rec["held"], rec["broke"], os.path.join(a.out, "qualify.json")))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
