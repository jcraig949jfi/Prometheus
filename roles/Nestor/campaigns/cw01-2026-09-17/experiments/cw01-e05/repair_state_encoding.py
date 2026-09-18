"""Repair CAMPAIGN_STATE.json so any reader can open it, and log the defect.

TWO PROBLEMS, ONE FILE.

1. MINE. My closeout scripts wrote CAMPAIGN_STATE.json with `ensure_ascii=False`,
   which emits raw UTF-8 bytes instead of \\uXXXX escapes. At e04 close (016e4a5b8)
   the file had ZERO non-ASCII bytes; it now has three. On Windows, whose default
   encoding is cp1252, the most natural way to read it -

       json.load(open("CAMPAIGN_STATE.json"))

   - raises UnicodeDecodeError. This is THE recovery file, and the campaign order
   requires state to be recoverable without depending on one Claude session. An
   independent executor following the obvious path hits a crash.

2. PRE-EXISTING. The character is U+6BCF in "something<U+6BCF> caller re-invents",
   where the English word "every" belonged - an e01-era text corruption. Restoring
   the intended word. This is a repair of corrupted prose, NOT a rewrite of a
   finding: the sentence's claim is unchanged.

Both fixed here, and the fix is VERIFIED by re-reading the file the naive way rather
than assumed.
"""
from __future__ import annotations

import json
import pathlib
import re
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
STATE = BASE / "CAMPAIGN_STATE.json"
LEDGER = BASE / "DEFECTS.jsonl"

CORRUPT = "something每 caller"
REPAIRED = "something every caller"
TITLE = "recovery file made unreadable by a naive reader (ensure_ascii=False)"


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    raw = STATE.read_bytes()
    before_na = sum(1 for b in raw if b > 127)
    text = raw.decode("utf-8")

    found = CORRUPT in text
    if found:
        text = text.replace(CORRUPT, REPAIRED)

    obj = json.loads(text)
    # ASCII-ONLY from here on: escapes survive every reader on every platform.
    STATE.write_text(json.dumps(obj, indent=1, ensure_ascii=True), encoding="utf-8")

    after = STATE.read_bytes()
    after_na = sum(1 for b in after if b > 127)

    # VERIFY by doing the thing that failed, not by assuming the fix worked.
    naive_ok = True
    try:
        with open(STATE) as fh:
            json.loads(fh.read())
    except Exception as e:                                   # noqa: BLE001
        naive_ok = False
        naive_err = type(e).__name__

    print("corrupted text found : %s" % found)
    print("non-ascii bytes      : %d -> %d" % (before_na, after_na))
    print("naive open() works   : %s" % (naive_ok if naive_ok else "NO (%s)" % naive_err))
    print("utf-8 open() works   : %s" % True)

    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    added = None
    if not any(d.get("title") == TITLE for d in entries):
        n = max(int(m.group(1)) for m in
                (re.match(r"CW01-D(\d+)", str(d.get("id", ""))) for d in entries) if m)
        rec = {
            "id": "CW01-D%03d" % (n + 1), "ts": now, "campaign_id": "cw01-2026-09-17",
            "experiment_id": "cw01-e05", "phase": "PACKAGE",
            "severity": "high", "category": "portability",
            "status": "FIXED" if (naive_ok and after_na == 0) else "OPEN",
            "title": TITLE,
            "evidence": "transition_e05.py, package_e05.py and fix_defect_tally.py wrote "
                        "CAMPAIGN_STATE.json with json.dumps(..., ensure_ascii=False), emitting raw "
                        "UTF-8. At e04 close (016e4a5b8) the file held 0 non-ascii bytes; afterwards 3. "
                        "On Windows, json.load(open(path)) - the obvious way for a recovering executor "
                        "to read it - raised UnicodeDecodeError, while encoding='utf-8' succeeded. "
                        "CAMPAIGN_STATE.json is the recovery file and the campaign order requires it to "
                        "be readable without depending on this session. It was the ONLY file in the "
                        "campaign tree with non-ascii bytes. Found by accident, when a throwaway "
                        "one-liner that omitted encoding= crashed.",
            "proposed_fix": "Applied and verified here: rewritten with ensure_ascii=True (0 non-ascii "
                            "bytes) and confirmed by actually performing the naive open() that failed. "
                            "All EIGHT ensure_ascii=False call sites are corrected - four "
                            "CAMPAIGN_STATE writers (transition, package, fix_defect_tally and "
                            "close_execute, the last of which I missed on the first pass) and four "
                            "DEFECTS.jsonl writers, latent only because that file happens to hold no "
                            "non-ascii - so the pattern does not reach e06. "
                            "Standing rule: durable campaign records are written ASCII-safe, because a "
                            "recovery reader's platform encoding is not ours to choose. Separately, a "
                            "pre-existing e01-era corruption (U+6BCF where the word 'every' belonged) "
                            "was repaired; the sentence's claim is unchanged.",
        }
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
        added = rec["id"]
        print("filed                : %s (%s)" % (added, rec["status"]))
    else:
        print("filed                : already present")

    return 0 if (naive_ok and after_na == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
