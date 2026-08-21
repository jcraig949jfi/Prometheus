# ATTACK CAT-MATH-0287 — Hardy-Littlewood prime triplets (spec ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P55) | Code: attack_0287_0324.py | Data: attack_0287_0324_results.json

Pre-stated readings: REVIEWER-REPRODUCED (type ratio 1.00079) + EFF-CONSISTENT (+-2%
band under H3*li_3, band added per the disposition note) / EFF-DRIFT / MISMATCH-first.

Result:
- (0,2,6): 55,600 and (0,4,6): 55,556 to 1e8; type ratio 1.00079 — reviewer REPRODUCED
  exactly (reflection symmetry prediction: ratio -> 1).
- H3 = 2.858249 computed from its Euler product (9/2)*prod_{p>3} p^2(p-3)/(p-1)^3 over
  primes to 1e7 — no memory constants.
- Effective ratios obs/(H3*li_3): r026 0.793->1.0020, r046 0.822->1.0012 across
  1e4..1e8 — both inside the +-2% band from 1e7, converging monotonically in envelope.
  li_3 via u-substitution (the P52 quadrature lesson applied at authoring time, not
  discovered again).

Reading: REVIEWER-REPRODUCED + EFF-CONSISTENT. In-range empirical quality of the HL
triplet prediction; nothing about infinitude of prime triplets is claimed or claimable.

Trace-vector: problem_id CAT-MATH-0287 | operations [euler-product-constant,
sieve-triplet-extraction, u-substitution-li3, type-ratio-symmetry-check] |
kill_pattern none | residue: the li-lesson held a third time — it is now standing
instrument doctrine for every HL-family attack, no longer a per-attack discovery
