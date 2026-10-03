"""Work-graph rules: packet fields, lifecycle, capability classes, receipts, escalations.

The normative text is roles/base-role/DISTRIBUTED_WORK.md; this module is its executable form.
"""
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
OPS = REPO / "ops"
CAMPAIGNS = OPS / "campaigns"

EPIC_SCHEMA = "prometheus.workgraph.epic.v1"
CAMPAIGN_SCHEMA = "prometheus.workgraph.campaign.v1"
TASK_SCHEMA = "prometheus.workgraph.task.v1"
LEASE_SCHEMA = "prometheus.workgraph.lease.v1"
RECEIPT_SCHEMA = "prometheus.workgraph.receipt.v1"

# --------------------------------------------------------------------------------------------------- lifecycle

LIFECYCLE = ("PROPOSED", "READY", "CLAIMED", "RED", "IMPLEMENTING", "GREEN", "LOCAL_REVIEW",
             "INTEGRATION_READY", "INTEGRATED", "CLOSED",
             "BLOCKED", "ESCALATED", "SUPERSEDED", "FAILED_AS_DESIGNED")
TERMINAL = ("CLOSED", "SUPERSEDED", "FAILED_AS_DESIGNED")
WORKING = ("READY", "CLAIMED", "RED", "IMPLEMENTING", "GREEN", "LOCAL_REVIEW", "INTEGRATION_READY")

_FORWARD = {
    "PROPOSED": {"READY"},
    "READY": {"CLAIMED"},
    "CLAIMED": {"RED", "IMPLEMENTING", "READY"},          # READY = lease released without work
    "RED": {"IMPLEMENTING"},
    "IMPLEMENTING": {"GREEN"},
    "GREEN": {"LOCAL_REVIEW", "INTEGRATION_READY", "IMPLEMENTING"},
    "LOCAL_REVIEW": {"INTEGRATION_READY", "IMPLEMENTING"},  # IMPLEMENTING = changes requested
    "INTEGRATION_READY": {"INTEGRATED", "IMPLEMENTING"},   # IMPLEMENTING = integration failed
    "INTEGRATED": {"CLOSED"},
    "BLOCKED": set(WORKING) | {"PROPOSED"},                # resume where it stopped
    "ESCALATED": set(WORKING) | {"PROPOSED", "BLOCKED"},
}
_SIDE = {"BLOCKED", "ESCALATED", "SUPERSEDED", "FAILED_AS_DESIGNED"}
TRANSITIONS: Dict[str, frozenset] = {}
for _s in LIFECYCLE:
    nxt = set(_FORWARD.get(_s, set()))
    if _s not in TERMINAL:
        nxt |= _SIDE - {_s}
    TRANSITIONS[_s] = frozenset(nxt)

# A dependency is satisfied when the upstream task reached one of these, unless the campaign or the packet says otherwise.
SATISFIED_DEFAULT = ("INTEGRATED", "CLOSED")

# --------------------------------------------------------------------------------------------------- fields

TASK_REQUIRED = ("schema", "task_id", "campaign_id", "title", "objective", "owner_role", "quality_class",
                 "can_downgrade", "escalate_to", "depends_on", "problem", "non_goals", "evidence_required",
                 "acceptance", "deliverables", "status", "history")
TASK_OPTIONAL = ("parent_objective", "eligible_roles", "preferred_model", "minimum_model", "requires_shas",
                 "owns", "reads", "resource_ceiling", "escalation_triggers", "kind", "red_required",
                 "satisfied_states", "receipt", "notes", "authority", "experiment_id")
TASK_KINDS = ("software", "science", "document", "review", "operations")

RECEIPT_REQUIRED = ("schema", "task_id", "campaign_id", "attempt_id", "role", "model", "quality_class",
                    "start_sha", "end_sha", "files_changed", "evidence_added", "evidence_executed", "red_observed",
                    "result", "known_escapes", "unresolved", "unblocks", "created_at_utc")
RECEIPT_OPTIONAL = ("instance", "host", "branch", "worktree_path", "resources", "cleanup", "notes")
ATTEMPT_TERMINAL = ("DONE_CLEAN", "FAILED_CLEAN", "BLOCKED_CLEAN", "ABORTED_CLEAN", "DIRTY")

ESCALATION_HEADERS = ("TASK_ID", "BLOCKER", "EVIDENCE", "OPTIONS", "RECOMMENDATION", "CAPABILITY_NEEDED")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def can_transition(old: str, new: str) -> bool:
    return old in TRANSITIONS and new in TRANSITIONS[old]


# --------------------------------------------------------------------------------------------------- epics / threads
# Epic -> Thread -> Campaign -> [Experiment] -> Task -> Attempt (DISTRIBUTED_WORK.md s1a). Epics and the
# thread/campaign links are optional: a campaign without thread_id and a Markdown-only thread stay valid.
# Evidence rolls upward; authority does not -- so an Epic carries no tasks, leases, receipts or claims.

EPIC_REQUIRED = ("schema", "epic_id", "title", "objective", "start_date", "status", "constraints",
                 "exit_conditions", "threads")
EPIC_OPTIONAL = ("north_star", "resource_refs", "operator_decisions", "deferred", "candidate_threads", "notes",
                 "authority")


def load_epics(ops: Path = OPS) -> Dict[str, Tuple[Path, dict]]:
    out = {}
    for f in sorted((Path(ops) / "epics").glob("*/EPIC.json")):
        e = _load(f)
        out[e.get("epic_id", f.parent.name)] = (f.parent, e)
    return out


def thread_epic(ops: Path, thread_id: str) -> Optional[str]:
    """The epic a thread declares ('epic: EP-..' line in ops/threads/<id>.md), '' if none, None if no thread."""
    f = Path(ops) / "threads" / (thread_id + ".md")
    if not f.exists():
        return None
    for line in f.read_text(encoding="utf-8").splitlines()[:30]:
        if line.lower().startswith("epic:"):
            return line.split(":", 1)[1].strip().split()[0] if line.split(":", 1)[1].strip() else ""
    return ""


def validate_epic(e: dict) -> List[str]:
    err = ["epic missing " + k for k in EPIC_REQUIRED if k not in e]
    err += ["epic field {} is not allowed (keep the epic thin: no tasks, leases, receipts or claims)".format(k)
            for k in e if k not in EPIC_REQUIRED and k not in EPIC_OPTIONAL]
    if e.get("schema") not in (None, EPIC_SCHEMA):
        err.append("epic schema must be " + EPIC_SCHEMA)
    for k in ("constraints", "exit_conditions", "threads"):
        if k in e and not isinstance(e[k], list):
            err.append("epic {} must be a list".format(k))
    return err


# --------------------------------------------------------------------------------------------------- loading

def load_campaigns(root: Path = CAMPAIGNS) -> Dict[str, Tuple[Path, dict]]:
    """Campaigns that carry a CAMPAIGN.json (older Markdown-only campaigns are not work graphs)."""
    out = {}
    for f in sorted(Path(root).glob("*/CAMPAIGN.json")):
        c = _load(f)
        out[c.get("campaign_id", f.parent.name)] = (f.parent, c)
    return out


def load_tasks(root: Path = CAMPAIGNS) -> Dict[str, Tuple[Path, dict]]:
    out = {}
    for f in sorted(Path(root).glob("*/tasks/*/TASK.json")):
        t = _load(f)
        out[t.get("task_id", f.parent.name)] = (f.parent, t)
    return out


# --------------------------------------------------------------------------------------------------- validation

def validate_campaign(c: dict) -> List[str]:
    e = []
    for k in ("schema", "campaign_id", "title", "objective", "coordinator_role", "authority", "quality_classes"):
        if k not in c:
            e.append("campaign missing " + k)
    if "epic_id" in c:
        e.append("a campaign names its thread_id, not an epic (the thread names the epic)")
    if c.get("schema") not in (None, CAMPAIGN_SCHEMA):
        e.append("campaign schema must be " + CAMPAIGN_SCHEMA)
    qc = c.get("quality_classes", {})
    if not isinstance(qc, dict) or not qc:
        e.append("quality_classes must be a non-empty object {class_id: {...}}")
    else:
        for cid, spec in qc.items():
            if not isinstance(spec, dict) or "description" not in spec:
                e.append("quality class {} needs a description".format(cid))
            if isinstance(spec, dict) and "rank" in spec and not isinstance(spec["rank"], int):
                e.append("quality class {} rank must be an integer".format(cid))
    for s in c.get("satisfied_states", []):
        if s not in LIFECYCLE:
            e.append("unknown satisfied state " + s)
    return e


def validate_task(t: dict, campaign: Optional[dict] = None, known_tasks: Optional[set] = None) -> List[str]:
    e = []
    for k in TASK_REQUIRED:
        if k not in t:
            e.append("missing " + k)
    for k in t:
        if k not in TASK_REQUIRED and k not in TASK_OPTIONAL and k != "lease":
            e.append("unknown field " + k)
    if t.get("schema") not in (None, TASK_SCHEMA):
        e.append("schema must be " + TASK_SCHEMA)
    st = t.get("status")
    if st not in LIFECYCLE:
        e.append("unknown status {!r}".format(st))
    if "kind" in t and t["kind"] not in TASK_KINDS:
        e.append("kind must be one of {}".format(TASK_KINDS))
    if not isinstance(t.get("can_downgrade"), bool):
        e.append("can_downgrade must be true or false")
    for k in ("depends_on", "non_goals", "evidence_required", "deliverables", "history"):
        if k in t and not isinstance(t[k], list):
            e.append(k + " must be a list")
    acc = t.get("acceptance")
    if acc is not None and not (isinstance(acc, dict) and (acc.get("command") or acc.get("condition"))):
        e.append("acceptance needs a command or a condition")
    if campaign is not None:
        qc = campaign.get("quality_classes", {})
        if t.get("quality_class") not in qc:
            e.append("quality_class {!r} is not declared by campaign {}".format(t.get("quality_class"),
                                                                              campaign.get("campaign_id")))
        if t.get("campaign_id") != campaign.get("campaign_id"):
            e.append("campaign_id does not match its campaign")
    if known_tasks is not None:
        for d in t.get("depends_on", []):
            if d not in known_tasks:
                e.append("depends on unknown task " + d)
        if t.get("task_id") in t.get("depends_on", []):
            e.append("depends on itself")
    hist = t.get("history", [])
    if isinstance(hist, list):
        prev = None
        for i, h in enumerate(hist):
            if not isinstance(h, dict) or "status" not in h or "by" not in h or "at_utc" not in h:
                e.append("history[{}] needs status, by, at_utc".format(i)); continue
            if prev is not None and not can_transition(prev, h["status"]):
                e.append("illegal transition {} -> {} at history[{}]".format(prev, h["status"], i))
            prev = h["status"]
        if hist and prev != st:
            e.append("status {} differs from the last history entry {}".format(st, prev))
        if t.get("kind", "software") == "software" and t.get("red_required", True):
            seen = [h.get("status") for h in hist if isinstance(h, dict)]
            if "GREEN" in seen and "RED" not in seen[:seen.index("GREEN")]:
                e.append("GREEN reached without a RED (set red_required false, with a reason in notes, if none applies)")
    return e


def validate_receipt(r: dict) -> List[str]:
    e = ["receipt missing " + k for k in RECEIPT_REQUIRED if k not in r]
    if r.get("schema") not in (None, RECEIPT_SCHEMA):
        e.append("receipt schema must be " + RECEIPT_SCHEMA)
    if r.get("result") not in ATTEMPT_TERMINAL:
        e.append("result must be one of {}".format(ATTEMPT_TERMINAL))
    for k in ("files_changed", "evidence_added", "evidence_executed", "known_escapes", "unresolved", "unblocks"):
        if k in r and not isinstance(r[k], list):
            e.append(k + " must be a list")
    ro = r.get("red_observed")
    if ro is not None and not (isinstance(ro, bool) or (isinstance(ro, dict) and "observed" in ro)):
        e.append("red_observed must be true/false/null or {observed, ...}")
    return e


def validate_escalation(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines()]
    return ["escalation missing " + h for h in ESCALATION_HEADERS
            if not any(ln.upper().startswith(h + ":") or ln.upper().startswith("## " + h) for ln in lines)]


def validate_all(root: Path = CAMPAIGNS, ops: Optional[Path] = None) -> Dict[str, List[str]]:
    """ops: the ops/ directory holding epics/ and threads/ (default: this repository's, when root is too)."""
    camps = load_campaigns(root)
    tasks = load_tasks(root)
    errs: Dict[str, List[str]] = {}
    if ops is None and Path(root) == CAMPAIGNS:
        ops = OPS
    if ops is not None:
        epics = load_epics(ops)
        for eid, (_, e) in epics.items():
            x = validate_epic(e)
            for th in e.get("threads", []):
                te = thread_epic(ops, th)
                if te is None:
                    x.append("thread {} not found at ops/threads/{}.md".format(th, th))
                elif te != eid:
                    x.append("thread {} declares epic {!r}, not {}".format(th, te, eid))
            if x:
                errs["epic " + eid] = x
        for cid, (_, c) in camps.items():
            th = c.get("thread_id")
            if not th:
                continue
            te = thread_epic(ops, th)
            x = []
            if te is None:
                x.append("thread_id {} not found at ops/threads/{}.md".format(th, th))
            elif te and te not in epics:
                x.append("thread {} declares unknown epic {}".format(th, te))
            elif te and th not in epics[te][1].get("threads", []):
                x.append("thread {} is not listed in epic {} threads".format(th, te))
            if x:
                errs.setdefault("campaign " + cid, []).extend(x)
    for cid, (_, c) in camps.items():
        x = validate_campaign(c)
        if x:
            errs["campaign " + cid] = x
    for tid, (d, t) in tasks.items():
        camp = camps.get(t.get("campaign_id"), (None, None))[1]
        x = validate_task(t, camp, set(tasks))
        if camp is None:
            x.append("campaign {} has no CAMPAIGN.json".format(t.get("campaign_id")))
        if d.name != tid:
            x.append("directory name {} differs from task_id".format(d.name))
        for rf in sorted(d.glob("attempts/*/RECEIPT.json")):
            x += ["{}: {}".format(rf.parent.name, m) for m in validate_receipt(_load(rf))]
        if x:
            errs["task " + tid] = x
    return errs


def capability(t: dict, campaign: dict) -> dict:
    """The effective capability requirement of a task: the packet's own fields, else its class defaults.
    Model names are campaign/charter data; the protocol only knows abstract classes and their ranks."""
    spec = dict(campaign.get("quality_classes", {}).get(t.get("quality_class"), {}))
    return {
        "quality_class": t.get("quality_class"),
        "rank": spec.get("rank"),
        "preferred_model": t.get("preferred_model") or spec.get("default_model"),
        "minimum_model": t.get("minimum_model") or spec.get("minimum_model"),
        "can_downgrade": bool(t.get("can_downgrade", False)),
        "escalate_to": t.get("escalate_to") or spec.get("escalate_to"),
    }


# --------------------------------------------------------------------------------------------------- discovery

def _satisfied(t: dict, tasks: Dict[str, Tuple[Path, dict]], camps: Dict[str, Tuple[Path, dict]]) -> List[str]:
    """Unmet dependencies of t (empty list = all satisfied)."""
    camp = camps.get(t.get("campaign_id"), (None, {}))[1] or {}
    ok = tuple(t.get("satisfied_states") or camp.get("satisfied_states") or SATISFIED_DEFAULT)
    unmet = []
    for d in t.get("depends_on", []):
        dep = tasks.get(d)
        if dep is None or dep[1].get("status") not in ok:
            unmet.append("{} ({})".format(d, dep[1].get("status") if dep else "missing"))
    return unmet


def ready_for(seat: str, root: Path = CAMPAIGNS) -> List[dict]:
    """READY tasks this seat may claim: owner_role or eligible_roles names it, dependencies satisfied, no lease."""
    camps, tasks = load_campaigns(root), load_tasks(root)
    out = []
    for tid, (d, t) in tasks.items():
        if t.get("status") != "READY":
            continue
        if seat != t.get("owner_role") and seat not in t.get("eligible_roles", []):
            continue
        if (d / "LEASE.json").exists() or _satisfied(t, tasks, camps):
            continue
        out.append(t)
    return sorted(out, key=lambda t: t["task_id"])


def blocked_by_dependencies(root: Path = CAMPAIGNS) -> Dict[str, List[str]]:
    camps, tasks = load_campaigns(root), load_tasks(root)
    return {tid: _satisfied(t, tasks, camps) for tid, (_, t) in tasks.items()
            if t.get("status") == "READY" and _satisfied(t, tasks, camps)}


# --------------------------------------------------------------------------------------------------- mutation

def transition(task_dir: Path, new: str, by: str, note: str = "", root: Path = CAMPAIGNS) -> dict:
    """Write a legal status change (and LEASE.json on CLAIMED, its removal on release). The caller commits
    the task directory by explicit paths and pushes fast-forward; a rejected push means somebody else moved
    first: fetch, re-read, and only retry if the transition is still legal."""
    task_dir = Path(task_dir)
    t = _load(task_dir / "TASK.json")
    old = t["status"]
    if not can_transition(old, new):
        raise ValueError("illegal transition {} -> {}".format(old, new))
    lease = task_dir / "LEASE.json"
    if new == "CLAIMED":
        if lease.exists():
            raise ValueError("already leased: " + _load(lease).get("holder", "?"))
        if t.get("depends_on"):
            camps, tasks = load_campaigns(root), load_tasks(root)
            unmet = _satisfied(t, tasks, camps)
            if unmet:
                raise ValueError("dependencies not satisfied: " + ", ".join(unmet))
        _dump(lease, {"schema": LEASE_SCHEMA, "task_id": t["task_id"], "holder": by, "claimed_at_utc": _now(),
                      "note": note})
    if new in ("READY",) + TERMINAL and lease.exists():
        lease.unlink()
    t["status"] = new
    t["history"].append({"status": new, "by": by, "at_utc": _now(), "note": note})
    _dump(task_dir / "TASK.json", t)
    return t
