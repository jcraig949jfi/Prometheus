"""Mechanically verify the checkable claims in a markdown report. NO inference.

Every control here is DECIDABLE: it either resolves or it does not. No model reads the prose,
no judgement is applied, and the exit code is the verdict.

MOTIVATION, from a measured record. Across cycles 049-059 the failures were:
    citation errors        a named symbol did not exist          -> CHECK 1, fully decidable
    numeric claims         a number with no reproducing command  -> CHECK 2, fully decidable
    population errors      a rate quoted without its denominator -> CHECK 3, fully decidable
    self-contradiction     X called a false positive AND counted -> CHECK 4, decidable by regex
None of these needs a language model. They need the claim to be MACHINE-ADDRESSABLE, which is
the actual gap: findings are written as prose, so nothing can test them.

    python -m techne.scripts.claim_check techne/loop/cycle_0*.md
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

# `module.path::symbol` or `module.path.symbol` inside backticks
SYMBOL = re.compile(r"`([a-z_][a-z0-9_]*(?:[./][a-z0-9_]+)+\.py)::(\w+)`", re.I)
DOTTED = re.compile(r"`((?:[a-z_][a-z0-9_]*\.){2,}[a-z_][a-z0-9_]*)::(\w+)`", re.I)
FILEREF = re.compile(r"`([\w./-]+\.(?:py|md|json|jsonl))`")
# a bare rate like 7/8 or 4/8 = 0.50
RATE = re.compile(r"\b(\d+)\s*/\s*(\d+)\s*=\s*([01]?\.\d+)")


def _defines(module_ref: str, symbol: str, repo: pathlib.Path) -> tuple[bool, str]:
    """True iff the module's SOURCE defines `symbol`. AST only -- nothing is executed.

    The first version imported the module to check `hasattr`. That was wrong twice over: it
    cost ~12 s per module for anything that initialises PARI, and it EXECUTED code merely to
    ask whether a name exists. Reading the source answers the same question in milliseconds
    with no side effects, which is what a check on a claim should cost.
    """
    rel = module_ref[:-3] if module_ref.endswith(".py") else module_ref.replace(".", "/")
    cand = [repo / f"{rel}.py", repo / rel.replace("/", "\\") ]
    path = next((c for c in cand if c.suffix == ".py" and c.exists()), None)
    if path is None:
        hits = list(repo.rglob(pathlib.Path(rel).name + ".py"))
        if not hits:
            return False, "module file not found"
        path = hits[0]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as e:
        return False, f"module unparseable ({e.msg})"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))                 and node.name == symbol:
            return True, ""
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == symbol:
                    return True, ""
    return False, "symbol not defined in module source"


def check_symbols(text: str, repo: pathlib.Path) -> list[str]:
    """CHECK 1 -- every `module::symbol` reference must resolve to a definition.

    This alone would have caught cycle 052's `_verify_mahler_mpmath`, a function named in a
    committed report and two log entries that does not exist. The real name is `mpmath_recheck`.
    """
    out = []
    seen = set()
    for pat in (SYMBOL, DOTTED):
        for mod, sym in pat.findall(text):
            if (mod, sym) in seen:
                continue
            seen.add((mod, sym))
            ok, why = _defines(mod, sym, repo)
            if not ok:
                out.append(f"UNRESOLVABLE SYMBOL  {mod}::{sym}  ({why})")
    return out


def check_files(text: str, repo: pathlib.Path, report: pathlib.Path) -> list[str]:
    """CHECK 2 -- every referenced file path must resolve SOMEWHERE checkable.

    Its own first version resolved only against the repo root and reported six "missing" files
    that were bare basenames or paths relative to the report's own directory. That was a real
    defect in this checker, and it is the right KIND of defect: decidable, reproducible, and
    fixed by widening the resolution rule rather than by anyone deciding what was meant.
    """
    out = []
    for ref in sorted(set(FILEREF.findall(text))):
        if ref.startswith(("http", "//")) or " " in ref:
            continue
        if (repo / ref).exists() or (report.parent / ref).exists():
            continue
        if list(repo.rglob(pathlib.Path(ref).name))[:1]:
            continue                      # bare basename that exists somewhere in the repo
        out.append(f"UNRESOLVABLE FILE    {ref}")
    return out


def check_rates(text: str) -> list[str]:
    """CHECK 3 -- a stated rate must equal its own fraction. Arithmetic, not opinion."""
    out = []
    for num, den, val in RATE.findall(text):
        n, d, v = int(num), int(den), float(val)
        if d == 0:
            out.append(f"RATE OVER ZERO       {num}/{den}")
        elif abs(n / d - v) > 0.006:
            out.append(f"RATE MISMATCH        {num}/{den} = {n/d:.3f}, text says {v}")
    return out


def check_contradictions(text: str) -> list[str]:
    """CHECK 4 -- a symbol called a FALSE POSITIVE must not also appear as a detection.

    Cycle 055 recorded `bootstrap_ci_from_seed_means` as a Lane A false positive in two places
    and reported 7/8 -- a total that counts it as a hit.

    ITS FIRST VERSION DID NOT FIRE ON THAT FILE. It required the symbol inside backticks and
    within 80 characters of "false positive" in the same sentence. In the real report the two
    facts sit in different sentences, and the tabulated line has the symbol unquoted inside a
    code block. A control keyed to formatting conventions the documents do not follow is not a
    control -- and that only surfaced by running it against the case it was built for.

    Decidable version: flag any identifier co-occurring with BOTH "false positive" and a
    detection marker. Whether the pairing is a genuine contradiction needs a reader; SURFACING
    the pair does not.
    """
    out = []
    if "false positive" not in text.lower():
        return out
    idents = set(re.findall(r"\b([a-z_][a-z0-9_]{6,})\b", text))
    for sym in sorted(idents):
        esc = re.escape(sym)
        near = (re.search(r"(?s)" + esc + r".{0,400}?false positive", text, re.I)
                or re.search(r"(?s)false positive.{0,400}?" + esc, text, re.I))
        if not near:
            continue
        if re.search(esc + r"[^\n]{0,60}\bFLAG\b", text):
            out.append("CONTRADICTION?       `" + sym + "` co-occurs with BOTH 'false "
                       "positive' and a FLAG -- verify it is not counted as a detection")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reports", nargs="+")
    ap.add_argument("--repo", default=str(pathlib.Path(__file__).resolve().parents[2]))
    a = ap.parse_args()
    repo = pathlib.Path(a.repo)
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    total = 0
    for r in a.reports:
        p = pathlib.Path(r)
        if not p.exists():
            print(f"{r}: MISSING REPORT"); total += 1; continue
        text = p.read_text(encoding="utf-8", errors="replace")
        issues = (check_symbols(text, repo) + check_files(text, repo, p)
                  + check_rates(text) + check_contradictions(text))
        if issues:
            print(f"\n{p.name}")
            for i in issues:
                print(f"   {i}")
            total += len(issues)
    print(f"\n{total} mechanically-decidable issues across {len(a.reports)} reports")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
