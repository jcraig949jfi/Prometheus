"""Offline tests for the B3 independent reaper: no real credentials, sockets,
or paid provider calls. Exercises the pre-create arming handoff and the
bounded scan/delete/reconcile sweep, including the host-offline rehearsal
scenarios required by ASTRA_CLOSURE_REVIEW_02.md section 6.

Run with: python -m pytest Aether/test/test_aeth01_independent_reaper.py -q
"""

from copy import deepcopy
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path

import pytest


MODULE = (Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"
          / "independent_reaper.py")
SPEC = importlib.util.spec_from_file_location("_independent_reaper_test", MODULE)
reaper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reaper)

SECRET = "offline-fixture-reaper-shared-secret-0123456789"
EPOCH = 1_800_000_000.0


def manifest():
    return {"version": 1, "run_id": "run-fixture-1", "run_name": "aeth01-age-run-fixture-1",
            "image": "registry.example/aeth01@sha256:" + "a" * 64,
            "creation_intent_id": "run-fixture-1",
            "cutoff_utc": reaper._utc(EPOCH + 1200), "cutoff_reference": "offline cutoff fixture",
            "reconciliation_horizon_seconds": 3600, "hourly_rate_usd": 6, "canary_budget_usd": 3}


def write_manifest(directory, data=None):
    path = Path(directory) / "reaper_manifest.json"
    reaper.atomic_write(path, reaper._encode(data if data is not None else manifest()))
    return path


class Clock:
    def __init__(self, start=EPOCH):
        self.now = start
        self.sleeps = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class Provider:
    """Cleanup-only-capable test double: no create_pod method exists at all."""

    def __init__(self):
        self.pods = {}
        self.deleted = set()
        self.list_hook = None
        self.get_hook = None
        self.delete_hook = None
        self.calls = []

    def _owned_pod(self, pod_id, name, run_id, status="RUNNING", image=None):
        self.pods[pod_id] = {"id": pod_id, "name": name, "image": image or manifest()["image"],
                              "env": {"AETH01_RUN_ID": run_id}, "status": status, "cost": 6}

    def visit_pods(self, visitor):
        self.calls.append("LIST")
        pods = self.list_hook(self) if self.list_hook else [
            deepcopy(p) for pid, p in self.pods.items() if pid not in self.deleted]
        for pod in pods:
            visitor(pod)

    def get_pod(self, pod_id):
        self.calls.append(("GET", pod_id))
        if self.get_hook:
            return self.get_hook(self, pod_id)
        if pod_id in self.deleted:
            return None
        return deepcopy(self.pods.get(pod_id))

    def terminate_pod(self, pod_id):
        self.calls.append(("DELETE", pod_id))
        if self.delete_hook:
            return self.delete_hook(self, pod_id)
        already = pod_id in self.deleted
        self.deleted.add(pod_id)
        return "NOT_FOUND_404" if already else "ACK_204"


def test_provider_has_no_create_capability():
    # B3: structural guarantee -- the reaper's own provider surface cannot
    # create a Pod, independent of what the wrapped client class supports.
    assert not hasattr(reaper.ReaperProvider, "create_pod")
    assert not hasattr(Provider(), "create_pod")


def test_arm_produces_hmac_bound_ack_matching_age_controller_contract(tmp_path):
    path = write_manifest(tmp_path)
    m, ack = reaper.arm(path, SECRET, "offline-fixture-scheduler", clock_time=lambda: EPOCH)
    assert set(ack) == reaper.ACK_KEYS
    assert ack["armed"] is True and ack["manifest_sha256"] == reaper._sha(path.read_bytes())
    assert ack["cutoff_utc"] == m["cutoff_utc"]
    expected = hmac.new(SECRET.encode(), path.read_bytes(), hashlib.sha256).hexdigest()
    assert ack["manifest_hmac_sha256"] == expected
    # A tampered manifest byte must change the digest the ack is bound to.
    tampered = path.read_bytes() + b" "
    assert reaper._sha(tampered) != ack["manifest_sha256"]


@pytest.mark.parametrize("secret", ["", "short", "a" * 4097, "bad\ttab" + "x" * 30])
def test_arm_rejects_invalid_secret_without_reading_manifest(tmp_path, secret):
    path = write_manifest(tmp_path)
    with pytest.raises(reaper.ReaperError, match="REAPER_SHARED_SECRET_REQUIRED"):
        reaper.arm(path, secret, "scheduler")


def test_arm_rejects_malformed_manifest(tmp_path):
    path = Path(tmp_path) / "reaper_manifest.json"
    reaper.atomic_write(path, reaper._encode({"version": 1}))
    with pytest.raises(reaper.ReaperError, match="INVALID_MANIFEST"):
        reaper.arm(path, SECRET, "scheduler")


def _run_sweep(m, provider, state=None, **kwargs):
    digest = reaper._sha(reaper._encode(m))
    state = state or reaper.new_evidence_state(m, digest)
    clock = kwargs.pop("clock", None) or Clock()
    return reaper.sweep(m, digest, provider, state, sleep=clock.sleep,
                        clock_time=clock.time, **kwargs), clock


def test_sweep_confirms_via_positive_terminated_observation():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])

    def get_hook(p, pod_id):
        if pod_id in p.deleted:
            return dict(p.pods[pod_id], status="TERMINATED")
        return deepcopy(p.pods.get(pod_id))
    provider.get_hook = get_hook

    state, _ = _run_sweep(m, provider)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert state["pod_evidence"]["pod_1"]["cleanup_confidence"] == "CONFIRMED"
    assert state["pod_evidence"]["pod_1"]["positive_termination_observed"] is True


def test_sweep_confirms_via_ack_plus_independent_reconciliation_absence():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    state, clock = _run_sweep(m, provider)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert state["pod_evidence"]["pod_1"]["delete_result"] == "ACK_204"
    assert state["pod_evidence"]["pod_1"]["absence_confirmations"] >= reaper.ABSENCE_SCANS_REQUIRED


def test_sweep_never_confirms_from_ambiguous_404_alone():
    # B1 equivalent: a DELETE that never gets ACK_204 (simulating access loss
    # / persistent 404) must never resolve, however many rounds run.
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    provider.delete_hook = lambda p, pod_id: "NOT_FOUND_404"

    def get_hook(p, pod_id):
        return None  # Always ambiguous: not found or not accessible.
    provider.get_hook = get_hook
    state, _ = _run_sweep(m, provider, rounds=10)
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"
    assert state["pod_evidence"]["pod_1"]["cleanup_confidence"] == "UNRESOLVED"


def test_sweep_late_visible_pod_with_no_returned_create_id_is_found_and_deleted():
    # Host-offline rehearsal core scenario: the reaper discovers and deletes
    # an owned pod purely via inventory, with no create-response ID ever
    # supplied to it (it never ran the controller or saw a create response).
    m = manifest()
    provider = Provider()
    calls = {"n": 0}

    def list_hook(p):
        calls["n"] += 1
        if calls["n"] == 1:
            return []  # First scan: not yet visible (late-visible Pod).
        if "pod_1" not in p.pods:
            p._owned_pod("pod_1", m["run_name"], m["run_id"])
        return [deepcopy(pod) for pid, pod in p.pods.items() if pid not in p.deleted]
    provider.list_hook = list_hook
    state, _ = _run_sweep(m, provider, rounds=8)
    assert "pod_1" in state["owned_ids"]
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert "pod_1" in provider.deleted


def test_sweep_reappearance_resets_absence_and_stays_unresolved():
    # B2 equivalent: a pod that flaps back visible in independent inventory
    # scans must reset accrued absence evidence -- no finite polling count
    # from stale-then-fresh observations may manufacture certainty.
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    calls = {"n": 0}

    def list_hook(p):
        calls["n"] += 1
        if calls["n"] % 2 == 0:
            return [deepcopy(p.pods["pod_1"])]  # Flaps back visible every other scan.
        return [deepcopy(pod) for pid, pod in p.pods.items() if pid not in p.deleted]
    provider.list_hook = list_hook
    state, _ = _run_sweep(m, provider, rounds=9)
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"


def test_sweep_unrelated_pod_is_never_deleted():
    m = manifest()
    provider = Provider()
    provider.pods["unrelated"] = {"id": "unrelated", "name": "other-run",
                                  "image": "registry.example/other@sha256:" + "b" * 64,
                                  "env": {"AETH01_RUN_ID": "other-run-id"}, "status": "RUNNING"}
    state, _ = _run_sweep(m, provider, rounds=2)
    assert provider.deleted == set()
    assert state["owned_ids"] == []


def test_sweep_ambiguous_duplicate_owned_pods_never_confirms():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    provider._owned_pod("pod_2", m["run_name"], m["run_id"])
    state, _ = _run_sweep(m, provider, rounds=6)
    assert state["ownership_ambiguous"] is True
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"
    assert provider.deleted == {"pod_1", "pod_2"}


def test_sweep_pagination_failure_keeps_positive_records_and_stays_unresolved():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    seen = []

    def list_hook(p):
        seen.append(1)
        if len(seen) == 1:
            raise RuntimeError("offline inventory page failure")
        return [deepcopy(pod) for pid, pod in p.pods.items() if pid not in p.deleted]
    provider.list_hook = list_hook
    state, _ = _run_sweep(m, provider, rounds=1)
    assert state["reconciled"] is False


def test_empty_inventory_requires_full_horizon_before_confirming(tmp_path):
    m = dict(manifest(), reconciliation_horizon_seconds=100)
    provider = Provider()  # Nothing ever owned: simulates a genuinely lost create.
    digest = reaper._sha(reaper._encode(m))
    state = reaper.new_evidence_state(m, digest)
    clock = Clock()
    # First invocation: horizon has not elapsed yet even though every scan is empty.
    state = reaper.sweep(m, digest, provider, state, rounds=2, sleep=clock.sleep,
                         clock_time=clock.time)
    assert state["status"] == "REAPER_PENDING"
    clock.now += 200  # Now past the announced horizon.
    for _ in range(reaper.EMPTY_HORIZON_SCANS_REQUIRED):
        state = reaper.sweep(m, digest, provider, state, rounds=1, sleep=clock.sleep,
                             clock_time=clock.time)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert state["owned_ids"] == []


def test_evidence_never_contains_secrets_or_raw_exception_text(tmp_path):
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    marker = "OFFLINE_UNTRUSTED_EXCEPTION_DO_NOT_LOG"
    provider.delete_hook = lambda p, pod_id: (_ for _ in ()).throw(RuntimeError(marker))
    state, _ = _run_sweep(m, provider, rounds=2)
    raw = json.dumps(state)
    assert marker not in raw and SECRET not in raw


def test_load_or_init_evidence_round_trips_and_rejects_mismatch(tmp_path):
    m = manifest()
    digest = reaper._sha(reaper._encode(m))
    path = Path(tmp_path) / "reaper_evidence.json"
    fresh = reaper.load_or_init_evidence(path, m, digest)
    assert fresh["status"] == "REAPER_PENDING"
    reaper.atomic_write(path, reaper._encode(fresh))
    reloaded = reaper.load_or_init_evidence(path, m, digest)
    assert reloaded == fresh
    with pytest.raises(reaper.ReaperError, match="EVIDENCE_MANIFEST_MISMATCH"):
        reaper.load_or_init_evidence(path, m, "0" * 64)


def test_cli_arm_then_sweep_round_trip(tmp_path, monkeypatch):
    manifest_path = write_manifest(tmp_path)
    ack_path = Path(tmp_path) / "reaper_ack.json"
    monkeypatch.setenv("AGE_REAPER_SHARED_SECRET", SECRET)
    code = reaper.main(["arm", "--manifest", str(manifest_path), "--out-ack", str(ack_path),
                       "--scheduler-id", "offline-fixture-scheduler"])
    assert code == 0
    ack = json.loads(ack_path.read_bytes())
    assert ack["armed"] is True

    import sys
    import types
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    shim = types.ModuleType("runpod_api")
    shim.RunPodAPI = lambda: provider
    monkeypatch.setitem(sys.modules, "runpod_api", shim)
    monkeypatch.setenv("RUNPOD_API_KEY", "offline-fixture-key")
    evidence_path = Path(tmp_path) / "reaper_evidence.json"
    code = reaper.main(["sweep", "--manifest", str(manifest_path), "--out-evidence",
                       str(evidence_path), "--ack", str(ack_path), "--rounds", "4",
                       "--poll-seconds", "0"])
    assert code == 0
    evidence = json.loads(evidence_path.read_bytes())
    assert evidence["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert evidence["ack_scheduler_id"] == "offline-fixture-scheduler"


AGE_MODULE = (Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"
             / "age_controller.py")
AGE_SPEC = importlib.util.spec_from_file_location("_reaper_age_integration_test", AGE_MODULE)
age = importlib.util.module_from_spec(AGE_SPEC)
AGE_SPEC.loader.exec_module(age)


def test_host_offline_rehearsal_reaper_arms_and_later_deletes_without_controller(tmp_path):
    """Section 6 host-offline rehearsal: the AGE controller host is treated
    as dead/offline after producing the plan/manifest (this test never calls
    age.run() at all). The independent reaper -- using only the durable
    manifest file, with no reference to the controller's runtime, process,
    or in-memory state -- arms independently, later discovers a Pod that
    appears with no returned create ID, and deletes it.
    """
    directory = tmp_path / "run"
    config = {"image": "registry.example/aeth01@sha256:" + "c" * 64,
              "gpu_id": "offline-gpu", "cloud": "COMMUNITY", "hourly_rate_usd": 6,
              "canary_budget_usd": 3, "remaining_budget_usd": 19.93,
              "max_lifetime_seconds": 240, "canary_timeout_seconds": 30,
              "independent_cutoff_deadline_utc": age._utc(EPOCH + 1200),
              "independent_cutoff_reference": "offline rehearsal cutoff fixture"}
    summary = age.create_plan(config, directory, clock=type("C", (), {"time": staticmethod(lambda: EPOCH)})())
    plan = json.loads((directory / "plan.json").read_bytes())
    manifest_path = directory / "reaper_manifest.json"
    assert json.loads(manifest_path.read_bytes()) == age.reaper_manifest_document(plan)

    # --- controller host now considered dead/offline; only files remain ---
    m, ack = reaper.arm(manifest_path, SECRET, "offline-fixture-scheduler", clock_time=lambda: EPOCH)
    ack_path = directory / "reaper_ack.json"
    reaper.atomic_write(ack_path, reaper._encode(ack))

    # The controller-side gate independently accepts this reaper-produced ack.
    age._require_reaper_armed(directory, plan, SECRET)

    # Independent reaper reaches cutoff; no create-response ID was ever given
    # to it. A late-visible owned Pod appears in inventory with no prior hint.
    provider = Provider()
    calls = {"n": 0}

    def list_hook(p):
        calls["n"] += 1
        if calls["n"] == 1:
            return []
        if "orphan-pod" not in p.pods:
            p._owned_pod("orphan-pod", plan["run_name"], plan["run_id"], image=plan["config"]["image"])
        return [deepcopy(pod) for pid, pod in p.pods.items() if pid not in p.deleted]
    provider.list_hook = list_hook

    digest = reaper._sha(manifest_path.read_bytes())
    state = reaper.load_or_init_evidence(directory / "reaper_evidence.json", m, digest)
    state = reaper.sweep(m, digest, provider, state, rounds=8, sleep=lambda s: None,
                         clock_time=lambda: EPOCH + 1300, ack=ack)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert "orphan-pod" in provider.deleted
    raw = json.dumps(state)
    assert SECRET not in raw


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
