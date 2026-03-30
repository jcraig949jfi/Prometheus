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

## HUBS TO EVALUATE: Biology & Complex Systems (19 hubs)

### Hub 1: BINDING_PROBLEM
- **Name:** Binding Problem *(look up the formal impossibility statement)*

### Hub 2: BROCAS_BINDING
- **Name:** Brocas Binding *(look up the formal impossibility statement)*

### Hub 3: DUAL_TASK_BOTTLENECK
- **Name:** Dual Task Bottleneck *(look up the formal impossibility statement)*

### Hub 4: FISHERS_THEOREM_LIMITS
- **Name:** Fishers Theorem Limits *(look up the formal impossibility statement)*

### Hub 5: GRASP_IMPOSSIBILITY
- **Name:** Grasp Impossibility *(look up the formal impossibility statement)*

### Hub 6: IMPOSSIBILITY_COMPETITIVE_EXCLUSION
- **Impossibility:** In a Lotka-Volterra system with n species competing for fewer than n limiting resources at equilibrium, coexistence is impossible. If n species compete for k < n resources, at most k species survive at stable equilibrium. Formally: for the system dN_i/dt = N_i(r_i - sum_j(a_ij * N_j)), stable coexis
- **Source:** COMPOSE(n species + k<n resources) -> COMPLETE(stable coexistence) FAILS -> BREAK_SYMMETRY(niche differentiation or nonequilibrium dynamics)

### Hub 7: IMPOSSIBILITY_FISHER_FUNDAMENTAL_THEOREM
- **Impossibility:** Fisher's fundamental theorem (1930): the rate of increase in mean fitness equals the additive genetic variance in fitness divided by mean fitness. This is an exact theorem, but it only accounts for the partial change due to natural selection. The total change in mean fitness can decrease because env
- **Source:** COMPOSE(additive selection + environmental change) -> COMPLETE(net fitness increase) FAILS -> BREAK_SYMMETRY(sacrifice adaptability or stability)

### Hub 8: IMPOSSIBILITY_INFORMATION_BOTTLENECK
- **Impossibility:** The Information Bottleneck method (Tishby et al. 1999) shows that any compressed representation T of input X that preserves information about target Y is bounded by the Markov chain X -> T -> Y. The data processing inequality gives I(T;Y) <= I(X;Y) and I(T;Y) <= I(T;X). For a given compression level
- **Source:** COMPOSE(compression + relevance preservation) -> COMPLETE(both maximal) FAILS -> BREAK_SYMMETRY(trade compression for relevance along IB curve)

### Hub 9: IMPOSSIBILITY_LOTKA_VOLTERRA_STRUCTURAL_STABILITY
- **Impossibility:** May (1972) proved that for a random community matrix A (n species, connectance C, interaction strength sigma), the system is almost surely unstable when sigma*sqrt(n*C) > 1. A large, richly connected ecosystem cannot simultaneously be: species-rich (large n), strongly interacting (large sigma), dens
- **Source:** COMPOSE(diversity + interaction strength + connectivity) -> COMPLETE(stable equilibrium) FAILS -> BREAK_SYMMETRY(reduce one factor or accept instability)

### Hub 10: IMPOSSIBILITY_POPULATION_GENETICS_DRIFT_SELECTION
- **Impossibility:** For a diploid population of effective size N_e, a mutation with selective coefficient |s| << 1/(2*N_e) is effectively invisible to selection and governed entirely by drift. Formally, the fixation probability u(s) = (1 - e^(-4*N_e*s*p)) / (1 - e^(-4*N_e*s)) (Kimura 1962). When |4*N_e*s| < 1, selectio
- **Source:** COMPOSE(selection + finite population) -> COMPLETE(deterministic allele fate) FAILS -> BREAK_SYMMETRY(increase N_e or accept drift dominance)

### Hub 11: IMPOSSIBILITY_PRICE_EQUATION_CONSTRAINT
- **Impossibility:** The Price equation (1970) decomposes evolutionary change into selection and transmission components: Delta(z_bar) = Cov(w,z)/w_bar + E(w*delta_z)/w_bar. A population cannot simultaneously maximize mean fitness, maintain genetic variance, and ensure faithful transmission. Selection that increases mea
- **Source:** COMPOSE(selection + transmission) -> COMPLETE(simultaneous optimization) FAILS -> BREAK_SYMMETRY(sacrifice one component)

### Hub 12: IMPOSSIBILITY_RATE_DISTORTION_NEURAL_CODING
- **Impossibility:** Shannon's rate-distortion theorem applied to neural coding: a neural channel with capacity C bits/sec cannot represent a source with entropy rate H at distortion level D if the rate-distortion function R(D) > C. Specifically, for a neuron with firing rate f_max and refractory period tau, channel cap
- **Source:** COMPOSE(channel capacity + source entropy) -> COMPLETE(lossless representation) FAILS -> BREAK_SYMMETRY(sacrifice precision, range, or add neurons)

### Hub 13: LEWONTIN_HERITABILITY
- **Name:** Lewontin Heritability *(look up the formal impossibility statement)*

### Hub 14: MILLERS_LAW
- **Name:** Millers Law *(look up the formal impossibility statement)*

### Hub 15: MULLERS_RATCHET
- **Name:** Mullers Ratchet *(look up the formal impossibility statement)*

### Hub 16: NEURAL_CODING_LIMITS
- **Name:** Neural Coding Limits *(look up the formal impossibility statement)*

### Hub 17: NEUTRAL_THEORY_LIMITS
- **Name:** Neutral Theory Limits *(look up the formal impossibility statement)*

### Hub 18: RATE_DISTORTION_BOUND
- **Name:** Rate Distortion Bound *(look up the formal impossibility statement)*

### Hub 19: UNIVERSAL_GRAMMAR_LIMITS
- **Name:** Universal Grammar Limits *(look up the formal impossibility statement)*

