# Concept Bridge Architecture — Undiscovered Public Knowledge Layer
## 2026-04-06

---

## The Problem

Scientific knowledge is siloed. Field A knows X→Y. Field C knows Y→Z.
Nobody knows X→Z because nobody reads both literatures. Don Swanson proved
this in the 1980s (fish oil → Raynaud's syndrome). The phenomenon is called
**Undiscovered Public Knowledge (UPK)**.

Our pipeline already finds these bridges computationally — knot determinants
matching LMFDB conductors survived the battery. But we find them by accident,
through LLM hypothesis generation. We need a structural layer that makes
bridge discovery systematic, not serendipitous.

## The Architecture: Atomic Concepts as Bridge Points

### The Core Idea

Every mathematical/scientific object maps to **atomic concepts** — normalized
topics, properties, or relationships. These concepts are the bridge points.

```
KnotInfo                          LMFDB
  knot 3_1 ──→ [determinant: 3]    EC 11.a1 ──→ [conductor: 11]
  knot 4_1 ──→ [determinant: 5]    EC 37.a1 ──→ [conductor: 37]
  knot 5_1 ──→ [determinant: 5]    MF 11.2.a ──→ [level: 11]
       │                                  │
       └────→ [odd_integer] ←────────────┘
       └────→ [prime] ←──────────────────┘
       └────→ [knot_group] ──→ [fundamental_group]
                                    ↑
  Fungrim                    mathlib
    Dedekind_eta ──→ [modular_form]  ──→ [L-function]
    Bernoulli_B  ──→ [zeta_values]   ──→ [special_values]
```

An **atomic concept** is:
- A normalized name (e.g., "prime", "modular_form", "determinant")
- A type (number, structure, property, relationship, theorem)
- Links to objects across datasets (many-to-many)
- Qualifying metadata on each link (how the object relates to the concept)

### Data Model

```
concepts (the atoms)
  id: "C-prime"
  name: "prime number"
  type: "number_property"
  aliases: ["prime", "primes", "prime number", "Primzahl"]

concept_links (the bridges — many-to-many)
  concept_id: "C-prime"
  dataset: "OEIS"
  object_id: "A000040"
  relationship: "is_sequence_of"
  qualifier: "the prime numbers"
  confidence: 1.0

  concept_id: "C-prime"
  dataset: "LMFDB"
  object_id: "11.a1"
  relationship: "conductor_is"
  qualifier: "conductor 11 is prime"
  confidence: 1.0

  concept_id: "C-prime"
  dataset: "KnotInfo"
  object_id: "3_1"
  relationship: "determinant_is"
  qualifier: "determinant 3 is prime"
  confidence: 1.0

  concept_id: "C-prime"
  dataset: "Metamath"
  object_id: "dfprime"
  relationship: "defines"
  qualifier: "formal definition of prime"
  confidence: 1.0
```

### Bridge Discovery

A **bridge** exists when two objects from different datasets share a concept
but have never been connected in the literature:

```sql
-- Find bridges: objects in different datasets sharing a concept
SELECT c.name, l1.dataset, l1.object_id, l2.dataset, l2.object_id
FROM concepts c
JOIN concept_links l1 ON c.id = l1.concept_id
JOIN concept_links l2 ON c.id = l2.concept_id
WHERE l1.dataset != l2.dataset
  AND NOT EXISTS (SELECT 1 FROM known_bridges kb
                  WHERE kb.source = l1.object_id AND kb.target = l2.object_id)
```

This is Swanson's ABC model implemented as a database join.

### How It Maps to Current Pipeline

1. **Concepts are extracted computationally** from each dataset:
   - OEIS: sequence properties (prime, Fibonacci, partition, etc.)
   - LMFDB: conductor factorization, rank, torsion, modular properties
   - KnotInfo: determinant, crossing number, polynomial properties
   - Fungrim: symbol names are already normalized concepts
   - ANTEDB: theorem topics (zero_density, exponent_pairs, etc.)
   - mathlib: namespace hierarchy IS a concept taxonomy
   - Metamath: theorem labels encode concepts

2. **Concept links are the edges** between datasets. Every time a search
   finds a match (OEIS sequence containing knot determinants, LMFDB curve
   with conductor = knot determinant), that's a concept link.

3. **Bridges are the hypotheses** our pipeline tests. The battery validates
   whether the bridge is statistically meaningful or coincidental.

### Building This Out (phases)

**Phase 1: Extract concepts from existing data (computational, no LLM)**
- Parse OEIS A-numbers for known mathematical properties
- Parse LMFDB conductor factorizations
- Parse KnotInfo determinant properties (prime, square-free, etc.)
- Parse Fungrim symbol names as concepts
- Parse mathlib namespace hierarchy as concept taxonomy
- Store in concepts.jsonl + concept_links.jsonl

**Phase 2: Build the bridge query**
- For each concept, find objects across 2+ datasets
- Score bridges by: number of shared concepts, uniqueness of the bridge,
  statistical significance from battery runs
- Rank bridges by "Sleeping Beauty" potential: high concept overlap,
  zero existing citations/connections

**Phase 3: Feed bridges into the research cycle**
- Instead of LLM-generated hypotheses, generate hypotheses FROM bridges
- "Objects X (KnotInfo) and Y (LMFDB) share concepts [prime, odd, <100].
  Hypothesis: their deeper invariants (polynomial coefficients vs a_p values)
  also correlate."
- This makes hypothesis generation data-driven, not LLM-creative

**Phase 4: Literature grounding**
- For each bridge, search Semantic Scholar for papers connecting the two domains
- If no papers exist → high UPK potential (Sleeping Beauty territory)
- If papers exist → validate our bridge against published results

### What This Replaces

Currently our hypothesis generation is:
```
LLM creativity → search plan → search → battery
```

With the concept layer, it becomes:
```
Concept extraction → bridge detection → hypothesis from bridge → search → battery
```

The LLM is removed from hypothesis generation entirely for bridge-derived
hypotheses. The concepts are data. The bridges are joins. The hypotheses are
structural, not creative. The battery still adjudicates.

### The Sleeping Beauty Index

For each bridge, compute:
- **Concept overlap score**: how many shared concepts?
- **Citation gap**: do papers in domain A cite papers in domain B? (via Semantic Scholar)
- **Statistical strength**: did the battery SURVIVE when tested?
- **Uniqueness**: is this bridge novel or does everyone know about it?

Bridges with high overlap, zero citations, battery survival, and high
uniqueness are **Sleeping Beauty candidates** — the most valuable output
of the entire pipeline.

---

## Relationship to Existing Prometheus Architecture

This is the **Library of Alexandria** vision from project_prometheus_vision.md,
made concrete. The spatial tensors are the embeddings. The concept layer is
the catalog. The bridges are the cross-references between scrolls that nobody
has read together.

The tensor trains (future) search the bridge layer. The concept atoms are
the coordinates. The qualifying metadata is the metric.

---

*"The bridge exists. The fare is tokens. The cargo is structure."*
*— Charon role document, adapted*
