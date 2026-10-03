"""Inherited epic priority bands and operator-approved overrides (DISTRIBUTED_WORK.md s13-s14).

Effective priority of a task = (band, local_priority, age). The band comes from the task's epic and can be
raised ONLY by an operator-approved, unexpired priority request committed under ops/operator_queue/priority/.
local_priority (0..99) orders work inside a band and can never cross it. A comms/A2A message changes nothing.
Deterministic; standard library only.
"""
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import core

BANDS = {"SAFETY": 400, "HIGH": 300, "MEDIUM": 200, "LOW": 100}
BAND_NAMES = {v: k for k, v in BANDS.items()}
DEFAULT_BAND = "LOW"                       # an epic that declares no priority, or an unlinked task
QUEUE = core.OPS / "operator_queue"
PRQ_SCHEMA = "prometheus.operator_queue.priority_request.v1"
PRQ_TYPES = ("START_PRIORITY", "PREEMPTION_PROTECTION", "RESOURCE_RESERVATION", "DEADLINE", "ANOMALY_FOLLOWUP")
PRQ_STATES = ("REQUESTED", "APPROVED", "DENIED", "EXPIRED", "WITHDRAWN", "COMPLETED")
PRQ_REQUIRED = ("schema", "request_id", "requester", "epic_id", "thread_id", "campaign_id", "experiment_id",
                "current_priority", "requested_priority", "request_type", "reason", "scientific_value", "why_now",
                "if_delayed", "resources", "expected_runtime", "restart_cost", "preemptible", "window",
                "created_at_utc", "expires_at_utc", "status", "operator_decision", "operator_note", "decided_at_utc")
PRQ_OPTIONAL = ("task_id", "decided_by", "git_ref", "notes")


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _ts(s: Optional[str]) -> Optional[datetime.datetime]:
    if not s:
        return None
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def _iso(d: datetime.datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------------------------------- requests

def load_requests(queue: Path = QUEUE) -> Dict[str, Tuple[Path, dict]]:
    out = {}
    for f in sorted((Path(queue) / "priority").glob("PRQ-*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        out[r.get("request_id", f.stem)] = (f, r)
    return out


def validate_request(r: dict) -> List[str]:
    e = ["request missing " + k for k in PRQ_REQUIRED if k not in r]
    e += ["unknown request field " + k for k in r if k not in PRQ_REQUIRED and k not in PRQ_OPTIONAL]
    if r.get("schema") not in (None, PRQ_SCHEMA):
        e.append("schema must be " + PRQ_SCHEMA)
    if r.get("request_type") not in PRQ_TYPES:
        e.append("request_type must be one of {}".format(PRQ_TYPES))
    if r.get("status") not in PRQ_STATES:
        e.append("status must be one of {}".format(PRQ_STATES))
    for k in ("current_priority", "requested_priority"):
        if r.get(k) not in BANDS:
            e.append("{} must be one of {}".format(k, tuple(BANDS)))
    if r.get("requested_priority") in BANDS and r.get("current_priority") in BANDS and \
            BANDS[r["requested_priority"]] <= BANDS[r["current_priority"]]:
        e.append("requested_priority must be above current_priority (lowering needs no request)")
    if not r.get("expires_at_utc"):
        e.append("a request needs an expiry (expires_at_utc)")
    else:
        try:
            _ts(r["expires_at_utc"]); _ts(r.get("created_at_utc"))
        except ValueError:
            e.append("timestamps must be YYYY-MM-DDTHH:MM:SSZ")
    if r.get("status") in ("APPROVED", "DENIED"):
        if r.get("decided_by") != "operator" or not r.get("decided_at_utc") or not r.get("operator_decision"):
            e.append("APPROVED/DENIED needs decided_by 'operator', operator_decision and decided_at_utc")
    if not (r.get("experiment_id") or r.get("campaign_id") or r.get("task_id")):
        e.append("a request targets an experiment (preferred), a campaign, or a task")
    return e


def active_overrides(queue: Path = QUEUE, now: Optional[datetime.datetime] = None) -> List[dict]:
    """Approved, operator-decided, unexpired requests. Nothing else elevates anything."""
    now = now or _now()
    out = []
    for _, r in load_requests(queue).values():
        if r.get("status") != "APPROVED" or r.get("decided_by") != "operator" or validate_request(r):
            continue
        exp = _ts(r.get("expires_at_utc"))
        if exp is None or now >= exp:
            continue
        out.append(r)
    return out


def _matches(o: dict, t: dict) -> bool:
    """Narrowest declared target wins: task, else experiment (within its campaign), else campaign."""
    if o.get("task_id"):
        return o["task_id"] == t.get("task_id")
    if o.get("experiment_id"):
        return o["experiment_id"] == t.get("experiment_id") and (
            not o.get("campaign_id") or o["campaign_id"] == t.get("campaign_id"))
    return bool(o.get("campaign_id")) and o["campaign_id"] == t.get("campaign_id")


# ------------------------------------------------------------------------------------------------- effective priority

def epic_band(epic_id: Optional[str], ops: Optional[Path]) -> str:
    if not epic_id or ops is None:
        return DEFAULT_BAND
    e = core.load_epics(ops).get(epic_id, (None, {}))[1] or {}
    return e.get("priority", DEFAULT_BAND) if e.get("priority") in BANDS else DEFAULT_BAND


def effective(t: dict, camps: dict, ops: Optional[Path], overrides: List[dict]) -> dict:
    epic = core.resolve_epic(t, camps, ops)
    base = epic_band(epic, ops)
    band = base
    if t.get("safety_critical") is True and epic == "EP-GLOBAL":
        band = "SAFETY"
    applied = None
    for o in overrides:
        if o.get("epic_id") == epic and _matches(o, t) and BANDS[o["requested_priority"]] > BANDS[band]:
            band, applied = o["requested_priority"], o["request_id"]
    created = (t.get("history") or [{}])[0].get("at_utc") or ""
    return {"epic_id": epic, "base_band": base, "band": band, "value": BANDS[band],
            "local": int(t.get("local_priority") or 0), "created_at_utc": created, "override": applied,
            "preemptible": preemptible(t, base, applied)}


def preemptible(t: dict, base_band: str, override: Optional[str]) -> bool:
    """Default: LOW-band work is preemptible, higher bands are not; the packet can say otherwise."""
    if t.get("preemptible") is not None:
        return bool(t["preemptible"])
    if (t.get("execution") or {}).get("preemption_policy") == "NOT_PREEMPTIBLE":
        return False
    return base_band == "LOW"


def sort_key(eff: dict) -> tuple:
    """(band, local, age): higher band first, then higher local, then older."""
    return (-eff["value"], -eff["local"], eff["created_at_utc"])


def may_preempt(running: dict, candidate: dict) -> bool:
    """A READY candidate may displace a running attempt only from a strictly higher band, and only if the
    running work is preemptible. Same band never preempts (lease expiry/release instead)."""
    return running["preemptible"] and candidate["value"] > running["value"]


# ------------------------------------------------------------------------------------------------- views

def render_markdown(queue: Path = QUEUE, now: Optional[datetime.datetime] = None) -> str:
    """ops/operator_queue/PRIORITY_REQUESTS.md: deterministic from the request files."""
    reqs = sorted(load_requests(queue).values(), key=lambda x: x[1].get("created_at_utc", ""))
    open_ = [r for _, r in reqs if r.get("status") == "REQUESTED"]
    lines = ["# Operator priority requests", "",
             "Generated by `python -m workgraph prq render` from ops/operator_queue/priority/PRQ-*.json (the canonical",
             "records). Only the operator decides; a request changes nothing until it is APPROVED here, and only until it",
             "expires. See roles/base-role/DISTRIBUTED_WORK.md s14.", "",
             "## Open ({})".format(len(open_)), ""]
    if open_:
        lines += ["| Request | Seat | Experiment | Current -> Requested | Type | Resource / runtime | Why now | Expires |",
                  "|---|---|---|---|---|---|---|---|"]
        for r in open_:
            lines.append("| {} | {} | {} | {} -> {} | {} | {} / {} | {} | {} |".format(
                r["request_id"], r["requester"], r.get("experiment_id") or r.get("campaign_id"),
                r["current_priority"], r["requested_priority"], r["request_type"],
                _cell(r.get("resources")), _cell(r.get("expected_runtime")), _cell(r.get("why_now")),
                r.get("expires_at_utc")))
    else:
        lines.append("None.")
    closed = [r for _, r in reqs if r.get("status") != "REQUESTED"]
    lines += ["", "## Decided / closed ({})".format(len(closed)), ""]
    for r in closed:
        lines.append("- {} {} ({} -> {}, {}): {}".format(r["request_id"], r["status"], r["current_priority"],
                                                        r["requested_priority"], r["requester"],
                                                        _cell(r.get("operator_note")) or "-"))
    return "\n".join(lines) + "\n"


def _cell(x) -> str:
    s = " ".join(str(x if x is not None else "").split()).replace("|", "/")
    return s if len(s) <= 60 else s[:57] + "..."


def digest(queue: Path = QUEUE, since_utc: Optional[str] = None) -> dict:
    """Data for the email digest: open requests and decisions since the previous digest. Deterministic."""
    reqs = [r for _, r in sorted(load_requests(queue).values(), key=lambda x: x[1].get("created_at_utc", ""))]
    since = _ts(since_utc) if since_utc else None
    counts = {"approved": 0, "denied": 0, "completed": 0, "expired": 0}
    for r in reqs:
        d = _ts(r.get("decided_at_utc")) if r.get("decided_at_utc") else None
        if since is not None and (d is None or d <= since):
            continue
        st = r.get("status", "").lower()
        if st in counts:
            counts[st] += 1
    rows = [{"request": r["request_id"], "seat": r["requester"], "experiment": r.get("experiment_id") or r.get("campaign_id"),
             "change": "{} -> {}".format(r["current_priority"], r["requested_priority"]), "type": r["request_type"],
             "resource_runtime": "{} / {}".format(_cell(r.get("resources")), _cell(r.get("expected_runtime"))),
             "why_now": _cell(r.get("why_now")), "expires": r.get("expires_at_utc")}
            for r in reqs if r.get("status") == "REQUESTED"]
    return {"open": rows, "since": since_utc, "decided_since": counts}


def decide(path: Path, decision: str, note: str, now: Optional[datetime.datetime] = None) -> dict:
    """Operator action: APPROVED or DENIED (or EXPIRED / COMPLETED / WITHDRAWN bookkeeping). Writes the record;
    the caller commits and pushes it -- the committed record is the authority."""
    if decision not in PRQ_STATES or decision == "REQUESTED":
        raise ValueError("decision must be one of {}".format(PRQ_STATES[1:]))
    path = Path(path)
    r = json.loads(path.read_text(encoding="utf-8"))
    r["status"] = decision
    if decision in ("APPROVED", "DENIED"):
        r["operator_decision"] = decision
        r["decided_by"] = "operator"
    r["operator_note"] = note
    r["decided_at_utc"] = _iso(now or _now())
    path.write_text(json.dumps(r, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    return r


def notify_command(r: dict, event: str, git_ref: str = "<sha>", sender: str = "") -> str:
    """The comms post that NOTIFIES (never authorizes) a request event. Body: the committed request file."""
    return ('python -m comms post --from {frm} --to {to} --kind report --subject "{ev} {rid} {exp} {cur}->{req}: {why}" '
            '--body-file ops/operator_queue/priority/{rid}.json').format(
        frm=sender or (r["requester"] if event == "PRIORITY_ELEVATION_REQUESTED" else "Aporia"),
        to="operator" if event == "PRIORITY_ELEVATION_REQUESTED" else r["requester"], ev=event, rid=r["request_id"],
        exp=r.get("experiment_id") or r.get("campaign_id"), cur=r["current_priority"], req=r["requested_priority"],
        why=_cell(r.get("reason"))[:50]) + "   # git ref {}".format(git_ref)
