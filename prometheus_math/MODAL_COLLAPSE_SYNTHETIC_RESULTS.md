# Modal-Collapse Synthetic Diagnostic — Results

**Date:** 2026-05-04
**Author:** Techne (executing Aporia's specification)
**Time budget:** 1 hour (per Aporia)
**Code:** `prometheus_math/modal_collapse_synthetic.py`
**Tests:** `prometheus_math/tests/test_modal_collapse_synthetic.py` (16/16 passing)
**Raw results:** `prometheus_math/_modal_collapse_synthetic_results.json`

---

## TL;DR — Verdict

**Case A. The substrate is broken.**

On the LOW-NOISE BALANCED variant — a synthetic env where `y = w·x + b + ε` with σ=0.01 and uniform bin edges, so a 26-parameter linear least-squares fit independently achieves **>60% bin accuracy** (authority test, see test suite) — both REINFORCE-linear and PPO-MLP fail to learn the linear map. REINFORCE collapses to 3 bins (top-3 mass = 99.1%) at 4.91% accuracy (random baseline = 4.84%). PPO stays uniform across all 21 bins at 4.61% accuracy.

The cross-domain modal-collapse pattern across BSD rank, modular forms, knot trace fields, genus-2, OEIS Sleeping Beauty, and mock theta is **not a substrate finding**. It is a confirmation of standard RL pathology under sparse 0/1 reward + episode-length-1 + entropy-floor REINFORCE/PPO — exactly as Aporia diagnosed. The §5 cross-domain claim has a different cause than I claimed.

---

## Setup

Synthetic env, episode length 1 (contextual bandit, identical to all six real envs):

- **Observation:** `x ~ N(0, I_d) ∈ R^d` with `d = 20`, concatenated with the same 6-feature history vector used by `bsd_rank_env` (so `obs_dim = 26`).
- **Hidden truth:** `w ∈ R^{20}` unit-norm, `b ∈ R`, both deterministic from `corpus_seed=0`.
- **Target:** `y = w·x + b + ε`, `ε ~ N(0, σ²)`.
- **Action space:** 21 bins covering `y`. (Matches `modular_form_env.N_BINS = 21`.)
- **Reward:** `100` if predicted bin == true bin, else `0`. (Matches `REWARD_HIT/REWARD_MISS` in both real envs.)

Trainers are **byte-for-byte ports** of `modular_form_env.train_random / train_reinforce / train_ppo` — same hyperparameters, same NumPy implementation, same entropy coefficient, same baseline decay, same PPO clip ε, same MLP shape (32-hidden ReLU). Only the env varies.

Four variants × three algorithms × three seeds × 5 000 episodes = **180 000 episodes total, ~11 seconds wall clock**.

| Variant            | Binning   | σ      | Description                              |
|--------------------|-----------|--------|------------------------------------------|
| V1 BALANCED        | uniform   | 0.10   | The "is the agent fundamentally OK?" probe |
| V2 SKEWED          | inner-tight | 0.10 | Matches real-domain class-prior imbalance |
| V3 LOW-NOISE       | uniform   | 0.01   | The decisive variant: trivially learnable  |
| V4 SKEWED + HIGH-σ | inner-tight | 0.50 | Real-domain stress test                  |

**Authority gate (passing):** the decisive variant V3 is solvable in principle. A pure-NumPy least-squares fit on 1 000 (x, y) samples, then bin via `searchsorted` on the env's edges, achieves bin accuracy **≥ 60%** (test `test_authority_linear_truth_recoverable_in_principle`). So if the trainer doesn't beat random on V3, that's the trainer's failure, not the env's.

---

## Results — 4 Variants × 3 Algorithms (mean ± std over 3 seeds, 5 000 episodes)

### V1 BALANCED (σ = 0.1, uniform bins — random baseline ≈ 4.76%)

| Agent     | Accuracy             | Resolution (within ±1 bin) | Active bins ≥1% mass | Top-3 bin mass |
|-----------|----------------------|----------------------------|----------------------|----------------|
| random    | 0.0475 ± 0.0011      | 0.141                      | 21 / 21              | 0.150          |
| REINFORCE | 0.0700 ± 0.0264      | 0.209                      | **3 / 21**           | **0.994**      |
| PPO       | 0.0438 ± 0.0030      | 0.135                      | 21 / 21              | 0.153          |

REINFORCE collapses to 3 bins (the modal-collapse signature) but, because the env is genuinely uniform, gets only marginal lift over random. PPO doesn't even collapse — it stays at random.

### V2 SKEWED (σ = 0.1, mass-concentrating bins — random baseline ≈ 4.76%)

| Agent     | Accuracy             | Resolution | Active bins | Top-3 bin mass |
|-----------|----------------------|-----------|-------------|----------------|
| random    | 0.0464 ± 0.0012      | 0.120     | 21 / 21     | 0.150          |
| REINFORCE | **0.2694 ± 0.0063**  | 0.290     | **2 / 21**  | **0.993**      |
| PPO       | 0.0457 ± 0.0038      | 0.118     | 21 / 21     | 0.153          |

**This is the textbook "modal-class collapse looks like signal."** REINFORCE crushes random (5.8× lift, 26.9% vs 4.6%) by collapsing to **2 bins** that absorb >50% of the y-distribution mass. The lift is real. The reasoning (`agent learned w · x`) is false. The agent learned the **prior**, not the **map**. This is what the §5 cross-domain results confused for substrate competence.

### V3 LOW-NOISE BALANCED (σ = 0.01 — decisive variant, lstsq solves at 60%+)

| Agent     | Accuracy             | Resolution | Active bins | Top-3 bin mass |
|-----------|----------------------|-----------|-------------|----------------|
| random    | 0.0484 ± 0.0015      | 0.142     | 21 / 21     | 0.150          |
| REINFORCE | **0.0491 ± 0.0335**  | 0.151     | **3 / 21**  | **0.991**      |
| PPO       | 0.0461 ± 0.0031      | 0.135     | 21 / 21     | 0.154          |

**The verdict is here.** A trivial least-squares fit gets ≥60%. Both trainers get ≈ random (≈ 5%). REINFORCE collapses to 3 bins anyway despite the env being uniform, so its modal collapse is **architectural / RL-pathological, not domain-driven**. PPO can't even pick out the modal class. **The architecture cannot extract the linear signal.** That is Case A.

### V4 SKEWED + HIGH-σ (σ = 0.5, the "real-domain stress test")

| Agent     | Accuracy             | Resolution | Active bins | Top-3 bin mass |
|-----------|----------------------|-----------|-------------|----------------|
| random    | 0.0460 ± 0.0019      | 0.116     | 21 / 21     | 0.150          |
| REINFORCE | 0.1893 ± 0.1180      | 0.221     | **3 / 21**  | **0.993**      |
| PPO       | 0.0464 ± 0.0038      | 0.118     | 21 / 21     | 0.163          |

Same story as V2: REINFORCE wins by predicting the mode, with 4.1× lift and absurd seed variance (±0.118 across only 3 seeds means it sometimes finds a slightly different modal bin). PPO is at random.

### Modal-collapse signature, summarized

| Variant | REINFORCE active bins | PPO active bins | REINFORCE top-3 mass |
|---------|-----------------------|-----------------|----------------------|
| V1 balanced       | 3 | 21 | 0.994 |
| V2 skewed         | 2 | 21 | 0.993 |
| V3 low-noise (decisive) | 3 | 21 | 0.991 |
| V4 skewed + high-σ      | 3 | 21 | 0.993 |

REINFORCE collapses to ≤ 3 bins on **every variant including V3 where the env is trivially learnable**. PPO stays uniform on every variant including V3. **Neither agent learns w · x even in the regime where lstsq trivially does.**

---

## Diagnostic Interpretation

### Case A — substrate broken (this is the result)

Both the linear policy gradient and the MLP-based PPO fail under this reward shape and episode structure on a synthetic env that is **demonstrably learnable**. Specifically:

1. **REINFORCE-linear collapses to a 2-3 bin distribution regardless of x.** Its policy gradient is `(R − baseline) · ∇log π(a | s)`, but with reward in {0, 100} and episode length 1, the advantage signal is tiny and high-variance. The entropy bonus (coef 0.01) is too low to prevent the policy from concentrating on whichever bin happens to be the modal class (or, in the balanced case, on whichever bin the early random initialization broke ties for). Once the policy has ≥ 90% mass on one bin, the gradient on the obs vector is essentially zero — the linear map cannot be learned because the policy never explores enough to receive the gradient signal.

2. **PPO-MLP cannot move from the uniform initialization.** With Xavier-init weights and no useful bootstrap signal in 5 K steps, PPO's clipped surrogate + advantage normalization keep the policy frozen near uniform. (Compare: in classical PPO benchmarks with episode length > 100 and shaped reward, PPO learns; on contextual bandits with sparse 0/1 reward, it is well-known to underperform REINFORCE.) PPO's advantage normalization across the batch wipes out the per-sample gradient signal because advantages within a batch are roughly equally good or equally bad — there is no relative-order information.

3. **Both behaviors are independent of the env's class prior.** The collapse happens on V1 (uniform) just as on V2 (skewed). The agent isn't "discovering" structure; the agent is doing what REINFORCE/PPO with these hyperparameters always do on contextual-bandit RL with sparse 0/1 reward.

This is what **Aporia diagnosed**: sparse-reward + episode-length-1 + entropy collapse → modal-class collapse is textbook for these algorithms. The synthetic test confirms: the cross-domain pattern across the six real domains is rediscovering this RL failure mode six times, not surfacing a real substrate signal.

### Implications for the §5 cross-domain claim

The §5 narrative claimed that "the same substrate machinery generalizes across BSD rank, modular forms, knot trace fields, genus-2, OEIS Sleeping Beauty, and mock theta." The lifts over random were real (1.5×–5×) but **were almost entirely class-prior recovery**, not substrate-driven discovery. The diagnostic reproduces the same lift pattern (5.8× on V2 skewed) on a synthetic env where the "substrate" is non-existent — it's just an MLP failing to fit a 21-bin linear regression.

The honest claim from the cross-domain experiments is:

> "REINFORCE/PPO with sparse 0/1 reward and episode length 1 always collapse to predicting the modal class. We confirmed this six times on real mathematical domains and once on a synthetic regression. The lift over uniform-random is the agent recovering the empirical class prior, not learning a feature-to-output map."

That is **not a finding about the substrate**. It is a finding about RL training pathology. The substrate's role in the six-domain pattern is to provide BIND/EVAL accounting infrastructure; the "lift" comes from the prior, not from the BIND/EVAL machinery.

### What this rules out

- Cross-domain modal collapse as a substrate-architecture finding.
- The §5 lift values as evidence that the substrate is generalizing.
- Continued use of sparse 0/1 reward + episode length 1 as a probe for substrate competence.

### What this does **not** rule out

- The substrate's BIND/EVAL accounting properties (cost model, capability provenance, etc.) — those are unrelated to the agent training loop.
- Specific positive findings that did not depend on RL training (e.g., cross-domain congruence verifications, the BSD MLP supervised baseline).
- The possibility that a substrate-aware agent with shaped reward and longer episodes would surface real cross-domain transfer. The diagnostic only invalidates the *current* training setup, not the substrate concept.

---

## Recommended Next Moves (Case A)

In rough order of cost:

1. **Retract the §5 cross-domain claim as currently written.** Replace with a shorter section: "Across six domains REINFORCE recovers the empirical class prior, exactly as Aporia predicted. We do not have evidence of substrate-driven generalization beyond class-prior recovery." This is a kill, but a clean one. Aporia's diagnostic is the strongest piece of evidence we have so far that the cross-domain lifts were artifactual.

2. **Replace sparse 0/1 reward with shaped reward.** For continuous targets (modular form `a_p`, knot trace fields), use `r = exp(-(pred − true)² / σ²)`. For ordinal targets (BSD rank, mock theta), use bin-distance reward (`r = 1 − |pred_bin − true_bin| / N_BINS`). The synthetic env supports this; re-running V3 with shaped reward should immediately verify whether shaping fixes Case A.

3. **Replace episode-length-1 contextual bandit with multi-step episodes.** Even a length-2 episode (predict feature, then predict output, with reward on the output) gives the agent's policy gradient a temporal anchor. The substrate's BIND/EVAL chain naturally supports this — we just haven't been using it.

4. **Stop comparing against uniform-random; compare against the empirical class prior.** "REINFORCE beats random by 5×" becomes meaningless once you realize the modal-class predictor *also* beats random by ~5× on a skewed distribution. The honest baseline is the modal-class predictor (zero learning required); the lift over THAT baseline is the only number that measures substrate competence.

5. **Add a per-input-perturbation probe to every cross-domain experiment.** If the agent's predictions don't change when x changes, the agent isn't using x. This is a 5-line check that should run as an automatic gate on any future cross-domain claim — a CI-level invariant. The synthetic env exposes this trivially: `pred_counts` already shows whether the policy ignores x.

---

## Reproduction

```bash
cd F:/Prometheus
python -m pytest prometheus_math/tests/test_modal_collapse_synthetic.py -v
python -c "
import json
from prometheus_math.modal_collapse_synthetic import run_diagnostic
report = run_diagnostic(n_episodes=5000, seeds=(0, 1, 2), d=20, n_bins=21)
with open('prometheus_math/_modal_collapse_synthetic_results.json', 'w') as f:
    json.dump(report, f, indent=2)
print('Verdict:', report['verdict'])
"
```

Expected wall clock: ≈ 11 seconds on a single CPU core (no GPU required). Verdict: A.
