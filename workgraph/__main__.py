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
    a = p.parse_args(argv)

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
