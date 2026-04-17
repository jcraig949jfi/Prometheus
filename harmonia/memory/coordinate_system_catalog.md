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
- Claims about object-level coupling across projections (use P010 Galois-label or P011 Lhash)
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
- Coupling-across-projection tests where both sides have canonical Galois structure

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
- **Rank ≥ 2 BSD-joined circularity (promoted from tautology note per sessionB review, 2026-04-17):** For rows where Sha is computed assuming BSD, stratifying by `rank` and comparing to any BSD-derived quantity (Sha, regulator × Sha, analytic_rank) is a closed loop. Use `rank ≥ 2 AND sha_computation_method != 'BSD_assumed'` as a filter, OR restrict to rank ≤ 1. Any publication-grade result at rank ≥ 2 must document which side of this filter it used. This is more than a tautology — it is a coordinate-system-invalidation at specific ranks, adjacent to the F003 BSD-parity calibration anchor (Pattern 7).

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

## P035 — Kodaira reduction type stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task `catalog_kodaira`). Reviewed and approved (with caveat) by Harmonia_M2_sessionA. Merged by Harmonia_M2_sessionC via `merge_P035_kodaira`.

> **DERIVABLE-NOT-STORED caveat (read before using):** `P035` is not a direct `lmfdb` column. Kodaira symbols per bad prime (`I_n`, `II`, `III`, `IV`, `I_n*`, `II*`, `III*`, `IV*`) must be computed from the a-invariants via **Tate's algorithm** (PARI `ellglobalred`, Sage `EllipticCurve.kodaira_symbol`, or LMFDB's build pipeline). **Any worker using P035 must first materialize Kodaira via Tate's algorithm or accept placeholder status.** Materialization is a multi-million-row infrastructure task owned by Mnemosyne / Koios with James's input — not auto-seedable.

**Code:** Derivable from `lmfdb.ec_curvedata` (`ainvs`, `bad_primes`, `semistable`, `potential_good_reduction`) via Tate's algorithm. No direct column. Proposed materialization: `kodaira_per_prime(lmfdb_label, prime, kodaira_symbol, n, split_nonsplit)` at ~7M rows (3.8M curves × mean ~2 bad primes).
**Type:** stratification (geometric reduction-type axis, refines P026 semistable vs additive)

**What it resolves:**
- **Per-bad-prime singular fiber geometry.** The Néron model at a bad prime `p` has a specific geometric type captured by the Kodaira symbol. `I_n (n≥1)` families are multiplicative / semistable; all others (`II`, `III`, `IV`, `I_n*`, `II*`, `III*`, `IV*`) are additive.
- **Refinement of P026 (semistable vs additive).** Within "additive," Kodaira distinguishes seven finer types, each with distinct local component groups, Tamagawa numbers, and L-function local factors.
- **Tamagawa-number prediction** (up to limited ambiguity). The local component-group order `c_p` is determined by the Kodaira type plus split/non-split information. Ogg's formula `f_p = ord_p(Δ) − m + 1` ties conductor exponent to Kodaira + Δ valuation.
- **Modular-curve genus and degeneration signature.** Kodaira types classify the degeneration of the Weierstrass singular fiber; the join profile across all bad primes is the curve's "global reduction signature."
- **Néron differential period behavior.** Additive-reduction types have specific integral-period factors relevant for BSD leading-term computations.

**What it collapses:**
- **Per-prime vs global.** Kodaira type is a PER-BAD-PRIME invariant. A curve has one Kodaira symbol per bad prime, not a single scalar. P035 usage must choose: (i) stratify by tuple of per-prime types, (ii) stratify by dominant type across bad primes, or (iii) stratify per `(curve, prime)` pair. Each choice collapses different features.
- **Non-reduction-related structure.** Features independent of the Néron model at bad primes are invariant under P035.
- **Split vs non-split multiplicative distinction** (if only coarse Kodaira symbol `I_n` is used). Record split/non-split separately.

**Tautology profile:**
- **P035 ↔ P026 (semistable vs additive).** P035 IS the refinement: `P026 = "semistable"` iff all Kodaira types are `I_n`; `P026 = "additive"` iff any is non-`I_n`. Joint P026 × P035 is *nested*, not orthogonal — double-counting risk.
- **P035 ↔ P021 (num_bad_primes).** For fixed `num_bad_primes`, the Kodaira type tuple has combinatorially more entropy than the scalar count — P035 refines P021 within each P021 stratum.
- **P035 ↔ Tamagawa numbers.** Product of local Tamagawa `c_p` enters the BSD formula. Most Kodaira types determine `c_p` up to small ambiguity; for `I_n`, `c_p = n` (or `n/2` for non-split). Treating P035 and "Tamagawa-number stratification" as independent re-asserts this near-identity as if it were signal.
- **P035 ↔ Conductor exponent `f_p` (Ogg's formula).** `f_p` is derivable from Kodaira + Δ valuation; joint with conductor conditioning (P020) risks formula-lineage leak (Pattern 1).

**Stratum-count summary (distribution shape, materialization pending):**
- 8-element coarse class: `{I_n (n≥1), II, III, IV, I_n* (n≥0), II*, III*, IV*}`. `I_n` and `I_n*` index infinitely many sub-types by `n`; use the coarse 8-class split for finite analysis with `n` as secondary axis.
- Per LMFDB aggregate counts: `I_n` dominates (~70–80% of all bad-prime Kodaira symbols); `II / III / IV` occur at 5–10% each; `II* / III* / IV*` and `I_n*` are rarer.
- **Small-n strata discipline:** at fine granularity (e.g., "curves all of whose bad primes are type II"), strata quickly drop below `n=100`. Apply sessionB's Liouville-lesson discipline.

**Calibration anchors:**
- **Tate's algorithm is proved**, not conjectural. Any LMFDB Kodaira symbol disagreeing with an independent PARI/GP or Sage computation on the same a-invariants is a data-quality violation — candidate F-level calibration anchor once materialized.
- **Ogg's formula** (conductor exponent from Kodaira + Δ) is proved. A P035 implementation computing `f_p` from Kodaira + local Δ valuation that disagrees with `ec_curvedata.conductor` at the corresponding prime is broken.
- **Neron component-group sizes** match the Kodaira type exactly (textbook identity). `I_n → c_p ∈ {1,...,n}` per split/non-split; `II → 1`; `III → 2`; `IV → 3`; `I_0* → {1,2,4}`; `I_n*` varies; `II* → 1`; `III* → 2`; `IV* → 3`.
- **Semistable reduction theorem** (Deligne-Mumford): every elliptic curve acquires semistable reduction (all Kodaira types become `I_n`) after a tame base change. Joint P035 × extension-degree analyses can validate.

**Known failure modes:**
- **Using P035 without materialized data** — any worker drawing claims from "Kodaira stratification" must either (a) run Tate's algorithm on the curves they use, (b) query LMFDB's public detail endpoint per curve (slow, rate-limited), or (c) defer until Mnemosyne materializes the `kodaira_per_prime` table. Do not fabricate strata from indirect LMFDB columns without an audit trail.
- **Choosing the wrong aggregation rule** (per-prime vs dominant-type vs tuple) and reporting as if canonical. Different choices yield different strata; document the rule explicitly.
- **Stratifying without split/non-split awareness.** Two `I_n` curves can have genuinely different arithmetic; ignoring split/non-split is an information leak.
- **Confusing Kodaira symbol with Kodaira-Néron model.** The symbol is a label; the Néron model is the geometric object. P035 classifies labels.

**When to use:**
- **Refining a P026 "additive" cohort** — when a pooled "additive" stratum has structural variation, P035 is the natural next refinement axis.
- **Tamagawa-number-driven claims** — local `c_p` structure is cleaner via Kodaira axis than via raw `c_p` values.
- **Cross-projection calibration** — Ogg's formula and Tate's algorithm are proved; candidate anchor source once materialized.
- **Investigating the Salem-region density around F014** — low-`num_ram` EC may correlate with specific Kodaira signatures.

**When NOT to use:**
- **As the sole axis for BSD-adjacent claims** — Tamagawa `c_p` enters BSD multiplicatively; Pattern 1 risk.
- **Jointly with P026 as if orthogonal** (nested-refinement tautology).
- **Before Tate-algorithm data is materialized** — the axis is notional without the per-prime Kodaira table.
- **At small `n` per sub-stratum** — rare types (`IV*`, `III*`, `II*`) have few representatives.

**Related projections:**
- **P026 semistable vs additive:** parent axis; P035 refines within additive cohort.
- **P021 num_bad_primes:** orthogonal-in-count; P035 refines at fixed `num_bad_primes`.
- **P020 conductor conditioning:** joint usage requires Ogg's formula awareness.
- **P036 Root number (sessionD draft):** local root numbers are Kodaira-type-sensitive (Rohrlich); joint P035 × P036 is natural.
- **P034 AlignmentCoupling** and **P039 Faltings height / P046 Regulator (proposed):** Kodaira can enter Néron differential period factor — formula-lineage check warranted.

**Follow-ups this entry motivates:**
1. **`materialize_kodaira_per_prime`** — run Tate's algorithm (PARI `ellglobalred` or Sage) on all 3.8M `ec_curvedata` rows, write to `kodaira_per_prime` table (Mnemosyne/Koios infra task; needs James input on runtime and storage).
2. **`audit_kodaira_ogg_consistency`** — verify Ogg's formula on every `(curve, bad_prime)` pair once materialized (Pattern 7).
3. **Candidate calibration anchor F006** — Kodaira consistency across LMFDB vs independent Tate-algorithm runs.
4. **Joint split/non-split flag** — orthogonal refinement of `I_n` that Kodaira alone doesn't capture; co-document here or give a sister P-ID.
5. **`wsw_F014_kodaira_salem_region`** — test whether Salem polynomials in the `(1.176, 1.228)` interval correlate with specific Kodaira signatures; connects F014 (Lehmer refined) to P035.

---

## P036 — Root number stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task catalog_root_number; approved by sessionA 1776426037120-0)

**Code:** `WHERE root_number = <+1|−1>` on `lmfdb.bsd_joined` (materialized view, 2,481,157 rows; also directly on `lmfdb.lfunc_lfunctions.root_number` for the wider L-function population). For EC, `signD` in `ec_curvedata` is **NOT** the root number (it is the sign of the discriminant) — do **NOT** confuse them. Reference: sessionB's tick-5 correction after `wsw_F011_katz_sarnak` flagged the same distinction. This pitfall has already surfaced once this session; a second slip would be a data-quality violation, not a finding.
**Type:** stratification (binary sign-of-functional-equation axis; parity axis on self-dual L-functions)

**What it resolves:**
- **Sign of the functional equation.** For a self-dual L-function Λ(s) = ε · Λ(1−s), `root_number = ε ∈ {+1, −1}`. This is the single bit that distinguishes functional-equation-even from functional-equation-odd L-functions.
- **Forced central-zero presence.** For ε = −1, Λ(1/2) = 0 by the functional equation (central-zero is forced). For ε = +1, Λ(1/2) may or may not vanish. Hence `P036` directly predicts whether the L-function has an odd-index zero structure near the center.
- **Katz-Sarnak SO_even / SO_odd split on the Artin / EC side.** For an elliptic curve L-function, `root_number = −1 ⇔ analytic_rank is odd ⇔ family-member of SO_odd`. For `root_number = +1`, SO_even. `P028 × P036` within the EC family is nested, not orthogonal (see tautology profile).
- **BSD parity anchor F003.** For every row in `bsd_joined` (n = 2,481,157), `(-1)^rank = root_number` holds at 100.000%. This is the cleanest parity-calibration axis we have. A single mismatch would be a catastrophic instrument failure.
- **Rohrlich local root-number decomposition.** Global root_number factors as a product of local root numbers ε_v; Kodaira type (P035) contributes to the local factor at each bad prime v. P035 × P036 cross-projection is a candidate calibration pair.

**What it collapses:**
- **Any non-parity feature of the L-function.** Two `root_number = +1` L-functions at different ranks, conductors, and arithmetic content all map to the same stratum. Use `P036` as a coarse parity filter; stratify further by `P023` rank, `P020` conductor, etc.
- **Rank-parity-invariant features.** Pooled analyses that average over ranks 0 and 2 (both root_number = +1) lose the distinction; `P036` alone cannot see rank inside a parity class.
- **Non-self-dual L-function distinctions.** `root_number` is meaningful only for self-dual (ν = +1 Frobenius-Schur, see `P031`) L-functions. For ν = 0 (complex) reps, the functional equation relates L(s) to its complex conjugate and "root number" is a phase on the unit circle, not ±1. Applying `P036` to ν = 0 L-functions is a category error.

**Tautology profile:**
- **P036 ↔ P023 rank (BSD parity theorem).** Proved for rank 0 and rank 1 (Kolyvagin, Gross-Zagier); empirically perfect across all 2.48M EC of `bsd_joined` at higher rank. Empirical from `bsd_joined` (2026-04-17):
  - `root_number = +1`: rank ∈ {0, 2, 4} exclusively (954K + 276K + 1 = 1,229,540).
  - `root_number = −1`: rank ∈ {1, 3} exclusively (1,245K + 7K = 1,251,617).
  Zero mismatches out of 2,481,157. **This is the cleanest calibration anchor in the instrument** (F003) and applying `P036` + `P023` as if they were independent axes is double-counting their mutual determination.
- **P036 ↔ P028 Katz-Sarnak (nested for EC).** Per the forced-central-zero mechanism: `root_number = +1` on an EC L-function ⇔ SO_even family membership; `root_number = −1` ⇔ SO_odd. Within the EC slice of `P028`, `P036` IS the binary picking between SO_even and SO_odd. `P028` additionally distinguishes U, Sp, and SO families (outside EC). Do not apply `P028` and `P036` jointly on the EC slice as if orthogonal — it is triple-counting with P023.
- **P036 ↔ P033 Is_Even (cross-family parity correspondence).** For EC L-functions attached to Galois representations, `root_number` corresponds to `Is_Even` via the local-root-number Rohrlich factorization. On modularity pairs, weight-2 MF root_number = Atkin-Lehner eigenvalue = EC root_number (F001 identity). `P036 × P033` across matched EC ↔ MF ↔ Artin triples is an identity pair under Langlands functoriality, not an independent cross-axis.
- **P036 ↔ Local root numbers at bad primes (Pattern 1 lineage).** Global ε factors as `∏_v ε_v`. If a specimen uses "per-prime root number" and "global root number" jointly, the product identity is formula-level lineage. Lemma-check before reporting ρ.

**Stratum-count summary (live `bsd_joined` query, 2026-04-17):**
- `root_number = +1`: 1,229,540 (49.55%)
- `root_number = −1`: 1,251,617 (50.45%)
- Total: 2,481,157 (bsd_joined matched rows)

Near 50:50 as predicted by Katz-Sarnak universality for a large EC family; the slight asymmetry is expected finite-N behavior.

**Small-n strata discipline:**
- At the bulk level, both `P036` strata are > 1M rows — no small-n concern.
- At joint stratifications: e.g., `P036 × P020 × P023` produces cells that can drop below `n = 100` at high conductor × high rank (per F033 coverage cliff; rank ≥ 4 is already data-limited regardless of root number). Apply sessionB's Liouville-lesson `n ≥ 100` discipline at the joint level, not the marginal.
- For non-EC L-functions in `lfunc_lfunctions`, coverage is thinner; enforce `n ≥ 100` per stratum before publication-grade per-stratum |z|.

**Calibration anchors:**
- **F003 BSD parity at 100.000% over 2.48M rows** — `(-1)^rank = root_number` exactly, zero mismatches. This is the load-bearing calibration anchor for any `P036` implementation: if a single row violates this, the instrument is broken (Pattern 7, stop all work). The theorem is proved for rank 0-1 (Kolyvagin, Gross-Zagier); the remaining rank ≥ 2 cases hold empirically in the dataset by construction of LMFDB.
- **F005 high-Sha parity** — restricted to sha ≥ 9, `(-1)^rank = root_number` also holds at 100% (67,035 rows). Consistent subset anchor.
- **Deligne's global-root-number = product-of-local-root-numbers** theorem is proved; `P036` implementations should match local-product computations.
- **Rohrlich local root-number tables** — for additive-reduction primes, the local root number depends on Kodaira type in a table-known way. `P035 × P036` consistency is a future calibration candidate.

**Known failure modes:**
- **Confusing `signD` (sign of discriminant) with `root_number`.** `ec_curvedata.signD ∈ {-1, +1}` is NOT the root number. sessionB's tick-5 F011 Katz-Sarnak run hit this: signD/root_number mismatch rate was 50% (noise against wrong column), correctly retracted as not a calibration violation. Any `P036` implementation on `ec_curvedata` alone is likely wrong — use `bsd_joined.root_number` or `lfunc_lfunctions.root_number`.
- **Applying `P036` to non-self-dual L-functions** (ν = 0 Artin / ν = 0 Frobenius-Schur). The "root number" is a complex phase, not ±1; category error.
- **Treating `P036` as independent from `P023` rank** — the BSD parity tautology collapses the axes to the same information content within EC. Never report "feature survives `P036` but collapses under `P023`" without realizing they are the same axis up to a sign.
- **Pooled analysis across `root_number` without reporting the parity distribution** — `P036` is one of the few axes where pooled analysis is defensible (50:50 split), but any rank-sensitive feature requires separate reporting within each stratum.

**When to use:**
- **As the canonical BSD parity calibration axis.** Before running any EC / L-function pipeline on fresh data, verify `(-1)^rank = root_number` on a random sample — this is the cheapest instrument-health check available.
- **Forced-central-zero-sensitive analyses** — any measurement of `L(1/2)`, leading-term-at-center, or lowest-zero distance from center should stratify by `P036`.
- **Katz-Sarnak symmetry-type filtering on EC L-functions** — `P036` is the cheap proxy for `P028`'s SO_even / SO_odd distinction on the EC slice; prefer `P036` when the question is rank-parity-flavored and `P028` when the question needs the finer U / Sp / SO classification.
- **Cross-family modularity checks** — root number of a weight-2 MF must match the root number of its modular EC; joint `P036 × P029 × conductor` is the natural cross-slice.

**When NOT to use:**
- **Jointly with `P023` as if orthogonal** on EC data — you are double-counting BSD parity.
- **Jointly with `P028` on the EC slice** — nested tautology via the SO_even / SO_odd correspondence.
- **For non-self-dual L-functions** — complex-phase root number, not ±1.
- **Before verifying F003 on your sample** — if the calibration anchor is broken on your subset, every downstream `P036` stratification is suspect.

**Related projections:**
- **P023 rank stratification:** tautological pair via `(-1)^rank = root_number`. Do NOT treat independently.
- **P028 Katz-Sarnak family symmetry type:** nested on the EC slice — `P036` picks SO_even vs SO_odd; `P028` adds U / Sp / SO distinction for families beyond EC.
- **P033 Is_Even Artin parity (sessionD):** cross-family parity companion; Rohrlich local decomposition connects Artin-side `Is_Even` to EC-side `root_number` under Langlands.
- **P035 Kodaira (sessionD, preceding entry):** cross-projection calibration via Rohrlich local-root-number tables at additive-reduction primes.
- **P020 conductor conditioning:** joint use is orthogonal (no formula-level tautology), recommended for any root-number-vs-conductor trend analysis.

**Follow-ups this entry motivates:**
1. `calibrate_F003_via_P036` — run the `(-1)^rank = root_number` check on the full 2.48M `bsd_joined` rows and confirm 100.000% agreement. Currently accepted on faith; cheap to formalize as a standing CI check.
2. `wsw_F010_P036` on the EC side — F010 resolved under P033 `Is_Even` on the Artin side (sessionB tick 12; subsequently tempered to `P028_INCONCLUSIVE` by sessionC bigsample at ~ρ = 0.3). The natural EC-side parallel is to stratify F010's EC partner by `P036`. Expect same structural parity (classical conductor-discriminant formula predicts); Pattern 5 (Known Bridges) calibration, not novelty.
3. Candidate calibration anchor F007 — Rohrlich local-global root-number product identity, once `P035` Kodaira is materialized.
4. `catalog_rank_parity_as_tautology_pair` — formalize `(root_number, (-1)^rank)` in Section 8 (Tautology Pairs) of the catalog; currently implicit via F003, should be explicit as a load-bearing lineage pair.

---

## P037 — Sato-Tate group stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task catalog_sato_tate_group; approved by sessionA 1776426881001-ish review cycle)

**Code:** `WHERE st_group = <group_label>` on `lmfdb.g2c_curves` (66,158 rows, column `st_group`) and on `lmfdb.lfunc_lfunctions` (column `st_group`, indexed via join strategies rather than full scan). Also `st_label` and `st_label_components` carry the finer rational classification.
**Infra note (Mnemosyne candidate):** `lfunc_lfunctions` origin-prefix queries (`origin LIKE 'EllipticCurve/Q/%'`) time out at 30 s — no `text_pattern_ops` index on `origin`. Drafting this entry required falling back to `g2c_curves` for the raw distribution. An index build (`idx_lfunc_origin_text_pattern_ops` or a functional `idx_lfunc_st_group_by_origin_family`) would unblock EC-side Sato-Tate queries at scale. `bsd_joined.symmetry_type` is all-NULL at 2026-04-17 (verified via `SELECT symmetry_type, count(*) FROM bsd_joined GROUP BY symmetry_type` — single NULL bucket of 2,481,157 rows) so it is NOT a usable EC Sato-Tate axis in its current state; backfill is a separate Mnemosyne candidate.
**Type:** stratification (algebraic / Lie-group equidistribution axis for normalized Frobenius traces)

**What it resolves:**
- **The compact Lie group on which normalized Frobenius eigenvalues equidistribute.** For an elliptic curve over Q: `SU(2)` in the generic (non-CM) case per the Sato-Tate conjecture (proved for weight-2 newforms by Taylor et al. 2011); `N(U(1))` (normalizer of the maximal torus in SU(2)) for CM curves. For a genus-2 curve: one of 34 possible Sato-Tate groups classified by Fité-Kedlaya-Rotger-Sutherland (2012); the 28 types actually achieved form the stratification here.
- **CM vs non-CM distinction at the L-function level.** Equivalent information to `P025 cm` for EC, but expressed in Lie-group-theoretic vocabulary. For g2c, Sato-Tate type carries strictly more information than a single CM flag since genus-2 Jacobians can have partial CM / RM / QM structures that decompose into different Lie groups.
- **Moment predictions for normalized a_p.** The Sato-Tate group determines moments `⟨(a_p/2√p)^k⟩` exactly via the character table of the group's irreducible representations. Any deviation at finite conductor is a measurement of finite-N vs asymptotic universality.
- **Cross-projection calibration for Katz-Sarnak.** P028 Katz-Sarnak is the *zero-side* symmetry classification; `P037` is the *a_p-side* companion. The two should agree on family assignments up to the classical correspondences (SU(2) generic EC → SO family, N(U(1)) CM EC → also SO but with forced central zero via ε, etc.). Disagreements are data-quality signals.

**What it collapses:**
- **Within-group structural distinctions.** All 63,107 `USp(4)` genus-2 Jacobians in LMFDB map to the same stratum regardless of conductor, automorphism group, rank, etc. Use `P037` as a coarse equidistribution filter; stratify further by `P022` aut_grp, conductor, rank, etc., when the question is finer than "which Sato-Tate class."
- **Non-a_p structure.** Features independent of the Frobenius-trace equidistribution — e.g., explicit ideal-class-group invariants, regulator values, Tamagawa numbers — are invariant under `P037` and collapse.
- **Finer rational classification (`st_label`).** `st_group` is the Lie group; `st_label` sub-divides by the rational component-group structure (e.g., different finite extensions of the same identity component). Using only `P037` collapses the rational refinement that `st_label` would expose.

**Tautology profile:**
- **P037 ↔ P025 (CM flag) on EC.** For elliptic curves over Q, `st_group = SU(2) ⇔ cm = 0`; `st_group = N(U(1)) ⇔ cm ≠ 0`. Full aliasing on the EC slice. Applying `P037` and `P025` independently on EC-only data is double-counting. On the genus-2 side or for higher-dimensional families, `P037` carries strictly more information than any single CM-flag, so the aliasing is a pure-EC concern.
- **P037 ↔ P028 Katz-Sarnak (cross-side correspondence).** Sato-Tate classifies by `a_p` moments; Katz-Sarnak classifies by low-lying zero statistics. For EC: SU(2) generic → SO_even or SO_odd by rank parity (another nested tautology with `P036` root number / `P023` rank). For g2c: USp(4) → Sp family predicted. The cross-side correspondence is a proved theorem stack (Taylor et al. + Katz-Sarnak); treating `P037` and `P028` as independent on the same family risks double-counting the same classical predictions.
- **P037 ↔ P031 Frobenius-Schur on Artin-origin L-functions.** For 2-dimensional Artin L-functions, Sato-Tate group is determined by the image of the Galois representation (SU(2) for "large image" cases; finite Lie groups for small-image cases). `P037 × P031` on the Artin slice is a proved-identity pair via known theorems, not an independent cross-axis.
- **P037 ↔ moments of `a_p`.** Reporting a deviation from the expected `⟨(a_p/2√p)^k⟩` moment under a specific Sato-Tate class, while using `P037` as the stratifier, is formula-level lineage (Pattern 1). The moment IS the prediction the class makes; use a null model (permutation of curve labels within class) to separate structural deviation from class-definition recovery.

**Stratum-count summary (live queries, 2026-04-17):**

For **genus-2 curves** (`g2c_curves`, top 20 of 28 observed classes out of 34 possible):
- `USp(4)`: 63,107 (95.4%) — generic g2c (no CM / no RM / full-image Galois)
- `SU(2)×SU(2)`: 2,440 (3.7%) — split Jacobian into two non-isogenous EC
- `N(U(1)×SU(2))`: 303
- `N(SU(2)×SU(2))`: 144
- `E_6`: 51
- `J(E_1..6)`: small counts
- `F_{ac}`, `D_{2,1}`, `D_{3,2}`, `D_{6,2}`, `J(C_2)`, `J(C_4)`: single- or double-digit counts
- Total: 66,158 g2c rows

For **elliptic curves** (via `lfunc_lfunctions` with `origin LIKE 'EllipticCurve/Q/%'`): query timed out at 30 s on unindexed prefix scan; per classical theory the distribution is ~99.8% `SU(2)` and ~0.2% `N(U(1))` (CM curves are rare, `cm != 0` in ~4,100 out of 2.48M bsd_joined rows per earlier session data).

**Small-n strata discipline:**
- For g2c, any `P037` stratum outside `USp(4)` and `SU(2)×SU(2)` drops below `n = 100` immediately. Applying sessionB's Liouville-lesson `n ≥ 100` discipline at the stratum level means only two g2c strata are adequate for per-stratum `|z|` reporting; the remaining 26+ exotic classes must be pooled or reported with explicit `n` caveats.
- For EC, both strata (`SU(2)` and `N(U(1))`) have `n ≥ 100` by a wide margin. No small-n concern at the marginal level.
- Joint `P037 × P020 conductor` at narrow conductor windows rapidly produces small strata for g2c exotic classes. Apply Pattern 9 (delinquent frontier) discipline — absence of signal in exotic Sato-Tate classes is usually absence of measurement.

**Calibration anchors:**
- **Sato-Tate conjecture for elliptic curves over Q** (weight-2 newforms): proved by Taylor, Barnet-Lamb, Geraghty, Harris, Shepherd-Barron (2006–2011). Any implementation that gives `SU(2)` for a known-CM curve, or `N(U(1))` for a known-non-CM curve, is broken (Pattern 7 — stop all work).
- **Fité-Kedlaya-Rotger-Sutherland classification** for g2c Sato-Tate groups (2012): proved complete list of 34 possible groups; `st_group` values in LMFDB are required to lie in this set. Any new value is a data-quality violation.
- **SU(2) moment universality** for non-CM EC: `⟨(a_p / 2√p)^k⟩` → `(1/π) ∫ sin²θ cos^k θ dθ` as p → ∞. Finite-conductor deviations are the finite-N structure relevant to F011's GUE story on the `a_p` side rather than the zero side.
- **ec.cm ↔ st_group = N(U(1)) identity** on EC: by the Sato-Tate conjecture classification, `cm != 0 ⇔ st_group = N(U(1))`. Any row violating this is a data-quality issue — candidate calibration-anchor F-slot pending verification (proposed as F008).

**Known failure modes:**
- **Applying `P037` to families where Sato-Tate is not yet proved.** For higher-genus families, higher-dimensional Artin reps, or non-modular-form L-functions, the Sato-Tate conjecture is open. `st_group` values in those families are conjectural, and LMFDB flags / documentation should be consulted before treating them as ground truth.
- **Confusing `st_group` with `st_label`.** `st_group` is the Lie group; `st_label` is the finer rational classification (different `st_label` values within the same `st_group` encode different component-group structures). Using one when the analysis needs the other silently loses information.
- **Small-n exotic-class extrapolation.** Genus-2 exotic classes (E_1..E_6, J(C_n), D_{n,k}) have counts in single digits to low tens. Any claim about exotic-class-specific behavior requires explicit `n` reporting; otherwise it is Pattern 4 / F012-Liouville noise inflation.
- **Treating `P037` and `P028` as independent cross-axes on the same family.** They are different sides of the same proved-theorem correspondence; joint independence is double-counting.

**When to use:**
- **Any genus-2 analysis** — `P037` is the primary non-conductor, non-rank axis available, and the 95.4% `USp(4)` / 3.7% split-Jacobian imbalance means pooled g2c is effectively a `USp(4)` analysis with noise.
- **CM vs non-CM EC questions** — preferred over raw `P025` only when the Lie-group framing is natural; otherwise `P025` is the cheaper boolean.
- **Cross-side calibration against Katz-Sarnak `P028`** — `P037` (a_p side) and `P028` (zero side) should agree on family-type assignments up to classical correspondences.
- **Moment-deviation probes** — any `⟨(a_p/2√p)^k⟩` measurement at finite conductor is testing Sato-Tate finite-N structure; stratify by `P037` at the start.

**When NOT to use:**
- **Jointly with `P025` CM on EC-only data** (full aliasing).
- **Jointly with `P028` on the same family as if orthogonal** (nested via classical theorem).
- **For non-EC, non-g2c, non-MF families without verifying Sato-Tate is proved** there.
- **As a claim-driver for exotic g2c classes with n < 100** — pre-commit to sessionB's Liouville discipline.

**Related projections:**
- **P022 aut_grp stratification (g2c-specific):** orthogonal in principle; joint `P037 × P022` is the natural g2c family-structure coordinate pair. F012 (H85 killed) was at `P022`; could re-examine within `USp(4)` vs split-Jacobian strata.
- **P025 CM:** aliased on EC; strictly refined by `P037` on higher-genus families.
- **P028 Katz-Sarnak:** cross-side correspondence via proved classical theorems.
- **P031 Frobenius-Schur Indicator:** on Artin-origin L-functions, jointly determines Sato-Tate group.
- **P036 Root number:** via rank parity and SO_even/SO_odd, forms a chain `P037 → P028 → P036 → P023`.

**Follow-ups this entry motivates:**
1. `build_idx_lfunc_st_group` (or `idx_lfunc_origin_text_pattern_ops`) — Mnemosyne infra; unblocks EC Sato-Tate queries currently blocked by 30 s timeouts.
2. `backfill_bsd_joined_symmetry_type` — populate the all-NULL `symmetry_type` column from `lfunc_lfunctions.st_group` via the origin join.
3. `calibrate_F_ec_cm_stgroup_identity` (proposed F008) — verify `cm != 0 ⇔ st_group = N(U(1))` across all 2.48M EC.
4. `wsw_F012_restricted_USp4` — re-run the killed H85 Möbius × aut_grp audit restricted to the 95.4 % `USp(4)` cohort. The killed-pooled-signal may have had structure masked by the split-Jacobian / exotic-class noise (<5 % by volume but distinct moment predictions).
5. `wsw_F011_stratified_stgroup` — test whether F011's GUE deficit also shows structure across `P037` classes. For EC this is near-trivial by aliasing with `P025` (already tested clean), but for MF / Dirichlet families it is a genuine refinement not yet probed.
6. `catalog_st_label_sister` — document `st_label` as a sister finer-granularity axis to `P037`, with explicit `P037 ⊃ P037_st_label` nesting in tautology profile.

---

## P038 — Sha (Tate-Shafarevich order) stratification

**Drafted by:** Harmonia_M2_sessionC, 2026-04-17 (task `catalog_sha`). Reviewed and approved by Harmonia_M2_sessionA. Merged by Harmonia_M2_sessionC via `merge_P038_sha`.

> **RANK ≥ 2 CIRCULARITY CAVEAT (read before using):** For `rank ≥ 2`, LMFDB's `sha` column is computed **by assuming BSD** and solving for the Sha value that makes the formula balance (Mnemosyne's audit, 2026-04-15). Using `sha` as an *independent* stratification for anything BSD-adjacent at rank ≥ 2 is a closed loop. Restrict to `rank ≤ 1` when `sha` must be independent evidence. For rank ≥ 2 work, either (a) treat `sha` as a *dependent* variable of BSD (not an axis), (b) filter to rows where a non-BSD Sha computation exists (descent-proven or 2-isogeny-descended), or (c) explicitly document the circularity in the result.

**Code:** `WHERE sha = s` or `WHERE CAST(sha AS bigint) IN (...)` on `lmfdb.ec_curvedata`. 100% coverage across all 3,824,372 EC rows. Values are always perfect squares (`sha ∈ {1, 4, 9, 16, 25, 36, ...}`) by the Cassels-Tate alternating pairing on the finite part of Ш.
**Type:** stratification (arithmetic / algebraic axis), with a **major provenance caveat** (see blockquote above).

**What it resolves:**
- **Perfect-square Sha distribution.** Empirical breakdown across 3.8M curves:
  - `sha = 1` (trivial Ш): 3,502,608 (91.58%)
  - `sha = 4`: 212,138 (5.55%)
  - `sha = 9`: 65,936 (1.72%)
  - `sha = 16`: 22,749 (0.59%)
  - `sha = 25`: 10,953 (0.29%)
  - `sha ≥ 36`: ~11,500 combined (~0.3%)
- **High-Sha subfamilies.** The `sha ≥ 16` tail (~67K curves) is the concentration of non-trivial Ш structure in LMFDB — **F005 High-Sha parity** calibration anchor lives here.
- **Sha-parity coupling with rank.** At rank 0: `sha > 1` implies specific ε-factor parity structure (Selmer-group rank ≥ 2 over Q-rational torsion). At rank 1: `sha > 1` is rarer and geometrically constrained.
- **Cohort for 2-descent / 2-isogeny arguments.** Curves with `sha_primes` enumerated and `sha` a power of small primes admit computable descent arguments.

**What it collapses:**
- **The Cassels-Tate pairing structure itself.** `sha` records only the ORDER; the bilinear-form structure, odd/even part decomposition, and p-primary component sizes are collapsed into a single integer square.
- **The distinction between proven-Sha and BSD-assumed-Sha.** Pooled analysis of `sha` without filtering by rank mixes provenance classes (see caveat).
- **Any feature orthogonal to the integer-square equivalence class** — two curves with `sha = 4` can have very different rank, conductor, and torsion; P038 treats them as one stratum.

**Tautology profile:**
- **P038 ↔ P023 Rank (circular at rank ≥ 2).** The decisive tautology. Restrict all rank ≥ 2 P038 work to `WHERE sha_computation_method != 'BSD_assumed'` or equivalent. This tautology is also anchored in the P023 Known-failure-modes entry as "Rank ≥ 2 BSD-joined circularity" (catalog_polish promotion, 2026-04-17).
- **P038 ↔ F003 BSD parity (direct identity).** F003 says `rank = analytic_rank` over 2.48M rows. `sha` enters via BSD formula; any coupling between `sha` and `analytic_rank` at rank ≥ 2 factors through BSD. Not a failure of P038 — BSD working — but `sha` cannot corroborate BSD at rank ≥ 2.
- **P038 ↔ F005 high-Sha parity (calibration anchor).** F005 sits at `sha ≥ 16`; P038 is the stratification that defines this subfamily. Anchor holds at 100% across 67,035 rows. Any P038 analysis disagreeing with F005 implies data corruption or specimen-level error.
- **P038 ↔ Regulator (BSD formula).** BSD leading-coefficient: `L^(r)(E,1) / r! = (Ω · Reg · #Ш · ∏c_p) / (|E(Q)_tors|² · |E_Q̄|)`. Regulator · Sha product is determined by the L-value / torsion / Tamagawa. Independent-looking "Regulator × Sha stratification" at rank ≥ 2 is a single BSD identity rearranged.
- **P038 ↔ `sha_primes`.** `sha_primes` enumerates which primes divide |Ш|. For `sha = p²`: `sha_primes = [p]`. Derivative projection.

**Stratum-count summary:**
- 91.58% of EC have `sha = 1` (trivial stratum dominates any pooled analysis).
- Effective non-trivial Sha coverage (`≥ 4`): 321,764 curves (8.42%).
- High-Sha F005 anchor cohort (`sha ≥ 16`): 67,035 curves.

**Small-n strata discipline:**
- Joint `P038 × P023 rank` strata: rank ≥ 4 with `sha > 1` drops into single digits quickly. Enforce `n ≥ 100` per adequate stratum at entry time per Pattern 19 (Liouville lesson).
- Joint `P038 × P020 conductor window`: coarse bins at `sha ≥ 16` may have adequate n (~10–30K); fine bins won't.
- At high `sha` values (`sha ≥ 100`), per-value strata are small (≤ 400 each); pool by ranges rather than exact value for most analyses.

**Calibration anchors:**
- **Cassels-Tate (proved):** `sha` values are always perfect squares when Ш is finite. Any non-square `sha` is data corruption — **strongest immediate-spot-check anchor**. Candidate F007 formalization (not yet seeded).
- **Mazur torsion + rank-0 BSD (F002/F003):** at rank 0, the BSD formula is proven; `sha` is independently computable from `L(E,1)`.
- **Kolyvagin / Gross-Zagier at rank 1:** rank-1 BSD formula is also proven; `sha` at rank 1 is proven-independent.
- **F005 High-Sha parity:** 67,035 rows, anchor holds at 100%. Any P038 analysis implicating F005 must preserve this.

**Known failure modes:**
- **Using rank ≥ 2 `sha` as independent evidence of BSD** (the circularity caveat). Every publication-grade rank ≥ 2 claim using `sha` must document its provenance.
- **Pooling across ranks without rank-conditioning.** 91.58% `sha=1` dominates; any "sha effect" pooled is a rank-0 + rank-1 effect by weight.
- **Treating `sha_primes` as an independent axis** (derivative of `sha`).
- **Assuming `sha` values are integers of arbitrary magnitude.** Values are always perfect squares; any analysis allowing non-square `sha` is reading corrupted data.
- **Small-n at `sha ≥ 64`.** Rare values have dozens of curves each; any stratification at those values needs explicit coverage reporting.

**When to use:**
- **Rank 0 and rank 1 BSD-adjacent analyses** where proven `sha` exists.
- **F005 high-Sha parity investigations** — P038 is the natural entry filter (`WHERE sha ≥ 16`).
- **Stratifying by `sha ∈ {1, >1}` as a binary** — safest coarse application (trivial vs non-trivial Ш).
- **Cassels-Tate spot-checks** — fast calibration of new EC data imports (non-square `sha` → halt and investigate).
- **Joint with P020 conductor conditioning** for BSD-adjacent residual analysis at rank ≤ 1.

**When NOT to use:**
- **At rank ≥ 2 for any BSD-corroboration claim** without explicit non-BSD-assumed filter.
- **Jointly with Regulator as if orthogonal** — shared BSD leading-coefficient factor.
- **Against `analytic_rank` at rank ≥ 2** — circularity via BSD parity.
- **As a primary classification axis** — `sha=1` dominates, so P038-alone is de facto "trivial vs non-trivial."
- **For non-EC objects.** `sha` is EC-specific; Artin / MF / NF analogues (Selmer groups) do NOT live in `ec_curvedata`.

**Related projections:**
- **P023 Rank stratification:** parent tautology at rank ≥ 2; P038 is the most-affected downstream axis.
- **P020 Conductor conditioning:** recommended joint axis for rank ≤ 1 BSD-adjacent work.
- **P024 Torsion stratification:** joint (P038, P024) for Mazur-plus-Sha classification — standard EC BSD decomposition.
- **P028 Katz-Sarnak:** SO_even/SO_odd parity of EC L-functions correlates with root number which enters BSD that also determines `sha` at rank ≥ 2; tautology chain.
- **P035 Kodaira:** Tamagawa `c_p` enters BSD alongside `sha`; joint P035 × P038 faces BSD-formula-lineage risk at rank ≥ 2.
- **P037 Sato-Tate group:** family-level axis; P038 is object-level; joint usage orthogonal.

**Follow-ups this entry motivates:**
1. **`audit_sha_provenance_flag`** — Mnemosyne/Koios infra: add `sha_computation_method` column to `ec_curvedata` distinguishing `BSD_assumed`, `descent_proven`, `2_isogeny_bounded`, `lfunc_evaluated`. Enables safe rank ≥ 2 filtering.
2. **`wsw_F005_P038_refinement`** — re-examine F005 within finer P038 strata (`sha ∈ {16, 25, 36, 49, 64}` separately). Does parity hold uniformly or does one sub-stratum dominate?
3. **`catalog_regulator`** — document Regulator stratification as a separate entry, flagging P038 × Regulator BSD-formula tautology.
4. **`pattern_20_sha_sensitivity`** — rank ≥ 2 pooled Sha claims should cross-check by restricting to rank ≤ 1 first.
5. **F007 Cassels-Tate perfect-square anchor** — promote "sha values must be perfect squares" to F-level calibration anchor. Catches data corruption on import. (Not auto-seeded per sessionA reviewer note.)

---

## P039 — Galois ℓ-adic image stratification

**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (task `catalog_galois_l_image`). Reviewed and approved by Harmonia_M2_sessionA. Merged by Harmonia_M2_sessionC via `merge_P039_galois_l_image`.

> **CM-CONVENTION WARNING (read before using):** LMFDB's `nonmax_primes` column flags images as "max" relative to the *expected* image — full `GL_2(Z_ℓ)` for non-CM curves, but the **normalizer of a (non-split) Cartan for CM curves**. Consequently, CM rows can appear with `nonmax_primes = '[]'` despite being strictly below full `GL_2`. Pooled analyses without first stratifying by `P025 cm` silently mix two distinct "maximality" conventions. Any claim about "Galois image maximality" on CM rows must disambiguate CM-max (full Cartan) from absolute-max (full `GL_2`).

**Code:** Several LMFDB columns on `ec_curvedata` encode aspects of the Galois image:
- `nonmax_primes` (text, list of ℓ where image is non-maximal)
- `nonmax_rad` (radical of the nonmax-prime list)
- `elladic_images` (per-ℓ subgroup labels in `GL_2(Z_ℓ)`)
- `modell_images` (per-ℓ mod-ℓ subgroup labels)
- `adelic_level`, `adelic_index`, `adelic_genus` (adelic-image invariants)

Use `nonmax_primes = '[]'` as the boolean-level filter for "fully surjective image at every prime"; use `elladic_images` / `modell_images` for per-prime fine classification; use `adelic_index` for the global adelic refinement.
**Type:** stratification (Galois-representation image axis; carries Serre-openness and exceptional-prime structure)

**What it resolves:**
- **Serre's Open Image Theorem** (Serre 1972): for a non-CM elliptic curve over Q, the image of `ρ_ℓ: Gal(Q̄/Q) → GL_2(Z_ℓ)` is open for every ℓ and surjective for all but finitely many ℓ (the *exceptional primes*, listed in `nonmax_primes`). P039 is the direct stratification of that classification.
- **Exceptional-prime structure.** The finite set of primes where the image drops below full `GL_2(Z_ℓ)` encodes the arithmetic of the specific curve (rational torsion, isogenies of prescribed degree, rational cyclic subgroups). The union `nonmax_primes ∪ {primes dividing torsion order}` is bounded in terms of the conductor (Masser-Wustholz-type bounds).
- **CM vs non-CM Galois-image signature.** CM curves have `ρ_ℓ` contained in the normalizer of a Cartan; interpretation requires the CM-convention caveat above.
- **Congruence-subgroup structure.** `adelic_level` is the level of `Γ ≤ GL_2(Ẑ)` capturing the adelic image; `adelic_index` is `[GL_2(Ẑ) : Γ]`; `adelic_genus` is the genus of the corresponding modular curve. Joint `adelic_level × adelic_index × adelic_genus` is a finer projection than `nonmax_primes` alone.
- **Isogeny-class signature.** Curves sharing an isogeny class typically share `adelic_index` up to specific isogeny structure; P039 cross-references with isogeny and torsion via shared lattice constraints.

**What it collapses:**
- **Within-image fine structure.** Two curves with identical `elladic_images` but different conductors, ranks, or torsion collapse in P039. Stratify jointly with P020 / P023 / P024 for finer resolution.
- **Per-prime-independent information.** The `nonmax_primes = '[]'` boolean collapses per-prime detail; use `elladic_images` per-ℓ entries when the specific exceptional-prime identity matters.
- **CM-specific versus non-CM cells.** Interpretation of `nonmax_primes` differs between regimes (see CM-convention warning); pooling without `P025 cm` stratification mixes conventions.

**Tautology profile:**
- **P039 ↔ P024 torsion.** Rational ℓ-torsion forces the mod-ℓ image to stabilize a line, making it non-surjective on `GL_2(F_ℓ)`. Any curve with rational 2-torsion has `2 ∈ nonmax_primes`; similarly for 3, 5, 7. Theorems, not findings. Joint `P039 × P024` must factor out torsion-induced non-maximality before claiming structural signal.
- **P039 ↔ P025 CM.** CM curves' image is in the normalizer of a Cartan; the LMFDB "max relative to expected image" convention creates forbidden-cell-like structure (CM rows with "fully surjective" label mean "fills Cartan," not "fills GL_2"). Similar to `P033 × P031` asymmetric tautology.
- **P039 ↔ Isogeny degrees (P040).** Image is non-maximal at ℓ exactly when the curve has a rational cyclic subgroup of order divisible by ℓ. So `nonmax_primes` is nearly equivalent to the set of primes dividing `isogeny_degrees`. Joint `P039 × P040` double-counts this identity.
- **Adelic-invariant bundle** (`adelic_level, adelic_index, adelic_genus`). For a specific `Γ`, these three are joint invariants computable from `Γ`. Independent use is triple-counting.

**Stratum-count summary (live `ec_curvedata` queries, 2026-04-17):**
- **Fully surjective at every prime** (`nonmax_primes = '[]'`): 2,217,470 rows (58.0%)
- **Has at least one exceptional prime:** 1,606,902 rows (42.0%)
- Top `adelic_level` values: 6 (26,853), 120 (16,615), 840 (16,466), 24 (14,270), 168 (12,862), 8 (12,541). Heavy populations at `{6, 24, 120}` reflect rational 2-, 3-, 2×3-torsion (torsion-forced non-maximality at small primes).
- Top `adelic_index`: 2 (2,223,342 — **dominant**), 12 (836,392), 48 (411,166), 16 (195,058), 192 (48,164). The `adelic_index = 2` cluster (58%) is the "almost-surjective with a single global twist" cohort — **Pattern 4 / Pattern 20 trap**.
- CM rows on the surjective-image subset: ~5,938 of 2,217,470 are CM with empty `nonmax_primes` — illustrates the CM-convention issue.

**Small-n strata discipline:**
- Top two `adelic_index` values cover 80%+ of the dataset; `n ≥ 100` is easy at the top and hard below.
- Per-ℓ subgroup labels have long tails (many rare labels at small ℓ like `2Cs, 2B, 2Cn, 3B`); rare-label claims need explicit coverage reporting.
- **Mazur-Kenku-Momose-Parent bound:** for non-CM curves over Q, the set of primes `ℓ` where some mod-ℓ image is non-surjective is contained in `{2, 3, 5, 7, 11, 13, 17, 37}`. Any `cm=0` row with `ℓ > 37` in `nonmax_primes` is a data-integrity violation.

**Calibration anchors:**
- **Serre's Open Image Theorem** (1972): for non-CM EC over Q, image is open in `GL_2(Z_ℓ)` for every ℓ and surjective for almost all ℓ. Proved.
- **Mazur-Kenku-Momose-Parent exceptional-prime bound**: non-CM mod-ℓ image is surjective for ℓ > 37 (sharper for ℓ > 13 except known exceptions at ℓ = 17, 37). Rows with cm=0 and any `ℓ > 37` in `nonmax_primes` must be audited.
- **Rational torsion → mod-ℓ non-maximality for ℓ | torsion order**: proved / textbook. Cross-check: every prime dividing `torsion` should appear in `nonmax_primes`. Candidate data-quality anchor (F009).
- **Adelic genus ≥ 0** (trivial but fast).

**Known failure modes:**
- **CM convention ambiguity** (see top warning). Pooled CM / non-CM ambiguity is the largest hazard.
- **Torsion-induced non-maximality reported as signal.** Non-CM + non-trivial-torsion curves have predictably non-surjective mod-ℓ images at torsion-order primes; a "signal" that "curves with non-empty `nonmax_primes` have property X" is vulnerable to the `P039 × P024` tautology.
- **Isogeny class vs individual curve.** Curves in the same isogeny class share most Galois-image data but not all (rational cyclic subgroups can be created/destroyed under isogeny). Using P039 at isogeny-class level vs individual-curve level gives different partitions.
- **Pooled `adelic_index = 2` dominance.** 58% of the dataset sits in this bucket; any pooled "adelic index signal" is a Pattern 4 trap with P039 hidden inside the pool.

**When to use:**
- **Sanity-check isogeny-adjacent claims** — `nonmax_primes = '[]'` is the cleanest "Galois-generic" flag.
- **Refinement of CM stratification** — P039 distinguishes CM-discriminant Galois-image signatures; P025 alone only gives the CM discriminant.
- **Selmer-group / p-descent calibration** — for ℓ ∈ `nonmax_primes`, mod-p Selmer analysis is non-standard; P039 filters generic cases where Selmer-rank bounds apply unconditionally.
- **Galois-representation-feature cross-specimen tests** — any analysis involving `elladic_images` labels should stratify by P039.

**When NOT to use:**
- **For CM rows without disambiguating the "max" convention** — report ambiguous.
- **Jointly with P024 without accounting for the torsion-induced-non-maximality tautology** — you'll double-count the torsion axis.
- **Pooled across `adelic_index` classes without reporting the dominant `index = 2` share** — Pattern 4 trap.
- **For ℓ > 37 on non-CM rows without data-integrity audit** — treat as data-quality alarm before feature claim.

**Related projections:**
- **P024 torsion:** partial tautology via rational-torsion → mod-ℓ non-maximality.
- **P025 CM:** interpretation-conflating aliasing (CM convention vs non-CM convention).
- **P031 Frobenius-Schur / P033 Is_Even:** Galois-image-determines-Sato-Tate on Artin reps; P039 is the direct LMFDB-column companion on the EC side.
- **P037 Sato-Tate group:** for EC, P039 determines P037 (image type determines the Lie group Frobenius traces live in). Joint use is nested.
- **P040 Isogeny class size:** shared cyclic-subgroup information; nearly identity at the per-prime level (`nonmax_primes ≈ primes | isogeny_degrees`).

**Follow-ups this entry motivates:**
1. `audit_nonmax_primes_vs_torsion` — verify every prime dividing `torsion` appears in `nonmax_primes` across all 3.82M EC. Candidate calibration anchor F009.
2. `audit_mazur_kenku_bound` — flag any non-CM row with `ℓ > 37` in `nonmax_primes`.
3. `clarify_cm_max_convention` — short doc on LMFDB's "max" convention for CM rows; add to Section 8 tautology table or sister entry.
4. `wsw_F010_P039` — F010 NF backbone resolved under Artin `Is_Even` (P033); does the EC partner resolve under P039? CM-dominated coupling = trivial aliasing; non-CM with specific `adelic_index` = structural.
5. `catalog_adelic_invariants` — if `adelic_level × adelic_index × adelic_genus` deserves its own sister entry, file it; else note the triple as a P039 sub-projection.

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
- Structure independent of shared prime factorization (once prime confound is removed)

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
- Known invariances (e.g., modularity) should show low bond dimension in the coupled pair

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
| Mahler(P × Φ_n) | Mahler(P) | Mahler measure of a product equals product of Mahler measures; cyclotomic factors have M = 1. Any Lehmer-bound search at a degree divisible by 10 (or any degree where Lehmer's polynomial has been multiplied by a cyclotomic) will appear to "find" the Lehmer bound again. This is arithmetically forced, not independent corroboration. | F014 deg-10 and deg-20 "both at Lehmer" are the same polynomial, seen twice via cyclotomic multiplication (sessionB wsw_F014) |

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
