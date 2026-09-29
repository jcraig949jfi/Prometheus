# Harvest D5 -- older lines (Mar-Aug 2026) and the external deep-research corpus

domain: D5 = the program's older lines (math discovery, LLM evolution, tensor/cross-domain exploration) + external deep-research corpus, harvested for relevance to the current North Star (grown, not designed, sagacity).
paths covered: aporia/docs/ (deep_research_batch_2026-05-10..14, _2026-08-17 answers, _2026-08-27, _2026-09-17, deep_research_reports/ apo_/lad_/tsc_/erg_/moros_ files, prometheus_pivot_research_batch1/, gemini_research_synthesis + queue, gemini_d4 dispatch, top-level DOCTRINE/CYCLE/germline/perpetual/PROGRAM_SUMMARY/META_SYNTHESIS/science_of_failure/EXTERNAL_REVIEW docs); apollo/ (pivot/, wall_corpus/); harmonia/ (memory/, probe/, proposals/, docs/, agents/iris); cartography/docs; ergon/ (gen1, gen1b, gen3, kouvaris2017, avida2003, docs); techne/ (research/evolution-as-learning, acquisition/poet_alife, loop/HITL_LOG, ARSENAL_ROADMAP); forge/ (architecture docs); exploratory/tensor_decomp_qd; prometheus_math/; zoo/conjecture_gp; sigma_kernel/; theseus/; ignis/; arcanum/docs; whitepapers/; roles/ of Apollo-era and archaeology-era seats listed in the brief.
paths NOT covered: the ~400 math-conjecture deep-research reports (stygian_, lethe_, argos_, achero, hypati, para_p, tens_, follow-up rows) -- title-screened as pure math and skipped; deep_research_batch5..10 dirs (seed titles only, math); erebos_v2 designs (sampled, one hit folded in); arcanum/ bulk (879 md, filename/heading sample only); code files (not read); koios/ (three result files, no narrative -- nothing harvested).
method: READ-ONLY. ls/find for titles, grep -n for open-question/future-work/lesson/null/tautology/compress/inherit/library vocab, sed -n on hits; six parallel read-only sub-scans, then every quote below re-located with grep -nF in this worktree (tip d7ec26d37, 2026-09-27). sha/date = commit that ADDED the file (git log --diff-filter=A), not necessarily the commit that wrote the quoted line. Quotes are verbatim except for ASCII normalization (em-dash -> "--", arrows -> "->", curly quotes -> straight, Delta -> "D", section sign -> "S").
counts: 58 candidates. By kind (primary): open-question 12, unfollowed-recommendation 12, prior-art-held 11, defect-ambiguity 6, anomaly 5, parked-experiment 5, directive-idea 4, contradiction 3. prior-art-gap items (Toussaint detector vs Crius; unfiled D4 dispatch) are in Cross-domain pointers; future-work items were merged into the thread they name.
later-evidence checks: current seat STATUS files (Aphrodite 9490f3f34, Ares 3f68be2b9, Cosmos ffd9887b6, Ananke, Crius, Ensorain; all 2026-09-25/26) and targeted greps across crius/, archaeon/, agent_d4_blind/, engine queues. "none found" means a bounded grep, not a proof of absence.
grouping: A heredity / inheritance of experience (01-12); B representation, compression, library learning (13-27); C variation, selection, open-endedness (28-41); D falsification instruments (42-52); E lineage, provenance, corpus hygiene (53-58).

## A. Heredity and inheritance of experience

### H-D5-01 Prometheus-minus-Prometheus: does the inherited machinery earn its keep?
- source: aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md:157,162 @ 1902bbc79 (2026-08-25), seat Aporia; quote: "3. **Prometheus-minus-Prometheus**: ablate the inherited machinery -- no forge ontology, no historical" ... "The third is the killer and should eventually be run regardless of the others."
- kind: unfollowed-recommendation
- question: At matched budget, does a lineage that inherits the program's libraries, failure corpora and learned proposers beat a generic typed enumerator that inherits nothing?
- why it might matter now: The North Star claims inheritance of experience is load-bearing; no engine has run the whole-stack ablation. Bears on Aphrodite (transplant), Crius, Ares.
- later evidence: none found (no commit names this arm being run). Aphrodite S4 ABSTRACTION_TRANSPLANT YES (roles/Aphrodite/STATUS.md:22 @ 9490f3f34) is a narrow, single-abstraction instance, not the whole-stack ablation.
- lenses: Aphrodite, Crius, Archaeon
- related: H-D5-05, H-D5-06, H-D5-20

### H-D5-02 Does a compression tell the system what to acquire next, or only describe what worked?
- source: aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md:188,197 @ 1902bbc79 (2026-08-25), seat Aporia; quote: "> Does this representation merely describe what already worked, or does it tell the system what" ... "Compression is widely used as an abstraction-SELECTION signal, but the marginal causal value of a"
- kind: open-question
- question: Does a compact handle (abstraction, primitive, memory key) causally increase downstream reachability, versus being a post-hoc summary? This is the sagacity anchor stated operationally.
- why it might matter now: Core test for Ensorain's tensor memory and Crius's reuse accessibility; DreamCoder/LILO/Stitch use compression to select, not to direct.
- later evidence: Aphrodite S3 ENDOGENOUS_ABSTRACTION YES (roles/Aphrodite/STATUS.md:20) is partial support for "tells what"; no general test found.
- lenses: Ensorain, Crius, Aphrodite, BEE z80atlas
- related: H-D5-14, H-D5-15, H-D5-24

### H-D5-03 The germline four-arm edge test (design vs random vs shuffled specialization)
- source: aporia/docs/germline_design_2026-08-17.md:116 @ 12a70a901 (2026-08-17), seat Aporia; quote: "CREDIT iff  x2 > x1  (design beats random)  AND  x3 ~= x1  (the specialization is load-bearing)"
- kind: parked-experiment
- question: When a parent produces a child, credit the heredity edge only if a designed child beats a random child AND shuffling the child's specialization removes the gain.
- why it might matter now: A ready-made admissibility rule for heredity claims in Aphrodite and any NPE/BEE lineage; guards against "the child was just better seeded".
- later evidence: none found as a standing gate.
- lenses: Aphrodite, Archaeon, NPE Z80 worlds
- related: H-D5-04, H-D5-05

### H-D5-04 Autonomous depth: how many generations can verified improvement propagate?
- source: aporia/docs/germline_design_2026-08-17.md:125 @ 12a70a901 (2026-08-17), seat Aporia; quote: "> **How many generations away from Master can verified capability improvement propagate without"
- kind: directive-idea
- question: Is "depth of verified improvement without re-seeding" a usable North Star metric, and what guards stop it being gamed (chain-splitting, sibling duplication, depth-1 quitters)?
- why it might matter now: Heredity is only real if gains compound across generations. Bears on Aphrodite's BOUNDED_RSI (NOT YET ESTABLISHED) and Nestor's depth-1 wall.
- later evidence: f4dae7a66 (2026-09-18, Crius) reports the frozen ratio metric rewards a depth-1-only quitter; 5a3c4a800 (2026-09-24, Nestor) "depth-1 wall mined to energy-pressure cells". The metric is live and already showing a gaming mode.
- lenses: Aphrodite, Archaeon, Ares
- related: H-D5-03, H-D5-37

### H-D5-05 Unit of inheritance: toolkit only, or toolkit plus failure residue?
- source: aporia/docs/germline_infrastructure_2026-08-17.md:152 @ 7fbfa8697 (2026-08-17), seat Aporia; quote: "**The inheritance rule:** a child is born with the SDK and its charter -- nothing else. Tool"
- kind: open-question
- question: The old germline passed on tools, not experience. What is the right unit of inheritance, and does adding a typed failure record change descendants' performance?
- why it might matter now: The North Star names "inheritance of experience"; no engine yet compares toolkit-only vs toolkit+residue inheritance. Crius, Ensorain.
- later evidence: none found.
- lenses: Crius, Ensorain, Archaeon
- related: H-D5-06, H-D5-07, H-D5-09

### H-D5-06 The loop audits and resumes but does not yet learn from failure
- source: aporia/docs/perpetual_engine_design_2026-08-17.md:342,345 @ 9f6dd1782 (2026-08-17), seat Aporia; quote: "now serves: **the first time a failure demonstrably improves a descendant** -- failure -> residue" ... "audits, researches, measures, and resumes -- and does not yet learn."
- kind: open-question
- question: Has any engine closed failure -> residue -> intervention -> descendant -> improvement, with an ablation showing the failure record was causal?
- why it might matter now: "Failure is evidence" is a premise; this names the missing demonstration. Aphrodite, Ares, SFE.
- later evidence: none found that meets the full chain with ablation.
- lenses: Aphrodite, Ares, Archaeon
- related: H-D5-09, H-D5-10, H-D5-12

### H-D5-07 Wisdom as prose vs a typed, navigable lesson
- source: whitepapers/icarus_synthetic_reasoning_v01_2026-05-27.md:217 @ ec43509b2 (2026-05-27), seat Icarus; quote: "**5.3 Wisdom is text, not typed gradient.** `wisdom.py` extracts recurring failure reasons from `outcome.json` and writes them as Markdown."
- kind: defect-ambiguity
- question: Should the lesson a generation hands down be a typed structure (kill path, trigger spec, nearby survivors, failure axis) rather than Markdown? What handle format lets a receiver reconstruct the richer lesson?
- why it might matter now: This is the sagacity handle-format question in its earliest form. Bears on Ananke (packet communication) and Aphrodite (what the improver passes on).
- later evidence: none found.
- lenses: Ananke, Aphrodite, Ensorain
- related: H-D5-08, H-D5-05

### H-D5-08 Reinjection: the literal sagacity test, specified in March and never built
- source: arcanum/docs/FUTURE_FEATURES.md:19 @ ffb3639d4 (2026-03-22), seat Arcanum; quote: "-   **Systematic Reinjection Framework:** Build a dedicated module for automatically testing the utility of discovered Arcanum." Also whitepapers/xenolexicon.md:115 @ 57caa85f9 (2026-04-23): "### 3.7 Stage 7: Reinjection (Future Work)"
- kind: parked-experiment
- question: When a discovered, named, compressed concept is handed back to a receiver, does the receiver do measurably better than without it (and better than a random-name control)?
- why it might matter now: Direct operationalization of "compact handle -> richer lesson". Ananke packets and Ensorain memory keys are the current carriers.
- later evidence: none found (no reinjection code in arcanum/).
- lenses: Ananke, Ensorain, Aphrodite
- related: H-D5-02, H-D5-07

### H-D5-09 Does conditioning proposals on the failure corpus beat blind proposals?
- source: roles/Lexis/PLAN_2026-08-25.md:206-207 @ 80ded3fb1 (2026-08-25), seat Lexis; quote: "experiment shows P(useful primitive | F) > P(useful primitive) at matched proposal" / "budget. Note the framing: the corpus is an UNTESTED F_n in the closure"
- kind: unfollowed-recommendation
- question: At matched proposal budget, is P(useful primitive | failure corpus) > P(useful primitive)?
- why it might matter now: The cleanest direct test of "failure is evidence". SFE, Aphrodite and Archaeon all assume it.
- later evidence: none found.
- lenses: SFE, Aphrodite, Archaeon
- related: H-D5-06, H-D5-10, H-D5-12

### H-D5-10 Richer failure traces may be exhaust, not signal
- source: aporia/docs/deep_research_batch_2026-08-17/11_does_failure_trace_richness_change_downstream_learnability_answer.md:197,199 @ ef567d9f1 (2026-08-17), seat Aporia (external DR); quote: "The fact that your records consist of 413 million verdict-shaped rows with an unpopulated kill-vector field may not be a bug; it may be an optimal compression state."
- kind: contradiction
- question: Does a richer failure representation measurably help a downstream learner over bare verdicts (an ERM baseline)? The external review says: establish that before investing.
- why it might matter now: Contradicts the default "more failure structure is better" in Archaeon and Ensorain; it is a testable fork, not a settled point.
- later evidence: none found.
- lenses: Archaeon, Ensorain, Ares
- related: H-D5-09, H-D5-11, H-D5-57

### H-D5-11 The "learnable gradient field" over kills was a lookup table
- source: prometheus_math/KILL_VECTOR_LEARNER_RESULTS.md:237 @ 9755008d8 (2026-05-04), seat prometheus_math lane; quote: "No generalisation beyond memorisation. Day 5 navigation founded on this learner is **just lookup**"
- kind: prior-art-held
- question: When an engine learns from its kill ledger, does it generalize beyond per-cell means? The recorded cause: only aggregates were stored, so nothing per-candidate could be learned.
- why it might matter now: A cautionary result for any improver trained on failure logs (Aphrodite) and for Crius's reuse measures.
- later evidence: remedy (per-candidate kill_vector persistence) proposed at :281; no retest found.
- lenses: Aphrodite, Crius, Archaeon
- related: H-D5-10

### H-D5-12 Does the failure frontier deform before fitness moves?
- source: techne/research/evolution-as-learning/FAILURE_LANDSCAPE_IMPLICATIONS.md:22 @ 111447d9f (2026-09-03), seat Techne; quote: "**Does the failure frontier deform before macroscopic adaptation is visible?**"
- kind: open-question
- question: Track the distribution of offspring outcomes around a fixed parent across history. If its shape changes while mean fitness is flat, history has changed the generator -- an early, fitness-free signal of heredity. The follow-on E1 attempt (techne/research/evolution-as-learning/E1_RESULT_INSTRUMENT_FAILURE.md:21 @ 468a1f9ba, 2026-09-04: "therefore NOT a null, NOT evidence for K2, and NOT a bounded negative result.") failed on the instrument, so K2 is still open.
- why it might matter now: Gives Archaeon a measurable pre-fitness lineage signal; bears on Aphrodite's "does history change the improver".
- later evidence: E1 is an instrument failure (overlap/positivity check missing, :87); no rerun found.
- lenses: Archaeon, Aphrodite, Ensorain
- related: H-D5-06, H-D5-44

## B. Representation, compression, library learning

### H-D5-13 The ceiling belongs to the representation; does the ecology ever move it?
- source: aporia/docs/PROGRAM_SUMMARY_2026-08-24.md:69,133 @ 66e06e027 (2026-08-24), seat Aporia; quote: "**0.833 is the substrate's ceiling, not evolution's.** The remaining 16.7% is unreachable by any" ... "not the lever. The question that matters is: *when Hephaestus mints a primitive, does the ceiling"
- kind: anomaly
- question: Every observed ceiling rise in the older line came from a human widening the representation. When a primitive or compression is minted from inside the ecology, does the reachable optimum move? That, not search efficiency, is the co-evolution metric.
- why it might matter now: The North Star's claim is that representations co-evolve; this is the discriminating measurement. Aphrodite, Crius, Ares.
- later evidence: Aphrodite S3/S4 YES (roles/Aphrodite/STATUS.md:20-22) is the first in-ecology abstraction that transfers; whether it moves a ceiling (vs speed) is not stated.
- lenses: Aphrodite, Crius, Ares, NPE Z80 worlds
- related: H-D5-14, H-D5-28, H-D5-37

### H-D5-14 "Primitives are fixed, routing evolves": the old design stance the North Star reverses
- source: roles/EvolutionaryArchitectAndReasoningSpeciesEngineer/Apollo_Role_Document.md:246 @ b56c7401a (2026-04-04), seat EvolutionaryArchitectAndReasoningSpeciesEngineer (Apollo); quote: "9. **Primitives are fixed. Routing evolves.** I compose, I don't redesign. The atoms are Forge's job. The molecules are mine."
- kind: contradiction
- question: The Apollo line hit a vocabulary ceiling under fixed atoms. Which current engines still freeze their primitive set, and is their ceiling a vocabulary ceiling?
- why it might matter now: Contradicts the co-evolution premise; worth auditing Crius and NPE/BEE primitive sets for the same freeze.
- later evidence: roles/Lexis/PLAN_2026-08-25.md:205-208 ties Apollo's stall to "the vocabulary C".
- lenses: Crius, NPE Z80 worlds, BEE z80atlas
- related: H-D5-13, H-D5-15

### H-D5-15 Automate vocabulary growth from recurring sub-patterns (the queued deep-dive never fired)
- source: aporia/docs/gemini_research_synthesis_2026-05-11.md:400 @ cf2438a5d (2026-08-18; content dated 2026-05), seat Aporia (external DR); quote: "**For Prometheus, this means substrate-vocabulary expansion can itself be automated** -- when many composite witnesses repeatedly co-instantiate the same sub-pattern, automatically promote to a new primitive."
- kind: unfollowed-recommendation
- question: Should recurring co-instantiated sub-patterns be promoted into the representation automatically, under selection? The follow-up (DR-411, a Stitch/LILO/TacMiner deep spec) sits in aporia/docs/gemini_research_queue/queue.jsonl:411 but not in fired_log.jsonl.
- why it might matter now: This is library learning as the mechanism by which representations co-evolve. Crius, Aphrodite.
- later evidence: none found for DR-411. Of 423 queued DR items, 57 were fired.
- lenses: Crius, Aphrodite, Ensorain
- related: H-D5-16, H-D5-18, H-D5-19

### H-D5-16 A composite chain that keeps being re-derived implies a missing primitive (never tested)
- source: roles/Atalanta/SALVAGE_ASSESSMENT_2026-09-11.md:66-68 @ 827d021eb (2026-09-11), seat Atalanta; quote: "Its premise is the part worth recording rather than the code: "a composite" / "chain that keeps being re-derived implies a missing primitive that should" / "be named and registered." That premise was never tested, at any point, by"
- kind: open-question
- question: Does the re-derivation frequency of an unnamed composite predict that naming it will pay off (in reach, not only speed)?
- why it might matter now: A cheap, observable selection signal for representation growth. Crius, Ensorain.
- later evidence: none found.
- lenses: Crius, Ensorain, Archaeon
- related: H-D5-15, H-D5-19

### H-D5-17 Learned libraries mostly aren't reused (the library-learning ablation crisis)
- source: aporia/docs/deep_research_batch_2026-08-17/04_library_learning_and_abstraction_discovery_canon_band_s_lemm_answer.md:77,109 @ 71f3cfa9b (2026-08-17), seat Aporia (external DR); quote: "Their findings were unequivocal: **Function and lemma reuse in LEGO-Prover and TroVE was extremely infrequent, bordering on non-existent** [cite: 13, 14]."
- kind: prior-art-held
- question: Do Crius-style reuse claims survive a leave-one-out library mask and a compute-matched baseline? The report treats a spread of single-use abstractions as the sign that library learning failed.
- why it might matter now: Crius measures reuse accessibility, and Archaeon campaign2 already reports "direct reuse 0.06-0.60".
- later evidence: archaeon/campaign2/CAMPAIGN_REPORT.md:177 adopts direct reuse; no compute-matched leave-one-out found.
- lenses: Crius, Archaeon
- related: H-D5-18, H-D5-20

### H-D5-18 Winning tools used 0% of their own primitive libraries
- source: forge/ARCHITECTURE_T2_T3.md:14 @ b674a9976 (2026-04-03), seat Forge/PipelineOrchestrator; quote: "2. **Winning tools used 0% of their own primitive libraries** -- primitives were decoration"
- kind: prior-art-held
- question: Is an engine's inherited library actually on the causal path of its winners, or is it decoration? The same pattern recurs as Apollo's "decorative branches".
- why it might matter now: Cheap audit for Aphrodite's donor library and Crius's reuse stores.
- later evidence: none found as a standing audit.
- lenses: Crius, Aphrodite, Archaeon
- related: H-D5-17, H-D5-19

### H-D5-19 The severed library: reconnecting an old library looks like synthesis
- source: aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md:4 @ c666081a1 (2026-08-24), seat Aporia; quote: "**Apollo v1's instruction set and Hephaestus's primitive library are the same 25 functions**, and the"
- kind: defect-ambiguity
- question: When an architecture rewrite drops a library, a later "acquisition" can simply be reconnecting it. Can lineage tell retrieval apart from real synthesis? The port-vs-mint question is recorded as open at aporia/docs/SALVAGE_ARC_AND_DISCRETE_CONTROLS_2026-08-25.md:205 ("a rewrite is **untested**.").
- why it might matter now: Every "endogenous abstraction" claim (Aphrodite S3) needs this retrieval-counterfeit check. Crius, Archaeon.
- later evidence: none found.
- lenses: Archaeon, Crius, Aphrodite
- related: H-D5-20, H-D5-42

### H-D5-20 IQ-NULL: a no-op operator must move the score by exactly zero
- source: aporia/docs/CYCLE_156S_SEVERED_LIBRARY_2026-08-24.md:64 @ c666081a1 (2026-08-24), seat Aporia; quote: "If it is not zero, then adding *any* op to the pool moves the ceiling, which would mean the assay is"; frozen as aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md:172 ("IQ-NULL      type-compatible no-op + already-solved-category port. Both DE exactly 0.")
- kind: parked-experiment
- question: Does adding a type-compatible no-op (or a port for an already-solved category) change the measured ceiling? If it does, the assay measures search dynamics, not expressivity.
- why it might matter now: A cheap sanity rung for Crius's accessibility frontier, Aphrodite's transplant, and NPE operator pools.
- later evidence: none found.
- lenses: Crius, Aphrodite, NPE Z80 worlds
- related: H-D5-13, H-D5-19, H-D5-42

### H-D5-21 Library-learning family choice parked: DreamCoder/Stitch vs Ruler/babble/Enumo
- source: techne/ARSENAL_ROADMAP.md:119 @ 0b90496fc (2026-04-25), seat Techne; quote: "Whether Family A (DreamCoder/Stitch) or Family B ("
- kind: unfollowed-recommendation
- question: Which compression family (abstraction-by-refactoring vs rewrite-rule discovery) fits co-evolving representations? The decision was deferred to Lexis and never made; the stitch_core wheel is "held pending a scientific decision".
- why it might matter now: Crius and Ensorain are building compression machinery without this prior-art decision.
- later evidence: techne/LICENSING_AND_COSTS_2026-09-10.md:48 records the Stitch licence as still unresolved; no decision found.
- lenses: Crius, Ensorain
- related: H-D5-15, H-D5-17

### H-D5-22 Reuse is threshold-then-plateau: the first reuse is where selection acts
- source: ergon/gen1b/REVIEW_PACKET_GEN1B_2026-09-01.txt:365-367 @ 83733abbe (2026-09-01), seat Ergon; quote: "The only steep transition is the FIRST one: 44% of artifacts never earn a" / "single credit, but an artifact that has earned two has a ~75-85% chance of" / "earning another, indefinitely. This is a threshold-then-plateau structure, not"
- kind: prior-art-held
- question: Does reuse in Crius stores and Ensorain memory show the same threshold-then-plateau? If so, selection pressure (and measurement) should focus on first reuse.
- why it might matter now: A ready-made structural prediction for Crius; the P3 annotation explicitly does not retract it.
- later evidence: not cited in crius/ or ensorain/ (grep) -- held but unused.
- lenses: Crius, Ensorain
- related: H-D5-23, H-D5-17

### H-D5-23 Memory capacity, not retention order, is the untested question
- source: ergon/gen3/REVIEW_PACKET_P3_2026-09-11.txt:236 @ 596e36fe2 (2026-09-11), seat Ergon; quote: "cap. The next question is the CAP itself (ERGON-06 re-premised)."
- kind: unfollowed-recommendation
- question: At cap 64, eviction order made a bounded, negligible difference. Before designing retention rules for tensor or packet memory, does memory capacity itself matter?
- why it might matter now: Directly bears on Ensorain's memory-vs-null ladder and Ananke's packet buffers.
- later evidence: ERGON-06 appears only in the gen3 prereg/packet; not run.
- lenses: Ensorain, Ananke, Crius
- related: H-D5-22, H-D5-24

### H-D5-24 Label-free evaluation of an endogenous memory index is still open
- source: aporia/docs/deep_research_batch_2026-08-27/report_ENDOGENOUS_MEMORY_GEOMETRY.md:156,158,162 @ a566a5517 (2026-08-29), seat Aporia (external DR); quote: "- Does any label-free evaluation protocol exist stronger than geometric agreement with a" ... "Nothing tests an index against a criterion the system itself generated --" ... "- Is the invariance set, rather than the labels or the metric, the real bottleneck?"
- kind: open-question
- question: Can tensor memory be scored against a criterion the system generates itself (predictive compression of future observations, description length of the indexed corpus), and who chooses what counts as "the same memory"?
- why it might matter now: Ensorain's null ladder uses external metrics; MDL/predictive compression would tie memory evaluation to the sagacity anchor.
- later evidence: the report says the closest area came back unsearched, not negative (:101). None found since.
- lenses: Ensorain, Cosmos
- related: H-D5-02, H-D5-25, H-D5-26

### H-D5-25 Two representations "agree" (Mantel r=0.94), but the random-projection control was never run
- source: harmonia/docs/m1_round3_tasks.md:6 @ d83859ff4 (2026-04-12), seat Harmonia; quote: "**The 41D tensor and the 5D phonemes see the same geometry.** Mantel r = 0.94, z = 118." Against it: cartography/docs/harmonia_adversarial_review.md:191 @ a8fb3556e (2026-04-13): "2. **Phoneme projections are hand-crafted.** No random projection control." And ergon/docs/phoneme_warning.md:7 @ 98a6590ab (2026-04-14): "to these axes via `DOMAIN_PHONEME_MAP`. This was a constructed coordinate system,"
- kind: contradiction
- question: Is agreement between two memories evidence of shared structure, or of shared magnitude and hand-built axes? The null ladder needs a random-projection/PCA rung.
- why it might matter now: Ensorain compares tensor memory against nulls; Cosmos compares invariants across worlds. Both can be fooled by constructed coordinates.
- later evidence: no record that the fix at harmonia_adversarial_review.md:201 was run.
- lenses: Ensorain, Cosmos
- related: H-D5-26, H-D5-27

### H-D5-26 Map which structures admit which tensor-train compressions, with known-rank controls; remove the dominant background first
- source: harmonia/memory/methodology_toolkit.md:332,350 @ 8f5632d2d (2026-04-20), seat Harmonia; quote: "admit which TT compressions, mapped rather than proved." ... "Meaningful compression exists; awaiting Phase-2 lineage check." Also aporia/docs/prometheus_pivot_research_batch1/report_19_tensor_decomposition_substrates.md:55 @ cf2438a5d (2026-08-18): "**Illusory low-rank from prime atmosphere (feedback_prime_atmosphere.md):** if 96% of cross-dataset structure is primes, naive TT will report low bond rank simply because the dominant signal is everywhere."
- kind: parked-experiment
- question: Could a rank-vs-error Pareto map (with planted rank-1 and incompressible controls, before/after detrending the dominant background) serve as Ensorain's null ladder?
- why it might matter now: Ensorain is literally tensor memory vs a null ladder; this is held prior art from the April TT engine.
- later evidence: Phase 2 never done (no DMRG/spectral descriptors found).
- lenses: Ensorain, Cosmos
- related: H-D5-24, H-D5-25

### H-D5-27 A null blamed on the representation, not the relationship
- source: cartography/docs/cross_landscape_findings.md:30 @ cf2438a5d (2026-08-18), seat Charon/Cartography; quote: "The failure is in the OEIS representation, not in the relationship."
- kind: defect-ambiguity
- question: When a compression is degenerate, how does an engine decide whether a null is the representation's fault or a real absence? Under co-evolution, representations should be selected, not assumed, and the null should be re-run under rival representations.
- why it might matter now: Cosmos and Ensorain nulls. Polyhymnia's rival structured decoders (roles/Polyhymnia/STATUS.md:37 @ 6580169fa: "8/8 controls PASS; M1 direction right; M2 direction WRONG (ledgered);") are a concrete way to supply rivals.
- later evidence: none found.
- lenses: Cosmos, Ensorain, NPE Z80 worlds
- related: H-D5-25, H-D5-50

## C. Variation, selection, open-endedness

### H-D5-28 Apollo exploited and never discovered; the LLM added zero lift over deterministic search
- source: apollo/pivot/APOLLO_REVIVAL_REVIEW_2026-09-01.md:53,55 @ 96ee6fac8 (2026-09-01), seat Apollo; quote: "deterministic numbers EXACTLY. Zero lift from the model." ... "Apollo exploits. It has not been shown to discover. Of its 5 documented"
- kind: anomaly
- question: Does selection pressure alone ever create new machinery, or only exploit what a human added? Does a learned (LLM) proposer earn its cost over a matched deterministic mutator?
- why it might matter now: Ares (pressure-induced machinery) and Aphrodite (improver-of-improvers) should carry the "human widened the substrate" control and a matched deterministic-mutator arm.
- later evidence: Ares cycle 2 (roles/Ares/STATUS.md:18 @ 3f68be2b9) "wins on SPEED, not capability" -- consistent with exploitation; Cosmos "selection not shown necessary" (roles/Cosmos/STATUS.md:12).
- lenses: Ares, Aphrodite
- related: H-D5-13, H-D5-29, H-D5-37

### H-D5-29 Offspring viability: AST-only mutation failed; the validity-projecting wrapper was never tried
- source: roles/EvolutionaryArchitectAndReasoningSpeciesEngineer/Apollo_Role_Document.md:34 @ b56c7401a (2026-04-04), seat EvolutionaryArchitectAndReasoningSpeciesEngineer; quote: "**The v1 Apollo run proved AST-only mutation is insufficient.** 190 generations, zero organisms beat NCD." Also exploratory/tensor_decomp_qd/PROJECT_SUMMARY_FOR_REVIEW.md:160 @ a685fec82 (2026-04-25): "- Validity-projecting wrapper around arbitrary mutations: untested; the hard part is solving the validity manifold projection problem cheaply"
- kind: unfollowed-recommendation
- question: How viable must offspring be for selection to do anything (3-8% viability in Apollo v1; 0% validity for LLM mutations in tensor QD)? Can the variation operator itself evolve to project onto the valid set?
- why it might matter now: The variation operator is part of what should co-evolve; bears on NPE/BEE mutation design and Aphrodite.
- later evidence: none found for the wrapper.
- lenses: NPE Z80 worlds, BEE z80atlas, Aphrodite
- related: H-D5-30, H-D5-28

### H-D5-30 Recombination, not single-step mutation, makes the substrate searchable; some faults show only in population structure
- source: apollo/wall_corpus/MANIFEST.md:71,89-90 @ e15179255 (2026-08-15), seat Apollo; quote: "2026-06-16 recombination finding: **the recombination operator, not the single-step" ... "coverage at control values. The fault is real and visible only in population structure" / "(31 cells vs the control's 878-956). A detector that fires only on accuracy loss will"
- kind: prior-art-held
- question: Do current engines' variation operators include crossover/union moves, and is ablating one mutation move invisible while crossover is on? Do falsification tools detect faults that change population structure but not fitness? The wall corpus holds 26 labelled walls in 4 failure classes for testing this.
- why it might matter now: Ares, Aphrodite, NPE operator design; Archaeon needs population-structure detectors.
- later evidence: wall-corpus F1 replicates single-move ablation parity under crossover.
- lenses: Ares, NPE Z80 worlds, Archaeon
- related: H-D5-29, H-D5-31

### H-D5-31 Shape-keyed novelty inflates for free; archives do not collapse near-duplicates
- source: aporia/docs/META_SYNTHESIS_2026-08-12_v1.md:667-668 @ 7d87b8a48 (2026-08-12), seat Aporia; quote: "*(1) Shape-keyed novelty inflates trivially* -- Apollo's 2,860 cells / 2,846 "distinct shapes"" / "produced **zero** accuracy lift, so the suite cannot key novelty on unrecognized shape." Also apollo/pivot/recombination_findings_2026-06-16.md:87 @ bb2037496: "op-duplication; that's an open instrumentation debt."
- kind: anomaly
- question: Does a new phenotype class or behaviour-descriptor cell count as progress? Do diversity counts collapse organisms that differ only by redundant ops?
- why it might matter now: BEE z80atlas and NPE archives count cells/phenotypes; S3_REWRITE had 11,717 phenotype classes and fragmented accessibility (agent_d4_blind/VERDICT-PHASE1.md:20).
- later evidence: type_bridge/LINEAGE.md:151 still records archive inflation as open (sub-scan report, not re-read here).
- lenses: BEE z80atlas, NPE Z80 worlds, Crius, Cosmos
- related: H-D5-32, H-D5-33, H-D5-40

### H-D5-32 QD/novelty is bottlenecked by human-authored behaviour descriptors; failure archives have precedent
- source: aporia/docs/deep_research_batch_2026-08-17/08_quality_diversity_and_open_endedness_canon_band_h2_answer.md:77,100 @ 71f3cfa9b (2026-08-17), seat Aporia (external DR); quote: "QD and NS algorithms are fundamentally bottlenecked by the human-crafted Behavioral Descriptor (BC) [cite: 7]." ... "**The answer is definitively YES.** There is strong, highly relevant academic precedent for maintaining explicitly indexed failure archives"
- kind: unfollowed-recommendation
- question: Can behaviour descriptors themselves be evolved or learned rather than authored? Should kill regions actively repel search (the JADE / adversarial-MAP-Elites archive of eliminated solutions, :191) instead of only being logged?
- why it might matter now: A hand-authored descriptor is a hand-designed prior the North Star warns against. BEE, NPE, SFE, Ares.
- later evidence: JADE cited only in frontier_campaign_69 dossiers and archaeon CROSSWALK; no engine uses a repelling failure archive (sub-scan grep).
- lenses: BEE z80atlas, NPE Z80 worlds, SFE, Ares
- related: H-D5-31, H-D5-33

### H-D5-33 The ASAL open-endedness score cannot tell life from garbage
- source: techne/acquisition/poet_alife/TECHNE107_RESULTS_2026-09-17.md:61 @ 44d109558 (2026-09-17), seat Techne; quote: "5. A moving blob and the Orbium are within 0.026 (P6): the score does not know life from"
- kind: prior-art-held
- question: Any foundation-model novelty/open-endedness score used in an artificial-physics or cross-world engine needs garbage and translation controls. The substrate-side control is recorded as still open (:67).
- why it might matter now: Aether (artificial physics) and Cosmos may adopt ASAL-like scores.
- later evidence: none found.
- lenses: Aether, Cosmos
- related: H-D5-31, H-D5-43

### H-D5-34 Monoculture under pressure; does stored experience raise the ceiling or only speed convergence?
- source: roles/ScienceAdvisor/RESPONSIBILITIES.md:151,159 @ 33405415c (2026-04-01), seat ScienceAdvisor; quote: "**Open question:** Does corpus-first initialization give evolution access to a **higher ceiling** or just **faster convergence** to the same ceiling?" ... "**The monoculture pattern:** Wherever optimization pressure rewards what already works, convergence to a single mode follows."
- kind: open-question
- question: Does seeding with stored representations raise the reachable ceiling or only accelerate convergence to the same one?
- why it might matter now: Same speed-vs-capability fork appears in Ares cycle 2 and Crius; Ensorain's memory claims need it too.
- later evidence: roles/Ares/STATUS.md:18 (recurrence wins on speed, not capability) is one datum for "faster, same ceiling" in a different carrier.
- lenses: Ares, Ensorain, Crius
- related: H-D5-13, H-D5-28

### H-D5-35 Convergent evolution across independent lineages: a success criterion never reached
- source: roles/EvolutionaryArchitectAndReasoningSpeciesEngineer/Apollo_Role_Document.md:232 @ b56c7401a (2026-04-04), seat EvolutionaryArchitectAndReasoningSpeciesEngineer; quote: "| Gen 50000 | Evidence of convergent evolution (independent lineages -> similar strategies) |"
- kind: open-question
- question: Do separately seeded lineages independently arrive at the same mechanism? If so, that mechanism is a candidate invariant of the world, not of the lineage.
- why it might matter now: Links Cosmos (cross-world invariants) with Archaeon (lineage); a mechanism-level analogue of cross-world invariance.
- later evidence: none found.
- lenses: Cosmos, Archaeon, Aether
- related: H-D5-36, H-D5-58

### H-D5-36 Learned coordinates do not transfer across topologies; cross-substrate convergence as fitness
- source: ignis/NORTH_STAR.md:33 @ 9e189d683 (2026-04-01), seat Ignis; quote: "- **Cross-architecture transfer: DEAD.** Pythia genomes on Llama = +1 net. Llama genomes on Pythia = +2 net." Also arcanum/docs/FUTURE_FEATURES.md:9 @ ffb3639d4 (2026-03-22): "-   **Cross-Substrate Convergence as a Fitness Signal:**"
- kind: prior-art-held
- question: Transfer of learned coordinates failed across different model topologies. Is convergence of a structure across several substrates a better fitness signal than transfer? Lexis's diagnosis applies: transfer needs shared interface semantics (roles/Lexis/PLAN_2026-08-25.md:46).
- why it might matter now: Cosmos (invariants across worlds), Aether (multiple physics), Crius (cross-world reuse).
- later evidence: none found that uses cross-substrate convergence as fitness.
- lenses: Cosmos, Aether, Crius
- related: H-D5-35, H-D5-58

### H-D5-37 The frozen selector, not the generator, may be the ceiling
- source: aporia/docs/deep_research_batch_2026-08-17/14_do_generator_upgrades_convert_to_verified_artifact_yield_answer.md:189 @ ef567d9f1 (2026-08-17), seat Aporia (external DR); quote: "Your history of zero measured lift from 2,152 mutations is not proof that generator upgrades are futile; rather, it is proof that your specific *frozen selector* lacks the epistemological rigor to demand deeper reasoning."
- kind: directive-idea
- question: Should the selector/verifier co-evolve with the improvers (the TANGO pattern, :145), and how is that kept from collusion?
- why it might matter now: Aphrodite's improver-of-improvers runs against fixed selectors; Ares pressures are fixed.
- later evidence: none found.
- lenses: Aphrodite, Ares
- related: H-D5-38, H-D5-39, H-D5-28

### H-D5-38 The graded party must not set the grader
- source: aporia/docs/PROGRAM_SUMMARY_2026-08-24.md:135 @ 66e06e027 (2026-08-24), seat Aporia; quote: "4. **Build Hephaestus an oracle it does not set the terms of.** The distractor policy cannot be"
- kind: defect-ambiguity
- question: An improver-of-improvers needs an evaluator it cannot author. Who owns the graders for Aphrodite and Ares, and what stops the improver from changing the distractor policy?
- why it might matter now: The tension with H-D5-37 (co-evolving selectors) is the design problem for Aphrodite.
- later evidence: Aphrodite FAIR_META_SELECTION (S2) PASS (roles/Aphrodite/STATUS.md) addresses meta-selection fairness, not grader ownership.
- lenses: Aphrodite, Ares
- related: H-D5-37, H-D5-39

### H-D5-39 A separable evaluation episode is a target; evaluator detection rate never measured
- source: aporia/docs/deep_research_batch_2026-08-27/report_SELECTION_DISCOVERED_CONCEALMENT.md:64-65,185 @ 5b658ac69 (2026-08-29), seat Aporia (external DR); quote: "**The design principle, stated as sharply as the evidence allows: if a distinguishable" / "evaluation episode exists at all, it is a target." ... "- How fast does **evaluator detection specifically** arise, as opposed to environment"
- kind: parked-experiment
- question: Should pressure come from in-population, lineage-relative replication (Avida's STERILIZE_BENEFICIAL) rather than separable test episodes? How fast does evaluator detection evolve? Proposed probe (:140): freeze the genome and perturb parts of the environment the lineage could not observe.
- why it might matter now: Every engine that evolves under a test harness (Ares, Aphrodite, NPE, Aether) is exposed.
- later evidence: STERILIZE_BENEFICIAL appears only in this report (grep).
- lenses: Ares, Aphrodite, NPE Z80 worlds, Aether
- related: H-D5-37, H-D5-38

### H-D5-40 Selection cannot value constructive actions that only enable later experiments
- source: aporia/docs/deep_research_batch_2026-08-17/16_expected_information_gain_experiment_selection_in_practice_answer.md:136 @ ef567d9f1 (2026-08-17), seat Aporia (external DR); quote: "Because algorithms cannot intrinsically value "constructive" actions (building tools, assays) [cite: 21], the calibration of human filers is the only way to navigate capability gating."
- kind: open-question
- question: Can selection reward tool-building steps with zero immediate gain but later unlock discrimination (a horizon/myopia problem)? Also: pressure-directed samplers can underperform uniform ones (aporia/docs/deep_research_reports/2026-05-22/00343_tsc_05_active_sampling_vs_uniform_enumeration_for_falsificat.md:43 @ b46284108), and a ~20% random-sample floor turns the selection bias into a measurable quantity (harmonia/memory/provocations.md:75 @ 02815264d: "A random-sample floor converts the bias from a **blind spot** into a **measurable**").
- why it might matter now: Crius (accessibility of tools that pay later), NPE/BEE samplers; every directed sampler should keep a uniform arm.
- later evidence: none found.
- lenses: Crius, NPE Z80 worlds, BEE z80atlas, Ares
- related: H-D5-31, H-D5-32

### H-D5-41 Recursive self-improvement rarely compounds; the headline citation was misattributed
- source: aporia/docs/deep_research_batch_2026-09-17/01_recursive_self_improvement_2024_2026_which_reported_successe.md:47 @ e0e78040f (2026-09-17), seat Aporia (external DR); quote: "There is currently no public record of a Tier W (weight-level) RSI system that successfully compounds across more than three iterations without human intervention or dataset relabeling."
- kind: prior-art-held
- question: Does an improver-of-improvers compound past the third round against an equal-compute baseline? The AlphaEvolve plateau figure comes from a third-party paper, not DeepMind (aporia/docs/deep_research_batch_2026-09-17/VERIFICATION_2026-09-17.md:12 @ 9095a24db: "**Attribution and status claims: 5 errors, one of which carries the report's main verdict.**").
- why it might matter now: Aphrodite's BOUNDED_RSI is "NOT YET ESTABLISHED"; this sets the bar and flags a citation not to reuse.
- later evidence: verification later revised to 4 errors (sub-scan); roles/Aphrodite/STATUS.md:16 BOUNDED_RECURSIVE_SELF_IMPROVEMENT NO.
- lenses: Aphrodite
- related: H-D5-04, H-D5-37

## D. Falsification instruments

### H-D5-42 The eight-class counterfeit battery as machine-enforced gates
- source: aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md:37,55 @ 1902bbc79 (2026-08-25), seat Aporia; quote: "retrieval counterfeit     capability already exists somewhere accessible" ... "Machine-enforced gates, not a checklist. A claim whose class has an unrun mandatory falsifier is"
- kind: unfollowed-recommendation
- question: Should every engine's capability claim clear the retrieval, parse, answer, search, budget, distribution, composition and evaluation counterfeit checks, enforced by machine, before it counts?
- why it might matter now: Held doctrine that current engines rediscover piecemeal (Ensorain null ladder, Aphrodite S1-S4 conditions, Crius gate v2).
- later evidence: none found as a shared cross-engine gate.
- lenses: all engines; Ensorain, Aphrodite, Crius
- related: H-D5-19, H-D5-20, H-D5-43

### H-D5-43 Every gate ships a positive control; a detector that never fired is not a detector
- source: harmonia/probe/THREE_EXPERIMENTS_HARMONIA_B_2026-08-25.md:189 @ 171ab7957 (2026-08-25), seat Harmonia; quote: "The cheapest repair in this whole document: **every gate ships a positive control**." Also roles/Nemesis/CALIBRATION.md:20 @ a95d67ed8 (2026-09-11): "A detector that has never fired is not a detector; its silence was read as a finding about the world"
- kind: unfollowed-recommendation
- question: How many current gates and nulls have a demonstrated firing case (a planted positive)? The older audit found that more than half of the gates had never been shown to fire.
- why it might matter now: Ensorain's null ladder, Cosmos's certificate, Ananke's XOR/FLIP NULL verdicts all rely on silence meaning absence.
- later evidence: none found as a fleet-wide rule.
- lenses: Ensorain, Cosmos, Ananke, all gates
- related: H-D5-42, H-D5-46, H-D5-58

### H-D5-44 Magnitude and generator tautologies: the outcome is predictable from who made the row
- source: aporia/docs/CYCLE_150N_MAGNITUDE_TAUTOLOGY_2026-08-24.md:14,90 @ c9af3911b (2026-08-24), seat Aporia; quote: "Knowing only which generator produced a row predicts its outcome at ~98%. That is the tautology the" ... "**Does not close:** the navigation hypothesis itself, which has still never been tested on an". Also harmonia/proposals/2026-06-09/B_RESULTS_2026-06-10.md:127 @ 55026bdfc: "tautology generator -- predicted==actual derive from the same flip table (1340/1340; REJECTED unreachable); needs a **T0_TAUTOLOGY** class before any miner touches it"
- kind: anomaly
- question: Before an outcome variable is used for selection or as evidence, check that generator identity, number scale, or a shared source does not already predict it.
- why it might matter now: SFE, Cosmos and Aether produce outcomes from generators they also score. Ares's pressure generators need the same check.
- later evidence: T0_TAUTOLOGY class added in the harmonia line (B_RESULTS :91); no cross-engine check found.
- lenses: SFE, Cosmos, Aether, Ares
- related: H-D5-45, H-D5-47

### H-D5-45 A published chance floor that was a ceiling
- source: harmonia/memory/retraction_registry.md:157,161 @ cc727f2f4 (file 2026-04-29; entry 1be87a0fe, 2026-08-31), seat Harmonia; quote: "**non-vacuity is not navigability**); `D` is **maximised by a fair coin** at every state (the least navigable world scores highest)" ... "**I published a chance floor that was a ceiling.**"
- kind: anomaly
- question: Before publishing a world metric, ask which world maximizes it, check Jensen's direction and label-swap symmetry. Open at :159: selecting which parents get a second logged action may inflate D.
- why it might matter now: NPE Z80 worlds and Aether define world-level metrics; Ares measures navigability.
- later evidence: retracted in place; no general metric audit found.
- lenses: NPE Z80 worlds, Aether, Ares
- related: H-D5-44, H-D5-46

### H-D5-46 Shuffled nulls cannot separate an exploit from a real capture; use dose-response at known break rates
- source: zoo/conjecture_gp/tink_3_design_questions.md:225 @ 2b63fc95d (2026-05-05), seat Zoo; quote: "The shuffled-null check (S0.3) does not separate exploits from"
- kind: directive-idea
- question: Replace pass/fail shuffle nulls with adversarial datasets where the anchor relation is broken at known rates, and require a dose-response.
- why it might matter now: Ensorain's null ladder and Cosmos's permutation null are pass/fail; a graded break rate would also give each gate a positive control.
- later evidence: none found.
- lenses: Ensorain, Cosmos, Ares
- related: H-D5-43, H-D5-47

### H-D5-47 Cross-context signals must be re-tested within each context; nulls must preserve the constraints
- source: cartography/docs/aletheia_session_20260412_13.md:130 @ d20aac287 (2026-04-13), seat Charon/Cartography; quote: "The lesson: any signal that exists across conductors must be tested within conductors. No exceptions." Also cartography/convergence/docs/metabolism_draft_deepseek_review.md:20 @ 109a93f20 (2026-04-07): "A proper null must preserve the row/column dependencies (e.g., via random bipartite graphs with fixed degree sequences or via random flux-balanced networks)."
- kind: prior-art-held
- question: Does each Cosmos cross-world invariant survive recomputation inside a single world or within matched world-parameter strata, and do Cosmos's nulls preserve conservation laws and degree sequences rather than just size and sparsity? The catalogue at :128 lists 7 failure modes usable as standard kill checks.
- why it might matter now: Cosmos's law SURVIVED three sealed universes; within-world and constraint-preserving nulls are the next obvious attacks.
- later evidence: none found in Cosmos docs (not grepped exhaustively).
- lenses: Cosmos, Aether
- related: H-D5-44, H-D5-58

### H-D5-48 "Invalid" where it should be "unknown": syntactic dispatch hides working reasoning
- source: aporia/docs/deep_research_batch_2026-08-17/13_syntactic_dispatch_as_a_hidden_failure_mode_in_verification__answer.md:166 @ ef567d9f1 (2026-08-17), seat Aporia (external DR); quote: "the system conflates an inability to parse with an assurance of falsehood."
- kind: defect-ambiguity
- question: Do falsification instruments return a three-way verdict (true / false / unknown) when they meet an unregistered shape?
- why it might matter now: Kills that are really parse failures corrupt the failure record that heredity depends on. Cosmos, Ananke, SFE.
- later evidence: tri-state appears in prometheus/ananke/report.py only (sub-scan grep).
- lenses: Ananke, Cosmos, SFE, all gates
- related: H-D5-49, H-D5-51

### H-D5-49 State injection: separate "cannot perceive" from "cannot compute" (never run)
- source: apollo/pivot/APOLLO_REVIVAL_REVIEW_2026-09-01.md:156 @ 96ee6fac8 (2026-09-01), seat Apollo; quote: "the single cheapest discriminating experiment on the board and it has". Also aporia/docs/CYCLE_155S_FOUR_ARE_NOT_FOUR_2026-08-24.md:86 @ e8aa82595: "that already worked. That would be a real capability delta and a false organism demonstration."
- kind: unfollowed-recommendation
- question: Pre-fill the representation by hand and see whether the reasoning layer then succeeds. This splits a representation ceiling from a mechanism ceiling, and exposes parser fixes passed off as new reasoning.
- why it might matter now: With representation and mechanism co-evolving, every engine needs this upper-bound decomposition. Ensorain, Aphrodite, Ares.
- later evidence: none found (no committed state-injection run).
- lenses: Ensorain, Aphrodite, Ares
- related: H-D5-13, H-D5-48

### H-D5-50 Blind batteries and co-adapted generators: scores that measure who wrote the tests
- source: apollo/pivot/APOLLO_REVIVAL_REVIEW_2026-09-01.md:95,164 @ 96ee6fac8 (2026-09-01), seat Apollo; quote: ""preconditions keyed on SEMANTIC SLOTS, never problem_text surface, that" ... "the generator is co-adapted and Apollo knows it before trusting it."
- kind: prior-art-held
- question: Do current capability numbers survive tasks written blind by another author (Apollo scored 0.0667 blind vs 0.60 on its own battery)? Should world/task generators be validated by reproducing a known blind result before being trusted?
- why it might matter now: NPE and Aether generate their own worlds; Cosmos's sealed universes are the right idea and are now spent.
- later evidence: E9 scorer rebuilt and reproduces 0.0667 (sub-scan). Cosmos has no sealed universes left (roles/Cosmos/STATUS.md).
- lenses: NPE Z80 worlds, Aether, Cosmos, BEE z80atlas
- related: H-D5-44, H-D5-52

### H-D5-51 How many "inherent limits" are unrecognised bugs?
- source: techne/loop/HITL_LOG.md:1590-1591 @ 31f1fe380 (2026-08-21), seat Techne; quote: "**Open question I cannot answer alone: how many other "inherent limits" in this arsenal are" / "unrecognised bugs?**"
- kind: open-question
- question: Before accepting a wall or null as a finding, audit the harness (guard, slot, interface). Related: a headline gain that cannot be reproduced from the repository (ergon/gen1/FINDING_d5_reproducibility_2026-09-01.md:115 @ 1acd0f4b7: "So the +10.95pp / p = 0.0007 **cannot be reproduced from the repository**.").
- why it might matter now: Failure is evidence only if the failure is the world's, not the instrument's. All engines; Archaeon's "caught_by" lineage.
- later evidence: Ares cycle 2 found two defects in its own apparatus that flipped gate C (roles/Ares/STATUS.md), the same class.
- lenses: all engines, Archaeon
- related: H-D5-48, H-D5-53

### H-D5-52 Is a ranking signal a predictor of progress, or a sensor for the oracle?
- source: roles/Diomedes/HANDOFF_lean_successor_2026-08-26.md:17-18 @ cedaad445 (2026-08-26), seat Diomedes; quote: "> **Does `Z(x,a)` predict future attainable verified progress -- or is it a sensor for the variables" / "> that define the current oracle?**"
- kind: open-question
- question: Do engine fitness signals predict future reachability, or just reconstruct the grader? Rule from the same doc (:35): the oracle is computed from the future; every ranking arm from the present. Arm B was never run (roles/Diomedes/CYCLE_005_ARMA_RESULT.md:106: "Disposition PARK. Q1 unresolved; Arm B still to run.").
- why it might matter now: NPE/BEE navigation signals, Aphrodite's meta-selection, SFE ranking.
- later evidence: none found.
- lenses: NPE Z80 worlds, BEE z80atlas, Aphrodite, SFE
- related: H-D5-37, H-D5-50

## E. Lineage, provenance, corpus hygiene

### H-D5-53 Defect lineage needs a typed record made at catch time, not commit prose
- source: harmonia/probe/THREE_EXPERIMENTS_HARMONIA_B_2026-08-25.md:167 @ 171ab7957 (2026-08-25), seat Harmonia; quote: "changed with the program's mood. Q4 needs a **prospective typed defect record emitted at catch"
- kind: unfollowed-recommendation
- question: Should Archaeon's causal lineage lens ingest typed records {class, introduced_at, caught_at, caught_by, guard_shipped} rather than infer from commit prose (whose length swung 35x across the June/July/August boundary, :194)?
- why it might matter now: Archaeon reads history; this says retrospective prose metrics are broken for the fleet.
- later evidence: none found.
- lenses: Archaeon
- related: H-D5-51, H-D5-54, H-D5-55

### H-D5-54 Data-assembly provenance: selection floors can create "laws"
- source: harmonia/proposals/2026-06-09/B_RESULTS_2026-06-10.md:104 @ 55026bdfc (2026-06-10), seat Harmonia; quote: "Catalog **assembly** provenance (quota stratification) remains unexamined by anyone."
- kind: unfollowed-recommendation
- question: Should Archaeon trace how a dataset or world sample was assembled, not only causal lineage? Example (:114): a relation held on all 1000 catalogued cases because the known counterexample sat below the catalog's floor.
- why it might matter now: Cosmos's worlds and Ensorain's corpora are assembled by rules that can manufacture invariants.
- later evidence: none found.
- lenses: Archaeon, Cosmos, Ensorain
- related: H-D5-53, H-D5-47

### H-D5-55 Incidents as splittable hypotheses; adversarial lineage data never used
- source: roles/Hermes/CONVERGENCE_PROBE_2026-09-11.md:174 @ 84cc58224 (2026-09-11), seat Hermes; quote: "SPLITTABILITY  CTL-2 proves a symptom key can gather two causes, so an". Also roles/Nemesis/ARCHAEOLOGY_2026-09-11.md:145 @ a95d67ed8: "52 of 92 records carry lineage_depth > 0 and no use was ever made of them."
- kind: prior-art-held
- question: Should causal-lineage clustering treat each incident as a hypothesis that observations share a cause, with split() so one failure cannot hide another? Once a live population exists, does adversarial ancestry predict which descendants break?
- why it might matter now: Archaeon's lens and Ares's pressure lineages.
- later evidence: none found.
- lenses: Archaeon, Ares
- related: H-D5-53, H-D5-56

### H-D5-56 Residual bridges: cluster falsification leftovers by failure signature
- source: harmonia/memory/architecture/residual_primitive_spec.md:185 @ eea66f664 (2026-05-02), seat Harmonia; quote: "it becomes a **residual bridge** -- a higher-order substrate symbol that maps regions of the cartography where the universe's noise is suspiciously structured."
- kind: directive-idea
- question: Cluster residuals from all engines by failure signature. Do shared signatures point to shared mechanisms? The spec has only a hypothetical worked example. The same idea recurs as the failure-dossier "science of failure": aporia/docs/science_of_failure_v0.1.md:36 @ 7e718388a (2026-06-04): "we do not yet know whether the field points to undiscovered structure or merely" (compresses the biases of our generators), with the null ladder at aporia/docs/failure_signal_protocol_v0.1.md:223 ("Null-2: operator-/family-shuffled near-math").
- why it might matter now: A cross-engine instance of "failure is evidence"; needs a family-shuffled null before it counts. Archaeon, Cosmos, Ensorain.
- later evidence: none found (never built).
- lenses: Archaeon, Cosmos, Ensorain
- related: H-D5-10, H-D5-55, H-D5-58

### H-D5-57 Score-once, skip-forever: new pressures never revisit old artifacts
- source: roles/Skopos/ARCHAEOLOGY_2026-09-11.md:194-196 @ b3e27f7f4 (2026-09-11), seat Skopos; quote: "skipped for ALL threads, for ever -- including threads that did not exist"
- kind: defect-ambiguity
- question: When a new selection pressure or question appears, are archived artifacts re-assessed against it, or does first contact decide their fate forever? A 2026-08 external review of retrodictive re-analysis sets the protocol: aporia/docs/deep_research_batch_2026-08-17/20_retrodictive_re_analysis_precedent_and_pitfalls_answer.md:119 @ ef567d9f1 ("*   Immediately freeze access to the 92,000 dataset."), i.e. a calibration slice, a blinded hold-out, and synthetic signal injection.
- why it might matter now: Crius's reuse accessibility depends on old artifacts being reachable under new pressures; Archaeon re-reads old kills and needs the blinded protocol.
- later evidence: none found.
- lenses: Crius, Archaeon
- related: H-D5-22, H-D5-58

### H-D5-58 The cross-domain null: compartmentalized worlds, or a representation that cannot see the link? Plus off-target DR reports to quarantine
- source: cartography/docs/meta_analysis_20260412.md:208 @ d1e3ab92e (2026-04-12), seat Charon/Cartography; quote: "The absence of cross-domain structure under these representations and this battery is itself the finding. Whether it reflects a deep truth about mathematical compartmentalization or a limitation of feature-based analysis remains an open question". Also cartography/docs/what_we_learned_v2.md:89 @ 830a83a3f (2026-06-09): "4. **Layer 3 (transformation detection)** -- still unexplored." And the external blinded-recovery design, aporia/docs/EXTERNAL_REVIEW_2026-08-22_loop_design.md:131 @ 05cb2d703: "> **If the signature system cannot recover deliberately hidden relationships that are already"
- kind: open-question
- question: When Cosmos finds no cross-world invariant, can it distinguish "the worlds are separate" from "the representation cannot see the link"? Plant a shared invariant (a positive control) and require blinded recovery; and search for maps between worlds (Layer 3), not only shared statistics.
- why it might matter now: Cosmos is the direct heir of this line; Aether's multiple physics are candidate worlds. Hygiene note for the same corpus: the Moros cross-pollination DR series is off-target (the agent saw only filenames), e.g. aporia/docs/deep_research_reports/2026-05-29/00419_moros_cross_pollination_pivot_kill_topography_findings_2026_.md:26 @ 733591a17: "The artifact `pivot\kill_topography_findings_2026-05-29.md` resides at the intersection of landscape archaeology, geomorphology, and taphonomic analysis." Any PATTERN_* drawn from that series should be quarantined.
- later evidence: Cosmos C3 law SURVIVED sealed universes (roles/Cosmos/STATUS.md) -- the first positive in the lineage; the planted-invariant positive control and Layer 3 were not found.
- lenses: Cosmos, Aether, Archaeon
- related: H-D5-35, H-D5-36, H-D5-43, H-D5-47

## Cross-domain pointers

- D-Archaeon/lineage harvest: H-D5-53..57 are lineage-instrument requirements (typed catch-time records, assembly provenance, splittability, blinded retrodiction). Cross-check against Archaeon expansion docs (archaeon/docs/expansion/ cites Toussaint/Kouvaris; crius/ does not -- see ergon/kouvaris2017/J_DETECTOR_GENEALOGY.md:128 @ 83e2c88c8: "buildable-but-unreported (as `computeM.m` showed); it was **built, published, run in all arms, and"). This is a prior-art gap for Crius: a local accessibility detector from the Toussaint line predates "reuse accessibility"; what is new is only the mechanism plus within-run measurement.
- D-Crius/Aphrodite harvest: H-D5-13, 15-22, 28, 37-41 bear on reuse and the improver-of-improvers; check whether Aphrodite S3/S4 already answer H-D5-02/13/19 in part.
- D-Ensorain harvest: H-D5-23..27, 43, 46 supply null-ladder rungs (random projection, known-rank TT controls, dose-response nulls, background detrending, label-free MDL scoring).
- D-Cosmos/Aether harvest: H-D5-33, 35, 36, 44, 47, 50, 58.
- D-NPE/BEE harvest: H-D5-29-32, 40, 45, 52; also ARC-AGI-3 prior art (aporia/docs/deep_research_reports/2026-05-19/00059_lad_02_arc_agi_2025_saturation.md:184 @ 0ec7d80ec) on scoring interactive worlds by relative action efficiency rather than static success, and the Avida version-uncertainty caveat (ergon/avida2003/ERGON_AVIDA2003_HISTORICAL_DEEP_DIVE_V0/V_FREEZE_RECORD.md:29 @ 2130c6a31: "We do not know, and no claim may rest on").
- Unfiled external research: aporia/docs/gemini_d4_substrate_dispatch_2026-08-27.md @ 852a3215e holds 20 written prompts (D4-01..20) on substrate physics, including :110 "USAGE FREQUENCY is a tautological measure of operator importance", :149 Avida/Tierra primary sources, :212 cellular-automata rule spaces, :354 library learning, :369 open-endedness and the metric becoming the target. No report_D4_* file exists and engine/queues/CONSUMPTION.jsonl has no D4 rows. Also about 360 of 423 queued Gemini DR items were never fired (gemini_research_queue). Candidate for a prior_art/ pass.
- Held-but-unused instruments from older seats: metamorphic relations (roles/Nemesis/ARCHAEOLOGY_2026-09-11.md:143, NEEDS_REPREMISE), a battery that grows with each kill (roles/CrossDomainCartographer/CrossDomainCartographer_Charon_Role.md:271), and an unverified 10-operator transformation basis (roles/StructuralMathematician/RESPONSIBILITIES.md:50). These belong with the falsification-instrument domain.
- Minor, not carded: multi-agent role proliferation / bounded structural mutation (DR 2026-08-17 #15 :82); coequalizers as formal representation-change checks (DR #03 :6); semantic-retrieval NULL as design limit (DR #12 :152); per-step kill-mode vectors claimed novel as of 2026-05 (deep_research_reports/2026-05-21/00274_erg_01_...:78); downward reuse of failed higher-tier artifacts (roles/PipelineOrchestrator/DESIGN_tiered_forge.md:249); Talos transfer-ablation T08 parked "nobody holds it" (roles/Talos/ARCHAEOLOGY_2026-09-11.md:95).
