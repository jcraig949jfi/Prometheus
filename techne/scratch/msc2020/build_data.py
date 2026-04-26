"""Build prometheus_math/databases/_msc2020_data.py from the AMS MSC2020 CSV.

Source: https://msc2020.org/MSC_2020.csv (downloaded 2026-04-25).

Output: a Python module embedding three flat dicts keyed by canonical code:
  - TOP:      "11" -> "Number theory"                              (63 entries)
  - SUBJECT:  "11G" -> "Arithmetic algebraic geometry ..."          (534 entries)
  - LEAF:     "11G05" -> "Elliptic curves over global fields"       (6006 entries)
                "11-01" -> "Introductory exposition ..."

The CSV uses "11-XX" for top-level, "11Gxx" for 3-char subjects, "11G05"
or "11-01" for 5-char leaves. We normalize to bare codes (strip -XX and
xx suffixes) and clean the descriptions of LaTeX-y cross-reference
annotations like `[See also 14H52]` and `\{For X, see Y\}`, while
preserving the core text exactly as published.

Run:
    python build_data.py > .../databases/_msc2020_data.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).with_name("MSC_2020.csv")
OUT_PATH = Path(__file__).resolve().parents[3] / "prometheus_math" / "databases" / "_msc2020_data.py"


_RX_TOP = re.compile(r"^(\d\d)-XX$")
_RX_SUBNUM = re.compile(r"^(\d\d)-(\d\d)$")  # 11-01
_RX_SUBJ = re.compile(r"^(\d\d)([A-Z])xx$")  # 11Gxx
_RX_LEAF = re.compile(r"^(\d\d)([A-Z])(\d\d)$")  # 11G05


def clean_description(text: str) -> str:
    """Strip the LaTeX-ish cross-reference annotations.

    The CSV emits things like:
        "Elliptic curves over global fields [See also 14H52]"
        "Methodology of mathematics \\{For mathematics education, see 97-XX\\}"
        "\\(K\\)-theory [See also 16E20, 18F25]"
        "Number theory"

    We keep the leading text up to the first `[` or `\\{`, then trim. The
    resulting strings are human-readable and stable for substring search.
    """
    s = text.strip()
    # Strip trailing \{...\} cross-reference (escaped braces in CSV)
    s = re.sub(r"\s*\\\{[^{}]*\\?\}.*$", "", s)
    # Strip trailing [See also ...]
    s = re.sub(r"\s*\[See also[^\]]*\].*$", "", s, flags=re.IGNORECASE)
    # Strip trailing [Consider also ...]
    s = re.sub(r"\s*\[Consider[^\]]*\].*$", "", s, flags=re.IGNORECASE)
    # Tidy escaped LaTeX math: \(K\)-theory -> K-theory ; \(>1\) -> >1
    s = re.sub(r"\\\((.*?)\\\)", r"\1", s)
    # Tidy escaped braces left over: \{ -> {  \} -> }
    s = s.replace("\\{", "{").replace("\\}", "}")
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build():
    rows = []
    with CSV_PATH.open("r", encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append((row["code"], row["description"]))

    top = {}      # "11" -> desc
    subject = {}  # "11G" -> desc
    leaf = {}     # "11G05" or "11-01" -> desc

    for code, desc in rows:
        d = clean_description(desc)
        m = _RX_TOP.match(code)
        if m:
            top[m.group(1)] = d
            continue
        m = _RX_SUBJ.match(code)
        if m:
            subject[m.group(1) + m.group(2)] = d
            continue
        m = _RX_SUBNUM.match(code)
        if m:
            leaf[code] = d
            continue
        m = _RX_LEAF.match(code)
        if m:
            leaf[code] = d
            continue
        # If we get here, the CSV contains a code shape we didn't anticipate.
        raise RuntimeError(f"Unrecognized MSC code shape: {code!r}")

    return top, subject, leaf


def emit(top, subject, leaf, out):
    out.write('"""MSC2020 hierarchy — embedded snapshot of the AMS classification.\n\n')
    out.write("Source: https://msc2020.org/MSC_2020.csv (AMS / zbMATH joint maintenance).\n")
    out.write("Snapshot date: 2026-04-25.\n\n")
    out.write("Three flat dicts keyed by canonical code:\n")
    out.write(f"    TOP     — {len(top)} entries, 2-character codes (e.g. '11' -> 'Number theory').\n")
    out.write(f"    SUBJECT — {len(subject)} entries, 3-character codes (e.g. '11G' -> 'Arithmetic ...').\n")
    out.write(f"    LEAF    — {len(leaf)} entries, 5-character codes (e.g. '11G05', '00-01').\n\n")
    out.write("The CSV uses '11-XX' for top, '11Gxx' for subject, '11G05' / '11-01' for\n")
    out.write("leaves; this module strips the redundant suffixes and trims the\n")
    out.write("descriptions of bracketed cross-reference annotations (the public\n")
    out.write("module API still emits raw cross-references in `extra` if needed).\n")
    out.write('"""\n')
    out.write("from __future__ import annotations\n\n")

    out.write("# 2-character top-level subjects.\n")
    out.write("TOP: dict[str, str] = {\n")
    for k in sorted(top):
        out.write(f"    {k!r}: {top[k]!r},\n")
    out.write("}\n\n")

    out.write("# 3-character subject codes (e.g. '11G' = 'Arithmetic algebraic geometry').\n")
    out.write("SUBJECT: dict[str, str] = {\n")
    for k in sorted(subject):
        out.write(f"    {k!r}: {subject[k]!r},\n")
    out.write("}\n\n")

    out.write("# 5-character leaf codes (the bulk of the MSC2020 hierarchy).\n")
    out.write("LEAF: dict[str, str] = {\n")
    for k in sorted(leaf):
        out.write(f"    {k!r}: {leaf[k]!r},\n")
    out.write("}\n")


if __name__ == "__main__":
    top, subject, leaf = build()
    print(f"TOP: {len(top)}", file=sys.stderr)
    print(f"SUBJECT: {len(subject)}", file=sys.stderr)
    print(f"LEAF: {len(leaf)}", file=sys.stderr)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        emit(top, subject, leaf, f)
    print(f"Wrote {OUT_PATH}", file=sys.stderr)
