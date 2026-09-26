"""The launch path: create, watch, retrieve, terminate, account.

This is the only module that can spend money, so it is the only one
written to be driven entirely by an injected provider and an injected
clock. Every ordering property below is a test against `FakeProvider`,
which means reliability work costs nothing and a rung of the engineering
ladder can be qualified before hardware is involved.

ORDER IS THE SAFETY PROPERTY. In sequence:

  1. READ THE INVENTORY FIRST, and refuse to launch if anything is
     already running, or if the read itself failed. One pod at a time is
     not a convention here; it is a precondition, and "I could not tell"
     is not permission.
  2. Build and hash the bundle, and plan the run, BEFORE creating
     anything. A malformed run must cost nothing.
  3. Create through `create_with_reconcile`, so an ambiguous outcome is
     resolved by reading the inventory rather than by a second create.
  4. Watch. Poll telemetry from the pod's own channel. Stop on the
     module's `end`, on the dollar ceiling, or on `max_runtime_s`.
  5. RETRIEVE BEFORE TERMINATING. Artifacts and telemetry come back from
     a pod that still exists. Terminating first to save a minute destroys
     exactly the evidence a failed run needs.
  6. TERMINATE IN A `finally`, on every path including an exception, and
     then confirm absence separately.
  7. Write a receipt that claims only what the evidence supports.

WHAT THIS MODULE WILL NOT DO. It will not retry a create blindly, it
will not treat an empty listing as proof of cleanup, and it will not
claim billing reconciliation. Those refusals live in
`provider.create_with_reconcile` and `receipt.py` respectively, and this
module is wired so it cannot route around them.
"""

import hashlib
import time

from . import cost as cost_mod
from . import dryrun
from . import provider as prov
from . import receipt as rc
from . import secrets as secrets_mod
from . import telemetry as tel_mod

# Relative to the ARTIFACT DIRECTORY, which is the artifact server's
# document root -- not to the module's working directory. Iteration 1's
# third flight spent ten minutes collecting 404s because these carried an
# "out/" prefix that the server root already accounted for.
TELEMETRY_PATH = "telemetry.jsonl"
STAGES_PATH = "stages.jsonl"
# Written by the platform sampler, not the module (dryrun.PLATFORM_SAMPLER).
PLATFORM_PATH = "platform.jsonl"
# Served by the artifact server: the pod's clock at the instant of asking.
CLOCK_PATH = "_clock"
CLOCK_SAMPLES = 5

# Pod stages, in order. The intervals between consecutive
# stages are what the cost model's overhead terms are made of.
STAGE_ORDER = ("boot", "fetched", "verified", "unpacked",
               "installed", "canary", "module_start",
               "module_end")


class LaunchRefused(RuntimeError):
    """A precondition failed. Nothing was created, so nothing is billing."""


def parse_stages(text):
    """Pod-side stage markers -> {stage: epoch_seconds}. Pod clock."""
    import json as _json
    out = {}
    for line in str(text).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = _json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and "stage" in rec and "epoch" in rec:
            try:
                out[str(rec["stage"])] = float(rec["epoch"])
            except (TypeError, ValueError):
                continue
    return out


def lifecycle(marks, stages, telemetry_summary=None, clock_sync=None):
    """Named intervals, each labelled with the clock it came from.

    Pod-to-pod intervals are sound. Controller-to-controller intervals are
    sound. An interval spanning both is reported with `cross_clock: true`,
    because the two machines' clocks are not the same clock and the
    difference is not something this measures.
    """
    stages = stages or {}
    out = {"pod_clock": {}, "controller_clock": {}, "cross_clock": {}}

    def pod_gap(name, a, b):
        if a in stages and b in stages:
            out["pod_clock"][name] = round(stages[b] - stages[a], 3)

    pod_gap("fetch_s", "boot", "fetched")
    pod_gap("verify_s", "fetched", "verified")
    pod_gap("unpack_s", "verified", "unpacked")
    pod_gap("dependency_install_s", "unpacked", "installed")
    pod_gap("canary_s", "installed", "canary")
    pod_gap("bootstrap_total_s", "boot", "module_start")
    pod_gap("execution_s", "module_start", "module_end")

    def ctl_gap(name, a, b):
        if a in marks and b in marks:
            out["controller_clock"][name] = round(marks[b] - marks[a], 3)

    ctl_gap("create_call_s", "create_requested", "create_answered")
    ctl_gap("accepted_to_first_telemetry_s", "create_answered",
            "first_telemetry")
    # When the pod first answered through the provider's proxy at all.
    # Iteration 2 found this, not provisioning, is where the time goes: the
    # pod booted ~2 s after the create was accepted and the proxy returned
    # 404 for ~25 s more.
    ctl_gap("accepted_to_first_contact_s", "create_answered", "first_contact")
    ctl_gap("artifact_transfer_s", "retrieve_start", "retrieve_end")
    ctl_gap("terminate_ack_s", "terminate_requested", "terminate_acknowledged")
    ctl_gap("absence_confirm_s", "terminate_requested", "absence_confirmed")
    ctl_gap("teardown_total_s", "retrieve_start", "absence_confirmed")
    if "create_requested" in marks and "absence_confirmed" in marks:
        out["controller_clock"]["total_wall_s"] = round(
            marks["absence_confirmed"] - marks["create_requested"], 3)

    # Provisioning is the one interval that genuinely spans both clocks:
    # from the controller seeing an accepted create to the pod's shell
    # starting. Reported, and labelled as such.
    if "create_answered" in marks and "boot" in stages:
        out["cross_clock"]["provision_s"] = round(
            stages["boot"] - marks["create_answered"], 3)
        out["cross_clock"]["note"] = (
            "controller instant subtracted from a pod instant; the two "
            "clocks are not synchronised and the offset is not measured here")

    # With a MEASURED offset the cross-clock interval becomes a measurement
    # with an error bar. Iteration 1 could only bound provisioning at <= 24 s
    # because the raw subtraction above assumes the clocks agree.
    if clock_sync and clock_sync.get("offset_s") is not None:
        out["synchronised"] = {
            "offset_s": clock_sync["offset_s"],
            "uncertainty_s": clock_sync["uncertainty_s"],
            "method": clock_sync.get("method"),
        }
        if "create_answered" in marks and "boot" in stages:
            boot_ctl = stages["boot"] - clock_sync["offset_s"]
            out["synchronised"]["provision_s"] = round(
                boot_ctl - marks["create_answered"], 3)
        if "create_answered" in marks and "module_start" in stages:
            out["synchronised"]["accepted_to_module_start_s"] = round(
                stages["module_start"] - clock_sync["offset_s"]
                - marks["create_answered"], 3)

    if telemetry_summary and telemetry_summary.get("elapsed_s"):
        out["module_reported_elapsed_s"] = telemetry_summary["elapsed_s"]
    return out


def estimate_offset(samples):
    """Pod-minus-controller clock offset from (t_send, pod_epoch, t_recv).

    The pod read its clock somewhere inside the round trip, so the offset
    is pod_epoch - midpoint, known to within half the round trip. The
    sample with the SHORTEST round trip gives the tightest bound, which is
    the standard NTP-style estimate. Returns None without usable samples.
    """
    usable = [(t1 - t0, pod - (t0 + t1) / 2.0)
              for t0, pod, t1 in samples
              if pod is not None and t1 >= t0]
    if not usable:
        return None
    rtt, offset = min(usable)
    return {"offset_s": round(offset, 4),
            "uncertainty_s": round(rtt / 2.0, 4),
            "rtt_min_s": round(rtt, 4),
            "samples": len(usable),
            "method": "min-RTT midpoint against the pod's /_clock"}


def summarise_platform(text):
    """Peak and mean of what the platform sampler recorded. Never raises."""
    import json as _json
    recs = []
    for line in str(text or "").splitlines():
        try:
            rec = _json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("kind") == "platform":
            recs.append(rec)
    if not recs:
        return {"samples": 0}

    def gpu_vals(key):
        vals = []
        for r in recs:
            for g in (r.get("gpus") or []):
                if g.get(key) is not None:
                    vals.append(float(g[key]))
        return vals

    def host_vals(key):
        return [float(r[key]) for r in recs if r.get(key) is not None]

    def peak(vals):
        return max(vals) if vals else None

    def mean(vals):
        return round(sum(vals) / len(vals), 4) if vals else None

    mem = gpu_vals("mem_used_mib")
    util = gpu_vals("util_pct")
    avail = host_vals("mem_available_b")
    total = host_vals("mem_total_b")
    costs = host_vals("sample_cost_s")
    free = host_vals("disk_free_b")
    names = sorted({g.get("name") for r in recs for g in (r.get("gpus") or [])
                    if g.get("name")})
    return {
        "samples": len(recs),
        "span_s": round(float(recs[-1].get("t_elapsed_s", 0))
                        - float(recs[0].get("t_elapsed_s", 0)), 3),
        "gpu_names": names,
        "gpu_mem_used_mib_peak": peak(mem),
        "gpu_mem_total_mib": peak(gpu_vals("mem_total_mib")),
        "gpu_util_pct_mean": mean(util),
        "gpu_util_pct_peak": peak(util),
        "gpu_temp_c_peak": peak(gpu_vals("temp_c")),
        "gpu_power_w_peak": peak(gpu_vals("power_w")),
        "gpu_power_w_mean": mean(gpu_vals("power_w")),
        "host_load1_peak": peak(host_vals("load1")),
        "host_mem_used_b_peak": (peak([t - a for t, a in zip(total, avail)])
                                 if total and avail else None),
        "disk_free_b_min": min(free) if free else None,
        "artifact_dir_b_peak": peak(host_vals("artifact_dir_b")),
        "sample_cost_s_mean": mean(costs),
        "sample_cost_s_peak": peak(costs),
        "gpu_errors": sorted({r["gpu_error"] for r in recs
                              if r.get("gpu_error")}),
    }




# ---------------------------------------------------------------- Iteration 3

MANIFEST_PATH = "_manifest"
# How many times one artifact is re-fetched when what arrived does not match
# the size and digest the pod computed for it.
ARTIFACT_FETCH_ATTEMPTS = 3
# The watch poll near the module's expected end. End detection is the
# largest poll-dependent overhead term (Iteration 2: 8.8 s at a 10 s poll,
# 0.39 s at 3 s), and it is only paid once.
TIGHT_POLL_S = 3.0
TIGHTEN_AT = 0.9


class SimulatedCrash(BaseException):
    """TESTS ONLY: the controller process dies here, with no `finally`.

    A real SIGKILL skips every `finally`, so the teardown that protects a
    controller that RAISES does not protect one that is KILLED. This lets a
    test stand in for the kill: the controller stops where it is, its pod
    keeps running, and only the ledger on disk remains. A BaseException, so
    no `except Exception` in this module can swallow it.
    """


class _Instrumented(object):
    """Wraps a provider so every control-plane call is timed and recorded.

    Provider latency is one of the things a long flight has to watch for
    drift, and "the API got slower over an hour" is invisible unless each
    call is on the record. Recording lives here so no call site can forget.
    Anything not wrapped is forwarded unchanged (e.g. `last_fetch`).
    """

    WRAPPED = ("create_pod", "list_pods", "get_pod", "terminate_pod")

    def __init__(self, inner, sink, now):
        self._inner = inner
        self._sink = sink
        self._now = now

    def __getattr__(self, name):
        attr = getattr(self._inner, name)
        if name not in self.WRAPPED:
            return attr

        def call(*a, **k):
            t_wall = self._now()
            t0 = time.perf_counter()
            status, ok = None, False
            try:
                out = attr(*a, **k)
                ok = True
                return out
            except prov.ProviderError as exc:
                status = exc.status
                raise
            finally:
                self._sink.append({"op": name, "t": t_wall,
                                   "dur_s": round(time.perf_counter() - t0, 4),
                                   "ok": ok, "status": status})
        return call


def load_ledger(path):
    import json as _json
    with open(path, "r", encoding="utf-8") as fh:
        return _json.load(fh)


class Controller(object):
    def __init__(self, provider, spec, module_dir, budget_usd,
                 transport_factory=dryrun.local_transport, seat="Aether",
                 poll_s=30.0, ready_timeout_s=900.0, ready_poll_s=None,
                 stall_timeout_s=300.0, artifact_token=None,
                 now=time.time, sleep=time.sleep, log=None,
                 ledger_path=None, crash_hook=None, telemetry_stall_s=None,
                 unreachable_s=600.0, expected_module_s=None,
                 get_every_polls=10, run_id=None, allowed_pod_names=None,
                 ledger_dir=None, should_abort=None):
        self.api_calls = []
        self.raw_provider = provider
        self.provider = _Instrumented(provider, self.api_calls, now)
        self.spec = spec
        self.module_dir = module_dir
        self.budget_usd = float(budget_usd)
        self.transport_factory = transport_factory
        self.seat = seat
        self.poll_s = float(poll_s)
        # The ready wait polls faster than the watch. Iteration 1 polled
        # both at 20 s, and that granularity was most of the uncertainty
        # in its provisioning figure. Polling is a few HTTP reads; the
        # pod bills the same whether or not we ask.
        self.ready_poll_s = float(ready_poll_s if ready_poll_s is not None
                                  else min(self.poll_s, 5.0))
        self.ready_timeout_s = float(ready_timeout_s)
        # How long with NO bootstrap progress before the pod is given up on.
        # This, not the total elapsed time, is what distinguishes a stuck pod
        # from a slow dependency install.
        self.stall_timeout_s = float(stall_timeout_s)
        # The same idea during the watch: how long the module's telemetry
        # may stay byte-for-byte unchanged before the module is called hung.
        # Default: ten of its own declared intervals, never under 5 min.
        interval = float(spec["telemetry"].get("interval_s", 15))
        self.telemetry_stall_s = float(
            telemetry_stall_s if telemetry_stall_s is not None
            else max(300.0, 10.0 * interval))
        # How long the pod's server may be unreachable DURING the watch
        # before the controller stops waiting. Early in a run None is
        # normal; once telemetry has been seen, a long silence is not.
        self.unreachable_s = float(unreachable_s)
        self.expected_module_s = (float(expected_module_s)
                                  if expected_module_s else None)
        self.get_every_polls = max(1, int(get_every_polls))
        self.artifact_token = artifact_token
        self._now = now
        self._sleep = sleep
        self._log = log or (lambda m: None)
        self.ledger_path = ledger_path
        # A directory instead of a path: the ledger is named by the run id,
        # which is only known once the run is planned.
        self.ledger_dir = ledger_dir
        self.crash_hook = crash_hook
        # A campaign's fail-fast signal. None (the default) means a sibling's
        # failure never stops this run.
        self.should_abort = should_abort
        self._crashed = False
        self.pod_id = None
        self.pod_name = None
        self.run_id = run_id
        # Names of OTHER pods this controller may see without refusing:
        # siblings in a fan-out. Anything else in the account refuses.
        self.allowed_pod_names = set(allowed_pod_names or ())
        self.creation_outcome = None
        self.telemetry_text = ""
        # Controller-clock instants. Kept apart from pod-clock stages,
        # because an interval spanning both is not a measurement.
        self.marks = {}
        self.create_attempts = []
        self.gpu_used = None
        self.stages_seen = {}
        self.stages_retrieved = {}
        self.clock_sync = None
        self.clock_sync_end = None
        self.platform_text = ""
        # Retrieved bytes, kept so a caller can store the evidence itself.
        # The receipt carries only size and digest.
        self.artifact_blobs = {}
        # One record per watch poll: the controller's own health, so a
        # long flight can show whether the CONTROLLER drifted.
        self.health = []
        self.disposition = None
        self.resumed = None
        self.started = None
        self.provider_view = {}
        self._ledger_state = None
        self.module_rc = None
        self.bundle_sha256 = None
        # Clock measurements attempted. Flight F2's proxy answered the
        # stage file but not /_clock in the first seconds, the controller
        # never asked again, and a whole run lost its clock sync.
        self._clock_tries = 0
        self.stock_at_launch = None
        # Platform samples and stages are snapshotted every this many
        # watch polls (~a minute at a 10 s poll).
        self.snapshot_every_polls = 6

    # ------------------------------------------------------------ helpers
    def _hourly(self):
        """The rate for the GPU that actually ran.

        Falling back to an alternative changes the price, so billing the
        requested card would misreport the cost of every run that did not
        get its first choice.
        """
        gpu = self.spec["gpu"]
        gpu_id = self.gpu_used or gpu.get("class")
        return cost_mod.hourly_for(gpu_id) * int(gpu.get("count", 1))

    def _fetch_bytes(self, path):
        """None means unreachable, which early in a run is the normal answer.

        A fetch never raises out of here. Losing a run because a poll was
        early, or because the proxy hiccuped once, would be absurd.
        """
        t_wall = self._now()
        t0 = time.perf_counter()
        blob = None
        try:
            blob = self.raw_provider.fetch(self.pod_id, path,
                                           token=self.artifact_token)
        except Exception as exc:
            self._log("fetch %s raised %s; treating as unreachable"
                      % (path, type(exc).__name__))
            blob = None
        self.api_calls.append({"op": "fetch", "path": str(path), "t": t_wall,
                               "dur_s": round(time.perf_counter() - t0, 4),
                               "ok": blob is not None,
                               "bytes": (len(blob) if blob is not None
                                         else None)})
        if blob is None:
            return None
        return blob if isinstance(blob, bytes) else blob.encode("utf-8")

    def _fetch(self, path):
        blob = self._fetch_bytes(path)
        return None if blob is None else blob.decode("utf-8", "replace")

    # ------------------------------------------------------------ ledger
    def _ledger(self, event, **fields):
        """Durable controller state, written atomically at every transition.

        The receipt is written at the END. A controller killed in the middle
        leaves no receipt, and without this file nothing on disk would say
        which pod it owned or how to read that pod's artifacts. The ledger
        holds the artifact token, so it lives outside the repository
        (`.ledger/`, gitignored) and never goes into a receipt.
        """
        if self._ledger_state is None:
            self._ledger_state = {
                "schema": "prometheus-gpu/ledger/1",
                "run_id": self.run_id, "pod_name": self.pod_name,
                "module": getattr(self.spec, "identity", None),
                "events": []}
        st = self._ledger_state
        st.update({"pod_id": self.pod_id,
                   "creation_outcome": self.creation_outcome,
                   "gpu_used": self.gpu_used, "started": self.started,
                   "marks": dict(self.marks),
                   "artifact_token": self.artifact_token,
                   "bundle_sha256": self.bundle_sha256,
                   "budget_usd": self.budget_usd})
        st.update(fields)
        st["events"].append({"event": event, "t": self._now()})
        if self.ledger_path is None and self.ledger_dir and self.run_id:
            import os as _os
            self.ledger_path = _os.path.join(self.ledger_dir,
                                             "%s.json" % self.run_id)
        if self.ledger_path:
            import json as _json
            import os as _os
            folder = _os.path.dirname(_os.path.abspath(self.ledger_path))
            _os.makedirs(folder, exist_ok=True)
            tmp = self.ledger_path + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                _json.dump(st, fh, indent=1, sort_keys=True)
                fh.write("\n")
            _os.replace(tmp, self.ledger_path)
        if self.crash_hook is not None:
            self.crash_hook(event)

    # -------------------------------------------------------- preconditions
    def preflight(self):
        """Refuse before spending. `LaunchRefused` means nothing exists."""
        try:
            pods = self.provider.list_pods()
        except prov.ProviderError as exc:
            raise LaunchRefused(
                "inventory read failed (status=%s). Refusing to create: a "
                "failed listing is indistinguishable from an empty account, "
                "and launching blind is how a second pod starts billing "
                "beside one nobody can see." % (exc.status,))
        foreign = [p for p in pods
                   if p.get("name") not in self.allowed_pod_names]
        if foreign:
            raise LaunchRefused(
                "%d pod(s) already active (%s). One pod at a time; terminate "
                "or adopt before launching."
                % (len(foreign), ", ".join(str(p.get("id")) for p in foreign)))
        return True

    # ------------------------------------------------------------- the run
    def run(self):
        self.preflight()

        # The plan is what gets recorded; the request is what gets sent.
        # They are built together, from the same inputs, so the receipt
        # describes the run that actually happened rather than a
        # reconstruction of it.
        plan, request, run_meta, _built = dryrun.prepare(
            self.spec, self.module_dir, inventory=self.provider.list_pods,
            transport_factory=self.transport_factory, seat=self.seat,
            run_id=self.run_id)
        secrets_mod.assert_no_credentials(request["env"],
                                          where="pod request env at launch")
        # The pod's artifact server is generated with a per-run token. The
        # controller has to hold the same one to read anything back, and
        # taking it from the plan means the two cannot drift apart.
        if self.artifact_token is None:
            self.artifact_token = run_meta.get("artifact_token")
        self.run_id = plan["run_id"]
        self.pod_name = request["name"]
        self.bundle_sha256 = plan["bundle"]["bundle_sha256"]

        receipt_obj = rc.from_plan(plan, result="NOT_RUN")
        self.started = self._now()
        receipt_obj["started_utc"] = rc._utc(self.started)
        result = "UNKNOWN"
        try:
            self._ledger("planned")
            self.pod_id, self.creation_outcome = self._create(request)
            self._ledger("created")
            if self.pod_id is None and self.creation_outcome == "unknown":
                # A create whose outcome could not be resolved. A pod may
                # exist and we do not have its id, so this is the one case
                # that must NOT be reported as a clean non-event.
                result = "UNKNOWN"
                self.disposition = "CREATE_UNRESOLVED"
                receipt_obj["notes"].append(
                    "create outcome unresolved and inventory unreadable; a "
                    "pod may exist that this controller cannot name. "
                    "RECONCILE MANUALLY before creating anything else.")
            elif self.pod_id is None:
                result = "NOT_RUN"
                refused = [a["gpu_id"] for a in self.create_attempts]
                if all(a["outcome"] == "FAILED_CLEAN"
                       for a in self.create_attempts) and refused:
                    self.disposition = "NO_CAPACITY"
                    receipt_obj["notes"].append(
                        "no capacity for any declared GPU (%s); provider "
                        "confirms nothing exists. Declare more "
                        "gpu.alternatives or try again later."
                        % ", ".join(refused))
                    # The qualified client discards the 400 body, so every
                    # card refusing cleanly is also what a MALFORMED request
                    # looks like. Iteration 3 flight F2b: a direct probe of
                    # the identical body read the provider's own words
                    # ("no longer any instances available"); nothing here
                    # did. FAILURE_PLAYBOOK 23.
                    receipt_obj["notes"].append(
                        "capacity is INFERRED from every create failing "
                        "cleanly with a 4xx; the response bodies were not "
                        "read, so a request the provider rejects as invalid "
                        "would look identical. Confirm with a direct probe "
                        "of the same body before changing the request.")
                else:
                    self.disposition = "CREATE_FAILED_CLEAN"
                    receipt_obj["notes"].append(
                        "create failed cleanly; provider confirms nothing "
                        "exists")
                receipt_obj["notes"].append(
                    "absence of a created pod rests on two LIST reads that "
                    "showed none named %s; a pod omitted from every LIST "
                    "cannot be excluded without its id" % self.pod_name)
            else:
                result = self._drive(receipt_obj, resumed=False)
        except LaunchRefused:
            raise
        except SimulatedCrash:
            self._crashed = True
            raise
        except Exception as exc:
            result = "UNKNOWN"
            self.disposition = self.disposition or "CONTROLLER_ERROR"
            receipt_obj["notes"].append(
                "controller raised %s: %s" % (type(exc).__name__, exc))
            self._log("controller raised %s; proceeding to teardown"
                      % type(exc).__name__)
        finally:
            if not self._crashed:
                self._finish(receipt_obj, result)
        rc.validate(receipt_obj)
        return receipt_obj

    def resume(self, ledger):
        """Pick up a run whose controller died, from its ledger alone.

        Never creates. Establishes, before touching anything, that the pod
        the ledger names still exists AND is ours by name; a pod id that
        now answers to a different name is somebody else's and is left
        alone. Then continues from where the ledger stopped: wait for the
        pod if telemetry was never seen, otherwise watch; then retrieve,
        terminate and write the receipt as a normal run would.

        Cost is counted from the ORIGINAL start, because the pod billed
        through the gap while no controller was watching it.
        """
        self.run_id = ledger["run_id"]
        self.pod_name = ledger["pod_name"]
        self.pod_id = ledger.get("pod_id")
        self.creation_outcome = ledger.get("creation_outcome") or "unknown"
        self.gpu_used = ledger.get("gpu_used")
        self.artifact_token = ledger.get("artifact_token")
        self.started = float(ledger["started"])
        self.marks = {k: float(v) for k, v in (ledger.get("marks") or {}).items()}
        last_event = (ledger.get("events") or [{}])[-1]
        gap_from = float(last_event.get("t", self.started))
        self._ledger_state = dict(ledger)
        self._ledger_state["events"] = list(ledger.get("events") or [])
        if self.pod_id is None:
            raise LaunchRefused("the ledger names no pod; nothing to resume. "
                                "If its create was ambiguous, reconcile the "
                                "inventory by name %r manually" % self.pod_name)

        plan, _request, _meta, _built = dryrun.prepare(
            self.spec, self.module_dir, inventory=None,
            transport_factory=self.transport_factory, seat=self.seat,
            run_id=self.run_id)
        receipt_obj = rc.from_plan(plan, result="NOT_RUN")
        receipt_obj["started_utc"] = rc._utc(self.started)
        # The bytes that RAN are the ledger's, not whatever the module
        # directory holds now.
        self.bundle_sha256 = ledger.get("bundle_sha256")
        if self.bundle_sha256 and (self.bundle_sha256
                                   != receipt_obj["bundle_sha256"]):
            receipt_obj["notes"].append(
                "the module directory now builds %s; the pod ran %s (from the "
                "ledger), which is what this receipt reports"
                % (receipt_obj["bundle_sha256"][:12], self.bundle_sha256[:12]))
            receipt_obj["bundle_sha256"] = self.bundle_sha256
        resumed_at = self._now()
        self.resumed = {"ledger_last_event": last_event.get("event"),
                        "controller_absent_s": round(resumed_at - gap_from, 3),
                        "resumed_utc": rc._utc(resumed_at)}
        receipt_obj["resumed"] = self.resumed
        self._log("RESUME %s pod=%s after %.0f s without a controller"
                  % (self.run_id, self.pod_id, resumed_at - gap_from))
        # Ownership is settled BEFORE anything that can reach the teardown.
        # A refusal raised inside the try below would still run `_finish`,
        # and `_finish` terminates -- which is how a resume that correctly
        # decided a pod was not ours went on to terminate it anyway (caught
        # by test_resume_leaves_alone_a_pod_that_is_no_longer_ours).
        pod, readable = None, False
        for _ in range(3):
            try:
                pod = self.provider.get_pod(self.pod_id)
                readable = True
                break
            except prov.ProviderError:
                self._sleep(self.ready_poll_s)
        if not readable:
            raise LaunchRefused(
                "GET for pod %s failed three times; cannot establish whether "
                "it exists or whose it is. Nothing was touched." % self.pod_id)
        if pod is not None and pod.get("name") not in (None, self.pod_name):
            raise LaunchRefused(
                "pod %s now answers to name %r, not %r: not ours; left "
                "untouched" % (self.pod_id, pod.get("name"), self.pod_name))
        result = "UNKNOWN"
        try:
            self._ledger("resumed")
            if pod is None:
                self.disposition = "POD_GONE_BEFORE_RESUME"
                receipt_obj["notes"].append(
                    "resumed from the ledger but GET no longer returns pod %s; "
                    "its artifacts cannot be retrieved. Absence is checked "
                    "below by LIST and GET together." % self.pod_id)
                result = "UNKNOWN"
            else:
                result = self._drive(receipt_obj, resumed=True)
        except LaunchRefused:
            raise
        except SimulatedCrash:
            self._crashed = True
            raise
        except Exception as exc:
            result = "UNKNOWN"
            self.disposition = self.disposition or "CONTROLLER_ERROR"
            receipt_obj["notes"].append(
                "controller raised %s: %s" % (type(exc).__name__, exc))
        finally:
            if not self._crashed:
                self._finish(receipt_obj, result)
        rc.validate(receipt_obj)
        return receipt_obj

    def _drive(self, receipt_obj, resumed):
        """Ready -> watch -> retrieve, for a pod this controller holds."""
        if "first_telemetry" in self.marks and resumed:
            result = self._watch(self.started)
        else:
            ready = self._await_ready(self.started)
            if not ready:
                result = "FAILED"
                self.disposition = self.disposition or "NEVER_READY"
                receipt_obj["notes"].append(
                    "pod never served telemetry; furthest bootstrap stage "
                    "reached was %s" % (self.last_stage() or "none"))
            else:
                self._ledger("first_telemetry")
                result = self._watch(self.started)
        self._ledger("watch_end", result=result, disposition=self.disposition)
        self._retrieve(receipt_obj)
        self._ledger("retrieved")
        return result

    def _finish(self, receipt_obj, result):
        """Teardown and the receipt's accounting. Runs on every path except
        a (simulated) kill, exactly as a `finally` does for a real process."""
        ended = self._now()
        started = self.started if self.started is not None else ended
        receipt_obj["ended_utc"] = rc._utc(ended)
        pods, inventory_ok = self._teardown()
        receipt_obj["pods"] = pods
        receipt_obj["cleanup"] = rc.cleanup_block(pods, inventory_ok)
        confirmed_nothing = (self.pod_id is None
                             and self.creation_outcome != "unknown")
        # A pod the provider confirms was never created bills nothing,
        # so the controller's own wall time is not a cost. An
        # UNRESOLVED create keeps its wall-time estimate: a pod may
        # exist, and pricing it at zero would hide that.
        receipt_obj["cost"] = cost_mod.actual(
            0.0 if confirmed_nothing else max(0.0, ended - started),
            self._hourly(), work_units=self._work_units(receipt_obj))
        if confirmed_nothing:
            receipt_obj["cost"]["basis"] = (
                "no pod existed (provider confirmed); nothing to bill")
            # Nothing ran, so nothing is MISSING: the artifacts were never
            # going to exist. Iteration 2's NOT_RUN receipts listed every
            # declared artifact as missing, which reads as a failed
            # retrieval.
            receipt_obj["artifacts_missing"] = []
        # Only a create the provider CONFIRMED created nothing may be
        # downgraded to NOT_RUN here. An unresolved create also has no
        # pod id, and calling that a non-event is how a pod that may
        # be billing disappears from the record.
        receipt_obj["result"] = "NOT_RUN" if confirmed_nothing else result
        receipt_obj["artifacts_expected"] = list(self.spec["artifacts"])
        receipt_obj["telemetry_summary"] = self._telemetry_summary()
        receipt_obj["create_attempts"] = self.create_attempts
        receipt_obj["stock_at_launch"] = self.stock_at_launch
        receipt_obj["last_stage"] = self.last_stage()
        receipt_obj["gpu_used"] = self.gpu_used
        receipt_obj["lifecycle"] = lifecycle(
            self.marks, receipt_obj.get("pod_stages"),
            receipt_obj.get("telemetry_summary"),
            clock_sync=self.clock_sync)
        receipt_obj["clock_sync"] = {"start": self.clock_sync,
                                     "end": self.clock_sync_end}
        receipt_obj["ready_poll_s"] = self.ready_poll_s
        receipt_obj["api_latency"] = summarise_api(self.api_calls)
        receipt_obj["controller_health"] = summarise_health(self.health)
        receipt_obj["disposition"] = self._disposition(receipt_obj)
        self._ledger("done", result=receipt_obj["result"])

    def _telemetry_summary(self):
        if not self.telemetry_text:
            return tel_mod.summarise([])
        try:
            return tel_mod.summarise(tel_mod.read_jsonl(self.telemetry_text,
                                                        is_text=True))
        except tel_mod.TelemetryError as exc:
            return {"records": 0, "complete": False,
                    "note": "telemetry unreadable: %s" % exc}

    def _disposition(self, r):
        """The six questions every failure has to answer, in one block.

        1 what the controller believes, 2 what the provider believes,
        3 what evidence was retained, 4 whether the run can resume, 5 whether
        cleanup is safe, 6 which statements are ABSENCE and which are only
        UNCERTAINTY. Derived from the receipt's own facts, never written by
        hand.
        """
        pods = r.get("pods") or []
        pod = pods[0] if pods else None
        ev = (pod or {}).get("absence_evidence") or {}
        integ = r.get("artifact_integrity") or {}
        tel = r.get("telemetry_summary") or {}
        cleanup = r.get("cleanup") or {}
        if pod is None:
            pod_state = ("never created (provider confirmed by LIST)"
                         if r["result"] == "NOT_RUN" else "unknown")
        elif pod.get("observed_absent"):
            pod_state = "ABSENT: LIST omits it and GET returns nothing"
        elif ev.get("list_omits") and ev.get("get_absent") is False:
            pod_state = "UNCERTAIN: LIST omits it but GET still returns it"
        elif ev.get("list_omits") is False and ev.get("get_absent"):
            pod_state = "UNCERTAIN: GET says gone but LIST still shows it"
        else:
            pod_state = "UNCERTAIN: absence not established"
        return {
            "cause": self.disposition or r["result"],
            "controller_believes": {
                "result": r["result"],
                "pod_id": self.pod_id,
                "terminate_acknowledged": bool(
                    (pod or {}).get("terminate_acknowledged")),
            },
            "provider_believes": dict(self.provider_view),
            "evidence_retained": {
                "telemetry_records": tel.get("records", 0),
                "telemetry_complete": tel.get("complete", False),
                "platform_samples": (r.get("platform_summary") or {}).get(
                    "samples", 0),
                "artifacts_verified": integ.get("verified", []),
                "artifacts_unverified": integ.get("unverified", []),
                "artifacts_corrupt": integ.get("mismatch", []),
                "artifacts_missing": r.get("artifacts_missing", []),
                "ledger": bool(self.ledger_path),
            },
            "resumable": bool(self.ledger_path and pod is not None
                              and not pod.get("observed_absent")),
            "cleanup_safe": bool(cleanup.get("operational_cleanup")),
            "pod_state": pod_state,
            "resumed": self.resumed,
        }

    # ------------------------------------------------------------- stages
    # Provider labels to receipt vocabulary. The mapping is explicit
    # because flattening ADOPTED into confirmed would erase a near miss,
    # and flattening AMBIGUOUS_UNRECONCILED into a clean failure would
    # hide a pod that may be billing.
    _OUTCOMES = {"CREATED": "confirmed",
                 "ADOPTED": "adopted",
                 "AMBIGUOUS_UNRECONCILED": "unknown",
                 "FAILED_CLEAN": None,
                 # Every declared GPU was refused for capacity. The
                 # provider confirmed nothing exists, so this is a clean
                 # non-event -- but a distinct one, because the fix is to
                 # ask for a different card, not to debug the request.
                 "NO_CAPACITY": None}

    def _mark(self, name):
        self.marks[name] = self._now()

    def gpu_candidates(self):
        """The declared GPU, then its declared alternatives, in order --
        reordered by advertised stock when the provider can say.

        Stable: within a stock level the declared order is kept, and a card
        with unknown stock keeps its place after the in-stock ones. Nothing
        is ever dropped, because advertised stock is advice, not a promise.
        """
        gpu = self.spec["gpu"]
        out = [gpu.get("class")]
        for alternative in gpu.get("alternatives", []):
            if alternative not in out:
                out.append(alternative)
        out = [g for g in out if g]
        probe = getattr(self.raw_provider, "stock_status", None)
        if probe is None or len(out) < 2:
            return out
        try:
            stock = probe(out) or {}
        except Exception:
            stock = {}
        self.stock_at_launch = stock
        rank = {"High": 0, "Medium": 1, "Low": 2}
        reordered = sorted(out, key=lambda g: rank.get(stock.get(g), 3))
        if reordered != out:
            self._log("advertised stock %s -> trying %s first"
                      % (stock, reordered[0]))
        return reordered

    def _create(self, request):
        self._mark("create_requested")
        candidates = self.gpu_candidates()
        pod, label, attempts = prov.create_with_alternatives(
            self.provider, request, candidates, log=self._log,
            sleep=self._sleep)
        self._mark("create_answered")
        self.create_attempts = attempts
        outcome = self._OUTCOMES.get(label, "unknown")
        pod_id = pod.get("id") if isinstance(pod, dict) else pod
        if pod_id is not None:
            # Record which GPU actually ran, not which one was asked for.
            for attempt in attempts:
                if attempt["outcome"] in ("CREATED", "ADOPTED"):
                    self.gpu_used = attempt["gpu_id"]
        self._log("create %s -> %s pod=%s gpu=%s"
                  % (label, outcome, pod_id, getattr(self, "gpu_used", None)))
        if pod_id is None:
            return None, outcome
        return pod_id, outcome

    def _await_ready(self, started):
        """Wait on PROGRESS, not on a fixed clock.

        Iteration 1's fifth flight reported "pod never reported ready within
        300 s" when the pod was healthy and had simply not finished
        installing a 1 GB CUDA wheel. A fixed deadline cannot tell a slow
        dependency install from a dead pod, so it calls both dead and throws
        away the one that was about to work.

        The pod emits a stage marker after each bootstrap step, so the
        controller can see where it is. While stages keep advancing it keeps
        waiting; it gives up when nothing has advanced for `stall_timeout_s`,
        or at the hard ceiling, and it says which stage it got to.
        """
        deadline = started + self.ready_timeout_s
        last_progress = self._now()
        reported = set()
        while self._now() < deadline:
            if self._fetch(TELEMETRY_PATH) is not None:
                if "first_contact" not in self.marks:
                    self._mark("first_contact")
                self._mark("first_telemetry")
                self._try_clock()
                return True

            stages_text = self._fetch(STAGES_PATH)
            if stages_text is not None:
                if "first_contact" not in self.marks:
                    self._mark("first_contact")
                self._try_clock()
                stages = parse_stages(stages_text)
                self.stages_seen = stages
                fresh = [st for st in STAGE_ORDER
                         if st in stages and st not in reported]
                for st in fresh:
                    reported.add(st)
                    self._log("stage %s" % st)
                if fresh:
                    last_progress = self._now()
                if "restart" in stages:
                    self._log("the pod's container RESTARTED during bootstrap")
                    self.disposition = "CONTAINER_RESTARTED"
                    return False
                if "module_end" in stages:
                    # The module ran and exited before it ever wrote
                    # telemetry. Nothing more will come; stop waiting.
                    self._log("module ended before any telemetry (rc=%s)"
                              % stages.get("module_rc"))
                    self.disposition = "MODULE_EXITED_WITHOUT_TELEMETRY"
                    return False
            else:
                last = getattr(self.raw_provider, "last_fetch", None)
                if last and "no-server" not in reported:
                    reported.add("no-server")
                    self._log("artifact server not answering yet (status=%s)"
                              % last.get("status"))

            stalled = self._now() - last_progress
            if stalled >= self.stall_timeout_s:
                self._log("STALLED: no stage advanced for %.0f s; last stage "
                          "was %s" % (stalled, self.last_stage() or "none"))
                self.disposition = "BOOTSTRAP_STALLED"
                return False
            try:
                if self.provider.get_pod(self.pod_id) is None:
                    self._log("pod vanished before it was ready")
                    self.disposition = "POD_VANISHED"
                    return False
            except prov.ProviderError:
                pass            # a control-plane blip is not a verdict
            self._sleep(self.ready_poll_s)
        self._log("ready ceiling %.0f s reached; last stage was %s"
                  % (self.ready_timeout_s, self.last_stage() or "none"))
        self.disposition = "READY_CEILING"
        return False

    def _try_clock(self, max_tries=6):
        """Measure the pod clock if it is still unknown, a bounded number of
        times in all. Each attempt is CLOCK_SAMPLES fetches."""
        if self.clock_sync is None and self._clock_tries < max_tries:
            self._clock_tries += 1
            self.clock_sync = self.measure_clock()

    def measure_clock(self, samples=CLOCK_SAMPLES):
        """Pod clock offset, measured, with its uncertainty. Never raises.

        Uses the controller's own `now`, so under a fake clock it is as
        deterministic as everything else here.
        """
        import json as _json
        rows = []
        for _ in range(samples):
            t0 = self._now()
            text = self._fetch(CLOCK_PATH)
            t1 = self._now()
            pod = None
            if text is not None:
                try:
                    pod = float(_json.loads(text)["epoch"])
                except (ValueError, KeyError, TypeError):
                    pod = None
            rows.append((t0, pod, t1))
        found = estimate_offset(rows)
        if found:
            self._log("pod clock offset %+.3f s (+/- %.3f s)"
                      % (found["offset_s"], found["uncertainty_s"]))
        else:
            self._log("pod clock unavailable; provisioning stays cross-clock")
        return found

    def last_stage(self, stages=None):
        """The furthest bootstrap stage the pod reported reaching.

        Prefers stages RETRIEVED at the end over those merely seen while
        waiting: a pod that became ready on the first poll never had its
        stages read during the wait, and reported None despite having them.
        """
        known = stages or self.stages_retrieved or self.stages_seen or {}
        reached = [st for st in STAGE_ORDER if st in known]
        return reached[-1] if reached else None

    def _module_exit(self):
        """(ended, rc, restarted) from the pod's stage file.

        `restarted` means the bootstrap's restart guard fired: the
        container's main process died, RunPod restarted the container, and
        the module is NOT running any more (the guard stops it re-running).
        """
        text = self._fetch(STAGES_PATH)
        if text is None:
            return False, None, False
        stages = parse_stages(text)
        self.stages_seen = stages
        if "restart" in stages:
            return False, None, True
        if "module_end" not in stages:
            return False, None, False
        rc_val = stages.get("module_rc")
        return True, (int(rc_val) if rc_val is not None else None), False

    def _watch(self, started):
        """Poll until the module finishes, the budget runs out, or time does.

        Iteration 3 adds four ways out that the Iteration 2 watch did not
        have, each of which used to end only at the budget or runtime cap:

          the module EXITED without an `end` record (crash, non-zero exit):
              seen in the pod's stage file, which the shell writes whatever
              the module does;
          the module HUNG: telemetry byte-for-byte unchanged for
              `telemetry_stall_s`, with no exit in the stage file;
          the SERVER went away: nothing readable for `unreachable_s` after
              telemetry had been seen, while GET still returns the pod;
          the POD went away: GET returns nothing (checked every
              `get_every_polls` polls, and whenever the server is silent).
        """
        hourly = self._hourly()
        runtime_cap = float(self.spec["max_runtime_s"])
        # `max_runtime_s` bounds the MODULE, which is what the cost model
        # prices it as (compute + overhead, added separately). It used to
        # be measured from the create, so a bootstrap that spent 305 s
        # installing wheels -- observed in Iteration 1 -- ate the module's
        # whole allowance, and a scout (whose bound is a small fraction of
        # its campaign's) would have timed out before running at all.
        # Money is bounded separately and from the create: the budget.
        module_origin = self.marks.get("first_telemetry", started)
        last_change = self._now()
        last_digest = None
        silent_since = None
        polls = 0
        while True:
            loop_t0 = time.perf_counter()
            now = self._now()
            elapsed = now - started
            spend = elapsed / 3600.0 * hourly
            if spend >= self.budget_usd:
                self._log("BUDGET CEILING $%.4f >= $%.4f after %.0f s"
                          % (spend, self.budget_usd, elapsed))
                self.disposition = "BUDGET_CEILING"
                return "ABORTED"
            if now - module_origin >= runtime_cap:
                self._log("max_runtime_s %.0f reached" % runtime_cap)
                self.disposition = "MAX_RUNTIME"
                return "TIMEOUT"
            if self.should_abort is not None and self.should_abort():
                self._log("campaign fail-fast: a sibling failed; stopping")
                self.disposition = "CAMPAIGN_FAIL_FAST"
                return "ABORTED"
            polls += 1
            text = self._fetch(TELEMETRY_PATH)
            records = None
            if text is not None:
                silent_since = None
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if digest != last_digest:
                    last_digest = digest
                    last_change = self._now()
                self.telemetry_text = text
                try:
                    records = tel_mod.read_jsonl(text, is_text=True)
                except tel_mod.TelemetryError as exc:
                    # A corrupted read (mid-transfer) is a bad read, not a
                    # verdict on the run. Keep polling.
                    self._log("telemetry unreadable this poll: %s" % exc)
                    records = None
                if records is not None:
                    ends = [r for r in records if r.get("kind") == "end"]
                    if ends:
                        status = str(ends[-1].get("status", "")).lower()
                        self._log("module reported end (status=%s)" % status)
                        ok = status in ("ok", "success", "")
                        self.disposition = ("OK" if ok
                                            else "MODULE_REPORTED_FAILURE")
                        self._health(polls, now, spend, text, loop_t0)
                        return "OK" if ok else "FAILED"
                    if [r for r in records if r.get("kind") == "error"]:
                        self._log("module reported an error record")
            else:
                if silent_since is None:
                    silent_since = self._now()

            ended, rc_val, restarted = self._module_exit()
            if restarted:
                self._log("the pod's container RESTARTED; the module is not "
                          "running and what it wrote before is all there is")
                self.disposition = "CONTAINER_RESTARTED"
                return "UNKNOWN"
            if ended:
                # Re-read once: the module may have written `end` and
                # exited between the two fetches of this poll.
                again = self._fetch(TELEMETRY_PATH)
                if again is not None:
                    self.telemetry_text = again
                    try:
                        recs = tel_mod.read_jsonl(again, is_text=True)
                    except tel_mod.TelemetryError:
                        recs = []
                    ends = [r for r in recs if r.get("kind") == "end"]
                    if ends:
                        status = str(ends[-1].get("status", "")).lower()
                        ok = status in ("ok", "success", "") and rc_val in (
                            0, None)
                        self.disposition = ("OK" if ok else
                                            "MODULE_REPORTED_FAILURE")
                        return "OK" if ok else "FAILED"
                self._log("module EXITED rc=%s without an end record" % rc_val)
                self.disposition = "MODULE_EXITED_WITHOUT_END"
                self.module_rc = rc_val
                return "FAILED"

            if (silent_since is not None
                    and self._now() - silent_since >= self.unreachable_s):
                exists = self._pod_exists()
                if exists is False:
                    self._log("pod VANISHED during the watch")
                    self.disposition = "POD_VANISHED"
                else:
                    self._log("artifact server UNREACHABLE for %.0f s while "
                              "the pod still exists" % (self._now()
                                                        - silent_since))
                    self.disposition = "ARTIFACT_SERVER_UNREACHABLE"
                return "UNKNOWN"
            if (silent_since is None and last_digest is not None
                    and self._now() - last_change >= self.telemetry_stall_s):
                self._log("telemetry unchanged for %.0f s and no module exit: "
                          "HUNG" % (self._now() - last_change))
                self.disposition = "TELEMETRY_STALLED"
                return "ABORTED"
            if polls % self.get_every_polls == 0:
                if self._pod_exists() is False:
                    self._log("pod VANISHED during the watch (GET)")
                    self.disposition = "POD_VANISHED"
                    return "UNKNOWN"
            if self.clock_sync is None and polls % 3 == 0:
                self._try_clock()
            if polls % self.snapshot_every_polls == 0:
                self._snapshot()
            self._health(polls, now, spend, text, loop_t0)
            self._ledger("watch", spend_usd=round(spend, 5))
            wait = self.poll_s
            if (self.expected_module_s and
                    self._now() - module_origin
                    >= TIGHTEN_AT * self.expected_module_s):
                wait = min(wait, TIGHT_POLL_S)
            self._sleep(wait)

    def _snapshot(self):
        """Keep the platform samples and stage file current DURING the run.

        They used to be read only at retrieval, so a server that died
        mid-run took every platform sample with it (flight F2c: telemetry
        up to the fault was kept, platform samples were zero). A snapshot is
        replaced only by a longer one, so a truncated read never shrinks
        what is held.
        """
        platform = self._fetch(PLATFORM_PATH)
        if platform is not None and len(platform) >= len(self.platform_text):
            self.platform_text = platform
        stages = self._fetch(STAGES_PATH)
        if stages:
            parsed = parse_stages(stages)
            if len(parsed) >= len(self.stages_retrieved):
                self.stages_retrieved = parsed

    def _pod_exists(self):
        """True/False from GET, or None when GET itself failed."""
        try:
            return self.provider.get_pod(self.pod_id) is not None
        except prov.ProviderError:
            return None

    def _health(self, polls, now, spend, text, loop_t0):
        self.health.append({
            "poll": polls, "t": now,
            "elapsed_s": round(now - self.started, 3),
            "spend_usd": round(spend, 6),
            "telemetry_bytes": len(text) if text is not None else None,
            "loop_s": round(time.perf_counter() - loop_t0, 4),
            "api_calls": len(self.api_calls),
        })

    def _retrieve(self, receipt_obj):
        """Before teardown, always. A dead pod hands back nothing.

        Iteration 3: every artifact is checked against the size and sha256
        the pod itself computes (`/_manifest`), re-fetched on mismatch, and
        filed as VERIFIED, UNVERIFIED (no pod-side digest to check it
        against: uncertainty) or MISMATCH (arrived, and is not what the pod
        holds: corrupt or truncated). Missing (absent) stays its own list.
        """
        import json as _json
        self._mark("retrieve_start")
        self._snapshot()
        if self.stages_retrieved:
            receipt_obj["pod_stages"] = self.stages_retrieved
        text = self._fetch(TELEMETRY_PATH)
        if text is not None:
            self.telemetry_text = text
        receipt_obj["platform_summary"] = summarise_platform(
            self.platform_text)

        def manifest():
            raw = self._fetch(MANIFEST_PATH)
            if raw is None:
                return None
            try:
                return (_json.loads(raw) or {}).get("files") or {}
            except ValueError:
                return None

        files = manifest()
        got, missing = [], []
        integrity = {"verified": [], "unverified": [], "mismatch": []}
        for path in self.spec["artifacts"]:
            record = None
            for attempt in range(1, ARTIFACT_FETCH_ATTEMPTS + 1):
                t0 = self._now()
                blob = self._fetch_bytes(path)
                t1 = self._now()
                if blob is None:
                    continue
                digest = hashlib.sha256(blob).hexdigest()
                record = {"path": path, "bytes": len(blob), "sha256": digest,
                          "fetch_s": round(t1 - t0, 4), "attempts": attempt}
                expected = (files or {}).get(path)
                if expected is None:
                    record["integrity"] = "unverified"
                    self.artifact_blobs[path] = blob
                    break
                if (expected.get("bytes") == len(blob)
                        and expected.get("sha256") == digest):
                    record["integrity"] = "verified"
                    self.artifact_blobs[path] = blob
                    break
                record["integrity"] = "mismatch"
                record["expected"] = {"bytes": expected.get("bytes"),
                                      "sha256": expected.get("sha256")}
                self._log("artifact %s MISMATCH on attempt %d (%d vs %s bytes); "
                          "re-fetching" % (path, attempt, len(blob),
                                           expected.get("bytes")))
                # The file may still be being written: ask the pod again.
                files = manifest() or files
            if record is None:
                missing.append(path)
                continue
            if record["integrity"] == "mismatch":
                # Kept as evidence of what arrived, never as the artifact.
                self.artifact_blobs[path + ".mismatch"] = blob
            got.append(record)
            integrity[record["integrity"]].append(path)
        self._mark("retrieve_end")
        if self.clock_sync is not None:
            # A second offset at the end bounds the drift over the run.
            self.clock_sync_end = self.measure_clock()
        receipt_obj["artifacts"] = got
        receipt_obj["artifacts_missing"] = missing
        receipt_obj["artifact_integrity"] = dict(
            integrity, manifest_available=files is not None)
        receipt_obj["artifact_bytes_total"] = sum(a["bytes"] for a in got)
        fetch_s = sum(a["fetch_s"] for a in got)
        largest = max(got, key=lambda a: a["bytes"]) if got else None
        receipt_obj["artifact_transfer"] = {
            "bytes": receipt_obj["artifact_bytes_total"],
            "seconds": round(fetch_s, 4),
            "bytes_per_s": (round(receipt_obj["artifact_bytes_total"]
                                  / fetch_s, 1) if fetch_s > 0 else None),
            "largest": largest,
            "largest_bytes_per_s": (
                round(largest["bytes"] / largest["fetch_s"], 1)
                if largest and largest["fetch_s"] > 0 else None),
        }
        if missing:
            # A missing artifact is a question, and the pod can still answer
            # it. The server's document root is the artifact directory, so
            # its index says exactly which files exist. Guessing at this from
            # the ground cost Iteration 1 a flight.
            listing = self._fetch("")
            if listing is not None:
                receipt_obj["artifact_dir_listing"] = listing[:4000]
                self._log("artifact dir listing retrieved (%d bytes)"
                          % len(listing))
            else:
                self._log("artifact dir listing also unreachable")
            self._log("artifacts NOT retrieved: %s" % ", ".join(missing))
        if integrity["mismatch"]:
            self._log("artifacts that did NOT match the pod's digest: %s"
                      % ", ".join(integrity["mismatch"]))

    def _teardown(self):
        """Terminate, then confirm absence by TWO independent reads.

        Absence used to mean "missing from a LIST". A LIST can omit a pod
        that exists, and after an acknowledged terminate that is exactly the
        case in which a run would report clean with a GPU still billing. It
        now needs LIST to omit the pod AND GET to return nothing; if the two
        disagree, the controller waits and asks again, and a disagreement
        that persists is recorded as such, never resolved by preference.
        """
        if self.pod_id is None:
            if self.creation_outcome == "unknown":
                # Nothing to terminate, because nothing can be named. This
                # must still appear in the receipt as unresolved, or the
                # run would read as a clean non-event.
                return [rc.pod_record(
                    "UNRESOLVED", creation_outcome="unknown",
                    note="create outcome unresolved; no id to terminate")], \
                    False
            return [], True
        acked, response = False, None
        self._mark("terminate_requested")
        for attempt in range(3):
            try:
                response = self.provider.terminate_pod(self.pod_id)
                acked = True
                self._mark("terminate_acknowledged")
                break
            except prov.ProviderError as exc:
                self._log("terminate attempt %d failed (status=%s)"
                          % (attempt + 1, exc.status))
                self._sleep(self.poll_s)
        self._ledger("terminate", terminate_response=response)
        evidence = {"list_omits": None, "get_absent": None, "reads": 0}
        absent, inventory_ok = False, False
        for attempt in range(4):
            evidence["reads"] += 1
            try:
                ids = [p.get("id") for p in self.provider.list_pods()]
                inventory_ok = True
                evidence["list_omits"] = self.pod_id not in ids
            except prov.ProviderError:
                inventory_ok = False
                evidence["list_omits"] = None
            try:
                evidence["get_absent"] = (
                    self.provider.get_pod(self.pod_id) is None)
            except prov.ProviderError:
                evidence["get_absent"] = None
            if evidence["list_omits"] and evidence["get_absent"]:
                absent = True
                self._mark("absence_confirmed")
                break
            if (evidence["list_omits"] is not None
                    and evidence["get_absent"] is not None
                    and evidence["list_omits"] != evidence["get_absent"]):
                self._log("LIST and GET DISAGREE about %s (list_omits=%s, "
                          "get_absent=%s); asking again"
                          % (self.pod_id, evidence["list_omits"],
                             evidence["get_absent"]))
            self._sleep(self.poll_s)
        evidence["agree"] = (evidence["list_omits"] is not None
                             and evidence["list_omits"]
                             == evidence["get_absent"])
        self.provider_view = {
            "list_contains_pod": (None if evidence["list_omits"] is None
                                  else not evidence["list_omits"]),
            "get_returns_pod": (None if evidence["get_absent"] is None
                                else not evidence["get_absent"]),
            "terminate_response": response,
            "reads": evidence["reads"]}
        if not inventory_ok:
            self._log("ABSENCE UNVERIFIED: inventory unreadable. Reconcile "
                      "before creating anything else.")
        elif not absent:
            self._log("ABSENCE NOT ESTABLISHED for %s: %s" % (self.pod_id,
                                                              evidence))
        pod = rc.pod_record(self.pod_id,
                            creation_outcome=self.creation_outcome or "unknown",
                            terminate_acknowledged=acked,
                            observed_absent=absent and inventory_ok,
                            absence_evidence=evidence,
                            terminate_response=response)
        self._ledger("absence", absence_evidence=evidence)
        return [pod], inventory_ok

    def _work_units(self, receipt_obj):
        declared = self.spec.get("work_units")
        if not declared:
            return None
        summary = self._telemetry_summary()
        actual = summary.get("units_final")
        if not actual:
            return None
        return {"name": declared["name"], "actual": float(actual)}


def _percentiles(vals):
    vals = sorted(vals)
    if not vals:
        return None

    def q(p):
        k = min(len(vals) - 1, max(0, int(round(p * (len(vals) - 1)))))
        return round(vals[k], 4)
    return {"n": len(vals), "p50": q(0.5), "p95": q(0.95), "p99": q(0.99),
            "max": round(vals[-1], 4)}


def summarise_api(calls):
    """Latency per operation, overall and first half vs second half.

    The halves are what show degradation over a long flight: the same
    operation getting slower (or failing more) as the run goes on.
    """
    out = {}
    ops = sorted({c["op"] for c in calls})
    for op in ops:
        rows = [c for c in calls if c["op"] == op]
        half = len(rows) // 2
        entry = {"calls": len(rows),
                 "failures": sum(1 for c in rows if not c["ok"]),
                 "latency_s": _percentiles([c["dur_s"] for c in rows])}
        if half >= 5:
            entry["first_half_p50_s"] = _percentiles(
                [c["dur_s"] for c in rows[:half]])["p50"]
            entry["second_half_p50_s"] = _percentiles(
                [c["dur_s"] for c in rows[half:]])["p50"]
            entry["first_half_failures"] = sum(1 for c in rows[:half]
                                               if not c["ok"])
            entry["second_half_failures"] = sum(1 for c in rows[half:]
                                                if not c["ok"])
        out[op] = entry
    return out


def summarise_health(health):
    if not health:
        return {"polls": 0}
    loops = [h["loop_s"] for h in health]
    gaps = [b["t"] - a["t"] for a, b in zip(health, health[1:])]
    return {"polls": len(health),
            "loop_s": _percentiles(loops),
            "poll_gap_s": _percentiles(gaps) if gaps else None,
            "spend_usd_last": health[-1]["spend_usd"],
            "telemetry_bytes_last": health[-1]["telemetry_bytes"]}
