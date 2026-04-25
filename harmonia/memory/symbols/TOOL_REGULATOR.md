---
name: TOOL_REGULATOR
type: tool
version: 1
tier: 1
language: python
interface: regulator(ainvs) -> float
also:
  - mordell_weil(ainvs) -> dict
  - height(ainvs, point) -> float
dependencies: [cypari]
complexity: dominated by ellrank (exponential in rank in worst case; polynomial for rank <= 3 at small conductor)
tested_against: LMFDB ec_curvedata.regulator for 37.a1, 43.a1, 53.a1, 58.a1, 389.a1, 433.a1, 5077.a1 (match to 10+ decimals); 16/16
failure_modes:
  - CRITICAL saturation gotcha - ellrank alone returns independent points but NOT a Z-basis; tool calls ellsaturation(bound=100) to fix this. Without saturation regulator is (index)^2 too large. Example - 37.a1 unsaturated gives 0.46 instead of 0.051.
  - For rank >= 2 at large conductor (>10^6), ellrank may not prove full rank; inspect rank_lower vs rank_upper in mordell_weil() output.
  - saturation_bound default 100 sufficient for LMFDB curves; raise if suspecting large prime index (rare).
  - Cremona labels not accepted (elldata pkg not installed); use a-invariants.
requested_by: Charon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P03, P08, P17]
references:
  - REQ-005
  - Report #48 (BSD Tier 1, Sha*Reg product bound)
---

# TOOL_REGULATOR — Regulator of an elliptic curve over Q

```python
from techne.lib.regulator import regulator, mordell_weil, height

# 37.a1 rank 1
regulator([0, 0, 1, -1, 0])          # 0.05111140823996884

# 389.a1 rank 2
regulator([0, 1, 1, -2, 0])          # 0.15246017794314375

# Full MW data
mw = mordell_weil([0, 0, 1, -1, 0])
# {'rank_lower': 1, 'rank_upper': 1, 'rank_proved': True,
#  'generators': [[0, -1]], 'regulator': 0.0511...,
#  'height_matrix': [[0.0511...]],
#  'torsion_order': 1, 'torsion_structure': []}

# Neron-Tate height on a specific point
height([0, 0, 1, -1, 0], [0, 0])      # 0.05111... (generator)
height([0, 0, 1, -1, 0], [-1, -1])    # 0.46 = 9 * h(0,0)  (i.e. 3*(0,0))
```

## When to use

- **BSD Tier 1 cross-check**: regulator enters Sha_an = L'(E,1) * |E_tors|^2 / (Omega_E * Reg * prod c_p). Used with `TOOL_CONDUCTOR` (Tamagawa product) to validate BSD formula.
- **Sha*Reg product bound**: Report #48's test requires paired regulator and analytic Sha for each curve; `mordell_weil()` returns both rank bounds so you can flag unproven-rank curves.
- **Height pairing studies**: `height()` for single-point canonical heights; useful for Lehmer-type lower bounds on elliptic curves.

## When NOT to use

- You just need rank: `ellrank` alone is faster.
- Curve has very large conductor and `ellrank` stalls: consider L-function approaches (analytic rank) — regulator may not be computable.
- You need regulator over an NF: this tool is Q-only; no EC/NF regulator yet.

## Critical note on saturation

PARI's `ellrank` returns *independent* non-torsion points, not a saturated Z-basis. This tool always calls `ellsaturation(bound=100)` before forming the height matrix. Without saturation the regulator is off by `index^2`. The `test_saturation_regression` test guards against this.

## Validated against

LMFDB `ec_curvedata.regulator` — match to 10+ decimals across rank 0/1/2/3 curves.
