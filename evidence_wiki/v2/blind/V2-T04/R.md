# PROPOSAL V2-T04 (arm)

## Hypothesis
A hybrid recommender system combining BM25 full-text search, semantic embeddings (all-MiniLM-L6-v2), domain/subdomain taxonomy, and content-derived tags can identify the K=5 most similar previously-attempted research problems to a new incoming problem with >75% rank correlation to expert ground truth, without requiring labeled training data on problem similarity pairs.

## Motivating evidence
- **Problem corpus density:** 1,094 problems across 14 domains (mathematics 537, physics 304, computer science 41) with consistent JSONL schema (id, title, domain, subdomain, statement, tags, related_ids, importance).
- **Ground truth availability:** The `related_ids` field on 537/1094 records encodes domain-expert-curated problem relations, providing an observable proxy for semantic similarity.
- **Existing infrastructure:** Evidence-wiki skill already implements hybrid BM25+embedding search (`search_evidence`); aethon project validates all-MiniLM-L6-v2 embeddings as usable for novelty/distance measurement (cosine distance range 0.053–0.30).
- **Related-ID sparsity:** Related_ids averaging <2 links per problem suggests the "most similar" ground set is small and well-separated, reducing false-positive rates in rank evaluation.

## Prospective predictions
- **P1:** BM25-only baseline (lexical search on titles + statements) achieves <0.55 Spearman ρ against related_ids ground truth due to topic label blindness.
- **P2:** Embedding-only (cosine similarity in title+statement embedding space) achieves 0.62–0.68 ρ by capturing semantic relation but misses domain-specific conventions (e.g., "Goldbach-like" conjectures in mathematics clustering despite different formal fields).
- **P3:** Hybrid (BM25 + embedding + domain agreement + tag overlap + importance distance) achieves 0.76–0.82 ρ, passing the >0.75 gate, due to cross-modal redundancy filtering false positives.
- **P4:** Cold-start queries (problems newly generated, not in corpus) show 0.70–0.74 ρ, reflecting embedding generalization gap when problem statement is synthetic or phrased differently from corpus priors.

## Experiment

### Data and sampling
- **Corpus:** All 1,094 problems from `/f/Prometheus/aporia/*/questions.jsonl` across 14 domains.
- **Test set:** Stratified sample of 50 problems (seed-resampled from per-domain strata) with ≥1 observed `related_ids` entry (N=537 eligible). Aim ≥5 related links per sampled problem to ensure dense ground truth.
- **Holdout construction:** For each test problem P, partition its related_ids into 5-fold CV; use 4-folds as ground truth for ranking, reserve 1-fold for external validity check.
- **Query variants:** 
  - *V1 (Canonical):* Use corpus title and statement as-is.
  - *V2 (Paraphrased):* Synthetically paraphrase each test problem's statement using a fixed prompt (GPT-4, temperature=0.3, one rewrite per problem, deterministic seed). Measures robustness to phrasing variance.
  - *V3 (Abbrevated):* Truncate statement to first sentence only. Measures robustness to information loss in sparse problem descriptions.

### Recommender pipeline
1. **Text indexing:** Build BM25 index on `{title, statement}` using rank-bm25 library (k1=1.5, b=0.75, default stopwords).
2. **Embedding:** Encode `{title, statement}` concatenated with ` [DOMAIN: {domain}]` using all-MiniLM-L6-v2 (768-dim); store in dense matrix.
3. **Similarity scoring (per candidate problem C, given query Q):**
   - s_bm25(Q, C) = BM25 rank-inverse (5 - rank / max_rank, clamped to [0, 5])
   - s_emb(Q, C) = cosine(embed(Q), embed(C))
   - s_domain(Q, C) = 1.0 if domain match, 0.5 if subdomain match, 0.0 otherwise
   - s_tag(Q, C) = Jaccard(tags(Q), tags(C)) (currently 0 since tags sparse, but structure ready)
   - s_importance(Q, C) = 1.0 - |importance_rank(Q) - importance_rank(C)| / max_rank, cap [0, 1]
4. **Hybrid score:** s_hybrid = 0.30*s_bm25 + 0.40*s_emb + 0.20*s_domain + 0.05*s_tag + 0.05*s_importance
5. **Ranking:** Retrieve top K=5 candidates by s_hybrid, excluding Q itself and already-promoted duplicates.

### Evaluation metric
- **Primary:** Spearman rank correlation ρ between recommender's K=5 ranking and position-weighted recall on ground-truth related_ids (if G is ground truth set, metric = (sum of 1/rank for hits) / sum(1/1..K)).
- **Secondary:** Mean Reciprocal Rank (MRR) of first match to ground truth in top-5.
- **Tertiary:** Coverage—% of test problems with ≥1 ground-truth match in top-5.
- **Per-query-variant:** Compute ρ separately for V1, V2, V3 to isolate robustness.

## Controls

### Baseline recommenders (no-learning alternatives)
- **C1 (Domain proximity only):** Rank candidates by (domain_match, subdomain_match, random tiebreak). Expected ρ ≈ 0.35–0.45.
- **C2 (Random within domain):** Shuffle within each domain; expected ρ ≈ 0.05–0.15.
- **C3 (Lexical distance only):** BM25 rank without embedding; expected ρ ≈ 0.50–0.60 (per P1).

### Ablation studies (hybrid minus component)
- **A1:** Hybrid − embedding (BM25 + domain only).
- **A2:** Hybrid − domain (BM25 + embedding only).
- **A3:** Hybrid − BM25 (embedding + domain only).
- **A4:** Uniform weight all components (0.2 each); measure if weighting matters.

### Null controls (corruption checks)
- **N1:** Shuffle statement text character-wise (preserves length, destroys semantics); expected ρ floor ≈ 0.05.
- **N2:** Replace statement with random domain-name permutation; confirms embedding relies on actual text.

## Confound defenses

### Confound: Corpus homogeneity (related_ids biased toward nearby domains)
- **Defense:** Stratify test set by domain; compute ρ separately per domain (report min/median/max). If within-domain ρ >> cross-domain ρ, indicates confound; if ρ stable, confound absent.

### Confound: Related_ids incompleteness (missing true relations)
- **Defense:** Use related_ids as **lower bound** on similarity only. Secondary validation: sample 20 test problems, have domain expert manually verify if top-5 recommender results are plausible (Likert 1–5 per match). Expert score correlated with ρ validates internal consistency of related_ids as proxy.

### Confound: Title-driven false positives (acronym/name overlap without semantic relation)
- **Defense:** Flag top-5 results where title cosine > 0.85 but statement cosine < 0.50; audit manually; report false-positive rate and impact on final ρ. If FP rate >10%, adjust embedding window or add anti-correlation term.

### Confound: Embedding model drift across versions
- **Defense:** Lock all-MiniLM-L6-v2 version and tokenizer at `sentence-transformers==2.5.0`; document git commit. Reproduce on fresh VM to verify determinism.

### Confound: Weight tuning leakage (weights fitted to test set)
- **Defense:** Fix weights a priori using domain knowledge (text 70%, structure 30%); do not fit to ρ. If weights updated, report as speculative extension, not core result.

## Preregistered falsifiers (numeric thresholds)

1. **FALSIFY-PRIMARY:** If Spearman ρ on V1 canonical queries < 0.72, the hybrid recommender fails the >0.75 gate. Verdict: "hybrid insufficient; requires learner training or hand-engineered features."

2. **FALSIFY-ROBUSTNESS:** If ρ(V2 paraphrased) < 0.65 or ρ(V3 abbreviated) < 0.60, the recommender is brittle to phrasing; verdict: "embedding generalization gap; structure alone insufficient."

3. **FALSIFY-COVERAGE:** If coverage (<1 ground-truth match in top-5) < 70%, verdict: "top-5 too small; increase K or threshold."

4. **FALSIFY-BASELINE-MARGIN:** If any baseline (C1–C3) achieves ρ > 0.68, confound likely (structure alone is doing the work); verdict: "recommender not leveraging embeddings; rebalance weights."

5. **FALSIFY-DOMAIN-BIAS:** If max(ρ per domain) - min(ρ per domain) > 0.30, strong domain-specific confound; verdict: "per-domain tuning required; not general recommender."

6. **FALSIFY-EXPERT-MISMATCH:** If expert manual review score (Likert) anti-correlates with ρ by > |−0.3|, related_ids proxy is invalid; verdict: "ground truth unreliable; redesign metric."

## Stopping rule

1. **Data collection:** Halt after test set of 50 stratified problems. Stop early if corpus queries exhaust all 1,094 problems (unlikely; each test problem samples ~200–300 comparisons).

2. **Computation:** Each test query runs 2 embedding passes (V1, V2, V3); 50 queries × 3 variants × ~3 sec per full embedding = ~450 sec total. Halt if runtime exceeds 1 hour (abort slow models).

3. **Decision rule:** Evaluate all 6 falsifiers simultaneously. If ≥2 falsifiers fire, stop and conclude recommender insufficient. If 0–1 fire, proceed to secondary validation (expert audit). If expert audit confirms >3.5 Likert on ≥60% of top-5 matches, declare success and propose learner training as next phase.

## Expected failure modes

1. **Embedding collapse:** all-MiniLM-L6-v2 treats mathematical statements as generic English; cosine distances plateau at 0.3–0.5, erasing fine-grained distinctions (e.g., "Goldbach" vs "twin primes" both ~0.5 distance). Mitigation: add domain-specific embedder (sciBERT) in ablation A3.

2. **Domain label sparsity:** tags field is empty on 95% of records; Jaccard overlap is always 0. Verdict: tag component is dead weight; recommend 0.0 tag weight for production.

3. **Paraphrasing brittleness (V2):** GPT-4 paraphrases may drift semantically (e.g., "find X" → "does X exist"), causing embedding divergence. Expected ρ(V2) = 0.50–0.60 vs 0.76 on V1. Mitigation: use deterministic synonym replacement instead of generative paraphrase.

4. **Cold-start ceiling (P4 prediction):** synthetic "new" problems phrased differently from corpus vocabulary may score <0.60 ρ. If critical, requires transfer learning or few-shot adaptation.

5. **Ablation paradox:** BM25-only (A1 + A2) may exceed hybrid on some domains (e.g., number theory, where "Goldbach conjecture" lexical match is stronger signal). If |ρ(BM25) - ρ(hybrid)| < 0.05 on >3 domains, embedding adds noise; recommend domain-specific weighting.

## Compute estimate

- **Text indexing & embedding:** ~15 min (vectorization of 1,094 problems at ~1 sec per problem on CPU).
- **Query evaluation:** 50 queries × 3 variants × 1,094 candidates × 10 µs per score = ~1.6 sec.
- **Evaluation metrics & plots:** ~5 min.
- **Manual expert audit (20 problems × 2 min ea):** ~40 min (if parallelized, negligible in wall-clock).
- **Total:** ~60 min CPU, ~90 min wall-clock on single machine (no GPU needed; all-MiniLM-L6-v2 runs on CPU).

## Prior evidence that materially changed this design (or 'none found')

**Evidence incorporated:**
1. **Aethon project (2026-08-20):** Validated all-MiniLM-L6-v2 as usable for distance measurement; informed embedding choice and cosine-distance range expectations.
2. **Evidence-wiki skill (2026-current):** Demonstrated hybrid BM25+embedding search is production-viable; informed weight structure (70% information-bearing, 30% structural).
3. **MEMORY.md feedback on sampling strategy (08-24):** "Alphabetical shard iteration is a sampling-window antipattern; stratify" — applied to test-set construction (stratified sample per domain, not prefix sampling).
4. **Feedback on validation (08-23, "verify signature exists before controls"):** Mandated manual expert audit on 20 problems to validate related_ids as ground truth proxy before declaring success.

**No contradictory evidence found** that would argue for learner-based vs. heuristic recommender at this scale.

## Unresolved uncertainty

1. **Optimal weight set:** Preregistered weights (0.30/0.40/0.20/0.05/0.05) are domain-knowledge guesses, not fitted. Ablation A4 (uniform weights) tests sensitivity; if no difference, weights are not a bottleneck.

2. **Generalization to non-mathematics:** Experiment focuses on corpus (537 math + 304 physics + 253 other). If physics/biology show ρ < 0.60, domain-specific embedders (sciBERT, PubMedBERT) may be required; verdict would be "recommender generalizes within STEM, not across."

3. **Cold-start variant (V3 abbreviated) efficiency:** If ρ(V3) > 0.68, abbreviated queries are viable (faster ingestion, lower bandwidth). If <0.60, full statements required (infrastructure cost).

4. **Related_ids bias toward recent problems:** Older problems may have fewer recorded relations; if test set skews recent, ρ may be inflated. Stratify by year_posed to audit (if available; field often null).

5. **Semantic drift in paraphrased variant:** GPT-4 at temperature=0.3 may still diverge from intent; deterministic synonym-replacement (V3) may be more reproducible than generative paraphrase (V2). Recommend V3 as primary robustness check if V2 shows >0.10 ρ drop.

