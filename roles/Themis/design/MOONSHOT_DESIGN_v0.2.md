# Project Moonshot -- Requirements & Design (v0.2)

Seat: Themis (owner). Epic: EP-MOONSHOT. Charter: roles/Themis/prompts/2026-10-05_charter/
(verbatim; governs where this doc differs). Operator review & Epic approval (authority for v0.2):
roles/Themis/prompts/2026-10-05_epic_approval_and_review/ (verbatim). Running synthesis:
operator auto-memory project_moonshot_rso_lane. Date: 2026-10-05. Supersedes v0.1 (in
superseded/). Status: committed design of record; experiments still gated as below.

> **Survival is the pressure. Sagacity is the measurement.**
> **Reachability is the prerequisite. The ruler is the adversary.**

## 0. What changed from v0.1 (operator review, all accepted)

The operator reviewed v0.1 and approved Moonshot as a new Epic with revisions. Themis held the
final word and accepts all of them; several fix real errors in v0.1, not preferences:
1. **Two independent hypotheses (H1/H2)** now front the design (S2). Moonshot is an *adversarial
   customer for Phase 3*, not merely a user of it.
2. **Launchpad is a fixed-world assay, not co-evolutionary** (S6.1): SYM and HYB see one
   identical preregistered world distribution. World mutation / islands / Red Queen move to a
   later thread (M5), after the launchpad.
3. **Reachability becomes three certified levels RC0/RC1/RC2** (S5, R-RC); a null is KILL only
   when the level relevant to the claim is certified, else UNDERPOWERED.
4. **Ablation made physically correct** (R6): not a "byte-identical run with information
   destroyed" (impossible -- the intervention changes downstream bytes), but identical initial
   state/RNG/organism/event-schedule differing only in a preregistered information-channel
   intervention, with two modes (channel-cut and state-scramble) to avoid manufacturing a drop.
5. **Reactive-null becomes a family** (R6): constant/reflex, optimal observation-only policy
   (exact oracle bound where tractable), and an evolved memory-disabled population at equal
   budget; agreement across the family makes the ruler hard to fool.
6. **Shard -> shard epoch** (S6.0, R-EP): the durable unit is `immutable checkpoint + epoch
   spec -> trace + next checkpoint`, atomically published. This resolves the "stateless pull vs
   resident population" tension and gives fault tolerance (N4) teeth.
7. **N1 relaxed from byte-identity to canonical semantic identity** (N1): one canonical trace
   serialization + a reference semantic oracle; GPU/accelerated implementations must demonstrate
   equality to the oracle *before admission*; host/perf metadata lives in a separate receipt.
8. **"No reward" rewritten** (R4): survival/reproduction *is* the fitness criterion and the
   experimenter designs the ecology; the exact, stronger claim is *no competence/sagacity
   measurement enters reproductive fitness*.
9. **Anti-degeneracy ecology** (R-AD): viability = reproductive continuation / lineage
   persistence under resource turnover, not merely remaining alive (evolution will otherwise
   discover stay-still / hide / minimize-metabolism / timeout-exploit).
10. **Ruler blindness made operational, not organizational** (R11): opaque IDs for calibration
    artifacts, independently generated positive/negative assignment, labels revealed only after
    scoring, sealed manifest retained as a receipt.
11. **Workgraph-on-seven-nodes is an experiment, not a solved problem** (M4, S7.2): instrument
    claim latency, push contention, abandoned tasks, ref growth, useful-CPU/coordination-CPU
    ratio, with a preregistered threshold at which the transport must be reconsidered.
12. **Prior art:** PAIRED / Unsupervised Environment Design added beside POET (S10); XLand added
    as the expensive task/reward-oriented opposite pole.
13. **Economics (old 11.5) demoted to a versioned appendix** (S11-APX), not part of the
    scientific contract -- spot prices decay faster than the design.

Operator rulings on the five open decisions, recorded: substrate = **wforge+Proteus for
Launchpad, BEE later as a substrate-transplant test**; fork = **instrument-first**; fusion =
**neural-as-primitive first**, neural-as-substrate later, neural-as-mutator an auxiliary arm
outside selection authority; cloud = **no extended campaign authorized; the scout *mechanism*
is authorized once RC2 + the local gate exist, dollar cap fixed at launch with fresh prices**;
coordination = the constitutional ownership boundary (S15).

## 1. Executive summary

Project Moonshot is the third prong of the program: the hybrid neuro-symbolic engine that
fuses deterministic AI with neural/GPU/tensor tooling across an e-waste CPU cluster, two GPU
boxes, and the cloud. It does two things at once, and they are **independent**: it is an
**adversarial external customer for Phase 3** (does the RSO correctly judge a producer it did
not build?), and it is a **commodity-scale evolutionary search** for the first rung of
sagacity (can survival-only evolution in deterministic worlds produce mechanisms that depend
on retained hidden information, provably?). Either can succeed while the other fails -- which is
exactly why they are stated as two hypotheses (S2).

The method is a signal-detection funnel -- generate cheap and wide on e-waste CPUs, sift with
deterministic falsification, promote to GPU then cloud only after preregistered gates **and** a
reachability certificate -- organized around four commitments: survival is the only selection
pressure; sagacity is scored offline and air-gapped from selection; reachability must be
certified before a null counts as a kill; and the ruler is treated as an adversary to be
attacked, not a dashboard to be trusted. Most machinery already exists and is reused (S8); the
new builds are small and specific (S7.4). It gives the program something it has never had: a
way to make **Phase 3 itself falsifiable**, while turning a pile of old Linux machines into
coherent science.

## 2. The two hypotheses

**H1 -- Observatory hypothesis.** Phase 3 (the RSO) can correctly judge an unfamiliar external
producer -- recognizing its positives, negatives, underpowered results, and contract
violations -- *without adapting the ruler to make the producer look good*. Moonshot tests H1 by
being a hostile integration: it feeds the RSO honest producers AND deliberately **planted
bad ones** (contract violations, internally-consistent fabrications, underpowered results) and
checks that the RSO accepts the good and rejects the bad on its own authority. H1 can be
confirmed even if every Moonshot organism dies stupid.

**H2 -- Scientific hypothesis.** Survival-only evolution in progressively richer deterministic
worlds can produce mechanisms whose dependence on retained hidden information *survives
matched-null and causal-ablation tests*. H2 is the open-ended-evolution bet.

**Why the separation is load-bearing:** evolving something interesting does NOT validate Phase
3 if the RSO cannot independently recognize it; and Phase 3 judging correctly does NOT require
that evolution produce anything. Conflating them is how a program convinces itself it found a
mind when it found a measurement artifact -- the Apollo failure (S5). Keeping them apart is what
lets a month of the cluster "merely" proving the ruler rejects garbage count as a real result.

## 3. Scientific premise

Evolution produced one cognitive architecture; the bet is that it is one point in a space, not
the only one. Isolate primitives and build worlds where sagacity is the only way to survive,
and a different architecture could crystallize. LLMs cannot *discover* such an architecture --
they are pulled toward the human corpus -- so you grow one, you do not retrieve it. (Honest
note, S10: this premise is essentially the Avida/ALife research program plus Clune's AI-GA
thesis restated; it is not claimed as new.)

## 4. The sagacity scale and the four-concept spine

S grades the depth of the world-model an organism must have internalized. Reference points
(log-scaled by counterfactual reach): S~10 a bare survival mechanism; S~1,000 toddler object
permanence; S~10,000,000 a scientist's thought experiment. The scale is also a world-design
spec: a rung is only selectable if the world makes it survival-relevant (S~10 differential
survival; S~1,000 partial observability; S~10^7 invariants + irreversible action). Moonshot
measures only the floor, because calibration needs known positives and those exist only at the
bottom.

The spine, in four concepts:
- **Pressure = survival** (R4): the only thing acting on reproduction.
- **Measurement = sagacity** (R5-R6): scored offline, never fed back into pressure.
- **Reachability = prerequisite** (R-RC): a null is informative only once the relevant
  reachability level is certified.
- **Ruler = adversary** (R11, H1): the instrument is attacked and must survive; it is never
  assumed correct because it is "ours."

## 5. Requirements

Functional (R), non-functional (N). MUST = load-bearing for validity.

R1. An organism MUST be a deterministic program over a fixed primitive palette (optionally
    including evolvable integer neural modules, R7), hashable, replayable and intervenable.
R2. A world MUST be a pure deterministic function of (grammar, seed, mutation-history) producing
    a trace that reproduces to **canonical semantic identity** (N1) on any host.
R3. Worlds MUST support partial observability and irreversible state as first-class
    affordances, and MUST be enrichable by a seeded mutation grammar (deferred to M5; the
    Launchpad world is fixed, S6.1).
R4. Selection MUST act on survival/reproduction only. **No competence or sagacity measurement
    may enter reproductive fitness.** The experimenter designs the ecology that determines
    survival; the measurement is a separate, downstream observer (R5).
R-AD. (Anti-degeneracy) Viability MUST be defined as reproductive continuation / lineage
    persistence under resource turnover, not merely "remaining alive," so that stay-still,
    hide, minimize-metabolism and timeout-exploit are not viable survival strategies.
R5. Sagacity MUST be scored by a separate offline consumer that reads only emitted logs and
    never runs inside the selection loop.
R6. The sagacity verdict MUST combine (a) a **preregistered reactive-null family** -- at minimum
    constant/reflex, an optimal observation-only policy (exact oracle bound where tractable),
    and an evolved memory-disabled population at equal compute budget -- and (b) a **causal
    ablation**: a counterfactual run with identical initial state, RNG streams, organism and
    event schedule, differing only in a preregistered information-channel intervention. At least
    two ablation modes MUST be available (channel-cut and state-scramble/resample) because
    zeroing recurrent state can manufacture a spurious survival drop. Signal = survival above
    the whole null family AND a survival drop under ablation that is not reproduced by the
    scramble control.
R7. Neural primitives MAY be included; they MUST be integer/quantized and reproduce to the
    canonical semantic oracle (N1), evolved by seeded mutation (no gradient training), obeying
    R1-R2. Initial fusion mode = **neural-as-primitive** (the organism calls it); neural-as-
    substrate (weights as genome) is later; neural-as-mutator is an auxiliary arm **outside
    selection authority**.
R8. Every experiment MUST be preregistered (arms, gates, effect-size margins, seed counts, kill
    criteria, reachability level required) with a manifest, before data.
R-RC. (Reachability) A claim MUST name the reachability level it needs, certified before a null
    becomes KILL:
    - **RC0 expressible:** a hand-written organism in the palette exhibits the mechanism (the
      substrate *can* express it).
    - **RC1 locally traversable:** fitness-improving / mortality-reducing intermediary mutations
      exist between randomized starts and the mechanism (the landscape is not a needle).
    - **RC2 search-reachable:** a preregistered search procedure crosses the floor at a known
      rate from appropriately randomized starts (evolution *can discover* it at budget).
    A null without the relevant RC level certified is UNDERPOWERED, never KILL (R10).
R9. Every run MUST emit a complete structured log sufficient to compute R6 from logs alone.
R10. Local outcomes are three, never two: PASS / KILL (null + required RC level) / UNDERPOWERED.
R11. (Operational ruler blindness) The ruler MUST be calibrated against disguised known controls
     whose identities it cannot see: opaque artifact IDs, independently generated positive/
     negative assignment, labels revealed only after scoring, sealed manifest kept as a receipt.
     R11 tests whether the instrument can *discriminate*, not whether anyone remembers the
     controls.
R12. Diversity/health MUST be judged by mechanism, with dead-world and random-population
     controls first-class (coverage is gameable; a dead world posts high coverage).
R13. A candidate MUST pass local gates + the required RC level before promotion to paid compute.
R-EP. (Shard epoch) The durable work unit MUST be `immutable checkpoint + epoch spec -> trace +
     next checkpoint`, with the output checkpoint and trace **atomically published**; a worker
     dying mid-epoch MUST have no semantic effect (the epoch simply re-runs from its input
     checkpoint).

N1. Determinism = **canonical semantic identity**: one defined canonical trace serialization and
    a reference semantic oracle. CPU integer implementations reproduce it directly; any
    accelerated (GPU/library) implementation MUST demonstrate equality to the oracle before
    admission, re-demonstrated per stack version -- "matched a CPU oracle once" is not a blanket
    certification. Host/performance metadata lives in a separate receipt, never in the trace.
N2. Cheap-wide: a Launchpad epoch MUST run as a lightweight process (<~1 GB RAM).
N3. No SPOF on the wide critical path: the wide search MUST run with no live dependency on the
    shared DB host; shared stores are best-effort indices.
N4. Fault tolerance via R-EP: node death requeues an epoch from its input checkpoint, no
    corruption, no partial-claim semantics.
N5. Independent lifecycles: logs are durable, the scorer is versioned; a better scorer
    re-scores the historical corpus without re-running experiments.
N6. Cost control: no paid compute without a passed local gate + required RC; cloud spend bounded
    by a hard guardrail + a preregistered estimate (S11, S16).
N7. Portability: a new commodity node joins with only Python, git and a push credential.

## 6. Architecture

**6.0 The shard epoch (the durable unit).** `immutable checkpoint + epoch spec -> trace + next
checkpoint`, atomically published (R-EP). A shard is a world instance with a resident
population; an *epoch* advances that shard a bounded number of ticks from a frozen input
checkpoint and publishes (trace, next checkpoint) as one atomic claim. This is both a
bag-of-tasks unit (stateless at the epoch boundary -- a dead laptop just loses an unpublished
epoch) and the carrier of a resident, evolving population across epochs. One object, three
roles: work unit, evolving world, replayable log.

**6.1 The Launchpad is a fixed-world assay.** For the first experiment, SYM and HYB arms see an
*identical preregistered world distribution* -- no world mutation, no migration, no co-evolution.
Otherwise HYB could change its own ecology and the arm comparison would be uninterpretable.
Open-ended world mutation / islands / Red Queen are M5, and begin only after the Launchpad
assay and its reachability science (M3) are in hand.

**6.2 Organisms and palette.** Deterministic programs over a fixed palette; the palette may
include an integer neural primitive (R7). Mutation/selection live in the population driver, not
the world. We never wire a reasoning mechanism; we make one survival-relevant and let selection
decide (R4).

**6.3 The offline S-meter** reads an epoch's logs (plus the ablation counterfactual's logs and
the reactive-null family) and emits an RSO-shaped producer receipt with no authority to change
what it scored (R5-R6). Offline + versioned => it re-scores the whole corpus when improved (N5).

**6.4 The funnel.** RC0/expressibility + substrate-viability -> operational-blind calibrated
ruler -> CPU sieve -> GPU confirm -> cloud scout. The first gates sit upstream of any paid
compute (R13, N6).

## 7. Scaling

**7.1 Workload = bag-of-tasks (epochs) + a rare hierarchical reduce (promotion).** Match the
plane to the coupling.

**7.2 Three planes.** Work plane = the `workgraph` git compare-and-swap pull-queue (DB-free,
no-GPU, fault-tolerant via R-EP, no live M1 dependency), **treated as an experiment not a solved
problem** (M4): Moonshot instruments claim latency, push/ref contention, abandoned-epoch rate,
repo/ref growth, and the useful-CPU/coordination-CPU ratio, and preregisters a threshold at
which the transport must be reconsidered (GitHub push rate-limits are a specific watch item
before raw branch contention). Seven e-waste boxes are an ideal stress rig to find that
threshold before anyone contemplates 100-1,000 workers. Promote/confirm plane = A2A over
`fabric` (capability-routed, low volume, M1 acceptable). Nervous system = pub/sub for liveness/
auto-join/wakeups only (NATS-class if polling costs; never for work).

**7.3 Hardware split by primitive cost, at epoch granularity.** The whole epoch runs on one
node. Symbolic-only epochs -> e-waste CPU; neural-primitive epochs -> the two GPU boxes, which
must first demonstrate oracle-equality (N1). Never split world-from-organism across the network
per tick.

**7.4 The two genuinely new builds:** the ruler-calibration harness (R11, operational blindness)
and node auto-join (N7); the sharded claim namespace rides with M4 if the threshold is hit.

**7.5 Deliberately refused** (fails the filter *deterministic + cheap-headless +
no-human-world-priors*): real-time UDP/MMORPG servers (break determinism + replay + reintroduce
SPOF), and graphics game engines (non-deterministic float physics, heavy per-epoch RAM, smuggle
in 3-D human-world priors). The dimensionality that drives sagacity is causal/epistemic, not
spatial; borrow at the RL-environment level, which the repo's integer-world engines already are.

## 8. Leverage from existing engines

Primary substrate = **wforge + Proteus** (wforge: deterministic floatless replay, world-mutation
grammar, partial-observability mutator, probe battery; Proteus: content-addressed organism VM
wforge was built to host). **Named risk:** wforge is a dormant, unlaunched prototype, so the
Launchpad's first real cost is *completing and wiring wforge*, not science (tracked in M2/M4).
**BEE = the later substrate-transplant test** (M5/M6): demonstrated above-floor phenomena on a
*different* substrate; if the same RSO floor-ruler finds the same phenomenon on BEE, that is far
stronger evidence than starting there. Also reused: SFE executor contract + ledger format;
mhc admission-rights alpha-ledger; cartography falsification battery; harmonia nulls; apollo
mutation operators; Aphrodite denotational dedup; rso/slice001 adapter (receipt template);
workgraph (distribution); Aether RunPod module (burst). Moonshot is substantially integration +
launch + two new builds, not invention.

## 9. Phase 3 overlap and hostile integration (H1)

The S-meter is RSO *consumer* machinery (same producer/consumer seam; producer has no authority
over its verdict). The two sagacity ladders meet at the retention rung, so the Launchpad is a
natural first real candidate for the RSO's retention instruments. The RSO design already calls
for a world forge (a POMDP-family grammar) and planted-organism rulers -- wforge and the planted
memory-user are those in prototype (coordinate with the cell before building; S15). The RSO
verdict is the promotion gate.

**Hostile integration (M1) is the H1 test with teeth:** Moonshot deliberately submits planted
contract violations, internally-consistent fabrications, and underpowered results, and H1 is
confirmed only if the RSO rejects them *on its own authority, without the ruler being relaxed to
flatter the producer*. The first contract friction is already known: the RSO slice-001 contract
is deterministic-finite-only; integer neural primitives fit, but any genuinely float GPU path
would need a SEMANTIC/PARTIAL-reproducibility amendment -- proposed through the cell's versioned
process, never slid in silently (S15).

## 10. Prior art and related research

Honest framing: **Moonshot reuses OEE/QD/neuroevolution/ALife wholesale.** The candidate novelty
is a narrow *combination*, in measurement + plumbing, not in the engine or the premise.
- Co-evolving worlds+agents: **POET / Enhanced POET** (Wang, Lehman, Clune, Stanley 2019/2020).
  **PAIRED / Unsupervised Environment Design** (Dennis et al. 2020) belongs beside POET: it
  directly attacks *automatically generating valid, solvable environments and escalating
  difficulty* -- adjacent to Moonshot's reachability/world-shaping (RC1/RC2, M3/M5).
- Survival/minimal-criterion selection: **Minimal Criterion Coevolution** (Brant & Stanley
  2017) -- the closest engine analogue to R4; roots in Novelty Search (Lehman & Stanley 2011).
- AI-generating algorithms: **Clune 2019** -- Moonshot is an austere Pillar-3 instance.
- No-backprop neuroevolution on cheap parallel HW: Deep Neuroevolution (Such et al. 2017),
  OpenAI ES (Salimans et al. 2017), NEAT/HyperNEAT, WANN (Gaier & Ha 2019).
- Digital organisms: Tierra (Ray 1991), Avida (Lenski, Ofria, Pennock, Adami, *Nature* 2003),
  Polyworld (Yaeger 1994, verify), Lenia (Chan 2019/2020).
- Competition-as-curriculum: Hide-and-Seek (Baker et al. 2019), AlphaStar (2019), Sims (1994).
  **XLand** (DeepMind 2021/2023, verify) = the expensive opposite pole: enormous procedurally
  generated task spaces + automatic curricula produce broad capability, but with heavy machinery
  and an explicitly task/reward-oriented learner -- which sharpens Moonshot's contrast
  (deterministic, headless, measurement-air-gapped, survival-only).
- World models & causal/memory: Ha & Schmidhuber 2018 (distinct: they learn by gradient and
  measure by task reward); causal RL (Scholkopf et al. 2021, verify); POMDP memory / DMTS.
- Contrast class NOT taken: active inference (Friston), intrinsic motivation/curiosity
  (Schmidhuber; ICM Pathak 2017; RND 2018) -- Moonshot takes the more radical survival-only route
  and makes competence an external offline measurement, not a drive.
- Metrics to position against (not reinvent): empowerment (Klyubin, Polani, Nehaniv 2005);
  evolutionary-activity stats (Bedau & Packard 1992); MODES (Dolson et al. 2019).
- LLM-as-mutator: ELM (Lehman et al. 2022), FunSearch (Romera-Paredes et al. 2024, verify),
  Eureka (2023, verify) -- findings on LLM-vs-deterministic mutation are mixed, no consensus;
  corroborates keeping neural-as-mutator auxiliary and off the selection path.
- Ablation/knockout to prove information use: causal scrubbing (Redwood 2022), amnesic probing
  (Elazar et al. 2021), causal mediation (Vig et al. 2020, verify), RSA (Kriegeskorte 2008,
  verify) -- the technique is standard; Moonshot's twist is applying it offline to an evolved
  organism's world-inputs and keeping the score out of selection.

**Candidate novelty (combination claim, "to our knowledge not previously combined"):** an
offline, selection-air-gapped sagacity estimator (reactive-null family + causal ablation twin)
over deterministic replayable co-evolved worlds, with selection-admitted integer neural
primitives, on commodity hardware, under preregistration + RC0/1/2. The air-gap of the
competence measurement from selection is the strongest single novelty candidate; everything
else is borrowed, and the doc says so. ("Sagacity" must be positioned against empowerment/
MODES/amnesic-probing, not asserted sui generis.)

## 11. Boundaries and scaling challenges

Local e-waste cluster: free idle wall-clock, no wide-tier SPOF, linear scaling; boundaries are
flaky/heterogeneous nodes (handled by R-EP), small RAM, no GPU, git-CAS contention at scale
(the M4 experiment). "Local" is not "small" -- scale *time* locally before renting *width*.
On-prem GPU (two RTX 5060 Ti): the confirm tier; must demonstrate oracle-equality (N1) and not
starve M1's DB. RunPod: burst + reachability scout. Hyperscalers: only for a large sustained
campaign; determinism makes spot/preemptible usable because any epoch replays from its
checkpoint. Concrete pricing, scenarios and traps live in the **versioned economics appendix
(S11-APX)**, deliberately kept out of the scientific contract because prices decay fast.

## 12. Epic structure (EP-MOONSHOT)

| Thread | Name | Purpose | H |
|---|---|---|---|
| M1 | RSO Hostile Integration | Prove Phase 3 judges a genuinely independent producer; submit honest AND planted-bad producers | H1 |
| M2 | Floor Sagacity Science | Delayed information -> survival -> reactive-null family + causal ablation (fixed-world assay) | H2 |
| M3 | Reachability Science | RC0/RC1/RC2 and the UNDERPOWERED/KILL semantics | both |
| M4 | Commodity Fabric | Seven-node fleet, auto-join, epoch replay, CAS-scaling threshold experiment | H1-infra |
| M5 | Open-ended Ecology | World mutation, islands, migration, Red Queen; begins only after the Launchpad | H2 |
| M6 | Scale Escalation | local CPU -> local GPU -> paid scout -> extended campaign (BEE transplant test here) | both |

M1-M4 can each produce valuable negative results even if M5 never earns permission to start.
This is what keeps Moonshot from collapsing into one monolithic "build an artificial-life
universe" effort.

## 13. First build (Launchpad, fixed-world)

World: a delayed-cue partial-observability micro-world (cue shown, cue vanishes, acting on the
vanished cue later determines survival -- delayed-match-to-sample). Arms: SYM vs HYB, identical
preregistered world distribution, matched by evaluation budget, hundreds of seeds, CPU only.
Scoring: offline S-meter (reactive-null family + two-mode causal ablation). Gates
(preregistered): operational-blind detector classifies planted memory-user vs planted reflex;
dead-world control never fires; promote only if HYB beats SYM by a preset margin, CI excluding
zero, holding on a second world variant; KILL only with the required RC level certified; else
UNDERPOWERED. Question: does an integer neural primitive raise the rate/speed of crossing the
floor vs a matched symbolic null at equal budget -- the adequately-powered re-test Apollo never
ran. Milestones map to M2 (assay), M3 (RC0->RC1->RC2), M4 (fabric), M1 (feed the result, honest
and planted-bad, to the RSO).

## 14. Why this is rigorous, not a hobbyist toy

The one thing that separates an instrument from a toy is whether the system can fool its author;
this is built so it cannot. Preregistration (R8); an independent, offline, operationally-blind,
calibrated ruler (R5/R11) that is *attacked* as an adversary (H1); a reactive-null family plus
causal ablation (R6); three-verdict logic with reachability-gated kills (R10/R-RC); canonical
semantic determinism and replay (N1/N5); mechanism over coverage (R12); anti-degeneracy ecology
(R-AD); gated economics (R13/N6). Each closes a specific Apollo failure (S5). The ambition is a
moonshot; the method is conservative on purpose, and designed to produce *honest* nulls cheaply.

## 15. Ownership and the constitutional boundary

Themis owns the Epic, the integration, the producer, and the experiments. **Palamedes / the RSO
cell owns whether the evidence satisfies RSO contracts and predicates.** Themis may *propose*
amendments but MUST NOT be able to silently relax the ruler -- amendments go through the cell's
versioned process. Archaeon's and Daedalus's components (SFE/wforge/BEE/nulls) are reusable
substrate dependencies, **not transferred scientific authority**. This turns the coordination
concern into an intentional independence mechanism: it is *because* Themis cannot move the ruler
that an H1 pass means something.

## 16. What is authorized now

Instrument-first, Launchpad on wforge+Proteus, neural-as-primitive. The **scout mechanism** (the
RunPod path) is authorized to be *built* but fires only once RC2 and the local gate exist, with
the dollar cap fixed at launch from fresh prices. **No extended cloud campaign is authorized.**
Coordinate with the RSO cell (M1) and Daedalus (wforge) before building on their components.

## 17. Risks

Needle worlds (caught by RC1); the neural half stays inert (the honest Apollo base rate -- detect
cheaply, move the component); determinism leaks (guarded by N1 + a parity test); wforge
completion cost (named, M2/M4); instrument self-deception (guarded by operational R11 + the H1
attack); coordination collision with the RSO cell (mitigated by S15 before any forge work);
ecology degeneracy (guarded by R-AD).

---
*v0.2 design of record. Economics appendix (S11-APX) maintained separately and versioned.*
