"""Derive the per-experiment defect tally from the ledger, and log the drift.

CAMPAIGN_STATE.json carried defects_per_experiment as a HAND-MAINTAINED count. It
drifted: it recorded e01=8 and e02=12 while DEFECTS.jsonl contains 17 and 11, and the
recorded tallies summed to 41 against a 49-entry ledger. The stale numbers were then
copied into PACKAGE.md, where they produced a false headline - that e05 was the
campaign high, when e01 is.

The fix is not to correct the numbers. It is to stop maintaining a derived quantity
by hand next to the source it is derived from.

This script applies the fix and files the defect in the SAME run, so the ledger entry
is never marked FIXED before the fix exists - which is the mistake made with D048.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
STATE = BASE / "CAMPAIGN_STATE.json"
LEDGER = BASE / "DEFECTS.jsonl"

TITLE = "hand-maintained defect tally drifted from the ledger into a package headline"


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    derived = collections.Counter(d.get("experiment_id") for d in entries)

    st = json.loads(STATE.read_text(encoding="utf-8"))
    before = dict(st["campaign_totals"].get("defects_per_experiment", {}))

    tally = {}
    for e in st["experiments"]:
        short = e["id"].replace("cw01-", "")
        n = derived.get(e["id"], 0)
        if n:
            tally[short] = n
    st["campaign_totals"]["defects_per_experiment"] = tally
    st["campaign_totals"]["defects_logged"] = len(entries)
    st["campaign_totals"]["_tally_provenance"] = (
        "DERIVED from DEFECTS.jsonl by experiment_id, not maintained by hand. A hand tally "
        "drifted (e01 recorded 8 vs 17 actual, e02 12 vs 11) and propagated a false headline "
        "into PACKAGE.md. See CW01-D049.")
    st["updated_local"] = now

    # --- file the defect in the same run as the fix -----------------------
    added = None
    if not any(d.get("title") == TITLE for d in entries):
        n = max(int(m.group(1)) for m in
                (re.match(r"CW01-D(\d+)", str(d.get("id", ""))) for d in entries) if m)
        rec = {
            "id": "CW01-D%03d" % (n + 1), "ts": now, "campaign_id": "cw01-2026-09-17",
            "experiment_id": "cw01-e05", "phase": "PACKAGE",
            "severity": "medium", "category": "bookkeeping", "status": "FIXED",
            "title": TITLE,
            "evidence": "CAMPAIGN_STATE.campaign_totals.defects_per_experiment was maintained by hand "
                        "and recorded e01=8, e02=12 while DEFECTS.jsonl contains 17 and 11 for those "
                        "experiments; the recorded tallies summed to 41 against a 49-entry ledger. The "
                        "stale figures were copied into PACKAGE.md's defect cost curve, producing the "
                        "false headline that e05 (13) was the campaign high when e01 (17) is. Caught by "
                        "a pre-commit check comparing the document's figures against the primary source, "
                        "before the document was committed.",
            "proposed_fix": "Applied in this same change: defects_per_experiment is now DERIVED from "
                            "DEFECTS.jsonl by experiment_id at write time, and carries a "
                            "_tally_provenance note. Never maintain a derived quantity by hand beside "
                            "its source. Related lesson: a raw defect count is a poor cross-experiment "
                            "instrument anyway - 5 of e05's 13 exist only because an independent lane "
                            "looked, so the count partly measures scrutiny, not quality.",
        }
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")   # CW01-D050
        added = rec["id"]
        st["campaign_totals"]["defects_logged"] = len(entries) + 1
        st["campaign_totals"]["defects_per_experiment"]["e05"] = derived.get("cw01-e05", 0) + 1

    # ASCII-safe: a recovery reader's default platform encoding is not ours to choose
    # (CW01-D050 - ensure_ascii=False made this file crash a naive open() on Windows).
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")

    back = json.loads(STATE.read_text(encoding="utf-8"))
    t = back["campaign_totals"]
    print("before (hand-maintained): %s  sum=%d" % (before, sum(before.values())))
    print("after  (derived)        : %s  sum=%d" % (t["defects_per_experiment"],
                                                    sum(t["defects_per_experiment"].values())))
    print("defects_logged          : %d" % t["defects_logged"])
    print("filed                   : %s" % (added or "already present"))
    print("reconciles              : %s" % (sum(t["defects_per_experiment"].values()) == t["defects_logged"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
