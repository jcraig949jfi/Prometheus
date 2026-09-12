"""Ingest a Wikipedia list page (fetched wikitext JSON from the parse API) into CANDIDATE entries.

A candidate is NOT a bit. It is a name + section path + one-line description at grade T2 (a human
description of a mechanism believed to exist), with classification PENDING. Bits are made from
candidates by the classification step (a judgment per entry, recorded with the vocab values and a
behavioural mechanism sentence) -- that step is the loop's work; this file only makes the queue.

    python -m nyx.catalog.ingest_wikipedia <parse.json> <source_id>
writes nyx/catalog/sources/<source_id>.json with page, revid, fetched_at, entries[].
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
REF = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.S)
HTML = re.compile(r"<[^>]+>")
BOLD = re.compile(r"'{2,3}")


def clean(s: str) -> str:
    s = REF.sub("", s)
    s = TEMPLATE.sub("", s)
    s = LINK.sub(lambda m: m.group(2) or m.group(1), s)
    s = HTML.sub("", s)
    s = BOLD.sub("", s)
    return re.sub(r"\s+", " ", s).strip()


def parse(wikitext: str):
    path = []
    entries = []
    for line in wikitext.splitlines():
        m = re.match(r"^(={2,5})\s*(.+?)\s*=+\s*$", line)
        if m:
            depth = len(m.group(1)) - 2
            path = path[:depth] + [clean(m.group(2))]
            continue
        m = re.match(r"^(\*+)\s*(.+)$", line)
        if not m:
            continue
        raw = m.group(2)
        link = LINK.search(raw)
        target = link.group(1) if link else None
        text = clean(raw)
        if not text:
            continue
        name, _, desc = text.partition(":")
        if not desc:
            name, _, desc = text.partition(" – ")
        if not desc:
            name, _, desc = text.partition(" - ")
        entries.append({"name": name.strip()[:120], "description": desc.strip(), "wiki_target": target,
                        "section": list(path), "depth": len(m.group(1)), "classification": "PENDING"})
    return entries


def main(argv):
    src = Path(argv[1]); source_id = argv[2]
    d = json.loads(src.read_text(encoding="utf-8"))["parse"]
    entries = parse(d["wikitext"])
    out = {"schema": "nyx.bit.source/0", "source_id": source_id, "page": d["title"], "revid": d.get("revid"),
           "url": f"https://en.wikipedia.org/w/index.php?title={d['title'].replace(' ', '_')}&oldid={d.get('revid')}",
           "fetched_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "grade": "T2",
           "n_entries": len(entries), "entries": entries}
    Path("nyx/catalog/sources").mkdir(parents=True, exist_ok=True)
    Path("nyx/catalog/sources", f"{source_id}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    sections = {}
    for e in entries:
        sections[" / ".join(e["section"][:2])] = sections.get(" / ".join(e["section"][:2]), 0) + 1
    print(source_id, d["title"], "revid", d.get("revid"), "entries", len(entries))
    for k, v in sorted(sections.items(), key=lambda kv: -kv[1])[:25]:
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main(sys.argv)
