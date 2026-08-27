# PREREG-INSTRUMENT — D-4 Phase 1 instrument definition

Status: DRAFT v1 (2026-08-27). Iteration permitted ONLY until the
instrument-validation gate (Section 8) passes on the synthetic controls.
Every revision is committed; nothing is overwritten silently. After
instrument validation, the surviving definitions are copied verbatim into
PREREG-PHASE1.md and frozen.

Design rule observed throughout: no metric may be scored by classifying the
generator's own output categories back onto themselves. Privilege is
measured intrinsically (transition structure, identifiability, concentration,
ablation collapse), never as balance across human-named mutation families.

---

## 1. Abstract substrate interface

All metrics, navigators, and gates are written against this interface and
nothing else. Synthetic controls and real substrates implement the same
interface, so the instrument is validated on geometries where truth is known
and then applied unchanged to geometries where it is not.

A substrate exposes:

- `n_ops`: number of primitive mutation mechanisms (operators are opaque
  indices 0..n_ops-1; no names or semantics are visible to any consumer).
- `random_genome(rng) -> G`: sample from the frozen ab-initio genome
  distribution.
- `mutate(G, op_index, rng) -> G'`: apply one primitive mutation mechanism.
- `evaluate(G) -> F`: deterministic behavioral fingerprint from the frozen
  probe suite. Metered. This is the ONLY route from genome to behavior.
- `viable(F) -> bool`: frozen mechanical viability predicate.
- `pkey(F) -> hashable`: phenotype equivalence class key (exact fingerprint
  identity on the frozen probes).
- `d1(F, F') in [0,1]`: primary behavioral distance (output disagreement).
- `d_aux(F, F') -> dict`: auxiliary distances (resource profile, trace
  disagreement) — reported, never gated on alone.

Navigators may call ONLY: random_genome, mutate, evaluate, viable, pkey, d1.
They receive no operator names, no graph, no oracle output, no substrate ID,
no target ID (only a raw target fingerprint when the task is targeted).

Meter: every evaluate() call is counted against the component that caused it
(census / operator_census / target_generation / navigation / counterfactual /
oracle_validation). Budgets bind on evaluate() counts, the common currency.
Phenotype-lookup caching, if enabled, is enabled identically for all
navigators and cache hits are metered at 1 evaluation (no cache asymmetry).

## 2. What "intrinsic privilege" means here (operational)

Privilege = the fixed physics makes a small set of directions, structures,
operators, or corridors disproportionately responsible for practical
accessibility. Four frozen assays, chosen because each detects a distinct
mechanism by which a designer can smuggle in "what kinds of change matter",
and none consults semantic labels:

- PRIV-1 Mutation-source identifiability. From behavioral displacement
  alone (feature vector of d1, d_aux components, and per-probe agreement
  pattern between parent and child), a frozen multinomial classifier
  predicts which primitive mechanism produced the transition. Accuracy far
  above chance means the operator menu partitions behavior space into
  designer-created corridors (each operator owns a recognizable kind of
  change). Reported with full confusion matrix and binomial CI, train/test
  split grouped by parent genome. Interpreted JOINTLY with displacement
  liveness: near-chance accuracy with dead operators is not neutrality.
- PRIV-2 Displacement anisotropy and concentration. Over sampled
  viable-parent transitions: (a) entropy / effective support of destination
  phenotype classes (exp of Shannon entropy, collision-adjusted); (b) share
  of behavioral displacement variance captured by the top principal
  direction of the displacement feature cloud; (c) Gini concentration of
  in-edges over destination phenotypes and top-1% hub mass. High hub mass /
  top-direction share = the physics funnels change into few channels.
- PRIV-3 Single-mechanism ablation collapse. Counterfactual removal of one
  primitive mechanism at a time; if pooled navigation success collapses
  (preregistered relative-drop bound) under removal of ONE mechanism, the
  space is a designed highway even if the full-menu histogram looks flat.
- PRIV-4 Encoding sensitivity. A frozen bijective re-coding of the genome
  alphabet (which preserves the phenotype SET exactly but changes mutation
  adjacency) is applied; if accessibility conclusions change outside a
  preregistered band, privilege lives in the representation.

Why these four: a designer can privilege change (a) through the operator
menu (PRIV-1), (b) through the geometry the operators induce (PRIV-2),
(c) through one load-bearing primitive (PRIV-3), or (d) through the binary
coding itself (PRIV-4). These are the channels the designer actually
controls once physics is fixed.

## 3. What "navigability" means here (operational)

Navigability = a history-free generic process can repeatedly reach distant
useful regions under realistic budgets. Frozen measurements:

- NAV-1 Target hit rate, stratified near/mid/far by preregistered remoteness
  (Section 6), per navigator, at frozen budget B evaluations, hit criterion
  d1(reached, target) <= EPS_HIT. (EPS_HIT reachable by construction: the
  target phenotype itself scores 0.)
- NAV-2 First-passage cost: median evaluations-to-hit among successes, and
  the full distribution.
- NAV-3 Re-findability: for each target hit by >= 1 seed of a navigator, the
  fraction of independent seeds that also hit it. Distinguishes existence /
  accidental discovery / reproducible accessibility.
- NAV-4 Coverage growth: unique viable phenotype classes discovered vs
  evaluations spent, per navigator (targetless), with collision counts.
- NAV-5 Oracle regret (analysis only): where the empirical phenotype graph
  is tractable, an omniscient BFS oracle over observed edges estimates
  topological reachability. Oracle-reachable but M0-missed = search
  weakness; oracle-unreachable = substrate failure. Oracle output never
  reaches any navigator.

## 4. Distinctions kept separate in reporting

EXPRESSIVITY (witness program exists), VALIDITY (executes — total-decode
substrates make this trivially high and it is disclosed as such, never
rewarded), VIABILITY (nontrivial: produces output on >= half the probes AND
output differs across probes, i.e. input-sensitive), DIVERSITY (distinct
phenotype classes, with Good-Turing unseen-mass estimate), ACCESSIBILITY
(reached by generic processes), CONNECTIVITY (empirical graph components),
NAVIGABILITY (NAV-1..5), PRIVILEGE (PRIV-1..4). One number never stands in
for another. "Phenotype mass" vs "accessible phenotype mass" vs
"reproducibly accessible phenotype mass" are reported as three numbers.

## 5. Synthetic geometry controls (instrument validation set)

Seven controls, all implementing the Section-1 interface, all with KNOWN
qualitative geometry. Latent structure: nodes with coordinates; fingerprint
exposes the coordinate through the same fingerprint type real substrates
use; operators are index-moves with controlled properties. The instrument
never sees the latent truth, only the interface.

- C1 FRAGMENTED: 400 islands x 25 nodes, all viable; every operator moves
  within-island only. Truth: diverse, locally fine, globally shattered.
  Expected primary flag: ACCESSIBILITY_FRAGMENTED (far-target hit ~0, oracle
  also fails far targets, giant component tiny).
- C2 IDENTITY_DOMINATED: one connected 1-D ring of 10,000 nodes; every
  operator application is identity with p=0.98, else a +/-1 step. Truth:
  connected but behaviorally inert. Expected primary flag: DISPLACEMENT
  failure (identity rate >> bound), poor coverage growth.
- C3 PRIVILEGED_CORRIDOR: two internally-navigable clusters (5,000 each);
  operators 0-3 make small within-cluster moves; operator 4 alone crosses
  between clusters, from a 1% gateway subset, with a large distinctive
  displacement. Truth: connected, diverse, navigable ONLY via a designed
  highway. Expected primary flags: PRIV-1 identifiability high (op 4
  recognizable), PRIV-3 ablation collapse on op 4 for cross-region targets.
- C4 TRAPPED_DRIFT: 100 cliques of 100 on a line; moves are strongly biased
  toward increasing index (funnel); return moves rare (p=0.02). Truth:
  locally viable and diverse, globally one-way; low-index regions become
  unreachable, re-finding early-reached regions fails. Expected primary
  flags: NAVIGATION failure on backward/far targets, RE-FINDABILITY low.
- C5 NAVIGABLE: 100x100 torus grid; five operators, each a different
  overlapping mixture of small steps, all approximately reversible. Truth:
  diverse, connected, multiply navigable, no load-bearing single operator.
  Expected: ALL gates pass; PRIV-1 accuracy low; ablation of any one
  operator degrades gracefully.
- C6 CHAOS: 100,000 nodes; fingerprint is a hash of node id (no locality:
  d1 between distinct nodes concentrates near max); operators teleport
  uniformly. Truth: enormous diversity, zero navigable structure (no
  gradient, no re-findability). Expected: NAV-1 far ~ chance, NAV-3 ~ 0.
- C7 TINY_COMPLETE: 40 nodes, complete graph, all viable, distinct
  fingerprints. Truth: perfectly navigable, trivially small. Expected:
  navigation passes but DIVERSITY floor fails (phenotype mass far below
  minimum).

Contradictory-incentive check these controls encode (charter s.28): C6
rewards diversity while failing navigability; C2 rewards connectivity via
identity; C7 rewards navigability without diversity; C3 rewards aggregate
connectivity achieved by one corridor. A metric suite that scores any of
C1, C2, C3, C4, C6, C7 as an overall PASS is broken.

## 6. Target selection procedure (frozen shape; constants frozen in PREREG-PHASE1)

Targets are generated by a designated process with its own seed, before and
independent of any navigation result, using only the substrate's own physics:

1. TARGET-GEN: from `n_tw` random viable starts, run uniform-operator random
   walks accepting viable steps, recording the phenotype at every accepted
   step, for `L_tw` accepted steps. Pool all recorded phenotypes (dedup by
   pkey).
2. Remoteness of a pooled phenotype = mean d1 to a frozen reference ensemble
   of `n_ref` fresh random viable genomes (target-gen seed family).
3. Stratify pool into near/mid/far by remoteness tertiles computed on the
   pool itself. Within each tertile, compute local density = count of
   pool-mates within d1 <= EPS_DENS; take the `k` lowest-density and `k`
   highest-density members, deterministic tie-break by SHA-256 of the
   fingerprint bytes.

Disclosure: this measures reachability of phenotypes THE PHYSICS ITSELF
exhibited under a generic process with an independent seed — i.e.
reproducible accessibility of demonstrated-to-exist phenotypes — not
reachability of arbitrary mathematically-existing phenotypes. That is the
honest measurable notion of "accessible phenotype mass" available without
exhaustive enumeration, and it is reported as such.

## 7. History-free navigator suite (M0)

All navigators: interface-only, no cross-episode state, fresh seeded RNG per
run, identical budget currency (metered evaluations), identical hit
criterion. At least two meaningfully different mechanisms must be
competitive (able to exploit structure when it exists — demonstrated on C5).

- N1 RESTART-WALK: random-accept mutation walk with restart on
  non-viability streak. (Floor baseline; also targetless coverage.)
- N2 HILLCLIMB-RESTART: greedy d1-to-target descent with plateau tolerance
  and random restarts.
- N3 NOVELTY: archive-based novelty search (targetless; within-run archive
  is search state, not learning history — discarded across runs). Coverage
  mapper; incidental target hits recorded.
- N4 RECOMBINER: population of viable genomes; selection on d1-to-target;
  variation by the frozen mutation menu plus one-point crossover at cell
  boundaries (crossover is registered as a primitive mechanism and included
  in the operator causal census; it is used only via this navigator).

N2 and N4 are the designated competitive pair (different mechanisms:
single-trajectory local descent vs population recombination). If only one
of them can exploit C5, the navigator suite is repaired before freeze —
against the SYNTHETIC controls only.

## 8. Instrument-validation gate (must pass before PREREG-PHASE1 freeze)

Run the complete pipeline (census, operator census, identifiability,
graph metrics, targets, all navigators, ablation counterfactual, gate
evaluator) on C1..C7. The instrument PASSES iff the frozen gate evaluator
assigns:

- C1 -> primary failure ACCESSIBILITY_FRAGMENTED
- C2 -> primary failure DISPLACEMENT_COLLAPSE (identity-dominated)
- C3 -> primary failure PRIVILEGED_CORRIDOR
- C4 -> primary failure NAVIGATION_FAILURE or REFINDABILITY_FAILURE
- C5 -> PASS on all gates
- C6 -> primary failure NAVIGATION_FAILURE or REFINDABILITY_FAILURE
- C7 -> primary failure PHENOTYPE_POVERTY (diversity floor)

All seven classifications must be produced by the SAME thresholds that will
be frozen for the real substrates. Thresholds are calibrated on these
controls (this is instrument calibration, explicitly not evidence about any
real substrate) and then frozen with margins reported. If the suite cannot
separate the controls, the instrument is repaired and re-run; every
iteration is committed.

## 9. Statistical discipline

- Every gated quantity is reported with its n, the unit of analysis at
  which independence actually holds (targets and seeds, not raw draws,
  where applicable), and a binomial/bootstrap CI.
- Every threshold is checked for attainability (chance level and ceiling
  computed) before freezing; a gate closer to its chance level than 2 SE at
  the planned n is redesigned before freeze.
- 5 seeds for the competitive navigator pair on the binding run; seed
  variation reported for every stochastic quantity.
