# Prometheus Phase 3 -- requirements specification

Architect: FABLE-5.1 (seat Dionysus, instance m1-3815a3b9, host SKULLPORT / M1).
Charter: roles/Dionysus/prompts/2026-10-01_charter/ (on main at 04b97a598).
Status: FROZEN. The freeze is the commit that first adds this file. Later
changes are dated annotations below the requirement they touch, never silent
rewrites.

## Derived before salvage

**These requirements were derived before any salvage analysis.** The order is
in git history: this file and RSE_ARCHITECTURE.md are committed before
SALVAGE_MATRIX.md exists and before I opened any seat dossier, any engine
source file or any engine index record in full.

What I had read when I froze this file:

- the architect prompt (docs/phase3/PHASE3_ARCHITECT_PROMPT.md) and the
  operator's charter message;
- the four crawler REPORT.md files, in full;
- Tityos failure_taxonomy.md, in full;
- Ixion inference_dependency_map.md and institutional_timeline.md, in full;
- aggregate counts from Tityos ruler_inventory.jsonl;
- the base role, the working contract, the North Star and the tracked
  doctrine (aporia/doctrine/critical_memories.md);
- docs/phase3/PHASE3_CHALLENGES.md, after I had written down my own position
  (process/00_SNAPSHOT_BEFORE_CHALLENGES_DOC.md, then
  process/01_DELTA_AFTER_CHALLENGES_DOC.md).

What I had not read: any seat dossier under docs/phase3/intake/*/seats/, any
engine source, the engine and artifact indexes beyond a truncated listing,
and any other architect's design (none existed on main).

So the failure record informed these requirements, as the prompt intends
(section 10: "Use Tityos's recovered failure history as a design input").
What exists in the repository did not. The crawler reports do describe the
engines in summary, and I could not unread that. Each requirement therefore
names the need and the historical failure that motivates it, and none names
a Prometheus component as its answer.

One measurement was taken to ground the compute requirements: a toy integer
register machine under Numba on M1 (Ryzen 7 7700X, 8 cores / 16 threads,
32 GB, RTX 5060 Ti 16 GB) ran about 530 million instructions per second on
one core and about 5.0 billion per second on all threads (three runs each,
process/vm_throughput_bench.py). A real organism in a real world will be
slower. I assume a factor of 10 until it is measured.

> Annotation, 2026-10-01, after the freeze. It has now been measured once.
> The P1 prototype kernel, with a world in the loop, ran 1.70 billion
> organism instructions per second on 12 threads of the same machine
> (prototype/p1_slice/RECEIPT_qualify.json, section G). That is about a
> factor of 3 below the toy figure, not 10. The prototype machine is much
> smaller than the workspace machine will be, so the planning figures in
> section 13 are left as written.

## How to read this file

Each requirement has an id, a status and four lines.

- Status is one of REQUIRED, HIGH VALUE, EXPERIMENTAL, REJECTED.
  - REQUIRED: Phase 3 results cannot be read as science without it.
  - HIGH VALUE: it buys discrimination cheaply; build it early.
  - EXPERIMENTAL: worth a bounded trial; its value is not established.
  - REJECTED: considered and excluded; the reason is given so it stays out.
- Statement: what must be true.
- Why: the first-principles reason.
- Record: the historical failure that motivates it. T-numbers are the
  classes in docs/phase3/intake/tityos/failure_taxonomy.md. "Sis", "Tan",
  "Tit", "Ixi" point to a section of that crawler's REPORT.md.
- Check: how to verify the requirement is met, by something that can fail.

Numbers given as defaults (lineage counts, power, margins) are starting
settings. A campaign may change them in its preregistration, with a reason.
They are not derived constants.

requirements.jsonl beside this file is generated from it by
process/requirements_to_jsonl.py, which also checks that ids are unique and
every requirement has all four lines.

----------------------------------------------------------------------

## 1. Definitions

The prompt's final discipline forbids using reasoning, abstraction,
sagacity, cognition, emergence, metacognition or self-improvement without an
operational definition and an experimental discriminator. These are mine.
Every later section uses the words only in these senses.

### 1.1 The unit of evidence

- CELL. One combination of a world family, an organism substrate, a search
  regime and a ruler, each at a stated version.
- CAPABILITY. A behavioural property defined by a class-exclusion test in a
  named world family, with a level (for example HOLD at 4 bits).
- RESTRICTED CLASS. A set of policies defined by what they cannot do: no
  memory, at most k internal states, no information carried across an
  episode boundary, a lookup table over seen cases, a fixed hypothesis
  space.
- CLASS EXCLUSION. A world carries an exact value, or a proven upper bound,
  for the best score any policy in a restricted class can reach. An organism
  whose score on sealed worlds exceeds that bound, with a stated confidence,
  is certified outside the class. Nothing is said about how it does it.

### 1.2 The four certificates

A cell supports inference only through four certificates. The operator's
evidence-profile letters (PHASE3_CHALLENGES.md 1a) are given for mapping.

| certificate | what it shows | how it is produced | operator axis |
|---|---|---|---|
| DEMAND | the world requires the capability, and the capability pays | exact or proven bounds for each restricted class; a reference policy beating them by a stated margin | W, part of B |
| EXPRESSIBILITY | the substrate can hold the capability at the tested size | a designed organism in that substrate passes the same ruler | S |
| REACH | the search can find targets of this size in this substrate | recovery rate of planted targets at graded distances: a search-power curve | not in the profile |
| DETECTABILITY | the ruler fires on the capability and not on its imitations | positive, negative and impostor organisms sorted with measured error rates; every control shown able to fail | R, part of B |

Rule of inference:

- A POSITIVE needs DEMAND and DETECTABILITY.
- A NULL about the phenomenon needs all four, and stated power.
- A null lacking a certificate is a null about the apparatus. It is labelled
  by the missing certificate: NOT_DEMANDED, NOT_SHOWN_EXPRESSIBLE,
  NOT_REACHED_UNCALIBRATED, RULER_NOT_QUALIFIED.

### 1.3 Calibration set

- POSITIVE. A designed organism known to have the capability.
- NEGATIVE. The nearest designed organism known to lack it.
- IMPOSTOR. The cheapest organism that imitates the capability by a
  shortcut: a constant, a lookup, a reader of leaked labels, a one-shot
  latch. There is usually more than one.
- CHANNEL TEST. A fabricated record of success fed straight to the ruler,
  to show the verdict depends on its input. This is the base role's cheat
  control.
- FIRE TEST. Each control is run once against a deliberately broken
  instrument or organism, to show the control can fail.

### 1.4 Scaffold levels

How much of a capability was designed and how much was found.

| level | what is given | what search must find |
|---|---|---|
| S5 | a complete designed organism | nothing (this is the positive control) |
| S4 | the designed structure with parts removed or parameters blanked | the missing parts |
| S3 | capability-specific primitives (for example a write-to-store step) | how to compose them |
| S2 | generic affordances only (section 3), no capability-specific primitive | the mechanism |
| S1 | generic affordances with one or more knocked out | whether the affordance was needed |
| S0 | no task reward at all; survival or ecology only | everything |

EMERGENCE DEPTH of a capability in a substrate is the lowest scaffold level
at which calibrated search reaches it. EMERGENCE, used as a claim, means
reached at S2 or below, with the mechanism absent from the initial
population by material tracing, in independent lineages.

### 1.5 Three stores and six relocations

An organism has three stores, declared to the harness with reset rules:

- FAST STATE: reset at every episode boundary by the harness.
- PERSISTENT STRUCTURE: survives episode boundaries within a lifetime.
- GENOME: fixed during a lifetime; changed only by the outer search.

Development is information relocating between the world and these stores.
Six relocations, each named by a verb:

| # | relocation | what moves | scarcity that drives it (a world or regime dial) | affordance it needs | certificate (class excluded) |
|---|---|---|---|---|---|
| T1 | HOLD | past observations into fast state | hidden state; delay between cue and use | writable fast state | best memoryless policy; with N symbols, a score p certifies log2(pN) bits |
| T2 | ADAPT | this life's hidden parameters into fast state | variation between episodes or lives larger than inherited capacity | fast state rich enough for a sufficient statistic | best policy that ignores within-episode evidence |
| T3 | BUILD | acquired information into persistent structure that later computation uses | lifetime information demand above fast-state capacity; fast-state resets | lifetime-writable structure read by computation | best policy carrying nothing across episode boundaries |
| T4 | COMPRESS | stored cases into regularities | storage cost or cap below the number of distinct situations; test items are new combinations | structure sharing; cost accounting | lookup table of the permitted size, on combinations balanced against surface similarity |
| T5 | COMPOSE | regularities into units invoked with arguments | tasks of compositional depth D with a step budget below flat search | mutation-robust addressing; invocation; composition | designed solver without reuse, at the same budget |
| T6 | RECURSE | the building procedure itself into modifiable structure | many learning episodes sharing meta-structure; later families outside the earlier span | learning machinery stored in mutable structure | designed learner with a fixed procedure and fixed hypothesis space |

T1 to T4 have exact or information-theoretic bounds. T5 and T6 are excluded
against designed reference organisms, which is weaker, and is said so
wherever those levels are claimed.

The relocations are coordinates for measurement. They are not a prescribed
developmental order and not a list of mechanisms. This is how the design
stays inside the North Star's "not a predetermined reasoning architecture
or ladder": the measurement is fixed in advance, the mechanism is not.

### 1.6 Words that need a definition before use

| word | operational definition | discriminator |
|---|---|---|
| reasoning | behaviour on new inputs that requires several internal steps over internally held structure | (a) class exclusion of lookup, interpolation and fixed finite-state policies at the stated depth; (b) intervening on an intermediate state changes the outcome as the step structure predicts |
| abstraction | a persistent structure reused across tasks that differ on the surface | (a) one lesion harms at least two surface-distinct tasks; (b) the benefit survives surface scrambling; (c) transplant confers the shared competence |
| sagacity | cost saved on withheld task families per bit of structure carried forward | forward transfer against a naive twin and a wrong-history twin, divided by the bits whose removal changes that transfer; a lookup impostor must score low |
| recursive sagacity | sagacity whose rate of production rises because of what the organism built | section 9, XFER-07 and DEV-05: transplantable gain in acquisition speed on out-of-span families, above a fixed-procedure learner |
| emergence | attainment at scaffold level S2 or below under calibrated search | section 1.4 |
| metacognition | behaviour that depends on the reliability of the organism's own internal state | noise injected into the identified memory carrier raises the opt-out rate in proportion, with stimulus difficulty held fixed (CAUS-07) |
| self-improvement | a within-lifetime rise in learning efficiency caused by the organism's own changes to its learning machinery | lesion of the changed machinery removes the rise; a frozen-procedure twin does not show it |
| cognition | not used as a claim word | use the certified capability and level instead |
| unfamiliar | a mechanism whose signature on qualified probes lies outside the measured reference class of conventional systems | ANTI-05; never "a model could not name it" |

### 1.7 Independence levels

| level | meaning |
|---|---|
| I0 | deterministic replay of the same run (not replication) |
| I1 | new random seeds, same code, same founders |
| I2 | new lineage founders and new world instances, same code |
| I3 | ruler and world independently implemented from the specification by a different author, where possible a different model family, and differentially tested |
| I4 | a different substrate, or an outside party |

### 1.8 Claim ladder

| level | name | evidence required | what may be said |
|---|---|---|---|
| C0 | observation | any logged run | "seen once in cell X" |
| C1 | effect | preregistered; DEMAND and DETECTABILITY present; beats the full baseline ladder; at least 5 independent lineages (I2); effect size with interval | "effect E in cell X" |
| C2 | robust effect | C1, plus an attack round with no surviving impostor, sealed worlds, clean-clone reproduction on a second host | "E holds in X under attack" |
| C3 | mechanism | C2, plus necessity and sufficiency by intervention, a mechanism model that predicts new preregistered interventions, and an I3 ruler; admitted by the operator | "mechanism M produces E in X" |
| C4 | transferable mechanism | C3, plus recurrence in independent lineages or a transplant that confers the function, and transfer to 3 different world families | "M is a reusable primitive across W1..W3" |
| C5 | principle | a quantitative relation that holds in at least 3 substrates and 3 world families, predicted in advance for a new cell, reproduced at I4 | "relation L holds across S1..S3" |
| C6 | architectural principle | a C5 principle used to design a system that reaches a predicted certified gain | "design rule D follows from L" |

The prompt's terms map as: anomaly C0; effect C1 and C2; mechanism C3;
reasoning primitive, developmental primitive and transferable mechanism C4;
architectural principle C5 and C6.

Nulls have their own two levels. N1, certified null: all four certificates,
power at least 0.8 for targets of the stated size, in one cell. N2: N1 in at
least two substrates and two search regimes. Anything less is an apparatus
null and carries its label from section 1.2.

----------------------------------------------------------------------

## 2. Scientific requirements

### SCI-01 [REQUIRED] Four certificates before inference
- Statement: No positive is recorded above C0 without DEMAND and DETECTABILITY for its cell. No null is read as being about the phenomenon without all four certificates and stated power.
- Why: A result says something about the world only if the apparatus could have produced the other outcome. Each certificate removes one way the outcome was fixed in advance.
- Record: T12, T13, T04; Tan 2.5 and 2.6 (organisms that could not perform the phenomenon; nulls capped by construction); Sis E.
- Check: The claim record schema has four certificate fields holding receipt hashes. A script rejects any claim above C0 with an empty required field.

### SCI-02 [REQUIRED] Three-valued verdicts with apparatus labels and counts
- Statement: Every verdict is PASS, FAIL or INDETERMINATE, or an apparatus label from section 1.2, and carries its eligible count and fired count.
- Why: "Nothing fired" and "nothing could have fired" are different facts. A two-valued verdict cannot tell them apart.
- Record: T03, T12, T19; Tit A (the three-valued checks were the strongest machinery found).
- Check: The verdict type is an enumeration in code. A fixture feeds a loader that admits nothing and must get INDETERMINATE, not PASS.

### SCI-03 [REQUIRED] Preregistration with a total, reachable verdict table
- Statement: A confirmatory campaign commits its hypothesis, cells, rulers, sample sizes and verdict table before data. The table assigns exactly one verdict to every possible outcome, and every verdict is shown attainable by running the whole pipeline on synthetic organisms that span the outcomes.
- Why: A rule fixed after the data fits the data. A table with a gap or an unreachable branch decides the result before the run.
- Record: T11 (17-minute amendment after exposure); T12 (IQ-NULL table did not partition outcomes; verdicts void before generation one); Tit A (control-first generator cut instrument failures from 6 of 16 to 0 of 8, reported).
- Check: The runner refuses to start unless the preregistration commit is an ancestor of the code commit and the attainability receipt lists one synthetic case per verdict.

### SCI-04 [REQUIRED] Claim ladder with ceilings
- Statement: Every claim has a level from section 1.8 and may be worded only as that level allows. Promotion to C3 or above is an operator act. Demotion on failed replication is automatic.
- Why: Attractive results climb by narrative unless each step has a price fixed in advance.
- Record: T02, T18 (corrections that never reached the headline); Tan 2.1 (labels outran mechanisms).
- Check: Claims live in a registry with level, evidence ids and wording template. A lint fails any document that states a registered claim above its level.

### SCI-05 [REQUIRED] Known-law recovery before novel claims
- Statement: Before a new instrument chain supports any claim, it recovers at least two results whose answer is known from theory, end to end (for example the memory bound of section 1.5 T1, and a Bayes-optimal policy on a small task family).
- Why: Qualifying each ruler does not qualify the chain. A pipeline that cannot rediscover a known law cannot be trusted on an unknown one.
- Record: T04 ("known truths calibrate the pipeline" never called the battery it was cited for); Sis C12 (a 1990s result as a positive control for a modern search stack was never run).
- Check: A recovery campaign with a preregistered tolerance exists and passed for the chain's current versions.

### SCI-06 [REQUIRED] Quantitative predictions and scored forecasts
- Statement: Every confirmatory campaign states a numeric prediction and what would falsify it, and logs a probability for each verdict. Forecasts are scored after the run.
- Why: A program that cannot predict its own experiments has not learned from them. Forecast skill is a direct measure of understanding.
- Record: T11 (claims strengthened before the test); Tit T08 (priority forecasts scored worse than a constant, and nobody was tracking it until one seat did).
- Check: The yield table (PHASE3_META_ANALYSIS.md, scientific-yield model) carries a running Brier score against a constant-forecast baseline.

### SCI-07 [REQUIRED] Laws are cross-substrate, predicted in advance
- Statement: A statement is called a law or principle only at C5.
- Why: One substrate, one author and one mutation operator agreeing with themselves is one observation.
- Record: Sis 1 ("N seats agree" meant one substrate agreeing with itself); Tan 2.9; T17.
- Check: The claim registry refuses level C5 without three substrate ids, three world-family ids and a dated prediction.

### SCI-08 [HIGH VALUE] The transition map is the primary scientific object
- Statement: The main product is a map of where each relocation appears as demand, affordance, pressure and search dials vary, with uncertainty. Individual specimens are evidence for the map.
- Why: Maps give laws and bounded negatives. Specimens give anecdotes, and the record shows how specimens mislead.
- Record: Tan 2.8 (surviving positives were instrument positives); Tit C.
- Check: Each campaign names the map cell it fills.

### SCI-09 [REQUIRED] Defined words only
- Statement: The words in section 1.6 appear in claims only with a link to the certificate that licenses them.
- Why: Naming stood in for specification throughout the record.
- Record: Tan 2.1 and section B ("tensor", "self-modifying", "RSI", "executable matter").
- Check: A lint scans claim records and reports for the listed words without a certificate link.

### SCI-10 [REQUIRED] Declared unit of replication and independence level
- Statement: Every claim states its unit of replication (lineage founder, world instance, substrate) and its independence level. Intervals are computed over that unit.
- Why: Counting correlated rows as independent manufactures confidence.
- Record: T10 (pseudo-replication; seed-level SE where cells vary, 52 times wider when fixed); Tan D11, D12; Sis D11 (replay counted as replication).
- Check: The analysis code takes the unit as a required argument and clusters on it.

### SCI-11 [REQUIRED] Exploration and confirmation are separate
- Statement: Exploratory runs need no preregistration and can produce only C0. Anything above C0 comes from a confirmatory campaign on fresh seeds and sealed worlds.
- Why: Exploration is how questions are found. It is not how they are answered.
- Record: T09 (winner's curse, 12 draws); T11.
- Check: Run receipts carry a mode field. The claim registry accepts only confirmatory receipts above C0.

### SCI-12 [EXPERIMENTAL] Re-test a few historical signals in the new apparatus
- Statement: A small number of old signals that map onto a Phase 3 question are re-run under the four certificates. The old record is not otherwise re-scored.
- Why: Most old cells lack S, W or R, so a full re-scoring would mostly restate the crawl at real cost. A few old geometries are cheap, decisive test cases.
- Record: Sis C (twelve signals worth revisiting); Tan C.
- Check: Each re-test is an ordinary preregistered campaign. None is cited before it runs.

### SCI-13 [REJECTED] Observe-and-interpret campaigns
- Statement: Do not run a substrate and look for interesting phenomena as the route to claims.
- Why: This is the loop that produced the record: the apparatus's capacity to reveal was never established first.
- Record: Tit C and D; Tan 4.2.
- Check: Covered by SCI-01 and SCI-11.

### SCI-14 [REJECTED] Novelty as a verdict or an objective
- Statement: Novelty and alienness are never verdicts, never fitness terms and never admission criteria.
- Why: The record shows the instrument failing both ways, and selecting for strangeness rewards noise.
- Record: T15; Tit 4.
- Check: ANTI-02 and ANTI-06.

----------------------------------------------------------------------

## 3. Organism requirements

### ORG-01 [REQUIRED] One organism protocol for every substrate
- Statement: Every substrate implements the same interface: birth from a genome and seed; step on an observation returning an action and a cost; optional internal steps with cost; exact snapshot and restore; a state partition listing named components with their store (section 1.5) and granularity; a genome with a size in bits.
- Why: Certificates, interventions and comparisons across substrates need one way in.
- Record: Sis 1 (shared substrates were consumed ad hoc); Ixi 5 (per-seat components, not shared).
- Check: A conformance suite runs every substrate through the protocol, including a snapshot-restore-replay equality test.

### ORG-02 [REQUIRED] Three stores under harness control
- Statement: The harness, not the organism, resets fast state at episode boundaries, and can reset, lesion, swap or add noise to any declared state component.
- Why: Relocations are defined by where information sits. That is only measurable if the harness controls the stores.
- Record: Tan E (tasks never rewarded retention across trials); Sis C2 (zero-register initialisation used as a free constant).
- Check: A designed organism that hides information in an undeclared component must be caught by the reset-equivalence test: behaviour after a declared full reset equals behaviour at birth.

### ORG-03 [REQUIRED] Minimal affordances, present and individually switchable
- Statement: At least one substrate provides all of the following, each with an off switch: (a) writable fast state; (b) lifetime-writable persistent structure that computation reads or executes; (c) state-dependent routing; (d) composition, including invoking stored structure with arguments; (e) addressing that stays valid when structure is inserted or deleted; (f) internal steps that do not act on the world; (g) creating, deleting, copying and modifying structure; (h) cost for time and for storage.
- Why: These are the affordances the six relocations need (section 1.5). They are what a computer needs to modify itself under cost, and they name no cognitive faculty. Switches turn "which affordance is necessary" into an experiment.
- Record: Tan 4.1 (no organism had hierarchy, binding and memory together); Tan F; Sis A5.
- Check: For each affordance a designed organism uses it and gains from it (EXPRESSIBILITY), and loses the gain when it is switched off.

### ORG-04 [REQUIRED] The learning machinery is inside the organism
- Statement: For any test of BUILD or above, whatever writes persistent structure is itself part of the organism's mutable structure or genome. Where a fixed external rule is supplied, the cell is labelled scaffold level S3 or above.
- Why: If the improver is fixed code outside the organism, improvement of the improver is impossible by construction.
- Record: Tan 3.7 and E (a fixed improver made the "no" close to a theorem about the setup).
- Check: The substrate's manifest lists every piece of code that can write persistent structure and whether the organism can alter it.

### ORG-05 [REQUIRED] Capacity margin
- Statement: The positive control for a capability fits within a stated fraction of the substrate's size limits (default: half), so search has room.
- Why: A substrate that can only just hold the capability makes every null ambiguous between "absent" and "no room".
- Record: T13; Sis E2.
- Check: The EXPRESSIBILITY receipt records plant size against the caps.

### ORG-06 [REQUIRED] No named cognitive modules as built-ins
- Statement: The physics contains no working-memory module, planner, attention block, episodic buffer or curiosity bonus. Any of these may appear only as a labelled knock-in contrast at scaffold level S3 or above.
- Why: Building the familiar architecture in forecloses finding another, and makes "it used working memory" a statement about the designer.
- Record: Tit T15, T24; tracked doctrine HARD-2.
- Check: The substrate manifest is reviewed against this list; knock-ins carry the S-level in their cell id.

### ORG-07 [REQUIRED] At least two unlike substrates plus a familiar reference
- Statement: Before any statement is made about substrates in general, it has been tested in at least two substrates of different computational kind and in a conventional trained system.
- Why: Substrate-general statements need more than one substrate. The conventional system says what familiar machinery does on the same probes.
- Record: Sis 1; Tan 2.9.
- Check: SCI-07.

### ORG-08 [REQUIRED] Total, deterministic, integer semantics
- Statement: Every genome decodes to a valid organism. Physics uses integers only. Randomness comes from a counter-based generator keyed by seed, lineage, tick and purpose.
- Why: Totality keeps variation from being mostly lethal. Integer physics makes replay exact across hosts.
- Record: Tan 4.4 and A (bit-exact oracles and cross-host replay were the strongest positives); T10 (a float threshold decided a verdict).
- Check: A golden trace reproduces bit for bit on a second host.

### ORG-09 [REQUIRED] Information accounting in bits
- Statement: Genome size, persistent structure in use and fast-state size are reported in bits for every organism and every stage.
- Why: Sagacity, the genome bottleneck and compression are statements about bits.
- Record: Tan 1 (organisms of 1 to 1024 floats; the one-float specimen).
- Check: Receipts carry the three sizes.

### ORG-10 [HIGH VALUE] State partition at several granularities
- Statement: The state partition exposes components at the levels primitive, motif, circuit and whole store, each with lesion and transplant operators.
- Why: A capability may be carried at a scale above single instructions.
- Record: PHASE3_CHALLENGES.md 2a; Sis A8 (carrier attribution to edges and cycles).
- Check: A designed organism with a known multi-part circuit is localised at the circuit level.

### ORG-11 [EXPERIMENTAL] Several organisms in one world
- Statement: Communication, competition and cooperation between organisms.
- Why: Social pressure may drive some relocations. It also removes exact certificates, so it comes after single-organism levels are certified.
- Record: Tan F.
- Check: Admitted only with a best-response certificate (WLD-13).

### ORG-12 [EXPERIMENTAL] Reading its own learning code as data
- Statement: The organism can inspect, not only alter, the structure that implements its learning.
- Why: It may be needed for RECURSE. It may also only add search space.
- Record: Tan 4.1 (self-reference appeared only as overwrites).
- Check: An affordance switch like any other in ORG-03.

### ORG-13 [REJECTED] Organisms whose competence is supplied
- Statement: No claims about reasoning from organisms that order hand-written solvers, attach a learned scalar to a fixed policy, or have no adaptive part.
- Why: Such a cell cannot express the phenomenon.
- Record: Tan 2.5; Sis E2.
- Check: EXPRESSIBILITY fails for them.

----------------------------------------------------------------------

## 4. Developmental requirements

### DEV-01 [REQUIRED] A lifetime has structure
- Statement: A lifetime is a sequence of episodes with harness-enforced fast-state resets, a persistent store and a recorded developmental age.
- Why: Without episode boundaries BUILD cannot be told from HOLD.
- Record: Tan E (lifetimes shorter than learning time; i.i.d. trials).
- Check: ORG-02.

### DEV-02 [REQUIRED] Development and outer search are separate switches
- Statement: Within-lifetime change and across-lifetime search can each be turned off without the other.
- Why: Otherwise "development did it" and "more search did it" cannot be separated.
- Record: PHASE3_CHALLENGES.md 4a and 4g.
- Check: The frozen-development arm runs in every developmental campaign.

### DEV-03 [REQUIRED] Capacity and realisation are measured separately
- Statement: Realisation is the certified level now. Capacity is the certified level after a standard exposure from a standard start within a stated budget.
- Why: An organism that scores low and develops fast is a different find from one that scores high and cannot change.
- Record: PHASE3_CHALLENGES.md 4e.
- Check: Both numbers appear in the frontier table.

### DEV-04 [REQUIRED] The developmental control set
- Statement: Any developmental claim includes: a same-compute direct arm (final world only), a shuffled-order curriculum arm, a frozen-development arm, a wrong-history twin (equal experience on unrelated families), and the constant and lookup baselines at every stage.
- Why: These separate curriculum from compute, order from exposure, development from parameter change, and specific history from general maturation.
- Record: PHASE3_CHALLENGES.md 4g (the first three; adopted from it); T08.
- Check: The preregistration template has the five arms as required fields.

### DEV-05 [REQUIRED] Forked-clone designs
- Statement: Developmental effects are measured on exact clones forked from a snapshot and given different treatments: continue, lesion a structure, receive a transplant, receive the wrong history.
- Why: Software organisms allow what no biological study can: identical individuals differing in one thing. Not using it wastes the main advantage.
- Record: Tan 4.4 (exact twins were the highest-resolving instruments).
- Check: Fork receipts show identical snapshot hashes before treatment.

### DEV-06 [REQUIRED] The trajectory is the measured object
- Statement: Snapshots are kept at stage boundaries. Each stage change records the structural difference, where the new capability is carried, whether it persists after its task is withdrawn, whether another task reuses it, and the saving on the next stage.
- Why: A final score cannot distinguish building from being built.
- Record: PHASE3_CHALLENGES.md 4d.
- Check: The stage record schema has these fields.

### DEV-07 [REQUIRED] Scaffold level on every cell
- Statement: Every cell states its scaffold level (section 1.4) and lists what was designed.
- Why: "Emerged" is meaningless without saying from what.
- Record: Sis D2, D3 (world-made copies counted as organism copies; construction mistaken for heredity); T07.
- Check: Cell ids carry the level. Seeded content is traced (PROV-10).

### DEV-08 [HIGH VALUE] Genome bottleneck and variance spectrum as dials
- Statement: Genome capacity and the timescale at which each world parameter varies (within episode, within life, across lives, never) are dials.
- Why: Information settles in the slowest store whose timescale and capacity fit it. These two dials decide what must be built in life and what can be inherited.
- Record: Tan E; Sis E7.
- Check: A recovery campaign shows a parameter moving from genome to persistent structure when its variation moves from "never" to "across lives".

### DEV-09 [HIGH VALUE] Storage rent as the compression dial
- Statement: Persistent structure costs a rent per bit per tick, paid from earned resource, and the rent is a dial.
- Why: With free storage and no novelty, lookup is optimal and nothing compresses.
- Record: Tan D1 to D3 (memorisation and free economies scored well).
- Check: The lookup impostor wins at zero rent and loses above a threshold.

### DEV-10 [EXPERIMENTAL] Self-ordered curriculum
- Statement: The organism chooses its next world.
- Why: Possibly part of RECURSE. Unproven.
- Record: none.
- Check: Compared against the staircase curriculum at equal compute.

### DEV-11 [EXPERIMENTAL] Offline phases
- Statement: Periods with internal steps and no world input.
- Why: Consolidation may need them. It may also happen without them.
- Record: none.
- Check: An affordance switch.

### DEV-12 [REJECTED] Final score as the measure of development
- Statement: Do not answer a developmental question with an end-of-run score alone.
- Why: DEV-06.
- Record: PHASE3_CHALLENGES.md 4d.
- Check: DEV-06.

----------------------------------------------------------------------

## 5. World requirements

### WLD-01 [REQUIRED] One world protocol; hidden state stays hidden
- Statement: Every world implements one interface with integer physics and keyed randomness. The organism receives the observation channel and nothing else. Scoring runs outside the organism's process.
- Why: The most common false positive in the record is the answer travelling inside the measurement.
- Record: T01 (nine independent instances).
- Check: WLD-05.

### WLD-02 [REQUIRED] A demand certificate for every claim-bearing world
- Statement: Each world family used for claims carries, for every restricted class it is used to exclude, an exact optimum or a proven upper bound, with the proof or the enumeration receipt.
- Why: World size says nothing about what a world requires. A bound does.
- Record: Tan 4.2 (no world demanded more than lookup or small finite-state control); Sis E1.
- Check: A solver receipt per bound; an independent second solver agrees (WLD-11).

### WLD-03 [REQUIRED] The baseline ladder ships with the world
- Statement: Before any organism runs, the world has scores for: constant action, majority action, best memoryless policy, best small finite-state or window policy, best non-adaptive policy, lookup of the permitted size, a same-class batch estimator tuned on the data, and the label's own definition written as a rule with no parameters. The runner refuses to score an organism in a world without them.
- Why: The cheap baseline arrived after the data every time it mattered.
- Record: T08; Tan 2.4 and G2 (a one-float running mean; a post-data batch fit beating all nine promoted specimens).
- Check: The scoring call requires a ladder hash.

### WLD-04 [REQUIRED] Demand is dialled, one axis at a time
- Statement: Each world family exposes dials that raise one demand while holding the others fixed: bits to hold, delay, bits to identify, evidence per observation, volatility, lifetime information, storage cap, novelty of test combinations, compositional depth, number of learning episodes.
- Why: A threshold on a controlled axis is a measurement. A score in a fixed world is not.
- Record: Sis F1; Tan G1.
- Check: Moving one dial changes its own bound and leaves the others unchanged, by the certificate.

### WLD-05 [REQUIRED] Leak probes and twin worlds
- Statement: Each world is tested for leaks before use: a probe trained to predict the hidden answer from the observation stream before the answer is legitimately available must be at chance; payload fields are scanned for label-to-answer mappings. Each world has an absence twin (the structure removed) and a surface-scrambled twin (same structure, permuted encoding).
- Why: Field-equality leak tests miss label mappings. Twins give a negative control on the world side.
- Record: T01; Tan 9 item 6 (a payload field mapped to the answer; the leak test checked equality only).
- Check: A planted one-character leak is caught. An organism that gains in the absence twin is flagged.

### WLD-06 [REQUIRED] Train, selection and sealed worlds
- Statement: Worlds are split into training, selection and sealed test sets by commit-reveal seeds. Sealed worlds are generated after the freeze. Use of a sealed world for selection burns it.
- Why: Selecting on the evaluation set inflates every number, including the controls.
- Record: Sis D6 (champion selected on the held-out set, verified in source); T09.
- Check: The search process has no access to sealed seeds. An access log exists and is checked.

### WLD-07 [REQUIRED] Shortcut audit before admission
- Statement: Before a world is admitted, an automated search over cheap policies (small programs, small automata, decision lists) attacks each bound. The world is admitted only if none beats its bound, and the specification is frozen only after its controls attain every verdict.
- Why: A bound proved on paper can be wrong in code. The cheapest non-degenerate cheat must be tried, not imagined.
- Record: T04 (only the dumbest cheat tested); Tit T07 (signals lived where worlds were degenerate); Tit A (control-first generator).
- Check: The admission receipt lists the attack budget and the best attacker's score against each bound.

### WLD-08 [REQUIRED] The capability must pay
- Statement: A reference policy with the capability beats the best restricted policy by a stated margin (default: at least four times the ruler's minimum detectable effect), net of the capability's cost.
- Why: If the capability does not pay, its absence is rational.
- Record: Sis E7 (costs from generation 0 killed organisms before a foothold); Tan E.
- Check: The DEMAND certificate records the margin.

### WLD-09 [REQUIRED] Coverage of the six relocations and of doubt
- Statement: There is at least one world family per relocation, and one family for uncertainty: misleading early evidence, costly observation, costly irreversible commitment, an opt-out action, changing rules.
- Why: A relocation with no world that demands it cannot be studied.
- Record: Tan 4.2.
- Check: The world registry maps families to relocations.

### WLD-10 [HIGH VALUE] Unauthored worlds
- Statement: A share of worlds is sampled from generic generators (small random decision processes and generative programs), with demand vectors computed, and selected by those vectors.
- Why: Authored worlds encode the author's idea of what reasoning needs. Sampled worlds with computed demand do not.
- Record: Tit T15 (familiarity to the model stood in for novelty); T24.
- Check: The share is declared per campaign.

### WLD-11 [HIGH VALUE] Two implementations of every claim-bearing world and solver
- Statement: Each claim-bearing world and its bound solver exist in two implementations written separately from the specification, agreeing on random traces.
- Why: A bug in a world or a solver manufactures science, and same-author review does not find it.
- Record: T17 (auditor imported the producer's generator and detector); Tit 2.6.
- Check: Differential test receipts.

### WLD-12 [HIGH VALUE] Construct validity
- Statement: The demand profile measured in certified small worlds is tested for whether it predicts success in richer, uncertified worlds.
- Why: If it does not, the certified worlds measure something irrelevant.
- Record: none in the record; this is the main risk of my own design.
- Check: A preregistered prediction from profile to performance on a transfer set.

### WLD-13 [EXPERIMENTAL] Social worlds with best-response certificates
- Statement: Small games with exact best responses and a level-of-recursion demand.
- Why: A possible seventh axis. Exactness is harder to keep.
- Record: Sis A6 (exact game solving exists as a method).
- Check: As WLD-02.

### WLD-14 [EXPERIMENTAL] World generators that co-evolve with organisms
- Statement: Open-ended world generation driven by organism performance.
- Why: The adaptive staircase covers curriculum for one organism. Open-ended co-evolution may add stepping stones, and removes certificates unless generation stays inside certified families.
- Record: North Star (POET as a reference arm).
- Check: Only inside certified families.

### WLD-15 [REJECTED] Size as evidence of depth
- Statement: World dimensions are never cited as evidence of demand.
- Why: A large world solved reactively is shallow.
- Record: Tan 3.5 (16384 squared reproduced the statistics of 256 squared).
- Check: WLD-02.

### WLD-16 [REJECTED] Reasoning claims with no environment
- Statement: No claim about reasoning from a system with no action-perception loop.
- Why: Nothing demands anything of it.
- Record: Tan 4.2 (several engines had no environment at all).
- Check: DEMAND fails.

### WLD-17 [REQUIRED] The readout is part of the certificate
- Statement: What is scored (final state or ever reached, which ticks, which ties) is fixed in the world certificate.
- Why: Readout choice decided verdicts more than horizon did.
- Record: Sis E8.
- Check: The certificate includes the readout rule; the scorer takes it from there.

----------------------------------------------------------------------

## 6. Pressure and search requirements

### SRCH-01 [REQUIRED] The search regime is a declared, varied factor
- Statement: Every cell names its search regime and version. "Not found" is not read without at least two regimes, one of which accepts neutral moves and keeps a population.
- Why: A search policy can be mistaken for a landscape.
- Record: Sis D5 (a greedy walk that structurally rejected neutral children, verified in source); Sis 3 item 4.
- Check: The null record lists regimes.

### SRCH-02 [REQUIRED] Search-power curve
- Statement: For each substrate and regime, targets are planted at graded distances from the founders and the recovery rate is measured against budget. Every null reports the power for a target of the plant's size.
- Why: This is the search's equivalent of statistical power. Without it "unreached" and "absent" are the same word.
- Record: T12; Tan 2.6 and E (in-space plants at 0.978 and 0.850 that search never found; a five-instruction target never reached).
- Check: REACH certificate with the curve and its confidence band.

### SRCH-03 [REQUIRED] Needle size and random-hit rate
- Statement: For each planted target: minimum edits from the founders, and the rate at which random organisms hit it.
- Why: They set the scale for budgets and for what "found" means.
- Record: Tan G3 ("the search reached a short program already in the grammar").
- Check: Fields in the REACH certificate.

### SRCH-04 [REQUIRED] Budgets in evaluations, against the needle
- Statement: A campaign states its budget in organism lifetimes and compares it with the needle estimate. Throughput is measured, not assumed.
- Why: The record's budgets were small against the targets, and nobody had the comparison.
- Record: Tan E (population 96 by 36 generations); Sis E3.
- Check: The preregistration has both numbers.

### SRCH-05 [REQUIRED] No selection on evaluation worlds
- Statement: Search sees training worlds. Model selection sees selection worlds. Reported numbers come from sealed worlds.
- Why: WLD-06.
- Record: Sis D6.
- Check: WLD-06.

### SRCH-06 [REQUIRED] Independent lineages
- Statement: Replication is over unrelated founders (default: at least 5). Founder concentration in any pooled result is reported.
- Why: Mutants of one founder are one observation.
- Record: Tan 2.9 (181 admitted worlds were mutants of 13 founders; 6 lineages behind 50 rows).
- Check: SCI-10.

### SRCH-07 [REQUIRED] Pressures are dials with their own positive control
- Statement: Each pressure (task diversity, lifetime length, rate of change, storage rent, genome cap, competition) is a dial. Before use, a designed organism that should win under the pressure is shown to win, and one that should lose is shown to lose.
- Why: A pressure that does not select is decoration.
- Record: Tit T13 (pressures never testable); Tan D10 (a shaping bonus paid codes at chance).
- Check: Pressure qualification receipt.

### SRCH-08 [HIGH VALUE] The optimiser is a factor
- Statement: Where possible the same cell is searched by blind structural variation, by a population method with a diversity archive, by model-guided proposals, and by gradient methods when the substrate allows.
- Why: What one optimiser cannot reach another may. A capability that appears under only one is a fact about reach.
- Record: Sis C7 (crossover crossed a valley that single steps did not, in one representation only).
- Check: Cell ids carry the optimiser.

### SRCH-09 [HIGH VALUE] An archive keyed by certified profile
- Statement: The population archive keeps the best organisms per region of the certified demand profile.
- Why: Stepping stones toward one relocation are often specialists in another.
- Record: Sis C10 (exaptation gradient killed on a yield rule).
- Check: Archive receipts.

### SRCH-10 [REQUIRED] Costs must not close the door
- Statement: Any cost applied from the first generation is shown, by a designed organism, to leave a viable path to the capability.
- Why: Costs applied on a flat landscape kill organisms before selectable structure forms.
- Record: Sis E7.
- Check: Part of SRCH-07.

### SRCH-11 [REQUIRED] Seeded content is labelled and traced
- Statement: Any designed or transplanted content in a population is recorded, and its material descendants are traced.
- Why: Seeded and transplanted phenomena were repeatedly reported as endogenous.
- Record: Sis 3 items 1 to 3 (26 "spontaneous replications" were all transplants).
- Check: PROV-10.

### SRCH-12 [EXPERIMENTAL] Survival-only pressure
- Statement: Scaffold level S0: no task reward.
- Why: It is the North Star's end state. It is also where nulls are least interpretable, so it comes last.
- Record: North Star.
- Check: Only in cells whose S2 result is already certified.

### SRCH-13 [REJECTED] Scalar fitness alone; unpriced shaping
- Statement: No developmental campaign reports scalar fitness without the demand profile. No shaping term without an arm that removes it.
- Why: A shaping term can pay for something other than the task.
- Record: Tan D10.
- Check: Preregistration template.

----------------------------------------------------------------------

## 7. Measurement requirements

### MEAS-01 [REQUIRED] A datasheet for every ruler
- Statement: Each ruler has a datasheet: what it measures, units, range, sensitivity curve and minimum detectable effect, false-positive rate with interval, saturation zones, the envelope inside which it is valid, version hash, independence level.
- Why: A ruler without known error rates is a probe.
- Record: Tit 2.1 (30 of 146 instruments shown able to detect, 56 partly, 60 not); T04.
- Check: A verdict outside the envelope is returned as RULER_NOT_QUALIFIED by the ruler itself.

### MEAS-02 [REQUIRED] Qualification is a gate in code
- Statement: A campaign cannot start unless its rulers have a current qualification receipt: calibration set sorted, channel test passed, a fire test for every control.
- Why: The base role's rule on negative, positive and cheat controls is prose. Prose was not enough.
- Record: Tit 2.3 and B ("the base-role test checks structure, not controls"); T03.
- Check: The runner verifies receipt hashes. Mutation tests in the kernel's suite break each control and expect a failure.

### MEAS-03 [REQUIRED] Capability is reported as a certified level
- Statement: The headline number is the level certified by class exclusion with its interval (for example "HOLD 3.2 bits, 95% lower bound 2.9"), not raw accuracy.
- Why: Raw scores invite comparison with nothing.
- Record: T08; Tan 2.4.
- Check: The report template.

### MEAS-04 [REQUIRED] Trivial responders beside every headline
- Statement: Constant, majority, payload-reader and lookup responders are scored on the same population and denominator and printed beside the result.
- Why: A constant answer beat 120 of 122 tools once.
- Record: T05; Tit E.
- Check: WLD-03.

### MEAS-05 [REQUIRED] One named test per distinction
- Statement: The measurement system separates each of the following by a named test: memorisation and lookup (new combinations, WLD-04); finite-state tricks (state-count bounds); reactive policies (memoryless bound); incidental recurrence (absence twin); reusable structure (shared lesion); transfer (sealed families, XFER-01); abstraction (scramble invariance, XFER-02); causal mechanism (CAUS-01); learning to learn (savings against a fixed learner); developmental restructuring (DEV-06); recursive improvement (XFER-07).
- Why: Each of these was confused with a neighbour somewhere in the record.
- Record: Tan 4.4 (rulers had high resolving power for determinism and low for the intended cognition).
- Check: The ruler registry maps tests to distinctions; none is empty.

### MEAS-06 [REQUIRED] Sealed ruler versions
- Statement: A verdict records the ruler's hash. Any change to the ruler after exposure marks dependent verdicts STALE automatically.
- Why: Post-exposure amendments were caught only by audit.
- Record: T11; T23.
- Check: A fixture changes a ruler and expects STALE.

### MEAS-07 [REQUIRED] Exact decision arithmetic
- Statement: Verdict decisions use integers or rationals. Ties and thresholds are specified. A second, independent evaluator recomputes every decision.
- Why: 0.2 minus 0.1 was less than 0.10 in floating point, and it decided a verdict.
- Record: T10.
- Check: The shadow evaluator agrees on every preregistered decision.

### MEAS-08 [REQUIRED] Power stated before the run
- Statement: The preregistration states the minimum detectable effect at the planned sample size. A gate closer to the expected value than its own standard error is not a gate.
- Why: Underpowered gates killed real small effects and passed unreal large ones.
- Record: T10.
- Check: Preregistration template; the runner computes the planned interval width.

### MEAS-09 [REQUIRED] Every judged row carries its context
- Statement: Denominator, exclusions, ruler version, and the identity of any model involved are on every judged row.
- Why: Counts over the wrong population and unrecorded judges made results unrecoverable.
- Record: T18, T19.
- Check: Schema.

### MEAS-10 [REQUIRED] An anti-calibration set
- Statement: Each kill path is tested on cases that are true but surprising, and its false-negative rate is reported.
- Why: A battery that kills everything looks rigorous.
- Record: Tit E (0 of 4 known truths survived one battery); T10.
- Check: The datasheet has a false-negative rate from this set.

### MEAS-11 [REQUIRED] Verdict authorship is separated
- Statement: The component that generates a record cannot write its verdict. Rulers run in a separate process with write access the generator lacks.
- Why: 99.98% of 658 million records were verdicted by the generator that wrote them.
- Record: T02.
- Check: File and database permissions; a fixture in which a generator tries to write a verdict and is refused.

### MEAS-12 [HIGH VALUE] Thresholds by adaptive staircase
- Statement: Each organism's threshold on each demand axis is found by an adaptive staircase, giving a psychometric curve and a just-noticeable difference for the instrument.
- Why: "High resolution" then has a number: the smallest difference in capability the instrument reliably detects.
- Record: Tan 4.4.
- Check: Designed organisms with known thresholds are recovered within the stated resolution.

### MEAS-13 [HIGH VALUE] Sagacity and savings
- Statement: Forward transfer, savings, and both divided by carried bits (section 1.6).
- Why: The North Star's own definition is about what is carried forward and what it buys.
- Record: North Star, "what this means for a seat's daily choices".
- Check: The lookup impostor scores low; the designed library learner scores high.

### MEAS-14 [HIGH VALUE] Capability per unit of compute
- Statement: Certified level per instruction and per estimated joule.
- Why: It compares substrates on a physical axis and feeds the resource model.
- Record: none.
- Check: Receipts carry the meters (ENRG-01).

### MEAS-15 [REJECTED] Model-judged measurement
- Statement: No model output is a measurement, a score or a verdict.
- Why: Same-model familiarity, prompt steering, refused calls changing denominators, scrubbers erasing content.
- Record: T24, T14, T15.
- Check: ANTI-01.

----------------------------------------------------------------------

## 8. Causal-analysis requirements

### CAUS-01 [REQUIRED] Mechanism claims need executed interventions
- Statement: A mechanism claim (C3) needs necessity by lesion and sufficiency by transplant or interchange, each with a matched control: a lesion of equal size elsewhere, a sham transplant.
- Why: A description of code is not a measurement of what the code does.
- Record: T16 (546 of 549 organs judged by reading; 0 transplants survived).
- Check: The claim registry requires both receipts at C3.

### CAUS-02 [REQUIRED] Exact counterfactual twins
- Statement: Interventions compare two runs with identical seeds that differ in one thing. An intervention counts only if it changed state.
- Why: This is the cleanest causal design available, and it is free in software.
- Record: Tan 4.4, C (interventions that refuse to count unless they changed state).
- Check: Twin receipts show identical hashes up to the intervention tick.

### CAUS-03 [REQUIRED] Interchange across runs that differ in a known latent
- Statement: A component is swapped between two runs that differ in one known hidden variable. Behaviour following the donor is FLIP; unchanged is NO-EFFECT; in between is reported with its rate. The ruler is qualified on designed organisms with known carriers.
- Why: It localises where a variable is carried without needing to read the mechanism.
- Record: Tan A (carrier-swap instruments); T04.
- Check: Known carriers recovered; known bystanders rejected.

### CAUS-04 [REQUIRED] A mechanism model must predict new interventions
- Statement: To reach C3 the proposed mechanism predicts the outcome of interventions not yet run, with at most a stated number of fitted parameters.
- Why: An account that only fits what was seen is a story.
- Record: Tan C (a zero-parameter model fitting 46 of 46 unseen curves is the form to aim at); T11.
- Check: Predictions are committed before the interventions run.

### CAUS-05 [REQUIRED] Lesions can reach the whole candidate circuit
- Statement: A coverage check shows the lesion operator can remove every component of the candidate.
- Why: A lesion design that never removed output nodes hid a third of a carrier.
- Record: T13.
- Check: Coverage receipt.

### CAUS-06 [REQUIRED] Material tracing for heredity and reuse
- Statement: Claims that structure was inherited, copied or reused rest on tracing the material (bytes, cells) from origin, not on labels, slots or locations.
- Why: Label descent over-reported material descent about tenfold.
- Record: Sis D1, D2, D3; T14.
- Check: PROV-10.

### CAUS-07 [HIGH VALUE] Carrier-noise opt-out test
- Statement: In worlds with an opt-out action, noise is injected into the organism's identified memory carrier on some trials, with stimulus difficulty fixed. An organism that opts out more on those trials monitors the reliability of its own state.
- Why: It is a causal test of a functional property that needs no label and has no first-order explanation by stimulus difficulty. It is impossible in animals and cheap here.
- Record: prompt section 7.
- Check: A designed organism with a reliability check passes; one that opts out on stimulus difficulty alone fails.

### CAUS-08 [HIGH VALUE] Reuse matrix
- Statement: Lesion every component against every task and report the matrix.
- Why: Shared rows are reuse. The matrix is generic across substrates.
- Record: PHASE3_CHALLENGES.md 4d.
- Check: Recovered on a designed organism with known sharing.

### CAUS-09 [EXPERIMENTAL] Blind second decomposition
- Statement: A second analyst or model decomposes the same organism without seeing the first decomposition.
- Why: It may show which mechanism descriptions are stable. It is model-mediated, so it sets priority and is never evidence.
- Record: T16 (designed, n = 0).
- Check: Agreement rate reported.

### CAUS-10 [REJECTED] Mechanism labels from reading
- Statement: A reading of code or weights is a hypothesis. It is not recorded as evidence.
- Why: CAUS-01.
- Record: T16.
- Check: CAUS-01.

----------------------------------------------------------------------

## 9. Transfer requirements

### XFER-01 [REQUIRED] Withheld structure, not only withheld seeds
- Statement: Transfer is tested on world families or combinations the organism never met, generated after the freeze.
- Why: New seeds of the same structure test noise robustness.
- Record: Tan 9 (held-out sets were in-distribution after quotienting).
- Check: The generator proves the sealed set is disjoint at the level of structure.

### XFER-02 [REQUIRED] Scramble invariance for abstraction claims
- Statement: The benefit must survive a permutation of the surface encoding that leaves structure intact.
- Why: Otherwise the organism learned the surface.
- Record: T14; Sis D9 (parsers that fit one author's phrasing: 0.60 to 0.067 under a blind author).
- Check: WLD-05 twins.

### XFER-03 [REQUIRED] Transplant with shams
- Statement: A transplant claim compares the donor structure with a random structure of equal size and with a wrong-history donor's structure.
- Why: Two shams once solved what the donor could not.
- Record: Tan 3.7.
- Check: Three arms in the receipt.

### XFER-04 [REQUIRED] Three unlike world families for C4
- Statement: A transferable mechanism transfers across at least three world families that differ in more than parameters.
- Why: SCI-07 at the mechanism level.
- Record: Tit 2.1 (cross-substrate transfer tested for 2 of 146 instruments).
- Check: Claim registry.

### XFER-05 [REQUIRED] Savings against a same-compute direct arm
- Statement: Any saving attributed to prior development is measured against an arm given the same total compute on the target alone.
- Why: DEV-04.
- Record: PHASE3_CHALLENGES.md 4g.
- Check: DEV-04.

### XFER-06 [REQUIRED] Withheld sets are built without the answer in them
- Statement: Validation and test sets are generated by a process that cannot see the planted structure under test.
- Why: A validation set that contains the planted motif selects it back.
- Record: Tan D14.
- Check: The generator for sealed sets takes no input from the treatment.

### XFER-07 [REQUIRED] Out-of-span families for recursion claims
- Statement: A claim of RECURSE needs acquisition gains on families that require something no earlier family required, where a fixed-procedure learner shows no gain by construction, and the gain must transplant: late-built structures placed in a naive clone speed its learning of new families.
- Why: A fixed hierarchical learner already speeds up inside its hypothesis space. Only a gain outside it, carried by built structure, goes beyond learning to learn.
- Record: Tan 3.7 (the improver never changed; what changed was a library that reordered a fixed search).
- Check: Positive control: a designed learner whose procedure adapts. Negative: the same with the procedure frozen. Impostor: memorised solutions to the curriculum.

### XFER-08 [HIGH VALUE] Function re-built in a second substrate
- Statement: A mechanism understood well enough is re-implemented in a different substrate and tested there.
- Why: It is the strongest test of understanding and the entry to C5.
- Record: none.
- Check: The re-implementation is written from the mechanism model alone.

----------------------------------------------------------------------

## 10. Provenance requirements

### PROV-01 [REQUIRED] One receipt schema; engines conform to the index
- Statement: Every campaign emits receipts in one schema: code commit, configuration hash, seeds, versions of world, organism, search and ruler, host, rows with hashes, verdicts with ruler hash, cost meters. The index reads that schema and nothing else.
- Why: An index that needs a hand-written adapter per engine lags, and its lag pushes work back into inference.
- Record: Ixi 2 (8.6 days of lag; 5 engines never registered; a 14-role model harvest to rebuild state from prose).
- Check: A campaign whose receipts fail schema validation does not complete.

### PROV-02 [REQUIRED] Hash repository bytes
- Statement: All hashes are over LF-normalised repository bytes.
- Why: Host-byte hashes were recorded as blob hashes three times.
- Record: T18.
- Check: The existing manifest tool; a fixture with CRLF and LF copies.

### PROV-03 [REQUIRED] No load-bearing artifact in an ignored path
- Statement: Nothing a result depends on lives in a gitignored, host-local or database-only location without a tracked, hashed pointer and a custody statement.
- Why: Ignored outputs were consumed downstream; ledgers were lost; evidence existed on one host only.
- Record: T18; Sis 0.1; Tan 8.
- Check: A test fails if a receipt cites a path that git ignores or does not track.

### PROV-04 [REQUIRED] Append-only records; corrections propagate
- Statement: Records are append-only. A correction is an annotation with a back-link. A retraction marks every claim that cites the retracted evidence.
- Why: Corrections did not reach stale headlines.
- Record: T18 (documents at HEAD still stating retracted results).
- Check: Retracting a fixture evidence id flags its dependants.

### PROV-05 [REQUIRED] Identifiers are unique and never reused
- Statement: Engines, tests, specimens and campaigns have ids that are never reused, and one name means one thing.
- Why: "F33" had four meanings; three instruction sets shared one name; two tenants shared one seat name.
- Record: T18; Sis 0.2; Tan 6.
- Check: Registry uniqueness constraint.

### PROV-06 [REQUIRED] The freeze is provable
- Statement: The runner checks that the preregistration commit precedes the first data commit.
- Why: A plan first committed with its results; a pilot begun ten minutes before its freeze.
- Record: T11.
- Check: SCI-03.

### PROV-07 [REQUIRED] Model identity and steering are recorded
- Statement: Any artifact a model touched records the model id, the prompt hash and every steering field.
- Why: A judge's identity across a three-provider fallback was never recorded; an effect became unrecoverable for lack of steering fields.
- Record: T18.
- Check: Schema.

### PROV-08 [REQUIRED] One writer for results
- Statement: Result rows are written by the runner to a content-addressed store and committed in batches by one process.
- Why: Commit-on-write raced with other git operations and killed workers.
- Record: Ixi inference_dependency_map.md, build table (row persistence: "git races documented"); T18 (ledgers destroyed and recovered).
- Check: No campaign code calls git.

### PROV-09 [REQUIRED] Seeded and endogenous are labelled by tracing
- Statement: Whether content is seeded, transplanted or endogenous is decided by material tracing from the first tick.
- Why: A predicate read a run label and reported 26 spontaneous events that were all transplants.
- Record: Sis 3 item 2.
- Check: A fixture with a transplanted organism under a "spontaneous" label is classified as a transplant.

### PROV-10 [HIGH VALUE] Sealed-world custody
- Statement: Sealed seeds are held by a broker with an access log.
- Why: WLD-06 needs an enforcer.
- Record: Tan 2.8 (sealed-holdout machinery was among the surviving strengths).
- Check: The log shows no access before reveal.

----------------------------------------------------------------------

## 11. Reproducibility requirements

### REPR-01 [REQUIRED] Bit-exact replay across hosts
- Statement: Physics kernels reproduce golden traces bit for bit on a second host.
- Why: It turns "did it run the same" from a judgement into a comparison.
- Record: Tan 2.8.
- Check: Golden fixtures in the suite.

### REPR-02 [REQUIRED] Clean-clone reproduction
- Statement: Any claim at C2 or above reproduces from a fresh clone on a second host with one command.
- Why: Scripts behind headline numbers were never committed.
- Record: T18.
- Check: The reproduction receipt is part of C2.

### REPR-03 [REQUIRED] Replay is not replication
- Statement: Reports state the independence level. I0 is never called replication.
- Why: Frozen counts replayed exactly while independent re-measurement moved them by multiples.
- Record: Sis D11.
- Check: SCI-10.

### REPR-04 [REQUIRED] Independent implementation behind C3
- Statement: The ruler and world behind any C3 claim exist at I3.
- Why: T17 is the record's main independence failure, and reviews by the same model family did not fix it.
- Record: T17; Tit limit 1.
- Check: WLD-11; MEAS-01 records the level.

### REPR-05 [REQUIRED] Validated configuration equals executed configuration
- Statement: The receipt holds the hash of the configuration that ran, and the qualification receipt holds the hash of the configuration that was qualified. They must match.
- Why: A validated renderer differed from the deployed one, and the arms separated at 1.000.
- Record: T23.
- Check: The runner compares them.

### REPR-06 [REQUIRED] Pinned environment
- Statement: Dependencies are locked and recorded.
- Why: Basic, and it was not uniform.
- Record: Ixi E (receipts that did not pin a clean tree).
- Check: Receipt fields; dirty tree refuses to run.

### REPR-07 [HIGH VALUE] External reproduction pack at C4
- Statement: C4 claims ship a pack an outside party can run.
- Why: Internal review is circular.
- Record: PHASE3_CHALLENGES.md 1e.
- Check: PUB-02.

----------------------------------------------------------------------

## 12. Anti-prior requirements

### ANTI-01 [REQUIRED] Three authorities, separated in code
- Statement: Generation proposes candidates. Reality (worlds, rulers, interventions) decides survival. Interpretation describes and proposes experiments. No interpretation output can delete, demote or exclude a candidate.
- Why: The dangerous loop is a model generating, recognising and admitting.
- Record: PHASE3_CHALLENGES.md 3c; T02; T17.
- Check: Write permissions on the archive and verdict tables; a fixture in which an interpretation process tries to demote a candidate and is refused.

### ANTI-02 [REQUIRED] Admission and allocation use certificate numbers only
- Statement: What gets compute next is decided from certified levels, effect sizes and costs. No description, name or familiarity judgement is an input.
- Why: Unfamiliar mechanisms are rejected as noise when a model's recognition is in the path.
- Record: T15.
- Check: The allocation function's inputs are typed and exclude text.

### ANTI-03 [REQUIRED] The unclassified-but-certified queue
- Statement: A candidate that passes behavioural and causal gates and that models cannot classify is raised in investigation priority. Failing to classify is never counted as evidence.
- Why: Both halves are needed. Without the first, the unfamiliar is discarded. Without the second, noise is rewarded.
- Record: PHASE3_CHALLENGES.md 3a, 3b.
- Check: Entry to the queue requires C2.

### ANTI-04 [REQUIRED] A declared share of blind variation
- Statement: Wherever model-guided generation is used, a declared share of evaluations (default: half) comes from structural variation that uses no model.
- Why: It keeps search mass outside the model's prior, and makes the comparison in ANTI-07 possible.
- Record: T24.
- Check: Receipts split evaluations by generator.

### ANTI-05 [REQUIRED] A measured reference class
- Statement: Conventional trained systems are run through the same worlds, rulers and intervention probes. Their signatures define the reference class. "Unfamiliar" means outside it.
- Why: It replaces "a model could not name it" with a measured distance.
- Record: T15 ("familiar" meant familiar to one model).
- Check: Reference signatures exist for every probe used in an unfamiliarity statement.

### ANTI-06 [REQUIRED] Prior art after validation, with measured recall
- Statement: Prior-art retrieval runs only after C2, is recorded as an outcome, and its recall is measured on planted known mechanisms. A failed lookup is not a miss. No match is not novelty.
- Why: The record erred both ways: no-precedent lists from unlogged searches, and known results counted as anomalies.
- Record: T15; Tit 4 (HARD-2 pushed against literature comparison).
- Check: A recall figure on the planted set accompanies every prior-art statement. Note: this narrows doctrine HARD-2 and needs an operator ruling (OPEN_QUESTIONS).

### ANTI-07 [HIGH VALUE] Generator-prior divergence experiment
- Statement: In one cell, model-guided generation and blind variation are run to the same certified level, and the signatures of what they find are compared.
- Why: It answers the epistemic-escape question by measurement.
- Record: prompt section 8.
- Check: Preregistered; the outcome is informative either way.

### ANTI-08 [REQUIRED] Familiar architectures are reference arms
- Statement: Transformers, backpropagation, standard reinforcement learning and conventional modules are run as controls and may be candidate substrates under the same certificates. They are not the default organism.
- Why: Banning the strongest known optimiser would be a prior of its own. Defaulting to it is the gravity the program exists to resist.
- Record: prompt section 23; North Star (reference arms).
- Check: Cell ids mark reference arms.

### ANTI-09 [EXPERIMENTAL] Multi-model disagreement panel
- Statement: Several model families describe a certified candidate; the pattern of agreement sets investigation priority. The panel is calibrated on planted familiar and planted unfamiliar mechanisms first.
- Why: It may expose shared priors. It is a model-based classifier of the kind the record shows failing.
- Record: PHASE3_CHALLENGES.md 3d; T17.
- Check: Calibration rates published before use.

### ANTI-10 [REJECTED] A model as detector or judge of novelty
- Statement: No model decides whether something is new.
- Why: An instrument that could not output "unfamiliar" reported zero unfamiliar items as a result.
- Record: T04, T15.
- Check: ANTI-02.

----------------------------------------------------------------------

## 13. Compute requirements

### COMP-01 [REQUIRED] Compiled integer kernels, CPU first, throughput measured
- Statement: World and organism physics run in compiled integer kernels. Each kernel publishes measured throughput on the reference host. Starting target for a register-machine substrate: at least 100 million organism instructions per second on M1 (the measured toy ceiling is about 5 billion).
- Why: Search budgets in the record were limited by implementation, not hardware.
- Record: Tan 4.5 (budgets of thousands to a few million evaluations on single hosts).
- Check: A benchmark receipt per kernel version.

### COMP-02 [REQUIRED] Campaigns are deterministic batch jobs
- Statement: A campaign is a resumable, checkpointed job that runs to completion with no model and no human in the loop.
- Why: Long autonomous deterministic runs are the cheapest resource the program has.
- Record: Ixi 7 (deterministic machinery waited for a session to trigger it).
- Check: A campaign killed mid-run resumes to the same result hash.

### COMP-03 [REQUIRED] GPU use is justified per campaign
- Statement: A campaign that uses the GPU states why and gives the CPU cost of the alternative.
- Why: The GPU is one device and electricity is a cost.
- Record: Tan 3.5 (scale demonstrations that reproduced small-lattice statistics).
- Check: Preregistration field.

### COMP-04 [REQUIRED] One queue and one lease mechanism
- Statement: All campaigns go through one execution queue with one resource-lease mechanism.
- Why: Eight queue and lease mechanisms coexisted, so no one place said what was running.
- Record: Ixi 5 (at least 8 queue and lease mechanisms).
- Check: Campaign code has no other way to start work.

### COMP-05 [REQUIRED] Budget caps enforced by the runner
- Statement: Wall time, CPU hours and GPU hours are capped per campaign and enforced.
- Why: A cap that is only written down is a wish. Runs grow.
- Record: Ixi B (run babysitting; one-shot launchers pointing into session scratchpads).
- Check: A fixture campaign that exceeds its cap is stopped.

### COMP-06 [HIGH VALUE] Predicted against actual cost
- Statement: Each campaign forecasts its cost and the error is tracked.
- Why: It makes planning improvable.
- Record: none.
- Check: Yield table.

### COMP-07 [EXPERIMENTAL] Rented compute
- Statement: Rented GPUs only for a question already qualified locally.
- Why: Scale without qualification repeats the record at higher cost.
- Record: Tan 3.5.
- Check: COMP-03.

----------------------------------------------------------------------

## 14. Inference requirements

### INF-01 [REQUIRED] No model in the tick path, none writing state
- Statement: No model runs inside a campaign. No model writes heartbeats, status, queue state or ledgers that code can derive from receipts.
- Why: 86 heartbeat messages in 25 hours; 158 commits in four days that changed only state files; a model brief that confabulated for weeks until it was made deterministic.
- Record: Ixi 4, 7, B.
- Check: The dashboard is generated by code from receipts.

### INF-02 [REQUIRED] Inference only at typed forks
- Statement: Model calls happen at: specification; implementation; independent re-implementation; attack construction; naming rival explanations; interpretation after certification; and a rare synthesis for the operator. Each call is tagged with its fork type.
- Why: These are the places the record found irreducibly model or human work. Everything else was already deterministic or could be.
- Record: Ixi 7 (hypothesis generation, naming rivals, framing, interpreting, authoring control documents, new adapters, hard gates).
- Check: The token log has a fork-type field with a closed vocabulary.

### INF-03 [REQUIRED] Tokens are metered
- Statement: Token use is recorded per session and per campaign, from the harness's own usage data, and cost per claim-ladder step is computed.
- Why: No mechanism anywhere recorded inference cost.
- Record: Ixi 7, G4.
- Check: The yield table has a token column that is not empty.

### INF-04 [REQUIRED] Triggers and alarm responses are code
- Statement: Scheduled work is triggered by a scheduler. An alarm with no automatic response goes to the operator's digest.
- Why: Detection was deterministic and response needed a session nobody scheduled. One alarm went unanswered for eight days.
- Record: Ixi 6, D.
- Check: Every detector has a named responder that is code or the operator.

### INF-05 [HIGH VALUE] Deterministic choice of the next experiment where rivals are named
- Statement: Once rival explanations are named, the next experiment is chosen by rule: the cheapest one that splits the remaining rivals; for thresholds, the staircase.
- Why: Selection is mechanisable; naming rivals is not.
- Record: Ixi 8 (a model-free selection kernel existed and was unused).
- Check: The selection rule's inputs and output are logged.

### INF-06 [HIGH VALUE] Cheap models for bulk, strong models for forks
- Statement: Bulk proposal generation uses small local or free models. Specification, attack and interpretation use the strongest available.
- Why: Tokens are the scarce resource; bulk mutation does not need the best model because reality filters it.
- Record: prompt section 16.
- Check: Token log by model.

### INF-07 [REJECTED] A standing fleet of model seats
- Statement: No always-on roster of model sessions that loop, report and coordinate.
- Why: Coordination share of traffic rose from 23% to 40% in four weeks; five control regimes in six days.
- Record: Ixi 4.
- Check: INF-01.

----------------------------------------------------------------------

## 15. Energy requirements

### ENRG-01 [REQUIRED] An energy estimate on every receipt
- Statement: Each campaign records estimated energy: GPU from sampled power draw, CPU from utilisation times a calibrated factor.
- Why: Electricity is a stated constraint and nothing measured it.
- Record: prompt section 16.
- Check: Receipt field.

### ENRG-02 [HIGH VALUE] One wall-power calibration
- Statement: A plug-in meter is used once to calibrate the software estimate for each host.
- Why: Software estimates of CPU power are rough.
- Record: none.
- Check: A calibration record per host.

### ENRG-03 [HIGH VALUE] Energy per unit of yield
- Statement: The yield table reports kilowatt-hours per claim-ladder step and per certified unit.
- Why: It is the honest efficiency of the program.
- Record: none.
- Check: Yield table.

### ENRG-04 [REQUIRED] Utilisation is not an objective
- Statement: No run exists to keep hardware busy.
- Why: The base role already says so; it bears repeating where compute is cheap.
- Record: base role 2a I.
- Check: Every campaign names the map cell it fills (SCI-08).

----------------------------------------------------------------------

## 16. Human-attention requirements

### HUM-01 [REQUIRED] A short list of operator decisions
- Statement: The operator decides admissions at C3 and above, budgets, hard gates and doctrine. Everything else has a default.
- Why: Operator attention is the scarcest resource, and it was spent on relay and routine.
- Record: Ixi 4 (177 operator prompts in 20 days; idle fleet on days without them).
- Check: The decision queue is derived from the claim registry and the budget table.

### HUM-02 [REQUIRED] One deterministic digest
- Statement: One generated digest, weekly by default, readable on a phone as plain text, plus alarms.
- Why: The one model-to-code migration on record (the operator brief) lost nothing and stopped confabulating.
- Record: Ixi 7.
- Check: The digest is produced by code.

### HUM-03 [REQUIRED] The operator is not the transport
- Statement: Work between model families goes through committed files and programmatic calls, not through the operator pasting blocks.
- Why: Every cross-model review passed through one person's phone.
- Record: Ixi 4, D.
- Check: The I3 re-implementation flow needs no paste.

### HUM-04 [REQUIRED] A stable control model
- Statement: One decisions register. A minimum dwell between changes to the control model (default: two weeks), except for safety.
- Why: Seven orders and 16,858 words in about 40 hours, several reversing the last.
- Record: Ixi 4.
- Check: The register's dates.

### HUM-05 [REQUIRED] Names say what things are
- Statement: Engines and artifacts are named for what they do. No name is reused. A glossary is kept.
- Why: Labels outran mechanisms, and reused names hid lineage.
- Record: Tan 2.1; Ixi D.
- Check: PROV-05.

### HUM-06 [HIGH VALUE] Operator time is metered
- Statement: The operator's minutes per week on the program are noted, even roughly.
- Why: It is a cost and belongs in the yield table.
- Record: none.
- Check: A weekly number in the digest.

----------------------------------------------------------------------

## 17. Publication and output requirements

### PUB-01 [REQUIRED] Externalisation follows the claim ladder
- Statement: Instruments, world suites, failure fixtures and negative results may be externalised when they reproduce from a clean clone. Effects at C2. Mechanisms at C3. Principles at C5.
- Why: Genuine work should end in forms an outsider can inspect, and nothing should be shown above its evidence.
- Record: prompt section 18; PHASE3_CHALLENGES.md 1e.
- Check: An external artifact cites its claim level.

### PUB-02 [REQUIRED] Every external claim ships its reproduction pack
- Statement: Code, seeds, certificates and one command.
- Why: REPR-02.
- Record: T18.
- Check: The pack runs on a clean host.

### PUB-03 [REQUIRED] External wording stays under the ceiling
- Statement: External text uses the wording template of the claim's level.
- Why: SCI-04.
- Record: Tit B (a database consistency check cited for months as the program's unique calibrated asset).
- Check: SCI-04 lint.

### PUB-04 [REQUIRED] The doctrine conflict is resolved by the operator first
- Statement: Tracked doctrine HARD-1 forbids any paper or publication framing. Section 18 of the architect prompt asks for external artifacts including preprints. Until the operator supersedes HARD-1 in the tracked file, Phase 3 outputs are reproducible packages and technical briefs.
- Why: The base role says a rule cites tracked doctrine or stands uncited; the tracked doctrine currently says no.
- Record: aporia/doctrine/critical_memories.md HARD-1; base role section 2.
- Check: The doctrine file's text.

### PUB-05 [HIGH VALUE] Instruments and negatives first
- Statement: The first external artifacts are the certified world suite, the qualification harness and the failure fixtures.
- Why: They are the part of the program most likely to be right and most useful to others.
- Record: Tan 2.8.
- Check: PUB-01.

----------------------------------------------------------------------

## 18. Traceability: failure classes to requirements

Every failure class in the Tityos taxonomy is answered by at least one
requirement that makes it hard or impossible, not merely discouraged.

| class | name (short) | requirements |
|---|---|---|
| T01 | measurement carries its own answer | WLD-01, WLD-05, MEAS-11 |
| T02 | self-verdicting | MEAS-11, ANTI-01, SCI-04 |
| T03 | controls that cannot fail | MEAS-02, SCI-02, SCI-03 |
| T04 | positive control absent or aimed beside the instrument | SCI-01, SCI-05, MEAS-01, MEAS-02 |
| T05 | invalid null, no chance floor | WLD-03, WLD-05, MEAS-04 |
| T06 | tautology | WLD-03 (definition rule), WLD-07 |
| T07 | construction artifacts | WLD-05, WLD-07, DEV-07 |
| T08 | baseline omitted | WLD-03, MEAS-04 |
| T09 | selection effects | WLD-06, SRCH-05, SCI-11 |
| T10 | statistical malpractice in gates | MEAS-07, MEAS-08, SCI-10 |
| T11 | post-exposure change | SCI-03, MEAS-06, PROV-06 |
| T12 | unreachable design | SCI-01, SCI-03, SRCH-02 |
| T13 | world or organism too weak | WLD-02, WLD-08, ORG-03, ORG-05 |
| T14 | label stands in for property | MEAS-03, CAUS-06, PROV-09 |
| T15 | novelty conflation | ANTI-02, ANTI-05, ANTI-06, SCI-14 |
| T16 | mechanism by description | CAUS-01, CAUS-04, CAUS-10 |
| T17 | improper independence | WLD-11, REPR-04, SCI-10, ANTI-01 |
| T18 | provenance failures | PROV-01 to PROV-09 |
| T19 | status from the wrong layer | SCI-02, MEAS-09 |
| T20 | safeguards never wired | MEAS-02, INF-04 |
| T21 | activity read as productivity | INF-01, ENRG-04, SCI-08 |
| T22 | the auditor commits the audited class | MEAS-10, WLD-11 |
| T23 | validated differs from deployed | REPR-05, MEAS-06 |
| T24 | model-specific measurement hazards | MEAS-15, ANTI-01, PROV-07 |
