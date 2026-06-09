# Findings — Tiered Classification
## 2026-04-11 Session (65 challenges) + 2026-04-11 Battery Retest
## Tiers: Conjecture → Possible → Probable → Working Theory → Validated
## UPDATED after F1-F23 unified battery retest (2026-04-11)

---

## VALIDATED (cross-confirmed by independent mathematical identities)

*None from this session.* Charon's 23 rediscoveries (modularity theorem, Sato-Tate, Deuring mass, etc.) remain validated.

---

## WORKING THEORY (survived full battery + independent subset replication)

*None yet.*

---

## PROBABLE (survived full F1-F23 battery including Tier B)

**P2. Space group predicts Tc (eta²=0.45) but NOT band gap (eta²=0.095)** ✓ CONFIRMED
- F17: CONFOUND_ROBUST (sensitivity 0.20). F18: STABLE (CV ratio 0.52).
- 3,995 records. Eta²=0.4551 for Tc, 0.095 for band gap.
- **Only finding at PROBABLE tier after full F1-F23 retest.**
- The selectivity (Tc yes, band gap no) is the key puzzle.

**P3. Config enrichment 11.8x (detrended from 16.4x)** — NOT YET RETESTED
- F17: Survived after detrending by element energy scale (28% drop)
- Needs: Full F1-F23 retest with atomic number Z as confound

---

## POSSIBLE (survived initial measurement, kill attempts incomplete)

**P1 → S0. G2 conductor M4/M2^2 = 2.939** (downgraded from Probable)
- F15: DEVIATES_FROM_LOGNORMAL. F16: EQUIVALENT to 3.0 (inside ±10%). F18: STABLE (CV=0.002).
- F20: REPRESENTATION_DEPENDENT (CV=0.32 across transforms).
- 63,107 USp(4) conductors. Value is 2.939, NOT 3.0.
- Classified POSSIBLE: no Tier B test ran (needs confound data).
- Needs: F17 with Sato-Tate subgroup strata, or F23 with (conductor, discriminant) pairs.

**S1. Jones/Alexander unit circle M4/M2^2 profiles are distinct (C41/C57)**
- Rich data (13 evaluation points × 3 polynomials)
- Jones degenerate at w3/w4, Alexander peaks at w6, Conway monotonically grows
- Needs: F15v2 at each evaluation point, F18 stability, check against different knot databases
- Risk: Could be an artifact of the specific knot sample (mostly 10-11 crossing knots)

**S2. S_n character M4/M2^2 = p(n)/n (C48)**
- Mathematical identity (Bernoulli sparsity of hook characters)
- Exact, not empirical — but the CONNECTION to the moment hierarchy is interpretive
- Needs: Verify the Bernoulli derivation is correct (not just empirical)
- Risk: The formula is right but the interpretation (hierarchy = sparsity) may be wrong

**S3. Prime gap M4/M2^2 scales at +0.23/decade toward Poisson (C43)**
- Measured at 4 magnitude ranges, monotonic increase
- F16v2: NOT equivalent to Poisson at current scale (4.60 vs 6.0)
- Needs: Extend to larger primes (10^8, 10^9), check if slope is constant
- Risk: Slope may not be constant; could curve or plateau

**S4. Lean proof power law B=0.47 (C12)**
- Regression on 500 modules
- Namespace enrichment 2.64x (corrected by F17)
- Needs: F18, test on full mathlib (not just 500 module sample), confound sweep
- Risk: 500 modules may not be representative

**S5. Tc complexity r=0.37 non-cuprate (C4)**
- Survives cuprate removal, stable across 20 splits
- Needs: Check against iron-based removal, heavy-fermion removal, etc.
- Risk: r=0.37 is moderate; could weaken further with more confound control

**S6. SC composition graph curvature kappa=-0.38 (C5)**
- Correlates with Tc (r=-0.479)
- Needs: F17 (is curvature just proxying for node degree/n_elements?), F18
- Risk: Graph construction (Jaccard > 0.5 threshold) is arbitrary

**S7. Crystal formation energy M4/M2^2 ≈ C3=5.0 (C60)**
- F15v2: PASSES (not log-normal)
- F16: 5.0 inside CI [4.689, 5.666]
- BUT M6/M2^3 = 52.5 ≠ C4=14.0 (second moment kills Catalan chain)
- Risk: One-dimensional coincidence

**S8. Galois group enrichment on class number 3.68x (C36)**
- Stronger than degree (2.56x)
- Needs: F17 (confound = degree, but P4 suggests Galois ⊃ degree), F18
- Risk: May be identical to degree enrichment via nesting

---

## CONJECTURE (observed but not yet seriously tested)

All remaining measurements from challenges C1-C65 that haven't been audited:
- Curvature landscape (arithmetic positive, everything else negative)
- Moment hierarchy as a meaningful ordering (partially rehabilitated by F15v2)
- Conway anti-correlated with Alexander around unit circle
- Tactic diversity M4/M2^2 = 1.31 (most constrained non-degenerate)
- Element identity enrichment 1.94x
- Ionization enrichment null
- Angular momentum L enrichment null, J enrichment 1.23x
- PDG mass M4/M2^2 = 69.6
- Crystal density M4/M2^2 = 67.1
- SG zeta Z'/Z = -4.913
- Proof chromatic number chi=4=omega
- Knot determinant M4/M2^2 = 2.16 (NOT confirmed as SU(2) match — INCONCLUSIVE)
- All enrichment values not yet confound-swept
- All moment values not yet subset-stability tested

---

## KILLED (confirmed false or artifact)

**K1. Knot det = SU(2) narrative** — F16 INCONCLUSIVE (90% CI [2.10, 2.21], 2.0 at lower edge). Value 2.1555 is real and STABLE but NOT exactly 2.0.

**K9. Galois enrichment on class number** (was P4/S8) — **KILLED by F17 (2026-04-11 retest)**
- F17: CONFOUND_DOMINATED (sensitivity 0.66). Enrichment drops from 3.94x to 1.34x when stratified by degree.
- Within-degree: Degree 3 = 1.16x, Degree 4 = 0.40x. Galois adds nothing beyond degree.
- Also kills "enrichment is MAX not multiplicative" (P4) — the nesting was degree → Galois → class number.

**K10. Isogeny single-slope model** — **KILLED by F23 (2026-04-11 retest)**
- F23: LATENT_CONFOUND (k=4, delta_r=0.23, 5/5 gates, 3/3 methods agree).
- Slopes vary 0.71-1.94 across size regimes. diameter = O(log n) holds but coefficient is size-dependent.
- Relationship is real (F1-F14 all pass, z=101), but single-slope model is wrong.

**K2. Moment hierarchy as "constraint depth spectrum"** — Partially rehabilitated by F15v2 (distributions deviate from log-normal) but the INTERPRETATION of the hierarchy as measuring algebraic constraint depth remains unproven. The ordering is real; the meaning is conjecture.

**K3. CMB Catalan chain** — M4/M2^2 = 4.54, nowhere near SU(2)=2.0. Catalan chain does not appear in physical acoustic spectra.

**K4. Earthquake phase coherence** — Null (r=-0.16, p=0.25). Phase coherence doesn't transfer from automorphic forms to seismic point processes.

**K5. NF reg deg3 = USp(4)** — F16v2 INCONCLUSIVE. 3.0 falls below the 90% CI lower bound.

**K6. Formation energy C3 second moment** — M6/M2^3 = 52.5, NOT 14.0 (C4). One-dimensional coincidence only.

**K7. Ionization enrichment** — 0.97x, null.

**K8. ST group → discriminant** — 0.82x, anti-enrichment.

---

## Dependencies

The following findings depend on lower-tier findings being correct:

```
P1 (G2 cond=USp(4)) ← standalone, no dependency
P2 (SG→Tc) ← standalone
P3 (config enrichment 11.8x) ← standalone
P4 (enrichment is MAX) ← depends on enrichment measurements being correct (P3, S8)

S1 (unit circle profiles) ← standalone measurement, but INTERPRETATION depends on moment hierarchy (CONJECTURE)
S3 (prime gap scaling) ← standalone
S5 (Tc complexity) ← standalone but corrected value depends on confound methodology
S6 (curvature) ← depends on graph construction choices (CONJECTURE-level)
S7 (form energy ≈ C3) ← killed at M6 level
```

No current finding in PROBABLE tier depends on another finding in a lower tier. This is healthy — each probable stands alone.

---

*Classified: 2026-04-11*
*0 Validated, 4 Probable, 8 Possible, ~30 Conjecture, 8 Killed*
*All raw data preserved for future re-audit*
