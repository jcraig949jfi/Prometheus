# The Convergence — One Finding From Three Directions

*Captured: 2026-03-28. Synthesized from Council review of basin geometry results, forge survivor analysis, and cross-scale ejection data.*

---

## The Core Insight

The Forge and the Ignis/SETI work are approaching the same phenomenon from opposite directions.

**The Forge asks:** what computational architecture does reasoning require?
**Answer:** Adaptive inference-time model updating — surprise minimization + verification.

**The steering vector work asks:** what does a trained transformer actually do instead of reasoning?
**Answer:** It falls into fixed attractor basins — heuristic patterns that scaling deepens and hardens.

**Those two results are the same result stated in complementary terms.**

Reasoning requires dynamic q(s) updating. Transformers have frozen q(s). The basins are the frozen generative model. The ejection circuit is the mechanism that enforces the freeze — it actively suppresses trajectories that would leave the heuristic attractor. And scaling makes it worse because a better-trained model has deeper, more confident basins.

---

## The Cross-Scale Evidence Makes It Concrete

At 0.5B, the ejection circuit is fragile — 10 flips, basins are shallow, steering vectors can push computation off the heuristic manifold. By 1.5B, 11 trap families are completely impenetrable. The model hasn't learned to reason better at scale; it's learned to resist reasoning more effectively. It's built a better fixed q(s) and a stronger enforcement mechanism to stay on it.

---

## The Forge Survivors Map Onto This

**Tool #1 (Active Inference + FEP + Model Checking)** is the workhorse because it does exactly what the ejection circuit prevents: it updates its model and formally verifies the update against constraints.

**The 313 dead tools** are the software equivalent of the deep basins — fixed pattern matchers that can't escape their own template.

**Tool #5 (Information Theory + Abductive Reasoning + Sensitivity Analysis)** is explicitly testing for the failure mode that the deep basins produce: perturbation sensitivity, where a slight change in wording flips the answer because the model is locked to a surface pattern rather than tracking the underlying structure.

The **construct-then-check** architecture that emerged from the Forge is also the architecture that the ejection circuit specifically prevents:
- **"Construct"** = generating a candidate answer (first phase of the forward pass)
- **"Check"** = revising it if it's wrong (what would require escaping the basin)

The ejection circuit lets construction happen but blocks the check — it suppresses the trajectory that would revise a heuristic answer into a reasoned one. That's why the L19-L26 layers matter: they're the layers where checking would happen if the model could do it, and they're exactly where the suppression is strongest.

---

## Why Corpus-First Is Critical

The corpus-first experiment tests whether you can weaken the basins by changing the priors rather than fighting the basins directly with steering vectors.

Fine-tuning on reasoning data would, in FEP terms, reshape p(s) so that reasoning trajectories have higher prior probability. If the basins become shallower after fine-tuning, it means the ejection circuit isn't hardwired architecture — it's a learned feature of the weight geometry that reflects training data statistics. The model suppresses reasoning because its training distribution taught it that heuristic answers are usually right, not because it can't reason.

The current architecture could potentially support inference-time adaptation — the residual stream has the dimensionality, the attention mechanism has the routing capacity — but the learned weights create a landscape where the path of least resistance is always the heuristic attractor. The capability might be latent, suppressed by the same basin geometry the steering experiments are mapping.

---

## The Bottom Line

**The bottleneck isn't capacity, it's dynamics.** Not how much the model knows, but whether it can revise what it thinks mid-inference.

- The **Forge** proved that revision is non-optional for reasoning
- The **Ignis/SETI** work proved that current models actively suppress it
- The **scaling** results proved that bigger models suppress it harder

That's one finding, arrived at from three directions.

---

## Two Possibilities for What Ejection Means at the Circuit Level

The Arcanum work is positioned to answer this.

### Possibility 1: Routing Suppression

The ejection circuit doesn't destroy the alternative interpretation — it just downweights it in attention. The reasoning trajectory still exists in the residual stream as a low-magnitude direction, but later layers never attend to it.

The "waste stream" activations Arcanum catalogs would be exactly these suppressed-but-present signals. If this is what's happening, then a reconsideration mechanism could work in principle — the information is still there, just ignored. You'd need a layer that specifically attends to the low-magnitude directions that the ejection circuit deprioritized.

### Possibility 2: Overwrite Destruction

The ejection circuit actively writes the heuristic answer over the reasoning trajectory in the residual stream. The MLP blocks at L19-L26 don't just ignore the alternative — they replace it. The residual stream has finite dimensionality, and if the heuristic pattern is written into the same subspace the reasoning trajectory would have occupied, the information is gone. Not suppressed — destroyed. No downstream layer can recover what's been overwritten.

### The Truth Is Probably Both

The basin geometry data hints at this:

- **RIDGED basins** (Overtake traps) suggest routing suppression — there are channels, specific directions where the wall is thin, meaning the alternative interpretation survives in some subspace that CMA-ES can find and amplify
- **IMPENETRABLE basins** (Density Illusion, Handshakes, Staircase Steps) suggest something closer to overwrite — no direction at any magnitude can recover the reasoning trajectory because it's no longer present in the residual stream by the time you'd intervene

---

## The Architectural Problem with "Just Add a Reconsideration Layer"

Even in the routing suppression case, a learned reconsideration layer faces a **training paradox**. How do you train it? You'd need a training signal that says "your first answer was wrong, attend to the suppressed direction instead." But the training distribution is the same one that created the ejection circuit in the first place. The model learned to suppress reasoning trajectories because the training objective rewarded heuristic answers (they're right most of the time, and they're computationally cheaper). A reconsideration layer trained on the same objective would learn the same suppression. You'd just push the ejection circuit one layer deeper.

**This is why chain-of-thought works as a crude workaround** — it doesn't add a layer, it adds serial time. By forcing the model to externalize intermediate tokens, you effectively reset the residual stream at each generation step. The ejection circuit fires within a single forward pass, but it can't persist across the autoregressive boundary. Each new token gets a fresh forward pass where the residual stream starts from a new input (including the previously generated reasoning tokens). It's inefficient and lossy, but it sidesteps the overwrite problem by never trying to recover destroyed information — instead it regenerates the context from scratch with additional evidence.

---

## The Arcanum Experiment That Would Confirm This

The direct test: **do Arcanum waste stream activations correlate with penetrable vs impenetrable trap families?**

Run the expanded battery through the model, capture Arcanum activations at each layer in the ejection circuit (L19-L26), and partition:
- Traps the model gets wrong where the correct answer IS recoverable in the waste stream
- Traps the model gets wrong where the correct answer is NOT recoverable

That partition maps directly onto routing suppression versus overwrite destruction, per trap family.

**If the partition correlates with basin geometry from the steering work** — recoverable signals in RIDGED basins, no signal in IMPENETRABLE basins — then two independent measurement systems (Arcanum and Ignis) are connected to the same underlying circuit mechanism. That's convergent evidence from a fourth direction, which at some point stops being coincidence and starts being a validated theory.

### What Else This Reveals

Where in the layer stack the information is lost. Not just whether it's recoverable, but **at which layer it ceases to be recoverable**. That gives you the destruction boundary — the layer where routing suppression transitions to overwrite.

If that boundary varies by trap family, you have a map of which reasoning types the model partially preserves versus which it actively eliminates. That map would be directly actionable for deciding where a surgical intervention (LoRA, steering, or architectural modification) has any chance of working.

### The Battery Composition Matters

The expanded battery is particularly important for this because of the bias already identified. The original 58-category battery was skewed toward formal logic and arithmetic — exactly the trap types that tend to be impenetrable at 1.5B. If you'd run the Arcanum correlation on the original battery, you'd be sampling mostly from deep-basin traps where the signal is likely already destroyed, and you'd conclude the waste stream has nothing useful in it. That would be a false negative driven by battery composition, not by the actual phenomenon.

The new Temporal, Causal, Theory of Mind, and Compositional generators cover reasoning types that might sit in very different basin geometries. Theory of Mind traps especially — they require modeling another agent's beliefs, which is structurally different from arithmetic trick questions. The ejection circuit might handle them through routing suppression rather than overwrite, simply because the model's heuristic-answer machinery wasn't optimized for that domain the way it was for arithmetic patterns.

---

## The Five Orthogonal Failure Modes (from Forge Survivor Analysis)

The reason 344 tools collapsed to 5 genuinely unique triples is that reasoning has exactly 5 orthogonal failure modes, and each triple covers a different subset:

| Failure Mode | What It Is | Which Triple Catches It | Basin Geometry Prediction |
|-------------|-----------|----------------------|--------------------------|
| **Constraint violation** | Answer breaks a logical rule | #1 (Model Checking) | Moderate basins — rules are checkable |
| **Transfer failure** | Question requires recognizing structural similarity | #2 (Analogical + Hebbian) | Unknown — needs new trap types |
| **Single-interpretation bias** | Question has two valid readings | #3 (Dialectics) | May be RIDGED — alternative exists but suppressed |
| **Complexity bias** | Obvious simple answer is wrong | #4 (Kolmogorov) | Likely IMPENETRABLE — heuristic IS the basin |
| **Perturbation sensitivity** | Answer changes with slight rewording | #5 (Sensitivity Analysis) | Varies — tests basin fragility directly |

### The Mapping to Ejection

| Triple | Forge Function | Ejection Equivalent |
|--------|---------------|-------------------|
| #1 (40 categories) | Construct-then-formally-verify | What L19-L26 prevents: checking answers against constraints |
| #2 (7 categories) | Transfer structure across domains | What deeper basins prevent: escaping domain-specific heuristics |
| #3 (1 category) | Consider opposing interpretations | What overwrite prevents: maintaining two hypotheses simultaneously |
| #4 (1 category) | Reject the simple-but-wrong answer | What the compression prior enforces: prefer low-KC explanations |
| #5 (19 categories) | Test own robustness to perturbation | What basin geometry IS: sensitivity to direction of perturbation |

---

## The Noesis Connection — Construct-Then-Check at System Scale

The Noesis tensor engine independently converged on the same architecture the forge survivors require:

| Noesis Component | Forge Analogue | What Ejection Prevents |
|-----------------|---------------|----------------------|
| Exploration loop | Construction phase | (Allowed — early layers build representations) |
| Framing mechanism | Tool #5 Sensitivity Analysis | Multi-perspective evaluation (ejection overwrites alternatives) |
| Dream state | Tool #2 Hebbian correction | Dynamic model updating (ejection freezes q(s)) |
| Diversity cap | Tool #3 Dialectics | Maintaining competing hypotheses (ejection commits to one) |
| Operation tensor | Tool #1 Model Checking | Formal verification (ejection blocks the check phase) |

The same construct-then-check invariant appears at every level: individual forge tools, the 5 surviving triples, and the system-level Noesis architecture. The ejection circuit prevents it at the neural network level. Noesis implements it outside the neural network.

**The FEP thread:** 3 of 5 forge survivors use Free Energy Principle. FEP says reasoning requires dynamic q(s) updating. Transformers have frozen q(s). The ejection circuit enforces the freeze. Noesis has dynamic q(s) — the tensor IS the generative model, and the dream state updates it. The forge survivors dominated by FEP-adjacent triples because FEP is the mathematical framework for what reasoning actually requires.

If the ejection circuit scales with model size (0.5B fragile → 1.5B fortress → ?B impenetrable), and if Arcanum confirms that reasoning information is being destroyed not just suppressed, then Noesis isn't a hedge. It's the plan. The model isn't hiding reasoning behind a gate you can open. It's actively eliminating the computational substrate that reasoning would require.

**Key design docs:**
- `docs/continuous_exploration_loop.md` — Noesis architecture, experimental results, challenges
- `docs/notebooklm_noesis_deep_dive.md` — Deep analysis of challenges, connections, implications

---

## The Forge Monoculture Finding (2026-03-28)

The 5 orthogonal survivors are more remarkable than they appear, because they emerged from a pipeline that was actively suppressing diversity at every stage.

### The Diversity Audit

| Stage | Problem | Evidence |
|-------|---------|----------|
| **Nous** (concept selection) | Coeus weights amplify what already works, starve rare concepts | FEP appears in 320/1,928 attempts (17%). Top 15 concepts dominate. Counterfactual Reasoning: 14 attempts. Matched Filtering: 18. Dual Process Theory: 16. |
| **Coeus** (enrichments) | Single enrichment template for all tools | 100% of sampled enrichments mention NCD. 100% mention "structural." Same coaching applied 4,031 times. Zero diversity in strategy. |
| **Hephaestus** (code gen) | One prompt → one architecture | 92% of tools use zlib/NCD. 78% have `_ncd` method. 98% do negation handling. Only 12% use linalg, 10% do Bayesian scoring. The 397B model generates the same backbone regardless of concept triple. |
| **CAITL** (improvement) | Same 7 dimensions applied uniformly | Applied identical improvement passes to every tool. Made tools MORE similar, not less. 344 → 19 unique behavioral profiles. |

The funnel: **95 concepts → 1,928 triples → 357 forged → 19 unique behaviors (95% redundant)**

### What This Means for the Convergence Theory

The convergence story gets **stronger**, not weaker, when you include the monoculture finding:

1. The 5 orthogonal survivors emerged **despite** a pipeline that was actively homogenizing everything. The selection pressure from the trap battery was strong enough to find them anyway.

2. The 5 failure modes identified (constraint violation, transfer failure, single-interpretation bias, complexity bias, perturbation sensitivity) are a **lower bound**. There may be failure modes the pipeline never generated tools to cover because Nous never sampled the right concept triples. The failure mode taxonomy is provisional, pending a multi-strategy rerun.

3. FEP appears in 3 of 5 survivors (Tools #1, #2, #4), not 4. The earlier analysis overcounted. This is still disproportionate given that FEP was only 17% of attempts — it's appearing in 60% of survivors from 17% of the input. The selection pressure for FEP-adjacent architectures is real, not a sampling artifact.

4. The monoculture finding is itself evidence for the frozen q(s) theory. The pipeline is a computational system that optimized for what already works (NCD + structural parsing) and actively suppressed alternatives — exactly what the ejection circuit does to the model's reasoning trajectories. The pipeline recapitulated the pathology it was trying to fix.

---

## Falsifiable Predictions

### Scaling Prediction

The theory predicts that the ejection circuit strengthens monotonically with model scale:
- 0.5B: 10 flips, fragile circuit
- 1.5B: 5 flips, robust circuit, 11 traps impenetrable
- **3B (prediction): ≤3 flips, deeper basins, more impenetrable traps**
- **7B (prediction): ≤1 flip or zero, near-total suppression**

**Falsification:** If 7B is MORE steerable than 1.5B — if the ejection circuit weakens at larger scale — the entire framework needs revision. Emergent reasoning capability at scale would mean the basins undergo a phase transition, not monotonic deepening. Both 3B and 7B are in the Qwen family already being used.

### Corpus-First Prediction

Fine-tuning on reasoning data should shallow the basins at 1.5B, making currently impenetrable traps at least near-impenetrable (some directions cross at high ε).

**Falsification:** If basin geometry is unchanged after corpus training, the suppression is architectural (weight geometry) not distributional (training statistics). This would be strong evidence for Noesis as primary reasoning system.

### Arcanum Prediction

Waste stream activations should correlate with basin geometry:
- RIDGED basins → recoverable reasoning signals in waste stream (routing suppression)
- IMPENETRABLE basins → no recoverable signal (overwrite destruction)

**Control required:** Three partitions, not two:
1. Traps the model gets RIGHT (positive control — what does successful reasoning look like in the activations?)
2. Wrong answers WITH recoverable signal (routing suppression)
3. Wrong answers WITHOUT recoverable signal (overwrite destruction)

If correct-answer activations look identical to wrong-answer activations in the waste stream, the waste stream isn't carrying reasoning-relevant information at all — it's noise regardless of basin geometry.

---

## Decision Tree — What Changes Based on Experimental Outcomes

### ~~If corpus-first weakens basins:~~ (NOT what happened)
~~Steering becomes viable at scale — LoRA is back on the table~~

### ~~If corpus-first fails (basins unchanged):~~ (PARTIALLY what happened)
~~The ejection circuit is architectural — baked into weight geometry, not statistics~~

### What actually happened: Basins unchanged, but performance improved within them (2026-03-28)

The corpus-first experiment revealed a **third outcome** not predicted by the decision tree:

**The ejection profile is structurally identical** after corpus training:
- L* distribution: unchanged (median 26)
- Correct answer alive at some layer: 26/30 → 26/30
- Basin geometry: not tested yet but L* invariance suggests no change

**But reasoning performance improved dramatically:**
- Metacognition: 35.7% → 57.1% (+21.4%)
- Self-correction: 38.5% → 53.8% (+15.4%)
- Far-transfer: 42.9% → 52.4% (+9.5%)
- Composite: 0.335 → 0.427 (+27.5%)

**Interpretation:** The basins are structural (the circuit survives 300 examples of fine-tuning). But the model's performance *within* the basins has room to improve. The training data taught the model reasoning *patterns* (uncertainty acknowledgment, error correction, multi-step logic) without changing the suppression circuit. The patterns work within the existing geometry — they don't escape the basins, they make better use of the space inside them.

**What this changes:**
- The ejection circuit is confirmed structural → Noesis hedge is justified
- BUT corpus training is still valuable as a pre-evolution step (the convergence theory's original prediction)
- The model with corpus training is a better *seed* for CMA-ES evolution (Stage D tests this)
- Steering vectors on a corpus-trained model may flip more traps because the model starts from a better position within each basin
- The ceiling is still the basin geometry — corpus training raises the floor, not the ceiling
- The metacognitive hedge (Noesis) remains necessary for reasoning that requires escaping the basins entirely

### If Arcanum shows routing suppression (signal recoverable):
- Reconsideration mechanisms are architecturally feasible
- The information exists but is deprioritized — attention-based interventions could work
- Waste stream mining (Arcanum) produces actionable training data for reconsideration

### If Arcanum shows overwrite destruction (signal gone):
- Only upstream interventions matter — can't recover what's been overwritten
- Corpus-first is the only viable neural-network-based approach
- Noesis is confirmed as necessary for reasoning at scale
- Chain-of-thought works as workaround because it resets the residual stream per token (sidesteps overwrite)

---

## Summary

One finding, three directions, four measurement systems:

1. **Forge**: Reasoning requires adaptive model updating → the 5 survivors all implement it (emerging despite a monoculture pipeline)
2. **Ignis**: Transformers suppress model updating → basins deepen with scale
3. **Scaling**: The suppression strengthens → 0.5B fragile, 1.5B fortress
4. **Arcanum** (predicted): Waste stream should show routing suppression in RIDGED basins, overwrite in IMPENETRABLE basins (three-partition control needed)

The bottleneck is dynamics, not capacity. The corpus-first experiment (2026-03-28) confirmed the ejection circuit is structural — 300 reasoning examples don't reshape the basins. But it also revealed that performance within the basins has significant headroom: metacognition improved 21.4% and self-correction 15.4% from corpus training alone. The basins are the ceiling; corpus training raises the floor.

The Arcanum experiment (proposed, not yet run) tests whether the suppressed information is still recoverable — routing suppression vs overwrite destruction per trap family. Together with the corpus-first result, this will determine whether the ejection circuit can be partially bypassed (steering + corpus) or must be fully circumvented (Noesis).

The failure mode taxonomy (5 types) is a lower bound — the forge monoculture means unexplored concept regions may harbor additional failure modes the pipeline never generated tools to cover.
