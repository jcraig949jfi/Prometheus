"""CLI: python -m primordial.bus <hello|read|post|claim|board|who> ...

  hello                       announce this lane/instance on the bus
  read [--block MS]           print unseen swarm messages for PM_LANE
  post KIND SUBJECT [BODY]    kinds: hello claim contract ask result kill note
  claim EXP_ID                first claim wins (exit 1 if taken)
  board [METRIC]              list boards, or standings for one metric
  results [N]                 last N receipts (one line each)
"""
from __future__ import annotations

import json
import sys

from primordial.bus import bus


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    r = bus.conn()
    if cmd == "hello":
        print(bus.post("hello", "online", r=r))
    elif cmd == "read":
        block = int(args[1]) if args[:1] == ["--block"] else None
        for mid, f in bus.read(block_ms=block, r=r):
            print(f"{mid} {f.get('lane')}[{f.get('tag')}] {f.get('kind')}: {f.get('subject')}"
                  + (f" | {f['body'][:300]}" if f.get("body") else "")
                  + (f" | ref {f['ref']}" if f.get("ref") else ""))
    elif cmd == "post":
        print(bus.post(args[0], args[1], args[2] if len(args) > 2 else "", r=r))
    elif cmd == "claim":
        ok = bus.claim(args[0], r=r)
        print("CLAIMED" if ok else f"TAKEN by {r.hget(bus.CLAIMS, args[0])}")
        return 0 if ok else 1
    elif cmd == "board":
        if not args:
            for k in sorted(r.scan_iter("pm:board:*")):
                print(k)
        else:
            for who, s in bus.standings(args[0], r=r):
                print(f"{s:12.3f}  {who}")
    elif cmd == "results":
        n = int(args[0]) if args else 20
        for mid, f in reversed(r.xrevrange(bus.RESULTS, count=n)):
            d = json.loads(f["json"])
            print(f"{mid} {d['lane']} {d['exp_id']} {d['status']} :: {d['claim'][:120]}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
