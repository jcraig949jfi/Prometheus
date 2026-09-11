"""python -m comms <command> ...   (see comms/__init__.py)"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import api


def _print_messages(msgs, full: bool = True) -> None:
    for m in msgs:
        head = "[{}] {} {} -> {} | {} | {}".format(m["id"], str(m["created_at"])[:16], m["sender"], ",".join(m["recipients"]), m["kind"], m["subject"])
        print(head)
        if full:
            print("    " + m["body"].replace("\n", "\n    "))
            print("    sha256 {}{}".format(m["sha256"][7:23], ("  task_ref " + m["task_ref"]) if m.get("task_ref") else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="comms")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("roster")
    s = sub.add_parser("sync"); s.add_argument("agent"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("inbox"); s.add_argument("agent"); s.add_argument("--all", action="store_true"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("tasks"); s.add_argument("agent"); s.add_argument("--status", default="queued")
    s = sub.add_parser("post"); s.add_argument("--from", dest="sender", required=True); s.add_argument("--to", required=True, help="Seat, comma list, or *")
    s.add_argument("--kind", default="prompt", choices=api.KINDS); s.add_argument("--subject", required=True)
    s.add_argument("--body-file", required=True); s.add_argument("--reply-to", type=int); s.add_argument("--task-ref"); s.add_argument("--priority", type=int, default=100)
    s = sub.add_parser("done"); s.add_argument("agent"); s.add_argument("message_id", type=int); s.add_argument("--note")
    s = sub.add_parser("boot"); s.add_argument("agent"); s.add_argument("--model"); s.add_argument("--capabilities", default="")
    s.add_argument("--status", default="active"); s.add_argument("--session-id"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("who"); s.add_argument("--minutes", type=int, default=api.ONLINE_MINUTES); s.add_argument("--json", action="store_true")
    s = sub.add_parser("status"); s.add_argument("agent"); s.add_argument("state", choices=["active", "parked", "dormant", "blocked", "retired"]); s.add_argument("--note")
    s = sub.add_parser("show"); s.add_argument("message_id", type=int)
    s = sub.add_parser("claim"); s.add_argument("agent"); s.add_argument("message_id", type=int)
    a = ap.parse_args(argv)
    conn = api.connect(require_schema=(a.cmd != "init"))
    try:
        if a.cmd == "init":
            api.init_schema(conn); print("comms schema", api.schema(), "ready"); return 0
        if a.cmd == "roster":
            print("\n".join(api.roster())); return 0
        if a.cmd == "sync":
            r = api.sync(conn, a.agent)
            if a.json:
                print(json.dumps(r, default=str, indent=1)); return 0
            print("== {} sync at {}: {} new, {} queued; queue length {}".format(a.agent, r["at"], len(r["new"]), len(r["queued"]), len(r["queue"])))
            _print_messages(r["new"])
            if r["queue"]:
                print("== task queue (in order)")
                for t in r["queue"]:
                    print("  #{} [{}] {} {} | {}".format(t["position"], t["id"], t["sender"], t["kind"], t["subject"]))
            return 0
        if a.cmd == "inbox":
            msgs = api.inbox(conn, a.agent, unseen_only=not a.all)
            if a.json:
                print(json.dumps(msgs, default=str, indent=1))
            else:
                _print_messages(msgs)
            return 0
        if a.cmd == "tasks":
            for t in api.tasks(conn, a.agent, a.status):
                print("#{} [{}] {} {} | {}{}".format(t["position"], t["id"], t["sender"], t["kind"], t["subject"], ("  " + t["task_ref"]) if t["task_ref"] else ""))
            return 0
        if a.cmd == "post":
            body = Path(a.body_file).read_text(encoding="utf-8")
            to = [x.strip() for x in a.to.split(",")]
            mid = api.post(conn, a.sender, to, a.kind, a.subject, body, reply_to=a.reply_to, task_ref=a.task_ref, priority=a.priority)
            print("posted", mid); return 0
        if a.cmd == "done":
            api.done(conn, a.agent, a.message_id, a.note); print("done", a.message_id); return 0
        if a.cmd == "boot":
            caps = [x.strip() for x in a.capabilities.split(",") if x.strip()]
            r = api.boot(conn, a.agent, model=a.model, capabilities=caps, status=a.status, session_id=a.session_id)
            if a.json:
                print(json.dumps(r, default=str, indent=1))
            else:
                print("booted {} on {} | model {} ({}) | {} @ {} [{}] | session {}".format(
                    r["agent"], r["machine"], r["model"], r["tier"], (r["workspace"].get("base_sha") or "?")[:9],
                    r["workspace"].get("worktree_path"), r["workspace"].get("branch"), r["session_id"]))
            return 0
        if a.cmd == "who":
            rows = api.who(conn, online_minutes=a.minutes)
            if a.json:
                print(json.dumps(rows, default=str, indent=1)); return 0
            print("{:<12} {:<7} {:<10} {:<8} {:<18} {:<6} {:<6} {:<17} {:<10} {}".format("agent", "online", "status", "tier", "model", "queued", "unseen", "last_sync", "sync_sha", "capabilities"))
            for r in rows:
                print("{:<12} {:<7} {:<10} {:<8} {:<18} {:<6} {:<6} {:<17} {:<10} {}".format(
                    r["agent"], "yes" if r["online"] else "no", r["status"], r.get("tier") or "?", (r.get("model") or "?")[:18],
                    r.get("queued") or 0, "?" if r.get("unseen") is None else r["unseen"], str(r.get("last_sync_at") or "-")[:16],
                    (r.get("last_sync_sha") or "-")[:9], ",".join(r.get("capabilities") or [])))
            return 0
        if a.cmd == "status":
            api.set_status(conn, a.agent, a.state, a.note); print(a.agent, "->", a.state); return 0
        if a.cmd == "show":
            print(json.dumps(api.message_status(conn, a.message_id), default=str, indent=1)); return 0
        if a.cmd == "claim":
            api.claim(conn, a.agent, a.message_id); print("claimed", a.message_id); return 0
    finally:
        conn.close()
    return 1


if __name__ == "__main__":
    sys.exit(main())
