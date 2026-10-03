# Tantalus forensic audit for ASTRA-6.0 / Enceladus

## 1. What evidence was inspected, and what does coverage establish?

### Takeaway and scope
- Audit date: 2026-10-01; repository: `C:/Prometheus-worktrees/enceladus-base-role`.
- Inspection freeze: `eeeda08bb45757298b3cb21ee22d816b44388aef`; supplied evidence base `9a83cec2c` is an ancestor, verified with Git.
- The worktree was clean before this audit; only this requested report is added. No commit, dependency change, campaign, source mutation, or infrastructure action was performed.
- Requirements and architecture remain the pre-salvage specification; the recommendations below are a later requirement-led audit, not retroactive edits to Stage I. [REQ] [ARCH]
- The crawler describes its own source tree as `21a47402a`. That is historical provenance, NOT this inspection's checkout. The blob register below identifies the versions actually inspected. [T]
- **V** = directly inspected implementation/text fact; **P** = primary-source reported measurement, not rerun; **D** = dossier/index-only account; **I** = this audit's inference or recommendation; **U** = unresolved.
- V does not mean runtime correctness. Reading a result table confirms the recorded claim, not the computation that produced it. No historical scientific result was recomputed.
- Searches were restricted to the Tantalus package and explicit source paths. No other architect conclusions, prohibited role trees, global content retrieval, unfiltered wiki, credential files, or sealed holdout contents were read.

### Index census and depth of inspection
- Read-only JSON parsing found 528 artifact rows, 528 distinct paths, and 527 existing paths; the sole missing path is `agents/icarus/cycles/cycle_018`, explicitly marked off-tree in its index record. [A]
- The engine index contains 46 rows and 186 distinct path entries; all 186 exist. A directory's existence does not establish the completeness or executability of its contents. [E]
- Artifact types: code 148; result 87; report 52; directive 38; design 33; prereg 30; review 28; data 23; errata 20; ledger 17; backlog 15; other 13; journal 12; test 6; config 5; todo 1. [A]
- Fifteen seat dossiers exist. All index rows were considered for the inventory; eleven seats received primary-source checks below. Coverage is not a claim that all 528 artifacts or all source bodies were read. [A] [E]

| Seat | Artifact rows | Engine rows | Audit depth and decisive source route |
|---|---:|---:|---|
| Ensorain | 53 | 7 | V/P: scorer, operator ruling, WTP-03 report, journal; [S01]-[S03], [S20] |
| Ananke | 54 | 3 | V/P: runtime state/checkpoints and dated correction chain; [S04]-[S05] |
| Theseus | 43 | 2 | V: collision/tensor code; D: campaign outcomes and May engine; [S09], [D-TH] |
| Cosmos | 40 | 3 | V/P: certificate and restricted/killed result ledger, no sealed implementation; [S06]-[S07] |
| Aether | 42 | 2 | V/P: CPU transition, paired-state assay, E-009 replication report; [S14]-[S15], [S27] |
| Tyche | 37 | 2 | V/P: cheat/causality audit, v1 correction, Block R report, historical TODO; [S12], [S21], [S23]-[S24] |
| Aphrodite | 46 | 4 | V: mutable library, immutable operations, S4 gate constants; D: broader campaign history; [S10]-[S11], [D-AP] |
| Ergon | 43 | 6 | V/P: retention runner, witness injection and headline correction; [S16]-[S17], [S26] |
| Diomedes | 32 | 4 | V/P: correction ledger and census code; Nyx defect report cross-checked against code; [S13], [S25], [S28] |
| Polyhymnia | 20 | 2 | V/P: decoder, exact-probe readout and operator pivot; [S18]-[S19], [S22] |
| Koios | 30 | 2 | V: residualization and gate implementation; D: other analyses/shared surfaces; [S08], [D-KO] |
| Talos | 23 | 1 | D: locator/inventory only; no extractor or semantic-audit rerun. [T] [E] |
| Arachne | 24 | 2 | D: locator/inventory only; no database, crawler or damage test run. [T] [E] |
| Icarus | 20 | 1 | D/U: decisive cycle artifact absent; no claim about the strategy it actually used. [A] [T] |
| Nous | 21 | 1 | D: locator/inventory only; self-rating account not independently reconstructed. [T] [E] |
| Shared surfaces | Included in seat artifact rows | 4 | D: collider, alien_circuitry, sigma_kernel, prometheus_math; no full body audit. [T] [E] |

### Immutable source register
All hashes are Git blob IDs resolved at the inspection freeze, not experiment commit IDs. Line spans identify inspected evidence; secondary locators retain their weaker D status.

| ID | Exact source and relevant line spans | Git blob |
|---|---|---|
| REQ | [REQUIREMENTS.md][REQ], 15-268 | `b689efa3bc6ab25536bf5b5147fa385d605f1733` |
| ARCH | [RSE_ARCHITECTURE.md][ARCH], 18-114, 167-201 | `7cb269deb81cc278fc4bcef39ca5dbcf6b363733` |
| T | [Tantalus REPORT.md][T], 21-56, 63-83, 426-542, 544-743 | `75c840c543557b590d9e595774b23a41cd6d6430` |
| A | [artifact_index.jsonl][A], 1-528 | `5d7e86cbe9e4bfef5695aa3dac3f41b719e9fb02` |
| E | [engine_index.jsonl][E], 1-46 | `8fd34aaece6a0e1a376814932fad268c62589f5f` |
| S01 | [ensorain/WTP02_OPERATOR_RULING.md][S01], 1-11 | `9bd9058571a8397cac3c8c1b2d8473c6a216941a` |
| S02 | [ensorain/wtp2/world2.py][S02], 10-37, 185-262, 289-299 | `a9e676f4e8aa5b9d96d616b949eae1ab112e2423` |
| S03 | [ensorain/ENSORAIN_WTP03_REPORT.md][S03], 16-71, 133-159 | `774acd818310d7101da6b3a9907e35ba03a9b5b0` |
| S04 | [roles/Ananke/pte/C1_ERRATA.md][S04], 36-39, 147-212 | `1f089ee94eb17f567c57fb0d81271cadeee69028` |
| S05 | [prometheus/ananke/engine.py][S05], 160-168, 221-264, 268-308, 439-472, 546-549 | `63190de2c393690e69b6a779607e6021c213ad95` |
| S06 | [roles/Cosmos/research/RESULTS.md][S06], 8-40 | `7579eb3c4488fa57de12ee73c3c4d03db01bce9a` |
| S07 | [prometheus/cosmos/phenomenon.py][S07], 1-49 | `fc92153012cab816d022254088635f872227aec2` |
| S08 | [koios/scripts/mpa_area1_moment_ratio.py][S08], 173-183, 353-377, 416-472 | `824f3b57bbc48c1f8241e3f7eaa140148c81c1db` |
| S09 | [theseus/synth/collide.py][S09], 1-30, 52-96, 111-152 | `c04e249f570b59bfefad869ad2b595cae6b18a2f` |
| S10 | [roles/Aphrodite/engine/improver.py][S10], 1-11, 77-119 | `cf7e99a730d05f4a8878a322111231a27f53dd12` |
| S11 | [roles/Aphrodite/engine/run_s3s4.py][S11], 377-425 | `3b4dae99b27b58037c1abf64fb6972f7b2e7cb71` |
| S12 | [tyche/audits.py][S12], 1-59, 62-90 | `13e6b71535c62c8bb6bc8ceb1cdbcec4fd4e78b2` |
| S13 | [nyx/specimens/diomedes_k0_census/FAILURES.md][S13], 3-19 | `8ba0eabebf6a7dff0f62c2585316f8cd85e17c5a` |
| S14 | [ops/campaigns/C-002/E-009/RESULT.md][S14], 3-33, 35-55 | `949fb526da8d5a1ea4b59734caa844ef237b1df1` |
| S15 | [Aether/observatory/aeth03_propagation.py][S15], 8-49, 74-147 | `70772b172cf8f2873a4663afb94d51b39612cda3` |
| S16 | [ergon/gen1b/ANNOTATION_2026-09-11_headline_falls.md][S16], 3-25 | `93f0ba588fd5bd5ff21d673472d6e56093d8384f` |
| S17 | [ergon/gen3/p3_common.py][S17], 15-23, 64-103 | `5148d93296043e9ecfa60a913d8b2d37a0ee2022` |
| S18 | [roles/Polyhymnia/ledgers/probe_01_lincode_2026-09-11.md][S18], 3-63 | `17ee9fbed8fe60e3a215cbff81057ea5ddb29197` |
| S19 | [roles/Polyhymnia/science/lincode_decoders.py][S19], 1-18, 34-109 | `cbfc281d9c3bb002dc59ae35f8fda294b1ee1c68` |
| S20 | [roles/Ensorain/journal/2026-09-24.md][S20], 21-32, 34-89 | `0cef4a3bf3132d7311f901b0104006bec91e7883` |
| S21 | [roles/Tyche/TODO.md][S21], 3-10 | `6b5d63165e956416ccd4b066c388453e32f8903b` |
| S22 | [roles/Polyhymnia/prompts/2026-09-11_reactivation_direction/OPERATOR_DIRECTIVE.md][S22], 13-53, 64-80 | `893d2aeea11a2c0774aad425a167e9d6323e2c65` |
| S23 | [tyche/runs/v1_2026-09-30/REPORT_v1.md][S23], 3-34, 48-100 | `7b44d0b573f69de8a2baea2a7ba1114ea47682cb` |
| S24 | [tyche/runs/v2_blockR/REPORT_BLOCK_R.md][S24], 3-41, 56-77 | `e01550213b2f30dbbfd9f07255b63a44d32416db` |
| S25 | [roles/Diomedes/coordinate_census.py][S25], 151-210, 243-251, 353-364 | `adf05f9bed8c4cf70a876528a140ebc26f71d91f` |
| S26 | [ergon/gen1b/gen1_run.py][S26], 1-20, 49-75, 113-129, 208-224 | `577125847aabf6a3087d06935e39701cffc751be` |
| S27 | [Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py][S27], 103-169 | `208883546611f1cb6b3d9badd5e60703043a5974` |
| S28 | [roles/Diomedes/REVIEW_ROUND2_CORRECTIONS_2026-08-25.md][S28], 10-90, 114-119 | `180a31336cb4231ac59468c777d6d6a7becd95f4` |
| D-TH | [Tantalus Theseus dossier][D-TH], secondary mechanism/campaign account | `1b22d9f9917b696cb69ce8543bd48f9dfcfeff47` |
| D-AP | [Tantalus Aphrodite dossier][D-AP], 158-218, 301-375, 448-512 | `4afeda490dc3eb706cf0beb52872626f616e6219` |
| D-ER | [Tantalus Ergon dossier][D-ER], 64-75, 163-168, 208-225 | `e933c866b9fa2c7870c996c80c45977bc8f4a44a` |
| D-KO | [Tantalus Koios dossier][D-KO], 73-97, 249-423 including shared surfaces | `9d73fe337adb032dfe457b454ff25940956f9655` |
| D-TY | [Tantalus Tyche dossier][D-TY], 159-219, 460-550, 641-679 | `02d94a45c68d5d3340ac053657e4f19125ae6de2` |
| D-AE | [Tantalus Aether dossier][D-AE], 68-116, 243-316, 387-443 | `8d348ce599f13735c273d32e51a307e2e019de12` |
| D-PO | [Tantalus Polyhymnia dossier][D-PO], 83-143, 268-326 | `633393b7743e325125f2e7d8e29f4294fd5d0e8c` |

### Historical reading and limits
- Ensorain's journal preserves a charter-to-foundry pivot, pre-data repair of a mutation branch never exercised in development, and the same-session scalar autopsy; the historical lesson is correlated gates, not dishonest reporting. V/P [S20:21-55][S20]
- Polyhymnia's operator explicitly stopped accumulate-before-consumer work and required one consumed representation probe before a daemon. This is an operating decision, not a theorem against representation scavenging. V [S22:13-48][S22]
- Tyche's TODO is dated 08:10Z on September 30 and still lists a v1 preregistration; the v1 report documents a completed run. A stale TODO cannot establish current execution status. V [S21] [S23]
- Backlog and unrun-design accounts remain D unless primary evidence above says otherwise; authored possibility is not implemented capacity or measured reachability. [T:408-424][T]

## 2. Which findings survive tracing, and how far do they reach?

### F01. Ensorain WTP-02 promoted a scalar because the baseline was too weak
- V: `AC` uses fixed birth variance, but the decisive comparison at lines 257-262 subtracts the ZERO predictor rather than the best learned constant. A nonzero DC prediction can therefore earn gain without cell-dependent competence. [S02]
- P: the frozen scorer returned EXPAND; the operator preserved it while ruling PARK/REDESIGN after the post-hoc constant explained the signal. Do not rewrite one verdict into the other. [S01:3-11][S01]
- D/P: WTP-01's preceding failure was a current-variance collapse, not the same constant-predictor defect; the journal distinguishes those stages. [T:201-216][T] [S20:21-32][S20]
- I: correlated replication/ablation/transfer gates cannot substitute for a missing null when all preserve the same scalar. This is an instrument failure, not evidence that factorized regression cannot work.
- Safeguard: freeze zero, fitted constant, recent mean, lookup, and matched-class competitors before search; require each causal intervention to change supported state. R-MSR-01, R-CAU-01.

### F02. WTP-03 retained a real but ordinary positive: online completion
- P: nine promoted specimens beat N0-N5; a POST-DATA tuned batch completion N6 beat all nine by approximately 0.22-2.28 AC. The report calls them known bounded online matrix/tensor completion, not extraordinary physics. [S03:16-71][S03]
- P: the transfer test retained the same field while changing noise/policy, and admission selected completion-friendly worlds. This restricts generality even when the measurements are reproducible. [S03:133-159][S03]
- I: a hindsight-tuned, differently resourced batch estimator is a mechanism explanation and future baseline, not a retroactive equal-budget contest. Preserve its POST-DATA label.
- Salvage: EXTRACT null-ladder/shared-stream/support-check patterns; retain completion as a HISTORICAL CONTROL. Do not inherit the world-admission rule as a broad cognition screen.
- Requirement consequence: same-field transfer cannot satisfy new-causal-family acquisition in R-TRF-01; capacity/lifetime comparisons need R-MSR-02 resource frontiers.

### F03. Ananke separates physical reach, one-shot propagation, and search failure
- V: PTE checkpoints include site registers, energy, rule state, inbox accumulators and in-flight packet sums/counts; the state is richer than a stateless classifier. Tensor layout is not evidence of tensor-algebra cognition. [S05:160-264][S05] [T:65-66][T]
- P: zero_comm is forced to 0.500 by mirrored trials, so COMM_DEPENDENT aliases SIGNAL for those families; it is not an additional causal test. [S04:36-39][S04]
- P: the two multi-hop RELAY signals are receipt-triggered, once-per-episode flood latches; certified forwarding survives, but resettable per-trial competence does not follow. [S04:188-201][S04]
- P: E-W20 reports 139/454 physics-capped nulls and 62-65 eligible search-limitation cases; later E-W23 supplies an in-genome XOR plant at 0.850 versus champion 0.503. [S04:147-154,202-212][S04]
- I: E-W23 qualifies the earlier XOR-zero entry. The dated census must not be presented as a final mutually exclusive partition; this audit did not recompute its overlaps or totals.
- Salvage: HARDEN tiny PTE as a local-transport comparator; EXTRACT complete-state replay and plant/ceiling certification. Require trial-position profiles and same-genome witnesses: R-DEV-01, R-WLD-01, R-CAU-01, R-REP-01.

### F04. Cosmos's law claims shrink to certificate-economics recovery
- V: `certify` computes SEL minus the better of LOG/LAST in normalized reward-minus-cost units; its threshold is 0.10. The certificate does not directly read coordinates, but that alone cannot prevent a coordinate from encoding its definition. [S07:24-49][S07]
- P: C0 laws A/B are RESTRICTED; the definition rung has no significant deficit on the reported sealed universes, all authored by Cosmos. A's 0.983/0.972/0.930 balanced accuracies do not establish a substrate-independent law. [S06:14-30][S06]
- P: C3 passed initial gates, then was KILLED BEFORE HOLDOUT after a coordinate/definition audit; sealed D2 remained unspent according to the public ledger. No hidden law or sealed rows were opened here. [S06:32-40][S06]
- I: preserve law mining as a finite hypothesis-search instrument, not a developmental organism. High prediction accuracy can be accurate restatement rather than discovery.
- Safeguard: definition rung, whole-search null, per-family boundary calibration and independent authorship precede broad-law language. R-WLD-02, R-MSR-01, R-CAU-03, R-REP-02.

### F05. Aether provides a narrow physical positive, not an adaptive organism
- V: the CPU oracle emits byte writes from one active opcode, checks energy, and resolves target/field contests by hash priority. The twin wrapper copies/comparisons include extra carried receive-state, not just visible byte fields. [S27:110-169][S27] [S15:86-147][S15]
- P: fresh-seed E-009 gives rcv_add 22/128 and rcv_str 15/128 sustained origins, versus rcv 4/128 and add/str 1/128 and 0/128; the frozen minimum was 13/128. [S14:9-30][S14]
- P: the report explicitly preserves the reading of activation traces/re-routing, NOT content transport; rcv_str is close to the pooled floor and two fresh seeds individually fall below it. [S14:21-33][S14]
- D: the assay's adjacency-based generation was later recognized as a lower bound rather than exact causal-parent depth; its code docstring still uses the stronger wording. Do not inherit that wording as proof. [S15:15-34][S15] [D-AE:113-117][D-AE] [T:640-642][T]
- I: keep the positive at local propagation under specified physics; lack of a task/learning process prevents developmental conclusions, but does not erase the physical effect.
- Salvage: EXTRACT twin/locality/receipt apparatus; HARDEN a small CPU comparator, not the large GPU deployment. R-ORG-01, R-CAU-01, R-REP-01, R-CMP-02.

### F06. Tyche repaired a residual ruler but did not establish dark-reserve advantage
- V: the future-reading cheat must both produce large gain and fail causality; an honest delayed lens must pass. Five future-replacement cut points are useful tests, not exhaustive causal certification. [S12:24-59][S12]
- P: v1 GATE 6 failed; one coalition's components had max home gains 0.004/0.006 and fusion gained 0.075, replicating at 0.101/0.109 but missing the frozen 0.10 original-test bar. Preserve both the trace and FAIL. [S23:12-34,80-90][S23]
- P: the v1 control secretly retained the old 14-slot reserve, so persistence could not be attributed uniquely to noise-level lexicase. The report's correction supersedes the stronger original interpretation below it. [S23:48-57][S23]
- P: Block R records 2/72 adaptations; its option-value clock missed an admitted coalition because that coalition did not re-enter the population matrix. Censoring and adaptation were different measurements. [S24:21-28,70-77][S24]
- D: the evolving object is a bounded causal feature DAG feeding fixed weak classifiers, not an acting organism; natural residual catalogue entries were never exercised. [D-TY:159-219,549-550][D-TY]
- Salvage: EXTRACT cheat controls, matched nulls and lineage-event accounting; REBUILD the residual/coalition clock for a new target. R-MSR-01, R-SRH-01, R-DEV-01, R-PRV-01.

### F07. Aphrodite's mutable library is not a mutable improvement procedure
- V: the artifact is an ordered data library; its candidates precede the complete G4 fallback. The mutation/fitness/selection machinery is explicitly immutable. This is a search-order prior with unchanged expressive grammar. [S10:1-11,77-119][S10]
- V: S4 conditions 4 and 8 are literal True with comments asserting hostile evaluation and no donor state. They encode trust in the construction, not independently fail-able runtime checks; this observation alone does not prove leakage occurred. [S11:385-420][S11]
- D: accepted S4 was later weakened by these conditions and a positive control equal to the derived schema; A23's positive used constructed recurrence that often recovered the planted motif. No relabeling is imposed by this audit. [D-AP:158-218,328-345][D-AP]
- I: a fixed meta-learner remains a legitimate competitor. But these records cannot satisfy the particular nested fresh-U/fresh-S intervention criterion in architecture section 5. [ARCH:78-87][ARCH]
- Salvage: EXTRACT metering/membrane/conformance patterns only after adversarial qualification; retain library inheritance as a HISTORICAL CONTROL. R-DEV-03, R-CAU-02, R-MSR-02, R-PRV-02.

### F08. Theseus's concept-tensor gain is per-parent, not a learned joint interaction
- V: `TensorStore.gains` evaluates each parent's own latent vector against a fixed positional vector; latent projection and positional vectors are seeded random. No joint parent-index term or fitting appears in that gain computation. [S09:52-82][S09]
- V: rule remapping, ordered parent blocks and provenance are real code; do not infer that the entire child dynamics lack interaction merely because this gain function is separable. [S09:99-152][S09]
- D: the synthetic ancestry campaign has small numeric rule programs, fingerprint-based rulers and corrected ancestry leakage/nondeterminism; the May claim-generating tenant is a different system. [D-TH] [T:237-249][T]
- I: ancestry bookkeeping and increasingly remote parent IDs do not establish semantic novelty, learned higher-order tensor structure, or transferred capability.
- Salvage: EXTRACT explicit ancestry/provenance if needed; REBUILD any interaction-learning claim around a registered joint-versus-separable comparator. R-PRV-01, R-MSR-03, R-TRF-01.

### F09. Ergon's retention null is informative only for the exercised memory channel
- V: the treatment varies eviction from a cap-64 genotype library; search/admission/task/budget are fixed. The cheat path explicitly plants an oracle witness, verifies it solves, and labels planted rows separately. [S26:1-20,49-75,208-224][S26] [S17:64-103][S17]
- P: the Gen-1B +2.78 percentage-point headline is retained as measured but withdrawn in interpretation after P1 I1-I3 = -0.31 pp, CI [-1.12,+0.55], and P3 I3-I0 = +0.55 pp, CI [-0.24,+1.33]. [S16:3-20][S16]
- V: the dossier table says I0 versus I3 for the latter contrast; the primary annotation explicitly says I3-I0. This audit follows the primary sign, not the crawler's table. [D-ER:209-212][D-ER] [S16]
- I: adding interval endpoints is the source's conservative descriptive combination, not a newly computed joint confidence interval. The bounded reading is about this consumer, cap 64 and 30,000 evaluations, not all retention or learning.
- Salvage: EXTRACT planted-path qualification and paired-lineage reporting; retain the library policies as controls rather than an RSE memory architecture. R-SCI-02, R-DEV-01, R-MSR-02.

### F10. Diomedes corrects both semantic overreach and the audit of its own ruler
- P: a proxy reproduced performance equivalent to 40.9% of the local above-chance AUC span; the seat explicitly withdrew causal decomposition and the alleged unexplained 59%. Program KILL and preregistered UNRESOLVED are separate ledgers. [S28:10-28,53-90][S28]
- V/P: `cluster_bootstrap` samples using low bits of a mod-2^31 LCG. Nyx reports power-of-two cluster draws becoming permutations, yielding degenerate intervals; the code confirms the problematic sampler. No bootstrap was rerun here. [S25:175-210][S25] [S13:3-13][S13]
- V correction to the correction: Nyx says zero width makes the gate-vs-error check pass ANY gate. At this freeze, `passes = bool(err and d >= 2 * err)` returns False for zero error. Likewise `includes_zero` depends on the point, not always False. [S25:159-199][S25]
- I: retain the actual bootstrap defect but reject those overbroad consequences. A defect report is evidence to inspect, not a privileged truth source.
- Salvage: REBUILD statistical implementation; EXTRACT headroom/reachability and proxy-reconstruction questions. R-SCI-02, R-MSR-01, R-MSR-02, R-PRV-03.

### F11. Koios's five-gate admission contains two nondiscriminating gates
- V: Gate 3 assigns True after printing diagnostics, without enforcing the stated information-retention threshold. [S08:353-377][S08]
- V/I: per-domain OLS with an intercept produces mean-zero residuals; Gate 5 compares between-domain means of those residuals. With adequate nondegenerate finite fits, its small eta-squared follows from preprocessing, not full distributional equivalence. [S08:173-183,416-472][S08]
- V: KS distribution checks are printed but not used in Gate 5's predicate. Mean equality therefore cannot justify domain-agnosticity in the stronger sense. [S08:442-472][S08]
- I: RETIRE these gates as admission authority, preserving their bytes as HISTORICAL CONTROL fixtures. No conclusion about the mathematical usefulness of moment ratios follows from this software defect.
- Safeguard: every acceptance branch must fail on a planted violation that survives preprocessing; evaluate preprocessing-plus-gate jointly. R-MSR-01, R-PRV-02.

### F12. Polyhymnia is a useful positive contrast: exact measurement can refute its prediction
- V: the decoder maps 12-bit genomes to 8-bit rules by syndrome correction; all choices are authored, not learned. The consumer import and deterministic coset-leader construction are explicit. [S19:1-18,34-99][S19]
- P: the exact probe reports 8/8 controls passing, including direct-map identity and rejection of a nonuniform cheat. Predicted Hamming reach >8 was wrong: 5.6875; class reach 5.6104 versus direct 7.7812. [S18:8-14,34-63][S18]
- P: scrambled Hamming preserves raw reach/neutral histograms while changing class assignments; structure, multiplicity and usefulness must not be conflated. This was a static one-flip assay, not a lineage experiment. [S18:16-31,63][S18]
- D/U: the dossier records an unfulfilled downstream table delivery. No downstream evolvability benefit is established here. [D-PO:268-326][D-PO]
- Salvage: HARDEN this finite decoder fixture; KEEP the consumer-first and prediction-loss record as process exemplars. R-APR-01, R-MSR-01, R-ATT-03.

## 3. What should be salvaged, rebuilt, or excluded, and at what cost?

### Takeaway and cost convention
- I: the defensible near-term salvage is apparatus and bounded comparators, not an already-qualified developmental or recursive engine. None of the directly inspected evidence satisfies Q6's nested protocol. This is an evidence limit, not a proof of impossibility. [ARCH:78-114][ARCH]
- Decisions below concern ASTRA integration, not deletion or retroactive scientific adjudication. KEEP means preserve the identified asset; HARDEN requires qualification; EXTRACT means isolate a smaller part; REBUILD replaces the relevant function; RETIRE excludes it from active authority; HISTORICAL CONTROL preserves a comparator; UNKNOWN blocks commitment pending evidence. [REQ:265-268][REQ]
- All costs are **planning guesses in engineer-days**, for one experienced developer: reading, isolation, adapter work and small qualification tests. They exclude campaign compute, independent replication, procurement, and downstream research.
- `reuse / new` compares the scoped salvage route with a minimal replacement providing the same bounded function, NOT reproduction of a whole historical program. Ranges overlap and are not additive because components share dependencies.
- D-only recommendations are provisional; a path's existence, old test count or reported PASS never qualifies a fresh integration. Requirement prefixes below use the exact R-* IDs in the frozen specification. [REQ]

### Complete engine-index disposition
Rows 01-46 correspond exactly to engine-index line numbers; [E] supplies each row's full path list, mechanism and limitations. Parenthesized paths are the principal integration seam, not an exhaustive dependency inventory.

| E row / component and real function | Evidence/limit; dependency or coupling | Disposition; reuse / new days; replacement alternative | Requirement IDs |
|---|---|---|---|
| 01 Ensorain E0-E2 (`ensorain/e0/` etc.): capped TT/CP regression | D; fixed policy, NumPy and shared TT class; not a planning learner. [E] | HISTORICAL CONTROL; 3-6 / 4-8; tiny capped regressors with exact field oracle | R-DEV-01, R-WLD-01 |
| 02 D-series (`ensorain/d1/`, `dials_retro.py`): parameter-coupling sweeps | D; metric/cost arithmetic can create coupling; E-series dependency. [E] | HISTORICAL CONTROL; 2-4 / 2-4; explicit factorial arithmetic fixture | R-MSR-02 |
| 03 WTP-01 (`ensorain/wtp/`): field/world-genome foundry | D/P; collapsing denominator, reusable serialization concept, v2/v3 coupling. [S20] [E] | EXTRACT; 3-6 / 4-7; small versioned world manifest/replay fixture | R-PRV-01, R-REP-01 |
| 04 WTP-02 (`ensorain/wtp2/`): seeded streams and fixed-reference scorer | V/P; wrong null, imports WTP substrates; not production competence authority. [S01] [S02] | HISTORICAL CONTROL; 2-4 / 2-4; constant-predictor adversarial fixture | R-MSR-01 |
| 05 WTP-03 (`ensorain/wtp3/`): shared-stream regression collider | P; N6 and cross-field tests missing pre-data; shared WTP/TT. [S03] | EXTRACT; 4-8 / 5-10; null ladder with resource frontiers and cross-field split | R-MSR-02, R-TRF-01 |
| 06 LM01 (`ensorain/lm01/`): lossless-vs-bounded estimator harness | D; frozen, never campaigned; accounting/arm internals not audited. [E] [T] | UNKNOWN; 3-6 audit / 8-15; narrow exact-store versus bounded-estimator test | R-MSR-03, R-SCI-02 |
| 07 ARC3 (`ensorain/arc3/`): Bayes/state/window calibration instruments | D; answer-keyed toy processes; shared estimator libraries. [E] | EXTRACT; 3-6 / 4-8; tiny hidden-state process with independent Bayes checker | R-WLD-01, R-MSR-01 |
| 08 PTE (`prometheus/ananke/engine.py` and peers): integer packet VM | V/P; complete state seam exists, Torch/RNG/topology coupling; no Q6 qualification. [S04] [S05] | HARDEN; 8-15 / 12-20; minimal CPU delayed-packet VM | R-ORG-01, R-REP-01 |
| 09 PTE lens (`lens*.py`, `c1b*.py`): native carrier swaps | D/P; exact checkpoint compatibility; forced controls and narrow lineages. [S04] [E] | EXTRACT; 4-8 / 5-9; snapshot lesion/sham/rescue contract | R-CAU-01, R-CAU-02 |
| 10 Wave-2 (`roles/Ananke/research/harvest/`): attainability certificates | P/D; research-only, evolving correction chain; not promoted runner. [S04] [T] | HARDEN; 5-10 / 6-12; tiny light-cone/witness preflight service | R-DEV-01, R-SCI-02 |
| 11 Theseus synth (`theseus/synth/`): rule recombination and genealogy | V/D; Tyche lens dependency; separable random parent gains. [S09] [D-TH] | EXTRACT; 3-6 / 3-6; immutable parent/edit/exposure ledger without tensor claims | R-PRV-01 |
| 12 Theseus May (`theseus/generators/` etc.): catalog tuple generator | D; generator-produced verdicts and off-tree corpus; different tenant. [T] [E] | RETIRE from judging; 2-4 / 5-9; separately checked candidate/reality interface | R-PRV-02, R-INF-03 |
| 13 Cosmos C0 (`prometheus/cosmos/`): coordinate-expression law search | V/P; shared economics/author; certificate plus miner, no organism. [S06] [S07] | HISTORICAL CONTROL; 3-6 / 4-7; finite law miner with definition rung | R-WLD-02, R-CAU-03 |
| 14 Cosmos C3 (`prometheus/cosmos/c3/`): memory certificate/custody | P/D; visible implementations partly withheld; do not import sealed data. [S06] [T] | EXTRACT public contract only; 4-8 / 5-10; independent swap/decodability checker | R-REP-02, R-CAU-03 |
| 15 Cosmos C4 (`roles/Cosmos/c4/`, `power_s0.py`): successor plan/power | D; design, not an exercised successor; family-floor critique unresolved. [T] [E] | UNKNOWN; 2-4 audit / 6-10; independent tiny certificate pilot | R-SCI-02, R-MSR-01 |
| 16 Aether lattice (`aeth01_cpu_oracle.py`, observatory): local byte dynamics | V/P; NumPy variants; carried-state and causal-depth semantics need care. [S14] [S15] [S27] | HARDEN small comparator/EXTRACT twins; 6-12 / 10-18; CPU finite lattice reference | R-ORG-01, R-CAU-01 |
| 17 Aether platform (`Aether/runpod/prometheus_gpu/`): GPU job lifecycle | D; cloud/Fabric/artifact custody; reported dropped large artifacts. [D-AE] | UNKNOWN/defer; 5-10 / 5-9; CPU runner with size/hash-checked receipts | R-CMP-01, R-CMP-02 |
| 18 Tyche ecology (`tyche/lens.py`, v1/v2): evolutionary features | V/P/D; sklearn/SciPy/NumPy, Hecate worlds; clocks/reserves confounded. [S12] [S23] [S24] | EXTRACT controls; 4-8 / 5-9; independent causal-feature calibration harness | R-MSR-01, R-SRH-01 |
| 19 Tyche catalogue (`tyche/residuals/`): quote provenance, not truth | D; Git/source availability; 122 entries are not experimental results. [T] [E] | EXTRACT; 1-3 / 2-4; quote/hash validator with explicit epistemic fields | R-PRV-01, R-OUT-01 |
| 20 Aphrodite E2 (`science/rsi/e2_self_improver.py`): ES hyperparameters | D; four mutable numbers and fixed optimizer; small objective toys. [D-AP] | HISTORICAL CONTROL; 1-3 / 2-4; fixed-meta versus self-tuned ES baseline | R-DEV-03 |
| 21 Aphrodite v1 (`engine/engine.py`): artifact membrane and code search | D; restricted loader/reset/metering need adversarial tests; no model science. [D-AP] | EXTRACT; 5-9 / 6-12; byte-artifact loader plus resource meter | R-PRV-02, R-MSR-02 |
| 22 Aphrodite G4/W5 (`engine/improver.py`): enumeration-order inheritance | V/D; fixed improver, grammar/tribunal coupling, asserted gates. [S10] [S11] | HISTORICAL CONTROL; 4-7 / 5-9; finite library-transfer baseline, not Q6 | R-DEV-03, R-TRF-01 |
| 23 Aphrodite C0 (`science/campaign0*/`): planted-truth assay | D; author-generated logistic outcomes; no independent calibration here. [D-AP] | EXTRACT design/HARDEN checker; 3-6 / 4-7; separately authored injected-effect harness | R-MSR-01, R-CAU-03 |
| 24 Ergon April (`ergon/tensor_executor.py` etc.): column-pair hypotheses | D; precomputed tables and correlation; not tensor-native reasoning. [E] [T] | RETIRE as cognition engine; 2-4 / 3-6; transparent feature/statistic comparator | R-WLD-01, R-ATT-03 |
| 25 Ergon typed DAG (`ergon/learner/`): MAP-Elites operator search | D; archive/operators/trials unaudited; genuine typed representation not qualification. [E] | UNKNOWN; 3-6 audit / 7-12; tiny typed-DAG search baseline | R-APR-01, R-SRH-02 |
| 26 Ergon LoRA/routing (`ergon/learner/greedy/`, `pipeline_d/`) | D; format/prior/template confounds; external-model arm outside CPU-first scope. [T] [E] | HISTORICAL CONTROL, defer execution; 3-6 / 4-8; cheap task-prior/format baselines | R-INF-01, R-MSR-01 |
| 27 Ergon probe (`ergon/probe/`): residue packets/scheduled tasks | D; network/corpus/host dependencies; transport errors and zero-row ticks. [T] [E] | RETIRE legacy scheduler; 3-6 / 4-7; fail-closed local job/receipt runner | R-ATT-01, R-PRV-02 |
| 28 Ergon D-5 (`ergon/gen*`, `agent_d5_blind/`): GA seed-library retention | V/P; Numba/reference VM coupling; only eviction treatment is measured. [S16] [S17] [S26] | EXTRACT qualification/HISTORICAL CONTROL; 5-9 / 8-14; register-VM paired-lineage baseline | R-DEV-01, R-MSR-02 |
| 29 Ergon forensics/detector (`ergon/detector_transfer/`): contract/history | D; proposed detector is blocked, not demonstrated transferable mechanism. [E] | KEEP evidence/UNKNOWN implementation; 2-4 / 5-9; native one-mutation census | R-PRV-03, R-TRF-03 |
| 30 Diomedes ranker (`roles/Diomedes/cycle*_run.py`): one-step AUC | P/D; catalog features reconstruct hidden scalar; untracked corpus dependency. [S28] [E] | HISTORICAL CONTROL; 2-5 / 4-7; object-cross-fitted proxy/true-action benchmark | R-WLD-01, R-MSR-01 |
| 31 Diomedes Arm A (`cycle005_armA_run.py`): scalar commutation enumeration | D; finite population with little conditional headroom. [E] | HISTORICAL CONTROL; 1-2 / 1-3; exact low-headroom gate fixture | R-SCI-02 |
| 32 Diomedes K0 (`coordinate_census.py`): headroom and statistics | V/P; custom RNG defect; report overstates zero-error gate consequence. [S13] [S25] | REBUILD statistics/EXTRACT checks; 2-4 / 2-5; qualified cluster bootstrap | R-MSR-01, R-MSR-02 |
| 33 Diomedes Diagnose (`PREFLIGHT_representational_multiplicity_2026-08-26.md`) | D; preflight only, no executable representation experiment. [E] | UNKNOWN; 1-3 audit / 5-10; tiny matched-pair representation test | R-CAU-03, R-APR-01 |
| 34 Polyhymnia daemon (`agents/polyhymnia/`): keyword/AST index | D/V directive; saturation and no demonstrated consumer, not a learned representation. [T] [S22] | RETIRE daemon/KEEP archive; 1-2 / 2-4; bounded consumer-requested extraction | R-ATT-03, R-PRV-01 |
| 35 Polyhymnia decoder (`science/lincode_decoders.py`): finite genotype map | V/P; Archaeon exact reference/Herakles class-map coupling; no lineage result. [S18] [S19] | HARDEN fixture; 2-4 / 3-5; independent GF(2) table enumerator | R-MSR-01, R-APR-01 |
| 36 Talos (`agents/talos/daemon.py`): AST corpus extraction | D; deduplicated rows are not trained-model improvement; source/checker coupling. [T] [E] | UNKNOWN/defer; 2-4 audit / 3-5; consumer-scoped extraction with semantic tests | R-ATT-03, R-OUT-01 |
| 37 Arachne swarm (`agents/arachne/`): SQL-adapter frontier walking | D; fixed relations/nulls and adapter mismatch; no direct inspection. [T] [E] | UNKNOWN; 3-6 audit / 5-9; tiny graph walk with independent edge validation | R-PRV-02, R-WLD-01 |
| 38 Arachne damage (`agents/arachne/damage.py`): authored damage examples | D; authored algebra instances do not demonstrate emergent repair. [T] [E] | HISTORICAL CONTROL; 1-3 / 2-4; planted lesion/sham/rescue fixture | R-CAU-01 |
| 39 Icarus (`agents/icarus/`): LLM-edited dispatch file | D/U; cycle_018 absent, one lineage, payload shortcut possible not proven used. [A] [T] | UNKNOWN; 2-5 audit if recovered / 5-10; typed-failure rewrite baseline, separately authorized | R-INF-01, R-PRV-01 |
| 40 Nous (`agents/nous/src/`): concept sampling plus self-rated LLM output | D; one proposer/judge, no independent capability ruler. [T] [E] | RETIRE admission authority; 1-3 / 3-6; offline candidate generator plus executable check | R-INF-03, R-PRV-02 |
| 41 collider (`collider/src/model/genome.ts`): name-hash visualization | D; WebGL concept rendering, no experimental organism. [T] [E] | RETIRE from science core; 1-2 / 2-4; optional read-only result viewer | R-ATT-03 |
| 42 Koios MPA (`koios/scripts/mpa_area*.py`): scalar gate admission | V; tautological/constant gates; frozen DuckDB/data coupling not inspected. [S08] | RETIRE gates/HISTORICAL CONTROL; 1-3 / 3-5; adversarial falsifiable feature tests | R-MSR-01 |
| 43 Koios rank (`koios/scripts/rank_analysis.py`): sparse matrix SVD | D; 31x37, 108 observations; rank sensitive to missingness choices. [D-KO] | HISTORICAL CONTROL; 1-3 / 2-4; planted-rank missing-data benchmark | R-MSR-01 |
| 44 alien_circuitry (`alien_circuitry/`): finite-monoid distances/orbit table | D; analyst-supplied quotient, orbit-overlapping split, free kernel pruning. [D-KO] | EXTRACT oracle/HISTORICAL CONTROL; 4-8 / 6-12; tiny enumerated graph with orbit-disjoint split | R-WLD-01, R-MSR-03 |
| 45 sigma_kernel (`sigma_kernel/`): claim ledger/opcode dispatcher | D; claimant-supplied FALSIFY number and skipped upper-tier stubs. [D-KO] [T] | REBUILD adjudication/EXTRACT identity idea; 4-8 / 5-10; append-only evidence ledger with separate checker | R-PRV-02, R-PRV-03 |
| 46 prometheus_math (`prometheus_math/`): domain envs/tensor regressors | D; bounded domain/prior-driven tasks, substantial unread bodies. [D-KO] | UNKNOWN; 4-8 audit / 6-12; isolated exact domain oracle only if demanded | R-WLD-01, R-CAU-03 |

### Enforceable admission safeguards derived from these failures
These are proposed integration tests, not tests already passed; they operationalize existing requirements rather than amending the frozen design.
- **G01 Baseline closure:** reject a claim manifest missing any applicable constant, lookup, task-prior, definition or tuned same-class rung; record unmatched resource advantages explicitly. F01/F02/F04 -> R-MSR-01, R-MSR-02.
- **G02 Gate liveness:** mutate one required invariant at a time; each gate must fail for a demonstrated reason. Constant assignments and preprocessing-enforced equalities cannot count as independent checks. F03/F07/F11 -> R-MSR-01.
- **G03 Capacity certificates:** attach native, within-budget witnesses and transport/representation ceilings to each null cell. Missing witness means CAPACITY_UNESTABLISHED, not absent development. F03/F06/F09 -> R-DEV-01, R-SCI-02.
- **G04 Complete-state replay:** audit byte/state ownership, in-flight messages, hidden flags, clock/RNG state, and reset boundaries; require fork/restore equality and distinct hashes after a planted state change. F03/F05 -> R-REP-01, R-ORG-02.
- **G05 Repeated-demand test:** score first versus later trials separately and reset only declared state. A latch that passes pooled accuracy must fail the reusable per-trial label. F03 -> R-WLD-01.
- **G06 Intervention delivery:** prove the target changed, record off-target effects, include matched sham and rescue; unsupported or no-op interventions block necessity claims. F01/F05/F07 -> R-CAU-01, R-CAU-02.
- **G07 Information custody:** separate proposer/world/ruler permissions; ledger source exposure, planted witnesses, donor bytes and adapters; reject undeclared access instead of merely annotating it. F07/F08/F09 -> R-PRV-01, R-PRV-02.
- **G08 Independent novelty:** distinguish new seed, new composition, new mechanism and new author lineage; an answer-key grammar or same hidden field cannot qualify a stronger novelty level. F02/F04/F06 -> R-WLD-02, R-TRF-02.
- **G09 Statistical adversaries:** test singleton/empty/unequal/power-of-two clusters, zero effects and planted alternatives; validate coverage on independent generators and use the varying unit, not convenient row count. F09/F10 -> R-MSR-01, R-MSR-02.
- **G10 Clock reconciliation:** reconcile admissions, population state, event timestamps, timeout censoring and first-success clocks; an admitted coalition cannot disappear from acquisition-cost accounting. F06 -> R-CMP-01, R-TRF-01.
- **G11 Mutable-process declaration:** identify exactly which bytes/dynamics can change and which intervention distinguishes S, U and V; if unavailable, retain fixed-meta/library language and withhold Q6. F07 -> R-DEV-03.
- **G12 Claim correction chain:** preserve original verdict, later measurement, interpretation, and program disposition separately; invalidate dependent claims without rewriting their source artifacts. F01/F09/F10 -> R-PRV-03, R-OUT-01.
- **G13 Consumption and receipts:** before background execution, demonstrate one actual consumer, byte-complete artifact delivery and a decision changed by its output; a successful process exit is insufficient. F05/F12 -> R-ATT-01, R-ATT-03.
- **G14 Independent scientific path:** shared serialization is allowed, shared decisive solver/ruler code is not independent replication; document dependencies including these extracted utilities. F02/F04/F12 -> R-CAU-03.

### Build-versus-reuse decision and remaining gaps
- I: do not integrate all 46 rows. First isolate the protocol, complete-state replay, baseline/gate qualification and tiny exact-world checking. An initial selected-apparatus slice is estimated at 12-22 engineer-days versus 15-28 for a clean implementation; uncertainty is dominated by coupling, not code length.
- I: an independently implemented decisive checker adds an estimated 5-10 engineer-days either way; copied test logic is not that checker. If extraction takes longer than the replacement band or forces legacy semantics, choose the replacement. These are estimates, not a funded schedule.
- I: use PTE/Aether only as bounded local-physics comparators; do not rename them three independent tracks. The inspected assets do not already provide qualified addressed local rewrites or recurrent mutable-update dynamics for all of architecture tracks A/B/C. [ARCH:30-42][ARCH]
- I: start without legacy code by building tiny native transitions, an independent exact checker, a run/receipt contract, and deliberately breakable positive/negative controls. Reuse only fixtures that reduce this cost without supplying the target explanation.
- U: no full source audit, import check, test-suite run, clean-machine rerun, or performance/energy benchmark was done. No component is certified deployable by this report.
- U: Icarus's reasoner, parts of Cosmos C3, Theseus's large corpus and Nous's disk-only rows remain off-tree/withheld according to the crawler. This is absence from inspected evidence, not proof that they do not exist. [T:477-505][T]
- U: LM01, WTP-04, Tyche Block M/natural-residual trials, Aphrodite natural recurrence/mutable-improver work and Aether E-012 are not promoted from plans to results. Their status is bounded by the frozen records, not present-day execution knowledge. [T:420-424][T]
- U: no estimate here establishes the population frequency of competent mechanisms. Admission-biased worlds, small author lineages, narrow budgets and unmeasured search-hit probabilities remain major limits. [S03] [S04] [S23] [ARCH:90-114][ARCH]
- Documentary validation passed (exit 0): 40 citation targets and registered blobs, cited line bounds, 31 requirement IDs, all 46 inventory rows, index counts and requested report length; tracked and staged diffs are empty. Future integration must add/update and run G01-G14 tests before treating salvage as qualified.
- Delivery note: this report exists on disk but is untracked and ignored by the existing `.gitignore:292` rule `docs/*`; it was not staged, and the ignore rule was not changed.

### Citation targets
[REQ]: ../REQUIREMENTS.md
[ARCH]: ../RSE_ARCHITECTURE.md
[T]: ../../../intake/tantalus/REPORT.md
[A]: ../../../intake/tantalus/artifact_index.jsonl
[E]: ../../../intake/tantalus/engine_index.jsonl
[S01]: ../../../../../ensorain/WTP02_OPERATOR_RULING.md
[S02]: ../../../../../ensorain/wtp2/world2.py
[S03]: ../../../../../ensorain/ENSORAIN_WTP03_REPORT.md
[S04]: ../../../../../roles/Ananke/pte/C1_ERRATA.md
[S05]: ../../../../../prometheus/ananke/engine.py
[S06]: ../../../../../roles/Cosmos/research/RESULTS.md
[S07]: ../../../../../prometheus/cosmos/phenomenon.py
[S08]: ../../../../../koios/scripts/mpa_area1_moment_ratio.py
[S09]: ../../../../../theseus/synth/collide.py
[S10]: ../../../../../roles/Aphrodite/engine/improver.py
[S11]: ../../../../../roles/Aphrodite/engine/run_s3s4.py
[S12]: ../../../../../tyche/audits.py
[S13]: ../../../../../nyx/specimens/diomedes_k0_census/FAILURES.md
[S14]: ../../../../../ops/campaigns/C-002/E-009/RESULT.md
[S15]: ../../../../../Aether/observatory/aeth03_propagation.py
[S16]: ../../../../../ergon/gen1b/ANNOTATION_2026-09-11_headline_falls.md
[S17]: ../../../../../ergon/gen3/p3_common.py
[S18]: ../../../../../roles/Polyhymnia/ledgers/probe_01_lincode_2026-09-11.md
[S19]: ../../../../../roles/Polyhymnia/science/lincode_decoders.py
[S20]: ../../../../../roles/Ensorain/journal/2026-09-24.md
[S21]: ../../../../../roles/Tyche/TODO.md
[S22]: ../../../../../roles/Polyhymnia/prompts/2026-09-11_reactivation_direction/OPERATOR_DIRECTIVE.md
[S23]: ../../../../../tyche/runs/v1_2026-09-30/REPORT_v1.md
[S24]: ../../../../../tyche/runs/v2_blockR/REPORT_BLOCK_R.md
[S25]: ../../../../../roles/Diomedes/coordinate_census.py
[S26]: ../../../../../ergon/gen1b/gen1_run.py
[S27]: ../../../../../Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py
[S28]: ../../../../../roles/Diomedes/REVIEW_ROUND2_CORRECTIONS_2026-08-25.md
[D-TH]: ../../../intake/tantalus/seats/Theseus.md
[D-AP]: ../../../intake/tantalus/seats/Aphrodite.md
[D-ER]: ../../../intake/tantalus/seats/Ergon.md
[D-KO]: ../../../intake/tantalus/seats/Koios.md
[D-TY]: ../../../intake/tantalus/seats/Tyche.md
[D-AE]: ../../../intake/tantalus/seats/Aether.md
[D-PO]: ../../../intake/tantalus/seats/Polyhymnia.md