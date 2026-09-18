"""Campaign 4 rehearsal C4-REH-1, stages S2-enqueue through S8: the executable half beyond
rehearsal.py (which builds and validates the bundle: S1, S2-validate).

    python -m archaeon.campaign4.rehearsal_full enqueue [--spacing 6] [--lead 20]
    python -m archaeon.campaign4.rehearsal_full go                      # S4: post GO to Daedalus
    python -m archaeon.campaign4.rehearsal_full wait [--timeout 3600]   # S3: rows to terminal
    python -m archaeon.campaign4.rehearsal_full verify                  # S3/S4/S5 from the register + engine
    python -m archaeon.campaign4.rehearsal_full publish                 # S6: artifacts under C4-REH-1/
    python -m archaeon.campaign4.rehearsal_full s7 --commit <sha>       # S7: PEW leg (Mnemosyne's tool)
    python -m archaeon.campaign4.rehearsal_full s8 --commit <sha>       # S8: reproduce RECEIPT.json
    python -m archaeon.campaign4.rehearsal_full receipt                 # REHEARSAL_RECEIPT.json S1..S8

REHEARSAL ONLY -- no scientific claim. Every row is Vivarium's `noop_v0` kind and every object
carries the label "REHEARSAL -- NOT EVIDENCE". The plan and its declared failure modes are
REHEARSAL_PLAN.md; the accounting invariants are in rehearsal/bundle/MANIFEST.json.

State is flushed to rehearsal/STATE_C4-REH-1.json after every mutation so an interrupted run
resumes from the register, never from memory. Timing decision (recorded here, not tuned after a
result): noop rows finish in about 3 s, so 48 rows back-to-back would drain in under 3 minutes,
faster than a restart posted by message can meet. Rows are therefore admitted with staggered
`not_before` (one every --spacing seconds after --lead seconds), which stretches the bundle to
about 5 minutes of near-continuous engine traffic. Pacing is a queue column, never a spec field,
so spec_hash and the accounting invariants are untouched.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C4 = REPO / "archaeon" / "campaign4"
BUNDLE = C4 / "rehearsal" / "bundle"
STATE = C4 / "rehearsal" / "STATE_C4-REH-1.json"
PUB = C4 / "C4-REH-1"
OUT = C4 / "REHEARSAL_RECEIPT.json"
REHEARSAL_ID = "C4-REH-1"
LABEL = "REHEARSAL -- NOT EVIDENCE"
PROTEUS_MINT = "proteus/eval/C4_STARTING_POPULATION_MANIFEST.json"
DAEDALUS_RECEIPT = "SerendipityFoundry/SerendipityFoundryEngine/deploy/REHEARSAL_RESTART_2026-09/restart_C4-REH-1.json"
# Two interruptions were executed: k1 landed BETWEEN rows (open_intents_at_kill []); k2 was armed on an
# event-density trigger and cut a request INSIDE the engine (an open A6 intent). Both are evidence.
DAEDALUS_RECEIPTS = {"k1": DAEDALUS_RECEIPT,
                     "k2": "SerendipityFoundry/SerendipityFoundryEngine/deploy/REHEARSAL_RESTART_2026-09/restart_C4-REH-1-k2.json"}
S7_SCRIPT = REPO / "evidence_wiki" / "integration" / "s7_rehearsal_leg.py"
S7_RESULTS = REPO / "evidence_wiki" / "integration" / "s7_rehearsal_results.json"
GO_BODY = REPO / "roles" / "Archaeon" / "prompts" / "2026-09-17_c4_convergence" / "02_DAEDALUS_S4_GO.md"
INSTANCE = "Archaeon[m2-49ee5a4d]"
TERMINAL = ("completed", "failed", "cancelled")

sys.path.insert(0, str(REPO / "vivarium"))
sys.path.insert(0, str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient"))


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def sha(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(p: Path) -> str:
    return str(p.relative_to(REPO)).replace("\\", "/")


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"_what_this_is": "C4-REH-1 rehearsal driver state; flushed after every mutation. " + LABEL,
            "rehearsal_id": REHEARSAL_ID, "driver": rel(Path(__file__)), "instance": INSTANCE}


def save_state(st: dict) -> None:
    st["updated_at"] = utc()
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")


def manifest() -> dict:
    return json.loads((BUNDLE / "MANIFEST.json").read_text(encoding="utf-8"))


def git(*args, timeout=120) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=timeout).stdout.strip()


def git_bytes(ref: str, path: str):
    r = subprocess.run(["git", "-C", str(REPO), "show", "%s:%s" % (ref, path)], capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def db():
    from viv import db as _db                                          # noqa: PLC0415
    return _db.connect()


def q(conn, sql, *args):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.rollback()
    return rows


# ---------------------------------------------------------------- S2 enqueue
def declared_bundle(spec: dict, unit: dict, pm: dict) -> dict:
    """The producer's start bundle: Vivarium's skeleton with the Campaign-4 population identity
    (Proteus's minted manifest, read from the tracked file) and the campaign rng identity."""
    from viv import bundle as _b                                       # noqa: PLC0415
    d = _b.declared_skeleton(spec)
    d["population"] = {"population_schema": pm["schema_version"], "manifest_hash": pm["manifest_hash"],
                       "manifest_ref": PROTEUS_MINT, "foundry_profile": pm["foundry_profile"]}
    d["rng"]["campaign_seed"] = manifest()["campaign_seed"]
    d["rng"]["rng_label"] = "%s/%s/s%d" % (REHEARSAL_ID, unit["arm"], unit["seed"])
    d["factors"] = {"harness": REHEARSAL_ID, "arm": unit["arm"], "label": LABEL}
    probs = _b.problems(d, spec=spec)
    if probs:
        raise SystemExit("declared bundle rejected by viv.bundle.problems: %s" % probs)
    return d


def cmd_enqueue(a) -> int:
    from viv import queue as _q, spec as _vspec, bundle as _b         # noqa: PLC0415
    st = load_state()
    mf = manifest()
    pm = json.loads((REPO / PROTEUS_MINT).read_text(encoding="utf-8"))["population_manifest"]
    ident = json.loads((C4 / "CAMPAIGN4_EXECUTION_IDENTITY.json").read_text(encoding="utf-8"))
    conn = db()
    t0 = _dt.datetime.now(_dt.timezone.utc)
    en = st.setdefault("enqueue", {"t0": t0.strftime("%Y-%m-%dT%H:%M:%SZ"), "spacing_s": a.spacing, "lead_s": a.lead,
                                   "created_by": "archaeon", "rows": {}})
    for i, u in enumerate(mf["units"]):
        if u["request_key"] in en["rows"]:
            continue
        spec = json.loads((REPO / u["file"]).read_text(encoding="utf-8"))
        nb = t0 + _dt.timedelta(seconds=a.lead + i * a.spacing)
        declared = declared_bundle(spec, u, pm)
        ev = {"rehearsal_id": REHEARSAL_ID, "label": LABEL, "unit_file": u["file"],
              "spec_sha256_canonical": u["spec_sha256_canonical"],
              "bundle_manifest_digest": sha((BUNDLE / "MANIFEST.json").read_bytes()),
              "identity_file_digest": sha((C4 / "CAMPAIGN4_EXECUTION_IDENTITY.json").read_bytes()),
              "engine_instance_id_expected": ident["tuple"]["daedalus"]["engine_instance_id"],
              "producer_instance": INSTANCE, "pacing": {"not_before": nb.strftime("%Y-%m-%dT%H:%M:%SZ"), "index": i}}
        try:
            eid = str(_q.enqueue(conn, created_by="archaeon",
                                 source_reason="%s integration rehearsal (%s): launch-gate item G2" % (REHEARSAL_ID, LABEL),
                                 experiment_spec=spec, source_evidence=ev, priority=100, not_before=nb,
                                 request_key=u["request_key"], family_id=u["family_id"], arm_id=u["arm_id"]))
            with conn.cursor() as cur:
                cur.execute("UPDATE viv.research_experiment_queue SET bundle_declared=%s WHERE experiment_id=%s AND status='queued'",
                            (json.dumps(declared), eid))
            conn.commit()
            how = "NEW"
        except _q.DuplicateRequest as exc:
            conn.rollback()
            eid = exc.experiment_id
            how = "EXISTING"
        h = _vspec.spec_hash(spec)
        en["rows"][u["request_key"]] = {"experiment_id": eid, "arm": u["arm"], "seed": u["seed"], "spec_hash": h,
                                        "world_name": _vspec.world_name(h), "not_before": nb.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                        "bundle_hash_declared": _b.bundle_hash(declared), "admitted": how}
        save_state(st)
        print("%-3d %s %s %s not_before=%s" % (i, how, u["request_key"], eid, en["rows"][u["request_key"]]["not_before"]), flush=True)
    en["finished_at"] = utc()
    en["units"] = len(en["rows"])
    save_state(st)
    print("enqueued %d units; last not_before %s" % (len(en["rows"]), nb.strftime("%H:%M:%SZ")))
    return 0


# ---------------------------------------------------------------- S4 go
def cmd_go(a) -> int:
    st = load_state()
    env = dict(os.environ)
    env.setdefault("EW_DB_HOST", "192.168.1.202")
    r = subprocess.run([sys.executable, "-m", "comms", "post", "--from", "Archaeon", "--to", "Daedalus", "--kind", "delegation",
                        "--subject", "S4 GO C4-REH-1 -- rows RUNNING on 8811; execute rehearsal_restart_m2.py --tag C4-REH-1 --relaunch watchdog; post the receipt path + sha256",
                        "--body-file", str(GO_BODY)], capture_output=True, text=True, timeout=120, env=env, cwd=str(REPO))
    st["go"] = {"posted_at": utc(), "stdout": r.stdout.strip()[-200:], "stderr": r.stderr.strip()[-200:], "rc": r.returncode,
                "body": rel(GO_BODY), "body_digest": sha(GO_BODY.read_bytes())}
    save_state(st)
    print(json.dumps(st["go"], indent=1))
    return r.returncode


# ---------------------------------------------------------------- S3 wait
def rows_now(conn) -> list:
    return q(conn, "SELECT experiment_id::text, request_key, arm_id, status, claimed_at, started_at, finished_at, "
                   "sfe_experiment_id, error FROM viv.research_experiment_queue WHERE family_id=%s ORDER BY not_before", REHEARSAL_ID)


def heartbeat(conn) -> dict:
    hb = q(conn, "SELECT worker_id, host, pid, last_seen, now()-last_seen AS age, current_experiment, build "
                 "FROM viv.worker_heartbeat WHERE worker_id='vivarium@m2'")
    return hb[0] if hb else {}


def cmd_wait(a) -> int:
    st = load_state()
    conn = db()
    w = st.setdefault("wait", {"started_at": utc(), "timeline": []})
    last = {}
    t0 = time.time()
    while True:
        rows = rows_now(conn)
        hb = heartbeat(conn)
        now = utc()
        for r in rows:
            key = r["request_key"]
            if last.get(key) != r["status"]:
                w["timeline"].append({"at": now, "unit": key, "status": r["status"], "experiment_id": r["experiment_id"]})
                last[key] = r["status"]
        var_dir = ((hb.get("build") or {}).get("var_dir")) if isinstance(hb.get("build"), dict) else None
        park = None
        if var_dir:
            pp = Path(var_dir) / "park-vivarium@m2.json"
            park = json.loads(pp.read_text(encoding="utf-8")) if pp.exists() else None
        hb_line = {"pid": hb.get("pid"), "age_s": round(hb["age"].total_seconds(), 1) if hb.get("age") is not None else None,
                   "current": hb.get("current_experiment"), "parked": bool(park), "park_reason": (park or {}).get("reason")}
        if w.get("last_hb") != hb_line:
            w["timeline"].append({"at": now, "consumer": hb_line})
            w["last_hb"] = hb_line
        counts = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        w["counts"] = counts
        save_state(st)
        print("%s %s consumer=%s" % (now, json.dumps(counts, sort_keys=True), json.dumps(hb_line, default=str)), flush=True)
        if rows and all(r["status"] in TERMINAL for r in rows):
            w["finished_at"] = now
            w["outcome"] = "ALL_TERMINAL"
            save_state(st)
            return 0
        if time.time() - t0 > a.timeout:
            w["finished_at"] = now
            w["outcome"] = "TIMEOUT"
            save_state(st)
            return 2
        time.sleep(a.poll)


# ---------------------------------------------------------------- S3/S4/S5 verify
def gather(conn) -> list:
    """Every register fact about the family: rows, attempts, steps. Raw, unjudged."""
    out = []
    for r in q(conn, "SELECT experiment_id::text, request_key, arm_id, status, priority, not_before, claimed_at, started_at, "
                     "finished_at, sfe_experiment_id, error, spec_hash, bundle_declared IS NOT NULL AS has_declared, result_summary "
                     "FROM viv.research_experiment_queue WHERE family_id=%s ORDER BY not_before", REHEARSAL_ID):
        atts = q(conn, "SELECT attempt_id::text, attempt_number, parent_attempt_id::text, terminal_state, termination, "
                       "bundle_hash, bundle_hash_declared, worker_id, opened_at, closed_at FROM viv.execution_attempt "
                       "WHERE experiment_id=%s ORDER BY attempt_number", r["experiment_id"])
        for at in atts:
            at["steps"] = q(conn, "SELECT step_kind, parts, status, replay_of_step IS NOT NULL AS is_replay, "
                                  "recomputed_from_step IS NOT NULL AS is_recompute, idempotency_key, result, started_at, completed_at "
                                  "FROM viv.execution_step WHERE attempt_id=%s ORDER BY started_at, step_id", at["attempt_id"])
        r["attempts"] = atts
        out.append(r)
    return out


def unit_facts(r: dict, repeats: int) -> dict:
    """What one unit's register rows say, reduced to the invariant's terms."""
    done = [a for a in r["attempts"] if a["terminal_state"] == "COMPLETED"]
    term = (done[0]["termination"] or {}) if done else {}
    ref = term.get("engine_termination_ref") or {}
    obs_by_attempt, statuses = {}, {}
    for a in r["attempts"]:
        ids = []
        for s in a["steps"]:
            statuses[s["status"]] = statuses.get(s["status"], 0) + 1
            if s["step_kind"] == "observe" and s["status"] in ("NEW", "REPLAYED") and isinstance(s["result"], str):
                ids.append(s["result"])
        obs_by_attempt[a["attempt_number"]] = ids
    all_obs = [o for ids in obs_by_attempt.values() for o in ids]
    world_ids = {(a["termination"] or {}).get("engine_termination_ref", {}).get("world_id")
                 for a in r["attempts"] if (a["termination"] or {}).get("engine_termination_ref")}
    world_ids.discard(None)
    return {"unit": r["request_key"], "experiment_id": r["experiment_id"], "status": r["status"],
            "attempts": len(r["attempts"]), "attempt_states": [a["terminal_state"] for a in r["attempts"]],
            "completed_attempts": len(done), "world_id": ref.get("world_id"), "exp_id": ref.get("exp_id"),
            "worlds_touched": sorted(world_ids),
            "observations_recorded": term.get("observations_recorded"), "termination_reason": term.get("termination_reason"),
            "censored": term.get("censored"), "distinct_obs_ids": len(set(all_obs)), "obs_ids_total": len(all_obs),
            "obs_ids": sorted(set(all_obs)), "step_statuses": statuses,
            "invariant": {"completed": r["status"] == "completed", "one_completed_attempt": len(done) == 1,
                          "exact_observations": term.get("observations_recorded") == repeats,
                          "one_world": len(world_ids) == 1, "no_duplicate_obs": len(set(all_obs)) == repeats,
                          "uncensored": term.get("censored") is False}}


def engine_client():
    from archaeon.campaign2.runner import Engine                       # noqa: PLC0415
    from archaeon.campaign4.c4base import CAMPAIGN_4                   # noqa: PLC0415
    return Engine(config=CAMPAIGN_4["config"], client_name=CAMPAIGN_4["client"])


def engine_check(units: list, repeats: int, wait_s: float) -> dict:
    """Exactly-once from the ENGINE's side, read with the Campaign 4 identity through the B1 grant.
    Worlds the consumer created enter Archaeon's read scope at the consumer's next batch
    boundary (viv/scope.py), so a world that is not readable yet is retried, then NOT_EXAMINED."""
    try:
        eng = engine_client()
    except Exception as exc:                                           # noqa: BLE001
        return {"status": "NOT_EXAMINED", "reason": "engine client: %s" % str(exc)[:200]}
    d = eng.descriptor
    out = {"engine_instance_id": d["engine_instance_id"], "engine_source_hash": d["engine_source_hash"],
           "schema_version": d["schema_version"], "worlds": {}, "not_readable": []}
    t0 = time.time()
    pending = [u for u in units if u["world_id"]]
    # The granted read (/v2/read/observations) returns EMPTY for a world outside every granted
    # scope, never 403; so an empty page is "not in scope yet", retried until wait_s elapses.
    while pending:
        still = []
        for u in pending:
            try:
                page = eng.c.read_observations(world_id=u["world_id"], limit=1000)
                obs = page.get("observations", []) if isinstance(page, dict) else []
                if not obs:
                    u["_err"] = "empty page (world not in a granted scope yet, or no observations)"
                    still.append(u)
                    continue
                ids = sorted({o.get("obs_id") or o.get("id") for o in obs})
                out["worlds"][u["unit"]] = {"world_id": u["world_id"], "n_obs": len(obs), "ids_match_register": ids == u["obs_ids"],
                                            "exact": len(obs) == repeats, "next_after_seq": page.get("next_after_seq"),
                                            "corpus": page.get("corpus")}
            except Exception as exc:                                   # noqa: BLE001
                u["_err"] = str(exc)[:160]
                still.append(u)
        pending = still
        if not pending or time.time() - t0 > wait_s:
            break
        time.sleep(15)
    try:
        sc = eng.c.read_worlds(limit=500)
        out["worlds_in_granted_scopes"] = len(sc.get("worlds", [])) if isinstance(sc, dict) else None
    except Exception as exc:                                           # noqa: BLE001
        out["worlds_in_granted_scopes"] = "error: %s" % str(exc)[:120]
    out["not_readable"] = [{"unit": u["unit"], "world_id": u["world_id"], "error": u.get("_err")} for u in pending]
    n = len(out["worlds"])
    out["examined"] = n
    out["all_exact"] = n > 0 and all(w["exact"] and w["ids_match_register"] for w in out["worlds"].values())
    out["status"] = "OK" if (out["all_exact"] and not pending) else ("PARTIAL" if n else "NOT_EXAMINED")
    return out


def _one_receipt(path: str, origin_main: str) -> dict:
    b = git_bytes("origin/main", path)
    if b is None:
        return {"status": "PENDING_RECEIPT", "path": path, "origin_main": origin_main}
    d = json.loads(b)
    inv = d.get("invariants") or {}
    # the receipt's invariants block is nested: a headline `ok`, sub-blocks with their own `ok`,
    # plain booleans, and descriptive dicts (ledger_after) that are not checks at all
    flat = {}
    for k, v in inv.items():
        if isinstance(v, bool):
            flat[k] = v
        elif isinstance(v, dict) and "ok" in v:
            flat[k] = bool(v["ok"])
    rec = {k: d.get(k) for k in ("recovery", "post", "retry")}
    if isinstance(rec.get("recovery"), dict):
        rec["recovery"] = {k: v for k, v in rec["recovery"].items() if k != "identities"}
    return {"status": "PRESENT", "path": path, "digest_lf_blob": sha(b), "origin_main": origin_main,
            "result": d.get("result"), "tag": d.get("tag"), "keys": sorted(d.keys()),
            "pre_events_last_60s": (d.get("pre") or {}).get("events_last_60s"),
            "interrupt": d.get("interrupt"), **rec, "invariants": flat,
            # `a6_degraded` is healthy when FALSE; every other flag is healthy when TRUE; the
            # receipt's own headline `ok` must also hold
            "invariants_all_true": bool(flat) and flat.get("ok") is True and flat.get("a6_degraded") is False
                                   and all(v is True for k, v in flat.items() if k not in ("ok", "a6_degraded")),
            "mid_request": bool((d.get("interrupt") or {}).get("open_intents_at_kill"))}


def daedalus_receipt() -> dict:
    """S4 evidence is Daedalus's committed receipts, read from origin/main after a fetch --
    never from a message. Absent = PENDING, and the seat says so. OK requires every receipt
    present with invariants true, and at least one kill that cut a request mid-flight."""
    git("fetch", "origin", timeout=300)
    om = git("rev-parse", "origin/main")
    recs = {tag: _one_receipt(p, om) for tag, p in DAEDALUS_RECEIPTS.items()}
    present = all(r["status"] == "PRESENT" for r in recs.values())
    inv_ok = present and all(r["invariants_all_true"] for r in recs.values())
    mid = any(r.get("mid_request") for r in recs.values())
    return {"status": "PRESENT" if present else "PENDING_RECEIPT", "path": DAEDALUS_RECEIPTS["k2"],
            "receipts": recs, "origin_main": om, "invariants_all_true": inv_ok, "mid_request_kill_present": mid,
            "digest": recs["k2"].get("digest_lf_blob"),
            "note": "digests are sha256 over the LF git blob (comms/manifest.py rule); a value quoted from a "
                    "CRLF working copy will differ and is not the artifact's identity"}


def cmd_verify(a) -> int:
    st = load_state()
    mf = manifest()
    repeats = mf["repeats_per_unit"]
    conn = db()
    raw = gather(conn)
    (C4 / "rehearsal").mkdir(exist_ok=True)
    units = [unit_facts(r, repeats) for r in raw]
    # S3
    s3 = {"units": len(units), "expected_units": len(mf["units"]),
          "completed": sum(1 for u in units if u["status"] == "completed"),
          "failed": [{"unit": u["unit"], "error": next((r["error"] for r in raw if r["request_key"] == u["unit"]), None)}
                     for u in units if u["status"] == "failed"],
          "sfe_experiment_ids_distinct": len({u["exp_id"] for u in units if u["exp_id"]})}
    s3["status"] = "OK" if (s3["units"] == s3["expected_units"] and s3["completed"] == s3["units"]) else "FAILED"
    # S5 accounting invariants (declared in MANIFEST before any row)
    inv = mf["accounting_invariants"]
    total_obs = sum(u["observations_recorded"] or 0 for u in units)
    worlds = [u["world_id"] for u in units if u["world_id"]]
    step_census = {}
    for u in units:
        for k, v in u["step_statuses"].items():
            step_census[k] = step_census.get(k, 0) + v
    multi = [u for u in units if u["attempts"] > 1]
    s5 = {"observations_total": total_obs, "observations_exactly": inv["observations_exactly"],
          "worlds_distinct": len(set(worlds)), "worlds_expected": len(units) * inv["worlds_per_unit"],
          "units_violating": [{"unit": u["unit"], "invariant": {k: v for k, v in u["invariant"].items() if not v}}
                              for u in units if not all(u["invariant"].values())],
          "units_with_more_than_one_attempt": [{"unit": u["unit"], "attempt_states": u["attempt_states"],
                                                "step_statuses": u["step_statuses"]} for u in multi],
          "step_status_census": step_census,
          # a REPLAYED observe step re-yields the id attempt 1 minted (the keyed retry working);
          # it is not a second mint. Duplicates are DISTINCT ids beyond the declared repeats,
          # in the register and (below) on the engine.
          "register_distinct_ids_beyond_repeats": sum(max(0, u["distinct_obs_ids"] - repeats) for u in units),
          "observe_steps_replayed": sum(u["step_statuses"].get("REPLAYED", 0) for u in units),
          "observe_steps_total": sum(u["obs_ids_total"] for u in units)}
    s5["engine"] = engine_check(units, repeats, a.engine_wait)
    s5["duplicates_minted"] = (s5["register_distinct_ids_beyond_repeats"]
                               + sum(max(0, w["n_obs"] - repeats) for w in (s5["engine"].get("worlds") or {}).values()))
    s5["register_invariants_hold"] = (total_obs == inv["observations_exactly"] and len(set(worlds)) == s5["worlds_expected"]
                                      and not s5["units_violating"])
    s5["status"] = "OK" if (s5["register_invariants_hold"] and s5["engine"]["status"] == "OK") else "FAILED"
    # S4: the interruption, from Daedalus's committed receipt + what the register saw
    s4 = {"daedalus": daedalus_receipt(), "go": st.get("go"),
          "register_saw_interruption": len(multi) > 0,
          "units_resumed": [u["unit"] for u in multi],
          "consumer_timeline": [e for e in (st.get("wait") or {}).get("timeline", []) if "consumer" in e]}
    dd = s4["daedalus"]
    s4["status"] = ("OK" if (dd["status"] == "PRESENT" and dd["invariants_all_true"] and dd["mid_request_kill_present"])
                    else ("PENDING_RECEIPT" if dd["status"] == "PENDING_RECEIPT" else "FAILED"))
    st["verify"] = {"at": utc(), "S3": s3, "S4": s4, "S5": s5, "units": units}
    save_state(st)
    (C4 / "rehearsal" / "REGISTER_C4-REH-1.json").write_text(
        json.dumps({"_what_this_is": "raw register rows for the rehearsal family (queue, attempts, steps). " + LABEL,
                    "gathered_at": utc(), "rows": raw}, indent=1, sort_keys=True, default=str) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({"S3": s3, "S4": {k: v for k, v in s4.items() if k != "consumer_timeline"},
                      "S5": {k: v for k, v in s5.items() if k != "engine"}, "S5.engine": {k: v for k, v in s5["engine"].items() if k != "worlds"}},
                     indent=1, default=str))
    return 0 if (s3["status"] == "OK" and s5["status"] == "OK" and s4["status"] == "OK") else 1


# ---------------------------------------------------------------- S6 publish
def derive_receipt(rows: list, mf: dict, ident: dict, restart: dict, s7: dict | None) -> dict:
    """RECEIPT.json is a PURE FUNCTION of committed inputs (rows.json, MANIFEST.json, the identity
    file, Daedalus's receipt digest, the S7 results). No generation timestamp; S8 recomputes it."""
    units = sorted(rows, key=lambda u: (u["arm"], u["seed"]))
    records = {"%s/s%d" % (u["arm"], u["seed"]): {"exp_id": u["exp_id"], "obs_id": (u["obs_ids"] or [None])[0],
                                                  "world_id": u["world_id"], "n_obs": u["observations_recorded"]} for u in units}
    worlds = {"%s/s%d" % (u["arm"], u["seed"]): u["world_id"] for u in units}
    started = min((u["started_at"] for u in units if u.get("started_at")), default=None)
    finished = max((u["finished_at"] for u in units if u.get("finished_at")), default=None)
    return {
        "_what_this_is": "Campaign 4 integration rehearsal receipt. %s" % LABEL,
        "campaign": "cmp4", "campaign_seed": mf["campaign_seed"], "experiment": REHEARSAL_ID,
        "attempt": 1, "attempt_id": REHEARSAL_ID + "/attempt-1",
        "purpose": "launch-gate item G2: one exact tuple of frozen surfaces carries a Campaign-4-shaped unit of work "
                   "from enqueue to reproduced receipt through an engine restart, without losing, duplicating or "
                   "silently corrupting a fact. No scientific claim.",
        "hypothesis": "REHEARSAL ONLY -- no scientific content.",
        "engine": ident["tuple"]["daedalus"], "engine_path": True,
        "identity": {"file": "archaeon/campaign4/CAMPAIGN4_EXECUTION_IDENTITY.json", "tuple": ident["tuple"]},
        "bundle": {"manifest": "archaeon/campaign4/rehearsal/bundle/MANIFEST.json", "units": len(mf["units"]),
                   "repeats_per_unit": mf["repeats_per_unit"], "expected_observations": mf["expected_observations"],
                   "accounting_invariants": mf["accounting_invariants"]},
        "worlds": worlds, "records": records,
        "started_at": started, "finished_at": finished,
        "interruption": restart,
        "pew_leg": s7,
        "summary": {"units": len(units), "completed": sum(1 for u in units if u["status"] == "completed"),
                    "observations_total": sum(u["observations_recorded"] or 0 for u in units),
                    "worlds_distinct": len({u["world_id"] for u in units if u["world_id"]}),
                    "units_resumed_after_interruption": [ "%s/s%d" % (u["arm"], u["seed"]) for u in units if u["attempts"] > 1],
                    "step_status_census": _census(units)},
        "typed_states": {"rehearsal": "PASS" if all(all(u["invariant"].values()) for u in units) else "FAILED"},
        "workspace_note": "built in a task worktree; base_sha/branch recorded in REHEARSAL_RECEIPT.json",
    }


def _census(units: list) -> dict:
    c = {}
    for u in units:
        for k, v in (u.get("step_statuses") or {}).items():
            c[k] = c.get(k, 0) + v
    return c


def cmd_publish(a) -> int:
    st = load_state()
    v = st.get("verify")
    if not v:
        raise SystemExit("run verify first")
    mf = manifest()
    ident = json.loads((C4 / "CAMPAIGN4_EXECUTION_IDENTITY.json").read_text(encoding="utf-8"))
    PUB.mkdir(exist_ok=True)
    en = st["enqueue"]["rows"]
    rows = []
    for u in v["units"]:
        e = en[u["unit"]]
        rows.append({**u, "arm": e["arm"], "seed": e["seed"], "spec_hash": e["spec_hash"], "world_name": e["world_name"],
                     "not_before": e["not_before"], "bundle_hash_declared": e["bundle_hash_declared"],
                     "started_at": _iso(v, u["unit"], "started_at"), "finished_at": _iso(v, u["unit"], "finished_at")})
    (PUB / "rows.json").write_text(json.dumps({"label": LABEL, "rehearsal_id": REHEARSAL_ID, "rows": rows}, indent=1,
                                              sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    dd = v["S4"]["daedalus"]
    restart = {"status": dd.get("status"), "invariants_all_true": dd.get("invariants_all_true"),
               "mid_request_kill_present": dd.get("mid_request_kill_present"), "origin_main": dd.get("origin_main"),
               "receipts": {tag: {k: r.get(k) for k in ("path", "digest_lf_blob", "result", "mid_request", "invariants_all_true", "interrupt", "recovery")}
                            for tag, r in (dd.get("receipts") or {}).items()}}
    s7 = st.get("s7")
    rec = derive_receipt(rows, mf, ident, restart, s7)
    (PUB / "RECEIPT.json").write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    (PUB / "RECORD.md").write_text(record_md(rec, v), encoding="utf-8", newline="\n")
    st["publish"] = {"at": utc(), "files": [rel(PUB / n) for n in ("rows.json", "RECEIPT.json", "RECORD.md")],
                     "receipt_digest": sha((PUB / "RECEIPT.json").read_bytes()), "rows_digest": sha((PUB / "rows.json").read_bytes())}
    save_state(st)
    print(json.dumps(st["publish"], indent=1))
    return 0


def _iso(v: dict, unit: str, key: str):
    # timestamps live in the raw register dump, keyed by request_key
    reg = json.loads((C4 / "rehearsal" / "REGISTER_C4-REH-1.json").read_text(encoding="utf-8"))
    for r in reg["rows"]:
        if r["request_key"] == unit:
            return r.get(key)
    return None


def record_md(rec: dict, v: dict) -> str:
    L = ["+" + "=" * 69 + "+",
         "|  CAMPAIGN 4 -- INTEGRATION REHEARSAL C4-REH-1 (%s)   |" % LABEL,
         "+" + "=" * 69 + "+", "",
         "This directory holds the rehearsal's rows and receipt so that PEW's",
         "campaign-4 reader has campaign-4 rows to ingest (S7). Nothing here is",
         "evidence about any hypothesis; the work kind is noop_v0.", "",
         "units %d  completed %d  observations %d  worlds %d" % (
             rec["summary"]["units"], rec["summary"]["completed"], rec["summary"]["observations_total"], rec["summary"]["worlds_distinct"]),
         "units resumed after the interruption: %s" % (", ".join(rec["summary"]["units_resumed_after_interruption"]) or "none"),
         "step status census: %s" % json.dumps(rec["summary"]["step_status_census"], sort_keys=True),
         "interruptions (Daedalus receipts on origin/main %s): %s" % (
             (rec["interruption"].get("origin_main") or "?")[:9],
             "; ".join("%s %s%s" % (tag, r.get("result"), " MID-REQUEST" if r.get("mid_request") else " between rows")
                       for tag, r in sorted((rec["interruption"].get("receipts") or {}).items()))),
         "typed state: %s" % rec["typed_states"]["rehearsal"], "",
         "S3 %s  S4 %s  S5 %s" % (v["S3"]["status"], v["S4"]["status"], v["S5"]["status"]), ""]
    return "\n".join(L)


# ---------------------------------------------------------------- S7 / S8
def cmd_s7(a) -> int:
    st = load_state()
    commit = git("rev-parse", a.commit)
    env = dict(os.environ)
    env.setdefault("EW_DB_HOST", "192.168.1.202")
    env.setdefault("PROMETHEUS_MACHINE", "M2")
    r = subprocess.run([sys.executable, str(S7_SCRIPT), "--commit", commit], capture_output=True, text=True,
                       timeout=3600, env=env, cwd=str(REPO / "evidence_wiki"))
    res = json.loads(S7_RESULTS.read_text(encoding="utf-8")) if S7_RESULTS.exists() else None
    st["s7"] = {"at": utc(), "commit": commit, "rc": r.returncode, "results_file": rel(S7_RESULTS),
                "results_digest": sha(S7_RESULTS.read_bytes()) if S7_RESULTS.exists() else None,
                "all_pass": (res or {}).get("all_pass"), "gates": [{k: g.get(k) for k in ("gate", "pass", "skipped")} for g in (res or {}).get("gates", [])],
                "stdout_tail": r.stdout[-1500:], "stderr_tail": r.stderr[-800:]}
    st["s7"]["status"] = "OK" if (r.returncode == 0 and st["s7"]["all_pass"] is True) else "FAILED"
    save_state(st)
    print(r.stdout[-3000:])
    print(json.dumps({k: st["s7"][k] for k in ("commit", "rc", "all_pass", "status", "gates")}, indent=1))
    return 0 if st["s7"]["status"] == "OK" else 1


def cmd_s8(a) -> int:
    """Re-derive RECEIPT.json from the COMMITTED inputs alone and compare byte-for-byte."""
    st = load_state()
    commit = git("rev-parse", a.commit)
    def need(p):
        b = git_bytes(commit, p)
        if b is None:
            raise SystemExit("S8: %s absent at %s" % (p, commit))
        return b
    rows = json.loads(need("archaeon/campaign4/C4-REH-1/rows.json"))["rows"]
    mf = json.loads(need("archaeon/campaign4/rehearsal/bundle/MANIFEST.json"))
    ident = json.loads(need("archaeon/campaign4/CAMPAIGN4_EXECUTION_IDENTITY.json"))
    committed = need("archaeon/campaign4/C4-REH-1/RECEIPT.json")
    committed_doc = json.loads(committed)
    rec = derive_receipt(rows, mf, ident, committed_doc["interruption"], committed_doc["pew_leg"])
    mine = (json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n").encode("utf-8")
    # compare canonical semantics AND bytes (the committed blob is LF; the checkout may be CRLF)
    same_bytes = mine == committed.replace(b"\r\n", b"\n")
    same_canon = canon(rec) == canon(committed_doc)
    st["s8"] = {"at": utc(), "commit": commit, "receipt_digest_committed": sha(committed.replace(b"\r\n", b"\n")),
                "receipt_digest_rederived": sha(mine), "bytes_equal": same_bytes, "canonical_equal": same_canon,
                "status": "OK" if (same_bytes and same_canon) else "FAILED"}
    save_state(st)
    print(json.dumps(st["s8"], indent=1))
    return 0 if st["s8"]["status"] == "OK" else 1


# ---------------------------------------------------------------- the receipt the gate reads
def cmd_receipt(a) -> int:
    from archaeon.campaign4 import rehearsal as R                      # noqa: PLC0415
    from archaeon.campaign4.c4base import CAMPAIGN_SEED                # noqa: PLC0415
    st = load_state()
    v = st.get("verify") or {}
    conn = db()
    held = q(conn, "SELECT experiment_id::text, status, not_before FROM viv.research_experiment_queue "
                   "WHERE created_by='archaeon' AND status='queued' AND family_id IS NULL")
    grant = q(conn, "SELECT 1")  # placeholder so the connection is exercised before the read proof below
    g3 = json.loads((C4 / "G3_READ_PROOF.json").read_text(encoding="utf-8")) if (C4 / "G3_READ_PROOF.json").exists() else {}
    pre = [
        {"id": "P1", "what": "campaign 4 engine credential (archaeon/campaign4/config.local.json)",
         "present": (C4 / "config.local.json").exists(), "owner": "operator / Daedalus", "blocks": ["S3", "S4", "S5", "S6", "S7", "S8"]},
        {"id": "P2", "what": "B1 read grant for the Campaign 4 identity on the M2 ledger (superseded wording: cli_2bb36261 was the M1-era "
                             "grantee; the live grantee is cmp4-archaeon cli_6354da5b, Vivarium #399)",
         "present": bool(g3.get("all_pass")), "evidence": "archaeon/campaign4/G3_READ_PROOF.json", "owner": "Vivarium", "blocks": ["S3"]},
        {"id": "P3", "what": "deliberate mid-run engine restart, executed and receipted by Daedalus",
         "present": (v.get("S4") or {}).get("status") == "OK", "evidence": DAEDALUS_RECEIPT, "owner": "Daedalus + Vivarium", "blocks": ["S4", "S5"]},
        {"id": "P4", "what": "PEW ingest/rebuild/release-check leg", "present": (st.get("s7") or {}).get("status") == "OK",
         "evidence": rel(S7_RESULTS), "owner": "Mnemosyne (tool); run by Archaeon with Mnemosyne's written consent, comms #391", "blocks": ["S7"]},
        {"id": "P5", "what": "Archaeon's five campaign-3 viv rows stay HELD (must not be swept in)",
         "present": len(held) == 5 and all(str(h["not_before"]).startswith("2026-12-31") or str(h["not_before"]).startswith("2027") for h in held),
         "evidence": [{"experiment_id": h["experiment_id"][:8], "not_before": str(h["not_before"])} for h in held], "owner": "Archaeon", "blocks": []},
    ]
    # S1: the bundle on disk must equal the bundle the rows were admitted from
    mf_digest = sha((BUNDLE / "MANIFEST.json").read_bytes())
    admitted_from = {r["spec_hash"] for r in (st.get("enqueue") or {}).get("rows", {}).values()}
    s2v = R.s2_validate()
    s1 = {"stage": "S1", "status": "OK" if (BUNDLE / "MANIFEST.json").exists() else "FAILED", "units": len(manifest()["units"]),
          "bundle_manifest": rel(BUNDLE / "MANIFEST.json"), "bundle_digest": mf_digest,
          "note": "bundle built by the previous instance (m2-411504ab) and not rebuilt; validated again below"}
    s2v["status"] = "OK" if (s2v.get("all_valid") and {r["spec_hash"] for r in s2v["rows"]} == admitted_from) else "FAILED"
    s2v["admitted_spec_hashes_match_bundle"] = {r["spec_hash"] for r in s2v["rows"]} == admitted_from
    s2v["rows"] = [{k: r[k] for k in ("arm", "seed", "spec_hash", "valid")} for r in s2v["rows"]]
    en = st.get("enqueue") or {}
    s2 = {"stage": "S2", "status": "OK" if en.get("units") == len(manifest()["units"]) else "FAILED",
          "units_admitted": en.get("units"), "pacing": {"lead_s": en.get("lead_s"), "spacing_s": en.get("spacing_s"), "t0": en.get("t0")},
          "created_by": en.get("created_by"), "family_id": REHEARSAL_ID,
          "experiment_ids": {k: r["experiment_id"] for k, r in en.get("rows", {}).items()}}
    def stage(name, d, keep):
        d = d or {}
        return {"stage": name, "status": d.get("status", "BLOCKED"), **{k: d.get(k) for k in keep if k in d}}
    s3 = stage("S3", v.get("S3"), ("units", "expected_units", "completed", "failed", "sfe_experiment_ids_distinct"))
    s4d = (v.get("S4") or {})
    s4 = stage("S4", s4d, ("register_saw_interruption", "units_resumed", "go"))
    s4["daedalus_receipts"] = {k: (s4d.get("daedalus") or {}).get(k) for k in ("status", "origin_main", "invariants_all_true", "mid_request_kill_present", "receipts", "note")}
    s5d = v.get("S5") or {}
    s5 = stage("S5", s5d, ("observations_total", "observations_exactly", "worlds_distinct", "worlds_expected", "units_violating",
                            "units_with_more_than_one_attempt", "step_status_census", "duplicates_minted", "register_invariants_hold"))
    s5["engine"] = {k: (s5d.get("engine") or {}).get(k) for k in ("status", "examined", "all_exact", "not_readable", "engine_instance_id", "engine_source_hash")}
    s6 = stage("S6", st.get("publish"), ("files", "receipt_digest", "rows_digest", "at"))
    s6["status"] = "OK" if st.get("publish") else "BLOCKED"
    s7 = stage("S7", st.get("s7"), ("commit", "rc", "all_pass", "gates", "results_file", "results_digest"))
    s8 = stage("S8", st.get("s8"), ("commit", "receipt_digest_committed", "receipt_digest_rederived", "bytes_equal", "canonical_equal"))
    stages = [s1, s2v, s2, s3, s4, s5, s6, s7, s8]
    ws = {"base_sha": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"), "worktree_path": str(REPO),
          "dirty": bool(git("status", "--porcelain", "--untracked-files=no"))}
    receipt = {
        "_what_this_is": "Campaign 4 synthetic end-to-end rehearsal receipt. REHEARSAL ONLY -- no scientific claim.",
        "generated_at": utc(), "generated_by": INSTANCE, "stage_mode": "full", "campaign_seed": CAMPAIGN_SEED,
        "identity": R.identity(), "plan": "archaeon/campaign4/REHEARSAL_PLAN.md",
        "driver": rel(Path(__file__)), "state": rel(STATE), "register_dump": "archaeon/campaign4/rehearsal/REGISTER_C4-REH-1.json",
        "stages": stages, "preconditions": pre, "workspace": ws,
        "pass_rule": "S5 invariant holds AND S7 rebuild digests stable AND S8 reproduces (REHEARSAL_PLAN.md s3)",
        "pass": all(s["status"] == "OK" for s in stages),
    }
    OUT.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"stages": {s["stage"]: s["status"] for s in stages}, "pass": receipt["pass"],
                      "preconditions": {p["id"]: p["present"] for p in pre}}, indent=1))
    print("written:", OUT, "sha256:", hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0 if receipt["pass"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("enqueue"); s.add_argument("--spacing", type=float, default=6.0); s.add_argument("--lead", type=float, default=20.0); s.set_defaults(fn=cmd_enqueue)
    s = sub.add_parser("go"); s.set_defaults(fn=cmd_go)
    s = sub.add_parser("wait"); s.add_argument("--timeout", type=float, default=3600.0); s.add_argument("--poll", type=float, default=5.0); s.set_defaults(fn=cmd_wait)
    s = sub.add_parser("verify"); s.add_argument("--engine-wait", type=float, default=240.0); s.set_defaults(fn=cmd_verify)
    s = sub.add_parser("publish"); s.set_defaults(fn=cmd_publish)
    s = sub.add_parser("s7"); s.add_argument("--commit", default="HEAD"); s.set_defaults(fn=cmd_s7)
    s = sub.add_parser("s8"); s.add_argument("--commit", default="HEAD"); s.set_defaults(fn=cmd_s8)
    s = sub.add_parser("receipt"); s.set_defaults(fn=cmd_receipt)
    a = ap.parse_args(argv)
    from archaeon import workspace                                     # noqa: PLC0415
    workspace.assert_not_canonical("campaign 4 rehearsal driver")
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
