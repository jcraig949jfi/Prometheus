"""Iteration 2 of the RunPod ladder: what it added, each part made to fail.

  - PROMETHEUS_WORK_UNITS, without which a scout is not smaller than its
    campaign (found in Iteration 2's dry run, before any spend);
  - the pod's /_clock and the controller's offset estimate, which turn
    the cross-clock provisioning bound into a measurement;
  - a shorter poll during the ready wait;
  - platform telemetry sampled by the platform, not the module;
  - max_runtime_s bounding the module rather than the whole pod;
  - per-artifact transfer timing;
  - a calibration pinned to the GPU it was measured on;
  - `flight.py`, generic over modules, free unless `--go`.
"""

import http.client
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time

import pytest

RUNPOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                      "runpod"))
sys.path.insert(0, RUNPOD)

from prometheus_gpu import dryrun                     # noqa: E402
from prometheus_gpu import launch                     # noqa: E402
from prometheus_gpu import provider as prov           # noqa: E402
from prometheus_gpu import receipt as rc              # noqa: E402
from prometheus_gpu import scout as scout_mod         # noqa: E402
from prometheus_gpu import secrets as secrets_mod     # noqa: E402
from prometheus_gpu import spec as spec_mod           # noqa: E402

SPEC = {
    "name": "iter2-test",
    "entrypoint": "run.py",
    "dependencies": {"pip": ["numpy==2.2.0"]},
    "gpu": {"class": "NVIDIA RTX A4000", "count": 1},
    "max_runtime_s": 600,
    "artifacts": ["result.json", "big.bin"],
    "canary": "python3 -c 'import numpy'",
    "env": {"KNOB": "7"},
    "env_allowlist": ["KNOB"],
    "work_units": {"name": "steps", "estimate": 1000},
    "telemetry": {"interval_s": 10, "platform_interval_s": 3},
}
TEL = "telemetry.jsonl"
START = '{"kind":"start","t_utc":"a","t_elapsed_s":0,"seq":1}\n'
END = ('{"kind":"end","t_utc":"c","t_elapsed_s":60,"seq":3,"units":1000,'
       '"status":"ok","elapsed_s":55.0}\n')
META = {"run_id": "r", "seat": "Aether", "workdir": "/app/module",
        "artifact_dir": "/app/out", "telemetry_path": "/app/out/telemetry.jsonl",
        "image": "img", "artifact_token": "tok", "artifact_port": 8081}
TRANSPORT = {"fetch_cmd": "curl -o b.tar.gz http://x", "local_name": "b.tar.gz",
             "bundle_sha256": "a" * 64}


class Clock(object):
    def __init__(self, start=1_000_000.0):
        self.t = float(start)
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.sleeps.append(float(seconds))
        self.t += float(seconds)


@pytest.fixture
def module_dir(tmp_path):
    d = tmp_path / "mod"
    d.mkdir()
    (d / "run.py").write_text("print('hello')\n")
    return str(d)


def spec(**over):
    data = json.loads(json.dumps(SPEC))
    data.update(over)
    return spec_mod.from_dict(data)


# ------------------------------------------------------- work units reach it

def test_the_module_is_told_how_much_work_to_do():
    env = secrets_mod.build_module_env(spec(), META)
    assert env["PROMETHEUS_WORK_UNITS"] == "1000"


def test_a_scout_is_smaller_than_its_campaign_and_otherwise_identical():
    """The defect this closes: a scout shrank a number the module never
    saw, so it would have run the whole campaign and billed for it."""
    campaign = spec()
    scouted = scout_mod.scout_spec(campaign, 0.05)
    a = secrets_mod.build_module_env(campaign, META)
    b = secrets_mod.build_module_env(scouted, META)
    assert b["PROMETHEUS_WORK_UNITS"] == "50"
    assert a["PROMETHEUS_WORK_UNITS"] == "1000"
    same = {k for k in a if k not in ("PROMETHEUS_WORK_UNITS",
                                      "PROMETHEUS_MODULE")}
    assert {k: a[k] for k in same} == {k: b[k] for k in same}
    assert scout_mod.representativeness(scouted, campaign)["representative"]


def test_a_module_without_work_units_gets_no_count():
    env = secrets_mod.build_module_env(spec(work_units=None), META)
    assert "PROMETHEUS_WORK_UNITS" not in env


# ------------------------------------------------------------ pod-side code

def test_the_sampler_starts_after_the_server_and_before_the_fetch():
    """The bootstrap itself -- a dependency install measured anywhere from
    6 s to 305 s -- has to be on the record, so sampling starts first."""
    boot = dryrun.build_bootstrap(spec(), META, TRANSPORT)
    server = boot.index("python3 -u /app/_serve.py &")
    sampler = boot.index("python3 -u /app/_sample.py")
    assert server < sampler < boot.index(TRANSPORT["fetch_cmd"])
    assert "PROMETHEUS_PLATFORM_INTERVAL_S=3 " in boot
    # Detached: a sampler failure must not take the bootstrap down.
    line = [l for l in boot.splitlines() if "/app/_sample.py" in l
            and l.startswith("PROMETHEUS_PLATFORM")][0]
    assert line.rstrip().endswith("&")


def test_the_platform_interval_falls_back_and_has_a_floor():
    assert dryrun.platform_interval(spec(telemetry={"interval_s": 7})) == 7.0
    assert dryrun.platform_interval(
        spec(telemetry={"interval_s": 7, "platform_interval_s": 0.1})) == 1.0


def test_the_sampler_records_without_a_gpu_and_never_raises(tmp_path):
    """No nvidia-smi here. The record must still be written, with the
    failure as a field -- a sampler that crashed would be a monitor that
    looks alive and records nothing."""
    script = tmp_path / "_sample.py"
    script.write_text(dryrun.PLATFORM_SAMPLER)
    env = dict(os.environ, PROMETHEUS_ARTIFACT_DIR=str(tmp_path / "out"),
               PROMETHEUS_PLATFORM_ONCE="1")
    proc = subprocess.run([sys.executable, str(script)], env=env,
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    lines = (tmp_path / "out" / "platform.jsonl").read_text().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["kind"] == "platform"
    assert "t_utc" in rec and "t_elapsed_s" in rec
    assert rec["sample_cost_s"] >= 0
    assert rec["gpus"] is not None or rec.get("gpu_error")
    assert "disk_free_b" in rec


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_the_artifact_server_reports_its_clock_to_the_token_only(tmp_path):
    script = tmp_path / "_serve.py"
    script.write_text(dryrun.ARTIFACT_SERVER)
    port = _free_port()
    env = dict(os.environ, PROMETHEUS_ARTIFACT_DIR=str(tmp_path),
               PROMETHEUS_ARTIFACT_TOKEN="tok",
               PROMETHEUS_ARTIFACT_PORT=str(port))
    proc = subprocess.Popen([sys.executable, str(script)], env=env,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + 20
        while True:
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                conn.request("GET", "/_clock")
                denied = conn.getresponse()
                denied.read()
                break
            except OSError:
                if time.time() > deadline:
                    raise
                time.sleep(0.2)
        assert denied.status == 401
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        before = time.time()
        conn.request("GET", "/_clock", headers={"Authorization": "Bearer tok"})
        resp = conn.getresponse()
        body = json.loads(resp.read())
        after = time.time()
        assert resp.status == 200
        assert before - 1 <= body["epoch"] <= after + 1
    finally:
        proc.kill()
        proc.wait(timeout=10)


# ------------------------------------------------------------- clock offset

def test_the_offset_comes_from_the_shortest_round_trip():
    rows = [(0.0, 105.5, 1.0),      # rtt 1.0 -> offset 105.0
            (2.0, 107.1, 2.2),      # rtt 0.2 -> offset 105.0, tightest
            (3.0, None, 3.1)]       # unreadable, ignored
    got = launch.estimate_offset(rows)
    assert got["offset_s"] == 105.0
    assert got["uncertainty_s"] == 0.1
    assert got["samples"] == 2
    assert launch.estimate_offset([(0.0, None, 1.0)]) is None


def _fake_with_pod_clock(clock, offset, rtt=0.4, boot_after=12.0,
                         stall_frames=0):
    """A pod whose clock is `offset` ahead, answering /_clock with a delay."""
    created = {}

    def pod_clock(_i):
        # The fetch itself takes `rtt`; the pod reads its clock midway.
        clock.t += rtt / 2
        value = clock.t + offset
        clock.t += rtt / 2
        return json.dumps({"epoch": value})

    def stages(_i):
        if "at" not in created:
            created["at"] = clock.t
        return '{"stage": "boot", "epoch": %f}\n' % (
            created["at"] - 30.0 + boot_after + offset)

    tel = [None] * stall_frames + [START, START + END]
    return prov.FakeProvider(served={
        TEL: tel, launch.STAGES_PATH: stages, launch.CLOCK_PATH: pod_clock,
        "result.json": '{"ok": true}', "big.bin": b"x" * 3_000_000,
        launch.PLATFORM_PATH: json.dumps({
            "kind": "platform", "t_elapsed_s": 1.0, "gpus": [
                {"name": "G", "mem_used_mib": 7000.0, "mem_total_mib": 16000.0,
                 "util_pct": 99.0, "temp_c": 70.0, "power_w": 140.0}],
            "mem_total_b": 100, "mem_available_b": 40,
            "sample_cost_s": 0.05}) + "\n"})


def test_the_controller_measures_the_pod_clock_and_corrects_provisioning(
        module_dir):
    clock = Clock()
    fake = _fake_with_pod_clock(clock, offset=3600.0, stall_frames=4)
    ctl = launch.Controller(fake, spec(), module_dir, budget_usd=5.0,
                            poll_s=30.0, now=clock.now, sleep=clock.sleep)
    r = ctl.run()
    assert r["result"] == "OK"
    sync = r["clock_sync"]["start"]
    assert abs(sync["offset_s"] - 3600.0) < 1e-6
    assert sync["uncertainty_s"] == pytest.approx(0.2)
    synced = r["lifecycle"]["synchronised"]
    assert "provision_s" in synced
    # The raw cross-clock figure is still reported, and is wrong by the
    # offset: that is the difference the measurement makes.
    raw = r["lifecycle"]["cross_clock"]["provision_s"]
    assert raw - synced["provision_s"] == pytest.approx(3600.0, abs=1e-3)
    assert r["clock_sync"]["end"] is not None
    rc.validate(r)


def test_no_clock_endpoint_leaves_provisioning_cross_clock(module_dir):
    clock = Clock()
    fake = prov.FakeProvider(served={TEL: [None, START, START + END],
                                     "result.json": "{}", "big.bin": "x"})
    ctl = launch.Controller(fake, spec(), module_dir, budget_usd=5.0,
                            poll_s=30.0, now=clock.now, sleep=clock.sleep)
    r = ctl.run()
    assert r["result"] == "OK"
    assert r["clock_sync"]["start"] is None
    assert "synchronised" not in r["lifecycle"]


def test_the_ready_wait_polls_faster_than_the_watch(module_dir):
    clock = Clock()
    fake = prov.FakeProvider(served={TEL: [None, None, None, START,
                                           START, START + END],
                                     "result.json": "{}", "big.bin": "x"})
    ctl = launch.Controller(fake, spec(), module_dir, budget_usd=5.0,
                            poll_s=30.0, ready_poll_s=3.0, now=clock.now,
                            sleep=clock.sleep)
    r = ctl.run()
    assert r["result"] == "OK"
    assert clock.sleeps[:3] == [3.0, 3.0, 3.0]
    assert 30.0 in clock.sleeps
    assert r["ready_poll_s"] == 3.0


def test_the_default_ready_poll_is_never_slower_than_five_seconds(module_dir):
    ctl = launch.Controller(prov.FakeProvider(), spec(), module_dir,
                            budget_usd=1.0, poll_s=20.0)
    assert ctl.ready_poll_s == 5.0
    ctl = launch.Controller(prov.FakeProvider(), spec(), module_dir,
                            budget_usd=1.0, poll_s=2.0)
    assert ctl.ready_poll_s == 2.0


# ---------------------------------------------------- runtime bound, transfer

def test_a_slow_bootstrap_does_not_eat_the_modules_runtime(module_dir):
    """max_runtime_s bounds the MODULE. Measured from the create, a 305 s
    wheel install -- observed in Iteration 1 -- would time out a module
    whose own bound was 120 s before it had run for a second."""
    clock = Clock()
    # 100 ready polls at 3 s: a 300 s install before the module starts.
    tel = [None] * 100 + [START] * 5 + [START + END]
    fake = prov.FakeProvider(served={
        TEL: tel, launch.STAGES_PATH: '{"stage": "boot", "epoch": 1}\n',
        "result.json": "{}", "big.bin": "x"})
    ctl = launch.Controller(fake, spec(max_runtime_s=120), module_dir,
                            budget_usd=5.0, poll_s=10.0, ready_poll_s=3.0,
                            stall_timeout_s=400.0, now=clock.now,
                            sleep=clock.sleep)
    r = ctl.run()
    assert r["result"] == "OK", r["notes"]


def test_a_module_that_overruns_is_still_stopped(module_dir):
    clock = Clock()
    fake = prov.FakeProvider(served={TEL: [START], "result.json": "{}",
                                     "big.bin": "x"})
    r = launch.Controller(fake, spec(max_runtime_s=60), module_dir,
                          budget_usd=5.0, poll_s=10.0, now=clock.now,
                          sleep=clock.sleep).run()
    assert r["result"] == "TIMEOUT"
    assert fake.leaked() == []


def test_the_receipt_carries_platform_peaks_and_transfer_rates(module_dir):
    clock = Clock()
    fake = _fake_with_pod_clock(clock, offset=0.0)
    ctl = launch.Controller(fake, spec(), module_dir, budget_usd=5.0,
                            poll_s=30.0, now=clock.now, sleep=clock.sleep)
    r = ctl.run()
    plat = r["platform_summary"]
    assert plat["samples"] == 1
    assert plat["gpu_mem_used_mib_peak"] == 7000.0
    assert plat["host_mem_used_b_peak"] == 60
    assert plat["sample_cost_s_mean"] == 0.05
    xfer = r["artifact_transfer"]
    assert xfer["bytes"] == 3_000_000 + len('{"ok": true}')
    assert xfer["largest"]["path"] == "big.bin"
    assert ctl.artifact_blobs["big.bin"] == b"x" * 3_000_000


def test_platform_summary_survives_garbage():
    assert launch.summarise_platform("") == {"samples": 0}
    got = launch.summarise_platform('not json\n{"kind": "other"}\n'
                                    '{"kind": "platform", "gpus": null}\n')
    assert got["samples"] == 1
    assert got["gpu_mem_used_mib_peak"] is None


# ------------------------------------------------------ calibration pinning

def _cal(gpu_used):
    return scout_mod.calibrate(100, 10.0, spec(), hourly=0.17,
                               overhead_seconds=40.0, gpu_used=gpu_used)


def test_a_calibration_on_one_card_does_not_price_another():
    campaign = spec(gpu={"class": "NVIDIA RTX A4000", "count": 1,
                         "alternatives": ["NVIDIA GeForce RTX 4090"]})
    with pytest.raises(scout_mod.CampaignRefused):
        scout_mod.plan_campaign(campaign, _cal("NVIDIA RTX A4000"), 1000, 1.0)
    with pytest.raises(scout_mod.CampaignRefused):
        scout_mod.plan_campaign(spec(), _cal("NVIDIA GeForce RTX 4090"),
                                1000, 1.0)
    plan = scout_mod.plan_campaign(spec(), _cal("NVIDIA RTX A4000"), 1000, 1.0)
    assert plan["decision"] == "PROCEED"
    # And the difference can be accepted, in as many words.
    plan = scout_mod.plan_campaign(campaign, _cal("NVIDIA RTX A4000"), 1000,
                                   1.0, accept_differences=True)
    assert plan["decision"] == "PROCEED"


# ---------------------------------------------------------------- flight.py

def _flight():
    path = os.path.join(RUNPOD, "flight.py")
    sp = importlib.util.spec_from_file_location("flight", path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def test_the_flight_script_creates_nothing_without_go(monkeypatch, capsys):
    flight = _flight()
    from prometheus_gpu import credentials

    def refuse(*a, **k):
        raise AssertionError("a non --go invocation touched a credential")
    monkeypatch.setattr(credentials, "install_into_environ", refuse)
    monkeypatch.setattr(credentials, "resolve", refuse)

    def no_provider(*a, **k):
        raise AssertionError("a non --go invocation built a real provider")
    monkeypatch.setattr(prov, "RunPodProvider", no_provider)

    assert flight.main(["examples/gpu_load", "--dry"]) == 0
    out = capsys.readouterr().out
    assert "POD CREATED: False" in out
    assert "PROMETHEUS_WORK_UNITS=6000" in out
    assert flight.main(["examples/gpu_load", "--scout", "0.05", "--dry"]) == 0
    assert "PROMETHEUS_WORK_UNITS=300" in capsys.readouterr().out
    assert flight.main(["examples/gpu_load", "--rehearse"]) == 0
    out = capsys.readouterr().out
    assert "result OK" in out
    assert '"offset_s": 1000.0' in out


def test_pinning_drops_the_alternatives():
    flight = _flight()
    pinned = flight.select_spec(flight.module_path("examples/gpu_load"),
                                pin_gpu="NVIDIA GeForce RTX 4090")
    assert pinned["gpu"]["class"] == "NVIDIA GeForce RTX 4090"
    assert pinned["gpu"]["alternatives"] == []


def test_a_scout_receipt_becomes_a_calibration(tmp_path, monkeypatch):
    flight = _flight()
    monkeypatch.setattr(flight, "HERE", str(tmp_path))
    run_dir = tmp_path / "receipts" / "s1"
    run_dir.mkdir(parents=True)
    (run_dir / "telemetry.jsonl").write_text(START + END)
    receipt = {"run_id": "s1", "evidence_dir": "receipts/s1",
               "telemetry_summary": {"units_final": 1000},
               "cost": {"elapsed_s": 100.0},
               "gpu_used": "NVIDIA RTX A4000"}
    cal = flight.calibration_from_receipt(receipt, spec())
    assert cal["seconds_per_unit"] == pytest.approx(0.055)
    assert cal["overhead_seconds"] == pytest.approx(45.0)
    assert cal["gpu_used"] == "NVIDIA RTX A4000"
    assert cal["hourly_usd"] == 0.17


def test_flight_overrides_do_not_move_the_bundle():
    """Scout, pin and sampling overrides edit the spec, never the files, so
    the committed bundle the pod fetches is the same bytes for all of them."""
    flight = _flight()
    from prometheus_gpu import bundle as bundle_mod
    mdir = flight.module_path("examples/gpu_load")
    base = bundle_mod.build(mdir, flight.select_spec(mdir)).sha256
    for kw in ({"scout": 0.05}, {"pin_gpu": "NVIDIA RTX A4000"},
               {"platform_interval": 1.0},
               {"scout": 0.05, "pin_gpu": "NVIDIA RTX A4000",
                "platform_interval": 1.0}):
        varied = flight.select_spec(mdir, **kw)
        assert bundle_mod.build(mdir, varied).sha256 == base, kw
    assert flight.select_spec(mdir, platform_interval=1.0)[
        "telemetry"]["platform_interval_s"] == 1.0


def test_first_contact_through_the_proxy_is_its_own_interval(module_dir):
    """Pod running and pod reachable are different instants. The gap between
    them is the proxy's, and Iteration 2 measured it at ~25 s."""
    clock = Clock()
    fake = _fake_with_pod_clock(clock, offset=0.0, stall_frames=3)
    real_fetch = fake.fetch
    calls = {"n": 0}

    def late_proxy(pod_id, path, **kw):
        calls["n"] += 1
        if calls["n"] <= 6:          # the proxy 404s for the first polls
            return None
        return real_fetch(pod_id, path, **kw)
    fake.fetch = late_proxy
    r = launch.Controller(fake, spec(), module_dir, budget_usd=5.0,
                          poll_s=30.0, ready_poll_s=3.0, now=clock.now,
                          sleep=clock.sleep).run()
    ctl = r["lifecycle"]["controller_clock"]
    assert ctl["accepted_to_first_contact_s"] > 0
    assert ctl["accepted_to_first_contact_s"] <= ctl[
        "accepted_to_first_telemetry_s"]


def _plan(tmp_path, decision="PROCEED", units=3000.0, module="gpu-load@1",
          prereg=True):
    plan = {"decision": decision, "module": module, "ceiling_usd": 0.2,
            "calibrated_estimate": {"expected_usd": 0.015, "margin": 0.2,
                                    "requested_units": units},
            "calibration": {"source": "scout receipt x",
                            "gpu_used": "NVIDIA RTX A4000"}}
    if prereg:
        plan["preregistered_estimate"] = {"expected_usd": 0.0152}
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    return str(path)


def test_a_campaign_plan_rides_into_the_receipt(tmp_path, capsys):
    flight = _flight()
    mdir = flight.module_path("examples/gpu_load")
    spec_ = flight.select_spec(mdir, pin_gpu="NVIDIA RTX A4000", units=3000)
    assert spec_["work_units"]["estimate"] == 3000.0
    plan = flight.load_campaign_plan(_plan(tmp_path), spec_)
    assert flight.rehearse(mdir, spec_, 0.2, plan=plan) == 0
    out = capsys.readouterr().out
    assert "calibration" in out and "predicted $0.0150" in out


@pytest.mark.parametrize("bad", [{"decision": "REFUSE"}, {"units": 6000.0},
                                 {"module": "other@1"}, {"prereg": False}])
def test_a_plan_for_some_other_run_is_refused(tmp_path, bad):
    flight = _flight()
    mdir = flight.module_path("examples/gpu_load")
    spec_ = flight.select_spec(mdir, units=3000)
    with pytest.raises(RuntimeError):
        flight.load_campaign_plan(_plan(tmp_path, **bad), spec_)
