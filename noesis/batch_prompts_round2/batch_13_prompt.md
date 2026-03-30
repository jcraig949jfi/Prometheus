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

## HUBS TO EVALUATE: Round 2 Batch 1 (5 hubs)

### Hub 1: ALGEBRAIC_COMPLETION
- **Impossibility:** Complete a structure by restoring missing elements, then reduce/simplify
- **Source:** Al-jabr pattern: fill gaps then balance. Appears wherever equations need solving.

### Hub 2: BINARY_DECOMP_RECOMP
- **Impossibility:** Decompose into binary components, compose selectively, reduce to result
- **Source:** Universal binary decomposition-recomposition motif for computing products via doubling and selection

### Hub 3: BYZANTINE_GENERALS_BOUND
- **Name:** Byzantine Generals Bound *(look up the formal impossibility statement)*

### Hub 4: CHURCH_UNDECIDABILITY
- **Name:** Church Undecidability *(look up the formal impossibility statement)*

### Hub 5: CIRCUIT_COMPLEXITY_LOWER_BOUND
- **Impossibility:** The MOD_q function cannot be computed by constant-depth circuits with AND/OR/MOD_p gates for distinct primes p,q; certain explicit functions require super-polynomial size bounded-depth circuits | SOURCE: Razborov 1987 (AC^0 lower bounds for clique); Smolensky 1987 (algebraic methods); Hastad 1986 (e
- **Source:** COMPOSE(shallow_circuit) -> COMPLETE(MOD_function) FAILS -> BREAK_SYMMETRY(algebraic_degree) | WHY: Low-degree polynomials over F_p cannot approximate MOD_q for p != q; the algebraic structure of the 

