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

`sweep` preserves per-pod histories across invocations, but NEVER credits
downtime toward reconciliation. An operational worker must sustain one
invocation for the entire manifest horizon, sampling at most 60 seconds
apart, after cutoff. The default six rounds are only a short cleanup pass.
The HMAC acknowledgement binds the manifest, not proof of scheduler health.

Live credentials: RUNPOD_API_KEY (list/get/delete only -- see ReaperProvider)
and AGE_REAPER_SHARED_SECRET (`arm` only). Neither is ever journaled; the
evidence file records only the closed, secret-safe vocabulary below.
"""

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
import hashlib
import hmac
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time as _time
import uuid


HERE = Path(__file__).resolve().parent
try:
    from . import cleanup_evidence as policy
except ImportError:
    _policy_spec = importlib.util.spec_from_file_location(
        "_aeth01_reaper_cleanup_evidence", HERE / "cleanup_evidence.py")
    policy = importlib.util.module_from_spec(_policy_spec)
    _policy_spec.loader.exec_module(policy)

MANIFEST_KEYS = frozenset({
    "version", "run_id", "run_name", "image", "creation_intent_id", "cutoff_utc",
    "cutoff_reference", "reconciliation_horizon_seconds", "hourly_rate_usd", "canary_budget_usd",
})
ACK_KEYS = frozenset({"version", "manifest_sha256", "armed", "scheduler_id",
                      "cutoff_utc", "acknowledged_at_utc", "manifest_hmac_sha256"})
_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
DEFAULT_ROUNDS = 6
DEFAULT_POLL_SECONDS = 10
MAX_ROUNDS = 10000
POLICY_VERSION = policy.POLICY_VERSION
ABSENCE_SCANS_REQUIRED = 2
EMPTY_HORIZON_SCANS_REQUIRED = 6


class ReaperError(Exception):
    """Fixed codes only; never include untrusted input or exceptions."""


def _require(condition, code):
    if not condition:
        raise ReaperError(code)


def _utc(seconds):
    return policy.utc(seconds)


def _timestamp(value):
    try:
        _require(isinstance(value, str), "INVALID_UTC")
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        _require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds() == 0, "INVALID_UTC")
        return stamp.timestamp()
    except (ValueError, OverflowError, OSError):
        raise ReaperError("INVALID_UTC") from None


def _read(path, limit=64 * 1024 * 1024):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(limit + 1)
        _require(len(raw) <= limit, "FILE_TOO_LARGE")
        return raw
    except OSError:
        raise ReaperError("FILE_READ_FAILED") from None


def _decode(raw):
    def unique_pairs(pairs):
        value = {}
        for key, item in pairs:
            _require(key not in value, "INVALID_JSON")
            value[key] = item
        return value

    def invalid_constant(value):
        raise ReaperError("INVALID_JSON")

    try:
        value = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=invalid_constant)
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
        if os.name != "nt":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _text(value, limit=256):
    return (isinstance(value, str) and 0 < len(value) <= limit
            and all(32 <= ord(c) <= 126 for c in value) and bool(value.strip()))


def _secret_valid(secret):
    return (isinstance(secret, str) and 32 <= len(secret) <= 4096
            and all(33 <= ord(c) <= 126 for c in secret))


def _validate_manifest(manifest):
    try:
        _require(isinstance(manifest, dict) and set(manifest) == MANIFEST_KEYS
                 and type(manifest["version"]) is int and manifest["version"] == 1,
                 "INVALID_MANIFEST")
        for key in ("run_id", "run_name", "image", "creation_intent_id", "cutoff_reference"):
            _require(_text(manifest[key], limit=4096), "INVALID_MANIFEST")
        _timestamp(manifest["cutoff_utc"])
        _require(type(manifest["reconciliation_horizon_seconds"]) is int
                 and manifest["reconciliation_horizon_seconds"] > 0, "INVALID_MANIFEST")
        for key in ("hourly_rate_usd", "canary_budget_usd"):
            _require(type(manifest[key]) in (int, float) and math.isfinite(manifest[key])
                     and manifest[key] > 0, "INVALID_MANIFEST")
    except (KeyError, TypeError):
        raise ReaperError("INVALID_MANIFEST") from None


def load_manifest(path):
    raw = _read(path)
    manifest = _decode(raw)
    _validate_manifest(manifest)
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
    return policy.new_pod()


def _classify_transport_error(error):
    category = getattr(error, "category", None)
    status = getattr(error, "status", None)
    if category == "SCHEMA_INVALID":
        return "HTTP_OTHER", None
    if isinstance(status, int):
        return "HTTP_OTHER", status
    return "TRANSPORT_UNKNOWN", None


def new_evidence_state(manifest, manifest_digest):
    _validate_manifest(manifest)
    _require(isinstance(manifest_digest, str)
             and re.fullmatch(r"[0-9a-f]{64}", manifest_digest), "INVALID_MANIFEST_DIGEST")
    _require(manifest_digest == _sha(_encode(manifest)), "EVIDENCE_MANIFEST_MISMATCH")
    return {"version": 2, "policy_version": POLICY_VERSION,
            "manifest": deepcopy(manifest), "run_id": manifest["run_id"],
            "manifest_sha256": manifest_digest, "journal_ok": True,
            "first_fired_at_utc": None, "last_fired_at_utc": None, "total_rounds_run": 0,
            "empty_scan_streak": 0, "owned_ids": [], "pod_evidence": {},
            "ownership_ambiguous": False, "reconciled": False, "status": "REAPER_PENDING",
            "known_owned_cleanup_status": "KNOWN_OWNED_CLEANUP_CONFIRMED",
            "reconciliation_window_status": "RECONCILIATION_PENDING",
            "scheduled_cutoff_utc": manifest["cutoff_utc"],
            "window": policy.new_window(uuid.uuid4().hex)}


def _validate_window(window, manifest, now):
    # window_complete validates ALL current and archived samples and derived
    # fields, even when the window is incomplete. Bind their cutoffs as well.
    policy.window_complete(window, manifest["reconciliation_horizon_seconds"], now=now)
    groups = [window["samples"]] + [event["samples"] for event in window["history"]]
    cutoff = _timestamp(manifest["cutoff_utc"])
    for samples in groups:
        for sample in samples:
            _require(_timestamp(sample["cutoff_utc"]) == cutoff, "EVIDENCE_MANIFEST_MISMATCH")


def _validate_evidence(state, manifest, manifest_digest, *, now=None):
    """Reject legacy/cached/foreign evidence rather than promoting labels."""
    now = _time.time() if now is None else now
    _require(type(now) in (int, float) and math.isfinite(now), "INVALID_UTC")
    template = new_evidence_state(manifest, manifest_digest)
    try:
        _require(isinstance(state, dict), "INVALID_EVIDENCE")
        _require(state.get("version") != 1, "LEGACY_EVIDENCE_UNSUPPORTED")
        optional = {"ack_scheduler_id", "ack_acknowledged_at_utc"}
        _require(set(state) in (set(template), set(template) | optional), "INVALID_EVIDENCE")
        _require(type(state["version"]) is int and state["version"] == 2
                 and type(state["policy_version"]) is int
                 and state["policy_version"] == POLICY_VERSION, "INVALID_EVIDENCE_VERSION")
        _validate_manifest(state["manifest"])
        _require(state["run_id"] == manifest["run_id"]
                 and state["manifest_sha256"] == manifest_digest
                 and state["manifest"] == manifest
                 and _sha(_encode(state["manifest"])) == manifest_digest
                 and state["scheduled_cutoff_utc"] == manifest["cutoff_utc"],
                 "EVIDENCE_MANIFEST_MISMATCH")
        for key in ("journal_ok", "ownership_ambiguous", "reconciled"):
            _require(type(state[key]) is bool, "INVALID_EVIDENCE")
        for key in ("total_rounds_run", "empty_scan_streak"):
            _require(type(state[key]) is int and state[key] >= 0, "INVALID_EVIDENCE")
        times = [state[key] for key in ("first_fired_at_utc", "last_fired_at_utc")]
        _require(all(t is None for t in times) or all(t is not None for t in times),
                 "INVALID_EVIDENCE")
        if times[0] is not None:
            _require(_timestamp(times[0]) <= _timestamp(times[1]) <= now, "INVALID_EVIDENCE_TIME")
        if "ack_scheduler_id" in state:
            _require(_text(state["ack_scheduler_id"]), "INVALID_EVIDENCE")
            _require(_timestamp(state["ack_acknowledged_at_utc"]) <= now, "INVALID_EVIDENCE_TIME")
        ids = state["owned_ids"]
        _require(isinstance(ids, list) and all(isinstance(pid, str) and _ID.fullmatch(pid)
                                             for pid in ids), "INVALID_EVIDENCE")
        _require(len(ids) == len(set(ids)) and isinstance(state["pod_evidence"], dict)
                 and set(ids) == set(state["pod_evidence"]), "INVALID_EVIDENCE")
        for rec in state["pod_evidence"].values():
            policy.validate_pod(rec, now=now)
            _require(rec["history"] and rec["history"][0]["kind"] == "OBSERVE", "INVALID_EVIDENCE")
            _require(state["ownership_ambiguous"] or not any(
                event["kind"] == "OWNERSHIP_CONFLICT" for event in rec["history"]),
                "INVALID_EVIDENCE")
        _validate_window(state["window"], manifest, now)
        _require(state["empty_scan_streak"] == state["window"]["scan_count"], "INVALID_EVIDENCE")
        samples = state["window"]["samples"]
        archived = sum(len(event["samples"]) for event in state["window"]["history"])
        _require(len(samples) + archived <= state["total_rounds_run"], "INVALID_EVIDENCE")
        if times[0] is None:
            _require(not ids and not state["total_rounds_run"] and not samples
                     and not state["window"]["history"] and not state["reconciled"], "INVALID_EVIDENCE")
        expected = deepcopy(state)
        # Freshness is a reporting concern; an otherwise valid old snapshot
        # can be loaded for cleanup, but every sweep discards its window credit.
        latest = state["window"]["latest_utc"]
        _refresh_status(manifest, expected, _timestamp(latest) if latest else now)
        for key in ("status", "known_owned_cleanup_status", "reconciliation_window_status"):
            _require(state[key] == expected[key], "INVALID_EVIDENCE_STATUS")
    except (KeyError, TypeError, ValueError, policy.EvidenceError):
        raise ReaperError("INVALID_EVIDENCE") from None
    return state


def load_or_init_evidence(path, manifest, manifest_digest, *, now=None):
    if not Path(path).exists():
        return new_evidence_state(manifest, manifest_digest)
    state = _decode(_read(path))
    return _validate_evidence(state, manifest, manifest_digest, now=now)


def _owned_confirmed(state, now=None):
    return not state["ownership_ambiguous"] and all(
        policy.validate_pod(state["pod_evidence"][pid], now=now)["cleanup_confidence"] == "CONFIRMED"
        for pid in state["owned_ids"])


def _refresh_status(manifest, state, now):
    try:
        known = state["journal_ok"] and _owned_confirmed(state, now=now)
    except policy.EvidenceError:
        known = False
    try:
        complete = (state["journal_ok"] and state["reconciled"]
                    and not state["ownership_ambiguous"]
                    and policy.window_complete(state["window"],
                                               manifest["reconciliation_horizon_seconds"], now=now))
    except policy.EvidenceError:
        # In-process backwards clocks may leave archived observations ahead
        # of now. Preserve those observations, fail closed, and keep deleting.
        complete = False
    state["empty_scan_streak"] = state["window"]["scan_count"]
    state["known_owned_cleanup_status"] = ("KNOWN_OWNED_CLEANUP_CONFIRMED" if known
                                            else "KNOWN_OWNED_CLEANUP_UNRESOLVED")
    state["reconciliation_window_status"] = ("RECONCILIATION_COMPLETE" if complete
                                              else "RECONCILIATION_PENDING")
    state["status"] = ("REAPER_CLEANUP_CONFIRMED" if known and complete else
                       "REAPER_PENDING" if known else "REAPER_CLEANUP_UNRESOLVED")


def sweep_once(manifest, state, provider, *, clock_time=None, monotonic=None, persist=None):
    """Keep exact-owned positives even if a later inventory page fails."""
    clock_time = clock_time or _time.time
    monotonic = monotonic or _time.monotonic
    persist = persist or (lambda: None)
    seen = set()
    conflicts = set()
    live_seen = set()

    def event(pod_id, kind, **kwargs):
        try:
            policy.append_pod(state["pod_evidence"][pod_id], kind, _utc(clock_time()), **kwargs)
        except Exception:
            # Never invent an observation timestamp or make a broken clock a
            # DELETE gate. This invocation's evidence is unusable for success.
            state["journal_ok"] = False

    def interrupt(reason):
        state["reconciled"] = False
        try:
            at = _utc(clock_time())
        except Exception:
            state["journal_ok"] = False
            at = None
        policy.reset_window(state["window"], reason, at)

    def observe(pod):
        if _owned(pod, manifest):
            pod_id = pod["id"]
            seen.add(pod_id)
            if pod.get("status") != "TERMINATED":
                live_seen.add(pod_id)
            if pod_id not in state["owned_ids"]:
                state["owned_ids"].append(pod_id)
            state["pod_evidence"].setdefault(pod_id, _new_pod_evidence())
            event(pod_id, "OBSERVE", status=pod.get("status"))
            interrupt("OWNED_SEEN")
        elif isinstance(pod, dict) and pod.get("id") in state["owned_ids"]:
            pod_id = pod["id"]
            conflicts.add(pod_id)
            state["ownership_ambiguous"] = True
            event(pod_id, "OWNERSHIP_CONFLICT")
            interrupt("OWNERSHIP_CONFLICT")
        # Unrelated and partial matches do not belong to this run.
        persist()

    scan_ok = True
    try:
        provider.visit_pods(observe)
    except Exception:
        scan_ok = False
    state["reconciled"] = scan_ok and not conflicts
    state["total_rounds_run"] += 1
    for pod_id in state["owned_ids"]:
        if not scan_ok:
            event(pod_id, "SCAN_FAILED")
        elif pod_id not in seen and pod_id not in conflicts:
            event(pod_id, "ABSENT_SCAN")
    try:
        policy.observe_window(state["window"], _utc(clock_time()), monotonic(),
                              complete=scan_ok and not conflicts, owned_seen=bool(seen),
                              cutoff=manifest["cutoff_utc"])
    except Exception:
        state["journal_ok"] = False
        interrupt("CLOCK_INVALID")
    persist()

    for pod_id in list(state["owned_ids"]):
        rec = state["pod_evidence"][pod_id]
        last_binding = next((entry["kind"] for entry in reversed(rec["history"])
                             if entry["kind"] in ("OBSERVE", "OWNERSHIP_CONFLICT")), None)
        if (pod_id in conflicts or (last_binding != "OBSERVE" and pod_id not in seen)
                or (policy.pod_confirmed(rec) and pod_id not in live_seen)):
            continue
        # Do not erase corroborating absence progress by retrying a current ACK.
        if rec["delete_result"] != "ACK_204" or pod_id in live_seen:
            event(pod_id, "DELETE_ATTEMPT")
            persist()
            try:
                result = provider.terminate_pod(pod_id)
                if result not in ("ACK_204", "NOT_FOUND_404"):
                    result = "TRANSPORT_UNKNOWN"
            except Exception as error:
                result, _ = _classify_transport_error(error)
            event(pod_id, "DELETE_RESULT", result=result)
            if result in ("HTTP_OTHER", "TRANSPORT_UNKNOWN"):
                interrupt("PROVIDER_FAILED")
            persist()
        try:
            pod = provider.get_pod(pod_id)
        except Exception:
            event(pod_id, "UNKNOWN")
            interrupt("PROVIDER_FAILED")
        else:
            if pod is None:
                event(pod_id, "MISSING")
            elif _owned(pod, manifest) and pod.get("id") == pod_id:
                observe(pod)
            else:
                state["ownership_ambiguous"] = True
                event(pod_id, "OWNERSHIP_CONFLICT")
                interrupt("OWNERSHIP_CONFLICT")
        persist()
    return scan_ok


def _validate_sweep_options(rounds, poll_seconds):
    _require(type(rounds) is int and 1 <= rounds <= MAX_ROUNDS, "INVALID_ROUNDS")
    _require(type(poll_seconds) in (int, float) and math.isfinite(poll_seconds)
             and 0 < poll_seconds <= 60, "INVALID_POLL_SECONDS")


def sweep(manifest, manifest_digest, provider, state, *, rounds=DEFAULT_ROUNDS,
          poll_seconds=DEFAULT_POLL_SECONDS, sleep=None, clock_time=None, ack=None,
          monotonic=None, persist=None):
    """Mutate state, persist each observation, and return a detached report.

    Every invocation starts a new session; only this invocation's healthy
    scans can complete the horizon. Persistence failure is sticky and must
    not suppress best-effort deletes. The optional callback accepts state.
    """
    _validate_sweep_options(rounds, poll_seconds)
    sleep = sleep or _time.sleep
    clock_time = clock_time or _time.time
    monotonic = monotonic or _time.monotonic
    now = clock_time()
    _validate_evidence(state, manifest, manifest_digest, now=now)
    policy.reset_window(state["window"], "RESTART", _utc(now))
    state["window"]["session_id"] = uuid.uuid4().hex
    state["reconciled"] = False
    if state["first_fired_at_utc"] is None:
        state["first_fired_at_utc"] = _utc(now)
    state["last_fired_at_utc"] = _utc(now)
    if ack is not None:
        _require(isinstance(ack, dict) and _text(ack.get("scheduler_id")), "INVALID_ACK")
        _require(_timestamp(ack.get("acknowledged_at_utc")) <= now, "INVALID_ACK")
        state["ack_scheduler_id"] = ack["scheduler_id"]
        state["ack_acknowledged_at_utc"] = ack["acknowledged_at_utc"]

    def checkpoint():
        try:
            current = clock_time()
            _utc(current)  # Reject malformed/nonfinite clock even with no pods.
        except Exception:
            state["journal_ok"] = False
            current = now  # Used only with success disabled, never as an event time.
        _refresh_status(manifest, state, current)
        if persist is not None:
            try:
                persist(deepcopy(state))
            except Exception:
                state["journal_ok"] = False
                _refresh_status(manifest, state, current)

    checkpoint()
    for attempt in range(rounds):
        sweep_once(manifest, state, provider, clock_time=clock_time,
                   monotonic=monotonic, persist=checkpoint)
        checkpoint()
        if state["status"] == "REAPER_CLEANUP_CONFIRMED":
            break
        if attempt + 1 < rounds:
            sleep(poll_seconds)
    checkpoint()
    return deepcopy(state)


@contextmanager
def evidence_lock(path):
    """Nonblocking OS advisory lock; a crash releases it, not its inode."""
    stream = None
    locked = False
    try:
        stream = Path(str(Path(path).resolve()) + ".lock").open("a+b")
        if os.name == "nt":
            import msvcrt
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
    except OSError:
        if stream is not None:
            stream.close()
        raise ReaperError("EVIDENCE_LOCK_UNAVAILABLE") from None
    try:
        yield
    finally:
        try:
            if locked:
                if os.name == "nt":
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        finally:
            stream.close()


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
            _validate_sweep_options(args.rounds, args.poll_seconds)
            manifest, manifest_raw = load_manifest(args.manifest)
            digest = _sha(manifest_raw)
            ack = None
            if args.ack:
                ack = _decode(_read(args.ack))
            with evidence_lock(args.out_evidence):
                state = load_or_init_evidence(args.out_evidence, manifest, digest)
                try:
                    from .runpod_api import RunPodAPI
                except ImportError:
                    from runpod_api import RunPodAPI
                _require(bool(os.environ.get("RUNPOD_API_KEY", "")), "RUNPOD_API_KEY_REQUIRED")
                provider = ReaperProvider(RunPodAPI())
                state = sweep(manifest, digest, provider, state, rounds=args.rounds,
                              poll_seconds=args.poll_seconds, ack=ack,
                              persist=lambda snapshot: atomic_write(args.out_evidence, _encode(snapshot)))
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
