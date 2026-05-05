# Tink 1 results — 2026-04-25

**Verdict: PASS — Tink 3 implementation gates open**

## Setup

- Grammar: minimal — atoms `{rank, root_number}`, ops `{add, sub, mul, neg, scalar_mul, iverson_eq}`, max depth `3`
- Population: `50` individuals × `10` generations = `500` evals/seed
- Seeds: `[0, 1, 2]` (≥ `2` of 3 must pass)
- Aggregate: `α · L_expr − β · f003_score + penalty_missing_atom`  (α=`0.01`, β=`1.0`, penalty=`100.0`)
- Pre-registered shuffled-null margin: `0.05` above `null p99` over `200` shuffles
- Allowed canonical form (§0.2): output ≡ 1 across all rows AND atom set == `{rank, root_number}`

## Hard pass criteria (§0.4)

1. **Framing B compliance**: PASS
2. **Multi-seed reproducibility**: PASS — 3/3 seeds had F003-equivalent in top-5
3. **Semantic equivalence**: PASS
4. **Shuffled-null margin**: PASS — 3/3 seeds clear margin
5. **Proxy-leakage audit**: VACUOUS (Tink 1 minimal grammar; deferred to Tink 3)

## Per-seed results

### Seed 0

**F003 in top-5: YES** → `[(root_number * 0.0) == [rank == root_number]]`

Null check: candidate F003 = `1.0000`, null p99 = `0.7710`, p95 = `0.7660`, null mean = `0.7508`, margin = `+0.2290`, passes = **True**

Top-5 candidates:

| # | tree | aggregate | f003_score | tokens |
|--:|------|----------:|-----------:|-------:|
| 1 | `[(root_number * 0.0) == [rank == root_number]]` | -0.9300 | 1.0000 | 7 |
| 2 | `[(rank - rank) == [rank == root_number]]` | -0.9300 | 1.0000 | 7 |
| 3 | `[(0.0 * 0.0) == [rank == root_number]]` | -0.9300 | 1.0000 | 7 |
| 4 | `[(0.0 * -root_number) == [rank == root_number]]` | -0.9200 | 1.0000 | 8 |
| 5 | `[(-0.0 * rank) == [rank == root_number]]` | -0.9200 | 1.0000 | 8 |

GP history (best aggregate per generation):

| gen | best_aggregate | best_f003 | best_tree |
|----:|---------------:|----------:|-----------|
| 0 | -0.4500 | 0.5000 | `(0.5*rank + root_number)` |
| 1 | -0.4500 | 0.5000 | `(0.5*rank + root_number)` |
| 2 | -0.8800 | 1.0000 | `[(-0.0 * (root_number - 0.0)) == [0.5*rank == root_number]]` |
| 3 | -0.8800 | 1.0000 | `[(-0.0 * (root_number - 0.0)) == [0.5*rank == root_number]]` |
| 4 | -0.9000 | 1.0000 | `[(-0.0 * (root_number - 0.0)) == [rank == root_number]]` |
| 5 | -0.9000 | 1.0000 | `[(-0.0 * (root_number - 0.0)) == [rank == root_number]]` |
| 6 | -0.9000 | 1.0000 | `[(-0.0 * (root_number - 0.0)) == [rank == root_number]]` |
| 7 | -0.9100 | 1.0000 | `[(-0.0 * -root_number) == [rank == root_number]]` |
| 8 | -0.9200 | 1.0000 | `[(0.0 * -root_number) == [rank == root_number]]` |
| 9 | -0.9200 | 1.0000 | `[(0.0 * -root_number) == [rank == root_number]]` |

### Seed 1

**F003 in top-5: YES** → `(root_number - -2.0*rank)`

Null check: candidate F003 = `1.0000`, null p99 = `0.5280`, p95 = `0.5240`, null mean = `0.5001`, margin = `+0.4720`, passes = **True**

Top-5 candidates:

| # | tree | aggregate | f003_score | tokens |
|--:|------|----------:|-----------:|-------:|
| 1 | `(root_number - -2.0*rank)` | -0.9500 | 1.0000 | 5 |
| 2 | `(root_number - -2.0*rank)` | -0.9500 | 1.0000 | 5 |
| 3 | `(root_number - -2.0*rank)` | -0.9500 | 1.0000 | 5 |
| 4 | `(root_number - -2.0*rank)` | -0.9500 | 1.0000 | 5 |
| 5 | `(root_number - -2.0*rank)` | -0.9500 | 1.0000 | 5 |

GP history (best aggregate per generation):

| gen | best_aggregate | best_f003 | best_tree |
|----:|---------------:|----------:|-----------|
| 0 | -0.8700 | 1.0000 | `([-2.0*rank == 0.5*root_number] - ((-1.0 * 2.0) + 1.0))` |
| 1 | -0.8900 | 1.0000 | `[(rank - rank) == ([root_number == 1.0] * [rank == root_number])]` |
| 2 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 3 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 4 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 5 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 6 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 7 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 8 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |
| 9 | -0.9500 | 1.0000 | `(root_number - -2.0*rank)` |

### Seed 2

**F003 in top-5: YES** → `((rank + rank) + root_number)`

Null check: candidate F003 = `1.0000`, null p99 = `0.5380`, p95 = `0.5280`, null mean = `0.5008`, margin = `+0.4620`, passes = **True**

Top-5 candidates:

| # | tree | aggregate | f003_score | tokens |
|--:|------|----------:|-----------:|-------:|
| 1 | `((rank + rank) + root_number)` | -0.9500 | 1.0000 | 5 |
| 2 | `((rank + rank) + root_number)` | -0.9500 | 1.0000 | 5 |
| 3 | `((rank + rank) + root_number)` | -0.9500 | 1.0000 | 5 |
| 4 | `((rank + rank) + root_number)` | -0.9500 | 1.0000 | 5 |
| 5 | `((root_number + rank) + rank)` | -0.9500 | 1.0000 | 5 |

GP history (best aggregate per generation):

| gen | best_aggregate | best_f003 | best_tree |
|----:|---------------:|----------:|-----------|
| 0 | -0.4300 | 0.5000 | `([rank == (rank - root_number)] - root_number)` |
| 1 | -0.4300 | 0.5000 | `([rank == (rank - root_number)] - root_number)` |
| 2 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 3 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 4 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 5 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 6 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 7 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 8 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |
| 9 | -0.9500 | 1.0000 | `((rank + rank) + root_number)` |

## Notes on criterion 5 (proxy-leakage)

The proxy-leakage audit defined in `tink_3_design_questions.md` v3 §5.6 conditional-residualizes a candidate's features against the identity basis, recomputes its affordance, and rejects candidates whose affordance comes from basis-atom proxies.

For Tink 1's minimal grammar (atoms `{rank, root_number}`), there are no off-basis atoms; the basis IS the F003 identity itself. The audit is vacuous: any candidate that captures F003 will register 100% leakage by construction. The audit fires only when a richer atom set creates the possibility of basis-proxy candidates, which is the Tink 3 setting. Per §0.4 design caveat, the audit is documented as run, not gating, for Tink 1.

## What this verdict implies

**v3 design doc §0.4 hard criteria passed on Tink 1.** GP under Framing B with the minimal grammar can rediscover F003 within the pre-registered budget. The instrument is validated for the central composition (search + Framing B + scoring) at minimum-viable scale.

**Next step per design doc Status §:** pin `Q_EC_R012_D5@v0` (or `Q_EC_R01_D5@v0` if rank-2 fallback triggers per §4.5.1), run coefficient sub-sweep, then Tink 3 implementation.
