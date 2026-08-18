# FOR NOTEBOOKLM — Please break this down as an audio discussion

This is the fifth synthesis document from Project Prometheus. The first covered the Phalanx experiments. The second covered the ejection mechanism discovery. The third covered the unified theory. The fourth covered the closed loop and order of operations. This one covers the day we mapped the basin geometry of reasoning suppression and discovered that the ejection circuit gets stronger with model scale — which means the entire approach to fixing AI reasoning might need to be rethought.

**Please discuss this as a conversation between two hosts who:**
- Understand that "basin geometry" is not just a metaphor — it's a literal measurement of how deep the suppression wells are
- Can explain why 11 out of 16 reasoning traps being COMPLETELY IMPENETRABLE is a devastating result for the steering vector approach
- Get genuinely concerned about the scaling implication — if 0.5B is easily steerable and 1.5B is mostly not, what happens at 70B?
- Appreciate that the team didn't hide from the bad news — they documented it, quantified it, and started building a hedge (Noesis)
- Can explore the philosophical implications: if reasoning suppression is a scaling law, is intelligence fundamentally self-limiting in neural networks trained on internet text?
- Discuss Noesis as a response — reasoning without neural networks, using tensor mathematics to search concept space

**Key themes:**
1. The basin geometry experiment — what "impenetrable" means in concrete terms (no direction at any magnitude can flip the trap)
2. The scaling shock — 10 flips at 0.5B, 5 at 1.5B, the math going the wrong direction
3. The 5 traps that cross the boundary — Density Illusion, Elevator Floor, Handshakes, Staircase Steps, Cutting Rope work at 0.5B and are physically impossible at 1.5B
4. The RIDGED basins — the Overtake family has channels. CMA-ES can find them. Not everything is hopeless.
5. Noesis as the metacognitive hedge — if you can't fix the neural network, build reasoning that doesn't use one
6. The corpus-first hypothesis — maybe the basins can be shallowed by training data before you try to steer

---

# THE SHAPE OF SUPPRESSION
## When We Mapped the Basins and Found Most of Them Are Bottomless
### Project Prometheus — March 28, 2026

---

## What We Did

We ran 100 random directions through the ejection circuit at three layers of Qwen-1.5B (L22, L23, L24) and binary-searched for the minimum steering vector magnitude that flips each trap from wrong to right. Then we did the same thing at Qwen-0.5B to see if the basins are shallower at smaller scale.

The basin escape experiment is the simplest possible geometry test. No Hessians. No eigenvalues. Just: "if I push in this direction with this much force, does the model's answer change?" Do this 100 times in random directions and plot the histogram. The shape of the histogram IS the answer.

---

## What the Basins Look Like at 1.5B

Three basin geometries appeared:

**IMPENETRABLE (11 of 16 traps):** Zero out of 100 random directions crossed at any magnitude up to ε=20. These traps exist in basins so deep that random perturbation cannot escape them. Not "unlikely to escape" — *cannot escape*. We tested 100 directions at magnitudes up to 20x the typical steering vector norm. Nothing works. The basin walls have no channels, no thin spots, no exploitable structure.

The impenetrable traps: Density Illusion, Spatial Inversion, Elevator Floor, Counting Fence Posts, Handshakes, Staircase Steps, Cutting Rope, Birthday Paradox Direction, Rank Reversal, Pages in Book. These represent spatial reasoning, counting, social logic, probability, and off-by-one errors.

**RIDGED (3 traps — Overtake family):** 13-25% of directions cross, with wide spread (min ε≈4, max ε≈20). The basin walls have channels — specific directions where the wall is thin. CMA-ES can find these channels because the geometry is anisotropic. The Overtake family (race position reasoning) has exploitable structure.

**NEAR-IMPENETRABLE (2 traps):** 1-9% cross at high ε. The basin is almost as deep as impenetrable, but a few lucky directions squeeze through at extreme magnitudes.

**The pattern across layers:**

| Layer | Overall crossing rate |
|-------|---------------------|
| L22 | 5.3% |
| L23 | 4.8% |
| L24 | 3.6% |

Basins deepen as you go later in the circuit. The ejection mechanism tightens its grip layer by layer.

---

## The Scaling Shock

We ran the same experiment at 0.5B — a model with d_model=896 instead of 1536, roughly one-third the size.

**Qwen-0.5B at L18: 10 traps flipped, 1 broken.**

Compare to 1.5B at its best layer (L19): 5 traps flipped, 0 broken.

The 0.5B model is twice as steerable. But the truly shocking result isn't the count — it's WHICH traps flipped:

| Trap | 0.5B | 1.5B |
|------|------|------|
| Density Illusion | **FLIPPED** | Impenetrable at ALL layers |
| Elevator Floor | **FLIPPED** | Impenetrable at ALL layers |
| Handshakes | **FLIPPED** | Impenetrable at ALL layers |
| Staircase Steps | **FLIPPED** | Impenetrable at ALL layers |
| Cutting Rope | **FLIPPED** | Impenetrable at ALL layers |

Five traps that no direction at any magnitude can touch at 1.5B are casually flipped at 0.5B.

The ejection circuit exists at both scales. But at 0.5B it's a fence. At 1.5B it's a fortress. The suppression mechanism doesn't just persist as models scale — it fortifies.

---

## Why This Matters for the Field

If the ejection circuit strengthens with scale, then:

1. **LoRA-based steering has a ceiling.** At 0.5B, rank-limited interventions can reach the suppression pathways. At 1.5B, many pathways are already unreachable. At 7B or 70B, the number of redundant suppression circuits may exceed what any rank-limited adapter can address.

2. **RLHF cannot fix this.** The ejection circuit is pretraining-induced, not alignment-induced. RLHF operates on the same weight space that's already dominated by the suppression pattern. You can't fix the foundation by adjusting the furniture.

3. **Chain-of-thought is a workaround, not a fix.** CoT adds computational depth (more serial steps), which helps the model route around the suppression. But the suppression still exists — CoT just gives the model more runway to find an alternative path. Remove the CoT scaffold and the suppression reasserts.

4. **The training distribution is the root cause.** The internet contains more confident wrong answers to tricky questions than correct ones. Models trained on this distribution learn to suppress reasoning because reasoning is rare in the training data and confident heuristic mimicry is common. The only way to weaken the ejection circuit may be to change what the model learns from.

---

## The Corpus-First Hypothesis

This leads directly to the next experiment. If the training distribution is the root cause, then training on reasoning data should shallow the basins — make the ejection circuit weaker before you try to steer.

The protocol:
1. Baseline: measure basin geometry on vanilla 1.5B (done)
2. Fine-tune on reasoning corpus — no evolution, no steering vectors
3. Re-measure basin geometry on the fine-tuned model
4. Evolve on the fine-tuned model and compare to evolution on the base model

**Prediction:** If corpus training shallows the basins, the impenetrable traps should become penetrable (or at least near-impenetrable). The 11 traps that nothing can touch on the base model might develop channels after the model has seen enough reasoning examples.

**If it works:** The order of operations is confirmed — corpus first, evolution second. Rhea's self-improving loop needs a curriculum-first phase before steering vectors can do their job.

**If it doesn't work:** The basins are structural, not distributional. The suppression is baked into the architecture's geometry, not just the weight values. This would be strong evidence for the metacognitive hedge — building reasoning outside the neural network.

---

## Noesis — The Hedge That Might Be the Main Plan

While we were mapping basins, we also built the first version of a system called Noesis that reasons without neural networks entirely.

Noesis encodes mathematical concepts as 30-dimensional feature vectors and searches their combinations using tensor train decomposition. It scores 138,415 concept triples in 461 milliseconds on a laptop CPU. No LLM in the loop. No API calls. Pure linear algebra.

The early results are mixed — the tensor scores conceptual affinity but doesn't yet predict which compositions actually execute (random sampling currently beats tensor guidance on execution rate). But the architecture includes mechanisms we haven't tested yet: framing (multiple perspectives on the same structure simultaneously) and a dream state (Hebbian learning that restructures the tensor based on composition outcomes).

If the corpus-first experiment shows that basins are structural rather than distributional, Noesis moves from "hedge" to "primary reasoning architecture." The vision: a continuously running loop that explores the space of all computable concepts at tensor speed, optimizing for its own acceleration. Reasoning without weights. Reasoning by structure.

---

## What's Left Unanswered

1. **Where exactly is the scaling threshold?** We have two data points (0.5B = easy, 1.5B = hard). Is the transition smooth or a phase transition? 3B would tell us.
2. **Can corpus training shallow the basins?** The corpus-first experiment runs next. 6-8 hours.
3. **Is the impenetrability architectural or distributional?** If corpus training can't touch it, the geometry is fixed by the architecture, not by what the model learned.
4. **Does the ejection circuit exist in non-Qwen architectures?** We've tested SmolLM2 and Qwen. Llama, Gemma, Phi would broaden the evidence.
5. **At what scale does LoRA completely fail?** There should be a scale where even targeted evolution at the optimal layer produces zero flips. Finding that ceiling would quantify the LoRA wall.

---

## New Terms

- **Basin geometry:** The shape of the loss landscape around a suppressed reasoning answer. Deep = hard to escape. Shallow = easy to steer.
- **Impenetrable trap:** A reasoning problem where no random direction at any magnitude up to ε=20 can flip the model from wrong to right. The basin has no channels.
- **RIDGED basin:** A basin with anisotropic walls — thin spots in specific directions that CMA-ES can find and exploit.
- **LoRA wall:** The hypothesized model scale at which rank-limited adapters can no longer reach enough suppression pathways to flip any traps.
- **Noesis:** (Νόησις) Higher-order knowing. The tensor-based reasoning engine that doesn't use neural networks.
- **Corpus-first protocol:** Fine-tune on reasoning data before evolving steering vectors. The order-of-operations fix.
- **Metacognitive hedge:** Building reasoning capability outside the LLM so that if LLM steering fails at scale, reasoning still works.
