"""Apply an enrichment file to catalogue entries (deterministic).

Enrichment rows {rid, behaviour_tags, raw_rows, raw_rows_note, engine,
seat_fix, framing_flag} were drafted by an agent that read each entry's
sources. What they may change: behaviour_tags, raw_rows (re-validated by
build.py like every other field), raw_rows_note, engine, seat (only when
seat_fix is a plain seat name, not an "unknown (...)" note). framing_flag
is kept VERBATIM as `framing_note` with its origin -- a reader's flag that
the source does not support the entry's framing, not a verdict; it does
not change residual_kind or remove an entry.

Usage: python -m tyche.residuals.enrich <entries.jsonl> <enrich.jsonl> <out.jsonl>
"""

from __future__ import annotations

import json
import re
import sys


def main(entries, enrich, out):
    ex = {}
    for line in open(enrich, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            ex[r["rid"]] = r
    n = 0
    with open(out, "w", encoding="ascii", newline="\n") as f:
        for line in open(entries, encoding="utf-8"):
            if not line.strip():
                continue
            e = json.loads(line)
            x = ex.get(e["rid"])
            if x:
                n += 1
                e["behaviour_tags"] = x.get("behaviour_tags") or e.get("behaviour_tags", [])
                e["raw_rows"] = x.get("raw_rows") or []
                e["raw_rows_note"] = x.get("raw_rows_note")
                e["engine"] = x.get("engine") or e.get("engine")
                sf = x.get("seat_fix")
                if sf and re.fullmatch(r"[A-Z][A-Za-z\-]+", sf):
                    e["seat_orig"] = e.get("seat")
                    e["seat"] = sf
                if x.get("framing_flag"):
                    e["framing_note"] = {"text": x["framing_flag"], "by": "agent:enrich-2026-09-30",
                                         "status": "reader flag, not a verdict"}
            f.write(json.dumps(e, sort_keys=True, ensure_ascii=True) + "\n")
    print(f"enriched {n}")


if __name__ == "__main__":
    main(*sys.argv[1:])
