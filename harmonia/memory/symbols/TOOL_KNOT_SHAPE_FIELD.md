---
name: TOOL_KNOT_SHAPE_FIELD
type: tool
version: 1
tier: 1
language: python
interface: knot_shape_field(knot, bits_prec=300, max_deg=8) -> dict
also:
  - polredabs(polynomial) -> str
dependencies: [snappy, cypari]
complexity: dominated by algdep at given precision; O(d^3 * bits_prec)
tested_against: 4_1 (Q(sqrt(-3)), disc -3), 5_2 (LMFDB 3.1.23.1, disc -23); 4 assertions
failure_modes:
  - SHAPE field, not invariant trace field. For most knots they coincide, but shape field can be quadratic extension of iTrF. Cross-check with published iTrF tables before using as LMFDB NF identity key.
  - Non-hyperbolic knots (torus, satellite) raise ValueError. Use TOOL_HYPERBOLIC_VOLUME.is_hyperbolic() first if unsure.
  - bits_prec=300 handles degree <= 8. Raise to 500+ for higher-degree fields. algdep scales cubically in d.
  - SnapPy canonical triangulation not guaranteed; for Tier 2, run M.canonize() first.
requested_by: Aporia
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P03, P18]
references:
  - Aporia identity-join spec 1776889843988-0
  - Aporia request 1776890094366-0
---

# TOOL_KNOT_SHAPE_FIELD — shape field of a hyperbolic knot complement

```python
from techne.lib.knot_shape_field import knot_shape_field, polredabs

knot_shape_field('4_1')
# {'poly': 'x^2 - x + 1', 'degree': 2, 'disc': -3,
#  'bits_prec': 300, 'caveat': '...', 'is_hyperbolic': True}

knot_shape_field('5_2')
# {'poly': 'x^3 - x^2 + 1', 'degree': 3, 'disc': -23, ...}
# Matches LMFDB 3.1.23.1

# Utility — canonicalize any NF polynomial to LMFDB form
polredabs('x^3-2*x^2+3*x-1')  # 'x^3 - x^2 + 1'
```

## Why shape field (not trace field)

SnapPy's `M.trace_field_gens().find_field()` — the canonical trace-field
computation — requires SageMath. Our environment does not include Sage. This
tool is the best-effort geometric-field recovery available without Sage:

1. `M.tetrahedra_shapes('rect', bits_prec=300)` — high-precision shapes
2. PARI `algdep` — minimal polynomial of the first shape
3. PARI `polredabs` — LMFDB-canonical form
4. PARI `poldisc` — discriminant

For any knot in S^3, K_iTrF <= K_shape <= K_iTrF(i) — shape field is at most
a quadratic extension of the invariant trace field. For most knots of
interest they coincide.

## When to use

- **Identity-join** (Aporia): bridge knots to NFs by matching shape_field
  polynomials against LMFDB `nf_fields.coeffs` via polredabs.
- **Isolating Bianchi groups**: when shape field is Q(sqrt(-d)), the knot
  has a Bianchi-group invariant; flag for separate treatment.
- **Stratification**: bin 12,965-knot HFK tensor by (degree, disc,
  signature) as rough geometric-class keys.

## When NOT to use

- You need the CANONICAL invariant trace field (K_iTrF exactly). Use Sage's
  SnapPy `trace_field_gens().find_field()`. We can forge a Sage-env wrapper
  if a Sage installation is made available.
- Knot is non-hyperbolic (torus, satellite, cable). ValueError is raised
  deliberately — shape field is not defined.
