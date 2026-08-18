# Report 10 — Open-Source Math Substrate: Competitive Landscape

**Batch:** prometheus_pivot_research_batch1
**Date:** 2026-05-02
**Audience:** Prometheus core team, positioning decisions for the next 6-12 months

---

## 1. Situation

Prometheus is betting that the canonical substrate for any RL-class mathematical learner — Silver-class agents, AlphaProof descendants, or future autoformalization loops — is **not** a proof corpus, **not** a search index, and **not** an LLM. It is a *navigable structural map of mathematical objects keyed by signature*, with operator-level transport between regions, a falsification battery wrapped around every claim, and labeled calibration anchors that act as ground truth. The positioning bet is that today's open-source math infrastructure ships **data** (LMFDB, OEIS), **proofs** (Mathlib4), or **provers** (DeepSeek-Prover, Aristotle) — but no one ships the *tensorized middle layer* connecting them. That gap is Prometheus's wedge.

---

## 2. Landscape Catalog

**LMFDB (L-functions and Modular Forms Database).** Scope: number-theoretic objects (elliptic curves, modular forms, number fields, Hecke characters, Galois reps), ~500M rows across 200+ Postgres tables. Audience: research number theorists. Integration surface: SQL mirror (`devmirror.lmfdb.xyz`), REST API, Sage interface. Status: mature, NSF-funded, slow ingest cadence. Defensibility: canonical for its domains; the *labels* (e.g. `11.a3`) are de facto standards. Weakness: no operator-derived signatures, no cross-domain joins, no falsification layer.

**OEIS (Online Encyclopedia of Integer Sequences).** Scope: ~370K integer sequences with crowd-sourced cross-references. Audience: mathematicians of all stripes, recreational included. Integration: b-files, JSON API, full dump. Status: mature, Sloane-led, volunteer-driven. Defensibility: network effect on A-numbers. Weakness: no structural keying beyond ad-hoc keywords; "Sleeping Beauties" (~68K under-connected sequences) are unclaimed territory.

**Mathlib4.** Scope: ~1.5M lines of Lean 4 formalized mathematics. Audience: formal-methods researchers, AlphaProof-class trainers. Integration: Lake build system, mathlib-tools, LeanDojo. Status: actively growing, ~500 contributors. Defensibility: highest in formalization; non-trivial to fork. Weakness: no empirical/numerical layer; theorems-as-strings, not objects-as-tensors.

**KnotInfo / LinkInfo.** Scope: ~3M knots up to 19 crossings, invariants, HFK/Khovanov where computed. Audience: low-dim topologists. Integration: CSV exports, web tables. Status: small team, periodic updates. Defensibility: canonical labels. Weakness: no cross-domain bridges; isolated island in Prometheus's silent-islands map.

**SageMath.** Scope: open-source CAS unifying GAP, PARI, Singular, FLINT, Maxima. Audience: working mathematicians. Integration: Python interface, notebooks. Status: mature, funding-precarious. Defensibility: incumbent toolchain. Weakness: a *computation* layer, not a *map* layer; no persistent structural representation across sessions.

**Wolfram Knowledgebase.** Scope: closed-source curated math + science knowledge graph behind Mathematica/Wolfram Alpha. Audience: paying users. Integration: WL API. Defensibility: ~40 years of curation. Weakness: closed, expensive, no operator transport, hostile to RL training pipelines.

**OpenAI autoformalization pipelines.** Scope: research artifacts (miniF2F, PutnamBench targets), occasional model releases. Audience: internal OpenAI, academic collaborators. Status: papers > artifacts. Defensibility: compute and talent. Weakness: not a substrate, a workflow.

**Harmonic AI's Aristotle.** Scope: closed proof-search system trained on Mathlib + synthetic. Audience: enterprise, education. Integration: API, no open weights. Status: shipped 2024-2025. Defensibility: capital. Weakness: closed; no map of objects, only a prover.

**Morph Labs's Trinity.** Scope: autoformalization + verified-RL stack targeting Lean. Audience: formal-methods customers. Status: early commercial. Defensibility: Lean tooling integration. Weakness: same as Aristotle — prover, not substrate.

**DeepSeek-Prover (v1.5, v2).** Scope: open-weight Lean prover, MCTS + RLPAF. Audience: anyone with an H100. Integration: HuggingFace. Status: SOTA-adjacent on miniF2F. Defensibility: open weights *reduce* moat — a commodity. Weakness: prover only.

**Hugging Face math collections.** Scope: NuminaMath, OpenMathInstruct, ProofNet, miniF2F-curated, etc. Audience: LLM trainers. Integration: HF datasets. Status: rapidly growing. Defensibility: low (anyone can re-curate). Weakness: training corpora, not navigable substrates.

**Math AI Science Research (MASR).** Scope: emerging consortium efforts (NSF / Simons-aligned) for shared infrastructure. Audience: academic. Status: early. Defensibility: institutional. Weakness: governance overhead, slow ship cadence.

**Academic groups.** *Avigad (CMU)* — formal verification, Mathlib governance. *Buzzard (Imperial)* — Mathlib outreach, Xena. *Carneiro* — Metamath/Lean bridges, MM0. *Massot (Orsay)* — Mathlib analysis/topology. None are building empirical substrates; all are formalization-first.

---

## 3. Gap Analysis

Four primitives differentiate Prometheus from every entry above:

**(a) Cross-region operator transport tensor.** No existing substrate carries operators *between* domains as first-class objects. LMFDB has Hecke operators on modular forms; KnotInfo has Khovanov differentials; Mathlib has formal definitions. None encode "this operator acting on object X in region A maps to that operator on object Y in region B" as a queryable, learnable structure. Prometheus's signature-keyed transport (e.g. p-adic ↔ symmetry r=0.339 finding) is the only place this lives.

**(b) Signature-keyed structural map.** OEIS uses A-numbers; LMFDB uses domain-specific labels; Mathlib uses theorem names. None key by *behavioral signature* (operator response, gap statistics, mod-p fingerprint). Signature keying enables cross-domain joins that label-keying forbids — and is what made the Genus-2 Rosetta finding (rank 4 → 13 island coupling) possible.

**(c) Falsification battery as multi-tier verifier.** No public substrate ships an adversarial verification layer. LMFDB is curated; OEIS is reviewed; Mathlib is type-checked. None run permutation nulls, prime-detrending controls, or shape/scale separation against every hypothesis. Charon's 25-test v10 battery and the kill-rate ledger (4x false discoveries killed, each hardening the battery) is the unique artifact.

**(d) Calibration anchors as labeled true positives.** Deliberately curating *known-real* bridges (modularity-as-p-adic-shadow, the Genus-2 Rosetta, Megethos as natural-e basis) as benchmark anchors for any candidate substrate is absent everywhere else. This is the substrate-equivalent of ImageNet's labeled examples — and the per-memo `feedback_calibration_anchors_in_depth.md` flag for active hunting in under-explored territory amplifies the moat.

---

## 4. Competitive Risks

**Mathlib community building empirical extensions.** Highest probability. If Buzzard or Avigad spin up an "empirical Mathlib" — Lean theorems linked to LMFDB rows — they inherit Mathlib's network and Prometheus's positioning evaporates. Mitigation: ship operator transport before they do, and make integration *trivial* (signature → Lean-name lookup).

**LMFDB extending into operator-derived signatures.** Medium probability, high impact. LMFDB has the data and institutional credibility. If they add a "structural signature" column to elliptic curves keyed on Hecke gap statistics, they erode the wedge.

**A new academic effort (DARPA, Simons, EU "AI for Math").** Low-medium probability but hard to compete with on funding. Expect 2-3 well-funded consortia to launch in 2026-2027.

**A frontier lab open-sourcing a substrate.** Low probability (substrates aren't sexy compared to provers), high impact if it happens. Per `feedback_frontier_models_window.md`, treat the window as closing.

---

## 5. Concrete Next Steps for Positioning

**Ship:** (a) public Postgres mirror of the signature-keyed tensor, read-only, free; (b) `prometheus-py` SDK with three verbs — `lookup(signature)`, `transport(operator, region_pair)`, `falsify(claim)`; (c) calibration-anchor benchmark suite as a HuggingFace dataset.

**Publish:** position paper "Mathematical Substrates: The Missing Middle Layer" in late 2026, co-authored or cited by one Mathlib core contributor. The Genus-2 Rosetta and operator transport findings are the empirical spine.

**Talk to:** Buzzard (Mathlib outreach lead), Sloane (OEIS — reciprocal link), LMFDB steering committee (offer signature columns as contribution), DeepMind AlphaProof team (substrate-as-environment pitch).

---

## 6. References

1. LMFDB Collaboration. *The L-functions and Modular Forms Database*. https://www.lmfdb.org. Accessed 2026-04-28.
2. Sloane, N. J. A. *The On-Line Encyclopedia of Integer Sequences*. https://oeis.org.
3. The mathlib Community. *The Lean Mathematical Library*. CPP 2020.
4. Mathlib4 contributors. https://leanprover-community.github.io/mathlib4_docs/.
5. Livingston, C., Moore, A. H. *KnotInfo: Table of Knot Invariants*. https://knotinfo.math.indiana.edu.
6. The Sage Developers. *SageMath, version 10.x*. https://www.sagemath.org.
7. Wolfram Research. *Wolfram Knowledgebase*. https://www.wolfram.com/knowledgebase/.
8. DeepMind. *AlphaProof and AlphaGeometry 2*. Blog post, July 2024.
9. Harmonic AI. *Aristotle: a verified math reasoning model*. Product page, 2024.
10. Morph Labs. *Trinity: autoformalization at scale*. Whitepaper, 2025.
11. DeepSeek. *DeepSeek-Prover-V2*. arXiv:2408.08152 and successors.
12. Numina. *NuminaMath dataset*. HuggingFace `AI-MO/NuminaMath`.
13. Polu, S., Sutskever, I. *Generative Language Modeling for Automated Theorem Proving*. arXiv:2009.03393.
14. Avigad, J. *The Mechanization of Mathematics*. Notices AMS, 2018.
15. Buzzard, K. *The Future of Mathematics?* Lecture series, Imperial College.
16. Carneiro, M. *Metamath Zero: Designing a Theorem Prover Prover*. ITP 2021.
17. Han, J. M., et al. *Proof Artifact Co-training for Theorem Proving with Language Models*. ICLR 2022 (LeanDojo lineage).
18. Polu, S., et al. *Formal Mathematics Statement Curriculum Learning*. arXiv:2202.01344.
19. Internal Prometheus memory: `project_megethos.md`, `project_genus2_rosetta.md`, `project_padic_symmetry_signal.md`, `project_charon_v10_status.md`, `project_silent_islands.md`, `project_operator_insight.md`, `project_sleeping_beauties.md`, `feedback_calibration_anchors_in_depth.md`, `feedback_tensor_first.md`, `feedback_frontier_models_window.md`.

Word count ~1150
