# Charon Journal — 2026-04-09 Evening

## Underground Expedition: GSp_4 Structural Analysis

### Session goal
Execute the 5 priorities from the congruence session handoff. Deformation rings deferred (need Sage/Magma). The other 4 completed or in progress.

### Tools built
1. **genus2_structural_analysis.py** — twist dedup + geometric case analysis + mod-2 scan (all from stored data)
2. **genus2_c2_extend.py** — F_{p^2} point counting for b_p extension (naive, O(p^2) with class overhead)
3. **genus2_c2_fast.py** — 80x faster version using norm-based square detection: z is square in F_{p^2} iff N(z) = a^2 - g*b^2 is square in F_p

### Results

#### Priority 1: Twist Deduplication — CLEAN
**0/37 are quadratic twists.** All 37 irreducible mod-3 congruences are independent.
- No exact twists (a_p ratio doesn't match any Kronecker symbol)
- No b_p exact matches (twist would preserve b_p)
- No mod-3 twists beyond the trivial character (d=1)
- Bug caught and fixed: initial scan showed all perfect squares matching (d=1,4,9,16,25,36,49) — trivial character, not a twist. Filtered to squarefree d only.

#### Priority 2: Geometric Cases — RECLASSIFIED
Previous: 7 geometric, 30 representation-theoretic.
**Revised: 2 genuine geometric, 5 vacuously geometric, 30 representation-theoretic.**

The 7 "geometric" cases (IC match mod 3) split into:
- **2 genuinely geometric** (N=2348, 20560): IC match mod 3 with nonzero residues. Absolute Igusa invariants (j1, j2, j3) match mod 3. Jacobians genuinely isomorphic over F_3-bar.
- **5 vacuously geometric** (N=20432, 32575, 124712, 155305, 173936): ALL Igusa-Clebsch invariants have v_3 >= 1 (I2), >= 2 (I4, I6). Everything is 0 mod 3 — match is trivial. But I10 has v_3 = 0 (good reduction), and IC mod 9 DIFFERS. These are NOT geometric. Reclassified as representation-theoretic with uninformative mod-3 IC test.

Structural note: N=155305 has IDENTICAL I10 = 3180646400 for both curves (same Jacobian discriminant).

**Effective count: 2 geometric, 35 representation-theoretic.**

#### Priority 3: Mod-2 Scan — 733 IRREDUCIBLE
The Hasse squeeze is weakest at ell=2. Results:

| Filter | Count |
|--------|-------|
| Total mod-2 congruences | 11,356 |
| Coprime to conductor | 1,141 |
| Both USp(4) + coprime | 1,115 |
| **Irreducible (4D)** | **733** |

**Ratio to mod-3: 733/37 = 19.8x** (Hasse prediction: ~9x). The excess is because mod-2 representations have richer structure — the image of Galois in GSp_4(F_2) has order 720 vs 51,840 for GSp_4(F_3), and the configuration space is correspondingly larger.

IC mod-2 analysis is uninformative (16 possible signatures, too coarse to discriminate). All 733 show as "geometric" at mod 2 — this is a false positive from the test's lack of resolution, not a structural statement.

Three pairs have ALL b_p differences exactly zero (N=4293, 7173, 9459) — potential exact quadratic twists. All are USp(4) and irreducible. Twist investigation queued.

Overlap with mod-3 landscape: only 2 conductors (N=1844, 2348) appear in both mod-3 and mod-2 irreducible sets. A simultaneous mod-6 congruence is very rare, as expected.

Rich multiplicity: N=2304 and N=2720 each have 6 mod-2 congruences.

#### Priority 4: b_p Extension — IN PROGRESS
Built F_{p^2} point counter. Key formula:
```
c2 = (c1^2 + #C(F_{p^2}) - p^2 - 1) / 2
```

**Bug caught**: initial formula had sign error (negated). Fixed and verified at known primes.

**Optimization**: replaced F_{p^2} Euler criterion (O(log p) F_{p^2} mults per element) with norm-based test (3 F_p mults per element). **80x speedup** (0.7s vs 55s per conductor at p<=150).

**COMPLETE: 37/37 full pass.** Both c1 and c2 verified at ~92 primes each (up to p=500), zero failures across all 37 conductors. 33 minutes total compute time.

| Metric | Value |
|--------|-------|
| Conductors tested | 37/37 |
| Average primes per pair | 92 (23 known + 69 extended) |
| c1 failures | 0 across 2,555 tests |
| c2 failures | 0 across 2,555 tests |
| Random probability per pair | (1/9)^92 ~ 10^{-88} |
| Total compute time | 33 minutes |

#### Priority 5: Deformation Rings — DEFERRED
Requires SageMath or Magma for tangent space computation. Neither available. Would need to compute dim_k(m/m^2) where m is the maximal ideal of the local deformation ring. Deferred to a session with CAS access.

### Key findings

1. **All 37 are independent.** No twists, no geometric redundancy (only 2 genuine geometric cases). The raw count of 37 stands after deduplication.

2. **The mod-2 landscape is massive.** 733 irreducible mod-2 congruences vs 37 mod-3. The paramodular Hecke algebra has dense mod-2 fibers.

3. **The reclassification sharpens the story.** 35/37 are purely representation-theoretic (Jacobians differ geometrically but share mod-3 Galois representation). Only 2/37 admit a geometric explanation.

4. **The norm trick.** z square in F_{p^2} iff N(z) square in F_p. Should have known this from the start. 80x speedup makes p=500 feasible.

5. **Sign errors in genus-2 formulas are the #1 bug source.** The LMFDB convention for the Euler factor coefficients has subtle sign differences from the characteristic polynomial convention. Every formula needs manual verification before deployment.

### What the next session needs

1. ~~Complete b_p extension~~ — DONE: 10^{-88} combined probability
2. **Twist check on the 3 mod-2 candidates** (N=4293, 7173, 9459 with b_p=0)
3. **Scale to more ell values** — mod-5 scan gave 0 coprime results at 24 primes. With extended primes (p<=500), might find candidates the original scan missed.
4. **Write the paper section** — the fiber structure table is now complete enough for the congruence landscape section
5. **Deformation rings** — need CAS access (SageMath or Magma)

### Updated state table

| Result | GL_2 | GSp_4 |
|--------|------|-------|
| Congruences | 981 (242 independent) | **37 irreducible** |
| Verification | Theorem-level (Sturm) | **92 primes, 10^{-88}** (was 10^{-79}) |
| Both Euler components | N/A (1 component) | **c1 AND c2 verified** (was c1 only) |
| Irreducibility | Proved (discriminant) | Proved (char poly factorization) |
| Twist dedup | Done | **Done: 0/37 are twists** |
| Geometric vs rep-theoretic | N/A | **2 geometric, 35 rep-theoretic** |
| Mod-2 landscape | Not explored | **733 irreducible** |

### Honest count

Novel cross-domain discoveries: **zero.**
Kills: **0 this session** (but 5 vacuous geometric cases reclassified).
New tools: **3 scripts** (structural_analysis, c2_extend, c2_fast).
New data: **37/37 c2 verified, 733 mod-2 congruences, twist dedup, IC classification.**
Computational innovation: **norm-based F_{p^2} square detection (80x speedup).**
Bugs caught: **2** (formula sign error, squarefree filter for twists).

---

*Session: 2026-04-09 evening*
*Charon v5.0 → v5.1 (underground expedition)*
*Standing orders: explore the unpopular, trust nothing, kill everything*
*The ferryman went underground. The water is deeper in GSp_4, but the instruments are sharper. 733 mod-2 lights in the dark.*

### Addendum: Twist Verification + Mod-5 Extinction + Research Triage

**Mod-2 twist anomalies: ALL THREE are quadratic twists by d = -3.**
- N=4293 (= 3^4 * 53): twist by d=-3, IC differ. Different curves, same twisted representation.
- N=7173 (= 3^2 * 797): twist by d=-3, IC identical. Geometrically isomorphic.
- N=9459 (= 3^2 * 1051): twist by d=-3, IC identical. Geometrically isomorphic.
- All conductors divisible by 9. The twist discriminant d=-3 divides N in every case.
- Kronecker symbol (-3/p) perfectly matches the a_p sign pattern at all 22-23 primes.
- **Not anomalies. Functorial.** These are exactly what the theory predicts.

**Mod-5 extended scan: EXTINCTION CONFIRMED.**
- 0 genuine coprime USp(4) congruences at ell=5 (or 7, 11, 13).
- The 668 "congruences" in the original scan were ALL isogeny-class ghosts (zero diffs).
- After proper deduplication: nothing at ell >= 5.

**The complete congruence landscape for genus-2 (GSp_4):**

| ell | Coprime USp(4) Irreducible | Probability | Status |
|-----|---------------------------|-------------|--------|
| 2 | 733 | (1/4)^k | Dense, mostly untested at depth |
| 3 | 37 | 10^{-88} | Fully verified, 35 rep-theoretic |
| 5+ | 0 | (1/25+)^k | Hasse squeeze extinction |

**5-agent research triage:**
- Lehmer: DEAD (can't beat 10^15 boundary with 31 terms)
- Maeda: LOW (only weight-2 data; already verified to k~14000)
- GSp(4) modularity: LOW (no Siegel forms in LMFDB for N>1000)
- Genus-3 Sato-Tate: MEDIUM (feasible, needs data ingest, ~400 lines new code)
- Mod-2 twists: DONE (all 3 are d=-3 twists, functorial)

**Total session tools built: 6 scripts.**

*The map is complete at ell=2,3. The mod-5 tunnel is sealed. The next frontier is genus-3, but it needs cargo (data) before the boat can sail.*

### Addendum 2: Five Frontiers — Lehmer and Moonshine

**Lehmer's Conjecture (Frontier 4):**
- Built tau(n) via q-expansion: Delta = q * prod(1-q^n)^24
- 3,000 values computed, 100% coverage, 30/30 OEIS match
- Ramanujan congruence mod 691: **200/200 PASS**
- **Rediscovery: mod-23 residue class starvation.** tau(n) takes only 5/23 residue classes (75.1% zero-class). This is the structural shadow of the S_4 Galois image of Delta mod 23. Found purely from coefficient data.
- Weight-12 Sato-Tate: variance 0.238 (expected 0.250), all |x_p| < 1 (Ramanujan-Petersson confirmed)
- Impossibility scan: max 9/25 simultaneous vanishing at n=1121. Lehmer safe.
- tau(p) saved for 430 primes — extensible framework for any modular form

**Moonshine (Frontier 5):**
- 21/21 core moonshine sequences found in OEIS
- 2,609 sequences in 1-hop cross-reference neighborhood
- 3,315 raw coefficient bridges, **filtered to 47 genuine** using:
  - Recursion order >= 3 (kills cyclotomic inversions)
  - Coefficient entropy >= 0.3 (kills zero-heavy sequences)
  - Zero fraction < 0.6 (kills trivial patterns)
- **THE bridge: mock theta f(q) shares [6,4,-3,-12,-8,12] with 5 McKay-Thompson 6E series.** This is the Cheng-Duncan-Harvey umbral functor rediscovered from raw coefficients.
- **A058728** (McKay-Thompson 60D) survived M24 filter — umbral-to-monstrous bridge
- **A289063** (E_6^2/Delta) connects j-function and J — structural bridge between Eisenstein and Monster
- 4 multi-core bridge sequences connect 2+ moonshine cores simultaneously

**LMFDB Situation:** Rate-limited after initial probes. Frontiers 1-3 (Maeda, Genus-3, Paramodular) blocked on data. Download scripts built and ready for when API recovers or James downloads manually.

**Tools built this session: 10 total** (6 GSp_4 + tau_extend.py + moonshine_oeis_bridge.py + moonshine_filter.py + mod-5 extended scan)

*The ferryman found the Ramanujan tau's hidden face (mod 23) and the umbral moonshine functor (mock theta -> Monster class 6E) — both from raw coefficient matching. The instruments see what they were built to see: structure in the coordinates.*
