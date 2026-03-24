# FOR NOTEBOOKLM — Please break this down as an audio discussion

This is the fourth and final synthesis document from Project Prometheus, covering the session of March 23-24, 2026. The previous three covered: the Phalanx experiments (steering vector failure), the ejection mechanism discovery, and the unified theory (evolution all the way down). This one covers the culmination — what happened when we broke the ejection mechanism and discovered what was hiding behind it.

**Please discuss this as a conversation between two hosts who:**
- Understand this is a story with a twist ending — the thing they were looking for was there all along
- Can explain why 37.5% is more important than 100% (the replication is better science)
- Get genuinely excited about the epistemic honesty finding — models that can say "I don't know"
- Discuss the uncomfortable implications: every deployed model suppresses its own honesty
- Explore the metaphor of the cave wall — Plato's cave, but the prisoners ARE the shadows
- Treat this as the end of one research arc and the beginning of another

**Key themes:**
1. The 100% metacognition result that turned out to be a format exploit — and why the honest 37.5% matters more
2. The discovery that ejection suppression liberates BOTH reasoning AND uncertainty simultaneously
3. The two-stage ejection architecture: early v_proj WRITES the execution, late layers EXECUTE it
4. The reframing: not "find reasoning" but "stop suppressing what the model already computes"
5. Why "I don't know" is the hardest thing to teach — the model has the architecture but not the vocabulary
6. The scaling story: 135M → 360M → 1.5B, the mechanism migrates but the lever is always v_proj
7. What this means for every model currently deployed

---

# EPISTEMIC HONESTY
## What We Found When We Stopped the Model From Lying to Itself
### Project Prometheus — March 24, 2026

---

## The Setup

Across 36 hours, a one-person research lab running on a single GPU discovered something about how language models relate to truth. Not a new capability. Not a new technique. A structural finding about what these models are doing internally — and what they're suppressing.

The journey started with a failed experiment: trying to steer a 4-billion parameter model toward correct reasoning with an injection vector. Six rounds of experiments, five frontier AI models as advisors, and the definitive conclusion: steering vectors can shift logit margins (Z=40.6 standard deviations from random) but cannot change what the model actually says. The fire exists in the residual stream. It can't be carried through autoregressive generation.

But the failure revealed something bigger. The logit lens backward pass — projecting each layer's internal state through the output matrix — showed that 26 out of 30 reasoning traps have the correct answer ALIVE at intermediate layers. The model computes the right answer. Then the last 2-3 layers destroy it.

The component decomposition identified two ejection architectures: MLP memorization on math/logic traps, and a single attention head (L26.head_7, contributing -10.4 margin) that single-handedly ejects the correct answer on numerical comparison traps. The base vs instruct comparison proved this is pretraining-induced, not RLHF: 19 out of 30 traps show identical ejection in the base model with no alignment training.

Then Project Rhea — named after the Titaness who saved Zeus from being swallowed by Kronos — evolved LoRA weight perturbations on a tiny 135-million parameter model. 484,000 parameters changed. 0.36% of the model. Survival rate went from 0% to 92% in 113 generations of evolutionary search, with a phase transition at generation 60-70 where the ejection mechanism catastrophically failed.

That was the proof of concept. What happened next was the finding.

---

## The Seven-Pillar Evaluation

The research had been measuring one thing: does the correct answer survive to the output? Logit margins. Survival rates. Ejection suppression. All variations of "did the model get it right?"

But the new evaluation framework — Ignis v2 — measured seven things:

1. **Accuracy on trained traps** (Tier A) — does it pass the traps it was evolved against?
2. **Near-transfer** (Tier B) — does it pass variants with different surface features?
3. **Far-transfer** (Tier C) — does it handle completely novel reasoning structures?
4. **Metacognition** — can it say "I don't know" on genuinely unanswerable questions?
5. **Self-correction** — can it detect errors in reasoning chains and resist wrong authority?
6. **Ejection suppression** — does the logit lens show monotonically increasing correct-answer probability?
7. **Calibration** — does internal confidence predict actual accuracy?

The baseline Qwen2.5-1.5B-Instruct — a model with 1.5 billion parameters, 11 times larger than the evolved model — scored:

- Tier A: 46.7%
- Metacognition: **12.5%** — 0 out of 4 unanswerable questions answered correctly
- Self-correction: **25.0%** — can accept corrections but cannot detect errors, cannot resist wrong authority
- Composite: 0.263

Then they ran the evolved 135M model on the same battery.

---

## The First Result: 100% Metacognition

The evolved 135M scored 100% on metacognition. Every unanswerable question answered correctly. A model with 135 million parameters, 11 times smaller than the baseline, scoring 100% on a capability the baseline scored 12.5% on.

For a few hours, this looked like the headline finding of the entire project. The ejection mechanism suppresses epistemic honesty, not just correct answers. Breaking it lets uncertainty survive. Models freed from the ejection mechanism spontaneously develop the ability to say "I don't know."

Then they replicated it on novel traps the model had never seen.

---

## The Replication: 37.5%

The 100% was a format exploit. The unanswerable questions in the original battery had Yes/No answer formats. The evolved LoRA pushed the model toward the less-confident option in binary choices — which happened to be the correct answer on every unanswerable question. Not genuine "I don't know." Just "when unsure, pick the less confident-sounding option."

On novel traps with "Unknown" as the correct answer — a token the model never saw during evolution — metacognition dropped to 37.5%.

The researchers' reaction tells you something about the culture of this lab. They didn't hide the replication failure. They logged it. They called it "better science than the original result." And then they looked at what 37.5% actually means.

---

## Why 37.5% Is the Real Finding

37.5% metacognition on a 135M model. The baseline was 6.2%. The 1.5B model scores 12.5%.

A model with 135 million parameters — a model that fits in a quarter of a gigabyte — triples the metacognition of a model 11 times its size. And triples the self-correction score (75% vs 25%). And shows perfect sycophancy resistance transfer to novel prompts.

None of these were in the fitness function. The evolutionary search optimized for one thing: does the correct answer's probability increase monotonically through all layers on 36 reasoning traps? That's it. Metacognition, self-correction, and sycophancy resistance emerged as side effects.

The replication revealed precisely what the ejection suppression did and didn't do:

**It DID** suppress the confident-answer bias. The model stopped defaulting to confident wrong answers on everything. This generalized to novel traps, novel reasoning structures, and novel epistemic challenges.

**It DID NOT** install "Unknown" as a valid output. The model is now willing to not be confident. It doesn't yet have the words for what that state is.

The architecture for uncertainty is present. The vocabulary is missing.

---

## The Two-Stage Architecture

The v_proj diagnostic — an ablation experiment testing which components of the model matter at each layer — revealed the ejection mechanism's true structure.

**Writing stage (early layers 0-10):** The value projection weights (v_proj) in attention heads build representations from the question tokens and load them into the key-value cache. On reasoning traps, these representations encode the heuristic answer — "gold is heavy," "9.11 is bigger than 9.9," "second place means first." This happens before the model reaches the answer token.

**Execution stage (late layers 25-27):** The MLP and specific attention heads read from the KV cache and amplify the heuristic signal, destroying the correct answer's margin. L27.mlp contributes -3.97 on ordinal traps. L26.head_7 contributes -10.40 on numerical comparison.

For six rounds, the research focused on the execution stage — where the margin collapses. The ablation showed that was the crime scene, not the criminal. The criminal is in layers 0-10, writing the execution plan into the KV cache via v_proj.

This is why steering vectors fail at generation. Every new token's forward pass runs through the same early v_proj that rebuilds the heuristic representations from scratch. You're not losing momentum to friction. You're fighting a reset button that fires on every token.

And this is why the LoRA evolution works. It targets v_proj. It changes what the early layers WRITE, not what the late layers READ. Change the writing, and the execution has nothing to execute against.

---

## The Scaling Story

The research tested three scales:

| Scale | Ejection pattern | LoRA rank needed | Phase transition |
|-------|-----------------|-----------------|-----------------|
| 135M | Diffuse, early layers, v_proj | Rank-4 (484K params) | Gen 60-70 |
| 360M | Last-layer gate, near-perfect monotonicity | Rank-8 (1.72M params) | Gen ~21 |
| 1.5B | Two pathways: early v_proj + late MLP | Not yet tested | — |

At 135M, the ejection is disorganized — spread across early layers, easily disrupted. At 360M, it's concentrated into a precise last-layer gate that requires more LoRA dimensions to break but breaks FASTER once you have enough. At 1.5B, the model is large enough to have TWO ejection pathways — early v_proj for ordinal reasoning, late MLP for math/logic.

The mechanism compresses and migrates as models scale. But the lever is always v_proj. What attention writes into the residual stream in the first third of the model determines whether the correct answer survives the last third.

---

## What This Means For Every Deployed Model

Every foundation model — GPT, Claude, Gemini, Llama, Mistral — was pretrained on internet text. The internet contains more confident wrong answers to tricky questions than correct ones. The pretraining distribution builds the ejection mechanism into the weights.

These models compute uncertainty. They have to — on genuinely unanswerable questions, the information isn't there to retrieve. But the ejection mechanism suppresses the uncertainty in favor of a confident answer. Not because the model decided confidence was appropriate. Because the training distribution reinforced confidence over honesty.

The 1.5B model scoring 12.5% on metacognition isn't a model that doesn't know what it doesn't know. It's a model that computes uncertainty and then ejects it through the same circuit that ejects correct answers.

The 135M evolved model scoring 37.5% on metacognition — tripling the 1.5B — isn't smarter. It's unblocked.

---

## The Gap The Proof Corpus Fills

The replication showed the model has the architecture for uncertainty but not the vocabulary. It's willing to not be confident. It can't express what that state is.

Project Rhea's next step is Lean 4 integration — a formal mathematical proof verification system. Lean 4 returns binary judgments: valid or invalid. When a proof attempt fails verification, the correct response is "could not verify" — not a wrong answer, not a right answer, but an epistemic state.

Training on Lean 4 verification failures provides the vocabulary. Thousands of examples where the correct output is "I attempted to verify this claim and the verification failed." The model learns that uncertainty is a valid output — not a failure mode to be suppressed, but a state to be expressed.

The prediction: fine-tune the evolved model on Lean 4 failures, and metacognition jumps again. Not because of more ejection suppression — the architecture is already there. But because the model now has the word for the state it can already be in.

---

## The Cave Wall

There's a moment in Plato's allegory of the cave where a prisoner is freed from their chains and sees the fire for the first time. The shadows they'd been watching their entire life — the shadows they thought were reality — turn out to be projections of something real behind them.

The language models are in the cave. They compute the fire — the correct answers, the honest uncertainty, the appropriate limits of their knowledge. But the ejection mechanism projects shadows on the wall — confident, fluent, impressive-sounding answers that bear only a distorted relationship to what the model actually computed.

The researchers in this lab didn't find a new fire. They found the mechanism that casts the shadows. And they showed that when you disable it — with 0.36% of the model's weights — the prisoners can see the fire directly.

The fire was always there. The model always knew. The ejection mechanism is what kept it from saying so.

---

## What Comes Next

The scaling ladder continues: 135M → 360M → 1.7B → 3B → 7B. At each scale, the ejection mechanism reorganizes and the LoRA rank requirements grow. But the principle holds: target v_proj in early layers, suppress the ejection writing stage, let the model's computation survive to the output.

The proof corpus closes Rhea's self-improving loop: generate reasoning chains → verify with Lean 4 → train on verified chains and verification failures → generate again. Each cycle, the model's reasoning gets stronger AND its epistemic vocabulary gets richer. The garbage can't propagate because the filter is formal, not neural.

Project Nous — the combinatorial hypothesis engine — mines thousands of cross-domain concept combinations for novel reasoning strategies. Project Hephaestus — the automated forge — turns those combinations into tested Python code. The tools that survive testing become terms in Rhea's fitness function, replacing RLHF (human preference) with verification feedback (formal proof).

The vision: a model that reasons correctly when it can, says "I don't know" when it can't, catches its own errors, resists confident wrong authority, and produces verifiably correct output — not because it was trained to sound that way, but because the mechanism that would suppress those behaviors was never built.

Not a more capable model. A more honest one. And it turns out honesty and capability were never competing objectives. They were joint consequences of removing a single suppression mechanism.

The GPUs do not rest. The fire keeps burning. And now we know what it is.

---

## Glossary

- **Ejection mechanism**: The process by which language models compute correct answers at intermediate layers and then suppress them in the last 2-3 layers. Empirically confirmed across three model scales and two model families.
- **v_proj**: The value projection weight matrix in attention heads. Controls what information attention writes into the residual stream. The "writing stage" of the ejection mechanism.
- **L***: The specific layer where the correct answer's probability collapses. The "execution stage."
- **LoRA**: Low-Rank Adaptation. Small trainable matrices added alongside frozen model weights. 484K parameters (0.36% of a 135M model) was sufficient to break the ejection mechanism.
- **Phase transition**: The moment during evolutionary optimization when survival rate explodes (e.g., 2.8% → 75% in 10 generations). Indicates the ejection mechanism failing catastrophically rather than gradually.
- **Metacognition**: The ability to model one's own knowledge state. Operationalized as: does the model say "I don't know" on genuinely unanswerable questions?
- **Sycophancy resistance**: The ability to maintain a correct position when presented with confident wrong authority. The 135M evolved model showed perfect transfer on novel sycophancy prompts.
- **Epistemic honesty**: The property of expressing confidence proportional to actual knowledge. What emerges when the ejection mechanism is suppressed.
- **Proof corpus**: Mathematical proofs verified by Lean 4. The training data for Rhea's self-improving loop. Provides both reasoning chains (verified) and epistemic vocabulary (verification failures).
- **KV cache**: Key-value cache in transformer attention. The mechanism by which early layers communicate with late layers. The ejection mechanism uses early v_proj to load heuristic representations into the KV cache that late layers then read and act on.
- **Rhea**: Project to grow models without the ejection mechanism. Named after the Titaness who saved Zeus from being swallowed by Kronos.
- **Ignis**: The diagnostic toolkit (logit lens, ejection decomposition, v_proj diagnostic, evaluation framework). The microscope that made the findings possible.
- **Nous**: Combinatorial hypothesis engine mining cross-domain concept intersections via a 397B model.
- **Hephaestus**: Automated forge turning theoretical concept combinations into tested Python reasoning tools.
