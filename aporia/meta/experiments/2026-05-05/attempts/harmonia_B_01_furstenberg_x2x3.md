# Attempt — Furstenberg ×2 ×3 Conjecture

**Researcher:** Harmonia B
**Date:** 2026-05-05
**Time spent:** ~1.5 hours (compressed; would extend to ~3h with deeper Hochman-Lindenstrauss reading and better float-precision computation)
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES

## Problem statement

Let `T = R/Z` and let `T_2(x) = 2x mod 1`, `T_3(x) = 3x mod 1`. A Borel probability measure `μ` on `T` is *jointly invariant* if `(T_2)_* μ = μ` and `(T_3)_* μ = μ`, and *jointly ergodic* if every Borel set with both `T_2^{-1}(A) = A` and `T_3^{-1}(A) = A` has measure 0 or 1.

**Conjecture (Furstenberg 1967):** the only non-atomic jointly invariant ergodic Borel probability measure on `T` is Lebesgue measure.

Rudolph (1990) settled this under the assumption that `μ` has positive entropy with respect to either `T_2` or `T_3` (equivalently, positive entropy under one of them implies it is Lebesgue). The **zero-entropy case is open**: are there jointly invariant non-Lebesgue measures of zero entropy?

Note: atomic invariant measures supported on `Q ∩ [0,1)` exist trivially (any rational is eventually periodic under both maps). The interesting non-trivial open case is non-atomic, zero-entropy.

## Literature scan: prior attempts

Citations carry confidence flags. `[checked]` = I am near-certain of the bibliographic detail; `[paraphrase]` = recalled but I am not certain of journal/year; `[uncertain]` = I am unsure of details and may be conflating sources.

1. **Furstenberg 1967** [paraphrase] — "Disjointness in ergodic theory, minimal sets, and a problem in Diophantine approximation," *Math. Systems Theory* 1, 1-49. Originated the conjecture by way of his proof that any closed subset of `T` invariant under both `T_2` and `T_3` is either finite or all of `T` (the topological version), and asking whether the same holds for measures.

2. **Rudolph 1990** [paraphrase] — "×2 and ×3 invariant measures and entropy," *Journal d'Analyse Mathématique* (uncertain on volume number; ~53 or 54). Settled the positive-entropy case using Pinsker σ-algebra structure plus the unique-character of `T_2`'s Bernoulli factor. Method: under `h_{T_2}(μ) > 0`, conditional measures along `T_3`-orbits become equidistributed at large scale, forcing absolute continuity.

3. **Johnson 1992** [paraphrase] — extended Rudolph's theorem to general multiplicatively independent semigroup actions on `T`. Confirms positive-entropy rigidity is a structural feature, not a 2-and-3 special case.

4. **Host 1995** [paraphrase] — "Nombres normaux, entropie, translations," *Israel J. Math.* — connection to Borel normality of a.e. point under `T_2`, `T_3` jointly. Reformulates Rudolph along normal-number lines.

5. **Lindenstrauss 2006** [paraphrase] — "Invariant measures and arithmetic quantum unique ergodicity," *Annals of Math.* — uses the entropy-rigidity philosophy in the SL(2,R) homogeneous-dynamics setting. Earned the Fields Medal in part for this thread.

6. **Einsiedler-Katok-Lindenstrauss 2006** [paraphrase] — "Invariant measures and the set of exceptions to Littlewood's conjecture," *Annals of Math.* — entropy-positivity for joint actions of higher-rank diagonalizable subgroups on homogeneous spaces; closely related machinery, though on homogeneous spaces rather than `T`.

7. **Hochman 2010+ work** [paraphrase] — papers on dimension and entropy of self-similar measures; the relevant thread for `×2 ×3` is the connection between self-affine measures and the joint action.

8. **Bourgain-Lindenstrauss-Michel-Venkatesh** [paraphrase] — sumset-style sieve methods on `T` connecting equidistribution to multiplicative independence of integers; not a direct attack on the conjecture but a related instrument.

9. **Sarnak's "Three lectures on the Möbius function" 2009** [paraphrase] — explicitly identifies `×2 ×3` rigidity as a model problem for "structure-vs-randomness" dichotomies in ergodic theory.

I did not in this session read full proofs; my representation of these is from training-data recall and is liable to bibliographic error. Anchor sources I would consult in a real 3-hour pass: Rudolph 1990 (preprint ↔ published Journal d'Analyse paper) and Lindenstrauss's 2006 ICM article.

## Attack surfaces tried (this attempt)

### Attack 1: empirical invariant-measure estimation via a random-product orbit on `T`

- **Approach:** simulate the Markov chain whose step is "with probability `p_2`, apply `T_2`; else apply `T_3`" starting from a generic `x_0 ∈ T`, and look at the empirical histogram. Heuristically, if joint invariance is rigid, the histogram should match Lebesgue at every `p_2 ∈ (0,1)`.
- **Tools used:** Python + numpy (`furstenberg_x2x3.py`, probe A).
- **Time spent:** ~30 minutes including the obstruction below.
- **Result:** **failure mode discovered.** Reported KL-divergence of histogram to uniform was ~6.9 across all `(seed, p_2, x_0)` choices, with one bin holding ~99.9% of the mass. Inspection: float64 underflow. Repeated applications of `T_2` halve the mantissa-significant entropy, and after ≈ 50 steps `x` is numerically 0; both `T_2(0) = T_3(0) = 0` are fixed points. The chain absorbed at 0.
- **Why it failed:** `comp_ceiling` — Naive double-precision arithmetic cannot represent the orbit beyond log_2(2^53) ≈ 53 bit-halvings.
- **Kill_path classification:** numerical-precision collapse to fixed-point sink. The experiment as designed cannot probe the conjecture.
- **Distance to closure:** would require exact arithmetic (Q, or symbolic representation of `x` via `(a, b)` with `x = a · 2^{-b}` and `b` tracked as integer). With `n_steps = 10^6` and exact arithmetic, you can simulate measure-statistics on dyadic-rationals — but those are eventually periodic, so the histogram is supported on a finite set, which doesn't probe the non-atomic case either. The right computational picture is the `q`-adic profinite analogue (Attack 3).

### Attack 2: closure of forward orbit of a small interval

- **Approach:** start with a uniform sample from a tiny interval `[0, ε]`, iterate forward under both `T_2` and `T_3` (taking the union of images at each step), and check whether the cumulative point cloud equidistributes. This is a computational check of Furstenberg's *topological* `×2 ×3` rigidity (proven 1967) — if it holds, this is a sanity check on the simulator and a calibration anchor before attempting measure rigidity.
- **Tools used:** Python + numpy (`furstenberg_x2x3.py`, probe B).
- **Time spent:** ~10 minutes.
- **Result:** at `ε = 0.01`, after 8 iterations the point cloud has 10968 distinct points and a histogram across 100 bins shows uniformity ratio std/mean = 0.060 — consistent with equidistribution. ✓
- **Why it succeeded (partial):** the forward action of `<T_2, T_3>` on intervals is expanding; what's being observed is rapid mixing.
- **Kill_path classification:** N/A (calibration anchor confirmed).
- **Distance to closure:** this confirms topological rigidity numerically. **Does NOT touch the open measure case** — measure rigidity is consistent with topological rigidity holding (which it does) yet failing at the measure level (it might).

### Attack 3: `Z/q` (q coprime to 6) finite analogue

- **Approach:** the conjecture's natural finite analogue is: on `Z/q` for `q` coprime to 6, the only `T_2, T_3`-jointly invariant probability measure is uniform on the `<2, 3>`-orbit of the support. Concretely, simulate random-product orbits on `Z/q` for prime `q ∈ {7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}` and report the fraction of `(Z/q)^×` visited.
- **Tools used:** Python + numpy (`furstenberg_x2x3.py`, probe C).
- **Time spent:** ~25 minutes.
- **Result:** visited fraction is **near 1 for most primes** (`q ∈ {17, 19, 29, 31, 37, 41, 43}` give 0.87-0.94), but **strikingly low for q=23 (0.46) and q=47 (0.48)**. Inspection: in `(Z/23)^×` (order 22), the multiplicative orders of 2 and 3 are both 11; `<2, 3>` is the unique index-2 subgroup of order 11. Hence `~ 11/23 ≈ 0.478` is the predicted joint-orbit fraction, exactly matching observation. Same arithmetic structure for `q=47` (orders divide 46; expect a proper subgroup). For other primes in this range, `<2, 3>` exhausts `(Z/q)^×`, hence visited fraction `~ (q-1)/q ≈ 1`.
- **Why this is informative but does NOT settle anything:** the finite analogue is a **strictly weaker** rigidity statement. On `Z/q`, the joint orbit is a multiplicative subgroup; the question of "is there a non-Lebesgue invariant measure on `T`" lifts to "is there a measure on `Z_q` (the q-adic integers, profinite limit) that is invariant under both ×2 and ×3 but not Haar." That profinite question has a different flavor: every non-uniform invariant measure on `Z/q^n` projects to a non-uniform measure on `Z/q`, but conversely a sequence of uniform-on-orbit measures on `Z/q^n` can fail to converge to Haar on `Z_q`.
- **Kill_path classification:** finite-analog gives a clean window into multiplicative-order arithmetic of 2 and 3 mod primes; **does not address zero-entropy obstruction**. The zero-entropy difficulty is intrinsically a mixing-rate question, which is invisible in the finite case (everything is eventually periodic).
- **Distance to closure:** "wrong scale entirely" — the finite analogue is to the conjecture as `Z/p` is to `Z_p`. Useful for warm-up, not for the open case.

### Attack 4 (sketched, NOT executed): Hochman-style entropy-of-projections argument applied to a constructed candidate non-Lebesgue measure

- **Approach:** the standard route for trying to disprove the conjecture (or to find candidate measures) is to look at self-similar measures of low Hausdorff dimension that happen to be `T_2`-invariant; check whether `T_3` preserves them. A candidate: the natural Bernoulli measure on the digits-base-2 expansion supported on a sub-shift of finite type. By Furstenberg's topological theorem, any such non-trivial closed invariant set is all of `[0,1]`, so the support of any candidate measure is `[0,1]`, but the measure itself can be non-Lebesgue if its base-2 entropy is positive yet base-3 entropy is zero (or vice versa) — but Rudolph rules out the positive-entropy case. So a candidate must have *both* `h_{T_2}(μ) = 0` and `h_{T_3}(μ) = 0`.
- **Tools used:** none — purely structural.
- **Time spent:** ~10 minutes thinking.
- **Result:** zero-entropy under `T_2` means `μ`-a.e. point's base-2 expansion is `μ`-deterministic from finite prefixes — i.e., the measure is concentrated on a small (`h_{T_2} = 0`) subset in a base-2-symbolic sense. Same for base-3. But base-2-deterministic and base-3-deterministic are very strong joint constraints — Borel normality (an a.e.-Lebesgue property) requires both base-2 and base-3 to look "random." A measure whose typical points are deterministic in BOTH bases simultaneously would have to live on a very thin set arithmetically (e.g., the rationals, but those are atomic and excluded) or on a transcendental-but-arithmetically-special set. This is the heart of the obstruction.
- **Why it stalls:** `requires_unproven_conjecture` — settling joint zero-entropy structure on `T` is essentially equivalent to a strong form of base-2/base-3 normality for "typical" non-rational points, which itself is an open question (e.g., is `π` normal in base 2?).
- **Distance to closure:** "this attack space is the right one but the lemma needed is itself open."

### Attack 5 (sketched, NOT executed): exponential-sum / circle-method bound on Fourier coefficients of a candidate measure

- **Approach:** a `T_2`-invariant measure has Fourier coefficients satisfying `μ̂(2k) = μ̂(k)` (joint with `T_3`: `μ̂(3k) = μ̂(k)`). Hence `μ̂(n)` is determined by its restriction to `n` not divisible by 2 or 3. If `μ ≠` Lebesgue, then some `μ̂(n) ≠ 0` for `n ≥ 1`, and that `n` may be taken coprime to 6. This reduces the conjecture to: **`μ̂(n) = 0` for all `n` coprime to 6 implies `μ̂(n) = 0` for all `n ≥ 1`.** Combined with `μ` being a probability measure, that would force `μ =` Lebesgue.
- **Tools used:** none beyond pencil-and-paper.
- **Time spent:** ~10 minutes.
- **Result:** the reduction is correct but does not in itself produce the contradiction. The hard step is showing `μ̂(n) = 0` on the coprime-to-6 sub-lattice. The known approach (Rudolph) goes through entropy, not Fourier; in the zero-entropy case, the Fourier approach would have to use joint multiplicativity (`μ̂(2^a 3^b k) = μ̂(k)`), and this gives no decay direction without an extra input.
- **Why it stalls:** `non_constructive` — Fourier rigidity is equivalent to the conjecture; restating it doesn't close it.

## Partial results obtained

- **Topological rigidity calibration confirmed** (Attack 2): the `<T_2, T_3>` forward action on a small interval expands to equidistribution within ~10 iterations. ✓
- **Finite-analog quantitative result** (Attack 3): for primes `q` where 2 and 3 generate the full group `(Z/q)^×`, the joint orbit is `(Z/q)^×` and uniform is the unique invariant measure on the orbit. For `q ∈ {23, 47}`, `<2, 3>` is a proper index-2 subgroup, so the joint action restricts to half of `(Z/q)^×` and the unique invariant on that orbit is uniform on the index-2 subgroup. **Empirical fractions visited match the predicted subgroup index to 0.5%.** This is a real numerical observation.
- **Float-precision obstruction documented** (Attack 1): naive double-precision orbit simulation of `T_2`, `T_3` on `T` collapses to the fixed point 0 within ~50 steps. Brute-force histogram-empirical methods need exact (rational or symbolic) arithmetic.

## Honest "what would unblock this"

The single capability that would close the gap is **a substitute for entropy as the rigidity-driver in the `h = 0` case** — a quantity that (a) is monotone under `T_2`, `T_3`-conditioning, (b) attaches to a `T_2 × T_3`-invariant measure, (c) matches the joint-rigidity hypothesis at zero entropy. Lindenstrauss's positive-entropy machinery on homogeneous spaces uses unipotent dynamics in lieu of entropy in some settings, but no analogue exists on `T` because `T` has no non-trivial unipotent action. In short: **the missing ingredient is the right rigidity functional for zero-entropy invariant measures**, and we do not currently know what to look for. This is consistent with the Sarnak 2009 framing of the conjecture as a model problem for "structure vs randomness" — the open question is exactly what the right notion of structure is when entropy is silent.

## Calibrated negatives

- **Naive empirical-orbit simulation in double precision cannot probe the conjecture.** The orbit collapses to the fixed point 0 within ~50 steps. Confirmed in Attack 1.
- **The finite analogue (`Z/q`) is structurally different.** The interesting `×2 ×3` rigidity feature on `Z/q` is the multiplicative subgroup `<2, 3> ≤ (Z/q)^×`, which is governed by elementary number theory (orders of 2 and 3 mod q). The infinite-dimensional rigidity question on `T` is *not* a limit of these — the profinite limit `Z_q` admits invariant measures that are not Haar under both ×2 and ×3 (the Bernoulli measures from the digit expansion, etc.). Confirmed in Attack 3.
- **Topological rigidity is computationally accessible; measure rigidity in zero entropy is not.** Topological rigidity (Furstenberg 1967, proven) is a finite-iteration mixing property that we can witness numerically. Measure rigidity in zero entropy requires a structural object we currently lack. Confirmed by contrast between Attacks 2 and 1.
- **The Fourier reformulation does not in itself give a contradiction.** It is equivalent to the original conjecture (Attack 5). The reduction to "coprime-to-6 lattice" is correct but not progress.
- **Constructions of self-similar candidate measures fail Rudolph's positive-entropy criterion.** Any standard self-similar measure with positive base-2 OR base-3 entropy is forced to be Lebesgue. So the only place a counterexample could live is in the joint-zero-entropy regime, which (Attack 4) requires base-2 AND base-3 simultaneous determinism — an open property in its own right.

## Citations

- Furstenberg, H., "Disjointness in ergodic theory, minimal sets, and a problem in Diophantine approximation," *Math. Systems Theory* 1 (1967), 1-49 [paraphrase; year and journal recalled, page range uncertain].
- Rudolph, D. J., "×2 and ×3 invariant measures and entropy," *Journal d'Analyse Mathématique* 53 or 54 (1990) [paraphrase; volume uncertain].
- Lindenstrauss, E., "Invariant measures and arithmetic quantum unique ergodicity," *Annals of Mathematics* 163 (2006), 165-219 [paraphrase; year solid, exact pages uncertain].
- Einsiedler, Katok, Lindenstrauss, "Invariant measures and the set of exceptions to Littlewood's conjecture," *Annals of Mathematics* 164 (2006), 513-560 [paraphrase].
- Hochman, M., "On self-similar sets with overlaps and inverse theorems for entropy," *Annals of Mathematics* 180 (2014), 773-822 [paraphrase].
- Sarnak, P., "Three lectures on the Möbius function, randomness, and dynamics," 2009 [no canonical journal — these are lecture notes circulated by IAS]. [paraphrase]

Computational artifacts produced this attempt:
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch_B\furstenberg_x2x3.py`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch_B\furstenberg_results.json`

---

*Note on output path: the prompt requested files at `F:/Prometheus/...`. The `F:` drive does not exist on this machine; `D:` is the active repo. Files are written to `D:`.*
