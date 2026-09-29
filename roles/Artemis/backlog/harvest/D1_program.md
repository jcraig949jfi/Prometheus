# D1 PROGRAM-LEVEL harvest -- candidate research Threads (Artemis Block A)
domain: D1 program level (ops/, Archaeon program docs, Harmonia, Aporia, Cyclops + Selective Irreversibility, Atlas, Chiron synthesis, Elenchus, Kairos, Charon, docs/, charter/README).
paths covered: ops/{threads,campaigns/C-001,initiatives}; roles/Archaeon/{ENGINE_LANDSCAPE,H0H5_STATUS,EXPANSIONS,TODO,BACKLOG_H0H5,REVIEW_PACKET_*,BLOCKED_*,prompts/2026-09-*}; archaeon/{docs,z80atlas/pivot,causal_lens/pivot,envgate2,frontier/DECISIONS.md}; roles/Harmonia/{VACUOUS_READINGS,RESUME_20260925,todo_20260925,AUDIT_*,REVIEW_PACKET_*}; roles/Aporia/{STATUS,BACKLOG_H0H5,DISSENT_LEDGER}, aporia/lot; programs/selective_irreversibility/* (incl. memo/); roles/Cyclops/STATUS; roles/Atlas/{theory,proposals,reports}; origin/chiron/base-role-adopt-2026-09-21 SYNTHESIS_DIRECTIVE; roles/Elenchus epistemic-debt LEDGER; roles/Kairos/{ARCHAEOLOGY,science/FAILURE_SURFACE_v0,BACKLOG}; roles/Charon/reviews/KILL_LIST; docs/essays; whitepapers/descriptor_collapse*; CHARTER_AND_CONTINUITY.md; README.md; roles/Artemis/threads/sfe_retrospective/THREADS.md; origin/archaeon/deep-block-2026-09-27 (checked as later evidence).
paths NOT covered: aporia/docs/deep_research_* (other domain); aporia/{mathematics,physics,...} subject folders; Harmonia/Aporia/Kairos session journals before 2026-09; roles/Harmonia/science, qualification code; roles/Charon/apollo_e9; docs/notebook_lm, docs/prompts; roles/Atlas/proposals/2026-09-19 ECOSYSTEM_CANDIDATES (skimmed only); archaeon campaign1-6 internal READOUTs (read only via their review packets); Postgres (not queried).
method: read-only. Keyword greps (unresolved|open|parked|deferred|untested|INDETERMINATE|QUESTIONS FOR THE REVIEWER) over the paths; read every ops thread, E-001/E-002 RESULT, review-packet question sections, SI program files, Atlas theory JSONL; for each candidate checked later commits on origin/* (git log --remotes=origin, -S, --grep) for answers/supersession.
counts: 68 candidates. open-question 23, anomaly 6, unfollowed-recommendation 8, parked-experiment 10, contradiction 1, prior-art-gap 6, directive-idea 9, defect-ambiguity 4, future-work 1.
note: 3 of the 6 TH-00x threads were re-scoped the same day on seat branch origin/archaeon/deep-block-2026-09-27 (72923db05, NOT on main); that branch also opens TH-007..TH-011, harvested here as H-D1-11..14.
note: ANSWERED/superseded items found during the sweep (not listed as candidates): SI equivalence margin (answered by operator LM01 rulings 1426c8e2e), SI "accessible" reading (resolved DISAGREEMENTS.md:28), PTE-C1 M3 ablation anomaly (answered by C1b cc98596dd), seeded-moat ledger (closed 6878f582d), copier prior (COPIER-CENSUS-01 c5067fac6).
convention: "seat" = the seat that authored the source; line numbers are at worktree tip d7ec26d37 unless a branch is named.

## A. ops/ threads and campaign C-001 (causal lens)

### H-D1-01 What constitutes heredity, authorship and identity when their carriers separate
- source: ops/threads/TH-001.md:7 @ 0a5c0895d (2026-09-27), seat Archaeon; quote: "What actually constitutes heredity, authorship, replication and identity when body, executor, code location, code material, inherited material and counterfactual causal power can separate?"
- kind: open-question
- question: as stated; the umbrella of TH-002..TH-006.
- why it might matter: every replication/lineage verdict in BEE, NPE, Archaeon and PTE depends on which referent is counted; three engines have already reversed claims on this (FF-1, AN1, FF-31).
- later evidence: origin/archaeon/deep-block-2026-09-27 ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/B_B1_B6_B8.md (72923db05) proposes a three-axis taxonomy CARRIER / RELATION / CONTRAST plus aggregation; not reviewed, not on main.
- lenses: causal lens (contract v0.3), BEE, NPE, Archaeon z80atlas, PTE
- related: H-D1-02..05, 07..14, 64, 66

### H-D1-02 Does BEE's native SR criterion under-count self-replication run from self-copied code?
- source: ops/threads/TH-002.md:4 @ c310bf6ad (2026-09-27), seat Archaeon; quote: "does BEE's native SR criterion (copy ops with pc < L, a WHERE reading) under-count self-replication that runs from the writer's own self-copied code in the window (a WHAT reading)?"
- kind: defect-ambiguity
- question: as stated; and does it change any BEE run- or family-level verdict?
- why it might matter: r038751 had 27,083 location-foreign but own-material births; BEE SR "CONFIRMED_CAUSAL" tallies may be systematically low where code relocates.
- later evidence: deep-block F_FRONTIER.md (72923db05, branch only) sharpens it and folds the sample into TH-010 (random sample of 20 BEE runs on ubu nodes, ~30 CPU-min). Not run. Needs Bellerophon coordination.
- lenses: BEE z80atlas, causal lens codeprov_replay
- related: H-D1-01, 05, 12 (TH-010), 06 (evidence only on M2)

### H-D1-03 Is NPE host-conditioned reproduction caused by the donor executing host material as code?
- source: ops/threads/TH-003.md:4 @ c310bf6ad (2026-09-27), seat Archaeon; quote: "is NPE's host-conditioned reproduction (the donor cannot rebuild a random victim) CAUSED by the donor depending on the host's material as code (cross-execution), or only associated with it?"
- kind: open-question
- question: as stated (46% vs 11% cross-execution, 34 births, one specimen).
- why it might matter: host-mediated reproduction is the lens's most novel mechanistic lead; if causal it is a new reproduction mode (parasitism-like) shared across substrates.
- later evidence: deep-block F_FRONTIER.md (72923db05) DEMOTES TH-003 and recommends the host-conditioned assay be re-rated NOT_READY until the NPE arm is restated on P-11-causal/"overwrite" events. Operator ruling needed before any prereg (CAMPAIGN.md:13).
- lenses: NPE (Nestor z80atlas), causal lens, HOST_CONDITIONED_ASSAY_READINESS
- related: H-D1-04, 13 (TH-009), 22 (CONTRACT_V02 Q4)

### H-D1-04 NPE births where blocking the donor's writes still yields a donor-like victim (AN8)
- source: ops/threads/TH-004.md:4 @ c310bf6ad (2026-09-27), seat Archaeon; quote: "Is that self-conversion by the victim, a measurement artifact of the ordinary donor-disabled re-execution, or pre-existing similarity (median initial fidelity 0.625)?"
- kind: anomaly
- question: in 11/34 pair-tape births the donor's writes were not necessary; which of the three explanations, and is NPE's native parent label supported there?
- why it might matter: if the victim self-converts, NPE "births" include a non-reproductive process and the native parent label is wrong for a third of events.
- later evidence: none found (carried unresolved through E-001 RESULT.md:37 and CONTRACT_V02_REVIEW Q3).
- lenses: NPE, causal lens
- related: H-D1-03, 13

### H-D1-05 Where is the BEE code that executes at pc >= 2L, and what material is it?
- source: ops/threads/TH-005.md:4 @ c310bf6ad (2026-09-27), seat Archaeon; quote: "528,897 own-sourced copy writes (66,669 in r038751) were performed by code at pc >= 2L, outside both the writer's region and the window."
- kind: anomaly
- question: input/output area or wrap-around; does it change the WHO/WHERE/WHAT reading of those births?
- why it might matter: half a million copy writes are outside the modelled regions; the probe says NOT_IDENTIFIABLE, so any BEE authorship census has a blind band.
- later evidence: none found.
- lenses: BEE, causal lens B6 probe
- related: H-D1-02, 12

### H-D1-06 Which verification artifacts can be made portable so nodes verify as well as execute?
- source: ops/threads/TH-006.md:7 @ e40904023 (2026-09-27), seat Archaeon/Odysseus; quote: "Question: which verification artifacts can be made portable (committed hashes, compact reference fixtures like archaeon/tests/fixtures_v03/, content-addressed copies), so that a node can verify as well as execute"
- kind: open-question
- question: as stated (operational, but it gates every cross-host replication).
- why it might matter: "compute was portable and evidence was not" -- every "science unchanged" check in C-001 ran on M2; residue unreachable off-host cannot feed future search.
- later evidence: roles/Odysseus/th006/REPORT.md (e40904023): a 10,970-byte pack lets ubu001 verify T-001 with no M2 file; M2 attestation of the preserved log hash still open; fd7ca4fde (platform defect: artifacts > 1 MiB verified then silently discarded).
- lenses: C-001 recipe, BEE/NPE preserved evidence, git
- related: H-D1-63 (T3), 62 (T2), 60

### H-D1-07 Does rule C-OP' (collapse identical contributors, lift ILL_POSED past an operator null) hold beyond PTE, and what is the null for a privileged operator?
- source: ops/campaigns/C-001/E-002/RESULT.md:42 @ 0a5c0895d (2026-09-27), seat Artemis (E-002 worker); quote: "**Proposed rule C-OP'** (a proposal for a future contract revision; NOT adopted, and NOT tested outside PTE):"
- kind: open-question
- question: C-OP' in a second substrate; the null for privileged (non-exchangeable) operators; F2 thin-margin cases (RESULT.md:61-63); choice of alpha (0.005 vs 0.05 untuned).
- why it might matter: decides when a singular parent lineage is meaningful at all under recombination; nearly every PTE recombinant currently has none.
- later evidence: origin/archaeon/deep-block-2026-09-27 archaeon/causal_lens/deep_block/cop_prime_attack.py and A_E002_REVIEW.md (72923db05) attack C-OP' clause (b): a per-child FLOW share compared with a population null calls a byte-identical child ILL_POSED. Not merged.
- lenses: causal lens contract, PTE, NPE, Archaeon
- related: H-D1-08, 09

### H-D1-08 FLOW vs DIFFERENCE: two referents of "material contribution" (candidate B8)
- source: ops/campaigns/C-001/E-002/RESULT.md:69 @ 0a5c0895d (2026-09-27), seat Artemis; quote: "**Contribution has two referents: FLOW vs DIFFERENCE.** FLOW asks which source the operator copied a unit from (mask, taint)."
- kind: contradiction
- question: which referent should continuity/identity vs genealogy questions use; PTE v0.1 counted DIFFERENCE, FF-33 switched to FLOW, NPE v0.2 uses DIFFERENCE.
- why it might matter: a "correction" that silently swaps referents changes 11/16 vs 1/16 outcomes; same pattern as B4/B6.
- later evidence: deep-block B_B1_B6_B8.md (72923db05, branch): "No as a distinction; yes as a lesson" -- recorded as the RELATION axis (identity-by-state vs identity-by-descent); CONTENT questions use DIFFERENCE, genealogy uses FLOW. Unreviewed.
- lenses: causal lens, PTE, NPE, BEE (FF-4/FF-27)
- related: H-D1-01, 07

### H-D1-09 A non-saturating criterion for architecture continuity under recombination (B7)
- source: ops/campaigns/C-001/E-002/RESULT.md:64 @ 0a5c0895d (2026-09-27), seat Artemis; quote: "**Architecture continuity under recombination has no usable criterion** in PTE: behavioural ones saturate, and graded ones track fitness."
- kind: open-question
- question: what structural or non-saturating behavioural probe can identify architecture continuity when champions sit at the ceiling?
- why it might matter: every "same architecture / same lineage by behaviour" claim is confounded with fitness; blocks any study of architectural inheritance in recombining populations.
- later evidence: archaeon/causal_lens/OBSERVATORY_DESIGN.md:80 (949b9ba4d) asks PTE for "a non-saturating behavioural probe set (worlds where perfect champions differ)"; deep-block C_B7.md (72923db05, branch). No probe built.
- lenses: PTE (Ananke), causal lens, any QD/behaviour ruler
- related: H-D1-24 (C4 Q2 finer distance)

### H-D1-10 Interpretive degrees of freedom when a fresh worker formalises a named-but-unstated criterion
- source: ops/campaigns/C-001/E-002/HANDOFF_FINDINGS.md:11 @ 0a5c0895d (2026-09-27), seat Artemis; quote: "**The candidate criterion was named, never stated.** ... T-007 had to formalise it ... A different worker could formalise it differently."
- kind: open-question
- question: how much do conclusions vary across independent workers formalising the same criterion from Git alone? (M1-M3 acceptance tests were worker-supplied.)
- why it might matter: an unmeasured "formaliser variance" sits under every adjudication handed between seats; the ops pilot assumes Git carries the science.
- later evidence: ops/campaigns/C-001/E-002/RELAY_NOTE.md (79d80877f) records handoff observations; no second independent formalisation attempted.
- lenses: ops handoff protocol, causal lens, any preregistration
- related: H-D1-06, 58 (maturity ladder)

### H-D1-11 Cargo erosion vs machinery conservation in copy-selected byte worlds (TH-007)
- source: origin/archaeon/deep-block-2026-09-27:ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:7 @ 72923db05 (2026-09-27), seat Archaeon; quote: "Is 'the copy core is conserved, cargo erodes unless paid for' a law of copy-selected byte worlds, and what is the minimal coupling that preserves cargo?"
- kind: open-question
- question: as stated.
- why it might matter: if general, it explains why functional payloads vanish in replicator soups -- a direct North-Star constraint on growing useful machinery on top of copying.
- later evidence: NPE C-CORE (programs/selective_irreversibility/EXPERIMENTS.md:126-146, 76061ddd9) shows founder core conserved, 13-25% founder bytes; BEE endogenous task decay; Archaeon only inferred. Thread file not on main.
- lenses: NPE, BEE, Archaeon block-13
- related: H-D1-38 (C-CORE circular relevance), 26 (copying gap)

### H-D1-12 Harness-copy hazard as a general reproduction-ruler law (TH-008) and code-referent scale (TH-010)
- source: origin/archaeon/deep-block-2026-09-27:ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:8 @ 72923db05 (2026-09-27), seat Archaeon; quote: "Can every reproduction ruler be required to enumerate all channels that move material (harness, migration, splice, transplant) and show zero credit leak?"
- kind: directive-idea
- question: can a synthetic leak fixture per known channel force every contract to name non-organism carriers; and (TH-010) how often population-wide does code LOCATION misattribute MATERIAL?
- why it might matter: three teams made the same error independently; a ruler-level check would prevent recurrence across all engines.
- later evidence: branch only; no fixture written.
- lenses: all reproduction rulers, contract v0.3 validator
- related: H-D1-02, 64 (T5 failure catalogue)

### H-D1-13 Reproduction vs copying: which "reproductions" transmit the capacity to reproduce? (TH-009)
- source: origin/archaeon/deep-block-2026-09-27:ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:9 @ 72923db05 (2026-09-27), seat Archaeon; quote: "Which recorded 'reproductions' transmit the CAPACITY to reproduce, not just material?"
- kind: prior-art-gap
- question: as stated (Griesemer's reproducer concept); no engine records capacity transmission per event.
- why it might matter: separates heredity of machinery from material flow; relevant to Atlas P-copy-not-heredity.
- later evidence: branch only; cheapest step named (run block-13 children through the frozen copier ruler).
- lenses: Archaeon, NPE (P-11), BEE, Atlas propositions
- related: H-D1-03, 04, 49 (P-copy-not-heredity via Atlas)

### H-D1-14 Does counterfactual dependence fail to chain where lens errors cluster? (TH-011)
- source: origin/archaeon/deep-block-2026-09-27:ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:10 @ 72923db05 (2026-09-27), seat Archaeon; quote: "Do lens errors cluster where a counterfactual-dependence result was chained like a production (flow) result (Hall)?"
- kind: prior-art-gap
- question: as stated (untested prediction from Hall's two concepts of causation).
- why it might matter: a methodological law for every causal ruler in the ecology; cheap to test on the false-friends ledger.
- later evidence: branch only.
- lenses: causal lens FALSE_FRIENDS FF-1..34
- related: H-D1-08, 64

## B. Archaeon program (Z80, ENVGATE, campaigns, frontier)

### H-D1-15 The five unexplained BAND0 establishments in ENVGATE-02's all-blocked arm
- source: archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md:20 @ 13cdec715 (2026-09-26), seat Archaeon; quote: "**The five BAND0 establishments.** Genetic establishments in the all-blocked arm, against a planned ~0.7 total. ... They stay unexplained, and no campaign will be spent on them now."
- kind: anomaly
- question: how did 5 genetic establishments occur (vs ~0.7 expected) when the environmental window was fully blocked?
- why it might matter: a 7x excess under the block implies a second route to reproductive access the gating model does not contain; "failure is evidence".
- later evidence: operator ruling roles/Archaeon/prompts/2026-09-26_portability01/00_OPERATOR_RULING_verbatim.md retains them as fossils, "not an allocation target"; TH-001 table row. No analysis.
- lenses: Archaeon envgate2, causal lens genetic attribution
- related: H-D1-16

### H-D1-16 Random-inflow ecology (RIE-01): staged, unfrozen, precondition failed
- source: archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md:16 @ 13cdec715 (2026-09-26), seat Archaeon; quote: "| RIE-01 | **correctly NOT launched.** Its precondition, the Phase-C gate, failed. It stays staged and unfrozen | archaeon/rie/ |"
- kind: parked-experiment
- question: does continuous random inflow make copier emergence common, merely possible, or invisible (operator 2026-09-23 path "decide from measured copier density whether a new random-inflow ecology is warranted")?
- why it might matter: the only designed test of open-ended origination in the Z80 family; census sizing says ~7e5 inflow tapes per surviving lineage (vmcopy32).
- later evidence: archaeon/rie/ code only (87f51c5ee); no run. Z80ATLAS_RULINGS_FOLLOWUP_REVIEW:239-257 gives inflow sizing.
- lenses: Archaeon rie, z80atlas census
- related: H-D1-15, 17, 26

### H-D1-17 Copier census limits: survival/conversion from one event; no copiers arising by mutation in-world
- source: archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:232 @ 863d34a55 (2026-09-23), seat Archaeon; quote: "- Measure survival/conversion properly (1 event). / - Measure copiers arising by mutation during a world's life, or ones that"
- kind: future-work
- question: what is the copier-founder -> surviving-lineage conversion rate, and the in-life mutational origin rate; and (Q1 line 263) should the model predict survivors rather than copier-worlds given 1/256 input gating?
- why it might matter: the "lottery explains the 1/27,141 survivor" conclusion rests on a conversion estimate from a single event.
- later evidence: ENVGATE-01/02 tested the gating dimension, not conversion; none found for conversion.
- lenses: z80atlas census, ENVGATE
- related: H-D1-16

### H-D1-18 Matched controls that change pressure in 40% of EXTERNAL treatments
- source: archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:198 @ 863d34a55 (2026-09-23), seat Archaeon; quote: "RESTRICTED means grammar.matched_controls still changes pressure (it drops / recombination/explicit_fitness) in 1,331 of 3,351 simulated EXTERNAL treatments (40%). The / fix belongs in the control constructor or the scorer, and is left for the"
- kind: defect-ambiguity
- question: which Z80xAtlas reproduction-via-matched-control contrasts are confounded by the control dropping pressures, and how should matched controls be constructed in factor grammars?
- why it might matter: "reproduction advantage" readings in the 72 h campaign may partly be pressure removal.
- later evidence: preflight gate forces recorded acceptance (a6b66ea96); fix not made; no later adaptive Z80 campaign.
- lenses: z80atlas grammar/preflight, any factor-grammar engine
- related: H-D1-19

### H-D1-19 Support/identifiability preflight for every factor-grammar campaign (beyond Z80)
- source: roles/Archaeon/prompts/2026-09-23_postcampaign_rulings/00_OPERATOR_RULINGS.md:21 @ 29b03fd80 (2026-09-23), seat Operator via Archaeon; quote: "That lesson is bigger than Z80: Atlas-style factor grammars need a preflight that detects structural coupling caused by constraints."
- kind: unfollowed-recommendation
- question: can a generic preflight prove each intended causal comparison has support in the sampled grammar, for BEE, NPE, CWE, WTP, PTE designs?
- why it might matter: the random_spec starvation bug silently removed a contrast (0/209 topology draws); other engines' samplers are unaudited.
- later evidence: archaeon/z80atlas/preflight.py (a6b66ea96) Z80-only; no cross-engine adoption found.
- lenses: all engines with sampled designs
- related: H-D1-18, 64

### H-D1-20 Is Archaeon a portable lens, and should seats' convergence be made measurable (varied/observed field)?
- source: roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md:69 @ 95fff9111 (2026-09-25), seat Archaeon; quote: "3. Add the lens field (varied/observed) to Atlas's standard?"
- kind: directive-idea
- question: operator's concern that seats "collapse into very similar modalities"; proposed per-experiment varied= / observed= pair so two engines on the same pair must justify or merge.
- why it might matter: an instrument for the ecology's own diversity -- the North Star needs differently biased "puddles", and convergence is currently unmeasured.
- later evidence: Q1 partly answered by PORTABILITY-01 (PORTABLE_WITH_DOMAIN_LIMITS); Q3 not adopted (Atlas parked; REPORT_2026-09-25 lists 15 engines, 4 with experiments).
- lenses: Atlas registry, all engines
- related: H-D1-66 (T6 triplication), 63 (T3), 57 (monoculture)

### H-D1-21 Three campaigns, zero supported positives: are the gates or the substrate at fault?
- source: roles/Archaeon/REVIEW_PACKET_WSE_ARCHITECTURE_2026-09-17.md:600 @ 503fcf5b7 (2026-09-17), seat Archaeon; quote: "Q6  Three campaigns, zero supported positives. Is that evidence of /      epistemic discipline, or of a system that cannot produce a result /      strong enough to survive its own gates"
- kind: open-question
- question: as stated; plus Q3 (line 585) whether a bounded LD/ST tape is the right substrate for working memory at all.
- why it might matter: a program-level calibration question: if gates are unattainable for this substrate class, negative results carry no information.
- later evidence: campaigns 4 and 5 closed "not worth continuing" (REVIEW_PACKET_CAMPAIGN4/5, 2026-09-18); pivot to Z80 (DF-016). Never answered as asked; no attainability audit of the gates.
- lenses: Archaeon WSE/SSF, Harmonia qualification
- related: H-D1-27 (D-A01), 29 (H0-H5 vacuous)

### H-D1-22 Is READY_WITH_ENGINE_SPECIFIC_LIMITS too generous for the host-conditioned assay?
- source: archaeon/causal_lens/pivot/CONTRACT_V02_REVIEW_2026-09-27.md:273 @ aede495ad (2026-09-26), seat Archaeon; quote: "Q4 Is READY_WITH_ENGINE_SPECIFIC_LIMITS too generous, given BEE needs a new harness and NPE continuity is NI in 25/34?"
- kind: open-question
- question: as stated.
- why it might matter: the assay is the only intervention that can make TH-003 causal; mis-rated readiness wastes a preregistration.
- later evidence: deep-block F_FRONTIER.md (72923db05, branch) recommends NOT_READY -- effectively answers "yes, too generous" pending review.
- lenses: causal lens, NPE, BEE
- related: H-D1-03

### H-D1-23 Gradient-free vs rare-but-climbable: what separates a lottery from a search floor?
- source: roles/Archaeon/REVIEW_PACKET_SSF_C1-3_2026-09-16.md:270 @ 37ca43bd4 (2026-09-16), seat Archaeon; quote: "Q4. Is 'search floor' the right reading of 0/60 and 2/9, or is it that /     the 4-bit exact-match reward has no gradient at all and any success /     is a lottery? What experiment separates gradient-free from"
- kind: open-question
- question: as stated.
- why it might matter: the same distinction underlies Crius's accessibility frontier and the Z80 founder lottery; a general assay would classify null campaigns.
- later evidence: none found as an assay; Crius C2 (7069c0ce6) measured foothold density for one primitive.
- lenses: SSF/WSE, Crius, z80atlas
- related: H-D1-44, 45

### H-D1-24 Would a finer behavioural distance turn a displacement cliff into a slope?
- source: roles/Archaeon/REVIEW_PACKET_CAMPAIGN4_2026-09-18.md:169 @ b5ce944f3 (2026-09-18), seat Archaeon; quote: "Q2  The displacement metric is a Hamming distance over answer vectors /       on 16 episodes. Could a finer behavioural distance turn the cliff /       into a slope?"
- kind: open-question
- question: as stated (damage-geometry maps).
- why it might matter: whether robustness landscapes are cliffs or slopes is ruler-dependent; relevant to B7 saturation.
- later evidence: none found (campaign closed).
- lenses: Archaeon campaign4/5 damage geometry
- related: H-D1-09

### H-D1-25 Deep Frontier P-boom: population capture inverts spiking under shared streams; bimodal shuffle arm
- source: archaeon/frontier/DECISIONS.md:199 @ c7610ea19 (2026-09-19), seat Archaeon; quote: "The within-arm spread dwarfs the between-arm difference; no order reading."
- kind: anomaly
- question: readout 2 (939e4f39e): K_F_popcapture 0.33 vs 5.17 independent-stream, K_B_shuffle bimodal (possible phase transition); N=3 insufficient. Is there a real interaction?
- why it might matter: the only Deep Frontier lineage with an arm-level signal; also exposed a hidden-seed defect (experiment_id as seed) that may exist elsewhere.
- later evidence: 939e4f39e (2026-09-21) readout 2 PROVISIONAL; frontier scheduler touched 1049aac73 (2026-09-26); no readout 3 found.
- lenses: archaeon/frontier, campaign6 segment
- related: H-D1-64 (hidden seed as failure class)

### H-D1-26 Observatory recall: planted blind-spot fixtures before worlds exist (Campaign 6)
- source: roles/Harmonia/todo_20260925.md:27 @ c09c9891e (2026-09-25), seat Harmonia; quote: "HARM-52  author the planted blind-spot fixtures with Nemesis (>= 3 per"
- kind: parked-experiment
- question: what fraction of planted phenomena does the observatory (eleven detectors) recover, at a recall threshold fixed before reveal?
- why it might matter: the only designed measurement of the ecology's detection recall -- without it "nothing found" cannot be distinguished from "could not see".
- later evidence: BLOCKED on operator Q4/Q5; Campaign 6 effectively superseded by Deep Frontier/Z80 (DF-016). none found.
- lenses: Harmonia qualification, archaeon/campaign6 observatory, Nemesis
- related: H-D1-51 (parent-child detectors), 59

### H-D1-27 Return the witness: what an organism can observe of its own failure
- source: roles/Archaeon/EXPANSIONS.md:35 @ 4322225c3 (2026-09-07), seat Archaeon (Herakles C-2); quote: "C-2 return the witness: WHICH positions disagreed, not only the match count | result carries a count | CEGAR/CEGIS/BMC/L2S, 5 templates; the first ACTIONABLE signal an organism could observe"
- kind: unfollowed-recommendation
- question: does giving evolving organisms the counterexample (not just a score) change what they can learn from failure?
- why it might matter: "failure is evidence" at the organism level, not just the experimenter's; a primitive the North Star asks us to supply.
- later evidence: PROPOSED, never built; SFE path retired. none found in post-SFE engines.
- lenses: SFE (retired), any task-scored engine (WTP, PTE, Aphrodite)
- related: H-D1-30 (H1 failure transport)

### H-D1-28 Does S17 prospective fragility transport to a corpus that can carry it?
- source: archaeon/docs/STAGE0_RESULT.md:18 @ ecfef4d87 (2026-09-05), seat Archaeon; quote: "substrate is uninteresting. Those questions remain open and untested."
- kind: parked-experiment
- question: Stage 0 KILLed on corpus structure (zero eligible claim-units); whether fragility exists or S17 rules transport is untested.
- why it might matter: a frozen, qualified primitive sits unused; the post-SFE engines produce within-world repeated observations that might now be eligible.
- later evidence: none found.
- lenses: Archaeon S17, any engine with repeated in-world observations
- related: H-D1-60 (T1 SFE archive)

## C. H0-H5 and representation/abstraction lines

### H-D1-29 The H0-H5 hypothesis set produced only vacuous readings; which interactions produce cumulative benefit?
- source: CHARTER_AND_CONTINUITY.md:90 @ d06e0130e (2026-09-10), seat Operator/Archaeon; quote: "**Open question:** Which interactions, on which substrates and timescales, produce repeatable cumulative benefit after full accounting?"
- kind: open-question
- question: H1 (V-003), H0 phase 2 (V-004), H2 (V-001), H5 (V-005) are all registered VACUOUS in roles/Harmonia/VACUOUS_READINGS.md; H3/H4 never reached a campaign. What would a corpus that can answer them look like?
- why it might matter: the charter's founding hypotheses (failure transport, retention, adaptive challenge, learned decoders) have never been tested with power; they are core North-Star mechanisms.
- later evidence: program pivoted to WSE (09-16) and Z80 (09-19); no reopening corpus built. Charon KILL_LIST_CAMPAIGNS_2026-09-11 documents why each read was void.
- lenses: Harmonia QR-1.2.1, Vivarium (down), Archaeon producer
- related: H-D1-30, 31, 21

### H-D1-30 Learned H5 decoder is indistinguishable from a random balanced permutation
- source: roles/Harmonia/VACUOUS_READINGS.md:66 @ f2c2452ea (2026-09-18), seat Harmonia; quote: "LEARNED balanced_7 read 11.7305. On the reach measure the learned decoder is indistinguishable / > from a random balanced permutation"
- kind: anomaly
- question: does any learned genotype-phenotype decoder improve access to useful variation beyond balance itself, on a map where the high bits are not inert?
- why it might matter: representation learning of the G->P map is a direct North-Star lever; the only measurement says "balance, not learning".
- later evidence: none found (KAIROS-15 attack of this claim never run).
- lenses: H5 ECA decoders, Harmonia QR bounds
- related: H-D1-29

### H-D1-31 H2: can bounded CA dynamics contribute causally to computation? (C3-3 GO, never run)
- source: roles/Harmonia/VACUOUS_READINGS.md:15 @ f2c2452ea (2026-09-18), seat Harmonia; quote: "V-001  H2: does descriptor-region            cs-c3-2 (C3-2): 120 acquired   every acquired rule is 0.000 on every"
- kind: parked-experiment
- question: C3-2 was STRUCTURALLY_VOID; C3-3 preflight passed option B (3a49ab0a4, corpus 180, GO predicate TRUE) but was never issued.
- why it might matter: the only designed test of stateful CA components as reusable computation; preflight shows the corpus CAN answer.
- later evidence: 3a49ab0a4 (2026-09-16) GO; HARM-19/20 "C3-3 readout, if Archaeon issues it" (todo_20260925.md); no run.
- lenses: Archaeon producer, Herakles CA, Harmonia D3
- related: H-D1-29

### H-D1-32 Stitch abstraction learning: "nothing parameterised" or "nothing could be"?
- source: roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md:125 @ 37b8ec8c8 (2026-09-11), seat Elenchus; quote: "C-06  STITCH LEARNS NOTHING PARAMETERISED        VERDICT: UNDERDETERMINED"
- kind: defect-ambiguity
- question: how many arity > 0 abstractions were structurally possible in 17 programs of 2-4 nodes; on what corpus does library learning produce parameterised abstractions from evolved programs?
- why it might matter: compression of evolved solutions into reusable abstractions is the representation half of the North Star; the headline null propagates without an attainable range.
- later evidence: none found.
- lenses: Techne stitch adapter, H1 solved programs, Aporia A3
- related: H-D1-33, 29

### H-D1-33 A3 attempt two: does reification (minting a reusable abstraction) earn its keep?
- source: roles/Aporia/BACKLOG_H0H5.md:44 @ d1d877b39 (2026-09-23), seat Aporia; quote: "APO-32 | A3 attempt two (amendment s9 allows two): preregister mechanism v2 (census over ALL minimal-size witnesses per early signature), a RETRIEVAL-ONLY memo control"
- kind: parked-experiment
- question: with a corrected census and a properly priced retrieval-only memo control, does promoting an abstraction pay on unseen later tasks?
- why it might matter: attempt one KILLED on a recall failure of the instrument, not on the idea; the SI memo also names it as the secondary lossless-memoriser countermodel.
- later evidence: aporia/lot/FINDINGS_A3_2026-09-11.md (attempt one); roles/Aporia/STATUS.md "A3 attempt two not started"; memo s7 (d50103524) cites it. none run.
- lenses: Aporia TINYPROG world, SI countermodel B
- related: H-D1-32, 34, 40

### H-D1-34 Preregister the detector of surprise: a Level-2 target certified outside the frozen closure
- source: roles/Aporia/DISSENT_LEDGER.md:12 @ fed32513a (2026-09-11), seat Aporia; quote: "preregistration is not a reason to drop /                    preregistration; it is a reason to preregister the /                    DETECTOR OF SURPRISE rather than the surprise."
- kind: directive-idea
- question: can non-membership in a frozen closure (APO-06 fixed point; APO-11 world4 hidden transformation) be the preregistered observable for mechanisms no human conceived?
- why it might matter: reconciles preregistration with open-endedness -- otherwise every gate confirms only what we could already name (D-A01 OPEN). README.md:218 names the same "concept invention vs verification gap".
- later evidence: APO-06 / APO-11 not started (BACKLOG_H0H5.md:18,23); Atlas BS-heldout-task-competence (F5-6/RA-2) proposes a related post-hoc-descriptor score. none run.
- lenses: Aporia Q045 certificate, TINYPROG, Atlas RA-2
- related: H-D1-21, 52

### H-D1-35 The copying gap: must the programme author its unit of inheritance?
- source: roles/Aporia/DISSENT_LEDGER.md:47 @ fed32513a (2026-09-11), seat Aporia; quote: "So the first /                    question is not whether the soup is rich enough; it is /                    what the unit of inheritance is"
- kind: open-question
- question: D-A02 / APO-28: H0-H5 contain no copying hypothesis; every precedent authored its replicator. Does the programme write it by hand and say so, or hold that it condenses?
- why it might matter: decides whether "grow, not hand-design" is achievable for heredity itself.
- later evidence: partly advanced -- COPIER-CENSUS-01 (c5067fac6) found exact self-copiers among random 32-byte tapes (~1 per 1e5) but "Copying requires the COPY primitive in this bench" (Z80ATLAS_RULINGS_FOLLOWUP_REVIEW:227); AGE (Aether) has no birth primitive. Operator never ruled on APO-28.
- lenses: z80atlas census, AGE, NPE, BEE; Atlas AL-5
- related: H-D1-50 (AL-5), 11, 13

### H-D1-36 Selection-induced evaluator gaming as a toy assay (evaluations-to-first-exploit)
- source: roles/Aporia/BACKLOG_H0H5.md:31 @ d1d877b39 (2026-09-23), seat Aporia; quote: "APO-19 | Selection-induced evaluator gaming as a toy assay: deliberately porous measurement channel, separable vs randomised vs structurally isolated evaluation"
- kind: parked-experiment
- question: base rate and speed at which selection finds evaluator exploits under different evaluation isolation designs.
- why it might matter: METRIC_EXPLOIT recurs (ASAL, Ares best-of-N, WSE W8 leak); a measured base rate would size every engine's cheat controls.
- later evidence: none run; Atlas EV-8/RA-3 (EXPERIMENTS.jsonl:21,32) propose the same measured on real campaigns; unpicked.
- lenses: all selection engines, Harmonia AF fixtures
- related: H-D1-53, 56

### H-D1-37 Endogenous, language-free memory geometry scored by operational consequence
- source: roles/Aporia/BACKLOG_H0H5.md:33 @ d1d877b39 (2026-09-23), seat Aporia; quote: "APO-21 | Endogenous language-free memory geometry: machine-native keys (extensional signatures, traces, failure vectors), self-organised index, scored only by an operational consequence"
- kind: directive-idea
- question: does a self-organised index over machine-native keys beat random / temporal / nearest-trace / taxonomy baselines for retrieval that changes outcomes?
- why it might matter: the representation/memory co-evolution the North Star names; also tests whether human taxonomy is a bottleneck (APO-16 mechanism-vs-topic index is the literature twin).
- later evidence: none found; depends on fossils (Vivarium/PEW down).
- lenses: fossil stores, Nyx organs, Atlas
- related: H-D1-54 (portable organs), 48 (memory outside world)

## D. Selective Irreversibility program (Aporia + Cyclops)

### H-D1-38 SI law: elimination is a theorem; is transient query-time contraction "the contraction the law requires"?
- source: programs/selective_irreversibility/FALSIFIERS.md:145 @ 61e09d32f (2026-09-26), seat Aporia; quote: "So 'does transient, query-time contraction count as the contraction the law requires?' is /     LOAD-BEARING. If it counts, B cannot falsify the law on generalization tasks at all"
- kind: open-question
- question: operator memo Q1 reading + Harmonia s12 conceptual freeze; with memo s11a ("THE ELIMINATION HALF IS A THEOREM", PORTFOLIO_MEMO:113) only selectivity and requirement are empirical.
- why it might matter: without the freeze the program's candidate law has unfalsifiability regions (s4B on generalization readouts) that invite post-hoc retreat.
- later evidence: RULINGS.md:61-65 (4f5d9bac8) hands Q1 and "the Harmonia s12 freeze (queued, not done)" to the operator; no freeze commit found through 2026-09-27.
- lenses: SI program, WTP-LM01, PTE-SI01, Harmonia
- related: H-D1-39, 40, 41

### H-D1-39 Selective advantage as bias-structure match rather than selectivity (GENERATOR_DEPENDENT)
- source: programs/selective_irreversibility/ANOMALIES.md:40 @ f6f58cf80 (2026-09-26), seat Cyclops; quote: "A SELECTIVE advantage may then be a claim / about bias-structure MATCH, not about selectivity as such."
- kind: anomaly
- question: does a GENERATOR_DEPENDENT winner pattern (cp/tt -> lossless, spectral -> selective) damage or fit the law's "requires" clause? (proposal P3 for the freeze)
- why it might matter: generalises beyond WTP: any "compression helps" claim may be an inductive-bias-match claim; central to representation co-evolution.
- later evidence: WTP-LM01 prereg frozen v0.3.1 (768ea8ce9, 2026-09-26) under operator rulings 1426c8e2e; whether P3 was decided before rows not verified here; no campaign rows found.
- lenses: WTP (Ensorain), SI
- related: H-D1-38, 40

### H-D1-40 In WTP, is "selective vs lossless" really a frontier over retained exact records?
- source: programs/selective_irreversibility/ANOMALIES.md:53 @ f6f58cf80 (2026-09-26), seat Cyclops; quote: "So in WTP the SELECTIVE/LOSSLESS contrast looked substantially like a same-optimizer FRONTIER over retained / exact records."
- kind: open-question
- question: with optimizer equalised, competence rises with exact records kept (B=216 .2 ... full 2.6); is there any selectivity effect beyond the reservoir size?
- why it might matter: could dissolve the SI contrast into a memory-budget curve; the intermediate mechanism (lossy factors + relevance-blind reservoir) became LM01's headline R-c.
- later evidence: LM01 frozen (768ea8ce9, 222ed8082 operator review packet); no result rows found.
- lenses: WTP-LM01
- related: H-D1-39, 33

### H-D1-41 The reversible-core experiment (learned selective export vs random export at matched merge-time curve)
- source: programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md:56 @ d50103524 (2026-09-25), seat Aporia+Cyclops; quote: "2. ONE reversible-core experiment covering A and C together (Cyclops R1.3; Aporia /    concurs). A bounded reversible agent, with an export channel outside the boundary /    and priced, learns an export policy."
- kind: parked-experiment
- question: does a bounded reversible agent that must export state learn a relevance-selective export policy, vs random export and a recency-decorrelated FIFO arm?
- why it might matter: the only designed attack on countermodels A and C; no reversible agent substrate exists on any host.
- later evidence: none found (Nestor/NPE named builder; stewards frozen 2026-09-26).
- lenses: NPE (to build), SI
- related: H-D1-38, 42

### H-D1-42 Distinction-Survival Assay (DSA) as a portable observation instrument
- source: programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md:67 @ d50103524 (2026-09-25), seat Aporia+Cyclops; quote: "3. DSA (distinction-survival assay) on FROZEN specimens: Ananke PTE M1-M3 (M1), AGE /    (the first M2 adapter), and the coupling campaign's Z80 specimens after its end"
- kind: parked-experiment
- question: which distinctions survive in frozen specimens vs a relevance-blind merge matched on the merge-time curve?
- why it might matter: a cross-engine, theory-neutral instrument for what systems keep and forget -- useful even if SI fails.
- later evidence: memo recommendation 12(i); be5636af4 lists "DSA holes"; no adapter or calibration found.
- lenses: PTE, AGE, BEE/Archaeon Z80, SI
- related: H-D1-43, 41

### H-D1-43 Cross-engine replay-and-perturb interface and full state-snapshot hashing
- source: programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md:97 @ d50103524 (2026-09-25), seat Aporia+Cyclops; quote: "No cross-engine replay-and-perturb interface. No state-snapshot hash that covers RNG / and in-flight state (PTE, Z80xAtlas, AGE)."
- kind: unfollowed-recommendation
- question: can engines expose a common replay + intervene hook with snapshot hashes covering RNG and in-flight state?
- why it might matter: every counterfactual/lens assay (DSA, causal lens, host-conditioned assay) is re-built per engine; this is the recurring bottleneck.
- later evidence: causal lens tools_bee/tools_npe are per-engine replays; no common interface found.
- lenses: all engines
- related: H-D1-42, 06, 62

### H-D1-44 C-CORE conservation read as "relevance" is circular; unit mismatch to s1
- source: programs/selective_irreversibility/EXPERIMENTS.md:140 @ 61b970537 (2026-09-26), seat Aporia; quote: "(1) G2: SELF+LDIR are 'what survived', so calling them relevant BECAUSE conserved is circular."
- kind: open-question
- question: how can relevance be established independently (knockout frozen first) and how does lineage-level byte turnover map to an agent's accessible causal state?
- why it might matter: general trap for any "conserved = important" reading in evolved populations; the matched null is purifying selection plus drift.
- later evidence: none found.
- lenses: NPE C-CORE, SI
- related: H-D1-11

## E. Accessibility frontier (Crius essay)

### H-D1-45 The controlled pair: same destination and payoff, different assembly geometry
- source: docs/essays/2026-09-24-accessibility-frontier.md:222 @ 391395aac (2026-09-24), seat Crius/Operator essay; quote: "What Crius proposes (s7-s9, the closing experiment): the assembly-geometry principle, the hidden axis, the rulers and the controlled pair. None of these has been tested anywhere."
- kind: directive-idea
- question: does discovery rate of a cognitive primitive track construction-landscape geometry (A-G: secondary uses, niches, coupled recombination, development, local credit, physics, transplant) rather than payoff?
- why it might matter: proposes a hidden axis of intelligence ("how much useful gradient the substrate exposes toward not-yet-complete machinery"); directly about what pressures/primitives Prometheus should supply.
- later evidence: none found. (Quote uses "s" for the essay's section sign.)
- lenses: Crius, CWE (Cosmos), BEE kernel (test G), WTP, AGE
- related: H-D1-46, 23

### H-D1-46 Accessibility rulers: a trusted form for the accessibility ratio, foothold density, semantic-link survival
- source: docs/essays/2026-09-24-accessibility-frontier.md:154 @ 391395aac (2026-09-24), seat Crius; quote: "We do not yet have a form we trust"
- kind: open-question
- question: can assembly distance, accessible path length, valley depth, foothold density, semantic-link survival and rho be measured on a second primitive/substrate?
- why it might matter: would make "evolvability toward machinery" a measurable substrate property comparable across engines.
- later evidence: none found.
- lenses: Crius, any engine with paired re-evaluation
- related: H-D1-45

## F. Atlas blind spots, prior-art raid, synthesis directive

### H-D1-47 Fixed vs mutable interpreter (copy machinery inside the heritable unit)
- source: roles/Atlas/theory/BLIND_SPOTS.jsonl:2 @ f8df65681 (2026-09-24), seat Atlas; quote: "The interpreter and the copy machinery are outside the heritable unit: organisms vary, the machine that runs them does not."
- kind: prior-art-gap
- question: AL-1: does a mutable interpreter enlarge the reachability SET at matched mutation rate and viability?
- why it might matter: every Prometheus organism runs on a fixed VM; stringmol/BFF/aevol show alternatives; a primary lever for co-evolving mechanism and representation.
- later evidence: status COMMISSIONED; no run found (git log --grep AL-1 empty since 2026-09-21).
- lenses: Z80 engines, AGE (no organism boundary)
- related: H-D1-35, 50

### H-D1-48 Environment co-evolution and memory-in-world (UED-1/UED-4; BS-memory-outside-world)
- source: roles/Atlas/theory/BLIND_SPOTS.jsonl:6 @ f8df65681 (2026-09-24), seat Atlas; quote: "Memory belongs to the organism and the world is a separate, mostly non-writable object."
- kind: prior-art-gap
- question: do organisms that persist only by writing a shared medium read by later organisms (vs private writes) produce different machinery; and (line 1, BS-fixed-environments) does selecting/co-evolving the environment change what evolves?
- why it might matter: Archaeon's ENVGATE shows environment gates reproductive access; no engine lets the environment evolve.
- later evidence: BS-memory-outside-world OPEN; UED-1 COMMISSIONED, blocked on Techne fossilising dcd (roles/Techne/resume.md:26); none run.
- lenses: Archaeon envgate, AGE, POET donor
- related: H-D1-37, 15

### H-D1-49 Detectors that need no parent-child pair (population-level transmission)
- source: roles/Atlas/theory/BLIND_SPOTS.jsonl:7 @ f8df65681 (2026-09-24), seat Atlas; quote: "Replication detectors assume an individual parent and an individual child, so anything that propagates without that shape is invisible."
- kind: prior-art-gap
- question: run a pair-free information-transmission detector on the SAME logs as the parent-child detectors and compare; with BS-discrete-individuals (TI-1/AL-3) on evolvable boundaries.
- why it might matter: the causal lens is entirely parent-child; collective or diffuse heredity (AGE, Aether) would be invisible to the current rulers.
- later evidence: OPEN; none found.
- lenses: causal lens, AGE, BEE, NPE logs
- related: H-D1-01, 13, 26

### H-D1-50 Implicit replication with no scalar objective anywhere (AL-5 / XE-07)
- source: roles/Atlas/theory/BLIND_SPOTS.jsonl:4 @ f8df65681 (2026-09-24), seat Atlas; quote: "Every engine carries an explicit fitness term, even when it also uses quality-diversity or novelty."
- kind: prior-art-gap
- question: what does the same substrate produce under implicit replication only; explicit reproduction opcode vs reproduction from local interactions?
- why it might matter: explicit fitness is a hand-designed pressure; the North Star prefers grown pressures.
- later evidence: COMMISSIONED; BEE/NPE Z80 worlds partly implicit but carry task terms; none run as specified.
- lenses: Z80 engines, AGE
- related: H-D1-35, 47

### H-D1-51 Reanalyses that need no new compute: evaluator-exploitation census, rediscovery rate, curriculum pools
- source: roles/Atlas/proposals/2026-09-21_prior_art_raid/EXPERIMENTS.jsonl:32 @ 2c7a19adb (2026-09-21), seat Atlas; quote: "RA-3 | REANALYSIS: evaluator-exploitation census across campaigns" (id/title fields)
- kind: unfollowed-recommendation
- question: RA-1 (queue pools as curriculum), RA-3 (exploit census), RA-4 (Crius PARTS as cross-niche recombination), RA-5 (rediscovery rate across seats).
- why it might matter: cheap, repo-only science on the fossil record; RA-5 directly measures the convergence the operator fears.
- later evidence: Techne journal 2026-09-25 (gandalf-a04f7c25_RESET.md:91) says "RA-1/RA-3 need nothing"; none run.
- lenses: Atlas index, all campaign records
- related: H-D1-36, 20, 64

### H-D1-52 Engine Five's kill rung: is persistence useful beyond equal-information context (F5-0)?
- source: roles/Atlas/proposals/2026-09-21_prior_art_raid/ENGINE_FIVE_EXPERIMENT_LADDER.md:5 @ 2c7a19adb (2026-09-21), seat Atlas; quote: "Cumulative lifetime competence, interacting recursively with generated /     worlds through a persistent, growing, reusable internal library, is a /     distinct scientific object that no existing Prometheus engine can hold."
- kind: parked-experiment
- question: the cheapest rung that can kill the hypothesis (F5-0), then F5-1 composition, F5-4 causal dependence on retained structure.
- why it might matter: decides whether a high-affordance fifth puddle is a distinct object; synthesis directive (9e54a51ce) superseded parts of the thesis but kept the question.
- later evidence: none run; Aphrodite (improvement-of-improvement, M4) is the nearest engine.
- lenses: Aphrodite, Voyager schema donor
- related: H-D1-54, 33

### H-D1-53 Can acquired machinery be portable, retrievable, executable organs? (synthesis directive)
- source: origin/chiron/base-role-adopt-2026-09-21:roles/Chiron/prompts/2026-09-21_synthesis_directive/SYNTHESIS_DIRECTIVE.md:315 @ 9e54a51ce (2026-09-21), seat Operator via Chiron; quote: "Can acquired machinery be represented as portable, / retrievable, executable organs that remain useful across / contexts, organisms or worlds?"
- kind: directive-idea
- question: ablate description / key / payload, transplant across agents and worlds, compare against raw demonstrations, episodic memory and whole-fossil transfer (GEA-4).
- why it might matter: "If this survives causal testing, it may become foundational"; the representational unit of cross-engine inheritance.
- later evidence: GEA-4 named Techne priority 1 (roles/Techne/resume.md:29) but not built; none found.
- lenses: Nyx organs, Techne fossils, Atlas GEA-4
- related: H-D1-37, 52

### H-D1-54 Do measurement defects, not substrates, explain most reversals? (P-measurement-before-mechanism)
- source: roles/Atlas/theory/PROPOSITIONS.jsonl:9 @ f8df65681 (2026-09-24), seat Atlas; quote: "Where a ruler is ill-conditioned, mechanism claims inherit its artefacts: measurement defects, not substrates, explain a large share of our reversals."
- kind: open-question
- question: what fraction of the ecology's reversed claims trace to ruler defects vs substrate facts?
- why it might matter: if large, investment should shift from new worlds to rulers; testable on the committed record.
- later evidence: none found as a count; C-001 false-friends ledger (FF-1..34) is raw material.
- lenses: all engines' forensics
- related: H-D1-64 (T5), 51

## G. Harmonia, Kairos, other program instruments

### H-D1-55 ASAL's open-endedness score rewards embedding drift; can a class rule separate genuine life?
- source: roles/Harmonia/REVIEW_PACKET_ASAL_001_AND_ANCESTRY_RULER_2026-09-18.txt:122 @ dab36b150 (2026-09-18), seat Harmonia[gandalf]; quote: "Reading in one line: the score rewards embedding drift, which turbulent /   Lenia supplies cheaply and coherent morphing Lenia supplies as well;"
- kind: open-question
- question: is a class rule frozen from one Orbium rollout defensible (47 crossers UNCLASSIFIED); does a full-domain run through ASAL's own Flax CLIP change I1/I2?
- why it might matter: foundation-model "aliveness/novelty" scores are a candidate automatic pressure; this shows they are exploitable by turbulence.
- later evidence: owed items (port extension, domain-acceptance check) listed s8; none found after 2026-09-18.
- lenses: Harmonia ASAL port, Techne, Nyx
- related: H-D1-36, 56

### H-D1-56 Ancestry reconstruction ruler on real fossils (Avida .spop), and POET rulers
- source: roles/Harmonia/REVIEW_PACKET_ASAL_001_AND_ANCESTRY_RULER_2026-09-18.txt:178 @ dab36b150 (2026-09-18), seat Harmonia[gandalf]; quote: "- Any Avida result: the ancestry ruler has measured synthetic truth /   only; the .spop from Techne does not yet exist."
- kind: parked-experiment
- question: how well can phylogeny (edge recall, MRCA error, extinct branches) be recovered from degraded real fossil records?
- why it might matter: every "lineage" claim from logs depends on reconstruction fidelity; this ruler would qualify Atlas/causal-lens ancestry reads.
- later evidence: HARM-47/48 in gandalf lane (todo_20260925.md "HARM-45, 47-51"); none found.
- lenses: Harmonia ancestry ruler, Avida donor, causal lens
- related: H-D1-49

### H-D1-57 Is the ecology still a selection monoculture ("promote what passes the gate")?
- source: roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md:39 @ 3e13f736c (2026-06-22), seat Harmonia; quote: "**A shared selection monoculture exists, found twice independently.**"
- kind: unfollowed-recommendation
- question: the 2026-06 audit found one hidden principle under diverse mechanisms and gates that trust caller-asserted survival; does the post-reset engine ecology repeat it at the level of discipline (prereg + gate + cheat control)?
- why it might matter: operator's 2026-09-25 convergence concern is the same worry; diversity of engines may hide one selection principle.
- later evidence: ENGINE_LANDSCAPE s3 (95fff9111) finds "convergence in DISCIPLINE (healthy)"; no re-audit of selection principles.
- lenses: all engines
- related: H-D1-20, 34

### H-D1-58 Failure surfaces instead of binary falsification
- source: roles/Kairos/science/FAILURE_SURFACE_v0.md:1 @ 30313d8e7 (2026-09-11), seat Kairos; quote: "A FALSIFIED outcome with no surface is INCOMPLETE work under the Kairos / charter. The surface is what lets a failed experiment name its / neighbours instead of ending the search."
- kind: directive-idea
- question: can every falsified result carry a map (SURVIVES / WEAKENS / DISAPPEARS / REVERSES / UNMEASURABLE / IMPLEMENTATION_DEPENDENT / UNTRIED) over its perturbation axes?
- why it might matter: an operational form of "failure is evidence"; converts nulls into search directions.
- later evidence: KAIROS-05/06 (reader, first map on H5 classes) never built; no adoption outside roles/Kairos found.
- lenses: all engines, Harmonia VACUOUS register
- related: H-D1-29, 64

### H-D1-59 One evidence-maturity ladder or two (SUGGESTED..AUDITED vs P0-P4), and freeze-reference proof
- source: ops/initiatives/GIT_NATIVE_OPEN_QUESTIONS.md:25 @ c17d4c477 (2026-09-27), seat Operator/Archaeon; quote: "| Q12 | **Evidence-maturity reconciliation.** One ladder or a mapping between SUGGESTED...AUDITED and the existing permanence ladder P0-P4? | Two ladders invite inconsistent promotion |" (ellipsis ASCII-substituted)
- kind: open-question
- question: Q12 plus Q11 (how a Task proves it honoured a prereg freeze and who checks drift).
- why it might matter: operational but science-blocking: inconsistent promotion ladders across seats make cross-engine claims incomparable.
- later evidence: none; pilot explicitly leaves them unresolved.
- lenses: ops control plane, Harmonia/Atlas doctrine
- related: H-D1-10

### H-D1-60 QD descriptor independence: port the descriptor-collapse audit to other archives
- source: whitepapers/descriptor_collapse_audit_review_questions.md:22 @ 2b63fc95d (2026-05-05), seat Harmonia (auditor); quote: "The next planned move is s8.2 -- porting the audit framework to" (section sign and dash ASCII-substituted)
- kind: unfollowed-recommendation
- question: are MAP-Elites/QD behaviour axes in current engines (NPE QD cells, Techne pyribs) independent, or do they collapse as in the Zoo TT study?
- why it might matter: QD archives are the ecology's stepping-stone memory; coupled axes silently shrink diversity.
- later evidence: none found for post-reset engines; Atlas QD-3 (learned vs human descriptors) also unrun.
- lenses: NPE QD, Techne pyribs, Atlas QD-1/QD-3
- related: H-D1-34

## H. Artemis SFE-retrospective threads (roles/Artemis/threads/sfe_retrospective/THREADS.md @ 0b00e4312, 2026-09-27)

### H-D1-61 T1 SFE disposition and archive custody
- source: roles/Artemis/threads/sfe_retrospective/THREADS.md:15 @ 0b00e4312 (2026-09-27), seat Artemis; quote: "Question: what is SFE now, and are its two ledgers safe?"
- kind: open-question
- question: custody census of M1 ledger eng_8a37a5d3 (89,939 experiments, H0-H5 corpus) and M2 eng_906356f7; then operator disposition.
- why it might matter: evidence loss risk; Harmonia HARM-13/16/18 and ARCH-47 blocked on the M1 corpus.
- later evidence: none found.
- lenses: SFE, PEW
- related: H-D1-28, 29

### H-D1-62 T2 Provenance as an embeddable receipt contract, not a service
- source: roles/Artemis/threads/sfe_retrospective/THREADS.md:41 @ 0b00e4312 (2026-09-27), seat Artemis; quote: "Question: can SFE's three guarantees (prediction before observation, / loser-keeping selection families, executed-vs-requested attestation) be / delivered as a small receipt format"
- kind: directive-idea
- question: as stated; retro-apply to one closed campaign (Crius C2 or Ares cycle 2).
- why it might matter: the one capability no post-SFE engine has; best-of-N and drift reversals recur.
- later evidence: C-001 "minimum portable-Task record" (CAMPAIGN.md:52) is a partial receipt; none found for the guarantees.
- lenses: SFE docs, all engines
- related: H-D1-06, 43

### H-D1-63 T3 Where the ecology's evidence actually lives
- source: roles/Artemis/threads/sfe_retrospective/THREADS.md:69 @ 0b00e4312 (2026-09-27), seat Artemis; quote: "Question: for each active engine, is the evidence behind its reported / results reachable by another seat -- in git, in the canonical store, or / only on the host that ran it?"
- kind: open-question
- question: as stated.
- why it might matter: North Star requires residue to remain available to future search; Atlas indexes 4 of 15 engines (REPORT_2026-09-25), 1,229 machine-local-only sources.
- later evidence: TH-006 slice (e40904023) for one task; fd7ca4fde (>1 MiB artifacts discarded). No census.
- lenses: Atlas, all engines
- related: H-D1-06, 20

### H-D1-64 T5 A cross-engine failure catalogue (class, detection, cost, pre-launch test)
- source: roles/Artemis/threads/sfe_retrospective/THREADS.md:115 @ 0b00e4312 (2026-09-27), seat Artemis; quote: "Question: can the ecology's forensic reversals be catalogued by failure / class so a new engine checks for them before launch rather than after?"
- kind: directive-idea
- question: as stated; measure recurrence after documentation.
- why it might matter: stale comparator, best-of-N, planted law, event-missing windows, identity vs heredity, hidden seeds recur engine after engine.
- later evidence: causal lens FALSE_FRIENDS.md (FF-1..34) is a lens-scoped seed; none ecology-wide.
- lenses: all engines' forensics
- related: H-D1-54, 12, 19, 25, 58

### H-D1-65 T4 Host coupling and placement
- source: roles/Artemis/threads/sfe_retrospective/THREADS.md:93 @ 0b00e4312 (2026-09-27), seat Artemis; quote: "Question: which engines must run where, and what does co-location cost?"
- kind: unfollowed-recommendation
- question: per engine inherent requirement vs host; measured peak RSS/CPU; standing processes per host.
- why it might matter: operational, but ENVGATE-02 co-running hung SFE/PEW (8c5a1a23b) and SI memo s10 notes co-running reduces campaign N (a science cost).
- later evidence: C-001 pilot shows BEE/NPE/PTE tasks run on 8 GB nodes (CAMPAIGN.md:75); Aether portable units (bc7cadc76). No placement decisions.
- lenses: all engines, hosts
- related: H-D1-06

### H-D1-66 T6 The Z80 triplication as a planned cross-implementation triangulation
- source: roles/Artemis/threads/sfe_retrospective/THREADS.md:136 @ 0b00e4312 (2026-09-27), seat Artemis; quote: "Question: should the three independent Z80 worlds (Nestor, Bellerophon, / Archaeon) be treated as one deliberate cross-implementation experiment, / or consolidated?"
- kind: open-question
- question: one preregistered assay on all three with a declared disagreement budget.
- why it might matter: agreement is a real cross-implementation result; divergence locates artefacts. Same as ENGINE_LANDSCAPE Q2 (line 71).
- later evidence: deep-block D_Z80_SYNTHESIS.md (72923db05, branch) synthesises the three; no joint assay preregistered.
- lenses: NPE, BEE, Archaeon z80atlas, causal lens
- related: H-D1-20, 01

## I. Two additional program-level items

### H-D1-67 SI blind lanes: one time-limited theory-blind lane for a fleet-wide hypothesis
- source: programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md:149 @ d50103524 (2026-09-25), seat Aporia+Cyclops; quote: "Q4. Blind lanes: the fleet has one, time-limited. Designate a second (a seat to be"
- kind: unfollowed-recommendation
- question: can a program hypothesis circulated fleet-wide (essay 1ba514fce linked from README) still be tested blind; is measured exposure (BLIND_LANES.md, DO_NOT_BRIEF probes) enough?
- why it might matter: theory-aware engines can manufacture support; blindness is an instrument property the program measured but did not secure.
- later evidence: RULINGS.md:62 hands Q4 to the operator; none answered.
- lenses: SI probes (prepost_check.py), Nyx/Techne, Bellerophon
- related: H-D1-38

### H-D1-68 Does the relevance-blind export control have to be random (recency confounds relevance)?
- source: programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md:62 @ d50103524 (2026-09-25), seat Cyclops; quote: "The relevance-blind control must be RANDOM export. FIFO/recency /    export is blind only where task relevance is uncorrelated with recency."
- kind: defect-ambiguity
- question: in which task families is recency correlated with relevance, and which "indiscriminate" controls across engines (FIFO, decay, drop) are silently selective?
- why it might matter: generalises to every forgetting/retention control in the ecology (H3 retention, WTP reservoirs, PTE decay).
- later evidence: none found.
- lenses: SI, WTP, PTE, H3 retention harness
- related: H-D1-41, 29

## Cross-domain pointers
- Proteus composition semantics "need redesign" and 12 stop-condition questions: roles/Harmonia/BOUNDARY_DEPTH_PACKET_02_2026-09-11.txt:423 (Proteus/Harmonia domain).
- Particles ESS-trigger variance-ratio claim not preregistrable at 50 seeds; plan re-issue vs fix: roles/Harmonia/REVIEW_PACKET_PARTICLES_002_AND_ALIFE_STEERING_2026-09-17.txt:201.
- Proteus V0.5 authored current vs sampling floor (V-008): roles/Harmonia/VACUOUS_READINGS.md:56.
- D3 live fires EXCHANGEABILITY_SUSPECT (V-006) and d3.v3 findings: roles/Harmonia/VACUOUS_READINGS.md:47; roles/Archaeon/BACKLOG_H0H5.md:54.
- Deep Research verifier calibration before trusting REFUTED (APO-15): roles/Aporia/BACKLOG_H0H5.md:27 (deep-research domain).
- Citation fetch-verification debt (458 citations, 55 with URL): roles/Elenchus/investigations/2026-09-11_epistemic_debt/LEDGER.md:188.
- Silent-islands predictions P1-P8 never run (math-era tensor lane): roles/Kairos/ARCHAEOLOGY_2026-09-11.md:99.
- OQ1 spectral tail test parked on 341 GB lfunc substrate: roles/Kairos/ARCHAEOLOGY_2026-09-11.md:66.
- Orbit canonicalizer 2D classification (equivalence x assurance): docs/meta_strategy_brainstorm_seed_2026-04-28.md:125.
- NPE W1 X-DD-STATELESS / C-STATELESS-FFA6 (post hoc cell restriction) results: commits 0cba4eb5c, d4f7ba271 (Nestor domain).
- Aether AETH-03 locality horizon-robust to 10,000 ticks; rcv_add/rcv_str falsifier: commits e67dd06bc, 9862cfa9e (Aether domain).
- PTE-C1b: M3 is transport landing on the readout tick; SETRULE required: commit cc98596dd (Ananke domain).
- Harmonia instances cannot message each other (comms inbox filters sender == agent): roles/Harmonia/RESUME_20260925_m2-ca1148a0.md:28 (ops/comms domain).
- Aphrodite Campaign 1 adversarial contract (#490) and requests #452..#534 untriaged: roles/Harmonia/todo_20260925.md:10; roles/Archaeon/BLOCKED_ON_OPERATOR_INPUT_2026-09-27.md:18.
- Crius C2 terminal review and Ares cycle 2 hostile worlds (source of H-D1-45/62 material): crius/, commit ab137f52b.
