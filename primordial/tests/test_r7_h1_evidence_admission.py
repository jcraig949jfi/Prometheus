"""H-R7-1 (gate 30): EVIDENCE_N_v1 at ADMISSION -- a verdict-class job whose sample is not exactly 32/4/8 balanced is
refused SAMPLE_RULE_MISMATCH by the real worker before its function runs: zero rows, no PRODUCTION_CANDIDATE stub
(D16); the E-R6-1 envelope replayed is refused the same way; a 32/4/8 job is admitted and runs."""
from __future__ import annotations

import json
import subprocess

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
LANE = "H-r7-1"
CLOCK = "t-r7-1"
FAMS = [4200, 2101, 3303, 5501]
E_R6_1 = json.loads('{"campaign_stage": "PRODUCTION", "checkpointable": true, "cohort": "E", "cpu_budget_s": 6000, '
                    '"expected_output_rows": 50, "experiment_class": "CLAUSE_B", "gpu_budget_s": 0, '
                    '"predicate_id": "E-R6-1-clauseB-live-w14-w13", "required_controls": ["scratch", "sham_featperm"], '
                    '"required_oracles": ["world", "brain", "fused_eq_numpy", "sham_integrity"], "wall_budget_s": 2400}')


def sample(per):
    counts = dict(zip(FAMS[:len(per)], per))
    return {"runs_total": sum(per), "rng_family_count": len(per),
            "runs_per_family": per[0] if len(set(per)) == 1 else None,
            "families": list(counts), "n_per_family": {str(k): v for k, v in counts.items()}}


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    keys = [W.JOBS.format(LANE), W.ROWS.format(LANE), W.DONE.format(LANE), W.STOP.format(LANE),
            W.WSTATE.format(LANE), EV.EVENTS, EV.CANDIDATES, RC.CURRENT, RC.KEY.format(CLOCK)]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", CLOCK)
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def _serve(r, repo, n):
    return W.Worker(LANE, url=URL, repo=repo, log=lambda *_: None).serve(max_jobs=n, block_ms=500)


def test_malformed_verdict_samples_are_refused_at_admission_with_zero_rows_and_no_stub(env):
    r, repo = env
    RC.start(r, CLOCK, stage="PILOT")
    jobs = [("16-1-16", sample([16])), ("32-4-16844", sample([16, 8, 4, 4])), ("32-4-29111", sample([29, 1, 1, 1])),
            ("32-4-8", sample([8, 8, 8, 8]))]
    for name, s in jobs:
        W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", f"H-R7-1-{name}", f"rows/{name}.jsonl", 60, {"n": 2},
                 r=r, envelope={**EV.example(experiment_class="CLAUSE_B", cohort="E", predicate_id=f"P-{name}"), **s})
    done = _serve(r, repo, len(jobs))
    assert [d["status"] for d in done] == ["refused", "refused", "refused", "ok"]
    for d in done[:3]:
        assert "SAMPLE_RULE_MISMATCH" in d["reasons"] and d["event"] == "SAMPLE_RULE_MISMATCH"
    assert EV.candidates(r) == []                                             # stub False on SAMPLE_RULE_MISMATCH (D16)
    for name, _ in jobs[:3]:
        assert not (repo / "rows" / f"{name}.jsonl").exists()                # zero simulation, zero rows
    assert done[3]["rows"] == 2 and (repo / "rows" / "32-4-8.jsonl").exists()


def test_the_e_r6_1_envelope_replayed_is_refused_at_admission(env):
    r, repo = env
    RC.start(r, CLOCK, stage="PRODUCTION")
    W.submit(LANE, "primordial.fabric.selftest_jobs:emit_n", "E-R6-1-replay", "rows/e-r6-1.jsonl", 60, {"n": 2}, r=r,
             envelope=E_R6_1)
    [d] = _serve(r, repo, 1)
    assert d["status"] == "refused" and "SAMPLE_RULE_MISMATCH" in d["reasons"]
    assert not (repo / "rows" / "e-r6-1.jsonl").exists() and EV.candidates(r) == []
