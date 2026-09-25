"""File CW01-D051 and close the tally drift it names - in that order, with proof.

D049 was raised when a hand-maintained defect tally drifted from DEFECTS.jsonl and
put a false headline into PACKAGE.md. I fixed it by DERIVING the tally at write time.
That was structurally wrong. A derivation performed once holds only until the next
append: repair_state_encoding.py appended CW01-D050 without re-deriving, and the
state went stale within minutes - ledger 51, state 50; e05 derived 15, recorded 14.

The invariant needs ENFORCING, not establishing. lib/recordsafety.check_tally is that
enforcement.

ORDER MATTERS HERE, and it is the point of the script:

  1. PROVE the gate on planted fixtures - it must refuse a drifted pair and admit a
     consistent one. If it cannot be shown to fire, nothing is filed and nothing is
     claimed.
  2. Only then append D051 as FIXED. Marking a defect FIXED before the fix is
     demonstrated is the mistake made with D048, and this is the third time in one
     session that a premature claim would have been easy to make.
  3. Re-derive the live tally from the ledger.
  4. VERIFY the live pair now passes the gate, and say so from the check's own output
     rather than from expectation.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
STATE = BASE / "CAMPAIGN_STATE.json"
LEDGER = BASE / "DEFECTS.jsonl"
sys.path.insert(0, str(BASE / "lib"))

import recordsafety as RS          # noqa: E402

TITLE = "derived tally fix was one-shot; drift recurred on the next ledger append"


def prove_gate():
    """Step 1: the gate must be OBSERVED refusing before anything is claimed."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    led = tmp / "L.jsonl"
    led.write_text("".join(json.dumps({"id": "X%d" % i, "experiment_id": "cw01-e01"}) + "\n"
                           for i in range(3)), encoding="utf-8")

    def state(total, per):
        s = tmp / ("S%d.json" % total)
        s.write_text(json.dumps({"campaign_totals": {"defects_logged": total,
                                                     "defects_per_experiment": per}}),
                     encoding="utf-8")
        return s

    refuses = RS.check_tally(state(2, {"e01": 2}), led)["outcome"] == "FAIL"
    admits = RS.check_tally(state(3, {"e01": 3}), led)["outcome"] == "PASS"
    fails_closed = False
    try:
        RS.require_tally_consistent(state(2, {"e01": 2}), led)
    except RS.TallyDrift:
        fails_closed = True
    print("1. gate proof   : refuses_drift=%s admits_consistent=%s fails_closed=%s"
          % (refuses, admits, fails_closed))
    return refuses and admits and fails_closed


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if not prove_gate():
        print("   gate could not be shown to fire; filing nothing and changing nothing.")
        return 1

    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    before = RS.check_tally(STATE, LEDGER)
    print("2. drift before : %s -> %s" % (before["outcome"], before["reason"][:88]))

    if not any(d.get("title") == TITLE for d in entries):
        n = max(int(m.group(1)) for m in
                (re.match(r"CW01-D(\d+)", str(d.get("id", ""))) for d in entries) if m)
        rec = {
            "id": "CW01-D%03d" % (n + 1), "ts": now, "campaign_id": "cw01-2026-09-17",
            "experiment_id": "cw01-e05", "phase": "PACKAGE",
            "severity": "medium", "category": "bookkeeping", "status": "FIXED",
            "title": TITLE,
            "evidence": "CW01-D049 was closed by DERIVING defects_logged and defects_per_experiment "
                        "from DEFECTS.jsonl at write time. repair_state_encoding.py then appended "
                        "CW01-D050 without re-deriving, and the state was immediately stale again: "
                        "ledger 51 vs recorded 50, e05 derived 15 vs recorded 14. A derivation "
                        "performed ONCE cannot hold an invariant across later writes. This is the "
                        "second time in one session I repaired an instance where an enforceable check "
                        "was required - the first being CW01-D044's self-invalidating verifier.",
            "proposed_fix": "lib/recordsafety.check_tally / require_tally_consistent added as a "
                            "standing gate asserting defects_logged == len(ledger) AND "
                            "defects_per_experiment == counts derived from the ledger, evaluated at "
                            "check time rather than at write time. Proven by an adversarial fixture "
                            "that plants a drifted pair and requires refusal, with a consistent pair "
                            "as positive control. Any closeout that appends to the ledger must "
                            "re-derive; the gate catches it when one forgets.",
            "found_by": "post-PACKAGE reconcile census before opening cw01-e06",
        }
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
        print("3. filed        : %s (%s)" % (rec["id"], rec["status"]))
    else:
        print("3. filed        : already present")

    truth = RS.derive_tally(LEDGER)
    st = json.loads(STATE.read_text(encoding="utf-8"))
    st["campaign_totals"]["defects_logged"] = truth["total"]
    st["campaign_totals"]["defects_per_experiment"] = truth["per_experiment"]
    st["campaign_totals"]["_tally_provenance"] = (
        "DERIVED from DEFECTS.jsonl at write time AND enforced at check time by "
        "lib/recordsafety.check_tally (CW01-D049 raised it, CW01-D051 showed that deriving once "
        "is not enough - the next append re-introduces drift).")
    st["updated_local"] = now
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")
    print("4. re-derived   : total=%d per_experiment=%s" % (truth["total"], truth["per_experiment"]))

    after = RS.check_tally(STATE, LEDGER)
    port = RS.check_records([STATE, LEDGER])
    print("5. gate after   : tally=%s (%s)" % (after["outcome"], after["reason"][:60]))
    print("   portability  : %s (%s)" % (port["verdict"], "pass %d fail %d nv %d"
                                         % (port["n_pass"], port["n_fail"], port["n_not_verified"])))
    return 0 if (after["outcome"] == "PASS" and port["safe"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
