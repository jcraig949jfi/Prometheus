# Deep Research Report #141: F-isocrystal Newton Stratification at LMFDB Scale

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** p-adic Hodge theory (crystalline channel)
**Companion:** Batch 6 #103 (Newton stratification, de Rham channel)

## 1. Problem Statement

Let X/F_p be a smooth proper variety (here, the reduction of an abelian variety A/Q at a prime p of good reduction) and let H = H^i_cris(X/W(F_p))[1/p] be its rational crystalline cohomology with the absolute Frobenius F. The pair (H, F) is an **F-isocrystal** over K_0 = W(F_p)[1/p]. Dieudonne-Manin classifies F-isocrystals over an algebraically closed residue field as direct sums of simple objects E_{s/r} of slope s/r in Q cap [0,1] (for the abelian-variety case, slopes lie in [0,1] with symmetry s <-> 1-s by Poincare duality).

The **Newton polygon** N(X) is the lower-convex hull of the multiset of slopes (s_i, multiplicities). The **Hodge polygon** H(X) is determined by the Hodge numbers h^{p,q}. **Mazur's inequality** (Katz 1979) states N(X) lies on or above H(X) with the same endpoints. The **Newton stratum** N_nu in A_g tensor F_p of fixed Newton polygon nu has expected codimension given by Rapoport-Richartz:

  codim(N_nu) = #{ lattice points strictly between nu and the Hodge polygon }.

For g=2 abelian surfaces the strata are: ordinary (slopes 0,0,1,1; codim 0), p-rank-1 (0,1/2,1/2,1; codim 1), supersingular (1/2,1/2,1/2,1/2; codim 2). The hypothesis: at LMFDB scale the **observed density** matches Rapoport-Richartz codimension weights p^{-codim(nu)} (modulo Hecke-orbit equidistribution); structural deviation is a Voloch-style "Newton-above-Hodge" anomaly.

## 2. Literature

- **Dieudonne-Manin (1958, 1963):** classification of F-isocrystals over alg-closed residue field by slopes.
- **Katz, "Slope filtration of F-crystals" (1979):** Mazur's inequality; existence of Newton stratification.
- **Rapoport-Richartz (1996):** Newton stratification on Shimura varieties; codimension formula via mu-admissibility.
- **Oort (2000):** Newton-polygon strata in A_g are non-empty, equidimensional, Hecke-stable.
- **Chai-Oort (2006, 2011):** Hecke-orbit conjecture; central leaves; equidistribution within strata.
- **Viehmann (2013):** affine Deligne-Lusztig varieties — refines codim formula and predicts irreducibility.
- **Hodge-Newton conjecture:** decomposition when N has a break point on H; proved by Katz (1979) for crystals, Mantovan (2008) for Shimura cases. **Status:** open in full generality at non-minuscule p.

## 3. LMFDB Data

- `av_fq_isog`: abelian-variety isogeny classes over F_q. Columns: `label`, `g`, `q`, `p_rank`, `slopes` (rational slope multiset, text), `newton_polygon`, `polynomial` (L-poly coefficients), `is_simple`, `is_supersingular`. ~500K rows; ~5K per (g=2, fixed p).
- `g2c_curves`: genus-2 curves over Q. Columns: `label`, `eqn_coeffs`, `cond`, `disc`, `euler_factors` (list of L-poly coefficients indexed by p <= 100). Newton slopes recovered from L_p(T) by p-adic Newton polygon of reverse polynomial.
- `abvar_fq_search`: precomputed search index over av_fq_isog with `slopes`, `p_rank`, `angle_numbers`.
- `nf_fields`: residue-degree bookkeeping if reductions are pulled back to F_{p^f}.

After grouping g2c_curves by (p, slope-vector) for p in {2,3,5,7,11,13}: expect ~5K curves x 6 primes = 30K reductions; per prime, three slope buckets for g=2, so ~1.5K per (p, nu) — sufficient for chi-square at 2 d.f. and KS on slope-coordinate density.

## 4. Test Design

**Step 1.** Postgres: `SELECT label, euler_factors, disc FROM g2c_curves WHERE cond < 1000000` (~66K curves; restrict to good reduction at p via `disc % p != 0`).

**Step 2.** For each prime p in {2,3,5,7,11,13}: extract L_p(T) from `euler_factors[p_index]`. In Sage:
```
R.<T> = QQ[]
Lp = R(coeffs)
slopes = Lp.newton_polygon(p).slopes()  # multiset in [0,1]
```
Symmetrize via functional equation; bucket by Newton vector nu.

**Step 3.** Cross-validate against `av_fq_isog.slopes` for the corresponding isogeny class (match by L-poly coefficients -> `polynomial`).

**Step 4.** Observed density: f_obs(nu) = #{curves with Newton nu at p} / total. Predicted: f_RR(nu) = p^{-codim(nu)} / Z_p, with Z_p the local partition function over the three g=2 strata.

**Step 5.** Tests:
- Chi-square: f_obs vs f_RR per prime, 2 d.f.
- KS on the middle-slope coordinate (the only free coordinate for g=2 with symmetry).
- Permutation null: randomly reassign slope vectors across curves; recompute chi-square; require observed p-value < 5th percentile of null.

**Step 6.** Stratify residuals by isogeny-class invariants (`p_rank`, `is_supersingular`, conductor class) to detect Voloch-style structural anomalies.

## 5. Falsification

- **Trivial confirmation:** chi-square p > 0.1 at all six primes, KS not significant -> Rapoport-Richartz holds at LMFDB scale; report as calibration anchor.
- **Structural deviation:** systematic excess of supersingular at small p (e.g., p=2,3) beyond p^{-2} prediction, persistent after conductor stratification -> **Newton-above-Hodge anomaly**, candidate V4 phoneme.
- **Strong kill:** observed slope distribution matches uniform (not Rapoport-Richartz) -> either LMFDB `slopes` column is miscomputed, or stratification is dominated by selection bias in g2c sampling.
- **Null sanity:** permuted-slope chi-square must reject at < 1% to ensure power. If null also fits Rapoport-Richartz, the prediction is vacuous at this scale.

## 6. Budget

~8 hours. Postgres pull from `av_fq_isog` and `g2c_curves` (~30 min, cached locally per `reference_lmfdb_postgres.md`). Sage Newton-polygon extraction: 30K x 6 primes ~ 180K polygons, ~2h on a single core (vectorize via PARI `nfnewtonpoly` for ~5x). Rapoport-Richartz codim table for g=2 is closed-form (no compute). Chi-square + KS + permutation null (1000 reps): ~1h. Stratified residual analysis: 2h. Writeup: 2h.

## 7. Expected Outcome

Pairs with Batch 6 #103 (de Rham Newton stratification) to span the **Hodge <-> crystalline channels** of the same underlying motive. #103 measures the Hodge polygon side; #141 measures the crystalline Frobenius side; their ratio at each curve gives a per-object "Mazur gap" — a direct quantitative measure of Newton-above-Hodge that Aporia can use as a void-detection coordinate. Curves with anomalous gap localize **motivic cells where p-adic Hodge comparison degenerates** (semistable-but-not-crystalline, or higher Hodge-Tate weight collisions). These cells are exactly the territory the silent-islands work flags as crystalline dark zones — the crystalline complement to #103's de Rham void map.

Prior: Rapoport-Richartz holds in expectation but tail behavior at small p is under-tested. A clean structural deviation at p=2 or p=3 — even at 2-sigma — would be the first LMFDB-scale empirical handle on the Hodge-Newton conjecture and would seed a candidate **V4 phoneme** alongside Megethos. Calibration value alone (a working LMFDB -> slope-vector pipeline) unlocks every downstream crystalline test on the Aporia roadmap.

**Word count: 788**
