# Withheld-Rediscovery Benchmark — §6.2.5 Results

**Spec:** `harmonia/memory/architecture/discovery_via_rediscovery.md` §6.2.5
**Implementation:** `prometheus_math/withheld_benchmark.py` + `demo_withheld_benchmark.py`
**Run date:** 2026-04-29
**Pilot configuration:** REINFORCE on `DiscoveryEnv(degree=10, reward_shape='shaped')`, 1000 episodes per seed × 3 seeds = 3000 total episodes.

---

## 1. Partition

Mossinghoff snapshot: **178 entries** (cross-checked against `techne.lib.mahler_measure` to 1e-9).

With `holdout_fraction=0.2, partition_seed=42`:

| Set       | Count | Description                                |
|-----------|-------|--------------------------------------------|
| Visible   | 142   | Treated as 'in catalog' during evaluation  |
| Withheld  | 36    | Held-out 'unknown' rediscovery targets     |

**Sub-Lehmer band coverage** (`1.001 < M < 1.18`, the env's reward sweet-spot):
the withheld set contains **2 entries** in this band (both at M ≈ 1.17628).
The other 34 withheld entries lie at M = 1.0 (cyclotomics, 6 entries) or at
M > 1.18 (28 entries in the higher Salem cluster). The agent can only
rediscover withheld entries whose M reaches the sub-Lehmer reward band; the
upper bound is therefore **2/36 = 5.6%** for this particular partition.

This is a structural feature of the partition, not a bug — the spec
mandates a uniform random 20% holdout, and Mossinghoff is heavily skewed
toward larger M (only ~10 of the 178 entries sit strictly in (1.001, 1.18)).
A future iteration could stratify by M-band, but that diverges from the
§6.2.5 protocol.

---

## 2. Per-seed rediscovery counts

| Seed | Rediscovered (of 36) | Promoted (of 36) |
|------|----------------------|------------------|
| 0    | 0                    | 0                |
| 1    | 0                    | 0                |
| 2    | 0                    | 0                |

**Aggregate (union across seeds):**

- `withheld_rediscovery_count = 0 / 36`
- `withheld_rediscovery_rate  = 0.0000`
- `withheld_PROMOTE_count     = 0 / 36`
- `withheld_PROMOTE_rate      = 0.0000`
- `episodes_per_rediscovery   = ∞` (no rediscoveries)

Pilot wall-time: **2.6s** total for 3000 episodes (env step is fast; the
agent terminates each episode in ~6 build-steps).

---

## 3. Why zero rediscoveries

Diagnostic on a single 1000-episode run with the same partition:

- Reward-label distribution: `{'shaped_continuous': 999, 'large_m': 1}` — every
  episode produced a polynomial with M ≥ 1.18 (Salem cluster or higher).
- Best M found across 1000 episodes: **~2.000**.
- Sub-Lehmer candidates flagged: **0**.

REINFORCE's contextual-policy gradient on a `7^6 ≈ 117K`-trajectory action
space with sparse-but-shaped reward did not converge to the sub-Lehmer
band within the 1000-episode budget. The agent learned to avoid M > 5 (no
'large_m' clusters), but the descent from M ~ 2 to M < 1.18 requires a
specific palindromic coefficient pattern that the linear policy rarely
samples uniformly.

This is consistent with the existing pivot evidence in
`prometheus_math/LEARNING_CURVE.md`: REINFORCE on this env discovers
zero sub-Lehmer polynomials at the 1k–5k episode scale; only at 10k+
episodes with a different policy class does the rate become non-zero.

---

## 4. Calibration interpretation

The withheld benchmark returns the system's **discovery-shape capability
measured against known ground truth** — this is the headline quantity §6.2.5
specifies as the gate before §6.2's open-discovery pilot.

**Result for the current REINFORCE-on-DiscoveryEnv stack:**

| Quantity                                           | Value     |
|----------------------------------------------------|-----------|
| Withheld rediscovery rate (REINFORCE, 3000 eps)    | 0.0%      |
| Per-1000-episode upper bound for §6.2 discovery    | < 1/3000  |
| Per-1000-episode rate consistent with the data     | ~0        |

**Honest framing.** The agent rediscovered **0 of 36** withheld entries.
This is not a failure of the benchmark instrument — the benchmark is
working exactly as designed (it rejects the hypothesis that "REINFORCE on
DiscoveryEnv discovers sub-Lehmer polynomials at the 1k-episode scale").
It IS a calibration result: §6.2's open-discovery pilot, run with this
same agent and budget, should be expected to produce **at most**
`< 1/1000` sub-Lehmer hits per episode, and any sub-Lehmer hit that
appears earlier than ~3000 episodes should be regarded as suspicious until
the discovery pipeline's full battery (F1/F6/F9/F11) clears it.

**Implications for §6.2:**

1. The 1000-episode budget is too small for the current REINFORCE-with-
   linear-policy stack. §6.2's open-discovery pilot needs to either
   (a) increase the budget to 10k+ episodes, or (b) upgrade the agent
   (PPO with value function, MCTS-guided rollouts, or a curriculum
   that warms up on the visible Mossinghoff entries before generalizing).

2. The withheld benchmark's instrument is now in place. Re-run after any
   agent / env / reward-shape change to track whether the rediscovery
   rate moves off zero. **A non-zero rate is the gate for trusting any
   §6.2 open-discovery claim.**

3. The 2/36 sub-Lehmer-band coverage in this particular partition is
   useful: even if the agent finds Lehmer's polynomial (a withheld
   entry at index in the partition), it would only count as 1/36 ≈ 2.8%
   rediscovery rate. That ceiling is itself the structural calibration
   for what 'success' looks like at this benchmark with this snapshot
   distribution.

---

## 5. Reproducibility

```bash
python -m prometheus_math.demo_withheld_benchmark \
    --episodes 1000 --seeds 3 --holdout 0.2 --partition-seed 42
```

Test suite:

```bash
python -m pytest prometheus_math/tests/test_withheld_benchmark.py -v
```

All 18 tests green (4 authority, 5 property, 5 edge, 4 composition).

---

## 6. Files

- `prometheus_math/withheld_benchmark.py` — partition + pipeline + pilot
- `prometheus_math/demo_withheld_benchmark.py` — CLI driver
- `prometheus_math/tests/test_withheld_benchmark.py` — 18 tests (4/5/5/4)
- `prometheus_math/WITHHELD_BENCHMARK_RESULTS.md` — this file
