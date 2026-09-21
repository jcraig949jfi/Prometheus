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
    def __init__(self, start=EPOCH + 1200):
        self.now = start
        self.mono = 0.0
        self.sleeps = []

    def time(self):
        return self.now

    def monotonic(self):
        return self.mono

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        self.mono += seconds


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
                        clock_time=clock.time, monotonic=clock.monotonic, **kwargs), clock


def assert_known_only(state):
    assert state["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_CONFIRMED"
    assert state["status"] == "REAPER_PENDING"
    assert state["reconciliation_window_status"] == "RECONCILIATION_PENDING"


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
    assert_known_only(state)
    assert state["pod_evidence"]["pod_1"]["cleanup_confidence"] == "CONFIRMED"
    assert state["pod_evidence"]["pod_1"]["positive_termination_observed"] is True


def test_sweep_confirms_via_ack_plus_independent_reconciliation_absence():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    state, clock = _run_sweep(m, provider)
    assert_known_only(state)
    assert state["pod_evidence"]["pod_1"]["delete_result"] == "ACK_204"
    assert state["pod_evidence"]["pod_1"]["absence_confirmations"] >= reaper.ABSENCE_SCANS_REQUIRED
    assert len(clock.sleeps) == reaper.DEFAULT_ROUNDS - 1


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
    assert_known_only(state)
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


def test_sweep_duplicate_exact_owned_pods_all_clean_without_permanent_ambiguity():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    provider._owned_pod("pod_2", m["run_name"], m["run_id"])
    state, _ = _run_sweep(m, provider, rounds=362)
    assert state["ownership_ambiguous"] is False
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert set(state["owned_ids"]) == {"pod_1", "pod_2"}
    assert provider.deleted == {"pod_1", "pod_2"}


def test_sweep_pagination_failure_keeps_positive_records_and_stays_unresolved():
    m = manifest()
    provider = Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    def list_hook(p):
        yield deepcopy(p.pods["pod_1"])
        raise RuntimeError("offline inventory page failure")
    provider.list_hook = list_hook
    state, _ = _run_sweep(m, provider, rounds=1)
    assert state["reconciled"] is False
    assert state["owned_ids"] == ["pod_1"]
    assert provider.deleted == {"pod_1"}
    assert state["pod_evidence"]["pod_1"]["absence_confirmations"] == 0
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"


def test_empty_inventory_requires_full_horizon_before_confirming(tmp_path):
    m = dict(manifest(), reconciliation_horizon_seconds=100)
    provider = Provider()  # Nothing ever owned: simulates a genuinely lost create.
    digest = reaper._sha(reaper._encode(m))
    state = reaper.new_evidence_state(m, digest)
    clock = Clock()
    # First invocation: horizon has not elapsed yet even though every scan is empty.
    state, _ = _run_sweep(m, provider, state, rounds=2, clock=clock)
    assert state["status"] == "REAPER_PENDING"
    clock.now += 200  # Now past the announced horizon.
    for _ in range(reaper.EMPTY_HORIZON_SCANS_REQUIRED):
        state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock)
        assert_known_only(state)
        assert state["window"]["covered_seconds"] == 0
        clock.sleep(10)
    state, _ = _run_sweep(m, provider, state, rounds=11, clock=clock)
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
    clock = Clock()
    monkeypatch.setattr(reaper._time, "time", clock.time)
    monkeypatch.setattr(reaper._time, "monotonic", clock.monotonic)
    monkeypatch.setattr(reaper._time, "sleep", clock.sleep)
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
                       "--poll-seconds", "10"])
    assert code == 0
    evidence = json.loads(evidence_path.read_bytes())
    assert_known_only(evidence)
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
                         clock_time=lambda: EPOCH + 1300, monotonic=lambda: 0, ack=ack)
    assert_known_only(state)
    assert "orphan-pod" in provider.deleted
    raw = json.dumps(state)
    assert SECRET not in raw


@pytest.mark.parametrize("rounds", [3, 6])
def test_a_short_empty_burst_cannot_confirm_hour_horizon(rounds):
    state, _ = _run_sweep(manifest(), Provider(), rounds=rounds)
    assert_known_only(state)
    assert state["window"]["covered_seconds"] == (rounds - 1) * 10


@pytest.mark.parametrize("statuses", [
    ["TERMINATED", "RUNNING"],
    ["TERMINATED", None, "RUNNING", "TERMINATED"],
])
def test_b_current_termination_demotes_and_history_survives(statuses):
    m, provider, clock = manifest(), Provider(), Clock()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    provider.delete_hook = lambda p, pid: "NOT_FOUND_404"
    state = None
    for status in statuses:
        provider.pods["pod_1"]["status"] = status
        provider.list_hook = lambda p: [] if status is None else [deepcopy(p.pods["pod_1"])]
        provider.get_hook = lambda p, pid: None if status is None else deepcopy(p.pods[pid])
        state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock)
        rec = state["pod_evidence"]["pod_1"]
        assert rec["positive_termination_observed"] is True
        if status == "RUNNING":
            assert rec["cleanup_confidence"] == "UNRESOLVED"
            assert rec["absence_confirmations"] == 0
            assert ("DELETE", "pod_1") in provider.calls
        elif status == "TERMINATED":
            assert rec["cleanup_confidence"] == "CONFIRMED"
        clock.sleep(10)


def test_b_ack_absent_absent_then_running_invalidates_old_ack():
    m, provider, clock = manifest(), Provider(), Clock()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    state, _ = _run_sweep(m, provider, rounds=3, clock=clock)
    assert_known_only(state)
    before = deepcopy(state)
    provider.deleted.clear()
    provider.delete_hook = lambda p, pid: "NOT_FOUND_404"
    clock.sleep(10)
    state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock)
    rec = state["pod_evidence"]["pod_1"]
    assert rec["cleanup_confidence"] == "UNRESOLVED"
    assert rec["delete_result"] != "ACK_204"
    assert rec["absence_confirmations"] == 0
    assert len(rec["history"]) > len(before["pod_evidence"]["pod_1"]["history"])


@pytest.mark.parametrize("status", ["PROVISIONING", "STARTING", "RUNNING", "EXITED", "ERROR", None,
                                    "UNTRUSTED_STATUS_DO_NOT_JOURNAL"])
def test_b_every_nonterminated_visibility_clears_confirmation(status):
    m, provider, clock = manifest(), Provider(), Clock()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"], status="TERMINATED")
    state, _ = _run_sweep(m, provider, rounds=1, clock=clock)
    clock.sleep(10)
    provider.pods["pod_1"]["status"] = status
    provider.delete_hook = lambda p, pid: None
    state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock)
    rec = state["pod_evidence"]["pod_1"]
    assert rec["cleanup_confidence"] == "UNRESOLVED"
    assert rec["positive_termination_observed"] is True
    assert rec["delete_result"] != "ACK_204"
    assert "UNTRUSTED_STATUS_DO_NOT_JOURNAL" not in json.dumps(state)


@pytest.mark.parametrize("result", [None, True, "", "UNKNOWN", {}, 204])
def test_b_unknown_delete_result_never_becomes_ack(result):
    m, provider = manifest(), Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])

    def delete(p, pid):
        p.deleted.add(pid)
        return result
    provider.delete_hook = delete
    state, _ = _run_sweep(m, provider, rounds=8)
    assert state["pod_evidence"]["pod_1"]["delete_result"] != "ACK_204"
    assert state["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_UNRESOLVED"


@pytest.mark.parametrize("changed", ["name", "image", "env"])
def test_b_partial_matches_are_ignored_not_ambiguity(changed):
    m, provider = manifest(), Provider()
    provider._owned_pod("not_ours", m["run_name"], m["run_id"])
    provider.pods["not_ours"][changed] = {} if changed == "env" else "other"
    state, _ = _run_sweep(m, provider, rounds=61, poll_seconds=60)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert not state["ownership_ambiguous"]
    assert state["owned_ids"] == []
    assert provider.deleted == set()


def test_b_different_object_at_known_id_is_conflict_not_delete_target():
    m, provider, clock = manifest(), Provider(), Clock()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"], status="TERMINATED")
    state, _ = _run_sweep(m, provider, rounds=1, clock=clock)
    provider.pods["pod_1"]["image"] = "different-image"
    clock.sleep(10)
    state, _ = _run_sweep(m, provider, state, rounds=6, clock=clock)
    assert state["ownership_ambiguous"]
    assert provider.deleted == set()
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"


def test_c1_hour_blind_then_six_empty_scans_covers_only_fifty_seconds(tmp_path):
    m, provider, clock = manifest(), Provider(), Clock()
    path = tmp_path / "evidence.json"
    persist = lambda s: reaper.atomic_write(path, reaper._encode(s))
    state, _ = _run_sweep(m, provider, rounds=1, clock=clock, persist=persist)
    clock.sleep(3600)
    state = reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())
    state, _ = _run_sweep(m, provider, state, rounds=6, clock=clock, persist=persist)
    assert_known_only(state)
    assert state["window"]["covered_seconds"] == 50


def test_c1_same_invocation_hour_gap_then_fifty_second_burst_is_not_coverage():
    class BlindClock(Clock):
        def sleep(self, seconds):
            super().sleep(3600 if not self.sleeps else seconds)
    state, _ = _run_sweep(manifest(), Provider(), rounds=7, clock=BlindClock())
    assert_known_only(state)
    assert state["window"]["scan_count"] == 6
    assert state["window"]["covered_seconds"] == 50


@pytest.mark.parametrize("poll", [10, 60])
def test_c2_healthy_single_invocation_covers_full_hour(poll):
    state, clock = _run_sweep(manifest(), Provider(), rounds=3600 // poll + 1, poll_seconds=poll)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    assert state["reconciliation_window_status"] == "RECONCILIATION_COMPLETE"
    assert state["window"]["covered_seconds"] == 3600
    assert len(clock.sleeps) == 3600 // poll


@pytest.mark.parametrize("failure_at", [1800, 3600])
def test_c3_failure_interrupts_window_and_latest_failure_cannot_confirm(failure_at):
    clock, provider = Clock(), Provider()

    def inventory(p):
        if clock.mono == failure_at:
            raise RuntimeError("offline inventory unavailable")
        return []
    provider.list_hook = inventory
    state, _ = _run_sweep(manifest(), provider, rounds=361, clock=clock)
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"
    assert state["window"]["covered_seconds"] < 1800
    assert state["window"]["history"]
    if failure_at == 3600:
        assert state["reconciled"] is False
        assert state["window"]["scan_count"] == 0


@pytest.mark.parametrize("status", ["RUNNING", "TERMINATED"])
def test_c4_owned_discovery_at_3500_restarts_even_when_terminated(status):
    m, clock, provider = manifest(), Clock(), Provider()
    provider._owned_pod("late", m["run_name"], m["run_id"], status=status)
    provider.list_hook = lambda p: [deepcopy(p.pods["late"])] if clock.mono == 3500 else []
    state, _ = _run_sweep(m, provider, rounds=361, clock=clock)
    assert_known_only(state)
    assert state["window"]["covered_seconds"] == 90
    assert state["owned_ids"] == ["late"]


def test_c5_partial_page_positive_is_durable_before_process_death(tmp_path):
    m, clock, provider = manifest(), Clock(), Provider()
    provider._owned_pod("late", m["run_name"], m["run_id"])
    path = tmp_path / "evidence.json"

    def inventory(p):
        yield deepcopy(p.pods["late"])
        raise SystemExit("offline crash before remaining inventory pages")
    provider.list_hook = inventory
    with pytest.raises(SystemExit):
        _run_sweep(m, provider, rounds=1, clock=clock,
                   persist=lambda s: reaper.atomic_write(path, reaper._encode(s)))
    saved = reaper.load_or_init_evidence(path, m, reaper._sha(reaper._encode(m)), now=clock.time())
    assert saved["owned_ids"] == ["late"]
    assert saved["pod_evidence"]["late"]["history"]
    provider.list_hook = lambda p: (_ for _ in ()).throw(RuntimeError("still unavailable"))
    state, _ = _run_sweep(m, provider, saved, rounds=1, clock=clock)
    assert provider.deleted == {"late"}
    assert state["window"]["covered_seconds"] == 0


def test_c6_auth_loss_invalidates_old_success_without_losing_known_ids():
    m, provider, clock = manifest(), Provider(), Clock()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    state, _ = _run_sweep(m, provider, rounds=362, clock=clock)
    assert state["status"] == "REAPER_CLEANUP_CONFIRMED"
    old = deepcopy(state)
    clock.sleep(10)
    provider.list_hook = lambda p: (_ for _ in ()).throw(PermissionError("denied"))
    state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock)
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"
    assert state["owned_ids"] == ["pod_1"]
    assert state["window"]["scan_count"] == 0
    assert old["status"] == "REAPER_CLEANUP_CONFIRMED"


@pytest.mark.parametrize("phase", ["window", "outage", "ack", "terminated", "reappearance"])
def test_durable_restart_resets_window_credit_but_keeps_histories(tmp_path, phase):
    m, provider, clock = manifest(), Provider(), Clock()
    path = tmp_path / "evidence.json"
    persist = lambda s: reaper.atomic_write(path, reaper._encode(s))
    if phase in ("ack", "terminated", "reappearance"):
        provider._owned_pod("pod_1", m["run_name"], m["run_id"],
                            status="TERMINATED" if phase != "ack" else "RUNNING")
    state, _ = _run_sweep(m, provider, rounds=1 if phase == "ack" else 61,
                          poll_seconds=60, clock=clock, persist=persist)
    if phase in ("outage", "reappearance"):
        clock.sleep(10)
        if phase == "outage":
            provider.list_hook = lambda p: (_ for _ in ()).throw(RuntimeError("offline"))
        else:
            provider.pods["pod_1"]["status"] = "RUNNING"
            provider.delete_hook = lambda p, pid: "NOT_FOUND_404"
        state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock, persist=persist)
    saved = deepcopy(state)
    clock.sleep(3600)
    state = reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())
    snapshots = []

    def checkpoint(s):
        persist(s)
        snapshots.append(s)
    _run_sweep(m, provider, state, rounds=1, clock=clock, persist=checkpoint)
    restarted = snapshots[0]
    assert restarted["window"]["session_id"] != saved["window"]["session_id"]
    assert restarted["window"]["covered_seconds"] == 0
    assert restarted["window"]["scan_count"] == 0
    assert restarted["window"]["history"][:len(saved["window"]["history"])] == saved["window"]["history"]
    assert restarted["pod_evidence"] == saved["pod_evidence"]
    assert restarted["status"] != "REAPER_CLEANUP_CONFIRMED"
    reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())


@pytest.mark.parametrize("wall_delta,mono_delta", [(-20, 10), (120, 10), (120, 120), (10, -20), (13, 10)])
def test_clock_discontinuity_resets_window(wall_delta, mono_delta):
    class JumpClock(Clock):
        def sleep(self, seconds):
            if len(self.sleeps) == 3:
                self.now += wall_delta - seconds
                self.mono += mono_delta - seconds
            super().sleep(seconds)
    state, _ = _run_sweep(manifest(), Provider(), rounds=8, clock=JumpClock())
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"
    assert state["window"]["covered_seconds"] <= 30
    assert state["window"]["history"]


@pytest.mark.parametrize("bad_time", [float("nan"), float("inf"), "bad", None])
def test_runtime_bad_clock_never_suppresses_deletion(bad_time):
    m, provider, clock = manifest(), Provider(), Clock()
    for pid in ("one", "two"):
        provider._owned_pod(pid, m["run_name"], m["run_id"])

    def inventory(p):
        clock.now = bad_time
        return [deepcopy(pod) for pod in p.pods.values()]
    provider.list_hook = inventory
    state, _ = _run_sweep(m, provider, rounds=1, clock=clock)
    assert provider.deleted == {"one", "two"}
    assert state["journal_ok"] is False
    assert state["status"] == "REAPER_CLEANUP_UNRESOLVED"
    assert state["window"]["covered_seconds"] == 0


def test_bad_clock_on_live_reappearance_does_not_reuse_old_confirmation():
    m, provider, clock = manifest(), Provider(), Clock()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"], status="TERMINATED")
    state, _ = _run_sweep(m, provider, rounds=1, clock=clock)
    prefix = deepcopy(state["pod_evidence"]["pod_1"]["history"])
    provider.pods["pod_1"]["status"] = "RUNNING"

    def inventory(p):
        clock.now = float("nan")
        return [deepcopy(p.pods["pod_1"])]
    provider.list_hook = inventory
    state, _ = _run_sweep(m, provider, state, rounds=1, clock=clock)
    assert provider.deleted == {"pod_1"}
    assert state["pod_evidence"]["pod_1"]["history"] == prefix
    assert state["journal_ok"] is False
    assert state["status"] == "REAPER_CLEANUP_UNRESOLVED"


def test_pre_cutoff_scans_never_count():
    state, _ = _run_sweep(manifest(), Provider(), rounds=10, clock=Clock(start=EPOCH))
    assert_known_only(state)
    assert state["window"]["scan_count"] == 0


def test_persist_failure_cannot_confirm_but_all_deletes_continue():
    m, provider = manifest(), Provider()
    for pid in ("one", "two"):
        provider._owned_pod(pid, m["run_name"], m["run_id"])

    def broken_disk(state):
        raise OSError("offline disk failure")
    state, _ = _run_sweep(m, provider, rounds=63, poll_seconds=60, persist=broken_disk)
    assert provider.deleted == {"one", "two"}
    assert state["journal_ok"] is False
    assert state["status"] != "REAPER_CLEANUP_CONFIRMED"


@pytest.mark.parametrize("field,value", [
    ("version", 1), ("version", 3), ("policy_version", 999), ("journal_ok", "true"),
    ("owned_ids", ["unknown"]), ("total_rounds_run", -1), ("unexpected", "field"),
    ("status", "REAPER_CLEANUP_CONFIRMED"), ("manifest_sha256", "0" * 64),
    ("first_fired_at_utc", "bad"), ("last_fired_at_utc", "9999-01-01T00:00:00+00:00"),
])
def test_strict_snapshot_validation_rejects_tampering(tmp_path, field, value):
    m = manifest()
    state, clock = _run_sweep(m, Provider(), rounds=2)
    digest = state["manifest_sha256"]
    state[field] = value
    path = tmp_path / "evidence.json"
    reaper.atomic_write(path, reaper._encode(state))
    with pytest.raises(reaper.ReaperError):
        reaper.load_or_init_evidence(path, m, digest, now=clock.time())


def test_manifest_copy_is_bound_and_not_aliased(tmp_path):
    m = manifest()
    state, clock = _run_sweep(m, Provider(), rounds=1)
    state["manifest"]["image"] = "different-image"
    assert m["image"] != "different-image"
    path = tmp_path / "evidence.json"
    reaper.atomic_write(path, reaper._encode(state))
    with pytest.raises(reaper.ReaperError, match="EVIDENCE_MANIFEST_MISMATCH"):
        reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())


def test_load_rejects_future_pod_history_and_forged_confidence(tmp_path):
    m, provider = manifest(), Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"], status="TERMINATED")
    state, clock = _run_sweep(m, provider, rounds=1)
    path = tmp_path / "evidence.json"
    reaper.atomic_write(path, reaper._encode(state))
    with pytest.raises(reaper.ReaperError):
        reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time() - 1)
    state["pod_evidence"]["pod_1"]["cleanup_confidence"] = "UNRESOLVED"
    reaper.atomic_write(path, reaper._encode(state))
    with pytest.raises(reaper.ReaperError):
        reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())


@pytest.mark.parametrize("field,value", [("covered_seconds", 3600), ("scan_count", 999),
                                        ("start_utc", "bad"), ("latest_utc", "bad"),
                                        ("samples", [{}]), ("history", [{}])])
def test_load_rejects_malformed_window(tmp_path, field, value):
    m = manifest()
    state, clock = _run_sweep(m, Provider(), rounds=2)
    state["window"][field] = value
    path = tmp_path / "evidence.json"
    reaper.atomic_write(path, reaper._encode(state))
    with pytest.raises(reaper.ReaperError):
        reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())


@pytest.mark.parametrize("flag,value", [("--rounds", "0"), ("--rounds", "-1"),
    ("--rounds", "10001"), ("--poll-seconds", "0"), ("--poll-seconds", "-1"),
    ("--poll-seconds", "nan"), ("--poll-seconds", "inf"), ("--poll-seconds", "61")])
def test_cli_invalid_flags_fail_closed_before_provider(tmp_path, monkeypatch, flag, value):
    import sys
    import types
    shim = types.ModuleType("runpod_api")
    shim.RunPodAPI = lambda: pytest.fail("invalid flags must not construct a provider")
    monkeypatch.setitem(sys.modules, "runpod_api", shim)
    code = reaper.main(["sweep", "--manifest", str(write_manifest(tmp_path)),
                        "--out-evidence", str(tmp_path / "evidence.json"), flag, value])
    assert code == 2
    assert not (tmp_path / "evidence.json").exists()


def test_cli_lock_prevents_read_sweep_write_and_releases(tmp_path, monkeypatch):
    path = tmp_path / "evidence.json"
    manifest_path = write_manifest(tmp_path)
    monkeypatch.setattr(reaper, "load_or_init_evidence",
                        lambda *a, **k: pytest.fail("second writer read evidence"))
    with reaper.evidence_lock(path):
        with pytest.raises(reaper.ReaperError, match="EVIDENCE_LOCK_UNAVAILABLE"):
            with reaper.evidence_lock(path):
                pytest.fail("second writer acquired lock")
        assert reaper.main(["sweep", "--manifest", str(manifest_path),
                            "--out-evidence", str(path)]) == 2
    with reaper.evidence_lock(path):
        pass


def test_sweep_report_and_persisted_snapshots_are_detached():
    m, clock = manifest(), Clock()
    digest = reaper._sha(reaper._encode(m))
    state = reaper.new_evidence_state(m, digest)
    snapshots = []
    report, _ = _run_sweep(m, Provider(), state, rounds=2, clock=clock, persist=snapshots.append)
    first = deepcopy(snapshots[0])
    report["window"]["samples"].clear()
    assert len(state["window"]["samples"]) == 2
    assert snapshots[0] == first


def test_default_monotonic_is_not_derived_from_injected_wall_clock(monkeypatch):
    m, clock = manifest(), Clock()
    digest = reaper._sha(reaper._encode(m))
    state = reaper.new_evidence_state(m, digest)
    monkeypatch.setattr(reaper._time, "monotonic", lambda: 17.0)
    report = reaper.sweep(m, digest, Provider(), state, rounds=61, poll_seconds=60,
                          clock_time=clock.time, sleep=clock.sleep)
    assert_known_only(report)
    assert report["window"]["covered_seconds"] == 0


@pytest.mark.parametrize("phase", ["DELETE_ATTEMPT", "DELETE_RESULT", "MISSING", "OBSERVE"])
def test_each_provider_result_is_durable_before_next_interaction(tmp_path, phase):
    m, clock, provider = manifest(), Clock(), Provider()
    path = tmp_path / "evidence.json"
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    if phase == "OBSERVE":
        provider.get_hook = lambda p, pid: dict(p.pods[pid], status="TERMINATED")

    def checkpoint(state):
        reaper.atomic_write(path, reaper._encode(state))
        rec = state["pod_evidence"].get("pod_1")
        if rec and rec["history"][-1]["kind"] == phase:
            if phase != "OBSERVE" or rec["current_termination_observed"]:
                raise SystemExit("offline crash after durable observation")
    with pytest.raises(SystemExit):
        _run_sweep(m, provider, rounds=1, clock=clock, persist=checkpoint)
    state = reaper.load_or_init_evidence(path, m, reaper._sha(reaper._encode(m)), now=clock.time())
    rec = state["pod_evidence"]["pod_1"]
    assert rec["history"][-1]["kind"] == phase
    if phase == "DELETE_ATTEMPT":
        assert provider.deleted == set()
    elif phase == "DELETE_RESULT":
        assert rec["delete_result"] == "ACK_204"
        assert ("GET", "pod_1") not in provider.calls
    elif phase == "OBSERVE":
        assert rec["current_termination_observed"]


@pytest.mark.parametrize("timestamp", ["bad", "2026-01-01T00:00:00", "9999-01-01T00:00:00+00:00"])
def test_load_rejects_bad_event_timestamps_even_when_cached_status_matches(tmp_path, timestamp):
    m, provider = manifest(), Provider()
    provider._owned_pod("pod_1", m["run_name"], m["run_id"])
    state, clock = _run_sweep(m, provider, rounds=1)
    state["pod_evidence"]["pod_1"]["history"][-1]["at_utc"] = timestamp
    path = tmp_path / "evidence.json"
    reaper.atomic_write(path, reaper._encode(state))
    with pytest.raises(reaper.ReaperError):
        reaper.load_or_init_evidence(path, m, state["manifest_sha256"], now=clock.time())


def test_future_archived_window_cannot_carry_success_on_restart(tmp_path):
    m = manifest()
    state, clock = _run_sweep(m, Provider(), rounds=61, poll_seconds=60)
    path = tmp_path / "evidence.json"
    reaper.atomic_write(path, reaper._encode(state))
    digest = state["manifest_sha256"]
    with pytest.raises(reaper.ReaperError):
        reaper.load_or_init_evidence(path, m, digest, now=clock.time() - 120)
    # When wall time catches up, loading is legitimate, but still grants no
    # cross-process monotonic credit: the next invocation begins from zero.
    state = reaper.load_or_init_evidence(path, m, digest, now=clock.time())
    report, _ = _run_sweep(m, Provider(), state, rounds=1, clock=Clock(start=clock.time()))
    assert_known_only(report)
    assert report["window"]["covered_seconds"] == 0


@pytest.mark.parametrize("raw", [b'{"version":2,"version":2}', b'{"number":NaN}', b'{"number":Infinity}'])
def test_json_rejects_duplicate_keys_and_nonfinite_numbers(raw):
    with pytest.raises(reaper.ReaperError, match="INVALID_JSON"):
        reaper._decode(raw)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
