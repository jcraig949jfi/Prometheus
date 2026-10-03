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
  It is FLAGGED when the +-200-character window around it uses search-outcome language and the
  row is not an evolve row.

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
  python kind_audit.py PATH [PATH ...] [--ext .md,.txt] [--min-len 8] [--fail-on HIGH]
                       [--json] [--csv OUT.csv] [--rows cells.jsonl.gz] [--all]
  PATH may be a file, a directory (recursive) or "-" for stdin.
  Exit 0: nothing at or above --fail-on. Exit 1: at least one such flag. Exit 2: cannot run
  (rows file not found, unreadable path).

API
  audit_text(text, path="<text>", index=None, min_len=8) -> list[dict]   (every citation)
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


def audit_text(text: str, path: str = "<text>", index: Index | None = None, min_len: int = 8) -> list[dict]:
    """Every resolved C1 citation in text, flagged or not. Line numbers are 1-based in text."""
    if min_len < 6 or min_len > MAX_HEX:
        raise ValueError(f"min_len must be in 6..{MAX_HEX}")
    index = index or load_index()
    out = []
    for m in _id_re(min_len).finditer(text):
        tok = m.group(1)
        cid = index.resolve(tok)
        if cid is None:
            continue
        meta = index.cells[cid]
        a, b = max(0, m.start() - WINDOW), min(len(text), m.end() + WINDOW)
        win, pos = text[a:b], m.start() - a
        terms, dmin = set(), None
        for name, rx in OUTCOME_RES:
            for t in rx.finditer(win):
                terms.add(name)
                d = min(abs(t.start() - pos), abs(t.end() - (pos + len(tok))))
                dmin = d if dmin is None else min(dmin, d)
        kind_named = bool(KIND_WORDS[meta["kind"]].search(win))
        sev = _severity(meta["kind"], terms, kind_named)
        out.append({
            "file": path, "line": text.count("\n", 0, m.start()) + 1, "token": tok, "cell_id": cid,
            "kind": meta["kind"], "wave": meta["wave"], "family": meta["family"],
            "flagged": int(bool(sev)), "severity": sev, "terms": "|".join(sorted(terms)),
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
                min_len: int = 8) -> list[dict]:
    index = index or load_index()
    recs = []
    for q in iter_files(paths, exts, exclude):
        recs += audit_text(q.read_text(encoding="utf-8", errors="replace"), _display(q), index, min_len)
    return recs


def summary(records: list[dict], index: Index | None = None, min_len: int = 8) -> dict:
    """Compact JSON-safe record of the flags (what deposit.py stores in provenance)."""
    fl = flags(records)
    return {"tool": TOOL_VERSION, "rows": index.source if index else None, "min_len": min_len,
            "citations": len(records), "counts": counts(records),
            "flags": [{k: r[k] for k in ("line", "token", "cell_id", "kind", "wave", "severity", "terms")}
                      for r in fl]}


# ----------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", help="files, directories (recursive) or - for stdin")
    ap.add_argument("--ext", default=",".join(DEFAULT_EXT), help="directory scan suffixes (comma list)")
    ap.add_argument("--exclude", action="append", default=[], help="extra fnmatch glob on absolute posix path")
    ap.add_argument("--min-len", type=int, default=8)
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
                recs += audit_text(sys.stdin.read(), "<stdin>", index, a.min_len)
            elif not pathlib.Path(p).exists():
                raise FileNotFoundError(p)
            else:
                recs += audit_paths([p], index, exts, (*DEFAULT_EXCLUDE, *a.exclude), a.min_len)
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
        print(json.dumps({"summary": summary(recs, index, a.min_len)["counts"], "citations": len(recs),
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
