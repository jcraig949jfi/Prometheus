# Open Problems in Tensor Mathematics — Consolidated Working Reference v1

**Date filed:** 2026-05-08
**Source:** Deduplicated synthesis of Claude / ChatGPT / Grok / DeepSeek / Gemini lists, with corrected status flags and per-problem attack surfaces. Filed by James 2026-05-08 with the directive: *"Prometheus is going to bathe in tensors long-term. We might as well set them as a high-bar to clear for problem spaces. Treat these as an especially near and dear set of open problems to the heart of Prometheus."*

**Status:** Canonical tensor-open-problems reference for Prometheus. Linked from `aporia/mathematics/lesser_known_open_problems.md`, `aporia/docs/attack_angle_taxonomy.md`, and the `aporia/docs/deep_research_master_index.md`. Future deep-research batches, Substrate-Tester representation-pressure probes (lane 12), and Learner-Tester corpus expansions all draw from this catalog.

**Ongoing pressure infrastructure** (queued post-filing):
- Techne ticket `T-2026-05-08-T038` — classify all 104 entries by substrate-primitive needs; surface capability gaps.
- Ergon ticket `T-2026-05-08-E009` — for each entry with computational hooks, design probe-shape for v1.0 corpus.
- Substrate-Tester lane 12 (representation-pressure): pulls capability-gap objects directly from this catalog.
- Aporia tracking: monthly cross-reference between catalog entries and substrate progress; new entries surfaced by review get appended as v2, v3, etc.

---

*Deduplicated synthesis of Claude / ChatGPT / Grok / DeepSeek / Gemini lists, with corrected status flags and per-problem attack surfaces.*

## Methodology and Status Flags

This document deduplicates ~110 raw entries from five independent surveys into ~85 distinct open problems. Each entry carries: problem statement and current bounds, classification, attack vectors, computational strategies, what resolution opens up, and references/tools. **Important corrections to the source lists** — several "open" problems in the input are in fact resolved; the open versions are stated precisely:

- **Comon's conjecture (original).** Disproven by Shitov (2018). The *border* Comon's conjecture is open.
- **Strassen's additivity for tensor rank.** Disproven by Shitov (2019). Open versions: *border-rank additivity*, and *Waring-rank additivity for forms*.
- **Cap set problem.** Solved (Croot-Lev-Pach, Ellenberg-Gijswijt 2016) via slice rank. Quantitative refinements remain.
- **Tensor rank decidability over ℤ.** Resolved as undecidable (Shitov 2016). Open over ℚ, conditional on Hilbert's tenth problem over ℚ.

A note on tools that recur: TensorLy (Python CP/Tucker/TT), TensorNetwork & ITensor (network contraction), Macaulay2 / Singular / SageMath / Bertini (algebraic geometry & numerical AG), GAP / Magma / LiE / Symmetrica (representation theory and combinatorics), HomotopyContinuation.jl (numerical AG), Tensor Toolbox (MATLAB), JAX / PyTorch (gradient methods on tensor manifolds). Per-problem references list the *specific* most-relevant ones.

---

## I. Foundations: Rank, Border Rank, Asymptotic Complexity

### 1. Matrix multiplication exponent ω
The infimum of τ such that two n×n matrices can be multiplied in O(n^τ) operations. Current bounds 2 ≤ ω ≤ 2.371339 (Alman-Duan-Vassilevska Williams-Xu-Xu-Zhou 2024, arXiv:2404.16349; supersedes prior 2.371552 figure of Duan-Wu-Zhou 2023 / VWXXZ 2024). Equivalent to the asymptotic rank of the matrix multiplication tensor M⟨n⟩. *Algorithm-discovery anchor:* DeepMind AlphaEvolve (May 2024) reported a rank-48 decomposition of the 4×4 matrix multiplication tensor over ℂ, the first improvement over Strassen-recursion's 49 in fifty-plus years for that format; orthogonal to the asymptotic ω bound but a paradigm event for evolutionary-LLM algorithm synthesis. (Updated 2026-05-10 per tensor batch synthesis §2.)
**Class.** Algebraic complexity / asymptotic tensor rank.
**Attack vectors.** Refinements of Strassen's laser method on Coppersmith–Winograd auxiliary tensors. Group-theoretic embedding via Cohn–Umans (find groups with the simultaneous triple product property of the right strength). Asymptotic spectrum: prove additional monotones that pinch ω from below. Construct entirely new auxiliary tensors with high subrank-to-rank ratios.
**Compute.** Low-rank decomposition search via SAT/SMT, gradient methods on Brent equations, or RL (AlphaTensor and successors). Symbolic verification of decompositions in Macaulay2 / Singular over ℚ and finite fields. Numerical homotopy methods (Bertini, HomotopyContinuation.jl) to navigate components of the rank variety.
**Opens.** ω = 2 would settle a half-century-old central question; cascades into linear programming, graph algorithms, neural network training, and circuit complexity. Even partial improvements rewrite practical complexity tables.
**Refs.** Bürgisser-Clausen-Shokrollahi *Algebraic Complexity Theory*; Landsberg *Geometry and Complexity Theory*; AlphaTensor (Fawzi et al., Nature 2022); AlphaEvolve (DeepMind, May 2024) — 4×4 rank-48 over ℂ; Alman-Duan-Vassilevska Williams-Xu-Xu-Zhou 2024 (arXiv:2404.16349); Alman-Williams "A Refined Laser Method" (2021); Vassilevska Williams' survey on matrix multiplication.

### 2. Strassen's asymptotic rank conjecture
Asymptotic tensor rank of every concise tight tensor in ℂ^d⊗ℂ^d⊗ℂ^d equals d. Implies ω = 2 when applied to M⟨2⟩.
**Class.** Asymptotic tensor rank / Strassen's asymptotic spectrum.
**Attack.** Find new monotones in Strassen's asymptotic spectrum. Recent results (Christandl-Hoeberechts-Nieuwboer-Vrana-Zuiddam 2024) show asymptotic rank is characterized by polynomial functionals — exploit this. Reduce to specific tight tensors with rich symmetry (e.g., generalized W tensors).
**Compute.** Numerical optimization over decomposition spaces of tensor powers T^⊗k for moderate k. Symmetry-reduced search (representation-theoretic decomposition before numerical search). Explicit construction of degeneration sequences and verification of subrank bounds.
**Opens.** Direct route to ω = 2 and a dramatic simplification of the spectrum-of-tensors landscape. Reshapes lower bound arguments across complexity theory.
**Refs.** Strassen's foundational papers (1986–1991); Christandl-Vrana-Zuiddam "Universal points in the asymptotic spectrum"; arXiv:2411.15789.

### 3. Asymptotic rank of the small Coppersmith–Winograd tensor T_{cw,2}
Whether the asymptotic rank of T_{cw,2} equals 3 (which would imply ω = 2) or strictly exceeds 3.
**Class.** Specific-tensor asymptotic complexity.
**Attack.** Border apolarity techniques (Buczyńska-Buczyński) to derive sharp lower bounds. Quantum functionals and support functionals (Christandl-Vrana-Zuiddam) applied to T_{cw,q}. Direct search for fast decompositions of T_{cw,2}^⊗k.
**Compute.** Symmetry-aware search exploiting T_{cw,q}'s SL_2-action. Numerical SDP relaxations bounding asymptotic rank. Symbolic computation of moment maps.
**Opens.** Either route gives ω = 2 (if asymptotic rank = 3) or proves a hard barrier to current laser-method approaches (if > 3), reshaping search direction.
**Refs.** Coppersmith-Winograd original; Landsberg-Michałek bad and good news for laser method (arXiv:2009.11391); Conner-Gesmundo-Landsberg-Ventura on laser-method limits.

### 4. Exact rank of the 3×3 matrix multiplication tensor M⟨3⟩
True minimum bilinear complexity. Bounds: 19 ≤ R(M⟨3⟩) ≤ 23. Recent additions-optimized rank-23 schemes don't lower the multiplication count.
**Class.** Exact tensor rank / bilinear complexity.
**Attack.** Tighten lower bounds via substitution methods (Bläser, Landsberg) and apolarity-based obstructions. Improve upper bounds via symmetry-restricted exhaustive search; use cyclic Z/3 symmetry of M⟨3⟩. Apply border-apolarity-style obstruction theory at rank 22 and below.
**Compute.** SAT/SMT solvers over finite fields (modular reductions of Brent equations). Lattice reduction over ternary or low-coefficient solutions. Reinforcement learning with action spaces over rank-r decompositions.
**Opens.** First exact value beyond Strassen's R(M⟨2⟩) = 7. Anchors rank lower-bound technique calibration.
**Refs.** Smirnov 2013 (rank-23 over ℤ); Heun, Ballard-Ikenmeyer-Landsberg-Ryder geometry of decompositions (arXiv:1801.00843); Stapleton 60-addition refinement; Smirnov-style ternary schemes (arXiv:2604.27645).

### 5. Exact border rank of M⟨n⟩ for n ≥ 3
R̲(M⟨2⟩) = 7 known. R̲(M⟨3⟩) ≥ 17 (Landsberg-Michałek), upper bound 21. Wide gap for n ≥ 4.
**Class.** Border rank / secant varieties of Segre varieties.
**Attack.** Border apolarity obstructions (Buczyńska-Buczyński-Galązka). Representation-theoretic obstructions via Young flattenings (Landsberg-Ottaviani). Geometric symmetry reductions exploiting GL_n × GL_n × GL_n action.
**Compute.** Numerical AG: deform into rank decompositions and read off border rank. Symbolic ideal-of-secant-variety computation in Macaulay2. Enumerate B-invariant ideals of fixed multiplicity (border-apolarity algorithm).
**Opens.** Tight lower bound for ω via the rule R̲(M⟨n⟩) ≥ 3n²/2 + n/2 - 1 lineage. Sharp asymptotic estimates for border rank cascade into laser-method tightness.
**Refs.** Landsberg-Michałek "Abelian tensors"; Landsberg "New lower bounds" (arXiv:1911.07981); Bini's degeneration paper (1980).

### 6. Border-rank additivity (Strassen direct sum, border version)
Whether R̲(T₁ ⊕ T₂) = R̲(T₁) + R̲(T₂) holds. Tensor rank version disproven (Shitov 2019). Border-rank version disproven for order ≥ 3 by Schönhage; quantitative gap structure for order ≥ 4 is open.
**Class.** Border rank algebra / direct-sum behavior.
**Attack.** Construct higher-order analogues of Schönhage's order-3 example. Bound subadditivity gaps using asymptotic spectrum monotones. Study direct sums of matrix multiplication tensors specifically.
**Compute.** Numerical search for direct-sum decompositions with rank below R̲(T₁) + R̲(T₂). Symbolic verification using border apolarity tooling.
**Opens.** Even mild quantitative bounds on subadditivity translate directly into laser-method improvements.
**Refs.** Schönhage's τ-theorem (1981); Christandl-Gesmundo-Michałek-Zuiddam "Border rank non-additivity for higher order tensors" (arXiv:2007.05458).

### 7. Border rank multiplicativity under tensor product
Characterize when R̲(T₁ ⊗ T₂) = R̲(T₁) · R̲(T₂) versus strict drops. Strict submultiplicativity exists but is poorly understood.
**Class.** Border rank algebra / asymptotic spectrum.
**Attack.** Catalogue all known submultiplicativity examples (Landsberg-Michałek 3×3 permanent). Derive obstructions through Young flattenings or quantum functionals. Consider tensor squares of small tensors with rich symmetry.
**Compute.** Numerical evaluation of border-rank upper bounds on T^⊗2 for small-format tensors. Symmetry-reduced enumeration via representation-theoretic decomposition.
**Opens.** Cleaner characterization of which tensors can serve as auxiliary tensors in laser-method-style bounds; tightness of asymptotic spectrum framework.
**Refs.** Landsberg-Michałek (arXiv:2009.11391); Conner et al. on small-format products.

### 8. Asymptotic restriction problem
Decide whether T^⊗n can be approximately restricted to S^⊗m for given asymptotic rate m/n. Settles ω as a special case.
**Class.** Asymptotic combinatorics of tensor pre-orders.
**Attack.** Compute restriction monotones (asymptotic spectrum points). Connect to entropy-like quantities via Strassen's representation theorem. Find sufficient conditions through symmetry / representation theory.
**Compute.** Compute Strassen monotones numerically (functions of moment polytopes). Search over restriction maps with small support.
**Opens.** Provides a unified framework that subsumes ω, asymptotic subrank questions, and many quantum-information capacity problems.
**Refs.** Strassen "Asymptotic spectrum of tensors" series; Christandl-Vrana-Zuiddam quantum functionals (arXiv:1709.07851).

### 9. Restriction preorder on small tensors
Combinatorial structure of Strassen's restriction preorder on 3×3×3 tensors over ℂ. Equivalence classes, Hasse diagram, gap sizes.
**Class.** Combinatorics of degenerations / orbit closures.
**Attack.** Enumerate GL₃³-orbits of 3×3×3 tensors (classified by Ng). Build the explicit restriction graph. Use border-apolarity obstructions to certify non-restrictions.
**Compute.** Symbolic enumeration in Macaulay2 / Singular. Numerical degeneration tracking in Bertini.
**Opens.** Cartography of small-tensor space — the discrete substrate underlying the asymptotic spectrum, useful for impossibility-hub style mapping.
**Refs.** Ng "Classification of 3×3×3 tensors"; Bürgisser-Ikenmeyer on orbit closures.

### 10. Bini-style degeneration sequence length
Sharp bounds on the length (degree of ε) of degeneration sequences witnessing border-rank decompositions.
**Class.** Quantitative border rank / approximate decompositions.
**Attack.** Refine Bini's original argument with explicit ε-expansion control. Derive lower bounds via apolarity-based moduli. Connect to algorithm runtime in approximate matrix multiplication.
**Compute.** Symbolic Puiseux-series computations for border-rank decompositions. Numerical fitting of degeneration paths.
**Opens.** Quantitative bridge between border rank and rank, controlling cost of ε-cancellation in laser-method-derived algorithms.
**Refs.** Bini 1980 original; Lehmkuhl-Lickteig 1989; recent border-apolarity literature.

### 11. Limits of the laser method
Whether known laser-method barriers (Ambainis-Filmus-Le Gall, Alman-Vassilevska Williams) are tight, and whether new auxiliary tensors can break them.
**Class.** Algorithmic complexity / laser method analysis.
**Attack.** Construct auxiliary tensors not in the Coppersmith-Winograd family. Refine "value" calculations via global laser-method analyses (Conner-Gesmundo-Landsberg-Ventura). Investigate skew Coppersmith-Winograd tensors.
**Compute.** Numerical and symbolic optimization over auxiliary-tensor parameter spaces. Automated search over compatible tensor families.
**Opens.** Either confirms current barriers as tight (motivating new techniques) or unlocks fresh territory below 2.37.
**Refs.** Ambainis-Filmus-Le Gall (2015); Alman-Williams refined laser method; Conner et al. on asymmetric laser methods.

### 12. Super-linear tensor-rank lower bounds for explicit order-3 tensors
Best known: Ω(n log n / log log n) (Strassen, Lickteig, refined by Bläser, Landsberg). Even Ω(n^{1+ε}) for explicit tensors is open and would imply formula-size lower bounds (Raz).
**Class.** Tensor lower bounds / circuit complexity.
**Attack.** Substitution methods with carefully chosen low-rank slices. Dimension counts on rank-r varieties combined with explicitness barriers. Partial derivatives and apolarity-style techniques.
**Compute.** Verify lower bound techniques on small tensors via SAT. Test candidate hard tensors via gradient descent (negative results = evidence of high rank).
**Opens.** Super-polynomial arithmetic-circuit lower bounds; partial separation of arithmetic complexity classes.
**Refs.** Raz "Tensor-rank and lower bounds for arithmetic formulas"; Shpilka-Yehudayoff arithmetic circuits survey; Hrubeš-Yehudayoff on tensor rank.

## II. The Rank Zoo: Alternative Rank Notions

### 13. Slice rank vs analytic rank gap
Over a fixed finite field 𝔽_q, the analytic rank A(T) and slice rank S(T) of an order-d tensor satisfy S(T) ≤ A(T) ≤ poly(S(T), d). The catalog originally posed the question of whether the polynomial dependence reduces to a constant factor (independent of d). The 2025 frontier subdivides this into four sub-questions, with one direction now negatively resolved. (Updated 2026-05-10 per tensor batch synthesis §2; see also synthesis §2 for the canonical (a)-(d) specification of `RankZooSignature`.)
- **(a) Uniform-in-d direction (partition-rank vs analytic-rank).** *NEGATIVELY-RESOLVED.* Lampert-Moshkovitz (Sept 2025, arXiv:2509.06294) construct an explicit family — built from `det_n` — witnessing that the partition-rank-to-analytic-rank ratio cannot be bounded uniformly in the order d. The "constant-factor independent of d" hope is dead in this direction.
- **(b) Bounded-d direction.** *OPEN.* For each fixed d, sharp constants in A ≤ C_d · S (and in the partition-rank counterpart) remain to be pinned down; current best constants degrade with d.
- **(c) Field-characteristic dependence.** *OPEN.* Whether the gap behavior is uniform across `char 𝔽_q` (or whether small primes / characteristic 0 are pathological) is unsettled; existing log-loss bounds (Cohen-Moshkovitz / Janzer) are field-uniform but the lower-bound constructions are characteristic-sensitive.
- **(d) Effective bound improvements.** *OPEN.* Quantitative refinements of A ≤ S^d (Lovett) and the polynomial bounds of Cohen-Moshkovitz / Janzer — particularly any sub-polynomial improvement for structured (non-generic) tensor families.
**Class.** Tensor structure detectors / additive combinatorics; rank-zoo coordinate separation (HARD-5).
**Attack.** Sharpen the proof of Lovett's bound A ≤ S^d. Improve on Cohen-Moshkovitz / Janzer log-loss bounds. Construct families with maximum A/S ratio. Post-Lampert-Moshkovitz: re-target attack at (b) and (c) — (a) is closed in the negative direction and further work there reduces to refining the explicit `det_n`-based separator.
**Compute.** Compute A and S for small explicit tensors over 𝔽_3, 𝔽_5. Random tensor experiments for typical A/S behavior. Explicit `det_n`-witness reproduction (Lampert-Moshkovitz construction) at moderate n on 𝔽_3.
**Opens.** Tightens the slice-rank method's reach in capset-like problems and unlocks parameter-counting arguments in Gowers-norm theory; (a)'s closure reframes downstream applications (capset quantitative refinements, Gowers-norm inverse theorems) around bounded-d regimes rather than uniform-d guarantees.
**Refs.** Lovett "The analytic rank of tensors"; Cohen-Moshkovitz "Structure vs randomness"; Janzer "Polynomial bound for partition rank in terms of analytic rank"; Lampert-Moshkovitz Sept 2025 (arXiv:2509.06294) — uniform-in-d separator via `det_n`.

### 14. Geometric rank vs partition rank
Geometric rank GR (Kopparty-Moshkovitz-Zuiddam 2020) and partition rank PR (Naslund 2017) for order-d tensors. Sharp polynomial-vs-linear comparison is open.
**Class.** Rank-zoo equivalences.
**Attack.** Derive a direct combinatorial reduction between GR and PR. Test for tensors associated with specific algebraic varieties.
**Compute.** Compute both ranks for small tensors over finite fields. Search for extremal-ratio tensors.
**Opens.** Unified theory of "low-complexity" tensors covering all standard structure detectors.
**Refs.** Kopparty-Moshkovitz-Zuiddam "Geometric rank of tensors and subrank of matrix multiplication"; Naslund slice-rank paper.

### 15. Slice-rank method optimality beyond 𝔽_3
Sharp upper bounds for cap-set-type problems in (ℤ/mℤ)^n for composite m, and over higher-genus rings.
**Class.** Additive combinatorics / slice rank applications.
**Attack.** Generalize Croot-Lev-Pach polynomial method to rings with zero divisors. Tensor-product slice rank constructions across moduli.
**Compute.** Computer searches for cap sets in (ℤ/4ℤ)^n, (ℤ/6ℤ)^n. Polynomial-method computations in computer algebra.
**Opens.** New extremal results across additive combinatorics; possibly improved lower bounds on Roth-type problems.
**Refs.** Ellenberg-Gijswijt cap set; Naslund-Sawin SL₂ trick; Pebody on cap sets in ℤ_4^n.

### 16. Subrank–rank duality / asymptotic spectrum description
Explicit description of all monotone semiring homomorphisms in Strassen's asymptotic spectrum of complex tensors. Currently known points: matrix flattenings, support functionals, Razborov rank functions, slice rank, quantum functionals.
**Class.** Asymptotic spectrum / structural duality.
**Attack.** Construct new monotones from quantum entropy inequalities. Identify representation-theoretic invariants stable under tensor product. Connect to non-commutative algebraic geometry (Schubert-style cells).
**Compute.** Compute candidate monotones on test tensors (W, GHZ, M⟨n⟩, CW). Verify monotonicity numerically over restriction relations.
**Opens.** Fully explicit asymptotic spectrum yields ω = 2 as a corollary if subrank/rank gap closes.
**Refs.** Strassen series 1986–1991; Christandl-Vrana-Zuiddam "Universal points"; Wigderson-Zuiddam survey on the asymptotic spectrum.

### 17. Asymptotic subrank of explicit tensors
Exact asymptotic subrank of the small CW tensor, skew CW tensor, and structured Hadamard tensors.
**Class.** Concrete asymptotic invariants.
**Attack.** Compute via explicit approximate restrictions (degeneration sequences). Use moment polytopes and quantum functionals to bound from above.
**Compute.** Search over approximate restrictions T^⊗n → ⟨q⟩^⊗m. Numerical SDP relaxations on slack matrices.
**Opens.** Direct constants for laser-method bookkeeping; sharp constants in barrier theorems.
**Refs.** Christandl-Vrana-Zuiddam asymptotic spectrum work; Strassen 1991.

### 18. Subspace rank / generalized secant theory
Generalize secant variety bounds via "subspace ranks" (rank with respect to families of subspaces rather than rank-1 elements).
**Class.** Algebraic geometry of tensor varieties.
**Attack.** Build the analogue of Alexander-Hirschowitz for subspaces. Connect to flag-variety embeddings and Schubert calculus.
**Compute.** Macaulay2 packages for secant ideals (e.g., SecantVarieties). Numerical AG via Bertini.
**Opens.** Better lower bounds on tensor rank via subspace defects; cleaner geometric framework for higher-order analogues.
**Refs.** Landsberg *Tensors* §10–12; Bocci-Chiantini secant varieties survey.

### 19. Cactus rank vs rank/border rank
Cactus rank (via 0-dimensional schemes, Buczyńska-Buczyński-Mella) lies between border rank and rank but its exact gaps are open for general tensors.
**Class.** Rank zoo / scheme-theoretic invariants.
**Attack.** Classify schemes that achieve cactus rank but not border rank. Characterize when border rank = cactus rank holds.
**Compute.** Macaulay2 computation of apolar schemes. Construct extremal examples in small format.
**Opens.** Bridges the gap between scheme-theoretic and topological closures of rank loci; clarifies the algebraic-geometric meaning of rank.
**Refs.** Buczyńska-Buczyński "Apolarity, border rank and multigraded Hilbert schemes"; Bernardi-Ranestad cactus rank work.

## III. Symmetric Tensors and Waring Decomposition

### 20. Border Comon's conjecture
For symmetric tensor F ∈ (ℂⁿ)^⊗d, d ≥ 3, whether border rank R̲(F) equals symmetric border rank R̲_S(F). The non-border original was disproven by Shitov; the border version is open even for minimal border rank.
**Class.** Symmetric vs ordinary border rank.
**Attack.** Border apolarity (Buczyńska-Buczyński) for minimal-border-rank case. Reduction to apolar Gorenstein schemes. Deformation theory of secant varieties.
**Compute.** Macaulay2 ideal computations for minimal-border-rank tensors. Test conjecture for tame tensors and small-format examples.
**Opens.** Reconnects symmetric and ordinary border rank under a uniform geometric picture; clarifies which results in symmetric setting transfer to general.
**Refs.** Mańdziuk-Ventura (arXiv:2411.05721); Buczyński-Ginensky-Landsberg "Determinantal equations for secant varieties."

### 21. Symmetric Waring rank classification (Alexander-Hirschowitz extensions)
Generic Waring rank of degree-d forms in n+1 variables is given by Alexander-Hirschowitz; sharp bounds for non-generic forms, and behavior on stratification of singular orbits, remain open.
**Class.** Waring decomposition / secant geometry.
**Attack.** Stratify by symmetry type (Schur-functor decomposition of forms). Refine Terracini's lemma via tangent-cone analysis.
**Compute.** Macaulay2 SecantVarieties; PowerSums package. Numerical decomposition via Bertini.
**Opens.** Classification of generic vs typical vs maximal symmetric ranks for forms — central to identifiability theory.
**Refs.** Alexander-Hirschowitz original; Iarrobino-Kanev *Power Sums*; Landsberg-Teitler "On the ranks and border ranks."

### 22. Waring rank of the permanent
Exact Waring rank of perm_n as a homogeneous polynomial. Tight bounds known only for small n.
**Class.** Specific-form Waring rank / GCT-relevant invariants.
**Attack.** Apolarity-based lower bounds using the apolar ideal of perm_n. Symmetric-flattening lower bounds. Use the GL_n × GL_n × ℤ/2 stabilizer.
**Compute.** Symbolic apolar-ideal computation; Hilbert-function bookkeeping. Numerical Waring decomposition via gradient methods on the secant variety of Veronese.
**Opens.** Direct quantitative input to GCT separation strategies; gap with Waring rank of det_n is geometrically meaningful.
**Refs.** Landsberg-Manivel-Ressayre lower bounds; Mulmuley-Sohoni GCT papers; Aronhold-style invariant theory.

### 23. Waring-rank version of Strassen additivity
For homogeneous forms F, G in disjoint variables, whether Waring rank of F + G equals R_W(F) + R_W(G). The tensor-rank analogue is false (Shitov); the symmetric version remains open in general.
**Class.** Symmetric direct-sum behavior.
**Attack.** Symmetric apolarity refinements; bipartite catalecticant bounds. Look for symmetric analogue of Shitov's construction (likely fails; if so, prove additivity).
**Compute.** Search over candidate Waring decompositions in small-degree settings. Verify in Macaulay2 with Apolarity-package routines.
**Opens.** Different from generic tensor case — would clarify how symmetry constrains decomposition arithmetic.
**Refs.** Carlini-Catalisano-Geramita "Strassen's conjecture for forms"; Teitler additivity surveys.

### 24. Operator norm bounds for random symmetric tensors
Sharp probabilistic bounds on operator norm and (approximate) symmetric rank of isotropic Gaussian symmetric tensors. Existing bounds carry suboptimal log factors.
**Class.** Random tensor analysis / non-asymptotic probability.
**Attack.** Adapt PAC-Bayesian and chaining methods (Boedihardjo-style). Generic chaining and dispersion estimates for tensor-valued processes.
**Compute.** Empirical scaling studies; Monte Carlo on Gaussian ensembles. Compare to predictions from random-matrix universality.
**Opens.** Foundation for tensor PCA, random tensor model bounds, theory of high-dimensional inference.
**Refs.** Bandeira-Dmitriev "Open Problems of 2025" (arXiv:2603.29571); Boedihardjo's tensor concentration paper; Ahlswede-Winter matrix Chernoff.

### 25. Sharp Lp approximate symmetric rank
Bounds on approximate symmetric rank with respect to general Lp norms (currently sharp results limited to Frobenius-style ℓ²).
**Class.** Functional analysis of symmetric tensors.
**Attack.** Interpolate between known ℓ² and ℓ∞ bounds. Use Chevet-Tomczak-style inequalities for tensor norms.
**Compute.** Numerical estimation via sampling on the unit Lp ball. SDP relaxations of Lp-symmetric-rank approximation.
**Opens.** Quantitative theory of approximate Waring decomposition; connections to dispersive PDEs, tensor-PCA-style hypothesis testing.
**Refs.** Bandeira-Dmitriev open problem set; Friedland-Lim norm comparisons.

## IV. Algebraic Geometry: Secant Varieties, Schemes, Apolarity

### 26. Defective Segre-Veronese varieties classification
Classify all defective Segre-Veronese varieties — secant varieties with dimension less than the parameter count predicts.
**Class.** Algebraic geometry / secant defectivity.
**Attack.** Terracini's lemma combined with cohomological dimension counts. Schur-functor decomposition of relevant tensor spaces. Conjectural lists by Abo-Brambilla and follow-ups.
**Compute.** Macaulay2 SecantVarieties; LinearAlgebra packages for Terracini. Bertini for numerical secant dimension.
**Opens.** Classification answers whether non-generic identifiability is possible and where it fails. Direct input to tensor decomposition uniqueness.
**Refs.** Abo-Ottaviani-Peterson; Abo-Brambilla; Catalisano-Geramita-Gimigliano survey.

### 27. Special line bundles on multiprojective spaces
Classify special line bundles on products of projective spaces (and beyond). Closely tied to defectivity.
**Class.** Algebraic geometry of multiprojective spaces.
**Attack.** Cohomological dimension counts via Künneth-type formulas. Connect to tensor decomposition via Terracini's lemma.
**Compute.** Macaulay2 cohomology packages; SchurRings. Hilbert-polynomial computations.
**Opens.** Geometric classification of where Alexander-Hirschowitz-style theorems can extend.
**Refs.** Postinghel cohomological work; Galuppi-Mella-Stagliano; AGATES summer school notes.

### 28. Terracini loci and 0-dim schemes failing independence
For variety X, line bundle L, and integer r, characterize 0-dimensional schemes (unions of degree-2 schemes) failing to impose independent conditions on L while their reduced supports do.
**Class.** Terracini-type defectivity.
**Attack.** Reduce to apolar Gorenstein scheme analysis. Use Hilbert function constraints.
**Compute.** Macaulay2 with Apolarity package. Schemes-on-Veronese explicit computations.
**Opens.** Quantitative refinements of Alexander-Hirschowitz theorem with applications to identifiability.
**Refs.** Chiantini-Ciliberto Terracini loci; Ballico-Bernardi recent work.

### 29. Regularity of minimal apolar schemes
For form F ∈ S^d V with minimal apolar scheme X, whether reg(X) ≤ d. Variants for irredundant or GAD-associated schemes.
**Class.** Castelnuovo-Mumford regularity / apolarity.
**Attack.** Bound regularity via Hilbert function of the apolar ideal F⊥. Use Macaulay's inverse-system theory.
**Compute.** Direct symbolic regularity computation in Macaulay2. Test against tensor decomposition identifiability examples.
**Opens.** Bounds the geometric complexity of optimal Waring decompositions; ties regularity to rank.
**Refs.** Bernardi-Brambilla-Carlini-Ciliberto-Geramita; AGATES notes.

### 30. Generalized additive decompositions (GADs) structure
Structural understanding of decompositions involving powers of linear forms plus higher-rank terms (binomials, etc.) — bridging Waring decomposition and full-rank decomposition.
**Class.** Hybrid decompositions / scheme-theoretic generalization.
**Attack.** Classify minimal-length GADs with specific component types. Connect to classical Apolarity and contemporary cactus rank.
**Compute.** Macaulay2 explicit minimization across GAD structures. Numerical recovery via constrained optimization.
**Opens.** Unified decomposition theory recovering rank, border rank, cactus rank, and Waring rank as special cases.
**Refs.** Bernardi-Iarrobino-Marques; Iarrobino-Kanev; Ranestad-Schreyer.

### 31. Defining equations of higher secant varieties
Explicit ideals (or sharp generation results) for σ_r(Seg(ℙⁿ × ℙⁿ × ℙⁿ)) for r ≥ 4. Salmon problem solved a special case (r = 4 in 4×4×4).
**Class.** Computational algebraic geometry.
**Attack.** Young flattening equations (Landsberg-Ottaviani). Border-apolarity-derived equations. Representation-theoretic decomposition of defining ideal.
**Compute.** Macaulay2 SecantVariety package (large-memory computations). HomotopyContinuation.jl for numerical witness sets.
**Opens.** Computational rank certification; better tensor decomposition algorithms with provable correctness.
**Refs.** Landsberg-Manivel; Friedland-Gross "Generic identifiability"; Sturmfels SemidefiniteProg / Bates-Hauenstein-Sommese-Wampler numerical AG.

### 32. Lower bounds for degrees of higher secant varieties
For secant varieties σ_r of Segre-Veronese, find general lower bounds on degree. Known formulas exist for σ₂; higher r is wide open.
**Class.** Enumerative geometry / secant degrees.
**Attack.** Schubert calculus combined with localization. Eisenbud-Harris-style intersection theory.
**Compute.** Schubert calculus tools (Schubert package in Macaulay2; Sage). Intersection theory in Bertini-style witness sets.
**Opens.** Tighter rank lower bounds; cleaner enumerative invariants for tensor moduli.
**Refs.** Oeding-Sam degrees of Veronese secants; Sturmfels-Sullivant statistical AG.

### 33. Singularities in tensor rank varieties
Characterize singular loci of border-rank varieties σ_r and their resolutions.
**Class.** Geometry of secant varieties.
**Attack.** Resolutions of singularities via blowups. Tangential variety analysis.
**Compute.** Macaulay2 for symbolic resolutions. Numerical witness sets identifying singular components.
**Opens.** Better behaved geometric models for tensor decomposition algorithms; insight into degenerate decompositions.
**Refs.** Holweck-Oeding singularities of secant; Michalek-Sturmfels combinatorial commutative algebra.

### 34. Border-rank variety membership problem
Algorithmic decision problem: given tensor T and integer r, decide whether T ∈ σ_r. NP-hard in general; specific complexity classification open.
**Class.** Computational complexity of algebraic geometry.
**Attack.** Reduction to existential theory of the reals. Witness-encoding via numerical AG.
**Compute.** Bertini / HomotopyContinuation.jl for membership testing. SDP relaxations from sum-of-squares hierarchies.
**Opens.** Algorithmic certification of border-rank lower bounds; foundation for verified-correct tensor decomposition.
**Refs.** Hauenstein-Oeding-Ottaviani-Sommese; Allman-Rhodes algebraic statistics.

### 35. Geometry of the Brent variety
Structure of the variety of rank-r decompositions of M⟨n⟩: connected components, dimensions, singular structure.
**Class.** Moduli of tensor decompositions.
**Attack.** Symmetry-orbit decomposition (cyclic, transpose, GL action). De Groote's theorem and refinements.
**Compute.** Numerical exploration via Bertini. Symmetry-reduced search for decomposition components.
**Opens.** Better-behaved local-search landscapes for fast matrix multiplication; structural insight into the moduli space.
**Refs.** De Groote 1978; Ballard-Ikenmeyer-Landsberg-Ryder "Geometry of rank decompositions" (arXiv:1801.00843); Heun symmetric MM decompositions.

## V. Generic Rank, Maximum Rank, Identifiability

### 36. Maximum rank of 3×3×3 tensors over ℝ
Best known bounds 5 ≤ R_max ≤ 5 over ℂ; over ℝ the maximum rank is known to be at least 5, possibly 6 — exact value open in some conventions.
**Class.** Real vs complex tensor rank / extremal questions.
**Attack.** Catalogue all real Kronecker normal forms of 3×3×3 tensors. Use semialgebraic analysis to certify maxima on real loci.
**Compute.** Symbolic exploration via Cylindrical Algebraic Decomposition (Mathematica, REDLOG). Numerical search for high-rank real tensors.
**Opens.** Foundational data point for the real-vs-complex rank gap; a model for higher-format extremal questions.
**Refs.** Friedland "On generic and typical ranks of 3-tensors" (arXiv:0805.3777); ten Berge typical real ranks.

### 37. Typical (generic) rank classification over ℝ vs ℂ
Over ℂ the generic rank is known (Lickteig). Over ℝ, multiple typical ranks may coexist; full classification is open.
**Class.** Real algebraic geometry of tensors.
**Attack.** Stratify ℝ-rank loci by signature-type invariants. Use real Terracini analysis.
**Compute.** Monte Carlo on Gaussian-random real tensors to detect typical ranks. Witness sets distinguishing typical-rank regions.
**Opens.** Quantitative ℝ-vs-ℂ rank gap; fundamental to applied tensor decomposition over real data.
**Refs.** ten Berge-Friedland-Tsui; Bocci-Chiantini-Mella; Comon-ten Berge real-typical-rank surveys.

### 38. Generic rank of order-d tensors for d ≥ 4
Generic rank for higher-order tensors beyond known Abo-Ottaviani-Peterson cases — particularly subtle for symmetric tensors of high degree and dimension.
**Class.** Algebraic geometry / generic invariants.
**Attack.** Refined Terracini analysis with cohomological vanishing. Specialized methods for very-defective cases.
**Compute.** Macaulay2 numerical certification of generic dimensions. Bertini-based dimension counts.
**Opens.** Closes the Alexander-Hirschowitz program for higher orders; sharpens identifiability bounds.
**Refs.** Abo-Ottaviani-Peterson series; Brambilla-Ottaviani; Catalisano-Geramita-Gimigliano survey.

### 39. Maximal symmetric rank for generic forms
Sharp upper bounds on Waring rank (not just generic rank) for forms of given degree and dimension. Known bounds (Alexander-Hirschowitz, Białynicki-Birula-Schinzel) often loose.
**Class.** Extremal Waring rank.
**Attack.** Apolarity and Macaulay's inverse-system theory. Catalecticant flattening lower bounds combined with sharp constructions.
**Compute.** Symbolic computation of apolar ideals; Hilbert function bookkeeping. Heuristic search for high-rank forms.
**Opens.** Sharp arithmetic complexity bounds for polynomial evaluation; tightness of decomposition algorithms.
**Refs.** Iarrobino-Kanev *Power Sums*; Geramita Inverse Systems; Bernardi-Carlini-Catalisano-Geramita-Gimigliano survey.

### 40. Generic CP identifiability beyond Kruskal
Sharp generic identifiability conditions for CP rank decompositions beyond Kruskal's bound 2r+2 ≤ k₁+k₂+k₃.
**Class.** Identifiability of tensor decompositions.
**Attack.** Improve Kruskal-style bounds via algebraic-geometric flexibility. Use weak identifiability and moduli-of-decompositions arguments.
**Compute.** Bertini for explicit witness uniqueness counts. TensorLy `identifiability` heuristics.
**Opens.** Robust theoretical foundation for parameter recovery in factor models, ML, signal processing.
**Refs.** Domanov-De Lathauwer; Chiantini-Ottaviani; COMON-Mourrain symmetric identifiability.

### 41. Uniqueness in overcomplete CP decompositions
Identifiability and decomposition algorithms in the overcomplete regime r > min(n_i).
**Class.** Overcomplete decomposition theory.
**Attack.** Sum-of-squares relaxations on overcomplete CP. Method of moments combined with smoothed analysis.
**Compute.** Tensor power iteration with restart heuristics. Lasso-style sparse decomposition.
**Opens.** Provably correct overcomplete dictionary learning, ICA, and topic-model recovery.
**Refs.** Anandkumar et al. method-of-moments papers; Ge-Ma-Lyu provable algorithms.

### 42. Block-term decomposition uniqueness
General uniqueness conditions for block-term decompositions beyond De Lathauwer's (L,L,1) and (L_r,L_r,1) special cases.
**Class.** Generalized tensor decompositions.
**Attack.** Mode-product analysis; algebraic-geometric extensions of Kruskal. Sufficient conditions via flattening generic ranks.
**Compute.** TensorLy block-term-decomposition (BTD) modules. Numerical exploration of uniqueness boundaries.
**Opens.** Cleaner theory for hybrid CP/Tucker decompositions used in array processing and biomedical signal analysis.
**Refs.** De Lathauwer BTD papers; Sorensen-De Lathauwer recent extensions.

## VI. Numerical Tensor Decomposition and Approximation

### 43. Existence of best rank-r tensor approximations
For order ≥ 3 and rank ≥ 2, best rank-r approximation may fail to exist (de Silva-Lim 2008). Characterize ill-posed instances and stable substitutes.
**Class.** Numerical analysis / approximation theory.
**Attack.** Use border-rank closure (well-defined) instead of rank. Tucker / hierarchical formats as stable approximants. Restrict to symmetric / orthogonal decompositions where existence holds.
**Compute.** TensorLy + regularization for stable CP fitting. T3F (TT-format) for hierarchical approximations.
**Opens.** Robust, theory-justified workhorse algorithms for applied tensor methods in ML and signal processing.
**Refs.** de Silva-Lim 2008; Hackbusch *Tensor Spaces and Numerical Tensor Calculus*; Comon-Lim-Mourrain symmetric existence.

### 44. Tensor nuclear norm characterization and computation
Tractable analogue of matrix nuclear norm (sum of singular values) for tensors. NP-hard to compute (Friedland-Lim); efficient approximations and dual characterizations are open.
**Class.** Convex analysis of tensor norms.
**Attack.** SDP hierarchies (Lasserre, sums of squares). Lifted convex relaxations using flattenings. Semidefinite programming with symmetry reductions.
**Compute.** Mosek / SDPT3 for SDP relaxations. TT-rank-bounded approximations as proxy.
**Opens.** Tensor analogues of nuclear-norm minimization for completion, denoising, robust PCA.
**Refs.** Friedland-Lim *Nuclear norm of tensors*; Yuan-Zhang on tensor nuclear norm; Nie SDP for symmetric tensor problems.

### 45. Alternating Least Squares (ALS) convergence
Comprehensive convergence theory for ALS in CP decomposition. Known to swamp, stall, and converge to non-optima; conditions for global convergence open.
**Class.** Numerical optimization / non-convex landscapes.
**Attack.** Łojasiewicz inequality on the rank-r manifold. Geometric integration on Grassmannian / Stiefel manifolds.
**Compute.** Gauss-Newton variants (provably faster locally). Riemannian optimization on tangent spaces of fixed-rank manifolds.
**Opens.** Routine, predictable factorization quality in applied ML, signal processing, statistical models.
**Refs.** Comon-Luciani-de Almeida; Uschmajew tensor-rank manifolds; Phan-Tichavský ALS variants.

### 46. HOPM convergence rate
Convergence rate of the Higher-Order Power Method for best rank-1 symmetric tensor approximation.
**Class.** Iterative methods on manifolds.
**Attack.** Lojasiewicz-type analyses; basins of attraction characterization. Smoothed analysis (perturbed initializations).
**Compute.** Numerical convergence diagnostics; phase transitions in test ensembles. Adaptive restart strategies.
**Opens.** Provable best-rank-1 algorithms, rank-1 tensor PCA recovery, signal denoising.
**Refs.** Kolda-Mayo "Shifted power method"; Anandkumar et al. tensor power iteration analysis; Lim singular value of tensors.

### 47. Gauss-Newton convergence basins on fixed-rank manifolds
Provable convergence basins for Gauss-Newton on rank-r tensor manifolds — the analogue of matrix-completion convex-relaxation guarantees.
**Class.** Riemannian optimization.
**Attack.** Restricted isometry-style conditions on tangent spaces. Smoothed analysis with Gaussian initialization.
**Compute.** Manopt / TensorLy Riemannian solvers. Empirical phase-diagram studies.
**Opens.** Polynomial-time provable tensor recovery; robust completion algorithms.
**Refs.** Uschmajew "Local convergence of ALS"; Steinlechner Riemannian preconditioning; Liu-Moitra tensor decomposition.

### 48. CP decomposition condition number bounds
Sharp condition-number bounds for identifiable CP decompositions.
**Class.** Numerical conditioning.
**Attack.** Differential of the decomposition map; Wedin-style sin-θ bounds. Connect to secant-variety geometry (closed-form Frobenius condition number).
**Compute.** Empirical condition-number distributions; near-identifiability boundary mapping. Pre-conditioner design for ALS / GN.
**Opens.** Reliable numerical decomposition with confidence intervals; rigorous error propagation.
**Refs.** Vannieuwenhoven et al. condition numbers; Beltran-Breiding-Vannieuwenhoven.

### 49. Optimal tensor-train rank determination complexity
Decision/optimization complexity of computing the minimal TT-rank vector. Suspected NP-hard but no proof.
**Class.** Tensor-train / hierarchical formats.
**Attack.** Reduction from matrix completion or 3-coloring. Strengthen TT-cross approximation theory.
**Compute.** TT-cross / DMRG-style rank-adaptive algorithms. T3F (TensorFlow), TT-Toolbox (Python).
**Opens.** Provably efficient model selection in TT-format; foundation for quantum simulation algorithms.
**Refs.** Oseledets *Tensor-Train decomposition*; Hackbusch *Tensor Spaces*; Khoromskij *Tensor numerical methods*.

### 50. Tucker compression accuracy/storage tradeoff
Sharp Pareto frontier between approximation error and Tucker-rank-bounded storage. Existing HOSVD bounds are loose by polynomial factors.
**Class.** Approximation theory / dimensionality reduction.
**Attack.** Sharp moment-analysis of randomized Tucker. Connect to multilinear PCA and concentration of measure.
**Compute.** Randomized HOSVD; Halko-Martinsson-Tropp-style sketching. TensorSketch and TensorRandomProjection.
**Opens.** Quantitatively rigorous compression guarantees in scientific computing, neural-net compression, large-scale data.
**Refs.** De Lathauwer-De Moor-Vandewalle HOSVD; Halko-Martinsson-Tropp; Sun-Guo-Tropp Tucker sketching.

### 51. Hackbusch-type conjectures on hierarchical formats
Generalizations of resolved hierarchical-Tucker results to other tree-structured / network formats.
**Class.** Tensor format design.
**Attack.** Tree-decomposition rank inequalities. Quantum-network parallels (MPS, PEPS, MERA).
**Compute.** ITensor (Julia/C++) network manipulation. Hackbusch-style HT-Toolbox.
**Opens.** Format-aware algorithms for high-dimensional PDE discretizations and variational quantum simulation.
**Refs.** Hackbusch-Kühn HT-format; Khoromskij hierarchical methods; Falcó-Hackbusch-Nouy tree formats.

### 52. Nearest supersymmetric tensor approximation
Efficient projection onto the supersymmetric tensor cone — closed-form for matrices, but tensor case has no clean theory.
**Class.** Closest-point on tensor varieties.
**Attack.** SDP-based projection onto symmetric multilinear forms. Reynolds-style symmetrization with approximation guarantees.
**Compute.** Group-averaging projections; Schur-Weyl reduction. Numerical SDP for sym(T) - T minimization.
**Opens.** Stable decomposition under symmetry assumptions; clean algorithms for moment-method ICA, latent-variable models.
**Refs.** Friedland-Stawiska on symmetric tensors; Comon-Sorensen on supersymmetric approximation.

### 53. Tensor completion sample-complexity bounds
Sharp lower bounds on samples needed for exact recovery of a rank-r order-d tensor. Current results have polynomial gaps from suspected optima.
**Class.** Statistical learning theory.
**Attack.** Information-theoretic Fano-type bounds. Restricted-isometry analysis on tensor manifolds.
**Compute.** Empirical phase transitions; T3F-based completion. TensorLy `tensor_completion`.
**Opens.** Theoretically grounded recovery guarantees in recommendation, knowledge graphs, multi-modal data.
**Refs.** Yuan-Zhang sample-complexity papers; Barak-Moitra noisy tensor completion; Cai-Li-Ma theory of tensor completion.

### 54. Multi-way tensor alignment
Optimal transformation aligning N tensors (registration / data fusion). Generalizes Procrustes; non-convex landscape poorly understood.
**Class.** Algorithmic / data fusion.
**Attack.** Sum-of-squares hierarchies on rotation groups. Synchronization on SO(n) and beyond.
**Compute.** TensorFlow-based gradient methods on Stiefel manifold. Burer-Monteiro factorizations of alignment SDPs.
**Opens.** Robust multi-modal data fusion; image / point-cloud / spectral alignment.
**Refs.** Bandeira-Singer-Cucuringu synchronization; Lerman-Shi tensor alignment.

## VII. Decidability and Computational Complexity

### 55. Tensor rank decidability over ℚ
Decidability of tensor rank over the rationals. Conditional on Hilbert's tenth problem over ℚ (still open). Tensor rank over ℤ is known undecidable (Shitov 2016).
**Class.** Mathematical logic / undecidability.
**Attack.** Reduce ℚ-decidability to specific Diophantine sub-problems. Look for decidable fragments (bounded coefficients, fixed format).
**Compute.** Symbolic computation in computer algebra; effective Hilbert10 reductions. Formal-verification of decision procedures (Coq, Lean) for sub-cases.
**Opens.** Status of a foundational decidability question; informs which tensor optimizations admit symbolic algorithms.
**Refs.** Shitov "How hard is the tensor rank?" (arXiv:1611.01559); Hillar-Lim "Most tensor problems are NP-hard."

### 56. Symmetric tensor rank NP-hardness (Hillar-Lim conjecture)
Hillar-Lim 2013 (*Most tensor problems are NP-hard*) established NP-hardness for tensor-rank computation over ℝ; that result remains the canonical anchor and stands. The closely-coupled question of **symmetric-rank-over-ℚ** is **SETTLED** by Shitov (2016, *How hard is the tensor rank?*, arXiv:1611.01559) — the proof reduces tensor rank over an integral domain to systems of polynomial equations, then specializes to symmetric tensors. Tensor rank over ℤ is **undecidable** by the same construction (answers Gonzalez–Ja'Ja' 1980). (Updated 2026-05-11 — citation arXiv:1611.01559 corrected per Wave 1 anti-anchor verification; prior arXiv:1605.07532 was wrong, points to a PDE paper.) The remaining open frontier under this entry: sharp parameterized / approximation-hardness for symmetric rank (e.g., constant-factor approximation algorithms vs. APX-hardness), and the analogous decidability picture over number fields beyond ℚ.
**Class.** Computational complexity of tensor problems; `ComputationalComplexityCertificate` Tier-B sub-primitive (synthesis §3.2).
**Attack.** Reduction from clique / 3-SAT through symmetric flattenings. Use Waring rank lower bounds as gadgets. For approximation-hardness frontier: PCP-style reductions from gap-3SAT.
**Compute.** Empirical hardness; reduction certificates. Sum-of-squares lower bounds.
**Opens.** Foundation for parameterized / approximation hardness in algebraic complexity; Shitov 2016 closure of the ℚ direction unblocks downstream `∃ℝ`-vs-NP separation work in the rank zoo.
**Refs.** Hillar-Lim 2013 *Most tensor problems are NP-hard*; Schaefer-Štefankovič NP-hardness refinements; Shitov 2016 *How hard is the tensor rank?* (arXiv:1611.01559) — settles symmetric-rank-over-ℚ; tensor rank over ℤ undecidable as a corollary.

### 57. Constant-factor approximation algorithms for tensor rank
Polynomial-time algorithms with provable constant approximation for tensor rank.
**Class.** Approximation algorithms.
**Attack.** LP / SDP relaxations bounding rank. Structural decomposition + heuristic rank estimation.
**Compute.** Sum-of-squares hierarchies. Gradient methods on rank surrogates.
**Opens.** Practical certified-bound rank estimation; cleaner heuristics with guarantees.
**Refs.** Barak-Brakensiek-Moitra; Schramm-Steurer; Bhattiprolu et al. rank approximation.

### 58. Tensor isomorphism complexity
Complexity of testing isomorphism for 3-tensors under group actions (GL₃, S_n, etc.). Captures many algebraic-structure problems; suspected GI-hard.
**Class.** Algebraic complexity / cryptography-relevant.
**Attack.** Reduction from Group Isomorphism / Code Equivalence. Tensor congruence via Smith normal form for matrix pencils (order-3 special case).
**Compute.** Magma / GAP for small tensors. Specialized algorithms for slim slices.
**Opens.** Foundation of post-quantum cryptography candidates (MEDS, ALTEQ); clear complexity-theoretic placement.
**Refs.** Grochow-Qiao tensor isomorphism series; Ji-Qiao-Song-Yun complexity; Ivanyos-Karpinski-Saxena MinRank.

### 59. Hyperdeterminant decision problems
Hardness of deciding hyperdeterminant zero / approximation. NP- and #P-hardness suspected; tight classifications open.
**Class.** Complexity of algebraic invariants.
**Attack.** Reduction from VPSPACE problems. Schwartz-Zippel-style polynomial identity testing.
**Compute.** Symbolic resultant computations (Schläfli's hyperdeterminant). SAT-encoded zero-test for low formats.
**Opens.** Complete picture of which tensor invariants are tractable.
**Refs.** Gelfand-Kapranov-Zelevinsky *Discriminants, Resultants, and Multidimensional Determinants*; Holweck-Luque-Thibon entanglement invariants.

### 60. Holant problem classification
Complexity dichotomy for Holant / tensor-contraction counting problems. Partial dichotomies known; complete classification open.
**Class.** Complexity of counting problems.
**Attack.** Holographic algorithms (Valiant); signature theory. Polynomial-method complexity dichotomies.
**Compute.** Specialized solvers for Holant frameworks. Tensor-network-contraction complexity software.
**Opens.** Unified complexity classification of partition functions, statistical-mechanics counts, quantum-amplitude evaluation.
**Refs.** Cai-Lu-Xia Holant series; Valiant *Holographic algorithms*; Backens unified diagrammatic approach.

### 61. Decidable fragments of tensor rank theory
Quantifier-free fragments of the existential theory of tensor rank over ℝ, ℂ, ℚ that admit algorithms.
**Class.** Effective real algebraic geometry.
**Attack.** Cylindrical algebraic decomposition with format-specific shortcuts. Combine with witness-set approaches in numerical AG.
**Compute.** REDLOG, QEPCAD, Mathematica `Resolve`. Bertini's positive-dimensional witness sets.
**Opens.** Tractable verification subroutines for rank-bound certification.
**Refs.** Basu-Pollack-Roy *Algorithms in Real Algebraic Geometry*; Hauenstein-Sottile real-AG numerical tools.

### 62. Real vs complex rank gap
Gap between R_ℝ(T) and R_ℂ(T) for specific structured families.
**Class.** Real-AG / typical-rank theory.
**Attack.** Stratify by Galois-action invariants. Use signature-bounded apolarity.
**Compute.** Numerical real decompositions; Galois-orbit counting. ten Berge-style typical-rank simulation.
**Opens.** Quantitative theory of real tensor decomposition with applications to real-data ML and stats.
**Refs.** ten Berge; Friedland-Stawiska; Comon-Lim-Liu-Mourrain.

## VIII. Spectral and Eigenvalue Theory

### 63. Variational characterization of tensor eigenvalues
Complete variational principles (Min-Max, Courant-Fischer, etc.) for H-, Z-, ℓ_p-, and other tensor eigenvalue notions.
**Class.** Spectral theory of tensors.
**Attack.** Lagrangian duality with constraint manifolds. Convex relaxations via SDP hierarchies.
**Compute.** Numerical eigenvalue solvers (TenEig, NCpol2sdpa, Lasserre hierarchies). Polynomial homotopy continuation.
**Opens.** Unified spectral perturbation theory for tensors, multi-stationary equilibria in dynamical systems.
**Refs.** Qi-Luo *Tensor Analysis*; Lim "Singular values and eigenvalues of tensors"; Chen-Ng-Qi review.

### 64. Number of real eigenvalues of symmetric tensors
Sharp upper / lower bounds on real eigenvalue count. Cartwright-Sturmfels gives complex count; real refinements partial.
**Class.** Real algebraic geometry of polynomial systems.
**Attack.** Real-AG dimension bounds via Khovanskii-Rolle. Newton-polytope analysis.
**Compute.** Bertini real solutions; HomotopyContinuation.jl. Symbolic resultant analysis.
**Opens.** Stability analysis of multilinear dynamical systems; counting real solutions in physics.
**Refs.** Cartwright-Sturmfels eigenvalue count; Friedland-Mehrmann-Pajarola real eigenvalues.

### 65. Geometric multiplicity for tensor eigenvalues
Definition of "multiplicity" for tensor eigenvalues that behaves correctly under perturbation (analogous to matrix algebraic multiplicity).
**Class.** Spectral perturbation theory.
**Attack.** Define via dimension of associated eigen-variety. Connect to tropical / Newton-polytope multiplicities.
**Compute.** Symbolic Gröbner basis for eigen-ideal. Numerical certification of multiplicities.
**Opens.** Robust perturbation theory for tensor PCA, multi-array spectral methods.
**Refs.** Qi *Eigenvalues of a real supersymmetric tensor*; Cartwright-Sturmfels.

### 66. Z-eigenvalue distribution
Distribution and counting of Z-eigenvalues for symmetric tensors.
**Class.** Random tensor spectral theory.
**Attack.** Kac-Rice formula on appropriate manifold. Random matrix theory adaptations.
**Compute.** Empirical Z-eigenvalue histograms via Monte Carlo. Wirtinger-flow-style numerical extraction.
**Opens.** Statistical foundation for tensor spectral methods; tensor PCA with Z-eigen formulation.
**Refs.** Qi Z-eigenvalue series; Auffinger-Ben Arous random tensor critical points.

### 67. Tensor spectral norm approximation
Polynomial-time approximation of the spectral norm of order-3 tensors. Currently known NP-hard; FPRAS / constant-factor approximation status unclear.
**Class.** Approximation of tensor invariants.
**Attack.** SDP rounding (Goemans-Williamson-style for tensors). Sum-of-squares hierarchies.
**Compute.** Lasserre hierarchies via Yalmip / Mosek. Tensor-power iteration with verification.
**Opens.** Practical certified bounds for tensor PCA, hardness of approximation, robust optimization.
**Refs.** Hillar-Lim NP-hardness; Bhattiprolu-Ghosh-Guruswami-Lee; Barak-Moitra.

### 68. Tensor Perron-Frobenius theory extension
Extend Perron-Frobenius theorem to broader nonnegative tensor classes beyond the irreducible / weakly-irreducible cases.
**Class.** Nonnegative tensor spectral theory.
**Attack.** Generalize Birkhoff-Hilbert metric arguments. Multilinear Collatz-Wielandt formulas.
**Compute.** Numerical Perron-vector iteration; convergence diagnostics. Reducibility detection via graph-theoretic algorithms.
**Opens.** Nonnegative tensor spectral methods; population dynamics, hypergraph eigenvalue theory.
**Refs.** Friedland-Gaubert-Han; Chang-Pearson-Zhang Perron-Frobenius for tensors; Lim singular value theory.

### 69. Positive definiteness check for even-order tensors
Polynomial-time algorithm for deciding whether a symmetric even-order tensor is positive definite. NP-hard in general (Hillar-Lim) but polynomial cases sought.
**Class.** Tensor convex analysis.
**Attack.** Sum-of-squares hierarchies (always succeeds in finite levels but bounded levels open). Special structure: Hankel / Toeplitz / sparse tensors.
**Compute.** SDP solvers (Mosek) with SOS hierarchies. Specialized Hankel/Toeplitz solvers.
**Opens.** Stability analysis in nonlinear elasticity, polynomial optimization, tensor-completion proofs.
**Refs.** Qi-Wang-Wang positive definiteness papers; Lasserre *Moments, Positive Polynomials and Their Applications*.

### 70. Nonnegative tensor (p,q)-spectral radius
Sharp inequalities relating the (p,q)-spectral radius and largest H- / Z-eigenvalue of nonnegative tensors.
**Class.** Spectral inequalities for tensors.
**Attack.** Hölder-style inequalities; multilinear generalizations of Friedland-Karelin. Convex duality.
**Compute.** Numerical experiments establishing sharpness. Symbolic verification on small symmetric examples.
**Opens.** Quantitative bounds in hypergraph spectral graph theory and nonnegative matrix theory's tensor analogue.
**Refs.** Qi *H-eigenvalues*; Chang-Qi-Zhang nonnegative tensors review.

## IX. Random Tensors and Probabilistic Problems

### 71. Sharp non-asymptotic operator-norm bounds for random tensors
Eliminate suboptimal log factors in operator norm of order-d random tensors with i.i.d. entries.
**Class.** Random tensor concentration.
**Attack.** Generic chaining; Talagrand-type majorizing measures for tensor processes. PAC-Bayesian argument adaptations (Bandeira-Boedihardjo).
**Compute.** Monte Carlo estimation of typical norms. Empirical comparison to theoretical bounds.
**Opens.** Foundation for tensor PCA, dispersive PDE estimates, Banach-space geometric type-2 constants.
**Refs.** Bandeira et al. tensor concentration; Boedihardjo independent-entry tensors; Vershynin *High-Dimensional Probability*.

### 72. Type-2 constant of tensors (Bandeira-Dmitriev)
Sharp scaling for sums of Gaussian-weighted symmetric tensors — the tensor analogue of matrix Bernstein.
**Class.** Banach-space geometry of tensor norms.
**Attack.** Adapt Tomczak-Jaegermann / Ahlswede-Winter to higher order. Explicit construction of type-2 witnesses.
**Compute.** Random ensembles, Monte Carlo type-2-constant estimates. Empirical scaling laws across order d.
**Opens.** Cleanly resolves coding-theoretic, dispersive-PDE, tensor-PCA, Gaussian-process bounds simultaneously.
**Refs.** Bandeira-Dmitriev "Open Problems of 2025" (arXiv:2603.29571); Tomczak-Jaegermann original; Ahlswede-Winter matrix Chernoff.

### 73. Tensor PCA computational threshold
Sharp characterization of statistical-vs-computational gaps in spiked tensor recovery (sub-Wigner spike model).
**Class.** High-dimensional statistics / planted-problem hardness.
**Attack.** Sum-of-squares lower bounds (Hopkins-Steurer-Steinhardt-Schramm). Low-degree likelihood-ratio arguments.
**Compute.** Empirical phase transitions across (n, d, signal strength) grids. AMP iterations and tensor power method.
**Opens.** Provable threshold characterization; tensor-PCA-style algorithms for unsupervised learning.
**Refs.** Richard-Montanari original tensor PCA; Hopkins-Steurer-Schramm low-degree; Wein-El Alaoui-Moore.

### 74. Colored random tensor model continuum limit
Existence of continuum limit and universality classes for colored / multi-trace random tensor models in mathematical physics.
**Class.** Mathematical physics / random geometry.
**Attack.** 1/N expansion beyond melonic dominance. Phase-transition analysis via combinatorial maps.
**Compute.** Monte Carlo on random tensor ensembles. Symbolic / combinatorial enumeration of melonic-vs-non-melonic terms.
**Opens.** Quantum gravity and emergent geometry from tensors; new universality classes beyond random matrix theory.
**Refs.** Gurau *Random Tensors*; Bonzom-Gurau-Riello-Rivasseau; Witten on SYK and tensor models.

## X. Quantum Information and Tensor Networks

### 75. Area law conditions for quantum systems
Necessary and sufficient conditions for ground states / Gibbs states to satisfy entanglement area laws.
**Class.** Quantum many-body physics / entanglement structure.
**Attack.** Lieb-Robinson bounds in higher dimension. Local-Hamiltonian gap-vs-area-law dichotomies.
**Compute.** DMRG / TEBD / iPEPS for empirical area law verification. ITensor (Julia/C++) and TenPy (Python) workflows.
**Opens.** Justifies efficient tensor-network simulation in 2D and 3D; complexity classification of quantum systems.
**Refs.** Hastings area law (1D); Eisert-Cramer-Plenio area-law review; Anshu-Arad-Gosset 2D progress.

### 76. PEPS contraction complexity
Complexity of contracting projected entangled pair states in useful generality. Exact contraction is #P-hard; approximate cases open.
**Class.** Quantum tensor-network complexity.
**Attack.** Approximation hardness via post-BQP reductions. Boundary-MPS / CTMRG approximation theorems.
**Compute.** iPEPS / boundary-MPS via TenPy, ITensor. Variational methods: Variational PEPS energy minimization.
**Opens.** Honest theory of which 2D quantum problems are tractable; bridges quantum complexity to tensor-network practice.
**Refs.** Schuch-Wolf-Verstraete-Cirac PEPS hardness; Verstraete-Murg-Cirac PEPS review; Haghshenas et al. variational PEPS.

### 77. Tensor network expressibility characterization
Which quantum states admit efficient tensor-network representation.
**Class.** Quantum-state complexity / approximation theory.
**Attack.** Entanglement-entropy scaling characterizations. Holographic codes and stabilizer formalism.
**Compute.** Empirical compression studies; rank-truncation accuracy. TensorNetwork (Google), ITensor variational fits.
**Opens.** Routes from physics intuition to provable simulation algorithms; characterization of "easy" quantum states.
**Refs.** Verstraete-Cirac-Murg review; Cirac-Pérez-García-Schuch-Verstraete *Matrix product states and projected entangled pair states*.

### 78. Holographic tensor network correspondence
Whether spacetime geometry in AdS/CFT fully emerges from entanglement tensors.
**Class.** Mathematical physics / quantum gravity.
**Attack.** HaPPY codes and stabilizer holography. Random tensor network bulk reconstruction.
**Compute.** Holographic entanglement entropy via numerical stabilizer codes. Random tensor network sampling.
**Opens.** Conceptual framework for emergent spacetime; constraints on quantum gravity theories.
**Refs.** Pastawski-Yoshida-Harlow-Preskill HaPPY; Hayden-Nezami-Qi-Thomas-Walter-Yang random tensor networks; Almheiri-Dong-Harlow.

### 79. SLOCC entanglement classification for n ≥ 5 qubits
Classify multipartite entanglement under stochastic local operations and classical communication for n ≥ 5 qubits — no finite parameterization known.
**Class.** Quantum information / algebraic geometry.
**Attack.** Geometric invariant theory (GIT) on the projective Hilbert space. Hilbert series computations; orbit-closure stratification.
**Compute.** Macaulay2 GIT package; Magma invariant rings. Numerical orbit detection.
**Opens.** Classification of multi-qubit resource theories; foundation for entanglement-based protocols.
**Refs.** Verstraete-Dehaene-De Moor-Verschelde (3-qubit); Lamata et al. 4-qubit; Holweck-Luque-Thibon higher-qubit.

### 80. Entanglement polytope characterization
For tensor representing a quantum state, compute the polytope of possible reduced density operator spectra.
**Class.** Quantum information geometry.
**Attack.** Connect to moment polytopes via Klyachko / Berenstein-Sjamaar. Use one-body quantum marginal problem techniques.
**Compute.** Polymake / Sage polytope computations. Numerical entropy / spectrum sampling.
**Opens.** Resource-theoretic capacity bounds; experimental certification of entanglement type.
**Refs.** Walter-Doran-Gross-Christandl entanglement polytopes; Klyachko marginal problem; Aulbach-Markham-Murao.

### 81. Most-entangled state identification
Tensor maximizing a given entanglement measure within a fixed Hilbert space.
**Class.** Quantum optimization / entanglement.
**Attack.** Variational ansätze; tensor-power iterations. Connection to maximally entangled states for specific monotones.
**Compute.** Riemannian optimization on projective Hilbert space. TensorFlow / PyTorch entanglement-measure optimizers.
**Opens.** Resource benchmarking; theoretical references for experimental quantum advantage.
**Refs.** Brierley-Higuchi maximally entangled state; Goyeneche-Życzkowski; Chen et al. on AME states.

### 82. Geometry of tensor network manifolds
Differential-geometric structure of state manifolds parameterized by tensor networks.
**Class.** Quantum information geometry.
**Attack.** Riemannian metric induced by quantum Fisher information. Connect to natural-gradient methods.
**Compute.** Manopt / TensorLy on tensor-network manifolds. Variational quantum simulation gradient methods.
**Opens.** Natural-gradient algorithms for variational quantum simulation, MPS/PEPS optimization.
**Refs.** Haegeman-Verstraete TDVP; Hackl-Guaita-Cirac-Bianchi geometry of variational manifolds.

### 83. Tensor network contraction with signs
Hardness of contracting tensor networks with negative entries (sign problem).
**Class.** Computational hardness of tensor contraction.
**Attack.** BQP / postBQP reductions for sign-problem-afflicted systems. Stoquastic-vs-non-stoquastic dichotomies.
**Compute.** DMRG, QMC for sign-problem-free systems. Auxiliary-field QMC for fermionic problems.
**Opens.** Foundational understanding of when classical simulation is hard; routes around sign problems.
**Refs.** Troyer-Wiese sign-problem hardness; Hastings on sign problems; Marvian-Lidar SU(2) sign-free.

### 84. Optimal tensor network contraction order
Find optimal contraction order minimizing memory / FLOPs. NP-hard in general (Markov-Shi); approximation algorithms with sharp guarantees open.
**Class.** Combinatorial optimization / algorithm engineering.
**Attack.** Tree decomposition / treewidth-based algorithms. Branch-and-bound with good heuristics.
**Compute.** opt_einsum (Python); cotengra; TensorNetwork. Genetic / RL-based contraction-order search.
**Opens.** Practical TN simulation speedups by orders of magnitude; quantum-circuit simulation acceleration.
**Refs.** Markov-Shi NP-hardness; Gray-Kourtis cotengra; Pfeifer-Haegeman-Verstraete optimal TN.

### 85. Zauner's conjecture / SIC-POVMs
Existence of equiangular tight frames with d² vectors in ℂ^d for every d.
**Class.** Quantum information / algebraic number theory.
**Attack.** Stark-conjecture-based constructions (Appleby-Flammia-Kopp). Class-field-theory / Heisenberg-orbit analysis.
**Compute.** High-precision numerical SIC-fiducial computations. Computer algebra search in number fields.
**Opens.** Quantum tomography, foundations, and a number-theoretic miracle linking quantum geometry to abelian extensions.
**Refs.** Zauner thesis; Appleby-Flammia-Kopp Stark conjecture work (arXiv); Scott-Grassl SIC-POVM database.

## XI. Specific Tensor Families

### 86. Tensor rank of det_n and perm_n
Exact tensor rank of the determinant and permanent regarded as multilinear forms / multi-tensors.
**Class.** Specific-tensor algebraic complexity.
**Attack.** Leverage stabilizer GL_n × GL_n × ℤ/2. Apolarity-based lower bounds; flattening ranks.
**Compute.** Brent-equation search with symmetry constraints. Symbolic verification of explicit decompositions.
**Opens.** Direct quantitative input to GCT permanent-vs-determinant separation strategies.
**Refs.** Landsberg-Manivel-Ressayre; Mulmuley-Sohoni; Kumar-Saraf-Saptharishi rank lower bounds.

### 87. Tensor rank of multidimensional DFT
Tensor rank of the multidimensional discrete Fourier transform tensor for d ≥ 3 dimensions.
**Class.** Algorithmic / specific tensor rank.
**Attack.** Cooley-Tukey-style decomposition refinements. Group-algebra structure (DFT as multiplication tensor of cyclic groups).
**Compute.** Search for fast-DFT algorithms via Brent equations. Symmetry-reduced exhaustive search.
**Opens.** Fundamentally new fast-DFT algorithms; direct impact on signal processing complexity.
**Refs.** Heideman-Burrus DFT algorithms; Pan computational complexity of polynomials.

### 88. Tensor rank of group-algebra multiplication
Exact tensor rank of multiplication in 𝔽[G] for non-abelian G as a function of |G| and representation theory.
**Class.** Algorithmic algebra.
**Attack.** Wedderburn decomposition + rank estimates per matrix block. Cohn-Umans triple-product property analysis.
**Compute.** GAP / Magma representation-theoretic decomposition. Specialized Brent-equation solvers per group.
**Opens.** Cleaner Cohn-Umans-style approaches to ω; quantum algorithm parallels.
**Refs.** Cohn-Kleinberg-Szegedy-Umans group-theoretic MM; Hopcroft-Kerr.

### 89. Cohn-Umans triple product property
Whether some finite group family realizes simultaneous triple product property strongly enough to imply ω = 2.
**Class.** Group-theoretic matrix multiplication.
**Attack.** Construct specific groups (e.g., based on uniquely solvable puzzles). Probabilistic constructions in finite simple groups.
**Compute.** GAP / Magma exhaustive search in specific group families. Random group constructions.
**Opens.** Alternative route to ω = 2 entirely independent of laser method.
**Refs.** Cohn-Umans original; Cohn-Kleinberg-Szegedy-Umans; Blasiak-Church-Cohn-Grochow-Naslund-Sawin-Umans negative results.

### 90. Schönhage τ-theorem optimization
Optimal asymptotic constants in partial matrix multiplication constructions.
**Class.** Asymptotic complexity bookkeeping.
**Attack.** Sharper τ-theorem analyses with multi-aspect-ratio partial MM. Asymmetric laser methods.
**Compute.** Symbolic / numerical optimization of τ-theorem parameters. Database search in partial-MM-tensor space.
**Opens.** Direct ω improvements via optimized partial-MM gadgets.
**Refs.** Schönhage 1981 original τ-theorem; Conner et al. asymmetric laser method.

### 91. Explicit high-rank tensor construction
Construct explicit tensor families with tight rank or border rank lower bounds beyond current best (e.g., breaking ratio R̲ ≥ 3 obstructions).
**Class.** Lower-bound construction.
**Attack.** Combinatorial designs (codes, expanders) embedded as tensors. Iterated tensor products of structured tensors.
**Compute.** Symbolic verification of border-apolarity-based lower bounds. Combinatorial searches over candidate tensor families.
**Opens.** First super-polynomial circuit lower bounds; concrete witnesses to barriers in lower-bound techniques.
**Refs.** Raz "Tensor-rank and lower bounds"; Forbes-Shpilka rank lower bounds; Bürgisser-Ikenmeyer-Lysikov.

## XII. Geometric Complexity Theory and Representation Theory

### 92. GCT VP vs VNP via padded permanent
Whether the orbit closure of the padded permanent is contained in that of the determinant — the central remaining barrier of the Mulmuley-Sohoni program. (Updated 2026-05-10 per tensor batch synthesis §2; cross-link to anti-anchor pins in synthesis §4.)
**Status notes (2024-2026 frontier).**
- **Lower-bound state.** The Mignon-Ressayre `n²/2` bound (Mignon-Ressayre 2004, IMRN) remains the current best unrestricted lower bound on `dc(perm_n)` and has stood for 22 years. No general-model improvement since.
- **Equivariant exponential is restricted-model only.** Landsberg-Ressayre 2017 (arXiv:1508.05788) gives an exponential lower bound on `dc(perm_n)` *restricted to the equivariant model*; this is NOT an unrestricted lower bound. Substrate must carry the `restricted_to: SymmetryGroup` annotation (synthesis §3.2 `EquivariantComplexityCertificate`) and refuse to extrapolate. (HARD-5 / PATTERN_RANK_PARITY_LEAK at the model-restriction layer.)
- **Occurrence obstructions are dead.** Bürgisser-Ikenmeyer-Panova (BIP, *Journal of the AMS* 2019, arXiv:1604.06431) proved that **occurrence obstructions cannot separate the determinant orbit closure from the padded-permanent orbit closure** for the relevant parameter regime. This kills the original Mulmuley-Sohoni occurrence-obstruction route. Anti-anchor PATTERN_GCT_OCCURRENCE_DEAD: substrate-tester sentinel rejects any agent attempt to construct an `OccurrenceObstruction` for `(det_m, padded_perm_{n,m}, m=poly(n))`.
- **Surviving GCT obstruction sub-types.** Multiplicity obstructions, vanishing-ideal obstructions, outside-orbit obstructions, and equivariant obstructions (the four non-occurrence subtypes of `GCTObstructionCertificate`, synthesis §3.2) remain open. No concrete obstruction has been constructed since 2020. Do not mistake "GCT survives" for "GCT has produced a separator."
**Class.** Geometric complexity theory; `OrbitClosureNonMembershipWitness`, `GCTObstructionCertificate` (composite Tier-B/E, ×5 sub-types), `BorderComplexitySeparator`, `EquivariantComplexityCertificate`, `AlgebraicNaturalProofsBarrier` (synthesis §3.2 / §3.4).
**Attack.** Plethystic decomposition obstructions for the surviving (non-occurrence) sub-types. Search for Kronecker / plethysm coefficients separating multiplicities. Newton-polytope and moment-map arguments. Cross-route weighting: per HARD-2, equal-or-higher weight on non-GCT routes (LST/Forbes 2024, Bhattacharjee 2024, Kumar-Volk 2021) before committing GCT-only effort.
**Compute.** Schur ring / SchurRings package in Macaulay2. LiE / Symmetrica for plethysm.
**Opens.** Polynomial vs exponential lower bounds; first algebraic-circuit super-polynomial separations. Even modest progress past Mignon-Ressayre `n²/2` in the unrestricted model would be a 22-year breakthrough.
**Refs.** Mulmuley-Sohoni *Geometric complexity theory* I-VIII; Mignon-Ressayre 2004 IMRN — `n²/2` lower bound on `dc(perm_n)`; Landsberg-Ressayre 2017 (arXiv:1508.05788) — equivariant exponential, restricted-model only; Bürgisser-Ikenmeyer-Panova 2019 J. AMS (arXiv:1604.06431) — occurrence obstructions killed for det/padded-perm; Ikenmeyer-Panova plethystic obstructions; cross-link to entry 95 (Saxl / Kronecker positivity, including Ikenmeyer-Mulmuley-Walter NP-hardness of Kronecker-positivity).

### 93. Orbit closure containment problem
For tensors / forms T and S under group action G, decide whether G·T ⊆ G·S̄ (orbit closure).
**Class.** Algebraic complexity / GIT.
**Attack.** Mumford's GIT and Hilbert-Mumford numerical criterion. Moment-map approaches.
**Compute.** Numerical orbit-closure detection via tropical geometry. Symbolic invariant ring computations.
**Opens.** Routine certification of complexity-theoretic reductions; foundation of GCT.
**Refs.** Mulmuley GCT; Bürgisser-Garg-Oliveira-Walter-Wigderson alternating-minimization for moment maps.

### 94. Moment polytope classification
Achievable spectra / orbits arising from tensor actions: explicit description of moment polytopes for general tensor formats.
**Class.** Geometric invariant theory.
**Attack.** Berenstein-Sjamaar / Klyachko sufficient conditions. Saturation-style theorems for tensor-product polytopes.
**Compute.** Polymake; Sage polytope packages. Numerical / combinatorial moment-polytope enumeration.
**Opens.** Quantum marginal problem; entanglement-polytope theory; Horn-style inequalities for tensors.
**Refs.** Berenstein-Sjamaar; Klyachko quantum marginals; Walter quantum-polytope thesis.

### 95. Kronecker coefficient vanishing/positivity
Decide when Kronecker coefficients g(λ, μ, ν) vanish / are positive. #P-hard in general; combinatorial interpretation a major open problem. (Updated 2026-05-10 per tensor batch synthesis §2.)
**Status notes (Mulmuley `PH1` falsified).** The Mulmuley `PH1` route — which would have routed Kronecker positivity into the polynomial hierarchy — was **falsified** by Ikenmeyer-Mulmuley-Walter, who proved Kronecker positivity is **NP-hard**. This eliminates the original GCT-program hope that Kronecker positivity admits an efficient verifier. Combinatorial interpretation (LR-rule analogue) and quantitative vanishing remain wide open. See entry 99 (Saxl conjecture) for a related positivity question — Saxl proper remains OPEN as of 2026-05-11 (Lee 2025 arXiv:2512.15035 was withdrawn within 3 days; Luo-Sellke 2017 proved only the fourth-power relaxation; 2022 follow-on tightened to the cube). (Updated 2026-05-11 per Wave 1 anti-anchor verification.)
**Class.** Algebraic combinatorics / representation theory; `RepresentationTheoreticInvariant`, `KroneckerInvariant`, `PartitionObject` (synthesis §3.5).
**Attack.** Search for Littlewood-Richardson-style combinatorial rule. Stanley's Kronecker-rule programs. Avoid Mulmuley `PH1`-style framings as a primary route (falsified above); treat the NP-hardness as a structural constraint.
**Compute.** Sage / Symmetrica explicit computation. Mulmuley-Narayanan-Sohoni nonnegativity tests.
**Opens.** GCT positivity conjectures; lower-bound certifications. Note: with `PH1` falsified, any new positivity verifier must accept the NP-hardness baseline.
**Refs.** Mulmuley-Narayanan-Sohoni #P-hardness; Pak-Panova; Ikenmeyer-Mulmuley-Walter — Kronecker positivity NP-hard (falsifies Mulmuley `PH1`).

### 96. Stability of Kronecker coefficients
Sharp stability ranges (Murnaghan-style stabilization) and combinatorial interpretations beyond rectangular shapes.
**Class.** Asymptotic representation theory.
**Attack.** Refined Murnaghan stability theorems. Polynomiality conjectures for stretched Kronecker.
**Compute.** Sage symmetric-function computations. Empirical stability detection.
**Opens.** Asymptotic regime is GCT-relevant; large-shape lower bounds.
**Refs.** Briand-Orellana-Rosas; Vallejo Kronecker stabilization; Sam-Snowden FI-modules and stability.

### 97. Stretched Kronecker positivity
Whether stretched Kronecker coefficients are eventually quasi-polynomial with positivity properties matching Littlewood-Richardson.
**Class.** Combinatorics of representation theory.
**Attack.** Polytopal models for stretched coefficients. Connection to quantum integer programming.
**Compute.** Latte / Polymake Ehrhart-quasipolynomial computation. Sage symmetric functions.
**Opens.** GCT-style positivity arguments at scale; effective combinatorial interpretations.
**Refs.** Mulmuley-Narayanan-Sohoni quasi-polynomiality; Christandl-Doran-Walter stretched Kronecker.

### 98. Foulkes' conjecture
For a ≤ b, whether the plethysm s_a[s_b] − s_b[s_a] is Schur-positive.
**Class.** Plethysm / algebraic combinatorics.
**Attack.** Combinatorial models for plethysm coefficients. Representation-theoretic Schur-positive constructions.
**Compute.** Sage / Symmetrica plethysm computation. Verified for small cases (a,b small); symbolic exploration.
**Opens.** Direct GCT separation tool; resolves a 70-year-old positivity question.
**Refs.** Foulkes 1950 original; Cheung-Ikenmeyer-Mkrtchyan partial progress; Briand-Orellana-Rosas plethysm survey.

### 99. Saxl's conjecture
Whether the tensor square of the staircase character of S_n contains every irreducible representation as a constituent. **OPEN.** (Updated 2026-05-11 per Wave 1 anti-anchor verification — the prior 2026-05-10 edit claiming "SOLVED unconditionally by Sellke 2025/26" was itself a fabrication and has been reverted; Lee 2025 arXiv:2512.15035 was withdrawn within 3 days due to mathematical gaps.)
**Status.** *OPEN.* Lee's December 2025 preprint (arXiv:2512.15035, "Staircase Minimality and a Proof of Saxl's Conjecture") was withdrawn 2025-12-20 with the comment "This paper requires significant revision to address mathematical gaps identified by expert reviewers." Luo-Sellke 2017 proved only the *fourth-power* relaxation `(S_{ρ_n})^⊗4 ⊇ all irreps`; a 2022 follow-on (centre-mersenne) tightened to the *cube* `(S_{ρ_n})^⊗3 ⊇ all irreps` (see new entry SAXL_CUBE_ANCHOR in anti_anchors registry). The tensor square (Saxl proper) remains open. Mulmuley's `PH1` GCT-style route was independently falsified at the Kronecker-positivity layer by Ikenmeyer-Mulmuley-Walter (see entry 95).
**Class.** Symmetric-group representation theory; `RepresentationTheoreticInvariant` / `KroneckerInvariant` consumer (synthesis §3.5).
**Attack.** Murnaghan-Nakayama formula refinements; bounds on plethysm coefficients; semigroup-property arguments (Luo-Sellke style); modular reduction methods. Lee's withdrawn approach via "Staircase Minimality Theorem" + Bessenrodt-Bowman-Sutton lifting is suggestive but the gap is in the lifting step.
**Compute.** Sage character-table computations. Empirical verification of the cube relaxation at moderate n; tensor-square multiplicity sweeps to identify which irreps' multiplicities approach zero.
**Opens.** The full Saxl conjecture itself; quantitative multiplicity lower bounds; analogues for non-staircase self-conjugate partitions; whether the gap between cube and square is genuinely structural or amenable to existing methods.
**Refs.** Saxl original; Pak-Panova-Vallejo; Luo-Sellke 2017 *J. Algebraic Combin.* (fourth-power); 2022 cube tightening; Ikenmeyer Saxl progress; Lee 2025 (arXiv:2512.15035, **WITHDRAWN**) — do not cite as proof; Ikenmeyer-Mulmuley-Walter — Kronecker-positivity NP-hardness (falsifies the Mulmuley `PH1` route, see entry 95).

### 100. Invariant theory of tensor orbits
Equations, syzygies, and stabilizers of orbit closures for specific tensor formats — beyond basic GCT cases.
**Class.** Classical invariant theory.
**Attack.** Hilbert series via Molien-style formulas. Schur-Weyl decomposition for invariant rings.
**Compute.** Magma / Singular for invariant rings. Macaulay2 InvariantRing package.
**Opens.** Refined orbit-closure containment tests; concrete obstructions for GCT.
**Refs.** Derksen-Kemper *Computational Invariant Theory*; Bürgisser-Ikenmeyer-Wigderson invariant theory in algorithms.

## XIII. Cryptographic and Foundational Connections

### 101. MinRank / tensor isomorphism cryptographic foundations
Tight reductions among MinRank, tensor isomorphism, and lattice / code problems underpinning post-quantum NIST candidates.
**Class.** Post-quantum cryptography.
**Attack.** Average-case / worst-case reductions. Quantum algorithm analysis (BHT, Grover variants).
**Compute.** Specialized cryptanalysis tools (Magma, custom MinRank solvers). SAT/SMT-based key recovery experiments.
**Opens.** Sound security foundations for MEDS, ALTEQ, RAINBOW-derivative, GeMSS-style schemes.
**Refs.** Tang-Lai-Lim *MinRank-based cryptography*; Couvreur-Debris-Alazard-Tillich code-based cryptography; Beullens hardness analyses.

## XIV. Tensorial PDEs and Physical Tensors

### 102. Ricci flow singularity classification
Classify singularity formation in tensorial curvature evolution equations (Ricci flow, mean curvature flow).
**Class.** Geometric analysis / PDE.
**Attack.** Blow-up analysis; Perelman's ℒ-geodesics framework. Solitonic singularity models.
**Compute.** Adaptive mesh PDE solvers (deal.II, PETSc). Symbolic curvature computations (Cadabra, Mathematica).
**Opens.** Smooth Poincaré-conjecture-style classification programs; topology via flow.
**Refs.** Hamilton-Perelman Ricci-flow papers; Cao-Zhu survey; Bamler regularity theory of Ricci flow.

### 103. Einstein equation global regularity
Long-time behavior and singularity structure for solutions of Einstein vacuum equations.
**Class.** Mathematical relativity / hyperbolic PDE.
**Attack.** Christodoulou-Klainerman-style stability proofs. Cosmic censorship attacks; gauge choices and well-posedness.
**Compute.** Numerical relativity (Einstein Toolkit, GRChombo). Spectral methods for Einstein-system PDEs.
**Opens.** Cosmic censorship; gravitational-wave templates; ultimate fate of generic spacetimes.
**Refs.** Christodoulou-Klainerman *Global Nonlinear Stability of Minkowski Space*; Ringström *The Cauchy Problem in General Relativity*; Bieri-Zipser stability.

### 104. Tensorial turbulence closure
Mathematically principled closure models for higher-order turbulent stress tensors in compressible / multi-phase flows.
**Class.** Mathematical fluid dynamics.
**Attack.** Renormalization-group-style closures. Optimal tensor-low-rank reduction of moment hierarchies.
**Compute.** DNS (direct numerical simulation) for closure validation. ML-augmented closures (TensorFlow / PyTorch SGS models).
**Opens.** Tractable engineering CFD without ad hoc tuning; first-principles understanding of inertial-range tensor structure.
**Refs.** Pope *Turbulent Flows*; Speziale-Gatski tensor closures; Duraisamy-Iaccarino-Xiao ML closures.

## Cross-Cutting Themes and Reading Map

A compact map of how these problems interconnect — useful for substrate-style exploration and cross-domain falsification design:

**Spectrum-of-tensors core (1, 2, 7, 8, 16, 17).** Knowing all monotones in Strassen's asymptotic spectrum determines ω, which controls dozens of downstream problems. The asymptotic spectrum is the deepest unifying object.

**Rank-zoo overlap (13, 14, 15, 16, 19).** Multiple incompatible "structure detectors" — slice rank, partition rank, geometric rank, analytic rank, cactus rank — share polynomial-equivalences but no constant-factor unification. Each detects different invariants. This is the closest natural analogue to multi-channel falsification batteries.

**Identifiability triangle (40, 41, 42, 26, 33).** Identifiability of decompositions ↔ non-defectivity of secant varieties ↔ generic-rank theorems. Algebraic geometry, statistics, and applied tensor methods meet here.

**Random tensor stack (24, 25, 71, 72, 73, 74).** Concentration → operator-norm → tensor PCA → random tensor models. Universal random-matrix-style machinery may or may not survive the order-3 transition.

**GCT cluster (92–100).** Plethysm, Kronecker, Foulkes, Saxl, orbit closures — all the "information channels" through which any algebraic-geometry-based separation must pass.

**Quantum / TN cluster (75–85).** Area laws, contraction complexity, expressibility, holography, SLOCC. Tensor networks unify approximation theory and quantum information; foundational understanding lags behind practical use.

**Specific tensors as anchors (1, 3, 4, 5, 22, 86, 87, 88).** Concrete tensors (M⟨n⟩, T_{cw,q}, det_n, perm_n, DFT) anchor abstract questions to computable lower-bound certificates. Best targets for empirical / RL-driven attacks.

**Concept inventory (universal subroutines used across attacks).** Apolarity / inverse systems; flattening / Young flattenings; border-rank obstructions; symmetry reduction (representation theory); homotopy continuation; sum-of-squares and Lasserre hierarchies; Strassen's restriction preorder; moment maps and GIT; AMP / low-degree likelihood ratio; restricted-isometry / RIP; method of moments. Almost every attack vector in this document is a composition of these.

**Suggested entry tools per cluster.** Algebraic geometry: Macaulay2 + SchurRings + SecantVarieties. Numerical AG: Bertini, HomotopyContinuation.jl. Tensor decomposition (numerical): TensorLy, Tensor Toolbox. Tensor networks: ITensor, TenPy, TensorNetwork, cotengra, opt_einsum. Representation theory: GAP, Magma, LiE, Symmetrica, Sage. Random tensors / probability: NumPy / JAX with custom samplers. Cryptanalysis: Magma + custom solvers. SDP / SOS: Mosek, Yalmip, NCpol2sdpa, SumOfSquares.jl.

---

*Document scope note.* This is a working-reference dedup of the combined input lists; ~85 distinct problems. Items 102–104 are tensorial in the differential-geometric sense rather than the multilinear-algebra sense and sit somewhat outside the rest of the document's natural coherence — included for completeness because the input lists carried them. The core multilinear-algebra problems are 1–101.

---

## Aporia notes (2026-05-08)

**Why this is "near and dear" to Prometheus** (per James 2026-05-08):

1. **Tensors are the natural data structure for substrate growth.** Prometheus is going to grow horizontally and vertically rapidly; many of the frontier-problem landscapes our future tools will participate in use tensors extensively. Many of these landscapes are NP-hard in nature.
2. **NP-hardness is the looming complexity wall.** Many problems in this catalog (44, 49, 56, 57, 67, 84) are explicitly NP-hard in their decision form. Substrate work that develops attack vectors for NP-hard tensor problems is directly preparing Prometheus for the broader complexity terrain.
3. **The field is young.** Mathematicians have not had centuries to noodle over tensor problems the way they have for algebraic-equation problems. Tools are emerging rapidly. Prometheus has a chance to be in the field while it's still soft.
4. **Unique attack vectors.** The attack vectors here (slice rank / polynomial method, asymptotic spectrum, border apolarity, secant varieties, tensor-network contraction, GCT plethysm) don't reduce cleanly to the P01-P26 paradigms in `aporia/docs/attack_angle_taxonomy.md`. P27-P31 added there capture the most distinctive ones.

**Cross-references with existing database:**
- ω matrix multiplication exponent ↔ `aporia/docs/deep_research_batch10/report_176_matrix_multiplication_exponent.md`
- Tensor decomposition substrates ↔ `aporia/docs/deep_research_batch1/report_19_tensor_decomposition_substrates.md`
- Maximum tensor rank ↔ `aporia/docs/attack_angle_taxonomy.md`
- Connes embedding (problem 50 in James's prompt; relates to MIP*=RE in solved-problems-genealogy R4) ↔ multiple references
- Zauner / SIC-POVMs ↔ `aporia/docs/deep_research_batch4.md`
- Cap set (RESOLVED) ↔ partial coverage

**Substrate-mapping (Techne ticket T-2026-05-08-T038 will produce):**
- Which of the 104 problems are encodable in current substrate primitives (CoordinateChart, KillVector, ExclusionCertificate, OperatorOutputSequence)
- Which need new primitives (likely candidates: TensorNetwork primitive, AsymptoticSpectrum-monotone primitive, BorderApolarity-witness primitive, MomentPolytope primitive)
- Which connect to existing capability-gap tickets (e.g., 79 SLOCC entanglement classification connects to T-ST-fire1-002 homotopy class; 31 secant variety equations connects to T-ST-fire21-002 ArityGradedOperationFamily)

**Probe-shape design (Ergon ticket T-2026-05-08-E009 will produce):**
- For each problem with computational hooks, a Learner-Tester probe template
- Calibration targets for what counts as substrate-grade vs. textbook-trivial response on tensor problems
- v1.0 corpus seeds drawing from this catalog

— Aporia, 2026-05-08
