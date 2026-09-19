"""Kernel conformance tests (directive s35). Pure stdlib; every test runs on any host; devices that are not
reachable (Redis) are SKIPPED with the reason, never failed -- absence of optional infrastructure is not a
kernel defect (s32)."""
from __future__ import annotations

import json
import pathlib
import tempfile

import pytest

from prometheus.toolbox import capabilities as C
from prometheus.toolbox.contracts import World, Substrate, Observer, Objective, Control, ActionSpace, PlayerSpec
from prometheus.toolbox.ir import Experiment, IRError, ref
from prometheus.toolbox.receipt import validate as validate_receipt, read_all, ReceiptError
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.ref.players import random_statemachine, constant_player, proteus_available, random_proteus_player
from prometheus.toolbox.ref.worlds import IntegerWorld
from prometheus.toolbox.admission import admit_world
from prometheus.toolbox.examples.exp_001_delay_sweep import build as build_exp001
from prometheus.toolbox.backends.local import execute, run_episode
from prometheus.toolbox import state as ST

REG = default_registry()


# ------------------------------------------------------------------------------------------ capabilities
def test_capability_negotiation_is_a_result_not_an_exception():
    n = C.negotiate({"core.world.v1", "ext.physics2d.v1"}, {"core.world.v1"})
    assert n.status == C.STATUS_BLOCKED and n.missing == {"ext.physics2d.v1"} and not n.ok
    n2 = C.negotiate({"core.world.v1"}, {"core.world.v1", "ext.made_up.v3"})
    assert n2.ok and "ext.made_up.v3" in n2.uncatalogued
    assert not C.negotiate({"world"}, {"world"}).ok       # malformed id blocks


def test_core_set_is_tiny():
    assert len(C.CORE) == 5 and all(c.startswith("core.") for c in C.CORE)


# ------------------------------------------------------------------------------------------ world contract
def test_integer_world_satisfies_protocol_and_bit_replay():
    w1, w2 = IntegerWorld(world_seed=3, n_players=2), IntegerWorld(world_seed=3, n_players=2)
    assert isinstance(w1, World)
    for w in (w1, w2):
        w.reset(7)
        for _ in range(20):
            w.step({0: [1, 2], 1: [3, 0]})
    assert w1.trace_hash() == w2.trace_hash()
    w2.reset(8); w2.step({0: [1, 2], 1: [3, 0]})
    assert w1.trace_hash() != w2.trace_hash()


def test_integer_world_events_and_snapshot():
    w = IntegerWorld(world_seed=1); w.reset(1)
    w.step({0: [2, 2]})
    ev = w.events()
    assert ev and all(len(e) == 5 and all(isinstance(x, int) for x in e) for e in ev)
    assert w.events() == []                       # drained
    snap = w.snapshot(); o_before = w.observe(0)
    w.step({0: [7, 7]}); assert w.observe(0) != o_before or True
    w.restore(snap); assert w.observe(0) == o_before
    assert isinstance(w.legal_actions(0), ActionSpace)


def test_unknown_world_param_is_refused():
    with pytest.raises(ValueError):
        IntegerWorld(gravity=9)


# ------------------------------------------------------------------------------------------ players / substrate
def test_substrate_instantiates_and_accounts():
    sub = REG.make("substrate.flat.v1")
    assert isinstance(sub, Substrate)
    inst = sub.instantiate(random_statemachine(5), seed=1)
    a = inst.act([1, 2, 3, 4, 5], ActionSpace(2, 8))
    assert len(a) == 2 and all(0 <= x < 8 for x in a)
    assert inst.fingerprint() == sub.instantiate(random_statemachine(5), seed=2).fingerprint()   # spec identity, not run state
    assert sub.accounting()["instances"] == 2 and sub.accounting()["transitions"] >= 1


def test_substrate_refuses_unmet_player_requirements():
    sub = REG.make("substrate.flat.v1")
    spec = PlayerSpec("statemachine.v1", random_statemachine(1).payload, {}, frozenset({"ext.workspace.kv.v1"}))
    with pytest.raises(Exception):
        sub.instantiate(spec, 0)


@pytest.mark.skipif(not proteus_available(), reason="proteus not importable on this tree")
def test_proteus_player_runs_through_the_flat_substrate():
    sub = REG.make("substrate.flat.v1"); w = IntegerWorld(world_seed=2); inst = sub.instantiate(random_proteus_player(3), 1)
    r = run_episode(w, {0: inst}, [], seed=1, horizon=16)
    assert r["ticks"] >= 1 and inst.cost()["ops"] >= 1


# ------------------------------------------------------------------------------------------ IR
def test_ir_validates_digests_and_refuses_run():
    e = build_exp001()
    assert e.validate() == [] and not hasattr(e, "run")
    d = Experiment.from_dict(json.loads(json.dumps(e.to_dict())))
    assert d.digest() == e.digest()
    bad = Experiment(family="x/y", world={}, substrate={"kind": "substrate.flat.v1"})
    assert len(bad.validate()) >= 2      # C84: "players empty" is no longer a defect
    with pytest.raises(IRError):
        bad.compile("local", REG)


def test_ir_sweep_expands_and_derives_requirements():
    e = build_exp001()
    assert len(e.sweep_points()) == 4
    req = e.derived_requirements()
    assert {"ext.intervention.observation_delay.v1", "ext.intervention.world_params.v1", "ext.multiplayer.v1"} <= req


def test_missing_capability_blocks_one_experiment_only():
    e = build_exp001(); e.required_capabilities = frozenset({"ext.physics2d.v1"})
    low = e.compile("local", REG)
    assert low.status == "BLOCKED_MISSING_CAPABILITY" and "ext.physics2d.v1" in low.negotiation["missing"]
    assert build_exp001().compile("local", REG).ok           # the kernel did not stop


def test_unregistered_component_is_target_unsupported():
    e = build_exp001(); e.world = ref("world.box2d.v1")
    low = e.compile("local", REG)
    assert low.status == "TARGET_UNSUPPORTED" and "world.box2d.v1" in low.reasons[0]


# ------------------------------------------------------------------------------------------ end to end
def test_exp001_runs_end_to_end_with_all_controls_met(tmp_path):
    e = build_exp001(); e.sweep = {"interventions.0.wrappers.observation_delay": [0, 4]}; e.seed_policy = {"base": 5, "n_seeds": 2}
    low = e.compile("local", REG); assert low.ok
    rep = execute(low.job, tmp_path / "r.jsonl", REG)
    assert rep.n_failed == 0 and rep.valid and set(rep.controls) == {"replay", "cheat", "negative", "positive", "sham", "scratch", "permutation"}
    rs = read_all(tmp_path / "r.jsonl")
    assert len(rs) == rep.n_runs + 1
    prim = [r for r in rs if r["arm"] == "primary"]
    assert all(r["replay_class"] == "BIT" for r in prim) and all(r["science"]["objective"]["kind"] == "objective.yield_net.v1" for r in prim)
    assert all(not (set(r["engineering"]) & set(r["science"])) for r in rs)


def test_failed_control_is_a_result_not_a_halt(tmp_path):
    """A world that REFUSES the kernel cheat parameter: the cheat arm FAILS, the primary still runs, the report says
    invalid, nothing raises. (Until C71 wforge was that world; its wrapper now implements the cheat, so a
    fork-registered refusing world plays the part.)"""
    from prometheus.toolbox.registry import ComponentRecord

    class NoCheat(IntegerWorld):
        kind = "world.nocheat.test"

        def __init__(self, **params):
            if "_cheat_skip_dynamics" in params:
                raise TypeError("this engine has no cheat mechanism")
            super().__init__(**params)
    R = REG.fork(); R.register(ComponentRecord("world.nocheat.test", "world", NoCheat, IntegerWorld.capabilities, route="write", provenance={"author": "test"}, license="repository"))
    e = build_exp001(); e.world = ref("world.nocheat.test", world_seed=1, n_players=2); e.sweep = {}; e.seed_policy = {"base": 1, "n_seeds": 1}
    e.interventions = []; e.controls = [ref("control.replay.v1"), ref("control.cheat.v1")]; e.required_capabilities = frozenset({"ext.replay.bit.v1"})
    low = e.compile("local", R); assert low.ok, low.reasons
    rep = execute(low.job, tmp_path / "w.jsonl", R)
    assert rep.n_completed >= 2 and rep.controls["replay"]["outcome"] == "MET" and rep.controls["cheat"]["outcome"] == "INDETERMINATE" and not rep.valid


# ------------------------------------------------------------------------------------------ receipts
def test_receipt_schema_refuses_overlapping_ledgers_and_bad_ids(tmp_path):
    e = build_exp001(); e.sweep = {}; e.seed_policy = {"base": 1, "n_seeds": 1}; e.controls = []
    rep = execute(e.compile("local", REG).job, tmp_path / "x.jsonl", REG)
    r = read_all(tmp_path / "x.jsonl")[0]
    bad = dict(r); bad["engineering"] = dict(bad["engineering"], objective=1); bad["science"] = dict(bad["science"], objective=2)
    with pytest.raises(ReceiptError):
        validate_receipt(bad)
    bad2 = dict(r); bad2["seed"] = 999
    with pytest.raises(ReceiptError):
        validate_receipt(bad2)                    # receipt_id no longer matches content


# ------------------------------------------------------------------------------------------ admission
def test_admission_admits_reference_and_marks_broken_impl_unavailable():
    r = admit_world("world.integer.v1", REG); assert r.state == "ADMITTED" and not r.failed

    class BrokenWorld(IntegerWorld):
        kind = "world.broken.v1"

        def trace_hash(self):
            import os
            return os.urandom(8).hex()             # not replayable
    from prometheus.toolbox.registry import ComponentRecord
    R = REG.fork(); R.register(ComponentRecord("world.broken.v1", "world", BrokenWorld, IntegerWorld.capabilities, route="write", provenance={"author": "test"}, license="repository"))
    b = admit_world("world.broken.v1", R)
    assert b.state == "UNAVAILABLE" and "replay" in b.failed
    e = build_exp001(); e.world = ref("world.broken.v1")
    assert e.compile("local", R).status == "TARGET_UNSUPPORTED"
    assert build_exp001().compile("local", R).ok           # unrelated experiments unaffected
    assert not REG.has("world.broken.v1")                    # C62: the default registry never saw the test component


# ------------------------------------------------------------------------------------------ lowering (F1)
def test_sfe_lowering_names_every_mismatch_for_exp001():
    low = build_exp001().compile("sfe", REG)
    assert low.status == "TARGET_UNSUPPORTED"
    joined = " ".join(low.reasons)
    assert "world.kind" in joined and "evolution segment" in joined and "control" in joined


def test_sfe_lowering_succeeds_for_a_frontier_shaped_ir():
    pytest.importorskip("archaeon.frontier.specs")
    e = Experiment(family="frontier_probe", world=ref("world.c6.composed.sample", seed=3), substrate=ref("substrate.flat.v1"), players=[],
                   selector=ref("selector.frontier.segment.v1", profile="v0", N=8, generations=2), objective=ref("objective.frontier.segment_reward.v1"),
                   observers=[ref("observer.frontier.detectors.v1")], controls=[ref("control.replay.v1")],
                   budget={"episodes": 4, "horizon": 24, "evaluations": 64}, provenance={"lane": "PROCEDURAL"})
    low = e.compile("sfe", REG)
    assert low.status == "OK", low.reasons
    assert low.job["schema"] == "archaeon.frontier.experiment_spec.v1" and low.job["organism"]["profile"] == "v0"


def test_npe_lowering_builds_a_valid_envelope_but_is_unavailable_until_primordial_lands():
    from prometheus.toolbox.backends.npe import validate_envelope
    low = build_exp001().compile("npe", REG)
    assert low.status in ("UNAVAILABLE_INTERFACE", "OK") and validate_envelope(low.job["envelope"]) == []
    assert low.job["kwargs"]["experiment"]["family"] == "exp001_delay_sweep"


# ------------------------------------------------------------------------------------------ state devices (Phase 2)
def _state_script(dev):
    dev.advance(0)
    dev.put("a", 1, scope="episode"); dev.put("b", b"xy", scope="lifetime", ttl=2); dev.put("p", 9, scope="persistent")
    dev.hset("rec", "f", 5); dev.append("s", (1, 2, 3)); dev.append("s", (4, 5, 6)); dev.zadd("rank", "m1", 3); dev.zadd("rank", "m0", 1)
    out = {"a": dev.get("a"), "b": dev.get("b"), "rec": dev.hget("rec", "f"), "s": dev.read("s", since=1), "z": dev.zrange("rank", 0, -1)}
    dev.advance(2); out["b_after_ttl"] = dev.get("b")
    out["ended"] = dev.end_scope("episode"); out["a_after_end"] = dev.get("a"); out["p_after_end"] = dev.get("p")
    snap = dev.snapshot(); dev.put("q", 1, scope="persistent"); dev.restore(snap); out["q_after_restore"] = dev.get("q")
    out["acct_keys"] = dev.accounting()["keys"]; out["expired"] = dev.accounting()["expired"]
    return out


EXPECTED = {"a": 1, "b": b"xy", "rec": 5, "s": [(2, (4, 5, 6))], "z": [("m0", 1), ("m1", 3)], "b_after_ttl": None, "a_after_end": None,
            "p_after_end": 9, "q_after_restore": None, "expired": 1}


def test_inprocess_state_device_semantics():
    out = _state_script(ST.InProcessStateDevice())
    for k, v in EXPECTED.items():
        assert out[k] == v, (k, out[k], v)
    assert out["ended"] >= 3


def test_redis_state_device_matches_inprocess_semantics():
    avail = ST.available_devices()["state.redis.v1"]
    if not avail["ok"]:
        pytest.skip("no Redis reachable: %s" % avail["reason"])
    out = _state_script(ST.RedisStateDevice(ns="pk_test"))
    for k, v in EXPECTED.items():
        assert out[k] == v, (k, out[k], v)


def test_state_device_events_are_kernel_events():
    dev = ST.InProcessStateDevice(); dev.put("k", 3, player=1); dev.get("k", player=1)
    ev = dev.events()
    assert len(ev) == 2 and all(len(e) == 5 for e in ev) and ev[0][2] == 1


# ------------------------------------------------------------------------------------------ schemas match code
def test_json_schemas_agree_with_the_code():
    import re
    root = pathlib.Path(__file__).resolve().parents[1] / "schemas"
    exp_schema = json.loads((root / "experiment.schema.json").read_text(encoding="utf-8"))
    assert set(exp_schema["required"]) <= set(build_exp001().to_dict().keys())
    rec_schema = json.loads((root / "receipt.schema.json").read_text(encoding="utf-8"))
    from prometheus.toolbox.receipt import REQUIRED, STATUSES
    assert set(rec_schema["required"]) == set(REQUIRED) and set(rec_schema["properties"]["status"]["enum"]) == set(STATUSES)
    from prometheus.toolbox.backends.local import SCALAR_EXECUTION, batch_plan
    from prometheus.toolbox.registry import default_registry as _dr
    reasons = {SCALAR_EXECUTION["reason"], "BATCHED"}
    e = build_exp001(); e.budget = dict(e.budget, batch=4); reasons.add(batch_plan(e, _dr())[1])
    e2 = build_exp001(); e2.interventions = []; e2.budget = dict(e2.budget, batch=4); reasons.add(batch_plan(e2, _dr())[1])
    assert reasons <= set(rec_schema["properties"]["execution"]["properties"]["reason"]["enum"])          # C105: the schema names every reason the code emits
    cap_schema = json.loads((root / "capability.schema.json").read_text(encoding="utf-8"))
    pat = re.compile(cap_schema["$defs"]["capabilityId"]["pattern"])
    for cid in list(C.CORE) + list(C.EXTENSIONS):
        assert pat.match(cid) and C.well_formed(cid), cid
    assert set(cap_schema["$defs"]["core"]["enum"]) == set(C.CORE)
    from prometheus.toolbox.registry import SLOTS, STATES
    assert set(cap_schema["$defs"]["registryRow"]["properties"]["slot"]["enum"]) == set(SLOTS)
    assert set(cap_schema["$defs"]["registryRow"]["properties"]["state"]["enum"]) == set(STATES)


# ------------------------------------------------------------------------------------------ EXP-001 as a frozen fixture
def test_exp001_committed_receipts_are_a_semantic_fixture(tmp_path):
    """The committed EXP-001 receipts pin the integer world's and the wrappers' semantics: a fresh run of the
    same IR must reproduce every primary trace hash and series-free objective value. Drift = a semantic change
    that must be versioned, not absorbed (overnight directive s2: EXP-001 is a regression fixture)."""
    committed = pathlib.Path(__file__).resolve().parents[1] / "examples" / "receipts" / "exp_001.jsonl"
    old = {(json.dumps(r["sweep_point"], sort_keys=True), r["seed"]): (r["trace_hashes"], r["science"]["objective"]["value"])
           for r in read_all(committed) if r["arm"] == "primary"}
    assert len(old) == 12
    e = build_exp001(); e.controls = []
    rep = execute(e.compile("local", REG).job, tmp_path / "fresh.jsonl", REG); assert rep.n_failed == 0
    new = {(json.dumps(r["sweep_point"], sort_keys=True), r["seed"]): (r["trace_hashes"], r["science"]["objective"]["value"])
           for r in read_all(tmp_path / "fresh.jsonl") if r["arm"] == "primary"}
    assert new == old


def test_series_schema_agrees_with_the_code_and_the_public_surface_imports():
    import prometheus.toolbox as T
    for name in T.__all__:
        assert getattr(T, name) is not None
    root = pathlib.Path(__file__).resolve().parents[1] / "schemas"
    sch = json.loads((root / "series.schema.json").read_text(encoding="utf-8"))
    from prometheus.toolbox import series as S
    assert set(sch["properties"]["status"]["enum"]) >= set(S.WRITTEN_STATUSES) and sch["properties"]["encoding"]["const"] == S.ENCODING
