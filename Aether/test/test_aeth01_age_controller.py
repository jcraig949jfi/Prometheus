"""Offline lifecycle tests: no real credentials, sockets, GPU, or provider calls.

Run with: python -m pytest Aether/test/test_aeth01_age_controller.py -q
All times/transports are injected. Temporary journals/artifacts are the only writes.
"""

from copy import deepcopy
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest


MODULE = (Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"
          / "age_controller.py")
SPEC = importlib.util.spec_from_file_location("_age_controller_test", MODULE)
age = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(age)
LIVE_CLIENTS = age._live_clients
# Deliberately synthetic, non-credential fixtures; never consult the host environment.
TOKEN = "offline-fixture-artifact-token-0123456789"
REAPER_SECRET = "offline-fixture-reaper-shared-secret-0123456789"
EPOCH = 1_800_000_000.0


class FakeClock:
    def __init__(self):
        self.wall = EPOCH
        self.mono = 100.0
        self.sleeps = []

    def time(self):
        return self.wall

    def monotonic(self):
        return self.mono

    def advance(self, seconds):
        self.wall += seconds
        self.mono += seconds

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.advance(seconds)


class NoEnvironment(dict):
    """An empty synthetic env; stdlib locale/terminal lookups are harmless."""

    def get(self, key, default=None):
        if key in ("RUNPOD_API_KEY", "AGE_ARTIFACT_TOKEN"):
            raise AssertionError("credential read forbidden")
        return super().get(key, default)

    def __getitem__(self, key):
        if key in ("RUNPOD_API_KEY", "AGE_ARTIFACT_TOKEN"):
            raise AssertionError("credential read forbidden")
        return super().__getitem__(key)


def config():
    return {"image": "registry.example/aeth01@sha256:" + "a" * 64,
            "gpu_id": "offline-gpu", "cloud": "COMMUNITY", "hourly_rate_usd": 6,
            "canary_budget_usd": 3, "remaining_budget_usd": 19.93,
            "max_lifetime_seconds": 240, "canary_timeout_seconds": 30,
            "independent_cutoff_deadline_utc": age._utc(EPOCH + 1200),
            "independent_cutoff_reference": "offline independent cutoff fixture"}


def read_json(path):
    return json.loads(Path(path).read_bytes())


class Provider:
    def __init__(self, directory, clock, events):
        self.directory, self.clock, self.events = directory, clock, events
        self.pods = {}
        self.deleted = set()
        self.create_error = None
        self.create_hook = None
        self.get_hook = None
        self.list_hook = None
        self.delete_hook = None
        self.delete_failures = 0
        self.confirmation_failures = 0
        self.delete_effective = True
        self.termination_status = None
        self.list_count = 0
        self.create_count = 0

    def create_pod(self, body):
        self.create_count += 1
        self.events.append(("POST",))
        state = read_json(self.directory / "state.json")
        assert state["phase"] == "CREATE_INTENT"
        assert state["owned_ids"] == []
        assert state["run_name"] == body["name"]
        assert state["image"] == body["image"]
        assert state["run_id"] == body["env"]["AETH01_RUN_ID"]
        assert state["plan_sha256"] == hashlib.sha256((self.directory / "plan.json").read_bytes()).hexdigest()
        assert age._timestamp(state["started_at_utc"]) <= self.clock.time()
        assert TOKEN not in (self.directory / "state.json").read_text()
        assert set(body) == {"name", "image", "gpu", "cloud", "disk", "ports", "env"}
        assert body["gpu"] == {"id": "offline-gpu", "count": 1, "minCudaVersion": "12.4"}
        assert body["disk"] == 10 and body["ports"] == ["8080/http"]
        assert "RUNPOD_API_KEY" not in body["env"]
        assert set(body["env"]) == {"AGE_ARTIFACT_TOKEN", "AETH01_RUN_ID",
                                   "AETH01_CANARY_REQUIRE_GPU", "AETH01_CANARY_TIMEOUT_SECONDS",
                                   "AETH01_CANARY_HOURLY_RATE", "AETH01_CANARY_MAX_DOLLAR_BUDGET"}
        self.pods["pod_1"] = dict(deepcopy(body), id="pod_1", status="RUNNING", cost=6)
        self.clock.advance(1)
        if self.create_hook:
            return self.create_hook(self)
        if self.create_error:
            raise self.create_error
        return deepcopy(self.pods["pod_1"])

    def get_pod(self, pod_id):
        self.events.append(("GET", pod_id))
        self.clock.advance(1)
        if pod_id in self.deleted:
            if self.confirmation_failures:
                self.confirmation_failures -= 1
                raise RuntimeError("offline confirmation error")
            if self.termination_status:
                return dict(deepcopy(self.pods[pod_id]), status=self.termination_status, cost=0)
            return None
        if self.get_hook:
            return self.get_hook(self, pod_id)
        return deepcopy(self.pods.get(pod_id))

    def list_pods(self):
        self.events.append(("LIST",))
        self.list_count += 1
        if self.list_hook:
            return self.list_hook(self)
        return [deepcopy(pod) for pod_id, pod in self.pods.items() if pod_id not in self.deleted]

    def terminate_pod(self, pod_id):
        self.events.append(("DELETE", pod_id))
        if self.delete_hook:
            self.delete_hook(self, pod_id)
        if self.delete_failures:
            self.delete_failures -= 1
            raise RuntimeError("offline deletion error")
        already_deleted = pod_id in self.deleted
        if self.delete_effective:
            self.deleted.add(pod_id)
        # Real DELETE semantics: idempotent retries after a genuine ACK see 404.
        return "NOT_FOUND_404" if already_deleted else "ACK_204"


class Artifacts:
    def __init__(self, plan, events):
        self.events, self.hook = events, None
        c = plan["config"]
        self.receipt = {"run_id": plan["run_id"], "semantics_id": "aeth01.v1",
                        "backend": "cupy", "status": "PASS", "cases_expected": 300,
                        "cases_run": 300, "cases_matched": 300, "single_tick_trials": 200,
                        "multi_tick_trials": 20, "multi_tick_steps": 5, "rng_seed": 0,
                        "mismatches": [], "source_hashes": deepcopy(plan["source_hashes"]),
                        "started_at_utc": age._utc(EPOCH + 1),
                        "finished_at_utc": age._utc(EPOCH + 2),
                        "gpu_kernel_seconds": 0.25, "cpu_oracle_seconds": 0.5,
                        "python_version": "3.13.0", "numpy_version": "2.2.0", "cupy_version": "13.3.0",
                        "cost_context": {"hourly_rate_usd": c["hourly_rate_usd"],
                                         "max_dollar_budget_usd": c["canary_budget_usd"],
                                         "watchdog_timeout_seconds": c["canary_timeout_seconds"]}}
        self.result = {"run_id": plan["run_id"], "finished": True, "exit_code": 0}
        self.missing = set()

    def fetch(self, pod_id, name):
        self.events.append(("FETCH", pod_id, name))
        if self.hook:
            return self.hook(pod_id, name)
        if name in self.missing:
            return None
        if name == "receipt.json":
            return age._encode(self.receipt)
        if name == "result.json":
            return age._encode(self.result)
        return b"offline final canary log\n"


@pytest.fixture(autouse=True)
def forbid_live_clients(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("live client construction forbidden in offline tests")
    monkeypatch.setattr(age, "_live_clients", forbidden)
    import socket
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def _arm_reaper(directory, plan, secret=REAPER_SECRET, scheduler_id="offline-fixture-scheduler",
                acknowledged_at=EPOCH, manifest_sha256=None, cutoff_utc=None):
    """Simulate the independent reaper's own durable HMAC-bound acknowledgement
    of the pre-create manifest (B3 section 6). A real reaper would write this
    from genuinely separate infrastructure; here it is a test double.
    """
    manifest_raw = (Path(directory) / "reaper_manifest.json").read_bytes()
    digest = manifest_sha256 if manifest_sha256 is not None else age._sha(manifest_raw)
    ack = {"version": 1, "manifest_sha256": digest, "armed": True, "scheduler_id": scheduler_id,
           "cutoff_utc": cutoff_utc if cutoff_utc is not None else
           plan["config"]["independent_cutoff_deadline_utc"],
           "acknowledged_at_utc": age._utc(acknowledged_at),
           "manifest_hmac_sha256": hmac.new(secret.encode(), manifest_raw, hashlib.sha256).hexdigest()}
    age.atomic_write(Path(directory) / "reaper_ack.json", age._encode(ack))


@pytest.fixture
def rig(tmp_path):
    clock, events = FakeClock(), []
    directory = tmp_path / "run"
    c = config()
    summary = age.create_plan(c, directory, clock=clock)
    plan = read_json(directory / "plan.json")
    assert summary["reaper_manifest_sha256"] == age._sha((directory / "reaper_manifest.json").read_bytes())
    _arm_reaper(directory, plan)
    approval = {"approved": True, "run_id": summary["run_id"],
                "plan_sha256": summary["plan_sha256"], "expires_at_utc": age._utc(EPOCH + 100),
                "independent_billing_cutoff": {"attested": True,
                                               "deadline_utc": c["independent_cutoff_deadline_utc"],
                                               "reference": c["independent_cutoff_reference"]}}
    return SimpleNamespace(directory=directory, clock=clock, events=events, plan=plan,
                           approval=approval, provider=Provider(directory, clock, events),
                           artifacts=Artifacts(plan, events))


def launch(rig, **overrides):
    kwargs = dict(execute_paid_run=True, provider=rig.provider, artifacts=rig.artifacts,
                  artifact_token=TOKEN, reaper_secret=REAPER_SECRET, clock=rig.clock)
    kwargs.update(overrides)
    with patch.object(age.os, "environ", NoEnvironment()):
        return age.run(rig.directory, rig.approval, **kwargs)


def cleanup(rig):
    with patch.object(age.os, "environ", NoEnvironment()):
        return age.recover(rig.directory, provider=rig.provider, clock=rig.clock)


def reload_lifecycle(rig):
    plan, digest = age._load_plan(rig.directory)
    state = age._load_state(rig.directory, plan, digest)
    return age._Lifecycle(rig.directory, plan, state, rig.provider, None, rig.clock)


@pytest.fixture
def owned_lifecycle(rig, monkeypatch):
    # Stop just after the durable create adoption; subsequent interactions are
    # explicit so every intermediate evidence state can be reloaded from disk.
    with monkeypatch.context() as context:
        context.setattr(age._Lifecycle, "monitor", lambda self, pod_id: None)
        context.setattr(age._Lifecycle, "cleanup", lambda self: None)
        launch(rig)
    return reload_lifecycle(rig)


def scan_status(rig, lifecycle, status):
    rig.clock.advance(1)
    rig.provider.list_hook = lambda p: [dict(deepcopy(p.pods["pod_1"]), status=status)]
    lifecycle.reconcile()
    return reload_lifecycle(rig)


def test_plan_is_fresh_nonsecret_and_zero_credential_reads_or_network(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("network attempted")
    import socket
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    directory = tmp_path / "plan"
    with patch.object(age.os, "environ", NoEnvironment()):
        summary = age.create_plan(config(), directory, clock=FakeClock())
    plan = read_json(directory / "plan.json")
    assert summary["plan_sha256"] == age._sha((directory / "plan.json").read_bytes())
    assert len(plan["run_id"]) == 36
    assert plan["run_name"] == "aeth01-age-" + plan["run_id"]
    assert sum(plan["phases"].values()) == 240
    assert plan["quoted_lifetime_cost_usd"] <= 1.5
    assert all(plan["source_hashes"][name] == age._sha((age.HERE / name).read_bytes())
               for name in age.SOURCES)
    assert not (directory / "state.json").exists()
    assert "AGE_ARTIFACT_TOKEN" not in (directory / "plan.json").read_text()
    assert "No verified provider billing fuse" in summary["billing_risk"]
    with pytest.raises(age.ControllerError):
        age.create_plan(config(), directory, clock=FakeClock())


@pytest.mark.parametrize("key,value", [
    ("canary_budget_usd", 3.01), ("canary_budget_usd", 0), ("canary_budget_usd", -1),
    ("canary_budget_usd", True), ("canary_budget_usd", float("nan")),
    ("canary_budget_usd", float("inf")), ("remaining_budget_usd", 19.94),
    ("remaining_budget_usd", 2.99), ("remaining_budget_usd", False),
    ("remaining_budget_usd", float("nan")), ("hourly_rate_usd", 100),
    ("hourly_rate_usd", "6"), ("hourly_rate_usd", True), ("hourly_rate_usd", 0),
    ("hourly_rate_usd", float("inf")), ("hourly_rate_usd", 10 ** 400),
    ("max_lifetime_seconds", 901), ("max_lifetime_seconds", True),
    ("max_lifetime_seconds", 240.0), ("max_lifetime_seconds", 200),
    ("canary_timeout_seconds", 601), ("canary_timeout_seconds", False),
    ("image", "registry.example/aeth01:latest"), ("cloud", "OTHER"),
    ("independent_cutoff_deadline_utc", "2027-01-01T00:00:00"),
    ("independent_cutoff_deadline_utc", age._utc(EPOCH + 200)),
    ("independent_cutoff_deadline_utc", age._utc(EPOCH + 1801)),
    ("independent_cutoff_reference", ""), ("env", {"UNEXPECTED": "value"}),
])
def test_invalid_config_is_refused_without_directory(tmp_path, key, value):
    c = config()
    c[key] = value
    directory = tmp_path / "bad-plan"
    with pytest.raises(age.ControllerError):
        age.create_plan(c, directory, clock=FakeClock())
    assert not directory.exists()


@pytest.mark.parametrize("key,value", [
    ("approved", False), ("approved", 1), ("approved", "true"),
    ("run_id", "another-run"), ("plan_sha256", "0" * 64),
    ("expires_at_utc", age._utc(EPOCH)), ("expires_at_utc", age._utc(EPOCH + 1201)),
    ("expires_at_utc", "not-a-date"), ("independent_billing_cutoff", None),
])
def test_invalid_approval_zero_calls(rig, key, value):
    rig.approval[key] = value
    with pytest.raises(age.ControllerError):
        launch(rig)
    assert rig.events == []
    assert not (rig.directory / "state.json").exists()


@pytest.mark.parametrize("key,value", [
    ("attested", 1), ("attested", False), ("reference", "different"),
    ("deadline_utc", age._utc(EPOCH + 1201)),
])
def test_independent_cutoff_requires_exact_attestation(rig, key, value):
    rig.approval["independent_billing_cutoff"][key] = value
    with pytest.raises(age.ControllerError):
        launch(rig)
    assert rig.events == []


@pytest.mark.parametrize("flag", [False, None, 1, "true"])
def test_paid_flag_is_explicit_and_precedes_all_calls(rig, flag):
    with pytest.raises(age.ControllerError):
        launch(rig, execute_paid_run=flag)
    assert rig.events == []


@pytest.mark.parametrize("token", ["", "a" * 31, "a" * 4097, "a" * 32 + "\n", "a" * 32 + "\u00e9"])
def test_artifact_token_gate_zero_calls(rig, token):
    with pytest.raises(age.ControllerError):
        launch(rig, artifact_token=token)
    assert rig.events == []


def test_intent_write_failure_prevents_post(rig, monkeypatch):
    def fail(*args):
        raise OSError("offline disk full")
    monkeypatch.setattr(age, "atomic_write", fail)
    with pytest.raises(age.ControllerError, match="CREATE_INTENT_WRITE_FAILED"):
        launch(rig)
    assert rig.events == []


def test_pass_requires_saved_hashed_artifacts_before_delete_and_confirmation(rig, monkeypatch):
    original = age.atomic_write
    def recording(path, raw):
        original(path, raw)
        rig.events.append(("DURABLE", Path(path).name))
    monkeypatch.setattr(age, "atomic_write", recording)
    def before_delete(provider, pod_id):
        state = read_json(rig.directory / "state.json")
        assert state["science_verdict"] == "PASS"
        assert set(state["artifacts"][pod_id]) == {"result.json", "receipt.json", "canary.log"}
        for name, digest in state["artifacts"][pod_id].items():
            assert digest == age._sha((rig.directory / "artifacts" / pod_id / name).read_bytes())
    rig.provider.delete_hook = before_delete
    result = launch(rig)
    assert result["verdict"] == result["science_verdict"] == "PASS"
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED" and result["exit_code"] == 0
    assert result["journal_ok"] is True
    post = rig.events.index(("POST",))
    delete = rig.events.index(("DELETE", "pod_1"))
    assert rig.events.index(("DURABLE", "state.json")) < post
    assert all(rig.events.index(("DURABLE", n)) < delete for n in ("receipt.json", "canary.log", "result.json"))
    assert ("GET", "pod_1") in rig.events[delete + 1:]
    assert rig.provider.create_count == 1
    # B2: reconciliation is unconditional and run-wide, even on a clean success.
    assert rig.provider.list_count >= 1
    state = read_json(rig.directory / "state.json")
    assert state["owned_ids"] == state["terminated_ids"] == ["pod_1"]
    for path in rig.directory.rglob("*"):
        if path.is_file():
            assert TOKEN.encode() not in path.read_bytes()


@pytest.mark.parametrize("missing", ["result.json", "receipt.json", "canary.log"])
def test_temporary_missing_artifacts_are_polled_not_prematurely_deleted(rig, missing):
    original = rig.artifacts.fetch
    counts = {}
    def delayed(pod_id, name):
        counts[name] = counts.get(name, 0) + 1
        if name == missing and counts[name] < 3:
            return None
        with patch.object(rig.artifacts, "hook", None):
            return original(pod_id, name)
    rig.artifacts.hook = delayed
    result = launch(rig)
    assert result["verdict"] == "PASS"
    assert counts[missing] == 3
    assert len(rig.clock.sleeps) >= 2


@pytest.mark.parametrize("missing", ["result.json", "receipt.json", "canary.log"])
def test_permanently_missing_artifacts_timeout_and_cleanup(rig, missing):
    rig.artifacts.missing.add(missing)
    result = launch(rig)
    assert result["exit_code"] != 0 and result["science_verdict"] != "PASS"
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.clock.time() - EPOCH <= 240
    assert rig.provider.deleted == {"pod_1"}


@pytest.mark.parametrize("key,value", [
    ("backend", "numpy_fallback"), ("run_id", "another-run"), ("run_id", None),
    ("status", "FAIL_INCOMPLETE"), ("cases_run", 299), ("cases_expected", True),
    ("cases_matched", 0), ("single_tick_trials", 199), ("multi_tick_trials", 19),
    ("multi_tick_steps", 4), ("rng_seed", False), ("mismatches", [{"difference": 1}]),
    ("source_hashes", {}), ("gpu_kernel_seconds", -0.1), ("cpu_oracle_seconds", True),
    ("gpu_kernel_seconds", 2.0), ("finished_at_utc", None),
    ("started_at_utc", age._utc(EPOCH - 1)), ("finished_at_utc", age._utc(EPOCH + 200)),
    ("finished_at_utc", "invalid"), ("cupy_version", None), ("python_version", ""),
    ("numpy_version", "garbage"), ("cost_context", {}),
])
def test_invalid_or_fallback_receipt_never_passes(rig, key, value):
    rig.artifacts.receipt[key] = value
    result = launch(rig)
    assert result["verdict"] == "FAIL" and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}


def test_source_hash_mismatch(rig):
    rig.artifacts.receipt["source_hashes"]["run_canary.py"] = "0" * 64
    assert launch(rig)["science_verdict"] == "FAIL"
    assert rig.provider.deleted == {"pod_1"}


@pytest.mark.parametrize("name,payload", [("receipt.json", b"not json"),
                                         ("receipt.json", b'{"value": NaN}'),
                                         ("result.json", b'{"finished":true,"finished":false}'),
                                         ("result.json", b"[]")])
def test_malformed_artifacts_cleanup(rig, name, payload):
    original = rig.artifacts.fetch
    def malformed(pod_id, requested):
        if requested == name:
            return payload
        with patch.object(rig.artifacts, "hook", None):
            return original(pod_id, requested)
    rig.artifacts.hook = malformed
    assert launch(rig)["verdict"] == "FAIL"
    assert rig.provider.deleted == {"pod_1"}


@pytest.mark.parametrize("key,value", [("exit_code", True), ("exit_code", "0"),
                                      ("exit_code", 1), ("exit_code", 124),
                                      ("finished", 1), ("finished", False),
                                      ("run_id", "wrong-run")])
def test_final_result_is_bound_finished_and_integer_zero(rig, key, value):
    rig.artifacts.result[key] = value
    assert launch(rig)["verdict"] == "FAIL"
    assert rig.provider.deleted == {"pod_1"}


@pytest.mark.parametrize("status", ["PROVISIONING", "STARTING", "EXITED", "ERROR", "TERMINATED", "UNKNOWN", None])
def test_status_is_not_process_success_and_provisioning_is_bounded(rig, status):
    def status_reply(provider, pod_id):
        return dict(provider.pods[pod_id], status=status)
    rig.provider.get_hook = status_reply
    result = launch(rig)
    assert result["verdict"] == "FAIL" and result["science_verdict"] == "FAIL"
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.clock.time() - EPOCH < 240


@pytest.mark.parametrize("rate", [None, False, 0, -1, "6", 6.01, float("inf"), float("nan")])
def test_missing_invalid_or_overquote_rate_causes_cleanup(rig, rate):
    rig.provider.get_hook = lambda provider, pod_id: dict(provider.pods[pod_id], cost=rate)
    assert launch(rig)["verdict"] == "FAIL"
    assert rig.provider.deleted == {"pod_1"}


def test_rate_drift_after_initial_valid_quote(rig):
    rig.artifacts.missing.add("result.json")
    calls = []
    def drifting(provider, pod_id):
        calls.append(pod_id)
        return dict(provider.pods[pod_id], cost=6 if len(calls) == 1 else 7)
    rig.provider.get_hook = drifting
    assert launch(rig)["verdict"] == "FAIL"
    assert len(calls) == 2
    assert rig.provider.deleted == {"pod_1"}


def test_lost_create_response_reconciles_repeatedly_without_post_retry(rig):
    rig.provider.create_error = RuntimeError("offline response lost")
    # Eventually-consistent inventory: absent on the first scan, then visible
    # until actually deleted. Late discovery leaves only one remaining round
    # for post-delete absence corroboration -- not enough to reach the B1
    # evidence bar, so this correctly stays LOCAL_CLEANUP_UNRESOLVED (loud,
    # not falsely confirmed) and the durable obligation passes to the reaper.
    rig.provider.list_hook = lambda p: ([] if p.list_count == 1
                                        else ([] if "pod_1" in p.deleted
                                              else [deepcopy(p.pods["pod_1"])]))
    result = launch(rig)
    assert result["verdict"] == "CLEANUP_UNRESOLVED" and result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert rig.provider.list_count == age.CLEANUP_ROUNDS
    assert rig.provider.create_count == 1 and rig.provider.deleted == {"pod_1"}


def test_unresolved_create_retains_intent_and_never_reposts(rig):
    rig.provider.create_error = RuntimeError("offline response lost")
    rig.provider.list_hook = lambda p: []
    result = launch(rig)
    assert result["verdict"] == "CLEANUP_UNRESOLVED"
    assert read_json(rig.directory / "state.json")["owned_ids"] == []
    assert rig.provider.create_count == 1
    with pytest.raises(age.ControllerError, match="RUN_ALREADY_LAUNCHED"):
        launch(rig)
    assert rig.provider.create_count == 1
    rig.provider.list_hook = None
    assert cleanup(rig)["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.create_count == 1


def test_restart_from_create_intent_recovers_without_approval_artifact_token_or_post(rig, monkeypatch):
    # Emulate process death after POST and before the response/owned-id journal.
    rig.provider.create_error = KeyboardInterrupt()
    with monkeypatch.context() as context:
        context.setattr(age._Lifecycle, "cleanup", lambda self: None)
        launch(rig)
    persisted = read_json(rig.directory / "state.json")
    assert persisted["phase"] == "CREATE_INTENT" and persisted["owned_ids"] == []
    rig.clock.advance(1300)  # Approval AND the live deadline have expired.
    rig.approval.clear()
    result = cleanup(rig)
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED" and result["exit_code"] != 0
    assert rig.provider.create_count == 1 and rig.provider.deleted == {"pod_1"}
    assert not any(event[0] == "FETCH" for event in rig.events)


@pytest.mark.parametrize("malformation", ["id_only", "wrong_image", "wrong_name", "wrong_run"])
def test_unverified_create_response_is_not_trusted_but_exact_inventory_is(rig, malformation):
    def malformed(provider):
        response = deepcopy(provider.pods["pod_1"])
        if malformation == "id_only":
            return {"id": "unrelated_response_id"}
        if malformation == "wrong_image":
            response["image"] = "wrong"
        elif malformation == "wrong_name":
            response["name"] = "wrong"
        else:
            response["env"]["AETH01_RUN_ID"] = "wrong"
        response["id"] = "unrelated_response_id"
        return response
    rig.provider.create_hook = malformed
    result = launch(rig)
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}
    assert read_json(rig.directory / "state.json")["owned_ids"] == ["pod_1"]


def test_exact_duplicates_are_all_cleaned_without_permanent_ambiguity(rig):
    def lost_with_duplicates(provider):
        provider.pods["pod_2"] = dict(deepcopy(provider.pods["pod_1"]), id="pod_2")
        raise RuntimeError("offline lost duplicate response")
    rig.provider.create_hook = lost_with_duplicates
    result = launch(rig)
    assert result["verdict"] == "FAIL"  # Lost create still cannot award science success.
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert result["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_CONFIRMED"
    assert result["ownership_ambiguous"] is False
    assert set(result["owned_ids"]) == {"pod_1", "pod_2"}
    assert result["reconciliation_required"] is True  # The independent horizon remains.
    assert rig.provider.deleted == {"pod_1", "pod_2"}
    assert rig.provider.create_count == 1


def test_unrelated_pods_are_never_deleted(rig):
    def add_unrelated(provider):
        for pod_id, changes in (("other_name", {"name": "unrelated"}),
                                ("similar_name", {"name": provider.pods["pod_1"]["name"] + "-other"}),
                                ("other_image", {"image": "unrelated"}),
                                ("other_run", {"env": {"AETH01_RUN_ID": "unrelated"}}),
                                ("fully_unrelated", {"name": "other", "image": "other", "env": {}})):
            provider.pods[pod_id] = dict(deepcopy(provider.pods["pod_1"]), id=pod_id, **changes)
        raise RuntimeError("offline lost response")
    rig.provider.create_hook = add_unrelated
    result = launch(rig)
    assert result["verdict"] == "FAIL"
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert result["ownership_ambiguous"] is False
    assert rig.provider.deleted == {"pod_1"}
    assert set(read_json(rig.directory / "state.json")["owned_ids"]) == {"pod_1"}


def test_failed_inventory_does_not_claim_cleanup_confirmed(rig):
    rig.provider.create_error = RuntimeError("offline response lost")
    def inventory(provider):
        if provider.list_count == 2:
            raise RuntimeError("offline inventory failed")
        return [deepcopy(provider.pods["pod_1"])]
    rig.provider.list_hook = inventory
    assert launch(rig)["verdict"] == "CLEANUP_UNRESOLVED"
    assert rig.provider.deleted == {"pod_1"}


def test_duplicate_launch_is_rejected_even_after_success(rig):
    assert launch(rig)["verdict"] == "PASS"
    events = list(rig.events)
    with pytest.raises(age.ControllerError, match="RUN_ALREADY_LAUNCHED"):
        launch(rig)
    assert rig.events == events


def test_os_lock_rejects_overlap_and_is_released_on_exception(rig):
    with pytest.raises(KeyboardInterrupt):
        with age.RunLock(rig.directory):
            with pytest.raises(age.ControllerError, match="RUN_LOCKED_OR_UNAVAILABLE"):
                launch(rig)
            assert rig.events == []
            raise KeyboardInterrupt()
    assert (rig.directory / "controller.lock").exists()
    assert launch(rig)["verdict"] == "PASS"


def test_teardown_failure_is_not_success_and_recovery_retries(rig):
    rig.provider.delete_failures = 100
    result = launch(rig)
    assert result["science_verdict"] == "PASS"
    assert result["verdict"] == "CLEANUP_UNRESOLVED" and result["exit_code"] != 0
    # B2: reconciliation now runs before AND after each round's deletion pass.
    assert sum(e[0] == "DELETE" for e in rig.events) == 2 * age.CLEANUP_ROUNDS
    rig.provider.delete_failures = 0
    rig.clock.advance(1300)
    assert cleanup(rig)["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.create_count == 1


@pytest.mark.parametrize("mode", ["delete_error", "confirmation_error", "terminated"])
def test_cleanup_retries_and_requires_get_confirmation(rig, mode):
    if mode == "delete_error":
        rig.provider.delete_failures = 1
    elif mode == "confirmation_error":
        rig.provider.confirmation_failures = 1
    else:
        rig.provider.termination_status = "TERMINATED"
    result = launch(rig)
    assert result["verdict"] == "PASS"
    if mode == "delete_error":
        assert sum(e[0] == "DELETE" for e in rig.events) >= 2
    elif mode == "confirmation_error":
        # A real ACK is corroborated by two complete inventory scans, not by
        # retrying an already-acknowledged DELETE/failed GET indefinitely.
        rec = result["pod_evidence"]["pod_1"]
        assert any(e["kind"] == "UNKNOWN" for e in rec["history"])
        assert rec["absence_confirmations"] >= 2
        assert rig.provider.list_count >= 2


@pytest.mark.parametrize("mode", ["ineffective_delete", "exited_not_terminated"])
def test_delete_response_or_exited_status_alone_is_not_confirmation(rig, mode):
    if mode == "ineffective_delete":
        rig.provider.delete_effective = False
    else:
        rig.provider.termination_status = "EXITED"
    result = launch(rig)
    assert result["verdict"] == "CLEANUP_UNRESOLVED" and result["science_verdict"] == "PASS"
    assert result["exit_code"] != 0


def test_transient_confirmation_errors_do_not_block_reconciliation_based_confirmation(rig):
    # B1: a persistently failing per-ID GET must not block the independent,
    # LIST-based reconciliation route to confirmation (route b) -- inventory
    # reconciliation is an independent corroboration channel, not merely a
    # retry of the same fragile per-ID query.
    rig.provider.confirmation_failures = 100
    result = launch(rig)
    assert result["verdict"] == "PASS" and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"


@pytest.mark.parametrize("failure", [OSError("offline fetch error"), KeyboardInterrupt()])
def test_artifact_error_or_interrupt_does_not_block_deletion(rig, failure):
    def fail(pod_id, name):
        raise failure
    rig.artifacts.hook = fail
    result = launch(rig)
    assert result["verdict"] == "FAIL" and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}


@pytest.mark.parametrize("target", ["artifacts", "all_after_intent", "final_journal"])
def test_disk_full_after_create_keeps_in_memory_ownership_and_deletes(rig, monkeypatch, target):
    original = age.atomic_write
    def disk_full(path, raw):
        path = Path(path)
        if ((target == "artifacts" and "artifacts" in path.parts)
                or (target == "all_after_intent" and rig.provider.create_count)
                or (target == "final_journal" and path.name == "state.json"
                    and json.loads(raw)["phase"] == "DONE")):
            raise OSError("offline disk full")
        original(path, raw)
    monkeypatch.setattr(age, "atomic_write", disk_full)
    result = launch(rig)
    assert result["exit_code"] != 0 and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}
    assert rig.provider.create_count == 1


def test_interruption_during_create_is_reconciled(rig):
    rig.provider.create_error = KeyboardInterrupt()
    result = launch(rig)
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED" and result["exit_code"] != 0
    assert rig.provider.create_count == 1 and rig.provider.deleted == {"pod_1"}


def test_live_wall_clock_backwards_fails_closed_but_deletes(rig):
    def backwards(provider, pod_id):
        provider.clock.wall = EPOCH - 20
        return deepcopy(provider.pods[pod_id])
    rig.provider.get_hook = backwards
    result = launch(rig)
    # A persistent backwards-wall fault fails the inter-round wait closed
    # (existing invariant), which now also means a second independent
    # reconciliation scan cannot run -- correctly leaving this UNRESOLVED
    # and loud rather than confirmed on a single scan's evidence (B1/B2).
    assert result["exit_code"] != 0 and result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert rig.provider.deleted == {"pod_1"}


def test_recovery_wall_clock_backwards_does_not_extend_wait_or_block_delete(rig):
    rig.provider.delete_failures = 100
    launch(rig)
    rig.provider.delete_failures = 0
    rig.clock.wall = EPOCH - 20
    sleeps = len(rig.clock.sleeps)
    result = cleanup(rig)
    assert result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED" and result["exit_code"] != 0
    assert rig.provider.deleted == {"pod_1"}
    assert len(rig.clock.sleeps) == sleeps


def test_create_latency_counts_from_before_post(rig):
    def slow_create(provider):
        provider.clock.advance(250)
        return deepcopy(provider.pods["pod_1"])
    rig.provider.create_hook = slow_create
    result = launch(rig)
    assert result["exit_code"] != 0 and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}
    assert not any(e[0] == "FETCH" for e in rig.events)


def test_expired_recovery_uses_emergency_window_for_transient_delete_retry(rig):
    rig.provider.delete_failures = 100
    launch(rig)
    rig.clock.advance(1300)
    rig.provider.delete_failures = 1
    before = sum(e[0] == "DELETE" for e in rig.events)
    result = cleanup(rig)
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    # B2: idempotent retries continue until independent reconciliation
    # corroborates absence; the exact count is a round-timing detail.
    assert sum(e[0] == "DELETE" for e in rig.events) - before >= 2
    assert result["verdict"] != "PASS"


def test_known_id_deleted_before_reconciliation_can_cross_original_deadline(rig):
    rig.provider.create_error = RuntimeError("offline lost create")
    rig.provider.delete_failures = 100
    launch(rig)
    rig.provider.delete_failures = 0
    state = read_json(rig.directory / "state.json")
    rig.clock.advance(age._timestamp(state["deadline_utc"]) - rig.clock.time() - 1)
    def slow_list(provider):
        assert "pod_1" in provider.deleted
        provider.clock.advance(2)
        return []
    rig.provider.list_hook = slow_list
    assert cleanup(rig)["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}


def test_partial_inventory_failure_still_deletes_positive_owned_records(rig):
    rig.provider.create_error = RuntimeError("offline lost create")
    def partial(visitor):
        visitor(deepcopy(rig.provider.pods["pod_1"]))
        # Ownership must already be durable when the next page fails.
        assert read_json(rig.directory / "state.json")["owned_ids"] == ["pod_1"]
        raise RuntimeError("offline later page failure")
    rig.provider.visit_pods = partial
    result = launch(rig)
    assert result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert rig.provider.deleted == {"pod_1"}
    assert rig.provider.create_count == 1


def test_late_first_running_status_exceeds_boot_pull_reserve(rig):
    def late_create(provider):
        provider.clock.advance(40)
        return deepcopy(provider.pods["pod_1"])
    rig.provider.create_hook = late_create
    result = launch(rig)
    assert result["science_verdict"] == "FAIL"
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"


def test_untrusted_exception_text_is_never_journaled_or_output(rig, capsys):
    marker = "OFFLINE_UNTRUSTED_EXCEPTION_DO_NOT_LOG"
    rig.provider.create_error = RuntimeError(marker)
    launch(rig)
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
    assert marker not in (rig.directory / "state.json").read_text()


def test_recover_missing_state_never_calls_provider(rig):
    with pytest.raises(age.ControllerError):
        cleanup(rig)
    assert rig.events == []


def test_cli_missing_paid_flag_does_not_read_approval_or_credentials(rig, capsys, monkeypatch):
    def forbidden(*args):
        raise AssertionError("file or credential read")
    monkeypatch.setattr(age, "_read", forbidden)
    with patch.object(age.os, "environ", NoEnvironment()):
        code = age.main(["run", "--run-dir", str(rig.directory), "--approval", "not-read.json"])
    assert code == 2
    assert json.loads(capsys.readouterr().out)["verdict"] == "REFUSED_OR_FAILED"
    assert rig.events == []


def test_cli_plan_uses_only_config_and_sources(tmp_path, monkeypatch, capsys):
    path = tmp_path / "config.json"
    path.write_bytes(age._encode(config()))
    monkeypatch.setattr(age.Clock, "time", staticmethod(lambda: EPOCH))
    with patch.object(age.os, "environ", NoEnvironment()):
        code = age.main(["plan", "--config", str(path), "--run-dir", str(tmp_path / "planned")])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["plan_sha256"]


@pytest.mark.parametrize("rate", [None, False, 7])
def test_invalid_create_quote_is_journaled_then_terminated(rig, rate):
    rig.provider.create_hook = lambda p: dict(deepcopy(p.pods["pod_1"]), cost=rate)
    result = launch(rig)
    assert result["verdict"] == "FAIL" and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert read_json(rig.directory / "state.json")["owned_ids"] == ["pod_1"]


def test_cleanup_latency_is_part_of_lifetime_bound(rig):
    rig.provider.delete_hook = lambda p, pod_id: p.clock.advance(250)
    result = launch(rig)
    # A single DELETE call already exhausts the whole cleanup budget, so a
    # second independent reconciliation scan cannot run in time -- correctly
    # LOCAL_CLEANUP_UNRESOLVED (loud) rather than confirmed early (B1/B2).
    assert result["science_verdict"] == "PASS" and result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert result["verdict"] == "CLEANUP_UNRESOLVED" and result["exit_code"] != 0
    assert rig.provider.deleted == {"pod_1"}


def test_monotonic_deadline_wins_when_wall_clock_stalls(rig):
    rig.artifacts.missing.add("result.json")
    def stalled_sleep(seconds):
        rig.clock.mono += 300
    rig.clock.sleep = stalled_sleep
    result = launch(rig)
    # The stalled monotonic clock also caps cleanup's own bounded window
    # after one round, so a second reconciliation scan cannot run in time.
    assert result["verdict"] == "CLEANUP_UNRESOLVED" and result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert rig.provider.deleted == {"pod_1"}


def test_fatal_exit_is_not_swallowed_but_still_cleans_up(rig):
    def exit_now(provider, pod_id):
        raise SystemExit(99)
    rig.provider.get_hook = exit_now
    with pytest.raises(SystemExit) as failure:
        launch(rig)
    assert failure.value.code == 99
    assert rig.provider.deleted == {"pod_1"}


def test_source_changes_since_plan_refuse_launch_before_provider_calls(rig, monkeypatch):
    original = age._read
    def changed(path, *args):
        if Path(path).name == "run_canary.py":
            return b"offline changed source fixture"
        return original(path, *args)
    monkeypatch.setattr(age, "_read", changed)
    with pytest.raises(age.ControllerError, match="LOCAL_SOURCE_CHANGED"):
        launch(rig)
    assert rig.events == []


def test_plan_bytes_are_bound_not_just_decoded_content(rig):
    path = rig.directory / "plan.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(age.ControllerError, match="APPROVAL_BINDING_FAILED"):
        launch(rig)
    assert rig.events == []


def test_atomic_writer_fsyncs_before_replace_and_keeps_old_snapshot_on_error(tmp_path, monkeypatch):
    path = tmp_path / "snapshot.json"
    path.write_bytes(b"old")
    original_sync, original_replace = age.os.fsync, age.os.replace
    events = []
    def sync(fd):
        events.append("fsync")
        original_sync(fd)
    def replace(source, destination):
        events.append("replace")
        original_replace(source, destination)
    monkeypatch.setattr(age.os, "fsync", sync)
    monkeypatch.setattr(age.os, "replace", replace)
    age.atomic_write(path, b"new")
    assert events[:2] == ["fsync", "replace"] and path.read_bytes() == b"new"
    def failed_sync(fd):
        raise OSError("offline fsync failure")
    monkeypatch.setattr(age.os, "fsync", failed_sync)
    with pytest.raises(OSError):
        age.atomic_write(path, b"not-published")
    assert path.read_bytes() == b"new"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["snapshot.json"]


def test_v1_price_field_is_not_accepted_as_v2_cost(rig):
    def obsolete(provider):
        pod = deepcopy(provider.pods["pod_1"])
        pod["costPerHr"] = pod.pop("cost")
        return pod
    rig.provider.create_hook = obsolete
    result = launch(rig)
    assert result["verdict"] == "FAIL"
    assert read_json(rig.directory / "state.json")["reason"] == "INVALID_OR_OVERQUOTE_RATE"
    assert rig.provider.deleted == {"pod_1"}


def test_sigterm_interrupt_uses_cleanup_path(rig):
    def terminated(provider, pod_id):
        age._interrupt(age.signal.SIGTERM, None)
    rig.provider.get_hook = terminated
    result = launch(rig)
    assert result["verdict"] == "FAIL" and result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert rig.provider.deleted == {"pod_1"}


def test_cli_restores_sigterm_handler_after_refusal(rig, capsys):
    previous = age.signal.getsignal(age.signal.SIGTERM)
    assert age.main(["run", "--run-dir", str(rig.directory), "--approval", "unused"]) == 2
    assert age.signal.getsignal(age.signal.SIGTERM) == previous
    assert json.loads(capsys.readouterr().out)["reason"] == "PAID_EXECUTION_FLAG_REQUIRED"


def test_duplicate_inventory_does_not_multiply_cleanup_time_without_bound(rig):
    def duplicate_create(provider):
        for i in range(2, 101):
            provider.pods[f"pod_{i}"] = dict(deepcopy(provider.pods["pod_1"]), id=f"pod_{i}")
        raise RuntimeError("offline lost-create response")
    rig.provider.create_hook = duplicate_create
    rig.provider.delete_hook = lambda p, pod_id: p.clock.advance(50)
    result = launch(rig)
    assert result["verdict"] == "CLEANUP_UNRESOLVED"
    assert 0 < len(rig.provider.deleted) < 100
    assert rig.clock.time() - EPOCH < 200
    # Every discovered ID is preserved for a later bounded recovery attempt.
    # Checked in-memory (the outcome, not a re-read of state.json): on this
    # Windows test environment, rapid sequential durable commits can rarely
    # lose the last few to real OS-level replace contention -- a pre-existing
    # characteristic of atomic_write()/best_commit() unrelated to this
    # repair's B1/B2 logic (reproduced on the unmodified base commit too).
    # The in-memory outcome is unaffected by that and reliably shows all 100.
    assert len(result["pod_evidence"]) == 100


def test_real_transport_wiring_uses_documented_v2_shapes(rig, monkeypatch):
    import io
    import sys
    import types
    spec = importlib.util.spec_from_file_location("_age_wiring_api", age.HERE / "runpod_api.py")
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    class Response(io.BytesIO):
        def __init__(self, status, raw):
            super().__init__(raw)
            self.status = status
        def getcode(self):
            return self.status
    class Wire:
        def open(self, request, timeout):
            assert timeout == 10
            if request.full_url.startswith("https://api.runpod.io/v2/pods"):
                assert request.get_header("Authorization") == "Bearer offline-api-fixture"
                method = request.get_method()
                if method == "POST":
                    return Response(201, age._encode(rig.provider.create_pod(json.loads(request.data))))
                if method == "DELETE":
                    # B2: honestly reflect ACK_204 vs NOT_FOUND_404, never collapse them.
                    result = rig.provider.terminate_pod(request.full_url.rsplit("/", 1)[1])
                    return Response(204 if result == "ACK_204" else 404, b"")
                if request.full_url == "https://api.runpod.io/v2/pods":
                    # B2: reconciliation now genuinely lists inventory over this wire.
                    page = {"pods": rig.provider.list_pods(),
                           "pagination": {"nextCursor": None, "hasNextPage": False}}
                    return Response(200, age._encode(page))
                pod = rig.provider.get_pod(request.full_url.rsplit("/", 1)[1])
                return Response(200 if pod else 404, age._encode(pod) if pod else b"")
            assert request.full_url.startswith("https://pod_1-8080.proxy.runpod.net/")
            assert request.get_header("Authorization") == "Bearer " + TOKEN
            name = request.full_url.rsplit("/", 1)[1]
            return Response(200, rig.artifacts.fetch("pod_1", name))
    wire = Wire()
    # Exercise the actual lazy client-construction seam with only fake env/data.
    shim = types.ModuleType("runpod_api")
    shim.RunPodAPI = lambda: api.RunPodAPI(wire)
    shim.ArtifactClient = lambda: api.ArtifactClient(wire)
    monkeypatch.setitem(sys.modules, "runpod_api", shim)
    with patch.dict(age.os.environ, {"RUNPOD_API_KEY": "offline-api-fixture",
                                    "AGE_ARTIFACT_TOKEN": TOKEN}, clear=True):
        provider, artifacts, token = LIVE_CLIENTS()
    assert token == TOKEN
    result = launch(rig, provider=provider, artifacts=artifacts)
    assert result["verdict"] == "PASS"
    assert rig.provider.deleted == {"pod_1"}


def test_live_credentials_must_use_distinct_artifact_token(monkeypatch):
    import sys
    import types
    shim = types.ModuleType("runpod_api")
    def forbidden():
        raise AssertionError("client must not be constructed")
    shim.RunPodAPI = shim.ArtifactClient = forbidden
    monkeypatch.setitem(sys.modules, "runpod_api", shim)
    with patch.dict(age.os.environ, {"RUNPOD_API_KEY": TOKEN, "AGE_ARTIFACT_TOKEN": TOKEN}, clear=True):
        with pytest.raises(age.ControllerError, match="DISTINCT_ARTIFACT_TOKEN_REQUIRED"):
            LIVE_CLIENTS()


# --- B3: reaper pre-create handoff must gate the one allowed POST ---------

def test_reaper_not_armed_without_ack_file_zero_calls(rig):
    (rig.directory / "reaper_ack.json").unlink()
    with pytest.raises(age.ControllerError, match="FILE_READ_FAILED"):
        launch(rig)
    assert rig.events == []


def test_reaper_ack_manifest_mismatch_refuses_post_zero_calls(rig):
    ack = read_json(rig.directory / "reaper_ack.json")
    ack["manifest_sha256"] = "0" * 64
    age.atomic_write(rig.directory / "reaper_ack.json", age._encode(ack))
    with pytest.raises(age.ControllerError, match="REAPER_NOT_ARMED"):
        launch(rig)
    assert rig.events == []


def test_reaper_wrong_shared_secret_refuses_post_zero_calls(rig):
    with pytest.raises(age.ControllerError, match="REAPER_NOT_ARMED"):
        launch(rig, reaper_secret="wrong-fixture-reaper-secret-0123456789")
    assert rig.events == []


def test_reaper_ack_cutoff_tamper_refuses_post_despite_valid_hmac(rig):
    # The HMAC alone is not enough: the cutoff field itself must also match
    # the plan exactly, closing off a swapped-cutoff substitution attempt.
    manifest_raw = (rig.directory / "reaper_manifest.json").read_bytes()
    ack = read_json(rig.directory / "reaper_ack.json")
    ack["cutoff_utc"] = age._utc(EPOCH + 1)
    ack["manifest_hmac_sha256"] = hmac.new(REAPER_SECRET.encode(), manifest_raw,
                                           hashlib.sha256).hexdigest()
    age.atomic_write(rig.directory / "reaper_ack.json", age._encode(ack))
    with pytest.raises(age.ControllerError, match="REAPER_NOT_ARMED"):
        launch(rig)
    assert rig.events == []


def test_reaper_ack_for_a_different_plan_is_rejected(rig, tmp_path):
    other = tmp_path / "other-run"
    other_config = config()
    other_summary = age.create_plan(other_config, other, clock=rig.clock)
    other_plan = read_json(other / "plan.json")
    _arm_reaper(other, other_plan)
    foreign_ack = (other / "reaper_ack.json").read_bytes()
    age.atomic_write(rig.directory / "reaper_ack.json", foreign_ack)
    with pytest.raises(age.ControllerError, match="REAPER_NOT_ARMED"):
        launch(rig)
    assert rig.events == []


def test_reaper_manifest_is_a_pure_function_of_the_plan(rig):
    manifest = read_json(rig.directory / "reaper_manifest.json")
    assert manifest == age.reaper_manifest_document(rig.plan)
    assert manifest["run_id"] == rig.plan["run_id"]
    assert manifest["reconciliation_horizon_seconds"] == age.RECONCILIATION_HORIZON_SECONDS
    assert "AGE_ARTIFACT_TOKEN" not in json.dumps(manifest)


# --- B4: secret-safe diagnostics must preserve distinguishing evidence ----

class _FakeProviderError(Exception):
    """Mimics runpod_api.ProviderError's public shape without importing it."""

    def __init__(self, status=None, category=None):
        self.status = status
        self.category = category


@pytest.mark.parametrize("label,error,expected_outcome,expected_status", [
    ("auth_401", "status_error", "HTTP_OTHER", 401),
    ("schema_422", "status_error", "HTTP_OTHER", 422),
    ("malformed_response", "category_error", "SCHEMA_INVALID", None),
    ("transport", "plain_error", "TRANSPORT_UNKNOWN", None),
])
def test_diagnostics_distinguish_auth_schema_and_transport_create_failures(
        rig, label, error, expected_outcome, expected_status):
    if error == "status_error":
        rig.provider.create_error = _FakeProviderError(status=expected_status)
    elif error == "category_error":
        rig.provider.create_error = _FakeProviderError(category="SCHEMA_INVALID")
    else:
        rig.provider.create_error = RuntimeError("offline transport failure")
    launch(rig)
    state = read_json(rig.directory / "state.json")
    create_diags = [d for d in state["diagnostics"] if d["stage"] == "CREATE"]
    assert len(create_diags) == 1
    assert create_diags[0]["outcome"] == expected_outcome
    assert create_diags[0]["http_status"] == expected_status
    # B4 does not change the fixed, coarse top-level reason vocabulary; the
    # diagnostics list is what preserves the distinction the review asked for.
    assert state["reason"] == "CONTROLLER_FAILED"


def test_diagnostics_never_leak_secrets_or_raw_exception_text(rig):
    marker = "OFFLINE_UNTRUSTED_EXCEPTION_DO_NOT_LOG"
    rig.provider.create_error = _FakeProviderError(status=401)
    rig.provider.create_error.args = (marker,)
    launch(rig)
    raw = (rig.directory / "state.json").read_text()
    assert marker not in raw
    assert TOKEN not in raw and REAPER_SECRET not in raw
    diagnostics = read_json(rig.directory / "state.json")["diagnostics"]
    for entry in diagnostics:
        assert set(entry) == {"stage", "outcome", "http_status", "pod_status",
                              "elapsed_seconds", "attempt"}
        assert entry["stage"] in age._DIAG_STAGES
        assert entry["outcome"] in age._DIAG_OUTCOMES


def test_diagnostics_are_bounded_and_never_unbounded_growth(rig):
    rig.artifacts.missing.add("result.json")
    launch(rig)
    diagnostics = read_json(rig.directory / "state.json")["diagnostics"]
    assert len(diagnostics) <= age._DIAGNOSTICS_LIMIT
    assert len(diagnostics) > 0


def test_pod_error_and_exited_status_are_journaled_distinctly(rig):
    def status_reply(provider, pod_id):
        return dict(provider.pods[pod_id], status="ERROR")
    rig.provider.get_hook = status_reply
    launch(rig)
    diagnostics = read_json(rig.directory / "state.json")["diagnostics"]
    assert any(d["outcome"] == "POD_ERROR" for d in diagnostics)


@pytest.mark.parametrize("status", ["RUNNING", "PROVISIONING", "STARTING", "EXITED", "ERROR",
                                   "CREATED", "PENDING", "STOPPING", "STOPPED", "UNKNOWN", None,
                                   "OFFLINE_UNTRUSTED_STATUS_DO_NOT_LOG"])
def test_terminated_then_live_demotes_and_retries_after_reload(rig, owned_lifecycle, status):
    lifecycle = scan_status(rig, owned_lifecycle, "TERMINATED")
    terminated_history = deepcopy(lifecycle.state["pod_evidence"]["pod_1"]["history"])
    assert lifecycle.state["terminated_ids"] == ["pod_1"]
    lifecycle = scan_status(rig, lifecycle, status)
    rec = lifecycle.state["pod_evidence"]["pod_1"]
    assert rec["history"][:len(terminated_history)] == terminated_history
    assert rec["positive_termination_observed"] is True
    assert rec["current_termination_observed"] is False
    assert rec["contradictory_live_reappearance"] is True
    assert rec["cleanup_confidence"] == "UNRESOLVED"
    assert rec["delete_result"] != "ACK_204" and rec["absence_confirmations"] == 0
    assert lifecycle.state["terminated_ids"] == []
    rig.provider.list_hook = None
    result = cleanup(rig)
    assert ("DELETE", "pod_1") in rig.events
    assert result["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert result["pod_evidence"]["pod_1"]["positive_termination_observed"] is True
    assert "OFFLINE_UNTRUSTED_STATUS_DO_NOT_LOG" not in (rig.directory / "state.json").read_text()


def test_ack_absence_absence_running_requires_fresh_ack_after_reload(rig, owned_lifecycle):
    owned_lifecycle.terminate("pod_1")
    lifecycle = reload_lifecycle(rig)
    assert lifecycle.state["pod_evidence"]["pod_1"]["delete_result"] == "ACK_204"
    for expected in (1, 2):
        lifecycle.reconcile()
        lifecycle = reload_lifecycle(rig)
        assert lifecycle.state["pod_evidence"]["pod_1"]["absence_confirmations"] == expected
    assert lifecycle.state["terminated_ids"] == ["pod_1"]
    old_history = deepcopy(lifecycle.state["pod_evidence"]["pod_1"]["history"])
    lifecycle = scan_status(rig, lifecycle, "RUNNING")
    rec = lifecycle.state["pod_evidence"]["pod_1"]
    assert rec["history"][:len(old_history)] == old_history
    assert rec["cleanup_confidence"] == "UNRESOLVED"
    assert rec["absence_confirmations"] == 0 and rec["delete_result"] != "ACK_204"
    rig.provider.list_hook = lambda p: []
    for _ in range(2):
        lifecycle.reconcile()
        lifecycle = reload_lifecycle(rig)
    assert lifecycle.state["terminated_ids"] == []
    assert lifecycle.state["pod_evidence"]["pod_1"]["cleanup_confidence"] == "UNRESOLVED"
    rig.provider.deleted.clear()  # The reappearing pod needs a genuine fresh ACK.
    lifecycle.terminate("pod_1")
    lifecycle = reload_lifecycle(rig)
    for _ in range(2):
        lifecycle.reconcile()
        lifecycle = reload_lifecycle(rig)
    assert lifecycle.state["terminated_ids"] == ["pod_1"]
    assert sum(e["kind"] == "DELETE_RESULT" and e["result"] == "ACK_204"
               for e in lifecycle.state["pod_evidence"]["pod_1"]["history"]) == 2


def test_terminated_absent_running_terminated_preserves_history_across_reloads(rig, owned_lifecycle):
    lifecycle = scan_status(rig, owned_lifecycle, "TERMINATED")
    prefix = deepcopy(lifecycle.state["pod_evidence"]["pod_1"]["history"])
    rig.provider.list_hook = lambda p: []
    lifecycle.reconcile()
    lifecycle = reload_lifecycle(rig)
    assert lifecycle.state["pod_evidence"]["pod_1"]["current_termination_observed"] is True
    lifecycle = scan_status(rig, lifecycle, "RUNNING")
    assert lifecycle.state["terminated_ids"] == []
    lifecycle = scan_status(rig, lifecycle, "TERMINATED")
    rec = lifecycle.state["pod_evidence"]["pod_1"]
    assert rec["history"][:len(prefix)] == prefix
    assert [e["kind"] for e in rec["history"]][-3:] == ["ABSENT_SCAN", "OBSERVE", "OBSERVE"]
    assert sum(e["kind"] == "OBSERVE" and e["status"] == "TERMINATED"
               for e in rec["history"]) == 2
    assert rec["positive_termination_observed"] is rec["current_termination_observed"] is True
    assert rec["cleanup_confidence"] == "CONFIRMED"
    assert cleanup(rig)["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
    assert not any(e[0] == "DELETE" for e in rig.events)


@pytest.mark.parametrize("result", [None, "", "unknown", True, {}])
def test_unknown_delete_return_never_becomes_ack(rig, monkeypatch, result):
    original = rig.provider.terminate_pod
    def unknown(pod_id):
        original(pod_id)
        return result
    monkeypatch.setattr(rig.provider, "terminate_pod", unknown)
    outcome = launch(rig)
    assert outcome["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    rec = outcome["pod_evidence"]["pod_1"]
    assert rec["delete_result"] == "TRANSPORT_UNKNOWN"
    assert rec["absence_confirmations"] == 0
    assert all(e["result"] == "TRANSPORT_UNKNOWN" for e in rec["history"]
               if e["kind"] == "DELETE_RESULT")
    assert reload_lifecycle(rig).state["terminated_ids"] == []


def test_repeated_live_get_clears_each_ack_and_complete_scans_still_record_absence(rig, owned_lifecycle):
    rig.provider.delete_effective = False
    for _ in range(2):
        owned_lifecycle.terminate("pod_1")
        owned_lifecycle = reload_lifecycle(rig)
        rec = owned_lifecycle.state["pod_evidence"]["pod_1"]
        assert rec["delete_result"] != "ACK_204"
        assert rec["cleanup_confidence"] == "UNRESOLVED"
    rig.provider.list_hook = lambda p: []
    for _ in range(2):
        owned_lifecycle.reconcile()
    rec = reload_lifecycle(rig).state["pod_evidence"]["pod_1"]
    assert [e["kind"] for e in rec["history"]][-2:] == ["ABSENT_SCAN", "ABSENT_SCAN"]
    assert rec["cleanup_confidence"] == "UNRESOLVED"


def test_ack_after_visible_get_can_be_corroborated_by_complete_scans(rig, owned_lifecycle, monkeypatch):
    # Emulate process death after the durable ACK, before a GET can supply any
    # new visibility fact. LIST must independently witness complete absence.
    def stop(pod_id):
        raise SystemExit(99)
    monkeypatch.setattr(rig.provider, "get_pod", stop)
    with pytest.raises(SystemExit):
        owned_lifecycle.terminate("pod_1")
    owned_lifecycle = reload_lifecycle(rig)
    rec = owned_lifecycle.state["pod_evidence"]["pod_1"]
    assert rec["delete_result"] == "ACK_204" and rec["last_visibility"] == "VISIBLE"
    for _ in range(2):
        owned_lifecycle.reconcile()
    assert reload_lifecycle(rig).state["terminated_ids"] == ["pod_1"]


@pytest.mark.parametrize("change", ["wrong_id", "wrong_name", "wrong_image", "wrong_run"])
def test_get_conflicting_identity_at_known_id_remains_anomaly(rig, change):
    def conflict(provider, pod_id):
        pod = deepcopy(provider.pods[pod_id])
        if change == "wrong_run":
            pod["env"]["AETH01_RUN_ID"] = "other"
        else:
            pod[change.removeprefix("wrong_")] = "other"
        return pod
    rig.provider.get_hook = conflict
    result = launch(rig)
    assert rig.provider.deleted == {"pod_1"}
    assert result["ownership_ambiguous"] is True
    assert result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert any(e["kind"] == "OWNERSHIP_CONFLICT"
               for e in result["pod_evidence"]["pod_1"]["history"])


def test_recovery_does_not_delete_known_id_after_identity_conflict(rig, owned_lifecycle):
    rig.provider.pods["pod_1"]["image"] = "unrelated-image"
    owned_lifecycle.reconcile()
    result = cleanup(rig)
    assert not rig.provider.deleted
    assert not any(e[0] == "DELETE" for e in rig.events)
    assert result["ownership_ambiguous"] is True
    assert result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    # A fresh exact binding may resume deletion, but the anomaly stays loud.
    rig.provider.pods["pod_1"]["image"] = rig.plan["config"]["image"]
    lifecycle = reload_lifecycle(rig)
    lifecycle.reconcile()
    lifecycle.terminate("pod_1")
    assert rig.provider.deleted == {"pod_1"}
    assert lifecycle.outcome()["ownership_ambiguous"] is True


@pytest.mark.parametrize("reload", [False, True])
def test_conflict_recording_failure_never_authorizes_old_binding(
        rig, owned_lifecycle, monkeypatch, reload):
    rig.provider.pods["pod_1"]["image"] = "unrelated-image"
    def broken_record(*args, **kwargs):
        raise age.policy.EvidenceError("INVALID_UTC")
    with monkeypatch.context() as context:
        context.setattr(age.policy, "append_pod", broken_record)
        owned_lifecycle._observe_get("pod_1", deepcopy(rig.provider.pods["pod_1"]))
    lifecycle = reload_lifecycle(rig) if reload else owned_lifecycle
    lifecycle.terminate("pod_1")
    assert not rig.provider.deleted
    assert not any(e[0] == "DELETE" for e in rig.events)
    assert lifecycle.outcome()["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    # Fresh binding, not successful journal writing, governs safe targeting.
    rig.provider.pods["pod_1"]["image"] = rig.plan["config"]["image"]
    lifecycle.reconcile()
    lifecycle.terminate("pod_1")
    assert rig.provider.deleted == {"pod_1"}


@pytest.mark.parametrize("version", [1, 2, 4, True])
def test_recovery_explicitly_refuses_old_or_unknown_state_schema(rig, owned_lifecycle, version):
    state = read_json(rig.directory / "state.json")
    state["version"] = version
    age.atomic_write(rig.directory / "state.json", age._encode(state))
    before = list(rig.events)
    with pytest.raises(age.ControllerError, match="UNSUPPORTED_STATE_VERSION"):
        cleanup(rig)
    assert rig.events == before


@pytest.mark.parametrize("tamper", ["confidence", "no_history", "empty_history", "missing_record",
                                   "extra_record", "terminated_ids", "attempted_ids"])
def test_recovery_replays_evidence_and_refuses_missing_or_forged_facts(rig, owned_lifecycle, tamper):
    state = read_json(rig.directory / "state.json")
    rec = state["pod_evidence"]["pod_1"]
    if tamper == "confidence":
        rec["cleanup_confidence"] = "CONFIRMED"
        state["terminated_ids"] = ["pod_1"]
    elif tamper == "no_history":
        del rec["history"]
    elif tamper == "empty_history":
        state["pod_evidence"]["pod_1"] = age.policy.new_pod()
    elif tamper == "missing_record":
        state["pod_evidence"].clear()
    elif tamper == "extra_record":
        state["pod_evidence"]["other"] = deepcopy(rec)
    elif tamper == "terminated_ids":
        state["terminated_ids"] = ["pod_1"]
    else:
        state["delete_attempted_ids"] = ["pod_1"]
    age.atomic_write(rig.directory / "state.json", age._encode(state))
    before = list(rig.events)
    with pytest.raises(age.ControllerError, match="INVALID_STATE"):
        cleanup(rig)
    assert rig.events == before


def test_outcome_is_a_deep_snapshot_bound_to_the_manifest(rig, owned_lifecycle):
    first = owned_lifecycle.outcome()
    saved = deepcopy(first)
    assert first["version"] == 3 and first["policy_version"] == 1
    assert first["manifest"] == age.reaper_manifest_document(rig.plan)
    assert first["manifest_sha256"] == age._sha(age._encode(first["manifest"]))
    owned_lifecycle.terminate("pod_1")
    assert first == saved
    first["owned_ids"].clear()
    first["pod_evidence"]["pod_1"]["history"].clear()
    first["manifest"]["image"] = "changed"
    assert owned_lifecycle.state["owned_ids"] == ["pod_1"]
    assert owned_lifecycle.state["pod_evidence"]["pod_1"]["history"]
    assert owned_lifecycle.outcome()["manifest"]["image"] == rig.plan["config"]["image"]


def test_empty_known_set_is_vacuously_known_clean_but_not_locally_clean(rig):
    rig.provider.create_error = RuntimeError("offline lost response")
    rig.provider.list_hook = lambda p: []
    result = launch(rig)
    assert result["owned_ids"] == []
    assert result["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_CONFIRMED"
    assert result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert result["reconciliation_required"] is True


def test_evidence_record_failure_never_suppresses_delete(rig, monkeypatch):
    def fail(*args, **kwargs):
        raise age.policy.EvidenceError("OFFLINE_UNTRUSTED_RECORD_FAILURE")
    monkeypatch.setattr(age.policy, "append_pod", fail)
    result = launch(rig)
    assert rig.provider.deleted == {"pod_1"}
    assert result["journal_ok"] is False
    assert result["cleanup_status"] == "LOCAL_CLEANUP_UNRESOLVED"
    assert "OFFLINE_UNTRUSTED_RECORD_FAILURE" not in (rig.directory / "state.json").read_text()


@pytest.mark.parametrize("status", ["RUNNING", "TERMINATED"])
def test_late_get_positive_is_durable_before_phase_guard_refuses(rig, owned_lifecycle, status):
    def late(provider, pod_id):
        provider.clock.advance(121)
        return dict(deepcopy(provider.pods[pod_id]), status=status)
    rig.provider.get_hook = late
    with pytest.raises(age.ControllerError, match="LIFECYCLE_TIMEOUT"):
        owned_lifecycle.monitor("pod_1")
    rec = reload_lifecycle(rig).state["pod_evidence"]["pod_1"]
    assert rec["last_status"] == status
    assert rec["last_positive_at_utc"] == age.policy.utc(rig.clock.time())
    assert rec["history"][-1]["kind"] == "OBSERVE"


def test_partial_scan_failure_is_durable_and_never_adds_absence_witness(rig, owned_lifecycle):
    def partial(visitor):
        visitor(dict(deepcopy(rig.provider.pods["pod_1"]), status="TERMINATED"))
        assert read_json(rig.directory / "state.json")["pod_evidence"]["pod_1"]["last_status"] == "TERMINATED"
        raise RuntimeError("offline later-page failure")
    rig.provider.visit_pods = partial
    with pytest.raises(RuntimeError):
        owned_lifecycle.reconcile()
    rec = reload_lifecycle(rig).state["pod_evidence"]["pod_1"]
    assert [e["kind"] for e in rec["history"]][-2:] == ["OBSERVE", "SCAN_FAILED"]
    assert rec["absence_confirmations"] == 0
    assert not owned_lifecycle.state["reconciled"]


@pytest.fixture
def structured_reports(rig):
    local = launch(rig)
    manifest = deepcopy(local["manifest"])
    window = age.policy.new_window("offline-independent-window")
    start = age._timestamp(manifest["cutoff_utc"])
    horizon = manifest["reconciliation_horizon_seconds"]
    for offset in range(0, horizon + 1, 60):
        age.policy.observe_window(window, age.policy.utc(start + offset), 100.0 + offset,
                                  complete=True, owned_seen=False, cutoff=manifest["cutoff_utc"])
    reaper = {"version": 2, "policy_version": 1, "manifest": manifest,
              "observation_policy": "LIST_AND_KNOWN_GET_V1",
              "manifest_sha256": age._sha(age._encode(manifest)), "run_id": local["run_id"],
              "owned_ids": [], "pod_evidence": {}, "ownership_ambiguous": False,
              "journal_ok": True, "status": "REAPER_CLEANUP_CONFIRMED", "window": window,
              "known_owned_cleanup_status": "KNOWN_OWNED_CLEANUP_CONFIRMED",
              "reconciliation_window_status": "RECONCILIATION_COMPLETE"}
    return local, reaper, start + horizon


def test_combine_replays_structured_histories_and_full_independent_window(structured_reports, rig):
    local, reaper, now = structured_reports
    original = deepcopy((local, reaper))
    result = age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)
    assert result["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_CONFIRMED"
    assert result["reconciliation_window_status"] == "RECONCILIATION_COMPLETE"
    assert result["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"
    assert result["authoritative_local_state"] is True
    assert result["local_seal"]["state_sha256"] == local["state_sha256"]
    assert read_json(rig.directory / "cleanup_seal.json") == result
    assert (local, reaper) == original


def test_combine_refuses_trivial_confirmed_labels_without_facts(rig):
    launch(rig)
    local = {"run_id": "offline-run", "cleanup_status": "LOCAL_CLEANUP_CONFIRMED"}
    reaper = {"run_id": "offline-run", "status": "REAPER_CLEANUP_CONFIRMED"}
    with pytest.raises(age.ControllerError, match="^INVALID_CLEANUP_EVIDENCE$"):
        age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=EPOCH)


@pytest.mark.parametrize("side,key", [("local", "manifest"), ("local", "manifest_sha256"),
                                     ("local", "owned_ids"), ("local", "pod_evidence"),
                                     ("local", "journal_ok"), ("local", "policy_version"),
                                     ("local", "ownership_ambiguous"), ("local", "cleanup_status"),
                                     ("reaper", "window"), ("reaper", "status"),
                                     ("reaper", "pod_evidence"), ("reaper", "manifest")])
def test_combine_refuses_missing_facts(structured_reports, rig, side, key):
    local, reaper, now = structured_reports
    del (local if side == "local" else reaper)[key]
    with pytest.raises(age.ControllerError, match="^INVALID_CLEANUP_EVIDENCE$"):
        age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)


@pytest.mark.parametrize("tamper", ["manifest_digest", "manifest_binding", "cached_confidence", "no_history"])
def test_combine_refuses_forged_or_unbound_evidence(structured_reports, rig, tamper):
    local, reaper, now = structured_reports
    if tamper == "manifest_digest":
        reaper["manifest_sha256"] = "0" * 64
    elif tamper == "manifest_binding":
        reaper["manifest"]["image"] = "registry.example/other@sha256:" + "b" * 64
        reaper["manifest_sha256"] = age._sha(age._encode(reaper["manifest"]))
    elif tamper == "cached_confidence":
        local["pod_evidence"]["pod_1"]["cleanup_confidence"] = "UNRESOLVED"
    else:
        del local["pod_evidence"]["pod_1"]["history"]
    with pytest.raises(age.ControllerError, match="^INVALID_CLEANUP_EVIDENCE$"):
        age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)


@pytest.mark.parametrize("case", ["short_window", "stale_window", "newer_live", "reaper_only_live",
                                  "journal_failure", "local_unresolved", "reaper_unresolved"])
def test_pure_evaluation_does_not_trust_labels_but_cannot_attest_authority(structured_reports, case):
    local, reaper, now = structured_reports
    if case == "short_window":
        start = age._timestamp(reaper["manifest"]["cutoff_utc"])
        reaper["window"] = age.policy.new_window("offline-short-window")
        for offset in range(0, 21, 4):  # Six scans / 20 seconds is not 3600 seconds.
            age.policy.observe_window(reaper["window"], age.policy.utc(start + offset),
                                      100.0 + offset, complete=True, owned_seen=False,
                                      cutoff=reaper["manifest"]["cutoff_utc"])
        now = start + 20
    elif case == "stale_window":
        now += 61
    elif case == "newer_live":
        age.policy.append_pod(local["pod_evidence"]["pod_1"], "OBSERVE",
                              age.policy.utc(now), status="RUNNING")
    elif case == "reaper_only_live":
        reaper["owned_ids"].append("pod_2")
        reaper["pod_evidence"]["pod_2"] = age.policy.new_pod()
        age.policy.append_pod(reaper["pod_evidence"]["pod_2"], "OBSERVE",
                              reaper["manifest"]["cutoff_utc"], status="RUNNING")
    elif case == "journal_failure":
        local["journal_ok"] = False
    elif case == "local_unresolved":
        local["cleanup_status"] = "LOCAL_CLEANUP_UNRESOLVED"
    else:
        reaper["status"] = "REAPER_CLEANUP_UNRESOLVED"
    result = age.policy.aggregate(local, reaper, now=now)
    assert result["authoritative_local_state"] is False
    assert result["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_UNRESOLVED"
    if case in ("short_window", "stale_window", "newer_live", "reaper_only_live"):
        assert result["reconciliation_window_status"] == "RECONCILIATION_PENDING"
    if case in ("newer_live", "reaper_only_live"):
        assert result["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_UNRESOLVED"


def test_n2_report_a_rejected_after_newer_durable_live_evidence_b(structured_reports, rig):
    local_a, reaper, now = structured_reports
    # The reaper's claimed window is already in progress when recovery sees B.
    rig.clock.advance(age._timestamp(reaper["window"]["start_utc"]) + 1800 - rig.clock.time())
    lifecycle = reload_lifecycle(rig)
    lifecycle._observe_get("pod_1", dict(deepcopy(rig.provider.pods["pod_1"]), status="RUNNING"))
    local_b = lifecycle.outcome()
    assert local_b["state_sha256"] != local_a["state_sha256"]
    assert read_json(rig.directory / "state.json")["pod_evidence"]["pod_1"]["last_status"] == "RUNNING"
    with pytest.raises(age.ControllerError, match="STALE_LOCAL_OUTCOME"):
        age.combine_operational_cleanup(local_a, reaper, run_dir=rig.directory, now=now)
    assert not (rig.directory / "cleanup_seal.json").exists()
    result = age.combine_operational_cleanup(local_b, reaper, run_dir=rig.directory, now=now)
    assert result["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_UNRESOLVED"
    assert result["reconciliation_window_status"] == "RECONCILIATION_PENDING"
    assert result["exit_code"] == 2
    # Replacing only A's hash cannot hide its stale contents.
    local_a["state_sha256"] = local_b["state_sha256"]
    with pytest.raises(age.ControllerError, match="INVALID_CLEANUP_EVIDENCE"):
        age.combine_operational_cleanup(local_a, reaper, run_dir=rig.directory, now=now)


def test_n2_authoritative_source_is_required_and_cannot_be_offline(structured_reports, tmp_path):
    local, reaper, now = structured_reports
    with pytest.raises(age.ControllerError, match="AUTHORITATIVE_RUN_DIR_REQUIRED"):
        age.combine_operational_cleanup(local, reaper, now=now)
    with pytest.raises(age.ControllerError, match="RUN_LOCKED_OR_UNAVAILABLE"):
        age.combine_operational_cleanup(local, reaper, run_dir=tmp_path / "offline", now=now)


def test_n2_sealing_and_recovery_use_same_exclusive_lock(structured_reports, rig, monkeypatch):
    local, reaper, now = structured_reports
    before = list(rig.events)
    with age.RunLock(rig.directory):
        with pytest.raises(age.ControllerError, match="RUN_LOCKED_OR_UNAVAILABLE"):
            age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)
    original = age.policy.aggregate
    def while_locked(*args, **kwargs):
        with pytest.raises(age.ControllerError, match="RUN_LOCKED_OR_UNAVAILABLE"):
            age.recover(rig.directory, provider=rig.provider, clock=rig.clock)
        return original(*args, **kwargs)
    monkeypatch.setattr(age.policy, "aggregate", while_locked)
    with patch.object(age.os, "environ", NoEnvironment()):
        result = age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)
    assert result["authoritative_local_state"] is True
    assert rig.events == before  # Seal has no provider or credential interactions.


@pytest.mark.parametrize("perturbation", ["missing_hash", "future_generation", "unfinished_state"])
def test_n2_seal_fails_closed_on_invalid_source(structured_reports, rig, perturbation):
    local, reaper, now = structured_reports
    if perturbation == "missing_hash":
        del local["state_sha256"]
    elif perturbation == "future_generation":
        local["generated_at_utc"] = age.policy.utc(now + 1)
    else:
        state = read_json(rig.directory / "state.json")
        state["phase"] = "CLEANUP"
        age.atomic_write(rig.directory / "state.json", age._encode(state))
    with pytest.raises(age.ControllerError):
        age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)
    assert not (rig.directory / "cleanup_seal.json").exists()


def test_n2_failed_seal_write_cannot_return_confirmation(structured_reports, rig, monkeypatch):
    local, reaper, now = structured_reports
    def failed_write(*args):
        raise OSError("offline synthetic seal write failure")
    monkeypatch.setattr(age, "atomic_write", failed_write)
    with pytest.raises(age.ControllerError, match="INVALID_CLEANUP_EVIDENCE"):
        age.combine_operational_cleanup(local, reaper, run_dir=rig.directory, now=now)


def test_n2_cli_combines_only_against_current_durable_state(structured_reports, rig, monkeypatch, capsys):
    local, reaper, now = structured_reports
    paths = [rig.directory / "local-outcome.json", rig.directory / "reaper-report.json"]
    for path, report in zip(paths, (local, reaper)):
        age.atomic_write(path, age._encode(report))
    monkeypatch.setattr(age.Clock, "time", staticmethod(lambda: now))
    args = ["combine", "--run-dir", str(rig.directory), "--local-outcome", str(paths[0]),
            "--reaper-report", str(paths[1])]
    assert age.main(args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["authoritative_local_state"] is True
    assert result["local_seal"]["sealed_at_utc"] == age.policy.utc(now)
    # Even benign newer durable state cannot silently reuse this old outcome.
    state = read_json(rig.directory / "state.json")
    state["controller_failed"] = True
    age.atomic_write(rig.directory / "state.json", age._encode(state))
    assert age.main(args) == 2
    assert json.loads(capsys.readouterr().out)["reason"] == "STALE_LOCAL_OUTCOME"