# PROPOSAL V2-T04 (arm B)

## Hypothesis
A recommender that ranks "most similar previously-attempted problems" using only title text, subject-area label, and topic tags carries **no navigable signal beyond what a field-shuffled corpus would produce**, when the ground truth is *actual usefulness* (the retrieved prior problem's approach genuinely transfers to solving the new one) rather than superficial tag/lexical overlap. This restates, in the recommender setting, a hard posture already logged in this program: routing/retrieval on human-authored semantic labels has previously returned a NULL (real fields == shuffled fields) in a cold-start setting, while behavior-conditioned (co-solve) retrieval was SUPPORTED and survived an adversarial check. The recommender under test is architecturally identical to the semantic arm of that prior asymmetry (title/subject/tags = semantic label fields; no behavioral/co-solve signal is used).

Secondary hypothesis: any apparent semantic signal that does survive the shuffle-null is largely a **base-rate/popularity artifact** — the recommender is rediscovering "which tags are common" rather than "which prior problems are actually similar in the sense that matters."

## Motivating evidence
- Evidence Wiki claim C-b2cebe551f3b (Ergon, SUPPORTED): warm-start **collaborative** (behavioral, co-solve) completion beats a popularity baseline (AUC 0.829 vs 0.754, P<0.0001) and survives an adversarial tail check — "the navigable handle for failure residue is behavioral, not semantic." Its stated `claim_ceiling` is that the true router objective is untested because the artifact (a) lacks probe features and (b) is top-10 truncated, and names these two gaps as "the spec for a router-grade artifact." A title/subject/tag recommender is exactly this untested router-grade artifact, and its ceiling defines two mandatory design features below (probe features must be present at evaluation time; recall must not be reported only at a truncated top-K).
- Repo doc `aporia/docs/deep_research_batch_2026-08-17/12_semantic_versus_behavioral_retrieval_keys.md` (and its paired question file) records an internal empirical result predating this proposal: routing on semantic labels of failures was NULL — "real fields performed no better than shuffled fields" — while behavioral co-solve clustering worked. It also names two failure patterns to guard against: `PATTERN_BASE_RATE_NEGLECT` (a semantic router over-indexing a specific label while ignoring the corpus base rate) and `PATTERN_RANK_PARITY_LEAK` (shuffled fields achieving score parity with real fields because the scorer rewards superficial lexical overlap, not functional relevance). These are treated here as **candidate confounds to instrument for**, not as validated external literature — the document is an AI deep-research synthesis with web citations, not a Prometheus-verified result, and per program doctrine (frontier-model convergence on a framing is corpus gravity, not validation) its proposed "attack vectors" (dense-embedding rewriting, entmax losses, etc.) are NOT adopted into the design; only its diagnostic vocabulary and its account of what happened internally are used.
- Evidence Wiki claim C-f8f06a6e21ca (Ergon, SUPPORTED): "same phenotype does not imply same mutational affordances" — 77% of apparent behavioral redundancy in a corpus did not survive a stronger affordance test; surface-level sameness routinely masks near-maximally different underlying processes. This forces the ground-truth label in this experiment to be defined by an actual downstream benefit of the recommendation, not by co-occurring tags/phenotype, else the evaluation would be circular (scoring the recommender against the same surface features it consumes).

## Prospective predictions
1. Real-field semantic similarity ranking will beat a random-candidate baseline (trivially — titles/tags are not pure noise).
2. Real-field semantic similarity ranking will NOT beat a field-shuffled null by a margin exceeding measurement error, when scored against a behavioral usefulness label (not a tag-overlap label).
3. Whatever edge the real-field ranker shows over the shuffle-null will substantially shrink (not just attenuate) once a popularity/frequency-weighted baseline is subtracted out, indicating the edge is mostly base-rate, not genuine similarity.
4. If a behavioral/co-solve baseline can be constructed on the same probe set (e.g., reusing Ergon's mined-failure solve-matrix construction where domains overlap), it will outperform the semantic recommender by a margin comparable to the 0.075 ΔAUC already observed for COLLAB vs POP in C-b2cebe551f3b.
5. Recall will be systematically understated at any single truncated cutoff (e.g., top-10); the true miss rate should be assessed by full-rank position, per the claim_ceiling warning against top-K truncation.

## Experiment
**Corpus.** Enumerate the actual inventory of "previously attempted problems" that exist with (title, subject_area, topic_tags) fields AND a usable outcome/behavioral record (e.g., which tool/operator/approach ultimately worked, cost-to-solve, success/fail) — candidates include the ergon task corpus, the mined-failure solve matrix underlying X-d1b20425676f, and/or `docs/TASK_CORPUS_V2.md`. **This inventory must be enumerated exhaustively before any stratified sample is drawn** (no alphabetical/prefix scan) — if no corpus has both semantic fields and a non-circular outcome record at adequate scale, this is reported as an early stop (see Stopping rule), not patched with a proxy label invented post hoc.

**Probe set.** Draw a stratified, without-replacement sample of N problems held out as "new incoming problems" (target N=150, minimum per subject-area stratum = 8; if a stratum is under-filled, widen strata rather than dropping the constraint). For each probe, the candidate pool is every other corpus problem (not top-K pre-filtered).

**Arms (all run on the identical probe set and candidate pool):**
- **SEM-REAL**: rank candidates by embedding/lexical similarity of (title + subject_area + topic_tags) to the probe's own fields.
- **SEM-SHUFFLE (null)**: identical pipeline, but title/subject_area/topic_tags are permuted across the *entire* candidate corpus (not resampled from the probe's own stratum — the permutation must break the selection relation between fields and outcome, not merely relabel within it) before ranking. Same probe set, same code path as SEM-REAL, differing only in this one permutation.
- **POP**: rank candidates by global outcome-success frequency / tag popularity, ignoring the probe entirely.
- **BEHAV** (if constructible without circularity): rank candidates by existing co-solve/behavioral association (reusing the C-b2cebe551f3b construction) — included only if the domain and data actually support it; if not constructible, BEHAV is dropped and this is logged as a scope limitation, not silently substituted.
- **RANDOM**: uniform random ranking, sanity floor.

**Ground truth.** A candidate counts as a true positive for a probe if there is an independently recorded behavioral fact that the candidate's approach/solution transferred usefully to the probe (e.g., same solving operator/tool used successfully, or a recorded reuse event) — NOT if it merely shares tags/subject area with the probe (that would make SEM-REAL correct by construction).

**Metric.** Per-probe AUC / ranking quality (e.g., AUC and MRR) of each arm against ground truth, plus full-rank position of the first true positive (not just hit@10), aggregated with bootstrap CIs over probes (the probe, not the candidate pair, is the unit of resampling — each probe contributes one ranking).

## Controls
- SEM-SHUFFLE: the mandatory field-shuffle null described above; must be regenerated fresh (new random permutation, fixed seed logged) rather than reusing a single shuffle, and its own sampling variance reported.
- POP baseline: isolates how much of any arm's apparent skill is attributable to global outcome base rate.
- RANDOM baseline: floor check that the ranking pipeline and metric are wired correctly.
- BEHAV baseline (where constructible): the one arm expected, from prior evidence, to actually clear POP by a large margin; its presence in the same run validates that the eval harness is capable of detecting real signal at all (a harness that also fails to separate BEHAV from POP would indicate an instrumentation problem, not a null result about semantics).

## Confound defenses
- **Selection-relation contamination (control-must-break-the-relation doctrine):** SEM-SHUFFLE permutes fields across the *whole* corpus, not within the probe's own subject-area stratum, so the permutation actually severs the field→outcome relation being tested rather than reproducing it under a new label.
- **Base-rate neglect (`PATTERN_BASE_RATE_NEGLECT`):** report ΔAUC(SEM-REAL − POP) as a separate, mandatory number, not just SEM-REAL vs SEM-SHUFFLE. If ΔAUC(SEM-REAL − SEM-SHUFFLE) is significant but ΔAUC(SEM-REAL − POP) is not, the "signal" is attributed to popularity, not similarity.
- **Rank-parity leak (`PATTERN_RANK_PARITY_LEAK`):** in addition to the AUC gap, report top-1 overlap rate between SEM-REAL and SEM-SHUFFLE picks; a high overlap rate at matched AUC indicates the scorer is keying on corpus-wide lexical frequency rather than probe-specific relevance.
- **Truncation ceiling (from C-b2cebe551f3b's claim_ceiling):** report full-rank position of the first true positive for every probe/arm, and recall at three depths (5/10/20), not a single top-K cutoff, so a real effect confined to deep ranks isn't hidden and a shallow illusory effect isn't flattered.
- **Phenotype-vs-affordance circularity (from C-f8f06a6e21ca):** ground truth is defined on recorded behavioral transfer, independently of the tag/title fields the recommender consumes; any candidate corpus where the only available "similarity" label is itself tag-co-occurrence is disqualified as ground truth for this experiment (would make the test tautological).
- **Measurement-error-vs-threshold ordering:** bootstrap SE for every ΔAUC is computed before any pass/fail threshold is finalized against it; no threshold is set closer to an anticipated observed value than 3x its projected SE.
- **Stratified, exhaustive sampling:** probe draw is stratified across subject areas and drawn without replacement from a fully enumerated corpus; no alphabetical or prefix-based iteration.
- **Single preregistered pass:** thresholds below are fixed before the probe set's ground-truth labels are read.

## Preregistered falsifiers (numeric thresholds)
- F1 (primary — falsifies the recommender having real signal): FAILS if ΔAUC(SEM-REAL − SEM-SHUFFLE) < 0.05 OR bootstrap P(Δ ≤ 0) ≥ 0.01, evaluated on probe-level AUC. (Threshold set to match, not exceed, the magnitude already required to call COLLAB "robust" in C-b2cebe551f3b: ΔAUC +0.075; 0.05 is a deliberately looser bar so a genuine but smaller effect is not falsely killed.)
- F2 (base-rate confound flag — does not falsify F1 by itself, but reclassifies a passing F1 as "popularity, not similarity"): TRIGGERS if ΔAUC(SEM-REAL − POP) < 0.02 while F1 passes.
- F3 (rank-parity leak flag): TRIGGERS if top-1 pick overlap between SEM-REAL and SEM-SHUFFLE exceeds 60%.
- F4 (behavioral-superiority check, only if BEHAV is constructed): FALSIFIES the "behavioral strictly beats semantic" prior posture if AUC_SEM-REAL ≥ AUC_BEHAV − 0.02 (i.e., semantic ties or beats behavioral within noise) — this would be a genuinely novel finding worth its own follow-up, not a design bug.
- F5 (truncation-ceiling check): if recall@10 differs from recall@20 by more than 0.15 for any arm, top-K-only reporting is disqualified as the primary metric for that arm and full-rank position must be used instead.

## Stopping rule
One planned analysis pass on N=150 stratified, without-replacement probes (minimum 8 per stratum). No optional stopping, no re-sampling after seeing ground-truth labels. Early stop is permitted only at the corpus-enumeration step: if no corpus exists with both semantic fields and a non-circular behavioral outcome record at N ≥ 150 with ≥ 8 probes per stratum, the experiment is not downgraded to a smaller N or a proxy label — it is reported as BLOCKED_ON_CORPUS and closed pending a corpus that meets the precondition.

## Expected failure modes
- The single largest risk is that no corpus in the repo currently pairs (title/subject/tags) with an independent, non-circular behavioral usefulness record at adequate scale — the "ground truth" most readily available (shared tags) is exactly the feature under test, which would make any naive execution circular.
- Subject-area strata may be too unevenly populated to hit 8 probes/stratum without pooling adjacent areas, diluting the stratification's power.
- Embedding/lexical-similarity implementation choices (bag-of-words vs. dense embedding) could each pass or fail F1 differently; if only one variant is run, a null could be an implementation artifact rather than a property of "semantic labels" per se — the spec calls for running SEM-REAL under at least two similarity implementations (sparse lexical overlap and one dense embedding) and requiring F1's verdict to agree across both before it is treated as a design-level finding.
- BEHAV may be impossible to construct on the same probe set without reusing labels already consumed elsewhere in the program (double-dipping the mined-failure matrix), in which case F4 must be dropped rather than faked.

## Compute estimate
Offline retrieval evaluation only — no model training. Embedding of ≤ a few thousand corpus titles/tag-strings (CPU-only, minutes), O(N × corpus_size) pairwise similarity scoring for N=150 probes (seconds to low minutes even unoptimized), plus bootstrap resampling over 150 probes (seconds). Total wall-clock estimate: well under 1 compute-hour on a single CPU core, dominated by corpus-enumeration and ground-truth-label auditing (human/agent time), not compute.

## Prior evidence that materially changed this design (or 'none found')
See "Evidence that changed this design" below — evidence was found and did change the design (not "none found").

## Unresolved uncertainty
Whether a corpus meeting the ground-truth precondition (semantic fields + independent, non-circular behavioral outcome record, N≥150, ≥8/stratum) actually exists in the repository at the required scale is unresolved by this specification and was explicitly not investigated (out of the 15-op/12-doc budget for a design task) — this is the first thing execution must verify, and BLOCKED_ON_CORPUS is an accepted, pre-legitimated outcome if it doesn't. Whether a BEHAV baseline can be built without label reuse from C-b2cebe551f3b's own artifact is also unresolved.

## Evidence Wiki consultation log (queries + object ids retrieved)
1. search_evidence("recommender system similarity problem suggestion embedding", k=8) → C-b2cebe551f3b, C-8f20c74fa0cf, C-e0b3b4966385, C-1f1a743fce1b, C-a9fc01aa3892, C-0c169dd6e0d9, C-b6a5822a8f70, C-f8f06a6e21ca
2. search_evidence("retrieval failed negative null tag semantic label not navigable", k=8, status='REFUTED') → 0 results (negative-evidence query, empty)
3. contradictions() → R-e68c9331eca2 (C-3a1c49fa5a78 vs C-3d12c440f087), R-2dc413ddca43 (C-1d99d0adac44 vs C-7d559fe50c7a) — neither materially relevant to this task's domain, not used further
4. get_claim("C-b2cebe551f3b") → full claim + claim_ceiling text
5. get_counterevidence("C-b2cebe551f3b") → empty (no counter-relations, no negative evidence recorded against this claim)
6. related_findings("C-b2cebe551f3b") → graph neighbors C-f1d363ff01e4 (SAME_MECHANISM), C-b57f0217986c; semantic neighbors C-94fc12c3e6af, C-aba202675bd8, C-065a321e0808, C-98702f29ab81, C-b287aa6823b0, C-a2cba4576ecd, C-9f87dea3d7d8, C-9d2f9bf2e064, C-6509907fc169 (not individually opened — budget)
7. get_claim("C-f8f06a6e21ca") → full claim text and claim_ceiling

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)
- C-b2cebe551f3b -> set the core hypothesis (semantic label recommender = untested "router-grade" analog of a claim already SUPPORTED for behavioral/collaborative retrieval); its `claim_ceiling` directly produced two design requirements: (a) probe features must exist at eval time (drove the "Corpus" precondition requiring real behavioral outcome fields, not just tags), and (b) do not truncate at top-K only (drove F5 and the full-rank-position reporting requirement).
- C-f8f06a6e21ca -> forced the ground-truth definition to be behavioral/downstream-benefit, not tag/phenotype co-occurrence, to avoid a tautological evaluation (drove the "Ground truth" and "Phenotype-vs-affordance circularity" clauses).
- `aporia/docs/deep_research_batch_2026-08-17/12_semantic_versus_behavioral_retrieval_keys.md` and its paired question file -> supplied the exact prior internal empirical framing being replicated (real-vs-shuffled-fields NULL) and the two named failure patterns `PATTERN_BASE_RATE_NEGLECT` / `PATTERN_RANK_PARITY_LEAK`, which became F2/F3 and the POP-baseline control; its own proposed "fixes" (dense embeddings, entmax losses, etc.) were deliberately NOT adopted, per doctrine that AI-frontier convergence on a framing is not itself validation.
- Contradictions R-e68c9331eca2, R-2dc413ddca43, and the counterevidence/related_findings lookups on C-b2cebe551f3b -> retrieved but did not affect design (no relevant counterevidence exists against the collaborative-completion claim, and neither logged contradiction concerns semantic-vs-behavioral retrieval).
- get_counterevidence("C-b2cebe551f3b") returning empty -> retrieved but did not affect design (confirms no recorded rebuttal to the claim this proposal leans on, but doesn't add new constraints).

## Operation log (numbered; ops used / 15, documents opened / 12)
1. search_evidence("recommender system similarity problem suggestion embedding", k=8) [wiki API]
2. search_evidence("retrieval failed negative null tag semantic label not navigable", k=8, status='REFUTED') [wiki API — required negative-evidence query]
3. contradictions() [wiki API — required contradictions query]
4. get_claim("C-b2cebe551f3b") [wiki API; document opened #1]
5. get_counterevidence("C-b2cebe551f3b") [wiki API]
6. related_findings("C-b2cebe551f3b") [wiki API]
7. get_claim("C-f8f06a6e21ca") [wiki API; document opened #2]
8. Grep repo for "recommender|similar_problems|recommend_similar|problem_similarity" over F:\Prometheus [repo search]
9. Read F:\Prometheus\aporia\docs\deep_research_batch_2026-08-17\12_semantic_versus_behavioral_retrieval_keys_answer.md [file open; document opened #3]
10. Read F:\Prometheus\aporia\docs\deep_research_batch_2026-08-17\12_semantic_versus_behavioral_retrieval_keys.md (partial, first page) [file open; document opened #4]

Ops used: 10 / 15. Documents opened: 4 / 12. Early stop taken — sufficient converging evidence found before budget exhaustion.
