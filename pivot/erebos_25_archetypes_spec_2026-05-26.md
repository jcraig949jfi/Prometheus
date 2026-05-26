# Erebos 25-Archetype Hypothesis-Generator Spec v1.0

**Date:** 2026-05-26
**Source:** James Craig directive 2026-05-26 (pasted verbatim into
session; original authorship outside Charon swarm context).
**Status:** Canonical spec for Erebos's generator-plugin registry.
This document is load-bearing -- the plugin implementations must
conform to the Erebos Implementation Spec format for each generator.

**Companion artifacts:**
- `pivot/charon_swarm_diminishing_returns_2026-05-25.md` -- the
  diminishing-returns audit that motivated the generative-layer
  build.
- `pivot/meta_analysis_charon_swarm_advice_2026-05-25.md` -- the
  4-frontier-model convergence that named "missing generative layer"
  as the load-bearing gap.
- `charon/agents/erebos/generators/__init__.py` -- plugin registry
  Erebos instantiates from.

---

## Design rule (NON-NEGOTIABLE)

> No conjecture confetti. Every generation must carry its own
> falsification route.

Every generator plugin MUST implement the six-field Erebos
Implementation Spec:

1. **Input / Provenance** -- which ledger rows, which kill patterns,
   which Hecate signals does this generator consume?
2. **Transformation** -- the deterministic operation that turns
   inputs into a composed claim.
3. **Output Claim** -- the structured statement (formal enough that
   a Stygian loader can be written for it).
4. **Falsification Route** -- the SPECIFIC Stygian battery shape +
   data restriction that tests the claim.
5. **Expected Kill Pattern** -- the kill_pattern label that Hecate
   will see in the kill_ledger when the claim fails the way the
   generator predicts.
6. **Loader Feasibility** -- Easy / Medium / Hard / Very Hard,
   with a one-line note on what the loader actually needs.

A generator that emits claims without a falsification route is
banned from the registry.

---

## Operational directive (per James 2026-05-26)

> Do not attempt to build all 25 simultaneously. Instruct the agent
> to build the **Erebos Phase 1 Combinators (1, 2, 3, 5)** first.
> They require the least custom mathematical logic and rely purely
> on data manipulation (filtering, sorting, substituting). They will
> produce the fastest falsifiable yields for Stygian.

Translation into Charon swarm sessions: this document is the spec;
each generator is one task; ship in iterations; document and
research per generator before implementing; loop, don't rush.

---

# PHASE 1: CORE COMBINATORS (Generators 1-5)

## Generator 1: Intersection Composer

**STATUS:** SHIPPED in Erebos v0.7 (commit 45cef115); refactor to
plugin form in v0.8 alongside this spec.

- **Input / Provenance:** Two survived or partially-survived claims
  (Claim A, Claim B) from the swarm's substantive-row pool (PROMOTED
  or UNVERIFIED-with-battery-output from Stygian/Pollux).
- **Transformation:** Extracts the subject of Claim A and applies
  the constraint/filter of Claim B.
- **Output Claim:** `Pattern X (from A) holds when restricted to
  Subset Y (from B)`.
- **Falsification Route:** Stygian samples objects exclusively
  within Subset Y and runs the standard battery for Pattern X.
- **Expected Kill Pattern:** `base_rate_failure` (the pattern holds
  no better in Subset Y than in the global population).
- **Loader Feasibility:** EASY. Reuses the exact loaders from Claim
  A and Claim B with compounded SQL/JSON filters.

**Charon swarm specifics:**
- Existing MVP at `charon/agents/erebos/daemon.py:_synthesize_composed_claim`.
- Currently emits 20+ composed claims per day; Stygian short-circuits
  with `stygian_erebos_composed_loader_pending`.
- The "compounded filter" loader is v0.9+ work and requires a
  composition-aware Stygian loader that can intersect two parent
  loaders' value sets.

## Generator 2: Contrast Generator

**STATUS:** Shipping in v0.8 alongside this spec.

- **Input / Provenance:** A globally-rejected claim that showed
  high variance in its kill logs (the rejection wasn't uniform
  across the dataset).
- **Transformation:** Splits the dataset via a binary categorical
  variable (e.g., CM / non-CM, Salem / non-Salem, even / odd
  degree) and hypothesizes a divergence in survival rate.
- **Output Claim:** `Survival rate of Claim C in Group A != Survival
  rate of Claim C in Group B by margin > delta`.
- **Falsification Route:** Permutation test. Stygian randomly
  shuffles the Group A / Group B labels N=1000 times and compares
  the observed divergence to the shuffled-label distribution.
- **Expected Kill Pattern:** `permutation_null` (the observed
  difference is statistically indistinguishable from shuffled
  labels).
- **Loader Feasibility:** EASY. Requires only a binary categorical
  available in the source dataset (BSD has CM flag; Mossinghoff has
  Salem class; OEIS has even/odd-index split).

**Charon swarm specifics:**
- First plugin to implement beyond G01.
- Needs a per-source categorical map (BSD → CM/non-CM; Mossinghoff
  → Salem/Pisot/non-extremal; OEIS → keyword categories).
- Permutation null is local computation, doesn't need new battery
  primitives.

## Generator 3: Failure-Neighborhood Generator

- **Input / Provenance:** A hard-killed claim with a structured
  kill_vector (e.g., failed on equality, but values remained close
  by some metric).
- **Transformation:** Weakens the mathematical operator. `=` becomes
  `≡ mod N`, `≤`, or `|A - B| < k`. The transformation is
  literally an operator substitution in the claim's predicate.
- **Output Claim:** `Invariant A [weaker_operator] Invariant B`.
- **Falsification Route:** Standard Stygian battery using the
  relaxed operator.
- **Expected Kill Pattern:** `boundary_collapse` (the weakened claim
  is so loose it becomes trivially true for random noise).
- **Loader Feasibility:** MEDIUM. Requires AST parsing + mutation of
  operator nodes in the claim's predicate code. James's spec.

**Charon swarm specifics:**
- True AST mutation requires the claim to be expressed as a Python
  callable, which Stygian's current text-claim-string format doesn't
  support directly.
- MVP could use string substitution on canonical_claim_text (less
  rigorous but ships in 1 session).
- Proper AST mutation requires a claim DSL or claim-as-code
  representation -- v0.10+ structural work.

## Generator 4: Survivor-Tightening Generator

- **Input / Provenance:** A claim that survived the battery but has
  a high "fuzziness" or variance score in its battery sub-tests.
- **Transformation:** Injects strict bounding constants or
  additional filters that constrain the claim until it becomes
  brittle.
- **Output Claim:** `Pattern X holds AND variance is bounded by
  epsilon AND persists after matching confound C`.
- **Falsification Route:** Adversarial edge-case search. Stygian
  specifically hunts for the exact boundary where the tightened
  constraint snaps.
- **Expected Kill Pattern:** `strict_threshold_violation`.
- **Loader Feasibility:** MEDIUM. Requires dynamic injection of
  threshold parameters into the parent loader.

## Generator 5: Confound-Swap Generator

- **Input / Provenance:** A fully promoted, surviving claim.
- **Transformation:** Identifies the highest-covariance hidden
  variable (e.g., conductor size, Mahler degree) and forces a
  control by randomizing or holding-constant that variable.
- **Output Claim:** `Pattern X survives even when Confound C is
  randomized or held constant`.
- **Falsification Route:** Stygian creates a synthetic, confound-
  matched dataset and reruns the claim.
- **Expected Kill Pattern:** `complete_signal_collapse` (proving the
  original claim was a shadow of the confound).
- **Loader Feasibility:** HARD. Requires complex dataset synthesis
  and matching algorithms (propensity score matching for math
  objects -- non-trivial).

---

# PHASE 2: DIMENSIONAL & GEOMETRIC PROBES (Generators 6-10)

## Generator 6: Null-Space Generator

- **Input / Provenance:** Hecate's density map of the kill landscape
  (which kill_patterns appear under which generators in what
  regions).
- **Transformation:** Identifies a coordinate region with zero
  surviving claims, and maps a known structural relation from a
  dense region into the void.
- **Output Claim:** `Relation R (common in dense space) will survive
  with probability >10% in Void Space V`.
- **Falsification Route:** Targeted generation of objects strictly
  within the void parameters.
- **Expected Kill Pattern:** `universal_rejection` (confirming the
  void is structural, not just an artifact of poor sampling).
- **Loader Feasibility:** HARD. Often requires writing completely
  new object-generation scripts for rare or difficult-to-compute
  spaces.

## Generator 7: Analogy Generator

- **Input / Provenance:** A highly resilient claim in Domain A.
- **Transformation:** Applies a hardcoded Erebos "dictionary" (e.g.,
  Conductor ↔ Crossing Number, Mod-p rank ↔ p-coloring).
- **Output Claim:** `Structural analogue of Pattern X holds in
  Domain B using mapped invariants`.
- **Falsification Route:** Stygian runs the exact same battery
  shape on Domain B's dataset.
- **Expected Kill Pattern:** `metaphor_collapse` (the analogy is
  poetic but mathematically incoherent, resulting in type-errors or
  random noise).
- **Loader Feasibility:** HARD. Requires Erebos to maintain a valid
  category-theory-lite dictionary.

## Generator 8: Dimensional-Lift Generator

- **Input / Provenance:** A claim with a weak positive signal (e.g.,
  R² ≈ 0.15).
- **Transformation:** Bundles the scalar target with 3-5 orthogonal
  invariants to find a hyperplane of separation.
- **Output Claim:** `Target vector Y is linearly separable in the
  joint coordinate space of [I_1, I_2, I_3, I_4]`.
- **Falsification Route:** Ergon trains a Ridge / GBT model on the
  joint space.
- **Expected Kill Pattern:** `overfitting_goodharting` (the model
  memorizes the dataset but fails on out-of-distribution held-out
  validation).
- **Loader Feasibility:** MEDIUM. Reuses existing invariants but
  requires Ergon's ML pipeline for validation.

## Generator 9: Projection-Collapse Generator

- **Input / Provenance:** A complex, surviving Erebos composition
  (e.g., G01 intersection that survived battery).
- **Transformation:** Isolates the single highest-variance
  coordinate and projects the entire claim onto it.
- **Output Claim:** `>95% of the predictive power of Complex Claim C
  is captured by the single variable Trivial Coordinate T`.
- **Falsification Route:** Ablation. Stygian drops the trivial
  coordinate and checks if the complex claim still holds any
  residual predictive power.
- **Expected Kill Pattern:** `residual_survival` (killing this
  generator means the complex claim IS genuinely complex).
- **Loader Feasibility:** EASY. Pure data-column dropping.

## Generator 10: Boundary Generator

- **Input / Provenance:** A claim that shows strange
  heteroskedasticity (variance changes over scale).
- **Transformation:** Sweeps a threshold theta across a size
  invariant to find a maximum information-gain split.
- **Output Claim:** `Pattern X survives for Size < theta and
  strictly fails for Size > theta`.
- **Falsification Route:** Focused sampling precisely at the theta
  boundary.
- **Expected Kill Pattern:** `smooth_degradation` (proving the
  boundary is an illusion of sampling density, not a true phase
  transition).
- **Loader Feasibility:** MEDIUM. Requires binary-search logic over
  continuous variables.

---

# PHASE 3: OUTLIERS, MUTATORS, META-GENERATORS (Generators 11-15)

## Generator 11: Exception-Miner

- **Input / Provenance:** A generator run that resulted in 99.9%
  kills, leaving a handful of unexplained survivors.
- **Transformation:** Cross-references the survivors against a
  massive database of boolean properties (CM, trivial torsion,
  prime conductor).
- **Output Claim:** `The isolated survivors of Failed Claim F are
  strictly defined by shared hidden property H`.
- **Falsification Route:** Generate NEW objects that possess
  Property H and feed them into Failed Claim F.
- **Expected Kill Pattern:** `out_of_sample_failure` (the shared
  property was a coincidence of the original dataset).
- **Loader Feasibility:** MEDIUM. Requires heavy database join
  operations.

## Generator 12: Invariant-Substitution Generator

- **Input / Provenance:** Any baseline claim.
- **Transformation:** Swaps Invariant A for Invariant A' based on a
  similarity matrix.
- **Output Claim:** `Relation R holds for [Substituted Invariant]`.
- **Falsification Route:** Standard battery.
- **Expected Kill Pattern:** `syntactic_or_semantic_failure`.
- **Loader Feasibility:** EASY. Simple AST node swapping.

## Generator 13: Relation-Weakening Generator

- (Close cousin to G03; focuses strictly on logical predicates
  rather than spatial neighbors.)
- **Transformation:** `A = B` → `A ≡ B mod 2`, `A | B`, `sign(A) =
  sign(B)`, etc.

## Generator 14: Relation-Strengthening Generator

- (Close cousin to G04; focuses on logical predicates rather than
  bounds.)

## Generator 15: Cross-Generator Mutual-Information Generator

- **Input / Provenance:** Kill ledger rows from two different
  generator families.
- **Transformation:** Calculates Jaccard similarity or Mutual
  Information between the kill vectors of Family A and Family B.
- **Output Claim:** `Failures in Family A and Family B are
  isomorphic; both are driven by Latent Confound L`.
- **Falsification Route:** Control for Latent L in both families
  simultaneously.
- **Expected Kill Pattern:** `uncorrelated_residual_failures`
  (meaning the generators are actually exploring orthogonal spaces).
- **Loader Feasibility:** HARD. Requires Erebos to operate on the
  substrate metadata, not just the math objects.

**Charon swarm specifics:**
- This is what Hecate already does in its cross-generator MI audit
  (post-prefix-strip patch). G15 inverts the direction: Hecate
  *measures* cross-gen MI; G15 *hypothesizes* a latent confound when
  cross-gen MI is high. Tight coupling between G15 and Hecate's
  existing pipeline.

---

# PHASE 4: ADVERSARIAL & EPISTEMIC GENERATORS (Generators 16-20)

## Generator 16: Anti-Anchor Generator

- **Input / Provenance:** A Lethe catalog of "established truths."
- **Transformation:** Inverts the assumption and posits an
  adversarial edge-case environment where the truth breaks.
- **Output Claim:** `Conjecture C fails under adversarially
  generated boundary condition B`.
- **Falsification Route:** Erebos generates the adversarial
  dataset; Stygian runs the conjecture.
- **Expected Kill Pattern:** `conjecture_survives_adversarial_attack`
  (validating the anchor).
- **Loader Feasibility:** HARD. Creating genuinely adversarial math
  objects is a search problem of its own.

## Generator 17: Causal-Intervention Generator

- **Input / Provenance:** A strong correlation.
- **Transformation:** Defines a synthetic data-munging intervention
  (e.g., shuffling labels while preserving distributions).
- **Output Claim:** `Intervention I will cleanly sever the link
  between A and B, leaving C untouched`.
- **Falsification Route:** Run the exact data permutation and
  observe the delta in the kill vector.
- **Expected Kill Pattern:** `correlation_survives_intervention`
  (implying the intervention was flawed).
- **Loader Feasibility:** MEDIUM. Standard causal inference
  pipeline.

## Generator 18: Minimal-Counterexample Generator

- **Input / Provenance:** An untested or "Unverified" global
  conjecture.
- **Transformation:** Uses Ergon's gradient field to predict the
  sector with the highest kill probability.
- **Output Claim:** `The minimal counterexample to Conjecture C
  exists within strict Region R` (e.g., conductor > 10^8, trivial
  torsion).
- **Falsification Route:** Compute heavily exclusively in Region R.
- **Expected Kill Pattern:** `region_R_exhausted_without_counterexample`.
- **Loader Feasibility:** MEDIUM. Pure orchestration routing.

## Generator 19: Proof-Obligation Generator

- **Input / Provenance:** A highly complex Erebos composition.
- **Transformation:** Emits the logical dependency graph.
- **Output Claim:** `Claim C is true iff Sub-claim C_1 and
  Sub-claim C_2 are true`.
- **Falsification Route:** Falsify C_1 or C_2 independently.
- **Expected Kill Pattern:** `sub_claim_falsified` (taking the
  macro-claim down with it).
- **Loader Feasibility:** HARD. Requires Lean / formal-logic
  integration to extract the obligations.

## Generator 20: Instrument-Disagreement Generator

- **Input / Provenance:** A Lethe cold-call verdict vs. a Stygian
  empirical verdict.
- **Transformation:** Detects a clash (LLM = True, Code = False).
- **Output Claim:** `The LLM hallucinated this capability due to
  data contamination from related Concept K`.
- **Falsification Route:** Ablation test on the LLM prompt excluding
  Concept K.
- **Expected Kill Pattern:** N/A (this generates meta-epistemic
  claims about the AI, not about the math).
- **Loader Feasibility:** EASY. Simple text-comparison script.

---

# PHASE 5: ADVANCED STRUCTURAL EXPANSIONS (Generators 21-25)

## Generator 21: Isomorphism / Functor Generator

- (Beyond Analogy (G07): maps not just patterns but the
  TRANSFORMATIONS between objects.)
- **Output Claim:** `The structural transformation f(A) → A'
  strictly maps to g(B) → B'`.
- **Loader Feasibility:** VERY HARD. Requires deep mathematical
  embedding mapping.

## Generator 22: Subgraph / Clique Generator

- **Input / Provenance:** A dense cluster of surviving claims with
  high Jaccard overlap in their datasets.
- **Transformation:** Intersects the logical predicates of the
  entire clique.
- **Output Claim:** `Clique C is generated entirely by the single
  Master Property M`.
- **Falsification Route:** Find an object that satisfies Master
  Property M but breaks one of the sub-claims in the clique.
- **Expected Kill Pattern:** `counterexample_breaks_master_unification`.
- **Loader Feasibility:** MEDIUM. Graph clustering algorithms
  (Louvain) over the kill ledger.

## Generator 23: Asymptotic Limit Generator

- **Input / Provenance:** A claim that is "mostly true" but messy
  in small configurations (small conductors, low degrees).
- **Transformation:** Formulates an expected error term that decays
  as size increases.
- **Output Claim:** `The failure rate of Pattern X scales
  proportionately to O(1/N) where N is object complexity`.
- **Falsification Route:** Stygian samples exponentially larger
  objects and plots the error decay.
- **Expected Kill Pattern:** `error_term_does_not_decay`.
- **Loader Feasibility:** MEDIUM. Requires high-compute loaders
  capable of accessing extreme-value databases.

## Generator 24: Symmetry / Twist Generator

- **Input / Provenance:** A confirmed surviving claim on an object.
- **Transformation:** Applies a twist / automorphism to the object.
- **Output Claim:** `Pattern X is strictly conserved under Symmetry
  Transformation S`.
- **Falsification Route:** Generate the twisted objects and run the
  battery.
- **Expected Kill Pattern:** `symmetry_breaking`.
- **Loader Feasibility:** EASY. If the underlying math libraries
  (SageMath / PARI) support the twist operations natively.

## Generator 25: Degeneracy / Trivial-Case Generator

- **Input / Provenance:** A highly complex, highly specific Erebos
  composed claim.
- **Transformation:** Strips all complexity (sets rank to 0, genus
  to 0, degree to 1).
- **Output Claim:** `The complex Relation R must trivially hold (or
  elegantly zero out) for Degenerate State D`.
- **Falsification Route:** Run the claim exclusively on degenerate
  objects.
- **Expected Kill Pattern:** `division_by_zero_or_type_error`
  (proving the logic wasn't generalized properly).
- **Loader Feasibility:** EASY. Extremely fast to compute; serves
  as a high-value preliminary filter before wasting compute on
  massive objects.

---

# CHARON SWARM FEASIBILITY RE-RANK (2026-05-26)

James's spec rates feasibility on intrinsic loader complexity. I
re-rank below by *current Charon swarm state*: what we can ship
THIS WEEK given existing infrastructure (kill_ledger, battery_unified,
stygian executor, pollux scanner, cascade, multi-source Hecate)
vs what needs new infrastructure first.

**Tier S -- Ship in v0.8 (one session, no new infra):**
- G01 Intersection (already shipped MVP; needs plugin refactor)
- G02 Contrast (binary split + permutation null; ~150 LOC)
- G09 Projection-Collapse (column-drop ablation; ~100 LOC -- can
  ship as Erebos plugin even without composition-aware Stygian
  loader because the claim itself is testable)
- G20 Instrument-Disagreement (text-compare Lethe vs Stygian
  verdicts; ~80 LOC; Lethe must produce a non-null verdict first --
  currently saturated; might be vacuous until Lethe v2 ships)

**Tier A -- Ship in v0.9 (one session, mild infra):**
- G12 Invariant-Substitution (similarity matrix + AST node swap; AST
  for strings is easy)
- G13 Relation-Weakening (string-substitution version: `=` → `≈`,
  `=` → `≡ mod N`; ~150 LOC for MVP)
- G14 Relation-Strengthening (tighten thresholds; ~150 LOC)
- G22 Subgraph/Clique (Louvain over Hecate's kill_ledger; needs
  networkx dep but otherwise straightforward; ~200 LOC)
- G25 Degeneracy/Trivial-Case (set rank=0, genus=0, etc. and run;
  ~120 LOC + per-domain trivial-case rules)

**Tier B -- Ship in v0.10+ (multi-session, real infra):**
- G03 Failure-Neighborhood (proper AST mutation -- requires claim
  DSL or claim-as-code rep; v0.10+ structural work)
- G04 Survivor-Tightening (dynamic threshold injection; needs
  parameterized parent loaders)
- G08 Dimensional-Lift (Ergon ML pipeline integration; Ergon work
  outside Charon scope)
- G10 Boundary (binary search + heteroskedasticity detection)
- G11 Exception-Miner (database join on boolean property cube)
- G15 Cross-Generator MI as Generator (inverse of Hecate's audit;
  Hecate emits the signal, G15 hypothesizes the latent confound)
- G17 Causal-Intervention (causal inference pipeline)
- G18 Minimal-Counterexample (Ergon gradient field integration)
- G23 Asymptotic Limit (high-compute loaders for extreme-value
  databases)
- G24 Symmetry/Twist (SageMath/PARI integration -- PARI is already
  used by mahler.py, so feasible)

**Tier C -- Big infrastructure prerequisites:**
- G05 Confound-Swap (propensity score matching for math objects --
  research-grade work)
- G06 Null-Space (writing new object-generation scripts for rare
  spaces)
- G07 Analogy (category-theory-lite dictionary; nontrivial domain
  modeling)
- G16 Anti-Anchor (adversarial math object search)
- G19 Proof-Obligation (Lean / formal-logic integration)
- G21 Isomorphism/Functor (deep mathematical embedding mapping)

---

# MULTI-SESSION SHIP LADDER

Per James's directive ("Loop, chipping away at it in iterations.
Do not just try and process this quickly as a single prompt
request."):

**v0.8 (this session):**
1. Erebos refactor to plugin architecture (G01 as first plugin).
2. G02 Contrast plugin.
3. This spec doc.
4. Backlog of remaining 23 generators as tracked tasks.

**v0.9 (next session):**
5. G09 Projection-Collapse plugin.
6. G12 Invariant-Substitution plugin.
7. G25 Degeneracy plugin.

**v0.10:**
8. G13 Relation-Weakening (string-substitution MVP).
9. G14 Relation-Strengthening.
10. G22 Subgraph/Clique (with networkx dep).

**v0.11+:**
11. Composition-aware Stygian loader so Erebos compositions actually
    get attacked by the battery (currently all short-circuit to
    `stygian_erebos_composed_loader_pending`). This is the load-
    bearing infra unlock for ALL Erebos generators -- without it,
    every generator produces unverifiable candidate-claims.
12. Continue Phase 2/3 generators as the composition-aware loader
    makes their outputs testable.

**Throughout:** for each generator shipped, research notes go into
`pivot/erebos_g<NN>_<name>_research_<date>.md` covering:
- which datasets in the repo it operates on
- which papers in the Clio paper-mining substrate are relevant
- which existing kill_vectors it consumes
- where in the kill_ledger its outputs land
- what would falsify the META-claim that this generator produces
  substrate-grade output (not just more rows)

---

# Closing posture

This spec turns Erebos from a single-method composer into a plugin
host for 25 hypothesis-generator archetypes. The architectural shift
is small (one new package directory + a registry); the substrate
shift is huge (the swarm gains 25 distinct ways to produce
candidate-claims, each with its own falsification semantics).

The non-negotiable design rule -- no conjecture confetti, every
generation must carry its own falsification route -- is what keeps
this from devolving into a markdown spam generator. Each plugin must
implement the six-field spec. The plugin registry refuses
registration of generators that don't conform.

Per the substrate-passive-consumer warning: shipping plugins without
the composition-aware Stygian loader produces beautiful-but-untested
candidate claims (the current state). The v0.11+ priority is closing
that gap so the generators' outputs carry empirical signal, not just
structural novelty.

-- Charon, 2026-05-26
