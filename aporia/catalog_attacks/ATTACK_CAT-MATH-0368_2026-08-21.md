# ATTACK CAT-MATH-0368 — Ankeny-Artin-Chowla to 1e5 (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P61) | Code: attack_0060_0368.py | Data: attack_0060_0368_results.json
Grounding: AAC is OPEN; verified to 2e11 in literature [the spec's VERIFY-AT-ATTACK
flag stands — this range is far inside it].

Pre-stated readings: ANCHOR-PASS (sympy cross-check + classical u=1 at 5/13/29) then
AAC-HOLDS (no p | u) / VIOLATION (instrument-bug-first at extreme prior).

Method (corrections binding): exact CF of sqrt(p) for the Z[sqrt p] Pell solution,
then EXACT cube-root descent to the maximal-order unit (t+u*sqrt(p))/2 — candidate
from 60-digit floating cbrt, verified by exact integer identity
((t+u*w)/2)^3 = +-(x0+y0*w); fallback eps_max = eps_Z when no odd descent exists.
Maximal-order convention stated (the reviewer measured it verdict-neutral in range).
Mirror enumeration demoted to cross-check per the disposition.

Result:
- Anchors: 20/20 agreement with sympy diop_DN(p, +-4) minimal solutions; classical
  u = 1 at p = 5, 13, 29 confirmed.
- Sweep: all 4,783 primes p = 1 mod 4 below 1e5 — ZERO violations (p never divides u).
  Total runtime ~1s (the CF+descent is fast).
- Empirical product: u mod p lands in the lowest decile for 15.7% of primes vs 10%
  uniform. FLAGGED, NOT CLAIMED: the simplest explanation is small-u prevalence
  (u = 1 and other tiny units reduce to themselves), which inflates the low decile
  without any u-mod-p structure. Decomposing small-u vs reduced-mod-p is the
  pre-registered next question if anyone pulls this thread; no structure claim is made.

NOT claimed: AAC's truth (range is 6 orders inside the literature bound); any
u mod p distributional structure (simplest explanation untested).

Trace-vector: problem_id CAT-MATH-0368 | operations [exact-cf-pell, exact-cube-root-descent,
sympy-anchor-crosscheck, distribution-flag-with-simplest-explanation] | kill_pattern none |
residue: floating candidate + exact verification is the safe pattern for unit computations —
never trust the float, never brute-force the explosion
