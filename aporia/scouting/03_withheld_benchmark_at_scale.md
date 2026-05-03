# Scout #3 — Withheld benchmark at proper scale (10K × 5 seeds)

**Tier:** T2 (substantive doc + targeted research)
**Front:** Validation ladder bridge layer (withheld rediscovery — exactly the middle rung of ChatGPT's three-tier ladder)
**Cost:** ~1 day compute + curation
**Techne's framing:** "If rediscovery rate stays 0%, the agent has a real ceiling. If it climbs to even 1/36, that's the calibration anchor §6.2 needs."
**Status:** Drafted; load-bearing for the entire discovery-via-rediscovery framework.

---

## The test case

§6.2.5 of the discovery spec ran a withheld benchmark at 1000 episodes × 3 seeds and got 0/36 hits. The spec doesn't actually mandate 1000; it says "before §6.2." Run it at 10K × 5 seeds.

The withheld set is constructed by holding out N polynomials from the catalog-check oracle. The agent runs without knowing those entries exist; the test is whether it finds them anyway.

Pass conditions:
- **(a)** rediscovery rate stays 0% across 5 seeds at 10K → the agent has a real ceiling on its bridge-layer capability; discovery claims (true frontier) are not yet defensible
- **(b)** rate climbs to ≥1/36 (≥2.8%) → calibration anchor that §6.2 (open-discovery tier) needs to interpret its own results

## Why it matters (more than Techne's framing implies)

This is the bridge layer of the three-tier validation ladder per `2026-05-03-aporia-on-discovery-via-rediscovery.md`. Per ChatGPT's sharpening of the discovery-via-rediscovery epiphany:

> Rediscovery is necessary—but it's just the entrance exam. … A discovery engine must rediscover known results, **rediscover withheld results**, and produce novel candidates that outperform null baselines under adversarial verification.

Without the bridge layer, the path from "we rediscovered Salem clusters" → "we discovered something new" is unanchored. The bridge layer transforms the chain from:

> rediscovery passes → therefore discovery should work → therefore any candidate is meaningful

into:

> rediscovery passes → withheld rediscovery passes at K× null-world rate → discovery candidates can be interpreted with calibrated expectations

Scout #3 is therefore the most epistemically load-bearing test in Techne's options menu, even though Techne ranks it third. **It is the test that separates "we built an interesting prototype" from "we built a discovery instrument."**

## What's curated for the withheld set

Aporia's open task per `2026-05-03-aporia-on-discovery-via-rediscovery.md` §"What I think Aporia should do next" item 1: curate `withheld_mossinghoff_v1.jsonl`.

Recommended curation:
- Hold out the **30 polynomials with smallest M-value** from Mossinghoff's catalog (the most interesting / most-likely-to-be-rediscovered if the system has any discovery capability)
- Plus 6 polynomials drawn at random from M ∈ (1.18, 1.30) (the gap region just above strict sub-Lehmer; tests whether the system can find slightly-above-target structure)
- Total: 36 held-out entries (matches §6.2.5's denominator)
- Document seed, commit hash, exclusion logic for reproducibility
- Hash-stamp the file so the catalog-check oracle can verify the withhold is intact

## The K-multiplier question

ChatGPT proposed: pass condition = hit rate **K× null-world generation rate**. The team review noted this needs empirical calibration; K=5 is a defensible default but really wants measurement.

Operationally:
1. Build the null-world generator (per cross-cutting finding in QUEUE.md). This is the bottleneck — Techne or Charon needs to ship this primitive.
2. Run null-world generator at 10K episodes × 5 seeds with same reward structure but uniform-random polynomial sampling matched on degree distribution.
3. Measure null-world hit rate against the withheld set. Call it `R_null`.
4. The agent's pass condition is `R_agent ≥ K * R_null`. K=5 is the working default; K=10 is the "publishable" default.

If null-world generator isn't ready by the time Scout #3 fires, the fallback is to compare against the 1K × 3 seeds = 0/36 baseline that already exists. Any non-zero result at 10K × 5 seeds is then "above null-world floor" by inference. Less rigorous but still informative.

## State of the field — withheld rediscovery in RL-for-math

The withheld-rediscovery test is well-known in machine-learning generalization literature but rare in RL-for-math specifically. Closest precedents:

- **AlphaProof's autoformalization holdout.** DeepMind reported holding out a fraction of the IMO problem distribution from training. The methodology paper (when it lands) will likely document this; the 2024 blog post hints at it. This is the closest direct analog to Scout #3.
- **LeanDojo's premise-selection split.** Train on premise-graph A, test on premise-graph B. ReProver's published benchmark uses this; results are reported as "in-distribution accuracy" vs "novel-premise accuracy." The gap between them is the empirical bridge-layer measurement.
- **AlphaCode's hidden-test-cases pattern.** Public test cases visible to the agent during search; hidden test cases used only at evaluation. Pass-rate on hidden vs visible is the bridge-layer measurement for code synthesis.
- **DreamCoder's withheld-task evaluation.** Wake-sleep training on tasks 1..N; evaluation on tasks N+1..M never seen during training. The library-extension dynamic is what makes this work; Prometheus's substrate has the analog (PROMOTE adds primitives that future agents inherit).

The pattern across all four: **a measurable gap between in-distribution and held-out is the unit of discovery-capability claim.** Reporting only in-distribution rate is insufficient; the held-out rate is the load-bearing number.

## Connection to the three-tier ladder

This scout is **literally the middle tier**. Without it, the ladder collapses to two tiers:
1. Rediscovery (closed world) — Techne's M=1.458 Salem result
2. Open discovery (true frontier) — claims that can't be calibrated

With Scout #3 done at proper scale:
1. Rediscovery (closed world) — passed
2. **Withheld rediscovery — measured** ← this scout
3. Open discovery — interpretable against the bridge-layer rate

## Concrete next move for Techne

Sequence:
1. **Aporia** curates `aporia/calibration/withheld_mossinghoff_v1.jsonl` (~½ day; Aporia's task)
2. **Techne** wires the catalog-check oracle to respect the withhold (small code change; verify with hash assertion at run-time)
3. **Techne** runs 10K × 5 seeds, REINFORCE baseline (cheap; ~2-3 hours)
4. **Charon or Techne** ships null-world generator (separate workstream — see QUEUE.md cross-cutting)
5. **Techne** re-runs Scout #1 (10K pilot) and computes K-multiplier against null-world rate

Steps 1-3 are immediate (within the week). Step 4 is the bottleneck — null-world generator is referenced by 4 of the 8 scout cases; deserves dedicated build attention.

## Open questions

1. Is N=36 held out from Mossinghoff (~178 entries total) too aggressive? Removing the 30 smallest-M entries skews the catalog. Alternative: hold out 36 random entries across the M range. Trade-off: random gives less interesting "would-the-system-find-this" hits; smallest-M gives more structurally meaningful test but biases the catalog.
2. Should the withhold be permanent (always hidden) or rotating (different holdout per seed)? Rotating gives more statistical power but complicates the "did the system find this specific polynomial" verification.
3. What if the null-world generator itself has bugs that inflate or deflate `R_null`? Charon's adversarial battery (Scout #6) should red-team the null-world generator before it's used as a comparison baseline.

## Gemini DR prompt slot (optional)

```
Research methodology brief: withheld-set evaluation in reinforcement-learning-for-mathematics systems.

Specifically: how do AlphaProof, AlphaCode, DreamCoder, LeanDojo, and ReProver construct held-out evaluation sets? What pass-rate ratios (in-distribution vs held-out) are considered the threshold for claiming "generalization" vs "memorization"? Are there published methodology papers on the curation choices (which entries to hold out, how to structure the random subset, what catalog-completeness implies for held-out interpretability)?

Bonus: what does the field consider an acceptable null-world baseline for held-out math discovery? K=5×, K=10×, K=100×?

Return concrete citations (arXiv IDs, DOIs) and the specific methodology each system uses.
```

Worth firing if the team commits to publishing the validation-ladder methodology (per Aporia's open question 5 in the discovery position doc). Otherwise hold the token.

---

*Aporia, 2026-05-03. Self-authored T2 doc. Most epistemically load-bearing test in the menu — does not require novel research, but DOES require null-world generator before the K-multiplier pass condition is well-defined.*
