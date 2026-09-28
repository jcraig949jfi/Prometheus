"""fabric.executors -- how an Attempt actually runs. Each executor returns a
Result; the WORKER RUNTIME (fabric.worker), not the executor or Claude,
uploads everything as artifacts, so a report survives even when the worker
could not write it anywhere itself.

  claude     isolated, disposable Claude Code (empty CLAUDE_CONFIG_DIR, pinned
             worktree, explicit model, dontAsk permissions, writes only to the
             attempt's output directory, wall-time limit)
  script     python3 <repo-relative script at the pinned SHA> [args]; no shell,
             path must resolve inside the pinned worktree
  synthetic  sleeps/prints/fails on request -- for pilots and failure tests
"""
from __future__ import annotations

import dataclasses
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

TOKEN_ENV_FILE = Path(os.path.expanduser("~/.config/prometheus/claude.env"))
DEFAULT_MODEL = "claude-opus-5-5"
READONLY_TOOLS = ["Read", "Grep", "Glob", "Bash(git log:*)", "Bash(git show:*)", "Bash(git grep:*)", "Bash(git diff:*)",
                  "Bash(ls:*)", "Bash(wc:*)", "Bash(head:*)", "Bash(sha256sum:*)"]
OPTIONAL_TOOLS = {"web": ["WebSearch", "WebFetch"], "python": ["Bash(python3:*)"]}


@dataclasses.dataclass
class Result:
    exit_code: Optional[int]
    final_text: str
    stdout: bytes
    stderr: bytes
    model: Optional[str] = None
    error: Optional[str] = None
    killed: Optional[str] = None                     # "timeout" | "cancel" | "fenced"
    extra: Dict[str, Any] = dataclasses.field(default_factory=dict)


def _token_env() -> Dict[str, str]:
    """Read KEY=VALUE lines from the node's protected token file WITHOUT
    printing or logging them. Only CLAUDE_CODE_OAUTH_TOKEN is passed on."""
    out = {}
    try:
        for line in TOKEN_ENV_FILE.read_text().splitlines():
            if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
                out["CLAUDE_CODE_OAUTH_TOKEN"] = line.split("=", 1)[1].strip()
    except OSError:
        pass
    return out


def _run(cmd: List[str], *, cwd: str, env: Dict[str, str], wall_s: int, should_stop: Callable[[], Optional[str]]) -> Result:
    """Run with a wall-time limit, polling should_stop() (cancel / fencing).
    The child gets its own process group so a stop kills everything it spawned."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    t0, killed = time.time(), None
    out_chunks, err_chunks = [], []
    import threading

    def pump(stream, sink):
        for chunk in iter(lambda: stream.read(65536), b""):
            sink.append(chunk)
    ths = [threading.Thread(target=pump, args=(p.stdout, out_chunks), daemon=True),
           threading.Thread(target=pump, args=(p.stderr, err_chunks), daemon=True)]
    [t.start() for t in ths]
    while p.poll() is None:
        reason = should_stop()
        if reason is None and time.time() - t0 > wall_s:
            reason = "timeout"
        if reason:
            killed = reason
            try:
                os.killpg(p.pid, signal.SIGTERM); time.sleep(3)
                if p.poll() is None:
                    os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            break
        time.sleep(1)
    p.wait()
    [t.join(timeout=5) for t in ths]
    return Result(p.returncode, "", b"".join(out_chunks), b"".join(err_chunks), killed=killed)


def run_claude(task: Dict[str, Any], attempt_id: str, worktree: str, attempt_dir: Path, should_stop) -> Result:
    params = task.get("params") or {}
    model = params.get("model") or DEFAULT_MODEL
    wall_s = int(params.get("wall_s") or 1800)
    out_dir = attempt_dir / "out"; out_dir.mkdir(parents=True, exist_ok=True)
    cfg = attempt_dir / "claude_config"; cfg.mkdir(parents=True, exist_ok=True)      # EMPTY: no seat memory, no settings
    # "//abs/path" = an ABSOLUTE path in Claude Code permission rules ("/x" would be relative to the project)
    tools = list(READONLY_TOOLS) + ["Write(/{}/**)".format(out_dir), "Edit(/{}/**)".format(out_dir)]
    for opt in params.get("tools") or []:
        tools += OPTIONAL_TOOLS.get(opt, [])
    system = ("You are a disposable research worker of the Prometheus Agent Fabric. Task {tid}, attempt {aid}. "
              "Your working copy is a read-only checkout of the Prometheus repository at commit {sha}. "
              "You have no seat identity and no memory of earlier sessions. Do not modify the repository. "
              "Write any files you want to deliver ONLY under {out}. Your final message is captured verbatim as your report."
              ).format(tid=task["task_id"], aid=attempt_id, sha=task.get("base_sha") or "HEAD", out=out_dir)
    cmd = ["claude", "-p", task["instruction"], "--model", model, "--output-format", "json", "--no-session-persistence",
           "--permission-mode", "dontAsk", "--add-dir", str(out_dir), "--append-system-prompt", system,
           "--allowedTools"] + tools
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_ENTRYPOINT",
                                                            "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CONFIG_DIR", "ANTHROPIC_API_KEY")}
    env.update(_token_env())
    env["CLAUDE_CONFIG_DIR"] = str(cfg)
    r = _run(cmd, cwd=worktree, env=env, wall_s=wall_s, should_stop=should_stop)
    try:
        j = json.loads(r.stdout.decode("utf-8", "replace") or "{}")
    except ValueError:
        j = {}
    r.final_text = j.get("result") or ""
    usage = j.get("modelUsage") or {}
    r.model = ",".join(sorted(usage)) if usage else None
    r.extra = {k: j.get(k) for k in ("is_error", "num_turns", "total_cost_usd", "duration_ms", "session_id", "subtype")}
    r.extra["model_requested"] = model
    if j.get("is_error") and r.exit_code == 0:
        r.error = "claude reported is_error ({})".format(j.get("subtype"))
    return r


def run_script(task: Dict[str, Any], attempt_id: str, worktree: str, attempt_dir: Path, should_stop) -> Result:
    params = task.get("params") or {}
    rel = params.get("script") or ""
    wt = Path(worktree).resolve()
    path = (wt / rel).resolve()
    if not rel or wt not in path.parents or not path.is_file():
        return Result(None, "", b"", b"", error="script {!r} is not a file inside the pinned worktree".format(rel))
    out_dir = attempt_dir / "out"; out_dir.mkdir(parents=True, exist_ok=True)
    env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": str(attempt_dir), "FABRIC_OUT_DIR": str(out_dir),
           "PYTHONDONTWRITEBYTECODE": "1"}
    args = [str(a) for a in params.get("args") or []]
    r = _run([sys.executable, "-I", str(path)] + args, cwd=str(wt), env=env, wall_s=int(params.get("wall_s") or 600),
             should_stop=should_stop)
    r.final_text = r.stdout.decode("utf-8", "replace")[-20000:]
    return r


def run_synthetic(task: Dict[str, Any], attempt_id: str, worktree: str, attempt_dir: Path, should_stop) -> Result:
    params = task.get("params") or {}
    out_dir = attempt_dir / "out"; out_dir.mkdir(parents=True, exist_ok=True)
    code = ("import sys,time,pathlib\n"
            "p={p!r}\n"
            "for i in range(int(p.get('seconds',1)*10)):\n time.sleep(0.1)\n"
            "if p.get('file'): pathlib.Path({o!r}).joinpath(p['file']).write_text(p.get('text','x'))\n"
            "for f in p.get('files') or []: pathlib.Path({o!r}).joinpath(f[0]).write_text(f[1])\n"
            "print(p.get('text','synthetic done'))\n"
            "sys.exit(1 if p.get('fail') else 0)\n").format(p=params, o=str(out_dir))
    r = _run([sys.executable, "-c", code], cwd=str(attempt_dir), env={"PATH": "/usr/bin:/bin"}, wall_s=int(params.get("wall_s") or 300),
             should_stop=should_stop)
    r.final_text = r.stdout.decode("utf-8", "replace")
    return r


EXECUTORS = {"claude": run_claude, "script": run_script, "synthetic": run_synthetic}
