"""Detached launch of a frozen PTE campaign (WORKING_CONTRACT s6).

    python -m prometheus.ananke.launch --freeze roles/Ananke/pte/FREEZE_PTE_C1.json \
        --sha <freeze commit> --pinned <dir for the detached worktree> [--home <ANANKE_HOME>]

1. `git worktree add --detach <pinned> <sha>` (a pinned tree nobody edits);
2. writes a watchdog .cmd into <home>/<campaign>/ (outside git): reruns the
   driver (which resumes at cell granularity) until it exits 0; refuses to
   restart on 3 (parked), 4 (code mismatch), 5 (dirty); caps attempts at 20;
3. starts it through a one-shot scheduled task (/IT), runs it, and disables
   the task (a Bash-tool child would die with the tool call; the task
   survives). Verifies the disable from `schtasks /Query /XML`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys


def sh(args, timeout=1800, check=True):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"{args[:3]} rc={r.returncode}: {r.stderr.strip()[:400]}")
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--pinned", required=True)
    ap.add_argument("--home", default=os.environ.get("ANANKE_HOME", str(pathlib.Path.home() / "ananke_runs")))
    ap.add_argument("--repo", default=str(pathlib.Path(__file__).resolve().parents[2]))
    ap.add_argument("--task", default="Ananke_PTE_C1")
    ap.add_argument("--max-attempts", type=int, default=20)
    a = ap.parse_args(argv)
    pinned = pathlib.Path(a.pinned)
    if not pinned.exists():
        sh(["git", "-C", a.repo, "worktree", "add", "--detach", str(pinned), a.sha], timeout=3600)
    head = sh(["git", "-C", str(pinned), "rev-parse", "HEAD"]).stdout.strip()
    assert head.startswith(a.sha[:9]) or a.sha.startswith(head[:9]), (head, a.sha)
    freeze = pinned / a.freeze
    cfg = json.loads(freeze.read_text())
    cid = cfg["config"]["campaign_id"]
    run_dir = pathlib.Path(a.home) / cid
    run_dir.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    cmd = run_dir / "watchdog.cmd"
    lines = [
        "@echo off",
        "setlocal",
        f'cd /d "{pinned}"',
        f'set PYTHONPATH={pinned}',
        f'set ANANKE_HOME={a.home}',
        "set ATTEMPT=0",
        ":loop",
        "set /a ATTEMPT+=1",
        f'echo [%DATE% %TIME%] attempt %ATTEMPT% >> "{run_dir / "watchdog.log"}"',
        f'"{py}" -m prometheus.ananke.campaign --config "{freeze}" --home "{a.home}" >> "{run_dir / "driver_stderr.log"}" 2>&1',
        "set RC=%ERRORLEVEL%",
        f'echo [%DATE% %TIME%] exited rc=%RC% >> "{run_dir / "watchdog.log"}"',
        "if %RC%==0 goto done",
        "if %RC%==3 goto refused",
        "if %RC%==4 goto refused",
        "if %RC%==5 goto refused",
        f"if %ATTEMPT% GEQ {a.max_attempts} goto capped",
        "timeout /t 60 /nobreak > nul",
        "goto loop",
        ":refused",
        f'echo [%DATE% %TIME%] REFUSED rc=%RC% - not restarting >> "{run_dir / "watchdog.log"}"',
        "goto end",
        ":capped",
        f'echo [%DATE% %TIME%] attempt cap reached >> "{run_dir / "watchdog.log"}"',
        "goto end",
        ":done",
        f'echo [%DATE% %TIME%] DONE >> "{run_dir / "watchdog.log"}"',
        ":end",
        "endlocal",
    ]
    cmd.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))
    st = (dt.datetime.now() + dt.timedelta(minutes=5)).strftime("%H:%M")
    sh(["schtasks", "/Create", "/TN", a.task, "/TR", f'cmd.exe /c "{cmd}"', "/SC", "ONCE",
        "/ST", st, "/IT", "/F"])
    sh(["schtasks", "/Run", "/TN", a.task])
    sh(["schtasks", "/Change", "/TN", a.task, "/DISABLE"])
    xml = sh(["schtasks", "/Query", "/TN", a.task, "/XML"]).stdout
    disabled = "<Enabled>false</Enabled>" in xml
    receipt = {"launched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "task": a.task,
               "pinned": str(pinned), "head": head, "cmd": str(cmd), "task_disabled_after_run": disabled,
               "python": py}
    (run_dir / "launch_receipt.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps(receipt, indent=1))
    return 0 if disabled else 6


if __name__ == "__main__":
    sys.exit(main())
