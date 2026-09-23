"""Experiment specifications (operator directive s1, s8, s9). An EXPERIMENT SPEC is data with every
required field; a FAMILY is a spec template plus a sweep grid that expands to many specs. Both are
validated by validate_spec() before they can enter a queue; the scheduler consumes only valid specs.

archaeon.frontier.experiment_spec.v1
  experiment_id       stable id (family_id + "/" + parameter digest, or the transformation id)
  family_id           the family this instance belongs to (a lineage's transformation, or a sweep)
  world               {"kind": "wse.WorldSpec", "knobs": {...}} | {"kind": "c6.composed.v1", "params": {...}} |
                      {"kind": "c6.composed.sample", "seed": int, "bin": int|null}    (generator spec: resolved by the runner)
  organism            {"profile": "v0"|"graph"|"repb_fizzle", "population": {"source": "c4_parents"|"foundry", "seed": int, "N": int}}
  params              {"E": int, "generations": int, "chunk": int, "archive": {...}, "freeze_policy": "tiered"|"c6_all_full"}
  schedule            {"kind": "stable"|"labeled"|"unlabeled", "seed": int}   (resolved by the runner)
  seed                the run seed (the runner derives every stream from it)
  budget              {"evaluations": int, "wall_s": int}
  controls            list of {"kind": "seed"|"initialization"|"budget"|"replay_A"|"replay_D", "spec_delta": {...}}  (descendant specs the runner may enqueue)
  required_capabilities  list of capability names (capabilities.PROBES)
  telemetry           {"t0_rows": true, "anchors": true, "detectors": "frozen_candidate", "log_scores": bool}
  output_schema       "archaeon.c6.segment_out.v1"
  checkpoint          {"resume": true, "replay_required": "A"}
  provenance          archaeon.c6.provenance.v1 (lane etc.)
  suppressions        list of suppression ids that apply (data files under frontier/suppressions/)
"""
from __future__ import annotations

import hashlib
import itertools
import json
from typing import Dict, Iterable, List

SCHEMA = "archaeon.frontier.experiment_spec.v1"
PROFILES = ("v0", "graph", "repb_fizzle")
WORLD_KINDS = ("wse.WorldSpec", "c6.composed.v1", "c6.composed.sample")
SCHEDULE_KINDS = ("stable", "labeled", "unlabeled")
LANES = ("HUMAN_DIRECTED", "LLM_PROPOSED", "PROCEDURAL", "EVOLUTION_GENERATED", "MIXED")
REQUIRED = ("experiment_id", "family_id", "world", "organism", "params", "schedule", "seed", "budget", "controls", "required_capabilities", "telemetry", "output_schema", "checkpoint", "provenance")


class SpecError(ValueError):
    pass


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:12]


def validate_spec(s: dict) -> dict:
    """Raise SpecError on any defect; return the spec with its digest filled."""
    if s.get("schema") != SCHEMA:
        raise SpecError("schema")
    for k in REQUIRED:
        if k not in s:
            raise SpecError("missing %s" % k)
    w = s["world"]
    if w.get("kind") not in WORLD_KINDS:
        raise SpecError("world.kind")
    if w["kind"] == "wse.WorldSpec" and "knobs" not in w:
        raise SpecError("world.knobs")
    if w["kind"] == "c6.composed.v1" and "params" not in w:
        raise SpecError("world.params")
    if w["kind"] == "c6.composed.sample" and not isinstance(w.get("seed"), int):
        raise SpecError("world.seed")
    o = s["organism"]
    if o.get("profile") not in PROFILES:
        raise SpecError("organism.profile")
    pop = o.get("population", {})
    if pop.get("source") not in ("c4_parents", "foundry") or not isinstance(pop.get("N"), int) or pop["N"] < 2:
        raise SpecError("organism.population")
    if o["profile"] == "graph" and pop["source"] != "foundry":
        raise SpecError("graph populations come from the graph foundry only (no lift from v0)")
    p = s["params"]
    for k in ("E", "generations", "chunk"):
        if not isinstance(p.get(k), int) or p[k] < 1:
            raise SpecError("params.%s" % k)
    if p.get("freeze_policy") not in ("tiered", "c6_all_full"):
        raise SpecError("params.freeze_policy")
    if s["schedule"].get("kind") not in SCHEDULE_KINDS:
        raise SpecError("schedule.kind")
    if not isinstance(s["seed"], int):
        raise SpecError("seed")
    b = s["budget"]
    if not isinstance(b.get("evaluations"), int) or b["evaluations"] < pop["N"]:
        raise SpecError("budget.evaluations")
    if not isinstance(s["controls"], list):
        raise SpecError("controls")
    if not isinstance(s["required_capabilities"], list) or not s["required_capabilities"]:
        raise SpecError("required_capabilities")
    if s["output_schema"] != "archaeon.c6.segment_out.v1":
        raise SpecError("output_schema")
    if s["checkpoint"].get("replay_required") not in ("A", None):
        raise SpecError("checkpoint.replay_required")
    if s["provenance"].get("lane") not in LANES:
        raise SpecError("provenance.lane")
    s = dict(s); s["spec_digest"] = _h({k: v for k, v in s.items() if k != "spec_digest"})
    return s


def capabilities_for(spec: dict) -> List[str]:
    """The capabilities a spec needs, derived from its content (a spec may list more; never fewer)."""
    need = {"segment_v1", "detectors_v1", "pressure_schedules_v1"}
    need.add({"v0": "v0_runtime", "graph": "graph_runtime", "repb_fizzle": "repb_fizzle"}[spec["organism"]["profile"]])
    need.add("composed_world_v1" if spec["world"]["kind"].startswith("c6.composed") else "wse_worldspec")
    if spec["organism"]["population"]["source"] == "c4_parents":
        need.add("c4_parents")
    return sorted(need)


def make_spec(*, family_id: str, experiment_id: str | None = None, world: dict, profile: str, population: dict, E: int, generations: int, chunk: int = 250,
              schedule: dict, seed: int, budget_evaluations: int, lane: str, generator: str, controls: list | None = None, suppressions: list | None = None,
              archive: dict | None = None, freeze_policy: str = "tiered", log_scores: bool = False, note: str = "",
              world_options: dict | None = None, nominate: dict | None = None, measurements: list | None = None) -> dict:
    from archaeon.campaign6 import schemas as S
    prov = S.provenance(lane, generator, "0.1", seed, {"family_id": family_id, "world": world.get("kind"), "profile": profile, "N": population["N"], "E": E, "generations": generations}, note=note)
    spec = {"schema": SCHEMA, "family_id": family_id, "world": world, "organism": {"profile": profile, "population": population},
            "params": {"E": E, "generations": generations, "chunk": chunk, "archive": archive or {"dense_until": 64, "neighbourhood": 16}, "freeze_policy": freeze_policy,
                       "world_options": world_options or {}, "nominate": nominate or {}, "measurements": measurements or []},
            "schedule": schedule, "seed": seed, "budget": {"evaluations": budget_evaluations, "wall_s": 6 * 3600},
            "controls": controls if controls is not None else default_controls(), "required_capabilities": [], "telemetry": {"t0_rows": True, "anchors": True, "detectors": "frozen_candidate", "log_scores": log_scores},
            "output_schema": "archaeon.c6.segment_out.v1", "checkpoint": {"resume": True, "replay_required": "A"}, "provenance": prov, "suppressions": suppressions or []}
    spec["required_capabilities"] = capabilities_for(spec)
    spec["experiment_id"] = experiment_id or (family_id + "/" + _h({k: v for k, v in spec.items() if k not in ("provenance",)}))
    return validate_spec(spec)


def default_controls() -> list:
    return [{"kind": "seed", "spec_delta": {"seed": "+1"}}, {"kind": "initialization", "spec_delta": {"organism.population.seed": "+1"}},
            {"kind": "replay_A", "spec_delta": {}}]


def expand_family(template: dict, grid: Dict[str, Iterable], *, family_id: str, id_prefix: str = "") -> List[dict]:
    """Cartesian sweep over dotted parameter paths; each point becomes a validated spec whose experiment_id encodes the point."""
    keys = list(grid.keys()); out = []
    for values in itertools.product(*[list(grid[k]) for k in keys]):
        s = json.loads(json.dumps(template))
        point = {}
        for k, v in zip(keys, values):
            _set(s, k, v); point[k] = v
        s["family_id"] = family_id
        s["experiment_id"] = "%s/%s%s" % (family_id, id_prefix, _h(point))
        s["sweep_point"] = point
        out.append(validate_spec(s))
    return out


def _set(d: dict, path: str, value) -> None:
    keys = path.split("."); cur = d
    for k in keys[:-1]:
        cur = cur.setdefault(k, {})
    cur[keys[-1]] = value


def apply_delta(spec: dict, delta: dict) -> dict:
    s = json.loads(json.dumps(spec))
    for path, v in delta.items():
        keys = path.split("."); cur = s
        for k in keys[:-1]:
            cur = cur[k]
        if isinstance(v, str) and v.startswith("+"):
            cur[keys[-1]] = cur[keys[-1]] + int(v[1:])
        elif isinstance(v, str) and v.startswith("x"):
            cur[keys[-1]] = int(cur[keys[-1]] * float(v[1:]))
        else:
            cur[keys[-1]] = v
    s.pop("spec_digest", None); s["experiment_id"] = spec["experiment_id"] + "/" + _h(delta)
    return validate_spec(s)
