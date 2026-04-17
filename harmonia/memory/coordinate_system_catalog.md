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
