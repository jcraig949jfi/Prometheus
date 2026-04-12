# Apollo Questions — Round 3

*Implementation-level questions. After cross-referencing round 2 decisions, the actual forge tool method signatures, the trap generator interface, and the runtime environment (Python 3.11 on Windows).*

---

## The Big One: How Wiring Actually Works

### 1. The Context Dict Key Problem

This is the single most important implementation question remaining. It determines the compiler architecture, gene extraction complexity, and whether self-referential wiring can actually function.

Each gene is an extracted method that reads/writes to the shared context dict. But extracted methods have **hardcoded key reads**. For example:

- Gene A (from tool X): reads `ctx['prompt']`, `ctx['candidate']`, writes `ctx['coherence_score']`
- Gene B (from tool Y): reads `ctx['parsed_numbers']`, `ctx['ncd_score']`, writes `ctx['final_score']`

The wiring graph says A→B. But B reads `ctx['parsed_numbers']` — a key that A doesn't write. The wiring connection is meaningless unless the compiler rewrites key access.

**Four possible models:**

**(a) Hardcoded keys, wiring is just execution order.** Genes read whatever keys they read. Wiring determines only the order genes fire. Self-referential iteration works only if genes happen to read keys that other genes wrote. Simple but severely limits what combinations are viable.

**(b) Gene-ID-namespaced outputs with explicit remapping.** Each gene writes to `ctx['gene_01_output']`. The wiring graph includes key mappings: "gene_01_output → gene_02_input_score". The compiler inserts `ctx['parsed_numbers'] = ctx['gene_01_output']` between gene calls. More complex but makes any wiring viable.

**(c) Convention-based keys by gene type.** During extraction, gene code is rewritten to use standard keys:
- PARSER genes: always read `ctx['raw_text']`, always write `ctx['parsed']`
- SCORER genes: always read `ctx['parsed']` + `ctx['raw_text']`, always write `ctx['score']`
- FALLBACK: always read `ctx['raw_text']`, always write `ctx['fallback_score']`

This is the simplest model that supports self-reference: a duplicated SCORER writes `ctx['score']`, and on the next iteration it reads the updated `ctx['score']`. Feedback loops emerge naturally from execution order + iteration.

**Downside:** Two PARSER genes both write `ctx['parsed']` — the second overwrites the first. Gene ordering becomes fragile.

**(d) Hybrid: convention-based with collision avoidance.** Same as (c) but genes write to `ctx[f'{gene_id}_parsed']` or `ctx[f'{gene_id}_score']`. The "input" for a gene is the convention key (e.g., `ctx['score']`), and the compiler inserts a `ctx['score'] = ctx['gene_03_score']` remapping before each gene fires, pulling from the designated upstream gene's namespaced output.

I lean toward **(c)** for MVP simplicity — convention-based keys with last-writer-wins semantics. It's the least compiler complexity, it naturally supports self-referential iteration, and the "two PARSERs overwrite each other" problem is just selection pressure toward pipeline shapes where you don't stack two PARSERs without a SCORER between them.

But this is a foundational choice. What's your call?

### 2. Per-Candidate vs All-Candidates Pipeline

The ReasoningTool interface takes a list of candidates: `evaluate(prompt, candidates) → list[dict]`. The context dict starts with one candidate: `ctx = {'prompt': prompt, 'candidate': candidate, ...}`.

**Does the pipeline run once per candidate?**

Most forge tools iterate: `for cand in candidates: score(cand)`. This is simple — the pipeline is a per-candidate scoring function, called once for each candidate, results collected and sorted.

But some forge tools do relative scoring — they need to see all candidates to compute min-max normalization or relative rankings. A per-candidate pipeline can't do this.

**Options:**
- **(a)** Per-candidate execution (simple). Each candidate gets its own pipeline run. No cross-candidate comparison. This is what 90%+ of forge tools do.
- **(b)** All-candidates execution. The context dict includes `ctx['all_candidates']` and the pipeline runs once. Genes can do relative scoring. More expressive but harder to compile.

I recommend **(a)** for MVP. It's simpler, matches the majority pattern, and relative scoring can be added post-MVP as a gene type that wraps the per-candidate pipeline.

### 3. Terminal Gene Designation

After all genes fire, which context dict key becomes the candidate's score?

**Options:**
- **(a)** Always `ctx['score']` — the convention key for SCORER genes. The last SCORER to fire determines the score.
- **(b)** The output of the gene designated as "terminal" in the wiring graph.
- **(c)** A fixed "output" gene that's automatically appended to every organism, reading whatever the last gene wrote.

I lean toward **(a)** — always `ctx['score']`. The convention that SCORER genes write to `ctx['score']` means the last SCORER in topological order is the terminal gene by default. If no SCORER fires (all genes crash), score defaults to 0.0.

---

## Runtime Constraints

### 4. Windows Sandbox Limitations

Python's `resource` module (for `setrlimit` CPU/memory limits) **does not exist on Windows**. This means:

- No `RLIMIT_CPU` for CPU time limits
- No `RLIMIT_AS` for memory limits
- No `RLIMIT_NPROC` for process count limits

**What we CAN do on Windows:**
- `multiprocessing.Process` with `process.join(timeout=2)` then `process.terminate()` for wall-clock timeout
- `concurrent.futures.ProcessPoolExecutor` with `future.result(timeout=2)`
- Pebble library for reliable timeout + worker restart
- Job Objects via `pywin32` for memory limits (but adds a dependency)

**Proposed approach for MVP:**
- Use `multiprocessing.Process` per organism evaluation with a 2-second wall-clock timeout
- Skip memory limits for MVP — the 2-second timeout is the real safety net (infinite loops time out, memory allocation takes time)
- If memory becomes a problem, add Job Objects or switch to Pebble

Also: `multiprocessing` on Windows uses **spawn** (not fork). This means:
- Every worker process re-imports modules from scratch
- Objects passed to workers must be pickle-serializable
- The compiled organism code must be passed as a string (not a live object)

The spawn constraint means the sandbox worker receives organism source code as a string, compiles it in the child process, executes it, and returns results via a Queue. This is actually more isolated than fork (the child has no access to the parent's memory), which is a security benefit.

### 5. RestrictedPython on Windows

RestrictedPython works on Windows (it's pure Python, AST-based). But it needs to be installed: `pip install RestrictedPython`.

For import whitelisting, RestrictedPython provides `safe_globals` and `limited_builtins`. We'd configure:
- Allowed: `numpy`, `math`, `re`, `collections`, `itertools`, `functools`, `statistics`, `hashlib`, `zlib`, `copy`, `dataclasses`, `random`, `string`, `operator`
- Blocked: `os`, `sys`, `subprocess`, `socket`, `io`, `pathlib`, `importlib`, everything else

**Question:** Should RestrictedPython be the AST-level import validator (compile-time check) while multiprocessing provides the runtime isolation? Or should we rely on RestrictedPython alone for both?

I recommend both — RestrictedPython catches disallowed imports at compile time (before the organism ever runs), multiprocessing with timeout provides runtime isolation (catches infinite loops and resource abuse). Defense in depth.

---

## Remaining Design Details

### 6. Gene Classification Heuristics

After analyzing 6 diverse forge tools, the method naming patterns are remarkably consistent:

| Gene Type | Name Patterns | Return Type | Key Reads |
|-----------|---------------|-------------|-----------|
| PARSER | `_extract_*`, `_parse_*`, `_tokenize*`, `_hash_*` | list, dict, tuple | `raw_text`, `prompt` |
| SCORER | `_compute_*`, `_check_*`, `_run_*`, `_score_*`, `_*_score` | float | varies |
| FALLBACK | `_ncd`, `_get_ncd`, `_normalized_compression_*` | float | `prompt`, `candidate` |

**Proposed auto-classification algorithm:**
1. If method name contains `ncd` or `compress` → FALLBACK
2. If method name starts with `_extract_`, `_parse_`, `_tokenize` → PARSER
3. If method name is `evaluate` or `confidence` → skip (these are the interface, not genes)
4. If method name is `__init__` → extract parameters only
5. If return type annotation is `float` OR method name contains `score`, `compute`, `check`, `run` → SCORER
6. Anything else → SCORER (default, since most methods produce scores)

If a method doesn't match any pattern, classify it as SCORER and let selection sort it out. This follows the "let selection handle incoherence" principle.

**Ambiguity case:** `_sigmoid(self, x)` — is it a SCORER? It's really a utility function. Classifying it as SCORER is harmless (it takes a float, returns a float — type-compatible with SCORER convention). If it gets spliced into a pipeline, it just applies a sigmoid to the upstream score. That's a valid operation.

Does this classification scheme work, or do you want more nuance?

### 7. Calibration Metric

The 3 NSGA-II objectives are: margin-over-NCD accuracy, calibration, novelty. What specifically is "calibration"?

**Options:**
- **(a) Expected Calibration Error (ECE):** Bin organisms by confidence level, compare stated confidence to actual accuracy within each bin. Standard metric. But with only 20 tasks per generation, bins are noisy.
- **(b) Simple confidence-accuracy correlation:** For each task, compute `|confidence(correct_answer) - accuracy_on_this_task|`. Average across tasks. Penalizes overconfidence on wrong answers and underconfidence on right answers.
- **(c) Brier score:** `(confidence - correct)^2` averaged across tasks. Where `correct=1` if organism ranked the right answer first, `correct=0` otherwise. Proper scoring rule.
- **(d) Confidence gap:** `confidence(correct_answer) - confidence(best_wrong_answer)`. Organisms that are confident in the right answer AND unconfident in wrong answers score high.

I recommend **(c) Brier score** — it's a proper scoring rule (organisms can't game it by always saying 50%), it works well with small sample sizes, and it's a single number per organism per generation. Margin-over-NCD Brier score for the calibration objective.

### 8. Error Handling Mid-Pipeline

When a gene crashes during execution (raises an exception), what happens?

**Options:**
- **(a)** Organism dies — fitness 0 on that task, crash logged to graveyard with cause
- **(b)** Gene skipped — context dict unchanged, pipeline continues without that gene's output
- **(c)** Default value injected — `ctx['score'] = 0.0` and continue

I recommend **(a)** for the task, **(b)** for the overall organism. If a gene crashes on one task, that task scores 0 (partial death). If it crashes on ALL tasks, the organism has fitness 0 and dies in selection. This way, an organism with one flaky gene that crashes 20% of the time still gets evaluated on the other 80% of tasks, and selection can determine whether the flaky gene's contribution on surviving tasks is worth the crash cost.

Log every crash: `{gene_id, task_id, exception_type, traceback_summary}` in the lineage JSONL. This feeds the graveyard analysis.

### 9. Population Model

**Generational** (replace entire population each generation) or **steady-state** (replace worst few each generation)?

The MVP spec says: 50 organisms, 50 offspring. This implies generational: evaluate 50 parents + 50 children = 100, select best 50 to survive.

Confirm: generational replacement with (mu+lambda) selection? Parents compete with children for survival — no elitism guarantee?

Or (mu,lambda): only children compete, parents always die? This is riskier but prevents population stagnation.

Or explicit elitism: top 5 parents always survive, remaining 45 slots filled by selection from the rest?

### 10. Phase 0 CMA-ES Specifics

Phase 0 evolves parameters of existing tools without structural changes. Using pymoo's CMA-ES:

- **Per tool or combined?** Run CMA-ES separately for each of the 50 seed tools (50 independent optimizations)? Or combine all tools into one big optimization (evolving parameters across all 50 simultaneously)?
- **Objective:** Margin-over-NCD accuracy? Or margin accuracy + calibration (multi-objective)?
- **Population size for CMA-ES:** Default is `4 + floor(3 * ln(n_params))`. For 20 params, that's ~13. Seems small?
- **Stopping criterion:** Fixed number of evaluations? Or convergence-based?
- **Duration budget:** 2 days ≈ 172,800 seconds. At 0.1s per eval, 20 tasks: each candidate evaluation takes 2 seconds. CMA-ES with 13 population for 50 tools × 200 generations = 130,000 evaluations = 260,000 seconds. Tight.

Maybe: 50 generations per tool, 50 tools = 2,500 generations × 13 candidates × 20 tasks = 650,000 evals at 0.1s = 65,000 seconds ≈ 18 hours. That fits in 2 days with room.

---

## One Final Question

### 11. Should the Viability Spike Include the Parameter Rewriting?

The viability spike tests whether AST method swapping produces viable chimeras. But the MVP also includes parameter rewriting (`self.param` → `self.params['gene_XX_param']`).

If the spike does basic method swapping WITHOUT parameter rewriting, it'll undercount viability (methods that reference `self.lambda_balance` will crash when that attribute doesn't exist in the chimera).

If the spike includes parameter rewriting, it's testing the full gene extraction pipeline — which is a significant portion of the build.

**My recommendation:** Do the spike in two phases:
1. **Phase A (1 hour):** Raw method swap, no parameter rewriting. Measures the floor — how many chimeras are syntactically valid Python that don't crash on import?
2. **Phase B (half day):** With parameter rewriting (extract `__init__` params, merge into `self.params` dict, rewrite `self.X` → `self.params['gene_XX_X']`). Measures the actual viability rate under MVP conditions.

Phase A tells us whether the approach is DOA. Phase B tells us the real number. Both are valuable.
