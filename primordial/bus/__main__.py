"""CLI: python -m primordial.bus <command> ...

  hello                          register PM_TAG as PM_LANE's instance and announce it
  beat [STATUS]                  refresh this lane's heartbeat (TTL PM_ALIVE_TTL)
  alive                          heartbeats of every lane, with seconds left
  read [--block MS]              unseen messages for PM_LANE (registered tag only);
                                 messages addressed to you print IN FULL
  inbox                          like read, but prints only messages addressed to you
  tail [N] [--full]              last N messages, read-only (acks nothing, no lane needed)
  post KIND SUBJECT [BODY] [--to L,L|ALL] [--ref REF]
  claim EXP_ID                   first claim wins (exit 1 if taken)
  burst SECONDS NOTE             announce a CPU burst (visible to host_load until it expires)
  board [METRIC]                 list boards, or standings for one metric
  results [N]                    last N receipts (one line each)
  anomaly add SUBJECT OBSERVATION [--expected X] [--surprise X] [--discriminator X] [--source X]
  anomaly list [--status OPEN|RESOLVED|REFUTED|INDETERMINATE]
  anomaly resolve ID STATUS NOTE [--exp EXP_ID]
  anomaly seed FILE.jsonl        add records whose subject is not already queued
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from primordial.bus import bus


def _line(mid: str, f: dict, full: bool) -> str:
    body = f.get("body") or ""
    to = f" -> {f['to']}" if f.get("to") else ""
    head = f"{mid} {f.get('lane')}[{f.get('tag')}] {f.get('kind')}{to}: {f.get('subject')}"
    if body:
        head += " | " + (body if full else body[:300] + ("..." if len(body) > 300 else ""))
    if f.get("ref"):
        head += f" | ref {f['ref']}"
    return head


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="python -m primordial.bus", add_help=True)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("hello")
    b = sub.add_parser("beat"); b.add_argument("status", nargs="?", default="")
    sub.add_parser("alive")
    rd = sub.add_parser("read"); rd.add_argument("--block", type=int)
    sub.add_parser("inbox")
    t = sub.add_parser("tail"); t.add_argument("n", nargs="?", type=int, default=50); t.add_argument("--full", action="store_true")
    p = sub.add_parser("post"); p.add_argument("kind"); p.add_argument("subject"); p.add_argument("body", nargs="?", default="")
    p.add_argument("--to", default=""); p.add_argument("--ref", default="")
    c = sub.add_parser("claim"); c.add_argument("exp_id")
    bu = sub.add_parser("burst"); bu.add_argument("seconds", type=int); bu.add_argument("note")
    bo = sub.add_parser("board"); bo.add_argument("metric", nargs="?")
    rs = sub.add_parser("results"); rs.add_argument("n", nargs="?", type=int, default=20)
    an = sub.add_parser("anomaly"); asub = an.add_subparsers(dest="acmd")
    aa = asub.add_parser("add"); aa.add_argument("subject"); aa.add_argument("observation")
    for k in ("expected", "surprise", "discriminator", "source"):
        aa.add_argument(f"--{k}", default="")
    al = asub.add_parser("list"); al.add_argument("--status")
    ar = asub.add_parser("resolve"); ar.add_argument("id"); ar.add_argument("status"); ar.add_argument("note")
    ar.add_argument("--exp", default="")
    aseed = asub.add_parser("seed"); aseed.add_argument("file")
    a = ap.parse_args(argv)
    if not a.cmd:
        print(__doc__)
        return 2
    r = bus.conn()
    if a.cmd == "hello":
        bus.register(r=r)
        print(bus.post("hello", "online", r=r))
    elif a.cmd == "beat":
        bus.beat(a.status, r=r)
        print("ok")
    elif a.cmd == "alive":
        now = time.time()
        for lane, h in bus.alive(r=r).items():
            print(f"{lane} {h.get('tag')} age {now - float(h.get('ts', now)):6.0f}s ttl {h.get('ttl')}s status {h.get('status')}")
    elif a.cmd in ("read", "inbox"):
        lane, _ = bus.me()
        got = bus.read(block_ms=getattr(a, "block", None), r=r)
        others = 0
        for mid, f in got:
            mine = bus.addressed_to(f, lane)
            if a.cmd == "inbox" and not mine:
                others += 1
                continue
            print(("[TO YOU] " if mine else "") + _line(mid, f, full=mine))
        if a.cmd == "inbox" and others:
            print(f"({others} messages not addressed to {lane} were marked read; see `tail`)")
    elif a.cmd == "tail":
        for mid, f in bus.tail(a.n, r=r):
            print(_line(mid, f, full=a.full))
    elif a.cmd == "post":
        print(bus.post(a.kind, a.subject, a.body, ref=a.ref, to=a.to, r=r))
    elif a.cmd == "claim":
        ok = bus.claim(a.exp_id, r=r)
        print("CLAIMED" if ok else f"TAKEN by {r.hget(bus.CLAIMS, a.exp_id)}")
        return 0 if ok else 1
    elif a.cmd == "burst":
        bus.burst(a.seconds, a.note, r=r)
        print("ok")
    elif a.cmd == "board":
        if not a.metric:
            for k in sorted(r.scan_iter("pm:board:*")):
                print(k)
        else:
            for who, s in bus.standings(a.metric, r=r):
                print(f"{s:12.3f}  {who}")
    elif a.cmd == "results":
        for mid, f in reversed(r.xrevrange(bus.RESULTS, count=a.n)):
            d = json.loads(f["json"])
            print(f"{mid} {d['lane']} {d['exp_id']} {d['status']} :: {d['claim'][:120]}")
    elif a.cmd == "anomaly":
        if a.acmd == "add":
            print(bus.anomaly_add(a.subject, a.observation, a.expected, a.surprise, a.discriminator, a.source, r=r))
        elif a.acmd == "list":
            for aid, f, st in bus.anomaly_list(a.status, r=r):
                print(f"{aid} {st:13s} {f.get('subject')} | {f.get('observation')}"
                      + (f" | expected: {f['expected']}" if f.get("expected") else "")
                      + (f" | discriminator: {f['discriminator']}" if f.get("discriminator") else "")
                      + (f" | source: {f['source']}" if f.get("source") else ""))
        elif a.acmd == "resolve":
            bus.anomaly_resolve(a.id, a.status, a.note, a.exp, r=r)
            print("ok")
        elif a.acmd == "seed":
            print("\n".join(bus.anomaly_seed(a.file, r=r)) or "nothing new")
        else:
            print(__doc__)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
