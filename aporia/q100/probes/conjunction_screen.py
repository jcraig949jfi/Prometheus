"""
The conjunction screen.

Derived from L4_GATE_REACHABILITY_2026-08-31.md section 2: eight rows were blocked by
a theorem the list never mentions, and they share one syntactic tell -- a PASS condition
CONJOINING two properties that a theorem says cannot co-occur. The defect lives in the
conjunction, not in the threshold, so the boundary-token regex cannot see it.

FROZEN 2026-09-01 under PREREG_L1_L2_GATE_REACHABILITY.md, committed UNRUN.

Scope limit, from the prereg section 0: runs over L1 and L2 only. L3 and L4 registries
retain no test text, so the screen cannot be scored against the very rows it was derived
from. Its calibration set is prose descriptions in a findings document.

Usage (from repo root):
    python aporia/q100/probes/conjunction_screen.py
"""
import json
import re
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

# Property terms, grouped. A hit requires two terms from DIFFERENT groups inside one
# test arm. Groups are the axes along which the known impossibility results cut.
GROUPS = {
    "completeness": [
        r"complete(?:ness)?", r"exhaustive", r"all (?:possible|valid) ",
        r"every (?:possible|valid) ", r"guaranteed to find",
    ],
    "termination": [
        r"terminat", r"halts?", r"decidable", r"always returns",
        r"bounded time", r"real[- ]time",
    ],
    "soundness": [
        r"sound(?:ness)?", r"zero false", r"no false positives", r"verified correct",
    ],
    "efficiency": [
        r"polynomial", r"poly[- ]time", r"linear time", r"sub[- ]exponential",
        r"efficient", r"tractable", r"o\(2\^", r"under (?:one|1) second",
    ],
    "exactness": [
        r"exact(?:ly)?", r"perfect(?:ly)?", r"100\s*%", r"\bzero\b", r"1\.0\b",
        r"optimal", r"ground[- ]truth recovery",
    ],
    "unboundedness": [
        r"unbounded", r"infinite", r"arbitrary(?:ily)? (?:long|large|deep|many)",
        r"open[- ]ended", r"indefinitely",
    ],
    "boundedness": [
        r"constant memory", r"fixed (?:size|budget|capacity)", r"bounded (?:memory|storage)",
        r"no (?:growth|forgetting)", r"same compute", r"equal compute",
    ],
    "robustness": [
        r"doubly robust", r"robust to arbitrary", r"mis-?specifi", r"worst[- ]case",
        r"adversarial",
    ],
    "generality": [
        r"domain[- ]independent", r"any domain", r"arbitrary (?:boolean|function|distribution)",
        r"all finite", r"universal",
    ],
}

# The pairs a theorem forbids. Ordered pairs of group names; a row fires only when a
# term from each side appears in the SAME test arm.
FORBIDDEN_PAIRS = [
    ("completeness", "termination"),    # decidability of an undecidable problem
    ("completeness", "efficiency"),     # complete search in polynomial time
    ("soundness", "completeness"),      # Godel, for a sufficiently strong system
    ("exactness", "efficiency"),        # exact solution to an NP-hard problem, fast
    ("unboundedness", "boundedness"),   # unbounded information in bounded storage
    ("robustness", "efficiency"),       # doubly robust AND efficient under bad nuisances
    ("generality", "exactness"),        # exact result for an arbitrary member of a huge class
    ("generality", "efficiency"),       # sample complexity over all Boolean functions
]

COMPILED = {g: [re.compile(p, re.I) for p in pats] for g, pats in GROUPS.items()}


def groups_present(text):
    return {g for g, pats in COMPILED.items() if any(p.search(text) for p in pats)}


def screen_row(row):
    """Return list of (arm, pair) hits for one row."""
    hits = []
    for arm in ("t1", "t2", "t3"):
        text = row.get(arm)
        if not text:
            continue
        present = groups_present(text)
        for a, b in FORBIDDEN_PAIRS:
            if a in present and b in present:
                hits.append((arm, f"{a}+{b}"))
    return hits


def main():
    total_rows = 0
    total_hits = 0
    for name, fn in [("L1", "REGISTRY.jsonl"), ("L2", "REGISTRY_L2.jsonl")]:
        path = os.path.join(BASE, fn)
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        print(f"\n=== {name} ({len(rows)} rows) ===")
        n = 0
        for r in rows:
            hits = screen_row(r)
            if hits:
                n += 1
                pairs = sorted({h[1] for h in hits})
                arms = sorted({h[0] for h in hits})
                verdict = r.get("_gate_verdict") or "UNLABELLED"
                print(f"  {r['id']}  arms={','.join(arms):12} {';'.join(pairs)}")
                print(f"        hand={verdict}")
        print(f"  -> {n}/{len(rows)} rows fire")
        total_rows += len(rows)
        total_hits += n
    print(f"\nTOTAL {total_hits}/{total_rows} rows fire across L1+L2")


if __name__ == "__main__":
    main()
