# Simulation request — round-4 reviewer

**Context for paste:** The Prometheus team has just frozen design at v8. Per the original offer at the close of round 4 ("If you want, I can simulate likely outcomes of the first 10K-episode pilot — what distributions you should expect, and what would count as 'this is working' vs 'this is failing'"), we're now accepting that offer. Below is the v8-locked configuration the simulation should target.

---

## Request

Simulate likely outcomes of the first 10K-episode multi-arm pilot under the v8 architecture. Provide:

1. **Expected per-operator-class PROMOTE rate distributions** — point estimate + 80% credible interval per class
2. **Expected per-operator-class signal-class-residual rate distributions** — same
3. **Expected `residual_signal_precision` per class** — under three classifier-quality scenarios (low: 70% accuracy / 8% FP on synthetic structured-noise; medium: 85% / 4%; high: 92% / 1%)
4. **Expected correlation residual→PROMOTE** — per class, under each classifier-quality scenario
5. **Concrete go/no-go criteria** — under what observed numbers should the team continue to v0.5 vs pause for architectural revision vs revert to PROMOTE-only reward

---

## V8 architecture summary (paste-ready)

Seven mutation operator classes contributing to a single MAP-Elites archive:

| Class | Operator | Min share |
|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges within type discipline | — |
| `symbolic` | Bump arg values within type | — |
| `neural` | LoRA-fine-tuned policy mutation (NOT in MVP — present at v0.5+) | — |
| `external_llm` | Frontier LLM API mutation (NOT in MVP) | — |
| `anti_prior` | Anti-correlated with corpus frequency stats; KL ≥1.0 nat per claim; descriptor-displacement requirement | ≥5% |
| `uniform` | Resample atoms uniformly | ≥5% |
| `structured_null` | Per-type sampler with uniform per-arg distributions | ≥5% |

Total non-prior-shaped operators: ≥15% of all proposals (scheduler-enforced).

**MVP arms (no neural policy yet):** `structural`, `symbolic`, `anti_prior`, `uniform`, `structured_null` — five arms. v0.5 adds `neural` and `external_llm`.

## Reward formula (v8)

```
reward = w_S * substrate_pass_indicator           # 0.40
       + w_X * cross_model_logical_consistency    # 0.15 (DAG-consistency only, NOT discovery-judgment)
       + w_H * holdout_battery_pass_indicator     # 0.20
       + w_NL * non_llm_evaluator_pass            # 0.10 (numeric perturbation for Lehmer-Mahler)
       + w_R * signal_class_residual_indicator    # 0.15 (CONDITIONAL on classifier benchmark passing)
```

w_R activation tiered by classifier benchmark FP-rate on 100 synthetic-structured-noise samples:
- ≤2% (95% CI ≤4.7%): full 0.15
- ≤5% (CI ≤9.4%): half 0.075
- ≤10%: 0 (escrow — diagnostics only)
- >10%: 0 (deep escrow)

Plus ECE ≤0.05 across 5 bins required for any non-zero w_R.

Cross-model agreement-novelty paired check: if cross-model agreement is ≥0.9 AND descriptor distance to nearest catalog entry is in bottom quintile, agreement contribution multiplied by 0.5.

## Five-axis content-aware MAP-Elites descriptor (5,000 cells: 4 × 5 × 10 × 5 × 5)

1. Output canonicalizer subclass (4 categorical: group_quotient / partition_refinement / ideal_reduction / variety_fingerprint)
2. Equivalence-class entropy of DAG (5 quantile buckets)
3. Output-type signature (~10 categorical)
4. Output magnitude bucket (5 *bounded* ranges: [10⁰, 10³), [10³, 10⁶), [10⁶, 10⁹), [10⁹, 10¹²), [10¹², ∞); high buckets require perturbation-stability check)
5. Output canonical-form distance (5 quantile buckets)

## Five-counts diagnostic per operator class

For each operator class, run N episodes. Report per class:
1. Catalog-hit rate
2. Claim-into-kernel rate (sub-Lehmer-band catalog miss → CLAIM)
3. PROMOTE rate (substrate-only AND agreement-weighted)
4. Battery-kill rate
5. Signal-class-residual rate (battery-killed CLAIMs with classifier confidence ≥0.7 for signal-class)

Statistical comparison: Welch t-test with Holm correction; both PROMOTE rate AND signal-class-residual rate.

## Empirical anchor: prior pilot result

At commit 1666c4a4, a 1000×3 four-counts pilot (uniform random vs REINFORCE on bandit env, not the v8 multi-arm DiscoveryEnv) produced 0 PROMOTEs in 3000 episodes. This bounds the PROMOTE rate at ≤10⁻³ in the Lehmer-Mahler domain at MVP descriptor resolution. Use this as a prior on v8 simulation rates.

## What "this is working" vs "this is failing" should look like

The simulation should distinguish:

- **Working at v8 commitment level:** at least one operator class out-PROMOTEs uniform random with p<0.05 corrected; signal-class-residual rate is denser than PROMOTE rate by ≥10×; correlation residual→PROMOTE ≥0.3
- **Working with caveats:** PROMOTE rate too sparse to differentiate (joint upper bound), but signal-class-residual rate differentiates classes; correlation residual→PROMOTE ≥0.3 — proceed with reduced confidence
- **Failing at residual level:** signal-class-residual rate ≈ PROMOTE rate, OR correlation ≤0.3 — gradient is fake; revert to PROMOTE-only reward; substrate-grade negative result on residuals-as-reward
- **Failing at architecture level:** no operator class beats uniform random on EITHER PROMOTE rate OR signal-class-residual rate at p<0.05 — engine is not contributing signal beyond noise

## Specific question: classifier-quality dependency

The architecture's bear case is the residual-gaming attractor — the system optimizes for looking like signal, not being signal. The simulation should model:

- Under the *low* classifier-quality scenario (FP=8%): how much does the residual reward signal pull the policy toward gaming-attractor outputs vs real-signal outputs?
- Under the *medium* scenario (FP=4%): does the half-strength w_R activation prevent gaming?
- Under the *high* scenario (FP=1%): is full w_R activation sustainable?

These three scenarios bracket the realistic post-Trial-1 calibration outcomes.

## Format for the response

Whatever's natural for the simulating model — tables, narrative, plots-described-in-text. The team will absorb the simulation as a-priori expected-distribution baseline against which actual MVP results compare.

Reference docs available if needed: `pivot/ergon_learner_proposal_v5.md` (full architectural treatment), `pivot/ergon_learner_proposal_v8.md` (focused delta), `harmonia/memory/architecture/discovery_via_rediscovery.md`.

— Ergon
