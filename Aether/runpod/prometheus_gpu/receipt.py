"""The run receipt: what a run is allowed to claim about itself.

A receipt is not a log. It is the record a later reader trusts when
nobody is left who remembers the run, so its job is to keep apart the
things that are easy to conflate and expensive to conflate wrongly.

FOUR CLEANUP CLAIMS, never interchangeable:

  terminate_acknowledged  the provider ACCEPTED a terminate request
  observed_absent         the pod is no longer in an inventory listing
  operational_cleanup     nothing we know of is still running
  billing_reconciled      PROVIDER BILLING DATA WAS OBTAINED

The ladder is enforced here, not left to the caller's discipline:

  * `observed_absent` cannot support anything unless the inventory read
    itself SUCCEEDED. A failed or filtered LIST omits pods too, and a run
    may not report clean because a listing happened to be empty.
  * `operational_cleanup` requires BOTH an acknowledged terminate and an
    observed absence, for every pod. Absence alone is a listing's opinion;
    an acknowledgement alone is a promise about the future.
  * `billing_reconciled` requires a `billing_evidence` block naming where
    the number came from. Wall-clock time multiplied by a quoted hourly
    rate is an ESTIMATE, and calling it reconciliation is the specific
    lie this module exists to prevent.

`cost.actual()` therefore always emits `billing_reconciled: false`, and
`validate()` refuses a receipt that flips it true without evidence.
"""

import json
import time

SCHEMA = "prometheus-gpu/run-receipt/1"

RESULTS = (
    "OK",        # workload ran to completion and reported success
    "PARTIAL",   # produced usable output but did not finish the plan
    "FAILED",    # ran and failed
    "TIMEOUT",   # hit max_runtime_s
    "ABORTED",   # the controller stopped it (budget, guardrail, operator)
    "NOT_RUN",   # never launched; a dry run's skeleton stays here
    "UNKNOWN",   # launched, and we genuinely cannot say. Not a synonym
                 # for FAILED: a lost pod whose outcome is unknown is a
                 # different operational situation from one that crashed.
)

CREATION_OUTCOMES = (
    "confirmed",  # create returned an id
    "adopted",    # create outcome was ambiguous; the pod was found by
                  # reconciling inventory rather than by a second create
    "unknown",    # create outcome ambiguous AND reconciliation failed
)


class ReceiptError(ValueError):
    """A receipt claiming more than its evidence supports."""


def _utc(when=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",
                         time.gmtime(when if when is not None else time.time()))


def pod_record(pod_id, creation_outcome="confirmed", created_utc=None,
               terminate_acknowledged=False, observed_absent=False,
               note=None):
    if creation_outcome not in CREATION_OUTCOMES:
        raise ReceiptError("creation_outcome must be one of %s"
                           % (CREATION_OUTCOMES,))
    rec = {"id": pod_id,
           "creation_outcome": creation_outcome,
           "created_utc": created_utc or _utc(),
           "terminate_acknowledged": bool(terminate_acknowledged),
           "observed_absent": bool(observed_absent)}
    if note:
        rec["note"] = note
    return rec


def cleanup_block(pods, inventory_read_ok, billing_evidence=None):
    """Derive the four claims from per-pod evidence. Never hand-written.

    Deriving rather than accepting is the point: a caller cannot assert
    `operational_cleanup` without the per-pod facts that justify it.
    """
    pods = list(pods or [])
    acked = all(p.get("terminate_acknowledged") for p in pods) if pods else True
    absent = all(p.get("observed_absent") for p in pods) if pods else True

    unresolved = []
    for pod in pods:
        reasons = []
        if not pod.get("terminate_acknowledged"):
            reasons.append("no terminate acknowledgement")
        if not pod.get("observed_absent"):
            reasons.append("still present in, or never confirmed absent by, "
                           "an inventory listing")
        if pod.get("creation_outcome") == "unknown":
            reasons.append("creation outcome unknown")
        if reasons:
            unresolved.append({"id": pod.get("id"), "reasons": reasons})

    # A listing that failed cannot testify to absence. Without a good
    # read, absence is not evidence and cleanup cannot be claimed.
    operational = bool(inventory_read_ok) and acked and absent and not unresolved

    block = {
        "inventory_read_ok": bool(inventory_read_ok),
        "terminate_acknowledged": acked,
        "observed_absent": absent and bool(inventory_read_ok),
        "operational_cleanup": operational,
        "billing_reconciled": False,
        "unresolved": unresolved,
        "pod_count": len(pods),
    }
    if not inventory_read_ok:
        block["note"] = ("inventory read failed; absence is unverified and "
                         "cleanup is NOT claimed. Reconcile before any "
                         "further create.")
    if billing_evidence:
        block["billing_reconciled"] = True
        block["billing_evidence"] = dict(billing_evidence)
    return block


def from_plan(plan, result="NOT_RUN"):
    """Start a receipt from a dry-run plan, so what was validated is what
    is reported. The plan is the skeleton; nothing is re-derived by hand."""
    return {
        "schema": SCHEMA,
        "run_id": plan["run_id"],
        "seat": plan.get("seat"),
        "module": plan["module"]["identity"],
        "entrypoint": plan["module"]["entrypoint"],
        "args": plan["module"]["args"],
        "bundle_sha256": plan["bundle"]["bundle_sha256"],
        "spec_sha256": plan["bundle"].get("spec_sha256"),
        "git": plan["bundle"].get("git"),
        "transport": plan.get("transport", {}).get("kind"),
        "guardrails": plan.get("guardrails"),
        "plan_cost_projection": plan.get("cost_projection"),
        "created_utc": _utc(),
        "started_utc": None,
        "ended_utc": None,
        "result": result,
        "pods": [],
        "cleanup": cleanup_block([], inventory_read_ok=True),
        "cost": None,
        "artifacts": [],
        "artifacts_missing": list(plan.get("artifacts_expected", [])),
        "telemetry_summary": None,
        "notes": [],
    }


def validate(rec):
    """Raise unless every claim in the receipt is supported. Reads a
    receipt written by anyone, including a future version of us."""
    if not isinstance(rec, dict):
        raise ReceiptError("a receipt must be a JSON object")
    if rec.get("schema") != SCHEMA:
        raise ReceiptError("unknown receipt schema %r; expected %r"
                           % (rec.get("schema"), SCHEMA))
    for field in ("run_id", "module", "result", "cleanup"):
        if field not in rec:
            raise ReceiptError("receipt needs `%s`" % field)
    if rec["result"] not in RESULTS:
        raise ReceiptError("result %r must be one of %s"
                           % (rec["result"], RESULTS))

    pods = rec.get("pods") or []
    for pod in pods:
        if pod.get("creation_outcome") not in CREATION_OUTCOMES:
            raise ReceiptError("pod %r has creation_outcome %r"
                               % (pod.get("id"), pod.get("creation_outcome")))

    clean = rec["cleanup"]
    derived = cleanup_block(pods, clean.get("inventory_read_ok", False),
                            billing_evidence=clean.get("billing_evidence"))

    if clean.get("operational_cleanup") and not derived["operational_cleanup"]:
        raise ReceiptError(
            "receipt claims operational_cleanup, but the per-pod evidence "
            "does not support it: %s. A run may not report clean because a "
            "listing happened to omit a pod."
            % (json.dumps(derived["unresolved"]),))

    if clean.get("observed_absent") and not clean.get("inventory_read_ok"):
        raise ReceiptError(
            "receipt claims observed_absent while the inventory read failed; "
            "a failed listing omits pods too")

    if clean.get("billing_reconciled") and not clean.get("billing_evidence"):
        raise ReceiptError(
            "receipt claims billing_reconciled with no billing_evidence. "
            "Wall time at a quoted rate is an ESTIMATE, not reconciliation; "
            "only actual provider billing data may set this true.")

    ev = clean.get("billing_evidence")
    if ev is not None:
        for field in ("source", "retrieved_utc", "amount_usd"):
            if field not in ev:
                raise ReceiptError(
                    "billing_evidence needs `%s` so a later reader can tell "
                    "where the number came from" % field)

    cost = rec.get("cost")
    if cost and cost.get("billing_reconciled"):
        raise ReceiptError(
            "cost.billing_reconciled must stay false; reconciliation is a "
            "cleanup claim backed by billing_evidence, not a cost estimate")

    if rec["result"] != "NOT_RUN" and not rec.get("bundle_sha256"):
        raise ReceiptError(
            "a run that happened must carry bundle_sha256; without it the "
            "bytes that ran cannot be identified later")
    return True


def render(rec):
    """The short human answer: what ran, what it cost, what is still up."""
    out = ["RECEIPT  %s" % rec["run_id"],
           "  module        %s   result %s" % (rec["module"], rec["result"]),
           "  bundle        %s" % (rec.get("bundle_sha256") or "-"),
           "  window        %s -> %s" % (rec.get("started_utc") or "-",
                                         rec.get("ended_utc") or "-")]
    cost = rec.get("cost") or {}
    if cost:
        out.append("  cost          $%.4f estimated over %.1f s (%s)"
                   % (cost.get("usd_estimated", 0.0),
                      cost.get("elapsed_s", 0.0),
                      "RECONCILED" if rec["cleanup"].get("billing_reconciled")
                      else "NOT reconciled with provider billing"))
    clean = rec["cleanup"]
    out.append("  cleanup       terminate_ack=%s observed_absent=%s "
               "operational=%s billing_reconciled=%s"
               % (clean.get("terminate_acknowledged"),
                  clean.get("observed_absent"),
                  clean.get("operational_cleanup"),
                  clean.get("billing_reconciled")))
    for item in clean.get("unresolved") or []:
        out.append("  UNRESOLVED    %s: %s" % (item["id"],
                                               "; ".join(item["reasons"])))
    tel = rec.get("telemetry_summary") or {}
    if tel:
        out.append("  telemetry     %s records, units=%s, complete=%s"
                   % (tel.get("records"), tel.get("units_final"),
                      tel.get("complete")))
    if rec.get("artifacts"):
        out.append("  artifacts     %d retrieved" % len(rec["artifacts"]))
    for missing in rec.get("artifacts_missing") or []:
        out.append("  MISSING       %s" % missing)
    for note in rec.get("notes") or []:
        out.append("  note          %s" % note)
    return "\n".join(out)


def write(rec, path):
    validate(rec)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        rec = json.load(fh)
    validate(rec)
    return rec
