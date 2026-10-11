"""python -m rso.scale.notify <command>   (C-016-T011)

    scan  [--campaign C-016 ...|--coordinator Palamedes] [--from Eupalamus] [--to Palamedes] [--dry-run]
          one comms notice per pending INTEGRATION_READY (task, head sha); disposition notices for earlier ones
    queue [--campaign ...|--coordinator ...] [--no-db]      the pending integration queue with age
Reads ops/campaigns of the checkout it runs in (use a worktree at origin/main). Writes comms only.
"""
import argparse
import json
import sys

from rso.scale.notify import notify as N


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m rso.scale.notify")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "queue"):
        s = sub.add_parser(name)
        s.add_argument("--campaign", action="append", help="campaign id (repeatable)")
        s.add_argument("--coordinator", help="every campaign whose coordinator_role is this seat")
        s.add_argument("--root", default=None, help="campaigns directory (default ops/campaigns)")
        s.add_argument("--json", action="store_true")
        if name == "scan":
            s.add_argument("--from", dest="sender", default="Eupalamus")
            s.add_argument("--to", default="Palamedes")
            s.add_argument("--dry-run", action="store_true")
        else:
            s.add_argument("--no-db", action="store_true")
    a = ap.parse_args(argv)
    if not a.campaign and not a.coordinator:
        ap.error("give --campaign and/or --coordinator")
    root = a.root or "ops/campaigns"
    if a.cmd == "scan":
        sink = N.DbSink(sender=a.sender, to=a.to.split(","))
        r = N.scan(root, sink, a.campaign, a.coordinator, dry_run=a.dry_run)
        print(json.dumps(r, indent=1) if a.json else "posted {} already {} dispositions {}{}".format(
            [(p["key"], p["id"]) for p in r["posted"]], r["already"],
            [(d["key"], d["disposition"], d["id"]) for d in r["dispositions"]], "  (dry run)" if a.dry_run else ""))
    else:
        sink = None if a.no_db else N.DbSink()
        rows = N.queue(root, sink, a.campaign, a.coordinator)
        if a.json:
            print(json.dumps(rows, indent=1))
        elif not rows:
            print("integration queue empty")
        else:
            for q in rows:
                print("{:<12} {:>5} min  {}  {}  by {}  sha {}  notified={}".format(
                    q["task_id"], q["age_minutes"], q["campaign_id"], q["since_utc"], q["by"],
                    (q["sha"] or "-")[:12], q["notified"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
