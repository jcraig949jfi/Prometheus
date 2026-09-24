"""prometheus-gpu: the command surface a seat actually uses.

    python -m prometheus_gpu.cli estimate  spec.json
    python -m prometheus_gpu.cli dry-run   spec.json [--out plan.json]
    python -m prometheus_gpu.cli bundle    spec.json [--out bundle.tar.gz]
    python -m prometheus_gpu.cli inventory
    python -m prometheus_gpu.cli cleanup   [--pod ID ...] [--all]

No seat should have to construct RunPod JSON to run an ordinary
experiment, and `estimate` and `dry-run` never touch the provider's
write path at all.

WHY `run` IS NOT HERE YET. The launch path is being qualified rung by
rung against the real provider, and a half-qualified `run` command is
worse than none: it invites a seat to spend money through a path that
has not yet demonstrated cleanup after an ambiguous create. `dry-run`
emits the exact request and the receipt skeleton, so nothing is blocked
in the meantime. `run` lands when Iteration 1 has flown.
"""

import argparse
import json
import os
import sys

from . import bundle as bundle_mod
from . import cost as cost_mod
from . import dryrun
from . import spec as spec_mod


def _load(path):
    try:
        return spec_mod.load(path)
    except spec_mod.SpecError as exc:
        print("SPEC REJECTED: %s" % exc, file=sys.stderr)
        raise SystemExit(2)


def _module_dir(spec_path, override):
    return override or os.path.dirname(os.path.abspath(spec_path)) or "."


def _inventory_callable():
    """Read-only pod inventory, or None when no credential is configured.

    Returns a BOUND METHOD, never a provider object: nothing the dry run
    holds may be able to create a pod.
    """
    from . import credentials
    if not credentials.available():
        return None
    try:
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "aeth01_canary"))
        credentials.install_into_environ()
        from . import provider as prov
        return prov.RunPodProvider().list_pods
    except Exception as exc:
        print("inventory unavailable (%s); dry run continues without it"
              % type(exc).__name__, file=sys.stderr)
        return None


def cmd_estimate(args):
    spec = _load(args.spec)
    projected = cost_mod.project(spec, workload_seconds=args.workload_seconds)
    print(json.dumps(projected, indent=2, sort_keys=True))
    return 0


def cmd_bundle(args):
    spec = _load(args.spec)
    built = bundle_mod.build(_module_dir(args.spec, args.module_dir), spec)
    print(json.dumps(built.summary(), indent=2, sort_keys=True))
    if args.out:
        with open(args.out, "wb") as fh:
            fh.write(built.blob)
        print("wrote %s (%d bytes)" % (args.out, built.bytes))
    return 0


def cmd_dry_run(args):
    spec = _load(args.spec)
    inventory = None if args.no_inventory else _inventory_callable()
    plan = dryrun.plan(spec, _module_dir(args.spec, args.module_dir),
                       inventory=inventory,
                       workload_seconds=args.workload_seconds)
    print(dryrun.render(plan))
    if args.out:
        dryrun.write_plan(plan, args.out)
        print("\nplan written to %s" % args.out)
    # A dry run with findings still exits 0: findings are advice, not
    # errors. A spec that would lose money or data was already refused
    # by validation with exit 2.
    return 0


def cmd_inventory(args):
    from . import credentials
    print("credential: %s" % json.dumps(credentials.describe(), sort_keys=True))
    inv = _inventory_callable()
    if inv is None:
        print("no provider credential configured; inventory unavailable")
        return 1
    pods = inv()
    print(json.dumps({"active": len(pods),
                      "ids": [p.get("id") for p in pods]}, indent=2))
    return 0


def cmd_cleanup(args):
    from . import credentials, provider as prov
    credentials.install_into_environ()
    api = prov.RunPodProvider()
    targets = list(args.pod or [])
    if args.all:
        targets += [p["id"] for p in api.list_pods() if p["id"] not in targets]
    if not targets:
        print("nothing to clean; inventory is empty")
        return 0
    receipt = {"terminate_acknowledged": [], "observed_absent": [],
               "failed": []}
    for pod_id in targets:
        try:
            api.terminate_pod(pod_id)
            receipt["terminate_acknowledged"].append(pod_id)
        except prov.ProviderError as exc:
            receipt["failed"].append({"pod": pod_id, "status": exc.status})
    remaining = {p["id"] for p in api.list_pods()}
    receipt["observed_absent"] = [p for p in targets if p not in remaining]
    receipt["still_present"] = sorted(remaining & set(targets))
    # Four different claims, kept apart on purpose.
    receipt["operational_cleanup"] = (not receipt["still_present"]
                                      and not receipt["failed"])
    receipt["billing_reconciled"] = False
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["operational_cleanup"] else 1


def build_parser():
    p = argparse.ArgumentParser(prog="prometheus-gpu",
                                description="Prometheus GPU flight system")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, needs_spec in (("estimate", cmd_estimate, True),
                                 ("dry-run", cmd_dry_run, True),
                                 ("bundle", cmd_bundle, True),
                                 ("inventory", cmd_inventory, False),
                                 ("cleanup", cmd_cleanup, False)):
        sp = sub.add_parser(name)
        sp.set_defaults(func=fn)
        if needs_spec:
            sp.add_argument("spec")
            sp.add_argument("--module-dir", default=None)
            sp.add_argument("--workload-seconds", type=float, default=None)
            sp.add_argument("--out", default=None)
        if name == "dry-run":
            sp.add_argument("--no-inventory", action="store_true")
        if name == "cleanup":
            sp.add_argument("--pod", action="append")
            sp.add_argument("--all", action="store_true")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
