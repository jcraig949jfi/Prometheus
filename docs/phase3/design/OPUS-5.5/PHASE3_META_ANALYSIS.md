# Prometheus Phase 3 -- independent meta-analysis, requirements and architecture

Architect: Epimetheus, IDENTITY OPUS-5.5 (runtime model claude-opus-5-5). Date: 2026-10-01.
Charter: roles/Epimetheus/prompts/2026-10-01_charter/ (verbatim, MANIFEST). Independence: no other architect's design
files were read (one exposure of file names on a git merge is recorded in the seat journal).

Package: this file; REQUIREMENTS.md (+ requirements.jsonl, tools/); RSE_ARCHITECTURE.md; ENGINE_PORTFOLIO.md;
SALVAGE_MATRIX.md (+ salvage.jsonl, tools/salvage_adjudicate.py); OPEN_QUESTIONS.md; ASSUMPTIONS.md; FALSIFIERS.md;
evidence/ (twelve reader digests, 353 historical evidence profiles, 192 verification verdicts); experiments/ (X0
preregistration, codes, result); salvage/ (component digests, raw skeptic records).

Order of work, checkable in git: charter verbatim (af4e0a3f6) -> evidence intake and X0 preregistration (d6f555fd7) ->
requirements v2, architecture and portfolio FROZEN before any salvage reading (77d3c99c3) -> salvage matrix and this
analysis (0933c72e8) -> final review (workflow wf_335d0a49-a24: charter compliance, internal consistency, hostile
scientific read) and the corrections it forced, made as explicit post-freeze amendments (REQUIREMENTS.md s10,
RSE_ARCHITECTURE.md s10; none motivated by salvage findings).

Method, briefly. The four forensic packages were read in full by the architect; twelve parallel readers then read every
seat dossier, the indexes, the ruler inventory, the Ixion maps, the Atlas materials and external prior art, and an
adversarial verifier per reader checked the readers' load-bearing claims against the underlying artifacts (100 sampled
load-bearing claims: 82 confirmed, 18 partial, 0 refuted; the same verifiers logged 92 further reader errors, listed in
evidence/verification.jsonl and not yet propagated into historical_profiles.jsonl; the idx and ext digests were not
verified). A first-principles requirements draft was attacked by a five-lens
critic panel and by five advocates of competing architectures with a judge; the judge's decisive experiment (X0) was
preregistered and run (the final review later found it non-discriminating for substrate count; X0_RESULT.md
addendum). Every agent in this pipeline is Claude-family; the same independence discount the crawlers
applied to themselves applies here (s13, s25).

----------------------------------------------------------------------------------------------------------------------

## 1. Executive thesis

1. **Prometheus built a scientific process before it built scientific instruments.** Preregistration, controls,
   provenance and unusually hard self-correction are real; the apparatus they wrapped mostly could not reveal the
   phenomena under test. Of the 130 profiled results the readers reclassified as an insufficiency, a true negative or a
   hypothesis failure (a population largely defined by a missing axis), 2 had substrate capacity, world demand and
   ruler validity all scored Y; of the 20 true negatives and hypothesis failures, none did. Of 146 distinct instruments,
   30 had demonstrated detectability, and about one measured an organism property. One of 171 indexed engines combined an adapting organism, a world with latent state and a ruler
   of demonstrated detectability -- and its "organisms" were hand-chosen estimators.

2. **The binding constraints were ruler validity, provenance and implementation, and world demand; search and
   same-substrate capacity tied at 5%.** A preregistered desk audit (X0) of 210 coded apparatus nulls and false
   positives found the cheapest repair was a ruler-side repair (qualification, planted control, baseline ladder or leak
   audit) for 54% (50-54% across sensitivity variants that drop the external-literature, Atlas and reader-error-flagged rows), provenance or implementation for 14%, world demand for 9%, statistics
   for 8%, search for 5%, a
   same-substrate capacity proof for 5% and independence for 2%. X0 coded a second substrate only when nothing else
   could settle an item and excluded the 20 surviving anomalies, so its 0% cannot reject an early portfolio: it supports
   instrument priority, not the substrate count (an X0b with a reachable portfolio branch is preregistered before day
   60).

3. **Phase 3 should therefore be an instrumented developmental observatory around one deeply instrumented primary
   substrate**, not one integrated "Recursive Sagacity Engine" and not a portfolio of separately authored engines. A
   shared Reality layer with a signed verdict job, a world forge that certifies cognitive depth with bounds, and a
   measurement bench whose rulers are qualified on authored and procedurally generated planted organisms host one
   primary developmental substrate whose affordances are switches on one code path, one familiar reference learner per
   world family, a tiny probe kernel by another model family or a human (independence class I3), and a second full
   substrate commissioned on measured triggers. Scientific questions (engines E3-E8) are run on this observatory in a staged sequence.

4. **The object of study is what an organism can become, measured as a distribution of developmental trajectories,
   not what it does.** "Transferable sagacity" is operationalised as censoring-aware reduction in acquisition cost on
   structurally novel families against capacity-matched controls; "recursive sagacity" as acceleration carried by
   developed structure of write-order three or more (order assigned by the structures that EXECUTE each write, not by
   those consulted), shown by reversion, donor-depth and executor-versus-content transplants -- which a fixed learning
   rule with a growing library must be shown not to fake (the DEV-14 deep-library plant).

5. **The first quarter is mostly instrument qualification.** The first scientific act is to reproduce a developmental
   result whose answer is known (lifetime learning evolves when environments vary within lifetimes and not when they
   are static) end to end through the ledger and verdict job. Nothing broad is built before that vertical slice
   passes; open-ended search begins only after it.

6. **Interpretable negatives are first-class.** A phenomenon-level null is issued only as a null certificate, bracketed
   by a positive of the same type at the adjacent easier point of a declared difficulty axis or by a planted solution
   recovered from distance by the identical pipeline, and stated as not-detected-above an MDE anchored to a
   constructive organism. Without a bracket the null is UNBRACKETED. Most historical nulls would be typed as nulls about
   the apparatus.

## 2. What Prometheus actually built

Quantities from the four indexes and the twelve digests (evidence/idx.md and others; counts are crawler- or
reader-derived and carry their tags):

    roles/ directories                       ~72 at crawl time (idx.md lists 59 crawled seats, 6 Phase-3 seats,
                                             base-role and 7 legacy, which sum to 73: an unresolved off-by-one
                                             in the source; charter: ~59)
    commits indexed                          11,779 (7,224 in September 2026)
    Python lines                             ~3.19M; ~39% LLM-forged reasoning-tool scrap; ~27% math-catalogue and
                                             falsification pipelines; ~20% organism/world engines
    engine/lens records                      171 raw (19 path-sharing pairs across the 247 crawler and Ixion
                                             records, of which 4 exact and ~6 perspective duplicates);
                                             instruments outnumber simulations 58:34; 26% self-describe as
                                             toy/prototype/unrun
    engines with any adapting organism       44/171 (29 population-only, 12 lifetime-only, 3 both)
    engines with latent state to infer       12/171
    adapting x latent x demonstrated ruler   1/171
    highest realised demand                  by an evolved organism: a one-cue latch (D3); 15 engines designed
                                             for >= D5, 1 realised D5 (hand-chosen estimators); D4 in 6 (fixed
                                             solutions)
    rulers (distinct)                        146: detectability 30 YES, 53 PARTIAL, 57 NO, 5 UNKNOWN, 1 N/A;
                                             cross-substrate tested in 2 of 152 inventory rows (1 failed)
    later-correction rows                    139 against 357 reported-result rows (0.39) in the three science
                                             packages (latency and corrector not measured)

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
   estimator, a coprime-to-30 one-liner, a constant answer matching or beating 120 of 122 full-coverage tools, a
   zero-parameter definition rule
   tying mined laws. Response: the automatic baseline ladder with chance floors (MEA-03).
4. **Nulls were about the apparatus.** Worlds that needed at most one bit, organisms that could not express the
   question, plants that existed in the searched space and were never found, greedy walks that could not accept a
   neutral step, lifetimes shorter than learning time. Response: typed nulls, null certificates, bracketing,
   developability proofs, reachability estimators, pressure certificates (SCI-03/08/13/14, DEV-13, PRS-03/12).
5. **Independence was a label.** One model family authored, executed, scored and audited; "N seats agree" meant one
   substrate agreeing with itself; councils sent one prompt to four vendors. Response: computed independence classes
   (REP-06); an I3 audit of the verdict job and first ruler with >= 20 sealed counterfeits before day 60 (REP-08); I3
   re-execution from raw receipts and source at L4 (REP-04); sealed procedurally generated plants (MEA-02).
6. **Coordination consumed the inference.** 86 model-written heartbeats in 25 hours, 432 state-file commits in four
   days, seven control orders (16,858 words) in 40 hours, the operator as the relay between seats and models.
   Response: derived status (INF-03), inference only at declared forks with token accounting (INF-01/02/06), bounded
   operator attention (HUM-01/04), a vertical slice before breadth (CMP-07).

## 4. Scientific maturity assessment

Prometheus is **premature science**: a genuinely scientific process applied, mostly, to apparatus that was not yet a
scientific instrument. It is not research cosplay. Two behaviours rule that out: it invented and adopted the right
norms (reachability-first, absence-needs-a-positive, freeze-precedes, verdict names a shortcut cannot pass), and its best
late instruments can fail both ways. It also corrected itself often: 139 later-correction rows stand against 357
reported-result rows (0.39) in the three science packages, though who corrected and how fast were not measured, and
some corrections took months or were never propagated. But serious process did not create serious science. The
evidence-profile axes over 353 profiled results show it plainly (NA = not applicable, counted separately):

    axis   Y     P     N     U     NA    reading
    Q      249   48    50    4     2     questions were usually falsifiable
    S      145   48    33    102   25    substrate capacity often unshown
    W      37    85    107   103   21    world demand rarely demonstrated -- the weakest axis
    R      62    159   121   11    0     ruler validity mostly partial
    B      120   108   78    36    11    baselines improving, often post-data
    Rep    20    112   202   13    6     independent replication rare (replay is not replication)
    M      24    69    196   44    20    mechanism by intervention rare

The defensible external description: an unusually extensive independent experimental programme with increasingly
sophisticated controls, prototype-grade instruments, almost no world-demand certification, and no externally
validated scientific claims about cognitive capacities.

## 5. Why historical results are insufficient

Not because they are false -- most were never in a position to be true or false about the capacities in question. The record's worlds
demanded at most small finite-state control; its organisms often could not act, learn, or change their own structure;
its rulers were seldom qualified; its searches were budget-capped below known needle sizes; its replications were
mostly replays; its independence was nominal. The few positives with recorded weakenings (a delay-invariant reader
that may be a start-anchored latch; super-additive propagation that is a relay; a fused sensor below its bar;
internalisation in 8 of 144 runs) are worth keeping as anomalies to re-test under qualified instruments, not as
findings. The 17 profiled true negatives (four rows first classed as true negatives were reclassified from their own
text; evidence/historical_profiles.jsonl 'correction' field) are mostly about specific instruments or designs (for
example AE-1, "the lattice is ~92% frozen by ~2,500 ticks"; KOI-2, a size-normalised statistic rejected by a
within-size permutation), which is valuable as negative knowledge about apparatus.

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

Compression is not sagacity by itself. The charter's comparison becomes four planted organisms that the transferable-
sagacity ruler must rank before "compression" is used about any result (MEA-19): 1,000 stored solutions save only on
canonicalised seen instances (TS = 0 on structurally novel families); 100 recurring patterns save environment
transitions spent identifying latent state, but not policy feedback; 20 strategies save policy acquisition within
developed families, but not on two-sided-certified novel families; 5 transferable principles save on certified novel
families. Only the last is sagacity in this package's sense, measured as bits of task-specific feedback the organism no
longer needs. The nine candidate measurements are assessed as follows:

    candidate measurement                     adopted as                                         requirement
    sample efficiency over developmental age  TS(o_t; T_new) on a declared age grid              TRF-01, DEV-04
    reduction in future learning cost         transferable sagacity TS                           TRF-01
    cross-domain reuse                        specificity across >= 3 distinct families          L4r (SCI-02)
    minimal description length                abstraction criterion 3, in two languages          REQUIREMENTS s3
    structural reuse                          shared ablation; recurrence-vs-reuse assay         MEA-07
    retained competence                       retention after task removal                       DEV-03
    intervention sensitivity                  graded dose                                        CAU-03
    transfer after representation scrambling  scrambling transfer                                TRF-03
    new-task adaptation rate                  within-episode curve of realised competence R      REQUIREMENTS s3

Five quantities are kept apart: latent cognitive capacity = substrate expressibility E(S, X, W) (constructive proof;
what the substrate could eventually support); developmental capacity DC(g) (a reaction norm over budgets and curricula,
with crossing evidence); realised competence R(o_t, T) (episode-reset evaluation); transferable sagacity TS; and
recursive sagacity (executor order >= 3) (REQUIREMENTS.md s3).

How developmental stages create new reachable stages (reachability expansion, DEV-16): a family T* that is censored
(not acquired within the lifetime) in at least a fraction q of naive runs becomes acquirable after T_n is acquired, and
reverting the carrier built for T_n at the retention boundary makes T* censored again. The curve of the number of
families acquirable within budget B over developmental age is reported; it is the organism-side counterpart of
curriculum prerequisite structure (WLD-08).

Critical thought (charter s7) is measured by signatures, never labels (E5; REQUIREMENTS.md s3). Uncertainty:
decodability of posterior entropy beyond an observation-history decoder. Competing hypotheses: on decisions with
d_hyp >= 2, interchange finds at least two carriers each tracking one hypothesis's likelihood. Evidence seeking: a
costly observation is taken when certified value of information exceeds its cost, and ablation removes this.
Contradiction detection: a carrier changes state on surprise beyond a latency-matched reactive baseline. Revision:
carrier update after misleading first evidence. Calibration: own-error decoding plus the own-reliability dissociation
(WLD-16). Compression into reusable structure: the same carrier meets L4r specificity across at least three epistemic
families and its minimised description length falls with age. Learning when to invoke: the carrier's activation carries
increasing information about certified per-decision d_hyp or d_voi over age, and the gating structure is absent at
birth (DEV-05). Evidence of metacognition without hard-coding is exactly the conjunction of the metacognition clauses
with no confidence output, slot or shaping reward in the physics (ORG-16, DEV-11).

## 7. Organism requirements

Affordances, not modules (REQUIREMENTS.md s6). Required: persistent writable state within and across episodes;
selectable access to stored state as a capacity (not a mandated primitive); conditional control; structural
create/delete/copy/modify during the lifetime; metered internal steps; in the primary substrate, modifiable
modification machinery as a lattice switch. Required instrument affordances: keyed determinism, snapshot/restore,
stable ids, a material provenance shadow from day one, intervention hooks for every carrier class in a closure audit.
Physics options: multiple timescales, invocable stored structure, neutral genotype-phenotype redundancy. Never built
in: working-memory buffers, attention modules, hypothesis slots, confidence outputs, planners, world-model modules,
labelled abstraction operators. Allowed to emerge and never required by a ruler: modularity, consolidation, hierarchy,
binding, internal simulation, uncertainty representation, metacognitive control, communication, compositionality,
resource allocation and credit assignment (the physics supplies no global error or gradient signal; DEV-15).
Recurrence is a minimal affordance (delayed edges allow cycles); temporary versus long-lived structure is a physics
option (evolvable decay constants). Capacity proofs may be
obtained by any recorded procedure (compilation, synthesis, privileged search), so the substrate need not be
human-programmable. Each affordance is tested by a lattice contrast on one code path.

## 8. Developmental physics

Development is separated from evolution as a declared timescale with independent switches (DEV-01). What evolution
specifies is the developmental program and physics settings; what development constructs is task-specific and
reusable structure; what the world teaches is carried only by the statistics of the curriculum. "Constructing
cognition" is distinguished from optimising parameters by experience-specificity, carriage by developed structure, and
a construction advantage over the value-only learner class and budget frozen in the experiment's preregistration, on a
pre-grown structure of the final size (DEV-05). Architectural reorganisation is distinguished from local structural
development as a change in the macro-scale partition (modules or strongly connected components under the CAU-08
operators) that coincides with a capability change (DEV-15). Credit assignment is organism-constructed: any carrier that
routes reward to developmental rules must be evolved or developed and is localised by interchange on eligibility-like
state (DEV-15).
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
only regime that predicts recursion); a genome-budget axis G (genome capacity swept relative to the description
length of the minimal solution, predicting a developmental program when the solution exceeds the budget); catastrophic
shift as an axis distinct from the change rate; P4 ecology, competition and cooperation, deferred to E9 because they
confound single-organism developmental attribution until the instruments are qualified. A level is in force only when a
pressure certificate shows the capable
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
full measurement closure recomputed at verdict time (MEA-01). The X0 result -- a ruler-side repair was the cheapest
way to make 54% of the coded historical failures interpretable (50-54% across sensitivity variants that drop the external-literature, Atlas and reader-error-flagged rows) -- is the strongest
argument in this package for building this layer first. The rulers that
must exist before discovery claims are listed in RSE_ARCHITECTURE.md s5; each operational definition is itself a
qualified predicate whose planted battery includes the cheapest organisms satisfying each clause without the property
(MEA-16).

## 12. Signal versus hallucination architecture

Each historical failure mode is made difficult or impossible by a named, enforced mechanism (the full map is generated
in REQUIREMENTS.md; the checker fails if any of the 70 classes loses a covering BLOCK- or RULE-enforced requirement
that carries a counterfeit fixture):

    failure class (examples)                       mechanism that blocks it
    leakage / answer in the measurement             all-channel differential leak audit; physics never reads rulers;
                                                    ruler input manifests; label-permutation invariance
    baseline omission                               automatic baseline ladder; missing rung blocks the verdict
    tautological / impossible-to-fail controls      controls wired to abort; fired-once on sealed cheats; mutation tests
    ruler saturation, uncalibrated detectors        qualification dossiers; FAMILIAR-ONLY class; dilution invariance
    shared-code "independence"                      computed independence classes from access logs and import graphs
    seeded phenomena read as endogenous             material provenance shadow; fixture/plant ancestry tags;
                                                    operator-model-free arm with MODEL-SEEDED typing
    selection on holdouts                           encrypted sealed splits decrypted only in evaluation;
                                                    consumable confirmatory reads
    cheap proxy strategies                          definition-as-rule rung; latch and payload readers; MEA-16 batteries
    unreachable search regions                      reachability estimator; concentration floor; bracketed nulls
    post-hoc interpretation                         executable preregistration as an earlier commit; runner refusal
    forking preregistrations                        ledger-derived multiplicity
    infrastructure hubs read as primitives          L4r specificity, double dissociation and interchange
    naming-layer hallucination                      vocabulary lock: defined terms only when the predicate is TRUE
    promotion without demotion                      dependency-driven mechanical demotion; challenge suspension
    a gate that silently stops working              standing canaries per failure class with a dead-man switch

The single structural principle: the component that generates a candidate never writes its verdict, and every verdict
can be recomputed from committed, computed rows by a signed batch job.

## 13. LLM epistemic escape

Can a search system mediated by historical human priors discover unfamiliar cognitive machinery? Possibly, but not by
an LLM inventing and recognising it. The design separates three roles in code: Generation (mutation, recombination,
procedurally generated primitive bases, and -- only in one budgeted campaign -- an information-isolated LLM operator)
proposes; Reality (worlds, development, interventions, qualified rulers, the verdict job) decides survival;
Interpretation (models, humans, prior-art search) proposes experiments and descriptions and can never delete or demote.
The prior enters through more than per-edit proposals: through authored primitive sets, mutation kernels, plants and
world admission. Hence the anti-gravity mechanisms: an operator-model-free arm in every campaign family that uses any
model-authored material (claims above L2 reproduce there or are tagged and capped; it removes only the model-operator
channel, since the substrate, basis, worlds and rulers are model-authored in every arm); a reserved share of search
mass (default >= 30%) under procedurally generated primitive bases from the start (AGR-18); grammar gravity (mechanisms
claimed as unfamiliar are re-searched under generated bases; mechanisms short only in the authored basis are
GRAMMAR-BORNE);
procedurally generated plants that ruler authors never inspect; an executable familiarity reference whose UNFAMILIAR
outcome is shown reachable before use; a material-descent gravity meter; mechanical follow-up allocation that serves
first the candidates no model proposed an experiment for; minimal causal cores before any interpretation so that
opacity is not rewarded. Unclassifiability raises priority only after the behavioural and causal gates and is never
evidence. How we would know: E8 measures directly whether the isolated LLM operator increases validated findings per
unit cost and whether its survivors are more familiar than the operator-model-free arm's. AGR-18 differs from the
rejected anti-gravity quota (AGR-03): it allocates search where the authored prior is absent and claims nothing about
the allocation as evidence.

The charter's seven LLM roles, analysed as channels for the prior:

    role                 where Phase 3 uses it           channel for the prior            control                          authority
    architect            DGM design, A0 basis, world     primitive set and affordance     AGR-15/18 generated bases;       proposes; never
                         grammar, this package           choice                           probe kernel at I3 (X10, X10b);  certifies its
                                                                                          second substrate at I2/I3; X11   own design
    mutation generator   E8 only                         prompt as answer channel;        AGR-16 isolation; AGR-14 arm;    Generation only,
                                                         corpus-shaped edits              AGR-04 material-descent meter    token-capped
    coder                all of R0-R3                    fail-open code correlated with   REP-02 reimplementation; MEA-05  no write path to
                                                         the auditor (salvage s5)         mutation tests; REP-08 I3 audit  verdicts
                                                                                          and sealed counterfeits
    hypothesis generator framing, prereg drafting        selection of familiar questions  prereg linter; AGR-13 serves     proposes only
                                                                                          unproposed candidates first
    interpreter          minimal cores after the L1      familiar labels                  SCI-17 vocabulary lock; AGR-02   cannot demote
                         battery
    classifier           none in the verdict path        unfamiliar read as noise         AGR-12 executable reference;     none
                         (MEA-12)                                                         panels as priority signal only
    admission gate       forbidden                       generate -> recognise -> admit   PRV-02/PRV-07 row-class filter;  none
                                                                                          HUM-01

## 14. Recursive sagacity definition

Operational definition (REQUIREMENTS.md s3, DEV-14 as amended): every lifetime write is tagged with its EXECUTOR set
-- the minimal set of instructions or nodes whose execution performed it (ablating a member changes or prevents the
write with operands held fixed); structures consulted only as operands, templates or proposal priors do not propagate
order. Structure written by an order-k executor has order k+1; recursion is order >= 3. A claim requires acceleration
of acquisition on sealed held-out families beyond matched twins (R1), removal of a declared fraction of it, relative to
a size-matched sham reversion, by reverting order >= 3 structure (R2), donor-depth dose-response in both the host's
acquisition cost and its subsequent learning-to-learn slope (R3), no effect from irrelevant-experience donors (R4,
excluding maturation clocks), no outer optimiser in the lifetime (R5), and an executor-versus-content transplant
showing that the donor's executors, not its content, carry the effect (R6). What would demonstrate something beyond
ordinary learning-to-learn: a gradient meta-learned recurrent learner and a fixed rule with a compositional library
both produce savings and even a temporarily accelerating slope, and the DEV-14 battery must classify both as order <= 2
(including a library of composition depth >= 5); a saturation null must tag < 5% of structure in random and P1/P2
genomes as order >= 3, or the substrate is RECURSION_UNTESTABLE. In the DGM, where invoked library code itself executes
developmental instructions, INSEPARABLE MACHINERY-CONTENT is the expected outcome unless R6 separates them. External
test cases: self-referential learners without a separate meta-optimiser (Schmidhuber 1993; Irie, Schlag, Csordas and
Schmidhuber 2022; Kirsch and Schmidhuber 2022). The regime must predict recursion (P3b, with a PRS-14 regime
certificate) for a negative to be phenomenon-level, and the null must be bracketed; in year one the expected outcome is
UNBRACKETED.

## 15. Proposed Phase 3 architecture

RSE_ARCHITECTURE.md: an instrumented developmental observatory around one primary substrate. Six layers (Reality kernel;
world forge; measurement bench; substrates; search and pressure; interpretation at forks). The primary substrate is a
developmental graph machine: nodes are small register machines; developmental instructions (spawn, link, unlink,
rewrite, set-decay, prune) are ordinary instructions, so the rules of development are rewritable state; two genotype
encodings; every affordance a lattice switch on one code path. The design is close to Self-Modifying Cartesian GP,
Gruau's cellular encoding and Avida (RSE_ARCHITECTURE.md s3 states the falsifiable difference: developmental
instructions run during the lifetime under world input, provenance-traced); alternatives are compared by an X11
bake-off. One CPU-trainable familiar reference learner per family; a probe kernel of about 1.5k lines by another model
family or a human (I3); a second full substrate on triggers (a claim at L4r/L4d, needle inflation > 100x, a blind
physics-span check, or the probe kernel's X1 threshold outside the primary's span); replacement of the primary
substrate on X1a, X1c, X6, X4, X11 or X10b (a >= 10x accessibility gap at depth). Staging: S1 vertical slice (days
0-30), S2 qualification with a day-60 kill gate, S3 first discrimination (days 61-90), S4 programme.

Alternatives considered and why they lost (judge scores in RSE_ARCHITECTURE.md s1): one integrated always-running
engine (attribution re-staged inside a coupled loop; the Deep Frontier shape); 10-12 separately authored engines (the
fossil record again: same-family breadth, split budgets, search-limited nulls); LLM program synthesis first (the prompt
is an answer channel; survivors invite mechanism-by-reading); ecology-first soup (copying without competence; no
qualified open-endedness metric); three bespoke substrates from the start (six kernels before any L4 candidate; split
budget; convergence without an instrument).

## 16. Engine portfolio

ENGINE_PORTFOLIO.md details eleven engines with all of the charter's fields, plus why each is needed, the historical
failure motivating it, the alternative considered and the distinguishing experiment. Instrument engines: E0 Reality kernel and verdict
authority; E1 instrument qualification lab; E2 world forge and depth certification. Science engines: E3 when
development pays (pressure transitions; known positive); E4 constructive development and reusable structure; E5
epistemic pressure and own-reliability tracking (the s3 metacognition predicate); E6 recursive plasticity; E7 mechanism transplant and
cross-substrate convergence (trigger-gated); E8 generation source and the gravity meter. Deferred or narrow: E9 yoked
ecology arm; E10 probe-kernel substrate variance. They share one substrate, one forge, one bench and one verdict job, so
their results are comparable and the search budget is not split twelve ways. Engines existing by day 90: E0, E1, E2,
E3, E4 (X5 only) and E10; E5-E9 are not started before month 4.

## 17. Prometheus salvage analysis

SALVAGE_MATRIX.md (written after the freeze; deduplicated after the final review). Seven evaluators read the source
and tests of the candidate components against the frozen requirements (143 evaluation rows, 130 distinct components
once rows evaluated by two groups are merged); an adversarial skeptic attacked every reuse recommendation with probes
run in scratch copies. Skeptic-adjusted result over the 130: KEEP 0; HARDEN 4; EXTRACT 1; REBUILD 26 (4 greenfield, 22
keeping a predecessor's design as specification); HISTORICAL_CONTROL 73; RETIRE 26. Skeptics raised 57 challenges: 53
downgrades and 4 upheld, and no verdict was an upgrade (49 changes move toward less reuse; 4 EXTRACT -> HARDEN changes
mean more fixing before use) -- the code that looked most reusable usually failed open where a probe could reach it (for example: a chance-floor helper that returns
the most permissive floor when counts are missing; a store-identity guard that passes on any database when registry
fields are null; a receipt helper that reports a clean tree when git fails; a manifest hasher that lets distinct short
binaries collide; a ledger whose clients write their own verdicts).

What carries forward: as running engines, nothing; as code, five small primitives (a liveness derivation,
eps-lexicase, exact NK/BitString landscapes, a qualification seed, an interchange decision rule); as designs to
rebuild, the write-provenance tracer, the causal-reach twin, the capacity gauntlet, the leak audit, the sealed-split
broker, the receipt schema, the keyed-stream schema and the job runner; as historical controls, 73 components'
known-answer fixtures, planted positives and negatives, canaries, anti-calibration items and design references
(including the interchange lens, the taint VMs, the null ladder and the exact-Bayes processes, which serve better as
failure corpus or sealed cross-checks than as code). The four load-bearing Reality-layer pieces (signed verdict job,
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
    USD                        computed from the lines above through the versioned price table (NRG-03), not quoted
    memory / storage           < 1 GB per worker; ~1-10 GB of snapshots and receipts per campaign
    operator attention         <= 90 minutes per week

Year one: roughly 200-600M build tokens processed (the 90-day envelope plus the second substrate, the kernel
reimplementation, F5-F10 generators, the write-order tracer and the E8 harness) and tens of thousands of core-hours.
Dominant cost by engine: E0-E2 build inference; E3-E6 CPU (E4 and E6 also carry the only material storage, DEV-03
snapshots of ~3-100 GB per campaign); E7 build inference for the second substrate; E8 inference tokens (capped); E9
CPU; E10 build inference (external author). Memory is not the dominant cost of any engine. Measurement: token ledger
joined to commits by session trailer; receipts with CPU-seconds, GPU-seconds, nominal energy and USD from the versioned
price table, reconciled monthly against invoices; operator minutes from prompt timestamps; useful yield as the vector
in s19, never a scalar.

## 19. Scientific-yield model

The charter's progression is kept in substance and restructured as the L0-L6 ladder (REQUIREMENTS.md s7), because
replication and baseline survival are not separable stages, "mechanistic compression" is a property of a carrier
rather than a stage, and nulls need their own ladder. The mapping:

    charter stage                    ladder
    anomaly                          L1
    replication                      L1 (>= 3 units); L2 (sealed one-shot confirmatory run); L3 (fresh-seed cross-host)
    baseline survival                L1 cheap rungs; L2 full ladder
    adversarial survival             L2: survives a budgeted explanation attempt by an I2 party (SCI-19)
    causal intervention              L3
    transplantation                  L3 (one route); abstraction criterion 4
    cross-world transfer             L4r / L4d (TRF-02, TRF-03)
    cross-substrate transfer         L5
    mechanistic compression          abstraction criterion 3; MEA-19 regime battery
    external reproduction            OUT-01; L6

Yield per quarter is a vector: claims at each level (promotions minus mechanical demotions, with time to demotion);
typed nulls and null certificates issued; qualified instruments; certified world families; canary catch rate per
failure class and time to catch; retractions caught internally versus externally; realised search-mass shares under
generated bases; and cost per item (tokens, USD, core-hours, kWh, operator minutes). A quarter with two qualified rulers, three certified families, one null certificate and
no L2 claim is productive; a quarter with forty L1 anomalies and no L2 is not. Commits, runs, flags and agent activity
are not yield.

## 20. Publication and externalisation model

Externalised artifacts are limited to (OUT-01): claims at L3 or above with I3 re-execution and the GATE-NOVELTY checks
where unfamiliarity is claimed; qualified
instruments with their dossiers; certified world suites with certificates and baseline ladders (the most likely
first external artifact, useful whether or not any organism succeeds); and interpretable negative results carrying
null certificates. Each ships as a one-command reproduction package. Nothing below L3 is presented externally as a
finding. Note the doctrine tension: the tracked doctrine forbids publication framing (critical_memories HARD-1), while
this charter asks for externally inspectable outputs including preprints and negative-result reports. This package
treats the charter as the newer direct instruction for this deliverable and words outputs as inspectable work products;
the operator should rule (OPEN_QUESTIONS Q-OP1).

## 21. First 90-day MVP

**What gets built (S1, days 0-30, the vertical slice).** R0 minimal: deterministic runner with keyed streams,
snapshot/restore and receipts (CPU, energy, tokens, USD); append-only hash-chained ledger with segment files; signed verdict
batch job with row-class filter; deterministic weekly digest; the build token ledger. DGM kernel v0 with the
developmental instructions X1 needs, plus a slow reference interpreter, differentially tested. Lattice switches for
lifetime modification and internal ticks. World family F1 (per-lifetime mapping draw with exact adaptive gap and payback
ratio; variability x reliability x lifetime grid). One qualified ruler: the censoring-aware acquisition curve, qualified
on authored planted learners and innate genomes plus random genomes (procedurally generated plants are added at CORE,
in S2). Baseline subset: constant,
best fixed policy, best detect-and-dispatch genome, random genome. One CPU reference learner (evolved plastic recurrent
network). Evolutionary engine v0 with declared neutral-accepting acceptance. Counterfeit fixtures for every SLICE
requirement (SLICE-MIN after amendments: REQUIREMENTS.md s8; checker-enforced). S1 work items carry their own token
budgets, summing to no more than 40% of the 90-day envelope. The X1a verdict is at L1-slice: the known-positive
replication waives CAU-10 minimisation and AGR-13 follow-up.

**First organisms.** DGM genomes with lifetime modification on and off; the plastic recurrent reference; planted
learners and innate genomes (compiled) in S1; procedurally generated plants found by search from S2.

**First worlds.** F1 (slice); then F1c random mappings or k-armed tasks for X1c, F2 static needle, F3 hidden-state process pair with exact Bayes, F4 keyed binding,
F7 exact games with a Nim-like decoy (S2); F5 procedure reuse and F6 compositional grammar (S3).

**First pressures.** P0 versus P1 across change rate and lifetime (X1a); the ruggedness axis (X1b); P2 sequences for
X5.

**First developmental curricula.** None in S1. In S3, F5/F6 curricula admitted only with verified prerequisite structure
(WLD-08), run against direct, shuffled, retention-frozen and irrelevant-twin controls.

**First rulers.** Acquisition curve (S1); retention, matched ablation, interchange, deliberation signature,
acquisition-matched finite-state learners, minimisation (S2); write-order tracer qualification only if X8 says E6 is
affordable.

**Qualification experiments.** X1a, X9 bring-up receipt (S1); X0b, X1b, X1c (task-count x capacity known positive),
X2, X3, X4 (incl. general parity), X6, X8, X11 (substrate bake-off) (S2); X5, X10, X10b (accessibility at depth) (S3).

**Reused.** Almost nothing as code (SALVAGE_MATRIX.md s4): productive_liveness for derived status and SFE's
NK/BitString landscapes as estimator fixtures. The receipt schema and keyed-stream pattern are specifications for new
code; the Ensorain exact-Bayes processes are a sealed cross-check for the F3 solver (S2); the historical-control corpus
supplies qualification fixtures (packaged in S2). The DGM, R0's verdict job and ledger, F1 and the rulers are new code.

**Expected compute.** X1a about 1,200 runs at ~0.3 core-hours (~400 core-hours); whole MVP 2-10k core-hours.

**Inference boundaries.** Code authoring in budgeted work items (<= 3 concurrent sessions); preregistration drafting;
an I3 party (a budgeted non-Claude model through code, or a human) audits the verdict job and the acquisition-curve
ruler and authors >= 20 sealed counterfeits before day 60 (REP-08) and authors the probe kernel (the operator decides
the I3 source by day 30, Q-OP4); no LLM variation.

**Milestones and kill gates.**

    day 30   X1a preregistered and run; L1-slice verdict row signed by the verdict job OR a typed diagnosis
             naming the failed layer; X9 build receipt (incl. instrumented throughput); counterfeit suite for
             SLICE requirements passing; operator decision on the I3 source (Q-OP4)
    day 60   X1a/X1b/X1c verdicts; X2 result against the best proxy; ruler dossiers (authored vs generated
             sensitivity); capacity and developability fixtures in CI; X6 reachability curves; X8 sizing; X11
             bake-off; second certificate tool scored (WLD-17); REP-08 I3 audit and held-out counterfeit catch
             rate; X0b preregistered; probe kernel commissioned at I3; KILL/CONTINUE gate (ENGINE_PORTFOLIO.md):
             replace the substrate, diagnose the stack, reframe depth, or continue
    day 90   X5 result typed (positive, typed null, null certificate, or UNBRACKETED); X10 substrate variance and
             X10b accessibility at depth; certified world suite v0 (F1-F7) with certificates and baseline ladders;
             canary stream live; first L2 preregistration frozen (a one-shot confirmatory replication of X1a on a
             never-read sealed split, run after WLD-17 passes); decision memo on E4-E6 order and on whether the L3
             path fits the residual envelope

Engines existing by day 90: E0, E1, E2, E3, E4 (X5 only) and E10; E5-E9 are not started.

The MVP is designed to maximise information about the architecture -- whether the stack can say YES to a known
positive, whether depth certificates predict anything, whether rulers detect unfamiliar planted mechanisms, whether the
substrate's search space is reachable -- not to produce impressive results.

## 22. Six-to-twelve-month programme

Months 4-6: E4 campaigns on F5/F6/F10 under P2 with developability proofs and concentration floors; E5 build of F8 with
the own-reliability dissociation; E8 pilot (isolated LLM operator, <= 10M tokens, matched operator-model-free arm);
the first L2 confirmatory run; REP-02 independent kernel reimplementation started as soon as any L2 candidate appears.
Months 6-9: E5 campaigns; E6 if X8 shows it affordable and the write-order tracer qualifies on planted organisms
(including the deep-library and saturation plants); first L3 attempts only if the costed L3 path fits the measured
residual envelope (REP-02 done); externalisation of the certified world suite and the first null certificates. Months
9-12: E7 if a trigger has fired (second substrate authored at I2 or better, I3 preferred, continuous or asynchronous);
E9 yoked-ecology arm if the slice and E4 are stable. The planned year-one ceiling is L2; L3 is attempted only if its
critical path fits; L4r/L4d are not planned for year one, and L5 needs the second substrate.

## 23. Falsifiers

FALSIFIERS.md lists them by component. The most important: the stack cannot reproduce X1a in any substrate with
qualified rulers (stop science, diagnose the stack); after 6-12 months, with developability proofs, concentration
floors and certified curricula, structural development never beats retention-frozen and value-only arms (the
developmental framing is wrong or mis-scaled at this size; issue null certificates); every validated carrier is
FAMILIAR at small k and the operator-model-free arm finds nothing the LLM arm does not (the epistemic-escape premise
fails here);
the cost of a single L2 claim exceeds the year's envelope (the standard is too expensive for the resources); a
cross-family re-derivation of X0 or the salvage matrix disagrees on more than a third of items (this package's reading is
family-bound).

## 24. Explicit answers Q1-Q10

**Q1 -- Scientific legitimacy.** Current Prometheus research is premature science: a real scientific process applied to
mostly prototype apparatus. Evidence: of the 130 profiled results reclassified as an insufficiency, a true negative or
a hypothesis failure, 2 (CRI-C2T, HER-03) had S, W and R all scored Y, and none of the 20 true negatives and hypothesis
failures did; 30 of 146 distinct rulers had demonstrated detectability and about one measures an organism property; W
(world demand) was demonstrated for 37 of 353 results; independent replication for 20; mechanism by intervention for
24. What rules out cosplay is the norms the programme invented and adopted and late instruments that can fail both
ways; 139 later-correction rows against 357 reported-result rows show frequent self-correction, though who corrected
and how fast were not measured. What Phase 3 must change: qualify instruments before
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
structure; budget curves have flattened; and a bracket exists: the identical pipeline produced a positive of the same
type at the adjacent easier point of a declared difficulty axis, or recovered a planted solution of the same type from
operator distance >= d0/2 in >= 3 of N runs. The answer to "how capable must the organism, world and development be" is
therefore relative, not absolute: capable enough to produce or recover the phenomenon at the bracket and constructively
capable at the target point. Without that, a p_emerge below the frozen rate is a statement about the apparatus. For
phenomena with no developable genome, Phase 3 can issue only UNBRACKETED or developability-not-shown nulls; that is the
expected recursive-sagacity outcome in year one.

**Q3 -- Developmental adequacy.** Required machinery: cross-episode writable state; structural plasticity during the
lifetime; modifiable modification machinery (as a lattice switch); metabolic pressure with ramps; organism-constructed
credit assignment (no global error signal in the physics, DEV-15). High-value physics options: invocable stored
structure, multiple timescales, idle periods. What does the compression: within a lifetime, the organism's own
developmental rules (SPAWN/LINK/REWRITE/PRUNE programs) under metabolic cost of structure; credit is assigned by
whatever developed carrier routes reward to those rules (DEV-15). Evolution selects the rules under reuse pressure (P2);
it does not compress any single lifetime's experience. Building one carrier that serves several families is then
cheaper than building several. What produces abstractions: worlds whose families share latent structure under surface variation
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
beyond matched twins, carried by developed structure of executor order three or more -- shown by reversion (restoring
order >= 3 structure to birth removes a declared fraction of the acceleration relative to a size-matched sham reversion,
while order <= 2 is kept), by donor-depth dose-response in both the host's acquisition cost and its later
learning-to-learn slope, by a null effect from irrelevant-experience donors, by an executor-versus-content transplant,
and with no outer optimiser in the lifetime. The observation beyond ordinary learning-to-learn is the reversion and
transplant result. A meta-learned learner or a fixed rule with a growing library shows savings, and must be shown (by
the DEV-14 plants, including a library of composition depth >= 5) to have no order >= 3 structure whose reversion
removes them.

**Q6 -- Epistemic escape.** Plausibly yes for components, not for invention-and-recognition. LLM-proposed architectures and
LLM familiarity judgements stay near the corpus -- and the DGM is itself an LLM-proposed architecture, which is why
search mass is reserved for procedurally generated bases from the start (AGR-18), the probe kernel is authored at I3,
alternatives are compared in an X11 bake-off, and a second substrate is authored outside the family; search-generated variation in a substrate with procedurally generated
primitive bases, selected by deterministic worlds and qualified rulers, can produce structure no model proposed. We would
know through E8 (does an isolated LLM operator add validated findings per unit cost, and are its survivors more familiar?),
through grammar gravity (does the mechanism stay short under a random basis?), through the executable familiarity
reference (distance to the nearest reference mechanism reproducing behaviour and intervention signature), and through
reproduction in the operator-model-free arm. Unfamiliar mechanisms are protected from being discarded as noise by code-level
authority (interpretation cannot demote), mechanical follow-up allocation that serves unproposed candidates first,
minimal cores (so opacity is not rewarded), and the rule that unclassifiability raises priority after the gates and is
never evidence.

**Q7 -- Single engine versus portfolio.** An observatory around one primary substrate, with engines as questions run on
it, a probe kernel for substrate variance, and a second substrate on triggers. Not one integrated engine (attribution
dies in a coupled loop); not a family of separately authored engines (budget split, same-family breadth, no comparability).
X0 cannot discriminate single-substrate from portfolio (it coded a second substrate only when nothing else could settle
an item); it supports instrument priority. The single-primary choice rests on build cost and the measured triggers, and
is tested at depth by X10b (accessibility on F3/F4 across DGM, probe kernel and reference learner), X1c and X11.

**Q8 -- Existing machinery.** Over 130 distinct evaluated components: as running engines, none (zero of roughly twenty
historical engine-level systems carries forward as an engine). As code, about 4% (5 of 130), all small primitives --
well under 1% of the repository by lines. As designs to rebuild, about a sixth (22 components whose design becomes the
specification of a new build). As historical controls, more than half (73): the failures of Phases 1 and 2 become the
qualification fixtures of Phase 3. Retired, about a fifth (26). Conceptually, then, roughly a fifth of the scientific
machinery survives (code plus designs, 27 of 130) and essentially none survives as running machinery. The most
valuable surviving asset is not code: it is the recovered failure taxonomy, mapped onto enforced requirements so that
every one of the 70 classes has a covering requirement with a counterfeit fixture. Nothing was preserved for sentiment:
every reuse claim was attacked by a skeptic, and 53 were downgraded.

**Q9 -- First experiments.** The smallest experiments that discriminate between Phase 3 architectures. X0 (done): in-
substrate repairs would have made all 210 coded failures interpretable, and a ruler-side repair was the cheapest for
54%; it excluded the 20 surviving anomalies and coded a second substrate only when nothing else could settle an item,
so it cannot reject an early portfolio -- it supports instrument priority (E1/E2 first), not the substrate count; X0b
asks the substrate question with a reachable portfolio branch. X1a (can the stack reproduce a known developmental
positive end to end -- discriminates "instrument works" from "instrument broken"); X1c (task-count x capacity: does a
generalising learner appear above a capacity-dependent threshold, in the reference learner and in the DGM --
discriminates qualified from unqualified transferable-sagacity rulers and DGM from reference accessibility); X2 (do depth
certificates predict held-out performance of learners not used in the certificates better than the best proxy --
discriminates world-forge-first from search-first); X3 (are core rulers sensitive on procedurally generated plants -- discriminates usable rulers from
FAMILIAR-ONLY); X4 and X6 (developability proofs and needle inflation in the full lattice -- discriminates the primary
substrate from a minimal variant or a second substrate); X8 (power for recursive sagacity -- discriminates whether E6 is
affordable at all); X10 and X10b (probe-kernel variance on F1 and accessibility at depth on F3/F4 -- discriminate
substrate-local from pressure-determined results); X11 (substrate bake-off -- discriminates the DGM from its
alternatives); X5 (development discriminator -- discriminates the developmental thesis from "more compute"). X7 (LLM
operator vs operator-model-free arm) discriminates LLM-in-the-loop generation from structural search, after month 4.

**Q10 -- Failure.** After 6-12 months, any of: the stack cannot reproduce X1a in any substrate with qualified rulers; with
developability proofs, concentration floors and certified curricula, structural development never beats retention-frozen
and value-only controls on savings or transfer in any certified family; every validated carrier is FAMILIAR at small k and
the operator-model-free arm finds nothing the LLM arm does not; a single L2 claim costs more than the year's envelope; or a
cross-family re-derivation overturns the X0 or salvage reading on more than a third of items. Any of these would say the
present thesis is wrong or badly framed at this scale.

## 25. Highest-value unresolved questions

OPEN_QUESTIONS.md lists them with owners and the experiment that resolves each. The five that matter most: Is cognitive
depth, as certified, predictive (X2)? Is the full-lattice primary substrate searchable at CPU scale (X6)? Can
developability proofs for keyed binding and procedure reuse be built cheaply (X4, X9)? Can an executable familiarity
reference reach UNFAMILIAR without rewarding noise (AGR-12)? Can an I3 party (another model family or a human) be engaged
by day 30 for the REP-08 audit and sealed counterfeits, the probe kernel and later re-execution (without it, the day-60
gate, L4 and externalisation stay blocked)?

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
shown able to say YES, and the desk audit found that a ruler-side repair was the cheapest way to make more than half of
the coded failures interpretable (many of them by catching false positives). An instrument that has reproduced a known positive end to end, with its matched negative, is the cheapest thing that
can make every later NO mean something -- and it is the thing Prometheus never had.
