"""Execution adapter: a Cell -> one SFE experiment (own client, own session)
-> one PEW fossil (namespace "theophrastus", never "prod") -> one ledger row.

SAME ENGINE, SAME WORLD MACHINERY, DIFFERENT EXPLORATION STRATEGY. This
module does not reimplement the execution path: it builds Vivarium's own
`ExecutionRequest` from the cell's sealed spec and hands it to Vivarium's
`SfeRunner` (viv/runner.py) used as a LIBRARY, so lease-keeping, the audit
envelope, repeat semantics, the outcome rule and the science profile are
byte-for-byte what the bench applies. The queue is not touched; the
consumer daemon is not started. Theophrastus is a separate SFE client, so
per-client ownership (403 on another client's world) isolates its worlds
from Vivarium's.

Credentials: theophrastus/config.local.json (gitignored) holds the SFE token
registered once on 2026-09-13; the PEW bearer is the committed legacy token
in evidence_wiki/config.json, presented with X-Prometheus-Agent=Theophrastus.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from . import __version__
from .cell import Cell
from .controls import result_digest
from .ledger import Ledger

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "vivarium", REPO / "SerendipityFoundry" / "SerendipityFoundryClient",
           REPO / "evidence_wiki", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from viv import runner as _runner                  # noqa: E402
from viv import request as _request                # noqa: E402
from viv import pew as _pew                        # noqa: E402

LOCAL = REPO / "theophrastus" / "config.local.json"
CACERT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient" / "config" / "m1.crt"
PEW_BASE = "http://192.168.1.202:8377/api/v1"
PEW_NAMESPACE = "theophrastus"


def _local() -> dict:
    if not LOCAL.exists():
        raise RuntimeError("theophrastus/config.local.json missing: register the "
                           "SFE identity once (see adapter.py docstring)")
    return json.loads(LOCAL.read_text(encoding="utf-8"))


def _pew_token() -> str:
    cfg = json.loads((REPO / "evidence_wiki" / "config.json").read_text(encoding="utf-8"))
    return cfg["auth_token"]


class Adapter:
    def __init__(self, ledger: Ledger, *, worker_id: str = "theophrastus@m1",
                 write_pew: bool = True, log=print):
        cfg = _local()
        self.ledger = ledger
        self.log = log
        self.runner = _runner.SfeRunner(
            base_url=cfg["sfe_base_url"], cafile=str(CACERT),
            token=cfg["sfe_token"], worker_id=worker_id,
            client_name="theophrastus", client_id=cfg.get("sfe_client_id"),
            lease_s=120.0, log=lambda *a: None)
        self.engine = self.runner.engine_identity
        self.pew = None
        if write_pew:
            self.pew = _pew.PewClient(PEW_BASE, _pew_token(), machine="M1",
                                      agent="Theophrastus", namespace=PEW_NAMESPACE)
        self.attempts = 0

    # ------------------------------------------------------------------
    def execute(self, cell: Cell, *, attempt_tag: str = "", phase: str = "",
                budget_state: Optional[dict] = None) -> Dict[str, Any]:
        """Run one cell. Always writes a ledger row (COMPLETED or FAILED)."""
        self.attempts += 1
        spec = cell.to_spec()
        canonical = cell.canonical_bytes()
        sealed = cell.spec_hash
        attempt_id = "theo:%s:%s%d" % (cell.cell_id.split(":")[1][:16],
                                       attempt_tag, self.attempts)
        req = _request.ExecutionRequest(experiment_id=attempt_id,
                                        spec_json=canonical, spec_hash=sealed)
        row: Dict[str, Any] = {
            "row_id": attempt_id, "cell_id": cell.cell_id, "spec_hash": sealed,
            "phase": phase, "budget_at_charge": budget_state,
            "labels": cell.labels, "cell": cell.record(),
            "engine": self.engine, "consumer": {"component": "theophrastus.adapter",
                                                "version": __version__,
                                                "via": "viv.runner.SfeRunner (library)",
                                                "worker_id": self.runner.worker_id,
                                                "sfe_client_id": self.runner.client_id},
        }
        try:
            res = self.runner.run(req)
            row.update({"status": "COMPLETED", "outcome": res.outcome,
                        "world_id": res.world_id, "sfe_experiment_id": res.sfe_experiment_id,
                        "work_id": res.work_id, "run_id": res.run_id,
                        "obs_ids": list(res.obs_ids), "anchor": res.anchor,
                        "reproducibility": (res.work_result or {}).get("reproducibility"),
                        "work_result": res.work_result,
                        "result_digest": result_digest(res.work_result or {}),
                        "resources": res.resources, "science": res.science,
                        "audit_envelope": (res.summary or {}).get("audit_envelope"),
                        "elapsed_s": ((res.summary or {}).get("repeat") or {}).get("elapsed_s"),
                        "failure_class": None})
            run = res
        except _runner.ExecutionFailure as exc:
            run = exc.partial
            row.update({"status": "FAILED", "failure_class": exc.failure_class,
                        "error": str(exc)[:2000], "world_id": run.world_id,
                        "sfe_experiment_id": run.sfe_experiment_id,
                        "work_id": run.work_id, "run_id": run.run_id,
                        "crossed_boundary": run.crossed_boundary,
                        "work_result": {"repeats": run.repeats}, "anchor": run.anchor})
        except Exception as exc:                    # noqa: BLE001
            row.update({"status": "FAILED", "failure_class": "ADAPTER",
                        "error": "%s: %s" % (type(exc).__name__, str(exc)[:2000])})
            run = None
        # PEW fossil, namespace theophrastus. A failed write never erases the row.
        row["pew"] = self._fossilize(spec, run, cell, sealed) if run is not None else \
            {"written": False, "reason": "no run object"}
        return self.ledger.append("rows", row)

    def _fossilize(self, spec: dict, run, cell: Cell, sealed: str) -> dict:
        if self.pew is None:
            return {"written": False, "reason": "pew disabled"}
        if not (run.anchor or {}).get("resolved"):
            return {"written": False, "reason": "unresolved SFE anchor",
                    "anchor": run.anchor}
        producer = {"component": "theophrastus.crucible", "version": __version__,
                    "engine_source_hash": self.engine.get("engine_source_hash"),
                    "spec_hash": sealed, "cell_id": cell.cell_id,
                    "labels": cell.labels,
                    "proposal": cell.proposal}
        try:
            out = _pew.write_encounter(self.pew, spec=spec, run=run, engine=self.engine,
                                       producer_version=__version__,
                                       relation={"cell_id": cell.cell_id},
                                       producer=producer)
            return {"written": bool(out.get("pew_reference")), **out}
        except Exception as exc:                    # noqa: BLE001
            return {"written": False, "reason": "write_failed",
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:1500])}
