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
from prometheus_gpu import campaign as campaign_mod  # noqa: E402
from prometheus_gpu import fanout as fanout_mod    # noqa: E402
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
# Controller ledgers hold the artifact token, so they live OUTSIDE the
# repository's tracked tree (gitignored). A receipt never carries one.
LEDGER_DIR = os.path.join(HERE, ".ledger")
KEEP_ARTIFACT_BYTES = 1 << 20
DEFAULT_BUDGET_USD = 0.25


def log(message):
    print("[flight %s] %s" % (time.strftime("%H:%M:%S"), message), flush=True)


def module_path(arg):
    path = arg if os.path.isabs(arg) else os.path.join(HERE, arg)
    if not os.path.exists(os.path.join(path, "module_spec.json")):
        raise SystemExit("no module_spec.json in %s" % path)
    return path


def select_spec(module_dir, scout=None, pin_gpu=None, platform_interval=None,
                units=None, env=None):
    """The spec that will actually fly: campaign, scout, or pinned.

    Every override here edits the in-memory spec only. The bundle is built
    from the module directory's files, so its hash -- and the committed
    bundle the pod fetches -- is unchanged by any of them.
    """
    spec = spec_mod.load(os.path.join(module_dir, "module_spec.json"))
    if env:
        # In-memory, like every other override: the module's files -- and
        # so the committed bundle -- are unchanged. The spec's own allowlist
        # still decides which names may be set.
        data = spec.to_dict()
        data["env"] = dict(data["env"], **env)
        spec = spec_mod.from_dict(data, source="%s (env %s)"
                                  % (spec.source, ",".join(sorted(env))))
    if units:
        data = spec.to_dict()
        data["work_units"] = dict(data["work_units"], estimate=float(units))
        spec = spec_mod.from_dict(data, source="%s (%g units)"
                                  % (spec.source, units))
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


def rehearse(module_dir, spec, budget_usd, plan=None):
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
    if plan is not None:
        attach_plan(receipt_obj, plan)
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
    for name, rows in (("controller_health.jsonl", ctl.health),
                       ("api_calls.jsonl", ctl.api_calls)):
        if rows:
            with open(os.path.join(run_dir, name), "w", encoding="utf-8",
                      newline="\n") as fh:
                for row in rows:
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
            kept.append(name)
    if ctl._ledger_state:
        # The ledger's EVENTS only; the ledger itself holds the token.
        with open(os.path.join(run_dir, "ledger_events.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump(ctl._ledger_state.get("events", []), fh, indent=1)
            fh.write("\n")
        kept.append("ledger_events.json")
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


def load_campaign_plan(path, spec):
    """A campaign plan from `--calibrate`, checked against what will fly.

    Refuses a plan that did not PROCEED, one for a different module, or one
    for a different amount of work: the receipt would otherwise carry an
    estimate for some other run.
    """
    with open(path, encoding="utf-8") as fh:
        plan = json.load(fh)
    if plan.get("decision") != "PROCEED":
        raise RuntimeError("the campaign plan decided %r, not PROCEED"
                           % plan.get("decision"))
    if plan.get("module") != spec.identity:
        raise RuntimeError("the plan is for %s, not %s"
                           % (plan.get("module"), spec.identity))
    planned = float(plan["calibrated_estimate"]["requested_units"])
    flying = float(spec["work_units"]["estimate"])
    if planned != flying:
        raise RuntimeError("the plan priced %g units but this flight does %g"
                           % (planned, flying))
    if plan.get("preregistered_estimate") is None:
        raise RuntimeError("the plan has no preregistered_estimate; a "
                           "calibration without what it replaced hides the "
                           "miss (receipt.validate refuses it too)")
    return plan


def attach_plan(receipt_obj, plan):
    """Both estimates into the receipt, beside what actually happened."""
    receipt_obj["preregistered_estimate"] = plan["preregistered_estimate"]
    receipt_obj["calibrated_estimate"] = plan["calibrated_estimate"]
    receipt_obj["campaign_plan"] = {
        "decision": plan["decision"],
        "ceiling_usd": plan["ceiling_usd"],
        "calibration_source": (plan.get("calibration") or {}).get("source"),
        "calibration_gpu": (plan.get("calibration") or {}).get("gpu_used"),
    }
    # The canonical record: spec sheet, scout, actual, and both errors.
    receipt_obj["estimates"] = rc.estimates_block(
        plan["preregistered_estimate"]["expected_usd"],
        plan["calibrated_estimate"]["expected_usd"],
        (receipt_obj.get("cost") or {}).get("usd_estimated"))
    rc.validate(receipt_obj)
    return receipt_obj


def kill_hook(ctl, kill_at_s):
    """REAL controller death for qualification: os._exit, no `finally`.

    Fires on the first watch poll at least `kill_at_s` after the module's
    first telemetry. The pod keeps running and billing; the only record of
    it is the ledger, and `--resume <ledger>` is the recovery being tested.
    """
    def hook(event):
        first = ctl.marks.get("first_telemetry")
        if event == "watch" and first is not None and \
                time.time() - first >= kill_at_s:
            log("KILLING THE CONTROLLER NOW (os._exit 137) with pod %s "
                "running; ledger %s" % (ctl.pod_id, ctl.ledger_path))
            sys.stdout.flush()
            os._exit(137)
    return hook


def make_controller(module_dir, spec, budget_usd, poll_s, ready_poll_s,
                    commit, plan=None, ctl_kwargs=None, resume_ledger=None,
                    provider=None, run_id=None, allowed_pod_names=None):
    kwargs = dict(ctl_kwargs or {})
    if plan is not None and not kwargs.get("expected_module_s"):
        est = plan["calibrated_estimate"]
        kwargs["expected_module_s"] = (est["per_pod_expected_seconds"]
                                       - est["overhead_seconds_per_pod"])
    return launch.Controller(provider or prov.RunPodProvider(), spec,
                             module_dir, budget_usd=budget_usd,
                             poll_s=poll_s, ready_poll_s=ready_poll_s,
                             ready_timeout_s=900.0,
                             transport_factory=transport_factory(spec, commit),
                             log=log, ledger_dir=LEDGER_DIR,
                             ledger_path=resume_ledger, run_id=run_id,
                             allowed_pod_names=allowed_pod_names, **kwargs)


def fly_receipt(module_dir, spec, budget_usd, poll_s, ready_poll_s, plan=None,
                kill_at_s=None, ctl_kwargs=None, resume_ledger=None):
    """The real launch (or resume). Returns (code, receipt or None)."""
    source = credentials.install_into_environ()
    log("credential source: %s" % source)        # provenance, never the value
    commit = git_head()
    built, transport = ensure_bundle_committed(module_dir, spec, commit)
    log("bundle %s reachable at the pinned commit %s"
        % (built.sha256[:12], commit[:12]))
    ctl = make_controller(module_dir, spec, budget_usd, poll_s, ready_poll_s,
                          commit, plan=plan, ctl_kwargs=ctl_kwargs,
                          resume_ledger=resume_ledger)
    if kill_at_s is not None:
        ctl.crash_hook = kill_hook(ctl, kill_at_s)
    os.makedirs(RECEIPT_DIR, exist_ok=True)
    receipt_obj = None
    try:
        if resume_ledger:
            receipt_obj = ctl.resume(launch.load_ledger(resume_ledger))
        else:
            receipt_obj = ctl.run()
    except launch.LaunchRefused as exc:
        log("REFUSED: %s" % exc)
        return 3, None
    finally:
        if receipt_obj is not None:
            if plan is not None:
                attach_plan(receipt_obj, plan)
            log("receipt written to %s" % save_evidence(ctl, receipt_obj))
    return None, receipt_obj


def fly(module_dir, spec, budget_usd, poll_s, ready_poll_s, plan=None,
        kill_at_s=None, ctl_kwargs=None, resume_ledger=None):
    """The real launch. The only path here that can spend money."""
    code, receipt_obj = fly_receipt(module_dir, spec, budget_usd, poll_s,
                                    ready_poll_s, plan=plan,
                                    kill_at_s=kill_at_s,
                                    ctl_kwargs=ctl_kwargs,
                                    resume_ledger=resume_ledger)
    if receipt_obj is None:
        return code
    print()
    print(rc.render(receipt_obj))
    print("  lifecycle   %s" % json.dumps(receipt_obj["lifecycle"]))
    print("  transfer    %s" % json.dumps(receipt_obj.get("artifact_transfer")))
    print("  platform    %s" % json.dumps(receipt_obj.get("platform_summary")))
    print("  disposition %s" % json.dumps(receipt_obj.get("disposition")))
    print("  api         %s" % json.dumps(receipt_obj.get("api_latency")))
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


def parse_env(pairs):
    out = {}
    for item in pairs or []:
        if "=" not in item:
            raise SystemExit("--env wants KEY=VALUE, got %r" % item)
        key, value = item.split("=", 1)
        out[key] = value
    return out


def auto(module_dir, args, env):
    """dry-run -> scout -> calibrate -> campaign, re-scouting on refusal."""
    commit = git_head()
    ctl_kwargs = controller_options(args)

    def fly_scout():
        spec = select_spec(module_dir, scout=args.scout or 0.05,
                           platform_interval=args.platform_interval, env=env)
        _code, rec = fly_receipt(module_dir, spec, args.scout_budget,
                                 args.poll, args.ready_poll,
                                 ctl_kwargs=ctl_kwargs)
        return rec

    def calibrate(scout_receipt):
        gpu = scout_receipt.get("gpu_used")
        spec = select_spec(module_dir, pin_gpu=gpu,
                           platform_interval=args.platform_interval,
                           units=args.units, env=env)
        cal = calibration_from_receipt(scout_receipt, spec)
        units = args.units or float(spec["work_units"]["estimate"])
        try:
            plan = scout_mod.plan_campaign(spec, cal, units,
                                           args.ceiling or args.budget,
                                           preregistered_usd=args.preregistered)
        except scout_mod.CampaignRefused as exc:
            return {"decision": "REFUSE", "refused": str(exc)}
        plan["calibration"] = cal
        print(scout_mod.render(plan))
        return plan

    def fly_campaign(plan, gpu):
        spec = select_spec(module_dir, pin_gpu=gpu,
                           platform_interval=args.platform_interval,
                           units=args.units, env=env)
        budget = max(args.budget, plan["recommended_controller_ceiling_usd"])
        _code, rec = fly_receipt(module_dir, spec, budget, args.poll,
                                 args.ready_poll, plan=plan,
                                 ctl_kwargs=ctl_kwargs)
        return rec

    del commit
    out = campaign_mod.run(fly_scout, calibrate, fly_campaign,
                           max_rescouts=args.max_rescouts, log=log)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = os.path.join(RECEIPT_DIR, "auto-%s-%s.json"
                        % (os.path.basename(module_dir), stamp))
    slim = dict(out)
    slim["flights"] = [{"role": f["role"],
                        "run_id": (f.get("receipt") or {}).get("run_id"),
                        "result": (f.get("receipt") or {}).get("result"),
                        "gpu_used": (f.get("receipt") or {}).get("gpu_used")}
                       for f in out["flights"]]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(slim, fh, indent=2, sort_keys=True, default=str)
        fh.write("\n")
    log("auto campaign summary written to %s" % path)
    print(json.dumps({k: slim[k] for k in ("decision", "stopped_because",
                                           "rescouts", "estimates")},
                     indent=1, default=str))
    return 0 if out.get("campaign_result") == "OK" else 1


def controller_options(args):
    out = {}
    if args.telemetry_stall is not None:
        out["telemetry_stall_s"] = args.telemetry_stall
    if args.unreachable is not None:
        out["unreachable_s"] = args.unreachable
    if args.expected_module_s is not None:
        out["expected_module_s"] = args.expected_module_s
    return out


def fanout(module_dir, args, env, rehearse_only=False):
    """Several pods at once from a shard file:

        {"campaign_id": "i4", "budget_usd_per_shard": 0.05,
         "shards": [{"id": "a", "env": {"SOAK_SEED": "1"}, "units": 180},
                    ...]}
    """
    with open(args.fanout, encoding="utf-8") as fh:
        conf = json.load(fh)
    commit = git_head() if not rehearse_only else None
    shards = []
    for sh in conf["shards"]:
        spec = select_spec(module_dir, pin_gpu=args.pin_gpu,
                           platform_interval=args.platform_interval,
                           units=sh.get("units"),
                           env=dict(env, **(sh.get("env") or {})))
        shards.append({"id": sh["id"], "spec": spec, "module_dir": module_dir,
                       "budget_usd": float(conf["budget_usd_per_shard"])})
    campaign_id = "%s-%s" % (conf["campaign_id"],
                             time.strftime("%H%M%S", time.gmtime()))
    kwargs = dict(controller_options(args), poll_s=args.poll,
                  ready_poll_s=args.ready_poll, ready_timeout_s=900.0,
                  ledger_dir=LEDGER_DIR)
    if rehearse_only:
        fake = rehearsal_fake(shards, campaign_id)
        clock = [0.0]
        kwargs.update(now=lambda: clock[0],
                      sleep=lambda s: clock.__setitem__(0, clock[0] + s),
                      ledger_dir=None)
        factory = lambda: fake                                  # noqa: E731
    else:
        source = credentials.install_into_environ()
        log("credential source: %s" % source)
        for shard in shards:
            ensure_bundle_committed(module_dir, shard["spec"], commit)
        kwargs["transport_factory"] = transport_factory(shards[0]["spec"],
                                                        commit)
        factory = prov.RunPodProvider
    out, results, ctls = fanout_mod.run(
        factory, shards, campaign_id, controller_kwargs=kwargs,
        fail_fast=args.fail_fast, log=log, concurrent=True)
    if not rehearse_only:
        os.makedirs(RECEIPT_DIR, exist_ok=True)
        for ctl, rec in zip(ctls, results):
            if ctl is not None and rec is not None and "schema" in rec:
                save_evidence(ctl, rec)
        path = os.path.join(RECEIPT_DIR, "%s.campaign.json" % campaign_id)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
            fh.write("\n")
        log("campaign receipt written to %s" % path)
    print(json.dumps(out, indent=1))
    if rehearse_only and fake.leaked():
        log("DEFECT: the fan-out rehearsal leaked a pod")
        return 1
    return 0 if out["operational_cleanup"] else 2


def rehearsal_fake(shards, campaign_id):
    served = {}
    for sh in shards:
        name = fanout_mod.shard_run_id(campaign_id, sh["id"])
        fail = (sh["spec"]["env"].get("SOAK_FAULT", "none") != "none")
        end = ('{"kind":"end","t_utc":"-","t_elapsed_s":1,"seq":2,"units":1,'
               '"status":"%s"}\n' % ("failed" if fail else "ok"))
        tel = '{"kind":"start","t_utc":"-","t_elapsed_s":0,"seq":1}\n' + end
        files = {path: '{"rehearsal": true}' for path in sh["spec"]["artifacts"]}
        files[launch.TELEMETRY_PATH] = [None, tel]
        served[name] = files
    return prov.FakeProvider(served_by_name=served)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("module", nargs="?", default="examples/gpu_load")
    ap.add_argument("--scout", type=float, default=None,
                    help="fly a scout at this fraction of the work units")
    ap.add_argument("--pin-gpu", default=None,
                    help="pin the GPU class and drop the alternatives")
    ap.add_argument("--platform-interval", type=float, default=None,
                    help="override telemetry.platform_interval_s")
    ap.add_argument("--env", action="append", default=[],
                    help="KEY=VALUE module env override (allowlisted names "
                         "only; in-memory, the bundle is unchanged)")
    ap.add_argument("--build", action="store_true", help="write the bundle")
    ap.add_argument("--dry", action="store_true", help="plan only")
    ap.add_argument("--rehearse", action="store_true")
    ap.add_argument("--go", action="store_true",
                    help="THE REAL LAUNCH; creates a pod and spends money")
    ap.add_argument("--budget", type=float, default=DEFAULT_BUDGET_USD)
    ap.add_argument("--scout-budget", type=float, default=0.05)
    ap.add_argument("--poll", type=float, default=10.0)
    ap.add_argument("--ready-poll", type=float, default=3.0)
    ap.add_argument("--workload-seconds", type=float, default=None)
    ap.add_argument("--calibrate", default=None,
                    help="scout receipt to calibrate a campaign from")
    ap.add_argument("--units", type=float, default=None,
                    help="work units to plan for, or to fly (in-memory; "
                         "the bundle is unchanged)")
    ap.add_argument("--plan", default=None,
                    help="campaign plan from --calibrate; both estimates "
                         "go into the receipt")
    ap.add_argument("--ceiling", type=float, default=None)
    ap.add_argument("--preregistered", type=float, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--auto", action="store_true",
                    help="with --go: scout, calibrate and fly the campaign "
                         "in one command, re-scouting on a capacity refusal")
    ap.add_argument("--max-rescouts", type=int,
                    default=campaign_mod.DEFAULT_MAX_RESCOUTS)
    ap.add_argument("--resume", default=None,
                    help="resume a run from its ledger (.ledger/<run>.json); "
                         "never creates")
    ap.add_argument("--kill-controller-at", type=float, default=None,
                    help="QUALIFICATION: hard-exit this controller this many "
                         "seconds after first telemetry, leaving the pod")
    ap.add_argument("--telemetry-stall", type=float, default=None)
    ap.add_argument("--unreachable", type=float, default=None)
    ap.add_argument("--expected-module-s", type=float, default=None)
    ap.add_argument("--fanout", default=None,
                    help="shard file: several pods at once")
    ap.add_argument("--fail-fast", action="store_true")
    args = ap.parse_args(argv)

    module_dir = module_path(args.module)
    env = parse_env(args.env)
    spec = select_spec(module_dir, args.scout, args.pin_gpu,
                       args.platform_interval,
                       units=None if args.calibrate else args.units, env=env)

    if args.fanout:
        if not (args.go or args.rehearse):
            print("fan-out needs --rehearse (fake) or --go (real)")
            return 0
        return fanout(module_dir, args, env, rehearse_only=not args.go)

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
        if not (args.dry or args.rehearse or args.go or args.resume):
            return 0
    if args.resume:
        log("RESUME from ledger %s (never creates)" % args.resume)
        if not credentials.available():
            log("no RunPod credential configured; see credentials.py")
            return 4
        return fly(module_dir, spec, args.budget, args.poll, args.ready_poll,
                   ctl_kwargs=controller_options(args),
                   resume_ledger=args.resume)
    if args.dry or not (args.rehearse or args.go):
        show_plan(module_dir, spec, args.workload_seconds)
        if not (args.rehearse or args.go):
            print("\nNothing was created. Pass --rehearse for a fake flight "
                  "or --go for the real one.")
        return 0
    plan = load_campaign_plan(args.plan, spec) if args.plan else None
    if args.rehearse:
        return rehearse(module_dir, spec, args.budget, plan=plan)

    log("REAL LAUNCH %s, budget ceiling $%.2f" % (spec.identity, args.budget))
    if not credentials.available():
        log("no RunPod credential configured; see credentials.py")
        return 4
    log("credential: %s" % json.dumps(credentials.describe(), sort_keys=True))
    if args.auto:
        return auto(module_dir, args, env)
    if plan is not None:
        log("campaign plan %s: calibrated $%.4f, preregistered $%.4f"
            % (plan["decision"], plan["calibrated_estimate"]["expected_usd"],
               plan["preregistered_estimate"]["expected_usd"]))
    return fly(module_dir, spec, args.budget, args.poll, args.ready_poll,
               plan=plan, kill_at_s=args.kill_controller_at,
               ctl_kwargs=controller_options(args))


if __name__ == "__main__":
    raise SystemExit(main())
