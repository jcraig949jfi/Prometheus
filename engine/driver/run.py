"""Non-agentic driver: a while-loop that cannot decide to stop.

Control flow lives here. Inference is a subroutine (`ask`) that answers a bounded
question and returns. Nothing in this file asks whether to continue.

    python engine/driver/run.py --max-items 20
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
Q = ROOT / "engine" / "queues"
DECISIONS = Q / "DECISIONS.jsonl"
WORK = Q / "WORK.jsonl"
LOG = ROOT / "engine" / "driver" / "driver_log.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def decide(question: str, options: list[str], rationale: str) -> str:
    """Resolve ambiguity WITHOUT stopping. Take option A, log it, continue.

    This is the whole point of the driver. A decision is a logged event, not a halt.
    James can reverse any of these later; reversal is cheap, stalling is not.
    """
    choice = options[0]
    append(DECISIONS, {"ts": now(), "question": question, "options": options,
                       "chose": choice, "rationale": rationale,
                       "reversible": True, "status": "AUTO-TAKEN"})
    return choice


def block(action: str, why: str) -> None:
    """Irreversible/outward-facing only. Blocks ITSELF, never the queue."""
    append(DECISIONS, {"ts": now(), "action": action, "why": why,
                       "reversible": False, "status": "PENDING-HITL"})


def ask(prompt: str, timeout: int = 900) -> str | None:
    """Call inference for a bounded judgement. It answers; it does not steer."""
    try:
        r = subprocess.run(["claude", "-p", prompt], capture_output=True,
                           text=True, timeout=timeout, cwd=str(ROOT))
        return r.stdout.strip() or None
    except Exception as exc:  # inference failure must not stop the loop
        append(LOG, {"ts": now(), "event": "ask_failed", "error": repr(exc)[:300]})
        return None


def load_work() -> list[dict]:
    if not WORK.exists():
        return []
    items = []
    for line in WORK.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            items.append(json.loads(line))
    return items


def save_work(items: list[dict]) -> None:
    WORK.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in items) + "\n",
                    encoding="utf-8")


def run_item(item: dict) -> dict:
    """Execute one item. Every branch returns; none of them halts the loop."""
    kind = item.get("kind")
    if kind == "shell":
        r = subprocess.run(item["cmd"], shell=True, capture_output=True,
                           text=True, timeout=item.get("timeout", 1800), cwd=str(ROOT))
        return {"rc": r.returncode, "out": r.stdout[-4000:], "err": r.stderr[-2000:]}
    if kind == "ask":
        return {"answer": ask(item["prompt"], item.get("timeout", 900))}
    return {"skipped": f"unknown kind {kind!r}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-items", type=int, default=25)
    ap.add_argument("--max-seconds", type=int, default=7200)
    args = ap.parse_args()

    started = time.time()
    done = 0
    while done < args.max_items and (time.time() - started) < args.max_seconds:
        items = load_work()
        pending = [i for i in items if i.get("status") in (None, "QUEUED")]
        if not pending:
            # Empty queue is NOT a reason to ask anything. Log and exit cleanly.
            append(LOG, {"ts": now(), "event": "queue_empty", "completed": done})
            break
        item = pending[0]
        item["status"] = "RUNNING"
        item["started"] = now()
        save_work(items)
        try:
            result = run_item(item)
            item["status"] = "DONE"
        except Exception as exc:
            # A failed item is a logged failure, not a halt. Next item.
            result = {"error": repr(exc)[:400]}
            item["status"] = "FAILED"
        item["finished"] = now()
        item["result"] = result
        save_work(items)
        append(LOG, {"ts": now(), "id": item.get("id"), "status": item["status"]})
        done += 1

    append(LOG, {"ts": now(), "event": "driver_exit", "completed": done,
                 "elapsed_s": round(time.time() - started)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
