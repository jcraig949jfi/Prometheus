"""Batched execution (overnight C92; report s18 pressure 1; design U1 / ext.batch.v1).

A batched world simulates n environments in lockstep behind ONE object. Batching is an EXECUTION POLICY
(budget.batch, outside the scientific digest like wall_s), never a scientific change: every science-bearing
field of a batched receipt must equal the scalar path's, run for run. Where the policy cannot be honoured the
executor falls back to the scalar path and the receipt says why (execution.batched=False, execution.reason).
"""
from __future__ import annotations

import collections
import json
import pathlib
import tempfile

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry, ComponentRecord
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute
from prometheus.toolbox.ref.players import random_statemachine_v2, constant_player
from prometheus.toolbox.ref.worlds import IntegerWorld

REG = default_registry()
SCIENCE_FIELDS = ("trace_hashes", "events_total", "science", "replay_class", "status", "capabilities", "split")


def _exp(world_kind="world.integer.v1", n_seeds=6, wrappers=None, **wp):
    params = dict(n_regs=6, n_players=2, act_width=2, act_range=8, world_seed=23, start_charge=24, yield_amt=10, step_cost=1)
    params.update(wp)
    return Experiment(
        family="batch_probe",
        world=ref(world_kind, **params) if world_kind == "world.integer.v1" else ref(world_kind),
        substrate=ref("substrate.kv.v1"),
        players=[random_statemachine_v2(21, n_states=5, n_buckets=12, mem_range=16, write_every=2).manifest(), constant_player([3, 1]).manifest()],
        interventions=[{"name": "conditions", "world_params": {"regime_period": 5, "stoch_rate": 3, "action_delay": 1} if world_kind == "world.integer.v1" else {},
                        "wrappers": wrappers or {}}],
        objective=ref("objective.yield_net.v1", penalties={"ws_reads": 0.05, "ws_writes": 0.05}),
        observers=[ref("observer.trace.v1"), ref("observer.series.v1")],
        controls=[ref("control.replay.v1"), ref("control.sham.v1")],
        seed_policy={"base": 500, "n_seeds": n_seeds, "holdout_seeds": 1},
        budget={"episodes": 2, "horizon": 40},
        provenance={"designer": "test"},
    )


def _run(exp, batch, tmp, name):
    e = Experiment.from_dict(exp.to_dict())
    e.budget = dict(e.budget, batch=batch)
    low = e.compile("local"); assert low.ok, low.as_dict()
    rep = execute(low.job, pathlib.Path(tmp) / name)
    rows = [r for r in read_all(rep.receipts_path) if r["arm"] != "SUMMARY"]
    return rep, {(r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"]): r for r in rows}


def _strip(acc):
    return {k: v for k, v in acc.items() if k not in ("wall_s", "cpu_s")}


# ------------------------------------------------------------------------------------------ policy
def test_batch_is_execution_policy_not_science():
    e = _exp(); d0 = e.digest()
    e.budget = dict(e.budget, batch=8)
    assert e.digest() == d0 and not e.validate()
    e.budget = dict(e.budget, batch=0); assert e.validate() == [] or all("batch" not in m for m in e.validate())
    e.budget = dict(e.budget, batch=-1); assert any("batch" in m for m in e.validate())
    e.budget = dict(e.budget, batch="4"); assert any("batch" in m for m in e.validate())


# ------------------------------------------------------------------------------------------ the batch world itself
def _drive(world_cls, seeds, ticks, actions, **params):
    out = []
    for s in seeds:
        w = world_cls(**params); w.reset(s); evs = []
        for _ in range(ticks):
            done = w.step(actions); evs += w.events()
            if done:
                break
        out.append((w.trace_hash(), evs, w.summary()))
    return out


@pytest.mark.parametrize("params", [dict(), dict(regime_period=4, stoch_rate=2, action_delay=2), dict(n_players=3, start_charge=6, step_cost=2), dict(n_players=0)])
def test_batch_world_reproduces_the_reference_env_for_env(params):
    from prometheus.toolbox.ref.worlds_integer_batch import IntegerWorldBatch
    p = dict(world_seed=9, n_players=2, horizon=30); p.update(params)
    seeds = [1, 2, 3, 4, 5]
    acts = {pid: [pid + 1, 2] for pid in range(p["n_players"])}
    ref_out = _drive(IntegerWorld, seeds, 30, acts, **p)
    w = IntegerWorldBatch(n_envs=len(seeds), **p); w.reset_batch(seeds)
    evs = [[] for _ in seeds]; done = [False] * len(seeds)
    for _ in range(30):
        d = w.step_batch([acts] * len(seeds))
        for i, e in enumerate(w.events_batch()):
            evs[i] += e
        done = [a or b for a, b in zip(done, d)]
        if all(done):
            break
    assert w.trace_hashes() == [o[0] for o in ref_out]
    assert evs == [o[1] for o in ref_out]
    assert w.summaries() == [o[2] for o in ref_out]
    # the scalar view (n_envs=1) is the same world: admission drives it through the ordinary contract
    w1 = IntegerWorldBatch(**p); w1.reset(seeds[2])
    for _ in range(30):
        if w1.step(acts):
            break
    assert w1.trace_hash() == ref_out[2][0]


def test_batch_world_is_admitted_by_reference_agreement_and_a_wrong_one_is_refused():
    from prometheus.toolbox.admission import admit
    from prometheus.toolbox.ref.worlds_integer_batch import IntegerWorldBatch

    class Wrong(IntegerWorldBatch):
        kind = "world.integer_batch_wrong.v1"
        ACT_MUL = 98
    R = REG.fork()
    R.register(ComponentRecord("world.integer_batch_wrong.v1", "world", Wrong, IntegerWorldBatch.capabilities, implements="world.integer", route="write", provenance={"author": "test"}, license="repository"))
    ok = admit("world.integer_batch.v1", R); bad = admit("world.integer_batch_wrong.v1", R)
    assert ok.state == "ADMITTED" and ok.checks["reference"]["ok"] is True and "ext.batch.v1" in REG.get("world.integer_batch.v1").capabilities
    assert bad.state == "UNAVAILABLE" and "reference" in bad.failed
    assert REG.batch_implementation("world.integer.v1") == "world.integer_batch.v1"
    assert REG.batch_implementation("world.grid.v1") is None
    assert R.batch_implementation("world.integer.v1") == "world.integer_batch.v1"    # the wrong one is UNAVAILABLE, never chosen


# ------------------------------------------------------------------------------------------ the executor path
def test_batched_execution_reproduces_the_scalar_receipts_run_for_run():
    exp = _exp()
    with tempfile.TemporaryDirectory() as td:
        rep_s, scalar = _run(exp, 0, td, "scalar.jsonl")
        rep_b, batched = _run(exp, 4, td, "batched.jsonl")
    assert rep_s.valid and rep_b.valid and rep_s.n_runs == rep_b.n_runs == 21
    assert set(scalar) == set(batched)
    for k, r in scalar.items():
        b = batched[k]
        for f in SCIENCE_FIELDS:
            assert b[f] == r[f], (k, f)
        assert _strip(b["accounting"]) == _strip(r["accounting"]), k
        assert b["series"]["observer.series.v1"]["series_hash"] == r["series"]["observer.series.v1"]["series_hash"], k
        assert r["execution"] == {"batched": False, "batch_size": 1, "reason": "BATCH_NOT_REQUESTED"}, k
        assert b["execution"]["batched"] is True and b["execution"]["world"] == "world.integer_batch.v1", k
    sizes = sorted(b["execution"]["batch_size"] for b in batched.values())
    assert sizes == [3] * 9 + [4] * 12          # 7 seeds per arm (6 + 1 holdout) -> a batch of 4 and a batch of 3, for each of 3 arms


def test_batch_falls_back_and_says_why():
    with tempfile.TemporaryDirectory() as td:
        _, rows = _run(_exp(world_kind="world.grid.v1", n_seeds=3), 4, td, "grid.jsonl")
        assert {r["execution"]["reason"] for r in rows.values()} == {"NO_BATCH_IMPLEMENTATION"} and all(not r["execution"]["batched"] for r in rows.values())
        e = _exp(n_seeds=3); e.interventions[0]["schedule"] = [{"tick": 3, "world_params": {"step_cost": 2}}]
        _, rows = _run(e, 4, td, "scheduled.jsonl")
        assert {r["execution"]["reason"] for r in rows.values()} == {"BATCHED"}                          # C112: schedules batch on a world with set_params
        from prometheus.toolbox.backends.local import batch_plan
        R = REG.fork(); row = R.get("world.integer_batch.v1"); row.capabilities = row.capabilities - {"ext.world.mutable_params.v1"}
        e.budget = dict(e.budget, batch=4); assert batch_plan(e, R) == (None, "SCHEDULE_NOT_BATCHED")
        _, rows = _run(_exp(n_seeds=3, wrappers={"observation_delay": 1}), 4, td, "wrapped.jsonl")       # C111: delay/permute batch now
        assert {r["execution"]["reason"] for r in rows.values()} == {"BATCHED"}
        _, rows = _run(_exp(n_seeds=3), 1, td, "one.jsonl")
        assert {r["execution"]["reason"] for r in rows.values()} == {"BATCH_NOT_REQUESTED"}


def test_one_failing_env_does_not_take_the_batch_down():

    class Bomb:
        kind = "bomb"; version = 1
        def __init__(self, seed):
            self.seed = seed; self.n = 0
        def act(self, obs, space):
            self.n += 1
            if self.seed % 3 == 0 and self.n == 5:
                raise RuntimeError("bomb %d" % self.seed)
            return [1, 1]
        def adapt(self, *a, **k): pass
        def cost(self): return {}
        def fingerprint(self): return "bomb%d" % self.seed
        def snapshot(self): return b""
        def restore(self, b): pass

    def make_bomb(payload=None, **kw):
        return {"representation": "bomb.v1", "payload": {}, "initial_state": {}, "requires": [], "meta": {}}
    from prometheus.toolbox.ref.substrates import KVSubstrate

    class KVWithBombs(KVSubstrate):                 # a substrate that can instantiate the bomb; everything else as kv
        kind = "substrate.kv_bombs.v1"
        representations = KVSubstrate.representations | {"bomb.v1"}
        def instantiate(self, spec, seed):
            return Bomb(seed) if spec.representation == "bomb.v1" else KVSubstrate.instantiate(self, spec, seed)
    R = REG.fork()
    R.register(ComponentRecord("bomb.v1", "representation", make_bomb, frozenset({"core.player.v1"}), route="write", provenance={"author": "test"}, license="repository"))
    R.register(ComponentRecord("substrate.kv_bombs.v1", "substrate", KVWithBombs, KVSubstrate.capabilities, route="write", provenance={"author": "test"}, license="repository"))
    exp = _exp(n_seeds=6)
    exp.substrate = ref("substrate.kv_bombs.v1")
    exp.players = [make_bomb(), constant_player([3, 1]).manifest()]
    exp.controls = []
    e = Experiment.from_dict(exp.to_dict()); e.budget = dict(e.budget, batch=6)
    low = e.compile("local", registry=R); assert low.ok, low.as_dict()
    with tempfile.TemporaryDirectory() as td:
        rep = execute(low.job, pathlib.Path(td) / "bomb.jsonl", registry=R)
        rows = [r for r in read_all(rep.receipts_path) if r["arm"] != "SUMMARY"]
    failed = [r for r in rows if r["status"] == "FAILED"]; ok = [r for r in rows if r["status"] == "COMPLETED"]
    assert failed and ok and all("bomb" in r["error"] for r in failed)
    assert {r["seed"] * 31 % 3 == 0 for r in failed} == {True} and all(r["seed"] * 31 % 3 != 0 for r in ok)
    assert all(r["execution"]["batched"] for r in ok) and all(r["execution"]["batched"] for r in failed)
    assert rep.n_failed == len(failed)


def test_batch_world_unavailable_on_this_host_falls_back():
    """C92b: the WSL probe found the whole registry failing to install without numpy; now the row stays, UNAVAILABLE, and
    the executor takes the scalar path with the reason on every receipt."""
    R = REG.fork(); row = R.get("world.integer_batch.v1"); row.state = "UNAVAILABLE"; row.admission = {"failed": "import: No module named numpy"}
    assert R.batch_implementation("world.integer.v1") is None
    from prometheus.toolbox.backends.local import batch_plan
    e = _exp(n_seeds=2); e.budget = dict(e.budget, batch=4)
    assert batch_plan(e, R) == (None, "NO_BATCH_IMPLEMENTATION")
    from prometheus.toolbox.admission import admit
    assert admit("world.integer_batch.v1", R).checks["registry"]["note"] == "absent machinery"


def test_interrupted_batched_job_resumes_and_matches_a_clean_run(tmp_path, monkeypatch):
    from prometheus.toolbox.backends import local as L
    e = _exp(n_seeds=6); e.budget = dict(e.budget, batch=4)
    job = L.lower(e, REG).job
    calls = {"n": 0}; real = L.run_batch

    def flaky(specs, registry, batch_kind, receipt_dir=None):
        calls["n"] += 1
        if calls["n"] == 3:
            raise KeyboardInterrupt("simulated interruption between batches")
        return real(specs, registry, batch_kind, receipt_dir)
    monkeypatch.setattr(L, "run_batch", flaky)
    with pytest.raises(KeyboardInterrupt):
        execute(job, tmp_path / "j.jsonl", REG)
    partial = [r for r in read_all(tmp_path / "j.jsonl") if r["arm"] != "SUMMARY"]
    assert 0 < len(partial) < 21 and all(r["execution"]["batched"] for r in partial)
    monkeypatch.setattr(L, "run_batch", real)
    rep = execute(job, tmp_path / "j.jsonl", REG, resume=True)
    assert rep.valid and rep.resumed_runs == len(partial) and rep.n_completed == 21
    rows = {(r["arm"], r["seed"]): r for r in read_all(tmp_path / "j.jsonl") if r["arm"] != "SUMMARY"}
    clean = execute(L.lower(e, REG).job, tmp_path / "clean.jsonl", REG)
    crow = {(r["arm"], r["seed"]): r for r in read_all(tmp_path / "clean.jsonl") if r["arm"] != "SUMMARY"}
    assert len(rows) == len(crow) == 21 and all(rows[k]["trace_hashes"] == crow[k]["trace_hashes"] for k in crow)


def test_absent_machinery_row_keeps_its_reason_across_repeated_admission():
    from prometheus.toolbox.admission import admit
    R = REG.fork(); row = R.get("world.integer_batch.v1"); row.state = "UNAVAILABLE"; row.admission = {"failed": "import: No module named numpy"}
    for _ in range(3):
        res = admit("world.integer_batch.v1", R)
        assert res.state == "UNAVAILABLE" and res.checks["registry"]["note"] == "absent machinery" and res.checks["registry"]["reason"].startswith("import")
    assert R.batch_implementation("world.integer.v1") is None


# ------------------------------------------------------------------------------------------ property over random IRs (C93)
_COVERAGE = collections.Counter()          # how the 40 random IRs were executed; the guard below refuses a vacuous green


@pytest.mark.parametrize("seed", list(range(100, 140)))
def test_batched_execution_equals_scalar_execution_for_random_experiments(tmp_path, seed):
    """For any valid IR the scalar and the batched path must agree run for run on every science field, whatever the
    executor decided about batching (the reason is on the receipt). Failures may differ only in their timing fields."""
    from prometheus.toolbox.tests.test_fuzz import random_experiment
    e = random_experiment(seed)
    if e.validate():
        return
    low = e.compile("local", REG)
    if not low.ok:
        return
    eb = Experiment.from_dict(e.to_dict()); eb.budget = dict(eb.budget, batch=3)
    lb = eb.compile("local", REG); assert lb.ok and lb.job.experiment_id == low.job.experiment_id
    execute(low.job, tmp_path / "s.jsonl", REG); execute(lb.job, tmp_path / "b.jsonl", REG)
    S = {(r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"]): r for r in read_all(tmp_path / "s.jsonl") if r["arm"] != "SUMMARY"}
    B = {(r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"]): r for r in read_all(tmp_path / "b.jsonl") if r["arm"] != "SUMMARY"}
    assert set(S) == set(B)
    for b in B.values():
        _COVERAGE[b["execution"]["reason"]] += 1
    for k, r in S.items():
        b = B[k]
        assert b["status"] == r["status"], k
        if r["status"] != "COMPLETED":
            bw = b["execution"].get("world")
            norm = b["error"].replace(bw, r["components"]["world"]["kind"]) if bw else b["error"]     # the batch world names itself in its errors (C140: never replace "")
            assert norm == r["error"], (k, b["error"], r["error"])
            continue
        for f in SCIENCE_FIELDS:
            assert b[f] == r[f], (seed, k, f)
        assert _strip(b["accounting"]) == _strip(r["accounting"]), (seed, k)
        assert {kk: v["series_hash"] for kk, v in (b.get("series") or {}).items()} == {kk: v["series_hash"] for kk, v in (r.get("series") or {}).items()}, (seed, k)
    sums = {r["experiment_id"]: r for r in read_all(tmp_path / "s.jsonl") if r["arm"] == "SUMMARY"}
    sumb = {r["experiment_id"]: r for r in read_all(tmp_path / "b.jsonl") if r["arm"] == "SUMMARY"}
    assert list(sums) == list(sumb)
    for k in sums:
        assert sums[k]["science"] == sumb[k]["science"], (seed, "controls/splits")


def test_the_random_property_actually_exercised_the_batch_path():
    """Coverage guard (C93): 40 random IRs must have produced BATCHED runs, or the property above proved nothing."""
    assert _COVERAGE["BATCHED"] >= 10, dict(_COVERAGE)
    assert _COVERAGE["NO_BATCH_IMPLEMENTATION"] > 0 and _COVERAGE["BATCHED"] > _COVERAGE["NO_BATCH_IMPLEMENTATION"], dict(_COVERAGE)


# ------------------------------------------------------------------------------------------ replay across paths (C99)
def test_replay_of_a_batched_file_runs_the_scalar_path_and_agrees(tmp_path):
    from prometheus.toolbox.backends.local import replay_file
    exp = _exp()
    _, batched = _run(exp, 4, tmp_path, "b.jsonl")
    assert all(r["execution"]["batched"] for r in batched.values())
    out = replay_file(tmp_path / "b.jsonl", tmp_path / "replay.jsonl")
    assert out["status"] == "OK" and out["runs_compared"] == 21 and out["divergent"] == []
    assert out["recorded_batch"] == 4 and out["replayed_batch"] == 0 and out["recorded_batched_runs"] == 21
    rows = [r for r in read_all(tmp_path / "replay.jsonl") if r["arm"] != "SUMMARY"]
    assert rows and all(r["execution"]["batched"] is False for r in rows)
    out2 = replay_file(tmp_path / "b.jsonl", tmp_path / "replay_same.jsonl", batch=None)      # the recorded policy, on request
    assert out2["replayed_batch"] == 4 and out2["divergent"] == []


# ------------------------------------------------------------------------------------------ search above a batched kernel (C101)
def test_evolve_reaches_the_same_archive_on_the_batched_and_the_scalar_path(tmp_path):
    from prometheus.toolbox import search as SR
    from prometheus.toolbox.ref.players import random_statemachine_v2

    def template(batch):
        return Experiment(family="batch_search", world=ref("world.integer.v1", world_seed=19, n_regs=6, start_charge=40, yield_amt=10, regime_period=6),
                          substrate=ref("substrate.kv.v1", scope="lifetime"), players=[random_statemachine_v2(1).manifest()],
                          objective=ref("objective.yield_net.v1", penalties={"ws_writes": 0.02}), observers=[ref("observer.descriptor.v1", action_scale=2, yield_scale=40)],
                          seed_policy={"base": 1, "n_seeds": 3}, budget={"episodes": 2, "horizon": 32, "batch": batch})
    sel = ref("selector.map_elites.v1", n=6, representation="statemachine.v2")
    a = SR.evolve(template(0), sel, generations=3, workdir=tmp_path / "scalar", seed=5)
    b = SR.evolve(template(8), sel, generations=3, workdir=tmp_path / "batched", seed=5)
    assert a["generations_done"] == b["generations_done"] == 3
    key = lambda rows: [(r["gen"], r["player_hash"], r["objective"], tuple(r["descriptor"])) for r in rows if r["kind"] == "elite"]
    ra = SR.load_rows(tmp_path / "scalar" / "archive.jsonl"); rb = SR.load_rows(tmp_path / "batched" / "archive.jsonl")
    assert key(ra) == key(rb) and len(key(ra)) == 18
    gen_b = read_all(sorted((tmp_path / "batched").glob("gen_*_a*.jsonl"))[0])
    assert all(r["execution"]["batched"] for r in gen_b if r["arm"] != "SUMMARY")            # the batch path really ran under the search


def test_series_artifacts_agree_across_paths(tmp_path):
    """C106: the random property never crosses the inline/artifact boundary (<= 120 records); this does (800)."""
    exp = _exp(n_seeds=2, start_charge=100000); exp.budget = dict(exp.budget, episodes=4, horizon=200); exp.controls = []
    _, S = _run(exp, 0, tmp_path, "s.jsonl"); _, B = _run(exp, 4, tmp_path, "b.jsonl")
    for k in S:
        s, b = S[k]["series"]["observer.series.v1"], B[k]["series"]["observer.series.v1"]
        assert s["status"] == b["status"] == "PRESENT" and "artifact" in s and s["series_hash"] == b["series_hash"] and s["artifact"] == b["artifact"], k
    assert (tmp_path / "artifacts").exists() and len(list((tmp_path / "artifacts").glob("series_*.json"))) >= 1


def test_delay_and_permute_wrappers_agree_across_paths_including_exp001(tmp_path):
    """C111: EXP-001 (the delay sweep) could not batch before; now its 96 runs batch and equal the scalar path."""
    from prometheus.toolbox.examples.exp_001_delay_sweep import build
    for name, wrappers in (("delay", {"observation_delay": 2}), ("permute", {"observation_permute": 7}), ("both", {"observation_delay": 1, "observation_permute": 3})):
        _, S = _run(_exp(n_seeds=3, wrappers=wrappers), 0, tmp_path, name + "_s.jsonl"); _, B = _run(_exp(n_seeds=3, wrappers=wrappers), 4, tmp_path, name + "_b.jsonl")
        assert all(B[k]["execution"]["batched"] for k in B) and all(S[k]["trace_hashes"] == B[k]["trace_hashes"] and S[k]["science"] == B[k]["science"] for k in S), name
    e = build(); _, S = _run(e, 0, tmp_path, "e1s.jsonl"); _, B = _run(e, 6, tmp_path, "e1b.jsonl")
    assert len(S) == 96 and sum(1 for k in B if B[k]["execution"]["batched"]) == 96
    assert all(S[k]["trace_hashes"] == B[k]["trace_hashes"] and S[k]["science"] == B[k]["science"] for k in S)
    # the manifest names the wrappers on the batched receipt too
    assert any(B[k]["components"]["world"]["manifest"].get("wrappers", {}).get("observation_delay") for k in B)


# ------------------------------------------------------------------------------------------ env independence (C116, metamorphic)
@pytest.mark.parametrize("params", [dict(), dict(regime_period=3, stoch_rate=2, action_delay=1), dict(n_players=2, start_charge=5)])
def test_batch_envs_do_not_leak_into_each_other(params):
    """An env's trace depends on its own seed and actions only: permuting the env order permutes the traces; replacing
    the OTHER envs' seeds and actions leaves an env's trace unchanged; an abandoned neighbour changes nothing."""
    from prometheus.toolbox.ref.worlds_integer_batch import IntegerWorldBatch
    p = dict(world_seed=5, n_players=1, horizon=25); p.update(params); n = p["n_players"]
    def run(seeds, acts_by_env, abandon_at=None):
        w = IntegerWorldBatch(n_envs=len(seeds), **p); w.reset_batch(list(seeds)); done = [False] * len(seeds)
        for t in range(25):
            acts = [None if (abandon_at is not None and i == abandon_at[0] and t >= abandon_at[1]) else acts_by_env[i](t) for i in range(len(seeds))]
            d = w.step_batch(acts); done = [a or b for a, b in zip(done, d)]
            if all(done):
                break
        return w.trace_hashes()
    A = lambda k: (lambda t: {pid: [(t + k + pid) % 8, (2 * t + k) % 8] for pid in range(n)})
    base = run([1, 2, 3], [A(0), A(1), A(2)])
    perm = run([3, 1, 2], [A(2), A(0), A(1)])
    assert perm == [base[2], base[0], base[1]]
    other = run([1, 9, 8], [A(0), A(7), A(5)])
    assert other[0] == base[0] and other[1] != base[1]
    aband = run([1, 2, 3], [A(0), A(1), A(2)], abandon_at=(1, 1))      # tick 1: before a 5-charge player can have died
    assert aband[0] == base[0] and aband[2] == base[2] and aband[1] != base[1]


# ------------------------------------------------------------------------------------------ crash mid-batch (C118)
def test_a_crash_between_two_receipts_of_one_batch_resumes_to_a_clean_result(tmp_path, monkeypatch):
    """A batch's receipts are written one by one after the batch ran; a crash after k of them leaves k valid rows
    (the scan is clean, nothing partial) and resume redoes exactly the missing runs -- the final file equals a
    clean run on every science field, with the resumed runs' receipts written on the SECOND execution."""
    from prometheus.toolbox import receipt as RC
    from prometheus.toolbox.backends import local as L
    e = _exp(n_seeds=6); e.budget = dict(e.budget, batch=4); e.controls = []
    job = L.lower(e, REG).job; assert len(job.runs) == 7
    real = RC.ReceiptWriter.write; calls = {"n": 0}

    def crashing(self, r):
        calls["n"] += 1
        if calls["n"] == 3:                                            # after 2 receipts of the first batch of 4
            raise KeyboardInterrupt("simulated crash mid-batch")
        return real(self, r)
    monkeypatch.setattr(RC.ReceiptWriter, "write", crashing)
    with pytest.raises(KeyboardInterrupt):
        L.execute(job, tmp_path / "j.jsonl", REG)
    monkeypatch.setattr(RC.ReceiptWriter, "write", real)
    sc = RC.scan(tmp_path / "j.jsonl"); assert sc["valid"] == 2 and not sc["defects"], sc
    rep = L.execute(job, tmp_path / "j.jsonl", REG, resume=True)
    assert rep.valid and rep.resumed_runs == 2 and rep.n_completed == 7
    rows = {r["seed"]: r for r in read_all(tmp_path / "j.jsonl") if r["arm"] != "SUMMARY"}
    clean = L.execute(L.lower(e, REG).job, tmp_path / "clean.jsonl", REG)
    crow = {r["seed"]: r for r in read_all(tmp_path / "clean.jsonl") if r["arm"] != "SUMMARY"}
    assert len(rows) == 7 and all(rows[s]["trace_hashes"] == crow[s]["trace_hashes"] and rows[s]["science"] == crow[s]["science"] for s in crow)
    # the two kept receipts still say batch_size 4 (their batch); the resume regroups the 5 remaining runs as 4 + 1
    assert sorted(r["execution"]["batch_size"] for r in rows.values()) == [1, 4, 4, 4, 4, 4, 4]


# ------------------------------------------------------------------------------------------ wall budget (C145)
@pytest.mark.parametrize("seed", list(range(1800, 1830)))
def test_wall_budget_stops_between_runs_and_resume_finishes_identically(tmp_path, seed):
    """A tiny wall budget stops the job BETWEEN runs (or batches): every written receipt is complete, the summary
    names the reason and the count not started, and resume=True finishes to exactly the unbudgeted rows -- on the
    scalar path and the batched one."""
    from prometheus.toolbox.tests.test_fuzz import random_experiment
    from prometheus.toolbox.backends.local import lower
    e = random_experiment(seed)
    if e.validate():
        return
    low = lower(e, REG)
    if not low.ok or len(low.job.runs) < 3:
        return
    batch = 3 if seed % 2 else 0
    eb = Experiment.from_dict(e.to_dict()); eb.budget = dict(eb.budget, batch=batch, wall_s=1e-9)
    rep = execute(lower(eb, REG).job, tmp_path / "w.jsonl", REG)
    rows = [r for r in read_all(tmp_path / "w.jsonl") if r["arm"] != "SUMMARY"]; summ = [r for r in read_all(tmp_path / "w.jsonl") if r["arm"] == "SUMMARY"][0]
    assert rep.runs_not_started > 0 and summ["engineering"]["stopped_reason"] == "WALL_BUDGET_EXHAUSTED" and summ["engineering"]["runs_not_started"] == rep.runs_not_started
    assert len(rows) + rep.runs_not_started == len(low.job.runs) and all(r["status"] in ("COMPLETED", "FAILED") for r in rows) and not rep.valid
    ec = Experiment.from_dict(e.to_dict()); ec.budget = dict(ec.budget, batch=batch)
    rep2 = execute(lower(ec, REG).job, tmp_path / "w.jsonl", REG, resume=True)
    assert rep2.runs_not_started == 0 and rep2.resumed_runs == len(rows)
    clean = execute(lower(ec, REG).job, tmp_path / "c.jsonl", REG)
    key = lambda r: (r["arm"], json.dumps(r["sweep_point"], sort_keys=True), r["seed"])
    A = {key(r): r for r in read_all(tmp_path / "w.jsonl") if r["arm"] != "SUMMARY"}; B = {key(r): r for r in read_all(tmp_path / "c.jsonl") if r["arm"] != "SUMMARY"}
    assert set(A) == set(B) and all(A[k]["trace_hashes"] == B[k]["trace_hashes"] and A[k]["status"] == B[k]["status"] for k in B), seed
