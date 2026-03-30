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

## HUBS TO EVALUATE: Game Theory & Social Choice (17 hubs)

### Hub 1: ARROW_IMPOSSIBILITY
- **Name:** Arrow Impossibility *(look up the formal impossibility statement)*

### Hub 2: COMMONS_DILEMMA
- **Name:** Commons Dilemma *(look up the formal impossibility statement)*

### Hub 3: CONDORCET_PARADOX
- **Name:** Condorcet Paradox *(look up the formal impossibility statement)*

### Hub 4: IMPOSSIBILITY_BILATERAL_TRADE_CHATTERJEE_SAMUELSON
- **Impossibility:** No incentive-compatible, individually rational, budget-balanced mechanism achieves full efficiency (ex-post trade whenever gains from trade exist) in bilateral trade with two-sided private information || CLOSURE FAILURE: With two-sided private information, the buyer has incentive to understate value
- **Source:** With two-sided private information, the buyer has incentive to understate value and the seller to overstate cost. The information rent required to elicit truthful reports from both sides exceeds the g

### Hub 5: IMPOSSIBILITY_COASE_IMPOSSIBILITY_CONDITIONS
- **Impossibility:** Efficient bargaining over externalities (Coase's result) fails when any of: (1) transaction costs are positive, (2) property rights are unclear, (3) parties are asymmetrically informed, or (4) there are many affected parties (public goods/commons). These conditions are generic, making the Coase resu
- **Source:** COMPOSE(bilateral_bargaining) → COMPLETE(efficient_externality_resolution) FAILS → BREAK_SYMMETRY(Pigouvian_tax_or_regulatory_assignment) | Under asymmetric information, the Myerson-Satterthwaite theo

### Hub 6: IMPOSSIBILITY_CONDORCET_JURY_LIMITATIONS
- **Impossibility:** The Condorcet Jury Theorem (majority voting aggregates information optimally) fails when: (1) voters are correlated (common information sources), (2) voters vote strategically rather than sincerely, or (3) voter competence is below 0.5. Under strategic voting, sincere revelation is not a Nash equili
- **Source:** COMPOSE(majority_vote_aggregation) → COMPLETE(optimal_collective_decision) FAILS → BREAK_SYMMETRY(mechanism_design_for_truthful_revelation) | Under strategic voting, a pivotal voter conditions on bein

### Hub 7: IMPOSSIBILITY_CONGESTION_PRICE_OF_ANARCHY
- **Impossibility:** Selfish routing in congestion games produces outcomes whose social cost can be a factor of Theta(log n / log log n) worse than optimal for general latency functions; no toll mechanism can simultaneously achieve system optimality, budget balance, and voluntary participation || CLOSURE FAILURE: Indivi
- **Source:** Individual best-response dynamics minimize personal cost, not social cost. The externality each agent imposes on others (marginal congestion contribution) is not internalized. Wardrop equilibrium and 

### Hub 8: IMPOSSIBILITY_DICTATORSHIP_WITHOUT_MONEY
- **Impossibility:** Without monetary transfers, any strategy-proof and onto social choice function over three or more alternatives with unrestricted preferences must be dictatorial; no non-dictatorial truthful mechanism exists without payments || CLOSURE FAILURE: Strategy-proofness imposes severe monotonicity constrain
- **Source:** Strategy-proofness imposes severe monotonicity constraints on the social choice function. With three or more alternatives and unrestricted ordinal preferences, the only functions satisfying these mono

### Hub 9: IMPOSSIBILITY_ENVY_FREE_DIVISION
- **Impossibility:** No deterministic mechanism for dividing indivisible goods can simultaneously guarantee envy-freeness, Pareto efficiency, and strategy-proofness || CLOSURE FAILURE: Envy-freeness requires symmetric treatment of agents, efficiency requires responsiveness to cardinal preferences, and truthfulness requi
- **Source:** Envy-freeness requires symmetric treatment of agents, efficiency requires responsiveness to cardinal preferences, and truthfulness requires monotonicity in allocations. The monotonicity constraints fr

### Hub 10: IMPOSSIBILITY_FOLK_THEOREM_BOUNDARY
- **Impossibility:** The folk theorem shows that virtually any individually rational payoff is sustainable as a Nash equilibrium in infinitely repeated games, but this breaks down with finite horizons, imperfect monitoring, or lack of common knowledge of rationality; backward induction forces defection in finitely repea
- **Source:** In finite games, backward induction from the last period unravels all cooperation: in the final round, defection dominates; knowing this, defection dominates in the penultimate round, etc. The infinit

### Hub 11: IMPOSSIBILITY_IMPLEMENTATION_MASKIN
- **Impossibility:** A social choice rule is Nash-implementable only if it satisfies Maskin monotonicity; many natural social choice rules (including most cardinal welfare criteria) fail this condition || CLOSURE FAILURE: If an alternative a is chosen at preference profile theta but not at theta', and agent i's lower co
- **Source:** If an alternative a is chosen at preference profile theta but not at theta', and agent i's lower contour set at a weakly expands from theta to theta', then no Nash equilibrium mechanism can distinguis

### Hub 12: IMPOSSIBILITY_REVENUE_EQUIVALENCE_BREAKDOWN
- **Impossibility:** Revenue equivalence across auction formats fails when bidders are risk-averse, asymmetric, have interdependent valuations, or face budget constraints; no single auction format simultaneously maximizes revenue, efficiency, and simplicity || CLOSURE FAILURE: Revenue equivalence holds only under indepe
- **Source:** Revenue equivalence holds only under independent private values with risk-neutral symmetric bidders. Risk aversion breaks the isomorphism between first-price and second-price auctions (expected paymen

### Hub 13: IMPOSSIBILITY_SECOND_WELFARE_IMPOSSIBILITY
- **Impossibility:** The Second Welfare Theorem (any Pareto efficient allocation can be decentralized as a competitive equilibrium with appropriate lump-sum transfers) fails when: (1) preferences are non-convex, (2) lump-sum transfers are informationally infeasible, (3) increasing returns to scale exist. Redistribution 
- **Source:** COMPOSE(lump_sum_transfers + competitive_markets) → COMPLETE(any_efficient_allocation_achieved) FAILS → BREAK_SYMMETRY(distortionary_taxation_with_efficiency_cost) | Lump-sum transfers require knowled

### Hub 14: IMPOSSIBILITY_STABLE_MATCHING_THREE_SIDED
- **Impossibility:** No stable matching need exist for three-sided (or higher) matching markets; the Gale-Shapley deferred acceptance algorithm cannot be generalized beyond two-sided markets || CLOSURE FAILURE: In two-sided markets, the lattice structure of stable matchings (guaranteed by the rural hospitals theorem and
- **Source:** In two-sided markets, the lattice structure of stable matchings (guaranteed by the rural hospitals theorem and Birkhoff's representation) breaks down with three or more sides. Preference cycles of the

### Hub 15: IMPOSSIBILITY_VCG_BUDGET_BALANCE
- **Impossibility:** No mechanism can simultaneously achieve efficiency (welfare maximization), incentive compatibility, individual rationality, and budget balance in general quasi-linear settings || CLOSURE FAILURE: The VCG transfer payments that align individual incentives with social welfare necessarily produce a bud
- **Source:** The VCG transfer payments that align individual incentives with social welfare necessarily produce a budget surplus (or deficit). The Clarke pivot payments extracted from agents cannot generically sum

### Hub 16: REVENUE_EQUIVALENCE
- **Name:** Revenue Equivalence *(look up the formal impossibility statement)*

### Hub 17: VCG_BUDGET_IMPOSSIBILITY
- **Name:** Vcg Budget Impossibility *(look up the formal impossibility statement)*

