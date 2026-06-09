# Phase 0 result — kill-space effective dimensionality (EXPERIMENTAL)

**Run:** 2026-05-27, `harmonia/experiments/phase0_killspace_dim.py`, seed 20260527, offline
(Mahler via `techne.lib.mahler_measure`, irreducibility via sympy). Degree-10 {-1,0,1} polynomials.

## Question
The native-pilot audit (`kv_basis_dim.py`) measured the KillVector basis at **effective dim = 1.0**
(`out_of_band` 99.93%, all 11 other components dead). Is that collapse fundamental, or an artifact?

## Method
Two populations (1500 each): RANDOM (gross-miss baseline) and NEAR-MISS (lowest-M tail + Lehmer/Salem
seeds). For each polynomial compute a **multi-gate** KillVector — every falsifier fires with a continuous
margin (not first-failing). Report per-component liveness, correlation, participation ratio (effective
dim), and confound-residual eff-dim (after partialling out the `out_of_band`/M axis).

## Result

| population | M median | eff-dim | confound-residual eff-dim |
|---|---|---|---|
| RANDOM (gross-miss) | 2.17 | **3.08** | 3.75 |
| NEAR-MISS (low-M tail) | 1.62 | **3.51** | 3.43 |

- `out_of_band` and `F9_cyclotomic` correlate **r = 1.00** — they are the *same* M axis (both M minus a
  constant). Real distinct components: ~5; PR discounts the duplication to eff-dim ~3.
- Alive independent-ish axes: M (band/cyclotomic), reciprocity, irreducibility, F1_perm_null
  (corr −0.71/−0.47 with M — partially independent), F6 (weak). `F11_cross_val` is float-noise (dead).

## The reframe (honest reading — this changes the priority order)

1. **The rank-1 collapse was an instrumentation + construction artifact, NOT fundamental.** The native
   pilot was rank-1 because (a) its `DiscoveryEnv` enforces palindromicity → reciprocity dead by
   construction, and (b) it recorded *first-failing* / short-circuited at the band gate → the downstream
   11 falsifiers were never computed. Compute them all on a free population and eff-dim is ~3.
2. **The dominant lever is multi-gate instrumentation (#26), not the near-miss generator (#1).** RANDOM
   already reaches 3.08; near-miss adds only a modest lift (→3.51), and its confound-residual is actually
   *lower* (3.75→3.43). The doctrine's prediction was directionally right (deeper falsifiers do carry
   signal) but the mechanism is instrumentation, not population. **Priorities reorder accordingly.**
3. **The basis has built-in redundancy** (`out_of_band` ≡ `F9`, r=1). Catalog #24 (orthogonalization)
   is not optional — two of the live components are literally one axis.

## Caveats (self-dissent)
- Not byte-identical to the native pilot (degree-10/{-1,0,1} vs degree-14/wider; multi-gate vs
  first-failing). So this *explains* the pilot's rank-1, it doesn't contradict it. A multi-gate re-run on
  the pilot's actual degree-14 population would fully close it.
- Eff-dim ~3 is **multi-dimensional but modest** — ~3 effective directions among 5 distinct components;
  substantial residual correlation remains (a 3-D-ish space, not a rich high-D map).

## Verdict
**K2 GATE: PASS.** The kill-space is genuinely multi-dimensional once properly instrumented — the
meta-harness's substrate prerequisite (a behavior descriptor with eff-dim > 1) is satisfiable on this
domain. Proceed to Phase 1, but with corrected priorities: **multi-gate instrumentation first, basis
orthogonalization second, near-miss generation third.**
