"""SFE RUNTIME bridge (overnight C43): a kernel Executor for the Serendipity Foundry Engine's worker loop.

This is the OTHER SFE seam -- not the frontier scheduler's spec (backends/sfe.py, which cannot express a
general IR: mismatches M1-M6), but the runtime's own pluggable execution contract (sfe/executors.py:
Executor.execute(WorkPackage) -> ExecutorResult, dispatched by `kind` in WorkerLoop). A WorkPackage of kind
"kernel.run_ir" carries the Experiment IR in its payload; the kernel executes it locally and returns the
receipts as an artifact plus the SUMMARY as the result, with SFE's own reproducibility vocabulary set from
the kernel's replay classes. Nothing in SFE is edited: Daedalus registers this class with a worker
(`WorkerLoop(foundry, worker_id, executors=[KernelExecutor()])`) or does not.

Imported lazily: on a tree without sfe/ the class still exists (for tests of the mapping) but
`available()` is False.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
from typing import Any, Dict

KIND = "kernel.run_ir"
REPRO_MAP = {"BIT": "BIT_DETERMINISTIC", "SEMANTIC": "SEMANTIC", "PARTIAL": "PARTIAL", "NONDETERMINISTIC": "NONDETERMINISTIC", "NOT_RUN": "NONDETERMINISTIC"}


def _sfe():
    root = pathlib.Path(__file__).resolve().parents[3] / "SerendipityFoundry" / "SerendipityFoundryEngine"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from sfe import executors as X
    return X


def available() -> bool:
    try:
        _sfe(); return True
    except Exception:
        return False


def run_payload(payload: Dict[str, Any], seed_root: int, workdir=None) -> Dict[str, Any]:
    """Backend-neutral half of the bridge: payload {"experiment": IR dict} -> {"status", "summary", "receipts_bytes",
    "reproducibility", "error"}. seed_root is SFE's; the IR's own seed_policy governs, and the mismatch is recorded."""
    from prometheus.toolbox.ir import Experiment, IRError
    from prometheus.toolbox.backends.local import execute
    from prometheus.toolbox.receipt import read_all
    from prometheus.toolbox.registry import default_registry
    out: Dict[str, Any] = {"status": "FAILED", "summary": None, "receipts_bytes": b"", "reproducibility": "NONDETERMINISTIC", "error": None}
    try:
        exp = Experiment.from_dict(payload["experiment"])
    except (KeyError, TypeError) as exc:
        out["error"] = "payload has no valid experiment: %s" % exc; return out
    try:
        low = exp.compile("local", default_registry())
    except IRError as exc:
        out["error"] = "invalid IR: %s" % exc; return out
    if not low.ok:
        out["error"] = "%s: %s" % (low.status, low.reasons); out["status"] = low.status; return out
    wd = pathlib.Path(workdir) if workdir else pathlib.Path(tempfile.mkdtemp(prefix="kernel_sfe_"))
    path = wd / "receipts.jsonl"
    rep = execute(low.job, path, default_registry())
    rs = read_all(path)
    classes = {r["replay_class"] for r in rs if r["arm"] != "SUMMARY" and r["status"] == "COMPLETED"}
    repro = "BIT_DETERMINISTIC" if classes == {"BIT"} else ("SEMANTIC" if classes <= {"BIT", "SEMANTIC"} and classes else ("PARTIAL" if "PARTIAL" in classes else "NONDETERMINISTIC"))
    out.update({"status": "COMPLETED" if rep.n_failed == 0 else "COMPLETED_WITH_FAILED_RUNS", "summary": rs[-1], "receipts_bytes": path.read_bytes(),
                "reproducibility": repro, "n_runs": rep.n_runs, "n_failed": rep.n_failed, "valid": rep.valid, "controls": rep.controls,
                "note": "seed_root %r from SFE is recorded, not used: the IR's seed_policy governs (recorded mismatch, not hidden)" % seed_root})
    return out


class KernelExecutor:
    """sfe.executors.Executor for kind 'kernel.run_ir'. Duck-typed on purpose so this module imports without sfe."""
    kind = KIND

    def execute(self, wp):
        X = _sfe()
        r = run_payload(dict(wp.payload), wp.seed_root)
        status = "COMPLETED" if r["status"].startswith("COMPLETED") else "FAILED"
        result = {k: v for k, v in r.items() if k not in ("receipts_bytes", "summary")}
        result["summary_receipt_id"] = (r["summary"] or {}).get("receipt_id")
        return X.ExecutorResult(status=status, result=result, artifacts=[r["receipts_bytes"]] if r["receipts_bytes"] else [],
                                reproducibility=r["reproducibility"], error=r["error"])
