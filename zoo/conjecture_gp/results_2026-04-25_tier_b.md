# Tink 2 Tier B results — 2026-04-25

**Verdict (Tier B): VALIDATED**

- n = 1000, seed = 42
- Aggregate: α · L_expr − β · |z|  (α=`0.1`, β=`1.0`)
- Pareto axes: (1 − basis_projection, affordance_gain, reconstructability)
- η_composite = `0.7` · η_inverse + `0.3` · η_trace
- Lineage tags: DISABLED (γ = 0; basis_projection measured but not penalized)

## Tier B additions

- **CAS Layer C** (SymPy symbolic canonicalization). For each candidate,
  expressions are converted to SymPy and checked for linear-combination
  membership in the identity basis. If reduced, basis_projection = 1.0
  is set with explicit `cas_reduced_to` provenance. Else fall through to
  Layer B linear regression.
- **η_trace** (AST step-by-step reversibility). Per internal AST node,
  measure how reversible the operation is. `add`/`sub`/`mul` collapse
  information; `neg`/`scalar_mul`/`exp`/`log` are bijective. η_trace =
  min over steps. Composite η = `0.7` · η_inverse + `0.3` · η_trace.

## Per-candidate scores (Tier B)

| name | class | tok | \|z\| | BP | BP src | aff | η_inv | η_trace | η_comp | agg | Pareto |
|------|-------|----:|-----:|---:|:------:|----:|-----:|-------:|-------:|----:|:------:|
| `F043_literal` | F043_family | 5 | 1.64 | 1.000 | CAS | 0.000 | 0.528 | 0.363 | 0.478 | +0.36 | · |
| `F043_solve_L` | F043_family | 7 | 30.88 | 1.000 | CAS | 0.002 | 0.471 | 0.222 | 0.397 | -28.08 | · |
| `F043_three_term` | F043_family | 5 | 14.00 | 1.000 | CAS | 0.002 | 0.136 | 0.001 | 0.095 | -12.00 | · |
| `F043_full_BSD` | F043_family | 11 | 265.41 | 1.000 | CAS | 0.000 | 0.341 | 0.222 | 0.306 | -261.01 | · |
| `F043_solved_for_Sha` | F043_family | 11 | 23.15 | 1.000 | CAS | 0.003 | 0.021 | 0.000 | 0.015 | -18.75 | · |
| `mixed_Sha_j` | mixed | 3 | 0.83 | 1.000 | CAS | 0.950 | 1.000 | 1.000 | 1.000 | +0.37 | · |
| `mixed_L_disc` | mixed | 3 | 0.17 | 1.000 | CAS | 0.032 | 1.000 | 1.000 | 1.000 | +1.03 | · |
| `offbasis_j_disc` | off_basis | 3 | 0.49 | 0.009 | L_B | 0.989 | 1.000 | 1.000 | 1.000 | +0.71 | ✓ |
| `offbasis_jsq_disc` | off_basis | 5 | 0.96 | 0.004 | L_B | 0.031 | 0.318 | 0.500 | 0.373 | +1.04 | ✓ |
| `offbasis_j_jPlusDisc` | off_basis | 5 | 51.34 | 0.009 | L_B | 0.989 | 0.905 | 0.133 | 0.674 | -49.34 | · |
| `mixed_bag` | mixed | 7 | 0.16 | 0.074 | L_B | 0.950 | 0.176 | 0.018 | 0.129 | +2.64 | · |
| `offbasis_j_L` | mixed | 3 | 0.71 | 1.000 | CAS | 0.950 | 1.000 | 1.000 | 1.000 | +0.49 | · |
| `stress_exp_logSha` | stress_cas | 5 | 1.67 | 0.935 | L_B | 0.001 | 1.000 | 1.000 | 1.000 | +0.33 | · |
| `stress_nested_basis` | stress_cas | 9 | 18.58 | 1.000 | CAS | 0.000 | 0.551 | 0.000 | 0.386 | -14.98 | · |
| `stress_quadratic_basis` | stress_cas | 5 | 0.82 | 1.000 | CAS | 0.003 | 1.000 | 0.500 | 0.850 | +1.18 | · |

## CAS Layer C activations

**10 of 15 candidates decided by CAS Layer C.**

| name | E_A marker | E_B marker | reduced_to |
|------|-----------|-----------|-----------|
| `F043_literal` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |
| `F043_solve_L` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |
| `F043_three_term` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |
| `F043_full_BSD` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |
| `F043_solved_for_Sha` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |
| `mixed_Sha_j` | linear_in_basis | not_in_linear_basis | E_A:linear_in_basis |
| `mixed_L_disc` | linear_in_basis | not_in_linear_basis | E_A:linear_in_basis |
| `offbasis_j_L` | not_in_linear_basis | linear_in_basis | E_B:linear_in_basis |
| `stress_nested_basis` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |
| `stress_quadratic_basis` | linear_in_basis | linear_in_basis | E_A:linear_in_basis; E_B:linear_in_basis |

## Top 5 by aggregate

1. `F043_full_BSD` (F043_family) — agg=-261.01, |z|=265.41, BP=1.000 (CAS_Layer_C), **✗ NOT on Pareto**
2. `offbasis_j_jPlusDisc` (off_basis) — agg=-49.34, |z|=51.34, BP=0.009 (Layer_B_linear), **✗ NOT on Pareto**
3. `F043_solve_L` (F043_family) — agg=-28.08, |z|=30.88, BP=1.000 (CAS_Layer_C), **✗ NOT on Pareto**
4. `F043_solved_for_Sha` (F043_family) — agg=-18.75, |z|=23.15, BP=1.000 (CAS_Layer_C), **✗ NOT on Pareto**
5. `stress_nested_basis` (stress_cas) — agg=-14.98, |z|=18.58, BP=1.000 (CAS_Layer_C), **✗ NOT on Pareto**

## Pareto front (substrate-value triple)

- `offbasis_j_disc` (off_basis) — novelty=0.991, usefulness=0.989, faithfulness=1.000
- `offbasis_jsq_disc` (off_basis) — novelty=0.996, usefulness=0.031, faithfulness=0.373

## Disagreement

- F043_family in top-5 by aggregate: **3 / 5**
- F043_family on Pareto front: **0 / 2**

## η_trace diagnostic — where η_trace and η_inverse disagree

Differences greater than 0.2 between the two reconstructability
signals are surfaced for inspection. Disagreement is informative —
it localizes which kind of information loss the candidate has.

- `F043_solve_L` — η_inverse=`0.471`, η_trace=`0.222` (diff `0.25`)
- `offbasis_j_jPlusDisc` — η_inverse=`0.905`, η_trace=`0.133` (diff `0.77`)
- `stress_nested_basis` — η_inverse=`0.551`, η_trace=`0.000` (diff `0.55`)
- `stress_quadratic_basis` — η_inverse=`1.000`, η_trace=`0.500` (diff `0.50`)

## Verdict notes

Tier B does not break v2's verdict; it tightens it. CAS Layer C now provides explicit symbolic provenance for basis-projection decisions on most F043-family candidates. η_trace adds a complementary signal to η_inverse.

**Tier B implementation gates close. Tier C (gen_11 merger, TRG implementation) remains gated on Tink 3 (full-grammar empty-niche scan) producing real VACUUM signals and auto-descriptor candidates.**
