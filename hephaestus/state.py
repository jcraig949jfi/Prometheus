"""hephaestus/STATE.json -- the queue's freshness and productivity record (base rule 7 and 8; HEPH-11).

Every hephaestus/src job calls `record(job, consumed, produced, note)` when it finishes so that
last_input_at / last_success_at and a domain-level productivity count can be read WITHOUT running
anything. Silence is never health: a reader compares `last_success_at` to the dormancy threshold in
roles/base-role/MONITORS.md (14 days without a new packet event = dormant queue).

Fields per job: last_run_at, last_success_at, last_input_at (newest mtime among the inputs the job
consumed), consumed (count), produced (count: packets advanced / attempts executed / results
written), note (an explicit no-op reason when produced == 0), workspace (D-23 receipt).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable, Optional

HEPH = Path(__file__).resolve().parent
STATE = HEPH / "STATE.json"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _newest_mtime(paths: Iterable[Path]) -> Optional[str]:
    ts = [p.stat().st_mtime for p in paths if p.exists()]
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(max(ts))) if ts else None


def load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"schema": "hephaestus_state_v1", "jobs": {}}


def record(job: str, consumed: Iterable[Path] = (), produced: int = 0, note: str = "", ok: bool = True) -> dict:
    consumed = list(consumed)
    try:
        from hephaestus.workspace_guard import receipt
        ws = receipt()
    except Exception as e:  # noqa: BLE001
        ws = {"error": repr(e)}
    st = load()
    row = st["jobs"].get(job, {})
    now = _now()
    row.update({"last_run_at": now, "consumed": len(consumed), "produced": int(produced),
                "note": note or ("" if produced else "NO-OP: nothing eligible"), "workspace": ws})
    row["last_input_at"] = _newest_mtime(consumed) or row.get("last_input_at")
    if ok:
        row["last_success_at"] = now
    st["jobs"][job] = row
    st["updated"] = now
    STATE.write_text(json.dumps(st, indent=2, default=str), encoding="utf-8")
    return row


__all__ = ["record", "load", "STATE"]
