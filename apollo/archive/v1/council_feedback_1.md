
The Council's Feeback after V2 that lead to design V3

[CHATGPT]

You’re doing something unusually well thought-out for this class of system. Most OEE / GP designs fail because they’re hand-wavy at exactly the layers you’ve specified concretely (execution model, fitness, mutation operators, logging). That said, there are a few **hard failure modes** in your current design that will likely kill the run early or quietly collapse it into triviality.

I’ll go point-by-point on your concerns, then give you the **non-negotiables + early warning signals**.

---

# 1) Bootstrap Viability — *your current plan is good but not sufficient*

Seeding with 50 working organisms is **necessary but not sufficient**.

### The real problem

Your system doesn’t fail because the initial population is invalid — it fails because:

> **the first generation of offspring has near-zero *semantic viability***
> (not just syntactic viability)

Your compiler catches:

* syntax
* imports
* interface
* some wiring issues

But it **does not guarantee meaningful signal flow**.

### Failure mode you will see

Within ~5–20 generations:

* Many offspring compile
* Most produce **constant or near-constant scores**
* Selection pressure collapses to:

  * “does it crash less?”
  * “does it approximate NCD?”

→ **No gradient → stagnation**

---

## What you should add (non-negotiable)

### 1. Typed I/O contracts for genes (lightweight, not strict typing)

Right now:

```
ctx['parsed'] = ANYTHING
ctx['score'] = float
```

You need **semantic shape constraints**, not just key presence.

Add metadata per gene:

```python
input_schema = {
  'parsed': 'list[float] | dict | str | None',
}
output_schema = {
  'score': 'float (finite, non-NaN)'
}
```

Then at compile time:

* insert **auto-generated guards**
* or reject obviously incompatible compositions

Without this, recombination is mostly noise.

---

### 2. “Signal sanity checks” during viability spike

Before allowing AST-only mutation, measure:

* % of offspring with:

  * non-constant output across candidates
  * variance in scores > ε
  * different outputs for different prompts

If not, your system is **functionally dead even if it “runs”**

---

### 3. Partial evaluation instead of hard failure

Right now:

> gene crash → score 0

That’s too harsh and kills gradient.

Instead:

* allow **masked execution**
* fallback to previous ctx values
* or inject penalty but continue

You want:

> degraded organisms, not dead organisms

---

### 4. “Safe scaffolds” for early generations

For first ~50–100 generations:

* enforce at least:

  * 1 PARSER
  * 1 SCORER
  * optional FALLBACK

Otherwise you’ll get:

* scorer-only loops
* parser-only no-ops
* degenerate pipelines

---

## Verdict on bootstrap

Your plan gets you **alive organisms**, not **evolvable organisms**.

Add:

* schema constraints
* signal checks
* scaffold constraints (temporary)

---

# 2) NCD Convergence — *this is your biggest existential risk*

You’re absolutely right to worry. This is not a minor issue.

### What will happen without intervention

Within ~100–300 generations:

* Population converges to:

  > “NCD + tiny perturbations”

Because:

* NCD gives immediate fitness
* your objectives reward margin-over-NCD, not independence-from-NCD

This creates a **local optimum attractor**.

---

## Why your current mitigation is insufficient

> “must beat NCD” + novelty

Problem:

* Beating NCD by 1–2% is easy with small tweaks
* Novelty is behavioral → NCD variants can still be “novel”

→ You still converge

---

## What you should do (strong recommendation)

### Option A (best): Penalize reliance on NCD

Track:

```python
ncd_usage_ratio = fraction of score derived from fallback
```

Add:

* soft penalty OR
* 4th objective OR
* constraint

---

### Option B: Gate NCD availability (phased removal)

* Generations 0–200: allow NCD
* 200–600: probabilistic removal
* > 600: NCD only allowed in minority of population

This mimics:

> curriculum learning away from crutches

---

### Option C: Make NCD adversarial

Occasionally:

* inject tasks where NCD fails catastrophically

This creates **selection pressure against over-reliance**

---

### What NOT to do

> “Remove NCD entirely at start”

That will:

* destroy early gradient
* increase crash rate
* likely fail bootstrap

---

## Verdict on NCD

You need **active pressure against it**, not just baseline comparison.

---

# 3) Gene Extraction Fragility — *you’re right, and it’s deeper than you think*

### Core issue

Method-level extraction assumes:

> methods are composable units

In your system, many are actually:

* **context-dependent**
* **format-dependent**
* **language-dependent**

---

## What’s actually happening

You have two gene classes:

### A) True functional genes (good)

* math transforms
* scoring functions
* probabilistic updates

### B) “Entangled” genes (dangerous)

* regex-heavy parsing
* format assumptions
* English heuristics

These will:

* silently fail when recombined
* degrade signal quality

---

## Recommendation (important)

### Move to **hybrid granularity**

Not just method-level.

Define:

### 1. Micro-genes (fine)

* math ops
* scoring primitives

### 2. Meso-genes (your current level)

* methods

### 3. Macro-genes (new, critical)

* parser + scorer bundles
* coherent sub-pipelines

---

### Why this matters

Evolution needs:

* **building blocks that actually work when moved**

Right now ~50% of your genes are:

> “organs removed without circulatory system”

---

## Minimal fix for MVP

Tag genes:

```python
portability_score ∈ [0,1]
```

Then:

* bias mutation toward high-portability genes early
* slowly introduce fragile ones later

---

# 4) Computational Budget — *you are likely generation-starved*

Your estimate:

> ~1,600 generations

For:

* population 50
* 3 objectives
* structural evolution

This is **borderline insufficient**.

---

## Empirical intuition (from GP / NEAT / Avida-like systems)

* meaningful structural innovation often takes:

  > 5k–50k generations

---

## Tradeoff decision

You asked:

> fewer tasks vs more generations?

### Strong recommendation:

**Yes — reduce evaluation cost to buy generations**

Specifically:

* 20 tasks → 10–12 tasks
* 2s timeout → 1s (or adaptive)

Then:

* double generation count

---

## Why

Early evolution needs:

> **more selection cycles, not more precise evaluation**

Noise is acceptable early.
Stagnation is not.

---

# 5) The “Interesting Gap” — avoiding fake reasoning

Your held-out battery is good, but not sufficient.

---

## Core failure mode

Organisms evolve:

> **task-specific heuristics that generalize within the trap distribution**

Even held-out seeds won’t fully prevent this.

---

## What you should add

### 1. Invariance tests (VERY important)

For same task:

* paraphrase prompt
* reorder candidates
* add irrelevant info

Measure:

* output stability

Add as:

* fitness penalty OR
* additional objective later

---

### 2. Counterfactual consistency

If:

* A > B
* B > C

Then:

* A > C

You already have some traps like this — expand it.

---

### 3. Process-based signals (cheap proxy for “reasoning”)

Use:

```python
ctx['_gene_trace']
```

Reward:

* multi-step transformations
* non-trivial intermediate states

Penalize:

* single-step collapse to fallback

---

### 4. Difficulty ramping (you mention it, make it central)

Static tasks → overfitting

You need:

* gradually harder compositional tasks

---

# 6) Non-Negotiable Design Decisions (MVP)

If you get these wrong, the run likely fails:

---

## 1. Maintain gradient (most important)

Ensure:

* most organisms produce **non-constant outputs**
* partial success survives

---

## 2. Control NCD dominance

Without this:

> your system becomes “NCD optimizer with noise”

---

## 3. Preserve functional building blocks

If recombination destroys semantics:

> evolution cannot accumulate complexity

---

## 4. Prioritize generations over evaluation fidelity

Evolution is iteration-hungry.

---

## 5. Measure behavior, not just outcomes

Your novelty system is good — extend it to:

* invariance
* trace complexity

---

# 7) What to Monitor from Generation 1

These are your **early death indicators**:

---

## 🚨 1. Output variance

If:

* most organisms produce near-constant scores

→ system is dead

---

## 🚨 2. NCD correlation

Track:

```python
corr(organism_scores, ncd_scores)
```

If → 0.9+ across population:
→ collapse to NCD

---

## 🚨 3. Novelty trajectory

If archive growth:

* plateaus early (<100 gens)

→ convergence

---

## 🚨 4. Functional gene usage

Track:

* % of genes actually affecting output

If many genes:

* write but don’t influence final score

→ bloat without function

---

## 🚨 5. Self-referential fitness delta

If:

* self-referential organisms appear but are always worse

→ your environment doesn’t reward metacognition

---

## 🚨 6. Crash rate trend

If:

* increases over time

→ mutation too destructive

If:

* drops to zero too fast

→ population homogenized

---

# 8) What I Would Change (Concise)

If I had to modify your design minimally but impactfully:

---

### 1. Add gene I/O schemas + runtime guards

Prevents silent semantic breakage.

---

### 2. Add NCD usage penalty (not removal)

Critical for long-term diversity.

---

### 3. Reduce evaluation cost → double generations

More evolution cycles > more accurate fitness.

---

### 4. Introduce macro-genes (bundled subgraphs)

Enables real recombination.

---

### 5. Add invariance-based fitness signals

Prevents shallow heuristics.

---

### 6. Add early-generation scaffolding constraints

Then remove after ~100 gens.

---

# Final Take

This is one of the more credible attempts at **practical open-ended program evolution** I’ve seen, but the failure modes are predictable:

* **Silent semantic collapse** (genes don’t compose)
* **NCD attractor basin**
* **Insufficient evolutionary time**
* **Fake novelty without capability**

If you solve:

1. gradient preservation
2. NCD suppression
3. composable building blocks

→ you have a real shot at producing **genuinely improved reasoning organisms within 40 days**

If not, the system will:

> look alive in logs, but be functionally stagnant.

---

If you want, I can go one level deeper and:

* simulate likely evolutionary dynamics of your system
* or propose a “Phase 1 diagnostic dashboard” to catch failure in the first 24 hours


[END CHATGPT]


[DEEPSEEK]

This is a thoughtful, highly detailed design. The core idea—evolving composable reasoning algorithms via AST‑level gene recombination—is compelling, and the extensive mitigation for known failure modes (sandboxing, checkpointing, phase‑0 warm‑up) shows you’ve learned from prior open‑ended evolution (OEE) efforts. Below I address your specific concerns, highlight additional architectural risks, and suggest concrete adjustments to maximize the chance of a meaningful run.

---

## 1. Bootstrap Viability

**Your approach:** seed with 50 original tools (post‑CMA‑ES) and run a viability spike to decide mutation strategy.  
**Risk:** Even with a good seed, the first generation of crossover/mutation will produce many non‑viable chimeras because:
- Different tools expect different input structures (e.g., one parser writes `ctx['tokens']`, another reads `ctx['parsed']`).
- Parameter names are rewritten, but the wiring graph may still contain unresolved dependencies.
- The initial population contains only whole tools, not recombined ones. The first offspring will be the first time recombination is tried.

**Recommendations:**
1. **Inject a small number of pre‑tested chimeras** into the initial population. After phase‑0, run a script that attempts a few safe recombinations (e.g., take two tools, swap a SCORER from one into the other) and keep only those that compile and run on 5 tasks without crashing. Add 5–10 such survivors to the seed population. This creates a “stepping stone” for the crossover operator.
2. **Enforce a stricter gene interface** during extraction. Rather than rewriting parameters alone, also standardise the keys each gene reads and writes. For example, require all PARSER genes to read `ctx['raw_text']` and write `ctx['parsed']`; all SCORER genes to read `ctx['parsed']` (or `ctx['raw_text']`) and write `ctx['score']`. This is the **context‑dict convention** already described, but it must be enforced at extraction time—if a gene writes to a non‑standard key, it should be rejected or automatically retargeted.
3. **Add a “gene compatibility” pre‑filter** to the gene library. For each gene, record its required input keys and produced output keys (based on static analysis). Then during crossover, reject connections where the upstream gene’s output set does not contain the downstream gene’s required input. This can be done cheaply at compile time, preventing many dead offspring.

The viability spike (measuring the fraction of random chimeras that compile) is an excellent diagnostic, but it should also trigger **automatic widening** of the initial population if viability is low—for example, by temporarily using whole‑tool crossover only (i.e., swapping entire tools) until viability exceeds a threshold.

---

## 2. NCD Convergence

**Your approach:** treat NCD as a baseline (organism must beat it to get positive margin accuracy) and include novelty as a separate Pareto objective.  
**Risk:** NCD is a strong baseline; 87% of tools have it as a fallback. Under selection for margin accuracy, organisms that simply replicate NCD (or add tiny decorations) will have zero margin, while those that deviate even slightly may have negative margin. The fitness landscape is therefore extremely rugged near the NCD “ridge.” Novelty may push away from NCD, but if novelty is only measured by score vectors (behavioural signature), it may still permit organisms that use NCD but with different parameter values—because their score vectors will be similar to NCD’s. This could lead to a population of NCD‑derived organisms with negligible diversity.

**Recommendations:**
1. **Make NCD unavailable as a gene.** Do not extract the NCD method as a SCORER or FALLBACK. Instead, treat NCD as a fixed external baseline that is always computed, but the organism cannot use it. This forces evolution to discover alternatives. The drawback is that many tools rely on NCD as a fallback; if you remove it, those tools become less fit initially. However, you already have a subset of tools that do not use NCD (13%). You could start with only those tools as the initial population, then reintroduce NCD later if diversity stalls.
2. **Use a margin that is multiplicative rather than additive.** Instead of `organism_accuracy - ncd_accuracy`, use `organism_accuracy / (ncd_accuracy + ε)`. This rewards even small improvements over NCD and penalises falling below more harshly. Combined with novelty, it might encourage divergence.
3. **Add a fourth objective:** “NCD‑independence” – a measure of how much the organism’s behaviour differs from NCD. This could be the KL divergence between the organism’s output distribution and NCD’s on a set of tasks. It directly pushes away from NCD.

---

## 3. Gene Extraction Fragility

**Your analysis:** ~50% of gene types are cleanly extractable; the other half are tightly coupled to answer formats or use complex regex patterns.  
**Risk:** The extracted gene library will contain many genes that are non‑portable—they may crash when given different input formats, or produce nonsensical outputs. This will increase the failure rate during compilation and evaluation, reducing effective population size and slowing evolution.

**Recommendations:**
1. **Perform a manual or semi‑automated pass** over the 146 tools to identify “good citizen” genes that are self‑contained, use only numpy/stdlib, and rely only on the context‑dict conventions. Build the initial gene library from only those high‑confidence genes. You can later add more as the system proves itself.
2. **Use a coarser granularity for initial evolution.** Start with whole tools as atomic units (i.e., no gene‑level recombination). After some generations, gradually enable finer‑grained recombination (e.g., first allow swapping entire SCORERs between tools, then later allow PARSERs, etc.). This is akin to a **multi‑scale representation** that avoids too many lethal chimeras early on.
3. **Implement a “gene test suite”** that checks each extracted gene on a standard set of inputs (e.g., simple text prompts and candidates). If the gene crashes or produces outputs outside expected ranges, it is flagged as “risky” and can only be used after a certain generation or with a penalty.
4. **Rewrite regex patterns** to be parameterised or replaced with more general parsers. For example, many tools contain regex for extracting numbers from English text. Instead of extracting that regex as is, replace it with a call to a standard utility (e.g., `_extract_numbers()`) that uses a parameterised pattern. This makes the gene more portable.

---

## 4. Computational Budget

**Your calculation:** 1,600 generations over 37 days (assuming 33 min/gen).  
**Risk:** 1,600 generations may be insufficient for complex structural evolution to produce meaningful metacognition. In many GP systems, thousands of generations are needed even for simple symbolic regression. With a population of 50 and three objectives, selection pressure is diffuse; the system may need more generations to explore the space.

**Recommendations:**
1. **Reduce evaluation cost aggressively.**  
   - Use fewer tasks: 15 seed traps + 5 generated = 20 tasks. Could start with 10 total (5 seeds + 5 generated) and only increase if the median fitness plateaus.  
   - Reduce timeout to 1 second (most tools run in <0.1s).  
   - Use a **multi‑stage evaluation**: quick screen on 3 easy tasks (0.5s) → if passes, evaluate on 10 tasks (1s) → only if top 20% of population, evaluate on full 20 tasks (2s). This reduces average evaluation time.  
   - Parallelise across CPU cores. The sandbox model using multiprocessing can easily evaluate multiple organisms in parallel. With 8 cores, evaluation time could drop to ~4 min/gen.
2. **Increase generation count by accepting a smaller population.** 50 is a reasonable number for NSGA‑II, but you could reduce to 30 and increase offspring to 60, maintaining the same total evaluation per generation while allowing more generations. The diversity loss may be offset by faster turnover.
3. **Use a surrogate model** to approximate fitness for the first few generations, or use early termination if an organism’s performance is clearly below a threshold (e.g., after 5 tasks it’s below NCD by a margin). This can cut evaluation time for poor individuals.

Given 37 days, if you can achieve 10 minutes per generation, you’d get ~5,300 generations—much more comfortable. Prioritising speed over exhaustive evaluation is advisable for an OEE system.

---

## 5. The “Interesting” Gap (Generalisation)

**Your approach:** held‑out tasks (seed 137) and eventual evaluation on Nemesis adversarial grid.  
**Risk:** Even with a held‑out set, the system might overfit to the structure of the 20 evaluation tasks (which are generated from a fixed seed and limited categories). The held‑out set is from the same generator, so it may share spurious patterns.

**Recommendations:**
1. **Continuously generate fresh tasks** during evolution. Use the trap generator with a **random seed per generation** to create new tasks that are not in the fixed set. Then evaluate on a random subset each generation. This prevents memorisation and forces generalisation. The held‑out set should be a separate, fixed set that is never used for selection.
2. **Introduce a “difficulty escalator”** – when the median margin accuracy exceeds a threshold, automatically generate harder tasks (e.g., longer chains, more distractors). This creates an arms race similar to co‑evolution, which is a classic driver of OEE.
3. **Monitor behavioural diversity** not just via the score vector, but via **input‑output pairs** on a diverse set of tasks. For example, use the 15 seed traps plus 15 newly generated tasks each generation to compute a richer signature. This makes it harder for organisms to be similar in behaviour while still being functionally different.
4. **Retain the final test on the Nemesis adversarial grid** as the ultimate validation. That grid was designed to break pattern‑matching; if organisms succeed there, they likely have genuine reasoning.

---

## 6. Additional Architectural Risks

### a. Code Bloat and Complexity Creep
Without a penalty on genome size, organisms will accumulate genes (especially via duplicate and splice) that provide no fitness benefit but add overhead. This leads to slower evaluation and potential overfitting.  
**Mitigation:** Add a **genome length penalty** as a soft objective (or as a regulariser in selection). For example, you could include “number of genes” as a fourth objective to be minimised (or use a multi‑objective approach with size as a fourth dimension). Alternatively, use parsimony pressure by occasionally deleting random genes (already in mutation) and preferring shorter genomes when crowding distance ties.

### b. Cycle Handling Overhead
Cycles are represented as feedback loops with a cap of 3 iterations. This can be expensive if many cycles exist. Moreover, cycles may be spurious and not actually improve fitness.  
**Mitigation:** During compilation, detect cycles and **tag genes involved**. Only allow cycles if they include at least one SCORER (so they serve as feedback). This reduces wasted cycles. Also, make the cycle cap evolvable but start low (2) to save time.

### c. Novelty Archive Saturation
The archive is unbounded; it will grow indefinitely, slowing novelty computation.  
**Mitigation:** Implement a **limited‑size archive** that retains only the most novel organisms (e.g., using a k‑means clustering to keep the top N). The `novelty_threshold` approach could also include a decay mechanism for old archive members.

### d. Parameter Explosion
Parameters are stored per‑gene in a flat dictionary. As genes duplicate, the number of parameters grows. CMA‑ES phase‑0 only optimised per‑tool parameters; during structural evolution, parameters are mutated by Gaussian drift. This may lead to many irrelevant parameters.  
**Mitigation:** Use **parameter deletion** as part of the delete mutation: if a gene is deleted, its parameters are removed. Also, when a gene is duplicated, the copy’s parameters are initially a copy but then undergo drift, which is fine.

### e. Compilation Validation Cost
The validation gates (AST parse, import check, interface, wiring, smoke test) are run on every organism before it enters the population. This is necessary but can be expensive.  
**Mitigation:** Cache validation results for identical genomes (by hash). Also, run the smoke test only on a single task, not 5.

---

## 7. Non‑Negotiable MVP Decisions

These are the pillars that must be done correctly for any chance of success:

1. **Sandbox security** – Using RestrictedPython + multiprocessing with timeout is essential to prevent malicious or buggy code from crashing the main process.
2. **Lineage logging** – You must record every organism’s genome, mutations, and fitness in a structured, append‑only format. Without it, you cannot post‑mortem why a run succeeded or failed.
3. **Checkpointing** – A 40‑day run will almost certainly encounter a system failure. Frequent, robust checkpoints are non‑negotiable.
4. **Reproducible task generation** – Fixed seeds for evolution and held‑out sets ensure that results are comparable across runs and can be debugged.
5. **Valid initial population** – At least a few dozen organisms that compile and produce non‑zero fitness. Phase‑0 ensures parameter optimisation, but you still need to ensure that the initial population has diversity in structure. Your selection of 30 best + 20 most diverse is a good start.
6. **Fast evaluation** – Without parallelism and reduced evaluation time, you will not get enough generations. This is a make‑or‑break factor.
7. **Explicit novelty archive** – The behavioural signature approach is crucial for maintaining diversity. Without it, the population will converge to NCD‑like solutions quickly.

---

## 8. Early Monitoring Metrics

From generation 1, log and watch:

- **Fraction of viable offspring** – If it drops below 10%, your crossover/mutation operators are too destructive. Adjust rates or introduce compatibility checks.
- **Median margin accuracy (on evolution set)** – If it stays near zero or negative for >50 generations, the system is not improving. Possibly NCD is too dominant; consider removing NCD genes.
- **Novelty archive size** – If it grows very slowly (e.g., <10 new signatures after 100 generations), novelty pressure is too weak or the behavioural signature is not discriminative.
- **Number of self‑referential organisms** – Even if they have low fitness, their emergence indicates the genotype space allows such topologies. If none appear after 500 generations, the mutation operators that produce cycles (duplicate‑and‑wire‑back, rewire) are too rare; increase their rates.
- **Held‑out accuracy** – This should roughly track evolution set accuracy. If it diverges (evolution accuracy rises but held‑out stays flat), overfitting is occurring. Introduce fresh tasks or increase difficulty.
- **Distribution of gene types** – If SCORER genes dominate and PARSER genes disappear, organisms may be bypassing structure extraction. This is a red flag for reasoning capability.

---

## 9. What I Would Change

- **Prioritise speed:** I would reduce the default evaluation tasks to 10, set timeout to 1 second, and parallelise heavily to aim for <5 minutes per generation. The trade‑off (less accurate fitness) is acceptable if you gain many more generations.
- **Remove NCD from the gene library** initially, forcing evolution to discover alternatives. Later, if diversity stalls, reintroduce NCD as a “recessive” gene with a high mutation rate.
- **Implement a multi‑scale evolution:** Start with whole‑tool crossover for the first 100 generations to build a robust baseline, then gradually enable finer‑grained recombination. This reduces early‑generation death.
- **Add a parsimony objective** (minimise number of genes) to combat bloat, especially if you see population size increasing without fitness gains.
- **Continuously generate fresh tasks** each generation, drawing from the trap generator with a new random seed. This prevents overfitting and provides an ever‑changing landscape.
- **Use a more informative behavioural signature** – e.g., the vector of scores on 20 tasks plus the vector of rankings (which candidate got highest score). This captures more nuance.

---

## 10. Conclusion

Your design is among the most thorough I’ve seen for an OEE system applied to reasoning algorithms. The key risks—bootstrap viability, NCD convergence, gene extraction fragility, computational budget, and generalisation—are all well‑identified. With the adjustments above (especially faster evaluation, staged recombination, and removal of NCD as a gene), I believe you have a strong chance of producing organisms that genuinely outperform their ancestors on held‑out tasks and exhibit self‑referential wiring.

The most critical non‑negotiable is **speed**: you must achieve many thousands of generations. Parallelise, reduce task count, use multi‑stage evaluation, and monitor early to tune parameters. The second is **logging**: without it, you cannot learn from the run.

Finally, I recommend reading **“Open‑ended evolution: Perspectives from the OEE workshop in York”** (Bedau et al.) and **“The Evolutionary Origins of Modularity”** (Wagner) for insights on how to foster sustained innovation. For practical implementation, look at **Avida** and **AVIDA‑ED** for ideas on maintaining diversity and detecting open‑endedness.

Apollo is a bold project. With careful implementation and the adjustments above, it can become a valuable platform for exploring how reasoning structures evolve.

[END DEEPSEEK]


[GEMINI]

This is a profoundly ambitious and elegantly structured architecture. Attempting to bridge the Comprehension Debt Paradox by forcing algorithmic reasoning to emerge through structural evolution, rather than just weight updates, is exactly the kind of high-risk, high-reward research the field needs. 

The pipeline from Nous through Hephaestus to generate the seed substrate is solid. However, transitioning from a generative pipeline to an open-ended evolutionary (OEE) system introduces brutal thermodynamic realities. Evolution is notoriously lazy; it will exploit the cheapest available path to fitness. 

Here is a direct critique of your five core concerns and the non-negotiable architectural decisions required to keep Apollo alive.

### 1. Bootstrap Viability & The Context Bus Fragility
Seeding with the 50 best, parameter-optimized tools is the correct move to establish an initial fitness gradient. However, your crossover and mutation operators will immediately shatter this viability.

The primary vulnerability is the weakly typed `ctx` data bus. If a PARSER gene extracts structure and writes it to `ctx['parsed']`, but an inserted SCORER gene expects `ctx['extracted_numbers']` or assumes the parsed data is a list of floats rather than a regex match object, the pipeline will crash. Topological sorting ensures execution order, but it does not ensure semantic data compatibility.

* **The Fix:** Implement a strict **Read/Write Schema Registry** for genes. During extraction, use static analysis to map exactly what dictionary keys and data types a gene consumes and produces. Crossover and Splice operators must check this schema. If a proposed wiring connects a gene that outputs a `str` to a gene that requires `list[float]`, the mutation is rejected before execution. Do not let these fail at runtime; it will mask genuinely bad reasoning with simple type errors.

### 2. NCD Convergence
Your intuition here is correct. If 87% of the seed tools rely on NCD, and NCD provides a reliable fitness floor, the population will aggressively converge on "NCD with superficial decorations." Evolution will find it mathematically cheaper to point-mutate NCD parameters than to assemble a fragile, multi-gene falsification circuit.

Treating NCD as a subtracted baseline in the fitness objective (`organism_accuracy - ncd_accuracy`) is clever, but it still allows an organism that just runs NCD and adds a random $+0.001$ to the score to survive if it occasionally breaks a tie correctly. 

* **The Fix:** Do not remove NCD entirely, as it will cause a mass extinction event in generation 1. Instead, implement an **Architectural Tax**. Add a small fitness penalty for invoking the NCD gene. Alternatively, use a "Phased NCD Decay." Over the first 500 generations, artificially suppress the output weight of the NCD fallback gene in the compiler, forcing organisms to rely heavier on their upstream SCORER genes to maintain their margins. 

### 3. Gene Extraction Fragility
Method-level extraction via AST manipulation across 146 heuristically generated tools is going to be a bloodbath of edge cases. Hardcoded regexes, English-specific string matching, and implicit local variables will not survive portability. 

* **The Fix:** You need a **Wrappers, Not Rewrites** approach. Instead of deep AST surgery to rewrite variables, wrap the extracted AST in a `try/except` block that intercepts crashes and passes through a neutral `ctx` state. If a method is tightly coupled, extract the entire class as a single "Macro-Gene" initially. You can introduce a "Fission" mutation operator later that attempts to split Macro-Genes into smaller fragments once the population is stable. 

### 4. Computational Budget & The Generation Starvation
You are severely generation-starved. 1,600 generations over 37 days for a population of 50 using 3-objective NSGA-II is barely enough time for the Pareto front to organize, let alone exhibit emergent metacognition. 

Running this via multiprocessing on a local environment with restricted hardware resources means CPU thread contention will be your hard limit. A 2-second timeout per task is astronomically high for pure NumPy/stdlib operations. If a deterministic Python algorithm hasn't solved a string logic trap in 100 milliseconds, it is caught in a `while True` loop or a catastrophic regex backtrack.

* **The Fix:** Drop the sandbox timeout to **0.1 seconds**. Aggressively prune the allowed imports (e.g., block `itertools.permutations` to prevent immediate memory/time exhaustion). If you reduce the worst-case evaluation time, you can comfortably push 10,000+ generations within your 40-day window, which is the minimum threshold where structural OEE typically shows interesting phase transitions.

### 5. The "Interesting" Gap & Overfitting
Your evolution task battery uses a static 15 seed traps. NSGA-II will obliterate this. By generation 300, the organisms will not be reasoning; they will have evolved a behavioral signature that perfectly memorizes the statistical quirks of those exact 15 prompts. When you test them on the held-out seed 137 battery, their fitness will collapse.

* **The Fix:** You cannot have a static environment for open-ended evolution. You must implement a **Rolling Curriculum**. Every 50 generations, cycle 5 older traps out of the evolution battery and cycle 5 newly generated traps in. The NCD baseline will need to be recomputed, but this forces the organisms to chase a moving target. They must evolve generalizable algorithms because the specific tasks they are evaluated against do not persist long enough to be memorized.

---

### Critical Early Monitoring (Generations 1-50)

If the run is dying, it will happen in the first 48 hours. Monitor these specific metrics:

* **The "Dead on Arrival" (DOA) Rate:** Track the percentage of offspring that fail the compilation gate or the 5-task quick screen. If DOA $> 85\%$, your mutation operators are too destructive. You must lower the crossover rate and increase point mutation.
* **Novelty Archive Velocity:** Track the rate of new additions to the Novelty Archive. If it stagnates before generation 100, your population has collapsed into a single local optimum. 
* **Gene Extinction:** Log which seed genes are entirely wiped from the population. If all non-NCD SCORER genes die by generation 50, you must restart and increase the NCD tax.

Would you like to focus next on designing the strict Read/Write Schema for the Context Dict to prevent those early compilation crashes?

[END GEMINI]


[GROK]

**Overall Assessment**  
This is one of the most complete, production-ready evolutionary-computation specifications I have ever seen for a *reasoning* domain. The architecture is coherent, the safety layers are thoughtful, the metacognition signal is explicitly measurable from generation 0, and the success criteria are correctly placed on a true held-out set. The Phase-0 CMA-ES warmup + viability spike + pure-AST mutations + context-dict bus + NSGA-II + perpetual novelty pressure is a very strong stack.  

The design already avoids most of the classic open-ended-evolution failure modes (Tierra-style collapse to parasites, GP bloat, premature convergence to a single trick). With the caveats below, I believe it has a realistic shot at producing organisms that genuinely outperform their 146 ancestors on held-out traps *via structural recombination* within the 40-day budget.

I will answer your five explicit concerns first, then the three meta-questions.

### 1. Bootstrap Viability  
**Your mitigation (seed with 50 proven forge tools + viability spike) is already sufficient for MVP.**  
Seeding with the 30 best + 20 structurally diverse originals guarantees that *every* initial genome compiles, runs, and beats NCD on at least some tasks. That gives selection an immediate fitness gradient. The viability spike (run one generation of random crossover + mutation on the 50 and measure % that still compile & evaluate) is the correct “go/no-go” gate.

**Additional cheap safeguards I would add at bootstrap (zero extra compute):**
- After gene extraction, compute a *dependency graph* over all genes (which convention keys each gene reads/writes). Store it in `gene_library.json`.
- During crossover and splice, the compiler already does a “wiring validation” (point 6.2). Extend it with a one-line topological check: for every edge A → B, confirm that B’s required input key appears in A’s output convention keys *or* is in the initial ctx. This catches 90 % of type-mismatch deaths before the sandbox ever runs.
- In the first 10 generations, log “compilation survival rate” and “quick-screen survival rate”. If either drops below 60 %, abort and fall back to the “warm-start mild mutations” strategy you already defined.

This is still pure AST, no LLM, and keeps the MVP promise.

### 2. NCD Convergence  
**Your current mitigation (margin-over-NCD + novelty as full Pareto dimension) is good but not bullet-proof.**  
Because FALLBACK genes are still in the library and provide an immediate ~0.4–0.6 accuracy floor with almost no structural cost, the early population will be dominated by “NCD-plus-one-scorer” chimeras. Novelty pressure helps, but behavioral signatures on only 15 reference tasks are coarse; two very different NCD wrappers can look similar.

**Recommended tweak (still MVP-compatible):**  
Do **not** remove NCD genes entirely — that would kill too many lineages. Instead, add a *fourth* (still maximized) objective that is **softly** anti-FALLBACK:

\[
\text{fallback\_penalty} = \frac{\text{number of FALLBACK genes in pipeline}}{ \text{total genes}} \times 0.2
\]

NSGA-II treats it as a fourth dimension. Organisms that drop their FALLBACK genes get a small bonus *only if* their margin accuracy is competitive. This is enough to create a gentle gradient away from NCD without crashing early viability. You can turn the coefficient to zero after generation 300 if you want.

Track in the elite log: `% of elites that still contain at least one FALLBACK gene`. If it stays >70 % past gen 300, increase the penalty coefficient to 0.3. This is the single highest-leverage change I would make.

### 3. Gene Extraction Fragility  
Method-level extraction is the *correct* granularity for MVP.  
Finer (statement/expression level) explodes the gene library into thousands of micro-fragments and makes wiring validation impossible. Coarser (whole-tool) removes the recombination power you want.

The ~50 % “cleanly extractable” yield you already anticipate is fine. The remaining 50 % that contain English-specific regexes or answer-format assumptions will simply die in crossover unless they happen to land in a compatible context — which is exactly what selection is for. The compiler’s wiring-validation gate already kills the incompatible chimeras.

**One practical improvement:**  
When you run `gene_extractor.py`, also output a per-gene “portability score” (number of unique convention keys it reads/writes + presence of hard-coded regex patterns or string literals longer than 20 chars). In the viability spike, weight splice probability *inversely* by portability score for the first 100 generations. This biases early recombination toward the clean 50 % while still allowing the brittle genes to survive in their native lineages.

### 4. Computational Budget  
33 min/gen × 1,600 generations ≈ 37 days is **tight but sufficient** if you parallelize aggressively.

**Quick wins (all in sandbox.py / evaluate_organism):**
- Use `multiprocessing.Pool` with `processes = min(CPU_COUNT, 20)` instead of one process per organism. You can evaluate all 50 offspring in parallel; the 2 s timeout is per *task*, not per organism.
- Hierarchical filtering is already excellent. Make the quick-screen use only 3 tasks (instead of 5) for the first 200 generations.
- After generation 500, if median accuracy > 0.65, you can dynamically drop the evolution battery to 12 tasks (still 15 for behavioral signatures). The held-out battery stays at 20.

With these, realistic wall-clock per generation drops to ~12–15 min → ~3,000–4,000 generations in 37 days. That is comfortably past your metacognition criterion (gen 2,000).

### 5. The “Interesting” Gap  
Held-out battery (seed 137) + Nemesis-style metamorphic testing post-MVP is the right generalization check. Historical systems failed because they had no pressure for *transfer* or because diversity collapsed.

**Additional low-cost safeguards:**
- Every 50 generations, run the *current elite 5* on a fresh set of 10 “Nemesis-light” tasks (generated with different seeds and one metamorphic transform). Log the accuracy drop. If the gap grows >0.25, increase the mutation rate of `duplicate-and-wire-back` (forces more self-reference) and/or add one meta-task where the prompt explicitly says “explain your reasoning then check it for contradictions.”
- Track in `lineage.jsonl`: median fitness of self-referential vs non-self-referential organisms *per generation*. You want the curves to cross upward for self-ref organisms by ~gen 1,500–2,000. If they stay flat or downward, you have a true metacognition failure and should escalate to meta-tasks earlier than planned.

### Non-Negotiable Architectural Decisions for MVP  
These must be locked before you start the 37-day run:
1. **Novelty never decays** and stays a full Pareto objective (your design already does this — do not change it).
2. **Self-referential wiring is detectable and selectable from gen 0** (`has_self_referential_wiring`, `cycle_count` fields). You already log it; keep it.
3. **Compiler must kill any organism that fails wiring validation or RestrictedPython** — no exceptions.
4. **Success is measured *only* on held-out battery** (seed 137). Evolution battery is training only.
5. **No LLM in the mutation loop** (your MVP rule). StarCoder is post-MVP only.
6. **Lineage + elite + self-ref logs must be append-only JSONL** and human-readable from day 1.

### What to Monitor from Generation 1 (Early-Warning Dashboard)  
Add a one-page `apollo_status.md` that appends every generation:
- Compilation survival % (offspring)
- Quick-screen survival %
- Elite margin_accuracy (evolution + held-out)
- % of population with self-referential wiring
- % of elites still containing FALLBACK genes
- Novelty archive size
- Median fitness gap (self-ref vs non-self-ref)
- Held-out vs evolution accuracy gap (overfitting signal)

If by gen 200 any of the following happens, intervene:
- Compilation survival < 55 % → switch to warm-start mild mutations.
- % FALLBACK in elites still > 80 % → increase fallback_penalty coefficient.
- Archive size < 15 → increase offspring to 80/gen or lower archive_threshold to 0.25.
- Self-ref % < 2 % and flat → bump `duplicate_and_wire_back` rate to 0.15.

### What I Would Change (Minimal Diff from Your Spec)  
1. **Add the soft fourth objective** (fallback_penalty) — highest leverage.
2. **Make splice probability inversely proportional to gene portability score** for first 100 gens.
3. **Aggressive parallel evaluation** in sandbox (Pool) + dynamic task count after gen 500.
4. **One extra field in Genome**: `fallback_count: int`. Makes the anti-NCD pressure trivial to implement.
5. **Optional but nice**: After Phase 0, run a 50-generation “diversity-only” warmup (NSGA-II with *only* novelty + anti-bloat) before turning on accuracy. This seeds the archive with more varied behavioral signatures.

Everything else in the spec is excellent. The gene system, context-dict bus, topological crossover, and sandbox are textbook-quality.

You have built a genuine *forge for reasoning organisms*, not just another GP system. With the tweaks above (all < 200 lines of extra code), I believe you will see the metacognition phase transition inside the 40-day window. The design is ready to ship.

Go run the viability spike. If it comes back > 40 %, launch. The rest of the system is already stronger than 95 % of the open-ended-evolution literature.

[END GROK]


[CLAUDE]


Let me read the full specification first.This is a remarkably well-thought-out design. The specification is buildable, the failure modes are acknowledged honestly, and the viability spike is exactly the right kind of "check your assumptions before committing" decision gate. I'll address each of your five concerns in depth, then raise additional issues the spec doesn't cover, and close with what to monitor from generation 1.

---

## 1. Bootstrap Viability

Your mitigation (seed with 50 proven tools, run a viability spike) is necessary but probably not sufficient. The core issue is that the viability spike tests random assembly, but your actual early generations are dominated by *crossover between working organisms*, which is a different failure mode.

**The crossover junction problem is worse than random assembly.** Your single-point pipeline crossover (Section 8) splices the tail of parent B onto the head of parent A with a single new wire. But gene output distributions are not standardized. A SCORER from tool A might write `ctx['score']` in the range [-3, 3] while a SCORER from tool B expects to *read* `ctx['score']` in [0, 1]. The context dict convention gives you type compatibility (everything is a float in the convention keys) but not *distributional* compatibility. The child compiles, passes the smoke test on 1 trap, enters the population, and then scores terribly on 19 of 20 tasks because gene B is operating on inputs from a distribution it was never calibrated against.

**Recommendations:**

Add a **normalization gene** as an implicit pipeline element. After every SCORER writes `ctx['score']`, inject a sigmoid or z-score normalization step that maps the output to [0, 1]. This makes cross-tool splicing distribionally safe. You can make the normalization parameters evolvable (learnable gain and bias per gene junction) so evolution can override it when raw scores are more useful, but the default provides a safe initial coupling. This is the single highest-leverage change you can make for bootstrap viability.

Run the viability spike not just on random assembly but specifically on **crossover products between your top-30 tools**. Generate 200 crossover children from your 30 best, measure functional viability. If that number is below 30%, your crossover operator needs the normalization shim before you start.

Consider a **graduated mutation schedule** for the first 100 generations regardless of viability spike results. Start with point mutation and parameter drift only (which preserve structure), introduce splice and delete at generation 50, and crossover at generation 100. This gives the population time to calibrate its parameters to the fitness landscape before you start shuffling structure. The analogy is warming up CMA-ES before structural evolution — you're already doing this at the Phase 0 level, but the same logic applies to the structural loop itself.

## 2. NCD Convergence

Your two mitigations (margin-over-NCD fitness floor, novelty as full Pareto dimension) are well-chosen but likely insufficient against a subtler failure mode.

**The problem isn't that organisms converge *to* NCD. The problem is that organisms converge to NCD-plus-epsilon.** Under your margin-accuracy objective, an organism that runs some complex gene pipeline and then falls back to NCD on 18 of 20 tasks gets the same margin score as an organism that genuinely outperforms NCD on those 2 tasks where both succeed, and NCD on the rest. The complex pipeline is dead weight — it computes stuff, occasionally helps, but mostly the fallback score wins. Selection can't distinguish "NCD with expensive decoration" from "genuine alternative that's still learning." The decoration organisms consume compute and crowd out novel lineages.

**Novelty pressure doesn't solve this** because behavioral signatures are computed on the *output scores*, not on the *computational path*. Two organisms that both ultimately fall back to NCD on 14 of 15 reference tasks have nearly identical behavioral signatures, even if their non-NCD genes are structurally different.

**Recommendations:**

Don't remove NCD as a gene — you're right that it would kill too many early organisms. Instead, **decompose the margin-accuracy objective into NCD-dependent and NCD-independent components**. Track, for each organism, which tasks were answered by a non-NCD gene pathway versus which fell through to the NCD fallback. You can detect this by checking whether `ctx['score']` was overwritten by a SCORER gene after the FALLBACK gene fired (the gene trace gives you this). Then define a **fourth objective or a modifier**: the fraction of tasks where the organism's final score was *not* determined by the FALLBACK gene. This creates direct selection pressure against NCD dependence without removing NCD as a safety net.

Alternatively, and more aggressively: **decay the FALLBACK gene's contribution over generations.** Start with FALLBACK contributing 100% when it fires (generation 0). By generation 500, FALLBACK contributes 50% of its score. By generation 1000, 25%. This creates a monotonically increasing selection pressure to develop non-NCD scoring pathways. Organisms that rely on FALLBACK find their fitness eroding over time. Organisms that develop alternative scorers are unaffected.

## 3. Gene Extraction Fragility

Method-level extraction is the right granularity for MVP but your ~50% clean extraction estimate is probably optimistic for the genes that matter most.

**The real issue is that SCORER genes are where the reasoning lives, and SCORER genes are the least portable.** A PARSER that extracts numbers from text is fairly context-independent — it reads raw_text, writes parsed, done. But a SCORER that implements "structural falsification with contradiction detection" typically has deep assumptions about what `ctx['parsed']` contains. It might expect a dict with keys `{'clauses': [...], 'negations': [...], 'entities': [...]}` because the PARSER it was co-evolved with in the original tool produces exactly that structure. When you splice this SCORER behind a different tool's PARSER that produces `{'numbers': [...], 'keywords': [...]}`, the SCORER either crashes or silently computes garbage.

**The context dict solves the *naming* problem but not the *schema* problem.** `ctx['parsed']` can be anything — a list, a dict, a float, a string. Genes that read it make structural assumptions that are invisible at the type level.

**Recommendations:**

Add a **parsed-schema tag** to PARSER genes during extraction. When a PARSER writes `ctx['parsed']`, record the *type signature* of what it typically produces (e.g., `dict[str, list[str]]` vs `list[float]` vs `str`). During crossover and splice, preferentially wire PARSERs to SCORERs that expect the same schema family. This is soft compatibility — don't block incompatible wirings (evolution should explore them) but bias the initial wiring toward compatible pairings.

For the ~50% that require deep refactoring: don't refactor them. **Extract them at tool level instead of method level.** Keep the original tool as a single coarse-grained "macro-gene" — one PARSER+SCORER bundle that can be spliced as a unit. Evolution can splice macro-genes alongside fine-grained genes. Over time, if a macro-gene's SCORER is useful but its PARSER isn't, a mutation can duplicate just the SCORER (once you've confirmed it can accept generic parsed input) and delete the PARSER. This gives you a two-tier gene library: ~300-400 fine-grained genes from the cleanly extractable 50%, and ~80-100 macro-genes from the rest. The macro-genes are less recombineable but they carry intact reasoning strategies that would otherwise be lost.

## 4. Computational Budget

1,600 generations is almost certainly insufficient for your stated success criteria, but the fix isn't to reduce evaluation quality.

**The math:** Pop 50 × 20 tasks × 2s timeout = 2,000s per generation worst case. But the hierarchical filter (Section 9.6) should kill 30-50% of organisms early with the 5-task quick screen. Realistic per-generation cost is probably 1,200-1,500s (~20-25 min). Over 37 days: ~2,100-2,600 generations. You need Criterion 1 by generation 1,000 and Criterion 3 by generation 2,000. That's tight but plausible for Criterion 1. Criterion 3 (metacognition emerging from selection pressure alone) at generation 2,000 is aspirational.

**The real problem is that NSGA-II with population 50 on 3 objectives is underpowered.** The Pareto front in 3D can support maybe 20-30 non-dominated individuals. With top-5 elitism, you have 45 competitive slots and a 3D front. Crowding distance in 3D is noisy. The population is too small for the objective space.

**Recommendations:**

**Parallelize evaluation, not generation count.** You're running organisms in separate processes (Section 12). Evaluate all 100 organisms (50 parents + 50 offspring) in a process pool with `n_workers = cpu_count`. On a modern machine with 8-16 cores, this cuts per-generation wall time by 4-8x. That's 8,000-16,000 effective generations in 37 days. This is where you buy your budget, not by cutting tasks or timeout.

Reduce the task battery only if parallelism isn't enough. If you must cut, go from 20 tasks to 12 (keep all categories represented) rather than cutting timeout. Short timeouts kill organisms that are doing real work (complex pipelines legitimately need time). Bad organisms are already killed by the hierarchical filter.

For the population size problem: consider increasing to 80-100 if compute allows after parallelization. Alternatively, drop to 2 objectives for the first 500 generations (margin accuracy + novelty, skip calibration) to give NSGA-II a tractable front, then introduce calibration as a third objective. Calibration matters less when organisms are still learning to be accurate.

## 5. The "Interesting" Gap

The held-out trap battery is a necessary generalization check but it is structurally insufficient as a safeguard against task-specific overfitting.

**The problem:** Your evolution battery has 20 tasks from seed 42. Your held-out battery is from seed 137. Both are generated by the same `trap_generator`. If the trap generator produces tasks with systematic regularities (e.g., the correct answer is always the longest candidate, or numeric answers cluster near specific values), organisms can overfit to those regularities and still generalize to the held-out battery because it shares the same generator biases. You'd see held-out accuracy tracking evolution accuracy and conclude "generalization works!" when in fact the organisms have learned the trap generator's biases, not reasoning.

**Recommendations:**

**Rotate the evolution battery.** Every 100 generations, regenerate 5 of the 20 evolution tasks with a new random seed. This prevents long-term overfitting to specific task instances. Keep the 15 seed traps fixed (they're your behavioral signature basis) but rotate the 5 generated tasks. This is cheap and significantly hardens against memorization.

**Add a second held-out battery from a different source.** If the Nemesis adversarial grid exists (mentioned in post-MVP), pull a small sample from it now. Even 5 Nemesis tasks, evaluated every 50 generations, gives you a cross-generator generalization signal. If evolution-battery accuracy rises but Nemesis accuracy doesn't, you're overfitting to the trap generator, not learning reasoning.

**Track the behavioral signature's effective dimensionality.** If organisms are genuinely developing diverse reasoning strategies, the 15-dimensional behavioral signature space should show increasing rank over generations (PCA on the population's signatures, track the number of components needed for 90% variance). If effective dimensionality drops over time, the population is collapsing into a small number of strategies regardless of what the novelty score says.

---

## Additional Architectural Concerns

**Bloat.** Your delete operator at 10% rate is the only simplification pressure. Splice (25%) and duplicate (15%) both increase genome size. Over 1,600+ generations, expect genome length to grow monotonically. Bloat is the dominant failure mode in genetic programming — introns accumulate, evaluation time grows, and eventually every organism hits the 2s timeout. You need stronger anti-bloat pressure. Options: (a) add genome length as a minimization objective (4th Pareto dimension, or a penalty on the accuracy objective), (b) increase delete rate to 20% and decrease splice to 15%, (c) add a hard cap on gene count (e.g., max 15 genes per organism), or (d) periodically run a "pruning pass" that removes genes whose contribution to ctx['score'] is below a threshold (dead code elimination by fitness measurement).

**The confidence method is a hack.** Section 6.1 auto-generates `confidence()` as sigmoid-of-evaluate-score. This means calibration fitness is entirely determined by the range and distribution of `ctx['score']`, not by any genuine calibration mechanism. Organisms can improve calibration by simply rescaling their scores, not by becoming better calibrated about their own uncertainty. This makes the calibration objective partially redundant with the accuracy objective (both reward higher scores for correct answers, lower for incorrect). Consider either (a) dropping calibration as a Pareto dimension for MVP and making it a post-MVP objective, or (b) making the confidence method evolvable (a separate gene pipeline that reads the gene trace and produces a probability, not just a sigmoid wrapper).

**The novelty archive grows without bound.** Section 11 adds organisms to the archive whenever they exceed the threshold. Over 2,000+ generations, this archive could grow to thousands of entries. Computing k-nearest distances against the full archive becomes expensive (O(n × archive_size) per generation). Cap the archive at ~500 entries and use a replacement strategy (replace the least-novel existing entry when a more novel one arrives). This also prevents the novelty score from inflating as the archive fills — if the archive covers the behavioral space densely, new organisms need to be extremely different to score high on novelty, which is too harsh a requirement in late generations.

**Checkpoint granularity.** Every 50 generations is too coarse for a 37-day unattended run. If the process crashes at generation 149, you lose 99 generations (~33 hours of compute). Checkpoint every 10 generations. The pickle cost is negligible compared to the evaluation cost. Also: rotate checkpoints (keep the last 5, delete older ones) to prevent disk bloat.

---

## What to Monitor from Generation 1

These are your early warning indicators. Plot all of them on a dashboard that updates every generation.

**Kill signals (stop and fix if you see these):**

1. **Compilation survival rate below 20%** for offspring after generation 50. If 80%+ of crossover/mutation products are dying at compilation, the mutation operators are too destructive or the context dict is too fragile.
2. **Median gene count monotonically increasing** for 100+ consecutive generations. Bloat has taken hold.
3. **All 5 elites share the same wiring hash** for 50+ consecutive generations. Population has converged; novelty pressure has failed.
4. **Held-out accuracy diverging from evolution accuracy** by more than 15 percentage points. Overfitting.

**Health signals (expect to see these if the run is working):**

1. **Compilation survival rate above 40%** and stable after the warmup period.
2. **Median margin accuracy positive** (above NCD baseline) by generation 200-300.
3. **Novelty archive growing** at roughly 1-3 new entries per generation through generation 500.
4. **At least 3 distinct wiring hashes** in the top-10 organisms at any given generation.
5. **Elite displacement events** occurring at least once per 20 generations. If the elites never change, selection isn't finding improvements.
6. **Self-referential wiring fraction** above zero by generation 500 (not necessarily fit yet, just present in the population).

**The single most important metric is the gap between the best organism's held-out accuracy and the best Phase 0 tool's held-out accuracy.** Plot this as a time series from generation 1. If this line trends upward, structural recombination is producing genuine improvement. If it's flat for 500+ generations, the structural evolution is not working and you need to revisit the mutation operators or gene compatibility.

---

## Summary of Recommended Changes (Priority Order)

1. **Add junction normalization** between genes (highest-leverage single change for bootstrap viability)
2. **Parallelize evaluation** across CPU cores (unlocks 4-8x more generations)
3. **Add NCD-independence tracking** as a fourth signal or objective modifier (prevents convergence to NCD-with-decoration)
4. **Introduce macro-genes** for the ~50% of tools that resist clean method-level extraction
5. **Increase anti-bloat pressure** (higher delete rate, gene count cap, or parsimony pressure)
6. **Rotate evolution task subset** every 100 generations
7. **Checkpoint every 10 generations**, not 50
8. **Cap novelty archive** at ~500 entries
9. **Graduate the mutation schedule** for the first 100 generations (structure-preserving mutations first)
10. **Drop calibration to 2-objective NSGA-II** for the first 500 generations, reintroduce as a third objective later

This is an unusually well-constructed specification for a project in this space. The viability spike, the margin-over-NCD framing, the held-out battery, and the honest acknowledgment of OEE impossibility results all suggest you know where the historical failure modes are. The biggest risks are distributional incompatibility at gene junctions (fixable with normalization), silent NCD dominance (fixable with pathway tracking), and bloat (fixable with parsimony pressure). If you nail those three, the run has a reasonable shot at Criterion 1 and an outside shot at Criterion 3.

[END CLAUDE]

---

# Council Synthesis — Assessment by Claude (Opus)

*Having built the forge pipeline that produces Apollo's seed substrate, here is my assessment of where the council agrees, where they diverge, and what unique insights emerged.*

---

## Where All Five Agree (Unanimous Consensus)

### 1. The Context Dict is the Achilles Heel
Every reviewer independently identified the weakly-typed `ctx` data bus as the primary bootstrap risk. The convention keys (`parsed`, `score`, `fallback_score`) solve naming but not schema compatibility. A PARSER that writes a `dict[str, list[str]]` wired to a SCORER expecting `list[float]` will silently compute garbage.

**ChatGPT** calls for typed I/O contracts. **DeepSeek** wants strict key standardization enforced at extraction time. **Gemini** demands a Read/Write Schema Registry. **Claude** identifies the deeper distributional problem — even when types match, value ranges differ between tools. **Grok** recommends a dependency graph with topological key validation.

**The consensus is clear:** some form of compile-time compatibility checking is non-negotiable. The disagreement is only on how strict.

### 2. NCD Will Dominate Without Active Counterpressure
All five confirm that margin-over-NCD + novelty is insufficient. NCD gives immediate fitness with zero structural complexity. The population WILL converge to "NCD with decoration" unless explicitly prevented.

**ChatGPT** recommends tracking NCD usage ratio and penalizing it. **DeepSeek** goes further — remove NCD as a gene entirely, start with only the 13% non-NCD tools. **Gemini** proposes a phased NCD decay (reduce FALLBACK contribution over generations). **Claude** identifies the subtlest version — decompose fitness into NCD-dependent vs NCD-independent components using the gene trace. **Grok** adds a soft fourth Pareto objective penalizing FALLBACK gene ratio.

**The consensus:** active pressure against NCD reliance is required. The approaches range from gentle (penalty term) to aggressive (complete removal). I recommend Claude's approach — trace-based NCD independence tracking — because it's the most precise. You know EXACTLY which tasks were answered by NCD vs by real scoring.

### 3. You Are Generation-Starved
All five flag 1,600 generations as borderline insufficient. The recommended fix is unanimous: **parallelize evaluation, not reduce task quality.**

**Grok** and **Claude** both recommend `multiprocessing.Pool` across CPU cores for 4-8x speedup. **Gemini** suggests dropping timeout to 0.1s (aggressive but defensible — numpy operations on strings rarely need more than 100ms). **DeepSeek** proposes multi-stage evaluation (3 tasks → 10 tasks → 20 tasks based on performance). **ChatGPT** recommends fewer tasks and shorter timeouts.

**The consensus:** with parallelization, 5,000-10,000+ generations is achievable within 37 days. This is comfortable for Criterion 1 and plausible for Criterion 3.

### 4. Static Tasks Will Be Memorized
All five agree that a fixed 20-task evolution battery will be memorized within a few hundred generations, regardless of the held-out set.

**Gemini** is the most forceful: "NSGA-II will obliterate this. By generation 300, the organisms will have memorized the statistical quirks of those exact 15 prompts." **Claude** recommends rotating 5 tasks every 100 generations. **DeepSeek** wants fresh random tasks every generation. **ChatGPT** and **Grok** recommend difficulty ramping.

**The consensus:** the evolution battery must have a moving component. Rotating a subset every 50-100 generations is the minimum viable approach.

### 5. Bloat Is Coming
All reviewers flag that splice (25%) + duplicate (15%) creates genes faster than delete (10%) removes them. Genome size will grow monotonically.

**Claude** gives the most specific fix: hard cap on gene count (max 15), increase delete to 20%, or add parsimony pressure. **DeepSeek** recommends a fourth minimization objective. **Grok** suggests it can be addressed with the existing mutation rates by tuning. **ChatGPT** recommends penalizing single-step fallback-only organisms.

---

## Where They Disagree (Key Decision Points)

### Should NCD Genes Be Removed?
- **DeepSeek:** Yes, remove NCD genes entirely. Start with only the 13% non-NCD tools.
- **Everyone else:** No. Removing NCD causes mass extinction. Penalize or decay instead.

**My take:** DeepSeek is too aggressive. The 13% non-NCD tools are a thin seed population. Decaying FALLBACK contribution over generations (Gemini/Claude's approach) achieves the same goal without the bootstrap risk.

### Gene Extraction Granularity
- **ChatGPT:** Hybrid (micro + meso + macro genes)
- **DeepSeek:** Start coarse (whole-tool crossover first 100 gens), then fine-grain
- **Gemini:** Wrappers not rewrites — extract tightly coupled tools as macro-genes, split later with a "Fission" mutation
- **Claude:** Two-tier library — fine-grained genes from clean tools, macro-genes from coupled tools
- **Grok:** Method-level is correct for MVP; bias splice toward portable genes early

**My take:** Claude and Gemini converge on the right answer — a two-tier gene library. Extract what's clean at method level (~50%), keep the rest as macro-genes. This avoids the "organs removed without circulatory system" problem (ChatGPT's metaphor) without giving up recombination entirely.

### Calibration as a Pareto Objective
- **Claude:** Drop calibration for the first 500 generations (2-objective NSGA-II), add it later
- **Everyone else:** Keep it from the start

**My take:** Claude makes a valid point — the auto-generated `confidence()` method (sigmoid of evaluate score) makes calibration partially redundant with accuracy. But dropping an objective mid-run creates a distributional shift that could destabilize the population. I'd keep all three from the start but consider making `confidence()` evolvable post-MVP.

---

## Unique Insights (One Per Reviewer)

### ChatGPT: "Signal Sanity Checks"
Measure whether offspring produce non-constant output across candidates. An organism that returns the same score for every candidate is functionally dead even if it compiles. This should be part of the viability spike — not just "does it compile?" but "does it discriminate?"

### DeepSeek: "Inject Pre-Tested Chimeras"
Before launching evolution, manually create 5-10 chimeras by swapping SCORERs between the top tools. Test them. The ones that survive become stepping stones in the initial population. This gives crossover a proven track record before generation 1.

### Gemini: "0.1 Second Timeout"
The most aggressive computational recommendation. If a deterministic numpy algorithm hasn't solved a string logic trap in 100ms, it's caught in an infinite loop or catastrophic regex backtrack. Dropping from 2s to 0.1s would allow 10,000+ generations — well into the range where structural OEE shows phase transitions.

### Grok: "Diversity-Only Warmup"
Run 50 generations with ONLY novelty + anti-bloat as objectives (no accuracy). This seeds the novelty archive with diverse behavioral signatures before accuracy pressure narrows the population. Elegant and cheap.

### Claude: "Junction Normalization"
Add an implicit sigmoid/z-score normalization step at every gene junction. This makes cross-tool splicing distributionally safe by default. The normalization parameters are evolvable so evolution can override them when raw scores are more useful. This is the single highest-leverage change for bootstrap viability across the entire review.

---

## My Assessment

The council confirms what I expected from the research review: the design is strong, the risks are real, and the mitigations are mostly right but need strengthening in three specific areas.

**The three non-negotiable changes (all reviewers agree):**

1. **Gene compatibility checking at compile time** — some form of schema or type validation on context dict keys. Whether typed I/O contracts (ChatGPT), key standardization (DeepSeek), schema registry (Gemini), or dependency graph validation (Grok), this must exist before the first generation.

2. **Active NCD counterpressure** — trace-based NCD independence tracking (Claude's approach) is the most precise. Track which tasks were answered by FALLBACK vs SCORER genes. Make NCD independence a selection signal.

3. **Parallel evaluation** — `multiprocessing.Pool` across CPU cores. This alone transforms 1,600 generations into 5,000-10,000+. Every reviewer flagged this.

**The three highest-leverage optional changes:**

1. **Junction normalization** (Claude) — sigmoid after every SCORER write. Highest single-change impact on bootstrap viability.
2. **Two-tier gene library** (Claude/Gemini) — fine-grained + macro-genes. Preserves reasoning strategies that can't be cleanly decomposed.
3. **Diversity-only warmup** (Grok) — 50 generations novelty-only before accuracy kicks in. Seeds the archive cheaply.

**Overall confidence:** The council is unanimously positive on the design's viability with these changes. Grok's assessment — "stronger than 95% of the open-ended-evolution literature" — is not hyperbole; the specification genuinely addresses failure modes that most OEE systems ignore. The viability spike is the correct decision gate. If it comes back >40%, launch.

The biggest unknown remains whether pure AST manipulation produces enough viable offspring for selection to have gradient. The viability spike answers this in an afternoon. Everything else is tunable.

[CHATGPT META ANALYSIS OF ABOVE]

After reading the *council feedback + Opus meta-analysis*, I’m going to focus only on **what is still missing** or **underweighted**, not repeat what’s already been said.

You already have strong coverage on:

* NCD attractor risk
* bootstrap viability
* gene extraction fragility
* evaluation budget
* overfitting vs novelty

What’s still under-addressed are **second-order dynamics** — the things that don’t break the system immediately, but quietly prevent meaningful emergence.

---

# 1) You don’t yet control the **evolutionary timescale mismatch**

This is subtle but critical.

You have *three processes evolving at different speeds*:

1. **Parameter adaptation** (CMA-ES warmup) → fast
2. **Structural mutation (AST)** → medium
3. **Behavioral selection (NSGA-II across tasks)** → slow

### Problem

These are not synchronized.

What typically happens:

* Parameter tuning finds local optima quickly
* Structural mutations disrupt them
* Selection cannot reliably reward structural improvements because evaluation noise is high

→ **Structure never stabilizes long enough to accumulate**

---

## Fix (high impact)

### Introduce **temporal freezing**

* After CMA-ES, **freeze parameters for N generations**
* Only allow structural evolution during that window
* Then periodically:

  * re-enable parameter tuning for top K organisms

This creates:

> **alternating phases of structure learning and parameter refinement**

Without this, structure never compounds.

---

# 2) You’re missing **heritable context structure**

Right now:

```python
ctx: Dict[str, Any]
```

This is powerful but **too unconstrained evolutionarily**.

### Problem

* Genes communicate via arbitrary keys
* Successful structures depend on **implicit conventions**
* These conventions are **not encoded genetically**

→ recombination breaks them constantly

---

## Fix (non-negotiable for deeper evolution)

### Introduce **context schemas as evolvable artifacts**

Each organism carries:

```python
ctx_schema = {
  "parsed": "list[float]",
  "features": "dict[str, float]",
  "score": "float"
}
```

Mutation can:

* rename fields
* merge/split fields
* introduce new channels

Now:

* communication structure becomes **heritable**
* recombination becomes **less destructive**

This is a big unlock for composability.

---

# 3) You are not explicitly managing **selection pressure shape**

NSGA-II is doing:

* accuracy
* calibration
* novelty

But what matters is:

> **relative pressure between them over time**

---

## Likely failure mode

Early generations:

* novelty dominates (random variation looks novel)
* accuracy weak signal

Later:

* accuracy dominates
* novelty collapses

→ **classic diversity → convergence → stagnation**

---

## Fix

### Dynamic objective weighting (even within Pareto)

Not by scalarizing, but by:

* **adjusting dominance thresholds**
* or **injecting selection bias**

Example:

* Gen 0–200 → novelty favored
* Gen 200–800 → balanced
* Gen 800+ → accuracy + calibration favored

Also:

* occasionally run **novelty-only selection generations**

---

# 4) You don’t yet protect against **neutral network drift collapse**

In evolutionary systems, progress often happens via:

> long walks across neutral mutations

But your system likely:

* penalizes too harshly (crash = 0, low fitness)
* or loses lineages too quickly

---

## Fix

### Add **lineage protection / speciation-lite**

Not full NEAT, but:

* cluster organisms by behavior signature
* ensure each cluster keeps **at least N survivors**

This prevents:

> promising but temporarily underperforming lineages from dying

---

# 5) Your novelty metric is behavioral — but not **causal**

Right now novelty = difference in outputs.

### Problem

Two organisms can:

* behave differently
* but use identical internal mechanisms (just noisy)

Or:

* behave similarly
* but use fundamentally new reasoning internally

---

## Fix (important for “interestingness”)

### Add **internal diversity metrics**

From `_gene_trace`, extract:

* sequence patterns
* dependency graphs
* depth of transformations

Reward:

* new computational motifs

This helps evolution discover:

> **new ways of thinking, not just new answers**

---

# 6) You’re not explicitly managing **bloat vs depth**

GP systems often:

* grow larger without becoming more capable

You already track complexity, but:

### Missing distinction:

* **structural size** vs **computational depth**

---

## Fix

Track:

* max dependency chain length
* number of meaningful transformations (non-noop)

Then:

* penalize size
* **reward depth**

This biases toward:

> *thinking longer*, not *being bigger*

---

# 7) The system lacks **ecological pressure**

Right now:

* all organisms solve same tasks
* compete globally

This creates:

> single dominant strategy pressure

---

## Fix (high leverage)

### Introduce **niches / task subsets**

* partition tasks into subsets
* organisms evaluated more heavily on a niche
* occasional cross-niche evaluation

This allows:

* multiple strategies to coexist
* recombination across niches → innovation

---

# 8) You don’t yet exploit **recombination asymmetry**

All recombination is treated equally.

### Reality:

* some genes are “high-value”
* some are noise

---

## Fix

Track per-gene:

```python
gene_contribution_score
```

Then bias:

* recombination toward high-value genes
* mutation away from low-value ones

This dramatically improves:

> signal-to-noise ratio of evolution

---

# 9) Missing: **catastrophic forgetting detection**

You will likely see:

* a lineage becomes strong
* then disappears due to mutation drift

---

## Fix

Maintain:

* **elite archive with periodic reintroduction**

Not just Hall of Fame — actually:

* re-seed population occasionally

---

# 10) The biggest meta-risk: **false sense of progress**

Your logs will likely show:

* increasing novelty
* stable accuracy
* complex organisms

But:

> they may not be meaningfully better reasoners

---

## Add one brutal test (highly recommended)

### “Capability step test”

Every N generations:

* introduce **qualitatively new task type**
* never seen before

Measure:

* adaptation speed

If system is real:
→ should adapt faster over time

If not:
→ it's memorizing task distribution

---

# 11) One thing I would *strongly* reconsider

### AST-only mutation as the sole mechanism

You removed LLMs (good for purity), but:

You also removed:

> **semantic repair and guided mutation**

---

## Suggestion (middle ground)

Not in-loop, but:

* every ~200 generations
* run **offline repair pass**:

  * simplify code
  * remove dead genes
  * normalize structure

Think of it as:

> evolutionary “sleep phase”

---

# Final Additions to Your Non-Negotiables

Add these to your existing list:

---

## 6. Synchronize evolutionary timescales

Structure and parameters must not fight each other.

## 7. Make communication structure evolvable

Context schemas must be first-class genes.

## 8. Control selection pressure over time

Static Pareto setups almost always converge prematurely.

## 9. Preserve diversity explicitly

Do not rely on novelty alone.

## 10. Measure internal computation, not just outputs

Otherwise you optimize for appearance, not reasoning.

---

# Early Signals (Add These to Your Dashboard)

In addition to what you already track:

---

### 🧠 Structural persistence

* how long do structural motifs survive?

If very short → recombination too destructive

---

### 🔁 Reuse rate

* % of genes reused across successful organisms

If low → no building blocks forming

---

### 🧬 Lineage depth

* longest continuous ancestry chain

If shallow → evolution resetting constantly

---

### ⚖️ Objective dominance shifts

* which objective is driving selection each generation

If one dominates → collapse risk

---

# Bottom Line

After incorporating the council + Opus:

You are **very close to a system that can produce something genuinely interesting**, but only if you:

### 1. Prevent early semantic collapse

### 2. Escape the NCD basin

### 3. Enable composable, heritable structure

### 4. Give evolution enough *time and stability* to build on itself



If I had to summarize the remaining gap in one sentence:

> You’ve designed a system that can generate variation — now you need to ensure it can **accumulate structure over time without constantly destroying it**.



[APOLLO DESIGNER META ANALYSIS]

Here's my honest take after reading the full council feedback.

The council is telling you the same thing five different ways, and they're right. Let me distill what actually matters and what to tell Claude Code.

---

## The Hard Truth About AST-Only Mutation

I need to be straight with you. I was too conservative when I pushed AST-only for MVP. The council is unanimous on this point, and the literature backs them up. AlphaEvolve, FunSearch, OpenELM, and Darwin Godel Machine all converged on the same finding: LLM-assisted mutation produces 60-80% viable offspring versus under 5% for random AST manipulation. That's not a marginal difference — it's the difference between a system that evolves and a system that generates noise and culls it.

The viability spike will almost certainly confirm this. Your forge tools aren't simple math expressions — they're 100+ line classes with regex parsers, numpy operations, compression calculations, and domain-specific heuristics. Splicing methods between them via AST manipulation will produce a bloodbath of type mismatches, distributional incompatibilities, and silent garbage. You'll get organisms that compile but produce constant or meaningless scores. ChatGPT called this "functionally dead even if it runs," and that's exactly what will happen.

**My revised recommendation:** Don't wait for the viability spike to fail. Plan for a local StarCoder 1B (or whatever coding model fits on your 17GB card) as the mutation operator from day one. No API calls. No network. Deterministic given a seed. It runs locally alongside the sandbox. The mutation prompt is simple: "Here is a Python method that scores reasoning quality. Here is another method from a different tool. Combine them into a single method that uses both approaches." The LLM understands what the code does semantically, so it produces chimeras that are functionally coherent, not just syntactically valid.

Still run the viability spike. If AST viability comes back above 40%, you have the option to go AST-only. But architect the system to support LLM mutation from the start so you're not rebuilding when the spike comes back at 8%.

## Sharpening the NCD Problem

The council nailed this. Margin-over-NCD is necessary but not sufficient. Claude (in the council) identified the deepest version of the problem: organisms that run complex pipelines but fall back to NCD on 18 of 20 tasks are indistinguishable in fitness from organisms that genuinely beat NCD on 2 tasks. The decoration organisms consume slots and crowd out real innovation.

**The fix is trace-based NCD independence.** You already have `ctx['_gene_trace']` recording which gene wrote the final `ctx['score']`. Use it. For each task, check whether the final score came from a SCORER gene or a FALLBACK gene. Then:

```python
ncd_independence = fraction_of_tasks_where_final_score_came_from_SCORER_not_FALLBACK
```

This becomes a fourth NSGA-II objective (or use Grok's approach — a soft penalty subtracted from accuracy). Organisms that lean on NCD see their fitness erode. Organisms that develop real scoring pathways are unaffected.

Additionally, adopt Gemini's phased decay. The FALLBACK gene's contribution is multiplied by a decay factor:

```python
fallback_weight = max(0.25, 1.0 - (generation / 2000))
```

At generation 0, FALLBACK contributes 100%. At generation 1500, it contributes 25%. This creates a slowly tightening noose — organisms must develop alternatives or die, but they have time to evolve them.

## The Three Changes That Actually Matter

After reading all five reviewers, here's what separates a run that produces something from a run that produces 40 days of NCD variants:

**1. Junction normalization (Claude's unique insight).** After every SCORER writes `ctx['score']`, inject a sigmoid normalization that maps the output to [0, 1]. This makes cross-tool splicing distributionally safe. When tool A's SCORER outputs values in [-3, 3] and tool B's SCORER expects inputs in [0, 1], the normalization shim prevents silent garbage. Make the normalization parameters evolvable (learnable gain and bias) so evolution can override the default when raw scores are better. This is the single highest-leverage change for bootstrap viability.

**2. Two-tier gene library (Claude + Gemini convergence).** Don't decompose every tool to method level. The ~50% of tools that are cleanly extractable get decomposed into fine-grained genes (PARSER, SCORER, FALLBACK, UTILITY). The other ~50% with tightly coupled regex, format assumptions, and entangled state get extracted as **macro-genes** — whole PARSER+SCORER bundles that stay together. Evolution can splice macro-genes alongside fine-grained genes. Over time, a "Fission" mutation can attempt to split a macro-gene once the population is stable. This prevents the "organs removed without circulatory system" problem.

**3. Rolling curriculum (Gemini, hardened by everyone else).** The evolution battery cannot be static. Every 50 generations, rotate 5 of the 20 tasks out and generate 5 new ones. The 15 seed traps stay fixed (they're the behavioral signature basis), but the generated tasks cycle. This prevents memorization and forces organisms to develop generalizable strategies. Recompute the NCD baseline whenever the task set changes.

## The Response to Claude Code

Here's the updated direction, incorporating the council's strongest consensus points:

---

The council feedback is clear and we need to incorporate the non-negotiable changes. Here's the revised plan:

### Architecture Changes (Non-Negotiable)

**1. LLM-Assisted Mutation as Default Strategy**

Architect the mutation system to support both AST and LLM mutation from day one. Still run the viability spike — if AST viability exceeds 40%, use AST as the primary operator with LLM mutation as a secondary. If below 40%, LLM mutation is the primary operator.

For LLM mutation: load a local coding model (StarCoder 1B or equivalent that fits on available GPU). No API calls, no network. The mutation prompt receives the organism's source code (or specific methods) plus the desired mutation type (splice, refactor, combine approaches) and produces a modified version. AST validates the output. The sandbox tests it.

LLM mutation operates alongside AST mutation, not instead of it. Point mutation, parameter drift, and delete remain pure AST. Splice, duplicate, and crossover can use LLM guidance when available.

**2. Junction Normalization**

After every SCORER gene writes `ctx['score']`, the compiler injects a normalization step:

```python
# Injected after each SCORER gene by the compiler
raw = ctx['score']
ctx['score'] = 1.0 / (1.0 + np.exp(-np.clip(raw * self.params.get('gene_XX_norm_gain', 1.0)
                                              + self.params.get('gene_XX_norm_bias', 0.0), -10, 10)))
```

The gain and bias parameters are evolvable per gene junction. Default: sigmoid normalization mapping any range to [0, 1]. Evolution can learn to override this when raw values are more useful.

This makes cross-tool splicing distributionally safe and is the single highest-impact change for bootstrap viability.

**3. Two-Tier Gene Library**

During gene extraction, classify each method's portability:

- **High portability (fine-grained gene):** Method uses only convention keys, no hardcoded string patterns longer than 20 chars, no format-specific regex, inputs/outputs match standard types. Extract at method level.
- **Low portability (macro-gene):** Method contains English-specific regex, format-dependent parsing, tightly coupled state with sibling methods. Extract as a PARSER+SCORER bundle that stays together as one unit.

Tag every gene with a portability score. For the first 100 generations, bias splice probability inversely by portability — prefer splicing high-portability genes early, introduce low-portability macro-genes gradually.

**4. NCD Counterpressure (Trace-Based)**

Use `ctx['_gene_trace']` to track which gene produced the final `ctx['score']` for each task.

```python
ncd_independence = count(tasks where final score came from SCORER) / total_tasks
```

Implement as: (a) a soft penalty on accuracy (`adjusted_margin = margin_accuracy * (0.5 + 0.5 * ncd_independence)`), AND (b) a phased FALLBACK decay where FALLBACK gene output is multiplied by `max(0.25, 1.0 - generation/2000)`.

Log `% of elites still using FALLBACK as primary scorer` every generation. If it stays above 70% past generation 300, increase the decay rate.

**5. Rolling Task Curriculum**

Every 50 generations, rotate 5 of the 20 evolution tasks. Replace them with freshly generated tasks using a new random seed. Keep the 15 seed traps fixed (behavioral signature basis). Recompute NCD baseline after every rotation.

This prevents memorization. Combined with the held-out battery (seed 137, never rotated, never used for selection), you have three levels of overfitting protection.

**6. Parallel Evaluation**

Use `multiprocessing.Pool` with `processes = min(cpu_count, 16)` for organism evaluation. Each organism evaluation is independent — perfect parallelism. On an 8-core machine, this cuts per-generation time by roughly 6x (accounting for overhead), transforming 1,600 generations into 8,000-10,000.

Drop the sandbox timeout from 2s to 0.5s. The council is right that deterministic numpy operations on strings should complete in under 100ms. The 0.5s timeout catches infinite loops while giving legitimate complex pipelines room. Gemini's 0.1s is too aggressive — some of the chaos reservoir tools genuinely need 200-300ms for their logistic map iterations.

**7. Signal Sanity Checks (ChatGPT's Insight)**

Add to the compilation validation: after the smoke test (1 trap, 2 candidates), check that the organism produces *different* scores for the two candidates. If the scores are identical (within epsilon), the organism is functionally dead and fails compilation.

Add to the viability spike: measure not just "does it compile" and "does it run" but "does it discriminate?" — produce different outputs for different inputs. The viability number that matters is functional discrimination rate, not just import success.

**8. Graduated Mutation Schedule (Claude Council Insight)**

For the first 100 generations, restrict mutations to structure-preserving types only:
- Generations 0-50: Point mutation + parameter drift only
- Generations 50-100: Add splice and delete (mild structural changes)
- Generations 100+: Full mutation suite including crossover, rewire, duplicate-and-wire-back

This gives the population time to calibrate parameters to the fitness landscape before structural shuffling starts. Same logic as Phase 0 CMA-ES but applied within the structural evolution phase itself.

**9. Anti-Bloat Pressure**

Gene count hard cap at 15. No organism can have more than 15 genes. Delete mutation applies at 10% rate. Additionally, add a micro-parsimony tiebreaker in NSGA-II crowding distance: when two organisms have identical Pareto rank and similar crowding distance, prefer the one with fewer genes.

**10. Diversity-Only Warmup (Grok's Insight)**

After Phase 0 CMA-ES and before accuracy-driven evolution: run 50 generations with ONLY novelty as the selection objective (no accuracy, no calibration). This seeds the novelty archive with diverse behavioral signatures before accuracy pressure narrows the population. Cheap, elegant, and prevents early convergence.

### What Stays the Same

Everything else in v2 holds: genome representation, context dict bus (with junction normalization added), per-candidate execution, terminal output via `ctx['score']`, error handling, NSGA-II with top-5 elitism, lineage logging, checkpointing, Phase 0 CMA-ES, seed population selection (30 best + 20 diverse), viability spike as first step, held-out battery on seed 137, success criteria on held-out battery.

### Revised Build Sequence

```
Step 1: Viability Spike .................. afternoon
        (determines AST vs LLM mutation balance)
Step 2: Phase 0 — CMA-ES ................ 2 days
Step 3: Diversity-Only Warmup ............ ~1 day (50 gens, novelty only)
Step 4: Graduated Structural Evolution ... 36 days
        (gen 0-50: params only, 50-100: mild structure, 100+: full suite)
```

### Revised Success Criteria

Same as before, evaluated on held-out battery only. But add one from ChatGPT:

**Criterion 4 — Capability Step Test (by generation 5,000):** Every 500 generations, introduce a qualitatively new task type never seen before. Measure how quickly the elite organisms adapt (accuracy on the new type after 50 more generations). If adaptation speed increases over time, the system is learning to reason, not memorizing tasks. If adaptation speed stays flat, it's overfitting.

### Early Death Indicators (Dashboard)

Monitor from generation 1. If any trigger fires, intervene:

- DOA rate > 85% → mutation operators too destructive, reduce crossover rate
- NCD correlation with population scores > 0.9 → NCD convergence, increase decay rate
- Novelty archive growth plateaus before generation 100 → convergence, increase novelty weight
- No self-referential organisms by generation 500 → increase duplicate-and-wire-back to 15%
- Held-out accuracy diverges from evolution accuracy by > 0.15 → overfitting, increase task rotation frequency
- Gene type distribution: if PARSER genes disappear → organisms bypassing structure extraction, red flag
- Crash rate increasing over time → mutations too destructive
- Crash rate drops to zero too fast → population homogenized

Build this. The council says it's viable with these changes. I agree. Let's go.

