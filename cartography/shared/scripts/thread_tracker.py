"""
Thread Tracker — Per-cycle in-memory thread state + append-only JSONL log.
===========================================================================
Refactored for concurrent terminal safety. Each cycle keeps threads in
memory. The only shared file is the append-only JSONL log (safe for
concurrent writes). No shared mutable JSON file.

Storage: convergence/data/threads.jsonl (append-only, audit trail)
In-memory: _cycle_threads dict (per-process, no file lock needed)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
THREADS_LOG = CONVERGENCE / "data" / "threads.jsonl"

VALID_STATUSES = {"pending", "searching", "evaluating", "confirmed", "falsified",
                   "open", "error", "search_failed", "irrelevant_evidence"}
TERMINAL_STATUSES = {"confirmed", "falsified", "search_failed", "irrelevant_evidence"}

# In-memory thread store — per-process, no race condition
_cycle_threads: dict = {}


def _ensure_dirs():
    THREADS_LOG.parent.mkdir(parents=True, exist_ok=True)


def _append_log(entry: dict):
    """Append to JSONL log. Safe for concurrent processes (append-only)."""
    _ensure_dirs()
    with open(THREADS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def create_thread(hypothesis: str, search_plan: list[dict],
                  cycle_id: str, source: str = "deepseek") -> str:
    """Create a new research thread. Returns thread ID."""
    tid = f"T-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(_cycle_threads):03d}"
    thread = {
        "id": tid,
        "cycle_id": cycle_id,
        "hypothesis": hypothesis,
        "search_plan": search_plan,
        "searches_run": [],
        "evidence": [],
        "evaluation": None,
        "status": "pending",
        "source": source,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "history": [{"status": "pending", "at": datetime.now().isoformat()}],
    }
    _cycle_threads[tid] = thread
    _append_log({"event": "created", "thread_id": tid, "at": thread["created_at"],
                 "hypothesis": hypothesis})
    return tid


def update_status(tid: str, status: str, detail: str = ""):
    """Transition a thread to a new status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
    if tid not in _cycle_threads:
        # Thread from a different cycle — create a stub
        _cycle_threads[tid] = {
            "id": tid, "status": "unknown", "history": [],
            "searches_run": [], "evidence": [], "evaluation": None,
            "hypothesis": "", "updated_at": "",
        }
    _cycle_threads[tid]["status"] = status
    _cycle_threads[tid]["updated_at"] = datetime.now().isoformat()
    _cycle_threads[tid]["history"].append({
        "status": status, "at": datetime.now().isoformat(), "detail": detail
    })
    _append_log({"event": "status_change", "thread_id": tid, "status": status,
                 "detail": detail, "at": datetime.now().isoformat()})


def add_evidence(tid: str, search_type: str, results: list[dict]):
    """Attach search results as evidence to a thread."""
    if tid not in _cycle_threads:
        return  # silently skip if thread not in this cycle
    entry = {
        "search_type": search_type,
        "n_results": len(results),
        "top_results": results[:5],
        "searched_at": datetime.now().isoformat(),
    }
    _cycle_threads[tid]["searches_run"].append(search_type)
    _cycle_threads[tid]["evidence"].append(entry)
    _cycle_threads[tid]["updated_at"] = datetime.now().isoformat()


def add_evaluation(tid: str, evaluation: str, verdict: str):
    """Attach evaluation and set status."""
    if tid not in _cycle_threads:
        return
    _cycle_threads[tid]["evaluation"] = {
        "text": evaluation,
        "verdict": verdict,
        "evaluated_at": datetime.now().isoformat(),
    }
    status_map = {"confirmed": "confirmed", "falsified": "falsified",
                  "inconclusive": "open", "needs_more_data": "open"}
    new_status = status_map.get(verdict, "open")
    _cycle_threads[tid]["status"] = new_status
    _cycle_threads[tid]["updated_at"] = datetime.now().isoformat()
    _cycle_threads[tid]["history"].append({
        "status": new_status, "at": datetime.now().isoformat(),
        "detail": f"Verdict: {verdict}"
    })
    _append_log({"event": "evaluated", "thread_id": tid, "verdict": verdict,
                 "status": new_status, "at": datetime.now().isoformat()})


def get_thread(tid: str) -> Optional[dict]:
    """Get thread from current cycle's in-memory store."""
    return _cycle_threads.get(tid)


def list_threads(status: str = None) -> list[dict]:
    """List threads from current cycle, optionally filtered by status."""
    if status:
        return [t for t in _cycle_threads.values() if t.get("status") == status]
    return list(_cycle_threads.values())


def summary() -> dict:
    """Summary of current cycle's threads."""
    counts = {}
    for t in _cycle_threads.values():
        s = t.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    return {
        "total": len(_cycle_threads),
        "by_status": counts,
        "cycle_ids": list(set(t.get("cycle_id", "") for t in _cycle_threads.values())),
    }


def clear_cycle():
    """Clear in-memory threads for a new cycle. Call between cycles if looping."""
    _cycle_threads.clear()
