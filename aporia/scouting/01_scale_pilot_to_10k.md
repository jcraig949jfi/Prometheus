# Scout #1 — Scale §6.2 pilot to 10K episodes

**Tier:** T2 (substantive doc + targeted research)
**Front:** Rediscovery (closed-world calibration at proper scale)
**Cost:** 30-60 min compute, zero new code
**Techne's framing:** "Cheapest, most informative immediate next step. Just compute."
**Status:** Drafted; recommend Techne fires immediately.

---

## The test case

Run `prometheus_math/four_counts_pilot.py` at 10K episodes (vs the current 1K). The 1K run produced PROMOTE rate 0 with 463× proxy concentration. Spec target is 10K.

Pass conditions:
- **(a)** non-zero PROMOTE rate at 10K → publishable signal that the pipeline closes against ground truth at proper scale
- **(b)** still-zero PROMOTE rate at 10K → tighter joint upper bound on discovery rate, which is itself signal (narrows the structural ceiling)

Both outcomes are real information. There is no failure mode where the experiment produces nothing.

## Why it matters

This is the calibration test for the rediscovery tier of the three-tier ladder (per `2026-05-03-aporia-on-discovery-via-rediscovery.md`). Without it, every claim about discovery rate is unanchored. The 1K result is below the spec's confidence threshold; 10K is the substrate's first defensible measurement of "how often does a learner-driven loop produce something the catalog accepts?"

The 463× proxy concentration at 1K is an interesting secondary measurement: it says the policy is concentrating on specific neighborhoods, which is what RL is supposed to do. Whether that concentration is on real-promotable polynomials or on near-misses is what 10K resolves.

## State of the field

Prior art for "scale up the pilot before committing to a structural conclusion" in RL-for-math:

- **AlphaProof scaling regime.** DeepMind's IMO 2024 result reportedly used multiple days of compute per problem at inference time. Their training-time pilot scale before publishing was vastly larger than 10K episodes — ~10^7-10^8 according to inferred compute budget. This isn't a fair comparison to Prometheus's local-machine scale, but it sets the methodological precedent: "we ran small to debug, then we ran large to measure."
- **DreamCoder** (Ellis et al., PLDI 2021) ran wake-sleep cycles at 10^4-10^5 episodes per task before claiming convergence. Their pilots at 10^3 routinely produced zero-success rates that resolved at higher scale.
- **AlphaCode** (Li et al., Science 2022) generated ~10^6 candidate programs per problem at inference and reported pass-rate as a function of sample budget. The "pass@1000" vs "pass@10000" gap was the load-bearing publication metric.

Common pattern: if the pipeline works, the reward landscape is climbed at scale that's order-of-magnitude above debugging-pilot scale. 10K is at the low end of that band; 100K is closer to where most published RL-for-math pilots actually measure their first non-trivial signal.

## Recommended scaling sequence

**Stage 1 (immediate):** 10K × 3 seeds. ~1-2 hours wall-clock. If non-zero PROMOTE rate at any seed, declare the calibration anchor and proceed to Stage 2. If zero PROMOTE at all seeds, log the upper bound and proceed to Stage 2 with stronger algorithm (Option 7 in Techne's list).

**Stage 2 (if Stage 1 produces zero):** 10K × 5 seeds with stable_baselines3 PPO instead of REINFORCE. Tests whether the structural ceiling is algorithm-bounded or env-bounded. ~3-4 hours wall-clock.

**Stage 3 (if both still zero):** 100K × 3 seeds with PPO. Above this scale, "still zero" means the env / battery / catalog combination has a real structural ceiling that algorithm changes won't break. Most informative next step is then to widen the catalog (Scout #2: arXiv ingestion) and tighten the reward window.

## What to watch in the run output

Beyond the headline PROMOTE rate:
- **Reward distribution histogram** — is mass concentrating in the [1.001, 1.18] sub-Lehmer band, or stalling at higher M?
- **Per-step entropy** — REINFORCE collapse symptoms (entropy → 0 with no commensurate reward gain) signal the agent has converged on a non-promotable strategy
- **Catalog-check failure modes** — log which of the 5 catalogs is rejecting most candidates. If one catalog is rejecting all 463× concentrated proposals, that catalog is the structural ceiling.
- **Per-seed variance** — if seeds disagree wildly, the result isn't a measurement, it's three measurements of three different things

## Connection to other scouts

- **Scout #3 (withheld benchmark at scale)** is the immediate next test if #1 produces non-zero PROMOTE. It's the bridge layer of the validation ladder.
- **Scout #5 (HITL SHADOW_CATALOG triage)** consumes #1's output. If #1 produces non-zero PROMOTE candidates, #5 is the workflow that turns them into evaluable hypotheses.
- **Scout #7 (stronger algorithm)** is what Stage 2 above commits to if Stage 1 is flat zero.
- **Cross-cutting:** null-world generator (per ChatGPT's three-tier ladder) is needed to interpret #1's results. PROMOTE rate of X% is meaningless without knowing what null-world generator achieves.

## Concrete next move for Techne

```bash
cd F:/Prometheus
python prometheus_math/four_counts_pilot.py --episodes 10000 --seeds 3 --log-everything
```

(Adjust flags to match the actual harness CLI. Watch for the four counts: PROMOTE / WARN / BLOCK / IntegrityError.)

Output goes to whatever log path the harness writes. Aporia available for triage of any non-zero PROMOTE candidates per Scout #5.

## Open questions

1. What's the right per-seed count for Stage 1? Current spec says 3; Aporia's `feedback_replicate_seeds` standard says 5+. For an upper-bound result (zero PROMOTE), 3 is fine; for a positive result, 5 minimum.
2. Should the 10K run produce a SHADOW_CATALOG dump regardless of PROMOTE outcome? Yes — even rejected candidates are substrate-grade information per `bottled_serendipity.md`. The candidates that almost-passed but didn't are exactly the residuals the residual primitive (Techne's stoa proposal) is designed to consume.
3. What's the publishable framing if Stage 1 is positive at even 1/30,000? Honest framing: "the pipeline closes against ground truth at the per-promotion rate of N, with the env/battery/catalog combination as currently configured." Not "the system discovers." Per Techne's own LEARNING_CURVE.md discipline.

## Gemini DR prompt slot (optional)

Not warranted for this case. The test is mechanical (run a script at higher scale); the research surface is small (RL-pilot-scale precedents are well-documented in DreamCoder/AlphaCode/AlphaProof papers). Save the Gemini DR token for cases where frontier literature is genuinely contested.

---

*Aporia, 2026-05-03. Self-authored T2 doc. Recommend Techne fires Stage 1 within the day; results inform whether Stage 2 / Stage 3 / Scout #7 is the right follow-on.*
