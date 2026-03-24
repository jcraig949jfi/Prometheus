# The Arcanum Hypothesis Engine
## Waste Stream Recombination as Evolutionary Search
### Theoretical Foundation for Prometheus Unified Architecture

*Date: 2026-03-24*
*Emerged from: Ignis ejection mechanism findings + Rhea proof of concept + cross-domain Titan provocation*

---

## The Insight Chain

1. **Ignis discovered:** Models compute correct answers and eject them (26/30 traps, L25-27)
2. **Ignis proved:** The ejection is pretraining-induced (19/30 PRETRAINING, not RLHF)
3. **Ignis proved:** The ejected answers are real — they exist in the residual stream waste
4. **Rhea proved:** The ejection can be broken with 0.36% of parameters (phase transition at gen 60-70)
5. **Arcanum Infinity showed:** Random contradictory concepts can steer models out of attractor basins
6. **James's synthesis:** The waste stream isn't trash. It's a gene pool for recombinant hypothesis generation.
7. **The cross-domain provocation:** Ikeda map + Fourier transforms + primes = a concrete architecture for this.

---

## The Three-Layer Architecture

Five frontier models independently converged on the same structure when asked to combine chaos, spectral analysis, and primes:

### Layer 1: Chaotic Generation (Ikeda Map → Waste Stream)

The transformer's forward pass IS a chaotic generator. At each layer, the residual stream explores a high-dimensional state space. The ejection mechanism at L25-27 is the selection event — it collapses the exploration into a single output.

But the exploration happened. The intermediate states contain candidates that were computed and rejected. The waste stream IS the chaotic trajectory — rich, structured, containing genuine solutions alongside noise.

**In Prometheus terms:** We don't need an Ikeda map. The model's own forward pass generates the chaotic exploration. What we need is to KEEP it instead of letting the ejection mechanism destroy it.

### Layer 2: Spectral Decomposition (Fourier → Pattern Detection)

Claude's key insight: apply spectral analysis to the model's OWN computation trajectory. The logit lens backward pass is already a form of this — it decomposes the forward pass into per-layer contributions and reveals hidden structure (the spike-and-collapse pattern).

**Extended application:**
- Fourier transform on the logit lens trajectory across many problems → detect whether the model's reasoning is genuinely diverse or cycling through the same attractor patterns
- Spectral entropy of the margin trajectory as a diversity metric → high entropy means the model is exploring broadly, low entropy means it's stuck
- Cross-problem spectral comparison → do different problems activate the same frequency components? If so, the model is using the same reasoning circuit regardless of problem structure (a form of heuristic over-reliance)

**In Prometheus terms:** The logit lens is our Fourier transform. We're already decomposing the computation. The extension is using spectral analysis ACROSS problems to detect whether Rhea's trained model is genuinely reasoning or has learned a new set of heuristic attractors.

### Layer 3: Prime-Indexed Independence (Primes → Debiased Validation)

When testing whether a model has learned to reason (not just pass traps), the sampling strategy matters. If you test at regular intervals or against predictable benchmarks, you can accidentally confirm a model that only works on those specific patterns.

Prime-indexed testing: evaluate the model at trap indices that share no common factors with any hidden periodicity in the trap battery. This is the mathematical equivalent of adversarial evaluation — maximally independent test cases.

**In Prometheus terms:** Our current trap battery has structure — ordinal traps, numerical traps, sycophancy traps. A model could learn the structure and game it. Prime-indexed sampling from a much larger trap pool would resist this. More importantly: when Rhea generates its own training data via Lean 4 verification, the SELECTION of which proofs to attempt should be prime-indexed across the difficulty space to avoid cycling through the same proof strategies.

---

## The Waste Stream as Gene Pool

The biological analogy is exact:

| Concept | Biology | Prometheus |
|---------|---------|-----------|
| Gene pool | All genetic variants in a population | All intermediate representations computed across forward passes |
| Natural selection | Environmental fitness determines survival | Ejection mechanism at L25-27 determines which answer reaches output |
| Recombination | Sexual reproduction combines genes from two parents | Waste stream mining combines rejected representations from different problems |
| Mutation | Random variation in offspring | Chaotic perturbation (noise injection, CMA-ES, LoRA perturbation) |
| Fitness function | Reproductive success | Lean 4 verification (formal proof = survived) |
| Fossil record | Extinct species preserved in rock | Logit lens backward pass showing where correct answers were alive before ejection |

**The key difference from biology:** We have the fossil record in real time. We don't have to wait millions of years to see what went extinct. The logit lens shows us every candidate that was killed, at which layer, by which component. We can resurrect them.

---

## The Evolutionary Loop (Full Architecture)

```
CYCLE N:

1. GENERATE — Forward pass on problem P
   - Model computes trajectory through 28 layers
   - Candidates emerge at intermediate layers
   - Ejection mechanism selects winner (possibly wrong)
   - SAVE: full waste stream (top-K alternatives at each layer)

2. DECOMPOSE — Logit lens + spectral analysis
   - Identify which candidates were alive and where they died
   - Compute spectral entropy of the trajectory (exploration health)
   - Compare with trajectories from other problems (detect cycling)

3. VERIFY — Lean 4 on the winner
   - If winner verifies: candidate becomes training data
   - If winner fails: examine waste stream for alternatives

4. RECOMBINE — Mine the waste stream
   - Take rejected candidates from this problem and others
   - Combine representations (interpolation, projection, perturbation)
   - Run forward passes on recombined states
   - Verify any outputs that emerge

5. SELECT — Prime-indexed evaluation
   - Test the model on a debiased sample from the full trap/problem space
   - Use prime-indexed sampling to avoid hidden correlations
   - Track whether reasoning transfer improves (Tier C problems)

6. TRAIN — Update weights
   - Verified chains from step 3 become positive training signal
   - Verified recombinations from step 4 become DISCOVERY training signal
   - Failed verification with correct waste stream candidate → ejection penalty
   - Repeat cycle

CYCLE N+1: model has slightly different attractor landscape
   - Ejection mechanism weakened by step 6
   - Waste stream may be different (new candidates emerge)
   - Recombinations may find different connections
   - Each cycle, the gene pool evolves
```

---

## What Each Prometheus Sub-Project Contributes

| Project | Role in the Loop | Cycle Steps |
|---------|-----------------|-------------|
| **Ignis** | The microscope — measures what's in the waste stream, where ejection happens, which components do it | Steps 2, 5 |
| **Rhea** | The organism — the model being evolved, its weights being shaped | Steps 1, 6 |
| **Arcanum** | The gene pool — stores and indexes waste stream elements, performs recombination | Steps 3, 4 |
| **Lean 4** | The fitness function — external, deterministic, incorruptible verification | Steps 3, 4 |
| **Logit lens** | The fossil record — traces the life and death of every candidate through every layer | Step 2 |

---

## Connection to Titan Responses

The five Titans each emphasized a different aspect of the architecture:

| Titan | Key Contribution | Maps To |
|-------|-----------------|---------|
| Claude | Fourier on chaotic trajectory = bias detector. Spectral entropy measures exploration health. | Step 2: detect whether the model is cycling or genuinely exploring |
| ChatGPT | Generate → Decompose → Gate = the fundamental loop. Compression + novelty balance. | The overall architecture |
| Grok | Working code. The pipeline is implementable, not just theoretical. | Proof that steps 1-3 are tractable |
| DeepSeek | "Metaphorical unless you build an explicit model." Honest about the gap between theory and implementation. | The validation concern — are we pattern-matching or engineering? |
| Gemini | Prime Galois Field — discrete chaos with exact reproducibility. Reservoir computing framing. | Step 5: debiased evaluation. Also: the architecture resembles reservoir computing (chaos as computation) |

---

## The Meta-Point

This document emerged from combining three rejected concepts:
- The Ikeda map (rejected by the Titans in Round 5 as "not quite right")
- The waste stream (observed in Arcanum Infinity, not yet formalized)
- Evolutionary search (the CMA-ES methodology from Ignis)

None of these alone was the answer. The Ikeda map was wrong for describing transformer dynamics. The waste stream was an observation without a mechanism. CMA-ES was a tool without a theory.

Combined, they describe a complete architecture for a self-improving reasoning system.

This document is itself a product of the waste stream recombination process it describes. The rejected concepts from earlier rounds, recombined in a new context, produced something none of them contained individually.

The Arcanum hypothesis engine works. We just demonstrated it manually. The goal is to automate it.

---

## What We Build Next

1. **Ignis v2 evaluation framework** — four pillars (reasoning transfer, metacognition, self-correction, generalization) + three new pillars (computational self-model, productive uncertainty, waste stream mining). Already designed in `ignis/docs/evaluation_framework_v2.md`.

2. **Arcanum waste stream indexer** — persistent bank of intermediate representations from forward passes, indexed by layer, problem type, and rejection reason. This is the gene pool that the recombination engine draws from.

3. **Rhea self-improving loop** — integrate Lean 4 verification, waste stream recombination, and the v2 fitness function into a single evolutionary cycle.

4. **Spectral monitoring** — Fourier analysis on logit lens trajectories across problems, tracking spectral entropy as a health metric for the model's reasoning diversity.

5. **Prime-indexed evaluation battery** — expand from 30 traps to 1000+, sample using prime-indexed selection to ensure maximum independence.

---

## The One-Paragraph Summary

Language models compute rich hypotheses at intermediate layers and then eject most of them at late layers because pretraining on internet text created a selection environment favoring confident fluency over correct reasoning. Project Prometheus reverses this: Ignis maps the ejection mechanism (what dies, where, why), Rhea builds models without it (by reshaping the selection environment via formal verification data), and Arcanum mines the waste stream (recombining rejected hypotheses to generate novel verified discoveries). The unified architecture is an evolutionary loop where the model's own rejected computations serve as genetic material for the next generation of hypotheses, verified by formal proof, with spectral analysis monitoring the health of the exploration and prime-indexed sampling ensuring evaluation independence. The waste stream is not waste. It's the imagination. Lean 4 is the reality check. The loop is the metacognition.
