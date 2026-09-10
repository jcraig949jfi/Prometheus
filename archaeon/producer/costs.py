"""Producer-side cost receipts (design v0.1 C4; brief requirement 5).

Every paid producer activity -- generation, retrieval, retention, decoder or
readout preparation, transfer, analysis -- emits one CostEvent with a unique
id, the attempt it belongs to, the stage, source/output artifact references,
an environment identity, and a resource vector whose every entry carries
{quantity, unit, method, enforcement_class, scope}. Enforcement classes are
the engine's: enforceable | measured | estimated | unavailable. Unavailable
is not zero and is never summed as zero.

Two rules from the design are mechanical here:

* A cost event has ONE billing owner; roll-ups reference child event ids
  rather than billing them again (`rollup`).
* Actual source-construction cost is recorded ONCE in the physical ledger;
  each counterfactual arm ATTRIBUTES the cost it would need under a frozen
  reuse horizon (`attribute_counterfactual`), so a shared source build is
  neither counted four times nor free for one arm.

Reconciliation against the executor's vector (Vivarium's load receipt +
resource vector) is by attempt id and stage; engine-side cost events
(Daedalus C4-3) do not exist yet, so reconciliation is producer<->executor
only and says so.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

ENFORCEMENT = ("enforceable", "measured", "estimated", "unavailable")
STAGES = ("generation", "oracle", "verification", "retrieval", "retention",
          "extraction", "decoder_training", "readout_training", "transfer",
          "execution", "analysis", "decoder_apply", "archive_replay")
UNITS = {"cpu_seconds": "s", "wall_seconds": "s", "gpu_seconds": "s",
         "oracle_calls": "count", "vm_operations": "count", "ca_cell_updates": "count",
         "solver_calls": "count", "retained_bytes": "bytes", "output_bytes": "bytes",
         "peak_memory_bytes": "bytes", "items": "count"}


@dataclass(frozen=True)
class Resource:
    resource: str
    quantity: Optional[float]           # None iff unavailable
    unit: str
    method: str                         # how it was obtained
    enforcement_class: str
    scope: str = "producer"

    def __post_init__(self):
        if self.enforcement_class not in ENFORCEMENT:
            raise ValueError("enforcement_class must be one of {}".format(ENFORCEMENT))
        if self.enforcement_class == "unavailable" and self.quantity is not None:
            raise ValueError("an unavailable resource has no quantity; unavailable is not zero")
        if self.enforcement_class != "unavailable" and self.quantity is None:
            raise ValueError("a {} resource needs a quantity".format(self.enforcement_class))
        if self.resource in UNITS and UNITS[self.resource] != self.unit:
            raise ValueError("resource {} is measured in {}, not {}".format(self.resource, UNITS[self.resource], self.unit))


def environment_identity() -> Dict[str, str]:
    return {"host": platform.node(), "platform": platform.platform(),
            "python": platform.python_version(), "pid": str(os.getpid())}


@dataclass
class CostEvent:
    stage: str
    attempt_id: str
    resources: List[Resource]
    source_refs: List[str] = field(default_factory=list)
    output_refs: List[str] = field(default_factory=list)
    billing_owner: str = "archaeon"
    children: List[str] = field(default_factory=list)      # roll-ups reference, never re-bill
    counterfactual: Optional[Dict[str, Any]] = None
    environment: Dict[str, str] = field(default_factory=environment_identity)
    started_at: float = field(default_factory=time.time)
    cost_event_id: str = ""

    def __post_init__(self):
        if self.stage not in STAGES:
            raise ValueError("stage must be one of {}".format(STAGES))
        if not self.cost_event_id:
            self.cost_event_id = self._identity()

    def _identity(self) -> str:
        body = {"stage": self.stage, "attempt_id": self.attempt_id,
                "resources": [asdict(r) for r in self.resources],
                "source_refs": self.source_refs, "output_refs": self.output_refs,
                "billing_owner": self.billing_owner, "children": self.children,
                "counterfactual": self.counterfactual, "started_at": self.started_at,
                "environment": self.environment}
        return "cost:" + hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()[:24]

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        d["resources"] = [asdict(r) for r in self.resources]
        return d


class Meter:
    """Wall and CPU seconds for one stage, measured (not enforceable) on the
    producer side. Use as a context manager."""

    def __init__(self):
        self.wall = None
        self.cpu = None

    def __enter__(self):
        self._w0 = time.perf_counter(); self._c0 = time.process_time(); return self

    def __exit__(self, *exc):
        self.wall = time.perf_counter() - self._w0
        self.cpu = time.process_time() - self._c0

    def resources(self, extra: Optional[List[Resource]] = None) -> List[Resource]:
        rs = [Resource("wall_seconds", self.wall, "s", "time.perf_counter delta", "measured"),
              Resource("cpu_seconds", self.cpu, "s", "time.process_time delta (this process)", "measured"),
              Resource("gpu_seconds", None, "s", "not instrumented on the producer", "unavailable")]
        return rs + list(extra or [])


def rollup(parent_stage: str, attempt_id: str, events: List[CostEvent]) -> CostEvent:
    """Sum ADDITIVE quantities of children into one parent event that
    references them. Peak memory is never summed (max is reported per child
    only); unavailable resources stay unavailable in the roll-up."""
    totals: Dict[str, float] = {}
    unavailable: set = set()
    for e in events:
        for r in e.resources:
            if r.resource == "peak_memory_bytes":
                continue
            if r.enforcement_class == "unavailable":
                unavailable.add(r.resource); continue
            totals[r.resource] = totals.get(r.resource, 0.0) + float(r.quantity)
    rs = [Resource(k, v, UNITS.get(k, "count"), "sum of child events", "measured") for k, v in sorted(totals.items())]
    rs += [Resource(k, None, UNITS.get(k, "count"), "unavailable in at least one child", "unavailable")
           for k in sorted(unavailable) if k not in totals]
    return CostEvent(stage=parent_stage, attempt_id=attempt_id, resources=rs,
                     children=[e.cost_event_id for e in events])


def attribute_counterfactual(physical: CostEvent, arm: str, uses_it: bool,
                             reuse_horizon: int) -> Dict[str, Any]:
    """The cost a comparison ARM would need for a shared source build under
    a frozen reuse horizon. The physical event is charged once elsewhere;
    this is attribution, and it says so."""
    if reuse_horizon < 1:
        raise ValueError("reuse_horizon must be >= 1")
    share = {}
    for r in physical.resources:
        if r.enforcement_class == "unavailable":
            share[r.resource] = None
        else:
            share[r.resource] = (float(r.quantity) / reuse_horizon) if uses_it else 0.0
    return {"schema": "archaeon.cost.counterfactual.v0", "arm": arm, "uses_source": uses_it,
            "physical_cost_event_id": physical.cost_event_id, "reuse_horizon": reuse_horizon,
            "attributed": share,
            "note": "attribution under a frozen reuse horizon; the physical cost is charged once in the ledger"}


def reconcile(producer: List[CostEvent], executor_vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Match producer events to executor resource vectors by attempt_id.
    Reports matched, producer-only and executor-only attempts. Engine-side
    events are not part of this until Daedalus C4-3 exists."""
    p = {e.attempt_id for e in producer}
    x = {v.get("attempt_id") for v in executor_vectors}
    return {"matched": sorted(p & x), "producer_only": sorted(p - x),
            "executor_only": sorted(x - p), "engine_side": "absent (Daedalus C4-3)"}
