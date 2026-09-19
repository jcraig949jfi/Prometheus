"""Experiment IR -- core.experiment.v1 (WORLDS_KERNEL_DESIGN v0.2 s4).

One backend-neutral description of scientific intent. It names components by registry kind and
parameters; it never names a library, a host, a queue or a transport. It has NO run(): it lowers
through `compile(target)` to a backend job (backends/local.py, backends/sfe.py, backends/npe.py),
and a backend that cannot express it faithfully returns a Lowering with status TARGET_UNSUPPORTED
and the exact mismatch -- never a distorted experiment.

    exp = Experiment(family="delay_sweep", world={"kind": "world.integer.v1", "params": {...}}, ...)
    exp.validate()                      # -> [] or a list of defects (strings)
    exp.digest()                        # content identity, stable across processes
    exp.compile("local", registry)      # -> Lowering(status, job, reasons)
"""
from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, FrozenSet, List, Optional

from prometheus.toolbox import capabilities as C

SCHEMA = "prometheus.toolbox.experiment.v1"
TARGETS = ("local", "sfe", "npe")
LOWERING_STATUSES = ("OK", "TARGET_UNSUPPORTED", "BLOCKED_MISSING_CAPABILITY", "UNAVAILABLE_INTERFACE")
CONTROL_KINDS = ("positive", "negative", "sham", "scratch", "permutation", "compute_matched", "storage_matched",
                 "replay", "ablation", "transplant", "cheat")


class IRError(ValueError):
    pass


def _h(obj, n=16) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:n]


def ref(kind: str, **params) -> dict:
    """A component reference: {"kind": <registry id>, "params": {...}}."""
    return {"kind": kind, "params": params}


@dataclass
class Experiment:
    family: str
    world: dict                                   # ref()
    substrate: dict                               # ref()
    players: List[dict] = field(default_factory=list)    # PlayerSpec.manifest() dicts, or [] when a selector proposes them
    interventions: List[dict] = field(default_factory=list)   # Intervention.manifest() dicts
    objective: Optional[dict] = None              # ref()
    observers: List[dict] = field(default_factory=list)       # ref()
    controls: List[dict] = field(default_factory=list)        # ref()  kind in CONTROL_KINDS via registry slot "control"
    transforms: List[dict] = field(default_factory=list)      # ref() + "target"
    selector: Optional[dict] = None               # ref()
    sweep: Dict[str, List[Any]] = field(default_factory=dict)  # dotted path -> values (cartesian)
    seed_policy: Dict[str, Any] = field(default_factory=lambda: {"base": 0, "n_seeds": 1})
    budget: Dict[str, Any] = field(default_factory=lambda: {"episodes": 1, "horizon": 64})
    required_capabilities: FrozenSet[str] = frozenset()
    provenance: Dict[str, Any] = field(default_factory=dict)  # designer seat, lane, note; never a verdict
    id: Optional[str] = None
    schema: str = SCHEMA

    def __post_init__(self):
        # C45: the IR is data; component OBJECTS a designer naturally writes are converted to their manifests here
        self.players = [p.manifest() if hasattr(p, "manifest") and not isinstance(p, dict) else p for p in self.players]
        self.interventions = [iv.manifest() if hasattr(iv, "manifest") and not isinstance(iv, dict) else iv for iv in self.interventions]
        self.required_capabilities = frozenset(self.required_capabilities)

    # ---------------------------------------------------------------- identity
    def to_dict(self) -> dict:
        d = asdict(self)
        d["required_capabilities"] = sorted(self.required_capabilities)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Experiment":
        d = dict(d)
        d["required_capabilities"] = frozenset(d.get("required_capabilities", ()))
        return cls(**d)

    def digest(self) -> str:
        """Content identity of the SCIENTIFIC definition: id, provenance and the wall budget (execution policy,
        C68: a job stopped by its wall clock and finished later is the same experiment) are excluded."""
        d = self.to_dict(); d.pop("id", None); d.pop("provenance", None)
        d["budget"] = {k: v for k, v in d.get("budget", {}).items() if k not in ("wall_s", "max_runs")}     # execution policy, not science
        return _h(d)

    def experiment_id(self) -> str:
        return self.id or "%s/%s" % (self.family, self.digest())

    # ---------------------------------------------------------------- validation (data only; no registry needed)
    def validate(self) -> List[str]:
        bad: List[str] = []
        if self.schema != SCHEMA:
            bad.append("schema")
        if not self.family or "/" in self.family:
            bad.append("family must be a non-empty name without '/'")
        for name, r in (("world", self.world), ("substrate", self.substrate)):
            if not isinstance(r, dict) or not r.get("kind"):
                bad.append("%s.kind" % name)
        for name, lst in (("observers", self.observers), ("controls", self.controls), ("transforms", self.transforms), ("interventions", self.interventions)):
            if not isinstance(lst, list):
                bad.append(name)
        if self.objective is not None and not self.objective.get("kind"):
            bad.append("objective.kind")
        # C84: players may be EMPTY -- a world observed with no player is a legitimate experiment; the world must
        # declare n_players=0 or lowering refuses the mismatch (C52). Nothing here assumes an agent exists.
        for i, p in enumerate(self.players):
            if not isinstance(p, dict) or "representation" not in p or "payload" not in p:
                bad.append("players[%d] is not a PlayerSpec manifest" % i)
            elif "substrate" in p and not (isinstance(p["substrate"], dict) and p["substrate"].get("kind")):
                bad.append("players[%d].substrate must be a component ref when present" % i)
        sp = self.seed_policy
        if not isinstance(sp.get("base"), int) or not isinstance(sp.get("n_seeds"), int) or sp["n_seeds"] < 1:
            bad.append("seed_policy needs int base and n_seeds >= 1")
        if "holdout_seeds" in sp and (not isinstance(sp["holdout_seeds"], int) or sp["holdout_seeds"] < 0):
            bad.append("seed_policy.holdout_seeds must be a non-negative int when present")
        b = self.budget
        if not isinstance(b.get("episodes"), int) or b["episodes"] < 1 or not isinstance(b.get("horizon"), int) or b["horizon"] < 0:
            bad.append("budget needs int episodes >= 1 and horizon >= 0")
        if "series_max_records" in b and (not isinstance(b["series_max_records"], int) or b["series_max_records"] < 0):
            bad.append("budget.series_max_records must be a non-negative int when present")
        if b.get("world_state", "episode") not in ("episode", "lifetime"):
            bad.append("budget.world_state must be 'episode' or 'lifetime'")
        if "max_runs" in b and (not isinstance(b["max_runs"], int) or b["max_runs"] < 1):
            bad.append("budget.max_runs must be a positive int when present")
        for path, vals in self.sweep.items():
            if not isinstance(vals, list) or not vals:
                bad.append("sweep[%s] must be a non-empty list" % path)
            if path.split(".")[0] not in ("world", "substrate", "interventions", "budget", "seed_policy", "objective", "players"):
                bad.append("sweep[%s]: axis root not sweepable" % path)
        for c in self.required_capabilities:
            if not C.well_formed(c):
                bad.append("required_capabilities: malformed %r" % c)
        try:                                                      # C30: an IR is pure data or it is not an IR
            json.dumps(self.to_dict(), allow_nan=False)
        except (TypeError, ValueError) as exc:
            bad.append("not serialisable as JSON (%s): an IR carries data only, never objects, callables or NaN" % str(exc)[:60])
        return bad

    # ---------------------------------------------------------------- requirements
    def component_kinds(self) -> List[str]:
        kinds = [self.world["kind"], self.substrate["kind"]]
        kinds += [o["kind"] for o in self.observers] + [c["kind"] for c in self.controls] + [t["kind"] for t in self.transforms]
        if self.objective:
            kinds.append(self.objective["kind"])
        if self.selector:
            kinds.append(self.selector["kind"])
        return kinds

    def derived_requirements(self) -> FrozenSet[str]:
        """Requirements implied by the IR's own content (interventions, players), unioned with the declared set.
        A designer may declare MORE; the kernel never lets them declare fewer than the content implies."""
        req = set(self.required_capabilities) | {"core.world.v1", "core.player.v1", "core.substrate.v1"}
        for iv in self.interventions:
            if iv.get("world_params"):
                req.add("ext.intervention.world_params.v1")
            for k in (iv.get("wrappers") or {}):
                req.add("ext.intervention.%s.v1" % k)
            if iv.get("schedule"):
                req.add("ext.intervention.schedule.v1"); req.add("ext.world.mutable_params.v1")
        for p in self.players:
            req |= set(p.get("requires", ()))
        if len(self.players) > 1:
            req.add("ext.multiplayer.v1")
        if self.budget.get("world_state") == "lifetime":
            req.add("ext.world.lifetime_state.v1")
        return frozenset(req)

    # ---------------------------------------------------------------- sweep expansion
    def sweep_points(self) -> List[dict]:
        if not self.sweep:
            return [{}]
        keys = list(self.sweep.keys())
        return [dict(zip(keys, vals)) for vals in itertools.product(*[self.sweep[k] for k in keys])]

    def at_point(self, point: dict) -> "Experiment":
        d = self.to_dict()
        for path, v in point.items():
            _set(d, path, v)
        d["sweep"] = {}
        d["id"] = None
        e = Experiment.from_dict(d)
        e.provenance = dict(self.provenance, sweep_point=point, parent=self.experiment_id())
        return e

    # ---------------------------------------------------------------- lowering
    def compile(self, target: str, registry=None) -> "Lowering":
        if target not in TARGETS:
            raise IRError("unknown target %r (one of %s)" % (target, TARGETS))
        defects = self.validate()
        if defects:
            raise IRError("experiment is not valid: %s" % defects)
        from prometheus.toolbox.registry import default_registry
        registry = registry or default_registry()
        if target == "local":
            from prometheus.toolbox.backends.local import lower
        elif target == "sfe":
            from prometheus.toolbox.backends.sfe import lower
        else:
            from prometheus.toolbox.backends.npe import lower
        return lower(self, registry)


@dataclass
class Lowering:
    target: str
    status: str
    experiment_id: str
    job: Any = None                      # LocalJob | frontier spec dict(s) | BusJob dict(s)
    reasons: List[str] = field(default_factory=list)
    negotiation: Optional[dict] = None

    @property
    def ok(self) -> bool:
        return self.status == "OK"

    def as_dict(self) -> dict:
        return {"target": self.target, "status": self.status, "experiment_id": self.experiment_id,
                "reasons": self.reasons, "negotiation": self.negotiation,
                "job": self.job.as_dict() if hasattr(self.job, "as_dict") else self.job}


def _set(d: dict, path: str, value) -> None:
    keys = path.split("."); cur: Any = d
    for k in keys[:-1]:
        if isinstance(cur, list):
            cur = cur[int(k)]
        else:
            cur = cur.setdefault(k, {})
    if isinstance(cur, list):
        cur[int(keys[-1])] = value
    else:
        cur[keys[-1]] = value


def _get(d: dict, path: str):
    cur: Any = d
    for k in path.split("."):
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur
