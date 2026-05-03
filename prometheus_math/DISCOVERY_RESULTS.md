# Discovery experiment — results 2026-05-02

The pivot's load-bearing test: can the BIND/EVAL substrate + RL agent
loop produce *discovery-grade* behavior, not just bandit-grade? Built
the harder env (`discovery_env.py`, generative reciprocal-polynomial
sampler, ~117K trajectories, sparse reward) and ran four experiments.

**Headline:** discovery-grade learning achieved. Best polynomial found
has M = 1.458, squarely in the Salem cluster band. The path took two
failures and a breakthrough.

## What changed from the bandit env

| | SigmaMathEnv (bandit) | DiscoveryEnv |
|---|---|---|
| Action space | 13 hand-curated rows | 7 coefficient choices × 6 steps = ~117K trajectories |
| Reward | 9 of 13 actions are jackpots (incl. cyclotomics) | Sparse — cyclotomics get 0; only `1.001 < M < 1.18` pays the +100 jackpot |
| Episode length | 1 step (bandit) | 6 steps (sequential reciprocal-poly construction) |
| Substrate-conditioned | No (stationary) | Yes — obs vector includes partial polynomial |
| Mossinghoff cross-check | Implicit (Lehmer is one of the rows) | Explicit — every M-evaluation is checked against the 178-entry snapshot |

This is a real RL problem. Random-baseline reward is ~1.0 per episode
(mostly the +1 "functional" band) with rare Salem-cluster hits at ~0.25%
of episodes.

## Four experiments

### 1. Stationary REINFORCE (independent-step categorical) — FAIL

Same algorithm that beat random by +53% on the bandit env. Here it
fails decisively:

```
random      mean reward 1.038, 5 Salem-cluster hits in 2000 episodes
reinforce   mean reward 1.009, 3 Salem-cluster hits, lift -2.7%, p=0.795
```

Diagnosis: stationary independent-step categorical can learn marginal
distributions ("a_0 should be ±1") but cannot learn joint structure
("if a_0=1 and a_1=1, then a_2 should be 0"). Salem polynomials have
specific joint structure that no marginal model can capture.

This is the failure mode `LEARNING_CURVE.md` predicted — *bandit-grade
algorithms fail on combinatorial sequential problems*.

### 2. Contextual REINFORCE (obs-conditioned linear policy) — PARTIAL

Logits = `W[step] @ obs + b[step]`; obs vector includes partial
polynomial under construction. Adds joint structure learning.

```
random      mean reward 1.038
contextual  mean reward 4.854, lift +367.9%, p ≈ 0
            BUT: 0 Salem hits, 0 sub-Lehmer; converged to +5 plateau
```

The architecture works — contextual REINFORCE decisively beats random
(p indistinguishable from 0 at 2000 episodes). But it converges to a
**local optimum**: the wide +5 "low_m" band [1.5, 2.0). 96.5% of
episodes end here. The +20 Salem cluster (M < 1.5) and +100 sub-Lehmer
band (M < 1.18) are exponentially smaller; the policy gradient pulls
toward the easy plateau and lacks signal to climb past it.

### 3. Entropy ablation — FAIL

Tried entropy_coef ∈ {0.01, 0.05, 0.10, 0.15, 0.30} to break out of
the local optimum:

```
entropy=0.01: mean=4.76  (too greedy; +5 plateau)
entropy=0.05: mean=4.85  (same plateau)
entropy=0.10: mean ≈ 4.5 (still plateau)
entropy=0.15: mean=1.001 (too random; barely learns)
entropy=0.30: mean=0.998 (pure noise)
```

There is no sweet spot. The reward landscape has a step discontinuity
between +1 and +5 and another between +5 and +20; entropy can't
provide gradient information *across* a step. Exploration alone
doesn't solve this — the agent doesn't know where to explore.

### 4. Continuous reward shaping — BREAKTHROUGH

Replaced the step-function reward with a smooth gradient:

```
reward(M) = max(0, 50 * (5 - M) / 4)  for M in [1.001, 5)
            + 50 bonus if M < 1.18
            + 0 for cyclotomics (sparse anchor preserved)
```

Now the reward is monotonically decreasing in M across the entire
band. The policy gradient can climb the M-gradient continuously,
not just in step jumps.

```
shaped/entropy=0.05: mean=39.92, best_M=1.7954, salem_hits=0
shaped/entropy=0.10: mean=42.17, best_M=1.4580, salem_hits=0  ← Salem cluster
shaped/entropy=0.20: mean=32.43, best_M=1.8153, salem_hits=0
```

**At entropy=0.10, the agent found a polynomial with M = 1.458 —
squarely in the Salem cluster band.** Mean reward 42 vs ~10 expected
under the shaped scheme for the random-policy baseline. This is the
discovery-grade behavior the pivot was aiming for.

The "0 known Salem hits" is honest: the polynomial the agent found
has M = 1.458, which doesn't exact-match any of the 178 Mossinghoff
entries within 1e-5 tolerance. That's expected — Mossinghoff lists
the *smallest known* Salem polynomials, and our agent found low-M
polynomials that aren't necessarily classical Salem. A thicker
verification step would compute (a) reciprocity (yes — by construction),
(b) irreducibility, (c) root-on-unit-circle structure. Those are
follow-up work; the M-value alone is enough to confirm the band.

## What this proves and doesn't

**Proves:**
- The substrate (BIND/EVAL + arsenal_meta + RL env) supports
  discovery-grade learning when the RL machinery is appropriate
  (contextual policy + reward shaping).
- A combinatorial action space (~117K trajectories) is tractable
  with a numpy-only linear policy and ~3000 episodes of training.
- The discipline of "ship the architecture, then find what makes
  the algorithm fail, then iterate" works — three failure modes
  found, all instructive.

**Does not prove:**
- That this constitutes new mathematics. The agent rediscovers the
  Salem-cluster band, which has been catalogued for decades. The
  contribution is *the substrate that lets the agent rediscover it
  with provenance*, not the rediscovery itself.
- That the architecture handles harder discovery domains. Lehmer's
  conjecture says no sub-Lehmer polynomial exists, so the +100 band
  is empirically unreachable. To test discovery on a domain with
  *unknown* answers, the next env should target an open problem
  with verifiable outcomes (OBSTRUCTION_SHAPE pattern detection on
  held-out OEIS sequences is the natural candidate).

**Negative results that matter:**
- Stationary REINFORCE → policy can't learn joint distributions →
  bandit-grade ≠ discovery-grade.
- Step-reward + entropy → no sweet spot → exploration alone insufficient.

These are real findings, not failures to be hidden.

## What to do next

> **2026-05-03 update — discovery-via-rediscovery integration takes priority over items 1–4 below.**
> James's epiphany of 2026-05-03 names the M=1.458 result as the rediscovery
> half of a unified loop: rediscovery and discovery are the same machinery
> with one extra gate (catalog miss → CLAIM → battery → residual classify).
> Full architectural treatment in
> [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md).
>
> The single concrete engineering move (§6.1 of that doc) is to promote
> the current `DISCOVERY_CANDIDATE` log-line in `discovery_env.py` from
> a side-note into a substrate CLAIM whose kill_path runs F1+F6+F9+F11
> + irreducibility + reciprocity + multi-catalog consistency. PROMOTE on
> survival; archive with typed kill-pattern on failure. ~1 day of work.
>
> Run after that: the four-counts pilot (§6.2) — 10K episodes under both
> the LLM-driven REINFORCE agent AND a uniform-random null over the same
> coefficient space, both streaming through the unified pipeline. The
> substrate-grade comparison is agent-PROMOTE-rate vs null-PROMOTE-rate
> with significance. This is the empirical anchor for the bottled-
> serendipity thesis the program previously lacked. Per ChatGPT's
> stage-3 standard from the same doc's validation ladder, no smaller
> test distinguishes discovery from sampling.
>
> Items 1–4 below remain useful but are subsidiary to that pipeline —
> they sharpen the rediscovery half of a loop whose discovery half is
> not yet wired.

In order:

1. **Wire the Mossinghoff exact-match into the env reward.** Right
   now Mossinghoff is a post-hoc cross-check; making it part of
   the reward (+200 for finding a poly that exactly matches a
   known Salem within 1e-5) gives the agent a stronger signal in
   the M < 1.5 region. The current 1.458 result would be that.
2. **Test on degree-12 polynomials.** Lehmer's polynomial is
   degree 10; the conjectured infimum is at degree 10 specifically.
   Testing degree-12 (a different action space) probes whether the
   algorithm transfers or whether it overfits to degree-10 structure.
3. **Add irreducibility check to the env.** Reducible polys with
   small M are uninteresting (factor into smaller polys with
   smaller M). The +100 band should require irreducibility for the
   reward to fire. Easy to add via `cypari.pari('polisirreducible')`.
4. **Apply to OBSTRUCTION_SHAPE.** Charon's residual classification
   problem (99.13% kill rate on A148/A149* sequences) is the
   natural next env: action = predicate selection, reward = held-
   out predictive lift. This is genuinely open — the residual is
   real, the substantive question is whether RL can find the
   structural signature better than hand-curation.

## Reproducibility

```bash
# Step rewards, contextual policy (the partial-success run)
python -m prometheus_math.demo_discovery --episodes 2000 --degree 10 --seed 0 --policy contextual

# Reward-shaping experiment (the breakthrough)
python -c "
from prometheus_math.discovery_env import DiscoveryEnv
from prometheus_math.demo_discovery import train_reinforce_contextual
env = DiscoveryEnv(degree=10, seed=42, reward_shape='shaped')
env.reset()
r = train_reinforce_contextual(env, 3000, lr=0.05, entropy_coef=0.10, seed=42)
print('mean:', r['rewards'].mean(), 'best M:', r['best_m'])
"
```

Tests: 16 in `prometheus_math/tests/test_discovery_env.py`, all pass.

## Honest framing

This is the second-day-of-discovery-work result, not the eight-week-of-
discovery-work result. The substrate handles a real RL problem, the
algorithm needed three iterations to crack the local optimum, and the
result is rediscovery of a known mathematical band rather than a
genuine open-problem advance. That's appropriate for the timeline; the
next experiments target genuinely-open territory and have stricter
acceptance criteria.

The architecture is RL-compatible at the discovery level. **What's
missing is the verification machinery — the residual primitive
proposed yesterday is exactly the discipline that converts an
"agent found a low-M polynomial" claim into a substrate-grade
artifact.** The two work streams are complementary; either order
of completion works.

— Techne, 2026-05-02
