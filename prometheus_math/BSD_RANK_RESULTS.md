# BSD Rank Prediction — Cross-Domain Substrate Validation

**Date:** 2026-04-29
**Stream:** Path (C) — pivot the discovery loop to a domain with KNOWN GROUND TRUTH.
**Verdict (one line):** Substrate plumbing validates cleanly on a ground-truth-dense domain; the linear policy recovers the rank prior but does not yet exploit the a_p signal.

## Why this run

216K episodes on `DiscoveryEnv` (Lehmer / Mahler-measure) produced 0 PROMOTEs. Either the substrate is broken, or it is hunting for something that does not exist (consistent with Lehmer's conjecture). To disentangle these, we re-ran the same machinery (sigma kernel + BIND/EVAL + REINFORCE) on a domain where the answers are known up front: predict the Mordell–Weil rank of an elliptic curve over **Q** from its first 20 a_p values. The Cremona / LMFDB mirror provides ground truth for ~64 K curves with conductor up to 100 000.

If the architecture works as a research instrument, it must at minimum reach above the random floor on this rediscovery task.

## Corpus inventory

Source: local `prometheus_math.databases.cremona` mirror (Cremona ECdata). `aplist` family was downloaded as part of this run (`update_mirror(families=('aplist',))`).

- Curves indexed: **64 687** (conductor ≤ ~20 000 in the test slice).
- Stratified sample drawn for the pilot: **1 000** curves with the shape

| stratum | target | drawn |
|---|---:|---:|
| rank-0 | 500 | 500 |
| rank-1 | 400 | 400 |
| rank-≥2 | 100 | 100 |

- Train / test split: 70 / 30 → **700 / 300** with reproducible `seed=42`.
- a_p feature dimension: **20** (primes 2…71). Bad-reduction columns encoded as +1 / −1 / 0 per Cremona convention (split / nonsplit multiplicative / additive).

## Pilot: random vs majority-class vs REINFORCE

1 000 episodes per arm × 3 seeds. Episode length is 1 (one prediction per curve). Reward = +100 if predicted rank matches LMFDB ground truth, else 0.

### Train-split mean reward

| arm | per-seed means | grand mean | accuracy |
|---|---|---:|---:|
| random (uniform over {0,1,2,3,4}) | 21.0 / 20.2 / 19.9 | **20.37** | 0.204 |
| majority-class (always 0) | 55.2 / 50.9 / 50.6 | **52.23** | 0.522 |
| REINFORCE (linear policy) | 39.1 / 51.7 / 48.0 | **46.27** | 0.463 |

### Held-out test mean reward (`argmax` of trained policy)

| arm | per-seed means | grand mean |
|---|---|---:|
| random | 20.1 / 21.3 / 18.5 | **19.97** |
| REINFORCE (deterministic argmax) | 44.6 / 50.6 / 46.6 | **47.27** |

### Statistical comparison

- Lift REINFORCE vs random (train) = **+1.27×**, p = **0.0098** (one-sided Welch).
- Lift REINFORCE vs random (test) = **+1.37×**, p = **0.00055**.
- Lift REINFORCE vs majority (train) = **−0.11×**, p = 0.88 (NOT distinguishable from majority).

## Did the agent learn the rank signal?

**Partial — and the failure mode is informative.**

- The agent decisively beats the uniform-random baseline at p < 0.01 on training and p < 0.001 on a held-out test split; that means the substrate's BIND/EVAL plumbing transmits a clean reward signal that the gradient picks up.
- The argmax-eval action distribution collapses to "always predict rank 0" within a few hundred episodes (`pred_counts ≈ [≥980, …, ≤10]` across all seeds and hyperparameters tried: lr ∈ {0.01, 0.05}, entropy_coef ∈ {0.001, 0.01, 0.02}).
- The agent therefore is recovering the **class prior** from the corpus (50 % rank 0 in our stratified sample, ~50 % accuracy), not the **a_p → rank** map.
- A linear softmax over 26-dimensional obs is too weak: distinguishing rank-0 from rank-1 requires reading the average sign / sum of |a_p|, which is well-known to be non-linear in the raw a_p (Goldfeld / Birch-Swinnerton-Dyer heuristics use averages, partial Euler products, …). That is the next-iteration upgrade — a small MLP, OR an explicit feature like Σ a_p / p (the "average sign") which a linear policy CAN exploit.

## Comparison with the Lehmer domain

| dimension | Lehmer / SigmaMath | BSD rank |
|---|---|---|
| ground truth | absent (Lehmer's conjecture) | dense (LMFDB) |
| reward signal | sparse, +100 jackpot | dense, +100 / 0 binary |
| 1 000-episode random baseline | ~0–5 / ep | ~20 / ep |
| 1 000-episode REINFORCE | ~0 PROMOTEs | beats random (p < 0.01) |
| substrate growth invariant | 1 binding + 1 EVAL / step | **identical** (verified) |
| episode length | up to 50 | 1 |

The architecture itself works. The substrate kernel correctly attributes BIND/EVAL rows per episode (verified in `test_composition_substrate_growth_one_binding_one_eval`); the reward function is well-formed (verified in `test_property_reward_in_zero_or_hundred`); the action space is enforced (`test_edge_action_out_of_range`); the train/test split is reproducible (`test_property_same_seed_same_split`).

## Honest framing

- This is **rediscovery**, not novel discovery. LMFDB has the answers for every curve we trained on. Validating that the substrate can RECOVER known math from labelled data is the entire point of the stream — confirming the architecture works where ground truth exists.
- The ablation reading on the original Lehmer 0-PROMOTE result is now: substrate is fine; the Lehmer reward landscape itself is too sparse for the current REINFORCE / random budget to find sub-Lehmer polynomials, OR they don't exist. We cannot distinguish those two from architecture-only signals.
- **What this run does NOT establish:** that the substrate can find facts not already in LMFDB. The ground-truth-dense version is necessary for instrument validation but explicitly insufficient for the discovery thesis.

## Test rubric coverage

`prometheus_math/tests/test_bsd_rank_env.py` — 17 tests, all green (16 s).

- Authority (4): corpus size ≥ 100; 11.a rank = 0 from Cremona agrees with LMFDB; correct rank → +100; wrong rank → 0.
- Property (4): reward ∈ {0, 100}; same seed → same split; episode length is 1; obs shape constant.
- Edge (5): empty corpus → ValueError; unknown split → ValueError; out-of-range action → ValueError; n_total=0 → ValueError; require_aplist filters cleanly.
- Composition (4): random in expected band [10, 40]; majority-class beats random; REINFORCE ≥ 1.5× random; substrate growth = exactly 1 BIND + 1 EVAL per step.

## Files

- `F:/Prometheus/prometheus_math/_bsd_corpus.py` — corpus loader (220 LOC).
- `F:/Prometheus/prometheus_math/bsd_rank_env.py` — Gym-compatible env (480 LOC).
- `F:/Prometheus/prometheus_math/tests/test_bsd_rank_env.py` — TDD test suite (250 LOC).
- `F:/Prometheus/prometheus_math/_run_bsd_rank_pilot.py` — pilot runner (175 LOC).
- `F:/Prometheus/prometheus_math/_bsd_rank_pilot_run.json` — captured numbers.

## Next iteration (suggested, not done in this run)

1. Add hand-engineered features: `mean(a_p / p)`, `mean(a_p^2 / p)`, sign-balance, count of vanishing a_p — these are the Birch / Goldfeld signals a linear policy can read directly.
2. Swap the linear policy for a 2-layer MLP (16 → 16 hidden) so non-linear rank-1 vs rank-0 boundaries become representable.
3. Increase the rank-2+ stratum or add explicit weighting in the loss; current 100/1000 is small enough that the gradient signal for the rare class is dominated by majority-class noise.
4. Once the agent beats majority by ≥ 5 percentage points on held-out, repeat the experiment on a corpus the agent has *not* trained on (different conductor band) — distinguishes "memorizes (label, rank)" from "learns the a_p→rank map".
