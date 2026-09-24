"""The zero-dollar dry run: everything except the request that spends.

Answers one question completely:

    If we pressed GO right now, exactly what would happen?

DRY RUN CANNOT CREATE A POD, and the guarantee is structural rather
than promised. `plan()` takes no provider capable of creating one: the
inventory read it needs is passed in as a plain callable. A dry run
therefore has nothing to POST with, which is a stronger property than a
flag that a future edit could forget to check. `test_platform.py`
asserts it against a provider that raises if create_pod is ever called.

The plan is also the receipt skeleton. A launch fills in outcomes; it
does not recompute identity, so what was validated is what runs.
"""

import datetime
import json
import os
import urllib.request

from . import bundle as bundle_mod
from . import cost as cost_mod
from . import secrets as secrets_mod

SCHEMA = "prometheus-gpu/run-plan/1"
STOCK_IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"


class DryRunViolation(RuntimeError):
    """A dry run tried to do something that spends money."""


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run_id_for(spec, now=None):
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime(
        "%Y%m%dT%H%M%SZ")
    return "%s-%s" % (spec.name, stamp)


def build_bootstrap(spec, run_meta, transport):
    """The exact shell the pod will run, in order.

    Ordering is the safety property: verify BEFORE installing, scrub
    credentials BEFORE running module code, and prove the scrub worked
    before the module starts rather than trusting it.
    """
    workdir = run_meta["workdir"]
    artifacts = run_meta["artifact_dir"]
    pip = spec["dependencies"].get("pip", [])
    lines = [
        "set -euo pipefail",
        "mkdir -p %s %s" % (workdir, artifacts),
        "cd %s" % workdir,
        transport["fetch_cmd"],
        "printf '%%s  %%s\\n' '%s' '%s' > bundle.sha256"
        % (transport["bundle_sha256"], transport["local_name"]),
        "sha256sum -c bundle.sha256",
        "tar -xzf %s" % transport["local_name"],
    ]
    if pip:
        lines.append("pip install --no-cache-dir " +
                     " ".join("'%s'" % p for p in pip))
    if spec["canary"]:
        lines.append("# health check before the real workload")
        lines.append(spec["canary"])
    lines.append("# secrets boundary")
    lines.append(secrets_mod.unset_prelude())
    lines.append(secrets_mod.verification_snippet())
    entry = spec["entrypoint"]
    args = " ".join("'%s'" % a for a in spec["args"])
    lines.append("python3 -u %s %s" % (entry, args))
    return "\n".join(lines)


def local_transport(bundle, run_meta):
    """Bundle served by the controller, fetched with a bearer token.

    Uses the proven artifact-serving machinery rather than a new one.
    The fetch command carries the token by ENV REFERENCE, never as a
    literal, so the command is safe to commit as evidence.
    """
    name = "module-%s.tar.gz" % bundle.sha256[:12]
    return {
        "kind": "controller-served",
        "local_name": name,
        "bundle_sha256": bundle.sha256,
        "fetch_cmd": ('curl -fsSL -H "Authorization: Bearer '
                      '$PROMETHEUS_BUNDLE_TOKEN" '
                      '"$PROMETHEUS_BUNDLE_URL" -o %s' % name),
        "requires_env": ["PROMETHEUS_BUNDLE_URL", "PROMETHEUS_BUNDLE_TOKEN"],
    }


def repo_transport(bundle, repo_path, commit):
    """Bundle already committed: the pod fetches it from the pinned commit.

    Preferred when the module lives in the repository, because identity
    is then anchored to a commit rather than to a running controller.
    """
    url = ("https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/%s"
           % (commit, repo_path))
    name = os.path.basename(repo_path)
    return {
        "kind": "repo-pinned",
        "local_name": name,
        "bundle_sha256": bundle.sha256,
        "commit": commit,
        "url": url,
        "fetch_cmd": "curl -fsSL '%s' -o %s" % (url, name),
        "requires_env": [],
    }


def check_retrievable(transport, timeout=30):
    """Prove the source is actually fetchable, now, before spending.

    A pod that boots and cannot fetch its own bundle is a pod that
    bills for nothing. Only the repo transport can be checked without a
    running controller; the controller-served one is checked at launch.
    """
    if transport["kind"] != "repo-pinned":
        return {"checked": False,
                "reason": "controller-served bundle is verified at launch"}
    try:
        req = urllib.request.Request(
            transport["url"], method="HEAD",
            headers={"User-Agent": "prometheus-gpu/1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"checked": True, "ok": resp.status == 200,
                    "status": resp.status}
    except Exception as exc:
        return {"checked": True, "ok": False, "error": type(exc).__name__}


def build_request(spec, run_meta, transport, module_env):
    """The exact body a launch would POST. Constructed in dry run so the
    thing validated is the thing sent."""
    gpu = spec["gpu"]
    env = dict(module_env)
    for name in transport.get("requires_env", []):
        env.setdefault(name, "")
    return {
        "name": run_meta["run_id"][:63],
        "image": run_meta.get("image", STOCK_IMAGE),
        "gpu": {"id": gpu.get("class"), "count": int(gpu.get("count", 1))},
        "cloud": gpu.get("cloud", "SECURE"),
        "disk": int(spec["disk_gb"]),
        "ports": run_meta.get("ports", ["8080/http"]),
        "env": env,
        "entrypoint": ["/bin/bash", "-c"],
        "cmd": [build_bootstrap(spec, run_meta, transport)],
    }


def prepare(spec, module_dir, inventory=None,
            transport_factory=local_transport, workload_seconds=None,
            seat="Aether", image=STOCK_IMAGE, now=None, run_id=None):
    """Return (plan, request, run_meta, built). Creates nothing.

    The PLAN is safe to print, save and commit: its request is scrubbed.
    The REQUEST is not, because it carries the module's environment, so it
    is returned separately and only `launch.py` ever asks for it. Keeping
    them apart is why a saved plan cannot leak a value.

    `inventory` is a zero-argument callable returning the current pod
    list, or None to skip. It is deliberately NOT a provider object:
    a dry run holds nothing that can create a pod.
    """
    findings = []
    run_id = run_id or run_id_for(spec, now)
    run_meta = {
        "run_id": run_id, "seat": seat,
        "workdir": "/app/module", "artifact_dir": "/app/out",
        "telemetry_path": "/app/out/telemetry.jsonl", "image": image,
    }

    built = bundle_mod.build(module_dir, spec)
    if built.manifest["git"].get("dirty"):
        findings.append("module directory is git-dirty; the bundle is "
                        "reproducible only from its own sha256")

    transport = transport_factory(built, run_meta)
    module_env = secrets_mod.build_module_env(spec, run_meta)
    request = build_request(spec, run_meta, transport, module_env)

    secrets_mod.assert_no_credentials(request["env"], where="pod request env")
    boot = request["cmd"][0]
    if secrets_mod.unset_prelude() not in boot:
        raise DryRunViolation("bootstrap does not scrub provider credentials")
    if boot.index(secrets_mod.unset_prelude()) > boot.index(spec["entrypoint"]):
        raise DryRunViolation("credentials are scrubbed AFTER the module "
                              "starts, which is not a boundary")

    projected = cost_mod.project(spec, workload_seconds=workload_seconds,
                                 include_canary=bool(spec["canary"]))
    if projected["overhead_fraction"] and projected["overhead_fraction"] > 0.5:
        findings.append(
            "overhead is %.0f%% of this run; a longer workload or a cheaper "
            "GPU would buy more compute per dollar"
            % (100 * projected["overhead_fraction"]))

    inv = {"checked": False}
    if inventory is not None:
        try:
            pods = inventory()
            inv = {"checked": True, "active": len(pods),
                   "ids": [p.get("id") for p in pods]}
            if pods:
                findings.append(
                    "%d pod(s) already active; a launch would add to them, "
                    "and one-pod-at-a-time is a budget guarantee" % len(pods))
        except Exception as exc:
            inv = {"checked": True, "error": type(exc).__name__}
            findings.append("inventory read failed; active pods are unknown")

    if not spec["artifacts"]:
        findings.append("no artifacts declared; nothing would be retrieved "
                        "and the run would leave no results")
    if not spec["canary"]:
        findings.append("no canary declared; a broken environment would not "
                        "be caught until the workload failed")

    result = {
        "schema": SCHEMA,
        "created_utc": _utc(),
        "run_id": run_id,
        "seat": seat,
        "module": {
            "identity": spec.identity,
            "spec_source": spec.source,
            "spec_sha256": built.manifest["spec_sha256"],
            "entrypoint": spec["entrypoint"],
            "args": spec["args"],
            "description": spec["description"],
        },
        "bundle": built.summary(),
        "bundle_manifest": built.manifest,
        "transport": {k: v for k, v in transport.items()},
        "source_retrievable": check_retrievable(transport),
        "request_sanitized": secrets_mod.scrub_request(request),
        "bootstrap": boot,
        "secrets": {
            "forbidden": list(secrets_mod.FORBIDDEN_ENV),
            "allowlist": spec["env_allowlist"],
            "env_keys": sorted(request["env"]),
            "scrub_before_module": True,
            "verified_on_pod": True,
        },
        "guardrails": {
            "max_runtime_s": spec["max_runtime_s"],
            "disk_gb": spec["disk_gb"],
            "telemetry_interval_s": spec["telemetry"]["interval_s"],
        },
        "cost_projection": projected,
        "inventory": inv,
        "artifacts_expected": spec["artifacts"],
        "findings": findings,
        "receipt_skeleton": {
            "schema": "prometheus-gpu/run-receipt/1",
            "run_id": run_id, "seat": seat, "module": spec.identity,
            "bundle_sha256": built.sha256, "pod_ids": [],
            "result": "NOT_RUN", "started_utc": None, "ended_utc": None,
            "cost_estimated_usd": None, "billing_reconciled": False,
            "cleanup": {"terminate_acknowledged": False,
                        "observed_absent": False,
                        "operational_cleanup": False,
                        "billing_reconciled": False},
            "artifacts": [], "telemetry_summary": None,
        },
        "would_spend_usd": projected["usd_total"],
        "pod_created": False,
    }
    return result, request, run_meta, built


def plan(*args, **kwargs):
    """The dry-run plan alone. This is what a seat and a receipt see."""
    return prepare(*args, **kwargs)[0]


def render(plan_dict):
    """Human-readable answer to: what would happen if we pressed GO?"""
    p = plan_dict
    out = []
    add = out.append
    add("DRY RUN  %s" % p["run_id"])
    add("  module      %s  (%s)" % (p["module"]["identity"],
                                    p["module"]["entrypoint"]))
    add("  bundle      %s  %d files, %d bytes"
        % (p["bundle"]["bundle_sha256"][:16], p["bundle"]["file_count"],
           p["bundle"]["bundle_bytes"]))
    git = p["bundle"]["git"]
    add("  source      %s%s" % (git.get("commit", "(not a git checkout)")[:12]
                                if git.get("available") else "(no git)",
                                " DIRTY" if git.get("dirty") else ""))
    add("  transport   %s -> %s" % (p["transport"]["kind"],
                                    p["transport"]["local_name"]))
    add("  retrievable %s" % p["source_retrievable"])
    c = p["cost_projection"]
    add("  gpu         %s x%d at $%.2f/h"
        % (c["gpu_class"], c["gpu_count"], c["hourly_usd"]))
    add("  time        %.0fs overhead + %.0fs compute%s = %.0fs"
        % (c["overhead_s"], c["compute_s"],
           " (CEILING)" if c["compute_is_ceiling"] else "", c["total_s"]))
    add("  cost        $%.4f  (overhead $%.4f, compute $%.4f, %.0f%% overhead)"
        % (c["usd_total"], c["usd_overhead"], c["usd_compute"],
           100 * (c["overhead_fraction"] or 0)))
    if "work_units" in c:
        w = c["work_units"]
        add("  work        %.3g %s, $%.6f per 1e9"
            % (w["estimate"], w["name"], w["usd_per_1e9_units"]))
    add("  inventory   %s" % p["inventory"])
    add("  artifacts   %s" % (p["artifacts_expected"] or "NONE DECLARED"))
    add("  secrets     scrub before module: yes, verified on pod: yes")
    if p["findings"]:
        add("  FINDINGS")
        for f in p["findings"]:
            add("    - %s" % f)
    add("  POD CREATED: %s" % p["pod_created"])
    return "\n".join(out)


def write_plan(plan_dict, path):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(plan_dict, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path
