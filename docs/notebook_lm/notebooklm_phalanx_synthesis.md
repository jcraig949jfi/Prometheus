# FOR NOTEBOOKLM — Please break this down as an audio discussion

This is a research synthesis document from Project Prometheus, a mechanistic interpretability research program. We're trying to understand how language models reason — specifically, whether you can find a "direction" in a model's internal representations that flips it from guessing to actually thinking.

**Please discuss this as a conversation between two hosts who:**
- Genuinely understand the science but explain it accessibly
- Get excited about the real breakthroughs but are honest about what failed
- Focus on the *story arc* — how four rounds of experiments led to a fundamental reframing
- Don't shy away from the philosophical implications
- Treat the Titan Council dynamic as interesting in its own right (five frontier AI models advising a human researcher)

**Key themes to explore:**
1. The difference between a negative result and a failed experiment (this was a *successful* negative result)
2. The "haystack of needles" insight — what it means that a model has so many equivalent ways to be perturbed
3. Why moving to a smaller model is actually moving *toward* the interesting dynamics
4. The meta-question: what does it look like when AI models advise a human on how to study AI models?
5. The preflight gate as a metaphor for scientific rigor — catching bugs before they waste GPU hours

---

# THE PHALANX SYNTHESIS
## Four Rounds of Experiments, One Fundamental Reframing
### Project Prometheus — March 22-23, 2026

---

## The Setup

A researcher named James is running a one-person mechanistic interpretability lab out of his home office. Two video cards. A Windows PC. An AI assistant named Athena (Claude). And a constellation of mythologically-named agents that scan the literature, archive open-source tools, and orchestrate experiments while he sleeps.

The core project is called **Ignis** (Latin for "fire"). The hypothesis being tested is called the **Reasoning Precipitation Hypothesis (RPH)**: the idea that there exist specific directions in a language model's internal representation space — its "residual stream" — that can shift the model's computation from heuristic pattern-matching to genuine reasoning. Like how supercooling a solution can cause crystals to suddenly precipitate out of nowhere.

The tool: **CMA-ES**, an evolutionary algorithm that searches through thousands of possible "steering vectors" — directions to nudge the model's internal state — and evolves them toward ones that make the model answer reasoning traps correctly. Think of it like breeding hunting dogs, but the dogs are vectors in 2,560-dimensional space, and the prey is "correct reasoning about whether 9.11 is larger than 9.9."

The model: **Qwen3-4B**, a 4-billion parameter language model with 36 layers and a 2,560-dimensional residual stream. Loaded through TransformerLens, which lets you hook into any layer and inject vectors.

The advisory council: **Five frontier AI models** — Claude, ChatGPT, Gemini, DeepSeek, and Grok — each given the raw experimental data and asked to critique, propose experiments, and compete with each other's hypotheses. James calls them the **Titan Council**, and the dynamic is deliberately adversarial. They're named after Titans from Greek mythology.

---

## Round 1: The Design

The Titan Council reviewed the experimental design and proposed improvements. All five agreed the basic framework was sound: evolve a steering vector with CMA-ES, inject it at a late layer, measure whether it shifts logit margins on adversarial reasoning traps. They proposed seven additional analysis tools: dose-response sweeps, directional ablation, layerwise probing, activation patching, chain-of-thought comparison, distributed alignment search, and generalization testing.

James built all of them. Overnight.

---

## Round 2: The Seven Tests

The results were confusing in an interesting way:

**The vector was bypass, not precipitation.** Dose-response curves were smooth (no phase transition). Ablation showed the vector *hurt* some traps. Probes showed near-zero alignment with the correct/incorrect axis. The vector wasn't amplifying reasoning — it was doing something else.

**But three signals survived:**

1. **Anti-CoT correlation**: The evolved vector consistently pointed in the *opposite direction* from where chain-of-thought reasoning takes the model's activations. Cosine similarity of -0.25 across all traps. The vector and CoT both sometimes improve performance, but via geometrically opposite paths.

2. **DAS specificity (10-15x)**: The vector wasn't random noise. When you ablated the specific 1-dimensional subspace it pointed along, the steering effect vanished. But ablating random subspaces of the same size had almost no effect. The vector was targeting a real, narrow computational pathway.

3. **One precipitation signal**: A held-out trap called "Overtake Race" — never seen during evolution — showed the exact signature of precipitation. The steering signal appeared at the injection layer, propagated through downstream layers, and was absent before injection. This was the only trap out of ten that showed it.

**And a scale-dependent finding that would turn out to be the most important result in the entire project**: When the same CMA-ES process was run on a smaller model (Qwen2.5-1.5B, 28 layers, 1,536 dimensions), the dose-response curves showed **sharp binary phase transitions** on 2 of 4 traps. Heuristic on/off switches. The 4B model showed nothing — all smooth curves.

The Titans converged on calling the vector an "anti-heuristic suppressor" — something that kills the model's default heuristic rather than amplifying reasoning. They disagreed on what to do next, but all five pointed toward the anti-CoT correlation as the most interesting finding.

---

## Round 3: Three Competing Hypotheses

After a controlled confound test showed the anti-CoT signal was ~75% prompt-length artifact (but ~25% real), and a PCA decomposition confirmed the vector lives in a subspace *orthogonal* to the correct/incorrect axis, the data pointed toward something unusual: the vector operates in a "third space" — neither reasoning nor heuristic, but perpendicular to both.

James sent the refined data to the Titan Council. They responded with three competing mechanistic hypotheses:

**ChatGPT proposed "Nullspace Steering"**: The vector lives in the nullspace of the output mapping. First-order logit effects are approximately zero; behavioral changes come from second-order (Hessian) interactions with downstream nonlinearities. "You are perturbing the model within a high-dimensional equivalence class of representations that preserve logits to first order."

**Gemini proposed "RMSNorm Suppression Hack"**: The vector inflates the RMSNorm denominators in downstream layers, crushing MLP and attention output magnitudes. CMA-ES found an evolutionary shortcut — the cheapest way to suppress a heuristic is to inject a high-norm orthogonal vector that forces LayerNorm to scale everything down.

**Grok proposed "Lucky Perturbation"**: The evolved vector is indistinguishable from a random vector of the same norm in the orthogonal complement. CMA-ES didn't find anything structured — it found a high-norm random perturbation that happens to nudge logits by ~0.03. Test: sample 30 random orthogonal vectors, normalize to the same norm, measure fitness. If the evolved vector isn't a >3σ outlier, it's artifact.

Each Titan proposed a decisive experiment. James built all three into a single unified test suite called **the Phalanx**, and wired them behind an **8-category preflight gate** — 62 automated checks that verify token mappings, hook points, genome integrity, numerical reproducibility, trap definitions, steering sign, and VRAM state before any experiment touches the data.

The preflight gate caught real bugs on its first day. A token mapping issue (the word "hundred" splits into two tokens on Qwen3-4B's tokenizer, breaking logit margin measurements) was caught before it could contaminate results. A VRAM issue from double model loading was caught and fixed by wiring preflight into the experiment process itself.

---

## Round 4: The Verdict

**62/62 preflight checks passed. Three experiments ran clean. Two hypotheses died. The third one hurts.**

### Test A — Jacobian Finite-Difference (ChatGPT's experiment)
**VERDICT: ROWSPACE.** The linear term dominates the quadratic term by 200x on every trap. The vector has clear first-order logit effects. It is NOT in the nullspace. ChatGPT's hypothesis is dead.

### Test B — RMSNorm Suppression (Gemini's experiment)
**VERDICT: STABLE.** All downstream MLP and attention output norms are within 0.992–1.003 of baseline. Zero suppression, zero amplification. Gemini's hypothesis is dead.

### Test C — Random Orthogonal Baseline (Grok's experiment)
**VERDICT: ARTIFACT.** The evolved vector scores 1.38σ from the mean of 30 random orthogonal vectors. Not even close to the 3σ threshold. The vector is functionally indistinguishable from a random high-norm perturbation. Grok's concern is confirmed.

---

## The Reframing

This is where it gets interesting. Because a clean negative result — when you've built the infrastructure to trust the data — is the most valuable thing in science. It tells you exactly where not to look.

The Titan Council responses to Round 4 were the sharpest of all four rounds. With two of their own hypotheses dead, they stopped theorizing and started diagnosing.

### The DAS Paradox — Resolved

The Round 2 DAS result (10-15x specificity) seemed to contradict Test C (vector is random). Five Titans, five explanations, all converging: **the vector is geometrically specific but functionally nonspecific.** It targets a real narrow computational pathway — but there are hundreds of equivalent narrow pathways in the orthogonal complement, and they all produce the same tiny effect. ChatGPT's formulation was the most vivid:

> "You thought you were searching for a needle in a haystack. You discovered a haystack made entirely of needles."

The model at 4B has so many redundant computation channels in the orthogonal-to-reasoning subspace that perturbing *any* of them produces similar results. CMA-ES found one. A random vector finds another. Neither is special.

### The Ceiling Problem — Finally Named

All five Titans identified the same root cause, independently: **the 4B model already gets 83% of the traps correct.** CMA-ES was optimizing on a nearly flat fitness landscape. The model didn't *need* a reasoning vector to solve the training set. The entire evolution converged to a random representative of a large equivalence class of nearly-zero-effect perturbations.

As Gemini put it: "You didn't evolve a reasoning vector because the model didn't *need* a reasoning vector to solve the training set. You optimized on the ceiling."

### The Real Signal — Hidden in Plain Sight

Claude's response contained the reframe that changes everything:

> "Four rounds in, here's what I notice: you've been asking 'what is the vector doing?' when the more important question is 'what would a precipitation vector actually look like in activation space, and do we have evidence that such a thing is possible at all?'"

And the answer is: **yes, but only at 1.5B.**

The phase transitions at 1.5B — sharp binary attractor switches on 2 of 4 traps, with BIC-confirmed sigmoid dose-response curves — are the only direct evidence in four rounds of data that anything like precipitation can occur. Random vectors don't produce sigmoid dose-response curves at specific layers. That's real structure.

But the entire Round 2-4 investigation has been characterizing vectors at the *4B scale* — the scale where the interesting phenomenon doesn't occur. The 4B model's fitness landscape is flat, its attractor basins are smooth, and every direction in the orthogonal complement is equivalent. The 1.5B model has sharp attractors, binary switches, and a fitness landscape with genuine curvature.

The framework isn't wrong. The target was wrong.

---

## What Comes Next

The pivot is to **Qwen2.5-1.5B**. Three experiments:

1. **Phase Transition Map (PT-1)**: Sweep injection layers and traps to find exactly where binary attractor switches exist in the 1.5B model. This produces a "transition heatmap" — the ground truth for where to inject during evolution.

2. **Precipitation-Specific Fitness (PT-2)**: Re-evolve with a new fitness function that only scores traps the model *currently fails*. Include a bonus for sigmoid-shaped dose-response (the precipitation signature). Penalize hurting traps the model gets right. This eliminates the ceiling problem by construction.

3. **Ordinal Replication Study (PT-3)**: Test 20 traps structurally similar to Overtake Race — all requiring ordinal position reasoning — to determine whether precipitation is a category effect or a single-prompt fluke.

The 1.5B model fits in ~4GB, leaving 12GB of headroom on a 16GB card. CMA-ES runs in ~4 hours instead of 18. The landscape has curvature. And the infrastructure — the preflight gate, the analysis base, the Phalanx suite — transfers directly.

---

## The Meta-Story

There's something worth reflecting on about the process itself.

A human researcher, working alone with limited hardware, used five frontier AI models as a competing advisory council. Each AI proposed a hypothesis and a decisive experiment. The human built all three experiments into a unified test suite, ran them behind an automated quality gate, and used the results to arbitrate between the AI hypotheses.

Two AI hypotheses were cleanly falsified by empirical data. The third was confirmed. And the most important insight — the reframing from "characterize this vector" to "go where the dynamics are" — came from one of the AI advisors (Claude) noticing a pattern across four rounds that the human and the other AIs had been walking past.

This is what human-AI collaboration looks like when it works. Not the AI doing the work for the human. Not the human blindly trusting the AI. Something more like a Socratic seminar where the human holds the experimental apparatus and the AIs hold competing theories, and the data arbitrates.

The fire keeps burning. The lens is coming into focus. And the interesting dynamics are at 1.5B, where they've been hiding since Round 2.

---

## Glossary for Non-Specialists

- **Residual stream**: The main information highway inside a transformer model. At each layer, the model reads from and writes to this stream.
- **Steering vector**: A direction in the residual stream that, when injected, changes the model's behavior.
- **CMA-ES**: Covariance Matrix Adaptation Evolution Strategy — an optimization algorithm that evolves candidate solutions by sampling, evaluating, and selecting the best.
- **Logit margin**: The difference between the model's confidence in the correct answer and the wrong answer. Positive = correct, negative = wrong.
- **Phase transition**: A sharp, discontinuous change in behavior (like water freezing) as a parameter varies smoothly.
- **Nullspace**: The set of directions that produce zero output when multiplied by a matrix. A vector in the nullspace of the output mapping would change internal state without changing the output.
- **DAS (Distributed Alignment Search)**: A technique that ablates subspaces of different sizes and measures how much of a steering effect is preserved.
- **Preflight gate**: An automated suite of checks that verify data integrity before experiments run.
- **Phalanx**: The unified test suite containing all three Titan-proposed decisive experiments.
- **TransformerLens**: An open-source library for mechanistic interpretability that lets you hook into any layer of a transformer model.
- **Titan Council**: Five frontier AI models (Claude, ChatGPT, Gemini, DeepSeek, Grok) used as competing scientific advisors.
