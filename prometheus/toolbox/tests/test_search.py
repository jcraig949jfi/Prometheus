"""Search ABOVE the execution kernel (directive s18; overnight C26): a Selector proposes players from ARCHIVE
ROWS, the kernel runs them as an ordinary Experiment (players as a sweep axis), receipts are ingested back into
rows. Critical search state never lives only in process memory: a run stopped after any generation resumes
from the rows alone and reaches the same archive as an uninterrupted run."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox import search as SR

REG = default_registry()


def template() -> Experiment:
    return Experiment(family="search_probe", world=ref("world.integer.v1", world_seed=8, start_charge=30, yield_amt=10), substrate=ref("substrate.flat.v1"),
                      players=[], objective=ref("objective.yield_net.v1"), observers=[ref("observer.descriptor.v1")],
                      seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 24})


def _rows_key(rows):
    return [(r["gen"], r["fingerprint"], r["objective"], tuple(r["descriptor"])) for r in rows if r["kind"] == "elite"]


def test_point_mutation_transform_changes_exactly_one_cell():
    spec = random_statemachine(4)
    mut = REG.make("transform.point_mutation.v1").apply(spec, 5)
    diff = [(i, j) for i, row in enumerate(spec.payload["table"]) for j, c in enumerate(row) if c != mut.payload["table"][i][j]]
    assert len(diff) == 1 and mut.meta["transform"] == "transform.point_mutation.v1"


def test_evolve_writes_rows_per_generation_and_resumes_from_them_identically(tmp_path):
    full = SR.evolve(template(), ref("selector.truncation.v1", keep=3, n=6), generations=4, workdir=tmp_path / "full", seed=11)
    assert full["generations_done"] == 4 and (tmp_path / "full" / "archive.jsonl").exists()
    part = SR.evolve(template(), ref("selector.truncation.v1", keep=3, n=6), generations=2, workdir=tmp_path / "part", seed=11)
    assert part["generations_done"] == 2
    resumed = SR.evolve(template(), ref("selector.truncation.v1", keep=3, n=6), generations=4, workdir=tmp_path / "part", seed=11)   # same workdir: RESUME
    assert resumed["resumed_from_gen"] == 2 and resumed["generations_done"] == 4
    assert _rows_key(SR.load_rows(tmp_path / "full" / "archive.jsonl")) == _rows_key(SR.load_rows(tmp_path / "part" / "archive.jsonl"))


def test_a_generation_interrupted_after_some_rows_is_abandoned_and_rerun(tmp_path, monkeypatch):
    """The crash lands AFTER gen 1's elite rows were appended but BEFORE its GEN_DONE marker (the worst case:
    plausible-looking rows with no commitment). Resume must ignore them, mark them abandoned, rerun gen 1,
    and the committed view must hold exactly n elites per generation."""
    real = SR._append

    def crash_on_marker(path, row):
        if row.get("kind") == "GEN_DONE" and row.get("gen") == 1:
            raise RuntimeError("simulated crash before committing generation 1")
        return real(path, row)
    monkeypatch.setattr(SR, "_append", crash_on_marker)
    with pytest.raises(RuntimeError):
        SR.evolve(template(), ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "w", seed=3)
    rows = SR.load_rows(tmp_path / "w" / "archive.jsonl")
    assert [r["gen"] for r in rows if r["kind"] == "GEN_DONE"] == [0] and sum(1 for r in rows if r["kind"] == "elite" and r["gen"] == 1) == 4
    monkeypatch.setattr(SR, "_append", real)
    out = SR.evolve(template(), ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "w", seed=3)
    rows = SR.load_rows(tmp_path / "w" / "archive.jsonl")
    assert out["resumed_from_gen"] == 1 and [r["gen"] for r in rows if r["kind"] == "GEN_DONE"] == [0, 1, 2]
    assert [r["gen"] for r in rows if r["kind"] == "GEN_ABANDONED"] == [1]
    committed = SR.committed_rows(rows)
    assert sorted(r["gen"] for r in committed) == [0] * 4 + [1] * 4 + [2] * 4
    # and the committed view equals an uninterrupted run's
    SR.evolve(template(), ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "clean", seed=3)
    assert _rows_key(committed) == _rows_key(SR.committed_rows(SR.load_rows(tmp_path / "clean" / "archive.jsonl")))


def test_map_elites_selector_keeps_one_elite_per_descriptor_cell(tmp_path):
    out = SR.evolve(template(), ref("selector.map_elites.v1", n=8), generations=3, workdir=tmp_path / "me", seed=5)
    rows = [r for r in SR.load_rows(tmp_path / "me" / "archive.jsonl") if r["kind"] == "elite"]
    cells = SR.elites_by_cell(rows)
    assert cells and all(len(v) == 1 for v in cells.values()) and out["generations_done"] == 3


# C27 (playtest D rows): a row's descriptor came from the FIRST seed only while its objective was the mean over
# seeds -- a cell key that contradicted its own objective. Descriptors aggregate element-wise (floor(mean+0.5))
# and every seed's descriptor is kept on the row.
def test_row_descriptor_aggregates_over_seeds_and_keeps_each_seed():
    fake = []
    for seed, desc, obj in ((1, [0, 7, 0], 0.0), (2, [0, 7, 7], 320.0)):
        fake.append({"arm": "primary", "status": "COMPLETED", "sweep_point": {"players": [{"x": 1}]}, "science": {"observations": {"observer.descriptor.v1": {"descriptor": desc}},
                     "player_fingerprints": {"0": {"hash": "abc", "silent": False}}, "objective": {"value": obj}}, "receipt_id": "r%d" % seed, "seed": seed,
                     "_player_manifest": {"x": 1}})
    rows = SR._rows_from_receipts(fake)
    assert len(rows) == 1 and rows[0]["descriptor"] == [0, 7, 4] and rows[0]["descriptors"] == [[0, 7, 0], [0, 7, 7]] and rows[0]["objective"] == 160.0


# C69: a wall budget that stops a generation midway must NOT let that generation be committed with fewer rows
# than proposals; evolve stops without a marker and reports why; the next call reruns the generation.
def test_wall_budget_inside_a_generation_leaves_it_uncommitted(tmp_path):
    t = template(); t.budget = dict(t.budget, wall_s=0.0)
    out = SR.evolve(t, ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "wb", seed=3)
    assert out["generations_done"] == 0 and out["stopped"] == "WALL_BUDGET_EXHAUSTED"
    rows = SR.load_rows(tmp_path / "wb" / "archive.jsonl")
    assert not any(r["kind"] == "GEN_DONE" for r in rows)
    t2 = template()
    out2 = SR.evolve(t2, ref("selector.truncation.v1", keep=2, n=4), generations=2, workdir=tmp_path / "wb", seed=3)
    assert out2["generations_done"] == 2 and [r["gen"] for r in SR.load_rows(tmp_path / "wb" / "archive.jsonl") if r["kind"] == "GEN_DONE"] == [0, 1]


# C73: playtest D had to SUBCLASS the selector to evolve statemachine.v2 (gen-0 proposals were hard-wired to v1).
# Selectors take `representation`; gen-0 draws from that representation's registered generator.
def test_selectors_evolve_any_registered_representation(tmp_path):
    for rep in ("statemachine.v2", "statemachine.v3", "rewrite.v1"):
        out = SR.evolve(template(), ref("selector.map_elites.v1", n=4, representation=rep), generations=2, workdir=tmp_path / rep, seed=2)
        rows = SR.committed_rows(SR.load_rows(tmp_path / rep / "archive.jsonl"))
        assert out["generations_done"] == 2 and rows and all(r["player"]["representation"] == rep for r in rows), rep


# C96 (playtest H): 11 DISTINCT players (different tables, different objectives, different descriptor cells) shared one
# "fingerprint" -- the behavioural probe (16 fixed observations) has little resolving power for a state machine, so
# rows keyed by it read as 14 elites where there were 40. Identity is the SPEC hash; the probe hash is a behavioural
# CLASS, kept and named as such.
def test_rows_carry_spec_identity_and_behavioural_class_separately(tmp_path):
    from prometheus.toolbox.ref.players import random_statemachine_v2, fingerprint_by_probe
    from prometheus.toolbox.contracts import component_manifest_hash
    sub = REG.make("substrate.kv.v1"); base = random_statemachine_v2(1); fp0 = fingerprint_by_probe(sub.instantiate(base, 1))
    twin = None
    for s in range(400):                                                   # a point mutation the probe cannot see
        cand = REG.make("transform.point_mutation.v1").apply(base, s)
        if cand.payload["table"] != base.payload["table"] and fingerprint_by_probe(sub.instantiate(cand, 1)) == fp0:
            twin = cand; break
    assert twin is not None, "no probe-blind mutation in 400 tries: the probe got stronger, revisit this test"
    t = template(); t.players = []; t.world["params"]["n_players"] = 1
    t.substrate = ref("substrate.kv.v1")
    from prometheus.toolbox.search import _run_generation, _rows_from_receipts
    receipts = _run_generation(t, [base, twin], 0, 5, tmp_path, REG)
    rows = _rows_from_receipts(receipts)
    assert len(rows) == 2 and rows[0]["fingerprint"] == rows[1]["fingerprint"] == fp0
    assert rows[0]["player_hash"] != rows[1]["player_hash"]
    assert {r["player_hash"] for r in rows} == {component_manifest_hash(base.manifest()), component_manifest_hash(twin.manifest())}
    prim = [r for r in receipts if r["arm"] == "primary"][0]
    assert prim["science"]["player_fingerprints"]["0"]["spec_hash"] == prim["components"]["players"][0]["manifest_hash"]
    assert set(prim["science"]["player_fingerprints"]["0"]) == {"hash", "silent", "spec_hash"}


# C104: "evolution must use generations" -- a STEADY STATE is the same machinery with one proposal per commit:
# every evaluation is its own committed unit, resumable at any point, and the archive reads the same whether the
# ten evaluations ran in one process or in three. An expression, not a new mechanism (like turn-taking, C72).
def test_steady_state_search_is_one_proposal_per_commit_and_resumes_anywhere(tmp_path):
    sel = ref("selector.truncation.v1", keep=2, n=1)
    one = SR.evolve(template(), sel, generations=10, workdir=tmp_path / "one", seed=4)
    assert one["generations_done"] == 10
    for stop in (3, 7, 10):
        r = SR.evolve(template(), sel, generations=stop, workdir=tmp_path / "three", seed=4)
        assert r["generations_done"] == stop
    a = SR.load_rows(tmp_path / "one" / "archive.jsonl"); b = SR.load_rows(tmp_path / "three" / "archive.jsonl")
    assert _rows_key(a) == _rows_key(b) and len(_rows_key(a)) == 10
    assert [r["n"] for r in a if r["kind"] == "GEN_DONE"] == [1] * 10          # one evaluation per committed unit


# C115 (soak design note): archive rows carried the full player manifest (~0.9 KB on disk, ~9 KB in memory each); a
# 100k-row archive would need ~1 GB to resume from. A COMPACT archive keeps identity (player_hash), the receipt ids
# and the generation FILE the player came from; the manifest is fetched on demand from that file's receipt
# (its sweep point IS the player). Same search, same rows, smaller archive.
def test_compact_archive_evolves_identically_and_fetches_players_on_demand(tmp_path):
    sel = ref("selector.map_elites.v1", n=6)
    full = SR.evolve(template(), sel, generations=3, workdir=tmp_path / "full", seed=11)
    comp = SR.evolve(template(), sel, generations=3, workdir=tmp_path / "compact", seed=11, compact=True)
    assert full["generations_done"] == comp["generations_done"] == 3
    fr = SR.load_rows(tmp_path / "full" / "archive.jsonl"); cr = SR.load_rows(tmp_path / "compact" / "archive.jsonl")
    key = lambda rows: [(r["gen"], r["player_hash"], r["objective"], tuple(r["descriptor"])) for r in rows if r["kind"] == "elite"]
    assert key(fr) == key(cr) and len(key(cr)) == 18
    assert all("player" not in r for r in cr if r["kind"] == "elite") and all(r["source"]["file"].startswith("gen_") for r in cr if r["kind"] == "elite")
    assert (tmp_path / "compact" / "archive.jsonl").stat().st_size < 0.4 * (tmp_path / "full" / "archive.jsonl").stat().st_size
    fe = [r for r in fr if r["kind"] == "elite"]; ce = [r for r in cr if r["kind"] == "elite"]
    for a, b in zip(fe, ce):
        assert SR.player_of(b, tmp_path / "compact") == a["player"] == SR.player_of(a, tmp_path / "full")
    # resume from the compact archive: the selector fetches parents on demand and the rows continue identically
    more_full = SR.evolve(template(), sel, generations=5, workdir=tmp_path / "full", seed=11)
    more_comp = SR.evolve(template(), sel, generations=5, workdir=tmp_path / "compact", seed=11, compact=True)
    assert more_full["resumed_from_gen"] == more_comp["resumed_from_gen"] == 3
    assert key(SR.load_rows(tmp_path / "full" / "archive.jsonl")) == key(SR.load_rows(tmp_path / "compact" / "archive.jsonl"))
    # a compact row whose file is gone is an honest error, not a silent fresh player
    (tmp_path / "compact" / ce[0]["source"]["file"]).unlink()
    with pytest.raises(FileNotFoundError):
        SR.player_of(ce[0], tmp_path / "compact")


# C125: the search layer's invariants as a PROPERTY over random templates and selectors: one process vs resumed
# (1 + 2 generations) vs compact archive must give identical rows; a vector objective gets a rank (or pareto);
# a template the kernel refuses is skipped, never a crash.
_SEARCH_COVERAGE = {"exercised": 0}


@pytest.mark.parametrize("seed", list(range(400, 440)))
def test_search_invariants_over_random_templates(tmp_path, seed):
    import random
    from prometheus.toolbox.tests.test_fuzz import random_experiment
    from prometheus.toolbox.backends.local import lower
    rnd = random.Random(seed)
    t = random_experiment(seed)
    if t.validate():
        return
    # a random IR made into a search TEMPLATE: one player slot, an objective, a horizon the search can see
    t.players = []; t.sweep = {}; t.controls = []; t.interventions = [iv for iv in t.interventions if "schedule" not in iv]
    t.world["params"]["n_players"] = 1
    t.objective = t.objective or ref("objective.yield_net.v1"); t.budget = dict(t.budget, horizon=max(int(t.budget["horizon"]), 6))
    if "observer.descriptor.v1" not in [o["kind"] for o in t.observers]:
        t.observers = list(t.observers) + [ref("observer.descriptor.v1")]
    rep = rnd.choice(["statemachine.v1", "statemachine.v2"])
    probe = Experiment.from_dict(t.to_dict()); probe.players = [random_statemachine(1).manifest() if rep == "statemachine.v1" else __import__("prometheus.toolbox.ref.players", fromlist=["x"]).random_statemachine_v2(1).manifest()]
    if not lower(probe, REG).ok:
        return
    vector = t.objective["kind"] == "objective.multi.v1"
    if vector:
        comp = rnd.choice(sorted(t.objective["params"]["components"]))
        sel = rnd.choice([ref("selector.truncation.v1", keep=2, n=3, representation=rep, rank=comp), ref("selector.map_elites.v1", n=3, representation=rep, rank=comp),
                          ref("selector.pareto.v1", n=3, representation=rep), ref("selector.pareto.v1", n=3, representation=rep, by_cell=True)])
    else:
        sel = rnd.choice([ref("selector.truncation.v1", keep=2, n=3, representation=rep), ref("selector.map_elites.v1", n=3, representation=rep), ref("selector.pareto.v1", n=3, representation=rep)])
    key = lambda rows: [(r["gen"], r["player_hash"], r["objective"], tuple(r["descriptor"])) for r in rows if r["kind"] == "elite"]
    one = SR.evolve(t, sel, generations=3, workdir=tmp_path / "one", seed=seed)
    if one["stopped"]:
        return
    _SEARCH_COVERAGE["exercised"] += 1
    SR.evolve(t, sel, generations=1, workdir=tmp_path / "two", seed=seed); SR.evolve(t, sel, generations=3, workdir=tmp_path / "two", seed=seed)
    SR.evolve(t, sel, generations=3, workdir=tmp_path / "compact", seed=seed, compact=True)
    a, b, c = (SR.load_rows(tmp_path / d / "archive.jsonl") for d in ("one", "two", "compact"))
    assert key(a) == key(b) == key(c) and len(key(a)) == 9, (seed, sel)
    assert all("player" not in r for r in c if r["kind"] == "elite")


def test_the_search_property_was_actually_exercised():
    assert _SEARCH_COVERAGE["exercised"] >= 12, _SEARCH_COVERAGE


# C148: a FAILED run inside a generation. Before: KeyError in row ingestion after the receipts were written -> no
# GEN_DONE -> abandoned and re-run on the next resume, forever. Now the row carries the failure (objective None,
# failed_seeds, errors) and the generation commits; selectors ignore the row through its None objective. Also:
# selectors resolved generators/transforms in the PROCESS-GLOBAL registry (C97b's hole in the search layer).
def test_a_failing_player_becomes_a_failed_row_and_the_generation_commits(tmp_path):
    from prometheus.toolbox.registry import ComponentRecord
    from prometheus.toolbox.ref.substrates import KVSubstrate
    from prometheus.toolbox.contracts import PlayerSpec
    failed = {"arm": "primary", "status": "FAILED", "sweep_point": {"players": [{"representation": "x", "payload": {}}]}, "science": {}, "receipt_id": "abc", "seed": 1,
              "_player_manifest": {"representation": "x", "payload": {}}, "_file": "gen_000_a0.jsonl", "error": "RuntimeError: boom"}
    rows = SR._rows_from_receipts([failed])
    assert len(rows) == 1 and rows[0]["objective"] is None and rows[0]["failed_seeds"] == [1] and "boom" in rows[0]["errors"][0] and rows[0]["player_hash"]

    class Bomb:
        kind = "bomb"; version = 1
        def __init__(self, seed): self.seed = seed; self.n = 0
        def act(self, obs, space):
            self.n += 1
            if self.seed % 2 == 0 and self.n == 3:
                raise RuntimeError("bomb %d" % self.seed)
            return [1] * space.width
        def adapt(self, *a, **k): pass
        def cost(self): return {}
        def fingerprint(self): return "bomb%d" % self.seed
        def snapshot(self): return b""
        def restore(self, b): pass

    def gen_bomb(seed, meta=None):
        return PlayerSpec("bomb.v1", {"seed": seed}, {}, frozenset(), dict(meta or {}, seed=seed))

    class KVWithBombs(KVSubstrate):
        kind = "substrate.kv_bombs.v1"; representations = KVSubstrate.representations | {"bomb.v1"}
        def instantiate(self, spec, seed):
            return Bomb(spec.payload["seed"]) if spec.representation == "bomb.v1" else KVSubstrate.instantiate(self, spec, seed)
    R = REG.fork()
    R.register(ComponentRecord("bomb.v1", "representation", gen_bomb, frozenset({"core.player.v1"}), route="write", provenance={"author": "test"}, license="repository"))
    R.register(ComponentRecord("substrate.kv_bombs.v1", "substrate", KVWithBombs, KVSubstrate.capabilities, route="write", provenance={"author": "test"}, license="repository"))
    t = template(); t.substrate = ref("substrate.kv_bombs.v1"); t.seed_policy = {"base": 1, "n_seeds": 1}
    out = SR.evolve(t, ref("selector.truncation.v1", keep=2, n=4, representation="bomb.v1", mutation="transform.shuffle.v1"), generations=2, workdir=tmp_path / "b", seed=2, registry=R)
    assert out["generations_done"] == 2
    rows = SR.load_rows(tmp_path / "b" / "archive.jsonl")
    assert [r["gen"] for r in rows if r["kind"] == "GEN_DONE"] == [0, 1] and not [r for r in rows if r["kind"] == "GEN_ABANDONED"]
    elites = [r for r in rows if r["kind"] == "elite"]
    assert elites and any(r["failed_seeds"] for r in elites) and any(not r["failed_seeds"] for r in elites)
    assert all((r["objective"] is None) == bool(r["failed_seeds"]) for r in elites)


# C149: a template whose lowering is refused (a required capability nobody provides) crashed evolve with an
# AttributeError on a None job. Now: a stopped search carrying the lowering status and reasons, nothing written.
def test_a_refused_lowering_stops_the_search_with_the_reasons(tmp_path):
    t = template(); t.required_capabilities = frozenset({"ext.physics2d.v1"})
    out = SR.evolve(t, ref("selector.truncation.v1", n=3), generations=2, workdir=tmp_path / "r", seed=1)
    assert out["generations_done"] == 0 and out["stopped"] == "BLOCKED_MISSING_CAPABILITY" and "ext.physics2d.v1" in out["detail"]
    assert not (tmp_path / "r" / "archive.jsonl").exists() or not [r for r in SR.load_rows(tmp_path / "r" / "archive.jsonl") if r["kind"] == "elite"]
