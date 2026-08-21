# ATTACK CAT-MATH-0316 — amicable pairs to 1e7 (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P60) | Code: attack_0067_0316.py | Data: attack_0067_0316_results.json
Grounding: infinitude of amicable pairs OPEN; Erdos density-0 — untouched here.

Pre-stated readings: REVIEWER-RECONCILED (standard ~108 / both-bounded 100 / delta =
exactly 8 boundary pairs) / COUNT-SURPRISE (investigate first).

Result: with the sigma sieve at 1e8, max s(a) for a <= 1e7 is 35,752,992 — INSIDE the
sieve (partner headroom MEASURED; the P59 out-of-range factorization design dissolved
via range headroom, the cheapest possible resolution). Counts: standard convention
(smaller member <= 1e7) = 108 EXACT; both-members-bounded = 100; boundary pairs
(a <= 1e7 < b) = 8, listed in the results json. All three reviewer numbers reproduced.
The remembered ~108 was right; the P49 spec's own wording was the false-alarm source —
as the reviewer diagnosed.

NOT claimed: nothing about infinitude; the count certifies convention + harness, and
the density-0 frame means no finite count is evidence in either direction.

Trace-vector: problem_id CAT-MATH-0316 | operations [sigma-sieve, dual-convention-count,
measured-partner-headroom, boundary-pair-listing] | kill_pattern none | residue: when
a range extension is cheap, MEASURE the headroom before building the out-of-range
machinery — the design point evaporated for the cost of one max()
