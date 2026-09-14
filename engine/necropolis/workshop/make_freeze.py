"""Write a FREEZE record for the workshop's reported state (schema necropolis.workshop.freeze/1).

    python engine/necropolis/workshop/make_freeze.py --date 2026-09-14 --reported-in <receipt path> --tag <tag> [--commit <sha>]

A freeze record is the reported state at a named commit; validate_workshop.py re-reads
every hash on every run (MATCH / DRIFT).  A later regeneration never rewrites an old
record: run this again with a new date.  Refuses to overwrite an existing record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ["TOOLS.jsonl", "tests/controls_result.json", "CORONER_RUN.md", "coroner_plans/DISPOSITIONS.jsonl",
         "FRANKENSTEIN_XREF.json", "CANDIDATE_INDEX.jsonl", "FORENSIC_QUESTIONS.json", "TOOL_SCHEMA.json"]


def sha_lf(p: Path):
    b = p.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest(), len(b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--reported-in", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--commit", default=None, help="reported commit; default = current HEAD (short)")
    a = ap.parse_args()
    out = HERE / f"FREEZE_{a.date}.json"
    if out.exists():
        print(f"refusing to overwrite {out.name}; a freeze record is immutable, pick a new date"); return 2
    files = {}
    for rel in FILES + sorted(str(p.relative_to(HERE)).replace("\\", "/") for p in (HERE / "coroner_plans").glob("CR-*.json")):
        p = HERE / rel
        if not p.exists():
            print("missing", rel); return 2
        h, n = sha_lf(p); files[rel] = {"sha256_lf": h, "bytes_lf": n}
    rows = [json.loads(l) for l in (HERE / "TOOLS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ctrl = json.loads((HERE / "tests" / "controls_result.json").read_text(encoding="utf-8"))
    head = a.commit or subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, capture_output=True, text=True).stdout.strip()
    adm = Counter(r["admissibility"]["admissible_as"] for r in rows)
    rec = {"schema": "necropolis.workshop.freeze/1", "frozen_at": a.date, "reported_in": a.reported_in, "reported_commit": head, "tag": a.tag,
           "status_counts": dict(Counter(r["necropolis_status"] for r in rows)), "admissibility_counts": dict(adm), "rows": len(rows),
           "controls": {"git_head": ctrl.get("git_head"), "counts": ctrl.get("counts"), "cases": len(ctrl.get("cases", []))},
           "dispositions": [json.loads(l)["disposition_id"] + ":" + json.loads(l)["plan_id"] + ":" + json.loads(l)["disposition"]
                            for l in (HERE / "coroner_plans" / "DISPOSITIONS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()],
           "reader": "validate_workshop.py recomputes these hashes on every run and prints FREEZE MATCH / FREEZE DRIFT per file; drift is expected once the registry is regenerated and is a note, not an error",
           "rule": "the reported state is this record, not the working tree; a later regeneration does not rewrite it (R-CR-2 spirit: descendants cite parents)",
           "files": files}
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8", newline="\n")
    print("wrote", out.name, "files", len(files), "head", head)
    return 0


if __name__ == "__main__":
    sys.exit(main())
