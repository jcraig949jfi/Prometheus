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
import re
import time

STAGES = ("SMOKE", "PILOT", "PRODUCTION", "REPLICATION")
FIELDS = ("campaign_stage", "wall_budget_s", "cpu_budget_s", "gpu_budget_s", "expected_output_rows",
          "checkpointable", "required_controls", "required_oracles", "cohort", "predicate_id",
          "experiment_class")
NUMERIC = ("wall_budget_s", "cpu_budget_s", "gpu_budget_s", "expected_output_rows")
EVIDENCE_CLASSES = ("VERDICT", "OBSERVATION")           # optional envelope field (R7, EVIDENCE_N_v1 at admission)
LISTS = ("required_controls", "required_oracles")
STREAM_ID_RE = re.compile(r"\d+-\d+")

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
    # R8 G5 interface (F<->P): the bus id of the PREDICATE claim (predicate_ref.post_predicate -> bus_id), stamped
    # on every emitted row by prepare_row(). Optional on the envelope; malformed when present is refused.
    if "predicate_event_id" in env and not (isinstance(env["predicate_event_id"], str)
                                            and STREAM_ID_RE.fullmatch(env["predicate_event_id"])):
        out.append("ENVELOPE_BAD_VALUE:predicate_event_id")
    return out


# ------------------------------------------------------------------ R8 G1 (D29): row vocabulary, LOUD

# The FROZEN row vocabulary. Round 7 (D29): D's rows declared a status outside rows.STATUSES, RowWriter refused
# each one inside Worker._drain, the refusal became an `aborted` wrapper row, and the JOB still reported ok. A's
# ruling: fail loudly, refuse at emit, NO alias -- "observation" is an evidence_class, never a row status.
ROW_STATUSES = ("record", "dev", "aborted", "timeout", "cheat", "control")     # == fabric.rows.STATUSES (linted)
ROW_EVIDENCE_CLASSES = EVIDENCE_CLASSES                                        # == score.evidence_n (linted)
ROW_VOCABULARY_REFUSED = "ROW_VOCABULARY_REFUSED"
ROW_PREDICATE_MISMATCH = "ROW_PREDICATE_MISMATCH"


class RowRefused(ValueError):
    """A row outside the frozen vocabulary. Raised at EMIT, so the job ends `error` -- never a silent per-row drop."""

    def __init__(self, reasons: list[str]):
        super().__init__("; ".join(reasons))
        self.reasons = list(reasons)


def vocabulary_reasons(row, index: int) -> list[str]:
    """-> refusals for ONE row, each naming the row index and the offending value (empty = in vocabulary).
    status is required and must be in ROW_STATUSES; evidence_class is optional and, if present, in
    ROW_EVIDENCE_CLASSES. Exact match only: no case folding, no alias."""
    if not isinstance(row, dict):
        return [f"{ROW_VOCABULARY_REFUSED}:row {index}:row is {type(row).__name__}, not a dict"]
    out = []
    st = row.get("status")
    if st not in ROW_STATUSES or not isinstance(st, str):
        out.append(f"{ROW_VOCABULARY_REFUSED}:row {index}:status {st!r} not in {ROW_STATUSES}")
    if "evidence_class" in row and (row["evidence_class"] not in ROW_EVIDENCE_CLASSES
                                    or not isinstance(row["evidence_class"], str)):
        out.append(f"{ROW_VOCABULARY_REFUSED}:row {index}:evidence_class {row['evidence_class']!r} "
                   f"not in {ROW_EVIDENCE_CLASSES}")
    return out


def check_rows(rows, start: int = 0) -> list[str]:
    """Batch form (submit-time or post-hoc): every refusal over `rows`, indices from `start`."""
    return [x for i, row in enumerate(rows, start) for x in vocabulary_reasons(row, i)]


def prepare_row(row, index: int, env=None) -> dict:
    """THE emit-path check (called by the worker's Ctx.emit before the row reaches the stream). -> a NEW row dict
    stamped with `predicate_id` and `predicate_event_id` from the envelope (keys always present; None when the
    envelope has none). Raises RowRefused on any vocabulary refusal, or ROW_PREDICATE_MISMATCH when the row itself
    names a different predicate than its envelope."""
    reasons = vocabulary_reasons(row, index)
    if reasons:
        raise RowRefused(reasons)
    env = env if isinstance(env, dict) else {}
    out = dict(row)
    for k in ("predicate_id", "predicate_event_id"):
        want = env.get(k)
        if k in out and want is not None and out[k] != want:
            raise RowRefused([f"{ROW_PREDICATE_MISMATCH}:row {index}:{k} {out[k]!r} != envelope {want!r}"])
        if out.get(k) is None:
            out[k] = want
    return out


def lint_vocabulary(paths=None, rows_paths=()) -> dict:
    """The gate's vocabulary lint. -> {ok, checks, violations}.

    1. The frozen tables agree: ROW_STATUSES == fabric.rows.STATUSES, ROW_EVIDENCE_CLASSES == score.evidence_n.
    2. Source (AST): every dict literal in `paths` (default: primordial/**/*.py minus tests) that carries a
       constant `evidence_class` must use the frozen token; a dict literal with an `evidence_class` key (i.e. a
       row) and a constant `status` must use a frozen row status. Dynamic values are the emit check's job.
    3. Rows (JSONL `rows_paths`): every row's status/evidence_class, through vocabulary_reasons.
    """
    import ast
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    checks, bad = 0, []
    from primordial.fabric import rows as RW
    from primordial.score import evidence_n as EN
    checks += 1
    if tuple(RW.STATUSES) != ROW_STATUSES:
        bad.append(f"TABLE:rows.STATUSES {tuple(RW.STATUSES)} != envelope.ROW_STATUSES {ROW_STATUSES}")
    checks += 1
    if tuple(EN.EVIDENCE_CLASSES) != ROW_EVIDENCE_CLASSES:
        bad.append(f"TABLE:evidence_n.EVIDENCE_CLASSES {tuple(EN.EVIDENCE_CLASSES)} != {ROW_EVIDENCE_CLASSES}")
    if paths is None:
        paths = [p for p in sorted((root / "primordial").rglob("*.py")) if "tests" not in p.parts]
    for p in map(pathlib.Path, paths):
        checks += 1
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"), filename=str(p))
        except SyntaxError as e:
            bad.append(f"SOURCE:{p}:unparseable: {e}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            kv = {k.value: v for k, v in zip(node.keys, node.values)
                  if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if "evidence_class" not in kv:
                continue
            ec, st = kv["evidence_class"], kv.get("status")
            if isinstance(ec, ast.Constant) and ec.value not in ROW_EVIDENCE_CLASSES:
                bad.append(f"SOURCE:{p}:{node.lineno}:evidence_class {ec.value!r} not in {ROW_EVIDENCE_CLASSES}")
            if isinstance(st, ast.Constant) and st.value not in ROW_STATUSES:
                bad.append(f"SOURCE:{p}:{node.lineno}:status {st.value!r} not in {ROW_STATUSES}")
    for p in map(pathlib.Path, rows_paths):
        checks += 1
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines()):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                bad.append(f"ROWS:{p}:line {i}: unparseable")
                continue
            bad.extend(f"ROWS:{p}:{x}" for x in vocabulary_reasons(row, i))
    return {"ok": not bad, "checks": checks, "violations": bad}


# ------------------------------------------------------------------ R8 GE: gate enforcement at admission

GATE_NOT_LANDED = "GATE_NOT_LANDED"
GATE_STATE_UNAVAILABLE = "GATE_STATE_UNAVAILABLE"
GATE_REFUSAL = "GATE_REFUSAL"
GATES_KEY = "pm:round:{}:gates"                # published by A's gate run: gate_id -> landed | not_landed
GATE_MAP_FILE = "roles/Nestor/sidequests/graphworld/GATE_MAP_{}.json"   # the committed record (A's gate_r8 --emit)
# Gates exist from round 8. Every campaign round id rN with N >= 8 is gate-checked and FAILS CLOSED without state
# (an undefined rN cannot start a clock at all -- G8/R18). Non-campaign clock ids (tests, dev: "t-r7-1") are not.
CAMPAIGN_ROUND_RE = re.compile(r"[rR](\d+)")
GATES_FROM_ROUND = 8


def _blocks_g1(env, kind):
    return env["expected_output_rows"] > 0


def _blocks_g2(env, kind):
    ec = env["experiment_class"]
    return ec == "ANTI_PRIOR" or ec.upper().startswith("BETA")


def _blocks_g3(env, kind):
    return kind == "cpu"                       # every brokered CPU job under a live round is shared-CPU multi-lane


def _blocks_c1(env, kind):
    return kind == "gpu"


def _blocks_c2(env, kind):
    # Clause B's verdict is transfer_b.signflip_p at n = 32 runs, which is the MC branch; OBSERVATIONs carry no verdict.
    return env["experiment_class"] == "CLAUSE_B" and env.get("evidence_class") != "OBSERVATION"


# SWARM_R8 s3 topology: which gate blocks which work. WHICH gates landed is never here -- it is read from A's
# published state. G4, G5, G6, G7 (and G8, GE, C3) block nothing at admission.
GATE_BLOCKS = {"G1": _blocks_g1, "G2": _blocks_g2, "G3": _blocks_g3, "C1": _blocks_c1, "C2": _blocks_c2}


def read_gate_state(round_id, r=None) -> dict | None:
    """-> {gate_id: "landed" | "not_landed"} for the round, or None when unavailable/unreadable (callers FAIL CLOSED).
    With r: the redis hash pm:round:<round_id>:gates. Without: the committed GATE_MAP_<ROUND>.json."""
    if not (isinstance(round_id, str) and round_id.strip()):
        return None
    try:
        if r is not None:
            state = dict(r.hgetall(GATES_KEY.format(round_id)) or {})
        else:
            import pathlib
            p = pathlib.Path(__file__).resolve().parents[2] / GATE_MAP_FILE.format(round_id.upper())
            rec = json.loads(p.read_text(encoding="utf-8"))
            if rec.get("round_id") != round_id:
                return None
            state = {g: ("landed" if v.get("landed") is True else "not_landed") for g, v in rec["gates"].items()}
    except Exception:                                   # noqa: BLE001 -- unreadable is unavailable, never permissive
        return None
    if not state or any(v not in ("landed", "not_landed") for v in state.values()):
        return None
    return state


def gate_reasons(env, kind: str, clock: dict | None, gates: dict | None = None, r=None) -> list[str]:
    """R8 GE. No clock (the BUILD phase) -> []. Clock -> GATE_STATE_UNAVAILABLE if the state cannot be read, else one
    GATE_NOT_LANDED:<id> per blocking gate that is not `landed` (a blocking gate absent from the state is not landed)."""
    if not clock:
        return []
    rid = clock.get("round_id")
    m = CAMPAIGN_ROUND_RE.fullmatch(rid.strip()) if isinstance(rid, str) else None
    if rid is None or not isinstance(rid, str):
        return [GATE_STATE_UNAVAILABLE]                 # a live clock with no identity cannot be gate-checked
    if m is None or int(m.group(1)) < GATES_FROM_ROUND:
        return []                                       # pre-gate campaign rounds (r5-r7) and test/dev clock ids
    state = gates if gates is not None else read_gate_state(rid, r)
    if not state or any(v not in ("landed", "not_landed") for v in state.values()):
        return [GATE_STATE_UNAVAILABLE]
    return [f"{GATE_NOT_LANDED}:{g}" for g, blocks in GATE_BLOCKS.items()
            if blocks(env, kind) and state.get(g) != "landed"]


def admit(env, kind: str = "cpu", clock: dict | None = None, now: float | None = None,
          continuation: bool = False, gates: dict | None = None, r=None) -> dict:
    """-> {"ok", "event", "reasons", "stage", "ceiling"}. kind: "cpu" or "gpu".
    clock: the round clock record (ops.round_clock) or None. continuation: a later segment of a job
    already admitted (it is past NO_NEW_WORK only if it cannot finish by the drain).
    gates / r (R8 GE): the round's gate state, else read from redis r, else from the committed GATE_MAP file."""
    now = time.time() if now is None else now
    reasons = validate(env)
    if reasons:
        return {"ok": False, "event": STAGE_BUDGET_REFUSAL, "reasons": reasons, "stage": None, "ceiling": None}
    # R8 GE (BOOT_R8 s3, R16): a gate that did not land refuses its dependent work HERE, at zero CPU, before any
    # other rule. Recorded as GATE_REFUSAL (not a scientific FAIL, P1) with no candidate stub.
    gated = gate_reasons(env, kind, clock, gates, r)
    if gated:
        return {"ok": False, "event": GATE_REFUSAL, "reasons": gated, "stage": (clock or {}).get("stage"),
                "ceiling": None, "stub": False}
    # H-R7-1 (SWARM_R7 O1, operator 23): EVIDENCE_N_v1 at admission, before any ceiling, clock or simulation.
    # The rule lives in ONE module (primordial.score.evidence_n); fail closed if it cannot be evaluated.
    try:
        from primordial.score.evidence_n import admission_reasons
        evidence = list(admission_reasons(env))
    except Exception:                                   # noqa: BLE001 -- no permissive default
        evidence = ["EVIDENCE_RULE_UNAVAILABLE"]
    reasons.extend(evidence)
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
    if evidence:                                        # H-R7-1: the sample refusal names the event, never a stub (D16)
        event = "SAMPLE_RULE_MISMATCH"
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
    stub = _stub(ev["event"], lane, question=env.get("predicate_id"), experiment_class=env.get("experiment_class"),
                 requested_cost={k: env.get(k) for k in ("wall_budget_s", "cpu_budget_s", "gpu_budget_s")},
                 dependencies=[], ts=ev["ts"], job_key=ev["job_key"], fn=ev["fn"], exp_id=ev["exp_id"],
                 reasons=ev["reasons"], cohort=env.get("cohort"))
    stub_id = r.xadd(CANDIDATES, {"json": json.dumps(stub, sort_keys=True)})
    return dict(ev, stub_id=stub_id)


def _stub(source_event, lane, question, experiment_class, requested_cost, dependencies, ts, **extra) -> dict:
    """The PRODUCTION_CANDIDATE stub record -- one shape for refuse() and open_candidate()."""
    return {"kind": "PRODUCTION_CANDIDATE", "status": "STUB", "source_event": source_event, "lane": lane,
            "job_key": None, "fn": None, "exp_id": None, "reasons": [], "cohort": None, **extra,
            "question": question, "experiment_class": experiment_class, "requested_cost": requested_cost,
            "measured_cost": None, "dependencies": dependencies, "ts": ts}


CANDIDATE_OPENED = "CANDIDATE_OPENED"


def open_candidate(r, lane: str, question: str, basis: str, requested_cost: dict | None = None,
                   dependencies: list | None = None, experiment_class: str | None = None,
                   source_event: str = CANDIDATE_OPENED) -> dict:
    """R8 G6 (D27): open a PRODUCTION_CANDIDATE with NO refusal event (WHY_NOT_RUN, residue, a defect's PC).
    -> {ok: True, stub_id} or {ok: False, reason} (NO_LANE, NO_QUESTION, NO_BASIS, BAD_COST, BAD_DEPENDENCIES,
    BAD_SOURCE_EVENT). Writes the stub and one CANDIDATE_OPENED lineage event, never a *_REFUSAL event.
    file_candidate() files a measured cost onto the returned stub_id exactly as for a refusal stub."""
    import os
    for name, v, reason in (("lane", lane, "NO_LANE"), ("question", question, "NO_QUESTION"),
                            ("basis", basis, "NO_BASIS"), ("source_event", source_event, "BAD_SOURCE_EVENT")):
        if not (isinstance(v, str) and v.strip()):
            return {"ok": False, "reason": reason}
    if source_event.endswith("_REFUSAL"):
        return {"ok": False, "reason": "BAD_SOURCE_EVENT"}   # a refusal stub comes from refuse(), never from here
    if requested_cost is not None and not (isinstance(requested_cost, dict) and all(
            v is None or (isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0)
            for v in requested_cost.values())):
        return {"ok": False, "reason": "BAD_COST"}
    if dependencies is not None and not (isinstance(dependencies, list)
                                         and all(isinstance(d, str) for d in dependencies)):
        return {"ok": False, "reason": "BAD_DEPENDENCIES"}
    if experiment_class is not None and not (isinstance(experiment_class, str) and experiment_class.strip()):
        return {"ok": False, "reason": "BAD_EXPERIMENT_CLASS"}
    ts = round(time.time(), 3)
    stub = _stub(source_event.strip(), lane, question=question.strip(), experiment_class=experiment_class,
                 requested_cost=requested_cost, dependencies=list(dependencies or []), ts=ts, basis=basis.strip(),
                 tag=os.environ.get("PM_TAG"))
    stub_id = r.xadd(CANDIDATES, {"json": json.dumps(stub, sort_keys=True)})
    r.xadd(EVENTS, {"event": CANDIDATE_OPENED, "json": json.dumps(
        {"event": CANDIDATE_OPENED, "stub_id": stub_id, "lane": lane, "source_event": stub["source_event"],
         "question": stub["question"], "basis": stub["basis"], "ts": ts}, sort_keys=True)})
    return {"ok": True, "stub_id": stub_id}


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


def main(argv=None) -> int:
    """python -m primordial.fabric.envelope lint [PY ...] [--rows JSONL ...]  (rc 0 clean, 1 violations)."""
    import argparse
    ap = argparse.ArgumentParser(prog="python -m primordial.fabric.envelope")
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("lint", help="G1 vocabulary lint")
    lp.add_argument("paths", nargs="*", help="python sources (default: primordial/**/*.py minus tests)")
    lp.add_argument("--rows", nargs="*", default=[], help="JSONL rows files")
    a = ap.parse_args(argv)
    out = lint_vocabulary(a.paths or None, a.rows)
    for v in out["violations"]:
        print(f"  VIOLATION {v}")
    print(f"checks run: {out['checks']}")
    print(f"violations: {len(out['violations'])}")
    print(f"vocabulary lint: {'PASS' if out['ok'] else 'FAIL'}")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
