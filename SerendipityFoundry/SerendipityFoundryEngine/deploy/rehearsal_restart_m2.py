"""The DELIBERATE mid-run engine restart for Archaeon's Campaign-4 rehearsal
(S4/S5), executed and receipted by the engine seat.

    python deploy/rehearsal_restart_m2.py --tag <rehearsal id> [--relaunch watchdog|now]
                                          [--min-inflight-events N] [--out <dir>]

What it records (the S4 requirement, PREPARE_C4 / rehearsal plan s95-99):
  pre        last confirmed operation before the kill: max event_seq, its
             event_id/type/world/ts, work_items by status, A6 intents open at
             that instant (from the journal files, not the process)
  interrupt  T0 of the kill (listener + its cmd.exe parent), port-free time
  recovery   who relaunched (the 5-min watchdog tick, or Start-ScheduledTask
             when --relaunch now), first /v2/version answer, identity 13-tuple
             equal to the pin (build hash, instance id, schema, route digest)
  post       first successful post-restart operation: the first event with
             seq > pre.max_event_seq (id/type/world/ts) and how long after T0;
             polled for --wait-post seconds
  retry      A6 view of the interruption: intents that had no outcome at T0
             and their attest() state after recovery; keyed replays after T0
             that resolved to an existing row (the consumer's retry landing
             on the original id) -- counted from the events + attestation
             journal, never inferred from logs
  invariants events monotonic (no seq reused, count only grew); the chain
             links for every world touched after `pre` (each event's prev_hash
             == previous entry_hash of that world, first post-restart link ==
             the pre-restart head); no (world, world_index) duplicated;
             A6 journal not degraded; checkpointer alive
Refuses to kill when the engine is idle if --min-inflight-events > 0 and
fewer events than that landed in the last 60 s: a restart that intersects
no live work rehearses nothing (the plan's own rule).
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from relocate_m2 import DATA, HOST, PORT, TASK, version, ps                # noqa: E402
from release_v9 import get, identities, ledger_facts, DB, CA                # noqa: E402
sys.path.insert(0, os.path.dirname(HERE))
from sfe.events import _entry_hash                                          # noqa: E402

PIN = json.load(open(os.path.join(HERE, "DEPLOYED_BUILD_M2.json"), encoding="utf-8"))
INCIDENTS = os.path.join(DATA, "incidents")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ro():
    cx = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True, timeout=20)
    cx.row_factory = sqlite3.Row
    return cx


def event_at(seq):
    with ro() as cx:
        r = cx.execute("SELECT event_seq, event_id, event_type, world_id, ts, actor FROM events WHERE event_seq=?", (seq,)).fetchone()
        return dict(r) if r else None


def first_event_after(seq):
    with ro() as cx:
        r = cx.execute("SELECT event_seq, event_id, event_type, world_id, ts, actor FROM events WHERE event_seq>? ORDER BY event_seq LIMIT 1", (seq,)).fetchone()
        return dict(r) if r else None


def events_since(t):
    with ro() as cx:
        return cx.execute("SELECT COUNT(*) FROM events WHERE ts>?", (t,)).fetchone()[0]


def journal_records():
    recs = []
    for n in sorted(os.listdir(INCIDENTS)) if os.path.isdir(INCIDENTS) else []:
        if n.endswith(".jsonl"):
            with open(os.path.join(INCIDENTS, n), encoding="ascii") as fh:
                for ln in fh:
                    try:
                        recs.append(json.loads(ln))
                    except ValueError:
                        pass
    return recs


def open_intents(recs, before_ts=None):
    by = {}
    for r in recs:
        s = by.setdefault(r["rid"], {})
        s["intent" if r["kind"] == "intent" else "outcome"] = r
    out = []
    for rid, s in by.items():
        i = s.get("intent")
        if i and "outcome" not in s and (before_ts is None or i["ts"] <= before_ts):
            out.append({"rid": rid, "route": i.get("route"), "idem_key": i.get("idem_key"), "ts": i.get("ts")})
    return out


def listener_pid():
    rc, out = ps("(Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue).OwningProcess" % PORT)
    s = (out or "").strip()
    return int(s) if s.isdigit() else None


def chain_check(after_seq):
    """Every world touched after `after_seq`: links hold from the pre-restart
    head through every later event; entry hashes recompute."""
    out = {"worlds": 0, "events_checked": 0, "link_breaks": [], "hash_mismatches": [], "dup_index": []}
    with ro() as cx:
        wids = [r[0] for r in cx.execute("SELECT DISTINCT world_id FROM events WHERE event_seq>?", (after_seq,))]
        out["worlds"] = len(wids)
        for wid in wids:
            rows = cx.execute("SELECT * FROM events WHERE world_id=? ORDER BY world_index", (wid,)).fetchall()
            seen = set()
            prev = None
            for r in rows:
                if r["world_index"] in seen:
                    out["dup_index"].append((wid, r["world_index"]))
                seen.add(r["world_index"])
                if r["event_seq"] > after_seq or (prev is not None and prev["event_seq"] <= after_seq and r["event_seq"] > after_seq):
                    out["events_checked"] += 1
                    if prev is not None and r["prev_hash"] != prev["entry_hash"]:
                        out["link_breaks"].append((wid, r["world_index"]))
                    h = _entry_hash(wid, r["world_index"], r["event_type"], r["ts"], r["actor"],
                                    json.loads(r["payload"]), json.loads(r["refs"]), json.loads(r["causal"]),
                                    json.loads(r["artifacts"]), r["prev_hash"])
                    if h != r["entry_hash"]:
                        out["hash_mismatches"].append((wid, r["world_index"]))
                prev = r
    out["ok"] = not (out["link_breaks"] or out["hash_mismatches"] or out["dup_index"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--relaunch", choices=("watchdog", "now"), default="watchdog")
    ap.add_argument("--min-inflight-events", type=int, default=1)
    ap.add_argument("--wait-post", type=float, default=900.0, help="seconds to wait for the first post-restart operation")
    ap.add_argument("--out", default=os.path.join(HERE, "REHEARSAL_RESTART_2026-09"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    rec = {"schema": "sfe_rehearsal_restart.v1", "tag": a.tag, "started_at": now(), "relaunch": a.relaunch, "pin": {
        "engine_source_hash": PIN["engine_source_hash"], "engine_instance_id": PIN["engine_instance_id"],
        "schema_version": PIN["schema_version"], "route_digest": PIN.get("route_digest")}}
    path = os.path.join(a.out, "restart_%s.json" % a.tag.replace("/", "_"))

    def save():
        with open(path, "w", encoding="ascii") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True, default=str)

    # ---- pre
    live = version()
    if not live:
        print("REFUSING: engine does not answer"); return 2
    lf = ledger_facts()
    inflight_60s = events_since(time.time() - 60)
    pre = {"identities": identities(), "ledger": lf, "last_event": event_at(lf["max_event_seq"]),
           "events_last_60s": inflight_60s, "a6_open_intents": open_intents(journal_records()),
           "health": get("/v2/health")}
    rec["pre"] = pre
    save()
    print("PRE   max_event_seq %d  last %s %s  events_last_60s %d  open_intents %d" % (
        lf["max_event_seq"], (pre["last_event"] or {}).get("event_type"), (pre["last_event"] or {}).get("world_id"),
        inflight_60s, len(pre["a6_open_intents"])))
    if inflight_60s < a.min_inflight_events:
        rec["result"] = "REFUSED_NO_LIVE_WORK"
        save()
        print("REFUSING: %d events in the last 60 s < %d; a restart that intersects no live work rehearses nothing" % (inflight_60s, a.min_inflight_events))
        return 3

    # ---- interrupt
    pid = listener_pid()
    t0 = time.time()
    rec["interrupt"] = {"t0": t0, "t0_utc": now(), "listener_pid": pid}
    ps("$p = Get-CimInstance Win32_Process -Filter 'ProcessId=%d'; Stop-Process -Id %d -Force; "
       "if ($p.ParentProcessId) { Stop-Process -Id $p.ParentProcessId -Force -ErrorAction SilentlyContinue }" % (pid, pid))
    while listener_pid() is not None and time.time() - t0 < 60:
        time.sleep(0.2)
    rec["interrupt"]["port_free_after_s"] = round(time.time() - t0, 2)
    rec["interrupt"]["open_intents_at_kill"] = open_intents(journal_records())
    save()
    print("KILL  pid %s at %s; port free after %.2f s; intents open at kill %d" % (
        pid, rec["interrupt"]["t0_utc"], rec["interrupt"]["port_free_after_s"], len(rec["interrupt"]["open_intents_at_kill"])))

    # ---- recovery
    if a.relaunch == "now":
        ps("Start-ScheduledTask -TaskName %s" % TASK)
    live2 = None
    while time.time() - t0 < 420:
        live2 = version(timeout=3)
        if live2:
            break
        time.sleep(1)
    rec["recovery"] = {"answered_after_s": round(time.time() - t0, 1) if live2 else None, "version": live2}
    if not live2:
        rec["result"] = "ENGINE_DID_NOT_RETURN_IN_420S"; save()
        print("FAIL  engine did not return within 420 s"); return 4
    ids = identities()
    same = {k: ids.get(k) == pre["identities"].get(k) for k in ("engine_instance_id", "engine_source_hash", "schema_version", "route_digest", "routes", "bind")}
    same["pin_engine_source_hash"] = ids["engine_source_hash"] == PIN["engine_source_hash"]
    same["new_process"] = ids.get("pid") != pre["identities"].get("pid")
    rec["recovery"]["identities"] = ids
    rec["recovery"]["identity_checks"] = same
    save()
    print("UP    after %.1f s (%s); identity checks %s" % (rec["recovery"]["answered_after_s"], a.relaunch, json.dumps(same)))

    # ---- post: first successful operation after the restart
    first = None
    t_wait = time.time()
    while time.time() - t_wait < a.wait_post:
        first = first_event_after(lf["max_event_seq"])
        if first:
            break
        time.sleep(2)
    rec["post"] = {"first_event_after_restart": first,
                   "first_op_after_t0_s": round(first["ts"] - t0, 1) if first else None}
    print("POST  first event %s %s %s after %s s" % ((first or {}).get("event_type"), (first or {}).get("world_id"),
                                                     (first or {}).get("event_id"), rec["post"]["first_op_after_t0_s"]))
    # ---- retry view (A6): intents open at kill -> attest states now; keyed replays after T0
    recs = journal_records()
    by = {}
    for r in recs:
        by.setdefault(r["rid"], {})["intent" if r["kind"] == "intent" else "outcome"] = r
    retry = {"open_at_kill": [], "keyed_replays_after_t0": 0, "refused_after_t0": 0, "effected_after_t0": 0}
    for oi in rec["interrupt"]["open_intents_at_kill"]:
        s = by.get(oi["rid"], {})
        o = s.get("outcome")
        retry["open_at_kill"].append({"rid": oi["rid"], "route": oi["route"], "idem_key": oi["idem_key"],
                                      "outcome_now": (o or {}).get("kind"), "ref": (o or {}).get("ref")})
    for rid, s in by.items():
        i, o = s.get("intent"), s.get("outcome")
        if i and i["ts"] > t0 and o:
            if o["kind"] == "effected":
                retry["effected_after_t0"] += 1
            elif o["kind"] == "refused":
                retry["refused_after_t0"] += 1
            if i.get("idem_key") and o["kind"] == "effected" and any(
                    s2.get("intent", {}).get("idem_key") == i["idem_key"] and s2["intent"]["ts"] <= t0 for s2 in by.values()):
                retry["keyed_replays_after_t0"] += 1
    rec["retry"] = retry
    # ---- invariants
    lf2 = ledger_facts()
    inv = {"events_monotonic": lf2["events"] >= lf["events"] and lf2["max_event_seq"] >= lf["max_event_seq"]
           and lf2["events"] - lf["events"] == lf2["max_event_seq"] - lf["max_event_seq"],
           "chain": chain_check(lf["max_event_seq"]),
           "a6_degraded": get("/v2/health")["attestation"]["degraded"],
           "checkpointer_alive": get("/v2/health")["checkpointer"]["alive"],
           "ledger_after": lf2}
    inv["ok"] = inv["events_monotonic"] and inv["chain"]["ok"] and not inv["a6_degraded"] and inv["checkpointer_alive"] and all(same.values())
    rec["invariants"] = inv
    rec["result"] = "PASS" if inv["ok"] and first else ("PASS_NO_POST_OP_SEEN" if inv["ok"] else "INVARIANT_FAILED")
    rec["finished_at"] = now()
    save()
    print("INV   monotonic %s  chain %s (worlds %d, events %d)  a6_degraded %s  ckpt %s" % (
        inv["events_monotonic"], inv["chain"]["ok"], inv["chain"]["worlds"], inv["chain"]["events_checked"], inv["a6_degraded"], inv["checkpointer_alive"]))
    print("RESULT %s  receipt %s" % (rec["result"], path))
    return 0 if rec["result"].startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
