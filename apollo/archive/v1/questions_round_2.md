# Apollo Questions — Round 2

*After cross-referencing the MVP spec, the design review, the actual forge tool code, the trap generator, the Nemesis grid, and the Hephaestus ledger.*

---

## Implementation-Critical (Need Answers to Build)

### 1. The `self` Problem in Gene Extraction

Every forge tool method references `self`. When we `ast.parse()` a tool and extract `_extract_numbers(self, text)`, it's a bound method that may reference instance variables from `__init__`:

```python
# From active_inference_x_epistemology_x_network_science.py
def __init__(self):
    self.lambda_balance = 0.4        # Used in _check_coherence and evaluate
    self.threshold_numeric = 0.01    # Used in evaluate
```

When Gene A (from Tool X, expects `self.lambda_balance`) is transplanted into an organism alongside Gene B (from Tool Y, also has a `self.lambda_balance` but set to 0.7), which value wins?

**My proposed solution:** During gene extraction, rewrite `self.param_name` references into the genome's evolvable `parameters` dict. The gene becomes parameter-agnostic — it references `self.params['lambda_balance']`, and the specific value lives in the genome's parameter vector. The compiler assembles `__init__` from the union of all gene parameter requirements. Name collisions between genes are resolved by prefixing with gene_id: `self.params['gene_03_lambda_balance']`.

This makes parameters explicitly evolvable and eliminates the collision problem. Does this approach track with your thinking, or do you want a simpler strategy?

### 2. Two Methods, One Wiring Graph

The ReasoningTool interface requires **two** methods: `evaluate(prompt, candidates) → list[dict]` and `confidence(prompt, answer) → float`. The genome is one wiring graph of genes.

Looking at the actual forge tools, most `confidence()` methods are thin wrappers — they reuse the same scoring logic from `evaluate()` but on a single candidate, then sigmoid-map the result. For example (from the tool I read):

```python
def confidence(self, prompt, answer):
    j = self._compute_justification(prompt, answer)
    c = self._check_coherence(prompt, answer)
    ig = self._compute_info_gain(prompt, answer)
    raw_score = (ig * j) - (self.lambda_balance * c)
    return 1.0 / (1.0 + np.exp(-raw_score))
```

**Options:**
- **(a)** The wiring graph only defines the `evaluate()` pipeline. `confidence()` is auto-generated: call `evaluate(prompt, [answer])`, return the score sigmoid-mapped to [0,1]. This is simpler and matches how most forge tools actually work.
- **(b)** The wiring graph has two subgraphs — one for evaluate, one for confidence. More expressive but doubles the compilation complexity.
- **(c)** The CONFIDENCE gene type IS the confidence method. Each organism has exactly one CONFIDENCE gene that takes the pipeline's raw scores and maps them.

I lean toward **(a)** for MVP — auto-generate confidence from evaluate. It eliminates an entire class of compilation problems and reflects how the forge tools actually work. The CONFIDENCE gene type then becomes a score-to-probability mapper within evaluate, not a separate method.

### 3. What Data Type Flows Through the Wires?

The wiring graph connects gene outputs to gene inputs. But what's the data type?

Looking at the forge tools:
- PARSER methods return heterogeneous types: `list[float]`, `dict[str, list]`, `tuple[list, list]`, `list[str]`
- SCORER methods expect heterogeneous inputs: some want raw `str`, some want pre-parsed `list[float]`

**Options:**
- **(a)** Everything is `str`. Genes that need structured data parse it themselves from string representations. Lossy but universal. Any gene can wire to any gene.
- **(b)** Everything is `dict[str, Any]`. Each gene reads the keys it needs, ignores the rest. Genes add their outputs as new keys. Accumulative — downstream genes see all upstream results.
- **(c)** Type-aware wiring. PARSER→SCORER connections must match specific type signatures. Compilation rejects mismatches.

I lean toward **(b)** — a shared context dict that accumulates results as genes fire. This is how many pipeline architectures work. Each gene reads `ctx['raw_text']` or `ctx['parsed_numbers']` or `ctx['upstream_score']` and writes its results back. The compiler validates that required keys exist upstream. This is permissive enough for novel combinations but structured enough to prevent most crashes.

The initial context dict starts as:
```python
ctx = {'prompt': prompt, 'candidate': candidate, 'raw_text': prompt + ' ' + candidate}
```

Each gene reads what it needs and writes what it produces. The final gene's output becomes the score.

### 4. NCD: Infrastructure or Gene?

The Hephaestus ledger already tracks `margin_accuracy` — accuracy relative to NCD baseline. The review says NCD should be infrastructure (always available, never scored). Your answer says "let selection handle it."

These two positions create a specific design question: **Should Apollo's accuracy metric be raw accuracy or margin-over-NCD?**

If raw accuracy: NCD organisms score ~30-40% and survive easily. Selection pressure is weak for organisms that add complexity on top of NCD because the marginal improvement is small relative to the NCD floor.

If margin-over-NCD: an organism that scores 40% (10% above NCD baseline) and an organism that scores 35% (5% above baseline) are compared on their ADDED VALUE, not their total score. This creates much stronger pressure to develop non-NCD strategies.

The Hephaestus forge already uses margin scoring. Should Apollo inherit this?

### 5. How Does Novelty Enter NSGA-II Selection?

MVP says: 2 objectives (accuracy + calibration) with NSGA-II, plus a novelty archive. But NSGA-II only ranks by Pareto dominance on its stated objectives. Novelty must enter somewhere.

**Options:**
- **(a)** Novelty is a 3rd NSGA-II objective. Makes it 3-objective — still fine for NSGA-II, gives novelty equal Pareto standing.
- **(b)** Novelty is a crowding distance tiebreaker — when two organisms are Pareto-equivalent, prefer the more novel one. Weaker but simpler.
- **(c)** Chromaria-style minimal criterion — any organism with novelty above threshold survives regardless of fitness, up to a population fraction cap (e.g., 20% of slots reserved for novel organisms). Strongest diversity guarantee.
- **(d)** Novelty bonus added to accuracy: `adjusted_accuracy = accuracy + 0.2 * novelty_score`. Collapses back to near-scalar optimization.

The review cites Lehman & Stanley saying 20% novelty weight may not be enough. The choice here shapes whether Apollo discovers genuinely novel strategies or converges to accuracy-optimized NCD variants.

Which approach?

### 6. Is Gene Deletion In or Out?

The MVP spec lists 4 operators: point mutate, splice, duplicate, rewire. Gene deletion is absent. The review flags bloat as medium risk — splice + duplicate add genes, nothing removes them.

Without deletion, genome size is monotonically increasing. By generation 1000, organisms could have 20+ genes when only 4-5 do useful work. The dead weight slows evaluation (more methods to execute) and makes crossover noisier (more irrelevant genes to inherit).

The original design had deletion at 10%. Should MVP include it?

---

## Risks the Review Raises That the Answers Don't Fully Address

### 7. The Viability Rate Question

You expect 80%+ viable offspring from AST method swaps. The review cites <5% for random AST manipulation. The truth depends on implementation specifics. **Can we test this cheaply before building the full system?**

Concrete proposal: a 50-line script that extracts methods from 10 forge tools, creates 100 random chimeras (swap methods between tools), and checks how many produce valid Python that runs on 1 trap without crashing. If viability is >50%, AST-only is proven for MVP. If <10%, we know early.

This takes an afternoon and eliminates the biggest uncertainty in the plan. Worth doing as a pre-build spike?

### 8. Held-Out Validation

The success criterion is "beat IBAI v2 at 67% on the 15 seed traps." The fitness evaluation uses the same 15 seed traps (plus 5 generated). Organisms are being trained and tested on the same data.

The review warns about the "interesting gap" — organisms that overfit to the 20 eval tasks without genuine reasoning improvement. A held-out set is the standard mitigation.

**Proposal:** Generate a fresh trap battery (using `trap_generator.py`) with a different seed. Use 15 traps + 5 generated for fitness evaluation. Use the held-out battery for success criterion validation. This costs nothing — the trap generator is deterministic given a seed.

### 9. NCD Monoculture Risk

You're warm-starting with the 50 best forge tools. Looking at the ledger, the top tools by accuracy are:
- Criticality × FEP × Pragmatics: 66.7%
- Chaos Theory × Dialectics × Feedback Control: 66.7%
- Info Theory × Multi-Armed Bandits × SAE: 60.0%
- Compositionality × Criticality × Global Workspace: 60.0%
- ...

But the Nemesis grid shows DIFFERENT top tools (thermodynamics variants at 73-75%). And 87% of all forge tools include NCD.

If the top 50 are mostly NCD variants, the initial population is NCD-dominated. Crossover between NCD variant A and NCD variant B produces NCD variant C. This is the convergence trap the review flags as HIGH RISK.

**Specific question:** Should we enforce diversity in the seed population? E.g., take the top 30 by accuracy + the 20 most structurally diverse (by gene composition, not score)?

### 10. Phase 0: Parameter Evolution as Warmup

The review recommends CMA-ES parameter-only evolution as a 2-day warmup before structural evolution. This:
- Validates the fitness environment works before building the hard parts
- Produces better-calibrated seed organisms
- Is ~100 lines of code using pymoo
- Could itself beat the 67% baseline (each tool has 15-25 evolvable floats)

You didn't address this in round 1. Is it worth the 2-day investment before structural evolution? Or skip straight to the hard stuff?

---

## Architecture Decisions Where the Two Documents Diverge

### 11. The LLM Mutation Question (The Elephant)

Your answer: stdlib `ast` only, no API calls, minimal dependencies.

The review: LLM-assisted mutation is "the single biggest design decision," the #1 thing that would make Apollo extraordinary, and its absence is the #1 risk that would kill it. Cites AlphaEvolve, FunSearch, OpenELM showing 10-100x viable offspring rates vs AST manipulation.

The review also suggests a middle path: a local 1-3B coding model (StarCoder 1B fits on the 17GB card) as a mutation operator. No API dependency. No network calls. Deterministic given a seed.

I'm not re-litigating the MVP decision — AST-only for MVP is clear. But I want to flag: **the review's recommendation to add LLM mutation as the first post-MVP enhancement is well-supported by the literature.** If the viability spike (question 7) shows AST offspring viability is <30%, LLM mutation moves from "post-MVP" to "MVP survival requirement."

Is there a viability threshold below which you'd reconsider?

### 12. Crossover on a Directed Graph

"Pipeline crossover — front half of parent A's wiring graph, back half of parent B's."

A wiring graph is a directed graph (possibly cyclic). "Front half" isn't well-defined for a graph. For MVP with a single crossover operator, I need a specific algorithm:

**My proposal:** Topological sort the wiring graph (breaking cycles at the iteration cap). Number genes 0..n by topo-sort order. Choose a crossover point k. Child gets genes 0..k from parent A (with A's wiring between those genes) and genes k+1..m from parent B (with B's wiring between those genes). New wiring connects A's gene[k] output to B's gene[k+1] input. If types are incompatible, the child fails compilation and dies.

This is the simplest graph crossover that preserves causal ordering. Sound right?

### 13. Self-Referential Emergence Rate

For self-referential wiring to appear, an organism needs gene duplication (15%) AND rewiring to create a back-connection (20%). That's ~3% per organism per generation, ~1.5 organisms per generation in a population of 50.

But these are independent mutations. A more natural path to self-reference might be a compound "duplicate-and-wire-back" operator — a single mutation that copies a gene AND wires the copy's input to the original's output. This would be explicitly designed to produce the self-checking pattern at a controllable rate.

**Question:** Should we add a "duplicate-and-wire-back" compound operator alongside the individual duplicate and rewire operators? This would increase the rate of self-referential emergence without increasing the overall mutation rate. The compound operator is specifically engineered to produce the metacognitive seed pattern.

This feels like it might violate the "let it emerge" philosophy. But it's also true that if the individual mutation probabilities make emergence too slow, we'll never see the signal in 34,000 generations. The compound operator doesn't guarantee self-reference helps — selection still decides whether it survives. It just makes sure the building block appears often enough for selection to act on it.

---

## One More Thing

Looking at the actual Nemesis grid data, the top tools score 73-75% on adversarial tasks — significantly higher than the ledger's 66.7% on standard traps. The success criterion references "IBAI v2 at 67%." Which benchmark should Apollo target? The standard trap battery accuracy (from the ledger) or the adversarial grid accuracy (from Nemesis)?

If the Nemesis grid tasks are harder and the top tool scores 75% on those, "beat 67% on standard traps" might be too easy — an organism could achieve it by parameter-tuning an existing top-scoring tool without any structural evolution. The more meaningful criterion might be: beat the best tool on the SAME task set Apollo uses for evaluation.
