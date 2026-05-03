# Scout #9 — Null-world generator for symbolic-search environments

**Tier:** T1 (frontier methodology research; load-bearing for Scouts #1, #3, #4, #6)
**Front:** Substrate epistemics — baseline calibration for `discovery_env` and the falsification battery
**Cost:** ~3-4 days build (week 1 spec) + iterative calibration
**Trigger:** ChatGPT pressure-cycle on team review (2026-05-03) flagged TWICE in 24h: *the substrate has no null-world generator; without one, residuals + RL = pattern-finding machine with no baseline.*
**Status:** Methodology brief; this scout is a prerequisite for Scout #3 (withheld benchmark) being interpretable.

---

## 1. Situation

Prometheus has three components that *touch* the calibration problem but do not solve it:

- **Techne's residual-primitive proposal** (commit `f76d3974`, "discovery loop: triple #3 — shaped reward + wider alphabet; structural ceiling confirmed"). The PROMOTE rate is well-defined operationally but uncalibrated: there is no expected-under-null PROMOTE rate to compare it against.
- **Charon's falsification battery v10** (25 tests / 4 tiers, frozen). The battery uses *permutation-shuffle nulls per finding* (per `feedback_permutation_null.md`, Harmonia Attack 4 killed NF backbone via this pattern), but the nulls are local to each finding rather than environmental.
- **Mossinghoff catalog as ground truth** (Scout #1, #3): the rediscovery-rate denominator is fixed, but the numerator (`R_agent`) lacks a `R_null` to divide against.

What's missing: an environment-level null-world generator that produces a stream of polynomials (and analogously, OEIS sequences, EC curves, theorem-strings) drawn from a *plausible-but-structureless* distribution, against which `discovery_env`'s PROMOTE rate becomes a *ratio* rather than an absolute. Scout #3 specifies the K-multiplier pass condition (`R_agent ≥ K · R_null`) but the null is not buildable today. This scout closes that gap.

---

## 2. State of the art

**AlphaGo / AlphaZero — random-rollout baseline** (Silver et al., *Nature* 2016, 2017). The original AlphaGo MCTS used *random rollouts as the value-network surrogate during early self-play*; later, AlphaZero reported Elo against a uniform-random move policy as the *zero point* of the Elo curve. Failure mode: if the random baseline is non-stationary (e.g., random with legal-move filtering vs. raw random), the Elo curve becomes incomparable across versions. Lesson: **fix the null and version-pin it**.

**AlphaProof autoformalization holdouts** (DeepMind blog, 2024; methodology paper forthcoming). Holdout problems are evaluated against (a) random tactic application from Lean's tactic library and (b) "trivial-tactic-only" (`rfl`, `simp`, `aesop`) baselines. The latter is the *informed-null*: a baseline that captures the cheap wins so the agent's reported gain isn't inflated by problems any compiler could close. Failure mode in early reports: trivial-tactic baseline closed ~20% of "novel" theorems, collapsing reported novelty.

**AlphaCode hidden-test baselines** (Li et al., *Science* 2022, [DOI:10.1126/science.abq1158](https://doi.org/10.1126/science.abq1158)). Pass-rate at sampling-rate-N is reported against random-program-generation at the same N. Random-program-generation pass rate on Codeforces was ≈0% even at N=10⁶, so AlphaCode's sub-percent gains were *real* — but the discipline of reporting against the random baseline is what made the comparison interpretable.

**DreamCoder randomized-prior controls** (Ellis et al., *PLDI* 2021, [arXiv:2006.08381](https://arxiv.org/abs/2006.08381)). Library evolution is measured against a *fixed random library* of equivalent size and primitive count. The "discovery" claim is gated on: tasks solved with evolved library / tasks solved with random library > 1. This is the closest precedent for Prometheus's PROMOTE rate: **the substrate's earned primitives must outperform a random-primitive control.**

**Permutation-null discipline** (Fisher, *Design of Experiments*, 1935; modernized by Good, *Permutation Tests*, 1994). The shuffling pattern is the canonical null for *exchangeability hypotheses*. Charon's battery already uses it locally. The extension to environment-level requires shuffling at a higher unit (the *generator distribution*, not individual data points).

**Random-baseline RL benchmarks** (Mnih et al., *Nature* 2015 for Atari DQN; Schulman et al., 2017 for PPO/MuJoCo, [arXiv:1707.06347](https://arxiv.org/abs/1707.06347)). Standard practice: report "human-normalized score" with random-policy at 0% and human at 100%. Failure mode: many environments have random-policy floors of ~10-20% just from incidental reward, inflating apparent gains; the field eventually adopted the *random-policy-with-action-repeat-30* explicit baseline (Machado et al., [arXiv:1709.06009](https://arxiv.org/abs/1709.06009)).

**The "null world" pattern in physical science.** Cosmology's *mock universe* simulations (e.g., MICE-GC, [arXiv:1411.3286](https://arxiv.org/abs/1411.3286)) generate 𝒪(10³) full universes from the null power spectrum to bound the variance of any structure claim. Particle physics' *data-driven background estimation via control regions* (ATLAS, CMS Higgs analyses) constructs the null *from the data itself* by isolating a region where the signal cannot be present. Both share a feature: **the null generator is at the same fidelity as the observation pipeline**, not a toy approximation.

---

## 3. Design patterns Prometheus should adopt

Five concrete null constructions, ordered by fidelity:

**(a) Random-polynomial-from-distribution.** Sample polynomials from the same degree distribution as Mossinghoff's catalog (degree ∈ {6, 8, 10, ..., 44} weighted by catalog frequency), with coefficients drawn uniformly from {-1, 0, 1}. Measure the fraction with M ∈ [1.001, 1.18]. This is a *broad* null: it asks "what fraction of monic-ish low-coefficient polynomials at these degrees have small Mahler measure by accident?" Expected answer: very few — most random ±1 polynomials have M well above 1.18. **This rate is the K-divisor for Scout #3.**

**(b) Coefficient-shuffle null.** For each Mossinghoff polynomial, *shuffle its coefficient sequence* (preserving degree, leading/trailing coefficient if monic-reciprocal). Compute M of the shuffled polynomial. This is a *structure-preserving* null: it controls for "having the right coefficient histogram" without preserving the algebraic structure that makes M small. Failure mode warning (see §5): for reciprocal polynomials, shuffling can preserve reciprocity by accident, leaking signal.

**(c) Generative-twist null.** Apply Aporia's mutator-front operators (palindrome lift, sign flip, cyclotomic multiplication by Φₙ) to *random seeds* rather than known small-M polynomials. Measure the M-distribution of mutator outputs. This nulls the *mutator architecture itself*: the agent's apparent gains might be the mutators doing the work, not the policy. Closest analog: DreamCoder's random-library control.

**(d) Synthetic-Mossinghoff null.** Generate *fake* Mossinghoff entries via degree-and-M-matched sampling: for each real entry at (degree=d, M=m), construct a synthetic entry at the same (d, m) drawn from a different polynomial family (e.g., random reciprocal at that degree, scaled to that M). Treat as a *hidden control set* mixed into the withheld benchmark. The discovery loop's "find-rate" on synthetic entries is the *baseline rate of false confirmation*. Closest analog: cosmology's mock universes.

**(e) Per-domain null-world patterns** (catalog of analogs for the broader substrate):
- **OEIS sleeping beauties:** random integer sequences with matched growth rate (use D-finite-by-rejection sampling to preserve OEIS-likeness).
- **LMFDB elliptic curves:** random Weierstrass equations (a₁..a₆) with conductor distribution matched to the LMFDB target slice.
- **Mathlib statements:** random theorem-like strings respecting type signatures and import dependencies (constraint-respecting random generation, per Polu & Sutskever, [arXiv:2009.03393](https://arxiv.org/abs/2009.03393)).
- **Knots / genus-2 curves** (per `project_silent_islands.md`): random braid words at matched length; random hyperelliptic equations at matched discriminant magnitude.

The five-pattern stack lets Prometheus report PROMOTE rate against multiple nulls simultaneously, matching cosmology's practice of reporting findings against several mock pipelines.

---

## 4. Concrete spec for Mahler-measure domain

Module: `techne/null_world.py` (or `charon/null_world/mahler.py` if Charon owns it).

```python
# API surface
def sample_null_polynomial(
    degree_dist: dict[int, float],   # e.g., {6: 0.1, 8: 0.15, ...}
    coeff_alphabet: tuple = (-1, 0, 1),
    enforce_monic: bool = True,
    enforce_reciprocal: bool = False,  # toggle for null variant
    seed: int,
) -> Polynomial: ...

def null_world_promote_rate(
    n_samples: int,
    discovery_env_reward_fn: Callable,
    promote_threshold: float,    # same as live env
    seed: int,
) -> dict:
    """Returns {'promote_rate': float, 'm_distribution': np.ndarray,
                'samples_seen': int, 'ci_95': tuple}."""

def calibrate_K_multiplier(
    agent_promote_rate: float,
    null_world_rate: float,
    n_seeds: int,
) -> dict:
    """Returns {'K_observed': float, 'pass_K5': bool, 'pass_K10': bool,
                'p_value_vs_null': float}."""
```

**Calibration test (ships with the module):** run `null_world_promote_rate` at n=10⁵ with the same reward function and PROMOTE threshold as `discovery_env`'s current shaped-reward configuration. Sanity-check: the null PROMOTE rate should be small but non-zero (estimated 10⁻⁴ to 10⁻² based on coefficient-space density of small-M polynomials, per Smyth's bounds for ±1 polynomials, [arXiv:0810.4067](https://arxiv.org/abs/0810.4067)). If it returns 0 at n=10⁵, the threshold is too tight and K-multiplier is undefined; if it returns >10%, the threshold is too loose and the live agent's PROMOTE rate is meaningless.

**Recommended K-multiplier threshold:** **K = 10 for "publishable", K = 5 for "interesting".** Rationale:
- Cosmology and particle physics adopt 5σ (≈ K=10⁶ in p-value terms) for *discovery*; this is too strict for substrate work.
- DreamCoder reported 2-4× over random-library baseline as the "library helps" threshold (Ellis et al. 2021).
- AlphaCode reported ~10× over random-program at fixed sampling-rate as their headline claim.
- K=5 is the working consensus in RL benchmarking literature for "above noise" (per Henderson et al., *AAAI* 2018, [arXiv:1709.06560](https://arxiv.org/abs/1709.06560)).
- **K=10 buys robustness against the multi-null-stack reporting** (§3): if the agent passes K=10 against one null and K=5 against the others, the headline can defensibly be "K≥5 across all nulls".

---

## 5. Failure modes

**Too-broad nulls.** Random ±1 coefficient polynomials have M-distribution dominated by Mahler ≈ exp(degree × log 2 / 2). Any agent that learns "small coefficients → small M" trivially beats this null. **Mitigation:** report against multiple nulls (§3 stack), with the strictest null setting the headline K.

**Too-narrow nulls.** Coefficient-shuffle of a Salem polynomial often preserves reciprocity by accident (≈30% of shuffles of degree-10 reciprocals are still reciprocal). Reciprocity is the algebraic property *responsible for* small M in Lehmer-class polynomials. **Mitigation:** stratify the shuffle null by "preserved reciprocity yes/no" and report both rates separately. The *broken-reciprocity* shuffle is the meaningful baseline.

**Algebraic-invariant leakage.** Cyclotomic factors are preserved under any permutation that fixes the cyclotomic divisor; structure-preserving nulls in number-theoretic domains routinely leak signal because the algebra has more invariants than the syntactic shuffle preserves. **Mitigation:** test the null on *known-positive* and *known-negative* control sets before deployment. If the null assigns equal mass to both, it is broken.

**Reward-function-dependent nulls.** A null calibrated against unshaped reward will under-estimate the rate when shaped reward is in play. **Mitigation:** the null generator must take the live reward function as a parameter (per §4 spec), and re-calibration is mandatory after every reward-shaping change.

---

## 6. Concrete next move for Techne

**Week 1 (ships):** Pattern (a), random-polynomial-from-distribution. Smallest API surface, broadest null, calibrates the K-divisor for Scout #3 immediately. ~200 LOC; one calibration run at n=10⁵ to set the floor. Wire into `discovery_env` as a CLI flag `--null-world-baseline` that runs the null in parallel and reports the K-ratio at episode-end.

**Week 2 (deferred but specified):** Pattern (b) coefficient-shuffle and pattern (c) generative-twist. These need Charon's mutator-front to be exposed as a callable.

**Deferred to Charon's queue:** Patterns (d) synthetic-Mossinghoff and (e) per-domain extension. (d) requires the catalog typology Aporia is curating; (e) requires the per-domain corpus pipelines to be stable.

**Before Scout #3 fires:** at minimum pattern (a) must be live, with K-divisor measured. Otherwise Scout #3's pass condition is operationally undefined and the result is uninterpretable.

---

## 7. References

1. Silver, D. et al. (2016). "Mastering the game of Go with deep neural networks and tree search." *Nature* 529, 484–489. [DOI:10.1038/nature16961](https://doi.org/10.1038/nature16961).
2. Silver, D. et al. (2017). "Mastering the game of Go without human knowledge." *Nature* 550, 354–359. [DOI:10.1038/nature24270](https://doi.org/10.1038/nature24270).
3. DeepMind (2024). "AI achieves silver-medal standard solving International Mathematical Olympiad problems." Blog post; AlphaProof methodology. https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/
4. Li, Y. et al. (2022). "Competition-level code generation with AlphaCode." *Science* 378, 1092–1097. [DOI:10.1126/science.abq1158](https://doi.org/10.1126/science.abq1158).
5. Ellis, K. et al. (2021). "DreamCoder: Bootstrapping inductive program synthesis with wake-sleep library learning." *PLDI 2021*. [arXiv:2006.08381](https://arxiv.org/abs/2006.08381).
6. Fisher, R. A. (1935). *The Design of Experiments*. Oliver and Boyd, Edinburgh.
7. Good, P. (1994). *Permutation Tests: A Practical Guide to Resampling Methods for Testing Hypotheses*. Springer.
8. Mnih, V. et al. (2015). "Human-level control through deep reinforcement learning." *Nature* 518, 529–533. [DOI:10.1038/nature14236](https://doi.org/10.1038/nature14236).
9. Schulman, J. et al. (2017). "Proximal Policy Optimization Algorithms." [arXiv:1707.06347](https://arxiv.org/abs/1707.06347).
10. Machado, M. C. et al. (2018). "Revisiting the Arcade Learning Environment." *JAIR* 61, 523–562. [arXiv:1709.06009](https://arxiv.org/abs/1709.06009).
11. Henderson, P. et al. (2018). "Deep Reinforcement Learning that Matters." *AAAI 2018*. [arXiv:1709.06560](https://arxiv.org/abs/1709.06560).
12. Crocce, M. et al. (2015). "The MICE Grand Challenge lightcone simulation." *MNRAS* 453, 1513–1530. [arXiv:1411.3286](https://arxiv.org/abs/1411.3286).
13. ATLAS Collaboration (2012). "Observation of a new particle... with the ATLAS detector at the LHC." *Phys. Lett. B* 716, 1–29. [arXiv:1207.7214](https://arxiv.org/abs/1207.7214). (Data-driven background estimation methodology.)
14. Smyth, C. (2008). "The Mahler measure of algebraic numbers: a survey." [arXiv:0810.4067](https://arxiv.org/abs/0810.4067). (Bounds on M for low-coefficient polynomials; sets the expectation for null-world rates.)
15. Polu, S. & Sutskever, I. (2020). "Generative Language Modeling for Automated Theorem Proving." [arXiv:2009.03393](https://arxiv.org/abs/2009.03393). (Constraint-respecting random theorem generation; analog for Mathlib null pattern.)
16. Boyd, D. W. (1980). "Reciprocal polynomials having small measure." *Math. Comp.* 35, 1361–1377. [DOI:10.2307/2006406](https://doi.org/10.2307/2006406). (Original Mossinghoff-precursor catalog; structural baseline for shuffle nulls.)

---

**Cross-cutting tag:** Once `null_world.py` ships, update `QUEUE.md` cross-cutting findings to mark Cases (1), (3), (4), (6) as un-blocked on the null-world dependency.
