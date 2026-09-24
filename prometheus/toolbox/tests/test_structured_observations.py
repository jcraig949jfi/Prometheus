"""Observations are not assumed flat (overnight C100; directive s10 "observations are scalar" and the design's
honest list "observations are int lists"). A world may declare ext.observation.structured.v1 and observe() a
nested JSON of ints (dict / list / int). The kernel treats an observation as OPAQUE data: it is delivered,
delayed, hashed and recorded as given. The reference players read it through one canonical flatten() (sorted
keys, depth first). The one kernel wrapper that needs a flat vector -- observation_permute -- is refused at
lowering for a structured world, with the reason; nothing is silently flattened."""
from __future__ import annotations

import json
import pathlib

import pytest

from prometheus.toolbox.contracts import flatten
from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower, ObservationWrapper
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, random_statemachine_v3, random_rewrite_system, constant_player
from prometheus.toolbox.ref.worlds_grid import GridWorld

REG = default_registry()


def test_flatten_is_canonical_and_total():
    assert flatten(7) == [7]
    assert flatten([1, [2, 3], [[4]]]) == [1, 2, 3, 4]
    assert flatten({"b": [2, 3], "a": 1, "c": {"z": 9, "y": [8]}}) == [1, 2, 3, 8, 9]
    assert flatten({}) == [] and flatten([]) == []
    with pytest.raises(TypeError):
        flatten({"a": 1.5})
    with pytest.raises(TypeError):
        flatten("abc")


def test_grid_world_offers_a_structured_observation_with_the_same_trace():
    flat = GridWorld(world_seed=3, n_players=2); struct = GridWorld(world_seed=3, n_players=2, obs_mode="structured")
    assert "ext.observation.structured.v1" not in flat.capabilities and "ext.observation.structured.v1" in struct.capabilities
    flat.reset(1); struct.reset(1)
    o = struct.observe(0)
    assert isinstance(o, dict) and set(o) == {"node", "pool", "cells", "foreign", "others", "charge"}
    assert flat.observe(0) == [o["node"], o["pool"], o["cells"], o["foreign"], o["others"], o["charge"]]
    acts = {0: [1, 2, 0], 1: [2, 1, 1]}
    for _ in range(12):
        flat.step(acts); struct.step(acts)
    assert flat.trace_hash() == struct.trace_hash()          # the encoding of the observation is not the state


def test_every_reference_player_acts_on_a_structured_observation():
    sub = REG.make("substrate.kv.v1"); space = GridWorld(world_seed=3).legal_actions(0)
    obs = {"node": 2, "pool": 1, "cells": 0, "foreign": 1, "others": 0, "charge": 9}
    # the fuzz (seed 20) found statemachine.v3 reading list(obs) -- the KEYS of a dict -- after v1/v2 were fixed: every representation is listed here
    for spec in (random_statemachine(3, width=3), random_statemachine_v2(3, width=3), random_statemachine_v3(3, width=3), random_rewrite_system(3), constant_player([1, 2, 3])):
        inst = sub.instantiate(spec, 1)
        a = inst.act(obs, space)
        assert isinstance(a, list) and len(a) == 3 and all(isinstance(x, int) for x in a), spec.representation
        b = sub.instantiate(spec, 1).act(flatten(obs), space)
        assert a == b, "a player must read the structured observation through flatten(): %s" % spec.representation


def _exp(obs_mode, wrappers=None):
    return Experiment(family="structured", world=ref("world.grid.v1", world_seed=3, n_players=2, obs_mode=obs_mode), substrate=ref("substrate.kv.v1"),
                      players=[random_statemachine_v2(3, width=3).manifest(), random_rewrite_system(4).manifest()],
                      interventions=[{"name": "w", "world_params": {}, "wrappers": wrappers or {}}],
                      objective=ref("objective.yield_net.v1"), observers=[ref("observer.trace.v1"), ref("observer.series.v1")],
                      controls=[ref("control.replay.v1"), ref("control.sham.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 2, "horizon": 24})


def test_structured_observations_run_end_to_end_and_are_delayed_opaquely(tmp_path):
    low = lower(_exp("structured"), REG); assert low.ok, low.as_dict()
    rep = execute(low.job, tmp_path / "s.jsonl", REG)
    assert rep.valid and rep.n_failed == 0 and rep.controls["replay"]["outcome"] == "MET"
    low = lower(_exp("structured", wrappers={"observation_delay": 2}), REG); assert low.ok, low.as_dict()
    rep = execute(low.job, tmp_path / "d.jsonl", REG)
    assert rep.valid and rep.n_failed == 0
    w = ObservationWrapper(GridWorld(world_seed=3, n_players=1, obs_mode="structured"), delay=1); w.reset(1)
    first = w.observe(0); w.step({0: [1, 1, 1]}); second = w.observe(0)
    assert isinstance(first, dict) and isinstance(second, dict) and second == first       # delayed by one tick, structure intact


def test_permute_is_refused_for_a_structured_world_with_the_reason():
    low = lower(_exp("structured", wrappers={"observation_permute": 5}), REG)
    assert not low.ok and low.status == "TARGET_UNSUPPORTED" and any("observation_permute" in r and "structured" in r for r in low.reasons), low.as_dict()
    low = lower(_exp("flat", wrappers={"observation_permute": 5}), REG); assert low.ok
    e = _exp("structured"); e.controls = [ref("control.permutation.v1")]
    low = lower(e, REG)
    assert not low.ok and any("observation_permute" in r for r in low.reasons)            # a control that needs it is refused too, before any run
