"""Offline pure-policy falsifiers: no controller/reaper imports or provider I/O.

Run: python -m pytest Aether/test/test_aeth01_cleanup_evidence.py -q
"""

from copy import deepcopy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path

import pytest


MODULE = (Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"
          / "cleanup_evidence.py")
SPEC = importlib.util.spec_from_file_location("_cleanup_evidence_test", MODULE)
evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evidence)
EPOCH = 1_800_000_000.0


def at(seconds=0):
    return evidence.utc(EPOCH + seconds)


def event(rec, kind, seconds=0, **kwargs):
    return evidence.append_pod(rec, kind, at(seconds), **kwargs)


def terminated(seconds=-1):
    return event(evidence.new_pod(), "OBSERVE", seconds, status="TERMINATED")


def acknowledged():
    rec = evidence.new_pod()
    event(rec, "OBSERVE", -3, status="RUNNING")
    event(rec, "DELETE_ATTEMPT", -2)
    return event(rec, "DELETE_RESULT", -1, result="ACK_204")


def scan(window, seconds, mono=None, *, complete=True, owned_seen=False, cutoff=0):
    return evidence.observe_window(window, at(seconds), seconds if mono is None else mono,
                                   complete=complete, owned_seen=owned_seen, cutoff=at(cutoff))


def healthy(start=0, end=3600, step=60):
    window = evidence.new_window("session-1")
    for seconds in range(start, end + 1, step):
        scan(window, seconds)
    return window


def manifest():
    return {"version": 1, "run_id": "run-fixture-1", "run_name": "aeth01-age-run-fixture-1",
            "image": "registry.example/aeth01@sha256:" + "a" * 64,
            "creation_intent_id": "run-fixture-1", "cutoff_utc": at(),
            "cutoff_reference": "offline fixture", "reconciliation_horizon_seconds": 3600,
            "hourly_rate_usd": 6, "canary_budget_usd": 3}


def bind(report, value):
    report["manifest"] = deepcopy(value)
    raw = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")
    report["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    report["run_id"] = value["run_id"]


def reports(local_pods=None, reaper_pods=None, window=None):
    local = {"policy_version": 1, "owned_ids": list(local_pods or {}),
             "pod_evidence": deepcopy(local_pods or {}), "journal_ok": True,
             "ownership_ambiguous": False, "cleanup_status": "LOCAL_CLEANUP_CONFIRMED"}
    reaper = {"policy_version": 1, "owned_ids": list(reaper_pods or {}),
              "pod_evidence": deepcopy(reaper_pods or {}), "journal_ok": True,
              "ownership_ambiguous": False, "status": "REAPER_CLEANUP_CONFIRMED",
              "window": healthy() if window is None else window}
    for report in (local, reaper):
        bind(report, manifest())
    return local, reaper


def combine(local, reaper, now=3600):
    return evidence.aggregate(local, reaper, now=EPOCH + now)


def assert_unresolved(result):
    assert result["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_UNRESOLVED"


def test_public_api_and_policy_constants_are_stable():
    expected = {
        "timestamp": "(value)", "utc": "(number)",
        "new_pod": "()", "append_pod": "(rec, kind, at, *, status=None, result=None)",
        "validate_pod": "(rec, now=None)", "pod_confirmed": "(rec)",
        "new_window": "(session_id)", "reset_window": "(window, reason, at)",
        "observe_window": "(window, at, monotonic, *, complete, owned_seen, cutoff)",
        "window_complete": "(window, horizon, now=None)", "aggregate": "(local, reaper, *, now=None)",
    }
    for name, signature in expected.items():
        assert str(inspect.signature(getattr(evidence, name))) == signature
    assert (evidence.POLICY_VERSION, evidence.MAX_SCAN_GAP_SECONDS,
            evidence.CLOCK_TOLERANCE_SECONDS, evidence.MIN_WINDOW_SCANS) == (1, 60, 2, 6)


def test_timestamp_requires_finite_utc_and_preserves_subseconds():
    assert evidence.timestamp(at(0.125)) == EPOCH + 0.125
    assert evidence.timestamp(at().replace("+00:00", "Z")) == EPOCH
    for value in (None, True, 0, "", "not-a-date", "2026-01-01", "2026-01-01T00:00:00",
                  "2026-01-01T00:00:00+01:00", "99999-01-01T00:00:00Z"):
        with pytest.raises(evidence.EvidenceError):
            evidence.timestamp(value)
    for value in (None, True, "1", float("nan"), float("inf"), -float("inf"), 10 ** 400):
        with pytest.raises(evidence.EvidenceError):
            evidence.utc(value)


def test_empty_record_is_unresolved_and_validation_returns_detached_facts():
    rec = evidence.new_pod()
    assert not evidence.pod_confirmed(rec)
    derived = evidence.validate_pod(rec)
    assert derived == rec and derived is not rec and derived["history"] is not rec["history"]
    assert rec["delete_result"] == "NONE" and not rec["delete_attempted"]


@pytest.mark.parametrize("status", ["RUNNING", "PROVISIONING", "STARTING", "EXITED", "ERROR",
                                   "STOPPED", "UNKNOWN", None, {"untrusted": "value"}])
def test_original_falsifier_terminated_to_live_demotes_current_not_history(status):
    rec = terminated()
    old_history = deepcopy(rec["history"])
    assert evidence.pod_confirmed(rec)
    assert event(rec, "OBSERVE", status=status) is rec
    assert not evidence.pod_confirmed(rec)
    assert rec["positive_termination_observed"] is True
    assert rec["current_termination_observed"] is False
    assert rec["history"][:-1] == old_history
    assert rec["history"][-1]["contradictory_live_reappearance"] is True
    assert rec["last_positive_at_utc"] == at()
    assert rec["delete_result"] == "NONE" and rec["absence_confirmations"] == 0


def test_original_falsifier_ack_two_absences_then_live_requires_fresh_evidence():
    rec = acknowledged()
    event(rec, "ABSENT_SCAN", 0)
    assert rec["last_visibility"] == "NOT_VISIBLE" and not evidence.pod_confirmed(rec)
    event(rec, "ABSENT_SCAN", 1)
    assert evidence.pod_confirmed(rec)
    event(rec, "OBSERVE", 2, status="RUNNING")
    assert not evidence.pod_confirmed(rec) and rec["contradictory_live_reappearance"]
    event(rec, "ABSENT_SCAN", 3)
    event(rec, "ABSENT_SCAN", 4)
    assert rec["absence_confirmations"] == 0 and not evidence.pod_confirmed(rec)
    event(rec, "DELETE_RESULT", 5, result="ACK_204")
    event(rec, "ABSENT_SCAN", 6)
    event(rec, "ABSENT_SCAN", 7)
    assert evidence.pod_confirmed(rec)


def test_terminated_absent_live_terminated_recovery_preserves_contradiction():
    rec = terminated()
    event(rec, "ABSENT_SCAN")
    assert evidence.pod_confirmed(rec)
    event(rec, "OBSERVE", 1, status="RUNNING")
    assert not evidence.pod_confirmed(rec)
    event(rec, "OBSERVE", 2, status="TERMINATED")
    assert evidence.pod_confirmed(rec)
    assert rec["current_termination_observed"] and rec["contradictory_live_reappearance"]
    assert rec["history"][-1]["contradictory_live_reappearance"] is False


@pytest.mark.parametrize("result", [None, "NOT_FOUND_404", "HTTP_OTHER", "TRANSPORT_UNKNOWN",
                                   "unexpected", 204, True, {"status": 204}])
def test_b1_no_ack_is_invented_from_missing_or_unknown_delete_result(result):
    rec = evidence.new_pod()
    event(rec, "DELETE_RESULT", result=result)
    for seconds in range(1, 5):
        event(rec, "MISSING", seconds)
        event(rec, "ABSENT_SCAN", seconds)
    assert not evidence.pod_confirmed(rec)
    assert rec["delete_result"] != "ACK_204" and rec["absence_confirmations"] == 0


@pytest.mark.parametrize("result", [None, "NOT_FOUND_404", "HTTP_OTHER", "TRANSPORT_UNKNOWN"])
def test_later_non_ack_does_not_erase_ack_in_same_visibility_epoch(result):
    rec = acknowledged()
    event(rec, "ABSENT_SCAN")
    event(rec, "DELETE_ATTEMPT", 1)
    event(rec, "DELETE_RESULT", 1, result=result)
    event(rec, "ABSENT_SCAN", 2)
    assert rec["delete_result"] == "ACK_204" and evidence.pod_confirmed(rec)
    assert rec["history"][-2]["result"] == (result or "TRANSPORT_UNKNOWN")


def test_missing_get_is_not_absence_and_failed_inventory_breaks_absence_streak():
    rec = acknowledged()
    for _ in range(3):
        event(rec, "MISSING")
    assert rec["absence_confirmations"] == 0 and not evidence.pod_confirmed(rec)
    event(rec, "ABSENT_SCAN")
    event(rec, "SCAN_FAILED")
    event(rec, "ABSENT_SCAN")
    assert rec["absence_confirmations"] == 1 and not evidence.pod_confirmed(rec)
    event(rec, "ABSENT_SCAN")
    assert evidence.pod_confirmed(rec)


def test_b4_only_allowlisted_provider_values_and_fixed_exception_codes_are_retained():
    marker = "untrusted-provider-payload"
    rec = event(evidence.new_pod(), "OBSERVE", status=marker)
    event(rec, "DELETE_RESULT", result=marker)
    assert marker not in json.dumps(rec)
    assert rec["last_status"] == "UNKNOWN" and rec["delete_result"] == "TRANSPORT_UNKNOWN"
    with pytest.raises(evidence.EvidenceError) as caught:
        event(rec, marker)
    assert str(caught.value) == "INVALID_EVENT" and caught.value.code == "INVALID_EVENT"
    assert str(evidence.EvidenceError(marker)) == "INVALID_REPORT"


def test_pod_history_allows_wall_clock_rollback_but_not_sequence_gaps_or_future_events():
    rec = terminated(10)
    event(rec, "OBSERVE", 0, status="RUNNING")
    assert not evidence.pod_confirmed(evidence.validate_pod(rec, EPOCH + 10))
    with pytest.raises(evidence.EvidenceError, match="FUTURE_EVIDENCE"):
        evidence.validate_pod(rec, EPOCH + 5)
    rec["history"][1]["seq"] = 3
    with pytest.raises(evidence.EvidenceError, match="INVALID_EVENT"):
        evidence.validate_pod(rec)


@pytest.mark.parametrize("field,value", [
    ("cleanup_confidence", "CONFIRMED"), ("current_termination_observed", True),
    ("positive_termination_observed", 1), ("absence_confirmations", True),
    ("delete_result", "ACK_204"), ("last_positive_at_utc", at()),
])
def test_pod_snapshot_tampering_is_rejected(field, value):
    rec = evidence.new_pod()
    rec[field] = value
    with pytest.raises(evidence.EvidenceError):
        evidence.pod_confirmed(rec)


@pytest.mark.parametrize("mutation", [
    lambda rec: rec.pop("history"),
    lambda rec: rec.update(history=None),
    lambda rec: rec["history"][0].update(seq=True),
    lambda rec: rec["history"][0].update(status="untrusted"),
    lambda rec: rec["history"][0].update(result="ACK_204"),
    lambda rec: rec["history"][0].update(contradictory_live_reappearance=True),
    lambda rec: rec["history"][0].update(raw_provider_object={}),
])
def test_malformed_history_is_not_promoted(mutation):
    rec = terminated()
    mutation(rec)
    with pytest.raises(evidence.EvidenceError):
        evidence.validate_pod(rec)


def test_original_falsifier_twenty_seconds_cannot_confirm_3600_second_horizon():
    window = healthy(end=20, step=4)
    assert window["scan_count"] == 6 and window["covered_seconds"] == 20
    assert not evidence.window_complete(window, 3600)
    assert_unresolved(combine(*reports({"pod-1": terminated()}, window=window), now=20))


def test_hour_blind_then_fifty_second_burst_counts_only_the_burst():
    window = evidence.new_window("session")
    scan(window, 0)
    for seconds in range(3600, 3651, 10):
        scan(window, seconds)
    assert window["covered_seconds"] == 50 and window["scan_count"] == 6
    assert window["history"][0]["reason"] == "SCAN_GAP"
    assert not evidence.window_complete(window, 3600)


def test_healthy_hour_and_freshness_boundary_require_both_count_and_duration():
    window = healthy()
    assert window["scan_count"] == 61 and window["covered_seconds"] == 3600
    assert evidence.window_complete(window, 3600, EPOCH + 3660)
    assert not evidence.window_complete(window, 3600, EPOCH + 3660.001)
    assert not evidence.window_complete(healthy(end=40, step=10), 40)
    assert evidence.window_complete(healthy(end=50, step=10), 50)


@pytest.mark.parametrize("at_seconds,complete,owned_seen", [(1800, False, False), (3500, True, True)])
def test_failure_or_owned_discovery_restarts_full_horizon(at_seconds, complete, owned_seen):
    window = healthy(end=at_seconds - 10, step=10)
    old_samples = deepcopy(window["samples"])
    scan(window, at_seconds, complete=complete, owned_seen=owned_seen)
    assert window["interrupted"] and window["covered_seconds"] == 0
    assert window["history"][-1]["samples"] == old_samples
    for seconds in range(at_seconds + 10, 3601, 10):
        scan(window, seconds)
    assert not window["interrupted"] and not evidence.window_complete(window, 3600)


def test_partial_inventory_retains_positive_and_permission_loss_never_counts_empty():
    rec, window = terminated(), healthy(end=50, step=10)
    event(rec, "OBSERVE", 60, status="RUNNING")  # Positive received on an early page.
    scan(window, 60, complete=False, owned_seen=True)  # Later page failed.
    assert not evidence.pod_confirmed(rec) and window["samples"] == []
    assert window["reset_reason"] == "OWNED_SEEN"
    event(rec, "UNKNOWN", 70)
    event(rec, "SCAN_FAILED", 70)
    scan(window, 70, complete=False)
    assert window["scan_count"] == 0 and not evidence.pod_confirmed(rec)


def test_unrelated_or_partial_identity_matches_do_not_interrupt_empty_window():
    # Exact ownership classification belongs to consumers. Unrelated/partial
    # matches MUST be passed as owned_seen=False, not as owned IDs or anomalies.
    window = healthy()
    scan(window, 3660, owned_seen=False)
    assert evidence.window_complete(window, 3600, EPOCH + 3660)
    scan(window, 3670, owned_seen=True)  # Even exact-owned TERMINATED is positive.
    assert window["samples"] == [] and window["reset_reason"] == "OWNED_SEEN"


@pytest.mark.parametrize("state", ["EMPTY", "LIVE", "ACK", "ONE_ABSENCE", "CONFIRMED", "TERMINATED"])
def test_b3_restart_archives_window_without_erasing_any_pod_evidence(state):
    rec = evidence.new_pod()
    if state != "EMPTY":
        event(rec, "OBSERVE", status="TERMINATED" if state == "TERMINATED" else "RUNNING")
    if state in {"ACK", "ONE_ABSENCE", "CONFIRMED"}:
        event(rec, "DELETE_RESULT", result="ACK_204")
    for _ in range({"ONE_ABSENCE": 1, "CONFIRMED": 2}.get(state, 0)):
        event(rec, "ABSENT_SCAN")
    rec = json.loads(json.dumps(rec))
    before = deepcopy(rec)
    window = json.loads(json.dumps(healthy()))
    evidence.reset_window(window, "PROCESS_RESTART", None)
    window["session_id"] = "session-2"
    assert window["history"][0]["session_id"] == "session-1"
    assert len(window["history"][0]["samples"]) == 61
    scan(window, 7200, mono=0)
    assert not evidence.window_complete(window, 3600)
    assert window["scan_count"] == 1 and window["covered_seconds"] == 0
    assert evidence.validate_pod(rec) == before
    evidence.reset_window(window, "PROCESS_RESTART", None)
    assert len(window["history"]) == 2  # Older archives were not rewritten.


@pytest.mark.parametrize("wall,mono", [(9, 20), (20, 9), (50, 20), (20, 50), (71, 71)])
def test_clock_discontinuity_good_current_sample_starts_at_zero(wall, mono):
    window = evidence.new_window("session")
    scan(window, 10)
    scan(window, wall, mono)
    assert window["scan_count"] == 1 and window["covered_seconds"] == 0
    assert len(window["history"]) == 1 and not evidence.window_complete(window, 1)


def test_delta_tolerance_and_both_total_clock_spans_are_checked():
    window = evidence.new_window("session")
    for index in range(6):
        scan(window, index * 12, mono=index * 10)
    assert window["covered_seconds"] == 50
    assert evidence.window_complete(window, 50) and not evidence.window_complete(window, 60)
    scan(window, 72.001, mono=60)
    assert window["scan_count"] == 1


@pytest.mark.parametrize("mono", [float("nan"), float("inf"), -float("inf"), None, True, "10"])
def test_bad_monotonic_resets_without_persisting_nonfinite_values(mono):
    window = healthy(end=50, step=10)
    evidence.observe_window(window, at(60), mono, complete=True, owned_seen=False, cutoff=at())
    assert window["samples"] == [] and window["reset_reason"] == "CLOCK_INVALID"
    json.dumps(window, allow_nan=False)


def test_precutoff_sample_resets_and_cannot_start_a_window():
    window = healthy(end=50, step=10)
    scan(window, -1)
    assert window["samples"] == [] and window["reset_reason"] == "BEFORE_CUTOFF"
    scan(window, 0)
    assert window["scan_count"] == 1 and window["covered_seconds"] == 0


@pytest.mark.parametrize("mutation", [
    lambda w: w.pop("history"), lambda w: w.update(scan_count=True),
    lambda w: w.update(covered_seconds=36000), lambda w: w.update(latest_utc=at(3700)),
    lambda w: w.update(interrupted=True), lambda w: w.update(reset_reason="SCAN_FAILED"),
    lambda w: w["samples"][2].update(at_utc="malformed"),
    lambda w: w["samples"][2].update(at_utc=at(121)),
    lambda w: w["samples"][2].update(monotonic=float("nan")),
    lambda w: w["samples"][2].update(monotonic=1),
    lambda w: w["samples"][2].update(complete=False),
    lambda w: w["samples"][2].update(owned_seen=True),
    lambda w: w["samples"][2].update(session_id="different-process"),
    lambda w: w["samples"][2].update(cutoff_utc=at(200)),
])
def test_malformed_or_forged_window_fails_closed(mutation):
    window = healthy()
    mutation(window)
    with pytest.raises(evidence.EvidenceError):
        evidence.window_complete(window, 3600, EPOCH + 3600)


@pytest.mark.parametrize("horizon", [None, True, 0, -1, "3600", float("nan"), float("inf")])
def test_invalid_horizon_is_not_pending(horizon):
    with pytest.raises(evidence.EvidenceError, match="INVALID_HORIZON"):
        evidence.window_complete(evidence.new_window("session"), horizon)


def test_future_current_or_archived_samples_and_reset_times_are_rejected():
    window = healthy()
    with pytest.raises(evidence.EvidenceError, match="FUTURE_EVIDENCE"):
        evidence.window_complete(window, 3600, EPOCH + 3599)
    evidence.reset_window(window, "PROCESS_RESTART", at(4000))
    with pytest.raises(evidence.EvidenceError, match="FUTURE_EVIDENCE"):
        evidence.window_complete(window, 3600, EPOCH + 3999)
    window["history"][0]["at_utc"] = None
    with pytest.raises(evidence.EvidenceError, match="FUTURE_EVIDENCE"):
        evidence.window_complete(window, 3600, EPOCH + 3599)


def test_archived_coverage_cannot_be_restored_before_the_reset_timestamp():
    window = healthy()
    old = deepcopy(window)
    evidence.reset_window(window, "SCAN_FAILED", at(3601))
    # Even internally consistent counters cannot revive a pre-failure horizon.
    old["history"] = window["history"]
    old["reset_reason"] = "SCAN_FAILED"
    with pytest.raises(evidence.EvidenceError, match="INVALID_WINDOW"):
        evidence.window_complete(old, 3600, EPOCH + 3601)
    # A real backward clock reading after failure starts fresh at zero instead.
    scan(window, 3500)
    assert window["reset_reason"] == "CLOCK_DISCONTINUITY"
    assert window["scan_count"] == 1 and window["covered_seconds"] == 0
    assert not evidence.window_complete(window, 3600, EPOCH + 3601)


def test_b2_b5_empty_union_still_requires_complete_fresh_independent_horizon():
    local, reaper = reports(window=evidence.new_window("session"))
    result = combine(local, reaper)
    assert result["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_CONFIRMED"
    assert result["reconciliation_window_status"] == "RECONCILIATION_PENDING"
    assert_unresolved(result)
    reaper["window"] = healthy()
    assert combine(local, reaper)["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"
    assert_unresolved(combine(local, reaper, now=3661))


def test_union_retains_local_only_reaper_only_and_multiple_exact_owned_ids():
    local, reaper = reports({"local-only": terminated(), "shared": terminated()},
                            {"reaper-only": terminated(), "shared": terminated()})
    before = deepcopy((local, reaper))
    assert combine(local, reaper)["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"
    assert (local, reaper) == before
    reaper["owned_ids"].append("late-duplicate")
    reaper["pod_evidence"]["late-duplicate"] = evidence.new_pod()
    assert_unresolved(combine(local, reaper))
    reaper["pod_evidence"]["late-duplicate"] = terminated()
    assert combine(local, reaper)["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"


@pytest.mark.parametrize("side", [0, 1])
def test_success_labels_cannot_hide_live_evidence_or_tampered_confidence(side):
    pair = reports({"pod": terminated()}, {"pod": terminated()})
    rec = pair[side]["pod_evidence"]["pod"]
    event(rec, "OBSERVE", 1, status="RUNNING")
    result = combine(*pair)
    assert result["known_owned_cleanup_status"] == "KNOWN_OWNED_CLEANUP_UNRESOLVED"
    assert_unresolved(result)
    rec["cleanup_confidence"] = "CONFIRMED"
    with pytest.raises(evidence.EvidenceError):
        combine(*pair)


@pytest.mark.parametrize("side,key,value", [
    (0, "journal_ok", False), (1, "journal_ok", False),
    (0, "ownership_ambiguous", True), (1, "ownership_ambiguous", True),
    (0, "cleanup_status", "LOCAL_CLEANUP_UNRESOLVED"),
    (1, "status", "REAPER_CLEANUP_UNRESOLVED"), (1, "status", "REAPER_PENDING"),
])
def test_neither_bad_health_nor_unresolved_side_can_be_overridden(side, key, value):
    pair = reports()
    pair[side][key] = value
    assert_unresolved(combine(*pair))


def test_hidden_ownership_conflict_in_history_cannot_be_cleared_by_report_flag():
    rec = terminated(-3)
    event(rec, "OWNERSHIP_CONFLICT", -2)
    assert not evidence.pod_confirmed(rec)
    event(rec, "OBSERVE", -1, status="TERMINATED")
    assert_unresolved(combine(*reports({"pod": rec})))


def test_window_must_strictly_follow_latest_local_event_even_after_wall_rollback():
    rec = terminated(5)
    event(rec, "OBSERVE", -1, status="TERMINATED")
    pair = reports({"pod": rec})
    assert combine(*pair)["reconciliation_window_status"] == "RECONCILIATION_PENDING"
    pair[1]["window"] = healthy(start=6, end=3606)
    assert combine(*pair, now=3606)["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"
    pair = reports({"pod": terminated(0)})
    assert_unresolved(combine(*pair))


@pytest.mark.parametrize("kind", ["OBSERVE", "SCAN_FAILED", "UNKNOWN"])
def test_reaper_positive_or_inventory_failure_cannot_coexist_with_claimed_empty_horizon(kind):
    rec = terminated()
    event(rec, kind, 1800, status="TERMINATED")
    result = combine(*reports(reaper_pods={"pod": rec}))
    assert result["reconciliation_window_status"] == "RECONCILIATION_PENDING"
    assert_unresolved(result)


@pytest.mark.parametrize("result", ["HTTP_OTHER", "TRANSPORT_UNKNOWN"])
def test_reaper_delete_failure_cannot_coexist_with_claimed_empty_horizon(result):
    rec = terminated()
    event(rec, "DELETE_RESULT", 1800, result=result)
    outcome = combine(*reports(reaper_pods={"pod": rec}))
    assert outcome["reconciliation_window_status"] == "RECONCILIATION_PENDING"
    assert_unresolved(outcome)


@pytest.mark.parametrize("side", [0, 1])
@pytest.mark.parametrize("field", ["policy_version", "manifest", "manifest_sha256", "run_id",
                                   "owned_ids", "pod_evidence", "journal_ok", "ownership_ambiguous"])
def test_missing_required_report_fields_never_get_optimistic_defaults(side, field):
    pair = reports()
    del pair[side][field]
    with pytest.raises(evidence.EvidenceError):
        combine(*pair)


@pytest.mark.parametrize("mutation", [
    lambda l, r: r.pop("window"), lambda l, r: r.update(window=None),
    lambda l, r: l.pop("cleanup_status"), lambda l, r: r.pop("status"),
    lambda l, r: l.update(policy_version=True), lambda l, r: r.update(policy_version=0),
    lambda l, r: l.update(journal_ok=1), lambda l, r: r.update(ownership_ambiguous=0),
    lambda l, r: l.update(owned_ids=["missing-pod"]),
    lambda l, r: r.update(pod_evidence={"unlisted-pod": terminated()}),
    lambda l, r: l.update(owned_ids=["pod", "pod"], pod_evidence={"pod": terminated()}),
    lambda l, r: l.update(manifest_sha256="0" * 64),
    lambda l, r: r.update(run_id="other-run"),
    lambda l, r: r.update(status="UNRECOGNIZED_SUCCESS"),
])
def test_invalid_reports_and_bindings_raise_not_confirm(mutation):
    local, reaper = reports()
    mutation(local, reaper)
    with pytest.raises(evidence.EvidenceError):
        combine(local, reaper)


@pytest.mark.parametrize("field,value", [
    ("run_id", "bad id"), ("run_name", ""), ("image", "registry.example/aeth01:latest"),
    ("creation_intent_id", "other-run"), ("cutoff_reference", None), ("version", True),
    ("cutoff_utc", "2026-01-01T00:00:00"), ("reconciliation_horizon_seconds", 0),
    ("reconciliation_horizon_seconds", True), ("reconciliation_horizon_seconds", float("inf")),
    ("hourly_rate_usd", float("nan")), ("canary_budget_usd", -1),
])
def test_manifest_structure_is_checked_even_if_both_digests_match(field, value):
    pair = reports()
    malformed = manifest()
    malformed[field] = value
    for report in pair:
        bind(report, malformed)
    with pytest.raises(evidence.EvidenceError):
        combine(*pair)


def test_manifest_horizon_and_cutoff_mismatch_cannot_be_rebound_away():
    local, reaper = reports()
    altered = manifest()
    altered["reconciliation_horizon_seconds"] = 20
    bind(reaper, altered)
    with pytest.raises(evidence.EvidenceError, match="MANIFEST_MISMATCH"):
        combine(local, reaper)
    altered = manifest()
    altered["cutoff_utc"] = at(100)
    bind(local, altered)
    bind(reaper, altered)
    with pytest.raises(evidence.EvidenceError, match="MANIFEST_MISMATCH"):
        combine(local, reaper)


def test_future_history_is_checked_on_both_sides_not_just_last_event():
    rec = terminated(3700)
    event(rec, "OBSERVE", -1, status="TERMINATED")
    for pair in (reports({"pod": rec}), reports(reaper_pods={"pod": rec})):
        with pytest.raises(evidence.EvidenceError, match="FUTURE_EVIDENCE"):
            combine(*pair)


def test_default_now_uses_current_time_and_invalid_now_is_rejected(monkeypatch):
    pair = reports()
    monkeypatch.setattr(evidence.time, "time", lambda: EPOCH + 3600)
    assert evidence.aggregate(*pair)["operational_cleanup_status"] == "OPERATIONAL_CLEANUP_CONFIRMED"
    monkeypatch.setattr(evidence.time, "time", lambda: EPOCH + 3661)
    assert_unresolved(evidence.aggregate(*pair))
    for now in (True, float("nan"), float("inf"), "3600"):
        with pytest.raises(evidence.EvidenceError):
            evidence.aggregate(*pair, now=now)