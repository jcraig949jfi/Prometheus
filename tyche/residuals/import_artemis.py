"""Import residual-kind entries from Artemis's harvest (roles/Artemis/backlog/
harvest/D1-D5.md) at a fixed ref, deterministically. Only kinds anomaly,
contradiction and parked-experiment are residuals; the rest (open
questions, future work, ...) are Artemis's backlog, not Tyche's catalogue.

Usage: python -m tyche.residuals.import_artemis <ref> <out.jsonl>
"""

from __future__ import annotations

import json
import re
import sys

from .catalogue import show

FILES = ["D1_program", "D2_replication", "D3_new_lenses", "D4_sfe_era", "D5_older_lines"]
KIND = {"anomaly": "unexplained", "contradiction": "contradictory", "parked-experiment": "parked"}
SRC = re.compile(r"(?P<path>[A-Za-z_][\w./\-]*?)(?::(?P<line>[\d,\-]+))?\s*@\s*(?P<sha>[0-9a-f]{7,40})")
MSG = re.compile(r"commit message\s+(?P<sha>[0-9a-f]{7,40})")
# a quote runs to the first unescaped double quote; \" inside it is literal
QUOTE = re.compile(r'quote:\s*"(?P<q>(?:[^"\\]|\\.)*)"')


def _q(m):
    return m.group("q").replace('\\"', '"') if m else ""


def parse(text, fname, ref):
    out = []
    blocks = re.split(r"\n(?=### H-)", text)
    for b in blocks:
        m = re.match(r"### (H-D\d-\d+[a-z]?)\s+(.*)", b)
        if not m:
            continue
        hid, title = m.group(1), m.group(2).strip()
        km = re.search(r"^- kind:\s*([\w\-]+)", b, re.M)
        kind = km.group(1) if km else None
        if kind not in KIND:
            continue
        sm = re.search(r"^- source:(.*)$", b, re.M)
        src_line = sm.group(1) if sm else ""
        s = SRC.search(src_line)
        q = QUOTE.search(src_line)
        seat = re.search(r"seat\s+([A-Z][\w\-]+)", src_line)
        sources = []
        mm = MSG.search(src_line)
        if mm and (not s or mm.start() < s.start()):
            sources.append({"path": "COMMIT_MSG", "sha": mm.group("sha"), "line": None,
                            "quote": _q(q)})
        elif s:
            sources.append({"path": s.group("path"), "sha": s.group("sha"),
                            "line": s.group("line"), "quote": _q(q)})
        out.append({
            "seat": seat.group(1) if seat else None, "engine": None,
            "phenomenon": title, "residual_kind": KIND[kind], "sources": sources,
            "raw_rows": [], "links": {"artemis": hid, "artemis_file": f"roles/Artemis/backlog/harvest/{fname}.md@{ref}"},
            "behaviour_tags": [], "drafted_by": "importer:artemis"})
    return out


def main(ref, out_path):
    rows = []
    for f in FILES:
        txt = show(ref, f"roles/Artemis/backlog/harvest/{f}.md")
        rows += parse(txt, f, ref)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        for i, r in enumerate(rows, 1):
            r = {"rid": f"R-A{i:03d}", **r}
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n")
    print(f"imported {len(rows)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
