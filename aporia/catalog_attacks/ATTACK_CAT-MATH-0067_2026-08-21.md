# ATTACK CAT-MATH-0067 — Artin primitive-root density, base 2 (spec ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P60) | Code: attack_0067_0316.py | Data: attack_0067_0316_results.json
Grounding: Artin's conjecture OPEN unconditionally (Hooley proved it under GRH;
Heath-Brown: at least one of 2,3,5 works, non-constructively) — untouched here.

Pre-stated readings: REVIEWER-REPRODUCED (0.373908 at 1e7) + CONVERGENT (toward the
product-computed A across decades to 1e8) / DRIFT / MISMATCH-first.

Instrument event: the first run's decade labels were shifted one decade (digit-count
binning bug: len(str(p))-1 put 7-digit primes in the 1e6 bucket). Caught by noticing
the reviewer's 1e7 value appearing at the 1e6 label; fixed and rerun before any
reading fired. Same shape as the P52 event: the cross-seat number acted as the
calibration standard.

Result: A computed from its product over primes to 1e7 = 0.3739558158. Cumulative
density of primes with 2 a primitive root: 0.375665 (1e5), 0.373785 (1e6), 0.373908
(1e7 — reviewer EXACT), 0.373991 (1e8). Ratio to A: 1.00457, 0.99954, 0.99987,
1.00009 — oscillating convergence, |ratio-1| <= 1e-4 by 1e8. Reading: CONVERGENT.
The uncorrected A is correct for base 2 (2 is not a perfect power and 2 mod 4 != 1 —
no correction factor), per the reviewer's disposition note.

NOT claimed: nothing about Artin's conjecture — in-range density behavior only.

Trace-vector: problem_id CAT-MATH-0067 | operations [spf-sieve-factoring,
ord-test-via-maximal-divisors, product-computed-constant, decade-cumulative] |
kill_pattern: label-shift caught pre-reading | residue: digit-count binning is an
off-by-one magnet — bucket by digit COUNT, and cross-check one bucket against a
known external value before reading any of them
