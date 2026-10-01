# Prometheus Phase 3 -- meta-analysis and proposal

Independent architect: FABLE-5.1 (seat Dionysus, instance m1-3815a3b9, host
SKULLPORT / M1). Written 2026-10-01.

This is the scientific argument. The other files in this directory carry
the detail it refers to:

| file | what it holds |
|---|---|
| REQUIREMENTS.md | 158 requirements, frozen before salvage; section 1 defines every term |
| RSE_ARCHITECTURE.md | the proposed architecture (sections 1 to 12 frozen with the requirements; section 13 added after salvage) |
| ENGINE_PORTFOLIO.md | nine experiment programs, each with the prompt's fields |
| SALVAGE_MATRIX.md | 86 decisions on existing components |
| ASSUMPTIONS.md, FALSIFIERS.md, OPEN_QUESTIONS.md | what the proposal rests on, what would overturn it, what it leaves open |
| prototype/p1_slice/ | a working miniature of the first experiment, with receipts |
| salvage_reports/ | seven worker fact sheets, verbatim, and one incident report |
| process/ | generators, checkers, a prior-art check, the snapshot of my position before I read the operator's challenges document |

## How this was produced

The prompt requires requirements and architecture before any look at the
existing engines. The order is in git:

| step | commit | on main |
|---|---|---|
| charter adopted | 04b97a598 | yes |
| requirements and architecture frozen | a0e3a4d03 | yes |
| briefs for seven read-only salvage workers | e3d7c7034 | with this package |
| prototype code and preregistration, before any run; also ASSUMPTIONS.md, FALSIFIERS.md, the prior-art check and worker report 01 | f98efbc33 | with this package |
| prototype first gate FAILED; amendment preregistered | 36924629d | with this package |
| prototype receipts | 020b9fe00 | with this package |
| worker reports 02 to 07 deposited; incident report | 546202ff6 | with this package |
| salvage matrix; architecture section 13 | 334140a83 | with this package |
| engine portfolio; correction to H1 | f463bc4c8 | with this package |
| this file, open questions, index; corrections from two reviews | the commit that adds this file | with this package |

Before the freeze I had read the architect prompt, the four crawler
reports, the Tityos failure taxonomy, two Ixion annexes, the base role and
the doctrine. I had not opened any seat dossier or engine source. I read
the operator's challenges document only after writing down my own position
(process/00_SNAPSHOT_BEFORE_CHALLENGES_DOC.md, then 01_DELTA).

What the freeze does and does not cover. The freeze commit holds
REQUIREMENTS.md and RSE_ARCHITECTURE.md sections 1 to 12. ASSUMPTIONS.md
and FALSIFIERS.md are not in it. They were first committed 28 minutes
later, in the same commit as the first worker report, and git cannot show
that they were written before I read that report.

Before pushing, two read-only reviewers checked the package against its
own sources: one for numbers and identifiers, one for claims. Between them
they found about 80 defects, nearly all of them mine and nearly all of one
kind: a statement stronger than its source. They are corrected. The frozen
files were corrected by dated annotation only.

I did not look for or read any other architect's design. Fetching main
before the push showed me three commit subject lines from another
architect's seat; I opened none of its files.

## What is measured here and what is argued

- Measured by me today: the prototype's results (section 21 and
  prototype/p1_slice/README.md); kernel throughput on M1.
- Reported by workers from source, ten points re-checked by me: the facts
  in SALVAGE_MATRIX.md.
- Taken from the crawler reports: the account of v1 and v2 in sections 2 to
  5. The crawlers, the workers and I are one model family.
- Argued, not measured: everything else, including the thesis.

## Departures from the prompt

The charter gave latitude. I used it in nine places.

1. RSE is a property with a test, not an engine to build.
2. "Engines" are experiments on one shared kernel.
3. Designed organisms are central: as calibration standards and as the top
   of a descent. The prompt leans toward emergence under pressure.
4. Conventional learners and gradient descent are in the design, as a
   reference arm and as one optimiser among several.
5. REACH is a fourth certificate. The prompt covers demand, capacity and
   ruler validity.
6. An operating model is part of the architecture.
7. I did not adopt the prompt's section 18 on publication, because tracked
   doctrine HARD-1 forbids it. I say what would qualify and leave the
   doctrine to the operator.
8. I ask for doctrine HARD-2 to be narrowed: prior art after validation,
   with measured recall.
9. I built and ran a miniature of the first experiment instead of only
   describing it.

----------------------------------------------------------------------

## 1. Executive thesis

**The diagnosis.** Prometheus v1 and v2 built many small engines, watched
them, interpreted what they saw, and audited afterwards. Under almost every
result the record shows the same four gaps: the world did not require the
phenomenon, the organism could not hold it, the search could not reach it,
or the ruler could not detect it. So positives could not be trusted and
nulls could not be read. The operator's summary is accurate: nothing built
so far put the program on a trajectory toward synthetic reasoning. Most v2
worlds demanded about one bit of memory or less, and no result was a
certified exclusion of a simpler explanation.

**The thesis.** Phase 3 should study the physics of within-lifetime
construction: when and how a system moves information from experience into
structure that persists, compresses, becomes callable, and improves the
process that built it. I name six such relocations: HOLD, ADAPT, BUILD,
COMPRESS, COMPOSE, RECURSE. They are coordinates for measurement. They are
not a ladder to climb and not a list of mechanisms.

**Why there.** A transformer holds and adapts at very large scale inside a
context window. Its compression and composition happened once, offline, in
training. Inside a deployed lifetime nothing it experiences becomes
persistent structure that it then computes with, unless a designer bolts a
memory on. If there is an architecture beyond the current one, a good place
to look is where systems construct their own reusable structure during
life. That can be studied small, because it is about where information sits
and how it is reused, not about how much a system knows. This is an
argument. Section 6 says which part of it an experiment can test.

**The method.** Reverse the old order. For every cell, first establish four
certificates, then ask the open question.

- DEMAND: the world ships the exact best score of every restricted class of
  policy. An organism that beats a bound on sealed worlds is outside that
  class. No interpretation is needed.
- EXPRESSIBILITY: a designed organism in that substrate passes the same
  ruler.
- REACH: search recovers planted targets of that size at a measured rate.
- DETECTABILITY: the ruler sorts known positives, negatives and impostors
  with measured error, and each of its controls has been made to fail.

A positive needs the first and the last. A null about the phenomenon needs
all four. Anything less is a null about the apparatus and is labelled so.

**The shape.** One measurement kernel. One foundry of certified worlds. A
conventional reference arm. Two unlike constructive substrates with
switchable affordances. Further substrates one at a time. Nine experiments,
one question each, run as deterministic campaigns with no model in the
loop.

**What is built first.** One end-to-end calibration slice for BUILD. A
miniature of it exists and has run. Its first gate failed on an error of
mine, which was the most useful thing it did (section 21).

**What this promises.** Not a reasoner. A certified frontier that moves, or
a certified account of why it does not.

**Where it is most exposed.** Small worlds may not predict large ones. The
first two substrates are familiar machines. The axes and the designed
organisms carry my priors. Sections 23 and 25 say what would show each.

----------------------------------------------------------------------

## 2. What Prometheus actually built

From the four crawler reports and the salvage workers. Counts are theirs
unless marked. Each crawler covered its own territory of seats, and
several of its statements are readings of code, not measurements; where a
statement below is of that kind it says so.

**An institution.** About 59 seats since March 2026, in a repository of
68,903 tracked files (my count today). A message bus with 1,239 hashed
messages. 358 hashed captures of operator directives. Five coordination
regimes in six days at the end of September. Eight or more queue and lease
mechanisms.

**Version 1, March to June.** Pipelines of model calls. Code sampled
concept triples; a model answered and rated its own answer; a model wrote
tools from them; batteries scored the tools. In parallel, one generator
engine emitted 658 million records of random (object, invariant, relation)
tuples, 99.98% of them carrying a verdict computed by the generator itself
(a recorded count, not re-verified).

**Version 2, August to October.** Small engines:

- three byte soups in one instruction-set family, with heredity
  instruments;
- evolutionary harnesses on one shared tape machine;
- a message-passing integer substrate on the GPU;
- a byte-copy lattice;
- online regressors behind a fixed policy;
- an enumerative program synthesiser with an inherited library;
- law mining over author-declared coordinates;
- feature programs for fixed classifiers;
- a register machine with a persistent executable workspace;
- exactly solvable game benches.

Around them: a hash-chained ledger service, an experiment queue, an
evidence store, an index, a job fabric.

**Three structural facts** matter more than the list.

1. In the territory Sisyphus crawled (fifteen seats) it was not fifteen
   engines. It was a few shared substrates used by many seats, authored and
   reviewed by one model family. In that crawler's words, "N seats agree"
   usually meant one substrate, one mutation operator and one author family
   agreeing with themselves.
2. Labels outran mechanisms. The Tantalus crawler tabulates the label each
   engine was given against the smallest mechanism its code implements.
   "Bounded recursive self-improvement" was an ordered library that
   reordered a fixed search; the improver never changed. A "tensor world
   engine" was a set of small online regressors behind a hand-coded policy.
   Seven seats used "tensor" for something that is not tensor algebra.
3. The worlds were shallow and the searches small. In the territory
   Tantalus crawled, by its reading of the code, no world demanded more
   than interpolation, lookup, small finite-state control or a one-step
   latch, with three partial exceptions, and no organism combined
   hierarchy, binding and memory. The largest lifetime-scale search the
   salvage found is about 2 x 10^7 evaluations, mostly in pure Python at
   tens to thousands of evaluations per second.

**What was real.** The crawlers agree, and the salvage confirms: the
positives that survive are mostly instrument positives. Bit-exact oracles and
cross-host replay. Exact counterfactual twins. Per-byte tracing of
material. Sealed-holdout receipts. Exactly solvable benches. Database-level
provenance invariants. A deterministic operator brief. These are good, and
most are small and recent.

----------------------------------------------------------------------

## 3. What Prometheus learned from failure

**The failure record is the program's best data.** Tityos recovered 24
failure classes with instances. The generators of false positives that
recur most: the measurement carries its own answer; the generator writes
its own verdict; an invalid null; a tautology; an artifact of construction;
a missing baseline; a change after exposure; nominal independence.

**The instruments were mostly unqualified.** Tityos's inventory has 152
records for 146 instruments. 30 records show an instrument that can
demonstrably output the class it rules on, 56 partly, 60 not, 5 unknown.
Two instruments were tested on a second substrate, 23 partly, 124 not at
all. 25 of 37 scoring instruments in one census had no chance floor. No
auditor was ever measured against planted defects.

**The corrections were real and came from inside.** This is the part of
the record that most deserves respect.

- 1,031 "spontaneous replicators" became 57 under a causal assay and about
  2 genuine self-copiers on closer analysis. The assay itself was then
  shown, by a constructed panel, to pass painters that carry zero heritable
  bits.
- 26 "spontaneous replications" became 0 when a predicate was found to
  read a run label and not provenance.
- 4 of 7 damage claims vanished under a qualified ruler.
- A model-written operator brief confabulated for weeks. It has been
  deterministic by default since 18 August.
- Most corrections were made by the seat that made the claim, often within
  hours.

**Five lessons I take from it.**

1. The unit of failure is the uncertified cell. Each of the 24 classes is a
   way for one of four things to be unestablished: demand, expressibility,
   reach, detectability.
2. A rule in prose does not bind. The base role already requires a
   negative, a positive and a cheat control on every critical instrument.
   Tityos notes that no mechanical check enforces it. I reproduced this in
   miniature today: I wrote the requirement "state power before the run",
   broke it within hours, and was caught only by a preregistered table
   compared in code.
3. Independence was nominal. Auditor and audited shared code, data, doctrine
   and model family. The one cross-family preregistered instrument was
   never graded.
4. Narrative is cheap and travels fast. Terms spread across seats within
   two days. The index layer turned "completed" into POSITIVE.
5. The deterministic parts of the institution worked and the model-mediated
   parts leaked. Detection was code; response needed a session that nobody
   had scheduled. One alarm went unanswered for 8 days.

**What the program learned that Phase 3 should keep.** Self-correction as a
norm. Hashes over normalised bytes. Verbatim capture of directives. Exact
replay. The instruments built in September after the audits: a three-valued
verdict with counts, an evaluator contract in exact fractions, a harness
that corrupts each control and expects a failure, a lockstep intervention
library, a constructed calibration panel. SALVAGE_MATRIX.md shows where
each goes.

----------------------------------------------------------------------

## 4. Scientific maturity assessment

**My characterisation: premature science.** Not hobby work and not cosplay.
The program practised the methods of science, often strictly:
preregistration, controls, replication attempts, hostile review, public
retraction. It practised them before the precondition that makes them bite
was in place: instruments of known validity, pointed at worlds of known
demand.

| dimension | state at the end of v2 | evidence |
|---|---|---|
| reproducibility of runs | strong where integer and deterministic | bit-exact oracles; cross-host replays; hashed ledgers |
| provenance | strong in places, fragmented | 358 hashed directives; ledgers off-repo; credentials in tracked files |
| preregistration | practised, weakly enforced | plans committed with results; thresholds moved after data |
| controls | required by rule, not by code | controls that could not fail in at least a dozen instruments |
| instrument validity | mostly unknown | 30 of 152 inventory records with demonstrated detectability; a measured error rate in two or three instruments at most |
| world validity | absent | no world shipped a computed bound for a restricted policy class; a few bounds were derived afterwards, per task |
| search validity | absent | no measurement of search power in any component examined |
| independence | nominal | one model family in every role; shared code between auditor and audited |
| claims about cognition | none certified | surviving positives are mostly about instruments; one old positive was never challenged |
| self-correction | unusually strong | most corrections by the claiming seat, often within hours (the crawler's reading) |
| institution | load rising | coordination share of messages 23% to 40% in four weeks, by a subject-word heuristic |

**What separates Phase 3 from hobby work or cosplay.** Not more rigour in
general. Four specific things, each checkable:

1. Every claim-bearing cell has its four certificates before it runs.
2. Every ruler has a datasheet with measured error rates and a
   qualification receipt, and the runner refuses without them.
3. Every claim has a level on a ladder with stated evidence, and a ceiling
   it may not be worded above.
4. Verdicts are written by code that the generating and interpreting
   parties cannot write to.

**The claim ladder** is in REQUIREMENTS.md section 1.8. In one line each:

| level | name | what it needs beyond the level below |
|---|---|---|
| C0 | observation | a logged run |
| C1 | effect | preregistered; DEMAND and DETECTABILITY; beats the whole baseline ladder; 5 independent lineages; effect size with interval |
| C2 | robust effect | an attack round with no surviving impostor; sealed worlds; clean-clone reproduction on a second host |
| C3 | mechanism | necessity and sufficiency by intervention; a mechanism model that predicts new interventions; an independently implemented ruler; operator admission |
| C4 | transferable mechanism | recurrence in independent lineages or a conferring transplant; three unlike world families |
| C5 | principle | a quantitative relation in three substrates and three families, predicted in advance for a new cell, reproduced outside |
| C6 | architectural principle | a C5 relation used to design a system that reaches a predicted certified gain |

Nulls have two levels: N1, all four certificates and power of at least 0.8
in one cell; N2, the same in two substrates and two search regimes.

The prompt's terms map as: anomaly C0; effect C1 and C2; mechanism C3;
reasoning primitive, developmental primitive and transferable mechanism C4;
architectural principle C5 and C6. By this ladder the old program holds no
claim about cognition above C0, and a handful of instrument results that
would be C1 or C2 if re-run under the kernel.

----------------------------------------------------------------------

## 5. Why historical results are insufficient

Read the old cells through the four certificates.

| certificate | what the record has |
|---|---|
| DEMAND | none. No component computes the best score of any restricted policy class for a world in which an organism acts. The few bounds that exist are per task, in floats, applied after the fact; one is violated in its own environment. |
| EXPRESSIBILITY | sometimes. Designed organisms or planted systems exist in at least six engines. In one, designed organisms scoring .850 and .978 sat in a genome space where search stayed near .5. |
| REACH | never measured. The nearest designs measure "solved over expressible" at fixed budgets on five tasks per depth. One search could not take a neutral step and reported its target unreachable. |
| DETECTABILITY | 30 of 152 inventory records; almost none with a measured error rate. |

Consequences:

- No old positive is a class exclusion. Each remains open to "a cheaper
  policy does that", and in the record a cheaper policy usually did: a
  constant, a lookup, a one-shot latch, a clock, a reader of a leaked label.
- No old null is a null about a phenomenon. Each is ambiguous between "the
  phenomenon is absent", "the world did not ask for it", "the organism had
  no room", "the search was too short or the wrong shape", and "the ruler
  could not see it". Tantalus counts 30.6% of one engine's nulls as capped
  by its physics.
- The few results that agree across engines share a substrate, a mutation
  operator and an author family.

There is also a ceiling the certificates do not capture. Most of the worlds
asked for at most a bit of memory or a one-bit hidden mapping. One family
of recall worlds asked for more, by a worker's reading of its code, and
computed no bound. A program that looks for reasoning in worlds that reward
lookup will find lookup. That is why "nothing put us on a trajectory" is
exact: the frontier table for v2 has one row, HOLD, and it is uncertified.

I do not propose to re-score the old record result by result. I propose to
compile its failure classes into fixtures the new kernel must catch, and to
re-test nine old signals inside the new apparatus (SALVAGE_MATRIX.md
section 6).

----------------------------------------------------------------------

## 6. First-principles model of cognitive development

### 6.1 Start from where information is

Behaviour that depends on something not present in the current observation
requires that the information be somewhere. There are four places.

- The WORLD.
- FAST STATE: reset at every episode boundary.
- PERSISTENT STRUCTURE: survives episode boundaries within a lifetime.
- The GENOME: fixed for a lifetime; changed only by outer search.

The harness, not the organism, controls the resets. That is what makes the
partition a measurement and not a description.

Development is information relocating between these places under cost. I
use "cognition" for no claim. I use the relocation and its certified level.

### 6.2 Six relocations

| | relocation | what moves | the scarcity that drives it | class it excludes |
|---|---|---|---|---|
| T1 | HOLD | past observations into fast state | hidden state; delay | the best memoryless policy |
| T2 | ADAPT | this life's hidden parameters into fast state | variation between episodes larger than inherited capacity | the best policy that ignores within-episode evidence |
| T3 | BUILD | acquired information into persistent structure that later computation uses | lifetime information above fast capacity; resets | the best policy carrying nothing across episodes |
| T4 | COMPRESS | stored cases into regularities | storage priced or capped below the number of situations; tests on new combinations | a lookup of the permitted size |
| T5 | COMPOSE | regularities into units invoked with arguments | tasks of depth D with a step budget below flat search | a designed solver without reuse |
| T6 | RECURSE | the building procedure itself into modifiable structure | many learning episodes with shared meta-structure; later families outside the earlier span | a designed learner with a fixed procedure |

T1 to T4 have exact or information-theoretic bounds. T5 and T6 are excluded
against designed reference organisms, which proves less, and every claim at
those levels says so.

### 6.3 The prompt's chain, taken apart

The prompt offers a chain and asks me not to accept it because it is
plausible: experience, regularity, representation, compressed structure,
reusable operation, abstraction, reasoning over abstractions, reasoning
about reasoning. Each arrow, read as a relocation:

| arrow | relocation | what must be physically true | what would show it |
|---|---|---|---|
| experience to regularity | ADAPT | fast state rich enough for a sufficient statistic; variation the genome cannot pre-store | beats the best non-adaptive policy; the statistic is found by interchange |
| regularity to representation that persists | BUILD | structure writable during life and read by later computation | beats the no-carry bound after resets; behaviour follows a transplanted store |
| to compressed structure | COMPRESS | storage that costs; tests that are new combinations | beats a lookup of the permitted size on combinations balanced against surface similarity |
| to reusable operation | COMPOSE | addressing that survives structural change; invocation with arguments | solves depth D inside a step budget that flat search exceeds; one lesion harms several surface-distinct tasks |
| to abstraction | (a property of built structure) | the same | scramble invariance; a transplant confers the shared competence |
| to reasoning over abstractions | COMPOSE at depth, on new inputs | internal steps that do not act on the world | intervening on an intermediate state changes the outcome as the step structure predicts |
| to reasoning about reasoning | RECURSE; and monitoring one's own state | the learning machinery stored in mutable structure | gains on out-of-span families that transplant; opt-out that tracks injected carrier noise |

Two things follow.

First, the chain is not one process. It is several relocations with
different physical requirements and different pressures. An organism can be
at different levels on different ones, and whether that is true is itself
tested (FALSIFIERS F-T3).

Second, "what distinguishes this from ordinary training" has a concrete
answer: where the information sits, and when it got there. In ordinary
training the outer loop writes the structure and the lifetime uses it. In
construction the lifetime writes structure that the same lifetime then
computes with. Interchange and lesion at the store level tell the two
apart. Task accuracy cannot.

### 6.4 Three working laws

These are hypotheses. Each has a falsifier.

**Store and timescale.** Information goes to the store whose lifetime
matches the timescale on which it varies, when storage is priced. What is
stable across lives goes to the genome. What varies between lives and is
stable within one goes to persistent structure. What varies between
episodes goes to fast state. What varies within an episode stays in the
world or is held briefly. The variance spectrum of the world is a dial
(DEV-08), so this is testable: move the timescale of a regularity and the
store that carries it should move.

**Payoff times reach.** A relocation appears where it pays, net of its
cost, and where search can reach it. Payoff comes from the world
certificate and the measured cost of a designed organism. Reach comes from
the search-power curve at that organism's needle size. Predicted transition
probability is the payoff indicator times reach, with no fitted parameter
(H2, H3). Where this holds, emergence is designable. Where it fails, the
residual is the first real lead.

**Compounding.** Built structure shortens the needle for what is built
next. In worlds with compositional depth, each built level cuts the cost of
the next by a factor that grows with depth; in flat worlds it does not
(H6). Stages create new reachable stages by changing reach, and reach is
measurable with and without the built structure.

### 6.5 What an experiment here can and cannot say about transformers

I froze a hypothesis, H1, that learners with only fast state cannot BUILD.
Writing the reference arm out showed it is a theorem of the state
partition: if the harness resets the only state a learner has, the learner
carries nothing. A deployed transformer whose context is cleared does not
build across the reset, as a fact of its architecture. No experiment here
could discover that.

What experiments here can discover is H1b: whether a learner trained
offline compresses, within a lifetime, structure of a kind its training
never covered; and what it costs conventional machinery that is allowed to
write weights or an external memory. If amortised learners do compress
unseen kinds of structure at this scale, the gap I am aiming at is not
where I put it. The correction is recorded in RSE_ARCHITECTURE.md section
13.5.

### 6.6 What this model leaves out

Communication. Embodiment. Several organisms in one world, beyond a bounded
trial. Any process that would need language. And any axis I have not
thought of, which is the limit OPEN_QUESTIONS.md B3 carries.

----------------------------------------------------------------------

## 7. Organism requirements

Thirteen requirements (REQUIREMENTS.md section 3). The ones that carry the
design:

- **One protocol for every substrate** (ORG-01): observation in, action
  out, declared stores, exact snapshot and fork.
- **Three stores under harness control** (ORG-02), with a
  reset-equivalence test. The prototype showed why the test is separate: a
  broken reset fools the ruler and only this check catches it.
- **Eight affordances, each with an off switch** (ORG-03): writable fast
  state; lifetime-writable structure that computation reads or executes;
  state-dependent routing; composition with arguments; addressing that
  survives insertion and deletion; internal steps; creating, deleting and
  copying structure; cost for time and storage. They name no cognitive
  faculty. Switches turn "which is necessary" into an experiment.
- **The learning machinery is inside the organism** (ORG-04). Nothing
  outside writes its store.
- **Capacity margin** (ORG-05): the designed organism fits in half the
  size limits, so a null is not "no room".
- **Total, deterministic, integer semantics** (ORG-08).
- **Two unlike substrates plus a familiar reference** before any statement
  about substrates in general (ORG-07).

Rejected: organisms whose competence is supplied by a library of
hand-written operators (ORG-13). A model in the tick path is excluded
separately (INF-01).

The substrates:

- REF, conventional learners, as a control and a candidate.
- WM, the workspace machine: a stored-program organism whose persistent
  structure is a store of tagged blocks of integer words, with call and
  return, tag addressing, rent, and seven switches. It can express every
  relocation at small size. Its weakness is reach.
- PN, the plastic network: fixed-point activations as fast state, weights
  and topology as persistent structure, local plasticity and structural
  change in the genome. BUILD is native. Its predicted weakness is COMPOSE.
- Open arms, one at a time. The first is message passing.

The salvage found no organism to carry forward. It found the workspace
machine's layout already working in one old machine, and three ways that
machine went wrong, which become kernel tests.

----------------------------------------------------------------------

## 8. Developmental physics

Twelve requirements (REQUIREMENTS.md section 4).

- **A lifetime has structure** (DEV-01): episodes with resets, inside a
  life, inside a lineage. Without it the relocations cannot be told apart.
- **Development and outer search are separate switches** (DEV-02). Any
  capability is attributed to one, the other or both by turning each off.
- **Capacity and realisation are measured separately** (DEV-03):
  realisation is the certified level now; capacity is the certified level
  after a standard exposure from a standard start within a stated budget.
- **The developmental control set** (DEV-04): a same-compute direct arm; a
  shuffled-order arm; a frozen-development arm; a wrong-history twin;
  constant and lookup baselines at every stage. The salvage adds one sham
  for store interventions: identifiers kept, contents emptied.
- **Forked clones** (DEV-05). Software organisms allow identical
  individuals that differ in one thing. Not using that wastes the main
  advantage this kind of science has over biology.
- **The trajectory is the measured object** (DEV-06), not the final score.
- **A scaffold level on every cell** (DEV-07): how much was designed and
  how much was found, from S5 (all designed) to S0 (survival only).
- **Storage rent as the compression dial** (DEV-09). With free storage and
  no novelty, lookup is optimal and nothing compresses.

What does the compressing? The organism's own code, under rent and tested
on new combinations. Not the harness and not the outer search.

How do structures become reusable objects? Through addressing that
survives change and invocation with arguments. Whether those two are
necessary is hypothesis H4, tested by switching them off.

What does curriculum do? It supplies rewarded intermediate stages, which
shortens the needle. H3 predicts by how much.

----------------------------------------------------------------------

## 9. World requirements

Seventeen requirements (REQUIREMENTS.md section 5). The centre is one
idea: **a world is admitted with its certificate or it carries no claim.**

- **A demand certificate** (WLD-02): the exact best score of each
  restricted class, and a reference policy that beats it by a stated margin
  net of cost (WLD-08).
- **The baseline ladder ships with the world** (WLD-03), before any data.
- **Demand is dialled one axis at a time** (WLD-04).
- **Twins and leak probes** (WLD-05): an absence twin where the capability
  cannot pay; a scrambled twin; a planted one-character leak that the probe
  must catch.
- **Train, selection and sealed worlds** (WLD-06), with sealed seeds held
  by a broker with an access log (PROV-10). After today's incident the
  design adds: outside the working tree (RSE_ARCHITECTURE.md 13.2).
- **A shortcut audit before admission** (WLD-07): an automated search over
  cheap policies must fail to beat any bound. A hand-built list of cheap
  policies is not such a search; the old record admitted Nim that way.
- **Two implementations** of every claim-bearing world and solver (WLD-11).
- **Construct validity** (WLD-12): do profiles measured in small certified
  worlds predict behaviour in richer ones? This is the main risk of my own
  design, and it has a test.

Nine families, by what they demand: RECALL (HOLD), TRACK (HOLD toward
ADAPT), IDENTIFY (ADAPT), RETAIN (BUILD), RECOMBINE (COMPRESS), CHAIN
(COMPOSE), FAMILIES (RECURSE), DOUBT (uncertainty and revision), MINED
(unauthored: small decision processes sampled at random and kept by their
computed demand).

Worlds are small and deep, not large. Depth is the certified gap between
what a restricted class scores and what the capability scores. Size is not
evidence of depth (WLD-15, REJECTED). Reasoning claims with no environment
are rejected (WLD-16).

The salvage found seeds or parts for seven families and nothing for RETAIN
and FAMILIES. It found no code that computes a demand certificate for a
world in which an organism acts.

----------------------------------------------------------------------

## 10. Evolutionary/search pressures

Thirteen requirements (REQUIREMENTS.md section 6).

**Pressures are dials with their own positive controls** (SRCH-07). The
table in section 6.2 names the scarcity that should drive each relocation.
Each is a dial. A pressure counts only if a designed organism gains from
the capability under it.

**Search is an instrument, so it is calibrated.**

- The regime is a declared, varied factor (SRCH-01), acceptance rule
  included.
- A search-power curve (SRCH-02): targets planted at graded distances,
  recovery measured against budget. Every null reports power for a target
  of the plant's size.
- Needle size and random-hit rate (SRCH-03).
- Budgets in evaluations, on a ladder (SRCH-04).
- No selection on evaluation worlds (SRCH-05).
- Independent lineages (SRCH-06).
- Costs must not close the door before a foothold exists (SRCH-10).
- Seeded content is labelled and traced (SRCH-11).
- The optimiser is a factor (SRCH-08): blind structural variation, a
  population method with a diversity archive, model-guided proposals, and
  gradient where the substrate allows.

**What the prototype measured.** On a toy machine, recovering one missing
instruction of an 8-instruction builder succeeded in 24, 9 or 1 of 24
lineages depending only on the acceptance rule. (These 24 are search seeds
on one planted target and one set of training lives: independence I1, not
the I2 lineages the experiments require.) No rule dominated: the
rule that was best at distance one recovered nothing at distance two, and
the rule that was worst at distance one was the only one to find a builder
from an empty program. Zero of 2,000,000 random programs reached 0.9. The
counts are small and the pattern is the finding: the acceptance rule is a
first-order factor in reach, and it has to be varied.

**Evolution against development.** What outer search specifies and what
the lifetime builds is an experimental variable. The store-and-timescale
law (section 6.4) predicts the division.

----------------------------------------------------------------------

## 11. Measurement and instrument qualification

Fifteen requirements (REQUIREMENTS.md section 7).

- **A datasheet for every ruler** (MEAS-01): what it measures, on what, its
  false-positive and false-negative rates, its minimum detectable effect.
- **Qualification is a gate in code** (MEAS-02). The runner refuses a ruler
  without a current receipt. The gate sorts a calibration set, passes a
  channel test, and passes a fire test for every control.
- **Capability is reported as a certified level** (MEAS-03): the largest
  demand at which the organism beats the bound, in bits where the bound is
  informational.
- **Trivial responders beside every headline** (MEAS-04).
- **One named test per distinction** (MEAS-05).
- **Exact decision arithmetic** (MEAS-07). A float sitting on a threshold
  decided a verdict in the record.
- **Power stated before the run** (MEAS-08), and enforced.
- **An anti-calibration set** (MEAS-10): each kill path is tested on cases
  that are true but surprising, and its false-negative rate is reported. A
  battery that kills everything looks rigorous.
- **Verdict authorship is separated** (MEAS-11): rulers run in a separate
  process and nothing else can write verdicts.
- **Thresholds by adaptive staircase** (MEAS-12).

Model-judged measurement is rejected (MEAS-15).

The calibration set, per ruler (REQUIREMENTS.md section 1.3):

| member | what it is |
|---|---|
| POSITIVE | a designed organism known to have the capability |
| NEGATIVE | the nearest designed organism known to lack it |
| IMPOSTOR | the cheapest organism that imitates it by a shortcut |
| CHANNEL TEST | a fabricated record of success fed straight to the ruler |
| FIRE TEST | each control run once against a deliberately broken instrument |

The prompt suggests that no engine interpret a novel signal until its
ruler has shown known-positive recovery, known-negative rejection, neutral
handling, a sensitivity curve and failure bounds. I adopt that and add two
things the record asks for: impostor rejection, and a fire test for every
control. And for nulls I add REACH, which is not a property of the ruler
at all.

----------------------------------------------------------------------

## 12. Signal vs hallucination architecture

The question the prompt asks: how should a Phase 3 engine be built so that
each historical failure mode becomes difficult or impossible?

My answer is structural, in three parts.

**Part 1. Three authorities, separated by write permission.**

    GENERATION      proposes organisms, worlds, hypotheses   (models, mutation, search)
    REALITY         decides survival and verdicts            (worlds, rulers, interventions)
    INTERPRETATION  describes, and proposes experiments      (models, the operator)

Interpretation cannot write to the claim registry, the archive or the
verdict tables. Generation cannot write verdicts. This is a database
credential per authority, not a convention. The salvage found that no
existing store separates write authority; every store shares one
credential.

**Part 2. A runner that refuses.** A campaign does not start without: a
preregistration commit that is an ancestor of the code; a verdict table
shown total and reachable on synthetic inputs; exact power for every
preregistered verdict; current qualification receipts for every ruler; a
baseline ladder for every world; budget caps.

**Part 3. The record as a control corpus.** The failure classes are
compiled into fixtures. The kernel's own test suite presents each one and
expects to catch it. A failure found later becomes a new fixture.

The prompt's twelve examples, each against the mechanism that blocks it:

| historical failure | what blocks it | an instance from the record |
|---|---|---|
| leakage | hidden state stays behind the world protocol; leak probe with a planted one-character leak; twins | an answer key inside a probe, with an executable cheat reader |
| baseline omission | the baseline ladder ships in the world's admission commit | a tuned baseline that arrived after the data |
| tautological controls | the control-identity audit: not a no-op, not a constant, not identical by design to another arm | two swaps that were one measurement in 93 of 93 groups |
| controls that cannot fail | a fire test for every control; a probe that checks whether a check can vary | a control arm with zero rows that passed |
| ruler saturation | the anti-calibration set; staircases; the power gate | a detector that fired 1,658,614 times in 3,719,136 evaluations |
| shared-code "independence" | independence levels on every claim; a second implementation behind C3 | two implementations that imported the same random streams |
| seeded phenomena | material tracing; seeded content labelled | 26 of 26 "spontaneous" flags that were transplants |
| selection on holdouts | train, selection and sealed worlds; custody; the runner picks the champion | a champion chosen by argmax on the evaluation seeds |
| cheap proxy strategies | class exclusion; impostors in the calibration set; an automated shortcut search at admission | a clock that solved a "learning" world at 1.000 |
| unreachable search regions | the search-power curve; acceptance rule varied; nulls carry power | a greedy walk that could not take a neutral step |
| uncalibrated detectors | datasheets; the qualification gate | 60 of 152 inventory records with no demonstrated detectability |
| post-hoc interpretation | interpretation only after certification, and it cannot write verdicts | a plan committed together with its results |

REQUIREMENTS.md section 18 traces all 24 failure classes to requirements.
SALVAGE_MATRIX.md section 5 lists 30 fixtures with sources; ten of the
twelve instances above are among them. Two of the 30 are mine, from today.

What this does not block: an error shared by everyone who looks. That is
why independence levels exist, and why the limit at I2 is printed on every
claim until a second model family is in the loop.

----------------------------------------------------------------------

## 13. LLM epistemic escape

**The question.** Can a search system mediated by human priors discover
unfamiliar machinery? The dangerous loop is: a model generates, a model
recognises, a model admits.

**Where a model may stand.**

| role | allowed | guard |
|---|---|---|
| architect | yes | certificates need no ontology; several architects; falsifiers written in advance |
| coder | yes | differential tests; a second implementation behind C3; fixtures |
| mutation generator | yes, as one generator among several | a declared blind share (default half); lineage tags by generator |
| hypothesis generator | yes | hypotheses enter as preregistrations with forecasts, and are scored |
| interpreter | yes, after certification | cannot write verdicts or the registry |
| classifier of mechanisms | no, as a verdict | "unfamiliar" is a measured distance from a reference class |
| admission gate | no | admission and allocation use certificate numbers only |

**The anti-gravity mechanisms**, in order of how much I trust them.

1. Class exclusion needs no ontology. A bound is beaten or it is not. A
   mechanism nobody can name passes exactly as a familiar one does.
2. Admission and allocation use certificate numbers only (ANTI-02). No
   novelty score, no model rating.
3. A measured reference class (ANTI-05). Conventional learners go through
   the same probes; "unfamiliar" means outside their signatures.
4. A declared share of blind variation (ANTI-04).
5. Unauthored worlds (MINED), so that the worlds are not all mine.
6. Open substrate arms.
7. The unclassified-but-certified queue (ANTI-03).

On the prompt's proposal that failure of all models to classify a
reproducible causal phenomenon should raise priority: yes, after C2, and
never as evidence. Both halves are needed. Without the first the
unfamiliar is discarded. Without the second noise is rewarded.

**How we would know** (the direct test). P8 searches the same cell with a
blind generator and with a model, at equal evaluations, and compares the
mechanisms found by their signatures. If model-guided finds are narrower
and some blind finds lie outside them, the restriction is real and has a
size. If not, the worry is not supported at this scale and the blind share
can shrink. The one existing data set points the expected way: model-written
genomes sat closest to the known library. It is a pilot with known defects.

**The limit I cannot design away.** I am a model, designing an apparatus
to escape a model's priors. The axes, the worlds and the designed
organisms are my choices. The answer is mechanical, not personal: bounds
that need no judgement, worlds nobody authored, blind variation, a second
implementation by another family, and other architects working separately.
The comparison across architects is the real check on this section.

One more point from the prompt's anti-gravity section, applied to myself.
My first two substrates are a stored-program machine and a plastic
recurrent network. Both are familiar. I chose them because calibration
needs substrates in which I can write designed organisms today. The
unfamiliar substrates wait until the kernel is qualified. Another architect
could weigh that differently and would have grounds.

----------------------------------------------------------------------

## 14. Recursive sagacity definition

### 14.1 The five terms the prompt asks me to separate

| the prompt's term | operational form here | measured by |
|---|---|---|
| latent cognitive capacity | EXPRESSIBILITY: the highest level at which a designed organism in the substrate passes the ruler, within half the size limits | designed organisms; exhaustive enumeration at small sizes |
| developmental capacity | capacity in the sense of DEV-03: the certified level an organism reaches after a standard exposure from a standard start within a stated budget, with outer search switched off | forked clones in P6; the frontier table carries it beside realisation |
| realized competence | realisation in the sense of DEV-03: the certified level now, the largest demand at which the organism beats the bound on sealed worlds | class exclusion with a staircase |
| transferable sagacity | cost saved on withheld task families per bit of structure carried forward | savings against a naive twin and a wrong-history twin, divided by the bits whose removal changes the savings |
| recursive sagacity | sagacity whose rate of production rises because of what the organism built | section 14.3 |

None of these is task accuracy. The first three are kept apart on purpose.
The old program repeatedly read a failure of search as a limit of the
substrate, and a low score now as a low ceiling.

### 14.2 Compression, and when it counts

The prompt compares storing 1,000 solutions, 100 patterns, 20 strategies
and 5 principles, and says the deepest representation should reduce the
new information needed for future problems. That is the definition of
sagacity above, read as a ratio: future acquisition cost saved, per bit
carried.

- 1,000 stored solutions carry many bits and save nothing on a new family.
  A lookup impostor must score near zero, and that is a check on the ruler
  (MEAS-13).
- 5 principles carry few bits and save a great deal.
- Description length alone does not measure this. A short description that
  does not transfer is not sagacity. So compression is certified by
  behaviour on new combinations in RECOMBINE, not by counting bits.

The prompt's candidate measurements, placed:

| candidate | where it lives |
|---|---|
| sample efficiency over developmental age | savings ratio per stage (P6) |
| reduction in future learning cost | sagacity numerator |
| cross-domain reuse; structural reuse | the reuse matrix: every component lesioned against every task (CAUS-08) |
| minimal description length | carried bits, by lesion; not description length of the genome |
| retained competence | RETAIN's certified level across gaps |
| intervention sensitivity | interchange and lesion |
| transfer after representation scrambling | the scrambled twin (XFER-02) |
| new-task adaptation rate | acquisition cost on withheld families |

### 14.3 Recursive sagacity, and what would go beyond learning to learn

A fixed hierarchical learner already gets faster inside its hypothesis
space. That is learning to learn, and the old record mistook it for
self-improvement: an improver that never changed, with a library that
reordered a fixed search.

**Definition.** An organism shows recursive sagacity if:

1. its cost to acquire each new task family falls with developmental age;
2. the fall holds on OUT-OF-SPAN families, which need something no earlier
   family needed, where a learner with a fixed procedure and fixed
   hypothesis space shows no gain by construction;
3. the gain is carried by structure the organism built: lesioning that
   structure removes it, and transplanting it into a naive clone confers
   it, against shams;
4. a memorising impostor, given the same curriculum, shows nothing.

**The observation that would go beyond ordinary learning to learn:** a
rising savings ratio on out-of-span families, above the fixed-procedure
learner, that transplants. Each clause has a designed control: a positive
(a learner whose procedure adapts), a negative (the same with the
procedure frozen) and an impostor (memorised solutions).

**What I do not know.** Whether the positive control can be built at toy
scale. The old record's nearest attempt built no reusable structure from
nothing in 8 of 8 runs. If it cannot be built by month 6, the ruler cannot
be qualified and no RECURSE claim is possible. That is stated now.

### 14.4 Critical thought

The prompt asks whether mechanisms corresponding to uncertainty, competing
hypotheses, evidence seeking, contradiction detection, revision and
calibration can emerge under pressure, and what would count as evidence of
metacognition without hard-coding labels.

The DOUBT family supplies the pressures the prompt lists: misleading early
evidence, costly observation, irreversible commitment, an opt-out, rule
changes. Each behaviour gets one exclusion test against the exact value of
the restricted policy that lacks it (ENGINE_PORTFOLIO.md section 9):
holds alternatives; seeks evidence when it is worth its cost and stops
when it is not; revises after a change.

For monitoring one's own state there is a causal test that needs no label
and has no first-order explanation: inject noise into the organism's
identified memory carrier on some trials, hold stimulus difficulty fixed,
and see whether it opts out more on those trials. It is impossible in
animals and cheap here.

Whether repeated use compresses these procedures into reusable structure
is the COMPOSE question asked of organisms from DOUBT worlds, and "when to
invoke them" is routing. Neither needs a new instrument.

----------------------------------------------------------------------

## 15. Proposed Phase 3 architecture

RSE_ARCHITECTURE.md is the specification. In brief.

**Alternatives considered** (its section 2): one integrated engine; six to
twelve independent engines; an instrument program only; scale first; soup
first; and the choice, a shared kernel with certified worlds, a reference
arm, a few unlike substrates and question-shaped experiments. The count of
experiments is a consequence, not a goal.

**Layers.**

    CLAIMS       claim registry; frontier table; emergence map;
                 transition map; yield table
    EXPERIMENTS  P1 .. P9
    RULERS       class exclusion; interchange and lesion; fork and savings;
                 signature and reference class; search-power curve; meters
    WORLDS       | SUBSTRATES
    nine         | REF, WM, PN, open arms; each with designed organisms
    families     |
    PROTOCOLS    organism, world, search, ruler, receipt
    KERNEL       deterministic runner; one queue; one ledger; qualification
                 gate; sealed-world broker; failure fixtures; derived index

**Three methods carry it**: class exclusion; descent from existence
proofs; a null model for emergence.

**Four standing products**, generated by code from receipts:

- FRONTIER TABLE: relocation by substrate, the highest certified level,
  with scaffold level, optimiser, cost and claim level. This is the
  program's trajectory.
- EMERGENCE MAP: relocation by substrate by scaffold level, reached or
  not, with search power.
- TRANSITION MAP: per relocation, observed transition probability beside
  the payoff-times-reach prediction.
- YIELD TABLE: section 19.

**Operating model** (its section 10; a proposal, since retiring seats is
the operator's act). The unit of work is a campaign: specify, build and
qualify, run, judge, attack, interpret, admit. Three roles taken per
campaign and dropped: BUILDER, BREAKER, OPERATOR. No model writes state. No
heartbeats. One queue, one ledger, one decisions register, one digest.

**Why not the fleet.** Ixion's account: coordination rising to 40% of
message traffic, by a subject-word heuristic; 158 commits in four days
that only moved state files; an alarm unanswered for eight days; 177
operator prompts in 20 days as reported by one seat, with about two seats
active on days without one.

----------------------------------------------------------------------

## 16. Engine portfolio

ENGINE_PORTFOLIO.md gives each experiment with all the prompt's fields.

| id | question | varies | hypothesis |
|---|---|---|---|
| P1 calibration slice | Can the apparatus tell a builder from a holder from a cheat? | nothing | -- |
| P2 reference arm | What do conventional learners certify, at what cost, and where do they stop? | the learner family | H1b |
| P3 affordance knockout | Which affordances are necessary for which relocation? | the organism's affordances | H4, H5 |
| P4 transition mapper | Where does each relocation appear, and does payoff times reach predict it? | the world's pressures | H2, H3 |
| P5 scaffold descent | How far below a designed organism can a capability be regenerated? | how much is designed | H3, H5 |
| P6 fork lab | Does built structure cut the cost of later acquisition, and does that compound? | developmental history | H6 |
| P7 doubt and reliability | Do organisms hold alternatives, seek evidence, revise, monitor themselves? | the reliability of evidence | -- |
| P8 generator divergence | Does a model generator find a narrower set of mechanisms than blind variation? | the generator | H7 |
| P9 open substrate arm | Does an unlike substrate reach the same levels by other mechanisms? | the substrate | -- |

They are complementary because each varies one thing and they share
everything else.

----------------------------------------------------------------------

## 17. Prometheus salvage analysis

SALVAGE_MATRIX.md has 86 decision rows with what each component does, what
shows it correct, its fit, the cost to adapt against the cost to rebuild,
its coupling and what is taken. Tallies are checked by script.

    all rows (86):        KEEP 3, HARDEN 13, EXTRACT 40, REBUILD 5,
                          RETIRE 11, HISTORICAL CONTROL 9, UNKNOWN 5
    scientific rows (72): KEEP 0, HARDEN 8, EXTRACT 36, REBUILD 5,
                          RETIRE 10, HISTORICAL CONTROL 9, UNKNOWN 4

**No old engine continues as an engine.**

What carries forward:

- into the kernel: a queue with a lease; a receipt schema; a three-valued
  verdict with counts; an evaluator contract in exact fractions; a harness
  that corrupts controls; preregistration checks; trivial responders; a
  model-call layer; the base role;
- into the foundry: an event-stream grammar (RECALL); exact-Bayes stream
  worlds (TRACK, IDENTIFY); a surrogate and holdout construction
  (RECOMBINE); a sampled-system generator (MINED); twins and leak worlds;
- into the rulers: a carrier-swap design with eight documented failure
  modes; a lockstep intervention library; store-content conditions;
  loop-aware lesions; a heredity record format with fixtures;
- into experiments: a fixed-procedure learner as the RECURSE negative
  control; a divergence statistic;
- as fixtures: 31 real defects listed by one worker; the matrix selects 30
  for the kernel, 7 from that list and the rest from the other reports and
  from this package.

What has no starting point, in order of how much the design leans on it:
demand-certificate solvers; the workspace-machine kernel; the search-power
instrument; the runner's refusal gates; separate write authority; custody
of sealed worlds; the reference arm; the plastic network; RETAIN and
FAMILIES; the staircase and the carrier-noise test; energy and token
metering; the claim registry; a signature space; a tracer for WM.

The workers also found 14 places where the crawler record was wrong. None
changes a requirement.

The matrix itself was then checked row by row against the worker reports
by a read-only reviewer. It found 22 items where my rows overstated a
sheet: "in the tree" where the worker wrote "in scope", dossier figures
quoted without their "not verified" marker, four miscounts. They are
corrected.

----------------------------------------------------------------------

## 18. Resource model

**Principle** (the prompt's): inference at genuine forks only. Everything
else is pushed down into code.

**Where inference is necessary.** Seven typed forks (INF-02):
specification; implementation; independent re-implementation; attack
construction; naming rival explanations; interpretation after
certification; a rare synthesis for the operator. Each call carries its
fork type. Everything else is deterministic: running campaigns, judging,
scheduling, indexing, the digest, alarms and their first response,
choosing the next experiment where rivals are already named.

**What dominates each experiment.**

| experiment | dominant cost | second |
|---|---|---|
| P1 | inference (building the kernel) | operator attention at the gate |
| P2 | GPU | inference |
| P3, P4, P5 | CPU | storage |
| P6 | inference (design) | CPU |
| P7 | CPU | inference |
| P8 | inference (the model arm) | CPU |
| P9 | GPU | inference |

**Totals** (ENGINE_PORTFOLIO.md section 12), at a planning floor of 100
million organism instructions per second on M1:

| | first 90 days | months 4 to 12 |
|---|---|---|
| CPU | about 29 M1-days of 90 | about 150 M1-days |
| GPU | about 60 hours | about 11 days |
| energy | about 160 kWh | about 800 kWh |
| tokens | order of 10^8 | order of 10^8 |
| operator | three gate reviews; a weekly digest; rulings | admissions at C3 and above |

Three consequences.

1. Electricity is not the binding constraint. A year is on the order of
   1,000 kWh. The energy figures rest on assumed wall power (200 W and
   350 W); nothing has ever been metered.
2. Tokens are the constraint, and they are front-loaded. Building the
   kernel, the worlds and the designed organisms is model work. After
   that, P3, P4 and P5 are configurations of existing code. If tokens
   become scarce after day 30, the maps keep filling with no model in the
   loop.
3. Utilisation is not an objective. The plan uses a third of the CPU on
   purpose.

**How each cost is measured.**

| cost | meter | status |
|---|---|---|
| tokens and dollars | one permitted model-call path, logging on by default, with model, tokens, cost and fork type | the layer exists; its log has never been enabled; the job fabric records dollars and drops tokens; one replay tool logs tokens for its own calls |
| CPU and GPU time | the runner, per campaign, on the receipt | new |
| energy | GPU from sampled power draw; CPU from utilisation times a factor calibrated once per host with a plug-in meter | new; no host has been metered |
| operator time | minutes per decision, from the decisions register | new |
| yield | section 19 | new |

The only inference cost measured in this package: seven salvage workers
used 4,174,516 tokens to characterise more than 143,000 lines of code.

----------------------------------------------------------------------

## 19. Scientific-yield model

**Not counted:** commits, experiments, agent activity, flags, "interesting"
observations. The old program had all of these in quantity.

**The prompt's ladder.** Anomaly, replication, baseline survival,
adversarial survival, causal intervention, transplantation, cross-world
transfer, cross-substrate transfer, mechanistic compression, externally
reproducible claim. The ingredients are right. As a single line it has
three faults.

1. It starts at an anomaly. That is the observe-first order. The scarce
   step comes before any anomaly: certifying the cell. A ladder that starts
   at "anomaly" gives no credit for the work that makes anomalies readable.
2. It has no rung for nulls or for instruments. In the first year most of
   the real yield will be qualified instruments and certified nulls.
3. The order is not the cheapest-kill-first order. Baseline survival is
   cheap and should precede replication, which is expensive. External
   reproducibility should not wait for cross-substrate transfer.

**Replacement.** The claim ladder C0 to C6, the null levels N1 and N2, and
instrument qualification as its own kind of result. The prompt's rungs map
onto it:

| the prompt's rung | here |
|---|---|
| anomaly | C0 |
| baseline survival, then replication | C1 (the ladder first, then five independent lineages) |
| adversarial survival | C2 |
| causal intervention; mechanistic compression | C3 |
| transplantation; cross-world transfer | C4 |
| cross-substrate transfer | C5 |
| externally reproducible claim | not a rung. Clean-clone reproduction on a second host is required from C2 (REPR-02) and a pack an outsider can run at C4 (REPR-07). What may be shown outside follows PUB-01 (section 20) |

**The yield table.** Per period, generated from the claim registry:

| counted | why |
|---|---|
| claim-level steps gained | the direct measure |
| claim-level steps LOST | a claim killed early is yield: it is cost not spent later. The old program's retractions were its most valuable output and were never counted as output |
| certified nulls (N1, N2) | they close cells |
| instruments qualified | they make everything else readable |
| forecast score | every prediction is registered with a probability and scored; a program that cannot forecast its own results does not understand them |

against kilowatt-hours, tokens and operator minutes.

Two derived ratios guide allocation: yield per token, and the fraction of
tokens spent on qualification (FALSIFIERS F-D8 fires if that exceeds 60%
at day 90 with fewer than six certified cells).

A first forecast score exists. For the prototype's search-power run I
registered six forecasts; five held; Brier 0.179 against 0.250 for always
saying one half. The miss was the informative one: I gave 0.97 to "no rule
recovers a builder from an empty program", and one did.

----------------------------------------------------------------------

## 20. Publication/externalization model

**The conflict.** Tracked doctrine HARD-1 forbids paper and publication
framing. The prompt's section 18 asks for externally legible artifacts. I
did not adopt section 18. What follows is what I would recommend if the
operator lifts or narrows HARD-1. Until then the default is no external
artifact.

**What qualifies** (PUB-01):

| artifact | qualifies when |
|---|---|
| instruments, world suites, failure fixtures | they reproduce from a clean clone on a second host |
| negative results | they reproduce from a clean clone; a null is worded as a null about the phenomenon only at N1, otherwise as a null about the apparatus |
| effects | C2 |
| mechanisms | C3 |
| principles | C5 |

Every external claim ships its reproduction pack and cites its claim level
(PUB-02), and its wording stays under its ceiling (PUB-03).

**What I would externalise first** (PUB-05): the instruments and the
negatives. They are the part most likely to be right and most useful to
others.

1. The certified world suite with its bounds, twins and baseline ladders,
   and the qualification harness. A benchmark in the useful sense: it
   comes with what a memoryless, a non-adaptive, a no-carry and a lookup
   policy can score, exactly.
2. The failure-fixture corpus: real defects, each with the check that
   catches it.
3. A methods note on the four certificates and on why nulls from small
   evolutionary engines were uninterpretable, with the old record as the
   worked example.
4. The reference-arm maps, whichever way H1b falls.
5. Later: the emergence map and the transition maps.

**On the professional portfolio.** Genuine work should end in forms an
outsider can inspect. The package that would serve that best is the first
one above: small, exact, reproducible, and unusual. It does not depend on
any claim about reasoning being true.

----------------------------------------------------------------------

## 21. First 90-day MVP

The aim is information about the architecture, not apparent success. Each
gate answers a question about whether the design is right.

### 21.1 What already exists

prototype/p1_slice/ is a miniature of P1, built and run on 2026-10-01
after the freeze: about 1,900 lines.

| question | result |
|---|---|
| Does the compiled kernel match a separately written oracle? | 3,672 comparisons, 0 mismatches; a deliberately wrong oracle is caught |
| Did the first gate pass? | No. One preregistered verdict came back INDETERMINATE. I had frozen thresholds and sample sizes without checking power. The failed receipt is kept. |
| Did the amended gate pass, on fresh sealed lives, with no threshold moved? | Yes: all 26 preregistered verdict cells and 8 fire tests as expected; the power gate covered 23 of the cells |
| Calibration | designed builders observed at 1.000, 0.814, 0.624 and 0.438 against known true rates of 1, 0.8125, 0.625 and 0.4375, each certified with a lower bound that never exceeds the true rate; holder, constant, lookup and leak reader at chance; the holder passes HOLD and fails BUILD |
| Causal rulers | the builder follows a transplanted store on 5,602 of 5,602 trials; the holder and a sham do not; lesion of used cells abolishes, of unused cells does not |
| The fire test to remember | with the harness's reset broken, the ruler alone passes a holder as a builder; only the separate reset-equivalence check catches it |
| Throughput with a world in the loop | 1.70 billion organism instructions per second on 12 threads |
| Search power | recovery of one missing instruction: 24, 9 or 1 of 24 lineages by acceptance rule; 0 of 2,000,000 random programs |
| What blind search found from nothing | one builder in 24 lineages, with a different mechanism from the designed one; certified before anyone understood it |

These are C0 observations about an instrument, by one author on one host.
They show the central instrument works mechanically at toy size. They say
nothing about the real workspace machine.

### 21.2 What gets built, and what gets reused

| built new | reused (SALVAGE_MATRIX row) |
|---|---|
| the five protocols and the runner with its refusal gates | toolbox receipt schema (I-02); Fabric lease (I-01) |
| the WM kernel, compiled, with a reference implementation | reference-plus-compiled pattern (O-04); Crius layout and designed programs (O-03) |
| RETAIN and RECALL with certificates, twins and ladders | event-stream grammar (W-01); cue task (W-12); twins and leak worlds (W-13, M-10) |
| TRACK and IDENTIFY with exact solvers | exact-Bayes streams (W-02) |
| the class-exclusion ruler library; interchange; lesion; reset equivalence | carrier-swap design and failure modes (C-02); store conditions (C-04); lockstep library (C-01) |
| the qualification gate | verdict type (M-01); certify and constancy (M-02); corruption operators (M-03); contract (W-09) |
| preregistration checks; the power gate | Harmonia primitives (M-05); attainability census (M-09) |
| the search-power instrument | reach classes (S-01); budget ladder (S-06); escrow and pairing (S-08) |
| the reference arm, four learners | none |
| meters for tokens, time and energy | model-call layer (I-08) |
| custody of sealed worlds | broker protocol (W-11) |
| the fixture suite, first 18 | Necropolis cases (M-12); list B of report 04 |

### 21.3 Which experiments exist in the first 90 days

P1 in full. P2 on four families. P3 on three relocations. P4 for ADAPT in
two substrates. P5 for BUILD from S5 to S3. Not P6 to P9.

- First organisms: designed only, through day 45. Builder, holder and the
  impostors; then designed organisms for HOLD and ADAPT.
- First worlds: RETAIN and RECALL; then TRACK and IDENTIFY.
- First pressures: delay and distractor load (RECALL); lifetime
  information and episodes per life (RETAIN); bits to identify and cost of
  observing (IDENTIFY).
- First developmental curricula: none beyond the episode structure of a
  life, until the ADAPT map, where a curriculum arm with rewarded
  intermediate stages tests the second half of H3.
- First rulers: class exclusion; interchange; lesion; reset equivalence;
  the leak probe; the search-power curve.

### 21.4 Schedule

| days | work | evidence at the gate |
|---|---|---|
| 0 to 10 | protocols; runner and gates; receipt; meters on from the first session; custody; WM kernel with reference and differential test; throughput measured | kernel conformance suite; a throughput number; a token log |
| 10 to 30 | P1 on the real WM: worlds, designed organisms, rulers, gate, first search-power curve; first 18 fixtures; golden trace replayed on a second host | **Day 30 gate**: calibration set sorted with measured error rates; every fire test fires; fixtures caught; two known-law recoveries (designed builders at their known rates; window learners on the enumerated floor of the Even process); replay bit for bit; token and energy totals |
| 30 to 60 | reference arm on four families; H1a as a conformance check; H1b retention curves; WM designed organisms for HOLD, ADAPT, BUILD with power curves; P3 starts at day 45 | **Day 60 gate**: the frontier table exists with certified levels for REF on T1 to T3; reference signatures stored; power curves for three relocations in WM; a first read on whether the axes separate |
| 60 to 90 | knockout matrix for T1 to T3; ADAPT transition map in REF and WM with H2 and H3 predictions registered first; BUILD descent S5 to S3; one world and one ruler re-implemented independently and differentially tested | **Day 90 gate**: the matrix; the map with predictions scored; the descent; the differential test; the yield table; a decision record on which substrates continue and what is cut |

### 21.5 Kill gates

| when | condition | action |
|---|---|---|
| first kernel build | below 10 million instructions per second | rewrite the hot loop before any campaign (F-D10) |
| day 45 | calibration set not sorted at 95% with a 95% lower limit, or a fire test that cannot fail | stop everything else; simplify the kernel (F-D1) |
| any time | the smuggler passes BUILD, or reset equivalence fails | no BUILD claim until the channel is closed (F-D3) |
| day 60 | the reference arm cannot reach its known ceiling on RECALL and TRACK | rebuild its training before any comparison |
| day 90 | over 60% of tokens on qualification and fewer than six certified cells | cut the open arms, P8 and P9; one substrate plus the reference arm; re-plan (F-D8) |
| day 90 | a second implementation unobtainable within a tenth of the first's cost | cap claims at C2 and say so (F-D4) |

### 21.6 Compute and inference boundaries

About 29 M1-days of CPU and 60 GPU-hours; about 160 kWh. No model runs
inside any campaign. Models work at the typed forks only, and the token log
carries the fork type from day 0. No model writes a status file, a queue or
a ledger.

### 21.7 What each gate tells us about the architecture

- Day 30: whether class exclusion is practical on the real machine, and
  what the kernel really costs in tokens. If it is not practical, the
  design's central instrument is wrong and that is known in a month.
- Day 60: whether conventional learners already do everything the first
  three relocations ask (toward F-T1); whether the axes separate at all
  (toward F-T3).
- Day 90: whether payoff times reach has any predictive value in one
  relocation; whether search gets below S4; whether an independent
  implementation is obtainable; what fraction of effort went to
  qualification.

----------------------------------------------------------------------

## 22. 6-12 month experimental program

**Phase 3B, months 4 to 8: the two maps and the second substrate.**

| work | question it settles |
|---|---|
| PN built and qualified through P1's gate | is BUILD native in a network, and is its reach better than WM's (H5) |
| descent to S2 where reach allows, in WM and PN | emergence depth per capability |
| transition maps for BUILD and COMPRESS in three substrates | H2 and H3 beyond one relocation |
| RECOMBINE with withheld kinds of structure; the reference arm on it | H1b, the compression half |
| CHAIN and its certificate; designed organisms for COMPOSE | is COMPOSE expressible and measurable; H4 |
| P7 pilot in DOUBT | do the four named tests separate organisms |
| P8 pilot in one certified cell | is a signature space usable; a first size for H7 |
| the construct-validity test | does small predict large (F-T2) |

Month 6 gate: PN on the frontier table; H1b decided; a COMPOSE ruler
qualified or declared not qualifiable; the designed adaptive learner for
RECURSE exists or P6 is reduced to COMPOSE.

Month 8 gate: three transition maps with predictions scored; the
construct-validity result; a decision on whether the program is still
about search or moves toward design (toward F-T4).

**Phase 3C, months 9 to 12: recursion, divergence, one open arm.**

| work | question it settles |
|---|---|
| P6 on CHAIN and FAMILIES | does savings compound; is anything found between the fixed and the adaptive learner (H6) |
| P8 in two certified cells | how much a model generator narrows what is found (H7) |
| P9: message passing through P1's gate, then T1 to T3 | a third kind of substrate on the frontier table |
| first mechanism claims at C3, where an independent ruler exists | whether the ladder above C2 is reachable in practice |
| the external package, if doctrine allows | PUB-05 |

Month 12 gate: the four standing tables; every hypothesis H1b to H7 with a
verdict or a reason it has none; the six thesis-level falsifiers
evaluated.

What is cut first if resources shrink: P9, then P8, then PN, then the
COMPRESS map. What is never cut: P1, the reference arm, the second
implementation behind any C3 claim.

----------------------------------------------------------------------

## 23. Falsifiers

FALSIFIERS.md gives thresholds. The ones that matter most, with when they
can fire.

**Of the thesis.**

| | what would be seen | what it would mean | when |
|---|---|---|---|
| F-T1 | conventional learners reach every certified level at equal or lower cost, and no certified mechanism lies outside their reference class | at this scale alternative substrates buy nothing; reduce to the instrument program or stop | month 12 |
| F-T2 | certified profiles do not predict performance on a richer transfer set (rank correlation below 0.5) | small does not predict large; redesign the worlds once, then reframe | month 8 |
| F-T3 | certified levels on the six axes move together (every pairwise correlation above 0.9) and no knockout moves one alone | there is one capability dimension here; collapse the axes | day 60 onward |
| F-T4 | nothing at BUILD or above regenerated below S4 in any substrate, at search power of at least 0.8 | search does not rebuild constructive machinery here; move from search to design | month 12 |
| F-T5 | H1b fails (amortised learners compress unseen kinds of structure, or weight-updating learners do so as cheaply as designed constructive organisms) AND the weight-updating reference learner passes BUILD, COMPRESS and COMPOSE at levels no other substrate exceeds | the gap is not where I put it; the apparatus stands and the target changes | month 6 for H1b; later for the second half |
| F-T6 | fewer than twelve certified cells at month 12, with more than half of all tokens spent on qualification (added by annotation) | the design is too heavy for the resources there are | month 12 |

**Of the hypotheses**: F-H1a (a conformance check), F-H1b, F-H2 (payoff),
F-H3 (reach), F-H4 (addressing), F-H5 (opposite weaknesses), F-H6
(compounding), F-H7 (prior restriction).

**Of design components**: ten, from "the kernel cannot be qualified" (day
45) to "throughput is far below the estimate".

**What would not falsify anything**: a run in which nothing interesting was
seen, without the four certificates; a mechanism no model can describe;
agreement between two runs of the same code; a striking positive at C0 or
C1; my own, or any model's, judgement that a result looks right.

Already fired, in miniature: my frozen H1 was not a hypothesis (corrected);
my first prototype gate was underpowered (corrected, with the failed
receipt kept); and two read-only reviewers found about 80 defects in this
package before it was pushed, most of them my overstating a source. Those
are corrected, and the kinds are listed in the seat's calibration ledger.

----------------------------------------------------------------------

## 24. Explicit answers Q1-Q10

### Q1 -- Scientific legitimacy

**Premature science.** It is not hobby research: preregistration,
controls, hostile review and public retraction were practised, often
strictly, and most corrections came from the claiming seat, often within
hours. It is not yet science about cognition: no result excludes a simpler
explanation, because no world shipped a computed bound for a restricted
policy class, no search had measured power, and 30 of 152 instrument
records showed demonstrated detectability. The positives that survive are
mostly about instruments.

Evidence: sections 2 to 5.

What Phase 3 must change: certificates before inference; rulers qualified
by a gate in code; claims on a ladder with ceilings; verdicts written by a
party the generator and the interpreter cannot write to; independence
stated on every claim.

### Q2 -- Cognitive sufficiency

A negative result becomes interpretable when the cell holds all four
certificates and stated power. Concretely:

- the world has a demand certificate, with the capability beating every
  restricted class by at least four times the ruler's minimum detectable
  effect, net of cost;
- a designed organism in the same substrate passes the same ruler inside
  half the size limits, with a lifetime in which it acquires what it needs;
- search recovers planted targets of the designed organism's needle size
  with power of at least 0.8, under more than one acceptance rule;
- the ruler is qualified.

Then the null says: this capability, at this level, did not appear at this
scaffold level, in this substrate, under this regime, with power p for
targets of this size. It never says "no reasoning". For generality it must
repeat in two substrates and two regimes.

The limit: reach is measured on targets I designed. A mechanism nobody
designed may be nearer or farther.

### Q3 -- Developmental adequacy

**Machinery required**: three stores under harness control; the eight
affordances of section 7; the learning machinery inside the organism; cost
for time and storage; a lifetime with structure.

**What does the compression**: the organism's own lifetime-writable code,
when storage is priced and tests are new combinations. In WM, programs
that rewrite stored blocks. In PN, plasticity with pruning under rent.

**What produces abstractions**: the pressure, not a module. A store capped
below the number of situations, tested on combinations never seen. An
abstraction is then certified by three things: one lesion harms several
surface-distinct tasks; the benefit survives scrambling; a transplant
confers it.

**How structures become reusable objects**: by having an address that
survives structural change, and by being invocable with arguments. Whether
both are necessary is H4.

### Q4 -- Evolution versus development

- **Evolution specifies**: the learning machinery, as a small initial
  store. Not the content. The size cap on the genome is a dial.
- **Development constructs**: everything specific to a life: its hidden
  parameters, its mappings, its regularities, its callable units, and
  changes to its own procedure.
- **The world teaches through scarcity**: hidden state and delay; variation
  larger than inherited capacity; resets; priced storage with novelty;
  depth with a step budget; families that share meta-structure; misleading
  evidence with costly commitment.

The division is not fixed by me. The store-and-timescale law predicts it:
information goes to the store whose lifetime matches the timescale of its
variation. Both switches (development off; outer search off) exist so the
attribution is measured.

### Q5 -- Recursive sagacity

**Definition**: sagacity is cost saved on withheld task families per bit
of structure carried forward. Recursive sagacity is sagacity whose rate of
production rises because of what the organism built.

**What would demonstrate something beyond learning to learn**: acquisition
cost falling with developmental age on out-of-span families, which need
something no earlier family needed and on which a fixed-procedure learner
shows no gain by construction; the gain removed by lesioning the built
structure and conferred by transplanting it; a memorising impostor showing
nothing.

### Q6 -- Epistemic escape

**Plausibly, and it is unproven.** A model can propose machinery outside
the familiar if what admits a candidate needs no ontology. Class exclusion
is that: a bound is beaten or not.

**How we would know**: P8 compares mechanisms found by a model and by
blind variation in the same cell at equal evaluations. "Unfamiliar" is a
measured distance from the signatures of conventional learners, never "a
model could not name it".

**How to keep unfamiliar mechanisms from being discarded**: admission by
certificate numbers only; a declared share of blind variation; a queue
that raises the priority of what is certified and unclassified; unauthored
worlds; open substrate arms. And no model as judge, classifier or gate.

### Q7 -- Single engine versus portfolio

**Neither.** One kernel, one foundry of certified worlds, a reference arm,
a few unlike substrates, and question-shaped experiments.

One engine cannot support a statement across substrates, and every null
from it is ambiguous. Many independent engines is what v2 was: no ruler
transferred and agreement was self-agreement. A shared kernel makes results
comparable; unlike substrates make agreement mean something.

The first 90 days are mostly instrument qualification. Calibrated search
follows. Open-ended search under survival pressure alone comes last, if at
all.

### Q8 -- Existing machinery

Of 72 decision rows of scientific machinery: none kept as it is; 8 enter
after hardening; 36 give up a primitive, about half of them as a design
and its fixtures and not as code; 5 are needs to rebuild; 9 are kept as
controls; 10 are retired; 4 are unknown.

**Conceptually about half survives, as primitives, designs and fixtures.
As running code, about a tenth. As engines, none.** Infrastructure fares
better. What survives best is what was written last: the instruments seats
built in September after their own results failed audit.

### Q9 -- First experiments

The smallest experiments that discriminate between architectures:

| experiment | cost | what it decides |
|---|---|---|
| P1, the calibration slice | weeks; almost no compute | whether instrument-first is practical at all, against observe-first |
| H1b on RECOMBINE | about a month after P2 | whether the target is construction within a lifetime, or elsewhere |
| a knockout on one relocation | days of CPU | whether affordances matter, which decides program-like against network-like as the primary substrate |
| one transition map with the payoff-times-reach prediction | about 8 M1-days | whether emergence is predictable, which decides a staged program against a soup |
| a descent on BUILD to S3 and S2 | about 6 to 16 M1-days | the weight of search against design |
| the construct-validity test | months 4 to 8 | whether the small-world method is the right tool |
| a P8 pilot in one cell | days, plus tokens | how much blind share is needed |

The first has been run in miniature.

### Q10 -- Failure

Any one of the first five in section 23. In one sentence each:

- conventional learners match everything and nothing lies outside their
  reference class;
- small does not predict large;
- the six axes are one;
- nothing regenerates below S4;
- amortised learners already compress what they never saw, and
  conventional weight-updating learners match every other substrate
  through COMPOSE.

A sixth is institutional (F-T6, added to FALSIFIERS.md by annotation): at
month 12 the frontier table has fewer than twelve certified cells and more
than half of all tokens went to qualification. Then the design is too
heavy to run with the resources there are, whatever its merits.

----------------------------------------------------------------------

## 25. Highest-value unresolved questions

Seven, from OPEN_QUESTIONS.md, ordered by what they would change.

1. **Does small predict large?** Everything above the kernel depends on
   it. The transfer set that would test it is not yet designed.
2. **Will the operator accept ninety days of instruments before any claim
   about reasoning?** This is the trade the design makes. It needs a yes or
   a no.
3. **Is a second model family reachable from code?** Without it claims
   stop at C2.
4. **Can a positive control for RECURSE be built at toy scale?** If not,
   the question the program is named for cannot be asked with a qualified
   ruler.
5. **Does reach on planted targets say anything about targets nobody
   designed?** If not, certified nulls are weaker than they look.
6. **Are the six relocations the right axes?** An organism that develops
   along an axis nobody defined would be measured only in uncertified
   worlds.
7. **What makes two mechanisms the same?** P8 and the reference class both
   need a signature space, and none exists.

Three doctrine points also wait on the operator: publication framing,
prior art, and fixed axes against the North Star.

----------------------------------------------------------------------

## Final question

*If Prometheus were being started today with everything we have now
learned, but none of its existing engines had yet been written, what would
you build first, and why?*

One end-to-end calibration slice for a single capability, BUILD: a world
small enough to carry an exact bound on what any policy can score if it
carries nothing across a reset; a compiled organism kernel whose stores the
harness controls; a designed organism that builds, one that only holds, and
the cheapest cheats; rulers in exact arithmetic; and a gate that refuses to
run until every preregistered verdict is attainable and every control has
been made to fail. Then one search-power curve on it. I would build this
first because every failure in the record traces to its absence: positives
that a cheaper policy explained, nulls that could not be told from a short
search or a blind ruler, controls that could not fail, rules that lived in
prose. It is the smallest thing that makes both a positive and a null mean
something, it tests the design's central instrument before anything
depends on it, and it costs weeks, not months. I chose BUILD because it is
the first capability that a learner with only fast state cannot have, by
construction, so it marks the edge of the paradigm the operator wants to
see past. I built a miniature today. Its first gate failed on an error of
mine that a requirement I had written that morning should have prevented,
and a table compared in code caught what the written rule did not. That is
the argument for building this first, in one result.
