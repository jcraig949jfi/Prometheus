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


class RunPodProvider(Provider):
    """Thin adapter over the already-qualified RunPod client."""

    def __init__(self, api=None):
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


# --------------------------------------------------------------- the fake

class Fault(object):
    """One scripted failure. `phantom` is the dangerous one: the create
    really happened and the caller was told it did not."""

    def __init__(self, status=None, timeout=False, phantom=False,
                 omit_from_list=False, message=""):
        self.status = status
        self.timeout = timeout
        self.phantom = phantom
        self.omit_from_list = omit_from_list
        self.message = message

    @staticmethod
    def http(status):
        return Fault(status=status)

    @staticmethod
    def lost_response():
        """Create succeeds server-side; the client sees a failure."""
        return Fault(status=500, phantom=True,
                     message="create accepted but response lost")

    @staticmethod
    def request_timeout():
        return Fault(timeout=True, message="timeout before response")


class FakeProvider(Provider):
    """In-memory provider with scriptable faults and a truthful ledger.

    `truth` records what ACTUALLY exists, regardless of what the API
    reported, so a test can assert that the controller reconciled an
    ambiguous outcome correctly rather than merely continuing past it.
    """

    def __init__(self, create_faults=(), list_faults=(), terminate_faults=(),
                 get_faults=(), hidden=()):
        self._ids = ("fake-%03d" % i for i in itertools.count(1))
        self.truth = {}                 # pod_id -> body, what really exists
        self.calls = {"create": 0, "list": 0, "get": 0, "terminate": 0}
        self._create_faults = list(create_faults)
        self._list_faults = list(list_faults)
        self._terminate_faults = list(terminate_faults)
        self._get_faults = list(get_faults)
        self._hidden = set(hidden)      # exists but omitted from list()

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
        return [{"id": pid, "desiredStatus": "RUNNING"}
                for pid in sorted(self.truth) if pid not in self._hidden]

    def get_pod(self, pod_id):
        self.calls["get"] += 1
        fault = self._next_fault(self._get_faults)
        if fault is not None:
            self._raise(fault)
        if pod_id not in self.truth:
            return None
        return {"id": pod_id, "desiredStatus": "RUNNING"}

    def terminate_pod(self, pod_id):
        self.calls["terminate"] += 1
        fault = self._next_fault(self._terminate_faults)
        if fault is not None:
            self._raise(fault)
        self.truth.pop(pod_id, None)
        self._hidden.discard(pod_id)
        return "ACK_204"

    # ------------------------------------------------------------ truth
    def actually_running(self):
        """What exists, including anything a LIST would hide."""
        return sorted(self.truth)

    def leaked(self):
        """Pods that exist but were never terminated: real money."""
        return self.actually_running()


# ----------------------------------------------------------- reconciliation

def create_with_reconcile(provider, body, log=lambda m: None, attempts=3,
                          sleep=time.sleep):
    """Create exactly one pod, treating any failure as AMBIGUOUS.

    A failed create does not say whether a pod exists. The only safe
    response is to ASK the inventory before doing anything else: adopt
    what is there, and retry only when the inventory is empty and the
    failure was therefore clean.

    If the reconciling LIST itself fails, this refuses to retry. A
    create of unknown outcome followed by an inventory read that also
    failed is exactly the state in which a retry produces a second
    billing pod, and guessing there is how one incident becomes two.
    """
    for attempt in range(1, attempts + 1):
        try:
            pod = provider.create_pod(body)
            log("create attempt %d -> accepted pod=%s" % (attempt, pod["id"]))
            return pod, "CREATED"
        except ProviderError as exc:
            log("create attempt %d failed status=%s; reconciling inventory"
                % (attempt, exc.status))
            try:
                existing = provider.list_pods()
            except ProviderError as inner:
                log("reconcile FAILED to list (status=%s): refusing to retry, "
                    "because a pod may exist unobserved" % inner.status)
                return None, "AMBIGUOUS_UNRECONCILED"
            if existing:
                log("reconcile: %d pod(s) present -> adopting %s, no further "
                    "creates" % (len(existing), existing[0]["id"]))
                return existing[0], "ADOPTED"
            log("reconcile: inventory empty, so that failure created nothing")
            if attempt < attempts:
                sleep(2)
    return None, "FAILED_CLEAN"
