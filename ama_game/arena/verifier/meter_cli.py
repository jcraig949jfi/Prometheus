#!/usr/bin/env python3
"""Command-line front end to the metered verifier, for live seats.

A seat runs this from a shell. Session state lives in a directory the seat is
told not to touch, and the ledger is a hash chain: each entry commits to the one
before it, so an edited or deleted entry breaks verification.

That is tamper-EVIDENT, not tamper-proof. A seat with filesystem access could
rewrite the whole chain. What it cannot do is edit one entry quietly, and
`--verify` at scoring time will say so. Given that the alternative was
self-reported counts, evident beats nothing; the honest statement is in
METER_FINDINGS.md rather than a claim of security.

  python meter_cli.py open   --claim NAV-0000 --seat A0-NAV-0000
  python meter_cli.py remaining --session <id>
  python meter_cli.py evaluate  --session <id> --point 42
  python meter_cli.py sample    --session <id> --point 42
  python meter_cli.py range     --session <id> --lo 1 --hi 50
  python meter_cli.py report    --session <id>
  python meter_cli.py verify    --session <id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
sys.path.insert(0, str(HERE))

from meter import BudgetExhausted, Meter  # noqa: E402

STATE = ARENA / "a0" / "_meter_sessions"


def chain_hash(prev: str, entry: dict) -> str:
    return hashlib.sha256(
        (prev + json.dumps(entry, sort_keys=True)).encode()).hexdigest()


def save(sid: str, rec: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / f"{sid}.json").write_text(json.dumps(rec, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")


def load(sid: str) -> dict:
    p = STATE / f"{sid}.json"
    if not p.exists():
        print(json.dumps({"error": f"no session {sid}"}))
        raise SystemExit(2)
    return json.loads(p.read_text(encoding="utf-8"))


def verify_chain(rec: dict) -> tuple[bool, str]:
    h = "genesis:" + rec["claim_id"]
    for e in rec["ledger"]:
        body = {k: v for k, v in e.items() if k != "chain"}
        h = chain_hash(h, body)
        if e["chain"] != h:
            return False, f"entry {e['seq']} does not match the chain"
    if rec["head"] != h:
        return False, "head does not match the chain"
    return True, "intact"


def rebuild(rec: dict, sealed_dir: Path):
    """Rehydrate a Session and replay the ledger so spend is authoritative."""
    m = Meter(sealed_dir, budget=rec["budget"])
    sess = m.open(rec["claim_id"], rec["seat"])
    for e in rec["ledger"]:
        sess.ledger.record(e["op"], e["cost"],
                           {k: v for k, v in e.items()
                            if k not in ("seq", "op", "cost", "chain")})
    sess.refused = rec.get("refusals", 0)
    return m, sess


def commit(rec: dict, sess) -> None:
    new = []
    h = "genesis:" + rec["claim_id"]
    for e in sess.ledger.entries:
        body = dict(e)
        h = chain_hash(h, body)
        body["chain"] = h
        new.append(body)
    rec["ledger"] = new
    rec["head"] = h
    rec["spent"] = sess.ledger.spent
    rec["remaining"] = sess.remaining()
    rec["refusals"] = sess.refused


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("open", "remaining", "evaluate", "sample", "range", "symbolic",
                 "report", "verify"):
        s = sub.add_parser(name)
        s.add_argument("--session")
        s.add_argument("--claim")
        s.add_argument("--seat")
        s.add_argument("--point", type=int)
        s.add_argument("--lo", type=int)
        s.add_argument("--hi", type=int)
        s.add_argument("--relation")
        s.add_argument("--set", default=str(ARENA / "heldout" / "NAV_PILOT"))
        s.add_argument("--budget", type=int, default=120)
    a = ap.parse_args()
    sealed_dir = Path(a.set) / "sealed"

    if a.cmd == "open":
        sid = a.seat or a.claim
        m = Meter(sealed_dir, budget=a.budget)
        sess = m.open(a.claim, sid)
        rec = {"session": sid, "claim_id": a.claim, "seat": sid,
               "budget": a.budget, "binding": sess.binding, "ledger": [],
               "head": "genesis:" + a.claim, "spent": 0,
               "remaining": a.budget, "refusals": 0,
               "set": str(Path(a.set))}
        save(sid, rec)
        print(json.dumps({"session": sid, "budget": a.budget,
                          "remaining": a.budget, "binding": sess.binding,
                          "statement": m.public(a.claim)}, indent=2))
        return 0

    rec = load(a.session)
    sealed_dir = Path(rec["set"]) / "sealed"
    ok, why = verify_chain(rec)
    if not ok:
        print(json.dumps({"error": "ledger integrity failure", "detail": why}))
        return 3

    if a.cmd == "verify":
        print(json.dumps({"session": a.session, "chain": why, "spent": rec["spent"],
                          "entries": len(rec["ledger"])}, indent=2))
        return 0
    if a.cmd == "remaining":
        print(json.dumps({"remaining": rec["remaining"], "spent": rec["spent"],
                          "refusals": rec["refusals"]}))
        return 0
    if a.cmd == "report":
        print(json.dumps(rec, indent=2))
        return 0

    m, sess = rebuild(rec, sealed_dir)
    try:
        if a.cmd == "evaluate":
            out = {"point": a.point, "holds": sess.evaluate(a.point)}
        elif a.cmd == "sample":
            out = {"point": a.point, "value": sess.sample(a.point)}
        elif a.cmd == "range":
            out = sess.evaluate_range(a.lo, a.hi)
        elif a.cmd == "symbolic":
            out = {"relation": a.relation,
                   "holds": sess.symbolic_check(a.relation)}
        else:
            print(json.dumps({"error": f"unknown op {a.cmd}"}))
            return 2
    except BudgetExhausted as e:
        rec["refusals"] = rec.get("refusals", 0) + 1
        save(a.session, rec)
        print(json.dumps({"refused": True, "reason": str(e),
                          "remaining": rec["remaining"]}))
        return 0

    commit(rec, sess)

    # Shared-session detection, surfaced to the seat rather than buried. In the
    # v0.2 A0 run the launcher relaunched claims whose first seat was still
    # working, so 12 of 32 sessions were charged by two seats. The seats noticed
    # and reported it unprompted, but only by inferring it from jumps in the
    # spend. Telling them directly costs nothing and removes the guesswork.
    seen, shared = set(), False
    for e in rec["ledger"]:
        key = (e["op"], e.get("point"), e.get("lo"), e.get("hi"))
        if key in seen:
            shared = True
            break
        seen.add(key)
    if shared:
        rec["shared_session"] = True

    save(a.session, rec)
    out["remaining"] = rec["remaining"]
    out["spent"] = rec["spent"]
    if shared:
        out["shared_session_warning"] = (
            "This session's ledger contains a repeated observation, which means "
            "another seat is working the same claim. Your spend is not solely "
            "yours. Report your own call count; the harness will exclude this "
            "session from the cost analysis.")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
