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
import secrets as _secrets
import urllib.request

from . import bundle as bundle_mod
from . import cost as cost_mod
from . import provider as prov_mod
from . import secrets as secrets_mod

SCHEMA = "prometheus-gpu/run-plan/1"
STAGE_FILE = "stages.jsonl"
STOCK_IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"


class DryRunViolation(RuntimeError):
    """A dry run tried to do something that spends money."""


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run_id_for(spec, now=None):
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime(
        "%Y%m%dT%H%M%SZ")
    return "%s-%s" % (spec.name, stamp)


ARTIFACT_SERVER = '''import hashlib
import http.server
import json
import os
import socketserver
import time

ROOT = os.environ.get("PROMETHEUS_ARTIFACT_DIR", "/app/out")
TOKEN = os.environ.get("PROMETHEUS_ARTIFACT_TOKEN", "")
PORT = int(os.environ.get("PROMETHEUS_ARTIFACT_PORT", "8080"))


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the artifact directory, and only to this run's token."""

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        if TOKEN and self.headers.get("Authorization") != "Bearer " + TOKEN:
            self.send_error(401, "artifact token required")
            return
        if self.path.split("?")[0] == "/_clock":
            # The pod's clock, read at the instant of the request, so the
            # controller can measure the offset between the two machines
            # instead of subtracting one clock from the other and hoping.
            body = json.dumps({"epoch": time.time()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?")[0] == "/_manifest":
            # Size and sha256 of every file, computed HERE, on the pod, at
            # the instant of asking. The controller compares what it
            # received against this, so a truncated or corrupted transfer
            # is detected instead of being recorded as the artifact.
            files = {}
            for root, _dirs, names in os.walk(ROOT):
                for name in sorted(names):
                    full = os.path.join(root, name)
                    rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                    digest = hashlib.sha256()
                    size = 0
                    try:
                        with open(full, "rb") as fh:
                            for chunk in iter(lambda: fh.read(1 << 20), b""):
                                digest.update(chunk)
                                size += len(chunk)
                    except OSError:
                        continue
                    files[rel] = {"bytes": size, "sha256": digest.hexdigest()}
            body = json.dumps({"epoch": time.time(),
                               "files": files}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
'''


PLATFORM_FILE = "platform.jsonl"

# Platform telemetry, sampled by the PLATFORM rather than by the module, so
# every run gets GPU memory, utilisation, temperature, power, host CPU/RAM
# and disk without a seat writing a line of it. It never raises: a sampler
# that crashed would be a monitor that looks alive and records nothing
# (base rule 7), so every failure becomes a field in the record instead.
# `sample_cost_s` is the sampler's own cost, recorded on every record, so
# observer overhead is a measurement rather than an assumption.
PLATFORM_SAMPLER = '''import json
import os
import shutil
import subprocess
import sys
import time

OUT = os.environ.get("PROMETHEUS_ARTIFACT_DIR", "/app/out")
PATH = os.path.join(OUT, "platform.jsonl")
INTERVAL = float(os.environ.get("PROMETHEUS_PLATFORM_INTERVAL_S", "5"))
ONCE = os.environ.get("PROMETHEUS_PLATFORM_ONCE") == "1"
ORIGIN = time.monotonic()
QUERY = ("name,memory.used,memory.total,utilization.gpu,temperature.gpu,"
         "power.draw")


def num(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def gpus():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=" + QUERY,
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10)
    except Exception as exc:
        return None, type(exc).__name__
    if out.returncode:
        return None, "nvidia-smi rc=%d" % out.returncode
    rows = []
    for line in out.stdout.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        rows.append({"name": parts[0], "mem_used_mib": num(parts[1]),
                     "mem_total_mib": num(parts[2]),
                     "util_pct": num(parts[3]), "temp_c": num(parts[4]),
                     "power_w": num(parts[5])})
    return rows, None


def host():
    out = {}
    try:
        out["load1"] = os.getloadavg()[0]
        out["cpus"] = os.cpu_count()
    except Exception as exc:
        out["load_error"] = type(exc).__name__
    try:
        mem = {}
        with open("/proc/meminfo") as fh:
            for line in fh:
                key, _, rest = line.partition(":")
                mem[key] = int(rest.split()[0]) * 1024
        out["mem_total_b"] = mem.get("MemTotal")
        out["mem_available_b"] = mem.get("MemAvailable")
    except Exception as exc:
        out["mem_error"] = type(exc).__name__
    try:
        usage = shutil.disk_usage(OUT)
        out["disk_used_b"] = usage.used
        out["disk_free_b"] = usage.free
    except Exception as exc:
        out["disk_error"] = type(exc).__name__
    try:
        total = 0
        for root, _dirs, files in os.walk(OUT):
            for name in files:
                total += os.path.getsize(os.path.join(root, name))
        out["artifact_dir_b"] = total
    except Exception as exc:
        out["artifact_error"] = type(exc).__name__
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    seq = 0
    while True:
        t0 = time.monotonic()
        rows, err = gpus()
        rec = {"kind": "platform",
               "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "t_elapsed_s": round(t0 - ORIGIN, 3),
               "epoch": time.time(), "seq": seq, "gpus": rows}
        if err:
            rec["gpu_error"] = err
        rec.update(host())
        rec["sample_cost_s"] = round(time.monotonic() - t0, 4)
        with open(PATH, "a") as fh:
            fh.write(json.dumps(rec) + "\\n")
        seq += 1
        if ONCE:
            return 0
        time.sleep(max(0.0, INTERVAL - (time.monotonic() - t0)))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
'''


def sampler_prelude(interval_s):
    """Write and start the platform sampler, detached from `set -e`.

    Started after the artifact server and before the fetch, so the
    bootstrap itself -- including a dependency install that has measured
    anywhere from 6 s to 305 s -- is on the record.
    """
    return ["cat > /app/_sample.py <<'PROM_SAMPLER_EOF'",
            PLATFORM_SAMPLER.rstrip("\n"),
            "PROM_SAMPLER_EOF",
            "PROMETHEUS_PLATFORM_INTERVAL_S=%s python3 -u /app/_sample.py "
            "> /dev/null 2>&1 &" % _interval_text(interval_s)]


def _interval_text(value):
    value = float(value)
    return ("%d" % value) if value == int(value) else ("%g" % value)


def platform_interval(spec):
    """Seconds between platform samples. `telemetry.platform_interval_s`,
    else the module's own telemetry interval, never below 1 s."""
    tel = spec["telemetry"]
    return max(1.0, float(tel.get("platform_interval_s",
                                  tel.get("interval_s", 15))))


def server_prelude():
    """Shell that writes and starts the artifact server, first of all.

    FAILURE_PLAYBOOK entry 5: the server comes up BEFORE the dependency
    install and before the module, because a workload that dies must still
    be able to hand back what it had. Serving only after the science
    succeeds destroys exactly the evidence a failed run needs.
    """
    return ["cat > /app/_serve.py <<'PROM_SERVER_EOF'",
            ARTIFACT_SERVER.rstrip("\n"),
            "PROM_SERVER_EOF",
            "python3 -u /app/_serve.py &",
            "PROM_SERVER_PID=$!"]


def build_bootstrap(spec, run_meta, transport):
    """The exact shell the pod will run, in order.

    Ordering is the safety property: serve BEFORE anything that can fail,
    verify BEFORE installing, scrub credentials BEFORE running module code,
    prove the scrub worked rather than trusting it, and stay alive on the
    server afterwards so the controller can retrieve before it terminates.
    """
    workdir = run_meta["workdir"]
    artifacts = run_meta["artifact_dir"]
    pip = spec["dependencies"].get("pip", [])
    stages = "%s/%s" % (artifacts, STAGE_FILE)
    # A shell function, so a stage marker is one short word at each step
    # rather than a repeated one-liner nobody will keep in step.
    # printf, not echo: the format is fixed here and the two values are
    # arguments, so a stage name can never be read as a format string.
    # Nanosecond resolution: Iteration 1's module ran in 0.67 s and whole
    # seconds reported its execution time as 0.0.
    # Built by concatenation, not %-formatting: the shell needs a
    # literal %N for nanoseconds and %-formatting rejects it.
    fmt = chr(39) + '{"stage": "%s", "epoch": %s}' + chr(92) + "n" + chr(39)
    mark = ("stage() { printf " + fmt + ' "$1" "$(date +%s.%N)" >> '
            + stages + "; }")
    # RESTART GUARD (Iteration 3, flight F2). When the container's main
    # process dies, RunPod RESTARTS the container: this whole script runs
    # again, on the same disk, and without this guard it re-ran the module
    # from scratch, appended a second run to the same telemetry and
    # artifacts, and did so in a loop -- while the controller saw an
    # ordinary, progressing run. A restarted pod now brings the artifact
    # server back (so what the first run wrote can still be retrieved),
    # records a `restart` stage for the controller, and runs nothing else.
    # The server script is already on disk from the first boot, so the
    # guard only starts it (re-writing it here would put a heredoc inside
    # an `if`, where its indentation and terminator are easy to break).
    restart_guard = [
        "if [ -f %s ] && grep -q '\"stage\": \"boot\"' %s; then"
        % (stages, stages),
        "  stage restart",
        "  python3 -u /app/_serve.py &",
        "  PROM_SERVER_PID=$!",
        "  wait $PROM_SERVER_PID",
        "  exit 0",
        "fi",
    ]
    lines = [
        "set -euo pipefail",
        "mkdir -p %s %s" % (workdir, artifacts),
        "cd %s" % workdir,
        mark,
    ] + restart_guard + [
        "stage boot",
    ] + server_prelude() + [
        "stage server_up",
    ] + sampler_prelude(platform_interval(spec)) + [
        transport["fetch_cmd"],
        "stage fetched",
        "printf '%%s  %%s\\n' '%s' '%s' > bundle.sha256"
        % (transport["bundle_sha256"], transport["local_name"]),
        "sha256sum -c bundle.sha256",
        "stage verified",
        "tar -xzf %s" % transport["local_name"],
        "stage unpacked",
    ]
    if pip:
        lines.append("pip install --no-cache-dir " +
                     " ".join("'%s'" % p for p in pip))
        lines.append("stage installed")
    if spec["canary"]:
        lines.append("# health check before the real workload")
        lines.append(spec["canary"])
        lines.append("stage canary")
    lines.append("# secrets boundary")
    lines.append(secrets_mod.unset_prelude())
    lines.append(secrets_mod.verification_snippet())
    entry = spec["entrypoint"]
    args = " ".join("'%s'" % a for a in spec["args"])
    lines.append("stage module_start")
    # The module's exit code must not abort the script. Under `set -e` a
    # non-zero exit would take the artifact server down with it, and the
    # run that most needs its telemetry read back is exactly the run that
    # failed. Captured and recorded as a stage instead.
    lines.append("set +e")
    lines.append("python3 -u %s %s" % (entry, args))
    lines.append("PROM_MODULE_RC=$?")
    lines.append("set -e")
    lines.append("stage module_end")
    lines.append('printf \'{"stage": "module_rc", "epoch": %s}\\n\' '
                 '"$PROM_MODULE_RC" >> ' + stages)
    # Hold the pod open on the server. The controller's teardown ends it,
    # after it has retrieved.
    lines.append("wait $PROM_SERVER_PID")
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
        "ports": run_meta.get("ports", list(prov_mod.DECLARED_PORTS)),
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
        # A fresh token per plan. Two plans for the same module get
        # different tokens, which is why a plan cannot be replayed to read
        # a later run's artifacts.
        "artifact_token": _secrets.token_urlsafe(24),
        "artifact_port": prov_mod.ARTIFACT_PORT,
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
