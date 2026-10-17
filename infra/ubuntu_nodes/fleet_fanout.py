#!/usr/bin/env python3
"""fleet_fanout.py -- run one command on many fleet nodes, or push/pull a directory, in parallel.

Stdlib only; works from Windows (OpenSSH and tar ship with Win10/11), macOS or Linux. Uses whatever
SSH key the calling account has; it never reads, prints or copies keys or tokens.

    python fleet_fanout.py run   --user mind --nodes ubu001,ubu003 -- 'uptime -p; nproc'
    python fleet_fanout.py run   --user jcraig --all -- 'systemctl --user is-active prometheus-worker.service'
    python fleet_fanout.py push  --user mind --nodes ubu003 ./build/skullport_minds /home/mind/skullport_minds
    python fleet_fanout.py pull  --user mind --all /home/mind/skullport_minds/logs ./collected   (LOCAL/<node>/)
    python fleet_fanout.py probe --user jcraig --all      (load, free RAM, disk, worker, mind processes)

Nodes are named ubuNNN and resolved to IPs from the table below (hostnames resolve to IPv6 link-local
on this LAN and fail the host-key check, so always IPs). --nodes takes names or raw IPs. The exit code
is the number of nodes that failed, so 0 means every node succeeded. Output is grouped per node with
its exit code; --json gives one machine-readable record instead.

push = tar -C LOCAL -cf - . | ssh user@ip 'mkdir -p REMOTE && tar -C REMOTE -xf -'  (no rsync needed on
the client). Existing files are overwritten, others left alone; --clean wipes REMOTE first. REMOTE must
be an absolute path under /home/<user>/; anything else is refused.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import shlex
import subprocess
import sys
import time

NODES = {  # name -> canonical IP (infra/ubuntu_nodes/ubuntu_server_machines.md)
    "ubu001": "192.168.1.218",
    "ubu002": "192.168.1.219",   # offline since 2026-10-12
    "ubu003": "192.168.1.220",
    "ubu004": "192.168.1.221",
    "ubu005": "192.168.1.222",
    "ubu006": "192.168.1.225",
    "ubu007": "192.168.1.3",     # HOLD: bad RAM
    "ubu008": "192.168.1.231",
    "ubu009": "192.168.1.230",   # soak test
}
ALL_AVAILABLE = ["ubu001", "ubu003", "ubu004", "ubu005", "ubu006", "ubu008"]

# One line per node, key=value, no secrets. Runs under the remote user's login shell (bash).
PROBE = (
    'h=$(hostname); l=$(cut -d" " -f1-3 /proc/loadavg); t=$(nproc); '
    'm=$(free -m | awk \'/Mem:/{print $7"/"$2"MB"}\'); d=$(df -h / | awk \'NR==2{print $4}\'); '
    'w=$(systemctl --user is-active prometheus-worker.service 2>/dev/null || echo n/a); '
    'mp=$(ps -u mind -o pid= 2>/dev/null | wc -l); '
    'mc=$(ps -u mind -o %cpu= 2>/dev/null | awk \'{s+=$1} END{print s+0}\'); '
    'mr=$(ps -u mind -o rss= 2>/dev/null | awk \'{s+=$1} END{print int(s/1024)}\'); '
    # Skullport mind hosts: the venv python running .../skullport_minds/app/tools/minds/host.py (units are
    # skullport-mind@<name>.service in mind's own user manager, which jcraig cannot list; so match the command line).
    'sm=$(ps -u mind -o args= 2>/dev/null | grep -cE "skullport_minds/|tools/minds/host\\.py"); '
    'echo "$h threads=$t load=$l mem_avail=$m disk_free=$d worker=$w '
    'mind_procs=$mp mind_cpu%=$mc mind_rss_mb=$mr skullport_minds=$sm"'
)


def ssh_base(user: str, ip: str, connect_timeout: int) -> list:
    return ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={connect_timeout}",
            "-o", "StrictHostKeyChecking=accept-new", f"{user}@{ip}"]


def resolve(args) -> list:
    names = ALL_AVAILABLE if args.all else [n.strip() for n in (args.nodes or "").split(",") if n.strip()]
    if not names:
        sys.exit("give --nodes ubu001,ubu003,... (names or IPs) or --all")
    out = []
    for n in names:
        if n in NODES:
            out.append((n, NODES[n]))
        elif n.count(".") == 3:
            out.append((next((k for k, v in NODES.items() if v == n), n), n))
        else:
            sys.exit(f"unknown node {n!r}; known: {', '.join(NODES)}")
    return out


def run_one(cmd: list, feeder: list | None, timeout: int) -> dict:
    """Run cmd; if feeder is given, its stdout is piped into cmd's stdin (the tar stream for push)."""
    t0 = time.time()
    try:
        if feeder:
            p1 = subprocess.Popen(feeder, stdout=subprocess.PIPE)
            r = subprocess.run(cmd, stdin=p1.stdout, capture_output=True, text=True, timeout=timeout)
            p1.stdout.close()
            rc = r.returncode or p1.wait(timeout=timeout)
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            rc = r.returncode
        return {"rc": rc, "out": r.stdout, "err": r.stderr, "secs": round(time.time() - t0, 1)}
    except subprocess.TimeoutExpired:
        return {"rc": 124, "out": "", "err": f"timeout after {timeout}s", "secs": round(time.time() - t0, 1)}
    except FileNotFoundError as e:
        return {"rc": 127, "out": "", "err": str(e), "secs": 0.0}


def check_remote_path(path: str, user: str) -> None:
    home = f"/home/{user}"
    if not path.startswith(home + "/") or "/../" in path or path.endswith("/..") or path.rstrip("/") == home:
        sys.exit(f"remote path must be absolute and strictly under {home}/ (got {path!r})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["run", "push", "pull", "probe"])
    ap.add_argument("--user", required=True, help="remote account, e.g. mind or jcraig")
    ap.add_argument("--nodes", help="comma list of ubuNNN names or IPs")
    ap.add_argument("--all", action="store_true", help=f"the available nodes: {','.join(ALL_AVAILABLE)}")
    ap.add_argument("--timeout", type=int, default=120, help="per-node seconds (default 120)")
    ap.add_argument("--connect-timeout", type=int, default=8)
    ap.add_argument("--parallel", type=int, default=8)
    ap.add_argument("--clean", action="store_true", help="push: remove the remote dir first")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("rest", nargs="*", help="run: command (after --); push: LOCAL REMOTE; pull: REMOTE LOCAL")
    args = ap.parse_args(argv)
    targets = resolve(args)
    ips = dict(targets)

    jobs = {}
    if args.mode in ("run", "probe"):
        command = PROBE if args.mode == "probe" else " ".join(args.rest)
        if not command:
            sys.exit("run: give the remote command after --")
        for name, ip in targets:
            jobs[name] = (ssh_base(args.user, ip, args.connect_timeout) + [command], None)
    elif args.mode == "push":
        if len(args.rest) != 2:
            sys.exit("push LOCAL_DIR REMOTE_DIR")
        local, remote = args.rest
        if not os.path.isdir(local):
            sys.exit(f"local dir not found: {local}")
        check_remote_path(remote, args.user)
        q = shlex.quote(remote)
        pre = f"rm -rf {q} && " if args.clean else ""
        remote_cmd = f"{pre}mkdir -p {q} && tar -C {q} -xf - && echo pushed:{remote} files=$(find {q} -type f | wc -l)"
        for name, ip in targets:
            jobs[name] = (ssh_base(args.user, ip, args.connect_timeout) + [remote_cmd], ["tar", "-C", local, "-cf", "-", "."])
    elif args.mode == "pull":
        if len(args.rest) != 2:
            sys.exit("pull REMOTE_DIR LOCAL_DIR   (writes LOCAL_DIR/<node>/)")
        remote, local = args.rest
        check_remote_path(remote, args.user)
        for name, ip in targets:
            dest = os.path.join(local, name)
            os.makedirs(dest, exist_ok=True)
            # The remote tar stream is unpacked locally by a second tar; both are fed through run_one's pipe.
            jobs[name] = (["tar", "-C", dest, "-xf", "-"],
                          ssh_base(args.user, ip, args.connect_timeout) + [f"tar -C {shlex.quote(remote)} -cf - ."])

    results = {}
    with cf.ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futs = {ex.submit(run_one, cmd, feeder, args.timeout): name for name, (cmd, feeder) in jobs.items()}
        for f in cf.as_completed(futs):
            results[futs[f]] = f.result()

    failed = [n for n, _ in targets if results[n]["rc"] != 0]
    if args.json:
        print(json.dumps({"mode": args.mode, "user": args.user, "results": results, "failed": failed}, indent=1))
    else:
        for name, _ in targets:
            r = results[name]
            tag = "OK" if r["rc"] == 0 else f"FAIL rc={r['rc']}"
            print(f"== {name} ({ips[name]}) {tag} {r['secs']}s")
            if r["out"].strip():
                print(r["out"].rstrip())
            if r["err"].strip():
                print("  [stderr] " + r["err"].strip().replace("\n", "\n  [stderr] "))
        print(f"-- {len(targets) - len(failed)}/{len(targets)} ok" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main())
