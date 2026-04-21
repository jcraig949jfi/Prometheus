# Frontier Model Review Synthesis — 2026-04-21
## Three models reviewed. Here's what they agreed on.

---

## Reviewers
- **Gemini** (detailed, 7 sections, specific citations)
- **ChatGPT** (systems-level, emphasis on continuum limits and SoS)
- **Claude-frontier** (calibrated, emphasis on edge quality and compatibility)

---

## Consensus: 6 New Paradigms (P19-P24)

All three models independently identified the same gaps. We now have **24 paradigms**.

| ID | Name | Agreed By | Core Move |
|----|------|-----------|-----------|
| P19 | Model-Theoretic / O-Minimality | All 3 | Tame definability bounds rational points |
| P20 | Ergodic / Dynamical Systems | All 3 | Recast as measure-preserving system |
| P21 | Higher-Order Fourier | Gemini + ChatGPT | Gowers norms generalize Fourier |
| P22 | Information-Theoretic / Entropy | All 3 | Bound structure via compression |
| P23 | Proof Mining / Reverse Math | Gemini | Extract computational content from ineffective proofs |
| P24 | Renormalization / Scale Separation | Gemini + ChatGPT | Coarse-grain across scales, find fixed points |

ChatGPT also flagged **Sum-of-Squares / Proofs-to-Algorithms** as borderline distinct from P17 (Variational). Gemini added **Microlocal / D-module analysis** as a possible P25. Both deferred for now but noted.

---

## Consensus: Highest-EV Paradigm Gaps

| Combination | Recommended By | Data Asset | Why High-EV |
|-------------|---------------|-----------|-------------|
| P15 (Tensor) × L-function families | Gemini + ChatGPT | 24M L-functions | Build T[E,p,k] = a_p(E)^k tensor; low-rank = CM/congruence |
| P13 (Tropical) × genus-2 / EC | Gemini + ChatGPT | 66K g2c, 3.8M EC | Tropical moduli stratification via j-invariant |
| P20 (Ergodic) × OEIS | Gemini | 394K sequences | Sequences as trajectories; equidistribution mod m |
| P21 (Higher Fourier) × NF signatures | Gemini | 22M NF | U^k norms on multiplicative groups |
| P22 (Entropy) × isogeny graphs | Gemini | 3.8M EC | Entropy of isogeny class = new invariant |
| P24 (RG Flow) × conductor stratification | ChatGPT | 24M L-functions | Atkin-Lehner as scale transformation; Sato-Tate as fixed point |

**Gemini's single highest-EV bet:** Tensor decomposition on L-function families. Hits god nodes (F011, F003), uses underexploited paradigm (P15), and our data is uniquely positioned.

---

## Consensus: Techne Priority Order

All three models agreed: **foundational primitives first, specialized tools last.**

| Priority | Tool | Why First | Agreed By |
|----------|------|-----------|-----------|
| 1 | LLL Reduction | Unblocks lattice, height, MPS approaches | Gemini + ChatGPT |
| 2 | Smith Normal Form | Unblocks cohomology, module classification | Gemini + ChatGPT + Claude |
| 3 | Class Number | Bridges NF, L-functions, arithmetic stats | All 3 |
| 4 | Galois Group | Structural invariant across all domains | All 3 |
| 5 | Functional Equation Verification | Validates P05 pipeline | Gemini + ChatGPT |
| 6 | Selmer Rank | Derived from SNF + Class Number | Gemini + Claude |
| 7 | Analytic Sha | Derived from FE + special values | Gemini |
| 8 | Khovanov Betti | Specialized, defer unless attacking F032 | All 3 |

**Key insight (Gemini):** "Build the trunk before the branches." LLL and SNF feed at least four downstream tools each.

---

## Consensus: Graph Densification

753 isolated nodes is a coverage problem. All three models identified the same fix categories:

| Strategy | Source | Expected Impact |
|----------|--------|-----------------|
| LMFDB cross-database links | Gemini | Halves isolated nodes (tens of thousands of curated edges) |
| MSC code co-occurrence | Gemini | Weak but broad edges between co-classified concepts |
| arXiv co-citation projection | Gemini + ChatGPT | Medium-strength edges from shared citations |
| Typed edges (uses, blocks, generalizes) | Claude | Critical for reasoning, not just clustering |
| Negative edges (incompatible, fails under) | Claude | Essential for avoiding false bridges |
| Intermediate abstraction nodes | Claude | Connective tissue ("L-function zero statistics" as hub) |
| Embedding similarity (with caution) | Gemini + ChatGPT | High false-positive risk; validate sample by hand |
| nLab / Encyclopedia of Math hyperlinks | Gemini | Small but high-quality |

**Claude's unique contribution:** "You need negative edges. Without 'incompatible with' / 'fails under', the graph can't reason — only cluster." This is the most important structural fix.

---

## Consensus: Sleeping Beauty Detection

All three models said yes. The formula converged:

```
SB(node) = StructuralImportance(node) / (HumanAttention(node) + ε)
```

Where:
- **Structural Importance** = betweenness + PageRank + eigenvector centrality (weighted)
- **Human Attention** = papers/year + citations + arXiv activity + MathOverflow tags

Refinements from Gemini:
- Time decay on attention (half-life ~10 years)
- Distinguish "dormant" (was hot, now cold) from "unattempted" (never noticed)
- Accessibility weighting (prerequisite depth matters)
- **Backtest** on known cases: Iwasawa pre-1970s, Khovanov pre-1999, Voevodsky pre-2000s

---

## Consensus: Paradigm Gap Formalization

All three models converged on **matrix completion with EV scoring**:

```
M[problem, paradigm] ∈ {0, 0.5, 1, ?}

EIG(p, a) = Importance(p) × Novelty(a,p) × Feasibility(a) × P(success|a,p)
```

**Gemini's extension:** The matrix factors (via SVD) reveal latent dimensions of paradigms — what makes paradigms similar in their applicability. "The latent dimensions may themselves be a discovery."

**Claude's critical filter:** "untried ≠ promising." Need a **compatibility layer** C[problem, paradigm] to filter structurally mismatched combinations before scoring.

**ChatGPT's extension:** This is really a three-way tensor with tools as the third axis:

```
T[problem, paradigm, tool_bundle] → EIG
```

---

## Consensus: Missing Tools (2025-2026)

| Tool | Recommended By | What It Unlocks |
|------|---------------|-----------------|
| OSCAR.jl (Julia CAS) | Gemini + ChatGPT | Replaces Sage for heavy lifting; native tropical, group theory, polyhedral |
| SDPA-GMP 8.0 | Gemini | Arbitrary-precision SDP; turns flag algebras into proof certificates |
| Lean 4 duper/hammer | Gemini | Semantic theorem search by type signature |
| flint3 | Gemini | Speedups for number-theoretic primitives |
| graph-tool / PyG | Claude | Beyond NetworkX for scale |
| PyMC / NumPyro | Claude | Probabilistic programming for uncertainty |

---

## The Meta-Observation (From Gemini)

> "Your system has an unusually clean separation between what to attack (knowledge graph), how to attack (paradigm taxonomy), and with what (Techne). The risk is that the three layers stay too decoupled. The highest leverage may be in the joint optimization: which (problem, paradigm, tool-bundle) triple has highest EIG given current state."

This is the **Aporia Action Score** — the unified metric that ties all three deliverables together.

---

## Actions Taken

1. **Paradigm catalog updated** from 18 → 24 (`attack_paradigms.json` v2)
2. **Paradigm gap matrix tool built** (`paradigm_gap_matrix.py`) — framework works, needs population enrichment
3. **This synthesis document** for permanent reference

## Next Actions (from review)

1. Enrich paradigm-problem matrix with LLM-assisted classification (sample 5%, audit)
2. Ingest LMFDB cross-database links into knowledge graph
3. Add typed edges (uses, blocks, generalizes) and negative edges (incompatible, fails)
4. Forge LLL + SNF as Techne's next two tools (unblocks 4+ downstream each)
5. Build Sleeping Beauty detector using betweenness / attention ratio
6. Evaluate OSCAR.jl as Sage replacement for heavy computation
7. Implement the three-way (problem × paradigm × tool) tensor for joint EIG optimization

---

*Three frontier models, one synthesis. The paradigm gap matrix is the strategic instrument. Build it, populate it, optimize across it.*

*Prometheus / Aporia — 2026-04-21*
