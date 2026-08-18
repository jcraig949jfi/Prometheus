# Report 13 — Solution-Paradigm Tagging Methodology at Scale

**Project Prometheus / Aporia / Pivot Research Batch 1**
**Date:** 2026-05-02
**Topic:** NLP, structured extraction, and weak supervision for tagging mathematical solutions with the P01..P22 attack-paradigm catalog.

---

## 1. Situation

Prometheus's Bloom-Erdős and MathNet ingests will produce ~30K+ solved-problem / solution-sketch pairs. Each must be tagged against the 18+2 attack-paradigm catalog (`aporia/docs/attack_angle_taxonomy.md`, P01..P22). These tags are not cosmetic — they become the **supervised signal** for any future RL agent's paradigm-recognition head, the discriminator for paradigm-coverage rewards in the Gymnasium env (Report 01), and the retrieval key for analogical reasoning over the corpus. Mis-tagging at scale poisons every downstream learner; over-confident hallucinated tags are *worse* than missing tags because they contaminate without leaving a missing-data flag. The methodology must therefore be **calibrated, multi-source, and firewalled from auto-labeled training drift** before a single RL gradient is taken.

---

## 2. State of the Art

**Weak supervision (Snorkel, Skweak, FlyingSquid).** Snorkel's labeling-function paradigm — write 20-50 noisy heuristics (regex, gazetteers, structural matchers like "uses Galois representation modularity"), aggregate via a generative label model that learns LF accuracies from agreement structure — is the gold standard for domain-specific tagging without per-example annotation. Reported accuracy on biomedical/legal corpora: 80-92% F1 on multi-class with 30-50 LFs and a few hundred gold labels for the discriminative end-model. Skweak (Lison et al., 2021) extends this to span/sequence labeling with HMM-based aggregation and is well-suited to citation-style "the proof uses [X]" extraction. **Calibration:** generative label models produce probabilistic outputs natively, but require Platt/isotonic recalibration on a gold dev set.

**NLP-based encoders.** SciBERT (Beltagy 2019), SPECTER (Cohan 2020), and MathBERT (Peng 2021) provide strong sentence/document embeddings for math text; fine-tuned with a few hundred labeled exemplars per paradigm class they reach 75-85% macro-F1 on MSC-2020-style classification. They have **no hallucination problem** (closed label set, softmax over P01..P22) but suffer from low recall on rare paradigms (P19 nonstandard analysis, P22 motivic) and miss multi-paradigm overlap unless reformulated as multi-label sigmoid heads.

**Fine-tuned / prompted LLMs.** GPT-class and Claude-class models with chain-of-thought + structured JSON output (constrained decoding via Outlines, JSON-mode, Guidance) reach 85-92% top-1 paradigm accuracy on hand-labeled math abstracts in published 2024-2025 benchmarks — but with **systematically over-confident calibration** (ECE 0.15-0.30) and 5-15% silent fabrication rate where the model invents plausible-sounding paradigm justifications for solutions it doesn't actually understand. Constrained decoding (JSON-schema with enum field) eliminates *format* hallucination but not *content* hallucination.

**Human-in-the-loop active learning.** Modal/uncertainty sampling (least-confident, BALD, core-set) reduces gold labels needed by 5-10x. Prodigy and Argilla are the production standards.

**Comparison summary:** Snorkel wins on calibration and zero-hallucination guarantee; LLMs win on raw accuracy and rare-class recall; fine-tuned encoders win on speed and reproducibility. **No single method dominates** — ensemble with disagreement gating is state of the art.

---

## 3. Recommended Pipeline for Prometheus

**(a) Seed corpus — hand-curated exemplars.**
Hand-tag 5-10 canonical solutions per paradigm: FLT (P05 modularity-lifting, P03 Galois-rep, P11 deformation-theory), Poincaré (P09 geometric-flow, P17 Ricci-surgery), Four-Color (P14 computer-assisted exhaustion), PFR / Polynomial Freiman-Ruzsa (P02 entropy-method, P08 additive-combinatorics), Green-Tao (P02 ergodic + P08), Wiles, Perelman, Tao-Ziegler, Maynard, etc. Target: ~150-250 exemplars covering all 22 paradigms, with multi-label where applicable (~60% of cases). Store as JSONL with full justification prose; this is the **gold-standard corpus**.

**(b) Snorkel labeling functions.**
Write 40-80 LFs over Bloom-Erdős solution text: keyword/phrase matchers ("zeta function", "Selberg trace", "Szemerédi regularity"), MSC-code mappers, citation-graph features (cites Faltings → P03/P05 prior), structural patterns ("by induction on ..." → P01). Train Snorkel label model on the 150-250 gold seeds; output probabilistic multi-label tags for the full 30K corpus.

**(c) LLM ensemble with cross-method agreement.**
Run two LLMs (e.g., Claude + a local Qwen/Llama-math) under JSON-schema constrained decoding emitting `{paradigms: [P##, ...], confidence: float, justification: str}`. **Mandatory agreement rule:** a tag survives only if (Snorkel marginal > 0.6) AND (LLM-A and LLM-B both list it) OR (≥2 of 3 with confidence > 0.8).

**(d) Aporia hand-review queue.**
Route to human review: (i) low-confidence cases (max marginal < 0.5), (ii) all multi-method disagreements, (iii) any tag never seen in gold seed for that solution-domain pair, (iv) stratified random 2% audit sample. Target queue size: 500-1500 items for first 30K batch.

**(e) Held-out evaluation.**
Reserve 200 hand-labeled solutions, never seen by any LF or LLM-prompt, as the **frozen evaluation set**. Re-evaluate every pipeline change. Track per-paradigm F1, macro-F1, expected calibration error (ECE), and hallucination rate (LLM tag absent from human consensus).

---

## 4. Anti-Patterns

**Single-LLM tagging.** Plausible-sounding wrong tags at scale. Without cross-method check, a sycophantic LLM will assign P05 (modularity) to anything mentioning elliptic curves. ECE on raw LLM outputs is consistently 0.15-0.30; treating its 0.95 confidence as actual 0.95 probability poisons downstream RL reward shaping. **Always require a second method to corroborate.**

**Training on LLM labels without firewall.** Catastrophic narrative drift: LLM-A labels corpus, fine-tuned encoder learns LLM-A's biases, RL agent rewarded for matching encoder, agent learns LLM-A's hallucinations as ground truth. This is the auto-labeled-training-data death spiral seen across NLP. **Mitigation:** all RL evaluation uses the held-out human-only gold set; auto-labels can train but never evaluate. (See `feedback_ai_to_ai_inflation.md`.)

**Ignoring multi-paradigm solutions.** ~60-70% of major proofs use 2-3 paradigms (FLT uses ≥4). Single-label classifiers force a winner-take-all that destroys the most informative signal. **Always multi-label** with sigmoid heads / probabilistic tags.

**Uniform calibration across paradigms.** Common paradigms (P01 induction, P02 probabilistic) calibrate easily; rare ones (P19 nonstandard, P22 motivic) need per-class temperature scaling. **Calibrate per paradigm class**, not globally.

**Heuristics-only.** Pure regex/gazetteer drift as math vocabulary evolves; needs LLM/encoder for semantic generalization. Pure LLM drifts on calibration; needs heuristics for grounding. Always both.

---

## 5. Concrete Next Steps for First Batch — Bloom-Erdős solved entries

1. **Week 1:** Hand-tag 150 exemplars across P01..P22 (James + 1 collaborator); freeze as gold seed + held-out 50.
2. **Week 1-2:** Author 50 Snorkel LFs over Bloom-Erdős solution text; train Snorkel label model.
3. **Week 2:** Run Claude + local Qwen-Math 14B with JSON-schema constrained decoding on full Bloom-Erdős solved subset.
4. **Week 3:** Merge via agreement rule (Section 3c); auto-tag the agreeing ~70% (~21K of 30K).
5. **Week 3-4:** Route ~500 disagreement/low-confidence items to Aporia review queue; report per-paradigm F1, macro-F1, ECE, hallucination rate against the held-out 50.
6. **Gate:** macro-F1 ≥ 0.75 and ECE ≤ 0.10 before any tag flows to RL training (Reports 01, 02).

---

## 6. References

1. Ratner, A. et al. (2017, 2020). *Snorkel: Rapid Training Data Creation with Weak Supervision.* VLDB / VLDB-J.
2. Lison, P., Barnes, J., Hubin, A. (2021). *Skweak: Weak Supervision Made Easy for NLP.* ACL System Demos.
3. Fu, D. et al. (2020). *Fast and Three-rious: Speeding Up Weak Supervision with Triplet Methods (FlyingSquid).* ICML.
4. Beltagy, I., Lo, K., Cohan, A. (2019). *SciBERT: A Pretrained Language Model for Scientific Text.* EMNLP.
5. Cohan, A. et al. (2020). *SPECTER: Document-level Representation Learning Using Citation-informed Transformers.* ACL.
6. Peng, S., Yuan, K., Gao, L., Tang, Z. (2021). *MathBERT: A Pre-Trained Model for Mathematical Formula Understanding.* arXiv:2105.00377.
7. Willard, B. T., Louf, R. (2023). *Efficient Guided Generation for Large Language Models (Outlines).* arXiv:2307.09702.
8. Lundberg, S. et al. (2023). *Guidance: A Guidance Language for Controlling LLMs.* Microsoft / GitHub.
9. Settles, B. (2009). *Active Learning Literature Survey.* Univ. Wisconsin TR-1648.
10. Houlsby, N. et al. (2011). *Bayesian Active Learning for Classification and Preference Learning (BALD).* arXiv:1112.5745.
11. Sener, O., Savarese, S. (2018). *Active Learning for CNNs: A Core-Set Approach.* ICLR.
12. Guo, C. et al. (2017). *On Calibration of Modern Neural Networks.* ICML. (temperature scaling, ECE).
13. Kadavath, S. et al. (2022). *Language Models (Mostly) Know What They Know.* Anthropic. (LLM self-calibration baseline).
14. Zhang, J. et al. (2022). *A Survey on Programmatic Weak Supervision.* arXiv:2202.05433.
15. Wang, B. et al. (2024). *Constrained Decoding for Structured Output: A Survey.* arXiv:2403.06988.
16. Tao, T. (2007). *What is Good Mathematics?* Bull. AMS. (paradigm-taxonomy precedent).
17. Mathematics Subject Classification 2020 (zbMATH / AMS). — gazetteer source for LFs.
18. Argilla / Prodigy documentation (2023-2025). — production HITL active-learning UIs.

Word count ~1180
