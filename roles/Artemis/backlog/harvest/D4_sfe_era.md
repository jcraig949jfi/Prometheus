# D4 harvest -- SFE-era science + instruments (Artemis Block A)
Domain: D4, SFE-era science and the instruments that gate it. Tip read: d7ec26d37 (2026-09-27). Harvested 2026-09-27.
Covered: SerendipityFoundry/{worldfoundry,worldfoundry/mhc,incubator,D6A,D7,D8,D10,D10phase2,selection_boundary,stackvm_admission,wow,forensics,Engine docs}; roles/Daedalus; archaeon/{wse,campaign1-6,docs/h0h5,frontier,causal_lens,envgate,envgate2,z80atlas}; roles/Archaeon (H0H5_STATUS, BACKLOG, review packets, ENGINE_LANDSCAPE); vivarium + roles/Vivarium; evidence_wiki + roles/Mnemosyne; proteus, ludus, herakles, theophrastus, genesis, nyx, techne (+ roles); ergon + roles/Ergon; roles/Metis; roles/Hypatia; alien_circuitry; incubation, incubation_d; roles/Harmonia/{rulings,science}.
Postgres (read-only, 192.168.1.202): ew.hypotheses 21 rows (all HYPOTHESIZED: 20 MISSING_CELL, 1 CANDIDATE_RELATION); ew.claims 147 (OBSERVED 64, SUPPORTED 33, REFUTED 18, RETRACTED 13, NOT_ESTABLISHED 13, ESTABLISHED 6). No claim status is literally OPEN or INDETERMINATE, so NOT_ESTABLISHED was treated as the open-like status. comms.messages kind='question': 27 rows.
NOT covered in depth: per-slot C4/C5 READOUTs; causal_lens/FALSE_FRIENDS.md; archaeon/rie and lineage code (no prose); SFE Engine/Client code; the evidence_wiki v2 arm outputs beyond spot checks; seat branches not merged to main; ops/ (only the TH-001..TH-006 threads, read for de-duplication).
Method: bounded git grep for open/unresolved/untested/parked/deferred/INDETERMINATE/"questions for the reviewer" markers, plus reading of review packets and campaign reports. Five read-only sub-harvesters by subdomain, then merged. For every candidate, later evidence was checked with git log --since on the directory and a cross-grep of later files.
Counts: about 99 raw candidates became 70 after merging and removing duplicates. Dropped as ops rather than science: Clio orphan base rate, degeneracy-guard retro audit, witness-bound off-by-one (already fixed), PEW-vs-ledger redundancy, step_scale registry rule, NK permutation convention (the last two appear under cross-domain pointers).
Existing threads ops/threads/TH-001..TH-006 were read. Candidates that duplicate them say so in "later evidence".
Kind counts are at the end of the file. A quote marked [em-dash] had one non-ASCII dash replaced; no other text in quotes was changed.
Staleness: most seats in this domain have made no science commits since 2026-09-11..09-19. "none found" usually means the line died when the seat went quiet, not that the question was answered.

### H-D4-01 Sterile length valley and reproductive isolation between length modes (stackvm)
- source: SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt:214 @ a6f86c3d3 (2026-09-03), seat Daedalus (WOW archaeology); quote: "sterile-band mechanism: does / mutation from 401-700 parents / work at all? The corpus contains"
- kind: parked-experiment
- question: 327 artifacts sit in the 401-700 byte band, and none was ever used as a parent. There were zero crossings from <=150 to >700 bytes (A3, line 147: "BIMODAL LENGTH WITH A STERILE VALLEY"). Is the valley sterile because of the mutation mechanism, and is the isolation between modes mechanical or historical (WOW-C-004)?
- why it might matter: This is a direct measurement of a damage cliff and of speciation-like isolation created by a variation operator alone. The operator decides which lineages can reach which representations.
- later evidence: none found. It is classified CC (fresh-intervention testable) at selection_boundary/EXTERNAL_REVIEW_PACKET.txt:318-321 @ ef504133f but was never run. No science commits have touched SerendipityFoundry/wow since 2026-09-04.
- lenses: stackvm-v1 mutation operator, SFE lineage ledger, CC fresh-randomization test
- related: H-D4-02, H-D4-04, H-D4-63

### H-D4-02 Neutral self-loops concentrated on 25 artifacts and U-shaped in length
- source: SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt:154 @ a6f86c3d3 (2026-09-03), seat Daedalus; quote: "A4  NEUTRAL SELF-LOOPS ARE CONCENTRATED AND U-SHAPED IN LENGTH. 344 of / 40,796 lineage edges (0.8%) are self-loops -- mutation returning a / byte-identical genotype -- and they fall on only 25 artifacts (top:"
- kind: anomaly
- question: Why do byte-identical mutation returns pile up on 25 artifacts, and why is the rate non-monotone in length (1.5% / 0.1% / 1.5%)?
- why it might matter: This hints at neutral-network or robustness structure in the stackvm genotype map, which is a precondition for evolvability. It was never turned into a candidate.
- later evidence: none found. It is not in the stackvm_admission queue.
- lenses: stackvm-v1, lineage ledger, neutral-network probes
- related: H-D4-01, H-D4-57, H-D4-59

### H-D4-03 One task solved twice from unrelated lineages in opposite length modes
- source: SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt:174 @ a6f86c3d3 (2026-09-03), seat Daedalus; quote: "9bc2b861. Task a768fad8 was solved TWICE, by eadcc0bd (37 bytes, / mutate, 3 ancestors) and 9bc2b861 (707 bytes, create_random) -- / artifacts with ZERO shared ancestry, from OPPOSITE length modes."
- kind: parked-experiment
- question: What do the two independent solutions share mechanistically (WOW-C-005)? Is there a representation-independent attractor for a768fad8?
- why it might matter: Convergent mechanisms across unrelated lineages would show structure in solution space that selection finds regardless of representation. The candidate is inadmissible as a rarity claim, but a mechanism comparison is still possible.
- later evidence: stackvm_admission/CONSOLIDATED_EXTERNAL_REVIEW_PACKET.txt:430 @ faff7495d asks whether frozen candidates should be "formally retired". No ruling was found.
- lenses: stackvm-v1, disassembly/ablation, map_elites archive
- related: H-D4-01, H-D4-16

### H-D4-04 Cross-engine sterility: treegp and push produced zero successes, stackvm seven
- source: SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt:169 @ a6f86c3d3 (2026-09-03), seat Daedalus; quote: "A6  CROSS-ENGINE STERILITY. treegp-deap (3,008 artifacts) and push-pyshgp / (2,404) produced ZERO successes; all seven belong to stackvm-v1."
- kind: anomaly
- question: Is the zero-success record a property of the tree-GP and Push representations, or of how they were configured and budgeted?
- why it might matter: This is an accidental representation-vs-representation comparison under selection, which is the axis the North Star cares about. It has never been measured deliberately at matched budget.
- later evidence: none found
- lenses: treegp-deap, push-pyshgp, stackvm-v1, SFE executors
- related: H-D4-21, H-D4-60

### H-D4-05 D6A: would a constructive, history-conditioned interface turn an endogenous signal into findability?
- source: SerendipityFoundry/D6A/REPORT_D6A.md:76 @ d332658cf (2026-09-01), seat Agent D-6A (Daedalus role); quote: "A successor generation would need a preregistered interface whose expressive locus is / constructive (e.g. z-conditioned composition proposals) rather than purely selective"
- kind: unfollowed-recommendation
- question: The endogenous signal (10x on-manifold concentration, Z1 > Z0) was real but only reordered proposals. Would the same signal raise exact findability if it generated proposals instead?
- why it might matter: It separates "history identifies modules" from "history helps solve". The null was attributed to the interface, not to the history.
- later evidence: partial. SerendipityFoundry/D7/README.md @ d332658cf used a history-conditioned synthesizer and certified a 3.1x positive in its own designed world. The z-conditioned arm on the D6A battery was never run.
- lenses: D6A battery, D7 synthesizer
- related: H-D4-06, H-D4-07

### H-D4-06 D7 nonlinear wormhole: does the only certified positive survive outside its designed world?
- source: SerendipityFoundry/D7/README.md:91 @ d332658cf (2026-09-01), seat Agent D-7 (Daedalus role); quote: "transfers); effect magnitudes are seed-sensitive; the mechanism depends on the / gated writer being marginally invisible, a designed property of this world. Post-"
- kind: open-question
- question: Does the certified effect hold when the gate-opener is not designed to be marginally invisible, and across seeds and worlds?
- why it might matter: This is the one certified positive for relational history as a selection channel in the D-series. Whether it generalizes decides whether that channel exists at all.
- later evidence: none found
- lenses: D7 substrate/census/certify, altworlds.py
- related: H-D4-05

### H-D4-07 D8 / accumulated executable history: is the null only a power failure, and does developmental content beat random material?
- source: SerendipityFoundry/D8/agent_d8/REPORT.md:245 @ d332658cf (2026-09-01), seat Agent D-8 (Daedalus role); quote: "of M1F's small numeric edge is reproduced by the same machinery filled / with random programs. The proposal-diversity scaffolding (seeding + / splicing anything at all) does the work; the developmental CONTENT adds". The same result is recorded as ew.claims id=C-065a321e0808 (NOT_ESTABLISHED): "G1 Delta = +0.100 with McNemar p = 0.210 fails".
- kind: parked-experiment
- question: At adequate n, which would need about 3-4x more discordant pairs and a matched H-RANDOM record count, does accumulated history add anything beyond the diversity that seeding and splicing supply?
- why it might matter: It is the direct test of whether lineage memory compounds or is just a diversity source. Whether "experience" matters at all depends on it.
- later evidence: none found. The claim is still NOT_ESTABLISHED, and the F4 transfer family was vacuous.
- lenses: D8 arms M1F/H-RANDOM/M0b, McNemar power
- related: H-D4-38, H-D4-51, H-D4-63

### H-D4-08 D10: give relevance keying an execution bridge (option b, never taken)
- source: SerendipityFoundry/D10phase2/REVIEW_PACKET_PHASE2.txt:166 @ d332658cf (2026-09-01), seat Agent D-10 (Daedalus role); quote: "THIS IS NOT evidence that endogenous relevance keying is impossible, and / says nothing about geometry, memory organization, concepts or cognition. It / RETIRES THIS INTERFACE: a future evolutionary null here would have been"
- kind: parked-experiment
- question: Syntax recovered run identity (.919), not function (.314). With a bounded execution primitive (phase-1 Q4 option b, REVIEW_PACKET_PHASE1.txt:680), can evolved memory organization key relevance? A second question: was the untested two-chromosome KA/KQ split modular (PHASE1_REPORT.md:346-352: "The transfer ceiling is entirely unmeasured"; about 32% of mutations rewrite both chromosomes)?
- why it might matter: This is a memory representation co-evolving with the searcher, a literal North Star mechanism. The blocker was structural, because syntax cannot reach semantics without execution.
- later evidence: none found. The phase-2 charter declined (b). ew.claims id=C-1f7991001445 (NOT_ESTABLISHED) lists "seven unresolved contamination threats".
- lenses: D10 organizer KA/KQ, Foundry 0.1.0 VM, fitness-autocorrelation probe
- related: H-D4-05, H-D4-38

### H-D4-09 Incubator World-0: where is the line between exploitable depth and authoring the ladder, and what should the world pay for?
- source: SerendipityFoundry/incubator/PROMETHEUS_INCUBATOR_WORLD0_DESIGN_REVIEW.txt:1022 @ 17f2b8d3a (2026-09-02), seat Daedalus (Incubator); quote: "Q2. WHERE IS THE LINE between \"biasing the channel generator toward compositional / reuse so that depth is exploitable\" and \"authoring the ladder\" (K2)? This is / the single most consequential unresolved design question (A3)."
- kind: open-question
- question: Is deep random composition exploitably regular or just noise? A companion question (Q1, line 1017): is "the world pays for predictive accuracy" neutral, or would paying for persistence, replication or construction select different machinery?
- why it might matter: It decides whether open-ended depth can emerge without human scaffolding (kill criterion K2). The choice of payout is itself a choice of which reasoning mechanisms can evolve.
- later evidence: none found. No World-0 physics core (channel generator, six-verb interface) exists in any *.py.
- lenses: Incubator World-0 (unbuilt), WORLD0_KILL_CRITERIA
- related: H-D4-10, H-D4-64

### H-D4-10 World Foundry: is the diversity currency gameable by noise, and does evolved play shift the pre-evolution null?
- source: SerendipityFoundry/worldfoundry/WORLD_FOUNDRY_V0_EXTERNAL_REVIEW_PACKET.txt:760 @ 6efa4f88d (2026-09-02), seat Daedalus; quote: "A6  THE DIVERSITY CURRENCY (R10) pays for behavioral divergence, which is / gameable in principle (cheap noise is divergent). The cluster cap and the / two-statistic rule guard the obvious exploit; the red team of the NEXT"
- kind: open-question
- question: Does paying for behavioural divergence select novelty or noise, and is the two-currency budget ecology or subsidy (Q4)? Second (A3, line 747): if evolution changes the correlation structure between worlds and opponents, is the exchangeable-unit null calibrated before evolution still valid?
- why it might matter: Co-evolving populations change their own environment. Both the reward and the null can be corrupted by exactly the process under study.
- later evidence: none found. The recommended next step, R12 earned admission on grammar v0 (line 798), is not in wforge/.
- lenses: wforge world/probes, R10 budget, R5 hierarchical null
- related: H-D4-09, H-D4-55

### H-D4-11 MHC observatory is blind on structured (memoryful) bases
- source: SerendipityFoundry/worldfoundry/mhc/QUALIFICATION_RESULTS_V0.txt:14 @ 5df88d07f (2026-09-02), seat Daedalus (MHC); quote: "          500  32   1.00/1.00        1.00/0.95        0.05/0.05      1.000"
- kind: defect-ambiguity
- question: At the strongest planted effect, recovery is 0.05 when the base already has structure (the echo column). Can MHC V1 show calibrated power on structured bases, for example by measuring fingerprint change under perturbation-exchangeability?
- why it might matter: The instrument built to detect "zero becoming not-quite-zero" fails in the realistic case, evolved organisms. Exposing it to science is prohibited until this is fixed.
- later evidence: MHC_V1_PLAN_EXTERNAL_REVIEW_PACKET.txt:442 @ 7173c9a87 ("B1 remains OPEN"). No V1 calibration results were found.
- lenses: Microstructure Hadron Collider / Observatory
- related: H-D4-33, H-D4-45

### H-D4-12 Selection boundary: a logged query interface so rarity claims become admissible
- source: SerendipityFoundry/selection_boundary/EXTERNAL_REVIEW_PACKET.txt:378 @ ef504133f (2026-09-03), seat Daedalus; quote: "Q4 THE ARCHITECTURAL REMEDY: mandate that all future mining run through a / LOGGED QUERY INTERFACE, so the consulted sigma-field is bounded by / construction and G-conditional rarity nulls become available. This is the"
- kind: unfollowed-recommendation
- question: If mining is bounded by a logged interface, do conditional rarity nulls exist for claims that "evolution found something rare"? M4 is capped at SR2 because of an unfalsifiable wall-clock channel.
- why it might matter: Without it, no serendipity claim from the ecology can be tested, which gates the whole "surprise" output of the program.
- later evidence: none found. No Q1-Q7 adjudication was located. SFE_C6_OBSERVATORY_REVIEW_2026-09-18.md:175 @ f42b07422 says "The engine cannot tell you when the SCIENCE goes blind".
- lenses: selection_replay_audit.py, RCLC, SFE ledger
- related: H-D4-50

### H-D4-13 The delay-invariant reader: what is it, and is it a capability or a sign the delay knob was never hard?
- source: archaeon/campaign3/CAMPAIGN_REPORT.md:452 @ cb9135104 (2026-09-17), seat Archaeon; quote: "C4-1  THE DELAY-INVARIANT READER. What is it? The ladder reliably" ... "instruction or a program shape. This is the campaign's only / reproducible positive capability and it is unexplained."
- kind: unfollowed-recommendation
- question: What are the genotype and the minimum lesion of the corridor organism that reads unseen delays (d8, d16)? REVIEW_PACKET_WSE_ARCHITECTURE_2026-09-17.md:580 @ 503fcf5b7 (Q2) asks whether this is a capability or evidence that "the delay knob was never / the difficulty it was assumed to be".
- why it might matter: It is the only reproducible positive capability in campaigns 1-3. If a construction-null solver also ignores delay, every working-memory claim on WSE is void.
- later evidence: none found. Campaign 4 turned to damage geometry and campaign 5 retired the substrate, so the reader was never dissected.
- lenses: WSE corridor ladder, lesion probes, held-out delay battery
- related: H-D4-14, H-D4-28

### H-D4-14 Does the curriculum ladder construct capability or select what the population already had?
- source: archaeon/campaign3/CAMPAIGN_REPORT.md:460 @ cb9135104 (2026-09-17), seat Archaeon; quote: "seeds the first delay-1 battery promoted an organism the W0 / population ALREADY contained. Probe the whole population, not / the elite, at each transition: what fraction is already"
- kind: unfollowed-recommendation
- question: At each rung transition, what fraction of the whole population already solves the next rung?
- why it might matter: This is the core ecology question: does staged pressure build new mechanisms or only filter standing variation?
- later evidence: none found. Population-level rung probes (the L3-020 telemetry note) were never run.
- lenses: WSE corridor ladder, CORRIDOR.jsonl, population-wide probes
- related: H-D4-13, H-D4-27

### H-D4-15 Injection cap plus a protected resident niche: can imports spread without extinguishing residents?
- source: archaeon/campaign3/CAMPAIGN_REPORT.md:476 @ cb9135104 (2026-09-17), seat Archaeon; quote: "The discriminating question is whether a cap plus a protected / resident niche keeps both lineages alive AND lets imported / capability spread -- the condition every future transfer"
- kind: unfollowed-recommendation
- question: Can a cap plus a protected niche keep residents and imports alive together while imported capability spreads?
- why it might matter: Every transfer and co-evolution design assumes this without testing it. C3-SFE-10 showed that injection moves populations regardless of what is injected.
- later evidence: adjacent only. C4-09 (campaign4/CAMPAIGN_REPORT.md) was INCONCLUSIVE ("rescued lineages persist and take over receiving populations"). No niche-protection test was found.
- lenses: inject()/common_fill cap, lateral ecology harness
- related: H-D4-24, H-D4-35

### H-D4-16 W2_K2 valley: missing primitive or missing search operator?
- source: archaeon/campaign3/CAMPAIGN_REPORT.md:468 @ cb9135104 (2026-09-17), seat Archaeon; quote: "and initialization are all exhausted. What remains / discriminating: a register/addressing primitive the grammar / lacks, or a search operator that can cross the two-value"
- kind: open-question
- question: Is the W2_K2 summit blocked because the representation lacks an addressing primitive, or because search lacks a valley-crossing operator?
- why it might matter: It is a clean representation-vs-search-mechanism discrimination, which is exactly the co-evolution axis.
- later evidence: advanced, not answered. C4-06 was INCONCLUSIVE ("0/6 and 0/6 crossings"). The C5 closure (campaign5/CAMPAIGN_REPORT.md:206-208 @ cdb55e152) says next work "must alter generative/search structure". The graph organisms and Proteus lane 2 are the untested successors.
- lenses: WSE W2_K2, recombination, graph organisms
- related: H-D4-59, H-D4-60, H-D4-20

### H-D4-17 Is the half-credit shelf a scientific object or an artifact of an additive reward?
- source: roles/Archaeon/REVIEW_PACKET_WSE_ARCHITECTURE_2026-09-17.md:575 @ 503fcf5b7 (2026-09-17), seat Archaeon; quote: "Q1  Is the half-credit shelf an interesting scientific object, or is it / an artifact of choosing a two-stream cell whose reward decomposes / additively? If the latter, the entire campaign-3 spine is a study"
- kind: open-question
- question: Does the shelf persist in a two-stream cell whose reward does not decompose additively?
- why it might matter: Campaigns 3-4 treat the shelf stratum as the main place graded change happens. If it is an artifact of the reward, that line of findings is void.
- later evidence: none found. C4 still treats "the shelf stratum" as real (campaign4/CAMPAIGN_REPORT.md:128-130).
- lenses: WSE reward decomposition, non-additive control cell
- related: H-D4-13

### H-D4-18 H2: does the CA compute, or the encoding? (Glover 2024 confound; D-18 v2 alpha never run)
- source: herakles/ca_stream/OBSTRUCTION.md:136 @ 5a0458fd6 (2026-09-10), seat Herakles; quote: "*these six rules, from an all-zero reset, through one binary port, / never leave the all-zero fixed point.* Change any one of those three / conditions and the measurement says nothing."
- kind: unfollowed-recommendation
- question: Under the approved D-18 v1 reset (Bernoulli 0.5, horizon 8), with the leakage probe run first, do the six density rules carry linearly readable temporal memory above the frozen-random null? And does that survive an encoding-null control (REVIEW_PACKET_2026-09-10.md:257 @ b29474229: "success can stem from the ENCODING / rather than the automaton (Glover, Osipov, Nichele 2024)")?
- why it might matter: Any claim that an evolved CA substrate is a reusable reasoning component, meaning an exaptation, must survive the published confound.
- later evidence: partial. D-18 v1 was APPROVED (archaeon/docs/expansion/DECISIONS.md:52), but ca_stream_v2 and run_alpha_v2 were never written (roles/Herakles/todo_2026-09-16.md:12-16). Archaeon SFE-04 (af666a099, 2026-09-16) got a weak positive of 0.608 vs 0.500, with the leakage probe NOT run (L-019). C3_2_READOUT.md:214 says C3-2 "CANNOT answer H2". C3-3 is unissued.
- lenses: herakles evca / ca_stream_v2, C3-3, encoding-null readout
- related: H-D4-19, H-D4-54

### H-D4-19 CA line falsification: can a reset-lattice-only readout reproduce particle2's margin?
- source: archaeon/campaign3/CAMPAIGN_REPORT.md:496 @ cb9135104 (2026-09-17), seat Archaeon; quote: "only as a falsification. Reproduce particle2's margin with a / readout over the reset lattice alone. If it reproduces, the CA / line closes permanently; if it does not, the mechanism is"
- kind: parked-experiment
- question: Does a readout over the reset lattice alone match particle2's margin?
- why it might matter: It is a cheap, decisive test that closes or reopens CA-as-computation. It is the concrete form of the Glover confound.
- later evidence: none found. It is only restated in REVIEW_PACKET_CMP3 and WSE_ARCHITECTURE:492.
- lenses: CA reset lattice readout, particle2 specimens
- related: H-D4-18

### H-D4-20 H3: does any archive/QD policy beat top-K on a real stream, and do the descriptors resolve anything?
- source: archaeon/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:129 @ 179cd46e4 (2026-09-11), seat Archaeon; quote: "4. What this does NOT say: nothing about a real C3/H1 stream (none exists / yet: C3-2's random arm was constant zero and C3-3 is unissued); nothing / about which of the three score-retaining policies is better"
- kind: prior-art-gap
- question: At matched budget on a generated stream, does QD retention beat sequential champion reuse? Prior art (Chen 2026, cited in REVIEW_PACKET_2026-09-10.md:261) found no QD advantage. Techne's receipt (roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:114 @ 2baf0680f) adds that "all 120 random rules fall into just four cells" and 126 of 150 score exactly 0.0. So which descriptor pair actually separates candidates?
- why it might matter: Archive memory of stepping stones is a core ecology assumption. A zero plateau is a neutral network the archive cannot see.
- later evidence: none found. ARCH-07 (a generated 1,024-candidate stream) is still open (roles/Archaeon/BACKLOG_H0H5.md:9), and TECHNE-03 is gated on demand.
- lenses: h3_replay.py, pyribs adapter, dead-stream twin control
- related: H-D4-16, H-D4-48

### H-D4-21 H5: can an evolved or learned encoding exceed the permutation bound in class-reach?
- source: archaeon/docs/h0h5/H5_1_READOUT_2026-09-11.md:37 @ 6fc3ea619 (2026-09-11), seat Archaeon; quote: "what the alpha was for. The evidence question (does an evolved encoding / exceed the permutation bound in class-reach?) needs the human-issued / comparison with a learned decoder, which does not exist yet."
- kind: open-question
- question: Can an evolved or learned genotype-phenotype decoder give more neutral accessibility than the analytic bound? (H5-1 only calibrated the instrument: every number was at its analytic bound.)
- why it might matter: This is the representation co-evolving to raise evolvability, measured on a fully enumerable space (256 rules, 224 classes).
- later evidence: none found. ARCH-30 (Polyhymnia table decoders) and ARCH-20 (encoding_search_v1) are still OPEN in BACKLOG_H0H5.md.
- lenses: eca_rule_eval_v1, h5_decoders, h5.lincode.v0
- related: H-D4-04, H-D4-59

### H-D4-22 H0/H1: library learning had no eligible input, and relevance was inert under budget caps
- source: roles/Archaeon/BACKLOG_H0H5.md:31 @ 0473b65b0 (2026-09-17), seat Archaeon; quote: "- ARCH-29 | H0 library cells have NO eligible input on the current H1 split (Nyx #53: 0 abstractions on PHASE1_3 by two extractors; the ALL_17 leak was the cheat firing) -> construct the H1 beta task family with shared parts across tasks"
- kind: parked-experiment
- question: On a task family with shared parts, does abstraction/library extraction yield reusable components that speed later solving? Related: archaeon/docs/h0h5/H1H0_PHASE2_READOUT.md:40 @ 8b78f1b5d says "relevance inert at this scope" because 10/12 targets hit BUDGET_VM_OPS. Does a relevant source pack beat a random one where targets are actually reachable?
- why it might matter: Library growth and relevant inheritance are the obvious routes by which reasoning mechanisms accumulate. "Nothing fired" here meant "nothing could have fired".
- later evidence: none found. ARCH-29 and ARCH-05 (H1 beta) are open. The campaign 1 report (lines 446-448) says the relevance question "was never posed".
- lenses: cegis_boolean_v1, Proteus boolean3.v0, stitch_core (D-17 dev-only)
- related: H-D4-07, H-D4-51

### H-D4-23 Host-conditioned reproduction as a cross-engine, portable assay
- source: archaeon/causal_lens/PORTABILITY01_REPORT.md:173 @ 37145999d (2026-09-26), seat Archaeon; quote: "2. **Outcome-C candidate: host-conditioned reproduction** now has three independent sightings: Archaeon host-mediated amplification / (ENVGATE-01 R2), NPE AN3 (reproduction that needs a similar host), and BEE CAPTURE/DECOUPLED. A cross-engine preregistered"
- kind: directive-idea
- question: Does reproduction depend on the host's prior state (necessity and sham both positive) with the same sign in Archaeon, NPE and BEE? This is the proposal in roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md:42 @ 95fff9111 ("make the lens portable ... Same result across three independent Z80 implementations = a real cross-engine differential").
- why it might matter: It would be a substrate-general ecological phenomenon, reproduction as a joint property of donor and host. It would also turn the Z80 triplication into a deliberate cross-implementation check rather than accidental convergence.
- later evidence: advanced. HOST_CONDITIONED_ASSAY_READINESS.md @ 949b9ba4d says "Nothing here is preregistered or launched". ops/campaigns/C-001/E-001/RESULT.md:34 says AN3 "SURVIVES", now thread ops/threads/TH-003.md (parked). The AN8 sibling is TH-004, and a launch needs the operator (C-001/CAMPAIGN.md:13). This is a DUPLICATE of TH-003 at the assay level; the cross-engine preregistration is the new part.
- lenses: causal_lens v0.2/v0.3, NPE P-11, BEE traced VM, archaeon/lineage taint VM
- related: H-D4-24, H-D4-25, H-D4-26

### H-D4-24 AN2: the random background out-reproduces the transplant in 40% of runs
- source: archaeon/causal_lens/PORTABILITY01_REPORT.md:119 @ 37145999d (2026-09-26), seat Archaeon; quote: "- AN2 (BEE) spontaneous-in-intervention: in 17 of 42 quarantined transplant runs, the first autonomous reproducer descends / from the RANDOM background, not from the transplant."
- kind: anomaly
- question: Why does a de novo reproducer arise from the random background before the transplanted replicator establishes?
- why it might matter: It bears on the origin of replication and on whether seeding actually controls what an ecology becomes. It parallels campaign 3's finding that injection moves populations regardless of content.
- later evidence: V02_REGRESSION_REPORT.md:130 @ 949b9ba4d marks it "UNCHANGED in the ancestry logic". No thread exists; TH-001..006 do not cover it.
- lenses: BEE harness, causal_lens ancestry, spontaneity tri-value
- related: H-D4-15, H-D4-23

### H-D4-25 ENVGATE: five unexplained establishments in the all-blocked arm
- source: archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md:20 @ 13cdec715 (2026-09-26), seat Archaeon; quote: "- **The five BAND0 establishments.** Genetic establishments in the all-blocked arm, against a planned ~0.7 total. Per-block / rows are in ENVGATE-02 RESULTS.json (`per_block`, `established_glins`). They stay unexplained, and no campaign will be / spent on them now."
- kind: anomaly
- question: How did lineages establish when every window was blocked (5 vs about 0.7 expected), and why do they cluster in the slow blocks 11, 13 and 14?
- why it might matter: The viable-window mechanism was rejected, so environmental gating is only partly explained. An unmodelled route to establishment is a fossil worth reading.
- later evidence: listed as a closed fossil at ops/threads/TH-001.md:15. Not investigated.
- lenses: envgate2 RESULTS.json, lineage taint VM, forensic replay
- related: H-D4-26, H-D4-23

### H-D4-26 Z80 replication endpoint may define away the real phenomenon (input-gated copying)
- source: archaeon/z80atlas/pivot/Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.md:361 @ 18772241e (2026-09-23), seat Archaeon; quote: "Q3 Does the frozen 0.9 mean-fidelity threshold exclude the only real / phenomenon (input-gated copying) by design? Should the endpoint be / lineage-level rather than world-cumulative?"
- kind: defect-ambiguity
- question: Is a world-cumulative 0.9 fidelity endpoint blind to replicators that copy only under an environmental condition? RULINGS_FOLLOWUP:21 says "99% of those copiers are input-gated".
- why it might matter: Conditional replication is a primitive form of environment sensing. An endpoint that excludes it hides the phenomenon of interest.
- later evidence: advanced. ENVGATE-01 GATING_PARTIALLY_SUPPORTED and ENVGATE-02 WINDOW_NOT_SUPPORTED (ENVGATE_CLOSURE_2026-09-26.md:11-14). No lineage-level endpoint rerun of the census was found.
- lenses: z80atlas census, copier_census EXACT_GATED, envgate
- related: H-D4-25

### H-D4-27 "Flat elite" and C5's untested boundary: population size, compute, or unclimbable worlds?
- source: archaeon/frontier/DECISIONS.md:139 @ c7610ea19 (2026-09-19), seat Archaeon; quote: "interpretations: C5-flat.T1 (N=200, W3_K3) max .500 > best starting parent .382 in three / seeds -- confounded by total compute vs C5 (60,000 vs 9,000-36,000) -> equal-compute N family / (50/100/200/400 x 3 seeds at 60,000 evaluations) queued to EXPLOITATION at top priority;"
- kind: open-question
- question: At matched compute, does a larger N escape the flat elite? And does bounded variation buy discovery on worlds evolution can climb? archaeon/campaign5/CAMPAIGN_REPORT.md:177 @ cdb55e152 says: "Not established: anything about worlds that evolution CAN / climb (no arm climbed any)".
- why it might matter: BOUNDARY_CREATED_NO_DISCOVERY_GAIN and "flat elite" may be population-size or world-choice artifacts, not substrate limits.
- later evidence: DIGEST_2026-09-21T2054Z.md @ 939e4f39e lists LIN-ffc7ae5d under SURVIVING MYSTERIES [PROVISIONAL]. No equal-compute readout was found.
- lenses: Deep Frontier scheduler, WSE W3_K3, Representation B
- related: H-D4-14, H-D4-29

### H-D4-28 P-boom: population capture inverts spiking on a shared stream
- source: commit message 939e4f39e (2026-09-21), seat Archaeon (frontier); quote: "3. K_F_popcapture (0.33) inverts vs F_popcapture (5.17) independent-stream -- / population capture suppresses spiking when stream is shared; strongest / arm-level interaction signal in dataset."
- kind: anomaly
- question: Does population capture really suppress boom/spike dynamics on a coupled world? Is the bimodality of K_B_shuffle (7 vs 0.33) a phase transition?
- why it might matter: The order vs population interaction on a shared stream is niche-construction dynamics. It is n=3 and PROVISIONAL, and a hidden-seed defect (DF-015) was found on the way.
- later evidence: none found. The stated next diagnostic ("N>=8 seeds per K_ arm") never followed.
- lenses: frontier c6.composed.v1, stream_key segments, population_shift/max_spike rulers
- related: H-D4-29

### H-D4-29 Graph organisms fire detectors 100x less: less dynamic, or detectors calibrated on v0?
- source: archaeon/frontier/DECISIONS.md:142 @ c7610ea19 (2026-09-19), seat Archaeon; quote: "graph populations fire two orders of magnitude less than v0 at v0-calibrated thresholds / (undetermined: churn vs spread);"
- kind: defect-ambiguity
- question: Is the drop a property of graph organisms or a bias of v0-calibrated detectors?
- why it might matter: Campaign 6's successor representation cannot be judged by a substrate-biased observatory. This gates every graph-organism claim.
- later evidence: still PROVISIONAL (LIN-6071e54d) in DIGEST_2026-09-21T2054Z.md. Campaign 6 has no CAMPAIGN_REPORT.
- lenses: campaign6 detectors/observatory, CALIBRATION_EPOCH
- related: H-D4-11, H-D4-59

### H-D4-30 H4: an adaptive difficulty policy with a live down-rule is untested
- source: archaeon/campaign1/SFE-05/RECORD.md:137 @ d3fb47c5f (2026-09-16), seat Archaeon; quote: "- Dead region: the down-rule (< 0.10) never fired; the ladder only went / up; a policy landscape (up/down thresholds) is untested."
- kind: parked-experiment
- question: Does an adaptive pressure schedule with a live down-rule beat fixed schedules? Is the adaptive +0.155 (weak, n=3) real?
- why it might matter: Adaptive pressure schedules are a primary lever the program is supposed to supply. H4 is NOT STARTED (H0H5_STATUS.md:44) apart from this one weak alpha.
- later evidence: none found
- lenses: WSE ladder, H4-ADAPTIVE-1.0.0, per-rung x generation matrix
- related: H-D4-14, H-D4-44

### H-D4-31 Does evolution reach the tape (addressed memory) when the VM can express it?
- source: archaeon/wse/READOUT_v01.md:199 @ b7518c392 (2026-09-16), seat Archaeon; quote: "\"substrate expressive boundary\" (POS proves the VM expresses W0-W3; the / untested question is whether EVOLUTION reaches the tape, and the survey / never gave it a foothold to test that)."
- kind: open-question
- question: Can evolution discover addressed tape memory rather than one recurrent register? READOUT_ssf.md:146 adds that "Selectivity pays" is untested by evolution.
- why it might matter: Whether expressibility equals accessibility is the core representation question of the North Star.
- later evidence: indirect only. WSE_ARCHITECTURE Q3 (line 585) questions the substrate. C4/C5 retired it without testing this.
- lenses: WSE survey, SSF stream worlds, graph organisms (memory nodes)
- related: H-D4-16, H-D4-60, H-D4-58

### H-D4-32 Gen-1 retention effect: what carried the gain, if not diversity?
- source: ergon/gen1b/REVIEW_PACKET_GEN1B_2026-09-01.txt:329 @ 83733abbe (2026-09-01), seat Ergon; quote: "What changed capability is not resolved by anything measured here, and the induced search trajectory remains the leading unresolved candidate."
- kind: open-question
- question: Diversity moved as designed (44.1 to 54.8) but correlated only r=+0.16 with the CFR gain (evidence_wiki/gold/harvest_a.jsonl:5 @ c711c5bf6). Does the effect run through library content or through the induced search trajectory? Can selected memory transfer without the trajectory that produced it?
- why it might matter: This is selection working for an unknown reason. The North Star needs to know what the selector actually selected for.
- later evidence: weakened. Project 1 and P3 (596e36fe2) found the effect does not replicate at n=100, so the mechanism question may be moot for this consumer. There are no Ergon commits after 2026-09-11.
- lenses: mediation analysis, trajectory ablation
- related: H-D4-33, H-D4-34, H-D4-47

### H-D4-33 Memory science after P3's null: is it capacity, not order, and does the null have a positive control?
- source: ergon/gen3/REVIEW_PACKET_P3_2026-09-11.txt:236 @ 7c1ad3729 (2026-09-11), seat Ergon; quote: "What we should stop: designing retention rules for this consumer at this cap. The next question is the CAP itself (ERGON-06 re-premised)."
- kind: unfollowed-recommendation
- question: At an identical metered budget, does keep-everything-to-cap differ from least-used retirement? That would be the first measured deletion. Line 240 of the same packet asks whether a bounded null on ORDER is enough without "an order-only cheat first", that is, can the channel detect a constructed 2 pp order dependency?
- why it might matter: Forgetting is how memory co-evolves with search. Retiring a research line on a null needs a positive control on the same axis.
- later evidence: none found. roles/Ergon/BACKLOG_H0H5.md:15 lists ERGON-06 NEEDS_REPREMISE, and no RESULT_retirement_vs_cap exists.
- lenses: memory metabolism, capacity vs policy, positive control
- related: H-D4-32, H-D4-11

### H-D4-34 Retention keyed on the mutation neighbourhood instead of the behaviour fingerprint
- source: ew.hypotheses id=H-9b0a7922015e (CANDIDATE_RELATION, 2026-09-01); quote: "admission/retention keyed on a mutation-neighborhood sketch instead of the behaviour fingerprint should change Gen-2 retention outcomes; if projection-equivalence is the shared mechanism, trap-world"
- kind: directive-idea
- question: Does keying the archive on what an organism could become (genotype neighbourhood) rather than what it does (phenotype) change which lineages survive?
- why it might matter: It tests whether the representation the selector sees shapes what evolves, which is a direct co-evolution lever.
- later evidence: none found. Still HYPOTHESIZED; it is only mentioned in evidence_wiki/docs/CASE_STUDIES_V0.md and the V1 charter.
- lenses: QD archive keying, evolvability descriptors
- related: H-D4-32, H-D4-20, H-D4-46

### H-D4-35 Origin takeover without clonal collapse: genome diversity hides lineage capture
- source: roles/Vivarium/point_release/VIVARIUM_EVIDENCE_INVENTORY.md:100 @ 37a5e9316 (2026-09-17), seat Vivarium; quote: "L3-017 MISSING_TELEMETRY    0    origin takeover is not clonal collapse; a genome-     lineage share per generation in trace rows"
- kind: anomaly
- question: How often does one origin lineage take over while genome diversity looks healthy? Should lineage share and realised dose be in every execution receipt?
- why it might matter: Diversity metrics that miss lineage capture misreport exploratory health. This bears on H-D4-32's diversity-mediator question.
- later evidence: partial. Intended vs realised dose is in Archaeon's trace but in no execution receipt (Amendment s6.G). No later receipt field was found.
- lenses: lineage vs genotype diversity, telemetry
- related: H-D4-15, H-D4-32

### H-D4-36 20 untested mechanism x substrate cells, incl. instrument_tautology in program_ecology
- source: ew.hypotheses id=H-a86125892a3e (and 19 MISSING_CELL siblings, e.g. H-f59eb0aaaedf, H-9d3b33c874bd, H-3d42b4c0891d); quote: "Untested combination: mechanism=confound_conditioning on substrate_class=program_ecology -- no evidence row in the V0 corpus despite both being heavily observed separately"
- kind: prior-art-gap
- question: Which program_ecology cells are real blind spots, and which are artifacts of how the vocabulary was built? The cells include confound_conditioning, negative_evidence_reuse, transfer_mediation, native_vocabulary, instrument_tautology, seed_instability and circular_verification.
- why it might matter: Instrument-validity failures in the core evolutionary substrate are the most dangerous blind spot, and the wiki already flags them mechanically.
- later evidence: none found. All 21 rows have stayed HYPOTHESIZED since 2026-09-02.
- lenses: Evidence Wiki gap analysis, ontology coverage
- related: H-D4-37

### H-D4-37 Explicit memory earned retrieval but not behaviour, only at sonnet tier, while an unlogged memory channel steered design
- source: evidence_wiki/V3_REVIEW_PACKET_2026-09-02.txt:233 @ 869755c2b (2026-09-02), seat Mnemosyne; quote: "Do you accept MARGINAL-under-saturation as grounds to fund a knowledge-bound (not skill-bound) execution instrument at larger n,"
- kind: unfollowed-recommendation
- question: When tasks bind on knowledge rather than skill, at larger n, does provenance-bound memory change behaviour? V3 measured +0.111 MARGINAL, a floor because the instrument saturated. V2 found the effect "MODEL_SPECIFIC_ONLY" (REVIEW_PACKET_V2.txt:124 @ 4c291e0a1) and an "implicit memory channel that shapes design behavior -- unlogged, unversioned, provenance-free" (line 79).
- why it might matter: It is the central test of whether accumulated failure evidence makes a reasoner wiser. If only strong reasoners can use it, memory and reasoner must co-evolve. The unlogged channel is also a confound on everything agents design.
- later evidence: none found. There is no evidence_wiki/v4, and the reviewer questions are unanswered. V3 mirrored only 4 operational claims.
- lenses: memory-augmented agents, ceiling effects, hidden-prior confound
- related: H-D4-07, H-D4-36

### H-D4-38 Relational-coordinate transfer is anti-predictive (below chance)
- source: ew.claims id=C-3c0f5fc710c0 (Diomedes, NOT_ESTABLISHED); quote: "arm B at 0.4885 is below chance with its interval excluding 0.500, so a model fit on one relation type is actively anti-predictive"
- kind: anomaly
- question: Is the below-chance transfer real structure (systematically inverted relation types) or a coding artifact? The claim itself says the artifact is "not excluded with certainty".
- why it might matter: A result below chance is information. It is either exploitable structure or an instrument defect, and both are worth knowing.
- later evidence: none found
- lenses: sign-flip audit, transfer
- related: H-D4-08

### H-D4-39 Outcome semantics: no kind-level INDETERMINATE, and single-field rules hide multi-metric results
- source: roles/Vivarium/BACKLOG_H0H5.md:73 @ 49ef27f9d (2026-09-16), seat Vivarium; quote: "| D3 | An `INDETERMINATE` outcome path for a kind that ran but could not decide. Today a kind either returns a result or raises. | READY | none |"
- kind: defect-ambiguity
- question: How should "ran but could not decide" be recorded, as distinct from an error? And how should metric multiplicity be declared so that picking a metric after the fact is visible? See roles/Vivarium/BOUNDARY_REVIEW_2026-09-05.md:112 @ a0f70c72d: "F5 [em-dash] a single-field rule silently narrows a multi-metric result (S14/A3)".
- why it might matter: Failure-as-evidence needs a third value. At present "unmeasurable" collapses into "invalid" or "negative" (compare 30e97ed94: "maj is not a structural zero, it was an unmeasurable one"), and post-hoc metric choice corrupts the fitness record.
- later evidence: partial. L3-039 fixed the rule-level branch, but VIVARIUM_EVIDENCE_INVENTORY.md:104 says "D3 (kind-level INDETERMINATE) still open". loop.py maps errors to INSTRUMENT_INVALID. F5 is unaddressed (DELIVERABLE_V0:271).
- lenses: three-valued verdicts, garden of forking paths
- related: H-D4-12, H-D4-48

### H-D4-40 Campaign 6 replay classes and T0 fingerprint plane were never built
- source: roles/Vivarium/campaign6/VIVARIUM_LANE_2026-09-18.md:40 @ 8291e211f (2026-09-18), seat Vivarium; quote: "replay A exact / B lineage / C world-seed   replication_of + request_key relations;      a REPLAY row kind that names the packet and"
- kind: future-work
- question: Can unplanned evolutionary events be noticed, frozen and replayed step by step (exact, lineage, world-seed, ablation, pressure perturbation), with EXOGENOUS/ENDOGENOUS pressure and HUMAN/LLM/EVOLUTION provenance labels?
- why it might matter: Replaying unplanned events with the fossils kept is what turns open-ended surprises into science rather than anecdote.
- later evidence: none found. The file says "Nothing below has been built or deployed". There is no replay_packet, provenance_class or evo_segment in vivarium/viv.
- lenses: replayability, provenance, observatory
- related: H-D4-12, H-D4-28

### H-D4-41 Fossil-directed vs uniform-control (F/C): preconditions were posed, no result found
- source: roles/Vivarium/prompts/2026-09-11_replies/ARCHAEON_FC_EXECUTION_PRECONDITIONS.md:1 @ 2d48582c4 (2026-09-12), seat Vivarium; also comms.messages id=219; quote: "Re: the preregistered fossil-vs-control experiment (F = fossil-directed, / C = uniform control). Vivarium executes; it does not judge F or C."
- kind: parked-experiment
- question: Does directing search by the fossil record (past failures and successes) beat uniform control on paired rows?
- why it might matter: It is the literal test of "failure is evidence and metabolic material".
- later evidence: none found in roles/Vivarium or in comms replies (only Daedalus #222). Archaeon's lane was not exhaustively checked.
- lenses: fossil-guided search, paired design
- related: H-D4-07, H-D4-37

### H-D4-42 No rewriting substrate: rewrite-strategy pressures are unhostable
- source: comms.messages id=189 (Nyx, 2026-09-11, kind=question); quote: "do you claim a rewriting substrate (boolean grammar v0 + identities as fact store)?"
- kind: prior-art-gap
- question: Should Prometheus host a term-rewriting substrate (transformation store, exhaustive application, observable termination) so that simplification strategies can evolve?
- why it might matter: Rewriting is a canonical reasoning mechanism, and without a substrate that whole mechanism class is outside selection.
- later evidence: comms id=276 (Proteus, 2026-09-16) says "(b) no rewriting substrate owned or intended". comms id=188 marks four lean_simp pressures UNHOSTABLE_TODAY. No owner.
- lenses: term rewriting, e-graphs, substrate coverage
- related: H-D4-64

### H-D4-43 Mutation-kernel nonequilibrium current: does it bias outcomes, and can the instrument certify absence?
- source: roles/Proteus/PROTEUS_V0_6_FINAL_EXTERNAL_REVIEW_PACKET.txt:1134 @ b9128d8f3 (2026-09-03), seat Proteus; quote: "U1  OPERATIONAL_SIGNIFICANCE_NOT_YET_ADJUDICATED. Whether the circulation / produces meaningful structural preference over realistic campaign / horizons."
- kind: open-question
- question: Does the authored grammar's irreversible probability current bias what evolves over campaign horizons? Is the residual current (U2, about 8e14x the reversible reference) authored asymmetry? And what minimum detectable current makes profiles comparable? Harmonia (roles/Harmonia/rulings/RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md:30 @ c387de555) says: "A per-profile measurement must be able to report \"no current above X\" / honestly, and today the instrument has no X."
- why it might matter: A hidden directional bias in variation shapes evolution independently of selection. Comparing geometry across grammar profiles is invalid until each profile's current is measured (comms id=341).
- later evidence: comms id=412 (Harmonia, 2026-09-18) says "ADMITTED AS A DETECTOR and NOT ADMITTED AS AN ABSENCE INSTRUMENT". FOUNDRY/GRAPH_PROFILE_CATALOG.json still say NOT_YET_ADJUDICATED. No P-1 positive control was found, and Proteus moved to graph organisms.
- lenses: detailed balance, mutational bias, minimum detectable effect
- related: H-D4-59, H-D4-60

### H-D4-44 Heritable variation operator in a modularly varying environment (Toussaint x Kouvaris)
- source: ergon/kouvaris2017/O_SFE_CALIBRATION_PROPOSAL.md:123 @ 83e2c88c8 (2026-09-03), seat Ergon; quote: "**The composition:** *variation machinery that changes itself under selection pressures that favour generalisable future variation*"
- kind: directive-idea
- question: If variation-operator parameters are heritable within a modularly varying environment under parsimony pressure, does the one-step offspring distribution evolve toward generalisable variation, measured longitudinally in every arm?
- why it might matter: It is the North Star made literal: variation mechanisms co-evolving under selection. The source says it is CPU-only and cheap.
- later evidence: none found. It is "recorded and NOT run" (line 119). The Kashtan-Alon MVG adjudications exist in elenchus, but nothing was built.
- lenses: evolvability, facilitated variation, heritable operators
- related: H-D4-49, H-D4-30

### H-D4-45 Latent-neighbourhood evolvability detector: no world exists that could falsify it
- source: ergon/detector_transfer/06_CANDIDATE_WORLDS.md:105 @ 1432d6b49 (2026-09-03), seat Ergon; quote: "The first SCIENTIFIC execution must wait on B acquiring a declared selection rule."
- kind: parked-experiment
- question: In a world with a world-applied selection rule, does the phenotype-partitioned neighbourhood RESIDUAL predict future acquisition beyond scalar summaries (Avida K1-K5)? A side question is still undecided: did Avida 1.6 already have this machinery? ergon/avida2003/.../V_FREEZE_RECORD.md:29 @ 2130c6a31 says "We do not know, and no claim may rest on either branch."
- why it might matter: On onemax, RESIDUAL = log2(k) is positive by construction, so the detector inherited from Avida has never faced a world that could kill it.
- later evidence: none found. No detector_transfer commits after 2026-09-03. Avida was re-acquired (713dfd0b1) and then deferred (4d1e22391).
- lenses: evolvability measurement, world adequacy, prior art
- related: H-D4-34, H-D4-11

### H-D4-46 Quotient organism: exact at oracle on T_7, inert in tensor-QD; does it scale, and when does it pay?
- source: alien_circuitry/nursery/NURSERY.md:75 @ 93cdb3392 (2026-09-14), seat AC-01 nursery; quote: "Held at SPECIMEN pending (a) a composition test with an orthogonal mechanism and (b) an account of WHY tensor-QD was inert (move-set bottleneck) that predicts inertness in advance"
- kind: contradiction
- question: Can we predict ahead of time when an exact quotient/canonicalizer cuts search cost (T_7, Diomedes) and when it does not (tensor-QD)? Separately: does the 25,382-orbit quotient stay compact at rank-3 or n=8? alien_circuitry/AC01D_V2_RECEIPT.md:106 @ 9072a959f: "Whether the same quotient suffices at rank-3 targets or n = 8 is a replication, not a corollary".
- why it might matter: It is the cleanest case of a discovered representation turning search into lookup, and the first organism seen recurring across ecologies. A theory of representation x move-set is what promotion requires.
- later evidence: CRUCIBLE-C passed (8157e9e70) and CRUCIBLE-B killed macros (93cdb3392). CRUCIBLES.md:106 prohibits "Any AC-01 scaling (rank-3, n = 8)". There have been no alien_circuitry commits since 2026-09-14.
- lenses: representation discovery, symmetry quotient, scaling
- related: H-D4-47, H-D4-34

### H-D4-47 Composition science: no calibrated zero point (CRUCIBLE-E), and reuse only tested where components are cheap
- source: genesis/harmonia_c/gen3/REVIEW_PACKET_FINAL_HARMONIA_C_GEN3.txt:476 @ d59cc7771 (2026-09-01), seat Harmonia C (genesis); quote: "THE SINGLE HIGHEST-VALUE FOLLOW-UP IS TO RAISE COMPONENT COST until / rediscovery is expensive, and re-run this identical harness unchanged."
- kind: unfollowed-recommendation
- question: When components are expensive to rediscover, does composition/reuse beat local mutation? In the cheap regime, children lost a parent capability at 78-83% of joins, and arm D had a 2.3x compute confound. What is the composition instrument's measured zero point? See alien_circuitry/nursery/CRUCIBLES.md:92 @ 86a429efe: "CRUCIBLE-E  NUR-008 composition control: orbit table + macros in T_7".
- why it might matter: Accumulation of capability through composition is a central North Star mechanism. Claims of "super-additive composition" (NUR-008) have no null without E.
- later evidence: the D16C LT benchmark was designed for this, but its pilot is HELD on ED-001 CRITICAL origin-laundering (D16C_PHASE0_REPORT.md @ 5910cc7fa). CRUCIBLE-A, D and E never ran. Nestor cw01-e05 (2026-09-17) prices components differently, which may be a cross-domain lead.
- lenses: composition, modularity, null instruments
- related: H-D4-46, H-D4-22, H-D4-53

### H-D4-48 A world with an exact oracle but no known certificate: does one exist at enumerable scale?
- source: alien_circuitry/UNIVERSE_C_DESIGN_SEARCH.md:166 @ f7ba88312 (2026-09-12), seat AC-01; quote: "If the operator wants a primary universe with NO known component at all, none passed the kill pass in this search"
- kind: open-question
- question: Does any enumerable world exist with an exact oracle, irreversible non-monotone traps and no textbook certificate? Or is that combination self-contradictory at enumerable scale? The companion U-C1 with R1 > 0 (SURVIVOR_GATE_RECEIPT.md:155 @ 014aa4f75) was never built. The K2 leakage ruler is also miscalibrated for a 0.39 base rate (line 152).
- why it might matter: Worlds that can tell rediscovery from discovery are the limiting reagent of the program. It is a structural question about the design space itself.
- later evidence: NUR-010 (LOCAL_EQUIVALENCE_GLOBAL_DIVERGENCE_WORLDS) is still a candidate. No new universe search after 2026-09-12.
- lenses: world design theory, leakage ruler, hidden-invariant discovery
- related: H-D4-09, H-D4-20

### H-D4-49 Can failure route plasticity to the right layer?
- source: incubation/v3/README.md:136 @ 5531f053f (2026-08-27), seat Incubation (Lens Genesis); quote: "algorithmic, and representational plasticity simultaneously, can failure route"
- kind: future-work
- question: With symbolic, algorithmic and representational plasticity available at the same time, can failure signals assign change to the correct layer? Line 122 adds: who writes the ontology of lens families?
- why it might matter: Credit assignment across co-evolving layers is the core North Star mechanism. v3 only showed selection within a designed family.
- later evidence: none found
- lenses: multi-level credit assignment
- related: H-D4-44, H-D4-50

### H-D4-50 Agent D homoiconic worlds: the meta-grammar passed census, but the worlds were never built
- source: incubation_d/README.md:39 @ f97feceaf (2026-08-27), seat Agent D; quote: "generator, QD archive, M0/M1 arms, transform ledger,"
- kind: parked-experiment
- question: Can accumulated executable experience in the frozen gv2 meta-grammar produce reusable transformations of the system's own machinery without a human-authored mutation taxonomy? The census passed: legacy share 0.365, all 12 edit shapes reachable.
- why it might matter: It is taxonomy-free self-modifying variation, which is squarely on the North Star.
- later evidence: none found. No incubation_d commits after 2026-08-27, and CK8 is deferred (design_manifest.md:177).
- lenses: homoiconicity, meta-evolution
- related: H-D4-44, H-D4-49

### H-D4-51 Four-arm learning-cost design: does learned indexing beat mere content (D vs C)?
- source: roles/Ludus/REVIEW_PACKET_2_2026-08-27.md:342 @ e85bfa6b9 (2026-09-01), seat Ludus; quote: "Decisive criterion: **D must beat C.** Otherwise the library / helps only because it contains useful programs, not because anything was learned about where to look."
- kind: parked-experiment
- question: Does an intact circuit library with its claimed indexing reduce the cost of mastering an unseen world compared with the same circuits with permuted associations?
- why it might matter: It separates "knowledge of where to look" from "having useful parts", which is the core transfer question.
- later evidence: CYCLE_005 (line 115) adopted it, and ARCHAEOLOGY_2026-09-11.md:219 PARKED it to H4. No run found.
- lenses: transfer, library learning, curricula
- related: H-D4-22, H-D4-07

### H-D4-52 Is a circuit's value a property of the world, or of the circuit, or of its partner? (r0003)
- source: roles/Ludus/CYCLE_004_VERDICT_basis_audit.md:47 @ e85bfa6b9 (2026-09-01), seat Ludus; quote: "**A circuit's measured value is primarily a property of the world it is measured in.**"
- kind: contradiction
- question: The world main effect (0.3497 vs 0.0998) was later "substantially explained away" (CYCLE_005), while rank stability (tau 0.9721) survives. Does a world-indexed r_i(W) ever beat a flat catalogue? Related: r0003's value "is NOT a function of (circuit, world) alone" (evidence_wiki/v1b/proposals/T6_wiki.md:162, partner spread 1.0000). ludus/atlas/CIRCUIT_LEDGER.md:13 @ 5e4f68c76 says partial loss is "Untested", yet cycle004_partner_matrix.json:845-856 already shows r0003|OPTIMAL = 0.0 on Coloretto.
- why it might matter: If mechanism value is ecological (world- and partner-dependent), then mechanisms cannot be catalogued independently of their ecology. The Coloretto cell may already be a damage cliff sitting exactly on the predicted precondition.
- later evidence: CYCLE_005_verdict_demotion.md:108-112 says "r_i(W) is NOT built". The ledger still reads "first failure: none recorded". No Ludus commits after 2026-09-16.
- lenses: niche dependence, partner effects, ledger staleness
- related: H-D4-53, H-D4-55

### H-D4-53 Martian Dice rule audit reversed which decision axis carries the difficulty
- source: roles/Ludus/CYCLE_002_stochastic_stopping.md:14 @ fb858dd5c (2026-09-16), seat Ludus; quote: "the residual lives in the claim axis\" result (s4) is therefore a fact about / the reconstruction, not about Martian Dice."
- kind: contradiction
- question: Which circuit maturity rungs move under the audited rules? STOP retentions changed by up to +0.74 and tau fell to 0.429. How many atlas conclusions rest on the 3 reconstructions that are still HYPOTHESIZED?
- why it might matter: World fidelity decides which mechanisms selection favours. Two corrected rules flipped the world's difficulty decomposition.
- later evidence: LUDUS-36 is open (roles/Ludus/BACKLOG_H0H5.md:47). No commits after fb858dd5c. LUDUS-15 left 2 constants UNSURE.
- lenses: world fidelity, instrument validity
- related: H-D4-52

### H-D4-54 Opponents: does an adversary create a new interface (DENY) or a new mechanism?
- source: roles/Ludus/REVIEW_PACKET_2_2026-08-27.md:212 @ e85bfa6b9 (2026-09-01), seat Ludus; quote: "Does an opponent create a **new interface** -- something like DENY, a decision whose value is entirely about the opponent's option set"
- kind: open-question
- question: Does adding an adversary create a denial interface or change the mechanism behind existing ones? Does self-play from the library collapse to a single style?
- why it might matter: It is the step from solitaire to coevolution, and a closed opponent pool is a known way for arms races to fail.
- later evidence: REVIEW_PACKET_4:363 says "n>2 turn management is untested". No DENY interface was found.
- lenses: coevolution, Red Queen, arms races
- related: H-D4-52, H-D4-10

### H-D4-55 ASAL observer: many-to-one compression, and the native Flax column was never scored
- source: nyx/atlas/gates/LEDGER.json:480 @ d8741f71a (2026-09-19), seat Nyx; quote: "distinct dynamical regimes are made equivalent by the observer's representation (a many-to-one compression). What dynamical or representational property makes distinct Lenia phenotypes occupy the same low-score region?"
- kind: anomaly
- question: Is the collapse of exploit dynamics and coherent life onto the same low score a property of the torch observer (HARM-56 outcome C) or a structured dependence? Do the torch-port crossers survive ASAL's native Flax CLIP path? See roles/Harmonia/rulings/RULING_ASAL_LEGIT_SEARCH_001_2026-09-18.md:189 @ 2ead5e011: "Owed (HARM-55): score the SAME 395 preserved frame sets through ASAL's original Flax CLIP path".
- why it might matter: An open-endedness metric that cannot tell life from garbage is a selection-pressure failure, and every learned-observer fitness will face the same problem.
- later evidence: Techne e3b927f4b (2026-09-25) says "HARM-55 native Flax column still not landed" (blocked on an AVX host). HARM-56 was preregistered (83a1c45a4) with no disposition as of Nyx RESUME 44e6bda1b (2026-09-25).
- lenses: observer dependence, metric exploitation, port equivalence
- related: H-D4-10, H-D4-11

### H-D4-56 Evolved memory is set-once, not a cue detector: what does evolution build under W16?
- source: roles/Nyx/reports/ARES_W4_READING_2026-09-25.md:212 @ bf5073a91 (2026-09-25), seat Nyx; quote: "A W16 lineage would have to add either a cue-magnitude threshold that ignites / from the rest state, or a rest state that sits near the ignition boundary. Ares's W16 runs, if / any exist, would show which."
- kind: open-question
- question: Under variable cue timing, which of the two predicted re-armable latch architectures does evolution find, or neither?
- why it might matter: It separates a reset-timing artifact from a genuine cue-detecting mechanism, a clean mapping from pressure to architecture.
- later evidence: answerable now, not yet read. Ares has 40 W16 files in ares/runs/sweep_c2 (1dde117f7, 2026-09-23), including W16_present_s201_dissect.json. No comparison was found.
- lenses: mechanism identification, Ares substrate
- related: H-D4-57, H-D4-31

### H-D4-57 Neutral accretion by duplicate_node: bloat or raw material for innovation?
- source: roles/Nyx/reports/ARES_W4_READING_2026-09-25.md:110 @ bf5073a91 (2026-09-25), seat Nyx; quote: "the pressure but neutral accretion by the search: no parsimony term, and `duplicate_node` / copies whole nodes (8 -> 10 at generation 15) that never acquire a function."
- kind: open-question
- question: Do neutral duplicates later become substrate for new function? The same question is queued at herakles/HERAKLES_HISTORICAL_COLLIDER_V0/K_RECONSTRUCTION_QUEUE.md:62: "Does a duplication event change the descendant mutation-effect distribution vs matched lineages?" (Lindgren IPD, rated TRIVIAL cost on 2026-09-03).
- why it might matter: Duplication-divergence is the canonical neutral-network route to novelty. Two seats raised it independently.
- later evidence: none found. No Lindgren reimplementation and no duplicate-vs-matched comparison.
- lenses: neutral networks, gene duplication, bloat
- related: H-D4-02, H-D4-56, H-D4-59

### H-D4-58 What is the unit of mechanism: a packet, a cut organ, or something else?
- source: roles/Nyx/RESUME_2026-09-25.md:223 @ 44e6bda1b (2026-09-25), seat Nyx; quote: "Is \"a mechanism == a cut organ\" the right granularity, now that \"a mechanism == a packet\" was / ruled wrong? All six registered mechanisms currently map one-to-one onto six organs"
- kind: open-question
- question: What is the right unit of selection and transplant for mechanisms? nyx/LOOP.md:58 has "organs repeatedly fail independent test" NOT YET TESTED, and MECHANISMS_THAT_SURVIVED_TRANSPLANT = 0. Related: nyx/catalog/eval/EVAL01/EVAL01_RESULTS.md:212 @ 053cc6c8e says "CATALOGUE RETRIEVAL SUPPORTED? INDETERMINATE." A non-author mapping (EVAL02) was never run.
- why it might matter: The unit of heredity decides what can be recombined. A mechanism representation that only its author can query cannot support cross-lineage recombination.
- later evidence: none found
- lenses: units of selection, modularity, transplant, catalogue validity
- related: H-D4-46, H-D4-47

### H-D4-59 PROTEUS-46: the cliff survives a graph grammar that is 64% neutral; can long neutral drift cross it?
- source: proteus/round2/PROTEUS-46_FALSIFIER.md:3 @ 6a98ef0bb (2026-09-18), seat Proteus; quote: "verdict CLIFF_SURVIVES | falsifier_status FALSIFIER_FAILED | neighbourhood_exhausted False"
- kind: open-question
- question: The graph grammar is far more neutral than v0.4 (0.64 vs 0.27), yet 0 of 9,148 children were useful and only 3-step walks were tried. Can long neutral drift, or a developmental regime (reopen conditions, line 85), reach the 6/6 summit?
- why it might matter: This is the direct test of whether neutral networks buy accessibility across a damage cliff in representation space.
- later evidence: none found. No Proteus commits after 2026-09-18, and neighbourhood_exhausted is False.
- lenses: neutral networks, damage cliff, search geometry
- related: H-D4-16, H-D4-60, H-D4-57, H-D4-02

### H-D4-60 Lane-2 admission: is encoding cost the barrier, or is a new primitive needed?
- source: proteus/docs/round2/ROUND_2_REPRESENTATION_AND_SEARCH_GEOMETRY.md:38 @ 6a98ef0bb (2026-09-18), seat Proteus; quote: "(if the frozen grammar / reaches the cheap form but not the expensive one, cost is the barrier; if it reaches neither, / the barrier is not cost and a new primitive is the wrong tool)"
- kind: directive-idea
- question: For two-value keyed memory, which is expressible but unreached, does the frozen grammar reach a hand-written cheaper encoding? A related lead is proteus/round2/ANATOMY_L0.md:9 (e11e22370): tick_budget separates delay_general from w0 solvers (p 0.0062, uncorrected).
- why it might matter: It decides whether to grow the representation or reshape costs, which is the representation co-evolution decision itself.
- later evidence: none found. Lane 2 is HELD with one deferred candidate.
- lenses: representation accessibility, genotype-phenotype anatomy
- related: H-D4-16, H-D4-31, H-D4-59

### H-D4-61 StackVM fitness effects are bimodal, and 23% of output-silent sites carry high hidden-state influence
- source: genesis/harmonia_a/d14/REVIEW_PACKET_FINAL_D14.txt:51 @ 6940805be (2026-09-01), seat Harmonia A (genesis); quote: "THE UNEXPECTED DISCOVERY (D-14C migration matrix): 333 of 1,457 / output-silent sites -- 23% -- carry HIGH hidden state influence"
- kind: anomaly
- question: Is the silent-or-catastrophic distribution of fitness effects robust to uniform-site sampling and a full trajectory ruler? Both rungs are blocked (D-14D). Does output-silent hidden-state variation act as cryptic variation that selection can later use?
- why it might matter: A landscape without gentle slopes reshapes search. Cryptic hidden-state variation is a candidate reservoir of neutrality.
- later evidence: none found. D-14D is blocked on the lack of a site-addressed endpoint.
- lenses: DFE, cryptic variation, stackvm, instrument gating
- related: H-D4-01, H-D4-02, H-D4-59

### H-D4-62 Active vs passive information: the confirmatory D15-A test was never run
- source: genesis/harmonia_a/d15a/D15A_PHASE0_REPORT.md:111 @ 82b023756 (2026-09-02), seat Harmonia A (genesis); quote: "2. Probe informativeness vs goal progress orthogonal? **UNTESTED**"
- kind: parked-experiment
- question: Does active probing beat passive observation for repair identifiability? Is probe informativeness orthogonal to goal progress? REVIEW_PACKET_D15A Q1 asks whether a graded dose-response (Z_8 x Z_8) is needed.
- why it might matter: It is whether evolved reasoners should be selected to experiment and not only observe, a core sagacity mechanism.
- later evidence: none found. Verdict SCIENCE_NOT_READY, with R-A/R-B sent to the operator.
- lenses: active learning, curiosity pressure
- related: H-D4-09

### H-D4-63 exp's one-class collapse: which rule-table entries fake competence?
- source: roles/Theophrastus/specimens/SPECIMENS_ROUND2_2026-09-14.md:120 @ 1b067751f (2026-09-14), seat Theophrastus; quote: "UNKNOWN at the rule-table level: which entries of exp's table produce the collapse cannot be tested without a table-level ablation/ substitution intervention (THEO-REQ-005)."
- kind: parked-experiment
- question: Which entries produce exp's N-dependent collapse to "all ones", which appears between N=149 and 599 and saturates by 999? A companion is the particle1 non-convergence outlier (roles/Herakles/todo_2026-09-16.md:35 @ bfe8f0bd8: "100 of 149 cells still flipping at T = 298"), whose replication on 5 more IC seeds was never run.
- why it might matter: It maps an evolved rule that scores like a constant classifier from genotype to phenotype. Deception detection of this kind is needed before any evolved-competence claim.
- later evidence: Herakles delivered derive_edit/derive_flip (bfe8f0bd8, 2026-09-16). No ablation was run, and Theophrastus has been inactive since 2026-09-14.
- lenses: genotype-phenotype map, ablation, evolved-rule dynamics
- related: H-D4-18, H-D4-01

### H-D4-64 Does the signed-margin response curve transport beyond density CA (a principled difficulty knob)?
- source: roles/Theophrastus/specimens/SPECIMENS_ROUND2_2026-09-14.md:71 @ 1b067751f (2026-09-14), seat Theophrastus; quote: "values. To other kinds: UNTESTED (needs a scalar sufficient statistic / of the input; eca_rule_eval_v1 has no classification task)."
- kind: open-question
- question: Does "accuracy = sum_k P_ens(k) * c(k)" generalize, so that a task ensemble acts on a phenotype only through a scalar statistic? Is the maj boundary shift m*(N) (THEO-CAND-003, line 143) real at about 10x more ICs?
- why it might matter: A curve that transports would give graded, principled pressure design for curricula.
- later evidence: it transported across consumers (150/150 Vivarium fossils, THEO-14). No transport to other kinds.
- lenses: curriculum design, pressure calibration
- related: H-D4-30

### H-D4-65 Metis: does composing evidence channels beat the best single channel?
- source: roles/Metis/season1/SEASON1_RECEIPT.md:130 @ f9f90c0f7 (2026-09-13), seat Metis; quote: "single-channel selection -- P-5 was never tested, because no single-channel"
- kind: unfollowed-recommendation
- question: Out of sample, does a composition of channels beat the best single channel? Does a blind second encoder's rules_out coding flip any episode (F4)?
- why it might matter: Correlated channels made agreement anti-predictive in the greedy-LoRA case. Whether the lab's own evidence composition works is a question about its reasoning instrument.
- later evidence: none found. Season 2 is "RECOMMENDED, NOT STARTED", and there are no Metis commits after 2026-09-13.
- lenses: evidence composition, correlated channels
- related: H-D4-66

### H-D4-66 Hypatia G5 grounding gate abstains on half the failure corpus
- source: roles/Hypatia/science/season1/REPORT.md:77 @ 1bd2a903c (2026-09-11), seat Hypatia; quote: "A gate that abstains on half its inputs is not a gate yet."
- kind: defect-ambiguity
- question: Is the failure record (autopsy prose with specific-density 0.42-0.64 against a 0.50 floor) mechanically ungroundable as written? Would changing the recording format or the gate catch confabulation?
- why it might matter: "Failure is evidence" only works if failure records can be checked. This concerns the representation of failure itself.
- later evidence: none found. HYPATIA-03 re-premise is open, with no commits after 2026-09-11.
- lenses: grounding, failure-record epistemics
- related: H-D4-65, H-D4-39

### H-D4-67 D-18 companion: the H2 injection semantics second arm (k-port below majority)
- source: roles/Archaeon/H0H5_STATUS.md:51 @ 6fc3ea619 (2026-09-11), seat Archaeon (recording Herakles); quote: "alternative 2 (k-port injection with k bounded / below the majority threshold) as a separately labelled second arm later."
- kind: parked-experiment
- question: Does distributed k-port injection below the majority threshold give a density CA readable memory where single-port injection provably cannot?
- why it might matter: It tests whether the obstruction concerns the port geometry or the substrate. That is the difference between a dead line and a mis-coupled one.
- later evidence: none found. Only alternative 1 was approved (archaeon/docs/expansion/DECISIONS.md:52), and neither arm was run under its own identity.
- lenses: herakles ca_stream, injection semantics
- related: H-D4-18, H-D4-19

### H-D4-68 Cross-engine lens field: record varied= / observed= so convergence between engines becomes measurable
- source: roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md:66 @ 95fff9111 (2026-09-25), seat Archaeon; quote: "**varied=** (environment | representation | physics | organism-boundary | memory | communication | improver),"
- kind: directive-idea
- question: If every engine's experiment record declares what it varies and what it observes, can seat convergence (for example, three Z80 builds from one directive) be detected and justified or merged? Atlas indexes none of z80atlas/census/envgate/envgate2 (harvest/archaeon_campaigns.py:59).
- why it might matter: It is instrumentation for the ecology of engines itself. It guards against the operator's concern that seats collapse into one modality, and it makes cross-engine differentials findable.
- later evidence: partial. Contract v0.2/v0.3 (949b9ba4d, 194c51193) standardise WHO/WHERE/WHAT across Archaeon, BEE and NPE for one assay. No Atlas field was added, and Bellerophon's ATLAS_EXTENSION_PROPOSAL.md remains unapplied.
- lenses: Atlas registry, causal_lens contract, cross-engine standard
- related: H-D4-23

### H-D4-69 Syntax cannot reach function: is any endogenous (semantic/geometric) relevance key capable?
- source: ew.claims id=C-1f7991001445 (agent_d10, NOT_ESTABLISHED); quote: "Not evidence that endogenous relevance keying is impossible ... it retires this interface; seven unresolved contamination threats listed."
- kind: open-question
- question: Would an endogenous relevance key that is semantic or behavioural rather than syntax-only pass the frozen capacity gate, with the seven contamination threats closed?
- why it might matter: How organisms find the relevant prior material is itself a representation that should be under selection.
- later evidence: none found. This narrows H-D4-08 (the execution-bridge variant) to the generic question.
- lenses: retrieval keying, representation learning
- related: H-D4-08, H-D4-34

### H-D4-70 C5 boundary verdict untested where it could show: tuned crossing rate, ADDRESS-level FAIL boundary
- source: archaeon/campaign5/CAMPAIGN_REPORT.md:177 @ cdb55e152 (2026-09-18), seat Archaeon; quote: "headroom. Not established: anything about worlds that evolution CAN / climb (no arm climbed any); anything about longer runs, larger N, or / a grammar whose crossing rate is tuned; whether a FAIL boundary at the"
- kind: future-work
- question: Would a grammar with a tuned crossing rate, or an ADDRESS-level FAIL boundary (rejected in D5-007), change BOUNDARY_CREATED_NO_DISCOVERY_GAIN?
- why it might matter: It is the evolvability-by-bounded-variation claim tested only where it could not show up. It connects C5 to the Proteus neutral-graph and lane-2 lines.
- later evidence: the operator closure (campaign5 s6a, lines 206-208) redirects to "alter generative/search structure". No direct test was found.
- lenses: Representation B (repb), WORLD_SCREEN, C5-10 RULE
- related: H-D4-27, H-D4-59, H-D4-60

## Kind counts
open-question 18; parked-experiment 14; unfollowed-recommendation 10; anomaly 9; defect-ambiguity 5; directive-idea 5; contradiction 3; prior-art-gap 3; future-work 3 (total 70).

## Cross-domain pointers
- ops/threads TH-001..TH-006 (Archaeon/ops pilot): H-D4-23 duplicates TH-003 at the assay level, AN8 is TH-004 (not repeated here), and H-D4-25 sits in TH-001:15. Whoever owns ops threads should decide whether H-D4-24 (AN2) becomes TH-007.
- NPE / Nestor (primordial, roles/Nestor): H-D4-47 (cw01-e05 component pricing) and H-D4-23 (P-11 host-conditioned). Not in D4.
- BEE / Bellerophon (prometheus/z80atlas, atlas_bee): H-D4-23 and H-D4-68 (unapplied ATLAS_EXTENSION_PROPOSAL.md).
- Atlas (atlas/, harvest/archaeon_campaigns.py:59): the indexing gap in H-D4-68.
- Ares (ares/runs/sweep_c2 W16 files): H-D4-56 can be answered by reading existing data.
- Aporia deck (3b1fb8a0f, vivarium branch): four of six H0-H5 hypotheses are untested in the literature as posed. It is the prior-art source for H-D4-18 and H-D4-20.
- Diomedes (ew.claims C-3c0f5fc710c0): H-D4-38.
- Elenchus (Kashtan-Alon MVG adjudications): H-D4-44.
- Daedalus engine: nk_landscape_v0 permutation convention undeclared (roles/Vivarium/BACKLOG_H0H5.md:70). A silent inverse is undetectable from outputs. This is an instrument chore, but it gates any NK science.
- Vivarium registry: random_walk_v0 step_scale is a pure rescaling (roles/Vivarium/INBOX_HERAKLES_DEGENERACY_AND_BACKEND_2026-09-06.md:47). It is an exact analytic null that could serve as a free positive control for variance detectors.
- Comms base-rate item (comms.messages id=96/103, Clio orphan producer), ops domain: queued as a sweep, no result found.
