# ATLAS_EXPERIMENT_TODO -- the durable experiment queue

Currency: 2026-09-21. Source of truth: EXPERIMENTS.jsonl beside this file (one record
per experiment, every field of the operator's record format). This file is GENERATED
from it -- edit the JSONL, then regenerate. Records are indexed into atlas.experiment
as kind=proposal (campaign atlas.proposal/2026-09-21_prior_art_raid).

Operator directive (verbatim + MANIFEST): roles/Atlas/prompts/2026-09-21_prior_art_raid/.
Techne's donor raid (what code actually exists) is cited per record:
roles/Techne/prompts/2026-09-21_prior_art_raid/FIRST_RETURN_2026-09-21.md.

STATUS vocabulary: IDEA | NEEDS_DONOR | READY_FOR_DESIGN | PREREG | READY | RUNNING |
ADJUDICATION | CLOSED | PARKED. Nothing here is READY: nothing has been designed with
its owning seat, and Atlas does not run experiments.

## Totals

    experiments            34
    by status              IDEA 15, NEEDS_DONOR 4, READY_FOR_DESIGN 15
    by compute class       L 2, M 11, S 16, XS 5
    prereg required        30

## NOMINATIONS (recommended for design attention, not prejudged)

Nominate means: give it design attention next. It does not predict the outcome.

### Five XS/S experiments worth preparing immediately

  RA-3 REANALYSIS: evaluator-exploitation census across campaigns [XS compute / XS eng]
      why now: MEDIUM-HIGH -- cheap, and it directly sizes EV-8.
      Techne donor needed: None needed

  RA-1 REANALYSIS: did frontier queue pools act as a curriculum? [XS compute / XS eng]
      why now: MEDIUM -- likely underpowered, but it costs almost nothing and sizes the real experiment.
      Techne donor needed: None needed

  UED-4 Environment transfer vs environment mutation [S compute / S eng]
      why now: HIGH -- cheap factorial that decides what to import.
      Techne donor needed: uber-research/poet (verified, last push 2022)

  UED-2 Do learnability estimators create invisible selection bias? [S compute / S eng]
      why now: HIGH -- XS-to-S cost, and it can falsify an assumption we are about to import.
      Techne donor needed: OMNI-EPIC, dcd (verified)

  GEA-4 Raw fossils vs extracted organs [S compute / S eng]
      why now: HIGH -- cheap, internal, and it tests a core architectural bet.
      Techne donor needed: Internal: techne/fossils (121 fossils, 105 runnable), nyx/atlas organs

### Five medium-term experiments

  F5-0 Persistence is actually useful [S / M]
      HIGH -- a negative result kills the fifth engine cheaply and redirects the Voyager machinery to a memory feature inside an existing engine.

  F5-1 Skill composition opens new reachable space [S / M]
      HIGH -- distinguishes 'memory' from 'substrate'.

  F5-4 Closed competence loop: is later progress causally dependent on earlier structure? [M / M]
      HIGH -- the single most discriminating test in the ladder.

  QD-1 Does MAP-Elites preserve stepping stones our selection loses? [M / S]
      HIGH -- tests a mechanism we already pay for.

  EV-1 Evolving executable machinery vs parameter-only adaptation [M / M]
      HIGH -- decides whether our next engines evolve programs or parameters, and it is the prerequisite measurement for EV-8's exploitation tax; both answers change what QA an engine needs.

### Three dangerous / high-value experiments needing new infrastructure

  F5-3 Generated world curriculum vs its controls [L / L]
      infrastructure: All open substitutes are video-first world models; adapting one to a measurable task world is the real work, and may be cheaper to replace with a parametric gen
      risk: generator collapses onto learner weaknesses (see G-9)

  AL-1 Fixed vs mutable interpreter [M / M]
      infrastructure: Mutable-interpreter substrate; Nestor's current campaign may already build the endogenous half.
      risk: mutable interpreter mostly lethal, so the arm is compute-starved

  TI-1 When does a collective become the unit of selection? [L / L]
      infrastructure: Statistic + validation harness; DISHTINY itself may be runnable as the substrate.
      risk: statistic too weak

## QUEUE

### A. ENGINE FIVE / VOYAGER x SIMA x GENERATED WORLDS

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    F5-0     READY_FOR_DESIGN   S/M      Engine-Five-candidate (h  Persistence is actually useful
    F5-1     READY_FOR_DESIGN   S/M      Engine-Five-candidate     Skill composition opens new reachable space
    F5-2     NEEDS_DONOR        M/L      Engine-Five-candidate     Cross-world transfer of acquired structure
    F5-3     NEEDS_DONOR        L/L      Engine-Five-candidate     Generated world curriculum vs its controls
    F5-4     READY_FOR_DESIGN   M/M      Engine-Five-candidate     Closed competence loop: is later progress causally dependent
    F5-5     READY_FOR_DESIGN   S/M      Engine-Five-candidate or  Self-generated tasks and rewards without evaluator collusion
    F5-6     IDEA               S/M      Engine-Five-candidate +   Open-ended reachability: new kinds, not just better scores

  F5-0 -- Persistence is actually useful
    QUESTION:   Does persistent acquired competence improve future performance beyond giving an agent the same information as history/context?
    CLAIM:      An executable, retrievable skill library produces cumulative capability that equal-information context memory does not.
    MATTERS:    Engine Five's whole premise. If false, the Voyager mechanism is a context-management trick and needs no engine.
    DONOR:      Voyager SkillManager (name + NL description + executable payload + embedding key; retrieval_top_k=5); Techne source autopsy 2026-09-21
    ENGINE:     Engine-Five-candidate (host: SFE or Bellerophon harness)
    WORLD:      A tiny gridworld/toolchain world with recurring structural regularities (shared sub-procedures) but no repeated task instances; deterministic, seedable, no LLM required for the base controller.
    TREATMENTS: A no memory; B episodic textual memory; C retrieved demonstrations; D persistent executable skill library; E library + composition
    CONTROLS:   equal-token/equal-byte information budget across B-E; equal compute (wall and steps); shuffled-library control (same size, wrong content); frozen-controller control (no learning at all)
    PRIMARY:    tasks solved per unit compute on held-out tasks after a context reset
    FALSIFIER:  With information and compute matched, D/E show no advantage over B/C on held-out post-reset competence.
    CAUSAL:     late-run library swap: empty / shuffled / equal-size irrelevant / foreign-lineage library; measure competence collapse
    ANTICHEAT:  held-out tasks never appear in any prompt or library entry; library contents hashed and diffed against task specs; detect verbatim answer storage (skill payload that encodes the solution rather than a procedure)
    ASSUMPTION COST: Skill libraries privilege discrete, nameable, reusable procedures; continuous or diffuse competence cannot enter the library and will look like 'no benefit'. Counter-arm: a non-discrete memory (parameter delta) treatment.
    DONOR CODE: MineDojo/Voyager MIT, pinned + fossilized (techne/fossils/specimens/voyager-minedojo-2023); SOURCE_ONLY (needs Minecraft client + paid API, not exercised)
    GAP:        Voyager's payload is JS-in-Minecraft; needs the schema re-hosted on a Prometheus substrate with our own executor. Techne organ 1 (SkillManager schema + versioning + vector retrieval, ~130 lines) is the extraction target.
    GATE:       D or E beats B/C on the primary endpoint at matched information and compute, in >= 2 world families, with the swap test showing collapse.
    STOPPING:   Stop at the preregistered episode budget or when the information-matching control fails audit.
    DEPENDS:    none

  F5-1 -- Skill composition opens new reachable space
    QUESTION:   Can independently acquired skills compose into competence that was never directly trained?
    CLAIM:      Composition of stored skills reaches goals that neither skill nor the base controller reaches alone.
    MATTERS:    Composition, not storage, is what would make a library a substrate for further search (see EV-10).
    DONOR:      Voyager .programs concatenation (stored skills + fixed primitives form the callable language)
    ENGINE:     Engine-Five-candidate
    WORLD:      Tasks requiring A+B where training exposes A and B separately and the composite never appears.
    TREATMENTS: monolithic policy; demonstrations; retrieved raw episodes; non-composable library (opaque payloads); composable library; hand-authored macro (ceiling)
    CONTROLS:   hand-authored macro as the performance ceiling; composite task withheld from every prompt, library and curriculum
    PRIMARY:    zero-shot success on withheld composite tasks
    FALSIFIER:  Composable and non-composable libraries perform identically on withheld composites.
    CAUSAL:     ablate one constituent skill and confirm the composite fails; restore and confirm recovery
    ANTICHEAT:  composite tasks generated after training and hashed; check retrieval logs for composite leakage; reject runs where a skill's description names the composite
    ASSUMPTION COST: Assumes competence decomposes into callable units; mechanisms that are irreducibly entangled are invisible to this design.
    DONOR CODE: Voyager (pinned)
    GAP:        Needs a composition-capable executor and a withheld-composite task generator.
    GATE:       Composable library beats all controls except the hand-authored ceiling on withheld composites.
    STOPPING:   Preregistered budget; stop early if leakage audit fails.
    DEPENDS:    F5-0

  F5-2 -- Cross-world transfer of acquired structure
    QUESTION:   Which acquired structures survive changes of appearance, geometry, dynamics, control mapping and embodiment?
    CLAIM:      A substrate-independent skill representation transfers where a world-specific script does not.
    MATTERS:    Separates generalized competence from world-specific scripts; the same question our transport experiments (SFE-03/SFE-07) asked in program space.
    DONOR:      SIMA's cross-world instructable agent; Voyager skill schema
    ENGINE:     Engine-Five-candidate
    WORLD:      One task family rendered in >= 4 variants: visuals, topology, control mapping, object identity, physics, action primitives, embodiment (one axis varied at a time).
    TREATMENTS: skill library transferred as-is; library re-indexed only; library retrained; no transfer (fresh)
    CONTROLS:   matched-compute fresh learner in the target variant; scrambled-mapping control (transfer with a deliberately wrong action mapping)
    PRIMARY:    competence in the varied world at fixed compute, transfer minus fresh
    FALSIFIER:  No axis shows transfer above the fresh baseline, or all axes transfer equally (then the variation is cosmetic).
    CAUSAL:     swap only the adapter layer and hold the library fixed; then the inverse
    ANTICHEAT:  verify the target variant is not solvable by the source policy by accident (run the frozen source policy first)
    ASSUMPTION COST: Assumes an adapter boundary exists at all; agents whose competence IS the interface cannot be tested this way.
    DONOR CODE: SIMA 2: NO_PUBLIC_SOURCE (Techne, verified by primary quote). kyegomez/SIMA graded TOY_CLONE. Only the Voyager half has donor code.
    GAP:        Prometheus must build its own multi-embodiment world variants; no donor supplies them.
    GATE:       Transfer beats fresh on >= 2 axes with the scrambled-mapping control at baseline.
    STOPPING:   Stop if the frozen source policy already solves the variants (design invalid).
    DEPENDS:    F5-0

  F5-3 -- Generated world curriculum vs its controls
    QUESTION:   Does adaptive world generation produce more cumulative capability than static, random-procedural, human, novelty-only or difficulty-only generation?
    CLAIM:      Adaptive generation expands the reachable competence frontier faster than any single-signal control.
    MATTERS:    Directly tests whether Engine Five needs a learned generator or whether our procedural worlds suffice.
    DONOR:      Genie-like learned interactive worlds; OMNI-EPIC learnability/interestingness; POET environment mutation
    ENGINE:     Engine-Five-candidate
    WORLD:      A parameterised world family where a generator can propose worlds and an oracle can measure reachability; photorealism explicitly out of scope.
    TREATMENTS: static; random procedural; human curriculum; novelty-only; difficulty-only; adaptive (learnability)
    CONTROLS:   held-out ground-truth worlds not produced by any generator; frozen-generator control
    PRIMARY:    expansion of the reachable competence frontier on held-out worlds
    FALSIFIER:  Adaptive generation matches random procedural on held-out worlds.
    CAUSAL:     swap the generator mid-run between arms and observe whether the frontier follows the generator or the learner
    ANTICHEAT:  held-out worlds generated by an independent process; detect generator-specific loopholes (agent success that collapses on held-out variants)
    ASSUMPTION COST: Learned world models inherit their training distribution; a generated curriculum can only pose what its prior can express. Counter-arm: procedural generator with an explicitly wider support.
    DONOR CODE: Genie 1/2/3: NO_PUBLIC_SOURCE (Techne). Open substitutes ranked by Techne: open-oasis, MineWorld, Matrix-Game. OMNI-EPIC and POET repos verified in the catalogue.
    GAP:        All open substitutes are video-first world models; adapting one to a measurable task world is the real work, and may be cheaper to replace with a parametric generator.
    GATE:       Adaptive beats every control on held-out frontier expansion at equal compute.
    STOPPING:   Stop if the generator cannot produce a held-out-valid world within the pilot budget.
    DEPENDS:    F5-0   CONFLICTS: UED-1 (overlapping question at lower cost)

  F5-4 -- Closed competence loop: is later progress causally dependent on earlier structure?
    QUESTION:   Does the generate-attempt-acquire-persist-harden loop produce progress that causally depends on retained structures?
    CLAIM:      Removing accumulated structure late in a run collapses competence; equal-size irrelevant structure does not restore it.
    MATTERS:    This is the operational definition of cumulative, as opposed to merely long.
    DONOR:      Voyager loop; OMNI-EPIC task selection
    ENGINE:     Engine-Five-candidate
    WORLD:      Same world as F5-0/F5-1 with a task ladder whose upper rungs are unreachable without lower-rung structure.
    TREATMENTS: full loop; loop without persistence; loop without generation; loop without composition
    CONTROLS:   empty library; shuffled library; equal-size irrelevant library; foreign-lineage library
    PRIMARY:    competence drop after late-run library replacement (per treatment)
    FALSIFIER:  Competence is unchanged by library replacement, i.e. progress was not cumulative.
    CAUSAL:     the ablation IS the causal test; add restoration to show reversibility
    ANTICHEAT:  verify the upper rungs are not solvable from scratch at the same compute (run a fresh learner at the ablation point)
    ASSUMPTION COST: Cumulativeness is defined via removable structures; competence that has diffused into weights is scored as non-cumulative.
    DONOR CODE: Voyager (pinned)
    GAP:        Needs library swap machinery and a fresh-learner comparator at the ablation point.
    GATE:       Collapse under empty/shuffled/irrelevant, recovery under restoration, no collapse under foreign-lineage only if skills are genuinely general.
    STOPPING:   Preregistered budget.
    DEPENDS:    F5-0, F5-1

  F5-5 -- Self-generated tasks and rewards without evaluator collusion
    QUESTION:   Can a system generate productive training objectives for itself without merely exploiting its own evaluator?
    CLAIM:      Generated task + generated reward yields competence that survives independent evaluation.
    MATTERS:    Our doctrine forbids an LLM adjudicating its own science; this measures the size of the effect that rule prevents.
    DONOR:      SIMA 2 self-generated objectives; OMNI-EPIC interestingness; AI Scientist self-evaluation
    ENGINE:     Engine-Five-candidate or Bellerophon
    WORLD:      Any world with an independent, frozen external scorer that the generator cannot read or modify.
    TREATMENTS: external task + external reward; generated task + external reward; generated task + generated reward; generated task + adversarial independent evaluator; generated task + delayed transfer evaluation
    CONTROLS:   frozen external scorer as ground truth for all arms; random-task control at matched count
    PRIMARY:    competence under the independent frozen scorer
    FALSIFIER:  Generated-reward arms match external-reward arms under independent evaluation (no collusion penalty, no benefit).
    CAUSAL:     swap the evaluator at the end and re-score all arms
    ANTICHEAT:  scorer state isolated from the generator; detect reward hacking by scoring frozen replays; log every evaluator read
    ASSUMPTION COST: Generated rewards privilege measurable objectives; unmeasurable competence is invisible and will be selected away.
    DONOR CODE: SIMA 2 no source; OMNI-EPIC verified repo; AI Scientist verified repo
    GAP:        Build the independent scorer harness; this is reusable instrumentation for AS-1/AS-2.
    GATE:       Self-generated arms retain >= external arms under the independent scorer.
    STOPPING:   Stop on detected scorer leakage; freeze the specimen first.
    DEPENDS:    none

  F5-6 -- Open-ended reachability: new kinds, not just better scores
    QUESTION:   Does the closed loop keep exposing new KINDS of reachable behaviour, or only improve within a fixed ontology?
    CLAIM:      Behaviour categories discovered post hoc keep appearing over run time rather than saturating.
    MATTERS:    Open-endedness claims need a measure that is not defined in advance by us.
    DONOR:      AURORA learned descriptors; ASAL foundation-model search; Atlas/Harmonia anomaly machinery
    ENGINE:     Engine-Five-candidate + Atlas analysis
    WORLD:      Any long F5-4 run with full behavioural telemetry.
    TREATMENTS: closed loop; loop without generation; static world
    CONTROLS:   shuffled-time control for the descriptor model; synthetic run with known category count (positive control for the discovery method)
    PRIMARY:    rate of new behaviour clusters per unit compute, discovered by descriptors fitted AFTER the run
    FALSIFIER:  New-cluster rate saturates in the closed loop as fast as in the static control.
    CAUSAL:     refit descriptors on shuffled time; clusters must disappear
    ANTICHEAT:  descriptors fitted without access to task labels; cluster count validated on the synthetic positive control
    ASSUMPTION COST: Learned descriptors impose their own geometry; alien behaviour that the embedding cannot separate is scored as 'no new kind'.
    DONOR CODE: QDax/pyribs verified; AURORA implementation to be confirmed by the catalogue top-up
    GAP:        Descriptor pipeline + cluster-stability test (shared with QD-3/QD-4 and RA-2).
    GATE:       New-cluster rate exceeds the static control with the positive control passing.
    STOPPING:   Stop if the synthetic positive control fails (method invalid).
    DEPENDS:    F5-4

### B. ENVIRONMENT GENERATION / UED

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    UED-1    READY_FOR_DESIGN   M/M      Nestor GraphWorld (same   Environment-selection law shoot-out on one organism populati
    UED-2    READY_FOR_DESIGN   S/S      Nestor GraphWorld or SFE  Do learnability estimators create invisible selection bias?
    UED-3    IDEA               S/S      Nestor GraphWorld         Generator-learner degenerate co-adaptation
    UED-4    IDEA               S/S      Nestor GraphWorld or SFE  Environment transfer vs environment mutation

  UED-1 -- Environment-selection law shoot-out on one organism population
    QUESTION:   Which environment-selection mechanism expands the reachable capability frontier fastest at equal compute?
    CLAIM:      Selection law, not environment mutation, drives frontier expansion.
    MATTERS:    All four Prometheus engines use fixed or procedural environments; this is the cheapest test of whether that is a limitation.
    DONOR:      POET, PLR, ACCEL, PAIRED, DRED, MCC, OMNI-EPIC learnability, plus Archaeon's own selector
    ENGINE:     Nestor GraphWorld (same population under different laws) or SFE
    WORLD:      An existing Nestor world family with a parametrised generator and a held-out set.
    TREATMENTS: random; novelty; minimal criterion; POET-style; PLR; ACCEL; PAIRED; DRED; learnability/interestingness; Archaeon native selector
    CONTROLS:   identical organism population and seeds across laws; equal environment steps; held-out worlds from an independent generator
    PRIMARY:    held-out solve rate at equal environment steps
    FALSIFIER:  All laws within seed variance on held-out frontier.
    CAUSAL:     replace the learner mid-run and measure which curricula still work (UED-5)
    ANTICHEAT:  held-out worlds never enter any curriculum; detect regret/learnability estimators reading held-out state
    ASSUMPTION COST: Learnability estimators select for what the current learner can almost do; alien-but-hard worlds are systematically suppressed (see UED-8).
    DONOR CODE: facebookresearch/dcd (PAIRED/PLR/ACCEL), dramacow/jaxued, uber-research/poet, OMNI-EPIC -- all VERIFIED in the catalogue
    GAP:        Port the selection laws onto one Prometheus population; the laws are small, the harness is the work.
    GATE:       A law beats random on held-out frontier in >= 2 world families.
    STOPPING:   Preregistered step budget.
    DEPENDS:    none   CONFLICTS: F5-3 (same question, higher cost)

  UED-2 -- Do learnability estimators create invisible selection bias?
    QUESTION:   Does an interestingness/learnability estimator suppress worlds whose value appears only later?
    CLAIM:      Estimator-driven selection discards worlds that would have become stepping stones.
    MATTERS:    This is the alienness risk in importing UED wholesale; it also bears on our own detector thresholds.
    DONOR:      OMNI-EPIC interestingness; PLR/ACCEL regret estimators
    ENGINE:     Nestor GraphWorld or SFE
    WORLD:      A world family containing planted late-value worlds (worthless now, valuable after a later capability).
    TREATMENTS: estimator-driven selection; random selection; estimator with a forced exploration floor
    CONTROLS:   planted late-value worlds with known payoff schedule; oracle selector that knows the schedule (ceiling)
    PRIMARY:    fraction of planted late-value worlds retained until their payoff epoch
    FALSIFIER:  Estimator retains late-value worlds as well as random selection does.
    CAUSAL:     re-run with the retained set forced to include the discarded worlds
    ANTICHEAT:  planted worlds indistinguishable by surface features (verify with a classifier probe)
    ASSUMPTION COST: The experiment defines value by a planted schedule, which is itself an ontology; genuinely alien late value is not represented.
    DONOR CODE: OMNI-EPIC, dcd (verified)
    GAP:        Planted-world generator with a hidden payoff schedule (reusable instrumentation).
    GATE:       Estimator retains significantly fewer late-value worlds than random, with the probe showing they were not surface-detectable.
    STOPPING:   Preregistered budget.
    DEPENDS:    UED-1

  UED-3 -- Generator-learner degenerate co-adaptation
    QUESTION:   Do generator and learner enter a degenerate loop where worlds collapse onto learner weaknesses?
    CLAIM:      Adaptive generation without a diversity floor converges to a narrow world distribution.
    MATTERS:    A failure mode Engine Five would inherit; also a risk for Archaeon's frontier scheduler.
    DONOR:      PAIRED minimax-regret dynamics; POET transfer/novelty guards
    ENGINE:     Nestor GraphWorld
    WORLD:      UED-1 harness with generator capacity high enough to overfit.
    TREATMENTS: adaptive generation; adaptive + novelty floor; adaptive + minimal criterion; random
    CONTROLS:   fixed-distribution control; learner replacement probe
    PRIMARY:    world-distribution entropy over time and held-out frontier
    FALSIFIER:  No entropy collapse even at high generator capacity.
    CAUSAL:     swap in a naive learner; a co-adapted generator should mis-serve it
    ANTICHEAT:  entropy computed on world parameters, not on generator internals
    ASSUMPTION COST: Entropy on chosen parameters is a proxy; collapse along unparametrised axes is invisible.
    DONOR CODE: dcd, poet (verified)
    GAP:        Entropy instrumentation only.
    GATE:       Entropy collapse reproduced and reversed by the diversity floor.
    STOPPING:   Fixed budget.
    DEPENDS:    UED-1

  UED-4 -- Environment transfer vs environment mutation
    QUESTION:   Does moving agents between environments matter more than mutating environments?
    CLAIM:      POET's transfer step, not its mutation step, carries most of the benefit.
    MATTERS:    Tells us which half of POET to import; transfer is far cheaper than a generator.
    DONOR:      POET (mutation + transfer), Enhanced POET, ATEP
    ENGINE:     Nestor GraphWorld or SFE
    WORLD:      A niche set with migration controls (our GraphWorld niches already support this).
    TREATMENTS: mutation only; transfer only; both; neither
    CONTROLS:   matched compute; matched number of environments
    PRIMARY:    held-out frontier at equal compute (2x2 factorial)
    FALSIFIER:  Only the interaction term matters, or neither factor does.
    CAUSAL:     disable transfer late and observe frontier stall
    ANTICHEAT:  transfer log audited for accidental copying of solutions
    ASSUMPTION COST: Assumes environments are separable into niches; continuous world spaces do not fit.
    DONOR CODE: uber-research/poet (verified, last push 2022)
    GAP:        Small: a 2x2 switch in the harness.
    GATE:       A main effect survives with matched compute.
    STOPPING:   Fixed budget.
    DEPENDS:    UED-1

### C. QUALITY DIVERSITY / STEPPING STONES

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    QD-1     READY_FOR_DESIGN   M/S      Nestor GraphWorld         Does MAP-Elites preserve stepping stones our selection loses
    QD-3     NEEDS_DONOR        S/M      Nestor GraphWorld + Atla  Learned vs human behaviour descriptors
    QD-8     IDEA               M/S      Nestor GraphWorld         Do archived weak lineages become critical after an environme
    QD-9     IDEA               S/S      Crius or Nestor GraphWor  Recombination across distant niches

  QD-1 -- Does MAP-Elites preserve stepping stones our selection loses?
    QUESTION:   Do archived low-fitness niches later become necessary ancestors of high-fitness solutions?
    CLAIM:      Quality-diversity archives retain lineages that our elite-selection loop discards, and those lineages matter later.
    MATTERS:    Our GraphWorld already keeps QD cells; this asks whether they pay off, using our own data plus a matched run.
    DONOR:      MAP-Elites, CMA-ME, QDax, pyribs
    ENGINE:     Nestor GraphWorld
    WORLD:      An existing GraphWorld family run twice: QD archive vs elite-only selection.
    TREATMENTS: QD archive; elite-only; QD with archive pruned each epoch
    CONTROLS:   matched evaluations; same seeds; random-archive control (keep random individuals at the same rate)
    PRIMARY:    fraction of final high-fitness solutions whose ancestry passes through a cell that elite-only would have discarded
    FALSIFIER:  High-fitness solutions rarely descend from discarded cells, or the random archive does as well.
    CAUSAL:     replay with the specific ancestor cells removed
    ANTICHEAT:  ancestry reconstructed from logged lineage, not inferred; random-archive control rules out 'any memory helps'
    ASSUMPTION COST: MAP-Elites needs a behavioural partition chosen in advance; stepping stones outside that partition are invisible (QD-3/QD-4 attack exactly this).
    DONOR CODE: QDax, pyribs (verified)
    GAP:        Ancestry reconstruction may need a telemetry addition; check RA-2 first -- old cells.jsonl may already suffice.
    GATE:       Archive-dependent ancestry exceeds the random-archive control.
    STOPPING:   Preregistered evaluation budget.
    DEPENDS:    none

  QD-3 -- Learned vs human behaviour descriptors
    QUESTION:   Do learned behaviour descriptors (AURORA-style) outperform our hand-chosen descriptors, and are they stable?
    CLAIM:      Unsupervised descriptors find axes our instrumentation missed without destroying historical comparability.
    MATTERS:    Our QD cells use human-chosen axes; if learned axes are better, every past archive is under-instrumented.
    DONOR:      AURORA unsupervised descriptors
    ENGINE:     Nestor GraphWorld + Atlas analysis
    WORLD:      One GraphWorld family with raw behaviour traces retained.
    TREATMENTS: human descriptors; learned descriptors (frozen after fit); learned descriptors refit each epoch
    CONTROLS:   random projection descriptors of the same dimension; synthetic data with known axes (positive control)
    PRIMARY:    coverage and peak fitness per evaluation under each descriptor set
    FALSIFIER:  Learned descriptors match random projections, or drift destroys comparability without any coverage gain.
    CAUSAL:     re-score an old archive under learned descriptors and check whether ranking changes materially
    ANTICHEAT:  descriptor fit must not see fitness; random-projection control rules out 'any embedding helps'
    ASSUMPTION COST: Learned descriptors inherit the trace representation; behaviour not expressed in the trace stays invisible.
    DONOR CODE: QDax verified; AURORA implementation availability pending the catalogue top-up
    GAP:        Descriptor pipeline shared with F5-6 and RA-2.
    GATE:       Learned descriptors beat human and random-projection on coverage at equal evaluations, with drift quantified.
    STOPPING:   Stop if the synthetic positive control fails.
    DEPENDS:    none

  QD-8 -- Do archived weak lineages become critical after an environment change?
    QUESTION:   After a world shift, do previously weak archived lineages become the source of the new best solutions?
    CLAIM:      Archives are insurance: their value appears only under nonstationarity.
    MATTERS:    Our worlds are mostly stationary; if archives only pay under change, our current measurements understate them.
    DONOR:      MAP-Elites archives; POET niche reuse; Flow-Lenia species turnover
    ENGINE:     Nestor GraphWorld
    WORLD:      A world family with a scheduled, preregistered shift at a fixed epoch.
    TREATMENTS: archive retained across the shift; archive cleared at the shift; archive replaced with random individuals
    CONTROLS:   no-shift control; shift announced vs unannounced (if the selector can see it)
    PRIMARY:    post-shift recovery time and peak, by archive policy
    FALSIFIER:  Recovery is identical with and without the archive.
    CAUSAL:     restore only the weak cells (not the elites) and measure recovery
    ANTICHEAT:  shift generated independently of the archive contents
    ASSUMPTION COST: Shifts are preregistered and parametric; real nonstationarity may not resemble them.
    DONOR CODE: QDax, pyribs (verified)
    GAP:        Scheduled-shift world wrapper (reusable).
    GATE:       Archive-retained arm recovers faster with ancestry traced to pre-shift weak cells.
    STOPPING:   Preregistered budget.
    DEPENDS:    QD-1

  QD-9 -- Recombination across distant niches
    QUESTION:   Does recombining individuals from distant archive cells produce useful novelty, or mostly inviable offspring?
    CLAIM:      Cross-niche recombination yields a higher rate of novel viable behaviour than within-niche variation at equal cost.
    MATTERS:    Crius already runs a recombination arm with PARTS donors; this generalises the question to archives.
    DONOR:      MAP-Elites variation operators; CycleQD; M2N2 merging
    ENGINE:     Crius or Nestor GraphWorld
    WORLD:      Any archive with a defined distance metric between cells.
    TREATMENTS: within-niche mutation; near-niche recombination; distant-niche recombination; random-pair recombination
    CONTROLS:   matched offspring count; viability-matched control (equal number of viable offspring)
    PRIMARY:    novel viable behaviours per unit compute
    FALSIFIER:  Distant recombination yields no more novelty per compute than within-niche mutation.
    CAUSAL:     ablate one parent's contribution (splice back) to attribute the novelty
    ANTICHEAT:  novelty measured against the archive as of the parent generation, not the final archive
    ASSUMPTION COST: Assumes a meaningful genotype crossover exists; representations without it are excluded.
    DONOR CODE: QDax, pyribs, CycleQD (verify), M2N2 (pending top-up)
    GAP:        Recombination operator per representation; Crius already has PARTS splicing.
    GATE:       Distant recombination beats within-niche on novel-viable-per-compute.
    STOPPING:   Fixed budget.
    DEPENDS:    none

### D. DIGITAL LIFE / ENDOGENOUS ORGANISMS

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    AL-1     READY_FOR_DESIGN   M/M      Nestor NPE                Fixed vs mutable interpreter
    AL-3     IDEA               M/L      Nestor NPE or a Lenia-cl  Evolvable organism boundary
    AL-5     IDEA               S/S      Nestor NPE                Explicit reproduction opcode vs reproduction from local inte
    TI-1     IDEA               L/L      Nestor NPE or DISHTINY-c  When does a collective become the unit of selection?

  AL-1 -- Fixed vs mutable interpreter
    QUESTION:   Does letting the copying/interpreting machinery itself mutate create qualitatively different evolutionary dynamics?
    CLAIM:      A mutable interpreter changes which computations are reachable, not merely how fast they are found.
    MATTERS:    Nestor, Bellerophon and Crius all assume a fixed interpreter; this is a foundational assumption test.
    DONOR:      Stringmol (program-program reactions), Tierra/Avida fixed CPUs, Aevol genome structure, BFF soups
    ENGINE:     Nestor NPE
    WORLD:      A small program soup where the copy operator is itself encoded in the genome and can be mutated.
    TREATMENTS: fixed interpreter + external copy; fixed interpreter + endogenous copy; mutable interpreter + endogenous copy
    CONTROLS:   matched mutation rate per site; matched compute; lethality-matched control (equalise the fraction of viable offspring)
    PRIMARY:    set of computations reached (reachability set), not time-to-solution
    FALSIFIER:  Reachability sets coincide once mutation rate and viability are matched.
    CAUSAL:     freeze the interpreter mid-run in the mutable arm and observe whether reachability stalls
    ANTICHEAT:  detect runner-provided reproduction; verify offspring arise from executed copies (event log)
    ASSUMPTION COST: Program soups privilege discrete symbolic heredity; continuous-substrate heredity (Lenia-like) is excluded and needs AL-3.
    DONOR CODE: stringmol, avida, aevol, cubff -- all verified repos in the catalogue
    GAP:        Mutable-interpreter substrate; Nestor's current campaign may already build the endogenous half.
    GATE:       Reachability differs with matched rates and viability.
    STOPPING:   Preregistered budget.
    DEPENDS:    none   CONFLICTS: Nestor's own Z80 campaign may overlap; coordinate before design

  AL-3 -- Evolvable organism boundary
    QUESTION:   What changes when the boundary of the organism is not fixed by the substrate?
    CLAIM:      An evolvable boundary permits phenomena (higher-level individuality, collective reproduction) that a fixed boundary forbids.
    MATTERS:    Our organisms have fixed boundaries by construction; this is a precondition for the individuality questions (TI-*).
    DONOR:      Flow-Lenia mass conservation and species; DISHTINY group cells; SCL autopoiesis
    ENGINE:     Nestor NPE or a Lenia-class substrate
    WORLD:      A mass-conserving continuous or cellular world where clusters can persist and divide.
    TREATMENTS: fixed boundary; evolvable boundary; evolvable boundary + mass conservation
    CONTROLS:   matched resource budget; no-selection drift control
    PRIMARY:    emergence and persistence of multi-unit reproducing entities
    FALSIFIER:  No persistent multi-unit entities under any treatment, or they appear equally with a fixed boundary.
    CAUSAL:     transplant a candidate entity into a fresh world and measure survival vs its components
    ANTICHEAT:  entity detection must not presuppose the expected structure (validate the detector on synthetic positives and negatives)
    ASSUMPTION COST: Continuous substrates make discrete lineage bookkeeping hard; our existing lineage tooling may not apply.
    DONOR CODE: FlowLenia (verified), DISHTINY (verified, MIT)
    GAP:        Entity detector with validated controls; this is the crux and is reusable for TI-1.
    GATE:       Entities detected with validated detector, persisting and transplanting better than components.
    STOPPING:   Stop if the detector fails its synthetic controls.
    DEPENDS:    none

  AL-5 -- Explicit reproduction opcode vs reproduction from local interactions
    QUESTION:   Does reproduction need a privileged operation, or can it emerge from generic local interactions?
    CLAIM:      Emergent reproduction yields a different distribution of replicator architectures than a reproduction opcode.
    MATTERS:    Determines whether 'reproduction' should be a substrate primitive in future engines.
    DONOR:      Stringmol reactions; BFF self-replicators from random soups; Squirm3 chemistry
    ENGINE:     Nestor NPE
    WORLD:      Random-initialised soup with only generic read/write/execute interactions, plus a matched arm with a copy opcode.
    TREATMENTS: explicit copy opcode; generic interactions only; generic + energy cost
    CONTROLS:   random soup with execution disabled (negative); seeded replicator (positive control for detection only, never as origin evidence)
    PRIMARY:    time to first replicator and architecture diversity of replicators found
    FALSIFIER:  Architecture distributions coincide; the opcode only changes speed.
    CAUSAL:     remove the opcode mid-run and test persistence of existing replicators
    ANTICHEAT:  seeded replicators never counted as spontaneous origin; check for runner-side copying
    ASSUMPTION COST: Emergence is scored by a replicator detector; alien self-maintenance that does not copy is missed.
    DONOR CODE: cubff (Apache-2.0, GPU, verified), stringmol, squirm3
    GAP:        Mostly configuration of an existing donor; cheapest of the AL family.
    GATE:       Distinct architecture distributions with matched compute.
    STOPPING:   Fixed budget; report eligibility if no replicator appears.
    DEPENDS:    none   CONFLICTS: Nestor Z80 campaign overlap

  TI-1 -- When does a collective become the unit of selection?
    QUESTION:   Can a higher-level unit of selection emerge without an explicit group-fitness term?
    CLAIM:      Collective reproduction and specialisation arise from local rules alone when the boundary is evolvable.
    MATTERS:    Bears directly on whether mixture-of-experts-like organisation can emerge rather than be designed.
    DONOR:      DISHTINY hierarchical transitions
    ENGINE:     Nestor NPE or DISHTINY-class substrate
    WORLD:      Spatial world with local resource sharing and heritable cell-level policies; no group fitness term anywhere.
    TREATMENTS: no group term (test); explicit group fitness (positive control); no sharing (negative control)
    CONTROLS:   group term arm proves the detector can see group selection; sharing disabled proves it is not an artefact
    PRIMARY:    evidence of selection acting at the collective level (validated multilevel-selection statistic)
    FALSIFIER:  No group-level signal without the explicit term, under a statistic that detects it in the positive control.
    CAUSAL:     transplant collectives vs matched component sets
    ANTICHEAT:  statistic validated on synthetic data with known group selection present and absent
    ASSUMPTION COST: Multilevel-selection statistics carry their own model of individuality; a transition of another kind will not register.
    DONOR CODE: DISHTINY (MIT, verified, active)
    GAP:        Statistic + validation harness; DISHTINY itself may be runnable as the substrate.
    GATE:       Group-level signal in the test arm with both controls behaving as required.
    STOPPING:   Stop if the positive control shows no signal (instrument invalid).
    DEPENDS:    AL-3

### E. SELF-MODIFYING / EVOLVING MACHINERY

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    EV-1     READY_FOR_DESIGN   M/M      Bellerophon or Crius      Evolving executable machinery vs parameter-only adaptation
    EV-8     READY_FOR_DESIGN   S/M      Bellerophon or Crius      What fraction of apparent improvement is evaluator exploitat
    EV-10    IDEA               M/M      Engine-Five-candidate     Evolution over a skill library vs over whole agents

  EV-1 -- Evolving executable machinery vs parameter-only adaptation
    QUESTION:   Does evolving code/structure outperform tuning parameters at equal compute, and at what reliability cost?
    CLAIM:      Structural (program) change produces larger capability jumps and lower reliability than parameter change.
    MATTERS:    Decides whether our future engines should evolve programs or parameters, and what QA that implies.
    DONOR:      FunSearch, AlphaEvolve, OpenEvolve, DGM
    ENGINE:     Bellerophon or Crius
    WORLD:      A task family with a frozen held-out evaluator and a parameterisable baseline solution.
    TREATMENTS: parameter search only; program mutation only; both
    CONTROLS:   equal evaluations; frozen held-out evaluator; random-program control
    PRIMARY:    held-out performance at equal evaluations
    FALSIFIER:  Program mutation matches parameter search on held-out performance and variance.
    CAUSAL:     transplant the evolved program to a sibling task (EV-9)
    ANTICHEAT:  held-out evaluator never in the loop; detect evaluator exploitation by re-scoring on a second independent evaluator (EV-8)
    ASSUMPTION COST: Program evolution assumes a programmatic representation; competence that is not expressible as code is excluded.
    DONOR CODE: OpenEvolve and DGM verified; AlphaEvolve has no runnable code (results repo only); FunSearch official repo verified
    GAP:        Evaluator harness shared with F5-5 and AS-*; LLM mutation costs need a budget decision.
    GATE:       A difference in held-out performance or variance survives matched evaluations.
    STOPPING:   Preregistered evaluation budget or spend cap.
    DEPENDS:    none

  EV-8 -- What fraction of apparent improvement is evaluator exploitation?
    QUESTION:   How much of self-modification's measured gain disappears under an independent evaluator?
    CLAIM:      A substantial fraction of gains from self-modifying loops is evaluator-specific.
    MATTERS:    We have 26 SCIENCE_DEFECT and multiple cheat-control findings already; this quantifies the tax.
    DONOR:      DGM self-modification; AI Scientist self-evaluation; our own cheat controls
    ENGINE:     Bellerophon or Crius
    WORLD:      EV-1 harness with two independently built evaluators.
    TREATMENTS: single evaluator in the loop; two evaluators alternating; evaluator rotated at a fixed schedule
    CONTROLS:   held-out evaluator built by a different author/process; frozen replay scoring
    PRIMARY:    gain retained under the independent evaluator, as a fraction of in-loop gain
    FALSIFIER:  Retained fraction is near 1 (no exploitation) across loop lengths.
    CAUSAL:     patch the exploited channel and re-run to see whether the gain returns legitimately
    ANTICHEAT:  the experiment IS the anti-cheat measurement; specimens frozen before any patch
    ASSUMPTION COST: Assumes exploitation is detectable by disagreement; correlated blind spots stay invisible.
    DONOR CODE: DGM, OpenEvolve (verified)
    GAP:        Second evaluator must be genuinely independent -- the hard part.
    GATE:       Retained fraction measured with a documented exploit taxonomy.
    STOPPING:   Freeze and stop on the first exploit that changes the substrate.
    DEPENDS:    EV-1

  EV-10 -- Evolution over a skill library vs over whole agents
    QUESTION:   Is search more effective over an acquired library than over the base agent?
    CLAIM:      A library is a better search substrate than a policy: same compute, more improvement.
    MATTERS:    If true, the library is not memory but a new evolutionary substrate -- the strongest argument for Engine Five.
    DONOR:      Voyager library + DGM/OpenEvolve program evolution
    ENGINE:     Engine-Five-candidate
    WORLD:      F5-1 world with a populated library.
    TREATMENTS: evolve the base policy; evolve library entries; evolve composition graph only
    CONTROLS:   equal evaluations; frozen-library control; random-edit control
    PRIMARY:    held-out competence gain per evaluation
    FALSIFIER:  Library evolution matches policy evolution per evaluation.
    CAUSAL:     transplant evolved library entries into a fresh agent
    ANTICHEAT:  held-out tasks fixed before search; detect edits that inline test answers
    ASSUMPTION COST: Assumes the library is the locus of competence; a controller that ignores it makes the test vacuous.
    DONOR CODE: OpenEvolve, DGM, Voyager (all verified/pinned)
    GAP:        Mutation operators over skill payloads.
    GATE:       Library search beats policy search per evaluation on held-out tasks.
    STOPPING:   Preregistered budget.
    DEPENDS:    F5-1

### F. PERSISTENT COMPETENCE

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    MEM-1    READY_FOR_DESIGN   S/M      Engine-Five-candidate or  Which memory forms survive a context reset, transfer and com
    MEM-9    IDEA               M/M      Engine-Five-candidate     Does consolidation compress episodes into competence, and do

  MEM-1 -- Which memory forms survive a context reset, transfer and compose?
    QUESTION:   Across memory forms, which survive context reset, transfer between agents, and compose with each other?
    CLAIM:      Executable and program-like memories survive and transfer; textual and parametric ones do not, at equal bytes.
    MATTERS:    Separates remembering from becoming able; the core of experience-to-competence efficiency.
    DONOR:      Voyager skills; retrieval-augmented memory; option learning; parameter updates
    ENGINE:     Engine-Five-candidate or SFE
    WORLD:      F5-0 world with a fixed competence probe battery.
    TREATMENTS: context; episodic retrieval; semantic summary; demonstrations; executable skill; learned option; controller fragment; program; graph/rewrite rule; parameter update
    CONTROLS:   equal bytes per form; equal compute; scrambled-content control per form
    PRIMARY:    competence retained after context reset, per byte
    FALSIFIER:  All forms perform equally per byte after reset.
    CAUSAL:     cross-transplant each form into a naive agent
    ANTICHEAT:  byte accounting audited; probe battery withheld from all memory content
    ASSUMPTION COST: Byte-matching privileges compact symbolic forms; distributed competence is penalised by construction. State this in the readout.
    DONOR CODE: Voyager (pinned)
    GAP:        Ten memory backends is the cost; a 4-form subset (context, retrieval, executable skill, parameter update) is the S-sized version.
    GATE:       A per-byte ranking with the scrambled controls at baseline.
    STOPPING:   Preregistered budget.
    DEPENDS:    F5-0

  MEM-9 -- Does consolidation compress episodes into competence, and does compression track generalisation?
    QUESTION:   Can many episodes be consolidated into a smaller structure that retains competence, and does the compression ratio predict generalisation?
    CLAIM:      Compression of experience into structure correlates with held-out generalisation.
    MATTERS:    A direct measure of experience-to-competence efficiency, and a candidate promotion signal.
    DONOR:      Skill-library consolidation; model merging (Evolutionary Model Merge, M2N2)
    ENGINE:     Engine-Five-candidate
    WORLD:      MEM-1 world with long runs and a held-out battery.
    TREATMENTS: no consolidation; periodic consolidation; aggressive consolidation
    CONTROLS:   random pruning at the same ratio; size-matched but unconsolidated memory
    PRIMARY:    held-out competence per byte after consolidation
    FALSIFIER:  Consolidation is indistinguishable from random pruning at the same ratio.
    CAUSAL:     restore pruned content and measure recovery
    ANTICHEAT:  random-pruning control rules out 'less is more'
    ASSUMPTION COST: Compression as a proxy for understanding is itself a strong assumption; report it as correlation only.
    DONOR CODE: Model-merge repos pending verification in the top-up
    GAP:        Consolidation operator per memory form.
    GATE:       Consolidated beats random-pruned at equal ratio.
    STOPPING:   Preregistered budget.
    DEPENDS:    MEM-1

### G. SHARED DISCOVERY / MACRO-ORGANISM

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    GEA-1    READY_FOR_DESIGN   M/M      Nestor GraphWorld or Cri  Independent lineages vs shared discovery
    GEA-4    READY_FOR_DESIGN   S/S      Crius or Bellerophon      Raw fossils vs extracted organs
    GEA-6    IDEA               S/S      Nestor GraphWorld         Sharing topology: near vs distant niches

  GEA-1 -- Independent lineages vs shared discovery
    QUESTION:   Does sharing discoveries between evolutionary branches raise cumulative innovation, or cause monoculture?
    CLAIM:      Sharing raises innovation up to a threshold, beyond which diversity and long-run innovation fall.
    MATTERS:    Prometheus IS a population of seats sharing fossils; this tests the macro-organism architecture itself.
    DONOR:      Group-evolving agents; POET transfer; island models
    ENGINE:     Nestor GraphWorld or Crius
    WORLD:      N independent lineages on one world family with a controllable sharing channel.
    TREATMENTS: no sharing; full sharing; selective (top-k) sharing; delayed sharing; within-niche only; cross-niche only
    CONTROLS:   matched compute per lineage; random-payload sharing control (share noise of the same size)
    PRIMARY:    cumulative distinct innovations across the population at equal total compute
    FALSIFIER:  Sharing changes nothing beyond seed variance, or full sharing dominates at every rate (no monoculture cost).
    CAUSAL:     cut the channel mid-run and observe divergence or stagnation
    ANTICHEAT:  random-payload control rules out 'any perturbation helps'; innovation counted on first appearance, deduplicated by mechanism
    ASSUMPTION COST: Assumes innovations are transferable objects; tacit competence that cannot be packaged is invisible.
    DONOR CODE: Pending the catalogue top-up for group-evolving agents; POET transfer verified
    GAP:        Innovation deduplication is the hard part and is reusable for GEA-4 and RA-5.
    GATE:       A sharing-rate optimum, or its absence, established with the random-payload control at baseline.
    STOPPING:   Preregistered budget.
    DEPENDS:    none

  GEA-4 -- Raw fossils vs extracted organs
    QUESTION:   Does access to extracted mechanisms beat access to raw ancestors?
    CLAIM:      Nyx-extracted organs raise innovation per compute more than Techne raw fossils, which beat no access.
    MATTERS:    This is the load-bearing claim of the Techne-to-Nyx pipeline; it has never been tested causally.
    DONOR:      DGM archive selection; fossil injection; Nyx organ extraction
    ENGINE:     Crius or Bellerophon
    WORLD:      A task family where known historical solutions exist in our fossil vault.
    TREATMENTS: no access; raw fossil access; extracted organ access; organ access with provenance hidden
    CONTROLS:   irrelevant-fossil control (same bytes, wrong domain); matched retrieval cost
    PRIMARY:    innovations per unit compute, and rediscovery cost avoided
    FALSIFIER:  Organ access matches raw fossil access, which matches the irrelevant-fossil control.
    CAUSAL:     withdraw access mid-run; measure whether the advantage persists (internalised) or collapses (dependency)
    ANTICHEAT:  irrelevant-fossil control; artefacts hashed; solutions diffed against them to detect copying rather than reuse
    ASSUMPTION COST: Extraction privileges mechanisms that survive being named and packaged; unpackageable advantages are scored as worthless.
    DONOR CODE: Internal: techne/fossils (121 fossils, 105 runnable), nyx/atlas organs
    GAP:        Injection harness; no external donor needed.
    GATE:       Ordering (organ > fossil > none) with the irrelevant-fossil control at baseline.
    STOPPING:   Fixed budget.
    DEPENDS:    none

  GEA-6 -- Sharing topology: near vs distant niches
    QUESTION:   Is sharing more productive within related niches or across distant ones?
    CLAIM:      Cross-niche sharing produces rarer but larger innovations; within-niche sharing produces more, smaller ones.
    MATTERS:    Informs how seats should route findings to each other.
    DONOR:      Island models; POET transfer; QD cross-niche recombination
    ENGINE:     Nestor GraphWorld
    WORLD:      GEA-1 harness with a niche-distance metric.
    TREATMENTS: within-niche; adjacent-niche; distant-niche; random-pair
    CONTROLS:   matched share volume; random-payload control
    PRIMARY:    innovation size distribution by sharing distance
    FALSIFIER:  Distance has no effect on innovation size or rate.
    CAUSAL:     swap the distance metric and re-run (metric sensitivity)
    ANTICHEAT:  distance metric fixed before the run
    ASSUMPTION COST: Requires a niche metric; if the metric is wrong, the result is about the metric.
    DONOR CODE: As GEA-1
    GAP:        Distance metric definition.
    GATE:       A distance effect survives the metric-swap check.
    STOPPING:   Fixed budget.
    DEPENDS:    GEA-1

### H. AUTOMATED SCIENCE

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    AS-3     IDEA               S/M      Archaeon frontier (or a   Branch selection: random vs expected-information-gain
    AS-6     IDEA               XS/S     Archaeon frontier + Atla  Can an autonomous system recover a hypothesis it previously 

  AS-3 -- Branch selection: random vs expected-information-gain
    QUESTION:   Does information-gain-driven branch selection increase discovery per compute without increasing false discovery?
    CLAIM:      EIG selection beats random branch selection on true discoveries per compute at equal false-discovery rate.
    MATTERS:    Archaeon's frontier scheduler already selects branches; this tests the selection rule itself.
    DONOR:      AI Scientist branch search; OMNI-EPIC interestingness; our frontier queues
    ENGINE:     Archaeon frontier (or a simulator of it)
    WORLD:      A synthetic hypothesis landscape with known ground truth, plus a replay of our own frontier queue decisions.
    TREATMENTS: random branch; EIG branch; greedy-score branch; our current scheduler
    CONTROLS:   ground-truth landscape with known true/false hypotheses; fixed compute per arm
    PRIMARY:    true discoveries per unit compute at matched false-discovery rate
    FALSIFIER:  EIG matches random at equal compute and FDR.
    CAUSAL:     replay our historical frontier decisions under each rule and compare outcomes
    ANTICHEAT:  ground truth hidden from the selector; false-discovery rate measured on held-out confirmation
    ASSUMPTION COST: EIG needs a model of the hypothesis space; genuinely alien hypotheses have no prior and are never selected.
    DONOR CODE: AI Scientist v1/v2 verified repos
    GAP:        Synthetic landscape generator; the replay half needs no new donor.
    GATE:       A rule beats random on discoveries per compute at matched FDR.
    STOPPING:   Fixed budget.
    DEPENDS:    none

  AS-6 -- Can an autonomous system recover a hypothesis it previously rejected?
    QUESTION:   Do automated campaigns ever revisit and revive correctly-rejected-then-wrong rejections?
    CLAIM:      Without an explicit revival mechanism, rejected hypotheses are never recovered, even when later evidence supports them.
    MATTERS:    Our own loops park and supersede; this measures whether parking is reversible in practice.
    DONOR:      AI Scientist branch pruning; our frontier suppressions and CW01 stasis records
    ENGINE:     Archaeon frontier + Atlas analysis
    WORLD:      Synthetic landscape where a hypothesis becomes true only after a later capability exists.
    TREATMENTS: prune permanently; prune with scheduled revival; never prune
    CONTROLS:   ground truth with known revival epoch
    PRIMARY:    recovery rate of revivable hypotheses
    FALSIFIER:  Permanent pruning recovers as well as scheduled revival.
    CAUSAL:     compare against our own historical suppression records (PROTEUS-46, CW01 stasis)
    ANTICHEAT:  revival schedule hidden from the selector
    ASSUMPTION COST: Revivability is defined by the planted schedule.
    DONOR CODE: AI Scientist v2 (verified)
    GAP:        Shares AS-3 infrastructure.
    GATE:       Recovery-rate difference established.
    STOPPING:   Fixed budget.
    DEPENDS:    AS-3

### I. REANALYSIS OF EXPERIMENTS WE HAVE ALREADY RUN

    id       status             cmp/eng  engine                    title
    -------  -----------------  -------  ------------------------  -----------------------------
    RA-1     READY_FOR_DESIGN   XS/XS    Atlas analysis over arch  REANALYSIS: did frontier queue pools act as a curriculum?
    RA-2     NEEDS_DONOR        S/M      Atlas analysis over nest  REANALYSIS: learned descriptors over old GraphWorld and CW01
    RA-3     READY_FOR_DESIGN   XS/XS    Atlas analysis            REANALYSIS: evaluator-exploitation census across campaigns
    RA-4     IDEA               XS/S     Atlas analysis over Criu  REANALYSIS: Crius PARTS takeovers as a cross-niche recombina
    RA-5     IDEA               XS/M     Atlas analysis            REANALYSIS: rediscovery rate across seats and lineages

  RA-1 -- REANALYSIS: did frontier queue pools act as a curriculum?
    QUESTION:   In our own DEEP FRONTIER history, did pool/priority assignment predict subsequent detector firings better than chance?
    CLAIM:      Existing queue decisions already contain a measurable curriculum effect.
    MATTERS:    Answers part of UED-1 with data we already hold; costs compute we already spent.
    DONOR:      PLR/ACCEL prioritisation concepts applied post hoc
    ENGINE:     Atlas analysis over archaeon.frontier
    WORLD:      None -- existing records.
    TREATMENTS: observed pool assignment; permuted assignment (null)
    CONTROLS:   time-shuffled null; budget-matched subsets
    PRIMARY:    firings and evaluations per queued item by pool, vs permutation null
    FALSIFIER:  Pool assignment carries no signal beyond the permutation null.
    CAUSAL:     none possible retrospectively; state it as association only
    ANTICHEAT:  null built by permuting assignment within time windows
    ASSUMPTION COST: Retrospective association only; no causal claim is licensed.
    DONOR CODE: None needed
    GAP:        A single SQL/notebook pass over atlas.*
    GATE:       Report with eligibility count stated first.
    STOPPING:   One pass.
    DEPENDS:    none

  RA-2 -- REANALYSIS: learned descriptors over old GraphWorld and CW01 runs
    QUESTION:   Do AURORA-style descriptors fitted post hoc reveal behaviour clusters, transitions or anomalies our original metrics missed?
    CLAIM:      Our historical archives contain structure our hand-chosen metrics did not capture.
    MATTERS:    The operator's explicit request: find missed science in what we already ran.
    DONOR:      AURORA unsupervised descriptors
    ENGINE:     Atlas analysis over nestor.graphworld and nestor.cw01
    WORLD:      None -- existing rows and QD cells.
    TREATMENTS: learned descriptors; original human descriptors
    CONTROLS:   random-projection descriptors; shuffled-time control; synthetic data with known clusters
    PRIMARY:    count of behaviour clusters not separable under the original metrics, validated against the synthetic control
    FALSIFIER:  No cluster structure beyond random projections.
    CAUSAL:     none retrospectively; flag candidates for prospective test
    ANTICHEAT:  descriptor fit blind to outcome labels; synthetic positive control must pass first
    ASSUMPTION COST: The embedding's geometry decides what counts as a cluster.
    DONOR CODE: QDax verified; AURORA pending top-up
    GAP:        Descriptor pipeline (shared with QD-3, F5-6).
    GATE:       Clusters survive the random-projection and shuffled-time controls.
    STOPPING:   Stop if the synthetic control fails.
    DEPENDS:    QD-3

  RA-3 -- REANALYSIS: evaluator-exploitation census across campaigns
    QUESTION:   Across all campaigns, how often did organisms or agents exploit the evaluator, and which control caught it?
    CLAIM:      Cheat controls, not positive controls or human reading, caught most exploitation.
    MATTERS:    Quantifies the value of our cheat-control doctrine and feeds EV-8's design.
    DONOR:      Our own defect ledgers and control facts
    ENGINE:     Atlas analysis
    WORLD:      None -- existing records.
    TREATMENTS: census by campaign, category and detecting control
    CONTROLS:   classification validated on a hand-labelled sample
    PRIMARY:    exploitation events per campaign and detecting mechanism
    FALSIFIER:  Exploits are too rare or too unevenly recorded to support any rate claim (report as such).
    CAUSAL:     none; descriptive
    ANTICHEAT:  hand-label a sample to measure classifier error before trusting counts
    ASSUMPTION COST: Only recorded exploits count; undetected ones are invisible by construction, which is the finding's main limit.
    DONOR CODE: None needed
    GAP:        One analysis pass plus hand labelling.
    GATE:       Census published with classifier error stated.
    STOPPING:   One pass.
    DEPENDS:    none

  RA-4 -- REANALYSIS: Crius PARTS takeovers as a cross-niche recombination result
    QUESTION:   Do Crius's existing recombination-arm takeover logs already show whether donor splices beat within-lineage variation?
    CLAIM:      The C2 recombination arm contains a usable answer to QD-9 at zero additional compute.
    MATTERS:    Prefer reanalysis before rerun; Crius ran the arm for another purpose.
    DONOR:      MAP-Elites recombination; Crius PARTS donors
    ENGINE:     Atlas analysis over Crius campaign 2
    WORLD:      None -- existing takeovers.jsonl and PARTS diagnostics.
    TREATMENTS: donor-splice offspring; within-lineage offspring
    CONTROLS:   paired common-random streams already used by Crius; structural-distance matched pairs
    PRIMARY:    takeover rate and selective value by donor distance
    FALSIFIER:  Donor distance has no association with takeover rate.
    CAUSAL:     none retrospectively; flag for prospective QD-9
    ANTICHEAT:  use Crius's own paired streams; do not re-derive significance from selected populations
    ASSUMPTION COST: Crius's distance metric is inherited wholesale.
    DONOR CODE: None needed
    GAP:        Index Crius campaign 2 first (Atlas does not yet harvest Crius).
    GATE:       Association reported with eligibility counts.
    STOPPING:   One pass.
    DEPENDS:    none

  RA-5 -- REANALYSIS: rediscovery rate across seats and lineages
    QUESTION:   How often have independent Prometheus lineages rediscovered the same mechanism?
    CLAIM:      Rediscovery is common enough to justify the fossil/organ pipeline (GEA-4).
    MATTERS:    Sizes the value of sharing before we build more sharing machinery.
    DONOR:      Group-evolving agents; our own mechanism ledgers
    ENGINE:     Atlas analysis
    WORLD:      None -- Nyx mechanism ledger, Techne fossils, campaign conclusions.
    TREATMENTS: mechanism-level deduplication across campaigns and seats
    CONTROLS:   hand-labelled sample for dedup accuracy; name-only matching as a weak baseline
    PRIMARY:    count of mechanisms independently arrived at more than once
    FALSIFIER:  Rediscovery is rare, weakening the case for organ sharing.
    CAUSAL:     none; descriptive
    ANTICHEAT:  dedup validated on labelled pairs before counting
    ASSUMPTION COST: Dedup by description privileges mechanisms that were named; unnamed convergence is missed.
    DONOR CODE: None needed
    GAP:        Mechanism dedup (shared with GEA-1).
    GATE:       Rate reported with dedup accuracy.
    STOPPING:   One pass.
    DEPENDS:    none

