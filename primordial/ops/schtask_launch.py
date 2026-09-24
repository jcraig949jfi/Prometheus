"""O1 (round 3): launch a lane session through a one-shot interactive scheduled task.

The Bash tool kills its child process tree when a command returns, so
`wt.exe new-tab` and `Start-Process` from an agent leave no session (memory
feedback_launch_sessions_via_schtasks, 09-14). A one-shot /IT scheduled task
survives. Its /ST trigger would refire that night, so the task is DISABLED
right after /Run (disabling does not stop the running instance) and the
disable is verified from the task XML (locale-free) before returning.

The .cmd is written by Python (bash printf corrupted `\\n` inside paths).

    python -m primordial.ops.schtask_launch launch F --worktree F:/Prometheus-worktrees/nestor-bld-f --prompt-dir prompts_bld
    python -m primordial.ops.schtask_launch selftest     # dummy cmd.exe /c exit 5; no Claude
    python -m primordial.ops.schtask_launch audit        # PM_* tasks still enabled (should be none)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time

OPS = pathlib.Path(__file__).resolve().parent
LAUNCH_PS1 = OPS / "launch_lane.ps1"
CMD_DIR = pathlib.Path(os.environ.get("PM_LAUNCH_CMD_DIR", "C:/Users/jcrai/lab/pm-data/launcher/cmd"))
PREFIX = "PM_"


def _run(args, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def write_cmd(path, lane: str, worktree, name: str = "", prompt_dir: str = "", exe: str = "",
              exe_args: list[str] | None = None, log_dir: str = "", no_exit: bool = True) -> pathlib.Path:
    """The .cmd the task runs: powershell [-NoExit] -File launch_lane.ps1 ..."""
    parts = ["powershell", "-ExecutionPolicy", "Bypass"]
    if no_exit:
        parts.append("-NoExit")
    parts += ["-File", f'"{pathlib.Path(LAUNCH_PS1)}"', "-Lane", lane, "-Worktree", f'"{pathlib.Path(worktree)}"']
    if name:
        parts += ["-Name", f'"{name}"']
    if prompt_dir:
        parts += ["-BootPrompt", "-PromptDir", prompt_dir]
    if exe:
        parts += ["-Exe", f'"{exe}"']
    if exe_args:                 # ONE string: under -File, PowerShell cannot bind '/c','x' as an array
        parts += ["-ExeArgs", '"' + " ".join(exe_args) + '"']
    if log_dir:
        parts += ["-LogDir", f'"{pathlib.Path(log_dir)}"']
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("@echo off\r\n" + " ".join(parts) + "\r\n").encode("ascii"))
    return path


def task_enabled(task: str, run=_run) -> bool | None:
    """True/False from the task XML; None if the task does not exist."""
    q = run(["schtasks", "/Query", "/TN", task, "/XML"])
    if q.returncode != 0:
        return None
    m = re.search(r"<Settings>.*?<Enabled>(true|false)</Enabled>", q.stdout, re.S)
    return True if m is None else m.group(1) == "true"      # absent <Enabled> means the default, true


def launch(task: str, cmd_path, run=_run, log=print) -> int:
    """Create -> Run -> Disable -> verify disabled. -> 0, or the failing step's code."""
    if not task.startswith(PREFIX):
        raise ValueError(f"task names start with {PREFIX}")
    steps = [
        ("create", ["schtasks", "/Create", "/TN", task, "/TR", str(pathlib.Path(cmd_path)),
                    "/SC", "ONCE", "/ST", "23:59", "/IT", "/F"]),
        ("run", ["schtasks", "/Run", "/TN", task]),
    ]
    rc = 0
    for label, args in steps:
        p = run(args)
        if p.returncode != 0:
            log(f"{label} failed: {(p.stdout + p.stderr).strip()[:300]}")
            rc = p.returncode
            break
    d = run(["schtasks", "/Change", "/TN", task, "/DISABLE"])     # always, even after a failed run
    en = task_enabled(task, run)
    if en:
        log(f"DISABLE FAILED: {task} is still enabled ({(d.stdout + d.stderr).strip()[:200]})")
        return rc or 5
    log(f"{task}: {'launched' if rc == 0 else 'not launched'}; task disabled")
    return rc


def audit(run=_run) -> list[str]:
    """PM_* scheduled tasks that are still enabled."""
    q = run(["schtasks", "/Query", "/FO", "CSV", "/NH"])
    names = sorted({row.split(",")[0].strip('"').lstrip("\\") for row in q.stdout.splitlines() if row.strip()})
    return [n for n in names if n.startswith(PREFIX) and task_enabled(n, run)]


def selftest(timeout_s: float = 90, log=print) -> int:
    """Launch a dummy (cmd.exe /c exit 5) through the real schtasks path; require the
    launch log to record start + exit code 5 and the task to be disabled; then delete it."""
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    task = f"{PREFIX}selftest_{stamp}"
    work = pathlib.Path(tempfile.mkdtemp(prefix="pm_o1_"))
    logdir = work / "log"
    cmd = write_cmd(work / "selftest.cmd", "F", OPS.parents[1], exe="cmd.exe", exe_args=["/c", "exit 5"],
                    log_dir=str(logdir), no_exit=False)
    rc = launch(task, cmd, log=log)
    ok = rc == 0
    events: list = []
    deadline = time.time() + timeout_s
    logfile = logdir / "launch_log.jsonl"
    while ok and time.time() < deadline:
        if logfile.exists():
            events = [json.loads(x) for x in logfile.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
            if any(e.get("event") == "exit" for e in events):
                break
        time.sleep(1)
    exits = [e for e in events if e.get("event") == "exit"]
    checks = {
        "launched": rc == 0,
        "start_logged": any(e.get("event") == "start" for e in events),
        "exit_code_5": bool(exits) and exits[-1].get("exit_code") == 5,
        "task_disabled": task_enabled(task) is False,
    }
    _run(["schtasks", "/Delete", "/TN", task, "/F"])
    checks["task_deleted"] = task_enabled(task) is None
    log(json.dumps({"selftest": task, **checks}))
    return 0 if all(checks.values()) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    la = sub.add_parser("launch")
    la.add_argument("lane")
    la.add_argument("--worktree", required=True)
    la.add_argument("--prompt-dir", default="")
    la.add_argument("--name", default="")
    la.add_argument("--task", default="")
    sub.add_parser("selftest")
    sub.add_parser("audit")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "audit":
        left = audit()
        print("\n".join(left) or "no enabled PM_* tasks")
        return 1 if left else 0
    task = a.task or f"{PREFIX}{a.lane}_{datetime.datetime.now():%Y%m%d_%H%M%S}"
    cmd = write_cmd(CMD_DIR / f"{task}.cmd", a.lane, a.worktree, a.name, a.prompt_dir)
    return launch(task, cmd)


if __name__ == "__main__":
    sys.exit(main())
