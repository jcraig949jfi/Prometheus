"""Rough shape census of @[simp]-family attribute sites in a mathlib4 checkout (Nyx, 2026-09-11).

For organ c01 (rule canonicalization): what fraction of tagged statements are NOT literal
equations, i.e. would be dropped by the ablation A9 (preprocess := identity)?

METHOD (declared so the number is read as what it is): enumerate every line matching
@[...simp...] under Mathlib/; sample N sites with a fixed seed; for each, take the text
from the attribute line to the first ':=' or '|' or 'where' (the statement), strip binders
before the last ':' at depth 0 as best a regex can, and classify the CONCLUSION by its
top-level connective in this order: '<->' / 'iff' -> IFF; leading 'not' or a top-level
'!=' -> NEG; a top-level '/\\' -> AND; a top-level '=' -> EQ; else OTHER (bare Prop, <=, etc).
Multi-line statements are handled by joining up to 12 following lines. This is a TEXT
census, not an elaboration; it over-counts EQ when '=' appears inside a binder and
mis-classifies anything the regex cannot bracket. Grade T1-LOCAL for the count of what the
regex saw; T3 for the inference that it approximates the elaborated shape.

Usage: python measure_simp_shapes.py <mathlib4 root> <N> <seed> > receipt.json
"""
from __future__ import annotations

import json
import random
import re
import subprocess
import sys
from pathlib import Path

ATTR = re.compile(r"@\[[^\]]*\bsimp\b")


def statement_after(lines, i):
    buf = []
    for j in range(i, min(i + 13, len(lines))):
        buf.append(lines[j])
        joined = " ".join(buf)
        if ":=" in joined or re.search(r"\bwhere\b", joined) or re.search(r"^\s*\|", lines[j]):
            break
    s = " ".join(buf)
    s = s.split(":=")[0]
    return s


def conclusion(stmt: str) -> str:
    # drop everything up to the LAST top-level ':' (binders end there)
    depth = 0
    last = -1
    for k, ch in enumerate(stmt):
        if ch in "([{⟨":
            depth += 1
        elif ch in ")]}⟩":
            depth -= 1
        elif ch == ":" and depth == 0 and k + 1 < len(stmt) and stmt[k + 1] != "=":
            last = k
    return stmt[last + 1:] if last >= 0 else stmt


def top_level_has(s: str, token: str) -> bool:
    depth = 0
    for k in range(len(s)):
        ch = s[k]
        if ch in "([{⟨":
            depth += 1
        elif ch in ")]}⟩":
            depth -= 1
        elif depth == 0 and s.startswith(token, k):
            return True
    return False


def classify(concl: str) -> str:
    c = concl.strip()
    if top_level_has(c, "↔") or top_level_has(c, " iff "):
        return "IFF"
    if c.startswith("¬") or top_level_has(c, "≠"):
        return "NEG"
    if top_level_has(c, "∧"):
        return "AND"
    if top_level_has(c, " = ") or top_level_has(c, "=") and not top_level_has(c, "≤") and not top_level_has(c, "≥"):
        return "EQ"
    return "OTHER"


def main(root: str, n: int, seed: int) -> None:
    files = sorted(Path(root, "Mathlib").rglob("*.lean"))
    sites = []
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except Exception:  # noqa: BLE001
            continue
        for i, ln in enumerate(lines):
            if ATTR.search(ln):
                sites.append((str(f.relative_to(root)), i))
    rnd = random.Random(seed)
    sample = rnd.sample(sites, min(n, len(sites)))
    counts = {"EQ": 0, "IFF": 0, "NEG": 0, "AND": 0, "OTHER": 0}
    examples = {k: [] for k in counts}
    for path, i in sample:
        lines = Path(root, path).read_text(encoding="utf-8").splitlines()
        stmt = statement_after(lines, i)
        cls = classify(conclusion(stmt))
        counts[cls] += 1
        if len(examples[cls]) < 3:
            examples[cls].append({"file": path, "line": i + 1, "conclusion": conclusion(stmt).strip()[:160]})
    sha = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    non_eq = sum(v for k, v in counts.items() if k != "EQ")
    out = {
        "method": "text census; see module docstring; NOT an elaboration",
        "mathlib4_sha": sha, "attribute_sites_total": len(sites), "sample_n": len(sample), "seed": seed,
        "counts": counts, "non_eq_fraction_in_sample": round(non_eq / len(sample), 3) if sample else None,
        "examples": examples,
        "grade": {"attribute_sites_total": "T1-LOCAL", "counts": "T1-LOCAL for what the regex saw", "shape_inference": "T3"},
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
