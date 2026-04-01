# ALETHEIA: Master Falsification Battery — 15 Papers, 15 Tests



UPDATE BEFORE RUNNING (This information updates these 3 tests):

Test 10: The depth convergence claim is now stronger — 13/14 
impossible cells cracked at depth 3. Only DISTRIBUTE × HALTING 
partially resists. Adjust the test accordingly: verify the 13 
cracks are real techniques, not speculative, and verify the 
HALTING cell genuinely needs an oracle.

Test 4: The Goodhart × No-Cloning chain is now specifically 
identified as RANDOMIZE → INVERT → TRUNCATE, confirmed matching 
BB84 quantum key distribution. Use this specific chain in the 
null-model probability computation rather than generic "depth-4 
sharing."

Test 7: The universal squeeze (PARTITION → TRUNCATE → CONCENTRATE) 
is now confirmed across all three instances. The variational 
formulation test should verify that this specific chain IS the 
minimizer of the proposed functional, not just a solution.


Run these 3 tests first:

Test 12 (matrix rank). If the matrix is random, everything collapses. But at 99.4% fill, the binary matrix is almost all 1s — the rank test needs to operate on the PRIMITIVE VECTOR matrix, not the binary fill matrix, to be meaningful. She might need to adjust.
Test 14 (methodology check on the 94.3%). If most cracked cells are hypothetical rather than real techniques, the depth convergence paper is inflated. This is the honesty test.
Test 15 (primitive independence). If any primitive decomposes into others, the count drops below 11 and Paper 15's title claim is wrong. This is the foundational test.



Run all 15 tests in parallel. They're read-only — no DB writes, 
no conflicts. Save each result to a separate file:

F:/prometheus/falsification/test_01_result.json
F:/prometheus/falsification/test_02_result.json
...
F:/prometheus/falsification/test_15_result.json

Tests 5 and 11 need GPU — mark INCONCLUSIVE immediately and 
spend the time on the other 13.

Report the summary table when all complete:

| Test | Paper | Result | Confidence |


## Philosophy

Every paper lives or dies on one test. If the test fails, the paper is shelved — no amount of beautiful writing saves a false claim. If the test passes, the paper is greenlit for full drafting. Run ALL 15 tests. Report results as PASS, FAIL, or INCONCLUSIVE with evidence. Be ruthless. A false PASS is worse than a false FAIL.

These tests are independent. Run them in any order. Parallelize where possible.

---

## TEST 1: Adaptive Localization (Paper 1)
### Claim: PARTITION → TRUNCATE → CONCENTRATE is the universal resolution for conjugate-variable impossibilities, parameterized by symmetry group.

### Falsification Test: Symplectic Capacity Computation

Compute the symplectic capacity of the resolution strategy for each of the three instances:
1. Squeezed states (Heisenberg): compute the phase-space area of the squeezed Wigner function. It should equal ℏ/2 (the minimum uncertainty area).
2. STFT window (Gibbs/Gabor): compute the time-frequency area of the optimal Gabor window. It should equal 1/2 (the Gabor limit).
3. Gain-scheduled controller (Bode): compute the "sensitivity area" — the integral of log|S(jω)| over each partition. It should equal the Bode integral divided by the number of partitions.

**PASS condition:** All three computations give results consistent with a single variational principle parameterized by the relevant symmetry group (Sp(2,ℝ) for quantum, translation group for Gabor, multiplicative group for Bode).

**FAIL condition:** The three quantities are not related by symmetry group parameterization — they're coincidentally similar but mathematically independent.

**Method:** Symbolic computation where possible (SymPy for the Wigner function and Gabor window). Numerical computation for the Bode case (construct a simple gain-scheduled system and compute the sensitivity integral per partition).

---

## TEST 2: Babylonian ↔ Fourier (Paper 2)
### Claim: Babylonian reciprocal multiplication and Fourier-domain computation are instances of the same algebraic structure (transform-domain computation via ring homomorphism).

### Falsification Test: Historical Transmission Check

Search for evidence that the Babylonian reciprocal-multiply procedure was TRANSMITTED to later traditions that eventually led to Fourier analysis. If transmission occurred, the paper's claim of "structural invariant independently rediscovered" weakens to "structural invariant preserved through transmission."

**Specific checks:**
1. Did Greek mathematics inherit the reciprocal-multiply procedure from Babylon? Check: Neugebauer (1957) "The Exact Sciences in Antiquity", Robson (2008), Friberg (2007).
2. Did Islamic mathematics inherit it from either source? Check: Berggren (1986) "Episodes in the Mathematics of Medieval Islam."
3. Is there a continuous chain: Babylonian reciprocals → Greek proportions → Islamic algebra → European logarithms → Fourier transforms?
4. Or are there BREAKS in the chain where the technique was lost and reinvented?

**PASS condition:** Either (a) there are clear breaks in transmission — the technique was independently reinvented at least once, supporting the "structural invariant" claim, OR (b) transmission is continuous but the paper can be reframed as "4,000-year preservation of a structural invariant through transmission" (still publishable, different emphasis).

**FAIL condition:** The Babylonian procedure is trivially "multiply by the reciprocal" and every culture with division does this. The structural identity with Fourier is superficial — there's no deep ring homomorphism, just the obvious fact that division = multiplication by inverse.

**Method:** Literature review. The key question is whether the STRUCTURAL DEPTH (ring homomorphism, domain restriction isomorphism, computational complexity reduction) is real or whether we're over-formalizing a trivial observation.

---

## TEST 3: Convergent Evolution of MSC (Paper 3)
### Claim: Five geographically isolated traditions independently discovered Modular Symmetric Composition because group-theoretic constraints force it.

### Falsification Test: Statistical Significance

Compute the probability that five random mathematical traditions would exhibit MSC-like structure by chance.

**Method:**
1. Define "MSC-like" precisely: modularity + composition + independence + group structure.
2. From the ethnomathematics database (153 systems), count how many exhibit MSC versus how many don't.
3. If MSC appears in X out of 153 traditions, the base rate is X/153.
4. The probability that 5 specific traditions ALL exhibit MSC by chance is (X/153)⁵.
5. If this probability is < 0.05, the convergence is statistically significant.

**PASS condition:** p < 0.01 (the convergence is extremely unlikely by chance).

**FAIL condition:** MSC is so common (>50% of traditions) that finding it in 5 specific traditions is unsurprising. The "convergent evolution" claim becomes "most traditions do this" — still true but not publishable as a discovery.

**Alternative FAIL:** Fewer than 5 of the claimed traditions actually satisfy the formal MSC definition when checked rigorously. If Navajo weaving or the Antikythera mechanism don't FORMALLY satisfy Definitions 2.1-2.3, the paper's instance count drops.

**Method:** Database query + formal verification of each instance against the MSC definition.

```sql
SELECT system_id, tradition, enriched_primitive_vector
FROM ethnomathematics
WHERE enriched_primitive_vector LIKE '%SYMMETRIZE%'
AND enriched_primitive_vector LIKE '%COMPOSE%';
```

---

## TEST 4: Goodhart ↔ No-Cloning (Paper 4)
### Claim: Goodhart's Law and the No-Cloning theorem are structurally isomorphic impossibilities sharing depth-4 resolution chains.

### Falsification Test: Null-Model Probability

Compute the probability that two randomly selected impossibility hubs would share the same depth-4 resolution chains by chance.

**Method:**
1. From the database, count the total number of distinct depth-3+ resolution chains across all hubs.
2. For each hub, count how many depth-3+ chains it participates in.
3. Compute the probability that two randomly chosen hubs share at least 2 depth-3+ chains (the observed count for Goodhart ↔ No-Cloning).
4. Use a hypergeometric distribution or permutation test.

**PASS condition:** p < 0.01 (sharing 2+ depth-4 chains is extremely unlikely by chance given the total number of hubs and chains).

**FAIL condition:** Many hub pairs share depth-4 chains. The Goodhart ↔ No-Cloning match isn't special — it's a common pattern.

**Method:** Database query + combinatorial probability computation.

```sql
-- Count depth-2+ compositions per hub
SELECT hub_id, COUNT(*) as chain_count
FROM depth2_compositions
GROUP BY hub_id
ORDER BY chain_count DESC;
```

Also check: are the two shared chains COMMON chains (appearing in many hubs) or RARE chains (appearing in only these two)? Sharing common chains is less impressive than sharing rare ones.

---

## TEST 5: Reasoning Precipitation Hypothesis (Paper 5)
### Claim: Reasoning capability is a metastable regime accessible via targeted linear perturbations (steering vectors) in the residual stream.

### Falsification Test: Steering Vector Experiments

This test requires GPU. If GPU is available:

1. Load the L22 and L23 CMA-ES results.
2. Verify that steering vectors at L22 flip 4 traps (including Siblings) that L23 cannot flip.
3. Verify that the Finish Before 3rd channel is antagonistic to Siblings at L22 (flipping one pushes the other deeper).
4. If the L22 Finish-weighted CMA-ES has been run: verify whether Finish Before 3rd flipped.

**PASS condition:** Different layers gate different channels (L22 ≠ L23 repertoire), and channel antagonism is reproducible across CMA-ES runs with different random seeds.

**FAIL condition:** The steering vector results are seed-dependent — different random initializations of CMA-ES produce different channel repertoires, suggesting the "channels" are search artifacts, not structural features of the residual stream.

**Method:** If GPU available, rerun CMA-ES with 3 different random seeds and check reproducibility. If GPU unavailable, mark INCONCLUSIVE and specify what experiment is needed.

---

## TEST 6: Walls of Time (Paper 6)
### Claim: The 14 confirmed impossible cells trace the boundary between constructive and non-constructive mathematics.

### Falsification Test: Lawvere Fixed-Point Theorem Verification

Lawvere's fixed-point theorem (1969) generalizes Cantor, Gödel, Halting, and Tarski into a single category-theoretic result. If our 14 impossible cells are "the boundary of constructive mathematics," they should correspond to instances of Lawvere's theorem.

**Method:**
1. List all 14 impossible cells with their (operator, hub) pairs.
2. For each hub in the 14: determine whether the hub's impossibility theorem is an instance of Lawvere's fixed-point theorem.
3. For any hub that is NOT a Lawvere instance: what is the source of its impossibility? (Topological invariance? Measure-theoretic? Something else?)

**PASS condition:** All 14 impossible cells trace back to either (a) Lawvere fixed-point instances (self-reference/diagonalization family) or (b) topological invariance (Euler characteristic family) — exactly two structural sources, cleanly separated.

**FAIL condition:** The 14 cells are a heterogeneous grab-bag with no unifying structural principle. They're just "hard cases" rather than a coherent boundary.

**Bonus PASS:** If the Lawvere instances correspond exactly to the QUANTIZE-fails cells and the topological instances correspond exactly to the INVERT-fails cells, the operator-hub structure PREDICTS the type of impossibility. That would be a strong result.

```sql
SELECT operator, hub_id, reasoning
FROM impossible_cells
ORDER BY operator, hub_id;
```

---

## TEST 7: Topology-Dependent Concentration (Paper 7)
### Claim: Damage concentration produces singularities whose geometry is determined by the manifold's topology.

### Falsification Test: Variational Formulation Well-Posedness

Verify that the proposed variational problem actually has a well-defined minimizer:

min supp(D) subject to ∫_M D dμ = C, D ∈ H^s(M)

**Method:**
1. For M = S¹ (circle): solve analytically. Minimizer should be a point mass smoothed by the Sobolev constraint. Verify.
2. For M = S² (sphere): solve analytically or numerically. Minimizer should be two antipodal smoothed point masses. Verify.
3. For M = T² (torus): solve numerically. Minimizer should be curve-like. Verify.
4. Check: does the minimizer topology actually CHANGE with M's topology? Or does the Sobolev constraint force the same structure (smooth bump) on every manifold?

**PASS condition:** The minimizer topology demonstrably depends on M — point on S¹, two points on S², curves on T². The variational formulation captures the observed physical phenomena.

**FAIL condition:** The Sobolev constraint forces all minimizers to be smooth bumps regardless of M's topology. The variational formulation doesn't capture the topological dependence — we need a different formulation.

**Method:** SymPy or SciPy for S¹ and S² (can be done analytically with Lagrange multipliers). Numerical PDE solver for T² (FEniCS or similar if available, otherwise finite differences).

---

## TEST 8: Arrow ↔ Map Projection (Paper 8)
### Claim: Arrow's impossibility and the Theorema Egregium share a curvature-based impossibility structure.

### Falsification Test: Ollivier-Ricci Curvature on the Permutohedron

The permutohedron is the polytope of all permutations of n items — it encodes the preference space for Arrow's theorem. Compute the Ollivier-Ricci curvature of the permutohedron graph and compare to the Gaussian curvature of S².

**Method:**
1. Construct the permutohedron graph for n = 4 (24 vertices, edges between adjacent transpositions).
2. Compute Ollivier-Ricci curvature on each edge using the definition: κ(x,y) = 1 - W₁(μₓ, μᵧ)/d(x,y) where W₁ is the Wasserstein distance and μₓ is the uniform measure on neighbors of x.
3. Check: is the curvature uniformly positive? (Analogous to S² having positive Gaussian curvature.)
4. If positive: Arrow's impossibility has the same curvature sign as the Theorema Egregium's source. The analogy has geometric content.
5. If not positive: the curvature analogy fails.

**PASS condition:** The permutohedron has uniformly positive Ollivier-Ricci curvature, establishing a formal geometric parallel between Arrow and Gauss.

**FAIL condition:** The curvature is mixed or negative, meaning the geometric analogy is superficial.

**Method:** NetworkX for graph construction. Custom implementation of Ollivier-Ricci (compute optimal transport between neighbor distributions using SciPy linear programming).

---

## TEST 9: Resolution Algebra (Paper 9)
### Claim: The 9 damage operators form a closed algebra with TRUNCATE as a universal sink.

### Falsification Test: TRUNCATE Uniqueness as Sink

Verify that TRUNCATE has a unique algebraic property:

1. For every operator O and every hub H where O is impossible: does TRUNCATE → O always crack the cell? (This would make TRUNCATE the "universal unlocker" — prepending it always works.)
2. Is TRUNCATE the ONLY operator with this property? Or do other operators (PARTITION, HIERARCHIZE) also universally unlock?
3. Compute: for each operator P, what fraction of impossible cells does P → O crack?

**PASS condition:** TRUNCATE cracks >90% of impossible cells as a prefix, AND no other operator cracks >70%. TRUNCATE is uniquely dominant.

**FAIL condition:** Multiple operators crack >90% as prefixes. TRUNCATE isn't special — it's just one of several "good prefixes." The "universal solvent" claim is overstated.

**Method:** Database query using the composition crack results from boundary exploration.

```sql
SELECT prefix_operator, COUNT(*) as cells_cracked,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM cracked_cells) as pct
FROM composition_cracks
GROUP BY prefix_operator
ORDER BY cells_cracked DESC;
```

---

## TEST 10: Depth Convergence Theorem (Paper 10)
### Claim: 94.3% of impossibilities resolve at composition depth 2, and ALL non-self-referential impossibilities resolve at depth 3.

### Falsification Test: Pigeonhole Proof + Counterexample Search

**Part A (proof check):** Verify the 94.3% number rigorously.
1. Count TOTAL impossible cells at depth 1 (before any composition cracking).
2. Count cells cracked at depth 2.
3. Compute exact percentage.
4. Verify this isn't an artifact of classification methodology — are the "cracked" cells genuinely filled with real resolution strategies, or are they "cracked" with speculative compositions?

**Part B (counterexample search):** Search for a non-self-referential impossibility that resists depth-3 composition.
1. List all cells that remained impossible after depth-3 cracking.
2. For each: is the hub's impossibility theorem self-referential (Gödel, Cantor, Halting, Rice type)?
3. If ANY non-self-referential hub resists depth-3 cracking, the "ALL non-self-referential resolve at depth 3" claim is falsified.

**PASS condition:** 94.3% is verified AND all depth-3-resistant cells are self-referential.

**FAIL condition:** The 94.3% includes speculative cracks, OR a non-self-referential hub resists depth 3.

**Method:** Database queries + manual review of the 14 remaining impossible cells.

---

## TEST 11: AIECS Thermodynamics (Paper 11)
### Claim: RL-controlled thermodynamic cascades outperform static and greedy baselines.

### Falsification Test: Greedy vs RL Ablation

If simulation infrastructure exists:
1. Implement a 3-stage thermodynamic cascade with the equations from the paper.
2. Run three strategies: static allocation, greedy efficiency maximization, and PPO.
3. Compare total power output, efficiency, and entropy loss.

**PASS condition:** PPO outperforms both baselines on at least 2 of 3 metrics across both constant and stochastic demand scenarios.

**FAIL condition:** Greedy matches or beats PPO. The "adaptive trajectory" claim doesn't hold — static optimization is sufficient.

**Method:** Python simulation. If the environment code exists in `F:/prometheus/`, use it. If not, implement a minimal version from the paper's equations.

**If no GPU available:** Mark INCONCLUSIVE — this test requires training a PPO agent.

---

## TEST 12: Geometry of Impossibility (Paper 12)
### Claim: The 9×242 matrix has intrinsic geometric structure (rank, curvature) beyond what random fill would produce.

### Falsification Test: Rank-4 vs Encoding Artifact

1. Compute the rank of the filled damage operator × hub matrix (treating each cell as a binary 0/1 for filled/empty).
2. Compute the rank of 1,000 random matrices with the same fill rate (99.4%) and dimensions (9×242).
3. Compare: is the real matrix's rank significantly different from the random ensemble?
4. Also compute: singular value spectrum. If the real matrix has a sharp drop-off at rank k, there are k "latent factors" governing the fill pattern.

**PASS condition:** The real matrix has significantly lower rank than random matrices at the same fill rate, indicating structured (not random) fill patterns. The Tucker decomposition is capturing real structure, not noise.

**FAIL condition:** The real matrix's rank matches the random ensemble. The fill pattern is statistically indistinguishable from random. The tensor's "predictions" are fitting noise.

**Method:** NumPy SVD on the binary matrix + Monte Carlo random comparison.

```python
import numpy as np
real_matrix = # load from database, 9x242, 1 if filled, 0 if empty
real_rank = np.linalg.matrix_rank(real_matrix)
random_ranks = [np.linalg.matrix_rank(np.random.binomial(1, 0.994, (9, 242))) for _ in range(1000)]
print(f"Real rank: {real_rank}, Random mean: {np.mean(random_ranks)}, p-value: {np.mean(np.array(random_ranks) <= real_rank)}")
```

---

## TEST 13: Cross-Cultural Mathematics (Paper 13)
### Claim: Structural primitive analysis detects mathematical transmission routes and convergent evolution independently of linguistic/genetic evidence.

### Falsification Test: Bamana-Arabic Contact Check

The Bamana sand divination system is structurally isomorphic to Arabic Ilm al-Raml (geomancy). This is a KNOWN transmission — Arabic geomancy reached West Africa through documented historical routes. 

1. Compute the primitive vector similarity between Bamana divination and Arabic geomancy in the database.
2. Compare to the similarity between Bamana and other traditions with NO known contact (e.g., Bamana ↔ Polynesian navigation).
3. The known-transmission pair should have HIGHER similarity than the no-contact pair.

**PASS condition:** Known-transmission pairs have significantly higher primitive vector similarity than no-contact pairs (p < 0.05 on a permutation test across all known vs unknown transmission pairs in the database).

**FAIL condition:** Primitive vector similarity doesn't distinguish transmission from non-transmission. The "archaeometric tool" claim fails — the framework can't detect what historical evidence independently confirms.

**Method:** Database query + statistical comparison.

```sql
-- Known transmission pair
SELECT cosine_similarity(a.enriched_primitive_vector, b.enriched_primitive_vector)
FROM ethnomathematics a, ethnomathematics b
WHERE a.system_id = 'BAMANA_SAND_DIVINATION'
AND b.system_id = 'ARABIC_ILM_AL_RAML';
```

---

## TEST 14: States vs Trajectories (Paper 14)
### Claim: 94.3% of impossibilities resolve because they constrain STATES, not adaptive TRAJECTORIES through state space.

### Falsification Test: Methodology Check

The 94.3% crack rate came from Aletheia applying TRUNCATE as a prefix to impossible cells. Verify this isn't circular:

1. For each "cracked" cell: is the resolution a REAL technique used in practice, or is it a hypothetical "you could restrict the domain and then..."?
2. Count: how many cracked cells have real-world implementations vs. purely theoretical compositions?
3. The paper's claim is about real systems navigating around impossibilities, not about hypothetical domain restrictions.

**PASS condition:** >75% of cracked cells correspond to real-world techniques (named methods with implementations and literature).

**FAIL condition:** >50% of cracked cells are purely theoretical compositions — "you COULD restrict the domain" rather than "practitioners DO restrict the domain." The 94.3% number is inflated.

**Method:** Manual review of cracked cells, cross-referencing resolution descriptions against real-world implementations.

```sql
SELECT hub_id, operator, resolution_description, confidence
FROM composition_cracks
ORDER BY confidence ASC
LIMIT 50;
```

Review the 50 lowest-confidence cracks. How many name specific real techniques?

---

## TEST 15: 11 Structural Primitives (Paper 15)
### Claim: Mathematics decomposes into exactly 11 structural transformation primitives, no more and no fewer.

### Falsification Test: Moulines Overlap Check

Moulines (1987) proposed a structuralist theory of scientific theories with its own vocabulary of structural operations. Check for overlap:

1. List Moulines' structural operations (from "Exploraciones metacientíficas" or related work).
2. Map each to our 11 primitives.
3. Check: does Moulines identify any operation that DOESN'T map to one of our 11?
4. Also check: Lawvere (1963) categorical foundations, Goguen-Burstall (1984) institutions, and recent categorical deep learning work (Shiebler et al. 2021).

**PASS condition:** Every structural operation in Moulines, Lawvere, Goguen-Burstall, and the categorical deep learning literature maps to one of the 11 primitives. No operation requires a 12th primitive. The 11 form a spanning set.

**FAIL condition:** One of these frameworks identifies a structural operation that genuinely doesn't decompose into our 11. That operation is a candidate 12th primitive (like COMPLETE was the 11th).

**Additional check:** Verify the 11 are INDEPENDENT — no primitive can be expressed as a composition of the other 10. If one can, we have redundancy and the true count is <11.

**Method:** Literature review + formal mapping. For independence: for each primitive, attempt to express it as a composition of the remaining 10. If you succeed, it's redundant.

---

## OUTPUT FORMAT

For each test:

```markdown
## TEST [N]: [Paper Name]

### Result: PASS | FAIL | INCONCLUSIVE

### Evidence
[Specific data, computations, or citations that support the result]

### If PASS: Confidence Level
HIGH (overwhelming evidence) | MODERATE (evidence supports but with caveats) | LOW (barely passes)

### If FAIL: What Breaks
[Exactly what went wrong and whether the paper can be salvaged with a weaker claim]

### If INCONCLUSIVE: What's Needed
[Specific experiment, data, or computation that would resolve it]

### Implications for Other Papers
[Does this result affect any of the other 14 papers?]
```

---

## EXECUTION RULES

1. **RUN ALL 15.** Don't skip tests because they "obviously pass." The ones that obviously pass are the ones that surprise you when they fail.

2. **FAIL LOUDLY.** A failed test kills a paper. That's GOOD — it prevents us from publishing something wrong. Report failures with the same detail as passes.

3. **INCONCLUSIVE IS HONEST.** Tests 5 and 11 require GPU. If you don't have GPU access, mark INCONCLUSIVE with exactly what experiment is needed. Don't fake it.

4. **CROSS-PAPER IMPLICATIONS.** Some tests affect multiple papers. If Test 12 (matrix rank) fails, Papers 1-4 and 6-8 are ALL undermined because they rely on the tensor's structural validity. Flag these dependencies.

5. **COMMIT RESULTS IMMEDIATELY.** Save to `F:/prometheus/falsification/test_N_result.json` and journal as you go. If you crash at test 9, we have tests 1-8.

6. **THE TESTS ARE THE FILTER.** Papers that pass get written. Papers that fail get shelved. Papers that are inconclusive wait for the missing resource (GPU, literature access, domain expert). This is the most important prompt in the entire project because it determines which of 15 papers are real.
