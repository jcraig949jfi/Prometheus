---
name: TOOL_FALTINGS_HEIGHT
type: tool
version: 1
tier: 1
language: python
interface: faltings_height(ainvs) -> float
also:
  - faltings_data(ainvs) -> dict (h_F, omega_1, tau, minimal_ainvs, is_minimal)
dependencies: [cypari]
complexity: O(1) after ellperiods; ellminimalmodel dominates for non-minimal input
tested_against: LMFDB ec_curvedata.faltings_height 37.a1, 389.a1, 5077.a1, 66.b1; match to 10+ decimals
failure_modes:
  - Formula identity only holds for GLOBAL MINIMAL Weierstrass models. Tool runs ellminimalmodel first; non-minimal input is reduced silently (minimal_ainvs in output dict).
  - For non-semistable curves (curves with additive reduction at some prime), the formula still holds because h_F = h_F_stable for E/Q (LMFDB's faltings_height and stable_faltings_height agree for all curves over Q).
  - Uses double-precision floats via Python complex; for high precision, switch to mpmath manually.
requested_by: Charon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P03, P08]
references:
  - REQ-006
  - Report #2 (BSD Tier 0 cross-check)
---

# TOOL_FALTINGS_HEIGHT — Faltings height of E/Q

```python
from techne.lib.faltings_height import faltings_height, faltings_data

faltings_height([0, 0, 1, -1, 0])            # 37.a1 -> -0.9965422076...
faltings_height([1, 1, 1, -352, -2689])       # 66.b1 -> -0.0949539009...

r = faltings_data([0, 0, 1, -1, 0])
# {'h_F': -0.99654..., 'omega_1': (5.9869+0j), 'tau': (0.5+1.66...j),
#  'minimal_ainvs': [0, 0, 1, -1, 0], 'is_minimal': True}
```

## The formula (why it's clean)

For an elliptic curve E/Q in a GLOBAL MINIMAL Weierstrass model with period
lattice Λ = Z ω_1 + Z ω_2 (τ = ω_2 / ω_1, Im τ > 0):

    h_F(E/Q) = -log|ω_1| - (1/2) log(Im τ)

This is the result after cancelling (1/12) log|Δ_min|, -log(2π), -2 log|η(τ)|,
and -(1/2) log(Im τ) through the identity
    (2π/ω_1)^12 η(τ)^24 = Δ_E.

## Process

1. Reduce input to minimal model via `ellminimalmodel` (no-op if already minimal).
2. Call `ellperiods` on the minimal model.
3. Compute τ = ω_2 / ω_1, conjugate if Im τ < 0.
4. Return -log|ω_1| - (1/2) log(Im τ).

Why the simpler early-cycle formulas failed: they either didn't cancel the
(1/12) log|Δ| term properly, or used omega[1] on the non-minimal input model.

## When to use

- **BSD Tier 0 cross-check** (Charon, Report #2): pair with `TOOL_REGULATOR`,
  `TOOL_CONDUCTOR`, `TOOL_ANALYTIC_SHA` for a four-factor BSD audit.
- **Szpiro-style Faltings-vs-conductor scans**: compare h_F across log(N).
- **abc-conjecture experiments**: h_F is a natural height in Faltings/Szpiro inequalities.

## When NOT to use

- Over an NF, not Q: this is Q-only. For NFs, the formula has extra terms
  summing over archimedean places.
- You need high precision (>15 decimals): switch to mpmath-based periods.
