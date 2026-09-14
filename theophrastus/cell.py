"""The CELL: the smallest replayable experimental coordinate.

    CELL = (mechanism, pressure, world, branch, intervention) + seed_root

IDENTITY IS BY CONTENT, NEVER BY LABEL. A label ("W149", "GKL") is a human
handle carried beside the coordinate; `cell_id` hashes the coordinate's
CONTENT (rule hex, lattice tuple, density set, transform, branch members'
hexes, seed), so two labels for one coordinate collide (self-control C2) and
one label over two coordinates separates (C3). The sealed Vivarium spec is
DERIVED from the cell and hashed by Vivarium's own `viv.spec.spec_hash`, so a
cell's `spec_hash` is the same grouping surface the rest of the bench uses.

UNKNOWN is a value. A dimension this seat cannot evidence is written
"UNKNOWN", never defaulted (charter VI).
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "vivarium", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from viv import spec as _vspec                     # noqa: E402

UNKNOWN = "UNKNOWN"
KIND = "ca_density_v0"
SPEC_VERSION = 3


def _h(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Mechanism:
    name: str
    rule_hex: str
    #: repo-relative pointer + provenance class; None is a C7 violation.
    provenance: Optional[str]

    def content(self) -> dict:
        return {"rule_hex": self.rule_hex.lower()}


@dataclass(frozen=True)
class Branch:
    name: str
    #: rule hexes of the members, sorted; the relation is over CONTENT.
    members: Tuple[str, ...]
    #: where the relation is evidenced; None is a C4 violation.
    evidence: Optional[str]
    #: the relation to other branches, or UNKNOWN.
    relation: str = UNKNOWN

    def content(self) -> dict:
        return {"members": sorted(m.lower() for m in self.members),
                "relation": self.relation}


@dataclass(frozen=True)
class World:
    label: str
    n_cells: int
    steps: int
    radius: int = 3

    def content(self) -> dict:
        return {"n_cells": self.n_cells, "steps": self.steps,
                "radius": self.radius}

    @property
    def identity(self) -> str:
        return _h(self.content())


@dataclass(frozen=True)
class Pressure:
    label: str
    ic_density_set: Tuple[Optional[float], ...]
    n_ic: int
    success_criterion: str

    def content(self) -> dict:
        return {"ic_density_set": list(self.ic_density_set),
                "n_ic": self.n_ic,
                "success_criterion": self.success_criterion}

    @property
    def identity(self) -> str:
        return _h(self.content())


@dataclass(frozen=True)
class Intervention:
    label: str
    transform: str

    def content(self) -> dict:
        return {"transform": self.transform}


@dataclass(frozen=True)
class Repeat:
    count: int = 8
    seed_derivation: str = "sha256_index"
    max_seconds: int = 600

    def block(self) -> dict:
        return {"count": self.count, "order": "sequential",
                "seed_derivation": self.seed_derivation, "state": "reset",
                "budget": {"max_seconds": self.max_seconds,
                           "max_observations": self.count}}


@dataclass(frozen=True)
class Cell:
    mechanism: Mechanism
    pressure: Pressure
    world: World
    branch: Branch
    intervention: Intervention
    seed_root: int
    repeat: Repeat = field(default_factory=Repeat)
    #: who proposed it and why; NEVER read by selection (C9).
    proposal: Dict[str, Any] = field(default_factory=dict)

    # -- identity ---------------------------------------------------------
    def coordinates(self) -> dict:
        return {"mechanism": self.mechanism.content(),
                "pressure": self.pressure.content(),
                "world": self.world.content(),
                "branch": self.branch.content(),
                "intervention": self.intervention.content(),
                "seed_root": self.seed_root,
                "repeat": self.repeat.block()}

    @property
    def cell_id(self) -> str:
        return _h(self.coordinates())

    @property
    def labels(self) -> dict:
        return {"mechanism": self.mechanism.name, "pressure": self.pressure.label,
                "world": self.world.label, "branch": self.branch.name,
                "intervention": self.intervention.label,
                "seed_root": self.seed_root}

    def short(self) -> str:
        l = self.labels
        return "%s/%s/%s/%s/%s/s%d" % (l["mechanism"], l["world"], l["pressure"],
                                       l["branch"], l["intervention"],
                                       self.seed_root)

    # -- the sealed spec (Vivarium v3, exact kind contract) -----------------
    def payload(self) -> dict:
        return {"rule_hex": self.mechanism.rule_hex.lower(),
                "radius": self.world.radius,
                "n_cells": self.world.n_cells,
                "steps": self.world.steps,
                "n_ic": self.pressure.n_ic,
                "ic_density_set": list(self.pressure.ic_density_set),
                "success_criterion": self.pressure.success_criterion,
                "transform": self.intervention.transform}

    def to_spec(self, namespace_tag: str = "theophrastus") -> dict:
        cid = self.cell_id.split(":", 1)[1]
        spec = {
            "spec_version": SPEC_VERSION,
            "world": {"seed_root": self.seed_root},
            "hypothesis": ("Theophrastus cell %s: criteria_agree holds "
                           "(C1-e established both uniform states are fixed "
                           "points for this rule)" % cid[:16]),
            "prediction": None,
            "work": {"kind": KIND, "payload": self.payload()},
            "outcome_rule": {"field": "criteria_agree", "op": "==",
                             "value": True, "aggregate": "all",
                             "if_true": "SURVIVED",
                             "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE"},
            "pew": {"encounter_id": "ENC-%s-%s" % (namespace_tag, cid[:16]),
                    "players": ["evca:%s" % self.mechanism.name],
                    "required": False},
            "repeat": self.repeat.block(),
        }
        _vspec.validate(spec)
        return spec

    @property
    def spec_hash(self) -> str:
        return _vspec.spec_hash(self.to_spec())

    @property
    def execution_hash(self) -> str:
        """Hash of exactly what the EXECUTOR reads: seed, kind, payload,
        repeat, outcome rule. The sealed spec also carries the pew identity
        block (players, encounter_id), so two labels can seal two spec_hashes
        over ONE execution; alias (C2) and no-op (C5) detection key on this
        surface, which is the one the engine cannot tell apart."""
        s = self.to_spec()
        return _h({"world": s["world"], "work": s["work"],
                   "repeat": s["repeat"], "outcome_rule": s["outcome_rule"]})

    def canonical_bytes(self) -> bytes:
        return _vspec.canonical_bytes(self.to_spec())

    # -- provenance record (what another seat needs to reconstruct) ----------
    def record(self) -> dict:
        return {"cell_id": self.cell_id, "spec_hash": self.spec_hash,
                "execution_hash": self.execution_hash,
                "labels": self.labels, "coordinates": self.coordinates(),
                "mechanism_provenance": self.mechanism.provenance,
                "branch_evidence": self.branch.evidence,
                "branch_relation": self.branch.relation,
                "world_identity": self.world.identity,
                "pressure_identity": self.pressure.identity,
                "proposal": dict(self.proposal)}


def neighbours(cell: Cell, axis: str, values: List[Any]) -> List[Cell]:
    """A local stencil: hold four dimensions, move ONE."""
    out = []
    for v in values:
        kw = {"mechanism": cell.mechanism, "pressure": cell.pressure,
              "world": cell.world, "branch": cell.branch,
              "intervention": cell.intervention, "seed_root": cell.seed_root,
              "repeat": cell.repeat,
              "proposal": {**cell.proposal, "stencil_of": cell.cell_id,
                           "axis": axis}}
        if axis not in kw:
            raise ValueError("unknown axis %r" % axis)
        kw[axis] = v
        out.append(Cell(**kw))
    return out
