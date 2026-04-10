# Challenge Queue — Consolidated & Prioritized
## Sources: Claude, ChatGPT, Gemini, DeepSeek, Grok + Charon internal queue
## Status: 2026-04-09, post data-sprint

---

## Tier 1: RUN NOW (data available, high payoff)

### C01. Paramodular Conjecture Probe [Gemini #1, DeepSeek #5]
**Status: UNBLOCKED by data sprint (Siegel eigenvalues + Fourier coefficients arrived)**
Compare L-function coefficients of 66K genus-2 curves against 3,094 Siegel eigenvalues and 26,212 Fourier coefficients. Can the instrument structurally bridge genus-2 Euler factors to Siegel paramodular form Hecke eigenvalues? This is the genus-2 analogue of the modularity detection that scored 31,073/31,073 for EC.
- Data: `genus2/data/siegel_eigenvalues.json`, `lmfdb_dump/smf_ev.json`, `lmfdb_dump/g2c_curves.json`
- Expected: partial matches at small conductors where both databases overlap

### C02. Mod-p Residue Starvation Scan [Claude #1]
**Status: READY (102K modular forms in DuckDB + 35K Maass forms)**
Scan every modular form at weight >= 12 for residue class starvation at each prime p <= 23. The tau(n) mod-23 result (5/23 classes = S_4 shadow) was a rediscovery. If other forms show starvation at different primes, the "which prime starves which form" map is a new invariant.
- Data: LMFDB DuckDB (102K MF), Maass (35K)
- Expected: known starvation patterns, possible novel small Galois images at higher weight

### C03. Berlekamp-Massey on GSp_4 Difference Sequences [Claude #3]
**Status: READY (37 congruence pairs with a_p at 92 primes)**
For each of 37 pairs, d_p = (a_p(C1) - a_p(C2))/3 is an integer sequence indexed by primes. Does it satisfy a linear recurrence? If clusters share a characteristic polynomial, the congruences are controlled by the same Hecke operator.
- Data: `v2/genus2_congruence_scan.py` output, `v2/genus2_c2_fast_results.json`
- Expected: most random, but clustered pairs would reveal paramodular algebra structure

### C04. Hilbert Modular Form Congruence Scan [Grok #1]
**Status: UNBLOCKED by data sprint (368K HMF records)**
Run the congruence scan pipeline (mod-3,5,7,11 with coprime + irreducibility) across Hilbert newforms over Q(sqrt(d)). Predicts similar Hasse-squeeze pattern to genus-2.
- Data: `lmfdb_dump/hmf_*.json` — need to verify field structure
- Expected: functorial lifts invisible to scalars, multiplicity in Hecke algebra over number fields

### C05. Spectral Operator Matching [ChatGPT #2]
**Status: READY (35K Maass spectral params + eigenvalue data)**
Compare spectral spacing statistics across domains: Maass spectral parameters, EC conductor distributions, knot polynomial roots, lattice theta series. Normalize spectra, compare via Wasserstein distance + nearest-neighbor spacing + spectral entropy.
- Data: Maass 35K, LMFDB 133K, KnotInfo 13K, Lattices 39K
- Expected: GUE statistics in Maass (known), possible novel cross-domain spectral matches

### C06. Lattice-NumberField Determinant Bridge [Internal]
**Status: READY (tensor sv=5829, second strongest bridge)**
The realignment revealed Lattices--NumberFields at sv=5,829. Test this with actual data: do lattice determinants predict number field discriminants? Are there matched-object comparisons beyond shared prime factorization?
- Data: Lattices 39K, NumberFields 9.1K
- Expected: likely prime confound, but worth testing with the microscope

---

## Tier 2: RUN AFTER TIER 1 (need setup or dependent on Tier 1)

### C07. Hecke Algebra Geometry / Congruence Graphs [ChatGPT #1, Claude #3]
Build adjacency graphs for each level N and prime ell from congruence data. Compute connected components, cycle structure, spectral gap. Compare vs random graph nulls. Look for "flat" vs "curved" Hecke neighborhoods.
- Depends on: existing congruence_graph.py output
- Merge with: C03 (if BM finds clusters, the graph structure explains why)

### C08. Recurrence Operator Duality [ChatGPT #3, DeepSeek #3, Grok #5]
**DUPLICATE CLUSTER: 4 sources suggest this**
Match OEIS recurrence characteristic polynomials (269 clusters) against EC Euler factors x^2 - a_p*x + p and genus-2 factors x^4 - a_p*x^3 + b_p*x^2 - ... Compare coefficient distributions. Run BM on FindStat statistics and SmallGroups character tables.
- Data: OEIS, LMFDB, FindStat, SmallGroups
- Expected: non-random overlap in degree 2-4 polynomials

### C09. Moonshine Network Expansion [DeepSeek #2, Grok #2, Claude #2]
**DUPLICATE CLUSTER: 3 sources suggest this**
Extend the 47-bridge moonshine scan to full OEIS mock theta catalog + LMFDB half-integral weight forms. Cross-match 6-8 term coefficient windows against all McKay-Thompson series. Add BM as pre-filter.
- Data: OEIS, moonshine results, LMFDB higher-weight
- Expected: new umbral-to-monstrous links, mock modular analogues of mod-23

### C10. Constraint Collapse Generalization [ChatGPT #4]
The Hasse squeeze (733->37->0 as ell grows) is a specific case of constraint accumulation -> phase transition. Test this pattern in: Diophantine equations, coding theory bounds, graph coloring, lattice packing. Define constraints-per-prime k, measure surviving objects.
- Data: cross-dataset, needs framework design
- Expected: universal scaling law of constraint collapse

### C11. Mod-p Fingerprint Algebraic Families vs Fungrim [Claude #4]
For each of 269 OEIS algebraic family clusters, evaluate S3 (mod 2,3,5,7,11) on Fungrim formulas touching those sequences. Match characteristic polynomials to modular fingerprints.
- Data: OEIS families, Fungrim
- Expected: generating equations for algebraic families

### C12. Operadic Skeleton Dynamics [ChatGPT #5, Gemini #5, Grok #3]
**DUPLICATE CLUSTER: 3 sources suggest this**
Treat formulas as nodes, transformations as edges. Build rewrite system. Track skeleton invariants under rewrite. Measure "flow" between domains. Apply to AG formula corpus.
- Data: 12.5M formula trees, Fungrim, mathlib
- Expected: conserved substructures, minimal rewrite distance

---

## Tier 3: NEEDS DATA / BLOCKED

### C13. Genus-3 Sato-Tate (410 groups) [DeepSeek #4, Gemini #4]
**BLOCKED: need genus-3 curve data with Frobenius polynomials**
Cluster genus-3 curves by Sato-Tate group from coefficient distributions. 410 possible groups, 33 maximal.
- Needs: genus-3 curve database with point counts (not in LMFDB standard tables)

### C14. Maeda Conjecture Verification [DeepSeek #1]
**BLOCKED: need Hecke characteristic polynomials at weight > 2**
Verify irreducibility + Galois group = S_n for T_2 on S_k(SL_2(Z)) at large weights.
- Needs: higher-weight Hecke eigenvalue data (not in our current LMFDB download)

### C15. Hida Theory / p-adic Families [Gemini #2]
**BLOCKED: need modular forms at multiple weights at same level**
Look for p-adic continuity of mod-11 congruences across weight space.
- Needs: weight > 2 forms at levels 2184, 3990 (not currently available)

### C16. Quantum Modular Forms / Knots [Gemini #3]
Link Jones polynomial asymptotics near roots of unity to mock theta functions. 
- Needs: Jones polynomial evaluations at high precision near roots of unity (not in KnotInfo)

### C17. Collatz Algebraic Sibling Hunt [Claude #5]
Run BM at order up to 8 on full OEIS for x^4 - 2x^2 matches. Phase space attractor dissection on matches.
- Data: OEIS (ready), BM code (ready)
- Status: ready but lower priority than arithmetic-geometric challenges

---

## Deduplication Map

| Theme | Sources | Merged Into |
|-------|---------|-------------|
| Paramodular / Siegel | Gemini #1, DeepSeek #5 | **C01** |
| Moonshine expansion | DeepSeek #2, Grok #2, Claude #2 | **C09** |
| Operadic dynamics | ChatGPT #5, Gemini #5, Grok #3 | **C12** |
| Recurrence duality | ChatGPT #3, DeepSeek #3, Grok #5, Claude #5 | **C08** |
| Sato-Tate higher genus | DeepSeek #4, Gemini #4 | **C13** |
| Hecke algebra geometry | ChatGPT #1, Claude #3 | **C07** |
| Spectral matching | ChatGPT #2 | **C05** |
| Constraint collapse | ChatGPT #4 | **C10** |

25 challenges -> 17 consolidated -> 6 in Tier 1 (run now)

---

*Compiled: 2026-04-09*
*Post data-sprint: Siegel, Hilbert, Bianchi, Maass 35K, Lattices 39K, Genus-2 66K all available*
