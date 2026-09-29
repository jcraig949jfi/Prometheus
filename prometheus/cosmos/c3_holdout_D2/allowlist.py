"""Custodian ANCHOR for the D2 protocol records (v12; MWO-0004 D2-1 resolves #925).

    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py allowlist add --role AUDIT|COMMITMENT|DESIGNATION|RESULT_SEAL \
        --record <file name in protocol/>
    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py allowlist show

Root of trust (MWO-0004 D2-1): published Git object identity + immutable blob hashes + an append-only
out-of-repository anchor on M1. There is no comms-sender check any more; comms is notification only.

`add` confirms one protocol record. It reads the record from refs/remotes/origin/main, finds the ONE commit that added it
(protocol._added_once: one blob in full history, one non-merge add), and APPENDS to the anchor:
    role, record, repository path, blob sha256 (LF), adding commit, anchored_utc,
    prev = the previous entry's entry_hash, entry_hash = sha256 of this entry's canonical body.
It never rewrites the file. Anchoring the same role/record again with a DIFFERENT blob is refused (once only).
Before every gated step protocol.check_gates and entry.py re-verify each record against its anchor entry:
the commit exists, is an ancestor of the fetched origin/main, still holds the anchored blob, and is the adding commit.
The anchor holds identifiers and hashes only: no sealed content.

Runs ONLY through entry.py (governing PASS audit binding, or the custodian-pinned pre-audit binding).
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

from prometheus.cosmos.c3_holdout_D2 import protocol

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROTO_REL = "prometheus/cosmos/c3_holdout_D2/protocol"
ALLOWLIST = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/ANCHOR.jsonl")
ROLES = ("AUDIT", "COMMITMENT", "DESIGNATION", "RESULT_SEAL", "KEY_RELEASED", "REVEALED")   # v13: once-only records too
ERR = {"AUDIT": protocol.AuditMissing, "COMMITMENT": protocol.CommitmentMissing,
       "DESIGNATION": protocol.DesignationMissing, "RESULT_SEAL": protocol.ResultNotSealed,
       "KEY_RELEASED": protocol.GateRefusal, "REVEALED": protocol.GateRefusal}


def record_bytes(ref, name):
    b = protocol._show(REPO, ref, "%s/%s" % (PROTO_REL, name))
    if b is None:
        raise SystemExit("REFUSED: %s/%s is not committed on %s" % (PROTO_REL, name, ref))
    return b


def load(path):
    return protocol.anchor_entries(path)


def add(role, name, ref=protocol.DEFAULT_REF, path=ALLOWLIST, expect_commit=None, expect_sha256=None) -> dict:
    if role not in ROLES:
        raise SystemExit("REFUSED: unknown role %r" % role)
    ref_c = protocol.resolve_ref(REPO, ref)
    b = record_bytes(ref_c, name)
    h = protocol.record_sha(b)
    rel = "%s/%s" % (PROTO_REL, name)
    try:
        c = protocol._added_once(REPO, ref_c, rel, ERR[role])
    except protocol.GateRefusal as e:
        raise SystemExit("REFUSED: %s: %s" % (type(e).__name__, e))
    # v13 (Odysseus v12 V12-4): the custodian states what the author published; anything else is refused
    if expect_commit is not None and c != expect_commit:
        raise SystemExit("REFUSED: %s was added by %s, not the expected %s" % (name, c[:12], str(expect_commit)[:12]))
    if expect_sha256 is not None and h != str(expect_sha256).lower():
        raise SystemExit("REFUSED: %s has sha256 %s..., not the expected %s..." % (name, h[:12], str(expect_sha256)[:12]))
    prior = [e for e in load(path) if e.get("role") == role and e.get("record") == name]
    if any(e.get("sha256") != h for e in prior):
        raise SystemExit("REFUSED: %s/%s is already anchored with a different blob (once only)" % (role, name))
    if prior:
        return prior[0]
    return protocol.anchor_append(path, {"role": role, "record": name, "path": rel, "sha256": h, "commit": c,
                                         "anchored_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("add", "show"))
    ap.add_argument("--role")
    ap.add_argument("--record")
    ap.add_argument("--expect-commit", help="add: the commit the author published (required)")
    ap.add_argument("--expect-sha256", help="add: the record's LF sha256 the author published (required)")
    a = ap.parse_args(argv)
    if not str(os.environ.get("C3D2_ENTRY", "")).startswith("verified"):
        print(json.dumps({"refused": True, "reason": "start allowlist through entry.py (v5 B-2)"}))
        return 3
    if a.cmd == "show":
        print(json.dumps(load(ALLOWLIST), indent=1))
        return 0
    if not (a.role and a.record and a.expect_commit and a.expect_sha256):
        print(json.dumps({"refused": True, "reason": "add needs --role, --record, --expect-commit and --expect-sha256"}))
        return 3
    e = add(a.role, a.record, expect_commit=a.expect_commit, expect_sha256=a.expect_sha256)
    print(json.dumps({"anchored": a.record, "role": a.role, "sha256": e["sha256"], "commit": e["commit"],
                      "entry_hash": e["entry_hash"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
