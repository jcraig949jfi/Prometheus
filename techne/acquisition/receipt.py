"""Receipt writing. One receipt per step, and the step's STAGE is in the receipt.

The four stages are kept apart because collapsing them is the documented way a tool
claim inflates:

    INSTALLATION            the bytes arrived, pinned and hashed
    FIRST_USEFUL_CHECK      the tool does the one thing we will rely on
    PAPER_REPRODUCTION      a published number came back within a declared tolerance
    ADAPTER_QUALIFICATION   a Prometheus consumer can call it under a typed contract
    LOCAL_SCIENTIFIC_BENEFIT an experiment got a better answer because of it

A receipt carries exactly one stage and an explicit `does_not_establish` list naming the
stages it does NOT speak to. A reader who quotes an INSTALLATION receipt as evidence of
benefit is contradicted by the receipt itself.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import platform
import subprocess
import sys

from . import paths

STAGES = ["INSTALLATION", "FIRST_USEFUL_CHECK", "PAPER_REPRODUCTION",
          "ADAPTER_QUALIFICATION", "LOCAL_SCIENTIFIC_BENEFIT"]


def _repo_state() -> dict:
    def g(args):
        try:
            r = subprocess.run(["git"] + args, cwd=str(paths.REPO_ROOT),
                               capture_output=True, text=True, timeout=30)
            return r.stdout.strip() if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None
    return {
        "commit": g(["rev-parse", "HEAD"]),
        "branch": g(["rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": bool(g(["status", "--porcelain"])),
    }


def new(stage: str, entry_id: str, *, tool: str | None = None) -> dict:
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    return {
        "schema": "techne.acquisition.receipt/1",
        "receipt_id": f"{stage.lower()}-{entry_id}-"
                      f"{_dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "stage": stage,
        "does_not_establish": [s for s in STAGES if s != stage],
        "entry_id": entry_id,
        "tool": tool or entry_id,
        "design_version": "0.1",
        "written_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "seat": "Techne",
        "repo": _repo_state(),
        "runner": {"python": sys.version.split()[0], "executable": sys.executable,
                   "platform": platform.platform(),
                   "tool_cache": str(paths.tool_cache()),
                   "tool_cache_source": ("TECHNE_TOOL_CACHE env"
                                        if __import__("os").environ.get("TECHNE_TOOL_CACHE")
                                        else "techne/config.local.json or the vault/ default"),
                   "tool_cache_note": "host-local and gitignored; only its HASHES are tracked"},
        "commands_run": [],
        "observations": {},
        "deviations": [],
        "unrun_or_blocked": [],
        "status": "INCOMPLETE",
    }


def write(rec: dict, out_dir: pathlib.Path | None = None) -> pathlib.Path:
    d = out_dir or paths.receipts()
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{rec['receipt_id']}.json"
    p.write_text(json.dumps(rec, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return p


def record_command(rec: dict, result: dict, *, keep_output: int = 2000) -> None:
    """Keep failures as well as successes, with their streams truncated not dropped."""
    rec["commands_run"].append({
        "argv": result.get("argv"),
        "returncode": result.get("returncode"),
        "timed_out": result.get("timed_out"),
        "wall_seconds": result.get("wall_seconds"),
        "stdout_tail": (result.get("stdout") or "")[-keep_output:],
        "stderr_tail": (result.get("stderr") or "")[-keep_output:],
    })
