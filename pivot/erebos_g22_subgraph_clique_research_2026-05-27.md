# G22 Subgraph/Clique Generator — Research Notes

**Date:** 2026-05-27 (ITER-3 prep, authored ITER-2)
**Status:** Iteration-3 implementation target. Tier A per spec.

---

## Spec recap

- **Mechanism:** Operate on the graph of surviving claims. If a
  dense clique of claims all survive independently, posit a
  master structural theorem that generates the whole clique.
- **Input:** Dense cluster of surviving (PROMOTED or substantively-
  UNVERIFIED) Erebos compositions with high Jaccard overlap on
  parent_record_ids or composition_payload fields.
- **Transformation:** Intersect the logical predicates of the
  entire clique; emit the intersection as a master property M.
- **Output:** "Clique C is generated entirely by Master Property M."
- **Falsification Route:** Find an object satisfying M but
  breaking one of the sub-claims.
- **Expected Kill Pattern:** `counterexample_breaks_master_unification`.
- **Loader Feasibility:** Tier A. Needs `networkx` dep + Louvain /
  label-propagation community detection.

---

## Reasoning Ladder mapping

- **Primary R3** (abstraction: the master property IS the abstracted
  shared structure).
- **Secondary R8** (conjecture formation: "C iff M" is a non-trivial
  conjecture).

---

## Adjacent fields

- Graph community detection (Louvain, label propagation, modularity
  optimization).
- Frequent subgraph mining (gSpan, FSG, GraphMiner).
- Concept lattices (Formal Concept Analysis — Ganter & Wille).
- Galois connections (objects ↔ attributes).
- The Apriori algorithm (frequent itemset mining; G22's claim-
  intersection analog).

---

## Dependencies

- **`networkx`** for graph construction + community detection.
  Not currently in Charon env; add to `charon/agents/erebos
  /requirements_extras.txt` or fall back to a hand-rolled
  Louvain (~80 LOC) to avoid the dep.

---

## Simple test claims (MVP)

1. Input: 5+ Erebos G02 contrast claims that all share the
   `permutation_n=1000` payload field.
   Clique: all 5 form a community by this shared coordinate.
   Master property: "all G02 contrast claims using permutation_n=
   1000 share the same shape" (potentially trivial).
   Expected kill: trivial-master — counterexample is any other
   permutation_n.

2. Input: 3+ Pollux PROMOTED pairs on Mahler subsets.
   Clique by shared subset_a domain (Mossinghoff).
   Master property: "all Pollux Mossinghoff-subset PROMOTED pairs
   share property M" — e.g., M = "subset_a is Salem-class".
   Expected kill: find a non-Salem subset that also produces
   PROMOTED.

---

## Frontier questions

```
A research swarm wants a generator that operates on the graph of
its own surviving claims: find a dense clique, posit that a
single Master Property M generates the whole clique. Falsification:
find an object satisfying M but breaking one sub-claim in the
clique.

Q1. Formal Concept Analysis (Ganter-Wille) treats this exact
    object↔attribute Galois connection. How should we use FCA to
    derive the master property rather than just guess it?
Q2. Louvain modularity is the standard community detection. Is
    it appropriate when nodes are claims and edges are payload-
    overlap, or should we use bipartite graph methods (claims ↔
    payload fields)?
Q3. Frequent-itemset mining (Apriori) gives confidence + support
    metrics for intersections. Are these the right scoring for
    G22's master-property candidates?
Q4. Pythia: are there published systems doing automatic
    master-theorem inference from clique structure in empirical
    mathematical claim databases?
Q5. When the clique is small (say 3 claims), the master property
    is over-determined (many M's fit). What's the principled choice?
```

---

## TDD test list (sketch)

1. `test_g22_not_applicable_without_clique`
2. `test_g22_detects_simple_3_member_clique`
3. `test_g22_master_property_is_intersection_of_payloads`
4. `test_g22_six_field_spec`
5. `test_g22_expected_kill_pattern`
6. `test_g22_metadata`

---

## Implementation sketch

```python
class SubgraphCliqueGenerator:
    id = "g22_subgraph_clique"
    name = "Subgraph / Clique"
    spec_phase = 5
    feasibility_tier = "A"
    reasoning_tier = "R3"
    expected_kill_pattern = "counterexample_breaks_master_unification"

    MIN_CLIQUE_SIZE = 3
    MIN_JACCARD_OVERLAP = 0.40

    def _build_claim_graph(self, state):
        # Nodes: Erebos compositions
        # Edges: Jaccard(parent_record_ids ∪ composition_payload.keys()) >= threshold
        ...

    def _find_largest_clique(self, graph):
        # Hand-rolled Louvain or simple greedy clique-finding
        ...
```

ETA: ~280 LOC + dep management (~30 LOC if hand-rolled Louvain).

---

## Handoff

- ITER-3: implement with hand-rolled clique detection to avoid
  networkx dep risk; can swap to networkx in v0.10 if benefits
  warrant.
- ITER-4+: tie to composition-aware loader so master-property
  candidates actually get battery-tested.

— Charon, 2026-05-27 (authored 2026-05-26 ITER-2)
