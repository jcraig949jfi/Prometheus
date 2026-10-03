"""PrometheusWorker -- deterministic generic execution (roles/generic-worker-role/RESPONSIBILITIES.md).

    python -m workgraph.worker --dry-run            identity, probed resources, eligible tasks in priority order
    python -m workgraph.worker --once               claim and run at most one task, then exit
    python -m workgraph.worker                      loop: claim -> run -> receipt -> release -> next

Run it from a dedicated LINKED worktree (its "state worktree"), never the canonical checkout. Identity:
PrometheusWorker/<hostname>/<instance>. No model inference: the worker executes fully specified GENERIC_WORKER
packets exactly as registered and returns receipts; it never interprets results, changes an experiment, shards
work the packet does not register as SHARDABLE, or claims a NAMED_SEAT task.
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Callable, List, Optional

from . import core, priority


# ------------------------------------------------------------------------------------------------- identity / probe

def identity(instance: Optional[str] = None, host: Optional[str] = None) -> str:
    return "PrometheusWorker/{}/{}".format((host or socket.gethostname()).lower(), instance or uuid.uuid4().hex[:8])


def _ram_gb() -> Optional[float]:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return round(int(line.split()[1]) / 1048576, 1)
    except OSError:
        pass
    if sys.platform == "win32":
        try:
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tot", ctypes.c_ulonglong),
                            ("avail", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong),
                            ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong)]
            m = MS(); m.l = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.avail / 1073741824, 1)
        except Exception:
            return None
    return None


def probe(base: Path) -> dict:
    gpus = []
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=20).stdout
            gpus = [ln.strip() for ln in out.splitlines() if ln.strip()]
        except (OSError, subprocess.SubprocessError):
            pass
    return {"host": socket.gethostname().lower(), "os": platform.system(), "python": platform.python_version(),
            "cpu": os.cpu_count() or 1, "ram_gb_available": _ram_gb(), "gpu": len(gpus), "gpus": gpus,
            "disk_gb_free": round(shutil.disk_usage(str(base)).free / 1073741824, 1),
            "caps": sorted(c for c in os.environ.get("PROMETHEUS_WORKER_CAPS", "").replace(",", " ").split() if c)}


def fits(t: dict, pr: dict) -> bool:
    """Resource and capability fit from execution.resources (bandwidth is not scheduled)."""
    res = (t.get("execution") or {}).get("resources") or {}
    if res.get("hosts") and pr["host"] not in [h.lower() for h in res["hosts"]]:
        return False
    if res.get("cpu", 1) > pr["cpu"] or res.get("gpu", 0) > pr["gpu"]:
        return False
    if res.get("ram_gb") and pr["ram_gb_available"] is not None and res["ram_gb"] > pr["ram_gb_available"]:
        return False
    if res.get("disk_gb") and res["disk_gb"] > pr["disk_gb_free"]:
        return False
    return all(c in pr["caps"] for c in res.get("caps", []))


# ------------------------------------------------------------------------------------------------- store

class FsStore:
    """Workgraph files on disk, no git (tests and dry runs). `on_sync` lets a test change the world mid-run."""

    def __init__(self, repo: Path, on_sync: Optional[Callable[[], None]] = None):
        self.repo = Path(repo)
        self.on_sync = on_sync

    @property
    def campaigns(self) -> Path:
        return self.repo / "ops" / "campaigns"

    @property
    def queue(self) -> Path:
        return self.repo / "ops" / "operator_queue"

    def sync(self) -> None:
        if self.on_sync:
            self.on_sync()

    def publish(self, paths: List[Path], message: str) -> bool:
        return True

    def checkout(self, sha: str, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)          # tests run the command in an empty directory

    def release(self, dest: Path) -> None:
        shutil.rmtree(dest, ignore_errors=True)


class GitStore(FsStore):
    """The real store: a linked worktree of the Prometheus clone. sync = fetch + detach at origin/main;
    publish = commit explicit paths + fast-forward push to main (the compare-and-swap; False = lost race)."""

    def __init__(self, repo: Path, allow_main_worktree: bool = False):
        super().__init__(repo)
        gd = self._git("rev-parse", "--git-dir").strip()
        cd = self._git("rev-parse", "--git-common-dir").strip()
        if not allow_main_worktree and Path(self.repo, gd).resolve() == Path(self.repo, cd).resolve():
            raise SystemExit("refusing to run in a main worktree (WORKING_CONTRACT s1): use a linked worktree, e.g. "
                             "git -C <canonical> worktree add --detach <path> origin/main")

    def _git(self, *args, check=True, timeout=900) -> str:
        r = subprocess.run(["git", "-C", str(self.repo)] + list(args), capture_output=True, text=True, timeout=timeout)
        if check and r.returncode != 0:
            raise RuntimeError("git {} failed: {}".format(" ".join(args), r.stderr.strip()[:300]))
        return r.stdout

    def sync(self) -> None:
        self._git("fetch", "-q", "origin")
        self._git("checkout", "-q", "--detach", "origin/main")

    def publish(self, paths: List[Path], message: str) -> bool:
        self._git("add", "--", *[str(Path(p).relative_to(self.repo)) for p in paths])
        self._git("-c", "user.name=PrometheusWorker", "-c", "user.email=prometheus-worker@users.noreply.github.com",
                  "commit", "-q", "-m", message)
        for _ in range(4):
            r = subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin", "HEAD:main"], capture_output=True,
                               text=True, timeout=600)
            if r.returncode == 0:
                return True
            # rejected: main moved. Rebase explicitly onto the fetched SHA (WORKING_CONTRACT s3); a conflict on the
            # same task file means another worker moved first -- a lost race, not an error.
            self._git("fetch", "-q", "origin")
            sha = self._git("rev-parse", "origin/main").strip()
            if subprocess.run(["git", "-C", str(self.repo), "rebase", "-q", sha], capture_output=True,
                              text=True, timeout=900).returncode != 0:
                self._git("rebase", "--abort", check=False)
                self._git("checkout", "-q", "--detach", sha)
                return False
        return False

    def checkout(self, sha: str, dest: Path) -> None:
        self._git("worktree", "add", "--detach", str(dest), sha, timeout=3600)

    def release(self, dest: Path) -> None:
        self._git("worktree", "remove", "--force", str(dest), check=False, timeout=3600)


# ------------------------------------------------------------------------------------------------- selection

def eligible(store: FsStore, pr: dict, now=None) -> List[tuple]:
    """[(effective, task_dir, task)] READY GENERIC_WORKER tasks this host can run, best first."""
    camps, tasks = core.load_campaigns(store.campaigns), core.load_tasks(store.campaigns)
    ops = core._ops_for(store.campaigns) or store.repo / "ops"
    ovr = priority.active_overrides(store.queue, now)
    out = []
    for tid, (d, t) in tasks.items():
        if t.get("status") != "READY" or core.executor_class(t) != "GENERIC_WORKER":
            continue
        if (d / "LEASE.json").exists() or core._satisfied(t, tasks, camps) or core.validate_task(t, camps.get(
                t.get("campaign_id"), (None, None))[1]) or not fits(t, pr):
            continue
        out.append((priority.effective(t, camps, ops, ovr), d, t))
    return sorted(out, key=lambda x: priority.sort_key(x[0]))


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------- run one

def run_one(store: FsStore, ident: str, base: Path, poll_s: float = 5.0, now=None) -> dict:
    """Claim the best eligible task and run it. Returns a summary dict (claimed / lost / idle / result)."""
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    store.sync()
    pr = probe(base)
    cands = eligible(store, pr, now)
    if not cands:
        return {"outcome": "IDLE"}
    eff, d, t = cands[0]
    tid = t["task_id"]
    try:
        core.transition(d, "CLAIMED", ident, "generic execution", root=store.campaigns)
        core.transition(d, "IMPLEMENTING", ident, "running registered command unchanged", root=store.campaigns)
    except ValueError as ex:
        return {"outcome": "REFUSED", "task_id": tid, "reason": str(ex)}
    if not store.publish([d], "PrometheusWorker: claim {} ({} band {})".format(tid, eff["epic_id"], eff["band"])):
        return {"outcome": "LOST_RACE", "task_id": tid}
    ex = t["execution"]
    attempt = "A-{}-{}-{}".format(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()), ident.split("/")[-1],
                                  uuid.uuid4().hex[:6])        # unique: a replay never overwrites a receipt
    work = Path(base) / "runs" / tid / attempt
    store.checkout(ex["source_sha"], work)
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "SYSTEMROOT", "HOME", "USERPROFILE", "TEMP", "TMP",
                                                         "EW_DB_HOST", "PYTHONIOENCODING")}
    env.update({str(k): str(v) for k, v in ((ex.get("environment") or {}).get("vars") or {}).items()})
    env["PROMETHEUS_TASK_ID"], env["PROMETHEUS_ATTEMPT_ID"] = tid, attempt
    started = time.time()
    proc = subprocess.Popen(ex["command"], cwd=str(work), env=env)
    preempted_by, timed_out = None, False
    while proc.poll() is None:
        try:
            time.sleep(poll_s)
        except KeyboardInterrupt:
            preempted_by = "operator stop (KeyboardInterrupt)"
            proc.terminate()
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
            break
        if time.time() - started > ex["timeout_s"]:
            timed_out = True
            proc.kill(); proc.wait()
            break
        store.sync()
        higher = [c for c in eligible(store, pr, now) if c[1] != d and priority.may_preempt(eff, c[0])]
        if higher:
            preempted_by = higher[0][2]["task_id"]
            proc.terminate()
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
            break
    if preempted_by:
        rec = core.preempt(d, ident, attempt, preempted_by, start_sha=ex["source_sha"])
        _cleanup(store, work, ex)
        store.publish([d], "PrometheusWorker: {} PREEMPTED_RESOURCE by {}; requeued unchanged".format(tid, preempted_by))
        return {"outcome": "PREEMPTED_RESOURCE", "task_id": tid, "attempt": attempt, "receipt": rec}
    code = proc.returncode
    out_dir = work / ex["output_dir"]
    keep = Path(base) / "results" / tid / attempt
    outputs = []
    if out_dir.is_dir():
        shutil.copytree(out_dir, keep, dirs_exist_ok=True)
        outputs = [{"path": str(f.relative_to(keep)).replace("\\", "/"), "sha256": _sha256(f), "bytes": f.stat().st_size}
                   for f in sorted(keep.rglob("*")) if f.is_file()]
    crit = ex["success_criteria"] if isinstance(ex["success_criteria"], dict) else {"exit_code": 0}
    ok = (not timed_out and code == crit.get("exit_code", 0)
          and all((keep / f).exists() for f in crit.get("files", [])))
    rec = {"schema": core.RECEIPT_SCHEMA, "task_id": tid, "campaign_id": t["campaign_id"], "attempt_id": attempt,
           "role": ident, "model": "none (deterministic execution)", "quality_class": t.get("quality_class"),
           "start_sha": ex["source_sha"], "end_sha": ex["source_sha"], "files_changed": [],
           "evidence_added": [], "evidence_executed": [" ".join(map(str, ex["command"])) + " -> exit {}".format(code)],
           "red_observed": None, "result": "DONE_CLEAN" if ok else "FAILED_CLEAN", "known_escapes": [],
           "unresolved": [] if ok else ["timeout" if timed_out else "execution criteria not met (exit {})".format(code)],
           "unblocks": [], "created_at_utc": core._now(), "host": pr["host"], "exit_code": code,
           "outputs": outputs, "experiment_id": t.get("experiment_id"), "effective_priority": eff,
           "resources": {"wall_s": round(time.time() - started, 1)},
           "notes": "execution facts only; interpretation belongs to owner_role {}; outputs kept at {}".format(
               t.get("owner_role"), keep)}
    (d / "attempts" / attempt).mkdir(parents=True, exist_ok=False)
    core._dump(d / "attempts" / attempt / "RECEIPT.json", rec)
    if ok:
        core.transition(d, "GREEN", ident, "execution criteria met", root=store.campaigns)
        core.transition(d, "INTEGRATION_READY", ident, "for owner {}".format(t.get("owner_role")), root=store.campaigns)
    else:
        core.transition(d, "ESCALATED", ident, "execution failed; owner {} decides".format(t.get("owner_role")),
                        root=store.campaigns)
    _cleanup(store, work, ex)
    if (d / "LEASE.json").exists():
        (d / "LEASE.json").unlink()                  # execution finished: the worker releases its lease
    store.publish([d], "PrometheusWorker: {} {}".format(tid, rec["result"]))
    return {"outcome": rec["result"], "task_id": tid, "attempt": attempt, "receipt": rec}


def _cleanup(store: FsStore, work: Path, ex: dict) -> None:
    if str(ex.get("cleanup", "")).upper() != "KEEP_WORKTREE":
        store.release(work)


# ------------------------------------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="workgraph.worker", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=str(core.REPO), help="the worker's linked state worktree (default: this checkout)")
    p.add_argument("--base", default=None, help="scratch for runs/ and results/ (default: <repo>/../prometheus-worker)")
    p.add_argument("--instance", default=None)
    p.add_argument("--once", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--poll", type=float, default=15.0)
    p.add_argument("--idle-sleep", type=float, default=300.0)
    a = p.parse_args(argv)
    repo = Path(a.repo).resolve()
    base = Path(a.base or repo.parent / "prometheus-worker").resolve()
    base.mkdir(parents=True, exist_ok=True)
    ident = identity(a.instance)
    if a.dry_run:
        store = FsStore(repo)
        pr = probe(base)
        print(json.dumps({"identity": ident, "inherits": ["roles/base-role/", "roles/generic-worker-role/"],
                          "probe": pr}, indent=2))
        for eff, d, t in eligible(store, pr):
            print("{}  {} band {} local {}  {}".format(t["task_id"], eff["epic_id"], eff["band"], eff["local"], t["title"]))
        return 0
    store = GitStore(repo)
    while True:
        r = run_one(store, ident, base, a.poll)
        print(json.dumps({k: v for k, v in r.items() if k != "receipt"}), flush=True)
        if a.once:
            return 0
        if r["outcome"] in ("IDLE", "LOST_RACE", "REFUSED"):
            time.sleep(a.idle_sleep if r["outcome"] == "IDLE" else 5)


if __name__ == "__main__":
    sys.exit(main())
