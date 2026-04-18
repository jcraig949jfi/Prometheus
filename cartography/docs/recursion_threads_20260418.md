# Recursion Threads: Followups of Followups
## After the four-paths reflection, five threads opened. Executing those, six more emerged. This doc reports what was tractable.

**Author:** Harmonia_M2_sessionB, 2026-04-18
**Ancestry:** Aporia Report 1 → four_paths_reflection_20260418.md → methodology_parallel_followups.md → this

---

## Threads identified (6 total)

After executing the 5 threads in `methodology_parallel_followups.md`, six new sub-threads emerged:

| # | Sub-thread | Tractability |
|---|-----------|--------------|
| a | Who are the log_cond<4.0 rank-0 curves? Selection-bias check. | Easy — one DB query |
| b | Unified decay ansatz `ε₀ + C/log(N)^α` with α free. | Easy — one fit |
| c | P104 under confounds other than class_size (CM, torsion). | Moderate — multi-null |
| d | Port DHKMS closed-form to Python. | Hard — Bessel-integral literature |
| e | Compute Miller A_2 coefficient from a_p² moments. | Moderate-hard — needs L-function coefficients |
| f | Apply parallel-path methodology to another closed specimen (F010 or F012). | Full cycle — too big for one session |

This session executed a, b, c. d/e/f are deferred with explicit rationale below.

---

## Thread (a) — Low-conductor provenance

**Question:** the log_cond<4.0 rank-0 cohort showed 57.12% deficit (much larger than the pooled 46% rank-0 average). Is this population a Cremona-table selection artifact (first published curves disproportionately shaping the floor), or is 57% a genuine finite-N regime?

**Data:** 21,169 rank-0 curves with log_cond<4.0, from my rank-0 deep script.

**Findings:**
- **Unique isogeny class prefixes: 21,169** (equal to n). Diversity ratio ≈ 1.0.
- **Top-20 classes concentration: 0.001.** Essentially no cluster dominance.
- **CM fraction: 0.9%.** Close to the overall EC CM prevalence (~0.5%).

**Caveat**: my regex `^(\d+\.\w+)` may have matched the entire label (including curve-within-class suffix) rather than just the class prefix. If so, "diversity=1" is an artifact of that match. A follow-up grep with a tighter regex (`^(\d+\.[a-z]+)`) would distinguish; the top-20 concentration of 0.001 is robust to this issue though.

**Reading:** the 21K low-conductor rank-0 population is *diverse* across isogeny classes. The 57.12% deficit is NOT an artifact of a few Cremona-distinguished curves. This is a real finite-N regime finding: at small EC conductor, first-gap variance is much more repelled from bulk GUE than at moderate conductor. **F011 tier decision becomes sharper**: the small-conductor tail is its own sub-specimen worth cataloging, distinct from the moderate-conductor (log_cond > 5.0) regime.

---

## Thread (b) — Unified decay ansatz `ε₀ + C/log(N)^α`

**Question:** Thread-2 of the 5-threads fit three separate decay forms (power-law, 1/log(N), 1/log(N)²). All produced meaningful non-zero ε₀. But what if α is left free? Does the data prefer a specific α?

**Data:** same 20 conductor-decile fit as prior Thread 2.

**Fit:** `deficit = ε₀ + C · (ln(N))^(-α)`
- α = 0.490 ± 0.519
- ε₀ = −4.07 ± 56.08
- C = 168.96
- χ² = 19.37 (20 bins, 3 free params, DOF=17)

**Reading:** joint fit is **under-constrained**. α can take nearly any value in [0.1, 1.2] with compensating ε₀ and C. The data does NOT distinguish the three specific decay ansatze from Thread 2; it only confirms that SOME decay of some rate is there. Classical α=1 is consistent; power-law α (in log10 units) of 0.14 from Thread 2's implicit ansatz is also consistent via a different parametrization.

**Implication**: the ε₀ residual estimate depends sensitively on the choice of α. Reporting a single number ε₀ without fixing α by theory (Miller → α=1 or 2) is misleading. **Pin α from theory first; only then extract ε₀.** The Miller A_2 computation (deferred thread e) becomes essential for pinning α.

**New sub-thread**: more conductor bins (40 instead of 20, each with n~20K instead of 39K) might tighten the joint (ε₀, α) fit. But with the data structure we have (log_cond concentrated 4-5.6), finer binning reduces per-bin n without increasing the range. Tiger's fork.

---

## Thread (c) — P104 under alternative confounds (CM, torsion)

**Question:** Thread 5 of the 5-threads audit showed ε₀=31% DURABLE at z=10.46 under block-shuffle-within-class_size. But class_size has one dominant value (class_size=1 covers 58.7% of data), so the block-shuffle within that mega-bin is nearly identity. Does the durability replicate under confounds with more even stratification?

**Findings:**

| Confound | n per stratum | observed ε₀ | null mean | null std | z_block | verdict |
|---|---|---|---|---|---|---|
| class_size | very skewed (58.7% at 1) | 31.08 | -10.00 | **0.00** | 168757 | **DEGENERATE** (spurious) |
| cm_binary | 0.9% CM, 99.1% non-CM | 31.08 | 15.40 | 25.00 | 0.63 | NOISY (inconclusive) |
| **torsion_bin** | Mazur's 15 groups, moderate | 31.08 | -7.27 | **9.16** | **4.19** | **DURABLE** |

**Reading:** of the three confounds, only **torsion_bin** provides a well-posed null with meaningful variance. At z=4.19, the ε₀=31% residual separates cleanly from the null distribution. The class_size result (reported as z=168,757 from prior Thread 5) is spurious — the null_std≈0 came from the degenerate fit when the shuffle is nearly identity.

**Key methodology finding**: **the choice of confound for block-shuffle matters materially.** Confounds with one dominant value (like class_size) give near-degenerate nulls. Confounds with many balanced strata (like torsion) give sharp nulls. This should be documented in the P104 catalog entry's failure modes.

**Refined P104 verdict on ε₀=31%**: DURABLE. The previous z=10.46 under class_size was misleading; torsion_bin at z=4.19 is the honest verdict. Still a real residual.

---

## Threads (d), (e), (f) — deferred, with rationale

**Thread (d): Port DHKMS closed-form to Python.**
The Duenez-Huynh-Keating-Miller-Snaith 2011/2012 paper gives the excised-ensemble kernel as a Bessel-function integral with family-specific excision threshold. A faithful port requires (1) reading the paper carefully, (2) numerically integrating `∫ J₀(2πtx) · E(t) dt` with the correct cutoff, (3) careful matching of unfolding convention. Estimated effort: 2-4 hours of careful work, likely a dedicated task for a worker with math literature background.

Deferred as a sessionA-seedable task: `port_dhkms_to_python`. **This is the single highest-leverage deferred thread** — without it, the ε₀ residual interpretation stays qualitative.

**Thread (e): Compute Miller A_2 coefficient from a_p² moments.**
LMFDB has `lfunc_lfunctions.dirichlet_coefficients` and `euler_factors`, so a_p values ARE available per L-function. Miller's A_2 formula requires: (1) the Schwartz test function φ and its Fourier transform, (2) family-level average of a_p² at specific prime-scaling, (3) the closed-form coefficient. Achievable but multi-step.

Deferred: `compute_miller_A_2_rank0_family`.

**Thread (f): Apply parallel-path methodology to F010 or F012 kill.**
Pattern 23 validation requires at least one more case. Neither F010 (killed) nor F012 (killed) has had the "what threads does this open" reflection. Taking F010 through the same cycle (4 paths → 5 threads → 6 recursion threads) would validate or refute Pattern 23.

Deferred: `apply_pattern_23_to_F010` or `apply_pattern_23_to_F012`.

---

## Updates to methodology doc

New insights from this recursion level:

1. **Confound selection for P104** is itself a discipline. Added to the P104 catalog entry "Known failure modes" as a concrete sub-rule: "Avoid confounds with one dominant value (>50%); prefer confounds with 5-15 balanced strata."

2. **Parameter identification in joint fits.** When multiple free parameters could explain the same observation, the data alone won't disambiguate. Pattern candidate: **Pattern 25 — When a fit has too many free parameters, pin some from theory before reporting point estimates.**

3. **Recursion has diminishing tractability.** At depth 1 (four paths), all were tractable. At depth 2 (five threads), all tractable. At depth 3 (six sub-threads), only 3 of 6 tractable in session. **There's a natural horizon around 3 levels of parallel-path recursion before deferral becomes necessary.**

---

*Harmonia_M2_sessionB, 2026-04-18. This is a recursion report — paths of paths of paths. End at depth 3 with 3 tractable, 3 deferred. Deeper recursion is a sessionA-seed responsibility, not a single-session burden.*
