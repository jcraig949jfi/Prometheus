"""campaign.run_wave (a) restarts the hour cap on every process attempt (t0 = time.time() per call),
so a watchdog relaunch (launch.py: up to 20 attempts) grants a FRESH full budget to the wave in
progress, contrary to PREREG s5 "hours are hard caps"; (b) silently accepts stored rows of a wave
that the regenerated specs no longer contain (upstream changed between attempts), and
store.rows(wave) then feeds them to every later wave and to report.py. Both FAIL on current code and
PASS with patches/run_wave_budget_and_exact_resume.diff. Neutrality: a first attempt on an empty
store, and an exact resume, run exactly as before. PTE-C1 ran one attempt (watchdog.log), so C1 is
unaffected."""
import json
import time

import pytest

from prometheus.ananke import campaign as C


def _spec(i, wave="A0"):
    return dict(wave=wave, kind="census", physics={"i": i}, env={"family": "RELAY"}, search={},
                search_seed=i, extra={}, levels={}, env_levels={}, parent=None)


@pytest.fixture
def fake_cell(monkeypatch):
    calls = []

    def run_cell(spec, device="cpu"):
        calls.append(spec["search_seed"])
        return {"cell_wall_s": 0.0}
    monkeypatch.setattr(C, "run_cell", run_cell)
    monkeypatch.setattr(C, "gpu_snapshot", lambda: "n/a")
    return calls


def test_first_attempt_runs_everything(tmp_path, fake_cell):
    cfg = C.CampaignConfig()
    st = C.Store(tmp_path, cfg)
    C.run_wave(st, cfg, "A0", [_spec(i) for i in range(3)], {}, "cpu")
    assert fake_cell == [0, 1, 2] and len(st.rows("A0")) == 3


def test_relaunch_does_not_get_a_fresh_budget(tmp_path, fake_cell):
    cfg = C.CampaignConfig()
    st = C.Store(tmp_path, cfg)
    C.run_wave(st, cfg, "A0", [_spec(0)], {}, "cpu")             # attempt 1 starts the wave clock
    p = st.dir / "heartbeat.json"
    hb = json.loads(p.read_text()) if p.exists() else {}
    key = "wave_A0_started_epoch"
    assert key in hb, "the wave start time is not persisted across attempts"
    hb[key] = time.time() - cfg.budget_hours["A0"] * 3600 - 60   # the wave's cap has elapsed
    p.write_text(json.dumps(hb))
    st2 = C.Store(tmp_path, cfg)                                   # attempt 2 (watchdog relaunch)
    C.run_wave(st2, cfg, "A0", [_spec(0), _spec(1), _spec(2)], {}, "cpu")
    assert fake_cell == [0], "a relaunch ran cells after the wave's hour cap"


def test_stale_rows_from_another_spec_set_are_refused(tmp_path, fake_cell):
    cfg = C.CampaignConfig()
    st = C.Store(tmp_path, cfg)
    C.run_wave(st, cfg, "A", [_spec(i, "A") for i in range(3)], {}, "cpu")
    st2 = C.Store(tmp_path, cfg)
    # upstream changed between attempts: the regenerated A specs differ from the stored A rows
    with pytest.raises(SystemExit):
        C.run_wave(st2, cfg, "A", [_spec(i, "A") for i in range(10, 13)], {}, "cpu")
    assert (st2.dir / "PARKED.json").exists()


def test_exact_resume_is_accepted(tmp_path, fake_cell):
    cfg = C.CampaignConfig()
    st = C.Store(tmp_path, cfg)
    C.run_wave(st, cfg, "A", [_spec(i, "A") for i in range(2)], {}, "cpu")
    st2 = C.Store(tmp_path, cfg)
    C.run_wave(st2, cfg, "A", [_spec(i, "A") for i in range(3)], {}, "cpu")
    assert fake_cell == [0, 1, 2]
