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
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, constant_player, random_proteus_player, proteus_available
from prometheus.toolbox.ref.worlds import IntegerWorld
from prometheus.toolbox.contracts import EVENT_KINDS

REG = default_registry()


def random_experiment(seed: int) -> Experiment:
    rnd = random.Random(seed)
    n_players = rnd.choice([1, 1, 2, 3])
    reps = ["sm1", "sm2", "const"] + (["proteus"] if proteus_available() else [])
    players = []
    for i in range(n_players):
        r = rnd.choice(reps)
        players.append({"sm1": lambda: random_statemachine(rnd.randrange(10**6), rnd.choice([2, 4, 6]), rnd.choice([4, 8, 16]), rnd.choice([1, 2, 3])),
                        "sm2": lambda: random_statemachine_v2(rnd.randrange(10**6), rnd.choice([2, 4]), rnd.choice([4, 8]), rnd.choice([1, 2])),
                        "const": lambda: constant_player([rnd.randrange(8) for _ in range(rnd.choice([1, 2, 3]))]),
                        "proteus": lambda: random_proteus_player(rnd.randrange(10**6))}[r]().manifest())
    world = ref("world.integer.v1", n_regs=rnd.choice([3, 6, 9]), n_players=n_players, act_width=rnd.choice([1, 2, 3]), act_range=rnd.choice([2, 8, 16]),
                n_ops=rnd.choice([0, 2, 5]), regime_period=rnd.choice([0, 0, 3, 7]), stoch_rate=rnd.choice([0, 0, 2, 9]), action_delay=rnd.choice([0, 1, 4]),
                world_seed=rnd.randrange(1000), start_charge=rnd.choice([1, 8, 64, 100000]), step_cost=rnd.choice([0, 1, 5]), yield_amt=rnd.choice([0, 4, 40]),
                obs_regs=rnd.choice([1, 4, 9]))
    substrate = rnd.choice([ref("substrate.flat.v1"), ref("substrate.kv.v1", scope=rnd.choice(["episode", "lifetime", "persistent"]), ttl=rnd.choice([None, 1, 3]), max_keys=rnd.choice([0, 1, 100])),
                            ref("substrate.stream.v1", scope=rnd.choice(["episode", "lifetime"]), lag=rnd.choice([1, 2, 9]), maxlen=rnd.choice([1, 8]))])
    interventions = []
    for _ in range(rnd.choice([0, 1, 2, 3])):
        interventions.append({"name": "iv", "world_params": rnd.choice([{}, {"regime_period": rnd.choice([0, 2])}, {"stoch_rate": rnd.choice([0, 3])}]),
                              "wrappers": rnd.choice([{}, {"observation_delay": rnd.choice([0, 1, 5, 40])}, {"observation_permute": rnd.randrange(100)}])})
    controls = rnd.sample(["control.replay.v1", "control.cheat.v1", "control.negative.v1", "control.positive.v1", "control.sham.v1", "control.scratch.v1", "control.permutation.v1"], rnd.choice([0, 1, 3]))
    observers = rnd.sample(["observer.trace.v1", "observer.descriptor.v1", "observer.series.v1"], rnd.choice([0, 1, 3]))
    sweep = rnd.choice([{}, {"world.params.world_seed": [1, 2]}, {"budget.horizon": [0, 3]}, {"interventions.0.wrappers.observation_delay": [0, 2]} if interventions else {}])
    budget = {"episodes": rnd.choice([1, 2, 4]), "horizon": rnd.choice([0, 1, 5, 30])}
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
                      objective=rnd.choice([None, ref("objective.yield_net.v1", penalties={"ops": 0.1}), ref("objective.survival.v1")]),
                      observers=[ref(o) for o in observers], controls=[ref(c) for c in controls], sweep=sweep,
                      seed_policy={"base": rnd.randrange(10**4), "n_seeds": rnd.choice([1, 2])}, budget=budget)


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
    assert not failed, "seed %d: %s" % (seed, [(r["arm"], r.get("error")) for r in failed][:3])
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
