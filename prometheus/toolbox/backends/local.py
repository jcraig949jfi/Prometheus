"""Local lowering and executor (directive s5, s25). The reference execution path.

lower(exp, registry) -> Lowering
    negotiates capabilities against the registry rows the IR names (BLOCKED_MISSING_CAPABILITY is a result),
    expands arms (primary + one per control) x sweep points x seeds into RunSpecs, and returns a LocalJob.
    No world is constructed at lowering time.

execute(job, out_path) -> ExecutionReport
    runs every RunSpec in order, writes one receipt per run (JSONL, flushed), then evaluates each control's
    expectation over (primary, arm) pairs keyed by (sweep_point, seed) and writes a control summary.
    A failed run is a FAILED receipt; a NOT_MET expectation marks the ARM receipt CONTROL_NOT_MET in the
    summary. Nothing here halts globally except an integrity error in the receipt writer itself.

The episode loop is the kernel's ONE execution semantics (every backend must reproduce it or declare it
cannot):  reset(seed) -> [observe all -> act all -> step -> drain events -> observers] x horizon or done.
Kernel-applied wrappers (interventions.wrappers): observation_delay, observation_permute.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from prometheus.toolbox import capabilities as C
from prometheus.toolbox.contracts import ActionSpace, PlayerSpec, component_manifest_hash
from prometheus.toolbox.ir import Experiment, Lowering
from prometheus.toolbox.receipt import ReceiptWriter
from prometheus.toolbox import series as SER
from prometheus.toolbox.ref.worlds import stream


# ---------------------------------------------------------------------------------------------- job
@dataclass
class RunSpec:
    arm: str                   # "primary" | control kind
    sweep_point: dict
    seed: int
    experiment: Experiment     # the arm's experiment at this sweep point

    def key(self):
        return (tuple(sorted(self.sweep_point.items())), self.seed)


@dataclass
class LocalJob:
    experiment_id: str
    runs: List[RunSpec] = field(default_factory=list)
    negotiation: Optional[dict] = None
    registry_rows: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"experiment_id": self.experiment_id, "n_runs": len(self.runs),
                "arms": sorted({r.arm for r in self.runs}), "negotiation": self.negotiation}


def seeds_for(exp: Experiment) -> List[int]:
    sp = exp.seed_policy
    return [sp["base"] + i for i in range(sp["n_seeds"])]


def lower(exp: Experiment, registry) -> Lowering:
    eid = exp.experiment_id()
    reasons: List[str] = []
    for kind in exp.component_kinds():
        if not registry.has(kind):
            reasons.append("no component registered as %r" % kind)
        elif registry.get(kind).state == "UNAVAILABLE":
            reasons.append("component %r is UNAVAILABLE: %s" % (kind, registry.get(kind).admission.get("failed")))
    if reasons:
        return Lowering("local", "TARGET_UNSUPPORTED", eid, reasons=reasons)
    provided = registry.provided_capabilities(exp.world["kind"], exp.substrate["kind"]) | {"core.player.v1", "core.experiment.v1", "core.receipt.v1"}
    # kernel-applied wrappers are capabilities the KERNEL provides
    provided |= {"ext.intervention.observation_delay.v1", "ext.intervention.observation_permute.v1"}
    sub = registry.make(exp.substrate["kind"], **exp.substrate.get("params", {}))
    provided |= set(sub.capabilities)
    for p in exp.players:
        if p["representation"] not in sub.representations:
            reasons.append("substrate %s cannot instantiate representation %r" % (sub.kind, p["representation"]))
    neg = C.negotiate(exp.derived_requirements(), provided)
    if not neg.ok:
        return Lowering("local", "BLOCKED_MISSING_CAPABILITY", eid, reasons=["missing: %s" % sorted(neg.missing)] + reasons, negotiation=neg.as_dict())
    if reasons:
        return Lowering("local", "TARGET_UNSUPPORTED", eid, reasons=reasons, negotiation=neg.as_dict())
    controls = [(c["kind"], registry.make(c["kind"], **c.get("params", {}))) for c in exp.controls]
    job = LocalJob(eid, negotiation=neg.as_dict(), registry_rows=[registry.get(k).row() for k in sorted(set(exp.component_kinds()))])
    for point in exp.sweep_points():
        base = exp.at_point(point)
        arms = [("primary", base)] + [(ctrl.kind, ctrl.arm(base, exp.seed_policy["base"] * 7919 + 1)) for _, ctrl in controls]
        for arm, aexp in arms:
            for s in seeds_for(exp):
                job.runs.append(RunSpec(arm, point, s, aexp))
    return Lowering("local", "OK", eid, job=job, negotiation=neg.as_dict())


# ---------------------------------------------------------------------------------------------- wrappers
class ObservationWrapper:
    """observation_delay: observe the state from d ticks ago (the first observation is repeated until d are buffered).
    observation_permute: a seeded permutation of observation channels, fixed for the episode."""

    def __init__(self, world, delay: int = 0, permute_seed: Optional[int] = None):
        self.w = world; self.delay = int(delay); self.permute_seed = permute_seed
        self._buf: Dict[int, List[List[int]]] = {}
        self._perm: Optional[List[int]] = None
        self.kind = world.kind; self.capabilities = world.capabilities; self.n_players = world.n_players

    def manifest(self) -> dict:
        return dict(self.w.manifest(), wrappers={"observation_delay": self.delay, "observation_permute": self.permute_seed})

    def reset(self, seed: int) -> None:
        self.w.reset(seed); self._buf = {}; self._perm = None

    def observe(self, pid: int) -> List[int]:
        obs = self.w.observe(pid)
        if self.permute_seed is not None:
            if self._perm is None:
                s = stream("permute", self.permute_seed); n = len(obs); perm = list(range(n))
                for i in range(n - 1, 0, -1):
                    j = s.below(i + 1); perm[i], perm[j] = perm[j], perm[i]
                self._perm = perm
            obs = [obs[i] for i in self._perm]
        if self.delay:
            buf = self._buf.setdefault(pid, [])
            buf.append(obs)
            if len(buf) > self.delay + 1:
                buf.pop(0)
            obs = buf[0] if len(buf) <= self.delay else buf[-1 - self.delay]
        return obs

    def __getattr__(self, name):
        return getattr(self.w, name)


def build_world(exp: Experiment, registry):
    params = dict(exp.world.get("params", {}))
    delay = 0; permute = None
    for iv in exp.interventions:
        params.update(iv.get("world_params", {}))
        wr = iv.get("wrappers", {})
        delay += int(wr.get("observation_delay", 0))
        if "observation_permute" in wr:
            permute = int(wr["observation_permute"])
    if "ext.intervention.world_params.v1" in registry.get(exp.world["kind"]).capabilities:
        params.setdefault("horizon", exp.budget["horizon"])     # a world without parameter overrides keeps its own horizon; the loop caps at budget.horizon anyway
    world = registry.make(exp.world["kind"], **params)
    if delay or permute is not None:
        world = ObservationWrapper(world, delay, permute)
    return world


# ---------------------------------------------------------------------------------------------- episode loop
def run_episode(world, instances: Dict[int, Any], observers: List[Any], seed: int, horizon: int) -> dict:
    world.reset(seed)
    for ob in observers:
        ob.begin({"n_players": world.n_players, "seed": seed})
    has_events = "ext.events.v1" in world.capabilities
    n_events = 0; ticks = 0; done = False
    while not done and ticks < horizon:
        observations = {pid: world.observe(pid) for pid in instances}
        actions = {pid: instances[pid].act(observations[pid], world.legal_actions(pid)) for pid in instances}
        done = world.step(actions)
        evs = world.events() if has_events else []
        n_events += len(evs)
        for ob in observers:
            # ORDER IS A CONTRACT (C1, 2026-09-19): the events of tick t are delivered BEFORE on_tick(t), so a
            # series record for tick t reflects the world AFTER step t (absorptions, yields of that tick included).
            if evs:
                ob.on_events(evs)
            ob.on_tick(ticks, observations, actions)
        ticks += 1
    return {"trace_hash": world.trace_hash(), "ticks": ticks, "events": n_events, "summary": world.summary() if hasattr(world, "summary") else {}}


def run_one(spec: RunSpec, registry, receipt_dir=None) -> dict:
    import pathlib
    receipt_dir = pathlib.Path(receipt_dir) if receipt_dir is not None else pathlib.Path(".")
    exp = spec.experiment
    started = datetime.now(timezone.utc).isoformat(); t0 = time.perf_counter(); c0 = time.process_time()
    world = build_world(exp, registry)
    sub = registry.make(exp.substrate["kind"], **exp.substrate.get("params", {}))
    specs = [PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {})) for p in exp.players]
    instances = {pid: sub.instantiate(ps, spec.seed * 31 + pid) for pid, ps in enumerate(specs)}
    fingerprints = {str(pid): inst.fingerprint() for pid, inst in instances.items()}   # spec identity: taken on the FRESH instance
    observers = [registry.make(o["kind"], **o.get("params", {})) for o in exp.observers]
    hashes: List[str] = []; ticks_total = 0; events_total = 0; summaries = []
    series_obs = [ob for ob in observers if getattr(ob, "series", False)]
    collected = {ob.kind: [] for ob in series_obs}
    for ep in range(exp.budget["episodes"]):
        r = run_episode(world, instances, observers, spec.seed * 1000 + ep, exp.budget["horizon"])
        hashes.append(r["trace_hash"]); ticks_total += r["ticks"]; events_total += r["events"]; summaries.append(r["summary"])
        for ob in series_obs:
            collected[ob.kind].append(ob.series_episode())
    wall = time.perf_counter() - t0; cpu = time.process_time() - c0
    acc = dict(sub.accounting()); acc.update(world.accounting() if hasattr(world, "accounting") else {"world_steps": ticks_total})
    acc["wall_s"] = round(wall, 6); acc["cpu_s"] = round(cpu, 6)
    science = {"observations": {ob.kind: ob.measure() for ob in observers}, "world_summary": summaries[-1] if summaries else {},
               "player_fingerprints": fingerprints}
    receipt = {
        "experiment_id": exp.experiment_id() if spec.arm == "primary" else exp.provenance.get("parent", exp.experiment_id()),
        "experiment_digest": exp.digest(), "arm": spec.arm, "sweep_point": spec.sweep_point, "seed": spec.seed, "status": "COMPLETED",
        "components": {"world": {"kind": exp.world["kind"], "manifest_hash": component_manifest_hash(world.manifest()), "manifest": world.manifest()},
                       "substrate": {"kind": sub.kind, "manifest_hash": component_manifest_hash(sub.manifest())},
                       "players": [{"representation": p.representation, "manifest_hash": component_manifest_hash(p.manifest()), "meta": p.meta} for p in specs],
                       "observers": [ob.manifest() for ob in observers],
                       "interventions": exp.interventions},
        "capabilities": {"required": sorted(exp.derived_requirements()), "world": sorted(world.capabilities), "substrate": sorted(sub.capabilities)},
        "replay_class": getattr(world, "replay_class", "NONDETERMINISTIC"), "trace_hashes": hashes, "events_total": events_total,
        "engineering": {"wall_s": acc["wall_s"], "cpu_s": acc["cpu_s"], "ticks": ticks_total, "steps_per_s": round(ticks_total / wall, 1) if wall > 0 else None},
        "science": science, "accounting": acc, "provenance": exp.provenance,
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    if series_obs:
        rc = receipt["replay_class"]
        receipt["series"] = {ob.kind: SER.build(collected[ob.kind], enabled=getattr(ob, "enabled", True), replay_class=rc,
                                                max_records=exp.budget.get("series_max_records"), max_inline=SER.DEFAULT_MAX_INLINE,
                                                receipt_dir=receipt_dir) for ob in series_obs}
    if exp.objective:
        obj = registry.make(exp.objective["kind"], **exp.objective.get("params", {}))
        receipt["science"]["objective"] = dict(obj.evaluate(receipt), kind=obj.kind, version=obj.version)
    return receipt


@dataclass
class ExecutionReport:
    experiment_id: str
    receipts_path: str
    n_runs: int
    n_completed: int
    n_failed: int
    controls: Dict[str, dict]
    valid: bool

    def as_dict(self) -> dict:
        return self.__dict__


def execute(job: LocalJob, out_path, registry=None) -> ExecutionReport:
    from prometheus.toolbox.registry import default_registry
    registry = registry or default_registry()
    w = ReceiptWriter(out_path)
    by_key: Dict[str, Dict[Any, dict]] = {}
    n_fail = 0
    try:
        for spec in job.runs:
            try:
                r = run_one(spec, registry, receipt_dir=w.path.parent)
            except Exception as exc:                                    # noqa: BLE001  a failed run is a receipt, never a halt
                n_fail += 1
                r = {"experiment_id": job.experiment_id, "experiment_digest": spec.experiment.digest(), "arm": spec.arm, "sweep_point": spec.sweep_point,
                     "seed": spec.seed, "status": "FAILED", "components": {"world": {"kind": spec.experiment.world["kind"]}, "substrate": {"kind": spec.experiment.substrate["kind"]}},
                     "capabilities": {}, "replay_class": "NOT_RUN", "trace_hashes": [], "events_total": 0, "engineering": {}, "science": {}, "accounting": {},
                     "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]), "started_utc": datetime.now(timezone.utc).isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat()}
            r = w.write(r)
            by_key.setdefault(spec.arm, {})[spec.key()] = r
        controls: Dict[str, dict] = {}
        ctrl_objs = {}
        for c in (job.runs[0].experiment.controls if job.runs else []):
            ctrl_objs[registry.make(c["kind"], **c.get("params", {})).kind] = (c["kind"], registry.make(c["kind"], **c.get("params", {})))
        for arm, (ckind, ctrl) in ctrl_objs.items():
            outcomes = []
            for key, prim in by_key.get("primary", {}).items():
                a = by_key.get(arm, {}).get(key)
                if a is None or a["status"] != "COMPLETED" or prim["status"] != "COMPLETED":
                    outcomes.append({"outcome": "INDETERMINATE", "detail": "run missing or failed"}); continue
                outcomes.append(ctrl.expectation(prim, a))
            met = sum(1 for o in outcomes if o["outcome"] == "MET"); nm = sum(1 for o in outcomes if o["outcome"] == "NOT_MET")
            controls[arm] = {"control": ckind, "pairs": len(outcomes), "met": met, "not_met": nm, "indeterminate": len(outcomes) - met - nm,
                             "outcome": "MET" if outcomes and nm == 0 and met == len(outcomes) else ("NOT_MET" if nm else "INDETERMINATE"),
                             "details": outcomes[:8]}
        summary = {"experiment_id": job.experiment_id, "arm": "SUMMARY", "sweep_point": {}, "seed": -1, "status": "COMPLETED",
                   "experiment_digest": job.runs[0].experiment.digest() if job.runs else "", "components": {"world": {}, "substrate": {}},
                   "capabilities": job.negotiation or {}, "replay_class": "NOT_RUN", "trace_hashes": [], "events_total": 0,
                   "engineering": {"n_runs": len(job.runs), "n_failed": n_fail}, "science": {"controls": controls}, "accounting": {},
                   "registry_rows": job.registry_rows, "started_utc": datetime.now(timezone.utc).isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat()}
        w.write(summary)
    finally:
        w.close()
    valid = n_fail == 0 and all(c["outcome"] == "MET" for c in controls.values())
    return ExecutionReport(job.experiment_id, str(w.path), len(job.runs), len(job.runs) - n_fail, n_fail, controls, valid)
