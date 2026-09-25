"""Pre-post check for program comms (Selective Irreversibility stewards).

Refuses a post when any recipient is on DO_NOT_BRIEF.txt, or when the recipient
is "*" (broadcast), whatever the body says: program posts go to named seats only.
Also reports STRONG probe terms in the body, so an operational message to a
listed seat can be seen to be clean. Exit 0 = clear to post, 2 = REFUSED.

usage: python prepost_check.py --to Seat1,Seat2 --body-file <path> [--program]
  --program  the post is program content (default). Without it (an operational
             note), a listed recipient is allowed ONLY if the body has no STRONG
             term and does not contain "blind" or "programs/selective".
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIST = os.path.join(HERE, "..", "DO_NOT_BRIEF.txt")
STRONG = ["selective irreversib", "selective-irreversib", "selective_irreversib",
          "2026-09-23-selective-irreversibility", "accessible causal state", "relevance-selective"]
EXTRA = ["blind", "programs/selective"]


def listed():
    out = {}
    for line in open(LIST, encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            seat = line.split("|")[0].strip()
            out[seat.lower()] = line.strip()
    return out


def check(recipients, body, program=True):
    """Return (ok, reasons)."""
    reasons = []
    dnb = listed()
    low = body.lower()
    strong = [t for t in STRONG if t in low]
    extra = [t for t in EXTRA if t in low]
    for r in recipients:
        r0 = r.strip()
        if r0 == "*":
            reasons.append("broadcast '*' reaches DO_NOT_BRIEF seats; name recipients")
        elif r0.lower() in dnb:
            if program:
                reasons.append(f"{r0} is DO_NOT_BRIEF ({dnb[r0.lower()]}); program post refused")
            elif strong or extra:
                reasons.append(f"{r0} is DO_NOT_BRIEF and the body contains {strong + extra}")
    return (not reasons), reasons


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--operational", action="store_true", help="not program content")
    a = ap.parse_args()
    body = open(a.body_file, encoding="utf-8").read()
    ok, why = check(a.to.split(","), body, program=not a.operational)
    for w in why:
        print("REFUSED:", w)
    print("CLEAR" if ok else "DO NOT POST")
    sys.exit(0 if ok else 2)
