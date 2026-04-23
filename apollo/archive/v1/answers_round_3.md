Good questions. These are the right things to nail down before writing code. Let me take them fast.

---

## 1. Context Dict Key Problem

Option (c) — convention-based keys with last-writer-wins. You're right that it's the simplest model that supports self-referential iteration, and you're right that the "two PARSERs overwrite each other" problem is just selection pressure toward viable pipeline shapes.

One small refinement. Don't use just `ctx['score']` and `ctx['parsed']`. Use a two-tier convention:

```python
# Tier 1: Convention keys (what genes READ)
ctx['raw_text']     # Every gene can read this
ctx['parsed']       # SCORERs read this
ctx['score']        # Downstream SCORERs and self-referential loops read this

# Tier 2: Gene-stamped keys (what genes WRITE)
ctx['score']        = result    # Convention write
ctx['gene_03_score'] = result   # Stamped write (always, automatically by compiler)
```

The compiler injects the stamped write after every gene execution. Genes themselves only write to convention keys. This means last-writer-wins for the convention key but every gene's output is also preserved in the stamped key. The `_gene_trace` list records which gene wrote which convention key in which order.

Why this matters: when you're debugging a self-referential organism that produces surprising results, you can inspect `ctx['gene_03_score']` and `ctx['gene_07_score']` independently even though both wrote to `ctx['score']`. The convention key drives execution. The stamped key drives analysis. Zero additional complexity for the gene code itself — the compiler handles the stamping.

This also gives you a future upgrade path. Post-MVP, the wiring graph could specify "gene_07 reads from gene_03_score instead of the convention key" for precise wiring. But for MVP, convention keys with automatic stamping is the right balance.

## 2. Per-Candidate vs All-Candidates

Option (a) — per-candidate execution. Correct for all the reasons you stated. The pipeline is a scoring function over a single candidate, called in a loop. The evaluate method collects results and sorts.

One detail for the compiler: the compiled `evaluate()` method should catch per-candidate crashes individually. If the pipeline crashes on candidate 3 of 5, candidates 1, 2, 4, 5 still get scores. Candidate 3 gets score 0.0. This matches your error handling recommendation in question 8 and prevents one adversarial candidate from killing the entire evaluation.

## 3. Terminal Gene Designation

Option (a) — always `ctx['score']`. The last SCORER to write `ctx['score']` determines the output. If no SCORER fires successfully, score defaults to 0.0.

This is also what makes self-referential wiring meaningful. When a SCORER reads `ctx['score']` and writes `ctx['score']`, it's reading its own previous output (or another SCORER's output) and refining it. The convention key IS the feedback channel. No special wiring needed.

## 4. Windows Sandbox

Your proposed approach is correct. RestrictedPython for compile-time import validation, multiprocessing with spawn for runtime isolation and timeout.

The spawn constraint is actually a feature, as you noted. The concrete implementation:

Parent process compiles organism source code string through RestrictedPython. If it passes, the string is sent to a worker process via a Queue. The worker receives the string, exec's it into a fresh namespace, instantiates the class, runs the evaluation, returns results via Queue. Parent joins with 2-second timeout. If timeout fires, parent terminates the worker and the organism gets score 0.0 on that task.

Skip memory limits for MVP. The 2-second timeout catches the real failure modes — infinite loops and runaway computation. Memory bombs that allocate faster than 2 seconds of wall-clock time would require deliberately adversarial code, which can't emerge from gene recombination of forge tools that are all well-behaved numpy operations.

On RestrictedPython specifically: use it as a compile-time gate only. Don't try to use its runtime guards (safe_globals, limited_builtins) — they add complexity and the process isolation already gives you runtime safety. RestrictedPython scans the AST for disallowed imports, the sandbox provides runtime containment. Clean separation.

## 5. RestrictedPython Role

You answered this yourself correctly. RestrictedPython is compile-time. Multiprocessing is runtime. Defense in depth. Don't mix their roles.

## 6. Gene Classification Heuristics

This scheme works. Ship it.

The one case I'd handle differently: utility functions like `_sigmoid`, `_normalize`, `_clamp`. These aren't really genes — they're helper functions that genes call internally. During extraction, if a method is only ever called by other methods in the same class (never directly in `evaluate()` or `confidence()`), extract it as a UTILITY rather than a SCORER. Utilities travel with whatever gene calls them — when Gene A is transplanted and Gene A internally calls `_sigmoid`, the `_sigmoid` method comes along as a dependency, not as a separate gene in the pipeline.

This prevents the wiring graph from being cluttered with tiny helper functions that make no sense as standalone pipeline stages. The classifier already handles this: if the method takes a single float and returns a single float, and its name starts with `_` but doesn't match any PARSER or SCORER pattern, flag it as UTILITY. During gene extraction, attach utilities to the genes that reference them.

If this adds too much complexity, skip it and classify everything as SCORER as you proposed. Selection will handle the noise. But if it's easy to detect the "only called by other methods" pattern via AST analysis, it's worth the cleaner gene library.

## 7. Calibration Metric

Option (c) — Brier score. Correct for all the reasons you stated. It's proper, it works with small samples, and it's a single number.

One implementation detail: the Brier score needs a probability output from the organism, not just a ranking. This is where the auto-generated `confidence()` method matters. For each task, the organism ranks candidates via `evaluate()`. The top-ranked candidate's confidence score (from the auto-generated sigmoid wrapper) becomes the probability input to Brier.

Brier score: `(confidence_in_top_ranked - 1.0)^2` if the top-ranked candidate is correct, `(confidence_in_top_ranked - 0.0)^2` if incorrect. Average across tasks. Lower is better. Subtract NCD baseline Brier for margin-over-NCD calibration.

Make sure the fitness objective is `1.0 - brier_score` so that higher fitness is better, consistent with the accuracy dimension. NSGA-II maximizes all objectives.

## 8. Error Handling Mid-Pipeline

Your recommendation is correct. Gene crashes on a specific task give that task score 0.0. Organism-level fitness is computed across all tasks including the zeros. An organism that crashes on 4 of 20 tasks gets fitness based on the 16 surviving tasks with 4 zeros dragging down the average.

This creates exactly the right selection pressure. An organism with a flaky gene that adds 10% accuracy when it works but crashes 30% of the time has an expected contribution of +7% accuracy minus the crash penalty. Selection will determine whether that tradeoff is worth it. Sometimes it will be — a high-variance strategy that crashes occasionally but scores very high when it doesn't might outperform a safe low-variance strategy on Pareto terms.

Log every crash with gene_id, task_id, exception type, and a one-line traceback summary. Don't log full tracebacks — at 50 organisms × 20 tasks × thousands of generations, full tracebacks will eat disk. One line is enough for pattern analysis.

## 9. Population Model

Explicit elitism: top 5 parents always survive, remaining 45 slots filled by NSGA-II selection from the combined pool of 45 remaining parents + 50 children.

Here's why. Pure (mu+lambda) with no elitism can lose the best organism in a single generation through bad luck — the best organism is Pareto-dominated on one dimension by a child that's worse on every other dimension. That's a real risk with only 3 objectives and 50 organisms. Losing your best organism at generation 400 and never recovering is a 40-day disaster.

Pure (mu,lambda) where parents always die is even riskier. It's great for avoiding stagnation but terrible for preserving hard-won innovations.

Top 5 elitism is the standard compromise. The 5 best organisms (by Pareto rank, then crowding distance) survive unconditionally. This preserves the best innovations while keeping 90% of the population under full competitive pressure. It's the default in most serious evolutionary computation implementations for good reason.

Those 5 elite slots also give you a natural monitoring point. Log the elite set every generation. When an elite organism gets displaced by a child, that's an evolutionary event worth examining in detail.

## 10. Phase 0 CMA-ES Specifics

Per tool, not combined. 50 independent CMA-ES runs, one per seed tool. Here's why:

Combined optimization over all 50 tools simultaneously would be a 1,000-dimensional optimization (50 tools × 20 params). CMA-ES doesn't scale well past ~100 dimensions. Per-tool optimization is 20 dimensions each, which is CMA-ES's sweet spot.

**Objective:** Single-objective for Phase 0 — margin-over-NCD accuracy only. Don't add calibration yet. Phase 0 is about finding better parameter settings, not about multi-objective optimization. Keep it simple. The calibration dimension enters when structural evolution starts.

**Population size:** Use `4 + floor(3 * ln(20))` ≈ 13. That's fine. CMA-ES is designed to work well with small populations relative to dimensionality. 13 is standard for 20 parameters.

**Stopping criterion:** 50 generations per tool OR convergence (sigma drops below 1e-6). Whichever comes first. Most tools will converge well before 50 generations. Budget-wise you computed it correctly — 18 hours fits in 2 days easily.

**One addition:** After all 50 tools are parameter-optimized, re-evaluate them all on the same task set and re-rank. The ranking might change — a tool that was 5th by accuracy might become 1st after parameter tuning. Use the post-Phase-0 ranking to select the seed population for structural evolution.

Also save the pre-optimization and post-optimization accuracy for each tool. The delta is informative — tools with large deltas had untapped parametric potential. Tools with zero delta were already at their parametric optimum and can only improve through structural changes. That's useful context for interpreting structural evolution results.

## 11. Viability Spike Phasing

Your two-phase approach is exactly right.

Phase A (1 hour): raw method swap, no parameter rewriting. This is the existential test. If 100 random chimeras produce fewer than 5 that are valid Python on import, you know the raw AST approach is going to struggle and you should be mentally preparing the StarCoder fallback.

Phase B (half day): with parameter rewriting. This is the real viability rate. This is the number that determines everything.

One addition to Phase B. Don't just test "does it import." Test "does it produce a non-zero score on at least 1 of the 15 seed traps." Import success and functional success are different things. A chimera might import fine but return NaN or crash during evaluation. The viability number you care about is "produces at least one valid score," not "passes ast.parse."

The threshold table:

- Above 40% functional viability → AST-only, proceed as planned
- 20-40% → AST-only but increase offspring per generation to 100 (accepting that 60-80% will die, but 20-40 survivors is enough for selection)
- 10-20% → Warm start with very mild mutations only for first 200 generations. Splice rate drops to 10%, point mutate dominates at 60%. Let the population build up viable building blocks before aggressive recombination.
- Below 10% → StarCoder mutation operator becomes an MVP requirement, not post-MVP.

Run the spike. That number is the foundation everything else stands on.

---

## Summary

1. Convention keys + automatic gene-stamped writes (tier 2 for analysis)
2. Per-candidate execution with per-candidate crash isolation
3. `ctx['score']` as terminal, last SCORER wins
4. RestrictedPython compile-time, multiprocessing runtime, skip memory limits
5. Same as 4 — defense in depth, don't mix roles
6. Classification scheme works, add UTILITY detection if cheap
7. Brier score, inverted (1 - brier) for maximization, margin over NCD
8. Gene crash = task scores 0.0, organism survives on remaining tasks, log one-line crash summaries
9. Explicit elitism — top 5 always survive, 45 slots competitive
10. Per-tool CMA-ES, single-objective (accuracy), 50 gens per tool, ~18 hours total
11. Two-phase spike, functional viability threshold determines the path

Weave these into the 