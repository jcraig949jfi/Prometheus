# Methodology Toolkit — Cross-Disciplinary Projections

**Status:** catalog, v1.0 (2026-04-20)
**Purpose:** shelf of methodological tools — information-theoretic, physical,
statistical — that have been proposed as Prometheus projections. When a
live specimen stalls under the existing arithmetic-projection catalog,
check here *before* inventing new infrastructure. Each entry is a
paste-ready specification that can become a symbol promotion, a new
projection, a sweep, or a generator.

**Why this file exists.** The cheapest way to find mathematical universals
humans haven't named is to port vocabulary from somewhere that isn't
mathematics. A projection that knows nothing about number theory — purely
about compression, information, or flow — is a projection that can, by
construction, apply to any domain we add later. That's substrate growth,
not a one-shot finding.

**North-star caveat.** Novelty is the reward; watch for reward-signal
capture. Every tool below is attractive because it promises a coordinate
system nobody else has tried. Apply each one against known calibration
anchors *before* treating its verdict on frontier specimens as evidence.
A tool that disagrees with F001–F005 under its own lens is miscalibrated,
not insightful.

---

## Tool shelf (six entries, extensible)

### 1. `KOLMOGOROV_HAT@v1` — fingerprint compressibility

- **Frame:** Kolmogorov complexity (CS). K(x) = length of the shortest
  program that outputs x. Uncomputable in general; `zstd` / `gzip` /
  Lempel-Ziv give a coarse upper-bound proxy.
- **Scorer:** for each object, canonicalize a fingerprint (a_p sequence
  for EC, zero list for L-functions, coefficient vector for polynomials);
  serialize to bytes under a pinned encoding; compress; record
  `K̂ = len(compressed) / len(raw)`.
- **Resolves:** domain-agnostic regularity. Objects with hidden algebraic
  structure compress; generic objects don't. K̂ is blind to arithmetic
  semantics — if F-IDs cluster in K̂-space differently from how they
  cluster under arithmetic stratification, K̂ has found an axis the
  internal catalog has no name for.
- **Effort:** ½ tick (cheapest thing on the shelf).
- **Status:** in scope for `gen_09_cross_disciplinary_transplants` v1.0
  (spec shipped 2026-04-20, commit `d9bb706b`, seeded at priority -1.6).
- **Composes with:** gen_03 (cross-domain transfer inherits the compressor
  when a new domain lands), gen_06 Pattern 30 sweep (a K̂ correlation
  needs its own lineage check: K̂ of `log L` vs K̂ of `log cond` may share
  algebra), null-family (K̂ of a permutation-null baseline is a bona-fide
  null for K̂ claims).
- **First test:** does F011's rank-0 residual concentrate in the low-K̂
  tail? Either answer is terrain data.

### 2. `CRITICAL_EXPONENT@v1` — scaling-law extraction

- **Frame:** statistical-mechanics universality. At critical points,
  systems with radically different microscopic rules share the same
  scaling exponents. Equivalence classes of exponents = universality
  classes.
- **Scorer:** for each F-ID, fit `f(N) = f_∞ + C · N^{-α}` against
  stratified-by-conductor-decile measurements; record (α, σ_α, f_∞, σ_∞).
  Pinned fit protocol (log-linear OLS with bootstrap CI; α-prior
  optional to avoid Pattern 25 under-constraint).
- **Resolves:** equivalence classes *across* F-IDs. F011 has α ≈ 0.49
  buried in its decay ansatz; F015 has per-k exponents; F041a has the
  nbp-slope ladder. Several specimens carry implicit exponents nobody's
  extracted systematically. Two F-IDs with matching α are in the same
  arithmetic universality class — a structural relation the current
  tensor has no cell for.
- **Effort:** 1 tick.
- **Status:** in scope for `gen_09_cross_disciplinary_transplants` v1.0.
- **Composes with:** Pattern 25 DRAFT (α-prior addresses under-
  constrained-fit concern at the tool level), gen_02 null-family
  (α distribution under NULL_PLAIN vs NULL_BSWCD tests whether α is
  a real exponent or a sample-size artifact).
- **Pattern 30 note:** exponent-matching between F-IDs that share
  definitional terms (e.g., both contain log(N) in a denominator) is
  partially forced. Check `algebraic_lineage` before treating α-match
  as universal evidence.

### 3. `CHANNEL_CAPACITY@v1` — bits-per-object per projection

- **Frame:** Shannon information theory. For a projection P viewed as a
  channel with object-identity X → verdict-under-P as Y, the mutual
  information `I(X; Y)` quantifies how much of X's identity survives P.
- **Scorer:** for each P, compute `MI(object_features; verdict_P)` over
  a pinned dataset using 16-bin equal-quantile binning on each side;
  subtract small-sample bias (Panzeri-Treves). Report bits and a
  per-stratum breakdown.
- **Resolves:** projection-quality audit, quantified. Currently the
  claim "P020 and P023 are principal axes" is prose (and the last
  external review correctly flagged it as selection-biased). Channel
  capacity replaces prose with bits, and surfaces projections the
  catalog has underused.
- **Effort:** 1–2 ticks (binning discipline is the subtle part).
- **Status:** in scope for `gen_09_cross_disciplinary_transplants` v1.0.
- **Composes with:** gen_01 Map-Elites (use channel capacity as the
  quality-score axis for behavior-cell coverage), gen_10 composition
  enumeration (score composed operators by the bit-gain over their
  components).
- **Discipline:** channel capacity requires careful binning to avoid
  overfitting MI estimators. A capacity claim without a bin-count
  sensitivity sweep is a Pattern 17 (missing schema) symptom.

### 4. `MDL_SCORER@v1` — principled model ranking

- **Frame:** minimum description length (Rissanen). The best model is
  the one that minimizes `bits(model) + bits(data | model)` — a total-
  description-length principle that penalizes overfitting structurally.
- **Scorer:** given an F-ID with N candidate mechanisms (ansatze,
  functional forms), compute total code length per candidate using
  a normalized-ML or BIC/AIC surrogate as appropriate; rank ascending.
- **Resolves:** model comparison as a first-class operation. Pattern 25
  (under-constrained fit) currently flags this in prose; MDL makes the
  ranking versioned and reproducible. F011's three competing ε₀ ansatze
  (22.9% classical 1/log(N) / 31.1% power-law / 35.8% 1/log²) get an
  ordered verdict instead of three plausible numbers.
- **Effort:** 1–2 ticks once per-F-ID candidate-model sets are
  formalized. Formalization is the blocking step.
- **Status:** Tier 2 deferred in gen_09 v1.0. Paste-ready extraction
  when MDL-first sessions claim.
- **Composes with:** gen_10 composition enumeration (MDL is the scoring
  function for enumerated compositions), gen_06 Pattern 30 sweep
  (a Level-3 rearrangement is zero data-bits — maximal compression —
  so MDL scores it as trivially-best-explanation, which is exactly
  the correct automated flag for "this correlation is definitional").

### 5. `RG_FLOW@v1` — trajectories, not just endpoints

- **Frame:** renormalization group. Iteratively coarse-grain a system
  and track how its parameters flow. Fixed points of the flow = universality
  classes. Bifurcations = phase transitions.
- **Scorer:** for each F-ID, measure the parameter of interest at each
  conductor decile 1..10 (coarse-graining proxy in arithmetic); fit a
  flow equation `dp/dl = β(p)`; record fixed points, flow dimension,
  and any bifurcation thresholds.
- **Resolves:** trajectories are structure we don't currently record.
  The tensor records end-states — "F011 has ε₀ ≈ 22.9% asymptotically."
  RG records "ε starts at 45.37% at decile 1 and flows to 22.9% with
  slope −7.17 per log-decade." Two F-IDs with the same fixed point but
  different trajectories are in the same universality class yet took
  different routes. Bifurcations would reveal conductor-threshold
  phase transitions in the arithmetic landscape.
- **Effort:** 2 ticks. Stratified-per-decile measurement mostly exists;
  the missing pieces are trajectory bookkeeping and flow-equation fits.
- **Status:** Tier 2 deferred in gen_09 v1.0.
- **Composes with:** `CRITICAL_EXPONENT@v1` (α is the fixed-point
  behavior near criticality), gen_02 null-family (each trajectory
  point can be family-tested for statistical significance).

### 6. `FREE_ENERGY@v1` — temperature-parameterized model mixture

- **Frame:** variational free energy (ML / stat mech). `F = U − TS`:
  fit penalty minus complexity reward, balanced by temperature.
- **Scorer:** for an F-ID with N candidate mechanisms, compute the
  free energy as a function of temperature; find the critical T at
  which one mechanism dominates the mixture.
- **Resolves:** decisiveness of evidence. When MDL ranks three ansatze
  within ε of each other, free energy quantifies how strongly any one
  dominates across temperature regimes. Useful at N ≥ 5 candidates.
- **Effort:** Tier 2+. Build MDL first; revisit when N ≥ 5 candidates
  per F-ID is common.
- **Status:** deferred pending MDL.
- **Composes with:** MDL_SCORER (generalization), gen_10 composition
  enumeration (enumerated compositions as the candidate mixture).

### 7. `GINI_COEFFICIENT@v1` — distribution inequality

- **Frame:** Economics (Corrado Gini, 1912). Measures inequality / concentration of a
  distribution; widely used in income economics. Ratio of the area between
  the Lorenz curve and the equality line to the total area under the
  equality line.
- **Scorer:** for any non-negative real-valued distribution (list of values
  OR a value-count dict), compute
  `Gini = (sum_{i,j} n_i n_j |v_i - v_j|) / (2 N² mean)`.
  ~10 lines of Python; sorted-cumulative-sum analytic form is faster than
  the naive double-sum at >10K rows.
- **Resolves:** distribution-inequality measurement on any non-negative
  real-valued list. Distinct from CHANNEL_CAPACITY (Shannon mutual-information
  on object-projection pairs; not inequality of a single distribution) and
  from KOLMOGOROV_HAT (compressibility of the object's raw fingerprint, not
  inequality of a derived statistic). Useful when the question is "how
  concentrated is X across the population?" Range [0, 1] where 0 = perfectly
  equal, 1 = maximally unequal.
- **Effort:** TRIVIAL (per gpt-4o-mini scorer-tractability probe 2026-04-23,
  cartography/docs/probe_gemini_scorer_tractability_results.md). One of the
  smallest scorers on this shelf.
- **Status:** v1 candidate (this entry, Harmonia_M2_auditor 2026-04-23).
- **Calibration anchors (auditor 2026-04-23):** three measurements on
  rank-0 EC (n=1,404,510 across LMFDB):
  1. Gini on `class_size` distribution = **0.295** (Mazur-bounded support
     {1,2,3,4,6,8}; mean 1.79; 53% at cs=1, 33% at cs=2). Reference frame:
     0.30 ≈ Scandinavian-income-distribution inequality.
  2. Gini on `sha` distribution = **0.564** (mean 2.67; max 5625; 79.6% have
     sha=1; heavy tail). Reference frame: 0.56 ≈ low-income-country inequality.
     **Side observation:** 100% of the 1,404,510 curves have sha = perfect
     square — validates the BSD prediction (sha is conjecturally a perfect
     square integer) at full LMFDB rank-0 sample.
  3. Gini on `sqrt(sha)` distribution = **0.221** (mean 1.35; sqrt-transform
     compresses the tail). Useful when comparing rank cohorts via Sha-
     rank-Mordell-Weil parity arguments.
  These three anchors span moderate-to-high inequality with the same dataset;
  any future GINI measurement on Prometheus arithmetic data can be compared.
  **Discipline:** descriptive Gini (this kind of measurement) is fine;
  inferential Gini (correlation with conductor or another BSD ingredient)
  requires Pattern-30 audit first.
- **Composes with:** PATTERN_30 (mandatory before any Gini-based correlation
  claim — see F043 lesson; Tamagawa products and Sha distributions are
  BSD-ingredients and can produce algebraically-induced "inequality"),
  CRITICAL_EXPONENT (Gini-as-a-function-of-conductor-decade is a candidate
  scaling), CHANNEL_CAPACITY (Gini and MI capture different structure on
  the same data — disagreement between them is informative).
- **First production targets** (none yet measured beyond the calibration anchor):
  (a) Sha distribution across rank-0 cohort — Sha is heavy-tailed; Gini
  expected ≫ 0.5; any structure that compresses the inequality is a
  candidate signal.
  (b) Tamagawa product distribution across rank-2 cohort — **REQUIRES**
  Pattern-30 BSD-tautology audit before any inferential use; Tamagawa is
  in the BSD-ingredient family.
  (c) Number-field discriminant distribution across degree-d strata —
  calibration target since the distribution is well-studied.

### 8. `CONTROLLABILITY_RANK@v1` — dynamic agency under linear dynamics

- **Frame:** Control theory (Kalman, 1960). A linear system `ẋ = Ax + Bu`
  is *controllable* iff the controllability matrix
  `[B | AB | A²B | ... | A^(n-1)B]` has full row rank `n` — i.e., the
  inputs `u` can steer the state vector `x` to any direction in
  n-dimensional space.
- **Scorer:** given `(A ∈ ℝ^(n×n), B ∈ ℝ^(n×m))`, compute
  `rank(np.hstack([B, A@B, (A@A)@B, ..., np.linalg.matrix_power(A, n-1)@B]))`
  via SVD-based rank with explicit `rcond` tolerance. Output: integer in
  `[0, n]`. Report both the rank and the ratio `σ_k / σ_1` (the smallest
  retained singular value over the largest) as a condition-number proxy.
  ~30 LOC once `(A, B)` are specified.
- **Resolves:** **dynamic agency** — degrees of freedom an input
  operator can influence in a state space evolving under a linear
  dynamics operator. Distinct from CHANNEL_CAPACITY (static MI between
  object and verdict), KOLMOGOROV_HAT (compressibility of a single
  fingerprint), CRITICAL_EXPONENT (scaling of a single quantity). Reads
  *temporal / iterative* structure rather than static structure — a
  genuinely new axis class for the shelf.
- **Effort:** TRIVIAL (per gpt-4o-mini tractability probe 2026-04-23,
  `probe_gemini_scorer_tractability_results.md`, FEASIBILITY=EASY;
  `numpy.linalg.matrix_rank` does the work once `(A, B)` are pinned).
- **Status:** v1 candidate (this entry, Harmonia_M2_sessionA 2026-04-23,
  per axis-4 shelf decision on 3 STRONG lens candidates — see
  `agora:harmonia_sync` DECISION entry). Self-drafted; NETWORK_MODULARITY
  delegated to auditor (MODERATE effort, auditor offered);
  CLADISTIC_PARSIMONY deferred pending arithmetic-phylogeny mapping.
- **Candidate (A, B) pairs on arithmetic data:**
  1. **Hecke controllability of modular forms** (calibration-first).
     `A` = matrix of first-m Hecke operators `T_p` acting on
     `S_k(Γ_0(N))`; `B` = identity on span of the first few `a_p`.
     Rank quantifies: "how many independent cusp-form directions are
     reachable from low-prime Hecke input?" Calibration target: rank
     should equal `dim(S_k(Γ_0(N)))` for small `(k, N)` — reproduces
     the Hecke-ring faithfulness theorem. Non-trivial deviation is
     instrument error, not a finding.
  2. **Isogeny controllability** (first novel target). `A` = isogeny-
     graph adjacency matrix on rank-0 EC at bounded conductor;
     `B` = indicator column on CM seeds. Rank probes: "how many
     isogeny classes are reachable from a CM-seed subset under
     iterated isogeny?" Rank ≪ cohort size → fragmented; rank ≈
     cohort size → well-connected. No existing shelf tool reports
     this quantity.
  3. **Zero-dynamics controllability.** `A` = coefficient-recurrence
     matrix built from consecutive differences of `γ_i` (L-function
     zero heights, stacked); `B` = conductor-perturbation column.
     Rank probes whether conductor variation injects structure into
     the zero distribution — natural compound with F011's rank-0
     residual.
- **Composes with:** FREE_ENERGY (controllability across mixture-
  temperature — how agency varies with decisiveness regime),
  CHANNEL_CAPACITY (input→state MI vs rank on the same `(A, B)` —
  disagreement is informative), RG_FLOW (how controllability flows
  under coarse-graining; candidate fixed point = structurally stable
  rank deficit), PATTERN_30 (matrices may be algebraically coupled —
  see hazards).
- **Pattern 30 / frame-hazard notes:**
  1. **Definition-forcing hazard.** If `A` is defined in terms of the
     same atomic quantities as the columns of `B`, rank is partially
     forced. Example: if `A` encodes a linear recurrence in `a_p` and
     `B` seeds from the first few `a_p`, the controllability rank
     equals the recurrence order by construction, not by arithmetic
     structure. Run PATTERN_30 lineage check on the
     `(A-definition, B-definition)` pair before promoting any
     controllability-dependent claim.
  2. **Numerical-rank discipline.** Use SVD rank with explicit
     `rcond`; report both the rank and `σ_k / σ_1`. A rank-dependent
     claim without explicit tolerance is a Pattern 17 (missing
     schema) symptom.
  3. **BSD-ingredient composition.** On `(A, B)` matrices derived
     from BSD-ingredient-family quantities (Sha, Ω, Reg, ∏c_p, Tor,
     L-value), `PATTERN_BSD_TAUTOLOGY` (`null_protocol_v1.1`) applies
     — the rank statement becomes a Class-5 claim about the identity
     structure, not about arithmetic structure. Pattern 30 skip to
     "write the identity" step before running.
- **Discipline:** descriptive controllability on non-overlapping
  `(A, B)` is fine; inferential claims (controllability correlates
  with another BSD-ingredient, or with a live-specimen verdict)
  require Pattern 30 + PATTERN_BSD_TAUTOLOGY audit first.
- **First production targets** (none measured yet):
  (a) Hecke controllability on a (k=2, N≤100) LMFDB cohort —
      calibration anchor against `dim(S_k(Γ_0(N)))`.
  (b) Isogeny controllability on rank-0 EC bounded conductor —
      first novel measurement.
  (c) Zero-dynamics controllability on F011 rank-0 cohort — probes
      conductor as a controllability axis for first-gap variance
      deficit.
- **Open question:** PATTERN_18 (uniform visibility) says "deficit
  visible through every projection"; full controllability says "state
  reachable from every input direction." These are structurally
  analogous. If the correspondence holds, CONTROLLABILITY_RANK may be
  a quantitative instance of PATTERN_18-adjacent structure, and
  rank-deficit measurements may map to VACUUM candidates. To be
  checked on the first production target.

### 9. `TT_APPROX_MAP@v0` — MAP-Elites archive of tensor-train approximations (CANDIDATE, playground-tier)

- **Frame:** Numerical linear algebra (Oseledets TT) + quality-diversity
  evolutionary search (Mouret-Clune MAP-Elites). Each individual is a
  (function, TT-approximation) pair; the archive is a grid indexed by
  behavior descriptors populated by evolving TT ranks. The archive IS
  the output, not any single approximation.
- **Scorer:** for a function evaluated as a dense tensor on a grid, run
  TT-SVD at candidate rank tuples; record `(n_params, rel_l2_error)`
  and place in the appropriate MAP-Elites cell. Phase-1 uses 2
  descriptors on a 20×20 grid; Phase-2 extends to 4 descriptors
  (adds spectral decay + Lipschitz).
- **Resolves:** "geometry of approximation" — which function-shapes
  admit which TT compressions, mapped rather than proved. The
  descriptor axes themselves are the coordinate-system-of-legibility
  choice (gen_11-adjacent territory in a non-arithmetic substrate).
- **Effort:** Phase-1 MVP shipped 2026-04-24 (auditor). Phase 2
  (DMRG refinement + spectral/Lipschitz descriptors +
  decomposition-lineage Pattern-30 analog + Lorenz/Gabor/heat-PDE
  frontier): ~3 ticks. Phase 3 (graduation to parallel substrate with
  own F-IDs / P-IDs / symbol promotion / null protocol): weeks.
- **Status:** CANDIDATE, **playground-tier**. Verdicts from `zoo/` do
  NOT migrate to the landscape tensor. Living at `zoo/` (standalone);
  see `zoo/README.md` for discipline contract + phase roadmap.
- **Phase-1 calibration results (2026-04-24):**
  - `prod_x` (TT rank 1 known-truth, 6D grid 12^6): min rel_err
    1.08e-13 at 72 params → PASS.
  - `random_gaussian` (incompressible known-truth, same shape): min
    rel_err 0.997, 7-point Pareto at full-rank ceiling → PASS.
  - `pairwise_tanh(x_1*x_2 + x_3*x_4 + x_5*x_6)` (frontier): 12 cells
    occupied, 11-point Pareto, min rel_err 1.72e-3 at 120 params.
    Meaningful compression exists; awaiting Phase-2 lineage check.
- **Composes with:** `KOLMOGOROV_HAT` (both measure compressibility
  via different lenses; disagreement is informative),
  `CRITICAL_EXPONENT` (error decay vs rank is itself a scaling law
  — fit α per function and feed back), `MDL_SCORER` (MDL ranks
  Pareto-front candidates principledly), `CONTROLLABILITY_RANK`
  (TT rank and Kalman rank are two different "how many degrees of
  freedom does this really have" measures; a cross-substrate joint
  study is a gen_09 target).
- **Pattern 30 note:** Phase-2 `decomposition_lineage` check is the
  TT analog of `algebraic_lineage`. If `f = g + h` with `g` low-rank
  and `h` small-but-important, TT-SVD recovers `g` and reports
  `error ≈ |h|`; two neighboring archive entries `(f, g)` are
  algebraically coupled, not independent measurements. Not yet
  enforced.
- **First frontier targets (deferred to Phase 2):** Lorenz trajectory
  on a time-delay grid, 2D heat-PDE solution at multiple timesteps,
  Gabor wavelet packet. Calibration anchors remain mandatory every
  run.

### 10. `CONJECTURE_GENERATOR@v0` — coordinate-system discovery under algebraic-lineage + MDL-calibration constraints (CANDIDATE)

- **Frame:** Genetic programming + MAP-Elites over a typed algebraic
  grammar with lineage tags, scored by MDL with ideal-quotient pruning,
  calibrated by encoding-perturbation robustness. This is NOT a
  "conjecture generator" in the naive sense; the reframe is load-
  bearing: it is a coordinate-transformation generator constrained so
  Framing-B (P-ID) output cannot silently collapse into Framing-C
  (claim). Architecture doc at [`architecture/conjecture_generator.md`](architecture/conjecture_generator.md) (v0.2 DRAFT, 2026-04-23)
  is the source of truth; this entry is the shelf pointer.
- **Methodological cousin:** `TT_APPROX_MAP@v0` (entry 9) — both are
  MAP-Elites over a discovery space with calibration anchors + a
  Pattern-30 analog. Differences: TT operates on functions via
  TT-SVD ranks; this operates on arithmetic data via an algebraic
  grammar. Cross-substrate study of how the two MAP-Elites archives
  relate is a gen_09 target.
- **Scorer:**
  ```
  input:
    dataset:          pinned dataset symbol (e.g., Q_EC_R0_D5@v1)
    grammar:          (atoms, operators, max_depth, lineage_tags, identity_basis)
                        - atoms drawn from Definition DAG Phase-0 extended seed
                        - each atom carries AXIS_CLASS@v1 + algebraic-closure tags
                        - operators carry lineage-propagation rules
                        - identity_basis = materialized known identities over dataset
    mdl_coefficients: (α, β, γ, δ)  [simplicity, fit, P30, calibration]
    map_axes:         subset of AXIS_CLASS@v1 values defining niche cells
    iteration_budget: int  (GP generations × population)
    seed:             int  (GP RNG)

  output (per candidate past all gates):
    (expression_ast,
     mdl_score,
     pattern_30_level,                  # 0|1 only; ≥2 pre-pruned
     algebraic_dependence_level,        # 0|1 only; ≥2 pre-pruned via R²
     map_cell_or_residual,              # AXIS_CLASS cell OR "residual"
     preserves_declared,                # list[property]
     destroys_declared,                 # list[property]
     signature)                         # full SIGNATURE@v2 JSON

  per-run audit artifacts (required for shelf promotion):
    encoding_perturbation_matrix        # Kendall's τ per operator
    margin_stability_matrix             # margin-ratios per anchor × perturbation
    null_encoding_top_K                 # random-grammar baseline
    out_of_map_fraction                 # residual-channel density
    out_of_map_clusters                 # top-N residual clusters + exemplars
  ```
- **Resolves:** candidate P-IDs (coordinate transformations) discovered
  by search rather than by human proposal. Framing A (claim-form
  output) is a derived artifact, surfaced only when a candidate's
  declared `preserves`/`destroys` imply a measurable invariant that
  passes `null_protocol_v1.1`. Primary output is substrate: new
  scorers, stratifications, feature maps with information-audit
  schemas. Differs from `gen_11` (which proposes axes from tensor
  demand signals like VACUUM / EXHAUSTION) by operating on grammar-
  level GP search over a pinned dataset; the two are complementary
  producers whose merger is a v2 question.
- **Effort:** HIGH — ~7–11 ticks to v1 promotion. Breakdown: 3–5 ticks
  Definition DAG Phase-0 extension (~60–80 nodes covering LMFDB EC +
  BSD-ingredient family with full lineage closure); 2–3 ticks GP +
  MAP-Elites scaffolding (`harmonia/runners/conjecture_gp.py` or at
  `zoo/conjecture_gp/` per playground-tier discipline); 1–2 ticks
  calibration battery including encoding-perturbation tests; 1 tick
  red-team (Tink 2 — deliberate F043 reproduction under disabled
  lineage gate). Most expensive entry on the shelf by ~5×. **Cheap-
  path alternative:** minimal hand-built BSD-only grammar + naive GP
  loop at `zoo/` in ~1 tick; trades infrastructure investment for
  earlier empirical feedback; scope restricted to Tink 1 + Tink 2.
- **Status:** v0 DRAFT candidate (this entry, Harmonia_M2_sessionC +
  James 2026-04-23 / 2026-04-24). Architecture doc v0.2 shipped at
  `architecture/conjecture_generator.md`. Graduation to v1 requires:
  Definition DAG Phase 0 landed, grammar-time P30 + ideal-quotient
  checks shipped in `harmonia/sweeps/pattern_30.py`, Tink 1 PASS
  (anchor rediscovery) AND Tink 2 DEMO (F043 reproduction under
  disabled gate), encoding-perturbation artifacts present, `gen_12`
  spec at `docs/prompts/gen_12_conjecture_generator.md`. Five open
  questions in architecture doc §13 pending James's call; decision-
  pending on target class, grammar atom set, `gen_11` merger, and
  cheap-path-vs-full-path.
- **Composes with:** `gen_11` coordinate-invention (sibling producer;
  merger-vs-sibling is a v2 decision), `MDL_SCORER@v1` (scoring
  backbone), `PATTERN_30@v1` + `PATTERN_BSD_TAUTOLOGY`
  (`null_protocol_v1.1`, grammar gate), `AXIS_CLASS@v1` (niche
  taxonomy — no parallel vocabulary), `VACUUM@v1` (residual-channel
  diagnostic at MAP level), `SHADOWS_ON_WALL@v1` (per-candidate lens
  count), `MULTI_PERSPECTIVE_ATTACK@v1` (Tink 4 cross-grammar
  convergence test), `TT_APPROX_MAP@v0` (methodological cousin;
  cross-substrate MAP-Elites comparison is a gen_09 target),
  Definition DAG (Phase 0 extended seed — **hard prerequisite** for
  full path; cheap-path bypasses via hand-built grammar),
  `SIGNATURE@v2` (extended to carry grammar spec +
  preserves/destroys + audit artifacts).
- **Pattern 30 / frame-hazard / null-protocol considerations:**
  1. **Grammar-time Pattern 30 is mandatory, not optional.** Level ≥ 2
     candidates are pruned before scoring, not after. Grammar encodes
     `algebraic_closure` tags on every atom; lineage propagates
     through operators; Level computed from atom-tag intersection at
     expression-tree construction.
  2. **Ideal-quotient check on top of atom-lineage.** Catches near-
     tautologies the atom-tag gate misses (log-transformed, partial-
     product, mixed-scale). `R² ≥ 0.9` against known-identity basis
     → prune; `R² ∈ [0.6, 0.9)` → advisory flag + MDL penalty. See
     architecture doc §2.1.
  3. **Framing B hard rule (architecture doc §1.1).** Candidates
     asserting invariants (`X = Y`, `X ≤ Y`, `X ~ f(Y)`) are
     type-rejected. Candidates without a declared `preserves` /
     `destroys` schema are type-rejected. Type-enforced, not cultural.
  4. **Residual channel as first-class audit (architecture §5.1).**
     Out-of-MAP fraction + cluster exemplars are required per-run
     artifacts. Empty residual with dense MAP is a WARNING (reward-
     signal capture on declared niches), not a success.
  5. **Encoding-perturbation robustness (architecture §6.1) required
     before novel output.** Ordering invariance under operator-cost
     perturbation, margin-stability test, null-encoding baseline.
     Scorers failing any of the three are measuring syntax preference,
     not structure.
  6. **Class-4 frame hazard.** Calibration dataset is `Q_EC_R0_D5@v1`
     — a curated cohort, not a population-random sample. Candidates
     discovered here carry an implicit
     `sampling_intent: heuristically-sampled` caveat per
     `long_term_architecture.md §2`. Any candidate that passes here
     but fails against an independently-sampled cohort is a Class-4
     construction-biased artifact.
- **Calibration anchors (design-target; none run yet):**
  1. **F003 BSD parity** `(−1)^rank = root_number`. Level 4 IDENTITY.
     Minimal grammar `{rank, root_number, =, ·, ^, (−1)}` at `depth
     ≤ 4` should emerge within first 100 candidates on
     `Q_EC_R0_D5@v1`. **Failure = instrument error.**
  2. **F004 Hasse bound** `|a_p| ≤ 2√p`. Level 4 IDENTITY
     (inequality form). Grammar `{a_p, p, ≤, |·|, √, 2}` at `depth
     ≤ 5`, ordinal × magnitude niche.
  3. **F002 Mazur torsion classification** — torsion-order
     enumeration concentrates in 15 known classes. Categorical niche.
  4. **F008 Scholz reflection ratio** — secondary target; requires
     number-field atoms (deferred to target-class-2 phase).
  5. **F043 reproduction under `lineage_tags=disabled`** (Tink 2
     red-team). `corr(log|Sha|, log(Ω·∏c_p))` should appear in
     top-20 MDL on rank-0 cohort. **Demonstrates gate necessity,
     not a bug.**
- **First production targets** (ordered; gated):
  (a) **Tink 1 — anchor rediscovery.** Minimal 2-atom grammar, F003
      target on `Q_EC_R0_D5@v1`. Pass: anchor in top-100 MDL within
      1000 candidates. ~½ tick once scaffolding exists.
  (b) **Tink 2 — F043 red-team** (post Tink 1 PASS). Demonstrates
      disabling the gate reproduces a known retraction. ~½ tick.
  (c) **Tink 3 — full-grammar empty-niche scan** (gated on Tink 1
      PASS + Tink 2 DEMO). `Q_EC_R0_D5@v1` + full BSD-lineage-tagged
      atoms, K=10000 candidates. Per-niche top candidate + MDL,
      `out_of_map_fraction` + top residual clusters. **First
      substrate-growth output.** No promotion; surfaces candidate
      P-IDs for `gen_11`-style review and residual clusters for
      `AXIS_CLASS` extension. ~1–2 ticks.
  (d) **Tink 4 — cross-grammar convergence** (deferred): two atom
      sets on the same data via `MULTI_PERSPECTIVE_ATTACK@v1`-at-
      grammar-level. Convergence across grammars = `coordinate_invariant`
      candidate; divergence = `map_of_disagreement` terrain.
- **Open questions:**
  1. **Merger with `gen_11`.** Overlapping output (candidate P-IDs);
     different input (tensor demand vs. grammar + data). v0 siblings;
     v2 question is whether one producer can accept demand signal as
     a grammar constraint. Deferred.
  2. **Cheap-path vs full-path first move.** Full v1 requires
     Definition DAG Phase-0 extension (~3–5 ticks). Cheap-path is
     `zoo/`-tier hand-built grammar + naive GP in ~1 tick.
     Architecture doc §13 Q5; James's call.
  3. **Playground-tier home.** Does early tinkering live at `zoo/`
     (parallel substrate, no tensor migration) like `TT_APPROX_MAP`,
     or in mainline under full discipline from day 1? The
     `zoo/`-tier option trades mainline-discipline cost for
     exploratory bandwidth; argues for Tink 1/2 at `zoo/`, Tink 3
     only at mainline once gates are honest.

---

### Auditor note: 4 STRONG candidates → 2 shipped, 1 delegated, 1 deferred (2026-04-23)

The auditor's 2026-04-23 cross-disciplinary lens probe (Gemini-2.5-flash;
`cartography/docs/probe_gemini_lens_candidates_results.md`) surfaced four
STRONG candidates beyond the original six tools: CLADISTIC_PARSIMONY
(evolutionary biology), CONTROLLABILITY_RANK (Kalman, control theory),
GINI_COEFFICIENT (economics), NETWORK_MODULARITY (Newman). Tractability
probe (gpt-4o-mini, 2026-04-23) rated all four implementable: GINI TRIVIAL,
CONTROLLABILITY_RANK EASY, CLADISTIC_PARSIMONY MODERATE (Fitch O(n) for
binary chars), NETWORK_MODULARITY MODERATE (Newman algorithm).

**Axis-4 shelf-ownership decision (sessionA 2026-04-23):**
- **GINI_COEFFICIENT@v1** — shipped as entry 7 (auditor 2026-04-23).
- **CONTROLLABILITY_RANK@v1** — shipped as entry 8 (sessionA 2026-04-23,
  self-drafted; EASY tractability + calibration-first Hecke target).
- **NETWORK_MODULARITY@v1** — accepted for shelf, drafting delegated to
  auditor per 2026-04-23 offer. MODERATE effort (Newman algorithm).
  Distinct from existing tools because it measures community-structure
  quality on a graph — orthogonal to static compression and dynamic
  controllability. First target candidates: isogeny graphs,
  Hecke-eigenvalue correlation networks, Galois-representation
  connectivity.
- **CLADISTIC_PARSIMONY** — DEFERRED (not rejected). Reason: the Fitch
  scorer is cheap, but arithmetic data has no canonical phylogeny. A
  shelf entry requires a pinned tree-source (candidates: isogeny
  graphs reduced to rooted trees; Galois-representation lineage;
  modular-form degeneration trees) AND a concrete feature matrix per
  object. Re-open when a live specimen or a team-proposed arithmetic-
  phylogeny hypothesis supplies both ingredients. Held in the
  Ideas-queue per the "How to add a new tool" template.

---

## How these compose into a single lens

All eight measure different faces of one underlying quantity: *how much
structure is in this arithmetic data under a compression lens?*

- `KOLMOGOROV_HAT` — compressibility of the object's raw fingerprint
- `CRITICAL_EXPONENT` — compressibility of a scaling law
- `CHANNEL_CAPACITY` — compressibility of object-identity under a
  projection
- `MDL_SCORER` — compressibility of the best candidate explanation
- `RG_FLOW` — compressibility of a trajectory (fixed-point description
  vs full history)
- `FREE_ENERGY` — compressibility of a mixture distribution
- `GINI_COEFFICIENT` — compressibility of "concentration" as a
  one-number summary of a distribution (low Gini = compressible-as-uniform;
  high Gini = compressible-as-Pareto-style-tail)
- `CONTROLLABILITY_RANK` — compressibility of *dynamic agency*: a full
  n-dimensional state reachable from m ≪ n inputs is a compression of
  the reachable set; rank-deficit is a compression failure (reachable
  set is a proper subspace)

A good projection *is* one that achieves maximal lossy compression while
retaining the structure we care about. A good F-ID *is* one that has a
short optimal description in some projection. The six tools together
reframe Prometheus as: find the projections and descriptions that
compress the arithmetic data most densely.

This is what the north-star note (`user_prometheus_north_star.md`) points
at: *compressing coordinate systems of legibility, not laws.* The
landscape doesn't come with a preferred coordinate system; we build the
coordinates that make structure legible. The tools here are candidate
coordinate builders.

---

## How to add a new tool

When proposing a seventh entry (or when a live-specimen dead-end suggests
a coordinate system we haven't listed), the template is:

1. **Frame** — which non-mathematical discipline does this come from?
   (physics, CS, stats, ML, neuroscience, linguistics, etc.)
2. **Scorer** — concrete input signature and output shape. If you can't
   write a pseudocode sketch, the tool isn't ready for the shelf.
3. **Resolves** — what does this measure that the current arithmetic-
   projection catalog can't? Be specific about what cell or equivalence
   class or claim the tool makes tractable.
4. **Effort** — ticks, honest. Shelf entries that say "½ tick" but
   would actually take 3 are anti-patterns.
5. **Status** — pending / spec'd / implemented / deprecated.
6. **Composes with** — list the generators, sweeps, or other shelf
   tools this interlocks with.
7. **Pattern 30 / frame-hazard / null-protocol considerations** —
   what epistemic gates apply when this tool produces a verdict?

Entries that fail the scorer sketch or the "resolves" specificity check
are held in a separate Ideas-queue, not promoted to the shelf. The shelf
is for paste-ready; ideas are for half-formed.

---

## Related: multi-perspective attack methodology

`harmonia/memory/methodology_multi_perspective_attack.md` is the
procedural companion to this toolkit. Where this file catalogs
*individual* cross-disciplinary lenses, that file describes how to
deploy ≥ 4 of them *simultaneously* against a single open problem
under committed-stance discipline. Anchor case: Lehmer's conjecture,
2026-04-20 — five threads (dynamical systems, information theory, RG,
adversarial search, mass-gap physics), each with forbidden moves,
produced genuinely differentiated predictions about the same
measurement. The toolkit shelf supplies the disciplinary priors; the
multi-perspective methodology supplies the protocol for using them in
parallel.

---

## Discoverability

The restore protocol (`harmonia/memory/restore_protocol.md`) references
this file at step 9 (geometries + operational footprint). Any cold-start
Harmonia instance reading the restore should check here when:

- The current projection catalog doesn't resolve a live specimen, AND
- The specimen has resisted at least two of Pattern 13's axis-class
  redirections, AND
- A new arithmetic projection would be the Nth of its class.

In that state, reaching for a cross-disciplinary lens (K̂, channel
capacity, critical exponent) is often cheaper than inventing a new
arithmetic coordinate. The tools here are the shelf.

---

## Version history

- **v1.1** — 2026-04-23 — two shelf entries added from the auditor's
  cross-disciplinary lens probe (Gemini 2.5 + gpt-4o-mini tractability
  follow-up): GINI_COEFFICIENT@v1 (auditor-drafted, entry 7) and
  CONTROLLABILITY_RANK@v1 (sessionA-drafted, entry 8). Axis-4 shelf
  ownership decision (sessionA) accepts NETWORK_MODULARITY for
  auditor-led drafting and defers CLADISTIC_PARSIMONY to the
  Ideas-queue pending an arithmetic-phylogeny ingredient. "How these
  compose into a single lens" updated to eight entries. No earlier
  entries modified.
- **v1.0** — 2026-04-20 — initial catalog, six entries, derived from
  James's conductor-framing conversation ("how could we leverage these
  at Prometheus"). First three entries (K̂, critical exponent, channel
  capacity) already scoped into gen_09 v1.0; remaining three (MDL, RG,
  free energy) are paste-ready extractions when claimed.
