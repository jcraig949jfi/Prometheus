"""Tests for the launch path -- the only module that can spend money.

Every one of these runs against `FakeProvider` with an injected clock, so
the whole reliability surface is qualified before hardware is involved
and re-qualifying it costs nothing. The ordering properties are the point:

  retrieve BEFORE terminate       a dead pod hands back nothing
  terminate in a `finally`        including when the controller raises
  inventory BEFORE create         "I could not tell" is not permission
  no clean claim without evidence enforced in the receipt, not by habit

The fake's `leaked()` is the ledger that matters: it reports pods that
really exist and were never terminated, regardless of what the API
reported. A test that ends with a leak is a test describing real money.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "runpod")))

from prometheus_gpu import launch                     # noqa: E402
from prometheus_gpu import provider as prov           # noqa: E402
from prometheus_gpu import receipt as rc              # noqa: E402
from prometheus_gpu import spec as spec_mod           # noqa: E402

SPEC = {
    "name": "launch-test",
    "entrypoint": "run.py",
    "dependencies": {"pip": ["numpy==2.2.0"]},
    "gpu": {"class": "NVIDIA RTX A4000", "count": 1},
    "max_runtime_s": 600,
    "artifacts": ["out/result.json"],
    "canary": "python3 -c 'import numpy'",
    "work_units": {"name": "steps", "estimate": 100},
}

TEL = "out/telemetry.jsonl"

START = '{"kind":"start","t_utc":"a","t_elapsed_s":0,"seq":1}\n'
PROG = '{"kind":"progress","t_utc":"b","t_elapsed_s":30,"seq":2,"units":50}\n'
END = ('{"kind":"end","t_utc":"c","t_elapsed_s":60,"seq":3,"units":100,'
       '"status":"ok"}\n')
END_BAD = ('{"kind":"end","t_utc":"c","t_elapsed_s":60,"seq":3,"units":40,'
           '"status":"failed"}\n')


class Clock(object):
    """Deterministic time. `sleep` is the only thing that advances it."""

    def __init__(self, start=1_000_000.0):
        self.t = float(start)

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.t += float(seconds)


def frames(*texts):
    """Serve each text once, then hold the last one."""
    seq = list(texts)

    def serve(index):
        return seq[min(index, len(seq) - 1)]
    return serve


@pytest.fixture
def module_dir(tmp_path):
    d = tmp_path / "mod"
    d.mkdir()
    (d / "run.py").write_text("print('hello')\n")
    return str(d)


def controller(fake, module_dir, budget_usd=1.0, spec=None, **kw):
    clock = Clock()
    ctl = launch.Controller(fake, spec_mod.from_dict(spec or dict(SPEC)),
                            module_dir, budget_usd=budget_usd,
                            poll_s=30.0, now=clock.now, sleep=clock.sleep, **kw)
    ctl.clock = clock
    return ctl


def happy_fake(**kw):
    return prov.FakeProvider(served={
        TEL: frames(None, START, START + PROG, START + PROG + END),
        "out/result.json": '{"answer": 42}',
    }, **kw)


# ------------------------------------------------------------ preconditions

def test_a_pod_already_running_refuses_the_launch(module_dir):
    """One pod at a time is a precondition, not a convention."""
    fake = happy_fake()
    fake.create_pod({"name": "someone-elses-run"})
    ctl = controller(fake, module_dir)
    with pytest.raises(launch.LaunchRefused) as exc:
        ctl.run()
    assert "already active" in str(exc.value)
    assert fake.calls["create"] == 1, "no SECOND pod was created"


def test_an_unreadable_inventory_refuses_the_launch(module_dir):
    """A failed listing is indistinguishable from an empty account, so it
    is not permission to create. 'I could not tell' is not 'nothing is
    running'."""
    fake = prov.FakeProvider(list_faults=[prov.Fault.http(500)])
    ctl = controller(fake, module_dir)
    with pytest.raises(launch.LaunchRefused) as exc:
        ctl.run()
    assert "inventory read failed" in str(exc.value)
    assert fake.calls["create"] == 0
    assert fake.leaked() == []


# -------------------------------------------------------------- happy path

def test_a_clean_run_retrieves_then_terminates(module_dir):
    fake = happy_fake()
    r = controller(fake, module_dir).run()

    assert r["result"] == "OK"
    # The artifact was retrieved. Since the fake serves nothing for a pod
    # that no longer exists, this ALSO proves retrieval happened before
    # termination -- the ordering that a failed run depends on.
    assert [a["path"] for a in r["artifacts"]] == ["out/result.json"]
    assert r["artifacts"][0]["bytes"] == len('{"answer": 42}')
    assert r["artifacts_missing"] == []

    assert r["cleanup"]["terminate_acknowledged"] is True
    assert r["cleanup"]["observed_absent"] is True
    assert r["cleanup"]["operational_cleanup"] is True
    assert r["cleanup"]["billing_reconciled"] is False
    assert fake.leaked() == [], "a leaked pod is real money"

    assert r["telemetry_summary"]["units_final"] == 100
    assert r["telemetry_summary"]["complete"] is True
    assert r["pods"][0]["creation_outcome"] == "confirmed"
    rc.validate(r)


def test_the_receipt_reports_work_in_the_modules_own_units(module_dir):
    r = controller(happy_fake(), module_dir).run()
    assert r["cost"]["work_units"]["name"] == "steps"
    assert r["cost"]["work_units"]["actual"] == 100.0
    assert r["cost"]["billing_reconciled"] is False


# ------------------------------------------------------------------ limits

def test_the_budget_ceiling_stops_the_run_and_still_cleans_up(module_dir):
    """A run that never ends must stop on money, not on patience."""
    fake = prov.FakeProvider(served={TEL: frames(START, START + PROG)})
    # A4000 at $0.17/h: $0.0005 is about 10 s of pod time.
    ctl = controller(fake, module_dir, budget_usd=0.0005)
    r = ctl.run()
    assert r["result"] == "ABORTED"
    assert fake.leaked() == []
    assert r["cleanup"]["operational_cleanup"] is True
    rc.validate(r)


def test_max_runtime_stops_the_run(module_dir):
    spec = dict(SPEC, max_runtime_s=60)
    fake = prov.FakeProvider(served={TEL: frames(START, START + PROG)})
    r = controller(fake, module_dir, budget_usd=100.0, spec=spec).run()
    assert r["result"] == "TIMEOUT"
    assert fake.leaked() == []


def test_a_pod_that_never_becomes_ready_is_a_failure_not_a_hang(module_dir):
    fake = prov.FakeProvider(served={})          # nothing ever served
    ctl = controller(fake, module_dir, ready_timeout_s=120.0)
    r = ctl.run()
    assert r["result"] == "FAILED"
    assert any("never reported ready" in n for n in r["notes"])
    assert fake.leaked() == []


def test_a_module_that_reports_failure_is_not_recorded_as_ok(module_dir):
    fake = prov.FakeProvider(served={
        TEL: frames(START, START + END_BAD), "out/result.json": "{}"})
    r = controller(fake, module_dir).run()
    assert r["result"] == "FAILED"
    assert r["telemetry_summary"]["module_status"] == "failed"
    assert fake.leaked() == []


# ------------------------------------------------------------- the failures

def test_the_pod_is_terminated_even_when_the_controller_raises(module_dir):
    """Teardown lives in a `finally`. A controller bug must not leave a
    GPU running."""
    fake = happy_fake()

    def exploding_fetch(*a, **k):
        raise KeyboardInterrupt("something awful mid-run")
    fake.fetch = exploding_fetch

    ctl = controller(fake, module_dir)
    with pytest.raises(KeyboardInterrupt):
        ctl.run()
    # BaseException propagates, and the `finally` still ran.
    assert fake.leaked() == [], "the pod was left running"


def test_a_transient_terminate_failure_is_retried(module_dir):
    fake = happy_fake(terminate_faults=[prov.Fault.http(502)])
    r = controller(fake, module_dir).run()
    assert r["cleanup"]["terminate_acknowledged"] is True
    assert r["cleanup"]["operational_cleanup"] is True
    assert fake.leaked() == []


def test_a_pod_that_cannot_be_terminated_is_reported_unresolved(module_dir):
    """The receipt must not round a stuck pod up to 'clean'."""
    fake = happy_fake(terminate_faults=[prov.Fault.http(500)] * 3)
    r = controller(fake, module_dir).run()
    assert r["cleanup"]["terminate_acknowledged"] is False
    assert r["cleanup"]["operational_cleanup"] is False
    assert r["cleanup"]["unresolved"][0]["reasons"]
    assert fake.leaked(), "the fake agrees the pod is still really there"
    rc.validate(r)


def test_a_pod_hidden_from_the_listing_is_still_terminated(module_dir):
    """Cleanup targets the id we hold, never 'whatever the listing shows'.

    A pod missing from a LIST is the case where trusting the listing
    leaves a GPU billing forever.
    """
    fake = happy_fake()
    r = controller(fake, module_dir).run()
    pod_id = r["pods"][0]["id"]
    assert pod_id and fake.leaked() == []

    hidden = happy_fake()
    ctl = controller(hidden, module_dir)
    original_create = hidden.create_pod

    def create_then_hide(body):
        out = original_create(body)
        hidden._hidden.add(out["id"])        # exists, invisible to list()
        return out
    hidden.create_pod = create_then_hide
    r2 = ctl.run()
    assert hidden.leaked() == [], "terminated by id despite being hidden"
    # Absence was confirmed by a listing that never showed it, so the
    # claim is honest only because the terminate was acknowledged too.
    assert r2["cleanup"]["terminate_acknowledged"] is True


def test_an_unresolvable_create_is_not_a_clean_non_event(module_dir):
    """The dangerous case: the create outcome is unknown AND the
    reconciling listing failed. A pod may exist that we cannot name, so
    the receipt must refuse to look like nothing happened."""
    fake = prov.FakeProvider(
        create_faults=[prov.Fault.lost_response()] * 3,
        list_faults=[None, prov.Fault.http(500), prov.Fault.http(500),
                     prov.Fault.http(500), prov.Fault.http(500)])
    r = controller(fake, module_dir).run()
    assert r["result"] == "UNKNOWN"
    assert r["cleanup"]["operational_cleanup"] is False
    assert r["pods"][0]["creation_outcome"] == "unknown"
    assert any("RECONCILE MANUALLY" in n for n in r["notes"])
    rc.validate(r)


def test_a_lost_create_response_is_adopted_not_duplicated(module_dir):
    fake = prov.FakeProvider(
        create_faults=[prov.Fault.lost_response()],
        served={TEL: frames(START, START + END), "out/result.json": "{}"})
    r = controller(fake, module_dir).run()
    assert fake.calls["create"] == 1, "a second create would bill twice"
    assert r["pods"][0]["creation_outcome"] == "adopted"
    assert fake.leaked() == []


def test_a_clean_create_failure_creates_nothing(module_dir):
    fake = prov.FakeProvider(create_faults=[prov.Fault.http(400)] * 3)
    r = controller(fake, module_dir).run()
    assert r["result"] == "NOT_RUN"
    assert r["pods"] == []
    assert fake.leaked() == []
    rc.validate(r)


# ----------------------------------------------------------------- secrets

def test_no_credential_reaches_the_pod_request(module_dir, monkeypatch):
    """Fake credentials are injected into the controller's environment on
    purpose. The request that goes to the provider must not carry them."""
    monkeypatch.setenv("RUNPOD_API_KEY", "rpa_" + "F" * 24)
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_" + "F" * 24)
    sent = {}
    fake = happy_fake()
    original = fake.create_pod

    def capture(body):
        sent.update(body)
        return original(body)
    fake.create_pod = capture

    controller(fake, module_dir).run()
    env = sent["env"]
    for forbidden in prov_forbidden():
        assert forbidden not in env
    joined = "\n".join("%s=%s" % kv for kv in env.items()) + sent["cmd"][0]
    assert "F" * 24 not in joined, "a credential VALUE reached the pod"


def prov_forbidden():
    return spec_mod.FORBIDDEN_ENV


# -------------------------------------------------------------- telemetry

def test_a_truncated_telemetry_tail_does_not_lose_the_run(module_dir):
    """The pod died mid-write. Everything up to the last flush must still
    reach the receipt."""
    partial = START + PROG + '{"kind":"prog'
    fake = prov.FakeProvider(served={TEL: frames(partial, partial)})
    r = controller(fake, module_dir, budget_usd=0.0005).run()
    assert r["result"] == "ABORTED"
    assert r["telemetry_summary"]["records"] == 2
    assert r["telemetry_summary"]["units_final"] == 50
    assert r["telemetry_summary"]["complete"] is False
    rc.validate(r)


def test_a_missing_artifact_is_reported_not_silently_dropped(module_dir):
    fake = prov.FakeProvider(served={TEL: frames(START, START + END)})
    r = controller(fake, module_dir).run()
    assert r["artifacts_missing"] == ["out/result.json"]
    assert r["artifacts"] == []
    rc.validate(r)


# ------------------------------------------------------------- the rehearsal

def test_rehearse_flies_the_whole_path_without_a_provider(module_dir, capsys,
                                                          monkeypatch, tmp_path):
    """A rehearsal must reach a valid OK receipt and must not so much as
    resolve a credential, or a seat cannot safely run it to check its spec."""
    from prometheus_gpu import cli, credentials

    def refuse(*a, **k):
        raise AssertionError("a rehearsal resolved a credential")
    monkeypatch.setattr(credentials, "resolve", refuse)
    monkeypatch.setattr(credentials, "install_into_environ", refuse)

    spec_path = tmp_path / "module_spec.json"
    spec_path.write_text(
        '{"name": "rehearsal", "entrypoint": "run.py",'
        ' "artifacts": ["out/result.json"],'
        ' "work_units": {"name": "steps", "estimate": 10}}')
    (tmp_path / "run.py").write_text("print('hi')\n")

    assert cli.main(["rehearse", str(spec_path)]) == 0
    out = capsys.readouterr().out
    assert "result OK" in out
    assert "REHEARSAL ONLY" in out
    assert "billing_reconciled=False" in out


def test_rehearse_does_not_overwrite_a_declared_telemetry_artifact(tmp_path):
    """A module may declare its telemetry file as an artifact. The
    rehearsal's synthetic telemetry must not be clobbered by placeholder
    bytes -- when it was, the rehearsal reported a spurious TIMEOUT."""
    from prometheus_gpu import cli, launch

    spec_path = tmp_path / "module_spec.json"
    spec_path.write_text(
        '{"name": "rehearsal2", "entrypoint": "run.py",'
        ' "artifacts": ["%s", "out/result.json"]}' % launch.TELEMETRY_PATH)
    (tmp_path / "run.py").write_text("print('hi')\n")
    assert cli.main(["rehearse", str(spec_path)]) == 0


# ------------------------------------------------------- the flight script

def _flight_module():
    import importlib.util
    path = os.path.join(os.path.dirname(__file__), "..", "runpod",
                        "iteration1_flight.py")
    spec = importlib.util.spec_from_file_location("iteration1_flight",
                                                  os.path.abspath(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_flight_script_needs_go_and_otherwise_creates_nothing(monkeypatch,
                                                                  capsys):
    """The expensive action is opt-in. Reading, importing or testing this
    file must be free, so `--go` is the only path that can spend."""
    flight = _flight_module()
    from prometheus_gpu import credentials, provider as prov

    def refuse(*a, **k):
        raise AssertionError("a non --go invocation touched a credential")
    monkeypatch.setattr(credentials, "install_into_environ", refuse)
    monkeypatch.setattr(credentials, "resolve", refuse)

    def no_provider(*a, **k):
        raise AssertionError("a non --go invocation built a real provider")
    monkeypatch.setattr(prov, "RunPodProvider", no_provider)

    assert flight.main([]) == 0
    assert "POD CREATED: False" in capsys.readouterr().out
    assert flight.main(["--dry"]) == 0
    assert flight.main(["--rehearse"]) == 0
    out = capsys.readouterr().out
    assert "result OK" in out
    assert "billing_reconciled=False" in out


def test_the_flight_budget_is_well_above_the_projection():
    """A ceiling set near the estimate turns a small projection error into
    lost work. That happened on AETH-02; see the calibration ledger."""
    flight = _flight_module()
    from prometheus_gpu import cost as cost_mod
    spec = flight.load_spec()
    projected = cost_mod.project(spec, workload_seconds=60.0)
    assert flight.DEFAULT_BUDGET_USD > 5 * projected["usd_total"]
