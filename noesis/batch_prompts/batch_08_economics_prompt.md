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
    "hub_id": "BROUWER_FIXED_POINT",
    "operator_grid": [
      {"operator": "DISTRIBUTE", "status": "FILLED", "resolution_name": "Approximate fixed points", "description": "Distribute error across epsilon-approximate fixed points.", "primitive_sequence": ["MAP","SYMMETRIZE"], "cross_domain_analog": "equal_temperament"},
      {"operator": "CONCENTRATE", "status": "IMPOSSIBLE", "description": "Fixed points are global; cannot localize."},
      {"operator": "TRUNCATE", "status": "EMPTY_PLAUSIBLE", "description": "Restrict to subdomain where fixed point is known."}
    ]
  }
]
```

Rules:
- FILLED = known technique from published literature. Name it.
- IMPOSSIBLE = structural reason why this operator CANNOT apply.
- EMPTY_PLAUSIBLE = could exist but you can't name a specific technique.

---

## HUBS TO EVALUATE: Economics & Social Science (14 hubs)

### Hub 1: ASHBY_LIMITS
- **Name:** Ashby Limits *(look up the formal impossibility statement)*

### Hub 2: BLACK_SCHOLES_ASSUMPTIONS
- **Name:** Black Scholes Assumptions *(look up the formal impossibility statement)*

### Hub 3: EFFICIENT_MARKET_LIMITS
- **Name:** Efficient Market Limits *(look up the formal impossibility statement)*

### Hub 4: HUMES_GUILLOTINE
- **Name:** Humes Guillotine *(look up the formal impossibility statement)*

### Hub 5: IMPOSSIBILITY_DIAMOND_DYBVIG_BANK_RUNS
- **Impossibility:** A banking system cannot simultaneously provide liquidity transformation (short-term deposits funding long-term loans), maintain sequential service (first-come-first-served withdrawal), and be immune to self-fulfilling bank runs, without deposit insurance or a lender of last resort.
- **Source:** COMPOSE(maturity_transformation) → COMPLETE(run_free_equilibrium) FAILS → BREAK_SYMMETRY(introduce_deposit_insurance_or_suspension_of_convertibility) | The demand-deposit contract creates two Nash equ

### Hub 6: IMPOSSIBILITY_GROSSMAN_STIGLITZ_PARADOX
- **Impossibility:** If markets are perfectly informationally efficient (prices fully reflect all information), then no agent has incentive to acquire costly information. But if no one acquires information, prices cannot reflect it. Perfect informational efficiency and costly information acquisition are mutually incompa
- **Source:** COMPOSE(rational_information_acquisition) → COMPLETE(informationally_efficient_prices) FAILS → BREAK_SYMMETRY(allow_noise_traders_or_information_rents) | In equilibrium, informed traders' profits must

### Hub 7: IMPOSSIBILITY_LONG_RUN_PHILLIPS_CURVE
- **Impossibility:** There is no permanent trade-off between inflation and unemployment. In the long run, monetary policy can only choose the inflation rate, not the unemployment rate. Attempts to hold unemployment below the natural rate permanently lead to accelerating inflation.
- **Source:** COMPOSE(monetary_expansion) → COMPLETE(permanent_unemployment_reduction) FAILS → BREAK_SYMMETRY(accept_natural_rate_or_structural_reform) | Adaptive (Friedman) or rational (Lucas/Sargent) expectations

### Hub 8: IMPOSSIBILITY_STOLPER_SAMUELSON_DISTRIBUTIONAL
- **Impossibility:** Free trade cannot benefit all factors of production simultaneously. In a Heckscher-Ohlin framework, trade liberalization necessarily raises the real return to the abundant factor and lowers the real return to the scarce factor. Pareto-improving trade is impossible without compensation.
- **Source:** COMPOSE(trade_liberalization) → COMPLETE(pareto_improvement_for_all_factors) FAILS → BREAK_SYMMETRY(compensatory_transfers_or_factor_mobility) | With two goods, two factors, and constant returns to sc

### Hub 9: IMPOSSIBILITY_WELFARE_IMPOSSIBILITY_INTERPERSONAL
- **Impossibility:** Ordinal utility theory provides no basis for interpersonal comparisons of utility. Without cardinal, comparable utility functions, social welfare functions requiring utility aggregation (utilitarian, Rawlsian, etc.) cannot be constructed from individual choice data alone.
- **Source:** COMPOSE(ordinal_preferences) → COMPLETE(interpersonal_welfare_comparison) FAILS → BREAK_SYMMETRY(impose_cardinal_comparability_assumption_or_use_capabilities) | Ordinal utility is invariant under arbi

### Hub 10: INTERPERSONAL_UTILITY
- **Name:** Interpersonal Utility *(look up the formal impossibility statement)*

### Hub 11: PROBLEM_OF_INDUCTION
- **Name:** Problem Of Induction *(look up the formal impossibility statement)*

### Hub 12: QUINE_INDETERMINACY
- **Name:** Quine Indeterminacy *(look up the formal impossibility statement)*

### Hub 13: SONNENSCHEIN_MANTEL_DEBREU
- **Name:** Sonnenschein Mantel Debreu *(look up the formal impossibility statement)*

### Hub 14: WOLPERT_NO_FREE_LUNCH
- **Name:** Wolpert No Free Lunch *(look up the formal impossibility statement)*

