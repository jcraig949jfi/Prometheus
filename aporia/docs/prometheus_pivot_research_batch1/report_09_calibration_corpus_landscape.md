# Report 09 — Calibration Corpus Landscape (LeanDojo, miniF2F, ProofNet, FrontierMath, PutnamBench, NaturalProofs, …)

**Batch:** prometheus_pivot_research_batch1
**Date:** 2026-05-02
**Companion to:** `F:\Prometheus\aporia\calibration\battery_calibration.jsonl`, `F:\Prometheus\techne\queue\requests.jsonl` REQ-001 (Bloom-Erdős), REQ-002 (MathNet), `feedback_calibration_anchors_in_depth.md`
**Drafted by:** Aporia (sub-agent research brief)

---

## 1. Situation

Today `aporia/calibration/battery_calibration.jsonl` contains **N=2** anchors (CAL-2026-04-26-001, the Tao/Lichtman primitive-sets transfer, and CAL-2026-04-26-002, its narrative-inflation negative). The Silver-thesis pivot demands a **100× scale-up** so the falsification battery can be evaluated against a meaningful population of true positives, true negatives, and gray-zone claims rather than two anecdotes. Bloom-Erdős (REQ-001) supplies ≈800 curated open/solved problems with curator-grade verdicts; MathNet (REQ-002) supplies multilingual proof-paradigm signal. Beyond those, the field already curates *several* corpora that are formally verified, machine-checkable, or expert-graded — exactly the substrate Prometheus needs to score itself. Adding them would (a) move calibration density from N=2 → N≈10⁵ statements, (b) replace expert-judgment labels with **machine-verified ground truth** for a non-trivial slice, and (c) cover regions (Olympiad, undergraduate, contemporary research, natural-language theorem-statement pairs) the Bloom catalog deliberately excludes.

## 2. Corpora catalog with details

### 2a. Formally verified (gold standard for true-positive labels)

**LeanDojo / Mathlib4.** Mathlib is the community Lean 4 mathematics library (≈180k theorems, Apache 2.0, growing weekly). LeanDojo (Yang et al., NeurIPS 2023) wraps it into a retrieval-aware extraction (`lean-dojo/LeanDojo` repo): every theorem ships with a fully type-checked proof, premise dependencies, tactic-level proof states, and a proof tree. Calibration value: **maximally high** — every entry is a verified true positive *with a verified derivation graph*. License: Apache 2.0 (Mathlib) + MIT (LeanDojo tooling); commercial use OK with attribution. Schema: `Theorem(name, statement, proof, premises[], file, commit, tactic_trace[])`. Complements: provides the operator-level verb signature Prometheus needs to test paradigm tags against ground-truth tactic sequences.

**miniF2F.** 488 olympiad-and-undergraduate problems formalized in **Lean, Isabelle, HOL Light, and Metamath** (Zheng, Han, Polu, ICLR 2022; v2 maintained by OpenAI / Meta forks). Train/valid/test split, AMC/AIME/IMO/MATH sources. License: MIT. Calibration value: high — the same problem in 4 provers gives **cross-system consistency anchors** (rare and load-bearing). Schema: per-prover `.lean / .thy / .ml / .mm` files plus a metadata index. Complements LeanDojo by being prover-agnostic and competition-flavored.

**ProofNet.** 371 undergraduate-textbook problems (Munkres, Rudin, Artin, Dummit-Foote, Axler, Pugh) with Lean 4 statements + natural-language pairs (Azerbayev et al., 2023). License: MIT. Schema: `(nl_statement, nl_proof, formal_statement, formal_proof_partial, source_book, chapter)`. Calibration value: medium-high — covers the **undergraduate band** that miniF2F (olympiad) and FrontierMath (research) both skip; precisely the band where Prometheus's substrate is currently thin.

**PutnamBench.** ≈640 William Lowell Putnam Competition problems (1962–2023) formalized in Lean 4, Coq, and Isabelle (Tsoukalas et al., NeurIPS 2024). License: Apache 2.0. Schema: per-prover formalizations + original NL statement + answer. Calibration value: high — short, hard, *answer-checkable* problems give clean true/false labels even for non-formal substrates.

### 2b. Expert-graded (high-confidence labels, unverified-by-machine)

**FrontierMath.** Epoch AI's contemporary-research benchmark (Glazer et al., 2024). ~300 problems authored by working mathematicians (Tao, Gowers and others publicly endorsed); answers are checkable but proofs are not released. License: **gated** — Epoch withholds the test set to prevent contamination; partial public sample only. Calibration value: very high *per row*, but ingest cost is high and redistribution forbidden. Schema: `(problem, numerical_or_symbolic_answer, domain_tag, difficulty)`.

**OlympiadBench.** ≈8k bilingual (Chinese + English) olympiad problems with step-level expert solutions (He et al., ACL 2024). License: Apache 2.0. Schema: multimodal-aware (some include diagrams). Calibration value: medium — labels are expert-graded but not machine-verified; large enough to support stratified sampling.

**TheoremQA.** 800 STEM theorem-application questions across math/physics/EE/finance (Chen et al., EMNLP 2023). License: MIT. Schema: `(question, answer, theorem_used, theorem_category)`. Calibration value: medium — the explicit `theorem_used` field is unusually useful for paradigm-tag supervision.

### 2c. Theorem-statement pairs (NL anchors for representation tests)

**NaturalProofs.** ~32k theorem-proof pairs scraped from ProofWiki, Stacks Project, and Mathlib (Welleck et al., NeurIPS 2021 D&B). License: MIT (code) + upstream licenses (CC-BY-SA for ProofWiki, MIT for Stacks). Schema: `(statement, proof_NL, references[], category)`. Calibration value: medium — large NL corpus, no machine verification, but the **reference graph** is itself a calibration substrate (mirrors what Prometheus is building).

### 2d. Reasoning benchmarks (broad-but-shallow)

**GSM8K** (8.5k grade-school word problems, MIT license, OpenAI 2021) and **MATH** (12.5k competition problems, MIT, Hendrycks et al. 2021). Calibration value per row is low (most are trivial or memorized) but they are the de facto industry baselines — useful as a **floor sanity check** that Prometheus isn't worse than a 2021 LLM at arithmetic.

### 2e. Pretrain corpora (different role — *scale, not anchors*)

**OpenWebMath** (14.7B tokens, ODC-By, Paster et al., ICLR 2024) and **MathPile** (9.5B tokens, CC-BY-SA-NC, Wang et al., NeurIPS 2024 D&B). These are **not** calibration sets — they are the noisy ocean from which calibration is *distinct*. Listed for completeness so they aren't accidentally treated as anchors. Per `feedback_weak_signals_are_threads.md`, these belong on the exploration track and must be firewalled from the calibration track.

## 3. Priority ranking for Prometheus ingest

Ranked by composite of (a) calibration value per row, (b) license compatibility, (c) integration cost, (d) coverage of substrate-thin regions.

1. **miniF2F** — 488 rows, MIT, 4-prover cross-anchors, structured filesystem layout, ingest cost ≈ ½ day. Highest information-per-dollar; covers olympiad band Prometheus has zero anchors in. **Ingest first.**
2. **PutnamBench** — 640 rows, Apache 2.0, multi-prover, answer-checkable. Marginal effort over miniF2F because the schema is similar; doubles olympiad-band coverage and adds the clean "numerical answer" labels Prometheus can grade without a prover loop.
3. **ProofNet** — 371 rows, MIT, fills the undergraduate gap that the previous two skip. Pairs NL with Lean 4 statements — directly trains Prometheus's NL→signature extractor. Ingest cost ≈ ½ day.
4. **LeanDojo / Mathlib4** — 180k rows, Apache 2.0. Largest verified corpus on Earth; cost is non-trivial (50 GB after extraction, premise-graph build is multi-hour) but every row is gold. Stage as REQ-006; index incrementally. *Defer raw-statement ingestion until 1–3 are operational so we don't drown the battery in mass before the schema is right.*
5. **NaturalProofs** — 32k rows, MIT. Adds the ProofWiki / Stacks reference graph as a second corroboration source for paradigm tags inferred from Bloom + MathNet. Lower per-row value but high graph-structure value.

**Below the cut (rationale):** FrontierMath (gated; pursue via collaboration request to Epoch, not unilateral ingest); OlympiadBench (overlaps PutnamBench / miniF2F coverage; revisit if multilingual signal becomes load-bearing); TheoremQA (small; use as a held-out paradigm-supervision validation set, not a primary anchor); GSM8K + MATH (industry-floor sanity only); OpenWebMath / MathPile (pretrain track, *not* calibration — explicit firewall per feedback file).

## 4. Risks / overlap analysis

**Overlap.** Mathlib appears verbatim inside LeanDojo, partially inside miniF2F-Lean, and is *referenced* by ProofNet and NaturalProofs. Deduplication must be on (theorem-statement-hash, prover) tuples or the same theorem will be counted up to four times and inflate calibration density artificially — a direct echo of `feedback_ai_to_ai_inflation.md` but at the corpus level. PutnamBench and miniF2F share AMC / AIME problems; intersection is small (~30) but real. OlympiadBench and miniF2F share IMO problems.

**License complications.** FrontierMath is gated and **not redistributable**; treat as remote-eval only. MathPile is CC-BY-SA-NC — non-commercial; bars use in any monetized derivative. ProofWiki content inside NaturalProofs is CC-BY-SA — share-alike obligation propagates to any republished derivative. Mathlib's Apache-2.0 is the cleanest. Document each anchor's license in the JSONL `license` field at ingest time; the falsification battery should refuse to surface anchors whose license forbids the surfacing context.

**Contamination risk.** Several of these corpora are in the training data of every frontier model. For Prometheus's *self-evaluation* this is fine (we are not training on labels), but for *frontier-critique blind trials* (`feedback_frontier_models_window.md`) we must hold out a contamination-free slice — the FrontierMath private set and any post-2024 Mathlib commits are the obvious candidates.

## 5. Concrete next steps for Mnemosyne

After REQ-001 (Bloom-Erdős) and REQ-002 (MathNet) land:

- **REQ-003 — miniF2F ingest.** Clone `openai/miniF2F`, parse Lean / Isabelle / HOL / Metamath statements, emit to `aporia/calibration/minif2f.jsonl` with `label="true_positive"`, `label_source="machine_verified_lean4"`, `prover_cross_check=[…]`.
- **REQ-004 — PutnamBench ingest.** Clone `trishullab/PutnamBench`, same schema, with `answer_checkable=true` flag.
- **REQ-005 — ProofNet ingest.** Clone `zhangir-azerbayev/ProofNet`, preserve `(nl, formal)` pairs.
- **REQ-006 — LeanDojo extraction.** Run LeanDojo's tracer against a pinned Mathlib4 commit; emit theorem-and-premise-graph; stage in `aporia/mirrors/mathlib/`.
- **REQ-007 — Frontier-eval gateway.** Open dialogue with Epoch AI for a held-out FrontierMath access channel.

Cross-corpus dedupe pass (`aporia/scripts/calibration_dedupe.py`) runs after each ingest; license registry (`aporia/calibration/license_index.json`) gates downstream use. Target: **N ≥ 10⁵ verified anchors by end of pivot Phase 1**.

## 6. References

1. Yang, K. et al. *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models.* NeurIPS 2023. https://leandojo.org , https://github.com/lean-dojo/LeanDojo
2. The mathlib Community. *The Lean Mathematical Library.* CPP 2020. https://leanprover-community.github.io/mathlib4_docs/
3. Zheng, K., Han, J. M., Polu, S. *miniF2F: a cross-system benchmark for formal Olympiad-level mathematics.* ICLR 2022. https://github.com/openai/miniF2F
4. Azerbayev, Z. et al. *ProofNet: Autoformalizing and Formally Proving Undergraduate-Level Mathematics.* arXiv:2302.12433. https://github.com/zhangir-azerbayev/ProofNet
5. Tsoukalas, G. et al. *PutnamBench: Evaluating Neural Theorem-Provers on the Putnam Mathematical Competition.* NeurIPS 2024 D&B. https://github.com/trishullab/PutnamBench
6. Glazer, E. et al. *FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI.* Epoch AI Technical Report, 2024. https://epoch.ai/frontiermath
7. Welleck, S. et al. *NaturalProofs: Mathematical Theorem Proving in Natural Language.* NeurIPS 2021 D&B. https://github.com/wellecks/naturalproofs
8. Cobbe, K. et al. *Training Verifiers to Solve Math Word Problems (GSM8K).* arXiv:2110.14168.
9. Hendrycks, D. et al. *Measuring Mathematical Problem Solving with the MATH Dataset.* NeurIPS 2021 D&B. https://github.com/hendrycks/math
10. Paster, K. et al. *OpenWebMath: An Open Dataset of High-Quality Mathematical Web Text.* ICLR 2024. https://huggingface.co/datasets/open-web-math/open-web-math
11. Wang, Z. et al. *MathPile: A Billion-Token-Scale Pretraining Corpus for Math.* NeurIPS 2024 D&B. https://huggingface.co/datasets/GAIR/MathPile
12. Chen, W. et al. *TheoremQA: A Theorem-driven Question Answering Dataset.* EMNLP 2023. https://github.com/wenhuchen/TheoremQA
13. He, C. et al. *OlympiadBench: A Challenging Benchmark for Promoting AGI with Olympiad-Level Bilingual Multimodal Scientific Problems.* ACL 2024. https://github.com/OpenBMB/OlympiadBench
14. Polu, S., Sutskever, I. *Generative Language Modeling for Automated Theorem Proving.* arXiv:2009.03393. (Context for miniF2F's GPT-f lineage.)
15. The ProofWiki Community. *ProofWiki.* https://proofwiki.org — CC-BY-SA upstream of NaturalProofs.

Word count ≈1180
