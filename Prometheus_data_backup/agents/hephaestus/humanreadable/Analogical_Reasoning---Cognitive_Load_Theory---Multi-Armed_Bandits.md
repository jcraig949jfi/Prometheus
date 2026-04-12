# Analogical Reasoning + Cognitive Load Theory + Multi-Armed Bandits

**Fields**: Cognitive Science, Cognitive Science, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:49:16.712709
**Report Generated**: 2026-03-31T16:39:45.729698

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – For each prompt and candidate answer, run a deterministic regex‑based extractor that produces a set of triples ⟨subject, predicate, object⟩. Predicates are normalized to a finite inventory: *negation* (¬), *comparative* (>,<,≥,≤), *conditional* (→), *causal* (→₍c₎), *ordering* (before, after, first, …), and *numeric* (=, ≠, <, >). Entities and numeric literals become node identifiers; predicates become edge labels with attached weight = 1 for symbolic relations, = |value₁−value₂| for numeric edges. The output is a directed labeled graph G = (V,E) stored as two NumPy arrays: V (shape [n_nodes, 2]) for node type IDs and E (shape [n_edges, 3]) for (src, predicate‑ID, dst).  

2. **Chunking (Cognitive Load)** – Compute intrinsic load Lᵢ = |V| + |E| (total elements). During matching, only sub‑graphs up to a fixed chunk size C (e.g., C = 7) are considered; any extra elements contribute to extraneous load Lₑ = max(0, |V|−C) + max(0, |E|−C).  

3. **Analogical Mapping** – For a candidate graph Gₖ and a reference solution graph Gᵣ, find the maximum‑weight sub‑graph isomorphism limited to chunk C using a greedy breadth‑first search that prioritizes edges with identical predicate IDs. Let M be the set of matched edges; germane load L_g = |M|.  

4. **Score** – Raw similarity S = ∑_{e∈M} w_e − α·∑_{e∈Eₖ\M} w_e − β·|numₖ−numᵣ|, where w_e = 1 for symbolic edges and w_e = exp(−|Δ|) for numeric edges, α,β are small constants (0.1). Final score = L_g − γ·(Lᵢ + Lₑ) with γ = 0.05.  

5. **Multi‑Armed Bandit Allocation** – Treat each candidate answer as an arm. Maintain empirical mean μₖ and pull count nₖ. After each incremental chunk evaluation (i.e., after processing another C elements), compute Upper Confidence Bound UCBₖ = μₖ + c·√(ln t / nₖ) (c = 1.0). Select the arm with highest UCBₖ for the next chunk, update μₖ with the newly obtained partial score, and increment nₖ. After a budget of T chunks per arm, return the arm with highest μₖ.  

**Parsed Structural Features** – Negation tokens, comparative operators, conditional antecedents/consequents, causal cue verbs, ordering adverbs, numeric literals, entity‑type tags, and attribute‑value pairs.  

**Novelty** – While structure‑mapping engines, cognitive‑load‑aware chunking, and bandit‑based resource allocation exist separately, their joint use to dynamically allocate reasoning effort while explicitly penalizing extraneous load is not present in current literature, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — The algorithm captures relational structure and uncertainty, but relies on greedy matching which may miss optimal mappings.  
Metacognition: 7/10 — Load terms provide explicit self‑regulation of working memory, yet the chunk size is fixed rather than adaptively inferred.  
Hypothesis generation: 6/10 — Bandit selection drives exploration of candidates, but hypothesis space is limited to parsed triples; richer abstractions are not generated.  
Implementability: 9/10 — All components use only regex, NumPy arrays, and standard‑library data structures; no external models or APIs are needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:39:17.032009

---

## Code

*No code was produced for this combination.*
