# Project Moonshot -- Requirements & Design (v0.1 DRAFT FOR OPERATOR REVIEW)

Seat: Themis (prong 3). Status: DRAFT, uncommitted pending operator review. Charter:
roles/Themis/prompts/2026-10-05_charter/ (verbatim; governs where this doc differs). Full
running synthesis: operator auto-memory project_moonshot_rso_lane. Date: 2026-10-05.

Sections 10 (prior art) and 11.5 (cloud cost) are grounded in web research run for this doc:
a prior-art literature search and a cloud-pricing search. Citation years and spot prices marked
"verify" should be confirmed before any external use. All other sections synthesize the
2026-10-04/05 design conversation.

---

## 1. Executive summary

Project Moonshot asks whether a cheap, commodity compute substrate can grow *alternative
cognitive architectures* -- not by designing them, but by placing evolving organisms in
worlds where sagacity (depth of internalized world-model) is the only way to survive, and
then *measuring* that sagacity with an instrument that is structurally prevented from being
gamed. It is the third prong of a larger program: prong 1 keeps the existing Phase-2 engines
doing science; prong 2 builds the Recursive Sagacity Observatory (RSO, Phase 3); prong 3
(this project) is the hybrid neuro-symbolic engine that fuses deterministic AI with
neural/GPU/tensor tooling across an e-waste CPU cluster, a pair of GPU boxes, and the cloud.

The design is organized as a **signal-detection funnel**: generate candidates cheaply and
widely on e-waste CPUs; sift them with deterministic falsification; promote the rare survivor
to GPU and then cloud only after it clears **preregistered gates and a reachability
certificate**. The engine's distinctive commitments -- and the reasons it is a research
instrument rather than a hobby toy -- are: (a) survival is the only selection pressure and
sagacity is scored **offline** from replayable logs, so the measurement can never leak into
selection; (b) every verdict is checked against a **matched null** and the measuring
instrument is itself **calibrated against disguised known controls**; (c) a local "no signal"
is treated as *underpowered* unless reachability was demonstrated, so the system cannot
quietly produce false negatives; (d) all runs are byte-deterministic and replayable, so an
improved instrument can re-score the entire historical corpus for free.

Most of the hard machinery already exists in the repository and is reused rather than rebuilt
(S8). The genuinely new builds are small and specific (S7.4): a ruler-calibration harness and
a node auto-join path. The first experiment (S12) is deliberately tiny -- a delayed-cue
memory world and a floor-level sagacity detector -- chosen because it is the one rung where
ground truth exists to calibrate the instrument against.

## 2. Scientific premise and question

Evolution produced exactly one cognitive architecture that, trained on data far outside what
biology shaped it for, does mathematics, science and language. The premise of the program is
that this is *one point in a space of possible minds, not the only point*. If the primitives
that generate general reasoning can be isolated and dropped into a sufficiently rich,
selection-bearing "primordial soup," a *different* architecture could crystallize.

The motivating thesis (operator's north star; Silver's "LLMs are a dead end, self-discovery
is the path"): large language models have a gravitational pull toward the human corpus -- they
can only reach for what is already in their data -- so they are the wrong instrument to
*discover* a new architecture. You grow one; you do not retrieve it.

**Question (prong 3):** can a commodity, falsification-first evolutionary substrate detect and
then amplify the *first rung* of sagacity -- an organism conditioning action on information not
present in the current observation, in a way that improves survival (memory that pays) -- and
do so with an instrument rigorous enough that a positive result is believable and a negative
result is informative?

## 3. The sagacity scale and the measurement principle

**Sagacity (S)** grades the depth of the world-model an organism must have internalized to act
as it does. The operator's reference points, roughly log-scaled by counterfactual reach:
- S ~ 10: an organism evolves a bare survival mechanism in a small digital world.
- S ~ 1,000: toddler-grade object permanence -- the ball rolled behind the couch, it did not
  cease to exist.
- S ~ 10,000,000: a scientist runs a thought experiment over two objects in spacetime and
  proposes a grand hypothesis.

The scale doubles as a **world-design specification**: a rung is only *selectable* if the
world makes that capability survival-relevant.
- S ~ 10 needs differential survival + heritable variation.
- S ~ 1,000 needs **partial observability** -- things must leave and re-enter observation, and
  tracking the unobserved must pay. A fully observable world can never select object
  permanence; there is nothing to model.
- S ~ 10,000,000 needs **invariant structure worth extracting + costly/irreversible action**,
  so that an organism that simulates before acting out-survives one that learns by trial.

"Enrich the world" therefore has a concrete gradient: add partial observability, then
invariants, then costly action.

**The design law (the single most important commitment):**
> Survival is the pressure. Sagacity is the measurement. They are never the same signal.

Selecting *for* S directly is teaching to the test -- the Goodhart failure that ended the
program's previous attempt (S5). Instead the engine selects for *survival in worlds that are
only survivable via sagacity*, and reads S off **independently, offline, after the fact**. The
art of the program is designing worlds where *survival implies sagacity* -- which is why the
object engineered is the world, not the organism.

**We measure only the floor.** Measuring S at the high end would be Nobel-grade; the project
explicitly does not attempt it. The floor is also the only scientifically valid place to
start, because *calibration requires known positives, and known positives exist only at the
bottom*: one can hand-write an organism that definitely uses retained information and one that
definitely does not, and check the instrument against them. There is no S=10^7 organism to
calibrate against.

## 4. Requirements

Functional (R) and non-functional (N). "MUST" items are load-bearing for scientific validity.

R1. The system MUST represent an organism as a deterministic program over a fixed primitive
    palette, optionally including evolvable integer/quantized neural modules (R7), such that an
    organism is hashable, replayable and ablatable.
R2. The system MUST host organisms in worlds that are pure, deterministic functions of
    (world-grammar, seed, mutation-history), producing a byte-identical trace on any host (N1).
R3. Worlds MUST support, as first-class affordances, partial observability and irreversible
    state, and MUST be enrichable by a seeded mutation grammar (so a world can gain complexity
    across generations).
R4. Selection MUST act on survival-in-world only. No sagacity term, novelty bonus, or
    experimenter-chosen target may enter the fitness signal (design law, S3).
R5. Sagacity MUST be scored by a separate, offline consumer that reads only emitted logs and
    never runs inside the selection loop.
R6. The sagacity score MUST be computed from (a) a reactive-null baseline (performance of the
    best memoryless policy) and (b) an ablation twin (a byte-identical run with the
    candidate's retained information destroyed); "signal" = survival above the null AND a
    survival drop under ablation.
R7. Organisms MAY incorporate neural primitives, which MUST be integer/quantized and
    bit-reproducible (S7.3), evolved by seeded mutation (no gradient training), so they obey
    R1-R2.
R8. Every experiment MUST be preregistered (arms, gates, effect-size margins, seed counts,
    kill criteria, reachability criteria) before data is collected, committed with a manifest.
R9. Every run MUST emit a complete, structured, replayable log sufficient for R6 to be
    computed from logs alone (nothing the scorer needs may be absent from the log).
R10. A local null result MUST be classified as KILL only with a reachability certificate
    (S11.x); otherwise UNDERPOWERED. Three outcomes, never two.
R11. The measuring instrument (the ruler) MUST be calibrated against disguised known controls
    (planted positives and negatives, dead-world control) before its verdicts are trusted.
R12. Diversity/health MUST be judged by mechanism, not by structure or archive coverage
    (coverage is gameable; a dead world can post high coverage).
R13. A candidate MUST pass local gates + a reachability certificate before promotion to paid
    compute (GPU, then cloud).

N1. Determinism: identical (code-sha, seed, spec) MUST reproduce byte-identical traces across
    heterogeneous hosts (integer-only compute, named RNG streams, no wall-clock, no float
    reductions, lookup-table nonlinearities).
N2. Cheap-wide: a stage-1 world+population shard MUST run as a lightweight process (<~1 GB RAM)
    so thousands run across commodity e-waste CPU nodes.
N3. No single point of failure on the critical path: the wide search MUST run with no live
    dependency on the shared database host (M1); shared stores are best-effort indices only.
N4. Fault tolerance: a node that sleeps or dies mid-task MUST NOT corrupt state; the task
    requeues (stateless pull).
N5. Independent lifecycles: logs are durable and the scorer is versioned, so an improved
    scorer can re-score the historical corpus without re-running experiments.
N6. Cost control: no paid compute without a passed local gate; cloud spend bounded by a
    hard guardrail and a preregistered estimate.
N7. Portability: a new commodity node MUST be able to join and run work with only Python, git,
    and a push credential -- no GPU, no database.

## 5. What killed the previous attempt, and what this design changes

The program previously ran a closed loop (Hephaestus generating primitives, Apollo evolving
compositions). It was declared a failure after roughly a dozen revival attempts. The forensic
finding (project memory) is precise and it is the spine of this design:

**Root cause: the ruler was co-adapted with the thing it scored.** Every apparent gain was a
capability a human had just inserted, scored on a metric the same seat authored. The instant
an independent instrument was applied, the signal vanished -- a headline 0.833 fell to 0.067
under a blind held-out battery (40/42 tasks abstained); transfer "enrichment" fell to the
floor under a from-random null; a generator's claimed gains were ungradeable off its own
ruler. No revival fixed it because none of them changed *who holds the ruler*. Secondary and
compounding: the substrate hosted almost nothing above noise (its entire reachable-solve set
was {identity, x+1}), diversity was measured by gameable archive coverage (a *dead* world
posted 19% coverage), and throughput was starved (multi-day runs).

Each Moonshot commitment maps to one of those failures:
- co-adapted ruler -> R5/R11: an **independent, offline, calibrated** ruler, air-gapped from
  selection and validated against disguised knowns.
- dead substrate -> R13 + reachability certificates: a **substrate-viability gate** before any
  scored compute; nothing is searched until something is reachable.
- gameable coverage -> R12: **mechanism, not coverage**, with dead-world and random-population
  controls first-class.
- throughput starvation -> the whole cheap-wide architecture (S6-S7) and N2/N7.

This is the difference between a hobbyist's evolutionary toy and an instrument: the toy
reports the number its own author chose; this design is built so that the author cannot.

## 6. Architecture

The unit that makes the architecture cohere is the **shard**. A shard is simultaneously three
things: a bag-of-tasks work unit, a shared co-evolving world with a resident population, and a
deterministic replayable log. One object, three roles -- which is the sign the design holds
together rather than fighting itself.

**6.1 Organisms and the primitive palette.** An organism is a deterministic program over a
fixed palette. The palette MAY include integer neural modules (S7.3). Mutation and selection
live in the population driver, not in the world. Crucially, we do not wire a reasoning
mechanism; we make one *survival-relevant* and let selection decide which primitives become
load-bearing (R4).

**6.2 Worlds.** A world is a pure function of (grammar, seed, mutation-history). It renders
only partial observations to the organism, can make actions irreversible, and can be enriched
across generations by a seeded mutation grammar (R3). Worlds are deterministic by construction
(integer state, named RNG streams, no floats) so every run has a stable trace hash (N1).

**6.3 Co-evolution (the self-enriching world).** Many organisms inhabit one shard and
co-evolve; survivors migrate between shards between generations (island model). Other evolving
agents are the one environment that stays more complex than the organism without the
experimenter hand-enriching it -- the Red Queen is the open-endedness engine. This is MMORPG
*dynamics* (sharded realms, island migration) delivered by a *deterministic tick simulation*,
not by a real-time server (S7.5 rejects real-time/UDP and game engines).

**6.4 The offline S-meter.** A separate consumer reads a shard's emitted log (and its ablation
twin's log and the reactive-null baseline) and computes S (R5-R6). It has no authority to
change what it scored; it only reads bytes and derives a verdict -- the same producer/consumer
shape as the RSO (S9). Because it is offline, it is also versioned and replayable: a better
S-meter re-scores the entire corpus for free (N5), which is literally how the system "gets
better at parsing signal from noise."

**6.5 The funnel.** Substrate-viability gate -> independent calibrated ruler -> CPU sieve
(wide) -> GPU confirm (local) -> cloud burst. The first two gates sit upstream of any paid
compute. The promotion rule is preregistered (R8, R13).

## 7. Scaling

**7.1 Workload shape.** Stage 1 is bag-of-tasks: millions of independent, pure-CPU,
deterministic shard runs with zero inter-shard coupling. Promotion is a rare, hierarchical
reduce. These are two different coupling regimes, and the architecture matches a transport to
each -- the central design principle is *match the plane to the coupling*.

**7.2 Three planes.**
- **Work plane (tier 1): pull/listener nodes over a durable, DB-free queue.** This is the
  existing `workgraph` git compare-and-swap mechanism -- a worker claims a task by a
  fast-forward push; the push *is* the claim. Stateless, fault-tolerant (N4), self-balancing,
  and with no live M1 dependency (N3). Proven on the Linux nodes (campaign C-005). The one
  scaling fix needed: shard the claim namespace so many workers do not contend on one branch
  (S7.4).
- **Promote/confirm plane (tier 2): A2A over the `fabric` Postgres queue**, capability-routed
  (`required_caps`) for the CPU->GPU->cloud handoff. Rare and low-volume, so routing it
  through M1 is acceptable; if M1 is down, tier 1 keeps sieving and survivors queue.
- **Nervous system: publish/subscribe** for liveness, auto-join announcements and "promotion
  happened" wakeups only -- never for work (pushing a task to a slept laptop loses it). Adopt a
  lightweight broker (NATS-class) only if polling the census files becomes a cost.

**7.3 Hardware split by primitive cost, at shard granularity.** The whole shard runs on one
node -- world and organisms together, never split across the network per tick. Shards whose
organisms use only cheap symbolic primitives run on e-waste CPU nodes; shards whose palette
includes GPU neural primitives run on the two GPU boxes (M1/M2). Integer neural inference is
bit-exact on GPU (the repo's CuPy and torch-integer kernels already demonstrate this against a
CPU oracle), so determinism (N1) survives the GPU tier.

**7.4 The two genuinely new builds.**
- **Ruler-calibration harness:** the component that certifies a ruler's false-positive rate
  against disguised-known controls (R11). Nothing in the repo packages this; it is the direct
  fix for "who holds the ruler." It generalizes the RSO producer-receipt template.
- **Node auto-join:** so a plugged-in e-waste box drains work without hand-provisioning (N7).
  Today every node is hand-built; for a *growing* cluster this is the main missing wiring. The
  sharded claim namespace (S7.2) rides along here.

**7.5 What the architecture deliberately refuses, and why.** Three times in design the
appealing move was a big, general-purpose, real-time tool; each fails the filter
*deterministic + cheap-headless + no-human-world-priors*:
- a real-time UDP mesh / MMORPG server -- breaks determinism (no replay, no ablation twin) and
  reintroduces the M1 SPOF; the science needs turn-order, not wall-clock latency.
- a graphics game engine for "world dimensionality" -- non-deterministic float physics, heavy
  per-shard RAM (kills the e-waste economics), and it smuggles in human-world 3-D priors the
  premise exists to escape. The dimensionality that drives sagacity is *causal/epistemic*
  (hidden state, delayed consequence), not spatial. Borrow at the RL-environment level
  (deterministic, headless, tiny), which the repo's integer-world engines already are.

## 8. What it leverages from existing engines (reuse, not rebuild)

| Component | Source (repo path) | Role in Moonshot |
|---|---|---|
| Executor contract + bit-deterministic kernels (+ reproducibility enum) | SerendipityFoundry/.../sfe/executors.py | The clean, headless, in-process world/organism execution contract -- lifts verbatim |
| Hash-chain ledger *format* + verifier | sfe/events.py, sfe/ids.py | The per-shard replayable log format |
| wforge: genome->expand->Encounter, named-RNG floatless trace-hash replay, world-mutation grammar, partial-observability mutator, probe battery | SerendipityFoundry/worldfoundry/wforge | The deterministic self-enriching world runtime -- the model to promote; satisfies R2/R3/N1 |
| mhc admission-rights alpha-ledger (Ville's inequality) | worldfoundry/mhc/ledger.py | Bounded false-admission statistical gate |
| Proteus organism VM (content-addressed programs) | proteus/ | Candidate organism substrate (wforge was built to host it) |
| BEE / Z80 worlds (demonstrated above-floor phenomena) | prometheus/toolbox, prometheus/z80atlas | Alternative substrate (demonstrated, not purpose-built) |
| Falsification battery (14 tests, no LLM) | cartography/shared/scripts/falsification_battery.py | The cheap deterministic kill tier |
| Null library (5 spec-pinned nulls) | harmonia/nulls/ | Matched-null machinery (R6) |
| Mutation operators | apollo/src/mutation.py | Symbolic variation operators |
| Denotational dedup / anti-unification | roles/Aphrodite/engine/{semantics,organ_extract}.py | Behavioral-equivalence dedup |
| Producer/consumer receipt template | rso/slice001/adapter.py | The shape of the S-meter's output; the RSO seam |
| Distribution (git CAS pull-queue) | workgraph/, roles/base-role/DISTRIBUTED_WORK.md | Tier-1 work plane (proven, C-005) |
| Cloud burst (launch/fanout/billing) | Aether/runpod/prometheus_gpu | Tier-3 RunPod burst (budget cap must be raised) |

The honest summary: the world layer, the execution contract, the null/battery/dedup
machinery, and the distribution layer already exist. Moonshot is substantially *integration +
launch + two new builds*, not invention. The substrate decision (wforge+Proteus, purpose-built
but dormant, vs BEE, demonstrated but not purpose-built) is an open operator decision.

## 9. Overlap with Phase 3 (the RSO)

Phase 3's Recursive Sagacity Observatory is the judge and the destination; prong 3 supplies
parts the RSO design already calls for but has not built.
- **The S-meter should be RSO consumer machinery, not a parallel scorer.** The RSO consumer
  already reads only producer bytes and recomputes outcomes from raw traces, and its producer
  has no authority over its own verdict -- exactly R5-R6. The floor-S predicates (reactive
  null, ablation twin) should be proposed as new RSO predicates/gates via its versioned
  amendment process. Prong 3 is a producer; the RSO is the consumer.
- **The ladders meet at the bottom rung.** The RSO's sagacity sequence is retention ->
  transfer -> combination -> reuse -> developmental improvement; its slice-001 predicates
  (RETENTION/ERASE/PRESERVE/CHANNEL/RESTART) test whether information survived a reset -- the
  same rung as floor-S. The RSO has no candidate connected yet (one fixture world), so the
  Moonshot launchpad is a natural first real candidate for its retention instruments.
- **The RSO design already specifies our parts.** Its architecture calls for "a world forge
  that certifies cognitive depth" (a POMDP family grammar -- i.e. partial observability) and
  "rulers qualified on planted organisms." wforge and the planted memory-user/reflex are those
  components in prototype. (Risk: the RSO cell may already own the world-forge work; coordinate
  before building -- an open item.)
- **The RSO verdict is the promotion gate.** The epic's policy -- internal fleet first, rented
  capacity only after gates pass -- is the same rule as Moonshot's "nothing reaches cloud
  without beating its null."
- **The first contract friction (the "adapting the RSO may be necessary" the operator
  predicted):** the RSO slice-001 contract is deterministic-finite-only, rationals not floats.
  Integer neural primitives are fine; any genuinely float GPU inference would need a
  contract amendment admitting a SEMANTIC/PARTIAL reproducibility level (the SFE enum already
  has one). Flag early as a planned amendment, not a surprise.

Independence is preserved: Moonshot is its own epic/lane, not a sub-task of Phase 2-B or Phase
3. It borrows from and overlaps with both but is owned by Themis end to end.

## 10. Prior art and related research

Honest framing up front: **Moonshot reuses wholesale from open-ended evolution (OEE),
quality-diversity (QD), neuroevolution and artificial life (ALife).** Almost every *component*
is well-trodden; the candidate novelty is narrow and lives in the *measurement + plumbing*
combination, not in the evolutionary engine or the scientific premise. (Citations below carry
authors/years; items flagged "verify" were not re-pulled from a live source for this draft.)

**10.1 What Moonshot borrows (cite, do not claim as new):**
- **Co-evolving worlds + organisms:** POET (Wang, Lehman, Clune, Stanley 2019) and Enhanced
  POET (Wang et al. 2020). Moonshot's island/world co-evolution is the same idea.
- **Survival-only / minimal-criterion selection:** Minimal Criterion Coevolution (Brant &
  Stanley 2017) is the closest engine analogue -- two populations survive by meeting a binary
  criterion, no fitness gradient. Roots in Novelty Search (Lehman & Stanley 2011).
- **AI-generating algorithms:** Clune (2019, arXiv:1905.10985). Moonshot is a deliberately
  austere instance of Clune's Pillar 3 (generate environments), not a new paradigm.
- **No-backprop neuroevolution on cheap parallel hardware:** NEAT (Stanley & Miikkulainen
  2002), Deep Neuroevolution (Such et al., Uber 2017), OpenAI ES (Salimans et al. 2017),
  Weight-Agnostic Nets (Gaier & Ha 2019). Moonshot's no-gradient stance is standard.
- **Digital organisms in a sim:** Tierra (Ray 1991), Avida (Ofria/Adami; Lenski, Ofria,
  Pennock, Adami, *Nature* 2003), Polyworld (Yaeger 1994, verify), Lenia (Chan 2019/2020).
  **The premise "evolution made one architecture; grow others" is essentially the Avida/ALife
  research program restated -- do not sell it as new.**
- **Competition/arms-race as curriculum:** Sims (1994), Hide-and-Seek (Baker et al., OpenAI
  2019), AlphaStar (Vinyals et al. 2019). The Red Queen bet is established OEE mechanism.
- **Distributed EC on commodity/volunteer clusters, island model:** BOINC (Anderson 2004),
  parallel-GA taxonomy (Cantu-Paz 1998, verify). The git-queue broker is an engineering choice,
  not research novelty.
- **Memory/object-permanence/delayed-match-to-sample as a first cognitive probe:** standard
  POMDP memory-RL paradigm. Moonshot uses the probe, it did not invent it.
- **Ablation/knockout to prove information use:** the oldest causal-attribution tool, formalized
  recently as causal scrubbing (Redwood 2022), activation patching, amnesic probing (Elazar et
  al. 2021), and RSA (Kriegeskorte 2008, verify). "Destroy the information, measure the drop" is
  amnesic probing imported from interpretability.
- **Preregistration / gated promotion:** standard open-science method, not an AI contribution.

**10.2 The contrast class Moonshot deliberately did NOT take** (cite to show the choice is
deliberate): active inference / free energy (Friston), and intrinsic motivation / curiosity
(Schmidhuber; ICM, Pathak et al. 2017; RND, Burda et al. 2018). These *replace* external reward
with an internal drive; Moonshot takes the more radical route of *no reward at all, only
survival*, and makes its competence signal an *external offline measurement*, not a drive.

**10.3 Metrics Moonshot must position "sagacity" against** (adjacent, not identical): empowerment
(Klyubin, Polani, Nehaniv 2005 -- action->sensor channel capacity); evolutionary-activity stats
(Bedau & Packard 1992) and the MODES toolbox (Dolson, Vostinar, Wiser, Ofria 2019 -- adopt rather
than reinvent); world models (Ha & Schmidhuber 2018 -- same vocabulary, but they *learn* the
model by gradient and *measure* it by task reward, where Moonshot *evolves* the organism and
*measures* world-model depth by offline ablation). Causal-RL framing: Scholkopf et al. 2021
(verify), Bengio et al. 2019-2020.

**10.4 On LLM-as-mutator** (relevant to the fusion-mode decision): ELM (Lehman et al., OpenAI
2022), FunSearch (Romera-Paredes et al., DeepMind, *Nature* 2024, verify year), Eureka (Ma et
al. 2023, verify). Published findings on whether LLM mutation beats deterministic mutation are
**mixed and task-dependent -- no clean consensus**; the evaluator/selection loop usually matters
more than the mutation operator. This corroborates the program's own Apollo result ("800 gens
matched deterministic exactly") and justifies treating LLM mutation as an **optional, unproven
accelerator kept off the selection path**, never a pillar.

**10.5 The candidate novel combination (state as a combination claim, cautiously -- "to our
knowledge not previously combined," never "first ever"):**
> An **offline, selection-air-gapped sagacity estimator** -- a reactive-null baseline plus an
> **ablation twin** that destroys the information an organism supposedly used and measures the
> survival drop -- applied over **deterministic, replayable, sharded co-evolved worlds**, where
> selection is **survival-only** (never the sagacity score), organisms may carry **evolvable
> integer/quantized neural modules admitted by selection**, run **wide-and-cheap on commodity/
> e-waste CPUs** under **preregistered gates + a reachability certificate**.

What is genuinely uncommon, assessed honestly: (1) **air-gapping the competence measurement
entirely from selection** -- nearly all prior systems either *optimize* the competence signal (QD
novelty, empowerment-as-reward, curiosity) or measure a task reward that *is* the selection
signal; measuring world-model depth by ablation purely as an observer, with zero feedback into
selection, is the part with no direct precedent found; (2) **determinism as a first-class
requirement specifically to make the counterfactual ablation replay exact**. Everything else is
borrowed, and the doc says so.

**10.6 Core citation list** (verify venue/year where flagged before any external use): Clune
2019 (AI-GAs); Wang et al. 2019/2020 (POET/Enhanced POET); Brant & Stanley 2017 (MCC); Lehman &
Stanley 2011 (Novelty Search); Mouret & Clune 2015 (MAP-Elites); Such et al. 2017 (Deep
Neuroevolution) + Salimans et al. 2017 (ES); Lenski et al. 2003 (Avida) + Ray 1991 (Tierra);
Baker et al. 2019 (Emergent Tool Use); Ha & Schmidhuber 2018 (World Models); Klyubin et al. 2005
(Empowerment); Dolson et al. 2019 (MODES) + Bedau & Packard 1992; Romera-Paredes et al. 2024
(FunSearch) + Lehman et al. 2022 (ELM); plus a causal-ablation reference (Vig et al. 2020 /
causal scrubbing 2022) to ground the ablation twin.

## 11. Boundaries, scaling challenges, and cost

**11.1 Local (e-waste cluster).** Strengths: effectively free wall-clock on otherwise-idle
hardware, no SPOF on the wide tier, linear scaling by adding nodes. Boundaries: heterogeneous
and flaky nodes (laptops sleep, Wi-Fi power-saves), small RAM, no GPU; the git-CAS claim
contends on one branch as node count grows (fixed by the sharded namespace); provisioning is
currently manual (fixed by auto-join). "Local" is not "small" -- an idle cluster can run for
weeks, so *scale time locally before renting width*.

**11.2 On-prem GPU (M1/M2).** Two RTX 5060 Ti (16 GB) boxes. Role: the confirm tier between
the CPU sieve and the cloud. Integer inference is bit-exact here. Boundary: only two cards and
M1 also hosts the shared Postgres, so GPU-tier work must not starve the database.

**11.3 RunPod.** The existing burst target. Role: extended runs and the reachability *scout*
(testing a preregistered scaling prediction, not merely confirming). Boundary: the module's
budget cap is currently ~$19.93 and must be raised deliberately; short jobs waste provision
overhead (batch them); community vs secure pricing differs.

**11.4 Hyperscalers (AWS/GCP/Azure).** Relevant only for a large, sustained, "run entirely in
the cloud" campaign. Trade-offs vs RunPod: higher raw GPU prices offset by mature spot/
preemptible markets and huge cheap CPU spot capacity (the wide tier is CPU-bound, which these
do well); the traps are egress fees, on-demand-vs-spot discipline, storage, and per-job
overhead on short tasks. Determinism is an asset here: preemptible/spot interruptions are
survivable because any shard can be replayed exactly.

**11.5 Cost model (as of 2026-10-05; hyperscaler figures are mid-2026 third-party tracker
snapshots and spot prices are live-market -- re-verify at launch).** Two facts shape the
economics: RunPod/neocloud GPU is ~3-5x cheaper than hyperscaler on-demand and bills
per-second with **$0 egress**; and because the wide tier is CPU-bound, **CPU spot is where the
real leverage is** (~$0.005/vCPU-hr spot vs ~$0.034 on-demand).

*Indicative $/GPU-hour, cheapest-first (RunPod = first-party; hyperscaler = tracker snapshots):*

| GPU | RunPod community | Hyperscaler spot | Hyperscaler on-demand |
|---|---|---|---|
| L4 (24GB) | $0.44 | ~$0.44 (AWS g6) | $0.71-0.80 |
| RTX 4090 (24GB) | $0.34 | n/a (not offered) | n/a |
| A40 (48GB) | $0.35 | n/a | n/a |
| A100 80GB | $1.19 | ~$0.82-2.5 (volatile) | $3.4-4.4 |
| H100 80GB | $1.99 | ~$2.1-3.8 | $6.9-12.3 |

*Three extended-campaign scenarios (storage/egress folded in; spot carries interruption risk):*
- **Scout (~100 GPU-h, L4/A40):** ~$35-85; RunPod community ~$36-44. Cheap enough that provider
  choice barely matters -- pick for convenience.
- **Campaign (~2,000 GPU-h, A100-class = ~1 month x 1 GPU or ~1 week x 12):** RunPod on-demand
  **~$2,400-3,200 all-in, no interruptions**. Hyperscaler on-demand $6,800-8,800; hyperscaler
  spot $1,600-6,200 but near-certain interruptions over weeks.
- **Large "run entirely in the cloud" (20k-50k GPU-h):** RunPod/neocloud A100 **~$16k-60k**;
  RunPod H100 ~$40k-100k; hyperscaler on-demand $170k-205k at the top (a 3-5x SLA markup an
  evolutionary search does not need).
- **CPU-fleet alternative (the wide tier):** 1,000 vCPUs for a month on spot ~= **$3.6k-8.8k**
  for ~730,000 vCPU-hours. Since stage-1 episodes are sub-second integer work, this buys far
  more useful search per dollar than GPU -- budget the bulk of the search on CPU spot and
  reserve GPU for the confirmation tier.

*Cost traps to design against:* (1) **per-job overhead dominates the wide tier** -- batch
thousands of episodes per long-lived worker, never one VM per episode (the single biggest
hidden cost); (2) **egress** (GCP $0.12/GB worst, AWS/Azure ~$0.09, RunPod $0) -- keep results
in-cloud, export only summaries; (3) **spot interruptions** over multi-week A100/H100 runs are
near-certain -- but Moonshot's byte-identical replay turns an interruption into a cheap resume,
so spot becomes usable *because* of the determinism requirement, not despite it; (4) idle
on-demand and standing storage accrue silently.

The framing these numbers serve: Apollo failed *dramatically* on extended runs partly because
it spent days of compute on a dead substrate with a co-adapted ruler -- it paid for search that
could not have found anything and could not have recognized it if it had. Moonshot's cost
discipline is **structural, not budgetary**: paid compute is gated behind a passed local gate
and a reachability certificate (R13, N6), spend is bounded by a hard guardrail plus a
preregistered estimate, and determinism makes spot capacity usable without a checkpointing tax.
The cost question is never "can we afford to keep searching" but "has this candidate earned the
next tier" -- a gate, not a budget line. And the reassurance for a cloud-only extended search:
even the *large* 20k-50k GPU-hour range on RunPod ($16k-60k) is bounded and gated, while the
dominant, cheapest work -- the CPU wide tier at single-digit-$k/month -- is exactly the part that
runs first and decides whether the expensive part is ever authorized.

## 12. The first build (launchpad) and milestones

**Launchpad = the smallest honest slice of the whole design.**
- World: a delayed-cue partial-observability micro-world (show a cue; it vanishes; later,
  acting on the vanished cue determines survival -- the delayed-match-to-sample paradigm, the
  dirt-simple cousin of object permanence).
- Two arms, identical but for the palette: SYM (symbolic only) vs HYB (symbolic + a tiny
  integer neural module), matched by evaluation budget, hundreds of seeds, CPU only.
- Scoring: the offline floor-S detector (reactive null + ablation twin).
- Gates (preregistered): G0 the detector classifies a planted memory-user and a planted reflex
  correctly; a dead-world control never fires; promote only if HYB beats SYM by a preset
  margin with a CI excluding zero, holding on a second world variant; kill if HYB <= SYM or the
  effect vanishes on the second world or the dead world fires; a null without a reachability
  certificate is UNDERPOWERED, not KILL.
- Question: does an integer neural primitive raise the rate/speed of crossing the floor versus
  a matched symbolic null, at equal budget? (A fair, adequately-powered re-test of the
  intuition Apollo left underpowered.)

Milestones (from the backlog): prereg committed (THEMIS-01) -> world spec + deterministic
reference run (THEMIS-04) -> offline detector + planted-organism calibration (THEMIS-05/06) ->
reachability suite + dead-world control (THEMIS-07/08) -> local runner lifting SFE+wforge
(THEMIS-09) -> workgraph packet (THEMIS-10) -> many-seed run + verdict (THEMIS-14) ->
multi-scale reachability curves (THEMIS-15) -> scout/scale per the curve (THEMIS-18/19).

## 13. Why this is a strong approach, not a hobbyist toy

A hobbyist evolutionary simulation and a research instrument can look identical in a
screenshot. They differ in exactly one place: whether the system can fool its author. This
design is built so it cannot.
- **Preregistration (R8):** arms, gates, margins and kill criteria are fixed and committed
  before data exists, so results cannot be chosen after the fact.
- **Independent, calibrated ruler (R5, R11):** the scorer is offline, air-gapped from
  selection, and is itself validated against disguised known controls before its negatives are
  believed. This is the specific thing the previous attempt never had, and the specific thing
  that killed it.
- **Matched nulls and ablation (R6):** every claim is stated against a null and confirmed by a
  causal intervention (destroy the information, watch survival fall), not by an absolute score.
- **Falsification-first, three-verdict logic (R10):** the product is the kill. A null counts
  as a kill only with a reachability certificate; otherwise it is honestly marked
  underpowered, so the system neither over-claims positives nor manufactures false negatives.
- **Determinism and replay (N1, N5):** every run is byte-reproducible, so results are
  independently checkable and a better instrument re-scores the whole history -- the opposite
  of an un-auditable toy.
- **Mechanism over coverage (R12):** diversity is judged by mechanism with dead-world and
  random controls, closing the Goodhart gap where a dead world posts high coverage.
- **Gated economics (R13, N6):** compute escalates only on earned evidence, which is why an
  extended cloud search here is a sequence of passed gates rather than a hopeful burn.

The ambition is a moonshot; the method is conservative on purpose. The project will mostly
produce nulls, and it is designed to produce *honest* nulls cheaply and to recognize the rare
real signal when the instrument -- proven against ground truth at the floor -- says so.

## 14. Open operator decisions

1. Substrate for the first build: wforge+Proteus (purpose-built, dormant) vs BEE (demonstrated,
   not purpose-built).
2. Strategic fork: instrument-first (this design) vs re-premise to a pure measurement/assay
   lane.
3. Fusion mode: neural-as-primitive (organism calls it) vs neural-as-substrate (weights are
   the genome) vs neural-as-mutator (re-tested at power).
4. RunPod/cloud budget authorization and cap.
5. Coordination posture with the RSO cell (Palamedes) and Daedalus (SFE/wforge) before
   building on their components.

## 15. Risks and failure modes

- **Needle-in-haystack worlds:** if a world's solution has no fitter intermediate neighbors,
  no compute reaches it -- caught by the needle-vs-slope reachability check, answered by world
  shaping, not scale.
- **The neural half stays inert:** the honest base rate (Apollo) is that it may; the design is
  built to detect that cheaply and move the neural component to a different role rather than
  keep spending.
- **Determinism leaks:** any accidental float reduction or wall-clock dependency breaks replay
  and the ablation twin; guarded by N1 and a parity test in the integer-primitive build.
- **Instrument self-deception:** guarded by calibration against disguised knowns (R11); if the
  ruler cannot recover a disguised known signal, its "no signal" means nothing.
- **Coordination collision:** building a world-forge the RSO cell already owns -- mitigated by
  the coordination item before any forge work.

---
*End v0.1 draft. Complete and ready for operator markup. Not yet committed -- awaiting your
review; I will commit the reviewed version under roles/Themis/design/ with a manifest.*
