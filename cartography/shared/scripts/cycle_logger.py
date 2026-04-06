"""
Cycle Logger — Structured logging for autonomous research cycles.
=================================================================
Dual output:
  1. Console: human-readable, timestamped
  2. JSONL file: machine-readable, every event fully structured

Log files land in: convergence/logs/cycle_{id}.jsonl
Each line is a self-contained JSON object with:
  - ts: ISO timestamp
  - elapsed_s: seconds since cycle start
  - level: info | warn | error | debug
  - component: council | search | tracker | cycle | evaluator
  - event: what happened (verb_noun, e.g. "search_completed")
  - data: structured payload (varies by event)
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parents[2] / "convergence" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class CycleLogger:
    """Structured logger for a single research cycle."""

    def __init__(self, cycle_id: str, console: bool = True):
        self.cycle_id = cycle_id
        self.console = console
        self.t0 = time.time()
        self.log_path = LOG_DIR / f"cycle_{cycle_id}.jsonl"
        self._f = open(self.log_path, "a", encoding="utf-8")
        self._token_totals = {"prompt_tokens": 0, "completion_tokens": 0, "api_calls": 0}
        self._search_totals = {"searches": 0, "total_results": 0, "errors": 0}

        self.info("cycle", "cycle_started", {
            "cycle_id": cycle_id,
            "log_path": str(self.log_path),
            "started_at": datetime.now().isoformat(),
        })

    def _elapsed(self) -> float:
        return round(time.time() - self.t0, 2)

    def _write(self, level: str, component: str, event: str, data: dict):
        record = {
            "ts": datetime.now().isoformat(),
            "elapsed_s": self._elapsed(),
            "level": level,
            "component": component,
            "event": event,
            "cycle_id": self.cycle_id,
            "data": data,
        }
        self._f.write(json.dumps(record, default=str) + "\n")
        self._f.flush()

    def _console_print(self, prefix: str, msg: str):
        if self.console:
            ts = datetime.now().strftime("%H:%M:%S")
            elapsed = self._elapsed()
            # Handle Windows console encoding (cp1252 can't encode some Unicode)
            line = f"  [{ts} +{elapsed:6.1f}s] {prefix} {msg}"
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode("ascii", errors="replace").decode("ascii"))

    # ------ Public logging methods ------

    def info(self, component: str, event: str, data: dict = None, msg: str = ""):
        self._write("info", component, event, data or {})
        if msg:
            self._console_print(f"[{component}]", msg)

    def warn(self, component: str, event: str, data: dict = None, msg: str = ""):
        self._write("warn", component, event, data or {})
        if msg:
            self._console_print(f"[{component}] WARN:", msg)

    def error(self, component: str, event: str, data: dict = None, msg: str = ""):
        self._write("error", component, event, data or {})
        if msg:
            self._console_print(f"[{component}] ERROR:", msg)

    def debug(self, component: str, event: str, data: dict = None):
        self._write("debug", component, event, data or {})

    # ------ Domain-specific structured events ------

    def log_api_call(self, provider: str, model: str, prompt_tokens: int,
                     completion_tokens: int, elapsed_s: float, system_msg: str = "",
                     prompt_preview: str = "", response_preview: str = ""):
        """Log an LLM API call with full token accounting."""
        self._token_totals["prompt_tokens"] += prompt_tokens
        self._token_totals["completion_tokens"] += completion_tokens
        self._token_totals["api_calls"] += 1
        self._write("info", "council", "api_call", {
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "elapsed_s": round(elapsed_s, 2),
            "system_msg_preview": system_msg[:200],
            "prompt_preview": prompt_preview[:300],
            "response_preview": response_preview[:500],
            "cumulative_prompt_tokens": self._token_totals["prompt_tokens"],
            "cumulative_completion_tokens": self._token_totals["completion_tokens"],
            "cumulative_api_calls": self._token_totals["api_calls"],
        })
        self._console_print("[council]",
            f"{provider}/{model} | {prompt_tokens}in/{completion_tokens}out | {elapsed_s:.1f}s "
            f"(total: {self._token_totals['prompt_tokens']+self._token_totals['completion_tokens']} tokens, "
            f"{self._token_totals['api_calls']} calls)")

    def log_hypothesis(self, index: int, hypothesis: dict):
        """Log a generated hypothesis with its full structure."""
        self._write("info", "cycle", "hypothesis_generated", {
            "index": index,
            "hypothesis": hypothesis.get("hypothesis", ""),
            "rationale": hypothesis.get("rationale", ""),
            "search_plan": hypothesis.get("searches", []),
            "falsification": hypothesis.get("falsification", ""),
        })
        hyp_text = hypothesis.get("hypothesis", "N/A")
        self._console_print("[cycle]",
            f"H{index+1}: {hyp_text[:120]}{'...' if len(hyp_text) > 120 else ''}")

    def log_search_start(self, thread_id: str, search_type: str, params: dict):
        """Log the start of a search execution."""
        self._write("info", "search", "search_started", {
            "thread_id": thread_id,
            "search_type": search_type,
            "params": params,
        })
        self._console_print("[search]",
            f"{search_type}({json.dumps(params, default=str)[:100]})")

    def log_search_result(self, thread_id: str, search_type: str, params: dict,
                          results: list, elapsed_s: float):
        """Log search results with full detail."""
        self._search_totals["searches"] += 1
        n_results = len(results) if isinstance(results, list) else 1
        has_errors = any(r.get("error") for r in results) if isinstance(results, list) else False
        if has_errors:
            self._search_totals["errors"] += 1
        self._search_totals["total_results"] += n_results

        self._write("info", "search", "search_completed", {
            "thread_id": thread_id,
            "search_type": search_type,
            "params": params,
            "n_results": n_results,
            "has_errors": has_errors,
            "elapsed_s": round(elapsed_s, 3),
            "results": results[:10],  # Full detail for top 10
            "cumulative_searches": self._search_totals["searches"],
            "cumulative_results": self._search_totals["total_results"],
        })
        status = f"{n_results} results" + (" (ERRORS)" if has_errors else "")
        self._console_print("[search]",
            f"  -> {status} in {elapsed_s:.2f}s "
            f"(total: {self._search_totals['searches']} searches, "
            f"{self._search_totals['total_results']} results)")

    def log_evaluation(self, thread_id: str, hypothesis: str, verdict: str,
                       confidence: float, reasoning: str, full_evaluation: dict):
        """Log council evaluation of evidence."""
        self._write("info", "evaluator", "evaluation_completed", {
            "thread_id": thread_id,
            "hypothesis": hypothesis,
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "strongest_evidence": full_evaluation.get("strongest_evidence", ""),
            "next_step": full_evaluation.get("next_step", ""),
            "full_evaluation": full_evaluation,
        })
        self._console_print("[evaluator]",
            f"VERDICT: {verdict} (confidence={confidence}) | {reasoning[:100]}")

    def log_thread_transition(self, thread_id: str, old_status: str, new_status: str,
                               detail: str = ""):
        """Log a thread state transition."""
        self._write("info", "tracker", "thread_transition", {
            "thread_id": thread_id,
            "from": old_status,
            "to": new_status,
            "detail": detail,
        })
        self._console_print("[tracker]",
            f"{thread_id}: {old_status} -> {new_status}" +
            (f" ({detail})" if detail else ""))

    def log_cycle_complete(self, threads: list, report_path: str):
        """Log cycle completion with full summary."""
        elapsed = self._elapsed()
        status_counts = {}
        for t in threads:
            s = t.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        summary = {
            "elapsed_s": elapsed,
            "n_threads": len(threads),
            "status_counts": status_counts,
            "token_totals": dict(self._token_totals),
            "search_totals": dict(self._search_totals),
            "report_path": report_path,
        }
        self._write("info", "cycle", "cycle_completed", summary)
        self._console_print("[cycle]", f"COMPLETE in {elapsed:.1f}s")
        self._console_print("[cycle]",
            f"Threads: {json.dumps(status_counts)} | "
            f"API: {self._token_totals['api_calls']} calls, "
            f"{self._token_totals['prompt_tokens']+self._token_totals['completion_tokens']} tokens | "
            f"Search: {self._search_totals['searches']} queries, "
            f"{self._search_totals['total_results']} results")
        self._console_print("[cycle]", f"Report: {report_path}")
        self._console_print("[cycle]", f"Log: {self.log_path}")

    def close(self):
        """Flush and close the log file."""
        self._f.close()

    def get_totals(self) -> dict:
        """Return cumulative token and search totals."""
        return {
            "tokens": dict(self._token_totals),
            "searches": dict(self._search_totals),
            "elapsed_s": self._elapsed(),
        }


# Singleton for the current cycle — set by research_cycle.py
_current: CycleLogger | None = None


def init(cycle_id: str, console: bool = True) -> CycleLogger:
    global _current
    _current = CycleLogger(cycle_id, console=console)
    return _current


def get() -> CycleLogger | None:
    return _current
