# Gemini Deep Research Prompt Deck — 2026-05-10

**20 prompts, 7 waves, fire 3 at a time in order.** After each return, save Gemini's report to:
`aporia/docs/gemini_research_2026-05/<slug>.md`

**Common framing** (already inlined in each prompt; do not need to re-add):
- Project Prometheus context — multi-agent mathematical research substrate, no paper-publishing framing, primary-source-anchored, dated/attributed claims.
- Format requirements per prompt are inline.

---

## Wave 1 — Anti-anchor verification

### Prompt 1: Verify anti-anchors AA-001 through AA-004

```
Project Prometheus is a multi-agent mathematical research substrate. We've registered 10 anti-anchors — pinned false claims that LLM training data tends to fabricate. Before these enter our v1.0 Learner training corpus, each must be verified against primary literature.

Verify the following four anti-anchors. For each: (a) confirm the canonical primary source and quote the relevant theorem/result, (b) check for follow-on work 2024-2026 that supersedes or refines the claim, (c) check whether the "false form" is being repeated in recent literature (which would confirm the anti-anchor is needed), (d) flag if the "true form" has any qualifications missed.

AA-001 PATTERN_GCT_OCCURRENCE_DEAD
- False form: "Bürgisser-Ikenmeyer-Panova killed GCT"
- True form: "BIP killed *occurrence* obstructions for det/padded-perm specifically; multiplicity, vanishing-ideal, outside-orbit, and equivariant obstructions remain."
- Citation: arXiv:1604.06431 (BIP 2019 J. AMS)

AA-002 ZAUNER_FALSE_ANCHOR
- False form: "Zauner SIC-POVMs proved in 2025"
- True form: "AFK 2025 (arXiv:2501.03970) is conditional on Stark conjectures + Shintani-Faddeev modularity"
- Citation: arXiv:2501.03970

AA-003 HILLAR_LIM_CLOSED
- False form: "Hillar-Lim symmetric-rank-over-ℚ is open"
- True form: "Symmetric-rank-over-ℚ is settled by Shitov 2016. Tensor-rank NP-hardness over ℝ remains as Hillar-Lim's main result."
- Citation: arXiv:1605.07532

AA-004 SAXL_CLOSED
- False form: "Saxl conjecture is open"
- True form: "Saxl conjecture solved unconditionally by Sellke 2025/26"
- Citation: arXiv:2512.15035

Output format per anti-anchor: 1-paragraph confirmation, primary-source quotes (exact theorem statements where possible), 2024-2026 follow-on work, status confirmation or refinement. Final section: recommendations on rewording, new sub-anchors discovered, follow-on work to track.

Length: 2000-3000 words total. Style: terse, primary-source-anchored, no paper framing, no rhetorical hedges. Date everything.
```

### Prompt 2: Verify anti-anchors AA-005 through AA-007

```
[Project Prometheus context — same as Prompt 1.]

Verify three anti-anchors regarding recent specific results.

AA-005 CACTUS_BARRIER
- Claim: For m × m × m tensors, the cactus barrier 6m − 4 is a structural ceiling — determinantal/rank-method lower bounds on R̄(M⟨m⟩) cannot exceed 6m − 4.
- Citation: Buczyński Feb 2026 arXiv:2602.11309
- Verify: (a) the exact statement of the bound, (b) whether it applies to all "rank-method" equations or only specific subclasses, (c) any earlier cactus-rank dimension counts that imply this barrier (Galązka-Mańdziuk-Rupniewski 2023 arXiv:2007.16203 may be relevant).

AA-006 LUCCA_ATTRIBUTION
- Claim: Conjecture 16 of arXiv:2603.29571 (Randomstrasse101: Open Problems of 2025) is proposed by Kevin Lucca, not Bandeira-Dmitriev jointly. Five document authors: Bandeira, Dmitriev, Lucca, Nizić-Nikolac, Rödder.
- Verify: (a) the proposer field of Conjecture 16 in the arXiv version, (b) whether secondary sources have miscited the proposer, (c) Lucca's other publications to confirm authorship pattern.

AA-007 TENSOR_TYPE_2_NOT_LOG_D
- Claim: Tensor type-2 constant scales like d^{1/2 − 1/p} polylog for tensors of order r ≥ 3, NOT √log d (which is matrix only). Conjecture 16 of arXiv:2603.29571 is the conjectural form.
- Citations: arXiv:2603.29571 (Conjecture 16); arXiv:2411.10633 (BGJLR STOC 2025, partial resolution for p ≥ 2r); arXiv:2108.06312 (BBvH Inventiones 2024, matrix sharp).
- Verify: (a) the gap exponent in the open p < 2r regime, (b) whether the volumetric barrier is proved or merely "currently observed," (c) any alternative bounds (generic chaining, PAC-Bayesian) that would beat BGJLR's exponent.

Output: per anti-anchor, primary-source quotes + follow-on survey + recommendations. Length 2000-3000 words. No paper framing.
```

### Prompt 3: Verify anti-anchors AA-008 through AA-010

```
[Project Prometheus context — same as Prompt 1.]

Verify three structural anti-anchors.

AA-008 EQUIVARIANT_NOT_UNRESTRICTED
- Claim: Landsberg-Ressayre 2017 exponential lower bound on dc(perm_n) under symmetry restriction is NOT a lower bound on unrestricted dc(perm_n). The (S_n × S_n) ⋊ Z/2 equivariance restriction is essential.
- Citation: arXiv:1508.05788
- Verify: (a) the exact restriction (does it match the ITCS 2016 vs arXiv version?), (b) any partial extensions to less-restricted models 2018-2026, (c) whether the unrestricted dc lower bound has improved past Mignon-Ressayre n²/2 (2004).

AA-009 BORDER_CACTUS_FIFTH_RANK
- Claim: Border cactus rank cr̄ is a distinct fifth rank invariant alongside (R, R̄, sr, cr). Substrate must track 5+ rank coordinates per symmetric tensor.
- Citation: Buczyńska-Buczyński Jan 2026 arXiv:2601.19558
- Verify: (a) the exact definition of cr̄ vs cr, (b) explicit examples where cr̄ ≠ cr or cr̄ ≠ R̄, (c) whether the literature contains any examples of substrate-style-collapsing notation that should be flagged.

AA-010 FIVE_APPLICATION_CONVERGENCE
- Claim: The tensor type-2 constant has unusual five-application convergence: (a) coding theory LDC lower bounds, (b) dispersive PDE Strichartz estimates, (c) tensor PCA SoS hardness, (d) Banach-space type-2 geometry, (e) Gaussian process supremum control.
- Source: arXiv:2603.29571 (Lucca enumerates these in the discussion of Conjecture 16)
- Verify: (a) confirm the five applications are explicit in Lucca's enumeration, (b) check whether other applications exist that should expand the list, (c) flag if any one application has a tighter conjectured bound that diverges from the unified Conjecture-16 form.

Output: per anti-anchor, primary-source quotes + follow-on survey + recommendations. Length 2000-3000 words. No paper framing.
```

---

## Wave 2 — Tensor catalog continuation

### Prompt 4: Border-rank cluster — T#5, T#6, T#20

```
Project Prometheus is doing deep research on tensor open problems for a substrate-grade catalog. We did 18 priority entries already (T#1, T#13, T#19, T#22, T#26, T#28, T#34, T#40, T#43, T#56, T#58, T#72, T#73, T#79, T#84, T#85, T#92, T#95). This is the next batch of 3.

Produce ONE substrate-grade report PER ENTRY. Each report must follow this 7-section format:
1. Brief summary (1 paragraph)
2. Flagged findings (5-8 bullets surfacing anything non-obvious)
3. Problem statement (formal)
4. Status & bounds (table form, dated)
5. Literature (primary sources, arXiv IDs, 2024-2026 frontier)
6. Attack vectors active in the literature (paradigms, sub-tactics)
7. Cross-references (other catalog entries, prior reports)

Each report: 2000-3500 words. Cite ≥2 of: PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK. Use "structural region" language, not bridge-narrative framing. No paper framing.

Entries to cover:

T#5: Border rank of the matrix multiplication tensor M⟨n⟩ — current best lower bounds (Conner-Harper-Landsberg 2023 had R̄(M⟨3⟩) ≥ 17; what's the current state for n = 3, 4, 5?). How does the cactus barrier 6m − 4 (Buczyński Feb 2026) constrain this?

T#6: Border-rank additivity (Strassen's additivity conjecture for border rank) — known counterexamples (Schönhage 1981 for tensor rank), border-rank version status, recent submultiplicativity / superadditivity results 2024-2026.

T#20: Minimal border rank tensors / border Comon's conjecture — does R̄(T) = R̄_S(T) for symmetric T? What's the current evidence pro/con? Connect to T#34 (border-rank membership) and T#19 (cactus rank) substrate work.

Output: 3 reports, each self-contained. ~7000-10000 words total.
```

### Prompt 5: Additivity + operator-norm cluster — T#23, T#24, T#71

```
[Project Prometheus context — same 7-section format as Prompt 4.]

Three entries on tensor additivity and norms:

T#23: Strassen's additivity conjecture for tensor rank — R(T_1 ⊕ T_2) = R(T_1) + R(T_2)? Schönhage's 1981 counterexample for direct sums of disjoint matrix-mult tensors is the canonical no; recent refinements (Shitov 2017 for symmetric tensors via tensor rank over ℚ; Landsberg 2019 etc.) — current status of additivity-modulo-precise-formulations 2024-2026.

T#24: Operator norm of random tensors — special case p = 2 of the type-2 constant problem (T#72 sister). Survey current best bounds for E ‖Σ g_i T_i‖_op when T_i have order r ≥ 3. Coverage of Boedihardjo arXiv:2412.21193 (independent entries), BGJLR 2024 (deterministic with Gaussian weights), and any 2025-2026 follow-ups.

T#71: Log-factor elimination in matrix concentration — a known sister problem to T#72. Tomczak-Jaegermann / Ahlswede-Winter give √log d for matrices; Bandeira-Boedihardjo-van Handel 2024 Inventiones gets sharp bound via free probability for r = 2. Question: can the log factor be eliminated for tensors of order r ≥ 3, even in restricted regimes? Connect to T#72.

Output: 3 reports, each self-contained, 2000-3500 words each. Same pattern citations + format requirements as Prompt 4. No paper framing.
```

### Prompt 6: Permanent + orbit closure — T#86, T#93, T#21

```
[Project Prometheus context — same 7-section format as Prompt 4.]

Three entries on permanent / orbit-closure / generic-stratum geometry:

T#86: Tensor rank of det vs perm — Glynn's R(perm_n) ≤ 2^{n−1}; recent improvements 2024-2026; Houston-Goucher-Johnston 2024 Bell-number formula for det (arXiv:2301.06586) — does an analogue exist for perm? (Catalog batch report T#22 found NO such analogue exists; cross-validate.) Current best bounds for R(det_n) and R(perm_n) at n = 3, 4, 5.

T#93: Orbit closure containment for polynomials — when is f ∈ \overline{GL · g}? GIT / Hilbert-Mumford / sequence-degeneration techniques. Connect to T#92 (GCT for det/padded-perm) and T#79 (SLOCC orbit classification). Recent 2024-2026 work on algorithmic decision of orbit closure containment.

T#21: Alexander-Hirschowitz stratification of generic Waring rank — A-H 1995 closed the generic case; survey defective stratum (where R_W < generic) 2024-2026. Connect to T#26 (Segre-Veronese defectivity, ABGO 2024 closed for d_i ≥ 3) and T#22 (Waring rank of permanent — perm_3 = 16 vs generic ≈ 19).

Output: 3 reports, 2000-3500 words each. Same pattern citations + format. No paper framing.
```

---

## Wave 3 — Adjacent calibration anchors

### Prompt 7: Knots / Khovanov homology 2024-2026 frontier

```
Project Prometheus is a multi-agent mathematical research substrate. Knot theory is one of our calibration target domains; Techne has request REQ-008 still open for Khovanov-homology computation. We need a substrate-grade survey of the current frontier before forging tools.

Cover:
1. Khovanov homology computation — fastest current implementations (KnotJob, Knotter, Sage, GAP), what knots are tractable (crossings ≤ ?), VRAM/runtime constraints.
2. Khovanov homology theoretical frontier 2024-2026 — sl(N) variants, link-homology categorification, 4-manifold invariants (Rasmussen + Lipshitz et al.).
3. Connections to physics — Witten's interpretation, gauge-theoretic constructions, Gukov et al. recent work.
4. Knot-tabulation status — Burton's tabulation up to which crossing-number; HOMFLY-PT and Jones-polynomial tabulation completeness.
5. Computational complexity of knot invariants — Hass-Lagarias-Pippenger framework status, recent quantum-algorithm proposals 2024-2026.
6. Anti-anchor flags — any "X proved Y in 2024-2026" claims worth verifying.

Format: 7-section report (1. summary, 2. flagged findings, 3. problem statement, 4. status & bounds, 5. literature, 6. attack vectors, 7. cross-references including connection to Prometheus's tensor work). 3000-5000 words. No paper framing. Primary-source citations.
```

### Prompt 8: Maass GL(3) spectral forms 2024-2026

```
Project Prometheus is doing deep research on automorphic-form data domains. Ergon (one of our research agents) has live scripts on Maass GL(3) cross-family analyses (maass_gl3_gap_scan.py) — needs external lit grounding before next research-thread iteration.

Cover:
1. Maass GL(3) computational frontier — Bian-Lazaridis-Booker level of completeness of the database; what spectral parameters have been computed; available data formats; LMFDB integration status as of 2024-2026.
2. Theoretical frontier — Bessel-model frontier (Stade integrals etc.), GL(3) trace formula explicit-formula status, density theorems (Sarnak-Xue, Marshall) refinements.
3. Connections to L-functions — GL(3) Rankin-Selberg, GL(3) × GL(2), GL(3) × GL(3) — moments + non-vanishing recent work.
4. Murmurations in GL(3) — He-Lee-Oliver-Pozdnyakov 2024+ extensions of EC murmurations to higher-rank automorphic; what's been confirmed?
5. Computational complexity / VRAM bottlenecks for GL(3) spectral computation.
6. Anti-anchor flags.

Format: 7-section report. 3000-5000 words. No paper framing.
```

### Prompt 9: Genus-2 curves 2024-2026 frontier

```
Project Prometheus has a "Rosetta Stone" project for genus-2 curves — they sit at the intersection of multiple mathematical worlds (NF, modular forms, BSD, ranks, isogeny). Need substrate-grade survey of 2024-2026 frontier.

Cover:
1. LMFDB g2c data status — completeness of the genus-2 curve database, isogeny class data, conductor ranges, regulator data availability.
2. Paramodular conjecture and Brumer-Kramer — current status; recent verifications 2024-2026.
3. Sato-Tate for genus-2 — Banaszak-Kedlaya classification status; computational verifications 2024-2026.
4. Isogeny graph structure — analogous to elliptic curve isogeny volcanoes? recent work on g2c isogeny graphs.
5. BSD-style rank-prediction in genus-2 — what's known about the analogous BSD conjecture; murmurations / rank-bias analogues.
6. Computational SOTA for g2c L-function computation.
7. Anti-anchor flags.

Format: 7-section report. 3000-5000 words. No paper framing.
```

---

## Wave 4 — Methodology deep dives

### Prompt 10: AlphaEvolve workflow forensics

```
Project Prometheus is studying paradigm-class methodologies for mathematical discovery. AlphaEvolve (DeepMind, May 2024) found a 4×4 matrix multiplication algorithm with rank 48 over ℂ — beating the previous Strassen-style state of the art. We need to understand HOW AlphaEvolve works, not just THAT it worked.

Cover:
1. The AlphaEvolve architecture — base LLM model(s) used, evolutionary loop structure, how candidates are generated and selected, evaluation gate design.
2. Prompt structure and program representation — what does the LLM see? what does it output? code? math expressions? algorithms-as-tensors?
3. Domain coverage — what other problems has AlphaEvolve been applied to? (Cap-set, kissing number, others?) What's the success-rate distribution across domains?
4. Comparison with prior LLM+search systems — FunSearch (Romera-Paredes et al. 2023), AlphaCode, AlphaTensor (DeepMind 2022). What's genuinely new in AlphaEvolve vs prior?
5. Reproducibility — is it open-source? what's known about training data, compute requirements?
6. Limitations and failure modes — where did AlphaEvolve fail or stall? What kinds of problems are out of reach?
7. Substrate-grade implications — what would a Prometheus-internal AlphaEvolve-style system need? (We have small math models 3B-4B locally; we have a substrate vocabulary; could we run a poor-man's AlphaEvolve?)

Format: 7-section report. 4000-6000 words. Primary-source-anchored (DeepMind blog posts, papers, talks). No paper framing.
```

### Prompt 11: Sum-of-squares hierarchies for tensor problems 2024-2026

```
Project Prometheus completed a deep-research report on Tensor PCA computational threshold (T#73) which references SoS lower bounds heavily. We need a fuller survey of SoS for tensor problems 2024-2026.

Cover:
1. SoS hierarchy primer (concise) — Lasserre-Parrilo-style, Positivstellensatz background, levels of the hierarchy.
2. SoS for tensor rank problems — what's known about SoS proofs of tensor-rank lower bounds; Hopkins-Schramm-Steurer 2017 framework; subsequent refinements 2018-2026.
3. SoS for tensor PCA — Hopkins thesis Cornell 2018 baseline; what tightened bounds 2020-2026.
4. SoS for tensor recovery / completion — connections to T#43 / T#73.
5. Computational tools — SOSTOOLS, YALMIP, Mosek scaling limits; what tensor problems are tractable at level k = 2, 4, 6, 8?
6. Lower-bound techniques against SoS — pseudo-distribution methods, low-degree likelihood ratio (LDLR), connections to T#72 type-2 constant.
7. Anti-anchor flags — any "X proved Y in 2024-2026" claims worth verifying.

Format: 7-section report. 4000-5500 words. Primary-source citations. No paper framing.
```

### Prompt 12: Tensor networks in quantum many-body 2024-2026

```
Project Prometheus has a HARD-3 posture that tensor mathematics is "near and dear" — but our substrate work is mostly algebraic-geometric. The largest production tensor-network engineering happens in quantum many-body physics. We need a calibration survey of where that frontier is now.

Cover:
1. DMRG / MPS frontier — what bond dimensions are tractable at scale; recent work on infinite MPS, finite-temperature MPS, time-evolution MPO/TDVP.
2. PEPS frontier — 2D tensor networks, projector entangled pair states, contraction approximations (boundary-MPS, CTMRG).
3. MERA and hierarchical TNs — branching MERA, holographic-MERA developments 2024-2026.
4. Open-source software stack — ITensor (Julia/C++), TeNPy (Python), block2, quimb, TenPy. SOTA performance benchmarks.
5. Connections to lattice gauge theory — recent work on QCD-with-tensor-networks (Banuls et al., Cirac et al. groups).
6. Connections to ML — TT-decomposition for neural-network compression; quantum-inspired classical ML; tensor-network MoE routing.
7. Connections to algebraic-geometric tensor work — does the QMB community use any of the apolarity / secant / cactus machinery? If not (likely), what's the cultural/technical gap?

Format: 7-section report. 4000-6000 words. Primary-source-anchored. No paper framing.
```

---

## Wave 5 — Learner v1.0 corpus inputs

### Prompt 13: Math-reasoning training corpora landscape 2024-2026

```
Project Prometheus is designing the v1.0 training corpus for our Learner model (Ergon agent). We need an external survey of what math-reasoning corpora exist, their scale, license, quality profile, and what anchor-density (theorem/proof/computation density) they offer.

Cover:
1. Major existing math corpora — MATH, GSM8K, MiniF2F, ProofNet, NaturalProofs, MathPile, OpenWebMath, ArXiv-Math, AlgebraicCombinatorics, Mathlib (Lean), Coq stdlib, Isabelle AFP. For each: scale (token count, problem count), license, anchor density.
2. Synthesis-augmented corpora — MetaMath, MAmmoTH, ToRA, DeepSeek-Math training sets. What augmentation strategies work?
3. Verifier-paired corpora — datasets with attached formal verifiers; STEP-DPO style preference data.
4. Anchor-density profiling — for the top 5 corpora above, what fraction is theorem statements vs. proofs vs. computations vs. expository prose? (This matters for our v1.0 anchor-density-first design.)
5. Underexplored corpora — number-theory-specific, algebraic-geometry-specific, knot-theory-specific corpora that exist but are less-mined.
6. Recent SOTA training pipelines — DeepSeek-Math, Qwen-Math, Gemma-Math: what corpora do they use, what augmentations, what evaluation?
7. Anti-anchor flags.

Format: 7-section report. 4000-6000 words. Primary-source citations. No paper framing.
```

### Prompt 14: 3B-4B locally-runnable math models — current SOTA

```
Project Prometheus has a hard VRAM ceiling: 17GB GPU caps usable models at 3B-4B parameters with TransformerLens-style activation tooling. We need a survey of 3B-4B math-specialized models 2024-2026 to inform Apollo/Rhea model selection.

Cover:
1. Top 3B-4B math models 2024-2026 — DeepSeek-Math 7B (too big? quantized variants?), Qwen2-Math-7B (quantized?), Llemma-7B (too big?), specialized 3B variants (DeepSeek-Math-Lite, Phi-3-Math-3B if exists, Gemma-2B-Math), MathStral, Mistral-Math.
2. Per model: parameter count, base model, training corpus, eval scores on MATH/GSM8K/MiniF2F, license, quantization options (4-bit, 8-bit), inference speed on consumer GPUs.
3. Activation-tooling compatibility — which 3B-4B models have working TransformerLens / nnsight / SAE-Lens hooks? Which are blocked by architectural variants (GQA, sliding window attention, MoE)?
4. Fine-tuning toolchains — LoRA, QLoRA, DPO, RLHF for 3B-4B math models on consumer hardware. Memory budget walk-through.
5. Checkpoint availability — open-weights vs API-only; HuggingFace presence.
6. Inference frameworks — vLLM, llama.cpp, mlx, ollama for 3B-4B math models on Win11 with NVIDIA consumer GPU.
7. Anti-anchor flags — any "X model claims Y benchmark in 2024-2026" claims worth verifying.

Format: 7-section report. 4000-6000 words. No paper framing.
```

### Prompt 15: Symbolic-regression / program-synthesis frontiers 2024-2026

```
Project Prometheus is building a substrate vocabulary (primitives + attacks + patterns + composition rules) intended as a discrete action space for a future Learner. The closest neighbor in published research is symbolic-regression and program-synthesis. Need a survey of where that frontier is now.

Cover:
1. Symbolic regression SOTA — PySR (Cranmer et al.), AI Feynman 2.0, DSO (Petersen et al.), Symbolicgpt, recent 2024-2026 work. What discrete grammars do they use?
2. Neural program synthesis — DreamCoder, library-learning systems, neuro-symbolic systems for math.
3. LLM-as-program-synthesizer — FunSearch, AlphaEvolve, Codey-style; how do these compare to non-LLM symbolic-regression?
4. Theorem-proving systems with library learning — Lean4 Mathport, Isabelle Sledgehammer, Coq plugins; how do they handle the analogous "primitive registry" problem?
5. DSL design for math reasoning — Mathematica primitives, SymPy, Magma, Pari/GP; how have they organized their primitive zoos? Are there published design retrospectives?
6. Composition-rule formalisms — operads, PROPs, multicategories — anyone using these explicitly for computational primitive registries 2020-2026?
7. The 'discrete action space for math reasoning' question — is anyone explicitly framing math reasoning as MCTS-over-typed-grammars? If yes, who and what?

Format: 7-section report. 4000-6000 words. Primary-source citations. No paper framing.
```

---

## Wave 6 — Substrate-vocabulary expansion

### Prompt 16: Type theory / categorical foundations for primitive registries

```
Project Prometheus is building a "substrate vocabulary" — a registry of frozen-interface mathematical primitives organized into tiers (Tier-A++ networks, Tier-B witnesses, Tier-C equations, Tier-D distributional certs, Tier-E representation-theoretic invariants), with composition rules between tiers. The closest mature analog is dependent-type theory in proof assistants. We need a focused survey.

Cover:
1. Dependent-type registries in major proof assistants — Lean4 Mathlib, Coq stdlib, Isabelle/HOL, Agda. How do they organize their primitive zoos? Inheritance vs. composition trade-offs.
2. Category-theoretic foundations for primitive composition — operads, PROPs, multicategories, monoidal categories, traced monoidal categories. Which is the right abstract structure for "Tier-B × Tier-D = composite witness"?
3. Recent work on library learning in dependent types — how do Mathlib contributors discover when to refactor a primitive vs introduce a new one?
4. Structure-preserving primitives — when a primitive composes with another, what type-theoretic guarantees can be carried? (E.g., our `CactusRankWitness` composes with `BorderRankWitness` to imply an inequality.)
5. Failure-mode taxonomy — what failure modes do Lean / Coq communities document for primitive misuse? (Our PATTERN_RANK_PARITY_LEAK is essentially a type-confusion error in their language.)
6. Versioning / contract-change-window protocols — how do major proof libraries handle breaking changes? Mathlib's stability policy as exemplar.
7. Cross-pollination opportunities — what could Prometheus borrow from Mathlib's organization, and what's genuinely novel about our approach (substrate-tier model, anti-anchor pins)?

Format: 7-section report. 4000-6000 words. Primary-source citations. No paper framing.
```

### Prompt 17: DSL design for mathematical reasoning

```
[Project Prometheus context — same as Prompt 16.]

Survey of how mature math-DSLs organize their primitive zoos.

Cover:
1. Mathematica primitive zoo — top-level Functions index, how it's organized, design rationale (where documented). Wolfram's "knowledge representation" framework.
2. SymPy module architecture — how the primitive set was organized; the "core" vs "applications" split; how new primitives are vetted.
3. Magma language design — discrete-math focus; primitive zoo organization; intrinsic vs user-defined functions.
4. Pari/GP primitive structure — number-theory focus; how it has evolved 1985-2026.
5. SageMath as super-system — how it federates SymPy + GAP + Pari + Singular + others; what coordination problems arise; what design lessons.
6. Cross-cutting design patterns — "trait-based" dispatch (e.g., Julia AbstractAlgebra.jl); typed arrays; lazy evaluation; categorification.
7. Lessons for Prometheus — which design choices map onto our Tier-A++ through Tier-E hierarchy; which don't; what ought we adopt vs. reject.

Format: 7-section report. 4000-6000 words. Primary-source citations (manuals, design docs, retrospectives). No paper framing.
```

### Prompt 18: Composition-rule literature (operads / PROPs / multicategories)

```
[Project Prometheus context — same as Prompt 16.]

Project Prometheus has confirmed two cross-tier composition rules empirically: (1) Tier-B × Tier-D (constructive witness × distributional cert), and (2) Tier-B × Tier-E (constructive witness × representation-theoretic invariant). We need a survey of mature composition-rule formalisms to ground this and to find candidate structures we may have missed.

Cover:
1. Operads primer (concise) — symmetric operads, non-symmetric operads, colored operads; which fits multi-tier composition?
2. PROPs and props — generalizing operads to multi-input multi-output; relevance to tensor-network composition.
3. Multicategories — generalizing operads to multi-input single-output with arbitrary types; relevance to our Tier-A through Tier-E typed composition.
4. Substructural type systems — linear types, affine types, separation logic; how they manage the "use-once" constraint in primitive composition (analogous to Sigma kernel's linear-capabilities design).
5. Functorial composition — when a Tier-B primitive maps onto a Tier-D primitive, is this a functor? What category structure does the substrate need?
6. Existing primitive-composition-rule libraries — categorial logic, Catlab.jl, GATlab, Coq's HoTT library. How they encode composition rules formally.
7. Concrete recommendations for Prometheus — given our 2 confirmed + 5 candidate compositions, what's the right abstract framework? Is it operadic? PROPs? Multicategorical? Or something simpler (typed graph rewriting)?

Format: 7-section report. 4000-6000 words. Primary-source citations. No paper framing.
```

---

## Wave 7 — Wildcards (2 prompts, fire after Waves 1-6 land)

### Prompt 19: TBD after Waves 1-6

```
[Pick based on what Waves 1-6 surfaced. Likely candidates:
- Cross-domain pattern hunt: are there "X proved Y in 2025" anti-anchor candidates in domains we haven't surveyed (analytic number theory, algebraic geometry, knot theory)?
- Specific deep dive into a primitive class (CactusRankWitness implementation in Macaulay2; or the cotengra contraction-order optimizer internals)?
- Apollo/Rhea-specific: what's the SOTA in math-specialized SAE training for mechanistic interpretability of small math models?
- Calibration: how does Prometheus's substrate-vocabulary compare to OpenAI's / Anthropic's / DeepMind's published reasoning-architecture work?
- Hard-3 expansion: tensor categories in QFT (TQFT, Reshetikhin-Turaev, modular tensor categories) — does our Tier-A++ TensorNetwork have an analog there?]
```

### Prompt 20: TBD after Waves 1-6

```
[Pick based on what Waves 1-6 surfaced. Same candidate list as Prompt 19.]
```

---

## Tracking

After firing each wave, log the date + prompt numbers fired here:

- [ ] Wave 1 fired: ____________
- [ ] Wave 2 fired: ____________
- [ ] Wave 3 fired: ____________
- [ ] Wave 4 fired: ____________
- [ ] Wave 5 fired: ____________
- [ ] Wave 6 fired: ____________
- [ ] Wave 7 fired: ____________

After each return, save Gemini's report to `aporia/docs/gemini_research_2026-05/<wave>_<slug>.md` and check off above.

When all 20 land, run a synthesis pass analogous to `tensor_priority_synthesis_2026-05-09.md` — aim for `gemini_research_synthesis_2026-05.md` consolidating findings, primitive proposals, anti-anchor refinements, catalog updates.
