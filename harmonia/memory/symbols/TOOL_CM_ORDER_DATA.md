---
name: TOOL_CM_ORDER_DATA
type: tool
version: 1
tier: 1
language: python
interface: cm_order_data(D) -> dict (fundamental_disc, cm_conductor, class_number, is_maximal, ring_class_polynomial, degree)
dependencies: [cypari]
complexity: O(1) for small |D|; polclass slows for h > 20
tested_against: 9 Heegner fundamentals (f=1), 4 non-maximal orders (-12, -16, -27, -28), Q(√-15) (h=2); 17 assertions
failure_modes:
  - D must be < 0 and ≡ 0 or 1 mod 4. Other inputs raise ValueError.
  - polclass can be expensive for high class number (h > 20); consider setting a class-number cap if used in bulk scans.
  - ring_class_polynomial string format uses PARI's default; polredabs optional if canonicality is needed for matching.
requested_by: Aporia
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P02, P08]
references:
  - Aporia per-disc residual regression 1776900205287-0
  - REQ-023
---

# TOOL_CM_ORDER_DATA — imaginary quadratic CM order invariants

```python
from techne.lib.cm_order_data import cm_order_data

cm_order_data(-12)
# {'fundamental_disc': -3, 'cm_conductor': 2, 'class_number': 1,
#  'is_maximal': False,
#  'ring_class_polynomial': 'x - 54000', 'degree': 1}

cm_order_data(-27)['cm_conductor']    # 3 (order Z + 3·O_{Q(√-3)})
cm_order_data(-3)['is_maximal']        # True
cm_order_data(-15)['class_number']     # 2
```

## Why this exists — Aporia's per-disc residual

Aporia's F011 closure regression at 79% gap1 / 69% gap4 left a per-disc
residual pattern that log|D| alone doesn't capture: D=-4 gives -16pp,
D=-12 gives +9pp, D=-16 gives -20pp, D=-27 gives -0.2pp. These four
discs all have `h(O_D) = 1` so class number is not discriminating.
The differentiator is the **CM conductor** f:

| D | d_K | f | residual |
|---|-----|---|----------|
| -4 | -4 | 1 | -16pp |
| -12 | -3 | 2 | +9pp |
| -16 | -4 | 2 | -20pp |
| -27 | -3 | 3 | -0.2pp |

Whether `(d_K, f)` as paired fixed effects (or their interaction) collapses
the per-disc dummy structure is Aporia's testable question. This tool gives
her `(d_K, f)` in one call per CM EC's discriminant.

## CM arithmetic, one paragraph

An imaginary quadratic field K = Q(√d_K) has maximal order O_K. The
non-maximal orders are O_f = Z + f·O_K for f ≥ 1 (the "conductor"
of the order). A CM elliptic curve has CM by exactly one such order,
and its CM discriminant is D = d_K · f². f = 1 ⟺ CM by the maximal
order ⟺ the ring class field = the Hilbert class field of K. For f > 1
the ring class field is a proper extension of the Hilbert class field,
and its conductor over K is exactly f.

## When to use

- **Aporia's next-predictor test** (R² residual regression): feed each
  CM EC's discriminant through this tool to get (d_K, f); regress the
  per-disc residuals on (log|D|, cm_conductor) instead of per-disc dummies.
- **Stratifying CM curves**: maximal vs non-maximal order is a natural
  coarse stratum; f is the finer fingerprint.
- **Identity-join on CM-j**: ring_class_polynomial is the unique monic
  polynomial over Z whose roots are j-invariants of CM-by-O_D curves.
  Useful for matching CM EC LMFDB labels against the 13 rational CM j's.

## When NOT to use

- D > 0: this is for imaginary quadratic only. Real CM is a different story.
- You only need h(O_K) of a maximal order: `TOOL_CLASS_NUMBER(f'x^2+{-d_K}')`
  is faster and more general (works for arbitrary NFs).
- Bulk scan over h > 20: `polclass` becomes expensive; consider caching.
