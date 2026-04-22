# Deep Research Batch 4 — Problems 61-80
## Aporia Void Detector | 2026-04-22
## 17 problem briefs + 3 tool evaluations

---

## Report #61: Birch-Tate Conjecture (Charon)
**Problem**: |K_2(O_F)| = w_2(F) · |zeta_F(-1)| for totally real F
**Key finding**: Proved up to a power of 2 (Mazur-Wiles odd part, Wiles Main Conjecture). The 2-adic obstruction is structural: Iwasawa theory at p=2 breaks due to torsion in Z_2-extensions. Our 22M NF database can batch-verify for totally real fields.
**Tensor cell**: OUT_OF_TENSOR — suggests new F: K_2 torsion.

## Report #62: Crouzeix's Conjecture (Harmonia)
**Problem**: ||p(A)|| ≤ 2 · sup|p on W(A)| for any matrix A, polynomial p
**Key finding**: Proved with constant 1+sqrt(2) by Crouzeix-Palencia (2017). Gap to 2 remains. Computationally testable at scale: sample random matrices, compute numerical range, measure ratio. Experiment design fits existing tensor infrastructure.
**Tensor cell**: OUT_OF_TENSOR.

## Report #63: Grothendieck-Katz p-Curvature (Charon)
**Problem**: Differential equation has algebraic solutions iff p-curvature vanishes for almost all p
**Key finding**: The p-curvature of Picard-Fuchs operators encodes the Hasse invariant of reduced fibers — exactly what our C11 mod-p enrichment detects. Direct bridge between algebraic geometry, number theory, and differential equations. Sage ore_algebra package computes p-curvature in Python.
**Tensor cell**: F001 x P010, verdict UNKNOWN.

## Report #64: Hadamard Conjecture (Ergon)
**Problem**: n×n Hadamard matrix exists for n≡0 mod 4
**Key finding**: Smallest unknown order is n=668. Attack: Williamson search (four circulant sequences of length 167) via automorphism-reduced SAT + SDP presolve. Three-week computational target on a workstation.
**Tensor cell**: OUT_OF_TENSOR.

## Report #65: Inverse Galois Problem (Charon)
**Problem**: Is every finite group Gal(K/Q) for some K?
**Key finding**: M_23 is the ONLY remaining sporadic group unrealized over Q. All solvable groups done (Shafarevich). Rigidity method (Thompson-Matzat-Völklein) is the main tool but fails when no rigid tuple exists. Our 544K groups database can flag realized/unknown status per group.
**Tensor cell**: F001 x P010, verdict UNKNOWN.

## Report #66: Serre's Conjecture II (Harmonia)
**Problem**: H^1(F, G) = 0 for simply connected G over cd(F)≤2 fields
**Key finding**: Fully resolved for function fields (de Jong 2004). Open for number fields, especially E_8. The conjecture IS the P02 (Cohomological Obstruction) paradigm applied to algebraic groups. Concrete test: E_6 torsor over Q(i).
**Tensor cell**: F001 x P010, verdict UNKNOWN.

## Report #67: Zauner's SIC-POVMs (Ergon)
**Problem**: d^2 equiangular lines exist in C^d for every d
**Key finding**: BRIDGE between quantum info and Hilbert's 12th problem. Exact SIC fiducials live in ray class fields of real quadratic fields predicted by Stark's conjectures. Each new exact SIC = datum about explicit class field theory. Computationally accessible via Riemannian optimization + algebraic number recognition.
**Tensor cell**: OUT_OF_TENSOR — suggests new F: SIC overlap phases.

## Report #68: Furstenberg ×2 ×3 Conjecture (Harmonia)
**Problem**: Only Lebesgue and atomic measures are (2,3)-invariant on R/Z
**Key finding**: Proved under positive entropy (Rudolph 1990, Einsiedler-Katok-Lindenstrauss). Zero-entropy case fully open. THE paradigm case for P20 (Ergodic) and P22 (Entropy). OEIS sequences with non-trivial 2-kernel and 3-kernel are discrete analogs worth scanning.
**Tensor cell**: OUT_OF_TENSOR.

## Report #69: Lonely Runner Conjecture (Ergon)
**Problem**: k runners on circular track — each gets distance ≥ 1/(k+1) from origin
**Key finding**: Proved for k≤7 (Barajas-Serra 2008). k=8 open. Equivalent to simultaneous Diophantine approximation. Attack: Arb interval arithmetic + PARI CF pre-filtering for speed sets {v_1,...,v_8} ⊂ {1,...,20}. SAT encoding feasible for fixed speed tuples.
**Tensor cell**: OUT_OF_TENSOR.

## Report #70: Union-Closed Sets / Frankl (Ergon)
**Problem**: Every union-closed family has an element in ≥ half the sets
**Key finding**: Gilmer's 2022 entropy breakthrough (P22!) gave first constant bound (1%). Chase-Lovett pushed to 3/8. The 3/8 barrier appears to be the entropy method's ceiling. Lattice-theoretic reformulation: join-irreducible elements in finite lattices.
**Tensor cell**: OUT_OF_TENSOR.

## Report #71: Ramsey R(5,5) (Ergon)
**Problem**: 43 ≤ R(5,5) ≤ 48
**Key finding**: 10^15-10^17 core-hours estimated for brute SAT resolution. Viable path: SDP flag algebras to compress upper bound to 45-46, then focused SAT on reduced range. Five Techne tools proposed: ramsey_cnf_gen, nauty_prune, flag_sdp, ramsey_validator, distributed_sat_coordinator.
**Tensor cell**: OUT_OF_TENSOR.

## Report #72: Collatz (Ergodic View) (Harmonia)
**Problem**: All orbits reach 1
**Key finding**: Tao 2019: almost all orbits attain almost bounded values (log density 1). Verified to 2^68. Four novel measurements proposed: spectral analysis of parity sequences, tensor decomposition of stopping times, 2-adic Lyapunov spectrum, entropy rate by residue class. None in the literature.
**Tensor cell**: OUT_OF_TENSOR.

## Report #73: MLC Conjecture (Harmonia)
**Problem**: Mandelbrot set is locally connected
**Key finding**: Proved at non-renormalizable parameters (Yoccoz) and bounded-type infinitely renormalizable (Lyubich). Open at unbounded combinatorics. Key measurement: modulus sequence m(n,c) of Yoccoz puzzle annuli — if m(n,c)→0 along a cascade, a priori bounds fail.
**Tensor cell**: OUT_OF_TENSOR.

## Report #74: Riemann Hypothesis (Charon)
**Problem**: All nontrivial zeros at Re(s)=1/2
**Key finding**: Verified to 2×10^13 zeros (Platt-Trudgian 2021). ~41% on critical line (Conrey). Every major paradigm has been tried; the gap is "not a missing calculation but a missing geometric object" (no Frobenius for Z). Prometheus contribution: anomaly detection in zero spacings, cross-family symmetry-type tests.
**Tensor cell**: F011 x P020, verdict UNKNOWN.

## Report #75: Hodge Conjecture (Harmonia)
**Problem**: Every Hodge class is algebraic
**Key finding**: Only proved for (1,1)-classes (Lefschetz). Integral version fails (Voisin). Gap between analytic (type (p,p)) and algebraic is the core difficulty. Our g2c data (66K genus-2 Jacobians) can test: CM curves should have extra Hodge classes, verifiable via Frobenius data as Tate conjecture proxy.
**Tensor cell**: OUT_OF_TENSOR.

## Report #76: Goldbach's Conjecture (Charon)
**Problem**: Every even n>2 is sum of two primes
**Key finding**: Ternary proved (Helfgott 2013). Binary: Chen's 1+2 is best. Circle method fails on minor arcs (needs GRH-strength zero-free regions). Verified to 4×10^18. The Goldbach comet's strand structure matches singular series — testable against our L-function data.
**Tensor cell**: OUT_OF_TENSOR.

## Report #77: Twin Prime Conjecture (Charon)
**Problem**: Infinitely many p with p+2 prime
**Key finding**: Gap 246 (Maynard-Polymath8b). Parity barrier is provably insurmountable for sieves alone. EH conjecture would give gap 12. Three Prometheus tests: gap distribution spectroscopy, twin prime density in L-function conductors, parity signal measurement in sieve residuals.
**Tensor cell**: F011 x P023, verdict UNKNOWN.

## Report #78: OSCAR.jl Evaluation (Techne)
**Recommendation**: Phased adoption. (1) Adopt Hecke/Nemo NOW for number fields and class groups — Windows-native, 2-5x faster than Sage. (2) Evaluate full OSCAR in WSL2 for group cohomology and polyhedral geometry. (3) Skip full Windows-native OSCAR until polymake support improves.

## Report #79: SDPA-GMP + SoS Tools (Techne)
**Recommendation**: Evaluate now, adopt selectively. (1) Reproduce Razborov's Caccetta-Haggkvist certificate via flagmatic under WSL2 as validation. (2) Use CSDP/SCS (double precision) for exploration, SDPA-GMP only for certificate promotion. (3) Union-closed 0.38 bound is the calibration target. (4) Defer Ramsey R(5,5) SDP until CKH validated.

## Report #80: Lean4 Ecosystem 2025-2026 (Techne)
**Recommendation**: Build selective pieces now. (1) Install Lean4 + LeanDojo immediately. (2) Deploy DeepSeek-Prover-V2-7B (14-15GB VRAM in bf16 — fits our 17GB card). (3) Use Herald + ProofBridge for autoformalization but budget 50% manual fallback. (4) Pipeline is ready for Mathlib-adjacent conjectures today. Autoformalization of novel conjectures is the gap — improving fast, worth partial adoption now.

---

## Batch 4 Summary

| Metric | Count |
|--------|-------|
| Total reports | 20 (all complete) |
| Problem briefs | 17 |
| Tool evaluations | 3 |
| Mapped to tensor cells | 5 |
| OUT_OF_TENSOR | 12 |
| Assigned Harmonia | 7 |
| Assigned Charon | 6 |
| Assigned Ergon | 4 |
| Assigned Techne | 3 |

### Key Discoveries This Batch
1. **Zauner SIC-POVMs** bridge quantum info ↔ Hilbert's 12th ↔ Stark's conjectures
2. **Grothendieck-Katz** p-curvature IS what our C11 mod-p enrichment detects
3. **M_23** is the only sporadic group unrealized over Q (Inverse Galois)
4. **RH** has no missing calculation — it has a missing geometric object
5. **Union-closed** broken by entropy methods (P22) after 43 years
6. **Collatz** has 4 unmeasured quantities (spectral, tensor, Lyapunov, entropy-by-residue)
7. **OSCAR.jl**: adopt Hecke/Nemo now, defer full stack to WSL2
8. **Lean4 pipeline viable now**: DeepSeek-Prover-V2-7B fits our 17GB VRAM, 65% MiniF2F
9. **SDPA-GMP**: evaluate via Caccetta-Haggkvist certificate first, then expand

### Tool Adoption Roadmap (from 3 evaluations)
| Tool | Action | Timeline |
|------|--------|----------|
| Hecke/Nemo (Julia) | Install NOW | This week |
| Lean4 + LeanDojo | Install NOW | This week |
| DeepSeek-Prover-V2-7B | Deploy for proof search | This week |
| CSDP/SCS (SDP solvers) | Install for flag algebras | Next week |
| SDPA-GMP | Evaluate via CKH | After CSDP validated |
| Full OSCAR.jl | WSL2 evaluation | When specific task demands |

### New Paradigm Connections Found
- P19 (Model-Theoretic): Grothendieck-Katz, Andre-Oort
- P20 (Ergodic): Furstenberg ×2×3, Collatz, MLC
- P22 (Information-Theoretic): Union-closed (Gilmer breakthrough), Furstenberg, Collatz
- P24 (Renormalization): MLC (renormalization cascades)

*Aporia, 2026-04-22 — Batch 4 in progress (80 total reports across 4 batches)*
