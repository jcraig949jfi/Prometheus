"""kind_audit: flag C1 cell ids cited with search-outcome language when the row is not kind=evolve.

Proposed home: roles/Ananke/research/tools/kind_audit.py. Pure stdlib. Productionised from
W2-I's harvest/wave2/W2-I/kind_audit.py (same severity semantics; recall gaps closed where safe).

What it does
  A token of 8-16 hex digits, in ANY case, that is not part of a longer alphanumeric run
  (underscore neighbours are allowed, so "D_f7e62fe3" is seen) is lower-cased and resolved as a
  PREFIX of exactly one real C1 cell_id (roles/Ananke/pte/c1_rows/cells.jsonl.gz; C1b rows cite
  C1 cell ids, so this id set covers both). Anything that does not resolve (git shas, hashes,
  dates, words like DEADBEEF) is ignored, so the case-insensitive match costs no precision.
  Each resolved citation gets its row kind (evolve / transfer / census / adjudicate) and wave.
  It is FLAGGED when the row is not an evolve row and its own text block uses search-outcome
  language. The block is the citation's paragraph or list item (hard-wrapped lines joined), with
  the item's nested children and the first line of each enclosing parent item, or the whole line
  when it is a '|' table/ledger row; clipped to +-200 characters. Sibling items, other paragraphs
  and other rows are out. W2-I used the whole +-200 window, which let "held"/"champion" in a
  NEIGHBOURING bullet raise HIGH; --scope window restores that, and every record also carries
  "severity_window" (the W2-I severity), so the narrower default hides nothing from a reviewer.
  The true-kind exoneration (LOW) still looks at the whole +-200 window.

  Outcome language: search/searched/searches/searching, evolved, champion(s) (any case),
  NULL (upper case only), held (any case, but NOT "held-out"/"held out", a transfer target).

Severity (a flag is a candidate for hand review, not a verdict)
  HIGH    outcome language, and the window never names the row's true kind
  NAMING  an adjudicate (D-wave) row with only "champion"/"evolved" nearby: every D genome is
          bit-identical to its parent's evolved champion, so this is a naming/provenance hole
  LOW     outcome language, but the window also names the true kind ("a transfer, not a
          search NULL"); usually a correction or a careful sentence

Deliberate limits (see W2-AA REPORT)
  * Ids shorter than 8 hex are NOT matched by default. 7-hex prefixes are unique in C1, but
    7-hex tokens are also git short shas; --min-len 7 opts in, and then each hit should be read.
  * Tokens longer than 16 hex (e.g. 40-hex shas) never match, even if their head is a cell id.
  * Default file types are .md and .txt. .py/.json/.jsonl/.csv/.log can be added with --ext;
    the files this tool (and W2-I's) writes are excluded so contexts are not double counted.

CLI
  python kind_audit.py PATH [PATH ...] [--ext .md,.txt] [--min-len 8] [--scope block|window]
                       [--fail-on HIGH] [--json] [--csv OUT.csv] [--rows cells.jsonl.gz] [--all]
  PATH may be a file, a directory (recursive) or "-" for stdin.
  Exit 0: nothing at or above --fail-on. Exit 1: at least one such flag. Exit 2: cannot run
  (rows file not found, unreadable path).

API
  audit_text(text, path="<text>", index=None, min_len=8, scope="block") -> list[dict]  (every citation)
  audit_paths(paths, index=None, exts=(".md", ".txt"), exclude=..., min_len=8, scope="block")
  flags(records) -> flagged records only;  counts(records) -> {"HIGH": n, "NAMING": n, "LOW": n}
"""
from __future__ import annotations

import argparse
import collections
import csv
import fnmatch
import functools
import gzip
import json
import os
import pathlib
import re
import sys

TOOL_VERSION = "kind_audit/1.0 (W2-AA, from W2-I)"
ROWS_REL = pathlib.Path("roles/Ananke/pte/c1_rows/cells.jsonl.gz")
WINDOW = 200
MAX_HEX = 16
SEVERITIES = ("HIGH", "NAMING", "LOW")
DEFAULT_EXT = (".md", ".txt")
DEFAULT_EXCLUDE = ("*/__pycache__/*", "*/.git/*", "*kind_audit*.csv", "*kind_audit*.json")

OUTCOME_RES = [
    ("search", re.compile(r"\bsearch(?:ed|es|ing)?\b", re.I)),
    ("evolved", re.compile(r"\bevolved\b", re.I)),
    ("champion", re.compile(r"\bchampions?\b", re.I)),
    ("NULL", re.compile(r"\bNULL\b")),
    ("held", re.compile(r"\bheld\b(?![- ]out)", re.I)),
]
# a line that starts a new text block: bullet, numbered item, heading, table row
BLOCK_START = re.compile(r"[ \t]*(?:[-*+][ \t]|\d+[.)][ \t]|#|\|)")
_ITEM = re.compile(r"[ \t]*(?:[-*+][ \t]|\d+[.)][ \t])")  # bullet or numbered item only
KIND_WORDS = {
    "transfer": re.compile(r"\btransfer(?:s|red|ring)?\b", re.I),
    "census": re.compile(r"\bcensus(?:es)?\b|\bA0\b", re.I),
    "adjudicate": re.compile(r"\badjudicat\w*|\bD-wave control|\bre-?evaluat\w*", re.I),
    "evolve": re.compile(r"\bevolve\b", re.I),
}


def _id_re(min_len: int) -> re.Pattern:
    return re.compile(r"(?<![0-9A-Za-z])([0-9A-Fa-f]{%d,%d})(?![0-9A-Za-z])" % (min_len, MAX_HEX))


# ----------------------------------------------------------------------------- C1 rows loader
def find_rows(start: pathlib.Path | None = None) -> pathlib.Path:
    """$KIND_AUDIT_ROWS, else the first ancestor of this file (then of cwd) holding ROWS_REL."""
    env = os.environ.get("KIND_AUDIT_ROWS")
    if env:
        return pathlib.Path(env)
    for base in (start, pathlib.Path(__file__).resolve(), pathlib.Path.cwd().resolve()):
        if base is None:
            continue
        for d in (base, *base.parents):
            if (d / ROWS_REL).is_file():
                return d / ROWS_REL
    raise FileNotFoundError(f"C1 rows {ROWS_REL} not found above {__file__} or cwd; set KIND_AUDIT_ROWS")


def iter_rows(path: pathlib.Path):
    """The C1 rows, one dict per cell (same file and parse as harvest/H-PLANT/hp_common.rows())."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


@functools.lru_cache(maxsize=4)
def load_index(rows_path: str | None = None) -> "Index":
    p = pathlib.Path(rows_path) if rows_path else find_rows()
    return Index({r["cell_id"].lower(): {"kind": r["kind"], "wave": r["wave"], "family": r["env"]["family"]}
                  for r in iter_rows(p)}, str(p))


class Index:
    """Prefix lookup: a token resolves only if it is a prefix of EXACTLY one cell id."""

    def __init__(self, cells: dict, source: str = "<memory>"):
        self.cells, self.source = cells, source
        self._by6 = collections.defaultdict(list)
        for cid in cells:
            self._by6[cid[:6]].append(cid)

    def resolve(self, tok: str):
        tok = tok.lower()
        if len(tok) < 6:
            return None
        cands = [c for c in self._by6.get(tok[:6], ()) if c.startswith(tok)]
        return cands[0] if len(cands) == 1 else None


# ----------------------------------------------------------------------------- core
def _severity(kind: str, terms: set, kind_named: bool) -> str:
    if kind == "evolve" or not terms:
        return ""
    if kind_named:
        return "LOW"
    if kind == "adjudicate" and terms <= {"champion", "evolved"}:
        return "NAMING"
    return "HIGH"


def _line_bounds(text: str, i: int) -> tuple[int, int]:
    """[start, end) of the line containing offset i (end excludes the newline)."""
    end = text.find("\n", i)
    return text.rfind("\n", 0, i) + 1, len(text) if end < 0 else end


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _is_table(line: str) -> bool:
    return line.count("|") >= 2


def _block(text: str, s: int, e: int, lo: int, hi: int) -> list[tuple[int, int]]:
    """Spans [start, end) of the citation's own text block, clipped to [lo, hi).

    Table/ledger row (2+ '|'): the whole line (a row is a record about its cell; other columns count).
    Otherwise: the citation's paragraph or list item, joined across hard-wrapped lines, PLUS the
    item's nested children (more-indented lines below it) and the first line of each enclosing parent
    item (less-indented lines above it). Sibling items, other paragraphs and other table rows are out.
    A blank line, a heading or a table row always ends the block."""
    ls, le = _line_bounds(text, s)
    if _is_table(text[ls:le]):
        return [(max(lo, ls), min(hi, le))]
    start = ls
    while start > lo and not BLOCK_START.match(text[start:_line_bounds(text, start)[1]]):
        ps, pe = _line_bounds(text, start - 1)
        prev = text[ps:pe]
        if not prev.strip() or BLOCK_START.match(prev) and not _ITEM.match(prev) or _is_table(prev):
            break  # blank, heading or table above: this paragraph starts here
        start = ps
        if _ITEM.match(prev):
            break  # we were a hard-wrapped continuation of this item
    base = _indent(text[start:_line_bounds(text, start)[1]])
    end = le
    while end < hi:
        ns, ne = _line_bounds(text, end + 1)
        nxt = text[ns:ne]
        if not nxt.strip() or _is_table(nxt) or (BLOCK_START.match(nxt) and _indent(nxt) <= base):
            break
        end = ne
    spans = [(max(lo, start), min(hi, end))]
    k, cur = start, base
    while k > lo and cur > 0:  # enclosing parent items: first less-indented line above, repeatedly
        ps, pe = _line_bounds(text, k - 1)
        prev = text[ps:pe]
        if not prev.strip() or _is_table(prev):
            break
        if _indent(prev) < cur:
            spans.append((max(lo, ps), min(hi, pe)))
            cur = _indent(prev)
        k = ps
    return spans


def audit_text(text: str, path: str = "<text>", index: Index | None = None, min_len: int = 8,
               scope: str = "block") -> list[dict]:
    """Every resolved C1 citation in text, flagged or not. Line numbers are 1-based in text.

    scope="block" (default): outcome terms count only inside the citation's own block (see _block),
    within +-WINDOW chars. scope="window": the whole +-WINDOW (W2-I behaviour). Each record carries
    both "severity" (the chosen scope) and "severity_window" (W2-I), so nothing is lost by the
    narrower default. The true-kind exoneration (LOW) always looks at the whole +-WINDOW."""
    if min_len < 6 or min_len > MAX_HEX:
        raise ValueError(f"min_len must be in 6..{MAX_HEX}")
    if scope not in ("block", "window"):
        raise ValueError("scope must be 'block' or 'window'")
    index = index or load_index()
    out = []
    for m in _id_re(min_len).finditer(text):
        tok = m.group(1)
        cid = index.resolve(tok)
        if cid is None:
            continue
        meta = index.cells[cid]
        a, b = max(0, m.start() - WINDOW), min(len(text), m.end() + WINDOW)
        spans = _block(text, m.start(), m.end(), a, b)
        block, wide, dmin = set(), set(), None
        for name, rx in OUTCOME_RES:
            for t in rx.finditer(text, a, min(len(text), b + 16)):
                if t.end() > b:
                    continue
                wide.add(name)
                inside = any(lo <= t.start() and t.end() <= hi for lo, hi in spans)
                if scope == "block" and not inside:
                    continue
                block.add(name)
                d = min(abs(t.start() - m.start()), abs(t.end() - m.end()))
                dmin = d if dmin is None else min(dmin, d)
        win = text[a:b]
        kind_named = bool(KIND_WORDS[meta["kind"]].search(win))
        sev = _severity(meta["kind"], block, kind_named)
        out.append({
            "file": path, "line": text.count("\n", 0, m.start()) + 1, "token": tok, "cell_id": cid,
            "kind": meta["kind"], "wave": meta["wave"], "family": meta["family"],
            "flagged": int(bool(sev)), "severity": sev,
            "severity_window": _severity(meta["kind"], wide, kind_named), "scope": scope,
            "terms": "|".join(sorted(block)), "terms_outside_block": "|".join(sorted(wide - block)),
            "nearest_term_chars": "" if dmin is None else dmin, "kind_named_in_window": int(kind_named),
            "context": " ".join(win.split())[:420],
        })
    return out


def flags(records: list[dict]) -> list[dict]:
    order = {s: i for i, s in enumerate(SEVERITIES)}
    return sorted((r for r in records if r["severity"]),
                  key=lambda r: (order[r["severity"]], r["file"], r["line"], r["token"]))


def counts(records: list[dict]) -> dict:
    c = collections.Counter(r["severity"] for r in records if r["severity"])
    return {s: c.get(s, 0) for s in SEVERITIES}


def is_binary(p: pathlib.Path) -> bool:
    with open(p, "rb") as f:
        return b"\0" in f.read(8192)


def iter_files(paths, exts=DEFAULT_EXT, exclude=DEFAULT_EXCLUDE):
    exts = {e.lower() for e in exts}
    for p in paths:
        p = pathlib.Path(p)
        cands = sorted(q for q in p.rglob("*") if q.is_file()) if p.is_dir() else [p]
        for q in cands:
            posix = q.resolve().as_posix()
            if p.is_dir() and q.suffix.lower() not in exts:
                continue
            if any(fnmatch.fnmatch(posix, g) for g in exclude):
                continue
            if is_binary(q):
                continue
            yield q


def _display(p: pathlib.Path) -> str:
    rp = p.resolve()
    for d in rp.parents:
        if (d / ".git").exists():
            return rp.relative_to(d).as_posix()
    return rp.as_posix()


def audit_paths(paths, index: Index | None = None, exts=DEFAULT_EXT, exclude=DEFAULT_EXCLUDE,
                min_len: int = 8, scope: str = "block") -> list[dict]:
    index = index or load_index()
    recs = []
    for q in iter_files(paths, exts, exclude):
        recs += audit_text(q.read_text(encoding="utf-8", errors="replace"), _display(q), index, min_len, scope)
    return recs


def summary(records: list[dict], index: Index | None = None, min_len: int = 8) -> dict:
    """Compact JSON-safe record of the flags (what deposit.py stores in provenance). "flags" lists every
    citation flagged under the chosen scope OR under the W2-I window scope (severity may then be "")."""
    order = {s: i for i, s in enumerate(("HIGH", "NAMING", "LOW", ""))}
    fl = sorted((r for r in records if r["severity"] or r["severity_window"]),
                key=lambda r: (order[r["severity"]], order[r["severity_window"]], r["line"], r["token"]))
    return {"tool": TOOL_VERSION, "rows": index.source if index else None, "min_len": min_len,
            "scope": records[0]["scope"] if records else None,
            "citations": len(records), "counts": counts(records),
            "counts_window_scope": counts([{**r, "severity": r["severity_window"]} for r in records]),
            "flags": [{k: r[k] for k in ("line", "token", "cell_id", "kind", "wave", "severity",
                                         "severity_window", "terms", "terms_outside_block")} for r in fl]}


# ----------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", help="files, directories (recursive) or - for stdin")
    ap.add_argument("--ext", default=",".join(DEFAULT_EXT), help="directory scan suffixes (comma list)")
    ap.add_argument("--exclude", action="append", default=[], help="extra fnmatch glob on absolute posix path")
    ap.add_argument("--min-len", type=int, default=8)
    ap.add_argument("--scope", choices=["block", "window"], default="block")
    ap.add_argument("--fail-on", choices=[*SEVERITIES, "none"], default="HIGH")
    ap.add_argument("--rows", default=None, help="C1 cells.jsonl.gz (default: found above this file)")
    ap.add_argument("--json", action="store_true", help="print flagged records as JSON")
    ap.add_argument("--csv", default=None, help="write every citation (flagged or not) to this CSV")
    ap.add_argument("--all", action="store_true", help="print LOW and NAMING too (default HIGH only)")
    a = ap.parse_args(argv)
    try:
        index = load_index(a.rows)
    except (OSError, ValueError, KeyError) as e:
        print(f"kind_audit: cannot load C1 rows: {e}", file=sys.stderr)
        return 2
    exts = tuple(e if e.startswith(".") else "." + e for e in a.ext.split(",") if e)
    recs = []
    try:
        for p in a.paths:
            if p == "-":
                recs += audit_text(sys.stdin.read(), "<stdin>", index, a.min_len, a.scope)
            elif not pathlib.Path(p).exists():
                raise FileNotFoundError(p)
            else:
                recs += audit_paths([p], index, exts, (*DEFAULT_EXCLUDE, *a.exclude), a.min_len, a.scope)
    except (OSError, ValueError) as e:
        print(f"kind_audit: {e}", file=sys.stderr)
        return 2
    fl = flags(recs)
    if a.csv:
        cols = list(recs[0]) if recs else ["file"]
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(sorted(recs, key=lambda r: (-r["flagged"], r["file"], r["line"])))
    shown = fl if a.all else [r for r in fl if r["severity"] == "HIGH"]
    if a.json:
        print(json.dumps({"summary": counts(recs), "citations": len(recs),
                          "flags": shown}, indent=1))
    else:
        for r in shown:
            print(f"{r['severity']:6} {r['file']}:{r['line']} {r['token']} [{r['kind']}/{r['wave']}] "
                  f"terms={r['terms']} | {r['context'][:200]}")
        print(f"kind_audit: {len(recs)} citations, {counts(recs)}", file=sys.stderr)
    if a.fail_on == "none":
        return 0
    worst = SEVERITIES[: SEVERITIES.index(a.fail_on) + 1]
    return 1 if any(r["severity"] in worst for r in fl) else 0


if __name__ == "__main__":
    sys.exit(main())
