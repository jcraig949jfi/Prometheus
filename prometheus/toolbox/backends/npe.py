"""NPE lowering: Experiment IR -> BusJob (a Primordial Machine fabric job: envelope + payload).

STATUS 2026-09-18: UNAVAILABLE_INTERFACE by decision D-BELL-2. primordial/ exists only on branch
nestor/sidequest-graphworld-2026-09-14; nothing here imports it. The MINIMAL NPE-FACING INTERFACE this
adapter targets is pinned below from primordial/fabric/envelope.py at that branch's tip (b22a09b19):
the eleven envelope FIELDS and their validation rules. When a worker on the NPE side that runs
`prometheus.toolbox.backends.local.execute` on a payload lands on main (one file, lane A's to write),
this lowering becomes OK without changing the IR.

Semantic mismatch recorded for F1 (directive s5): an NPE job is a LANE ENTRY POINT (job_key -> a Python
callable in the lane's directory, kwargs, rows emitted through fabric.rows with the frozen row vocabulary);
the kernel IR is backend-neutral data. The bridge is therefore a generic job_key ("kernel.run_ir") whose
callable is the local executor, and rows = kernel receipts re-emitted in the fabric row vocabulary
(status "record"; evidence_class "OBSERVATION"). No IR field is lost in that mapping; what is NOT expressible
is the fabric's stage admission (campaign_stage ceilings) -- that is an NPE execution policy, not a
scientific field, so it lives in the envelope the caller fills, never in the IR.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from prometheus.toolbox.ir import Experiment, Lowering

# Pinned from primordial/fabric/envelope.py @ b22a09b19 (branch nestor/sidequest-graphworld-2026-09-14).
ENVELOPE_FIELDS = ("campaign_stage", "wall_budget_s", "cpu_budget_s", "gpu_budget_s", "expected_output_rows",
                   "checkpointable", "required_controls", "required_oracles", "cohort", "predicate_id", "experiment_class")
STAGES = ("SMOKE", "PILOT", "PRODUCTION", "REPLICATION")
NUMERIC = ("wall_budget_s", "cpu_budget_s", "gpu_budget_s", "expected_output_rows")
LISTS = ("required_controls", "required_oracles")
ROW_STATUSES = ("record", "dev", "aborted", "timeout", "cheat", "control")
EVIDENCE_CLASSES = ("VERDICT", "OBSERVATION")
JOB_KEY = "kernel.run_ir"
PINNED_AT = {"branch": "nestor/sidequest-graphworld-2026-09-14", "sha": "b22a09b19", "file": "primordial/fabric/envelope.py"}


def validate_envelope(env: dict) -> List[str]:
    """A copy of envelope.validate()'s rules so a BusJob can be checked here without importing primordial."""
    out = ["ENVELOPE_MISSING_FIELD:%s" % k for k in ENVELOPE_FIELDS if k not in env]
    if "campaign_stage" in env and env["campaign_stage"] not in STAGES:
        out.append("STAGE_NOT_ALLOWED")
    for k in NUMERIC:
        v = env.get(k)
        if k in env and (isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0):
            out.append("ENVELOPE_BAD_VALUE:%s" % k)
    if "checkpointable" in env and not isinstance(env["checkpointable"], bool):
        out.append("ENVELOPE_BAD_VALUE:checkpointable")
    for k in LISTS:
        if k in env and not isinstance(env[k], list):
            out.append("ENVELOPE_BAD_VALUE:%s" % k)
    for k in ("cohort", "predicate_id", "experiment_class"):
        if k in env and not (isinstance(env[k], str) and env[k].strip()):
            out.append("ENVELOPE_BAD_VALUE:%s" % k)
    if "evidence_class" in env and env["evidence_class"] not in EVIDENCE_CLASSES:
        out.append("ENVELOPE_BAD_VALUE:evidence_class")
    return out


def bus_job(exp: Experiment, *, stage: str = "SMOKE", cohort: str = "kernel", wall_budget_s: int = 900, cpu_budget_s: int = 900) -> dict:
    n_runs = len(exp.sweep_points()) * (1 + len(exp.controls)) * exp.seed_policy["n_seeds"]
    env = {"campaign_stage": stage, "wall_budget_s": wall_budget_s, "cpu_budget_s": cpu_budget_s, "gpu_budget_s": 0,
           "expected_output_rows": n_runs + 1, "checkpointable": False,
           "required_controls": [c["kind"] for c in exp.controls], "required_oracles": ["trace_hash"],
           "cohort": cohort, "predicate_id": "kernel-ir:%s" % exp.digest(), "experiment_class": "KERNEL_IR", "evidence_class": "OBSERVATION"}
    return {"job_key": JOB_KEY, "envelope": env, "kwargs": {"experiment": exp.to_dict()},
            "hypothesis": exp.provenance.get("note", "kernel IR %s" % exp.experiment_id()),
            "row_mapping": {"status": "record", "evidence_class": "OBSERVATION", "receipt_schema": "prometheus.toolbox.receipt.v1"}}


def primordial_available() -> bool:
    try:
        import importlib
        importlib.import_module("primordial.fabric.envelope")
        return True
    except Exception:
        return False


def lower(exp: Experiment, registry) -> Lowering:
    eid = exp.experiment_id()
    job = bus_job(exp)
    bad = validate_envelope(job["envelope"])
    if bad:
        return Lowering("npe", "TARGET_UNSUPPORTED", eid, job=job, reasons=bad)
    if not primordial_available():
        return Lowering("npe", "UNAVAILABLE_INTERFACE", eid, job=job,
                        reasons=["primordial.fabric not on this tree (D-BELL-2); BusJob built against the pinned interface %s and validated structurally" % PINNED_AT])
    return Lowering("npe", "OK", eid, job=job)
