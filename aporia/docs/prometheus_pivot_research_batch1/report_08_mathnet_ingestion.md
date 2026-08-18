# Report 08 — MathNet Ingestion Architecture and Multi-Language Paradigm Extraction

**Author:** Research agent (Opus 4.7, 1M context)
**Date:** 2026-05-02
**Topic:** MathNet ingestion into `aporia/mathematics/questions.jsonl` with paradigm-tagged solution metadata
**Queue ref:** Mnemosyne REQ-002 in topic spec (note: `techne/queue/requests.jsonl` already binds REQ-002 to TOOL_ALEXANDER_POLYNOMIAL fulfilled 2026-04-22 — a fresh `REQ-MATHNET-001` should be opened to avoid id collision).

---

## 1. Situation

MathNet is the largest open corpus of proof-based olympiad mathematics ever assembled: 30,676 expert-authored problems with peer-reviewed multi-page solutions, drawn from 47 countries, 17 languages, 143 competitions, and roughly four decades (1985–2025). It was released 2026-04-20 by MIT CSAIL, KAUST Academy, and HUMAIN, and presented at ICLR 2026 in Brazil. Crucially for Prometheus, MathNet's solutions are *expert-written* (not crowd-sourced) and frequently present several distinct approaches per problem. That makes it the densest known source of *paradigm pairs* — same problem, different proof technique — which is exactly the substrate needed to populate Aporia's P01..P22 paradigm catalog with high-quality calibration anchors. Per `feedback_calibration_anchors_in_depth`, this corpus is load-bearing substrate infrastructure, not an optional dataset.

## 2. MathNet structure analysis

**Confirmed canonical artifacts** (verified 2026-04-28):

- **Landing page:** https://mathnet.mit.edu/ (MIT CSAIL)
- **Bulk download:** Hugging Face dataset `ShadenA/MathNet`, loadable via `datasets.load_dataset("ShadenA/MathNet", split="train")`
- **Code/loader:** https://github.com/ShadeAlsha/MathNet (ICLR 2026 reference impl)
- **Paper:** *MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval*, arXiv 2604.18584; OpenReview `zPvdG1Va5Q`
- **MIT News release:** https://news.mit.edu/2026/mit-scientists-build-worlds-largest-collection-olympiad-level-math-problems-open-0424

**License:** **CC BY 4.0** for problems where no explicit national copyright is asserted. Where a country/contest organization asserts its own copyright, that copyright is retained and takes precedence. CC BY 4.0 is acceptable for repository commit with an attribution NOTICE file (OSI does not certify content licenses, but CC BY 4.0 is the standard open-content choice). The country-asserted-copyright clause is the gating risk: we cannot blanket-commit raw problem text without auditing the per-country flag. Mitigation: store only problem **IDs + hashes + paradigm metadata** in-repo for the country-asserted set, and resolve full text on demand from the HF cache (mirrors how Prometheus handles heavy LMFDB tables).

**Schema (HF columns):**
- `problem_markdown` (str, LaTeX-rich)
- `solutions_markdown` (list[str], one entry per official approach, multi-page)
- `images` (list[PIL.Image]) — figures (multimodal subset)
- `topics`, `topics_flat` (list[str], hierarchical: e.g. `algebra/inequalities/AM-GM`)
- `language` (str, ISO label among the 17: English, Portuguese, Spanish, French, Italian, Serbian, Slovenian, German, Chinese, Romanian, Korean, Dutch, Russian, Mongolian, Macedonian, Polish, Hungarian)
- `country`, `competition`, `year` (provenance)

Distribution: 74% English, 26% non-English. Pipeline note from MIT: PDFs were OCR'd, segmented, normalized via GPT-4.1, then human-verified — so markdown is model-touched, not raw OCR (see Risks).

## 3. Ingestion architecture proposal

Recommended pipeline — six stages, each a separate Techne-callable script:

1. **`mathnet_fetch.py`** — `datasets.load_dataset("ShadenA/MathNet", split="train", cache_dir=Z:/datasets/mathnet/)`. Pin a snapshot revision SHA. Z: drive, not repo, per `feedback_two_machine_sync`.
2. **`mathnet_license_audit.py`** — for every row, classify into `{cc_by_4_0_clean, country_asserted, unknown}`. The `country_asserted` set goes to a shadow inventory and is **not** committed to repo; only its `MATHNET-` id and metadata stub are.
3. **`mathnet_to_canonical.py`** — emit one JSONL row per problem to `aporia/mathematics/questions.jsonl` extending the existing schema:
   ```json
   {"id": "MATHNET-00001", "domain": "mathematics", "subdomain": "<topics_flat[0]>",
    "statement": "<problem_markdown OR placeholder if country_asserted>",
    "status": "solved", "year_posed": <year>, "posed_by": "<competition>",
    "country": "<country>", "language": "<lang>",
    "sources": ["https://huggingface.co/datasets/ShadenA/MathNet#row=<i>"],
    "tags": [...topics_flat], "solutions_ref": "MATHNET-00001.sol.json",
    "license_class": "cc_by_4_0_clean|country_asserted",
    "paradigm_tags": ["P09","P11"], "paradigm_confidence": [0.92,0.71]}
   ```
4. **Multi-page solutions belong in sidecar files** under `aporia/mathematics/mathnet_solutions/MATHNET-XXXXX.sol.json` (list of solution objects, one per official approach, each with its own paradigm vector). Inlining into JSONL would balloon row sizes — typical solution is 2–10 KB, sometimes 50 KB with figures.
5. **`mathnet_paradigm_tag.py`** — see Section 4.
6. **Incremental ingest** — drive by HF revision diff. Maintain `aporia/mathematics/mathnet_state.json` with `{revision_sha, last_row_processed, paradigm_model_version}`. Re-tag triggers when `paradigm_model_version` bumps; re-ingest only when revision changes. MATHNET-ids are immutable; never recycle.

## 4. Multi-language paradigm extraction

26% of solutions are non-English across 16 languages. The P01..P22 paradigm catalog is defined in English. Three complementary strategies, deployed as an ensemble:

**(a) Translate-then-classify.** Use one multilingual MT model (NLLB-200 or Madlad-400; both Apache-2 / open weights) to translate non-English solutions to English, then run the existing English paradigm classifier. Trade-off: MT loses mathematical idiom (e.g., Russian olympiad shorthand for "AM-GM applied n−1 times"). Mitigation: regex-protect LaTeX blocks and translate only prose.

**(b) Multilingual LLM direct prompt.** Use a multilingual model (Qwen-3, Aya-23, Gemma-3) that natively reads the source language and returns the paradigm tag set directly. Trade-off: LLMs hallucinate paradigm labels, especially in lower-resource languages (Mongolian, Macedonian, Slovenian — together ~1–3% of MathNet but disproportionately interesting because under-represented in Western olympiad training data). Mitigation: require self-consistency between two independent multilingual models before accepting a high-confidence tag.

**(c) Weak supervision via cross-lingual alignment.** MathNet has many problems with both an English and a non-English official solution (IMO problems appear in many national booklets). Tag the English version with the existing classifier, then propagate the tag to the aligned non-English row. This generates a labeled multilingual training set for free, usable to fine-tune a small multilingual classifier (XLM-RoBERTa-large + paradigm head) that no longer needs translation. Per `feedback_replicate_seeds`, train across 5+ seeds before publishing.

**Ensemble decision rule:** A paradigm tag is committed to `paradigm_tags` only if (a)+(b) agree, OR if (c) backs it with cosine ≥ 0.85 against an English exemplar set. Disagreements go to `paradigm_tags_candidate` with confidences and surface in Aporia's review queue. Per `feedback_ai_to_ai_inflation`, two-AI agreement is *not* validation; cross-method agreement plus periodic human spot-check is.

## 5. Risks and anti-patterns

- **License creep.** The CC BY 4.0 / national-copyright split is the highest risk. Anti-pattern: blanket-committing raw problem text "because most are CC BY". Mitigation: `license_class` is mandatory; country-asserted text stays out of repo and is fetched on demand.
- **Multilingual paradigm hallucination.** LLMs invent plausible-sounding tags ("induction-on-degree") not in P01..P22. Constrain output to the closed catalog; reject anything else.
- **Olympiad clever-trick bias.** Olympiad problems reward closed-form, single-page-fits aesthetic solutions; Prometheus's substrate is built around long-horizon *open-conjecture* mode (BSD, abc, RH). Anti-pattern: letting MathNet's paradigm distribution dominate global priors. Mitigation: store MathNet paradigm counts on a separate corpus axis (`source: mathnet`) and never marginalize them into the prior used by aporia/charon for open conjectures.
- **Calibration drift.** OCR + GPT-4.1 normalization means MathNet markdown is *model-touched*. Treat as Tier-2 ground truth; do not use MathNet-derived paradigm exemplars to retrain a frontier model that then audits MathNet (training-eval leak).

## 6. Concrete next steps (this week, Mnemosyne)

1. Open `REQ-MATHNET-001` in `techne/queue/requests.jsonl` distinct from REQ-002; cite this report.
2. Implement `mathnet_fetch.py` and pin HF revision SHA (~2 h, low risk).
3. Implement `mathnet_license_audit.py` with country-asserted ruleset (~4 h — start with top-10 countries by row count).
4. Smoke-test `mathnet_to_canonical.py` on 100 English-only CC-BY rows; commit only those under a `MATHNET-TEST-` namespace before scaling.
5. Stand up paradigm-tagger paths (a) and (c) before (b); they cover ~74% of corpus on English alone with no LLM cost.
6. Datestamp all progress per `feedback_todo_hygiene`.

## 7. References

1. MIT News, *MIT scientists build the world's largest collection of Olympiad-level math problems* (2026-04-24). https://news.mit.edu/2026/mit-scientists-build-worlds-largest-collection-olympiad-level-math-problems-open-0424
2. MIT CSAIL release page (2026-04-20). https://www.csail.mit.edu/news/mit-researchers-build-worlds-largest-collection-olympiad-level-math-problems-and-open-it
3. MathNet landing page. https://mathnet.mit.edu/
4. Hugging Face dataset `ShadenA/MathNet`. https://huggingface.co/datasets/ShadenA/MathNet
5. Alsharif et al., *MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval*, ICLR 2026. arXiv:2604.18584. OpenReview `zPvdG1Va5Q`.
6. GitHub reference implementation. https://github.com/ShadeAlsha/MathNet
7. NLLB Team (Costa-jussà et al.), *No Language Left Behind: Scaling Human-Centered Machine Translation*, Meta AI 2022 — MT backbone for strategy (a).
8. Kudugunta et al., *MADLAD-400: A Multilingual And Document-Level Large Audited Dataset*, NeurIPS 2023 — alternative open MT corpus.
9. Conneau et al., *Unsupervised Cross-lingual Representation Learning at Scale (XLM-R)*, ACL 2020 — basis for the multilingual paradigm classifier in strategy (c).
10. Üstün et al., *Aya: An Open Multilingual Instruction-Tuned LLM*, Cohere for AI 2024 — direct multilingual LLM tagger candidate for strategy (b).
11. Ratner et al., *Snorkel: Rapid Training Data Creation with Weak Supervision*, VLDB 2017 — framework underlying strategy (c).
12. Creative Commons Attribution 4.0 International. https://creativecommons.org/licenses/by/4.0/
13. Prometheus internal: `F:\Prometheus\aporia\mathematics\paradigm_gap_v2.json` — current P01..P22 catalog distribution; baseline for tagger consistency tests.
14. Prometheus internal feedback memos: `feedback_calibration_anchors_in_depth.md`, `feedback_ai_to_ai_inflation.md`, `feedback_replicate_seeds.md`, `feedback_narrative_resistance.md`, `feedback_two_machine_sync.md`, `feedback_todo_hygiene.md` — guardrails applied throughout this design.

---

**Key findings:** (i) MathNet is on HuggingFace at `ShadenA/MathNet`, license CC BY 4.0 with national-copyright override clause, schema confirmed; (ii) recommended architecture stores problems in extended `questions.jsonl` with sidecar solution files and a `license_class` gate; (iii) 17-language paradigm extraction should ensemble translate-then-classify + multilingual LLM + cross-lingual weak supervision rather than rely on any single approach; (iv) the topic-spec REQ-002 collides with an already-fulfilled queue id and should be re-opened as `REQ-MATHNET-001`. The largest risk is the per-country copyright split, which dictates a no-blanket-commit policy on raw text.
