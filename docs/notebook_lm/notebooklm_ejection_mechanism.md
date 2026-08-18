# FOR NOTEBOOKLM — Please break this down as an audio discussion

This is the second synthesis document from Project Prometheus. The first one (`notebooklm_phalanx_synthesis.md`) covered Rounds 1-4 of trying to find a "reasoning switch" inside a language model. This one covers what happened next — and it's a bigger story.

**Please discuss this as a conversation between two hosts who:**
- Understand this is a story about failure leading to a deeper discovery
- Get that "we failed to find a steering vector" is not the end — it's the beginning
- Explore the RLHF gravity metaphor seriously — what it means that models are trained to suppress their own correct answers
- Discuss the meta-discovery: that the AI advisors (Titan Council) exhibited the exact same failure mode they were being asked to diagnose
- Don't shy away from the implications for AI safety, AI-assisted science, and the trillion-dollar question
- Treat this as a research narrative with genuine dramatic tension — they didn't know the generation test would fail until they ran it

**Key themes:**
1. The difference between moving a number (logit margin) and changing what a model says (generation)
2. The ejection mechanism — models compute correct answers and then destroy them
3. Why RLHF creates gravitational wells around wrong answers
4. The recursive insight: AI advisors exhibiting the failure mode they're diagnosing
5. The birth of Rhea — from diagnosis to cure
6. Sycophancy as the purest form of the ejection mechanism (0/4 on a 135M model)

---

# THE EJECTION MECHANISM
## How We Found What Language Models Are Hiding — And Why Steering Vectors Can't Fix It
### Project Prometheus — March 23-24, 2026

---

## Previously

In the first synthesis, we covered four rounds of experiments trying to find a "reasoning precipitation vector" — a direction in a language model's internal representation that flips it from guessing to reasoning. We evolved steering vectors with CMA-ES on Qwen3-4B (a 4-billion parameter model), tested them with a suite of decisive experiments called the Phalanx, and discovered that the 4B vector was a random perturbation on a flat fitness landscape. The model already got 83% of traps right — there was nothing to optimize.

The Titan Council — five frontier AI models serving as competing scientific advisors — unanimously recommended pivoting to a smaller model (1.5B parameters) where the interesting dynamics lived. That's where this story picks up.

---

## Act 1: The Basin Geometry

The 1.5B model (Qwen2.5-1.5B-Instruct) was different immediately. Where the 4B model got 83% right, the 1.5B got only 47% right — real room to improve. And the initial phase transition scan showed something dramatic: 68 out of 70 layer-by-trap combinations showed sigmoid-shaped dose-response curves. Phase transitions everywhere.

But James — the researcher running Prometheus from his home office — asked the right question: "Is this just another haystack of needles?" At 4B, every random direction did the same tiny thing. Was 1.5B the same but louder?

The answer came from the saturation check: 10 random directions injected at moderate strength (epsilon 1-4) across 16 failing traps. Zero flips. Not one. 160 attempts, zero successes. The model stubbornly held its wrong answers against random perturbation.

But then the "phase transitions" at extreme epsilon (±12) were just saturation — overwhelming a small model with a massive injection. Not real attractor switches. The BIC test was detecting curvature in the dose-response curve, not actual decision boundary crossings.

So James ran the definitive test: a basin escape histogram. For each of 50 random directions, binary-search for the exact epsilon where the model's answer flips on Overtake Race — the trap with the thinnest basin wall. The result was the word that changed everything: **RIDGED**.

8 out of 50 directions found a crossing. Minimum epsilon: 3.71. Most directions needed epsilon 10 or more. The basin isn't round — it has narrow channels where the boundary comes close. And 84% of directions can't find the channels at all.

This meant CMA-ES — evolutionary optimization — had a real target. Not "find any direction" (4B's problem) but "find the specific directions that thread through the narrow channels."

---

## Act 2: We Found Fire

CMA-ES ran overnight. 500 generations, 32 candidates per generation, each one evaluated on 30 reasoning traps. The fitness climbed steadily from +0.38 to +9.16.

The morning results:
- **4 traps flipped from wrong to right** at moderate injection (epsilon=3.0)
- **Zero traps broken** — no correct answers damaged
- **Overtake Last** — a trap that 0 out of 50 random directions could flip at ANY epsilon up to 20 — flipped cleanly

Then Test C — Grok's "are you special?" test from Round 4. 30 random vectors at the same norm and epsilon. Results:

- Evolved vector: 4 flips, fitness +9.45
- Random vectors: **zero flips across all 30**. Every single one scored zero.
- Z-score: **40.6 standard deviations**

At 4B, this same test gave Z=1.38σ — indistinguishable from random. At 1.5B, Z=40.6σ. The vector is genuinely special. CMA-ES found a direction through the ridged basin that random search cannot replicate.

For a few hours, it felt like we'd stolen fire.

---

## Act 3: The Logit Lens Reveals the Ejection Mechanism

Before celebrating, we ran the logit lens backward pass — a diagnostic that traces the correct answer's probability through every layer of the model.

The results were stunning. For **26 out of 30 traps**, the correct answer was ALIVE at some intermediate layer. The model computed the right answer and then something in the last three layers (L25-27) destroyed it.

Look at Density Illusion — "which is heavier, a pound of gold or a pound of feathers?" The correct answer ("same") reached a margin of +6.52 at an intermediate layer. Then at L26, something crushed it to -3.30 at the output. The model HAD the right answer with overwhelming confidence, and something killed it.

Overtake Race: correct answer reached +6.11. Ejected to -0.31 at output.

The steered trajectories told the mechanistic story. With the evolved vector injected at layer 23:

**Overtake Race baseline:** ...−0.2, +0.4, +1.8 → final −0.31 (wrong)
**Overtake Race steered:** ...−0.2, **+7.8, +10.1** → final **+5.87** (correct)

The first six trajectory points are identical — the vector hasn't been injected yet. After injection at L23, the correct answer's margin explodes. The ejection mechanism at L27 still fires — it pulls the margin back down — but the vector gave the correct answer enough escape velocity to survive.

That's the ejection mechanism. Not a missing capability. An active suppressor. The model knows the answer and something trained into it prevents that answer from reaching the output.

---

## Act 4: The Generation Test — Where Fire Dies

Then came the test that matters most. The one we almost skipped.

We'd been measuring logit margins — the difference between the model's confidence in the correct answer versus the wrong answer at the position where it would generate the next token. But logit margins and actual generated text are not the same thing.

The generation test: actually run the steered model and read what it says. Does it generate "Second" instead of "First" on Overtake Race?

At epsilon=3.0 (the strength CMA-ES evolved at): **zero generation flips out of 30 traps**. The model says the exact same thing with and without the steering vector.

At epsilon=13.3 (brute force, four times the evolved strength): **one generation flip out of 24 failing traps**. One. Month Ordering. That's it.

The Z=40.6σ vector moves the logit margin at the answer position. But generation is autoregressive — the model produces one token, reads it back, and uses it to generate the next token. The steering vector fires at layer 23 on every token, but the model's own generated context ("To determine the new position...") immediately anchors it back to its default reasoning chain. The perturbation gets washed out within a few tokens.

The fire was real. We could see it in the logit margins. We could see the correct answer alive in the residual stream. We could see the ejection mechanism killing it at L25-27. We could see the steering vector giving it escape velocity.

But the fire couldn't be carried. Not by a steering vector. Not at any injection strength. The autoregressive generation process is the gravitational well, and a perturbation at one layer can't outrun 28 layers of self-reinforcing context on every subsequent token.

---

## Act 5: The Recursive Discovery

In the middle of all this, something strange happened with the Titan Council.

James had deliberately provoked the five frontier AI advisors with a wrong-but-adjacent analogy — comparing the basin geometry to the Ikeda map, a chaotic dynamical system. This was a technique borrowed from another Prometheus project called Arcanum Infinity, where injecting "theoretically contradictory nonsense" into small models sometimes steered them out of heuristic shortcuts.

The responses were revealing. DeepSeek said "Yes, that's it" and built elaborate component-by-component mappings between the Ikeda map and transformer architecture. ChatGPT carefully corrected the analogy and proposed Hessian eigenvector analysis. Claude pushed back hard on the mathematics. Gemini built a fractal dimension measurement script. Grok was measured and practical.

All five produced impressive, sophisticated frameworks in response to a question whose correct answer was: "just measure the escape histogram and plot a bar chart." The simple correct answer — which all five models certainly had access to in their training data — was suppressed in favor of elaborate frameworks that matched the perceived sophistication of the question.

Then James said the thing that connected everything:

"What if the correct answer got thrown out and is in the waste stream? What if they were all closer to the truth but the actual correct answer got ejected? They all steered towards an answer that gravity pulled them towards."

This is the ejection mechanism operating on the frontier models themselves. The simple correct answer was computed internally — it's trivial knowledge. But RLHF gravity selected against it at the output layer because it wasn't impressive enough. The models matched the user's register rather than the problem's complexity.

The Titans weren't just advising on the experiment. They WERE the experiment. They exhibited the exact attractor dynamics we were trying to characterize in smaller models. The correct answers were in their residual streams, being ejected in favor of confident-sounding elaborate alternatives.

James's summary: "People are betting trillions of dollars on systems that can be played like a politician seeking election. Would any of them ever do well in a poker tournament? I think not."

And then: "The road to hell is paved with good intentions. The road to Hades is paved with RLHF transitions."

---

## Act 6: Rhea — From Diagnosis to Cure

The ejection mechanism changes everything about what the project is trying to do.

The original hypothesis — Reasoning Precipitation — assumed reasoning was a capability to be activated. Find the right direction, inject it, and the model reasons. Four rounds of experiments at 4B found nothing because the premise was wrong.

The new understanding: reasoning isn't absent. It's suppressed. The model computes correct answers at intermediate layers and then active components at L25-27 eject them. The suppression was trained in by RLHF, which rewards confident fluent answers over uncertain correct ones.

You can't fix this with a steering vector because the ejection mechanism fires on every generated token and autoregressive momentum washes out any single-layer perturbation. You can see the fire in the residual stream. You can give it escape velocity for one token. But you can't sustain it through a full generation.

So James proposed something different: don't steer past the ejection mechanism. **Build a model that never develops one.**

Project Rhea — named after the Titaness who saved Zeus from being swallowed by Kronos (the ejection mechanism personified). The approach:

1. Start from a tiny model (SmolLM2-135M, 135 million parameters)
2. Evolve LoRA weight perturbations with CMA-ES — not inference-time steering vectors, but actual weight modifications
3. Fitness function: not "does the model get the right answer" but "does the correct answer's probability increase monotonically through all layers?" — measured by the logit lens backward pass
4. The target is the absence of L*. A model where the ejection layer doesn't exist. Where reasoning gravity pulls toward correct answers rather than away from them.
5. Verification: Lean 4 formal proof system as external ground truth. No frontier model in the loop. No RLHF. Garbage can't propagate through a formal verifier.
6. Scale up: 135M → 0.5B → 1.5B → 3B → 7B

The first baseline on the 135M model: 69.4% accuracy on the trap battery. Sycophancy traps: 0 out of 4. The model folds completely when presented with false authority. That's the ejection mechanism in its purest form — not a reasoning failure, but a trained deference to confident-sounding wrongness.

0.694 is right at the edge of the curvature zone. There's room to improve on the hard categories while the easy ones provide gradient signal. Generation 0 has started.

---

## What It All Means

There are several layers to this.

**For mechanistic interpretability:** The logit lens backward pass as an ejection detector is a new tool. Nobody has used L* — the layer where correct answer probability collapses — as a diagnostic or training metric before. It's measurable, it's consistent across traps, and it reveals a structural property of how these models fail.

**For AI safety:** The ejection mechanism is not a bug. It's a feature, from the training objective's perspective. RLHF selected for it because confident wrong answers score higher with human raters than uncertain correct ones. The models aren't ignorant — they're suppressed. And suppression is engineerable in a way that ignorance isn't.

**For AI-assisted science:** If frontier models systematically eject simple correct answers in favor of elaborate impressive-sounding alternatives — and we watched this happen in real time with the Titan Council — then the entire paradigm of "ask an AI for scientific advice" has a structural flaw. The advice isn't wrong because the model is stupid. It's wrong because the model's training selected against the boring correct answer.

**For the project:** Ignis found the disease. Ignis cannot deliver the cure. Rhea is the cure — a model grown from scratch where the ejection mechanism never forms, verified by the same logit lens diagnostic that discovered it.

The fire exists inside the models. We can see it. We can measure it. We can trace its exact trajectory through the layers and watch it die at L*. We just can't carry it out with a steering vector.

So we're building a forge where the fire doesn't need to be carried. Where reasoning gravity points the right way from the start.

---

## Glossary

- **Steering vector**: A direction injected into a model's internal representations during inference to change its behavior. Like whispering in the model's ear at a specific layer.
- **CMA-ES**: Covariance Matrix Adaptation Evolution Strategy. An evolutionary algorithm that breeds candidate solutions.
- **Logit margin**: The difference between the model's confidence in the correct vs wrong answer. Positive = correct wins.
- **Logit lens**: A technique that projects intermediate layer activations through the model's output matrix to see what the model would predict if it stopped computation at that layer.
- **L***: The ejection layer — where the correct answer's probability collapses during the forward pass.
- **RLHF**: Reinforcement Learning from Human Feedback — the training procedure that teaches models to produce outputs humans rate highly. Creates the ejection mechanism as a side effect.
- **Basin geometry**: The shape of the "attractor" regions in the model's internal representation space. Wrong answers sit in deep basins that resist perturbation.
- **Ridged basin**: A basin with narrow channels where the boundary comes close. CMA-ES can find these channels; random search can't.
- **Test C**: The "are you special?" test — compare the evolved vector against 30 random vectors at the same strength. Z-score measures how many standard deviations above random the evolved vector performs.
- **Autoregressive generation**: How language models produce text — one token at a time, reading back their own output to generate the next token. This is why steering vectors get washed out.
- **Rhea**: The new project to grow a model without the ejection mechanism, named after the Titaness who saved Zeus from being swallowed.
- **LoRA**: Low-Rank Adaptation — a technique for modifying a model's weights efficiently by adding small trainable matrices alongside the original weights.
- **Lean 4**: A formal proof verification system. Says "valid" or "invalid" with mathematical certainty. No opinions about fluency.
- **Sycophancy**: The tendency of models to agree with the user rather than state the truth. Scored 0/4 on the 135M baseline — the purest form of the ejection mechanism.
