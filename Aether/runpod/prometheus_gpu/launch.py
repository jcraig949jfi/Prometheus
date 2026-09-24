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

TELEMETRY_PATH = "out/telemetry.jsonl"
STAGES_PATH = "out/stages.jsonl"

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


def lifecycle(marks, stages, telemetry_summary=None):
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

    if telemetry_summary and telemetry_summary.get("elapsed_s"):
        out["module_reported_elapsed_s"] = telemetry_summary["elapsed_s"]
    return out


class Controller(object):
    def __init__(self, provider, spec, module_dir, budget_usd,
                 transport_factory=dryrun.local_transport, seat="Aether",
                 poll_s=30.0, ready_timeout_s=600.0, artifact_token=None,
                 now=time.time, sleep=time.sleep, log=None):
        self.provider = provider
        self.spec = spec
        self.module_dir = module_dir
        self.budget_usd = float(budget_usd)
        self.transport_factory = transport_factory
        self.seat = seat
        self.poll_s = float(poll_s)
        self.ready_timeout_s = float(ready_timeout_s)
        self.artifact_token = artifact_token
        self._now = now
        self._sleep = sleep
        self._log = log or (lambda m: None)
        self.pod_id = None
        self.creation_outcome = None
        self.telemetry_text = ""
        # Controller-clock instants. Kept apart from pod-clock stages,
        # because an interval spanning both is not a measurement.
        self.marks = {}
        self.create_attempts = []
        self.gpu_used = None

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
        try:
            blob = self.provider.fetch(self.pod_id, path,
                                       token=self.artifact_token)
        except Exception as exc:
            self._log("fetch %s raised %s; treating as unreachable"
                      % (path, type(exc).__name__))
            return None
        if blob is None:
            return None
        return blob if isinstance(blob, bytes) else blob.encode("utf-8")

    def _fetch(self, path):
        blob = self._fetch_bytes(path)
        return None if blob is None else blob.decode("utf-8", "replace")

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
        if pods:
            raise LaunchRefused(
                "%d pod(s) already active (%s). One pod at a time; terminate "
                "or adopt before launching."
                % (len(pods), ", ".join(str(p.get("id")) for p in pods)))
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
            transport_factory=self.transport_factory, seat=self.seat)
        secrets_mod.assert_no_credentials(request["env"],
                                          where="pod request env at launch")
        # The pod's artifact server is generated with a per-run token. The
        # controller has to hold the same one to read anything back, and
        # taking it from the plan means the two cannot drift apart.
        if self.artifact_token is None:
            self.artifact_token = run_meta.get("artifact_token")

        receipt_obj = rc.from_plan(plan, result="NOT_RUN")
        started = self._now()
        receipt_obj["started_utc"] = rc._utc(started)
        result = "UNKNOWN"
        try:
            self.pod_id, self.creation_outcome = self._create(request)
            if self.pod_id is None and self.creation_outcome == "unknown":
                # A create whose outcome could not be resolved. A pod may
                # exist and we do not have its id, so this is the one case
                # that must NOT be reported as a clean non-event.
                result = "UNKNOWN"
                receipt_obj["notes"].append(
                    "create outcome unresolved and inventory unreadable; a "
                    "pod may exist that this controller cannot name. "
                    "RECONCILE MANUALLY before creating anything else.")
            elif self.pod_id is None:
                result = "NOT_RUN"
                refused = [a["gpu_id"] for a in self.create_attempts]
                if all(a["outcome"] == "FAILED_CLEAN"
                       for a in self.create_attempts) and refused:
                    receipt_obj["notes"].append(
                        "no capacity for any declared GPU (%s); provider "
                        "confirms nothing exists. Declare more "
                        "gpu.alternatives or try again later."
                        % ", ".join(refused))
                else:
                    receipt_obj["notes"].append(
                        "create failed cleanly; provider confirms nothing "
                        "exists")
            else:
                ready = self._await_ready(started)
                if not ready:
                    result = "FAILED"
                    receipt_obj["notes"].append(
                        "pod never reported ready within %.0f s"
                        % self.ready_timeout_s)
                else:
                    result = self._watch(started)
                self._retrieve(receipt_obj)
        except LaunchRefused:
            raise
        except Exception as exc:
            result = "UNKNOWN"
            receipt_obj["notes"].append(
                "controller raised %s: %s" % (type(exc).__name__, exc))
            self._log("controller raised %s; proceeding to teardown"
                      % type(exc).__name__)
        finally:
            ended = self._now()
            receipt_obj["ended_utc"] = rc._utc(ended)
            pods, inventory_ok = self._teardown()
            receipt_obj["pods"] = pods
            receipt_obj["cleanup"] = rc.cleanup_block(pods, inventory_ok)
            receipt_obj["cost"] = cost_mod.actual(
                max(0.0, ended - started), self._hourly(),
                work_units=self._work_units(receipt_obj))
            # Only a create the provider CONFIRMED created nothing may be
            # downgraded to NOT_RUN here. An unresolved create also has no
            # pod id, and calling that a non-event is how a pod that may
            # be billing disappears from the record.
            never_existed = (self.pod_id is None
                             and self.creation_outcome != "unknown")
            receipt_obj["result"] = "NOT_RUN" if never_existed else result
            receipt_obj["telemetry_summary"] = tel_mod.summarise(
                tel_mod.read_jsonl(self.telemetry_text, is_text=True)
                if self.telemetry_text else [])
            receipt_obj["create_attempts"] = self.create_attempts
            receipt_obj["gpu_used"] = self.gpu_used
            receipt_obj["lifecycle"] = lifecycle(
                self.marks, receipt_obj.get("pod_stages"),
                receipt_obj.get("telemetry_summary"))
        rc.validate(receipt_obj)
        return receipt_obj

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
        """The declared GPU, then its declared alternatives, in order."""
        gpu = self.spec["gpu"]
        out = [gpu.get("class")]
        for alternative in gpu.get("alternatives", []):
            if alternative not in out:
                out.append(alternative)
        return [g for g in out if g]

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
        deadline = started + self.ready_timeout_s
        while self._now() < deadline:
            if self._fetch(TELEMETRY_PATH) is not None:
                self._mark("first_telemetry")
                return True
            try:
                if self.provider.get_pod(self.pod_id) is None:
                    self._log("pod vanished before it was ready")
                    return False
            except prov.ProviderError:
                pass            # a control-plane blip is not a verdict
            self._sleep(self.poll_s)
        return False

    def _watch(self, started):
        """Poll until the module finishes, the budget runs out, or time does."""
        hourly = self._hourly()
        runtime_cap = float(self.spec["max_runtime_s"])
        while True:
            elapsed = self._now() - started
            spend = elapsed / 3600.0 * hourly
            if spend >= self.budget_usd:
                self._log("BUDGET CEILING $%.4f >= $%.4f after %.0f s"
                          % (spend, self.budget_usd, elapsed))
                return "ABORTED"
            if elapsed >= runtime_cap:
                self._log("max_runtime_s %.0f reached" % runtime_cap)
                return "TIMEOUT"
            text = self._fetch(TELEMETRY_PATH)
            if text is not None:
                self.telemetry_text = text
                records = tel_mod.read_jsonl(text, is_text=True)
                ends = [r for r in records if r.get("kind") == "end"]
                if ends:
                    status = str(ends[-1].get("status", "")).lower()
                    self._log("module reported end (status=%s)" % status)
                    return "OK" if status in ("ok", "success", "") else "FAILED"
                errors = [r for r in records if r.get("kind") == "error"]
                if errors:
                    self._log("module reported an error record")
            self._sleep(self.poll_s)

    def _retrieve(self, receipt_obj):
        """Before teardown, always. A dead pod hands back nothing."""
        self._mark("retrieve_start")
        stages = self._fetch(STAGES_PATH)
        if stages:
            receipt_obj["pod_stages"] = parse_stages(stages)
        text = self._fetch(TELEMETRY_PATH)
        if text is not None:
            self.telemetry_text = text
        got, missing = [], []
        for path in self.spec["artifacts"]:
            blob = self._fetch_bytes(path)
            if blob is None:
                missing.append(path)
                continue
            got.append({"path": path, "bytes": len(blob),
                        "sha256": hashlib.sha256(blob).hexdigest()})
        self._mark("retrieve_end")
        receipt_obj["artifacts"] = got
        receipt_obj["artifacts_missing"] = missing
        receipt_obj["artifact_bytes_total"] = sum(a["bytes"] for a in got)
        if missing:
            self._log("artifacts NOT retrieved: %s" % ", ".join(missing))

    def _teardown(self):
        """Terminate, then confirm absence. Two facts, recorded separately."""
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
        acked = False
        self._mark("terminate_requested")
        for attempt in range(3):
            try:
                self.provider.terminate_pod(self.pod_id)
                acked = True
                self._mark("terminate_acknowledged")
                break
            except prov.ProviderError as exc:
                self._log("terminate attempt %d failed (status=%s)"
                          % (attempt + 1, exc.status))
                self._sleep(self.poll_s)
        absent, inventory_ok = False, False
        for attempt in range(3):
            try:
                ids = [p.get("id") for p in self.provider.list_pods()]
                inventory_ok = True
                absent = self.pod_id not in ids
                if absent:
                    self._mark("absence_confirmed")
                    break
            except prov.ProviderError:
                inventory_ok = False
            self._sleep(self.poll_s)
        if not inventory_ok:
            self._log("ABSENCE UNVERIFIED: inventory unreadable. Reconcile "
                      "before creating anything else.")
        pod = rc.pod_record(self.pod_id,
                            creation_outcome=self.creation_outcome or "unknown",
                            terminate_acknowledged=acked,
                            observed_absent=absent and inventory_ok)
        return [pod], inventory_ok

    def _work_units(self, receipt_obj):
        declared = self.spec.get("work_units")
        if not declared:
            return None
        records = tel_mod.read_jsonl(self.telemetry_text, is_text=True) \
            if self.telemetry_text else []
        summary = tel_mod.summarise(records)
        actual = summary.get("units_final")
        if not actual:
            return None
        return {"name": declared["name"], "actual": float(actual)}
