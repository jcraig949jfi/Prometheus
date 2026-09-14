"""Catalogue controls: the planted behavioural queries are the catalogue's positive / negative / cheat
controls (base-role rule 3). Run after every ingestion; a regression is a ledger event, not a note.

    python -m nyx.catalog.controls            # exit 1 on any failed control
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from nyx.catalog.schema import load_all, validate, recurrences
from nyx.catalog.search import match

ROOT = Path("nyx/catalog")


def run(root: Path = ROOT) -> dict:
    bits = load_all(root / "bits")
    invalid = {b["id"]: validate(b) for b in bits if validate(b)}
    q = json.loads((root / "queries" / "planted.json").read_text(encoding="utf-8"))
    results = []
    for item in q["queries"]:
        r = {"id": item["id"], "kind": item["kind"]}
        try:
            ranked = match(item["query"], bits)
        except ValueError as e:
            r["error"] = str(e)[:120]
            r["pass"] = bool(item.get("expect_error"))
            results.append(r); continue
        if item.get("expect_error"):
            r["pass"] = False; r["why"] = "expected the matcher to refuse this query"; results.append(r); continue
        top = [b["id"] for s, b, _ in ranked[:max(1, len(item["expect_top"]))]]
        top_score = ranked[0][0] if ranked else 0.0
        if item["kind"] == "negative":
            r["pass"] = top_score <= item.get("max_score", 0.5); r["top_score"] = top_score; r["top"] = top[:1]
        else:
            # every expected id must be within the top len(expect_top)+1 and the first expected must be top-1 exact
            r["top"] = top; r["top_score"] = top_score
            r["pass"] = ranked[0][1]["id"] in item["expect_top"] and all(e in [b["id"] for s, b, _ in ranked[:len(item["expect_top"]) + 1]] for e in item["expect_top"])
        results.append(r)
    return {"bits": len(bits), "invalid": invalid, "recurrence_groups": {"|".join(k): v for k, v in recurrences(bits).items()},
            "controls": results, "all_pass": all(r["pass"] for r in results) and not invalid}


def main() -> int:
    out = run()
    print(json.dumps(out, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
