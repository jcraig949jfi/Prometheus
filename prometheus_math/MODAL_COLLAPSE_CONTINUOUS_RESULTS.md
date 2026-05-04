# Modal-Collapse Continuous-Reward Diagnostic — Results

**Date:** 2026-05-04
**Author:** Techne (executing Aporia's Day-2 specification)
**Code:** `prometheus_math/modal_collapse_continuous.py`
**Tests:** `prometheus_math/tests/test_modal_collapse_continuous.py` (15/15 passing)
**Raw results:** `prometheus_math/_modal_collapse_continuous_results.json`
**Day-1 baseline (preserved as regression):** `prometheus_math/modal_collapse_synthetic.py` (16/16 passing)
**Wall clock:** 32.7 s for the full 3 × 4 × 3 × 3 × 5 000 grid (1 620 000 episodes)

---

## TL;DR — Verdict

**Case A persists.**

Swapping the binary 0/1 reward for a continuous reward (L2, L1, or log distance to true y) does **not** break modal collapse. Across all three reward shapes, all four env variants, and all three seeds:

- **REINFORCE-linear collapses to 2–3 active bins** on every single cell (top-3 mass ≥ 99.3 %).
- **PPO-MLP stays uniform** across all 21 bins on every cell (top-3 mass ≈ 15 % = 3/21), at exactly random-baseline accuracy.
- **On V3 (the decisive lstsq-solvable variant where a 26-parameter linear fit achieves ≥ 60 % bin accuracy in 1 000 samples)**: best REINFORCE = **9.08 %** (L2), best PPO = **4.74 %** (L2). The lstsq gold standard is **>6× higher** than either.

Continuous reward does not fix Layer 2. Kill-vector navigation (or a different intervention at the search-mechanism layer) is required.

---

## Setup

The env, observation, ground-truth `y = w·x + b + ε`, action space (21 bins), and four variants (V1 balanced, V2 skewed, V3 low-noise, V4 skewed + high σ) are **identical** to `modal_collapse_synthetic` (Day 1). The trainers are byte-for-byte mirrors of the binary trainers — same learning rate, same network shape (32-hidden ReLU MLP for PPO; linear softmax for REINFORCE), same entropy coefficient, same baseline decay, same PPO clip ε, same minibatch size.

**The only change is the reward signal.** The action remains a discrete bin index k ∈ [0, 21); we map it to the bin-center y, then compute continuous error against the true y:

| Reward variant | Formula                                          | Calibration                          |
|----------------|--------------------------------------------------|--------------------------------------|
| L2             | `reward = -scale × (predicted_y - true_y)²`      | scale = 100 / 9   (worst err ≈ 3σ)   |
| L1             | `reward = -scale × |predicted_y - true_y|`       | scale = 100 / 3                      |
| log            | `reward = -scale × log(1 + |predicted_y - true_y|)` | scale = 100 / log(4)                |

All three rewards are clipped to `[-REWARD_FLOOR, 0]` with `REWARD_FLOOR = 100`, so the dynamic range matches the binary case (`{0, 100}`) and the trainer's `reward_scale = 1/100` produces commensurate advantage magnitudes. **Only the shape of the gradient surface changes.**

Total budget: 3 reward variants × 4 env variants × 3 algorithms × 3 seeds × 5 000 episodes = **540 000 episodes per reward shape**, 1 620 000 episodes overall, 32.7 s wall clock.

**Authority gate (passing in test suite):** the lstsq linear-fit baseline still solves V3 at ≥ 60 % bin accuracy. The env hasn't changed — only the trainer's reward signal has.

---

## Results — 3 Reward Variants × 4 Env Variants × 3 Algorithms

Mean ± std over 3 seeds, 5 000 episodes per cell. "Active bins" = bins capturing ≥ 1 % of mass. "Top-3 mass" = fraction of predictions in the top-3 most-used bins (the modal-collapse signature: ≥ 0.99 means the agent is essentially playing 3 actions out of 21).

### Reward = L2 (`-error²`, scaled to [-100, 0])

| Variant         | Agent     | Accuracy           | Resolution | Active bins | Top-3 mass |
|-----------------|-----------|--------------------|------------|-------------|------------|
| V1 balanced     | random    | 0.0475 ± 0.0011   | 0.141      | 21 / 21     | 0.150      |
| V1 balanced     | REINFORCE | 0.0887 ± 0.0063   | 0.268      | **2 / 21**  | **0.997**  |
| V1 balanced     | PPO       | 0.0452 ± 0.0024   | 0.136      | 21 / 21     | 0.153      |
| V2 skewed       | random    | 0.0464 ± 0.0012   | 0.120      | 21 / 21     | 0.150      |
| V2 skewed       | REINFORCE | 0.0241 ± 0.0008   | 0.072      | **2 / 21**  | **0.993**  |
| V2 skewed       | PPO       | 0.0451 ± 0.0029   | 0.117      | 21 / 21     | 0.154      |
| V3 low-noise    | random    | 0.0484 ± 0.0015   | 0.142      | 21 / 21     | 0.150      |
| **V3 low-noise**| REINFORCE | **0.0908 ± 0.0040** | 0.259    | **3 / 21**  | **0.996**  |
| **V3 low-noise**| PPO       | **0.0474 ± 0.0027** | 0.137    | 21 / 21     | 0.153      |
| V4 skewed+highσ | random    | 0.0460 ± 0.0019   | 0.116      | 21 / 21     | 0.150      |
| V4 skewed+highσ | REINFORCE | 0.0239 ± 0.0015   | 0.071      | **2 / 21**  | **0.995**  |
| V4 skewed+highσ | PPO       | 0.0455 ± 0.0032   | 0.119      | 21 / 21     | 0.153      |

### Reward = L1 (`-|error|`, scaled to [-100, 0])

| Variant         | Agent     | Accuracy           | Resolution | Active bins | Top-3 mass |
|-----------------|-----------|--------------------|------------|-------------|------------|
| V1 balanced     | random    | 0.0475 ± 0.0011   | 0.141      | 21 / 21     | 0.150      |
| V1 balanced     | REINFORCE | 0.0801 ± 0.0127   | 0.237      | **3 / 21**  | **0.996**  |
| V1 balanced     | PPO       | 0.0451 ± 0.0027   | 0.136      | 21 / 21     | 0.154      |
| V2 skewed       | random    | 0.0464 ± 0.0012   | 0.120      | 21 / 21     | 0.150      |
| V2 skewed       | REINFORCE | 0.0243 ± 0.0007   | 0.070      | **3 / 21**  | **0.995**  |
| V2 skewed       | PPO       | 0.0453 ± 0.0026   | 0.117      | 21 / 21     | 0.153      |
| V3 low-noise    | random    | 0.0484 ± 0.0015   | 0.142      | 21 / 21     | 0.150      |
| **V3 low-noise**| REINFORCE | **0.0810 ± 0.0143** | 0.240    | **3 / 21**  | **0.997**  |
| **V3 low-noise**| PPO       | **0.0469 ± 0.0032** | 0.137    | 21 / 21     | 0.154      |
| V4 skewed+highσ | random    | 0.0460 ± 0.0019   | 0.116      | 21 / 21     | 0.150      |
| V4 skewed+highσ | REINFORCE | 0.0258 ± 0.0025   | 0.075      | **3 / 21**  | **0.994**  |
| V4 skewed+highσ | PPO       | 0.0456 ± 0.0033   | 0.118      | 21 / 21     | 0.159      |

### Reward = log (`-log(1+|error|)`, scaled to [-100, 0])

| Variant         | Agent     | Accuracy           | Resolution | Active bins | Top-3 mass |
|-----------------|-----------|--------------------|------------|-------------|------------|
| V1 balanced     | random    | 0.0475 ± 0.0011   | 0.141      | 21 / 21     | 0.150      |
| V1 balanced     | REINFORCE | 0.0490 ± 0.0096   | 0.150      | **3 / 21**  | **0.996**  |
| V1 balanced     | PPO       | 0.0451 ± 0.0029   | 0.136      | 21 / 21     | 0.154      |
| V2 skewed       | random    | 0.0464 ± 0.0012   | 0.120      | 21 / 21     | 0.150      |
| V2 skewed       | REINFORCE | 0.0239 ± 0.0011   | 0.073      | **3 / 21**  | **0.994**  |
| V2 skewed       | PPO       | 0.0451 ± 0.0030   | 0.117      | 21 / 21     | 0.153      |
| V3 low-noise    | random    | 0.0484 ± 0.0015   | 0.142      | 21 / 21     | 0.150      |
| **V3 low-noise**| REINFORCE | **0.0702 ± 0.0106** | 0.216    | **3 / 21**  | **0.997**  |
| **V3 low-noise**| PPO       | **0.0468 ± 0.0034** | 0.137    | 21 / 21     | 0.154      |
| V4 skewed+highσ | random    | 0.0460 ± 0.0019   | 0.116      | 21 / 21     | 0.150      |
| V4 skewed+highσ | REINFORCE | 0.0226 ± 0.0034   | 0.072      | **3 / 21**  | **0.996**  |
| V4 skewed+highσ | PPO       | 0.0457 ± 0.0032   | 0.119      | 21 / 21     | 0.153      |

---

## Per-bin distribution diagnostic

The collapse signature on V3 is identical across reward shapes. REINFORCE concentrates ~33 % each on three adjacent central bins; PPO is uniform.

| Reward | REINFORCE V3 top-3 bins (mass)            | PPO V3 top-3 bins (mass)              |
|--------|-------------------------------------------|---------------------------------------|
| L2     | b8=0.33, b11=0.33, b12=0.33 (top3=0.996)  | b2=0.05, b11=0.05, b12=0.05 (top3=0.153) |
| L1     | b8=0.33, b14=0.33, b11=0.33 (top3=0.997)  | b2=0.05, b11=0.05, b12=0.05 (top3=0.154) |
| log    | b14=0.33, b8=0.33, b13=0.33 (top3=0.997)  | b2=0.05, b11=0.05, b12=0.05 (top3=0.154) |

Compare Day 1 (binary reward) on V3: REINFORCE top-3 mass = **0.991** in 3 bins, PPO uniform.

The continuous reward shifts *which bins* REINFORCE selects (it now picks bins whose centers are closest to the true y-mean, which is the L2/L1-optimal point estimate), but it **does not widen the support**.

---

## Did any reward variant break modal collapse?

**No.**

| Reward | REINFORCE active bins on V3 | PPO active bins on V3 | Best V3 accuracy | lstsq baseline |
|--------|------------------------------|------------------------|------------------|---------------|
| binary | 3 (Day 1)                    | 21 (uniform, Day 1)    | 4.91 %           | ≥ 60 %        |
| **L2** | **3**                        | **21 (uniform)**       | **9.08 %**       | ≥ 60 %        |
| **L1** | **3**                        | **21 (uniform)**       | **8.10 %**       | ≥ 60 %        |
| **log**| **3**                        | **21 (uniform)**       | **7.02 %**       | ≥ 60 %        |

REINFORCE's V3 accuracy ticks up from 4.9 % → 9.1 % under L2, but this is **not learning the linear map**. With only 3 active bins and the agent's predictions concentrated near y=0 (the L2-optimal scalar estimate), the modest accuracy lift comes from the **prior** (the central bins of a balanced env naturally have higher y-density) — not from any input-dependent map. Resolution score on V3 (within ±1 bin) is 0.27 vs random 0.14: this is "near-mean betting", not signal extraction.

PPO's V3 accuracy stays at random across all three reward shapes. The MLP gradient on the continuous reward provides no more usable signal than the binary reward did.

---

## The Verdict — Case A persists

The classifier `_classify_verdict` returns `A_persists`:

- For all three reward variants, on V3, **neither REINFORCE nor PPO** reaches accuracy ≥ 4× random with active_bins ≥ 8.
- For all three reward variants, on V3, **neither REINFORCE nor PPO** even reaches accuracy ≥ 2× random with active_bins ≥ 8 (the partial-improvement criterion).

**The two collapse signatures are unchanged.** REINFORCE still collapses to 2–3 bins. PPO still goes uniform-at-random. Continuous reward changes the location and magnitude of REINFORCE's collapse without breaking it.

### Why continuous reward didn't help

Two complementary diagnoses:

1. **The gradient surface is still single-channel.** L2/L1/log all return a *scalar* signal that says "you are this far from the right answer". For a 21-way categorical policy, that scalar gets distributed across 21 logits via the policy gradient identity — and the entire vector update is rank-1 (it's `advantage × ∇log π(a|s)`). The continuous reward does *not* tell the agent "the answer was bin 13, not bin 8"; it only says "you got 0.34 less reward this time". Modal collapse persists because, although the *gradient* is now non-zero almost everywhere, it is still **directionally ambiguous about which other action would have helped.**

2. **REINFORCE finds the L2-optimal collapse.** Under L2 reward with no input dependence, the optimal *constant* policy puts all probability on the bin whose center is closest to E[y]. With balanced binning, that's the central bins; with skewed binning, that's a less-favored bin (and indeed REINFORCE on V2/V4 does *worse* than random — 2.4 % vs 4.6 % — because it's collapsing to the L2-optimum, not the modal class). Continuous reward changes the collapse target; it does not break the collapse.

This is consistent with ChatGPT's reframe: the binary reward "projects the gradient away" at the bin boundary, and continuous reward restores *some* gradient. But the restored gradient is the *wrong shape* — it pushes the policy toward a single optimal *constant* rather than toward the *map* `x → bin(w·x + b)`.

---

## Implication for the kill-vector / continuous-reward design choice

**Continuous scalar reward is insufficient. Kill-vector navigation is required.**

The Day-2 question was whether the simplest Layer-2 fix (continuous scalar reward) would break modal collapse. The answer is decisive: **no.** Three different continuous reward shapes (L2, L1, log), each calibrated to match the binary case's dynamic range and gradient magnitude, all leave the collapse signatures intact:

- REINFORCE: 2–3 active bins on every cell.
- PPO: uniform-at-random on every cell.
- V3 best accuracy: 9.1 % vs lstsq's 60 %+.

This means the bottleneck is not "the reward is sparse" — it is "the reward is *unidirectional and unstructured*". A scalar signal cannot tell a 21-way categorical policy *which other action* would have been better. Kill-vector navigation provides that structure: instead of one scalar per step, the trainer receives a structured signal that names the bin axis (or axes) along which the prediction was wrong, allowing the gradient to point at the right *neighbor* of the current action rather than just away from the current loss.

**Design priority going forward:** continuous-reward shaping is not a pre-requisite for the kill-vector intervention. They are not sequential; the kill-vector design directly addresses the failure mode that all three continuous rewards left intact. Kill-vector navigation is the **actual upgrade**.

### Caveats

- 5 000 episodes is the same budget Day 1 used. It is plausible (though not visible in the per-seed std bars) that 50 000+ episodes with continuous reward might eventually break collapse on V3 specifically. The std on REINFORCE V3 accuracy (0.0040–0.0143) is small relative to the gap to lstsq, so this would have to be a **very** slow phase transition. The current evidence is decisively against it within the budget that matches the real-domain experiments that motivated the diagnostic.
- The reward calibration (REWARD_FLOOR = 100) was chosen so the trainer hyperparameters didn't have to change. If the hyperparameters themselves are the bottleneck, this test wouldn't catch it. But the symmetric finding — REINFORCE's collapse target *moves* under continuous reward, just doesn't *widen* — argues the hyperparameters are not the issue.
- The continuous reward gives REINFORCE genuine info on V1 (acc 0.088 > random 0.048, ~1.9× lift) — but at 2-bin width and resolution score 0.268 vs random 0.141, this is the modal-prior gambit, not learned signal. The lift on V1 evaporates on V3 (lstsq territory) and inverts on V2/V4 (skewed prior). This is a clean signature of "agent learned the y-prior, not the x→y map" — exactly the failure mode Day 1 identified, just with a different victim.

---

## Files

- `prometheus_math/modal_collapse_continuous.py` (~440 LOC) — env reuse, three continuous-reward variants, bin-center mapping, three trainers, run_diagnostic, _classify_verdict.
- `prometheus_math/tests/test_modal_collapse_continuous.py` (15 tests, ~225 LOC) — authority (4), property (3), edge (4), composition (4). All passing.
- `prometheus_math/_modal_collapse_continuous_results.json` — raw 3 × 4 × 3 × 3 grid.
- `prometheus_math/_run_modal_collapse_continuous.py` — one-shot driver.
- `prometheus_math/modal_collapse_synthetic.py` — **unmodified** (Day-1 regression preserved; 16/16 tests still pass).
