"""Conservative, stdlib-only AGE controller. Import and plan never read credentials.

CLI (paths only; never pass credentials as arguments):
  plan --config CONFIG --run-dir FRESH_DIRECTORY
  run --run-dir DIRECTORY --approval APPROVAL --execute-paid-run
  recover --run-dir DIRECTORY

Config has exactly CONFIG_KEYS below. Prices are conservative *all-in* USD/hour
estimates, not a provider billing guarantee. The immutable image must run the
bundled pod_service.py. Source hashes are taken beside this module, without
importing the scientific code. Approval has exactly APPROVAL_KEYS; its nested
independent_billing_cutoff contains attested=true, deadline_utc, reference, which
must match the config. Approval expires at launch, not during cleanup.

Live credentials: RUNPOD_API_KEY, AGE_ARTIFACT_TOKEN, and AGE_REAPER_SHARED_SECRET
only. Generate each independently with a cryptographic RNG (>=32 printable
non-whitespace characters). AGE_REAPER_SHARED_SECRET is never forwarded to the
provider or the pod; it only HMACs the local reaper_manifest.json/reaper_ack.json
handoff (see independent_reaper.py) and is never journaled. Inject provider,
artifacts, token, reaper_secret, and clock for offline operation; injected
operation reads no env.

B3 pre-create handoff: create_plan() also writes reaper_manifest.json beside
plan.json. Before `run` may POST, an independent reaper process must have
durably received that manifest and written reaper_ack.json (HMAC-bound with
AGE_REAPER_SHARED_SECRET) back into the run directory; run() refuses to POST
otherwise (REAPER_NOT_ARMED). This is evidence of an armed, acknowledging
reaper, not proof it is running on genuinely separate infrastructure -- that
remains an operational fact to verify out of band.

The quoted lifetime uses <=half the canary budget. An independently enforced,
operator-attested absolute cutoff must fall inside the full quoted budget window.
There is NO verified provider maxCost/expiry fuse. Process timeout does NOT stop
billing. Clock checks and transport timeouts cannot preempt a blocked OS/provider;
the independent cutoff and operator follow-up remain essential residual risks.
State/plan are atomic fsynced snapshots (directory fsync on POSIX); keep the run
directory on a durable local filesystem supporting advisory locks and rename.
Never edit/copy/reuse it to launch another run. Cleanup is bounded best effort,
including after expiry, and never depends on being able to write another journal.
"""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import hmac
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import signal
import tempfile
import time as _time
import uuid


HERE = Path(__file__).resolve().parent
if __package__:
    from . import cleanup_evidence as policy
else:
    _policy_spec = importlib.util.spec_from_file_location(
        "_age_cleanup_evidence", HERE / "cleanup_evidence.py")
    policy = importlib.util.module_from_spec(_policy_spec)
    _policy_spec.loader.exec_module(policy)

SOURCES = ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py")
CONFIG_KEYS = frozenset({
    "image", "gpu_id", "cloud", "hourly_rate_usd", "canary_budget_usd",
    "remaining_budget_usd", "max_lifetime_seconds", "canary_timeout_seconds",
    "independent_cutoff_deadline_utc", "independent_cutoff_reference",
})
APPROVAL_KEYS = frozenset({
    "approved", "run_id", "plan_sha256", "expires_at_utc", "independent_billing_cutoff",
})
RETRIEVAL_SECONDS = 60
CLEANUP_SECONDS = 120
POLL_SECONDS = 2
CLEANUP_ROUNDS = 3
# B1: a pod's cleanup evidence is CONFIRMED only from a positive TERMINATED
# observation, or from an acknowledged DELETE plus this many independent,
# fully successful inventory reconciliation scans (run AFTER the DELETE
# attempt) that do not observe the pod. A single ambiguous 404 is never
# enough; see ASTRA_CLOSURE_REVIEW_02.md section 4.
POST_DELETE_ABSENCE_SCANS_REQUIRED = 2
# B3: the reconciliation obligation handed to the independent reaper extends
# this far past the controller's own bounded run; it is a durable obligation,
# not a controller-verified guarantee.
RECONCILIATION_HORIZON_SECONDS = 3600
RISK = ("No verified provider billing fuse; timeout does not stop billing. "
        "Independent cutoff is operator-attested, not provider-verified. "
        "LOCAL_CLEANUP_CONFIRMED reflects this controller's own bounded evidence "
        "only; operational cleanup additionally requires the independent "
        "reaper's corroborating evidence (see independent_reaper.py).")
_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
_DIGEST = re.compile(r"[0-9a-f]{64}")
_IMAGE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/:+-]*@sha256:[0-9a-f]{64}")

# Closed provider-status vocabulary: unknown positive visibility is still live,
# but arbitrary provider text must never reach evidence or diagnostics.
_POD_STATUSES = frozenset({"CREATED", "PENDING", "PROVISIONING", "STARTING", "RUNNING",
                          "STOPPING", "STOPPED", "EXITED", "ERROR", "TERMINATED", "UNKNOWN"})
# B4: closed diagnostic vocabulary. Secret-safe: only allowlisted fields ever
# reach the journal (stage/outcome/status/pod-status/elapsed/attempt).
_DIAG_STAGES = frozenset({"AUTH_PREFLIGHT", "CREATE", "GET_STATUS", "LIST_INVENTORY",
                          "ARTIFACT_RESULT", "ARTIFACT_RECEIPT", "ARTIFACT_LOG",
                          "DELETE", "RECONCILE"})
_DIAG_OUTCOMES = frozenset({"SUCCESS", "MISSING", "ACK_204", "NOT_FOUND_404", "HTTP_OTHER",
                            "TRANSPORT_UNKNOWN", "SCHEMA_INVALID", "POD_ERROR", "POD_EXITED"})
_DIAGNOSTICS_LIMIT = 200
REAPER_ACK_KEYS = frozenset({"version", "manifest_sha256", "armed", "scheduler_id",
                             "cutoff_utc", "acknowledged_at_utc", "manifest_hmac_sha256"})


def _new_pod_evidence():
    return policy.new_pod()


def _pod_status(pod):
    status = pod.get("status")
    return status if isinstance(status, str) and status in _POD_STATUSES else None


def _classify_transport_error(error):
    """Coarse, secret-safe classification of a transport/runpod_api exception."""
    category = getattr(error, "category", None)
    status = getattr(error, "status", None)
    if category == "SCHEMA_INVALID":
        return "SCHEMA_INVALID", None
    if isinstance(status, int):
        return "HTTP_OTHER", status
    return "TRANSPORT_UNKNOWN", None


class ControllerError(Exception):
    """Messages are fixed codes only; never include untrusted input or exceptions."""


class Clock:
    time = staticmethod(_time.time)
    monotonic = staticmethod(_time.monotonic)
    sleep = staticmethod(_time.sleep)


def _require(condition, code):
    if not condition:
        raise ControllerError(code)


def _number(value, positive=True):
    try:
        return (type(value) in (int, float) and math.isfinite(value)
                and (value > 0 if positive else value >= 0))
    except OverflowError:
        return False


def _text(value, limit=256):
    return (isinstance(value, str) and 0 < len(value) <= limit
            and all(32 <= ord(c) <= 126 for c in value) and bool(value.strip()))


def _utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def _timestamp(value):
    try:
        _require(isinstance(value, str), "INVALID_UTC")
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        _require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds() == 0,
                 "INVALID_UTC")
        return stamp.timestamp()
    except (ValueError, OverflowError):
        raise ControllerError("INVALID_UTC") from None


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "INVALID_JSON")
        result[key] = value
    return result


def _constant(_):
    raise ControllerError("INVALID_JSON")


def _decode(raw):
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
        _require(isinstance(value, dict), "INVALID_JSON")
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise ControllerError("INVALID_JSON") from None


def _encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _read(path, limit=1024 * 1024):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(limit + 1)
        _require(len(raw) <= limit, "FILE_TOO_LARGE")
        return raw
    except OSError:
        raise ControllerError("FILE_READ_FAILED") from None


def _sync_directory(path):
    if os.name != "nt":
        directory_fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)


def _replace_with_retry(source, destination):
    # An external process (AV/indexer) can transiently deny replacing a
    # just-written file on some platforms; a few short bounded retries
    # absorb that without masking a genuine, persistent failure. This
    # governs only local I/O timing, never a billing/evidence decision.
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
    """Never truncate the previous snapshot; fsync before and after rename."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".age-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        _replace_with_retry(temporary, path)
        _sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class RunLock:
    """Persistent lock inode; kernel releases the lock after process death."""

    def __init__(self, directory):
        self.path = Path(directory) / "controller.lock"
        self.stream = None

    def __enter__(self):
        try:
            self.stream = self.path.open("a+b")
            if self.stream.seek(0, os.SEEK_END) == 0:
                self.stream.write(b"\0")
                self.stream.flush()
                os.fsync(self.stream.fileno())
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            if self.stream is not None:
                self.stream.close()
            raise ControllerError("RUN_LOCKED_OR_UNAVAILABLE") from None
        return self

    def __exit__(self, *_):
        # Closing is sufficient on both platforms; do not unlink the lock file.
        self.stream.close()


def validate_config(config, created_at):
    _require(isinstance(config, dict) and set(config) == CONFIG_KEYS, "INVALID_CONFIG_KEYS")
    _require(isinstance(config["image"], str) and _IMAGE.fullmatch(config["image"]),
             "IMMUTABLE_IMAGE_REQUIRED")
    _require(_text(config["gpu_id"]) and config["cloud"] in ("COMMUNITY", "SECURE"),
             "INVALID_HARDWARE")
    for key in ("hourly_rate_usd", "canary_budget_usd", "remaining_budget_usd"):
        _require(_number(config[key]), "INVALID_BUDGET")
    budget = config["canary_budget_usd"]
    rate = config["hourly_rate_usd"]
    _require(budget <= 3 and budget <= config["remaining_budget_usd"] <= 19.93,
             "INVALID_BUDGET")
    lifetime = config["max_lifetime_seconds"]
    timeout = config["canary_timeout_seconds"]
    _require(type(lifetime) is int and 1 <= lifetime <= 900
             and type(timeout) is int and 1 <= timeout <= 600, "INVALID_DURATION")
    boot = lifetime - timeout - RETRIEVAL_SECONDS - CLEANUP_SECONDS
    _require(boot >= 30, "INSUFFICIENT_PHASE_RESERVES")
    _require(rate * lifetime / 3600 <= budget / 2, "QUOTE_EXCEEDS_HALF_BUDGET")
    cutoff = _timestamp(config["independent_cutoff_deadline_utc"])
    budget_window = budget / rate * 3600
    _require(math.isfinite(budget_window) and created_at + lifetime < cutoff
             <= created_at + budget_window, "INVALID_CUTOFF_WINDOW")
    _require(_text(config["independent_cutoff_reference"]), "CUTOFF_REFERENCE_REQUIRED")
    return {"boot_pull_seconds": boot, "canary_seconds": timeout,
            "retrieval_seconds": RETRIEVAL_SECONDS, "cleanup_seconds": CLEANUP_SECONDS}


def _plan_document(config, created_at, run_id, source_hashes):
    phases = validate_config(config, created_at)
    return {"version": 1, "run_id": run_id, "run_name": "aeth01-age-" + run_id,
            "created_at_utc": _utc(created_at), "config": config,
            "source_hashes": source_hashes, "phases": phases,
            "quoted_lifetime_cost_usd": config["hourly_rate_usd"]
            * config["max_lifetime_seconds"] / 3600, "billing_risk": RISK}


def reaper_manifest_document(plan):
    """B3 pre-create handoff: the durable, bounded manifest the independent
    reaper must acknowledge (arm) before the controller may POST. Pure
    function of the plan; carries no credentials.
    """
    c = plan["config"]
    return {"version": 1, "run_id": plan["run_id"], "run_name": plan["run_name"],
            "image": c["image"], "creation_intent_id": plan["run_id"],
            "cutoff_utc": c["independent_cutoff_deadline_utc"],
            "cutoff_reference": c["independent_cutoff_reference"],
            "reconciliation_horizon_seconds": RECONCILIATION_HORIZON_SECONDS,
            "hourly_rate_usd": c["hourly_rate_usd"], "canary_budget_usd": c["canary_budget_usd"]}


def create_plan(config, run_dir, *, clock=None, source_dir=HERE):
    """No transports, imports of clients, env reads, or credential checks."""
    clock = clock or Clock()
    source_hashes = {name: _sha(_read(Path(source_dir) / name, 4 * 1024 * 1024))
                     for name in SOURCES}
    plan = _plan_document(config, clock.time(), str(uuid.uuid4()), source_hashes)
    manifest_raw = _encode(reaper_manifest_document(plan))
    directory = Path(run_dir)
    try:
        directory.mkdir(mode=0o700, exist_ok=False)
        raw = _encode(plan)
        atomic_write(directory / "plan.json", raw)
        # Durable pre-create handoff: written before any approval/launch step
        # exists, so an independent reaper can receive and arm it early.
        atomic_write(directory / "reaper_manifest.json", manifest_raw)
        _sync_directory(directory.parent)
    except OSError:
        raise ControllerError("FRESH_PLAN_WRITE_FAILED") from None
    return {"run_id": plan["run_id"], "plan_sha256": _sha(raw),
            "reaper_manifest_sha256": _sha(manifest_raw), "billing_risk": RISK}


def _reaper_secret_valid(secret):
    return (isinstance(secret, str) and 32 <= len(secret) <= 4096
            and all(33 <= ord(c) <= 126 for c in secret))


def _require_reaper_armed(directory, plan, secret):
    """B3: refuse the paid create unless a durably-received, HMAC-bound
    acknowledgement from the independent reaper exists and matches this
    exact plan. This is stronger than an operator's Boolean attestation:
    it requires a file the reaper itself produced, keyed with a secret the
    controller never writes to disk or logs (see independent_reaper.py).
    """
    _require(_reaper_secret_valid(secret), "REAPER_SHARED_SECRET_REQUIRED")
    manifest_raw = _read(directory / "reaper_manifest.json")
    _require(_decode(manifest_raw) == reaper_manifest_document(plan), "INVALID_REAPER_MANIFEST")
    manifest_digest = _sha(manifest_raw)
    ack = _decode(_read(directory / "reaper_ack.json"))
    try:
        _require(isinstance(ack, dict) and set(ack) == REAPER_ACK_KEYS, "REAPER_NOT_ARMED")
        _require(ack["version"] == 1 and ack["armed"] is True, "REAPER_NOT_ARMED")
        _require(ack["manifest_sha256"] == manifest_digest, "REAPER_NOT_ARMED")
        _require(ack["cutoff_utc"] == plan["config"]["independent_cutoff_deadline_utc"],
                 "REAPER_NOT_ARMED")
        _require(_text(ack["scheduler_id"]), "REAPER_NOT_ARMED")
        _timestamp(ack["acknowledged_at_utc"])
        expected = hmac.new(secret.encode("utf-8"), manifest_raw, hashlib.sha256).hexdigest()
        _require(isinstance(ack["manifest_hmac_sha256"], str)
                 and hmac.compare_digest(ack["manifest_hmac_sha256"], expected), "REAPER_NOT_ARMED")
    except (KeyError, TypeError):
        raise ControllerError("REAPER_NOT_ARMED") from None


def _load_plan(directory):
    raw = _read(Path(directory) / "plan.json")
    plan = _decode(raw)
    try:
        run_id = plan["run_id"]
        _require(str(uuid.UUID(run_id)) == run_id, "INVALID_PLAN")
        hashes = plan["source_hashes"]
        _require(isinstance(hashes, dict) and set(hashes) == set(SOURCES)
                 and all(isinstance(h, str) and _DIGEST.fullmatch(h) for h in hashes.values()),
                 "INVALID_PLAN")
        expected = _plan_document(plan["config"], _timestamp(plan["created_at_utc"]),
                                  run_id, hashes)
        _require(plan == expected and type(plan["version"]) is int, "INVALID_PLAN")
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ControllerError("INVALID_PLAN") from None
    return plan, _sha(raw)


def validate_approval(approval, plan, digest, now):
    _require(isinstance(approval, dict) and set(approval) == APPROVAL_KEYS,
             "INVALID_APPROVAL")
    _require(approval["approved"] is True and approval["run_id"] == plan["run_id"]
             and approval["plan_sha256"] == digest, "APPROVAL_BINDING_FAILED")
    config = plan["config"]
    attestation = approval["independent_billing_cutoff"]
    _require(isinstance(attestation, dict)
             and set(attestation) == {"attested", "deadline_utc", "reference"}
             and attestation["attested"] is True
             and attestation["deadline_utc"] == config["independent_cutoff_deadline_utc"]
             and attestation["reference"] == config["independent_cutoff_reference"],
             "INDEPENDENT_CUTOFF_ATTESTATION_REQUIRED")
    cutoff = _timestamp(config["independent_cutoff_deadline_utc"])
    _require(_timestamp(plan["created_at_utc"]) <= now
             < _timestamp(approval["expires_at_utc"]) <= cutoff
             and now + config["max_lifetime_seconds"] < cutoff, "APPROVAL_TIME_FAILED")


def _token_valid(token):
    return (isinstance(token, str) and 32 <= len(token) <= 4096
            and all(33 <= ord(c) <= 126 for c in token))


def _live_clients(cleanup_only=False):
    # Deliberately lazy: refused runs and planning do not even import clients.
    try:
        from .runpod_api import RunPodAPI, ArtifactClient
    except ImportError:
        from runpod_api import RunPodAPI, ArtifactClient
    if cleanup_only:
        provider = RunPodAPI()
        token = os.environ.get("AGE_ARTIFACT_TOKEN", "")
        artifacts = None
        if _token_valid(token):
            try:
                artifacts = ArtifactClient()
            except Exception:
                pass  # Artifact transport construction must not prevent DELETE.
        return provider, artifacts, None
    token = os.environ.get("AGE_ARTIFACT_TOKEN", "")
    _require(_token_valid(token), "ARTIFACT_TOKEN_REQUIRED")
    _require(token != os.environ.get("RUNPOD_API_KEY"), "DISTINCT_ARTIFACT_TOKEN_REQUIRED")
    return RunPodAPI(), ArtifactClient(), token


def _live_reaper_secret():
    # Deliberately lazy and separate from _live_clients: never read alongside
    # planning/refused runs, and never logged or journaled.
    secret = os.environ.get("AGE_REAPER_SHARED_SECRET", "")
    _require(_reaper_secret_valid(secret), "REAPER_SHARED_SECRET_REQUIRED")
    return secret


def _body(plan, token):
    c = plan["config"]
    return {"name": plan["run_name"], "image": c["image"],
            "gpu": {"id": c["gpu_id"], "count": 1, "minCudaVersion": "12.4"},
            "cloud": c["cloud"], "disk": 10, "ports": ["8080/http"],
            "env": {"AGE_ARTIFACT_TOKEN": token, "AETH01_RUN_ID": plan["run_id"],
                    "AETH01_CANARY_REQUIRE_GPU": "1",
                    "AETH01_CANARY_TIMEOUT_SECONDS": str(c["canary_timeout_seconds"]),
                    "AETH01_CANARY_HOURLY_RATE": str(c["hourly_rate_usd"]),
                    "AETH01_CANARY_MAX_DOLLAR_BUDGET": str(c["canary_budget_usd"])}}


def _owned(pod, plan):
    return (isinstance(pod, dict) and isinstance(pod.get("id"), str)
            and _ID.fullmatch(pod["id"]) is not None
            and pod.get("name") == plan["run_name"]
            and pod.get("image") == plan["config"]["image"]
            and isinstance(pod.get("env"), dict)
            and pod["env"].get("AETH01_RUN_ID") == plan["run_id"])


def validate_result(raw, plan):
    _require(isinstance(raw, bytes) and len(raw) <= 4096, "INVALID_ARTIFACT_SIZE")
    result = _decode(raw)
    _require(result.get("run_id") == plan["run_id"] and result.get("finished") is True
             and type(result.get("exit_code")) is int, "INVALID_RESULT")
    return result["exit_code"]


def validate_receipt(raw, plan, started, now):
    _require(isinstance(raw, bytes) and len(raw) <= 4 * 1024 * 1024, "INVALID_ARTIFACT_SIZE")
    r = _decode(raw)
    required = {"run_id", "semantics_id", "backend", "status", "cases_expected", "cases_run",
                "cases_matched", "single_tick_trials", "multi_tick_trials", "multi_tick_steps",
                "rng_seed", "mismatches", "source_hashes", "started_at_utc", "finished_at_utc",
                "gpu_kernel_seconds", "cpu_oracle_seconds", "python_version", "numpy_version",
                "cupy_version", "cost_context"}
    _require(set(r) == required, "INVALID_RECEIPT_FIELDS")
    _require(r.get("run_id") == plan["run_id"] and r.get("semantics_id") == "aeth01.v1"
             and r.get("backend") == "cupy" and r.get("status") == "PASS",
             "RECEIPT_NOT_GPU_PASS")
    for key, value in {"cases_expected": 300, "cases_run": 300, "cases_matched": 300,
                       "single_tick_trials": 200, "multi_tick_trials": 20,
                       "multi_tick_steps": 5, "rng_seed": 0}.items():
        _require(type(r.get(key)) is int and r[key] == value, "INCOMPLETE_CORPUS")
    _require(r.get("mismatches") == [] and r.get("source_hashes") == plan["source_hashes"],
             "RECEIPT_BINDING_FAILED")
    begin = _timestamp(r.get("started_at_utc"))
    end = _timestamp(r.get("finished_at_utc"))
    _require(started <= begin <= end <= now
             and end - begin <= plan["config"]["canary_timeout_seconds"],
             "INVALID_RECEIPT_DATES")
    for key in ("gpu_kernel_seconds", "cpu_oracle_seconds"):
        _require(_number(r.get(key), positive=False) and r[key] <= end - begin,
                 "INVALID_RECEIPT_TIMING")
    for key in ("python_version", "numpy_version", "cupy_version"):
        _require(isinstance(r.get(key), str)
                 and re.fullmatch(r"[0-9]+\.[0-9]+(?:[A-Za-z0-9.+_-]*)", r[key]),
                 "INVALID_RECEIPT_VERSION")
    context = r.get("cost_context")
    _require(isinstance(context, dict), "INVALID_COST_CONTEXT")
    for key, expected in (("hourly_rate_usd", plan["config"]["hourly_rate_usd"]),
                          ("max_dollar_budget_usd", plan["config"]["canary_budget_usd"]),
                          ("watchdog_timeout_seconds", plan["config"]["canary_timeout_seconds"])):
        _require(_number(context.get(key)) and context[key] == expected,
                 "INVALID_COST_CONTEXT")


class _Lifecycle:
    def __init__(self, directory, plan, state, provider, artifacts, clock):
        self.directory, self.plan, self.state = Path(directory), plan, state
        self.provider, self.artifacts, self.clock = provider, artifacts, clock
        self.journal_failed = False
        self.evidence_failed_ids = set()
        # If a prior conflict could not be journaled, require fresh bindings
        # for every saved ID rather than treating old history as authorization.
        self.binding_conflicts = set(state["owned_ids"]) if state["ownership_ambiguous"] else set()
        self.last_wall = _timestamp(state["last_wall_utc"])
        self.last_mono = clock.monotonic()
        remaining = max(0, _timestamp(state["deadline_utc"]) - clock.time())
        self.deadline = self.last_mono + remaining
        self.mono_start = self.deadline - plan["config"]["max_lifetime_seconds"]

    def _diag(self, stage, outcome, http_status=None, pod_status=None, attempt=None):
        # B4: secret-safe, closed-vocabulary journal. Never persist raw
        # exception text, headers, env, or provider bodies here.
        _require(stage in _DIAG_STAGES and outcome in _DIAG_OUTCOMES, "INVALID_DIAGNOSTIC")
        if len(self.state["diagnostics"]) >= _DIAGNOSTICS_LIMIT:
            return
        self.state["diagnostics"].append({
            "stage": stage, "outcome": outcome,
            "http_status": http_status if isinstance(http_status, int) else None,
            "pod_status": pod_status if isinstance(pod_status, str) and pod_status in _POD_STATUSES else None,
            "elapsed_seconds": round(max(0.0, self.clock.monotonic() - self.mono_start), 3),
            "attempt": attempt if isinstance(attempt, int) else None,
        })

    def _diag_error(self, stage, error, attempt=None):
        outcome, status = _classify_transport_error(error)
        self._diag(stage, outcome, http_status=status, attempt=attempt)

    def _fetch_diag(self, pod_id, name, stage):
        """Fetch one artifact, journaling a B4-safe outcome either way.

        A transient miss (None) is not an error: it is journaled MISSING so an
        operator can distinguish "service never produced it" from a transport
        failure, without ever delaying DELETE or blocking on this journal.
        """
        try:
            raw = self.artifacts.fetch(pod_id, name)
        except (Exception, KeyboardInterrupt) as error:
            self._diag_error(stage, error)
            raise
        self._diag(stage, "SUCCESS" if raw is not None else "MISSING")
        return raw

    def commit(self):
        atomic_write(self.directory / "state.json", _encode(self.state))

    def best_commit(self):
        try:
            self.commit()
        except (Exception, KeyboardInterrupt):
            self.journal_failed = True
            self.state["controller_failed"] = True

    def _record(self, pod_id, kind, *, status=None, result=None):
        """Keep provider facts durable without making recording a DELETE gate."""
        if kind == "OWNERSHIP_CONFLICT":
            self.binding_conflicts.add(pod_id)
        elif kind == "OBSERVE":
            self.binding_conflicts.discard(pod_id)
        try:
            rec = self.state["pod_evidence"].setdefault(pod_id, _new_pod_evidence())
            policy.append_pod(rec, kind, policy.utc(self.clock.time()),
                              status=status, result=result)
            self._refresh_confidence(pod_id)
        except (Exception, KeyboardInterrupt):
            self.journal_failed = True
            self.state["controller_failed"] = True
            self.evidence_failed_ids.add(pod_id)
            self.state["cleanup_status"] = "LOCAL_CLEANUP_UNRESOLVED"
            if pod_id in self.state["terminated_ids"]:
                self.state["terminated_ids"].remove(pod_id)
        self.best_commit()

    def _observe_get(self, pod_id, pod):
        if pod is None:
            self._record(pod_id, "MISSING")
        elif _owned(pod, self.plan) and pod["id"] == pod_id:
            self._record(pod_id, "OBSERVE", status=_pod_status(pod))
        else:
            # A different identity at a known GET target is not mere absence.
            self.state["ownership_ambiguous"] = True
            self._record(pod_id, "OWNERSHIP_CONFLICT")

    def now(self):
        wall, mono = self.clock.time(), self.clock.monotonic()
        _require(_number(wall) and _number(mono, positive=False)
                 and wall >= self.last_wall and mono >= self.last_mono, "CLOCK_BACKWARDS")
        self.last_wall, self.last_mono = wall, mono
        self.state["last_wall_utc"] = _utc(wall)
        return wall, mono

    def available(self, reserve=0):
        try:
            wall, mono = self.now()
            return (mono + reserve < self.deadline
                    and wall + reserve < _timestamp(self.state["deadline_utc"]))
        except (Exception, KeyboardInterrupt):
            self.state["controller_failed"] = True
            self.state["reason"] = "CLOCK_BACKWARDS"
            return False

    def guard(self, deadline):
        wall, mono = self.now()
        _require(mono < min(deadline, self.deadline)
                 and wall < _timestamp(self.state["deadline_utc"]) - CLEANUP_SECONDS,
                 "LIFECYCLE_TIMEOUT")
        return wall, mono

    def adopt(self, pod):
        _require(_owned(pod, self.plan), "UNVERIFIED_CREATE_RESPONSE")
        pod_id = pod["id"]
        if pod_id not in self.state["owned_ids"]:
            self.state["owned_ids"].append(pod_id)
        # Ownership remains in memory if the disk fills at this precise point.
        self.state["phase"] = "OWNED"
        # B2: a single successful create response does NOT prove exactly-once
        # allocation. reconciliation_required stays true for the whole run
        # (and is a durable obligation the independent reaper also carries);
        # it is never disarmed by this optimistic path.
        self._record(pod_id, "OBSERVE", status=_pod_status(pod))
        _require(not self.journal_failed, "JOURNAL_FAILED")
        return pod_id

    def save_artifact(self, pod_id, name, raw):
        limit = 4096 if name == "result.json" else 4 * 1024 * 1024
        _require(isinstance(raw, bytes) and len(raw) <= limit, "INVALID_ARTIFACT_SIZE")
        directory = self.directory / "artifacts" / pod_id
        directory.mkdir(parents=True, exist_ok=True)
        _sync_directory(directory.parent)
        atomic_write(directory / name, raw)
        self.state["artifacts"].setdefault(pod_id, {})[name] = _sha(raw)
        self.commit()

    def check_rate(self, pod):
        # RunPod v2 reports `cost`, not v1-style `costPerHr`. This remains
        # a cross-check, never proof of all-in billing or a price reservation.
        rate = pod.get("cost") if isinstance(pod, dict) else None
        _require(_number(rate) and rate <= self.plan["config"]["hourly_rate_usd"],
                 "INVALID_OR_OVERQUOTE_RATE")

    def monitor(self, pod_id):
        start_mono = self.deadline - self.plan["config"]["max_lifetime_seconds"]
        boot_deadline = start_mono + self.plan["phases"]["boot_pull_seconds"]
        work_deadline = self.deadline - CLEANUP_SECONDS
        running_deadline = None
        while True:
            self.guard(work_deadline)
            try:
                pod = self.provider.get_pod(pod_id)
            except (Exception, KeyboardInterrupt) as error:
                self._diag_error("GET_STATUS", error)
                self._record(pod_id, "UNKNOWN")
                raise
            # Retain a late positive even when the following phase guard fails.
            self._observe_get(pod_id, pod)
            wall, mono = self.guard(work_deadline)
            _require(_owned(pod, self.plan) and pod["id"] == pod_id,
                     "POD_MISSING_OR_OWNERSHIP_CHANGED")
            self.check_rate(pod)
            status = _pod_status(pod)
            self._diag("GET_STATUS", "SUCCESS",
                       pod_status=status if isinstance(status, str) else None)
            if status in ("EXITED", "ERROR"):
                self._diag("GET_STATUS", "POD_EXITED" if status == "EXITED" else "POD_ERROR",
                           pod_status=status)
            _require(status in ("PROVISIONING", "STARTING", "RUNNING"), "POD_STATUS_FAILED")
            if status != "RUNNING":
                _require(mono < boot_deadline and running_deadline is None, "BOOT_TIMEOUT")
            else:
                if running_deadline is None:
                    _require(mono < boot_deadline, "BOOT_TIMEOUT")
                    running_deadline = min(work_deadline, mono + RETRIEVAL_SECONDS
                                           + self.plan["config"]["canary_timeout_seconds"])
                self.guard(running_deadline)
                final = self._fetch_diag(pod_id, "result.json", "ARTIFACT_RESULT")
                self.guard(running_deadline)
                if final is not None:
                    exit_code = validate_result(final, self.plan)
                    receipt = self._fetch_diag(pod_id, "receipt.json", "ARTIFACT_RECEIPT")
                    self.guard(running_deadline)
                    log = self._fetch_diag(pod_id, "canary.log", "ARTIFACT_LOG")
                    wall, _ = self.guard(running_deadline)
                    if receipt is not None and log is not None:
                        # Preserve even a final failure before adjudicating science.
                        for name, raw in (("result.json", final), ("receipt.json", receipt),
                                          ("canary.log", log)):
                            self.save_artifact(pod_id, name, raw)
                        validate_receipt(receipt, self.plan,
                                         _timestamp(self.state["started_at_utc"]), wall)
                        _require(exit_code == 0, "CANARY_EXIT_FAILED")
                        self.guard(running_deadline)
                        self.state["science_verdict"] = "PASS"
                        self.state["phase"] = "ARTIFACTS_SAVED"
                        self.commit()
                        return
            self.best_commit()
            _require(not self.journal_failed, "JOURNAL_FAILED")
            self.clock.sleep(POLL_SECONDS)

    def reconcile(self):
        """Retain every exact-owned positive, including on partial page failure."""
        seen = set()

        def observe(pod):
            if _owned(pod, self.plan):
                pod_id = pod["id"]
                seen.add(pod_id)
                if pod_id not in self.state["owned_ids"]:
                    self.state["owned_ids"].append(pod_id)
                self._record(pod_id, "OBSERVE", status=_pod_status(pod))
            elif isinstance(pod, dict) and pod.get("id") in self.state["owned_ids"]:
                seen.add(pod["id"])
                self.state["ownership_ambiguous"] = True
                self._record(pod["id"], "OWNERSHIP_CONFLICT")
            # Partial name/run matches at other IDs are unrelated, not ambiguous.

        visitor = getattr(self.provider, "visit_pods", None)
        try:
            if visitor is not None:
                visitor(observe)  # Later page failure retains earlier positive ownership.
            else:
                pods = self.provider.list_pods()
                _require(isinstance(pods, list), "INVALID_INVENTORY")
                for pod in pods:
                    observe(pod)
        except (Exception, KeyboardInterrupt) as error:
            self._diag_error("LIST_INVENTORY", error)
            for pod_id in list(self.state["owned_ids"]):
                self._record(pod_id, "SCAN_FAILED")
            self.best_commit()
            raise
        self._diag("LIST_INVENTORY", "SUCCESS")
        # This scan fully succeeded: every currently-owned pod that was NOT
        # observed just became one independent absence witness, but only if
        # its DELETE was actually acknowledged -- absence alone never counts.
        self.state["reconciled"] = True
        self.state["reconciliation_scans_completed"] += 1
        for pod_id in list(self.state["owned_ids"]):
            if pod_id in seen:
                continue
            self._record(pod_id, "ABSENT_SCAN")
        self.best_commit()

    def _refresh_confidence(self, pod_id):
        """Current confidence is replay-derived, never historical termination."""
        rec = self.state["pod_evidence"][pod_id]
        derived = policy.validate_pod(rec)
        confirmed = (derived["cleanup_confidence"] == "CONFIRMED"
                     and pod_id not in self.evidence_failed_ids)
        if confirmed:
            if pod_id not in self.state["terminated_ids"]:
                self.state["terminated_ids"].append(pod_id)
        else:
            self.state["cleanup_status"] = "LOCAL_CLEANUP_UNRESOLVED"
            if pod_id in self.state["terminated_ids"]:
                self.state["terminated_ids"].remove(pod_id)

    def salvage(self, pod_id):
        if self.artifacts is None:
            return
        for name in ("result.json", "receipt.json", "canary.log"):
            if not self.available(reserve=60):
                return
            if name in self.state["artifacts"].get(pod_id, {}):
                continue
            try:
                raw = self.artifacts.fetch(pod_id, name)
                if raw is not None:
                    self.save_artifact(pod_id, name, raw)
            except (Exception, KeyboardInterrupt):
                # Logs and disk failures must never prevent DELETE.
                continue

    def terminate(self, pod_id):
        """B1: record DELETE's real result and the following GET's real
        visibility as independent facts. NEVER infer termination from an
        ambiguous 404 alone (official v2 NotFoundError means "not found or
        not accessible to the caller", not solely "no longer exists").
        """
        rec = self.state["pod_evidence"].get(pod_id, {})
        last_binding = next((entry["kind"] for entry in reversed(rec.get("history", []))
                             if entry["kind"] in ("OBSERVE", "OWNERSHIP_CONFLICT")), None)
        if pod_id in self.binding_conflicts or last_binding == "OWNERSHIP_CONFLICT":
            # Do not act on a stale identity after positively observing a
            # different object at this ID. A fresh exact binding is required.
            return
        if pod_id not in self.state["delete_attempted_ids"]:
            self.state["delete_attempted_ids"].append(pod_id)
        self._record(pod_id, "DELETE_ATTEMPT")
        try:
            result = self.provider.terminate_pod(pod_id)
            result = result if result in ("ACK_204", "NOT_FOUND_404") else "TRANSPORT_UNKNOWN"
            self._diag("DELETE", result)
        except KeyboardInterrupt:
            result = "TRANSPORT_UNKNOWN"
        except Exception as error:
            result, status = _classify_transport_error(error)
            result = "HTTP_OTHER" if result == "SCHEMA_INVALID" else result
            self._diag("DELETE", result, http_status=status)
        self._record(pod_id, "DELETE_RESULT", result=result)
        try:
            pod = self.provider.get_pod(pod_id)
        except (Exception, KeyboardInterrupt) as error:
            if not isinstance(error, KeyboardInterrupt):
                self._diag_error("GET_STATUS", error)
            self._record(pod_id, "UNKNOWN")
        else:
            self._observe_get(pod_id, pod)
            if pod is None:
                # Ambiguous: not found OR not accessible. NOT evidence of
                # termination by itself; only independent reconciliation
                # (_refresh_confidence route b) may corroborate it.
                self._diag("GET_STATUS", "SUCCESS")
            elif _owned(pod, self.plan) and pod.get("id") == pod_id:
                status = _pod_status(pod)
                self._diag("GET_STATUS", "SUCCESS",
                           pod_status=status if isinstance(status, str) else None)
                if status not in ("EXITED", "TERMINATED"):
                    try:
                        self.check_rate(pod)
                    except ControllerError:
                        self.state["controller_failed"] = True
        self.best_commit()

    def cleanup(self):
        self.state["phase"] = "CLEANUP"
        self.best_commit()
        salvaged = set()
        inventory_ok = True
        # Recovery after an expired live deadline still needs a bounded emergency
        # deletion window. Many duplicate IDs must not multiply this into hours.
        cleanup_start = self.clock.monotonic()
        cleanup_end = cleanup_start + CLEANUP_SECONDS

        def finish_owned():
            for pod_id in list(self.state["owned_ids"]):
                if pod_id in self.state["terminated_ids"]:
                    continue
                if self.clock.monotonic() >= cleanup_end:
                    break
                rec = self.state["pod_evidence"].get(pod_id, {})
                if (pod_id not in self.evidence_failed_ids and rec.get("delete_result") == "ACK_204"
                        and rec.get("absence_confirmations", 0) > 0):
                    # Let inventory corroborate a current ACK without an
                    # unnecessary GET failure erasing its independent witness.
                    # Every live observation clears this ACK and re-enables DELETE.
                    continue
                try:
                    if pod_id not in salvaged:
                        salvaged.add(pod_id)
                        self.salvage(pod_id)
                except (Exception, KeyboardInterrupt):
                    pass
                finally:
                    self.terminate(pod_id)

        def owned_confirmed():
            # A run that never positively owned anything can NEVER be
            # confirmed clean from empty scans alone (no finite polling count
            # proves a create never silently succeeded, B2) -- it stays loud
            # and UNRESOLVED until something is actually found-and-deleted or
            # an operator/reaper otherwise resolves it.
            return bool(self.state["owned_ids"]) and self._known_owned_confirmed()

        # B2: reconciliation is unconditional and run-wide -- it happens even
        # on an apparently clean success, and it is never skipped merely
        # because a create response was received. Known-ID deletion is never
        # delayed for it (finish_owned runs both before and after the scan).
        # Expiry never cancels deletion. Exceeding the original deadline still
        # fails the controller verdict; emergency retries use their own window.
        for attempt in range(CLEANUP_ROUNDS):
            if self.clock.monotonic() >= cleanup_end:
                break
            finish_owned()  # Do not delay already-known pod deletion for inventory.
            try:
                self.reconcile()
            except (Exception, KeyboardInterrupt):
                inventory_ok = False
            finish_owned()  # Includes positive records from an incomplete listing.
            if owned_confirmed() and self.state["reconciled"] and inventory_ok:
                break
            if (attempt + 1 == CLEANUP_ROUNDS
                    or self.clock.monotonic() + POLL_SECONDS >= cleanup_end):
                break
            try:
                self.now()  # Backwards clocks still fail closed; expiry does not.
                self.clock.sleep(POLL_SECONDS)
            except (Exception, KeyboardInterrupt):
                break
        clean = owned_confirmed() and inventory_ok and self.state["reconciled"] \
            and not self.state["ownership_ambiguous"]
        if not self.available():
            self.state["controller_failed"] = True
        # B2/B3: this is ONLY this controller's own bounded local evidence.
        # reconciliation_required stays true regardless -- it is a durable
        # obligation the independent reaper still carries; see RISK/outcome().
        self.state["cleanup_status"] = "LOCAL_CLEANUP_CONFIRMED" if clean else "LOCAL_CLEANUP_UNRESOLVED"
        self.state["phase"] = "DONE"
        self.best_commit()

    def _known_owned_confirmed(self):
        try:
            return (not self.evidence_failed_ids and not self.state["ownership_ambiguous"]
                    and set(self.state["pod_evidence"]) == set(self.state["owned_ids"])
                    and all(policy.pod_confirmed(rec) for rec in self.state["pod_evidence"].values()))
        except policy.EvidenceError:
            return False

    def outcome(self):
        known_clean = self._known_owned_confirmed()
        clean = self.state["cleanup_status"] == "LOCAL_CLEANUP_CONFIRMED" and known_clean
        success = (clean and self.state["science_verdict"] == "PASS"
                   and not self.state["controller_failed"] and not self.journal_failed)
        manifest = reaper_manifest_document(self.plan)
        return deepcopy({"version": 3, "policy_version": 1,
                "state_sha256": _sha(_encode(self.state)),
                "generated_at_utc": policy.utc(self.clock.time()),
                "manifest": manifest, "manifest_sha256": _sha(_encode(manifest)),
                "owned_ids": self.state["owned_ids"],
                "ownership_ambiguous": self.state["ownership_ambiguous"],
                "known_owned_cleanup_status": ("KNOWN_OWNED_CLEANUP_CONFIRMED"
                    if known_clean else "KNOWN_OWNED_CLEANUP_UNRESOLVED"),
                "run_id": self.plan["run_id"], "verdict": "PASS" if success else
                ("FAIL" if clean else "CLEANUP_UNRESOLVED"),
                "science_verdict": self.state["science_verdict"],
                "cleanup_status": "LOCAL_CLEANUP_CONFIRMED" if clean else "LOCAL_CLEANUP_UNRESOLVED",
                "reconciliation_required": self.state["reconciliation_required"],
                "pod_evidence": self.state["pod_evidence"],
                "journal_ok": not self.journal_failed,
                "exit_code": 0 if success else (1 if clean else 2), "billing_risk": RISK,
                "operational_note": ("LOCAL_CLEANUP_CONFIRMED reflects only this controller's "
                                     "bounded evidence. Run-level OPERATIONAL cleanup additionally "
                                     "requires the independent reaper's REAPER_CLEANUP_CONFIRMED "
                                     "evidence under a bounded observation policy; this does not "
                                     "prove billing stopped. See "
                                     "independent_reaper.py and combine_operational_cleanup().")})


def run(run_dir, approval, *, execute_paid_run=False, provider=None, artifacts=None,
        artifact_token=None, reaper_secret=None, clock=None):
    """Exactly one possible POST. All gates and durable intent precede that POST."""
    _require(execute_paid_run is True, "PAID_EXECUTION_FLAG_REQUIRED")
    clock = clock or Clock()
    directory = Path(run_dir)
    with RunLock(directory):
        _require(not (directory / "state.json").exists(), "RUN_ALREADY_LAUNCHED")
        plan, digest = _load_plan(directory)
        validate_approval(approval, plan, digest, clock.time())
        _require(plan["source_hashes"] == {name: _sha(_read(HERE / name, 4 * 1024 * 1024))
                                            for name in SOURCES}, "LOCAL_SOURCE_CHANGED")
        if (provider is None and artifacts is None and artifact_token is None
                and reaper_secret is None):
            provider, artifacts, artifact_token = _live_clients()
            reaper_secret = _live_reaper_secret()
        _require(provider is not None and artifacts is not None and _token_valid(artifact_token),
                 "INCOMPLETE_INJECTED_CLIENTS")
        # B3: refuse the paid create unless a genuinely independent, durably
        # armed reaper has acknowledged this exact plan. See
        # ASTRA_CLOSURE_REVIEW_02.md section 6: "a Boolean attestation is not
        # evidence"; this requires an HMAC-bound file the reaper produced.
        _require_reaper_armed(directory, plan, reaper_secret)
        started, mono = clock.time(), clock.monotonic()
        validate_approval(approval, plan, digest, started)
        state = {"version": 3, "run_id": plan["run_id"], "plan_sha256": digest,
                 "run_name": plan["run_name"], "image": plan["config"]["image"],
                 "phase": "CREATE_INTENT", "started_at_utc": _utc(started),
                 "deadline_utc": _utc(started + plan["config"]["max_lifetime_seconds"]),
                 "last_wall_utc": _utc(started), "owned_ids": [], "delete_attempted_ids": [],
                 "terminated_ids": [], "pod_evidence": {},
                 # B2: this obligation is durable and is never disarmed by an
                 # optimistic create response; see adopt()/cleanup()/RISK.
                 "reconciliation_required": True, "reconciled": False,
                 "reconciliation_scans_completed": 0,
                 "ownership_ambiguous": False, "science_verdict": "INCOMPLETE",
                 "cleanup_status": "LOCAL_CLEANUP_UNRESOLVED", "controller_failed": False,
                 "reason": "", "artifacts": {}, "diagnostics": []}
        lifecycle = _Lifecycle(directory, plan, state, provider, artifacts, clock)
        lifecycle.deadline = mono + plan["config"]["max_lifetime_seconds"]
        # Preflight failure is a hard refusal with ZERO provider calls.
        try:
            lifecycle.commit()
        except OSError:
            raise ControllerError("CREATE_INTENT_WRITE_FAILED") from None
        try:
            lifecycle.guard(lifecycle.deadline - CLEANUP_SECONDS)
            validate_approval(approval, plan, digest, clock.time())
            try:
                response = provider.create_pod(_body(plan, artifact_token))  # NEVER retry.
            except (Exception, KeyboardInterrupt) as error:
                if not isinstance(error, KeyboardInterrupt):
                    lifecycle._diag_error("CREATE", error)
                raise
            lifecycle._diag("CREATE", "SUCCESS")
            pod_id = lifecycle.adopt(response)
            lifecycle.check_rate(response)
            lifecycle.monitor(pod_id)
        except (Exception, KeyboardInterrupt) as error:
            state["controller_failed"] = True
            state["reason"] = ("INTERRUPTED" if isinstance(error, KeyboardInterrupt) else
                               str(error) if isinstance(error, ControllerError) else "CONTROLLER_FAILED")
            if state["science_verdict"] != "PASS":
                state["science_verdict"] = "FAIL"
        finally:
            lifecycle.cleanup()
        return lifecycle.outcome()


def _load_state(directory, plan, digest):
    state = _decode(_read(Path(directory) / "state.json"))
    try:
        _require(type(state["version"]) is int and state["version"] == 3,
                 "UNSUPPORTED_STATE_VERSION")
        _require(state["run_id"] == plan["run_id"] and state["plan_sha256"] == digest
                 and state["run_name"] == plan["run_name"]
                 and state["image"] == plan["config"]["image"],
                 "INVALID_STATE_BINDING")
        start = _timestamp(state["started_at_utc"])
        _require(_timestamp(plan["created_at_utc"]) <= start
                 and _timestamp(state["deadline_utc"]) == start + plan["config"]["max_lifetime_seconds"]
                 and _timestamp(state["last_wall_utc"]) >= start, "INVALID_STATE_DATES")
        for key in ("owned_ids", "delete_attempted_ids", "terminated_ids"):
            _require(isinstance(state[key], list)
                     and all(isinstance(p, str) and _ID.fullmatch(p) for p in state[key])
                     and len(state[key]) == len(set(state[key])), "INVALID_STATE_OWNERSHIP")
        _require(set(state["terminated_ids"]) <= set(state["owned_ids"])
                 and set(state["delete_attempted_ids"]) <= set(state["owned_ids"]),
                 "INVALID_STATE_OWNERSHIP")
        for key in ("reconciliation_required", "reconciled", "ownership_ambiguous", "controller_failed"):
            _require(type(state[key]) is bool, "INVALID_STATE")
        _require(type(state["reconciliation_scans_completed"]) is int
                 and state["reconciliation_scans_completed"] >= 0, "INVALID_STATE")
        _require(state["science_verdict"] in ("INCOMPLETE", "FAIL", "PASS")
                 and isinstance(state["artifacts"], dict), "INVALID_STATE")
        evidence = state["pod_evidence"]
        _require(isinstance(evidence, dict) and set(evidence) == set(state["owned_ids"]), "INVALID_STATE")
        for pod_id, rec in evidence.items():
            derived = policy.validate_pod(rec)
            _require(bool(rec["history"])
                     and derived["delete_attempted"] == (pod_id in state["delete_attempted_ids"])
                     and (derived["cleanup_confidence"] == "CONFIRMED") ==
                         (pod_id in state["terminated_ids"]), "INVALID_STATE_EVIDENCE")
        diagnostics = state["diagnostics"]
        _require(isinstance(diagnostics, list) and len(diagnostics) <= _DIAGNOSTICS_LIMIT, "INVALID_STATE")
        for entry in diagnostics:
            _require(isinstance(entry, dict) and set(entry) ==
                     {"stage", "outcome", "http_status", "pod_status", "elapsed_seconds", "attempt"},
                     "INVALID_STATE")
            _require(entry["stage"] in _DIAG_STAGES and entry["outcome"] in _DIAG_OUTCOMES, "INVALID_STATE")
    except (KeyError, TypeError, policy.EvidenceError):
        raise ControllerError("INVALID_STATE") from None
    return state


def combine_operational_cleanup(local_outcome, reaper_report, *, run_dir=None, now=None):
    """Seal against the authoritative original run directory, without provider I/O.

    Run/recover hold this same lock for their entire provider lifecycle. A seal
    is point-in-time evidence, not permission to reuse a report after recovery.
    Copies/rollbacks of the authoritative directory are outside this protocol.
    """
    _require(run_dir is not None, "AUTHORITATIVE_RUN_DIR_REQUIRED")
    try:
        with RunLock(run_dir):
            plan, digest = _load_plan(run_dir)
            state = _load_state(run_dir, plan, digest)
            _require(state["phase"] == "DONE", "LOCAL_STATE_NOT_FINAL")
            sealed_at = Clock().time() if now is None else now
            seal_time = policy.utc(sealed_at)
            result = policy.aggregate(local_outcome, reaper_report, now=sealed_at)
            _require(local_outcome.get("state_sha256") == _sha(_encode(state)),
                     "STALE_LOCAL_OUTCOME")
            _require(policy.timestamp(local_outcome.get("generated_at_utc")) <= sealed_at,
                     "INVALID_CLEANUP_EVIDENCE")
            # Reconstruct from disk, not from the supplied hash or cached labels.
            fresh = _Lifecycle(run_dir, plan, state, None, None, Clock()).outcome()
            _require({k: v for k, v in local_outcome.items() if k != "generated_at_utc"}
                     == {k: v for k, v in fresh.items() if k != "generated_at_utc"},
                     "INVALID_CLEANUP_EVIDENCE")
            result["authoritative_local_state"] = True
            result["local_seal"] = {"version": 1, "run_id": plan["run_id"],
                "state_sha256": fresh["state_sha256"], "sealed_at_utc": seal_time,
                "local_report_sha256": _sha(_encode(local_outcome)),
                "reaper_report_sha256": _sha(_encode(reaper_report))}
            result["exit_code"] = (0 if result["operational_cleanup_status"] ==
                                   "OPERATIONAL_CLEANUP_CONFIRMED" else 2)
            atomic_write(Path(run_dir) / "cleanup_seal.json", _encode(result))
            return result
    except (policy.EvidenceError, KeyError, TypeError, ValueError, OSError):
        raise ControllerError("INVALID_CLEANUP_EVIDENCE") from None


def recover(run_dir, *, provider=None, artifacts=None, clock=None):
    """Cleanup only: no approval, no source recheck, no token required to DELETE."""
    clock = clock or Clock()
    directory = Path(run_dir)
    with RunLock(directory):
        plan, digest = _load_plan(directory)
        state = _load_state(directory, plan, digest)
        if provider is None:
            _require(artifacts is None, "INCOMPLETE_INJECTED_CLIENTS")
            provider, artifacts, _ = _live_clients(cleanup_only=True)
        lifecycle = _Lifecycle(directory, plan, state, provider, artifacts, clock)
        # Recovery does not retroactively award scientific/controller success.
        state["controller_failed"] = True
        lifecycle.cleanup()
        return lifecycle.outcome()


def _interrupt(signum, frame):
    # Normal SIGTERM must run the same finally/cleanup path as Ctrl-C.
    # SIGKILL, host loss, and provider outage still require independent recovery.
    raise KeyboardInterrupt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planning = commands.add_parser("plan")
    planning.add_argument("--config", required=True)
    planning.add_argument("--run-dir", required=True)
    launching = commands.add_parser("run")
    launching.add_argument("--run-dir", required=True)
    launching.add_argument("--approval", required=True)
    launching.add_argument("--execute-paid-run", action="store_true")
    recovering = commands.add_parser("recover")
    recovering.add_argument("--run-dir", required=True)
    combining = commands.add_parser("combine")
    combining.add_argument("--run-dir", required=True)
    combining.add_argument("--local-outcome", required=True)
    combining.add_argument("--reaper-report", required=True)
    args = parser.parse_args(argv)
    previous_term = signal.signal(signal.SIGTERM, _interrupt)
    try:
        if args.command == "plan":
            outcome = create_plan(_decode(_read(args.config)), args.run_dir)
        elif args.command == "run":
            _require(args.execute_paid_run, "PAID_EXECUTION_FLAG_REQUIRED")
            outcome = run(args.run_dir, _decode(_read(args.approval)), execute_paid_run=True)
        elif args.command == "combine":
            outcome = combine_operational_cleanup(
                _decode(_read(args.local_outcome, 64 * 1024 * 1024)),
                _decode(_read(args.reaper_report, 64 * 1024 * 1024)), run_dir=args.run_dir)
        else:
            outcome = recover(args.run_dir)
    except (Exception, KeyboardInterrupt) as error:
        # Do not print exception repr, provider bodies, paths, or environment.
        reason = str(error) if isinstance(error, ControllerError) else "CONTROLLER_FAILED"
        print(json.dumps({"verdict": "REFUSED_OR_FAILED", "reason": reason,
                          "exit_code": 2, "billing_risk": RISK}))
        return 2
    finally:
        signal.signal(signal.SIGTERM, previous_term)
    print(json.dumps(outcome, sort_keys=True))
    return outcome.get("exit_code", 0)


if __name__ == "__main__":
    raise SystemExit(main())