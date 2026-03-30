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

## HUBS TO EVALUATE: Control & Signal Processing (12 hubs)

### Hub 1: ANTENNA_GAIN_BANDWIDTH
- **Name:** Antenna Gain Bandwidth *(look up the formal impossibility statement)*

### Hub 2: GABOR_LIMIT
- **Name:** Gabor Limit *(look up the formal impossibility statement)*

### Hub 3: IMPOSSIBILITY_BODE_GAIN_PHASE
- **Impossibility:** For any stable, minimum-phase, causal LTI system, the phase at any frequency omega_0 is uniquely determined by the gain curve via the Hilbert transform: angle(G(j*omega_0)) = (1/pi) * PV integral of (d(ln|G|)/d(ln omega)) * ln|coth(|u|/2)| du, where u = ln(omega/omega_0). A designer cannot independe
- **Source:** COMPOSE(gain + phase + minimum-phase) -> COMPLETE(independent specification) FAILS -> BREAK_SYMMETRY(allow non-minimum-phase zeros or sacrifice gain/phase freedom)

### Hub 4: IMPOSSIBILITY_CHANNEL_CODING_CONVERSE
- **Impossibility:** For a discrete memoryless channel with capacity C, any code with rate R > C has error probability P_e -> 1 exponentially fast as block length n -> infinity. Specifically, P_e >= 1 - 2^(-n*E_sp(R,C)) where E_sp is the sphere-packing exponent. The strong converse (Wolfowitz 1957, Arimoto 1973) proves 
- **Source:** COMPOSE(rate above capacity + reliable decoding) -> COMPLETE(low error communication) FAILS -> BREAK_SYMMETRY(reduce rate or accept exponential error growth)

### Hub 5: IMPOSSIBILITY_KALMAN_OPTIMALITY_BOUND
- **Impossibility:** The Kalman filter achieves the minimum mean-square estimation error for linear Gaussian systems. For any other estimator E applied to y = Cx + v (Gaussian noise), MSE(E) >= MSE(Kalman) = tr(P), where P satisfies the Riccati equation P = APA' - APC'(CPC'+R)^(-1)CPA' + Q. No estimator can beat the Kal
- **Source:** COMPOSE(noisy observations + linear dynamics) -> COMPLETE(perfect state estimation) FAILS -> BREAK_SYMMETRY(accept Riccati-bounded error or add sensors)

### Hub 6: IMPOSSIBILITY_LUCAS_CRITIQUE_POLICY_INVARIANCE
- **Impossibility:** Econometric models estimated under one policy regime cannot be used to predict outcomes under a different policy regime, because agents' decision rules (and hence the model parameters) change endogenously with policy. Policy-invariant reduced-form models are impossible when agents are forward-lookin
- **Source:** COMPOSE(reduced_form_estimation) → COMPLETE(policy_invariant_predictions) FAILS → BREAK_SYMMETRY(estimate_deep_structural_parameters) | Reduced-form parameters are functions of both structural (prefer

### Hub 7: IMPOSSIBILITY_MIMO_FUNDAMENTAL_LIMITS
- **Impossibility:** In MIMO (multi-input multi-output) systems, the sensitivity function S(s) = (I + G(s)K(s))^(-1) satisfies: for any plant G with RHP zero z (output direction u_z, input direction v_z), the sensitivity in direction u_z at frequency omega = Im(z) cannot be made less than |u_z' * S(j*omega) * u_z| >= pr
- **Source:** COMPOSE(multivariable control + directional performance) -> COMPLETE(independent per-channel optimization) FAILS -> BREAK_SYMMETRY(accept directional coupling or decouple plant)

### Hub 8: IMPOSSIBILITY_PONTRYAGIN_MAXIMUM_PRINCIPLE
- **Impossibility:** Pontryagin's Maximum Principle (1956): for a control system dx/dt = f(x,u) minimizing J = integral L(x,u)dt + phi(x(T)), the optimal control must satisfy the Hamiltonian condition H(x*,u*,lambda) >= H(x*,u,lambda) for all admissible u, where lambda satisfies the costate equation d_lambda/dt = -dH/dx
- **Source:** COMPOSE(bounded control + optimality + smoothness) -> COMPLETE(smooth optimal trajectory) FAILS -> BREAK_SYMMETRY(accept bang-bang switching or relax bounds)

### Hub 9: IMPOSSIBILITY_SMALL_GAIN_THEOREM
- **Impossibility:** The Small Gain Theorem: a feedback interconnection of two stable systems G and Delta is stable for ALL perturbations ||Delta||_inf <= 1/gamma iff ||G||_inf < gamma. A system with high loop gain (||G||_inf >= gamma) for performance CANNOT be robustly stable against all perturbations of size 1/gamma. 
- **Source:** COMPOSE(performance gain + robustness margin) -> COMPLETE(both maximal) FAILS -> BREAK_SYMMETRY(sacrifice performance or robustness)

### Hub 10: IMPOSSIBILITY_WATERBED_GENERALIZED
- **Impossibility:** For a feedback system with plant P(s) having p unstable poles {p_i} and z unstable zeros {z_j}, the weighted sensitivity integral satisfies: integral_0^inf ln|S(j*omega)| * W(omega) d_omega = pi * sum_i Re(p_i) + corrections from unstable zeros. When unstable zeros are present, the waterbed is ampli
- **Source:** COMPOSE(sensitivity reduction + unstable poles/zeros) -> COMPLETE(global sensitivity reduction) FAILS -> BREAK_SYMMETRY(accept amplified waterbed or redesign plant)

### Hub 11: NYQUIST_SHANNON
- **Name:** Nyquist Shannon *(look up the formal impossibility statement)*

### Hub 12: SHANNON_CHANNEL_CAPACITY
- **Name:** Shannon Channel Capacity *(look up the formal impossibility statement)*

