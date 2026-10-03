"""Deterministic CWO inputs for an epic over a window (default 48 h) -- DISTRIBUTED_WORK.md s15.

Assembles, from Git files only, what a seat (or Aporia, publishing) needs at the CWO boundary: tasks that moved,
attempt receipts by close category, preemptions to replay unchanged, open escalations, unresolved items,
priority requests and cross-epic findings. No interpretation: categories come from receipts and states.
"""
import datetime
from pathlib import Path
from typing import Optional

from . import core, priority

# Close categories at a CWO boundary (directive s23)
CATEGORY = {"DONE_CLEAN": "DONE", "PREEMPTED_RESOURCE": "PREEMPTED_RESOURCE", "FAILED_CLEAN": "ENGINEERING_FAIL",
            "DIRTY": "ENGINEERING_FAIL", "ABORTED_CLEAN": "DEFERRED", "BLOCKED_CLEAN": "DEFERRED"}
STATE_CATEGORY = {"FAILED_AS_DESIGNED": "SCIENTIFIC_OUTCOME", "SUPERSEDED": "SUPERSEDED"}


def _in(ts: Optional[str], since: datetime.datetime) -> bool:
    try:
        return bool(ts) and priority._ts(ts) >= since
    except ValueError:
        return False


def inputs(epic_id: str, hours: float = 48.0, root: Path = core.CAMPAIGNS, now=None, previous_cwo: str = "") -> dict:
    now = now or priority._now()
    since = now - datetime.timedelta(hours=hours)
    ops = core._ops_for(root) or Path(root).parent
    camps, tasks = core.load_campaigns(root), core.load_tasks(root)
    out = {"schema": "prometheus.cwo_inputs.v1", "epic_id": epic_id, "window_hours": hours,
           "since_utc": priority._iso(since), "until_utc": priority._iso(now), "previous_cwo": previous_cwo or None,
           "campaigns": [], "moved": [], "closed": {}, "replay_unchanged": [], "escalated": [], "unresolved": [],
           "open_ready_or_running": [], "priority_requests": [], "cross_epic_findings": [], "resource_use": {}}
    for cid, (_, c) in sorted(camps.items()):
        if core.resolve_epic({"campaign_id": cid}, camps, ops) == epic_id:
            out["campaigns"].append({"campaign_id": cid, "thread_id": c.get("thread_id"), "status": c.get("status", "OPEN"),
                                     "coordinator": c.get("coordinator_role")})
    mine = {cid for cid in (x["campaign_id"] for x in out["campaigns"])}
    wall = 0.0
    for tid, (d, t) in sorted(tasks.items()):
        if t.get("campaign_id") not in mine:
            continue
        hist = [h for h in t.get("history", []) if _in(h.get("at_utc"), since)]
        if hist:
            out["moved"].append({"task_id": tid, "owner": t.get("owner_role"), "now": t["status"],
                                 "transitions": [h["status"] for h in hist], "experiment_id": t.get("experiment_id")})
        if t["status"] in STATE_CATEGORY and hist:
            out["closed"].setdefault(STATE_CATEGORY[t["status"]], []).append(tid)
        if t["status"] in ("ESCALATED", "BLOCKED"):
            out["escalated"].append({"task_id": tid, "owner": t.get("owner_role"), "status": t["status"]})
        if t["status"] in ("READY", "CLAIMED", "RED", "IMPLEMENTING"):
            out["open_ready_or_running"].append({"task_id": tid, "status": t["status"],
                                                 "executor_class": core.executor_class(t)})
        for rf in sorted(d.glob("attempts/*/RECEIPT.json")):
            r = core._load(rf)
            if not _in(r.get("created_at_utc"), since):
                continue
            cat = CATEGORY.get(r.get("result"), "DEFERRED")
            out["closed"].setdefault(cat, []).append("{}/{}".format(tid, r.get("attempt_id")))
            if cat == "PREEMPTED_RESOURCE":
                out["replay_unchanged"].append({"task_id": tid, "attempt": r.get("attempt_id"),
                                                "experiment_id": r.get("experiment_id"),
                                                "instruction": "replay unchanged when capacity becomes available"})
            for u in r.get("unresolved", []):
                out["unresolved"].append({"task_id": tid, "attempt": r.get("attempt_id"), "item": u})
            wall += float((r.get("resources") or {}).get("wall_s") or 0)
    out["resource_use"] = {"attempt_wall_s": round(wall, 1)}
    for _, r in priority.load_requests(ops / "operator_queue").values():
        if r.get("epic_id") == epic_id and (r.get("status") == "REQUESTED" or _in(r.get("decided_at_utc"), since)):
            out["priority_requests"].append({k: r.get(k) for k in ("request_id", "requester", "experiment_id",
                                                                   "status", "requested_priority", "expires_at_utc")})
    for f in sorted((ops / "epics" / epic_id / "findings").glob("*.md")):
        out["cross_epic_findings"].append(str(f.relative_to(ops.parent)).replace("\\", "/"))
    return out
