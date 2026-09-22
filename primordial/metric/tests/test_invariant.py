"""G-R4-1: the input-invariant learner is E4b's open-loop QD, seeded, at round 1's budget, and resumable."""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pytest

from primordial.metric import floors as F
from primordial.metric import invariant as I
from primordial.qd import e4_run as E4
from primordial.qd import e4b_run as E4B
from primordial.tests._live import live_url

ROOT = pathlib.Path(__file__).resolve().parents[3]


@pytest.fixture
def r():
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    yield c
    for k in c.scan_iter("pm:qd:g-r4-inv-*", count=5000):
        c.delete(k)


def test_budget_is_round1_open_loop_budget_from_committed_rows():
    rows = {}
    for name in ("E6-heldout-seed-generalisation", "E10-linear-closed-vs-open-128-seeds"):
        p = ROOT / "primordial" / "ledger" / "rows" / "E" / f"{name}.jsonl"
        rows[name] = {json.loads(x)["open_genomes"] for x in p.read_text(encoding="utf-8").splitlines()
                      if x.strip() and json.loads(x).get("tag") == "full"}
    assert rows["E6-heldout-seed-generalisation"] == {np.prod(I.BUDGET["train8_held64"])}
    assert rows["E10-linear-closed-vs-open-128-seeds"] == {np.prod(I.BUDGET["train128_held64"])}


def test_nb_fit_equals_e4b_and_numpy_reference():
    spec = E4.Spec(4)
    G = E4.init_genomes(np.random.Generator(np.random.PCG64(3)), spec, 12)
    seeds = F.HELD64[:5]
    with I.e4_seeds(seeds):
        assert np.array_equal(I.nb_fit(spec, G, seeds), E4B.nb_evaluate(spec, G))
        assert np.array_equal(I.nb_fit(spec, G, seeds), E4.evaluate(spec, G)[0])
    assert np.array_equal(E4.SEEDS, np.arange(9100, 9108))          # the global is restored


def test_open_loop_genome_is_input_invariant():
    # the same action tensor is played on every seed: the numba world replays exactly the actions given,
    # checked episode by episode against wforge with the genome's own actions (no observation input exists)
    spec = E4.Spec(1)
    G = E4.init_genomes(np.random.Generator(np.random.PCG64(5)), spec, 2)
    o = I.oracle_top(1, G, F.HELD64[:2])
    assert o["elites_failing"] == 0 and o["nb_np_fitness_equal"]


def test_run_is_replayable_and_saves_elites(r, tmp_path):
    a = I.learner_run(r, 4, "train8_held64", 0, gens=3, batch=8, elites_dir=tmp_path / "a")
    b = I.learner_run(r, 4, "train8_held64", 0, gens=3, batch=8, elites_dir=tmp_path / "b")
    assert a["held64_per_seed"] == b["held64_per_seed"] and a["top_sha256"] == b["top_sha256"]
    assert pathlib.Path(a["elites"]).read_bytes() == pathlib.Path(b["elites"]).read_bytes()
    assert not a["budget_ok"] and a["genomes"] == 24 and a["top"] <= I.TOP
    c = I.learner_run(r, 4, "train8_held64", 1, gens=3, batch=8, elites_dir=tmp_path / "c")
    assert c["top_sha256"] != a["top_sha256"]


def test_pause_and_resume_equals_uninterrupted(r, tmp_path, monkeypatch):
    monkeypatch.setattr(I, "PAUSE_EVERY", 2)
    whole = I.learner_run(r, 4, "train8_held64", 2, gens=5, batch=8, elites_dir=tmp_path / "w")
    first = I.learner_run(r, 4, "train8_held64", 2, gens=5, batch=8, elites_dir=tmp_path / "p",
                          should_pause=lambda: True)
    assert "paused" in first and first["paused"]["gen"] == 2
    state = json.loads(json.dumps(first["paused"], default=int))        # survives a round trip (pickled in F9)
    rest = I.learner_run(r, 4, "train8_held64", 2, gens=5, batch=8, elites_dir=tmp_path / "p",
                         should_pause=lambda: False, state=first["paused"])
    assert state["gen"] == 2
    assert rest["top_sha256"] == whole["top_sha256"] and rest["held64_per_seed"] == whole["held64_per_seed"]
    assert pathlib.Path(rest["elites"]).read_bytes() == pathlib.Path(whole["elites"]).read_bytes()


def test_floor_part_is_median_over_at_least_eight_run_seeds():
    assert I.floor_part([1, 2, 3, 4, 5, 6, 7, 100]) == 4.5
    with pytest.raises(ValueError):
        I.floor_part([1, 2, 3, 4, 5, 6, 7])


class FakeCtx:
    def __init__(self, pause_after=None):
        self.rows, self.ck, self.pause_after, self.polls = [], None, pause_after, 0

    def emit(self, row):
        self.rows.append(json.loads(json.dumps(row)))

    def load_checkpoint(self):
        return self.ck

    def should_pause(self):
        self.polls += 1
        return self.pause_after is not None and self.polls >= self.pause_after

    def pause(self, state):
        import pickle
        self.ck = pickle.loads(pickle.dumps(state))
        raise RuntimeError("paused")


def test_job_emits_runs_then_floor_row_and_resumes(r, tmp_path, monkeypatch):
    monkeypatch.setattr(I, "PAUSE_EVERY", 2)
    kw = dict(cells=[[4, "train8_held64"]], gens=3, batch=8, archive_url=live_url(), elites_dir=str(tmp_path))
    ref = FakeCtx()
    I.job(ref, **kw)
    assert [x["kind"] for x in ref.rows] == ["run"] * 8 + ["floor_invariant"]
    assert ref.rows[0]["oracle_held8"]["elites_failing"] == 0
    fl = ref.rows[-1]
    assert fl["invariant_held64_median"] == float(np.median(fl["held64_by_run_seed"])) and fl["status"] == "control"

    ctx = FakeCtx(pause_after=3)
    with pytest.raises(RuntimeError):
        I.job(ctx, **kw)
    ctx.pause_after = None
    I.job(ctx, **kw)
    got = [x for x in ctx.rows]

    def strip(x):
        x = {k: v for k, v in x.items() if k not in ("qd_wall_s", "elites")}
        if "oracle_held8" in x:
            x["oracle_held8"] = {k: v for k, v in x["oracle_held8"].items() if k != "wforge_episodes_per_s"}
        return x
    assert [strip(x) for x in got] == [strip(x) for x in ref.rows]
