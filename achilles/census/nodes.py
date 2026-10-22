"""Linux node probe for the fleet census: one SSH round-trip per node, in parallel, bounded.

The node table and the probe command are the fleet's shared ones in infra/ubuntu_nodes/fleet_fanout.py
(loaded by path so there is exactly one list of nodes). Every value is what the node itself printed;
a node that does not answer is UNREACHABLE with the reason, never guessed. The probe never raises:
the census must not fail because a laptop is asleep. Requested by the operator and the M1 "Skullport"
session 2026-10-17 so the sandboxed `mind` account's load is visible on the fleet page and in the email.
"""
from __future__ import annotations

import concurrent.futures as cf
import importlib.util
import subprocess
import time
from pathlib import Path

FANOUT_REL = Path("infra") / "ubuntu_nodes" / "fleet_fanout.py"
CODE_ROOT = Path(__file__).resolve().parents[2]   # the pinned code worktree (same rule as run.py)
USER = "jcraig"
FIELDS = ("threads", "load", "mem_avail", "disk_free", "worker", "mind_procs", "mind_cpu%", "mind_rss_mb", "skullport_minds")
HOST_FIELDS = ("load", "mem_avail", "disk_free", "pkg_c", "uptime_h", "sk_procs", "sk_cpu%", "sk_rss_mb", "units")


def load_fanout(root: Path):
    """Import infra/ubuntu_nodes/fleet_fanout.py by path: the code root first (the probe is code, pinned with
    the census), then the given root (tests, or a publish tree that carries it). Returns the module or None."""
    p = next((c / FANOUT_REL for c in (CODE_ROOT, root) if (c / FANOUT_REL).is_file()), None)
    if p is None:
        return None
    spec = importlib.util.spec_from_file_location("fleet_fanout", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_probe_line(line: str, fields: tuple = FIELDS) -> dict:
    """'ubu003 threads=4 load=0.17 0.06 0.01 mem_avail=6191/7330MB ... skullport_minds=0' -> dict.

    `load` is three space-separated numbers, so tokens are re-joined until the next key=.
    """
    toks = line.strip().split()
    if not toks:
        return {}
    out = {"hostname": toks[0]}
    key = None
    for t in toks[1:]:
        if "=" in t and t.split("=", 1)[0] in fields:
            key, val = t.split("=", 1)
            out[key] = val
        elif key:
            out[key] = (out[key] + " " + t).strip()
    for k in ("mind_procs", "skullport_minds", "mind_rss_mb", "threads", "sk_procs", "sk_rss_mb", "pkg_c"):
        if k in out:
            try:
                out[k] = int(float(out[k]))
            except ValueError:
                pass
    for k in ("mind_cpu%", "sk_cpu%", "uptime_h"):
        if k in out:
            try:
                out[k] = float(out[k])
            except ValueError:
                pass
    return out


def parse_units(units: str | None) -> dict:
    """'skullport-qa:enabled/active,skullport-prod:enabled/failed' -> {unit: (enabled_state, active_state)}."""
    out = {}
    for item in (units or "").split(","):
        if ":" not in item:
            continue
        name, st = item.split(":", 1)
        en, _, act = st.partition("/")
        out[name] = (en, act)
    return out


def ssh_command(ip: str, probe_cmd: str, connect_timeout: int) -> list:
    """The ssh argv. -n (stdin from the null device) and -T (never a tty) matter on Windows: the scheduled
    census of 2026-10-17 04:30Z saw 4 of 6 ssh.exe clients stall after authentication (the nodes logged the
    session opened and then nothing until the client's 25 s cut) while the two others answered in 0.8 s.
    That is the Windows OpenSSH console-stdin hang; the client must never touch the hidden console."""
    return ["ssh", "-n", "-T", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={connect_timeout}",
            "-o", "StrictHostKeyChecking=accept-new", f"{USER}@{ip}", probe_cmd]


def _probe_one(name: str, ip: str, probe_cmd: str, connect_timeout: int, timeout: int, attempts: int = 2,
               fields: tuple = FIELDS) -> dict:
    """One node. `timeout` is the whole allowance for this node; it is split over `attempts` tries so a
    client that stalls once (see ssh_command) gets a second, independent connection within the budget."""
    t0 = time.time()
    cmd = ssh_command(ip, probe_cmd, connect_timeout)
    per_try = max(5, timeout // max(1, attempts))
    last_err = "no attempt made"
    for n in range(1, attempts + 1):
        try:
            r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=per_try)
        except subprocess.TimeoutExpired as e:
            partial = ((e.stderr or b"") if isinstance(e.stderr, (bytes, bytearray)) else (e.stderr or "")) or ""
            partial = partial.decode(errors="replace") if isinstance(partial, (bytes, bytearray)) else partial
            last_err = f"timeout after {per_try}s on attempt {n}/{attempts}" + (f"; stderr: {partial.strip()[:120]}" if partial.strip() else "")
            continue
        except (FileNotFoundError, OSError) as e:
            return {"node": name, "ip": ip, "status": "UNREACHABLE", "error": str(e)[:200], "secs": round(time.time() - t0, 1), "attempts": n}
        if r.returncode != 0 or not r.stdout.strip():
            err = (r.stderr.strip().splitlines() or ["no output"])[-1][:200]
            last_err = f"rc={r.returncode}: {err}"
            if r.returncode == 255 and "timed out" not in err.lower():
                break      # a definite ssh failure (auth, host key, refused) does not improve by retrying
            continue
        row = {"node": name, "ip": ip, "status": "OK", "error": None, "secs": round(time.time() - t0, 1), "attempts": n}
        row.update(parse_probe_line(r.stdout.strip().splitlines()[-1], fields))
        return row
    return {"node": name, "ip": ip, "status": "UNREACHABLE", "error": last_err, "secs": round(time.time() - t0, 1), "attempts": attempts}


def probe_nodes(root: Path, now_iso: str, connect_timeout: int = 6, timeout: int = 25, budget_s: int = 40) -> dict:
    """Probe the available nodes in parallel. Never raises; a missing table or SSH binary yields UNAVAILABLE.

    Returns {"status": "ok"|"UNAVAILABLE", "probed_at": iso, "source": "...", "user": USER,
             "nodes": {name: row}, "unreachable": [...], "worker_down": [...], "totals": {...}}
    """
    out = {"status": "UNAVAILABLE", "probed_at": now_iso, "user": USER, "source": str(FANOUT_REL).replace("\\", "/"),
           "nodes": {}, "unreachable": [], "worker_down": [], "totals": {}}
    try:
        fan = load_fanout(root)
        if fan is None:
            out["error"] = f"{FANOUT_REL.as_posix()} not found under {CODE_ROOT} or {root}"
            return out
        targets = [(n, fan.NODES[n]) for n in fan.ALL_AVAILABLE if n in fan.NODES]
        rows = {}
        with cf.ThreadPoolExecutor(max_workers=max(1, len(targets))) as ex:
            futs = {ex.submit(_probe_one, n, ip, fan.PROBE, connect_timeout, timeout): n for n, ip in targets}
            for f in cf.as_completed(futs, timeout=budget_s):
                r = f.result()
                rows[r["node"]] = r
        for n, ip in targets:
            rows.setdefault(n, {"node": n, "ip": ip, "status": "UNREACHABLE", "error": f"no answer within {budget_s}s budget"})
        out["nodes"] = {n: rows[n] for n, _ in targets}
        out["unreachable"] = [n for n, _ in targets if rows[n]["status"] != "OK"]
        out["worker_down"] = [n for n, _ in targets if rows[n]["status"] == "OK" and rows[n].get("worker") != "active"]
        ok = [rows[n] for n, _ in targets if rows[n]["status"] == "OK"]
        out["totals"] = {"nodes": len(targets), "reachable": len(ok),
                         "threads": sum(int(r.get("threads") or 0) for r in ok),
                         "mind_procs": sum(int(r.get("mind_procs") or 0) for r in ok),
                         "skullport_minds": sum(int(r.get("skullport_minds") or 0) for r in ok),
                         "mind_rss_mb": sum(int(r.get("mind_rss_mb") or 0) for r in ok),
                         "mind_cpu%": round(sum(float(r.get("mind_cpu%") or 0) for r in ok), 1)}
        out["status"] = "ok" if ok else "UNAVAILABLE"
        if not ok:
            out["error"] = "no node answered"
        return out
    except Exception as e:  # the census never fails because of the node probe
        out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        return out


def probe_hosts(root: Path, now_iso: str, connect_timeout: int = 6, timeout: int = 25, budget_s: int = 40) -> dict:
    """Probe the reserved hosts (fleet_fanout.RESERVED_HOSTS: in the table, out of the job pool). Never raises.

    A unit counts as down when it is enabled but not active; a disabled or absent unit is not expected to run.
    Returns {"status", "probed_at", "user", "source", "hosts": {name: row}, "unreachable": [...], "units_down": [[host, unit, state]]}.
    """
    out = {"status": "UNAVAILABLE", "probed_at": now_iso, "user": USER, "source": str(FANOUT_REL).replace("\\", "/"),
           "hosts": {}, "unreachable": [], "units_down": []}
    try:
        fan = load_fanout(root)
        reserved = getattr(fan, "RESERVED_HOSTS", None) if fan else None
        if not reserved:
            out["status"] = "none"
            return out
        targets = [(n, fan.NODES[n], role) for n, role in reserved.items() if n in fan.NODES]
        rows = {}
        with cf.ThreadPoolExecutor(max_workers=max(1, len(targets))) as ex:
            futs = [ex.submit(_probe_one, n, ip, fan.HOST_PROBE, connect_timeout, timeout, 2, HOST_FIELDS) for n, ip, _ in targets]
            for f in cf.as_completed(futs, timeout=budget_s):
                r = f.result()
                rows[r["node"]] = r
        for n, ip, role in targets:
            rows.setdefault(n, {"node": n, "ip": ip, "status": "UNREACHABLE", "error": f"no answer within {budget_s}s budget"})
            rows[n]["role"] = role
            for unit, (en, act) in parse_units(rows[n].get("units")).items():
                if en == "enabled" and act != "active":
                    out["units_down"].append([n, unit, act])
        out["hosts"] = {n: rows[n] for n, _, _ in targets}
        out["unreachable"] = [n for n, _, _ in targets if rows[n]["status"] != "OK"]
        out["status"] = "ok" if len(out["unreachable"]) < len(targets) else "UNAVAILABLE"
        return out
    except Exception as e:  # the census never fails because of the host probe
        out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        return out
