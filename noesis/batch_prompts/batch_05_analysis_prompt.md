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

## HUBS TO EVALUATE: Analysis & Approximation (18 hubs)

### Hub 1: BAIRE_CATEGORY
- **Name:** Baire Category *(look up the formal impossibility statement)*

### Hub 2: CANTOR_DIAGONALIZATION
- **Name:** Cantor Diagonalization *(look up the formal impossibility statement)*

### Hub 3: CLASSIFICATION_IMPOSSIBILITY_WILD
- **Name:** Classification Wild *(look up the formal impossibility statement)*

### Hub 4: ERGODIC_BREAKING
- **Name:** Ergodic Breaking *(look up the formal impossibility statement)*

### Hub 5: IMPOSSIBILITY_BALASSA_SAMUELSON_PRICE_CONVERGENCE
- **Impossibility:** Purchasing Power Parity (equal price levels across countries) is impossible when countries differ in relative productivity between tradable and non-tradable sectors. Higher-productivity countries systematically have higher price levels for non-tradables.
- **Source:** COMPOSE(trade_equalization + internal_wage_equalization) → COMPLETE(absolute_PPP) FAILS → BREAK_SYMMETRY(accept_systematic_price_level_differences) | Trade equalizes tradable goods prices. Internal la

### Hub 6: IMPOSSIBILITY_BERNSTEIN_LETHARGY
- **Impossibility:** For any sequence of nested finite-dimensional subspaces V_1 ⊂ V_2 ⊂ ... in a Banach space X, and any rate ε_n → 0, there exists an element f ∈ X whose best approximation error E_n(f) = inf_{g ∈ V_n} ||f-g|| decreases no faster than ε_n.
- **Source:** COMPOSE(nested_subspace_approximation) → COMPLETE(guaranteed_fast_rate) FAILS → BREAK_SYMMETRY(restrict_to_smoothness_subclass) | The quotient space X/V_n has infinite dimension for each n. The best a

### Hub 7: IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY
- **Impossibility:** For functions in the Sobolev space W^s_p([0,1]^d), the optimal approximation rate using n parameters is O(n^{-s/d}). As dimension d grows, exponentially many parameters are needed to maintain a fixed accuracy. No method escapes this for the full Sobolev class.
- **Source:** COMPOSE(grid_sampling) → COMPLETE(accurate_high_dimensional_approximation) FAILS → BREAK_SYMMETRY(exploit_low_dimensional_structure_or_sparsity) | The ε-covering number of the unit ball in W^s_p([0,1]

### Hub 8: IMPOSSIBILITY_DU_BOIS_REYMOND_FOURIER_DIVERGENCE
- **Impossibility:** There exists a continuous function on [0,2π] whose Fourier series diverges at a point. Pointwise convergence of Fourier series is not guaranteed even for continuous functions.
- **Source:** COMPOSE(Fourier_partial_sums) → COMPLETE(pointwise_recovery) FAILS → BREAK_SYMMETRY(restrict_to_Lp_convergence_or_Cesaro_summation) | The Dirichlet kernel D_n has unbounded L^1 norm (grows as log n). 

### Hub 9: IMPOSSIBILITY_FABER_THEOREM_INTERPOLATION
- **Impossibility:** For any triangular array of interpolation nodes in [a,b], there exists a continuous function for which the interpolating polynomial sequence diverges. No single choice of nodes guarantees convergence for ALL continuous functions.
- **Source:** COMPOSE(polynomial_interpolation_on_fixed_nodes) → COMPLETE(convergence_for_all_f_in_C[a,b]) FAILS → BREAK_SYMMETRY(restrict_smoothness_class_or_use_best_approximation) | The Banach-Steinhaus theorem 

### Hub 10: IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY
- **Impossibility:** The span of monomials {x^{λ_n}} is dense in C[0,1] if and only if Σ 1/λ_n = ∞. If the exponents are too sparse (series converges), the monomial system cannot approximate all continuous functions.
- **Source:** COMPOSE(lacunary_monomial_span) → COMPLETE(dense_in_C[0,1]) FAILS → BREAK_SYMMETRY(add_missing_exponents_until_divergence_condition_met) | When Σ 1/λ_n < ∞, the closed span of {x^{λ_n}} in C[0,1] is a

### Hub 11: IMPOSSIBILITY_TRACKING_DISTURBANCE_LIMIT
- **Impossibility:** For a SISO feedback system, the complementary sensitivity T(s) = 1 - S(s) satisfies its own integral constraint: for plants with time delay tau, integral_0^inf (1/omega^2) * ln|T(j*omega)| d_omega <= pi*tau/2. Tracking (requiring T close to 1) and noise rejection (requiring T close to 0) at high fre
- **Source:** COMPOSE(tracking + noise rejection + time delay) -> COMPLETE(both perfect) FAILS -> BREAK_SYMMETRY(limit bandwidth or accept noise amplification)

### Hub 12: IMPOSSIBILITY_UNIFORM_CONVERGENCE_FOURIER
- **Name:** Uniform Convergence Fourier *(look up the formal impossibility statement)*

### Hub 13: IMPOSSIBILITY_UNIVERSAL_APPROXIMATION_RATE_IMPOSSIBILITY
- **Impossibility:** No approximation scheme can achieve a universal rate of convergence for all continuous functions simultaneously. For any sequence of approximation operators L_n with dim(L_n)=n, there exist continuous functions that converge arbitrarily slowly.
- **Source:** COMPOSE(finite_basis_expansion) → COMPLETE(uniform_rate_for_all_f) FAILS → BREAK_SYMMETRY(restrict_function_class_by_smoothness_or_spectral_decay) | By the Bernstein lethargy theorem, for any decreasi

### Hub 14: IMPOSSIBILITY_VALIANT_EVOLVABILITY
- **Impossibility:** In Valiant's (2009) formal model of evolvability, evolution is modeled as a restricted form of statistical query learning. A concept class is evolvable iff it is learnable by statistical queries with tolerance. Boolean functions requiring superpolynomial statistical queries (e.g., parities, cryptogr
- **Source:** COMPOSE(mutation + selection + polynomial time) -> COMPLETE(arbitrary function learning) FAILS -> BREAK_SYMMETRY(restrict target class or allow exponential time)

### Hub 15: IMPOSSIBILITY_ZAMES_SENSITIVITY
- **Impossibility:** Zames (1981) formulated the H-infinity optimal control problem: minimize ||W*S||_inf over all stabilizing controllers, where W is a performance weighting and S is the sensitivity function. The minimum achievable value gamma_opt > 0 is determined by the plant's unstable poles and zeros via Nevanlinna
- **Source:** COMPOSE(sensitivity minimization + stability + unstable plant) -> COMPLETE(arbitrarily low sensitivity) FAILS -> BREAK_SYMMETRY(accept gamma_opt floor or redesign plant)

### Hub 16: LIOUVILLE_APPROXIMATION
- **Name:** Liouville Approximation *(look up the formal impossibility statement)*

### Hub 17: MUNTZ_SZASZ
- **Name:** Muntz Szasz *(look up the formal impossibility statement)*

### Hub 18: WEIERSTRASS_NOWHERE_DIFFERENTIABLE
- **Name:** Weierstrass Nowhere Differentiable *(look up the formal impossibility statement)*

