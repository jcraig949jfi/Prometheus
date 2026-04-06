# Charon Cartography v3 — Design Document
## Based on lessons from v2 (2026-04-06)

---

## What v2 Got Right
- Falsification battery as authoritative adjudicator
- NLI relevance gate (cheap, catches garbage before battery)
- Kill diagnosis (genuine_null vs resolution_limit vs artifact)
- Search plan enrichment (inject real data for placeholders)
- Random dataset selection (forces novel combinations)
- Nested loops (research → tensor review → council review)
- Structured JSONL logging

## What v2 Got Wrong
- LLM hypothesis generation still hallucinates search params (7% rejection rate)
- Battery skips 40%+ of threads (insufficient numerical data)
- JSON parse failures waste 10%+ of tokens despite JSON mode
- No literature grounding for hypotheses
- No Sleeping Beauty detection
- No inverse search capability
- Concept layer is nouns only (integer values), not verbs (operations)
- No constrained null tests (mass-balance, conservation laws)

---

## v3 Architecture

### 1. Hypothesis Generation: Bridge-Driven, Not LLM-Creative

**v2:** LLM proposes hypotheses from prompt → validation gate filters bad ones.

**v3:** Three hypothesis sources, prioritized:
1. **Bridge-derived** (from concept_index.py) — objects sharing concepts across
   datasets generate hypotheses automatically. No LLM needed. Highest priority.
2. **Literature-derived** (from external_research.py + Sleeping Beauty scan) —
   papers with high Beauty Coefficient near our topics generate hypotheses.
3. **LLM-creative** (current system) — fallback when bridges and literature
   don't produce enough candidates. Lowest priority.

Token budget: 0 for bridge/literature hypotheses. LLM only as fallback.

### 2. Search: Verb-Aware, Not Noun-Matching

**v2:** Searches match object properties (integers, names, types).

**v3:** Add operation-aware searches:
- Fungrim formula STRUCTURE matching (which operations connect which symbols)
- mathlib import PATTERNS (not just namespace names)
- Stoichiometric matrix ALGEBRAIC properties (rank, nullspace, eigenvalues)
- Cross-dataset TRANSFORMATION matching (same verb, different domains)

New search functions:
- `fungrim_operation_pattern(pattern="Equal(Sum, Product)")` — find formulas with matching operation structure
- `lmfdb_eigenvalue_check(eigenvalues=[...], constants_tol=0.005)` — check if eigenvalues match known constants
- `metabolism_sv_ratios(model_id, top_n=20)` — return SV ratios for a BiGG model
- `cross_dataset_verb_match(verb="factors_as", datasets=["lmfdb", "knots"])` — find objects connected by the same operation

### 3. Battery: Domain-Aware, With Constrained Nulls

**v2:** Same 11 tests for all hypotheses. Random matrices as null.

**v3:** Add domain-specific null generators:
- **Stoichiometric null:** random matrices satisfying mass balance (S·1 = 0 for each metabolite)
- **Divisibility null:** random integers with matching prime factorization distribution
- **Polynomial null:** random polynomials with matching degree and coefficient distribution
- **Graph null:** random graphs with matching degree distribution (Erdos-Renyi or configuration model)

Each null preserves the CONSTRAINTS of the domain while randomizing the DATA.
The metabolism signal (z=32) needs the stoichiometric null specifically.

### 4. Concept Layer: Verbs as Primary Coordinates

**v2:** Concepts are mostly nouns — "prime", "determinant_5", "conductor_11".

**v3:** Concept extraction prioritizes operations:
- From Fungrim: `Equal`, `Sum`, `Product`, `Integral`, `Limit`, `Derivative`
- From mathlib: `import` relationships as verbs, theorem TYPES (def, lemma, theorem)
- From LMFDB: `factors_as`, `is_isogenous_to`, `has_modular_form`
- From KnotInfo: `has_polynomial`, `is_amphichiral`, `crossing_change`
- From metabolism: `produces`, `consumes`, `catalyzes`, `inhibits`

The tensor dimensions become: [domain, object, operation, target].
Distance = how similarly two objects BEHAVE under the same operations.

### 5. Literature Layer: Sleeping Beauty Detection + Inverse Search

**v2:** External research feed searches by keyword, archives by domain.

**v3:** Add three capabilities:
1. **Beauty Coefficient** — compute B for all papers in S2 results.
   High B = forgotten paper. High B + topically adjacent = priority read.
2. **Inverse search** — for each surviving hypothesis, query Elicit/Consensus:
   "What frameworks resolve [X]?" without specifying domain.
3. **Citation topology** — for papers near our findings, use Scite to check:
   supported (confirmation) vs contrasted (disagreement) vs mentioned (gap).

### 6. Constant Geometry: Integrated Into Search

**v2:** Separate tool, not in the pipeline.

**v3:** Constant matching is a search function:
- Any numerical result from any search gets checked against 439 constants
- Eigenvalues, ratios, statistical measures — all pass through constant_matcher
- Matches above threshold become concept links automatically
- Base-phi representation for cross-constant clustering

### 7. Tensor Train: The Endgame Search

**v2:** Not implemented (separate tensors per domain, bridge layer as joins).

**v3 prep:** Build the data structures that TT needs:
- Per-domain embedding matrices (done for LMFDB, need others)
- Cross-domain bridge matrix (from concept_index, enriched with verbs)
- Sparse tensor representation of the full cross-product
- When ready: TT-decompose, read bond dimensions, search by contraction

This is Phase 3-4 of the tensor train architecture doc. v3 builds the
input format. v4 does the actual decomposition.

---

## Migration Path

### v2 → v3 (incremental, not rewrite)
1. Add bridge-derived hypothesis generator alongside LLM (new function, not replacement)
2. Add constrained null generators to battery (new tests, existing framework)
3. Add verb extraction to concept_index.py (extend, not replace)
4. Add Sleeping Beauty computation to external_research.py (new function)
5. Add constant_matcher as a search function in search_engine.py
6. Add metabolism-specific searches to search_engine.py

### Breaking Changes: None
v3 is additive. v2 continues to work. New features are additional
hypothesis sources, additional null tests, additional concept types.

---

## Success Metrics for v3

1. **Bridge-derived hypotheses > 50% of total** (currently 0%)
2. **Battery skip rate < 20%** (currently ~40%)
3. **Constrained null for metabolism** — does z=32 survive?
4. **Verb concepts > noun concepts** in concept_index
5. **At least 1 Sleeping Beauty paper found** relevant to our findings
6. **Inverse search produces 1+ cross-domain paper** per priority thread
