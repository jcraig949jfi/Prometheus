"""F-R5-1 (round 5): the job envelope and stage admission. Code owns the ceiling, not prose.

Every job submitted to an F7 worker carries an envelope (operator 19 s1):

  campaign_stage        SMOKE | PILOT | PRODUCTION | REPLICATION
  wall_budget_s         wall the job may use (the worker kills it past this)
  cpu_budget_s          CPU seconds the job may use (the worker's ttl_cpu_s is capped at this)
  gpu_budget_s          leased GPU wall (0 for CPU jobs)
  expected_output_rows  int
  checkpointable        bool
  required_controls     list
  required_oracles      list
  cohort                the budget identity (F13 shares); physical CPU is the broker's
  predicate_id          the posted predicate the run answers
  experiment_class      free label (e.g. CLAUSE_A, DISTANT_QD, ANTI_PRIOR, B2_ADMISSION, PROBE)

admit(envelope, kind, clock, now) checks the envelope against ONE table, CEILINGS, for the active
stage (the round clock's stage; the envelope's own stage when no round runs). A refusal is a normal
result -- {"ok": False, "reasons": [...]} -- never an exception and never a scientific FAIL. refuse()
publishes it: a STAGE_BUDGET_REFUSAL (or NO_NEW_WORK_REFUSAL) event on pm:events plus a
PRODUCTION_CANDIDATE stub on pm:production_candidates carrying the requested cost. The stub is not
authorization to run anything.
"""
from __future__ import annotations

import json
import time

STAGES = ("SMOKE", "PILOT", "PRODUCTION", "REPLICATION")
FIELDS = ("campaign_stage", "wall_budget_s", "cpu_budget_s", "gpu_budget_s", "expected_output_rows",
          "checkpointable", "required_controls", "required_oracles", "cohort", "predicate_id",
          "experiment_class")
NUMERIC = ("wall_budget_s", "cpu_budget_s", "gpu_budget_s", "expected_output_rows")
EVIDENCE_CLASSES = ("VERDICT", "OBSERVATION")           # optional envelope field (R7, EVIDENCE_N_v1 at admission)
LISTS = ("required_controls", "required_oracles")

# The one ceiling table. None = no ceiling at that stage (operator-authorized stages only).
# PILOT per operator 19 s1 / SWARM_R5 s3 F-R5-1; SMOKE may not exceed PILOT.
#   cpu_wall_s                   wall of one segment of a CHECKPOINTABLE cpu job (it continues in its next segment)
#   cpu_wall_noncheckpointable_s wall of a NON-checkpointable cpu job (R7 D15: one such job held every lane 8.8 min)
#   gpu_wall_s                   leased GPU wall per lease segment (a longer GPU job checkpoints between leases)
#   cpu_budget_s                 CPU seconds per job, cumulative over segments
CEILINGS = {
    "SMOKE":       {"cpu_wall_s": 900, "cpu_wall_noncheckpointable_s": 900, "gpu_wall_s": 600, "cpu_budget_s": 1200},
    "PILOT":       {"cpu_wall_s": 900, "cpu_wall_noncheckpointable_s": 900, "gpu_wall_s": 600,
                    "cpu_budget_s": 2400},   # operator 20 (09-15 07:23): 40 CPU-min
    # PRODUCTION: operator 22; round 7 values per SWARM_R7 s2 (cpu_budget_s 36000 = 10 CPU-h; non-checkpointable 900)
    "PRODUCTION":  {"cpu_wall_s": 2400, "cpu_wall_noncheckpointable_s": 900, "gpu_wall_s": 600, "cpu_budget_s": 36000},
    "REPLICATION": {"cpu_wall_s": 2400, "cpu_wall_noncheckpointable_s": 900, "gpu_wall_s": 600, "cpu_budget_s": 36000},
}
# Which job stages an active stage admits (A 1789467348712-0): a PILOT round admits SMOKE and REPLICATION
# at PILOT's ceilings (never looser); PRODUCTION needs an operator ruling. A stage not in this table or in
# CEILINGS -> STAGE_NOT_ALLOWED (no permissive default).
ALLOWED = {"SMOKE": {"SMOKE"}, "PILOT": {"SMOKE", "PILOT", "REPLICATION"},
           "PRODUCTION": set(STAGES), "REPLICATION": set(STAGES)}

EVENTS = "pm:events"
CANDIDATES = "pm:production_candidates"
STAGE_BUDGET_REFUSAL = "STAGE_BUDGET_REFUSAL"
NO_NEW_WORK_REFUSAL = "NO_NEW_WORK_REFUSAL"


def validate(env) -> list[str]:
    """-> reason codes for a malformed envelope (empty = well formed)."""
    if not isinstance(env, dict):
        return ["ENVELOPE_MISSING"]
    out = [f"ENVELOPE_MISSING_FIELD:{k}" for k in FIELDS if k not in env]
    if "campaign_stage" in env and (env["campaign_stage"] not in CEILINGS or env["campaign_stage"] not in STAGES):
        out.append("STAGE_NOT_ALLOWED")
    for k in NUMERIC:
        v = env.get(k)
        if k in env and (isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0):
            out.append(f"ENVELOPE_BAD_VALUE:{k}")
    if "checkpointable" in env and not isinstance(env["checkpointable"], bool):
        out.append("ENVELOPE_BAD_VALUE:checkpointable")
    for k in LISTS:
        if k in env and not isinstance(env[k], list):
            out.append(f"ENVELOPE_BAD_VALUE:{k}")
    for k in ("cohort", "predicate_id", "experiment_class"):
        if k in env and not (isinstance(env[k], str) and env[k].strip()):
            out.append(f"ENVELOPE_BAD_VALUE:{k}")
    # R7 (A 1789504263405-0): evidence_class is optional; an unknown value is a malformed envelope, not a sample
    # defect. Whether the sample satisfies EVIDENCE_N_v1 is H's evidence_n module, called from admit().
    if "evidence_class" in env and env["evidence_class"] not in EVIDENCE_CLASSES:
        out.append("ENVELOPE_BAD_VALUE:evidence_class")
    return out


def admit(env, kind: str = "cpu", clock: dict | None = None, now: float | None = None,
          continuation: bool = False) -> dict:
    """-> {"ok", "event", "reasons", "stage", "ceiling"}. kind: "cpu" or "gpu".
    clock: the round clock record (ops.round_clock) or None. continuation: a later segment of a job
    already admitted (it is past NO_NEW_WORK only if it cannot finish by the drain)."""
    now = time.time() if now is None else now
    reasons = validate(env)
    if reasons:
        return {"ok": False, "event": STAGE_BUDGET_REFUSAL, "reasons": reasons, "stage": None, "ceiling": None}
    stage = (clock or {}).get("stage") or env["campaign_stage"]
    if stage not in CEILINGS or stage not in ALLOWED:
        return {"ok": False, "event": STAGE_BUDGET_REFUSAL, "reasons": ["STAGE_NOT_ALLOWED"], "stage": stage,
                "ceiling": None}
    ceil = CEILINGS[stage]
    if env["campaign_stage"] not in ALLOWED[stage]:
        reasons.append("STAGE_NOT_ALLOWED")
    if kind == "gpu":
        if ceil["gpu_wall_s"] is not None and env["gpu_budget_s"] > ceil["gpu_wall_s"]:
            reasons.append("GPU_WALL_OVER_CEILING")
    elif ceil["cpu_wall_s"] is not None and env["wall_budget_s"] > ceil["cpu_wall_s"]:
        reasons.append("CPU_WALL_OVER_CEILING")
    elif (not env["checkpointable"] and ceil["cpu_wall_noncheckpointable_s"] is not None
          and env["wall_budget_s"] > ceil["cpu_wall_noncheckpointable_s"]):
        reasons.append("NONCHECKPOINTABLE_WALL_OVER_CEILING")      # F-R7-2 (D15)
    if ceil["cpu_budget_s"] is not None and env["cpu_budget_s"] > ceil["cpu_budget_s"]:
        reasons.append("CPU_BUDGET_OVER_CEILING")
    wall = env["gpu_budget_s"] if kind == "gpu" else env["wall_budget_s"]
    event = STAGE_BUDGET_REFUSAL
    if clock:
        # horizon = drain_ts (T+110), operator 19 s14, A 1789468596599-0; end_ts stays the hard close.
        # Past no_new_work_ts the NO_NEW_WORK rule alone decides (it already applies the drain fit).
        past_nnw = now >= float(clock["no_new_work_ts"])
        if not past_nnw and now + wall > float(clock["drain_ts"]):
            reasons.append("PROJECTED_PAST_ROUND_END")
        if past_nnw and (not continuation or now + wall > float(clock["drain_ts"])):
            reasons.append("NO_NEW_WORK")
            if len(reasons) == 1:
                event = NO_NEW_WORK_REFUSAL
    return {"ok": not reasons, "event": None if not reasons else event, "reasons": reasons, "stage": stage,
            "ceiling": ceil, "stub": bool(reasons) and event == STAGE_BUDGET_REFUSAL}


def refuse(r, lane: str, job: dict, verdict: dict, env, stub: bool = True) -> dict:
    """Publish a refusal: one pm:events record and (stub=True) one PRODUCTION_CANDIDATE stub.
    -> the event record, with stub_id (the stub's stream id, for file_candidate) or None."""
    env = env if isinstance(env, dict) else {}
    ev = {"event": verdict["event"], "lane": lane, "job_id": job.get("job_id"),
          "job_key": job.get("job_key") or job.get("job_id"), "fn": job.get("fn"), "exp_id": job.get("exp_id"),
          "reasons": verdict["reasons"], "stage": verdict["stage"], "ceiling": verdict["ceiling"],
          "envelope": env, "ts": round(time.time(), 3),
          **{k: verdict[k] for k in ("loaded", "want", "error") if k in verdict}}
    r.xadd(EVENTS, {"event": ev["event"], "json": json.dumps(ev, sort_keys=True)})
    if not stub:
        return dict(ev, stub_id=None)
    stub = {"kind": "PRODUCTION_CANDIDATE", "status": "STUB", "source_event": ev["event"], "lane": lane,
            "job_key": ev["job_key"], "fn": ev["fn"], "exp_id": ev["exp_id"], "reasons": ev["reasons"],
            "question": env.get("predicate_id"), "experiment_class": env.get("experiment_class"),
            "cohort": env.get("cohort"),
            "requested_cost": {k: env.get(k) for k in ("wall_budget_s", "cpu_budget_s", "gpu_budget_s")},
            "measured_cost": None, "dependencies": [], "ts": ev["ts"]}
    stub_id = r.xadd(CANDIDATES, {"json": json.dumps(stub, sort_keys=True)})
    return dict(ev, stub_id=stub_id)


FILED = "pm:production_candidates:filed"     # F-R6-3: stub_id -> filing JSON (one filing per stub)


def file_candidate(r, stub_id: str, measured_cost: dict, basis: str, lane: str | None = None) -> dict:
    """F-R6-3 (D6): file a measured cost against a PRODUCTION_CANDIDATE stub. -> {ok, reason?, filing?}.
    measured_cost: non-empty {name: number >= 0} (e.g. wall_s, cpu_s, gpu_s, runs); basis: where it was
    measured (rows path / sha / receipt id). Refused, not raised: NO_STUB, BAD_COST, NO_BASIS, ALREADY_FILED."""
    import os
    if not r.xrange(CANDIDATES, stub_id, stub_id):
        return {"ok": False, "reason": "NO_STUB"}
    if not (isinstance(measured_cost, dict) and measured_cost and all(
            isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 for v in measured_cost.values())):
        return {"ok": False, "reason": "BAD_COST"}
    if not (isinstance(basis, str) and basis.strip()):
        return {"ok": False, "reason": "NO_BASIS"}
    filing = {"stub_id": stub_id, "measured_cost": measured_cost, "basis": basis.strip(),
              "lane": lane or os.environ.get("PM_LANE"), "tag": os.environ.get("PM_TAG"), "ts": round(time.time(), 3)}
    if not r.hsetnx(FILED, stub_id, json.dumps(filing, sort_keys=True)):
        return {"ok": False, "reason": "ALREADY_FILED", "filing": json.loads(r.hget(FILED, stub_id))}
    r.xadd(EVENTS, {"event": "CANDIDATE_FILED", "json": json.dumps(dict(filing, event="CANDIDATE_FILED"),
                                                                   sort_keys=True)})
    return {"ok": True, "filing": filing}


def open_candidates(r) -> list[dict]:
    """Stubs with no measured-cost filing, oldest first, each with its stub_id (the close tally reads this)."""
    filed = set(r.hkeys(FILED))
    return [dict(json.loads(f["json"]), stub_id=mid) for mid, f in r.xrange(CANDIDATES) if mid not in filed]


def filed_candidates(r) -> list[dict]:
    filings = {k: json.loads(v) for k, v in r.hgetall(FILED).items()}
    return [dict(json.loads(f["json"]), stub_id=mid, filing=filings[mid]) for mid, f in r.xrange(CANDIDATES)
            if mid in filings]


def events(r, name: str | None = None) -> list[dict]:
    return [json.loads(f["json"]) for _, f in r.xrange(EVENTS) if name is None or f.get("event") == name]


def candidates(r) -> list[dict]:
    return [json.loads(f["json"]) for _, f in r.xrange(CANDIDATES)]


def example(**kw) -> dict:
    """A well-formed PILOT CPU envelope (tests, self-checks); override any field."""
    env = {"campaign_stage": "PILOT", "wall_budget_s": 60, "cpu_budget_s": 120, "gpu_budget_s": 0,
           "expected_output_rows": 1, "checkpointable": False, "required_controls": [], "required_oracles": [],
           "cohort": "F", "predicate_id": "selftest", "experiment_class": "SELFTEST"}
    env.update(kw)
    return env
