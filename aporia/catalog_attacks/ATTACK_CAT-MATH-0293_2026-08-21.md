# ATTACK CAT-MATH-0293 — Wieferich primes (CALIBRATION, spec ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P59) | Code: attack_0293_0306.py | Data: attack_0293_0306_results.json

Pre-stated readings: EXACT-SET ({1093, 3511}, nothing else) / MISMATCH (instrument fail
— the search is exhaustive to 6.7e15 in the literature with only these two).

Result: sweep of all primes p <= 1e7 for 2^(p-1) = 1 mod p^2 returns EXACTLY
[1093, 3511] in 5s — reviewer reproduced. Modular-exponentiation harness certified
against a known-sparse target.

CALIBRATION: says nothing about the Wieferich infinitude question (open in both
directions — infinitude of Wieferich AND of non-Wieferich primes are both unproven,
the latter conditional on abc).

Trace-vector: problem_id CAT-MATH-0293 | operations [modpow-sweep, exact-set-match] |
kill_pattern none | residue: none beyond the certification
