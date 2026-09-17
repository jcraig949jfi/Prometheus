"""The s14 CANARY: one Campaign-shaped harness through the PRODUCTION consumer,
production queue `viv`, production engine, as the production identity --
with a negative control and a deliberate mid-run death + NEW ATTEMPT.

    A  gate FAIL control      pre_execution gate reads a producer-supplied
                              measurement below its measured reference ->
                              FAILED / PREREQUISITE_FAILED, gate receipt FAIL
                              committed, NO world created
    B  gate PASS, 3 repeats   ca_density_v0 (GKL, 149 cells, 300 steps, 400
                              ICs) x3 -> COMPLETED, 3 observations, every
                              step NEW, envelope not censored, labels recorded
    C  resume                 5 heavier repeats; the consumer process is KILLED
                              while running (pid from its heartbeat), the row
                              released --new-attempt, the dead-man task relaunches
                              the consumer; attempt 2 REUSES the world and the
                              experiment, REPLAYS the observations attempt 1
                              recorded, computes the rest -> COMPLETED with
                              exactly 5 observations on the engine, ONE world

Everything is checked from the queue's own tables and from the engine's read
routes (as the owning `vivarium` identity; worlds are owned, other clients get 403). The receipt is written per
check as it lands, so a stall leaves a partial record, not nothing. This
script never reads or prints a token value.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("EW_DB_HOST", "192.168.1.202"); os.environ.setdefault("VIV_DB_HOST", "192.168.1.202")
HERE = Path(__file__).resolve().parent
VIVARIUM = HERE.parent
REPO = VIVARIUM.parent
sys.path.insert(0, str(VIVARIUM))
sys.path.insert(0, str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient"))
from viv import bundle as _b                                     # noqa: E402
from viv import db as _db                                        # noqa: E402
from viv import queue as _q                                      # noqa: E402
from viv import spec as _spec                                    # noqa: E402

GKL = "005f005f005f005f005fff5f005fff5f"
HARNESS = "C4-CANARY-W1"
CREATED_BY = "vivarium-canary"


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def spec_ca(*, repeats: int, n_cells: int, steps: int, n_ic: int, max_seconds: int, seed_root: int, label: str) -> dict:
    return {"spec_version": 3, "world": {"seed_root": seed_root},
            "hypothesis": "canary %s: the GKL density classifier's accuracy is >= 0 (a tautology; the canary measures the LAB, not the rule)" % label,
            "prediction": None,
            "work": {"kind": "ca_density_v0",
                     "payload": {"rule_hex": GKL, "radius": 3, "n_cells": n_cells, "steps": steps, "n_ic": n_ic,
                                 "ic_density_set": [None], "success_criterion": "at_T", "transform": "none"}},
            "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0, "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE", "aggregate": "first"},
            "pew": None,
            "repeat": {"count": repeats, "order": "sequential", "seed_derivation": "sha256_index", "state": "reset",
                       "budget": {"max_seconds": max_seconds, "max_observations": repeats}}}


GATE = {"gate_id": "pc:w0_climbed", "phase": "pre_execution",
        "condition": "the W0 control best >= the measured shelf floor of THIS table",
        "measurement": {"source": "producer_supplied", "ref": "w0_best"},
        "rule": {"op": ">=", "reference": {"ref": "shelf_floor"}, "if_indeterminate": "FAIL"},
        "on_fail": "abort_attempt", "definition_ref": "canary:%s#gates[0]" % HARNESS}


def declared_for(spec: dict, label: str) -> dict:
    d = _b.declared_skeleton(spec)
    d["gates"] = [GATE]
    d["evaluator"] = {"profile_id": "ev.accuracy_at_T.v1", "reward_mode": "accuracy"}
    d["schedule"] = {"schedule_id": "canary.fixed.v1", "kind": "fixed", "parameters": {}}
    d["population"] = {"population_schema": "UNKNOWN", "manifest_hash": "UNKNOWN", "manifest_ref": "UNKNOWN",
                       "foundry_profile": "UNKNOWN"}
    d["factors"] = {"harness": HARNESS, "arm": label, "rule": "GKL"}
    assert _b.problems(d, spec=spec) == [], _b.problems(d, spec=spec)
    return d


class Canary:
    def __init__(self, receipt: Path, var_dir: Path):
        self.receipt = receipt
        self.var_dir = var_dir
        self.out = {"schema": "vivarium_canary.v1", "harness": HARNESS, "started_at": _utc(), "checks": {}, "rows": {}}
        self.conn = _db.connect()

    def save(self):
        self.receipt.parent.mkdir(parents=True, exist_ok=True)
        self.out["updated_at"] = _utc()
        self.receipt.write_text(json.dumps(self.out, indent=2, default=str), encoding="utf-8")

    def check(self, name, ok, **detail):
        self.out["checks"][name] = {"ok": bool(ok), **detail}
        print("  %s %s %s" % ("ok " if ok else "BAD", name, json.dumps(detail, default=str)[:200]), flush=True)
        self.save()
        return bool(ok)

    def q(self, sql, *args):
        with _db.dict_cur(self.conn) as cur:
            cur.execute(sql, args or None)
            rows = [dict(r) for r in cur.fetchall()]
        self.conn.rollback()
        return rows

    def enqueue(self, spec, label, measurements):
        eid = str(_q.enqueue(self.conn, created_by=CREATED_BY, source_reason="s14 canary %s (window C4-20260917-W1)" % HARNESS,
                             experiment_spec=spec, source_evidence={"gate_measurements": measurements},
                             family_id=HARNESS, arm_id=label))
        d = declared_for(spec, label)
        with self.conn.cursor() as cur:
            cur.execute("UPDATE viv.research_experiment_queue SET bundle_declared=%s WHERE experiment_id=%s AND status='queued'",
                        (json.dumps(d), eid))
        self.conn.commit()
        self.out["rows"][label] = {"experiment_id": eid, "spec_hash": _spec.spec_hash(spec), "bundle_hash_declared": _b.bundle_hash(d)}
        self.save()
        return eid

    def wait_terminal(self, eid, timeout_s):
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            r = self.q("SELECT status, error, sfe_experiment_id, result_summary FROM viv.research_experiment_queue WHERE experiment_id=%s", eid)[0]
            if r["status"] in ("completed", "failed", "cancelled"):
                return r
            time.sleep(2)
        return None

    def attempts(self, eid):
        return self.q("SELECT attempt_id, attempt_number, terminal_state, termination, parent_attempt_id, bundle_hash, bundle_hash_declared "
                      "FROM viv.execution_attempt WHERE experiment_id=%s ORDER BY attempt_number", eid)

    def steps(self, attempt_id):
        return self.q("SELECT step_kind, parts, status, result FROM viv.execution_step WHERE attempt_id=%s ORDER BY started_at, step_id", attempt_id)

    PINNED = Path(r"D:\Prometheus-worktrees\vivarium-consumer\vivarium")

    def engine_read(self, wid: str, exp_id=None) -> dict:
        """Read the world's observations (and one experiment) from the engine
        as the world's OWNER `vivarium` (the engine answers 403 to any other client,
        including vivarium-test -- worlds are owned). A READ only. Runs INSIDE the pinned
        consumer worktree, whose gitignored config holds the identities; this
        process never sees a token."""
        code = (
            "import json,os,sys; sys.path.insert(0, r'%s')\n"
            "from viv import db as _db, identity as _i\n"
            "from sfclient import EngineClient\n"
            "cfg=_db.load_config(); ca=cfg.get('sfe_cacert'); ca=ca if (not ca or os.path.isabs(ca)) else os.path.join(r'%s', ca)\n"
            "c=EngineClient(cfg['sfe_base_url'], _i.token_for('production'), cafile=ca, timeout=60)\n"
            "obs=c.list_observations(sys.argv[1]); obs=obs.get('observations', obs) if isinstance(obs, dict) else obs\n"
            "exp=c.get_experiment(sys.argv[1], sys.argv[2]) if len(sys.argv)>2 else None\n"
            "w=c.get_world(sys.argv[1])\n"
            "print(json.dumps({'n_obs': len(obs), 'experiment_found': bool(exp), 'world_found': bool(w), "
            "'labels': (w or {}).get('labels')}))\n"
        ) % (str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient"), str(REPO))
        env = dict(os.environ, VIV_SFE_BASE_URL="https://192.168.1.191:8811",
                   VIV_SFE_CACERT="SerendipityFoundry/SerendipityFoundryClient/config/m2.crt")
        args = [sys.executable, "-c", code, wid] + ([exp_id] if exp_id else [])
        r = subprocess.run(args, capture_output=True, text=True, cwd=str(self.PINNED), env=env, timeout=120)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:300])
        return json.loads(r.stdout.strip().splitlines()[-1])

    # ------------------------------------------------------------ rows
    def row_a(self):
        print("A: gate FAIL control", flush=True)
        spec = spec_ca(repeats=1, n_cells=21, steps=42, n_ic=64, max_seconds=120, seed_root=20260917, label="A")
        eid = self.enqueue(spec, "A-gate-fail", {"w0_best": 0.3, "shelf_floor": 0.45})
        r = self.wait_terminal(eid, 300)
        self.check("A.terminal", r is not None and r["status"] == "failed", status=r and r["status"], error=((r or {}).get("error") or "")[:160])
        atts = self.attempts(eid)
        self.check("A.one_attempt_prerequisite_failed", len(atts) == 1 and atts[0]["terminal_state"] == "FAILED"
                   and (atts[0]["termination"] or {}).get("termination_reason") == "PREREQUISITE_FAILED",
                   attempts=[(a["attempt_number"], a["terminal_state"], (a["termination"] or {}).get("termination_reason")) for a in atts])
        g = self.q("SELECT gate_id, result, action_taken, measured, reference FROM viv.gate_receipt WHERE attempt_id=%s", atts[0]["attempt_id"]) if atts else []
        self.check("A.gate_receipt_fail_aborted", len(g) == 1 and g[0]["result"] == "FAIL" and g[0]["action_taken"] == "aborted_attempt", receipts=g)
        st = self.steps(atts[0]["attempt_id"]) if atts else []
        self.check("A.no_world_created", not any(s["step_kind"] == "world" for s in st) and (r or {}).get("sfe_experiment_id") is None, steps=[s["step_kind"] for s in st])

    def row_b(self):
        print("B: gate PASS, 3 repeats", flush=True)
        spec = spec_ca(repeats=3, n_cells=149, steps=300, n_ic=400, max_seconds=600, seed_root=20260917, label="B")
        eid = self.enqueue(spec, "B-three-repeats", {"w0_best": 0.62, "shelf_floor": 0.45})
        self.verify_b(eid)

    def verify_b(self, eid):
        r = self.wait_terminal(eid, 600)
        self.check("B.terminal_completed", r is not None and r["status"] == "completed", status=r and r["status"], error=((r or {}).get("error") or "")[:160])
        atts = self.attempts(eid)
        env = (atts[0]["termination"] or {}) if atts else {}
        self.check("B.one_attempt_completed_uncensored", len(atts) == 1 and atts[0]["terminal_state"] == "COMPLETED"
                   and env.get("termination_reason") == "COMPLETED_ALL_REPEATS" and env.get("censored") is False
                   and env.get("observations_recorded") == 3, envelope=env)
        st = self.steps(atts[0]["attempt_id"]) if atts else []
        kinds = [(s["step_kind"], s["status"]) for s in st]
        self.check("B.steps_all_new", bool(st) and all(s["status"] == "NEW" for s in st)
                   and sum(1 for s in st if s["step_kind"] == "observe") == 3 and sum(1 for s in st if s["step_kind"] == "world") == 1, steps=kinds)
        world = next((s for s in st if s["step_kind"] == "world"), None)
        wres = (world or {}).get("result") or {}
        self.check("B.labels_recorded", "labels" in wres and "labels_applied" in wres, labels=wres.get("labels"), applied=wres.get("labels_applied"))
        g = self.q("SELECT result, action_taken FROM viv.gate_receipt WHERE attempt_id=%s", atts[0]["attempt_id"]) if atts else []
        self.check("B.gate_receipt_pass", len(g) == 1 and g[0]["result"] == "PASS" and g[0]["action_taken"] == "proceeded", receipts=g)
        declared_hash = (self.out["rows"].get("B-three-repeats") or {}).get("bundle_hash_declared")
        self.check("B.bundle_filled_over_declared", bool(atts) and (declared_hash is None or atts[0]["bundle_hash_declared"] == declared_hash)
                   and atts[0]["bundle_hash"] != atts[0]["bundle_hash_declared"], declared=declared_hash, recorded=(atts[0]["bundle_hash_declared"] if atts else None))
        ob = self.q("SELECT event_kind, state, stream FROM viv.pew_outbox WHERE source_experiment=%s ORDER BY stream, sequence", eid)
        self.check("B.outbox_rows_pending_no_pew_token", bool(ob) and all(o["state"] == "PENDING" for o in ob),
                   kinds=sorted({o["event_kind"] for o in ob}), n=len(ob))
        try:
            wid = wres.get("world_id")
            e = self.engine_read(wid, r["sfe_experiment_id"])
            self.check("B.engine_has_world_experiment_3_observations", e["n_obs"] == 3 and e["experiment_found"] and e["world_found"],
                       world_id=wid, exp_id=r["sfe_experiment_id"], **e)
        except Exception as exc:                                   # noqa: BLE001
            self.check("B.engine_has_world_experiment_3_observations", False, error=str(exc)[:200])

    def consumer_pid(self):
        h = self.q("SELECT pid, host, last_seen FROM viv.worker_heartbeat WHERE worker_id='vivarium@m2'")
        return (h[0]["pid"], h[0]["host"]) if h else (None, None)

    def row_c(self, L="C", *, die="in_loop"):
        """die="in_loop": kill while the repeats are computing under the lease
        (the common death: compute dominates) -> lease expires -> RETRYABLE ->
        attempt 2's claim is RECOMPUTED, runs recomputed, item completed once.
        die="posting": kill while observations are being posted, after the
        engine completed the item -> attempt 2's claim is REPLAYED, nothing
        completed twice. The second window is short (observations post in
        ~0.3 s each); if the kill lands after the row completed the check is
        recorded NOT_EXERCISED, never passed by default."""
        print("%s: mid-run death (%s) -> NEW ATTEMPT" % (L, die), flush=True)
        if die == "in_loop":
            spec = spec_ca(repeats=5, n_cells=149, steps=600, n_ic=4000, max_seconds=900, seed_root=20260918 + ord(L), label=L)
        else:
            spec = spec_ca(repeats=12, n_cells=21, steps=42, n_ic=64, max_seconds=900, seed_root=20260918 + ord(L), label=L)
        eid = self.enqueue(spec, "%s-resume-%s" % (L, die), {"w0_best": 0.62, "shelf_floor": 0.45})
        t0 = time.time(); killed = None; steps_at_kill = []
        while time.time() - t0 < 600:
            atts = self.attempts(eid)
            if atts:
                st = self.steps(atts[0]["attempt_id"])
                n_obs = sum(1 for s in st if s["step_kind"] == "observe")
                n_run = sum(1 for s in st if s["step_kind"] == "run")
                ready = (n_run >= 2) if die == "in_loop" else (n_obs >= 1)
                if ready:
                    pid, host = self.consumer_pid()
                    r = subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, text=True, timeout=30)
                    killed = {"pid": pid, "host": host, "rc": r.returncode, "out": (r.stdout or r.stderr)[-120:], "at": _utc(),
                              "observations_before_kill": n_obs}
                    steps_at_kill = [(s["step_kind"], s["status"]) for s in st]
                    break
            time.sleep(1 if die == "in_loop" else 0.1)
        self.check(L + ".consumer_killed_mid_run", killed is not None and killed["rc"] == 0, **(killed or {}), steps=steps_at_kill)
        if killed is None:
            return
        time.sleep(3)
        row = self.q("SELECT status FROM viv.research_experiment_queue WHERE experiment_id=%s", eid)[0]
        if row["status"] == "completed":
            self.out["checks"][L + ".NOT_EXERCISED"] = {"ok": True, "note": "the row completed before the kill landed; "
                                                        "this death shape was not exercised on production this run"}
            self.save()
            return
        self.check(L + ".row_stranded_running", row["status"] in ("running", "claimed"), status=row["status"])
        r = subprocess.run([sys.executable, "-m", "viv.cli", "release", eid, "--new-attempt", "--by", "vivarium@m2",
                            "--reason", "s14 canary: consumer killed mid-run; NEW ATTEMPT is the only recovery"],
                           capture_output=True, text=True, cwd=str(VIVARIUM), timeout=120)
        self.check(L + ".released_new_attempt", r.returncode == 0, out=(r.stdout or r.stderr)[-200:])
        atts = self.attempts(eid)
        self.check(L + ".attempt1_stranded", bool(atts) and atts[0]["terminal_state"] == "STRANDED"
                   and (atts[0]["termination"] or {}).get("termination_reason") == "STRANDED",
                   a1=(atts[0]["terminal_state"], (atts[0]["termination"] or {}).get("termination_reason")) if atts else None)
        # the production relaunch path: the dead-man task (run it now rather than wait for its 5-minute tick)
        rr = subprocess.run(["schtasks", "/Run", "/TN", "VivariumDeadmanM2"], capture_output=True, text=True, timeout=60)
        self.out["checks"][L + ".deadman_run_requested"] = {"ok": rr.returncode == 0, "out": (rr.stdout or rr.stderr)[-120:]}
        t1 = time.time(); new_pid = None
        while time.time() - t1 < 420:
            pid, _ = self.consumer_pid()
            if pid and pid != killed["pid"]:
                new_pid = pid; break
            time.sleep(3)
        self.check(L + ".consumer_relaunched_by_deadman", new_pid is not None, new_pid=new_pid, old_pid=killed["pid"], waited_s=round(time.time() - t1))
        rt = self.wait_terminal(eid, 900)
        self.check(L + ".terminal_completed", rt is not None and rt["status"] == "completed", status=rt and rt["status"], error=((rt or {}).get("error") or "")[:160])
        atts = self.attempts(eid)
        a2 = atts[1] if len(atts) > 1 else None
        env = (a2 or {}).get("termination") or {}
        self.check(L + ".attempt2_completed_all_observations", a2 is not None and a2["terminal_state"] == "COMPLETED"
                   and env.get("observations_recorded") == (5 if die == "in_loop" else 12) and env.get("censored") is False
                   and a2["parent_attempt_id"] == atts[0]["attempt_id"], envelope=env)
        st2 = self.steps(a2["attempt_id"]) if a2 else []
        by = {}
        for s in st2:
            by.setdefault(s["step_kind"], []).append(s["status"])
        world_ids = {(s["result"] or {}).get("world_id") for a in atts for s in self.steps(a["attempt_id"]) if s["step_kind"] == "world"}
        n_rep = 5 if die == "in_loop" else 12
        claim_expect = "RECOMPUTED" if die == "in_loop" else "REPLAYED"
        self.check(L + ".attempt2_replayed_world_experiment_claim_%s_one_world" % claim_expect.lower(),
                   by.get("world") == ["REPLAYED"] and by.get("experiment") == ["REPLAYED"]
                   and by.get("claim") == [claim_expect]
                   # the engine may hold MORE observations than the recorder saw at the kill (a POST
                   # that landed before its step result did -- recovered by content): replayed >= recorded
                   and by.get("observe", []).count("REPLAYED") >= killed["observations_before_kill"]
                   and len(by.get("observe", [])) == n_rep and len(world_ids) == 1,
                   statuses=by, world_ids=sorted(x for x in world_ids if x),
                   recorded_at_kill=killed["observations_before_kill"])
        try:
            wid = next(iter(x for x in world_ids if x))
            e = self.engine_read(wid)
            self.check(L + ".engine_exactly_n_observations_one_world", e["n_obs"] == (5 if die == "in_loop" else 12), world_id=wid, **e)
        except Exception as exc:                                   # noqa: BLE001
            self.check(L + ".engine_exactly_n_observations_one_world", False, error=str(exc)[:200])
        ob = self.q("SELECT event_kind, state FROM viv.pew_outbox WHERE source_experiment=%s ORDER BY stream, sequence", eid)
        self.check(L + ".outbox_has_both_attempts", sum(1 for o in ob if o["event_kind"] == "ATTEMPT_OPENED") == 2
                   and sum(1 for o in ob if o["event_kind"] == "ATTEMPT_TERMINATED") == 2, kinds=[o["event_kind"] for o in ob])

    def close(self):
        left = self.q("SELECT count(*) AS n FROM viv.research_experiment_queue WHERE created_by=%s AND status NOT IN ('completed','failed','cancelled')", CREATED_BY)[0]["n"]
        self.check("close.no_canary_work_left_in_queue", left == 0, open_rows=left)
        self.out["ok"] = all(c["ok"] for c in self.out["checks"].values())
        self.out["finished_at"] = _utc()
        self.save()
        self.conn.close()
        return self.out["ok"]


def main() -> int:
    receipt = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\Prometheus-data\vivarium\window\canary-C4-20260917-W1.json")
    c = Canary(receipt, Path(r"D:\Prometheus-data\vivarium\var"))
    try:
        c.row_a(); c.row_b(); c.row_c("C", die="in_loop"); c.row_c("D", die="posting")
    except Exception as exc:                                       # noqa: BLE001
        import traceback; c.check("aborted", False, error="%s: %s" % (type(exc).__name__, str(exc)[:300]), trace=traceback.format_exc()[-800:])
    ok = c.close()
    print("canary", "OK" if ok else "FAILED", "->", receipt)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
