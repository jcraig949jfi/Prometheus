"""
Thread Tracker — JSON-based research thread state management.
==============================================================
Each research cycle produces threads. Each thread tracks:
  - hypothesis (what we're testing)
  - searches (what we ran)
  - evidence (what we found)
  - evaluation (council's assessment)
  - status: pending → searching → evaluating → confirmed / falsified / open
  - timestamps for each transition

Storage: convergence/data/threads.jsonl (append-only log)
Active state: convergence/data/active_threads.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
THREADS_LOG = CONVERGENCE / "data" / "threads.jsonl"
ACTIVE_FILE = CONVERGENCE / "data" / "active_threads.json"

VALID_STATUSES = {"pending", "searching", "evaluating", "confirmed", "falsified",
                   "open", "error", "search_failed", "irrelevant_evidence"}
TERMINAL_STATUSES = {"confirmed", "falsified", "search_failed", "irrelevant_evidence"}


def _ensure_dirs():
    THREADS_LOG.parent.mkdir(parents=True, exist_ok=True)


def _load_active() -> dict:
    """Load active threads dict. Keys are thread IDs."""
    if ACTIVE_FILE.exists():
        return json.loads(ACTIVE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_active(threads: dict):
    _ensure_dirs()
    ACTIVE_FILE.write_text(json.dumps(threads, indent=2, default=str), encoding="utf-8")


def _append_log(thread: dict):
    _ensure_dirs()
    with open(THREADS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(thread, default=str) + "\n")


def create_thread(hypothesis: str, search_plan: list[dict],
                  cycle_id: str, source: str = "deepseek") -> str:
    """Create a new research thread. Returns thread ID."""
    threads = _load_active()
    tid = f"T-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(threads):03d}"
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
    threads[tid] = thread
    _save_active(threads)
    _append_log({"event": "created", "thread_id": tid, "at": thread["created_at"],
                 "hypothesis": hypothesis})
    return tid


def update_status(tid: str, status: str, detail: str = ""):
    """Transition a thread to a new status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
    threads = _load_active()
    if tid not in threads:
        raise KeyError(f"Thread {tid} not found")
    threads[tid]["status"] = status
    threads[tid]["updated_at"] = datetime.now().isoformat()
    threads[tid]["history"].append({
        "status": status, "at": datetime.now().isoformat(), "detail": detail
    })
    _save_active(threads)
    _append_log({"event": "status_change", "thread_id": tid, "status": status,
                 "detail": detail, "at": datetime.now().isoformat()})


def add_evidence(tid: str, search_type: str, results: list[dict]):
    """Attach search results as evidence to a thread."""
    threads = _load_active()
    if tid not in threads:
        raise KeyError(f"Thread {tid} not found")
    entry = {
        "search_type": search_type,
        "n_results": len(results),
        "top_results": results[:5],  # Keep top 5 for readability
        "searched_at": datetime.now().isoformat(),
    }
    threads[tid]["searches_run"].append(search_type)
    threads[tid]["evidence"].append(entry)
    threads[tid]["updated_at"] = datetime.now().isoformat()
    _save_active(threads)


def add_evaluation(tid: str, evaluation: str, verdict: str):
    """Attach council evaluation and set terminal status."""
    threads = _load_active()
    if tid not in threads:
        raise KeyError(f"Thread {tid} not found")
    threads[tid]["evaluation"] = {
        "text": evaluation,
        "verdict": verdict,
        "evaluated_at": datetime.now().isoformat(),
    }
    # Map verdict to status
    status_map = {"confirmed": "confirmed", "falsified": "falsified",
                  "inconclusive": "open", "needs_more_data": "open"}
    new_status = status_map.get(verdict, "open")
    threads[tid]["status"] = new_status
    threads[tid]["updated_at"] = datetime.now().isoformat()
    threads[tid]["history"].append({
        "status": new_status, "at": datetime.now().isoformat(),
        "detail": f"Verdict: {verdict}"
    })
    _save_active(threads)
    _append_log({"event": "evaluated", "thread_id": tid, "verdict": verdict,
                 "status": new_status, "at": datetime.now().isoformat()})


def get_thread(tid: str) -> Optional[dict]:
    threads = _load_active()
    return threads.get(tid)


def list_threads(status: str = None) -> list[dict]:
    """List all active threads, optionally filtered by status."""
    threads = _load_active()
    if status:
        return [t for t in threads.values() if t["status"] == status]
    return list(threads.values())


def summary() -> dict:
    """Summary statistics of all threads."""
    threads = _load_active()
    counts = {}
    for t in threads.values():
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    return {
        "total": len(threads),
        "by_status": counts,
        "cycle_ids": list(set(t["cycle_id"] for t in threads.values())),
    }
