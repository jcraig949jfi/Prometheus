"""Sandbox harness for LLM-authored mutations (SelfImprovingDaemon v2c iter 3).

Public API: sandbox_test(proposal, mock_agent_dict, mock_state_dict, timeout)
→ SandboxResult with passed/error/state_restored details.

Isolation: invokes agents/_shared/_sandbox_worker.py as a subprocess. The
worker uses restricted SAFE_BUILTINS (no __import__, no open, no exec/eval/
compile passthrough). Parent enforces subprocess.run(timeout=) wall clock.

Also provides: mark_sandbox_result_in_audit() to update the audit log row,
and executable_llm_proposals() for the mixin to read approved-and-passed
proposals as Tier 4 menu items.
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_WORKER = REPO_ROOT / "agents" / "_shared" / "_sandbox_worker.py"
DEFAULT_AUDIT_LOG = REPO_ROOT / "agents" / "_shared" / "llm_authored_mutations_audit.jsonl"

DEFAULT_SANDBOX_TIMEOUT_SEC = 10

log = logging.getLogger("llm_sandbox")


@dataclass
class SandboxResult:
    passed: bool
    stage: str               # 'input_parse'|'apply_compile'|'apply_lookup'|'apply_run'|
                             # 'revert_compile'|'revert_lookup'|'complete'|'timeout'|'invocation_failed'
    error: Optional[str] = None
    snapshot: Optional[str] = None
    state_restored: Optional[bool] = None
    revert_error: Optional[str] = None
    duration_sec: Optional[float] = None


def sandbox_test(
    apply_code: str,
    revert_code: str,
    mock_agent_dict: dict,
    mock_state_dict: dict,
    timeout_sec: int = DEFAULT_SANDBOX_TIMEOUT_SEC,
) -> SandboxResult:
    """Run apply_code then revert_code against a mock agent/state in a
    subprocess. Returns SandboxResult with full diagnostics."""
    if not SANDBOX_WORKER.exists():
        return SandboxResult(passed=False, stage="invocation_failed",
                             error=f"sandbox worker not found at {SANDBOX_WORKER}")
    payload = json.dumps({
        "apply_code": apply_code,
        "revert_code": revert_code,
        "agent_dict": mock_agent_dict,
        "state_dict": mock_state_dict,
    })
    started = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(
            [sys.executable, str(SANDBOX_WORKER)],
            input=payload, capture_output=True, text=True,
            timeout=timeout_sec, check=False,
        )
    except subprocess.TimeoutExpired:
        return SandboxResult(passed=False, stage="timeout",
                             error=f"sandbox exceeded {timeout_sec}s")
    except Exception as e:
        return SandboxResult(passed=False, stage="invocation_failed",
                             error=f"{type(e).__name__}: {e}")
    duration = (datetime.now(timezone.utc) - started).total_seconds()

    if not proc.stdout:
        return SandboxResult(passed=False, stage="invocation_failed",
                             error=f"empty stdout; stderr={(proc.stderr or '')[:200]}",
                             duration_sec=duration)
    try:
        result_dict = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as e:
        return SandboxResult(passed=False, stage="invocation_failed",
                             error=f"could not parse worker output: {e}; raw={proc.stdout[:200]}",
                             duration_sec=duration)
    return SandboxResult(
        passed=bool(result_dict.get("passed", False)),
        stage=str(result_dict.get("stage", "unknown")),
        error=result_dict.get("error"),
        snapshot=result_dict.get("snapshot"),
        state_restored=result_dict.get("state_restored"),
        revert_error=result_dict.get("revert_error"),
        duration_sec=duration,
    )


def mark_sandbox_result_in_audit(
    proposal_id: str, sandbox_status: str, error: Optional[str] = None,
    audit_path: Optional[Path] = None,
) -> bool:
    """Read the audit log, find the row with matching proposal_id, append
    an updated copy with new sandbox_status. The audit log stays append-only;
    later rows for the same proposal_id supersede earlier ones."""
    p = audit_path or DEFAULT_AUDIT_LOG
    if not p.exists():
        return False
    found_row = None
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("proposal_id") == proposal_id:
            found_row = row
    if not found_row:
        return False
    found_row["sandbox_status"] = sandbox_status
    if error:
        existing_notes = found_row.get("notes", "")
        found_row["notes"] = (existing_notes + " | " if existing_notes else "") + f"sandbox: {error}"
    found_row["sandbox_updated_at"] = datetime.now(timezone.utc).isoformat()
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(found_row, ensure_ascii=False) + "\n")
    return True


def executable_llm_proposals(
    agent_name: str, audit_path: Optional[Path] = None,
) -> list[dict]:
    """Return the LATEST row per proposal_id that is:
      - from the given agent
      - parse_succeeded=True
      - safety_violations is empty
      - sandbox_status='passed'
      - human_approval='approved'
    These are the proposals the mixin should expose as Tier 4 menu items."""
    p = audit_path or DEFAULT_AUDIT_LOG
    if not p.exists():
        return []
    latest_per_id: dict[str, dict] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("agent_name") != agent_name:
            continue
        pid = row.get("proposal_id")
        if not pid:
            continue
        latest_per_id[pid] = row
    out = []
    for row in latest_per_id.values():
        if not row.get("parse_succeeded"):
            continue
        if row.get("safety_violations"):
            continue
        if row.get("sandbox_status") != "passed":
            continue
        if row.get("human_approval") != "approved":
            continue
        out.append(row)
    return out
