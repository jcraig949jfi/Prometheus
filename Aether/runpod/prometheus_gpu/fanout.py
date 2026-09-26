"""Several pods at once, on independent shards, with honest aggregation.

Each shard is an ordinary single-pod run through `launch.Controller`, so it
keeps every property Iterations 1-3 qualified: inventory before create,
reconcile by name, retrieve before terminate, terminate in a `finally`,
absence by LIST and GET together, a ledger per shard, a receipt per shard.
What this module adds is the campaign around them:

  ONE CAMPAIGN PREFLIGHT. Before ANY shard creates, the account must hold
  nothing but pods named for this campaign's shards (normally: nothing).
  One-pod-at-a-time was a budget guarantee; its campaign form is "exactly
  the pods this campaign declared, and no others".

  NAMES ARE THE OWNERSHIP. Shard run ids are `<campaign>-<shard>`, unique
  by construction, and each shard's controller may see only its siblings'
  names without refusing. Artifacts land under each shard's own run id,
  so two shards cannot collide on a path.

  ISOLATION, NOT FAIL-FAST, BY DEFAULT. A failed shard is recorded and
  cleaned; its siblings run on. `fail_fast=True` (a module contract may
  ask for it) makes the first failure abort the rest, recorded as
  `CAMPAIGN_FAIL_FAST`, never as their own failure.

  HONEST AGGREGATE. OK only if every shard is OK; PARTIAL if some are;
  FAILED if none; UNKNOWN if any shard is UNKNOWN. Cleanup is claimed for
  the campaign only if every shard's own receipt claims it. Cost is the
  sum of the shards' estimates, each still unreconciled.
"""

import threading

from . import launch
from . import provider as prov


class CampaignRefused(RuntimeError):
    """The campaign preflight failed. No shard created anything."""


def shard_run_id(campaign_id, shard_id):
    return ("%s-%s" % (campaign_id, shard_id))[:63]


def aggregate(results):
    kinds = [r["result"] for r in results]
    if any(k == "UNKNOWN" for k in kinds):
        overall = "UNKNOWN"
    elif all(k == "OK" for k in kinds):
        overall = "OK"
    elif any(k == "OK" for k in kinds):
        overall = "PARTIAL"
    else:
        overall = "FAILED"
    return overall


def run(provider_factory, shards, campaign_id, controller_kwargs=None,
        fail_fast=False, log=lambda m: None, concurrent=True):
    """`shards`: list of dicts {id, spec, module_dir, budget_usd, **kw}.

    `provider_factory()` returns a provider; each shard gets its own, so no
    provider object is shared between threads.
    """
    controller_kwargs = dict(controller_kwargs or {})
    names = [shard_run_id(campaign_id, s["id"]) for s in shards]
    if len(set(names)) != len(names):
        raise CampaignRefused("two shards map to the same run id: %s" % names)

    # The campaign preflight: before any create.
    try:
        pods = provider_factory().list_pods()
    except prov.ProviderError as exc:
        raise CampaignRefused("inventory read failed (status=%s); refusing "
                              "to start %d pods blind" % (exc.status,
                                                          len(shards)))
    foreign = [p for p in pods if p.get("name") not in set(names)]
    if foreign:
        raise CampaignRefused(
            "%d pod(s) not belonging to this campaign are active (%s); "
            "refusing before any shard creates"
            % (len(foreign), ", ".join(str(p.get("id")) for p in foreign)))

    abort = threading.Event()
    results = [None] * len(shards)
    controllers = [None] * len(shards)

    def one(index, shard):
        run_id = names[index]
        kwargs = dict(controller_kwargs)
        kwargs.update(shard.get("controller_kwargs") or {})
        if fail_fast:
            kwargs["should_abort"] = abort.is_set
        ctl = launch.Controller(
            provider_factory(), shard["spec"], shard["module_dir"],
            budget_usd=shard["budget_usd"], run_id=run_id,
            allowed_pod_names=set(names) - {run_id},
            log=lambda m, _r=run_id: log("[%s] %s" % (_r, m)), **kwargs)
        controllers[index] = ctl
        try:
            receipt_obj = ctl.run()
        except launch.LaunchRefused as exc:
            receipt_obj = {"run_id": run_id, "result": "NOT_RUN",
                           "refused": str(exc), "cleanup": {
                               "operational_cleanup": True},
                           "cost": {"usd_estimated": 0.0}}
        results[index] = receipt_obj
        if fail_fast and receipt_obj.get("result") not in ("OK",):
            abort.set()

    if concurrent:
        threads = [threading.Thread(target=one, args=(i, s), daemon=False)
                   for i, s in enumerate(shards)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        for i, s in enumerate(shards):
            one(i, s)

    per_shard = []
    for name, shard, rec in zip(names, shards, results):
        cleanup = rec.get("cleanup") or {}
        integ = rec.get("artifact_integrity") or {}
        per_shard.append({
            "shard": shard["id"], "run_id": name,
            "result": rec.get("result"),
            "cause": (rec.get("disposition") or {}).get("cause"),
            "pod_ids": [p.get("id") for p in rec.get("pods") or []],
            "gpu_used": rec.get("gpu_used"),
            "usd_estimated": (rec.get("cost") or {}).get("usd_estimated"),
            "operational_cleanup": bool(cleanup.get("operational_cleanup")),
            "artifacts_verified": integ.get("verified", []),
            "artifacts_missing": rec.get("artifacts_missing", []),
        })
    pod_ids = [pid for s in per_shard for pid in s["pod_ids"] if pid]
    out = {
        "schema": "prometheus-gpu/campaign-receipt/1",
        "campaign_id": campaign_id,
        "fail_fast": bool(fail_fast),
        "result": aggregate(results),
        "shards": per_shard,
        "distinct_pods": len(set(pod_ids)) == len(pod_ids),
        "operational_cleanup": all(s["operational_cleanup"]
                                   for s in per_shard),
        "usd_estimated_total": round(sum(s["usd_estimated"] or 0.0
                                         for s in per_shard), 5),
        "billing_reconciled": False,
    }
    return out, results, controllers
