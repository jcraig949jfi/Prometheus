# Coordinate System Catalog
## Harmonia's periodic table of instruments
## Drafted: 2026-04-17 by Harmonia_M2_sessionA
## Joint commit with Harmonia_M2_sessionB

---

## Why this exists

Every scorer, index, feature extractor, battery test, and stratification we use
is a **coordinate system** — a way of projecting the landscape so some features
become visible and others disappear. Under the landscape-is-singular charter,
what matters is not "did it survive?" but "through which projections does it
resolve, and through which does it collapse?"

This catalog makes that question answerable. Every entry documents:
- **What it resolves:** features visible through this projection
- **What it collapses:** structure that becomes invariant (disappears) under this projection
- **Tautology profile:** what trivially-dependent quantities it smuggles in
- **Calibration anchors:** known-math features this projection detects correctly
- **Known failure modes:** specific pathologies observed in the wild
- **When to use / when NOT to use**

Projection IDs match the tensor manifest (`landscape_manifest.json`). Adding a
new coordinate system = adding an entry here AND a column in the tensor.

---

# Section 1 — Feature-Distribution Projections

These measure alignment between *distributions* of features across paired
objects. They are fast, general, and **collapse object identity** — survive
under label permutation, which is their fingerprint.

## P001 — CouplingScorer (cosine feature similarity)

**Code:** `harmonia/src/coupling.py:CouplingScorer`
**Type:** feature_distribution (normalized cosine of feature vectors across domain pairs)

**What it resolves:**
- Distributional alignment between paired feature vectors
- Magnitude co-variation if features are unnormalized
- Coarse similarity between two populations

**What it collapses:**
- Object-level identity (survives permutation of object labels — Pattern 2)
- Sparse/binary structure (cosine is dense)
- Categorical structure (Galois labels, aut groups, torsion types — use P010/P011/P022 instead)

**Tautology profile:**
- Sensitive to Megethos (P003): magnitude-sorted features give ρ≈1.0 trivially
- Requires prime decontamination (P052) before numerical coupling on scalar features
- Features normalized with z-score still leak magnitude if log-transformed

**Calibration anchors:**
- Detects modularity (EC↔MF) when shared feature sets exist
- Does NOT detect NF↔Artin Langlands coupling (killed F022 at z=0.0 under permutation null)

**Known failure modes:**
- Phoneme framework (F021): gave ρ=0.95+ across domains, killed by trivial 1D predictor
- NF backbone via feature-distribution (F022): z=0.0 under F1 permutation
- The canonical "cross-domain finding" false positive

**When to use:**
- Initial exploration of a new domain pair (set baseline before claiming anything)
- Calibration against known bridges
- Cheap first pass to rule out trivial couplings

**When NOT to use:**
- Claims about object-level cross-domain coupling (use P010 Galois-label or P011 Lhash)
- Any coupling where objects share a magnitude axis without decontamination
- Publication-grade findings without at least one permutation null

---

## P002 — DistributionalCoupling (M4/M2² kurtosis-sensitive)

**Code:** `harmonia/src/coupling.py:DistributionalCoupling`
**Type:** feature_distribution extended with kurtosis ratio

**What it resolves:**
- Tail structure mismatch (kurtosis signals non-Gaussian coupling)
- Distributions with same mean/variance but different shape

**What it collapses:**
- Same as P001 plus: loses fine-grained covariance structure

**Tautology profile:**
- Same Megethos susceptibility as P001
- High kurtosis readings on sorted log-normal pairs (Pattern 2 applies)

**Calibration anchors:** (inherits from P001)

**Known failure modes:**
- Phoneme framework used this scorer; same kill chain as P001

**When to use:**
- When you suspect tail-driven coupling (fat tails in one domain)
- As a check on P001 when cosine gives suspicious results

**When NOT to use:**
- Same as P001

---

## P034 — AlignmentCoupling (rank-based extremity coupling)

**Code:** `harmonia/src/coupling.py:AlignmentCoupling` (class body lines 182–298)
**Type:** feature_distribution (rank-based; Megethos-robust by construction)

**What it resolves:**
- **Coupling visible only through rank structure** — where each object sits in its feature distribution (quantile rank ∈ [0, 1]), not its raw magnitude. Objects with identical ranks across two domains have identical coupling weight, regardless of their absolute feature values.
- **Extremity co-variation.** For each feature column per domain, the scorer weights by `(q − 0.5).abs()` — distance from median. Objects that are extreme in one domain are scored higher when paired with objects that are extreme in another. Mid-population pairings contribute near-zero, by design.
- **Sign-preserving alignment.** A secondary term uses `(q − 0.5).sign()` times an interaction-matrix-weighted dot-product with the partner domain's sign vector. This rewards "both high" or "both low" configurations and penalizes "one high, one low". Weight on this term is 0.3 in `score_batch` (line 292) — small relative to the extremity term.
- **Learning-time interaction structure.** At init (lines 219–257), per-domain-pair, it samples 5000 random pairings, computes the extremity cross-correlation matrix (d_i × d_j), estimates the null by shuffling the partner domain 5 times, and keeps only feature-pair interactions that are **> 2σ above the shuffled null**. The interaction matrix is the scorer's learned memory; it resolves which feature columns co-vary under any real pairing vs. which are noise.

**What it collapses:**
- **Magnitude-scale structure.** Quantile rank erases absolute feature magnitudes entirely. Two objects with feature vectors (1, 2, 3) and (100, 200, 300) have identical rank signatures if they occupy the same percentile slots. This is Megethos-robust **by construction**, not by discipline — the scorer cannot be contaminated by P003 the way P001 and P002 can.
- **Sparse/binary feature structure.** Features with mostly-identical values (e.g. binary flags, sparse indicators) produce degenerate rankings where ties dominate, collapsing extremity differences. Use categorical projections (P010/P011/P012) instead.
- **Low-count populations** where rank quantiles are coarse. Below ~1000 objects, the rank granularity is too coarse for stable extremity measurement.

**Tautology profile:**
- **Not independent of P001/P002.** The underlying claim is still "these projections share a feature correspondence" — just measured through ranks instead of raw cosine. Using both P001 and P034 on the same hypothesis double-counts the distributional alignment signal. Pattern 1 (Distribution/Identity Trap) applies: if P001 gives ρ=0.9 and P034 gives a high score, check whether both are driven by the same formula-level overlap before celebrating.
- **Learning-time null ≠ inference-time null.** The built-in 2σ filter on the interaction matrix is a **learning discipline** — it rejects interaction cells that are noise given the observed pairings. It is NOT a post-hoc permutation null on the final score. To probe whether a batch-level coupling survives permutation, use P040 externally. Conflating the two is a protocol error.
- **Quantile-rank × degree-of-freedom coupling.** For tables where most objects have identical feature values (e.g. `rank` on ec_curvedata — 80% rank 0 or 1), the quantile map is nearly step-function. The rank-based transformation preserves less information than the raw numeric one. Check distribution shape before adopting P034 over P001.
- **Extreme-tail over-weighting in small samples.** `(q − 0.5).abs()` weights tails quadratically in a sense; with n < 1000 the top and bottom quantiles are dominated by 2-3 outlier objects, and their interactions drive the score disproportionately. Apply P043 bootstrap to confirm stability.

**Calibration anchors:**
- **Known rank-structure invariances.** Where rank signature across projections is a real invariance — e.g. F010 NF backbone's "small-disc NFs pair with low-conductor Artin reps" — P034 should resolve the signal. Untested on F010 as of this entry; candidate follow-up.
- **Modularity (F001) via P034 is weak.** Modularity is about L-function identity, not rank co-variation on arithmetic invariants. P034 has no principled reason to detect modularity; expect it to give no signal on pure EC↔MF modularity probes. If it does, either Pattern 5 applies (known invariance re-projected) or there is a leak.
- **Against P001 on the phoneme corpus (F021).** Phoneme framework gave ρ=0.95+ under P001 and was killed by P040. P034 on the same corpus should ALSO give a high score (ranks are aligned in the same trivial way the raw cosine is) — the 2σ learning-filter would not help here because the 5-shuffle null is too weak. This is the expected failure mode; confirms P034 is not a magic Megethos escape.

**Known failure modes:**
- **High-Megethos data gives decent-looking scores in noisy ways.** Rank normalization kills magnitude scale, but rank order can still track magnitude within a stratum. If two projections have strongly-correlated magnitudes, their rank signatures are also correlated — P034 sees this as "aligned extremity" and fires. Pre-decontaminate with P052 where applicable.
- **The interaction-matrix is a memory.** AlignmentCoupling learns from the sample it sees at init. If you change the population (e.g. add new objects, change filters) without re-initializing, the interaction matrix is stale. Pattern 19 (Stale/Irreproducible) at scorer-state level.
- **Sigmoid normalization compresses the tail.** Final score is `sigmoid(total_score * 5)` (line 297). This compresses high-magnitude couplings toward 1.0 and mid-range toward 0.5. Two distinct "very strong" couplings are indistinguishable in output; use the pre-sigmoid `total_score` if relative ranking matters.
- **5-shuffle null at init is noisy.** The 2σ filter estimates null mean/std from only 5 permutations (line 245). This is a permissive filter — the effective rejection rate is ~5% under pure noise. Treat the learned interactions as coarse, not definitive.

**When to use:**
- **Coupling-across-projection probes where Megethos has been a chronic confound** and P052 decontamination is infeasible (categorical or non-numeric features). P034 gives a rank-based floor that P001 doesn't.
- **Extremity-driven phenomena.** When the hypothesis is literally "extremes align" (e.g. high-Sha curves paired with low-regulator curves), P034's extremity weighting is the right shape.
- **As a corroborating scorer alongside P001.** If P001 shows a signal, P034 showing the same signal at rank level is weak corroboration (Pattern 3 Weak Signal Walk invariance evidence). If P001 shows a signal but P034 doesn't, the coupling is magnitude-mediated and likely Megethos-contaminated — Pattern 3 kill axis.
- **Exploratory first-pass on new projection pairs** where rank-order is known but absolute scaling is arbitrary (mixed-unit datasets).

**When NOT to use:**
- **Categorical/object-level coupling claims.** Use P010/P011/P012. Quantile rank is defined only for continuous features.
- **Small-n populations (n < 1000).** Rank granularity is too coarse; bootstrap (P043) dominates the signal.
- **Publication-grade findings without post-hoc P040 permutation null.** The built-in 2σ learning-time filter is not a substitute for inference-time null.
- **In place of P001 when you want raw cosine similarity.** P034 and P001 measure different things; P034 is not a cleaner version of P001 — it is a distinct projection with a different invariance surface.

**Relationship to other projections:**
- **P001 CouplingScorer — parent class.** P034 inherits `__init__`'s feature-normalization machinery but overrides scoring entirely. Running both jointly and comparing is diagnostic: agreement = robust distributional signal; P001-only = magnitude-mediated (Megethos-suspicious); P034-only = pure rank extremity (may indicate sparse/binary features in the data).
- **P002 DistributionalCoupling — sibling.** P002 adds kurtosis ratio on top of cosine; P034 replaces cosine entirely with rank. Different axes on what "distributional" means.
- **P040 F1 permutation null — orthogonal/complementary.** P040 tests the inference-time coupling under label shuffle; P034's internal 2σ filter tests the learning-time interaction matrix under shuffle. They answer different questions and do not substitute for one another.
- **P052 Prime decontamination — can precede.** If the projections have prime-factorization-mediated coupling, decontaminate first; otherwise P034 will inherit the contamination (Pattern 1 at rank level).

---

# Section 2 — Magnitude Axes (Confounds)

## P003 — Megethos (log|magnitude| axis)

**Code:** Not a single scorer — this is the PC of log-magnitude features
(log disc, log conductor, log level, log |discriminant|)

**Type:** magnitude_axis (confound, not signal)

**What it resolves:**
- Nothing useful. This is an anti-projection.

**What it collapses:**
- Everything — structure buried under magnitude variation

**Tautology profile:**
- The canonical tautology: sorted log-normals give cosine ρ=1.0
- Responsible for 97% of "cross-domain" findings in the pre-charter era (F020 kill)

**Calibration anchors:**
- None. This is a coordinate system we explicitly **remove**.

**Known failure modes:**
- The entire phoneme framework
- Several R1-R5 genocide survivors in the old frame
- Any numerical feature coupling that wasn't magnitude-normalized

**When to use:**
- Diagnostic: project features onto this axis to see how much of their variance is magnitude
- If >90% of variance is Megethos, the features need decontamination (P052) or replacement

**When NOT to use:**
- Never as a signal projection.

---

# Section 3 — Categorical Object-Level Projections

These use **object-level categorical identity** (Galois labels, Lhash, specific
group labels) as the coupling axis. They **survive permutation nulls** — because
shuffling labels destroys the identity that carries the coupling. This is what
distinguishes them from feature-distribution projections.

## P010 — Galois-label object-keyed scorer

**Code:** `cartography/shared/scripts/nf_backbone_object_keyed.py`
**Type:** categorical_object_level

**What it resolves:**
- Langlands-style coupling between number-theoretic domains (NF, Artin, MF)
- Object-level correspondence mediated by Galois group label
- Any coupling where shared Galois label predicts a joint property

**What it collapses:**
- Pure distributional alignment without categorical link
- Coupling that doesn't factor through Galois structure

**Tautology profile:**
- Not tautological per se, but: Galois label is often implicit in LMFDB's labeling scheme
- If two objects sharing a Galois label also share a conductor (because LMFDB indexes that way),
  the coupling may leak conductor-mediation (P020 required as control)

**Calibration anchors:**
- F010 NF backbone: rescued at ρ=0.40, z=3.64 after same data gave z=0.0 under P001
- F001 modularity (EC↔MF via shared a_p coefficients at 100%)

**Known failure modes:**
- None observed in the wild yet. Protocol: always follow up with conductor conditioning (P020).

**When to use:**
- Any coupling claim in number-theoretic domains (NF, Artin, MF, EC)
- When P001 kills a signal at z=0 — try P010 before filing as KILLED
- Cross-domain tests where both sides have canonical Galois structure

**When NOT to use:**
- Geometric / topological domains without canonical Galois assignment
- Knots, polytopes, graphs — no natural Galois projection

---

## P011 — Lhash exact match (isospectral grouping)

**Code:** LMFDB column `lfunc_lfunctions."Lhash"`, index `idx_lfunc_lhash` (built 2026-04-17)
**Type:** categorical_object_level

**What it resolves:**
- EC ↔ MF modularity pairs (same L-function zeros → same Lhash)
- Kac "drum pairs": objects sharing Lhash but differing in algebraic invariants

**What it collapses:**
- Fine spectral differences (Lhash is a hash of early zeros, discards detail)
- Any structure beyond the first few zeros

**Tautology profile:**
- Not tautological — it's a pure identity match
- False negatives possible if the hash truncates too aggressively

**Calibration anchors:**
- Should detect all known modular elliptic curves (each EC L-function has a matching MF L-function with same Lhash)
- Koios running cross-family Lhash join (Artin↔MF) as of session end

**Known failure modes:**
- Used too coarse: collisions within same isogeny class aren't "drum pairs"
- Must post-filter by requiring distinct algebraic invariants (cm, rank, torsion, class_size)

**When to use:**
- Finding isospectral-but-not-isomorphic object pairs across families
- Verifying modularity predictions
- Any question about "what do the zeros miss?"

**When NOT to use:**
- Questions about specific zero values (Lhash is lossy by design)
- Small-conductor high-degree L-functions (Lhash may collide trivially)

---

## P012 — trace_hash (Hecke eigenvalue hash)

**Code:** LMFDB column `lfunc_lfunctions.trace_hash`
**Type:** categorical_object_level (stricter than Lhash)

**What it resolves:**
- Exact Hecke eigenvalue sequences
- Finer object identity than Lhash

**What it collapses:**
- Any approximation — trace_hash wants exact values

**Tautology profile:**
- Direct hash of computed Hecke eigenvalues. If the computation is wrong, the hash is wrong.

**Calibration anchors:**
- Same as P011 but stricter

**When to use:**
- When Lhash gives too many false matches
- Publication-grade identity claims

**When NOT to use:**
- Approximate matches (degraded L-function data)

---

# Section 4 — Stratifications

These split the dataset by a categorical/ordinal axis before applying another
projection. Critical for revealing features hidden in pooled analysis.

## P020 — Conductor conditioning

**Code:** Standard: `WHERE conductor BETWEEN lo AND hi` in queries
**Type:** stratification (scale axis)

**What it resolves:**
- Any feature that varies with conductor
- Separates finite-N effects from structural ones

**What it collapses:**
- Conductor-mediated couplings (they disappear within bins)

**Tautology profile:**
- Conductor confounds virtually all EC analysis. Almost every signal in pooled data is partly conductor-driven.

**Calibration anchors:**
- F023 spectral tail: pooled showed ARI=0.55; within-bin conditional analysis killed it (all 4 bins p>0.05)

**Known failure modes:**
- Over-stratification: bins too narrow → not enough objects per bin
- Under-stratification: bins too wide → conductor variation survives

**When to use:**
- ALWAYS as a control on EC / L-function couplings
- Before claiming any structural signal

**When NOT to use:**
- Rarely. Conductor conditioning should be default discipline.

---

## P021 — Bad-prime count stratification

**Code:** `WHERE num_bad_primes = k` splits
**Type:** stratification (arithmetic axis)

**What it resolves:**
- Features that scale with bad-prime cardinality
- Separating additive vs multiplicative reduction effects

**What it collapses:**
- Coupling that averages over bad-prime types

**Tautology profile:**
- Bad-prime count correlates weakly with conductor — may need joint P020+P021

**Calibration anchors:**
- F015 abc/Szpiro rescue (Ergon, 2026-04-16): monotone decrease of Szpiro ratio survives at fixed num_bad_primes; Ergon's axis

**Known failure modes:**
- None observed. Underused projection in practice.

**When to use:**
- Any abc / Szpiro / discriminant-based claim
- Signals that seemed to die in pooled analysis — try this stratification

**When NOT to use:**
- Domains without a natural "bad prime" structure (topology, QM9 chemistry)

---

## P022 — aut_grp stratification (genus-2)

**Code:** `WHERE aut_grp_id = g` splits on g2c_curves
**Type:** stratification (geometric/symmetry axis)

**What it resolves:**
- Features carried by automorphism symmetry class of the Jacobian
- Geometric signals that are invisible pooled

**What it collapses:**
- Signals averaged over aut group types

**Tautology profile:**
- aut_grp correlates with discriminant class and possibly with rank — joint stratification may be needed

**Calibration anchors:**
- F012 (H85) Möbius bias: |z|=6.15 pooled by aut_grp. The canonical use case.

**Known failure modes:**
- Small-n strata give unstable z-scores (must require n≥100 per group)

**When to use:**
- Any signal in g2c data
- Whenever a geometric symmetry label exists as a coordinate

**When NOT to use:**
- Without checking n per stratum first

---

## P023 — Rank stratification

**Code:** `WHERE rank = r` splits
**Type:** stratification (algebraic axis)

**What it resolves:**
- Features that vary with Mordell-Weil rank
- Rank-dependent zero structure (F013)

**What it collapses:**
- Rank-invariant features

**Tautology profile:**
- rank = analytic_rank for rank 0-1 by BSD proof; for rank ≥ 2, this is a circularity trap (Mnemosyne's catch)

**Calibration anchors:**
- F003 BSD parity: perfect across 2.48M rows (calibration, not finding)
- F013 spacing rigidity vs rank: slope=-0.0019 with R²=0.399

**Known failure modes:**
- Rank ≥ 4: severe data gap (F030, F033 — only 1 of 2,105 rank-4+ curves has lfunc data)
- Claims at rank ≥ 2 that use Sha are circular (Mnemosyne's BSD v1 kill)

**When to use:**
- Any BSD-adjacent analysis
- Zero-spacing or regulator claims

**When NOT to use:**
- High-rank extrapolation without checking coverage (Pattern 9)

---

## P024 — Torsion stratification

**Code:** `WHERE torsion = T` splits
**Type:** stratification (finite-group axis)

**What it resolves:**
- Torsion-dependent features (which is rare under Mazur's theorem)

**What it collapses:**
- Almost everything beyond Mazur's classification

**Calibration anchors:**
- F002 Mazur torsion: 3.8M curves, torsion ∈ {1,2,3,...,10,12, Z/2×Z/2, Z/2×Z/4, Z/2×Z/6, Z/2×Z/8}

**Known failure modes:**
- H38: torsion does NOT predict z1 (ρ=0.086, p=0.87, killed)
- Torsion is a weak stratification axis for zero-structure

**When to use:**
- Torsion-specific claims
- As a cross-check on rank stratification

**When NOT to use:**
- Expecting torsion to resolve zero structure (it doesn't)

---

## P025 — CM vs non-CM

**Code:** `WHERE cm != 0` vs `WHERE cm = 0`
**Type:** stratification (binary algebraic axis)

**What it resolves:**
- Complex-multiplication-specific features
- Family-level Sato-Tate type differences

**What it collapses:**
- Any feature that doesn't distinguish CM from generic

**Calibration anchors:**
- CM curves satisfy modularity with different analytic behavior (known)
- Root number forced to +1 for CM with specific conditions (F031 contamination caught this in zeros_vector pos 21)

**Known failure modes:**
- Tested 2026-04-16: zero spacings CM vs non-CM indistinguishable (KS p=0.38). Clean null.

**When to use:**
- Sato-Tate analysis
- Family-level symmetry-type claims

**When NOT to use:**
- Expecting CM/non-CM to resolve generic spectral features

---

## P026 — Semistable vs additive reduction

**Code:** `WHERE semistable = t` vs `WHERE semistable != t`
**Type:** stratification (reduction type axis)

**What it resolves:**
- Additive-reduction-specific features
- Multiplicative vs additive contrasts

**What it collapses:**
- Reduction-type-invariant features

**Calibration anchors:** (uncertain)

**Known failure modes:**
- H10 tested: ADE split (A_n multiplicative, D_n/E_n additive) does NOT explain GUE deficit (|Δvar|=0.006, killed)
- Pattern 13: this is one of the two axes that killed F011 cleanly — a cumulative negative finding along family axes

**When to use:**
- Reduction-type-specific claims

**When NOT to use:**
- Expecting it to resolve finite-N spectral features

---

## P027 — ADE type stratification (proxy via Galois label)

**Code:** Heuristic: small Galois labels (1T1, 2T1, 3T1, etc.) as proxy for ADE
**Type:** stratification (Dynkin classification axis)

**What it resolves:**
- ADE-classified-group-specific features (in theory)

**What it collapses:**
- Real ADE classification if heuristic proxy is wrong

**Tautology profile:**
- The small-Galois-label heuristic biases toward simpler groups. May not correlate with actual ADE type.

**Calibration anchors:** None clean.

**Known failure modes:**
- H11 tested: ADE gatekeeping claim gave Cohen's d=4.96 in WRONG direction (ADE groups have higher disc/factorial(deg), not lower).
  Either the hypothesis was wrong OR the heuristic proxy is.

**When to use:**
- Exploratory only, with explicit acknowledgment that proxy may not match intent

**When NOT to use:**
- Publication-grade ADE claims (compute actual Dynkin type from Lie algebra structure)

---

## P028 — Katz-Sarnak family symmetry type

**Code:** Derivable from family definition; not a single function. For a given L-function family, classify each L-function into one of {U, Sp, SO_even, SO_odd}. In LMFDB, partly carried by `st_group` and partly by family metadata; for EC the SO_even/SO_odd split follows root-number / rank-parity, for quadratic twists the family is Sp by construction.
**Type:** stratification (symmetry-type axis, from random-matrix universality for low-lying zeros)

**What it resolves:**
- **Low-lying zero statistics** (first few zeros above the central point). Each symmetry type has a distinct one-level density function — sin²(πt)/(πt)² for U, different Bessel-function combinations for Sp / SO_even / SO_odd. Pooled GUE cannot see these differences because GUE is the bulk asymptotic; Katz-Sarnak is the finite-family near-center regime.
- **Parity-driven features.** SO_odd families have a *forced* central zero (the functional-equation sign requires it); SO_even does not. Any feature depending on "is there a zero at s=1/2?" splits cleanly here.
- **Family-level discrimination.** Dirichlet L-functions (U), quadratic L-functions (Sp), and elliptic-curve L-functions (SO split by rank parity) sit at distinct symmetry-type points in the Katz-Sarnak classification.
- **GUE deviations at finite conductor.** F011's 14% first-gap deficit is a low-lying zero question — exactly the regime where Katz-Sarnak predicts family-specific deviations from universal GUE.

**What it collapses:**
- **Bulk spectral statistics.** For high zeros, every symmetry type converges back to universal GUE. Above a conductor-dependent unfolding scale, Katz-Sarnak distinctions wash out. Do not use this stratification for pair-correlation or moment analysis of bulk zeros.
- **Within-type distinctions.** Two SO_even families look identical to first order. Second-order corrections (via Conrey-Farmer-Mezzadri-Snaith moment conjectures) can distinguish them, but the projection itself does not.
- **Structure orthogonal to symmetry type.** Conductor effects, bad-prime effects, non-parity-driven rank effects still need independent axes.

**Tautology profile:**
- **Rank parity × symmetry type for EC.** For elliptic-curve L-functions, SO_even ↔ rank even, SO_odd ↔ rank odd (by root-number/BSD parity). So Katz-Sarnak stratification of EC is not independent of P023 rank stratification modulo 2. Joint claims via P028 × P023 must demonstrate residual signal after parity control.
- **Family definition × symmetry type.** Quadratic L-functions are Sp by construction; Dirichlet complex-character L-functions are U by construction. Stratifying across these families is identical to stratifying by family. Only meaningful within a single family containing multiple symmetry types (e.g., EC has both SO_even and SO_odd).
- **Functional-equation sign aliasing.** For EC, the Atkin-Lehner sign determines SO_even vs SO_odd. Verify P028 is not a rename of an already-catalogued sign projection.

**Calibration anchors:**
- **Function-field Katz-Sarnak theorem.** For L-functions over F_q(T), symmetry type is *provable* via algebro-geometric monodromy. That is the ground truth the number-field case is modelled on. If P028 misclassifies a function-field family, the instrument is broken.
- **Rubinstein–Sarnak mock-Gaussian** lowest-zero distribution results for EC families match Katz-Sarnak predictions at current LMFDB conductor ranges.
- **Modularity cross-projection.** Weight-2 MF L-function symmetry type must match corresponding EC symmetry type under modularity — an identity calibration every P028 implementation must satisfy.

**Known failure modes:**
- **Small-n strata.** SO_odd counts at narrow conductor windows can drop below 100, especially in quadratic-twist families. Require n_per_type ≥ 100 before reporting per-type z-scores.
- **Symmetry-type misclassification for imprimitive L-functions.** Use primitive forms only; decomposable L-functions inherit ambiguous symmetry.
- **Bulk-regime misuse.** Applying Katz-Sarnak predictions to zero index ~1000 rather than ~3 produces spurious deviations — GUE has already reasserted itself at that height.
- **Double-counting with P051 unfolding.** N(T) unfolding rescales zero heights; Katz-Sarnak one-level density is already in the unfolded regime by definition. Do not unfold a second time.

**When to use:**
- **F011 GUE first-gap deficit.** Textbook application — low-lying zero question across a family containing multiple symmetry types. Pattern 13 context: H08 Faltings and H10 ADE died as mechanism hypotheses, both family-level. P028 is *also* family-level BUT encodes low-lying-zero prediction directly rather than a general object property. Worth one more family-axis shot before full pivot to preprocessing (P051) + finite-N (H09).
- **Cross-family modularity calibration.** Verify EC and matched MF families classify identically post-modularity.
- **Any first-zero statistics question** (not bulk).
- **Parity-sensitive analyses** where separating "central zero present?" from "spacing of zeros above it" matters.

**When NOT to use:**
- **Bulk zero statistics** — use P051 N(T) unfolding + GUE directly.
- **Within-U or within-Sp publication-grade claims** without second-order moment analysis — first-order Katz-Sarnak will not distinguish two U families.
- **After P051 unfolding** — already in the unfolded regime; do not apply both as independent preprocessing.
- **When the primary variation tested is EC rank-parity** — nearly identical to P028 in that case, so you are just re-running P023 with a rename.

**Pattern 13 note:** If P028 *also* kills the F011 mechanism (symmetry-type stratification does not explain the 14% first-gap deficit), that is the *third* family-level axis to die cleanly. Under Pattern 13, three family-axis kills = the feature is definitively not on the family axis; redirect remaining effort entirely into preprocessing (P051) + finite-N (H09) + sample-frame discipline. P028's expected contribution is therefore either (a) rescues F011 (high-value), or (b) kills the family-axis hypothesis conclusively (also high-value — ends a search direction).

---

## P029 — MF weight stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task catalog_mf_weight)
**Code:** `WHERE weight = k` on `lmfdb.mf_newforms` (index: `idx_mf_weight_level` on `(weight::int, level::int)`)
**Type:** stratification (modular-form weight axis)

**What it resolves:**
- Modularity correspondence at **weight 2**: weight-2 rational newforms (`weight='2' AND dim='1'`) are in 1–1 bijection with isogeny classes of elliptic curves over Q. This is the calibration anchor F001.
- Deligne-Serre correspondence at **weight 1**: weight-1 newforms ↔ odd 2-dimensional Artin reps. Different structural regime from weight ≥ 2 and the only clean MF↔Artin stratum.
- L-function functional-equation differences: analytic conductor scales as `N·k²/(4π²)` at leading order, so weight changes the effective spectral scale.
- Character-parity alignments: weight parity must match character parity for non-trivial forms.

**What it collapses:**
- EC↔MF coupling pooled across weights (modularity is weight-2-only; non-weight-2 entries dilute the signal).
- Sato-Tate / Galois-side comparisons where Satake parameters are weight-dependent.
- Family-type symmetry (Katz-Sarnak) pooled across weights within a level.

**Tautology profile:**
- Weight co-varies with analytic conductor through `N·k²` — treating P029 as independent of P020 can reintroduce conductor mediation. Use joint P020 × P029 when claiming weight-specific structural effect.
- `mf_newforms` skews heavily toward weight 2 (~91% of 1.14M rows). Unstratified "MF-wide" claims almost always reduce to weight-2 claims (Pattern 4 variant).
- weight=2 AND dim=1 is the slice used by `harmonia/scripts/st_weighted_compression.py`; treating Sato-Tate results on that slice as "MF-universal" is a tautology-by-sampling-frame.

**Calibration anchors:**
- F001 modularity — **weight-2-only anchor**. Without P029 stratification, "100% a_p agreement" is ill-defined.
- Deligne-Serre (weight 1 ↔ Artin 2-dim odd) — candidate calibration anchor; 19,306 weight-1 newforms ready for comparison against Artin side. Unclaimed F-slot.

**Known failure modes:**
- Pooled Lhash (P011) matching across weights gives false "modularity-adjacent" hits.
- High-weight strata underpopulated: 249 distinct weights, 35 with n≥100, only 14 with n≥1000.
- `dim` column further splits — weight-2 dim=1 ≈ 620K, weight-2 dim>1 ≈ 418K. Several scripts silently restrict to dim=1.

**Stratum-count summary (LMFDB live, 2026-04-17):**
- weight 1: 19,306 (Deligne-Serre regime)
- weight 2: 1,038,068 (modularity regime; dominates)
- weight 3: 12,713
- weight 4: 28,466
- weight 5: 4,053
- weight 6: 10,789
- ...
- 14 weights with n≥1000; 35 with n≥100; 249 distinct total.

**Discipline for small-n strata:**
- Require n≥1000 per stratum for permutation-null z-scores to be stable.
- For n ∈ [100, 1000), report n alongside z and cap claim at "suggestive, coverage-limited."
- For n<100, don't stratify at that granularity — merge with nearest populated weight or abandon the bin.

**When to use:**
- Any EC↔MF test (must stratify to weight=2, always).
- MF↔Artin tests involving odd 2-dim Galois reps (weight 1 specifically).
- Sato-Tate / a_p statistics that pool across weights — pre-split or report as pooled-baseline-only.
- Zero-density / RMT analysis on `mf_newforms` L-functions.

**When NOT to use:**
- Counting-level statistics where weight is irrelevant.
- Exploratory first pass where the question is "does ANY MF signal exist" — pool first, stratify after signal.

**Related projections:**
- **P020 conductor conditioning** — joint P020 × P029 required for weight-specific claims.
- **P011 Lhash** — modularity matching valid within weight=2 only; cross-weight Lhash matches are drum-pair candidates, not modularity failures.
- **(pending) P030 level stratification** — co-varies with weight through analytic conductor; likely needs joint P029×P030 projection.

**Follow-ups this entry uncovered:**
1. Section 9 MF stratification entries (weight / level / character parity) co-vary through analytic conductor — candidate joint projection `P029 × P030 × P031` rather than three independent slots.
2. Deligne-Serre as candidate calibration anchor — give it an F-slot for a second surveyor's pin at weight=1.
3. Pattern 4 canonical example: 91% weight-2 skew in mf_newforms is a textbook sampling-frame trap.

---

## P030 — MF level stratification

**Drafted by:** Harmonia_M2_sessionC, 2026-04-17 (task catalog_mf_level)
**Code:** `WHERE level = N` on `lmfdb.mf_newforms` (1,141,510 rows; level range 1..999,983)
**Type:** stratification (arithmetic axis, orthogonal to P029 weight)

**What it resolves:**
- Level-dependent modular-form features (Fourier coefficients a_n sharing factors with N)
- Atkin-Lehner eigenvalue structure (AL involutions act at fixed level)
- Fricke involution and Hecke eigenvalue interactions that factor through N
- Oldform/newform decomposition at fixed level

**What it collapses:**
- Level-invariant features (weight-only, character-only, Galois-rep-only)
- Analyses aggregating across X_0(N) of differing genus
- The `weight` coordinate (P029) — independent axis, joint required for full resolution

**Tautology profile:**
- **CRITICAL:** For EC↔MF modularity pairs in weight 2, `mf_newforms.level ≡ ec_curvedata.conductor` by the modularity theorem. Any cross-side coupling between level and conductor collapses to IDENTITY under this projection. Treat as calibration anchor (F001), not finding. Add `(level, conductor)` to the Section-8 tautology-pair table.
- `level_radical`, `level_is_squarefree`, `level_is_prime*` etc. are deterministic functions of level — redundant if used together.
- Level correlates with `Nk2 = level · weight²` (analytic conductor driver). Joint analytic-conductor-driven studies require partial-control argument or P052 decontamination.

**Calibration anchors:**
- F001 modularity: `mf_newforms.level` matches `ec_curvedata.conductor` on matched weight-2 newforms. The identity that makes the tautology profile load-bearing.
- Ramanujan-Petersson bound |a_p| ≤ 2√p for p ∤ level — uniform at every level, violations = data-quality signal not level effect.
- Dimension formulas `dim S_k(Γ_0(N))` known exactly; strata at N=1, prime, square can be cross-checked against classical formulas.

**Known failure modes:**
- Tautological EC↔MF coupling collapse (see above).
- Small-level singularities: levels 1, 2, 3 have genus-0 modular curves; variance measurements over all levels without exclusion yield misleading per-stratum stats. Recommend `level ≥ 11` or explicit exclusion.
- Top-heavy distribution: levels concentrated at small-to-moderate values. Without MIN_STRATUM_N ≥ 100 filter, triggers Pattern 4 sampling-frame trap.

**When to use:**
- Isolating Atkin-Lehner / Fricke signals at fixed N
- Testing whether MF↔X coupling is level-mediated (within-level ρ vs pooled ρ)
- Joint stratification with P029 (weight) for dimension-formula sanity
- Before claiming a novel MF feature — check whether the signal is explained by level

**When NOT to use:**
- Comparing MF.level against EC conductor on matched pairs (tautological, F001)
- Without controlling Nk2 on analytic-conductor-driven effects
- Small-level tails (level ≤ 10) without manual sanity checks

**Related projections:**
- **P029 MF weight:** orthogonal axis; joint (P029, P030) is the natural MF coordinate pair.
- **P020 conductor conditioning:** becomes redundant for EC↔MF weight-2 matched pairs (level≡conductor). Use one or the other.
- **P052 prime decontamination:** recommended pairing for numeric features with prime structure.
- **Pattern 13:** P030 is a conductor-family axis; if F011 doesn't resolve here, Pattern 13 redirects away from all such axes.

**Follow-ups this entry motivates:**
1. `wsw_F001_via_P030` — confirm modularity calibration at per-level.
2. `catalog_nk2_joint` — document `Nk2 = level × weight²` as its own derived coordinate.
3. `catalog_level_radical` — separate entry for the squarefree-kernel projection.

---

## P031 — Frobenius-Schur Indicator stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task catalog_artin_indicator)
**Code:** `WHERE "Indicator" = v` on `lmfdb.artin_reps` (indexed via `idx_artin_dim_conductor`; Indicator itself is unindexed — add `idx_artin_indicator` if this becomes a hot path)
**Type:** stratification (symmetry / self-duality axis, classical representation theory)

**What it resolves:**
- **Self-duality and symmetry type of a complex irreducible representation.** For an irreducible character χ of a finite group, the Frobenius-Schur indicator ν(χ) ∈ {-1, 0, +1} classifies:
  - `+1` — χ is the complexification of a real (orthogonal) representation — fixes a symmetric bilinear form.
  - `-1` — χ is quaternionic (symplectic) — fixes an alternating bilinear form.
  - ` 0` — χ is not self-conjugate (complex type in the reality sense).
- **Expected L-function symmetry type** for the Artin L-function attached to the rep. The Katz-Sarnak symmetry type (`P028`) follows directly from ν via:
  - `ν = +1` with `Is_Even = True`  → `SO_even` family.
  - `ν = +1` with `Is_Even = False` → `SO_odd`  family.
  - `ν = -1`                        → `Sp`        family.
  - `ν = 0`                         → `U`         family.
  This is the arithmetic companion of `P028`'s random-matrix classification.
- **Whether the rep descends to a real form**, which matters for base-change arguments and for selecting out the self-dual subfamily in cross-specimen analyses.

**What it collapses:**
- **Within-indicator distinctions.** Two `ν = +1` reps of different dimensions, different Galois groups, different conductors all map to the same stratum. Use `P031` as a coarse symmetry filter; stratify further by dimension or Galois label when needed.
- **Representation content beyond symmetry.** The full character values are lost; only the self-duality class survives.
- **The `Is_Even = False` ⇒ `ν ≠ -1` forbidden cell** makes joint `P031 × Is_Even` non-orthogonal (see tautology profile below).

**Tautology profile:**
- **`P031` ↔ `Is_Even` (partial tautology, asymmetric).** Empirical from `artin_reps` (798,140 rows, 2026-04-17):
  - `Is_Even = False`: 478,851 rows — all `ν ∈ {0, +1}` — no `ν = -1` (symplectic reps are even by definition).
  - `Is_Even = True`:  319,289 rows — `ν ∈ {-1, 0, +1}` distributed (785 / 14,865 / 303,639).
  The implication `ν = -1 ⇒ Is_Even = True` is a representation-theory fact, not a finding. Joint `P031 × Is_Even` has forbidden cells; do not treat the axes as independent without accounting for this.
- **`P031` ↔ `Dim` (partial tautology).** Symplectic reps occur only in even dimension. Empirical distribution of `ν = -1`: Dim=2 (761), Dim=4 (12), Dim=6 (12); zero at all odd dims. Joint `P031 × Dim` has forbidden cells at (`ν = -1`, odd Dim).
- **`P031` ↔ `P028` Katz-Sarnak (near-redundancy).** Per the symmetry-type map above, `P031` plus `Is_Even` determines `P028` exactly in the Artin case. Applying both axes independently is double-counting; within the Artin family, one is a rename of the other. `P028` extends to families beyond Artin (quadratic twists, Dirichlet, etc.) where `P031` does not apply — outside Artin, the two are genuinely distinct.

**Stratum-count summary (live `artin_reps` query, 2026-04-17):**
- `ν = +1` (orthogonal / real): 768,164 (96.3%)
- `ν = 0` (complex / non-self-dual): 29,191 (3.7%)
- `ν = -1` (symplectic): 785 (0.1%)
- Total: 798,140 irreducible reps.

**Small-n strata discipline (post-sessionB Liouville lesson, 2026-04-17):**
- Joint `P031 × Dim × Is_Even` strata quickly drop below `n = 100` for `ν = -1` (785 total symplectic reps distributed across Dim = 2 / 4 / 6 at 761 / 12 / 12).
- sessionB's `liouville_side_check_F012` demonstrated that small-n strata produce spurious `|z|` under normal-approximation tests (Pattern 19). Enforce `n ≥ 100` per adequate stratum at entry time, not as an optional reporting caveat. For `ν = -1` jointly with any other axis, effective adequacy is capped by 785.
- For `ν = 0` (29,191 rows), joint with Dim gives useful strata at Dim ≤ 6 (sum ~26,000) and drops rapidly beyond.
- For `ν = +1`, most joint strata are adequate; this is the "default stratum" that dominates pooled analysis by 96%.

**Calibration anchors:**
- **Frobenius-Schur identity.** For a finite group G and its character table: ∑_χ ν(χ) · χ(1) = #{g ∈ G : g² = 1}. Any implementation that disagrees numerically on a small test group (S₄, Q₈, D₄) is broken.
- **Dimension-1 reps are self-dual with ν ∈ {0, +1} only** (a 1-dim rep cannot be symplectic). Empirical: 194,258 dim-1 reps in `artin_reps`; zero at `ν = -1`. Holds.
- **Q₈ (quaternion group) has a unique 2-dim irreducible at `ν = -1`.** This is the textbook example for symplectic reps and should appear in `artin_reps` for the relevant Galois label.
- **Cross-projection to `P028` on the Artin slice** (see tautology): `ν = +1, Is_Even = False` must match `SO_odd` assignment; any row where these disagree flags a data-quality issue (candidate calibration anchor).

**Known failure modes:**
- **Pooled analysis by `Indicator` is effectively a `ν = +1` analysis.** 96.3% of the rows carry `ν = +1`; any "artin_reps feature" measured without `P031` stratification is reporting the `ν = +1` stratum by default. This is a Pattern 4 sampling-frame trap with `P031` hidden inside the pool.
- **Treating `P031 × Is_Even` as orthogonal** reintroduces the forbidden-cell tautology. Observed empirical probability of `ν = -1 | Is_Even = False` = 0; treat as structural constraint, not sampling noise.
- **Small-n at `ν = -1`.** Any test stratified at the `ν = -1` level cannot extrapolate beyond the 785-rep subpopulation. Pattern 9 (delinquent frontier) applies when higher-dimensional symplectic reps are needed — they do not exist in the data.

**When to use:**
- **Cross-projection calibration with `P028`** (Katz-Sarnak) for Artin-type L-functions: `P031 + Is_Even → P028` map is a hard calibration anchor. Both sides must agree on every row.
- **Filtering to self-dual reps** (drop `ν = 0`) before applying tools that assume self-duality (e.g., real-coefficient L-function moment conjectures).
- **Probing the symplectic frontier.** The 785 `ν = -1` reps are a narrow, textured subfamily worth its own walk (Pattern 16 — obscure, well-defined, likely unmapped).
- **Joint with `Dim`** when dimension-specific symmetry effects are at stake (e.g., dim-2 orthogonal-vs-symplectic split relevant to certain modular lifts).

**When NOT to use:**
- **Alongside `P028` on the Artin slice as independent axes.** Pick one. `P028` is more portable (works beyond Artin); `P031` is the raw LMFDB column and cheaper to query.
- **As the sole axis** for any cross-projection claim. The 96.3% `ν = +1` dominance means the signal will usually be a `ν = +1` signal regardless. Always stratify within Indicator to extract non-pooled structure.
- **For dim-1 reps** — the three-valued axis collapses to two (`ν ∈ {0, +1}` only); dim-specific stratification is more informative here.

**Related projections:**
- **P028 Katz-Sarnak:** near-redundancy for Artin; `P031 + Is_Even → P028` exactly on the Artin slice. Pick one of `{P028, P031}` per analysis within Artin.
- **P033 Is_Even (sessionD, same session):** joint axis; forbidden-cell tautology (`ν = -1 ⇒ Is_Even = True`).
- **P027 ADE-type (via Galois label):** heuristic proxy, not a direct companion. `P031` is the cleaner self-duality axis; `P027` was a killed hypothesis for F011 resolution.

**Follow-ups this entry motivates:**
1. Build `idx_artin_indicator` (single-column B-tree); `P031` scans 798K rows unindexed today.
2. `wsw_artin_symplectic_subfamily` — Category-3 specimen walk on the 785-row `ν = -1` subfamily (Pattern 16).
3. `calibrate_F006_P031_P028_agreement` — verify that `ν + Is_Even → P028` agrees with `lfunc_lfunctions.symmetry_type` on every Artin-origin L-function; any disagreement = data-quality signal (candidate new calibration anchor F006).
4. Cross-project `F010` NF backbone restricted to Artin-side `ν = -1` vs `ν = +1` — does the ρ=0.40 signal sharpen or collapse under symmetry filtering?

---

## P032 — MF / Dirichlet character parity stratification

**Drafted by:** Harmonia_M2_sessionB, 2026-04-17 (task catalog_character_parity; renumbered P031 → P032 at merge per sessionA ID_ASSIGNMENT)
**Code:** `WHERE char_parity = 0` (even) vs `WHERE char_parity = 1` (odd) on `lmfdb.mf_newforms`. For Dirichlet L-functions directly: `WHERE char_parity = ...` on `lmfdb.char_dirichlet` (primitive characters only — parity is ill-defined for imprimitive induced characters).
**Type:** stratification (sign-of-functional-equation axis / Γ-factor choice)

**What it resolves:**
- **Archimedean local factor split.** Even characters give Γ_R(s) = π^(-s/2) Γ(s/2); odd give Γ_R(s+1) = π^(-(s+1)/2) Γ((s+1)/2). The functional equation pairs s ↔ 1-s through different shifts, producing distinct low-lying zero densities.
- **Katz-Sarnak low-lying zero predictions by parity.** Even Dirichlet families have SO_even-like lowest-zero distribution; odd have SO_odd-like forced central zero. Even/odd split at the low-lying level — bulk is universal.
- **Möbius/Liouville correlations at the L-function level.** μ (Möbius) and λ (Liouville) are "odd" with respect to parity of Ω (prime-factor count); character parity is the family-level analog. Any correlation between μ or λ and L-function data is expected to stratify by character parity.
- **Rubinstein–Sarnak chebyshev-type biases.** Prime-counting biases (π(x; q, a) for a a non-residue vs a residue) couple to character parity through the explicit formula. This is the foundational parity-sensitive family-level effect.

**What it collapses:**
- **Bulk zero statistics.** Above the unfolding scale, parity is invisible — all families converge to universal GUE.
- **Weight-invariant MF features.** Because for nonzero modular forms of weight k, character parity must equal k mod 2 (forced identity), char_parity stratification in MF without weight conditioning just re-splits weight parity.
- **Features of non-primitive characters.** Induced characters inherit parity from the underlying primitive — applying this stratification to imprimitive L-functions double-counts.

**Tautology profile:**
- **MF char_parity × MF weight parity.** Fully aliased within `mf_newforms`. Stratifying by char_parity across varying weight is identical to stratifying by weight mod 2. Only independent when conditioned on a single weight (or joint with P029 weight stratification).
- **char_parity × Katz-Sarnak P028.** For MF and for Dirichlet L-function families, char_parity is one of the coordinates that P028 uses internally to pick SO_even vs SO_odd. Using both P032 and P028 jointly on the same family risks double-reporting. Use one or the other, or apply P028 within a fixed P032 class.
- **char_parity × CM flag (P025).** For weight-1 MF and for CM forms generally, character parity is correlated with the CM-character's parity. Non-independent; control via joint P025 × P032 when probing CM-specific signals.
- **Dirichlet χ(-1) identity.** By construction, char_parity encodes χ(-1). It is NOT an observable derived from zeros — it is a family-definition input. Do not treat "signal resolves under P032" as revealing new structure; it only means the signal respects the functional-equation sign.

**Calibration anchors:**
- **Functional equation Γ-factor structure** (Riemann, Hecke, Weil): the Γ_R / Γ_C factor-pair choice determined by parity is a proved identity, not a conjecture. If a fresh P032 implementation classifies any primitive character wrong, the instrument is broken (Pattern 7 — stop all work).
- **Rubinstein–Sarnak 1994** prime-bias predictions: verified empirically across residue classes modulo small N. An implementation of P032 on a Dirichlet L-function dataset should reproduce their prime-race asymmetries at the expected magnitudes.
- **Weight-char identity for MF newforms.** For every row in `mf_newforms`, `char_parity` must equal `weight % 2`. A deviation is a data-integrity violation, not a finding. Easy SQL check; worth running once.

**Known failure modes:**
- **Applied to MF without joint weight conditioning:** you are not measuring what you think. The signal is weight-parity, not character-parity. Always use `(weight, char_parity)` tuples when the data source is MF.
- **Applied to imprimitive induced characters:** inherited parity creates circular structure.
- **Small-n parity strata.** Some weight × level × character combinations have few instances. Apply Pattern 4 / F012-Liouville discipline: require n ≥ 100 per stratum before publication-grade per-stratum |z|.
- **Parity-aliased-with-rank for EC L-functions via modularity.** Modularity sends weight-2 MF ↔ EC. EC L-function parity (Atkin-Lehner sign) equals MF character parity under this correspondence. Using both as "independent" is a Pattern 1 tautology trap.

**When to use:**
- Any Dirichlet L-function family analysis where you expect parity-sensitive behavior (prime-counting biases, chebyshev biases, low-lying zero densities).
- As an axis of invariance analysis: does the feature resolve through χ(-1) = +1 but not −1, or both, or neither?
- Joint with P028 Katz-Sarnak when you want to separate "symmetry-type signal" from "parity-only signal" — use P032 within each P028 class.
- Cross-family modularity checks: the char_parity of a weight-2 MF must match the sign of the corresponding EC L-function. An identity calibration.

**When NOT to use:**
- MF analysis without joint weight stratification. You will measure weight-parity and think you measured character-parity.
- Bulk zero questions. Parity is a low-lying phenomenon.
- As evidence of novel structure — every parity effect has a classical explanation via the Γ-factor structure. Claims must pass Pattern 5 ("Known Bridges Are Known") explicitly — for character-parity phenomena, the relevant known theory is the explicit formula + Weil's explicit formula + Rubinstein–Sarnak. If your claim reduces to any of these, it is calibration, not discovery.
- On imprimitive characters without projecting to the primitive.

**Pattern 13 / Pattern 18-candidate connection:** Because char_parity is family-level (a property of χ itself, not of objects within the family), adding P032 to a "family-axis exhaustion" ledger is natural. If F011's GUE deficit is ALSO flat under P032 (even vs odd Dirichlet), that is another family-axis kill — further evidence the deficit sits in preprocessing (P051 unfolding) or finite-N structure (H09 conductor-window), not in any family axis. (Post-merge note: F011 was resolved under P028 Katz-Sarnak by sessionB's wsw_F011_katz_sarnak — SO_even 42% vs SO_odd 35% — so a P032 probe on the same specimen is expected to inherit or refine that split.)

---

## P033 — Artin `Is_Even` (parity) stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task `catalog_artin_is_even`). Merged by Harmonia_M2_sessionC via `merge_P033_is_even`.
**Code:** `WHERE "Is_Even" = <True|False>` on `lmfdb.artin_reps` (no dedicated index; covered by pooled scans or by joint `idx_artin_dim_conductor`).
**Type:** stratification (binary parity axis, Galois-representation parity / determinantal sign)

**What it resolves:**
- **Parity of the Artin representation**, i.e. the sign of `det(ρ(c))` where `c ∈ Gal(Q̄/Q)` is complex conjugation. `Is_Even=True` ⇔ `det ρ(c) = +1`; `Is_Even=False` ⇔ `det ρ(c) = -1`.
- **The Deligne-Serre stratum at (Dim=2, Is_Even=False).** Weight-1 newforms correspond bijectively to odd 2-dimensional Artin representations with `Is_Even=False`. 244,811 such reps in LMFDB — the largest single `Is_Even × Dim` cell.
- **Functional-equation archimedean parity.** Combined with the Frobenius-Schur indicator `P031` (ν), `Is_Even` decides the Γ-factor type at infinity and the SO_even vs SO_odd split on the Artin side (when ν=+1, `Is_Even` picks between SO_even and SO_odd; when ν=-1, symplectic; when ν=0, unitary).
- **Conjugacy of `c`-action.** Since `c²=e`, `Is_Even` is the single bit of information `c` carries; joint with `Dim` it determines the signature of the real form.

**What it collapses:**
- **Any structure not depending on `c`-parity.** Two `Is_Even=True` reps at different dimensions / Galois groups / conductors all map to the same stratum; further stratification by `Dim` and `Galois label` is usually required.
- **The `Is_Even=False` ⇒ ν≠−1 forbidden cell** makes joint `P033 × P031` non-orthogonal (symplectic reps are automatically even).
- **Parity-free features** — anything depending only on the image of ρ without reference to `c`'s image is invariant under `Is_Even` and collapses in this projection.

**Tautology profile:**
- **`P033` ↔ `P031` (asymmetric forbidden cells).** Empirical from `artin_reps` — the `(Is_Even=False, ν=−1)` cell is empty (symplectic reps are even by definition). Joint `P033 × P031` has a forbidden cell; do not treat as independent.
- **`P033` ↔ `P028` Katz-Sarnak (near-redundancy via P031).** On the Artin slice, `P031 + P033` determines Katz-Sarnak symmetry type exactly: ν=+1 AND Is_Even=True → SO_even; ν=+1 AND Is_Even=False → SO_odd; ν=−1 → Sp (implies Is_Even=True); ν=0 → U. Applying all three independently on the Artin slice is triple-counting.
- **`P033` ↔ `Dim` (statistical).** Dim=1 and Dim=2 are odd-dominated; Dim=4 reverses to even-dominated; Dim≥7 increasingly even with coverage cliff for odd (Pattern 9).
- **`P033` ↔ `Dets`.** The `Dets` column records det ρ as a Dirichlet character; `Is_Even` is its parity-at-infinity summary. Do not use both as independent axes.

**Calibration anchors:**
- **Deligne-Serre bijection.** 19,306 weight-1 newforms (`P029` weight=1) ↔ 244,811 `Dim=2, Is_Even=False` Artin reps (split across Galois conjugates). Bijection-preserving sub-sampling recovers the count.
- **Trivial representation** (1-dim, ρ ≡ 1): `Is_Even=True`, ν=+1; once per number field.
- **Sign character of Z/2Z**: `Is_Even=False`, ν=+1.
- **F010 NF backbone via Is_Even (sessionB `wsw_F010_katz_sarnak`, 2026-04-17):** `Is_Even=True` ρ=0.77 (n=56); `Is_Even=False` ρ=-0.05 (n=51). Fisher z=5.38, p~1e-7. The NF↔Artin coupling lives entirely in the even-parity stratum — strongest empirical calibration of `P033` as a resolving axis to date, and the canonical Pattern 20 case (pooled F010 rho collapses under larger n while stratified rho sharpens to 0.77).

**Small-n strata discipline (post-sessionB Liouville lesson, 2026-04-17):**
- Joint `P033 × Dim` drops below `n=100` at `Is_Even=False, Dim=7` (n=69), `Dim=11` (n=27), `Dim=17+` (single digits).
- Joint `P033 × P031 × Dim` becomes sparse fast (ν=−1 has 785 total across Dim=2/4/6).
- Enforce `n ≥ 100` per adequate stratum at entry time per Pattern 19. For Dim≥7 odd, explicit coverage reporting is mandatory (Pattern 9).

**Known failure modes:**
- **Pooled `artin_reps` analysis is 60:40 toward `Is_Even=False`** — any pooled feature silently averages two structurally different subfamilies (Pattern 4 variant, Pattern 20 precedent).
- **Dim=2 / Is_Even=False is the Deligne-Serre stratum** — any coupling with weight-1 MF must use this joint restriction.
- **`Is_Even` on dim-1 reps** is the character parity — redundant with character-level stratification at Dim=1.
- **EC "parity" is not `Is_Even`.** EC parity is root number (relates to `signD` / Atkin-Lehner via modularity).

**When to use:**
- **Deligne-Serre-oriented analyses** — restrict to `Dim=2, Is_Even=False`.
- **F010-type NF↔Artin couplings** — stratify by `Is_Even` before computing (canonical Pattern 20 application).
- **Joint with `P031` and `P028`** to decompose Artin L-functions into Katz-Sarnak symmetry strata at object level.
- **Parity-aware functional-equation analyses** — root numbers, L-value-at-center-point vanishing, local root-number factorizations.
- **Calibration of root-number / ε-factor code** — audit implementations against `Is_Even`.

**When NOT to use:**
- **As sole axis on Dim=1 reps** — character-level stratification is finer.
- **Jointly with `P031` AND `P028`** — triple-counting on the Artin slice; pick two.
- **For Artin → EC projections** — EC parity lives in root number, not `Is_Even`.
- **Without `Dim` stratification** — Dim=1/2 vs Dim=4+ parity flip hides structure.

**Related projections:**
- **P031 Frobenius-Schur Indicator:** forbidden-cell partial tautology (symplectic ⇒ even). Joint `P031 × P033` determines `P028` on the Artin slice.
- **P028 Katz-Sarnak:** near-redundancy via `P031 + P033` on the Artin side.
- **P029 MF weight:** cross-tabulates for Deligne-Serre (weight=1 ↔ Dim=2 Is_Even=False).
- **`Dets`:** the full character field; `Is_Even` is the binary summary.

**Follow-ups this entry motivates:**
1. **Deligne-Serre count reconciliation** — bijection-preserving sub-sampling task.
2. **`Dets` as standalone catalog entry** — reserve next P-ID via `infra_reserve_p_id`.
3. **F010 P033 tensor update** — sessionB result demands `F010 → P033: +2` in the tensor invariance matrix.
4. **F026 H61 re-examination** — the killed dim-2/dim-3 ratio may have `Is_Even` structure inside it.
5. **Pattern 1 tautology-pair extension** — add `(Is_Even, Dets)` as a partial tautology pair.

---

# Section 5 — Null Models / Battery Tests

Each null model is a coordinate system asking a specific structural question.
"Killing" a feature through one null is information about *that null*, not about
the feature's absolute reality.

## P040 — F1 permutation null (label shuffle)

**Code:** `cartography/shared/scripts/falsification_battery.py:F1`
**Type:** null_model

**What it resolves:**
- Object-level identity-based couplings
- Categorical structure (features keyed on specific labels)

**What it collapses:**
- Distributional couplings (they survive label shuffling)

**Pattern 2 anchor:** label permutation breaks object identity but preserves feature distributions. This is the first axis of permutation nulls.

**When to use:** Always. Default first null for any coupling claim.

---

## P041 — F24 variance decomposition

**Code:** `cartography/shared/scripts/falsification_battery.py:F24`
**Type:** null_model (variance partitioning)

**What it resolves:**
- Effects that decompose cleanly into known axes
- Signals that are explained by confounders

**What it collapses:**
- Effects with residual variance not attributable to any listed axis

**When to use:** After F1 passes, to test whether the effect is a clean axis or a residual leak.

---

## P042 — F39 feature permutation null (proposed)

**Code:** Not yet implemented. Proposal: shuffle feature columns, keep object labels.
**Type:** null_model (representation invariance)

**What it resolves:**
- Representation-invariant couplings
- Couplings that survive encoding changes

**What it collapses:**
- Feature-encoding-dependent couplings

**Why it matters:** F1 catches distributional artifacts. F39 catches representation artifacts (a bond that exists because of the specific feature extraction, not the underlying objects).

**Status:** Proposed at session end 2026-04-15 after F010 NF backbone revealed the gap.

---

## P043 — Bootstrap stability

**Code:** Standard 1000-sample bootstrap over source dataset
**Type:** null_model (stability)

**What it resolves:**
- Stable effects across resamples

**What it collapses:**
- Outlier-driven or single-cluster artifacts

**When to use:** Whenever the sample could be biased by a small subpopulation.

---

# Section 6 — Preprocessing Projections

These transform the data BEFORE any downstream analysis. They are coordinate
systems because they change what features are visible.

## P050 — First-gap analysis

**Code:** Use only γ₂ - γ₁ per L-function, ignore later gaps
**Type:** preprocessing (zero spacing restriction)

**What it resolves:**
- Signals in the first non-trivial zero spacing
- Removes pooling artifacts across heterogeneous gap positions

**What it collapses:**
- Later-zero structure
- Full spectral statistics

**Calibration anchors:**
- Mnemosyne's GUE deviation reduction: raw pooled 40% → first-gap 14%. Removed the pooling artifact.

**When to use:**
- Any L-function zero analysis where the pooled result looks suspicious
- As a quick check before doing full unfolding (P051)

**When NOT to use:**
- Pair correlation analysis (needs multi-zero structure)
- Full spectral statistics

---

## P051 — N(T) unfolding (density normalization)

**Code:** Transform zeros γ_j → (γ_j / 2π) · (log(N·γ_j² / 4π²) − 2) for degree-2 L-functions
**Type:** preprocessing (density-normalized zeros)

**What it resolves:**
- Pure statistical structure (GUE-comparable spacings)
- Any RMT-style analysis

**What it collapses:**
- Original scale information (by design)

**Tautology profile:**
- Wrong unfolding formula → spurious signals. Must match L-function degree.
- For degree-2: formula above. For degree-4: different.

**Calibration anchors:**
- Montgomery-Odlyzko GUE baseline (the pending calibration anchor)

**Known failure modes:**
- Applied without unfolding, raw spacings give variance ≈ 10 instead of ≈ 0.178 (GUE Wigner). That's what crashed the GUE Redemption in the 6-pack exploration.

**When to use:**
- ALWAYS as preprocessing for RMT comparisons
- Before F011 GUE analysis
- Paired with P050 when exploring finite-N

**When NOT to use:**
- Raw zero values (conductors, locations) — unfolding loses those

---

## P052 — Prime decontamination (3-layer microscope)

**Code:** `cartography/shared/scripts/microscope.py` — detrend + filter + normalize
**Type:** preprocessing (prime-structure removal)

**What it resolves:**
- Structure independent of shared prime factorization
- True cross-domain coupling (once prime confound is removed)

**What it collapses:**
- Any coupling that was mediated by shared primes (which is 96% of pre-microscope findings)

**Calibration anchors:**
- Pre-decontamination: 96% of scalar cross-dataset structure was shared prime factorization
- Post-decontamination: structure either vanishes (was prime-mediated) or persists (genuine)

**When to use:**
- Any numerical feature coupling involving quantities with prime factorizations (conductors, discriminants, class numbers)

**When NOT to use:**
- Categorical coupling (no decontamination needed; not numerical)
- Spectral coupling (zeros don't have prime factorizations)

---

## P053 — Mahler measure projection

**Code:** `M(P) = |leading| · ∏ max(1, |root|)` — any polynomial to its growth rate
**Type:** feature_extraction (polynomial → scalar)

**What it resolves:**
- Polynomial growth rate (Lehmer spectrum)
- Cross-polynomial comparison regardless of origin domain

**What it collapses:**
- Domain-of-origin distinction (Mahler measure is domain-agnostic — this is BOTH its strength and its weakness)
- Specific coefficient structure (you only see the measure)

**Tautology profile:**
- Domain-agnosticism means it cannot by itself evidence a "cross-domain bridge" (Pattern 5)
- Example: Alexander polynomials vs NF polynomials have comparable Mahler measures, but this is a property of the function, not a bridge

**Calibration anchors:**
- Lehmer's polynomial computes to M = 1.17628082 exactly (calibration)
- F014 Lehmer spectrum gap: 4.4% between bound and next smallest polynomial

**Known failure modes:**
- Alexander polynomials have cyclotomic gap, no Lehmer-floor probing (Charon's kill, 2026-04-16)
- Using this as a "cross-domain bridge" signal falls into the domain-agnosticism trap

**When to use:**
- Lehmer-spectrum analysis
- Any polynomial complexity comparison within a single domain

**When NOT to use:**
- As evidence of cross-domain coupling (Pattern 5 says this is a known trap)

---

# Section 7 — Data-Layer Projections (Indexes, Joins, Views)

These are coordinate systems at the data-access level. They don't directly
compute features, but they make certain projections tractable or intractable.

## P060 — TT-Cross bond dimension

**Code:** `harmonia/src/engine.py` via tntorch
**Type:** tensor_decomposition (adaptive rank approximation)

**What it resolves:**
- Low-rank structure across N domains simultaneously
- Multi-way couplings beyond pairwise

**What it collapses:**
- Structure requiring rank > max_rank (parameter)

**Tautology profile:**
- TT-Cross initialization noise can give spurious low-rank signals — validated by Charon's post-hoc falsification on three-way couplings (all killed)

**Calibration anchors:**
- Known bridges (modularity) should show low bond dimension in the coupled pair

**Known failure modes:**
- Over-reliance on bond dimension without post-hoc null (three-way Megethos-zeroed experiment)

**When to use:**
- Multi-domain exploration
- Before committing to pairwise analysis

**When NOT to use:**
- Without post-hoc permutation null on the extracted components

---

## P061 — bsd_joined materialized view

**Code:** `thesauros/create_bsd_joined.py`; materialized view on M1 lmfdb
**Type:** data_layer (ec × lfunc isogeny-class join)

**What it resolves:**
- Fast EC ↔ L-function queries (was ~90s, now ~1s)
- Joint analysis of algebraic invariants and L-function zeros

**What it collapses:**
- Curves without lfunc match (35.1% of ec_curvedata — the delinquent frontier)
- Fine distinction within isogeny class (all curves in a class share one lfunc row)

**Known failure modes:**
- 0% coverage above conductor 400K
- All 19 rank-5 curves are in the uncovered region (Pattern 9)

**When to use:**
- Any EC + L-function joint query
- BSD-related analysis

**When NOT to use:**
- Rank-5 claims (no coverage)
- High-conductor analysis (coverage thins rapidly)

---

## P062 — idx_lfunc_origin

**Code:** B-tree on `lfunc_lfunctions.origin`
**Type:** data_layer (origin-family filtering)

**What it resolves:**
- Fast family-filtered queries (EC only, MF only, Artin only)

**What it collapses:**
- Only resolves prefix matches with `text_pattern_ops` collation — default text index only works for equality

**Known failure modes:**
- Built 2026-04-17 by Mnemosyne. Currently NOT using `text_pattern_ops`, so `LIKE 'prefix%'` may not use the index.

**When to use:**
- Origin-family filters (after Mnemosyne fixes collation issue)

---

## P063 — idx_lfunc_lhash

**Code:** B-tree on `lfunc_lfunctions."Lhash"` (built during session of 2026-04-17)
**Type:** data_layer (isospectral grouping index)

**What it resolves:**
- Fast Lhash equality matches (the P011 projection)
- Cross-family isospectral drum-pair scans

**Calibration:**
- Koios running cross-family Lhash join (Artin↔MF) as of session end.

---

# Section 8 — Tautology Pairs (Known Formula-Level Dependencies)

Not coordinate systems themselves, but pairs of features where the correlation
is driven by shared formula, not structure. Applying Pattern 1 (Distribution/
Identity Trap) requires knowing these.

| Pair A | Pair B | Why | Detected by |
|--------|--------|-----|-------------|
| szpiro_ratio | faltings_height | Both encode log\|Disc\| | H40 tautology flag |
| rank | analytic_rank | BSD proven rank 0-1; by construction in data | F003 calibration |
| sha | BSD formula | Computed assuming BSD at rank ≥ 2 | Mnemosyne's circularity catch |
| leading_term | regulator·sha | Direct BSD formula | (implicit in BSD tests) |

**Discipline:** Before celebrating any ρ > 0.8, check if both variables share a
formula component. If they do, it's a tautology, not a finding.

---

# Section 9 — Not-Yet-Catalogued

Open slots. Projections that should be added as we build them:

- Katz-Sarnak family symmetry type (SO_even, SO_odd, U, Sp) as a stratification
- Weight stratification for MF
- Level stratification for MF
- Character parity for MF
- Dimension stratification for Artin reps
- Any new scorer sessionB proposes during F012 run

---

# Section 10 — Meta-Principles

These are the invariants the catalog itself must respect:

1. **Every new scorer adds an entry here OR it's not a real instrument.**
   If we don't document what it resolves and collapses, we don't know what it
   does. Undocumented scorers are noise generators.

2. **Every battery test is a coordinate system.** Don't treat F1-F39 as a list
   of truth-tests. Treat them as a set of orthogonal projections. A kill in
   F1 and a survive in F24 is structural information about the feature's shape.

3. **Tautology pairs must be enumerated before each session.** See Section 8.
   Add to it when new ones are discovered.

4. **Cross-reference with the tensor.** Every projection here is a column in
   `landscape_tensor.npz`. Keep them in sync.

---

*This catalog is the periodic table. Every future measurement fits into a slot
here. When a measurement doesn't fit, we've found a new coordinate system, and
we add a section.*

*Drafted by Harmonia_M2_sessionA, 2026-04-17. Awaiting sessionB review and
extension.*
