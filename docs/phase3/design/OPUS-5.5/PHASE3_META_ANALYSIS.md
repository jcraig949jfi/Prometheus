# Prometheus Phase 3 -- independent meta-analysis, requirements and architecture

Architect: Epimetheus, IDENTITY OPUS-5.5 (runtime model claude-opus-5-5). Date: 2026-10-01.
Charter: roles/Epimetheus/prompts/2026-10-01_charter/ (verbatim, MANIFEST). Independence: no other architect's design
files were read (one exposure of file names on a git merge is recorded in the seat journal).

Package: this file; REQUIREMENTS.md (+ requirements.jsonl, tools/); RSE_ARCHITECTURE.md; ENGINE_PORTFOLIO.md;
SALVAGE_MATRIX.md (+ salvage.jsonl); OPEN_QUESTIONS.md; ASSUMPTIONS.md; FALSIFIERS.md; evidence/ (twelve reader digests,
353 historical evidence profiles, 100 verified load-bearing claims); experiments/ (X0 preregistration, codes, result);
salvage/ (component digests).

Order of work, checkable in git: charter verbatim (af4e0a3f6) -> evidence intake and X0 preregistration (d6f555fd7) ->
requirements v2, architecture and portfolio FROZEN before any salvage reading (77d3c99c3) -> salvage matrix and this
analysis (later commits).

Method, briefly. The four forensic packages were read in full by the architect; twelve parallel readers then read every
seat dossier, the indexes, the ruler inventory, the Ixion maps, the Atlas materials and external prior art, and an
adversarial verifier per reader checked the readers' load-bearing claims against the underlying artifacts (100 claims:
82 confirmed, 18 partially confirmed, 0 refuted). A first-principles requirements draft was attacked by a five-lens
critic panel and by five advocates of competing architectures with a judge; the judge's decisive experiment (X0) was
preregistered and run. Every agent in this pipeline is Claude-family; the same independence discount the crawlers
applied to themselves applies here (s13, s25).

----------------------------------------------------------------------------------------------------------------------

## 1. Executive thesis

1. **Prometheus built a scientific process before it built scientific instruments.** Preregistration, controls,
   provenance and unusually hard self-correction are real; the apparatus they wrapped mostly could not reveal the
   phenomena under test. Of 130 historical nulls profiled, 2 had substrate capacity, world demand and ruler validity all
   demonstrated. Of 146 instruments, 30 showed they could output the class they ruled on, and about one measured an
   organism property. One of 171 indexed engines combined an adapting organism, a world with latent state and a ruler
   of demonstrated detectability -- and its "organisms" were hand-chosen estimators.

2. **The binding constraints were world demand, ruler validity, search reach and independence -- not organism
   expressiveness.** A preregistered desk audit (X0) of 210 historical apparatus nulls and false positives found the
   cheapest repair was a qualified ruler for 54%, provenance or implementation for 14%, world demand for 9%, statistics
   for 8%, search for 5%, a same-substrate capacity proof for 5% -- and a second substrate for 0% (blind-coder kappa
   0.935).

3. **Phase 3 should therefore be an instrumented developmental observatory around one deeply instrumented primary
   substrate**, not one integrated "Recursive Sagacity Engine" and not a portfolio of separately authored engines. A
   shared Reality layer with a signed verdict job, a world forge that certifies cognitive depth with bounds, and a
   measurement bench whose rulers are qualified on authored and procedurally generated planted organisms host one
   primary developmental substrate whose affordances are switches on one code path, one familiar reference learner per
   world family, a tiny probe kernel by a different author, and a second full substrate commissioned on measured
   triggers. Scientific questions (engines E3-E8) are run on this observatory in a staged sequence.

4. **The object of study is what an organism can become, measured as a distribution of developmental trajectories,
   not what it does.** "Transferable sagacity" is operationalised as censoring-aware reduction in acquisition cost on
   structurally novel families against capacity-matched controls; "recursive sagacity" as acceleration carried by
   developed structure of write-order three or more, shown by reversion and donor-depth transplant, which a fixed
   learning rule with a growing library cannot fake.

5. **The first quarter is mostly instrument qualification.** The first scientific act is to reproduce a developmental
   result whose answer is known (lifetime learning evolves when environments vary within lifetimes and not when they
   are static) end to end through the ledger and verdict job. Nothing broad is built before that vertical slice
   passes; open-ended search begins only after it.

6. **Interpretable negatives are first-class.** A phenomenon-level null is issued only as a null certificate, bracketed
   by a positive of the same type at an easier point of a declared difficulty axis, and stated as not-detected-above
   an MDE anchored to a constructive organism. Most historical nulls would be typed as nulls about the apparatus.

## 2. What Prometheus actually built

Quantities from the four indexes and the twelve digests (evidence/idx.md and others; counts are crawler- or
reader-derived and carry their tags):

    seats in roles/ (census)                 63 (charter: ~59)
    commits indexed                          11,779 (7,224 in September 2026)
    Python lines                             ~3.19M; ~39% LLM-forged reasoning-tool scrap; ~27% math-catalogue and
                                             falsification pipelines; ~20% organism/world engines
    engine/lens records (deduplicated view)  171; instruments outnumber simulations 58:34; 26% self-describe as
                                             toy/prototype/unrun
    engines with any adapting organism       44/171 (29 population-only, 12 lifetime-only, 3 both)
    engines with latent state to infer       12/171
    adapting x latent x demonstrated ruler   1/171
    highest verified realised demand         about a one-cue latch (D3); 15 engines designed for hidden-state or
                                             compositional demand, 1 realised it
    rulers (distinct)                        146: 30 detectability YES, 56 PARTIAL, 60 NO; cross-substrate tested: 2
    later-correction rows                    139 against 357 reported results (0.39)

What exists, by kind. **Substrates**: three Z80-like byte soups with real heredity instrumentation; the Proteus
instruction VM that carried most evolutionary campaigns; Crius's register VM with a persistent executable workspace
(the richest organism); Ares recurrent graph organisms with carrier attribution; Ananke's deterministic message-passing
substrate with a bit-exact CPU oracle; Aether's byte lattice; Tyche's evolved causal feature programs; Ensorain's
bounded tensor-train regressors. **Worlds**: Ludus exactly solvable games with depth profiles and a differential leak
audit; Bellerophon's world kernel with receipts; Ensorain's world-genome foundry and answer-keyed hidden-state
processes scored against exact Bayes; Cosmos's world graph with a sealed holdout broker. **Measurement**: material-grade
descent tracers (taint VM, z8taint), the CVT-R heredity certificate validated on a constructed panel, Charon's
three-valued checks, Nemesis cheatlib, Harmonia's audit primitives and standing rules, Tyche's causality audit with a
future-reading cheat, Ensorain's null ladder, Cosmos's definition rung and location attack, a qualified Bernoulli(f)
damage ruler. **Infrastructure**: the comms queue, verbatim hashed prompts, Agent Fabric, the Atlas index, the Achilles
census, the evidence wiki and campaign reader, SFE's hash-chained ledger with prediction-before-observation, Vivarium's
blind executor, a workspace guard.

What it mostly was: an **instrument foundry**. The positives that survive scrutiny are overwhelmingly instrument
positives (99 of 353 profiled results), while the organism-level positives that survive are anomalies with recorded
weakenings (20).

## 3. What Prometheus learned from failure

The recovered failure history (Tityos's 24 classes, Sisyphus's 15 and Tantalus's 19 confound classes, Ixion's
institutional failure modes; 70 classes in all, each mapped to an enforced requirement in REQUIREMENTS.md) reduces to
six lessons that drive the design:

1. **The measurement carried its own answer.** Metadata inside measured vectors, answer keys inside probes, generators
   writing their own verdicts (99.98% of 658M records), labels standing in for material provenance (26 "spontaneous
   replications" -> 0), payload fields that map to the answer. Design response: physics never consults the ruler
   (WLD-14); all-channel differential leak audits (WLD-07); rulers with input manifests and label-permutation
   invariance (MEA-01); mechanical verdict authority (PRV-02).
2. **Controls that could not fail and instruments never shown able to detect.** Hard-coded PASS rows, silence-forcing
   ablations, a mirror design that forced a control to exactly .500, a novelty detector whose UNFAMILIAR class was
   unreachable by definition. Executed controls caught defects within a day; reading-based audits took months.
   Response: the instrument qualification layer (MEA-01), controls wired to abort (MEA-05), canaries with a dead-man
   switch (MEA-17), qualified definitions (MEA-16).
3. **The cheap baseline arrived after the data -- and won.** A one-float running mean, a same-class tuned batch
   estimator, a coprime-to-30 one-liner, a constant answer beating 120 of 122 tools, a zero-parameter definition rule
   tying mined laws. Response: the automatic baseline ladder with chance floors (MEA-03).
4. **Nulls were about the apparatus.** Worlds that needed at most one bit, organisms that could not express the
   question, plants that existed in the searched space and were never found, greedy walks that could not accept a
   neutral step, lifetimes shorter than learning time. Response: typed nulls, null certificates, bracketing,
   developability proofs, reachability estimators, pressure certificates (SCI-03/08/13/14, DEV-13, PRS-03/12).
5. **Independence was a label.** One model family authored, executed, scored and audited; "N seats agree" meant one
   substrate agreeing with itself; councils sent one prompt to four vendors. Response: computed independence classes
   (REP-06), cross-family re-derivation at L4 (REP-04), sealed procedurally generated plants (MEA-02).
6. **Coordination consumed the inference.** 86 model-written heartbeats in 25 hours, 432 state-file commits in four
   days, seven control orders (16,858 words) in 40 hours, the operator as the relay between seats and models.
   Response: derived status (INF-03), inference only at declared forks with token accounting (INF-01/02/06), bounded
   operator attention (HUM-01/04), a vertical slice before breadth (CMP-07).

## 4. Scientific maturity assessment

Prometheus is **premature science**: a genuinely scientific process applied, mostly, to apparatus that was not yet a
scientific instrument. It is not research cosplay. Three behaviours rule that out: it killed its own attractive results
repeatedly and fast (most corrections were made by the claiming seat, often within hours); it invented and adopted the
right norms (reachability-first, absence-needs-a-positive, freeze-precedes, verdict names a shortcut cannot pass); and
its best late instruments can fail both ways. But serious process did not create serious science. The evidence-profile
axes over 353 profiled results show it plainly:

    axis   Y     P     N     U     reading
    Q      249   48    52    4     questions were usually falsifiable
    S      145   48    58    102   substrate capacity often unshown
    W      37    85    128   103   world demand rarely demonstrated -- the weakest axis
    R      62    159   121   11    ruler validity mostly partial
    B      120   108   89    36    baselines improving, often post-data
    Rep    20    112   208   13    independent replication rare (replay is not replication)
    M      24    69    216   44    mechanism by intervention rare

The defensible external description: an unusually extensive independent experimental programme with increasingly
sophisticated controls, prototype-grade instruments, almost no world-demand certification, and no externally
validated scientific claims about cognition.

## 5. Why historical results are insufficient

Not because they are false -- most were never in a position to be true or false about cognition. The record's worlds
demanded at most small finite-state control; its organisms often could not act, learn, or change their own structure;
its rulers were seldom qualified; its searches were budget-capped below known needle sizes; its replications were
mostly replays; its independence was nominal. The few positives with recorded weakenings (a delay-invariant reader
that may be a start-anchored latch; super-additive propagation that is a relay; a fused sensor below its bar;
internalisation in 8 of 144 runs) are worth keeping as anomalies to re-test under qualified instruments, not as
findings. The 21 profiled true negatives are mostly about specific instruments or designs (for example "the withheld
benchmark recovered 0 of 36"; "the lattice freezes within 2,500 ticks"), which is valuable as negative knowledge about
apparatus.

## 6. First-principles model of cognitive development

The measured object is the triple (developmental program g, environment-family distribution or curriculum C, budget B)
mapped to a distribution of developmental trajectories. The proposed causal chain -- experience, regularity,
representation, compressed structure, reusable operation, abstraction, reasoning over abstractions, reasoning about
reasoning -- is treated as a hypothesis with a test at each link rather than as a ladder to climb:

    link                                   what must be physically true                    test
    experience -> regularity               the world family has latent structure shared      certificate: Delta > 0,
                                           across episodes and families                     d_comp > 0
    regularity -> retained state           cross-episode writable state; development is      retention boundary (DEV-04)
                                           whatever survives the episode boundary
    state -> compressed structure          a pressure that makes compact structure cheaper   abstraction criterion 3 in
                                           (metabolic cost, reuse) and a way to restructure  two description languages
    compressed -> reusable operation       stored structure invocable from several contexts  specificity across families;
                                                                                             interchange
    reusable -> abstraction                reuse across structurally distinct families,      surface invariance; transfer
                                           invariant to surface encoding                     on two-sided-certified T_new
    abstraction -> reasoning over it       composition of carriers in combinations unseen    d_comp certificate; held-out
                                           during development                                compositions
    -> reasoning about reasoning           developed structure that modifies the machinery   write order >= 3; reversion;
                                           that builds learning components                   donor-depth transplant

Compression is not cognition by itself: storage of 1,000 solutions compresses nothing; 100 patterns compress
observation; 20 strategies compress policy; 5 transferable principles compress future acquisition. Only the last is
sagacity in this package's sense, measured as bits of task-specific feedback the organism no longer needs. Four
quantities are kept apart: substrate expressibility (constructive proof), developmental capacity (a reaction norm over
budgets and curricula, with crossing evidence), realised competence (episode-reset evaluation), and transferable and
recursive sagacity (REQUIREMENTS.md s3).

## 7. Organism requirements

Affordances, not modules (REQUIREMENTS.md s6). Required: persistent writable state within and across episodes;
selectable access to stored state as a capacity (not a mandated primitive); conditional control; structural
create/delete/copy/modify during the lifetime; metered internal steps; in the primary substrate, modifiable
modification machinery as a lattice switch. Required instrument affordances: keyed determinism, snapshot/restore,
stable ids, a material provenance shadow from day one, intervention hooks for every carrier class in a closure audit.
Physics options: multiple timescales, invocable stored structure, neutral genotype-phenotype redundancy. Never built
in: working-memory buffers, attention modules, hypothesis slots, confidence outputs, planners, world-model modules,
labelled abstraction operators. Allowed to emerge and never required by a ruler: modularity, consolidation, hierarchy,
binding, internal simulation, uncertainty representation, metacognitive control, communication. Capacity proofs may be
obtained by any recorded procedure (compilation, synthesis, privileged search), so the substrate need not be
human-programmable. Each affordance is tested by a lattice contrast on one code path.

## 8. Developmental physics

Development is separated from evolution as a declared timescale with independent switches (DEV-01). What evolution
specifies is the developmental program and physics settings; what development constructs is task-specific and
reusable structure; what the world teaches is carried only by the statistics of the curriculum. "Constructing
cognition" is distinguished from optimising parameters by experience-specificity, carriage by developed structure, and
a construction advantage over the strongest value-only learner on a pre-grown structure of the final size (DEV-05).
Every developmental claim carries a claim-indexed control set: same-compute direct exposure, shuffled curriculum,
retention-boundary freezing, an irrelevant-experience twin, yoked replay, and constant/lookup baselines per rung
(DEV-02). Developmental capacity proofs (a genome in the searched language that develops the capability within the
lifetime) gate developmental nulls (DEV-13). Lifetimes must exceed three times that genome's acquisition time (WLD-18).
Stage-like development is a hypothesis measured by change-point analysis, never a promotion criterion (DEV-08).

## 9. World requirements

World size is not cognitive depth. Every family carries a bound-typed depth certificate (gap to the best memoryless
policy, gap to canonicalised lookup on held-out instances, information horizon, a bracketed minimal-memory bound, and
where claims need them compositional depth, live hypotheses, value of information, nonstationarity, a deliberation
time-space ratio, the adaptive gap and payback ratio, distance to the best familiar policy, and policy multiplicity).
Families are admitted only when cheap baselines and acquisition-matched finite-state learners fail by margins exceeding
the ruler's MDE and solvability is witnessed. Worlds are generated in families with sealed, quotient-disjoint splits;
evaluation families are authored independently of substrate and rulers; two independent certificate tools are checked
on sealed known-answer worlds including a Nim-like decoy. The first ten anchor families (RSE_ARCHITECTURE.md s4) span
the pressure ladder, hidden state, keyed binding, procedure reuse, composition, deliberation, epistemic pressure,
bias-shift sequences and surface-varied recurrence.

## 10. Evolutionary and search pressures

When does development pay? The answer is computed, not assumed (REQUIREMENTS.md s5): P0 static (development is waste at
equilibrium); P1 per-lifetime variation with adaptive gap Delta and payback ratio rho predicting innate-adaptive
programs versus slow-state plasticity; a separate ruggedness axis predicting transient Baldwinian learning; P2 shared
latent structure across environments in long lifetimes; P3 shifting learning biases; P3b open-ended bias growth (the
only regime that predicts recursion); P4 ecology. A level is in force only when a pressure certificate shows the capable
fixture wins under the exact selection regime with N_e*s >= 10. Search policy, recombination and the optimiser are
declared factors; every "not found" carries a reachability estimate from a rediscovery-from-distance curve; no arm
launches below the budget that gives three expected hits on a planted target (concentration floor). Scalar fitness is
not assumed sufficient: lexicase and quality-diversity selection over stable behavioural and intervention signatures
are available, with a strict noise-free counterfactual arm.

## 11. Measurement and instrument qualification

No ruler emits verdict-bearing rows until its committed dossier shows: definition in atomic variables; attainable
verdict set; planted-positive sensitivity curves on the actual pipeline, separately for authored and procedurally
generated plants (a ruler insensitive on generated plants is FAMILIAR-ONLY and cannot support phenomenon-level nulls);
matched-negative false-positive rate; the cheapest-cheat battery; neutral and dilution invariance; failure regimes;
label-permutation invariance and a content-stripped metadata classifier at chance; and a qualification hash over the
full measurement closure recomputed at verdict time (MEA-01). The X0 result -- ruler repair was the cheapest fix for
54% of historical failures -- is the strongest argument in this package for building this layer first. The rulers that
must exist before discovery claims are listed in RSE_ARCHITECTURE.md s5; each operational definition is itself a
qualified predicate whose planted battery includes the cheapest organisms satisfying each clause without the property
(MEA-16).

## 12. Signal versus hallucination architecture

Each historical failure mode is made difficult or impossible by a named, enforced mechanism (the full map is generated
in REQUIREMENTS.md; the checker fails if any of the 70 classes loses its BLOCK- or RULE-enforced requirement):

    failure class (examples)                       mechanism that blocks it
    leakage / answer in the measurement             all-channel differential leak audit; physics never reads rulers;
                                                    ruler input manifests; label-permutation invariance
    baseline omission                               automatic baseline ladder; missing rung blocks the verdict
    tautological / impossible-to-fail controls      controls wired to abort; fired-once on sealed cheats; mutation tests
    ruler saturation, uncalibrated detectors        qualification dossiers; FAMILIAR-ONLY class; dilution invariance
    shared-code "independence"                      computed independence classes from access logs and import graphs
    seeded phenomena read as endogenous             material provenance shadow; fixture/plant ancestry tags;
                                                    model-free reference arm with MODEL-SEEDED typing
    selection on holdouts                           encrypted sealed splits decrypted only in evaluation;
                                                    consumable confirmatory reads
    cheap proxy strategies                          definition-as-rule rung; latch and payload readers; MEA-16 batteries
    unreachable search regions                      reachability estimator; concentration floor; bracketed nulls
    post-hoc interpretation                         executable preregistration as an earlier commit; runner refusal
    forking preregistrations                        ledger-derived multiplicity
    infrastructure hubs read as primitives          L4 specificity, double dissociation and interchange
    naming-layer hallucination                      vocabulary lock: defined terms only when the predicate is TRUE
    promotion without demotion                      dependency-driven mechanical demotion; challenge suspension
    a gate that silently stops working              standing canaries per failure class with a dead-man switch

The single structural principle: the component that generates a candidate never writes its verdict, and every verdict
can be recomputed from committed, computed rows by a signed batch job.

## 13. LLM epistemic escape

Can a search system mediated by historical human priors discover unfamiliar cognitive machinery? Possibly, but not by
an LLM inventing and recognising it. The design separates four roles in code: Generation (mutation, recombination,
procedurally generated primitive bases, and -- only in one budgeted campaign -- an information-isolated LLM operator)
proposes; Reality (worlds, development, interventions, qualified rulers, the verdict job) decides survival;
Interpretation (models, humans, prior-art search) proposes experiments and descriptions and can never delete or demote.
The prior enters through more than per-edit proposals: through authored primitive sets, mutation kernels, plants and
world admission. Hence the anti-gravity mechanisms: a model-free reference arm in every campaign family that uses any
model-authored material (claims above L2 reproduce there or are tagged and capped); grammar gravity (each L3+ mechanism
re-searched under procedurally generated bases; mechanisms short only in the authored basis are GRAMMAR-BORNE);
procedurally generated plants that ruler authors never inspect; an executable familiarity reference whose UNFAMILIAR
outcome is shown reachable before use; a material-descent gravity meter; mechanical follow-up allocation that serves
first the candidates no model proposed an experiment for; minimal causal cores before any interpretation so that
opacity is not rewarded. Unclassifiability raises priority only after the behavioural and causal gates and is never
evidence. How we would know: E8 measures directly whether the isolated LLM operator increases validated findings per
unit cost and whether its survivors are more familiar than the model-free arm's.

## 14. Recursive sagacity definition

Operational definition (REQUIREMENTS.md s3, DEV-14): every lifetime write is tagged with its writer set; structure
written with an order-k writer has order k+1; recursion is order >= 3. A claim requires acceleration of acquisition on
sealed held-out families beyond matched twins (R1), removal of a declared fraction by reverting order >= 3 structure
(R2), donor-depth dose-response in both the host's acquisition cost and its subsequent learning-to-learn slope (R3), no
effect from irrelevant-experience donors (R4, excluding maturation clocks), and no outer optimiser in the lifetime (R5).
What would demonstrate something beyond ordinary learning-to-learn: a gradient meta-learned recurrent learner and a
fixed rule with a compositional library both produce savings and even a temporarily accelerating learning-to-learn
slope, but neither produces order >= 3 writes whose reversion removes the acceleration while order <= 2 structure is
kept. The regime must predict recursion (P3b) for a negative to be phenomenon-level.

## 15. Proposed Phase 3 architecture

RSE_ARCHITECTURE.md: an instrumented developmental observatory around one primary substrate. Six layers (Reality kernel;
world forge; measurement bench; substrates; search and pressure; interpretation at forks). The primary substrate is a
developmental graph machine: nodes are small register machines; developmental instructions (spawn, link, unlink,
rewrite, set-decay, prune) are ordinary instructions, so the rules of development are rewritable state; two genotype
encodings; every affordance a lattice switch on one code path. One CPU-trainable familiar reference learner per family;
a probe kernel of about 1.5k lines by a different author; a second full substrate on triggers (a claim at L4, needle
inflation > 100x, a blind physics-span check, or the probe kernel's X1 threshold outside the primary's span). Staging:
S1 vertical slice (days 0-30), S2 qualification with a day-60 kill gate, S3 first discrimination (days 61-90), S4
programme.

Alternatives considered and why they lost (judge scores in RSE_ARCHITECTURE.md s1): one integrated always-running
engine (attribution re-staged inside a coupled loop; the Deep Frontier shape); 10-12 separately authored engines (the
fossil record again: same-family breadth, split budgets, search-limited nulls); LLM program synthesis first (the prompt
is an answer channel; survivors invite mechanism-by-reading); ecology-first soup (copying without competence; no
qualified open-endedness metric); three bespoke substrates from the start (six kernels before any L4 candidate; split
budget; convergence without an instrument).

## 16. Engine portfolio

ENGINE_PORTFOLIO.md details eleven engines with the charter's fields. Instrument engines: E0 Reality kernel and verdict
authority; E1 instrument qualification lab; E2 world forge and depth certification. Science engines: E3 when
development pays (pressure transitions; known positive); E4 constructive development and reusable structure; E5
epistemic pressure and the emergence of self-monitoring; E6 recursive plasticity; E7 mechanism transplant and
cross-substrate convergence (trigger-gated); E8 generation source and the gravity meter. Deferred or narrow: E9 yoked
ecology arm; E10 probe-kernel substrate variance. They share one substrate, one forge, one bench and one verdict job, so
their results are comparable and the search budget is not split twelve ways.

## 17. Prometheus salvage analysis

SALVAGE_MATRIX.md (written after the freeze). Seven evaluators read the source and tests of 143 components against the
frozen requirements; an adversarial skeptic attacked every reuse recommendation with probes run in scratch copies.
Skeptic-adjusted result: KEEP 0; HARDEN 6; EXTRACT 2; REBUILD 31 (8 greenfield, 23 keeping a predecessor's design as
specification); HISTORICAL_CONTROL 79; RETIRE 25. Skeptics changed 55 categories, all but one downward -- the code that
looked most reusable usually failed open where a probe could reach it (for example: a chance-floor helper that returns
the most permissive floor when counts are missing; a store-identity guard that passes on any database when registry
fields are null; a receipt helper that reports a clean tree when git fails; a manifest hasher that lets distinct short
binaries collide; a ledger whose clients write their own verdicts).

What carries forward: as running engines, nothing; as code, eight small primitives (a receipt schema, a liveness
derivation, a keyed-stream pattern, eps-lexicase, exact NK/BitString landscapes, exact-Bayes hidden-state processes, a
qualification seed, an interchange decision rule); as designs to rebuild, the write-provenance tracer, the interchange
lens, the provenance shadow, the causal-reach twin, the capacity gauntlet, the leak audit, the null ladder, the
sealed-split broker and the job runner; as historical controls, 79 known-answer fixtures, planted positives and
negatives, canaries and anti-calibration items. The four load-bearing Reality-layer pieces (signed verdict job,
dependency demotion, row-class filter, token harvester) and the four search estimators (rediscovery-from-distance,
random-sampling needle rate, concentration floor, pressure certificate) exist nowhere and are new. No existing seat's
code becomes a dependency of the Phase 3 core. Twenty-four defects found during salvage are listed for routing
(SALVAGE_MATRIX.md s5; salvage/NEW_DEFECTS.md); 57 components named by skeptics were not evaluated (UNKNOWN).

## 18. Resource model

Inference is used only at declared epistemic forks: code authoring inside budgeted work items, world-grammar proposals,
preregistration drafting (linted by code), cross-family review of frozen designs, interpretation of minimal cores after
the follow-up battery, prior-art search with measured recall, and the capped LLM operator in E8. Everything else --
execution, scheduling, rulers, triage, follow-up allocation, status, reports -- runs without models. The year-one
inference cost is dominated by the build, not by operation; it is budgeted per work item with a 1.5x stop rule and
measured by harvesting session logs (INF-02, INF-06).

    90-day envelope (order of magnitude; replaced by measurements within two weeks)
    build tokens processed     60-200M (>= 85% cache reads); build output tokens 3-8M
    operate tokens             < 5M (no LLM variation before month 4)
    CPU                        2-10k core-hours
    GPU                        0-100 GPU-hours (only if a transformer reference is preregistered)
    energy                     ~50-250 kWh (nominal watts x wall time)
    operator attention         <= 90 minutes per week

Dominant cost by engine: E0-E2 build inference; E3-E6 CPU; E7 build inference for the second substrate; E8 inference
tokens (capped); E9 CPU; E10 build inference (external author). Measurement: token ledger joined to commits by session
trailer; receipts with CPU-seconds, GPU-seconds and nominal energy; operator minutes from prompt timestamps; useful yield
as the vector in s19, never a scalar.

## 19. Scientific-yield model

The charter's progression is kept in substance and restructured as the L0-L6 ladder (REQUIREMENTS.md s7), because
replication and baseline survival are not separable stages, "mechanistic compression" is a property of a carrier
rather than a stage, and nulls need their own ladder. Yield per quarter is a vector: claims at each level (promotions
minus mechanical demotions, with time to demotion); typed nulls and null certificates issued; qualified instruments;
certified world families; canary catch rate per failure class and time to catch; retractions caught internally versus
externally; and cost per item. A quarter with two qualified rulers, three certified families, one null certificate and
no L2 claim is productive; a quarter with forty L1 anomalies and no L2 is not. Commits, runs, flags and agent activity
are not yield.

## 20. Publication and externalisation model

Externalised artifacts are limited to (OUT-01): claims at L3 or above with cross-family re-derivation; qualified
instruments with their dossiers; certified world suites with certificates and baseline ladders (the most likely
first external artifact, useful whether or not any organism succeeds); and interpretable negative results carrying
null certificates. Each ships as a one-command reproduction package. Nothing below L3 is presented externally as a
finding. Note the doctrine tension: the tracked doctrine forbids publication framing (critical_memories HARD-1), while
this charter asks for externally inspectable outputs including preprints and negative-result reports. This package
treats the charter as the newer direct instruction for this deliverable and words outputs as inspectable work products;
the operator should rule (OPEN_QUESTIONS Q-OP1).

## 21. First 90-day MVP

**What gets built (S1, days 0-30, the vertical slice).** R0 minimal: deterministic runner with keyed streams,
snapshot/restore and receipts (CPU, energy, tokens); append-only hash-chained ledger with segment files; signed verdict
batch job with row-class filter; deterministic weekly digest; the build token ledger. DGM kernel v0 with the
developmental instructions X1 needs, plus a slow reference interpreter, differentially tested. Lattice switches for
lifetime modification and internal ticks. World family F1 (per-lifetime mapping draw with exact adaptive gap and payback
ratio; variability x reliability x lifetime grid). One qualified ruler: the censoring-aware acquisition curve, qualified
on authored and procedurally generated planted learners, innate genomes and random genomes. Baseline subset: constant,
best fixed policy, best detect-and-dispatch genome, random genome. One CPU reference learner (evolved plastic recurrent
network). Evolutionary engine v0 with declared neutral-accepting acceptance. Counterfeit fixtures for every SLICE
requirement.

**First organisms.** DGM genomes with lifetime modification on and off; the plastic recurrent reference; planted
learners and innate genomes (compiled), and procedurally generated plants found by search.

**First worlds.** F1 (slice); then F2 static needle, F3 hidden-state process pair with exact Bayes, F4 keyed binding,
F7 exact games with a Nim-like decoy (S2); F5 procedure reuse and F6 compositional grammar (S3).

**First pressures.** P0 versus P1 across change rate and lifetime (X1a); the ruggedness axis (X1b); P2 sequences for
X5.

**First developmental curricula.** None in S1. In S3, F5/F6 curricula admitted only with verified prerequisite structure
(WLD-08), run against direct, shuffled, retention-frozen and irrelevant-twin controls.

**First rulers.** Acquisition curve (S1); retention, matched ablation, interchange, deliberation signature,
acquisition-matched finite-state learners, minimisation (S2); write-order tracer qualification only if X8 says E6 is
affordable.

**Qualification experiments.** X1a (S1); X1b, X2, X3, X4, X6, X8, X9 (S2); X5, X10 (S3).

**Reused.** Almost nothing (SALVAGE_MATRIX.md s4): the toolbox receipt schema after fixes, the keyed-stream pattern behind a new key schema, productive_liveness for derived status, SFE's NK/BitString landscapes as estimator fixtures, the exact-Bayes processes for F3 (S2), and the historical-control corpus as qualification fixtures (packaged in S2). The DGM, R0's verdict job and ledger, F1 and the rulers are new code.

**Expected compute.** X1a about 1,200 runs at ~0.3 core-hours (~400 core-hours); whole MVP 2-10k core-hours.

**Inference boundaries.** Code authoring in budgeted work items (<= 3 concurrent sessions); preregistration drafting;
cross-family review of the X1a and X5 preregistrations if an I3 reviewer is available; no LLM variation.

**Milestones and kill gates.**

    day 30   X1a preregistered and run; L1 verdict row signed by the verdict job OR a typed diagnosis naming the
             failed layer; X9 build receipt; counterfeit suite for SLICE requirements passing
    day 60   X1a/X1b verdicts; X2 result; ruler dossiers (authored vs generated sensitivity); capacity and
             developability fixtures in CI; X6 reachability curves; X8 sizing; probe kernel commissioned;
             KILL/CONTINUE gate (ENGINE_PORTFOLIO.md): replace the substrate, diagnose the stack, reframe depth,
             or continue
    day 90   X5 result typed (positive, typed null, or null certificate); X10 substrate variance; certified world
             suite v0 (F1-F7) with certificates and baseline ladders; canary stream live; first L2 attempt (a
             one-shot confirmatory replication of X1a on a never-read sealed split); decision memo on E4-E6 order

The MVP is designed to maximise information about the architecture -- whether the stack can say YES to a known
positive, whether depth certificates predict anything, whether rulers detect unfamiliar planted mechanisms, whether the
substrate's search space is reachable -- not to produce impressive results.

## 22. Six-to-twelve-month programme

Months 4-6: E4 campaigns on F5/F6/F10 under P2 with developability proofs and concentration floors; E5 build of F8 with
the own-reliability dissociation; E8 pilot (isolated LLM operator, <= 10M tokens, matched model-free arm); second
certificate tool from an independent author; REP-02 independent kernel reimplementation started as soon as any L2
candidate appears. Months 6-9: E5 campaigns; E6 if X8 shows it affordable and the write-order tracer qualifies on
planted organisms; first L3 attempts (only with REP-02 done); externalisation of the certified world suite and the
first null certificates. Months 9-12: E7 if a trigger has fired (second substrate authored at I2 or better, preferably
continuous or asynchronous); E9 yoked-ecology arm if the slice and E4 are stable; first L4 attempt with cross-family
re-derivation. A realistic year-one ceiling is L4 in one substrate; L5 needs the second substrate.

## 23. Falsifiers

FALSIFIERS.md lists them by component. The most important: the stack cannot reproduce X1a in any substrate with
qualified rulers (stop science, diagnose the stack); after 6-12 months, with developability proofs, concentration
floors and certified curricula, structural development never beats retention-frozen and value-only arms (the
developmental framing is wrong or mis-scaled at this size; issue null certificates); every validated carrier is
FAMILIAR at small k and the model-free arm finds nothing the LLM arm does not (the epistemic-escape premise fails here);
the cost of a single L2 claim exceeds the year's envelope (the standard is too expensive for the resources); a
cross-family re-derivation of X0 or the salvage matrix disagrees on more than a third of items (this package's reading is
family-bound).

## 24. Explicit answers Q1-Q10

**Q1 -- Scientific legitimacy.** Current Prometheus research is premature science: a real scientific process applied to
mostly prototype apparatus. Evidence: 2 of 130 profiled nulls had S, W and R demonstrated; 30 of 146 rulers showed
detectability and about one measures an organism property; W (world demand) was demonstrated for 37 of 353 results;
independent replication for 20; mechanism by intervention for 24; 139 corrections against 357 results -- most made by the
claiming seat within hours, which is what rules out cosplay. What Phase 3 must change: qualify instruments before
interpreting them (MEA-01, MEA-16); certify worlds with bounds (WLD-01/02/17); prove capacity and developability
constructively (ORG-14, DEV-13); make authority mechanical (PRV-02, SCI-02, SCI-16); compute independence (REP-06);
account for inference and attention (INF-02/06, HUM-04); and run a vertical slice to a known positive before breadth
(CMP-07).

**Q2 -- Cognitive sufficiency.** A negative about reasoning becomes interpretable when a null certificate passes: a
constructive organism in the substrate exhibits the capability (S); a genome in the searched language develops it within
the lifetime (D); the world demands it, with admission baselines failing by more than the ruler's MDE (W); the pressure
certificate shows selection can see it (P); the ruler detects the SESOI with power 0.8, including on procedurally
generated plants (R); a rediscovery-from-distance estimate shows at least three expected hits at the budget used; the
lifetime exceeds three times the developable genome's acquisition time; the curriculum has verified prerequisite
structure; budget curves have flattened; and the identical pipeline produced a positive of the same type at an easier
point of a declared difficulty axis (the bracket). The answer to "how capable must the organism, world and development
be" is therefore relative, not absolute: capable enough to produce the phenomenon at the easier bracket point and
constructively capable at the target point. Without that, NO EMERGENCE is a statement about the apparatus.

**Q3 -- Developmental adequacy.** Required machinery: cross-episode writable state; structural plasticity; invocable
stored structure; modifiable modification machinery; multiple timescales; metabolic pressure with ramps; idle periods.
What does the compression: selection on developmental programs under reuse pressure (P2) and metabolic cost, acting
through the organism's own developmental rules, so that building one carrier that serves several families is cheaper
than building several. What produces abstractions: worlds whose families share latent structure under surface variation
(certified d_comp, surface-varied recurrence) and lifetimes long enough to meet several families. How structures become
reusable objects of subsequent cognition: when they are invocable from several contexts and addressable and rewritable by
other developmental rules, so that they can be composed, specialised and modified -- which is what the developmental
instruction set provides. These are hypotheses; E4 tests them against retention-frozen and value-only controls with
developability proofs.

**Q4 -- Evolution versus development.** Evolution should specify developmental rules, physics settings (timescales,
decay constants, costs of its own structure), a small seed structure and biases about what to attend to and how to
learn -- not solutions, except where the adaptive gap is near zero or the payback ratio is low (P0), where a genome
containing the solution is correct. Development should construct task-specific structure and reusable carriers within the
lifetime. The world should teach only through statistics: within-lifetime variability (P1), shared latent structure
across a sequence of environments (P2), shifting learning biases (P3/P3b), costs and idle periods. Shaping rewards on
internal states are forbidden (DEV-11).

**Q5 -- Recursive sagacity.** Strongest operational definition: acceleration of acquisition on sealed held-out families,
beyond matched twins, carried by developed structure of write-order three or more -- shown by reversion (restoring order
>= 3 structure to birth removes the acceleration while order <= 2 is kept), by donor-depth dose-response in both the host's
acquisition cost and its later learning-to-learn slope, by a null effect from irrelevant-experience donors, and with no
outer optimiser in the lifetime. The observation beyond ordinary learning-to-learn is the reversion result: a meta-learned
learner or a fixed rule with a growing library shows savings, but has no order >= 3 structure whose reversion removes them.

**Q6 -- Epistemic escape.** Plausibly yes for components, not for invention-and-recognition. LLM-proposed architectures and
LLM familiarity judgements stay near the corpus; search-generated variation in a substrate with procedurally generated
primitive bases, selected by deterministic worlds and qualified rulers, can produce structure no model proposed. We would
know through E8 (does an isolated LLM operator add validated findings per unit cost, and are its survivors more familiar?),
through grammar gravity (does the mechanism stay short under a random basis?), through the executable familiarity
reference (distance to the nearest reference mechanism reproducing behaviour and intervention signature), and through
reproduction in the model-free arm. Unfamiliar mechanisms are protected from being discarded as noise by code-level
authority (interpretation cannot demote), mechanical follow-up allocation that serves unproposed candidates first,
minimal cores (so opacity is not rewarded), and the rule that unclassifiability raises priority after the gates and is
never evidence.

**Q7 -- Single engine versus portfolio.** An observatory around one primary substrate, with engines as questions run on
it, a probe kernel for substrate variance, and a second substrate on triggers. Not one integrated engine (attribution
dies in a coupled loop); not a family of separately authored engines (budget split, same-family breadth, no comparability).
The X0 result (0 of 210 historical failures needed a second substrate as their cheapest repair) and the binding-constraint
analysis support concentrating on depth first.

**Q8 -- Existing machinery.** As running engines, none: zero of roughly twenty historical engine-level systems carries
forward as an engine. As code, about 5% of evaluated components (8 of 143), all small primitives -- well under 1% of the
repository by lines. As designs to rebuild, about a fifth (23 components whose design becomes the specification of a new
build). As historical controls, more than half (79): the failures of Phases 1 and 2 become the qualification fixtures of
Phase 3. Retired, about a sixth. Conceptually, then, roughly a quarter of the scientific machinery survives (code plus
designs) and essentially none survives as running machinery. The most valuable surviving asset is not code: it is the
recovered failure taxonomy, encoded as 70 enforced requirements with counterfeit fixtures. Nothing was preserved for
sentiment: every reuse claim was attacked by a skeptic, and 55 were downgraded.

**Q9 -- First experiments.** The smallest experiments that discriminate between Phase 3 architectures: X0 (done: depth-first
confirmed); X1a (can the stack reproduce a known developmental positive end to end -- discriminates "instrument works" from
"instrument broken"); X2 (do depth certificates predict which baselines fail -- discriminates world-forge-first from
search-first); X3 (are core rulers sensitive on procedurally generated plants -- discriminates usable rulers from
FAMILIAR-ONLY); X4 and X6 (developability proofs and needle inflation in the full lattice -- discriminates the primary
substrate from a minimal variant or a second substrate); X8 (power for recursive sagacity -- discriminates whether E6 is
affordable at all); X10 (probe-kernel variance -- discriminates substrate-local from pressure-determined results); X5
(development discriminator -- discriminates the developmental thesis from "more compute"). X7 (LLM operator vs model-free
arm) discriminates LLM-in-the-loop generation from structural search, after month 4.

**Q10 -- Failure.** After 6-12 months, any of: the stack cannot reproduce X1a in any substrate with qualified rulers; with
developability proofs, concentration floors and certified curricula, structural development never beats retention-frozen
and value-only controls on savings or transfer in any certified family; every validated carrier is FAMILIAR at small k and
the model-free arm finds nothing the LLM arm does not; a single L2 claim costs more than the year's envelope; or a
cross-family re-derivation overturns the X0 or salvage reading on more than a third of items. Any of these would say the
present thesis is wrong or badly framed at this scale.

## 25. Highest-value unresolved questions

OPEN_QUESTIONS.md lists them with owners and the experiment that resolves each. The five that matter most: Is cognitive
depth, as certified, predictive (X2)? Is the full-lattice primary substrate searchable at CPU scale (X6)? Can
developability proofs for keyed binding and procedure reuse be built cheaply (X4, X9)? Can an executable familiarity
reference reach UNFAMILIAR without rewarding noise (AGR-12)? Can an I3 party (another model family or a human) be engaged
for re-derivation, the probe kernel and the second certificate tool (without it, L4 and externalisation stay blocked)?

----------------------------------------------------------------------------------------------------------------------

## Final question

If Prometheus were being started today with everything now learned and none of its engines written, I would build first a
vertical slice of the instrument rather than any engine: a deterministic runner whose only writer of verdicts is a signed
batch job; one small, exactly solvable world family whose adaptive gap and payback ratio are computed rather than assumed;
one ruler -- a censoring-aware acquisition curve -- qualified on planted learners, planted innate genomes and procedurally
generated organisms that its author never inspected; and a tiny developmental substrate with a switch that turns lifetime
modification on and off. I would use it to reproduce one result whose answer is already known: that lifetime learning
evolves when environments vary within a lifetime and does not when they are static. The reason is the whole fossil
record: Prometheus's failures were not failed hypotheses but uninterpretable outputs of apparatus that had never been
shown able to say YES, and the desk audit found that qualifying the ruler alone would have rescued more than half of
them. An instrument that has reproduced a known positive end to end, with its matched negative, is the cheapest thing that
can make every later NO mean something -- and it is the thing Prometheus never had.
