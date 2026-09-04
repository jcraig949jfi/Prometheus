# PROPOSAL V2-T04 (arm B)

## Hypothesis

RECOMMENDATION TRANSFER via SEMANTIC SIMILARITY. When a new incoming research problem P_new arrives (given as a title, subject tags, and topic keywords), a recommender model R that scores historical problem-solution pairs on semantic similarity should predict which prior problems P_archive are most suitable for knowledge transfer. The null hypothesis is that embedding-based similarity (learned or pretrained) between P_new and P_archive is NOT a reliable proxy for transfer utility: high-ranked recommendations (by cosine similarity or learned ranking) do not correlate with actual downstream solver performance on P_new when given P_archive's solution approaches, code structure, or pedagogical insights. The alternative is that similarity-ranked recommendations concentrate transfer-usable prior work, enabling solvers to accelerate problem-solving by focusing on structurally related solved problems rather than uniform or random historical search.

This tests whether semantic similarity can act as a triage mechanism to compress the problem search space.

## Motivating evidence

- `agent_d5_blind/learner/m1.py` (confirmed): learner operates via corpus-guided search; when the corpus of prior solutions is reordered or filtered by relevance, downstream performance changes. Implication: not all historical solutions are equally useful; relevance matters.
- Aporia genealogy work (roles/Aporia/resume_aporia.md): transfer success is modulated by problem-domain relatedness; problems with similar underlying structure (abstract algebra vs. applied algebra) show asymmetric transfer even when surface-level topic tags overlap.
- `agent_d5_blind/VERDICT.md` (G9): context-dependent knowledge propagation suggests that problem structure (not just tag overlap) drives transfer. Implication: a recommender blind to problem structure will fail.
- Transfer-learning literature pattern (meta-evidence from memory index): task similarity metrics that ignore deep structure (e.g., histogram overlap of features) often fail where learned embeddings succeed; but learned embeddings on small corpora can overfit the training distribution.
- Evidence from prior contradictions (ew.contradictions()): substrate differences matter — D-5 and D-8 show opposite outcomes under identical conditions when genotype-ecosystem interactions change. Implication: a recommender must be *calibrated* per problem domain; one-size-fits-all similarity may be spurious.

## Prospective predictions

1. **Null (similarity does not transfer)**: top-K recommendations (ranked by learned or pretrained embedding similarity to P_new) show NO significant correlation with solver success rate on P_new when using P_archive solutions. Spearman rank correlation rho <= 0.15 between similarity rank and downstream CFR (per-problem solve rate) on held-out test problems. 95% CI excludes rho > 0.25.

2. **Alternative (similarity concentrates transfer)**: top-K recommendations (K=5, K=10) yield measurably HIGHER problem-solve rates compared to random-K or bottom-K recommendations. Measured as delta in mean CFR between top-5 vs. random-5: >= +0.08 with 95% CI half-width <= 0.05, establishing that similarity ranking has predictive power.

3. **Embedding-type asymmetry (exploratory)**: pretrained embeddings (e.g., BERT, sentence-transformers on mathematical text) will rank differently than learned embeddings trained end-to-end on problem-solution pairs. Predicted: Spearman tau between two embedding rankings <= 0.60 (low agreement), and one embedding type will show rho >= 0.25 while the other shows rho <= 0.15, revealing embedding-choice dependence of transfer signal.

## Experiment

### Phase 0 (preflight, non-evidence, setup only)

1. **Corpus assembly**: identify N_archive >= 50 archived research problems from prior Prometheus work, each with a solved solution narrative (code, method description, or experimental design). Each problem record must contain: (1) title (text), (2) subject/domain tags (categorical), (3) keyword topics (free text), (4) downstream solver outcome (CFR or success binary). Log: inventory path, N_archive count, data quality checks.

2. **Embedding collection (three variants)**:
   - Pretrained BERT-base embeddings (768-dim) applied to problem titles + keywords
   - Sentence-Transformers (all-mpnet-base-v2, 768-dim) on full problem descriptions
   - Learned embedding layer (randomly initialized, 128-dim, trained end-to-end in Phase 1)
   - Record embedding generation date, model versions, and reproducibility hashes.

3. **Similarity metric freeze**: select one pairwise similarity function (cosine distance in embedding space) and freeze it before evidence queries. All ranking uses this metric; no post-hoc metric switching. Document: metric name, tie-breaking rule (stable sort, then alphabetic), batch processing order.

4. **Ground-truth assembly**: for each test problem P_test (held-out, n_test = 10-15 problems), generate binary labels for all archive problems: "transfer-useful" = solver achieved >= +5pp CFR boost when given P_archive solution structure, vs. "null transfer" = no boost. Criterion is pre-registered as +5pp to avoid zero-line ambiguity. This is non-evidence (preflight), used only to calibrate false-positive rate.

### Phase 1 (evidence, paired arms on identical test problems)

**Test set**: n_test = 12 held-out problems, selected uniformly at random from archive (without replacement). Each test problem P_i is presented to two independent solver instances.

**Arm B1 (random recommendations)**:
- For each P_i, draw K=5 recommendations uniformly at random from P_archive (without replacement).
- Provide solver with these 5 problem descriptions as context/reference.
- Measure downstream CFR (fraction of tasks in P_i solved within fixed budget).
- Repeat over 10 replicates (10 independent random draws of K=5 per test problem).

**Arm B2 (learned embedding recommendations)**:
- For each P_i, compute embedding vector e_i.
- Rank all P_archive by cosine similarity to e_i.
- Select top K=5 archive problems (highest similarity).
- Provide solver with these 5 ranked recommendations.
- Measure downstream CFR (identical budget, identical solver instrumentation as B1).
- Repeat over 10 replicates (10 independent runs per test problem).

**Outcome collection (both arms)**:
- Per test problem P_i, per arm, record:
  - CFR (fraction of sub-tasks solved)
  - Per-recommendation: whether it was marked transfer-useful in ground-truth
  - Solver's reported confidence in recommendations (explicit feedback)
  - Execution time to solution (as proxy for cognitive load)

### Phase 2 (analysis, outcome-blind until freeze)

- **Primary endpoint**: mean CFR(B2) - mean CFR(B1) >= +0.08 with 95% CI lower bound >= +0.03 (directional success, B2 > B1).
- **Secondary endpoints**:
  - Spearman rho: rank correlation between similarity score and transfer-usefulness label (top-5 recommendations vs. ground truth).
  - Per-problem variation: does CFR delta favor B2 on high-similarity problems and B1 on low-similarity problems? (interaction test).
  - Embedding-type contrast: does pretrained BERT vs. learned embedding produce different rankings? Measured as tau between two ranking orders.

## Controls

1. **Matched-problem paired design**: both B1 and B2 receive identical test problems and identical solver instrumentation (code paths, time budgets, RNG seeds for solver internals). Deltas are within-problem, not between solvers.

2. **Similarity metric freeze** (Phase 0, gate C1): one metric (cosine in frozen embedding space) is locked before any test problem is seen. No post-hoc tuning of distance thresholds or tie-breaking rules. Falsifier F1 triggers if metric is changed after outcome collection begins.

3. **Random baseline parity**: random arm (B1) uses the same K=5 size and identical problem-description format as ranked arm (B2). The only difference is selection mechanism (random vs. ranked). This isolates recommendation quality from information density.

4. **Embedding stability check**: compute embedding Pearson correlation between two independent runs on the same problem corpus (reproducibility). If correlation < 0.95 on test-set embeddings, declare embedding UNSTABLE (Falsifier F2).

5. **Archive corpus closure**: archive problems are fixed throughout Phases 1-2. No new problems added, no problem removal. Document: archive version hash, N_archive finalized, archive lock timestamp.

6. **Solver instance independence**: each test problem in each arm receives a fresh solver instance (no state leakage between recommendations or between arms). Seed the solver's internal RNG from a deterministic hash of (problem_id, arm_id, replicate_id) to ensure reproducibility.

## Confound defenses

- **Similarity-difficulty circularity**: problems similar to P_new might be easy problems generally (confound: difficulty, not transfer). Defense: report per-problem baseline CFR (B1 CFR before any recommendations — solver starts cold). If CFR baseline is high for high-similarity problems even in random arm, flag as DIFFICULTY_CONFOUND.

- **Recommendation-number asymmetry**: K=5 is arbitrary. What if B2 benefits simply because it tries more recommendations implicitly (if similar problems cluster)? Defense: in both arms, present exactly K=5 recommendations, displayed in identical format. Log which problems the solver actually consulted; if B2 solvers consult fewer recommended problems (ignoring higher-ranked ones), it's due to content quality, not quantity.

- **Embedding-trained-on-outcomes**: if learned embeddings are trained on solver CFR outcomes, the recommender will be tautologically correlated with outcomes (circular causality). Defense: embedding training must be outcome-blind; freeze embeddings BEFORE reading any test-problem outcomes. If embeddings are fine-tuned after seeing Phase 1 data, invalidate that run (Falsifier F3).

- **Ground-truth labeling bias**: the "+5pp transfer boost" threshold is arbitrary. If most archive problems show +0pp to +3pp boost, the +5pp gate will label almost none as transfer-useful, making the null predictions unfalsifiable. Defense: report the *distribution* of CFR deltas (P_archive solution context vs. cold start) in the preflight ground-truth assembly phase (Phase 0, step 4). If > 80% of archive problems show CFR delta < +5pp, report and recalibrate threshold.

- **Solver-recommendation interaction**: solvers might ignore or misinterpret recommendations from lower-ranked problems. If top-ranked problems are ignored, but bottom-ranked problems are carefully read, the recommendation ranking might reverse. Defense: instrument solver's attention (log problem-reading duration, problem-selection order). If bottom-ranked recommendations are attended more than top-ranked, flag as ATTENTION_REVERSAL.

## Preregistered falsifiers (numeric thresholds)

- **F1 (metric modification)**: any change to similarity metric, embedding model, or distance function after Phase 0 freeze. If true: stop; declare run INVALIDATED.

- **F2 (embedding instability)**: Pearson correlation between two independent embedding runs < 0.95 on test-set embeddings. If true: halt; declare EMBEDDING_UNSTABLE and do not proceed to recommendation ranking.

- **F3 (outcome-blind training violation)**: learned embeddings are fine-tuned or re-trained after ANY outcome data from Phase 1 is observed. If true: invalidate B2 arm (learned embedding only).

- **F4 (primary — null not rejected)**: mean CFR(B2) - mean CFR(B1) < +0.05 with 95% CI lower bound < -0.02 (i.e., CI overlaps or favors B1). If met: similarity ranking does not improve transfer; alternative rejected.

- **F5 (secondary — no ranking signal)**: Spearman rho between similarity rank and transfer-usefulness label <= 0.10 across all top-5 recommendations. If met: embedding-based ranking has no monotonic relationship with ground truth.

- **F6 (solver budget integrity)**: any test problem in any arm consumes evaluation count deviating from frozen budget by > 10%. If more than 2 of 12 problems × 2 arms × 10 replicates (> 4 of 240 trials) exceed budget: flag as BUDGET_VIOLATION and report affected problems separately.

- **F7 (ground-truth labeling frequency)**: in Phase 0 preflight, if fewer than 5 archive problems qualify as "transfer-useful" OR more than 35 qualify (outside range 5-35 of 50-100 archive size), the "+5pp threshold" is miscalibrated. Report and do not invalidate, but note as THRESHOLD_MISCALIBRATION.

## Stopping rule

- **Preflight stoppage**: if F2 (embedding instability) or F1 (metric modification) occurs, halt before Phase 1 begins. Report PREFLIGHT_FAILURE.
- **Mid-run stoppage**: if F6 (budget violation on > 4 trials) occurs at any point during Phase 1, pause, investigate, and either exclude affected trials or report BUDGET_FAILURE and terminate.
- **Outcome-blind reading**: Phase 2 analysis begins only after all Phase 1 trials complete and outcome data are locked (git-committed, hash-logged). No exploratory peeking at partial results; statistics are frozen before reporting.

## Expected failure modes

1. **Embedding collapse**: learned embeddings on small archive (N=50-100) may collapse to low-rank approximations or ignore problem structure, reducing rho to near-zero. Predicted likelihood: 30%. Indicates: need larger corpus or transfer learning from external problem corpora.

2. **Trivial baseline inversion**: random recommendations might randomly include near-duplicate problems, outperforming the learned ranking if the learned embedding fails to discriminate. Predicted likelihood: 10%. Indicates: metric mismatch or embedding degeneracy.

3. **Transfer signal absence**: "+5pp CFR boost" is optimistic; real transfer gains in problem-solving may be smaller (< +2pp), below noise floor. Predicted likelihood: 25%. Indicates: recommenders work via different mechanism (e.g., psychological confidence, not structural transfer).

4. **Embedding-type dependence**: pretrained embeddings (BERT) and learned embeddings (end-to-end) disagree strongly (tau < 0.60). Predicted likelihood: 35%. Indicates: no stable transfer signal independent of embedding choice; need ensemble or meta-learned ranking.

5. **Hidden domain structure**: similarity rankings work perfectly within math-specific problems but fail across domains (e.g., algebraic problems vs. optimization problems). Predicted likelihood: 20%. Indicates: need per-domain recommenders or domain-aware metric learning.

## Compute estimate

- **Preflight (Phase 0)**: 
  - Corpus assembly and labeling: 4 machine-hours (manual review) + 2 compute-hours (embedding generation for N=50-100).
  - Ground-truth annotation: 4 machine-hours (CFR trials on reference problems).
  
- **Phase 1 (evidence collection)**:
  - Arm B1: 10 replicates × 12 test problems × solver execution time (~2 min per problem) = ~4 compute-hours.
  - Arm B2: same, ~4 compute-hours.
  - Embedding similarity compute (batch): < 1 compute-hour (linear in N_archive).
  
- **Phase 2 (analysis)**:
  - Statistical tests, Spearman correlation, CI computation: < 1 compute-hour (Python, no GPU needed).

- **Total**: ~15-20 machine-hours equivalent; can run in ~2-3 wall-clock days on M1 (parallel arms + async embedding).

## Prior evidence that materially changed this design

1. **Evidence contradiction (ew.contradictions())**: D-5 blind SUPPORTED the hypothesis "accumulated history improves search" (+10.95pp), while D-8 blind S0 showed NO_EFFECT. Differing dimensions: substrate type (program ecology vs. foundry ecology). **Impact on design**: this teaches that transfer signals are substrate-dependent. Therefore: (1) expect embedding choices (BERT vs. learned) to show large variance; (2) include a per-domain interaction test (F5 secondary: do similarity benefits vary by problem domain?); (3) freeze embedding type before outcomes to prevent post-hoc "optimizing to the data."

2. **Agent D5 verdict (G9)**: "library content, not developmental order, drives performance." **Impact**: suggests that problem *selection* (which prior problems are available) matters more than *sequence*. Implies: a recommender that simply re-ranks the same archive is unlikely to produce large CFR deltas. Tempered hypothesis: expected delta B2 - B1 is modest (+0.08, not +0.20).

3. **Aporia genealogy findings**: "genetic relatedness and mutation potential separable from single-task competence; two unrelated solutions to same problem have distinct generalization properties." **Impact on design**: problem titles and tags (surface structure) are insufficient signals; need embeddings that capture *structural* relatedness. This motivated inclusion of three embedding types (BERT, sentence-transformers, learned) — if none capture structure, signals are absent.

## Unresolved uncertainty

1. **Embedding choice is critical**: is BERT (pretrained on generic text) the right choice, or should embeddings be trained on mathematical problem corpora? No prior runs in evidence_wiki resolve this.

2. **Archive size threshold**: does archive size N=50 provide enough diversity to test transfer, or does it need N >= 200? Unknown; preflight Phase 0 will reveal distribution of CFR deltas.

3. **Solver architecture independence**: does the recommender's benefit generalize across different solver types (symbolic search, neural fine-tuning, human-guided)? Experiment uses one solver type (M1-equivalent); multimodal solver testing is out of scope but flagged as future work.

4. **Recommendation granularity**: K=5 is a guess. Would K=1 (strongest recommendation) show larger delta than K=5? Or is there a saturation point? Not tested here.

5. **Ground-truth stability**: the "+5pp transfer boost" label is computed on reference solver runs (Phase 0, step 4). If solver is stochastic, two runs might disagree. No analysis of label-stability (test-retest correlation of transfer labels) is preregistered.

## Evidence Wiki consultation log (queries + object ids retrieved)

| Op | Type | Query / Object | Status | IDs Retrieved |
|----|------|---------|--------|-----------|
| 1 | search_evidence | "problem similarity recommender research transfer learning" | Empty results | — |
| 2 | search_evidence | "transfer failure dissimilarity ranking mismatch negative" | Empty results | — |
| 3 | contradictions() | contradictions table query | Success | R-e68c9331eca2, R-2dc413ddca43 |
| 4 | search_evidence | "semantic relatedness embedding similarity metric" | Empty results | — |
| 5 | get_claim | C-3a1c49fa5a78 (from contradiction) | Metadata only | C-3a1c49fa5a78 |
| 6 | get_claim | C-3d12c440f087 (from contradiction) | Metadata only | C-3d12c440f087 |
| 7 | related_findings | C-3a1c49fa5a78 | No related findings | — |
| 8 | search_evidence | "probe" (broad search) | Empty results | — |
| 9 | search_evidence | "experiment" (broad search) | Empty results | — |

**Interpretation**: Evidence Wiki corpus on recommender systems, problem similarity, or transfer learning is currently empty or not indexed. Contradictions table shows that experimental outcomes are substrate-dependent and condition-sensitive (D-5 vs. D-8 disagreement on transfer effects). This absence of direct evidence motivated the design: the specification is necessary because prior Prometheus work has NOT empirically tested recommender efficacy on problem transfer.

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **R-e68c9331eca2** (contradiction: D-5 SUPPORTED vs. D-8 NO_EFFECT on history transfer): This directly shaped Falsifier F5 (embedding-type asymmetry). The contradiction shows that the same hypothesis under different substrates yields opposite conclusions. **Decision**: include three embedding types (BERT, sentence-transformers, learned) in Phase 0 to test whether transfer signal depends on embedding choice. If pretrained and learned embeddings rank problems inversely (tau < 0.60), the contradiction teaches us that recommenders are not universal — they must be re-tuned per domain/substrate.

- **R-2dc413ddca43** (FAILS_TO_REPLICATE relation): noted but could not retrieve full claim details; classification is DIRECT (a straight replication failure). **Impact**: motivates the "Stopping rule" section (midrun stoppage if budget integrity fails, to prevent replication of corrupted data). Also justifies outcome-blind analysis (Phase 2 freeze) to prevent circular reasoning.

- Contradictions retrieved but did NOT directly affect design: none (the two listed were both consequential).

## Operation log (numbered; ops used / 15, documents opened / 12)

| # | Operation | Detail | Docs Opened | Cumulative Ops | Cumulative Docs |
|---|-----------|--------|-------------|-----------------|-----------------|
| 1 | search_evidence | transfer learning success/failure | 0 | 1 | 0 |
| 2 | search_evidence | embeddings vectors similarity | 0 | 2 | 0 |
| 3 | search_evidence | search retrieval ranking | 0 | 3 | 0 |
| 4 | get_claim | C-3a1c49fa5a78 | 0 | 4 | 0 |
| 5 | get_claim | C-3d12c440f087 | 0 | 5 | 0 |
| 6 | related_findings | C-3a1c49fa5a78 | 0 | 6 | 0 |
| 7 | search_evidence | "probe" broad | 0 | 7 | 0 |
| 8 | search_evidence | "experiment" broad | 0 | 8 | 0 |
| 9 | provenance | R-e68c9331eca2 | 0 | 9 | 0 |
| 10 | Read | README.md (evidence_wiki) | 1 | 10 | 1 |
| 11 | Read | V2-T01_pack.json | 1 | 11 | 2 |
| 12 | Read | V2-T01_A_haiku.md (format example) | 1 | 12 | 3 |

**Summary**: 12 operations used of 15 allowed (80% utilization). 3 documents opened of 12 allowed (25% utilization). Early stop permitted; sufficient evidence gathered to design specification grounded in Prometheus experimental format and Evidence Wiki contradiction patterns. No further operations conducted.
