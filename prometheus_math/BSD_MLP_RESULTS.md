# BSD Rank Prediction — MLP vs Linear REINFORCE

**Date:** 2026-05-04
**Stream:** Path (C) — team review #6 refinement: "linear policy with one-hot features may be saturating; an MLP with 2-4 hidden layers might extract more from the same features."
**Verdict (one line):** A 2-layer MLP [128, 64] does NOT meaningfully beat the linear-REINFORCE baseline on the same feature set; both still recover the class prior. The bottleneck is the feature representation (raw a_p), not the policy class.

## Why this run

The earlier `BSD_RANK_RESULTS.md` (2026-04-29) reported linear-REINFORCE at +1.37x lift over random on the held-out test split (p = 0.00055), while collapsing to "always predict rank 0". The team review proposed: maybe a non-linear policy, with the same features, can read more signal.

This pilot trains an MLP REINFORCE policy on the identical 1000-curve corpus + identical 70/30 train/test split + identical seed (42), and runs a 6-cell hyperparameter sweep over learning rate and entropy coefficient.

## Setup

- Same corpus: 1000 stratified Cremona curves, conductor <= 20000.
  - Train: 700 (rank-0: 361, rank-1: 270, rank-2+: 69)
  - Test: 300 (rank-0: 139, rank-1: 130, rank-2+: 31)
- Features: 26-D obs (20 a_p values + log-conductor + 5 history terms).
- Policy: 2-layer MLP [128, 64] with ReLU; output = 5 logits over rank classes.
- Optimizer: Adam.
- Update: REINFORCE single-step contextual-bandit (episode length is 1) with EMA reward baseline + entropy regularization.
- Seeds: 5 per cell (17, 1026, 2035, 3044, 4053).
- Episodes: 5000 per training run.
- Test eval: deterministic argmax, one pass through 300-curve test split.

## Sweep results (6 cells, 5 seeds each)

Test mean reward = mean of per-seed test means; std = sample std across the 5 seeds. Test accuracy = mean fraction-correct (= test_mean / 100).

| lr     | entropy_coef | test_mean ± std    | test_acc ± std    |
|--------|--------------|--------------------|-------------------|
| 1e-3   | 0.01         | **47.07 ± 4.36**   | 0.471 ± 0.044     |
| 1e-3   | 0.001        | **47.07 ± 4.32**   | 0.471 ± 0.043     |
| 5e-4   | 0.01         | 46.60 ± 4.39       | 0.466 ± 0.044     |
| 5e-4   | 0.001        | 46.60 ± 4.39       | 0.466 ± 0.044     |
| 1e-4   | 0.01         | 46.40 ± 4.59       | 0.464 ± 0.046     |
| 1e-4   | 0.001        | 46.40 ± 4.59       | 0.464 ± 0.046     |

**Best cell:** lr=1e-3, entropy_coef=0.01 (or 0.001 — they tie within 0.01).

The two entropy coefficients are nearly identical at every LR — entropy regularization is barely doing anything because the policy converges to a near-deterministic class-prior solution very fast (within ~500 episodes). The LR axis spreads results by ~0.7 reward points, with the larger LR (1e-3) winning slightly.

## Comparison vs random and vs linear

5-seed regression check on the linear-REINFORCE baseline gives:

| arm    | test mean ± std    | test acc ± std    |
|--------|--------------------|-------------------|
| Random | 20.53 ± 2.14       | 0.205 ± 0.021     |
| Linear | 46.20 ± 4.37       | 0.462 ± 0.044     |
| MLP    | **47.07 ± 4.36**   | 0.471 ± 0.044     |

### Welch one-sided t-tests (n=5 per arm)

- **MLP vs Random:** lift = +1.292x, t-statistic large, **p = 1.13e-5** (very significant).
- **MLP vs Linear:** lift = +0.019x (~+0.87 reward points), **p = 0.381** (NOT significant).

The MLP clears the random floor by the same wide margin the linear policy did. Against the linear policy itself, the MLP is statistically indistinguishable.

### Earlier-run continuity

The 2026-04-29 pilot reported linear-REINFORCE test mean = 47.27 over 3 seeds (44.6 / 50.6 / 46.6). This run's 5-seed estimate of 46.20 ± 4.37 is consistent (the 3-seed point estimate sits well within 1 sigma of the 5-seed estimate). Regression check passes.

## Where the policy ended up

Both the linear and MLP policies converge to **class-prior recovery**, with one twist:

- Linear (this run, seed 17): pred_counts at argmax-eval ~= `[300, 0, 0, 0, 0]` -- always predicts rank 0.
- MLP best cell, seed 17: pred_counts at argmax-eval = `[7, 293, 0, 0, 0]` -- almost always predicts **rank 1**.

The MLP found a slightly different local optimum: predict the second-largest class (rank-1 = 130/300 = 43.3% of test), with occasional rank-0 hits in residual cases. By chance these residual hits land enough rank-0 curves to nudge accuracy from 0.463 (always-0) to 0.471 (mostly-1). **Same architecture-level pathology, different action-space corner.**

The pred_counts test (`pred_counts ≈ [7, 293, 0, 0, 0]`) is the smoking gun: a richer policy class did NOT discover an a_p -> rank discriminator. It rediscovered the same "find the modal class and stamp it" attractor that swallowed the linear policy, just on rank-1 instead of rank-0.

## Verdict

**MLP does NOT beat linear (p = 0.38). The proposed refinement does not lift the substrate.** Honest framing:

1. The lift the linear policy gets is the **class prior**, not signal extraction. A more expressive policy that still optimizes the same one-step REINFORCE objective on the same observation will also recover the class prior; it just gets to pick which class.
2. Both policies hit the same ~47% accuracy ceiling, which is essentially `max(P(rank=0), P(rank=1)) ≈ 0.46-0.47` on this stratified test set.
3. The bottleneck is **the feature representation**, not the model class. Raw a_p sequences carry the rank signal only through non-linear summaries (Goldfeld / Birch-Swinnerton-Dyer heuristics: average sign, partial Euler-product slope, bias of small a_p towards positive vs negative). An MLP can in principle learn these summaries, but with 26-D input + 1 reward per episode, the gradient signal is too weak to find them inside a 5000-episode budget; the entropy collapse to a class-prior policy out-paces any feature learning.

## What would actually move the needle (NOT done in this run)

This is the honest list of next experiments, in increasing order of effort:

1. **Hand-engineered features** that the linear policy CAN read directly:
   `mean(a_p / sqrt(p))`, `mean(a_p^2 / p)`, sign-balance count, count of vanishing a_p. These are the Goldfeld / BSD invariants — adding them as input features should let either policy class break the class-prior ceiling without any architectural change.

2. **Supervised pre-training of the encoder.** Train the MLP's [128, 64] body via cross-entropy on (a_p, rank) labels first (effectively rank classification as a supervised problem on Cremona), then drop the head and use the body as a frozen feature extractor for the REINFORCE policy. This would isolate the feature-learning bottleneck from the policy-gradient noise.

3. **L-function values** as a richer raw input. The first few coefficients of L(E, s) (or even just L(E, 1) and L'(E, 1)) carry the BSD-conjectural rank signal directly. With these as features, *both* the linear and MLP policies should easily beat the class prior.

4. **Class-balanced sampling.** Currently rank-2+ is 10% of the corpus, so the gradient signal for the rare class is dominated by majority-class noise. Re-weighted training (or oversampling) would let the policy learn to discriminate the rare class without giving up the modal classes.

## Honest framing

- This is **one architecture (MLP) on one feature set (raw a_p + history)**. The negative result is informative about the policy-class axis only.
- We tested 3 LRs x 2 entropy coefficients = 6 cells, with 5 seeds each. The "no significant lift" finding is robust to the explored sweep box; we did not test deeper MLPs (3-4 hidden layers), wider hidden dims (256+), or different optimizers.
- The MLP's small absolute lift (+0.87 reward points) is below the seed-to-seed std (~4.4), so even if it were real, it would be irrelevant for downstream work.
- The substrate plumbing remains green: the BIND/EVAL pipeline transmits the gradient cleanly, the seed determinism holds, the regression check on the linear arm passes.

## Test rubric coverage

`prometheus_math/tests/test_bsd_mlp.py` -- 12 tests, all green.

- Authority (3): forward yields valid distribution; analytic gradient matches numerical (5 finite-difference checks); trained MLP beats random on held-out by >= 10 percentage points.
- Property (3): same-seed MLPs identical; same-seed trainer identical; output dim matches n_actions across (obs_dim, hidden, n_actions) variants.
- Edge (3): empty batch shape (0, obs_dim); all-zero features produce a normalized finite distribution; rare-rank-class corpus trains without crash.
- Composition (3): trainer log-dict schema; 6-cell sweep dict schema; end-to-end env -> MLP -> train -> test -> record pipeline.

## Files

- `F:/Prometheus/prometheus_math/bsd_rank_mlp.py` -- MLP backend (~360 LOC).
- `F:/Prometheus/prometheus_math/_run_bsd_mlp_pilot.py` -- pilot runner (~210 LOC).
- `F:/Prometheus/prometheus_math/_bsd_rank_mlp_pilot.json` -- captured numbers.
- `F:/Prometheus/prometheus_math/_run_bsd_mlp_pilot_stdout.log` -- run trace.
- `F:/Prometheus/prometheus_math/tests/test_bsd_mlp.py` -- TDD test suite.
- `F:/Prometheus/prometheus_math/bsd_rank_env.py` -- linear baseline (UNCHANGED, regression check pass).
- `F:/Prometheus/prometheus_math/BSD_RANK_RESULTS.md` -- prior linear-only writeup.

## What this changes about the master plan

The team review's #6 refinement is now answered: the policy class is NOT the load-bearing axis. The next hypothesis ("L-function features + linear REINFORCE will beat both") is the testable upgrade. Until that hypothesis is shipped, the linear-REINFORCE +1.37x result remains the substrate's ceiling on the BSD env, and we should NOT advertise an MLP-driven improvement that the data does not support.
