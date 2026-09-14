"""Bounded census of environment-dependent correctness (batch 10 P5).

md5-rfc1321 compiles clean, runs clean, exits 0 and prints WRONG digests on LP64, because
RFC 1321 declares `typedef unsigned long int UINT4` -- true in 1992, false today. The charter asks
whether that was a one-off or whether the vault holds other specimens whose CORRECTNESS depends on
a property of the world rather than of the code.

This is a MECHANICAL scan of preserved bodies. It does not judge; it reports what patterns are
present, with the matching line, so candidates can then be TESTED in two worlds. Nothing is
manufactured: a fossil appears here only if its own preserved bytes contain the pattern.

    python -m techne.fossils.env_assumption_census [--out F]

Precision matters more than recall here: a noisy scan that flags every C file would be useless, so
each pattern is narrow and carries its rationale.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import time

from . import vault

TEXT_EXT = {".c", ".h", ".cc", ".cpp", ".hpp", ".f", ".f77", ".f90", ".inc", ".txt", ".py", ".s", ".asm"}
MAX_BYTES = 2_000_000

# Each pattern is deliberately narrow. `why` states what could go wrong, not that it does.
PATTERNS = [
    ("WORD_WIDTH_TYPEDEF",
     re.compile(r"typedef\s+(?:unsigned\s+)?long(?:\s+int)?\s+\w*(?:32|4|word)\w*\s*;", re.I),
     "a fixed width is asserted onto `long`, whose width is platform-dependent (the exact MD5 defect)"),
    ("WORD_WIDTH_ASSUMPTION",
     re.compile(r"sizeof\s*\(\s*(?:unsigned\s+)?long\s*\)\s*==\s*4|assume.{0,20}32.bit|32-bit\s+(?:long|word)", re.I),
     "code states or tests an assumption about a 32-bit word"),
    ("ENDIANNESS",
     re.compile(r"\b(BIG_ENDIAN|LITTLE_ENDIAN|BYTE_ORDER|__bswap|bswap_32|htonl|ntohl)\b"),
     "byte order is handled explicitly; correctness may depend on which branch is taken"),
    ("ALIGNMENT_CAST",
     re.compile(r"\(\s*(?:unsigned\s+)?(?:int|long|short)\s*\*\s*\)\s*(?:\(\s*)?(?:buf|buffer|data|p|ptr|block)\b"),
     "a byte buffer is reinterpreted as a wider type; unaligned access is UB on some targets"),
    ("SIGNED_CHAR",
     re.compile(r"\bchar\s+\w+\s*=\s*-|\bif\s*\(\s*\w+\s*<\s*0\s*\).{0,30}char", re.I),
     "plain `char` signedness differs between platforms (ARM vs x86)"),
    ("TIME_32BIT",
     re.compile(r"\b(?:unsigned\s+)?long\s+\w*time\w*\s*[;,)]|\btime_t\b.{0,40}\blong\b", re.I),
     "time held in a platform-width integer; Y2038 / representation change"),
    ("INT_OVERFLOW_RELIANCE",
     re.compile(r"-fwrapv|\boverflow\b.{0,30}\bwrap|wraps?\s+around", re.I),
     "behaviour depends on signed-overflow semantics, which are undefined in C"),
]


def scan_body(tree: pathlib.Path):
    hits = {}
    for p in tree.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT:
            continue
        if ".git" in p.relative_to(tree).parts:
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for name, rx, _why in PATTERNS:
            m = rx.search(txt)
            if m:
                line = txt[max(0, m.start() - 60):m.end() + 60].replace("\n", " ").strip()
                hits.setdefault(name, {"files": 0, "example_file": str(p.relative_to(tree)).replace("\\", "/"),
                                       "example": line[:160]})
                hits[name]["files"] += 1
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    rows = []
    sp = vault.specimen_dir("_").parent
    for d in sorted(sp.iterdir()):
        if not (d / "record.json").exists():
            continue
        body = vault.body_dir(d.name) / "upstream"
        if not body.exists():
            continue
        hits = scan_body(body)
        if hits:
            rows.append({"specimen_id": d.name, "patterns": sorted(hits), "detail": hits})

    tally = {}
    for r in rows:
        for p in r["patterns"]:
            tally[p] = tally.get(p, 0) + 1

    # the sharpest signal: the exact defect class MD5 exhibited
    sharp = [r["specimen_id"] for r in rows if "WORD_WIDTH_TYPEDEF" in r["patterns"]]

    doc = {"schema": "techne.fossil.env_assumption_census/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "scanned_specimens": sum(1 for d in sp.iterdir() if (d / "record.json").exists()),
           "specimens_with_any_pattern": len(rows),
           "by_pattern": tally,
           "sharpest_candidates_word_width_typedef": sharp,
           "patterns": [{"name": n, "regex": rx.pattern, "why": w} for n, rx, w in PATTERNS],
           "note": "Presence of a pattern is NOT a defect. ENDIANNESS especially usually means the authors "
                   "handled byte order deliberately. Only a two-world TEST can show correctness actually "
                   "depends on the environment; this census only says where to look.",
           "rows": rows}
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("scanned %d specimens; %d carry at least one pattern" % (doc["scanned_specimens"], len(rows)))
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print("  %-24s %d" % (k, v))
    print("\nSHARPEST (same defect class as md5-rfc1321):", sharp or "NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
