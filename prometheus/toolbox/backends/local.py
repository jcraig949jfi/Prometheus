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

import json
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
    split: str = "train"       # "train" | "holdout" (C14: seed_policy.holdout_seeds)
    job_id: str = ""           # the JOB's experiment id (C29: every receipt of one job carries one id; the point's digest is experiment_digest)

    def key(self):
        import json
        return (json.dumps(self.sweep_point, sort_keys=True, separators=(",", ":"), default=str), self.seed)   # C8: sweep values may be dicts


@dataclass
class LocalJob:
    experiment_id: str
    runs: List[RunSpec] = field(default_factory=list)
    negotiation: Optional[dict] = None
    registry_rows: List[dict] = field(default_factory=list)
    experiment: Optional[Experiment] = None       # the job's IR (C32: embedded in the SUMMARY receipt)

    def as_dict(self) -> dict:
        arms = sorted({r.arm for r in self.runs}); seeds = sorted({r.seed for r in self.runs})
        points = len({json.dumps(r.sweep_point, sort_keys=True, default=str) for r in self.runs})
        return {"experiment_id": self.experiment_id, "n_runs": len(self.runs), "arms": arms, "negotiation": self.negotiation,
                "eligibility": {"points": points, "arms": len(arms), "seeds": len(seeds), "runs": len(self.runs)}}   # C77: computed before dispatch


def seeds_for(exp: Experiment) -> List[tuple]:
    """-> [(seed, split)]: n_seeds train seeds then holdout_seeds held-out seeds, contiguous from base."""
    sp = exp.seed_policy
    out = [(sp["base"] + i, "train") for i in range(sp["n_seeds"])]
    out += [(sp["base"] + sp["n_seeds"] + i, "holdout") for i in range(int(sp.get("holdout_seeds", 0)))]
    return out


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
    provided |= {"ext.intervention.observation_delay.v1", "ext.intervention.observation_permute.v1", "ext.intervention.schedule.v1"}
    sub = registry.make(exp.substrate["kind"], **exp.substrate.get("params", {}))
    provided |= set(sub.capabilities)
    for i, p in enumerate(exp.players):
        # C34: a player may name its own substrate; its requirements are negotiated against THAT machine
        psub = sub
        if p.get("substrate"):
            if not registry.has(p["substrate"]["kind"]):
                reasons.append("players[%d].substrate %r is not registered" % (i, p["substrate"]["kind"])); continue
            psub = registry.make(p["substrate"]["kind"], **p["substrate"].get("params", {}))
        if p["representation"] not in psub.representations:
            reasons.append("substrate %s cannot instantiate representation %r (players[%d])" % (psub.kind, p["representation"], i))
        unmet = set(p.get("requires", ())) - set(psub.capabilities)
        if unmet:
            reasons.append("players[%d] requires %s which its substrate %s does not offer" % (i, sorted(unmet), psub.kind))
    req = set(exp.derived_requirements()) - {c for p in exp.players if p.get("substrate") for c in p.get("requires", ())}
    neg = C.negotiate(req, provided)
    if not neg.ok:
        return Lowering("local", "BLOCKED_MISSING_CAPABILITY", eid, reasons=["missing: %s" % sorted(neg.missing)] + reasons, negotiation=neg.as_dict())
    if reasons:
        return Lowering("local", "TARGET_UNSUPPORTED", eid, reasons=reasons, negotiation=neg.as_dict())
    controls = [(c["kind"], registry.make(c["kind"], **c.get("params", {}))) for c in exp.controls]
    n_points = len(exp.sweep_points()); n_arms = 1 + len(controls); n_seeds = len(seeds_for(exp)); n_runs = n_points * n_arms * n_seeds
    max_runs = exp.budget.get("max_runs")
    if max_runs is not None and n_runs > int(max_runs):          # C77: the ELIGIBILITY COUNT refuses before any run
        return Lowering("local", "TARGET_UNSUPPORTED", eid, reasons=["%d runs (%d sweep points x %d arms x %d seeds) exceed budget.max_runs=%d" % (n_runs, n_points, n_arms, n_seeds, int(max_runs))], negotiation=neg.as_dict())
    job = LocalJob(eid, negotiation=neg.as_dict(), registry_rows=[registry.get(k).row() for k in sorted(set(exp.component_kinds()))], experiment=exp)
    for point in exp.sweep_points():
        base = exp.at_point(point)
        try:                                                      # C38: a construction error is reported ONCE, here, not per run
            w0 = build_world(base, registry)
        except Exception as exc:                                  # noqa: BLE001
            return Lowering("local", "TARGET_UNSUPPORTED", eid, reasons=["world cannot be constructed at sweep point %s: %s: %s" % (json.dumps(point, sort_keys=True, default=str), type(exc).__name__, str(exc)[:200])], negotiation=neg.as_dict())
        if getattr(w0, "n_players", len(base.players)) != len(base.players):                        # C52/C84: no phantom players, zero allowed when the world says zero
            return Lowering("local", "TARGET_UNSUPPORTED", eid, reasons=["world declares n_players=%d but %d players are given at sweep point %s" % (w0.n_players, len(base.players), json.dumps(point, sort_keys=True, default=str))], negotiation=neg.as_dict())
        arms = [("primary", base)] + [(ctrl.kind, ctrl.arm(base, exp.seed_policy["base"] * 7919 + 1)) for _, ctrl in controls]
        for arm, aexp in arms:
            for s, split in seeds_for(exp):
                job.runs.append(RunSpec(arm, point, s, aexp, split, eid))
    return Lowering("local", "OK", eid, job=job, negotiation=neg.as_dict())


# ---------------------------------------------------------------------------------------------- wrappers
class ObservationWrapper:
    """Kernel-applied observation wrappers, COMPOSED in intervention order (C4, 2026-09-19: a dict keyed by
    wrapper name let a control silently replace the designer's own permutation).
    observation_delay: the delays ADD; observe the state from d ticks ago (the first observation is repeated
    until d are buffered).  observation_permute: one seeded channel permutation per seed, applied in order;
    all seeds are recorded in the manifest."""

    def __init__(self, world, delay: int = 0, permute_seeds: Optional[List[int]] = None):
        self.w = world; self.delay = int(delay); self.permute_seeds = list(permute_seeds or [])
        self._buf: Dict[int, List[List[int]]] = {}
        self._perms: Optional[List[List[int]]] = None
        self.kind = world.kind; self.capabilities = world.capabilities; self.n_players = world.n_players

    def manifest(self) -> dict:
        return dict(self.w.manifest(), wrappers={"observation_delay": self.delay, "observation_permute": list(self.permute_seeds)})

    def reset(self, seed: int, keep: bool = False) -> None:
        (self.w.reset(seed, keep=True) if keep else self.w.reset(seed)); self._buf = {}; self._perms = None

    def _perm(self, seed: int, n: int) -> List[int]:
        s = stream("permute", seed); perm = list(range(n))
        for i in range(n - 1, 0, -1):
            j = s.below(i + 1); perm[i], perm[j] = perm[j], perm[i]
        return perm

    def observe(self, pid: int) -> List[int]:
        obs = self.w.observe(pid)
        if self.permute_seeds:
            if self._perms is None:
                self._perms = [self._perm(sd, len(obs)) for sd in self.permute_seeds]
            for perm in self._perms:
                obs = [obs[i] for i in perm]
        if self.delay:
            buf = self._buf.setdefault(pid, [])
            buf.append(obs)
            if len(buf) > self.delay + 1:
                buf.pop(0)
            obs = buf[0] if len(buf) <= self.delay else buf[-1 - self.delay]
        return obs

    def __getattr__(self, name):
        return getattr(self.w, name)


class ScheduleWrapper:
    """ext.intervention.schedule.v1 (C19): applies world_params changes at tick boundaries (before the step of the
    named tick) through the world's set_params; changes are recorded in the manifest; replay is unaffected."""

    def __init__(self, world, schedule: List[dict]):
        self.w = world; self.schedule = sorted(schedule, key=lambda s: int(s["tick"])); self._i = 0; self._t = 0
        self.kind = world.kind; self.capabilities = world.capabilities; self.n_players = world.n_players

    def manifest(self) -> dict:
        return dict(self.w.manifest(), schedule=self.schedule)

    def reset(self, seed: int, keep: bool = False) -> None:
        (self.w.reset(seed, keep=True) if keep else self.w.reset(seed)); self._i = 0; self._t = 0
        self._apply()

    def _apply(self) -> None:
        # the wrapper keeps its own tick count: it never reads the world's internals
        while self._i < len(self.schedule) and int(self.schedule[self._i]["tick"]) <= self._t:
            self.w.set_params(**self.schedule[self._i]["world_params"]); self._i += 1

    def step(self, actions):
        done = self.w.step(actions)
        self._t += 1
        self._apply()
        return done

    def __getattr__(self, name):
        return getattr(self.w, name)


def _world_params(exp: Experiment, registry, kind: str) -> tuple:
    """-> (params, delay, permutes, schedule): the IR's world params with every intervention's world_params applied,
    plus the kernel-level wrappers the interventions ask for (C92: shared by the scalar and the batch path)."""
    params = dict(exp.world.get("params", {}))
    delay = 0; permutes: List[int] = []; schedule: List[dict] = []
    for iv in exp.interventions:
        params.update(iv.get("world_params", {}))
        wr = iv.get("wrappers", {})
        delay += int(wr.get("observation_delay", 0))
        if "observation_permute" in wr:
            permutes.append(int(wr["observation_permute"]))
        schedule += list(iv.get("schedule") or [])
    if "ext.intervention.world_params.v1" in registry.get(kind).capabilities:
        params.setdefault("horizon", exp.budget["horizon"])     # a world without parameter overrides keeps its own horizon; the loop caps at budget.horizon anyway
    return params, delay, permutes, schedule


def build_world(exp: Experiment, registry):
    params, delay, permutes, schedule = _world_params(exp, registry, exp.world["kind"])
    world = registry.make(exp.world["kind"], **params)
    if schedule:
        world = ScheduleWrapper(world, schedule)
    if delay or permutes:
        world = ObservationWrapper(world, delay, permutes)
    return world


# ---------------------------------------------------------------------------------------------- episode loop
def _loop(world, instances, observers, subs, horizon, ticks, n_events, checkpoint_at=None, record_actions=False, seed=None, episode=0):
    has_events = "ext.events.v1" in world.capabilities
    ev_subs = [so for so in subs if hasattr(so, "events")]
    done = False; acts_log = []; checkpoint = None
    while not done and ticks < horizon:
        if checkpoint_at is not None and ticks == checkpoint_at:
            checkpoint = make_checkpoint(world, instances, observers, subs, ticks, n_events, seed, episode); break
        observations = {pid: world.observe(pid) for pid in instances}
        actions = {pid: instances[pid].act(observations[pid], world.legal_actions(pid)) for pid in instances}
        if record_actions:
            acts_log.append({pid: list(a) for pid, a in actions.items()})
        done = world.step(actions)
        for so in subs:
            if hasattr(so, "tick"):
                so.tick(ticks)
        evs = (world.events() if has_events else [])
        for so in ev_subs:
            evs += so.events()
        n_events += len(evs)
        for ob in observers:
            # ORDER IS A CONTRACT (C1, 2026-09-19): the events of tick t are delivered BEFORE on_tick(t), so a
            # series record for tick t reflects the world AFTER step t (absorptions, yields of that tick included).
            if evs:
                ob.on_events(evs)
            ob.on_tick(ticks, observations, actions)
        ticks += 1
    out = {"trace_hash": world.trace_hash(), "ticks": ticks, "events": n_events, "summary": world.summary() if hasattr(world, "summary") else {},
           "checkpoint": checkpoint}
    if record_actions:
        out["actions"] = acts_log
    return out


def run_episode(world, instances: Dict[int, Any], observers: List[Any], seed: int, horizon: int, substrate=None, episode: int = 0,
                checkpoint_at: Optional[int] = None, record_actions: bool = False, keep_world: bool = False) -> dict:
    if keep_world and episode > 0:
        world.reset(seed, keep=True)                              # ext.world.lifetime_state.v1 (C40)
    else:
        world.reset(seed)
    subs = substrate if isinstance(substrate, list) else ([substrate] if substrate is not None else [])
    for so in subs:
        if hasattr(so, "episode_begin"):
            so.episode_begin(episode, seed)                          # ext.substrate.lifecycle.v1
    for ob in observers:
        ob.begin({"n_players": world.n_players, "seed": seed})
    return _loop(world, instances, observers, subs, horizon, 0, 0, checkpoint_at, record_actions, seed, episode)


# ---------------------------------------------------------------------------------------------- checkpoint (C37)
def make_checkpoint(world, instances, observers, subs, ticks: int, n_events: int, seed, episode) -> dict:
    """A mid-episode checkpoint: world snapshot (ext.snapshot.v1 required), every player instance's snapshot,
    every substrate's device snapshot, the observers' snapshots where they have one, the tick, and the trace
    hash SO FAR. Resuming from it is honest: the resumed trace is PARTIAL and names this hash."""
    if "ext.snapshot.v1" not in world.capabilities:
        raise ValueError("world %s has no ext.snapshot.v1: it cannot be checkpointed mid-episode" % world.kind)
    ck = {"tick": ticks, "n_events": n_events, "seed": seed, "episode": episode, "world": world.snapshot().hex(),
          "instances": {str(pid): inst.snapshot().hex() for pid, inst in instances.items()},
          "substrates": [so.dev.snapshot().hex() if hasattr(so, "dev") else None for so in subs],
          "observers": [ob.snapshot().hex() if hasattr(ob, "snapshot") else None for ob in observers],
          "pre_checkpoint_trace": world.trace_hash()}
    return ck


def resume_episode(checkpoint: dict, world, instances: Dict[int, Any], observers: List[Any], horizon: int, substrate=None, record_actions: bool = False) -> dict:
    """Continue an episode from a checkpoint in FRESH objects (same kinds and params as the originals)."""
    subs = substrate if isinstance(substrate, list) else ([substrate] if substrate is not None else [])
    world.reset(checkpoint["seed"])
    for so in subs:
        if hasattr(so, "episode_begin"):
            so.episode_begin(checkpoint["episode"], checkpoint["seed"])
    for ob in observers:
        ob.begin({"n_players": world.n_players, "seed": checkpoint["seed"]})
    world.restore(bytes.fromhex(checkpoint["world"]))
    for pid, inst in instances.items():
        inst.restore(bytes.fromhex(checkpoint["instances"][str(pid)]))
    for so, snap in zip(subs, checkpoint["substrates"]):
        if snap is not None and hasattr(so, "dev"):
            so.dev.restore(bytes.fromhex(snap))
    for ob, snap in zip(observers, checkpoint["observers"]):
        if snap is not None and hasattr(ob, "restore"):
            ob.restore(bytes.fromhex(snap))
    out = _loop(world, instances, observers, subs, horizon, checkpoint["tick"], checkpoint["n_events"], None, record_actions, checkpoint["seed"], checkpoint["episode"])
    out.update({"replay_class": "PARTIAL", "checkpoint_tick": checkpoint["tick"], "pre_checkpoint_trace": checkpoint["pre_checkpoint_trace"]})
    return out


SCALAR_EXECUTION = {"batched": False, "batch_size": 1, "reason": "BATCH_NOT_REQUESTED"}


def _prepare(spec: RunSpec, registry, world=None) -> dict:
    """Everything a run builds before its first tick (C92: one function for the scalar and the batch path so the
    two cannot drift): world (unless a shared batch world is handed in), substrates (per player, C34), fresh player
    instances with their fingerprints, observers keyed by kind (C48), series collectors."""
    exp = spec.experiment
    started = datetime.now(timezone.utc).isoformat(); t0 = time.perf_counter(); c0 = time.process_time()
    world = build_world(exp, registry) if world is None else world
    sub = registry.make(exp.substrate["kind"], **exp.substrate.get("params", {}))
    specs = [PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {})) for p in exp.players]
    subs_by_pid: Dict[int, Any] = {}; sub_objs: Dict[str, Any] = {json.dumps(exp.substrate, sort_keys=True): sub}
    for pid, p in enumerate(exp.players):
        if p.get("substrate"):
            k = json.dumps(p["substrate"], sort_keys=True)
            if k not in sub_objs:
                sub_objs[k] = registry.make(p["substrate"]["kind"], **p["substrate"].get("params", {}))
            subs_by_pid[pid] = sub_objs[k]
        else:
            subs_by_pid[pid] = sub
    instances = {pid: subs_by_pid[pid].instantiate(ps, spec.seed * 31 + pid) for pid, ps in enumerate(specs)}
    all_subs = list(sub_objs.values())
    from prometheus.toolbox.ref.players import probe_silent
    # C96: "hash" is a BEHAVIOURAL CLASS (the probe's 16 observations; distinct machines collide on it); "spec_hash" is the
    # player's identity (its manifest). Both on the FRESH instance.
    fingerprints = {str(pid): {"hash": inst.fingerprint(), "silent": probe_silent(inst), "spec_hash": component_manifest_hash(specs[pid].manifest())}
                    for pid, inst in instances.items()}
    observers = [registry.make(o["kind"], **o.get("params", {})) for o in exp.observers]
    seen_kinds: Dict[str, int] = {}; obs_keys: List[str] = []
    for i, ob in enumerate(observers):
        obs_keys.append(ob.kind if ob.kind not in seen_kinds else "%s#%d" % (ob.kind, i)); seen_kinds[ob.kind] = i
    series_obs = [(k, ob) for k, ob in zip(obs_keys, observers) if getattr(ob, "series", False)]
    return {"spec": spec, "exp": exp, "started": started, "t0": t0, "c0": c0, "world": world, "sub": sub, "specs": specs, "subs_by_pid": subs_by_pid,
            "instances": instances, "all_subs": all_subs, "fingerprints": fingerprints, "observers": observers, "obs_keys": obs_keys,
            "series_obs": series_obs, "collected": {k: [] for k, _ in series_obs},
            "hashes": [], "ticks_total": 0, "events_total": 0, "summaries": []}


def _finish(ctx: dict, registry, receipt_dir, world_manifest: dict, world_accounting: Dict[str, int], replay_class: str, execution: dict) -> dict:
    """The receipt of a prepared and stepped run."""
    import pathlib
    receipt_dir = pathlib.Path(receipt_dir) if receipt_dir is not None else pathlib.Path(".")
    spec = ctx["spec"]; exp = ctx["exp"]; sub = ctx["sub"]; all_subs = ctx["all_subs"]; observers = ctx["observers"]; obs_keys = ctx["obs_keys"]
    wall = time.perf_counter() - ctx["t0"]; cpu = time.process_time() - ctx["c0"]
    acc = {}
    for so in all_subs:
        for k, v in so.accounting().items():
            acc[k] = acc.get(k, 0) + int(v)
    if len(all_subs) > 1:
        acc["by_substrate"] = {so.kind: so.accounting() for so in all_subs}
    acc.update(world_accounting)
    acc["wall_s"] = round(wall, 6); acc["cpu_s"] = round(cpu, 6)
    summaries = ctx["summaries"]; ticks_total = ctx["ticks_total"]
    science = {"observations": {k: ob.measure() for k, ob in zip(obs_keys, observers)}, "world_summary": summaries[-1] if summaries else {},
               "player_fingerprints": ctx["fingerprints"]}
    for so in all_subs:
        if hasattr(so, "science"):
            science.setdefault("substrate", {}).update(so.science() if len(all_subs) == 1 else {so.kind: so.science()})
    receipt = {
        "experiment_id": spec.job_id or exp.experiment_id(),
        "experiment_digest": exp.digest(), "arm": spec.arm, "sweep_point": spec.sweep_point, "seed": spec.seed, "split": spec.split, "status": "COMPLETED",
        "components": {"world": {"kind": world_manifest["kind"], "manifest_hash": component_manifest_hash(world_manifest),
                                 "manifest": dict(world_manifest, world_state=exp.budget.get("world_state", "episode"))},
                       "substrate": {"kind": sub.kind, "manifest_hash": component_manifest_hash(sub.manifest())},
                       "player_substrates": [ctx["subs_by_pid"][pid].kind for pid in range(len(ctx["specs"]))],
                       "players": [{"representation": p.representation, "manifest_hash": component_manifest_hash(p.manifest()), "meta": p.meta} for p in ctx["specs"]],
                       "observers": [ob.manifest() for ob in observers],
                       "interventions": exp.interventions},
        # capabilities.world names what the IR ASKED for and negotiated against; execution.world names what stepped (C92)
        "capabilities": {"required": sorted(exp.derived_requirements()), "world": sorted(registry.get(exp.world["kind"]).capabilities), "substrate": sorted(sub.capabilities)},
        "replay_class": replay_class, "trace_hashes": ctx["hashes"], "events_total": ctx["events_total"],
        # a batched run's wall clock is the BATCH's (shared by its envs): the per-run rate is unknowable and is written as
        # None; the batch-level rate is filled in by run_batch (C92: never a divided-up fiction)
        "engineering": {"wall_s": acc["wall_s"], "cpu_s": acc["cpu_s"], "ticks": ticks_total,
                        "steps_per_s": (round(ticks_total / wall, 1) if wall > 0 else None) if not execution.get("batched") else None},
        "execution": dict(execution),
        "science": science, "accounting": acc, "provenance": exp.provenance,
        "started_utc": ctx["started"], "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    if ctx["series_obs"]:
        receipt["series"] = {k: SER.build(ctx["collected"][k], enabled=getattr(ob, "enabled", True), replay_class=replay_class,
                                          max_records=exp.budget.get("series_max_records"), max_inline=SER.DEFAULT_MAX_INLINE,
                                          receipt_dir=receipt_dir, columns=(ob.series_columns() if hasattr(ob, "series_columns") else None)) for k, ob in ctx["series_obs"]}
    if exp.objective:
        obj = registry.make(exp.objective["kind"], **exp.objective.get("params", {}))
        # an objective may read the SERIES (C13): the recovered episodes are handed over on a transient key that
        # never reaches the written receipt (the receipt keeps the series itself, inline or by artifact)
        receipt["_series_episodes"] = SER.recover(receipt, receipt_dir) if ctx["series_obs"] else {}
        receipt["science"]["objective"] = dict(obj.evaluate(receipt), kind=obj.kind, version=obj.version)
        del receipt["_series_episodes"]
    return receipt


def run_one(spec: RunSpec, registry, receipt_dir=None, execution: Optional[dict] = None) -> dict:
    ctx = _prepare(spec, registry); exp = spec.experiment; world = ctx["world"]
    for ep in range(exp.budget["episodes"]):
        r = run_episode(world, ctx["instances"], ctx["observers"], spec.seed * 1000 + ep, exp.budget["horizon"],
                        substrate=ctx["all_subs"] if len(ctx["all_subs"]) > 1 else ctx["sub"], episode=ep, keep_world=exp.budget.get("world_state") == "lifetime")
        ctx["hashes"].append(r["trace_hash"]); ctx["ticks_total"] += r["ticks"]; ctx["events_total"] += r["events"]; ctx["summaries"].append(r["summary"])
        for k, ob in ctx["series_obs"]:
            ctx["collected"][k].append(ob.series_episode())
    return _finish(ctx, registry, receipt_dir, world.manifest(), world.accounting() if hasattr(world, "accounting") else {"world_steps": ctx["ticks_total"]},
                   getattr(world, "replay_class", "NONDETERMINISTIC"), execution or SCALAR_EXECUTION)


def batch_plan(exp: Experiment, registry) -> tuple:
    """-> (batch_kind or None, reason): whether this experiment's runs may be grouped behind one ext.batch.v1 world."""
    n = int(exp.budget.get("batch") or 0)
    if n < 2:
        return None, "BATCH_NOT_REQUESTED"
    _, delay, permutes, schedule = _world_params(exp, registry, exp.world["kind"])
    if delay or permutes or schedule:
        return None, "WRAPPERS_NOT_BATCHED"                    # kernel wrappers are per-world objects; the batch face has no wrapper yet
    bk = registry.batch_implementation(exp.world["kind"])
    if bk is None:
        return None, "NO_BATCH_IMPLEMENTATION"
    return bk, "BATCHED"


def _failed_receipt(spec: RunSpec, exc: BaseException, execution: dict, job_id=None) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {"experiment_id": job_id or spec.job_id or spec.experiment.experiment_id(), "experiment_digest": spec.experiment.digest(), "arm": spec.arm,
            "sweep_point": spec.sweep_point, "seed": spec.seed, "split": spec.split, "status": "FAILED",
            "components": {"world": {"kind": spec.experiment.world["kind"]}, "substrate": {"kind": spec.experiment.substrate["kind"]}},
            "capabilities": {}, "replay_class": "NOT_RUN", "trace_hashes": [], "events_total": 0, "engineering": {}, "execution": dict(execution), "science": {}, "accounting": {},
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]), "started_utc": now, "finished_utc": now}


def run_batch(specs: List[RunSpec], registry, batch_kind: str, receipt_dir=None) -> List[dict]:
    """C92: the runs of `specs` (same arm, sweep point and experiment; different seeds) stepped in lockstep behind one
    ext.batch.v1 world. Same semantics as run_one, env by env: reset -> [observe all -> act all -> step -> drain
    events -> observers] x horizon or done, per episode. A failing env is a FAILED receipt and is abandoned
    (actions None), never a halt of the batch; a failure shared by every env (world construction) fails them all."""
    exp = specs[0].experiment; n = len(specs)
    execution = {"batched": True, "batch_size": n, "reason": "BATCHED", "world": batch_kind, "requested_world": exp.world["kind"]}
    params, _, _, _ = _world_params(exp, registry, batch_kind)
    try:
        world = registry.make(batch_kind, n_envs=n, **params)
    except Exception as exc:                                                    # noqa: BLE001
        return [_failed_receipt(sp, exc, execution) for sp in specs]
    ctxs: List[Any] = []; errors: Dict[int, BaseException] = {}
    for i, sp in enumerate(specs):
        try:
            ctxs.append(_prepare(sp, registry, world=world))
        except Exception as exc:                                                # noqa: BLE001
            ctxs.append(None); errors[i] = exc
    live = [c is not None for c in ctxs]
    has_events = "ext.events.v1" in world.capabilities
    horizon = exp.budget["horizon"]; keep = exp.budget.get("world_state") == "lifetime"
    ticks_by_env = [0] * n; events_by_env = [0] * n
    for ep in range(exp.budget["episodes"]):
        seeds = [sp.seed * 1000 + ep for sp in specs]
        world.reset_batch(seeds, keep=keep and ep > 0)
        for i, c in enumerate(ctxs):
            if not live[i]:
                continue
            try:
                for so in c["all_subs"]:
                    if hasattr(so, "episode_begin"):
                        so.episode_begin(ep, seeds[i])
                for ob in c["observers"]:
                    ob.begin({"n_players": world.n_players, "seed": seeds[i]})
            except Exception as exc:                                            # noqa: BLE001
                live[i] = False; errors[i] = exc
        done = [not live[i] for i in range(n)]; ticks = 0; ep_ticks = [0] * n; ep_events = [0] * n
        while ticks < horizon and not all(done):
            obs_by_pid = {pid: world.observe_batch(pid) for pid in range(world.n_players)}
            acts: List[Any] = [None] * n; obs_env: List[Any] = [None] * n
            for i, c in enumerate(ctxs):
                if done[i]:
                    continue
                try:
                    observations = {pid: obs_by_pid[pid][i] for pid in c["instances"]}
                    acts[i] = {pid: c["instances"][pid].act(observations[pid], world.legal_actions(pid)) for pid in c["instances"]}
                    obs_env[i] = observations
                except Exception as exc:                                        # noqa: BLE001
                    live[i] = False; done[i] = True; errors[i] = exc; acts[i] = None
            step_done = world.step_batch(acts)
            evs_all = world.events_batch() if has_events else [[] for _ in range(n)]
            for i, c in enumerate(ctxs):
                if done[i]:
                    continue
                try:
                    evs = list(evs_all[i])
                    for so in c["all_subs"]:
                        if hasattr(so, "tick"):
                            so.tick(ticks)
                        if hasattr(so, "events"):
                            evs += so.events()
                    ep_events[i] += len(evs)
                    for ob in c["observers"]:
                        if evs:
                            ob.on_events(evs)                                   # same ORDER contract as _loop (C1)
                        ob.on_tick(ticks, obs_env[i], acts[i])
                except Exception as exc:                                        # noqa: BLE001
                    live[i] = False; done[i] = True; errors[i] = exc; continue
                ep_ticks[i] += 1
                if step_done[i]:
                    done[i] = True
            ticks += 1
        hashes = world.trace_hashes(); sums = world.summaries()
        for i, c in enumerate(ctxs):
            if not live[i]:
                continue
            c["hashes"].append(hashes[i]); c["ticks_total"] += ep_ticks[i]; c["events_total"] += ep_events[i]; c["summaries"].append(sums[i])
            for k, ob in c["series_obs"]:
                c["collected"][k].append(ob.series_episode())
    out = []
    wacc = world.accounting_batch() if hasattr(world, "accounting_batch") else [{"world_steps": c["ticks_total"] if c else 0} for c in ctxs]
    for i, (sp, c) in enumerate(zip(specs, ctxs)):
        if not live[i]:
            out.append(_failed_receipt(sp, errors[i], execution)); continue
        try:
            out.append(_finish(c, registry, receipt_dir, world.manifest(), wacc[i], getattr(world, "replay_class", "NONDETERMINISTIC"), execution))
        except Exception as exc:                                                # noqa: BLE001
            out.append(_failed_receipt(sp, exc, execution))
    batch_wall = max((r["engineering"].get("wall_s", 0) for r in out if r["status"] == "COMPLETED"), default=0.0)
    batch_ticks = sum(r["engineering"].get("ticks", 0) for r in out if r["status"] == "COMPLETED")
    for r in out:
        if r["status"] == "COMPLETED":
            r["engineering"]["batch"] = {"size": n, "wall_s": batch_wall, "ticks_total": batch_ticks, "steps_per_s": round(batch_ticks / batch_wall, 1) if batch_wall > 0 else None}
    return out


def objective_shape(v) -> str:
    """scalar | vector (dict of numbers/None) | none | UNSUPPORTED (C94: the kernel assumes no singular reward)."""
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "UNSUPPORTED"
    if isinstance(v, (int, float)):
        return "scalar"
    if isinstance(v, dict) and v and all(isinstance(k, str) and (x is None or (isinstance(x, (int, float)) and not isinstance(x, bool))) for k, x in v.items()):
        return "vector"
    return "UNSUPPORTED"


def summarise_objectives(values: list) -> dict:
    """-> objective_shape, objective_n, objective_mean (number | {component: mean|None} | None), objective_unsupported.
    Mixed shapes are reported as MIXED with the counts; nothing is averaged across shapes."""
    shapes = [objective_shape(v) for v in values]
    counts = {s: shapes.count(s) for s in sorted(set(shapes))}
    present = {s for s in counts if s != "none"}
    out = {"objective_n": 0, "objective_mean": None, "objective_unsupported": counts.get("UNSUPPORTED", 0), "objective_shape_counts": counts}
    if not present:
        out["objective_shape"] = "none"; return out
    if len(present) > 1:
        out["objective_shape"] = "MIXED"; return out
    shape = present.pop(); out["objective_shape"] = shape
    if shape == "scalar":
        vals = [v for v in values if objective_shape(v) == "scalar"]
        out["objective_n"] = len(vals); out["objective_mean"] = sum(vals) / len(vals)
    elif shape == "vector":
        vals = [v for v in values if objective_shape(v) == "vector"]
        keys = sorted(set().union(*(set(v) for v in vals)))
        out["objective_n"] = len(vals)
        out["objective_mean"] = {k: (sum(v[k] for v in vals if v.get(k) is not None) / sum(1 for v in vals if v.get(k) is not None)) if any(v.get(k) is not None for v in vals) else None for k in keys}
        out["objective_component_n"] = {k: sum(1 for v in vals if v.get(k) is not None) for k in keys}
    return out


@dataclass
class ExecutionReport:
    experiment_id: str
    receipts_path: str
    n_runs: int
    n_completed: int
    n_failed: int
    controls: Dict[str, dict]
    valid: bool
    resumed_runs: int = 0
    runs_not_started: int = 0      # C68: stopped by budget.wall_s; resume=True finishes them

    def as_dict(self) -> dict:
        return self.__dict__


def execute(job: LocalJob, out_path, registry=None, append: bool = False, resume: bool = False) -> ExecutionReport:
    """One receipts file is ONE execution (C22): an existing non-empty file is refused unless append=True
    (a second execution added on purpose) or resume=True (C29: the SAME job continuing -- runs already on
    disk for this experiment, keyed by (arm, sweep_point, seed), are kept and skipped; a partial last line
    is a defect the forensic scan reports, and that run is redone)."""
    import pathlib
    from prometheus.toolbox.registry import default_registry
    from prometheus.toolbox.receipt import scan
    registry = registry or default_registry()
    op = pathlib.Path(out_path)
    done: Dict[str, Dict[Any, dict]] = {}
    if op.exists() and op.stat().st_size > 0:
        if resume:
            prior_ids = set()
            for r in _valid_receipts(op):
                prior_ids.add(r["experiment_id"])
                if r["experiment_id"] == job.experiment_id and r["arm"] != "SUMMARY":
                    done.setdefault(r["arm"], {})[(json.dumps(r["sweep_point"], sort_keys=True, separators=(",", ":"), default=str), r["seed"])] = r
            if prior_ids and job.experiment_id not in prior_ids:          # C79: a resume names the SAME experiment or is refused
                raise ValueError("%s holds receipts of %s, not of %s; resume=True must name the same experiment (use append=True to add another on purpose)"
                                 % (op, sorted(prior_ids), job.experiment_id))
        elif not append:
            raise FileExistsError("%s already holds receipts; pass append=True (second execution) or resume=True (continue this job)" % op)
    w = ReceiptWriter(out_path)
    by_key: Dict[str, Dict[Any, dict]] = {}
    n_fail = 0; n_resumed = 0; not_started = 0; stopped_reason = None
    wall_budget = (job.experiment.budget.get("wall_s") if job.experiment is not None else None)
    t_start = time.perf_counter()
    try:
        plans: Dict[str, tuple] = {}
        pending: List[RunSpec] = []          # C92: consecutive same-group runs waiting for a batch

        def group_of(sp: RunSpec):
            return (sp.arm, json.dumps(sp.sweep_point, sort_keys=True, separators=(",", ":"), default=str), sp.experiment.digest())

        def flush():
            nonlocal n_fail
            if not pending:
                return
            bk = plans[pending[0].experiment.digest()][0]
            try:
                rs = run_batch(list(pending), registry, bk, receipt_dir=w.path.parent)
            except Exception as exc:                                    # noqa: BLE001  a failed batch is n FAILED receipts, never a halt
                rs = [_failed_receipt(sp, exc, {"batched": True, "batch_size": len(pending), "reason": "BATCHED", "world": bk}, job.experiment_id) for sp in pending]
            for sp, r in zip(pending, rs):
                r["experiment_id"] = job.experiment_id
                if r["status"] == "FAILED":
                    n_fail += 1
                by_key.setdefault(sp.arm, {})[sp.key()] = w.write(r)
            pending.clear()

        for spec in job.runs:
            if stopped_reason is not None:
                not_started += 1; continue
            if wall_budget is not None and (time.perf_counter() - t_start) > float(wall_budget) and (by_key or pending):
                flush(); stopped_reason = "WALL_BUDGET_EXHAUSTED"; not_started += 1; continue          # C68: stop BETWEEN runs, never mid-run
            prior = done.get(spec.arm, {}).get(spec.key())
            if prior is not None:
                flush()
                by_key.setdefault(spec.arm, {})[spec.key()] = prior; n_resumed += 1
                if prior["status"] == "FAILED":
                    n_fail += 1
                continue
            dg = spec.experiment.digest()
            if dg not in plans:
                plans[dg] = batch_plan(spec.experiment, registry)
            bk, reason = plans[dg]
            if bk is not None:
                if pending and (group_of(pending[0]) != group_of(spec) or len(pending) >= int(spec.experiment.budget["batch"])):
                    flush()
                pending.append(spec); continue
            flush()
            try:
                r = run_one(spec, registry, receipt_dir=w.path.parent, execution={"batched": False, "batch_size": 1, "reason": reason})
            except Exception as exc:                                    # noqa: BLE001  a failed run is a receipt, never a halt
                n_fail += 1
                r = _failed_receipt(spec, exc, {"batched": False, "batch_size": 1, "reason": reason}, job.experiment_id)
            r = w.write(r)
            by_key.setdefault(spec.arm, {})[spec.key()] = r
        flush()
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
        splits: Dict[str, dict] = {}
        for r in by_key.get("primary", {}).values():
            sp = splits.setdefault(r.get("split", "train"), {"n": 0, "objective_values": []})
            sp["n"] += 1
            if r["status"] == "COMPLETED":
                sp["objective_values"].append((r.get("science", {}).get("objective") or {}).get("value"))
        for sp in splits.values():
            sp.update(summarise_objectives(sp.pop("objective_values")))          # C94: shape-aware, never a silent drop
        summary = {"experiment_id": job.experiment_id, "arm": "SUMMARY", "sweep_point": {}, "seed": -1, "status": "COMPLETED",
                   "experiment_digest": job.runs[0].experiment.digest() if job.runs else "", "components": {"world": {}, "substrate": {}},
                   "capabilities": job.negotiation or {}, "replay_class": "NOT_RUN", "trace_hashes": [], "events_total": 0,
                   "engineering": {"n_runs": len(job.runs), "n_failed": n_fail, "runs_not_started": not_started, "stopped_reason": stopped_reason,
                                   "wall_s": round(time.perf_counter() - t_start, 3), "wall_budget_s": wall_budget},
                   "science": {"controls": controls, "splits": splits}, "accounting": {},
                   "experiment": job.experiment.to_dict() if job.experiment is not None else None,      # C32: the receipts file alone can be replayed
                   "registry_rows": job.registry_rows, "started_utc": datetime.now(timezone.utc).isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat()}
        w.write(summary)
    finally:
        w.close()
    valid = n_fail == 0 and not_started == 0 and all(c["outcome"] == "MET" for c in controls.values())
    return ExecutionReport(job.experiment_id, str(w.path), len(job.runs), len(job.runs) - n_fail - not_started, n_fail, controls, valid, n_resumed, not_started)


def _valid_receipts(path) -> List[dict]:
    """Receipts a resume may trust: valid lines only (a truncated tail is skipped, not trusted)."""
    from prometheus.toolbox.receipt import validate, ReceiptError
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(validate(json.loads(line)))
            except (ValueError, ReceiptError):
                continue
    return out


# ---------------------------------------------------------------------------------------------- replay (C32)
def replay_file(receipts_path, out_path, registry=None) -> dict:
    """Re-execute the IR embedded in a receipts file's SUMMARY and compare every run's scientific record
    (trace hashes, series hashes, objective value) with the recorded one. Divergences are DATA; a kernel hash
    difference is information beside them. Raises only if the file has no replayable summary."""
    from prometheus.toolbox.registry import default_registry
    from prometheus.toolbox.receipt import read_all
    registry = registry or default_registry()
    old = read_all(receipts_path)
    summ = [r for r in old if r["arm"] == "SUMMARY" and r.get("experiment")]
    if not summ:
        raise ValueError("%s has no SUMMARY receipt carrying an experiment; nothing to replay" % receipts_path)
    exp = Experiment.from_dict(summ[-1]["experiment"])
    low = lower(exp, registry)
    if not low.ok:
        return {"status": low.status, "reasons": low.reasons, "runs_compared": 0, "divergent": [], "kernel_hash_equal": None}
    rep = execute(low.job, out_path, registry)
    new = read_all(out_path)
    key = lambda r: (r["arm"], json.dumps(r["sweep_point"], sort_keys=True, separators=(",", ":"), default=str), r["seed"])
    old_by = {key(r): r for r in old if r["arm"] != "SUMMARY"}; new_by = {key(r): r for r in new if r["arm"] != "SUMMARY"}
    divergent = []; compared = 0
    for k, o in old_by.items():
        n = new_by.get(k)
        if n is None:
            divergent.append({"key": k, "field": "missing_in_replay"}); continue
        compared += 1
        for field_name, get in (("trace_hashes", lambda r: r["trace_hashes"]),
                                ("series_hashes", lambda r: {kk: v["series_hash"] for kk, v in (r.get("series") or {}).items()}),
                                ("objective", lambda r: (r["science"].get("objective") or {}).get("value"))):
            if get(o) != get(n):
                divergent.append({"key": k, "field": field_name, "recorded": get(o), "replayed": get(n)}); break
    return {"status": "OK", "runs_compared": compared, "divergent": divergent, "replay_path": str(out_path),
            "kernel_hash_equal": summ[-1]["build"]["kernel_hash"] == new[-1]["build"]["kernel_hash"],
            "recorded_kernel_hash": summ[-1]["build"]["kernel_hash"], "replay_kernel_hash": new[-1]["build"]["kernel_hash"]}
