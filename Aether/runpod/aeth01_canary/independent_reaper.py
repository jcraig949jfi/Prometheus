"""B3 independent cleanup-only reaper (Astra Closure Review 02, section 6).

Deployable on a host/process/scheduler that does NOT depend on the AGE
launch controller's process, local filesystem, power, network session, or
artifact proxy. This module intentionally has no import dependency on
age_controller.py (independence at the code level, not just at runtime),
and its provider wrapper (ReaperProvider) never exposes a create-pod
operation: this reaper cannot allocate compute, only find and delete it.

CLI (paths only; never pass credentials as arguments):
  arm    --manifest MANIFEST_JSON --out-ack ACK_JSON --scheduler-id ID
  sweep  --manifest MANIFEST_JSON --out-evidence EVIDENCE_JSON
         [--ack ACK_JSON] [--rounds N] [--poll-seconds S]

`arm` durably records this reaper's HMAC-bound acknowledgement of an exact
plan's reaper_manifest.json (written by age_controller.create_plan()). The
AGE controller's run() refuses the one allowed POST unless a matching
reaper_ack.json exists -- see age_controller._require_reaper_armed(). This
is stronger than an operator's Boolean attestation: it is a file this
process produced, HMAC-keyed with a secret the controller never logs.

`sweep` performs one bounded scan/delete/reconcile pass and is meant to be
invoked REPEATEDLY (by an external scheduler: cron, systemd timer, a
different host's job queue) from at/after the plan's cutoff until the
manifest's reconciliation_horizon_seconds has elapsed. Evidence accumulates
across invocations in EVIDENCE_JSON (first_fired_at_utc, total scan/delete
attempts, per-pod facts) so that "REAPER_CLEANUP_CONFIRMED with zero owned
pods ever found" can only be reached after the full announced horizon has
elapsed with consistently empty, fully-successful scans -- not from a
handful of scans in one process lifetime (the review's explicit objection
to manufacturing certainty from "three potentially stale scans").

Live credentials: RUNPOD_API_KEY (list/get/delete only -- see ReaperProvider)
and AGE_REAPER_SHARED_SECRET (`arm` only). Neither is ever journaled; the
evidence file records only the closed, secret-safe vocabulary below.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time as _time


HERE = Path(__file__).resolve().parent
MANIFEST_KEYS = frozenset({
    "version", "run_id", "run_name", "image", "creation_intent_id", "cutoff_utc",
    "cutoff_reference", "reconciliation_horizon_seconds", "hourly_rate_usd", "canary_budget_usd",
})
ACK_KEYS = frozenset({"version", "manifest_sha256", "armed", "scheduler_id",
                      "cutoff_utc", "acknowledged_at_utc", "manifest_hmac_sha256"})
_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
DEFAULT_ROUNDS = 6
DEFAULT_POLL_SECONDS = 10
# B1-equivalent evidence bar, reimplemented independently of age_controller.py.
ABSENCE_SCANS_REQUIRED = 2
# How many fully-successful, empty scans (accumulated across invocations,
# spanning the full announced horizon) are required before "nothing was ever
# owned" may be treated as CONFIRMED rather than left pending/unresolved.
EMPTY_HORIZON_SCANS_REQUIRED = 6
_DELETE_RESULTS = frozenset({"NONE", "ACK_204", "NOT_FOUND_404", "HTTP_OTHER", "TRANSPORT_UNKNOWN"})
_VISIBILITY = frozenset({"UNKNOWN", "NOT_VISIBLE", "VISIBLE"})
_CONFIDENCE = frozenset({"UNRESOLVED", "CONFIRMED"})


class ReaperError(Exception):
    """Fixed codes only; never include untrusted input or exceptions."""


def _require(condition, code):
    if not condition:
        raise ReaperError(code)


def _utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def _timestamp(value):
    try:
        _require(isinstance(value, str), "INVALID_UTC")
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        _require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds() == 0, "INVALID_UTC")
        return stamp.timestamp()
    except (ValueError, OverflowError):
        raise ReaperError("INVALID_UTC") from None


def _read(path, limit=1024 * 1024):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(limit + 1)
        _require(len(raw) <= limit, "FILE_TOO_LARGE")
        return raw
    except OSError:
        raise ReaperError("FILE_READ_FAILED") from None


def _decode(raw):
    try:
        value = json.loads(raw)
        _require(isinstance(value, dict), "INVALID_JSON")
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise ReaperError("INVALID_JSON") from None


def _encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _replace_with_retry(source, destination):
    delay = 0.01
    for attempt in range(5):
        try:
            os.replace(source, destination)
            return
        except OSError:
            if attempt == 4:
                raise
            _time.sleep(delay)
            delay *= 2


def atomic_write(path, raw):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".reaper-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_retry(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _text(value, limit=256):
    return (isinstance(value, str) and 0 < len(value) <= limit
            and all(32 <= ord(c) <= 126 for c in value) and bool(value.strip()))


def _secret_valid(secret):
    return (isinstance(secret, str) and 32 <= len(secret) <= 4096
            and all(33 <= ord(c) <= 126 for c in secret))


def load_manifest(path):
    raw = _read(path)
    manifest = _decode(raw)
    try:
        _require(set(manifest) == MANIFEST_KEYS and manifest["version"] == 1, "INVALID_MANIFEST")
        for key in ("run_id", "run_name", "image", "creation_intent_id", "cutoff_reference"):
            _require(_text(manifest[key], limit=4096), "INVALID_MANIFEST")
        _timestamp(manifest["cutoff_utc"])
        _require(type(manifest["reconciliation_horizon_seconds"]) is int
                 and manifest["reconciliation_horizon_seconds"] > 0, "INVALID_MANIFEST")
        for key in ("hourly_rate_usd", "canary_budget_usd"):
            _require(type(manifest[key]) in (int, float) and manifest[key] > 0, "INVALID_MANIFEST")
    except (KeyError, TypeError):
        raise ReaperError("INVALID_MANIFEST") from None
    return manifest, raw


def arm(manifest_path, secret, scheduler_id, *, clock_time=None):
    """Produce this reaper's durable, HMAC-bound acknowledgement.

    This is the evidence age_controller.py's _require_reaper_armed() checks
    before allowing the controller's one paid POST -- a file THIS process
    produced, not a Boolean the operator merely typed into the approval JSON.
    """
    _require(_secret_valid(secret), "REAPER_SHARED_SECRET_REQUIRED")
    manifest, raw = load_manifest(manifest_path)
    _require(_text(scheduler_id), "INVALID_SCHEDULER_ID")
    now = clock_time() if clock_time is not None else _time.time()
    ack = {"version": 1, "manifest_sha256": _sha(raw), "armed": True,
           "scheduler_id": scheduler_id, "cutoff_utc": manifest["cutoff_utc"],
           "acknowledged_at_utc": _utc(now),
           "manifest_hmac_sha256": hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()}
    return manifest, ack


def _owned(pod, manifest):
    return (isinstance(pod, dict) and isinstance(pod.get("id"), str)
            and _ID.fullmatch(pod["id"]) is not None
            and pod.get("name") == manifest["run_name"]
            and pod.get("image") == manifest["image"]
            and isinstance(pod.get("env"), dict)
            and pod["env"].get("AETH01_RUN_ID") == manifest["run_id"])


class ReaperProvider:
    """Cleanup-only wrapper: deliberately never exposes create_pod.

    Wrap a runpod_api.RunPodAPI (or an offline test double exposing the same
    get_pod/list_pods/visit_pods/terminate_pod surface). Even though the
    wrapped client's class may itself define create_pod, this wrapper's own
    surface -- the only one independent_reaper.py code ever calls through --
    has no such method, so a review of this file alone shows no create path.
    """

    def __init__(self, api):
        self._api = api

    def get_pod(self, pod_id):
        return self._api.get_pod(pod_id)

    def visit_pods(self, visitor):
        visitor_fn = getattr(self._api, "visit_pods", None)
        if visitor_fn is not None:
            return visitor_fn(visitor)
        for pod in self._api.list_pods():
            visitor(pod)

    def terminate_pod(self, pod_id):
        return self._api.terminate_pod(pod_id)


def _new_pod_evidence():
    return {"delete_attempted": False, "delete_result": "NONE", "last_visibility": "UNKNOWN",
            "last_status": None, "positive_termination_observed": False,
            "absence_confirmations": 0, "cleanup_confidence": "UNRESOLVED"}


def _classify_transport_error(error):
    category = getattr(error, "category", None)
    status = getattr(error, "status", None)
    if category == "SCHEMA_INVALID":
        return "HTTP_OTHER", None
    if isinstance(status, int):
        return "HTTP_OTHER", status
    return "TRANSPORT_UNKNOWN", None


def new_evidence_state(manifest, manifest_digest):
    return {"version": 1, "run_id": manifest["run_id"], "manifest_sha256": manifest_digest,
            "first_fired_at_utc": None, "last_fired_at_utc": None, "total_rounds_run": 0,
            "empty_scan_streak": 0, "owned_ids": [], "pod_evidence": {},
            "ownership_ambiguous": False, "reconciled": False, "status": "REAPER_PENDING"}


def load_or_init_evidence(path, manifest, manifest_digest):
    if not Path(path).exists():
        return new_evidence_state(manifest, manifest_digest)
    state = _decode(_read(path))
    try:
        _require(state["run_id"] == manifest["run_id"]
                 and state["manifest_sha256"] == manifest_digest, "EVIDENCE_MANIFEST_MISMATCH")
    except (KeyError, TypeError):
        raise ReaperError("INVALID_EVIDENCE") from None
    return state


def _refresh_confidence(rec):
    confirmed = rec["positive_termination_observed"] or (
        rec["delete_result"] == "ACK_204" and rec["last_visibility"] != "VISIBLE"
        and rec["absence_confirmations"] >= ABSENCE_SCANS_REQUIRED)
    rec["cleanup_confidence"] = "CONFIRMED" if confirmed else "UNRESOLVED"


def sweep_once(manifest, state, provider):
    """One bounded scan-then-delete-then-recheck pass. Never retries CREATE
    (this module has no create path at all); never treats one empty scan as
    proof of absence (see EMPTY_HORIZON_SCANS_REQUIRED / owned-pod evidence
    bar in _refresh_confidence, mirroring age_controller.py's B1 repair).
    """
    seen = set()

    def observe(pod):
        if _owned(pod, manifest):
            pod_id = pod["id"]
            seen.add(pod_id)
            if pod_id not in state["owned_ids"]:
                state["owned_ids"].append(pod_id)
            rec = state["pod_evidence"].setdefault(pod_id, _new_pod_evidence())
            status = pod.get("status")
            rec["last_visibility"] = "VISIBLE"
            rec["last_status"] = status if isinstance(status, str) else None
            if status == "TERMINATED":
                rec["positive_termination_observed"] = True
            else:
                rec["absence_confirmations"] = 0
            _refresh_confidence(rec)
        elif isinstance(pod, dict):
            env = pod.get("env")
            if (pod.get("name") == manifest["run_name"]
                    or isinstance(env, dict) and env.get("AETH01_RUN_ID") == manifest["run_id"]):
                state["ownership_ambiguous"] = True
        if len(state["owned_ids"]) > 1:
            state["ownership_ambiguous"] = True

    scan_ok = True
    try:
        provider.visit_pods(observe)
    except Exception:
        scan_ok = False
    if scan_ok:
        state["reconciled"] = True
        if not state["owned_ids"]:
            state["empty_scan_streak"] += 1
        else:
            state["empty_scan_streak"] = 0
        for pod_id in list(state["owned_ids"]):
            if pod_id in seen:
                continue
            rec = state["pod_evidence"].setdefault(pod_id, _new_pod_evidence())
            if rec["delete_result"] == "ACK_204" and rec["last_visibility"] != "VISIBLE":
                rec["absence_confirmations"] += 1
            _refresh_confidence(rec)
    else:
        state["empty_scan_streak"] = 0

    for pod_id in list(state["owned_ids"]):
        rec = state["pod_evidence"][pod_id]
        if rec["cleanup_confidence"] == "CONFIRMED":
            continue
        rec["delete_attempted"] = True
        try:
            result = provider.terminate_pod(pod_id)
            result = result if result in ("ACK_204", "NOT_FOUND_404") else "ACK_204"
        except Exception as error:
            result, _ = _classify_transport_error(error)
        if rec["delete_result"] != "ACK_204":
            rec["delete_result"] = result
        try:
            pod = provider.get_pod(pod_id)
        except Exception:
            rec["last_visibility"] = "UNKNOWN"
        else:
            if pod is None:
                rec["last_visibility"] = "NOT_VISIBLE"
            elif _owned(pod, manifest) and pod.get("id") == pod_id:
                status = pod.get("status")
                rec["last_visibility"] = "VISIBLE"
                rec["last_status"] = status if isinstance(status, str) else None
                if status == "TERMINATED":
                    rec["positive_termination_observed"] = True
                else:
                    rec["absence_confirmations"] = 0
            else:
                rec["last_visibility"] = "VISIBLE"
                state["ownership_ambiguous"] = True
        _refresh_confidence(rec)
    return scan_ok


def _owned_confirmed(state):
    return bool(state["owned_ids"]) and all(
        rec["cleanup_confidence"] == "CONFIRMED" for rec in state["pod_evidence"].values())


def _horizon_elapsed(manifest, state, now):
    if state["first_fired_at_utc"] is None:
        return False
    horizon = manifest["reconciliation_horizon_seconds"]
    return now - _timestamp(state["first_fired_at_utc"]) >= horizon


def sweep(manifest, manifest_digest, provider, state, *, rounds=DEFAULT_ROUNDS,
          poll_seconds=DEFAULT_POLL_SECONDS, sleep=None, clock_time=None, ack=None):
    """Run up to `rounds` bounded passes, updating durable, cumulative
    evidence in `state` (see load_or_init_evidence). Intended to be invoked
    repeatedly by an external scheduler until the manifest's
    reconciliation_horizon_seconds has elapsed since the first firing.
    """
    sleep = sleep or _time.sleep
    clock_time = clock_time or _time.time
    now = clock_time()
    if state["first_fired_at_utc"] is None:
        state["first_fired_at_utc"] = _utc(now)
    state["last_fired_at_utc"] = _utc(now)
    for attempt in range(rounds):
        sweep_once(manifest, state, provider)
        state["total_rounds_run"] += 1
        if _owned_confirmed(state) and state["reconciled"]:
            break
        if attempt + 1 < rounds:
            sleep(poll_seconds)
    horizon_done = _horizon_elapsed(manifest, state, clock_time())
    if state["owned_ids"]:
        clean = (_owned_confirmed(state) and state["reconciled"]
                 and not state["ownership_ambiguous"])
    else:
        # Never manufacture certainty from a handful of empty scans (the
        # review's explicit objection): require BOTH the full announced
        # horizon to have elapsed AND a long, unbroken, fully-successful
        # empty-scan streak spanning it.
        clean = (state["reconciled"] and not state["ownership_ambiguous"]
                 and horizon_done and state["empty_scan_streak"] >= EMPTY_HORIZON_SCANS_REQUIRED)
    state["status"] = "REAPER_CLEANUP_CONFIRMED" if clean else (
        "REAPER_CLEANUP_UNRESOLVED" if horizon_done else "REAPER_PENDING")
    if ack is not None:
        state["ack_scheduler_id"] = ack.get("scheduler_id")
        state["ack_acknowledged_at_utc"] = ack.get("acknowledged_at_utc")
    state["scheduled_cutoff_utc"] = manifest["cutoff_utc"]
    return state


def _load_state_dict(directory_state):
    return directory_state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    arming = commands.add_parser("arm")
    arming.add_argument("--manifest", required=True)
    arming.add_argument("--out-ack", required=True)
    arming.add_argument("--scheduler-id", required=True)
    sweeping = commands.add_parser("sweep")
    sweeping.add_argument("--manifest", required=True)
    sweeping.add_argument("--out-evidence", required=True)
    sweeping.add_argument("--ack", default=None)
    sweeping.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    sweeping.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    args = parser.parse_args(argv)
    try:
        if args.command == "arm":
            secret = os.environ.get("AGE_REAPER_SHARED_SECRET", "")
            manifest, ack = arm(args.manifest, secret, args.scheduler_id)
            atomic_write(args.out_ack, _encode(ack))
            outcome = {"status": "ARMED", "run_id": manifest["run_id"],
                      "manifest_sha256": ack["manifest_sha256"]}
        else:
            manifest, manifest_raw = load_manifest(args.manifest)
            digest = _sha(manifest_raw)
            ack = None
            if args.ack:
                ack = _decode(_read(args.ack))
            try:
                from .runpod_api import RunPodAPI
            except ImportError:
                from runpod_api import RunPodAPI
            key = os.environ.get("RUNPOD_API_KEY", "")
            _require(bool(key), "RUNPOD_API_KEY_REQUIRED")
            provider = ReaperProvider(RunPodAPI())
            state = load_or_init_evidence(args.out_evidence, manifest, digest)
            state = sweep(manifest, digest, provider, state, rounds=args.rounds,
                          poll_seconds=args.poll_seconds, ack=ack)
            atomic_write(args.out_evidence, _encode(state))
            outcome = {"status": state["status"], "run_id": manifest["run_id"]}
    except (Exception, KeyboardInterrupt) as error:
        reason = str(error) if isinstance(error, ReaperError) else "REAPER_FAILED"
        print(json.dumps({"status": "REFUSED_OR_FAILED", "reason": reason}))
        return 2
    print(json.dumps(outcome, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
