"""Iteration 1 of the engineering ladder: one tiny pod, through the platform.

The first real launch driven by `prometheus_gpu.launch.Controller` rather
than a campaign-specific orchestrator. It proves, on hardware, what is so
far only proven against the fake: bootstrap, dependency install, canary,
telemetry, artifact retrieval, termination, absence confirmation, and a
receipt that claims only what the evidence supports.

Target: `examples/hello_gpu` on the cheapest GPU that can run it, at a
few minutes of pod time. Budget defaults to $0.30, which is six times the
projection -- the ceiling is a guardrail against a hang, not a target, and
setting it near the estimate is how a small projection error turns into
lost work (calibration ledger, 2026-09-24).

  python iteration1_flight.py --dry            # plan only, no pod
  python iteration1_flight.py --rehearse       # fake provider, no pod
  python iteration1_flight.py --go             # THE REAL LAUNCH

`--go` is required. Nothing here creates a pod without it, so the file can
be read, imported and tested safely.

PRECONDITIONS, enforced rather than remembered:
  * the controller refuses to launch if any pod is already active, or if
    the inventory read fails;
  * the credential is resolved through `credentials.py` and never printed,
    logged, placed on argv or written to the receipt;
  * the receipt is written before the process exits on every path.

One pod at a time. If AETH-02 is flying, this refuses, and that is
correct.
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "aeth01_canary"))

from prometheus_gpu import cost as cost_mod        # noqa: E402
from prometheus_gpu import credentials             # noqa: E402
from prometheus_gpu import dryrun                  # noqa: E402
from prometheus_gpu import launch                  # noqa: E402
from prometheus_gpu import provider as prov        # noqa: E402
from prometheus_gpu import receipt as rc           # noqa: E402
from prometheus_gpu import spec as spec_mod        # noqa: E402

MODULE_DIR = os.path.join(HERE, "examples", "hello_gpu")
BUNDLE_DIR = os.path.join(HERE, "examples", "dist")
REPO_BUNDLE_PATH = "Aether/runpod/examples/dist/hello_gpu-%s.tar.gz"
SPEC_PATH = os.path.join(MODULE_DIR, "module_spec.json")
RECEIPT_DIR = os.path.join(HERE, "receipts")
DEFAULT_BUDGET_USD = 0.30


def git_head():
    """The commit the pod will fetch from. Must be pushed to be reachable."""
    import subprocess
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                         capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError("cannot determine HEAD: %s" % out.stderr.strip())
    return out.stdout.strip()


def repo_transport_factory(commit):
    """A transport_factory bound to one commit, for launch.Controller."""
    def factory(bundle, run_meta):
        return dryrun.repo_transport(
            bundle, REPO_BUNDLE_PATH % bundle.sha256[:12], commit)
    return factory


def ensure_bundle_committed(spec, commit):
    """Refuse before spending if the pod could not fetch the bundle.

    Three ways this fails and all of them are free to discover here: the
    bundle was never built, it was built but not committed, or it was
    committed but not pushed. The third is the one that looks fine
    locally and fails on the pod.
    """
    from prometheus_gpu import bundle as bundle_mod
    built = bundle_mod.build(MODULE_DIR, spec)
    local = os.path.join(BUNDLE_DIR, "hello_gpu-%s.tar.gz" % built.sha256[:12])
    if not os.path.exists(local):
        raise RuntimeError(
            "bundle %s is not in %s. Build it and commit it: the pod fetches "
            "it from the pinned commit, not from this machine."
            % (built.sha256[:12], BUNDLE_DIR))
    transport = dryrun.repo_transport(
        built, REPO_BUNDLE_PATH % built.sha256[:12], commit)
    check = dryrun.check_retrievable(transport)
    if not check.get("ok"):
        raise RuntimeError(
            "the pod could not fetch %s (%s). Commit AND PUSH the bundle "
            "before launching; a pod that cannot fetch its module still bills."
            % (transport["url"], check))
    return built, transport


def log(message):
    print("[i1 %s] %s" % (time.strftime("%H:%M:%S"), message), flush=True)


def load_spec():
    return spec_mod.load(SPEC_PATH)


def show_plan(spec, workload_seconds=60.0):
    factory = dryrun.local_transport
    try:
        factory = repo_transport_factory(git_head())
    except Exception as exc:
        print("(no git HEAD: %s; planning with the controller-served "
              "transport)" % exc)
    plan = dryrun.plan(spec, MODULE_DIR, inventory=None,
                       transport_factory=factory,
                       workload_seconds=workload_seconds)
    print(dryrun.render(plan))
    projected = cost_mod.project(spec, workload_seconds=workload_seconds)
    print("\nprojected $%.4f (%.0f%% overhead) at %s"
          % (projected["usd_total"], 100 * projected["overhead_fraction"],
             projected["gpu_class"]))
    return plan


def rehearse(spec, budget_usd):
    """The whole controller path against the fake. Creates nothing."""
    telemetry = ('{"kind":"start","t_utc":"-","t_elapsed_s":0,"seq":1}\n'
                 '{"kind":"end","t_utc":"-","t_elapsed_s":1,"seq":2,'
                 '"units":200,"status":"ok"}\n')
    served = {launch.TELEMETRY_PATH: [None, telemetry]}
    for path in spec["artifacts"]:
        served.setdefault(path, '{"rehearsal": true}')
    fake = prov.FakeProvider(served=served)
    clock = [0.0]
    ctl = launch.Controller(
        fake, spec, MODULE_DIR, budget_usd=budget_usd, poll_s=1.0,
        now=lambda: clock[0],
        sleep=lambda s: clock.__setitem__(0, clock[0] + s), log=log)
    receipt_obj = ctl.run()
    print(rc.render(receipt_obj))
    if fake.leaked():
        log("DEFECT: the rehearsal leaked a pod")
        return 1
    return 0 if receipt_obj["result"] == "OK" else 1


def fly(spec, budget_usd, poll_s):
    """The real launch. The only path here that can spend money."""
    source = credentials.install_into_environ()
    log("credential source: %s" % source)        # provenance, never the value

    commit = git_head()
    built, transport = ensure_bundle_committed(spec, commit)
    log("bundle %s reachable at the pinned commit %s"
        % (built.sha256[:12], commit[:12]))

    api = prov.RunPodProvider()
    ctl = launch.Controller(api, spec, MODULE_DIR, budget_usd=budget_usd,
                            poll_s=poll_s, ready_timeout_s=300.0,
                            transport_factory=repo_transport_factory(commit),
                            log=log)
    os.makedirs(RECEIPT_DIR, exist_ok=True)
    receipt_obj = None
    try:
        receipt_obj = ctl.run()
    except launch.LaunchRefused as exc:
        # A refusal means nothing was created, so there is nothing to
        # clean up and no receipt to write.
        log("REFUSED: %s" % exc)
        return 3
    finally:
        if receipt_obj is not None:
            path = os.path.join(RECEIPT_DIR,
                                "%s.json" % receipt_obj["run_id"])
            rc.write(receipt_obj, path)
            log("receipt written to %s" % path)

    print()
    print(rc.render(receipt_obj))
    clean = receipt_obj["cleanup"]
    if not clean["operational_cleanup"]:
        log("CLEANUP NOT CLAIMED. Reconcile with: "
            "python -m prometheus_gpu.cli inventory")
        return 2
    log("ITERATION_1_%s" % ("PASS" if receipt_obj["result"] == "OK"
                            else "FAIL"))
    return 0 if receipt_obj["result"] == "OK" else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry", action="store_true", help="plan only")
    ap.add_argument("--rehearse", action="store_true",
                    help="fly the controller against the fake provider")
    ap.add_argument("--go", action="store_true",
                    help="THE REAL LAUNCH; creates a pod and spends money")
    ap.add_argument("--budget", type=float, default=DEFAULT_BUDGET_USD)
    ap.add_argument("--poll", type=float, default=20.0)
    args = ap.parse_args(argv)

    spec = load_spec()
    if args.dry or not (args.rehearse or args.go):
        show_plan(spec)
        if not (args.rehearse or args.go):
            print("\nNothing was created. Pass --rehearse for a fake flight "
                  "or --go for the real one.")
        return 0
    if args.rehearse:
        return rehearse(spec, args.budget)

    log("REAL LAUNCH, budget ceiling $%.2f" % args.budget)
    if not credentials.available():
        log("no RunPod credential configured; see credentials.py")
        return 4
    log("credential: %s" % json.dumps(credentials.describe(), sort_keys=True))
    return fly(spec, args.budget, args.poll)


if __name__ == "__main__":
    raise SystemExit(main())
