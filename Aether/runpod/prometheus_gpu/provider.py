"""Provider abstraction, plus a fake that can fail on demand.

Two implementations behind one interface:

  RunPodProvider   wraps the qualified Aether/runpod/aeth01_canary
                   client. It is the only code here that can spend money.
  FakeProvider     scriptable failures, for exercising the REAL
                   controller logic without a pod.

The fake exists because the expensive cloud run should be the final
confirmation, not where basic bugs are found. Every failure mode below
has either already happened to this seat or is one step away from a
mode that has:

  400/500 on create        happened, four launches in a row
  create accepted, response lost
                           the ambiguous case that makes blind retry
                           able to produce two billing pods
  LIST omission            the reason "absent from a listing" is not
                           the same claim as "terminated"
  DELETE transient failure the reason terminate is retried and then
                           independently verified
  429 / timeout / 401      not yet seen, cheap to be ready for

A DryRunProvider is deliberately NOT provided. Dry run is enforced by
never constructing a provider at all (see dryrun.py), because a
"provider that promises not to POST" is one bug away from POSTing.
"""

import itertools
import time


# The pod serves telemetry and artifacts on this port. The default Python
# User-Agent is Cloudflare-blocked on this account, so it is set
# explicitly everywhere a request leaves the controller.
# 8081, not 8080. Iteration 1's second flight created a pod that never
# became reachable on 8080; the qualified AETH-01/02 orchestrators have
# always served artifacts on 8081 and declared 8080 alongside it. The stock
# image is a plausible occupant of 8080, and a failed bind under `set -e`
# takes the script down before it can report anything.
ARTIFACT_PORT = 8081
DECLARED_PORTS = ("8080/http", "8081/http")
USER_AGENT = "prometheus-gpu/1 (+Prometheus Aether)"


class ProviderError(RuntimeError):
    def __init__(self, status=None, message=""):
        super().__init__(message or ("provider request failed (%s)" % status))
        self.status = status


class ProviderTimeout(ProviderError):
    pass


class Provider(object):
    """Interface. Creation is the only method that can cost money."""

    def create_pod(self, body):
        raise NotImplementedError

    def list_pods(self):
        raise NotImplementedError

    def get_pod(self, pod_id):
        raise NotImplementedError

    def terminate_pod(self, pod_id):
        raise NotImplementedError

    def fetch(self, pod_id, path, port=ARTIFACT_PORT, token=None, timeout=60):
        """Read a file the pod is serving, or None if it is not reachable.

        Deliberately separate from the control plane. This is how
        telemetry and artifacts come back WHILE the pod is running, so a
        workload that dies still hands back what it had. Unreachable is
        not an error: early in a run the server is simply not up yet, and
        the caller must be able to tell "not yet" from "failed".
        """
        raise NotImplementedError


class RunPodProvider(Provider):
    """Thin adapter over the already-qualified RunPod client."""

    def __init__(self, api=None):
        self.last_fetch = None
        if api is None:
            import runpod_api
            api = runpod_api.RunPodAPI()
        self._api = api
        import runpod_api as _r
        self._err = _r.ProviderError

    def _wrap(self, fn, *a):
        try:
            return fn(*a)
        except self._err as exc:
            raise ProviderError(getattr(exc, "status", None)) from None

    def create_pod(self, body):
        return self._wrap(self._api.create_pod, body)

    def list_pods(self):
        return self._wrap(self._api.list_pods)

    def get_pod(self, pod_id):
        return self._wrap(self._api.get_pod, pod_id)

    def terminate_pod(self, pod_id):
        return self._wrap(self._api.terminate_pod, pod_id)

    def stock_status(self, gpu_ids):
        """{gpu_id: "High"|"Medium"|"Low"|None} for SECURE cloud. Read-only.

        Iteration 3 flight F2b walked five declared cards into five capacity
        refusals; a single GraphQL read at the same moment showed one card
        in stock that was not on the list. Advisory only: stock changes by
        the second, so this reorders the walk, it never removes a card.
        Returns {} if the read fails -- never raises into a launch.
        """
        import json as _json
        import os as _os
        from urllib.request import Request, build_opener, ProxyHandler
        query = ("query { gpuTypes { id lowestPrice(input: {gpuCount: 1, "
                 "secureCloud: true}) { stockStatus } } }")
        try:
            req = Request(
                "https://api.runpod.io/graphql",
                data=_json.dumps({"query": query}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json",
                         "User-Agent": USER_AGENT,
                         "Authorization": "Bearer "
                         + _os.environ.get("RUNPOD_API_KEY", "")})
            with build_opener(ProxyHandler({})).open(req, timeout=20) as r:
                rows = (_json.loads(r.read()).get("data") or {}).get(
                    "gpuTypes") or []
        except Exception:
            return {}
        wanted = set(gpu_ids)
        return {g["id"]: (g.get("lowestPrice") or {}).get("stockStatus")
                for g in rows if g.get("id") in wanted}

    def fetch(self, pod_id, path, port=ARTIFACT_PORT, token=None, timeout=60):
        """Read from the pod's HTTP proxy. UNQUALIFIED against hardware.

        The URL shape and the bearer header are copied from the working
        AETH-01/02 orchestrators, and the explicit User-Agent is not
        cosmetic: the default Python one is Cloudflare-blocked on this
        account (FAILURE_PLAYBOOK entry 1).

        Every failure returns None rather than raising, because the
        caller polls this and "not up yet" is the normal early answer. A
        run must never be abandoned because a fetch was early.
        """
        from urllib.request import Request, build_opener, ProxyHandler
        url = "https://%s-%d.proxy.runpod.net/%s" % (
            pod_id, port, str(path).lstrip("/"))
        req = Request(url, method="GET",
                      headers={"Accept": "*/*", "User-Agent": USER_AGENT})
        if token:
            req.add_unredirected_header("Authorization", "Bearer " + token)
        self.last_fetch = {"url": url, "status": None, "error": None}
        try:
            with build_opener(ProxyHandler({})).open(req, timeout=timeout) as r:
                self.last_fetch["status"] = r.getcode()
                if r.getcode() == 200:
                    return r.read()
        except Exception as exc:
            self.last_fetch["error"] = "%s: %s" % (type(exc).__name__, exc)
            status = getattr(exc, "code", None)
            if status is not None:
                self.last_fetch["status"] = status
            return None
        return None


# --------------------------------------------------------------- the fake

class Fault(object):
    """One scripted failure. `phantom` is the dangerous one: the create
    really happened and the caller was told it did not."""

    def __init__(self, status=None, timeout=False, phantom=False,
                 omit_from_list=False, message="", keep=False):
        self.status = status
        self.timeout = timeout
        self.phantom = phantom
        self.omit_from_list = omit_from_list
        self.message = message
        # terminate only: the provider ACKs and the pod stays. The case in
        # which an acknowledgement alone would be reported as cleanup.
        self.keep = keep

    @staticmethod
    def http(status):
        return Fault(status=status)

    @staticmethod
    def lost_response():
        """Create succeeds server-side; the client sees a failure."""
        return Fault(status=500, phantom=True,
                     message="create accepted but response lost")

    @staticmethod
    def lost_response_hidden():
        """Create succeeds, the response is lost, AND the pod is omitted
        from every LIST. Nothing the controller can read names it."""
        return Fault(status=500, phantom=True, omit_from_list=True,
                     message="create accepted, response lost, list omits it")

    @staticmethod
    def ambiguous():
        """A transport-level failure with no HTTP status at all: the
        request may or may not have reached the provider."""
        return Fault(status=None, phantom=True,
                     message="connection reset after send; no status")

    @staticmethod
    def request_timeout():
        return Fault(timeout=True, message="timeout before response")

    @staticmethod
    def ack_but_keep():
        """terminate: acknowledged, and the pod is still there."""
        return Fault(keep=True, message="terminate acknowledged; pod remains")


class FakeProvider(Provider):
    """In-memory provider with scriptable faults and a truthful ledger.

    `truth` records what ACTUALLY exists, regardless of what the API
    reported, so a test can assert that the controller reconciled an
    ambiguous outcome correctly rather than merely continuing past it.
    """

    def __init__(self, create_faults=(), list_faults=(), terminate_faults=(),
                 get_faults=(), hidden=(), served=None, fetch_faults=(),
                 served_by_name=None, stale_list_reads=0, unnamed=False):
        self._ids = ("fake-%03d" % i for i in itertools.count(1))
        self.truth = {}                 # pod_id -> body, what really exists
        self.calls = {"create": 0, "list": 0, "get": 0, "terminate": 0}
        self._create_faults = list(create_faults)
        self._list_faults = list(list_faults)
        self._terminate_faults = list(terminate_faults)
        self._get_faults = list(get_faults)
        self._fetch_faults = list(fetch_faults)
        self._hidden = set(hidden)      # exists but omitted from list()
        # What the pod is serving. A value may be bytes/str (constant), a
        # LIST (one frame per fetch, so a test can watch a run progress),
        # or a callable(call_index). Anything absent fetches as None,
        # which is how "the server is not up yet" is expressed.
        self.served = dict(served or {})
        # Per-pod content, keyed by the pod's NAME (the run id), for
        # several pods at once. Falls back to `served`.
        self.served_by_name = dict(served_by_name or {})
        self._fetches = {}
        # GET/LIST disagreement the other way round: a terminated pod keeps
        # appearing in LIST for this many reads while GET says it is gone.
        self._stale_list_reads = int(stale_list_reads)
        self._stale = {}                # pod_id -> remaining stale reads
        self._stale_names = {}
        # A provider whose listings carry no names: ownership cannot be
        # established from them.
        self._unnamed = bool(unnamed)

    def _record(self, pod_id):
        body = self.truth.get(pod_id) or {}
        rec = {"id": pod_id, "desiredStatus": "RUNNING"}
        if not self._unnamed and body.get("name") is not None:
            rec["name"] = body.get("name")
        return rec

    def _next_fault(self, queue):
        return queue.pop(0) if queue else None

    @staticmethod
    def _raise(fault):
        if fault.timeout:
            raise ProviderTimeout(message=fault.message or "timeout")
        raise ProviderError(fault.status, fault.message)

    def create_pod(self, body):
        self.calls["create"] += 1
        fault = self._next_fault(self._create_faults)
        if fault is not None:
            if fault.phantom:
                pod_id = next(self._ids)
                self.truth[pod_id] = dict(body)     # it really exists
                if fault.omit_from_list:
                    self._hidden.add(pod_id)
            self._raise(fault)
        pod_id = next(self._ids)
        self.truth[pod_id] = dict(body)
        return {"id": pod_id, "desiredStatus": "RUNNING"}

    def list_pods(self):
        self.calls["list"] += 1
        fault = self._next_fault(self._list_faults)
        if fault is not None:
            self._raise(fault)
        out = [self._record(pid)
               for pid in sorted(self.truth) if pid not in self._hidden]
        for pid in sorted(self._stale):
            if self._stale[pid] > 0:
                self._stale[pid] -= 1
                out.append({"id": pid, "desiredStatus": "RUNNING",
                            "name": self._stale_names.get(pid)})
        return out

    def get_pod(self, pod_id):
        self.calls["get"] += 1
        fault = self._next_fault(self._get_faults)
        if fault is not None:
            self._raise(fault)
        if pod_id not in self.truth:
            return None
        return self._record(pod_id)

    def _served_for(self, pod_id):
        name = (self.truth.get(pod_id) or {}).get("name")
        return self.served_by_name.get(name, self.served)

    def fetch(self, pod_id, path, port=ARTIFACT_PORT, token=None, timeout=60):
        self.calls["fetch"] = self.calls.get("fetch", 0) + 1
        fault = self._next_fault(self._fetch_faults)
        if fault is not None:
            return None                 # unreachable, not an exception
        if pod_id not in self.truth:
            return None
        key = str(path).lstrip("/")
        value = self._served_for(pod_id).get(key)
        if value is None:
            return None
        counter = (pod_id, key)
        index = self._fetches.get(counter, 0)
        self._fetches[counter] = index + 1
        if callable(value):
            value = value(index)
        elif isinstance(value, list):
            value = value[min(index, len(value) - 1)]
        if value is None:
            return None
        return value.encode("utf-8") if isinstance(value, str) else value

    def terminate_pod(self, pod_id):
        self.calls["terminate"] += 1
        fault = self._next_fault(self._terminate_faults)
        if fault is not None:
            if fault.keep:
                return "ACK_204"        # acknowledged; the pod stays
            self._raise(fault)
        if pod_id not in self.truth:
            return "NOT_FOUND_404"
        name = self.truth[pod_id].get("name")
        self.truth.pop(pod_id, None)
        self._hidden.discard(pod_id)
        if self._stale_list_reads:
            self._stale[pod_id] = self._stale_list_reads
            self._stale_names[pod_id] = name
        return "ACK_204"

    # ------------------------------------------------------------ truth
    def actually_running(self):
        """What exists, including anything a LIST would hide."""
        return sorted(self.truth)

    def leaked(self):
        """Pods that exist but were never terminated: real money."""
        return self.actually_running()


# ----------------------------------------------------------- reconciliation

# A create rejected for CAPACITY is a clean refusal, not an ambiguous
# outcome: the provider is telling us it made nothing. It is worth
# distinguishing, because the useful response is to ask for a different
# GPU rather than to retry the same one.
CAPACITY_MARKERS = ("no longer any instances available",
                    "no instances available",
                    "insufficient capacity",
                    "currently unavailable")


def looks_like_capacity(detail):
    text = str(detail or "").lower()
    return any(marker in text for marker in CAPACITY_MARKERS)


def create_with_alternatives(provider, body, gpu_ids, log=lambda m: None,
                             sleep=time.sleep):
    """Try each GPU id in turn, reconciling between attempts.

    GPU availability is a runtime condition. A seat should not have to know
    which card happens to have capacity at 4pm on a Tuesday, so it declares
    the GPUs its workload can run on and the platform walks the list.

    SAFETY: every attempt goes through `create_with_reconcile`, so a failed
    create is confirmed to have created nothing BEFORE the next id is
    tried. Without that, walking a list of alternatives would be a loop of
    blind retries -- the exact failure mode the reconciliation exists to
    prevent.
    """
    attempted = []
    for index, gpu_id in enumerate(gpu_ids):
        candidate = dict(body)
        candidate["gpu"] = dict(body.get("gpu") or {}, id=gpu_id)
        log("create attempt on %s (%d of %d)" % (gpu_id, index + 1,
                                                 len(gpu_ids)))
        pod, label = create_with_reconcile(provider, candidate, log=log,
                                          attempts=1, sleep=sleep)
        attempted.append({"gpu_id": gpu_id, "outcome": label})
        if pod is not None:
            return pod, label, attempted
        if label == "AMBIGUOUS_UNRECONCILED":
            # A pod may exist that we cannot name. Trying another GPU here
            # could put a second one beside it.
            log("outcome unresolved on %s; refusing to try further GPUs"
                % gpu_id)
            return None, label, attempted
    return None, "NO_CAPACITY", attempted


# Seconds between the two LIST reads that must BOTH show none of our pods
# before a failed create may be called clean. One empty read is one
# listing's opinion; a pod still materialising, or an eventually
# consistent LIST, can be absent from it and present a moment later.
RECONCILE_CONFIRM_S = 5.0


def _owned(pods, name):
    """Split a listing into (ours, unnamed). Ours means the name matches.

    Ownership is by NAME, which is the run id. Adopting "whatever is in
    the account" was safe only while exactly one controller could ever
    create; with several pods in flight, or another seat on the account,
    the first pod in a listing may belong to someone else, and adopting it
    means terminating it.
    """
    ours = [p for p in pods if p.get("name") == name]
    unnamed = [p for p in pods if p.get("name") is None]
    return ours, unnamed


def create_with_reconcile(provider, body, log=lambda m: None, attempts=3,
                          sleep=time.sleep, confirm_s=RECONCILE_CONFIRM_S):
    """Create exactly one pod, treating any failure as AMBIGUOUS.

    A failed create does not say whether a pod exists. The only safe
    response is to ASK the inventory before doing anything else: adopt
    what is there, and retry only when the inventory is empty and the
    failure was therefore clean.

    If the reconciling LIST itself fails, this refuses to retry. A
    create of unknown outcome followed by an inventory read that also
    failed is exactly the state in which a retry produces a second
    billing pod, and guessing there is how one incident becomes two.

    Iteration 3: adoption is by OWNERSHIP (the pod's name is this run's
    id), a listed pod with no name makes ownership undecidable and so the
    outcome AMBIGUOUS, and "created nothing" needs TWO LIST reads
    `confirm_s` apart that both show none of ours. What remains uncovered,
    and is said so in the receipt: a pod that every LIST omits cannot be
    found by anything but its id, which a lost response never delivered.
    """
    name = body.get("name")
    for attempt in range(1, attempts + 1):
        try:
            pod = provider.create_pod(body)
            log("create attempt %d -> accepted pod=%s" % (attempt, pod["id"]))
            return pod, "CREATED"
        except ProviderError as exc:
            log("create attempt %d failed status=%s; reconciling inventory"
                % (attempt, exc.status))
            for read in (1, 2):
                try:
                    existing = provider.list_pods()
                except ProviderError as inner:
                    log("reconcile FAILED to list (status=%s): refusing to "
                        "retry, because a pod may exist unobserved"
                        % inner.status)
                    return None, "AMBIGUOUS_UNRECONCILED"
                ours, unnamed = _owned(existing, name)
                if ours:
                    log("reconcile read %d: our pod %s is present -> adopting, "
                        "no further creates" % (read, ours[0]["id"]))
                    return ours[0], "ADOPTED"
                if unnamed:
                    log("reconcile read %d: %d listed pod(s) carry no name, so "
                        "ownership cannot be decided; refusing to retry or "
                        "adopt" % (read, len(unnamed)))
                    return None, "AMBIGUOUS_UNRECONCILED"
                if read == 1:
                    sleep(confirm_s)
            log("reconcile: two reads %.0f s apart show none of ours, so that "
                "failure created nothing we can see" % confirm_s)
            if attempt < attempts:
                sleep(2)
    return None, "FAILED_CLEAN"
