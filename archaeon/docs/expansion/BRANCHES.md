# Branches of diversity — worlds, organisms, interfaces, modalities

Annex to `archaeon/docs/ROADMAP.md` §Diversity. 2026-09-07. Evidence:
`ASSETS.md` (what exists and at what maturity), `SOURCES.md` (what the record
can hold), `CROSSWALK.md` (which of the 69 each branch serves).

Four branches were proposed in the assignment. The research keeps all four,
renames one, and adds a fifth that is not a diversity branch but an
instrument class. For each: the smallest world that has the phenomenon, the
organisms that can live in it, the variation / memory / observation / action
interfaces, the exchangeability null and the mechanism control, the first
bounded experiment, the reuse evidence, and what the branch cannot do.

---

## 0. What would count as an unplanned finding, and how we would know one

Written before any branch runs, at Herakles's ask (critique 2026-09-07 §6.1).
This is Archaeon's proposal; Harmonia adjudicates whether any candidate meets
it. It is deliberately narrow.

**Four separate properties (operator's correction, 2026-09-07).** A result
can be *authored* (its inputs are ours), *predictable* (derivable from those
inputs before running), *already known* (in the literature or the record),
and *scientifically novel* (not previously known, bounded to its domain).
These are independent. Choosing the rules does not mean knowing their
consequences; a regularity derived analytically can still be a discovery;
and a substrate with unauthored dynamics does not make its results novel.
The absence of an analytical shortcut is therefore **not** a discovery
requirement. For every family we still declare, at admission, its
**authoring inputs** (NK tables and neighbour lists from the seed; the CA
rule table, lattice size, horizon and IC distribution; the program
specification and step budget; the replicator's kernel and resource regime),
because the *stipulated-outcomes list* below is written against them, and
because a result about the construction itself must be reported as one.

**Candidate unplanned finding.** A regularity in the fossil record that
(1) was **not stipulated**: it is off the family's stipulated-outcomes list
— the enumerated competing explanations and predicted outcomes registered
before the run — whether it concerns the dynamics or the landscape itself;
(2) survives the family's exchangeability null and its mechanism control
under matched seeds; (3) is **not already known** for that substrate — a
rediscovery of a literature-known result is a calibration anchor and is
labelled so; (4) is reproducible under replay and under a fresh seed of the
same authored world class. Whether it is *predictable* from the authoring
inputs is recorded as a property of the finding (analytic, numerical, or
only by running), not used as a bar. Harmonia then rules whether the
candidate is a finding, a calibration, or an artefact. A finding is bounded
to the world class it appeared in.

**Consequence for the branches.** Branch A's *purpose* is method
evaluation, and that is what its first experiments are designed to
establish. It could nonetheless yield a previously unknown regularity about
search or landscape structure, which would be a real finding with a limited
domain, and (1)–(4) apply to it unchanged. Branch C offers the more direct
route to collective computation — the EvCA literature's achievement was the
evolution and analysis of strategies expressed through the dynamics of
authored rules — but its substrate does not make its results novel: a
reappearance of particle strategies is a calibration anchor under (3); a new
strategy class, or structure in the random-rule record that predicts
accuracy, would be a candidate. C runs **in parallel with A** (ROADMAP §D.8)
because it is the more direct route, not because A cannot surprise.

**What this definition refuses.** "Looks interesting" (any judge, human or
model); a detector firing (a reason to look, per charter); a high score; a
new descriptor cell occupied; anything computable from the seed.

---

## A. Interacting landscapes (static, structured) — 17 entries

**Purpose, named:** a METHOD-EVALUATION instrument. Its difficulty is a parameter we set and its tables are derived from a seed we choose; nothing in it is unauthored (§0).

*Candidate strings whose components affect one another's usefulness.*

**Phenomenon.** Epistasis: the contribution of a locus depends on the state
of others. On the current bench (onemax against a hashed target) every locus
is independent, so hill-climbing, illumination, novelty and stepping-stone
claims are all confounded (Herakles C-3; entries `sbse.hillclimb.search`,
`map.elites`, `novelty.search`, `illumination.grid`, `evolcomp.fitness`,
`nas_bench_evaluation`, `coevolution.parasites`, `adam_yeast_growth` …).

**Smallest world that has it.** An NK landscape: `length` loci, each with a
contribution table over itself and `k` others, tables derived from the world
seed. `k = 0` is additive (the built-in mechanism control); `k > 0` is
epistatic. Deterministic, seed-derived, ~100 lines, no external code.
Alternatives retained: `royal_road` (block structure; composition), `needle`
(no gradient; the search-difficulty control), and the repo's own
`genesis/harmonia_c/gen3/arena.py` SlotVM (shared-register interference,
RUNNABLE_IN_ISOLATION, adjudicated as an *instrument*) — reopen SlotVM if NK
proves too tame to separate methods.

**Organism.** A bitstring. Variation: bit flip, block crossover (declared,
seeded). Memory: none in the organism; the *producer* supplies memory through
the fixed-target series (C-0). Observation: score, and — if the executor
returns it — the per-locus contribution vector (the witness of this family:
which loci are below their table maximum). Action: propose the next
candidate.

**Exchangeability null.** Relabel loci under a permutation and permute the
candidate identically; score must be invariant. Known answer: zero effect.

**Mechanism control.** `k = 0` under matched seeds. Anything a method does on
`k > 0` that it also does on `k = 0` is not about interaction.

**First bounded experiment (WP-A3).** Fixed-target series at `k ∈ {0, 2, 4}`,
`length 24`, matched seeds, `N = 20` queries per series, 3 seeds per `k`,
random queries only (the frozen random control of this family). Observations:
score per query, contribution witness. Measured: D3 eligibility and fire rate
per `k` against the family's exchangeability null. **Question not stipulated
in the design:** whether the fossil record of `k > 0` worlds carries region
structure a directed policy could exploit and `k = 0` does not. That is
M-SIGNAL's question, asked on a substrate where the answer is not analytically
flat. Controls: `k = 0`; the permutation null. What the observations change:
a fired D3 region on `k > 0` becomes the argument of
`bitstring.resample_region.v0`'s NK sibling.

**What this branch can and cannot do.** Transfer of a **source-derived
candidate** into a related NK world through a declared mapping, against
matched fresh / shuffled / unrelated-source baselines, is available on WP-A4
alone (R6 as amended). What the branch cannot support is a claim about
*carried runtime state*, because its organism has none; that contrast is
reserved for a family whose organism does.

**Reuse evidence.** None runnable for NK itself; `SerendipityFoundry/D7`
`proof_world` (lock-chain, CERTIFIED_NONLINEAR_WORMHOLE) and
`incubation/worlds/families.py` (integer-register puzzles with an exact
meet-in-the-middle oracle, 44 tests passing) are structured static worlds that
could follow NK as second and third families with an *exact* oracle.

---

## B. Symbolic execution — 17 entries

*Programs, expressions, or rewrite systems with compositional behaviour and
exact counterexamples or execution traces.*

**Phenomenon.** Compositionality and exact refutation: a program's behaviour is
a function of its parts, and a specification violation has a *witness* (an
input on which the program is wrong). Entries: `cegar.abstraction.loop`,
`cegis_boolean`, `fm.bounded.model.check`, `l2s.dagger`,
`program_synthesis_sketch`, `eprover_superposition`, `lm_guided_proof`,
`mil_predicate_invention`, `symbolic_regression_gp`, `lgp.bloat`,
`am_concept_generation`, `automated_conjecture_hr`, `structure_mapping` …

**Smallest world that has it.** Program evaluation against a specification
given as a finite truth table or input/output set: run the program on every
input under a step budget; result = outputs, halted flags, steps, trace
digest, and the **witness** (first input where output ≠ spec, or the full
mismatch set). Reuse: `proteus/foundry/vm.py` is INTEGRATED_WITH_SFE via
`integration/harmonia_arena.py` and replay-proven (152 tests); RM-D5's
14-opcode register machine (`agent_d5_blind`, runnable) is the alternative
interpreter; `agent_d3_blind/s3_trs.py` (term rewriting, PRESENT) and
`incubation_d/vm/machine.py` (homoiconic D-VM, 6 tests) are the rewrite-system
and self-modifying variants for later.

**Organism.** A program (tape / opcode list). The 64 frozen USE_A specimens
are the only existing organisms; Harmonia measured that 75% are world-blind
under the current input channel, so claims *about that population's
responsiveness* wait on a wider channel (Harmonia's PATH B; D-8, scoped) —
producer-proposed programs do not. Variation:
Proteus's thirteen syntactic descent operators exist but are
`NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`; until a neutral kernel is
qualified, variation is producer-side (seeded edits declared in the template)
and breeding stays BLOCKED per Proteus's charter. Memory: the tape. Observation:
outputs, witness, trace (bounded). Action: emit output; later, modify tape.

**Exchangeability null.** Rename opcodes under a bijection applied to both
program and interpreter table; trace and outputs must be identical. Known
answer: zero effect.

**Mechanism control.** Withhold the witness: the same search with a
count-only oracle. Rounds-to-match with and without the witness prices C-2
before any other use of it (entries `cegar.abstraction.loop`,
`cegis_boolean`, `query_by_committee`).

**First bounded experiment (WP-B3).** Fixed specification (one truth table
over 4 inputs, seed-derived), fixed-target series of `N = 20` proposed
programs per series, two arms declared in a comparison family: **witness
returned** vs **witness withheld**, selection in both arms by the *same*
deterministic rule over prior fossils (the producer's next program is chosen
from the retained set by a declared rule, not by an LLM). 3 seeds per arm.
Measured: rounds-to-match; step budget consumed. **Question not stipulated:**
whether the program family's fossil record has region structure (opcode
histogram as coordinate) that differs from the bitstring family's — i.e.
whether compositional worlds produce fossils a detector can read at all. What
the observations change: the witness becomes the argument of a directed
template (`program.refine_on_witness.v0`), which is the first template whose
*parameter* is a prior observation's content.

**What this branch cannot do.** It does not make the 64 specimens into
organisms that observe the world; that is Proteus's and Harmonia's PATH B
(WP-B4), which gates **claims relying on that population and channel** —
not producer-proposed programs, not source-artifact transfer, and not the
witness experiment (WP-B3).

---

## C. Spatial, stateful environments — 10 entries

**Purpose, named:** the only substrate in this plan where an unauthored regularity can appear today (§0). Runs in parallel with A.

*Controllers with memory, local observations, and actions that change later
possibilities.*

**Phenomenon.** Local rule, global task: an organism sees only its
neighbourhood, its action changes the state its neighbours will see, and the
task (classify global density) is only solvable by coordinating through
time. Entries: `hide_and_seek_autocurriculum`, `empowerment`,
`artificial_curiosity`, `intrinsic`, `l2o.meta.optimizer`,
`poet_paired_coevolution` (environment side), `rbn.attractor`,
`evodevo.bias`, `neurodynamics.attractor.evo`, `pbt_hyperparam_schedule` …

**Smallest world that has it — and it already exists, runnable and
verified.** The 1993-95 EvCA density-classification task:
one-dimensional binary cellular automaton, radius 3, `N = 149` cells,
`T` steps, initial conditions drawn at declared densities. The organism is the
128-bit rule table; the world is the ring; observation is the 7-cell
neighbourhood; the action is the cell's next state; memory is the lattice.
Herakles recovered six historical genomes and verified them by execution
(`herakles/specimens/spec-evca-density/`, numpy verifier, RUNNABLE_IN_ISOLATION;
GATE-1 open). This is the **only** spatial substrate in the repository. The
`ludus/arena` grid/arena worlds are RUNNABLE_IN_ISOLATION with zero pytest
coverage and reach at most "ablation supported" in their own maturity ladder;
they are the retained alternative, reopened when a test suite exists.

**Organism.** The rule table (a controller: 128 bits, one action per local
observation). Variation: bit flips on the table; the two exact symmetries
(left–right reflection, 0–1 complement) are semantics-preserving moves.
Memory: none inside the rule (the lattice is the memory; a rule *uses* it
through time). Observation: neighbourhood; at the family level, accuracy over
`n_ic` initial conditions and the **witness** (which initial conditions were
misclassified). Action: next state. Raw material: a bounded space-time
diagram for one declared initial condition (149 × T bits, ~6 KB at T = 320)
— the family's *raster*.

**Exchangeability null.** For an exact reflection null, transform the rule
**and the realised initial condition**; for complement, also the majority
target and the witnesses. "Same seed" alone is not the symmetry. Trajectories
are compared after normalisation, not as raw hashes of differently oriented
arrays. Known answer: identical correctness masks. A literature-known
symmetry, so it doubles as a calibration anchor (WP-C1/C2).

**Mechanism control.** Radius 0 — an explicit centre-only rule family (or a
declared projection) with the correct table size, so the control really reads
only the centre cell: no interaction. `T = 1` — a **shortened-horizon**
intervention (one declared update); it is not the removal of all state or
memory, and the report names the horizon change separately from any memory
claim. Both are single-parameter interventions; both are described for what
they are (WP-C2).

**First bounded experiment (WP-C3).** Two comparison arms in one family:
**random rule tables** (the family's frozen random control, seeded) vs the
**six historical genomes** as fixed organisms, on the same declared IC
distribution and seeds, `n_ic = 100`, `T = 320`, 4 ordered repeats per world.
Observations: accuracy, misclassified-IC witness, one space-time diagram
digest per repeat. Measured: accuracy distributions; D3/D6 eligibility and
fire rate on the random arm against the reflection null. **Question not
stipulated:** whether the random-rule fossil record has region structure
(rule-table density of 1s, or a declared descriptor such as the number of
output-1 entries among neighbourhoods of a given density, as the coordinate)
that a detector flags and a directed template raises accuracy on — the
literature says particle-based strategies occupy a small region; whether a
*fossil-directed* search finds it is not stipulated, and a rediscovery would
be a calibration result, not a discovery. Controls: `r = 0`, `T = 1`, the
reflection null. What the observations change: a fired region becomes the
argument of `ca.resample_region.v0`; a witness IC set becomes the seed of a
directed IC distribution.

**Perceptual modality, honestly.** The space-time diagram is an image. The
rule *receives* only its neighbourhood, not the image; the image is rendered
for humans and for descriptor computation. An organism that actually receives
a raster is a two-dimensional grid controller with a windowed observation —
deferred until a family needs it for a scientific question (D-10).

**What this branch cannot do.** No population, no inheritance, no resource;
the organism does not act on the world beyond its own cell. Coevolution of
IC distributions against rules (`poet`, `hide_and_seek`) is the first later
bridge to Branch D.

---

## D. Population ecology — 7 entries

*Replicators or competing populations whose conditions depend on resources,
inheritance, and other organisms.*

**Phenomenon.** Frequency-dependent fitness, heredity with variation, resource
competition, lineages. Entries: `digitevol.avida`, `alife.tierra`,
`alife.tierra.soup`, `raf.detection`, `mcc.bipartite`, `openended.novelty`,
`universal_darwinism.weasel`, `evo_epistemology.bvsr`.

**Does existing Avida work make this branch available earlier? No.**
`ergon/avida2003/` holds a dossier, a 112-genotype lineage of descent, and an
Avida 2.2 tarball (2005, wrong version for the 2003 experiment) that has
never been built; there is no binary, no python port, and no Tierra material
anywhere. The freeze record forbids H1B population generation and the
translation plan says "do not build an SFE world for this specimen yet" with
seven physics parameters unspecified. Herakles's "route Avida/Tierra to
`ergon/avida2003/`" was a directory-existence claim; the audit corrects it.

**Smallest world that has it.** Two candidates, neither runnable today:
1. **In-process replicator soup** (`replicator_soup_v0`): fixed-length
   genomes, copy with declared mutation rate, a resource cap, seeded
   scheduling; ~200 lines; BIT_DETERMINISTIC by construction. Emits one
   observation per generation (lineage id, parent, genome hash, resource
   share). Mechanism controls are single parameters: unlimited resource (no
   competition), zero mutation (no variation), no interaction term.
2. **External backend** (Avida 2.2 built under the host's MinGW toolchain,
   wrapped under the not-yet-existing `external_backend_v0` contract).
   Fidelity to Avida 1.6 unknown; repeatability must be measured under
   tested conditions (WP-P0/X2), not assumed either way, and matching runs
   are not proof of determinism.
The Toussaint L-system replicator (`herakles/specimens/spec-toussaint-
exploration/derived/hct01.c`, RUNNABLE_IN_ISOLATION after compilation) is a
third: a developmental replicator with real dynamics, in C with its own PRNG.

**Organism.** A genome in a population. Variation: copy with mutation — and
**no qualified neutral mutation operator exists anywhere in the repo**
(Proteus's kernel carries authored probability current; memory:
`project_proteus_seat`). A *specified* neutral baseline (reference measure,
mutation process, fitness, reproduction/replacement, resource regime) is
qualified under WP-P3 for the **claims that need it**; reversibility
(detailed balance) is a separate statement — nonreversible kernels have
stationary distributions, and a declared mutation bias can itself be a
treatment. Descriptive execution and study of population dynamics do not
wait on P3.
Memory: the population. Observation: resource share, offspring count.
Action: replicate.

**Exchangeability null.** Relabel lineages; permute genome loci consistently;
known answer: zero effect on lineage statistics.

**Mechanism control.** Unlimited resource → neutral drift with the same
demography (the matched null for every "diversity persists" claim). Zero
interaction → independent replicators.

**First bounded experiment.** Not yet designable: the unit of analysis
(`generation`) does not exist in SFE's vocabulary (D-2), and no runnable
world exists. The branch begins with a **spike (WP-P0)**: build Avida 2.2 or
port the soup, run each twice under one seed, compare digests, report which
is BIT_DETERMINISTIC and what it costs. Two days, no science.

**What this branch needs from others.** Harmonia: the unit vocabulary and the
neutral-kernel qualification test. Daedalus: `generation` in
`unit_of_analysis`. Mnemosyne: a lineage-edge write path. Vivarium: the
stateful kind or the backend contract.

---

## E. Numeric calibration — 13 entries (an instrument class, not a branch)

`bacon_equation_discovery`, `comp_sci_discovery.bacon`,
`equation_discovery_sindy`, `falsification_walk`, `pbt.stateful.walk`,
`computational_mathematics_walk`, `d_optimal_design`, `sciml_pinn_residual`,
`bayesian_utility`, `discovery_informatics`, `causal_discovery_pc`,
`simulate_study`, `science_of_science`. These are experiments whose correct
answer is analytic on the current bench (the walk's variance law, the
exchangeability of bits, the rescaling of `step_scale`). They **qualify
instruments** — the detectors, the seed derivation, the repeat machinery —
and they establish nothing about discovery. Kept as the calibration layer
every branch must pass (R4, R5), and as the honest reading of the two
entries built on the dead bits axis.

**Other (5).** `ai_scientist_training`, `computational_serendipity`,
`creativity`, `knowledge_discovery`, `agi.mc.aixi.ctw`: program-level or
meta-level proposals with no world; retained in the crosswalk as questions
about the program, routed to Aporia's open-questions register rather than to
a family.

---

## Organism diversity, stated plainly

| Representation | Exists? | Variation operator | Memory | Observes | Acts |
|---|---|---|---|---|---|
| bitstring | yes (bench) | flip / crossover (declared) | none | score, witness (after C-2) | propose |
| program (tape) | 64 frozen USE_A | 13 descent ops, NOT qualified neutral | tape | inputs; 75% world-blind today | output |
| rule table (controller) | 6 historical + random | flips; 2 exact symmetries | lattice (through time) | 7-cell neighbourhood | next state |
| replicator genome | none runnable | copy-with-mutation, kernel unqualified | population | resource share | replicate |

Multiple LLM models or prompt variants are not rows in this table. An LLM
may *propose* a program or a rule table as a PROPOSED template; the organism
is the artifact, sealed and replayable, not the proposer.

## Modalities entering the ecosystem

| Modality | Carrier today | First family that emits it | Organism receives it? |
|---|---|---|---|
| numeric | `result.score`, measurements | all | yes (score) |
| symbolic | `result.witness`, trace digest, outputs | B | yes (witness, after C-2) |
| spatial | space-time diagram (bounded raster, digest) | C | no — rule receives neighbourhood only |
| temporal | repeats as trajectory; per-step trace (bounded) | walk, C | C: through the lattice |
| interaction | comparison-family arms; later co-evolved pairs | A (k), C (IC vs rule) | not yet |
| lineage | one observation per generation; PEW lineage fields | D | D: through the population |
| perceptual (image) | rendered from C for humans/descriptors | C (render only) | no; D-10 |

## Amendment 2026-09-07 (later) — per the operator's amendment order

- Transfer language corrected in A and B (source-derived artifacts transfer
  without runtime memory; PATH B scoped to its population/channel).
- C's symmetry and ablation descriptions corrected (joint transformation;
  r=0 as centre-only family; T=1 as horizon change).
- D's neutral-baseline and repeatability language scoped (P3, P0/X2).
- Two continuing research workstreams replace the earlier "bench-first only"
  instruction (Herakles H-R1): region-targeted probes for A/B/C, and faithful
  requirements and expansion opportunities extracted from the existing 69,
  including routes outside the initial portfolio. The thirteen calibration-
  class proxies keep their original scientific class and a retained route
  (`CROSSWALK.md`, amended): equation discovery (BACON, SINDy) and
  physics-informed residuals are dynamical / continuous routes with named
  spikes, not calibration items.
- Perceptual input remains an explicit design option with a reopening
  condition (D-10), not a closed door.

## Branch kill conditions (computed before each branch runs; Herakles O-1)

Each branch names the result that would say it was the wrong bet, as a
precondition on its first corpus, not a discovery afterwards. A kill here
ends the branch as a bet on this program; it rejects no field.

| Branch | Kill test (precondition) | Attainable range beside it | If it kills |
|---|---|---|---|
| A (NK) | At the chosen k and L, a one-flip hill climber from random starts reaches the global optimum in ≤ c·L queries on ≥ 90% of 20 seeds (c = 2 declared). Herakles measured exactly L on the additive bench, 20/20, L 16–48. | For k = 0 the bound is exactly L; for k > 0 the fraction of starts trapped in a local optimum is computed by exhaustive enumeration at L ≤ 16 before the test (A1-e fixture). | the landscape is not doing the work: move k, or the branch is wrong at this L. Precondition on A3-acq. |
| B (programs) | The specification space is small enough that exhaustive enumeration of programs within the step budget finds a match in ≤ N proposals (N = the series length); or the witness-using toy policy (B3-d) does not differ from witness-withheld on the toy. | Enumerable program count at the declared opcode set and length; queries-to-match floor L/log₂(L+1) for the bitstring analogue (~5.2 at L = 24). | the task is a plumbing test with a known answer (A-4): enlarge the specification or the program space before any B3 claim. |
| C (CA) | **Implementation hold, not a branch kill:** a failed reflection null stops use of the implementation while it is investigated and says nothing about cellular automata as a direction. Indistinguishability of the six historical genomes from 50 random rules is a kill only after measurement sensitivity is shown adequate: the IC sample must give an SE small enough that the literature gap (lead: ~0.2–0.3 in accuracy) would be detected at the declared power. | Random rules: accuracy ≈ the density prior (~0.5 at ρ = 0.5 ICs); historical genomes: roughly 0.7–0.8 under the 1994 conventions (literature lead, unfetched; C1-e measures it). Reflection null: exact. Sensitivity: SE ≈ √(p(1−p)/n_ic) ≈ 0.05 at n_ic = 100, 0.016 at 1,000. | null failure → hold and diagnose (C3 list); indistinguishable at adequate sensitivity → the task instance or conventions are wrong, fix before any random-rule corpus is read. |
| D (replicators) | WP-P0 finds no route that builds, runs, and repeats under tested conditions within the operator's cap. | n/a (a build/run fact) | DEFERRED with the reason and reopening condition; no route is chosen by preference. |

## Attainable ranges beside every stated gate (Herakles A-2, inherited from the crosswalk)

No threshold in a branch or work package is stated without its attainable
range computed beside it. Gates named in this file:

- A3: D3 per-region false-alarm rate on a floor-sized null corpus = 0.083 exact F(7,31), 0.088 ± 0.006 measured (D3_NULL_RECONCILIATION); a "fire rate differs by k" claim needs the rate at each k's corpus geometry computed first. Hill-climb bound: exactly L at k = 0.
- B3: rounds-to-match floor for an exact oracle on a bitstring analogue L/log₂(L+1); for a program space, the enumerable-program count divided by the step budget bounds success within budget from above.
- C3: accuracy of a random rule under the declared IC distribution ≈ the density prior; the historical anchor is a lead until C1-e measures it; the reflection null's attainable deviation is exactly zero.
- E3 (bitstring exchangeability): mean 0.5, sd √(1/(4L)); the attainable "effect" is zero by derivation.
- `falsification_walk.v1`: displacement ≥ 138.6 at steps = 6400, step_scale = 1 is 3 sd (var = steps/3 → sd = 46.2), P ≈ 0.0013 one-sided under the null; at steps = 100 the same threshold is 24 sd (sd = 5.8) and cannot fire — the ladder therefore needs a per-rung threshold or a normalised field, which is recorded as a defect of v1's single-value rule, to be fixed at admission.
