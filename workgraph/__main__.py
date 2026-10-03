"""python -m workgraph <command>   (roles/base-role/DISTRIBUTED_WORK.md s9)

    validate                      every CAMPAIGN.json, TASK.json and attempt RECEIPT.json under ops/campaigns/
    ready <Seat>                  READY tasks this seat may claim now (dependencies met, no lease)
    status [<campaign_id>]        task counts by status, and READY tasks still waiting on dependencies
    show <task_id>                one packet, with its effective capability requirement
    transition <task_id> <STATUS> --by <Seat[tag]> [--note ...]
                                  write a legal status change (CLAIMED writes LEASE.json); then commit the task
                                  directory by explicit paths and push fast-forward to main -- the push is the claim
    check-receipt <file>          validate an attempt receipt
    check-escalation <file>       validate an escalation body (TASK_ID / BLOCKER / EVIDENCE / OPTIONS /
                                  RECOMMENDATION / CAPABILITY_NEEDED)
    escalation-template <task_id> print an escalation body to fill in
    report [--json]               non-terminal tasks with epic / thread / campaign / state / class / holder / host
    epics                         the epics, their status and threads
    new-campaign <template> --owner <Seat> --subject <engine or topic> --by <Seat[tag]> [--id C-NNN]
                                  instantiate ops/templates/<template>/ (e.g. P2B-ENGINE-REENTRY); then commit
                                  and push the new campaign directory
    priority <task_id>            effective priority (epic band, local, override, preemptible)
    prq validate | render | decide <PRQ-id> <APPROVED|DENIED|EXPIRED|COMPLETED|WITHDRAWN> --note ".." |
        notify <PRQ-id> <EVENT> | template
                                  operator priority requests (ops/operator_queue/); `decide` is the operator's act
    cwo-inputs <epic_id> [--hours 48] [--previous CWO-ID]
                                  deterministic JSON of the window's moves, receipts, preemptions, escalations,
                                  priority requests and cross-epic findings (input to the next CWO)
    worker: python -m workgraph.worker [--dry-run|--once] (roles/generic-worker-role/)
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from . import core


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="workgraph", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    r = sub.add_parser("ready"); r.add_argument("seat")
    s = sub.add_parser("status"); s.add_argument("campaign", nargs="?")
    sh = sub.add_parser("show"); sh.add_argument("task_id")
    tr = sub.add_parser("transition"); tr.add_argument("task_id"); tr.add_argument("status")
    tr.add_argument("--by", required=True); tr.add_argument("--note", default="")
    cr = sub.add_parser("check-receipt"); cr.add_argument("file")
    ce = sub.add_parser("check-escalation"); ce.add_argument("file")
    et = sub.add_parser("escalation-template"); et.add_argument("task_id")
    rp = sub.add_parser("report"); rp.add_argument("--json", action="store_true")
    sub.add_parser("epics")
    nc = sub.add_parser("new-campaign"); nc.add_argument("template"); nc.add_argument("--owner", required=True)
    nc.add_argument("--subject", required=True); nc.add_argument("--by", required=True); nc.add_argument("--id")
    pp = sub.add_parser("priority"); pp.add_argument("task_id")
    pq = sub.add_parser("prq"); pq.add_argument("action", choices=["validate", "render", "decide", "notify", "template"])
    pq.add_argument("args", nargs="*"); pq.add_argument("--note", default="")
    cw = sub.add_parser("cwo-inputs"); cw.add_argument("epic_id"); cw.add_argument("--hours", type=float, default=48.0)
    cw.add_argument("--previous", default="")
    a = p.parse_args(argv)
    from . import priority as P, cwo as CWO

    if a.cmd == "priority":
        tasks, camps = core.load_tasks(), core.load_campaigns()
        if a.task_id not in tasks:
            print("unknown task " + a.task_id, file=sys.stderr); return 2
        print(json.dumps(P.effective(tasks[a.task_id][1], camps, core.OPS, P.active_overrides()), indent=2))
        return 0

    if a.cmd == "cwo-inputs":
        print(json.dumps(CWO.inputs(a.epic_id, a.hours, previous_cwo=a.previous), indent=2))
        return 0

    if a.cmd == "prq":
        reqs = P.load_requests()
        if a.action == "validate":
            bad = {k: P.validate_request(r) for k, (_, r) in reqs.items() if P.validate_request(r)}
            for k, v in bad.items():
                print("{}: {}".format(k, "; ".join(v)))
            print("{} request(s): {}".format(len(reqs), "OK" if not bad else "{} with errors".format(len(bad))))
            return 1 if bad else 0
        if a.action == "render":
            out = P.QUEUE / "PRIORITY_REQUESTS.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(P.render_markdown(), encoding="utf-8", newline="\n")
            print("wrote " + str(out.relative_to(core.REPO)).replace("\\", "/"))
            return 0
        if a.action == "template":
            print(json.dumps({k: None for k in P.PRQ_REQUIRED}, indent=2))
            return 0
        if not a.args or a.args[0] not in reqs:
            print("unknown request", file=sys.stderr); return 2
        path, r = reqs[a.args[0]]
        if a.action == "decide":
            if len(a.args) < 2:
                print("decide <PRQ-id> <STATE> --note ..", file=sys.stderr); return 2
            P.decide(path, a.args[1], a.note)
            print("recorded {} {}; commit {} and re-render; the committed record is the authority".format(
                a.args[0], a.args[1], str(path.relative_to(core.REPO)).replace("\\", "/")))
            return 0
        if a.action == "notify":
            ev = a.args[1] if len(a.args) > 1 else "PRIORITY_ELEVATION_REQUESTED"
            print(P.notify_command(r, ev))
            return 0

    if a.cmd == "report":
        rows = core.report()
        if a.json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                print("{epic_id} / {thread_id} / {campaign_id} / {task_id}  {status}  {quality_class}  "
                      "holder={holder} host={host}".format(**r))
            print("{} active task(s)".format(len(rows)))
        return 0

    if a.cmd == "epics":
        for eid, (_, e) in core.load_epics().items():
            print("{}  {}{}  threads={}  {}".format(eid, e.get("status"), " PERMANENT" if e.get("permanent") else "",
                                                  ",".join(e.get("threads", [])), e.get("title")))
        return 0

    if a.cmd == "new-campaign":
        try:
            d = core.new_campaign(a.template, a.owner, a.subject, a.by, campaign_id=a.id)
        except ValueError as ex:
            print("REFUSED: {}".format(ex), file=sys.stderr)
            return 1
        rel = str(d.relative_to(core.REPO)).replace("\\", "/")
        print("created {} (tasks PROPOSED; tailor them, make them READY, then git add {} ; commit ; push "
              "fast-forward to main)".format(rel, rel))
        return 0

    if a.cmd == "validate":
        errs = core.validate_all()
        n_e, n_c, n_t = len(core.load_epics()), len(core.load_campaigns()), len(core.load_tasks())
        for k, v in errs.items():
            for m in v:
                print("{}: {}".format(k, m))
        print("{} epic(s), {} campaign(s), {} task(s): {}".format(n_e, n_c, n_t, "OK" if not errs else "{} with errors".format(len(errs))))
        return 1 if errs else 0

    if a.cmd == "ready":
        rows = core.ready_for(a.seat)
        camps = core.load_campaigns()
        for t in rows:
            cap = core.capability(t, camps.get(t["campaign_id"], (None, {}))[1])
            print("{}  [{} pref={} min={} downgrade={}]  {}".format(t["task_id"], cap["quality_class"],
                  cap["preferred_model"], cap["minimum_model"], cap["can_downgrade"], t["title"]))
        if not rows:
            print("no READY task for {} (report READY; run the inherited work-conserving loop)".format(a.seat))
        return 0

    if a.cmd == "status":
        tasks = {k: v for k, v in core.load_tasks().items() if not a.campaign or v[1].get("campaign_id") == a.campaign}
        c = Counter(t["status"] for _, t in tasks.values())
        for st in core.LIFECYCLE:
            if c.get(st):
                print("{:<18} {}".format(st, c[st]))
        for tid, unmet in sorted(core.blocked_by_dependencies().items()):
            if tid in tasks:
                print("waiting {}: {}".format(tid, ", ".join(unmet)))
        print("{} task(s)".format(len(tasks)))
        return 0

    tasks = core.load_tasks()
    if a.cmd in ("show", "transition", "escalation-template") and a.task_id not in tasks:
        print("unknown task " + a.task_id, file=sys.stderr)
        return 2

    if a.cmd == "show":
        d, t = tasks[a.task_id]
        camp = core.load_campaigns().get(t["campaign_id"], (None, {}))[1]
        out = dict(t, capability=core.capability(t, camp), lease_exists=(d / "LEASE.json").exists(),
                   path=str(d.relative_to(core.REPO)).replace("\\", "/"))
        print(json.dumps(out, indent=2))
        return 0

    if a.cmd == "transition":
        d, _ = tasks[a.task_id]
        try:
            t = core.transition(d, a.status, a.by, a.note)
        except ValueError as ex:
            print("REFUSED: {}".format(ex), file=sys.stderr)
            return 1
        rel = str(d.relative_to(core.REPO)).replace("\\", "/")
        print("{} -> {}. Now: git add {} ; commit ; push fast-forward to main. Rejected push = lost race: "
              "fetch, re-read, retry only if still legal.".format(t["task_id"], t["status"], rel))
        return 0

    if a.cmd == "check-receipt":
        errs = core.validate_receipt(json.loads(Path(a.file).read_text(encoding="utf-8")))
        print("\n".join(errs) or "receipt OK")
        return 1 if errs else 0

    if a.cmd == "check-escalation":
        errs = core.validate_escalation(Path(a.file).read_text(encoding="utf-8"))
        print("\n".join(errs) or "escalation OK")
        return 1 if errs else 0

    if a.cmd == "escalation-template":
        _, t = tasks[a.task_id]
        print("TASK_ID: {}\nBLOCKER: \nEVIDENCE: \nOPTIONS:\n  1. \n  2. \nRECOMMENDATION: \nCAPABILITY_NEEDED: {}\n"
              .format(t["task_id"], t.get("escalate_to") or "(class or role)"))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
