"""E-R5-2: GPU queue + arbiter -- F's admission, the O5 lease held for every timing row, 19 s6 fields, timeout ->
PRODUCTION_CANDIDATE, lease busy -> requeue. Live Redis on the per-lane test db; rows go to an in-memory writer."""
from __future__ import annotations

import json

import pytest

from primordial.bus import bus
from primordial.fabric import envelope as EV
from primordial.nv import gpuq as GQ

SNAP = {"gpu_device": "planted GPU", "driver": "000.00", "vram_used_mib": 100, "gpu_util_pct": 0}


class _W:
    rows: list = []

    def __init__(self, path, exp_id):
        self.path, self.exp_id = path, exp_id

    def write(self, row):
        from primordial.fabric.rows import STATUSES          # the live RowWriter's rule (crashed the first smoke)
        assert row.get("status") in STATUSES, row
        _W.rows.append(row)

    def close(self, note=""):
        pass


@pytest.fixture
def live(monkeypatch):
    redis = pytest.importorskip("redis")
    from primordial.tests._live import live_url
    url = live_url()
    r = redis.Redis.from_url(url, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = (GQ.QUEUE, GQ.DONE, EV.EVENTS, EV.CANDIDATES, bus.GPU_LEASE, "pm:round:current")
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", url)
    monkeypatch.setenv("PM_LANE", "E")
    monkeypatch.setenv("PM_TAG", "t-e")
    _W.rows = []
    yield r
    r.delete(*keys)


def _arb(r, **kw):
    return GQ.Arbiter(r, snapshot=lambda: dict(SNAP), cpu_load=lambda: 12.5, writer=_W, poll_s=0.2,
                      log=lambda *_: None, **kw)


def _env(**kw):
    return EV.example(**({"campaign_stage": "SMOKE", "gpu_budget_s": 60, "cohort": "E",
                          "experiment_class": "GPU_SELFTEST"} | kw))


def _run(r, arb, fn, env, kwargs=None):
    GQ.submit(r, fn, "local", env, "E-R5-2-selftest", "primordial/ledger/rows/E/x.jsonl", kwargs)
    return arb.serve(max_jobs=1, block_ms=500, idle_exit_s=5)


def test_rows_are_stamped_under_the_lease_with_19s6_fields(live):
    out = _run(live, _arb(live), "primordial.nv.gpuq_selftest:two_rows", _env())
    assert out[0]["status"] == "ok" and out[0]["rows"] == 3 and out[0]["timing_rows_valid"] == 1
    timing = [x for x in _W.rows if x.get("kind") == "timing"]
    assert len(timing) == 2 and all(x["lease_token"] and x["lease_lost"] is False for x in timing)
    assert all(x[f] is not None for x in timing for f in GQ.HOST_FIELDS)
    assert timing[0]["speed_status"] == "VALID" and timing[1]["speed_status"] == "INDETERMINATE"
    assert timing[1]["missing_fields"] == ["comparison_backend"]
    assert _W.rows[-1]["kind"] == "gpu_job_end" and _W.rows[-1]["cap_s"] == 60
    assert bus.lease_holder(live) is None                                          # released after the job


def test_over_ceiling_is_refused_by_fs_admission_not_run(live):
    out = _run(live, _arb(live), "primordial.nv.gpuq_selftest:two_rows", _env(gpu_budget_s=900))
    assert out[0]["status"] == "refused" and "GPU_WALL_OVER_CEILING" in out[0]["reasons"]
    assert [e["event"] for e in EV.events(live)] == [EV.STAGE_BUDGET_REFUSAL]
    assert EV.candidates(live)[0]["kind"] == "PRODUCTION_CANDIDATE"
    assert not any(x.get("kind") == "timing" for x in _W.rows) and bus.lease_holder(live) is None
    bad = _run(live, _arb(live), "primordial.nv.gpuq_selftest:two_rows", {"campaign_stage": "PILOT"})
    assert bad[0]["status"] == "refused" and any(x.startswith("ENVELOPE_MISSING_FIELD") for x in bad[0]["reasons"])


def test_cap_kills_the_child_keeps_rows_and_files_a_production_candidate(live):
    arb = _arb(live, max_wall_s=3)
    out = _run(live, arb, "primordial.nv.gpuq_selftest:sleeper", _env(gpu_budget_s=600), {"seconds": 60})
    assert out[0]["status"] == "timeout" and out[0]["wall_s"] < 30
    end = _W.rows[-1]
    assert end["status"] == "timeout" and end["reason"] == "GPU_WALL_CAP" and end["cap_s"] == 3
    assert end["checkpoint"] and end["rows_from_child"] == 1                        # the row before the kill survived
    assert [e["event"] for e in EV.events(live)] == ["TIMEOUT"]
    stub = EV.candidates(live)[0]
    assert stub["source_event"] == "TIMEOUT" and stub["measured_cost"]["gpu_wall_s"] >= 3
    assert bus.lease_holder(live) is None


def test_busy_lease_requeues_and_runs_nothing(live, monkeypatch):
    monkeypatch.setenv("PM_TAG", "other")
    holder = bus.lease_acquire("someone else", ttl_s=30, r=live)
    monkeypatch.setenv("PM_TAG", "t-e")
    out = _run(live, _arb(live, lease_wait_s=0), "primordial.nv.gpuq_selftest:two_rows", _env())
    assert out[0]["status"] == "lease_busy" and out[0]["requeued_job_id"]
    assert live.xlen(GQ.QUEUE) == 2 and not any(x.get("kind") == "timing" for x in _W.rows)
    assert bus.lease_release(holder, r=live)


def test_child_error_is_an_aborted_row_and_gw_venv_is_never_a_gpu_venv(live):
    out = _run(live, _arb(live), "primordial.nv.gpuq_selftest:crash", _env())
    assert out[0]["status"] == "aborted" and "planted child failure" in _W.rows[-1]["stderr_tail"]
    with pytest.raises(ValueError):
        GQ.venv_python("gw")
    assert GQ.venv_python("u").endswith("nv-venv-u\\Scripts\\python.exe") or GQ.venv_python("u").endswith("nv-venv-u/Scripts/python.exe")
