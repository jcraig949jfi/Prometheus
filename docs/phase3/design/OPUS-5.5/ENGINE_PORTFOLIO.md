# Phase 3 engine portfolio -- OPUS-5.5 (Epimetheus)

Status: frozen with RSE_ARCHITECTURE.md before salvage (77d3c99c3), except the field "Reusable Prometheus components",
which was filled after salvage from SALVAGE_MATRIX.md (categories in brackets: HARDEN, EXTRACT, REBUILD = rebuild keeping
the design, HC = historical control). Currency 2026-10-01.

An "engine" here is a scientific question run on the shared observatory (R0-R5 of RSE_ARCHITECTURE.md), not a
separately authored code base. All science engines use the same primary substrate (DGM), the same world forge, the
same rulers and the same verdict job; they differ in world families, pressure statistics, lattice switches and
measurement emphasis. That is deliberate: it is what makes their results comparable and what keeps the search budget
concentrated. Engines E0-E2 are instrument engines whose outputs are qualified instruments and certified worlds; E3-E8
are science engines; E9-E10 are deferred or narrow.

Common to every engine (not repeated below): executable preregistration (SCI-04), keyed random streams (REP-07),
claim ceiling declared before running (SCI-09), typed nulls (SCI-03), the automatic baseline ladder (MEA-03), the
signed verdict job (PRV-02), the material provenance shadow (ORG-08), receipts with CPU/energy/token fields (CMP-02).

## Discriminating experiments referenced throughout

    id    experiment                                                                          engine  stage
    X0    desk audit of historical apparatus nulls and false agreements (done; X0_RESULT.md)  -       pre
    X1a   variability x reliability x lifetime sweep: plasticity evolves where Delta and rho   E3      S1
          predict; matched P0 negative
    X1b   static needle: transient learning then assimilation (feedback events counted)        E3      S2
    X2    certificates predict which baselines fail on fresh instances (F1-F4, F7 incl. a      E2      S2
          Nim-like decoy)
    X3    ruler bake-off on authored and procedurally generated plants                         E1      S2
    X4    capacity and developability proofs for keyed binding, hidden-state tracking,         E1      S2
          procedure reuse and a self-modified learning rule; affordance-necessity proofs
    X5    development discriminator: curriculum / direct / shuffled / retention-frozen /       E4      S3
          irrelevant twin on F5/F6, budget curves in two currencies
    X6    needle inflation and reachability: p_hit(k) curves, full lattice vs minimal          E1      S2
          variant, neutral-accepting vs novelty search, budgets 1e4..1e8
    X7    generation source: isolated LLM operator vs model-free arm                           E8      S4
    X8    recursive- and transferable-sagacity power simulation on planted organisms           E1      S2
    X9    kernel bring-up and ruler port-cost receipt (tokens, agent-days, defects)            E0      S1-S2
    X10   probe-kernel substrate variance on X1a                                               E10     S3

----------------------------------------------------------------------------------------------------------------

## E0 -- Reality kernel and verdict authority (instrument engine)

- **Scientific question.** Does the pipeline refuse every counterfeit in the requirement fixtures (one or more per
  recovered failure class, 70 classes), while admitting every genuine planted positive and the predicted genuine
  null?
- **Organism / developmental / world physics.** Not applicable (operates on rows, receipts and fixtures).
- **Search / pressure.** None.
- **Measurement stack.** Counterfeit fixture suite derived from the "fake" field of every BLOCK requirement;
  dependency-demotion tests; canary injector (MEA-17).
- **Known-positive qualification.** Genuine planted claims at L1 and L2 pass end to end; the predicted genuine null
  passes the null-certificate checker.
- **Known-negative qualification.** Every counterfeit is refused at the named component.
- **Cheap baseline.** A pipeline that refuses everything (must fail the positive suite) and one that accepts
  everything (must fail the counterfeit suite).
- **Causal intervention.** Disable one gate at a time in staging; the matching canary must escape and the dead-man
  switch must freeze promotion above L2.
- **Transfer test.** The same suite run against the probe kernel's and reference learner's rows.
- **Primary hallucination risk.** Structural compliance: gates that check the shape of rows rather than their
  content (the historical sigma_kernel PROMOTE pattern).
- **Primary false-negative risk.** Over-strict gates that make every promotion impossible (detected by the positive
  suite).
- **Expected compute / inference / energy.** Negligible CPU; build inference M-L; no operating inference.
- **Dominant cost.** Build inference (code authoring) and operator review of the counterfeit suite.
- **Reusable Prometheus components.** toolbox receipt schema [EXTRACT, after fixing default=str collisions and making the chain mandatory]; productive_liveness [HARDEN] for derived status; SFE prediction-before-observation and evidence-class rules, comms.manifest LF rule, workspace-guard and Alethelia contracts [HC: design rules only, each with a fail-open defect to avoid]; Agent Fabric invariants [REBUILD as the one job runner]. The signed verdict job, dependency demotion, row-class filter and token harvester are greenfield.
- **New components.** Signed verdict batch job; row-class filter; dependency graph for demotion; counterfeit suite.
- **Kill criteria.** If after the slice any counterfeit class passes, promotion above L1 is frozen until fixed (not a
  kill of the programme).
- **What success means.** The program's claims are only as good as this engine; success means attractive
  hallucinations cannot be promoted by any route a seat or model could take.
- **Claim ceiling.** Instrument claims only.

## E1 -- Instrument qualification lab (instrument engine)

- **Scientific question.** At what effect sizes do the core rulers (acquisition curve, retention, specificity,
  interchange, transplant, dose, minimisation, deliberation signature, write-order tracer, decoder, familiarity
  reference, null-certificate checker) detect planted developmental and mechanistic phenomena, with what false-
  positive rates, on authored versus procedurally generated plants -- and can the substrate express and develop the
  target capabilities at all?
- **Organism physics.** DGM plants: authored (compiled from reference programs) and procedurally generated (found by
  exhaustive or random search over small organisms; never inspected by ruler authors). Includes the cheapest
  non-target organisms for each definition clause (library, clock, hub, deep reactive pipeline, first-order Bayes
  agent, painter, latch).
- **Developmental physics.** Planted developmental genomes g* (DEV-13) and planted order-1/2/3 writers plus a
  maturation clock (DEV-14).
- **World physics.** F1-F4 initially; F5-F10 as they are certified.
- **Search / pressure.** For X6 only: neutral-accepting population search and novelty search from planted distances.
- **Measurement stack.** The rulers under qualification; the statistics library (MEA-11) with known-answer tests.
- **Known-positive qualification.** Each ruler's sensitivity curve on planted positives, reported separately for
  authored and generated plants.
- **Known-negative qualification.** Matched negatives, cheapest cheats, label-permutation invariance,
  content-stripped metadata classifier at chance.
- **Cheap baseline.** A ruler that reads only observation statistics (must fail decoder and interchange
  qualification); the existence-of-FSC baseline (must not be used as evidence).
- **Causal intervention.** Plant mechanisms carried by structure, transient state, timing and organism-written world
  state; each must be localised by at least one route (CAU-09).
- **Transfer test.** Rulers re-qualified on the reference learner and, when available, the probe kernel (MEA-10).
- **Primary hallucination risk.** Rulers qualified only on familiar, model-authored plants (FAMILIAR-ONLY), then
  used to declare unfamiliar mechanisms absent.
- **Primary false-negative risk.** Plants too easy (single ceiling hits) so sensitivity at the effect sizes of
  interest is unknown.
- **Expected compute.** Low to moderate CPU (hundreds to a few thousand core-hours, dominated by X6 and X8).
- **Expected inference.** Build M-L (plant compilation and synthesis tooling); operate none.
- **Expected energy.** Tens of kWh.
- **Dominant cost.** Build inference for plant tooling; CPU for X6.
- **Reusable Prometheus components.** Ananke explib qualification seed [HARDEN]; Ananke swap_rel interchange rule [HARDEN, into the statistics library]; NPE z8shadow tracer, Ananke mirror-twin lens, Archaeon taint VM, Aether one-bit twin, Hephaestus closure gauntlet, Ergon bounded-null skeleton [REBUILD keeping the design]; fixtures [HC]: VACUOUS_READINGS, NULL_BOOT, attacks/REGISTRY classes, Ensorain WTP specimens, CVT-R panel design and painters, P-11 geometry, Crius id-counter cheats, Ares zero-hidden latch, Aphrodite order-2 shape, Hecate exact AUC/CP as specimens.
- **New components.** Plant compiler and procedural plant generator; dossiers; FAMILIAR-ONLY classification;
  rediscovery-from-distance estimator.
- **Kill criteria.** A ruler that cannot reach sensitivity >= 0.8 at the preregistered SESOI on generated plants within
  two redesigns is retired and its claim class is not attempted in year one.
- **What success means.** Every later claim can state its ruler's measured sensitivity, false-positive rate and
  failure regimes; nulls can be typed by ruler capability.
- **Claim ceiling.** Instrument claims; no claims about organisms.

## E2 -- World forge and depth certification (instrument engine)

- **Scientific question.** Do bound-typed cognitive-depth certificates predict which baseline classes (constant,
  memoryless, canonicalised lookup, acquisition-matched FSC learners, reference learner) fail on fresh instances?
- **Organism physics.** Baselines and reference policies only (plus constructive DGM organisms as witnesses).
- **Developmental physics.** Not applicable.
- **World physics.** POMDP family grammar; F1-F10; sealed known-answer world set for WLD-17 (closed-form-solvable,
  lookup-solvable, latch-solvable, leaky worlds).
- **Search / pressure.** Privileged search for existence witnesses (open-demand tier).
- **Measurement stack.** Exact solvers plus an independently authored slow solver; certificate calculators;
  all-channel leak audit; admission ladder.
- **Known-positive qualification.** Families with analytic depth (causal-state processes, keyed recall with fooling
  sets) reproduce their analytic certificates exactly.
- **Known-negative qualification.** The Nim-like decoy must be certified shallow under the closed-form policy; leaky
  worlds must fail the audit.
- **Cheap baseline.** Grid size and state count as depth proxies (must predict worse than the certificate).
- **Causal intervention.** Sweep generator parameters; certificate components must move monotonically.
- **Transfer test.** Certificates computed by two independent tools agree (union-vs-best miss rate).
- **Primary hallucination risk.** The forge certifies the demand its author expects; correlated blind spots across
  all families from one author.
- **Primary false-negative risk.** Certificates that are only upper bounds, admitting shallow worlds as deep or
  excluding deep ones.
- **Expected compute.** Low (exact solvers on small families); moderate for open-demand witnesses.
- **Expected inference.** Build M-L; grammar proposals at forks.
- **Expected energy.** Low.
- **Dominant cost.** Build inference (solvers, certificate tools, independent second tool).
- **Reusable Prometheus components.** Ensorain arc3/suff exact-Bayes processes [HARDEN] as the F3 core; Ludus leak audit, Ensorain null ladder, Cosmos holdout broker, Charon ceiling_v0 [REBUILD keeping the design]; Ludus Nim-345/Bouton and leak fixtures, alien_circuitry monoid oracle and its non-quotient-disjoint split, Tyche needle classes [HC] for WLD-17 and WLD-03 regression tests.
- **New components.** Family grammar; certificate calculators with bound types; sealed known-answer set.
- **Kill criteria.** If X2 shows the certificate predicts baseline failure no better than state count on fresh
  instances, the depth concept is reframed before any reasoning claim is attempted.
- **What success means.** "Cognitive depth" becomes a measured property of worlds rather than a description.
- **Claim ceiling.** Instrument claims; the certified suite is an externalisable artifact (OUT-02).

## E3 -- When development pays (pressure transitions)

- **Scientific question.** Do the adaptive gap Delta and the payback ratio rho = L / tau_id predict where lifetime
  plasticity, innate-adaptive programs and transient Baldwinian learning evolve -- in the DGM, the probe kernel and
  the reference learner?
- **Organism physics.** DGM with structural development on/off and value-only plasticity arms; probe kernel;
  evolved plastic RNN reference.
- **Developmental physics.** Lifetime learning on/off (lattice); retention boundary defines development.
- **World physics.** F1 (per-lifetime mapping draw; variability x reliability x lifetime grid with exact Delta, rho)
  and F2 (static needle).
- **Evolutionary / search pressure.** P0, P1 and R axis swept; between- and within-lifetime change rates swept
  (PRS-07); costs ramped with a zero-cost arm; pressure certificate per cell (PRS-12).
- **Measurement stack.** Acquisition curve (within-lifetime improvement), innate competence at birth, genome
  analysis of evolved plasticity, budget curves in two currencies.
- **Known-positive qualification.** External: learning evolves at moderate change rates and gives way to genetic
  control when change is rare or lifetimes short; Baldwinian smoothing of needles. Internal: planted learner and
  planted innate genomes classified correctly.
- **Known-negative qualification.** P0 cells: plasticity must not be favoured at equilibrium (the predicted genuine
  null for the null-certificate checker).
- **Cheap baseline.** Best fixed detect-and-dispatch genome within the genome size limit.
- **Causal intervention.** Switch plasticity off in evolved learners at fixed genome; graded dose on plastic
  carriers.
- **Transfer test.** Transition boundaries compared across DGM, probe kernel and reference learner (X10).
- **Primary hallucination risk.** Counting generations instead of feedback events makes learning look cheaper than
  it is (external critique of the Baldwin literature); fixed by MEA-14.
- **Primary false-negative risk.** Lifetimes shorter than identification time; costs from generation zero.
- **Expected compute.** About 1,200 runs at ~0.3 core-hours for X1a (~400 core-hours); X1b smaller.
- **Expected inference.** None operating.
- **Expected energy.** About 5-10 kWh.
- **Dominant cost.** CPU.
- **Reusable Prometheus components.** None as code beyond the R0/R1 items; keyed-stream pattern [HARDEN behind a new key schema]; Tyche eps-lexicase [HARDEN]; external known positives (evolved plasticity under environmental change; Baldwin needles) as qualification targets.
- **New components.** F1/F2 generators with exact Delta/rho; detect-and-dispatch baseline.
- **Kill criteria.** If X1a fails on the DGM with qualified rulers while passing on the reference learner or probe
  kernel, the DGM is replaced (substrate trigger); if it fails everywhere, the stack is diagnosed before any other
  science engine runs.
- **What success means.** The program's whole stack can recover a known developmental result, and the pressure
  statistics that make development pay are measured in this substrate.
- **Claim ceiling.** L2 (a pressure-statistics effect), L3 at most for the plastic carrier.

## E4 -- Constructive development and reusable structure

- **Scientific question.** Under P2 pressure, does lifetime structural development produce carriers that meet the
  abstraction criteria (specificity beyond sham, surface invariance, compression in two languages, transplant or
  interchange) and reduce acquisition cost on structurally novel families, compared with retention-frozen and
  value-only controls at matched budgets?
- **Organism physics.** DGM full lattice vs structural-development-off vs value-only arms; two encodings at L3.
- **Developmental physics.** Structural development; idle periods on/off; curriculum panel (standard, shuffled,
  direct, impoverished).
- **World physics.** F5 (procedure-library inference and reuse), F6 (compositional grammar with pair-block holdout),
  F10 (surface-varied recurrence).
- **Evolutionary / search pressure.** P2 sequences in long lifetimes; developmental programs evolved; concentration
  floor per arm.
- **Measurement stack.** Acquisition curves with yoked replay; transfer with two-sided certificate; specificity,
  interchange, transplant with sham arms; construction test (DEV-05); minimisation.
- **Known-positive qualification.** Planted organisms with genuine reusable procedures (DEV-13 g*) recovered;
  external: modularly varying goals and connection costs produce modular structure.
- **Known-negative qualification.** Table-memoisation organisms show zero transfer on F5; extra-inert-capacity
  organisms show zero TS (TRF-06).
- **Cheap baseline.** Same-compute direct exposure; shuffled curriculum; fixed reference meta-learner.
- **Causal intervention.** Interchange of candidate carriers between runs with different latent library entries;
  transplant into capacity-matched naive hosts.
- **Transfer test.** Structurally novel families admitted by the two-sided certificate; representation scrambling.
- **Primary hallucination risk.** Grown infrastructure hubs (clock, normaliser) passing shared-ablation tests; blocked
  by specificity and double dissociation at L4.
- **Primary false-negative risk.** Developmental programs not findable within budget (search-bounded); curricula
  without usable prerequisites (WLD-08).
- **Expected compute.** Moderate to high CPU (thousands of core-hours per campaign).
- **Expected inference.** None operating; interpretation of minimal cores at forks.
- **Expected energy.** Tens of kWh per campaign.
- **Dominant cost.** CPU.
- **Reusable Prometheus components.** D-5 G9 shuffled-history vs random-library decomposition [HC template for DEV-02]; Crius PARTS and RELAY design [HC design source for F5]; Ensorain WTP-03 pair-block holdout [HC design reference for F6]; Ergon library-seeding decomposition [HC].
- **New components.** F5/F6/F10 generators; curriculum builder with prerequisite verification.
- **Kill criteria.** If, with developability proofs present and the concentration floor met, structural-development
  arms never beat retention-frozen and value-only arms on savings in two consecutive preregistered campaigns, the
  claim "structural development is a lever" is withdrawn for this substrate (a null certificate is issued if every
  element passes).
- **What success means.** Evidence that a developmental process, not a genome, constructed reusable structure that
  makes new problem classes cheaper.
- **Claim ceiling.** L4 in year one (L5 requires the second substrate).

## E5 -- Epistemic pressure and the emergence of self-monitoring

- **Scientific question.** Do worlds with misleading first evidence, unreliable sources of learnable reliability and
  costly verification select carriers that track the organism's own error and drive verification, abstention or
  revision under own-reliability dissociation -- beyond a first-order Bayes-optimal baseline?
- **Organism physics.** DGM full lattice; internal-step truncation and internal-noise injection as manipulations.
- **Developmental physics.** As E4.
- **World physics.** F8 (epistemic family) and F7 (deliberation-relevant games).
- **Evolutionary / search pressure.** Costs on observation and premature action; reward for revision.
- **Measurement stack.** Qualified decoders (conditional decodability beyond observation history); interchange
  between high- and low-error trials; deliberation signature; WLD-16 dissociation.
- **Known-positive qualification.** Planted self-monitoring organism (abstains more under truncation).
- **Known-negative qualification.** Planted first-order Bayes organism (no response to dissociation).
- **Cheap baseline.** First-order Bayes policy; observation-statistics difficulty model.
- **Causal intervention.** Interchange of candidate error-tracking carriers; ablation sparing first-order competence.
- **Transfer test.** New epistemic families with different source structures.
- **Primary hallucination risk.** Decoding difficulty features as self-monitoring (blocked by MEA-15 and WLD-16).
- **Primary false-negative risk.** Self-monitoring that is amortised and invisible to decoders at the chosen probe
  capacity.
- **Expected compute.** Moderate CPU.
- **Expected inference.** None operating.
- **Expected energy.** Tens of kWh.
- **Dominant cost.** CPU; build inference for F8.
- **Reusable Prometheus components.** None as code (F8 is new); Charon ceiling_v0 [REBUILD] as the design reference for active identification.
- **New components.** F8 generator with exact Bayes reference; dissociation manipulations.
- **Kill criteria.** No organism beats the first-order Bayes baseline on the dissociation arm after two campaigns
  with the concentration floor met: claim class withdrawn for year one.
- **What success means.** A measured, causally localised carrier whose function is tracking the organism's own
  reliability, arising under pressure without a labelled confidence output.
- **Claim ceiling.** L4.

## E6 -- Recursive plasticity

- **Scientific question.** Under the P3b regime, do order >= 3 writes arise, and do they carry acceleration of
  acquisition on held-out families beyond fixed-rule-plus-library and maturation-clock controls (R1-R5)?
- **Organism physics.** DGM with rewrite-of-rewriters on vs off (single switch).
- **Developmental physics.** Order-tagged writes (DEV-14); reversion of order >= 3 structure; donor-depth transplants.
- **World physics.** F9 (P3 and P3b sequences with certificates showing fixed meta-rules fall behind after h*).
- **Evolutionary / search pressure.** Long lifetimes; sequences of families within a lifetime.
- **Measurement stack.** Write-order tracer; acquisition curves relative to the family-prior Bayes floor; reversion
  and donor-depth dose-response.
- **Known-positive qualification.** Planted order-3 organism classified and its acceleration removed by reversion.
- **Known-negative qualification.** Planted fixed-rule-plus-library organism (m=30, c=3) and maturation clock rejected.
- **Cheap baseline.** Fixed meta-rule learner; gradient meta-learned recurrent reference (learning-to-learn without
  recursion).
- **Causal intervention.** Reversion of order >= 3 structure; transplant from irrelevant-experience donors (clock
  control).
- **Transfer test.** Held-out families from the P3b grammar beyond h*.
- **Primary hallucination risk.** Library growth or maturation masquerading as machinery change.
- **Primary false-negative risk.** Power: second-order effects need many families and runs (sized by X8); regimes
  that do not predict recursion (P3 only).
- **Expected compute.** High CPU (long lifetimes x many families); sized by X8.
- **Expected inference.** None operating.
- **Expected energy.** Tens to low hundreds of kWh per campaign.
- **Dominant cost.** CPU.
- **Reusable Prometheus components.** Aphrodite fold-DSL engine [HC: the order-2 planted shape]; NPE z8shadow label algebra [REBUILD into the write-order tracer].
- **New components.** Write-order tracer; F9 generators with bias-growth certificates.
- **Kill criteria.** If X8 shows power 0.8 requires more than the year's envelope, E6 is deferred (not killed). If run
  at adequate power with every null-certificate element passing and no order >= 3 effect, a null certificate is
  issued for this substrate and regime.
- **What success means.** The first operational evidence for "recursive sagacity" in the strict sense of
  REQUIREMENTS.md s3, or a calibrated negative bounding it.
- **Claim ceiling.** L4.

## E7 -- Mechanism transplant and cross-substrate convergence (trigger-gated)

- **Scientific question.** Does an L4 carrier found in the DGM have a functional equivalent, matched by behaviour and
  intervention signature, in an independently authored second substrate, on families with policy multiplicity?
- **Organism physics.** DGM plus the second full substrate (preferably continuous or asynchronous).
- **Developmental physics.** As in the originating engine.
- **World physics.** The originating anchor families plus families authored at I2 or better (TRF-04).
- **Evolutionary / search pressure.** As originating engine.
- **Measurement stack.** Signature matching qualified on planted pairs; rulers qualified on both substrates (MEA-10).
- **Known-positive qualification.** A planted mechanism implemented in both substrates is matched.
- **Known-negative qualification.** Different mechanisms with equal scores are not matched.
- **Cheap baseline.** Score-only matching (must be beaten).
- **Causal intervention.** Interchange within each substrate; cross-substrate functional transplant where an
  interface map exists.
- **Transfer test.** The engine is the transfer test.
- **Primary hallucination risk.** Convergence forced by a narrow optimum (blocked by WLD-20).
- **Primary false-negative risk.** The second substrate cannot express the mechanism (requires its own capacity
  proofs).
- **Expected compute / inference / energy.** Moderate CPU; build inference L-XL for the second substrate.
- **Dominant cost.** Build inference.
- **Reusable Prometheus components.** None (the second substrate is new by construction); Aether and Ananke independent-oracle differential tests [HC exemplars].
- **New components.** Second substrate; cross-substrate signature matcher.
- **Kill criteria.** Not started until a trigger fires.
- **What success means.** A mechanism that belongs to the problem rather than to one substrate.
- **Claim ceiling.** L5 (L6 needs a sealed confirmation substrate and external replication).

## E8 -- Generation source and the gravity meter

- **Scientific question.** Does adding an information-isolated LLM variation operator increase the rate of
  reality-validated L1/L2 findings per unit cost relative to the model-free arm at matched evaluation budget -- and
  does it shift survivors toward familiar reference mechanisms (FAMILIAR-k) and toward the authored basis rather
  than procedurally generated bases?
- **Organism physics.** DGM; authored and procedurally generated bases.
- **Developmental physics.** As E4.
- **World physics.** A subset of certified families where E4 or E5 have L1 candidates.
- **Evolutionary / search pressure.** Matched arms: structural operators only; structural plus isolated LLM operator
  (genome text, bounded-precision fitness, frozen hashed prompt only).
- **Measurement stack.** Material-descent gravity meter; familiarity reference (AGR-12); grammar-gravity re-search;
  cost per validated finding.
- **Known-positive qualification.** A planted cheat operator with world access must be detected (AGR-16).
- **Known-negative qualification.** A random-edit "LLM" stand-in must show no familiarity shift.
- **Cheap baseline.** The model-free arm; a cheap template-edit operator.
- **Causal intervention.** Regenerate model-authored regions with an isolated operator or random edits; competence
  that disappears was model-seeded.
- **Transfer test.** Survivors re-searched under a procedurally generated basis.
- **Primary hallucination risk.** The prompt as answer channel; the corpus recognising itself.
- **Primary false-negative risk.** Prompt and operator design so constrained that the LLM adds nothing that a better
  structural operator would not.
- **Expected compute.** Moderate CPU.
- **Expected inference.** HEAVY relative to other engines; capped per preregistration (for example <= 10M tokens per
  pilot); the only engine with operating inference.
- **Expected energy.** Moderate.
- **Dominant cost.** Inference tokens.
- **Reusable Prometheus components.** prometheus_llm [REBUILD as the single, mandatory-audit choke point]; Fabric claude-executor isolation recipe [REBUILD]; Proteus crucible [HC/REBUILD] for publishing unselected variation kernels (AGR-15).
- **New components.** Isolated operator harness; familiarity reference library.
- **Kill criteria.** If the LLM arm does not beat the model-free arm on validated findings per unit cost in two pilots,
  LLM variation is excluded from production search.
- **What success means.** A measured answer to the epistemic-escape question for this programme: whether model-
  mediated variation finds more, and whether what it finds is more familiar.
- **Claim ceiling.** L2 for the meta-claim; mechanisms found are tagged MODEL-ASSISTED or MODEL-SEEDED and capped at L3
  unless they reproduce in the model-free arm.

## E9 -- Yoked ecology arm (deferred, EXPERIMENTAL)

- **Scientific question.** Does contingent interaction with other adapting organisms, compared with yoked replay of
  the identical interaction stream, select developmental capacities that authored worlds do not?
- **Organism / developmental / world physics.** DGM populations sharing a world; yoked replay arm.
- **Search / pressure.** P4 ecological interaction.
- **Measurement stack.** Contingency battery (ON vs YOKED vs SHUFFLED); qualified open-endedness metrics only (MEA-18).
- **Known-positive / negative qualification.** Contingent-payment effect (historical BEE ON vs YOKED geometry) as a
  positive; yoked arm as the negative.
- **Cheap baseline.** Yoked replay.
- **Causal intervention.** Remove contingency while preserving resource totals.
- **Transfer test.** Developed organisms tested on authored certified families.
- **Primary hallucination risk.** Unqualified complexity metrics read as progress.
- **Primary false-negative risk.** Ecology too small or short.
- **Compute / inference / energy.** High CPU; no inference.
- **Reusable Prometheus components.** BEE ON vs YOKED contingency design [HC]; primordial/qd/archive.py [UNKNOWN, possible QD reference].
- **Kill criteria.** Not started before month 6 and the vertical slice.
- **What success means.** Evidence that interaction supplies pressure authored worlds cannot.
- **Claim ceiling.** L3.

## E10 -- Probe-kernel substrate variance (narrow)

- **Scientific question.** Is the X1a transition threshold a property of the pressure statistics or of the DGM?
- **Organism physics.** Probe kernel (<= ~1.5k lines, authored at I2+, different conventions).
- **World physics.** F1.
- **Measurement stack.** The E3 rulers, ported (the port cost is X9).
- **Known-positive / negative qualification.** As E3.
- **Cheap baseline.** As E3.
- **Kill criteria / trigger.** A threshold outside the DGM's within-kernel span fires the second-substrate trigger.
- **Compute / inference / energy.** Low CPU; build inference S-M (external author preferred).
- **Reusable Prometheus components.** None (authored outside the family by design).
- **Claim ceiling.** L2 (a substrate-variance measurement).

----------------------------------------------------------------------------------------------------------------

## Day-60 kill/continue gate (S2 -> S3)

    condition at day 60                                              action
    X1a reproduced at L1 on DGM with matched P0 negative               continue
    X1a fails on DGM, passes on probe kernel or reference learner      replace the primary substrate (design
                                                                       review; second-substrate commission)
    X1a fails everywhere with rulers qualified                         stop science engines; diagnose the stack
    X2: certificates no better than state count                        reframe depth before E4-E6
    X3: core rulers FAMILIAR-ONLY on generated plants                  no phenomenon-level nulls in year one;
                                                                       redesign rulers
    X6: needle inflation > 100x for >= 2 target classes                substrate trigger (minimal-lattice variant or
                                                                       second substrate)
    X8: E6 power needs more than the year's envelope                   defer E6; keep E4/E5
