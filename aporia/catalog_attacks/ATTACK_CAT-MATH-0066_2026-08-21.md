# ATTACK CAT-MATH-0066 — prime-pair counts vs HL singular series (re-authored spec, ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P68) | Code: attack_0066_0137.py | Data: attack_0066_0137_results.json
Grounding: Polignac's conjecture OPEN (AA-058 adjacent: bounded gaps at 246 proven).
History: the ORIGINAL spec was REJECTED by the reviewer (consecutive-gap counts vs a
pair singular series — category mismatch firing at gap 8); this attack executes the
re-authored pair-count version the reviewer verified by execution.

Pre-stated readings: REVIEWER-REPRODUCED (N_2=440312, max|z|=0.84, zero rows >2sigma,
Poisson-scale tolerance per the reviewer's standing note) / MISMATCH-first.

Instrument event: MISMATCH FIRED — first run gave max|z|=541 (13 rows beyond 2sigma).
Root cause: the singular-series helper did not strip factor 2 before the odd-prime
loop (k=6 -> 1 instead of 2) — the SAME landmine class (sing_prod) the reviewer
deleted from the P51 template, re-created independently and caught within minutes by
the reviewer target. Fixed; the fix and its cause are in the code comment.

Result: N_2k(1e8) for k=1..50; N_2 = 440,312; ratios vs prod_{odd q|k}(q-1)/(q-2)
under z = (ratio/pred - 1)/sqrt(1/N_2k + 1/N_2): max |z| = 0.84, ZERO rows beyond
2 sigma — reviewer reproduced exactly. No pair class is missing (min N_2k well
populated); the HL singular-series ratios describe the pair counts at Poisson scale
across all 50 classes.

NOT claimed: nothing about Polignac's infinitude — in-range distributional agreement.

Trace-vector: problem_id CAT-MATH-0066 | operations [padded-sieve-pair-counts,
factor-2-stripped-singular-series, poisson-scale-z] | kill_pattern:
MISMATCH caught the sing-landmine recreation | residue: the sing_prod landmine class
is now twice-observed — factor-2 stripping belongs in a SHARED tested helper, not
per-attack rewrites (filed for the method bank)
