"""
Mechanical structural profile of the four frontier lists.

Run BEFORE any hand classification of L1/L2, so the preregistered prediction
is based on structure (counts over regexes) and not on content (row verdicts).
No judgement anywhere in this file. Counts only. Deterministic.

Usage (from repo root):
    python aporia/q100/probes/structure_profile.py
"""
import json
import re
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

LISTS = [
    ("L1", "REGISTRY.jsonl"),
    ("L2", "REGISTRY_L2.jsonl"),
    ("L3", "REGISTRY_L3.jsonl"),
    ("L4", "REGISTRY_L4.jsonl"),
]

# --- the frozen boundary-token proxy, reproduced verbatim from the L3 pass ---
BOUNDARY = re.compile(
    r"\b(zero|100\s*%|exact|exactly|perfect|perfectly|infinite|never|1\.0)\b", re.I
)

# --- universal quantification in the T1 arm ---
UNIVERSAL = re.compile(r"\b(for all|all possible|every|arbitrary|any valid)\b", re.I)

# --- counterexample-hunt discipline in the T3 arm ---
CEX = re.compile(
    r"\b(counterexample|counter-example|fail if found|show a case|exhibit a|"
    r"find a case|adversarial case|or disprove|lower bound)\b", re.I
)

# --- an explicit two-sided band: a PASS number and a FAIL number ---
BAND = re.compile(r"\b(pass|fail|progress)\b", re.I)


def test_text(row):
    """Concatenated test text, or None when the registry did not retain it."""
    parts = [row.get("t1"), row.get("t2"), row.get("t3")]
    if all(p is None for p in parts):
        return None
    return " || ".join(p or "" for p in parts)


def main():
    print("STRUCTURAL PROFILE OF THE FOUR LISTS")
    print("mechanical, no judgement, test text only\n")
    print(f"{'list':6} {'rows':>5} {'text?':>6} {'bound':>7} {'univ':>7} {'cex':>7} {'band':>7}")
    for name, fn in LISTS:
        path = os.path.join(BASE, fn)
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        texts = [test_text(r) for r in rows]
        have = [t for t in texts if t is not None]
        n = len(rows)
        if not have:
            print(f"{name:6} {n:5d} {'NO':>6} {'--':>7} {'--':>7} {'--':>7} {'--':>7}")
            continue
        b = sum(1 for t in have if BOUNDARY.search(t))
        u = sum(1 for r in rows if r.get("t1") and UNIVERSAL.search(r["t1"]))
        c = sum(1 for r in rows if r.get("t3") and CEX.search(r["t3"]))
        d = sum(1 for t in have if len(BAND.findall(t)) >= 2)
        f = lambda k: f"{100.0*k/len(have):.0f}%"
        print(f"{name:6} {n:5d} {'yes':>6} {f(b):>7} {f(u):>7} {f(c):>7} {f(d):>7}")

    print("\nRETENTION AUDIT -- can each list's verdict be re-derived from the repo?")
    for name, fn in LISTS:
        path = os.path.join(BASE, fn)
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        has_q = sum(1 for r in rows if r.get("question"))
        has_t = sum(1 for r in rows if test_text(r) is not None)
        has_v = sum(1 for r in rows if r.get("_gate_verdict"))
        print(f"  {name}: rows={len(rows):3d}  full_question={has_q:3d}  "
              f"test_text={has_t:3d}  gate_verdict={has_v:3d}")


if __name__ == "__main__":
    main()
