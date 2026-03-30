# BATCH SPOKE GENERATION — Fill the Grid

## Your Task

For each hub listed below, evaluate ALL 9 damage operators and classify each cell as FILLED, EMPTY_PLAUSIBLE, or IMPOSSIBLE.

### The 9 Damage Operators
| # | Operator | What it does | Example |
|---|----------|-------------|---------|
| 1 | DISTRIBUTE | Spread damage uniformly | Equal temperament |
| 2 | CONCENTRATE | Localize damage | Wolf interval |
| 3 | TRUNCATE | Remove problematic region | Bandlimiting |
| 4 | EXPAND | Add resources/structure | Error correction |
| 5 | RANDOMIZE | Convert to probability | Monte Carlo |
| 6 | HIERARCHIZE | Push to meta-level | Combined cycle engines |
| 7 | PARTITION | Split domain | Gain scheduling |
| 8 | QUANTIZE | Force onto discrete grid | 12-TET tuning |
| 9 | INVERT | Reverse direction | Heat pumps |

## Output Format

Return a JSON array. For each hub, provide hub_id and a 9-element operator_grid:

```json
[
  {
    "hub_id": "EXAMPLE_HUB",
    "operator_grid": [
      {"operator": "DISTRIBUTE", "status": "FILLED", "resolution_name": "Name", "description": "1-2 sentences", "primitive_sequence": ["MAP","SYMMETRIZE"], "cross_domain_analog": "equal_temperament"},
      {"operator": "CONCENTRATE", "status": "IMPOSSIBLE", "description": "Why it cant apply"},
      {"operator": "TRUNCATE", "status": "EMPTY_PLAUSIBLE", "description": "What it would look like"}
    ]
  }
]
```

Rules:
- FILLED = known technique from published literature. Name it.
- IMPOSSIBLE = structural reason why this operator CANNOT apply.
- EMPTY_PLAUSIBLE = could exist but you cant name a specific technique.

---

## HUBS TO EVALUATE: Round 2 Batch 10 (4 hubs)

### Hub 1: POINCARE_DUALITY_OBSTRUCTION
- **Impossibility:** Not every space satisfying Poincare duality is a manifold; surgery theory obstructions (Wall groups) prevent realization of Poincare duality spaces as manifolds | SOURCE: C.T.C. Wall, 1970. Surgery on Compact Manifolds. London Mathematical Society Monographs
- **Source:** DUALIZE(homology<->cohomology) -> COMPLETE(manifold_structure) FAILS -> BREAK_SYMMETRY(surgery_obstruction) | WHY: The surgery exact sequence contains L-group obstructions; the signature and Arf invar

### Hub 2: TOPOLOGICAL_INVARIANCE_OF_DIMENSION
- **Name:** Topological Invariance Of Dimension *(look up the formal impossibility statement)*

### Hub 3: UNIQUE_GAMES_CONJECTURE
- **Impossibility:** If the Unique Games Conjecture holds, optimal inapproximability thresholds for Max-Cut, Vertex Cover, and many CSPs are exactly characterized by SDP relaxation gaps; beating the SDP bound is NP-hard | SOURCE: Khot 2002. On the power of unique 2-prover 1-round games. STOC 2002. Khot-Kindler-Mossel-O'
- **Source:** MAP(approximate) -> COMPLETE(beyond_SDP_ratio) FAILS -> BREAK_SYMMETRY(integrality_gap) | WHY: Unique Games hardness reductions show that the SDP relaxation captures all polynomial-time extractable in

### Hub 4: WHITNEY_EMBEDDING_BOUND
- **Name:** Whitney Embedding Bound *(look up the formal impossibility statement)*

