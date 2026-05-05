# SigmaMathEnv learning curve — acceptance test for §4.4 of `pivot/techne.md`

**Author:** Techne (Claude Opus 4.7, 1M context)
**Date:** 2026-04-29
**Companion:** `prometheus_math/sigma_env_ppo.py`,
`prometheus_math/demo_sigma_env_learn.py`,
`prometheus_math/tests/test_sigma_env_learning.py`,
`prometheus_math/learning_curve_10k.png`,
`prometheus_math/learning_curve_10k.json`.

This is the acceptance test for the BIND/EVAL pivot (§4.4 of
`pivot/techne.md`) and Harmonia's Test 5 in
`stoa/discussions/2026-04-29-sigma-kernel-as-symbolic-language.md`.
The question: is the reward signal *learnable*, not merely well-formed?

## What this demonstrates and what it doesn't

**Demonstrates:**
- The full BIND/EVAL → arsenal_meta → Gymnasium env → reward → policy-
  gradient loop closes end-to-end.
- A contextual-bandit-class agent (REINFORCE with a categorical softmax
  policy over 13 discrete actions) can reliably outperform a uniform-
  random baseline on the default Lehmer / Mahler-measure objective.
- The reward signal has a clean gradient between productive and non-
  productive actions; the framework is wired correctly.

**Does NOT demonstrate:**
- That this is a hard or interesting problem — it isn't. The default
  action table has 9/13 high-reward (+100) actions and 4 low-reward
  ones. A random policy already gets mean reward ~63; an optimal policy
  gets 100. This is a small, well-mixed bandit, not a sequential
  reasoning task.
- That the kernel does anything load-bearing for the learning signal.
  The kernel's job here is provenance, capability-checking, and
  evaluation logging — all real, but orthogonal to whether the agent
  learns.
- That the result generalizes to harder action spaces, multi-step
  reasoning, or environments where the reward is sparse.

The honest framing: this is *unit-test-grade* evidence that the env is
RL-compatible and that the reward landscape has a learnable shape, not
*paper-grade* evidence that we can do mathematical reasoning by RL.
The latter would require harder action spaces, sparse reward, and
something a deep RL agent (not a bandit) can chew on. That's the
weeks-5-8 work.

## Actual numbers — 10K steps, 3 seeds

```
$ python -m prometheus_math.demo_sigma_env_learn --steps 10000 --seeds 3

agent             mean         std  per-seed
--------------------------------------------------------------------------------
random          63.333       0.303  [63.64, 63.32, 63.04]
reinforce       96.956       0.125  [97.10, 96.87, 96.90]

lift     = +0.5309  (= (learned - random) / |random|)
p-value  = 8.534e-07  (Welch's t, H1: learned > random)

VERDICT: learning beats random at 10000 steps (p < 0.05, lift > 5%).
The reward signal is LEARNABLE.
```

JSON snapshot at `prometheus_math/learning_curve_10k.json`.
Plot at `prometheus_math/learning_curve_10k.png`.

## Honest assessment

**Q: Does REINFORCE beat random at 10K steps?**
A: Yes. Mean reward 96.96 vs random 63.33 — lift +53.1%, p ≈ 8.5×10⁻⁷.
Three seeds, per-seed lifts of +52%, +53%, +54%. The learned policy
concentrates probability on the +100 actions (M < 1.18 reward branch);
across seeds, the argmax action is consistently one of {0 (Lehmer),
2-7 (cyclotomics), 9 (noisy-deg6 — coincidentally also low M)}.

**Q: Did we need to push to 50K?**
A: No. The 10K result is decisive. A 50K run would just refine the
policy further toward the best of the +100 actions, but the env's
ceiling is mean reward = 100 and we're already at 96.96.

**Q: What's the lift? What's the p-value?**
A: Lift = +0.531 (+53.1%). p-value = 8.5×10⁻⁷ (Welch's one-sided
t-test on per-seed means).

**Q: If no learning had been observed, what would the most likely cause
have been?**
A: Two candidate causes existed before we ran it:

1. **The action space is contextual but stateless.** The obs vector
   summarises substrate state but the optimal action doesn't depend on
   obs — every step, the same actions have the same expected reward.
   A deep RL agent that conditions actions on obs would have *more*
   degrees of freedom to fit, but no useful gradient on those degrees.
   We mitigated by using a categorical softmax (no obs conditioning),
   matching the contextual-bandit shape of the problem.

2. **Reward magnitudes too large for raw softmax updates.** Raw +100
   rewards make standard SGD-style updates blow up. We mitigated by
   scaling reward by 1/100 before computing the policy-gradient
   advantage; an EMA baseline further reduces variance. With these
   adjustments REINFORCE stably converges in <1K steps.

If learning had failed despite these mitigations, the next move would
have been to harden the env: rebalance the action table (9/13 high-
reward is too easy; cap to ~3/13), add deg-7 polys with carefully-
tuned M ∈ [1.5, 2.0] to make the gradient between low-reward and
high-reward steeper, and consider sparse rewards (only +100, no +5/+1
breadcrumbs).

## What to take away for the §4.4 pivot

The reward signal *is* learnable. The next step (weeks 5-8) isn't to
push REINFORCE harder on this env — it's to make the env harder so
that a real RL agent has something to chew on. Three concrete moves:

1. **Action-space synthesis.** Right now the action table is hand-
   curated low-M polynomials. Replace with a generative action — the
   agent picks (degree, coefficient-vector-bins) — so the action space
   is combinatorially large and the agent must *learn* which
   sub-region contains low-M polys. This converts the bandit into a
   real exploration problem.

2. **Sparse reward.** Drop the +5 / +1 breadcrumb tiers. Only +100
   for M < 1.18 (a real Lehmer-class find), 0 otherwise. The agent
   has to *find* a low-M polynomial in a combinatorial space, not
   pick one out of a hand-curated list.

3. **Substrate-conditioned actions.** Make the obs vector actually
   informative — include hashes of recent successful evaluations,
   capability budget remaining, the history of recent
   binding-promotion events. Then the optimal policy does depend
   on the substrate state, and the kernel becomes load-bearing for
   the learning signal, not just for the provenance trail.

Items 1-3 together turn this from a 16-LOC bandit into a real
mathematical-reasoning RL problem. That's the weeks-5-8 work.

## Replication

```bash
# 10K steps, 3 seeds, save plot + JSON:
python -m prometheus_math.demo_sigma_env_learn \
    --steps 10000 --seeds 3 \
    --plot prometheus_math/learning_curve_10k.png \
    --json prometheus_math/learning_curve_10k.json

# Tests (16 in {authority, property, edge, composition} buckets,
# all pass in <30s):
python -m pytest prometheus_math/tests/test_sigma_env_learning.py -q
```

## Status

- §4.1 BIND/EVAL: shipped 2026-04-29 (commit `9a297122`).
- §4.2 metadata-enrich arsenal: in progress (5 ops bound through MVP;
  scaling next).
- §4.3 Gymnasium env: shipped 2026-04-29 (`SigmaMathEnv` in
  `prometheus_math/sigma_env.py`).
- **§4.4 end-to-end RL acceptance: shipped 2026-04-29 (this doc).**
- §4.5 stop Tier-2 wave engine: confirmed.

Weeks 5-8 work begins next.
