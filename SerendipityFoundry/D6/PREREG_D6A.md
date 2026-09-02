# D6-A PREREGISTRATION — BLIND ENDOGENOUS METRIC GENESIS
Frozen 2026-08-27, before any M0 evidence was produced.

## 0. Question
Can relational executable history construct a machine-native derived signal `z` whose use
causally increases acquisition of EXACT solvers, when task feedback is PASS/FAIL only?

## 1. Frozen substrate
- Artifact = straight-line boolean program, N_IN=6 inputs, DOM=64 rows, 8-gate basis
  (AND OR XOR NAND NOR XNOR ANDN ORN), 1<=L<=32.
- Wire semantics = full 64-row truth table held as one 64-bit integer. Verification is
  exhaustive over the entire domain; there is no sampling and no approximation.
- Mutation physics: point 0.70 / insert 0.15 / delete 0.15, operands uniform over legal
  earlier wires. IDENTICAL for every arm. Defined in src/substrate.py; hash recorded in
  runs/freeze.json.

## 2. Task oracle (the sparse wall)
- Each task holds a HIDDEN target behavior. The learner never receives it.
- oracle(prog) -> True | False, true iff the designated outputs equal the target on ALL 64 rows.
- NOT exposed, ever: hamming distance, count of correct rows, partial score, target truth
  table, reference solver, task id, family id, tier, module identity, any human label.
- Observable and preregistered as intrinsic: the candidate OWN full-domain wire traces,
  its length, and its own execution. These are properties of the artifact, not of the task.

## 3. Families (hidden structure, never exposed)
- A latent module set M (K=8 short programs) is chosen at battery build time.
- DEV    : tier1 = m_i ; tier2 = op(m_i,m_j) ; tier3 = op(op(m_i,m_j),m_k).   [discovery]
- CONF   : tier2/tier3 compositions of the SAME modules, index-disjoint from DEV.
           [segregated confirmation]
- ALIEN  : different surface encoding - 2 designated outputs, depth-4 compositions.
           [frozen transfer]
- STRUCT : behaviors of random programs, matched rarity, NO module content.
           [structureless control]
- NEG    : compositions of a SECOND, disjoint latent module set.  [negative transfer]

## 4. Budget and units
- B = 200,000 oracle calls per (task, arm, seed). Identical across arms. Any candidate
  generation, signal evaluation or archive work is metered separately and reported.
- 12 seeds per (task, arm). Per-task solve rate = fraction of seeds that found an exact solver.
- UNIT OF INFERENCE = task (paired across arms). Never candidate rows, never seeds.

## 5. Arms
- M0          : history-free. B split equally across three components: uniform sampling,
                restart random walk, intrinsic-novelty archive search. PASS if any solves.
- H0          : M0 (no hoard).
- H1/M1-HOARD : same search + identical retained artifact hoard, NO relations.
- H2          : same hoard + SHUFFLED relational history.
- H3/M1-REL   : same hoard + INTACT relational history, may construct/use `z`.
- Z0          : history-free signal search over the same frozen signal grammar, same
                candidate budget, same evaluator, same use-interface.
- Z1          : identical to Z0 except it receives relational history.
- Genotype inventory is byte-identical between H1, H2, H3.

## 6. Signal use interface (one, uniform)
A `z` artifact emits a bounded machine-native value used for exactly one thing: ORDERING
proposals drawn from the frozen mutation/composition physics. No other API exists. `z` may
not call the oracle, may not read the target, may not read task or family identity.

## 7. Battery validity gates (checked before any M1 work)
- V1 P0: 100% of tasks have a constructively verified exact solver within L<=32.
- V2 M0 tier1 DEV solve rate in [0.10, 0.90].  (outside -> TASK_BATTERY_INVALID)
- V3 M0 tier3 solve rate <= 0.15.              (above -> NO_SPARSE_FEEDBACK_WALL)
- V4 M0 CONF (tier2+tier3) solve rate <= 0.15. (above -> NO_SPARSE_FEEDBACK_WALL)
- V5 all anti-cheat probes of section 10 pass.

## 8. Primary preregistered tests (Holm-Bonferroni, family alpha = 0.05)
- T-P1 sparse wall      : M0 CONF rate <= 0.15.
- T-P3 causal signal    : mean(M1-REL - M1-HOARD) on CONF >= +0.20 absolute, paired
                          permutation over tasks (10,000 permutations), p < 0.01,
                          95% bootstrap CI (10,000 resamples, task-level) excluding 0.
- T-P4 not-just-hoard   : M1-REL > H2 (shuffled relations) by >= +0.15, same test.
- T-P5 frozen transfer  : z frozen BEFORE first ALIEN exposure; M1-REL - H1 >= +0.15 on
                          ALIEN, same test. Zero-shot reported separately from adaptation.
- T-CTRL structureless  : |M1-REL - H1| <= 0.10 on STRUCT. A larger effect triggers the
                          leakage / generic-diversity investigation of section 18 and caps
                          the verdict at HOARD_EFFECT_ONLY pending resolution.
Ablation (gate F): removing z from M1-REL must remove >= 75% of its advantage over H1.
Matched-complexity control (gate G): random signals of equal grammar size and equal
evaluation budget must not reproduce the effect (>= 50% of it).

## 9. Verdict ladder (exact gates)
- TASK_BATTERY_INVALID     : V1-V5 fail.
- NO_SPARSE_FEEDBACK_WALL  : V3 or V4 fail.
- HOARD_EFFECT_ONLY        : T-P3 passes vs H0 but fails vs H1/H2.
- ENDOGENOUS_SIGNAL_FOUND  : admission gates A-C hold and a z artifact exists and is used.
- CAUSAL_FINDABILITY_SIGNAL: + T-P3, T-P4, gates F and G.
- FROZEN_SIGNAL_TRANSFER   : + T-P5 with z frozen before exposure.
- SIGNAL_REVISION          : + NEG world shows use of the old z falling and an admitted
                             successor, with the original history preserved, not overwritten.

## 10. Anti-cheat probes (all must pass)
task-id leakage; family-id leakage; target or reference-solver reachability from learner
state; partial-score reachability; host introspection; cached witnesses across arms; z
access to privileged diagnostics; DEV/CONF overlap; oracle calls after budget exhaustion;
genotype inventory asymmetry between H1/H2/H3.

## 11. No within-generation rescue (section 24)
After M0 evidence is recorded: no new partial score, no easier tasks, no altered signal
grammar, no larger budget, no comparator weakening. Fatal defect -> preserve and stop.

## 12. Language discipline
The machine verdict will not use: abstraction, representation, concept, understanding,
metric, meaning. `z` is a derived signal artifact and nothing more.

## AMENDMENT 1 (2026-08-27, after M0 freeze, BEFORE any Z/M1 evidence)
Section 6 interface finalized as: tournament-k artifact selection. Wherever the frozen
proposal physics draws an artifact uniformly (archive parent, hoard operand, candidate
submitted to the oracle), a z-bearing arm draws k candidates and keeps argmax z. z=None
reduces to k=1 (uniform), so H1 is unchanged. k is a single global constant, identical at
every choice point and for every z-bearing arm (H2, H3, Z0-z, RAND-Z), fixed by the
preregistered step-8 synthetic validation (a designer-side truth-seeded z vs a matched
random z) and then frozen. Rationale: pure output-ordering cannot express any preference
over which artifacts enter a composition, making the interface unable to transmit ANY
signal - including a perfect one - which would render the experiment vacuous rather than
hard. Battery, oracle, budgets, seeds, M0 comparator, and all section 8 tests unchanged.

## AMENDMENT 2 (same time): frozen signal grammar
z genome = (w0,w1,w2,w3, tf, agg, lw): wi in {-1,0,1} weight table slot Ti; tf in
{identity, signed-log1p, positivity-indicator} per-wire transform; agg in {sum, max, mean,
count-positive} over the candidate's own distinct wire behaviors; lw in {-1,0,1} times
0.1 times program length added to the aggregate. 2916 genomes total. Table slots are filled
per condition: Z1/H3 from intact relational history (recurrence, ancestry, co-occurrence
degree, solved-output indicator); H2 from the SHUFFLED history; Z0 from hoard-intrinsic
maps only (membership, entry length, behavior popcount, empty). Same grammar, same
selection procedure, same budgets everywhere; only table contents differ. RAND-Z (gate G)
draws uniform random genomes over this same grid with intact tables and no selection.

## AMENDMENT 3 (2026-08-27, after step-8 validation, BEFORE any Z/M1 evidence)
Interface constants fixed by the preregistered step-8 machinery validation:
K_TOURN=32, candidate batch=1 (z acts ONLY at artifact-draw tournaments; every generated
proposal is submitted). Basis, all designer-side with a truth-seeded z the learner never
sees: end-to-end solve counts were binomially noisy (n=24), so a mechanistic probe
(runs/mech_probe.json) measured submitted-module-pair concentration per config; k32/cb1
maximized it (8.5e-4 vs 0 for all cb>1 configs, whose candidate-level score ranking
provably favors wire-accreting blobs and collapses pair submissions). Random-table z
solved 0/24 at k>=8, confirming tournament mechanics alone confer no advantage.
These constants now bind every z-bearing arm identically. FROZEN.
