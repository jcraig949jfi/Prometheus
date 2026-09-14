"""One-time backfill of pin evidence destroyed by the batch scripts (batch 10 P1).

PREREG: techne/fossils/PREREG_PIN_EVIDENCE_2026-09-13.md

acquire() wrote each resolved pin to BOTH source_origin (the request) and hashes.artifacts (the
receipt). Re-running a batch script rebuilt source_origin from a literal and destroyed the request
half, leaving 21 git artifacts pointing at a moving "HEAD" and 239 url artifacts with no digest --
while the receipt still held the truth. record.merge_artifact_pins now prevents the loss going
forward; this restores what was already lost.

    python -m techne.fossils.backfill_pins [--apply]

Without --apply it reports what it would change and writes nothing. It only ever ADDS a fixed
identifier that the record itself already proves; it never invents one and never overwrites a pin
that is already established.
"""
from __future__ import annotations

import argparse
import json
import time

from . import record, vault


def audit() -> dict:
    rows = []
    sp = vault.specimen_dir("_").parent
    for d in sorted(sp.iterdir()):
        if not (d / "record.json").exists():
            continue
        rec = record.load(d.name)
        hashes = (rec.get("hashes") or {}).get("artifacts") or []
        for a in (rec.get("source_origin") or {}).get("artifacts") or []:
            own = record.established_pin(a)
            recv = record.established_pin(a, hashes)
            if own:
                continue
            rows.append({"specimen_id": d.name, "kind": a.get("kind"),
                         "ref": a.get("url") if a.get("kind") == "git" else a.get("filename"),
                         "request_says": a.get("commit") if a.get("kind") == "git" else None,
                         "recoverable": bool(recv), "pin": recv[:12]})
    return {"n_unpinned_in_request": len(rows),
            "recoverable_from_receipt": sum(1 for r in rows if r["recoverable"]),
            "not_recoverable": sum(1 for r in rows if not r["recoverable"]),
            "rows": rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    before = audit()
    restored_total, touched = 0, []
    if a.apply:
        sp = vault.specimen_dir("_").parent
        for d in sorted(sp.iterdir()):
            if not (d / "record.json").exists():
                continue
            rec = record.load(d.name)
            # merging the record with ITSELF carries the receipt onto the request
            n = record.merge_artifact_pins(rec, rec)
            if n:
                record.save(rec)
                restored_total += n
                touched.append({"specimen_id": d.name, "pins_restored": n})
    after = audit()

    doc = {"schema": "techne.fossil.pin_backfill/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "prereg": "techne/fossils/PREREG_PIN_EVIDENCE_2026-09-13.md",
           "applied": bool(a.apply), "pins_restored": restored_total, "specimens_touched": touched,
           "before": {k: before[k] for k in ("n_unpinned_in_request", "recoverable_from_receipt", "not_recoverable")},
           "after": {k: after[k] for k in ("n_unpinned_in_request", "recoverable_from_receipt", "not_recoverable")},
           "note": "only fixed identifiers the record itself already proves are written; nothing is invented."}
    if a.out:
        __import__("pathlib").Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: doc[k] for k in ("applied", "pins_restored", "before", "after")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
