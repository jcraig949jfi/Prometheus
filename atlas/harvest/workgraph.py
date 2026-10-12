"""Source adapter: the program workgraph (ops/campaigns/C-*/ on a git ref).

The workgraph is the program's own campaign/task/receipt record (schemas
prometheus.workgraph.campaign.v1, .task.v1, .receipt.v1; tool `python -m
workgraph`). Native ids map one to one:

    CAMPAIGN.json   campaign_id C-009         -> campaign   workgraph/C-009
    TASK.json       task_id     C-009-T030    -> experiment workgraph/C-009:C-009-T030
    RECEIPT.json    attempt_id  A-001         -> attempt    ...#A-001

A workgraph task is a unit of work, not necessarily a scientific test: its
`status` (CLOSED, INTEGRATED, ...) is a PROCESS state and is kept verbatim in
reported_disposition, never mapped onto a science class. The receipt's
`result` word (DONE_CLEAN, ...) is likewise kept verbatim.

Edges come only from structured fields: task.depends_on (DEPENDS_ON),
campaign.predecessor / disposition.successor (CONTINUATION_OF; the C-NNN id is
read from the start of the field). Receipt lists are kept as facts:
evidence_added (OBSERVED, as stated by the executor), evidence_executed
(RAN, executed_check), known_escapes (known_escape), unresolved
(open_question, UNRESOLVED).

LEASE.json is coordination state, not evidence, and is not read.
"""
from __future__ import annotations

import re
from typing import Dict, Optional

from atlas import classify, gitsrc
from atlas.harvest import common as C
from atlas import db

VERSION = "workgraph/1"
ENGINE = "workgraph"
PROGRAM = "workgraph"
ROOT = "ops/campaigns"
CID = re.compile(r"^\s*(C-\d{3,})\b")
_V0 = re.compile(r"^ops/campaigns/(C-\d+)/(?:CAMPAIGN\.md|(E-\d+)/(RESULT|EXPERIMENT)\.md)$")
# E-NNN experiments that an engine adapter indexes with richer context (campaign row still made here)
E_OWNED_BY = {"C-002": "aether"}
_PATH = re.compile(r"^ops/campaigns/(C-\d+)/(?:CAMPAIGN\.json|tasks/(C-\d+-[A-Z]+\d+[A-Z]?)/(?:TASK\.json|attempts/([^/]+)/RECEIPT\.json))$")


def _clean(v):
    """Postgres text/jsonb cannot hold NUL; a receipt quoting a grep for it keeps the escape visibly."""
    if isinstance(v, str):
        return v.replace(chr(0), "<NUL>")
    if isinstance(v, list):
        return [_clean(x) for x in v]
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    return v


def _cid(field: Optional[str]) -> Optional[str]:
    m = CID.match(field or "")
    return m.group(1) if m else None


def _host(host_field: Optional[str], instance: Optional[str]):
    tag = (instance or "").split()
    hid = classify.host_from_tag(tag[0]) if tag else None
    if hid:
        return hid, "instance tag {!r} (registry alias)".format(tag[0])
    hid, basis = classify.host_from_text(host_field)
    if hid:
        return hid, "receipt host field: " + basis
    return None, ("receipt host {!r} is not a registered host".format(host_field) if host_field else None)


def _hist_at(task: dict, status: str) -> Optional[str]:
    for h in task.get("history") or []:
        if h.get("status") == status:
            return h.get("at_utc")
    return None


def run(args) -> dict:
    ref = args.ref
    files = {p: (s, z) for p, s, z in gitsrc.ls_tree(ref, ROOT)}
    newest, oldest, _touch = gitsrc.path_commits(ref, ROOT)
    b = C.Batch("workgraph", VERSION, "workgraph")
    camps: Dict[str, dict] = {}
    tasks: Dict[str, dict] = {}
    recs: Dict[str, dict] = {}
    v0: Dict[str, str] = {}
    with gitsrc.CatFile() as cat:
        for path, (sha, _z) in sorted(files.items()):
            if _V0.match(path):
                v0[path] = cat.text(sha) or ""
                continue
            m = _PATH.match(path)
            if not m:
                continue
            try:
                obj = _clean(cat.json(sha))
            except Exception:  # unparseable JSON is recorded as a source with no facts
                obj = None
            if m.group(3):
                recs[path] = obj
            elif m.group(2):
                tasks[path] = obj
            else:
                camps[path] = obj

    def src(path, obj):
        s, z = files[path]
        return b.git_source(ref, path, s, z, newest.get(path), oldest.get(path), obj=obj)

    # campaigns ---------------------------------------------------------------
    for path, c in camps.items():
        cnat = _PATH.match(path).group(1)
        ck = C.campaign_key(PROGRAM, cnat)
        uri = src(path, c)
        c = c or {}
        disp = c.get("disposition") or {}
        b.campaign(campaign_key=ck, program=PROGRAM, native_id=cnat, engine_id=ENGINE,
                   driver_seat=c.get("coordinator_role"), title=c.get("title") or c.get("label"),
                   reported_status=disp.get("result") or disp.get("status") or c.get("status"),
                   summary=C.trunc(c.get("objective")),
                   extract={k: c.get(k) for k in ("schema", "thread_id", "epic_id", "label", "members", "authority",
                                                  "contract", "window_end_utc", "predecessor", "created_by",
                                                  "created_at_utc") if c.get(k) is not None}
                   | ({"disposition": disp} if disp else {}))
        b.link(uri, "campaign", ck, "definition")
        if disp:
            b.conclusion("campaign", ck, disp.get("result") or disp.get("status"), disp.get("record"), uri,
                         "disposition", author=(disp.get("by") or "").split("[")[0] or None,
                         stated_at=disp.get("closed_at_utc"))
        pid = _cid(c.get("predecessor"))
        if pid and pid != cnat:
            b.edge(("campaign", ck), ("campaign", C.campaign_key(PROGRAM, pid)), "CONTINUATION_OF", "EXECUTION",
                   reason="DECLARED_PARENT", basis="DECLARED", confidence="HIGH",
                   detail="CAMPAIGN.json predecessor: {}".format(c.get("predecessor")), uri=uri, locator="predecessor")
        sid = _cid(disp.get("successor"))
        if sid and sid != cnat:
            b.edge(("campaign", C.campaign_key(PROGRAM, sid)), ("campaign", ck), "CONTINUATION_OF", "EXECUTION",
                   reason="DECLARED_PARENT", basis="DECLARED", confidence="HIGH",
                   detail="CAMPAIGN.json disposition.successor: {}".format(disp.get("successor")), uri=uri,
                   locator="disposition.successor")

    # v0 campaigns (2026-09-27 pilot shape: CAMPAIGN.md + E-NNN/EXPERIMENT.md, RESULT.md) ------------------
    for path, text in sorted(v0.items()):
        cnat, enat, which = _V0.match(path).groups()
        ck = C.campaign_key(PROGRAM, cnat)
        if not enat:
            uri = b.git_source(ref, path, files[path][0], files[path][1], newest.get(path), oldest.get(path), text=text)
            owner = re.search(r"Owner:\s*([A-Z][A-Za-z]+)", text)
            b.campaign(campaign_key=ck, program=PROGRAM, native_id=cnat, engine_id=ENGINE,
                       driver_seat=owner.group(1) if owner else None,
                       title=text.split("\n", 1)[0].lstrip("# ").strip()[:300],
                       extract={"shape": "v0 pilot (CAMPAIGN.md, no JSON)"})
            b.link(uri, "campaign", ck, "definition")
            continue
        if E_OWNED_BY.get(cnat):
            continue
        ek = C.experiment_key(ck, enat)
        uri = b.git_source(ref, path, files[path][0], files[path][1], newest.get(path), oldest.get(path), text=text)
        b.experiment(experiment_key=ek, campaign_key=ck, engine_id=ENGINE, native_id=enat, kind="workgraph.v0_experiment",
                     title=text.split("\n", 1)[0].lstrip("# ").strip()[:300], atlas_class="UNKNOWN",
                     atlas_class_confidence="LOW", validity_state="UNKNOWN",
                     atlas_class_method="v0 RESULT.md carries no machine-readable verdict")
        b.link(uri, "experiment", ek, which.lower())

    # tasks -------------------------------------------------------------------
    tkey: Dict[str, str] = {}
    for path, t in tasks.items():
        m = _PATH.match(path)
        cnat, tnat = m.group(1), m.group(2)
        ek = C.experiment_key(C.campaign_key(PROGRAM, cnat), tnat)
        tkey[tnat] = ek
    for path, t in tasks.items():
        m = _PATH.match(path)
        cnat, tnat = m.group(1), m.group(2)
        ck = C.campaign_key(PROGRAM, cnat)
        ek = tkey[tnat]
        uri = src(path, t)
        t = t or {}
        b.experiment(experiment_key=ek, campaign_key=ck, engine_id=ENGINE, native_id=tnat,
                     kind="workgraph." + str(t.get("kind") or "task"), title=t.get("title"),
                     question=C.trunc(t.get("objective"), 2000), purpose=t.get("kind"),
                     driver_seat=t.get("owner_role"), reported_disposition=t.get("status"),
                     atlas_class="UNKNOWN", atlas_class_confidence="LOW",
                     atlas_class_method="workgraph status is a process state, not a scientific verdict",
                     validity_state="UNKNOWN", first_seen_at=_hist_at(t, "PROPOSED"),
                     extract={k: t.get(k) for k in ("schema", "quality_class", "owns", "reads", "deliverables",
                                                    "non_goals", "parent_objective", "escalate_to")
                              if t.get(k) not in (None, [], {})}
                     | {"history": [{"status": h.get("status"), "by": h.get("by"), "at_utc": h.get("at_utc")}
                                    for h in (t.get("history") or [])][:40]})
        b.link(uri, "experiment", ek, "definition")
        if t.get("problem"):
            b.fact("RAN", "open_question", "experiment", ek, "workgraph.problem", t["problem"], uri, "problem",
                   author=t.get("owner_role"))
        for i, ev in enumerate(t.get("evidence_required") or []):
            b.fact("RAN", "condition", "experiment", ek, "workgraph.evidence_required[{}]".format(i), ev, uri,
                   "evidence_required[{}]".format(i))
        acc = t.get("acceptance") or {}
        if acc:
            b.fact("RAN", "condition", "experiment", ek, "workgraph.acceptance", acc, uri, "acceptance")
        for dep in t.get("depends_on") or []:
            dc = _cid(dep)
            if not tkey.get(dep) and not dc:
                b.fact("RAN", "condition", "experiment", ek, "workgraph.depends_on_unresolved", dep, uri, "depends_on")
                continue
            dk = tkey.get(dep) or C.experiment_key(C.campaign_key(PROGRAM, dc), dep)
            b.edge(("experiment", ek), ("experiment", dk), "DEPENDS_ON", "EXECUTION", reason="DECLARED_PARENT",
                   basis="DECLARED", confidence="HIGH", detail="TASK.json depends_on", uri=uri, locator="depends_on")

    # receipts -> attempts ----------------------------------------------------
    last: Dict[str, str] = {}
    for path in sorted(recs):
        _c, tn, an = _PATH.match(path).groups()
        last[tn] = max(last.get(tn, an), an)
    for path, r in recs.items():
        m = _PATH.match(path)
        cnat, tnat, anat = m.groups()
        ek = tkey.get(tnat) or C.experiment_key(C.campaign_key(PROGRAM, cnat), tnat)
        ak = C.attempt_key(ek, anat)
        uri = src(path, r)
        r = r or {}
        hid, hbasis = _host(r.get("host"), r.get("instance"))
        inst = ((r.get("instance") or "").split() or [None])[0]
        res = r.get("result")
        no = re.search(r"(\d+)$", anat)
        b.attempt(attempt_key=ak, experiment_key=ek, native_id=anat, attempt_no=int(no.group(1)) if no else None,
                  of_record=(last.get(tnat) == anat), reported_status=res, validity_state=C.validity_from(res),
                  finished_at=r.get("created_at_utc"), host_id=hid, host_basis=hbasis, instance_tag=inst,
                  operator_seat=r.get("role"), branch=r.get("branch"), commit_sha=r.get("end_sha"),
                  worktree_path=r.get("worktree_path"),
                  budget=r.get("resources") if isinstance(r.get("resources"), dict) else {},
                  result_summary=C.trunc(r.get("notes"), 2000),
                  extract={k: r.get(k) for k in ("schema", "model", "quality_class", "start_sha", "end_sha", "host",
                                                 "instance", "commits", "red_observed") if r.get(k) is not None})
        b.link(uri, "attempt", ak, "receipt")
        who = r.get("role")
        b.fact("RAN", "parameter", "attempt", ak, "workgraph.model", r.get("model"), uri, "model", author=who)
        b.fact("RAN", "parameter", "attempt", ak, "workgraph.quality_class", r.get("quality_class"), uri,
               "quality_class", author=who)
        if r.get("resources"):
            b.fact("RAN", "budget", "attempt", ak, "workgraph.resources", r["resources"], uri, "resources", author=who)
        for i, ev in enumerate(r.get("evidence_executed") or []):
            b.fact("RAN", "executed_check", "attempt", ak, "workgraph.evidence_executed[{}]".format(i), ev, uri,
                   "evidence_executed[{}]".format(i), author=who)
        for i, ev in enumerate(r.get("evidence_added") or []):
            b.fact("OBSERVED", "measurement", "attempt", ak, "workgraph.evidence_added[{}]".format(i), ev, uri,
                   "evidence_added[{}]".format(i), author=who)
        for i, ev in enumerate(r.get("known_escapes") or []):
            b.fact("CONCLUDED", "known_escape", "attempt", ak, "workgraph.known_escapes[{}]".format(i), ev, uri,
                   "known_escapes[{}]".format(i), author=who)
        for i, ev in enumerate(r.get("unresolved") or []):
            b.fact("CONCLUDED", "open_question", "attempt", ak, "workgraph.unresolved[{}]".format(i), ev, uri,
                   "unresolved[{}]".format(i), author=who, status="UNRESOLVED")
        b.conclusion("attempt", ak, res, r.get("notes"), uri, "result", author=who, stated_at=r.get("created_at_utc"))
        b.fact("RAN", "telemetry_availability", "attempt", ak, "workgraph.receipt_lists",
               {k: len(r.get(k) or []) for k in ("evidence_added", "evidence_executed", "known_escapes", "unresolved")},
               uri, "", author="ATLAS_DERIVED")
    with db.harvest("workgraph", VERSION, source_ref="{}:{}".format(ref, ROOT)) as h:
        return b.flush(h)
