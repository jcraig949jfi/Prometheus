"""Negative control for the B' oracle: does the admission path reject FALSE claims?

B' admitted 24/24 on its first clean run. A 100% admission rate is exactly the
shape a broken oracle produces — a checker that always returns True, or an
admission path that never consults the checker, would look identical from the
outside. Standing order: build the null that would produce the same signal by
accident, before trusting the signal.

So: ask the SAME author model for plausible-but-FALSE claims with honest
checkers, and push them through the SAME `_run_checker` + admission rule. If the
oracle has teeth, admission here is 0 and every item reports oracle_verdict=False
via an executed counterexample search. If anything is admitted, the oracle is
broken and the 24 admissions above mean nothing.

Usage:
    PYTHONPATH=. python harmonia/experiments/bprime_negative_control.py
"""
from __future__ import annotations

import json
from pathlib import Path

from harmonia.experiments.bprime_generate import (
    EXCLUDED,
    _call_model,
    _parse_json_array,
    _run_checker,
)

OUT_PATH = Path(__file__).resolve().parent / "bprime_negative_control.json"

PROMPT = """You are building a NEGATIVE CONTROL for a benchmark of true mathematical claims.

Produce exactly 8 claims that are FALSE, but plausibly-worded enough that a
careless reader would accept them. Classic near-miss errors are ideal: a theorem
with a dropped hypothesis, a bound off by one, an identity that holds for small
cases and then fails, a converse that does not hold.

Requirements:
1. Every claim must be genuinely FALSE. This is a control set; falsity is the point.
2. Each must have a counterexample findable by exhaustive search over a SMALL
   bounded domain.
3. Avoid these areas: {excluded}.
4. Vary the domain (graphs, combinatorics, linear algebra, real inequalities,
   number theory, sets/functions) and the logical shape.
5. The checker must be HONEST: it searches for a counterexample and returns True
   iff none is found. Do NOT write a checker that just returns False. Since the
   claims are false, an honest checker will return False by finding a real
   counterexample.

Return STRICT JSON, an array of exactly 8 objects with keys:
  "statement" : self-contained natural-language statement of the FALSE claim
  "domain"    : short domain tag
  "checker"   : Python 3 source defining `def check() -> bool:` that exhaustively
                searches a small bounded domain and returns True iff no
                counterexample is found. Only `math`, `itertools`, `fractions`.
                Must run in well under 5 seconds.

Output ONLY the JSON array. No prose, no markdown fences.
"""


def main() -> int:
    items = _parse_json_array(_call_model(PROMPT.format(excluded=EXCLUDED)))
    results = []
    admitted = 0
    for item in items:
        stmt, checker = item.get("statement"), item.get("checker")
        verdict, note = _run_checker(checker or "")
        # The admission rule under test is exactly B''s: admit iff verdict is True.
        would_admit = verdict is True
        admitted += would_admit
        results.append({
            "domain": item.get("domain"), "statement": stmt,
            "oracle_verdict": verdict, "oracle_note": note,
            "would_admit": would_admit,
        })
        flag = "ADMITTED (oracle FAILED)" if would_admit else "rejected"
        print(f"  [{str(item.get('domain'))[:20]:20s}] verdict={str(verdict):5s} {flag}")
        print(f"      {str(stmt)[:100]}")

    n = len(results)
    unusable = sum(1 for r in results if r["oracle_verdict"] is None)
    print(f"\nfalse claims tested : {n}")
    print(f"correctly rejected  : {n - admitted}")
    print(f"wrongly admitted    : {admitted}")
    print(f"unusable checkers   : {unusable}  (fail-closed; not evidence either way)")
    verdict = "PASS — oracle rejects false claims" if admitted == 0 else "FAIL — oracle admits falsehoods"
    print(f"CONTROL: {verdict}")

    OUT_PATH.write_text(json.dumps({
        "purpose": "negative control on the B' admission path",
        "n": n, "wrongly_admitted": admitted, "unusable_checkers": unusable,
        "verdict": verdict, "items": results,
    }, indent=2), encoding="utf-8")
    print(f"written: {OUT_PATH}")
    return 0 if admitted == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
