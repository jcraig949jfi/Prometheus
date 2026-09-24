"""prometheus-gpu: the command surface a seat actually uses.

    python -m prometheus_gpu.cli estimate  spec.json
    python -m prometheus_gpu.cli dry-run   spec.json [--out plan.json]
    python -m prometheus_gpu.cli bundle    spec.json [--out bundle.tar.gz]
    python -m prometheus_gpu.cli rehearse  spec.json [--verbose]
    python -m prometheus_gpu.cli scout     spec.json --scale 0.02
    python -m prometheus_gpu.cli campaign  spec.json --calibration cal.json                                            --units 1e11 --ceiling 3.00
    python -m prometheus_gpu.cli inventory
    python -m prometheus_gpu.cli cleanup   [--pod ID ...] [--all]
    python -m prometheus_gpu.cli validate-telemetry telemetry.jsonl
    python -m prometheus_gpu.cli validate-receipt   receipt.json

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


def cmd_rehearse(args):
    """Fly the whole launch path against the FAKE provider. $0.00.

    A dry run proves the request is well formed. A rehearsal proves the
    controller can carry THIS spec from create through retrieval,
    termination and a valid receipt -- including the parts that only exist
    at launch time, like the credential assertion on the real request.
    Nothing here can reach a provider: the fake is constructed locally and
    no credential is resolved.
    """
    from . import launch, provider as prov, receipt as rc
    spec = _load(args.spec)
    telemetry = ('{"kind":"start","t_utc":"-","t_elapsed_s":0,"seq":1}\n'
                 '{"kind":"end","t_utc":"-","t_elapsed_s":1,"seq":2,'
                 '"units":%s,"status":"ok"}\n'
                 % ((spec.get("work_units") or {}).get("estimate", 1)))
    served = {launch.TELEMETRY_PATH: [None, telemetry]}
    for path in spec["artifacts"]:
        # setdefault, not assignment: a module that declares its telemetry
        # file as an artifact would otherwise have the synthetic telemetry
        # overwritten by placeholder bytes, and the rehearsal would report
        # a spurious TIMEOUT. It did, the first time this ran.
        served.setdefault(path, '{"rehearsal": true}')
    fake = prov.FakeProvider(served=served)
    clock = [0.0]
    ctl = launch.Controller(
        fake, spec, _module_dir(args.spec, args.module_dir),
        budget_usd=args.budget or 1.0, poll_s=1.0,
        now=lambda: clock[0], sleep=lambda s: clock.__setitem__(0, clock[0] + s),
        log=(lambda m: print("  " + m)) if args.verbose else None)
    receipt_obj = ctl.run()
    print(rc.render(receipt_obj))
    print("\nREHEARSAL ONLY. No pod existed; the provider was a fake and no "
          "credential was resolved.")
    if fake.leaked():
        print("DEFECT: the rehearsal leaked a pod. Report this.",
              file=sys.stderr)
        return 1
    if args.out:
        rc.write(receipt_obj, args.out)
        print("receipt written to %s" % args.out)
    return 0 if receipt_obj["result"] == "OK" else 1


def cmd_scout(args):
    """Emit the reduced spec for a representative calibration run.

    Only the work-unit count and the runtime bound shrink. GPU class,
    dependencies, entrypoint, args and environment are carried over
    unchanged, because a scout that quietly dropped the instrumentation
    would reproduce the AETH-02 miss exactly.
    """
    from . import scout as scout_mod
    spec = _load(args.spec)
    try:
        reduced = scout_mod.scout_spec(spec, args.scale)
    except ValueError as exc:
        print("SCOUT REFUSED: %s" % exc, file=sys.stderr)
        return 2
    rep = scout_mod.representativeness(reduced, spec)
    print(json.dumps(reduced.to_dict(), indent=2, sort_keys=True))
    print("\nrepresentative: %s%s"
          % (rep["representative"],
             "" if rep["representative"]
             else "  DIFFERS IN: " + ", ".join(sorted(rep["differences"]))),
          file=sys.stderr)
    projected = cost_mod.project(reduced, workload_seconds=None)
    print("scout ceiling cost $%.4f" % projected["usd_total"], file=sys.stderr)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(reduced.to_dict(), fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("wrote %s" % args.out, file=sys.stderr)
    return 0


def cmd_campaign(args):
    """Plan a campaign from a MEASURED calibration, or refuse it.

    The calibration JSON is what `scout.calibrate` produced from a scout
    run. The decision is taken on the estimate PLUS its margin, because a
    ceiling met by the bare estimate is a ceiling that a 7% miss turns
    into a truncated run -- which is what happened to AETH-02.
    """
    from . import scout as scout_mod
    spec = _load(args.spec)
    with open(args.calibration, encoding="utf-8") as fh:
        calibration = json.load(fh)
    try:
        plan = scout_mod.plan_campaign(
            spec, calibration, args.units, args.ceiling, pods=args.pods,
            margin=args.margin,
            accept_differences=args.accept_differences,
            preregistered_usd=args.preregistered)
    except scout_mod.CampaignRefused as exc:
        print("CAMPAIGN REFUSED: %s" % exc, file=sys.stderr)
        return 3
    print(scout_mod.render(plan))
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(plan, fh, indent=2, sort_keys=True)
            fh.write("\n")
    return 0 if plan["decision"] == "PROCEED" else 1


def cmd_validate_telemetry(args):
    from . import telemetry as tel
    try:
        records, summary = tel.validate_file(args.path)
    except tel.TelemetryError as exc:
        print("TELEMETRY REJECTED: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary.get("complete"):
        print("\nNOTE: no `end` record. The module never reported finishing, "
              "which is not the same as the run having failed.", file=sys.stderr)
    return 0


def cmd_validate_receipt(args):
    from . import receipt as rc
    try:
        rec = rc.load(args.path)
    except rc.ReceiptError as exc:
        print("RECEIPT REJECTED: %s" % exc, file=sys.stderr)
        return 2
    print(rc.render(rec))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="prometheus-gpu",
                                description="Prometheus GPU flight system")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, needs_spec in (("estimate", cmd_estimate, True),
                                 ("dry-run", cmd_dry_run, True),
                                 ("bundle", cmd_bundle, True),
                                 ("rehearse", cmd_rehearse, True),
                                 ("scout", cmd_scout, True),
                                 ("campaign", cmd_campaign, True),
                                 ("inventory", cmd_inventory, False),
                                 ("cleanup", cmd_cleanup, False),
                                 ("validate-telemetry",
                                  cmd_validate_telemetry, False),
                                 ("validate-receipt",
                                  cmd_validate_receipt, False)):
        sp = sub.add_parser(name)
        sp.set_defaults(func=fn)
        if name.startswith("validate-"):
            sp.add_argument("path")
        if needs_spec:
            sp.add_argument("spec")
            sp.add_argument("--module-dir", default=None)
            sp.add_argument("--workload-seconds", type=float, default=None)
            sp.add_argument("--out", default=None)
        if name == "dry-run":
            sp.add_argument("--no-inventory", action="store_true")
        if name == "scout":
            sp.add_argument("--scale", type=float, default=0.02)
        if name == "campaign":
            sp.add_argument("--calibration", required=True)
            sp.add_argument("--units", type=float, required=True)
            sp.add_argument("--ceiling", type=float, required=True)
            sp.add_argument("--pods", type=int, default=1)
            sp.add_argument("--margin", type=float, default=0.20)
            sp.add_argument("--preregistered", type=float, default=None)
            sp.add_argument("--accept-differences", action="store_true",
                            dest="accept_differences")
        if name == "rehearse":
            sp.add_argument("--budget", type=float, default=None)
            sp.add_argument("--verbose", action="store_true")
        if name == "cleanup":
            sp.add_argument("--pod", action="append")
            sp.add_argument("--all", action="store_true")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
