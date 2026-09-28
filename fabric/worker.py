"""fabric.worker -- a pull worker. One process = one worker instance = one
Attempt at a time.

Loop: reap (anyone may) -> claim a compatible Task (capabilities, executors,
host, target) together with its resource leases -> prepare a pinned worktree
-> run the executor with a heartbeat thread -> the RUNTIME uploads the
artifacts (final text, stdout, stderr, environment receipt, output files, a
patch if the checkout was modified) -> finish the Attempt.

If this process dies mid-Attempt, nothing is uploaded and nothing is
finished: the heartbeat stops, a reaper abandons the Attempt, its leases are
released and the Task returns to the queue (retry policy permitting).

    python -m fabric worker --agent worker.ubu001 --caps repo.read research.repo_readonly ... [--once]
"""
from __future__ import annotations

import fcntl
import json
import os
import platform
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import store as S
from .executors import EXECUTORS, TOKEN_ENV_FILE

CANONICAL = Path(os.environ.get("FABRIC_CANONICAL_CLONE", os.path.expanduser("~/Prometheus")))


def host_label() -> str:
    return socket.gethostname().lower()


def _git(*args, cwd: Path, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd)] + list(args), capture_output=True, text=True, timeout=timeout)


class Worker:
    def __init__(self, agent: str, capabilities: List[str], executors: List[str], *, work_root: Path,
                 poll_s: float = 5.0, ttl_s: int = 90, model: Optional[str] = None, description: str = ""):
        self.agent, self.caps, self.executors = agent, capabilities, executors
        self.host = host_label()
        self.instance = "{}-{}".format(self.host, secrets.token_hex(4))
        self.actor = "{}[{}]".format(agent, self.instance)
        self.root = work_root / agent
        self.poll_s, self.ttl_s, self.model, self.description = poll_s, ttl_s, model, description
        self.conn = S.connect()
        S.register_instance(self.conn, agent, "worker", self.instance, self.host, capabilities=capabilities, executors=executors,
                            model=model, capacity=1, description=description)

    # ---------------------------------------------------------------- worktrees
    def worktree(self, sha: Optional[str]) -> Path:
        """A detached checkout of `sha` owned by THIS worker (one Attempt at a
        time per worker, so it can be diffed and restored after each run).
        Creation is serialised per host with a file lock (concurrent
        `git worktree add` on one clone collides -- Archaeon E-001 lesson).
        The canonical clone is only fetched and used for worktree management."""
        sha = sha or _git("rev-parse", "origin/main", cwd=CANONICAL).stdout.strip()
        path = self.root / "bases" / sha[:12]
        if (path / ".git").exists():
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        lock = open(Path(os.path.expanduser("~")) / ".fabric-worktree.lock", "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            if _git("cat-file", "-e", sha + "^{commit}", cwd=CANONICAL).returncode != 0:
                _git("fetch", "-q", "origin", cwd=CANONICAL)
            r = _git("worktree", "add", "--detach", str(path), sha, cwd=CANONICAL)
            if r.returncode != 0:
                raise S.FabricError("worktree add failed: " + r.stderr[-500:])
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN); lock.close()
        return path

    def _restore(self, wt: Path) -> Optional[bytes]:
        """If the executor changed the checkout, capture the change as a patch
        (an artifact) and restore the checkout. Nothing is ever pushed."""
        st = _git("status", "--porcelain", cwd=wt).stdout
        if not st.strip():
            return None
        _git("add", "-A", ".", cwd=wt)
        patch = subprocess.run(["git", "-C", str(wt), "diff", "--binary", "--cached", "HEAD"], capture_output=True).stdout
        _git("reset", "-q", "--hard", "HEAD", cwd=wt); _git("clean", "-fdq", cwd=wt)   # this worker's own cache only
        return patch

    # ---------------------------------------------------------------- one attempt
    def run_attempt(self, claimed: Dict[str, Any]) -> Dict[str, Any]:
        task, aid = claimed["task"], claimed["attempt_id"]
        tid = task["task_id"]
        adir = self.root / "attempts" / aid
        adir.mkdir(parents=True, exist_ok=True)
        stop = {"reason": None}
        hb_conn = S.connect()

        def beat():
            while stop.get("done") is not True:
                try:
                    h = S.heartbeat(hb_conn, aid, self.actor, ttl_s=self.ttl_s)
                    if not h["ok"]:
                        stop["reason"] = "fenced"
                    elif h["cancel_requested"]:
                        stop["reason"] = "cancel"
                except Exception as e:                    # store unreachable: keep trying; expiry will decide
                    stop["hb_error"] = str(e)[:200]
                for _ in range(int(self.ttl_s / 4)):
                    if stop.get("done"):
                        break
                    time.sleep(1)
        hb = threading.Thread(target=beat, daemon=True); hb.start()

        receipt = {"host": self.host, "agent": self.agent, "instance": self.instance, "python": sys.version.split()[0],
                   "platform": platform.platform(), "pid": os.getpid(), "attempt_dir": str(adir), "base_sha": task.get("base_sha"),
                   "executor": task["executor"], "token_env_present": TOKEN_ENV_FILE.exists(), "started_utc": time.strftime("%FT%TZ", time.gmtime())}
        wt = None
        try:
            if task["executor"] != "synthetic":            # synthetic work needs no checkout
                wt = self.worktree(task.get("base_sha"))
                receipt["worktree"] = str(wt)
                receipt["worktree_head"] = _git("rev-parse", "HEAD", cwd=wt).stdout.strip()
            if task["executor"] == "claude":
                receipt["claude_version"] = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
                receipt["claude_config_dir"] = str(adir / "claude_config")
            res = EXECUTORS[task["executor"]](task, aid, str(wt or adir), adir, lambda: stop["reason"])
        except Exception as e:
            from .executors import Result
            res = Result(None, "", b"", b"", error="runtime: {}: {}".format(type(e).__name__, str(e)[:500]))
        stop["done"] = True
        hb.join(timeout=5)
        patch = self._restore(wt) if wt is not None else None
        receipt.update({"ended_utc": time.strftime("%FT%TZ", time.gmtime()), "exit_code": res.exit_code, "killed": res.killed,
                        "model_used": res.model, "executor_extra": res.extra, "heartbeat_error": stop.get("hb_error")})

        # The RUNTIME captures everything, whatever the executor managed to write.
        up = []
        def put(name, kind, data, media="text/plain", **md):
            if data is None:
                return
            up.append(S.add_artifact(self.conn, tid, aid, name, kind, data if isinstance(data, bytes) else data.encode(),
                                     media_type=media, metadata=md, actor=self.actor))
        put("final_text.md", "final_text", res.final_text or "")
        put("stdout", "stdout", res.stdout); put("stderr", "stderr", res.stderr)
        put("env_receipt.json", "env_receipt", json.dumps(receipt, indent=1, default=str), "application/json")
        out = adir / "out"
        deliver = ((task.get("params") or {}).get("deliver") or {})
        if out.is_dir():
            import mimetypes
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    rel = str(f.relative_to(out))
                    put(rel, "file", f.read_bytes(), mimetypes.guess_type(rel)[0] or "application/octet-stream",
                        deliver_as=deliver.get(rel))
        if patch:
            put("changes.patch", "patch", patch, "text/x-diff")

        if res.killed == "fenced":
            outcome, err = "failed", "attempt fenced (no longer running in the store)"
        elif res.killed == "cancel":
            outcome, err = "canceled", "canceled by request"
        elif res.error or res.killed or res.exit_code != 0:
            outcome, err = "failed", res.error or "exit {} {}".format(res.exit_code, res.killed or "")
        else:
            outcome, err = "succeeded", None
            fs = (task.get("params") or {}).get("final_state")
            if task["executor"] == "synthetic" and fs in ("input-required", "rejected"):
                outcome = fs
        if res.final_text and outcome in ("succeeded", "input-required", "rejected"):
            S.add_message(self.conn, tid, "msg-" + aid, "agent", [{"text": res.final_text.strip()}], actor=self.actor)
        fin = S.finish_attempt(self.conn, aid, outcome, self.actor, exit_code=res.exit_code, error=err, model=res.model,
                               env_receipt=receipt, worktree=str(wt) if wt else None,
                               result_summary=(res.final_text or "")[:500] or None)
        hb_conn.close()
        shutil.rmtree(adir / "claude_config", ignore_errors=True)
        return {"task_id": tid, "attempt_id": aid, "outcome": outcome, "finish": fin, "artifacts": len(up)}

    # ---------------------------------------------------------------- loop
    def loop(self, once: bool = False, max_tasks: Optional[int] = None, idle_exit_s: Optional[float] = None) -> None:
        done, idle_since = 0, time.time()
        while True:
            try:
                S.reap(self.conn, actor=self.actor)
                S.touch_instance(self.conn, self.agent, self.instance)
                got = S.claim(self.conn, self.agent, self.instance, self.host, self.caps, self.executors, ttl_s=self.ttl_s)
            except Exception as e:
                print(json.dumps({"worker": self.actor, "store_error": str(e)[:300]}), flush=True)
                try:
                    self.conn.close()
                except Exception:
                    pass
                time.sleep(self.poll_s)
                try:
                    self.conn = S.connect()                # fail closed: no work without the store
                except Exception:
                    pass
                continue
            if got is None:
                if once or (idle_exit_s and time.time() - idle_since > idle_exit_s):
                    break
                time.sleep(self.poll_s)
                continue
            r = self.run_attempt(got)
            print(json.dumps(dict(r, worker=self.actor), default=str), flush=True)
            done += 1; idle_since = time.time()
            if once or (max_tasks and done >= max_tasks):
                break
        S.touch_instance(self.conn, self.agent, self.instance, status="offline")
