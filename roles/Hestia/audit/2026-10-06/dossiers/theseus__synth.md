# Dossier: theseus/synth (Theseus concept tensor / synthetic ancestry)

Hestia audit 1, group G8(a). Auditor: Hestia worker (Claude, same model
family as the engine author -- see AUDIT_PLAN s4 conflict note).
Currency: 2026-10-06. Worktree HEAD 3fed30ac9 (origin/main merge).

VERDICT: SALVAGE_COMPONENT -- the collision ecology does not beat random programs and cannot express a reasoning task, but its control-and-ruler harness (hidden-known, execution-neutral, lineage-integrity, matched-random, rule-destroyed twins, preregistered H1) is a reusable instrument that should be carried forward.

## 0. Identity

- Paths: theseus/synth/ (15 files, 3320 lines incl. tests), run outputs
  theseus/{corpus/g0,entities,lineages,collisions,tensor,fingerprints,
  archive,dark_objects,controls,runs,reports}/*v0*_2026-09-30*.
- Seat: Theseus (roles/Theseus/, 30 files). Charter
  roles/Theseus/prompts/2026-09-30_charter/01_OPERATOR_CHARTER_verbatim.md.
- Census (docs/fleet/fleet_state.json): engine_id theseus/synth,
  kind research-engine, state ACTIVE (derived from last commit c96bc5538
  2026-09-30), WORK_STATE READY. No synth code or run commit since
  2026-09-30; the seat's 2026-10-06 journal is about an unrelated Cosmos C4
  world family (roles/Theseus/journal/2026-10-06.md).
- Blobs read at HEAD 3fed30ac9: substrate.py a969edc68f, compile_g0.py
  1f681c3417, collide.py c04e249f57, battery.py 216e1532c0, rulers.py
  e98a992175, ecology.py b592527dbf, entities.py 4bccde4a5f, dark.py
  ca03151a82, known.py ad1449c6cc, run_v0.py e569bd1158, analysis.py
  9171f49dc7 (lines 1-70 only), README.md e777fe8b0d.
- Results read: theseus/reports/v0_2026-09-30.md, theseus/reports/
  v0_1_2026-09-30.md (both full), theseus/corpus/g0/v0_1_2026-09-30.jsonl
  and theseus/collisions/v0_1_2026-09-30.jsonl (parsed with python),
  roles/Theseus/REVIEW_PACKET_v0_2026-09-30.txt (lines 200-317),
  roles/Theseus/calibration/LEDGER.md, STATUS.md, BACKLOG_H0H5.md (item
  lines), PREREG.md s9-s10.
- NOT read: analysis.py beyond line 70 (the H1 rule is in its docstring,
  lines 13-26, which I relied on), tests/test_synth_v0.py, PREREG.md
  sections 1-8 in full, PREREG_AMENDMENT_1.md, the LLM arm
  (theseus/controls/llm_arm_v0/SPEC.md, GENOMES.jsonl), the tyche lens
  executor (tyche/lens.py; covered by the tyche dossier), the review packet
  lines 1-199, entity/fingerprint jsonl beyond the parse above, the .npz
  traces. I did not run the engine.

## 1. Mechanism (code, cited)

Pipeline: keyword-compile 95 human concepts -> small real-valued
reaction-diffusion-like programs -> collide k parents into a child program
-> fingerprint the child by 22 perturbations -> quality-diversity archive
-> repeat for 30 generations in lanes that forbid human parents.

1.1 Substrate. A genome is C<=4 channels over N=32 cells, T=128 steps,
up to MAXRULES=14 rules applied sequentially per step
(substrate.py:41-46, 312-399). 19 ops, all fixed numpy update laws:
diffuse, advect, react (tanh product), saturate, conserve, decay,
remember/recall (one memory field), threshold, replicate, select, mirror,
coarse, delay (HIST=9), wrap, rank, drive, gate, lensmap
(substrate.py:54-74, 321-375). The docstring itself states "nothing
Theseus finds can leave the space these ops span" (substrate.py:20-24).
There is no input stream and no output port: the only exogenous signal is
the initial condition and an optional sinusoidal "drive" (substrate.py:364-
367). A run is a closed dynamical system.

1.2 G0 compiler. Deterministic regex keyword tables map concept prose to
16 "primitive properties" (compile_g0.py:37-104), then a fixed
if-chain maps properties to ops (compile_g0.py:180-224); parameters come
from a hash of the concept NAME (compile_g0.py:151-152). The docstring
calls it "crude" (compile_g0.py:15-18). Measured by me on
theseus/corpus/g0/v0_1_2026-09-30.jsonl: 95 concepts -> 76 distinct
(C, topo, bc, init, op-sequence) skeletons, 67 distinct op sequences, mean
6.5 rules. The largest class, 14 concepts, is the 2-rule genome
[diffuse, saturate] on a 1-channel ring with spike init: program_synthesis,
constraint_satisfaction, epigenetics, active_inference, falsificationism,
pragmatism, dialectics, abductive_reasoning, autopoiesis, causal_inference,
multi_armed_bandits, type_theory, model_checking, compositional_semantics.
bayesian_inference = fourier_transforms = spectral_analysis =
[diffuse, saturate] with random init. In other words, essentially every
REASONING concept in the corpus compiles to the heat equation with a
tanh clamp; they differ only by name-hashed parameters. The
property-shuffled G0 control that would test whether concept identity
matters (compile_g0.py:17-18) was never run (BACKLOG THESEUS-08 open).

1.3 Collision. collide() (collide.py:378-504): take a contiguous cyclic
run of each parent's rules (collide.py:410-419), remap channels by parent
position (collide.py:366-370), insert a generated k-ary "react" law
(collide.py:422-431), apply 1-3 of 8 named operators chosen at random
(collide.py:391-393, 434-500), truncate to 14 rules at random keeping the
law (collide.py:481-485). Topology/bc/init are copied from first/mid/last
parent (collide.py:487-497).

1.4 "Concept tensor". Gains are 2 tanh(<u_i, w_j>) with u_i = a random
projection of the entity's fingerprint (or a hash-seeded Gaussian) and w a
FIXED random matrix drawn once from the master seed (collide.py:322-349).
TensorStore.record stores outcomes (collide.py:351-360) but nothing reads
them except use counts for coalition weighting (ecology.py:88, 106-107)
and a duplicate-tuple check (ecology.py:117). refresh_latent
(collide.py:344-346) is defined and never called (grep: no call site).
So the "tensor" is a random hash from (fingerprint, position) to a gain;
it learns nothing and transmits no credit.

1.5 Giant ball. 8-D field positions are a random projection of the
z-fingerprint (ecology.py:45-53); partner selection mixes
near/far/under-used/random modes with fixed probabilities 0.3/0.3/0.2/0.2
(ecology.py:36, 96-108); vitality is +1 per viable child, +2 per
novel-flagged child, decay 0.9 (run_v0.py:311, 347-351). Fossilisation above POP_CAP=400 (ecology.py:122-
132) did not bind: active population reached 581 (review packet D5).

1.6 Fingerprint and viability. 12 trace descriptors (level, temporal and
spatial std, ac1, spectral entropy, dominant period, activity fractions,
cross-channel corr, IC memory, value entropy; battery.py:65-98) plus 22
intervention responses, each the mean tanh of descriptor shifts
(battery.py:189-213): a 34-number vector. Viability is seven mechanical
gates (battery.py:216-253). Niche grids bin PCA/descriptor projections at
G0 percentiles into 7 bins per axis (rulers.py:302, 384-410): 7^4 = 2401
(pca), 2401 (desc), 7^3 = 343 (resp) cells. The archive quality is
reproducibility, not novelty (rulers.py:413-451) -- a good design choice.

1.7 Known-mechanism ruler. 12 hand-written textbook families in the same
DSL, 40 random parameterisations each plus 16 local refinements; verdict
by distance in units of tau_rep (known.py:30-31, 50-92, 133-161).

1.8 Dark objects and lenses. A ridge regressor predicts next-step channel
means/stds from 2C+3 observed series; DARK when held-out residual >= 0.25
and lag-1 autocorrelation >= 0.5 (dark.py:331-416). Lens evolution is a
(16+16) x 12-generation search over Tyche lens genomes, admitted if the
held-out drop >= 0.05 and beats the 95th percentile of 30 random lenses
(dark.py:426-458). Admitted lenses re-enter as collision matter via a
lensmap rule (collide.py:402-409).

Documented vs code. The README and charter language ("concept tensor",
"higher-order interaction structure", "giant ball", "synthetic concepts")
is CLAIMED vocabulary; the code is: random contiguous rule splicing +
random gains + summary-statistic novelty binning. The code is honest about
this in its own docstrings (substrate.py:20-26, compile_g0.py:11-18,
known.py:5-8, PREREG s9 conflict-of-interest paragraph).

## 2. Evidence (tiered)

OBSERVED (committed rows on main, tag v0 and v0_1, 2026-09-30):
- H1 hard test (does deep-ancestry arm D occupy cells no other arm
  reaches): v0 FAIL, v0_1 INDETERMINATE, equal n = 51
  (theseus/reports/v0_2026-09-30.md:5-14, v0_1:5-14). v0_1 exclusive
  cells EX(D) vs permutation null median: pca 21 vs 21 (p .564), desc 23
  vs 21 (p .293), resp 11 vs 7 (p .089). Random arm R has EX desc 27 > D
  23. Distance-to-other-arms O(D)-O(R): euclid +0.32 CI [-0.33, 0.76],
  cosine -0.022, quantile_l1 -0.006. No metric separates D from random.
- Arity: one-shot viable fraction pairs/triples/sextuples 0.70/0.71/0.72
  (v0) and 0.65/0.74/0.73 (v0_1); occupied pca cells 138/141/135 (v0).
  Arity is irrelevant (ledger row 1 attributes this to the 14-rule cap).
- Depth drift: Spearman(generation, distance to one-shot union) 0.080
  (v0, p .018) and 0.105 (v0_1, p .001). Detectable, tiny; straddles the
  preregistered 0.1 threshold across runs (LEDGER rows 3 and 9).
- Human material persists: VERY_DEEP raw-human rule fraction 0.24, DEEP
  0.35 (v0_1 genealogy table) because binding copies contiguous runs
  verbatim (LEDGER row 2). min_depth_to_g0 median for DEEP is 2, so
  "generation >= 5" lanes are only 2 collisions from raw human genomes.
- Mechanistic ruler: random programs R are FURTHER from the 12 known
  families than D (median best distance / tau 3.45 vs 2.15 in v0_1; 2.98
  vs 2.75 in v0). NOT_REPRODUCED_YET: R 8/10, D 12/20 (v0_1). The ruler
  calls random noise "more unexplained" than the ecology's products.
- Lens ruler: lens-dependent fraction R 12/60 vs D 5/60, E 8/60 (v0_1);
  v0 R 7, D 3, E 6. Median best residual drop 0.004-0.014. Lenses help
  random programs at least as much as deep descendants.
- Lens loop: 60 attempts, 10 admitted (v0_1), 8 (v0); drops 0.05-0.18.
- Controls: execution-neutral 0/40 viable (gate works); hidden-known 19/20
  REPRODUCED + 1 PARTIAL (positive control works); lineage integrity
  1173 checked, 0 mismatches. BUT deliberately "weird" random programs
  pass viability 38/60 (63%) and 39/60 (65%), comparable to one-shot
  pairs (65-70%): the viability gate does not exclude weird-because-broken
  dynamics.
- Rule-destroyed twins: 7/80 viable (v0_1), median distance 3.1 tau: rules
  matter to the fingerprint (non-trivial, expected).
- Compute: v0 48 min wall / ~9049 s CPU; v0_1 36 min / ~7100 s, 4 CPUs.
- Strongest candidate M000617 (D, gen 15, min depth 4, INTERPRET):
  "lens dependence NOT MEASURED" and the seat itself writes that these
  "rows have not yet beaten the random-program explanation" (review packet
  lines 215-237).
CLAIMED: none beyond the above; the seat makes no positive claim.
DESIGNED (not run): THESEUS-23 discriminating rulers with planted
structure, THESEUS-08 property-shuffled G0, THESEUS-11 evolvable
fingerprint, THESEUS-16 evolved experiments, THESEUS-17 organism
exploitation ruler, THESEUS-19 scale-up (BACKLOG_H0H5.md:3-25).

## 3. Matrix

### 3a Combinatorial explosion and reachability

Genome space (discrete skeleton only, continuous parameters ignored; my
calculation, scratchpad theseus_space.py): rule choices per slot are 25
(C=1), 1074 (C=2), 29637 (C=3), 349732 (C=4); with <= 14 rules and 100
(topo x bc x init) headers the skeleton count is ~10^21.6 (C=1) up to
~10^79.6 (C=4). Op sequences alone (C=1): ~10^17.6.

Collision-tuple space over the 95 G0 seeds alone: ordered pairs 8.9e3,
ordered triples 8.3e5, ordered sextuples 6.3e11.

Explored: ~2648 genomes evaluated per run (95 G0 + 1173 ecology + 900
one-shot + 480 control/LLM rows). Fraction of skeleton space: ~10^-76.
That number is meaningless on its own -- the point is where the space
COLLAPSES:

- Behavioural space is tiny. Every genome is projected to 34 summary
  statistics, then to 2401/2401/343 grid cells. The pooled equal-n H1 set
  (5 arms x 51 = 255 viable programs) occupies 160 of 2401 pca cells
  (behaviour_shuffle control, v0_1, analysis.py:220-238) = 6.7%, and each arm of n=51 occupies ~20-25 exclusive
  cells. The "niche" landscape saturates after a few hundred programs;
  random programs fill it as fast as the ecology. This is not a desert of
  reachability, it is the opposite: a FLAT space where everything is
  reachable by noise, so reaching a cell carries no information.
- The seed set is degenerate: 14 of 95 concepts (15%), including every
  reasoning-flavoured concept I could identify, compile to the same
  2-rule diffusion clamp. The real "G0" is ~67 op sequences over 18 ops.
- Depth is shallow in fact: min ancestry depth to a human genome is 2-4
  for most "deep" entities, and ~24-35% of their rules are verbatim G0
  rules. 30 generations of splicing under a 14-rule cap is a mixing
  process over a fixed rule pool plus mutations, not open-ended growth.
- Arity is flat (0.70/0.71/0.72) because the 14-rule cap divides budget
  by k (collide.py:397-398): a sextuple gives each parent ~2 rules.

### 3b Cosplay vs foundation

What does the work called "synthesis/novelty": (1) a fixed library of 19
hand-written numpy update laws; (2) random contiguous splicing and random
gains (the "tensor" is a frozen random projection, collide.py:322-349);
(3) a novelty ruler made of 34 summary statistics. Nothing in the loop
composes in the sense of building a new reusable abstraction: a child is a
list of at most 14 primitive rules; there is no subroutine, no call, no
typed interface, no hierarchical reuse. "Synthetic concepts SYN-###" are
DESIGNED, never built (THESEUS-13).

Is there any "reasoning circuit"? No, and the substrate cannot express one:
there is no task, no input-to-output mapping, no reward, no
environment to predict or act on. The only "learning" anywhere is a ridge
regression in the dark-object assay and the (16+16) lens search
(dark.py:355-369, 426-458), both of which are measurement devices, not
part of the mechanism's behaviour.

Is it cosplay? Of the charter vocabulary, "giant ball", "concept tensor",
"synthetic ancestry" and "lens evolution" are real code but the labels are
far grander than the mechanics: genetic-programming crossover over a
reaction-diffusion DSL, scored by novelty search. The seat does NOT
cosplay in its claims -- it scored its own hypothesis FAIL/INDETERMINATE
and logged 10 wrong calls -- but the mechanism is a selection loop over a
tiny operator set with a hard ceiling: the reachable behaviours are those
of <=14 compositions of 19 fixed field ops on 32 cells, judged by 34
numbers. That ceiling is reached already (random programs match it).

Ceiling, concretely: max expressible structure = sequential composition of
14 fixed-form local/global field updates with 1 memory field and 9-step
delay; max observable distinction = which of ~5000 grid cells the 34-dim
fingerprint lands in. Neither grows with generations.

### 3c Substrate bottlenecks

- Representation: flat rule list, no hierarchy, no binding of variables,
  no reuse. 14-rule cap (substrate.py:42) is the binding constraint on
  depth and arity (LEDGER row 1, review packet Q3).
- State and memory: 4 x 32 floats + one 4 x 32 memory field + 9-step
  history (substrate.py:41-46, 299-301). No addressable memory.
- I/O bandwidth: zero inputs during a run; the system cannot be asked a
  question, so no competence can be measured, only "behaviour".
- Credit assignment: none. Outcomes are recorded in TensorStore.edges and
  never read; selection is novelty + vitality counts, not credit for which
  rule or which parent caused a property.
- Compositionality: parent rules are spliced, not composed: channel
  remapping by (c + j) mod C (collide.py:366-370) means a parent's rules
  act on channels they were not written for; the child's "law" is a
  random-gain tanh product. No interface contract is preserved.
- Observation: the fingerprint is the bottleneck the seat itself names
  (review packet s8(d)): 12 descriptors are mostly spectral/variance
  statistics that random high-gain dynamics max out trivially.
- Seed: keyword compiler collapses meaning (1.2 above).

## 4. Deliverable sections

Discovery Approach. Turn human concepts into executable field programs,
let them interbreed for many generations in lanes that forbid direct human
parents, and ask whether late descendants occupy behaviour that one-shot
combination, an LLM, and matched random programs cannot reach -- all
judged by mechanical perturbation fingerprints, with preregistered nulls.
The "physics of intelligence" hypothesis here is that recursive
self-derived matter expands behavioural space beyond its human seeds.

The Brick Walls.
1. Random-program equivalence (number: O(D)-O(R) euclid +0.32, CI
   [-0.33, 0.76]; EX desc D 23 vs R 27, v0_1). After 30 generations the
   ecology is statistically indistinguishable from complexity-matched
   random programs on every ruler; on the mechanistic and lens rulers
   random programs look MORE novel (R 8/10 NOT_REPRODUCED vs D 12/20;
   lens-dependent R 12/60 vs D 5/60).
2. Flat behavioural space (number: 160 of 2401 pca cells, 6.7%, for the
   255-program pooled H1 set; weird programs 63-65% viable). The 34-dim fingerprint
   cannot distinguish organised from merely busy dynamics, so novelty
   search rewards noise. This wall is upstream of any scale-up.
3. Degenerate seed and no task (number: 14/95 concepts -> identical
   2-rule genome; 0 input channels). Human "reasoning" concepts carry no
   reasoning structure into the substrate, and the substrate has no
   input/output by which reasoning could be exercised or scored.
Also: the 14-rule cap makes arity irrelevant (0.70/0.71/0.72) and keeps
~24% of VERY_DEEP rules verbatim human.

Seed Viability. As a cognitive architecture: dead end as built. It
generates field dynamics, not computation, and the core synthesis loop is
GP crossover over a fixed op set with a random "tensor". What survives is
the INSTRUMENT: the preregistered H1 with equal-n permutation tests,
matched-random / execution-neutral / hidden-known / rule-destroyed-twin /
lineage-shuffle controls, exact rule-level provenance (raw_human_rule_frac,
entities.py:230-249), and the honest calibration ledger. Those would
detect a real advantage of recursive ancestry if one existed, and they
correctly refused to award one here. The ruler stack needs one fix before
reuse (viability gate admits 63% of weird programs). Hence
SALVAGE_COMPONENT (the harness), not VIABLE_SEED.

Evolutionary Roadmap (what would turn this into a substrate where
reasoning could even be tested):
1. Give the substrate a task interface. Add input channels written every
   step from an external stream and output cells read as answers; define
   a small battery of compositional tasks (parity of k bits, copy-with-
   delay, conditional routing, counting) so "behaviour" becomes
   competence. Without this, no Theseus result can bear on reasoning.
2. Replace splicing with typed composition. Make genomes typed programs
   (simply typed lambda calculus or a typed dataflow graph with port
   types: field, scalar, boolean) so a collision is a well-typed
   composition (function application, graph substitution) rather than
   rule-list concatenation; allow a child to CALL a parent as a
   subroutine. Then "synthetic concepts" become library entries
   (DreamCoder-style library learning with MDL compression: keep a
   fragment only if it shortens descriptions of solved tasks).
3. Make the tensor learn or delete it. Either fit the CP factors u, w to
   recorded collision outcomes (a bandit / Thompson sampling over parent
   tuples, credit = descendant task success) or drop the word "tensor".
4. Fix the rulers first (seat's own THESEUS-23): plant known deep-
   ancestry structure and require each ruler to separate it from matched
   random at AUC >= 0.8 before it judges D. Replace summary-statistic
   fingerprints with task-performance vectors plus compression-based
   complexity (e.g. Lempel-Ziv or MDL of the trace relative to a fitted
   linear model) so noise is penalised, not rewarded.
5. Open-endedness metrics: report a phylogenetic MODES-style suite
   (change, novelty, complexity, ecology) and an "activity" statistic
   (Bedau-Packard) against a shadow run with random selection; growth of
   the persistent-novelty curve above the shadow is the only acceptable
   evidence of open-ended expansion.
6. Multi-agent dynamics: let entities act on a shared world and compete
   for a resource whose acquisition requires a task competence (the seat's
   THESEUS-17 organism ruler), so selection pressure is about doing
   something, not about being far away.

The ONE decisive experiment next: a planted-structure discrimination test.
Build 50 genomes whose behaviour REQUIRES a 3-step recursive construction
(positive controls the charter already asks for) plus 50 complexity-
matched random genomes, and score both with the current fingerprint and
grid rulers. Kill criterion: if no ruler (any grid, any metric) separates
planted from random with AUC >= 0.75 at n = 50+50, the fingerprint is
blind to ancestry-dependent structure and the synthetic-ancestry ecology
should be retired (its H1 can never pass for a real reason). If a ruler
does separate them, rerun H1 at n >= 200 across 3 master seeds with that
ruler only. (This is THESEUS-23 made into a gate; cost < 1 CPU-hour.)

## 5. What would change this verdict

- Up to VIABLE_SEED: H1 PASS on a ruler that has first passed the planted-
  structure discrimination test, replicated over >= 3 master seeds at
  n >= 200, AND, after a task interface is added, deep descendants solving
  a compositional task that one-shot and random arms do not at matched
  compute.
- Down to DEAD_END: if the planted-structure test fails for every ruler
  AND no task-performance ruler can be attached without rewriting the
  substrate, then even the harness has no consumer here; it would remain
  only as a pattern for other seats.
- Audit falsifier: if analysis.py beyond line 70 (not read) computes H1
  differently from its docstring, or if the LLM-arm / tests files contain
  evidence of a ruler that does discriminate, the "random equivalence"
  wall would need restating. The 14-concept degenerate class was computed
  by me from the v0_1 corpus file; if the v0 corpus differs materially,
  restate 1.2.
