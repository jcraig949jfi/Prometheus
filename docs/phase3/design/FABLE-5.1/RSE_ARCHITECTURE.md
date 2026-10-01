# Prometheus Phase 3 -- proposed architecture

Architect: FABLE-5.1 (seat Dionysus). Companion to REQUIREMENTS.md, which
defines every term used here (certificates, relocations T1 to T6, scaffold
levels S5 to S0, claim levels C0 to C6, independence levels I0 to I4).

Status: sections 1 to 12 were written and committed together with
REQUIREMENTS.md, before any salvage analysis. They name no existing
Prometheus component. Section 13 was added after salvage and says which
existing components fill which slot. The engine-by-engine detail is in
ENGINE_PORTFOLIO.md.

----------------------------------------------------------------------

## 1. The proposal in one page

**What Phase 3 studies.** The physics of within-lifetime construction: when
and how a system moves information from experience into structure that
persists, compresses, becomes callable, and improves the process that built
it. REQUIREMENTS.md section 1.5 names six such relocations: HOLD, ADAPT,
BUILD, COMPRESS, COMPOSE, RECURSE.

**Why that target.** A transformer does HOLD and ADAPT at very large scale
inside a context window. COMPRESS and COMPOSE happened to it once, offline,
in training. Within a deployed lifetime it does not BUILD: nothing it
experiences becomes persistent structure that it then computes with. That
is an argument, not a measured fact, and the first experiments test it
(hypothesis H1). If it holds, the place to look for architectures beyond
the current paradigm is BUILD and above, and those relocations can be
studied at small scale because they are about where information sits and
how it is reused, not about how much knowledge a system has.

**How Phase 3 differs from v1 and v2.** The old loop was: build a small
engine, watch it, interpret, audit afterwards. The crawlers show the same
four gaps under most results: the world did not require the phenomenon, the
organism could not hold it, the search could not reach it, the ruler could
not detect it. Phase 3 reverses the order. For every cell it first
establishes DEMAND, EXPRESSIBILITY, REACH and DETECTABILITY, and only then
runs the open question.

**Three methods carry the design.**

1. Class exclusion. A world ships the exact best score of every restricted
   policy class. An organism that beats a bound on sealed worlds is
   certified outside that class. No interpretation, no model, no ontology.
2. Descent from existence proofs. Each capability starts from a designed
   organism that provably has it (scaffold level S5). Scaffolding is then
   removed one level at a time and search is asked to regenerate what was
   removed. The lowest level reached is the measured emergence depth.
   Ascent from below runs too, and its nulls are readable because the
   descent calibrated them.
3. A null model for emergence. The working hypothesis is that a relocation
   appears where it pays and where search can reach it, and that both
   factors can be measured in advance: payoff from the world certificate and
   the plant's cost, reach from the search-power curve. Where the product
   predicts the transition map, emergence is designable. Where it fails,
   the residual is the interesting physics.

**Shape.** One shared measurement kernel. One foundry of demand-certified
worlds. One conventional reference arm. Two unlike constructive substrates
with switchable affordances. Further substrates admitted one at a time
through the same gate. Nine experiments, each with one question, run as
deterministic campaigns.

**What "RSE" means here.** Recursive sagacity is a property with a test
(XFER-07), not a machine. Any substrate may pass it. Nothing in Phase 3 is
named "the RSE".

**What is built first.** One end-to-end calibration slice for BUILD: a
certified world that requires carrying information across fast-state
resets, a designed organism that does it, one that cannot, the cheapest
cheats, and rulers that sort them with known error rates.

----------------------------------------------------------------------

## 2. Alternatives considered

The prompt asks for one engine, a portfolio, a staged observatory, or
something else, chosen for scientific discrimination.

| option | what it is | why not, or why | what would distinguish it from my choice |
|---|---|---|---|
| A. One integrated engine | one substrate, one world system, one search, built to grow a reasoner | A single cell cannot support a cross-substrate statement (SCI-07), and every null from it is ambiguous between its world, organism, search and ruler. This is the v2 engine at larger size. | If one substrate dominated every relocation at every scaffold level in the first two substrates tested, a single engine would be justified afterwards. |
| B. Six to twelve independent engines | each with its own substrate, worlds, rulers and seat | This is what v2 was. Sisyphus found the engines shared a few substrates and one author family, so agreement between them was self-agreement, and no ruler transferred (2 of 146 tested across substrates). | Nothing; the record already ran this experiment. |
| C. Instrument program only | build certified worlds and rulers, run only conventional learners | Safe and useful, but it gives up the question the program exists for. | If the reference arm reaches every certified level cheaply and no other substrate adds a mechanism outside its class, the program reduces to this (FALSIFIERS F2). |
| D. Scale first | rent GPUs, train large meta-learners, look for construction at scale | It repeats the conventional paradigm at a size a home laboratory cannot win at, and tests nothing about alternatives. | H1 failing: if a conventional in-context learner certifies BUILD beyond its fast capacity. |
| E. Soup first | open-ended ecology with survival pressure only (S0) | Nulls at S0 are the least interpretable in the whole design. It is the North Star's destination, so it stays in the plan as the bottom of the descent. | Any S2 result certified first. |
| F. Shared kernel, certified worlds, a reference arm, few unlike substrates, question-shaped experiments (chosen) | section 3 | Every experiment shares rulers and worlds, so results compare. Substrates differ in kind, so agreement means something. Nulls carry certificates. | -- |

The count of engines is a consequence, not a goal. It is nine experiments
on three shared infrastructure components and, to start, three substrates.

----------------------------------------------------------------------

## 3. Layers

    +------------------------------------------------------------------+
    | CLAIMS      claim registry (C0..C6, N1..N2)   frontier table      |
    |             emergence map   transition map    yield table         |
    +------------------------------------------------------------------+
    | EXPERIMENTS P1 calibration slice   P2 reference arm               |
    |             P3 affordance knockout P4 transition mapper           |
    |             P5 scaffold descent    P6 fork lab                    |
    |             P7 doubt and reliability  P8 generator divergence     |
    |             P9 open substrate arms                                |
    +------------------------------------------------------------------+
    | RULERS      class exclusion   interchange and lesion              |
    |             fork and savings  signature and reference class       |
    |             search-power curve   cost meters                      |
    |             each with a datasheet and a qualification receipt     |
    +---------------------------+--------------------------------------+
    | WORLDS                    | SUBSTRATES                           |
    | certified families,       | REF  conventional reference arm      |
    | one per relocation,       | WM   workspace machine               |
    | plus doubt, plus mined;   | PN   plastic network                 |
    | baseline ladder, twins,   | open arms, admitted one at a time    |
    | sealed sets               | each with designed organisms (plants)|
    +---------------------------+--------------------------------------+
    | PROTOCOLS   organism   world   search   ruler   receipt          |
    +------------------------------------------------------------------+
    | KERNEL      deterministic runner, one queue, one ledger,         |
    |             qualification gate, sealed-world broker,             |
    |             failure fixtures, derived index and dashboard        |
    +------------------------------------------------------------------+

    Authority runs across the layers, enforced by write permissions:

      GENERATION     proposes organisms, worlds, hypotheses   (models, mutation, search)
      REALITY        decides survival and verdicts            (worlds, rulers, interventions)
      INTERPRETATION describes and proposes experiments       (models, operator)

    Interpretation cannot write to the claim registry, the archive or the
    verdict tables. Generation cannot write verdicts.

----------------------------------------------------------------------

## 4. The kernel

The kernel is the part every experiment shares. It is infrastructure, and
it is where the historical failure classes are made hard to commit.

**Protocols.** Five interfaces: organism (ORG-01), world (WLD-01), search,
ruler, receipt (PROV-01). A substrate, a world family or a ruler is a
plug-in that passes a conformance suite.

**Physics rules.** Integers only. Counter-based randomness keyed by seed,
lineage, tick and purpose. Every genome decodes. Exact snapshot, restore
and fork. A state partition that the harness, not the organism, controls.

**Runner.** A campaign is a preregistered, deterministic, resumable batch
job. The runner refuses to start without: a preregistration commit that is
an ancestor of the code; a verdict table shown total and reachable on
synthetic organisms; current qualification receipts for every ruler; a
baseline ladder for every world; budget caps. It writes rows through one
writer and never calls git from campaign code.

**Qualification gate.** For each ruler: sort the calibration set, pass the
channel test, and pass a fire test for every control. The kernel's own test
suite breaks each control in turn and expects a failure. This is the base
role's rule on negative, positive and cheat controls, as code.

**Failure fixtures.** The failure taxonomy is compiled into executable
cases: an answer key inside a probe, a generator that writes its own
verdict, a control that cannot fail, a baseline that arrives late, a
verdict table with a gap, a selection on the evaluation set, a transplant
under a "spontaneous" label, a hash over host bytes, and so on. The kernel
must catch each. A new failure found later becomes a new fixture. This is
the record used as a control corpus.

**Derived state.** The index, the dashboard and the operator digest are
generated by code from receipts. Nothing in them is written by a model.

**Independence.** The world solvers, the baseline ladder and the rulers
behind any C3 claim exist in a second implementation written from the
specification by a different author, where possible a different model
family, and the two are differentially tested.

----------------------------------------------------------------------

## 5. The world foundry

One generator per world family. Every claim-bearing family ships its demand
certificate, baseline ladder, absence twin, scrambled twin, sealed-set
generator and leak-probe receipt. Admission is control-first: the family's
specification is frozen only after its designed organisms attain every
verdict and an automated cheap-policy search fails to beat any bound.

Families, by the relocation they demand. The dials are what is varied one
at a time.

| family | demands | one-sentence physics | dials | how the bound is obtained |
|---|---|---|---|---|
| RECALL | HOLD | a cue, a delay with distractors, a probe | symbols N, items, delay, distractor load | information bound: C bits carried gives at most 2^C / N |
| TRACK | HOLD, toward ADAPT | a hidden process with a known number of causal states emits symbols; predict the next | causal states, memory length, noise | exact Bayes predictor from the generating machine; best k-state predictor by enumeration |
| IDENTIFY | ADAPT | each episode draws a hidden rule from a family; evidence arrives by acting | bits to identify, evidence per observation, cost of observing, rate of change | exact Bayes-adaptive value by dynamic programming on small instances; best non-adaptive policy by enumeration |
| RETAIN | BUILD | a life of many episodes shares a hidden mapping; fast state is reset between episodes; probes are first presentations within an episode | mapping bits, episodes per life, evidence per episode, storage rent | exact: with nothing carried across episodes, probe accuracy is chance |
| RECOMBINE | COMPRESS | situations are combinations of factors; a life covers a fraction; the store is capped below the number of distinct situations; tests are unseen combinations balanced against surface similarity | factors, values, coverage, store cap, rent | counting bound for a lookup of the permitted size; by construction similarity-based guessing is at chance |
| CHAIN | COMPOSE | a task is a composition of learned transformations to depth D, to be solved within a step budget below flat search | depth D, branching b, step budget, primitives; curriculum arm | exhaustive flat search cost against budget; designed no-reuse solver as the negative |
| FAMILIES | RECURSE | a life contains many learning episodes over task families that share meta-structure; later families need something no earlier one did | number of families, depth of meta-structure, distance of the out-of-span families | designed fixed-procedure learner as the negative; designed adaptive-procedure learner as the positive |
| DOUBT | uncertainty and revision | early evidence misleads; observing costs; committing is irreversible and costly when wrong; an opt-out exists; rules change | misleading strength, observation cost, commitment cost, hazard rate | exact value of the Bayes-optimal policy; exact value of commit-on-first-evidence and never-revise policies |
| MINED | unauthored | small decision processes and generative programs sampled at random, kept by computed demand vector | the target demand vector | bounds by enumeration on the sampled instance |

Three properties matter more than the list.

- Worlds are small and deep, not large. Depth is the certified gap between
  what a restricted class can score and what the capability scores.
- The dials are factorised, so an organism has a threshold on each axis,
  found by an adaptive staircase, with a stated resolution.
- A later step tests construct validity (WLD-12): whether profiles measured
  here predict behaviour in richer worlds that have no certificate. If they
  do not, this foundry measures the wrong thing, and that is a named
  falsifier.

----------------------------------------------------------------------

## 6. Substrates

Three to start. They are chosen to differ in kind, so that agreement
between them is evidence and disagreement is informative.

### 6.1 REF -- the conventional reference arm

Small conventional learners run through the same worlds, rulers and probes:

- a recurrent network trained to imitate the exact Bayes-optimal policy
  (cheap, because the foundry already has that policy);
- an in-context sequence model with a fixed window;
- a small network trained online by gradient descent during the lifetime.

It serves four purposes: it shows each world is climbable; it gives the
measured reference class for "unfamiliar" (ANTI-05); it gives the cost
baseline per certified level; and it tests H1 directly, because the first
two have only fast state and the third writes persistent structure.

It is a control and a candidate under the same certificates. It is not the
default organism (ANTI-08).

### 6.2 WM -- the workspace machine (primary constructive candidate)

A stored-program organism designed around the affordances in ORG-03, each
with an off switch.

- Fast state: a few integer registers and a small stack, reset by the
  harness at episode boundaries.
- Persistent structure: a store of blocks. A block is a tag plus a body of
  fixed-width integer words. A word is data or an instruction; every word
  decodes.
- Addressing: by nearest tag within a radius, so inserting or deleting a
  block does not break references to the others.
- Instructions, about thirty: integer arithmetic and logic; read and write
  a block cell by tag and offset; conditional skip; bounded loop; call a
  block by tag with the current stack, and return; create, delete, copy and
  append to blocks; read an observation component; emit an action.
- Internal steps: the organism runs until it acts, up to a step cap per
  world tick. Every instruction costs energy. Every stored cell costs rent
  per tick. Energy comes from reward.
- Genome: the initial store, with a size cap.
- The learning machinery is the organism's own code. Nothing outside the
  organism writes its store.

Switches for the knockout experiment: store writes; conditional
instructions; call and return; tag addressing against absolute addressing;
step cap of one against many; block creation and deletion; zero rent
against positive rent.

Why it is the primary candidate. It can express every relocation through
RECURSE at small size, because code and data are the same material and
built structure can be named and invoked. Its weakness is reach: program
spaces are hard to search. The descent method exists to measure exactly
that weakness instead of tripping over it.

### 6.3 PN -- the plastic network

A recurrent network in fixed-point integers. Activations are fast state.
Weights and topology are persistent structure. The genome holds initial
wiring statistics and the parameters of local plasticity and of structural
growth and pruning. A modulatory signal can gate plasticity. Outer search
is by evolution strategies, and by gradient through the lifetime as a
labelled optimiser arm.

Switches: plasticity; structural change; modulatory gating; and one
knock-in contrast at scaffold level S3, a key-addressed memory.

Why it is second. BUILD is native here, since weights are lifetime-written
structure, and reach is good, since small changes have small effects. Its
predicted weakness is COMPOSE: nothing in it names and invokes built
structure with arguments. Hypothesis H5 is that WM and PN fail in opposite
places. If so, the interesting substrate is one with PN's reach and WM's
addressing, and the open arms should look for it.

### 6.4 Open arms

Further substrates are admitted one at a time, never more than one new
substrate under qualification at once. A candidate is admitted when it
implements the organism protocol, has measured throughput, and has designed
organisms for HOLD and ADAPT, or else states that its nulls will be
labelled NOT_SHOWN_EXPRESSIBLE.

Candidate kinds, each with the distinct question it would buy:

- function chemistry (expressions that act on expressions, under a
  conservation law): does invocation arise without designed addressing?
- lattice or cellular dynamics with local rules: can spatial locality carry
  BUILD without a store?
- message-passing media (state carried in transit between sites): is there
  a memory primitive that is neither register nor weight?
- tensor-network organisms (a chain or tree of small tensors with a bond
  dimension): bond dimension is an exact capacity dial, which makes a
  capacity law testable.

No open arm starts before P1 to P3 have qualified the kernel on WM, PN and
REF.

----------------------------------------------------------------------

## 7. The experiments

Each is a program of campaigns on the shared kernel. One question each.
Detail, including qualification sets, cheap baselines, kill criteria and
claim ceilings, is in ENGINE_PORTFOLIO.md.

| id | name | the one question | first relocations | needs |
|---|---|---|---|---|
| P1 | calibration slice | Can the apparatus tell a builder from a holder from a cheat when the answer is known? | BUILD | kernel, RETAIN, WM plants |
| P2 | reference arm | What do conventional learners certify on each relocation, at what cost, with what signatures, and where do they stop? | T1 to T4 | P1, REF |
| P3 | affordance knockout | Which organism affordances are necessary for which relocation under calibrated search? | T1 to T3, then T5 | P1, WM |
| P4 | transition mapper | Where does each relocation appear as pressure dials vary, and does payoff times reach predict it in every substrate? | ADAPT, BUILD, COMPRESS | P2, P3 |
| P5 | scaffold descent | How far below a designed organism can each capability be regenerated by search? | T1 to T5 | P3 |
| P6 | fork lab | Do built structures reduce the cost of later acquisition, and does the reduction compound? | COMPRESS, COMPOSE, RECURSE | P5 |
| P7 | doubt and reliability | Under misleading evidence and costly commitment, do organisms come to hold alternatives, seek evidence, revise, and monitor their own reliability? | cross-cutting | P2, P3 |
| P8 | generator divergence | At equal certified level, does model-guided generation find a narrower set of mechanisms than blind variation? | whichever is certified at S3 or below | P5 |
| P9 | open substrate arms | Do substrates unlike programs and networks reach the same levels by mechanisms outside the reference class? | T1 to T3 first | P1 to P3 qualified |

Order of dependence: P1 qualifies the chain. P2 and P3 fill the first rows
of the frontier table and give the reference class and the power curves.
P4 and P5 produce the two maps. P6 is where recursion is tested. P7 runs
alongside from P2 onward. P8 and P9 need certified cells to compare.

----------------------------------------------------------------------

## 8. The hypotheses the architecture is built to test

Each has a prediction made before the run and a named way to fail
(FALSIFIERS.md gives the thresholds).

| id | hypothesis | prediction | decided by |
|---|---|---|---|
| H1 | The within-lifetime gap. Learners with only fast state certify no BUILD beyond their fast capacity. | In RETAIN, the fixed-window and Bayes-imitating reference learners sit at the no-carry bound once lifetime information exceeds their window; the online-gradient learner passes. | P2 |
| H2 | Payoff. A relocation appears only where its net payoff, computed from the world certificate and the designed organism's measured cost, is positive. | The transition boundary in each dial lies where computed payoff changes sign, within the stated resolution. | P4 |
| H3 | Reach. The gap between the payoff boundary and the observed boundary is predicted by the search-power curve at the needle size of the designed organism, and a curriculum that supplies intermediate rewarded stages shrinks it. | Observed transition probability equals payoff indicator times measured reach, with no fitted parameter. | P4, P5 |
| H4 | Addressing. COMPOSE needs addressing that survives structural change, plus invocation. | In WM, switching tag addressing to absolute addressing, or removing call, abolishes COMPOSE at S2 and S3 and leaves BUILD intact. | P3 |
| H5 | Opposite weaknesses. Program-like substrates express T5 and T6 at small size and are hard to reach; network-like substrates reach T1 to T4 and stall at T5. | The emergence map shows WM deeper in expressibility and shallower in reach than PN, crossing at COMPOSE. | P3, P5 |
| H6 | Compounding. In worlds with compositional depth, each built level cuts the cost of acquiring the next by a factor that grows with depth; in flat worlds it does not. | Savings ratio rises with stage in CHAIN and FAMILIES for the designed adaptive learner, and is flat for the fixed-procedure learner; any found organism is placed between them. | P6 |
| H7 | Prior restriction. Model-guided generation reaches certified levels faster and with lower signature diversity than blind variation. | Lower dispersion of mechanism signatures among model-guided finds at equal level; some blind finds outside the model-guided set. | P8 |

H2 and H3 together are the null model for emergence. If they hold across
three substrates, that is a C5 candidate: relocations occur where they pay
and can be reached, and both are measurable in advance. If they fail, the
places where they fail are the first real leads.

----------------------------------------------------------------------

## 9. The standing products

Four tables, generated by code from receipts.

- FRONTIER TABLE. Relocation by substrate: the highest certified level,
  for realisation and for capacity, with scaffold level, optimiser, cost and
  claim level. This is the program's trajectory. By the crawlers' account
  the most any v2 world demanded was about one bit of memory or a one-bit
  hidden mapping, and none of it was certified in this sense.
- EMERGENCE MAP. Relocation by substrate by scaffold level: reached or not,
  with search power. It fills from S5 downward.
- TRANSITION MAP. Per relocation, the dial space, with observed transition
  probability beside the payoff-times-reach prediction.
- YIELD TABLE. Claim-level steps gained and lost, certified nulls,
  instruments qualified, forecast score, against kilowatt-hours, tokens and
  operator minutes.

----------------------------------------------------------------------

## 10. Operating model

This section is a proposal to the operator. It retires no seat and changes
no charter. Those are operator acts.

**The unit of work is a campaign, not a seat.** A campaign goes through
fixed steps:

1. Specify. Question, map cell, prediction, forecast, verdict table. One
   commit. (Model fork, with the operator for anything at C3 or above.)
2. Build and qualify. Code, calibration set, qualification receipt.
3. Run. Deterministic, resumable, no model.
4. Judge. Rulers in a separate process write verdicts.
5. Attack. A different author, where possible a different model family,
   builds impostors and attacks against the result. Required for C2.
6. Interpret. Only after certification. Output is descriptions and next
   experiments, never verdicts.
7. Admit. The operator, for C3 and above.

**Three roles, taken per campaign and then dropped.** BUILDER writes
specifications and code. BREAKER builds attacks, impostors and second
implementations, and should not share a model family with the builder
where that can be arranged. OPERATOR admits and sets budgets. The runner is
code.

**No model writes state.** No heartbeats, no status files, no queues, no
ledgers by hand. One queue, one ledger, one decisions register, one digest.

**Inference happens at typed forks** (INF-02): specification,
implementation, independent re-implementation, attack, naming rivals,
interpretation, and a rare synthesis.

**Why this and not the fleet.** Ixion measured the alternative: about 60
seats, five control regimes in six days, coordination rising to 40% of
message traffic, 158 commits in four days that only moved state files, an
alarm unanswered for eight days because its responder was a session nobody
had scheduled. None of that was science. The deterministic parts of the
institution worked. The model-mediated parts were where it leaked.

----------------------------------------------------------------------

## 11. Phases and gates

**Phase 3A, days 0 to 90: qualify, then first maps.**

- Day 30 gate. Kernel conformance suite passes. P1 sorts its calibration
  set with measured error rates. Two known-law recoveries pass. The failure
  fixtures are caught. Throughput is measured. If the calibration set
  cannot be sorted by day 45, stop and simplify the kernel before anything
  else is built.
- Day 60 gate. REF has certified levels on T1 to T3 and the H1 result is
  in. WM has designed organisms for T1 to T3 and a search-power curve. The
  frontier table exists.
- Day 90 gate. The affordance knockout matrix for T1 to T3 on WM. The
  first transition map for ADAPT in REF and WM with the H2 and H3
  predictions scored. A descent on BUILD from S5 to S3. One world and one
  ruler re-implemented independently and differentially tested. A decision
  record: which substrates continue, which experiment is cut.

**Phase 3B, months 4 to 8: the two maps and the second substrate.** PN
qualified. Descent to S2 where reach allows. Transition maps for BUILD and
COMPRESS in three substrates. COMPOSE worlds and designed organisms. P7 and
P8 pilots. The construct-validity test.

**Phase 3C, months 9 to 12: recursion and the first external package.**
P6 on CHAIN and FAMILIES. One open arm. The certified world suite and the
qualification harness prepared as an external package, subject to the
operator's ruling on doctrine HARD-1.

The detailed 90-day plan, with compute and inference boundaries, is in
PHASE3_META_ANALYSIS.md section 21.

----------------------------------------------------------------------

## 12. What this architecture does not do, and where it departs from the prompt

Not done, on purpose:

- It does not re-score the historical record result by result. It compiles
  the failure classes into fixtures and re-tests a few old signals inside
  the new apparatus (SCI-12).
- It does not start from a soup, and it does not start from scale.
- It does not use a model as a judge of anything.
- It does not add seats or mythological names.
- It does not promise a reasoner. It promises a certified frontier that
  moves or a certified account of why it does not.

Departures from the architect prompt, each allowed by the charter's
latitude:

1. RSE is a property with a test, not an engine (prompt sections 1 and 11
   treat it as something to build).
2. Designed organisms are central, as calibration standards and as the top
   of the descent. The prompt leans toward emergence under pressure. The
   North Star permits this: reproducing a designed tool is "a calibration,
   not the goal".
3. Conventional learners and gradient descent are in the design as a
   reference arm and as one optimiser among several. The prompt's
   anti-gravity section allows them as controls. I go a step further and
   say the anti-prior rule is about admission and search mass, not about
   banning the strongest optimiser.
4. REACH is a fourth certificate. The prompt and the challenges document
   cover demand, capacity and ruler validity.
5. An operating model is part of the architecture. The prompt asks for
   inference and attention requirements; I answer with a structure.
6. On publication, I do not adopt the prompt's section 18 as written,
   because tracked doctrine HARD-1 still forbids it. I define what would
   qualify for externalisation and leave the doctrine change to the
   operator.
7. I ask for doctrine HARD-2 to be narrowed: prior art as data, with
   measured recall, becomes required after validation (ANTI-06).

One tension with the North Star, stated plainly. The North Star says
Prometheus supplies "primitives, environments, falsification instruments,
provenance and pressures -- not a predetermined reasoning architecture or
ladder". The six relocations are a predetermined set of measurement axes.
They do not prescribe a mechanism or an order, and the MINED family and the
open arms exist to keep the axes from becoming the only thing that can be
seen. But an organism that develops along an axis nobody defined would be
measured only in uncertified worlds. That is a real limit of this design,
and OPEN_QUESTIONS.md carries it.

----------------------------------------------------------------------

## 13. Slots filled after salvage

Added 2026-10-01, after SALVAGE_MATRIX.md. Sections 1 to 12 are unchanged
since the freeze (a0e3a4d03). Row ids (O-03, W-01, ...) are rows of
SALVAGE_MATRIX.md section 3.

### 13.1 What fills each slot

| layer | slot | filled by | status |
|---|---|---|---|
| kernel | queue and lease | Agent Fabric store and lease (I-01) | harden; workers are Linux-only, so Phase 3A runs a local runner on M1 under a Fabric lease |
| kernel | receipt, ledger | toolbox receipt.v1 (I-02), with a hash chain and prediction window (I-03) and database triggers for append-only records (I-04) | harden |
| kernel | verdict type | Charon three-valued checks with counts (M-01); Hecate contract in exact fractions (W-09); Techne measurement type (M-02) | extract |
| kernel | qualification gate | Techne certify and constancy probe (M-02); Hecate corruption operators (M-03); Ananke Wave-2 lockstep library (C-01) | extract, harden |
| kernel | preregistration checks | Harmonia primitives and adjudicator (M-05); Diomedes census (M-09) | extract |
| kernel | failure fixtures | Necropolis cases (M-12); 31 real defects in salvage report 04 list B; 30 in SALVAGE_MATRIX section 5 | port |
| kernel | sealed-world broker | Cosmos ordering-and-commitment protocol (W-11) | harden; custody is new |
| kernel | index, digest | Atlas tables (I-07); mailer and honest renderer (I-09) | harden |
| kernel | model-call path | prometheus_llm (I-08) | harden |
| worlds | RECALL | Archaeon event-stream grammar (W-01) | extract |
| worlds | TRACK, IDENTIFY | Ensorain exact-Bayes streams (W-02) | extract |
| worlds | RETAIN | none; the P1 prototype is the first version | new |
| worlds | RECOMBINE | Ensorain surrogate and pair-block holdout (W-03) | extract parts |
| worlds | CHAIN | compositional asks of W-01; exact closure method (S-09) | extract parts |
| worlds | FAMILIES | none | new |
| worlds | DOUBT | Ludus solver pattern (W-04); Cosmos misleading-hint dial (W-12) | extract parts |
| worlds | MINED | Hecate sampled finite systems (W-10) | extract |
| worlds | demand certificates | none: no code computes the best value of a restricted policy class | new |
| substrates | REF | none | new |
| substrates | WM | none as code; layout from Crius (O-03), conventions from Proteus (O-01), kernel pattern from D-5 (O-04) | rebuild |
| substrates | PN | none: no network in the tree keeps weights across episodes (O-11) | rebuild |
| substrates | first open arm | Ananke packet-tensor engine, message-passing (O-09) | harden, after P1 to P3 |
| rulers | class exclusion | none | new; first version in the P1 prototype |
| rulers | interchange, lesion | Ananke lens design and failure modes (C-02); Cosmos planted-system gate (C-03); Crius store conditions (C-04); Ares cuts (C-05) | extract |
| rulers | material tracing | Archaeon record format and fixtures (C-06) | extract; a tracer per substrate is new |
| rulers | search-power curve | vocabulary from Ergon and D-5 (S-06) | new; first version in the P1 prototype |
| rulers | cost meters | none | new |
| search | protocol | reach classes and typed states (S-01); escrow and keyed pairing (S-08) | extract |
| experiments | P6 negative control | Aphrodite engine as the fixed-procedure learner (O-13) | harden |
| experiments | P8 statistic | Theseus divergence statistic (S-07) | extract |

No old engine continues as an engine.

### 13.2 Adjustments the salvage evidence asks for

These add to the frozen sections. None removes anything.

1. To section 6.2 (WM). The Crius machine already has the three-store
   layout. Its defects become three kernel tests for WM: every instruction
   field decodes by modulus; no identifier counter is visible to the
   organism; no capability-specific opcode exists above scaffold level S3.
2. To section 4 (kernel) and DEV-04. The developmental control set gains an
   identifiers-only sham: the store's identifiers kept, its contents
   emptied.
3. To section 4 (rulers) and CAUS-03. An interchange verdict is reported
   over a sweep of swap ticks, with the declared state boundary on the row.
   Every intervention first passes a control-identity audit: it is not a
   no-op, not a constant, not identical by design to another arm, and it is
   reversible by a witness.
4. To section 10 (operating model). Phase 3A does not need a distributed
   queue. One host runs campaigns under one lease; the two small Linux nodes
   are used for clean-clone and cross-host replay.
5. To section 11 (gates). Sealed worlds leave the working tree by the day-30
   gate. The search-rule incident of 2026-10-01
   (salvage_reports/00_SEARCH_RULE_INCIDENT.md) is the reason.
6. To section 6.4 (open arms). The first open arm is named: message
   passing, on the Ananke engine. It still waits for P1 to P3.
7. To section 7, P6. The negative control exists. The positive control does
   not, and the old record is a warning: a fixed-procedure learner starting
   from nothing built no reusable structure in 8 of 8 runs.
8. To section 4. One vocabulary for controls, the five names of
   REQUIREMENTS 1.3. The old tree uses "cheat control" for three different
   things.

### 13.3 What the P1 prototype added

prototype/p1_slice/ is a working miniature of the calibration slice, built
and run on 2026-10-01 after the freeze. Its results are C0 observations
about an instrument. Four of them change how the first build is planned.

1. Throughput. With a world in the loop the compiled kernel ran 1.70
   billion organism instructions per second on 12 threads (1.86 million
   lifetimes per second). REQUIREMENTS assumed a factor of 10 below the toy
   benchmark; the measured factor is about 3. The planning figure of 100
   million instructions per second for the real WM kernel keeps a wide
   margin.
2. The harness is part of the instrument. With the fast-state reset
   deliberately broken, the BUILD ruler passed an organism that cannot
   build. Only a separate reset-equivalence check caught it. The kernel
   therefore qualifies the harness (ORG-02) with its own fire test, beside
   every ruler.
3. Power is a gate, not a paragraph. The first gate run failed because
   thresholds and sample sizes were frozen without checking that every
   preregistered verdict was attainable. The runner now computes exact power
   from the schedules alone, before any organism runs, and refuses below
   0.99.
4. The acceptance rule is a first-order factor in reach. Recovery of one
   missing instruction was 24, 9 or 1 of 24 lineages depending only on the
   rule, and no rule dominated across distances. Every search-power curve is
   therefore measured under at least three acceptance rules, and SRCH-01's
   "declared, varied factor" includes the acceptance rule by name.

It also produced one small unplanned observation. Blind search from an empty
program found a builder with no jump, which used never-written registers as
constants. Register initialisation is a world variable and is swept in P3.

### 13.4 Slots that stay empty

Fourteen components have no starting point in the tree. SALVAGE_MATRIX.md
section 4 lists them. The four the design leans on most: demand-certificate
solvers, the WM kernel, the search-power instrument and the runner's
refusal gates.

### 13.5 A correction to hypothesis H1

Added 2026-10-01, found while writing ENGINE_PORTFOLIO.md. Section 8 above
is left as frozen; this corrects how it is to be read.

H1 as written predicts that learners with only fast state sit at the
no-carry bound in RETAIN. In RETAIN the harness resets fast state at every
episode boundary, and the bound is exact for any policy that carries
nothing across the boundary. The prediction is therefore a theorem of the
state partition, and a violation could only be a leak. It is not a
hypothesis. I froze it as one, and that was an error.

H1 is split.

- H1a, conformance. Fast-state-only learners score at the no-carry bound on
  RETAIN probes. True by construction; kept as a kernel check.
- H1b, the empirical claim. A learner trained offline that can carry only
  activations or a token window through a lifetime, even when that state is
  not reset, (1) carries fewer bits as the gap and the interference grow,
  and (2) certifies COMPRESS within a lifetime only for kinds of structure
  present in its training distribution; on RECOMBINE families with withheld
  kinds of structure it falls to the lookup bound. A learner that updates
  weights during life passes on the withheld families at a sample cost at
  least ten times that of the designed constructive organism.

Consequences:

- Section 6.1 gains a fourth reference learner, REF-d: a sequence model
  with an external read-and-write memory. It is the conventional answer to
  "it cannot build", and it is BUILD by design at scaffold level S3.
- Section 11, day-60 gate: "the H1 result" means H1a as a conformance
  check, and H1b's retention curves. H1b's compression half needs
  RECOMBINE and falls in Phase 3B.
- Section 1's second paragraph still stands as an argument: a deployed
  transformer does not BUILD across context resets. That is a fact about
  its architecture, not something an experiment here could discover. What
  the experiments can discover is what H1b says: whether amortised learners
  compress, within a lifetime, structure of a kind their training never
  covered, and what it costs conventional machinery that is allowed to write
  weights or an external memory.
