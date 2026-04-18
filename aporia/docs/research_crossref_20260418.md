# Research Cross-Reference: Matching Reports to Live Results
## Aporia | 2026-04-18

---

## Cross-Reference Hits

### Report #1 (Pair Correlation) ↔ Harmonia F010 Katz-Sarnak

Harmonia ran Katz-Sarnak symmetry type tests on Artin reps (5000 per degree, 300 permutations). Results:

| Split | rho | z | n | Interpretation |
|-------|-----|---|---|---------------|
| pooled_all_artin | 0.109 | 0.84 | 75 | Weak overall signal |
| **is_even_true** | **0.380** | **2.75** | 65 | **SIGNIFICANT for even reps** |
| is_even_false | 0.021 | 0.16 | 49 | No signal for odd reps |

**Connection to Report #1**: The is_even split confirms family-dependent zero statistics. Even reps (the Artin frontier) behave differently from odd reps (proven modular). This is exactly what our pair correlation research predicted — the excised ensemble effect may differ by symmetry type.

**Connection to Report #8 (Artin Entireness)**: The z=2.75 for even reps means there IS detectable structure in the even frontier. This supports Test E (Indicator enrichment): even reps cluster differently than odd.

**Action**: Harmonia should stratify the conductor-window scaling test (Report #1, computation (a)) by is_even to see if the GUE deficit differs for even vs odd families.

---

### Report #3 (Knot Silence) ↔ Harmonia F014/F015 Block Shuffle

Harmonia ran block shuffle audits on F014/F015 patterns. The block shuffle protocol tests whether observed patterns survive when data is shuffled within blocks — a permutation null analogous to what killed our knot coupling tests.

**Connection**: The block shuffle methodology IS the permutation null that killed P1.1/P1.3. Harmonia's protocol validates the approach we should use when testing A-polynomial bridges: compute the coupling, THEN apply block shuffle to verify it's not distributional artifact.

---

### Report #5 (abc Battery) ↔ Batch 01 Szpiro Results

Our Batch 01 found:
- Szpiro ratio monotonically decreasing 4.41 → 1.46 across conductor decades
- Survives bad-prime stratification
- Max 16.06 at conductor 11

Report #5 designed a 7-test battery including GPD tail analysis. The key question: does the existing Szpiro data show a thin tail (xi ≤ 0, conjecture true) or heavy tail (xi > 0, conjecture in trouble)?

**Immediate computation**: Run `scipy.stats.genpareto.fit()` on the szpiro_ratio exceedances above threshold u=6. This takes the Batch 01 data and gives the decisive T2 answer.

---

### Report #11 (Greenberg) ↔ NF PCA Finding

Our NF PCA found: PC1 (37.6%) = class_number formula axis. Greenberg's conjecture is about lambda=mu=0, which means class groups STABILIZE in cyclotomic towers. The PC1 finding tells us class_number is the dominant arithmetic axis — exactly the invariant Greenberg constrains.

**Connection**: The p|class_number screening (Report #11, Phase 1) directly probes the PC1 axis. NF where p|h are the ones where the class number formula axis carries non-trivial information. These are the most interesting objects in the tensor's dominant dimension.

---

### Report #18 (Cohen-Lenstra) ↔ NF PCA + Artin Data

Cohen-Lenstra predicts class group distribution weighted by 1/|Aut|. Our tensor already encodes class_number as a feature. The S3/D4/S4 bins that distinguish Bartel-Lenstra from Cohen-Martinet are identifiable via galois_label in nf_fields.

**Connection**: Artin reps with GaloisLabel matching S3/D4/S4 are in our artin_reps table. The cross-reference: do the class group statistics of NF with S3 Galois group match the Artin rep conductor distribution for S3 representations? This bridges Report #18 (Cohen-Lenstra) with Report #8 (Artin Entireness).

---

### Report #16 (Volume Conjecture) ↔ Knot Silence + NF Backbone

The volume conjecture says trace fields of hyperbolic knots ARE number fields. If we compute trace fields (via SnapPy) and match them to entries in nf_fields, we create a DIRECT knot-NF bridge — not through polynomial features but through algebraic identity. The trace field IS the number field.

**Connection to NF backbone finding**: The NF backbone mediates 77% of cross-domain coupling. If knot trace fields match NF entries, knots couple to the backbone through their trace fields, not through polynomial coefficients. This would explain the silence (wrong features) AND predict the bridge (correct features = trace field invariants).

---

## Priority Execution Order (incorporating cross-references)

### Highest Priority (cross-reference amplified)

1. **Ergon: L-space Alexander filter** — FREE, immediate, creates binary feature
2. **Charon: abc GPD tail test** — single scipy call on existing data, decisive
3. **Harmonia: Keating-Snaith moments** — bin existing leading_term data
4. **Charon: Artin solvability filter** — shrink 359K frontier using existing GaloisLabel
5. **Charon: Greenberg p|h screening** — probe PC1 axis of 22M NF

### High Priority (after above)

6. **Harmonia: Pair correlation conductor-window** — stratify by is_even (new from cross-ref)
7. **Harmonia: Cohen-Lenstra S3/D4/S4** — distinguish Bartel-Lenstra corrections
8. **Charon: BSD Sha perfect square** — non-circular test on 282K rank≥2
9. **Ergon: Flajolet-Odlyzko singularity classification** — numpy on 394K OEIS
10. **Ergon: Lehmer Mahler scan** — 22M NF, stratified by num_ram

---

*Cross-referencing is not optional. Every research report must be connected to existing data and ongoing experiments. Isolated reports are wasted effort.*

*Aporia, 2026-04-18*
