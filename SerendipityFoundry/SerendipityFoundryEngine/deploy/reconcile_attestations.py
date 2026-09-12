"""A6 reconciler -- the SEPARATE WITNESS that turns UNKNOWN into CONFIRMED.

The engine's intent journal (sfe/attestation.py) records intent BEFORE the
ledger lock and an outcome AFTER; when the process died in between, or the
caller timed out, the journal holds an intent with no outcome and the verdict
is UNKNOWN. This tool is the independent reader the vocabulary requires: it
looks the intent up IN THE LEDGER and only then says CONFIRMED_EFFECT or
CONFIRMED_NO_EFFECT.

What it can and cannot settle, stated rather than blurred:
  * an intent WITH an Idempotency-Key: the ledger's idempotency_keys table is
    the effect's own receipt (the row is written in the same transaction as
    the effect, runtime.py). Present -> CONFIRMED_EFFECT; absent after the
    engine's busy window -> CONFIRMED_NO_EFFECT.
  * an intent WITHOUT a key: UNKNOWN_UNRECONCILABLE. There is nothing to look
    up. That is the truthful answer, and the reason consumers should send
    keys (backlog A2).
  * a key used by more than one client: UNKNOWN_UNRECONCILABLE, ambiguous.

Read-only on the ledger. Writes its verdicts to <incidents>/reconciled.jsonl
(a separate file from the journal, which stays append-only and engine-owned).

    python deploy/reconcile_attestations.py --incidents <dir> --db <ledger> [--older-than 120]
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time

_ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)
from sfe.attestation import Journal  # noqa: E402


def open_intents_on_disk(directory, older_than_s):
    """All intents with no outcome line across every journal file (cold scan;
    the engine's in-memory view dies with its process, which is the case this
    tool exists for)."""
    slots = {}
    try:
        names = sorted(n for n in os.listdir(directory) if n.endswith(".jsonl"))
    except OSError:
        return []
    for n in names:
        with open(os.path.join(directory, n), encoding="ascii") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                s = slots.setdefault(rec.get("rid"), {})
                s["intent" if rec.get("kind") == "intent" else "outcome"] = rec
    cutoff = time.time() - older_than_s
    return [s["intent"] for s in slots.values() if "intent" in s and "outcome" not in s and s["intent"]["ts"] <= cutoff]


def ledger_has_effect(db, idem_key):
    """True / False / None(ambiguous or no key)."""
    if not idem_key:
        return None
    c = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True, timeout=10)
    try:
        n = c.execute("SELECT COUNT(DISTINCT client_id) FROM idempotency_keys WHERE idem_key=?", (idem_key,)).fetchone()[0]
    finally:
        c.close()
    if n == 0:
        return False
    if n == 1:
        return True
    return None


def reconcile(incidents_dir, db, *, older_than_s=120.0, now=None):
    j = Journal(incidents_dir)
    out = []
    for intent in open_intents_on_disk(incidents_dir, older_than_s):
        key = intent.get("idem_key")
        has = ledger_has_effect(db, key)
        v = j.attest(intent["rid"], ledger_has_effect=has)
        if key and has is None:
            # the witness LOOKED and the key is used by more than one client:
            # not reconcilable by this key, and saying so beats "still open"
            v["state"] = "UNKNOWN_UNRECONCILABLE"
            v["why"] = "idempotency key %r is held by more than one client; ambiguous" % key
        v["reconciled_at"] = now or time.time()
        v["witness"] = "deploy/reconcile_attestations.py: idempotency_keys lookup"
        out.append(v)
    if out:
        with open(os.path.join(incidents_dir, "reconciled.jsonl"), "a", encoding="ascii") as fh:
            for v in out:
                fh.write(json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--incidents", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--older-than", type=float, default=120.0,
                    help="seconds; younger intents may still be in flight (engine busy window is 30 s)")
    a = ap.parse_args(argv)
    out = reconcile(a.incidents, a.db, older_than_s=a.older_than)
    by = {}
    for v in out:
        by[v["state"]] = by.get(v["state"], 0) + 1
    print(json.dumps({"reconciled": len(out), "by_state": by}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
