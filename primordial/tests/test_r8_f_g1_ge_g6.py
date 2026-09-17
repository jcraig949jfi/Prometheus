"""R8 BUILD, TRACK-1 (F, envelope.py): G1 row vocabulary LOUD-FAIL (D29), GE gate enforcement at admission, G6
open_candidate (D27). Each test is aimed at the claim in BUILD_R8 / prompts_bld_r8/F.md, not beside it."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
LANE = "F-r8-g1"
TAG = "t-r8-f"
ALL_LANDED = {g: "landed" for g in ("G8", "G1", "GE", "G6", "G5", "G7", "G2", "G3", "G4", "C1", "C2", "C3")}
NOW = 1_800_000_000.0
LIVE = {"round_id": "r8", "stage": "PRODUCTION", "start_ts": NOW - 60, "epoch_s": 3600.0, "epochs": 12,
        "no_new_work_ts": NOW + 40000, "drain_ts": NOW + 41800, "end_ts": NOW + 43600}


# ------------------------------------------------------------------ job functions run by the REAL worker

def emit_r7_shape(ctx, n: int = 4):
    """Round 7's D29 shape: a job whose rows carry evidence_class OBSERVATION and status 'observation'."""
    for i in range(n):
        ctx.emit(EV.prepare_row({"status": "observation", "evidence_class": "OBSERVATION", "i": i}, i))


def emit_bare_r7_shape(ctx, n: int = 4):
    """The ACTUAL D29 shape: bare ctx.emit, no prepare_row in the job. Covered only by the worker's emit hook."""
    for i in range(n):
        ctx.emit({"status": "observation", "evidence_class": "OBSERVATION", "i": i})


def emit_bare_good(ctx, n: int = 3):
    for i in range(n):
        ctx.emit({"status": "record", "i": i})


def emit_good(ctx, n: int = 3):
    for i in range(n):
        ctx.emit(EV.prepare_row({"status": "record", "evidence_class": "OBSERVATION", "i": i}, i))


# ------------------------------------------------------------------ G1 unit: refusal names value AND index, no alias

def test_g1_refusal_names_offending_value_and_row_index():
    got = EV.check_rows([{"status": "record"}, {"status": "observation"}, {"status": "dev", "evidence_class": "obs"}])
    assert len(got) == 2
    assert got[0].startswith("ROW_VOCABULARY_REFUSED:row 1:") and "'observation'" in got[0]
    assert got[1].startswith("ROW_VOCABULARY_REFUSED:row 2:") and "evidence_class 'obs'" in got[1]
    with pytest.raises(EV.RowRefused) as e:
        EV.prepare_row({"status": "PASS"}, 17)
    assert "row 17" in str(e.value) and "'PASS'" in str(e.value)


@pytest.mark.parametrize("status", ["observation", "OBSERVATION", "Observation", "verdict", "VERDICT", "Record", "",
                                    None])
def test_g1_no_alias_observation_is_not_mapped_onto_a_status(status):
    row = {"evidence_class": "OBSERVATION"} if status is None else {"status": status, "evidence_class": "OBSERVATION"}
    with pytest.raises(EV.RowRefused):
        EV.prepare_row(row, 0)
    assert EV.ROW_STATUSES == ("record", "dev", "aborted", "timeout", "cheat", "control")   # nothing was added


def test_g1_evidence_class_is_exact_and_optional():
    assert EV.vocabulary_reasons({"status": "record"}, 0) == []
    for ec in EV.ROW_EVIDENCE_CLASSES:
        assert EV.vocabulary_reasons({"status": "record", "evidence_class": ec}, 0) == []
    for ec in ("observation", "Verdict", "", None, 1):
        assert EV.vocabulary_reasons({"status": "record", "evidence_class": ec}, 3), ec


def test_g1_prepare_row_stamps_predicate_event_id_and_refuses_a_mismatch():
    env = EV.example(predicate_id="P-1", predicate_event_id="1789564627164-0")
    assert EV.validate(env) == []
    row = EV.prepare_row({"status": "record"}, 0, env)
    assert row["predicate_id"] == "P-1" and row["predicate_event_id"] == "1789564627164-0"
    bare = EV.prepare_row({"status": "record"}, 0, None)
    assert "predicate_event_id" in bare and bare["predicate_event_id"] is None
    with pytest.raises(EV.RowRefused) as e:
        EV.prepare_row({"status": "record", "predicate_event_id": "1-0"}, 5, env)
    assert str(e.value).startswith("ROW_PREDICATE_MISMATCH:row 5:")
    assert EV.validate(EV.example(predicate_event_id="not-an-id")) == ["ENVELOPE_BAD_VALUE:predicate_event_id"]


# ------------------------------------------------------------------ G1 lint

def test_g1_lint_passes_on_the_tree_and_counts_its_checks():
    out = EV.lint_vocabulary()
    assert out["ok"], out["violations"][:5]
    assert out["checks"] > 100                                 # it actually walked the sources


def test_g1_lint_fails_on_tokens_outside_the_frozen_vocabulary(tmp_path):
    src = tmp_path / "job.py"
    src.write_text('def job(ctx):\n'
                   '    ctx.emit({"status": "observation", "evidence_class": "OBSERVATION"})\n'
                   '    ctx.emit({"status": "record", "evidence_class": "observation"})\n'
                   '    ctx.emit({"status": "record", "evidence_class": "VERDICT"})\n', encoding="utf-8")
    rows = tmp_path / "rows.jsonl"
    rows.write_text(json.dumps({"status": "record"}) + "\n" + json.dumps({"status": "observation"}) + "\n",
                    encoding="utf-8")
    out = EV.lint_vocabulary([src], [rows])
    assert not out["ok"] and out["checks"] == 4
    v = out["violations"]
    assert len(v) == 3, v
    assert any(":2:status 'observation'" in x for x in v)
    assert any(":3:evidence_class 'observation'" in x for x in v)
    assert any("row 1:status 'observation'" in x for x in v)
    cli = subprocess.run([sys.executable, "-m", "primordial.fabric.envelope", "lint", str(src), "--rows", str(rows)],
                         capture_output=True, text=True)
    assert cli.returncode == 1 and "checks run: 4" in cli.stdout and "vocabulary lint: FAIL" in cli.stdout


# ------------------------------------------------------------------ G1 through the REAL worker (round-7 shape)

@pytest.fixture
def live(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES, EV.FILED]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", TAG)
    monkeypatch.setenv("PM_LANE", "F")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def test_g1_round7_shape_n_rows_refused_job_is_not_ok(live):
    r, repo = live
    W.submit(LANE, f"{__name__}:emit_r7_shape", "F-R8-D29", "rows/d29.jsonl", 60, {"n": 4}, r=r)
    W.submit(LANE, f"{__name__}:emit_good", "F-R8-ok", "rows/ok.jsonl", 60, {"n": 3}, r=r)
    bad, good = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=2, block_ms=500)
    assert bad["status"] == "error" and bad["status"] != "ok"
    assert bad["rows"] <= 1                                    # only the worker's own job_end row, never a data row
    rows = [json.loads(x) for x in (repo / "rows" / "d29.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(x.get("kind") == "job_end" for x in rows)
    assert "ROW_VOCABULARY_REFUSED:row 0:status 'observation'" in rows[-1]["error"]
    assert good["status"] == "ok" and good["rows"] == 3


def test_g1_bare_ctx_emit_round7_shape_job_is_not_ok_and_rows_carry_predicate_event_id(live):
    r, repo = live
    env = EV.example(predicate_id="P-d29", predicate_event_id="1789564627164-0")
    W.submit(LANE, f"{__name__}:emit_bare_r7_shape", "F-R8-D29-bare", "rows/bare.jsonl", 60, {"n": 4}, r=r,
             envelope=env)
    W.submit(LANE, f"{__name__}:emit_bare_good", "F-R8-bare-ok", "rows/bare_ok.jsonl", 60, {"n": 3}, r=r,
             envelope=env)
    bad, good = W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=2, block_ms=500)
    assert bad["status"] == "error"
    rows = [json.loads(x) for x in (repo / "rows" / "bare.jsonl").read_text(encoding="utf-8").splitlines()]
    assert not any(x.get("i") is not None and x.get("status") == "observation" for x in rows)   # no data row survived
    assert "ROW_VOCABULARY_REFUSED:row 0:status 'observation'" in json.dumps(rows)
    assert good["status"] == "ok" and good["rows"] == 3
    ok_rows = [json.loads(x) for x in (repo / "rows" / "bare_ok.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(ok_rows) == 3 and all(x["predicate_event_id"] == "1789564627164-0" and x["predicate_id"] == "P-d29"
                                     for x in ok_rows)


# ------------------------------------------------------------------ GE: gate enforcement at admission

def test_ge_live_clock_g1_not_landed_refuses_row_emitting_env_exactly():
    v = EV.admit(EV.example(), clock=LIVE, now=NOW, gates=dict(ALL_LANDED, G1="not_landed"))
    assert v["ok"] is False and v["reasons"] == ["GATE_NOT_LANDED:G1"] and v["event"] == EV.GATE_REFUSAL
    assert v["stub"] is False                                  # recorded, not a candidate and not a scientific FAIL


def test_ge_refusal_happens_before_any_simulation_zero_cpu(monkeypatch):
    import primordial.score.evidence_n as EN

    def boom(env):
        raise AssertionError("the gate refusal must precede every later rule")
    monkeypatch.setattr(EN, "admission_reasons", boom)
    v = EV.admit(EV.example(), clock=LIVE, now=NOW, gates=dict(ALL_LANDED, G1="not_landed"))
    assert v["reasons"] == ["GATE_NOT_LANDED:G1"]


def test_ge_all_landed_admits_with_no_gate_reason():
    v = EV.admit(EV.example(campaign_stage="PRODUCTION"), clock=LIVE, now=NOW, gates=ALL_LANDED)
    assert v["ok"] is True and not any("GATE" in x for x in v["reasons"])


@pytest.mark.parametrize("state", [None, {}, {"G1": "yes"}, {"G1": "landed", "G2": ""}])
def test_ge_fails_closed_when_state_missing_or_unreadable(state, monkeypatch):
    monkeypatch.setattr(EV, "GATE_MAP_FILE", "does/not/exist/GATE_MAP_{}.json")
    v = EV.admit(EV.example(), clock=LIVE, now=NOW, gates=state)
    assert v["ok"] is False and v["reasons"] == ["GATE_STATE_UNAVAILABLE"]


def test_ge_fails_closed_on_an_unreadable_redis_hash():
    class Dead:
        def hgetall(self, k):
            raise ConnectionError("down")
    v = EV.admit(EV.example(), clock=LIVE, now=NOW, r=Dead())
    assert v["reasons"] == ["GATE_STATE_UNAVAILABLE"]


def test_ge_reads_the_committed_gate_map_record(tmp_path, monkeypatch):
    rec = {"round_id": "r8", "gates": {g: {"landed": s == "landed"} for g, s in ALL_LANDED.items()}}
    rec["gates"]["G2"]["landed"] = False
    monkeypatch.setattr(EV, "GATE_MAP_FILE", str(tmp_path / "GATE_MAP_{}.json"))   # absolute: replaces the repo root
    (tmp_path / "GATE_MAP_R8.json").write_text(json.dumps(rec), encoding="utf-8")
    assert EV.read_gate_state("r8") == dict(ALL_LANDED, G2="not_landed")
    assert EV.admit(EV.example(experiment_class="ANTI_PRIOR"), clock=LIVE, now=NOW)["reasons"] == \
        ["GATE_NOT_LANDED:G2"]
    (tmp_path / "GATE_MAP_R8.json").write_text(json.dumps(dict(rec, round_id="r7")), encoding="utf-8")
    assert EV.admit(EV.example(), clock=LIVE, now=NOW)["reasons"] == ["GATE_STATE_UNAVAILABLE"]


def test_ge_reads_the_published_redis_hash():
    class R:
        def __init__(self, h):
            self.h = h

        def hgetall(self, k):
            assert k == "pm:round:r8:gates"
            return self.h
    assert EV.admit(EV.example(), clock=LIVE, now=NOW, r=R(dict(ALL_LANDED, G1="not_landed")))["reasons"] == \
        ["GATE_NOT_LANDED:G1"]
    assert EV.admit(EV.example(campaign_stage="PRODUCTION"), clock=LIVE, now=NOW, r=R(ALL_LANDED))["ok"] is True


def test_ge_no_clock_build_phase_has_no_gate_reasons(monkeypatch):
    monkeypatch.setattr(EV, "GATE_MAP_FILE", "does/not/exist/GATE_MAP_{}.json")
    assert EV.gate_reasons(EV.example(), "cpu", None) == []
    assert EV.admit(EV.example())["ok"] is True
    for rid in ("t-r7-1", "r7", "r6"):                         # pre-gate rounds and test clocks are not gate-checked
        assert EV.gate_reasons(EV.example(), "cpu", dict(LIVE, round_id=rid)) == []
    assert EV.gate_reasons(EV.example(), "cpu", dict(LIVE, round_id="r9")) == ["GATE_STATE_UNAVAILABLE"]
    assert EV.gate_reasons(EV.example(), "cpu", dict(LIVE, round_id=None)) == ["GATE_STATE_UNAVAILABLE"]


def test_ge_topology_g2_c1_c2_g3_and_the_non_blocking_gates():
    g = lambda **kw: dict(ALL_LANDED, **kw)                    # noqa: E731
    clause_b = EV.example(experiment_class="CLAUSE_B")
    anti = EV.example(experiment_class="ANTI_PRIOR")
    assert EV.gate_reasons(anti, "cpu", LIVE, g(G2="not_landed")) == ["GATE_NOT_LANDED:G2"]
    assert EV.gate_reasons(clause_b, "cpu", LIVE, g(G2="not_landed")) == []
    assert EV.gate_reasons(EV.example(experiment_class="BETA_SWEEP"), "cpu", LIVE, g(G2="not_landed")) == \
        ["GATE_NOT_LANDED:G2"]
    assert EV.gate_reasons(EV.example(), "gpu", LIVE, g(C1="not_landed")) == ["GATE_NOT_LANDED:C1"]
    assert EV.gate_reasons(EV.example(), "cpu", LIVE, g(C1="not_landed")) == []
    assert EV.gate_reasons(clause_b, "cpu", LIVE, g(C2="not_landed")) == ["GATE_NOT_LANDED:C2"]
    assert EV.gate_reasons(dict(clause_b, evidence_class="OBSERVATION"), "cpu", LIVE, g(C2="not_landed")) == []
    assert EV.gate_reasons(EV.example(), "cpu", LIVE, g(G3="not_landed")) == ["GATE_NOT_LANDED:G3"]
    assert EV.gate_reasons(EV.example(), "gpu", LIVE, g(G3="not_landed")) == []
    rowless = EV.example(expected_output_rows=0)
    assert EV.gate_reasons(rowless, "gpu", LIVE, g(G1="not_landed")) == []
    for gid in ("G4", "G5", "G6", "G7", "G8", "GE", "C3"):
        assert EV.gate_reasons(anti, "gpu", LIVE, g(**{gid: "not_landed"})) == [], gid


def test_ge_refusal_is_recorded_as_an_event_not_a_fail(live):
    r, _ = live
    v = EV.admit(EV.example(), clock=LIVE, now=NOW, gates=dict(ALL_LANDED, G1="not_landed"))
    ev = EV.refuse(r, "F", {"job_id": "j-ge"}, v, EV.example(), stub=v["stub"])
    assert ev["stub_id"] is None and EV.candidates(r) == []
    got = EV.events(r, EV.GATE_REFUSAL)
    assert len(got) == 1 and got[0]["reasons"] == ["GATE_NOT_LANDED:G1"]
    assert "FAIL" not in json.dumps(got[0]).replace("GATE_", "")


# ------------------------------------------------------------------ G6: open_candidate (D27)

def test_g6_open_candidate_writes_a_stub_with_no_refusal_event(live):
    r, _ = live
    out = EV.open_candidate(r, "G", "w1 t128 learner remainder", "SWARM_R8 s4.1 measured 509.4 CPU-s/run",
                            requested_cost={"cpu_budget_s": 48124.0}, dependencies=["PC 1789532813234-0"],
                            experiment_class="R16_SCREEN_CELL", source_event="WHY_NOT_RUN")
    assert out == {"ok": True, "stub_id": out["stub_id"]} and out["stub_id"]
    names = [f.get("event") for _, f in r.xrange(EV.EVENTS)]
    assert not any(str(n).endswith("_REFUSAL") for n in names), names
    assert names == [EV.CANDIDATE_OPENED]
    stubs = EV.open_candidates(r)
    assert [s["stub_id"] for s in stubs] == [out["stub_id"]]
    s = stubs[0]
    assert s["source_event"] == "WHY_NOT_RUN" and s["kind"] == "PRODUCTION_CANDIDATE" and s["status"] == "STUB"
    assert s["question"] == "w1 t128 learner remainder" and s["dependencies"] == ["PC 1789532813234-0"]
    assert s["requested_cost"] == {"cpu_budget_s": 48124.0} and s["measured_cost"] is None


def test_g6_file_candidate_works_on_an_opened_stub(live):
    r, _ = live
    sid = EV.open_candidate(r, "E", "D25 canonical signflip ordering", "residue: better_instrument")["stub_id"]
    got = EV.file_candidate(r, sid, {"cpu_s": 12.5}, "rows/E/x.jsonl@abc1234")
    assert got["ok"] and EV.open_candidates(r) == []
    assert [c["stub_id"] for c in EV.filed_candidates(r)] == [sid]


def test_g6_open_candidate_refusals_and_refuse_still_stubs(live):
    r, _ = live
    assert EV.open_candidate(r, "E", " ", "b")["reason"] == "NO_QUESTION"
    assert EV.open_candidate(r, "E", "q", "")["reason"] == "NO_BASIS"
    assert EV.open_candidate(r, "", "q", "b")["reason"] == "NO_LANE"
    assert EV.open_candidate(r, "E", "q", "b", requested_cost={"cpu_s": -1})["reason"] == "BAD_COST"
    assert EV.open_candidate(r, "E", "q", "b", dependencies="x")["reason"] == "BAD_DEPENDENCIES"
    assert EV.open_candidate(r, "E", "q", "b", source_event="STAGE_BUDGET_REFUSAL")["reason"] == "BAD_SOURCE_EVENT"
    assert EV.candidates(r) == [] and EV.events(r) == []
    v = EV.admit(EV.example(wall_budget_s=10 ** 5))
    ev = EV.refuse(r, "E", {"job_id": "j", "fn": "m:f", "exp_id": "x"}, v, EV.example(wall_budget_s=10 ** 5))
    stub = EV.open_candidates(r)[0]
    assert ev["stub_id"] == stub["stub_id"] and stub["source_event"] == "STAGE_BUDGET_REFUSAL"
    assert stub["exp_id"] == "x" and stub["requested_cost"]["wall_budget_s"] == 10 ** 5 and stub["dependencies"] == []
