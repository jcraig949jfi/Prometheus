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
LISTS = ("required_controls", "required_oracles")

# The one ceiling table. None = no ceiling at that stage (operator-authorized stages only).
# PILOT per operator 19 s1 / SWARM_R5 s3 F-R5-1; SMOKE may not exceed PILOT.
CEILINGS = {
    "SMOKE":       {"cpu_wall_s": 900, "gpu_wall_s": 600, "cpu_budget_s": 1200},
    "PILOT":       {"cpu_wall_s": 900, "gpu_wall_s": 600, "cpu_budget_s": 1200},
    "PRODUCTION":  {"cpu_wall_s": None, "gpu_wall_s": None, "cpu_budget_s": None},
    "REPLICATION": {"cpu_wall_s": None, "gpu_wall_s": None, "cpu_budget_s": None},
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
    if ceil["cpu_budget_s"] is not None and env["cpu_budget_s"] > ceil["cpu_budget_s"]:
        reasons.append("CPU_BUDGET_OVER_CEILING")
    wall = env["gpu_budget_s"] if kind == "gpu" else env["wall_budget_s"]
    event = STAGE_BUDGET_REFUSAL
    if clock:
        if now + wall > float(clock["end_ts"]):
            reasons.append("PROJECTED_PAST_ROUND_END")
        if now >= float(clock["no_new_work_ts"]) and (not continuation or now + wall > float(clock["drain_ts"])):
            reasons.append("NO_NEW_WORK")
            if len(reasons) == 1:
                event = NO_NEW_WORK_REFUSAL
    return {"ok": not reasons, "event": None if not reasons else event, "reasons": reasons, "stage": stage,
            "ceiling": ceil}


def refuse(r, lane: str, job: dict, verdict: dict, env) -> dict:
    """Publish a refusal: one pm:events record and one PRODUCTION_CANDIDATE stub. -> the event record."""
    env = env if isinstance(env, dict) else {}
    ev = {"event": verdict["event"], "lane": lane, "job_id": job.get("job_id"),
          "job_key": job.get("job_key") or job.get("job_id"), "fn": job.get("fn"), "exp_id": job.get("exp_id"),
          "reasons": verdict["reasons"], "stage": verdict["stage"], "ceiling": verdict["ceiling"],
          "envelope": env, "ts": round(time.time(), 3)}
    r.xadd(EVENTS, {"event": ev["event"], "json": json.dumps(ev, sort_keys=True)})
    stub = {"kind": "PRODUCTION_CANDIDATE", "status": "STUB", "source_event": ev["event"], "lane": lane,
            "job_key": ev["job_key"], "fn": ev["fn"], "exp_id": ev["exp_id"], "reasons": ev["reasons"],
            "question": env.get("predicate_id"), "experiment_class": env.get("experiment_class"),
            "cohort": env.get("cohort"),
            "requested_cost": {k: env.get(k) for k in ("wall_budget_s", "cpu_budget_s", "gpu_budget_s")},
            "measured_cost": None, "dependencies": [], "ts": ev["ts"]}
    r.xadd(CANDIDATES, {"json": json.dumps(stub, sort_keys=True)})
    return ev


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
