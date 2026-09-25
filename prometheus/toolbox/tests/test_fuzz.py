"""Fuzzed compositions (overnight C11) and unexpected events (C17). Seeded, deterministic, cheap: ~40 random
Experiments assembled from the registry must each either compile to a Lowering or be refused as data, and
execute() must never raise -- a FAILED receipt is the worst permitted outcome. Every failure is printed with
its seed so the smallest reproducer can be frozen."""
from __future__ import annotations

import json
import random

import pytest

from prometheus.toolbox.ir import Experiment, IRError, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, lower, run_episode
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, random_statemachine_v3, constant_player, random_proteus_player, proteus_available, random_rewrite_system
from prometheus.toolbox.ref.worlds import IntegerWorld
from prometheus.toolbox.contracts import EVENT_KINDS

REG = default_registry()


def random_experiment(seed: int) -> Experiment:
    rnd = random.Random(seed)
    n_players = rnd.choice([1, 1, 2, 3])
    reps = ["sm1", "sm2", "sm3", "const", "rewrite"] + (["proteus"] if proteus_available() else [])
    players = []
    for i in range(n_players):
        r = rnd.choice(reps)
        m = {"sm1": lambda: random_statemachine(rnd.randrange(10**6), rnd.choice([2, 4, 6]), rnd.choice([4, 8, 16]), rnd.choice([1, 2, 3])),
             "sm2": lambda: random_statemachine_v2(rnd.randrange(10**6), rnd.choice([2, 4]), rnd.choice([4, 8]), rnd.choice([1, 2])),
             "sm3": lambda: random_statemachine_v3(rnd.randrange(10**6), rnd.choice([2, 4]), rnd.choice([4, 8]), rnd.choice([1, 2]), 8, rnd.choice([1, 16])),
             "const": lambda: constant_player([rnd.randrange(8) for _ in range(rnd.choice([1, 2, 3]))]),
             "rewrite": lambda: random_rewrite_system(rnd.randrange(10**6), rnd.choice([1, 4, 8]), rnd.choice([2, 8]), rnd.choice([2, 6, 12])),
             "proteus": lambda: random_proteus_player(rnd.randrange(10**6))}[r]().manifest()
        if rnd.random() < 0.25:                                                        # C34: per-player substrate override
            m = dict(m, substrate=rnd.choice([ref("substrate.flat.v1"), ref("substrate.kv.v1", scope="lifetime", ttl=rnd.choice([None, 2])), ref("substrate.stream.v1", lag=rnd.choice([1, 3]))]))
        players.append(m)
    wrapped = rnd.random()
    if wrapped < 0.06 and REG.get("world.wforge.encounter.v0").state != "UNAVAILABLE":   # C140: the WRAPPED engines too, when importable
        n_players = REG.make("world.wforge.encounter.v0").n_players; players = players[:n_players] + [players[0]] * (n_players - len(players))
        world = ref("world.wforge.encounter.v0", genome_seed=rnd.randrange(50))
    elif wrapped < 0.12 and REG.get("world.c6.composed.v1").state != "UNAVAILABLE":
        players = players[:1]; world = ref("world.c6.composed.v1", seed=rnd.randrange(50), ticks=rnd.choice([8, 24]))
    elif rnd.random() < 0.15:                                                          # C63: the SEMANTIC pendulum too
        world = ref("world.pendulum.v1", n_players=n_players, quantum=rnd.choice([1e-6, 1e-3]), start_charge=rnd.choice([2, 30, 1000]), step_cost=rnd.choice([0, 1]), world_seed=rnd.randrange(100))
    elif rnd.random() < 0.3:                                                           # C42: the grid world too
        world = ref("world.grid.v1", n_nodes=rnd.choice([2, 5, 9]), n_players=n_players, act_range=rnd.choice([3, 8]), start_charge=rnd.choice([1, 20, 1000]),
                    step_cost=rnd.choice([0, 1]), regen_every=rnd.choice([0, 1, 4]), pool_max=rnd.choice([0, 3]), world_seed=rnd.randrange(1000),
                    obs_mode=rnd.choice(["flat", "structured"]))                                       # C100
    else:
        world = ref("world.integer.v1", n_regs=rnd.choice([3, 6, 9]), n_players=n_players, act_width=rnd.choice([1, 2, 3]), act_range=rnd.choice([2, 8, 16]),
                    n_ops=rnd.choice([0, 2, 5]), regime_period=rnd.choice([0, 0, 3, 7]), stoch_rate=rnd.choice([0, 0, 2, 9]), action_delay=rnd.choice([0, 1, 4]),
                    world_seed=rnd.randrange(1000), start_charge=rnd.choice([1, 8, 64, 100000]), step_cost=rnd.choice([0, 1, 5]), yield_amt=rnd.choice([0, 4, 40]),
                    obs_regs=rnd.choice([1, 4, 9]))
    substrate = rnd.choice([ref("substrate.flat.v1"), ref("substrate.kv.v1", scope=rnd.choice(["episode", "lifetime", "persistent"]), ttl=rnd.choice([None, 1, 3]), max_keys=rnd.choice([0, 1, 100])),
                            ref("substrate.stream.v1", scope=rnd.choice(["episode", "lifetime"]), lag=rnd.choice([1, 2, 9]), maxlen=rnd.choice([1, 8])),
                            ref("substrate.mailbox.v1", scope=rnd.choice(["episode", "lifetime"]), capacity=rnd.choice([1, 4, 32])),
                            ref("substrate.artifact.v1", scope=rnd.choice(["episode", "lifetime"]), ttl=rnd.choice([None, 2]), max_keys=rnd.choice([0, 2, 100]))])
    interventions = []
    for _ in range(rnd.choice([0, 1, 2, 3])):
        iv = {"name": "iv", "world_params": rnd.choice([{}, {"step_cost": rnd.choice([0, 2])}]),
              "wrappers": rnd.choice([{}, {"observation_delay": rnd.choice([0, 1, 5, 40])}, {"observation_permute": rnd.randrange(100)}])}
        if rnd.random() < 0.3:                                                         # C19: schedules, sometimes with a non-mutable param
            iv["schedule"] = [{"tick": rnd.randrange(0, 8), "world_params": rnd.choice([{"step_cost": rnd.randrange(0, 4)}, {"n_regs": 3}])}]
        interventions.append(iv)
    controls = rnd.sample(["control.replay.v1", "control.cheat.v1", "control.negative.v1", "control.positive.v1", "control.sham.v1", "control.scratch.v1", "control.permutation.v1", "control.ablation.v1"], rnd.choice([0, 1, 3]))
    observers = rnd.sample(["observer.trace.v1", "observer.descriptor.v1", "observer.series.v1"], rnd.choice([0, 1, 3]))
    per_player = rnd.random() < 0.4                                                   # C109: per-player series layout too
    sweep = rnd.choice([{}, {"world.params.world_seed": [1, 2]}, {"budget.horizon": [0, 3]}, {"interventions.0.wrappers.observation_delay": [0, 2]} if interventions else {},
                        {"players": [players, players[:1]]}, {"substrate": [ref("substrate.flat.v1"), ref("substrate.kv.v1")]}])
    budget = {"episodes": rnd.choice([1, 2, 4]), "horizon": rnd.choice([0, 1, 5, 30])}
    if rnd.random() < 0.3:
        budget["world_state"] = "lifetime"
    objective = rnd.choice([None, ref("objective.yield_net.v1", penalties={"ops": 0.1}), ref("objective.survival.v1"), ref("objective.series_gain.v1"),
                            ref("objective.survival.v2"), ref("objective.multi.v1", components={"a": ref("objective.yield_net.v1"), "b": ref("objective.series_gain.v1")})])   # C109
    seed_policy = {"base": rnd.randrange(10**4), "n_seeds": rnd.choice([1, 2])}
    if rnd.random() < 0.3:
        seed_policy["holdout_seeds"] = rnd.choice([0, 1, 2])
    if rnd.random() < 0.3:
        budget["series_max_records"] = rnd.choice([0, 1, 10])
    # adversarial knobs: each must end in a clean refusal (BLOCKED / TARGET_UNSUPPORTED / IRError), never a crash
    if rnd.random() < 0.15:
        players[0] = dict(players[0], requires=["ext.workspace.graph.v1"])          # nobody grants this
    if rnd.random() < 0.15:
        interventions.append({"name": "alien", "world_params": {}, "wrappers": {"observation_foo": 1}})
    if rnd.random() < 0.1:
        sweep = {"players": [[players[0]], players]}                                # not a sweepable root (yet)
    if rnd.random() < 0.1:
        budget["horizon"] = -1
    return Experiment(family="fuzz%d" % seed, world=world, substrate=substrate, players=players, interventions=interventions,
                      objective=objective, observers=[ref(o, per_player=True) if (o == "observer.series.v1" and per_player) else ref(o) for o in observers], controls=[ref(c) for c in controls], sweep=sweep,
                      seed_policy=seed_policy, budget=budget)


@pytest.mark.parametrize("seed", list(range(40)))
def test_random_composition_lowers_or_refuses_and_never_raises(tmp_path, seed):
    e = random_experiment(seed)
    defects = e.validate()
    if defects:
        with pytest.raises(IRError):
            e.compile("local", REG)
        return
    low = e.compile("local", REG)
    assert low.status in ("OK", "TARGET_UNSUPPORTED", "BLOCKED_MISSING_CAPABILITY"), low.as_dict()
    if not low.ok:
        assert low.reasons, "a refusal must carry its reason"
        return
    rep = execute(low.job, tmp_path / "f.jsonl", REG)
    rs = read_all(tmp_path / "f.jsonl")
    failed = [r for r in rs if r["status"] == "FAILED"]
    # the ONLY permitted failure is a schedule naming a non-mutable param (a designer error the kernel reports per run)
    assert all("not runtime-mutable" in (r.get("error") or "") for r in failed), "seed %d: %s" % (seed, [(r["arm"], r.get("error")) for r in failed][:3])
    assert len(rs) == rep.n_runs + 1


# C17: a world may emit event kinds the kernel has not catalogued. Observers must RETAIN them (as UNKNOWN_<id>),
# never crash on them and never normalise them away (directive s2 "unexpected events retained").
class NoisyWorld(IntegerWorld):
    kind = "world.noisy.v1"

    def step(self, actions):
        done = super().step(actions)
        self._events.append((self._state["tick"] - 1, 99, 0, 7, 3))       # an uncatalogued kind
        return done


def test_uncatalogued_event_kinds_are_retained_by_observers():
    w = NoisyWorld(world_seed=1); obs = [REG.make("observer.trace.v1"), REG.make("observer.series.v1")]
    from prometheus.toolbox.ref.substrates import FlatInProcessSubstrate
    inst = FlatInProcessSubstrate().instantiate(random_statemachine(1), 1)
    r = run_episode(w, {0: inst}, obs, seed=1, horizon=5)
    m = obs[0].measure()
    assert m["events_by_kind"].get("UNKNOWN_99") == 5 and r["events"] >= 5


# C91: serialisation round trip + digest stability over the fuzzed compositions: to_dict -> JSON -> from_dict
# must reproduce the IR exactly and its digest; the digest must ignore provenance, id and execution policy.
@pytest.mark.parametrize("seed", list(range(40, 60)))
def test_ir_round_trips_through_json_with_a_stable_digest(seed):
    e = random_experiment(seed)
    d = json.loads(json.dumps(e.to_dict()))
    e2 = Experiment.from_dict(d)
    assert e2.to_dict() == e.to_dict() and e2.digest() == e.digest()
    e3 = Experiment.from_dict(dict(d, provenance={"x": 1}, id="custom"))
    e3.budget = dict(e3.budget, wall_s=1.5, max_runs=10)
    assert e3.digest() == e.digest()
    e4 = Experiment.from_dict(d); e4.budget = dict(e4.budget, horizon=e4.budget["horizon"] + 1)
    assert e4.digest() != e.digest()


# C128: two IR laws as properties. Sweeps: the number of points is the product of the axis sizes, every point sets
# exactly the swept paths and nothing else, the swept value is READ BACK from the point's IR at its dotted path, and
# points have distinct digests unless two axes' values coincide. Negotiation: BLOCKED implies a non-empty missing
# set that nobody provides; OK implies every implied requirement is provided.
def _get(d, path):
    cur = d
    for part in path.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


@pytest.mark.parametrize("seed", list(range(800, 880)))
def test_sweep_and_negotiation_laws(seed):
    from prometheus.toolbox import capabilities as C
    e = random_experiment(seed)
    if e.validate():
        return
    pts = e.sweep_points()
    expected = 1
    for vals in e.sweep.values():
        expected *= len(vals)
    assert len(pts) == expected and all(set(p) == set(e.sweep) for p in pts)
    base = e.to_dict()
    for p in pts:
        d = e.at_point(p).to_dict()
        for path, v in p.items():
            assert _get(d, path) == v, (seed, path)
        # a point's IR records its parent and the point in provenance and carries no sweep of its own; everything else is untouched
        assert d["sweep"] == {} and d["provenance"]["parent"] == e.experiment_id() and d["provenance"]["sweep_point"] == p
        untouched = {k: v for k, v in d.items() if k not in ("sweep", "provenance", "id") and not any(path.split(".")[0] == k for path in p)}
        assert untouched == {k: v for k, v in base.items() if k in untouched}, seed
    digests = [e.at_point(p).digest() for p in pts]
    if len(pts) > 1 and all(len(set(json.dumps(v, sort_keys=True) for v in vals)) == len(vals) for vals in e.sweep.values()):
        assert len(set(digests)) == len(pts), seed
    low = e.compile("local", REG)
    provided = REG.provided_capabilities(e.world["kind"], e.substrate["kind"]) | set(REG.make(e.substrate["kind"], **e.substrate.get("params", {})).capabilities) \
        | {"core.player.v1", "core.experiment.v1", "core.receipt.v1", "ext.intervention.observation_delay.v1", "ext.intervention.observation_permute.v1", "ext.intervention.schedule.v1"}
    if low.status == "BLOCKED_MISSING_CAPABILITY":
        missing = set(low.negotiation["missing"])
        assert missing and not (missing & provided) and missing <= set(e.derived_requirements()), (seed, missing)
    elif low.status == "OK":
        req = set(e.derived_requirements()) - {c for pl in e.players if pl.get("substrate") for c in pl.get("requires", ())}
        assert req <= provided, (seed, req - provided)


# C143: lowering laws as a property: n runs = points x arms x seeds; every RunSpec names the job; arm names are
# unique; the replay arm's experiment IS the primary's (same digest, since a replay re-runs the same thing) and
# every other arm's differs; splits follow the seed policy; the negotiation records what was provided.
@pytest.mark.parametrize("seed", list(range(1700, 1760)))
def test_lowering_laws(seed):
    from prometheus.toolbox.backends.local import lower, seeds_for
    e = random_experiment(seed)
    if e.validate():
        return
    low = lower(e, REG)
    if not low.ok:
        assert low.reasons and low.job is None
        return
    job = low.job; pts = e.sweep_points(); seeds = seeds_for(e); arms = ["primary"] + [REG.make(c["kind"], **c.get("params", {})).kind for c in e.controls]
    assert len(job.runs) == len(pts) * len(arms) * len(seeds), seed
    assert len(set(arms)) == len(arms) and {r.arm for r in job.runs} == set(arms)
    assert all(r.job_id == job.experiment_id for r in job.runs)
    for r in job.runs:
        assert (r.seed, r.split) in seeds
    by_arm = {}
    for r in job.runs:
        by_arm.setdefault((r.arm, json.dumps(r.sweep_point, sort_keys=True)), set()).add(r.experiment.digest())
    assert all(len(v) == 1 for v in by_arm.values())                            # one experiment per (arm, point)
    for (arm, pt), dg in by_arm.items():
        prim = by_arm[("primary", pt)]
        if arm == "replay":
            assert dg == prim, seed
        elif arm != "primary":
            assert dg != prim, (seed, arm)
    assert set(low.negotiation["required"]) <= set(low.negotiation["provided"]) | set(low.negotiation.get("uncatalogued", []))
