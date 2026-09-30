"""Relabel the recipe axis of records that never had a recipe to scan (TECHNE-126, 2026-09-30).

harvest.preservation_of() wrote recipe_status = "NO_NETWORK_FETCH_DETECTED" whenever the network
pattern did not match recipe.json -- including when there was NO recipe.json, where the scan could
not have fired. Measured 2026-09-30 on origin/main e571efec0 plus the new dcd record: of the 52
records carrying a recipe_status (51 tracked + dcd), 48 (47 tracked + dcd) had no recipe.json. The instrument now reports
"NO_RECIPE" for that case (harvest.RECIPE_STATES, harvest.recipe_status_of); this script brings the
already-stored records into line so a stored label and a recomputed label agree.

What this does, and only this:
  - for every techne/fossils/specimens/*/record.json whose preservation.recipe_status is
    "NO_NETWORK_FETCH_DETECTED" AND that has no recipe.json beside it, the ONE line
        "recipe_status": "NO_NETWORK_FETCH_DETECTED"
    becomes
        "recipe_status": "NO_RECIPE"
    by a byte-level replacement. No other byte changes; the file is never re-serialised; line
    endings are whatever they were.
  - refuses (status AMBIGUOUS, file left alone) unless the old text occurs EXACTLY ONCE in the file
    and the parsed document after replacement differs from the parsed document before ONLY in
    preservation.recipe_status.
  - a record that HAS a recipe.json keeps NO_NETWORK_FETCH_DETECTED: there the scan ran (status
    HAS_RECIPE_KEPT). preservation.status, body_status, checked_utc and every other field are not
    touched: this is a relabel of what the old check could say, not a re-run of the check.
  - a receipt (path, sha256 before/after over LF-normalised bytes = the git blob, old and new value)
    goes to techne/fossils/RECIPE_STATUS_MIGRATION_2026-09-30.json unless --dry-run. The old value
    stays readable there and in git history; it is superseded, not erased.
  - idempotent: a second run finds nothing to relabel and rewrites nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

from . import vault

OLD = "NO_NETWORK_FETCH_DETECTED"
NEW = "NO_RECIPE"
OLD_TEXT = b'"recipe_status": "NO_NETWORK_FETCH_DETECTED"'
NEW_TEXT = b'"recipe_status": "NO_RECIPE"'
RECEIPT = vault.REPO / "techne" / "fossils" / "RECIPE_STATUS_MIGRATION_2026-09-30.json"


def _sha_lf(b: bytes) -> str:
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def relabel_bytes(raw: bytes):
    """(new_bytes, status). status in RELABELED / NOT_APPLICABLE / AMBIGUOUS. Pure; no I/O."""
    try:
        before = json.loads(raw.decode("utf-8"))
    except ValueError:
        return raw, "AMBIGUOUS"
    pres = before.get("preservation")
    if not isinstance(pres, dict) or pres.get("recipe_status") != OLD:
        return raw, "NOT_APPLICABLE"
    if raw.count(OLD_TEXT) != 1:
        return raw, "AMBIGUOUS"
    new = raw.replace(OLD_TEXT, NEW_TEXT)
    after = json.loads(new.decode("utf-8"))
    expect = json.loads(raw.decode("utf-8"))
    expect["preservation"]["recipe_status"] = NEW
    if after != expect:
        return raw, "AMBIGUOUS"
    return new, "RELABELED"


def migrate_file(rec_path: pathlib.Path, write: bool) -> dict:
    try:
        rel = rec_path.relative_to(vault.REPO).as_posix()
    except ValueError:
        rel = str(rec_path)
    raw = rec_path.read_bytes()
    row = {"path": rel, "sha256_lf_before": _sha_lf(raw), "status": None}
    if (rec_path.parent / "recipe.json").exists():
        try:
            rs = (json.loads(raw.decode("utf-8")).get("preservation") or {}).get("recipe_status")
        except ValueError:
            rs = None
        row["status"] = "HAS_RECIPE_KEPT" if rs == OLD else "NOT_APPLICABLE"
        return row
    new, status = relabel_bytes(raw)
    row["status"] = status
    if status == "RELABELED":
        row["old"] = OLD
        row["new"] = NEW
        row["sha256_lf_after"] = _sha_lf(new)
        if write:
            rec_path.write_bytes(new)
        else:
            row["status"] = "WOULD_RELABEL"
    return row


def migrate(specimens: pathlib.Path, write: bool) -> dict:
    rows = [migrate_file(d / "record.json", write)
            for d in sorted(specimens.iterdir()) if d.is_dir() and (d / "record.json").exists()]
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    return {"schema": "techne.fossil.recipe_status_migration/1",
            "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "old": OLD, "new": NEW, "write": write, "records_scanned": len(rows), "by_status": by,
            "hash_rule": "sha256 over LF-normalised bytes (equals the git blob content hash input)",
            "files": [r for r in rows if r["status"] != "NOT_APPLICABLE"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--specimens", default=None, help="specimens directory (default: the tracked one)")
    a = ap.parse_args()
    specimens = pathlib.Path(a.specimens) if a.specimens else vault.specimen_dir("_").parent
    doc = migrate(specimens, write=not a.dry_run)
    print(json.dumps({k: v for k, v in doc.items() if k != "files"}, indent=1))
    if not a.dry_run and a.specimens is None:
        if doc["by_status"].get("RELABELED", 0) > 0:
            RECEIPT.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
            print("receipt", RECEIPT)
        else:
            # an idempotent second run must not overwrite the receipt of the run that did the work
            print("nothing relabeled; receipt left as it is")


if __name__ == "__main__":
    main()
