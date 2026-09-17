#!/usr/bin/env python3
"""D11 (point release 2026-09): the RESTART / DUPLICATE / CHECKPOINT fixture.

    python test_harness/longrun_restart.py [--engine-dir DIR] [--port 8931] [--n 300]
                                           [--receipt PATH] [--base URL --token TOK]

Runs a REAL engine process of the candidate tree on loopback with a disposable
ledger (never production), drives it through the lifecycle the operator's order
names, kills the process mid-run, relaunches it, and checks that nothing was
lost, duplicated or re-identified:

    create (manifest + labels) -> write (experiments/observations with
    logical_time + Idempotency-Key, world events, artifacts) -> checkpoint ->
    read -> duplicate posts (same key, 3 threads) -> kill -9 -> relaunch ->
    identity unchanged -> resume cursor traversal from a saved position ->
    fork two children -> artifact list -> clean termination with facts ->
    verify-anchor on every OBSERVATION_RECORDED.

Every check is recorded as a SHAPE with counts in the receipt (a failed
shape is a finding, not a red X). Exit 0 iff every shape held.

With --base/--token it runs the same sequence against an ALREADY RUNNING
engine and SKIPS the kill/relaunch (used for post-deploy qualification on
production, where the engine restart is done by the supervisor, not by a
test).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ENGINE = os.path.normpath(os.path.join(HERE, "..", "..", "SerendipityFoundryEngine"))
HDR = "X-SFE-Session"


class Api:
    def __init__(self, base, token=None, cafile=None):
        self.base = base.rstrip("/")
        self.token = token
        self.session_key = None
        self.ctx = None
        if cafile:
            import ssl
            self.ctx = ssl.create_default_context(cafile=cafile)

    def req(self, method, path, body=None, headers=None, timeout=20):
        h = {"content-type": "application/json"}
        if self.token:
            h["authorization"] = "Bearer " + self.token
        if self.session_key:
            h[HDR] = self.session_key
        h.update(headers or {})
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=timeout) as z:
                return z.status, json.loads(z.read().decode() or "null")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode() or "null")

    def ok(self, method, path, body=None, headers=None):
        st, out = self.req(method, path, body, headers)
        if st != 200:
            raise RuntimeError("%s %s -> %s %s" % (method, path, st, json.dumps(out)[:300]))
        return out


def port_free(port):
    s = socket.socket(); s.settimeout(1)
    try:
        return s.connect_ex(("127.0.0.1", port)) != 0
    finally:
        s.close()


def wait_version(api, seconds=30):
    t0 = time.time()
    while time.time() - t0 < seconds:
        try:
            st, v = api.req("GET", "/v2/version")
            if st == 200:
                return v
        except Exception:                                   # noqa: BLE001
            pass
        time.sleep(0.25)
    raise RuntimeError("engine did not answer /v2/version in %ss" % seconds)


def launch(engine_dir, db, port, log):
    return subprocess.Popen(
        [sys.executable, os.path.join(engine_dir, "serve.py"), "--db", db,
         "--host", "127.0.0.1", "--port", str(port), "--insecure",
         "--registration", "open", "--max-artifact-bytes", "33554432"],
        cwd=engine_dir, stdout=log, stderr=subprocess.STDOUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine-dir", default=DEFAULT_ENGINE)
    ap.add_argument("--port", type=int, default=8931)
    ap.add_argument("--n", type=int, default=300, help="experiments+observations before the kill")
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--base", default=None, help="run against a RUNNING engine (no kill/relaunch)")
    ap.add_argument("--token", default=None)
    ap.add_argument("--cafile", default=None)
    a = ap.parse_args()
    rec = {"fixture": "longrun_restart", "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "mode": "running-engine" if a.base else "scratch-process", "shapes": [], "timings_s": {}}
    ok_all = True

    def shape(name, passed, **detail):
        nonlocal ok_all
        ok_all = ok_all and bool(passed)
        rec["shapes"].append({"shape": name, "held": bool(passed), **detail})
        print("  [%s] %s  %s" % ("HELD" if passed else "BROKE", name,
                                 " ".join("%s=%s" % kv for kv in detail.items())[:160]))

    tmp = None
    proc = None
    log = None
    try:
        if a.base:
            api = Api(a.base, a.token, a.cafile)
        else:
            if not port_free(a.port):
                print("REFUSING: port %d is held (never aim this at a live engine)" % a.port)
                return 2
            tmp = tempfile.mkdtemp(prefix="sfe_longrun_")
            db = os.path.join(tmp, "scratch.db")
            log = open(os.path.join(tmp, "engine.log"), "ab")
            proc = launch(a.engine_dir, db, a.port, log)
            api = Api("http://127.0.0.1:%d" % a.port)
            t0 = time.time()
            v0 = wait_version(api)
            rec["timings_s"]["first_start"] = round(time.time() - t0, 2)
            api.token = api.ok("POST", "/v2/clients", {"name": "longrun"})["token"]
        v0 = api.ok("GET", "/v2/version")
        cap = api.ok("GET", "/v2/capabilities")
        rec["engine_before"] = {k: v0.get(k) for k in ("engine_instance_id", "engine_source_hash", "schema_version")}
        shape("capabilities agrees with version on identity",
              cap["engine_instance_id"] == v0["engine_instance_id"] and cap["engine_source_hash"] == v0["engine_source_hash"],
              schema=cap["schema_version"])

        # ---- create
        sess = api.ok("POST", "/v2/sessions", {"name": "longrun"})
        api.session_key = sess["session_key"]
        man = {"kind": "fixture.longrun", "logical_time_unit": "generation",
               "declared_event_kinds": ["phase", "pressure", "import.realized"]}
        w = api.ok("POST", "/v2/worlds", {"session_id": sess["session_id"], "name": "longrun",
                                          "manifest": man, "manifest_schema": "fixture/1",
                                          "labels": {"attempt": "longrun/a01"}, "seed_root": 12345},
                   headers={"Idempotency-Key": "idem:world:longrun"})
        wid = w["world_id"]
        shape("manifest hash sealed on create", bool(w["manifest_hash"]) and w["labels"] == {"attempt": "longrun/a01"})
        api.ok("POST", "/v2/worlds/%s/start" % wid)

        # ---- write
        t0 = time.time()
        obs_ids, exp_ids = [], []
        for i in range(a.n):
            e = api.ok("POST", "/v2/worlds/%s/experiments" % wid, {"spec": {"i": i}},
                       headers={"Idempotency-Key": "idem:exp:%d" % i})["exp_id"]
            api.ok("POST", "/v2/worlds/%s/experiments/%s/commit" % (wid, e), {})
            o = api.ok("POST", "/v2/worlds/%s/observations" % wid,
                       {"exp_id": e, "content": {"score": (i % 10) / 10.0}, "outcome": "SURVIVED",
                        "logical_time": i}, headers={"Idempotency-Key": "idem:obs:%d" % i})
            obs_ids.append(o["obs_id"]); exp_ids.append(e)
            if i % 25 == 0:
                api.ok("POST", "/v2/worlds/%s/events" % wid,
                       {"kind": "phase", "logical_time": i, "payload": {"phase": i // 25}},
                       headers={"Idempotency-Key": "idem:phase:%d" % i})
        rec["timings_s"]["write_%d" % a.n] = round(time.time() - t0, 2)
        api.ok("POST", "/v2/worlds/%s/events" % wid,
               {"kind": "import.realized", "logical_time": a.n,
                "payload": {"requested_dose": 4, "realized_dose": 4, "origin_shares": {"import": 0.02}}})
        st, out = api.req("POST", "/v2/worlds/%s/events" % wid, {"kind": "undeclared", "payload": {}})
        shape("undeclared event kind refused under a declaring manifest", st == 422, status=st)
        art_ids = []
        for k in range(5):
            r = api.ok("POST", "/v2/worlds/%s/artifacts" % wid,
                       {"kind": "trace", "data_b64": base64.b64encode(os.urandom(2048)).decode()},
                       headers={"Idempotency-Key": "idem:art:%d" % k})
            art_ids.append(r["artifact_id"])

        # ---- checkpoint + read
        head_at_ck = api.ok("GET", "/v2/worlds/%s" % wid)["head_hash"]
        t0 = time.time()
        ck = api.ok("POST", "/v2/worlds/%s/checkpoint" % wid)
        rec["timings_s"]["checkpoint"] = round(time.time() - t0, 3)
        shape("checkpoint carries the chain head it captured and a state digest",
              ck["head_hash"] == head_at_ck and bool(ck["state_hash"]), world_index=ck["world_index"])

        # ---- duplicate posts: same key, three threads, one row
        results = []
        def dup():
            results.append(api.req("POST", "/v2/worlds/%s/observations" % wid,
                                   {"exp_id": exp_ids[0], "content": {"dup": True}, "outcome": "SURVIVED",
                                    "replication": True, "logical_time": 1},
                                   headers={"Idempotency-Key": "idem:dup:1"}))
        ts = [threading.Thread(target=dup) for _ in range(3)]
        [t.start() for t in ts]; [t.join() for t in ts]
        codes = sorted(r[0] for r in results)
        ids = {r[1].get("obs_id") for r in results if r[0] == 200}
        n_obs_dup = len(api.ok("GET", "/v2/worlds/%s/observations" % wid, headers=None)["observations"])
        shape("duplicate concurrent posts under one key yield one row",
              codes.count(200) >= 1 and len(ids) == 1 and n_obs_dup == a.n + 1,
              codes=codes, distinct_ids=len(ids), observations=n_obs_dup)

        # ---- a cursor position saved BEFORE the restart
        page = api.ok("GET", "/v2/worlds/%s/observations?after_seq=0&limit=100" % wid)
        saved_cursor = page["next_after_seq"]
        first_page_ids = [o["obs_id"] for o in page["observations"]]
        events_before = api.ok("GET", "/v2/worlds/%s/events?after_seq=0&limit=1000" % wid)["events"]
        head_before = api.ok("GET", "/v2/worlds/%s" % wid)["head_hash"]   # the last write before the kill

        # ---- KILL and RELAUNCH (scratch mode only)
        if proc is not None:
            t0 = time.time()
            proc.kill(); proc.wait(timeout=30)
            rec["timings_s"]["kill_to_port_free"] = None
            for _ in range(100):
                if port_free(a.port):
                    rec["timings_s"]["kill_to_port_free"] = round(time.time() - t0, 2); break
                time.sleep(0.1)
            t1 = time.time()
            proc = launch(a.engine_dir, db, a.port, log)
            v1 = wait_version(api)
            rec["timings_s"]["relaunch_to_version"] = round(time.time() - t1, 2)
            shape("identity unchanged across a kill -9 and relaunch",
                  v1["engine_instance_id"] == v0["engine_instance_id"]
                  and v1["engine_source_hash"] == v0["engine_source_hash"]
                  and v1["schema_version"] == v0["schema_version"],
                  instance=v1["engine_instance_id"], schema=v1["schema_version"])
            # session keys are ledger state: still valid
            st, _ = api.req("GET", "/v2/worlds/%s" % wid)
            shape("session key survives the restart", st == 200, status=st)
        else:
            shape("kill/relaunch SKIPPED (running-engine mode)", True)

        # ---- resume traversal from the saved cursor; compare to a full walk
        head_after = api.ok("GET", "/v2/worlds/%s" % wid)["head_hash"]
        shape("head hash unchanged across restart", head_after == head_before)
        rest, after = [], saved_cursor
        pages = 0
        while after is not None:
            p = api.ok("GET", "/v2/worlds/%s/observations?after_seq=%d&limit=100" % (wid, after))
            rest += [o["obs_id"] for o in p["observations"]]; after = p["next_after_seq"]; pages += 1
        full, after, = [], 0
        while after is not None:
            p = api.ok("GET", "/v2/worlds/%s/observations?after_seq=%d&limit=250" % (wid, after))
            full += [o["obs_id"] for o in p["observations"]]; after = p["next_after_seq"]
        shape("cursor resume after restart == full walk (no gap, no dup)",
              first_page_ids + rest == full and len(set(full)) == len(full) == a.n + 1,
              resumed_pages=pages, rows=len(full))
        events_after = api.ok("GET", "/v2/worlds/%s/events?after_seq=0&limit=1000" % wid)["events"]
        shape("event history byte-identical across restart",
              [(e["event_seq"], e["entry_hash"]) for e in events_before]
              == [(e["event_seq"], e["entry_hash"]) for e in events_after], events=len(events_after))
        lts = [o["logical_time"] for o in api.ok("GET", "/v2/worlds/%s/observations?after_seq=0&limit=1000" % wid)["observations"]]
        shape("logical_time preserved on every row", lts[:a.n] == list(range(a.n)), sample=lts[:3])

        # ---- duplicate post AFTER restart replays, never re-writes
        r2 = api.ok("POST", "/v2/worlds/%s/observations" % wid,
                    {"exp_id": exp_ids[0], "content": {"dup": True}, "outcome": "SURVIVED",
                     "replication": True, "logical_time": 1}, headers={"Idempotency-Key": "idem:dup:1"})
        shape("idempotent replay after restart returns the original id", r2["obs_id"] in ids)

        # ---- fork two children at the checkpoint
        kids = api.ok("POST", "/v2/worlds/%s/fork" % wid, {"checkpoint_id": ck["checkpoint_id"], "children": [
            {"name": "same"}, {"name": "pressureQ", "manifest": {**man, "pressure": "Q"}, "manifest_schema": "fixture/1",
                               "interventions": {"pressure": "Q"}}]})["children"]
        ev_q = api.ok("GET", "/v2/worlds/%s/events?after_seq=0&limit=5" % kids[1]["world_id"])["events"]
        forked = [e for e in ev_q if e["event_type"] == "WORLD_FORKED"]
        shape("fork ancestry explicit: parent, fork_point, changed-field diff",
              all(k["parent_world_id"] == wid and k["fork_point"] == ck["world_index"] for k in kids)
              and forked and "manifest_hash" in forked[0]["payload"]["changed"]
              and kids[0]["manifest_hash"] == w["manifest_hash"],
              changed=list(forked[0]["payload"]["changed"]) if forked else None)

        # ---- artifact list
        al = api.ok("GET", "/v2/worlds/%s/artifacts" % wid)
        shape("artifact list matches what was posted", [x["artifact_id"] for x in al["artifacts"]] == art_ids,
              listed=len(al["artifacts"]))

        # ---- clean termination with facts
        t = api.ok("POST", "/v2/worlds/%s/terminate" % wid,
                   {"reason": "fixture:horizon", "logical_time": a.n, "horizon": a.n,
                    "budget_consumed": {"observations": a.n + 1}, "reference": "longrun/a01"})
        st, _ = api.req("POST", "/v2/worlds/%s/events" % wid, {"kind": "phase", "payload": {}})
        shape("termination facts recorded and writes refused afterwards",
              t["termination"]["reason"] == "fixture:horizon" and st == 409, post_terminate_status=st)

        # ---- verify-anchor on every OBSERVATION_RECORDED
        n_ok = 0
        obs_events = [e for e in events_after if e["event_type"] == "OBSERVATION_RECORDED"]
        for e in obs_events:
            st, out = api.req("POST", "/v2/audit/verify-anchor",
                              {"world_id": wid, "event_id": e["event_id"], "entry_hash": e["entry_hash"],
                               "obs_id": e["refs"]["obs_id"]})
            n_ok += int(st == 200 and out.get("valid") is True)
        shape("every observation anchor verifies", n_ok == len(obs_events), verified=n_ok, total=len(obs_events))
        rec["engine_after"] = {k: v for k, v in api.ok("GET", "/v2/version").items()
                               if k in ("engine_instance_id", "engine_source_hash", "schema_version")}
    finally:
        if proc is not None:
            proc.kill()
            try: proc.wait(timeout=10)
            except Exception: pass                                   # noqa: BLE001
        if log:
            log.close()
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["held"] = sum(1 for s_ in rec["shapes"] if s_["held"])
    rec["broke"] = sum(1 for s_ in rec["shapes"] if not s_["held"])
    print("\n  %d shapes held, %d broke; timings %s" % (rec["held"], rec["broke"], json.dumps(rec["timings_s"])))
    if a.receipt:
        os.makedirs(os.path.dirname(os.path.abspath(a.receipt)), exist_ok=True)
        json.dump(rec, open(a.receipt, "w", encoding="utf-8"), indent=1)
        print("  receipt: %s" % a.receipt)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
