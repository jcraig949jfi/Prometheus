"""Fly any module through the platform: build, dry run, rehearse, go.

Iteration 2's reusable replacement for `iteration1_flight.py`, which was
hard-wired to `examples/hello_gpu`. Everything here works for any module
directory with a `module_spec.json`, and adds the scout path:

  python flight.py examples/gpu_load --build                 # write bundle
  python flight.py examples/gpu_load --dry                   # plan, no pod
  python flight.py examples/gpu_load --rehearse              # fake provider
  python flight.py examples/gpu_load --go --budget 0.25      # REAL

  python flight.py examples/gpu_load --scout 0.05 --build    # scout bundle
  python flight.py examples/gpu_load --scout 0.05 --go --budget 0.15

  python flight.py examples/gpu_load --calibrate receipts/<scout>.json \\
      --ceiling 0.50 --preregistered 0.029                   # plan campaign

  python flight.py examples/gpu_load --pin-gpu "NVIDIA RTX A4000" --build
  python flight.py examples/gpu_load --pin-gpu "NVIDIA RTX A4000" --go ...

`--go` is the only path that can spend. `--scout` and `--pin-gpu` change the
spec, which changes the bundle hash, so each variant is built, committed and
pushed on its own before it can fly: the pod fetches its bundle from the
pinned commit, and `ensure_bundle_committed` refuses otherwise.

EVIDENCE. A real flight writes `receipts/<run_id>.json` plus a directory
`receipts/<run_id>/` holding the platform samples, the module's telemetry
and every retrieved artifact up to `KEEP_ARTIFACT_BYTES`; larger artifacts
are recorded by size and digest only, which is what the receipt already
proves about them.
"""

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "aeth01_canary"))

from prometheus_gpu import bundle as bundle_mod    # noqa: E402
from prometheus_gpu import cost as cost_mod        # noqa: E402
from prometheus_gpu import credentials             # noqa: E402
from prometheus_gpu import dryrun                  # noqa: E402
from prometheus_gpu import launch                  # noqa: E402
from prometheus_gpu import provider as prov        # noqa: E402
from prometheus_gpu import receipt as rc           # noqa: E402
from prometheus_gpu import scout as scout_mod      # noqa: E402
from prometheus_gpu import spec as spec_mod        # noqa: E402

DIST_DIR = os.path.join(HERE, "examples", "dist")
REPO_DIST = "Aether/runpod/examples/dist"
RECEIPT_DIR = os.path.join(HERE, "receipts")
KEEP_ARTIFACT_BYTES = 1 << 20
DEFAULT_BUDGET_USD = 0.25


def log(message):
    print("[flight %s] %s" % (time.strftime("%H:%M:%S"), message), flush=True)


def module_path(arg):
    path = arg if os.path.isabs(arg) else os.path.join(HERE, arg)
    if not os.path.exists(os.path.join(path, "module_spec.json")):
        raise SystemExit("no module_spec.json in %s" % path)
    return path


def select_spec(module_dir, scout=None, pin_gpu=None, platform_interval=None):
    """The spec that will actually fly: campaign, scout, or pinned.

    Every override here edits the in-memory spec only. The bundle is built
    from the module directory's files, so its hash -- and the committed
    bundle the pod fetches -- is unchanged by any of them.
    """
    spec = spec_mod.load(os.path.join(module_dir, "module_spec.json"))
    if platform_interval:
        data = spec.to_dict()
        data["telemetry"] = dict(data["telemetry"],
                                 platform_interval_s=float(platform_interval))
        spec = spec_mod.from_dict(data, source="%s (platform every %gs)"
                                  % (spec.source, platform_interval))
    if pin_gpu:
        data = spec.to_dict()
        data["gpu"] = dict(data["gpu"], alternatives=[])
        data["gpu"]["class"] = pin_gpu
        spec = spec_mod.from_dict(data, source="%s (pinned to %s)"
                                  % (spec.source, pin_gpu))
    if scout:
        spec = scout_mod.scout_spec(spec, scout)
    return spec


def bundle_name(spec, built):
    return "%s-%s.tar.gz" % (spec.name, built.sha256[:12])


def build(module_dir, spec):
    built = bundle_mod.build(module_dir, spec)
    os.makedirs(DIST_DIR, exist_ok=True)
    path = os.path.join(DIST_DIR, bundle_name(spec, built))
    with open(path, "wb") as fh:
        fh.write(built.blob)
    return built, path


def git_head():
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                         capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError("cannot determine HEAD: %s" % out.stderr.strip())
    return out.stdout.strip()


def transport_factory(spec, commit):
    def factory(built, run_meta):
        return dryrun.repo_transport(
            built, "%s/%s" % (REPO_DIST, bundle_name(spec, built)), commit)
    return factory


def ensure_bundle_committed(module_dir, spec, commit):
    """Refuse before spending if the pod could not fetch its bundle."""
    built = bundle_mod.build(module_dir, spec)
    local = os.path.join(DIST_DIR, bundle_name(spec, built))
    if not os.path.exists(local):
        raise RuntimeError("bundle %s is not built. Run --build, commit and "
                           "push it first." % bundle_name(spec, built))
    transport = transport_factory(spec, commit)(built, None)
    check = dryrun.check_retrievable(transport)
    if not check.get("ok"):
        raise RuntimeError("the pod could not fetch %s (%s). Commit AND PUSH "
                           "the bundle before launching."
                           % (transport["url"], check))
    return built, transport


def show_plan(module_dir, spec, workload_seconds=None):
    factory = dryrun.local_transport
    try:
        factory = transport_factory(spec, git_head())
    except Exception as exc:
        print("(no git HEAD: %s; planning with the controller-served "
              "transport)" % exc)
    plan = dryrun.plan(spec, module_dir, inventory=None,
                       transport_factory=factory,
                       workload_seconds=workload_seconds)
    print(dryrun.render(plan))
    print("  module env units  PROMETHEUS_WORK_UNITS=%s"
          % int(round(float((spec.get("work_units") or {}).get("estimate",
                                                               0)))))
    print("  platform samples  every %gs -> %s"
          % (dryrun.platform_interval(spec), launch.PLATFORM_PATH))
    return plan


def rehearse(module_dir, spec, budget_usd):
    """The whole controller path against the fake. Creates nothing."""
    units = (spec.get("work_units") or {}).get("estimate", 1)
    clock = [0.0]
    telemetry = ('{"kind":"start","t_utc":"-","t_elapsed_s":0,"seq":1}\n'
                 '{"kind":"end","t_utc":"-","t_elapsed_s":1,"seq":2,'
                 '"units":%s,"status":"ok","elapsed_s":1.0}\n' % units)
    platform = json.dumps({
        "kind": "platform", "t_utc": "-", "t_elapsed_s": 0.0, "seq": 0,
        "gpus": [{"name": "FAKE", "mem_used_mib": 1.0, "mem_total_mib": 2.0,
                  "util_pct": 50.0, "temp_c": 40.0, "power_w": 70.0}],
        "sample_cost_s": 0.01}) + "\n"
    served = {launch.TELEMETRY_PATH: [None, telemetry],
              launch.PLATFORM_PATH: platform,
              launch.STAGES_PATH: '{"stage": "boot", "epoch": 1003.0}\n',
              # A pod clock deliberately 1000 s ahead, so the rehearsal
              # proves the offset is measured rather than assumed zero.
              launch.CLOCK_PATH: lambda i: json.dumps(
                  {"epoch": clock[0] + 1000.0})}
    for path in spec["artifacts"]:
        served.setdefault(path, '{"rehearsal": true}')
    fake = prov.FakeProvider(served=served)
    ctl = launch.Controller(
        fake, spec, module_dir, budget_usd=budget_usd, poll_s=10.0,
        ready_poll_s=3.0, now=lambda: clock[0],
        sleep=lambda s: clock.__setitem__(0, clock[0] + s), log=log)
    receipt_obj = ctl.run()
    print(rc.render(receipt_obj))
    print("  clock sync  %s" % json.dumps(receipt_obj["clock_sync"]["start"]))
    print("  platform    %s" % json.dumps(receipt_obj["platform_summary"]))
    if fake.leaked():
        log("DEFECT: the rehearsal leaked a pod")
        return 1
    return 0 if receipt_obj["result"] == "OK" else 1


def save_evidence(ctl, receipt_obj):
    """Receipt plus the raw rows it summarises."""
    run_dir = os.path.join(RECEIPT_DIR, receipt_obj["run_id"])
    os.makedirs(run_dir, exist_ok=True)
    kept = []
    if ctl.platform_text:
        with open(os.path.join(run_dir, "platform.jsonl"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(ctl.platform_text)
        kept.append("platform.jsonl")
    for path, blob in sorted(ctl.artifact_blobs.items()):
        if len(blob) <= KEEP_ARTIFACT_BYTES:
            with open(os.path.join(run_dir, path), "wb") as fh:
                fh.write(blob)
            kept.append(path)
    if ctl.telemetry_text and "telemetry.jsonl" not in kept:
        with open(os.path.join(run_dir, "telemetry.jsonl"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(ctl.telemetry_text)
        kept.append("telemetry.jsonl")
    receipt_obj["evidence_dir"] = os.path.relpath(run_dir, HERE).replace(
        os.sep, "/")
    receipt_obj["evidence_kept"] = kept
    path = os.path.join(RECEIPT_DIR, "%s.json" % receipt_obj["run_id"])
    rc.write(receipt_obj, path)
    return path


def fly(module_dir, spec, budget_usd, poll_s, ready_poll_s):
    """The real launch. The only path here that can spend money."""
    source = credentials.install_into_environ()
    log("credential source: %s" % source)        # provenance, never the value
    commit = git_head()
    built, transport = ensure_bundle_committed(module_dir, spec, commit)
    log("bundle %s reachable at the pinned commit %s"
        % (built.sha256[:12], commit[:12]))
    api = prov.RunPodProvider()
    ctl = launch.Controller(api, spec, module_dir, budget_usd=budget_usd,
                            poll_s=poll_s, ready_poll_s=ready_poll_s,
                            ready_timeout_s=900.0,
                            transport_factory=transport_factory(spec, commit),
                            log=log)
    os.makedirs(RECEIPT_DIR, exist_ok=True)
    receipt_obj = None
    try:
        receipt_obj = ctl.run()
    except launch.LaunchRefused as exc:
        log("REFUSED: %s" % exc)
        return 3
    finally:
        if receipt_obj is not None:
            log("receipt written to %s" % save_evidence(ctl, receipt_obj))
    print()
    print(rc.render(receipt_obj))
    print("  lifecycle   %s" % json.dumps(receipt_obj["lifecycle"]))
    print("  transfer    %s" % json.dumps(receipt_obj.get("artifact_transfer")))
    print("  platform    %s" % json.dumps(receipt_obj.get("platform_summary")))
    if not receipt_obj["cleanup"]["operational_cleanup"]:
        log("CLEANUP NOT CLAIMED. Reconcile with: "
            "python -m prometheus_gpu.cli inventory")
        return 2
    log("FLIGHT_%s" % ("PASS" if receipt_obj["result"] == "OK" else "FAIL"))
    return 0 if receipt_obj["result"] == "OK" else 1


def calibration_from_receipt(receipt_obj, spec):
    """A calibration MEASURED by a flown scout, overhead included.

    Compute is the module's own loop time from its `end` record. Overhead
    is what this scout actually spent outside that loop: the whole paid
    wall time minus the loop. Both are one sample; the margin in
    `plan_campaign` is what covers the compute estimate, and the report
    says so rather than pretending one sample is a distribution.
    """
    run_dir = os.path.join(HERE, receipt_obj.get("evidence_dir", ""))
    tel_path = os.path.join(run_dir, "telemetry.jsonl")
    loop_s = None
    if os.path.exists(tel_path):
        with open(tel_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("kind") == "end" and rec.get("elapsed_s"):
                    loop_s = float(rec["elapsed_s"])
    if loop_s is None:
        raise RuntimeError("the scout's telemetry has no end record with "
                           "elapsed_s; nothing was measured")
    units = float(receipt_obj["telemetry_summary"]["units_final"])
    wall = float(receipt_obj["cost"]["elapsed_s"])
    gpu_used = receipt_obj.get("gpu_used")
    cal = scout_mod.calibrate(
        units, loop_s, spec, hourly=cost_mod.hourly_for(gpu_used),
        overhead_seconds=max(0.0, wall - loop_s),
        source="scout receipt %s" % receipt_obj["run_id"], gpu_used=gpu_used)
    cal["scout_wall_s"] = wall
    return cal


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("module", nargs="?", default="examples/gpu_load")
    ap.add_argument("--scout", type=float, default=None,
                    help="fly a scout at this fraction of the work units")
    ap.add_argument("--pin-gpu", default=None,
                    help="pin the GPU class and drop the alternatives")
    ap.add_argument("--platform-interval", type=float, default=None,
                    help="override telemetry.platform_interval_s")
    ap.add_argument("--build", action="store_true", help="write the bundle")
    ap.add_argument("--dry", action="store_true", help="plan only")
    ap.add_argument("--rehearse", action="store_true")
    ap.add_argument("--go", action="store_true",
                    help="THE REAL LAUNCH; creates a pod and spends money")
    ap.add_argument("--budget", type=float, default=DEFAULT_BUDGET_USD)
    ap.add_argument("--poll", type=float, default=10.0)
    ap.add_argument("--ready-poll", type=float, default=3.0)
    ap.add_argument("--workload-seconds", type=float, default=None)
    ap.add_argument("--calibrate", default=None,
                    help="scout receipt to calibrate a campaign from")
    ap.add_argument("--units", type=float, default=None)
    ap.add_argument("--ceiling", type=float, default=None)
    ap.add_argument("--preregistered", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    module_dir = module_path(args.module)
    spec = select_spec(module_dir, args.scout, args.pin_gpu,
                       args.platform_interval)

    if args.calibrate:
        with open(args.calibrate, encoding="utf-8") as fh:
            scout_receipt = json.load(fh)
        cal = calibration_from_receipt(scout_receipt, spec)
        units = args.units or float(spec["work_units"]["estimate"])
        try:
            plan = scout_mod.plan_campaign(
                spec, cal, units, args.ceiling or args.budget,
                preregistered_usd=args.preregistered)
        except scout_mod.CampaignRefused as exc:
            print("CAMPAIGN REFUSED: %s" % exc)
            return 3
        plan["calibration"] = cal
        print(scout_mod.render(plan))
        if args.out:
            with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(plan, fh, indent=2, sort_keys=True)
                fh.write("\n")
            print("plan written to %s" % args.out)
        return 0 if plan["decision"] == "PROCEED" else 1

    if args.build:
        built, path = build(module_dir, spec)
        print("built %s (%d bytes) -> %s"
              % (built.sha256[:12], built.bytes,
                 os.path.relpath(path, os.path.dirname(HERE))))
        if not (args.dry or args.rehearse or args.go):
            return 0
    if args.dry or not (args.rehearse or args.go):
        show_plan(module_dir, spec, args.workload_seconds)
        if not (args.rehearse or args.go):
            print("\nNothing was created. Pass --rehearse for a fake flight "
                  "or --go for the real one.")
        return 0
    if args.rehearse:
        return rehearse(module_dir, spec, args.budget)

    log("REAL LAUNCH %s, budget ceiling $%.2f" % (spec.identity, args.budget))
    if not credentials.available():
        log("no RunPod credential configured; see credentials.py")
        return 4
    log("credential: %s" % json.dumps(credentials.describe(), sort_keys=True))
    return fly(module_dir, spec, args.budget, args.poll, args.ready_poll)


if __name__ == "__main__":
    raise SystemExit(main())
