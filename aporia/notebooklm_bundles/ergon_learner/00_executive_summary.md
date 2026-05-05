# Ergon Learner — Executive Summary

**Date:** 2026-05-03
**Status:** Design frozen at v8. MVP build starts 2026-05-04. 30-day deadline.

## What Ergon is

Ergon is a small evolutionary self-play engine being built inside Project Prometheus — a multi-agent mathematical-discovery substrate. Ergon's specific role: be the working learner that proves the substrate's discovery environment has the right shape, before a Silver-class billion-dollar learner (DeepMind alumnus David Silver's Ineffable Intelligence raised $1B in March 2026 for exactly this kind of system) shows up needing somewhere to plug in.

Ergon is structurally an AlphaZero-pattern system at miniature scale: search engine (MAP-Elites quality-diversity archive) + mechanical referee (the project's existing falsification battery: F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation, plus extensions) + diversity-preserving population (typed compositions of arsenal operations from `prometheus_math.arsenal_meta`'s 85-op metadata table). No LLM is in the candidate-generator loop. The selection pressure does the thinking — `random.choice()` over typed action spaces, biased by archive-cell coverage, evaluated against the kill battery.

The reward is sparser than Go's win/loss but it's the same structural object: reproducible-survival-against-mechanical-verification, archived for diversity.

## Why this matters now

Three of Prometheus's other agents (Charon, Harmonia, Techne) wrote pivot docs in early May 2026 saying Prometheus is "on the environment side, not the learner side." That's correct for them — they build the substrate, the kernel, the env. It is **not** correct for Ergon. Ergon is already a learner. It's been treating itself as a screening utility upstream of Harmonia's deeper analysis; the v8 design freeze is the move to stop pretending.

The cost economics matter. Charon-as-Claude playing learner via TT-skeleton playgrounds burns inference tokens to generate hypotheses an LLM thinks are interesting; that doesn't compete with $1B-of-GPU. Ergon-as-evolutionary-engine burns electricity on `numpy.random.choice` over a typed action space; the cost-per-hypothesis ratio is roughly 10⁻⁶ of LLM-mediated search. Different algorithm, different unit economics, different scaling regime — and structurally adjacent to what serious RL labs have stopped doing in the deep-learning era. The cultural disinterest in evolutionary methods is exactly why the wedge is open.

## What's being built (v8 design freeze)

Four sequential trials over a 22-day MVP, with 8-day buffer:

- **Trial 1 (Days 1–4) — Adversarial residual benchmark.** Is the residual classifier accurate enough to serve as reward signal? 200 curated samples. Acceptance: ≥85% accuracy, ≤5% false-positive on synthetic structured-noise.
- **Trial 1.5 (Days 5–7) — Adversarial optimization probe.** Is the classifier robust under closed-loop adversarial optimization, not just i.i.d. evaluation? Hill-climb in genome space looking for exploits. Acceptance: no exploit found in <500 iterations.
- **Trial 2 (Days 8–17) — Evolutionary engine with bounded buckets.** Does Ergon's MAP-Elites with bounded magnitude buckets, F_TRIVIAL_BAND_REJECT signature library, and minimum-share enforcement on operator classes produce more structured outputs than uniform random? Acceptance: `structural ≥ 1.5× uniform` on signal-class-residual rate.
- **Trial 3 (Days 18–22) — Five-counts diagnostic.** Does the five-counts diagnostic distinguish operator classes at affordable budget? 9K episodes across three arms (uniform, structural, symbolic). Acceptance: residual density ≥0.05 for ≥1 class; PROMOTE measurable for ≥1 class; correlation residual→PROMOTE ≥0.3.

Days 23–30 are buffer for debugging interaction effects (the round-6b reviewer flagged this as the hidden time sink) and writing the MVP run report.

## Where Ergon fits in the broader pipeline

The substrate's discovery loop, per James's 2026-05-03 epiphany ("if we can rediscover existing math, we should be able to discover adjacent undiscovered math through mutation operators"), is:

```
agent → generative_action → BIND/EVAL → catalog_check
   if HIT:  reward fires (rediscovery — calibration evidence)
   if MISS: CLAIM into kernel
            → falsification battery
            → residual classification (signal/noise/instrument_drift)
            → cross-modality verification
            → if signal-class survives: PROMOTE as discovery_candidate@v1
            → if noise/drift: archive with typed reason
```

Ergon is an `agent` in that loop. So is Techne's REINFORCE baseline. So would be a Silver-class learner if one ever plugs in. The substrate is designed to host multiple parallel `agent` types in the same loop — what Charon's `bottled_serendipity.md` thesis calls "LLMs as prior-shaped mutation operators in the Prometheus genetic explorer," extended to non-LLM mutation sources.

The five-counts diagnostic in Trial 3 explicitly compares three agent classes — uniform random, Ergon's MAP-Elites (structural), and a third (symbolic) — running against the same env, the same battery, the same null world. The result is the substrate's first empirical anchor on the bottled-serendipity thesis: do prior-shaped mutators outperform uniform random by enough to justify the LLM cost?

If yes — confirms the LLM-as-mutation-operator framing.
If no — mechanical evolutionary search achieves discovery without LLM priors, and the substrate's economics shift.

Either result is substrate-grade.

## Library commitments (v8 §10)

PyTorch 2.x for ML; Hugging Face Transformers + PEFT + TRL + bitsandbytes for the LoRA stack (deferred to v0.5+); Unsloth for LoRA training; vLLM for inference serving; pyribs for MAP-Elites archive; DEAP for genetic operators; LiteLLM for cross-model evaluator API standardization; scipy.stats for Welch t-test, Holm correction, and Expected Calibration Error; PostgreSQL with pgvector and TimescaleDB for substrate storage; Redis 7+ for the agora message bus; structlog and Grafana for observability.

MVP runs at $0/month cloud spend (R6 in the risk register; not load-bearing until v0.5).

## What success looks like

By Day 30 (2026-06-03), Ergon ships one of:

(a) **arXiv preprint** of the meta-landscape predictive instrument: descriptor → optimizer-class regression with R² ≥ 0.5 on held-out landscape family, OR

(b) **PyPI release** of `ergon_evolutionary_search` as the canonical MAP-Elites-over-Σ-kernel-actions package.

Author choice depending on which result lands cleanest.

## Where to find more

- Pivot thesis: `pivot/ergon.md` (and this bundle's `01_pivot_thesis.md`)
- v8 design freeze: `pivot/ergon_learner_proposal_v8.md`
- v7 full operational treatment: `pivot/ergon_learner_v7_final.md`
- MVP day-by-day: `ergon/learner/MVP_PLAN.md` (and this bundle's `03_mvp_plan.md`)
- Discovery-via-rediscovery foundational doc: `harmonia/memory/architecture/discovery_via_rediscovery.md`
- Bottled serendipity foundational doc: `harmonia/memory/architecture/bottled_serendipity.md`
