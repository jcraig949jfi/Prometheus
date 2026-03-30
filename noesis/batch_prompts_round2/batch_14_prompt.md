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

## HUBS TO EVALUATE: Round 2 Batch 2 (5 hubs)

### Hub 1: CIRCUIT_LOWER_BOUNDS
- **Name:** Circuit Lower Bounds *(look up the formal impossibility statement)*

### Hub 2: CLAUSIUS_INEQUALITY
- **Name:** Clausius Inequality *(look up the formal impossibility statement)*

### Hub 3: COMPLEXITY_HIERARCHY
- **Name:** Complexity Hierarchy *(look up the formal impossibility statement)*

### Hub 4: COSMIC_CENSORSHIP
- **Name:** Cosmic Censorship *(look up the formal impossibility statement)*

### Hub 5: COVERING_SPACE_OBSTRUCTION
- **Impossibility:** A continuous map lifts to a covering space if and only if its induced fundamental group homomorphism lands in the covering subgroup; otherwise lifting is impossible | SOURCE: Lifting criterion theorem, formalized by Seifert and Threlfall 1934; modern treatment in Hatcher Ch.1
- **Source:** MAP(continuous) -> EXTEND(lift) FAILS -> BREAK_SYMMETRY(fundamental_group) | WHY: The long exact sequence of homotopy groups for the fibration forces pi_1 compatibility; loops in the base that are not

