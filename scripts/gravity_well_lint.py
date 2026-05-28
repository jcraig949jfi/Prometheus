"""Gravity-well lint — flag publication-ladder vocabulary in commits + docs.

Per Erebos Doctrine v1.0 (pivot/erebos_doctrine_v1_2026-05-27.md)
§"counter-discipline rules". Run on commit messages, finding docs,
synthesis docs, whitepapers BEFORE pushing. Flag (do not block)
language that pulls the substrate's framing back into the
publication-ladder gravity well.

Why FLAG, not BLOCK: discipline has to come from the team's eyes.
A blocker becomes a bypass. A flag becomes a conversation.

Usage:
  python scripts/gravity_well_lint.py <file_or_dir>
  python scripts/gravity_well_lint.py --commit-msg <file>
  python scripts/gravity_well_lint.py --recent-commits 10
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


# Banned phrases (case-insensitive). Each entry: (phrase, why-it's-a-warning).
BANNED_PHRASES = [
    ("novel mathematical finding", "publication-ladder framing"),
    ("publishable result", "publication-ladder framing"),
    ("publishable claim", "publication-ladder framing"),
    ("literature-grade", "publication-ladder framing"),
    ("literature grade", "publication-ladder framing"),
    ("primary-literature submission", "publication-ladder framing"),
    ("primary literature submission", "publication-ladder framing"),
    ("peer-reviewable", "publication-ladder framing"),
    ("peer reviewable", "publication-ladder framing"),
    ("would be reported in journals", "publication-ladder framing"),
    ("would be reported in primary literature",
     "publication-ladder framing"),
    ("submit to arxiv", "publication-ladder framing (per feedback_exploration_not_papers)"),
    ("ready for publication", "publication-ladder framing"),
    ("beats the benchmark", "benchmark-ladder framing (Layer 1 evaluator misuse)"),
    ("SOTA", "benchmark-ladder framing (Layer 1 evaluator misuse)"),
    ("state-of-the-art", "benchmark-ladder framing (Layer 1 evaluator misuse)"),
    # Soft warnings (lower priority)
    ("novel discovery", "review framing — is this a substrate finding (Layer 2 contribution) or a Layer-1 result?"),
    ("breakthrough", "review framing — too close to publication-ladder vocabulary"),
]

# Phrases that are TYPICALLY GRAVITY-WELL but might be legitimate
# (used in critique or in describing what the project IS NOT).
SOFT_FLAGS = [
    ("paper", "ensure usage is in 'NOT a project to write papers' framing, not 'we should write a paper'"),
    ("publication", "ensure usage is critique / counter-discipline, not aspiration"),
    ("benchmark", "Layer 1 evaluator — ensure not treated as substrate value criterion"),
]


def lint_text(text: str, source: str = "<input>") -> list[dict]:
    """Return list of {line_no, phrase, why, severity, line_content} hits."""
    hits: list[dict] = []
    for i, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        for phrase, why in BANNED_PHRASES:
            if phrase.lower() in lower:
                hits.append({
                    "source": source,
                    "line_no": i,
                    "phrase": phrase,
                    "why": why,
                    "severity": "WARN",
                    "line_content": line.strip()[:200],
                })
        for phrase, why in SOFT_FLAGS:
            # Use word boundary for soft flags to reduce false positives
            if re.search(r"\b" + re.escape(phrase) + r"\b", lower):
                hits.append({
                    "source": source,
                    "line_no": i,
                    "phrase": phrase,
                    "why": why,
                    "severity": "SOFT",
                    "line_content": line.strip()[:200],
                })
    return hits


def lint_file(path: Path) -> list[dict]:
    """Lint a single file."""
    if not path.exists() or not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    return lint_text(text, source=str(path))


def lint_dir(path: Path, extensions: tuple = (".md", ".py")) -> list[dict]:
    """Lint all files matching extensions in a directory."""
    hits: list[dict] = []
    for ext in extensions:
        for p in path.rglob(f"*{ext}"):
            hits.extend(lint_file(p))
    return hits


def lint_recent_commits(n: int = 10) -> list[dict]:
    """Lint the last N commit messages."""
    try:
        out = subprocess.check_output(
            ["git", "log", f"-{n}", "--format=%H%n%B%x00"],
            text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        print(f"git log failed: {e}")
        return []
    hits: list[dict] = []
    for chunk in out.split("\x00"):
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        if not lines:
            continue
        sha = lines[0][:12]
        body = "\n".join(lines[1:])
        hits.extend(lint_text(body, source=f"commit {sha}"))
    return hits


def format_hit(hit: dict) -> str:
    sev = hit["severity"]
    marker = "!!" if sev == "WARN" else "..."
    return (
        f"  {marker} {sev}: {hit['source']}:{hit['line_no']}  "
        f"phrase={hit['phrase']!r}\n"
        f"      why: {hit['why']}\n"
        f"      line: {hit['line_content']!r}"
    )


# Canonical docs that LIST the banned phrases by design (the doctrine,
# the counter-discipline memory files, the gravity-well lint itself).
# Linting these would produce noise; they're the SOURCE of the rules.
EXEMPT_PATH_PATTERNS = [
    "erebos_doctrine_v1",
    "feedback_llm_convergence_is_gravity_amplifier",
    "feedback_failure_metabolization_doctrine",
    "feedback_residue_must_be_navigable_not_logged",
    "feedback_anti_gravitational_well",
    "feedback_exploration_not_papers",
    "gravity_well_lint.py",
]


def is_exempt(path_str: str) -> bool:
    return any(p in path_str for p in EXEMPT_PATH_PATTERNS)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Gravity-well lint per Erebos Doctrine v1.0"
    )
    ap.add_argument("target", nargs="?", default=None,
                    help="File or directory to lint")
    ap.add_argument("--commit-msg", type=str, default=None,
                    help="Path to a commit message file (e.g., .git/COMMIT_EDITMSG)")
    ap.add_argument("--recent-commits", type=int, default=None,
                    help="Lint the last N commit messages")
    ap.add_argument("--only-warn", action="store_true",
                    help="Suppress SOFT flags; only show WARN-level hits")
    args = ap.parse_args()

    hits: list[dict] = []
    if args.commit_msg:
        hits = lint_file(Path(args.commit_msg))
    elif args.recent_commits:
        hits = lint_recent_commits(args.recent_commits)
    elif args.target:
        target = Path(args.target)
        if target.is_dir():
            hits = lint_dir(target)
        else:
            hits = lint_file(target)
    else:
        print("Specify a target / --commit-msg / --recent-commits")
        return 2

    # Skip canonical docs that define the banned phrases by design
    hits = [h for h in hits if not is_exempt(h["source"])]

    if args.only_warn:
        hits = [h for h in hits if h["severity"] == "WARN"]

    if not hits:
        print("OK: no gravity-well vocabulary detected.")
        return 0

    print(f"FOUND {len(hits)} gravity-well hit(s):\n")
    for h in hits:
        print(format_hit(h))
        print()

    n_warn = sum(1 for h in hits if h["severity"] == "WARN")
    n_soft = sum(1 for h in hits if h["severity"] == "SOFT")
    print(f"\nSummary: {n_warn} WARN, {n_soft} SOFT.")
    print(
        "\nFlags are advisory. Discipline comes from the team's eyes.\n"
        "Per Erebos Doctrine v1.0 §counter-discipline: review each hit\n"
        "and decide whether the language pulls the substrate's framing\n"
        "into the publication-ladder gravity well."
    )
    # Exit code: 0 = clean, 1 = WARN-level hits, 0 = only SOFT
    return 1 if n_warn else 0


if __name__ == "__main__":
    sys.exit(main())
