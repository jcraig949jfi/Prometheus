"""PARADIGM-P25 worked example — Pivotal Negative Result, executed.

The paradigm's move: FIND the unexpected counterexample that kills a
widely-believed proposition and reorients the field. Executable instance:
Euler's sum-of-powers conjecture (1769: at least k k-th powers are needed to
sum to a k-th power) — believed for ~200 years, killed by machine search.

Legs:
  A. VERIFY both historic kills in EXACT integer arithmetic:
     k=5 (Lander-Parkin 1966): 27^5 + 84^5 + 110^5 + 133^5 = 144^5
     k=4 (Elkies/Frye 1988):  95800^4 + 217519^4 + 414560^4 = 422481^4
     (citations unverified-pending-fetch as attributions; the ARITHMETIC is
     verified here, which is what a counterexample IS).
  B. REDISCOVER the k=5 kill by OUR OWN search that does not know the
     answer: meet-in-the-middle over pair-sums a^5+b^5 (a<=b<=N), N=150 —
     hash all pair sums, then for each e and each pair-sum s test e^5 - s in
     the hash. The search reports EVERY solution in range; finding the
     Lander-Parkin quadruple (and nothing spurious) is the leg's verdict.
  C. REORIENTATION typed: the kill reformulates 'how many k-th powers
     suffice' — the negative result's product is the better question
     (Waring-type), recorded as the paradigm's payoff.

Pre-stated readings (BEFORE run):
  KILL-REDISCOVERED  A: both identities exact; B: the search finds the
                     (27,84,110,133;144) solution (up to ordering) and every
                     reported solution re-verifies exactly.
  SEARCH-FAULT       instrument-first: hash collisions across pair-sums
                     (store lists, not single values), a<=b<=c<=d ordering
                     dedup, integer overflow (python ints exempt).
"""
from __future__ import annotations
import json
import pathlib
from collections import defaultdict

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p25_results.json"

# --- A: exact verification of the historic kills ------------------------------
lp = (27, 84, 110, 133, 144)
assert sum(x ** 5 for x in lp[:4]) == lp[4] ** 5, "Lander-Parkin identity FAILS"
ef = (95800, 217519, 414560, 422481)
assert sum(x ** 4 for x in ef[:3]) == ef[3] ** 4, "Elkies-Frye identity FAILS"
print("A. both historic counterexamples verify EXACTLY (k=5 and k=4)", flush=True)

# --- B: rediscovery by blind search ------------------------------------------
N = 150
pair_sums = defaultdict(list)
for a in range(1, N + 1):
    a5 = a ** 5
    for b in range(a, N + 1):
        pair_sums[a5 + b ** 5].append((a, b))

solutions = set()
for e in range(2, N + 1):
    e5 = e ** 5
    for s, pairs_ab in pair_sums.items():
        rem = e5 - s
        if rem < s:                       # enforce s <= rem to halve work; dedup below
            continue
        if rem in pair_sums:
            for (a, b) in pairs_ab:
                for (c, d) in pair_sums[rem]:
                    quad = tuple(sorted((a, b, c, d)))
                    if sum(x ** 5 for x in quad) == e5:
                        solutions.add((quad, e))
print(f"B. blind search a<=b<=c<=d<=e<={N}: {len(solutions)} solution(s) found:", flush=True)
ok_all = True
found_lp = False
for quad, e in sorted(solutions):
    exact = sum(x ** 5 for x in quad) == e ** 5
    ok_all &= exact
    found_lp |= (quad == (27, 84, 110, 133) and e == 144)
    print(f"   {quad} -> {e}^5  exact={exact}", flush=True)

verdict = "KILL-REDISCOVERED" if (found_lp and ok_all) else "SEARCH-FAULT"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "exact verification of both historic Euler-conjecture kills + blind meet-in-the-middle rediscovery to N=150 (every reported solution re-verified exactly)",
    "historic_verified": {"lander_parkin_k5": list(lp), "elkies_frye_k4": list(ef)},
    "search_N": N, "solutions_found": [[list(q), e] for q, e in sorted(solutions)],
    "verdict": verdict,
    "reorientation": "the kill's product is the better question: minimal number of k-th powers (Waring-type reformulation) — the negative result as reorienting lemma"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
