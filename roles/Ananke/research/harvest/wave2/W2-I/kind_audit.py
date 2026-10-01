"""W2-I citation KIND auditor.

Scans every .md/.txt file under roles/Ananke (binary files skipped, nothing else excluded) for
C1 cell ids (8-16 lowercase hex, matched as a PREFIX of a real cell_id from the C1 rows; C1b rows
reference C1 cell ids, so the C1 id set covers both). Each citation is mapped to its row kind
(evolve / transfer / census / adjudicate) and wave, and flagged when the +-200-character window
around it uses search-outcome language for a NON-evolve row.

Outcome language: search/searched/searches/searching, evolved, champion(s) (any case), NULL
(upper case only), held (any case, but NOT "held-out"/"held out", which names a transfer target).
Severity:
  HIGH  outcome language present and the window never names the row's true kind
  LOW   outcome language present but the window also names the true kind (e.g. "a transfer,
        not a search NULL"); usually a correction or a careful sentence
  NAMING an adjudicate (D-wave) row id with only "champion"/"evolved" nearby: the genome IS an
        evolved champion (bit-identical to its parent's), so this is a naming/provenance hole
A flag is a candidate for hand review, not a verdict.

usage: python kind_audit.py [--root roles/Ananke] [--out DIR]
Outputs kind_audit.csv (every citation, flagged or not) and kind_audit_summary.json.
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
WINDOW = 200

# underscores allowed as neighbours so "D_f7e62fe3" and "main_bbef66a1" are seen
ID_RE = re.compile(r"(?<![0-9A-Za-z])([0-9a-f]{8,16})(?![0-9A-Za-z])")
OUTCOME_RES = [
    ("search", re.compile(r"\bsearch(?:ed|es|ing)?\b", re.I)),
    ("evolved", re.compile(r"\bevolved\b", re.I)),
    ("champion", re.compile(r"\bchampions?\b", re.I)),
    ("NULL", re.compile(r"\bNULL\b")),
    ("held", re.compile(r"\bheld\b(?![- ]out)", re.I)),
]
KIND_WORDS = {
    "transfer": re.compile(r"\btransfer(?:s|red|ring)?\b", re.I),
    "census": re.compile(r"\bcensus(?:es)?\b|\bA0\b", re.I),
    "adjudicate": re.compile(r"\badjudicat\w*|\bD-wave control|\bre-?evaluat\w*", re.I),
    "evolve": re.compile(r"\bevolve\b", re.I),
}


def load_index(rows_path=ROWS) -> dict:
    """full 16-hex cell_id -> {"kind", "wave", "family"}"""
    idx = {}
    for line in gzip.open(rows_path, "rt"):
        r = json.loads(line)
        idx[r["cell_id"]] = {"kind": r["kind"], "wave": r["wave"], "family": r["env"]["family"]}
    return idx


class Resolver:
    """Prefix lookup; a token resolves only if it is a prefix of EXACTLY one cell id."""

    def __init__(self, index: dict):
        self.index = index
        self.by8 = collections.defaultdict(list)
        for cid in index:
            self.by8[cid[:8]].append(cid)

    def resolve(self, tok: str):
        cands = [c for c in self.by8.get(tok[:8], ()) if c.startswith(tok)]
        return cands[0] if len(cands) == 1 else None


def is_binary(p: pathlib.Path) -> bool:
    with open(p, "rb") as f:
        return b"\0" in f.read(8192)


def audit_text(text: str, resolver: Resolver, path: str = "<text>") -> list[dict]:
    out = []
    for m in ID_RE.finditer(text):
        tok = m.group(1)
        cid = resolver.resolve(tok)
        if cid is None:
            continue
        meta = resolver.index[cid]
        a, b = max(0, m.start() - WINDOW), min(len(text), m.end() + WINDOW)
        win = text[a:b]
        pos = m.start() - a
        terms, dmin = [], None
        for name, rx in OUTCOME_RES:
            for t in rx.finditer(win):
                terms.append(name)
                dist = min(abs(t.start() - pos), abs(t.end() - (pos + len(tok))))
                dmin = dist if dmin is None else min(dmin, dist)
        terms = sorted(set(terms))
        kind_named = bool(KIND_WORDS[meta["kind"]].search(win))
        flagged = meta["kind"] != "evolve" and bool(terms)
        if not flagged:
            sev = ""
        elif kind_named:
            sev = "LOW"
        elif meta["kind"] == "adjudicate" and set(terms) <= {"champion", "evolved"}:
            # every D adjudicate genome is bit-identical to its parent's evolved champion
            # (checked in W2-I); naming the champion by the adjudicate row id is a
            # provenance/naming hole, not a search-outcome misattribution
            sev = "NAMING"
        else:
            sev = "HIGH"
        line = text.count("\n", 0, m.start()) + 1
        out.append({
            "file": path, "line": line, "token": tok, "cell_id": cid, "kind": meta["kind"],
            "wave": meta["wave"], "family": meta["family"], "flagged": int(flagged),
            "severity": sev, "terms": "|".join(terms), "nearest_term_chars": "" if dmin is None else dmin,
            "kind_named_in_window": int(kind_named),
            "context": " ".join(win.split())[:420],
        })
    return out


def scan(root: pathlib.Path, resolver: Resolver) -> list[dict]:
    recs = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (".md", ".txt"):
            continue
        if is_binary(p):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        recs += audit_text(text, resolver, p.relative_to(ROOT).as_posix())
    return recs


def summarise(recs: list[dict]) -> dict:
    fl = [r for r in recs if r["flagged"]]
    by_doc = collections.defaultdict(list)
    for r in fl:
        by_doc[r["file"]].append(r)
    return {
        "citations": len(recs),
        "distinct_cells_cited": len({r["cell_id"] for r in recs}),
        "files_with_citations": len({r["file"] for r in recs}),
        "citations_by_kind": dict(collections.Counter(r["kind"] for r in recs)),
        "flagged": len(fl),
        "flagged_HIGH": sum(r["severity"] == "HIGH" for r in fl),
        "flagged_LOW": sum(r["severity"] == "LOW" for r in fl),
        "flagged_NAMING": sum(r["severity"] == "NAMING" for r in fl),
        "flagged_by_kind": dict(collections.Counter(r["kind"] for r in fl)),
        "flagged_cells": dict(collections.Counter(r["cell_id"][:8] + ":" + r["kind"] for r in fl).most_common()),
        "flagged_by_document": {
            f: {"HIGH": sum(r["severity"] == "HIGH" for r in v), "LOW": sum(r["severity"] == "LOW" for r in v),
                "NAMING": sum(r["severity"] == "NAMING" for r in v),
                "cells": sorted({r["cell_id"][:8] for r in v})}
            for f, v in sorted(by_doc.items(), key=lambda kv: -len(kv[1]))},
    }


def rank(recs):
    """Review order: HIGH first, then closest outcome term to the id."""
    fl = [r for r in recs if r["flagged"]]
    order = {"HIGH": 0, "NAMING": 1, "LOW": 2}
    return sorted(fl, key=lambda r: (order[r["severity"]], r["nearest_term_chars"], r["file"], r["line"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "roles/Ananke"))
    ap.add_argument("--out", default=str(pathlib.Path(__file__).resolve().parent))
    a = ap.parse_args()
    res = Resolver(load_index())
    recs = scan(pathlib.Path(a.root), res)
    out = pathlib.Path(a.out)
    cols = list(recs[0].keys()) if recs else ["file"]
    with open(out / "kind_audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(recs, key=lambda r: (-r["flagged"], {"HIGH": 0, "NAMING": 1, "LOW": 2, "": 3}[r["severity"]],
                                           r["file"], r["line"])))
    summ = summarise(recs)
    summ["review_order_top15"] = [
        {k: r[k] for k in ("file", "line", "token", "kind", "wave", "family", "severity", "terms", "context")}
        for r in rank(recs)[:15]]
    (out / "kind_audit_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k not in ("review_order_top15", "flagged_by_document",
                                                                 "flagged_cells")}, indent=1))


if __name__ == "__main__":
    main()
