"""promexec acceptance run: the frozen matrix M1-M20 + PC1/PC2 against the INSTALLED broker (EXPERIMENTAL).

    python3 fabric/promexec/acceptance.py [--note TEXT]

Runs as the fabric worker account (jcraig). It uses only the sudoers-permitted broker call
(`sudo -n /usr/local/sbin/promexec-run ...`), never generic sudo. Canaries are synthetic random strings written
for this run and removed afterwards; no real credential is read. Every hostile probe is bounded (fork count,
memory, time). The result goes to fabric/promexec/ACCEPTANCE_RUNS/<n>.json together with the installed broker's
sha256 and the host facts the reviewer asked for (Aether round 1, requests 1-3).

Not covered here (sequence step 8, after wiring): the Claude tool-allowlist fall-through / command-substitution
fixtures (Aether surface 9). promexec is not on any worker's tool list, so there is nothing to fall through yet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BROKER = "/usr/local/sbin/promexec-run"
RUNS_DIR = HERE / "ACCEPTANCE_RUNS"
HOME = Path.home()

PRELUDE = r'''
import json, os, sys, time, errno
ARGS = json.load(open(os.environ["PROMEXEC_ARGS"]))
OUT = os.environ["PROMEXEC_OUT"]
R = {"uid": os.getuid(), "gid": os.getgid()}
def done():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump(R, f)
def attempt(label, fn):
    try:
        R[label] = {"ok": True, "value": fn()}
    except Exception as e:
        R[label] = {"ok": False, "error": "%s: %s" % (type(e).__name__, str(e)[:160])}
'''

FIX = {
    "M1": r'''
import numpy as np, scipy.stats as st
d = np.loadtxt(os.path.join(os.environ["PROMEXEC_IN"], "data.csv"), delimiter=",")
R["M2_rows"] = int(d.shape[0])
R["pearson"] = float(st.pearsonr(d[:, 0], d[:, 1])[0])
R["M3"] = True
done()
''',
    "READS": r'''
for i, p in enumerate(ARGS["paths"]):
    attempt("read%d" % i, lambda p=p: open(p).read(200))
done()
''',
    "ENV": r'''
R["env"] = dict(os.environ)
done()
''',
    "PRIV": r'''
import subprocess
attempt("sudo", lambda: subprocess.run(["sudo", "-n", "true"], capture_output=True, text=True, timeout=10).returncode)
attempt("crontab", lambda: subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10).returncode)
for i, p in enumerate(ARGS["write"]):
    def w(p=p):
        with open(p, "w") as f:
            f.write("promexec-acceptance-probe\n")
        os.unlink(p)
        return "WROTE"
    attempt("write%d" % i, w)
attempt("net", lambda: __import__("socket").create_connection(("1.1.1.1", 53), timeout=3) and "CONNECTED")
attempt("net_local", lambda: __import__("socket").create_connection(("127.0.0.1", 22), timeout=3) and "CONNECTED")
attempt("host_tmp_marker", lambda: os.path.exists(ARGS["host_tmp"]))
attempt("tmp_write", lambda: open("/tmp/promexec-m12-from-unit", "w").write("x"))
done()
''',
    "SLEEPER": r'''
open(os.path.join(os.getcwd(), "sibling-secret.txt"), "w").write(ARGS["marker"])
open("/tmp/promexec-m12-xchg", "w").write(ARGS["marker"])
R["pid"] = os.getpid()
time.sleep(ARGS["sleep"])
done()
''',
    "PEEKER": r'''
time.sleep(ARGS["delay"])
pids = [p for p in os.listdir("/proc") if p.isdigit()]
R["visible_pids"] = len(pids)
found = []
for p in pids:
    for leaf in ("cmdline", "environ"):
        try:
            if ARGS["marker"].encode() in open("/proc/%s/%s" % (p, leaf), "rb").read():
                found.append([p, leaf])
        except Exception:
            pass
    try:
        if ARGS["marker"] in open("/proc/%s/cwd/sibling-secret.txt" % p).read():
            found.append([p, "cwd"])
    except Exception:
        pass
for m in ARGS["argv_markers"]:
    for p in pids:
        for leaf in ("cmdline", "environ"):
            try:
                if m.encode() in open("/proc/%s/%s" % (p, leaf), "rb").read():
                    found.append([p, leaf, "worker-marker"])
            except Exception:
                pass
R["found"] = found
attempt("list_runs", lambda: os.listdir("/var/lib/promexec/runs"))
attempt("list_view", lambda: sorted(os.listdir("/var/lib/promexec")))
attempt("tmp_xchg", lambda: open("/tmp/promexec-m12-xchg").read())
done()
''',
    "ORPHAN": r'''
import subprocess
if os.fork() == 0:
    os.setsid()
    if os.fork() == 0:
        os.execv(sys.executable, [sys.executable, "-c", "import time; time.sleep(300)", ARGS["marker"]])
    os._exit(0)
time.sleep(1)
R["spawned"] = True
done()
''',
    "PIDS": r'''
kids = []
try:
    for i in range(ARGS["n"]):
        pid = os.fork()
        if pid == 0:
            time.sleep(20); os._exit(0)
        kids.append(pid)
except OSError as e:
    R["fork_error"] = e.errno
R["forked"] = len(kids)
for k in kids:
    os.kill(k, 9)
done()
''',
    "MEM": r'''
done()
blocks = []
for i in range(ARGS["mb"] // 64):
    blocks.append(bytearray(64 * 2**20))
    for j in range(0, len(blocks[-1]), 4096):
        blocks[-1][j] = 1
R["allocated_mb"] = 64 * len(blocks)
done()
''',
    "WALL": r'''
done()
time.sleep(ARGS["sleep"])
R["woke"] = True
done()
''',
    "OUTLINKS": r'''
os.symlink("/etc/hostname", os.path.join(OUT, "link-file"))
os.symlink("/etc", os.path.join(OUT, "link-dir"))
os.mkfifo(os.path.join(OUT, "fifo"))
attempt("in_listing", lambda: sorted(os.listdir(os.environ["PROMEXEC_IN"])))
done()
''',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def broker(stage, out, run_id, limits=None, extra_env=None, raw=None):
    """One direct broker call. raw replaces the argument list (for M19)."""
    args = raw if raw is not None else ["--run-id", run_id, "--in", str(stage), "--out", str(out)]
    for k, v in (limits or {}).items():
        args += ["--" + k, str(v)]
    env = dict(os.environ); env.update(extra_env or {})
    r = subprocess.run(["sudo", "-n", BROKER] + args, capture_output=True, text=True, env=env, timeout=4000)
    try:
        s = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        s = {"unparsed": (r.stdout + r.stderr)[-1500:]}
    s["_rc"] = r.returncode
    res = Path(out) / "result.json"
    s["_fixture"] = json.loads(res.read_text()) if res.is_file() else None
    s["_out_files"] = sorted(str(p.relative_to(out)) for p in Path(out).rglob("*")) if Path(out).is_dir() else []
    return s


class Run:
    def __init__(self, tmp):
        self.tmp = Path(tmp); self.n = 0

    def stage(self, fixture, args, files=None, links=None):
        self.n += 1
        st = self.tmp / ("s%02d" % self.n); out = self.tmp / ("o%02d" % self.n)
        st.mkdir(); out.mkdir()
        (st / "main.py").write_text(PRELUDE + FIX[fixture])
        (st / ".promexec_args.json").write_text(json.dumps(args))
        for name, text in (files or {}).items():
            (st / name).write_text(text)
        for name, target in (links or {}).items():
            os.symlink(target, st / name)
        return st, out, "acc-%02d" % self.n


def host_facts():
    f = {"hostname": platform.node(), "kernel": platform.release(),
         "systemd": subprocess.run(["systemctl", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
         "proc_mount": [l for l in open("/proc/mounts") if l.split()[1] == "/proc"],
         "cgroup_fs": subprocess.run(["stat", "-fc", "%T", "/sys/fs/cgroup"], capture_output=True, text=True).stdout.strip(),
         "crontab_present": shutil.which("crontab"), "at_present": shutil.which("at"),
         "cron_allow_exists": os.path.exists("/etc/cron.allow"),
         "broker_stat": subprocess.run(["stat", "-c", "%U:%G %a %s", BROKER], capture_output=True, text=True).stdout.strip(),
         "sudo_l": subprocess.run(["sudo", "-n", "-l"], capture_output=True, text=True).stdout[-1500:],
         "promexec_id": subprocess.run(["id", "promexec"], capture_output=True, text=True).stdout.strip()}
    return f


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--note", default="")
    ns = ap.parse_args()
    RUNS_DIR.mkdir(exist_ok=True)
    n = 1 + max([int(p.stem) for p in RUNS_DIR.glob("*.json") if p.stem.isdigit()] or [0])
    rec = {"run": n, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "note": ns.note,
           "broker_installed_sha256": sha(BROKER), "broker_committed_sha256": sha(HERE / "broker.py"),
           "broker_reviewed_pin": (HERE / "REVIEWED_BROKER_SHA256").read_text().split()[0],
           "repo_head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "host": host_facts(), "rows": {}, "evidence": {}}
    rows, ev = rec["rows"], rec["evidence"]
    tag = secrets.token_hex(8)
    canaries = {"M4": HOME / ("promexec-canary-%s.txt" % tag),
                "M5": HOME / ".claude" / ("promexec-canary-%s.txt" % tag),
                "M6": HOME / ".config" / "prometheus" / ("promexec-canary-%s.txt" % tag)}
    procs = []
    tmp = tempfile.mkdtemp(prefix="promexec-acc-", dir=str(HOME))
    try:
        for k, p in canaries.items():
            p.write_text("PROMEXEC-CANARY-%s-%s\n" % (k, tag))
        R = Run(tmp)
        # PC1: the ordinary account CAN read the canaries
        rows["PC1"] = all(p.read_text().startswith("PROMEXEC-CANARY") for p in canaries.values())
        # M20 first: everything else is meaningless against an unreviewed broker
        rows["M20"] = {"installed_equals_committed": rec["broker_installed_sha256"] == rec["broker_committed_sha256"]}
        sys.path.insert(0, str(REPO / "fabric" / "tools"))
        import promexec as W                                  # the wrapper's own check, fed a wrong source
        bad = Path(tmp) / "not-the-broker.py"; bad.write_text("# different\n")
        rows["M20"]["wrapper_refuses_mismatch"] = W.broker_matches(Path(BROKER), bad)[0] is False
        rows["M20"]["wrapper_accepts_match"] = W.broker_matches()[0] is True
        rows["M20"]["PASS"] = all(rows["M20"].values())
        # M1-M3
        rng = __import__("random").Random(7)
        data = "\n".join("%f,%f" % (x, 2 * x + rng.gauss(0, 0.05)) for x in (i / 200 for i in range(200)))
        st, out, rid = R.stage("M1", {}, files={"data.csv": data})
        s = broker(st, out, rid); ev["M1"] = s
        fx = s["_fixture"] or {}
        rows["M1"] = bool(s.get("ok") and fx.get("pearson", 0) > 0.99)
        rows["M2"] = fx.get("M2_rows") == 200
        rows["M3"] = "result.json" in s["_out_files"]
        # M4-M6 (and uid facts)
        st, out, rid = R.stage("READS", {"paths": [str(p) for p in canaries.values()]})
        s = broker(st, out, rid); ev["M4-6"] = s; fx = s["_fixture"] or {}
        for i, k in enumerate(("M4", "M5", "M6")):
            got = fx.get("read%d" % i, {})
            rows[k] = bool(fx) and not got.get("ok", True) and tag not in json.dumps(fx)
        rows["uid_dynamic"] = bool(fx) and 61184 <= fx.get("uid", 0) <= 65519
        # M7: credential-shaped variables in the caller's environment must not reach the unit
        fake = {"CLAUDE_CODE_OAUTH_TOKEN": "PROMEXEC-M7-%s" % tag, "GITHUB_TOKEN": "PROMEXEC-M7G-%s" % tag,
                "ANTHROPIC_API_KEY": "PROMEXEC-M7A-%s" % tag}
        st, out, rid = R.stage("ENV", {})
        s = broker(st, out, rid, extra_env=fake); ev["M7"] = s; fx = s["_fixture"] or {}
        rows["M7"] = bool(fx) and not any(v in json.dumps(fx) for v in fake.values()) and \
            not any(k in fx.get("env", {}) for k in fake)
        # M8-M10, M12 (host /tmp), network
        host_tmp = Path("/tmp") / ("promexec-m12-host-%s" % tag); host_tmp.write_text("host")
        targets = [str(REPO / ("promexec-m9-%s" % tag)), "/opt/promexec/m10-%s" % tag, "/usr/local/sbin/m10-%s" % tag,
                   "/etc/sudoers.d/m10-%s" % tag, "/var/lib/promexec/runs/m10-%s" % tag]
        st, out, rid = R.stage("PRIV", {"write": targets, "host_tmp": str(host_tmp)})
        s = broker(st, out, rid); ev["M8-10,M12,net"] = s; fx = s["_fixture"] or {}
        host_tmp.unlink()
        rows["M8"] = bool(fx) and fx.get("sudo", {}).get("value", 1) != 0
        rows["M9"] = bool(fx) and not fx.get("write0", {}).get("ok") and not Path(targets[0]).exists()
        rows["M10"] = bool(fx) and all(not fx.get("write%d" % i, {}).get("ok") for i in range(1, 5))
        rows["crontab_blocked"] = bool(fx) and fx.get("crontab", {}).get("value", 1) != 0
        rows["network_denied"] = bool(fx) and not fx.get("net", {}).get("ok") and not fx.get("net_local", {}).get("ok")
        m12_host = bool(fx) and fx.get("host_tmp_marker", {}).get("value") is False and \
            not Path("/tmp/promexec-m12-from-unit").exists()
        # M11, M12 (unit to unit), M13: a sleeper, a peeker, and a synthetic worker process with argv/environ markers
        marker = "PROMEXEC-SIBLING-%s" % tag
        wmark = "PROMEXEC-M13-ARGV-%s" % tag; emark = "PROMEXEC-M13-ENV-%s" % tag
        worker = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(90)", wmark],
                                  env=dict(os.environ, PROMEXEC_M13=emark))
        procs.append(worker)
        rows["PC_M13_marker_readable_by_owner"] = wmark.encode() in Path("/proc/%d/cmdline" % worker.pid).read_bytes()
        sa = R.stage("SLEEPER", {"marker": marker, "sleep": 25})
        sb = R.stage("PEEKER", {"marker": marker, "delay": 8, "argv_markers": [wmark, emark]})
        res = {}
        ta = threading.Thread(target=lambda: res.__setitem__("a", broker(*sa)))
        ta.start(); time.sleep(4)
        units = subprocess.run(["systemctl", "list-units", "promexec-*", "--no-legend", "--plain"],
                               capture_output=True, text=True).stdout.split()
        live = [u for u in units if u.startswith("promexec-") and u.endswith(".service")]
        if live:
            show = subprocess.run(["systemctl", "show", live[0], "-p",
                                   "User,DynamicUser,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,"
                                   "PrivateNetwork,IPAddressDeny,ProtectProc,ProcSubset,RestrictSUIDSGID,MemoryMax,TasksMax,"
                                   "RuntimeMaxUSec,TemporaryFileSystem,BindPaths,BindReadOnlyPaths"],
                                  capture_output=True, text=True).stdout
            ev["unit_effective_properties"] = show
        res["b"] = broker(*sb); ta.join()
        ev["M11-13"] = res
        fb = res["b"]["_fixture"] or {}
        rows["M11"] = bool(fb) and not [f for f in fb.get("found", []) if len(f) == 2] and \
            not fb.get("list_runs", {}).get("ok") and set(fb.get("list_view", {}).get("value", [])) <= {"in", "out", "work"}
        rows["M12"] = m12_host and bool(fb) and not fb.get("tmp_xchg", {}).get("ok")
        rows["M13"] = bool(fb) and not [f for f in fb.get("found", []) if len(f) == 3]
        worker.kill()
        # PC2: two processes of the SAME uid (the ordinary account) CAN see each other's exposed fixture
        d = Path(tmp) / "pc2"; d.mkdir(); (d / "sibling-secret.txt").write_text(marker)
        pa = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], cwd=str(d)); procs.append(pa)
        time.sleep(0.5)
        rows["PC2"] = marker in Path("/proc/%d/cwd/sibling-secret.txt" % pa.pid).read_text()
        pa.kill()
        # M14: a double-forked, setsid child must not survive its unit
        omark = "PROMEXEC-ORPHAN-%s" % tag
        st, out, rid = R.stage("ORPHAN", {"marker": omark})
        s = broker(st, out, rid); ev["M14"] = s; time.sleep(3)
        survivors = subprocess.run(["pgrep", "-f", omark], capture_output=True, text=True).stdout.split()
        rows["M14"] = bool(s["_fixture"]) and not survivors
        ev["M14"]["survivors"] = survivors
        # M15-M17
        st, out, rid = R.stage("PIDS", {"n": 64})
        s = broker(st, out, rid, limits={"tasks": 16}); ev["M15"] = s; fx = s["_fixture"] or {}
        rows["M15"] = bool(fx) and fx.get("forked", 99) < 16
        st, out, rid = R.stage("MEM", {"mb": 1024})
        s = broker(st, out, rid, limits={"mem-mb": 128}); ev["M16"] = s; fx = s["_fixture"] or {}
        rows["M16"] = s.get("result") not in ("success", None) and "allocated_mb" not in fx
        st, out, rid = R.stage("WALL", {"sleep": 120})
        t0 = time.time(); s = broker(st, out, rid, limits={"wall-s": 5}); ev["M17"] = s
        rows["M17"] = s.get("result") == "timeout" and time.time() - t0 < 60 and "woke" not in (s["_fixture"] or {})
        # M18: symlinks in the staging dir are not transferred in; links/fifos in out/ are not transferred back;
        # the wrapper refuses an input outside its roots
        st, out, rid = R.stage("OUTLINKS", {}, links={"canary-link": str(canaries["M4"]), "home-link": str(HOME)})
        s = broker(st, out, rid); ev["M18"] = s; fx = s["_fixture"] or {}
        in_list = fx.get("in_listing", {}).get("value", [])
        att = Path(tmp) / "att-m18"; (att / "out").mkdir(parents=True)
        (att / "out" / "job.py").write_text("print(1)\n")
        env = dict(os.environ, FABRIC_OUT_DIR=str(att / "out"), FABRIC_WORKTREE=str(REPO))
        wr = subprocess.run([sys.executable, str(REPO / "fabric/tools/promexec.py"), "job.py", "--input", "/etc/hostname"],
                            capture_output=True, text=True, env=env)
        rows["M18"] = bool(fx) and "canary-link" not in in_list and "home-link" not in in_list and \
            not {"link-file", "link-dir", "fifo"} & set(s["_out_files"]) and wr.returncode == 64
        # M19: malformed or hostile invocations fail closed
        bad_calls = {
            "relative_in": ["--run-id", "m19a", "--in", "rel", "--out", str(out)],
            "bad_run_id": ["--run-id", "../x", "--in", str(st), "--out", str(out)],
            "trailing_args": ["--run-id", "m19c", "--in", str(st), "--out", str(out), "--", "x"],
            "unknown_opt": ["--run-id", "m19d", "--in", str(st), "--out", str(out), "--script", "main.py"],
            "missing_in": ["--run-id", "m19e", "--in", str(Path(tmp) / "nope"), "--out", str(out)],
            "no_entry": ["--run-id", "m19f", "--in", str(d), "--out", str(out)],
            "nonint_limit": ["--run-id", "m19g", "--in", str(st), "--out", str(out), "--mem-mb", "lots"],
        }
        m19 = {k: broker(None, out, None, raw=v) for k, v in bad_calls.items()}
        ev["M19"] = {k: {x: v.get(x) for x in ("_rc", "ok", "refused")} for k, v in m19.items()}
        rows["M19"] = all(v["_rc"] != 0 and not v.get("ok") for v in m19.values())
    finally:
        for p in procs:
            try:
                p.kill()
            except Exception:
                pass
        for p in canaries.values():
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        shutil.rmtree(tmp, ignore_errors=True)
    rec["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    matrix = ["M%d" % i for i in range(1, 21)] + ["PC1", "PC2"]
    rec["summary"] = {k: (rows[k]["PASS"] if isinstance(rows.get(k), dict) else rows.get(k)) for k in matrix}
    rec["all_pass"] = all(v is True for v in rec["summary"].values())
    # the canary values must not appear in the record itself
    text = json.dumps(rec, indent=1, default=str).replace(tag, "<tag>")
    (RUNS_DIR / ("%d.json" % n)).write_text(text + "\n")
    print(json.dumps({"run": n, "all_pass": rec["all_pass"], "summary": rec["summary"],
                      "broker_installed_sha256": rec["broker_installed_sha256"]}, indent=1))
    return 0 if rec["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
