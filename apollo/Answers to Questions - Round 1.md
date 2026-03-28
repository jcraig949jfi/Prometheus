

Good analysis. The compute budget question is the right thing to flag first because it constrains everything. Let's address that and then the other questions, all through the lens of MVP — but an MVP that has the seed of metacognition in its grammar from day one.

## Compute Budget: Path Forward

Option 2 — smaller population, more generations. For MVP we don't need 200 organisms and 100 tasks. We need to prove that evolution produces something more capable than the seed tools, and that self-referential wiring emerges under selection pressure.

**MVP parameters:**

Population size 50. Eval tasks 20 (the 15 seed traps plus 5 generated). Sandbox timeout 2 seconds — these are numpy-only tools doing regex and arithmetic, not training neural networks. Most evaluations should complete in under 0.1 seconds. The 2-second timeout is a safety net for degenerate loops, especially organisms that evolve self-referential gene wiring.

At 0.1s average per evaluation: 50 organisms × 20 tasks = 1,000 evaluations × 0.1s = 100 seconds per generation. That's roughly 860 generations per day, 34,000+ in 40 days. Plenty.

Add the hierarchical filtering suggestion — 5 quick-screen tasks first, kill broken organisms before full eval. This probably halves actual compute since recombination produces a lot of non-viable chimeras early on.

Save the island model, full parallelism, and 200-population runs for after MVP proves the concept works. Don't engineer for scale before you've confirmed there's something worth scaling.

## Ground Truth for Synthetic Tasks

Purely algorithmic. No API calls, no oracle. For MVP, the task universe is:

Numeric comparison (deterministic), arithmetic word problems (computable), transitive chains (deterministic at any depth), logical evaluation with negation and quantifiers (deterministic), conditional reasoning — modus ponens, modus tollens, affirming the consequent (deterministic).

These are all tasks where ground truth is a pure function of the input. The existing trap generator in `trap_generator.py` already covers most of these categories. Apollo should import and extend it, not rebuild it.

Phase 4-5 tasks (meta-tasks, hypothesis generation) are post-MVP. Don't build them yet. The escalator for MVP is just increasing chain depth and distractor count on the existing task types.

## Gene Granularity: Selection Unit

Option (b) — individual methods within the class. Here's why:

Option (a) — whole class selection — is just the current forge with recombination. You're not getting novel compositions, you're shuffling monoliths. Option (c) — sub-method blocks — is too fine-grained. You'll spend all your time on compilation failures and semantic garbage.

Methods are the natural unit. `_extract_numbers()`, `_compute_ncd()`, `_parse_structure()`, `_score_candidate()` — these are the actual functional components. Each method has a clear signature (inputs and outputs), a clear purpose, and can be meaningfully swapped between organisms.

For MVP, the gene types are:

- **PARSER methods** — take raw text, return structured representation
- **SCORER methods** — take structured representation, return float
- **FALLBACK methods** — NCD and similar baseline scorers
- **CONFIDENCE methods** — take scores, return calibrated confidence

That's four gene types. Don't add MONITOR or FALSIFIER as explicit types yet. **But — and this is the critical architectural decision — the genome representation must allow any gene to wire its input to any other gene's output, including genes of the same type.** A SCORER wired to the output of another SCORER is a self-checking loop. A PARSER wired to a SCORER's output is an organism trying to structurally decompose its own scoring. These combinations sound weird. Most will be garbage. But the ones that work are the path to metacognition, and they can only emerge if the wiring grammar permits them.

## Self-Referential Wiring: The One Non-Negotiable

This is what separates a tire-kicker from a metacognition incubator. The genome wiring specification must allow:

**Forward self-reference** — Gene B takes Gene A's output as input AND Gene A's output also feeds the final score. Gene B is checking Gene A's work. This is the simplest metacognitive pattern and should be representable from generation zero.

**Bounded cycles** — Gene A feeds Gene B feeds Gene A, capped at 3 iterations. Make the iteration cap an evolvable parameter in range 1-5, default 3. This allows iterative refinement loops to emerge — an organism that scores, re-evaluates, re-scores, and converges.

**Duplicate-and-diverge** — When gene duplication creates two copies of the same SCORER and mutation modifies one copy's parameters, you get an organism with two slightly different scoring perspectives on the same input. If an INTEGRATOR or CONFIDENCE gene downstream learns to compare them, that's the beginning of uncertainty detection — "my two internal evaluations disagree, so my confidence should be low."

The implementation is straightforward. The wiring specification is a directed graph over gene IDs. Cycles are legal but execution follows a topological sort with cycle-breaking at the iteration cap. If an organism's wiring graph has no valid execution order even with cycle-breaking, it fails compilation and dies.

**What to watch for in the logs:** Track how many organisms in each generation have self-referential wiring (any gene whose input traces back to its own output through any path). If this number stays at zero for 500+ generations, novelty pressure needs to increase or the mutation rates for duplication and rewiring need to go up. If the number increases AND those organisms have higher fitness than non-self-referential ones, that's the phase transition. That's metacognition emerging from selection pressure.

## Semantic Incoherence

Let selection handle it. This is the correct answer for evolutionary systems. If you build semantic compatibility constraints, you're encoding your assumptions about what combinations should work. The whole point of Apollo is to find combinations you wouldn't predict. Most incoherent splices will produce garbage and die immediately. That's fine — that's what selection is for. The rare incoherent splice that accidentally works is a discovery.

For MVP, the only compatibility constraint should be type-level: outputs must be type-compatible with downstream inputs. Don't go deeper than that. Let the wiring grammar be permissive and let selection be the judge.

## AST Manipulation

Yes, use `ast` from stdlib. Not LibCST yet — that's an optimization for later. For MVP:

`ast.parse()` validates every compiled organism. Gene extraction is `ast.parse()` on each forge tool, walk the tree, extract method definitions as AST nodes. Recombination is AST node replacement — swap one method's AST subtree for another's. This eliminates syntax errors from string manipulation, which would otherwise kill the majority of offspring.

This is the single highest-impact implementation decision. Get this right and the viable offspring rate goes from maybe 10% (string manipulation) to 80%+ (AST manipulation). That's an 8x speedup in effective evolution.

## Warm Start

Yes. Seed the population with the 50 best forge tools (by trap battery score), not random assemblies. Add 0 random organisms at start. Let mutation and recombination produce novelty from proven survivors. Starting from random assemblies wastes hundreds of generations rediscovering what the forge already found.

## The MVP Spec

Here's what Apollo v0.1 needs to prove the concept:

**Build:**
- Gene extractor using `ast` — parse forge tools into method-level genes typed as PARSER/SCORER/FALLBACK/CONFIDENCE
- Genome representation with a **directed wiring graph** that allows forward references, bounded cycles (cap 1-5, evolvable, default 3), and self-referential paths. This is non-negotiable — it's what makes this a metacognition incubator rather than a better forge.
- Genome compiler — assemble genes back into valid ReasoningTool classes using AST manipulation. Execution follows topological sort with cycle-breaking at iteration cap.
- 4 mutation operators: point mutate (tweak parameters), splice (insert gene from library), **duplicate** (copy a gene with mutated parameters — enables self-checking patterns), **rewire** (change one connection in the wiring graph — enables self-referential topology)
- 1 crossover operator: pipeline crossover (front half of parent A's wiring graph, back half of parent B's)
- Fitness evaluation: accuracy + calibration on 20 tasks. Two dimensions, not six. Use pymoo for NSGA-II (not III — two objectives don't need reference points)
- Novelty: simple behavioral signature (score vector on 15 seed traps), archive with k-nearest distance. Use the basic implementation, not pyribs yet
- Sandbox: RestrictedPython + 2-second timeout via multiprocessing
- Population: 50 organisms, 50 offspring per generation
- Logging: append-only JSONL with genome ID, parent IDs, fitness scores, alive/dead status, **wiring graph hash, boolean flag for self-referential wiring, cycle count if any**
- Checkpointing: pickle the population every 50 generations

**Don't build yet:**
- Speciation (post-MVP — watch for it manually in the logs, log everything, we'll use these for analysis)
- Island model (post-MVP — single population is fine for proving concept)
- Task escalation beyond depth/distractor scaling on existing types
- MAP-Elites (post-MVP — add when we have more fitness dimensions)
- Coevolutionary parasites (post-MVP)
- Reports and deep analysis (post-MVP — JSONL logs are enough)
- geppy (evaluate after MVP — stdlib ast may be sufficient)
- phylotrackpy (post-MVP — flat JSONL lineage is enough to start)
- Explicit MONITOR, FALSIFIER, or METACOGNITIVE gene types (let these roles emerge from the four basic types through duplication and rewiring)

**Success criteria for MVP (revised):**

**Criterion 1 — Evolution works:** After 1,000 generations, at least one evolved organism scores higher on the 15 seed traps than the best forge tool (IBAI v2 at 67% accuracy). If this happens, evolutionary recombination of forge tools produces genuine improvement.

**Criterion 2 — Diversity holds:** The novelty archive contains at least 30 behaviorally distinct organisms by generation 500. If the archive is small, the population has converged and novelty pressure needs to increase.

**Criterion 3 — The metacognition signal:** By generation 2,000, at least 10% of surviving organisms have self-referential wiring (any gene whose input traces back through its own output). AND those organisms have equal or higher median fitness than non-self-referential organisms. This is the big one. If self-referential organisms emerge AND they're fit, evolution has discovered that self-checking pays off. That's the phase transition.

If criterion 3 fails — self-referential organisms never emerge, or they emerge but are always less fit — that tells us something important too. It means the current fitness environment doesn't reward metacognition, and we need to add tasks where self-checking is the difference between correct and incorrect (the meta-tasks from the original Phase 4).

Build this. Get it running. Let it cook for 48 hours. Then we look at the data and decide what to add.

One more thing — on the component stack, start with pymoo and RestrictedPython only as external dependencies. Everything else is stdlib + numpy + ast. Add libraries as specific needs emerge from actual results, not anticipated needs. Every dependency you add now is a dependency you debug later at 3am when Apollo crashes on day 12.

Ask a second round of questions based on this feedback.