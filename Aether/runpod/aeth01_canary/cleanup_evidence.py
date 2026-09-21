"""Pure, secret-free cleanup evidence policy v1; no provider or persistence I/O.

Mutators update and return their dictionary. Validators replay rather than trust
snapshots. Pod history is sequence-ordered, not wall-clock-ordered. A historical
termination or contradiction survives recovery, but is not current proof.
Window resets archive samples without crediting them to the current session.
Ownership classification, durable writes and new-invocation resets are callers'
responsibility; this module neither authenticates reports nor proves billing stop.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import time


POLICY_VERSION = 1
MAX_SCAN_GAP_SECONDS = 60
CLOCK_TOLERANCE_SECONDS = 2
MIN_WINDOW_SCANS = 6

_KINDS = frozenset({"DELETE_ATTEMPT", "DELETE_RESULT", "OBSERVE", "ABSENT_SCAN",
                    "MISSING", "UNKNOWN", "SCAN_FAILED", "OWNERSHIP_CONFLICT"})
_STATUSES = frozenset({"CREATED", "PENDING", "PROVISIONING", "STARTING", "RUNNING",
                       "STOPPING", "STOPPED", "EXITED", "ERROR", "TERMINATED", "UNKNOWN"})
_RESULTS = frozenset({"ACK_204", "NOT_FOUND_404", "HTTP_OTHER", "TRANSPORT_UNKNOWN"})
_ERRORS = frozenset({"INVALID_UTC", "INVALID_NUMBER", "INVALID_POD", "INVALID_EVENT",
                     "SNAPSHOT_MISMATCH", "FUTURE_EVIDENCE", "INVALID_WINDOW",
                     "INVALID_HORIZON", "INVALID_MANIFEST", "MANIFEST_MISMATCH",
                     "INVALID_REPORT"})
_EVENT_KEYS = {"seq", "kind", "at_utc", "status", "result", "contradictory_live_reappearance"}
_SAMPLE_KEYS = {"at_utc", "monotonic", "complete", "owned_seen", "cutoff_utc", "session_id"}
_RESET_KEYS = {"seq", "reason", "at_utc", "session_id", "samples"}
_WINDOW_KEYS = {"session_id", "samples", "history", "start_utc", "latest_utc",
                "covered_seconds", "scan_count", "interrupted", "reset_reason"}
_MANIFEST_KEYS = {"version", "run_id", "run_name", "image", "creation_intent_id",
                  "cutoff_utc", "cutoff_reference", "reconciliation_horizon_seconds",
                  "hourly_rate_usd", "canary_budget_usd"}
_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
_IMAGE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/:+-]*@sha256:[0-9a-f]{64}")
_CODE = re.compile(r"[A-Z][A-Z0-9_]{0,63}")


class EvidenceError(ValueError):
    """Only fixed codes are exposed, never rejected input or exception text."""

    def __init__(self, code="INVALID_REPORT"):
        self.code = code if isinstance(code, str) and code in _ERRORS else "INVALID_REPORT"
        super().__init__(self.code)


def _require(condition, code):
    if not condition:
        raise EvidenceError(code)


def _number(value, code="INVALID_NUMBER"):
    _require(type(value) in (int, float), code)
    try:
        value = float(value)
        _require(math.isfinite(value), code)
    except (OverflowError, ValueError):
        raise EvidenceError(code) from None
    return value


def _text(value, limit=256):
    return (isinstance(value, str) and 0 < len(value) <= limit and bool(value.strip())
            and all(32 <= ord(char) <= 126 for char in value))


def timestamp(value):
    """Parse a timezone-aware UTC string to finite Unix seconds (no naive dates)."""
    _require(isinstance(value, str), "INVALID_UTC")
    try:
        stamp = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        _require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds() == 0,
                 "INVALID_UTC")
        return _number(stamp.timestamp(), "INVALID_UTC")
    except (ValueError, OverflowError, OSError):
        raise EvidenceError("INVALID_UTC") from None


def utc(number):
    """Format finite Unix seconds as a timezone-aware UTC ISO timestamp."""
    number = _number(number, "INVALID_UTC")
    try:
        return datetime.fromtimestamp(number, timezone.utc).isoformat()
    except (ValueError, OverflowError, OSError):
        raise EvidenceError("INVALID_UTC") from None


def _not_future(at, now):
    seconds = timestamp(at)
    if now is not None:
        _require(seconds <= now, "FUTURE_EVIDENCE")
    return seconds


def new_pod():
    return {"history": [], "delete_attempted": False, "delete_result": "NONE",
            "last_visibility": "UNKNOWN", "last_status": None,
            "positive_termination_observed": False, "current_termination_observed": False,
            "last_positive_at_utc": None, "contradictory_live_reappearance": False,
            "absence_confirmations": 0, "cleanup_confidence": "UNRESOLVED"}


def _apply_event(facts, event):
    kind = event["kind"]
    contradiction = False
    if kind == "DELETE_ATTEMPT":
        facts["delete_attempted"] = True
    elif kind == "DELETE_RESULT":
        facts["delete_attempted"] = True
        # A failed retry cannot erase a positive ACK in this visibility epoch.
        if facts["delete_result"] != "ACK_204":
            facts["delete_result"] = event["result"]
    elif kind == "OBSERVE":
        terminated = event["status"] == "TERMINATED"
        contradiction = not terminated and (
            facts["current_termination_observed"] or facts["delete_result"] == "ACK_204")
        facts["last_visibility"] = "VISIBLE"
        facts["last_status"] = event["status"]
        facts["last_positive_at_utc"] = event["at_utc"]
        facts["current_termination_observed"] = terminated
        facts["positive_termination_observed"] |= terminated
        facts["contradictory_live_reappearance"] |= contradiction
        facts["absence_confirmations"] = 0
        if not terminated:
            facts["delete_result"] = "NONE"
    elif kind == "ABSENT_SCAN":
        facts["last_visibility"] = "NOT_VISIBLE"
        if facts["delete_result"] == "ACK_204":
            facts["absence_confirmations"] += 1
    elif kind == "MISSING":
        # Ambiguous GET 404 is not a complete inventory witness.
        facts["last_visibility"] = "NOT_VISIBLE"
    elif kind in ("UNKNOWN", "SCAN_FAILED"):
        facts["last_visibility"] = "UNKNOWN"
        facts["absence_confirmations"] = 0
    elif kind == "OWNERSHIP_CONFLICT":
        facts["last_visibility"] = "VISIBLE"
        facts["last_status"] = "UNKNOWN"
        facts["last_positive_at_utc"] = event["at_utc"]
        facts["current_termination_observed"] = False
        facts["delete_result"] = "NONE"
        facts["absence_confirmations"] = 0
    confirmed = facts["current_termination_observed"] or (
        facts["delete_result"] == "ACK_204" and facts["last_visibility"] == "NOT_VISIBLE"
        and facts["absence_confirmations"] >= 2)
    facts["cleanup_confidence"] = "CONFIRMED" if confirmed else "UNRESOLVED"
    return contradiction


def _replay_pod(history, now=None):
    _require(isinstance(history, list), "INVALID_POD")
    facts = new_pod()
    for seq, event in enumerate(history, 1):
        _require(isinstance(event, dict) and set(event) == _EVENT_KEYS, "INVALID_EVENT")
        _require(type(event["seq"]) is int and event["seq"] == seq, "INVALID_EVENT")
        kind = event["kind"]
        _require(isinstance(kind, str) and kind in _KINDS, "INVALID_EVENT")
        _not_future(event["at_utc"], now)
        _require((isinstance(event["status"], str) and event["status"] in _STATUSES)
                 if kind == "OBSERVE" else event["status"] is None, "INVALID_EVENT")
        _require((isinstance(event["result"], str) and event["result"] in _RESULTS)
                 if kind == "DELETE_RESULT" else event["result"] is None, "INVALID_EVENT")
        contradiction = _apply_event(facts, event)
        _require(type(event["contradictory_live_reappearance"]) is bool
                 and event["contradictory_live_reappearance"] == contradiction, "INVALID_EVENT")
    facts["history"] = deepcopy(history)
    return facts


def validate_pod(rec, now=None):
    """Return a detached replay-derived record; reject missing or forged facts."""
    if now is not None:
        now = _number(now)
    _require(isinstance(rec, dict) and set(rec) == set(new_pod()), "INVALID_POD")
    facts = _replay_pod(rec["history"], now)
    for key, value in facts.items():
        _require(type(rec[key]) is type(value) and rec[key] == value, "SNAPSHOT_MISMATCH")
    return facts


def append_pod(rec, kind, at, *, status=None, result=None):
    facts = validate_pod(rec)
    _require(isinstance(kind, str) and kind in _KINDS, "INVALID_EVENT")
    timestamp(at)
    event = {"seq": len(facts["history"]) + 1, "kind": kind, "at_utc": at,
             "status": None, "result": None, "contradictory_live_reappearance": False}
    if kind == "OBSERVE":
        event["status"] = status if isinstance(status, str) and status in _STATUSES else "UNKNOWN"
    if kind == "DELETE_RESULT":
        event["result"] = result if isinstance(result, str) and result in _RESULTS else "TRANSPORT_UNKNOWN"
    event["contradictory_live_reappearance"] = _apply_event(facts, event)
    facts["history"].append(event)
    rec.update(facts)
    return rec


def pod_confirmed(rec):
    return validate_pod(rec)["cleanup_confidence"] == "CONFIRMED"


def new_window(session_id):
    _require(_text(session_id, 128), "INVALID_WINDOW")
    return {"session_id": session_id, "samples": [], "history": [], "start_utc": None,
            "latest_utc": None, "covered_seconds": 0.0, "scan_count": 0,
            "interrupted": False, "reset_reason": None}


def _discontinuity(previous, current):
    wall = timestamp(current["at_utc"]) - timestamp(previous["at_utc"])
    mono = current["monotonic"] - previous["monotonic"]
    if wall < 0 or mono < 0 or abs(wall - mono) > CLOCK_TOLERANCE_SECONDS:
        return "CLOCK_DISCONTINUITY"
    if wall > MAX_SCAN_GAP_SECONDS or mono > MAX_SCAN_GAP_SECONDS:
        return "SCAN_GAP"
    if timestamp(previous["cutoff_utc"]) != timestamp(current["cutoff_utc"]):
        return "CUTOFF_CHANGED"
    return None


def _validate_samples(samples, session_id, now):
    _require(isinstance(samples, list), "INVALID_WINDOW")
    previous = None
    for sample in samples:
        _require(isinstance(sample, dict) and set(sample) == _SAMPLE_KEYS, "INVALID_WINDOW")
        at = _not_future(sample["at_utc"], now)
        _number(sample["monotonic"], "INVALID_WINDOW")
        _require(sample["complete"] is True and sample["owned_seen"] is False
                 and sample["session_id"] == session_id
                 and at >= timestamp(sample["cutoff_utc"]), "INVALID_WINDOW")
        if previous is not None:
            _require(_discontinuity(previous, sample) is None, "INVALID_WINDOW")
        previous = sample


def _window_facts(window):
    samples = window["samples"]
    history = window["history"]
    covered = 0.0
    if samples:
        covered = min(timestamp(samples[-1]["at_utc"]) - timestamp(samples[0]["at_utc"]),
                      samples[-1]["monotonic"] - samples[0]["monotonic"])
    return {"start_utc": samples[0]["at_utc"] if samples else None,
            "latest_utc": samples[-1]["at_utc"] if samples else None,
            "covered_seconds": covered, "scan_count": len(samples),
            "interrupted": bool(history) and not samples,
            "reset_reason": history[-1]["reason"] if history else None}


def _validate_window(window, now=None):
    _require(isinstance(window, dict) and set(window) == _WINDOW_KEYS, "INVALID_WINDOW")
    _require(_text(window["session_id"], 128) and isinstance(window["history"], list),
             "INVALID_WINDOW")
    for seq, event in enumerate(window["history"], 1):
        _require(isinstance(event, dict) and set(event) == _RESET_KEYS, "INVALID_WINDOW")
        _require(type(event["seq"]) is int and event["seq"] == seq
                 and isinstance(event["reason"], str) and _CODE.fullmatch(event["reason"])
                 and _text(event["session_id"], 128), "INVALID_WINDOW")
        if event["at_utc"] is not None:
            _not_future(event["at_utc"], now)
        _validate_samples(event["samples"], event["session_id"], now)
    _validate_samples(window["samples"], window["session_id"], now)
    if window["history"] and window["samples"]:
        reset_at = window["history"][-1]["at_utc"]
        _require(reset_at is None or timestamp(window["samples"][0]["at_utc"]) >= timestamp(reset_at),
                 "INVALID_WINDOW")
    facts = _window_facts(window)
    _number(window["covered_seconds"], "INVALID_WINDOW")
    for key, value in facts.items():
        if key != "covered_seconds":
            _require(type(window[key]) is type(value), "INVALID_WINDOW")
        _require(window[key] == value, "SNAPSHOT_MISMATCH")
    return facts


def reset_window(window, reason, at):
    """Archive current samples; preserve previous reset history. Reasons are codes."""
    _validate_window(window)
    _require(isinstance(reason, str) and _CODE.fullmatch(reason), "INVALID_WINDOW")
    if at is not None:
        timestamp(at)
    window["history"].append({"seq": len(window["history"]) + 1, "reason": reason,
                              "at_utc": at, "session_id": window["session_id"],
                              "samples": deepcopy(window["samples"])})
    window["samples"] = []
    window.update(_window_facts(window))
    return window


def observe_window(window, at, monotonic, *, complete, owned_seen, cutoff):
    """Record a complete empty scan, or reset; a discontinuity earns zero time."""
    _validate_window(window)
    wall, cutoff_seconds = timestamp(at), timestamp(cutoff)
    _require(type(complete) is bool and type(owned_seen) is bool, "INVALID_WINDOW")
    if owned_seen:
        return reset_window(window, "OWNED_SEEN", at)
    if not complete:
        return reset_window(window, "SCAN_FAILED", at)
    if wall < cutoff_seconds:
        return reset_window(window, "BEFORE_CUTOFF", at)
    try:
        monotonic = _number(monotonic, "INVALID_WINDOW")
    except EvidenceError:
        return reset_window(window, "CLOCK_INVALID", at)
    sample = {"at_utc": at, "monotonic": monotonic, "complete": True,
              "owned_seen": False, "cutoff_utc": cutoff, "session_id": window["session_id"]}
    if window["samples"]:
        reason = _discontinuity(window["samples"][-1], sample)
        if reason is not None:
            reset_window(window, reason, at)
    elif window["history"]:
        reset_at = window["history"][-1]["at_utc"]
        if reset_at is not None and wall < timestamp(reset_at):
            reset_window(window, "CLOCK_DISCONTINUITY", at)
    window["samples"].append(sample)
    window.update(_window_facts(window))
    return window


def window_complete(window, horizon, now=None):
    """Malformed/future evidence raises; incomplete or stale evidence is pending."""
    horizon = _number(horizon, "INVALID_HORIZON")
    _require(horizon > 0, "INVALID_HORIZON")
    if now is not None:
        now = _number(now)
    facts = _validate_window(window, now)
    if facts["scan_count"] < MIN_WINDOW_SCANS or facts["covered_seconds"] < horizon:
        return False
    return now is None or now - timestamp(facts["latest_utc"]) <= MAX_SCAN_GAP_SECONDS


def _manifest_digest(manifest):
    _require(isinstance(manifest, dict) and set(manifest) == _MANIFEST_KEYS, "INVALID_MANIFEST")
    _require(type(manifest["version"]) is int and manifest["version"] == POLICY_VERSION,
             "INVALID_MANIFEST")
    run_id = manifest["run_id"]
    _require(isinstance(run_id, str) and _ID.fullmatch(run_id)
             and manifest["creation_intent_id"] == run_id, "INVALID_MANIFEST")
    _require(isinstance(manifest["run_name"], str)
             and re.fullmatch(r"[A-Za-z0-9_-]{1,256}", manifest["run_name"])
             and isinstance(manifest["image"], str) and _IMAGE.fullmatch(manifest["image"])
             and _text(manifest["cutoff_reference"], 4096), "INVALID_MANIFEST")
    timestamp(manifest["cutoff_utc"])
    horizon = manifest["reconciliation_horizon_seconds"]
    _require(type(horizon) is int and horizon > 0, "INVALID_MANIFEST")
    _number(horizon, "INVALID_MANIFEST")
    for key in ("hourly_rate_usd", "canary_budget_usd"):
        _require(_number(manifest[key], "INVALID_MANIFEST") > 0, "INVALID_MANIFEST")
    raw = (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_report(report, side, now):
    required = {"policy_version", "manifest", "manifest_sha256", "run_id", "owned_ids",
                "pod_evidence", "journal_ok", "ownership_ambiguous"}
    required |= {"cleanup_status"} if side == "local" else {"status", "window"}
    _require(isinstance(report, dict) and required <= set(report), "INVALID_REPORT")
    _require(type(report["policy_version"]) is int and report["policy_version"] == POLICY_VERSION,
             "INVALID_REPORT")
    digest = _manifest_digest(report["manifest"])
    _require(report["manifest_sha256"] == digest
             and report["run_id"] == report["manifest"]["run_id"], "MANIFEST_MISMATCH")
    _require(type(report["journal_ok"]) is bool and type(report["ownership_ambiguous"]) is bool,
             "INVALID_REPORT")
    ids = report["owned_ids"]
    _require(isinstance(ids, list) and all(isinstance(pid, str) and _ID.fullmatch(pid) for pid in ids),
             "INVALID_REPORT")
    _require(len(ids) == len(set(ids)) and isinstance(report["pod_evidence"], dict)
             and set(report["pod_evidence"]) == set(ids), "INVALID_REPORT")
    if side == "local":
        allowed = {"LOCAL_CLEANUP_CONFIRMED", "LOCAL_CLEANUP_UNRESOLVED", "UNRESOLVED"}
        status = report["cleanup_status"]
    else:
        allowed = {"REAPER_CLEANUP_CONFIRMED", "REAPER_CLEANUP_UNRESOLVED", "REAPER_PENDING",
                   "UNRESOLVED", "PENDING"}
        status = report["status"]
    _require(isinstance(status, str) and status in allowed, "INVALID_REPORT")
    return {pid: validate_pod(rec, now) for pid, rec in report["pod_evidence"].items()}


def aggregate(local, reaper, *, now=None):
    """Validate bound reports and derive three separate cleanup propositions.

    Side labels are returned for provenance, not accepted as proof. Every record
    from both sources must currently confirm (including shared IDs). A pod already
    deleted locally need not occur in the reaper's independently empty horizon.
    """
    now = _number(time.time() if now is None else now)
    local_pods = _validate_report(local, "local", now)
    reaper_pods = _validate_report(reaper, "reaper", now)
    _require(local["manifest_sha256"] == reaper["manifest_sha256"]
             and local["manifest"] == reaper["manifest"]
             and local["run_id"] == reaper["run_id"], "MANIFEST_MISMATCH")
    manifest, window = local["manifest"], reaper["window"]
    window_ok = window_complete(window, manifest["reconciliation_horizon_seconds"], now)
    cutoff = timestamp(manifest["cutoff_utc"])
    sample_groups = [window["samples"]] + [entry["samples"] for entry in window["history"]]
    for samples in sample_groups:
        for sample in samples:
            _require(timestamp(sample["cutoff_utc"]) == cutoff
                     and timestamp(sample["at_utc"]) >= cutoff, "MANIFEST_MISMATCH")
    local_events = [event for rec in local_pods.values() for event in rec["history"]]
    reaper_events = [event for rec in reaper_pods.values() for event in rec["history"]]
    if window["start_utc"] is not None:
        start = timestamp(window["start_utc"])
        if local_events and start <= max(timestamp(event["at_utc"]) for event in local_events):
            window_ok = False
        # Claimed empty coverage cannot coexist with independent positive/failure
        # evidence during or after it, even if the reaper forgot to reset its window.
        if any((event["kind"] in {"OBSERVE", "SCAN_FAILED", "OWNERSHIP_CONFLICT", "UNKNOWN"}
                or (event["kind"] == "DELETE_RESULT"
                    and event["result"] in {"HTTP_OTHER", "TRANSPORT_UNKNOWN"}))
               and timestamp(event["at_utc"]) >= start for event in reaper_events):
            window_ok = False
    ambiguous = (local["ownership_ambiguous"] or reaper["ownership_ambiguous"]
                 or any(event["kind"] == "OWNERSHIP_CONFLICT" for event in local_events + reaper_events))
    owned_ids = set(local_pods) | set(reaper_pods)
    known_ok = not ambiguous and all(
        pods[pid]["cleanup_confidence"] == "CONFIRMED"
        for pid in owned_ids for pods in (local_pods, reaper_pods) if pid in pods)
    operational = (known_ok and window_ok and local["journal_ok"] and reaper["journal_ok"]
                   and local["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED"
                   and reaper["status"] == "REAPER_CLEANUP_CONFIRMED")
    return {"run_id": local["run_id"],
            "known_owned_cleanup_status": "KNOWN_OWNED_CLEANUP_CONFIRMED" if known_ok else "KNOWN_OWNED_CLEANUP_UNRESOLVED",
            "reconciliation_window_status": "RECONCILIATION_COMPLETE" if window_ok else "RECONCILIATION_PENDING",
            "operational_cleanup_status": "OPERATIONAL_CLEANUP_CONFIRMED" if operational else "OPERATIONAL_CLEANUP_UNRESOLVED",
            "local_cleanup_status": local["cleanup_status"], "reaper_status": reaper["status"]}