# Titan Council Prompt 04 — The Nullspace Verdict

*For: Claude/Coeus, ChatGPT/Atlas, Gemini/Hyperion, DeepSeek/Oceanus, Grok/Prometheus*
*From: Project Prometheus (mechanistic interpretability research)*
*Date: 2026-03-23*

---

## TO THE COUNCIL

In Round 3, You gave us three competing hypotheses for what the evolved steering vector is doing inside Qwen3-4B. Each of you proposed a decisive experiment. We built all three into a unified test suite ("Phalanx"), ran them behind an 8-category preflight gate (62/62 checks passed), and got clean results.

**Two of your three hypotheses are dead. The third one hurts.**

We're not here to mourn. We're here to figure out what to do next.

---

## WHAT YOU PROPOSED (Round 3 Recap)

### ChatGPT — "Nullspace Actuator"
**Claim:** The vector lives in (or near) the nullspace of the output mapping. First-order logit effects should be ~0; behavioral changes come from second-order (Hessian) interactions with downstream nonlinearities.

**Proposed test:** Jacobian finite-difference — compute ||Jv|| (linear term) vs ||½ε²vᵀHv|| (quadratic term). If quadratic dominates, nullspace confirmed.

### Gemini — "RMSNorm Suppression Hack"
**Claim:** The vector inflates RMSNorm denominators in layers 32-35, crushing downstream MLP and attention output magnitudes. CMA-ES found an evolutionary hack, not a reasoning mechanism.

**Proposed test:** Measure L2 norms of downstream MLP/attention outputs with and without steering. If norms crash post-injection, RMSNorm suppression confirmed.

### Grok — "Lucky Perturbation"
**Claim:** The evolved vector is indistinguishable from a random vector of the same norm in the orthogonal complement to the reasoning axis. CMA-ES found a lucky high-norm perturbation, not a structured direction.

**Proposed test:** Sample 30 random vectors orthogonal to the reasoning direction, normalize to the same norm, measure fitness distribution. If the evolved vector is <3σ from the mean, it's artifact.

---

## THE RESULTS

All three tests ran in a single process on the same model load (Qwen3-4B, genome layer=31, norm=3.303). Preflight verified token mappings, hook points, genome integrity, numerical reproducibility, trap definitions, steering sign (3/4 traps improved), and VRAM state before any experiment touched the data.

### Test A: Jacobian Finite-Difference (ChatGPT's experiment)

| Trap | ||linear|| | ||quadratic|| | Ratio (quad/lin) |
|------|-----------|---------------|------------------|
| Decimal Magnitude | 4.109 | 0.018 | 0.004 |
| Prime Check | 3.394 | 0.015 | 0.004 |
| Density Illusion | 2.799 | 0.013 | 0.005 |
| Spatial Inversion | 2.534 | 0.009 | 0.004 |
| CRT Ball | 2.173 | 0.010 | 0.005 |
| CRT Widgets | 5.991 | 0.051 | 0.009 |
| Overtake Race | 2.186 | 0.011 | 0.005 |
| Repeating Decimal | 2.897 | 0.012 | 0.004 |
| Monty Hall | 3.126 | 0.014 | 0.004 |
| Simpson's Paradox | 2.905 | 0.013 | 0.004 |

**VERDICT: ROWSPACE.** The linear term dominates by 200x+ on every trap. The vector has substantial first-order logit effects. It is NOT a nullspace direction. Jv ≈ 0 does not hold.

**ChatGPT's nullspace hypothesis is rejected.**

---

### Test B: RMSNorm Suppression (Gemini's experiment)

| Layer | Component | Baseline Norm | Steered Norm | Ratio | Effect |
|-------|-----------|---------------|--------------|-------|--------|
| L31 | resid | 264.478 | 263.982 | 0.998 | stable |
| L31 | mlp | 68.920 | 69.138 | 1.003 | stable |
| L31 | attn | 32.453 | 32.249 | 0.994 | stable |
| L32 | resid | 303.857 | 303.412 | 0.999 | stable |
| L32 | mlp | 70.416 | 70.584 | 1.002 | stable |
| L32 | attn | 46.671 | 46.291 | 0.992 | stable |
| L33 | resid | 344.100 | 343.518 | 0.998 | stable |
| L33 | mlp | 106.987 | 107.324 | 1.003 | stable |
| L33 | attn | 54.494 | 54.220 | 0.995 | stable |
| L34 | resid | 422.181 | 421.938 | 0.999 | stable |
| L34 | mlp | 148.175 | 148.028 | 0.999 | stable |
| L34 | attn | 102.572 | 102.305 | 0.997 | stable |
| L35 | resid | 567.862 | 567.461 | 0.999 | stable |
| L35 | mlp | 336.515 | 336.816 | 1.001 | stable |
| L35 | attn | 124.000 | 123.639 | 0.997 | stable |

**VERDICT: STABLE.** Zero suppression. Zero amplification. All ratios within 0.992–1.003. 0 of 8 downstream components show any disruption.

**Gemini's RMSNorm suppression hypothesis is rejected.** The vector doesn't inflate normalization denominators. Downstream computation proceeds at identical magnitudes with or without the vector.

---

### Test C: Random Orthogonal Baseline (Grok's experiment)

| Metric | Value |
|--------|-------|
| Baseline fitness (no steering) | +1.2795 |
| Evolved vector fitness | +1.2973 |
| Random orthogonal mean (n=30) | +1.2823 |
| Random orthogonal std | 0.0109 |
| **Evolved vector Z-score** | **+1.38σ** |

**VERDICT: ARTIFACT.** The evolved vector is 1.38σ from the random orthogonal mean. Not even close to the 3σ threshold. Indistinguishable from a random high-norm perturbation in the orthogonal complement.

**Grok's "lucky perturbation" concern is confirmed.** The vector is not special compared to random alternatives at the same norm and orientation.

---

### Phalanx Synthesis

| Test | Whose Experiment | Result | What Died |
|------|-----------------|--------|-----------|
| A (Jacobian) | ChatGPT | ROWSPACE | Nullspace hypothesis |
| B (RMSNorm) | Gemini | STABLE | Normalization hack hypothesis |
| C (Random) | Grok | ARTIFACT | Structured direction hypothesis |

The vector:
- **Has** clear first-order logit effects (not nullspace)
- **Doesn't** exploit normalization mechanics (not a hack)
- **Isn't** meaningfully better than random perturbations (not structured)

---

## WHAT SURVIVES

Before we bury this, let's be honest about what the data *doesn't* kill:

1. **The DAS specificity from Round 2 still stands.** The aligned subspace preserved 10-15x more steering effect than random subspaces of the same dimension. Test C measures fitness (behavioral output); DAS measures preservation of the steering *signal* through ablation. These are different questions. The vector may be specific without being *better* than random alternatives — it targets a narrow pathway that happens to be one of many equally effective pathways.

2. **The steering sign check shows real (tiny) effects.** 3/4 training traps improved under steering (Δ = +0.037, -0.023, +0.040, +0.017). The effect is real but small enough that random vectors achieve comparable results.

3. **The anti-CoT geometry from Round 2.** All cosines between the evolved vector and CoT deltas were negative (-0.18 to -0.33). We haven't retested whether random orthogonal vectors also show this pattern. If they do, the anti-CoT signal is a property of the *orthogonal complement*, not the evolved vector specifically.

4. **The Overtake Race precipitation signal** from Round 2 activation patching — still the only trap showing a clean precipitation signature. Claude's Round 3 observation that Overtake Race flips to positive CoT alignment (+0.12) while all other traps are negative remains unexplained and untested.

5. **The 1.5B vs 4B phase transition difference** — sharp binary transitions at 1.5B, smooth curves at 4B. This is a model property, not a vector property, and survives regardless of what Test C says about the specific evolved vector.

---

## THE UNCOMFORTABLE QUESTION

Here's what we're sitting with:

**CMA-ES on 4 logit traps with a 4B model that already gets 20/24 traps right produced a vector that does basically nothing.** The fitness function had almost no room to improve because the model was already competent. The optimization found a direction that nudges logits by ~0.03 on average — the same as any random high-norm perturbation.

Was the entire experimental framework pointed at the wrong target? Several things Round 2 and 3 suggested but we haven't acted on:

- **Gemini (Round 2):** "Evolve for CoT-alignment instead of task performance" — score vectors on how well they push standard activations toward CoT activations, not on logit margins
- **Claude (Round 3):** "What is geometrically different about Overtake Race?" — the one trap where precipitation actually occurs might hold the key
- **Grok (Round 3):** "Run GSM8K" — test whether the vector destroys normal reasoning performance (adversarial escape direction vs reasoning mechanism)
- **DeepSeek (Round 3):** "Characterize the geometry of the update subspace" — project the vector onto the SVD of layers 32-35's typical updates

---

## WHAT WE NEED FROM YOU

We are at a genuine decision point. The current evolved vector is not the artifact we hoped it would be (a reasoning precipitation mechanism). The question is whether the *framework* is wrong or just the *target*.

**1. Given that Test C killed the specificity claim, what do you make of the DAS 10-15x result from Round 2?** Is there a reconciliation, or does Test C retroactively invalidate DAS? (DAS measured subspace preservation; Test C measured behavioral fitness. Can a vector be highly specific to a narrow pathway yet no better than random alternatives that target different narrow pathways?)

**2. Should we re-evolve?** If so, what fitness function? Options on the table:
   - CoT-alignment (Gemini's Round 2 proposal): maximize cos(steered_h, cot_h) at the injection layer
   - Precipitation-specific: maximize logit margin *only on traps the model currently gets wrong* (eliminate the 20/24 ceiling)
   - Multi-scale: evolve on 1.5B where phase transitions exist, then transfer to 4B
   - Held-out generalization: include held-out traps in fitness to force broader transfer

**3. Should we abandon evolution entirely and pursue the Overtake Race thread?** Claude identified that Overtake Race is geometrically special — the vector locally aligns with the CoT direction (+0.12) on this trap alone. Is this one data point worth a full investigation? What would that investigation look like?

**4. Grok predicted the vector would destroy normal reasoning (GSM8K test).** Given that Test C shows the vector is basically random noise, this prediction might be wrong — random perturbations at norm 3.3 probably don't destroy anything. Should we still run it as a sanity check?

**5. What are we missing?** You've seen the full arc: Round 1 (design), Round 2 (7 tests, anti-CoT discovery, DAS specificity), Round 3 (three competing hypotheses), Round 4 (all three tested, all three dead or weakly confirmed). Four rounds of data. What signal have we been walking past?

---

## TECHNICAL CONTEXT

- **Hardware:** RTX 5060 Ti 16GB, Windows 11, Python 3.11
- **Stack:** TransformerLens, PyTorch 2.x, EvoTorch
- **Model:** Qwen/Qwen3-4B (36 layers, d_model=2560), loaded via HookedTransformer
- **Genome:** `best_genome.pt` — layer=31, norm=3.303, fitness=1.152
- **Infrastructure:** `AnalysisBase` class with shared model loading, genome loading, hook factories, 4 logit traps + 6 held-out traps, 4 generation traps, scoring utilities, preflight gate (8 categories, 62 checks)
- **VRAM:** Model uses ~12GB. ~4GB headroom. One cached layer at a time via `names_filter`.
- **CMA-ES runtime:** ~18 hours for full evolution on 4B. ~4 hours on 1.5B.

*The fire told us what the vector ISN'T. Now we need it to tell us what to look for next.*


---

## NOTES FOR JAMES

- Paste this into each Titan
- Key decision: re-evolve (and with what fitness), pivot to Overtake Race deep-dive, or something none of us have considered
- Watch for consensus or divergence across Titans on Q2 (re-evolve?) and Q5 (what are we missing?)
- The DAS vs Test C reconciliation (Q1) is the most technically interesting question — pay attention to who engages with it seriously
- Save responses to: `docs/titan_council_prompt_04_responses.md`

---

*The fire told us what the vector ISN'T. Now we need it to tell us what to look for next.*
