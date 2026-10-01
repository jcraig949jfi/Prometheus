"""Residual catalogue (CWO 2026-09-30, TYCHE CURRENT).

A residual is a phenomenon a Prometheus experiment observed and left
unexplained, contradictory, weak, unreplicated, parked or instrument-
ambiguous. The catalogue keeps provenance to the generating experiment;
it asserts nothing about the phenomenon's truth.

Entry schema (one JSON object per line in CATALOGUE_v0.jsonl):
  rid            R-0001 ...
  seat, engine   originating seat / engine or program
  phenomenon     one sentence, what was observed (numbers as written)
  residual_kind  unexplained | contradictory | weak | not_replicated |
                 parked | instrument_ambiguity
  sources        [{path, sha, quote}] -- quote must be an exact substring
                 of `git show sha:path` (a "..." in the quote splits it
                 into parts that must each appear, in order; " / " is a
                 line break unless the file contains it literally; path
                 COMMIT_MSG means the commit message of sha)
  raw_rows       [paths on the checked ref] or []; raw_rows_note for
                 off-repo evidence
  links          {"artemis": "H-D2-01", "thread": "TH-004", ...}
  behaviour_tags provisional, model-assigned descriptors for the NEXT
                 clustering assay; NOT evidence, never a selection ruler
  drafted_by     importer:artemis | agent:<id> | seat

validate() is the only admission rule: an entry whose source path does not
exist at its sha, whose quote is not in the file, or whose raw_rows do not
exist at the checked ref is REJECTED with a reason. Nothing is admitted on
anyone's say-so, including this seat's.

Usage: python -m tyche.residuals.catalogue <entries.jsonl> [ref]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

KINDS = {"unexplained", "contradictory", "weak", "not_replicated", "parked", "instrument_ambiguity"}
COMMIT_MSG = "COMMIT_MSG"
ELLIPSIS = re.compile(r"\.\.\.|" + chr(0x2026))  # "..." or the one-character ellipsis


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, timeout=60)


def show(sha, path):
    if path == COMMIT_MSG:
        r = _git("show", "-s", "--format=%B", sha)
    else:
        r = _git("show", f"{sha}:{path}")
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def _norm(s):
    return re.sub(r"\s+", " ", s.replace("\r\n", "\n")).strip()


def _quote_in(text, quote):
    t = _norm(text)
    pos = 0
    for part in [p for p in ELLIPSIS.split(quote) if p.strip()]:
        n = _norm(part)
        i = t.find(n, pos)
        if i < 0:
            return False
        pos = i + len(n)
    return True


def quote_in(text, quote):
    """" / " marks a hard line break in harvest-style quotes, but some files
    contain " / " literally: accept either reading."""
    return _quote_in(text, quote) or _quote_in(text, quote.replace(" / ", " "))


def validate(entry, ref="origin/main"):
    why = []
    for k in ("rid", "seat", "phenomenon", "residual_kind", "sources"):
        if not entry.get(k):
            why.append(f"missing {k}")
    if entry.get("residual_kind") not in KINDS:
        why.append(f"bad residual_kind {entry.get('residual_kind')}")
    for s in entry.get("sources", []):
        txt = show(s.get("sha", ""), s.get("path", ""))
        if txt is None:
            why.append(f"path not at sha: {s.get('path')}@{s.get('sha')}")
        elif not s.get("quote") or not quote_in(txt, s["quote"]):
            why.append(f"quote not found in {s.get('path')}@{s.get('sha')}")
    for p in entry.get("raw_rows", []):
        if _git("cat-file", "-e", f"{ref}:{p}").returncode != 0:
            why.append(f"raw_rows missing at {ref}: {p}")
    return why


def run(path, ref="origin/main"):
    ok, bad, rids = [], [], set()
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        e = json.loads(line)
        why = validate(e, ref)
        if e.get("rid") in rids:
            why.append("duplicate rid")
        rids.add(e.get("rid"))
        (bad if why else ok).append((e, why))
    return ok, bad


def main(path, ref="origin/main"):
    ok, bad = run(path, ref)
    for e, why in bad:
        print("REJECT", e.get("rid"), "; ".join(why))
    print(f"admitted {len(ok)} rejected {len(bad)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
